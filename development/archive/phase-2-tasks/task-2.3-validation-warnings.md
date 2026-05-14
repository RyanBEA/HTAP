# Task 2.3: Validation & Warnings

**Duration:** 3-4 hours
**Phase:** 2 - Core Functionality
**Dependencies:** Task 1.2 (Data Models), Task 2.1 (Panel Interactions), Task 2.2 (Cost Resolution)
**Completion Criteria:** Comprehensive validation system, inline warnings, configuration completeness checks

---

## Objective

Implement a comprehensive validation system that checks configuration completeness, detects missing costs, warns about conflicts, and provides real-time feedback to guide users toward valid HTAP configurations.

---

## What You'll Build

1. Configuration validator class with multiple validation rules
2. Real-time validation in UI (LEFT and MIDDLE panels)
3. Warning and error displays with severity levels
4. Configuration completeness checker
5. Cost completeness validator
6. Unit tests with real HTAP data

---

## Context: Validation Requirements

Based on HTAP .run file structure and options data:

1. **Required selections:**
   - At least one archetype
   - Location must be selected
   - Ruleset must be selected

2. **Cost warnings:**
   - Options marked as `costed: true` should have cost data
   - Missing cost components should be flagged

3. **Category constraints:**
   - Some categories may have `stop_on_error: true` requiring valid selection
   - Default values available via `category.default`

4. **Configuration completeness:**
   - All selected options should be from defined categories
   - Options should exist in HTAP-options.json

---

## Step-by-Step Implementation

### Step 1: Create Validation Module (90 min)

**File:** `src/utils/validator.py`

```python
"""
Configuration validation for HTAP runs
Validates completeness, cost data, and configuration constraints
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum

from src.models.option import OptionsDatabase, OptionCategory
from src.utils.cost_resolver import CostResolver


class ValidationSeverity(str, Enum):
    """Validation message severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ValidationMessage:
    """A validation message with severity and context"""

    def __init__(
        self,
        severity: ValidationSeverity,
        message: str,
        category: Optional[str] = None,
        field: Optional[str] = None
    ):
        self.severity = severity
        self.message = message
        self.category = category
        self.field = field

    def __repr__(self):
        context = f" [{self.category}]" if self.category else ""
        return f"{self.severity.value.upper()}{context}: {self.message}"


class HTAPConfigValidator:
    """
    Validates HTAP run configurations
    """

    def __init__(
        self,
        options_db: OptionsDatabase,
        cost_resolver: Optional[CostResolver] = None
    ):
        """
        Initialize validator

        Args:
            options_db: Loaded options database
            cost_resolver: Optional cost resolver for cost validation
        """
        self.options_db = options_db
        self.cost_resolver = cost_resolver

    def validate_run_config(
        self,
        run_config: Dict
    ) -> List[ValidationMessage]:
        """
        Validate run configuration (LEFT panel data)

        Args:
            run_config: Dict with keys: archetypes, location, ruleset, cost_source

        Returns:
            List of validation messages
        """
        messages = []

        # Check archetypes
        archetypes = run_config.get('archetypes', [])
        if not archetypes:
            messages.append(ValidationMessage(
                ValidationSeverity.ERROR,
                "At least one archetype must be selected",
                field="archetypes"
            ))
        elif len(archetypes) > 10:
            messages.append(ValidationMessage(
                ValidationSeverity.WARNING,
                f"{len(archetypes)} archetypes selected. Large runs may take significant time.",
                field="archetypes"
            ))

        # Check location
        location = run_config.get('location')
        if not location:
            messages.append(ValidationMessage(
                ValidationSeverity.ERROR,
                "Location must be selected",
                field="location"
            ))

        # Check ruleset
        ruleset = run_config.get('ruleset')
        if not ruleset:
            messages.append(ValidationMessage(
                ValidationSeverity.WARNING,
                "No ruleset selected, using 'as-found'",
                field="ruleset"
            ))

        # Check cost source
        cost_source = run_config.get('cost_source')
        if not cost_source:
            messages.append(ValidationMessage(
                ValidationSeverity.WARNING,
                "No cost source selected, costs will not be calculated",
                field="cost_source"
            ))

        return messages

    def validate_selected_options(
        self,
        selected_options: Dict[str, str],
        cost_source: Optional[str] = None
    ) -> List[ValidationMessage]:
        """
        Validate selected options (MIDDLE panel data)

        Args:
            selected_options: Dict mapping category_name -> choice_name
            cost_source: Cost source for cost validation (optional)

        Returns:
            List of validation messages
        """
        messages = []

        for category_name, choice_name in selected_options.items():
            # Validate category exists
            if category_name not in self.options_db.categories:
                messages.append(ValidationMessage(
                    ValidationSeverity.ERROR,
                    f"Unknown category '{category_name}'",
                    category=category_name
                ))
                continue

            category = self.options_db.categories[category_name]

            # Validate choice exists in category
            if choice_name not in category.options:
                messages.append(ValidationMessage(
                    ValidationSeverity.ERROR,
                    f"Unknown choice '{choice_name}' in category '{category_name}'",
                    category=category_name
                ))
                continue

            choice = category.options[choice_name]

            # Validate cost completeness if category is costed
            if category.costed and self.cost_resolver and cost_source:
                if not choice.costs or not choice.costs.components:
                    messages.append(ValidationMessage(
                        ValidationSeverity.WARNING,
                        f"Option '{choice_name}' has no cost data (category is marked as costed)",
                        category=category_name
                    ))
                else:
                    # Check for missing cost components
                    is_valid, missing = self.cost_resolver.validate_option_costs(
                        choice,
                        cost_source
                    )
                    if not is_valid:
                        messages.append(ValidationMessage(
                            ValidationSeverity.WARNING,
                            f"Missing cost components: {', '.join(missing[:3])}"
                            + (f" and {len(missing)-3} more" if len(missing) > 3 else ""),
                            category=category_name
                        ))

        return messages

    def validate_configuration_completeness(
        self,
        selected_options: Dict[str, str]
    ) -> List[ValidationMessage]:
        """
        Check if configuration has selections for important categories

        Args:
            selected_options: Dict mapping category_name -> choice_name

        Returns:
            List of validation messages
        """
        messages = []

        # Define important categories that should have selections
        important_categories = [
            "Opt-Location",
            "Opt-Archetype",
            "Opt-Heating-Cooling",
            "Opt-DHWSystem",
            "Opt-VentSystem"
        ]

        for cat_name in important_categories:
            if cat_name in self.options_db.categories:
                if cat_name not in selected_options:
                    category = self.options_db.categories[cat_name]
                    default = category.default if hasattr(category, 'default') else None

                    if default:
                        messages.append(ValidationMessage(
                            ValidationSeverity.INFO,
                            f"No selection for '{cat_name}', will use default: '{default}'",
                            category=cat_name
                        ))
                    else:
                        messages.append(ValidationMessage(
                            ValidationSeverity.WARNING,
                            f"No selection for important category '{cat_name}'",
                            category=cat_name
                        ))

        return messages

    def get_category_status(
        self,
        category_name: str,
        selected_choice: Optional[str] = None,
        cost_source: Optional[str] = None
    ) -> Tuple[str, List[ValidationMessage]]:
        """
        Get status of a specific category

        Args:
            category_name: Category to check
            selected_choice: Currently selected choice (if any)
            cost_source: Cost source for cost validation

        Returns:
            Tuple of (status_icon, list_of_messages)
            status_icon: "✅" (valid), "⚠️" (warning), "❌" (error), "⬜" (not selected)
        """
        messages = []

        if category_name not in self.options_db.categories:
            return "❌", [ValidationMessage(
                ValidationSeverity.ERROR,
                f"Category '{category_name}' not found",
                category=category_name
            )]

        category = self.options_db.categories[category_name]

        # Not selected
        if not selected_choice:
            if category.default:
                return "⬜", [ValidationMessage(
                    ValidationSeverity.INFO,
                    f"Will use default: {category.default}",
                    category=category_name
                )]
            return "⬜", []

        # Selected but invalid choice
        if selected_choice not in category.options:
            return "❌", [ValidationMessage(
                ValidationSeverity.ERROR,
                f"Invalid choice '{selected_choice}'",
                category=category_name
            )]

        choice = category.options[selected_choice]

        # Check cost completeness
        has_warnings = False
        if category.costed and self.cost_resolver and cost_source:
            if not choice.costs or not choice.costs.components:
                messages.append(ValidationMessage(
                    ValidationSeverity.WARNING,
                    "No cost data available",
                    category=category_name
                ))
                has_warnings = True
            else:
                is_valid, missing = self.cost_resolver.validate_option_costs(
                    choice,
                    cost_source
                )
                if not is_valid:
                    messages.append(ValidationMessage(
                        ValidationSeverity.WARNING,
                        f"Missing {len(missing)} cost components",
                        category=category_name
                    ))
                    has_warnings = True

        if has_warnings:
            return "⚠️", messages

        return "✅", messages

    def validate_full_configuration(
        self,
        run_config: Dict,
        selected_options: Dict[str, str]
    ) -> Dict[str, List[ValidationMessage]]:
        """
        Perform comprehensive validation of entire configuration

        Args:
            run_config: Run configuration from LEFT panel
            selected_options: Selected options from MIDDLE panel

        Returns:
            Dict with keys: 'run_config', 'options', 'completeness', 'summary'
            Each containing list of validation messages
        """
        cost_source = run_config.get('cost_source')

        return {
            'run_config': self.validate_run_config(run_config),
            'options': self.validate_selected_options(selected_options, cost_source),
            'completeness': self.validate_configuration_completeness(selected_options),
            'summary': self._generate_summary_messages(run_config, selected_options)
        }

    def _generate_summary_messages(
        self,
        run_config: Dict,
        selected_options: Dict[str, str]
    ) -> List[ValidationMessage]:
        """Generate overall configuration summary messages"""
        messages = []

        archetypes = run_config.get('archetypes', [])
        location = run_config.get('location')

        if archetypes and location and selected_options:
            total_combinations = len(archetypes) * len(selected_options)
            messages.append(ValidationMessage(
                ValidationSeverity.INFO,
                f"Configuration will generate {total_combinations} simulation runs"
            ))

        return messages

    def has_errors(self, messages: List[ValidationMessage]) -> bool:
        """Check if any messages are errors"""
        return any(msg.severity == ValidationSeverity.ERROR for msg in messages)

    def has_warnings(self, messages: List[ValidationMessage]) -> bool:
        """Check if any messages are warnings"""
        return any(msg.severity == ValidationSeverity.WARNING for msg in messages)
```

---

### Step 2: Update LEFT Panel with Validation (30 min)

**File:** `src/ui/left_panel.py`

Add validation feedback to LEFT panel:

```python
def render_left_panel():
    """Render LEFT panel with validation"""
    st.header("1️⃣ Run Configuration")

    # Initialize validator
    if 'validator' not in st.session_state:
        from src.utils.validator import HTAPConfigValidator
        st.session_state.validator = HTAPConfigValidator(
            st.session_state.options_db,
            st.session_state.get('cost_resolver')
        )

    validator = st.session_state.validator

    # ... existing selectors ...

    # Validate configuration
    run_config = st.session_state.get('run_config', {})
    validation_messages = validator.validate_run_config(run_config)

    # Display validation messages
    if validation_messages:
        st.divider()
        st.subheader("⚠️ Configuration Status")

        for msg in validation_messages:
            if msg.severity == "error":
                st.error(msg.message)
            elif msg.severity == "warning":
                st.warning(msg.message)
            else:
                st.info(msg.message)

    # Show overall status
    has_errors = validator.has_errors(validation_messages)
    has_warnings = validator.has_warnings(validation_messages)

    if has_errors:
        st.error("❌ Configuration has errors that must be fixed")
    elif has_warnings:
        st.warning("⚠️ Configuration has warnings")
    else:
        st.success("✅ Configuration is valid")
```

---

### Step 3: Update MIDDLE Panel with Validation (45 min)

**File:** `src/ui/middle_panel.py`

Add per-option validation:

```python
def render_middle_panel():
    """Render MIDDLE panel with validation"""
    st.header("2️⃣ Select Options")

    if 'options_db' not in st.session_state:
        st.info("👈 Load HTAP options in the left panel first")
        return

    validator = st.session_state.get('validator')
    cost_source = st.session_state.run_config.get('cost_source')

    # ... existing category selector ...

    if selected_category:
        category = st.session_state.options_db.categories[selected_category]
        selected_choice = st.session_state.selected_options.get(selected_category)

        # Get category validation status
        if validator:
            status_icon, status_messages = validator.get_category_status(
                selected_category,
                selected_choice,
                cost_source
            )
        else:
            status_icon = "⬜"
            status_messages = []

        # Show category header with status
        col1, col2 = st.columns([4, 1])
        with col1:
            st.subheader(f"Options in {selected_category}")
        with col2:
            st.metric("Status", status_icon)

        # Show category-level messages
        if status_messages:
            for msg in status_messages:
                if msg.severity == "error":
                    st.error(msg.message)
                elif msg.severity == "warning":
                    st.warning(msg.message)
                else:
                    st.info(msg.message)

        # Show category metadata
        if category.costed:
            st.caption("💰 This category affects costs")
        if hasattr(category, 'stop_on_error') and category.stop_on_error:
            st.caption("⚠️ Selection required")

        # ... existing option display with costs ...

        # Add validation warnings per option
        for choice_name, choice in category.options.items():
            # ... existing button and cost display ...

            # Add warnings if this choice is selected and has issues
            if choice_name == selected_choice and validator:
                choice_messages = validator.validate_selected_options(
                    {selected_category: choice_name},
                    cost_source
                )
                if choice_messages:
                    for msg in choice_messages:
                        if msg.severity == "warning":
                            st.warning(f"⚠️ {msg.message}")
```

---

### Step 4: Create Validation Summary Widget (30 min)

**File:** `src/ui/validation_summary.py`

```python
"""
Validation summary widget for RIGHT panel
"""

import streamlit as st
from src.utils.validator import ValidationSeverity


def render_validation_summary():
    """
    Render validation summary in RIGHT panel
    Shows overall configuration health
    """
    st.subheader("✓ Validation Summary")

    validator = st.session_state.get('validator')
    if not validator:
        st.info("Validation not available")
        return

    run_config = st.session_state.get('run_config', {})
    selected_options = st.session_state.get('selected_options', {})

    # Perform full validation
    validation_results = validator.validate_full_configuration(
        run_config,
        selected_options
    )

    # Count by severity
    all_messages = (
        validation_results['run_config'] +
        validation_results['options'] +
        validation_results['completeness'] +
        validation_results['summary']
    )

    error_count = sum(1 for msg in all_messages if msg.severity == ValidationSeverity.ERROR)
    warning_count = sum(1 for msg in all_messages if msg.severity == ValidationSeverity.WARNING)
    info_count = sum(1 for msg in all_messages if msg.severity == ValidationSeverity.INFO)

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Errors", error_count, delta=None if error_count == 0 else "Fix required")
    with col2:
        st.metric("Warnings", warning_count)
    with col3:
        st.metric("Info", info_count)

    # Overall status
    if error_count > 0:
        st.error("❌ Configuration has errors and cannot be exported")
    elif warning_count > 0:
        st.warning("⚠️ Configuration has warnings but can be exported")
    else:
        st.success("✅ Configuration is valid and ready to export")

    # Expandable details
    if all_messages:
        with st.expander("📋 Validation Details", expanded=error_count > 0):
            for section_name, messages in validation_results.items():
                if messages:
                    st.markdown(f"**{section_name.replace('_', ' ').title()}**")
                    for msg in messages:
                        if msg.severity == "error":
                            st.error(msg.message)
                        elif msg.severity == "warning":
                            st.warning(msg.message)
                        else:
                            st.info(msg.message)
                    st.divider()
```

