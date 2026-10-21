from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Supplier, User
from app.schemas.schemas import SupplierCreate, SupplierUpdate, SupplierRead
from app.deps import get_current_user, require_company_access
from app.graph.builder import get_upstream_ancestors, get_downstream_descendants, build_graph
import uuid
from datetime import datetime

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("", response_model=list[SupplierRead])
def list_suppliers(
    company_id: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Supplier)
    if company_id:
        require_company_access(company_id, db, current_user)
        q = q.filter(Supplier.company_id == company_id)
    elif not current_user.is_platform_admin:
        from app.models.models import CompanyMembership
        ids = [m.company_id for m in db.query(CompanyMembership).filter(
            CompanyMembership.user_id == current_user.id).all()]
        q = q.filter(Supplier.company_id.in_(ids))
    return q.all()


@router.post("", response_model=SupplierRead, status_code=201)
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_company_access(data.company_id, db, current_user)
    supplier = Supplier(id=str(uuid.uuid4()), **data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.get("/{supplier_id}", response_model=SupplierRead)
def get_supplier(supplier_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    require_company_access(supplier.company_id, db, current_user)
    return supplier


@router.put("/{supplier_id}", response_model=SupplierRead)
def update_supplier(supplier_id: str, data: SupplierUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    require_company_access(supplier.company_id, db, current_user)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(supplier, k, v)
    supplier.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}", status_code=204)
def delete_supplier(supplier_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    require_company_access(supplier.company_id, db, current_user)
    db.delete(supplier)
    db.commit()


@router.get("/{supplier_id}/upstream")
def get_upstream(supplier_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    require_company_access(supplier.company_id, db, current_user)
    G = build_graph(db)
    ancestors = get_upstream_ancestors(G, supplier_id)
    result = []
    for anc_id in ancestors:
        anc = db.query(Supplier).filter(Supplier.id == anc_id).first()
        if anc:
            result.append({"id": anc.id, "name": anc.name, "supplier_type": anc.supplier_type,
                           "tier_level": anc.tier_level})
    return {"supplier_id": supplier_id, "upstream_count": len(result), "upstream": result}


@router.get("/{supplier_id}/downstream")
def get_downstream(supplier_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    require_company_access(supplier.company_id, db, current_user)
    G = build_graph(db)
    descendants = get_downstream_descendants(G, supplier_id)
    result = []
    for desc_id in descendants:
        desc = db.query(Supplier).filter(Supplier.id == desc_id).first()
        if desc:
            result.append({"id": desc.id, "name": desc.name, "supplier_type": desc.supplier_type,
                           "tier_level": desc.tier_level})
    return {"supplier_id": supplier_id, "downstream_count": len(result), "downstream": result}
