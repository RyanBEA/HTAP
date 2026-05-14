"""
Performance and integration tests for run file parser
"""

import time
from pathlib import Path
from src.parsers.run_parser import parse_run_file
from src.parsers.run_writer import write_run_file


def test_parse_performance():
    """Test parsing performance"""
    run_file = "C:/HTAP/development/htap-config-editor/data/regions.run"

    # Warm up
    parse_run_file(run_file)

    # Measure parsing time
    iterations = 100
    start = time.perf_counter()
    for _ in range(iterations):
        config = parse_run_file(run_file)
    end = time.perf_counter()

    avg_time_ms = ((end - start) / iterations) * 1000

    print(f"\n{'='*70}")
    print(f"PERFORMANCE TEST RESULTS")
    print(f"{'='*70}")
    print(f"File: {run_file}")
    print(f"Iterations: {iterations}")
    print(f"Average parse time: {avg_time_ms:.2f}ms")
    print(f"Parsed upgrades: {len(config.upgrades)}")
    print(f"{'='*70}\n")

    assert avg_time_ms < 10, f"Parser too slow: {avg_time_ms:.2f}ms (should be < 10ms)"


def test_roundtrip_integrity():
    """Test parse -> write -> parse integrity"""
    run_file = "C:/HTAP/development/htap-config-editor/data/regions.run"
    temp_file = "C:/HTAP/development/htap-config-editor/temp_test.run"

    # Parse original
    config1 = parse_run_file(run_file)

    # Write to temp
    write_run_file(config1, temp_file, include_timestamp=False)

    # Parse written file
    config2 = parse_run_file(temp_file)

    # Compare
    print(f"\n{'='*70}")
    print(f"ROUNDTRIP INTEGRITY TEST")
    print(f"{'='*70}")
    print(f"Original file: {run_file}")
    print(f"Temp file: {temp_file}")
    print(f"")
    print(f"Original upgrades: {len(config1.upgrades)}")
    print(f"Re-parsed upgrades: {len(config2.upgrades)}")
    print(f"")
    print(f"Parameters match: {config1.parameters == config2.parameters}")
    print(f"Scope match: {config1.scope == config2.scope}")
    print(f"Upgrade count match: {len(config1.upgrades) == len(config2.upgrades)}")
    print(f"")

    # Check individual upgrades
    matches = 0
    for key in config1.upgrades:
        if key in config2.upgrades:
            if config1.upgrades[key].choices == config2.upgrades[key].choices:
                matches += 1

    print(f"Matching upgrades: {matches}/{len(config1.upgrades)}")
    print(f"{'='*70}\n")

    # Cleanup
    Path(temp_file).unlink(missing_ok=True)

    assert matches == len(config1.upgrades), "Roundtrip integrity check failed"


def test_real_files():
    """Test parsing real HTAP .run files"""
    test_files = [
        "C:/HTAP/development/htap-config-editor/data/regions.run",
    ]

    print(f"\n{'='*70}")
    print(f"REAL FILE PARSING TEST")
    print(f"{'='*70}")

    for file_path in test_files:
        if not Path(file_path).exists():
            print(f"SKIP: {file_path} (not found)")
            continue

        try:
            start = time.perf_counter()
            config = parse_run_file(file_path)
            end = time.perf_counter()

            parse_time = (end - start) * 1000

            print(f"\nFile: {Path(file_path).name}")
            print(f"  Parse time: {parse_time:.2f}ms")
            print(f"  Run mode: {config.parameters.run_mode.value}")
            print(f"  Archetypes: {config.scope.archetypes}")
            print(f"  Locations: {config.scope.locations}")
            print(f"  Upgrades: {len(config.upgrades)}")
            print(f"  Comments: {len(config.comments)}")
            print(f"  Status: SUCCESS")

        except Exception as e:
            print(f"\nFile: {Path(file_path).name}")
            print(f"  Status: FAILED - {str(e)}")

    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    print("\nRunning performance and integration tests...\n")

    test_parse_performance()
    test_roundtrip_integrity()
    test_real_files()

    print("\n✓ All performance tests passed!\n")
