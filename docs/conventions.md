# Code Conventions and Contribution Guidelines

## Code Style

### Python

- Follow PEP 8
- Use type hints where possible
- Maximum line length: 100 characters
- Use `black` for formatting
- Use `ruff` for linting

**Example**:

```python
from typing import List, Optional

def process_files(files: List[str]) -> Optional[dict]:
    """Process a list of files."""
    if not files:
        return None
    # ...
```

### JavaScript/React

- Use ES6+ features
- Prefer functional components
- Use meaningful variable names
- Follow React best practices

**Example**:

```javascript
function Component({ prop1, prop2 }) {
  const [state, setState] = useState(null);
  
  useEffect(() => {
    // Effect logic
  }, [prop1]);
  
  return <div>Content</div>;
}
```

## Project Structure

```
project-companion/
├── app/              # FastAPI application
├── scanner/          # Code scanning modules
├── knowledge/        # Knowledge graph storage
├── audit/            # Audit logging
├── cli/              # CLI interface
├── ui/               # React frontend
├── tests/            # Test suite
└── docs/             # Documentation
```

## Naming Conventions

- **Files**: `snake_case.py` for Python, `PascalCase.jsx` for React components
- **Classes**: `PascalCase`
- **Functions**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Variables**: `snake_case`

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When something goes wrong
    """
    pass
```

### Comments

- Use comments to explain **why**, not **what**
- Keep comments up-to-date with code
- Remove commented-out code before committing

## Testing

### Test Structure

- One test file per module: `test_<module>.py`
- Test functions: `test_<functionality>()`
- Use descriptive test names

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_scanner.py

# With coverage
pytest --cov=app --cov=scanner
```

### Test Coverage

- Aim for >80% coverage
- Test edge cases
- Test error conditions

## Git Workflow

### Branch Naming

- `main`: Production-ready code
- `develop`: Development branch
- `feature/<name>`: New features
- `fix/<name>`: Bug fixes
- `docs/<name>`: Documentation updates

### Commit Messages

Follow conventional commits:

```
feat: Add new parser for Rust
fix: Handle empty file lists
docs: Update README with examples
test: Add tests for graph service
refactor: Simplify scan service
```

### Pull Requests

- Keep PRs focused and small
- Include tests for new features
- Update documentation
- Request review before merging

## Security

- Never commit secrets
- Use environment variables
- Validate all inputs
- Follow principle of least privilege
- Log security-relevant events

## Performance

- Profile before optimizing
- Use appropriate data structures
- Consider caching for expensive operations
- Optimize database queries

## Error Handling

- Use specific exception types
- Provide helpful error messages
- Log errors appropriately
- Don't expose internal details

## Dependencies

- Keep dependencies up-to-date
- Prefer standard library when possible
- Document why external dependencies are needed
- Pin versions in production

## Questions?

If you're unsure about conventions, ask! We're here to help.

