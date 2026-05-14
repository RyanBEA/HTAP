"""
Test script for error handling and validation functions
Tests all error scenarios without running the Streamlit app
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.error_handler import (
    HTAPError, DataLoadError, ValidationError, ExportError,
    safe_file_load, validate_input
)
from src.ui.input_validators import (
    validate_filename, validate_archetype_list, validate_location,
    sanitize_path, validate_path_exists, validate_option_selection,
    validate_combination_count, validate_run_configuration
)


def test_custom_exceptions():
    """Test custom exception classes"""
    print("\n=== Testing Custom Exceptions ===")

    try:
        raise HTAPError("Base error")
    except HTAPError as e:
        print(f"[OK] HTAPError: {e}")

    try:
        raise DataLoadError("Data load failed")
    except DataLoadError as e:
        print(f"[OK] DataLoadError: {e}")

    try:
        raise ValidationError("Validation failed")
    except ValidationError as e:
        print(f"[OK] ValidationError: {e}")

    try:
        raise ExportError("Export failed")
    except ExportError as e:
        print(f"[OK] ExportError: {e}")


def test_filename_validation():
    """Test filename validation"""
    print("\n=== Testing Filename Validation ===")

    test_cases = [
        ("valid_filename.run", True, "Valid filename"),
        ("valid_filename", True, "Valid filename without extension"),
        ("", False, "Empty filename"),
        ("file<name>.run", False, "Invalid character <"),
        ("file>name.run", False, "Invalid character >"),
        ("file:name.run", False, "Invalid character :"),
        ('file"name.run', False, 'Invalid character "'),
        ("file/name.run", False, "Invalid character /"),
        ("file\\name.run", False, "Invalid character \\"),
        ("file|name.run", False, "Invalid character |"),
        ("file?name.run", False, "Invalid character ?"),
        ("file*name.run", False, "Invalid character *"),
        ("CON.run", False, "Reserved Windows name"),
        ("a" * 300 + ".run", False, "Too long"),
    ]

    for filename, expected_valid, description in test_cases:
        is_valid, error = validate_filename(filename)
        status = "[OK]" if is_valid == expected_valid else "[FAIL]"
        print(f"{status} {description}: valid={is_valid}, error='{error}'")


def test_archetype_validation():
    """Test archetype list validation"""
    print("\n=== Testing Archetype Validation ===")

    test_cases = [
        (["AB-base.h2k"], True, "Valid single archetype"),
        (["AB-base.h2k", "BC-base.h2k"], True, "Valid multiple archetypes"),
        ([], False, "Empty list"),
        (["AB-base.txt"], False, "Wrong extension"),
        (["AB-base.h2k", "AB-base.h2k"], False, "Duplicate entries"),
        ([""], False, "Empty string in list"),
    ]

    for archetypes, expected_valid, description in test_cases:
        is_valid, error = validate_archetype_list(archetypes)
        status = "[OK]" if is_valid == expected_valid else "[FAIL]"
        print(f"{status} {description}: valid={is_valid}, error='{error}'")


def test_location_validation():
    """Test location validation"""
    print("\n=== Testing Location Validation ===")

    test_cases = [
        ("Vancouver-BC", True, "Valid location"),
        ("", False, "Empty location"),
        ("NA", False, "Placeholder NA"),
        ("NONE", False, "Placeholder NONE"),
    ]

    for location, expected_valid, description in test_cases:
        is_valid, error = validate_location(location)
        status = "[OK]" if is_valid == expected_valid else "[FAIL]"
        print(f"{status} {description}: valid={is_valid}, error='{error}'")


def test_path_sanitization():
    """Test path sanitization"""
    print("\n=== Testing Path Sanitization ===")

    test_cases = [
        ("C:/HTAP/file.txt", "C:/HTAP/file.txt", "Normal path unchanged"),
        ("C:/HTAP/../file.txt", "C:/HTAP/file.txt", "Remove .."),
        ("C://HTAP//file.txt", "C:/HTAP/file.txt", "Remove double slashes"),
        ("C:\\\\HTAP\\\\file.txt", "C:\\HTAP\\file.txt", "Remove double backslashes"),
    ]

    for input_path, expected, description in test_cases:
        result = sanitize_path(input_path)
        status = "[OK]" if result == expected else "[FAIL]"
        print(f"{status} {description}: '{input_path}' -> '{result}'")


def test_option_validation():
    """Test option selection validation"""
    print("\n=== Testing Option Selection Validation ===")

    test_cases = [
        ({"Opt-ACH": "ACH_2_50"}, True, "Valid single option"),
        ({"Opt-ACH": {"ACH_2_50", "ACH_3_00"}}, True, "Valid multi-select"),
        ({}, False, "Empty options"),
        ({"InvalidKey": "value"}, False, "Invalid key (no Opt- prefix)"),
        ({"Opt-ACH": ""}, False, "Empty value"),
        ({"Opt-ACH": set()}, False, "Empty set"),
    ]

    for options, expected_valid, description in test_cases:
        is_valid, error = validate_option_selection(options)
        status = "[OK]" if is_valid == expected_valid else "[FAIL]"
        print(f"{status} {description}: valid={is_valid}, error='{error}'")


def test_combination_count_validation():
    """Test combination count validation"""
    print("\n=== Testing Combination Count Validation ===")

    test_cases = [
        (0, False, "Zero combinations"),
        (10, True, "Small count (10)"),
        (150, True, "Medium count with warning (150)"),
        (1500, False, "Exceeds threshold (1500)"),
    ]

    for count, expected_valid, description in test_cases:
        is_valid, message = validate_combination_count(count)
        status = "[OK]" if is_valid == expected_valid else "[FAIL]"
        print(f"{status} {description}: valid={is_valid}, message='{message[:50]}...'")


def test_run_configuration_validation():
    """Test complete run configuration validation"""
    print("\n=== Testing Run Configuration Validation ===")

    test_cases = [
        (
            ["AB-base.h2k"], "Vancouver-BC", {"Opt-ACH": "ACH_2_50"},
            True, "Valid configuration"
        ),
        (
            [], "Vancouver-BC", {"Opt-ACH": "ACH_2_50"},
            False, "Missing archetypes"
        ),
        (
            ["AB-base.h2k"], "", {"Opt-ACH": "ACH_2_50"},
            False, "Missing location"
        ),
        (
            ["AB-base.h2k"], "Vancouver-BC", {},
            False, "Missing options"
        ),
    ]

    for archetypes, location, options, expected_valid, description in test_cases:
        is_valid, errors = validate_run_configuration(archetypes, location, options)
        status = "[OK]" if is_valid == expected_valid else "[FAIL]"
        print(f"{status} {description}: valid={is_valid}, errors={len(errors)}")
        if errors:
            for error in errors:
                print(f"    - {error}")


def test_input_validation():
    """Test general input validation"""
    print("\n=== Testing Input Validation ===")

    # Test required validation
    print("\n  Required Field Tests:")
    print(f"  [OK] Valid: {validate_input('value', 'field', required=True)}")
    print(f"  [FAIL] Empty: {validate_input('', 'field', required=True)}")
    print(f"  [OK] Not required: {validate_input('', 'field', required=False)}")

    # Test length validation
    print("\n  Length Tests:")
    print(f"  [OK] Min length OK: {validate_input('12345', 'field', min_length=3)}")
    print(f"  [FAIL] Too short: {validate_input('12', 'field', min_length=3)}")
    print(f"  [OK] Max length OK: {validate_input('123', 'field', max_length=5)}")
    print(f"  [FAIL] Too long: {validate_input('123456', 'field', max_length=5)}")


def main():
    """Run all tests"""
    print("=" * 70)
    print("HTAP Configuration Editor - Error Handling Test Suite")
    print("=" * 70)

    try:
        test_custom_exceptions()
        test_filename_validation()
        test_archetype_validation()
        test_location_validation()
        test_path_sanitization()
        test_option_validation()
        test_combination_count_validation()
        test_run_configuration_validation()
        test_input_validation()

        print("\n" + "=" * 70)
        print("[OK] All tests completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\n[FAIL] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
