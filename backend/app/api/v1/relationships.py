from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import SupplierRelationship, RelationshipEvidence, User
from app.schemas.schemas import RelationshipCreate, RelationshipUpdate, RelationshipRead, EvidenceCreate, EvidenceRead
from app.deps import get_current_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/relationships", tags=["relationships"])


@router.get("", response_model=list[RelationshipRead])
def list_relationships(
    from_supplier_id: str | None = Query(None),
    to_supplier_id: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(SupplierRelationship)
    if from_supplier_id:
        q = q.filter(SupplierRelationship.from_supplier_id == from_supplier_id)
    if to_supplier_id:
        q = q.filter(SupplierRelationship.to_supplier_id == to_supplier_id)
    return q.limit(500).all()


@router.post("", response_model=RelationshipRead, status_code=201)
def create_relationship(data: RelationshipCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rel = SupplierRelationship(id=str(uuid.uuid4()), **data.model_dump())
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


@router.get("/{rel_id}", response_model=RelationshipRead)
def get_relationship(rel_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rel = db.query(SupplierRelationship).filter(SupplierRelationship.id == rel_id).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")
    return rel


@router.put("/{rel_id}", response_model=RelationshipRead)
def update_relationship(rel_id: str, data: RelationshipUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rel = db.query(SupplierRelationship).filter(SupplierRelationship.id == rel_id).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(rel, k, v)
    rel.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(rel)
    return rel


@router.get("/{rel_id}/evidence", response_model=list[EvidenceRead])
def get_evidence(rel_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(RelationshipEvidence).filter(RelationshipEvidence.relationship_id == rel_id).all()


@router.post("/{rel_id}/evidence", response_model=EvidenceRead, status_code=201)
def add_evidence(rel_id: str, data: EvidenceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rel = db.query(SupplierRelationship).filter(SupplierRelationship.id == rel_id).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")
    ev = RelationshipEvidence(id=str(uuid.uuid4()), relationship_id=rel_id, **data.model_dump())
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev
