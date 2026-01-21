"""Prometheus metrics exporter."""
from prometheus_client import Counter, Gauge, Histogram, start_http_server
from prometheus_client.core import CollectorRegistry
from typing import Dict
import time

# Create registry
registry = CollectorRegistry()

# Define metrics
# Training Metrics
training_runs_total = Counter(
    'ml_training_runs_total',
    'Total number of training runs',
    ['tenant_id', 'model_type'],
    registry=registry
)

training_duration_seconds = Histogram(
    'ml_training_duration_seconds',
    'Duration of training runs in seconds',
    ['tenant_id', 'model_type'],
    registry=registry
)

# Drift Metrics
drift_alerts_total = Counter(
    'ml_drift_alerts_total',
    'Total number of drift alerts',
    ['tenant_id', 'model_id'],
    registry=registry
)

drift_score = Gauge(
    'ml_drift_score',
    'Current drift score',
    ['tenant_id', 'model_id'],
    registry=registry
)

# Retraining Metrics
retraining_triggered_total = Counter(
    'ml_retraining_triggered_total',
    'Total number of automatic retrainings triggered',
    ['tenant_id', 'model_id'],
    registry=registry
)

# Model Metrics
models_deployed_total = Counter(
    'ml_models_deployed_total',
    'Total number of models deployed',
    ['tenant_id', 'model_type'],
    registry=registry
)

active_models = Gauge(
    'ml_active_models',
    'Number of currently active models',
    ['tenant_id'],
    registry=registry
)

# Model Performance Metrics
model_accuracy = Gauge(
    'ml_model_accuracy',
    'Model accuracy score',
    ['tenant_id', 'model_id', 'model_name'],
    registry=registry
)

model_f1_score = Gauge(
    'ml_model_f1_score',
    'Model F1 score',
    ['tenant_id', 'model_id', 'model_name'],
    registry=registry
)

# Inference Metrics
prediction_requests_total = Counter(
    'ml_prediction_requests_total',
    'Total number of prediction requests',
    ['tenant_id', 'model_id'],
    registry=registry
)

prediction_latency_seconds = Histogram(
    'ml_prediction_latency_seconds',
    'Prediction latency in seconds',
    ['tenant_id', 'model_id'],
    registry=registry
)

# Tenant Metrics
active_tenants = Gauge(
    'ml_active_tenants',
    'Number of active tenants',
    registry=registry
)


class MetricsExporter:
    """Prometheus metrics exporter for ML SaaS."""
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.registry = registry
    
    def start(self):
        """Start Prometheus metrics server."""
        start_http_server(self.port, registry=self.registry)
        print(f"Prometheus metrics server started on port {self.port}")
    
    # Helper methods to record metrics
    
    def record_training_run(self, tenant_id: str, model_type: str, duration: float):
        """Record a training run."""
        training_runs_total.labels(tenant_id=tenant_id, model_type=model_type).inc()
        training_duration_seconds.labels(tenant_id=tenant_id, model_type=model_type).observe(duration)
    
    def record_drift_alert(self, tenant_id: str, model_id: str, drift_score_value: float):
        """Record a drift alert."""
        drift_alerts_total.labels(tenant_id=tenant_id, model_id=model_id).inc()
        drift_score.labels(tenant_id=tenant_id, model_id=model_id).set(drift_score_value)
    
    def record_retraining(self, tenant_id: str, model_id: str):
        """Record an automatic retraining."""
        retraining_triggered_total.labels(tenant_id=tenant_id, model_id=model_id).inc()
    
    def record_model_deployment(self, tenant_id: str, model_type: str):
        """Record a model deployment."""
        models_deployed_total.labels(tenant_id=tenant_id, model_type=model_type).inc()
    
    def update_active_models(self, tenant_id: str, count: int):
        """Update active models count."""
        active_models.labels(tenant_id=tenant_id).set(count)
    
    def update_model_metrics(self, tenant_id: str, model_id: str, model_name: str, 
                            accuracy: float, f1: float):
        """Update model performance metrics."""
        model_accuracy.labels(tenant_id=tenant_id, model_id=model_id, 
                            model_name=model_name).set(accuracy)
        model_f1_score.labels(tenant_id=tenant_id, model_id=model_id, 
                            model_name=model_name).set(f1)
    
    def record_prediction(self, tenant_id: str, model_id: str, latency: float):
        """Record a prediction request."""
        prediction_requests_total.labels(tenant_id=tenant_id, model_id=model_id).inc()
        prediction_latency_seconds.labels(tenant_id=tenant_id, model_id=model_id).observe(latency)
    
    def update_active_tenants(self, count: int):
        """Update active tenants count."""
        active_tenants.set(count)


# Global instance
metrics_exporter = MetricsExporter()
