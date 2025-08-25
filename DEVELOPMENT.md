# 🔬 **Genetic Load Manager - Development Guide**

## 📋 **Table of Contents**

1. [🚀 **Quick Start**](#-quick-start)
2. [🏗️ **Project Structure**](#️-project-structure)
3. [🔧 **Development Environment**](#-development-environment)
4. [🧪 **Testing Strategy**](#-testing-strategy)
5. [📚 **Documentation**](#-documentation)
6. [🔄 **Development Workflow**](#-development-workflow)
7. [🔍 **Code Quality Tools**](#-code-quality-tools)
8. [🚀 **Deployment Process**](#-deployment-process)

---

## 🚀 **Quick Start**

### **1. Clone Repository**

```bash
git clone https://github.com/username/genetic-load-manager.git
cd genetic-load-manager
```

### **2. Setup Development Environment**

```bash
cd development
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **3. Run Tests**

```bash
cd testing
python run_tests.py
```

---

## 🏗️ **Project Structure**

```
genetic-load-manager/
├── 🏠 custom_components/           # Production integration
│   └── genetic_load_manager/      # HACS-ready package
├── 🔬 development/                 # Development environment
│   ├── testing/                   # Test scripts and data
│   ├── documentation/             # Development guides
│   └── requirements.txt           # Development dependencies
├── 📊 *.yaml                      # Dashboard templates
└── 📚 *.md                        # Project documentation
```

### **Key Directories**

#### **`custom_components/genetic_load_manager/`**

- **Production Code**: All files needed for Home Assistant integration
- **HACS Ready**: Proper structure for HACS installation
- **Integration Files**: `__init__.py`, `genetic_algorithm.py`, `pricing_calculator.py`, etc.

#### **`development/`**

- **Testing Environment**: All test scripts and mock data
- **Documentation**: Development guides and research notes
- **Dependencies**: Python requirements and virtual environment

---

## 🔧 **Development Environment**

### **Required Python Version**

- **Python 3.8+** (Home Assistant requirement)
- **Python 3.13** (recommended for development)

### **Core Dependencies**

```bash
# Scientific computing
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
scipy>=1.7.0

# Testing framework
pytest>=6.2.0
pytest-asyncio>=0.15.0
pytest-cov>=2.12.0
pytest-mock>=3.6.0

# Development tools
black>=21.0.0
flake8>=3.9.0
mypy>=0.910
isort>=5.9.0
```

### **Environment Setup**

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import numpy, pandas, matplotlib, scipy; print('All packages installed!')"
```

---

## 🧪 **Testing Strategy**

### **Dual Testing Approach**

The project uses a sophisticated dual testing strategy that allows development without full Home Assistant installation:

#### **1. Local Testing Environment**

```
development/testing/
├── test_integration_local.py      # Core component testing
├── test_real_ha_entities.py      # Mock entity simulation
├── quick_algorithm_test.py       # Fast algorithm validation
├── ems_testing_integration.py    # EMS framework testing
└── run_tests.py                  # Complete test suite runner
```

#### **2. Mock Entity System**

```python
class MockHAEntity:
    """Simulate Home Assistant entities for testing."""

    def __init__(self, entity_id, state, attributes=None):
        self.entity_id = entity_id
        self.state = state
        self.attributes = attributes or {}

# Create realistic test data
mock_entities = {
    "sensor.solcast_pv_forecast": MockHAEntity(
        "sensor.solcast_pv_forecast",
        "28.88",
        {
            "daily_estimate": 28.88,
            "hourly_forecast": [3.44, 3.40, 3.06, ...],
            "data_correct": True
        }
    )
}
```

#### **3. Test Categories**

| Test Type            | Purpose             | Duration | Coverage               |
| -------------------- | ------------------- | -------- | ---------------------- |
| **Quick Test**       | Basic validation    | 10-30s   | Core files, constants  |
| **Integration Test** | Component testing   | 1-5min   | All integration parts  |
| **Real Entity Test** | Mock simulation     | 2-10min  | Full entity processing |
| **Full Suite**       | Complete validation | 2-10min  | Everything end-to-end  |

### **Running Tests**

#### **Quick Algorithm Test**

```bash
cd development/testing
python quick_algorithm_test.py
```

**Purpose**: Verify core algorithm functionality
**Best for**: Development and debugging

#### **Integration Test**

```bash
python test_integration_local.py
```

**Purpose**: Test all integration components
**Best for**: Pre-deployment validation

#### **Full Test Suite**

```bash
python run_tests.py
```

**Purpose**: Test everything end-to-end
**Best for**: Final validation before HACS submission

### **Test Results Example**

```
🚀 Genetic Load Manager - Test Suite Runner
============================================================

🧪 Running: Integration Components Test
📁 Script: test_integration_local.py
============================================================
✅ Integration Components Test completed successfully in 2.17s

🧪 Running: Real HA Entities Simulation
📁 Script: test_real_ha_entities.py
============================================================
✅ Real HA Entities Simulation completed successfully in 1.05s

🧪 Running: Algorithm Local Testing
📁 Script: quick_algorithm_test.py
============================================================
✅ Algorithm Local Testing completed successfully in 0.09s

📊 TEST SUITE SUMMARY
============================================================
✅ PASS Integration Components Test
✅ PASS Real HA Entities Simulation
✅ PASS Algorithm Local Testing

Overall: 3/3 test suites passed (100.0%)
Total time: 4.31 seconds

🎉 All test suites passed! Your integration is ready for testing.
```

---

## 📚 **Documentation**

### **Documentation Structure**

```
📚 Documentation/
├── README.md                    # Main project overview
├── PROJECT_STRUCTURE.md         # Project organization
├── DEPLOYMENT.md               # Installation + Configuration
├── TROUBLESHOOTING.md          # All debugging + troubleshooting
└── DEVELOPMENT.md               # This file - development guide
```

### **Documentation Guidelines**

#### **For End Users**

- **Clear Instructions**: Step-by-step installation and configuration
- **Troubleshooting**: Common issues and solutions
- **Examples**: Real-world configuration examples
- **Screenshots**: Visual guides where helpful

#### **For Developers**

- **Technical Details**: Implementation specifics and architecture
- **Testing Procedures**: How to test and validate changes
- **Development Workflow**: Best practices and processes
- **Code Examples**: Sample code and usage patterns

---

## 🔄 **Development Workflow**

### **1. Development Cycle**

```
Edit Code → Test Locally → Test in HA → Update Docs → Commit
```

### **2. Testing Strategy**

- **Unit Tests**: `development/testing/test_*.py`
- **Integration Tests**: `development/testing/ems_testing_integration.py`
- **Real HA Tests**: `development/testing/test_real_ha_entities.py`

### **3. Documentation Updates**

- **User Docs**: Update root `README.md` and `DEPLOYMENT.md`
- **Dev Docs**: Update `development/README.md` and relevant guides
- **Code Docs**: Update inline comments and docstrings

### **4. Development Process**

#### **Step 1: Make Changes**

```bash
# Edit integration code
edit custom_components/genetic_load_manager/genetic_algorithm.py
edit custom_components/genetic_load_manager/pricing_calculator.py
```

#### **Step 2: Test Locally**

```bash
cd development/testing
python quick_algorithm_test.py        # Fast validation
python test_integration_local.py      # Component testing
python test_real_ha_entities.py       # Mock simulation
```

#### **Step 3: Test in Home Assistant**

```bash
# Copy changes to Home Assistant
cp -r custom_components/genetic_load_manager /path/to/ha/config/custom_components/

# Restart Home Assistant
# Test integration functionality
# Check logs for errors
```

#### **Step 4: Update Documentation**

```bash
# Update relevant documentation files
edit README.md
edit DEPLOYMENT.md
edit TROUBLESHOOTING.md
```

#### **Step 5: Commit Changes**

```bash
git add .
git commit -m "feat: improve genetic algorithm performance"
git push origin main
```

---

## 🔍 **Code Quality Tools**

### **Code Formatting**

#### **Black (Code Formatter)**

```bash
# Format all Python files
black custom_components/genetic_load_manager/

# Check formatting without changes
black --check custom_components/genetic_load_manager/
```

#### **isort (Import Sorter)**

```bash
# Sort imports
isort custom_components/genetic_load_manager/

# Check import order
isort --check-only custom_components/genetic_load_manager/
```

### **Code Quality**

#### **flake8 (Linting)**

```bash
# Run linter
flake8 custom_components/genetic_load_manager/

# Configuration (.flake8)
[flake8]
max-line-length = 88
extend-ignore = E203, W503
```

#### **mypy (Type Checking)**

```bash
# Run type checker
mypy custom_components/genetic_load_manager/

# Configuration (mypy.ini)
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
```

### **Pre-commit Hooks**

#### **Setup Pre-commit**

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

#### **Pre-commit Configuration (.pre-commit-config.yaml)**

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

---

## 🚀 **Deployment Process**

### **Pre-Deployment Checklist**

#### **Code Quality**

- [ ] All tests pass locally
- [ ] Code formatted with Black
- [ ] Imports sorted with isort
- [ ] No linting errors with flake8
- [ ] Type checking passes with mypy

#### **Functionality**

- [ ] Integration loads in Home Assistant
- [ ] All entities created successfully
- [ ] Services work as expected
- [ ] Algorithm runs without errors
- [ ] Dashboard displays correctly

#### **Documentation**

- [ ] README.md updated
- [ ] Configuration examples current
- [ ] Troubleshooting guide complete
- [ ] Installation steps verified

### **Deployment Steps**

#### **1. Final Testing**

```bash
# Run complete test suite
cd development/testing
python run_tests.py

# Test in Home Assistant
# Verify all functionality works
# Check for any new issues
```

#### **2. Version Update**

```bash
# Update version in manifest.json
# Update version in README.md
# Update changelog if applicable
```

#### **3. Commit and Tag**

```bash
git add .
git commit -m "feat: release v1.4.0 - enhanced optimization algorithms"
git tag v1.4.0
git push origin main --tags
```

#### **4. HACS Update**

```bash
# HACS will automatically detect new version
# Users can update via HACS interface
# Monitor for any post-update issues
```

### **Post-Deployment**

#### **Monitor for Issues**

- Check GitHub Issues for bug reports
- Monitor Home Assistant community for problems
- Review logs for any new error patterns

#### **Document Lessons Learned**

- Update troubleshooting guide with new issues
- Improve installation instructions if needed
- Add new configuration examples

---

## 🎯 **Best Practices**

### **Code Organization**

- **Single Responsibility**: Each class/module has one clear purpose
- **Consistent Naming**: Follow Python naming conventions
- **Clear Interfaces**: Well-defined public APIs
- **Error Handling**: Graceful failure with helpful error messages

### **Testing Strategy**

- **Test Early**: Write tests as you develop features
- **Mock Dependencies**: Use mocks for external services
- **Coverage Goals**: Aim for >80% code coverage
- **Real Scenarios**: Test with realistic data and conditions

### **Documentation**

- **Keep Current**: Update docs with code changes
- **User Focused**: Write for the intended audience
- **Examples**: Provide working configuration examples
- **Troubleshooting**: Document common issues and solutions

### **Performance**

- **Profile Code**: Identify bottlenecks early
- **Optimize Algorithms**: Focus on algorithmic improvements
- **Cache Results**: Cache expensive calculations
- **Monitor Resources**: Watch CPU and memory usage

---

## 🆘 **Getting Help**

### **Development Issues**

1. **Check Tests**: Run test suite to identify problems
2. **Review Logs**: Check Home Assistant logs for errors
3. **Simplify**: Reduce complexity to isolate issues
4. **Research**: Look for similar problems in community

### **Community Resources**

- **GitHub Issues**: Report bugs and request features
- **Home Assistant Community**: Ask questions and get help
- **Documentation**: Review this guide and project docs
- **Discussions**: Join community discussions on GitHub

### **Contributing**

1. **Fork Repository**: Create your own copy
2. **Create Branch**: Work on feature or fix
3. **Test Changes**: Ensure all tests pass
4. **Submit PR**: Create pull request with description

---

_For more information, user guides, and community support, visit the project repository and documentation._
