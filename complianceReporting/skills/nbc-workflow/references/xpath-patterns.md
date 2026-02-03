# XPath Patterns for NBC Compliance Classification

Reference XPaths used by `h2k_analyzer.py` to classify H2K files and determine the appropriate reference house run file.

## Equipment Classification

### Type1 Heating System

| Component | XPath | Returns |
|-----------|-------|---------|
| Furnace fuel | `.//HeatingCooling/Type1/Furnace/Equipment/EnergySource/English` | Natural gas, Electric, Propane, Oil |
| Boiler fuel | `.//HeatingCooling/Type1/Boiler/Equipment/EnergySource/English` | Natural gas, Electric, Propane, Oil |
| Baseboard | `.//HeatingCooling/Type1/Baseboards` | Element presence = electric baseboard |

**Classification logic:** Check furnace first, then boiler, then baseboard. First match determines fuel type.

### Type2 Heat Pump

| Component | XPath | Returns |
|-----------|-------|---------|
| ASHP presence | `.//HeatingCooling/Type2/AirHeatPump` | Element presence = has ASHP |
| HP type | `.//HeatingCooling/Type2/AirHeatPump/Equipment/Type/English` | Air source, Mini-split, etc. |

### Domestic Hot Water

| Component | XPath | Returns |
|-----------|-------|---------|
| DHW fuel | `.//Components/HotWater/Primary/EnergySource/English` | Natural gas, Electric, etc. |
| Alt path | `.//House/Components/HotWater/Primary/EnergySource/English` | Same (alternate location) |
| DWHR flag | `.//Components/HotWater/Primary@hasDrainWaterHeatRecovery` | true/false |

## Foundation Classification

### Configuration Types

| Component | XPath | Attribute | Typical Values |
|-----------|-------|-----------|----------------|
| Basement config | `.//Components/Basement/Configuration` | `type` | BCCB, BCIN, BCEB |
| Slab config | `.//Components/Slab/Configuration` | `type` | SCB, SCN |
| Crawlspace | `.//Components/Crawlspace` | - | Element presence |
| Walkout | `.//Components/Walkout` | - | Element presence |

**Configuration codes:**
- `BCCB` = Basement with concrete block
- `BCIN` = Basement with interior insulation
- `BCEB` = Basement with exterior insulation
- `SCB` = Slab on grade with concrete block
- `SCN` = Slab on grade (no stem wall)

### Foundation Details

| Component | XPath | Attribute | Returns |
|-----------|-------|-----------|---------|
| Below grade area | `.//Basement/Floor/Measurements` | `area` | Area in m2 |
| Frost line | `.//Basement/Floor/Construction` | `isBelowFrostline` | true/false |
| Footing type | `.//Basement/Configuration` | `type` | Config code |
| Heated floor | `.//Basement/Floor/Construction` | `heatedFloor` | true/false |
| Slab heated | `.//Slab/Floor/Construction` | `heatedFloor` | true/false |

## Manual Intervention Flags

| Flag | Detection XPath | Condition |
|------|-----------------|-----------|
| Pony wall | `.//Basement/Wall@hasPonyWall` | Attribute = "true" |
| DWHR | `.//HotWater/Primary@hasDrainWaterHeatRecovery` | Attribute = "true" |
| Skylights | `.//Ceiling/Components/Window` | Element count > 0 |
| Heated floors | `.//Basement/Floor/Construction@heatedFloor` | Attribute = "true" |

## Run File Selection Logic

The analyzer maps Type1 fuel to reference house run files:

| Normalized Fuel | Source Values | Run File |
|-----------------|---------------|----------|
| `gas` | Natural gas, Gas | `referencehouse_T1gasfurnace_T2ASHP.run` |
| `propane` | Propane | `referencehouse_T1gasfurnace_T2ASHP.run` |
| `electric` | Electric, Electricity, Baseboard | `referencehouse_T1elecfurnace_T2ASHP.run` |
| `oil` | Oil, Heating oil | Not yet supported (manual reference house creation required) |

**Note:** Propane uses the gas furnace run file as NBC treats propane similarly to natural gas for reference house equipment selection.

## Energy Source Normalization

The analyzer normalizes various H2K energy source strings to standard keys:

```
"natural gas" -> "gas"
"gas"         -> "gas"
"propane"     -> "propane"
"electric"    -> "electric"
"electricity" -> "electric"
"oil"         -> "oil"
"heating oil" -> "oil"
"wood"        -> "wood"
"wood pellets"-> "wood"
```
