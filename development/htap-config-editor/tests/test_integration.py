"""
Integration tests for HTAP Configuration Editor
Tests complete end-to-end workflows
"""

import pytest
from pathlib import Path
from typing import Dict, Set

from src.utils.loaders import load_options, load_unit_costs
from src.utils.options_search import OptionsSearch
from src.utils.cost_resolver import CostResolver
from src.utils.run_file_generator import RunFileGenerator
from src.utils.export_validator import ExportValidator
from src.utils.cost_report import CostReportGenerator
from src.utils.validator import HTAPConfigValidator


@pytest.fixture
def htap_paths():
    """Returns paths to HTAP data files (skip tests if not found)"""
    options_path = Path("C:/HTAP/HTAP-options.json")
    costs_path = Path("C:/HTAP/HTAPUnitCosts.json")

    if not options_path.exists() or not costs_path.exists():
        pytest.skip("HTAP data files not found at C:/HTAP/")

    return {
        "options": str(options_path),
        "costs": str(costs_path)
    }


@pytest.fixture
def app_state(htap_paths):
    """
    Setup complete application state (simulates st.session_state)

    Returns:
        Dict with all initialized utilities and state
    """
    # Load databases
    options_db = load_options(htap_paths["options"])
    costs_db = load_unit_costs(htap_paths["costs"])

    # Initialize utilities
    search = OptionsSearch(options_db)
    cost_resolver = CostResolver(costs_db)
    validator = HTAPConfigValidator(options_db, cost_resolver)
    export_validator = ExportValidator(options_db, validator)
    cost_report_gen = CostReportGenerator(options_db, cost_resolver)

    # Create default run config (matches actual app structure)
    run_config = {
        'archetypes': ['test_archetype.h2k'],
        'location': 'OTTAWA',
        'ruleset': 'as-found',
        'cost_source': 'LEEP-ON-Ottawa'
    }

    # Selected options Dict[str, Set[str]]
    selected_options: Dict[str, Set[str]] = {}

    return {
        "options_db": options_db,
        "costs_db": costs_db,
        "search": search,
        "cost_resolver": cost_resolver,
        "validator": validator,
        "export_validator": export_validator,
        "cost_report_gen": cost_report_gen,
        "run_config": run_config,
        "selected_options": selected_options
    }


class TestCompleteWorkflow:
    """Test complete user workflows end-to-end"""

    def test_basic_configuration_workflow(self, app_state):
        """
        Test: Load data → Select options → Validate → Export
        """
        # Step 1: Verify data loaded
        assert app_state['options_db'] is not None
        assert len(app_state['options_db'].categories) > 30

        # Step 2: Select some valid options from actual data
        options_db = app_state['options_db']

        # Find valid ACH option
        if 'Opt-ACH' in options_db.categories:
            ach_options = list(options_db.categories['Opt-ACH'].options.keys())
            if ach_options:
                app_state['selected_options']['Opt-ACH'] = {ach_options[0]}

        # Find valid Window option
        if 'Opt-Windows' in options_db.categories:
            window_options = list(options_db.categories['Opt-Windows'].options.keys())
            if window_options:
                app_state['selected_options']['Opt-Windows'] = {window_options[0]}

        assert len(app_state['selected_options']) == 2

        # Step 3: Validate configuration
        validator = app_state['export_validator']
        readiness, messages = validator.check_export_readiness(
            app_state['run_config'],
            app_state['selected_options']
        )

        # Should be ready or have warnings (not blocked)
        assert readiness.value in ['ready', 'warnings']

        # Step 4: Export
        generator = RunFileGenerator()
        run_content = generator.generate_run_file(
            app_state['run_config'],
            app_state['selected_options']
        )

        # Step 5: Verify
        is_valid, errors = generator.validate_format(run_content)
        assert is_valid
        assert len(errors) == 0
        assert 'RunParameters_START' in run_content
        assert 'RunScope_START' in run_content
        assert 'Upgrades_START' in run_content

    def test_search_and_select_workflow(self, app_state):
        """
        Test: Search → Select → Verify
        """
        search = app_state['search']

        # Step 1: Search for windows
        results = search.search(query="window", limit=50)

        # Should find window options
        assert len(results) > 0

        # Step 2: Select first result
        if len(results) > 0:
            first_result = results.iloc[0]
            category = first_result['category']
            choice = first_result['choice']

            app_state['selected_options'][category] = {choice}

        # Step 3: Verify
        assert len(app_state['selected_options']) > 0

    def test_cost_calculation_workflow(self, app_state):
        """
        Test: Select options with costs → Calculate → Report → CSV
        """
        # Step 1: Select options with costs
        options_db = app_state['options_db']

        # Find a costed option
        for cat_name, category in options_db.categories.items():
            if category.costed:
                for choice_name, choice in category.options.items():
                    if choice.costs and choice.costs.components:
                        app_state['selected_options'][cat_name] = {choice_name}
                        break
                if cat_name in app_state['selected_options']:
                    break

        if not app_state['selected_options']:
            pytest.skip("No costed options found")

        # Step 2: Calculate costs
        cost_gen = app_state['cost_report_gen']
        config_cost = cost_gen.calculate_configuration_cost(
            app_state['selected_options'],
            app_state['run_config']['cost_source']
        )

        assert config_cost.total_cost >= 0

        # Step 3: Generate report
        summary = cost_gen.generate_cost_summary_text(config_cost)
        assert "Cost Summary" in summary or "Total Costs" in summary

        # Step 4: Export CSV
        csv_data = cost_gen.export_to_csv(config_cost)
        assert len(csv_data) > 0

    def test_multi_select_parametric_workflow(self, app_state):
        """
        Test: Multi-select → Count combinations → Export
        """
        # Step 1: Select multiple valid options per category
        options_db = app_state['options_db']

        # Get actual option names from database
        if 'Opt-ACH' in options_db.categories:
            ach_options = list(options_db.categories['Opt-ACH'].options.keys())[:3]
            if len(ach_options) >= 3:
                app_state['selected_options']['Opt-ACH'] = set(ach_options)

        if 'Opt-Windows' in options_db.categories:
            window_options = list(options_db.categories['Opt-Windows'].options.keys())[:2]
            if len(window_options) >= 2:
                app_state['selected_options']['Opt-Windows'] = set(window_options)

        # Step 2: Count combinations
        total = 1
        for choices in app_state['selected_options'].values():
            total *= len(choices)

        assert total == 6  # 3 * 2

        # Step 3: Export
        generator = RunFileGenerator()
        run_content = generator.generate_run_file(
            app_state['run_config'],
            app_state['selected_options']
        )

        is_valid, errors = generator.validate_format(run_content)
        assert is_valid


