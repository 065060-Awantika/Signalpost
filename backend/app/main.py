from fastapi import FastAPI

from backend.app.api.companies import router as companies_router
from backend.app.config import settings


app = FastAPI(
    title="Signalpost",
    version="0.1.0",
)

app.include_router(companies_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }