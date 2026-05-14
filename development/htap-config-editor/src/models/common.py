"""
Common types and enums used across models
"""

from enum import Enum
from pydantic import BaseModel, ConfigDict


class HTAPBaseModel(BaseModel):
    """Base model with common configuration for Pydantic v2"""

    model_config = ConfigDict(
        extra="allow",  # Allow extra fields from JSON
        populate_by_name=True,  # Allow field population by alias or name
        validate_assignment=True,  # Validate on assignment after creation
    )


class OptionType(str, Enum):
    """Types of HTAP options"""
    ARCHETYPE = "Opt-Archetype"
    LOCATION = "Opt-Location"
    ACH = "Opt-ACH"
    WINDOWS = "Opt-Windows"
    ABOVE_GRADE_WALL = "Opt-AboveGradeWall"
    ATTIC_CEILINGS = "Opt-AtticCeilings"
    FOUNDATION_WALL_EXT = "Opt-FoundationWallExtIns"
    FOUNDATION_WALL_INT = "Opt-FoundationWallIntIns"
    FOUNDATION_SLAB_ON_GRADE = "Opt-FoundationSlabOnGrade"
    FOUNDATION_SLAB_BELOW_GRADE = "Opt-FoundationSlabBelowGrade"
    HEATING_COOLING = "Opt-Heating-Cooling"
    DHW_SYSTEM = "Opt-DHWSystem"
    VENT_SYSTEM = "Opt-VentSystem"
    H2K_PV = "Opt-H2K-PV"
    RESULT_HOUSE_CODE = "Opt-ResultHouseCode"
