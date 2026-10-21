import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import Notification, User


def create_notification(
    db: Session,
    user_id: str,
    title: str,
    message: str | None = None,
    notification_type: str | None = None,
    company_id: str | None = None,
    related_entity_type: str | None = None,
    related_entity_id: str | None = None,
) -> Notification:
    notif = Notification(
        id=str(uuid.uuid4()),
        user_id=user_id,
        company_id=company_id,
        title=title,
        message=message,
        notification_type=notification_type,
        is_read=False,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def get_user_notifications(db: Session, user_id: str) -> list[Notification]:
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )


def mark_read(db: Session, notification_id: str, user_id: str) -> Notification | None:
    notif = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == user_id)
        .first()
    )
    if notif:
        notif.is_read = True
        db.commit()
    return notif


def mark_all_read(db: Session, user_id: str) -> int:
    updated = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read == False)
        .all()
    )
    for n in updated:
        n.is_read = True
    db.commit()
    return len(updated)
