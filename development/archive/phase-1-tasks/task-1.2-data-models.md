# Task 1.2: Data Models & Loading

**Duration:** 2-3 hours
**Phase:** 1 - Foundation
**Dependencies:** Task 1.1 (Project Setup)
**Completion Criteria:** Pydantic models created, JSON loaders functional, tests passing with REAL data

⚠️ **IMPORTANT:** This task has been updated based on architectural review to match actual HTAP data structures.

---

## Objective

Create type-safe Pydantic models for HTAP data structures and implement loaders for HTAP-options.json (0.32 MB) and HTAPUnitCosts.json (0.19 MB).

---

## What You'll Build

1. Pydantic models for:
   - Unit Costs (from HTAPUnitCosts.json) - **CORRECTED STRUCTURE**
   - Options (from HTAP-options.json) - **WITH ALL METADATA**
   - Run Configuration (for .run files)
2. JSON loaders with validation
3. Simple in-memory caching with @lru_cache
4. Unit tests with **REAL HTAP data** (not mocks)

---

## Technical Approach

### Data Model Architecture

```
src/models/
├── __init__.py           # Export all models
├── cost.py               # SourceCostData, UnitCostsDatabase (CORRECTED)
├── option.py             # OptionChoice, OptionCategory (WITH METADATA)
├── run_config.py         # RunConfig, RunScope, RunParameters
└── common.py             # Shared types and enums
```

### Key Design Decisions

1. **Pydantic v2** for runtime validation and type safety
2. **Nested models** to match actual JSON structure
3. **All category metadata fields** included
4. **Simple @lru_cache** (files are only 0.32 MB + 0.19 MB)
5. **Test with real data** from day one

---

## Step-by-Step Implementation

### Step 1: Create Common Types (20 min)

**File:** `src/models/common.py`

```python
"""
Common types and enums used across models
"""

from enum import Enum
from pydantic import BaseModel


class HTAPBaseModel(BaseModel):
    """Base model with common configuration"""

    class Config:
        # Pydantic v2 configuration
        extra = "allow"  # Allow extra fields from JSON
        populate_by_name = True
        validate_assignment = True


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
```

---

### Step 2: Create Cost Models (45 min)

⚠️ **CRITICAL:** The actual HTAPUnitCosts.json structure is **nested by source**, not flat!

**File:** `src/models/cost.py`

```python
"""
Pydantic models for HTAPUnitCosts.json
CORRECTED to match actual nested structure
"""

from typing import Dict, List, Optional
from pydantic import Field

from .common import HTAPBaseModel


class SourceCostData(HTAPBaseModel):
    """
    Cost data from a specific source (e.g., LEEP-ON-Ottawa)

    This is the actual structure within HTAPUnitCosts.json
    """

    category: str = Field(description="Cost category (DRYWALL, HVAC, etc.)")
    description: str = Field(description="Component description")
    units: str = Field(description="Unit of measurement (sf wall, each, etc.)")  # Note: plural!
    UnitCostMaterials: float = Field(description="Material cost per unit")
    UnitCostLabour: float = Field(description="Labour cost per unit")
    note: Optional[str] = Field(None, description="Additional notes")
    date: Optional[str] = Field(None, description="Date of cost data")
    source: str = Field(description="Source identifier")

    def total_cost(self) -> float:
        """Get combined material + labour cost"""
        return self.UnitCostMaterials + self.UnitCostLabour


class CostSource(HTAPBaseModel):
    """Metadata for a cost data source"""

    filename: str = Field(description="Original source filename")
    date_collated: str = Field(description="Date data was collected")
    date_imported: str = Field(description="Date imported into HTAP")
    schema_used: str = Field(description="Schema version")
    origin: str = Field(description="Description of data source")
    inherits: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Inheritance map: {parent_source: [component_ids]}"
    )


class UnitCostsDatabase(HTAPBaseModel):
    """
    Complete HTAPUnitCosts.json structure

    Structure: {component_id: {source_name: SourceCostData}}
    """

    sources: Dict[str, CostSource] = Field(description="Cost data sources metadata")
    data: Dict[str, Dict[str, SourceCostData]] = Field(
        description="Component cost data: {component_id: {source: data}}"
    )

    def get_component(self, component_id: str) -> Optional[Dict[str, SourceCostData]]:
        """Get all source data for a component"""
        return self.data.get(component_id)

    def get_cost(self, component_id: str, source: str) -> Optional[float]:
        """Get total cost (materials + labour) for component from source"""
        if component_id in self.data and source in self.data[component_id]:
            return self.data[component_id][source].total_cost()
        return None

    def list_sources(self) -> List[str]:
        """List all available cost sources"""
        return list(self.sources.keys())

    def list_components(self) -> List[str]:
        """List all component IDs"""
        return list(self.data.keys())

    def get_components_with_source(self, source: str) -> List[str]:
        """Get all components that have data from specified source"""
        return [
            comp_id
            for comp_id, sources in self.data.items()
            if source in sources
        ]
```

