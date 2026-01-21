"""ML training service with tenant isolation."""
import os
from typing import Dict, Any, Optional
import mlflow
import boto3
from sklearn.ensemble import IsolationForest
import numpy as np
import pandas as pd
import pickle
from datetime import datetime

from ..core.config import get_settings
from ..models.database import ModelMetadata
from sqlalchemy.orm import Session


class MLTrainingService:
    """Service for training ML models with tenant isolation."""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.settings = get_settings()
        self._init_mlflow()
        
    def _init_mlflow(self):
        """Initialize MLflow tracking."""
        mlflow.set_tracking_uri(self.settings.MLFLOW_TRACKING_URI)
        # Set experiment per tenant
        mlflow.set_experiment(f"tenant-{self.tenant_id}")
    
    def train_log_anomaly_model(
        self,
        training_data: pd.DataFrame,
        model_name: str,
        hyperparameters: Optional[Dict[str, Any]] = None
    ) -> ModelMetadata:
        """Train log anomaly detection model."""
        if hyperparameters is None:
            hyperparameters = {
                'contamination': 0.1,
                'n_estimators': 100,
                'max_samples': 'auto'
            }
        
        # Start MLflow run
        with mlflow.start_run() as run:
            # Log parameters
            mlflow.log_params(hyperparameters)
            mlflow.set_tag("tenant_id", self.tenant_id)
            mlflow.set_tag("model_type", "log_anomaly_detector")
            
            # Train model
            model = IsolationForest(**hyperparameters)
            model.fit(training_data)
            
            # Evaluate on training data
            train_predictions = model.predict(training_data)
            anomaly_count = np.sum(train_predictions == -1)
            anomaly_rate = anomaly_count / len(training_data)
            
            # Log metrics
            mlflow.log_metric("anomaly_rate", anomaly_rate)
            mlflow.log_metric("training_samples", len(training_data))
            
            # Save model to MLflow
            mlflow.sklearn.log_model(model, "model")
            
            # Save model to S3 with tenant isolation
            s3_path = self._save_to_s3(model, model_name, run.info.run_id)
            
            # Create model metadata record
            model_version = datetime.now().strftime("%Y%m%d-%H%M%S")
            model_metadata = ModelMetadata(
                tenant_id=self.tenant_id,
                model_name=model_name,
                model_version=model_version,
                model_type="log_anomaly_detector",
                mlflow_run_id=run.info.run_id,
                mlflow_model_uri=f"runs:/{run.info.run_id}/model",
                s3_model_path=s3_path,
                is_deployed=False,
                deployment_status="trained"
            )
            
            self.db.add(model_metadata)
            self.db.commit()
            self.db.refresh(model_metadata)
            
            return model_metadata
    
    def _save_to_s3(self, model: Any, model_name: str, run_id: str) -> str:
        """Save model to S3 with tenant isolation."""
        try:
            s3_client = boto3.client(
                's3',
                region_name=self.settings.AWS_REGION,
                aws_access_key_id=self.settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=self.settings.AWS_SECRET_ACCESS_KEY
            )
            
            # Get tenant-specific S3 prefix
            from .tenant_service import TenantService
            tenant_service = TenantService(self.db)
            tenant = tenant_service.get_tenant(self.tenant_id)
            
            if not tenant:
                raise ValueError(f"Tenant {self.tenant_id} not found")
            
            # Create S3 key with tenant isolation
            s3_key = f"{tenant.s3_prefix}/models/{model_name}/{run_id}/model.pkl"
            
            # Serialize model
            model_bytes = pickle.dumps(model)
            
            # Upload to S3
            s3_client.put_object(
                Bucket=self.settings.AWS_S3_BUCKET,
                Key=s3_key,
                Body=model_bytes
            )
            
            return f"s3://{self.settings.AWS_S3_BUCKET}/{s3_key}"
        except Exception as e:
            print(f"Warning: Failed to save model to S3: {str(e)}")
            return ""
    
    def load_model_from_s3(self, s3_path: str) -> Any:
        """Load model from S3."""
        try:
            # Parse S3 path
            parts = s3_path.replace("s3://", "").split("/", 1)
            bucket = parts[0]
            key = parts[1]
            
            s3_client = boto3.client(
                's3',
                region_name=self.settings.AWS_REGION,
                aws_access_key_id=self.settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=self.settings.AWS_SECRET_ACCESS_KEY
            )
            
            # Download model
            response = s3_client.get_object(Bucket=bucket, Key=key)
            model_bytes = response['Body'].read()
            
            # Deserialize model
            model = pickle.loads(model_bytes)
            return model
        except Exception as e:
            raise ValueError(f"Failed to load model from S3: {str(e)}")
