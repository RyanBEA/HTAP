# Task 1.1: Project Setup & Dependencies

**Duration:** 2-3 hours
**Phase:** 1 - Foundation
**Dependencies:** None
**Completion Criteria:** Project structure created, dependencies installed, basic app runs

---

## Objective

Set up the foundational project structure, development environment, and core dependencies for the HTAP Configuration Editor.

---

## What You'll Build

1. Complete project directory structure
2. Python virtual environment
3. Dependency management (requirements.txt)
4. Basic configuration files
5. Initial documentation (README.md)
6. Minimal Streamlit app that launches successfully

---

## Technical Approach

### Project Structure

```
htap-config-editor/
├── .venv/                    # Virtual environment (generated)
├── src/
│   ├── __init__.py
│   ├── models/               # Pydantic data models
│   │   └── __init__.py
│   ├── parsers/              # File parsers (run, JSON)
│   │   └── __init__.py
│   ├── ui/                   # Streamlit UI components
│   │   └── __init__.py
│   └── utils/                # Utility functions
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_parsers.py
│   └── test_ui.py
├── data/                     # Sample data for development
│   └── .gitkeep
├── .streamlit/               # Streamlit configuration
│   └── config.toml
├── app.py                    # Main Streamlit application
├── requirements.txt          # Dependencies
├── requirements-dev.txt      # Dev dependencies
├── .gitignore
├── .env.example              # Environment variable template
├── pyproject.toml            # Project metadata (optional but recommended)
└── README.md                 # Project documentation
```

### Technology Stack

**Core:**
- Python 3.10+ (3.11 or 3.12 recommended)
- Streamlit 1.28.0+

**Data Handling:**
- pandas 2.1.0+ (tabular data manipulation)
- pydantic 2.4.0+ (data validation and models)

**Development:**
- pytest 7.4.0+ (testing framework)
- pytest-cov 4.1.0+ (code coverage)
- black 23.9.0+ (code formatting)
- ruff 0.0.290+ (fast linting)
- mypy 1.5.0+ (type checking)

**UI Enhancement:**
- streamlit-aggrid 0.3.4+ (enhanced data grids)
- plotly 5.17.0+ (cost visualization charts)

---

## Step-by-Step Implementation

### Step 1: Create Directory Structure (15 min)

```bash
cd C:/HTAP/development
mkdir htap-config-editor
cd htap-config-editor

# Create all directories
mkdir -p src/{models,parsers,ui,utils}
mkdir -p tests
mkdir -p data
mkdir -p .streamlit

# Create __init__.py files
touch src/__init__.py
touch src/models/__init__.py
touch src/parsers/__init__.py
touch src/ui/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py

# Create placeholder for data
touch data/.gitkeep
```

### Step 2: Create requirements.txt (10 min)

**File:** `requirements.txt`

```txt
# HTAP Configuration Editor - Core Dependencies
# Python 3.10+

# Core Framework
streamlit>=1.28.0

# Data Processing & Validation
pandas>=2.1.0
pydantic>=2.4.0

# UI Components
streamlit-aggrid>=0.3.4
plotly>=5.17.0

# Utilities
python-dotenv>=1.0.0
```

**File:** `requirements-dev.txt`

```txt
# Development Dependencies
-r requirements.txt

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0

# Code Quality
black>=23.9.0
ruff>=0.0.290
mypy>=1.5.0

# Type Stubs
pandas-stubs>=2.0.0
```

### Step 3: Create Virtual Environment (10 min)

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Git Bash / MSYS)
source .venv/Scripts/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Step 4: Create Configuration Files (20 min)

**File:** `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#0066CC"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
maxUploadSize = 200

[browser]
gatherUsageStats = false
```

**File:** `.env.example`

```env
# HTAP Configuration Editor - Environment Variables

# Path to HTAP installation
HTAP_ROOT=C:/HTAP

# Paths to configuration files
HTAP_OPTIONS_PATH=C:/HTAP/HTAP-options.json
HTAP_COSTS_PATH=C:/HTAP/HTAPUnitCosts.json

# Cache settings
CACHE_DIR=.cache
CACHE_MAX_SIZE_MB=500

# Logging
LOG_LEVEL=INFO
```

**File:** `.gitignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
env/

# Streamlit
.streamlit/secrets.toml

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
*.cover

# OS
.DS_Store
Thumbs.db
desktop.ini

# Project specific
.cache/
.env
data/*.json
data/*.run
!data/.gitkeep

# Exports
exports/
*.bundle/
```

**File:** `pyproject.toml`

```toml
[project]
name = "htap-config-editor"
version = "0.1.0"
description = "Streamlit-based configuration editor for HTAP"
requires-python = ">=3.10"
authors = [
    {name = "HTAP Team"}
]
readme = "README.md"

[tool.black]
line-length = 100
target-version = ['py310']

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
```

### Step 5: Create Basic Streamlit App (30 min)

**File:** `app.py`

