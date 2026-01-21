"""Test database models."""
from src.app.models.database import Tenant, ModelMetadata, DriftAlert


def test_tenant_model_creation():
    """Test tenant model creation."""
    tenant = Tenant(
        name="test-tenant",
        display_name="Test Tenant",
        description="Test description",
        s3_prefix="tenant-test-tenant",
        k8s_namespace="ml-tenant-test-tenant",
        is_active=True
    )
    
    assert tenant.name == "test-tenant"
    assert tenant.display_name == "Test Tenant"
    assert tenant.is_active is True


def test_model_metadata_creation():
    """Test model metadata creation."""
    model = ModelMetadata(
        tenant_id="test-tenant-id",
        model_name="test-model",
        model_version="v1",
        model_type="log_anomaly_detector",
        is_deployed=False,
        deployment_status="pending"
    )
    
    assert model.tenant_id == "test-tenant-id"
    assert model.model_name == "test-model"
    assert model.is_deployed is False


def test_drift_alert_creation():
    """Test drift alert creation."""
    alert = DriftAlert(
        tenant_id="test-tenant-id",
        model_id="test-model-id",
        drift_score="0.25",
        drift_detected=True,
        alert_sent=False,
        retraining_triggered=False
    )
    
    assert alert.tenant_id == "test-tenant-id"
    assert alert.drift_detected is True
    assert float(alert.drift_score) == 0.25
