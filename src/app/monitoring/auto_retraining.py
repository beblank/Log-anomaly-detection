"""Auto-retraining pipeline orchestrator."""
import asyncio
from typing import Dict, Any
import pandas as pd
from sqlalchemy.orm import Session

from .drift_detection import DriftDetectionService
from .alert_service import AlertService
from ..ml_pipeline.training_service import MLTrainingService
from ..ml_pipeline.evaluation_service import ModelEvaluationService
from ..ml_pipeline.deployment_service import ModelDeploymentService
from ..models.database import DriftAlert, ModelMetadata


class AutoRetrainingPipeline:
    """Orchestrates the auto-retraining pipeline: Drift → Alert → Train → Evaluate → Deploy."""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.drift_service = DriftDetectionService(db, tenant_id)
        self.alert_service = AlertService(db, tenant_id)
        self.training_service = MLTrainingService(db, tenant_id)
        self.evaluation_service = ModelEvaluationService(db, tenant_id)
        self.deployment_service = ModelDeploymentService(db, tenant_id)
    
    async def check_and_retrain(
        self,
        model_id: str,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        new_training_data: pd.DataFrame,
        test_data: pd.DataFrame,
        test_labels: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Check for drift and trigger retraining pipeline if needed.
        
        Flow: Data Drift → Alert → Trigger Pipeline → Train → Evaluate → Register → Deploy
        """
        result = {
            'drift_detected': False,
            'alert_sent': False,
            'retraining_triggered': False,
            'new_model_deployed': False,
            'drift_alert_id': None,
            'new_model_id': None
        }
        
        # Step 1: Detect drift
        drift_alert = self.drift_service.detect_drift(
            reference_data=reference_data,
            current_data=current_data,
            model_id=model_id
        )
        result['drift_detected'] = drift_alert.drift_detected
        result['drift_alert_id'] = drift_alert.id
        
        # Step 2: Send alert if drift detected
        if drift_alert.drift_detected:
            await self.alert_service.send_drift_alert(drift_alert)
            drift_alert.alert_sent = True
            self.db.commit()
            result['alert_sent'] = True
        
        # Step 3: Check if retraining should be triggered
        if self.drift_service.should_trigger_retraining(drift_alert):
            result['retraining_triggered'] = True
            drift_alert.retraining_triggered = True
            self.db.commit()
            
            # Get original model info
            original_model = self.db.query(ModelMetadata).filter(
                ModelMetadata.id == model_id
            ).first()
            
            if not original_model:
                return result
            
            # Step 4: Train new model
            new_model = self.training_service.train_log_anomaly_model(
                training_data=new_training_data,
                model_name=original_model.model_name,
                hyperparameters=None  # Use defaults or retrieve from original
            )
            result['new_model_id'] = new_model.id
            
            # Step 5: Evaluate new model
            model_obj = self.training_service.load_model_from_s3(new_model.s3_model_path)
            metrics = self.evaluation_service.evaluate_model(
                model=model_obj,
                test_data=test_data,
                true_labels=test_labels,
                model_id=new_model.id
            )
            
            # Step 6: Compare with old model and decide to deploy
            if self._should_deploy_new_model(original_model, new_model):
                # Step 7: Deploy new model
                deployed_model = self.deployment_service.deploy_model(new_model.id)
                result['new_model_deployed'] = True
                
                # Send success alert
                await self.alert_service.send_retraining_success_alert(
                    drift_alert=drift_alert,
                    new_model=deployed_model,
                    metrics=metrics
                )
        
        return result
    
    def _should_deploy_new_model(
        self,
        old_model: ModelMetadata,
        new_model: ModelMetadata
    ) -> bool:
        """Decide if new model should be deployed based on performance."""
        # Simple strategy: deploy if new model has better F1 score
        if not old_model.f1_score or not new_model.f1_score:
            return True  # Deploy if we don't have metrics
        
        old_f1 = float(old_model.f1_score)
        new_f1 = float(new_model.f1_score)
        
        # Deploy if new model is at least as good or within 5% of old model
        return new_f1 >= (old_f1 * 0.95)
