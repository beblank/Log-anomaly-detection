"""Tenant API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.schemas import TenantCreate, TenantResponse
from ...services.tenant_service import TenantService

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("/", response_model=TenantResponse, status_code=201)
def create_tenant(
    tenant_data: TenantCreate,
    db: Session = Depends(get_db)
):
    """Create a new tenant with isolated resources."""
    service = TenantService(db)
    return service.create_tenant(tenant_data)


@router.get("/", response_model=List[TenantResponse])
def list_tenants(db: Session = Depends(get_db)):
    """List all tenants."""
    service = TenantService(db)
    return service.list_tenants()


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(tenant_id: str, db: Session = Depends(get_db)):
    """Get tenant by ID."""
    service = TenantService(db)
    tenant = service.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.delete("/{tenant_id}", status_code=204)
def delete_tenant(tenant_id: str, db: Session = Depends(get_db)):
    """Delete tenant and cleanup resources."""
    service = TenantService(db)
    if not service.delete_tenant(tenant_id):
        raise HTTPException(status_code=404, detail="Tenant not found")
    return None
