// Generate complete NBC 2020 form with all 9 validated tables
const fs = require('fs');

// Read the three validated test files
const remainingCode = fs.readFileSync('testRemainingTables.js', 'utf8');
const table4Code = fs.readFileSync('testTable4Complete.js', 'utf8');
const table7Code = fs.readFileSync('testTable7Complete.js', 'utf8');

// Extract the header (requires, helpers, borders)
const headerMatch = table4Code.match(/^const fs.*?function footnoteRef[\s\S]*?\}/m);
const header = headerMatch ? headerMatch[0] : '';

// Extract table definitions using a simpler approach
console.log('Extracting table definitions...');

// Get lines for each table from the source files
const getLines = (content, start, end) => {
  const lines = content.split('\n');
  return lines.slice(start - 1, end).join('\n');
};

// Tables 1, 2, 3 from testRemainingTables.js
const table1Def = getLines(remainingCode, 45, 77);
const table2Def = getLines(remainingCode, 79, 117);
const table3Def = getLines(remainingCode, 119, 212);

// Table 4 from testTable4Complete.js
const table4Rows = getLines(table4Code, 46, 456);
const table4Table = getLines(table4Code, 458, 463);

// Tables 5, 6 from testRemainingTables.js
const table5Def = getLines(remainingCode, 214, 260);
const table6Def = getLines(remainingCode, 262, 366);

// Table 7 from testTable7Complete.js
const table7Rows = getLines(table7Code, 46, 537);
const table7Table = getLines(table7Code, 539, 544);

// Tables 8, 9 from testRemainingTables.js
const table8Def = getLines(remainingCode, 368, 385);
const table9Def = getLines(remainingCode, 387, 433);

// Build the complete file
const completeScript = `${header}

console.log('Generating complete NBC 2020 form with all 9 tables...');

// Column width helpers
const colWidth2 = 1560;
const colWidth3 = 1337;
const colWidth5 = 2340;
const colWidth6 = 1170;
const colWidth9 = 1560;

${table1Def}

${table2Def}

${table3Def}

${table4Rows}

${table4Table}

${table5Def}

${table6Def}

${table7Rows}

${table7Table}

${table8Def}

${table9Def}

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
`;

fs.writeFileSync('generatedComplete.js', completeScript);
console.log('✓ Created generatedComplete.js');
console.log('Running it to generate the complete document...');

