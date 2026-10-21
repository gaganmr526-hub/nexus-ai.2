from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.models import User
from app.security.auth import hash_password, verify_password, create_access_token
import uuid


def register_user(db: Session, email: str, password: str, full_name: str | None = None, is_platform_admin: bool = False) -> User:
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        is_active=True,
        is_platform_admin=is_platform_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_token_for_user(user: User) -> str:
    return create_access_token({"sub": user.id})
