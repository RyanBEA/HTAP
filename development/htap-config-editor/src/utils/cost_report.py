"""
Cost report generation for HTAP configurations
Provides comprehensive cost summaries, breakdowns, and exports
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple
import pandas as pd
from io import StringIO

from src.models.option import OptionsDatabase, OptionChoice
from src.utils.cost_resolver import CostResolver


@dataclass
class CategoryCost:
    """Cost summary for a single category"""
    category: str
    options: List[str]
    total_materials: float
    total_labour: float
    total_cost: float
    component_count: int

    def __post_init__(self):
        """Ensure total_cost matches materials + labour"""
        self.total_cost = self.total_materials + self.total_labour


@dataclass
class ConfigurationCost:
    """Complete cost summary for a configuration"""
    total_materials: float
    total_labour: float
    total_cost: float
    category_costs: List[CategoryCost] = field(default_factory=list)
    component_details: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())

    def __post_init__(self):
        """Ensure total_cost matches materials + labour"""
        self.total_cost = self.total_materials + self.total_labour


class CostReportGenerator:
    """
    Generates cost reports for HTAP configurations
    Supports summaries, breakdowns, comparisons, and CSV exports
    """

    def __init__(self, options_db: OptionsDatabase, cost_resolver: CostResolver):
        """
        Initialize cost report generator

        Args:
            options_db: Loaded options database
            cost_resolver: Cost resolver with source inheritance
        """
        self.options_db = options_db
        self.cost_resolver = cost_resolver

    def calculate_configuration_cost(
        self,
        selected_options: Dict[str, Set[str]],
        cost_source: str
    ) -> ConfigurationCost:
        """
        Calculate total cost for a configuration

        Args:
            selected_options: Dict mapping category -> set of option names
            cost_source: Cost source to use (e.g., "LEEP-ON-Ottawa")

        Returns:
            ConfigurationCost with totals and breakdowns
        """
        all_category_costs = []
        all_component_details = []

        total_materials = 0.0
        total_labour = 0.0

        # Process each category
        for category_name, option_names in selected_options.items():
            if not option_names:
                continue

            category = self.options_db.get_category(category_name)
            if not category:
                continue

            # Calculate costs for all options in this category
            cat_materials = 0.0
            cat_labour = 0.0
            cat_component_count = 0

            for option_name in option_names:
                choice = category.get_choice(option_name)
                if not choice:
                    continue

                # Resolve option cost
                option_cost, details = self.cost_resolver.resolve_option_cost(
                    choice,
                    cost_source
                )

                # Aggregate materials and labour from details
                option_materials = sum(d.get('unit_cost_materials', 0) * d.get('quantity', 1) for d in details)
                option_labour = sum(d.get('unit_cost_labour', 0) * d.get('quantity', 1) for d in details)

                cat_materials += option_materials
                cat_labour += option_labour
                cat_component_count += len(details)

                # Add category and option info to details
                for detail in details:
                    detail['category'] = category_name
                    detail['option'] = option_name
                    all_component_details.append(detail)

            # Create category cost summary
            if cat_component_count > 0:
                category_cost = CategoryCost(
                    category=category_name,
                    options=sorted(option_names),
                    total_materials=cat_materials,
                    total_labour=cat_labour,
                    total_cost=cat_materials + cat_labour,
                    component_count=cat_component_count
                )
                all_category_costs.append(category_cost)

                total_materials += cat_materials
                total_labour += cat_labour

        # Create component details DataFrame
        if all_component_details:
            df = pd.DataFrame(all_component_details)

            # Calculate total_materials and total_labour columns if not present
            if 'total_materials' not in df.columns:
                df['total_materials'] = df['unit_cost_materials'] * df['quantity']
            if 'total_labour' not in df.columns:
                df['total_labour'] = df['unit_cost_labour'] * df['quantity']

            # Ensure all required columns exist with proper order
            required_cols = [
                'category', 'option', 'component_id', 'description',
                'quantity', 'units', 'unit_cost_materials', 'unit_cost_labour',
                'total_materials', 'total_labour', 'total_cost', 'source_used'
            ]

            # Add any missing columns with None
            for col in required_cols:
                if col not in df.columns:
                    df[col] = None

            # Select only required columns in proper order
            df = df[required_cols]
        else:
            df = pd.DataFrame()

        return ConfigurationCost(
            total_materials=total_materials,
            total_labour=total_labour,
            total_cost=total_materials + total_labour,
            category_costs=all_category_costs,
            component_details=df
        )

    def generate_cost_summary_text(self, config_cost: ConfigurationCost) -> str:
        """
        Generate markdown-formatted cost summary report

        Args:
            config_cost: Calculated configuration cost

        Returns:
            Markdown-formatted report string
        """
        lines = []
        lines.append("# HTAP Configuration Cost Summary")
        lines.append("")
        lines.append("## Total Costs")
        lines.append("")
        lines.append(f"- **Materials:** ${config_cost.total_materials:,.2f}")
        lines.append(f"- **Labour:** ${config_cost.total_labour:,.2f}")
        lines.append(f"- **Total Cost:** ${config_cost.total_cost:,.2f}")
        lines.append("")

        if config_cost.category_costs:
            lines.append("## Cost Breakdown by Category")
            lines.append("")

            for cat_cost in sorted(config_cost.category_costs, key=lambda c: c.total_cost, reverse=True):
                lines.append(f"### {cat_cost.category.replace('Opt-', '')}")
                lines.append("")
                lines.append(f"- **Options:** {', '.join(cat_cost.options)}")
                lines.append(f"- **Materials:** ${cat_cost.total_materials:,.2f}")
                lines.append(f"- **Labour:** ${cat_cost.total_labour:,.2f}")
                lines.append(f"- **Total:** ${cat_cost.total_cost:,.2f}")
                lines.append(f"- **Components:** {cat_cost.component_count}")
                lines.append("")

        if not config_cost.component_details.empty:
            lines.append("## Component Summary")
            lines.append("")
            lines.append(f"Total components: {len(config_cost.component_details)}")
            lines.append("")

            # Top 10 most expensive components
            top_components = config_cost.component_details.nlargest(10, 'total_cost')
            if not top_components.empty:
                lines.append("### Top 10 Most Expensive Components")
                lines.append("")
                for idx, row in top_components.iterrows():
                    lines.append(f"- **{row['component_id']}** ({row['category']}): ${row['total_cost']:,.2f}")
                lines.append("")

        lines.append("---")
        lines.append("*Generated by HTAP Configuration Editor*")

        return "\n".join(lines)

    def export_to_csv(self, config_cost: ConfigurationCost) -> str:
        """
        Export component details to CSV format

        Args:
            config_cost: Calculated configuration cost

        Returns:
            CSV-formatted string
        """
        if config_cost.component_details.empty:
            return "No component details available"

        # Use StringIO to generate CSV
        output = StringIO()
        config_cost.component_details.to_csv(output, index=False)
        return output.getvalue()

    def calculate_cost_comparison(
        self,
        selected_options: Dict[str, Set[str]],
        cost_sources: List[str]
    ) -> pd.DataFrame:
        """
        Calculate cost comparison across multiple sources

        Args:
            selected_options: Dict mapping category -> set of option names
            cost_sources: List of cost sources to compare

        Returns:
            DataFrame with columns: source, total_materials, total_labour, total_cost
        """
        comparison_data = []

        for source in cost_sources:
            config_cost = self.calculate_configuration_cost(selected_options, source)

            comparison_data.append({
                'source': source,
                'total_materials': config_cost.total_materials,
                'total_labour': config_cost.total_labour,
                'total_cost': config_cost.total_cost,
                'component_count': len(config_cost.component_details) if not config_cost.component_details.empty else 0
            })

        return pd.DataFrame(comparison_data)

    def get_category_summary(self, config_cost: ConfigurationCost) -> pd.DataFrame:
        """
        Get category-level summary as DataFrame

        Args:
            config_cost: Calculated configuration cost

        Returns:
            DataFrame with category cost summaries
        """
        if not config_cost.category_costs:
            return pd.DataFrame()

        data = []
        for cat_cost in config_cost.category_costs:
            data.append({
                'category': cat_cost.category.replace('Opt-', ''),
                'options_count': len(cat_cost.options),
                'options': ', '.join(cat_cost.options),
                'materials': cat_cost.total_materials,
                'labour': cat_cost.total_labour,
                'total_cost': cat_cost.total_cost,
                'component_count': cat_cost.component_count
            })

        return pd.DataFrame(data)

    def get_top_components(
        self,
        config_cost: ConfigurationCost,
        top_n: int = 10
    ) -> pd.DataFrame:
        """
        Get top N most expensive components

        Args:
            config_cost: Calculated configuration cost
            top_n: Number of top components to return

        Returns:
            DataFrame with top N components
        """
        if config_cost.component_details.empty:
            return pd.DataFrame()

        return config_cost.component_details.nlargest(top_n, 'total_cost')

    def validate_configuration_costs(
        self,
        selected_options: Dict[str, Set[str]],
        cost_source: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all selected options have cost data

        Args:
            selected_options: Dict mapping category -> set of option names
            cost_source: Cost source to validate against

        Returns:
            Tuple of (is_valid, list_of_missing_options)
        """
        missing = []

        for category_name, option_names in selected_options.items():
            category = self.options_db.get_category(category_name)
            if not category:
                continue

            for option_name in option_names:
                choice = category.get_choice(option_name)
                if not choice:
                    continue

                # Check if option has costs
                if not choice.costs or not choice.costs.components:
                    # Check if it has a cost proxy
                    if not choice.cost_proxy:
                        missing.append(f"{category_name}/{option_name}")
                    continue

                # Validate all components are available
                is_valid, missing_comps = self.cost_resolver.validate_option_costs(
                    choice,
                    cost_source
                )

                if not is_valid:
                    missing.append(f"{category_name}/{option_name} (missing components: {', '.join(missing_comps)})")

        return len(missing) == 0, missing
