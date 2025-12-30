# Contributing to pymstodoapi

Thank you for considering contributing to pymstodoapi! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose (for containerized development)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/qaq112233/pymstodoapi.git
   cd pymstodoapi
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r api_requirements.txt
   pip install pytest pytest-cov pytest-asyncio black isort flake8 mypy bandit pre-commit
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure credentials
   ```

5. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

### Running the Application Locally

```bash
# Without Docker
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# With Docker
docker-compose up --build
```

### Code Style and Formatting

This project uses:
- **Black** for code formatting (line length: 100)
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking (optional but encouraged)

Run formatters before committing:
```bash
# Format code
black api/
isort api/

# Check linting
flake8 api/

# Type checking (optional)
mypy api/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=api --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v
```

### Security Checks

```bash
# Check for vulnerable dependencies
safety check

# Run security linter
bandit -r api/
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, concise commit messages
   - Add tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass
   - Run linters and formatters

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```
   
   Follow conventional commit format:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test additions/changes
   - `refactor:` for code refactoring
   - `chore:` for maintenance tasks

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**
   - Provide a clear description of changes
   - Link related issues
   - Ensure CI checks pass
   - Request review from maintainers

## Testing Guidelines

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Use fixtures for reusable test data

### Integration Tests
- Test API endpoints end-to-end
- Use TestClient from FastAPI
- Test error cases and edge cases

### Test Coverage
- Aim for at least 80% code coverage
- Focus on critical paths and business logic
- Don't sacrifice quality for coverage percentage

## Documentation

### Code Documentation
- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include type hints for function parameters and return values

### API Documentation
- Update OpenAPI schemas when modifying endpoints
- Add examples to endpoint descriptions
- Document error responses

Example docstring:
```python
def create_task(title: str, list_id: str, due_date: Optional[datetime] = None) -> Task:
    """
    Create a new task in a task list.
    
    Args:
        title: The task title (required)
        list_id: The ID of the task list
        due_date: Optional due date for the task
        
    Returns:
        The created Task object
        
    Raises:
        GraphAPIError: If the API request fails
    """
    pass
```

## Project Structure

```
pymstodoapi/
├── api/                    # Main application code
│   ├── __init__.py
│   ├── main.py            # FastAPI application
│   ├── config.py          # Configuration management
│   ├── auth.py            # Authentication logic
│   ├── graph_client.py    # Microsoft Graph API client
│   ├── dependencies.py    # Dependency injection
│   ├── middleware.py      # Custom middleware
│   ├── models.py          # Pydantic models
│   └── routes/            # API route handlers
├── tests/                 # Test files
├── .github/               # GitHub Actions workflows
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
└── api_requirements.txt   # Python dependencies
```

## Common Issues and Solutions

### Issue: Import errors in tests
**Solution**: Ensure you're running pytest from the project root directory.

### Issue: Rate limit exceeded during development
**Solution**: Increase `RATE_LIMIT_PER_MINUTE` in your `.env` file or disable rate limiting for local development.

### Issue: Docker build fails
**Solution**: Clear Docker cache with `docker system prune -a` and rebuild.

## Questions and Support

- Open an issue for bugs or feature requests
- Check existing issues before creating new ones
- Tag issues appropriately (bug, enhancement, question, etc.)

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
