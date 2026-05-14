# Task 3.2: Export Validation

**Duration:** 2-3 hours
**Phase:** 3 - Export & Polish
**Dependencies:** Task 2.3 (Validation), Task 3.1 (Export Run File)
**Completion Criteria:** Pre-export validation working, blocks invalid exports, clear error messages

---

## Objective

Implement comprehensive pre-export validation that prevents users from exporting invalid or incomplete configurations. Provide clear, actionable feedback about what needs to be fixed before export.

---

## What You'll Build

1. Export readiness checker
2. Configuration completeness validator
3. HTAP compatibility validator
4. Export blocker UI with fix suggestions
5. Validation report generator
6. Unit tests with edge cases

---

## Context: Export Validation Requirements

Before allowing export, validate:

1. **Configuration completeness:**
   - At least one archetype selected
   - Location specified
   - Ruleset specified

2. **Options validity:**
   - All selected options exist in options database
   - No conflicting options (if applicable)
   - Required categories have selections

3. **File format:**
   - Generated .run file passes format validation
   - All sections present and well-formed

4. **HTAP compatibility:**
   - Archetype files exist (if checking disk)
   - Options match HTAP-options.json structure
   - Cost source valid (if costs enabled)

---

## Step-by-Step Implementation

### Step 1: Create Export Validator (75 min)

**File:** `src/utils/export_validator.py`

