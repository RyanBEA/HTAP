# NBC 2020 Energy Compliance Form Generation

## Purpose & Scope
The compliance reporting system generates NBC 2020 Energy Compliance Forms programmatically from HOT2000 .h2k building simulation files. It uses a configuration-driven architecture that extracts data from reference and proposed building models and populates the official NBC compliance form template through XPath-based data extraction, value transformations, and formula calculations.

This approach ensures forms remain synchronized with official NBC requirements while enabling automated generation from HTAP runs.

## Location
- **Source code**: `complianceReporting/`
- **Documentation**: `doc/complianceReporting.md` (this file)
- **Template utilities**: `util/build_fillable_form.py`, `util/fill_form_dummy_data.py`

## Quick Start

```bash
# Navigate to complianceReporting directory
cd C:/HTAP/complianceReporting

# Run the processor with your H2K files
python process_h2k_to_nbc.py reference.h2k proposed.h2k output.docx
```

This will:
1. Load configuration from `h2k_to_nbc_mapping.json`
2. Extract data from both reference and proposed H2K XML files
3. Apply transformations and calculate formulas
4. Fill the NBC form template with extracted data
5. Generate a completed compliance form (.docx)

## System Architecture

### Configuration-Driven Design
The system is driven entirely by `h2k_to_nbc_mapping.json`, which defines:
- **137 field mappings** (T0_R1_C1 through T17_R6_C1)
- **XPath expressions** for data extraction
- **Transformations** (R-to-U conversion, climate zone lookup, rounding, etc.)
- **Formulas** (FDWR calculation, ventilation power, complex equipment descriptions)
- **Data sources** (reference vs. proposed model selection)

This design allows non-programmers to add new field mappings by editing JSON configuration rather than modifying Python code.

### Core Components

**process_h2k_to_nbc.py** (270 lines)
- Main orchestration script
- Loads configuration, H2K files, and form template
- Coordinates extraction, transformation, and form filling
- Handles static values, formulas, and complex mappings

**h2k_to_nbc_mapping.json** (58 KB, version 3.4)
- Configuration file with 137 field mappings
- 82 real data extractions from H2K files (78 unique + 4 FDWR/wall/window area fields in Tables 3 and 5)
- 55 placeholder mappings (extract from `.//Application/Name` for manual completion)
- Type-filtered parallel path RSI formulas for ceiling types (attic vs cathedral/flat)
- Attribute-filtered formulas for unheated basement floors (above/below frost line), heated floors, and exterior doors
- Component presence detection with N/A support for absent building components (ceilings, floors, skylights, doors)
- Comprehensive wall area, fenestration, and FDWR% formulas (used in Tables 3 and 5)
- Parent-relative XPath support for basement wall perimeter calculation
- Weighted average formulas for window and skylight SHGC calculations
- Conditional COP to HSPF conversion for heat pump systems based on isCop attribute
- Metadata tracking: version, date, fields mapped

**config_loader.py** (137 lines)
- Loads and validates JSON configuration
- Ensures all required fields present
- Validates references to transformations and formulas

**h2k_extractor.py** (185 lines)
- Extracts data from H2K XML using XPath expressions
- Handles element extraction with optional attributes
- Supports XPath lists for concatenated multi-field values
- Checks element existence for validation
- Extracts multiple attributes from same element (value + check attribute)
- Returns tuples for conditional conversion processing

**transformations.py** (180 lines)
- Value transformation functions:
  - `r_to_u`: R-value to U-value conversion (1/R)
  - `climate_zone`: HDD range to NBC climate zone
  - `orientation_abbrev`: Full name to abbreviation (Southwest → SW)
  - `round2`, `round1`: Decimal rounding
  - `text`: Passthrough for strings

**formula_processor.py** (540 lines)
- Formula calculation engine with parallel path RSI support
- Type-filtered component selection (e.g., filter ceilings by Attic/gable vs Cathedral)
- Attribute-filtered component selection (e.g., filter basement floors by heatedFloor="false" and isBelowFrostline="true")
- Component presence detection: returns "N/A" string when components don't exist (vs 0 when uninsulated)
- Parent-relative XPath support: enables navigation to sibling elements (e.g., basement wall perimeter from Floor element)
- Handles missing rValue elements (treats as uninsulated, returns 0)
- Complex mapping processor for multi-component strings with conditional conversions
- Conditional unit conversion based on XML attributes (COP to HSPF conversion)
- Examples: FDWR calculation, parallel path RSI averaging, ventilation power, equipment descriptions with heat pumps

### Form Template Structure

**form_template.docx** (48 KB)
- Official NBC 2020 Energy Compliance Form with placeholders
- 137 data cells replaced with `{{T#_R#_C#}}` tokens
- All formatting, merged cells, and styling preserved
- Generated by `util/build_fillable_form.py` from official form

**form_template_fields.json** (19 KB)
- Metadata for all 137 fields
- Maps field IDs to row/column labels
- Used to understand semantic meaning of each field

## Field Coordinate System

Each fillable field uses a coordinate-based identifier:

```
Format: T<table>_R<row>_C<column>

Examples:
  T0_R1_C1  = Table 0, Row 1, Column 1 (Project Name)
  T5_R3_C2  = Table 5, Row 3, Column 2 (Ceiling RSI - Reference)
  T5_R3_C3  = Table 5, Row 3, Column 3 (Ceiling RSI - Proposed)
  T14_R5_C4 = Table 14, Row 5, Column 4 (Heating system type)
```

**Important Column Assignments**:
- **Table 5 (Building Envelope)**: C2 = Reference Model, C3 = Proposed Model
- **Table 14 (Reference Specifications)**: C4 = Proposed Model (most fields in C5/C6/C7)
- This differs from other tables where C1 is typically Reference

## Configuration File Structure

