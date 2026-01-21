"""Tenant management service."""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import boto3
from kubernetes import client, config as k8s_config
from fastapi import HTTPException

from ..models.database import Tenant
from ..models.schemas import TenantCreate, TenantResponse
from ..core.config import get_settings


class TenantService:
    """Service for managing tenants."""
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self._init_k8s()
        
    def _init_k8s(self):
        """Initialize Kubernetes client."""
        try:
            if self.settings.K8S_IN_CLUSTER:
                k8s_config.load_incluster_config()
            else:
                k8s_config.load_kube_config()
            self.k8s_v1 = client.CoreV1Api()
        except Exception:
            self.k8s_v1 = None
    
    def create_tenant(self, tenant_data: TenantCreate) -> TenantResponse:
        """Create a new tenant with isolated resources."""
        # Generate resource names
        tenant_name = tenant_data.name
        s3_prefix = f"tenant-{tenant_name}"
        k8s_namespace = f"{self.settings.K8S_NAMESPACE_PREFIX}-{tenant_name}"
        
        # Create tenant record
        tenant = Tenant(
            name=tenant_name,
            display_name=tenant_data.display_name,
            description=tenant_data.description,
            s3_prefix=s3_prefix,
            k8s_namespace=k8s_namespace,
            is_active=True
        )
        
        try:
            # Create K8s namespace
            if self.k8s_v1:
                self._create_k8s_namespace(k8s_namespace)
            
            # Create S3 prefix (bucket should exist)
            self._setup_s3_prefix(s3_prefix)
            
            # Create IAM role (optional)
            iam_role_arn = self._create_iam_role(tenant_name)
            if iam_role_arn:
                tenant.iam_role_arn = iam_role_arn
            
            # Save to database
            self.db.add(tenant)
            self.db.commit()
            self.db.refresh(tenant)
            
            return TenantResponse.model_validate(tenant)
            
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Tenant already exists")
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create tenant: {str(e)}")
    
    def _create_k8s_namespace(self, namespace: str):
        """Create Kubernetes namespace for tenant."""
        if not self.k8s_v1:
            return
        
        try:
            namespace_manifest = client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=namespace,
                    labels={
                        "app.kubernetes.io/managed-by": "ml-saas",
                        "tenant": namespace
                    }
                )
            )
            self.k8s_v1.create_namespace(namespace_manifest)
        except client.exceptions.ApiException as e:
            if e.status != 409:  # Ignore if already exists
                raise
    
    def _setup_s3_prefix(self, s3_prefix: str):
        """Setup S3 prefix for tenant (create folder structure)."""
        try:
            s3_client = boto3.client(
                's3',
                region_name=self.settings.AWS_REGION,
                aws_access_key_id=self.settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=self.settings.AWS_SECRET_ACCESS_KEY
            )
            
            # Create folder structure in S3
            folders = ['models/', 'data/', 'logs/']
            for folder in folders:
                key = f"{s3_prefix}/{folder}"
                s3_client.put_object(
                    Bucket=self.settings.AWS_S3_BUCKET,
                    Key=key,
                    Body=b''
                )
        except Exception as e:
            # Log error but don't fail tenant creation
            print(f"Warning: Failed to setup S3 prefix: {str(e)}")
    
    def _create_iam_role(self, tenant_name: str) -> Optional[str]:
        """Create IAM role for tenant (optional)."""
        try:
            iam_client = boto3.client(
                'iam',
                region_name=self.settings.AWS_REGION,
                aws_access_key_id=self.settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=self.settings.AWS_SECRET_ACCESS_KEY
            )
            
            role_name = f"ml-saas-{tenant_name}"
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "eks.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            response = iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=str(trust_policy),
                Description=f"IAM role for tenant {tenant_name}"
            )
            
            return response['Role']['Arn']
        except Exception as e:
            # Log error but don't fail tenant creation
            print(f"Warning: Failed to create IAM role: {str(e)}")
            return None
    
    def get_tenant(self, tenant_id: str) -> Optional[TenantResponse]:
        """Get tenant by ID."""
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if tenant:
            return TenantResponse.model_validate(tenant)
        return None
    
    def get_tenant_by_name(self, tenant_name: str) -> Optional[TenantResponse]:
        """Get tenant by name."""
        tenant = self.db.query(Tenant).filter(Tenant.name == tenant_name).first()
        if tenant:
            return TenantResponse.model_validate(tenant)
        return None
    
    def list_tenants(self) -> List[TenantResponse]:
        """List all tenants."""
        tenants = self.db.query(Tenant).all()
        return [TenantResponse.model_validate(t) for t in tenants]
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """Delete tenant and cleanup resources."""
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return False
        
        try:
            # Cleanup K8s namespace
            if self.k8s_v1:
                try:
                    self.k8s_v1.delete_namespace(tenant.k8s_namespace)
                except Exception as e:
                    print(f"Warning: Failed to delete K8s namespace: {str(e)}")
            
            # Note: S3 and IAM cleanup should be done carefully in production
            
            # Delete from database
            self.db.delete(tenant)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to delete tenant: {str(e)}")
