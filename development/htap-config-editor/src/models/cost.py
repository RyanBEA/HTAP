"""
Pydantic models for HTAPUnitCosts.json
CORRECTED to match actual nested structure
"""

from typing import Dict, List, Optional
from pydantic import Field

from .common import HTAPBaseModel


class SourceCostData(HTAPBaseModel):
    """
    Cost data from a specific source (e.g., LEEP-ON-Ottawa)

    This is the actual structure within HTAPUnitCosts.json
    """

    category: str = Field(description="Cost category (DRYWALL, HVAC, etc.)")
    description: str = Field(description="Component description")
    units: str = Field(description="Unit of measurement (sf wall, each, etc.)")  # Note: plural!
    UnitCostMaterials: float = Field(description="Material cost per unit")
    UnitCostLabour: float = Field(description="Labour cost per unit")
    note: Optional[str] = Field(None, description="Additional notes")
    date: Optional[str] = Field(None, description="Date of cost data")
    source: str = Field(description="Source identifier")

    def total_cost(self) -> float:
        """Get combined material + labour cost"""
        return self.UnitCostMaterials + self.UnitCostLabour


class CostSource(HTAPBaseModel):
    """Metadata for a cost data source"""

    filename: str = Field(description="Original source filename")
    date_collated: str = Field(description="Date data was collected")
    date_imported: str = Field(description="Date imported into HTAP")
    schema_used: str = Field(description="Schema version")
    origin: str = Field(description="Description of data source")
    inherits: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Inheritance map: {parent_source: [component_ids]}"
    )


class UnitCostsDatabase(HTAPBaseModel):
    """
    Complete HTAPUnitCosts.json structure

    Structure: {component_id: {source_name: SourceCostData}}
    """

    sources: Dict[str, CostSource] = Field(description="Cost data sources metadata")
    data: Dict[str, Dict[str, SourceCostData]] = Field(
        description="Component cost data: {component_id: {source: data}}"
    )

    def get_component(self, component_id: str) -> Optional[Dict[str, SourceCostData]]:
        """Get all source data for a component"""
        return self.data.get(component_id)

    def get_cost(self, component_id: str, source: str) -> Optional[float]:
        """Get total cost (materials + labour) for component from source"""
        if component_id in self.data and source in self.data[component_id]:
            return self.data[component_id][source].total_cost()
        return None

    def list_sources(self) -> List[str]:
        """List all available cost sources"""
        return list(self.sources.keys())

    def list_components(self) -> List[str]:
        """List all component IDs"""
        return list(self.data.keys())

    def get_components_with_source(self, source: str) -> List[str]:
        """Get all components that have data from specified source"""
        return [
            comp_id
            for comp_id, sources in self.data.items()
            if source in sources
        ]
