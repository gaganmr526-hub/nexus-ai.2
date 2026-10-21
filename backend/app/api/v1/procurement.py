from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import PurchaseOrder, PurchaseOrderItem, User
from app.schemas.schemas import PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderRead, PurchaseOrderItemCreate, PurchaseOrderItemRead
from app.deps import get_current_user, require_company_access
import uuid
from datetime import datetime

router = APIRouter(prefix="/procurement", tags=["procurement"])


@router.get("/purchase-orders", response_model=list[PurchaseOrderRead])
def list_pos(
    company_id: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(PurchaseOrder)
    if company_id:
        require_company_access(company_id, db, current_user)
        q = q.filter(PurchaseOrder.company_id == company_id)
    return q.order_by(PurchaseOrder.created_at.desc()).all()


@router.post("/purchase-orders", response_model=PurchaseOrderRead, status_code=201)
def create_po(
    data: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(data.company_id, db, current_user)
    po = PurchaseOrder(
        id=str(uuid.uuid4()),
        order_number=data.order_number or f"PO-{uuid.uuid4().hex[:8].upper()}",
        **data.model_dump(),
    )
    db.add(po)
    db.commit()
    db.refresh(po)
    return po


@router.get("/purchase-orders/{po_id}", response_model=PurchaseOrderRead)
def get_po(po_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    require_company_access(po.company_id, db, current_user)
    return po


@router.put("/purchase-orders/{po_id}", response_model=PurchaseOrderRead)
def update_po(
    po_id: str,
    data: PurchaseOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    require_company_access(po.company_id, db, current_user)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(po, k, v)
    po.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(po)
    return po


@router.post("/purchase-orders/{po_id}/approve")
def approve_po(
    po_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    require_company_access(po.company_id, db, current_user)
    po.status = "approved"
    po.approval_status = "approved"
    po.approved_by_id = current_user.id
    po.updated_at = datetime.utcnow()
    db.commit()
    return {"id": po_id, "status": "approved"}


@router.get("/requisitions", response_model=list[PurchaseOrderRead])
def list_requisitions(
    company_id: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(PurchaseOrder).filter(PurchaseOrder.status == "draft")
    if company_id:
        require_company_access(company_id, db, current_user)
        q = q.filter(PurchaseOrder.company_id == company_id)
    return q.all()


@router.post("/requisitions", response_model=PurchaseOrderRead, status_code=201)
def create_requisition(
    data: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(data.company_id, db, current_user)
    po = PurchaseOrder(
        id=str(uuid.uuid4()),
        status="draft",
        order_number=data.order_number or f"REQ-{uuid.uuid4().hex[:8].upper()}",
        **data.model_dump(),
    )
    db.add(po)
    db.commit()
    db.refresh(po)
    return po
