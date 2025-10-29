# NBC 2020 Energy Compliance Form Generation

## Overview
The compliance reporting system programmatically generates NBC 2020 Energy Compliance Forms as Word documents (.docx) using Node.js and the `docx` library. The system recreates complex multi-table compliance forms with precise formatting, cell merging, and layout matching the official NBC requirements.

## Location
- **Source Code**: `complianceReporting/v2/`
- **Original Form**: `complianceReporting/v2/form.docx`
- **Test Scripts**: `complianceReporting/v2/testRemainingTables.js`, `testTable4Complete.js`, `testTable7Complete.js`

## Form Structure
The NBC 2020 Energy Compliance Form consists of 9 tables:

1. **Table 1**: Project Information (3 cols × 5 rows)
2. **Table 2**: Project Design Conditions (6 cols × 4 rows)
3. **Table 3**: Compliance Option (7 cols × 9 rows) - Complex vertical merging
4. **Table 4**: D.1 Performance Compliance (9 cols × 40 rows)
5. **Table 5**: Additional Information (4 cols × 5 rows)
6. **Table 6**: Performance Energy Modeling Professional (8 cols × 11 rows)
7. **Table 7**: D.2 Effective Thermal Resistance (19 cols × 51 rows)
8. **Table 8**: Tiered Energy Compliance (1 col × 2 rows)
9. **Table 9**: Designer Declaration (6 cols × 5 rows)

## Generated Documents
- `test_remaining_tables.docx` - Tables 1, 2, 3, 5, 6, 8, 9
- `test_table4_complete.docx` - Table 4 only
- `test_table7_complete.docx` - Table 7 only

## Key Technical Concepts

### Cell Merging in docx Library
The `docx` npm package handles cell merging differently than manual XML editing:

**Horizontal Merging (columnSpan)**:
```javascript
createCell("Cell Text", colWidth, { columnSpan: 3 })
// Merges cell across 3 columns
// XML: <w:gridSpan w:val="3"/>
```

**Vertical Merging (rowSpan)**:
```javascript
// First row - initiates merge
createCell("Cell Text", colWidth, { rowSpan: 4 })
// Subsequent 3 rows - DO NOT include this cell position
// The docx library automatically handles vMerge continuation
```

**Critical Behavior**: When using `rowSpan`, subsequent rows should NOT define cells for the merged positions. The library handles the XML `vMerge` tags automatically.

### Column Width Calculations
Width units are in DXA (twentieths of a point):
- Full page width: 9360 DXA
- 7-column table: `colWidth = Math.floor(9360 / 7)` = 1337 DXA per column
- 19-column table: `colWidth = Math.floor(9360 / 19)` = 492 DXA per column

### Cell Styling
```javascript
const createCell = (text, width, options = {}) => {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    children: [new Paragraph({
      text: text,
      alignment: options.alignment || AlignmentType.LEFT
    })],
    columnSpan: options.columnSpan,
    rowSpan: options.rowSpan,
    borders: options.borders || defaultBorders
  });
};
```

## Validation Approach

### Structure Validation
Compare cell counts per row between test and original documents:

```javascript
// Extract XML from .docx (ZIP archive)
unzip -qo document.docx -d document_unpacked

// Parse and compare with xml2js
const testRows = testTable['w:tr'];
const origRows = origTable['w:tr'];

for (let i = 0; i < rows.length; i++) {
  const testCells = testRows[i]['w:tc'].length;
  const origCells = origRows[i]['w:tc'].length;
  // Compare counts
}
```

### Visual Validation
Open generated .docx files in Word/LibreOffice to verify:
- Cell alignment and text positioning
- Border styles and thickness
- Column widths and proportions
- Merged cell appearance

## Running the Generators

```bash
# Generate Tables 1, 2, 3, 5, 6, 8, 9
cd complianceReporting/v2
node testRemainingTables.js

# Generate Table 4
node testTable4Complete.js

# Generate Table 7
node testTable7Complete.js

# Validate structure
unzip -qo test_remaining_tables.docx -d test_unpacked
node analyzeRemainingTables.js
```

## Common Issues and Solutions

### Issue 1: Cell Count Mismatches
**Problem**: Row has wrong number of cells compared to original
**Cause**: Incorrect understanding of rowSpan behavior
**Solution**: When rowSpan is used, subsequent rows omit those cell positions

### Issue 2: Table Width Overflow
**Problem**: Table extends beyond page margins
**Cause**: Column widths exceed 9360 DXA total
**Solution**: Recalculate column widths: `Math.floor(9360 / columnCount)`

### Issue 3: Border Rendering
**Problem**: Borders appear incorrectly or missing
**Cause**: Incomplete border definitions
**Solution**: Define all four borders explicitly:
```javascript
borders: {
  top: { style: BorderStyle.SINGLE, size: 1, color: "000000" },
  bottom: { style: BorderStyle.SINGLE, size: 1, color: "000000" },
  left: { style: BorderStyle.SINGLE, size: 1, color: "000000" },
  right: { style: BorderStyle.SINGLE, size: 1, color: "000000" }
}
```

## Dependencies
```json
{
  "docx": "^8.x",
  "xml2js": "^0.6.x"
}
```

Install with:
```bash
cd complianceReporting/v2
npm install
```

## File Format Notes
- .docx files are ZIP archives containing XML
- Main content: `word/document.xml`
- Table structure: `<w:tbl>` → `<w:tr>` (rows) → `<w:tc>` (cells)
- Cell merging: `<w:gridSpan>` (horizontal), `<w:vMerge>` (vertical)

## Integration with HTAP
The compliance forms can be populated with data from HTAP simulation results:
- Energy performance metrics from HOT2000 output
- Component specifications from .h2k files
- Cost estimates from HTAPUnitCosts.json
- Designer information from project metadata

Future integration points:
- Auto-populate Table 4 from simulation results
- Extract thermal resistance values for Table 7
- Link project information from HTAP run definitions

## References
- **docx Library**: https://docx.js.org/
- **Office Open XML**: https://docs.microsoft.com/en-us/office/open-xml/
- **NBC 2020 Energy Compliance**: National Building Code of Canada, Subsection 9.36
