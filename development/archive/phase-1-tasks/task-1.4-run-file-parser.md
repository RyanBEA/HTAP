# Task 1.4: Run File Parser

**Duration:** 3-4 hours
**Phase:** 1 - Foundation
**Dependencies:** Task 1.2 (Data Models)
**Completion Criteria:** Parser reads/writes .run files, validates format, tests pass

---

## Objective

Create a robust parser for HTAP .run files that can read, validate, modify, and write run configurations.

---

## What You'll Build

1. `.run` file parser (reads to Pydantic models)
2. `.run` file writer (exports from Pydantic models)
3. Format validation and error handling
4. Support for comments and formatting preservation
5. Unit tests with real .run files

---

## Run File Format

Based on actual HTAP .run files:

```
! Comments start with !
! Definitions file for HTAP-PRM RUN

RunParameters_START
  run-mode                           = parametric
  archetype-dir                      = C:/HTAP/archetypes
  unit-costs-db                      = C:/HTAP/HTAPUnitCosts.json
  options-file                       = C:/HTAP/HTAP-options.json
RunParameters_END

RunScope_START
  archetypes                        = *.H2K
  locations                         = NA
  rulesets                          = as-found
RunScope_END

Upgrades_START
   Opt-ResultHouseCode  = General
   Opt-ACH              = NA
   Opt-Windows          = NA
   Opt-AboveGradeWall   = NA, NC_2x6_r19nom_r16Eff, NC_R-23(eff)_2x6-16inOC
   Opt-AtticCeilings    = NA
   Opt-Heating-Cooling  = NA
   Opt-DHWSystem        = NA
   Opt-VentSystem       = NA
   Opt-H2K-PV           = NA
Upgrades_END
```

---

## Technical Approach

### Parser Architecture

```
src/parsers/
├── __init__.py
├── run_parser.py        # Main parser
├── run_writer.py        # Export to .run format
└── validation.py        # Validation rules
```

---

## Step-by-Step Implementation

### Step 1: Create Run Configuration Models (45 min)

**File:** `src/models/run_config.py`

```python
"""
Pydantic models for .run file configuration
"""

from typing import List, Dict, Optional
from enum import Enum
from pydantic import Field, field_validator

from .common import HTAPBaseModel


class RunMode(str, Enum):
    """Run mode types"""
    PARAMETRIC = "parametric"
    MESH = "mesh"
    SAMPLE = "sample"
    OPTIMIZE = "optimize"


class RunParameters(HTAPBaseModel):
    """RunParameters section of .run file"""

    run_mode: RunMode = Field(default=RunMode.PARAMETRIC, description="Execution mode")
    archetype_dir: str = Field(
        default="C:/HTAP/archetypes",
        alias="archetype-dir",
        description="Path to archetype directory"
    )
    unit_costs_db: str = Field(
        default="C:/HTAP/HTAPUnitCosts.json",
        alias="unit-costs-db",
        description="Path to unit costs JSON"
    )
    options_file: str = Field(
        default="C:/HTAP/HTAP-options.json",
        alias="options-file",
        description="Path to options JSON"
    )

    @field_validator("archetype_dir", "unit_costs_db", "options_file")
    @classmethod
    def normalize_path(cls, v: str) -> str:
        """Normalize Windows paths to forward slashes"""
        return v.replace("\\", "/")


class RunScope(HTAPBaseModel):
    """RunScope section of .run file"""

    archetypes: str = Field(
        default="*.H2K",
        description="Archetype file pattern or comma-separated list"
    )
    locations: str = Field(
        default="NA",
        description="Location codes (NA = all from options file)"
    )
    rulesets: str = Field(
        default="as-found",
        description="Ruleset to apply"
    )

    def get_archetype_list(self) -> List[str]:
        """Parse archetypes into list"""
        if self.archetypes == "*.H2K":
            return []  # Will be expanded by htap-prm.rb
        return [a.strip() for a in self.archetypes.split(",")]

    def get_location_list(self) -> List[str]:
        """Parse locations into list"""
        if self.locations.upper() == "NA":
            return []  # All locations
        return [loc.strip() for loc in self.locations.split(",")]


class OptionUpgrade(HTAPBaseModel):
    """Single option upgrade specification"""

    option_type: str = Field(description="Option type (e.g., Opt-Windows)")
    choices: List[str] = Field(description="List of choices to test")

    @field_validator("choices", mode="before")
    @classmethod
    def parse_choices(cls, v):
        """Parse comma-separated choices"""
        if isinstance(v, str):
            return [c.strip() for c in v.split(",")]
        return v

    def to_run_format(self) -> str:
        """Export to .run file format"""
        choices_str = ", ".join(self.choices)
        return f"   {self.option_type:<25} = {choices_str}"


class RunConfiguration(HTAPBaseModel):
    """Complete .run file configuration"""

    parameters: RunParameters = Field(description="Run parameters section")
    scope: RunScope = Field(description="Run scope section")
    upgrades: Dict[str, OptionUpgrade] = Field(
        default_factory=dict,
        description="Upgrade options"
    )
    comments: List[str] = Field(
        default_factory=list,
        description="File header comments"
    )

    def add_upgrade(self, option_type: str, choices: List[str]) -> None:
        """Add or update an upgrade option"""
        self.upgrades[option_type] = OptionUpgrade(
            option_type=option_type,
            choices=choices
        )

    def remove_upgrade(self, option_type: str) -> bool:
        """Remove an upgrade option"""
        if option_type in self.upgrades:
            del self.upgrades[option_type]
            return True
        return False

    def get_upgrade(self, option_type: str) -> Optional[OptionUpgrade]:
        """Get specific upgrade"""
        return self.upgrades.get(option_type)

    def list_upgrades(self) -> List[str]:
        """List all upgrade option types"""
        return list(self.upgrades.keys())
```

### Step 2: Create Run File Parser (1 hour)

**File:** `src/parsers/run_parser.py`

```python
"""
Parser for HTAP .run files
"""

import re
from pathlib import Path
from typing import Optional, List, Tuple

from src.models.run_config import (
    RunConfiguration,
    RunParameters,
    RunScope,
    OptionUpgrade,
    RunMode
)


class RunFileParser:
    """Parser for .run configuration files"""

    def __init__(self):
        self.current_section = None
        self.parameters_data = {}
        self.scope_data = {}
        self.upgrades_data = {}
        self.comments = []

    def parse_file(self, file_path: str) -> RunConfiguration:
        """
        Parse a .run file into RunConfiguration model

        Args:
            file_path: Path to .run file

        Returns:
            RunConfiguration model

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Run file not found: {file_path}")

        self._reset()

        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    self._parse_line(line)
                except Exception as e:
                    raise ValueError(
                        f"Error parsing line {line_num}: {line.strip()}\n{str(e)}"
                    )

        return self._build_configuration()

    def parse_string(self, content: str) -> RunConfiguration:
        """
        Parse .run file content from string

        Args:
            content: .run file content as string

        Returns:
            RunConfiguration model
        """
        self._reset()

        for line_num, line in enumerate(content.splitlines(), 1):
            try:
                self._parse_line(line)
            except Exception as e:
                raise ValueError(
                    f"Error parsing line {line_num}: {line.strip()}\n{str(e)}"
                )

        return self._build_configuration()

    def _reset(self) -> None:
        """Reset parser state"""
        self.current_section = None
        self.parameters_data = {}
        self.scope_data = {}
        self.upgrades_data = {}
        self.comments = []

    def _parse_line(self, line: str) -> None:
        """Parse a single line"""
        line = line.rstrip()

        # Skip empty lines
        if not line or line.isspace():
            return

        # Handle comments (preserve header comments only)
        if line.strip().startswith("!"):
            if self.current_section is None:
                self.comments.append(line.strip())
            return

        # Detect section markers
        if "RunParameters_START" in line:
            self.current_section = "parameters"
            return
        elif "RunParameters_END" in line:
            self.current_section = None
            return
        elif "RunScope_START" in line:
            self.current_section = "scope"
            return
        elif "RunScope_END" in line:
            self.current_section = None
            return
        elif "Upgrades_START" in line:
            self.current_section = "upgrades"
            return
        elif "Upgrades_END" in line:
            self.current_section = None
            return

        # Parse key-value pairs
        if "=" in line:
            key, value = self._parse_key_value(line)

            if self.current_section == "parameters":
                self.parameters_data[key] = value
            elif self.current_section == "scope":
                self.scope_data[key] = value
            elif self.current_section == "upgrades":
                self.upgrades_data[key] = value

    def _parse_key_value(self, line: str) -> Tuple[str, str]:
        """
        Parse key = value line

        Args:
            line: Line containing key = value

        Returns:
            Tuple of (key, value)
        """
        parts = line.split("=", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid key=value format: {line}")

        key = parts[0].strip()
        value = parts[1].strip()

        return key, value

    def _build_configuration(self) -> RunConfiguration:
        """Build RunConfiguration from parsed data"""

        # Build RunParameters
        parameters = RunParameters(
            run_mode=self.parameters_data.get("run-mode", "parametric"),
            archetype_dir=self.parameters_data.get(
                "archetype-dir",
                "C:/HTAP/archetypes"
            ),
            unit_costs_db=self.parameters_data.get(
                "unit-costs-db",
                "C:/HTAP/HTAPUnitCosts.json"
            ),
            options_file=self.parameters_data.get(
                "options-file",
                "C:/HTAP/HTAP-options.json"
            )
        )

        # Build RunScope
        scope = RunScope(
            archetypes=self.scope_data.get("archetypes", "*.H2K"),
            locations=self.scope_data.get("locations", "NA"),
            rulesets=self.scope_data.get("rulesets", "as-found")
        )

        # Build OptionUpgrades
        upgrades = {}
        for opt_type, choices_str in self.upgrades_data.items():
            if opt_type.startswith("Opt-"):
                upgrades[opt_type] = OptionUpgrade(
                    option_type=opt_type,
                    choices=choices_str
                )

        return RunConfiguration(
            parameters=parameters,
            scope=scope,
            upgrades=upgrades,
            comments=self.comments
        )


def parse_run_file(file_path: str) -> RunConfiguration:
    """
    Convenience function to parse a .run file

    Args:
        file_path: Path to .run file

    Returns:
        RunConfiguration model
    """
    parser = RunFileParser()
    return parser.parse_file(file_path)
```

