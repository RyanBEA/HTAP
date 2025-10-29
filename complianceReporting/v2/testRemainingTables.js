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

// TABLE 1: Project Information (3 columns × 5 rows)
const table1 = new Table({
  columnWidths: [3120, 3120, 3120],  // 3 equal columns
  margins: { top: 50, bottom: 50, left: 100, right: 100 },
  rows: [
    new TableRow({
      children: [
        createCell("The (name of jurisdiction) Requirements for Division B Subsection 9.36 Energy Efficiency - House",
                   9360, { bold: true, shading: "E7E6E6", colSpan: 3, alignment: AlignmentType.CENTER })
      ]
    }),
    new TableRow({
      children: [
        createCell("Project Name:", 3120, { bold: true }),
        createCell("", 3120, {}),
        createCell("Building Permit Number (Completed Internally)", 3120, { rowSpan: 4, shading: "E7E6E6" })
      ]
    }),
    new TableRow({
      children: [
        createCell("Project Address:", 3120, { bold: true }),
        createCell("", 3120, {})
      ]
    }),
    new TableRow({
      children: [
        createCell("Applicant Name:", 3120, { bold: true }),
        createCell("", 3120, {})
      ]
    }),
    new TableRow({
      children: [
        createCell("Applicant Address:", 3120, { bold: true }),
        createCell("", 3120, {})
      ]
    })
  ]
});

// TABLE 2: Project Design Conditions (6 columns × 4 rows)
const colWidth2 = 1560; // 9360 / 6
const table2 = new Table({
  columnWidths: [colWidth2, colWidth2, colWidth2, colWidth2, colWidth2, colWidth2],
  margins: { top: 50, bottom: 50, left: 100, right: 100 },
  rows: [
    new TableRow({
      children: [
        createCell("A. Project Design Conditions", 9360,
                  { bold: true, shading: "E7E6E6", colSpan: 6, alignment: AlignmentType.CENTER })
      ]
    }),
    new TableRow({
      children: [
        createCell("Zone 4 (< 3000)", colWidth2, { bold: true, shading: "E7E6E6", alignment: AlignmentType.CENTER }),
        createCell("Zone 5 (3000 to 3999)", colWidth2, { bold: true, shading: "E7E6E6", alignment: AlignmentType.CENTER }),
        createCell("Zone 6 (4000 to 4999)", colWidth2, { bold: true, shading: "E7E6E6", alignment: AlignmentType.CENTER }),
        createCell("Zone 7A (5000 to 5999)", colWidth2, { bold: true, shading: "E7E6E6", alignment: AlignmentType.CENTER }),
        createCell("Zone 7B (6000 to 6999)", colWidth2, { bold: true, shading: "E7E6E6", alignment: AlignmentType.CENTER }),
        createCell("Zone 8 (7000 to 7999)", colWidth2, { bold: true, shading: "E7E6E6", alignment: AlignmentType.CENTER })
      ]
    }),
    new TableRow({
      children: [
        createCell("Occupancy type", colWidth2 * 2, { bold: true, colSpan: 2 }),
        createCell("Floor area", colWidth2, { bold: true }),
        createCell("Fenestration and door area to gross wall ratio (FDWR)", colWidth2 * 3,
                  { bold: true, colSpan: 3 })
      ]
    }),
    new TableRow({
      children: [
        createCell("", colWidth2 * 2, { colSpan: 2 }),
        createCell("", colWidth2, {}),
        createCell("", colWidth2 * 3, { colSpan: 3 })
      ]
    })
  ]
});

