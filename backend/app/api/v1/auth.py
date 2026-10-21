from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import UserCreate, UserRead, Token, LoginRequest
from app.services.auth_service import register_user, authenticate_user, create_token_for_user
from app.deps import get_current_user, check_rate_limit, require_platform_admin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(
    data: UserCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(require_platform_admin),  # open for initial setup
):
    return register_user(db, data.email, data.password, data.full_name)


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    check_rate_limit(data.email)
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User account is inactive")
    token = create_token_for_user(user)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user
