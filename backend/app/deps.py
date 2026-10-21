from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, CompanyMembership
from app.security.auth import decode_token

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise exc
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise exc
    user_id: str = payload.get("sub")
    if user_id is None:
        raise exc
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if user is None:
        raise exc
    return user


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User | None:
    if credentials is None:
        return None
    payload = decode_token(credentials.credentials)
    if payload is None:
        return None
    user_id: str = payload.get("sub")
    if user_id is None:
        return None
    return db.query(User).filter(User.id == user_id, User.is_active == True).first()


def require_platform_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_platform_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Platform admin required")
    return current_user


def require_company_access(company_id: str, db: Session, current_user: User) -> None:
    """Raises 403 if user is not a member of the company (admins bypass)."""
    if current_user.is_platform_admin:
        return
    membership = (
        db.query(CompanyMembership)
        .filter(
            CompanyMembership.user_id == current_user.id,
            CompanyMembership.company_id == company_id,
        )
        .first()
    )
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this company")


def get_accessible_company_ids(db: Session, current_user: User) -> list[str]:
    if current_user.is_platform_admin:
        from app.models.models import Company
        return [c.id for c in db.query(Company.id).all()]
    memberships = (
        db.query(CompanyMembership)
        .filter(CompanyMembership.user_id == current_user.id)
        .all()
    )
    return [m.company_id for m in memberships]


# Simple in-memory rate limiter for auth endpoints
_login_attempts: dict[str, list] = {}


def check_rate_limit(email: str, max_attempts: int = 10, window_seconds: int = 300) -> None:
    from datetime import datetime
    now = datetime.utcnow()
    attempts = _login_attempts.get(email, [])
    cutoff = now.timestamp() - window_seconds
    attempts = [t for t in attempts if t > cutoff]
    if len(attempts) >= max_attempts:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
        )
    attempts.append(now.timestamp())
    _login_attempts[email] = attempts
