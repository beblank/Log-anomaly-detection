"""Model management API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import pandas as pd

from ...core.database import get_db
from ...core.tenant_context import get_tenant_id
from ...models.schemas import ModelMetadataResponse, TrainingRequest
from ...ml_pipeline.training_service import MLTrainingService
from ...ml_pipeline.deployment_service import ModelDeploymentService
from ...models.database import ModelMetadata

router = APIRouter(prefix="/models", tags=["models"])


@router.post("/train", response_model=ModelMetadataResponse)
async def train_model(
    request: Request,
    training_request: TrainingRequest,
    db: Session = Depends(get_db)
):
    """Train a new model."""
    tenant_id = get_tenant_id(request)
    
    # Validate tenant_id matches
    if training_request.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    # Load training data (in production, this would come from S3)
    # For now, create dummy data
    training_data = pd.DataFrame({
        'feature_1': [1, 2, 3, 4, 5],
        'feature_2': [2, 4, 6, 8, 10]
    })
    
    service = MLTrainingService(db, tenant_id)
    model = service.train_log_anomaly_model(
        training_data=training_data,
        model_name=training_request.model_name,
        hyperparameters=training_request.hyperparameters
    )
    
    return ModelMetadataResponse.model_validate(model)


@router.get("/", response_model=List[ModelMetadataResponse])
async def list_models(
    request: Request,
    db: Session = Depends(get_db)
):
    """List all models for tenant."""
    tenant_id = get_tenant_id(request)
    
    models = db.query(ModelMetadata).filter(
        ModelMetadata.tenant_id == tenant_id
    ).all()
    
    return [ModelMetadataResponse.model_validate(m) for m in models]


@router.get("/{model_id}", response_model=ModelMetadataResponse)
async def get_model(
    request: Request,
    model_id: str,
    db: Session = Depends(get_db)
):
    """Get model by ID."""
    tenant_id = get_tenant_id(request)
    
    model = db.query(ModelMetadata).filter(
        ModelMetadata.id == model_id,
        ModelMetadata.tenant_id == tenant_id
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return ModelMetadataResponse.model_validate(model)


@router.post("/{model_id}/deploy", response_model=ModelMetadataResponse)
async def deploy_model(
    request: Request,
    model_id: str,
    db: Session = Depends(get_db)
):
    """Deploy a model to Kubernetes."""
    tenant_id = get_tenant_id(request)
    
    service = ModelDeploymentService(db, tenant_id)
    model = service.deploy_model(model_id)
    
    return ModelMetadataResponse.model_validate(model)
