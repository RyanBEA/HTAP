"""
Utility to generate a programmatically fillable clone of complianceReporting/form.docx.

The script copies the original Word document, replaces every light blue data cell
(w:shd fill="DEEAF6") with a unique placeholder token, and writes both the cloned
document and a JSON mapping file describing each placeholder.
"""
from __future__ import annotations

import io
import json
import zipfile
from collections import OrderedDict
from pathlib import Path
import xml.etree.ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DOC = REPO_ROOT / "complianceReporting" / "form.docx"
TARGET_DOC = REPO_ROOT / "complianceReporting" / "form_template.docx"
FIELD_MAP_PATH = REPO_ROOT / "complianceReporting" / "form_template_fields.json"

FILLABLE_SHADE = "DEEAF6"


def load_namespaces(xml_bytes: bytes) -> dict[str, str]:
    """Collect namespace declarations so ElementTree preserves prefixes."""
    namespaces: dict[str, str] = {}
    for event, data in ET.iterparse(io.BytesIO(xml_bytes), events=("start-ns",)):
        prefix, uri = data
        if prefix in namespaces:
            continue
        namespaces[prefix or ""] = uri
        ET.register_namespace(prefix or "", uri)
    return namespaces


def text_in_element(element: ET.Element, ns: dict[str, str]) -> str:
    """Join the text of all w:t nodes within an element."""
    strings = []
    for node in element.findall(".//w:t", ns):
        if node.text:
            strings.append(node.text)
    return "".join(strings).strip()


def ensure_paragraph_with_placeholder(
    cell: ET.Element, placeholder: str, w_namespace: str, ns: dict[str, str]
) -> None:
    """
    Ensure the table cell contains a single run with the provided placeholder text.

    Existing runs are dropped but paragraph properties (alignment, styling) are preserved.
    """
    paragraph = cell.find("./w:p", ns)
    if paragraph is None:
        paragraph = ET.SubElement(cell, f"{{{w_namespace}}}p")
    for child in list(paragraph):
        if child.tag == f"{{{w_namespace}}}pPr":
            continue
        paragraph.remove(child)
    run = ET.SubElement(paragraph, f"{{{w_namespace}}}r")
    text = ET.SubElement(run, f"{{{w_namespace}}}t")
    text.text = placeholder


def build_fillable_template() -> None:
    if not SOURCE_DOC.exists():
        raise FileNotFoundError(f"Missing source document: {SOURCE_DOC}")

    with zipfile.ZipFile(SOURCE_DOC, "r") as zin:
        document_xml = zin.read("word/document.xml")

    namespaces = load_namespaces(document_xml)
    w_namespace = namespaces["w"]
    ns = {"w": w_namespace}

    root = ET.fromstring(document_xml)

    field_map: dict[str, dict[str, int | str]] = {}

    for table_index, table in enumerate(root.findall(".//w:tbl", ns)):
        rows = table.findall("./w:tr", ns)
        header_cells = rows[0].findall("./w:tc", ns) if rows else []

        for row_index, row in enumerate(rows):
            cells = row.findall("./w:tc", ns)
            row_label = ""
            if cells:
                row_label = text_in_element(cells[0], ns)

            for column_index, cell in enumerate(cells):
                shade = cell.find("./w:tcPr/w:shd", ns)
                fill_value = (
                    shade.get(f"{{{w_namespace}}}fill") if shade is not None else None
                )
                if fill_value != FILLABLE_SHADE:
                    continue

                field_id = f"T{table_index}_R{row_index}_C{column_index}"
                placeholder_text = "{{" + field_id + "}}"

                ensure_paragraph_with_placeholder(
                    cell, placeholder_text, w_namespace, ns
                )

                column_label = ""
                if column_index < len(header_cells):
                    column_label = text_in_element(header_cells[column_index], ns)

                field_map[field_id] = {
                    "table": table_index,
                    "row": row_index,
                    "column": column_index,
                    "row_label": row_label,
                    "column_label": column_label,
                }

    modified_xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    TARGET_DOC.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(SOURCE_DOC, "r") as zin, zipfile.ZipFile(
        TARGET_DOC, "w"
    ) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                data = modified_xml
            zout.writestr(item, data)

    ordered_map = OrderedDict(sorted(field_map.items()))
    FIELD_MAP_PATH.write_text(json.dumps(ordered_map, indent=2), encoding="utf-8")


if __name__ == "__main__":
    build_fillable_template()