### 1. Metadata Section
```json
{
  "metadata": {
    "version": "2.7",
    "description": "Comprehensive H2K to NBC 2020 compliance form field mapping configuration",
    "last_updated": "2025-10-30",
    "notes": "Added attribute-filtered parallel path RSI formulas for unheated basement floors (above/below frost line). Supports missing AddedToSlab elements.",
    "fields_mapped": 137,
    "fields_total": 137
  }
}
```

### 2. Field Mappings

#### Simple XPath Extraction
```json
{
  "nbc_field": "T5_R3_C3",
  "description": "Ceiling RSI (Proposed)",
  "source": "proposed",
  "xpath": ".//House/Components/Ceiling/Construction/CeilingType",
  "xpath_attr": "rValue",
  "transform": "round2",
  "default": ""
}
```

#### XPath List (Concatenated)
```json
{
  "nbc_field": "T0_R2_C1",
  "description": "Project Address",
  "source": "proposed",
  "xpath_list": [
    ".//ProgramInformation/Client/StreetAddress/Street",
    ".//ProgramInformation/Client/StreetAddress/City",
    ".//ProgramInformation/Client/StreetAddress/Province",
    ".//ProgramInformation/Client/StreetAddress/PostalCode"
  ],
  "transform": "concatenate",
  "separator": ", ",
  "default": ""
}
```

#### Formula-Based Field
```json
{
  "nbc_field": "T3_R1_C1",
  "description": "FDWR Percentage (Reference)",
  "formula": "fdwr_reference",
  "format": "%.1f",
  "default": ""
}
```

#### Complex Mapping (Multi-Component)
```json
{
  "nbc_field": "T5_R25_C2",
  "description": "Heating System Description (Proposed)",
  "complex_mapping": "heating_system_proposed",
  "default": ""
}
```

#### Placeholder Field (Manual Completion)
```json
{
  "nbc_field": "T5_R26_C3",
  "description": "PLACEHOLDER - manual mapping required",
  "source": "proposed",
  "xpath": ".//Application/Name",
  "transform": "text",
  "default": "NA"
}
```
*Note: Placeholder fields extract "HOT2000" from the H2K file for easy identification in the output document.*

### 3. Formulas

#### Standard Formula Example: FDWR Calculation

```json
{
  "formulas": {
    "fdwr_calculation": {
      "description": "Calculate FDWR (Fenestration and Door to Wall Ratio)",
      "inputs": {
        "window_area": ".//AllResults/Results/Other/GrossArea/MainFloors",
        "door_area": ".//AllResults/Results/Other/GrossArea/MainFloors",
        "wall_area": ".//AllResults/Results/Other/GrossArea/MainFloors"
      },
      "input_attrs": {
        "window_area": "windows",
        "door_area": "doors",
        "wall_area": "mainWalls"
      },
      "calculation": "((window_area + door_area) / wall_area) * 100",
      "format": "%.1f"
    }
  }
}
```

#### Parallel Path RSI Formula Example

Calculates area-weighted average RSI using the parallel path method: **Average RSI = (Total Area) / Σ(Area_i / RSI_i)**

```json
{
  "formulas": {
    "parallel_path_rsi_walls": {
      "description": "Calculate area-weighted average RSI for walls using parallel path method",
      "type": "parallel_path_rsi",
      "elements_xpath": ".//House/Components/Wall",
      "rvalue_xpath": "./Construction/Type",
      "rvalue_attr": "rValue",
      "area_height_xpath": "./Measurements",
      "area_height_attr": "height",
      "area_perimeter_xpath": "./Measurements",
      "area_perimeter_attr": "perimeter",
      "format": "%.2f"
    },
    "parallel_path_rsi_ceilings_attic": {
      "description": "Calculate average RSI for attic ceilings only",
      "type": "parallel_path_rsi",
      "elements_xpath": ".//House/Components/Ceiling",
      "type_filter": ["Attic/gable", "Attic/hip"],
      "type_xpath": "./Construction/Type/English",
      "rvalue_xpath": "./Construction/CeilingType",
      "rvalue_attr": "rValue",
      "area_xpath": "./Measurements",
      "area_attr": "area",
      "format": "%.2f"
    }
  }
}
```

**Parallel Path Formula Features:**
- **Type filtering**: Filter components by Construction/Type/English (e.g., ceiling types: "Attic/gable", "Cathedral", "Flat")
- **Attribute filtering**: Filter components by XML attributes (e.g., basement floor heatedFloor="false", isBelowFrostline="true")
- **Area calculation methods**:
  - Direct area: `area_xpath` + `area_attr` (for ceilings, floors)
  - Calculated area: height × perimeter (for walls)
- **Missing rValue handling**: `allow_missing_rvalue=true` treats missing AddedToSlab elements as uninsulated (returns 0)
- **Per NRCan guidance**: https://natural-resources.canada.ca/energy-efficiency/energy-star/tables-calculating-effective-thermal-resistance-opaque-assemblies

#### Attribute-Filtered Formula Example

For unheated basement floors below frost line:

```json
{
  "formulas": {
    "parallel_path_rsi_basement_floors_unheated_below_frost": {
      "description": "Calculate RSI for unheated basement floors below frost line",
      "type": "parallel_path_rsi",
      "elements_xpath": ".//Basement/Floor",
      "attribute_filter": {
        "heatedFloor": "false",
        "isBelowFrostline": "true"
      },
      "attribute_filter_xpath": "./Construction",
      "rvalue_xpath": "./Construction/AddedToSlab",
      "rvalue_attr": "rValue",
      "allow_missing_rvalue": true,
      "area_xpath": "./Measurements",
      "area_attr": "area",
      "format": "%.2f"
    }
  }
}
```

**Attribute Filter Behavior:**
- Filters elements by checking attributes on the element found at `attribute_filter_xpath`
- All attribute conditions must match (AND logic)
- If `allow_missing_rvalue=true`: missing AddedToSlab or rValue=0 returns 0.00 (uninsulated)
- If `allow_missing_rvalue=false`: missing elements are skipped

#### Skylight and Door Formulas

**Skylight U-Value (Parallel Path Method)**

Calculates area-weighted average U-value for skylights using the parallel path method:

```json
{
  "formulas": {
    "parallel_path_rsi_skylights": {
      "description": "Calculate area-weighted average RSI for skylights using parallel path method",
      "type": "parallel_path_rsi",
      "elements_xpath": ".//House/Components/Ceiling/Components/Window",
      "rvalue_xpath": "./Construction/Type",
      "rvalue_attr": "rValue",
      "area_height_xpath": "./Measurements",
      "area_height_attr": "height",
      "area_width_xpath": "./Measurements",
      "area_width_attr": "width",
      "return_na_if_no_elements": true,
      "format": "%.4f"
    }
  }
}
```

**Skylight Identification:**
- Windows nested under `Ceiling/Components` are considered skylights
- No additional filtering by tilt code - location determines classification
- Returns "N/A" if no skylights present in building

**Skylight SHGC (Weighted Average Method)**

Calculates area-weighted average Solar Heat Gain Coefficient for skylights:

```json
{
  "formulas": {
    "weighted_average_shgc_skylights": {
      "description": "Calculate area-weighted average SHGC for skylights",
      "type": "weighted_average",
      "elements_xpath": ".//House/Components/Ceiling/Components/Window",
      "attribute_name": "shgc",
      "attribute_xpath": ".",
      "area_height_xpath": "./Measurements",
      "area_height_attr": "height",
      "area_width_xpath": "./Measurements",
      "area_width_attr": "width",
      "return_na_if_no_elements": true,
      "format": "%.3f"
    }
  }
}
```

**SHGC Calculation:**
- Weighted average: `Σ(SHGC_i × Area_i) / Σ(Area_i)`
- Area = height × width for each skylight
- Returns "N/A" if no skylights present

**Door U-Value (Parallel Path Method)**

Calculates area-weighted average U-value for all exterior doors:

```json
{
  "formulas": {
    "parallel_path_rsi_doors": {
      "description": "Calculate area-weighted average R-value for all exterior doors using parallel path method",
      "type": "parallel_path_rsi",
      "elements_xpath": ".//House/Components/Wall/Components/Door | .//House/Components/Basement/Components/Door",
      "attribute_filter": {
        "adjacentEnclosedSpace": "false"
      },
      "attribute_filter_xpath": ".",
      "rvalue_xpath": ".",
      "rvalue_attr": "rValue",
      "area_height_xpath": "./Measurements",
      "area_height_attr": "height",
      "area_width_xpath": "./Measurements",
      "area_width_attr": "width",
      "return_na_if_no_elements": true,
      "format": "%.4f"
    }
  }
}
```

**Door Filtering:**
- Includes doors from both Wall and Basement components
- Filters by `adjacentEnclosedSpace="false"` to include only exterior doors
- Excludes garage doors and doors to enclosed porches
- All 39 test archetype files contain exterior doors
- Returns "N/A" if no exterior doors present (theoretical case)

#### Component Presence Detection (N/A Support)

The `return_na_if_no_elements` flag distinguishes between components that don't exist versus components that exist but are uninsulated:

```json
{
  "formulas": {
    "parallel_path_rsi_foundation_walls": {
      "description": "Calculate RSI for foundation walls using parallel path method",
      "type": "parallel_path_rsi",
      "elements_xpath": ".//House/Components/Basement/Wall",
      "return_na_if_no_elements": true,
      "format": "%.2f"
    }
  }
}
```

