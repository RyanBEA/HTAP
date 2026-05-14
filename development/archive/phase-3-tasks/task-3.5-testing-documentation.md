# Task 3.5: Testing & Documentation

**Duration:** 3-4 hours
**Phase:** 3 - Export & Polish
**Dependencies:** All previous tasks
**Completion Criteria:** Integration tests passing, user documentation complete, deployment guide created

---

## Objective

Create comprehensive integration tests, user documentation, and deployment guides to ensure the application is production-ready. Validate end-to-end workflows and provide clear instructions for users and developers.

---

## What You'll Build

1. Integration tests for complete workflows
2. User documentation (README.md)
3. Deployment guide
4. Troubleshooting guide
5. Developer documentation
6. Example configurations
7. Testing checklist

---

## Step-by-Step Implementation

### Step 1: Create Integration Tests (90 min)

**File:** `tests/test_integration.py`

```python
"""
Integration tests for complete workflows
"""

import pytest
from pathlib import Path
import pandas as pd

from src.utils import load_options, load_unit_costs
from src.utils.cost_resolver import CostResolver
from src.utils.options_search import OptionsSearch
from src.utils.validator import HTAPConfigValidator
from src.utils.export_validator import ExportValidator
from src.utils.run_file_generator import RunFileGenerator
from src.utils.cost_report import CostReportGenerator


@pytest.fixture
def app_state():
    """
    Setup complete application state
    Simulates what would be in st.session_state
    """
    options_path = "C:/HTAP/HTAP-options.json"
    costs_path = "C:/HTAP/HTAPUnitCosts.json"

    if not Path(options_path).exists() or not Path(costs_path).exists():
        pytest.skip("HTAP files not found")

    state = {}

    # Load databases
    state['options_db'] = load_options(options_path)
    state['costs_db'] = load_unit_costs(costs_path)

    # Initialize utilities
    state['cost_resolver'] = CostResolver(state['costs_db'])
    state['search_index'] = OptionsSearch(state['options_db'])
    state['validator'] = HTAPConfigValidator(
        state['options_db'],
        state['cost_resolver']
    )
    state['export_validator'] = ExportValidator(
        state['options_db'],
        state['validator']
    )
    state['cost_report_gen'] = CostReportGenerator(
        state['options_db'],
        state['cost_resolver']
    )

    # Initialize configuration
    state['run_config'] = {
        'archetypes': ['test_archetype.h2k'],
        'location': 'OTTAWA',
        'ruleset': 'as-found',
        'cost_source': 'LEEP-ON-Ottawa'
    }

    state['selected_options'] = {}

    return state


class TestCompleteWorkflow:
    """Test complete user workflows"""

    def test_basic_configuration_workflow(self, app_state):
        """
        Test basic workflow:
        1. Load data
        2. Select options
        3. Validate
        4. Export
        """
        # Step 1: Verify data loaded
        assert app_state['options_db'] is not None
        assert len(app_state['options_db'].categories) == 34

        # Step 2: Select some options
        # Find options with costs
        for cat_name, category in list(app_state['options_db'].categories.items())[:3]:
            for choice_name in list(category.options.keys())[:1]:
                app_state['selected_options'][cat_name] = {choice_name}
                break

        assert len(app_state['selected_options']) > 0

        # Step 3: Validate configuration
        validator = app_state['export_validator']
        readiness, messages = validator.check_export_readiness(
            app_state['run_config'],
            app_state['selected_options']
        )

        # Should be ready or have warnings (not blocked)
        assert readiness.value in ['ready', 'warnings']

        # Step 4: Export
        generator = RunFileGenerator()
        run_content = generator.generate_run_file(
            app_state['run_config'],
            app_state['selected_options']
        )

        # Validate export
        is_valid, errors = generator.validate_format(run_content)
        assert is_valid
        assert len(errors) == 0

    def test_search_and_select_workflow(self, app_state):
        """
        Test search workflow:
        1. Search for options
        2. Select from results
        3. Verify selection
        """
        # Step 1: Search
        search_index = app_state['search_index']
        results = search_index.search(query="window", limit=10)

        assert len(results) > 0

        # Step 2: Select first result
        if len(results) > 0:
            first_result = results.iloc[0]
            category = first_result['category']
            choice = first_result['choice']

            app_state['selected_options'][category] = {choice}

        # Step 3: Verify
        assert category in app_state['selected_options']
        assert choice in app_state['selected_options'][category]

    def test_cost_calculation_workflow(self, app_state):
        """
        Test cost workflow:
        1. Select options with costs
        2. Calculate costs
        3. Generate report
        4. Export CSV
        """
        # Step 1: Select options with costs
        for cat_name, category in app_state['options_db'].categories.items():
            if category.costed:
                for choice_name, choice in category.options.items():
                    if choice.costs and choice.costs.components:
                        app_state['selected_options'][cat_name] = {choice_name}
                        break
                if cat_name in app_state['selected_options']:
                    break

        if not app_state['selected_options']:
            pytest.skip("No options with costs found")

        # Step 2: Calculate costs
        cost_gen = app_state['cost_report_gen']
        config_cost = cost_gen.calculate_configuration_cost(
            app_state['selected_options'],
            app_state['run_config']['cost_source']
        )

        assert config_cost.total_cost >= 0

        # Step 3: Generate report
        summary = cost_gen.generate_cost_summary_text(config_cost)
        assert "Cost Summary Report" in summary

        # Step 4: Export CSV
        csv_data = cost_gen.export_to_csv(config_cost)
        assert len(csv_data) > 0

    def test_multi_select_parametric_workflow(self, app_state):
        """
        Test parametric run workflow:
        1. Select multiple options per category
        2. Verify combination count
        3. Export
        """
        # Step 1: Select multiple options
        for cat_name, category in list(app_state['options_db'].categories.items())[:2]:
            choices = set(list(category.options.keys())[:3])
            app_state['selected_options'][cat_name] = choices

        # Step 2: Count combinations
        total = 1
        for choices in app_state['selected_options'].values():
            total *= len(choices)

        assert total > 1  # Should create multiple runs

        # Step 3: Export should work
        generator = RunFileGenerator()
        run_content = generator.generate_run_file(
            app_state['run_config'],
            app_state['selected_options']
        )

        is_valid, errors = generator.validate_format(run_content)
        assert is_valid


class TestDataIntegrity:
    """Test data integrity and consistency"""

    def test_all_categories_loadable(self, app_state):
        """Test that all categories load correctly"""
        options_db = app_state['options_db']

        for cat_name, category in options_db.categories.items():
            # Verify structure
            assert hasattr(category, 'category_type')
            assert hasattr(category, 'structure')
            assert hasattr(category, 'options')

            # Verify options
            assert len(category.options) > 0

    def test_cost_database_coverage(self, app_state):
        """Test cost database has reasonable coverage"""
        costs_db = app_state['costs_db']

        # Should have components
        assert len(costs_db.data) > 0

        # Check a few known components exist
        known_components = [
            "1/2in_gypsum_board",
            # Add more if known
        ]

        for component_id in known_components:
            if component_id in costs_db.data:
                assert len(costs_db.data[component_id]) > 0

    def test_search_index_completeness(self, app_state):
        """Test search index covers all options"""
        search_index = app_state['search_index']
        options_db = app_state['options_db']

        # Count options in database
        total_options = sum(
            len(cat.options)
            for cat in options_db.categories.values()
        )

        # Search index should have same count
        assert len(search_index.df) == total_options

    def test_validation_catches_errors(self, app_state):
        """Test that validation catches invalid configurations"""
        validator = app_state['export_validator']

        # Test empty config
        readiness, messages = validator.check_export_readiness({}, {})
        assert readiness.value == 'blocked'

        # Test invalid option
        bad_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }
        bad_options = {
            'Invalid-Category': {'Invalid-Choice'}
        }

        readiness, messages = validator.check_export_readiness(bad_config, bad_options)
        assert readiness.value == 'blocked'


class TestPerformance:
    """Test performance benchmarks"""

    def test_search_performance(self, app_state):
        """Test search completes quickly"""
        import time

        search_index = app_state['search_index']

        # Warm up
        search_index.search("test")

        # Time search
        start = time.time()
        results = search_index.search("window", limit=100)
        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 10, f"Search took {elapsed_ms:.1f}ms (expected <10ms)"

    def test_cost_calculation_performance(self, app_state):
        """Test cost calculation is fast enough"""
        import time

        # Select multiple options
        for cat_name, category in list(app_state['options_db'].categories.items())[:5]:
            choices = set(list(category.options.keys())[:2])
            app_state['selected_options'][cat_name] = choices

        cost_gen = app_state['cost_report_gen']

        start = time.time()
        config_cost = cost_gen.calculate_configuration_cost(
            app_state['selected_options'],
            'LEEP-ON-Ottawa'
        )
        elapsed_ms = (time.time() - start) * 1000

        # Should complete in reasonable time
        assert elapsed_ms < 1000, f"Cost calc took {elapsed_ms:.1f}ms (expected <1000ms)"
```