class TestDataIntegrity:
    """Test data integrity across the application"""

    def test_all_categories_loadable(self, app_state):
        """Test: All categories load correctly"""
        options_db = app_state['options_db']

        # Should have categories
        assert len(options_db.categories) > 30

        # All categories should have options
        for cat_name, category in options_db.categories.items():
            assert len(category.options) > 0, f"{cat_name} has no options"

    def test_cost_database_coverage(self, app_state):
        """Test: Cost database has components"""
        costs_db = app_state['costs_db']
        cost_resolver = app_state['cost_resolver']

        # Should have components
        assert len(costs_db.data) > 0

        # Should be able to get available sources
        sources = cost_resolver.get_available_sources()
        assert len(sources) > 0
        assert 'LEEP-ON-Ottawa' in sources

    def test_search_index_completeness(self, app_state):
        """Test: Search index covers all options"""
        search = app_state['search']
        options_db = app_state['options_db']

        # Count options in database
        total_options = sum(
            len(cat.options) for cat in options_db.categories.values()
        )

        # Count options in search index
        assert len(search.df) == total_options

    def test_validation_catches_errors(self, app_state):
        """Test: Validation detects invalid configs"""
        validator = app_state['export_validator']

        # Test empty config
        readiness, messages = validator.check_export_readiness({}, {})
        assert readiness.value == 'blocked'

        # Test invalid option
        bad_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }
        bad_options = {
            'Invalid-Category': {'Invalid-Choice'}
        }

        readiness, messages = validator.check_export_readiness(bad_config, bad_options)
        assert readiness.value == 'blocked'


class TestPerformance:
    """Test performance benchmarks"""

    def test_search_performance(self, app_state):
        """Test: Search completes quickly"""
        import time

        search = app_state['search']

        # Warm up
        search.search("test")

        # Time search
        start = time.time()
        results = search.search("window", limit=100)
        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 10, f"Search took {elapsed_ms:.1f}ms (expected <10ms)"
        assert len(results) > 0

    def test_cost_calculation_performance(self, app_state):
        """Test: Cost calculation is fast enough"""
        import time

        # Select options with costs
        options_db = app_state['options_db']
        count = 0
        for cat_name, category in options_db.categories.items():
            if category.costed and count < 5:
                choices = set(list(category.options.keys())[:2])
                app_state['selected_options'][cat_name] = choices
                count += 1

        if not app_state['selected_options']:
            pytest.skip("No costed options found")

        cost_gen = app_state['cost_report_gen']

        start = time.time()
        config_cost = cost_gen.calculate_configuration_cost(
            app_state['selected_options'],
            'LEEP-ON-Ottawa'
        )
        elapsed_ms = (time.time() - start) * 1000

        # Should complete in reasonable time
        assert elapsed_ms < 1000, f"Cost calc took {elapsed_ms:.1f}ms (expected <1000ms)"
