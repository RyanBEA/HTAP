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

// Column width for 19 equal columns: 9360 / 19 ≈ 493 DXA
const colWidth = 493;

// Create Table 7 with correct 19-column structure - ALL 51 ROWS
const table7Rows = [
  // Row 0: Title
  new TableRow({
    children: [
      createCell("Effective Thermal Resistance of Opaque Assemblies (Metric Units, RSI)", colWidth * 19, { bold: true, shading: "FFFFFF", colSpan: 19, alignment: AlignmentType.CENTER })
    ]
  }),

  // Row 1: Header - Assembly | Climate Zone | Proposed
  new TableRow({
    children: [
      createCell("Assembly", colWidth * 6, { bold: true, shading: "E7E6E6", colSpan: 6, rowSpan: 2, alignment: AlignmentType.CENTER }),
      createCell("Climate Zone", colWidth * 12, { bold: true, shading: "E7E6E6", colSpan: 12, alignment: AlignmentType.CENTER }),
      createCell("Proposed (min. effective RSI)", colWidth, { bold: true, shading: "E7E6E6", rowSpan: 2, alignment: AlignmentType.CENTER })
    ]
  }),

  // Row 2: Climate zone numbers
  new TableRow({
    children: [
      createCell("4", colWidth, { bold: true, shading: "E7E6E6", alignment: AlignmentType.CENTER }),
      createCell("5", colWidth * 2, { bold: true, shading: "E7E6E6", colSpan: 2, alignment: AlignmentType.CENTER }),
      createCell("6", colWidth * 2, { bold: true, shading: "E7E6E6", colSpan: 2, alignment: AlignmentType.CENTER }),
      createCell("7A", colWidth * 3, { bold: true, shading: "E7E6E6", colSpan: 3, alignment: AlignmentType.CENTER }),
      createCell("7B", colWidth, { bold: true, shading: "E7E6E6", alignment: AlignmentType.CENTER }),
      createCell("8", colWidth * 3, { bold: true, shading: "E7E6E6", colSpan: 3, alignment: AlignmentType.CENTER })
    ]
  }),

  // Row 3: Above-ground - Ceilings below attics (w/out HRV)
  new TableRow({
    children: [
      createCell("Above-ground", colWidth * 2, { bold: true, shading: "E7E6E6", colSpan: 2, rowSpan: 6 }),
      createCell("Ceilings below attics", colWidth * 3, { colSpan: 3, rowSpan: 2 }),
      createCell("w/out HRV", colWidth, {}),
      createCell("6.91", colWidth, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
      createCell("8.67", colWidth * 4, { shading: "E7E6E6", colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("10.43", colWidth * 7, { shading: "E7E6E6", colSpan: 7, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 4: w/ HRV
  new TableRow({
    children: [
      createCell("w/ HRV", colWidth, {}),
      createCell("6.91", colWidth * 2, { shading: "E7E6E6", colSpan: 2, alignment: AlignmentType.CENTER }),
      createCell("8.67", colWidth * 6, { shading: "E7E6E6", colSpan: 6, alignment: AlignmentType.CENTER }),
      createCell("10.43", colWidth * 4, { shading: "E7E6E6", colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 5: Cathedral ceilings, flat roofs
  new TableRow({
    children: [
      createCell("Cathedral ceilings, flat roofs", colWidth * 4, { colSpan: 4 }),
      createCell("4.67", colWidth * 5, { shading: "E7E6E6", colSpan: 5, alignment: AlignmentType.CENTER }),
      createCell("5.02", colWidth * 7, { shading: "E7E6E6", colSpan: 7, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 6: Walls (w/out HRV)
  new TableRow({
    children: [
      createCell("Walls", colWidth * 3, { colSpan: 3, rowSpan: 2 }),
      createCell("w/out HRV", colWidth, {}),
      createCell("2.78", colWidth, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
      createCell("3.08", colWidth * 7, { shading: "E7E6E6", colSpan: 7, alignment: AlignmentType.CENTER }),
      createCell("3.85", colWidth * 4, { shading: "E7E6E6", colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 7: w/ HRV
  new TableRow({
    children: [
      createCell("w/ HRV", colWidth, {}),
      createCell("2.78", colWidth, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
      createCell("2.97", colWidth * 7, { shading: "E7E6E6", colSpan: 7, alignment: AlignmentType.CENTER }),
      createCell("3.08", colWidth * 4, { shading: "E7E6E6", colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 8: Floors over unheated spaces
  new TableRow({
    children: [
      createCell("Floors over unheated spaces", colWidth * 4, { colSpan: 4 }),
      createCell("4.67", colWidth * 5, { shading: "E7E6E6", colSpan: 5, alignment: AlignmentType.CENTER }),
      createCell("5.02", colWidth * 7, { shading: "E7E6E6", colSpan: 7, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 9: Below-Grade - Foundation walls (w/out HRV)
  new TableRow({
    children: [
      createCell("Below-Grade or in Contact with Ground", colWidth * 2, { bold: true, shading: "E7E6E6", colSpan: 2, rowSpan: 8 }),
      createCell("Foundation walls", colWidth * 3, { colSpan: 3, rowSpan: 2 }),
      createCell("w/out HRV", colWidth, {}),
      createCell("1.99", colWidth, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
      createCell("2.98", colWidth * 4, { shading: "E7E6E6", colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("3.46", colWidth * 4, { shading: "E7E6E6", colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("3.97", colWidth * 3, { shading: "E7E6E6", colSpan: 3, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 10: w/ HRV
  new TableRow({
    children: [
      createCell("w/ HRV", colWidth, {}),
      createCell("1.99", colWidth, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
      createCell("2.98", colWidth * 11, { shading: "E7E6E6", colSpan: 11, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 11: Unheated floors - below frost line
  new TableRow({
    children: [
      createCell("Unheated floors", colWidth * 2, { colSpan: 2, rowSpan: 2 }),
      createCell("below frost line", colWidth * 2, { colSpan: 2 }),
      createCell("Uninsulated", colWidth * 12, { shading: "E7E6E6", colSpan: 12, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 12: above frost line
  new TableRow({
    children: [
      createCell("above frost line", colWidth * 2, { colSpan: 2 }),
      createCell("1.96", colWidth * 12, { shading: "E7E6E6", colSpan: 12, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 13: Floors on permafrost
  new TableRow({
    children: [
      createCell("Floors on permafrost", colWidth * 4, { colSpan: 4 }),
      createCell("n/a", colWidth * 8, { shading: "E7E6E6", colSpan: 8, alignment: AlignmentType.CENTER }),
      createCell("4.44", colWidth * 4, { shading: "E7E6E6", colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 14: Heated floors
  new TableRow({
    children: [
      createCell("Heated floors", colWidth * 4, { colSpan: 4 }),
      createCell("2.32", colWidth * 5, { shading: "E7E6E6", colSpan: 5, alignment: AlignmentType.CENTER }),
      createCell("2.84", colWidth * 7, { shading: "E7E6E6", colSpan: 7, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 15: Slabs-on-grade w/ integr. footing (w/out HRV)
  new TableRow({
    children: [
      createCell("Slabs-on-grade w/ integr. footing", colWidth * 3, { colSpan: 3, rowSpan: 2 }),
      createCell("w/out HRV", colWidth, {}),
      createCell("1.96", colWidth * 5, { shading: "E7E6E6", colSpan: 5, alignment: AlignmentType.CENTER }),
      createCell("3.72", colWidth * 4, { shading: "E7E6E6", colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("4.59", colWidth * 3, { shading: "E7E6E6", colSpan: 3, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 16: w/ HRV
  new TableRow({
    children: [
      createCell("w/ HRV", colWidth, {}),
      createCell("1.96", colWidth * 5, { shading: "E7E6E6", colSpan: 5, alignment: AlignmentType.CENTER }),
      createCell("2.84", colWidth * 4, { shading: "E7E6E6", colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("3.72", colWidth * 3, { shading: "E7E6E6", colSpan: 3, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 17: New section - Thermal Characteristics of Fenestration
  new TableRow({
    children: [
      createCell("Thermal Characteristics of Fenestration, Doors and Skylights", colWidth * 19, { bold: true, shading: "FFFFFF", colSpan: 19, alignment: AlignmentType.CENTER })
    ]
  }),

  // Row 18: Header - Assembly | Climate Zone | Proposed
  new TableRow({
    children: [
      createCell("Assembly", colWidth * 6, { bold: true, shading: "E7E6E6", colSpan: 6, rowSpan: 2, alignment: AlignmentType.CENTER }),
      createCell("Climate Zone", colWidth * 12, { bold: true, shading: "E7E6E6", colSpan: 12, alignment: AlignmentType.CENTER }),
      createCell("Proposed (max. U or min. ER)", colWidth, { bold: true, shading: "E7E6E6", rowSpan: 2, alignment: AlignmentType.CENTER })
    ]
  }),

  // Row 19: Climate zone numbers (different grouping)
  new TableRow({
    children: [
      createCell("4", colWidth, { bold: true, shading: "E7E6E6", alignment: AlignmentType.CENTER }),
      createCell("5", colWidth * 2, { bold: true, shading: "E7E6E6", colSpan: 2, alignment: AlignmentType.CENTER }),
      createCell("6", colWidth * 3, { bold: true, shading: "E7E6E6", colSpan: 3, alignment: AlignmentType.CENTER }),
      createCell("7A", colWidth * 2, { bold: true, shading: "E7E6E6", colSpan: 2, alignment: AlignmentType.CENTER }),
      createCell("7B", colWidth, { bold: true, shading: "E7E6E6", alignment: AlignmentType.CENTER }),
      createCell("8", colWidth * 3, { bold: true, shading: "E7E6E6", colSpan: 3, alignment: AlignmentType.CENTER })
    ]
  }),

  // Row 20: Fenestration & doors - Max. U-value
  new TableRow({
    children: [
      createCell("Fenestration & doors", colWidth * 3, { colSpan: 3, rowSpan: 2 }),
      createCell("Max. U-value", colWidth * 3, { colSpan: 3 }),
      createCell("1.84", colWidth * 3, { shading: "E7E6E6", colSpan: 3, alignment: AlignmentType.CENTER }),
      createCell("1.61", colWidth * 5, { shading: "E7E6E6", colSpan: 5, alignment: AlignmentType.CENTER }),
      createCell("1.44", colWidth * 4, { shading: "E7E6E6", colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 21: Min. Energy Rating
  new TableRow({
    children: [
      createCell("Min. Energy Rating", colWidth * 3, { colSpan: 3 }),
      createCell("21", colWidth * 3, { shading: "E7E6E6", colSpan: 3, alignment: AlignmentType.CENTER }),
      createCell("25", colWidth * 5, { shading: "E7E6E6", colSpan: 5, alignment: AlignmentType.CENTER }),
      createCell("29", colWidth * 4, { shading: "E7E6E6", colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 22: Skylights
  new TableRow({
    children: [
      createCell("Skylights (Max. U-value)", colWidth * 6, { colSpan: 6 }),
      createCell("2.92", colWidth * 3, { shading: "E7E6E6", colSpan: 3, alignment: AlignmentType.CENTER }),
      createCell("2.75", colWidth * 5, { shading: "E7E6E6", colSpan: 5, alignment: AlignmentType.CENTER }),
      createCell("2.41", colWidth * 4, { shading: "E7E6E6", colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 23: One door exception
  new TableRow({
    children: [
      createCell("One door exception (Max. U-value)", colWidth * 6, { colSpan: 6 }),
      createCell("2.6", colWidth * 12, { shading: "E7E6E6", colSpan: 12, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 24: Access hatches
  new TableRow({
    children: [
      createCell("Access hatches (Min. RSIeff)", colWidth * 6, { colSpan: 6 }),
      createCell("2.6", colWidth * 12, { shading: "E7E6E6", colSpan: 12, alignment: AlignmentType.CENTER }),
      createCell("", colWidth, { shading: "DEEAF6" })
    ]
  }),

  // Row 25: HVAC Equipment section
  new TableRow({
    children: [
      createCell("HVAC Equipment Efficiency Requirements", colWidth * 19, { bold: true, shading: "FFFFFF", colSpan: 19, alignment: AlignmentType.CENTER })
    ]
  }),

  // Row 26: HVAC header
  new TableRow({
    children: [
      createCell("Equipment", colWidth * 4, { bold: true, shading: "E7E6E6", colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("Capacity kW", colWidth * 2, { bold: true, shading: "E7E6E6", colSpan: 2, alignment: AlignmentType.CENTER }),
      createCell("Standard", colWidth * 4, { bold: true, shading: "E7E6E6", colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("Min. Efficiency", colWidth * 6, { bold: true, shading: "E7E6E6", colSpan: 6, alignment: AlignmentType.CENTER }),
      createCell("Proposed (fuel & equipment type, efficiency)", colWidth * 3, { bold: true, shading: "E7E6E6", colSpan: 3, alignment: AlignmentType.CENTER })
    ]
  }),

  // Row 27: Furnace - Gas-fired
  new TableRow({
    children: [
      createCell("Furnace", colWidth, { rowSpan: 3 }),
      createCell("Gas-fired", colWidth * 3, { colSpan: 3 }),
      createCell("≤ 66", colWidth * 2, { colSpan: 2, rowSpan: 3, alignment: AlignmentType.CENTER }),
      createCell("CSA P.2", colWidth * 4, { colSpan: 4, rowSpan: 3, alignment: AlignmentType.CENTER }),
      createCell("AFUE ≥ 95%", colWidth * 6, { shading: "E7E6E6", colSpan: 6 }),
      createCell("", colWidth * 3, { shading: "DEEAF6", colSpan: 3 })
    ]
  }),

  // Row 28: Oil-fired
  new TableRow({
    children: [
      createCell("Oil-fired", colWidth * 3, { colSpan: 3 }),
      createCell("AFUE ≥ 85%", colWidth * 6, { shading: "E7E6E6", colSpan: 6 }),
      createCell("", colWidth * 3, { shading: "DEEAF6", colSpan: 3 })
    ]
  }),

  // Row 29: Electric
  new TableRow({
    children: [
      createCell("Electric", colWidth * 3, { colSpan: 3 }),
      new TableCell({
        borders: cellBorders,
        width: { size: colWidth * 6, type: WidthType.DXA },
        shading: { fill: "E7E6E6", type: ShadingType.CLEAR },
        columnSpan: 6,
        children: [
          new Paragraph({
            children: [
              new TextRun({ text: "See footnote ", size: 20 }),
              footnoteRef(5)
            ]
          })
        ]
      }),
      createCell("", colWidth * 3, { shading: "DEEAF6", colSpan: 3 })
    ]
  }),

  // Row 30: Boiler - Gas-fired
  new TableRow({
    children: [
      createCell("Boiler", colWidth, { rowSpan: 3 }),
      createCell("Gas-fired", colWidth * 3, { colSpan: 3 }),
      createCell("< 88", colWidth * 2, { colSpan: 2, rowSpan: 3, alignment: AlignmentType.CENTER }),
      createCell("CSA P.2", colWidth * 4, { colSpan: 4, rowSpan: 3, alignment: AlignmentType.CENTER }),
      createCell("AFUE ≥ 90%", colWidth * 6, { shading: "E7E6E6", colSpan: 6 }),
      createCell("", colWidth * 3, { shading: "DEEAF6", colSpan: 3 })
    ]
  }),

  // Row 31: Oil-fired
  new TableRow({
    children: [
      createCell("Oil-fired", colWidth * 3, { colSpan: 3 }),
      createCell("AFUE ≥ 86%", colWidth * 6, { shading: "E7E6E6", colSpan: 6 }),
      createCell("", colWidth * 3, { shading: "DEEAF6", colSpan: 3 })
    ]
  }),

  // Row 32: Electric
  new TableRow({
    children: [
      createCell("Electric", colWidth * 3, { colSpan: 3 }),
      createCell("See footnote", colWidth * 6, { shading: "E7E6E6", colSpan: 6 }),
      createCell("", colWidth * 3, { shading: "DEEAF6", colSpan: 3 })
    ]
  }),

  // Row 33: Air source heat pump
  new TableRow({
    children: [
      createCell("Air source heat pump – split", colWidth * 4, { colSpan: 4 }),
      createCell("< 19", colWidth * 2, { colSpan: 2, alignment: AlignmentType.CENTER }),
      createCell("CSA C656", colWidth * 4, { colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("HSPF V ≥ 7.1", colWidth * 6, { shading: "E7E6E6", colSpan: 6 }),
      createCell("", colWidth * 3, { shading: "DEEAF6", colSpan: 3 })
    ]
  }),

  // Row 34: Combined space- and water-heating
  new TableRow({
    children: [
      createCell("Combined space- and water-heating systems", colWidth * 4, { colSpan: 4 }),
      createCell("≤ 87.9 (boiler), or  ≤ 73.2 (service water heater)", colWidth * 2, { colSpan: 2, alignment: AlignmentType.CENTER }),
      createCell("CSA-P.9", colWidth * 4, { colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("TPF ≥ 0.80", colWidth * 6, { shading: "E7E6E6", colSpan: 6 }),
      createCell("", colWidth * 3, { shading: "DEEAF6", colSpan: 3 })
    ]
  }),

  // Row 35: Heat Recovery Ventilation @ 0°C
  new TableRow({
    children: [
      createCell("Heat Recovery Ventilation", colWidth * 4, { colSpan: 4, rowSpan: 2 }),
      createCell("-", colWidth * 2, { colSpan: 2, rowSpan: 2, alignment: AlignmentType.CENTER }),
      createCell("CSA-C439", colWidth * 4, { colSpan: 4, rowSpan: 2, alignment: AlignmentType.CENTER }),
      createCell("@0°C", colWidth * 3, { colSpan: 3 }),
      createCell("60%SRE", colWidth * 3, { shading: "E7E6E6", colSpan: 3 }),
      createCell("", colWidth * 3, { shading: "DEEAF6", colSpan: 3 })
    ]
  }),

  // Row 36: @ -25°C
  new TableRow({
    children: [
      createCell("@-25°C", colWidth * 3, { colSpan: 3 }),
      createCell("55%SRE", colWidth * 3, { shading: "E7E6E6", colSpan: 3 }),
      createCell("", colWidth * 3, { shading: "DEEAF6", colSpan: 3 })
    ]
  }),

  // Row 37: (Other)
  new TableRow({
    children: [
      createCell("(Other)", colWidth * 4, { colSpan: 4 }),
      createCell("", colWidth * 2, { colSpan: 2 }),
      createCell("", colWidth * 4, { colSpan: 4 }),
      createCell("", colWidth * 6, { shading: "E7E6E6", colSpan: 6 }),
      createCell("", colWidth * 3, { shading: "DEEAF6", colSpan: 3 })
    ]
  }),

  // Row 38: Service Water Heater section
  new TableRow({
    children: [
      createCell("Service Water Heater Efficiency Requirements", colWidth * 19, { bold: true, shading: "FFFFFF", colSpan: 19, alignment: AlignmentType.CENTER })
    ]
  }),

  // Row 39: Water heater header
  new TableRow({
    children: [
      createCell("Equipment", colWidth * 4, { bold: true, shading: "E7E6E6", colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("Capacity", colWidth * 2, { bold: true, shading: "E7E6E6", colSpan: 2, alignment: AlignmentType.CENTER }),
      createCell("Standard", colWidth * 4, { bold: true, shading: "E7E6E6", colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("Min. Efficiency", colWidth * 7, { bold: true, shading: "E7E6E6", colSpan: 7, alignment: AlignmentType.CENTER }),
      createCell("Proposed (fuel & equipment type, efficiency)", colWidth * 2, { bold: true, shading: "E7E6E6", colSpan: 2, alignment: AlignmentType.CENTER })
    ]
  }),

  // Row 40: Tank Storage - Electric - 50-270L (top inlet)
  new TableRow({
    children: [
      createCell("Tank Storage", colWidth * 2, { colSpan: 2, rowSpan: 7 }),
      createCell("Electric (≤ 12 kW)", colWidth * 2, { colSpan: 2, rowSpan: 4 }),
      createCell("50-270L", colWidth * 2, { colSpan: 2, rowSpan: 2 }),
      createCell("CSA-C191", colWidth * 4, { colSpan: 4, rowSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("SL≤ 35+0.20V (top in.)", colWidth * 7, { shading: "E7E6E6", colSpan: 7 }),
      createCell("", colWidth * 2, { shading: "DEEAF6", colSpan: 2 })
    ]
  }),

  // Row 41: bottom inlet
  new TableRow({
    children: [
      createCell("SL ≤ 40+0.20V (bottom in.)", colWidth * 7, { shading: "E7E6E6", colSpan: 7 }),
      createCell("", colWidth * 2, { shading: "DEEAF6", colSpan: 2 })
    ]
  }),

  // Row 42: 270-454L (top inlet)
  new TableRow({
    children: [
      createCell("270-454L", colWidth * 2, { colSpan: 2, rowSpan: 2 }),
      createCell("SL≤0.472V-38.5 (top in.)", colWidth * 7, { shading: "E7E6E6", colSpan: 7 }),
      createCell("", colWidth * 2, { shading: "DEEAF6", colSpan: 2 })
    ]
  }),

  // Row 43: bottom inlet
  new TableRow({
    children: [
      createCell("SL ≤ 0.472V-33.5 (bottom in.)", colWidth * 7, { shading: "E7E6E6", colSpan: 7 }),
      createCell("", colWidth * 2, { shading: "DEEAF6", colSpan: 2 })
    ]
  }),

  // Row 44: Gas-fired - 1st hr <68 L
  new TableRow({
    children: [
      createCell("Gas-fired (≤ 22 kW)", colWidth * 2, { colSpan: 2, rowSpan: 3 }),
      createCell("1st hr <68 L", colWidth * 2, { colSpan: 2 }),
      createCell("CSA-P.3", colWidth * 4, { colSpan: 4, rowSpan: 3, alignment: AlignmentType.CENTER }),
      createCell("UEF ≥ 0.3456 – 0.00053V", colWidth * 7, { shading: "E7E6E6", colSpan: 7 }),
      createCell("", colWidth * 2, { shading: "DEEAF6", colSpan: 2 })
    ]
  }),

  // Row 45: 1st hr 68-192 L
  new TableRow({
    children: [
      createCell("1st hr 68-192 L", colWidth * 2, { colSpan: 2 }),
      createCell("UEF ≥ 0.5982 – 0.00050V", colWidth * 7, { shading: "E7E6E6", colSpan: 7 }),
      createCell("", colWidth * 2, { shading: "DEEAF6", colSpan: 2 })
    ]
  }),

  // Row 46: 1st hr 193-283 L
  new TableRow({
    children: [
      createCell("1st hr 193-283 L", colWidth * 2, { colSpan: 2 }),
      createCell("UEF ≥ 0.6483 – 0.00045V", colWidth * 7, { shading: "E7E6E6", colSpan: 7 }),
      createCell("", colWidth * 2, { shading: "DEEAF6", colSpan: 2 })
    ]
  }),

  // Row 47: Tankless, gas-fired - < 6.4 L/min
  new TableRow({
    children: [
      createCell("Tankless, gas-fired (≤ 58.6 kW)", colWidth * 4, { colSpan: 4, rowSpan: 2 }),
      createCell("< 6.4 L/min", colWidth * 2, { colSpan: 2 }),
      createCell("CSA-P.3", colWidth * 4, { colSpan: 4, rowSpan: 2, alignment: AlignmentType.CENTER }),
      createCell("UEF ≥ 0.86", colWidth * 7, { shading: "E7E6E6", colSpan: 7 }),
      createCell("", colWidth * 2, { shading: "DEEAF6", colSpan: 2 })
    ]
  }),

  // Row 48: ≥ 6.4 L/min
  new TableRow({
    children: [
      createCell("≥ 6.4 L/min", colWidth * 2, { colSpan: 2 }),
      createCell("UEF ≥ 0.87", colWidth * 7, { shading: "E7E6E6", colSpan: 7 }),
      createCell("", colWidth * 2, { shading: "DEEAF6", colSpan: 2 })
    ]
  }),

  // Row 49: Heat pump water heaters
  new TableRow({
    children: [
      createCell("Heat pump water heaters", colWidth * 4, { colSpan: 4 }),
      createCell("≤24 A and ≤250 V", colWidth * 2, { colSpan: 2 }),
      createCell("CSA-C745", colWidth * 4, { colSpan: 4, alignment: AlignmentType.CENTER }),
      createCell("EF ≥ 2.1", colWidth * 7, { shading: "E7E6E6", colSpan: 7 }),
      createCell("", colWidth * 2, { shading: "DEEAF6", colSpan: 2 })
    ]
  }),

  // Row 50: (Other)
  new TableRow({
    children: [
      createCell("(Other)", colWidth * 4, { colSpan: 4 }),
      createCell("", colWidth * 2, { colSpan: 2 }),
      createCell("", colWidth * 4, { colSpan: 4 }),
      createCell("", colWidth * 7, { shading: "E7E6E6", colSpan: 7 }),
      createCell("", colWidth * 2, { shading: "DEEAF6", colSpan: 2 })
    ]
  })
];

// Create Table 7 with correct 19-column structure
const table7 = new Table({
  columnWidths: Array(19).fill(colWidth),  // 19 columns of 493 DXA each
  margins: { top: 50, bottom: 50, left: 100, right: 100 },
  rows: table7Rows
});

// Create document
const doc = new Document({
  sections: [{
    children: [
      new Paragraph({
        children: [new TextRun({ text: "Table 7 Complete Test - D.2 Effective Thermal Resistance (51 rows)", bold: true, size: 24 })]
      }),
      table7
    ]
  }]
});

// Save
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("test_table7_complete.docx", buffer);
  console.log("Complete Table 7 (51 rows) generated: test_table7_complete.docx");
});
