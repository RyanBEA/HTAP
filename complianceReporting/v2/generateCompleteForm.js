const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, Header,
        AlignmentType, BorderStyle, WidthType, ShadingType, VerticalAlign } = require('docx');

// Border definitions
const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "000000" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

// Helper to create a cell with borders
function createCell(content, width, options = {}) {
  const {
    bold = false,
    shading = null,
    verticalAlign = VerticalAlign.TOP,
    alignment = AlignmentType.LEFT,
    colSpan = 1,
    rowSpan = 1,
    italics = false,
    size = 20
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

// Helper for superscript footnote markers
function footnoteRef(num) {
  return new TextRun({ text: num.toString(), superScript: true, size: 18 });
}

console.log("Loading table definitions from test files...");

//COMPREHENSIVE_END
echo "Created comprehensive form generator base (will continue building)"
