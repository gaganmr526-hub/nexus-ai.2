from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import AuditLog, User
from app.schemas.schemas import AuditLogRead
from app.deps import get_current_user, require_company_access

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs", response_model=list[AuditLogRead])
def get_audit_logs(
    company_id: str = Query(...),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(company_id, db, current_user)
    return (
        db.query(AuditLog)
        .filter(AuditLog.company_id == company_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )
