# NBC 2020 Compliance Form - Table Structure Mapping

## Overview
Original form has **9 tables** (not 15). The key is using complex cell merging (gridSpan for colspan, vMerge for rowspan) within single large tables, NOT creating multiple separate tables.

## All Tables Summary

| Table | Columns | Rows | Description |
|-------|---------|------|-------------|
| 1 | 3 | 5 | Project Information Header |
| 2 | 6 | 4 | Building Information |
| 3 | 7 | 9 | Compliance Path Selection |
| 4 | 9 | 40 | D.1 Performance Compliance (CRITICAL) |
| 5 | 4 | 5 | Additional Information |
| 6 | 8 | 11 | Performance Energy Modeling Professional |
| 7 | 19 | 51 | D.2 Effective Thermal Resistance (CRITICAL) |
| 8 | 1 | 2 | Tiered Energy Compliance |
| 9 | 6 | 5 | Designer Declaration |

## Table 4: D.1 Performance Compliance (9 columns × 40 rows)

### Grid Structure
- **9 columns total** with equal widths
- Uses extensive gridSpan (horizontal merging)
- Uses vMerge="restart" and vMerge=null for vertical merging

### Row-by-Row Breakdown

**Row 0: Header Row**
- Cell 0: gridSpan=7, text="Input Parameters"
- Cell 1: gridSpan=1, text="Reference Model"
- Cell 2: gridSpan=1, text="Proposed Model"
- **Total: 3 cells spanning 9 columns (7+1+1)**

**Row 1: Section Header**
- Cell 0: gridSpan=7, text="Opaque Assemblies"
- Cell 1: gridSpan=2, text="Effective Thermal Resistance (RSI)"
- **Total: 2 cells spanning 9 columns (7+2)**

**Row 2: Above-ground section start**
- Cell 0: gridSpan=1, vMerge=restart, text="Above-ground"
- Cell 1: gridSpan=6, text="Ceilings below attics"
- Cell 2: gridSpan=1, text="" (input field)
- Cell 3: gridSpan=1, text="" (input field)
- **Total: 4 cells spanning 9 columns (1+6+1+1)**
- **Note: Cell 0 has vMerge=restart - starts vertical merge**

**Row 3-5: Continuation of Above-ground**
- Cell 0: gridSpan=1, vMerge=null, text="" (vertically merged with Row 2)
- Cell 1: gridSpan=6, text="Cathedral ceilings...", "Walls", "Floors..."
- Cell 2: gridSpan=1, text=""
- Cell 3: gridSpan=1, text=""
- **Pattern repeats for 3 rows**

**Row 6: Below-Grade section start**
- Cell 0: gridSpan=1, vMerge=restart, text="Below-Grade or in Contact with Ground"
- Cell 1: gridSpan=6, text="Foundation walls"
- Cell 2: gridSpan=1, text=""
- Cell 3: gridSpan=1, text=""

**Row 7-8: Unheated floors subsection**
- Cell 0: gridSpan=1, vMerge=null, text="" (merged)
- Cell 1: gridSpan=3, vMerge=restart, text="Unheated floors"
- Cell 2: gridSpan=3, text="below/above frost line"
- Cell 3: gridSpan=1, text=""
- Cell 4: gridSpan=1, text=""
- **Total: 5 cells spanning 9 columns (1+3+3+1+1)**

### Key Patterns in Table 4
1. First column (Column 0) used for major section headers with vMerge
2. Columns 1-7 used for parameter descriptions (often gridSpan=6)
3. Last 2 columns (8-9) used for Reference/Proposed values
4. Complex nesting with sub-sections that have their own gridSpan patterns

## Table 7: D.2 Effective Thermal Resistance (19 columns × 51 rows)

### Grid Structure
- **19 columns total**
- Uses extensive gridSpan for climate zone headers
- Uses vMerge extensively for assembly type groupings

### Row-by-Row Breakdown (First 10 rows)

