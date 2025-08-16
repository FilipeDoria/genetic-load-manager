# Contributing to GA Load Manager

Thank you for your interest in contributing to the GA Load Manager Home Assistant add-on! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites
- Python 3.13+
- Docker
- Home Assistant (for testing)
- Git

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/genetic-load-manager.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Install dependencies: `pip install -r requirements-python313.txt`
5. Make your changes
6. Test your changes: `python test_python313.py`
7. Commit and push: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose

### Testing
- Run the test script before committing: `python test_python313.py`
- Test Docker builds: `docker build -f Dockerfile.python313 .`
- Test the web interface locally
- Ensure compatibility with Python 3.13+

### Docker Images
- Test all Dockerfile variants
- Ensure builds work on different architectures
- Keep images lightweight and secure

## Pull Request Process

1. **Create a descriptive title** that explains the change
2. **Fill out the PR template** completely
3. **Link related issues** using `Fixes #123` or `Closes #123`
4. **Test thoroughly** before submitting
5. **Update documentation** if needed
6. **Respond to review comments** promptly

## Issue Reporting

### Bug Reports
- Use the bug report template
- Include steps to reproduce
- Provide environment details
- Attach relevant logs

### Feature Requests
- Use the feature request template
- Explain the use case
- Consider alternatives
- Provide examples

## Release Process

### Versioning
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update `CHANGELOG.md` with changes
- Tag releases with `v1.0.0` format

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version numbers updated
- [ ] Docker images build successfully
- [ ] Release notes prepared

## Community Guidelines

- Be respectful and inclusive
- Help other contributors
- Provide constructive feedback
- Follow the Code of Conduct

## Getting Help

- Check existing issues and PRs
- Search documentation
- Ask questions in issues
- Join community discussions

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

Thank you for contributing to GA Load Manager! 🚀 