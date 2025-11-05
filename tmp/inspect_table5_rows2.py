import zipfile
import xml.etree.ElementTree as ET
import sys
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile('complianceReporting/form_template.docx') as z:
    root=ET.fromstring(z.read('word/document.xml'))
    tbl=root.findall('.//w:tbl', ns)[5]
    for row_idx, tr in enumerate(tbl.findall('./w:tr', ns)):
        if row_idx in (25, 26, 27, 28, 29, 30, 31, 33,34,35,36,37):
            sys.stdout.buffer.write(f'row {row_idx}\n'.encode('utf-8'))
            for idx, cell in enumerate(tr.findall('./w:tc', ns)):
                text=' '.join((t.text or '') for t in cell.findall('.//w:t', ns))
                sys.stdout.buffer.write(f'  col {idx}: {text}\n'.encode('utf-8'))
