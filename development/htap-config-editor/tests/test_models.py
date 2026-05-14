"""
Unit tests for Pydantic models
MUST USE REAL DATA - not mocks!
"""

import pytest
from pathlib import Path
from src.models.cost import UnitCostsDatabase, SourceCostData, CostSource
from src.models.option import OptionsDatabase, OptionCategory, OptionChoice, CostComponents
from src.utils.loaders import load_unit_costs, load_options, clear_cache


# Path to test data files
DATA_DIR = Path(__file__).parent.parent / "data"
UNIT_COSTS_FILE = str(DATA_DIR / "HTAPUnitCosts.json")
OPTIONS_FILE = str(DATA_DIR / "HTAP-options.json")


class TestCostModels:
    """Test cost data models with real data"""

    def test_source_cost_data_structure(self):
        """Test SourceCostData model matches actual structure"""
        # Real data sample from HTAPUnitCosts.json
        real_data = {
            "category": "DRYWALL",
            "description": "1/2in Gypsum board",
            "units": "sf wall",  # Note: plural!
            "UnitCostMaterials": 0.35,
            "UnitCostLabour": 0.41,
            "note": "n.d.",
            "date": "n.d.",
            "source": "LEEP-ON-Ottawa"
        }

        cost_data = SourceCostData(**real_data)
        assert cost_data.units == "sf wall"
        assert cost_data.total_cost() == 0.76
        assert cost_data.category == "DRYWALL"
        assert cost_data.description == "1/2in Gypsum board"

    def test_cost_source_structure(self):
        """Test CostSource model structure"""
        source_data = {
            "filename": "test.csv",
            "date_collated": "2016-09-01",
            "date_imported": "2020-04-24 09:42:09",
            "schema_used": "oldLeep",
            "origin": "Test source",
            "inherits": {
                "LEEP-ON-Ottawa": ["comp1", "comp2"]
            }
        }

        source = CostSource(**source_data)
        assert source.filename == "test.csv"
        assert "LEEP-ON-Ottawa" in source.inherits
        assert len(source.inherits["LEEP-ON-Ottawa"]) == 2

    def test_load_real_cost_database(self):
        """Test loading actual HTAPUnitCosts.json"""
        costs = load_unit_costs(UNIT_COSTS_FILE)

        # Verify structure
        assert len(costs.sources) > 0, "Should have cost sources"
        assert len(costs.data) > 0, "Should have cost data"

        # Verify methods work
        sources = costs.list_sources()
        assert len(sources) > 0
        assert isinstance(sources, list)

        components = costs.list_components()
        assert len(components) > 0
        assert isinstance(components, list)

    def test_cost_database_methods(self):
        """Test UnitCostsDatabase helper methods"""
        costs = load_unit_costs(UNIT_COSTS_FILE)

        # Test get_component
        first_comp = costs.list_components()[0]
        comp_data = costs.get_component(first_comp)
        assert comp_data is not None
        assert isinstance(comp_data, dict)

        # Test get_cost
        # Find a component that has data for the first source
        first_source = costs.list_sources()[0]
        components_with_source = costs.get_components_with_source(first_source)
        assert len(components_with_source) > 0

        # Test with a component that definitely has this source
        test_comp = components_with_source[0]
        cost = costs.get_cost(test_comp, first_source)
        assert cost is not None
        assert isinstance(cost, float)
        assert cost >= 0


class TestOptionModels:
    """Test option data models with real data"""

    def test_option_choice_structure(self):
        """Test OptionChoice model structure"""
        choice_data = {
            "choice_name": "test_choice",
            "h2kMap": {"base": {"tag": "value"}},
            "tags": ["tag1", "tag2"],
            "costs": {
                "components": ["comp1"],
                "custom-costs": {"field": 123}
            }
        }

        choice = OptionChoice(**choice_data)
        assert choice.choice_name == "test_choice"
        assert choice.h2k_map is not None
        assert len(choice.tags) == 2
        assert choice.costs is not None

    def test_option_category_has_metadata(self):
        """Test that category model includes all metadata fields"""
        cat_data = {
            "category_type": "Opt-Windows",
            "structure": "tree",
            "costed": True,
            "options": {},
            "default": "NA",
            "stop-on-error": True,
            "h2kSchema": ["House", "Components"]
        }

        category = OptionCategory(**cat_data)
        assert category.structure == "tree"
        assert category.costed is True
        assert category.default == "NA"
        assert category.stop_on_error is True
        assert category.h2k_schema == ["House", "Components"]
        assert category.category_type == "Opt-Windows"

    def test_load_real_options_database(self):
        """Test loading actual HTAP-options.json"""
        options = load_options(OPTIONS_FILE)

        # Verify we loaded categories
        assert len(options.categories) > 0, "Should have option categories"

        # Verify methods work
        categories = options.list_categories()
        assert len(categories) > 0
        assert isinstance(categories, list)

        # Get a category and verify structure
        first_cat = categories[0]
        category = options.get_category(first_cat)
        assert category is not None
        assert hasattr(category, "structure")
        assert hasattr(category, "costed")
        assert hasattr(category, "options")

    def test_option_category_methods(self):
        """Test OptionCategory helper methods"""
        options = load_options(OPTIONS_FILE)

        # Get first category with choices
        for cat_name in options.list_categories():
            category = options.get_category(cat_name)
            if len(category.options) > 0:
                # Test list_choices
                choices = category.list_choices()
                assert len(choices) > 0
                assert isinstance(choices, list)

                # Test get_choice
                first_choice = choices[0]
                choice = category.get_choice(first_choice)
                assert choice is not None
                assert choice.choice_name == first_choice

                # Test search_choices
                search_results = category.search_choices(first_choice[:3])
                assert isinstance(search_results, dict)
                break

    def test_custom_costs_field_exists(self):
        """Test that CostComponents has custom-costs field"""
        # Test with string components
        costs1 = CostComponents(
            components=["comp1"],
            custom_costs={"custom_field": 123}
        )
        assert "custom_field" in costs1.custom_costs
        assert costs1.custom_costs["custom_field"] == 123

        # Test with dict components (conditional costs)
        costs2 = CostComponents(
            components=[
                "comp1",
                {"H2KHouseInfo.HVAC/Furnace/capacity_kW": {"per?14": "furnace_component"}}
            ],
            custom_costs={}
        )
        assert len(costs2.components) == 2
        assert isinstance(costs2.components[0], str)
        assert isinstance(costs2.components[1], dict)

    def test_options_search_all(self):
        """Test search across all categories"""
        options = load_options(OPTIONS_FILE)

        # Search for a common term
        results = options.search_all("NA")
        assert isinstance(results, dict)


