const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
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

// Create Table 4 with correct 9-column structure
const table4 = new Table({
  columnWidths: [1040, 1040, 1040, 1040, 1040, 1040, 1040, 1040, 1040],  // 9 equal columns
  margins: { top: 50, bottom: 50, left: 100, right: 100 },
  rows: [
    // Row 0
    new TableRow({
      children: [
        createCell("Input Parameters", 7280, { bold: true, shading: "FFFFFF", colSpan: 7 }),
        createCell("Reference Model", 1040, { bold: true, shading: "FFFFFF", alignment: AlignmentType.CENTER }),
        createCell("Proposed Model", 1040, { bold: true, shading: "FFFFFF", alignment: AlignmentType.CENTER })
      ]
    }),

    // Row 1
    new TableRow({
      children: [
        createCell("Opaque Assemblies", 7280, { bold: true, shading: "E7E6E6", colSpan: 7 }),
        createCell("Effective Thermal Resistance (RSI)", 2080, { bold: true, shading: "E7E6E6", colSpan: 2, alignment: AlignmentType.CENTER })
      ]
    }),

    // Row 2
    new TableRow({
      children: [
        createCell("Above-ground", 1040, { bold: true, shading: "E7E6E6", rowSpan: 4 }),
        createCell("Ceilings below attics", 6240, { colSpan: 6 }),
        createCell("", 1040, { shading: "E7E6E6" }),
        createCell("", 1040, { shading: "E7E6E6" })
      ]
    }),

    // Row 3
    new TableRow({
      children: [
        createCell("Cathedral ceilings and flat roofs", 6240, { colSpan: 6 }),
        createCell("", 1040, { shading: "E7E6E6" }),
        createCell("", 1040, { shading: "E7E6E6" })
      ]
    }),

    // Row 4
    new TableRow({
      children: [
        createCell("Walls", 6240, { colSpan: 6 }),
        createCell("", 1040, { shading: "E7E6E6" }),
        createCell("", 1040, { shading: "E7E6E6" })
      ]
    }),

    // Row 5
    new TableRow({
      children: [
        createCell("Floors over unheated spaces", 6240, { colSpan: 6 }),
        createCell("", 1040, { shading: "E7E6E6" }),
        createCell("", 1040, { shading: "E7E6E6" })
      ]
    }),

    // Row 6
    new TableRow({
      children: [
        createCell("Below-Grade or in Contact with Ground", 1040, { bold: true, shading: "E7E6E6", rowSpan: 6 }),
        createCell("Foundation walls", 6240, { colSpan: 6 }),
        createCell("", 1040, { shading: "E7E6E6" }),
        createCell("", 1040, { shading: "E7E6E6" })
      ]
    }),

    // Row 7
    new TableRow({
      children: [
        createCell("Unheated floors", 3120, { rowSpan: 2, colSpan: 3 }),
        createCell("below frost line", 3120, { colSpan: 3 }),
        createCell("", 1040, { shading: "E7E6E6" }),
        createCell("", 1040, { shading: "E7E6E6" })
      ]
    }),

    // Row 8
    new TableRow({
      children: [
        createCell("above frost line", 3120, { colSpan: 3 }),
        createCell("", 1040, { shading: "E7E6E6" }),
        createCell("", 1040, { shading: "E7E6E6" })
      ]
    }),

    // Row 9
    new TableRow({
      children: [
        createCell("Heated and unheated floors on permafrost", 6240, { colSpan: 6 }),
        createCell("", 1040, { shading: "E7E6E6" }),
        createCell("", 1040, { shading: "E7E6E6" })
      ]
    }),

    // Row 10
    new TableRow({
      children: [
        createCell("Heated floors", 6240, { colSpan: 6 }),
        createCell("", 1040, { shading: "E7E6E6" }),
        createCell("", 1040, { shading: "E7E6E6" })
      ]
    }),

    // Row 11
    new TableRow({
      children: [
        createCell("Slabs-on-grade with an integral footing", 6240, { colSpan: 6 }),
        createCell("", 1040, { shading: "E7E6E6" }),
        createCell("", 1040, { shading: "E7E6E6" })
      ]
    })
    // ... will add more rows for testing
  ]
});

// Create document
const doc = new Document({
  sections: [{
    children: [
      new Paragraph({ text: "Table 4 Test - D.1 Performance Compliance", bold: true }),
      table4
    ]
  }]
});

// Save
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("test_table4.docx", buffer);
  console.log("Test Table 4 generated: test_table4.docx");
});
