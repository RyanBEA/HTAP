#!/usr/bin/env python3
"""
H2K Analyzer Script

Analyzes HOT2000 .h2k files to extract equipment and foundation characteristics
for determining the appropriate reference house run file for NBC compliance.

Usage:
    python h2k_analyzer.py <input_directory>
    python h2k_analyzer.py <file1.h2k> <file2.h2k> ...

Output:
    JSON with file analysis results, runfile groupings, and summary statistics.
"""

import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


# Run file classification mapping
RUNFILE_MAPPING = {
    'gas': 'referencehouse_T1gasfurnace_T2ASHP.run',
    'propane': 'referencehouse_T1gasfurnace_T2ASHP.run',
    'electric': 'referencehouse_T1elecfurnace_T2ASHP.run',
    'oil': 'referencehouse_T1oilfurnace_T2ASHP.run',
}

# Energy source normalization mapping
ENERGY_SOURCE_NORMALIZE = {
    'natural gas': 'gas',
    'gas': 'gas',
    'propane': 'propane',
    'electric': 'electric',
    'electricity': 'electric',
    'oil': 'oil',
    'heating oil': 'oil',
    'wood': 'wood',
    'wood pellets': 'wood',
}


def normalize_energy_source(source):
    """Normalize energy source string to standard key."""
    if not source:
        return None
    return ENERGY_SOURCE_NORMALIZE.get(source.lower().strip(), source.lower().strip())


def safe_find_text(root, xpath, default=None):
    """Safely find text content at xpath, returning default if not found."""
    try:
        elem = root.find(xpath)
        if elem is not None and elem.text:
            return elem.text.strip()
    except Exception:
        pass
    return default


def safe_find_attr(root, xpath, attr, default=None):
    """Safely find attribute value at xpath, returning default if not found."""
    try:
        elem = root.find(xpath)
        if elem is not None:
            return elem.get(attr, default)
    except Exception:
        pass
    return default


def safe_findall(root, xpath):
    """Safely find all elements at xpath, returning empty list if error."""
    try:
        return root.findall(xpath) or []
    except Exception:
        return []


def extract_type1_heating(root):
    """
    Extract Type1 heating system information.

    Returns dict with:
        - equipment_type: furnace, boiler, baseboard, or None
        - fuel_type: normalized fuel type
        - raw_fuel: original fuel string from file
    """
    result = {
        'equipment_type': None,
        'fuel_type': None,
        'raw_fuel': None,
    }

    # Check for furnace
    furnace_fuel = safe_find_text(root, './/HeatingCooling/Type1/Furnace/Equipment/EnergySource/English')
    if furnace_fuel:
        result['equipment_type'] = 'furnace'
        result['raw_fuel'] = furnace_fuel
        result['fuel_type'] = normalize_energy_source(furnace_fuel)
        return result

    # Check for boiler
    boiler_fuel = safe_find_text(root, './/HeatingCooling/Type1/Boiler/Equipment/EnergySource/English')
    if boiler_fuel:
        result['equipment_type'] = 'boiler'
        result['raw_fuel'] = boiler_fuel
        result['fuel_type'] = normalize_energy_source(boiler_fuel)
        return result

    # Check for baseboards
    baseboards = root.find('.//HeatingCooling/Type1/Baseboards')
    if baseboards is not None:
        result['equipment_type'] = 'baseboard'
        result['fuel_type'] = 'electric'
        result['raw_fuel'] = 'Electric (baseboard)'
        return result

    return result


def extract_type2_ashp(root):
    """
    Check for presence of Type2 Air Source Heat Pump.

    Returns dict with:
        - present: bool
        - type: heat pump type if present
    """
    ashp = root.find('.//HeatingCooling/Type2/AirHeatPump')
    if ashp is not None:
        hp_type = safe_find_text(root, './/HeatingCooling/Type2/AirHeatPump/Equipment/Type/English')
        return {
            'present': True,
            'type': hp_type,
        }
    return {
        'present': False,
        'type': None,
    }


