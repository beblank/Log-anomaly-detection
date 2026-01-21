# Multi-Tenancy Guide

## Overview

This platform implements comprehensive multi-tenancy to ensure complete isolation between tenants at all levels of the stack.

## Tenant Lifecycle

### 1. Creating a Tenant

```bash
curl -X POST "http://localhost:8080/api/v1/tenants" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "acme-corp",
    "display_name": "Acme Corporation",
    "description": "Production tenant for Acme Corp"
  }'
```

This automatically provisions:
- Kubernetes namespace: `ml-tenant-acme-corp`
- S3 prefix: `tenant-acme-corp/`
- Database record with tenant metadata
- IAM role (if configured): `ml-saas-acme-corp`

### 2. Using Tenant Context

All API requests (except tenant management) require the `X-Tenant-ID` header:

```bash
curl -X GET "http://localhost:8080/api/v1/models" \
  -H "X-Tenant-ID: tenant-uuid-here"
```

## Tenant Isolation Layers

### API Layer
- Middleware enforces tenant context
- All queries filtered by tenant_id
- No cross-tenant data access possible

### Storage Layer
**S3 Structure:**
```
ml-saas-models/
├── tenant-acme-corp/
│   ├── models/
│   ├── data/
│   └── logs/
├── tenant-beta-inc/
│   ├── models/
│   ├── data/
│   └── logs/
```

### Compute Layer
**Kubernetes:**
- Namespace per tenant with resource quotas
- Network policies for isolation
- Pod security policies
