"""
Unit tests for cost reporting functionality
"""

import pytest
from pathlib import Path
import pandas as pd

from src.utils import load_unit_costs, load_options
from src.utils.cost_resolver import CostResolver
from src.utils.cost_report import (
    CostReportGenerator,
    CategoryCost,
    ConfigurationCost
)


@pytest.fixture
def costs_db():
    """Load real costs database"""
    path = "C:/HTAP/HTAPUnitCosts.json"
    if not Path(path).exists():
        pytest.skip(f"Costs file not found: {path}")
    return load_unit_costs(path)


@pytest.fixture
def options_db():
    """Load real options database"""
    path = "C:/HTAP/HTAP-options.json"
    if not Path(path).exists():
        pytest.skip(f"Options file not found: {path}")
    return load_options(path)


@pytest.fixture
def resolver(costs_db):
    """Create cost resolver"""
    return CostResolver(costs_db)


@pytest.fixture
def cost_gen(options_db, resolver):
    """Create cost report generator"""
    return CostReportGenerator(options_db, resolver)


class TestCategoryAndConfigurationCost:
    """Test data classes"""

    def test_category_cost_dataclass(self):
        """Test CategoryCost dataclass initialization"""
        cat_cost = CategoryCost(
            category="Opt-Windows",
            options=["NC_9007-U1.60-SHGC0.22"],
            total_materials=100.0,
            total_labour=50.0,
            total_cost=150.0,
            component_count=5
        )

        assert cat_cost.category == "Opt-Windows"
        assert cat_cost.total_cost == 150.0
        assert cat_cost.component_count == 5

    def test_category_cost_post_init(self):
        """Test that total_cost is recalculated"""
        cat_cost = CategoryCost(
            category="Opt-Windows",
            options=["test"],
            total_materials=100.0,
            total_labour=50.0,
            total_cost=0.0,  # Will be overridden
            component_count=5
        )

        assert cat_cost.total_cost == 150.0

    def test_configuration_cost_dataclass(self):
        """Test ConfigurationCost dataclass initialization"""
        config_cost = ConfigurationCost(
            total_materials=200.0,
            total_labour=100.0,
            total_cost=300.0
        )

        assert config_cost.total_materials == 200.0
        assert config_cost.total_labour == 100.0
        assert config_cost.total_cost == 300.0
        assert isinstance(config_cost.category_costs, list)
        assert isinstance(config_cost.component_details, pd.DataFrame)

    def test_configuration_cost_post_init(self):
        """Test that total_cost is recalculated"""
        config_cost = ConfigurationCost(
            total_materials=200.0,
            total_labour=100.0,
            total_cost=0.0  # Will be overridden
        )

        assert config_cost.total_cost == 300.0


