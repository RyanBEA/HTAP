"""
Populate the programmatic template with representative dummy data so reviewers can
confirm layout and formatting before wiring real integrations.
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = REPO_ROOT / "complianceReporting" / "form_template.docx"
FIELD_MAP_PATH = REPO_ROOT / "complianceReporting" / "form_template_fields.json"
OUTPUT_PATH = REPO_ROOT / "complianceReporting" / "form_filled_dummy.docx"


def load_field_map() -> dict[str, dict[str, int | str]]:
    return json.loads(FIELD_MAP_PATH.read_text(encoding="utf-8"))


def build_sample_values(field_map: dict[str, dict[str, int | str]]) -> dict[str, str]:
    values: dict[str, str] = {key: "" for key in field_map}

    # Project overview
    values.update(
        {
            "T0_R1_C1": "Sunrise Terrace Redevelopment",
            "T0_R2_C1": "1234 Aurora Way, Victoria, BC V8W 2L1",
            "T0_R3_C1": "Northern Built Consulting Ltd.",
            "T0_R4_C1": "Suite 210, 890 Harbor St, Victoria, BC V8W 2L1",
            "T1_R3_C0": "Zone 5 (3,620 HDD) - City of Kelowna jurisdiction",
            "T2_R0_C0": "241.6",
            "T3_R1_C0": "48.7",
            "T3_R1_C2": "263.4",
            "T3_R1_C4": "18.5",
            "T6_R1_C0": "<= 1.5 ACH @ 50 Pa",
            "T7_R0_C1": "118",
            "T8_R0_C1": "57",
            "T9_R0_C0": "2",
            "T9_R0_C2": "3",
            "T10_R1_C1": "HOT2000",
            "T10_R1_C3": "11.13.2",
            "T11_R1_C0": "96.2 GJ/yr",
            "T11_R1_C2": "61.4 GJ/yr",
            "T12_R0_C1": "Tier 3 compliance package attached",
            "T16_R0_C1": "Step Code Tier 3 confirmed",
        }
    )

    # Envelope performance (Table 5)
    envelope_pairs = [
        ("T5_R2_C2", "RSI 8.67"),
        ("T5_R2_C3", "RSI 9.10"),
        ("T5_R3_C2", "RSI 6.35"),
        ("T5_R3_C3", "RSI 6.88"),
        ("T5_R4_C2", "RSI 3.08"),
        ("T5_R4_C3", "RSI 3.42"),
        ("T5_R5_C2", "RSI 5.02"),
        ("T5_R5_C3", "RSI 5.68"),
        ("T5_R6_C2", "RSI 2.98"),
        ("T5_R6_C3", "RSI 3.32"),
        ("T5_R7_C3", "RSI 1.96"),
        ("T5_R7_C4", "RSI 2.10"),
        ("T5_R8_C3", "RSI 1.96"),
        ("T5_R8_C4", "RSI 2.24"),
        ("T5_R9_C2", "RSI 3.10"),
        ("T5_R9_C3", "RSI 3.10"),
        ("T5_R10_C2", "RSI 2.84"),
        ("T5_R10_C3", "RSI 3.28"),
        ("T5_R11_C2", "RSI 3.72"),
        ("T5_R11_C3", "RSI 4.18"),
    ]
    for key, value in envelope_pairs:
        values[key] = value

    values.update(
        {
            "T5_R13_C1": "South-east",
            "T5_R14_C2": "U-1.20 W/(m^2-K)",
            "T5_R14_C3": "ER 38",
            "T5_R15_C3": "0.32",
            "T5_R16_C2": "U-1.60 W/(m^2-K)",
            "T5_R16_C3": "ER 32",
            "T5_R17_C3": "0.38",
            "T5_R18_C1": "Two insulated steel slabs, U-1.6",
            "T5_R18_C2": "Triple-glazed fiberglass slab, U-1.1",
            "T5_R19_C1": "17.8%",
            "T5_R19_C2": "18.5%",
            "T5_R25_C1": "Baseline 2-stage gas furnace, 92% AFUE",
            "T5_R25_C2": "Modulating gas furnace, 97% AFUE",
            "T5_R26_C2": "10.5",
            "T5_R26_C3": "Variable-speed compressor, 10.5 kW",
            "T5_R27_C2": "14.5",
            "T5_R27_C3": "18.0",
            "T5_R28_C3": "Yes - cold-climate ASHP",
            "T5_R28_C4": "HSPFv 10.2",
            "T5_R29_C3": "-12C",
            "T5_R29_C4": "-18C",
            "T5_R30_C1": "2 kW electric baseboard (garage)",
            "T5_R30_C2": "Hydronic coil off main ASHP",
            "T5_R31_C2": "46",
            "T5_R33_C4": "121",
            "T5_R34_C4": "96",
            "T5_R35_C4": "74",
            "T5_R36_C4": "68",
            "T5_R37_C1": "189 L electric tank, UEF 0.93",
            "T5_R37_C2": "76 L heat pump WH, UEF 3.2",
        }
    )

    # Airtightness / ventilation complements
    values.update(
        {
            "T6_R1_C0": "<= 1.5 ACH @ 50 Pa",
            "T7_R0_C1": "118",
            "T8_R0_C1": "57",
            "T9_R0_C0": "2",
            "T9_R0_C2": "3",
        }
    )

    # Performance software & certification
    values.update(
        {
            "T10_R1_C1": "HOT2000",
            "T10_R1_C3": "11.13.2",
            "T11_R1_C0": "96.2 GJ/yr",
            "T11_R1_C2": "61.4 GJ/yr",
            "T12_R0_C1": "Tier 3 compliance package attached",
            "T16_R0_C1": "Step Code Tier 3 confirmed",
        }
    )

    # Professional information (Table 13 & 17)
    values.update(
        {
            "T13_R1_C1": "Taylor Morgan",
            "T13_R1_C3": "Highline Energy Modelling Inc.",
            "T13_R2_C1": "604-555-2378",
            "T13_R2_C3": "taylor.morgan@highline.ca",
            "T13_R3_C1": "CACEA #PAN-34782",
            "T13_R5_C1": "2025-04-30",
            "T13_R5_C3": "Taylor Morgan",
            "T13_R7_C1": "Rebecca Singh",
            "T13_R7_C3": "AIBC Architect #41276",
            "T13_R8_C1": "778-555-1098",
            "T13_R8_C3": "rsingh@designatelier.ca",
            "T13_R10_C1": "2025-05-02",
            "T13_R10_C3": "Rebecca Singh",
            "T17_R1_C1": "Rebecca Singh",
            "T17_R1_C3": "AIBC Architect #41276",
            "T17_R2_C1": "778-555-1098",
            "T17_R2_C3": "rsingh@designatelier.ca",
            "T17_R4_C1": "2025-05-02",
            "T17_R4_C3": "Digital signature on file",
        }
    )

    # Reference tables (Table 14) – populate with indicative results
    values.update(
        {
            "T14_R2_C7": "5",
            "T14_R3_C6": "9.9",
            "T14_R4_C6": "11.0",
            "T14_R5_C4": "5.6",
            "T14_R6_C6": "3.6",
            "T14_R7_C6": "3.2",
            "T14_R8_C4": "5.2",
            "T14_R9_C7": "3.5",
            "T14_R10_C5": "3.1",
            "T14_R11_C4": "R-0",
            "T14_R12_C4": "2.2",
            "T14_R13_C4": "n/a",
            "T14_R14_C4": "2.9",
            "T14_R15_C6": "4.6",
            "T14_R16_C6": "3.8",
            "T14_R20_C5": "1.20",
            "T14_R21_C5": "34",
            "T14_R22_C4": "1.80",
            "T14_R23_C2": "1.80",
            "T14_R24_C2": "RSI 3.1",
            "T14_R27_C5": "Condensing gas – 97% AFUE",
            "T14_R28_C5": "High-efficiency oil – 86% AFUE",
            "T14_R29_C5": "Electric resistance – see note",
            "T14_R30_C5": "Condensing boiler – 94% AFUE",
            "T14_R31_C5": "High-output oil – 88% AFUE",
            "T14_R32_C5": "Electric boiler – refer to footnote",
            "T14_R33_C4": "ASHP split – HSPFv 10.0",
            "T14_R34_C4": "Combo system – TPF 0.88",
            "T14_R35_C5": "HRV - 75% SRE @0C",
            "T14_R36_C5": "HRV - 68% SRE @-25C",
            "T14_R37_C1": "Balanced ERV (if alternate)",
            "T14_R37_C2": "Balanced ERV – 200 L/s",
            "T14_R37_C3": "Sens. effectiveness 70%",
            "T14_R37_C4": "Unit located in mech. room",
            "T14_R40_C5": "HPWH – 189 L, EF 3.2",
            "T14_R41_C5": "Top loss 32 W",
            "T14_R42_C5": "Family tank – EF 0.85",
            "T14_R43_C5": "Bottom loss 28 W",
            "T14_R44_C5": "Gas tank – UEF 0.68",
            "T14_R45_C5": "Gas tank mid – UEF 0.74",
            "T14_R46_C5": "Gas tank high – UEF 0.78",
            "T14_R47_C4": "Tankless cold-climate – UEF 0.91",
            "T14_R48_C4": "Tankless high-load – UEF 0.92",
            "T14_R49_C4": "HPWH compact – EF 2.6",
            "T14_R50_C1": "Alt equipment note",
            "T14_R50_C2": "Alt capacity 4.5 kW",
            "T14_R50_C3": "Alt efficiency 89%",
            "T14_R50_C4": "Alt notes: demand recirc.",
        }
    )

    # Remaining cells default to descriptive sample text.
    for key, meta in field_map.items():
        if values[key]:
            continue
        row_label = meta.get("row_label", "") or ""
        column_label = meta.get("column_label", "") or ""
        descriptor = " ".join(
            part.strip()
            for part in [row_label, column_label]
            if part and "{{" not in part
        )
        descriptor = " ".join(descriptor.split())
        if not descriptor:
            descriptor = key
        values[key] = f"Sample {descriptor}"

    return values


def generate_document(template: Path, output: Path, values: dict[str, str]) -> None:
    with zipfile.ZipFile(template) as zin:
        document_xml = zin.read("word/document.xml").decode("utf-8")
        for key, value in sorted(values.items()):
            document_xml = document_xml.replace(
                "{{" + key + "}}", escape(value, entities={"'": "&apos;"})
            )

        with zipfile.ZipFile(output, "w") as zout:
            for entry in zin.infolist():
                data = document_xml.encode("utf-8") if entry.filename == "word/document.xml" else zin.read(entry.filename)
                zout.writestr(entry, data)


def main() -> None:
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template missing: {TEMPLATE_PATH}")
    field_map = load_field_map()
    sample_values = build_sample_values(field_map)
    generate_document(TEMPLATE_PATH, OUTPUT_PATH, sample_values)
    print(f"Generated dummy form at {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
