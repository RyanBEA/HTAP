const fs = require('fs');
const xml2js = require('xml2js');

const xmlContent = fs.readFileSync('unpacked_original/word/document.xml', 'utf8');

xml2js.parseString(xmlContent, (err, result) => {
  if (err) {
    console.error('Parse error:', err);
    return;
  }

  const body = result['w:document']['w:body'][0];
  const tables = body['w:tbl'];

  console.log('Total tables in original:', tables.length);

  // We want tables 0, 1, 2, 4, 5, 7, 8 (skipping 3=Table4 and 6=Table7)
  const tablesToAnalyze = [0, 1, 2, 4, 5, 7, 8];
  const tableNames = [
    'Table 1: Project Information',
    'Table 2: Project Design Conditions',
    'Table 3: Compliance Option',
    'Table 5: Additional Information',
    'Table 6: Performance Energy Modeling Professional',
    'Table 8: Tiered Energy Compliance',
    'Table 9: Designer Declaration'
  ];

  tablesToAnalyze.forEach((tableIdx, nameIdx) => {
    const table = tables[tableIdx];
    console.log(`\n=== ${tableNames[nameIdx]} ===`);

    // Get grid columns
    const tblGrid = table['w:tblGrid'][0]['w:gridCol'];
    const numCols = tblGrid ? tblGrid.length : 0;
    console.log(`Columns: ${numCols}`);

    // Get all rows
    const rows = table['w:tr'];
    console.log(`Rows: ${rows.length}`);

    // Analyze each row
    console.log('\nRow Details:');
    rows.forEach((row, rowIdx) => {
      const cells = row['w:tc'] || [];
      const cellInfo = [];
      let totalSpan = 0;

      cells.forEach((cell, cellIdx) => {
        const gridSpanAttr = cell['w:tcPr']?.[0]?.['w:gridSpan']?.[0]?.['$'];
        const vMergeAttr = cell['w:tcPr']?.[0]?.['w:vMerge']?.[0]?.['$'];
        const span = gridSpanAttr ? parseInt(gridSpanAttr['w:val']) : 1;
        const vMerge = vMergeAttr ? vMergeAttr['w:val'] || 'continue' : null;

        // Get cell text
        const paragraphs = cell['w:p'] || [];
        let text = '';
        paragraphs.forEach(p => {
          const runs = p['w:r'] || [];
          runs.forEach(r => {
            const t = r['w:t'];
            if (t) {
              text += Array.isArray(t) ? t.join('') : (t[0] || '');
            }
          });
        });

        totalSpan += span;
        cellInfo.push({ span, vMerge, text: text.substring(0, 50) });
      });

      console.log(`  Row ${rowIdx}: ${cells.length} cells, span=${totalSpan}`);
      cellInfo.forEach((info, idx) => {
        const vMergeStr = info.vMerge ? `, vMerge=${info.vMerge}` : '';
        console.log(`    Cell ${idx}: span=${info.span}${vMergeStr}, text="${info.text}"`);
      });
    });
  });
});
