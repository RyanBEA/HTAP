"""
Error handling utilities for HTAP Configuration Editor

Provides custom exceptions, error handler decorators, and utility functions
for graceful error handling with user-friendly messages.
"""

import streamlit as st
import traceback
from pathlib import Path
from typing import Callable, Any
from functools import wraps
from contextlib import contextmanager


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class HTAPError(Exception):
    """Base exception for HTAP Configuration Editor"""
    pass


class DataLoadError(HTAPError):
    """Error loading data files (options, costs, etc.)"""
    pass


class ValidationError(HTAPError):
    """Validation error (configuration, input, etc.)"""
    pass


class ExportError(HTAPError):
    """Error during export operations"""
    pass


# ============================================================================
# ERROR HANDLER DECORATOR
# ============================================================================

def handle_errors(error_message: str = "An error occurred", show_details: bool = False):
    """
    Decorator for handling errors with user-friendly messages

    Args:
        error_message: User-friendly error message to display
        show_details: Whether to show technical details in expander

    Usage:
        @handle_errors("Failed to load configuration", show_details=True)
        def load_config():
            # ... code that might raise errors

    Handles:
        - HTAPError and subclasses (custom error messages)
        - FileNotFoundError (file not found messages)
        - PermissionError (permission denied messages)
        - Exception (generic error messages)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)

            except HTAPError as e:
                # Custom HTAP errors - show the specific error message
                st.error(f"❌ {error_message}: {str(e)}")
                if show_details:
                    with st.expander("🔍 Technical Details"):
                        st.code(traceback.format_exc())
                return None

            except FileNotFoundError as e:
                # File not found - provide helpful guidance
                st.error(f"❌ {error_message}: File not found")
                st.info(
                    "**Troubleshooting:**\n"
                    "- Check that HTAP is installed at C:/HTAP/\n"
                    "- Verify the file path is correct\n"
                    "- Make sure you have read permissions"
                )
                if show_details:
                    with st.expander("🔍 Technical Details"):
                        st.code(f"File: {str(e)}\n\n{traceback.format_exc()}")
                return None

            except PermissionError as e:
                # Permission denied - provide helpful guidance
                st.error(f"❌ {error_message}: Permission denied")
                st.info(
                    "**Troubleshooting:**\n"
                    "- Check that you have write permissions to the target directory\n"
                    "- Close any programs that might have the file open\n"
                    "- Try running as administrator if necessary"
                )
                if show_details:
                    with st.expander("🔍 Technical Details"):
                        st.code(f"File: {str(e)}\n\n{traceback.format_exc()}")
                return None

            except Exception as e:
                # Generic error - show user-friendly message
                st.error(f"❌ {error_message}")
                st.warning(
                    "**An unexpected error occurred.**\n"
                    "If this persists, please check the technical details below and contact support."
                )
                if show_details:
                    with st.expander("🔍 Technical Details"):
                        st.code(f"Error: {str(e)}\n\n{traceback.format_exc()}")
                return None

        return wrapper
    return decorator


# ============================================================================
# FILE OPERATIONS
# ============================================================================

def safe_file_load(filepath: str, file_type: str = "file") -> bool:
    """
    Check if file exists and is readable, show appropriate errors

    Args:
        filepath: Path to the file
        file_type: Description of file type (e.g., "options database", "cost database")

    Returns:
        True if file is accessible, False otherwise

    Side effects:
        Shows error messages in Streamlit UI if file is not accessible
    """
    path = Path(filepath)

    # Check existence
    if not path.exists():
        st.error(f"❌ {file_type} not found: {filepath}")
        st.info(
            f"**Please ensure:**\n"
            f"- HTAP is installed at C:/HTAP/\n"
            f"- The {file_type} exists at the expected location\n"
            f"- The file path is correct"
        )
        return False

    # Check if it's a file (not directory)
    if not path.is_file():
        st.error(f"❌ {filepath} is not a file")
        return False

    # Check readability
    try:
        with open(path, 'r') as f:
            f.read(1)  # Try to read one character
        return True
    except PermissionError:
        st.error(f"❌ Permission denied reading {file_type}: {filepath}")
        st.info("Please check file permissions and try again")
        return False
    except Exception as e:
        st.error(f"❌ Error accessing {file_type}: {str(e)}")
        return False


# ============================================================================
# INPUT VALIDATION
# ============================================================================

def validate_input(
    value: Any,
    field_name: str,
    required: bool = True,
    min_length: int = None,
    max_length: int = None
) -> bool:
    """
    Validate user input with clear error messages

    Args:
        value: Value to validate
        field_name: Name of the field (for error messages)
        required: Whether the field is required
        min_length: Minimum length for string values
        max_length: Maximum length for string values

    Returns:
        True if valid, False otherwise

    Side effects:
        Shows error messages in Streamlit UI if validation fails
    """
    # Check required
    if required:
        if value is None or (isinstance(value, str) and not value.strip()):
            st.error(f"❌ {field_name} is required")
            return False
        if isinstance(value, (list, dict, set)) and len(value) == 0:
            st.error(f"❌ {field_name} cannot be empty")
            return False

    # Check min length
    if min_length is not None and isinstance(value, str):
        if len(value) < min_length:
            st.error(f"❌ {field_name} must be at least {min_length} characters")
            return False

    # Check max length
    if max_length is not None and isinstance(value, str):
        if len(value) > max_length:
            st.error(f"❌ {field_name} must be at most {max_length} characters")
            return False

    return True


# ============================================================================
# LOADING STATES
# ============================================================================

@contextmanager
def show_loading(message: str = "Loading..."):
    """
    Context manager for showing loading spinner

    Args:
        message: Loading message to display

    Usage:
        with show_loading("Loading data..."):
            # ... long operation
            pass
    """
    with st.spinner(message):
        yield


# ============================================================================
# ERROR RECOVERY
# ============================================================================

def try_recover(error_context: str, recovery_actions: list[str]) -> None:
    """
    Show error recovery suggestions

    Args:
        error_context: Context of the error (what failed)
        recovery_actions: List of suggested recovery actions

    Side effects:
        Shows error and recovery information in Streamlit UI
    """
    st.error(f"❌ {error_context}")

    if recovery_actions:
        st.info("**Try these steps to recover:**")
        for i, action in enumerate(recovery_actions, 1):
            st.info(f"{i}. {action}")


def show_error_with_guidance(
    error_message: str,
    troubleshooting_steps: list[str] = None,
    technical_details: str = None
) -> None:
    """
    Show comprehensive error message with troubleshooting guidance

    Args:
        error_message: User-friendly error message
        troubleshooting_steps: List of troubleshooting steps
        technical_details: Technical error details (optional)

    Side effects:
        Shows error information in Streamlit UI
    """
    st.error(f"❌ {error_message}")

    if troubleshooting_steps:
        st.info("**Troubleshooting:**")
        for step in troubleshooting_steps:
            st.info(f"• {step}")

    if technical_details:
        with st.expander("🔍 Technical Details"):
            st.code(technical_details)
