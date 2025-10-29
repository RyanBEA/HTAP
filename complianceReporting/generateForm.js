const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, Header, Footer,
        AlignmentType, BorderStyle, WidthType, ShadingType, VerticalAlign, LevelFormat } = require('docx');

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
    : content; // Allow passing array of Paragraphs

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

// Create the document
const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullet-list",
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: "•",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } }
          }
        ]
      }
    ]
  },
  styles: {
    default: {
      document: {
        run: { font: "Arial", size: 20 }
      }
    }
  },
  sections: [{
    properties: {
      page: {
        margin: { top: 720, right: 720, bottom: 720, left: 720 }
      }
    },
    headers: {
      default: new Header({
        children: [
          new Paragraph({
            alignment: AlignmentType.RIGHT,
            children: [
              new TextRun({ text: "NBC 2020, Subsection 9.36", bold: true, size: 24 })
            ]
          }),
          new Paragraph({
            alignment: AlignmentType.RIGHT,
            children: [
              new TextRun({ text: "Submittal Form", bold: true, size: 24 })
            ]
          })
        ]
      })
    },
    children: [
      // A. Project Information
      new Paragraph({
        spacing: { before: 200, after: 120 },
        children: [new TextRun({ text: "A. Project Information", bold: true, size: 24 })]
      }),

      new Table({
        columnWidths: [2340, 4680, 2340],
        margins: { top: 50, bottom: 50, left: 100, right: 100 },
        rows: [
          new TableRow({
            children: [
              createCell("The (name of jurisdiction) Requirements for Division B 9.36 Compliance", 9360, {
                bold: true, shading: "D9D9D9", alignment: AlignmentType.CENTER, colSpan: 3
              })
            ]
          }),
          new TableRow({
            children: [
              createCell("Project Name:", 2340),
              createCell("", 2340),
              createCell("Building Permit Number (Completed Internally)", 2340, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Project Address:", 2340),
              createCell("", 4680, { colSpan: 2 })
            ]
          }),
          new TableRow({
            children: [
              createCell("Applicant Name:", 2340),
              createCell("", 4680, { colSpan: 2 })
            ]
          }),
          new TableRow({
            children: [
              createCell("Applicant Address:", 2340),
              createCell("", 4680, { colSpan: 2 })
            ]
          })
        ]
      }),

      // B. Project Design Conditions
      new Paragraph({
        spacing: { before: 240, after: 120 },
        children: [new TextRun({ text: "B. Project Design Conditions", bold: true, size: 24 })]
      }),

      new Table({
        columnWidths: [1560, 1560, 1560, 1560, 1560, 1560],
        margins: { top: 50, bottom: 50, left: 100, right: 100 },
        rows: [
          new TableRow({
            children: [
              createCell("Climate zone (based on heating degree days in Celsius Degree-Days, per AHJ or Appendix C Table C2)", 9360, {
                bold: true, shading: "E7E6E6", colSpan: 6
              })
            ]
          }),
          new TableRow({
            children: [
              createCell("☐ Zone 4\n(< 3000)", 1560, { alignment: AlignmentType.CENTER }),
              createCell("☐ Zone 5\n(3000 to 3999)", 1560, { alignment: AlignmentType.CENTER }),
              createCell("☐ Zone 6\n(4000 to 4999)", 1560, { alignment: AlignmentType.CENTER }),
              createCell("☐ Zone 7A\n(5000 to 5999)", 1560, { alignment: AlignmentType.CENTER }),
              createCell("☐ Zone 7B\n(6000 to 6999)", 1560, { alignment: AlignmentType.CENTER }),
              createCell("☐ Zone 8\n(7000 to 7999)", 1560, { alignment: AlignmentType.CENTER })
            ]
          })
        ]
      }),

      new Table({
        columnWidths: [3120, 3120, 3120],
        margins: { top: 50, bottom: 50, left: 100, right: 100 },
        rows: [
          new TableRow({
            children: [
              createCell("Occupancy type", 3120, { bold: true }),
              createCell("Floor area", 3120, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("Fenestration and door area to gross wall ratio (FDWR)", 3120, { bold: true })
            ]
          }),
          new TableRow({
            children: [
              createCell("", 3120),
              createCell("____________ m²", 3120, { alignment: AlignmentType.CENTER }),
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                verticalAlign: VerticalAlign.TOP,
                children: [
                  new Paragraph({
                    children: [
                      new TextRun({ text: "Fenestration & door area/ m² =", size: 20 })
                    ]
                  }),
                  new Paragraph({
                    children: [
                      new TextRun({ text: "Gross wall area = m² =", size: 20 })
                    ]
                  }),
                  new Paragraph({
                    children: [
                      new TextRun({ text: "FDWR%", size: 20 }),
                      footnoteRef(1)
                    ]
                  })
                ]
              })
            ]
          })
        ]
      }),

      // C. Compliance Option
      new Paragraph({
        spacing: { before: 240, after: 120 },
        children: [new TextRun({ text: "C. Compliance Option", bold: true, size: 24 })]
      }),

      new Table({
        columnWidths: [1170, 1560, 1170, 1170, 1170, 1170, 1950],
        margins: { top: 50, bottom: 50, left: 100, right: 100 },
        rows: [
          new TableRow({
            children: [
              createCell("Indicate Compliance Path", 2730, { bold: true, shading: "E7E6E6", colSpan: 2 }),
              createCell("Energy\nPerformance Tier", 1170, { bold: true, shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("Building\nEnvelope\nTrade-Off?", 1170, { bold: true, shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("Forms to Complete", 4290, { bold: true, shading: "E7E6E6", colSpan: 3, alignment: AlignmentType.CENTER })
            ]
          }),
          new TableRow({
            children: [
              createCell("", 1170),
              createCell("", 1560),
              createCell("", 1170),
              createCell("", 1170),
              createCell("D1", 1170, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("D2", 1170, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("9.36 Submittal Calculator", 1950, { bold: true, alignment: AlignmentType.CENTER })
            ]
          }),
          new TableRow({
            children: [
              createCell("☐", 1170, { alignment: AlignmentType.CENTER, rowSpan: 3 }),
              createCell("Prescriptive\n(Subsections 9.36.2-9.36.4, 9.36.8)", 1560, { rowSpan: 3 }),
              createCell("☐ 1", 1170),
              createCell("☐ No", 1170),
              createCell("", 1170),
              createCell("√", 1170, { alignment: AlignmentType.CENTER }),
              createCell("", 1950)
            ]
          }),
          new TableRow({
            children: [
              createCell("", 1170),
              createCell("☐ Yes", 1170),
              createCell("", 1170),
              createCell("√", 1170, { alignment: AlignmentType.CENTER }),
              createCell("√ (BE Trade-off tab)", 1950)
            ]
          }),
          new TableRow({
            children: [
              createCell("☐ 2-5", 1170),
              createCell("-", 1170, { alignment: AlignmentType.CENTER }),
              createCell("", 1170),
              createCell("√", 1170, { alignment: AlignmentType.CENTER }),
              createCell("√ (Prescriptive Tier tab)", 1950)
            ]
          }),
          new TableRow({
            children: [
              createCell("☐", 1170, { alignment: AlignmentType.CENTER, rowSpan: 2 }),
              createCell("Performance\n(Subsection 9.36.5, 9.36.7)", 1560, { rowSpan: 2 }),
              createCell("☐ 1", 1170),
              createCell("-", 1170, { alignment: AlignmentType.CENTER }),
              createCell("√", 1170, { alignment: AlignmentType.CENTER }),
              createCell("", 1170),
              createCell("", 1950)
            ]
          }),
          new TableRow({
            children: [
              createCell("☐ 2-5", 1170),
              createCell("-", 1170, { alignment: AlignmentType.CENTER }),
              createCell("√", 1170, { alignment: AlignmentType.CENTER }),
              createCell("", 1170),
              createCell("√ (Performance Tier tab)", 1950)
            ]
          })
        ]
      }),

      new Table({
        columnWidths: [4680, 4680],
        margins: { top: 50, bottom: 50, left: 100, right: 100 },
        rows: [
          new TableRow({
            children: [
              createCell("Additional information to be submitted for review", 9360, {
                bold: true, shading: "E7E6E6", colSpan: 2
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 4680, type: WidthType.DXA },
                children: [
                  new Paragraph({ children: [new TextRun("☐ Insulation and air barrier details in project drawing set, including:", { size: 20 })] }),
                  new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Attic hatch", { size: 20 })] }),
                  new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Eaves to top of wall transition", { size: 20 })] }),
                  new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Upper floor rim joist", { size: 20 })] }),
                  new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Slab/footing junction", { size: 20 })] }),
                  new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Cantilever floors", { size: 20 })] }),
                  new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Bonus room/living space over attached garage (including ducts and insulation coverage of ducts)", { size: 20 })] }),
                  new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Typical electrical junction box detail", { size: 20 })] }),
                  new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Typical window/door jamb and sill detail", { size: 20 })] }),
                  new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("(if applicable) Party wall meeting outside wall, electric meter/vent pipe/duct in insulated wall, skylight shaft walls, slab edges in walkouts and heated slabs, masonry fireplaces", { size: 20 })] })
                ]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 4680, type: WidthType.DXA },
                children: [
                  new Paragraph({ children: [new TextRun("☐ Window & door schedule", { size: 20 })] }),
                  new Paragraph({ children: [new TextRun("☐ RSI assembly calculations", { size: 20 })] }),
                  new Paragraph({ children: [new TextRun("☐ Heat loss and heat gain calculations (CSA F280)", { size: 20 })] }),
                  new Paragraph({ children: [new TextRun("☐ Mechanical layout (i.e. duct design)", { size: 20 })] }),
                  new Paragraph({ children: [new TextRun("☐ Ventilation design (Subsection 9.32.3, or CSA F326)", { size: 20 })] })
                ]
              })
            ]
          })
        ]
      }),

      // Footnote for page 1
      new Paragraph({
        spacing: { before: 200 },
        children: [
          footnoteRef(1),
          new TextRun({ text: " Per Article 9.36.2.3", size: 18 })
        ]
      }),

      // D.1 Performance Compliance
      new Paragraph({
        spacing: { before: 300, after: 120 },
        children: [new TextRun({ text: "D.1  Performance Compliance – Subsection 9.36.5", bold: true, size: 22 })]
      }),

      new Table({
        columnWidths: [1170, 1170, 780, 3120, 3120],
        margins: { top: 50, bottom: 50, left: 100, right: 100 },
        rows: [
          new TableRow({
            children: [
              createCell("Input Parameters", 3120, { bold: true, shading: "FFFFFF", colSpan: 3 }),
              createCell("Reference Model", 3120, { bold: true, shading: "FFFFFF", alignment: AlignmentType.CENTER }),
              createCell("Proposed Model", 3120, { bold: true, shading: "FFFFFF", alignment: AlignmentType.CENTER })
            ]
          }),
          new TableRow({
            children: [
              createCell("Opaque Assemblies", 9360, { bold: true, shading: "E7E6E6", colSpan: 5 })
            ]
          }),
          new TableRow({
            children: [
              createCell("", 3120, { colSpan: 3 }),
              createCell("Effective Thermal Resistance (RSI)", 6240, { bold: true, shading: "E7E6E6", colSpan: 2, alignment: AlignmentType.CENTER })
            ]
          }),
          new TableRow({
            children: [
              createCell("Above-ground", 3120, { bold: true, shading: "E7E6E6", colSpan: 3 }),
              createCell("", 3120),
              createCell("", 3120)
            ]
          }),
          new TableRow({
            children: [
              createCell("  Ceilings below attics", 3120, { colSpan: 3 }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("  Cathedral ceilings and flat roofs", 3120, { colSpan: 3 }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("  Walls", 3120, { colSpan: 3 }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("  Floors over unheated spaces", 3120, { colSpan: 3 }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Below-Grade or in Contact with Ground", 3120, { bold: true, shading: "E7E6E6", colSpan: 3 }),
              createCell("", 3120),
              createCell("", 3120)
            ]
          }),
          new TableRow({
            children: [
              createCell("  Foundation walls", 3120, { colSpan: 3 }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("  Unheated floors", 1170),
              createCell("below frost line", 1950, { colSpan: 2 }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("", 1170),
              createCell("above frost line", 1950, { colSpan: 2 }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("  Heated and unheated floors on permafrost", 3120, { colSpan: 3 }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("  Heated floors", 3120, { colSpan: 3 }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("  Slabs-on-grade with an integral footing", 3120, { colSpan: 3 }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Fenestration, Doors, Skylights", 9360, { bold: true, shading: "E7E6E6", colSpan: 5 })
            ]
          }),
          new TableRow({
            children: [
              createCell("", 3120, { colSpan: 3 }),
              createCell("U-factor, Energy Rating, RSIeff", 6240, { bold: true, shading: "E7E6E6", colSpan: 2, alignment: AlignmentType.CENTER })
            ]
          }),
          new TableRow({
            children: [
              createCell("Front orientation of house (N, NE, E, SE, S, SW, W, NW):", 9360, { colSpan: 5 })
            ]
          }),
          new TableRow({
            children: [
              createCell("Windows", 1170, { rowSpan: 2 }),
              createCell("U-factor or ER", 1950, { colSpan: 2 }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Solar Heat Gain Coefficient", 1950, { colSpan: 2 }),
              createCell("0.26", 3120, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Skylights", 1170, { rowSpan: 2 }),
              createCell("U-factor or ER", 1950, { colSpan: 2 }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Solar Heat Gain Coefficient", 1950, { colSpan: 2 }),
              createCell("0.26", 3120, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Doors", 3120, { colSpan: 3 }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                columnSpan: 3,
                children: [
                  new Paragraph({
                    children: [
                      new TextRun({ text: "Fenestration & door area to gross wall ratio, FDWR (%)", size: 20 }),
                      footnoteRef(2)
                    ]
                  })
                ]
              }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Airtightness", 9360, { bold: true, shading: "E7E6E6", colSpan: 5 })
            ]
          }),
          new TableRow({
            children: [
              createCell("", 3120, { colSpan: 3 }),
              createCell("Air Changes per Hour (ACH @ 50 Pa)", 6240, { bold: true, shading: "E7E6E6", colSpan: 2, alignment: AlignmentType.CENTER })
            ]
          }),
          new TableRow({
            children: [
              createCell("☐ Construction complies with Section 9.25", 3120, { colSpan: 3 }),
              createCell("2.5", 3120, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("3.2", 3120, { shading: "E7E6E6", alignment: AlignmentType.CENTER })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                columnSpan: 3,
                children: [
                  new Paragraph({
                    children: [
                      new TextRun({ text: "☐ ", size: 20, italics: true }),
                      new TextRun({ text: "Air barrier system", size: 20, italics: true }),
                      new TextRun({ text: " constructed to Subsection 9.25.3 and Articles 9.36.2.9. and 9.36.2.10.", size: 20 })
                    ]
                  })
                ]
              }),
              createCell("2.5", 3120, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("2.5", 3120, { shading: "E7E6E6", alignment: AlignmentType.CENTER })
            ]
          }),
          new TableRow({
            children: [
              createCell("☐ Airtightness tested (per Sentence 9.36.6.3.(1))", 3120, { colSpan: 3 }),
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                shading: { fill: "E7E6E6", type: ShadingType.CLEAR },
                children: [
                  new Paragraph({ children: [new TextRun("☐ 2.5 (detached house)", { size: 20 })] }),
                  new Paragraph({ children: [new TextRun("☐ 3.0 (attached house)", { size: 20 })] })
                ]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                shading: { fill: "E7E6E6", type: ShadingType.CLEAR },
                children: [
                  new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [new TextRun("Max. test result target:", { size: 20 })]
                  })
                ]
              })
            ]
          }),
          new TableRow({
            children: [
              createCell("HVAC, Service Hot Water", 9360, { bold: true, shading: "E7E6E6", colSpan: 5 })
            ]
          }),
          new TableRow({
            children: [
              createCell("", 3120, { colSpan: 3 }),
              createCell("Fuel & Equipment Type, Efficiencies", 6240, { bold: true, shading: "E7E6E6", colSpan: 2, alignment: AlignmentType.CENTER })
            ]
          }),
          new TableRow({
            children: [
              createCell("Heating System(s)", 3120, { colSpan: 3 }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Cooling System", 1170, { rowSpan: 3 }),
              createCell("Capacity (kW)", 1950, { colSpan: 2 }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("SEER", 1950, { colSpan: 2 }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 1950, type: WidthType.DXA },
                columnSpan: 2,
                children: [
                  new Paragraph({ children: [new TextRun("☐ Air Source Heat Pump?", { size: 20 })] }),
                  new Paragraph({ children: [new TextRun("HSPF V", { size: 20 })] }),
                  new Paragraph({ children: [new TextRun("Cutoff Temperature", { size: 20 })] })
                ]
              }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                columnSpan: 3,
                children: [
                  new Paragraph({
                    children: [
                      new TextRun({ text: "Supplementary Heating System(s)", size: 20 }),
                      footnoteRef(3)
                    ]
                  })
                ]
              }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Ventilation System", 1170, { rowSpan: 4 }),
              new TableCell({
                borders: cellBorders,
                width: { size: 1950, type: WidthType.DXA },
                columnSpan: 2,
                children: [
                  new Paragraph({
                    children: [
                      new TextRun({ text: "Principal Ventilation Rate (L/s)", size: 20 }),
                      footnoteRef(4)
                    ]
                  })
                ]
              }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Runtime (hrs/day)", 1950, { colSpan: 2 }),
              createCell("8", 3120),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Fan Power (W)", 1170),
              createCell("@ 0°C\n@ -25°C", 780),
              createCell("2.32 W/L/s = ______ W", 3120),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Heat Recovery, % SRE", 1170),
              createCell("@ 0°C\n@ -25°C", 780),
              createCell("none", 3120, { alignment: AlignmentType.CENTER }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Service Water Heating System(s)", 3120, { colSpan: 3 }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("", 3120, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Drain Water Heat Recovery", 1170, { rowSpan: 2 }),
              createCell("Recovery efficiency, flow configuration", 1950, { colSpan: 2 }),
              createCell("none", 3120, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                shading: { fill: "E7E6E6", type: ShadingType.CLEAR },
                children: [
                  new Paragraph({ children: [new TextRun("___% RE", { size: 20 })] }),
                  new Paragraph({ children: [new TextRun("☐equal flow  ☐unequal flow", { size: 20 })] })
                ]
              })
            ]
          }),
          new TableRow({
            children: [
              createCell("# of showers connected (of total)", 1950, { colSpan: 2 }),
              createCell("", 3120, { shading: "E7E6E6" }),
              createCell("___ of ___", 3120, { shading: "E7E6E6" })
            ]
          })
        ]
      }),

      // Performance Software Calculations
      new Table({
        columnWidths: [4680, 4680],
        margins: { top: 50, bottom: 50, left: 100, right: 100 },
        rows: [
          new TableRow({
            children: [
              createCell("Performance Software Calculations", 9360, { bold: true, shading: "E7E6E6", colSpan: 2 })
            ]
          }),
          new TableRow({
            children: [
              createCell("Software Title:", 4680),
              createCell("Version:", 4680)
            ]
          }),
          new TableRow({
            children: [
              createCell("Is software HOT2000v11 or ANSI/ASHRAE 140 compliant?", 4680),
              createCell("☐ Yes    ☐ No", 4680)
            ]
          }),
          new TableRow({
            children: [
              createCell("Annual Energy Consumption (GJ/yr):", 4680),
              new TableCell({
                borders: cellBorders,
                width: { size: 4680, type: WidthType.DXA },
                children: [
                  new Paragraph({
                    children: [
                      new TextRun({ text: "Reference House: ______", size: 20 }),
                      new TextRun({ text: " > ", size: 20, bold: true }),
                      new TextRun({ text: "Proposed House: ______", size: 20 })
                    ]
                  })
                ]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 9360, type: WidthType.DXA },
                columnSpan: 2,
                children: [
                  new Paragraph({ children: [new TextRun("☐ Full house energy report (or equivalent) generated by approved software is attached", { size: 20 })] }),
                  new Paragraph({ children: [new TextRun("☐ Air tightness test report is attached (if applicable)", { size: 20 })] }),
                  new Paragraph({ children: [new TextRun("☐ (if pursuing Energy Tier ≥ 2) 9.36 Submittal Calculator attached, demonstrating Energy Tier of _______", { size: 20 })] })
                ]
              })
            ]
          })
        ]
      }),

      // Performance Energy Modeling Professional
      new Table({
        columnWidths: [2340, 2340, 2340, 2340],
        margins: { top: 50, bottom: 50, left: 100, right: 100 },
        rows: [
          new TableRow({
            children: [
              createCell("Performance Energy Modeling Professional", 9360, { bold: true, shading: "E7E6E6", colSpan: 4 })
            ]
          }),
          new TableRow({
            children: [
              createCell("Name:", 2340),
              createCell("", 2340),
              createCell("Company:", 2340),
              createCell("", 2340)
            ]
          }),
          new TableRow({
            children: [
              createCell("Phone:", 2340),
              createCell("", 2340),
              createCell("Email:", 2340),
              createCell("", 2340)
            ]
          }),
          new TableRow({
            children: [
              createCell("Accreditation or Evaluator/ Advisor/Rater License #:", 2340),
              createCell("", 7020, { colSpan: 3 })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 9360, type: WidthType.DXA },
                columnSpan: 4,
                children: [
                  new Paragraph({
                    children: [
                      new TextRun({
                        text: "I hereby certify that the calculations submitted were prepared in full accordance with the operation and procedures of the software and:",
                        italics: true,
                        size: 20
                      })
                    ]
                  }),
                  new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [
                      new TextRun({ text: "☐ ", italics: true, size: 20 }),
                      new TextRun({ text: "Subsection 9.36.5 of NBC 2020", italics: true, size: 20 }),
                      new TextRun({ text: "  OR  ", italics: true, size: 20 }),
                      new TextRun({ text: "☐ EnerGuide Rating System v15", italics: true, size: 20 })
                    ]
                  })
                ]
              })
            ]
          }),
          new TableRow({
            children: [
              createCell("Date:", 2340, { bold: true }),
              createCell("", 2340),
              createCell("Signature:", 2340, { bold: true }),
              createCell("", 2340)
            ]
          })
        ]
      }),

      // Designer section for Performance
      new Table({
        columnWidths: [2340, 2340, 2340, 2340],
        margins: { top: 50, bottom: 50, left: 100, right: 100 },
        rows: [
          new TableRow({
            children: [
              createCell("Designer(s) [name(s) & accreditation/licensing, of person(s) providing information herein to substantiate that design meets building code]", 9360, {
                bold: true, shading: "E7E6E6", colSpan: 4
              })
            ]
          }),
          new TableRow({
            children: [
              createCell("Name:", 2340),
              createCell("", 2340),
              createCell("Accreditation or licensing #:", 2340),
              createCell("", 2340)
            ]
          }),
          new TableRow({
            children: [
              createCell("Phone:", 2340),
              createCell("", 2340),
              createCell("Email:", 2340),
              createCell("", 2340)
            ]
          }),
          new TableRow({
            children: [
              createCell("Declaration of designer to have reviewed and take responsibility for the design work.", 9360, {
                italics: true, colSpan: 4
              })
            ]
          }),
          new TableRow({
            children: [
              createCell("Date:", 2340, { bold: true }),
              createCell("", 2340),
              createCell("Signature:", 2340, { bold: true }),
              createCell("", 2340)
            ]
          })
        ]
      }),

      // Footnotes for page 2-3
      new Paragraph({
        spacing: { before: 200 },
        children: [
          footnoteRef(2),
          new TextRun({ text: " For houses with 1 or 2 dwelling units, the Reference model's %FDWR shall be same as Proposed (if Proposed FDWR is 17-22%), or 17% (if Proposed FDWR is < 17%, or 22% (if Proposed FDWR is >22%).", size: 18 })
        ]
      }),
      new Paragraph({
        children: [
          footnoteRef(3),
          new TextRun({ text: " If provided in the Proposed house", size: 18 })
        ]
      }),
      new Paragraph({
        children: [
          footnoteRef(4),
          new TextRun({ text: " In accordance with Article 9.32.3.3. based on the number of bedrooms in the proposed house", size: 18 })
        ]
      }),

      // D.2 Prescriptive Compliance
      new Paragraph({
        spacing: { before: 300, after: 120 },
        children: [new TextRun({ text: "D.2  Prescriptive Compliance", bold: true, size: 22 })]
      }),

      // Effective Thermal Resistance table - this is complex, continuing...
      new Table({
        columnWidths: [1170, 1170, 1170, 1170, 1170, 1170, 1170, 1170, 1170, 1170],
        margins: { top: 50, bottom: 50, left: 100, right: 100 },
        rows: [
          new TableRow({
            children: [
              createCell("Effective Thermal Resistance of Opaque Assemblies (RSI)", 11700, { bold: true, shading: "E7E6E6", colSpan: 10 })
            ]
          }),
          new TableRow({
            children: [
              createCell("Assembly", 3510, { bold: true, colSpan: 3 }),
              createCell("Climate Zone", 7020, { bold: true, colSpan: 6, alignment: AlignmentType.CENTER }),
              createCell("Proposed\n(min. effective RSI)", 1170, { bold: true, shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("", 1170),
              createCell("", 1170),
              createCell("", 1170),
              createCell("4", 1170, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("5", 1170, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("6", 1170, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("7A", 1170, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("7B", 1170, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("8", 1170, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("", 1170, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Above-ground", 1170, { bold: true, shading: "E7E6E6", rowSpan: 9 }),
              createCell("Ceilings below attics", 1170, { rowSpan: 2 }),
              createCell("☐ w/out HRV", 1170),
              createCell("6.91", 1170, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("8.67", 2340, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 2 }),
              createCell("10.43", 2340, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 2 }),
              createCell("", 1170)
            ]
          }),
          new TableRow({
            children: [
              createCell("☐ w/ HRV", 1170),
              createCell("6.91", 2340, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 2 }),
              createCell("8.67", 2340, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 2 }),
              createCell("10.43", 1170, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("", 1170)
            ]
          }),
          new TableRow({
            children: [
              createCell("Cathedral ceilings, flat roofs", 2340, { colSpan: 2 }),
              createCell("4.67", 3510, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 3 }),
              createCell("5.02", 2340, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 2 }),
              createCell("", 1170)
            ]
          }),
          new TableRow({
            children: [
              createCell("Walls", 1170, { rowSpan: 2 }),
              createCell("☐ w/out HRV", 1170),
              createCell("2.78", 1170, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("3.08", 3510, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 3 }),
              createCell("3.85", 1170, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("", 1170)
            ]
          }),
          new TableRow({
            children: [
              createCell("☐ w/ HRV", 1170),
              createCell("2.78", 1170, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("2.97", 3510, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 3 }),
              createCell("3.08", 1170, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("", 1170)
            ]
          }),
          new TableRow({
            children: [
              createCell("Floors over unheated spaces", 2340, { colSpan: 2 }),
              createCell("4.67", 3510, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 3 }),
              createCell("5.02", 2340, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 2 }),
              createCell("", 1170)
            ]
          }),
          new TableRow({
            children: [
              createCell("Below-Grade or in Contact with Ground", 1170, { bold: true, shading: "E7E6E6", rowSpan: 9 }),
              createCell("Foundation walls", 1170, { rowSpan: 2 }),
              createCell("☐ w/out HRV", 1170),
              createCell("1.99", 1170, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("2.98", 2340, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 2 }),
              createCell("3.46", 1170, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("3.97", 1170, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("", 1170)
            ]
          }),
          new TableRow({
            children: [
              createCell("☐ w/ HRV", 1170),
              createCell("1.99", 1170, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("2.98", 4680, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 4 }),
              createCell("", 1170)
            ]
          }),
          new TableRow({
            children: [
              createCell("Unheated floors", 1170, { rowSpan: 2 }),
              createCell("below frost line", 1170),
              createCell("Uninsulated", 7020, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 6 }),
              createCell("", 1170)
            ]
          }),
          new TableRow({
            children: [
              createCell("above frost line", 1170),
              createCell("1.96", 7020, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 6 }),
              createCell("", 1170)
            ]
          }),
          new TableRow({
            children: [
              createCell("Floors on permafrost", 2340, { colSpan: 2 }),
              createCell("n/a", 4680, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 4 }),
              createCell("4.44", 1170, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("", 1170)
            ]
          }),
          new TableRow({
            children: [
              createCell("Heated floors", 2340, { colSpan: 2 }),
              createCell("2.32", 3510, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 3 }),
              createCell("2.84", 2340, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 2 }),
              createCell("", 1170)
            ]
          }),
          new TableRow({
            children: [
              createCell("Slabs-on-grade w/ integr. footing", 1170, { rowSpan: 2 }),
              createCell("☐ w/out HRV", 1170),
              createCell("1.96", 3510, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 3 }),
              createCell("3.72", 1170, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("4.59", 1170, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("", 1170)
            ]
          }),
          new TableRow({
            children: [
              createCell("☐ w/ HRV", 1170),
              createCell("1.96", 3510, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 3 }),
              createCell("2.84", 1170, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("3.72", 1170, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("", 1170)
            ]
          })
        ]
      }),

      // Thermal Characteristics of Fenestration table
      new Table({
        columnWidths: [2730, 1170, 1170, 1170, 1170, 1170, 1170, 1170],
        margins: { top: 50, bottom: 50, left: 100, right: 100 },
        rows: [
          new TableRow({
            children: [
              createCell("Thermal Characteristics of Fenestration, Doors and Skylights (U-value, ER)", 9360, { bold: true, shading: "E7E6E6", colSpan: 8 })
            ]
          }),
          new TableRow({
            children: [
              createCell("Assembly", 2730, { bold: true }),
              createCell("Climate Zone", 5850, { bold: true, colSpan: 6, alignment: AlignmentType.CENTER }),
              createCell("Proposed\n(max. U or min. ER)", 1170, { bold: true })
            ]
          }),
          new TableRow({
            children: [
              createCell("", 2730),
              createCell("4", 1170, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("5", 1170, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("6", 1170, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("7A", 1170, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("7B", 1170, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("8", 1170, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("", 1170, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Fenestration & doors", 2730, { rowSpan: 2 }),
              createCell("Max. U-value", 1170, { colSpan: 2 }),
              createCell("1.84", 2340, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 2 }),
              createCell("1.61", 2340, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 2 }),
              createCell("1.44", 1170, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("", 1170, { rowSpan: 2 })
            ]
          }),
          new TableRow({
            children: [
              createCell("Min. Energy Rating", 1170, { colSpan: 2 }),
              createCell("21", 2340, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 2 }),
              createCell("25", 2340, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 2 }),
              createCell("29", 1170, { shading: "E7E6E6", alignment: AlignmentType.CENTER })
            ]
          }),
          new TableRow({
            children: [
              createCell("Skylights (Max. U-value)", 2730),
              createCell("2.92", 2340, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 2 }),
              createCell("2.75", 2340, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 2 }),
              createCell("2.41", 1170, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
              createCell("", 1170)
            ]
          }),
          new TableRow({
            children: [
              createCell("One door exception (Max. U-value)", 2730),
              createCell("2.6", 5850, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 5 }),
              createCell("", 1170)
            ]
          }),
          new TableRow({
            children: [
              createCell("Access hatches (Min. RSIeff)", 2730),
              createCell("2.6", 5850, { shading: "E7E6E6", alignment: AlignmentType.CENTER, colSpan: 5 }),
              createCell("", 1170)
            ]
          })
        ]
      }),

      // HVAC Equipment Efficiency Requirements
      new Table({
        columnWidths: [780, 3120, 1560, 1560, 1560, 2340],
        margins: { top: 50, bottom: 50, left: 100, right: 100 },
        rows: [
          new TableRow({
            children: [
              createCell("HVAC Equipment Efficiency Requirements", 10920, { bold: true, shading: "E7E6E6", colSpan: 6 })
            ]
          }),
          new TableRow({
            children: [
              createCell("Equipment", 3900, { bold: true, colSpan: 2 }),
              createCell("Capacity kW", 1560, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("Standard", 1560, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("Min. Efficiency", 1560, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("Proposed\n(fuel & equipment type, efficiency)", 2340, { bold: true, shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Furnace", 780, { bold: true, rowSpan: 3 }),
              createCell("Gas-fired", 1560),
              createCell("≤ 66", 1560, { alignment: AlignmentType.CENTER, rowSpan: 2, shading: "E7E6E6" }),
              createCell("CSA P.2", 1560, { alignment: AlignmentType.CENTER, rowSpan: 2, shading: "E7E6E6" }),
              new TableCell({
                borders: cellBorders,
                width: { size: 1560, type: WidthType.DXA },
                shading: { fill: "E7E6E6", type: ShadingType.CLEAR },
                children: [
                  new Paragraph({
                    children: [
                      new TextRun({ text: "AFUE ≥ 95%", size: 20 }),
                      footnoteRef(5)
                    ]
                  })
                ]
              }),
              createCell("", 2340)
            ]
          }),
          new TableRow({
            children: [
              createCell("Oil-fired", 1560),
              createCell("AFUE ≥ 85%", 1560, { shading: "E7E6E6" }),
              createCell("", 2340)
            ]
          }),
          new TableRow({
            children: [
              createCell("Electric", 1560),
              createCell("≤ 66", 1560, { alignment: AlignmentType.CENTER, shading: "E7E6E6" }),
              createCell("-", 1560, { alignment: AlignmentType.CENTER, shading: "E7E6E6" }),
              new TableCell({
                borders: cellBorders,
                width: { size: 1560, type: WidthType.DXA },
                shading: { fill: "E7E6E6", type: ShadingType.CLEAR },
                children: [
                  new Paragraph({
                    children: [
                      new TextRun({ text: "See footnote ", size: 20 }),
                      footnoteRef(5)
                    ]
                  })
                ]
              }),
              createCell("", 2340)
            ]
          }),
          new TableRow({
            children: [
              createCell("Boiler", 780, { bold: true, rowSpan: 3 }),
              createCell("Gas-fired", 1560),
              createCell("< 88", 1560, { alignment: AlignmentType.CENTER, rowSpan: 2, shading: "E7E6E6" }),
              createCell("CSA P.2", 1560, { alignment: AlignmentType.CENTER, rowSpan: 2, shading: "E7E6E6" }),
              createCell("AFUE ≥ 90%", 1560, { shading: "E7E6E6" }),
              createCell("", 2340)
            ]
          }),
          new TableRow({
            children: [
              createCell("Oil-fired", 1560),
              createCell("AFUE ≥ 86%", 1560, { shading: "E7E6E6" }),
              createCell("", 2340)
            ]
          }),
          new TableRow({
            children: [
              createCell("Electric", 1560),
              createCell("< 88", 1560, { alignment: AlignmentType.CENTER, shading: "E7E6E6" }),
              createCell("-", 1560, { alignment: AlignmentType.CENTER, shading: "E7E6E6" }),
              new TableCell({
                borders: cellBorders,
                width: { size: 1560, type: WidthType.DXA },
                shading: { fill: "E7E6E6", type: ShadingType.CLEAR },
                children: [
                  new Paragraph({
                    children: [
                      new TextRun({ text: "See footnote", size: 20 }),
                      footnoteRef(6)
                    ]
                  })
                ]
              }),
              createCell("", 2340)
            ]
          }),
          new TableRow({
            children: [
              createCell("Air source heat pump – split", 3900, { colSpan: 2 }),
              createCell("< 19", 1560, { alignment: AlignmentType.CENTER, shading: "E7E6E6" }),
              createCell("CSA C656", 1560, { alignment: AlignmentType.CENTER, shading: "E7E6E6" }),
              createCell("HSPF V ≥ 7.1", 1560, { shading: "E7E6E6" }),
              createCell("", 2340)
            ]
          }),
          new TableRow({
            children: [
              createCell("Combined space- and water-heating systems", 3900, { colSpan: 2 }),
              createCell("≤ 87.9 (boiler), or\n≤ 73.2 (service water heater)", 1560, { shading: "E7E6E6" }),
              createCell("CSA-P.9", 1560, { alignment: AlignmentType.CENTER, shading: "E7E6E6" }),
              createCell("TPF ≥ 0.80", 1560, { shading: "E7E6E6" }),
              createCell("", 2340)
            ]
          }),
          new TableRow({
            children: [
              createCell("Heat Recovery Ventilation", 3900, { colSpan: 2 }),
              createCell("-", 1560, { alignment: AlignmentType.CENTER, shading: "E7E6E6" }),
              createCell("CSA-C439", 1560, { alignment: AlignmentType.CENTER, shading: "E7E6E6" }),
              new TableCell({
                borders: cellBorders,
                width: { size: 1560, type: WidthType.DXA },
                shading: { fill: "E7E6E6", type: ShadingType.CLEAR },
                children: [
                  new Paragraph({ children: [new TextRun("@0°C", { size: 20 })] }),
                  new Paragraph({ children: [new TextRun("60 %SRE", { size: 20, bold: true })] }),
                  new Paragraph({ children: [new TextRun("@-25°C", { size: 20 })] }),
                  new Paragraph({
                    children: [
                      new TextRun({ text: "55 %SRE", size: 20, bold: true }),
                      footnoteRef(7)
                    ]
                  })
                ]
              }),
              createCell("", 2340)
            ]
          }),
          new TableRow({
            children: [
              createCell("(Other)", 3900, { colSpan: 2 }),
              createCell("", 1560, { shading: "E7E6E6" }),
              createCell("", 1560, { shading: "E7E6E6" }),
              createCell("", 1560, { shading: "E7E6E6" }),
              createCell("", 2340)
            ]
          })
        ]
      }),

      // Service Water Heater Efficiency Requirements
      new Table({
        columnWidths: [780, 3120, 1560, 1560, 1560, 2340],
        margins: { top: 50, bottom: 50, left: 100, right: 100 },
        rows: [
          new TableRow({
            children: [
              createCell("Service Water Heater Efficiency Requirements", 10920, { bold: true, shading: "E7E6E6", colSpan: 6 })
            ]
          }),
          new TableRow({
            children: [
              createCell("Equipment", 3900, { bold: true, colSpan: 2 }),
              createCell("Capacity", 1560, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("Standard", 1560, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("Min. Efficiency", 1560, { bold: true, alignment: AlignmentType.CENTER }),
              createCell("Proposed\n(fuel & equipment type, efficiency)", 2340, { bold: true, shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Tank Storage", 780, { bold: true, rowSpan: 6 }),
              createCell("Electric\n(≤ 12 kW)", 1560, { rowSpan: 4 }),
              createCell("50-270L", 1560, { alignment: AlignmentType.CENTER, rowSpan: 2, shading: "E7E6E6" }),
              createCell("CSA-C191", 1560, { alignment: AlignmentType.CENTER, rowSpan: 4, shading: "E7E6E6" }),
              createCell("SL ≤ 35+0.20V (top in.)", 1560, { shading: "E7E6E6" }),
              createCell("", 2340, { rowSpan: 4 })
            ]
          }),
          new TableRow({
            children: [
              createCell("SL ≤ 40+0.20V (bottom in.)", 1560, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("270-454L", 1560, { alignment: AlignmentType.CENTER, rowSpan: 2, shading: "E7E6E6" }),
              createCell("SL ≤ 0.472V-38.5 (top in.)", 1560, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("SL ≤ 0.472V-33.5 (bottom in.)", 1560, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Gas-fired (≤ 22 kW)", 1560, { rowSpan: 3 }),
              createCell("1st hr <68 L", 1560, { alignment: AlignmentType.CENTER, shading: "E7E6E6" }),
              createCell("CSA-P.3", 1560, { alignment: AlignmentType.CENTER, rowSpan: 3, shading: "E7E6E6" }),
              createCell("UEF ≥ 0.3456 – 0.00053V", 1560, { shading: "E7E6E6" }),
              createCell("", 2340, { rowSpan: 3 })
            ]
          }),
          new TableRow({
            children: [
              createCell("1st hr 68-192 L", 1560, { alignment: AlignmentType.CENTER, shading: "E7E6E6" }),
              createCell("UEF ≥ 0.5982 – 0.00050V", 1560, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("1st hr 193-283 L", 1560, { alignment: AlignmentType.CENTER, shading: "E7E6E6" }),
              createCell("UEF ≥ 0.6483 – 0.00045V", 1560, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Tankless, gas-fired (≤ 58.6 kW)", 3900, { colSpan: 2 }),
              createCell("< 6.4 L/min", 1560, { alignment: AlignmentType.CENTER, shading: "E7E6E6" }),
              createCell("CSA-P.3", 1560, { alignment: AlignmentType.CENTER, rowSpan: 2, shading: "E7E6E6" }),
              createCell("UEF ≥ 0.86", 1560, { shading: "E7E6E6" }),
              createCell("", 2340, { rowSpan: 2 })
            ]
          }),
          new TableRow({
            children: [
              createCell("", 3900, { colSpan: 2 }),
              createCell("≥ 6.4 L/min", 1560, { alignment: AlignmentType.CENTER, shading: "E7E6E6" }),
              createCell("UEF ≥ 0.87", 1560, { shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("Heat pump water heaters", 3900, { colSpan: 2 }),
              createCell("≤24 A and ≤250 V", 1560, { alignment: AlignmentType.CENTER, shading: "E7E6E6" }),
              createCell("CSA-C745", 1560, { alignment: AlignmentType.CENTER, shading: "E7E6E6" }),
              createCell("EF ≥ 2.1", 1560, { shading: "E7E6E6" }),
              createCell("", 2340)
            ]
          }),
          new TableRow({
            children: [
              createCell("(Other)", 3900, { colSpan: 2 }),
              createCell("", 1560, { shading: "E7E6E6" }),
              createCell("", 1560, { shading: "E7E6E6" }),
              createCell("", 1560, { shading: "E7E6E6" }),
              createCell("", 2340)
            ]
          })
        ]
      }),

      // Tiered Energy Compliance
      new Table({
        columnWidths: [9360],
        margins: { top: 50, bottom: 50, left: 100, right: 100 },
        rows: [
          new TableRow({
            children: [
              createCell("Tiered Energy Compliance – Prescriptive Path", 9360, { bold: true, shading: "E7E6E6" })
            ]
          }),
          new TableRow({
            children: [
              createCell("(if pursuing Energy Tier ≥ 2) Energy Tier Achieved: _______  (from 9.36 Submittal Calculator – 9.36.8 tab)", 9360)
            ]
          })
        ]
      }),

      // Final Designer section
      new Table({
        columnWidths: [2340, 2340, 2340, 2340],
        margins: { top: 50, bottom: 50, left: 100, right: 100 },
        rows: [
          new TableRow({
            children: [
              createCell("Designer(s) [name(s) & accreditation/licensing of person(s) providing information herein to substantiate that design meets building code]", 9360, {
                bold: true, shading: "E7E6E6", colSpan: 4
              })
            ]
          }),
          new TableRow({
            children: [
              createCell("Name:", 2340),
              createCell("", 2340),
              createCell("Accreditation or licensing #:", 2340),
              createCell("", 2340)
            ]
          }),
          new TableRow({
            children: [
              createCell("Phone:", 2340),
              createCell("", 2340),
              createCell("Email:", 2340),
              createCell("", 2340)
            ]
          }),
          new TableRow({
            children: [
              createCell("Declaration of designer to have reviewed and take responsibility for the design work.", 9360, {
                italics: true, colSpan: 4
              })
            ]
          }),
          new TableRow({
            children: [
              createCell("Date:", 2340, { bold: true }),
              createCell("", 2340),
              createCell("Signature:", 2340, { bold: true }),
              createCell("", 2340)
            ]
          })
        ]
      }),

      // Final footnotes
      new Paragraph({
        spacing: { before: 200 },
        children: [
          footnoteRef(5),
          new TextRun({ text: " Must be equipped with a high-efficiency constant torque or constant airflow fan motor", size: 18 })
        ]
      }),
      new Paragraph({
        children: [
          footnoteRef(6),
          new TextRun({ text: " Must be equipped with automatic water temperature control", size: 18 })
        ]
      }),
      new Paragraph({
        children: [
          footnoteRef(7),
          new TextRun({ text: " Only required for locations with a 2.5% January design temperature of less than -10°C", size: 18 })
        ]
      })
    ]
  }]
});

// Save the document
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("form_recreated_v4.docx", buffer);
  console.log("Form generated successfully: form_recreated_v4.docx");
});