---

### Step 3: Create Option Models (45 min)

⚠️ **CRITICAL:** OptionCategory has important metadata fields that were missing!

**File:** `src/models/option.py`

```python
"""
Pydantic models for HTAP-options.json
CORRECTED to include all category-level metadata
"""

from typing import Any, Dict, List, Optional
from pydantic import Field

from .common import HTAPBaseModel


class H2KMapping(HTAPBaseModel):
    """HOT2000 XML mapping for an option"""
    # Uses extra="allow" to capture all h2kMap fields dynamically
    pass


class CostComponents(HTAPBaseModel):
    """Cost component assignments for an option"""

    components: List[str] = Field(
        default_factory=list,
        description="List of component IDs from HTAPUnitCosts.json"
    )
    custom_costs: Dict[str, Any] = Field(  # ← THIS WAS MISSING
        default_factory=dict,
        alias="custom-costs",
        description="Custom cost overrides"
    )


class OptionChoice(HTAPBaseModel):
    """A single choice within an option category"""

    choice_name: str = Field(description="Internal name for this choice")
    h2k_map: Optional[Dict[str, Any]] = Field(
        None,
        alias="h2kMap",
        description="HOT2000 XML mappings"
    )
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    costs: Optional[CostComponents] = Field(None, description="Associated cost components")
    cost_proxy: Optional[str] = Field(
        None,
        alias="costProxy",
        description="Reference to another option's costs"
    )
    display_name: Optional[str] = Field(None, description="Human-readable name")
    description: Optional[str] = Field(None, description="Detailed description")


class OptionCategory(HTAPBaseModel):
    """A category of options (e.g., Opt-Windows)"""

    category_type: str = Field(description="Category name (Opt-*)")
    structure: str = Field(description="Structure type: 'flat' or 'tree'")  # ← WAS MISSING
    costed: bool = Field(description="Whether costs are tracked")  # ← WAS MISSING
    options: Dict[str, OptionChoice] = Field(description="Available choices")  # Note: "options" not "choices"
    default: Optional[str] = Field(None, description="Default option choice")  # ← WAS MISSING
    stop_on_error: bool = Field(  # ← WAS MISSING
        True,
        alias="stop-on-error",
        description="Stop execution on error"
    )
    h2k_schema: Optional[List[str]] = Field(  # ← WAS MISSING
        None,
        alias="h2kSchema",
        description="H2K XML schema tags"
    )

    def list_choices(self) -> List[str]:
        """List all choice names in this category"""
        return list(self.options.keys())

    def get_choice(self, choice_name: str) -> Optional[OptionChoice]:
        """Get a specific choice by name"""
        return self.options.get(choice_name)

    def search_choices(self, query: str) -> Dict[str, OptionChoice]:
        """Search choices by name, tags, or description"""
        query_lower = query.lower()
        results = {}

        for name, choice in self.options.items():
            if query_lower in name.lower():
                results[name] = choice
            elif choice.description and query_lower in choice.description.lower():
                results[name] = choice
            elif any(query_lower in tag.lower() for tag in choice.tags):
                results[name] = choice

        return results


class OptionsDatabase(HTAPBaseModel):
    """Complete HTAP-options.json structure"""

    categories: Dict[str, OptionCategory] = Field(description="All option categories")

    def get_category(self, category_type: str) -> Optional[OptionCategory]:
        """Get an option category by type"""
        return self.categories.get(category_type)

    def list_categories(self) -> List[str]:
        """List all category types"""
        return list(self.categories.keys())

    def search_all(self, query: str) -> Dict[str, Dict[str, OptionChoice]]:
        """Search across all categories"""
        results = {}
        for cat_name, category in self.categories.items():
            cat_results = category.search_choices(query)
            if cat_results:
                results[cat_name] = cat_results
        return results
```

