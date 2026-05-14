"""
Data loaders for HTAP JSON files
Uses simple caching for 0.32 MB + 0.19 MB files
"""

import json
from pathlib import Path
from functools import lru_cache
from typing import Dict

from src.models.cost import UnitCostsDatabase, CostSource, SourceCostData
from src.models.option import OptionsDatabase, OptionCategory, OptionChoice


@lru_cache(maxsize=2)
def load_unit_costs(file_path: str) -> UnitCostsDatabase:
    """
    Load HTAPUnitCosts.json with validation

    Args:
        file_path: Path to HTAPUnitCosts.json

    Returns:
        Validated UnitCostsDatabase model

    Note: Cached in memory (file is only 0.19 MB)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Unit costs file not found: {file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # Parse sources
    sources = {
        source_name: CostSource(**source_data)
        for source_name, source_data in raw_data.get("sources", {}).items()
    }

    # Parse component data (nested by source)
    data: Dict[str, Dict[str, SourceCostData]] = {}
    for comp_id, source_dict in raw_data.get("data", {}).items():
        data[comp_id] = {
            source_name: SourceCostData(**source_data)
            for source_name, source_data in source_dict.items()
        }

    return UnitCostsDatabase(sources=sources, data=data)


@lru_cache(maxsize=2)
def load_options(file_path: str) -> OptionsDatabase:
    """
    Load HTAP-options.json with validation

    Args:
        file_path: Path to HTAP-options.json

    Returns:
        Validated OptionsDatabase model

    Note: Cached in memory (file is only 0.32 MB)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Options file not found: {file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    categories = {}
    for cat_name, cat_data in raw_data.items():
        if cat_name.startswith("Opt-") or cat_name.startswith("GOconfig"):
            # Parse choices (note: field is "options" in JSON)
            choices = {}
            structure = cat_data.get("structure", "flat")

            for choice_name, choice_data in cat_data.get("options", {}).items():
                # Handle flat structure (string values) vs tree structure (dict values)
                if isinstance(choice_data, str):
                    # Flat structure: "choice": "value"
                    choices[choice_name] = OptionChoice(
                        choice_name=choice_name,
                        h2k_map={"value": choice_data} if choice_data != choice_name else None
                    )
                elif isinstance(choice_data, dict):
                    # Tree structure: "choice": {...}
                    choices[choice_name] = OptionChoice(
                        choice_name=choice_name,
                        **choice_data
                    )
                else:
                    # Skip unknown types
                    continue

            # Create category with all metadata
            categories[cat_name] = OptionCategory(
                category_type=cat_name,
                structure=structure,
                costed=cat_data.get("costed", False),
                options=choices,
                default=cat_data.get("default"),
                stop_on_error=cat_data.get("stop-on-error", True),
                h2k_schema=cat_data.get("h2kSchema")
            )

    return OptionsDatabase(categories=categories)


def clear_cache():
    """Clear loader cache"""
    load_unit_costs.cache_clear()
    load_options.cache_clear()