class TestLoaders:
    """Test loader functionality and caching"""

    def test_cache_functionality(self):
        """Test that caching works correctly"""
        import time

        # Clear cache first
        clear_cache()

        # First load (cold cache)
        start = time.time()
        costs1 = load_unit_costs(UNIT_COSTS_FILE)
        first_load_time = time.time() - start

        # Second load (warm cache)
        start = time.time()
        costs2 = load_unit_costs(UNIT_COSTS_FILE)
        second_load_time = time.time() - start

        # Cached load should be much faster
        assert second_load_time < first_load_time
        # Should be the same object
        assert costs1 is costs2

    def test_file_not_found_error(self):
        """Test that loaders raise FileNotFoundError for missing files"""
        with pytest.raises(FileNotFoundError):
            load_unit_costs("nonexistent.json")

        with pytest.raises(FileNotFoundError):
            load_options("nonexistent.json")

    def test_load_performance(self):
        """Test that loading completes within reasonable time"""
        import time

        clear_cache()

        # Load costs
        start = time.time()
        costs = load_unit_costs(UNIT_COSTS_FILE)
        costs_load_time = (time.time() - start) * 1000  # Convert to ms

        # Load options
        start = time.time()
        options = load_options(OPTIONS_FILE)
        options_load_time = (time.time() - start) * 1000  # Convert to ms

        # Should load relatively quickly (less than 500ms each)
        assert costs_load_time < 500, f"Cost loading took {costs_load_time:.0f}ms"
        assert options_load_time < 500, f"Options loading took {options_load_time:.0f}ms"

        print(f"\nLoad times:")
        print(f"  Costs: {costs_load_time:.0f}ms ({len(costs.data)} components)")
        print(f"  Options: {options_load_time:.0f}ms ({len(options.categories)} categories)")


class TestDataIntegrity:
    """Test data structure integrity with real HTAP files"""

    def test_all_cost_components_have_required_fields(self):
        """Verify all cost components have required fields"""
        costs = load_unit_costs(UNIT_COSTS_FILE)

        for comp_id, sources in costs.data.items():
            for source_name, source_data in sources.items():
                assert source_data.category, f"Component {comp_id} missing category"
                assert source_data.description, f"Component {comp_id} missing description"
                assert source_data.units, f"Component {comp_id} missing units"
                assert isinstance(source_data.UnitCostMaterials, (int, float))
                assert isinstance(source_data.UnitCostLabour, (int, float))
                # Source field should exist (may not always match key exactly)
                assert source_data.source, f"Component {comp_id} missing source field"

    def test_all_option_categories_valid(self):
        """Verify all option categories have valid structure"""
        options = load_options(OPTIONS_FILE)

        for cat_name, category in options.categories.items():
            assert category.category_type == cat_name
            assert category.structure in ["flat", "tree"]
            assert isinstance(category.costed, bool)
            assert isinstance(category.options, dict)

    def test_option_choices_have_valid_structure(self):
        """Verify option choices have valid structure"""
        options = load_options(OPTIONS_FILE)

        for cat_name, category in options.categories.items():
            for choice_name, choice in category.options.items():
                # choice_name should match the key
                assert choice.choice_name == choice_name
                # Tags should be a list
                assert isinstance(choice.tags, list)
                # If costs exist, validate structure
                if choice.costs:
                    assert isinstance(choice.costs.components, list)
                    # Components can be strings or dicts (conditional components)
                    for comp in choice.costs.components:
                        assert isinstance(comp, (str, dict))
