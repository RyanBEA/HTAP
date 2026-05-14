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
        # Pad option_type to 25 characters for alignment
        return f"   {self.option_type:<24} = {choices_str}"


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
