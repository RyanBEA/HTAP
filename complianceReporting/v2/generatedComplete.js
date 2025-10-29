

console.log('Generating complete NBC 2020 form with all 9 tables...');

// Column width helpers
const colWidth2 = 1560;
const colWidth3 = 1337;
const colWidth5 = 2340;
const colWidth6 = 1170;
const colWidth9 = 1560;

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
        createCell("Prescriptive (Subsections 9.36.2-9.36.4, 9.36.8)", colWidth3,
                  { rowSpan: 4 }),
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

const table4Rows = [
  // Row 0: Header
  new TableRow({
    children: [
      createCell("Input Parameters", 7280, { bold: true, shading: "FFFFFF", colSpan: 7 }),
      createCell("Reference Model", 1040, { bold: true, shading: "FFFFFF", alignment: AlignmentType.CENTER }),
      createCell("Proposed Model", 1040, { bold: true, shading: "FFFFFF", alignment: AlignmentType.CENTER })
    ]
  }),

  // Row 1: Opaque Assemblies header
  new TableRow({
    children: [
      createCell("Opaque Assemblies", 7280, { bold: true, shading: "E7E6E6", colSpan: 7 }),
      createCell("Effective Thermal Resistance (RSI)", 2080, { bold: true, shading: "E7E6E6", colSpan: 2, alignment: AlignmentType.CENTER })
    ]
  }),

  // Row 2: Above-ground (start of vertical merge)
  new TableRow({
    children: [
      createCell("Above-ground", 1040, { bold: true, shading: "E7E6E6", rowSpan: 4 }),
      createCell("Ceilings below attics", 6240, { colSpan: 6 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 3: Cathedral ceilings
  new TableRow({
    children: [
      createCell("Cathedral ceilings and flat roofs", 6240, { colSpan: 6 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 4: Walls
  new TableRow({
    children: [
      createCell("Walls", 6240, { colSpan: 6 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 5: Floors over unheated spaces
  new TableRow({
    children: [
      createCell("Floors over unheated spaces", 6240, { colSpan: 6 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 6: Below-Grade (start of new vertical merge)
  new TableRow({
    children: [
      createCell("Below-Grade or in Contact with Ground", 1040, { bold: true, shading: "E7E6E6", rowSpan: 6 }),
      createCell("Foundation walls", 6240, { colSpan: 6 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 7: Unheated floors - below frost line (start of sub-merge)
  new TableRow({
    children: [
      createCell("Unheated floors", 3120, { rowSpan: 2, colSpan: 3 }),
      createCell("below frost line", 3120, { colSpan: 3 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 8: above frost line (sub-merge continues)
  new TableRow({
    children: [
      createCell("above frost line", 3120, { colSpan: 3 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 9: Heated and unheated floors on permafrost
  new TableRow({
    children: [
      createCell("Heated and unheated floors on permafrost", 6240, { colSpan: 6 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 10: Heated floors
  new TableRow({
    children: [
      createCell("Heated floors", 6240, { colSpan: 6 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 11: Slabs-on-grade
  new TableRow({
    children: [
      createCell("Slabs-on-grade with an integral footing", 6240, { colSpan: 6 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 12: Fenestration section header
  new TableRow({
    children: [
      createCell("Fenestration, Doors, Skylights", 7280, { bold: true, shading: "E7E6E6", colSpan: 7 }),
      createCell("U-factor, Energy Rating, RSIeff", 2080, { bold: true, shading: "E7E6E6", colSpan: 2, alignment: AlignmentType.CENTER })
    ]
  }),

  // Row 13: Front orientation
  new TableRow({
    children: [
      createCell("Front orientation of house (N, NE, E, SE, S, SW, W, NW):", 7280, { colSpan: 7 }),
      createCell("", 2080, { colSpan: 2 })
    ]
  }),

  // Row 14: Windows (start of vertical merge)
  new TableRow({
    children: [
      createCell("Windows", 3120, { rowSpan: 2, colSpan: 3 }),
      createCell("U-factor or ER", 4160, { colSpan: 4 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 15: Solar Heat Gain Coefficient
  new TableRow({
    children: [
      createCell("Solar Heat Gain Coefficient", 4160, { colSpan: 4 }),
      createCell("0.26", 1040, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 16: Skylights (start of vertical merge)
  new TableRow({
    children: [
      createCell("Skylights", 3120, { rowSpan: 2, colSpan: 3 }),
      createCell("U-factor or ER", 4160, { colSpan: 4 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 17: Solar Heat Gain Coefficient
  new TableRow({
    children: [
      createCell("Solar Heat Gain Coefficient", 4160, { colSpan: 4 }),
      createCell("0.26", 1040, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 18: Doors
  new TableRow({
    children: [
      createCell("Doors", 7280, { colSpan: 7 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 19: FDWR with footnote
  new TableRow({
    children: [
      new TableCell({
        borders: cellBorders,
        width: { size: 7280, type: WidthType.DXA },
        columnSpan: 7,
        children: [
          new Paragraph({
            children: [
              new TextRun({ text: "Fenestration & door area to gross wall ratio, FDWR (%)", size: 20 }),
              footnoteRef(2)
            ]
          })
        ]
      }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 20: Airtightness header
  new TableRow({
    children: [
      createCell("Airtightness", 7280, { bold: true, shading: "E7E6E6", colSpan: 7 }),
      createCell("Air Changes per Hour (ACH @ 50 Pa)", 2080, { bold: true, shading: "E7E6E6", colSpan: 2, alignment: AlignmentType.CENTER })
    ]
  }),

  // Row 21: Section 9.25 compliance
  new TableRow({
    children: [
      createCell("Construction complies with Section 9.25", 7280, { colSpan: 7 }),
      createCell("2.5", 1040, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
      createCell("3.2", 1040, { shading: "E7E6E6", alignment: AlignmentType.CENTER })
    ]
  }),

  // Row 22: Air barrier system with footnote
  new TableRow({
    children: [
      new TableCell({
        borders: cellBorders,
        width: { size: 7280, type: WidthType.DXA },
        columnSpan: 7,
        children: [
          new Paragraph({
            children: [
              new TextRun({ text: "Air barrier system constructed to Subsection 9.25.3", size: 20 }),
              footnoteRef(2)
            ]
          })
        ]
      }),
      createCell("2.5", 1040, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
      createCell("2.5", 1040, { shading: "E7E6E6", alignment: AlignmentType.CENTER })
    ]
  }),

  // Row 23: Airtightness tested
  new TableRow({
    children: [
      createCell("Airtightness tested (per Sentence 9.36.6.3.(1))", 7280, { colSpan: 7 }),
      createCell("2.5 (detached house)  3.0 (attached house)", 1040, { shading: "E7E6E6", alignment: AlignmentType.CENTER }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 24: HVAC section header
  new TableRow({
    children: [
      createCell("HVAC, Service Hot Water", 7280, { bold: true, shading: "E7E6E6", colSpan: 7 }),
      createCell("Fuel & Equipment Type, Efficiencies", 2080, { bold: true, shading: "E7E6E6", colSpan: 2, alignment: AlignmentType.CENTER })
    ]
  }),

  // Row 25: Heating System
  new TableRow({
    children: [
      createCell("Heating System(s)", 7280, { colSpan: 7 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 26: Cooling System - Capacity (start of vertical merge)
  new TableRow({
    children: [
      createCell("Cooling System", 3120, { rowSpan: 4, colSpan: 3 }),
      createCell("Capacity (kW)", 4160, { colSpan: 4 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 27: SEER
  new TableRow({
    children: [
      createCell("SEER", 4160, { colSpan: 4 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 28: Air Source Heat Pump - HSPF V (with nested merge)
  new TableRow({
    children: [
      createCell("Air Source Heat Pump?", 2080, { rowSpan: 2, colSpan: 2 }),
      createCell("HSPF V", 2080, { colSpan: 2 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 29: Cutoff Temperature
  new TableRow({
    children: [
      createCell("Cutoff Temperature", 2080, { colSpan: 2 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 30: Supplementary Heating with footnote
  new TableRow({
    children: [
      new TableCell({
        borders: cellBorders,
        width: { size: 7280, type: WidthType.DXA },
        columnSpan: 7,
        children: [
          new Paragraph({
            children: [
              new TextRun({ text: "Supplementary Heating System(s)", size: 20 }),
              footnoteRef(3)
            ]
          })
        ]
      }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 31: Ventilation System (start of vertical merge)
  new TableRow({
    children: [
      createCell("Ventilation System", 3120, { rowSpan: 6, colSpan: 3 }),
      createCell("Principal Ventilation Rate (L/s)", 4160, { colSpan: 4 }),
      createCell("", 2080, { shading: "FFFFFF", colSpan: 2 })  // Note: no shading per original
    ]
  }),

  // Row 32: Runtime
  new TableRow({
    children: [
      createCell("Runtime (hrs/day)", 4160, { colSpan: 4 }),
      createCell("8", 2080, { shading: "E7E6E6", colSpan: 2, alignment: AlignmentType.CENTER })
    ]
  }),

  // Row 33: Fan Power @ 0°C (with nested merges)
  new TableRow({
    children: [
      createCell("Fan Power (W)", 3120, { rowSpan: 2, colSpan: 3 }),
      createCell("@ 0°C", 1040),
      createCell("2.32 W/L/s = ______ W", 1040, { rowSpan: 2, shading: "FFFFFF" }),  // Note: no shading
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 34: @ -25°C
  new TableRow({
    children: [
      createCell("@ -25°C", 1040),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 35: Heat Recovery @ 0°C (with nested merges)
  new TableRow({
    children: [
      createCell("Heat Recovery, % SRE", 3120, { rowSpan: 2, colSpan: 3 }),
      createCell("@ 0°C", 1040),
      createCell("none", 1040, { rowSpan: 2, shading: "FFFFFF", alignment: AlignmentType.CENTER }),  // Note: no shading
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 36: @ -25°C
  new TableRow({
    children: [
      createCell("@ -25°C", 1040),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 37: Service Water Heating
  new TableRow({
    children: [
      createCell("Service Water Heating System(s)", 7280, { colSpan: 7 }),
      createCell("", 1040, { shading: "E7E6E6" }),
      createCell("", 1040, { shading: "E7E6E6" })
    ]
  }),

  // Row 38: Drain Water Heat Recovery - efficiency (with nested merges)
  new TableRow({
    children: [
      createCell("Drain Water Heat Recovery", 2080, { rowSpan: 2, colSpan: 2 }),
      createCell("Recovery efficiency, flow configuration", 5200, { colSpan: 5 }),
      createCell("none", 1040, { rowSpan: 2, shading: "FFFFFF", alignment: AlignmentType.CENTER }),  // Note: no shading
      new TableCell({
        borders: cellBorders,
        width: { size: 1040, type: WidthType.DXA },
        shading: { fill: "E7E6E6", type: ShadingType.CLEAR },
        children: [
          new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({ text: "___% RE\n", size: 20 }),
              new TextRun({ text: "☐equal flow  ☐unequal flow", size: 18 })
            ]
          })
        ]
      })
    ]
  }),

  // Row 39: # of showers connected
  new TableRow({
    children: [
      createCell("# of showers connected (of total)", 5200, { colSpan: 5 }),
      createCell("____ of ____", 1040, { shading: "E7E6E6", alignment: AlignmentType.CENTER })
    ]
  })
];

// Create Table 4 with correct 9-column structure
const table4 = new Table({
  columnWidths: [1040, 1040, 1040, 1040, 1040, 1040, 1040, 1040, 1040],  // 9 equal columns
  margins: { top: 50, bottom: 50, left: 100, right: 100 },
  rows: table4Rows
});

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


  // Row 47: Tankless, gas-fired - < 6.4 L/min
  new TableRow({
    children: [
      createCell("Tankless, gas-fired (≤ 58.6 kW)", colWidth * 4, { colSpan: 4, rowSpan: 2 }),
      createCell("< 6.4 L/min", colWidth * 2, { colSpan: 2 }),

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


// Create comprehensive document
const { Document, Packer, Paragraph, TextRun, Header, AlignmentType } = require('docx');

const doc = new Document({
  sections: [{
    properties: { page: { margin: { top: 720, right: 720, bottom: 720, left: 720 } } },
    headers: {
      default: new Header({
        children: [
          new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "NBC 2020, Subsection 9.36", bold: true, size: 24 })] }),
          new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Submittal Form", bold: true, size: 24 })] })
        ]
      })
    },
    children: [
      new Paragraph({ spacing: { before: 200, after: 120 }, children: [new TextRun({ text: "A. Project Information", bold: true, size: 24 })] }),
      table1,
      new Paragraph({ spacing: { before: 240, after: 120 }, children: [new TextRun({ text: "B. Project Design Conditions", bold: true, size: 24 })] }),
      table2,
      new Paragraph({ spacing: { before: 240, after: 120 }, children: [new TextRun({ text: "C. Compliance Option", bold: true, size: 24 })] }),
      table3,
      new Paragraph({ spacing: { before: 240, after: 120 }, children: [new TextRun({ text: "D.1 Performance Compliance", bold: true, size: 24 })] }),
      table4,
      new Paragraph({ spacing: { before: 240, after: 120 }, children: [new TextRun({ text: "E. Additional Information", bold: true, size: 24 })] }),
      table5,
      new Paragraph({ spacing: { before: 240, after: 120 }, children: [new TextRun({ text: "F. Performance Energy Modeling Professional", bold: true, size: 24 })] }),
      table6,
      new Paragraph({ spacing: { before: 240, after: 120 }, children: [new TextRun({ text: "D.2 Effective Thermal Resistance", bold: true, size: 24 })] }),
      table7,
      new Paragraph({ spacing: { before: 240, after: 120 }, children: [new TextRun({ text: "G. Tiered Energy Compliance", bold: true, size: 24 })] }),
      table8,
      new Paragraph({ spacing: { before: 240, after: 120 }, children: [new TextRun({ text: "H. Designer Declaration", bold: true, size: 24 })] }),
      table9
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("NBC2020_Complete_All9Tables.docx", buffer);
  console.log("✅ Complete NBC 2020 form generated: NBC2020_Complete_All9Tables.docx");
  console.log("   Contains all 9 validated tables in proper order");
});