```python
"""
Export validation for HTAP configurations
Ensures configurations are complete and valid before export
"""

from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path
from enum import Enum

from src.models.option import OptionsDatabase
from src.utils.validator import HTAPConfigValidator, ValidationMessage, ValidationSeverity
from src.utils.run_file_generator import RunFileGenerator


class ExportReadiness(str, Enum):
    """Export readiness status"""
    READY = "ready"
    WARNINGS = "warnings"
    BLOCKED = "blocked"


class ExportValidator:
    """
    Validates configurations before export
    """

    def __init__(
        self,
        options_db: OptionsDatabase,
        config_validator: HTAPConfigValidator
    ):
        """
        Initialize export validator

        Args:
            options_db: Loaded options database
            config_validator: Configuration validator from Task 2.3
        """
        self.options_db = options_db
        self.config_validator = config_validator

    def check_export_readiness(
        self,
        run_config: Dict,
        selected_options: Dict[str, Set[str]]
    ) -> Tuple[ExportReadiness, List[ValidationMessage]]:
        """
        Check if configuration is ready for export

        Args:
            run_config: Run configuration
            selected_options: Selected options

        Returns:
            Tuple of (readiness_status, list_of_messages)
        """
        all_messages = []

        # Run all validation checks
        config_messages = self._validate_run_config(run_config)
        options_messages = self._validate_options(selected_options)
        completeness_messages = self._validate_completeness(run_config, selected_options)
        format_messages = self._validate_export_format(run_config, selected_options)

        all_messages.extend(config_messages)
        all_messages.extend(options_messages)
        all_messages.extend(completeness_messages)
        all_messages.extend(format_messages)

        # Determine readiness
        has_errors = any(msg.severity == ValidationSeverity.ERROR for msg in all_messages)
        has_warnings = any(msg.severity == ValidationSeverity.WARNING for msg in all_messages)

        if has_errors:
            return ExportReadiness.BLOCKED, all_messages
        elif has_warnings:
            return ExportReadiness.WARNINGS, all_messages
        else:
            return ExportReadiness.READY, all_messages

    def _validate_run_config(self, run_config: Dict) -> List[ValidationMessage]:
        """Validate run configuration"""
        messages = []

        # Check archetypes
        archetypes = run_config.get('archetypes', [])
        if not archetypes:
            messages.append(ValidationMessage(
                ValidationSeverity.ERROR,
                "At least one archetype must be selected",
                field="archetypes"
            ))
        else:
            # Optionally check if archetype files exist
            archetype_dir = Path("C:/HTAP/archetypes")
            if archetype_dir.exists():
                for arch in archetypes:
                    arch_path = archetype_dir / arch
                    if not arch_path.exists():
                        messages.append(ValidationMessage(
                            ValidationSeverity.WARNING,
                            f"Archetype file not found: {arch}",
                            field="archetypes"
                        ))

        # Check location
        location = run_config.get('location')
        if not location:
            messages.append(ValidationMessage(
                ValidationSeverity.ERROR,
                "Location must be selected for export",
                field="location"
            ))

        # Check ruleset
        ruleset = run_config.get('ruleset')
        if not ruleset:
            messages.append(ValidationMessage(
                ValidationSeverity.WARNING,
                "No ruleset selected, will use 'as-found'",
                field="ruleset"
            ))

        return messages

    def _validate_options(self, selected_options: Dict[str, Set[str]]) -> List[ValidationMessage]:
        """Validate selected options"""
        messages = []

        if not selected_options:
            messages.append(ValidationMessage(
                ValidationSeverity.WARNING,
                "No options selected. Configuration will use defaults.",
                category="options"
            ))
            return messages

        for category, choices in selected_options.items():
            # Check category exists
            if category not in self.options_db.categories:
                messages.append(ValidationMessage(
                    ValidationSeverity.ERROR,
                    f"Unknown category: {category}",
                    category=category
                ))
                continue

            cat_obj = self.options_db.categories[category]

            # Check all choices exist
            for choice in choices:
                if choice not in cat_obj.options:
                    messages.append(ValidationMessage(
                        ValidationSeverity.ERROR,
                        f"Unknown choice '{choice}' in category '{category}'",
                        category=category
                    ))

        return messages

    def _validate_completeness(
        self,
        run_config: Dict,
        selected_options: Dict[str, Set[str]]
    ) -> List[ValidationMessage]:
        """Validate configuration completeness"""
        messages = []

        # Important categories that should have selections
        important_categories = {
            "Opt-Location": "Location defines weather data",
            "Opt-Archetype": "Archetype defines building geometry",
        }

        for cat_name, reason in important_categories.items():
            if cat_name in self.options_db.categories:
                if cat_name not in selected_options or not selected_options[cat_name]:
                    messages.append(ValidationMessage(
                        ValidationSeverity.INFO,
                        f"No selection for '{cat_name}'. {reason}",
                        category=cat_name
                    ))

        # Check if configuration will generate runs
        total_combos = self._count_combinations(run_config, selected_options)

        if total_combos == 0:
            messages.append(ValidationMessage(
                ValidationSeverity.ERROR,
                "Configuration will generate 0 simulation runs",
                category="completeness"
            ))
        elif total_combos > 1000:
            messages.append(ValidationMessage(
                ValidationSeverity.WARNING,
                f"Configuration will generate {total_combos} runs. This may take hours or days.",
                category="completeness"
            ))
        elif total_combos > 100:
            messages.append(ValidationMessage(
                ValidationSeverity.INFO,
                f"Configuration will generate {total_combos} runs. Estimated time: {total_combos * 2} minutes.",
                category="completeness"
            ))

        return messages

    def _validate_export_format(
        self,
        run_config: Dict,
        selected_options: Dict[str, Set[str]]
    ) -> List[ValidationMessage]:
        """Validate that export format will be valid"""
        messages = []

        try:
            # Try generating the file
            generator = RunFileGenerator()
            content = generator.generate_run_file(run_config, selected_options)

            # Validate format
            is_valid, errors = generator.validate_format(content)

            if not is_valid:
                for error in errors:
                    messages.append(ValidationMessage(
                        ValidationSeverity.ERROR,
                        f"Export format error: {error}",
                        category="format"
                    ))
        except Exception as e:
            messages.append(ValidationMessage(
                ValidationSeverity.ERROR,
                f"Error generating export file: {str(e)}",
                category="format"
            ))

        return messages

    def _count_combinations(
        self,
        run_config: Dict,
        selected_options: Dict[str, Set[str]]
    ) -> int:
        """Count total number of simulation combinations"""
        total = 1

        # Multiply by archetypes
        archetypes = run_config.get('archetypes', [])
        if archetypes:
            total *= len(archetypes)

        # Multiply by options in each category
        for choices in selected_options.values():
            if choices:
                total *= len(choices)

        return total

    def generate_validation_report(
        self,
        run_config: Dict,
        selected_options: Dict[str, Set[str]]
    ) -> str:
        """
        Generate human-readable validation report

        Args:
            run_config: Run configuration
            selected_options: Selected options

        Returns:
            Markdown-formatted validation report
        """
        readiness, messages = self.check_export_readiness(run_config, selected_options)

        lines = []
        lines.append("# Export Validation Report")
        lines.append("")

        # Overall status
        if readiness == ExportReadiness.READY:
            lines.append("## ✅ Status: Ready to Export")
        elif readiness == ExportReadiness.WARNINGS:
            lines.append("## ⚠️ Status: Ready with Warnings")
        else:
            lines.append("## ❌ Status: Cannot Export")

        lines.append("")

        # Configuration summary
        lines.append("## Configuration Summary")
        lines.append("")
        lines.append(f"- **Archetypes:** {len(run_config.get('archetypes', []))}")
        lines.append(f"- **Location:** {run_config.get('location', 'Not set')}")
        lines.append(f"- **Ruleset:** {run_config.get('ruleset', 'Not set')}")
        lines.append(f"- **Selected Categories:** {len(selected_options)}")
        lines.append(f"- **Total Combinations:** {self._count_combinations(run_config, selected_options)}")
        lines.append("")

        # Messages by severity
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR]
        warnings = [m for m in messages if m.severity == ValidationSeverity.WARNING]
        infos = [m for m in messages if m.severity == ValidationSeverity.INFO]

        if errors:
            lines.append("## ❌ Errors (must fix before export)")
            lines.append("")
            for msg in errors:
                context = f" [{msg.category or msg.field}]" if msg.category or msg.field else ""
                lines.append(f"- {msg.message}{context}")
            lines.append("")

        if warnings:
            lines.append("## ⚠️ Warnings (recommended to review)")
            lines.append("")
            for msg in warnings:
                context = f" [{msg.category or msg.field}]" if msg.category or msg.field else ""
                lines.append(f"- {msg.message}{context}")
            lines.append("")

        if infos:
            lines.append("## ℹ️ Information")
            lines.append("")
            for msg in infos:
                context = f" [{msg.category or msg.field}]" if msg.category or msg.field else ""
                lines.append(f"- {msg.message}{context}")
            lines.append("")

        return "\n".join(lines)
```

