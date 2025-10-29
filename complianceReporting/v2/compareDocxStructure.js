const fs = require('fs');
const xml2js = require('xml2js');

async function parseXML(filePath) {
  const xml = fs.readFileSync(filePath, 'utf8');
  const parser = new xml2js.Parser({ explicitArray: false });
  return await parser.parseStringPromise(xml);
}

function extractTableStructure(doc) {
  const body = doc['w:document']['w:body'];
  const elements = Array.isArray(body) ? body : [body];

  const tables = [];
  let tableIndex = 0;

  // Flatten body elements
  const bodyElements = [];
  for (const el of elements) {
    if (el['w:tbl']) {
      const tbls = Array.isArray(el['w:tbl']) ? el['w:tbl'] : [el['w:tbl']];
      bodyElements.push(...tbls.map(t => ({ type: 'table', data: t })));
    } else if (el['w:p']) {
      const paras = Array.isArray(el['w:p']) ? el['w:p'] : [el['w:p']];
      bodyElements.push(...paras.map(p => ({ type: 'paragraph', data: p })));
    }
  }

  // Extract tables from body
  const bodyContent = body['w:tbl'] || [];
  const tablesToProcess = Array.isArray(bodyContent) ? bodyContent : [bodyContent];

  for (const table of tablesToProcess) {
    if (!table) continue;

    const tblPr = table['w:tblPr'] || {};
    const tblGrid = table['w:tblGrid'] || {};
    const tblRows = table['w:tr'];

    // Get grid columns
    const gridCols = tblGrid['w:gridCol'] || [];
    const gridColArray = Array.isArray(gridCols) ? gridCols : [gridCols];
    const columnCount = gridColArray.length;

    // Get rows
    const rows = Array.isArray(tblRows) ? tblRows : [tblRows];
    const rowCount = rows.length;

    // Analyze each row
    const rowStructures = rows.map((row, rowIdx) => {
      if (!row || !row['w:tc']) return null;

      const cells = Array.isArray(row['w:tc']) ? row['w:tc'] : [row['w:tc']];
      const cellStructures = cells.map(cell => {
        const tcPr = cell['w:tcPr'] || {};
        const gridSpan = tcPr['w:gridSpan'] ? parseInt(tcPr['w:gridSpan']['$']['w:val'] || '1') : 1;
        const vMerge = tcPr['w:vMerge'] ? (tcPr['w:vMerge']['$'] ? tcPr['w:vMerge']['$']['w:val'] : 'continue') : null;

        // Get cell text
        const cellText = extractCellText(cell);

        return {
          gridSpan,
          vMerge,
          text: cellText
        };
      });

      return {
        rowIndex: rowIdx,
        cellCount: cells.length,
        cells: cellStructures
      };
    }).filter(r => r !== null);

    tableIndex++;
    tables.push({
      tableIndex,
      columnCount,
      rowCount,
      rows: rowStructures
    });
  }

  return tables;
}

function extractCellText(cell) {
  try {
    const paragraphs = cell['w:p'];
    if (!paragraphs) return '';

    const paraArray = Array.isArray(paragraphs) ? paragraphs : [paragraphs];
    const texts = paraArray.map(p => {
      if (!p['w:r']) return '';
      const runs = Array.isArray(p['w:r']) ? p['w:r'] : [p['w:r']];
      return runs.map(r => {
        if (r['w:t']) {
          return typeof r['w:t'] === 'string' ? r['w:t'] : r['w:t']['_'] || '';
        }
        return '';
      }).join('');
    });

    return texts.join(' ').trim().substring(0, 50); // First 50 chars
  } catch (e) {
    return '[error extracting text]';
  }
}

