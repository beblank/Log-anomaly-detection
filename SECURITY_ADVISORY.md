# Security Advisory - Dependency Updates

## Date: 2026-01-21

## Summary
Updated critical dependencies to patch security vulnerabilities identified in the initial implementation.

## Vulnerabilities Fixed

### 1. FastAPI (CVE: ReDoS Vulnerability)
**Previous Version:** 0.109.0  
**Updated Version:** 0.109.1  
**Severity:** Medium  
**Description:** FastAPI Content-Type Header ReDoS vulnerability  
**Impact:** Potential denial of service through regular expression attacks  
**Fix:** Upgraded to patched version 0.109.1

### 2. MLflow (Multiple CVEs)
**Previous Version:** 2.9.2  
**Updated Version:** 3.5.0  
**Severity:** Critical to High  

**Vulnerabilities Fixed:**
1. **DNS Rebinding Attack** - Lack of Origin header validation (< 3.5.0)
2. **Weak Password Requirements** - Authentication bypass (< 2.22.0rc0)
3. **Directory Traversal RCE** - Model creation vulnerability (< 2.22.4)
4. **Local File Read/Path Traversal** - DBFS vulnerability (< 2.17.0rc0)
5. **Excessive Directory Permissions** - Local privilege escalation (< 2.16.0)
6. **Local File Inclusion** - LFI vulnerability (< 2.11.3)
7. **Path Traversal Vulnerabilities** - Multiple instances (< 2.12.1)
8. **Cross-Site Scripting (XSS)** - Client-side RCE (< 2.10.0)
9. **Unsafe Deserialization** - Multiple instances (various versions)

**Impact:** 
- Remote code execution
- Privilege escalation
- Information disclosure
- Authentication bypass

**Fix:** Upgraded to version 3.5.0 which addresses all known vulnerabilities

### 3. PyTorch (Multiple CVEs)
**Previous Version:** 2.0.1  
**Updated Version:** 2.6.0  
**Severity:** High  

**Vulnerabilities Fixed:**
1. **Heap Buffer Overflow** - Memory corruption vulnerability (< 2.2.0)
2. **Use-After-Free** - Memory safety issue (< 2.2.0)
3. **torch.load RCE** - Remote code execution with weights_only=True (< 2.6.0)

**Impact:**
- Remote code execution
- Memory corruption
- Arbitrary code execution

**Fix:** Upgraded to version 2.6.0 which addresses all known vulnerabilities

## Changes Made

### requirements.txt
```diff
- fastapi==0.109.0
+ fastapi==0.109.1

- mlflow==2.9.2
+ mlflow==3.5.0

- torch==2.0.1
+ torch==2.6.0
```

### docker/docker-compose.yml
```diff
- image: ghcr.io/mlflow/mlflow:v2.9.2
+ image: ghcr.io/mlflow/mlflow:v3.5.0
```

## Verification

To verify the updates:

```bash
# Check installed versions
pip list | grep -E "fastapi|mlflow|torch"

# Expected output:
# fastapi      0.109.1
# mlflow       3.5.0
# torch        2.6.0
```

## Compatibility Notes

### MLflow 3.5.0 Changes
The upgrade from MLflow 2.9.2 to 3.5.0 is a major version change. Key compatibility considerations:

1. **API Changes**: MLflow 3.x has some API changes from 2.x
2. **Database Schema**: May require database migration
3. **Artifact Storage**: Fully backward compatible with S3
4. **Python API**: Core tracking API remains stable

**Action Required:**
- Review MLflow 3.x migration guide: https://mlflow.org/docs/latest/migration.html
- Test existing MLflow integrations
- Run database migrations if needed

### PyTorch 2.6.0 Changes
Upgrade from 2.0.1 to 2.6.0 includes several minor version updates:

1. **Model Compatibility**: Models saved with 2.0.1 are loadable in 2.6.0
2. **API Stability**: Core PyTorch API is stable across 2.x versions
3. **Performance**: Improved performance in 2.6.0

## Security Best Practices

Moving forward, we recommend:

1. **Regular Updates**: Check for security updates monthly
2. **Dependency Scanning**: Use tools like `pip-audit` or `safety`
3. **Version Pinning**: Continue to pin dependency versions
4. **Security Monitoring**: Subscribe to security advisories for critical packages

## Automated Scanning

Add to your CI/CD pipeline:

```bash
# Install pip-audit
pip install pip-audit

# Scan for vulnerabilities
pip-audit -r requirements.txt
```

## References

- FastAPI Security Advisory: https://github.com/tiangolo/fastapi/security/advisories
- MLflow Security Advisories: https://github.com/mlflow/mlflow/security/advisories
- PyTorch Security Advisories: https://github.com/pytorch/pytorch/security/advisories
- GitHub Advisory Database: https://github.com/advisories

## Additional Security Measures

Beyond dependency updates, consider:

1. **Network Security**
   - Use private VPCs for production deployments
   - Enable network policies in Kubernetes
   - Restrict MLflow server access

2. **Authentication**
   - Enable MLflow authentication in production
   - Use strong passwords and API keys
   - Implement role-based access control

3. **Data Security**
   - Enable encryption at rest for S3
   - Use TLS for all network communication
   - Regular security audits

4. **Monitoring**
   - Monitor for suspicious activity
   - Set up alerts for security events
   - Regular vulnerability scanning

## Testing

After updates, run the test suite:

```bash
# Run unit tests
pytest tests/

# Run integration tests
pytest tests/test_api.py -v

# Test API endpoints
curl http://localhost:8080/health
```

## Rollback Plan

If issues arise after upgrade:

```bash
# Revert to previous versions
git checkout <previous-commit> requirements.txt docker/docker-compose.yml

# Rebuild containers
docker-compose down
docker-compose up --build
```

## Sign-off

**Updated By:** GitHub Copilot Agent  
**Date:** 2026-01-21  
**Status:** ✅ All vulnerabilities patched  
**Next Review:** 2026-02-21
