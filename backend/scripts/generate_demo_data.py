"""
generate_demo_data.py
Deterministic demo data generator (random.seed(42)) for NEXUSTRACE AI.
Outputs CSV/JSON files to data/demo/.
"""
import random
import json
import csv
import os
import uuid
import bcrypt
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

BASE_DIR = Path(__file__).parent.parent
DEMO_DIR = BASE_DIR / "data" / "demo"
DEMO_DIR.mkdir(parents=True, exist_ok=True)

NOW = datetime(2024, 6, 1, 12, 0, 0)


def rnd_id():
    return str(uuid.UUID(int=random.getrandbits(128)))


def rnd_date(base=NOW, days_back=180):
    delta = timedelta(days=random.randint(0, days_back))
    return (base - delta).isoformat()


def write_csv(filename, rows, fieldnames=None):
    path = DEMO_DIR / filename
    if not rows:
        return
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Written {len(rows)} rows → {path.name}")


def write_json(filename, data):
    path = DEMO_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"  Written -> {path.name}")


# ─────────────────────────────────────────────
# COMPANIES
# ─────────────────────────────────────────────
COMPANIES = [
    {
        "id": rnd_id(), "name": "ApexDrive Mobility", "industry": "automotive",
        "description": "Tier-1 automotive systems manufacturer", "is_demo": True,
        "tenant_id": rnd_id(), "created_at": rnd_date(), "updated_at": rnd_date(),
    },
    {
        "id": rnd_id(), "name": "VoltEdge Energy", "industry": "energy-storage",
        "description": "Battery and energy storage systems provider", "is_demo": True,
        "tenant_id": rnd_id(), "created_at": rnd_date(), "updated_at": rnd_date(),
    },
    {
        "id": rnd_id(), "name": "OrionTech Devices", "industry": "electronics",
        "description": "Consumer and industrial electronics OEM", "is_demo": True,
        "tenant_id": rnd_id(), "created_at": rnd_date(), "updated_at": rnd_date(),
    },
]
APEX_ID, VOLT_ID, ORION_ID = COMPANIES[0]["id"], COMPANIES[1]["id"], COMPANIES[2]["id"]


# ─────────────────────────────────────────────
# USERS
# ─────────────────────────────────────────────
# Hash the documented demo password so seeded credentials always work.
DEMO_HASH = bcrypt.hashpw(b"demo1234!", bcrypt.gensalt(rounds=12)).decode("utf-8")

USERS = [
    {
        "id": rnd_id(), "email": "admin@nexustrace.demo",
        "hashed_password": DEMO_HASH, "full_name": "Demo Admin",
        "is_active": True, "is_platform_admin": True,
        "created_at": rnd_date(), "updated_at": rnd_date(),
    },
    {
        "id": rnd_id(), "email": "analyst@apexdrive.demo",
        "hashed_password": DEMO_HASH, "full_name": "Alex Chen",
        "is_active": True, "is_platform_admin": False,
        "created_at": rnd_date(), "updated_at": rnd_date(),
    },
    {
        "id": rnd_id(), "email": "analyst@voltedge.demo",
        "hashed_password": DEMO_HASH, "full_name": "Maria Santos",
        "is_active": True, "is_platform_admin": False,
        "created_at": rnd_date(), "updated_at": rnd_date(),
    },
]
ADMIN_ID = USERS[0]["id"]
APEX_USER_ID = USERS[1]["id"]
VOLT_USER_ID = USERS[2]["id"]


# ─────────────────────────────────────────────
# MEMBERSHIPS
# ─────────────────────────────────────────────
MEMBERSHIPS = [
    {"id": rnd_id(), "user_id": ADMIN_ID, "company_id": APEX_ID, "role": "admin", "created_at": rnd_date()},
    {"id": rnd_id(), "user_id": ADMIN_ID, "company_id": VOLT_ID, "role": "admin", "created_at": rnd_date()},
    {"id": rnd_id(), "user_id": ADMIN_ID, "company_id": ORION_ID, "role": "admin", "created_at": rnd_date()},
    {"id": rnd_id(), "user_id": APEX_USER_ID, "company_id": APEX_ID, "role": "analyst", "created_at": rnd_date()},
    {"id": rnd_id(), "user_id": VOLT_USER_ID, "company_id": VOLT_ID, "role": "analyst", "created_at": rnd_date()},
]


# ─────────────────────────────────────────────
# SUPPLIERS — 55+
# ─────────────────────────────────────────────
# Key suppliers (fixed IDs for relationship wiring)
HELIOS_ID = rnd_id()     # THE shared upstream semiconductor manufacturer
NORTHSTAR_ID = rnd_id()  # direct to ApexDrive + VoltEdge
BLUEPEAK_ID = rnd_id()   # raw material
CIRROTECH_ID = rnd_id()  # direct to ApexDrive
ARCLIGHT_ID = rnd_id()   # direct to VoltEdge
SKYNODE_ID = rnd_id()    # direct to OrionTech
PEAKFORGE_ID = rnd_id()  # steel/aluminium
OMEGALOG_ID = rnd_id()   # logistics
HARBOUR_ID = rnd_id()    # port/hub
SILVERCORE_ID = rnd_id() # sub-tier manufacturer
TERRANOVA_ID = rnd_id()  # raw material (lithium)
AZURECHIP_ID = rnd_id()  # semiconductor assembler → Helios
QUANTUMTEK_ID = rnd_id() # direct to OrionTech
SOLARIS_ID = rnd_id()    # direct to ApexDrive
PINNACLE_ID = rnd_id()   # direct to VoltEdge
NEXUSFAB_ID = rnd_id()   # sub-tier to CirroTech
COBALT_ID = rnd_id()     # cobalt supplier for batteries
IRONVAULT_ID = rnd_id()  # precision metals
STARLITE_ID = rnd_id()   # optics/displays supplier
DEEPROOTS_ID = rnd_id()  # agricultural/industrial polymers
MIRAGE_ID = rnd_id()     # regional distributor
TITANWORKS_ID = rnd_id() # titanium parts manufacturer
RIVERTECH_ID = rnd_id()  # river logistics
ALPHACAST_ID = rnd_id()  # die-casting
PRISMCORE_ID = rnd_id()  # prism/lens supplier
CRYSTALTEK_ID = rnd_id() # crystal oscillators
WINDROSE_ID = rnd_id()   # shipping/freight
GOLDVEIN_ID = rnd_id()   # gold/precious metal
MERIDIAN_ID = rnd_id()   # sub-tier logistics
POLARIS_ID = rnd_id()    # polar region logistics
NOVALITH_ID = rnd_id()   # lithium refining
EMBERCORE_ID = rnd_id()  # thermal components
LUMINOS_ID = rnd_id()    # LED/lighting components
FERROSTEEL_ID = rnd_id() # specialty steel
DENSIFY_ID = rnd_id()    # compression / packaging
SOLVENT_ID = rnd_id()    # chemical solvents
TRIAXLE_ID = rnd_id()    # axle components
FLEXIWIRE_ID = rnd_id()  # wiring harnesses
MICROWAVE_ID = rnd_id()  # microwave components
GRAPHTEK_ID = rnd_id()   # graphene materials
SILICATEK_ID = rnd_id()  # silica / quartz
OHMFORM_ID = rnd_id()    # resistors/passives
PHOSCAPE_ID = rnd_id()   # photovoltaic components
ULTRACAST_ID = rnd_id()  # ultra-precision casting