def extract_dhw(root):
    """
    Extract domestic hot water system information.

    Returns dict with:
        - fuel_type: normalized fuel type
        - raw_fuel: original fuel string
        - has_dwhr: whether drain water heat recovery is present
    """
    fuel = safe_find_text(root, './/Components/HotWater/Primary/EnergySource/English')

    # Also check House/Components path
    if not fuel:
        fuel = safe_find_text(root, './/House/Components/HotWater/Primary/EnergySource/English')

    dwhr = safe_find_attr(root, './/Components/HotWater/Primary', 'hasDrainWaterHeatRecovery')
    if dwhr is None:
        dwhr = safe_find_attr(root, './/House/Components/HotWater/Primary', 'hasDrainWaterHeatRecovery')

    return {
        'fuel_type': normalize_energy_source(fuel) if fuel else None,
        'raw_fuel': fuel,
        'has_dwhr': dwhr == 'true' if dwhr else False,
    }


def extract_foundation(root):
    """
    Extract foundation configuration information.

    Returns dict with:
        - type: basement, slab, crawlspace, walkout, or combination
        - basement_config: basement configuration type if present
        - slab_config: slab configuration type if present
        - has_pony_wall: whether pony wall is present
        - basement_area: below grade area if available
        - heated_floor: whether heated floor is present
    """
    result = {
        'type': None,
        'basement_config': None,
        'slab_config': None,
        'has_pony_wall': False,
        'basement_area': None,
        'heated_floor': False,
    }

    foundation_types = []

    # Check for basement - try multiple paths
    basements = safe_findall(root, './/Components/Basement')
    if not basements:
        basements = safe_findall(root, './/House/Components/Basement')

    if basements:
        foundation_types.append('basement')
        # Get configuration type from first basement
        for basement in basements:
            config = basement.find('./Configuration')
            if config is not None:
                result['basement_config'] = config.get('type')
                break

        # Check for pony wall
        for basement in basements:
            wall = basement.find('./Wall')
            if wall is not None and wall.get('hasPonyWall') == 'true':
                result['has_pony_wall'] = True
                break

        # Check for heated floor in basement
        for basement in basements:
            floor_const = basement.find('./Floor/Construction')
            if floor_const is not None and floor_const.get('heatedFloor') == 'true':
                result['heated_floor'] = True
                break

    # Check for slab - try multiple paths
    slabs = safe_findall(root, './/Components/Slab')
    if not slabs:
        slabs = safe_findall(root, './/House/Components/Slab')

    if slabs:
        foundation_types.append('slab')
        # Get configuration type from first slab
        for slab in slabs:
            config = slab.find('./Configuration')
            if config is not None:
                result['slab_config'] = config.get('type')
                break

        # Check for heated floor in slab
        for slab in slabs:
            floor_const = slab.find('./Floor/Construction')
            if floor_const is not None and floor_const.get('heatedFloor') == 'true':
                result['heated_floor'] = True
                break

    # Check for crawlspace
    crawlspaces = safe_findall(root, './/Components/Crawlspace')
    if not crawlspaces:
        crawlspaces = safe_findall(root, './/House/Components/Crawlspace')
    if crawlspaces:
        foundation_types.append('crawlspace')

    # Check for walkout
    walkouts = safe_findall(root, './/Components/Walkout')
    if not walkouts:
        walkouts = safe_findall(root, './/House/Components/Walkout')
    if walkouts:
        foundation_types.append('walkout')

    # Set foundation type
    if len(foundation_types) == 0:
        result['type'] = 'unknown'
    elif len(foundation_types) == 1:
        result['type'] = foundation_types[0]
    else:
        result['type'] = '+'.join(foundation_types)

    return result


def extract_special_features(root):
    """
    Extract special features that may require manual intervention.

    Returns dict with feature presence flags.
    """
    result = {
        'has_skylights': False,
        'skylight_count': 0,
    }

    # Check for skylights (windows in ceilings)
    skylights = safe_findall(root, './/Components/Ceiling/Components/Window')
    if not skylights:
        skylights = safe_findall(root, './/House/Components/Ceiling/Components/Window')
    if not skylights:
        # Alternative path
        skylights = safe_findall(root, './/Ceiling//Window')

    if skylights:
        result['has_skylights'] = True
        result['skylight_count'] = len(skylights)

    return result


def determine_runfile(type1_heating):
    """
    Determine the appropriate reference house run file based on Type1 heating.

    Returns tuple of (runfile_name, classification_reason).
    """
    fuel = type1_heating.get('fuel_type')

    if fuel in RUNFILE_MAPPING:
        return RUNFILE_MAPPING[fuel], f"Type1 fuel: {fuel}"

    # If fuel type is unknown or not mapped, return None
    return None, f"Unknown fuel type: {fuel}"


