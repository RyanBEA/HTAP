"""
Demonstration of HTAP Validation System
Shows all validation features with real data
"""

from src.utils import load_options, load_unit_costs, HTAPConfigValidator, CostResolver, ValidationSeverity


def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)


def print_messages(messages, indent=0):
    """Print validation messages with proper formatting"""
    prefix = "  " * indent
    for msg in messages:
        severity_icons = {
            'error': '[X]',
            'warning': '[!]',
            'info': '[i]'
        }
        icon = severity_icons.get(msg.severity.value, '[-]')
        category_info = f" ({msg.category})" if msg.category else ""
        print(f"{prefix}{icon} {msg.message}{category_info}")


def main():
    """Run validation demonstrations"""

    print_section("HTAP Configuration Validator - Demo")
    print("Loading HTAP data...")

    # Load data
    options_db = load_options('C:/HTAP/HTAP-options.json')
    costs_db = load_unit_costs('C:/HTAP/HTAPUnitCosts.json')
    cost_resolver = CostResolver(costs_db)
    validator = HTAPConfigValidator(options_db, cost_resolver)

    print(f"Loaded {len(options_db.categories)} option categories")
    print(f"Loaded {len(costs_db.data)} cost components")
    print(f"Validator initialized successfully")

    # Demo 1: Empty Configuration
    print_section("Demo 1: Empty Configuration Validation")
    messages = validator.validate_run_config({})
    print_messages(messages)
    print(f"\nHas errors: {validator.has_errors(messages)}")
    print(f"Has warnings: {validator.has_warnings(messages)}")

    # Demo 2: Valid Configuration
    print_section("Demo 2: Valid Configuration")
    valid_config = {
        'archetypes': ['test.h2k'],
        'location': 'Ottawa',
        'ruleset': 'as-found',
        'cost_source': 'LEEP-ON-Ottawa'
    }
    messages = validator.validate_run_config(valid_config)
    if messages:
        print_messages(messages)
    else:
        print("[OK] No validation issues found")
    print(f"\nHas errors: {validator.has_errors(messages)}")

    # Demo 3: Configuration with Warnings
    print_section("Demo 3: Configuration with Warnings")
    warning_config = {
        'archetypes': [f'archetype-{i}.h2k' for i in range(15)],
        'location': 'Ottawa',
        # Missing ruleset and cost_source
    }
    messages = validator.validate_run_config(warning_config)
    print_messages(messages)
    print(f"\nHas errors: {validator.has_errors(messages)}")
    print(f"Has warnings: {validator.has_warnings(messages)}")

    # Demo 4: Invalid Option Selection
    print_section("Demo 4: Invalid Option Selection")
    invalid_selections = {
        'Invalid-Category': 'some-choice',
        'Opt-ACH': 'invalid-choice-name'
    }
    messages = validator.validate_selected_options(invalid_selections)
    print_messages(messages)

    # Demo 5: Valid Option Selection
    print_section("Demo 5: Valid Option Selection")
    valid_selections = {
        'Opt-ACH': 'ACH_1_5'
    }
    messages = validator.validate_selected_options(
        valid_selections,
        'LEEP-ON-Ottawa'
    )
    if messages:
        print_messages(messages)
    else:
        print("[OK] No validation issues found")

    # Demo 6: Category Status
    print_section("Demo 6: Category Status Indicators")

    test_categories = [
        ('Opt-ACH', 'ACH_1_5'),
        ('Opt-ACH', None),  # Unselected
        ('Opt-ACH', 'invalid-choice'),  # Invalid
    ]

    for cat, choice in test_categories:
        icon, messages = validator.get_category_status(
            cat,
            choice,
            'LEEP-ON-Ottawa'
        )
        status_names = {
            '[v]': 'Valid',
            '[!]': 'Warning',
            '[X]': 'Error',
            '[ ]': 'Not Selected'
        }
        # Replace emojis with ASCII for console
        icon_ascii = {'✅': '[v]', '⚠️': '[!]', '❌': '[X]', '⬜': '[ ]'}.get(icon, icon)
        print(f"\nCategory: {cat}")
        print(f"Choice: {choice if choice else '(none)'}")
        print(f"Status: {icon_ascii} - {status_names.get(icon_ascii, 'Unknown')}")
        if messages:
            print_messages(messages, indent=1)

    # Demo 7: Full Configuration Validation
    print_section("Demo 7: Full Configuration Validation")

    full_config = {
        'archetypes': ['test1.h2k', 'test2.h2k'],
        'location': 'Ottawa',
        'ruleset': 'as-found',
        'cost_source': 'LEEP-ON-Ottawa'
    }

    full_selections = {
        'Opt-ACH': 'ACH_1_5',
        'Opt-Windows': 'NC_9_36'
    }

    results = validator.validate_full_configuration(full_config, full_selections)

    # Aggregate all messages
    all_messages = (
        results['run_config'] +
        results['options'] +
        results['completeness'] +
        results['summary']
    )

    # Count by severity
    errors = sum(1 for m in all_messages if m.severity == ValidationSeverity.ERROR)
    warnings = sum(1 for m in all_messages if m.severity == ValidationSeverity.WARNING)
    infos = sum(1 for m in all_messages if m.severity == ValidationSeverity.INFO)

    print(f"\nValidation Summary:")
    print(f"  Errors:   {errors}")
    print(f"  Warnings: {warnings}")
    print(f"  Info:     {infos}")
    print(f"  Total:    {len(all_messages)}")

    print("\nMessages by Section:")
    for section_name, messages in results.items():
        if messages:
            print(f"\n{section_name.replace('_', ' ').title()}:")
            print_messages(messages, indent=1)

    # Demo 8: Large Configuration Warning
    print_section("Demo 8: Large Configuration Warning")

    large_config = {
        'archetypes': [f'arch-{i}.h2k' for i in range(20)],
        'location': 'Ottawa',
        'ruleset': 'as-found',
        'cost_source': 'LEEP-ON-Ottawa'
    }

    large_selections = {
        f'Opt-Category-{i}': f'choice-{i}' for i in range(10)
    }

    results = validator.validate_full_configuration(large_config, large_selections)
    summary_messages = results['summary']

    print("Configuration:")
    print(f"  Archetypes: {len(large_config['archetypes'])}")
    print(f"  Options: {len(large_selections)}")
    print(f"  Total runs: {len(large_config['archetypes']) * len(large_selections)}")

    print("\nValidation:")
    print_messages(summary_messages)

    # Final Summary
    print_section("Demo Complete")
    print("All validation features demonstrated successfully!")
    print("\nKey Features:")
    print("  [v] Three severity levels: ERROR, WARNING, INFO")
    print("  [v] Run configuration validation")
    print("  [v] Option selection validation")
    print("  [v] Category status indicators")
    print("  [v] Configuration completeness checking")
    print("  [v] Combination count warnings")
    print("  [v] Cost data validation")
    print("\nIntegration:")
    print("  [v] LEFT panel: Run config validation")
    print("  [v] MIDDLE panel: Category status icons")
    print("  [v] RIGHT panel: Validation summary widget")


if __name__ == '__main__':
    main()