---

### Step 2: Update Export Widget with Validation (45 min)

**File:** `src/ui/export_widget.py`

Update to show validation status:

```python
def render_export_widget():
    """
    Render export widget with validation
    """
    st.subheader("💾 Export Configuration")

    # Get configuration
    run_config = st.session_state.get('run_config', {})
    selected_options = st.session_state.get('selected_options', {})

    # Initialize export validator
    if 'export_validator' not in st.session_state:
        from src.utils.export_validator import ExportValidator

        validator = st.session_state.get('validator')
        if validator:
            st.session_state.export_validator = ExportValidator(
                st.session_state.options_db,
                validator
            )

    export_validator = st.session_state.get('export_validator')

    # Check export readiness
    if export_validator:
        from src.utils.export_validator import ExportReadiness

        readiness, messages = export_validator.check_export_readiness(
            run_config,
            selected_options
        )

        # Display readiness status
        if readiness == ExportReadiness.READY:
            st.success("✅ Configuration is ready to export")
        elif readiness == ExportReadiness.WARNINGS:
            st.warning("⚠️ Configuration has warnings but can be exported")
        else:
            st.error("❌ Configuration has errors and cannot be exported")

        # Show validation messages
        if messages:
            with st.expander("📋 Validation Details", expanded=(readiness == ExportReadiness.BLOCKED)):
                errors = [m for m in messages if m.severity.value == "error"]
                warnings = [m for m in messages if m.severity.value == "warning"]
                infos = [m for m in messages if m.severity.value == "info"]

                if errors:
                    st.markdown("**❌ Errors (must fix):**")
                    for msg in errors:
                        st.error(msg.message)

                if warnings:
                    st.markdown("**⚠️ Warnings:**")
                    for msg in warnings:
                        st.warning(msg.message)

                if infos:
                    st.markdown("**ℹ️ Information:**")
                    for msg in infos:
                        st.info(msg.message)

        st.divider()

        # Show summary
        total_combos = export_validator._count_combinations(run_config, selected_options)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Archetypes", len(run_config.get('archetypes', [])))
            st.metric("Categories", len(selected_options))
        with col2:
            st.metric("Total Runs", total_combos)

        st.divider()

    # ... rest of export UI (template selector, preview, download button) ...

    # Disable export button if blocked
    export_disabled = readiness == ExportReadiness.BLOCKED if export_validator else True

    st.download_button(
        label="⬇️ Download .run file",
        data=run_content,
        file_name=filename,
        mime="text/plain",
        use_container_width=True,
        disabled=export_disabled,
        help="Export is disabled due to validation errors" if export_disabled else None
    )
```

---

### Step 3: Create Validation Report Generator (30 min)

**File:** `src/ui/validation_report_widget.py`

```python
"""
Validation report display widget
"""

import streamlit as st


def render_validation_report():
    """
    Render detailed validation report
    """
    st.subheader("📊 Validation Report")

    export_validator = st.session_state.get('export_validator')
    if not export_validator:
        st.info("Validation not available")
        return

    run_config = st.session_state.get('run_config', {})
    selected_options = st.session_state.get('selected_options', {})

    # Generate report
    report = export_validator.generate_validation_report(
        run_config,
        selected_options
    )

    # Display report
    st.markdown(report)

    # Download report button
    st.download_button(
        label="📄 Download Validation Report",
        data=report,
        file_name="validation_report.md",
        mime="text/markdown",
        use_container_width=True
    )
```

---

### Step 4: Create Unit Tests (30 min)

**File:** `tests/test_export_validator.py`

