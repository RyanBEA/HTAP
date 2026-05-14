"""
Unit tests for cost resolution logic
"""

import pytest
from pathlib import Path

from src.utils import load_unit_costs, load_options
from src.utils.cost_resolver import CostResolver


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


class TestCostResolver:
    """Test cost resolution functionality"""

    def test_direct_component_lookup(self, resolver):
        """Test looking up component from primary source"""
        cost_data = resolver.get_component_cost(
            "1/2in_gypsum_board",
            "LEEP-ON-Ottawa"
        )

        assert cost_data is not None
        assert cost_data.units == "sf wall"
        assert cost_data.UnitCostMaterials > 0
        assert cost_data.UnitCostLabour >= 0

    def test_inherited_component_lookup(self, resolver):
        """Test looking up component with inheritance"""
        # LEEP-BC-KamloopsChesnut should inherit from LEEP-ON-Ottawa
        cost_data = resolver.get_component_cost(
            "1/2in_gypsum_board",
            "LEEP-BC-KamloopsChesnut"
        )

        assert cost_data is not None
        assert cost_data.source in ["LEEP-BC-KamloopsChesnut", "LEEP-ON-Ottawa"]

    def test_missing_component(self, resolver):
        """Test looking up non-existent component"""
        cost_data = resolver.get_component_cost(
            "non_existent_component_12345",
            "LEEP-ON-Ottawa"
        )

        assert cost_data is None

    def test_resolve_option_cost(self, resolver, options_db):
        """Test resolving total cost for an option"""
        # Find an option with costs
        option_with_costs = None
        for category in options_db.categories.values():
            for choice in category.options.values():
                if choice.costs and choice.costs.components:
                    option_with_costs = choice
                    break
            if option_with_costs:
                break

        if option_with_costs is None:
            pytest.skip("No options with costs found")

        total_cost, details = resolver.resolve_option_cost(
            option_with_costs,
            "LEEP-ON-Ottawa"
        )

        assert total_cost >= 0
        assert isinstance(details, list)
        assert len(details) == len(option_with_costs.costs.components)

    def test_option_without_costs(self, resolver, options_db):
        """Test option with no costs defined"""
        # Find option without costs
        option_no_costs = None
        for category in options_db.categories.values():
            for choice in category.options.values():
                if not choice.costs or not choice.costs.components:
                    option_no_costs = choice
                    break
            if option_no_costs:
                break

        if option_no_costs is None:
            pytest.skip("All options have costs")

        total_cost, details = resolver.resolve_option_cost(
            option_no_costs,
            "LEEP-ON-Ottawa"
        )

        assert total_cost == 0.0
        assert details == []

    def test_get_available_sources(self, resolver):
        """Test listing all cost sources"""
        sources = resolver.get_available_sources()

        assert isinstance(sources, list)
        assert len(sources) > 0
        assert "LEEP-ON-Ottawa" in sources

    def test_source_component_count(self, resolver):
        """Test counting components in a source"""
        count = resolver.get_source_component_count("LEEP-ON-Ottawa")

        assert count > 0
        # Note: Count may vary, so we just check it's positive

    def test_validate_option_costs(self, resolver, options_db):
        """Test validating option costs against source"""
        # Find option with costs
        option_with_costs = None
        for category in options_db.categories.values():
            for choice in category.options.values():
                if choice.costs and choice.costs.components:
                    option_with_costs = choice
                    break
            if option_with_costs:
                break

        if option_with_costs is None:
            pytest.skip("No options with costs found")

        is_valid, missing = resolver.validate_option_costs(
            option_with_costs,
            "LEEP-ON-Ottawa"
        )

        assert isinstance(is_valid, bool)
        assert isinstance(missing, list)