class TestCostCalculation:
    """Test cost calculation logic"""

    def test_calculate_single_option(self, cost_gen, options_db):
        """Test calculating cost for single option"""
        # Find an option with costs
        option_with_costs = None
        category_name = None

        for cat_name, category in options_db.categories.items():
            for choice_name, choice in category.options.items():
                if choice.costs and choice.costs.components:
                    option_with_costs = choice_name
                    category_name = cat_name
                    break
            if option_with_costs:
                break

        if option_with_costs is None:
            pytest.skip("No options with costs found")

        # Create selection
        selected_options = {category_name: {option_with_costs}}

        # Calculate cost
        config_cost = cost_gen.calculate_configuration_cost(
            selected_options,
            "LEEP-ON-Ottawa"
        )

        assert isinstance(config_cost, ConfigurationCost)
        assert config_cost.total_cost >= 0
        assert len(config_cost.category_costs) >= 0
        # Materials + Labour should equal Total
        assert abs(config_cost.total_cost - (config_cost.total_materials + config_cost.total_labour)) < 0.01

    def test_calculate_multiple_options(self, cost_gen, options_db):
        """Test calculating cost for multiple options across categories"""
        # Find multiple options with costs
        selected_options = {}
        max_categories = 3

        for cat_name, category in options_db.categories.items():
            if len(selected_options) >= max_categories:
                break

            for choice_name, choice in category.options.items():
                if choice.costs and choice.costs.components:
                    if cat_name not in selected_options:
                        selected_options[cat_name] = set()
                    selected_options[cat_name].add(choice_name)
                    break

        if len(selected_options) < 2:
            pytest.skip("Not enough options with costs found")

        # Calculate cost
        config_cost = cost_gen.calculate_configuration_cost(
            selected_options,
            "LEEP-ON-Ottawa"
        )

        assert config_cost.total_cost >= 0
        assert len(config_cost.category_costs) >= 1
        # Should have category costs for each category
        assert len(config_cost.category_costs) <= len(selected_options)

    def test_component_details_dataframe(self, cost_gen, options_db):
        """Test that component details DataFrame has correct structure"""
        # Find option with costs
        option_with_costs = None
        category_name = None

        for cat_name, category in options_db.categories.items():
            for choice_name, choice in category.options.items():
                if choice.costs and choice.costs.components:
                    option_with_costs = choice_name
                    category_name = cat_name
                    break
            if option_with_costs:
                break

        if option_with_costs is None:
            pytest.skip("No options with costs found")

        selected_options = {category_name: {option_with_costs}}

        config_cost = cost_gen.calculate_configuration_cost(
            selected_options,
            "LEEP-ON-Ottawa"
        )

        if not config_cost.component_details.empty:
            df = config_cost.component_details

            # Check required columns
            required_cols = [
                'category', 'option', 'component_id', 'description',
                'quantity', 'units', 'unit_cost_materials', 'unit_cost_labour',
                'total_cost', 'source_used', 'total_materials', 'total_labour'
            ]

            for col in required_cols:
                assert col in df.columns, f"Missing column: {col}"

            # Check data types
            assert df['category'].dtype == object
            assert df['option'].dtype == object
            assert pd.api.types.is_numeric_dtype(df['quantity'])
            assert pd.api.types.is_numeric_dtype(df['total_cost'])

    def test_zero_cost_options(self, cost_gen):
        """Test handling of options without cost data"""
        # Create selection with non-existent category (will have no costs)
        selected_options = {
            "Opt-NonExistent": {"SomeOption"}
        }

        config_cost = cost_gen.calculate_configuration_cost(
            selected_options,
            "LEEP-ON-Ottawa"
        )

        assert config_cost.total_cost == 0.0
        assert config_cost.total_materials == 0.0
        assert config_cost.total_labour == 0.0
        assert len(config_cost.category_costs) == 0

    def test_materials_labour_split(self, cost_gen, options_db):
        """Test that materials and labour are correctly separated"""
        # Find option with costs
        option_with_costs = None
        category_name = None

        for cat_name, category in options_db.categories.items():
            for choice_name, choice in category.options.items():
                if choice.costs and choice.costs.components:
                    option_with_costs = choice_name
                    category_name = cat_name
                    break
            if option_with_costs:
                break

        if option_with_costs is None:
            pytest.skip("No options with costs found")

        selected_options = {category_name: {option_with_costs}}

        config_cost = cost_gen.calculate_configuration_cost(
            selected_options,
            "LEEP-ON-Ottawa"
        )

        # Materials and labour should be non-negative
        assert config_cost.total_materials >= 0
        assert config_cost.total_labour >= 0

        # Total should equal sum
        assert abs(config_cost.total_cost - (config_cost.total_materials + config_cost.total_labour)) < 0.01

        # Check category costs too
        for cat_cost in config_cost.category_costs:
            assert cat_cost.total_materials >= 0
            assert cat_cost.total_labour >= 0
            assert abs(cat_cost.total_cost - (cat_cost.total_materials + cat_cost.total_labour)) < 0.01