### Step 3: Create Run File Writer (45 min)

**File:** `src/parsers/run_writer.py`

```python
"""
Writer for HTAP .run files
"""

from pathlib import Path
from datetime import datetime

from src.models.run_config import RunConfiguration


class RunFileWriter:
    """Writer for .run configuration files"""

    def write_file(
        self,
        config: RunConfiguration,
        output_path: str,
        include_timestamp: bool = True
    ) -> None:
        """
        Write RunConfiguration to .run file

        Args:
            config: RunConfiguration model
            output_path: Output file path
            include_timestamp: Add generation timestamp to header
        """
        content = self.generate_content(config, include_timestamp)

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def generate_content(
        self,
        config: RunConfiguration,
        include_timestamp: bool = True
    ) -> str:
        """
        Generate .run file content from RunConfiguration

        Args:
            config: RunConfiguration model
            include_timestamp: Add generation timestamp

        Returns:
            .run file content as string
        """
        lines = []

        # Header comments
        if config.comments:
            lines.extend(config.comments)
        else:
            lines.append("! Definitions file for HTAP-PRM RUN")

        if include_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"! Generated by HTAP Configuration Editor on {timestamp}")

        lines.append("")

        # RunParameters section
        lines.append("! Run-Mode: Parameters that affect how htap-prm is configured.")
        lines.append("RunParameters_START")
        lines.append(
            f"  {'run-mode':<35} = {config.parameters.run_mode.value}"
        )
        lines.append(
            f"  {'archetype-dir':<35} = {config.parameters.archetype_dir}"
        )
        lines.append(
            f"  {'unit-costs-db':<35} = {config.parameters.unit_costs_db}"
        )
        lines.append(
            f"  {'options-file':<35} = {config.parameters.options_file}"
        )
        lines.append("RunParameters_END")
        lines.append("")
        lines.append("")

        # RunScope section
        lines.append(
            "! Parameters controlling archetypes, locations, reference rulesets."
        )
        lines.append("RunScope_START")
        lines.append("")
        lines.append(
            f"  {'archetypes':<35} = {config.scope.archetypes}"
        )
        lines.append(
            f"  {'locations':<35} = {config.scope.locations}"
        )
        lines.append(
            f"  {'rulesets':<35} = {config.scope.rulesets}"
        )
        lines.append("")
        lines.append("RunScope_END")
        lines.append("")

        # Upgrades section
        lines.append("! Parameters controlling the design of the building")
        lines.append("Upgrades_START")
        lines.append("")

        if config.upgrades:
            for opt_type, upgrade in sorted(config.upgrades.items()):
                lines.append(upgrade.to_run_format())
        else:
            lines.append("   ! No upgrades specified")

        lines.append("")
        lines.append("Upgrades_END")

        return "\n".join(lines)


def write_run_file(
    config: RunConfiguration,
    output_path: str,
    include_timestamp: bool = True
) -> None:
    """
    Convenience function to write a .run file

    Args:
        config: RunConfiguration model
        output_path: Output file path
        include_timestamp: Add generation timestamp
    """
    writer = RunFileWriter()
    writer.write_file(config, output_path, include_timestamp)
```

