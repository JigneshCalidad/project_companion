# Security Guidelines

## 🔒 Security Philosophy

Project Companion is designed with **security-first principles**. The default mode is read-only, and all privileged actions require explicit human approval.

## 🛡️ Core Security Principles

### 1. Read-Only by Default

- The bot never modifies files, executes commands, or makes network calls without explicit permission
- All scanning operations are read-only file system operations
- No automatic code execution or dynamic analysis without user consent

### 2. Explicit Approval Workflow

Every action that could modify your project follows this workflow:

```
Request → Log → Approve → Execute → Log Result
```

- Actions are stored in an audit log before execution
- Each action requires a unique approval token
- Approval must come from an authenticated user session
- All actions are logged with timestamps and user context

### 3. Ephemeral Credentials

- Never store long-lived credentials in plaintext
- Use environment variables or encrypted keystores
- Credentials are loaded only when needed
- Credentials are cleared from memory after use

### 4. No Plaintext Secrets

- Never commit secrets to the repository
- Use `.env` files (gitignored) for local development
- Use HashiCorp Vault or similar for production
- All secrets must be encrypted at rest

## 🔐 Secret Management

### Local Development

Create a `.env` file in the project root:

```bash
# .env (DO NOT COMMIT THIS FILE)
GITHUB_TOKEN=ghp_your_token_here
ENABLE_DYNAMIC_SCAN=false
VAULT_ADDR=https://vault.example.com
VAULT_TOKEN=your_vault_token
```

Add `.env` to `.gitignore` (already included).

### Production Deployment

**Option 1: Environment Variables**

Set secrets as environment variables in your deployment platform:

```bash
export GITHUB_TOKEN=ghp_...
export ENABLE_DYNAMIC_SCAN=false
```

**Option 2: HashiCorp Vault**

See `docs/vault_integration.md` for detailed setup.

**Option 3: Encrypted Keystore**

Use the built-in encrypted keystore (coming soon).

## 🚨 Threat Model

### Potential Threats

1. **Unauthorized Code Execution**
   - Mitigation: All actions require approval, no automatic execution

2. **Secret Leakage**
   - Mitigation: No secrets in code, encrypted storage, ephemeral credentials

3. **Unauthorized Repository Access**
   - Mitigation: Explicit token management, scope-limited tokens

4. **Dynamic Scanning Abuse**
   - Mitigation: Disabled by default, requires explicit enablement and confirmation

5. **Audit Log Tampering**
   - Mitigation: Append-only log, checksums, read-only audit view

## 📋 Security Checklist

Before deploying or sharing:

- [ ] Verify `.env` is in `.gitignore`
- [ ] Check that no secrets are in committed files
- [ ] Review `audit/` directory permissions
- [ ] Ensure `ENABLE_DYNAMIC_SCAN=false` unless explicitly needed
- [ ] Verify all GitHub tokens have minimal required scopes
- [ ] Review audit logs for any unexpected actions
- [ ] Test approval workflow end-to-end

## 🔍 Audit Logging

All actions are logged to `audit/audit.log`:

```
[2024-01-15 10:30:45] ACTION_REQUEST: user=done, cmd="git mv old.py new.py", status=pending
[2024-01-15 10:31:12] ACTION_APPROVE: user=done, action_id=123, approved=true
[2024-01-15 10:31:13] ACTION_EXECUTE: user=done, action_id=123, result=success
```

The audit log is append-only and should be monitored regularly.

## 🚫 What Project Companion Will NOT Do

- Execute code without explicit approval
- Make outbound network calls without configuration
- Store credentials in plaintext
- Auto-enable dynamic scanning
- Bypass approval workflows
- Access repositories without valid tokens

## 🛠️ Reporting Security Issues

If you discover a security vulnerability:

1. **Do not** open a public issue
2. Email security concerns to the maintainer
3. Include steps to reproduce
4. Allow time for patching before disclosure

## 📚 Additional Resources

- `docs/vault_integration.md` - Secure secret storage
- `docs/oauth_example.md` - Safe OAuth token management
- `docs/conventions.md` - Secure coding practices

---

**Remember**: Security is a shared responsibility. Always review actions before approval, monitor audit logs, and keep credentials secure.