// TABLE 3: Compliance Option (7 columns × 9 rows)
const colWidth3 = 1337; // 9360 / 7
const table3 = new Table({
  columnWidths: [colWidth3, colWidth3, colWidth3, colWidth3, colWidth3, colWidth3, colWidth3],
  margins: { top: 50, bottom: 50, left: 100, right: 100 },
  rows: [
    new TableRow({
      children: [
        createCell("B. Compliance Pathway", colWidth3 * 2,
                  { bold: true, shading: "E7E6E6", colSpan: 2, rowSpan: 2 }),
        createCell("Energy Performance Tier", colWidth3,
                  { bold: true, shading: "E7E6E6", rowSpan: 2, alignment: AlignmentType.CENTER }),
        createCell("Building Envelope Trade-Off?", colWidth3,
                  { bold: true, shading: "E7E6E6", rowSpan: 2, alignment: AlignmentType.CENTER }),
        createCell("Forms to Complete", colWidth3 * 3,
                  { bold: true, shading: "E7E6E6", colSpan: 3, alignment: AlignmentType.CENTER })
      ]
    }),
    new TableRow({
      children: [
        createCell("D1", colWidth3, { bold: true, shading: "E7E6E6", alignment: AlignmentType.CENTER }),
        createCell("D2", colWidth3, { bold: true, shading: "E7E6E6", alignment: AlignmentType.CENTER }),
        createCell("9.36 Submittal Calculator", colWidth3,
                  { bold: true, shading: "E7E6E6", alignment: AlignmentType.CENTER })
      ]
    }),
    new TableRow({
      children: [
        createCell("Prescriptive (Subsections 9.36.2-9.36.4, 9.36.8)", colWidth3, { rowSpan: 2 }),
        createCell("Tier 1", colWidth3, { rowSpan: 2, alignment: AlignmentType.CENTER }),
        createCell("No", colWidth3, { alignment: AlignmentType.CENTER }),
        createCell("", colWidth3, {}),
        createCell("√", colWidth3, { alignment: AlignmentType.CENTER }),
        createCell("", colWidth3, {})
      ]
    }),
    new TableRow({
      children: [
        createCell("", colWidth3, {}),
        createCell("Yes", colWidth3, { alignment: AlignmentType.CENTER }),
        createCell("", colWidth3, {}),
        createCell("√", colWidth3, { alignment: AlignmentType.CENTER }),
        createCell("√ (Trade-off tab)", colWidth3, { alignment: AlignmentType.CENTER })
      ]
    }),
    new TableRow({
      children: [
        createCell("", colWidth3, {}),
        createCell("Tier 2", colWidth3, { alignment: AlignmentType.CENTER }),
        createCell("Yes", colWidth3, { alignment: AlignmentType.CENTER }),
        createCell("-", colWidth3, { alignment: AlignmentType.CENTER }),
        createCell("", colWidth3, {}),
        createCell("√", colWidth3, { alignment: AlignmentType.CENTER }),
        createCell("√", colWidth3, { alignment: AlignmentType.CENTER })
      ]
    }),
    new TableRow({
      children: [
        createCell("Performance (Subsection 9.36.5, 9.36.7)", colWidth3, { rowSpan: 2 }),
        createCell("Tier 1", colWidth3, { alignment: AlignmentType.CENTER }),
        createCell("-", colWidth3, { alignment: AlignmentType.CENTER }),
        createCell("√", colWidth3, { alignment: AlignmentType.CENTER }),
        createCell("", colWidth3, {}),
        createCell("", colWidth3, {})
      ]
    }),
    new TableRow({
      children: [
        createCell("", colWidth3, {}),
        createCell("Tier 2", colWidth3, { alignment: AlignmentType.CENTER }),
        createCell("-", colWidth3, { alignment: AlignmentType.CENTER }),
        createCell("√", colWidth3, { alignment: AlignmentType.CENTER }),
        createCell("", colWidth3, {}),
        createCell("√", colWidth3, { alignment: AlignmentType.CENTER })
      ]
    }),
    new TableRow({
      children: [
        createCell("Additional information to be submitted for review", colWidth3 * 7,
                  { bold: true, shading: "E7E6E6", colSpan: 7 })
      ]
    }),
    new TableRow({
      children: [
        createCell("Attic hatch details, Eaves to top of wall transition details, etc.", colWidth3 * 3,
                  { colSpan: 3 }),
        createCell("Drawings, images, details", colWidth3 * 4, { colSpan: 4 })
      ]
    })
  ]
});