---

### Step 4: Create Data Loaders (45 min)

**File:** `src/utils/loaders.py`

```python
"""
Data loaders for HTAP JSON files
Uses simple caching for 0.32 MB + 0.19 MB files
"""

import json
from pathlib import Path
from functools import lru_cache
from typing import Dict

from src.models.cost import UnitCostsDatabase, CostSource, SourceCostData
from src.models.option import OptionsDatabase, OptionCategory, OptionChoice


@lru_cache(maxsize=2)
def load_unit_costs(file_path: str) -> UnitCostsDatabase:
    """
    Load HTAPUnitCosts.json with validation

    Args:
        file_path: Path to HTAPUnitCosts.json

    Returns:
        Validated UnitCostsDatabase model

    Note: Cached in memory (file is only 0.19 MB)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Unit costs file not found: {file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # Parse sources
    sources = {
        source_name: CostSource(**source_data)
        for source_name, source_data in raw_data.get("sources", {}).items()
    }

    # Parse component data (nested by source)
    data: Dict[str, Dict[str, SourceCostData]] = {}
    for comp_id, source_dict in raw_data.get("data", {}).items():
        data[comp_id] = {
            source_name: SourceCostData(**source_data)
            for source_name, source_data in source_dict.items()
        }

    return UnitCostsDatabase(sources=sources, data=data)


@lru_cache(maxsize=2)
def load_options(file_path: str) -> OptionsDatabase:
    """
    Load HTAP-options.json with validation

    Args:
        file_path: Path to HTAP-options.json

    Returns:
        Validated OptionsDatabase model

    Note: Cached in memory (file is only 0.32 MB)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Options file not found: {file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    categories = {}
    for cat_name, cat_data in raw_data.items():
        if cat_name.startswith("Opt-"):
            # Parse choices (note: field is "options" in JSON)
            choices = {}
            for choice_name, choice_data in cat_data.get("options", {}).items():
                choices[choice_name] = OptionChoice(
                    choice_name=choice_name,
                    **choice_data
                )

            # Create category with all metadata
            categories[cat_name] = OptionCategory(
                category_type=cat_name,
                structure=cat_data.get("structure", "flat"),
                costed=cat_data.get("costed", False),
                options=choices,
                default=cat_data.get("default"),
                stop_on_error=cat_data.get("stop-on-error", True),
                h2k_schema=cat_data.get("h2kSchema")
            )

    return OptionsDatabase(categories=categories)


def clear_cache():
    """Clear loader cache"""
    load_unit_costs.cache_clear()
    load_options.cache_clear()
```

---

### Step 5: Create Unit Tests (45 min)

⚠️ **CRITICAL:** Test with REAL HTAP data, not mocked structures!

**File:** `tests/test_models.py`

