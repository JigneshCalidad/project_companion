# GitHub OAuth Integration Example

## Overview

This guide demonstrates how to integrate Project Companion with GitHub using OAuth tokens for secure repository access.

## Prerequisites

- GitHub account
- Personal Access Token (PAT) or GitHub App credentials

## Option 1: Personal Access Token (PAT)

### Creating a PAT

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` (for private repositories)
   - `read:org` (if accessing organization repos)
4. Generate and copy the token

### Using the PAT

**Local Development**:

Create a `.env` file:

```bash
GITHUB_TOKEN=ghp_your_token_here
```

**Environment Variable**:

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

**In Code**:

```python
import os
token = os.getenv("GITHUB_TOKEN")
```

### Security Best Practices

- Never commit tokens to version control
- Use minimal required scopes
- Rotate tokens regularly
- Use fine-grained tokens when possible

## Option 2: GitHub App

### Creating a GitHub App

1. Go to your organization/user settings → Developer settings → GitHub Apps
2. Click "New GitHub App"
3. Configure:
   - Name: "Project Companion"
   - Homepage URL: Your app URL
   - Webhook: Optional
   - Permissions:
     - Repository contents: Read-only
     - Metadata: Read-only
4. Generate a private key
5. Note the App ID

### Installing the App

1. Install the app on your repositories
2. Note the installation ID

### Using GitHub App Credentials

**Store Credentials Securely**:

```bash
# .env
GITHUB_APP_ID=123456
GITHUB_APP_INSTALLATION_ID=789012
GITHUB_APP_PRIVATE_KEY_PATH=/path/to/private-key.pem
```

**Authenticate**:

```python
import jwt
import time
import requests

def get_github_app_token(app_id, installation_id, private_key_path):
    # Generate JWT
    now = int(time.time())
    payload = {
        'iat': now - 60,
        'exp': now + 600,
        'iss': app_id
    }
    
    with open(private_key_path, 'r') as f:
        private_key = f.read()
    
    token = jwt.encode(payload, private_key, algorithm='RS256')
    
    # Get installation access token
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    response = requests.post(
        f'https://api.github.com/app/installations/{installation_id}/access_tokens',
        headers=headers
    )
    
    return response.json()['token']
```

## Scanning GitHub Repositories

### Using the CLI

```bash
# With PAT
export GITHUB_TOKEN=ghp_...
companion scan github://owner/repo-name

# Or specify token inline (not recommended)
GITHUB_TOKEN=ghp_... companion scan github://owner/repo-name
```

### Using the API

```bash
curl -X POST http://localhost:8000/api/scan/static \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -d '{"path": "github://owner/repo-name"}'
```

## Implementation Example

Add to `scanner/static_scanner.py`:

```python
def scan_github_repo(owner: str, repo: str, token: str) -> ScanResult:
    """Scan a GitHub repository."""
    import tempfile
    import subprocess
    
    # Clone repository to temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_url = f"https://{token}@github.com/{owner}/{repo}.git"
        subprocess.run(
            ["git", "clone", repo_url, tmpdir],
            check=True,
            capture_output=True
        )
        
        # Scan the cloned repository
        return scan_repository(tmpdir)
```

## Security Considerations

1. **Token Storage**: Never store tokens in code or version control
2. **Token Scope**: Use minimal required permissions
3. **Token Rotation**: Rotate tokens regularly
4. **Ephemeral Tokens**: Prefer GitHub App tokens (they expire)
5. **Audit**: Log all repository access

## Troubleshooting

**401 Unauthorized**:
- Check token validity
- Verify token has required scopes
- Ensure token hasn't expired

**403 Forbidden**:
- Token lacks required permissions
- Repository is private and token can't access it

**Rate Limiting**:
- GitHub has rate limits
- Use authenticated requests for higher limits
- Implement retry logic with exponential backoff

## References

- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub Apps](https://docs.github.com/en/apps)
- [GitHub API Authentication](https://docs.github.com/en/rest/authentication)

