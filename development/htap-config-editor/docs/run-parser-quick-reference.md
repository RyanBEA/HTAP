# Run File Parser - Quick Reference

**Version:** 1.0
**Date:** 2025-10-09

---

## Import Statements

```python
# Parser and writer
from src.parsers import parse_run_file, write_run_file, RunFileParser, RunFileWriter

# Validation
from src.parsers import validate_run_configuration, ValidationError

# Models
from src.models import (
    RunConfiguration,
    RunParameters,
    RunScope,
    OptionUpgrade,
    RunMode
)
```

---

## Quick Start

### Read a Run File

```python
from src.parsers import parse_run_file

config = parse_run_file("path/to/file.run")
```

### Write a Run File

```python
from src.parsers import write_run_file

write_run_file(config, "output.run")
```

### Validate Configuration

```python
from src.parsers import validate_run_configuration

is_valid, errors = validate_run_configuration(config)
```

---

## Common Operations

### Access Configuration Data

```python
# Run parameters
print(config.parameters.run_mode)          # RunMode.PARAMETRIC
print(config.parameters.archetype_dir)     # "C:/HTAP/archetypes"
print(config.parameters.unit_costs_db)     # "C:/HTAP/HTAPUnitCosts.json"
print(config.parameters.options_file)      # "C:/HTAP/HTAP-options.json"

# Run scope
print(config.scope.archetypes)             # "*.H2K"
print(config.scope.locations)              # "NA"
print(config.scope.rulesets)               # "as-found"

# Upgrades
print(len(config.upgrades))                # Number of upgrades
print(config.list_upgrades())              # List of upgrade names
```

### Modify Upgrades

```python
# Add upgrade
config.add_upgrade("Opt-Windows", ["NA", "DoubleGlazed", "TripleGlazed"])

# Get upgrade
windows = config.get_upgrade("Opt-Windows")
print(windows.choices)  # ["NA", "DoubleGlazed", "TripleGlazed"]

# Remove upgrade
removed = config.remove_upgrade("Opt-ACH")
print(removed)  # True if existed, False if not
```

### Parse Lists from Scope

```python
# Get archetype list
archetypes = config.scope.get_archetype_list()
# Returns [] for "*.H2K", or list of files for comma-separated

# Get location list
locations = config.scope.get_location_list()
# Returns [] for "NA", or list of locations for comma-separated
```

---

## Creating New Configuration

### From Scratch

```python
from src.models import RunConfiguration, RunParameters, RunScope, RunMode

config = RunConfiguration(
    parameters=RunParameters(
        run_mode=RunMode.PARAMETRIC,
        archetype_dir="C:/HTAP/archetypes",
        unit_costs_db="C:/HTAP/HTAPUnitCosts.json",
        options_file="C:/HTAP/HTAP-options.json"
    ),
    scope=RunScope(
        archetypes="*.H2K",
        locations="OTTAWA, TORONTO",
        rulesets="as-found"
    ),
    upgrades={}
)

# Add upgrades
config.add_upgrade("Opt-Windows", ["NA", "DoubleGlazed"])
config.add_upgrade("Opt-ACH", ["NA", "1.5"])

# Save
write_run_file(config, "new.run")
```

### With Defaults

```python
from src.models import RunConfiguration, RunParameters, RunScope

# Use all defaults
config = RunConfiguration(
    parameters=RunParameters(),  # Uses default values
    scope=RunScope(),            # Uses default values
    upgrades={}
)
```

---

## Advanced Usage

### Parse from String

```python
from src.parsers import RunFileParser

content = """
RunParameters_START
  run-mode = parametric
  archetype-dir = C:/HTAP/archetypes
RunParameters_END

RunScope_START
  archetypes = *.H2K
  locations = NA
  rulesets = as-found
RunScope_END

Upgrades_START
  Opt-Windows = NA, DoubleGlazed
Upgrades_END
"""

parser = RunFileParser()
config = parser.parse_string(content)
```

### Generate String (Without File)

```python
from src.parsers import RunFileWriter

writer = RunFileWriter()
content = writer.generate_content(config, include_timestamp=True)
print(content)
```

### Error Handling

```python
from src.parsers import parse_run_file

try:
    config = parse_run_file("file.run")
except FileNotFoundError:
    print("File not found")
except ValueError as e:
    print(f"Parse error: {e}")
```

---

## Validation

### Basic Validation

```python
from src.parsers import validate_run_configuration

is_valid, errors = validate_run_configuration(config)

if not is_valid:
    print("Configuration has errors:")
    for error in errors:
        print(f"  {error}")
```

### Filter by Severity

```python
is_valid, errors = validate_run_configuration(config)

# Only show errors (not warnings or info)
critical_errors = [e for e in errors if e.severity == "error"]

# Only show warnings
warnings = [e for e in errors if e.severity == "warning"]

# Only show info
info_messages = [e for e in errors if e.severity == "info"]
```

### Validation Error Properties

```python
for error in errors:
    print(error.severity)  # "error", "warning", or "info"
    print(error.field)     # Field name (e.g., "archetype-dir")
    print(error.message)   # Human-readable message
    print(str(error))      # Formatted: "[ERROR] field: message"
```

---

## RunConfiguration Model

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `parameters` | `RunParameters` | Run parameters section |
| `scope` | `RunScope` | Run scope section |
| `upgrades` | `Dict[str, OptionUpgrade]` | Upgrade options |
| `comments` | `List[str]` | Header comments |

### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `add_upgrade()` | `option_type, choices` | `None` | Add/update upgrade |
| `remove_upgrade()` | `option_type` | `bool` | Remove upgrade |
| `get_upgrade()` | `option_type` | `Optional[OptionUpgrade]` | Get upgrade |
| `list_upgrades()` | - | `List[str]` | List upgrade names |

---

## RunParameters Model

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `run_mode` | `RunMode` | `PARAMETRIC` | Execution mode |
| `archetype_dir` | `str` | `C:/HTAP/archetypes` | Archetype directory |
| `unit_costs_db` | `str` | `C:/HTAP/HTAPUnitCosts.json` | Unit costs file |
| `options_file` | `str` | `C:/HTAP/HTAP-options.json` | Options file |

### RunMode Enum

```python
RunMode.PARAMETRIC  # "parametric"
RunMode.MESH        # "mesh"
RunMode.SAMPLE      # "sample"
RunMode.OPTIMIZE    # "optimize"
```

---

## RunScope Model

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `archetypes` | `str` | `*.H2K` | Archetype pattern |
| `locations` | `str` | `NA` | Location codes |
| `rulesets` | `str` | `as-found` | Ruleset name |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `get_archetype_list()` | `List[str]` | Parse archetypes to list |
| `get_location_list()` | `List[str]` | Parse locations to list |

---

## OptionUpgrade Model

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `option_type` | `str` | Option type (e.g., "Opt-Windows") |
| `choices` | `List[str]` | List of choices |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `to_run_format()` | `str` | Export to .run format |

### Example

```python
from src.models import OptionUpgrade

upgrade = OptionUpgrade(
    option_type="Opt-Windows",
    choices=["NA", "DoubleGlazed", "TripleGlazed"]
)

print(upgrade.to_run_format())
# Output: "   Opt-Windows              = NA, DoubleGlazed, TripleGlazed"
```

---

## Common Patterns

### Load, Modify, Save

```python
# Load
config = parse_run_file("input.run")

# Modify
config.add_upgrade("Opt-Heating-Cooling", ["NA", "ASHP"])
config.parameters.run_mode = RunMode.MESH

# Save
write_run_file(config, "output.run")
```

### Clone Configuration

```python
# Parse original
config1 = parse_run_file("original.run")

# Write to temp location
write_run_file(config1, "temp.run")

# Parse copy
config2 = parse_run_file("temp.run")
```

### Iterate Over Upgrades

```python
for opt_type, upgrade in config.upgrades.items():
    print(f"{opt_type}:")
    for choice in upgrade.choices:
        print(f"  - {choice}")
```

### Filter Upgrades

```python
# Get only upgrades with multiple choices
multi_choice = {
    opt_type: upgrade
    for opt_type, upgrade in config.upgrades.items()
    if len(upgrade.choices) > 1
}

# Get only upgrades that aren't just "NA"
active_upgrades = {
    opt_type: upgrade
    for opt_type, upgrade in config.upgrades.items()
    if upgrade.choices != ["NA"]
}
```

---

## Testing

### Run Parser Tests

```bash
# All parser tests
pytest tests/test_run_parser.py -v

# Specific test class
pytest tests/test_run_parser.py::TestRunFileParser -v

# Specific test
pytest tests/test_run_parser.py::TestRunFileParser::test_parse_real_file -v
```

### Run Demo

```bash
python demo_parser.py
```

---

## File Format Reference

### Structure

```
! Comments start with !
RunParameters_START
  key = value
RunParameters_END

RunScope_START
  key = value
RunScope_END

Upgrades_START
  Opt-CategoryName = choice1, choice2, choice3
Upgrades_END
```

### Example

```
! Definitions file for HTAP-PRM RUN

RunParameters_START
  run-mode                           = parametric
  archetype-dir                      = C:/HTAP/archetypes
  unit-costs-db                      = C:/HTAP/HTAPUnitCosts.json
  options-file                       = C:/HTAP/HTAP-options.json
RunParameters_END

RunScope_START
  archetypes                        = *.H2K
  locations                         = OTTAWA, TORONTO
  rulesets                          = as-found
RunScope_END

Upgrades_START
  Opt-Windows     = NA, DoubleGlazed, TripleGlazed
  Opt-ACH         = NA, 1.5, 2.5
  Opt-Heating-Cooling = NA, ASHP, CCASHP
Upgrades_END
```

---

## Troubleshooting

### Issue: Parse Error on Line X

**Solution:** Check that line has proper `key = value` format with equals sign.

### Issue: File Not Found

**Solution:** Use absolute paths, not relative. Windows paths use forward slashes in .run files.

### Issue: Validation Errors

**Solution:** Check that referenced files (archetype-dir, unit-costs-db, options-file) exist.

### Issue: Lost Comments After Roundtrip

**Expected:** Only header comments (before first section) are preserved. In-section comments are not kept.

### Issue: Different Formatting After Write

**Expected:** Writer uses standardized formatting (35-char field width, sorted upgrades). Content is preserved, formatting may differ.

---

## Performance Tips

- Parsing is fast (~5ms per file)
- Writing is fast (~3ms per file)
- Use `parse_string()` if content is already in memory
- Use `generate_content()` if you don't need to write to file
- Validation is quick but can be skipped if files are known to exist

---

## Related Files

- **Implementation:** `src/parsers/run_parser.py`
- **Models:** `src/models/run_config.py`
- **Tests:** `tests/test_run_parser.py`
- **Demo:** `demo_parser.py`
- **Complete Documentation:** `TASK-1.4-COMPLETE.md`

---

**Questions?** Check the comprehensive tests in `tests/test_run_parser.py` for more examples.