class TestCostReports:
    """Test report generation"""

    def test_generate_summary_text(self, cost_gen, options_db):
        """Test generating markdown summary report"""
        # Find option with costs
        option_with_costs = None
        category_name = None

        for cat_name, category in options_db.categories.items():
            for choice_name, choice in category.options.items():
                if choice.costs and choice.costs.components:
                    option_with_costs = choice_name
                    category_name = cat_name
                    break
            if option_with_costs:
                break

        if option_with_costs is None:
            pytest.skip("No options with costs found")

        selected_options = {category_name: {option_with_costs}}

        config_cost = cost_gen.calculate_configuration_cost(
            selected_options,
            "LEEP-ON-Ottawa"
        )

        summary = cost_gen.generate_cost_summary_text(config_cost)

        # Check structure
        assert isinstance(summary, str)
        assert len(summary) > 0

        # Check for key sections
        assert "# HTAP Configuration Cost Summary" in summary
        assert "## Total Costs" in summary
        assert "Materials:" in summary
        assert "Labour:" in summary
        assert "Total Cost:" in summary

    def test_export_to_csv(self, cost_gen, options_db):
        """Test CSV export"""
        # Find option with costs
        option_with_costs = None
        category_name = None

        for cat_name, category in options_db.categories.items():
            for choice_name, choice in category.options.items():
                if choice.costs and choice.costs.components:
                    option_with_costs = choice_name
                    category_name = cat_name
                    break
            if option_with_costs:
                break

        if option_with_costs is None:
            pytest.skip("No options with costs found")

        selected_options = {category_name: {option_with_costs}}

        config_cost = cost_gen.calculate_configuration_cost(
            selected_options,
            "LEEP-ON-Ottawa"
        )

        csv_data = cost_gen.export_to_csv(config_cost)

        assert isinstance(csv_data, str)

        if not config_cost.component_details.empty:
            # Check CSV has headers
            assert "component_id" in csv_data
            assert "total_cost" in csv_data
        else:
            assert "No component details available" in csv_data

    def test_empty_configuration(self, cost_gen):
        """Test report generation with no options selected"""
        selected_options = {}

        config_cost = cost_gen.calculate_configuration_cost(
            selected_options,
            "LEEP-ON-Ottawa"
        )

        summary = cost_gen.generate_cost_summary_text(config_cost)

        assert isinstance(summary, str)
        assert "# HTAP Configuration Cost Summary" in summary
        assert "$0.00" in summary or "0.00" in summary

    def test_report_sections(self, cost_gen, options_db):
        """Test that all required sections are present in report"""
        # Find multiple options
        selected_options = {}
        max_categories = 2

        for cat_name, category in options_db.categories.items():
            if len(selected_options) >= max_categories:
                break

            for choice_name, choice in category.options.items():
                if choice.costs and choice.costs.components:
                    if cat_name not in selected_options:
                        selected_options[cat_name] = set()
                    selected_options[cat_name].add(choice_name)
                    break

        if len(selected_options) < 1:
            pytest.skip("Not enough options with costs found")

        config_cost = cost_gen.calculate_configuration_cost(
            selected_options,
            "LEEP-ON-Ottawa"
        )

        summary = cost_gen.generate_cost_summary_text(config_cost)

        # Check all sections exist
        assert "# HTAP Configuration Cost Summary" in summary
        assert "## Total Costs" in summary

        if config_cost.category_costs:
            assert "## Cost Breakdown by Category" in summary

        if not config_cost.component_details.empty:
            assert "## Component Summary" in summary


