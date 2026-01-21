"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .core.config import get_settings
from .core.database import init_db
from .core.tenant_context import TenantContextMiddleware
from .api.v1 import tenants, models, monitoring
from .monitoring.prometheus_metrics import metrics_exporter

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-Tenant ML SaaS Platform for Log Anomaly Detection with Auto-Retraining & Monitoring"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add tenant context middleware
app.add_middleware(TenantContextMiddleware)

# Include routers
app.include_router(tenants.router, prefix=settings.API_V1_PREFIX)
app.include_router(models.router, prefix=settings.API_V1_PREFIX)
app.include_router(monitoring.router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    # Initialize database
    init_db()
    
    # Start Prometheus metrics server
    try:
        metrics_exporter.start()
    except Exception as e:
        print(f"Warning: Failed to start Prometheus metrics server: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Multi-Tenant ML SaaS Platform",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


def main():
    """Run the application."""
    uvicorn.run(
        "src.app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )


if __name__ == "__main__":
    main()