def make_supplier(
    sid, company_id, name, stype, tier, region, risk, criticality,
    verification="verified", source_type="synthetic",
):
    return {
        "id": sid,
        "company_id": company_id,
        "name": name,
        "supplier_type": stype,
        "tier_level": tier,
        "risk_score": round(risk, 3),
        "criticality": criticality,
        "geographic_region": region,
        "verification_status": verification,
        "is_demo": True,
        "source_type": source_type,
        "source_name": "synthetic-seed",
        "confidence_score": round(random.uniform(0.7, 0.99), 3),
        "tenant_id": None,
        "created_at": rnd_date(),
        "updated_at": rnd_date(),
    }

SUPPLIERS = [
    # ── ApexDrive direct suppliers (tier 1)
    make_supplier(NORTHSTAR_ID, APEX_ID, "Northstar Precision Components", "direct", 1, "North America", 0.55, "critical"),
    make_supplier(CIRROTECH_ID, APEX_ID, "CirroTech Electronics", "direct", 1, "East Asia", 0.62, "critical"),
    make_supplier(SOLARIS_ID, APEX_ID, "Solaris Systems", "direct", 1, "Europe", 0.40, "high"),
    make_supplier(TRIAXLE_ID, APEX_ID, "TriAxle Components", "direct", 1, "North America", 0.38, "high"),
    make_supplier(FLEXIWIRE_ID, APEX_ID, "FlexiWire Harnesses", "direct", 1, "Southeast Asia", 0.45, "medium"),

    # ── VoltEdge direct suppliers (tier 1)
    make_supplier(ARCLIGHT_ID, VOLT_ID, "ArcLight Power Systems", "direct", 1, "East Asia", 0.65, "critical"),
    make_supplier(PINNACLE_ID, VOLT_ID, "Pinnacle Cell Technologies", "direct", 1, "Europe", 0.48, "high"),
    make_supplier(COBALT_ID, VOLT_ID, "Cobalt Dynamics", "direct", 1, "Africa", 0.72, "critical"),

    # ── OrionTech direct suppliers (tier 1)
    make_supplier(SKYNODE_ID, ORION_ID, "SkyNode Sensors", "direct", 1, "East Asia", 0.58, "critical"),
    make_supplier(QUANTUMTEK_ID, ORION_ID, "QuantumTek Devices", "direct", 1, "North America", 0.42, "high"),
    make_supplier(STARLITE_ID, ORION_ID, "Starlite Display Systems", "direct", 1, "East Asia", 0.50, "high"),
    make_supplier(LUMINOS_ID, ORION_ID, "Luminos Photonics", "direct", 1, "Europe", 0.35, "medium"),

    # ── Shared upstream (tier 2–3) — ALL companies
    make_supplier(HELIOS_ID, APEX_ID, "Helios Semiconductor Works", "manufacturer", 3, "East Asia", 0.88, "critical", "verified"),
    make_supplier(AZURECHIP_ID, APEX_ID, "AzureChip Assembly", "manufacturer", 2, "East Asia", 0.75, "critical"),
    make_supplier(SILICATEK_ID, APEX_ID, "SilicaTek Materials", "material", 4, "East Asia", 0.60, "high"),
    make_supplier(GRAPHTEK_ID, APEX_ID, "GraphTek Advanced Materials", "material", 4, "Europe", 0.52, "medium"),

    # ── Sub-tier / upstream for ApexDrive chain
    make_supplier(SILVERCORE_ID, APEX_ID, "SilverCore Fabrication", "subtier", 2, "North America", 0.44, "high"),
    make_supplier(PEAKFORGE_ID, APEX_ID, "PeakForge Metals", "material", 3, "North America", 0.41, "high"),
    make_supplier(IRONVAULT_ID, APEX_ID, "IronVault Precision", "subtier", 2, "Europe", 0.38, "medium"),
    make_supplier(FERROSTEEL_ID, APEX_ID, "FerroSteel Specialties", "material", 3, "Europe", 0.35, "medium"),
    make_supplier(ALPHACAST_ID, APEX_ID, "AlphaCast Manufacturing", "production_facility", 2, "North America", 0.40, "medium"),
    make_supplier(TITANWORKS_ID, APEX_ID, "TitanWorks Fabrication", "subtier", 3, "North America", 0.37, "medium"),
    make_supplier(NEXUSFAB_ID, APEX_ID, "NexusFab Precision", "subtier", 2, "East Asia", 0.55, "high"),
    make_supplier(OHMFORM_ID, APEX_ID, "OhmForm Electronics", "subtier", 2, "East Asia", 0.60, "high"),

    # ── Sub-tier / upstream for VoltEdge chain
    make_supplier(TERRANOVA_ID, VOLT_ID, "TerraNova Minerals", "material", 3, "South America", 0.70, "critical"),
    make_supplier(NOVALITH_ID, VOLT_ID, "Novalith Refining", "manufacturer", 2, "South America", 0.65, "critical"),
    make_supplier(COBALT_ID if False else rnd_id(), VOLT_ID, "BluePeak Materials", "material", 3, "Africa", 0.68, "critical"),  # BluePeak
    make_supplier(EMBERCORE_ID, VOLT_ID, "EmberCore Thermal", "subtier", 2, "Europe", 0.42, "high"),
    make_supplier(CRYSTALTEK_ID, VOLT_ID, "CrystalTek Oscillators", "subtier", 2, "East Asia", 0.55, "high"),

    # ── Sub-tier / upstream for OrionTech chain
    make_supplier(PRISMCORE_ID, ORION_ID, "PrismCore Optics", "subtier", 2, "Europe", 0.45, "high"),
    make_supplier(MICROWAVE_ID, ORION_ID, "MicroWave Components", "subtier", 2, "East Asia", 0.58, "high"),
    make_supplier(GOLDVEIN_ID, ORION_ID, "GoldVein Metals", "material", 3, "Africa", 0.72, "high"),
    make_supplier(PHOSCAPE_ID, ORION_ID, "PhosCapture PV Systems", "subtier", 2, "Europe", 0.40, "medium"),

    # ── Logistics / infrastructure (shared)
    make_supplier(OMEGALOG_ID, APEX_ID, "OmegaLogistics", "logistics", 1, "Global", 0.30, "high"),
    make_supplier(HARBOUR_ID, APEX_ID, "HarbourPoint Terminal", "port", 1, "East Asia", 0.25, "high"),
    make_supplier(RIVERTECH_ID, APEX_ID, "RiverTech Inland Logistics", "logistics", 2, "North America", 0.22, "medium"),
    make_supplier(WINDROSE_ID, APEX_ID, "WindRose Freight", "logistics", 2, "Global", 0.28, "medium"),
    make_supplier(MERIDIAN_ID, APEX_ID, "Meridian Distribution", "logistics", 2, "Europe", 0.26, "medium"),
    make_supplier(POLARIS_ID, APEX_ID, "Polaris Arctic Logistics", "logistics", 3, "North America", 0.35, "low"),

    # ── Additional upstream materials
    make_supplier(BLUEPEAK_ID, APEX_ID, "BluePeak Materials", "material", 3, "Africa", 0.65, "high"),
    make_supplier(DEEPROOTS_ID, APEX_ID, "DeepRoots Polymers", "material", 3, "North America", 0.33, "medium"),
    make_supplier(SOLVENT_ID, APEX_ID, "SolventChem Industries", "material", 4, "Europe", 0.38, "medium"),
    make_supplier(MIRAGE_ID, APEX_ID, "Mirage Regional Distributors", "logistics", 2, "Middle East", 0.42, "medium"),
    make_supplier(DENSIFY_ID, APEX_ID, "Densify Packaging", "subtier", 3, "Southeast Asia", 0.28, "low"),
    make_supplier(ULTRACAST_ID, APEX_ID, "UltraCast Precision Foundry", "production_facility", 2, "Europe", 0.40, "high"),
]

