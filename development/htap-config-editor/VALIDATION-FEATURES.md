# HTAP Configuration Validation System

**Status:** ✅ Fully Implemented and Tested
**Version:** 1.0
**Date:** October 9, 2025

---

## Overview

The HTAP Configuration Validation System provides comprehensive, real-time validation of user configurations across all three panels of the Configuration Editor. It uses a three-tier severity system (ERROR, WARNING, INFO) to provide clear, actionable feedback.

---

## Validation Severity Levels

### ❌ ERROR (Blocking)
**Impact:** Configuration cannot be exported
**Examples:**
- Missing required archetypes
- Missing required location
- Unknown category selection
- Unknown choice in category
- Too many combinations (>500 runs)

### ⚠️ WARNING (Non-blocking)
**Impact:** Configuration can be exported but may have issues
**Examples:**
- Missing ruleset (defaults to 'as-found')
- Missing cost source (costs won't be calculated)
- Many archetypes selected (>10)
- Large combination count (>100 runs)
- Costed option without cost data
- Missing cost components

### ℹ️ INFO (Informational)
**Impact:** No negative impact, informational only
**Examples:**
- Using default value for unselected category
- Combination count summary
- Configuration statistics

---

## Validation Rules

### Run Configuration (LEFT Panel)

| Rule | Severity | Condition | Message |
|------|----------|-----------|---------|
| Archetypes required | ERROR | `len(archetypes) == 0` | "At least one archetype must be selected" |
| Too many archetypes | WARNING | `len(archetypes) > 10` | "N archetypes selected. Large runs may take significant time." |
| Location required | ERROR | `location is None` | "Location must be selected" |
| Ruleset optional | WARNING | `ruleset is None` | "No ruleset selected, using 'as-found'" |
| Cost source optional | WARNING | `cost_source is None` | "No cost source selected, costs will not be calculated" |

### Option Selection (MIDDLE Panel)

| Rule | Severity | Condition | Message |
|------|----------|-----------|---------|
| Category exists | ERROR | `category not in db` | "Unknown category 'X'" |
| Choice exists | ERROR | `choice not in category` | "Unknown choice 'X' in category 'Y'" |
| Costed option has data | WARNING | `costed && no costs` | "Option 'X' has no cost data (category is marked as costed)" |
| Cost components valid | WARNING | `missing components` | "Missing cost components: A, B, C..." |

### Configuration Completeness

| Category | Severity | Condition | Message |
|----------|----------|-----------|---------|
| Opt-Location | INFO/WARNING | Not selected | "No selection, will use default" / "No selection" |
| Opt-Archetype | INFO/WARNING | Not selected | "No selection, will use default" / "No selection" |
| Opt-Heating-Cooling | INFO/WARNING | Not selected | "No selection, will use default" / "No selection" |
| Opt-DHWSystem | INFO/WARNING | Not selected | "No selection, will use default" / "No selection" |
| Opt-VentSystem | INFO/WARNING | Not selected | "No selection, will use default" / "No selection" |

### Combination Count

| Rule | Severity | Condition | Message |
|------|----------|-----------|---------|
| Normal size | INFO | `count ≤ 100` | "Configuration will generate N simulation runs" |
| Large size | WARNING | `100 < count ≤ 500` | "Configuration will generate N runs. Large runs may take significant time." |
| Too large | ERROR | `count > 500` | "Configuration will generate N runs. This is too large (max 500 recommended)." |

---

## Category Status Indicators

Each category displays a visual status indicator:

| Icon | Status | Description |
|------|--------|-------------|
| ✅ | Valid | Option is selected and has no issues |
| ⚠️ | Warning | Option is selected but has warnings (e.g., missing costs) |
| ❌ | Error | Option is selected but invalid |
| ⬜ | Not Selected | No option selected for this category |

---

## Panel Integration

### LEFT Panel: Run Configuration Status

**Location:** Below cost source selector

**Features:**
- Section header: "⚠️ Configuration Status"
- Real-time validation on every change
- Color-coded message display
- Overall status indicator

**Example Output:**
```
⚠️ Configuration Status

❌ At least one archetype must be selected
❌ Location must be selected
⚠️ No ruleset selected, using 'as-found'

❌ Configuration has errors that must be fixed
```

---

### MIDDLE Panel: Option Status

**Location:** In each option card

**Features:**
- Status icon next to category name
- Validation message counts for selected options
- 4-column layout: [Option | Cost | Validation | Details]

**Example Output:**
```
Option Card:
  ✅ 📁 ACH
  $5,000
  [view button]

Option Card (with warnings):
  ⚠️ 📁 Windows
  $15,000
  ⚠️ 2  [view button]
```

---

### RIGHT Panel: Validation Summary

**Location:** Top of panel, above option details

**Features:**
- Metrics showing error/warning/info counts
- Overall configuration status
- Expandable validation details (auto-expands on errors)
- Organized by validation type

**Example Output:**
```
✓ Validation Summary

Errors    Warnings    Info
  0          2         3

⚠️ Configuration has warnings but can be exported

📋 Validation Details ▼
  Options
    ⚠️ Option 'ACH_1_5' has no cost data

  Completeness
    ℹ️ No selection for 'Opt-Heating-Cooling', will use default: 'BASEBOARD'
    ℹ️ No selection for 'Opt-DHWSystem', will use default: 'DHW_elec'

  Summary
    ℹ️ Configuration will generate 1 simulation runs
```

---

## API Reference

### HTAPConfigValidator

```python
from src.utils import HTAPConfigValidator, ValidationSeverity

validator = HTAPConfigValidator(options_db, cost_resolver)
```

**Methods:**

#### validate_run_config(run_config: Dict) → List[ValidationMessage]
Validates run configuration from LEFT panel.

**Parameters:**
- `run_config`: Dict with keys `archetypes`, `location`, `ruleset`, `cost_source`

**Returns:**
- List of ValidationMessage objects

**Example:**
```python
config = {
    'archetypes': ['test.h2k'],
    'location': 'Ottawa',
    'ruleset': 'as-found',
    'cost_source': 'LEEP-ON-Ottawa'
}
messages = validator.validate_run_config(config)
```

---

#### validate_selected_options(selected_options: Dict, cost_source: str) → List[ValidationMessage]
Validates selected options from MIDDLE panel.

**Parameters:**
- `selected_options`: Dict mapping category_name → choice_name
- `cost_source`: Cost source for cost validation (optional)

**Returns:**
- List of ValidationMessage objects

**Example:**
```python
selections = {
    'Opt-ACH': 'ACH_1_5',
    'Opt-Windows': 'NC_9_36'
}
messages = validator.validate_selected_options(selections, 'LEEP-ON-Ottawa')
```

---

#### get_category_status(category: str, choice: str, cost_source: str) → Tuple[str, List[ValidationMessage]]
Gets status indicator and messages for a specific category.

**Parameters:**
- `category`: Category name (e.g., 'Opt-ACH')
- `choice`: Selected choice name (or None if not selected)
- `cost_source`: Cost source for cost validation (optional)

**Returns:**
- Tuple of (status_icon, messages)
- status_icon: "✅", "⚠️", "❌", or "⬜"

**Example:**
```python
icon, messages = validator.get_category_status('Opt-ACH', 'ACH_1_5', 'LEEP-ON-Ottawa')
# Returns: ("✅", [])
```

---

#### validate_full_configuration(run_config: Dict, selected_options: Dict) → Dict
Comprehensive validation of entire configuration.

**Parameters:**
- `run_config`: Run configuration dict
- `selected_options`: Selected options dict

**Returns:**
- Dict with keys: `run_config`, `options`, `completeness`, `summary`
- Each value is a list of ValidationMessage objects

**Example:**
```python
results = validator.validate_full_configuration(config, selections)
# Returns:
# {
#   'run_config': [...],
#   'options': [...],
#   'completeness': [...],
#   'summary': [...]
# }
```

---

#### has_errors(messages: List[ValidationMessage]) → bool
Check if any messages are errors.

**Example:**
```python
if validator.has_errors(messages):
    print("Configuration has errors")
```

---

#### has_warnings(messages: List[ValidationMessage]) → bool
Check if any messages are warnings.

**Example:**
```python
if validator.has_warnings(messages):
    print("Configuration has warnings")
```

---

### ValidationMessage

```python
from src.utils import ValidationMessage, ValidationSeverity

msg = ValidationMessage(
    severity=ValidationSeverity.ERROR,
    message="At least one archetype must be selected",
    category=None,
    field="archetypes"
)
```

**Attributes:**
- `severity`: ValidationSeverity enum (ERROR, WARNING, INFO)
- `message`: Human-readable message text
- `category`: Optional category name (e.g., 'Opt-ACH')
- `field`: Optional field name (e.g., 'archetypes')

---

## Testing

### Test Coverage

**29 tests across 6 test classes:**

1. **TestRunConfigValidation (7 tests)**
   - Empty configuration
   - Valid configuration
   - Missing archetypes
   - Missing location
   - Many archetypes warning
   - Missing ruleset warning
   - Missing cost source warning

2. **TestOptionsValidation (5 tests)**
   - Valid selection
   - Invalid category
   - Invalid choice
   - Costed option without costs
   - Multiple selections

3. **TestCategoryStatus (5 tests)**
   - Unselected with/without default
   - Selected category
   - Invalid category name
   - Invalid choice in category

4. **TestConfigurationCompleteness (3 tests)**
   - Empty selections
   - Partial selections
   - Important categories with defaults

5. **TestFullConfiguration (5 tests)**
   - Comprehensive validation
   - Validation with errors
   - Combination count info/warning/error

6. **TestHelperMethods (4 tests)**
   - has_errors()
   - has_warnings()
   - ValidationMessage repr/equality

**Test Results:** 28 passed, 1 skipped (0.70s)

---

## Usage Examples

### Example 1: Basic Validation

```python
from src.utils import load_options, HTAPConfigValidator

options_db = load_options('C:/HTAP/HTAP-options.json')
validator = HTAPConfigValidator(options_db)

config = {
    'archetypes': [],  # Error: empty
    'location': None   # Error: missing
}

messages = validator.validate_run_config(config)
for msg in messages:
    print(f"{msg.severity.value.upper()}: {msg.message}")

# Output:
# ERROR: At least one archetype must be selected
# ERROR: Location must be selected
```

### Example 2: Category Status

```python
icon, messages = validator.get_category_status(
    'Opt-ACH',
    'ACH_1_5',
    'LEEP-ON-Ottawa'
)

print(f"Status: {icon}")
# Output: Status: ✅ or ⚠️ or ❌
```

### Example 3: Full Validation

```python
config = {
    'archetypes': ['test.h2k'],
    'location': 'Ottawa',
    'ruleset': 'as-found',
    'cost_source': 'LEEP-ON-Ottawa'
}

selections = {
    'Opt-ACH': 'ACH_1_5'
}

results = validator.validate_full_configuration(config, selections)

# Count messages by severity
all_msgs = sum(results.values(), [])
errors = sum(1 for m in all_msgs if m.severity == ValidationSeverity.ERROR)
warnings = sum(1 for m in all_msgs if m.severity == ValidationSeverity.WARNING)
infos = sum(1 for m in all_msgs if m.severity == ValidationSeverity.INFO)

print(f"Errors: {errors}, Warnings: {warnings}, Info: {infos}")
```

---

## Performance

**Validation Speed:**
- Run config validation: <1ms
- Option validation: <5ms (per 100 options)
- Category status: <1ms
- Full configuration: <10ms
- All tests: 700ms

**Optimization:**
- O(1) lookups via dictionary keys
- Minimal redundant checks
- Cached cost lookups (via CostResolver)
- Lazy evaluation (only validates on change)

---

## Future Enhancements

**Potential improvements:**
1. Custom validation rules (user-defined)
2. Validation profiles (different rule sets)
3. Validation history tracking
4. Export validation report (PDF/HTML)
5. Batch validation (multiple configs)
6. Async validation (for large datasets)
7. Validation rule priorities
8. Auto-fix suggestions

---

## Changelog

### Version 1.0 (October 9, 2025)
- ✅ Initial implementation
- ✅ Three severity levels (ERROR, WARNING, INFO)
- ✅ Run config validation
- ✅ Option selection validation
- ✅ Category status indicators
- ✅ Configuration completeness checking
- ✅ Combination count warnings
- ✅ Cost data validation
- ✅ Integration with all 3 panels
- ✅ Comprehensive test suite (29 tests)

---

## Support

**Documentation:** See TASK-2.3-COMPLETION-REPORT.md
**Tests:** Run `pytest tests/test_validator.py -v`
**Demo:** Run `python demo_validation.py`
**Issues:** Report via project issue tracker

---

**Maintained by:** HTAP Development Team
**Last Updated:** October 9, 2025
