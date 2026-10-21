"""
conftest.py — shared pytest fixtures for NEXUSTRACE AI backend tests.

Key design:
- StaticPool forces ALL SQLAlchemy connections (TestClient AND direct DB
  fixtures) to share a single underlying SQLite connection. This guarantees
  that tables created by create_tables are visible everywhere — no more
  "no such table" from connection isolation.
- scope="session" engine lives for the entire pytest session.
- Tests use unique identifiers to avoid PK conflicts across test functions.
"""
import pytest
import sys
from pathlib import Path

# Ensure backend root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ── Import models BEFORE anything else so metadata is populated
from app.database import Base, get_db
import app.models.models as M  # noqa: F401

from app.main import app
from app.models.models import (
    User, Company, CompanyMembership, Supplier, SupplierRelationship,
    Component, Product, BillOfMaterial, InventorySnapshot, Scenario,
    RiskFinding
)
from app.security.auth import hash_password, create_access_token
import uuid

# ── In-memory SQLite via StaticPool — single connection shared by ALL threads
TEST_DATABASE_URL = "sqlite://"  # in-memory

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,          # ALL connections reuse ONE underlying connection
)

# Disable FK checks for easier test fixture setup
@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=OFF")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# ── Override FastAPI dependency so TestClient uses our in-memory DB
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


# ── Create ALL tables ONCE for the entire session
@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=test_engine)
    yield
    # Leave tables in place — dropping can cause teardown ordering issues


# ── Provide a DB session per test function
@pytest.fixture(scope="function")
def db(create_tables):
    session = TestingSessionLocal()
    yield session
    try:
        session.close()
    except Exception:
        pass


# ── FastAPI test client (depends on create_tables so tables exist)
@pytest.fixture(scope="function")
def client(create_tables):
    with TestClient(app) as c:
        yield c


# ─────────────────────────────────────────────────────────────
# Auth helpers
# ─────────────────────────────────────────────────────────────

def make_user(db, email="test@example.com", password="testpass123", admin=False):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return existing
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        hashed_password=hash_password(password),
        full_name="Test User",
        is_active=True,
        is_platform_admin=admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_token(user: User) -> str:
    return create_access_token({"sub": user.id})


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def admin_user(db):
    return make_user(db, f"admin_{uuid.uuid4().hex[:6]}@test.com", "admin1234", admin=True)


@pytest.fixture(scope="function")
def admin_token(admin_user):
    return make_token(admin_user)


@pytest.fixture(scope="function")
def admin_headers(admin_token):
    return auth_headers(admin_token)


# ─────────────────────────────────────────────────────────────
# Demo data fixtures
# ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def demo_company(db):
    company = Company(
        id=str(uuid.uuid4()),
        name=f"Test Company {uuid.uuid4().hex[:6]}",
        industry="manufacturing",
        is_demo=True,
        tenant_id=str(uuid.uuid4()),
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@pytest.fixture(scope="function")
def demo_membership(db, admin_user, demo_company):
    m = CompanyMembership(
        id=str(uuid.uuid4()),
        user_id=admin_user.id,
        company_id=demo_company.id,
        role="admin",
    )
    db.add(m)
    db.commit()
    return m


@pytest.fixture(scope="function")
def helios_network(db, demo_company):
    """
    Build the Helios hidden-dependency network:
        CirroTech, Northstar, ArcLight → depends_on → Helios
        SkyNode → depends_on → AzureChip → manufactures → Helios
    All suppliers belong to demo_company so build_graph sees them.
    """

    def make_sup(name, stype="direct", tier=1):
        s = Supplier(
            id=str(uuid.uuid4()),
            company_id=demo_company.id,
            name=name,
            supplier_type=stype,
            tier_level=tier,
            is_demo=True,
            source_type="synthetic",
            risk_score=round(0.4 + tier * 0.1, 2),
            verification_status="verified",
        )
        db.add(s)
        return s

    helios   = make_sup("Helios Semiconductor Works", "manufacturer", 3)
    azurechip = make_sup("AzureChip Assembly", "manufacturer", 2)
    cirrotech = make_sup("CirroTech Electronics", "direct", 1)
    northstar = make_sup("Northstar Precision Components", "direct", 1)
    arclight  = make_sup("ArcLight Power Systems", "direct", 1)
    skynode   = make_sup("SkyNode Sensors", "direct", 1)
    db.flush()

    def make_rel(from_id, to_id, rtype):
        r = SupplierRelationship(
            id=str(uuid.uuid4()),
            from_supplier_id=from_id,
            to_supplier_id=to_id,
            relationship_type=rtype,
            confidence_score=0.95,
            verification_status="verified",
            source_type="synthetic",
        )
        db.add(r)
        return r

    # All four direct suppliers depend on Helios (directly or via AzureChip)
    make_rel(cirrotech.id, helios.id,    "depends_on")
    make_rel(northstar.id, helios.id,    "depends_on")
    make_rel(arclight.id,  helios.id,    "depends_on")
    make_rel(skynode.id,   azurechip.id, "depends_on")
    make_rel(azurechip.id, helios.id,    "manufactures")

    db.commit()
    return {
        "helios":    helios,
        "azurechip": azurechip,
        "cirrotech": cirrotech,
        "northstar": northstar,
        "arclight":  arclight,
        "skynode":   skynode,
    }


@pytest.fixture(scope="function")
def demo_scenario(db, demo_company, helios_network, admin_user):
    scenario = Scenario(
        id=str(uuid.uuid4()),
        company_id=demo_company.id,
        name="Test Helios Shortage",
        disruption_type="supply_shortage",
        target_supplier_id=helios_network["helios"].id,
        duration_days=30,
        capacity_reduction_pct=100.0,
        recovery_lead_time_days=60,
        status="draft",
        created_by_id=admin_user.id,
        is_predefined=False,
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return scenario


@pytest.fixture(scope="function")
def demo_product_with_bom(db, demo_company, helios_network):
    comp = Component(
        id=str(uuid.uuid4()),
        name="Test IC",
        component_type="semiconductor",
        supplier_id=helios_network["cirrotech"].id,
        unit_price=100.0,
        currency="USD",
        lead_time_days=14,
    )
    db.add(comp)
    db.flush()

    product = Product(
        id=str(uuid.uuid4()),
        company_id=demo_company.id,
        name="Test Product Alpha",
        daily_demand=10.0,
        revenue_per_unit=5000.0,
        currency="USD",
    )
    db.add(product)
    db.flush()

    bom = BillOfMaterial(
        id=str(uuid.uuid4()),
        product_id=product.id,
        component_id=comp.id,
        quantity_required=2.0,
    )
    db.add(bom)

    inv = InventorySnapshot(
        id=str(uuid.uuid4()),
        company_id=demo_company.id,
        component_id=comp.id,
        supplier_id=helios_network["cirrotech"].id,
        quantity_on_hand=100.0,
        days_of_supply=10.0,
    )
    db.add(inv)
    db.commit()
    return {"product": product, "component": comp, "bom": bom, "inventory": inv}
