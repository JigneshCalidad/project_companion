# HashiCorp Vault Integration

## Overview

For production deployments, Project Companion can integrate with HashiCorp Vault for secure secret management.

## Prerequisites

- HashiCorp Vault server (local or remote)
- Vault CLI or Python `hvac` library

## Setup

### Install Dependencies

```bash
pip install hvac
```

### Configure Vault

**Start Vault** (development mode):

```bash
vault server -dev
```

**Set Environment Variables**:

```bash
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='your-dev-root-token'
```

### Create Secrets

**Store GitHub Token**:

```bash
vault kv put secret/project-companion/github token=ghp_your_token_here
```

**Store Other Secrets**:

```bash
vault kv put secret/project-companion/config \
  enable_dynamic_scan=false \
  read_only_mode=true
```

## Integration Code

### Vault Service

Create `app/services/vault_service.py`:

```python
import os
import hvac
from typing import Optional


class VaultService:
    """Service for interacting with HashiCorp Vault."""
    
    def __init__(self):
        vault_addr = os.getenv("VAULT_ADDR")
        vault_token = os.getenv("VAULT_TOKEN")
        
        if not vault_addr or not vault_token:
            raise ValueError("VAULT_ADDR and VAULT_TOKEN must be set")
        
        self.client = hvac.Client(url=vault_addr, token=vault_token)
    
    def get_secret(self, path: str, key: str) -> Optional[str]:
        """Get a secret from Vault."""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            return response['data']['data'].get(key)
        except Exception as e:
            print(f"Error reading secret: {e}")
            return None
    
    def get_github_token(self) -> Optional[str]:
        """Get GitHub token from Vault."""
        return self.get_secret("project-companion/github", "token")
    
    def get_config(self, key: str) -> Optional[str]:
        """Get configuration value from Vault."""
        return self.get_secret("project-companion/config", key)
```

### Using Vault in Services

**Update `app/services/scan_service.py`**:

```python
from app.services.vault_service import VaultService

class ScanService:
    def __init__(self, knowledge_store, permission_service):
        self.knowledge_store = knowledge_store
        self.permission_service = permission_service
        self.vault = VaultService()  # Optional
    
    def scan_github_repo(self, owner: str, repo: str):
        """Scan GitHub repo using token from Vault."""
        token = self.vault.get_github_token()
        if not token:
            raise ValueError("GitHub token not found in Vault")
        
        # Use token to scan...
```

## Environment-Based Configuration

Support both environment variables and Vault:

```python
def get_github_token() -> Optional[str]:
    """Get GitHub token from Vault or environment."""
    # Try Vault first
    try:
        vault = VaultService()
        token = vault.get_github_token()
        if token:
            return token
    except:
        pass
    
    # Fallback to environment variable
    return os.getenv("GITHUB_TOKEN")
```

## Production Considerations

### Vault Authentication

**AppRole** (recommended for production):

```python
# Authenticate using AppRole
client = hvac.Client(url=vault_addr)
client.auth.approle.login(
    role_id=os.getenv("VAULT_ROLE_ID"),
    secret_id=os.getenv("VAULT_SECRET_ID")
)
```

**AWS IAM**:

```python
# Authenticate using AWS IAM
client.auth.aws.iam_login(
    access_key=os.getenv("AWS_ACCESS_KEY_ID"),
    secret_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)
```

### Secret Rotation

Vault supports automatic secret rotation. Configure policies:

```hcl
# vault policy
path "secret/project-companion/*" {
  capabilities = ["read"]
}
```

### High Availability

- Use Vault cluster for HA
- Configure auto-unseal
- Set up monitoring and alerts

## Security Best Practices

1. **Least Privilege**: Grant minimal required permissions
2. **Secret Rotation**: Rotate secrets regularly
3. **Audit Logging**: Enable Vault audit logs
4. **Network Security**: Use TLS for Vault communication
5. **Token Management**: Use short-lived tokens when possible

## Troubleshooting

**Connection Errors**:
- Verify `VAULT_ADDR` is correct
- Check network connectivity
- Verify TLS certificates

**Authentication Errors**:
- Verify token/credentials are valid
- Check token expiration
- Verify policy permissions

**Secret Not Found**:
- Verify secret path is correct
- Check secret exists in Vault
- Verify KV version (v1 vs v2)

## References

- [HashiCorp Vault Documentation](https://www.vaultproject.io/docs)
- [Python Vault Client (hvac)](https://hvac.readthedocs.io/)
- [Vault Best Practices](https://learn.hashicorp.com/tutorials/vault/production-hardening)