function compareTables(original, recreated) {
  const issues = [];

  if (original.length !== recreated.length) {
    issues.push({
      type: 'TABLE_COUNT_MISMATCH',
      severity: 'HIGH',
      message: `Table count mismatch: Original has ${original.length}, Recreated has ${recreated.length}`
    });
  }

  const minLength = Math.min(original.length, recreated.length);

  for (let i = 0; i < minLength; i++) {
    const origTable = original[i];
    const recTable = recreated[i];

    if (origTable.columnCount !== recTable.columnCount) {
      issues.push({
        type: 'COLUMN_COUNT_MISMATCH',
        severity: 'HIGH',
        table: i + 1,
        message: `Table ${i + 1}: Column count mismatch - Original: ${origTable.columnCount}, Recreated: ${recTable.columnCount}`
      });
    }

    if (origTable.rowCount !== recTable.rowCount) {
      issues.push({
        type: 'ROW_COUNT_MISMATCH',
        severity: 'HIGH',
        table: i + 1,
        message: `Table ${i + 1}: Row count mismatch - Original: ${origTable.rowCount}, Recreated: ${recTable.rowCount}`
      });
    }

    // Compare row structures
    const minRows = Math.min(origTable.rows.length, recTable.rows.length);
    for (let r = 0; r < minRows; r++) {
      const origRow = origTable.rows[r];
      const recRow = recTable.rows[r];

      if (origRow.cellCount !== recRow.cellCount) {
        issues.push({
          type: 'CELL_COUNT_MISMATCH',
          severity: 'MEDIUM',
          table: i + 1,
          row: r + 1,
          message: `Table ${i + 1}, Row ${r + 1}: Cell count mismatch - Original: ${origRow.cellCount}, Recreated: ${recRow.cellCount}`
        });
      }

      // Compare cell spans
      const minCells = Math.min(origRow.cells.length, recRow.cells.length);
      for (let c = 0; c < minCells; c++) {
        const origCell = origRow.cells[c];
        const recCell = recRow.cells[c];

        if (origCell.gridSpan !== recCell.gridSpan) {
          issues.push({
            type: 'GRIDSPAN_MISMATCH',
            severity: 'MEDIUM',
            table: i + 1,
            row: r + 1,
            cell: c + 1,
            message: `Table ${i + 1}, Row ${r + 1}, Cell ${c + 1}: GridSpan mismatch - Original: ${origCell.gridSpan}, Recreated: ${recCell.gridSpan}`,
            originalText: origCell.text,
            recreatedText: recCell.text
          });
        }

        if (origCell.vMerge !== recCell.vMerge) {
          issues.push({
            type: 'VMERGE_MISMATCH',
            severity: 'MEDIUM',
            table: i + 1,
            row: r + 1,
            cell: c + 1,
            message: `Table ${i + 1}, Row ${r + 1}, Cell ${c + 1}: vMerge mismatch - Original: ${origCell.vMerge}, Recreated: ${recCell.vMerge}`
          });
        }
      }
    }
  }

  return issues;
}

async function main() {
  console.log('Comparing DOCX table structures...\n');

  const originalDoc = await parseXML('unpacked_original/word/document.xml');
  const recreatedDoc = await parseXML('unpacked_v4/word/document.xml');

  const originalTables = extractTableStructure(originalDoc);
  const recreatedTables = extractTableStructure(recreatedDoc);

  console.log(`Original document: ${originalTables.length} tables`);
  console.log(`Recreated document: ${recreatedTables.length} tables\n`);

  // Output table summaries
  console.log('=== ORIGINAL TABLES ===');
  originalTables.forEach((t, i) => {
    console.log(`Table ${i + 1}: ${t.columnCount} columns, ${t.rowCount} rows`);
  });

  console.log('\n=== RECREATED TABLES ===');
  recreatedTables.forEach((t, i) => {
    console.log(`Table ${i + 1}: ${t.columnCount} columns, ${t.rowCount} rows`);
  });

  // Compare and find issues
  const issues = compareTables(originalTables, recreatedTables);

  console.log('\n=== ISSUES FOUND ===');
  if (issues.length === 0) {
    console.log('No structural differences found!');
  } else {
    console.log(`Found ${issues.length} issues:\n`);

    const highSeverity = issues.filter(i => i.severity === 'HIGH');
    const mediumSeverity = issues.filter(i => i.severity === 'MEDIUM');

    if (highSeverity.length > 0) {
      console.log('HIGH SEVERITY ISSUES:');
      highSeverity.forEach(issue => {
        console.log(`  [${issue.type}] ${issue.message}`);
      });
      console.log('');
    }

    if (mediumSeverity.length > 0) {
      console.log('MEDIUM SEVERITY ISSUES:');
      mediumSeverity.forEach(issue => {
        console.log(`  [${issue.type}] ${issue.message}`);
        if (issue.originalText && issue.recreatedText) {
          console.log(`    Original text: "${issue.originalText}"`);
          console.log(`    Recreated text: "${issue.recreatedText}"`);
        }
      });
    }
  }

  // Save detailed report
  const report = {
    summary: {
      originalTableCount: originalTables.length,
      recreatedTableCount: recreatedTables.length,
      issueCount: issues.length
    },
    originalTables,
    recreatedTables,
    issues
  };

  fs.writeFileSync('comparison-report.json', JSON.stringify(report, null, 2));
  console.log('\nDetailed report saved to comparison-report.json');
}

main().catch(console.error);
