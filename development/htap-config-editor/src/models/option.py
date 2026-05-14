"""
Pydantic models for HTAP-options.json
CORRECTED to include all category-level metadata
"""

from typing import Any, Dict, List, Optional
from pydantic import Field

from .common import HTAPBaseModel


class H2KMapping(HTAPBaseModel):
    """HOT2000 XML mapping for an option"""
    # Uses extra="allow" to capture all h2kMap fields dynamically
    pass


class CostComponents(HTAPBaseModel):
    """Cost component assignments for an option"""

    components: List[Any] = Field(
        default_factory=list,
        description="List of component IDs (strings) or conditional components (dicts) from HTAPUnitCosts.json"
    )
    custom_costs: Dict[str, Any] = Field(
        default_factory=dict,
        alias="custom-costs",
        description="Custom cost overrides"
    )


class OptionChoice(HTAPBaseModel):
    """A single choice within an option category"""

    choice_name: str = Field(description="Internal name for this choice")
    h2k_map: Optional[Dict[str, Any]] = Field(
        None,
        alias="h2kMap",
        description="HOT2000 XML mappings"
    )
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    costs: Optional[CostComponents] = Field(None, description="Associated cost components")
    cost_proxy: Optional[str] = Field(
        None,
        alias="costProxy",
        description="Reference to another option's costs"
    )
    display_name: Optional[str] = Field(None, description="Human-readable name")
    description: Optional[str] = Field(None, description="Detailed description")


class OptionCategory(HTAPBaseModel):
    """A category of options (e.g., Opt-Windows)"""

    category_type: str = Field(description="Category name (Opt-*)")
    structure: str = Field(description="Structure type: 'flat' or 'tree'")
    costed: bool = Field(description="Whether costs are tracked")
    options: Dict[str, OptionChoice] = Field(description="Available choices")  # Note: "options" not "choices"
    default: Optional[str] = Field(None, description="Default option choice")
    stop_on_error: bool = Field(
        True,
        alias="stop-on-error",
        description="Stop execution on error"
    )
    h2k_schema: Optional[List[str]] = Field(
        None,
        alias="h2kSchema",
        description="H2K XML schema tags"
    )

    def list_choices(self) -> List[str]:
        """List all choice names in this category"""
        return list(self.options.keys())

    def get_choice(self, choice_name: str) -> Optional[OptionChoice]:
        """Get a specific choice by name"""
        return self.options.get(choice_name)

    def search_choices(self, query: str) -> Dict[str, OptionChoice]:
        """Search choices by name, tags, or description"""
        query_lower = query.lower()
        results = {}

        for name, choice in self.options.items():
            if query_lower in name.lower():
                results[name] = choice
            elif choice.description and query_lower in choice.description.lower():
                results[name] = choice
            elif any(query_lower in tag.lower() for tag in choice.tags):
                results[name] = choice

        return results


class OptionsDatabase(HTAPBaseModel):
    """Complete HTAP-options.json structure"""

    categories: Dict[str, OptionCategory] = Field(description="All option categories")

    def get_category(self, category_type: str) -> Optional[OptionCategory]:
        """Get an option category by type"""
        return self.categories.get(category_type)

    def list_categories(self) -> List[str]:
        """List all category types"""
        return list(self.categories.keys())

    def search_all(self, query: str) -> Dict[str, Dict[str, OptionChoice]]:
        """Search across all categories"""
        results = {}
        for cat_name, category in self.categories.items():
            cat_results = category.search_choices(query)
            if cat_results:
                results[cat_name] = cat_results
        return results