---

### Step 5: Create Unit Tests (45 min)

**File:** `tests/test_validator.py`

```python
"""
Unit tests for configuration validation
"""

import pytest
from pathlib import Path

from src.utils import load_options, load_unit_costs
from src.utils.validator import HTAPConfigValidator, ValidationSeverity
from src.utils.cost_resolver import CostResolver


@pytest.fixture
def options_db():
    """Load real options database"""
    path = "C:/HTAP/HTAP-options.json"
    if not Path(path).exists():
        pytest.skip(f"Options file not found: {path}")
    return load_options(path)


@pytest.fixture
def costs_db():
    """Load real costs database"""
    path = "C:/HTAP/HTAPUnitCosts.json"
    if not Path(path).exists():
        pytest.skip(f"Costs file not found: {path}")
    return load_unit_costs(path)


@pytest.fixture
def cost_resolver(costs_db):
    """Create cost resolver"""
    return CostResolver(costs_db)


@pytest.fixture
def validator(options_db, cost_resolver):
    """Create validator"""
    return HTAPConfigValidator(options_db, cost_resolver)


class TestRunConfigValidation:
    """Test run configuration validation"""

    def test_empty_config(self, validator):
        """Test validation of empty configuration"""
        messages = validator.validate_run_config({})

        assert len(messages) > 0
        assert validator.has_errors(messages)

    def test_valid_config(self, validator):
        """Test validation of complete configuration"""
        config = {
            'archetypes': ['archetype1.h2k'],
            'location': 'Ottawa',
            'ruleset': 'as-found',
            'cost_source': 'LEEP-ON-Ottawa'
        }

        messages = validator.validate_run_config(config)

        # Should have no errors (may have info messages)
        assert not validator.has_errors(messages)

    def test_missing_archetypes(self, validator):
        """Test validation with missing archetypes"""
        config = {
            'archetypes': [],
            'location': 'Ottawa',
            'ruleset': 'as-found'
        }

        messages = validator.validate_run_config(config)

        assert validator.has_errors(messages)
        assert any('archetype' in msg.message.lower() for msg in messages)

    def test_many_archetypes_warning(self, validator):
        """Test warning for large number of archetypes"""
        config = {
            'archetypes': [f'arch{i}.h2k' for i in range(15)],
            'location': 'Ottawa',
            'ruleset': 'as-found'
        }

        messages = validator.validate_run_config(config)

        assert validator.has_warnings(messages)


class TestOptionsValidation:
    """Test selected options validation"""

    def test_valid_selection(self, validator, options_db):
        """Test validation of valid option selection"""
        # Get first category and first option
        cat_name = list(options_db.categories.keys())[0]
        category = options_db.categories[cat_name]
        choice_name = list(category.options.keys())[0]

        selected = {cat_name: choice_name}
        messages = validator.validate_selected_options(selected)

        # Should have no errors
        assert not validator.has_errors(messages)

    def test_invalid_category(self, validator):
        """Test validation with invalid category"""
        selected = {'Invalid-Category': 'some-choice'}
        messages = validator.validate_selected_options(selected)

        assert validator.has_errors(messages)

    def test_invalid_choice(self, validator, options_db):
        """Test validation with invalid choice in valid category"""
        cat_name = list(options_db.categories.keys())[0]
        selected = {cat_name: 'invalid-choice-name'}

        messages = validator.validate_selected_options(selected)

        assert validator.has_errors(messages)

    def test_costed_option_without_costs(self, validator, options_db):
        """Test warning for costed category with option lacking costs"""
        # Find a costed category
        for cat_name, category in options_db.categories.items():
            if category.costed:
                # Find option without costs
                for choice_name, choice in category.options.items():
                    if not choice.costs or not choice.costs.components:
                        selected = {cat_name: choice_name}
                        messages = validator.validate_selected_options(
                            selected,
                            'LEEP-ON-Ottawa'
                        )

                        # Should have warning about missing costs
                        assert validator.has_warnings(messages)
                        return

        pytest.skip("No costed category with cost-less option found")


class TestCategoryStatus:
    """Test category status checking"""

    def test_unselected_category_with_default(self, validator, options_db):
        """Test status of unselected category that has default"""
        # Find category with default
        for cat_name, category in options_db.categories.items():
            if hasattr(category, 'default') and category.default:
                icon, messages = validator.get_category_status(cat_name, None)

                assert icon == "⬜"
                assert any('default' in msg.message.lower() for msg in messages)
                return

        pytest.skip("No category with default found")

    def test_selected_category(self, validator, options_db):
        """Test status of validly selected category"""
        cat_name = list(options_db.categories.keys())[0]
        category = options_db.categories[cat_name]
        choice_name = list(category.options.keys())[0]

        icon, messages = validator.get_category_status(
            cat_name,
            choice_name,
            'LEEP-ON-Ottawa'
        )

        assert icon in ["✅", "⚠️"]  # Valid or warning, not error


class TestFullConfiguration:
    """Test full configuration validation"""

    def test_comprehensive_validation(self, validator):
        """Test full configuration validation"""
        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'Ottawa',
            'ruleset': 'as-found',
            'cost_source': 'LEEP-ON-Ottawa'
        }

        selected_options = {
            'Opt-ACH': 'ACH_1_5'
        }

        results = validator.validate_full_configuration(run_config, selected_options)

        assert 'run_config' in results
        assert 'options' in results
        assert 'completeness' in results
        assert 'summary' in results
```