# Fix BluePeak — use actual constant
for s in SUPPLIERS:
    if s["name"] == "BluePeak Materials" and s["id"] != BLUEPEAK_ID:
        BLUEPEAK_ID = s["id"]
        break


# ─────────────────────────────────────────────
# RELATIONSHIPS — 60+
# ─────────────────────────────────────────────
def make_rel(from_id, to_id, rel_type, confidence=None, verification="verified", notes=""):
    return {
        "id": rnd_id(),
        "from_supplier_id": from_id,
        "to_supplier_id": to_id,
        "relationship_type": rel_type,
        "confidence_score": round(confidence or random.uniform(0.7, 0.95), 3),
        "verification_status": verification,
        "evidence_source": "synthetic data",
        "notes": notes,
        "source_type": "synthetic",
        "tenant_id": None,
        "effective_date": rnd_date(days_back=365),
        "created_at": rnd_date(),
        "updated_at": rnd_date(),
    }

# Direct supplier → company relationships (supplies = company purchases from supplier)
RELATIONSHIPS = [
    # ── ApexDrive purchases from its direct suppliers
    make_rel(CIRROTECH_ID, APEX_ID, "supplies", 0.99, notes="Primary electronics supplier"),
    make_rel(NORTHSTAR_ID, APEX_ID, "supplies", 0.99, notes="Primary precision components"),
    make_rel(SOLARIS_ID, APEX_ID, "supplies", 0.95),
    make_rel(TRIAXLE_ID, APEX_ID, "supplies", 0.92),
    make_rel(FLEXIWIRE_ID, APEX_ID, "supplies", 0.90),

    # ── VoltEdge purchases from its direct suppliers
    make_rel(ARCLIGHT_ID, VOLT_ID, "supplies", 0.99, notes="Primary power systems"),
    make_rel(NORTHSTAR_ID, VOLT_ID, "supplies", 0.95, notes="Shared with ApexDrive"),
    make_rel(PINNACLE_ID, VOLT_ID, "supplies", 0.93),
    make_rel(COBALT_ID, VOLT_ID, "supplies", 0.97),

    # ── OrionTech purchases from its direct suppliers
    make_rel(SKYNODE_ID, ORION_ID, "supplies", 0.99, notes="Primary sensors"),
    make_rel(QUANTUMTEK_ID, ORION_ID, "supplies", 0.95),
    make_rel(STARLITE_ID, ORION_ID, "supplies", 0.93),
    make_rel(LUMINOS_ID, ORION_ID, "supplies", 0.88),

    # ── THE KEY HIDDEN DEPENDENCY — all paths lead to Helios
    make_rel(CIRROTECH_ID, HELIOS_ID, "depends_on", 0.98, notes="CirroTech sources all ICs from Helios"),
    make_rel(NORTHSTAR_ID, HELIOS_ID, "depends_on", 0.97, notes="Northstar uses Helios chips in precision modules"),
    make_rel(ARCLIGHT_ID, HELIOS_ID, "depends_on", 0.96, notes="ArcLight BMS controllers sourced from Helios"),
    make_rel(SKYNODE_ID, AZURECHIP_ID, "depends_on", 0.95, notes="SkyNode sensors built on AzureChip modules"),
    make_rel(AZURECHIP_ID, HELIOS_ID, "manufactures", 0.99, notes="AzureChip assembles Helios wafers into modules"),
    make_rel(QUANTUMTEK_ID, HELIOS_ID, "depends_on", 0.90, notes="QuantumTek uses Helios FPGAs"),
    make_rel(PINNACLE_ID, HELIOS_ID, "depends_on", 0.88, notes="Pinnacle cell management ICs from Helios"),

    # ── Helios upstream
    make_rel(HELIOS_ID, SILICATEK_ID, "produces_from", 0.95, notes="Helios wafer fab uses SilicaTek silicon"),
    make_rel(HELIOS_ID, GRAPHTEK_ID, "produces_from", 0.85, notes="Advanced node processes use GraphTek materials"),
    make_rel(AZURECHIP_ID, BLUEPEAK_ID, "depends_on", 0.88, notes="AzureChip uses BluePeak substrates"),

    # ── Sub-tier for ApexDrive chain
    make_rel(CIRROTECH_ID, NEXUSFAB_ID, "depends_on", 0.85, notes="CirroTech PCB assemblies"),
    make_rel(NORTHSTAR_ID, SILVERCORE_ID, "depends_on", 0.90, notes="Northstar housings"),
    make_rel(NORTHSTAR_ID, IRONVAULT_ID, "depends_on", 0.82),
    make_rel(SILVERCORE_ID, PEAKFORGE_ID, "depends_on", 0.88, notes="Steel sourcing"),
    make_rel(SOLARIS_ID, ALPHACAST_ID, "depends_on", 0.85),
    make_rel(SOLARIS_ID, TITANWORKS_ID, "depends_on", 0.80),
    make_rel(TRIAXLE_ID, FERROSTEEL_ID, "depends_on", 0.87),
    make_rel(TRIAXLE_ID, ALPHACAST_ID, "depends_on", 0.82),
    make_rel(NEXUSFAB_ID, OHMFORM_ID, "depends_on", 0.85),
    make_rel(NEXUSFAB_ID, BLUEPEAK_ID, "depends_on", 0.82),
    make_rel(PEAKFORGE_ID, DEEPROOTS_ID, "depends_on", 0.80),
    make_rel(IRONVAULT_ID, FERROSTEEL_ID, "depends_on", 0.84),
    make_rel(ALPHACAST_ID, ULTRACAST_ID, "depends_on", 0.78),

    # ── Sub-tier for VoltEdge chain
    make_rel(COBALT_ID, TERRANOVA_ID, "depends_on", 0.92, notes="Cobalt source minerals from TerraNova"),
    make_rel(ARCLIGHT_ID, NOVALITH_ID, "depends_on", 0.90, notes="Lithium cells from Novalith"),
    make_rel(ARCLIGHT_ID, EMBERCORE_ID, "depends_on", 0.88),
    make_rel(NOVALITH_ID, TERRANOVA_ID, "produces_from", 0.95, notes="Lithium refined from TerraNova ore"),
    make_rel(PINNACLE_ID, CRYSTALTEK_ID, "depends_on", 0.85),
    make_rel(CRYSTALTEK_ID, SILICATEK_ID, "depends_on", 0.88, notes="Crystal growth requires SilicaTek quartz"),

    # ── Sub-tier for OrionTech chain
    make_rel(SKYNODE_ID, PRISMCORE_ID, "depends_on", 0.87),
    make_rel(STARLITE_ID, PRISMCORE_ID, "depends_on", 0.85, notes="Shared optics supplier"),
    make_rel(QUANTUMTEK_ID, MICROWAVE_ID, "depends_on", 0.83),
    make_rel(LUMINOS_ID, PHOSCAPE_ID, "depends_on", 0.80),
    make_rel(STARLITE_ID, GOLDVEIN_ID, "depends_on", 0.82, notes="Bonding wire gold"),
    make_rel(QUANTUMTEK_ID, GOLDVEIN_ID, "depends_on", 0.80, notes="Connector gold plating"),

    # ── Logistics relationships
    make_rel(OMEGALOG_ID, HARBOUR_ID, "transports_through", 0.90),
    make_rel(HELIOS_ID, HARBOUR_ID, "transports_through", 0.95, notes="Helios ships via HarbourPoint"),
    make_rel(AZURECHIP_ID, HARBOUR_ID, "transports_through", 0.92),
    make_rel(WINDROSE_ID, HARBOUR_ID, "transports_through", 0.88),
    make_rel(MERIDIAN_ID, OMEGALOG_ID, "transports_through", 0.85),
    make_rel(RIVERTECH_ID, MERIDIAN_ID, "transports_through", 0.80),
    make_rel(POLARIS_ID, RIVERTECH_ID, "transports_through", 0.75),

    # ── Material flows
    make_rel(TERRANOVA_ID, BLUEPEAK_ID, "produces_from", 0.85, notes="TerraNova also supplies BluePeak"),
    make_rel(SOLVENT_ID, NEXUSFAB_ID, "supplies", 0.78),
    make_rel(DENSIFY_ID, OMEGALOG_ID, "supplies", 0.75),
    make_rel(MIRAGE_ID, MERIDIAN_ID, "transports_through", 0.78),

    # ── Substitution relationships
    make_rel(AZURECHIP_ID, NEXUSFAB_ID, "substitutes_for", 0.70, "evidence_inference"),
    make_rel(NOVALITH_ID, COBALT_ID, "substitutes_for", 0.65, "evidence_inference"),
]


