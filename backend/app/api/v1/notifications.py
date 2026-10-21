from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Notification, User
from app.schemas.schemas import NotificationRead
from app.deps import get_current_user
from app.services.notification_service import get_user_notifications, mark_read, mark_all_read

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationRead])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_notifications(db, current_user.id)


@router.put("/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notif = mark_read(db, notification_id, current_user.id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"id": notification_id, "is_read": True}


@router.put("/read-all/batch")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = mark_all_read(db, current_user.id)
    return {"marked_read": count}
