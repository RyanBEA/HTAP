# NBC 2020 Compliance Form Generation from H2K Files

## Overview

This directory contains a configuration-driven system for automatically generating NBC 2020 Energy Compliance Forms from HOT2000 .h2k building model files. The system extracts data from reference and proposed building models and populates the official NBC compliance form template.

## Quick Start

```bash
# Navigate to the complianceReporting directory
cd C:/HTAP/complianceReporting

# Run the processor with your H2K files
python process_h2k_to_nbc.py reference.h2k proposed.h2k output.docx
```

This will:
1. Extract data from both H2K files
2. Apply transformations and calculations
3. Generate a completed NBC compliance form (.docx)

## Files and Structure

### Core Files

- **process_h2k_to_nbc.py** - Main processing script
- **h2k_to_nbc_mapping.json** - Configuration file defining all field mappings
- **config_loader.py** - Configuration file loader and validator
- **h2k_extractor.py** - H2K XML data extraction engine
- **transformations.py** - Value transformation functions
- **formula_processor.py** - Formula calculation engine

### Form Templates and Data

- **form_template.docx** - NBC compliance form template with placeholders
- **form_template_fields.json** - Field metadata (137 fields)
- **reference.h2k** - Example reference building model
- **proposed.h2k** - Example proposed building model

## Configuration File Structure

The `h2k_to_nbc_mapping.json` file drives the entire extraction and mapping process. It consists of:

### 1. Field Mappings

Each field mapping defines:
- **nbc_field**: NBC form field ID (e.g., `T5_R14_C2`)
- **description**: Human-readable description
- **source**: Data source (`reference` or `proposed`)
- **xpath**: XPath expression to locate data in H2K file
- **xpath_attr**: Optional attribute name to extract
- **transform**: Transformation to apply (e.g., `r_to_u`, `climate_zone`)
- **format**: Format string for output (e.g., `%.2f`)
- **default**: Default value if extraction fails

Example:
```json
{
  "nbc_field": "T5_R14_C2",
  "description": "Window U-value (Proposed)",
  "source": "proposed",
  "xpath": ".//House/Components/Wall/Components/Window/Construction/Type",
  "xpath_attr": "rValue",
  "transform": "r_to_u",
  "format": "%.2f",
  "default": ""
}
```

### 2. Formulas

Complex calculations like FDWR (Fenestration and Door to Wall Ratio):
```json
{
  "fdwr_calculation": {
    "description": "Calculate fenestration and door to wall ratio",
    "inputs": {
      "window_se": ".//AllResults/Results/Other/GrossArea/MainFloors/Windows/SouthEast",
      "wall_main": ".//AllResults/Results/Other/GrossArea/MainFloors"
    },
    "input_attrs": {
      "window_se": "grossArea",
      "wall_main": "mainWalls"
    },
    "calculation": "((window_se + ...) / wall_main) * 100",
    "format": "%.1f"
  }
}
```

### 3. Transformations

Value transformations applied to extracted data:
- **passthrough**: Return value as-is
- **concatenate**: Join multiple values
- **lookup**: Range-based lookup (e.g., HDD to climate zone)
- **map**: Dictionary-based mapping (e.g., "Southwest" → "SW")
- **calculation**: Apply formula to value
- **round**: Round to specified decimals

### 4. Complex Mappings

Multi-component formatting for complex descriptions:
```json
{
  "heating_system": {
    "description": "Format heating system description",
    "components": [
      {
        "xpath": ".//House/HeatingCooling/Type1/Furnace/Equipment/EnergySource/English",
        "default": "Unknown"
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
```

## Adding New Field Mappings

To add a new field mapping to the configuration:

1. **Identify the NBC field** from `form_template_fields.json`
   - Example: `T5_R20_C1` for ceiling insulation

2. **Find the data in H2K file** using XPath
   - Use `h2k_extractor.py` to test XPaths
   - Example: `.//House/Components/Ceiling/Construction/CeilingType`

