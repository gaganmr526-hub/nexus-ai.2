from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import AlternativeSupplier, User
from app.schemas.schemas import AlternativeSupplierRead
from app.deps import get_current_user, require_company_access
from app.services.alternative_service import rank_alternatives, compare_suppliers
from pydantic import BaseModel

router = APIRouter(prefix="/alternatives", tags=["alternatives"])


class CompareRequest(BaseModel):
    supplier_ids: list[str]
    company_id: str


@router.get("", response_model=list[AlternativeSupplierRead])
def list_alternatives(
    company_id: str = Query(...),
    component_id: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(company_id, db, current_user)
    return rank_alternatives(db, company_id, component_id)


@router.post("/{alt_id}/shortlist")
def shortlist(
    alt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alt = db.query(AlternativeSupplier).filter(AlternativeSupplier.id == alt_id).first()
    if not alt:
        raise HTTPException(status_code=404, detail="Alternative supplier not found")
    require_company_access(alt.company_id, db, current_user)
    alt.verification_status = "shortlisted"
    db.commit()
    return {"id": alt_id, "status": "shortlisted"}


@router.post("/compare")
def compare(
    data: CompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(data.company_id, db, current_user)
    return compare_suppliers(db, data.supplier_ids, data.company_id)