# ─────────────────────────────────────────────
# MATERIALS
# ─────────────────────────────────────────────
MATERIALS = [
    {"id": rnd_id(), "name": "Silicon Wafer 300mm", "material_type": "semiconductor", "unit": "wafer", "description": "High-purity 300mm silicon wafer", "source_type": "synthetic", "created_at": rnd_date()},
    {"id": rnd_id(), "name": "Lithium Carbonate", "material_type": "raw_material", "unit": "kg", "description": "Battery-grade lithium carbonate", "source_type": "synthetic", "created_at": rnd_date()},
    {"id": rnd_id(), "name": "Cobalt Sulfate", "material_type": "raw_material", "unit": "kg", "description": "Cobalt sulfate for NMC cathodes", "source_type": "synthetic", "created_at": rnd_date()},
    {"id": rnd_id(), "name": "Aluminium Alloy 6061", "material_type": "metal", "unit": "kg", "description": "Structural aluminium alloy", "source_type": "synthetic", "created_at": rnd_date()},
    {"id": rnd_id(), "name": "Steel HSLA 950", "material_type": "metal", "unit": "kg", "description": "High-strength low-alloy steel", "source_type": "synthetic", "created_at": rnd_date()},
    {"id": rnd_id(), "name": "Copper Foil 8µm", "material_type": "metal", "unit": "m2", "description": "Lithium battery copper current collector", "source_type": "synthetic", "created_at": rnd_date()},
    {"id": rnd_id(), "name": "Epoxy Resin FR4", "material_type": "polymer", "unit": "kg", "description": "PCB substrate resin", "source_type": "synthetic", "created_at": rnd_date()},
    {"id": rnd_id(), "name": "Gold Wire 25µm", "material_type": "precious_metal", "unit": "g", "description": "Semiconductor bonding wire", "source_type": "synthetic", "created_at": rnd_date()},
    {"id": rnd_id(), "name": "Neodymium Magnet N42", "material_type": "rare_earth", "unit": "piece", "description": "NdFeB permanent magnet", "source_type": "synthetic", "created_at": rnd_date()},
    {"id": rnd_id(), "name": "Optical Grade Glass", "material_type": "glass", "unit": "m2", "description": "Display-grade optical glass", "source_type": "synthetic", "created_at": rnd_date()},
]
MAT_IDS = [m["id"] for m in MATERIALS]


