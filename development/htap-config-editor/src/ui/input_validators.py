"""
Input validation utilities for HTAP Configuration Editor

Provides validation functions for user inputs with clear error messages.
"""

import re
from typing import Tuple, List
from pathlib import Path


# ============================================================================
# FILENAME VALIDATION
# ============================================================================

def validate_filename(filename: str) -> Tuple[bool, str]:
    """
    Validate filename for .run file export

    Args:
        filename: Filename to validate

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if filename is valid, False otherwise
        - error_message: Empty string if valid, error description if invalid

    Checks:
        - Not empty
        - No invalid characters: < > : " / \\ | ? *
        - Ends with .run (or will be appended)
        - Length <= 255 characters
    """
    # Check empty
    if not filename or not filename.strip():
        return False, "Filename cannot be empty"

    filename = filename.strip()

    # Check invalid characters for Windows filenames
    invalid_chars = r'[<>:"/\\|?*]'
    if re.search(invalid_chars, filename):
        return False, "Filename contains invalid characters: < > : \" / \\ | ? *"

    # Check length (Windows MAX_PATH is 260, leave room for path)
    if len(filename) > 255:
        return False, f"Filename too long: {len(filename)} characters (max 255)"

    # Check/add .run extension
    if not filename.endswith('.run'):
        # Will be added automatically, so check total length with extension
        if len(filename) + 4 > 255:
            return False, "Filename too long (including .run extension)"

    # Check for reserved Windows names
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    name_without_ext = filename.replace('.run', '').upper()
    if name_without_ext in reserved_names:
        return False, f"'{filename}' is a reserved Windows filename"

    # All checks passed
    return True, ""


# ============================================================================
# ARCHETYPE VALIDATION
# ============================================================================

def validate_archetype_list(archetypes: List[str]) -> Tuple[bool, str]:
    """
    Validate list of archetype files

    Args:
        archetypes: List of archetype filenames

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if list is valid, False otherwise
        - error_message: Empty string if valid, error description if invalid

    Checks:
        - Not empty
        - All items end with .h2k
        - No duplicates
        - No empty strings
    """
    # Check empty
    if not archetypes or len(archetypes) == 0:
        return False, "At least one archetype must be selected"

    # Check for empty strings
    if any(not arch or not arch.strip() for arch in archetypes):
        return False, "Archetype list contains empty entries"

    # Check all end with .h2k
    non_h2k = [arch for arch in archetypes if not arch.endswith('.h2k')]
    if non_h2k:
        return False, f"All archetypes must be .h2k files. Invalid: {', '.join(non_h2k)}"

    # Check for duplicates
    if len(archetypes) != len(set(archetypes)):
        duplicates = [arch for arch in set(archetypes) if archetypes.count(arch) > 1]
        return False, f"Duplicate archetypes found: {', '.join(duplicates)}"

    # All checks passed
    return True, ""


# ============================================================================
# LOCATION VALIDATION
# ============================================================================

def validate_location(location: str) -> Tuple[bool, str]:
    """
    Validate location selection

    Args:
        location: Location string

    Returns:
        Tuple of (is_valid, error_message)

    Checks:
        - Not empty
        - Not placeholder value
    """
    if not location or not location.strip():
        return False, "Location must be selected"

    if location.strip().upper() in ['NA', 'NONE', 'SELECT']:
        return False, "Please select a valid location"

    return True, ""


# ============================================================================
# PATH VALIDATION
# ============================================================================

def sanitize_path(path: str) -> str:
    """
    Sanitize file path to prevent path traversal attacks

    Args:
        path: Path string to sanitize

    Returns:
        Sanitized path string

    Removes:
        - .. (parent directory references)
        - // and \\\\ (double slashes)
        - Leading/trailing whitespace
    """
    if not path:
        return ""

    # Remove leading/trailing whitespace
    path = path.strip()

    # Remove path traversal attempts
    path = path.replace('..', '')

    # Normalize slashes
    path = re.sub(r'\\\\+', '\\\\', path)  # Multiple backslashes -> single
    path = re.sub(r'//+', '/', path)  # Multiple forward slashes -> single

    return path


