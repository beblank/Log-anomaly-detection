"""Monitoring and drift detection API endpoints."""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import pandas as pd

from ...core.database import get_db
from ...core.tenant_context import get_tenant_id
from ...models.schemas import DriftAlertResponse
from ...monitoring.drift_detection import DriftDetectionService
from ...monitoring.auto_retraining import AutoRetrainingPipeline

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/drift-alerts", response_model=List[DriftAlertResponse])
async def get_drift_alerts(
    request: Request,
    model_id: str = None,
    db: Session = Depends(get_db)
):
    """Get drift alerts for tenant."""
    tenant_id = get_tenant_id(request)
    
    service = DriftDetectionService(db, tenant_id)
    alerts = service.get_drift_alerts(model_id)
    
    return [DriftAlertResponse.model_validate(a) for a in alerts]


@router.post("/check-drift/{model_id}", response_model=DriftAlertResponse)
async def check_drift(
    request: Request,
    model_id: str,
    db: Session = Depends(get_db)
):
    """Check for data drift on a model."""
    tenant_id = get_tenant_id(request)
    
    # In production, load real data from S3
    # For now, create dummy data
    reference_data = pd.DataFrame({
        'feature_1': [1, 2, 3, 4, 5],
        'feature_2': [2, 4, 6, 8, 10]
    })
    
    current_data = pd.DataFrame({
        'feature_1': [10, 20, 30, 40, 50],  # Significantly different
        'feature_2': [20, 40, 60, 80, 100]
    })
    
    service = DriftDetectionService(db, tenant_id)
    drift_alert = service.detect_drift(
        reference_data=reference_data,
        current_data=current_data,
        model_id=model_id
    )
    
    return DriftAlertResponse.model_validate(drift_alert)


@router.post("/auto-retrain/{model_id}", response_model=Dict[str, Any])
async def trigger_auto_retraining(
    request: Request,
    model_id: str,
    db: Session = Depends(get_db)
):
    """Trigger auto-retraining pipeline for a model."""
    tenant_id = get_tenant_id(request)
    
    # In production, load real data from S3
    # For now, create dummy data
    reference_data = pd.DataFrame({
        'feature_1': [1, 2, 3, 4, 5],
        'feature_2': [2, 4, 6, 8, 10]
    })
    
    current_data = pd.DataFrame({
        'feature_1': [10, 20, 30, 40, 50],
        'feature_2': [20, 40, 60, 80, 100]
    })
    
    new_training_data = pd.DataFrame({
        'feature_1': [1, 2, 3, 4, 5, 10, 20, 30],
        'feature_2': [2, 4, 6, 8, 10, 20, 40, 60]
    })
    
    test_data = pd.DataFrame({
        'feature_1': [6, 7, 8],
        'feature_2': [12, 14, 16]
    })
    
    test_labels = pd.Series([1, 1, 1])  # 1 = normal, 0 = anomaly
    
    pipeline = AutoRetrainingPipeline(db, tenant_id)
    result = await pipeline.check_and_retrain(
        model_id=model_id,
        reference_data=reference_data,
        current_data=current_data,
        new_training_data=new_training_data,
        test_data=test_data,
        test_labels=test_labels
    )
    
    return result
