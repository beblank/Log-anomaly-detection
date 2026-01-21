# Architecture Documentation

## System Architecture

The Multi-Tenant ML SaaS platform is designed with a microservices architecture that provides:
- Tenant isolation at multiple levels
- Scalable ML pipeline
- Real-time monitoring and alerting
- Auto-retraining capabilities

## Components

### 1. API Layer (FastAPI)
- **Purpose**: Handles all HTTP requests and enforces tenant isolation
- **Key Features**:
  - RESTful API endpoints
  - Tenant context middleware
  - Request validation
  - OpenAPI documentation

### 2. Tenant Management
- **Purpose**: Manages tenant lifecycle and resources
- **Responsibilities**:
  - Create/delete tenants
  - Provision Kubernetes namespaces
  - Setup S3 prefixes
  - Create IAM roles (optional)

### 3. ML Pipeline
- **Training Service**: Trains models with tenant isolation
- **Evaluation Service**: Evaluates model performance
- **Deployment Service**: Deploys models to Kubernetes

### 4. Monitoring System
- **Drift Detection**: Uses Evidently AI to detect data drift
- **Auto-Retraining**: Orchestrates the retraining pipeline
- **Alert Service**: Sends notifications via Slack
- **Metrics**: Exposes Prometheus metrics

### 5. Storage Layer
- **PostgreSQL**: Stores metadata (tenants, models, alerts)
- **MLflow**: Tracks experiments and model versions
- **S3**: Stores model artifacts with tenant prefixes

### 6. Observability Stack
- **Prometheus**: Collects metrics
- **Grafana**: Visualizes metrics and dashboards
- **Alertmanager**: Manages alerts (optional)

## Data Flow

### Model Training Flow
```
1. API receives training request with tenant context
2. Tenant service validates tenant
3. Training service:
   - Loads data from tenant S3 prefix
   - Trains model
   - Logs to MLflow with tenant tag
   - Saves to tenant S3 prefix
   - Records metadata in database
```

### Drift Detection & Auto-Retraining Flow
```
1. Scheduled job or manual trigger
2. Drift detection service:
   - Loads reference and current data
   - Runs Evidently AI analysis
   - Calculates drift score
   - Creates alert if drift detected
3. If drift exceeds threshold:
   - Send Slack alert
   - Trigger training pipeline
   - Evaluate new model
   - Deploy if better than current
   - Send success notification
```

## Tenant Isolation

### Level 1: API Isolation
- X-Tenant-ID header required
- Middleware validates and enforces tenant context
- All database queries scoped by tenant_id

### Level 2: Storage Isolation
- S3 prefix: `tenant-{name}/`
- Bucket policies enforce prefix access
- Model registry scoped by tenant_id

### Level 3: Compute Isolation
- Kubernetes namespace per tenant
- Resource quotas and limits
- Network policies (optional)

### Level 4: IAM Isolation (Optional)
- IAM role per tenant
- Least privilege access
- Cross-account access support
