import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

def write(line):
    sys.stdout.buffer.write((line + "\n").encode('utf-8'))

ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile('complianceReporting/form_template.docx') as z:
    root = ET.fromstring(z.read('word/document.xml'))
field_map = json.loads(Path('complianceReporting/form_template_fields.json').read_text())
rows = []
for key, meta in field_map.items():
    tbl = root.findall('.//w:tbl', ns)[meta['table']]
    tr = tbl.findall('./w:tr', ns)[meta['row']]
    cells = tr.findall('./w:tc', ns)
    context = []
    for idx in range(meta['column']):
        txt = ' '.join((t.text or '') for t in cells[idx].findall('.//w:t', ns)).strip()
        if txt:
            context.append(' '.join(txt.split()))
    rows.append((key, ' | '.join(context)))
for key, ctx in sorted(rows):
    write(f"{key}\t{ctx}")
