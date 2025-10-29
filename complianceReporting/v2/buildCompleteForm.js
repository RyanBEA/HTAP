const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, Header,
        AlignmentType, BorderStyle, WidthType, ShadingType, VerticalAlign } = require('docx');

// Border definitions
const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "000000" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

// Helper to create a cell
function createCell(content, width, options = {}) {
  const {
    bold = false, shading = null, verticalAlign = VerticalAlign.TOP,
    alignment = AlignmentType.LEFT, colSpan = 1, rowSpan = 1,
    italics = false, size = 20
  } = options;

  const children = typeof content === 'string'
    ? [new Paragraph({
        alignment: alignment,
        children: [new TextRun({ text: content, bold: bold, italics: italics, size: size })]
      })]
    : content;

  return new TableCell({
    borders: cellBorders,
    width: { size: width, type: WidthType.DXA },
    shading: shading ? { fill: shading, type: ShadingType.CLEAR } : undefined,
    verticalAlign: verticalAlign,
    columnSpan: colSpan,
    rowSpan: rowSpan,
    children: children
  });
}

function footnoteRef(num) {
  return new TextRun({ text: num.toString(), superScript: true, size: 18 });
}

// Import validated table generators
const table1Code = fs.readFileSync('testRemainingTables.js', 'utf8');
const table4Code = fs.readFileSync('testTable4Complete.js', 'utf8');
const table7Code = fs.readFileSync('testTable7Complete.js', 'utf8');

console.log("Building comprehensive form by extracting table definitions...");
console.log("This will parse and extract table structures from validated test files.");

// For now, create a simpler approach
console.log("");
console.log("Strategy: Use eval to extract table objects from test files");
console.log("This ensures we use the exact validated structures.");
