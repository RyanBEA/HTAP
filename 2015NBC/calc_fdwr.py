#!/usr/bin/env python3
"""Compute FDWR (fenestration-to-wall ratio) for HOT2000 .h2k files."""

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, Optional
import xml.etree.ElementTree as ET

def attr_float(element: Optional[ET.Element], attribute: str) -> float:
    if element is None:
        return 0.0
    value = element.get(attribute)
    if not value:
        return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0

def window_area(parent: Optional[ET.Element]) -> float:
    total = 0.0
    if parent is None:
        return total
    windows = parent.find("Windows")
    if windows is not None:
        for opening in windows:
            total += attr_float(opening, "grossArea")
    return total

def door_area(parent: Optional[ET.Element]) -> float:
    total = 0.0
    if parent is None:
        return total
    for door in parent.findall("Door"):
        total += attr_float(door, "grossArea")
    return total

def compute_fdwr(path: Path) -> Optional[Dict[str, float]]:
    tree = ET.parse(path)
    root = tree.getroot()
    gross_area = root.find(".//AllResults/Results/Other/GrossArea")
    if gross_area is None:
        return None

    main = gross_area.find("MainFloors")
    basement = gross_area.find("Basement")
    crawlspace = gross_area.find("Crawlspace")

    wall_main = attr_float(main, "mainWalls")
    wall_basement = attr_float(basement, "aboveGrade")
    wall_crawl = attr_float(crawlspace, "wall")

    fenestration = window_area(main) + window_area(basement) + window_area(crawlspace)
    door = door_area(main) + door_area(basement) + door_area(crawlspace)

    wall_total = wall_main + wall_basement + wall_crawl
    fd_total = fenestration + door
    fdwr = fd_total / wall_total if wall_total else float("nan")

    return {
        "wall_main": wall_main,
        "wall_basement": wall_basement,
        "wall_crawl": wall_crawl,
        "F": fenestration,
        "D": door,
        "FD": fd_total,
        "W": wall_total,
        "FDWR": fdwr,
    }

def format_number(value: float) -> str:
    if value != value:  # NaN check
        return "n/a"
    return f"{value:.3f}"

def export_number(value: float) -> str:
    if value != value:  # NaN
        return ""
    return f"{value:.3f}"

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Calculate FDWR for all .h2k files under the given directory."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Directory to scan (defaults to current working directory)",
    )
    parser.add_argument(
        "--csv",
        dest="csv_path",
        help="Optional path for CSV export",
    )
    args = parser.parse_args()

    root_path = Path(args.root).resolve()
    if not root_path.exists():
        print(f"Directory not found: {root_path}", file=sys.stderr)
        return 1

    files = sorted(root_path.rglob("*.h2k"))
    if not files:
        print("No .h2k files found.", file=sys.stderr)
        return 1

    header = f"{'file':<50} {'W (m^2)':>12} {'F (m^2)':>12} {'D (m^2)':>12} {'FD (m^2)':>12} {'FDWR':>12}"
    print(header)
    print("-" * len(header))

    rows = []
    for path in files:
        try:
            display = str(path.relative_to(root_path))
        except ValueError:
            display = str(path)
        try:
            result = compute_fdwr(path)
        except ET.ParseError as exc:
            print(f"{display}: parse error ({exc})", file=sys.stderr)
            continue
        if result is None:
            print(
                f"{display}: missing AllResults/Results/Other/GrossArea",
                file=sys.stderr,
            )
            continue

        rows.append({"file": display, **result})
        print(
            f"{display:<50} {result['W']:12.3f} {result['F']:12.3f} {result['D']:12.3f} {result['FD']:12.3f} {format_number(result['FDWR']):>12}"
        )

    if args.csv_path and rows:
        csv_path = Path(args.csv_path)
        if csv_path.is_dir():
            csv_path = csv_path / "fdwr_results.csv"
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "file",
            "wall_main",
            "wall_basement",
            "wall_crawl",
            "F",
            "D",
            "FD",
            "W",
            "FDWR",
        ]
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        "file": row["file"],
                        "wall_main": export_number(row["wall_main"]),
                        "wall_basement": export_number(row["wall_basement"]),
                        "wall_crawl": export_number(row["wall_crawl"]),
                        "F": export_number(row["F"]),
                        "D": export_number(row["D"]),
                        "FD": export_number(row["FD"]),
                        "W": export_number(row["W"]),
                        "FDWR": export_number(row["FDWR"]),
                    }
                )
        print(f"CSV written to {csv_path}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
