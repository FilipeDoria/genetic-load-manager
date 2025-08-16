# Troubleshooting Guide

## Common Issues and Solutions

### 1. Build Issues and Solutions

This section covers common Docker build issues and their solutions in order of preference:

#### Solution A: Use the Python 3.13 Dockerfile (Recommended for Python 3.13+)
The `Dockerfile.python313` is specifically designed for Python 3.13+ compatibility:
```bash
cp Dockerfile.python313 Dockerfile
docker build -t genetic-load-manager .
```

#### Solution B: Use the Pure Python Dockerfile
The `Dockerfile.pure-python` uses only pure Python packages with no compilation needed:
```bash
cp Dockerfile.pure-python Dockerfile
docker build -t genetic-load-manager .
```

#### Solution C: Use the Main Dockerfile
The main `Dockerfile` uses Python 3.11-slim with modern package management.

#### Solution D: Use the Modern Dockerfile
For the latest approach with Python 3.11+:
```bash
cp Dockerfile.modern Dockerfile
docker build -t genetic-load-manager .
```

#### Solution E: Use the Minimal Dockerfile
If you still have issues, use the minimal version:
```bash
cp Dockerfile.minimal Dockerfile
docker build -t genetic-load-manager .
```

#### Solution F: Use the Alternative Dockerfile
For Alpine-based systems:
```bash
cp Dockerfile.alternative Dockerfile
docker build -t genetic-load-manager .
```

#### Solution G: Manual Fix
If none of the above work, check system dependencies:
```dockerfile
# Ensure all system dependencies are installed
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    python3-dev
```

### 2. Build Failures During Package Installation

#### Check Python Version Compatibility
- Use Python 3.13 for best compatibility with current systems
- The pure Python approach ensures compatibility across Python versions
- Modern package management handles dependency issues properly
- All packages are tested for Python 3.13+ compatibility

#### Update Build Tools
```dockerfile
RUN pip install --upgrade pip setuptools wheel
```

#### Install System Dependencies
```dockerfile
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    python3-dev
```

### 3. Runtime Import Errors

#### Test Imports Locally
Run the test script to verify your environment:
```bash
python test_imports.py
```

#### Check Package Versions
Use the exact versions specified in `requirements.txt` or `requirements-minimal.txt`

### 4. Home Assistant Integration Issues

#### Check Entity IDs
- Ensure all configured entity IDs exist in Home Assistant
- Verify entity states are accessible via API

#### Check Permissions
- Ensure the add-on has proper access to Home Assistant entities
- Check API tokens and authentication

### 5. Performance Issues

#### Reduce Genetic Algorithm Complexity
- Decrease population size (default: 50 → 25)
- Reduce generations (default: 100 → 50)
- Increase optimization interval (default: 15 → 30 minutes)

#### Monitor Resource Usage
- Check CPU and memory usage during optimization
- Adjust scheduling based on system capabilities

## Environment-Specific Solutions

### Docker Desktop (Windows/macOS)
- Ensure Docker has sufficient memory (at least 4GB)
- Use the main Dockerfile with Python 3.9-slim

### Linux Systems
- Use the main Dockerfile for best compatibility
- Ensure Docker and build tools are up to date

### ARM-based Systems (Raspberry Pi, etc.)
- Use the main Dockerfile
- May need to build from source for some packages

### Home Assistant Supervised
- Follow the standard add-on installation process
- Use the repository URL: `https://github.com/filipe0doria/genetic-load-manager`

## Debugging Steps

### 1. Check Docker Build Logs
```bash
docker build --no-cache -t genetic-load-manager . 2>&1 | tee build.log
```

### 2. Test Container Locally
```bash
docker run --rm -it genetic-load-manager python test_imports.py
```

### 3. Check Container Logs
```bash
docker logs <container_id>
```

### 4. Verify File Structure
```bash
docker run --rm -it genetic-load-manager ls -la /app
```

## Getting Help

### 1. Check the Logs
- Look for specific error messages
- Note the exact line numbers and context

### 2. Verify Your Environment
- Docker version: `docker --version`
- Python version in container: `docker run genetic-load-manager python --version`
- System architecture: `uname -m`

### 3. Community Support
- Home Assistant Community Forums
- GitHub Issues
- Docker Community Forums

### 4. Provide Debug Information
When asking for help, include:
- Exact error message
- Docker version
- System architecture
- Build logs
- Steps to reproduce

## Prevention

### 1. Use Compatible Versions
- Stick to Python 3.9 for now
- Use the exact package versions in requirements files

### 2. Test Before Deployment
- Always test locally first
- Use the test script to verify imports
- Build and test in a clean environment

### 3. Keep Dependencies Updated
- Regularly update requirements files
- Test compatibility with new versions
- Maintain a changelog of working combinations 