---

### Step 2: Create User Documentation (60 min)

**File:** `docs/USER_GUIDE.md`

```markdown
# HTAP Configuration Editor - User Guide

## Overview

The HTAP Configuration Editor is a graphical interface for creating and managing HTAP (Housing Technology Assessment Platform) run configurations. It provides a simple 3-panel layout for configuring parametric HOT2000 simulations.

## Installation

### Prerequisites

- Python 3.9 or higher
- HTAP installed at `C:/HTAP/`
- HTAP-options.json and HTAPUnitCosts.json in HTAP directory

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   streamlit run src/app.py
   ```

3. Open browser to `http://localhost:8501`

## User Interface

The application has three panels:

### LEFT Panel: Run Configuration

Configure basic run parameters:

1. **Archetypes**: Select one or more .h2k building models
2. **Location**: Choose weather location
3. **Ruleset**: Select building code (usually 'as-found')
4. **Cost Source**: Choose regional cost database

### MIDDLE Panel: Option Selection

Select building upgrade options:

- **Browse Tab**: Browse options by category
- **Search Tab**: Search for specific options
- **Statistics Tab**: View category statistics

**Selection Modes:**
- **Single-select**: Choose one option per category
- **Multi-select**: Choose multiple options (creates parametric runs)

### RIGHT Panel: Review & Export

