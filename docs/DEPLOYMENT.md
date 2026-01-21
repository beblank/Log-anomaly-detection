# Deployment Guide

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [AWS Infrastructure Setup](#aws-infrastructure-setup)
5. [Production Considerations](#production-considerations)

## Local Development Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 15+
- Docker (optional)

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/beblank/Log-anomaly-detection.git
cd Log-anomaly-detection
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

4. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Start PostgreSQL**
```bash
# Using Docker
docker run --name ml-saas-postgres \
  -e POSTGRES_DB=mlsaas \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15
```

6. **Initialize database**
```bash
# The application will auto-create tables on startup
python -m src.app.main
```

7. **Access the application**
- API: http://localhost:8080
- API Docs: http://localhost:8080/docs

## Docker Deployment

### Using Docker Compose

1. **Navigate to docker directory**
```bash
cd docker
```

2. **Start all services**
```bash
docker-compose up -d
```

This starts:
- API application (port 8080)
- PostgreSQL database (port 5432)
- MLflow server (port 5000)
- Prometheus (port 9090)
- Grafana (port 3000)

3. **View logs**
```bash
docker-compose logs -f api
```

4. **Stop services**
```bash
docker-compose down
```

### Building Custom Docker Image

```bash
docker build -f docker/Dockerfile -t ml-saas:latest .
docker run -p 8080:8080 -p 8000:8000 ml-saas:latest
```

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (EKS, GKE, AKS, or local)
- kubectl configured
- AWS credentials (for S3 access)

### Steps

1. **Create namespace**
```bash
kubectl create namespace ml-saas
```

2. **Create secrets**
```bash
kubectl create secret generic ml-saas-secrets \
  --from-literal=database-url='postgresql://user:password@postgres:5432/mlsaas' \
  --from-literal=aws-access-key-id='YOUR_ACCESS_KEY' \
  --from-literal=aws-secret-access-key='YOUR_SECRET_KEY' \
  -n ml-saas
```

3. **Deploy application**
```bash
kubectl apply -f k8s/deployment.yaml
```

4. **Deploy Prometheus**
```bash
kubectl apply -f k8s/prometheus.yaml
```

5. **Verify deployment**
```bash
kubectl get pods -n ml-saas
kubectl get services -n ml-saas
```

6. **Access the application**
```bash
# Get external IP
kubectl get service ml-saas-api-service -n ml-saas

# Port forward for local access
kubectl port-forward -n ml-saas service/ml-saas-api-service 8080:80
```

### Creating Tenant Namespaces

For each tenant, create an isolated namespace:

```bash
# Edit the template with tenant name
sed 's/ml-tenant-example/ml-tenant-acme-corp/g' k8s/tenant-namespace-template.yaml | kubectl apply -f -
```

## AWS Infrastructure Setup

### Using Terraform

1. **Navigate to terraform directory**
```bash
cd terraform
```

2. **Initialize Terraform**
```bash
terraform init
```

3. **Review the plan**
```bash
terraform plan
```

4. **Apply infrastructure**
```bash
terraform apply
```

This creates:
- S3 bucket for model storage
- IAM roles and policies
- (Optional) EKS cluster configuration

5. **Get outputs**
```bash
terraform output
```

### Manual AWS Setup

If not using Terraform:

1. **Create S3 bucket**
```bash
aws s3 mb s3://ml-saas-models --region us-east-1
```

2. **Enable versioning**
```bash
aws s3api put-bucket-versioning \
  --bucket ml-saas-models \
  --versioning-configuration Status=Enabled
```

3. **Enable encryption**
```bash
aws s3api put-bucket-encryption \
  --bucket ml-saas-models \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

## Production Considerations

### Security

1. **Enable HTTPS**
```yaml
# Use cert-manager or AWS ALB with TLS
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
```

2. **Use Kubernetes Secrets**
- Store all sensitive data in K8s secrets
- Use external secret managers (AWS Secrets Manager, HashiCorp Vault)

3. **Network Policies**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: tenant-isolation
spec:
  podSelector:
    matchLabels:
      tenant: acme-corp
  policyTypes:
  - Ingress
  - Egress
```

### High Availability

1. **Database**
- Use managed PostgreSQL (RDS, Cloud SQL)
- Enable Multi-AZ deployment
- Configure automated backups

2. **Application**
- Run multiple replicas (min 3)
- Use pod disruption budgets
- Configure health checks

3. **Storage**
- Use S3 with cross-region replication
- Enable lifecycle policies

### Monitoring

1. **Enable logging**
```bash
# CloudWatch logs for EKS
kubectl apply -f https://amazon-eks.s3.us-west-2.amazonaws.com/cloudwatch-insights/latest/fluentd.yaml
```

2. **Configure alerts**
- Set up Alertmanager
- Configure Slack/PagerDuty webhooks
- Define SLOs and SLIs

### Backup and Recovery

1. **Database backups**
```bash
# Automated daily backups
pg_dump mlsaas > backup_$(date +%Y%m%d).sql
```

2. **S3 versioning**
- Already enabled via Terraform
- Configure lifecycle rules for old versions

3. **Disaster recovery plan**
- Document recovery procedures
- Test recovery regularly
- Maintain runbooks

### Scaling

1. **Horizontal Pod Autoscaler**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-saas-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-saas-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

2. **Database connection pooling**
- Configure in application settings
- Use PgBouncer for connection pooling

### Cost Optimization

1. **Resource requests and limits**
- Set appropriate values based on monitoring
- Use vertical pod autoscaler

2. **S3 lifecycle policies**
- Archive old models to Glacier
- Delete unused data

3. **Reserved instances**
- Use for long-running workloads
- Consider Savings Plans

## Troubleshooting

### Common Issues

**Application won't start**
- Check database connection
- Verify environment variables
- Review logs: `kubectl logs -n ml-saas <pod-name>`

**S3 access denied**
- Verify IAM role permissions
- Check bucket policy
- Validate credentials

**High latency**
- Check database query performance
- Review Prometheus metrics
- Scale up resources

**Out of memory**
- Increase pod memory limits
- Check for memory leaks
- Optimize ML model loading
