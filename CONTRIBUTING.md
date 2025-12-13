# Contributing to LDF

Thank you for your interest in contributing to LDF! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/LLMdotInfo/ldf/issues)
2. If not, create a new issue with:
   - A clear, descriptive title
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Your environment (Python version, OS, LDF version)

### Suggesting Features

1. Check existing [Issues](https://github.com/LLMdotInfo/ldf/issues) for similar suggestions
2. Create a new issue with the "feature request" label
3. Describe the feature and its use case
4. Explain why this would benefit the project

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Ensure tests pass and code style is correct (see below)
5. Commit with clear, descriptive messages
6. Push to your fork and open a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ldf.git
cd ldf

# Install in development mode
pip install -e ".[dev]"
```

## Code Style

We use the following tools to maintain code quality:

- **Black** for code formatting (line length: 100)
- **Ruff** for linting
- **MyPy** for type checking

Run all checks before submitting:

```bash
# Format code
black .

# Lint
ruff check .

# Type check
mypy ldf/
```

## Testing

All changes should include appropriate tests. We use pytest:

```bash
# Run tests with coverage
pytest

# Run specific test file
pytest tests/test_lint.py
```

Aim for maintaining or improving code coverage.

## Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Update documentation if needed
- Add tests for new functionality
- Ensure all CI checks pass
- Reference related issues in your PR description

## License

By contributing to LDF, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have questions, feel free to open an issue or reach out through the project's GitHub discussions.
