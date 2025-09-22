#!/usr/bin/env python3
"""Compute FDWR (fenestration-to-wall ratio) for HOT2000 .h2k files."""

import argparse
import csv
import math
import sys
from pathlib import Path
from typing import Dict, Optional
import xml.etree.ElementTree as ET

DIMENSION_MM_THRESHOLD = 25.0  # heuristic for detecting millimetre units


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


def measurement_area(measurements: Optional[ET.Element]) -> float:
    """Return area from a Measurements node, normalising units when needed."""
    if measurements is None:
        return 0.0
    height = attr_float(measurements, "height")
    width = attr_float(measurements, "width")
    if height > DIMENSION_MM_THRESHOLD:
        height /= 1000.0
    if width > DIMENSION_MM_THRESHOLD:
        width /= 1000.0
    return height * width


def iterate_windows(components: ET.Element):
    for window in components.findall(".//Window"):
        measurements = window.find("Measurements")
        number = attr_float(window, "number") or 1.0
        yield measurement_area(measurements) * number


def iterate_doors(components: ET.Element):
    for door in components.findall(".//Door"):
        measurements = door.find("Measurements")
        number = attr_float(door, "number") or 1.0
        yield measurement_area(measurements) * number


def sum_wall_area(components: ET.Element) -> float:
    total = 0.0
    for wall in components.findall("Wall"):
        if wall.get("adjacentEnclosedSpace", "").lower() == "true":
            continue
        measurements = wall.find("Measurements")
        height = attr_float(measurements, "height")
        perimeter = attr_float(measurements, "perimeter")
        total += height * perimeter
        for header in wall.findall(".//FloorHeader"):
            header_measurements = header.find("Measurements")
            h_height = attr_float(header_measurements, "height")
            h_perimeter = attr_float(header_measurements, "perimeter")
            total += h_height * h_perimeter
    return total


def basement_above_grade_area(components: ET.Element) -> float:
    total = 0.0
    for basement in components.findall("Basement"):
        floor_meas = basement.find("Floor/Measurements")
        wall_meas = basement.find("Wall/Measurements")
        if floor_meas is None or wall_meas is None:
            continue
        perimeter = attr_float(floor_meas, "perimeter")
        height = attr_float(wall_meas, "height")
        depth = attr_float(wall_meas, "depth")
        pony = attr_float(wall_meas, "ponyWallHeight")
        above_grade_height = max(height - depth, 0.0) - pony
        if above_grade_height < 0.0:
            above_grade_height = 0.0
        total += perimeter * above_grade_height
    return total


def pony_wall_area(components: ET.Element) -> float:
    total = 0.0
    for basement in components.findall("Basement"):
        floor_meas = basement.find("Floor/Measurements")
        wall_meas = basement.find("Wall/Measurements")
        if floor_meas is None or wall_meas is None:
            continue
        perimeter = attr_float(floor_meas, "perimeter")
        pony = attr_float(wall_meas, "ponyWallHeight")
        total += perimeter * pony
    return total


def basement_header_area(components: ET.Element) -> float:
    total = 0.0
    for basement in components.findall("Basement"):
        for header in basement.findall("Components/FloorHeader"):
            meas = header.find("Measurements")
            height = attr_float(meas, "height")
            perimeter = attr_float(meas, "perimeter")
            total += height * perimeter
    return total


def crawlspace_wall_area(components: ET.Element) -> float:
    total = 0.0
    for crawlspace in components.findall("Crawlspace"):
        wall_meas = crawlspace.find("Wall/Measurements")
        floor_meas = crawlspace.find("Floor/Measurements")
        if wall_meas is None or floor_meas is None:
            continue
        perimeter = attr_float(floor_meas, "perimeter")
        height = attr_float(wall_meas, "height")
        depth = attr_float(wall_meas, "depth")
        above_grade_height = max(height - depth, 0.0)
        total += perimeter * above_grade_height
    return total


