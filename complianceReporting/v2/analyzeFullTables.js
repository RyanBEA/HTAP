const report = require('./comparison-report.json');
const fs = require('fs');

let output = '';

output += '=== COMPLETE TABLE 4 STRUCTURE (D.1 Performance Compliance) ===\n';
output += '9 columns, 40 rows\n\n';

const table4 = report.originalTables[3];
table4.rows.forEach((row, i) => {
  output += `Row ${i} (${row.cellCount} cells):\n`;
  let colCount = 0;
  row.cells.forEach((cell, j) => {
    output += `  Cell ${j}: span=${cell.gridSpan}, vMerge=${cell.vMerge}, text="${cell.text}"\n`;
    colCount += cell.gridSpan;
  });
  output += `  → Total span: ${colCount} columns\n\n`;
});

output += '\n\n=== COMPLETE TABLE 7 STRUCTURE (D.2 Effective Thermal Resistance) ===\n';
output += '19 columns, 51 rows\n\n';

const table7 = report.originalTables[6];
table7.rows.forEach((row, i) => {
  output += `Row ${i} (${row.cellCount} cells):\n`;
  let colCount = 0;
  row.cells.forEach((cell, j) => {
    output += `  Cell ${j}: span=${cell.gridSpan}, vMerge=${cell.vMerge}, text="${cell.text}"\n`;
    colCount += cell.gridSpan;
  });
  output += `  → Total span: ${colCount} columns\n\n`;
});

fs.writeFileSync('table-structures-complete.txt', output);
console.log('Complete table structures written to table-structures-complete.txt');