**Row 0: Title Row**
- Cell 0: gridSpan=19, text="Effective Thermal Resistance of Opaque Assemblies..."
- **Total: 1 cell spanning all 19 columns**

**Row 1: Major Headers**
- Cell 0: gridSpan=6, vMerge=restart, text="Assembly"
- Cell 1: gridSpan=12, text="Climate Zone"
- Cell 2: gridSpan=1, vMerge=restart, text="Proposed (min. effective RSI)"
- **Total: 3 cells spanning 19 columns (6+12+1)**

**Row 2: Climate Zone Sub-headers**
- Cell 0: gridSpan=6, vMerge=null (merged with Row 1)
- Cell 1: gridSpan=1, text="4"
- Cell 2: gridSpan=2, text="5"
- Cell 3: gridSpan=2, text="6"
- Cell 4: gridSpan=3, text="7A"
- Cell 5: gridSpan=1, text="7B"
- Cell 6: gridSpan=3, text="8"
- Cell 7: gridSpan=1, vMerge=null (merged with Row 1)
- **Total: 8 cells spanning 19 columns (6+1+2+2+3+1+3+1)**

**Row 3: Above-ground / Ceilings below attics (w/out HRV)**
- Cell 0: gridSpan=2, vMerge=restart, text="Above-ground"
- Cell 1: gridSpan=3, vMerge=restart, text="Ceilings below attics"
- Cell 2: gridSpan=1, text="w/out HRV"
- Cell 3: gridSpan=1, text="6.91"
- Cell 4: gridSpan=4, text="8.67"
- Cell 5: gridSpan=7, text="10.43"
- Cell 6: gridSpan=1, text="" (input)
- **Total: 7 cells spanning 19 columns (2+3+1+1+4+7+1)**

**Row 4: Ceilings below attics (w/ HRV)**
- Cell 0: gridSpan=2, vMerge=null (merged)
- Cell 1: gridSpan=3, vMerge=null (merged)
- Cell 2: gridSpan=1, text="w/ HRV"
- Cell 3: gridSpan=2, text="6.91"
- Cell 4: gridSpan=6, text="8.67"
- Cell 5: gridSpan=4, text="10.43"
- Cell 6: gridSpan=1, text="" (input)
- **Total: 7 cells spanning 19 columns**

### Key Patterns in Table 7
1. First 6 columns used for Assembly descriptions with complex merging
2. Columns 7-18 (12 columns) used for climate zone values with varying gridSpan
3. Last column (19) used for Proposed values
4. Heavy use of vMerge for assembly type groupings (Above-ground, Below-Grade, etc.)
5. Sub-rows for HRV variants with vMerge=null to continue merged cells

## Implementation Strategy

### Critical Requirements
1. **Single Table Creation**: Each section must be ONE table, not multiple tables
2. **Proper gridSpan**: Must calculate and set gridSpan for every merged cell
3. **Proper vMerge**: Use vMerge="restart" to start vertical merge, vMerge="continue" or null for continuation
4. **Correct Column Counts**:
   - Table 4: 9 columns
   - Table 7: 19 columns
5. **Row Cell Counts**: Must match exactly (varies per row due to gridSpan)

### docx Package Usage
```javascript
// For horizontal merge (colspan)
new TableCell({
  columnSpan: 7,  // spans 7 columns
  children: [new Paragraph("Text")]
})

// For vertical merge (rowspan)
// First cell (starts merge)
new TableCell({
  rowSpan: 4,  // spans 4 rows
  children: [new Paragraph("Text")]
})

// Subsequent rows - cells are omitted from merged columns
```

### Next Steps
1. Rewrite generateForm.js to create Table 4 with proper 9-column structure
2. Implement all row-by-row cell configurations with correct gridSpan/vMerge
3. Rewrite Table 7 with proper 19-column structure
4. Test with compareDocxStructure.js after each table
5. Iterate until zero structural differences
