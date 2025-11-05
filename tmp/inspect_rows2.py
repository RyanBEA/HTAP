import zipfile
import xml.etree.ElementTree as ET
import sys

ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile('complianceReporting/form_template.docx') as z:
    root=ET.fromstring(z.read('word/document.xml'))
    tbl=root.findall('.//w:tbl', ns)[14]
    for key in ['T14_R11_C4','T14_R12_C4','T14_R13_C4','T14_R14_C4','T14_R15_C6','T14_R16_C6','T14_R20_C5','T14_R21_C5','T14_R22_C4','T14_R23_C2','T14_R24_C2']:
        for row_idx, tr in enumerate(tbl.findall('./w:tr', ns)):
            cells=tr.findall('./w:tc', ns)
            for col_idx, cell in enumerate(cells):
                text=' '.join((t.text or '') for t in cell.findall('.//w:t', ns))
                if '{{'+key+'}}' in text:
                    sys.stdout.buffer.write(f'[{key}] row {row_idx}\n'.encode('utf-8'))
                    for idx, c in enumerate(cells):
                        t=' '.join((tt.text or '') for tt in c.findall('.//w:t', ns))
                        sys.stdout.buffer.write(f'  col {idx}: {t}\n'.encode('utf-8'))
                    break