Review and export your configuration:

- **Validation Tab**: Check configuration status
- **Costs Tab**: View estimated costs
- **Export Tab**: Download .run file

## Typical Workflow

### 1. Basic Configuration

1. Open application
2. In LEFT panel:
   - Select archetypes (e.g., `SFD_1storey.h2k`)
   - Choose location (e.g., `OTTAWA`)
   - Select cost source (e.g., `LEEP-ON-Ottawa`)

### 2. Select Options

1. In MIDDLE panel:
   - Browse categories or use search
   - Click options to select
   - Review selections in expander

### 3. Review Costs

1. In RIGHT panel, Costs tab:
   - View total estimated costs
   - See breakdown by category
   - Download cost report

### 4. Export Configuration

1. In RIGHT panel, Export tab:
   - Review validation status
   - Preview .run file
   - Download .run file

### 5. Run Simulation

1. Save .run file to `C:/HTAP/`
2. Run with htap-prm.rb:
   ```bash
   ruby C:/HTAP/htap-prm.rb -r your_config.run -c -k
   ```

## Advanced Features

### Parametric Runs

Create multiple simulation combinations:

1. Click "Switch to Multi Select" in MIDDLE panel
2. Select multiple options per category
3. View total combinations in RIGHT panel
4. Export generates all combinations

**Example:**
- 2 archetypes × 3 wall options × 2 window options = 12 simulations

### Search

Find options quickly:

1. Use Search tab in MIDDLE panel
2. Enter search term (e.g., "low-e")
3. Apply filters:
   - Category filter
   - Cost presence
   - Structure type
4. Select from results

### Cost Comparison

Compare costs across regions:

1. In RIGHT panel, Costs tab
2. Use "Cost Source Comparison" section
3. Select multiple sources
4. View comparison chart

## Tips & Best Practices

### Before Starting

- ✅ Verify HTAP is installed at `C:/HTAP/`
- ✅ Check archetype files exist
- ✅ Know your target location and building code

### While Configuring

- 💡 Start with single-select mode
- 💡 Test with one archetype first
- 💡 Review validation warnings
- 💡 Check cost estimates

### Large Parametric Runs

- ⚠️ >100 combinations may take hours
- ⚠️ >500 combinations not recommended
- 💡 Use filters to reduce combinations
- 💡 Test smaller subsets first

## Troubleshooting

### "File not found" error