```python
"""
Unit tests for export validation
"""

import pytest
from pathlib import Path

from src.utils import load_options
from src.utils.export_validator import ExportValidator, ExportReadiness
from src.utils.validator import HTAPConfigValidator


@pytest.fixture
def options_db():
    """Load real options database"""
    path = "C:/HTAP/HTAP-options.json"
    if not Path(path).exists():
        pytest.skip(f"Options file not found: {path}")
    return load_options(path)


@pytest.fixture
def config_validator(options_db):
    """Create config validator"""
    return HTAPConfigValidator(options_db)


@pytest.fixture
def export_validator(options_db, config_validator):
    """Create export validator"""
    return ExportValidator(options_db, config_validator)


class TestExportReadiness:
    """Test export readiness checking"""

    def test_empty_config_blocked(self, export_validator):
        """Test that empty config is blocked"""
        run_config = {}
        selected_options = {}

        readiness, messages = export_validator.check_export_readiness(
            run_config,
            selected_options
        )

        assert readiness == ExportReadiness.BLOCKED
        assert len(messages) > 0

    def test_valid_config_ready(self, export_validator, options_db):
        """Test that valid config is ready"""
        # Get first category and choice
        cat_name = list(options_db.categories.keys())[0]
        category = options_db.categories[cat_name]
        choice_name = list(category.options.keys())[0]

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }

        selected_options = {
            cat_name: {choice_name}
        }

        readiness, messages = export_validator.check_export_readiness(
            run_config,
            selected_options
        )

        # Should be ready or have only warnings
        assert readiness in [ExportReadiness.READY, ExportReadiness.WARNINGS]

    def test_missing_archetypes_blocked(self, export_validator):
        """Test that missing archetypes blocks export"""
        run_config = {
            'archetypes': [],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }

        selected_options = {}

        readiness, messages = export_validator.check_export_readiness(
            run_config,
            selected_options
        )

        assert readiness == ExportReadiness.BLOCKED

    def test_invalid_option_blocked(self, export_validator):
        """Test that invalid option blocks export"""
        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }

        selected_options = {
            'Invalid-Category': {'Invalid-Choice'}
        }

        readiness, messages = export_validator.check_export_readiness(
            run_config,
            selected_options
        )

        assert readiness == ExportReadiness.BLOCKED

    def test_large_combination_warning(self, export_validator, options_db):
        """Test warning for large number of combinations"""
        # Get multiple options to create large combo
        run_config = {
            'archetypes': [f'arch{i}.h2k' for i in range(1, 11)],  # 10 archetypes
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }

        # Find categories with multiple options
        selected_options = {}
        for cat_name, category in list(options_db.categories.items())[:5]:
            choices = set(list(category.options.keys())[:10])  # 10 choices each
            selected_options[cat_name] = choices

        readiness, messages = export_validator.check_export_readiness(
            run_config,
            selected_options
        )

        # Should have warning about large run
        warnings = [m for m in messages if m.severity.value == "warning"]
        assert any("runs" in m.message.lower() for m in warnings)


class TestValidationReport:
    """Test validation report generation"""

    def test_generate_report(self, export_validator):
        """Test generating validation report"""
        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }

        selected_options = {}

        report = export_validator.generate_validation_report(
            run_config,
            selected_options
        )

        assert "Export Validation Report" in report
        assert "Configuration Summary" in report
        assert "Status:" in report

    def test_report_shows_errors(self, export_validator):
        """Test that report shows errors"""
        run_config = {}  # Invalid - no archetypes
        selected_options = {}

        report = export_validator.generate_validation_report(
            run_config,
            selected_options
        )

        assert "❌" in report
        assert "Errors" in report or "Cannot Export" in report
```

---

## Acceptance Criteria

✅ **Export validator created** with comprehensive checks
✅ **Export blocked** when configuration has errors
✅ **Clear error messages** guide user to fix issues
✅ **Warnings allowed** but user can still export
✅ **Validation report** generated in markdown
✅ **Export button disabled** when validation fails
✅ **Tests pass** for all validation scenarios

---

## Testing Checklist

```bash
# Run unit tests
pytest tests/test_export_validator.py -v -s

# Manual testing in Streamlit:
# 1. Try exporting with no archetypes (should be blocked)
# 2. Try exporting with invalid option (should be blocked)
# 3. Export with warnings (should show warning but allow)
# 4. Export valid config (should show ready status)
# 5. Download validation report
```

---

## Common Issues & Solutions

### Issue: Validation too strict, blocks valid configs
**Solution:** Distinguish between errors (blockers) and warnings (allowed)

### Issue: Validation messages unclear
**Solution:** Provide specific, actionable messages with category/field context

### Issue: False positives on archetype file checks
**Solution:** Make file existence check optional (warning not error)

---

## Next Steps

After completing this task:
1. Test validation with various invalid configurations
2. Verify export blocking works correctly
3. Proceed to **Task 3.3: Cost Summary Report**

---

## Time Tracking

- Export validator: 75 min
- Export widget updates: 45 min
- Validation report widget: 30 min
- Unit tests: 30 min
- **Total: ~3 hours**
