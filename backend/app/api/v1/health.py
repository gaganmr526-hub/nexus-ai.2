from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def liveness():
    return {
        "status": "ok",
        "version": "1.0.0",
        "app_name": settings.APP_NAME,
    }


@router.get("/ready")
def readiness(db: Session = Depends(get_db)):
    db_status = "ok"
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {e}"

    overall = "ok" if db_status == "ok" else "degraded"
    return {
        "status": overall,
        "database": db_status,
        "checks": {
            "database": db_status,
        },
    }