// TABLE 5: Additional Information (4 columns × 5 rows)
const colWidth5 = 2340; // 9360 / 4
const table5 = new Table({
  columnWidths: [colWidth5, colWidth5, colWidth5, colWidth5],
  margins: { top: 50, bottom: 50, left: 100, right: 100 },
  rows: [
    new TableRow({
      children: [
        createCell("Performance Software Calculations", colWidth5 * 4,
                  { bold: true, shading: "E7E6E6", colSpan: 4, alignment: AlignmentType.CENTER })
      ]
    }),
    new TableRow({
      children: [
        createCell("Software Title:", colWidth5, { bold: true }),
        createCell("", colWidth5, {}),
        createCell("Version:", colWidth5, { bold: true }),
        createCell("", colWidth5, {})
      ]
    }),
    new TableRow({
      children: [
        createCell("Is software HOT2000v11 or ANSI/ASHRAE 140 compliant?", colWidth5 * 2,
                  { bold: true, colSpan: 2 }),
        createCell("Yes / No", colWidth5 * 2, { colSpan: 2, alignment: AlignmentType.CENTER })
      ]
    }),
    new TableRow({
      children: [
        createCell("Annual Energy Consumption (GJ/yr):", colWidth5 * 2,
                  { bold: true, colSpan: 2 }),
        createCell("", colWidth5 * 2, { colSpan: 2 })
      ]
    }),
    new TableRow({
      children: [
        createCell("Notes:", colWidth5 * 4, { bold: true, colSpan: 4 })
      ]
    })
  ]
});

// TABLE 6: Performance Energy Modeling Professional (8 columns × 11 rows)
const colWidth6 = 1170; // 9360 / 8
const table6 = new Table({
  columnWidths: Array(8).fill(colWidth6),
  margins: { top: 50, bottom: 50, left: 100, right: 100 },
  rows: [
    new TableRow({
      children: [
        createCell("Performance Energy Modeling Professional", colWidth6 * 8,
                  { bold: true, shading: "E7E6E6", colSpan: 8, alignment: AlignmentType.CENTER })
      ]
    }),
    new TableRow({
      children: [
        createCell("Name:", colWidth6 * 2, { bold: true, colSpan: 2 }),
        createCell("", colWidth6 * 2, { colSpan: 2 }),
        createCell("Company:", colWidth6 * 2, { bold: true, colSpan: 2 }),
        createCell("", colWidth6 * 2, { colSpan: 2 })
      ]
    }),
    new TableRow({
      children: [
        createCell("Phone:", colWidth6 * 2, { bold: true, colSpan: 2 }),
        createCell("", colWidth6 * 2, { colSpan: 2 }),
        createCell("Email:", colWidth6 * 2, { bold: true, colSpan: 2 }),
        createCell("", colWidth6 * 2, { colSpan: 2 })
      ]
    }),
    new TableRow({
      children: [
        createCell("Accreditation or Evaluator/Advisor/Rater License Number:", colWidth6 * 4,
                  { bold: true, colSpan: 4 }),
        createCell("", colWidth6 * 4, { colSpan: 4 })
      ]
    }),
    new TableRow({
      children: [
        createCell("I hereby certify that the calculations submitted were completed in accordance with applicable codes.",
                  colWidth6 * 8, { colSpan: 8, italics: true })
      ]
    }),
    new TableRow({
      children: [
        createCell("Date:", colWidth6, { bold: true }),
        createCell("", colWidth6 * 2, { colSpan: 2 }),
        createCell("Signature:", colWidth6 * 2, { bold: true, colSpan: 2 }),
        createCell("", colWidth6 * 3, { colSpan: 3 })
      ]
    }),
    new TableRow({
      children: [
        createCell("Designer(s) - accreditation or licensing required", colWidth6 * 8,
                  { bold: true, shading: "E7E6E6", colSpan: 8, alignment: AlignmentType.CENTER })
      ]
    }),
    new TableRow({
      children: [
        createCell("Name:", colWidth6 * 2, { bold: true, colSpan: 2 }),
        createCell("", colWidth6, {}),
        createCell("Accreditation or licensing #:", colWidth6 * 4, { bold: true, colSpan: 4 }),
        createCell("", colWidth6, {})
      ]
    }),
    new TableRow({
      children: [
        createCell("Phone:", colWidth6 * 2, { bold: true, colSpan: 2 }),
        createCell("", colWidth6, {}),
        createCell("Email:", colWidth6 * 4, { bold: true, colSpan: 4 }),
        createCell("", colWidth6, {})
      ]
    }),
    new TableRow({
      children: [
        createCell("Declaration of designer to have reviewed and take responsibility for this submittal.",
                  colWidth6 * 8, { colSpan: 8, italics: true })
      ]
    }),
    new TableRow({
      children: [
        createCell("Date:", colWidth6, { bold: true }),
        createCell("", colWidth6 * 2, { colSpan: 2 }),
        createCell("Signature:", colWidth6 * 2, { bold: true, colSpan: 2 }),
        createCell("", colWidth6 * 3, { colSpan: 3 })
      ]
    })
  ]
});