```python
"""
HTAP Configuration Editor
Main Streamlit application entry point
"""

import streamlit as st
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="HTAP Configuration Editor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    """Main application entry point"""

    st.title("🏠 HTAP Configuration Editor")
    st.markdown("---")

    # Welcome message
    st.info("""
    **Welcome to the HTAP Configuration Editor!**

    This tool helps you configure and manage HTAP simulation runs by providing
    a visual interface to:
    - Browse and select options from HTAP-options.json
    - View and assign cost components from HTAPUnitCosts.json
    - Build and export validated .run files

    **Status:** Project initialized successfully! ✅
    """)

    # Sidebar
    with st.sidebar:
        st.header("Configuration")

        st.subheader("Data Sources")
        options_file = st.text_input(
            "HTAP Options File",
            value="C:/HTAP/HTAP-options.json",
            help="Path to HTAP-options.json"
        )

        costs_file = st.text_input(
            "Unit Costs File",
            value="C:/HTAP/HTAPUnitCosts.json",
            help="Path to HTAPUnitCosts.json"
        )

        st.markdown("---")
        st.subheader("About")
        st.caption("Version: 0.1.0")
        st.caption("Phase 1: Foundation")

    # Main content placeholder
    st.header("Quick Start")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("1️⃣ Load Data")
        st.write("Load HTAP options and costs")
        st.button("Load Files", disabled=True, help="Coming in Task 1.2")

    with col2:
        st.subheader("2️⃣ Configure Run")
        st.write("Select options and build configuration")
        st.button("Start Configuration", disabled=True, help="Coming in Task 1.3")

    with col3:
        st.subheader("3️⃣ Export")
        st.write("Export validated .run file")
        st.button("Export Configuration", disabled=True, help="Coming in Task 3.1")

    # Footer
    st.markdown("---")
    st.caption("HTAP Configuration Editor | NRCan IETS")


if __name__ == "__main__":
    main()
```

### Step 6: Create README.md (30 min)

**File:** `README.md`

```markdown
# HTAP Configuration Editor

A Streamlit-based 3-panel editor for managing HTAP run configurations.

## Overview

This tool provides a visual interface for configuring HTAP (Housing Technology Assessment Platform) simulation runs, eliminating the need to manually edit multiple JSON files.

**Status:** Phase 1 - Foundation (In Development)

## Features (Planned)

- 📂 Load and parse HTAP-options.json (50MB+)
- 💰 Manage unit costs from HTAPUnitCosts.json
- 📝 Parse and edit .run configuration files
- 🔍 Search and filter options
- ✅ Real-time validation
- 📦 Export validated configuration bundles

## Requirements

- Python 3.10 or higher
- HTAP installation at `C:/HTAP/`

## Installation

### 1. Clone or navigate to the project

```bash
cd C:/HTAP/development/htap-config-editor
```

### 2. Create virtual environment

```bash
python -m venv .venv
source .venv/Scripts/activate  # Git Bash
# or
.venv\Scripts\activate  # Windows CMD
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your HTAP paths
```

## Usage

### Run the application

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

### Run tests

```bash
pytest tests/ -v
pytest tests/ --cov=src  # With coverage
```

### Code formatting

```bash
black src/ tests/
ruff check src/ tests/
mypy src/
```

## Project Structure

```
htap-config-editor/
├── src/
│   ├── models/      # Pydantic data models
│   ├── parsers/     # File parsers (run, JSON)
│   ├── ui/          # Streamlit UI components
│   └── utils/       # Utility functions
├── tests/           # Unit tests
├── data/            # Sample data (not in git)
├── .streamlit/      # Streamlit config
├── app.py           # Main application
└── requirements.txt # Dependencies
```

## Development Roadmap

See [roadmap.md](../roadmap.md) for detailed development phases.

### Phase 1: Foundation (Week 1) - Current Phase

- [x] Task 1.1: Project Setup & Dependencies
- [ ] Task 1.2: Data Models & Loading
- [ ] Task 1.3: Basic UI Layout
- [ ] Task 1.4: Run File Parser
- [ ] Task 1.5: Options Data Structure

## Contributing

This is an internal NRCan tool. For questions or issues, contact the HTAP team.

## License

Internal use only - NRCan IETS
```

### Step 7: Test the Setup (15 min)

```bash
# Verify imports
python -c "import streamlit; import pandas; import pydantic; print('All imports OK')"

# Run the app
streamlit run app.py

# In another terminal, run basic tests
pytest tests/ -v
```

---

## Acceptance Criteria

✅ **Project structure created** with all directories and __init__.py files
✅ **Virtual environment** created and activated
✅ **Dependencies installed** without errors
✅ **Configuration files** (.streamlit/config.toml, .env.example, .gitignore)
✅ **Basic Streamlit app** runs without errors
✅ **README.md** documents installation and usage
✅ **App displays** welcome page with three disabled placeholder buttons

---

## Common Issues & Solutions

### Issue: Python version too old
**Solution:** Install Python 3.10+ from python.org

### Issue: pip install fails on Windows
**Solution:**
```bash
python -m pip install --upgrade pip
pip install --upgrade setuptools wheel
```

### Issue: Streamlit won't start
**Solution:**
```bash
# Check if port is in use
netstat -ano | findstr :8501
# Use different port
streamlit run app.py --server.port 8502
```

---

## Next Steps

After completing this task:
1. Commit changes to git
2. Verify app runs successfully
3. Move to **Task 1.2: Data Models & Loading**

---

## Time Tracking

- Directory structure: 15 min
- Requirements files: 10 min
- Virtual environment: 10 min
- Config files: 20 min
- Basic app.py: 30 min
- README.md: 30 min
- Testing: 15 min
- **Total: ~2.5 hours**