- Check HTAP is at `C:/HTAP/`
- Verify HTAP-options.json exists
- Check file permissions

### Options not loading

- Verify JSON files are valid
- Check console for error messages
- Try refreshing browser

### Export validation fails

- Review error messages
- Fix missing required fields
- Check option selections are valid

### Costs showing as $0

- Verify cost source is selected
- Check option has cost data
- Try different cost source

## Keyboard Shortcuts

- `Ctrl+R`: Reload app
- `Ctrl+/`: Open keyboard shortcuts panel
- `?`: Show help

## Getting Help

- Documentation: [HTAP GitHub](https://github.com/NRCan-IETS-CE-O-HBC/HTAP)
- Issues: Report bugs on GitHub Issues
- Email: [Support email]

## Appendix: File Formats

### .run File Format

```
RunParameters_START
  run-mode = mesh
  archetype-dir = C:/HTAP
  options-file = HTAP-options.json
  unit-costs-db = HTAPUnitCosts.json
RunParameters_END

RunScope_START
  archetypes = archetype1.h2k, archetype2.h2k
  locations = OTTAWA
  rulesets = as-found
RunScope_END

Upgrades_START
  Opt-Windows = WindowOption1, WindowOption2
  Opt-Walls = WallOption1
Upgrades_END
```

### Example Configurations

See `examples/` directory for:
- Basic single run
- Parametric study
- Cost optimization
- Location comparison
```

---

### Step 3: Create Deployment Guide (30 min)

**File:** `docs/DEPLOYMENT.md`

```markdown
# Deployment Guide

## Production Deployment

### Option 1: Local Deployment

1. Install Python 3.9+
2. Clone repository
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `streamlit run src/app.py`

### Option 2: Streamlit Cloud

1. Push code to GitHub
2. Connect Streamlit Cloud to repository
3. Configure secrets for file paths
4. Deploy

### Option 3: Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "src/app.py", "--server.port=8501"]
```

Build and run:
```bash
docker build -t htap-editor .
docker run -p 8501:8501 -v C:/HTAP:/htap htap-editor
```

## Configuration

### Environment Variables

- `HTAP_PATH`: Path to HTAP installation (default: `C:/HTAP`)
- `OPTIONS_FILE`: Path to options JSON (default: `HTAP-options.json`)
- `COSTS_FILE`: Path to costs JSON (default: `HTAPUnitCosts.json`)

### Streamlit Config

Create `.streamlit/config.toml`:

```toml
[server]
port = 8501
enableCORS = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

## Performance Tuning

### Caching

Application uses Streamlit caching for:
- Data loading (`@st.cache_data`)
- Cost resolution (`@lru_cache`)
- Search index (in-memory)

### Memory

Expected memory usage:
- Base app: ~50MB
- With data loaded: ~100MB
- With large datasets: ~200MB

## Monitoring

### Health Checks

Add health check endpoint:

```python
# src/health.py
def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "data_loaded": 'options_db' in st.session_state
    }
```

### Logging

Configure logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='htap_editor.log'
)
```

## Security

### File Access

- Validate all file paths
- Sanitize user inputs
- Restrict file operations to HTAP directory

### Data Privacy

- No sensitive data stored
- No external API calls
- All processing local

## Backup & Recovery

### Data Backup

Backup these files:
- Configuration files (`.run` files)
- User preferences (if implemented)
- Application logs

### Disaster Recovery

1. Keep HTAP data files backed up
2. Version control all code
3. Document configuration
```

---

### Step 4: Create Developer Documentation (30 min)

**File:** `docs/DEVELOPER.md`

```markdown
# Developer Documentation

## Architecture

### Project Structure

```
src/
├── models/           # Pydantic data models
│   ├── option.py     # Option categories and choices
│   └── cost.py       # Cost database models
├── utils/            # Utility functions
│   ├── loaders.py    # Data loading
│   ├── cost_resolver.py
│   ├── options_search.py
│   ├── validator.py
│   ├── export_validator.py
│   ├── run_file_generator.py
│   └── cost_report.py
├── ui/               # UI components
│   ├── left_panel.py
│   ├── middle_panel.py
│   ├── right_panel.py
│   └── widgets/
└── app.py            # Main entry point

