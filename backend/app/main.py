from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.changes import router as changes_router
from backend.app.api.companies import router as companies_router
from backend.app.api.intelligence import router as intelligence_router
from backend.app.config import settings
from backend.app.database.database import Base, engine
from backend.app.models.change import FactChange


# Create any missing database tables.
# Existing tables and data are preserved.
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Signalpost",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(companies_router)
app.include_router(intelligence_router)
app.include_router(changes_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }