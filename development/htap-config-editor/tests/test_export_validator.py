"""
Unit tests for export validation

Tests comprehensive pre-export validation to ensure configurations
are complete and valid before export.
"""

import pytest
from pathlib import Path

from src.utils import load_options
from src.utils.validator import HTAPConfigValidator, ValidationSeverity
from src.utils.export_validator import ExportValidator, ExportReadiness


@pytest.fixture
def options_db():
    """Load real options database"""
    path = "C:/HTAP/HTAP-options.json"
    if not Path(path).exists():
        pytest.skip(f"Options file not found: {path}")
    return load_options(path)


@pytest.fixture
def config_validator(options_db):
    """Create config validator"""
    return HTAPConfigValidator(options_db)


@pytest.fixture
def export_validator(options_db, config_validator):
    """Create export validator"""
    return ExportValidator(options_db, config_validator)


class TestExportReadiness:
    """Test export readiness determination"""

    def test_empty_config_blocked(self, export_validator):
        """Test that empty configuration is blocked"""
        run_config = {}
        selected_options = {}

        readiness, messages = export_validator.check_export_readiness(
            run_config,
            selected_options
        )

        assert readiness == ExportReadiness.BLOCKED
        assert any(msg.severity == ValidationSeverity.ERROR for msg in messages)

    def test_missing_archetypes_blocked(self, export_validator):
        """Test that configuration without archetypes is blocked"""
        run_config = {
            'archetypes': [],
            'location': 'Ottawa',
            'ruleset': 'as-found'
        }
        selected_options = {}

        readiness, messages = export_validator.check_export_readiness(
            run_config,
            selected_options
        )

        assert readiness == ExportReadiness.BLOCKED
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR]
        assert any('archetype' in msg.message.lower() for msg in errors)

    def test_missing_location_blocked(self, export_validator):
        """Test that configuration without location is blocked"""
        run_config = {
            'archetypes': ['test.h2k'],
            'location': None,
            'ruleset': 'as-found'
        }
        selected_options = {}

        readiness, messages = export_validator.check_export_readiness(
            run_config,
            selected_options
        )

        assert readiness == ExportReadiness.BLOCKED
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR]
        assert any('location' in msg.message.lower() for msg in errors)

    def test_invalid_option_blocked(self, export_validator):
        """Test that configuration with invalid option is blocked"""
        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'Ottawa',
            'ruleset': 'as-found'
        }
        selected_options = {
            'Invalid-Category-12345': {'invalid-choice'}
        }

        readiness, messages = export_validator.check_export_readiness(
            run_config,
            selected_options
        )

        assert readiness == ExportReadiness.BLOCKED
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR]
        assert any('unknown category' in msg.message.lower() for msg in errors)

    def test_invalid_choice_blocked(self, export_validator, options_db):
        """Test that configuration with invalid choice is blocked"""
        # Get valid category but use invalid choice
        cat_name = list(options_db.categories.keys())[0]

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'Ottawa',
            'ruleset': 'as-found'
        }
        selected_options = {
            cat_name: {'invalid-choice-12345'}
        }

        readiness, messages = export_validator.check_export_readiness(
            run_config,
            selected_options
        )

        assert readiness == ExportReadiness.BLOCKED
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR]
        assert any('unknown choice' in msg.message.lower() for msg in errors)

    def test_valid_config_ready_or_warnings(self, export_validator, options_db):
        """Test that valid configuration is ready or has warnings only"""
        # Get first valid option
        cat_name = list(options_db.categories.keys())[0]
        category = options_db.categories[cat_name]
        choice_name = list(category.options.keys())[0]

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'Ottawa',
            'ruleset': 'as-found',
            'cost_source': 'LEEP-ON-Ottawa'
        }
        selected_options = {
            cat_name: {choice_name}
        }

        readiness, messages = export_validator.check_export_readiness(
            run_config,
            selected_options
        )

        # Should be READY or WARNINGS, not BLOCKED
        assert readiness in [ExportReadiness.READY, ExportReadiness.WARNINGS]
        # Should not have any errors
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR]
        assert len(errors) == 0

    def test_large_combination_warning(self, export_validator):
        """Test warning for large number of combinations"""
        # Create config with >1000 combinations
        run_config = {
            'archetypes': [f'test{i}.h2k' for i in range(10)],  # 10 archetypes
            'location': 'Ottawa',
            'ruleset': 'as-found'
        }
        selected_options = {
            f'Opt-ACH': {f'ACH_{i}' for i in range(150)}  # 150 choices (impossible but tests the logic)
        }

        readiness, messages = export_validator.check_export_readiness(
            run_config,
            selected_options
        )

        # Should have warning (may also be BLOCKED due to invalid options, but should have warning about combos)
        warnings = [m for m in messages if m.severity == ValidationSeverity.WARNING]
        # Look for combination warning
        has_combo_warning = any(
            'combination' in msg.message.lower() or 'simulation runs' in msg.message.lower()
            for msg in warnings
        )
        assert has_combo_warning

    def test_no_options_warning(self, export_validator):
        """Test that configuration with no options has info message (not blocked)"""
        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'Ottawa',
            'ruleset': 'as-found'
        }
        selected_options = {}

        readiness, messages = export_validator.check_export_readiness(
            run_config,
            selected_options
        )

        # Should NOT be blocked (can export with defaults)
        assert readiness != ExportReadiness.BLOCKED

        # Should have info message about no options
        infos = [m for m in messages if m.severity == ValidationSeverity.INFO]
        assert any('no upgrade options' in msg.message.lower() or 'no options' in msg.message.lower() for msg in infos)

    def test_missing_ruleset_warning_not_blocking(self, export_validator):
        """Test that missing ruleset produces warning but doesn't block export"""
        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'Ottawa',
            'ruleset': None
        }
        selected_options = {}

        readiness, messages = export_validator.check_export_readiness(
            run_config,
            selected_options
        )

        # Should have warning but not be blocked
        warnings = [m for m in messages if m.severity == ValidationSeverity.WARNING]
        assert any('ruleset' in msg.message.lower() for msg in warnings)

        # Should be READY or WARNINGS, not BLOCKED
        assert readiness in [ExportReadiness.READY, ExportReadiness.WARNINGS]

    def test_multiple_archetypes_info(self, export_validator):
        """Test info/warning for multiple archetypes"""
        run_config = {
            'archetypes': ['test1.h2k', 'test2.h2k', 'test3.h2k'],
            'location': 'Ottawa',
            'ruleset': 'as-found'
        }
        selected_options = {}

        readiness, messages = export_validator.check_export_readiness(
            run_config,
            selected_options
        )

        # Should have message about combinations
        all_messages_text = ' '.join(msg.message.lower() for msg in messages)
        assert 'simulation run' in all_messages_text or 'combination' in all_messages_text


class TestValidationReport:
    """Test validation report generation"""

    def test_generate_report(self, export_validator):
        """Test that validation report is generated"""
        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'Ottawa',
            'ruleset': 'as-found'
        }
        selected_options = {}

        report = export_validator.generate_validation_report(
            run_config,
            selected_options
        )

        assert isinstance(report, str)
        assert len(report) > 0
        # Check for expected sections
        assert "Validation Report" in report
        assert "Export Readiness" in report
        assert "Configuration Summary" in report

    def test_report_shows_errors(self, export_validator):
        """Test that report displays errors"""
        run_config = {
            'archetypes': [],  # Error
            'location': None  # Error
        }
        selected_options = {}

        report = export_validator.generate_validation_report(
            run_config,
            selected_options
        )

        # Should show blocked status
        assert "BLOCKED" in report
        # Should have errors section
        assert "Errors" in report or "❌" in report

    def test_report_format(self, export_validator, options_db):
        """Test that report is valid markdown"""
        # Get valid option
        cat_name = list(options_db.categories.keys())[0]
        category = options_db.categories[cat_name]
        choice_name = list(category.options.keys())[0]

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'Ottawa',
            'ruleset': 'as-found'
        }
        selected_options = {
            cat_name: {choice_name}
        }

        report = export_validator.generate_validation_report(
            run_config,
            selected_options
        )

        # Check for markdown formatting
        assert report.startswith("#")  # Should start with heading
        assert "##" in report  # Should have subheadings
        assert "- " in report or "**" in report  # Should have lists or bold text


