# Project Structure

```
Log-anomaly-detection/
├── README.md                          # Main documentation
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore rules
├── setup.py                          # Python package setup
├── requirements.txt                   # Production dependencies
├── requirements-dev.txt              # Development dependencies
├── quick-start.sh                    # Quick start script
│
├── src/                              # Source code
│   └── app/
│       ├── main.py                   # FastAPI application entry point
│       ├── api/                      # API endpoints
│       │   └── v1/
│       │       ├── tenants.py        # Tenant management API
│       │       ├── models.py         # Model management API
│       │       └── monitoring.py     # Monitoring & drift API
│       ├── core/                     # Core functionality
│       │   ├── config.py            # Configuration settings
│       │   ├── database.py          # Database connection
│       │   └── tenant_context.py    # Tenant isolation middleware
│       ├── models/                   # Data models
│       │   ├── database.py          # SQLAlchemy models
│       │   └── schemas.py           # Pydantic schemas
│       ├── services/                 # Business logic
│       │   └── tenant_service.py    # Tenant management service
│       ├── ml_pipeline/              # ML pipeline
│       │   ├── training_service.py  # Model training
│       │   ├── evaluation_service.py # Model evaluation
│       │   └── deployment_service.py # Model deployment
│       └── monitoring/               # Monitoring & drift detection
│           ├── drift_detection.py   # Evidently AI integration
│           ├── auto_retraining.py   # Auto-retraining pipeline
│           ├── alert_service.py     # Slack alerts
│           └── prometheus_metrics.py # Prometheus metrics
│
├── tests/                            # Unit tests
│   ├── conftest.py                  # Test configuration
│   ├── test_api.py                  # API tests
│   └── test_models.py               # Model tests
│
├── docker/                           # Docker configuration
│   ├── Dockerfile                   # Application container
│   └── docker-compose.yml           # Local development stack
│
├── k8s/                             # Kubernetes manifests
│   ├── deployment.yaml              # API deployment
│   ├── prometheus.yaml              # Prometheus deployment
│   └── tenant-namespace-template.yaml # Tenant namespace template
│
├── terraform/                        # Infrastructure as Code
│   ├── main.tf                      # Main configuration
│   ├── variables.tf                 # Variables
│   ├── s3.tf                        # S3 bucket configuration
│   ├── iam.tf                       # IAM roles and policies
│   ├── eks-variables.tf             # EKS variables
│   └── outputs.tf                   # Terraform outputs
│
├── prometheus/                       # Prometheus configuration
│   ├── prometheus.yml               # Prometheus config
│   └── alerts.yml                   # Alert rules
│
├── grafana/                         # Grafana configuration
│   ├── provisioning/
│   │   ├── datasources/            # Data source configuration
│   │   └── dashboards/             # Dashboard provisioning
│   └── dashboards/
│       └── ml-saas-overview.json   # Main dashboard
│
└── docs/                            # Documentation
    ├── ARCHITECTURE.md              # Architecture guide
    ├── DEPLOYMENT.md                # Deployment guide
    └── MULTI_TENANCY.md            # Multi-tenancy guide
```

## Key Components

### API Layer
- **FastAPI**: Modern web framework with automatic OpenAPI docs
- **Tenant Context Middleware**: Enforces tenant isolation
- **REST API**: CRUD operations for tenants, models, and monitoring

### Multi-Tenancy
- **Tenant Service**: Manages tenant lifecycle
- **Isolation**: Kubernetes namespaces, S3 prefixes, database scoping
- **IAM**: Optional per-tenant IAM roles

### ML Pipeline
- **Training**: Isolated model training with MLflow tracking
- **Evaluation**: Performance metrics calculation
- **Deployment**: Automated Kubernetes deployment

### Monitoring
- **Drift Detection**: Evidently AI for data drift analysis
- **Auto-Retraining**: Automated pipeline orchestration
- **Alerts**: Slack notifications for drift and errors
- **Metrics**: Prometheus metrics for observability

### Infrastructure
- **Docker**: Containerized application
- **Kubernetes**: Orchestration with tenant namespaces
- **Terraform**: AWS infrastructure provisioning
- **S3**: Model artifact storage with tenant prefixes

## Technology Stack

### Backend
- Python 3.10+
- FastAPI
- SQLAlchemy
- Pydantic

### ML/MLOps
- Scikit-learn
- MLflow
- Evidently AI

### Storage
- PostgreSQL (metadata)
- S3 (model artifacts)

### Monitoring
- Prometheus
- Grafana
- Slack

### Infrastructure
- Docker
- Kubernetes
- Terraform
- AWS (S3, IAM, EKS)