def validate_path_exists(path: str, path_type: str = "path") -> Tuple[bool, str]:
    """
    Validate that a path exists

    Args:
        path: Path to validate
        path_type: Description of path type (for error messages)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path or not path.strip():
        return False, f"{path_type} cannot be empty"

    path_obj = Path(path)

    if not path_obj.exists():
        return False, f"{path_type} does not exist: {path}"

    return True, ""


def validate_directory_writable(directory: str) -> Tuple[bool, str]:
    """
    Validate that a directory exists and is writable

    Args:
        directory: Directory path to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not directory or not directory.strip():
        return False, "Directory path cannot be empty"

    dir_path = Path(directory)

    # Check exists
    if not dir_path.exists():
        return False, f"Directory does not exist: {directory}"

    # Check is directory
    if not dir_path.is_dir():
        return False, f"Path is not a directory: {directory}"

    # Check writable (try to create a temp file)
    try:
        test_file = dir_path / '.htap_write_test'
        test_file.touch()
        test_file.unlink()
        return True, ""
    except PermissionError:
        return False, f"Permission denied: Cannot write to {directory}"
    except Exception as e:
        return False, f"Cannot write to directory: {str(e)}"


# ============================================================================
# OPTION VALIDATION
# ============================================================================

def validate_option_selection(selected_options: dict) -> Tuple[bool, str]:
    """
    Validate selected options dictionary

    Args:
        selected_options: Dict of {option_type: option_choice}

    Returns:
        Tuple of (is_valid, error_message)

    Checks:
        - Not empty
        - All keys start with 'Opt-'
        - All values are non-empty strings or sets
    """
    if not selected_options or len(selected_options) == 0:
        return False, "At least one option must be selected"

    # Check all keys are valid option types
    invalid_keys = [key for key in selected_options.keys() if not key.startswith('Opt-')]
    if invalid_keys:
        return False, f"Invalid option types: {', '.join(invalid_keys)}"

    # Check all values are non-empty
    for opt_type, opt_value in selected_options.items():
        if isinstance(opt_value, str):
            if not opt_value or not opt_value.strip():
                return False, f"Option {opt_type} has empty value"
        elif isinstance(opt_value, (list, set)):
            if len(opt_value) == 0:
                return False, f"Option {opt_type} has empty selection"
        else:
            return False, f"Option {opt_type} has invalid type: {type(opt_value)}"

    return True, ""


# ============================================================================
# COMBINATION COUNT VALIDATION
# ============================================================================

def validate_combination_count(total_combinations: int, warn_threshold: int = 100, error_threshold: int = 1000) -> Tuple[bool, str]:
    """
    Validate total combination count and provide warnings

    Args:
        total_combinations: Total number of simulation combinations
        warn_threshold: Threshold for showing warning (default: 100)
        error_threshold: Threshold for blocking export (default: 1000)

    Returns:
        Tuple of (is_valid, message)
        - is_valid: False if exceeds error threshold, True otherwise
        - message: Warning or error message
    """
    if total_combinations == 0:
        return False, "Configuration will generate 0 runs. Please select options."

    if total_combinations > error_threshold:
        return False, (
            f"Configuration will generate {total_combinations} runs. "
            f"This exceeds the recommended maximum of {error_threshold} and may be impractical. "
            "Consider reducing options or using sample mode."
        )

    if total_combinations > warn_threshold:
        return True, (
            f"Configuration will generate {total_combinations} runs. "
            f"This may take significant time to complete. Consider reducing options if practical."
        )

    return True, ""


# ============================================================================
# COMPOSITE VALIDATION
# ============================================================================

def validate_run_configuration(
    archetypes: List[str],
    location: str,
    selected_options: dict
) -> Tuple[bool, List[str]]:
    """
    Validate complete run configuration

    Args:
        archetypes: List of archetype files
        location: Selected location
        selected_options: Dict of selected options

    Returns:
        Tuple of (is_valid, error_messages)
        - is_valid: True if all validations pass
        - error_messages: List of error messages (empty if valid)
    """
    errors = []

    # Validate archetypes
    is_valid, error = validate_archetype_list(archetypes)
    if not is_valid:
        errors.append(f"Archetypes: {error}")

    # Validate location
    is_valid, error = validate_location(location)
    if not is_valid:
        errors.append(f"Location: {error}")

    # Validate options
    is_valid, error = validate_option_selection(selected_options)
    if not is_valid:
        errors.append(f"Options: {error}")

    return len(errors) == 0, errors