class TestCountCombinations:
    """Test combination counting"""

    def test_count_single_archetype_no_options(self, export_validator):
        """Test counting with single archetype and no options"""
        run_config = {
            'archetypes': ['test.h2k']
        }
        selected_options = {}

        count = export_validator._count_combinations(run_config, selected_options)
        assert count == 1

    def test_count_multiple_archetypes_no_options(self, export_validator):
        """Test counting with multiple archetypes and no options"""
        run_config = {
            'archetypes': ['test1.h2k', 'test2.h2k', 'test3.h2k']
        }
        selected_options = {}

        count = export_validator._count_combinations(run_config, selected_options)
        assert count == 3

    def test_count_single_archetype_single_option(self, export_validator):
        """Test counting with single archetype and single option"""
        run_config = {
            'archetypes': ['test.h2k']
        }
        selected_options = {
            'Opt-ACH': {'ACH_1_5', 'ACH_2_5'}
        }

        count = export_validator._count_combinations(run_config, selected_options)
        assert count == 2  # 1 archetype * 2 choices

    def test_count_multiple_dimensions(self, export_validator):
        """Test counting with multiple archetypes and multiple options"""
        run_config = {
            'archetypes': ['test1.h2k', 'test2.h2k']
        }
        selected_options = {
            'Opt-ACH': {'ACH_1_5', 'ACH_2_5', 'ACH_3_0'},
            'Opt-Windows': {'NC_9_36', 'NC_11_40'}
        }

        count = export_validator._count_combinations(run_config, selected_options)
        assert count == 12  # 2 archetypes * 3 ACH * 2 Windows

    def test_count_no_archetypes(self, export_validator):
        """Test that no archetypes returns 0"""
        run_config = {
            'archetypes': []
        }
        selected_options = {
            'Opt-ACH': {'ACH_1_5'}
        }

        count = export_validator._count_combinations(run_config, selected_options)
        assert count == 0


class TestFormatValidation:
    """Test run file format validation"""

    def test_valid_format_passes(self, export_validator, options_db):
        """Test that valid configuration generates valid format"""
        cat_name = list(options_db.categories.keys())[0]
        category = options_db.categories[cat_name]
        choice_name = list(category.options.keys())[0]

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'Ottawa',
            'ruleset': 'as-found'
        }
        selected_options = {
            cat_name: {choice_name}
        }

        messages = export_validator._validate_export_format(run_config, selected_options)

        # Should have no errors from format validation
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR and 'format' in msg.message.lower()]
        assert len(errors) == 0

    def test_format_validation_with_minimal_config(self, export_validator):
        """Test format validation with minimal valid config"""
        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'Ottawa',
            'ruleset': 'as-found'
        }
        selected_options = {}

        messages = export_validator._validate_export_format(run_config, selected_options)

        # Should not have format errors (may have other validation issues)
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR]
        # Format validation should pass even with minimal config
        assert not any('format' in msg.message.lower() for msg in errors)


class TestCompletenessValidation:
    """Test configuration completeness validation"""

    def test_missing_important_categories_info(self, export_validator):
        """Test that missing important categories generate info messages"""
        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'Ottawa'
        }
        selected_options = {}

        messages = export_validator._validate_completeness(run_config, selected_options)

        # Should have info messages about important categories
        infos = [m for m in messages if m.severity == ValidationSeverity.INFO]
        assert len(infos) > 0

    def test_zero_combinations_error(self, export_validator):
        """Test that zero combinations generates error"""
        run_config = {
            'archetypes': [],  # No archetypes = 0 combinations
            'location': 'Ottawa'
        }
        selected_options = {}

        messages = export_validator._validate_completeness(run_config, selected_options)

        # Should have error about 0 combinations
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR]
        assert any('0 simulation runs' in msg.message or '0 runs' in msg.message for msg in errors)

    def test_large_combination_warning_threshold(self, export_validator):
        """Test that >1000 combinations generates warning"""
        run_config = {
            'archetypes': [f'test{i}.h2k' for i in range(20)],  # 20 archetypes
            'location': 'Ottawa'
        }
        selected_options = {
            'Opt-Cat1': {f'choice{i}' for i in range(60)}  # 60 choices = 1200 runs
        }

        messages = export_validator._validate_completeness(run_config, selected_options)

        # Should have warning about large number
        warnings = [m for m in messages if m.severity == ValidationSeverity.WARNING]
        assert any('1200' in msg.message or 'simulation runs' in msg.message.lower() for msg in warnings)