# ─────────────────────────────────────────────
# COMPONENTS — 30
# ─────────────────────────────────────────────
SUP_IDS = [s["id"] for s in SUPPLIERS]

COMPONENTS = []
COMP_DEFS = [
    ("Advanced Driver-Assist IC", "semiconductor", "ADI-7820", CIRROTECH_ID, 0, 285.00, 14),
    ("LiDAR Signal Processor", "semiconductor", "LSP-3300", CIRROTECH_ID, 1, 420.00, 21),
    ("Battery Management System IC", "semiconductor", "BMS-5500", ARCLIGHT_ID, 2, 180.00, 10),
    ("Precision Torque Sensor", "sensor", "PTS-1200", NORTHSTAR_ID, 3, 95.00, 18),
    ("High-Voltage Connector Assy", "connector", "HVC-880", NORTHSTAR_ID, 4, 48.50, 7),
    ("NMC 811 Cell Module", "battery", "NMC-811-M", ARCLIGHT_ID, 5, 2200.00, 45),
    ("FPGA Control Unit", "semiconductor", "FCU-4400", QUANTUMTEK_ID, 6, 340.00, 28),
    ("MEMS Accelerometer", "sensor", "MEA-660", SKYNODE_ID, 7, 22.50, 12),
    ("4K OLED Display Panel", "display", "ODP-4K-60", STARLITE_ID, 8, 185.00, 30),
    ("Axle Bearing Assembly", "mechanical", "ABA-2200", TRIAXLE_ID, 9, 120.00, 21),
    ("Wiring Harness Main", "wiring", "WHM-1500", FLEXIWIRE_ID, 10, 780.00, 35),
    ("Aluminium Structural Frame", "mechanical", "ASF-3300", SOLARIS_ID, 3, 1200.00, 42),
    ("Thermal Runaway Prevention Module", "safety", "TRP-220", ARCLIGHT_ID, 5, 95.00, 14),
    ("Optical Proximity Sensor", "sensor", "OPS-110", SKYNODE_ID, 7, 18.50, 10),
    ("Power Inverter Module 150kW", "power", "PIM-150K", ARCLIGHT_ID, 5, 3800.00, 60),
    ("Graphene Supercapacitor", "energy", "GSC-550F", QUANTUMTEK_ID, 6, 65.00, 20),
    ("Titanium Chassis Bracket", "mechanical", "TCB-880", SOLARIS_ID, 3, 320.00, 28),
    ("5G RF Transceiver Module", "rf", "RFT-5G-22", QUANTUMTEK_ID, 6, 145.00, 18),
    ("Pressure Die-Cast Housing", "mechanical", "PDH-4400", ALPHACAST_ID, 9, 88.00, 14),
    ("LED Driver IC", "semiconductor", "LDI-330", LUMINOS_ID, 8, 12.50, 8),
    ("Cobalt Cathode Precursor", "material", "CCP-111", COBALT_ID, 5, 48.00, 30),
    ("Lithium Anode Foil", "material", "LAF-200", ARCLIGHT_ID, 5, 35.00, 25),
    ("Steel Chassis Rail", "mechanical", "SCR-5500", PEAKFORGE_ID, 9, 420.00, 21),
    ("Crystal Oscillator 25MHz", "electronic", "CO-25M", CRYSTALTEK_ID, 6, 4.20, 12),
    ("High-K Dielectric Capacitor", "passive", "HKC-1206", OHMFORM_ID, 3, 0.85, 5),
    ("Optical Lens Array", "optics", "OLA-880", PRISMCORE_ID, 8, 68.00, 20),
    ("Flex PCB Assembly", "pcb", "FPA-3300", NEXUSFAB_ID, 3, 125.00, 18),
    ("Neodymium Motor Magnet", "magnetic", "NMM-42N", IRONVAULT_ID, 3, 28.50, 14),
    ("Thermal Interface Material", "thermal", "TIM-3.5W", EMBERCORE_ID, 6, 15.00, 7),
    ("Gold Bond Wire Spool", "material", "GBW-25U", GOLDVEIN_ID, 7, 2200.00, 45),
]

for i, (name, ctype, pnum, sup_id, mat_idx, price, lt) in enumerate(COMP_DEFS):
    COMPONENTS.append({
        "id": rnd_id(),
        "name": name,
        "component_type": ctype,
        "part_number": pnum,
        "description": f"Synthetic demo component: {name}",
        "supplier_id": sup_id,
        "material_id": MAT_IDS[mat_idx % len(MAT_IDS)],
        "unit_price": price,
        "currency": "USD",
        "lead_time_days": lt,
        "created_at": rnd_date(),
    })
COMP_IDS = [c["id"] for c in COMPONENTS]