---

## Acceptance Criteria

✅ **Validator class created** with comprehensive rules
✅ **Run config validation** checks required fields
✅ **Option validation** verifies choices exist
✅ **Cost validation** warns about missing cost data
✅ **Real-time feedback** in LEFT and MIDDLE panels
✅ **Validation summary** in RIGHT panel
✅ **Severity levels** (error, warning, info) work correctly
✅ **Tests pass** with real HTAP data

---

## Testing Checklist

```bash
# Run unit tests
pytest tests/test_validator.py -v -s

# Test in Streamlit app
streamlit run src/app.py

# Manual validation scenarios to test:
# 1. Empty configuration (should show errors)
# 2. Missing archetype (should show error)
# 3. Select costed option without costs (should show warning)
# 4. Valid complete configuration (should show success)
# 5. Category with default, no selection (should show info)
```

---

## Common Issues & Solutions

### Issue: Too many validation messages cluttering UI
**Solution:** Use expandable sections, show only errors/warnings by default

### Issue: Validation runs on every keystroke
**Solution:** Validation only runs when configuration changes (via session state)

### Issue: False warnings about missing costs
**Solution:** Only validate costs if category.costed is True

---

## Next Steps

After completing this task:
1. Test validation with various invalid configurations
2. Verify warnings display correctly in all three panels
3. Proceed to **Task 2.4: Multiple Option Selection**

---

## Time Tracking

- Validator module: 90 min
- LEFT panel updates: 30 min
- MIDDLE panel updates: 45 min
- Validation summary widget: 30 min
- Unit tests: 45 min
- **Total: ~3.5 hours**
