"""
Unit tests for configuration validation
"""

import pytest
from pathlib import Path

from src.utils import load_options, load_unit_costs
from src.utils.validator import HTAPConfigValidator, ValidationSeverity, ValidationMessage
from src.utils.cost_resolver import CostResolver


@pytest.fixture
def options_db():
    """Load real options database"""
    path = "C:/HTAP/HTAP-options.json"
    if not Path(path).exists():
        pytest.skip(f"Options file not found: {path}")
    return load_options(path)


@pytest.fixture
def costs_db():
    """Load real costs database"""
    path = "C:/HTAP/HTAPUnitCosts.json"
    if not Path(path).exists():
        pytest.skip(f"Costs file not found: {path}")
    return load_unit_costs(path)


@pytest.fixture
def cost_resolver(costs_db):
    """Create cost resolver"""
    return CostResolver(costs_db)


@pytest.fixture
def validator(options_db, cost_resolver):
    """Create validator"""
    return HTAPConfigValidator(options_db, cost_resolver)


class TestRunConfigValidation:
    """Test run configuration validation"""

    def test_empty_config(self, validator):
        """Test validation of empty configuration"""
        messages = validator.validate_run_config({})

        assert len(messages) > 0
        assert validator.has_errors(messages)

    def test_valid_config(self, validator):
        """Test validation of complete configuration"""
        config = {
            'archetypes': ['archetype1.h2k'],
            'location': 'Ottawa',
            'ruleset': 'as-found',
            'cost_source': 'LEEP-ON-Ottawa'
        }

        messages = validator.validate_run_config(config)

        # Should have no errors (may have info messages)
        assert not validator.has_errors(messages)

    def test_missing_archetypes(self, validator):
        """Test validation with missing archetypes"""
        config = {
            'archetypes': [],
            'location': 'Ottawa',
            'ruleset': 'as-found'
        }

        messages = validator.validate_run_config(config)

        assert validator.has_errors(messages)
        assert any('archetype' in msg.message.lower() for msg in messages)

    def test_missing_location(self, validator):
        """Test validation with missing location"""
        config = {
            'archetypes': ['test.h2k'],
            'ruleset': 'as-found'
        }

        messages = validator.validate_run_config(config)

        assert validator.has_errors(messages)
        assert any('location' in msg.message.lower() for msg in messages)

    def test_many_archetypes_warning(self, validator):
        """Test warning for large number of archetypes"""
        config = {
            'archetypes': [f'arch{i}.h2k' for i in range(15)],
            'location': 'Ottawa',
            'ruleset': 'as-found'
        }

        messages = validator.validate_run_config(config)

        assert validator.has_warnings(messages)

    def test_missing_ruleset_warning(self, validator):
        """Test warning for missing ruleset"""
        config = {
            'archetypes': ['test.h2k'],
            'location': 'Ottawa'
        }

        messages = validator.validate_run_config(config)

        # Should have warning about ruleset
        warning_messages = [m for m in messages if m.severity == ValidationSeverity.WARNING]
        assert any('ruleset' in msg.message.lower() for msg in warning_messages)

    def test_missing_cost_source_warning(self, validator):
        """Test warning for missing cost source"""
        config = {
            'archetypes': ['test.h2k'],
            'location': 'Ottawa',
            'ruleset': 'as-found'
        }

        messages = validator.validate_run_config(config)

        # Should have warning about cost source
        warning_messages = [m for m in messages if m.severity == ValidationSeverity.WARNING]
        assert any('cost' in msg.message.lower() for msg in warning_messages)


class TestOptionsValidation:
    """Test selected options validation"""

    def test_valid_selection(self, validator, options_db):
        """Test validation of valid option selection"""
        # Get first category and first option
        cat_name = list(options_db.categories.keys())[0]
        category = options_db.categories[cat_name]
        choice_name = list(category.options.keys())[0]

        selected = {cat_name: choice_name}
        messages = validator.validate_selected_options(selected)

        # Should have no errors
        assert not validator.has_errors(messages)

    def test_invalid_category(self, validator):
        """Test validation with invalid category"""
        selected = {'Invalid-Category': 'some-choice'}
        messages = validator.validate_selected_options(selected)

        assert validator.has_errors(messages)
        assert any('unknown category' in msg.message.lower() for msg in messages)

    def test_invalid_choice(self, validator, options_db):
        """Test validation with invalid choice in valid category"""
        cat_name = list(options_db.categories.keys())[0]
        selected = {cat_name: 'invalid-choice-name-12345'}

        messages = validator.validate_selected_options(selected)

        assert validator.has_errors(messages)
        assert any('unknown choice' in msg.message.lower() for msg in messages)

    def test_costed_option_without_costs(self, validator, options_db):
        """Test warning for costed category with option lacking costs"""
        # Find a costed category
        for cat_name, category in options_db.categories.items():
            if category.costed:
                # Find option without costs
                for choice_name, choice in category.options.items():
                    if not choice.costs or not choice.costs.components:
                        selected = {cat_name: choice_name}
                        messages = validator.validate_selected_options(
                            selected,
                            'LEEP-ON-Ottawa'
                        )

                        # Should have warning about missing costs
                        assert validator.has_warnings(messages)
                        return

        pytest.skip("No costed category with cost-less option found")

    def test_multiple_selections(self, validator, options_db):
        """Test validation with multiple selections"""
        # Select first option from first 3 categories
        selected = {}
        for i, (cat_name, category) in enumerate(options_db.categories.items()):
            if i >= 3:
                break
            choice_name = list(category.options.keys())[0]
            selected[cat_name] = choice_name

        messages = validator.validate_selected_options(selected)

        # Should have no errors for valid selections
        assert not validator.has_errors(messages)


