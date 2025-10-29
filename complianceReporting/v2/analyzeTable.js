const report = require('./comparison-report.json');

console.log('=== ORIGINAL TABLE 4 (D.1 Performance Compliance) ===');
const table4 = report.originalTables[3];
console.log('Columns:', table4.columnCount);
console.log('Rows:', table4.rowCount);
console.log('\nFirst 10 rows structure:');
table4.rows.slice(0, 10).forEach((row, i) => {
  console.log(`\nRow ${i}: ${row.cellCount} cells`);
  row.cells.forEach((cell, j) => {
    console.log(`  Cell ${j}: gridSpan=${cell.gridSpan}, vMerge=${cell.vMerge}, text="${cell.text}"`);
  });
});

console.log('\n\n=== ORIGINAL TABLE 7 (D.2 Effective Thermal Resistance) ===');
const table7 = report.originalTables[6];
console.log('Columns:', table7.columnCount);
console.log('Rows:', table7.rowCount);
console.log('\nFirst 10 rows structure:');
table7.rows.slice(0, 10).forEach((row, i) => {
  console.log(`\nRow ${i}: ${row.cellCount} cells`);
  row.cells.forEach((cell, j) => {
    console.log(`  Cell ${j}: gridSpan=${cell.gridSpan}, vMerge=${cell.vMerge}, text="${cell.text}"`);
  });
});
