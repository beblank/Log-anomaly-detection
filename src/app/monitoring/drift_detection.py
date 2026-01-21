"""Data drift detection service using Evidently AI."""
import json
from typing import Dict, Any, Optional
import pandas as pd
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report
from sqlalchemy.orm import Session

from ..models.database import DriftAlert, ModelMetadata
from ..core.config import get_settings


class DriftDetectionService:
    """Service for detecting data drift using Evidently AI."""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.settings = get_settings()
    
    def detect_drift(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        model_id: str
    ) -> DriftAlert:
        """Detect data drift between reference and current data."""
        # Create Evidently report
        report = Report(metrics=[
            DataDriftPreset()
        ])
        
        # Run report
        report.run(
            reference_data=reference_data,
            current_data=current_data
        )
        
        # Get report results
        report_dict = report.as_dict()
        
        # Extract drift metrics
        drift_metrics = report_dict.get('metrics', [])
        drift_detected = False
        drift_score = 0.0
        features_drifted = []
        
        for metric in drift_metrics:
            if metric.get('metric') == 'DatasetDriftMetric':
                result = metric.get('result', {})
                drift_detected = result.get('dataset_drift', False)
                drift_score = result.get('drift_share', 0.0)
                
                # Get drifted features
                drift_by_columns = result.get('drift_by_columns', {})
                for col, details in drift_by_columns.items():
                    if details.get('drift_detected', False):
                        features_drifted.append(col)
        
        # Create drift alert
        drift_alert = DriftAlert(
            tenant_id=self.tenant_id,
            model_id=model_id,
            drift_score=f"{drift_score:.4f}",
            drift_detected=drift_detected,
            features_drifted=json.dumps(features_drifted) if features_drifted else None,
            alert_sent=False,
            retraining_triggered=False
        )
        
        self.db.add(drift_alert)
        self.db.commit()
        self.db.refresh(drift_alert)
        
        return drift_alert
    
    def should_trigger_retraining(self, drift_alert: DriftAlert) -> bool:
        """Determine if retraining should be triggered based on drift."""
        if not drift_alert.drift_detected:
            return False
        
        drift_score = float(drift_alert.drift_score)
        threshold = self.settings.DRIFT_THRESHOLD
        
        return drift_score >= threshold
    
    def get_drift_alerts(self, model_id: Optional[str] = None) -> list[DriftAlert]:
        """Get drift alerts for tenant."""
        query = self.db.query(DriftAlert).filter(
            DriftAlert.tenant_id == self.tenant_id
        )
        
        if model_id:
            query = query.filter(DriftAlert.model_id == model_id)
        
        return query.order_by(DriftAlert.created_at.desc()).all()