# ─────────────────────────────────────────────
# PRODUCTS — 20
# ─────────────────────────────────────────────
PRODUCTS = []
PROD_DEFS = [
    # ApexDrive products
    (APEX_ID, "AX-7 Electric Drive Unit", "AX7-EDU", 12.0, 8500.0),
    (APEX_ID, "AX-5 Hybrid Powertrain", "AX5-HPT", 20.0, 6200.0),
    (APEX_ID, "SmartAxle Pro", "SAP-200", 35.0, 3800.0),
    (APEX_ID, "Autonomous Drive Controller", "ADC-900", 8.0, 12000.0),
    (APEX_ID, "Thermal Management System", "TMS-440", 25.0, 2200.0),
    (APEX_ID, "Brake-by-Wire Module", "BBW-330", 40.0, 1800.0),
    (APEX_ID, "Vehicle Control Unit", "VCU-880", 18.0, 4500.0),
    # VoltEdge products
    (VOLT_ID, "VE-100 Battery Pack 100kWh", "VE100-BP", 6.0, 28000.0),
    (VOLT_ID, "VE-50 Energy Storage Module", "VE50-ESM", 10.0, 14000.0),
    (VOLT_ID, "GridEdge Stationary Storage", "GE-500", 3.0, 85000.0),
    (VOLT_ID, "PowerCell BMS Platform", "PCB-220", 15.0, 8800.0),
    (VOLT_ID, "FastCharge Unit 350kW", "FCU-350", 5.0, 42000.0),
    (VOLT_ID, "Supercap Hybrid Module", "SHM-120", 8.0, 6500.0),
    # OrionTech products
    (ORION_ID, "OT-Pro Industrial Sensor Hub", "OT-ISH-10", 22.0, 4200.0),
    (ORION_ID, "OrionVision LiDAR System", "OV-LIDAR-3", 5.0, 18500.0),
    (ORION_ID, "EdgeCompute Module X1", "ECM-X1", 30.0, 2800.0),
    (ORION_ID, "5G-IoT Gateway v3", "5GG-V3", 18.0, 1900.0),
    (ORION_ID, "OT-Display 4K Industrial", "OT-D4K", 12.0, 3400.0),
    (ORION_ID, "SmartSensor Array 64ch", "SSA-64", 8.0, 7200.0),
    (ORION_ID, "OT-Connect Telematics Unit", "OCT-220", 25.0, 1200.0),
]

for company_id, name, code, demand, revenue in PROD_DEFS:
    PRODUCTS.append({
        "id": rnd_id(),
        "company_id": company_id,
        "name": name,
        "product_code": code,
        "description": f"Synthetic demo product: {name}",
        "daily_demand": demand,
        "revenue_per_unit": revenue,
        "currency": "USD",
        "created_at": rnd_date(),
    })
PROD_IDS = [p["id"] for p in PRODUCTS]


# ─────────────────────────────────────────────
# BILL OF MATERIALS
# ─────────────────────────────────────────────
BOM = []
# Each product uses 2-4 components
for i, prod in enumerate(PRODUCTS):
    n_comps = random.randint(2, 4)
    chosen = random.sample(range(len(COMPONENTS)), n_comps)
    for ci in chosen:
        BOM.append({
            "id": rnd_id(),
            "product_id": prod["id"],
            "component_id": COMP_IDS[ci],
            "quantity_required": round(random.uniform(1, 8), 1),
            "unit": "unit",
            "created_at": rnd_date(),
        })


# ─────────────────────────────────────────────
# INVENTORY — 25
# ─────────────────────────────────────────────
INVENTORY = []
for i in range(25):
    company = random.choice(COMPANIES)
    comp = random.choice(COMPONENTS)
    sup = random.choice(SUPPLIERS)
    qty = round(random.uniform(50, 5000), 1)
    daily = round(random.uniform(2, 50), 1)
    INVENTORY.append({
        "id": rnd_id(),
        "company_id": company["id"],
        "component_id": comp["id"],
        "supplier_id": sup["id"],
        "quantity_on_hand": qty,
        "unit": "unit",
        "snapshot_date": rnd_date(days_back=7),
        "days_of_supply": round(qty / daily, 1),
        "source_type": "synthetic",
        "created_at": rnd_date(days_back=7),
    })


# ─────────────────────────────────────────────
# DEMAND FORECASTS
# ─────────────────────────────────────────────
FORECASTS = []
for prod in PRODUCTS:
    for month_offset in range(3):
        forecast_date = NOW + timedelta(days=30 * month_offset)
        FORECASTS.append({
            "id": rnd_id(),
            "product_id": prod["id"],
            "forecast_date": forecast_date.isoformat(),
            "daily_demand": round(prod["daily_demand"] * random.uniform(0.9, 1.1), 2),
            "forecast_period_days": 30,
            "confidence": round(random.uniform(0.75, 0.95), 3),
            "created_at": rnd_date(),
        })


# ─────────────────────────────────────────────
# PURCHASE ORDERS — 15
# ─────────────────────────────────────────────
PO_STATUSES = ["approved", "issued", "received", "pending_approval", "draft"]
PURCHASE_ORDERS = []
PO_ITEMS = []
for i in range(15):
    company = random.choice(COMPANIES)
    supplier = random.choice(SUPPLIERS)
    po_id = rnd_id()
    total = round(random.uniform(50000, 2000000), 2)
    PURCHASE_ORDERS.append({
        "id": po_id,
        "company_id": company["id"],
        "supplier_id": supplier["id"],
        "order_number": f"PO-{2024}-{str(i+1).zfill(4)}",
        "status": random.choice(PO_STATUSES),
        "total_amount": total,
        "currency": "USD",
        "delivery_date": (NOW + timedelta(days=random.randint(14, 90))).isoformat(),
        "shipping_terms": random.choice(["FOB", "CIF", "EXW", "DDP"]),
        "payment_terms": random.choice(["Net30", "Net60", "Prepaid"]),
        "approval_status": "approved",
        "approved_by_id": ADMIN_ID,
        "is_demo": True,
        "source_type": "synthetic",
        "created_at": rnd_date(),
        "updated_at": rnd_date(),
    })
    for _ in range(random.randint(1, 3)):
        comp = random.choice(COMPONENTS)
        qty = round(random.uniform(10, 500), 0)
        PO_ITEMS.append({
            "id": rnd_id(),
            "order_id": po_id,
            "component_id": comp["id"],
            "quantity": qty,
            "unit_price": comp["unit_price"],
            "currency": "USD",
            "description": comp["name"],
            "created_at": rnd_date(),
        })


