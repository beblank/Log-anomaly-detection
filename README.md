# Multi-Tenant ML SaaS Platform

A production-ready Multi-Tenant Machine Learning SaaS platform for Log Anomaly Detection with Auto-Retraining and Comprehensive Monitoring.

## 🌟 Features

### Multi-Tenancy
- **Namespace per tenant** - Isolated Kubernetes namespaces
- **S3 bucket prefix per tenant** - Segregated storage for models and data
- **Model registry scoped by tenant_id** - Tenant-specific model versioning
- **IAM role per tenant** - Fine-grained access control (optional)

### MLOps Lifecycle
Complete automated pipeline:
```
Data Drift Detection → Alert → Trigger Pipeline → Train → Evaluate → Register → Deploy
```

### Monitoring & Observability
- **Prometheus** - Metrics collection and alerting
- **Evidently AI** - Advanced data drift detection
- **Grafana** - Real-time dashboards and visualizations
- **Slack** - Instant alerts and notifications

### AWS Integration
- S3 for model storage with tenant isolation
- IAM roles for secure access control
- Ready for EKS deployment
- Terraform infrastructure as code

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       API Gateway / LB                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          Tenant Context Middleware                     │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌─────────────┬──────────────┬───────────────────────────┐│
│  │  Tenant API │  Model API   │  Monitoring API           ││
│  └─────────────┴──────────────┴───────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
           │                 │                │
           ▼                 ▼                ▼
┌──────────────────┐  ┌─────────────┐  ┌──────────────┐
│   PostgreSQL     │  │   MLflow    │  │  Prometheus  │
│   (Metadata)     │  │  (Tracking) │  │  (Metrics)   │
└──────────────────┘  └─────────────┘  └──────────────┘
                              │
                              ▼
                      ┌───────────────┐
                      │  S3 Storage   │
                      │ (per tenant)  │
                      └───────────────┘

Kubernetes Namespaces (per tenant):
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  ml-tenant-acme  │  │  ml-tenant-beta  │  │  ml-tenant-...   │
│  ┌────────────┐  │  │  ┌────────────┐  │  │  ┌────────────┐  │
│  │ Model Pod  │  │  │  │ Model Pod  │  │  │  │ Model Pod  │  │
│  └────────────┘  │  │  └────────────┘  │  │  └────────────┘  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Kubernetes cluster (for production)
- AWS account (optional, for S3 and IAM)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/beblank/Log-anomaly-detection.git
cd Log-anomaly-detection
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Start services with Docker Compose**
```bash
cd docker
docker-compose up -d
```

5. **Initialize the database**
```bash
python -m alembic upgrade head
```

6. **Run the application**
```bash
python -m src.app.main
```

The API will be available at:
- API: http://localhost:8080
- Docs: http://localhost:8080/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## 📚 API Usage

### Create a Tenant
```bash
curl -X POST "http://localhost:8080/api/v1/tenants" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "acme-corp",
    "display_name": "Acme Corporation",
    "description": "Acme Corp tenant"
  }'
```

### Train a Model
```bash
curl -X POST "http://localhost:8080/api/v1/models/train" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: <tenant-id>" \
  -d '{
    "tenant_id": "<tenant-id>",
    "model_name": "log-anomaly-v1",
    "model_type": "log_anomaly_detector",
    "training_data_path": "s3://bucket/tenant-acme-corp/data/training.csv"
  }'
```

### Check for Data Drift
```bash
curl -X POST "http://localhost:8080/api/v1/monitoring/check-drift/<model-id>" \
  -H "X-Tenant-ID: <tenant-id>"
```

### Trigger Auto-Retraining
```bash
curl -X POST "http://localhost:8080/api/v1/monitoring/auto-retrain/<model-id>" \
  -H "X-Tenant-ID: <tenant-id>"
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Application
APP_NAME=Multi-Tenant ML SaaS
DEBUG=false

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mlsaas

# AWS
AWS_REGION=us-east-1
AWS_S3_BUCKET=ml-saas-models
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000

# Monitoring
PROMETHEUS_PORT=8000
EVIDENTLY_PORT=8001

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_BOT_TOKEN=xoxb-your-bot-token

# Drift Detection
DRIFT_CHECK_INTERVAL_HOURS=24
DRIFT_THRESHOLD=0.1

# Kubernetes
K8S_NAMESPACE_PREFIX=ml-tenant
K8S_IN_CLUSTER=false
```

## 🚢 Deployment

### Kubernetes Deployment

1. **Apply base infrastructure**
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/prometheus.yaml
```

2. **Create tenant namespace (for each tenant)**
```bash
# Edit tenant-namespace-template.yaml with tenant name
kubectl apply -f k8s/tenant-namespace-template.yaml
```

### AWS Infrastructure with Terraform

1. **Initialize Terraform**
```bash
cd terraform
terraform init
```

2. **Review and apply**
```bash
terraform plan
terraform apply
```

This creates:
- S3 bucket with versioning and encryption
- IAM roles and policies
- Tenant isolation policies

## 📊 Monitoring

### Prometheus Metrics

Available metrics:
- `ml_training_runs_total` - Total training runs
- `ml_drift_alerts_total` - Drift alerts
- `ml_retraining_triggered_total` - Auto-retraining events
- `ml_models_deployed_total` - Deployed models
- `ml_model_accuracy` - Model accuracy
- `ml_model_f1_score` - Model F1 score
- `ml_prediction_latency_seconds` - Prediction latency

### Grafana Dashboards

Pre-configured dashboards available:
1. **Multi-Tenant Overview** - System-wide metrics
2. **Per-Tenant Dashboard** - Tenant-specific metrics
3. **Model Performance** - ML model metrics
4. **Drift Detection** - Data drift monitoring

Access Grafana at http://localhost:3000

### Slack Alerts

Configure Slack webhook URL to receive:
- Data drift detection alerts
- Auto-retraining success/failure notifications
- System health alerts

## 🔒 Security

### Tenant Isolation

1. **Network Isolation** - Kubernetes namespaces with NetworkPolicies
2. **Storage Isolation** - S3 bucket prefixes per tenant
3. **API Isolation** - Tenant ID validation middleware
4. **IAM Isolation** - Optional per-tenant IAM roles

### Best Practices

- Always use HTTPS in production
- Rotate AWS credentials regularly
- Use Kubernetes secrets for sensitive data
- Enable audit logging
- Implement rate limiting per tenant

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- MLflow for experiment tracking
- Evidently AI for drift detection
- Prometheus & Grafana for monitoring
- FastAPI for the web framework
- Scikit-learn for ML models

## 📞 Support

For issues and questions:
- GitHub Issues: https://github.com/beblank/Log-anomaly-detection/issues

---

Made with ❤️ for the ML community
