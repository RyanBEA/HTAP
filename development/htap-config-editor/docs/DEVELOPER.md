# HTAP Configuration Editor - Developer Documentation

## Table of Contents

1. [Architecture](#architecture)
2. [Development Setup](#development-setup)
3. [Testing](#testing)
4. [Code Style](#code-style)
5. [Adding New Features](#adding-new-features)
6. [Common Patterns](#common-patterns)
7. [Performance Guidelines](#performance-guidelines)
8. [Release Process](#release-process)

---

## Architecture

### Project Structure

```
htap-config-editor/
├── src/                          # Source code
│   ├── models/                   # Pydantic data models
│   │   ├── common.py            # Shared types
│   │   ├── cost.py              # Cost database models
│   │   ├── option.py            # Options database models
│   │   └── run_config.py        # Run configuration models
│   ├── parsers/                  # File parsing and generation
│   │   ├── run_parser.py        # .run file parser (future)
│   │   ├── run_writer.py        # .run file generator
│   │   └── validation.py        # Configuration validation
│   ├── ui/                       # Streamlit UI components
│   │   ├── components.py        # Reusable UI components
│   │   ├── cost_summary_widget.py  # Cost tab implementation
│   │   ├── export_widget.py     # Export tab implementation
│   │   ├── help_content.py      # Help text and messages
│   │   ├── input_validators.py  # UI input validation
│   │   ├── layout.py            # Main layout structure
│   │   ├── left_panel.py        # Left panel implementation
│   │   ├── loading_states.py    # Loading spinners
│   │   ├── middle_panel.py      # Middle panel implementation
│   │   ├── right_panel.py       # Right panel implementation
│   │   └── search_widget.py     # Search functionality
│   └── utils/                    # Utility modules
│       ├── cost_report.py       # Cost calculation and reporting
│       ├── cost_resolver.py     # Cost resolution with inheritance
│       ├── loaders.py           # Data file loaders with caching
│       └── options_search.py    # Search using pandas
├── tests/                        # Test suite
│   ├── test_*.py                # Unit tests
│   └── test_integration.py      # Integration tests
├── docs/                         # Documentation
│   ├── USER_GUIDE.md            # End-user documentation
│   ├── DEPLOYMENT.md            # Deployment guide
│   ├── DEVELOPER.md             # This file
│   └── examples/                # Example configurations
├── .streamlit/                   # Streamlit configuration
│   └── config.toml              # App settings
├── app.py                        # Main application entry point
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
└── pyproject.toml               # Project metadata
```

---

### Data Flow

```
User Input → Streamlit UI → Session State → Data Models → File Generation → Export

[Browser]
    ↓ User interaction
[Streamlit Widgets] (left_panel.py, middle_panel.py, right_panel.py)
    ↓ Updates
[Session State] (st.session_state)
    ↓ Contains
[RunConfiguration] (run_config.py model)
    ↓ Passed to
[RunFileGenerator] (run_writer.py)
    ↓ Produces
[.run file content] (string)
    ↓ Downloaded by
[Browser] (via st.download_button)
```

**Data loading flow:**
```
Application Startup
    ↓
[load_options()] (loaders.py) → [OptionsDatabase] (option.py)
[load_unit_costs()] (loaders.py) → [UnitCostsDatabase] (cost.py)
    ↓
[OptionsSearch] (options_search.py) ← Used for searching
[CostResolver] (cost_resolver.py) ← Used for cost calculations
    ↓
Stored in st.session_state
    ↓
Used by UI components
```

---

### Component Relationships

**Models Layer** (Pydantic):
- `OptionChoice`, `OptionCategory`, `OptionsDatabase`
- `SourceCostData`, `CostSource`, `UnitCostsDatabase`
- `RunConfiguration`, `RunParameters`, `RunScope`, `Upgrade`
- Provides: Type safety, validation, serialization

**Utils Layer** (Business logic):
- `loaders.py`: Loads JSON files into models
- `options_search.py`: Pandas-based search engine
- `cost_resolver.py`: Cost lookup with inheritance
- `cost_report.py`: Cost aggregation and reporting

**Parsers Layer** (File I/O):
- `run_writer.py`: Generates .run file content
- `validation.py`: Validates RunConfiguration
- Future: `run_parser.py` for parsing existing .run files

**UI Layer** (Streamlit):
- `layout.py`: Main 3-panel structure
- `left_panel.py`: Configuration inputs
- `middle_panel.py`: Option selection (browse/search/stats)
- `right_panel.py`: Review and export (validation/costs/export)
- `components.py`: Shared widgets
- `*_widget.py`: Specific feature implementations

---

## Development Setup

### Prerequisites

- **Python 3.9+**
- **Git**
- **HTAP data files** at `C:/HTAP/`
- **VS Code** (recommended) or other Python IDE

### Clone and Install

```bash
# Clone repository
cd C:/HTAP/development
git clone <repository-url> htap-config-editor
cd htap-config-editor

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verify installation
python -c "import streamlit; print(streamlit.__version__)"
pytest --version
```

### IDE Setup (VS Code)

**Recommended extensions:**
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Ruff (charliermarsh.ruff)
- Even Better TOML (tamasfe.even-better-toml)

**Workspace settings** (`.vscode/settings.json`):
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"],
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.analysis.typeCheckingMode": "basic"
}
```

### Run Development Server

```bash
# Run with auto-reload
streamlit run app.py

# Run with debugging
streamlit run app.py --logger.level=debug

# Run on specific port
streamlit run app.py --server.port=8502
```

---

## Testing

### Running Tests

**All tests:**
```bash
pytest
```

**Specific test file:**
```bash
pytest tests/test_models.py
```

**Specific test:**
```bash
pytest tests/test_models.py::test_option_choice_creation
```

**With coverage:**
```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html to view report
```

**Integration tests:**
```bash
pytest tests/test_integration.py -v -s
```

**Performance benchmarks:**
```bash
pytest tests/test_integration.py::TestPerformance --benchmark-only
```

### Test Organization

**Unit tests** (tests/test_*.py):
- Test individual functions and classes
- Fast (<1ms per test)
- No external dependencies
- Mocked data where possible

**Integration tests** (tests/test_integration.py):
- Test complete workflows
- Use real HTAP data files
- Skip if files not found
- Slower (10-100ms per test)

**Test fixtures** (conftest.py or in test files):
```python
@pytest.fixture
def sample_option():
    """Create sample OptionChoice for testing"""
    return OptionChoice(
        choice_name="test_option",
        description="Test option description"
    )
```

### Coverage Goals

**Target coverage:**
- **Overall**: >85%
- **Models**: >95% (critical for data integrity)
- **Utils**: >90% (business logic)
- **Parsers**: >90% (file generation)
- **UI**: >60% (harder to test, focus on logic)

**Check coverage:**
```bash
pytest --cov=src --cov-report=term-missing
```

### CI/CD Integration

**GitHub Actions** (example `.github/workflows/test.yml`):
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

## Code Style

### PEP 8 Compliance

**Follow PEP 8** for all Python code:
- 88 characters per line (Black default)
- 4 spaces for indentation
- 2 blank lines between top-level definitions
- 1 blank line between methods

**Use Black** for automatic formatting:
```bash
black src/ tests/
```

**Use isort** for import sorting:
```bash
isort src/ tests/
```

**Use Ruff** for linting:
```bash
ruff check src/ tests/
```

### Type Hints

**Always use type hints:**
```python
from typing import List, Dict, Optional, Tuple

def calculate_cost(
    option: OptionChoice,
    source: str,
    multiplier: float = 1.0
) -> Tuple[float, List[Dict]]:
    """
    Calculate cost for option

    Args:
        option: Option to price
        source: Cost source name
        multiplier: Cost multiplier (default 1.0)

    Returns:
        Tuple of (total_cost, component_details)
    """
    ...
```

**Run mypy** for type checking:
```bash
mypy src/
```

### Docstring Standards

**Use Google-style docstrings:**

```python
def search_options(
    query: str,
    categories: Optional[List[str]] = None,
    limit: int = 100
) -> pd.DataFrame:
    """
    Search options with filters

    Args:
        query: Search term to match
        categories: Optional list of categories to filter
        limit: Maximum results to return

    Returns:
        DataFrame with matching options

    Raises:
        ValueError: If limit is negative

    Example:
        >>> results = search_options("window", limit=10)
        >>> len(results) <= 10
        True
    """
    ...
```

### Naming Conventions

**Variables and functions:**
- Use `snake_case`: `option_count`, `calculate_total_cost`
- Be descriptive: `total_cost` not `tc`
- Use verbs for functions: `get_option`, `calculate_cost`, `validate_config`

**Classes:**
- Use `PascalCase`: `OptionChoice`, `CostResolver`, `RunFileGenerator`
- Nouns for data classes: `RunConfiguration`, `ValidationError`
- Descriptive names: `OptionsSearch` not `Search`

**Constants:**
- Use `UPPER_SNAKE_CASE`: `MAX_COMBINATIONS`, `DEFAULT_SOURCE`
- Define at module level
- Group related constants

**Private members:**
- Prefix with underscore: `_internal_method`, `_cache`
- Only if truly internal

---

## Adding New Features

### New Option Category

**Good news**: Categories are loaded automatically from HTAP-options.json!

**No code changes needed** if:
- Category follows standard format in HTAP-options.json
- Uses flat or tree structure
- Has standard fields (structure, costed, options)

**Code changes needed only for**:
- Custom category rendering (e.g., special UI widget)
- Custom validation rules
- Category-specific cost calculation

**Example** (custom rendering):
```python
# In middle_panel.py

if category_name == "Opt-SpecialCategory":
    # Custom widget for this category
    st.multiselect(
        "Special Selection",
        options=category.options.keys(),
        key=f"special_{category_name}"
    )
else:
    # Standard rendering
    render_category_selector(category_name, category)
```

### New Cost Source

**Steps:**

1. **Add to HTAPUnitCosts.json** (HTAP repository):
   ```json
   {
     "sources": {
       "LEEP-NEW-Region": {
         "name": "New Region",
         "description": "Costs for new region"
       }
     },
     "data": {
       "component_id": {
         "LEEP-NEW-Region": {
           "UnitCostMaterials": 10.0,
           "UnitCostLabour": 5.0,
           "description": "Component description",
           "units": "m2"
         }
       }
     }
   }
   ```

2. **Add inheritance** (if needed) in `cost_resolver.py`:
   ```python
   SOURCE_INHERITANCE = {
       "LEEP-NEW-Region": "LEEP-ON-Ottawa",
       # New source falls back to Ottawa
   }
   ```

3. **No UI changes needed** - source appears automatically in dropdown

### New Export Format

**Example**: Add JSON export alongside .run file

1. **Create generator** in `src/parsers/`:
   ```python
   # json_writer.py

   from typing import Dict, Any
   import json
   from src.models.run_config import RunConfiguration

   class JSONConfigGenerator:
       """Generate JSON representation of run configuration"""

       def __init__(self, config: RunConfiguration):
           self.config = config

       def generate(self) -> str:
           """Generate JSON string"""
           data = {
               "parameters": {
                   "run_mode": self.config.parameters.run_mode,
                   "archetype_dir": self.config.parameters.archetype_dir,
                   # ... more fields
               },
               "scope": {
                   "archetypes": self.config.scope.archetypes,
                   # ... more fields
               },
               "upgrades": {
                   attr: upgrade.choices
                   for attr, upgrade in self.config.upgrades.items()
               }
           }
           return json.dumps(data, indent=2)
   ```

2. **Add to export widget** (`export_widget.py`):
   ```python
   from src.parsers.json_writer import JSONConfigGenerator

   # In export tab
   col1, col2 = st.columns(2)

   with col1:
       st.download_button(
           "Download .run file",
           run_content,
           file_name="config.run"
       )

   with col2:
       json_gen = JSONConfigGenerator(run_config)
       json_content = json_gen.generate()
       st.download_button(
           "Download JSON",
           json_content,
           file_name="config.json"
       )
   ```

3. **Add tests** (`tests/test_json_writer.py`):
   ```python
   def test_json_generation(sample_run_config):
       gen = JSONConfigGenerator(sample_run_config)
       content = gen.generate()

       # Should be valid JSON
       data = json.loads(content)

       # Should have expected structure
       assert "parameters" in data
       assert "scope" in data
       assert "upgrades" in data
   ```

---

## Common Patterns

### State Management

**Streamlit session state** is the single source of truth:

```python
import streamlit as st

# Initialize state (in app.py or first use)
if "run_config" not in st.session_state:
    st.session_state.run_config = RunConfiguration(...)

# Read state
config = st.session_state.run_config

# Update state
st.session_state.run_config.upgrades["Opt-ACH"] = Upgrade(...)

# Widget with state
st.text_input(
    "Location",
    value=st.session_state.run_config.scope.locations[0],
    key="location_input"  # Auto-syncs to st.session_state.location_input
)
```

**State organization:**
- `run_config`: Main configuration object
- `options_db`: Loaded options database
- `costs_db`: Loaded unit costs database
- `search`: OptionsSearch instance
- `cost_resolver`: CostResolver instance
- Widget keys: `f"{category}_selection"`

### Error Handling

**Use @handle_errors decorator** for utilities:
```python
from functools import wraps

def handle_errors(func):
    """Decorator to catch and display errors"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"Error in {func.__name__}: {str(e)}")
            return None
    return wrapper

@handle_errors
def load_data(file_path: str):
    """Load data with error handling"""
    return json.load(open(file_path))
```

**User-friendly error messages:**
```python
try:
    data = load_options(path)
except FileNotFoundError:
    st.error(f"""
    ⚠️ Options file not found at: {path}

    Please ensure:
    1. HTAP is installed at C:/HTAP/
    2. HTAP-options.json exists
    3. Path is correct in left panel
    """)
except json.JSONDecodeError:
    st.error("Options file is not valid JSON. Please check file integrity.")
```

### Caching with Streamlit

**For data loading:**
```python
import streamlit as st

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_options(file_path: str) -> OptionsDatabase:
    """Load options with caching"""
    # Expensive operation
    return OptionsDatabase(...)

# Use in app
options_db = load_options("C:/HTAP/HTAP-options.json")
```

**For object creation:**
```python
@st.cache_resource  # Cache resource (not serializable)
def create_search_index(options_db: OptionsDatabase) -> OptionsSearch:
    """Create search index (cached)"""
    return OptionsSearch(options_db)

# Use in app
search = create_search_index(options_db)
```

**Clear cache** when data changes:
```python
st.cache_data.clear()
st.cache_resource.clear()
```

### Loading States

**Use st.spinner for operations >500ms:**
```python
with st.spinner("Loading options..."):
    options_db = load_options(path)

with st.spinner("Calculating costs..."):
    cost_report = calculate_all_costs(config)
```

**Progress bars for long operations:**
```python
progress = st.progress(0)
for i, option in enumerate(options):
    process_option(option)
    progress.progress((i + 1) / len(options))
progress.empty()
```

---

## Performance Guidelines

### Cache Expensive Operations

**What to cache:**
- ✅ File loading (JSON parsing)
- ✅ Database initialization
- ✅ Search index creation
- ✅ Component cost lookups

**What NOT to cache:**
- ❌ Session state
- ❌ User inputs
- ❌ Generated content (changes frequently)

### Limit DataFrame Operations

**Efficient patterns:**
```python
# ✅ Good: Single pass with vectorized operations
df['total'] = df['materials'] + df['labour']
result = df[df['total'] > 100]

# ❌ Bad: Multiple iterations
result = []
for _, row in df.iterrows():
    total = row['materials'] + row['labour']
    if total > 100:
        result.append(row)
```

**Use pandas for search:**
```python
# ✅ Good: Pandas filtering
results = df[
    df['choice'].str.contains(query, case=False) &
    df['category'].isin(categories)
]

# ❌ Bad: Manual filtering
results = []
for item in all_items:
    if query in item['choice'].lower():
        if item['category'] in categories:
            results.append(item)
```

### Avoid Nested Loops in UI

**Efficient rendering:**
```python
# ✅ Good: Render once, use keys
for category_name in categories:
    st.selectbox(
        category_name,
        options[category_name],
        key=f"select_{category_name}"
    )

# ❌ Bad: Nested loops recreating widgets
for category in categories:
    for option in category.options:
        if st.button(f"{category}_{option}"):
            # This creates N*M buttons, very slow
            ...
```

### Performance Targets

- **Search**: <10ms for 769 options
- **Cost calculation**: <100ms per configuration
- **Page load**: <2 seconds
- **Widget response**: <100ms
- **Export generation**: <500ms

**Benchmark critical paths:**
```python
import time

start = time.time()
result = expensive_operation()
elapsed = time.time() - start

if elapsed > 1.0:
    print(f"WARNING: Operation took {elapsed:.2f}s")
```

---

## Release Process

### Version Numbering

**Semantic versioning** (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

**Examples:**
- 1.0.0 → 1.0.1: Bug fix
- 1.0.1 → 1.1.0: New export format added
- 1.1.0 → 2.0.0: Changed data model (breaking)

### Release Checklist

**1. Update version**
```python
# pyproject.toml
[project]
version = "1.1.0"

# app.py (if displayed)
VERSION = "1.1.0"
```

**2. Run all tests**
```bash
pytest
pytest --cov=src --cov-report=term
# Ensure >85% coverage
# Ensure all tests pass
```

**3. Update CHANGELOG**
```markdown
# Changelog

## [1.1.0] - 2025-10-10

### Added
- JSON export format
- Enhanced cost visualization

### Fixed
- Search performance for large queries
- Cost inheritance for BC sources

### Changed
- Updated UI layout for better responsiveness
```

**4. Create git tag**
```bash
git add .
git commit -m "Release v1.1.0"
git tag -a v1.1.0 -m "Version 1.1.0"
git push origin main --tags
```

**5. Deploy**
- Update production environment
- Test deployed version
- Monitor for issues

**6. Announce**
- Notify users of update
- Highlight new features
- Provide migration guide if breaking changes

---

## Development Best Practices

### Code Review Checklist

**Before submitting PR:**
- [ ] All tests pass
- [ ] Coverage maintained or improved
- [ ] Code formatted with Black
- [ ] Type hints added
- [ ] Docstrings written
- [ ] No commented-out code
- [ ] No debug print statements
- [ ] Performance acceptable
- [ ] Error handling added

### Debugging Tips

**Streamlit debugging:**
```python
# Use st.write for quick debugging
st.write("Debug:", variable)

# Check session state
st.write("Session state:", st.session_state)

# Use expander for verbose output
with st.expander("Debug info"):
    st.json(debug_data)
```

**Python debugging:**
```python
# Use breakpoint() for pdb
def some_function():
    breakpoint()  # Execution pauses here
    ...

# Use logging instead of print
import logging
logging.info(f"Processing {item}")
```

**VS Code debugging:**
- Set breakpoints in editor (F9)
- Run "Python: Debug Current File"
- Inspect variables, stack trace
- Step through code

### Common Pitfalls

**1. Streamlit reruns entire script**
- Cache expensive operations
- Don't put slow code at top level
- Use session state for persistence

**2. Widget keys must be unique**
- Use f"{category}_{field}" pattern
- Don't reuse keys across widgets
- Check for key conflicts in console

**3. Pandas SettingWithCopyWarning**
- Use `.copy()` when creating DataFrames
- Don't chain indexing: `df[df['x'] > 0]['y'] = 1`
- Use `.loc` instead: `df.loc[df['x'] > 0, 'y'] = 1`

**4. Pydantic validation errors**
- Check model definitions
- Ensure all required fields provided
- Use `model_validate()` for dict data

---

**Version**: 1.0.0
**Last Updated**: 2025-10-09
**Application**: HTAP Configuration Editor