class TestCostComparison:
    """Test cost comparison across sources"""

    def test_compare_sources(self, cost_gen, options_db):
        """Test comparing costs across multiple sources"""
        # Find option with costs
        option_with_costs = None
        category_name = None

        for cat_name, category in options_db.categories.items():
            for choice_name, choice in category.options.items():
                if choice.costs and choice.costs.components:
                    option_with_costs = choice_name
                    category_name = cat_name
                    break
            if option_with_costs:
                break

        if option_with_costs is None:
            pytest.skip("No options with costs found")

        selected_options = {category_name: {option_with_costs}}

        # Get available sources
        sources = cost_gen.cost_resolver.get_available_sources()
        if len(sources) < 2:
            pytest.skip("Need at least 2 sources for comparison")

        # Compare first 2 sources
        comparison_df = cost_gen.calculate_cost_comparison(
            selected_options,
            sources[:2]
        )

        assert isinstance(comparison_df, pd.DataFrame)
        assert len(comparison_df) == 2

    def test_comparison_dataframe(self, cost_gen, options_db):
        """Test comparison DataFrame structure"""
        # Find option with costs
        option_with_costs = None
        category_name = None

        for cat_name, category in options_db.categories.items():
            for choice_name, choice in category.options.items():
                if choice.costs and choice.costs.components:
                    option_with_costs = choice_name
                    category_name = cat_name
                    break
            if option_with_costs:
                break

        if option_with_costs is None:
            pytest.skip("No options with costs found")

        selected_options = {category_name: {option_with_costs}}

        sources = cost_gen.cost_resolver.get_available_sources()
        if len(sources) < 1:
            pytest.skip("Need at least 1 source")

        comparison_df = cost_gen.calculate_cost_comparison(
            selected_options,
            [sources[0]]
        )

        # Check columns
        required_cols = ['source', 'total_materials', 'total_labour', 'total_cost', 'component_count']
        for col in required_cols:
            assert col in comparison_df.columns

        # Check data types
        assert pd.api.types.is_numeric_dtype(comparison_df['total_materials'])
        assert pd.api.types.is_numeric_dtype(comparison_df['total_labour'])
        assert pd.api.types.is_numeric_dtype(comparison_df['total_cost'])


class TestHelperMethods:
    """Test helper methods"""

    def test_get_category_summary(self, cost_gen, options_db):
        """Test getting category summary DataFrame"""
        # Find option with costs
        option_with_costs = None
        category_name = None

        for cat_name, category in options_db.categories.items():
            for choice_name, choice in category.options.items():
                if choice.costs and choice.costs.components:
                    option_with_costs = choice_name
                    category_name = cat_name
                    break
            if option_with_costs:
                break

        if option_with_costs is None:
            pytest.skip("No options with costs found")

        selected_options = {category_name: {option_with_costs}}

        config_cost = cost_gen.calculate_configuration_cost(
            selected_options,
            "LEEP-ON-Ottawa"
        )

        category_df = cost_gen.get_category_summary(config_cost)

        if not category_df.empty:
            assert 'category' in category_df.columns
            assert 'total_cost' in category_df.columns
            assert 'materials' in category_df.columns
            assert 'labour' in category_df.columns

    def test_get_top_components(self, cost_gen, options_db):
        """Test getting top N components"""
        # Find option with costs
        option_with_costs = None
        category_name = None

        for cat_name, category in options_db.categories.items():
            for choice_name, choice in category.options.items():
                if choice.costs and choice.costs.components:
                    option_with_costs = choice_name
                    category_name = cat_name
                    break
            if option_with_costs:
                break

        if option_with_costs is None:
            pytest.skip("No options with costs found")

        selected_options = {category_name: {option_with_costs}}

        config_cost = cost_gen.calculate_configuration_cost(
            selected_options,
            "LEEP-ON-Ottawa"
        )

        top_5 = cost_gen.get_top_components(config_cost, top_n=5)

        if not config_cost.component_details.empty:
            assert len(top_5) <= 5
            assert len(top_5) <= len(config_cost.component_details)

            # Check costs are sorted descending
            if len(top_5) > 1:
                costs = top_5['total_cost'].tolist()
                assert costs == sorted(costs, reverse=True)

    def test_validate_configuration_costs(self, cost_gen, options_db):
        """Test validating configuration costs"""
        # Find option with costs
        option_with_costs = None
        category_name = None

        for cat_name, category in options_db.categories.items():
            for choice_name, choice in category.options.items():
                if choice.costs and choice.costs.components:
                    option_with_costs = choice_name
                    category_name = cat_name
                    break
            if option_with_costs:
                break

        if option_with_costs is None:
            pytest.skip("No options with costs found")

        selected_options = {category_name: {option_with_costs}}

        is_valid, missing = cost_gen.validate_configuration_costs(
            selected_options,
            "LEEP-ON-Ottawa"
        )

        assert isinstance(is_valid, bool)
        assert isinstance(missing, list)