3. **Add mapping to configuration**
   ```json
   {
     "nbc_field": "T5_R20_C1",
     "description": "Ceiling insulation RSI",
     "source": "proposed",
     "xpath": ".//House/Components/Ceiling/Construction/CeilingType",
     "xpath_attr": "rValue",
     "transform": "round2",
     "default": ""
   }
   ```

4. **Test the extraction**
   ```bash
   python process_h2k_to_nbc.py reference.h2k proposed.h2k test_output.docx
   ```

## Testing Individual Components

### Test Configuration Loading
```bash
python config_loader.py h2k_to_nbc_mapping.json
```

### Test H2K Extraction
```bash
python h2k_extractor.py proposed.h2k
```

### Test Formula Processing
```bash
python formula_processor.py h2k_to_nbc_mapping.json proposed.h2k
```

### Test Transformations
```bash
python transformations.py
```

## Key Extracted Fields

The current configuration extracts the following key fields:

**Project Information (Table 0)**
- Project name, address
- Applicant name, address

**Climate Zone (Table 1)**
- Calculated from heating degree days

**Building Envelope (Table 5)**
- Front orientation
- Window U-value
- FDWR percentage
- Wall and foundation RSI values
- Heating/cooling systems
- Ventilation system (HRV/ERV)
- Domestic hot water system

**Airtightness (Table 6)**
- ACH @ 50 Pa from blower door test

**Energy Performance (Table 11)**
- Annual energy consumption (GJ) for reference and proposed

**Professional Information (Table 13)**
- Modeler name, phone
- Evaluation date

## Extending the Configuration

### Adding a New Transformation

1. Edit `h2k_to_nbc_mapping.json` transformations section:
```json
{
  "transformations": {
    "my_transform": {
      "type": "map",
      "mapping": {
        "value1": "output1",
        "value2": "output2"
      }
    }
  }
}
```

2. Use in field mapping:
```json
{
  "nbc_field": "T5_R25_C1",
  "transform": "my_transform"
}
```

### Adding a New Formula

1. Define formula in configuration:
```json
{
  "formulas": {
    "my_calculation": {
      "inputs": {
        "input1": ".//xpath/to/value1",
        "input2": ".//xpath/to/value2"
      },
      "input_attrs": {
        "input1": "attr_name",
        "input2": "attr_name"
      },
      "calculation": "input1 + input2",
      "format": "%.2f"
    }
  }
}
```

2. Use in field mapping:
```json
{
  "nbc_field": "T5_R30_C1",
  "formula": "my_calculation"
}
```

## Troubleshooting

### Field Not Extracting

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

### Configuration Validation Errors

Run the configuration validator:
```bash
python config_loader.py h2k_to_nbc_mapping.json
```

This will report:
- Missing required keys
- Invalid field mappings
- Undefined formula/transformation references
- Other configuration issues

### Empty Form Fields

Check the data extraction summary in the console output to see which fields have empty values. Common causes:
- Incorrect XPath expression
- Missing data in H2K file
- Transformation error
- Missing attribute specification

## Output

The generated NBC compliance form (`*.docx`) contains:
- All mapped fields populated with extracted data
- Formatted values (percentages, decimals, etc.)
- System descriptions (heating, DHW, HRV)
- Calculated metrics (FDWR, energy consumption)

Open the generated `.docx` file in Microsoft Word or compatible software to review and manually complete any remaining fields not yet mapped in the configuration.

## Dependencies

- **Python 3.7+** (standard library only)
- No external packages required
- Uses built-in modules: `xml.etree.ElementTree`, `zipfile`, `json`, `pathlib`

## Future Enhancements

Potential improvements to the system:
1. Map remaining NBC form fields (currently 24 of 137 fields mapped)
2. Add validation rules for extracted values
3. Support for multiple window types (average or specific orientation)
4. Add error reporting and data quality checks
5. Generate comparison report (reference vs. proposed)
6. Support for batch processing multiple buildings

## See Also

- **doc/complianceReporting.md** - Detailed documentation of form generation system
- **util/build_fillable_form.py** - Template generation from official form
- **util/fill_form_dummy_data.py** - Form filling with test data
