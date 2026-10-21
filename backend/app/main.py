from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api.v1.router import router

# Import all models so SQLAlchemy registers them
import app.models.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup (dev convenience; prod uses Alembic)
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: nothing to clean up for SQLite


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="NEXUSTRACE AI — Enterprise Supply-Chain Intelligence Platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} backend is running", "docs": "/docs"}