**N/A Return Conditions:**
- When `return_na_if_no_elements: true` is set
- Returns "N/A" string (not 0.00) if:
  - No elements found at `elements_xpath` (component doesn't exist in building)
  - No elements pass type/attribute filters (e.g., no cathedral ceilings in attic-only building)
- Returns 0.00 if:
  - Elements exist but have rValue=0 (uninsulated component)
  - Elements exist but missing rValue element with `allow_missing_rvalue: true`

**Used For:**
- **T5_R2_C2/C3**: Attic ceilings (N/A if no attic)
- **T5_R3_C2/C3**: Cathedral/flat ceilings (N/A if none present)
- **T5_R5_C2/C3**: Heated floors (N/A if not present)
- **T5_R6_C2/C3**: Foundation walls (N/A if slab-on-grade)
- **T5_R7_C3/C4**: Unheated basement floors above frost (N/A if no basement)
- **T5_R8_C3/C4**: Unheated basement floors below frost (N/A if no basement or above frost)
- **T5_R10_C2/C3**: Exposed floors (N/A if not present)
- **T5_R11_C2/C3**: Slabs with integral footing (N/A if not present)
- **T5_R16_C2/C3**: Skylights (N/A if no skylights in ceiling)
- **T5_R17_C3**: Skylight SHGC (N/A if no skylights in ceiling)
- **T5_R18_C1/C2**: Exterior doors (N/A if no exterior doors - theoretical)

This allows NBC forms to correctly indicate "not applicable" for components that don't exist in specific building configurations (full basement vs crawlspace vs slab-on-grade).

**N/A Value Handling:**

The system preserves "N/A" values throughout the processing pipeline:

1. **Formula calculation**: Functions like `parallel_path_rsi` and `weighted_average` return "N/A" string when no elements found
2. **Formatting**: `_format_result()` passes through "N/A" unchanged, skipping numeric formatting
3. **Transformations**: process_h2k_to_nbc.py skips transforms for "N/A" values (lines 111, 116)
4. **Final output**: "N/A" appears verbatim in generated Word document

This ensures that absence of a component is clearly distinguished from presence of an uninsulated component (which shows 0.00).

#### Parent-Relative XPath Support

For basement foundation walls, the perimeter is stored in the Floor element rather than the Wall element. The formula processor supports parent-relative XPath navigation using `../` prefix:

```json
{
  "formulas": {
    "parallel_path_rsi_foundation_walls": {
      "elements_xpath": ".//House/Components/Basement/Wall",
      "area_height_xpath": "./Measurements",
      "area_height_attr": "height",
      "area_perimeter_xpath": "../Floor/Measurements",
      "area_perimeter_attr": "perimeter"
    }
  }
}
```

**Implementation:**
- Builds parent map for entire XML tree when processing parallel path formulas
- Detects `../` prefix in XPath expressions
- Navigates to parent element and searches from there
- Enables access to sibling elements for area calculations

**Use Case:**
- Basement walls store height in `Wall/Measurements/@height`
- Basement perimeter stored in `Basement/Floor/Measurements/@perimeter`
- Wall area = height × perimeter requires accessing sibling Floor element

#### Gross Wall Area Formula

Calculates total above-grade wall area for NBC compliance forms by summing all wall components:

```json
{
  "formulas": {
    "gross_wall_area": {
      "description": "Calculate total above-grade wall area in m²",
      "inputs": {
        "pony_wall": ".//AllResults/Results/Other/GrossArea",
        "main_walls": ".//AllResults/Results/Other/GrossArea/MainFloors",
        "basement_above_grade": ".//AllResults/Results/Other/GrossArea/Basement",
        "basement_floor_header": ".//AllResults/Results/Other/GrossArea/Basement",
        "crawlspace_wall": ".//AllResults/Results/Other/GrossArea/Crawlspace",
        "crawlspace_floor_header": ".//AllResults/Results/Other/GrossArea/Crawlspace"
      },
      "input_attrs": {
        "pony_wall": "ponyWall",
        "main_walls": "mainWalls",
        "basement_above_grade": "aboveGrade",
        "basement_floor_header": "floorHeader",
        "crawlspace_wall": "wall",
        "crawlspace_floor_header": "floorHeader"
      },
      "calculation": "pony_wall + main_walls + basement_above_grade + basement_floor_header + crawlspace_wall + crawlspace_floor_header",
      "format": "%.1f"
    }
  }
}
```

**Wall Components:**
- **ponyWall**: Walk-out/daylight basement pony walls above grade
- **mainWalls**: Main floor exterior walls above grade
- **basement aboveGrade**: Exposed basement walls above grade
- **basement floorHeader**: Rim joists at basement ceiling
- **crawlspace wall**: Crawlspace perimeter walls
- **crawlspace floorHeader**: Rim joists at crawlspace ceiling

All components are present in 100% of H2K files (verified across 39 archetype files). Components are set to 0.0 when not applicable (e.g., no pony wall in full basement homes, no crawlspace in slab-on-grade).

#### Total Fenestration and Door Area Formula

Calculates total fenestration and door area including both main floors and basement:

```json
{
  "formulas": {
    "total_window_door_area": {
      "description": "Calculate total fenestration and door area in m²",
      "inputs": {
        "window_se": ".//AllResults/Results/Other/GrossArea/MainFloors/Windows/SouthEast",
        "window_ne": ".//AllResults/Results/Other/GrossArea/MainFloors/Windows/NorthEast",
        "window_nw": ".//AllResults/Results/Other/GrossArea/MainFloors/Windows/NorthWest",
        "window_sw": ".//AllResults/Results/Other/GrossArea/MainFloors/Windows/SouthWest",
        "window_s": ".//AllResults/Results/Other/GrossArea/MainFloors/Windows/South",
        "window_n": ".//AllResults/Results/Other/GrossArea/MainFloors/Windows/North",
        "window_e": ".//AllResults/Results/Other/GrossArea/MainFloors/Windows/East",
        "window_w": ".//AllResults/Results/Other/GrossArea/MainFloors/Windows/West",
        "door_main": ".//AllResults/Results/Other/GrossArea/MainFloors/Door",
        "door_basement": ".//AllResults/Results/Other/GrossArea/Basement/Door",
        "basement_window_[8 orientations]": ".//AllResults/Results/Other/GrossArea/Basement/Windows/[Orientation]"
      },
      "input_attrs": {
        "[all inputs]": "grossArea"
      },
      "calculation": "sum of all window and door areas",
      "format": "%.1f"
    }
  }
}
```

**Fenestration Components:**
- 8 main floor window orientations (S, SE, E, NE, N, NW, W, SW)
- 8 basement window orientations (S, SE, E, NE, N, NW, W, SW)
- Main floor doors
- Basement doors

Formula correctly handles buildings with or without basement windows (0.0 when absent).

#### FDWR Percentage Formula

Calculates the Fenestration and Door to Wall Ratio as a percentage by dividing total fenestration area by gross wall area:

```json
{
  "formulas": {
    "fdwr_percentage_comprehensive": {
      "description": "Calculate FDWR percentage (fenestration and door to wall ratio)",
      "inputs": {
        "[18 fenestration inputs]": "all window and door components",
        "[6 wall inputs]": "all wall components"
      },
      "calculation": "((total_fenestration) / (total_wall)) * 100 if total_wall > 0 else 0",
      "format": "%.1f"
    }
  }
}
```

**Formula Details:**
- Combines all inputs from `total_window_door_area` (18 components) and `gross_wall_area` (6 components)
- Calculates: **(Fenestration Area / Wall Area) × 100**
- Includes division-by-zero protection (returns 0 if wall area is 0)
- Used by fields:
  - **T3_R1_C4** (Proposed FDWR in Table 3)
  - **T5_R19_C1** (Reference FDWR in Table 5)
  - **T5_R19_C2** (Proposed FDWR in Table 5)

**Example Results:**
- Full basement (1000 sf): 22.2 m² / 107.9 m² = 20.6% FDWR
- Crawlspace (1900 sf): 15.9 m² / 228.5 m² = 6.9% FDWR
- Slab on grade (2100 sf): 37.1 m² / 292.1 m² = 12.7% FDWR
- Proposed model (test): 31.5 m² / 270.2 m² = 11.7% FDWR

### 4. Complex Mappings

Complex mappings combine multiple H2K values into formatted strings and support conditional conversions based on attribute values.

#### Basic Complex Mapping Example

```json
{
  "complex_mappings": {
    "heating_system": {
      "description": "Format heating system description",
      "components": [
        {
          "xpath": ".//House/HeatingCooling/Type1/Furnace/Equipment/EnergySource/English",
          "default": "Unknown fuel"
        },
        {
          "xpath": ".//House/HeatingCooling/Type1/Furnace/Equipment/EquipmentType/English",
          "default": "Unknown type"
        },
        {
          "xpath": ".//House/HeatingCooling/Type1/Furnace/Specifications",
          "attr": "efficiency",
          "default": "0"
        }
      ],
      "format": "{0} {1}, {2}% AFUE"
    }
  }
}
```
*Output example: "Natural gas Condensing, 96.1% AFUE"*

#### Complex Mapping with Conditional Conversion

For heat pump systems, heating efficiency may be stored as either COP or HSPF depending on the `isCop` attribute. The system supports conditional conversion:

```json
{
  "complex_mappings": {
    "heating_system_with_hp": {
      "description": "Format heating system with optional heat pump",
      "components": [
        {
          "xpath": ".//House/HeatingCooling/Type1/Furnace/Equipment/EnergySource/English",
          "default": "Unknown"
        },
        {
          "xpath": ".//House/HeatingCooling/Type1/Furnace/Equipment/EquipmentType/English",
          "default": "furnace"
        },
        {
          "xpath": ".//House/HeatingCooling/Type1/Furnace/Specifications",
          "attr": "efficiency",
          "default": "0"
        },
        {
          "xpath": ".//House/HeatingCooling/Type2/AirHeatPump/Equipment/Type/English",
          "default": "",
          "optional": true
        },
        {
          "xpath": ".//House/HeatingCooling/Type2/AirHeatPump/Specifications/HeatingEfficiency",
          "attr": "value",
          "check_attr": "isCop",
          "conversion": "cop_to_hspf_conditional",
          "default": "",
          "optional": true
        }
      ],
      "format": "{0} {1}, {2}% AFUE; {3} HSPF {4}",
      "format_simple": "{0} {1}, {2}% AFUE"
    }
  }
}
```

**Conditional Conversion Logic:**
- `check_attr: "isCop"` - Reads the `isCop` attribute from the HeatingEfficiency element
- `conversion: "cop_to_hspf_conditional"` - Applies conversion if needed:
  - If `isCop="true"`: Value is COP, convert to HSPF using: **HSPF = (COP - 0.78) / 0.376**
  - If `isCop` is not "true": Value is already HSPF, use as-is
- Always displays result as HSPF in the output

**Example Results:**
- H2K stores `isCop="true" value="3.45"` → Converts to "HSPF 7.10"
- H2K stores `isCop="false" value="7.13"` → Uses directly as "HSPF 7.13"

**Optional Components:**
- Components marked `"optional": true` may not exist in all H2K files
- If optional components are absent, uses `format_simple` instead of `format`
- Example: Furnace-only systems use simple format without heat pump details

### 5. Transformations

```json
{
  "transformations": {
    "r_to_u": {
      "type": "calculation",
      "formula": "1/x",
      "format": "%.2f"
    },
    "climate_zone": {
      "type": "lookup",
      "ranges": [
        {"min": 0, "max": 2999, "value": "Zone 4 (<3000 HDD)"},
        {"min": 3000, "max": 3999, "value": "Zone 5 (3000-3999 HDD)"},
        {"min": 4000, "max": 4999, "value": "Zone 6 (4000-4999 HDD)"},
        {"min": 5000, "max": 5999, "value": "Zone 7A (5000-5999 HDD)"},
        {"min": 6000, "max": 9999, "value": "Zone 7B (≥6000 HDD)"}
      ]
    },
    "orientation_abbrev": {
      "type": "map",
      "mapping": {
        "North": "N",
        "NorthEast": "NE",
        "East": "E",
        "SouthEast": "SE",
        "South": "S",
        "SouthWest": "SW",
        "West": "W",
        "NorthWest": "NW"
      }
    }
  }
}
```

## Current Field Coverage

**Status**: 137 of 137 fields mapped (100%)
- **Real extractions**: 82 fields with H2K data (78 unique + 4 FDWR/wall/window area fields in Tables 3 and 5)
- **Placeholders**: 55 fields extracting "HOT2000" for manual completion

### Fully Mapped Sections

**Table 0 - Project Information** (4 fields)
- Project name, address
- Applicant name, address

**Table 1 - Climate Zone** (1 field)
- Climate zone calculated from heating degree days

**Table 3 - FDWR & Wall Areas** (3 fields)
- Total fenestration and door area (T3_R1_C0) - sum of all windows and doors
- Gross above-grade wall area (T3_R1_C2) - includes pony walls, main walls, basement above-grade, floor headers, and crawlspace walls
- FDWR percentage (T3_R1_C4) - calculated as (fenestration area / wall area) × 100

**Table 5 - Building Envelope** (Selected fields)
- Front orientation (T5_R13_C1)
- FDWR percentage (T5_R19_C1 Reference, T5_R19_C2 Proposed) - calculated using comprehensive formula
- **Ceilings below attics RSI** (T5_R2_C2, T5_R2_C3) - Type-filtered for Attic/gable and Attic/hip
- **Cathedral ceilings and flat roofs RSI** (T5_R3_C2, T5_R3_C3) - Type-filtered for Cathedral and Flat
- **Walls above grade RSI** (T5_R4_C2, T5_R4_C3) - Parallel path method
- Below-grade walls RSI (T5_R6_C2, T5_R6_C3)
- **Unheated floors below frost line RSI** (T5_R7_C3, T5_R7_C4) - Attribute-filtered, AddedToSlab insulation
- **Unheated floors above frost line RSI** (T5_R8_C3, T5_R8_C4) - Attribute-filtered, AddedToSlab insulation
- Heated/unheated floors on permafrost (T5_R9_C2, T5_R9_C3) - Placeholder for manual completion
- Window U-value (T5_R14_C2, T5_R14_C3) - Parallel path method
- **Skylight U-value** (T5_R16_C2, T5_R16_C3) - Parallel path method, returns "N/A" if no skylights
- **Skylight SHGC** (T5_R17_C3) - Weighted average, returns "N/A" if no skylights
- **Door U-value** (T5_R18_C1, T5_R18_C2) - Parallel path method for exterior doors only
- Airtightness (T5_R20_C1, T5_R20_C2)
- Heating system descriptions (T5_R25_C1, T5_R25_C2)
- Ventilation system (T5_R31_C2)
- DHW system (T5_R37_C1, T5_R37_C2)

**Table 6 - Airtightness Target** (1 field)
- ACH @ 50 Pa target value

**Table 11 - Energy Performance** (2 fields)
- Annual energy consumption (GJ) for reference and proposed

**Table 13 - Professional Information** (5 fields)
- Modeler name, phone, accreditation
- Evaluation date

**Table 14 - Reference Specifications** (12 fields)
- Building details (floor area, stories, orientation)
- Envelope specifications
- Equipment types and efficiencies

### Placeholder Fields (55 fields)

Placeholder fields are mapped to extract `.//Application/Name` which returns "HOT2000". These fields appear in the generated document with "HOT2000" as the value, making them easy to identify for manual completion.

Sections with placeholders include:
- Table 5: Additional envelope details, window orientations
- Table 12-13: Some professional certification fields
- Table 16-17: Designer declarations and signatures

## Key Extracted Values (Examples)

From the example H2K files (`reference.h2k` and `proposed.h2k`):

**Building Envelope (Table 5)**:
- Walls: 2.97 RSI (Ref) → 3.19 RSI (Prop)
- Ceiling: 8.67 RSI (Ref) → 9.16 RSI (Prop)
- Exposed Floor: 4.67 RSI (Ref) → 5.04 RSI (Prop)
- Window U-value: 1.60 (Ref) → 1.40 (Prop)

**Wall Areas & Fenestration (Tables 3 & 5)**:
- Fenestration & door area: 31.5 m² (Proposed) / 45.9 m² (Reference)
- Gross wall area: 270.2 m² (both models)
  - Pony wall: 43.1 m²
  - Main walls: 217.7 m²
  - Basement above grade: 1.1 m²
  - Basement floor header: 8.3 m²
- **FDWR%:**
  - **T3_R1_C4 (Table 3 Proposed): 11.7%**
  - **T5_R19_C1 (Table 5 Reference): 17.0%**
  - **T5_R19_C2 (Table 5 Proposed): 11.7%**

**Energy Performance (Table 11)**:
- Reference: ~78 GJ/year
- Proposed: ~52 GJ/year

## Adding New Field Mappings

To map a currently placeholder field:

1. **Identify the NBC field** from `form_template_fields.json`
   - Example: `T5_R26_C3` for DHW tank insulation

2. **Find the data in H2K file** using XPath
   - Open `.h2k` file in text editor
   - Navigate XML structure to find desired element
   - Test XPath with `h2k_extractor.py`

3. **Update mapping in configuration**
   ```json
   {
     "nbc_field": "T5_R26_C3",
     "description": "DHW tank insulation RSI",
     "source": "proposed",
     "xpath": ".//House/Components/HotWater/TankInsulation",
     "xpath_attr": "rValue",
     "transform": "round2",
     "default": ""
   }
   ```

4. **Test extraction**
   ```bash
   python process_h2k_to_nbc.py reference.h2k proposed.h2k test_output.docx
   ```

5. **Verify in output document**
   - Open `test_output.docx`
   - Check field shows extracted value instead of "HOT2000"

## Form Template Generation

The form template is created from the official NBC form using a one-time setup process:

### Step 1: Build Fillable Template (One-Time Setup)

**Script**: `util/build_fillable_form.py`

```bash
cd C:/HTAP
python util/build_fillable_form.py
```

**Process**:
1. Opens official `form.docx` as ZIP archive
2. Extracts and parses `word/document.xml` with namespace-aware ElementTree
3. Identifies all cells with light blue fill (`w:shd w:fill="DEEAF6"`)
4. Replaces cell content with placeholder tokens `{{T#_R#_C#}}`
5. Captures row/column labels for field mapping
6. Writes `form_template.docx` and `form_template_fields.json`

**When to run**: Only when official `form.docx` is updated with new NBC requirements

### Step 2: Fill Template with Data

**Script**: `util/fill_form_dummy_data.py` (example) or `process_h2k_to_nbc.py` (production)

The fill process:
1. Opens template, extracts `word/document.xml`
2. Performs string substitution: `{{FIELD_ID}}` → actual value
3. XML-escapes values to handle special characters
4. Writes completed form to output file

## Testing Individual Components

### Test Configuration Loading
```bash
cd complianceReporting
python config_loader.py h2k_to_nbc_mapping.json
```

### Test H2K Extraction
```python
from h2k_extractor import H2KExtractor
ext = H2KExtractor('proposed.h2k')
value = ext.extract_by_xpath('.//House/Components/Ceiling/Construction/CeilingType', 'rValue')
print(f'Ceiling R-value: {value}')
```

### Test Transformations
```python
from transformations import ValueTransformer
transformer = ValueTransformer()
u_value = transformer.transform('r_to_u', '9.16')
print(f'U-value: {u_value}')  # Output: 0.11
```

### Test Formula Processing
```bash
cd complianceReporting
python formula_processor.py h2k_to_nbc_mapping.json proposed.h2k
```

## Integration with HTAP Workflow

### Current Status
The form generation system is fully functional and ready for integration with HTAP simulation workflows.

### Integration Examples

**Option 1: Post-Processing Script**
```ruby
# In htap-prm.rb or custom script

# After HTAP run completes
reference_h2k = "output/NBC_reference.h2k"
proposed_h2k = "output/NBC_proposed.h2k"

# Generate compliance form
system("python complianceReporting/process_h2k_to_nbc.py #{reference_h2k} #{proposed_h2k} output/NBC_compliance.docx")
```

**Option 2: Batch Processing**
```ruby
# Process multiple buildings
buildings = ['house_A', 'house_B', 'house_C']

buildings.each do |building|
  ref = "output/#{building}_reference.h2k"
  prop = "output/#{building}_proposed.h2k"
  out = "output/#{building}_NBC_compliance.docx"

  system("python complianceReporting/process_h2k_to_nbc.py #{ref} #{prop} #{out}")
end
```

**Option 3: Integration Module**
```ruby
# In substitute-h2k.rb or new compliance module

def generate_nbc_compliance_form(reference_path, proposed_path, output_path)
  # Validate input files exist
  unless File.exist?(reference_path) && File.exist?(proposed_path)
    puts "Error: H2K files not found"
    return false
  end

  # Call Python processor
  cmd = "python complianceReporting/process_h2k_to_nbc.py #{reference_path} #{proposed_path} #{output_path}"
  success = system(cmd)

  if success
    puts "Generated NBC compliance form: #{output_path}"
  else
    puts "Error generating compliance form"
  end

  success
end
```

## Technical Details

### Document Format (Office Open XML)
- `.docx` files are ZIP archives containing XML files
- Primary content in `word/document.xml`
- All other files (styles, relationships, theme) copied unchanged
- Only `document.xml` is modified during fill process

### Light Blue Cell Marker
- XML attribute: `<w:shd w:fill="DEEAF6"/>`
- Color code: `#DEEAF6` (light blue)
- Identifies data cells vs. static form content
- Automatically detected by `build_fillable_form.py`

### Placeholder Format
- Pattern: `{{FIELD_ID}}` (double braces)
- Simple text tokens, not Word fields
- Enables straightforward string substitution
- Unlikely to collide with real building data

### XML Special Character Handling
- Values are XML-escaped using `xml.sax.saxutils.escape()`
- Handles: `<`, `>`, `&`, apostrophes, quotes
- Example: `"Owner's Name"` → `"Owner&apos;s Name"`

### Namespace Preservation
- Must register all XML namespaces before parsing
- Ensures `w:`, `wp:`, `r:` prefixes preserved in output
- Without this, ElementTree uses full namespace URIs
- Handled by `load_namespaces()` function in template scripts

## Troubleshooting

### Problem: Field Not Extracting

**Diagnostic Steps**:
1. Verify XPath is correct:
   ```python
   from h2k_extractor import H2KExtractor
   ext = H2KExtractor('proposed.h2k')
   value = ext.extract_by_xpath('.//your/xpath', 'attribute_name')
   print(f'Value: {value}')
   ```

2. Check if element exists:
   ```python
   exists = ext.element_exists('.//your/xpath')
   print(f'Exists: {exists}')
   ```

3. View all matching elements:
   ```python
   values = ext.extract_all_by_xpath('.//your/xpath', 'attribute_name')
   print(f'All values: {values}')
   ```

**Common Causes**:
- Incorrect XPath expression (typo, wrong hierarchy)
- Missing data in H2K file (element doesn't exist)
- Missing attribute specification (forgot `xpath_attr`)
- Wrong data source (should be 'reference' not 'proposed')

### Problem: Configuration Validation Errors

Run the configuration validator:
```bash
python config_loader.py h2k_to_nbc_mapping.json
```

This reports:
- Missing required keys in field mappings
- Invalid source values (must be 'reference' or 'proposed')
- Undefined formula/transformation references
- Malformed JSON structure

### Problem: Empty Form Fields

Check console output during processing - it shows extraction summary with empty fields. Common causes:
- Incorrect XPath expression
- Missing data in H2K file
- Transformation error (check transformation definition)
- Missing attribute specification
- Wrong table column (C2 vs C3 confusion)

### Problem: Placeholders Not Replaced

**Symptoms**: Output shows `{{T5_R3_C3}}` instead of actual value

**Solutions**:
- Verify field ID matches exactly (case-sensitive)
- Check field exists in `h2k_to_nbc_mapping.json`
- Ensure no typos in field coordinates
- Verify extraction returned non-empty value

### Problem: XML Corruption in Output

**Symptoms**: Word cannot open output file

**Solutions**:
- Verify values are properly XML-escaped
- Check for unescaped `<`, `>`, `&` characters
- Ensure `xml.sax.saxutils.escape()` used on all values
- Verify only `document.xml` is modified, all other ZIP entries copied unchanged

### Problem: Formatting Lost in Output

**Solutions**:
- Ensure only `document.xml` is modified
- Verify all other ZIP entries copied unchanged
- Check namespace preservation in XML parsing
- Don't use Word "Save As" - extract from ZIP manually if needed

## Maintenance

### Updating the Official Form

When NBC updates the compliance form:

1. **Replace official form**
   - Save new official form as `complianceReporting/form.docx`
   - Ensure data cells marked with light blue fill (`#DEEAF6`)

2. **Regenerate template**
   ```bash
   cd C:/HTAP
   python util/build_fillable_form.py
   ```

3. **Review field mapping**
   - Open `complianceReporting/form_template_fields.json`
   - Check for new/changed/removed fields
   - Update `h2k_to_nbc_mapping.json` accordingly

4. **Test with example data**
   ```bash
   cd complianceReporting
   python process_h2k_to_nbc.py reference.h2k proposed.h2k test_output.docx
   ```

5. **Update field count in metadata**
   - Edit `h2k_to_nbc_mapping.json` metadata section
   - Update `fields_total` and increment version

### Adding New Transformations

Edit `h2k_to_nbc_mapping.json` transformations section:

```json
{
  "transformations": {
    "my_transform": {
      "type": "map",
      "mapping": {
        "input_value_1": "output_value_1",
        "input_value_2": "output_value_2"
      }
    }
  }
}
```

Use in field mapping:
```json
{
  "nbc_field": "T5_R25_C1",
  "transform": "my_transform"
}
```

### Adding New Formulas

Define formula in configuration:

```json
{
  "formulas": {
    "my_calculation": {
      "description": "Calculate my custom metric",
      "source": "proposed",
      "inputs": {
        "input1": ".//xpath/to/value1",
        "input2": ".//xpath/to/value2"
      },
      "input_attrs": {
        "input1": "attr_name",
        "input2": "attr_name"
      },
      "calculation": "(input1 + input2) / 2",
      "format": "%.2f"
    }
  }
}
```

Use in field mapping:
```json
{
  "nbc_field": "T14_R5_C4",
  "formula": "my_calculation"
}
```

## Dependencies

- **Python 3.7+** (tested with 3.7-3.12)
- **Standard library only**:
  - `xml.etree.ElementTree` - XML parsing
  - `zipfile` - DOCX manipulation
  - `json` - Configuration loading
  - `pathlib` - File path handling
  - `xml.sax.saxutils` - XML escaping
- **No external packages required**

## Performance

- **Processing time**: ~1-2 seconds for typical building
- **Memory usage**: < 50 MB
- **Batch processing**: Can process hundreds of buildings sequentially

## Limitations

1. **Manual completion required**: 55 placeholder fields need manual entry
2. **Single window type**: Currently uses overall average window U-value, not per-orientation
3. **Equipment descriptions**: Some complex equipment configurations may need manual adjustment
4. **No validation**: Extracted values not validated against NBC requirements
5. **Word-only output**: No PDF generation (requires Word or compatible software)

## Future Enhancements

Potential improvements:
1. Map remaining 55 placeholder fields with real H2K data
2. Add validation rules for extracted values (range checks, required fields)
3. Support for per-orientation window specifications
4. Generate comparison report (reference vs. proposed side-by-side)
5. Add PDF export option
6. Support for batch processing with summary report
7. Error reporting and data quality checks
8. Integration with HTAP run definitions (.run files)

## Recent Enhancements

### v3.4 (2025-11-05)

**COP to HSPF Conversion** - Added conditional unit conversion for heat pump efficiency:
- Reads `isCop` attribute from HeatingEfficiency element
- If `isCop="true"`: Converts COP to HSPF using formula: **HSPF = (COP - 0.78) / 0.376**
- If `isCop` is not "true": Uses value directly as HSPF
- Applied to T5_R25_C1 (Reference) and T5_R25_C2 (Proposed) heating system descriptions
- Ensures consistent HSPF reporting regardless of how HOT2000 stores the value
- Enhanced `h2k_extractor.py` to read multiple attributes from same element
- Enhanced `formula_processor.py` with conditional conversion processing

### v3.3 (2025-11-04)

**Skylight Support** - Added parallel path RSI and weighted average SHGC calculations for skylights:
- T5_R16_C2/C3: Skylight U-values using parallel path method
- T5_R17_C3: Skylight SHGC using weighted average
- Skylights identified by location (Window elements under Ceiling/Components)
- Returns "N/A" when no skylights present in building

**Door Support** - Added parallel path RSI calculation for exterior doors:
- T5_R18_C1/C2: Door U-values for exterior doors only
- Filters by `adjacentEnclosedSpace="false"` to exclude garage/porch doors
- Searches both Wall and Basement door locations
- Returns "N/A" when no exterior doors present (theoretical)

**Improved N/A Handling** - Enhanced treatment of absent building components:
- N/A values preserved throughout processing pipeline
- Skip transformations and formatting for N/A values
- Clearly distinguishes absent components from uninsulated components (0.00)
- Applied to ceilings, floors, skylights, and doors

## Related HTAP Components

- **H2K files** - HOT2000 building models (XML format)
- **substitute-h2k.rb** - Main transformation engine
- **htap-prm.rb** - Batch processing manager
- **HTAP-options.json** - Master upgrade catalog

## References

- **NBC 2020**: National Building Code of Canada, Subsection 9.36 (Energy Efficiency)
- **HOT2000**: NRCan's energy modeling software
- **Office Open XML**: https://docs.microsoft.com/en-us/office/open-xml/
- **Python zipfile**: https://docs.python.org/3/library/zipfile.html
- **ElementTree**: https://docs.python.org/3/library/xml.etree.elementtree.html

## Support

For issues or questions:
- Check `complianceReporting/README.md` for user guide
- Review configuration examples in `h2k_to_nbc_mapping.json`
- Test individual components using scripts in `complianceReporting/`
- Examine example files: `reference.h2k`, `proposed.h2k`
