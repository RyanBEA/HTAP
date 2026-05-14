"""
Test parser with multiple real HTAP .run files
"""

import time
from pathlib import Path
from src.parsers.run_parser import parse_run_file
from src.parsers.validation import validate_run_configuration


def test_multiple_run_files():
    """Test parsing multiple real HTAP .run files"""
    test_files = [
        "C:/HTAP/development/htap-config-editor/data/regions.run",
        "C:/HTAP/fdwr.run",
        "C:/HTAP/doc/examples/example.run",
        "C:/HTAP/recover/regions.run",
    ]

    print("\n" + "="*70)
    print("TESTING PARSER WITH REAL HTAP .RUN FILES")
    print("="*70 + "\n")

    total_files = 0
    successful = 0
    failed = 0

    for file_path in test_files:
        if not Path(file_path).exists():
            print(f"SKIP: {file_path} (not found)")
            continue

        total_files += 1

        try:
            start = time.perf_counter()
            config = parse_run_file(file_path)
            end = time.perf_counter()

            parse_time = (end - start) * 1000

            # Validate
            is_valid, errors = validate_run_configuration(config)

            print(f"File: {Path(file_path).name}")
            print(f"  Path: {file_path}")
            print(f"  Parse time: {parse_time:.2f}ms")
            print(f"  Run mode: {config.parameters.run_mode.value}")
            print(f"  Archetype dir: {config.parameters.archetype_dir}")
            print(f"  Archetypes: {config.scope.archetypes}")
            print(f"  Locations: {config.scope.locations}")
            print(f"  Rulesets: {config.scope.rulesets}")
            print(f"  Upgrades: {len(config.upgrades)}")
            print(f"  Comments: {len(config.comments)}")
            print(f"  Validation: {'VALID' if is_valid else 'INVALID'}")

            if errors:
                print(f"  Validation issues:")
                for error in errors[:3]:  # Show first 3
                    print(f"    - [{error.severity}] {error.message}")

            print(f"  Status: SUCCESS\n")
            successful += 1

        except Exception as e:
            print(f"File: {Path(file_path).name}")
            print(f"  Path: {file_path}")
            print(f"  Status: FAILED")
            print(f"  Error: {str(e)[:100]}\n")
            failed += 1

    print("="*70)
    print(f"SUMMARY")
    print("="*70)
    print(f"Total files tested: {total_files}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/total_files*100) if total_files > 0 else 0:.1f}%")
    print("="*70 + "\n")

    return successful, failed


if __name__ == "__main__":
    successful, failed = test_multiple_run_files()

    if failed == 0:
        print("All real file tests passed!")
    else:
        print(f"WARNING: {failed} file(s) failed to parse")