```python
"""
Unit tests for Pydantic models
MUST USE REAL DATA - not mocks!
"""

import pytest
from src.models.cost import UnitCostsDatabase, SourceCostData
from src.models.option import OptionsDatabase, OptionCategory


class TestCostModels:
    """Test cost data models with real data"""

    def test_source_cost_data_structure(self):
        """Test SourceCostData model matches actual structure"""
        # Real data sample from HTAPUnitCosts.json
        real_data = {
            "category": "DRYWALL",
            "description": "1/2in Gypsum board",
            "units": "sf wall",  # Note: plural!
            "UnitCostMaterials": 0.35,
            "UnitCostLabour": 0.41,
            "note": "n.d.",
            "date": "n.d.",
            "source": "LEEP-ON-Ottawa"
        }

        cost_data = SourceCostData(**real_data)
        assert cost_data.units == "sf wall"
        assert cost_data.total_cost() == 0.76

    def test_load_real_cost_database(self):
        """Test loading actual HTAPUnitCosts.json"""
        from src.utils.loaders import load_unit_costs

        costs = load_unit_costs("C:/HTAP/HTAPUnitCosts.json")

        # Verify structure
        assert len(costs.sources) == 8
        assert len(costs.data) == 351

        # Test known component
        gypsum = costs.get_component("1/2in_gypsum_board")
        assert gypsum is not None

        ottawa_data = gypsum["LEEP-ON-Ottawa"]
        assert ottawa_data.category == "DRYWALL"
        assert ottawa_data.units == "sf wall"
        assert ottawa_data.UnitCostMaterials == 0.35
        assert ottawa_data.UnitCostLabour == 0.41


class TestOptionModels:
    """Test option data models with real data"""

    def test_option_category_has_metadata(self):
        """Test that category model includes all metadata fields"""
        cat_data = {
            "category_type": "Opt-Windows",
            "structure": "tree",
            "costed": True,
            "options": {},
            "default": "NA",
            "stop-on-error": True,
            "h2kSchema": ["House", "Components"]
        }

        category = OptionCategory(**cat_data)
        assert category.structure == "tree"
        assert category.costed == True
        assert category.default == "NA"
        assert category.stop_on_error == True
        assert category.h2k_schema == ["House", "Components"]

    def test_load_real_options_database(self):
        """Test loading actual HTAP-options.json"""
        from src.utils.loaders import load_options

        options = load_options("C:/HTAP/HTAP-options.json")

        # Verify counts
        assert len(options.categories) == 34

        # Test known category
        windows = options.get_category("Opt-Windows")
        assert windows is not None
        assert windows.structure == "tree"
        assert windows.costed == True
        assert len(windows.options) == 61
        assert windows.default == "NA"

    def test_custom_costs_field_exists(self):
        """Test that CostComponents has custom-costs field"""
        from src.models.option import CostComponents

        costs = CostComponents(
            components=["comp1"],
            custom_costs={"custom_field": 123}  # Field was missing before
        )

        assert "custom_field" in costs.custom_costs
```

---

## Acceptance Criteria

✅ **Pydantic models created** matching actual JSON structure
✅ **Models validate** real HTAP-options.json and HTAPUnitCosts.json
✅ **Loaders work** with actual files (not mocks)
✅ **Simple caching** with @lru_cache (no diskcache needed)
✅ **Unit tests pass** with real HTAP data
✅ **Load time** <200ms for both files

---

## Testing Checklist

Run these commands to verify completion:

```bash
# Type checking
mypy src/models/ src/utils/

# Run tests with real data
pytest tests/test_models.py -v

# Load real data (manual test)
python -c "
from src.utils.loaders import load_unit_costs, load_options
import time

start = time.time()
costs = load_unit_costs('C:/HTAP/HTAPUnitCosts.json')
print(f'Loaded {len(costs.data)} cost components in {(time.time()-start)*1000:.0f}ms')

start = time.time()
options = load_options('C:/HTAP/HTAP-options.json')
print(f'Loaded {len(options.categories)} option categories in {(time.time()-start)*1000:.0f}ms')

# Verify structure
windows = options.get_category('Opt-Windows')
print(f'Windows category: structure={windows.structure}, costed={windows.costed}, choices={len(windows.options)}')
"
```

Expected output:
```
Loaded 351 cost components in ~150ms
Loaded 34 option categories in ~50ms
Windows category: structure=tree, costed=True, choices=61
```

---

## Common Issues & Solutions

### Issue: Pydantic validation error "units" not "unit"
**Solution:** Field is plural in actual JSON: `units: str`

### Issue: Can't find "choices" in category
**Solution:** Field is named `options` in JSON, use `category.options`

### Issue: Cost structure doesn't match
**Solution:** Data is nested: `{comp_id: {source: SourceCostData}}`

---

## Next Steps

After completing this task:
1. Verify all tests pass with real HTAP files
2. Test cache functionality (second load should be <10ms)
3. Move to **Task 1.3: Basic UI Layout**

---

## Time Tracking

- Common types: 20 min
- Cost models: 45 min
- Option models: 45 min
- Loaders: 45 min
- Unit tests: 45 min
- **Total: ~2.5 hours**

---

## 📊 Actual Data Statistics (for reference)

```
File Sizes:
  HTAP-options.json:     0.32 MB (328 KB)
  HTAPUnitCosts.json:    0.19 MB (191 KB)

Data Inventory:
  Option categories:     34
  Total option choices:  769
  Cost components:       351
  Cost sources:          8

  Choices with costs:    175 (23%)
  Costed categories:     27 (79%)
```