# ─────────────────────────────────────────────
# ALTERNATIVE SUPPLIERS — 20
# ─────────────────────────────────────────────
ALT_SUPPLIERS = []
for i in range(20):
    company = random.choice(COMPANIES)
    comp = random.choice(COMPONENTS)
    sup = random.choice(SUPPLIERS)
    compat = round(random.uniform(0.5, 0.95), 3)
    cap = round(random.uniform(0.4, 1.0), 3)
    rel = round(random.uniform(0.6, 0.98), 3)
    geo = round(random.uniform(0.1, 0.8), 3)
    conc = round(random.uniform(0.1, 0.7), 3)
    lt = random.randint(14, 90)
    overall = round((compat * 0.25 + cap * 0.20 + rel * 0.20 + (1 - geo) * 0.15 + (1 - conc) * 0.10 + max(0, 1 - lt / 120) * 0.10), 4)
    ALT_SUPPLIERS.append({
        "id": rnd_id(),
        "company_id": company["id"],
        "component_id": comp["id"],
        "supplier_id": sup["id"],
        "compatibility_score": compat,
        "capacity_score": cap,
        "lead_time_days": lt,
        "quality_cert": random.choice(["ISO9001", "IATF16949", "AS9100", None]),
        "geographic_exposure_score": geo,
        "concentration_score": conc,
        "reliability_score": rel,
        "switching_cost_estimate": round(random.uniform(10000, 500000), 2),
        "overall_score": overall,
        "notes": "Synthetic alternative supplier record",
        "verification_status": random.choice(["unverified", "verified", "shortlisted"]),
        "source_type": "synthetic",
        "created_at": rnd_date(),
    })


# ─────────────────────────────────────────────
# DISRUPTIONS — 20
# ─────────────────────────────────────────────
DISRUPTION_TYPES = ["supply_shortage", "logistics", "facility_damage", "geopolitical", "labor", "cyber", "natural_disaster", "financial"]
SEVERITIES = ["low", "medium", "high", "critical"]
DISR_STATUSES = ["active", "resolved", "simulated"]
DISRUPTIONS = []
for i in range(20):
    company = random.choice(COMPANIES)
    sup = random.choice(SUPPLIERS)
    start = NOW - timedelta(days=random.randint(0, 180))
    DISRUPTIONS.append({
        "id": rnd_id(),
        "company_id": company["id"],
        "name": f"Disruption Event {i+1}: {random.choice(DISRUPTION_TYPES).replace('_', ' ').title()}",
        "disruption_type": random.choice(DISRUPTION_TYPES),
        "affected_supplier_id": sup["id"],
        "status": random.choice(DISR_STATUSES),
        "severity": random.choice(SEVERITIES),
        "start_date": start.isoformat(),
        "end_date": (start + timedelta(days=random.randint(7, 120))).isoformat() if random.random() > 0.3 else None,
        "capacity_reduction_pct": round(random.uniform(20, 100), 1),
        "description": f"Synthetic disruption event affecting {sup['name']}",
        "source_type": "synthetic",
        "created_at": rnd_date(),
    })


# ─────────────────────────────────────────────
# SCENARIOS — 10
# ─────────────────────────────────────────────
SCENARIOS = []
SCENARIO_DEFS = [
    (APEX_ID, "Helios Semiconductor Shutdown", "supply_shortage", HELIOS_ID, 90, 100.0, True),
    (APEX_ID, "HarbourPoint Terminal Closure", "logistics", HARBOUR_ID, 30, 80.0, False),
    (VOLT_ID, "TerraNova Mining Halt", "natural_disaster", TERRANOVA_ID, 60, 100.0, False),
    (VOLT_ID, "ArcLight Factory Fire", "facility_damage", ARCLIGHT_ID, 45, 100.0, False),
    (ORION_ID, "SkyNode Geopolitical Ban", "geopolitical", SKYNODE_ID, 180, 100.0, True),
    (ORION_ID, "AzureChip Cyber Attack", "cyber", AZURECHIP_ID, 14, 80.0, False),
    (APEX_ID, "CirroTech Labour Strike", "labor", CIRROTECH_ID, 21, 90.0, False),
    (VOLT_ID, "Cobalt Dynamics Bankruptcy", "financial", COBALT_ID, 365, 100.0, True),
    (ORION_ID, "QuantumTek Supply Shortage", "supply_shortage", QUANTUMTEK_ID, 60, 70.0, False),
    (APEX_ID, "NexusFab Quality Crisis", "quality", NEXUSFAB_ID, 30, 50.0, False),
]

for company_id, name, dtype, target_id, dur, cap_red, is_pre in SCENARIO_DEFS:
    SCENARIOS.append({
        "id": rnd_id(),
        "company_id": company_id,
        "name": name,
        "description": f"Synthetic scenario: {name}",
        "disruption_type": dtype,
        "target_supplier_id": target_id,
        "duration_days": dur,
        "capacity_reduction_pct": cap_red,
        "start_date": NOW.isoformat(),
        "inventory_assumption": "current",
        "demand_level": "baseline",
        "recovery_lead_time_days": random.randint(30, 120),
        "substitute_availability": random.choice(["none", "partial", "full"]),
        "status": "draft",
        "created_by_id": ADMIN_ID,
        "is_predefined": is_pre,
        "created_at": rnd_date(),
        "updated_at": rnd_date(),
    })
SCEN_IDS = [s["id"] for s in SCENARIOS]


# ─────────────────────────────────────────────
# RISK FINDINGS — 15
# ─────────────────────────────────────────────
FINDING_TYPES = ["hidden_dependency", "concentration", "single_point_of_failure", "geographic_exposure"]
RISK_FINDINGS = []

# Key pre-seeded finding about Helios
helios_finding_id = rnd_id()
RISK_FINDINGS.append({
    "id": helios_finding_id,
    "company_id": APEX_ID,
    "finding_type": "hidden_dependency",
    "title": "Hidden Shared Dependency on Helios Semiconductor Works",
    "description": (
        "4 direct suppliers (CirroTech Electronics, Northstar Precision Components, "
        "ArcLight Power Systems, SkyNode Sensors via AzureChip) all depend on "
        "Helios Semiconductor Works upstream. A single disruption at Helios cascades "
        "to all simultaneously, creating a hidden single point of failure."
    ),
    "shared_upstream_supplier_id": HELIOS_ID,
    "severity": "critical",
    "status": "open",
    "confidence_score": 0.97,
    "affected_suppliers_json": json.dumps([CIRROTECH_ID, NORTHSTAR_ID, ARCLIGHT_ID, SKYNODE_ID]),
    "affected_products_json": json.dumps(PROD_IDS[:7]),
    "dependency_paths_json": json.dumps({
        CIRROTECH_ID: [[CIRROTECH_ID, HELIOS_ID]],
        NORTHSTAR_ID: [[NORTHSTAR_ID, HELIOS_ID]],
        ARCLIGHT_ID: [[ARCLIGHT_ID, HELIOS_ID]],
        SKYNODE_ID: [[SKYNODE_ID, AZURECHIP_ID, HELIOS_ID]],
    }),
    "evidence_json": json.dumps({"betweenness": 0.45, "concentration": 0.82}),
    "recommended_action": "Dual-source semiconductor ICs from a non-Helios foundry; qualify GlobalFoundries or TSMC as alternatives.",
    "analyst_notes": None,
    "analyst_id": None,
    "source_type": "synthetic",
    "created_at": rnd_date(),
    "updated_at": rnd_date(),
})