class TestCategoryStatus:
    """Test category status checking"""

    def test_unselected_category_with_default(self, validator, options_db):
        """Test status of unselected category that has default"""
        # Find category with default
        for cat_name, category in options_db.categories.items():
            if hasattr(category, 'default') and category.default:
                icon, messages = validator.get_category_status(cat_name, None)

                assert icon == "⬜"
                assert any('default' in msg.message.lower() for msg in messages)
                return

        pytest.skip("No category with default found")

    def test_unselected_category_without_default(self, validator, options_db):
        """Test status of unselected category without default"""
        # Find category without default
        for cat_name, category in options_db.categories.items():
            if not hasattr(category, 'default') or not category.default:
                icon, messages = validator.get_category_status(cat_name, None)

                assert icon == "⬜"
                return

        pytest.skip("All categories have defaults")

    def test_selected_category(self, validator, options_db):
        """Test status of validly selected category"""
        cat_name = list(options_db.categories.keys())[0]
        category = options_db.categories[cat_name]
        choice_name = list(category.options.keys())[0]

        icon, messages = validator.get_category_status(
            cat_name,
            choice_name,
            'LEEP-ON-Ottawa'
        )

        assert icon in ["✅", "⚠️"]  # Valid or warning, not error

    def test_invalid_category_name(self, validator):
        """Test status with invalid category name"""
        icon, messages = validator.get_category_status(
            'Invalid-Category-12345',
            'some-choice'
        )

        assert icon == "❌"
        assert validator.has_errors(messages)

    def test_invalid_choice_in_category(self, validator, options_db):
        """Test status with invalid choice in valid category"""
        cat_name = list(options_db.categories.keys())[0]

        icon, messages = validator.get_category_status(
            cat_name,
            'invalid-choice-12345'
        )

        assert icon == "❌"
        assert validator.has_errors(messages)


class TestConfigurationCompleteness:
    """Test configuration completeness checking"""

    def test_empty_selections(self, validator):
        """Test completeness with no selections"""
        messages = validator.validate_configuration_completeness({})

        # Should have messages about important categories
        assert len(messages) > 0

    def test_partial_selections(self, validator, options_db):
        """Test completeness with partial selections"""
        # Select just one option
        cat_name = list(options_db.categories.keys())[0]
        category = options_db.categories[cat_name]
        choice_name = list(category.options.keys())[0]

        selected = {cat_name: choice_name}
        messages = validator.validate_configuration_completeness(selected)

        # May have info/warning messages about other categories
        # but should not have errors
        assert not validator.has_errors(messages)

    def test_important_categories_with_defaults(self, validator, options_db):
        """Test that categories with defaults get INFO messages"""
        # Find important category with default
        important_cats = ["Opt-Heating-Cooling", "Opt-DHWSystem", "Opt-VentSystem"]

        for cat_name in important_cats:
            if cat_name in options_db.categories:
                category = options_db.categories[cat_name]
                if hasattr(category, 'default') and category.default:
                    messages = validator.validate_configuration_completeness({})

                    # Should have INFO message for this category
                    info_messages = [m for m in messages if m.severity == ValidationSeverity.INFO]
                    assert any(cat_name in msg.category for msg in info_messages if msg.category)
                    return

        pytest.skip("No important category with default found")


