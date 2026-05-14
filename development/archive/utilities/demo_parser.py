"""
Demonstration of the run file parser with real regions.run file
"""

from pathlib import Path
from src.parsers.run_parser import parse_run_file
from src.parsers.run_writer import write_run_file
from src.parsers.validation import validate_run_configuration


def main():
    """Demonstrate parser functionality"""

    # Parse the real regions.run file
    input_file = "C:/HTAP/development/htap-config-editor/data/regions.run"

    print("=" * 70)
    print("HTAP Run File Parser Demonstration")
    print("=" * 70)
    print()

    print(f"Reading: {input_file}")
    config = parse_run_file(input_file)
    print("Successfully parsed!")
    print()

    # Display RunParameters
    print("RunParameters:")
    print(f"  run-mode:       {config.parameters.run_mode.value}")
    print(f"  archetype-dir:  {config.parameters.archetype_dir}")
    print(f"  unit-costs-db:  {config.parameters.unit_costs_db}")
    print(f"  options-file:   {config.parameters.options_file}")
    print()

    # Display RunScope
    print("RunScope:")
    print(f"  archetypes:     {config.scope.archetypes}")
    print(f"  locations:      {config.scope.locations}")
    print(f"  rulesets:       {config.scope.rulesets}")
    print()

    # Display Upgrades
    print(f"Upgrades ({len(config.upgrades)} total):")
    for opt_type, upgrade in sorted(config.upgrades.items()):
        choices_str = ", ".join(upgrade.choices)
        print(f"  {opt_type:<30} = {choices_str}")
    print()

    # Validate configuration
    print("Validation:")
    is_valid, errors = validate_run_configuration(config)
    if is_valid:
        print("  Configuration is VALID")
    else:
        print("  Configuration has ERRORS")

    if errors:
        print(f"  Found {len(errors)} validation messages:")
        for error in errors:
            print(f"    {error}")
    print()

    # Test modification
    print("Testing modification:")
    print("  Adding upgrade: Opt-Heating-Cooling = NA, ASHP")
    config.add_upgrade("Opt-Heating-Cooling", ["NA", "ASHP"])
    print(f"  Total upgrades now: {len(config.upgrades)}")
    print()

    # Write to new file
    output_file = "C:/HTAP/development/htap-config-editor/demo_output.run"
    print(f"Writing to: {output_file}")
    write_run_file(config, output_file, include_timestamp=True)
    print("Successfully written!")
    print()

    # Verify roundtrip
    print("Verifying roundtrip (parse -> write -> parse):")
    config2 = parse_run_file(output_file)
    print(f"  Original upgrades: {len(config.upgrades)}")
    print(f"  Re-parsed upgrades: {len(config2.upgrades)}")
    print(f"  Match: {len(config.upgrades) == len(config2.upgrades)}")
    print()

    # Display sample of written file
    print("Sample of written file:")
    print("-" * 70)
    with open(output_file, 'r') as f:
        lines = f.readlines()[:30]  # First 30 lines
        print(''.join(lines))
        if len(lines) == 30:
            print("... (truncated)")
    print("-" * 70)
    print()

    print("=" * 70)
    print("Demonstration complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