// TABLE 8: Tiered Energy Compliance (1 column × 2 rows)
const table8 = new Table({
  columnWidths: [9360],
  margins: { top: 50, bottom: 50, left: 100, right: 100 },
  rows: [
    new TableRow({
      children: [
        createCell("Tiered Energy Compliance – Prescriptive Path", 9360,
                  { bold: true, shading: "E7E6E6", alignment: AlignmentType.CENTER })
      ]
    }),
    new TableRow({
      children: [
        createCell("", 9360, {})
      ]
    })
  ]
});

// TABLE 9: Designer Declaration (6 columns × 5 rows)
const colWidth9 = 1560; // 9360 / 6
const table9 = new Table({
  columnWidths: Array(6).fill(colWidth9),
  margins: { top: 50, bottom: 50, left: 100, right: 100 },
  rows: [
    new TableRow({
      children: [
        createCell("Designer(s) - accreditation or licensing required", colWidth9 * 6,
                  { bold: true, shading: "E7E6E6", colSpan: 6, alignment: AlignmentType.CENTER })
      ]
    }),
    new TableRow({
      children: [
        createCell("Name:", colWidth9 * 2, { bold: true, colSpan: 2 }),
        createCell("", colWidth9, {}),
        createCell("Accreditation or licensing #:", colWidth9 * 2, { bold: true, colSpan: 2 }),
        createCell("", colWidth9, {})
      ]
    }),
    new TableRow({
      children: [
        createCell("Phone:", colWidth9 * 2, { bold: true, colSpan: 2 }),
        createCell("", colWidth9, {}),
        createCell("Email:", colWidth9 * 2, { bold: true, colSpan: 2 }),
        createCell("", colWidth9, {})
      ]
    }),
    new TableRow({
      children: [
        createCell("Declaration of designer to have reviewed and take responsibility for this submittal.",
                  colWidth9 * 6, { colSpan: 6, italics: true })
      ]
    }),
    new TableRow({
      children: [
        createCell("Date:", colWidth9, { bold: true }),
        createCell("", colWidth9 * 2, { colSpan: 2 }),
        createCell("Signature:", colWidth9, { bold: true }),
        createCell("", colWidth9 * 2, { colSpan: 2 })
      ]
    })
  ]
});

// Create document with all tables
const doc = new Document({
  sections: [{
    children: [
      new Paragraph({ text: "Table 1: Project Information", bold: true }),
      table1,
      new Paragraph({ text: "" }),
      new Paragraph({ text: "Table 2: Project Design Conditions", bold: true }),
      table2,
      new Paragraph({ text: "" }),
      new Paragraph({ text: "Table 3: Compliance Option", bold: true }),
      table3,
      new Paragraph({ text: "" }),
      new Paragraph({ text: "Table 5: Additional Information", bold: true }),
      table5,
      new Paragraph({ text: "" }),
      new Paragraph({ text: "Table 6: Performance Energy Modeling Professional", bold: true }),
      table6,
      new Paragraph({ text: "" }),
      new Paragraph({ text: "Table 8: Tiered Energy Compliance", bold: true }),
      table8,
      new Paragraph({ text: "" }),
      new Paragraph({ text: "Table 9: Designer Declaration", bold: true }),
      table9
    ]
  }]
});

// Save
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("test_remaining_tables.docx", buffer);
  console.log("All remaining tables generated: test_remaining_tables.docx");
  console.log("  Table 1: 3 columns × 5 rows (Project Information)");
  console.log("  Table 2: 6 columns × 4 rows (Project Design Conditions)");
  console.log("  Table 3: 7 columns × 9 rows (Compliance Option)");
  console.log("  Table 5: 4 columns × 5 rows (Additional Information)");
  console.log("  Table 6: 8 columns × 11 rows (Performance Energy Modeling Professional)");
  console.log("  Table 8: 1 column × 2 rows (Tiered Energy Compliance)");
  console.log("  Table 9: 6 columns × 5 rows (Designer Declaration)");
});