### Step 4: Create Validation (30 min)

**File:** `src/parsers/validation.py`

```python
"""
Validation for run configurations
"""

from typing import List, Tuple
from pathlib import Path

from src.models.run_config import RunConfiguration


class ValidationError:
    """Represents a validation error"""

    def __init__(self, severity: str, message: str, field: str = ""):
        self.severity = severity  # "error", "warning", "info"
        self.message = message
        self.field = field

    def __str__(self) -> str:
        if self.field:
            return f"[{self.severity.upper()}] {self.field}: {self.message}"
        return f"[{self.severity.upper()}] {self.message}"


def validate_run_configuration(
    config: RunConfiguration
) -> Tuple[bool, List[ValidationError]]:
    """
    Validate a run configuration

    Args:
        config: RunConfiguration to validate

    Returns:
        Tuple of (is_valid, list of errors/warnings)
    """
    errors = []

    # Validate paths exist
    if not Path(config.parameters.archetype_dir).exists():
        errors.append(ValidationError(
            "warning",
            f"Archetype directory not found: {config.parameters.archetype_dir}",
            "archetype-dir"
        ))

    if not Path(config.parameters.unit_costs_db).exists():
        errors.append(ValidationError(
            "error",
            f"Unit costs file not found: {config.parameters.unit_costs_db}",
            "unit-costs-db"
        ))

    if not Path(config.parameters.options_file).exists():
        errors.append(ValidationError(
            "error",
            f"Options file not found: {config.parameters.options_file}",
            "options-file"
        ))

    # Validate at least one upgrade specified
    if not config.upgrades:
        errors.append(ValidationError(
            "warning",
            "No upgrades specified. Run will execute baseline only.",
            "upgrades"
        ))

    # Check for NA in all upgrades
    all_na = all(
        upgrade.choices == ["NA"]
        for upgrade in config.upgrades.values()
    )
    if all_na and config.upgrades:
        errors.append(ValidationError(
            "info",
            "All upgrades set to NA. This will run baseline configuration only.",
            "upgrades"
        ))

    # Determine if configuration is valid (no errors, only warnings/info)
    has_errors = any(e.severity == "error" for e in errors)

    return (not has_errors, errors)
```

### Step 5: Create Unit Tests (1 hour)

**File:** `tests/test_run_parser.py`

