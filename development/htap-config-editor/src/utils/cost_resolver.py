"""
Cost resolution logic for HTAP options
Handles multiple sources, component inheritance, and cost calculations
"""

from typing import Dict, List, Optional, Tuple
from functools import lru_cache

from src.models.cost import UnitCostsDatabase, SourceCostData
from src.models.option import OptionChoice, CostComponents


class CostResolver:
    """
    Resolves costs for HTAP options with source inheritance support
    """

    # Known inheritance chain (can be made configurable later)
    SOURCE_INHERITANCE = {
        "LEEP-BC-KamloopsChesnut": "LEEP-ON-Ottawa",
        "LEEP-BC-Victoria": "LEEP-ON-Ottawa",
        "LEEP-BC-Kelowna": "LEEP-ON-Ottawa",
        # Add more as discovered in HTAPUnitCosts.json
    }

    def __init__(self, costs_db: UnitCostsDatabase):
        """
        Initialize cost resolver

        Args:
            costs_db: Loaded unit costs database
        """
        self.costs_db = costs_db

    @lru_cache(maxsize=1024)
    def get_component_cost(
        self,
        component_id: str,
        source: str
    ) -> Optional[SourceCostData]:
        """
        Get cost for component from source, with inheritance fallback

        Args:
            component_id: Component identifier (e.g., "1/2in_gypsum_board")
            source: Cost source (e.g., "LEEP-BC-KamloopsChesnut")

        Returns:
            SourceCostData if found, None if component doesn't exist in any source
        """
        # Try direct lookup
        if component_id in self.costs_db.data:
            component_sources = self.costs_db.data[component_id]
            if source in component_sources:
                return component_sources[source]

        # Try inheritance chain
        current_source = source
        while current_source in self.SOURCE_INHERITANCE:
            parent_source = self.SOURCE_INHERITANCE[current_source]
            if component_id in self.costs_db.data:
                component_sources = self.costs_db.data[component_id]
                if parent_source in component_sources:
                    return component_sources[parent_source]
            current_source = parent_source

        return None

    def resolve_option_cost(
        self,
        option: OptionChoice,
        source: str
    ) -> Tuple[float, List[Dict]]:
        """
        Calculate total cost for an option choice

        Args:
            option: OptionChoice with costs defined
            source: Cost source to use

        Returns:
            Tuple of (total_cost, component_details)
            component_details is list of dicts with:
                - component_id
                - description
                - units
                - quantity (from option.costs.components)
                - unit_cost_materials
                - unit_cost_labour
                - total_cost
                - source_used (which source provided the cost)
        """
        if not option.costs or not option.costs.components:
            return 0.0, []

        total_cost = 0.0
        component_details = []

        # Handle components list (can be strings or dicts)
        for component_item in option.costs.components:
            # Parse component item
            if isinstance(component_item, str):
                component_id = component_item
                quantity = 1.0
            elif isinstance(component_item, dict):
                component_id = component_item.get("component", "")
                quantity = component_item.get("quantity", 1.0)
            else:
                continue

            cost_data = self.get_component_cost(component_id, source)

            if cost_data:
                unit_cost = cost_data.UnitCostMaterials + cost_data.UnitCostLabour
                component_total = unit_cost * quantity

                component_details.append({
                    "component_id": component_id,
                    "description": cost_data.description,
                    "units": cost_data.units,
                    "quantity": quantity,
                    "unit_cost_materials": cost_data.UnitCostMaterials,
                    "unit_cost_labour": cost_data.UnitCostLabour,
                    "unit_cost_total": unit_cost,
                    "total_cost": component_total,
                    "source_used": cost_data.source
                })

                total_cost += component_total
            else:
                # Component not found in any source
                component_details.append({
                    "component_id": component_id,
                    "description": "Component not found",
                    "units": "unknown",
                    "quantity": quantity,
                    "unit_cost_materials": 0.0,
                    "unit_cost_labour": 0.0,
                    "unit_cost_total": 0.0,
                    "total_cost": 0.0,
                    "source_used": "NOT_FOUND",
                    "error": True
                })

        # Handle custom costs
        if option.costs.custom_costs:
            for custom_id, custom_data in option.costs.custom_costs.items():
                # Custom costs can be float or dict
                if isinstance(custom_data, dict):
                    custom_amount = custom_data.get("TotUnitCost", 0.0)
                    custom_units = custom_data.get("Units", "lump sum")
                    custom_comment = custom_data.get("Comment", "Custom cost")
                else:
                    custom_amount = float(custom_data)
                    custom_units = "lump sum"
                    custom_comment = "Custom cost"

                component_details.append({
                    "component_id": custom_id,
                    "description": custom_comment,
                    "units": custom_units,
                    "quantity": 1.0,
                    "unit_cost_materials": 0.0,
                    "unit_cost_labour": 0.0,
                    "unit_cost_total": custom_amount,
                    "total_cost": custom_amount,
                    "source_used": "CUSTOM",
                    "is_custom": True
                })
                total_cost += custom_amount

        return total_cost, component_details

    def get_available_sources(self) -> List[str]:
        """
        Get list of all available cost sources

        Returns:
            Sorted list of source names
        """
        sources = set()
        for component_data in self.costs_db.data.values():
            sources.update(component_data.keys())
        return sorted(sources)

    def get_source_component_count(self, source: str) -> int:
        """
        Count how many components are available in a source (with inheritance)

        Args:
            source: Cost source name

        Returns:
            Number of components available
        """
        count = 0
        for component_id in self.costs_db.data.keys():
            if self.get_component_cost(component_id, source) is not None:
                count += 1
        return count

    def validate_option_costs(
        self,
        option: OptionChoice,
        source: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all components in option are available in source

        Args:
            option: OptionChoice to validate
            source: Cost source to check against

        Returns:
            Tuple of (is_valid, list_of_missing_components)
        """
        if not option.costs or not option.costs.components:
            return True, []

        missing = []
        for component_item in option.costs.components:
            # Parse component item
            if isinstance(component_item, str):
                component_id = component_item
            elif isinstance(component_item, dict):
                component_id = component_item.get("component", "")
            else:
                continue

            if self.get_component_cost(component_id, source) is None:
                missing.append(component_id)

        return len(missing) == 0, missing