def determine_manual_flags(analysis):
    """
    Determine what features require manual intervention.

    Returns list of flag descriptions.
    """
    flags = []

    # Pony wall requires manual handling
    if analysis.get('foundation', {}).get('has_pony_wall'):
        flags.append('pony_wall')

    # DWHR requires manual handling
    if analysis.get('dhw', {}).get('has_dwhr'):
        flags.append('dwhr')

    # Skylights require manual handling
    if analysis.get('special_features', {}).get('has_skylights'):
        flags.append('skylights')

    # Heated floors require manual handling
    if analysis.get('foundation', {}).get('heated_floor'):
        flags.append('heated_floors')

    return flags


def analyze_h2k_file(filepath):
    """
    Analyze a single H2K file and extract all relevant characteristics.

    Returns dict with analysis results or error information.
    """
    result = {
        'filename': os.path.basename(filepath),
        'filepath': str(filepath),
        'success': False,
        'error': None,
    }

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        # Extract all characteristics
        type1_heating = extract_type1_heating(root)
        type2_ashp = extract_type2_ashp(root)
        dhw = extract_dhw(root)
        foundation = extract_foundation(root)
        special_features = extract_special_features(root)

        # Determine run file
        runfile, classification_reason = determine_runfile(type1_heating)

        # Build analysis result
        analysis = {
            'type1_heating': type1_heating,
            'type2_ashp': type2_ashp,
            'dhw': dhw,
            'foundation': foundation,
            'special_features': special_features,
        }

        # Determine manual flags
        manual_flags = determine_manual_flags(analysis)

        result.update({
            'success': True,
            'analysis': analysis,
            'runfile': runfile,
            'classification_reason': classification_reason,
            'manual_flags': manual_flags,
            'requires_manual_intervention': len(manual_flags) > 0,
        })

    except ET.ParseError as e:
        result['error'] = f"XML parse error: {str(e)}"
    except FileNotFoundError:
        result['error'] = f"File not found: {filepath}"
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"

    return result


def collect_h2k_files(args):
    """
    Collect H2K files from command line arguments.

    Handles both directory and individual file arguments.
    Returns list of file paths.
    """
    files = []

    for arg in args:
        path = Path(arg)

        if path.is_dir():
            # Collect all .h2k files in directory
            files.extend(path.glob('*.h2k'))
            files.extend(path.glob('*.H2K'))
        elif path.is_file() and path.suffix.lower() == '.h2k':
            files.append(path)
        elif path.is_file():
            # File exists but not .h2k - include anyway for error handling
            files.append(path)

    return sorted(set(files))


def group_by_runfile(results):
    """
    Group analyzed files by their required reference run file.

    Returns dict mapping runfile names to lists of filenames.
    """
    groups = {}
    ungrouped = []

    for result in results:
        if result.get('success') and result.get('runfile'):
            runfile = result['runfile']
            if runfile not in groups:
                groups[runfile] = []
            groups[runfile].append(result['filename'])
        else:
            ungrouped.append(result['filename'])

    if ungrouped:
        groups['_ungrouped'] = ungrouped

    return groups


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python h2k_analyzer.py <input_directory>")
        print("       python h2k_analyzer.py <file1.h2k> <file2.h2k> ...")
        sys.exit(1)

    # Collect files
    files = collect_h2k_files(sys.argv[1:])

    if not files:
        print(json.dumps({
            'error': 'No .h2k files found',
            'searched_paths': sys.argv[1:],
        }, indent=2))
        sys.exit(1)

    # Analyze each file
    results = []
    for filepath in files:
        result = analyze_h2k_file(filepath)
        results.append(result)

    # Group by runfile
    runfile_groups = group_by_runfile(results)

    # Collect files requiring manual intervention
    manual_intervention = [
        {
            'filename': r['filename'],
            'flags': r['manual_flags'],
        }
        for r in results
        if r.get('success') and r.get('requires_manual_intervention')
    ]

    # Build summary
    summary = {
        'total_files': len(results),
        'successful': sum(1 for r in results if r.get('success')),
        'errors': sum(1 for r in results if r.get('error')),
        'manual_intervention_required': len(manual_intervention),
    }

    # Build output
    output = {
        'files': results,
        'runfile_groups': runfile_groups,
        'manual_intervention_required': manual_intervention,
        'summary': summary,
    }

    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
