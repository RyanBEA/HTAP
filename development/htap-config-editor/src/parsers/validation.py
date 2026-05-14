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

    def __repr__(self) -> str:
        return f"ValidationError(severity='{self.severity}', field='{self.field}', message='{self.message}')"


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
    archetype_path = Path(config.parameters.archetype_dir)
    if not archetype_path.exists():
        errors.append(ValidationError(
            "warning",
            f"Archetype directory not found: {config.parameters.archetype_dir}",
            "archetype-dir"
        ))

    costs_path = Path(config.parameters.unit_costs_db)
    if not costs_path.exists():
        errors.append(ValidationError(
            "error",
            f"Unit costs file not found: {config.parameters.unit_costs_db}",
            "unit-costs-db"
        ))

    options_path = Path(config.parameters.options_file)
    if not options_path.exists():
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
    else:
        # Check for NA in all upgrades
        all_na = all(
            upgrade.choices == ["NA"]
            for upgrade in config.upgrades.values()
        )
        if all_na:
            errors.append(ValidationError(
                "info",
                "All upgrades set to NA. This will run baseline configuration only.",
                "upgrades"
            ))

    # Determine if configuration is valid (no errors, only warnings/info)
    has_errors = any(e.severity == "error" for e in errors)

    return (not has_errors, errors)
