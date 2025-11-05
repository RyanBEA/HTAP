import json
from pathlib import Path
import sys

field_map = json.loads(Path('complianceReporting/form_template_fields.json').read_text())
lines = []
for key, meta in sorted(field_map.items()):
    context = ' | '.join(filter(None, [meta.get('row_label',''), meta.get('column_label','')]))
    lines.append(f"    '{key}': '',  # {context}")

def write(chunk):
    sys.stdout.buffer.write((chunk + "\n").encode('utf-8'))

write('sample_values = {')
for line in lines:
    write(line)
write('}')
