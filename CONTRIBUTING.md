# Contributing to Resume Analyzer

Thank you for your interest in contributing! Here's how you can help improve this project.

## Development Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd rag-app
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment variables:
```bash
cp .env.example .env
```

## Running the Application

### Option 1: Local Development
```bash
# Start API server
uvicorn api:app --reload --port 8000

# In another terminal, start Streamlit UI
streamlit run ui/streamlit_app.py
```

### Option 2: Docker
```bash
docker-compose up --build
```

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## Code Quality

We use several tools to maintain code quality:

```bash
# Linting
flake8 .

# Security scanning
bandit -r .

# Type checking (optional)
mypy app/
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation if needed
7. Submit a pull request

## Code Style

- Follow PEP 8
- Use type hints where possible
- Write descriptive commit messages
- Keep functions focused and small
- Add docstrings for public methods

## Reporting Issues

When reporting issues, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages (if any)

## Feature Requests

We welcome feature requests! Please:
- Check existing issues first
- Provide clear use cases
- Explain the expected behavior
- Consider implementation complexity

## Areas for Contribution

- 🐛 Bug fixes
- 📚 Documentation improvements
- ✨ New features (see issues)
- 🧪 Test coverage improvements
- 🎨 UI/UX enhancements
- 🚀 Performance optimizations

Thank you for contributing!