tests/                # Unit and integration tests
docs/                 # Documentation
```

### Data Flow

1. User selects options in UI
2. Options stored in `st.session_state`
3. Validation runs on state changes
4. Export generates .run file from state

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- IDE (VS Code recommended)

### Setup

```bash
# Clone repo
git clone https://github.com/NRCan-IETS-CE-O-HBC/HTAP.git
cd HTAP/streamlit-editor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Run app
streamlit run src/app.py
```

## Testing

### Unit Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_cost_resolver.py

# Run with coverage
pytest --cov=src

# Run with verbose output
pytest -v -s
```

### Integration Tests

```bash
pytest tests/test_integration.py
```

## Code Style

### Python Style

Follow PEP 8:
- Use Black for formatting
- Use isort for imports
- Use mypy for type checking

```bash
black src/
isort src/
mypy src/
```

### Type Hints

Always use type hints:

```python
def load_options(filepath: str) -> OptionsDatabase:
    ...

def calculate_cost(
    option: OptionChoice,
    source: str
) -> Tuple[float, List[Dict]]:
    ...
```

## Adding New Features

### Adding a New Option Category

1. Data model exists (from HTAP-options.json)
2. No code changes needed
3. Search automatically includes new category

### Adding a New Cost Source

1. Add to HTAPUnitCosts.json
2. Update inheritance in CostResolver if needed
3. Test with real options

### Adding a New Export Format

1. Create new generator in `src/utils/`
2. Add UI widget
3. Add tests

## Common Patterns

### State Management

```python
# Initialize state
if 'key' not in st.session_state:
    st.session_state.key = default_value

# Update state
st.session_state.key = new_value

# React to state change
if st.session_state.key == value:
    # Do something
```

### Error Handling

```python
from src.utils.error_handler import handle_errors

@handle_errors("Failed to load data", show_details=True)
def load_data(filepath: str):
    # May raise exceptions
    ...
```

### Caching

```python
@st.cache_data
def load_large_file(filepath: str):
    # Expensive operation
    ...
```

## Performance Guidelines

- Cache expensive operations
- Limit DataFrame operations
- Use pandas for search (fast enough)
- Avoid nested loops in UI code

## Release Process

1. Update version in `pyproject.toml`
2. Run all tests
3. Update CHANGELOG.md
4. Create git tag
5. Deploy to production
```

---

### Step 5: Update README-TASK-PLANS.md (30 min)

Will do this after all task plans are complete.

---

## Acceptance Criteria

✅ **Integration tests created** covering complete workflows
✅ **User guide written** with examples and screenshots
✅ **Deployment guide created** with multiple options
✅ **Developer docs complete** with architecture and patterns
✅ **All tests passing** (unit + integration)
✅ **README updated** with installation and usage
✅ **Example configurations** provided

---

## Testing Checklist

### Functional Testing

- [ ] All 15 task plans implemented
- [ ] Data loading works
- [ ] Option selection works
- [ ] Search works
- [ ] Validation works
- [ ] Cost calculation works
- [ ] Export works
- [ ] Downloaded .run file is valid

### Integration Testing

- [ ] Complete workflow (load → select → export)
- [ ] Search → select workflow
- [ ] Multi-select parametric workflow
- [ ] Cost calculation workflow

### Performance Testing

- [ ] Search <10ms
- [ ] Cost calculation <1s
- [ ] UI responsive
- [ ] No memory leaks

### Usability Testing

- [ ] Clear error messages
- [ ] Help text helpful
- [ ] Intuitive navigation
- [ ] Loading states visible

## Documentation Checklist

- [ ] User guide complete
- [ ] Deployment guide complete
- [ ] Developer docs complete
- [ ] API documentation (if applicable)
- [ ] Example configurations
- [ ] Troubleshooting guide
- [ ] FAQ section

---

## Next Steps

After completing this task:

1. Run full test suite
2. Review all documentation
3. Create example configurations
4. **PROJECT COMPLETE!** 🎉

---

## Time Tracking

- Integration tests: 90 min
- User documentation: 60 min
- Deployment guide: 30 min
- Developer docs: 30 min
- README updates: 30 min
- **Total: ~4 hours**

---

## Success Metrics

After completion, you should have:

- ✅ 100% test coverage on critical paths
- ✅ Complete user documentation
- ✅ Deployment-ready application
- ✅ Clear developer onboarding docs
- ✅ Working example configurations
- ✅ Production-ready MVP
