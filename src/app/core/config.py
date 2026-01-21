"""Core configuration and utilities."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Multi-Tenant ML SaaS"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/mlsaas"
    
    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = "ml-saas-models"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    # MLflow
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    MLFLOW_S3_ENDPOINT_URL: Optional[str] = None
    
    # Monitoring
    PROMETHEUS_PORT: int = 8000
    EVIDENTLY_PORT: int = 8001
    
    # Slack
    SLACK_WEBHOOK_URL: Optional[str] = None
    SLACK_BOT_TOKEN: Optional[str] = None
    
    # Drift Detection
    DRIFT_CHECK_INTERVAL_HOURS: int = 24
    DRIFT_THRESHOLD: float = 0.1
    
    # Kubernetes
    K8S_NAMESPACE_PREFIX: str = "ml-tenant"
    K8S_IN_CLUSTER: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
