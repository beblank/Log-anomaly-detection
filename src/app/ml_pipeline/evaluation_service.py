"""Model evaluation service."""
from typing import Dict, Any
import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from sqlalchemy.orm import Session

from ..models.database import ModelMetadata


class ModelEvaluationService:
    """Service for evaluating ML models."""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    def evaluate_model(
        self,
        model: Any,
        test_data: pd.DataFrame,
        true_labels: np.ndarray,
        model_id: str
    ) -> Dict[str, float]:
        """Evaluate model on test data."""
        # Get predictions
        predictions = model.predict(test_data)
        
        # Convert predictions to binary (1 for normal, 0 for anomaly)
        binary_predictions = (predictions == 1).astype(int)
        
        # Calculate metrics
        accuracy = accuracy_score(true_labels, binary_predictions)
        precision = precision_score(true_labels, binary_predictions, zero_division=0)
        recall = recall_score(true_labels, binary_predictions, zero_division=0)
        f1 = f1_score(true_labels, binary_predictions, zero_division=0)
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        }
        
        # Update model metadata with metrics
        model_metadata = self.db.query(ModelMetadata).filter(
            ModelMetadata.id == model_id,
            ModelMetadata.tenant_id == self.tenant_id
        ).first()
        
        if model_metadata:
            model_metadata.accuracy = f"{accuracy:.4f}"
            model_metadata.precision = f"{precision:.4f}"
            model_metadata.recall = f"{recall:.4f}"
            model_metadata.f1_score = f"{f1:.4f}"
            self.db.commit()
        
        return metrics
    
    def compare_models(
        self,
        model_ids: list[str]
    ) -> Dict[str, Dict[str, float]]:
        """Compare multiple models."""
        results = {}
        
        for model_id in model_ids:
            model_metadata = self.db.query(ModelMetadata).filter(
                ModelMetadata.id == model_id,
                ModelMetadata.tenant_id == self.tenant_id
            ).first()
            
            if model_metadata:
                results[model_id] = {
                    'accuracy': float(model_metadata.accuracy) if model_metadata.accuracy else 0.0,
                    'precision': float(model_metadata.precision) if model_metadata.precision else 0.0,
                    'recall': float(model_metadata.recall) if model_metadata.recall else 0.0,
                    'f1_score': float(model_metadata.f1_score) if model_metadata.f1_score else 0.0,
                }
        
        return results