# HarbourPoint concentration
RISK_FINDINGS.append({
    "id": rnd_id(),
    "company_id": APEX_ID,
    "finding_type": "concentration",
    "title": "Port Concentration Risk: HarbourPoint Terminal",
    "description": "85% of East Asia shipments route through HarbourPoint Terminal, creating severe logistics concentration.",
    "shared_upstream_supplier_id": HARBOUR_ID,
    "severity": "high",
    "status": "open",
    "confidence_score": 0.91,
    "affected_suppliers_json": json.dumps([HELIOS_ID, AZURECHIP_ID, CIRROTECH_ID]),
    "affected_products_json": json.dumps(PROD_IDS[:3]),
    "dependency_paths_json": None,
    "evidence_json": None,
    "recommended_action": "Negotiate backup port agreements with NanPort and ShenzhenEast terminals.",
    "analyst_notes": None,
    "analyst_id": None,
    "source_type": "synthetic",
    "created_at": rnd_date(),
    "updated_at": rnd_date(),
})

# Geographic exposure — Africa cobalt
RISK_FINDINGS.append({
    "id": rnd_id(),
    "company_id": VOLT_ID,
    "finding_type": "geographic_exposure",
    "title": "Geographic Concentration: Africa Cobalt Supply",
    "description": "72% of cobalt sourcing is concentrated in single African nation with high geopolitical risk rating.",
    "shared_upstream_supplier_id": COBALT_ID,
    "severity": "high",
    "status": "investigating",
    "confidence_score": 0.88,
    "affected_suppliers_json": json.dumps([COBALT_ID, TERRANOVA_ID]),
    "affected_products_json": json.dumps(PROD_IDS[7:13]),
    "dependency_paths_json": None,
    "evidence_json": None,
    "recommended_action": "Qualify Australian and Chilean cobalt suppliers; invest in cobalt-free cell chemistry R&D.",
    "analyst_notes": "Reviewing alternative suppliers in Q3 2024.",
    "analyst_id": ADMIN_ID,
    "source_type": "synthetic",
    "created_at": rnd_date(),
    "updated_at": rnd_date(),
})

# Fill remaining 12 findings
for i in range(12):
    company = random.choice(COMPANIES)
    RISK_FINDINGS.append({
        "id": rnd_id(),
        "company_id": company["id"],
        "finding_type": random.choice(FINDING_TYPES),
        "title": f"Risk Finding {i+4}: {random.choice(FINDING_TYPES).replace('_', ' ').title()} Event",
        "description": f"Synthetic risk finding #{i+4} for demo purposes.",
        "shared_upstream_supplier_id": random.choice(SUP_IDS),
        "severity": random.choice(SEVERITIES),
        "status": random.choice(["open", "investigating", "verified", "resolved"]),
        "confidence_score": round(random.uniform(0.5, 0.97), 3),
        "affected_suppliers_json": json.dumps(random.sample(SUP_IDS, 2)),
        "affected_products_json": json.dumps(random.sample(PROD_IDS, 2)),
        "dependency_paths_json": None,
        "evidence_json": None,
        "recommended_action": "Review and address supply chain exposure.",
        "analyst_notes": None,
        "analyst_id": None,
        "source_type": "synthetic",
        "created_at": rnd_date(),
        "updated_at": rnd_date(),
    })


# ─────────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────────
NOTIFICATIONS = []
for user in USERS:
    for j in range(3):
        NOTIFICATIONS.append({
            "id": rnd_id(),
            "user_id": user["id"],
            "company_id": random.choice([APEX_ID, VOLT_ID, ORION_ID]),
            "title": f"Demo Notification {j+1}",
            "message": "This is a synthetic notification for demo purposes.",
            "notification_type": random.choice(["risk_alert", "scenario_complete", "import_done"]),
            "is_read": random.choice([True, False]),
            "related_entity_type": "RiskFinding",
            "related_entity_id": helios_finding_id,
            "created_at": rnd_date(),
        })


# ─────────────────────────────────────────────
# WRITE ALL FILES
# ─────────────────────────────────────────────
print("\nGenerating demo data files...")

write_json("companies.json", COMPANIES)
write_json("users.json", USERS)
write_json("memberships.json", MEMBERSHIPS)
write_csv("suppliers.csv", SUPPLIERS)
write_csv("relationships.csv", RELATIONSHIPS)
write_json("materials.json", MATERIALS)
write_json("components.json", COMPONENTS)
write_json("products.json", PRODUCTS)
write_json("bom.json", BOM)
write_json("inventory.json", INVENTORY)
write_json("demand_forecasts.json", FORECASTS)
write_json("purchase_orders.json", PURCHASE_ORDERS)
write_json("purchase_order_items.json", PO_ITEMS)
write_json("alternative_suppliers.json", ALT_SUPPLIERS)
write_json("disruptions.json", DISRUPTIONS)
write_json("scenarios.json", SCENARIOS)
write_json("risk_findings.json", RISK_FINDINGS)
write_json("notifications.json", NOTIFICATIONS)

print(f"\nDemo data generation complete! Files saved to: {DEMO_DIR}")
print(f"   Companies: {len(COMPANIES)}")
print(f"   Users: {len(USERS)}")
print(f"   Suppliers: {len(SUPPLIERS)}")
print(f"   Relationships: {len(RELATIONSHIPS)}")
print(f"   Components: {len(COMPONENTS)}")
print(f"   Products: {len(PRODUCTS)}")
print(f"   BOM entries: {len(BOM)}")
print(f"   Inventory records: {len(INVENTORY)}")
print(f"   Purchase orders: {len(PURCHASE_ORDERS)}")
print(f"   Scenarios: {len(SCENARIOS)}")
print(f"   Risk findings: {len(RISK_FINDINGS)}")