class TestFullConfiguration:
    """Test full configuration validation"""

    def test_comprehensive_validation(self, validator):
        """Test full configuration validation"""
        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'Ottawa',
            'ruleset': 'as-found',
            'cost_source': 'LEEP-ON-Ottawa'
        }

        selected_options = {
            'Opt-ACH': 'ACH_1_5'
        }

        results = validator.validate_full_configuration(run_config, selected_options)

        assert 'run_config' in results
        assert 'options' in results
        assert 'completeness' in results
        assert 'summary' in results

        # All values should be lists of ValidationMessage
        assert isinstance(results['run_config'], list)
        assert isinstance(results['options'], list)
        assert isinstance(results['completeness'], list)
        assert isinstance(results['summary'], list)

    def test_validation_with_errors(self, validator):
        """Test full validation with errors"""
        run_config = {
            'archetypes': [],  # Error: no archetypes
            'location': None,  # Error: no location
        }

        selected_options = {
            'Invalid-Category': 'some-choice'  # Error: invalid category
        }

        results = validator.validate_full_configuration(run_config, selected_options)

        # Should have errors in both run_config and options
        all_messages = (
            results['run_config'] +
            results['options'] +
            results['completeness'] +
            results['summary']
        )

        assert validator.has_errors(all_messages)

    def test_combination_count_info(self, validator):
        """Test summary message about combination count"""
        run_config = {
            'archetypes': ['test1.h2k', 'test2.h2k'],
            'location': 'Ottawa',
            'ruleset': 'as-found',
            'cost_source': 'LEEP-ON-Ottawa'
        }

        selected_options = {
            'Opt-ACH': 'ACH_1_5',
            'Opt-Windows': 'NC_9_36'
        }

        results = validator.validate_full_configuration(run_config, selected_options)

        # Should have info message about combinations
        summary_messages = results['summary']
        assert len(summary_messages) > 0
        assert any('simulation runs' in msg.message.lower() for msg in summary_messages)

    def test_large_combination_warning(self, validator):
        """Test warning for large number of combinations"""
        run_config = {
            'archetypes': [f'test{i}.h2k' for i in range(10)],
            'location': 'Ottawa',
            'ruleset': 'as-found',
            'cost_source': 'LEEP-ON-Ottawa'
        }

        selected_options = {
            f'Opt-Category-{i}': f'choice-{i}' for i in range(15)
        }

        results = validator.validate_full_configuration(run_config, selected_options)

        # Should have warning about large combination count
        summary_messages = results['summary']
        warning_or_error = any(
            msg.severity in [ValidationSeverity.WARNING, ValidationSeverity.ERROR]
            for msg in summary_messages
        )
        assert warning_or_error

    def test_very_large_combination_error(self, validator):
        """Test error for very large number of combinations"""
        run_config = {
            'archetypes': [f'test{i}.h2k' for i in range(100)],
            'location': 'Ottawa',
            'ruleset': 'as-found',
            'cost_source': 'LEEP-ON-Ottawa'
        }

        selected_options = {
            f'Opt-Category-{i}': f'choice-{i}' for i in range(10)
        }

        results = validator.validate_full_configuration(run_config, selected_options)

        # Should have error about too many combinations (100 * 10 = 1000 > 500)
        summary_messages = results['summary']
        assert any(msg.severity == ValidationSeverity.ERROR for msg in summary_messages)


class TestHelperMethods:
    """Test helper methods"""

    def test_has_errors(self, validator):
        """Test has_errors method"""
        messages = [
            ValidationMessage(ValidationSeverity.ERROR, "Test error"),
            ValidationMessage(ValidationSeverity.WARNING, "Test warning")
        ]

        assert validator.has_errors(messages) is True

        messages = [
            ValidationMessage(ValidationSeverity.WARNING, "Test warning"),
            ValidationMessage(ValidationSeverity.INFO, "Test info")
        ]

        assert validator.has_errors(messages) is False

    def test_has_warnings(self, validator):
        """Test has_warnings method"""
        messages = [
            ValidationMessage(ValidationSeverity.WARNING, "Test warning"),
            ValidationMessage(ValidationSeverity.INFO, "Test info")
        ]

        assert validator.has_warnings(messages) is True

        messages = [
            ValidationMessage(ValidationSeverity.INFO, "Test info")
        ]

        assert validator.has_warnings(messages) is False

    def test_validation_message_repr(self):
        """Test ValidationMessage string representation"""
        msg = ValidationMessage(
            ValidationSeverity.ERROR,
            "Test message",
            category="Opt-Test"
        )

        repr_str = repr(msg)
        assert "ERROR" in repr_str
        assert "Test message" in repr_str
        assert "Opt-Test" in repr_str

    def test_validation_message_equality(self):
        """Test ValidationMessage equality"""
        msg1 = ValidationMessage(
            ValidationSeverity.ERROR,
            "Test message",
            category="Opt-Test"
        )

        msg2 = ValidationMessage(
            ValidationSeverity.ERROR,
            "Test message",
            category="Opt-Test"
        )

        msg3 = ValidationMessage(
            ValidationSeverity.WARNING,
            "Test message",
            category="Opt-Test"
        )

        assert msg1 == msg2
        assert msg1 != msg3