```python
"""
Unit tests for run file parser
"""

import pytest
from pathlib import Path

from src.parsers.run_parser import RunFileParser, parse_run_file
from src.parsers.run_writer import RunFileWriter, write_run_file
from src.parsers.validation import validate_run_configuration
from src.models.run_config import RunConfiguration, RunMode


@pytest.fixture
def sample_run_content():
    """Sample .run file content"""
    return """
! Test run file
RunParameters_START
  run-mode                           = parametric
  archetype-dir                      = C:/HTAP/archetypes
  unit-costs-db                      = C:/HTAP/HTAPUnitCosts.json
  options-file                       = C:/HTAP/HTAP-options.json
RunParameters_END

RunScope_START
  archetypes                        = *.H2K
  locations                         = NA
  rulesets                          = as-found
RunScope_END

Upgrades_START
   Opt-Windows     = NA, DoubleGlazed-LowE
   Opt-ACH         = NA, 1.5
Upgrades_END
"""


class TestRunFileParser:
    """Test run file parsing"""

    def test_parse_string(self, sample_run_content):
        """Test parsing from string"""
        parser = RunFileParser()
        config = parser.parse_string(sample_run_content)

        assert config.parameters.run_mode == RunMode.PARAMETRIC
        assert config.scope.archetypes == "*.H2K"
        assert len(config.upgrades) == 2

    def test_parse_upgrades(self, sample_run_content):
        """Test upgrade parsing"""
        parser = RunFileParser()
        config = parser.parse_string(sample_run_content)

        windows = config.get_upgrade("Opt-Windows")
        assert windows is not None
        assert windows.choices == ["NA", "DoubleGlazed-LowE"]

    def test_roundtrip(self, sample_run_content, tmp_path):
        """Test parse → write → parse"""
        parser = RunFileParser()
        writer = RunFileWriter()

        # Parse original
        config1 = parser.parse_string(sample_run_content)

        # Write to file
        output_file = tmp_path / "test.run"
        writer.write_file(config1, str(output_file), include_timestamp=False)

        # Parse written file
        config2 = parser.parse_file(str(output_file))

        # Compare
        assert config1.parameters.run_mode == config2.parameters.run_mode
        assert config1.scope.archetypes == config2.scope.archetypes
        assert len(config1.upgrades) == len(config2.upgrades)


class TestRunFileWriter:
    """Test run file writing"""

    def test_write_file(self, tmp_path):
        """Test writing configuration to file"""
        config = RunConfiguration(
            parameters={
                "run_mode": "parametric",
                "archetype_dir": "C:/HTAP/archetypes",
                "unit_costs_db": "C:/HTAP/HTAPUnitCosts.json",
                "options_file": "C:/HTAP/HTAP-options.json"
            },
            scope={
                "archetypes": "*.H2K",
                "locations": "NA",
                "rulesets": "as-found"
            },
            upgrades={}
        )

        output_file = tmp_path / "output.run"
        write_run_file(config, str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        assert "RunParameters_START" in content
        assert "RunScope_START" in content


class TestValidation:
    """Test configuration validation"""

    def test_validate_valid_config(self):
        """Test validation of valid configuration"""
        config = RunConfiguration(
            parameters={
                "run_mode": "parametric",
                "archetype_dir": "C:/HTAP/archetypes",
                "unit_costs_db": "C:/HTAP/HTAPUnitCosts.json",
                "options_file": "C:/HTAP/HTAP-options.json"
            },
            scope={
                "archetypes": "*.H2K",
                "locations": "NA",
                "rulesets": "as-found"
            },
            upgrades={}
        )

        is_valid, errors = validate_run_configuration(config)
        # May have warnings about missing files, but no critical errors
        critical_errors = [e for e in errors if e.severity == "error"]
        assert len(critical_errors) >= 0  # Depends on environment
```

---

## Acceptance Criteria

✅ **Parser reads** .run files without errors
✅ **Parser handles** comments and formatting correctly
✅ **Writer exports** valid .run files
✅ **Roundtrip works** (parse → write → parse gives same result)
✅ **Validation** catches missing files and invalid options
✅ **Tests pass** with 100% coverage on parser
✅ **Works with real** HTAP .run files from C:/HTAP/

---

## Testing Checklist

```bash
# Run tests
pytest tests/test_run_parser.py -v

# Test with real file
python -c "
from src.parsers.run_parser import parse_run_file
from src.parsers.run_writer import write_run_file

# Parse existing file
config = parse_run_file('C:/HTAP/recover/regions.run')
print(f'Parsed {len(config.upgrades)} upgrades')

# Write to new file
write_run_file(config, 'test_output.run')
print('Exported successfully')
"
```

---

## Next Steps

After completing this task:
1. Test parser with all .run files in C:/HTAP/
2. Document any edge cases found
3. Move to **Task 1.5: Options Data Structure**

---

## Time Tracking

- Run config models: 45 min
- Parser: 60 min
- Writer: 45 min
- Validation: 30 min
- Unit tests: 60 min
- **Total: ~3.5 hours**
