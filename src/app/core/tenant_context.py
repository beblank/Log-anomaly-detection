"""Tenant context middleware for request isolation."""
from typing import Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and validate tenant context from requests."""
    
    async def dispatch(self, request: Request, call_next):
        # Extract tenant ID from header
        tenant_id = request.headers.get("X-Tenant-ID")
        
        # Skip tenant validation for health checks and public endpoints
        public_paths = ["/health", "/docs", "/openapi.json", "/api/v1/tenants"]
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)
        
        if not tenant_id:
            raise HTTPException(
                status_code=400,
                detail="X-Tenant-ID header is required"
            )
        
        # Store tenant ID in request state for use in endpoints
        request.state.tenant_id = tenant_id
        
        response = await call_next(request)
        return response


def get_tenant_id(request: Request) -> str:
    """Extract tenant ID from request state."""
    if not hasattr(request.state, "tenant_id"):
        raise HTTPException(
            status_code=400,
            detail="Tenant context not found"
        )
    return request.state.tenant_id
