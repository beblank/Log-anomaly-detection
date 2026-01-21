"""Model deployment service."""
from typing import Optional
from sqlalchemy.orm import Session
from kubernetes import client
from fastapi import HTTPException

from ..models.database import ModelMetadata
from ..core.config import get_settings


class ModelDeploymentService:
    """Service for deploying ML models to Kubernetes."""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.settings = get_settings()
        self.k8s_apps_v1 = client.AppsV1Api()
        self.k8s_v1 = client.CoreV1Api()
    
    def deploy_model(self, model_id: str) -> ModelMetadata:
        """Deploy model to Kubernetes in tenant namespace."""
        # Get model metadata
        model_metadata = self.db.query(ModelMetadata).filter(
            ModelMetadata.id == model_id,
            ModelMetadata.tenant_id == self.tenant_id
        ).first()
        
        if not model_metadata:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Get tenant info
        from .tenant_service import TenantService
        tenant_service = TenantService(self.db)
        tenant = tenant_service.get_tenant(self.tenant_id)
        
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        try:
            # Create deployment in tenant namespace
            self._create_k8s_deployment(
                namespace=tenant.k8s_namespace,
                model_name=model_metadata.model_name,
                model_path=model_metadata.s3_model_path
            )
            
            # Create service
            self._create_k8s_service(
                namespace=tenant.k8s_namespace,
                model_name=model_metadata.model_name
            )
            
            # Update model metadata
            model_metadata.is_deployed = True
            model_metadata.deployment_status = "deployed"
            self.db.commit()
            self.db.refresh(model_metadata)
            
            return model_metadata
        except Exception as e:
            model_metadata.deployment_status = "failed"
            self.db.commit()
            raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")
    
    def _create_k8s_deployment(self, namespace: str, model_name: str, model_path: str):
        """Create Kubernetes deployment."""
        deployment_name = f"{model_name}-deployment"
        
        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(
                name=deployment_name,
                namespace=namespace,
                labels={"app": model_name, "tenant": self.tenant_id}
            ),
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(
                    match_labels={"app": model_name}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={"app": model_name, "tenant": self.tenant_id}
                    ),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name="model-server",
                                image="ml-saas/model-server:latest",
                                env=[
                                    client.V1EnvVar(name="MODEL_PATH", value=model_path),
                                    client.V1EnvVar(name="TENANT_ID", value=self.tenant_id)
                                ],
                                ports=[client.V1ContainerPort(container_port=8080)],
                                resources=client.V1ResourceRequirements(
                                    requests={"cpu": "500m", "memory": "512Mi"},
                                    limits={"cpu": "1000m", "memory": "1Gi"}
                                )
                            )
                        ]
                    )
                )
            )
        )
        
        try:
            self.k8s_apps_v1.create_namespaced_deployment(
                namespace=namespace,
                body=deployment
            )
        except client.exceptions.ApiException as e:
            if e.status == 409:  # Already exists
                self.k8s_apps_v1.patch_namespaced_deployment(
                    name=deployment_name,
                    namespace=namespace,
                    body=deployment
                )
            else:
                raise
    
    def _create_k8s_service(self, namespace: str, model_name: str):
        """Create Kubernetes service."""
        service_name = f"{model_name}-service"
        
        service = client.V1Service(
            metadata=client.V1ObjectMeta(
                name=service_name,
                namespace=namespace,
                labels={"app": model_name}
            ),
            spec=client.V1ServiceSpec(
                selector={"app": model_name},
                ports=[client.V1ServicePort(
                    port=80,
                    target_port=8080
                )],
                type="ClusterIP"
            )
        )
        
        try:
            self.k8s_v1.create_namespaced_service(
                namespace=namespace,
                body=service
            )
        except client.exceptions.ApiException as e:
            if e.status != 409:  # Ignore if already exists
                raise