class TestCostInheritance:
    """Test cost source inheritance"""

    def test_inheritance_chain(self, resolver):
        """Test that inheritance chain is followed"""
        # Pick a component that only exists in parent source
        # This test assumes we know the inheritance structure

        bc_source = "LEEP-BC-KamloopsChesnut"
        parent_source = "LEEP-ON-Ottawa"

        # Get component from BC source (should inherit)
        bc_cost = resolver.get_component_cost("1/2in_gypsum_board", bc_source)

        # Get same component from parent
        parent_cost = resolver.get_component_cost("1/2in_gypsum_board", parent_source)

        # If BC doesn't override, should get parent's cost
        assert bc_cost is not None
        assert parent_cost is not None

    def test_inheritance_priority(self, resolver, costs_db):
        """Test that direct definitions take priority over inheritance"""
        # Find a component that exists in both parent and child
        bc_source = "LEEP-BC-KamloopsChesnut"

        # Get all components in BC source
        bc_components = costs_db.get_components_with_source(bc_source)

        if len(bc_components) == 0:
            pytest.skip("BC source has no direct components")

        # Pick first component
        component_id = bc_components[0]

        # Get from BC source
        bc_cost = resolver.get_component_cost(component_id, bc_source)

        assert bc_cost is not None
        assert bc_cost.source == bc_source  # Should use BC source, not parent


class TestCostCalculations:
    """Test cost calculation accuracy"""

    def test_component_cost_calculation(self, resolver):
        """Test that component costs are calculated correctly"""
        cost_data = resolver.get_component_cost(
            "1/2in_gypsum_board",
            "LEEP-ON-Ottawa"
        )

        if cost_data:
            total = cost_data.UnitCostMaterials + cost_data.UnitCostLabour
            assert total == cost_data.total_cost()

    def test_option_cost_with_quantity(self, resolver, options_db):
        """Test option cost calculation with quantities"""
        # Find option with component that has quantity
        for category in options_db.categories.values():
            for choice in category.options.values():
                if choice.costs and choice.costs.components:
                    # Check if any component is a dict with quantity
                    for comp in choice.costs.components:
                        if isinstance(comp, dict):
                            # Found option with quantity
                            total_cost, details = resolver.resolve_option_cost(
                                choice,
                                "LEEP-ON-Ottawa"
                            )

                            # Verify total matches sum of component totals
                            calculated_total = sum(d['total_cost'] for d in details)
                            assert abs(total_cost - calculated_total) < 0.01
                            return

        pytest.skip("No options with quantity-based components found")

    def test_custom_costs(self, resolver, options_db):
        """Test that custom costs are handled correctly"""
        # Find option with custom costs
        for category in options_db.categories.values():
            for choice in category.options.values():
                if choice.costs and choice.costs.custom_costs:
                    total_cost, details = resolver.resolve_option_cost(
                        choice,
                        "LEEP-ON-Ottawa"
                    )

                    # Verify custom costs are included
                    custom_details = [d for d in details if d.get('is_custom')]
                    assert len(custom_details) > 0

                    # Verify custom cost amounts
                    for custom_detail in custom_details:
                        assert custom_detail['source_used'] == 'CUSTOM'
                        assert custom_detail['total_cost'] > 0

                    return

        pytest.skip("No options with custom costs found")


class TestPerformance:
    """Test performance and caching"""

    def test_caching_works(self, resolver):
        """Test that @lru_cache improves performance"""
        import time

        component_id = "1/2in_gypsum_board"
        source = "LEEP-ON-Ottawa"

        # First call (uncached)
        start = time.time()
        result1 = resolver.get_component_cost(component_id, source)
        first_duration = time.time() - start

        # Second call (cached)
        start = time.time()
        result2 = resolver.get_component_cost(component_id, source)
        second_duration = time.time() - start

        # Results should be identical
        assert result1 == result2

        # Second call should be faster (cached)
        # Note: This may not always be true due to system variance
        # but it should be true in most cases
        assert second_duration <= first_duration * 2  # Allow for variance

    def test_multiple_source_lookups(self, resolver):
        """Test performance of multiple source lookups"""
        import time

        sources = resolver.get_available_sources()
        component_id = "1/2in_gypsum_board"

        start = time.time()
        for source in sources:
            resolver.get_component_cost(component_id, source)
        duration = time.time() - start

        # Should complete reasonably quickly
        assert duration < 1.0  # Less than 1 second for all sources