def crawlspace_header_area(components: ET.Element) -> float:
    total = 0.0
    for crawlspace in components.findall("Crawlspace"):
        for header in crawlspace.findall("Components/FloorHeader"):
            meas = header.find("Measurements")
            height = attr_float(meas, "height")
            perimeter = attr_float(meas, "perimeter")
            total += height * perimeter
    return total


def compute_from_gross_area(root: ET.Element) -> Optional[Dict[str, float]]:
    gross_area = root.find(".//AllResults/Results/Other/GrossArea")
    if gross_area is None:
        return None

    main = gross_area.find("MainFloors")
    basement = gross_area.find("Basement")
    crawlspace = gross_area.find("Crawlspace")

    wall_main = attr_float(main, "mainWalls")
    wall_basement = attr_float(basement, "aboveGrade")
    wall_pony = attr_float(gross_area, "ponyWall")
    wall_crawl = attr_float(crawlspace, "wall")
    wall_basement_header = attr_float(basement, "floorHeader")
    wall_crawl_header = attr_float(crawlspace, "floorHeader")

    fenestration = 0.0
    for section in [main, basement, crawlspace]:
        windows = section.find("Windows") if section is not None else None
        if windows is None:
            continue
        for opening in windows:
            fenestration += attr_float(opening, "grossArea")

    door_area = attr_float(gross_area, "doors")
    fd_total = fenestration + door_area
    wall_total = (
        wall_main
        + wall_basement
        + wall_crawl
        + wall_pony
        + wall_basement_header
        + wall_crawl_header
    )
    fdwr = fd_total / wall_total if wall_total else math.nan

    return {
        "wall_main": wall_main,
        "wall_basement": wall_basement,
        "wall_pony": wall_pony,
        "wall_basement_header": wall_basement_header,
        "wall_crawl": wall_crawl,
        "wall_crawl_header": wall_crawl_header,
        "F": fenestration,
        "D": door_area,
        "FD": fd_total,
        "W": wall_total,
        "FDWR": fdwr,
    }


def compute_from_geometry(root: ET.Element) -> Optional[Dict[str, float]]:
    components = root.find(".//House/Components")
    if components is None:
        return None

    wall_main = sum_wall_area(components)
    wall_basement = basement_above_grade_area(components)
    wall_pony = pony_wall_area(components)
    wall_basement_header = basement_header_area(components)
    wall_crawl = crawlspace_wall_area(components)
    wall_crawl_header = crawlspace_header_area(components)

    fenestration = sum(iterate_windows(components))
    door_area = sum(iterate_doors(components))

    fd_total = fenestration + door_area
    wall_total = (
        wall_main
        + wall_basement
        + wall_crawl
        + wall_pony
        + wall_basement_header
        + wall_crawl_header
    )
    fdwr = fd_total / wall_total if wall_total else math.nan

    return {
        "wall_main": wall_main,
        "wall_basement": wall_basement,
        "wall_pony": wall_pony,
        "wall_basement_header": wall_basement_header,
        "wall_crawl": wall_crawl,
        "wall_crawl_header": wall_crawl_header,
        "F": fenestration,
        "D": door_area,
        "FD": fd_total,
        "W": wall_total,
        "FDWR": fdwr,
    }


def compute_fdwr(path: Path) -> Optional[Dict[str, float]]:
    tree = ET.parse(path)
    root = tree.getroot()

    result = compute_from_gross_area(root)
    if result is not None:
        return result
    return compute_from_geometry(root)


def format_number(value: float) -> str:
    if math.isnan(value):
        return "n/a"
    return f"{value:.3f}"


def export_number(value: float) -> str:
    if math.isnan(value):
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
                f"{display}: insufficient geometry data for AllResults or fallback",
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
            "wall_pony",
            "wall_basement_header",
            "wall_crawl",
            "wall_crawl_header",
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
                        "wall_pony": export_number(row["wall_pony"]),
                        "wall_basement_header": export_number(row["wall_basement_header"]),
                        "wall_crawl": export_number(row["wall_crawl"]),
                        "wall_crawl_header": export_number(row["wall_crawl_header"]),
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
