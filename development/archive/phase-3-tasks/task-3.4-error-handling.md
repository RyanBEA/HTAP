# Task 3.4: Error Handling & Polish

**Duration:** 2-3 hours
**Phase:** 3 - Export & Polish
**Dependencies:** All previous tasks
**Completion Criteria:** Robust error handling, smooth UX, proper loading states, user-friendly messages

---

## Objective

Improve application reliability and user experience by implementing comprehensive error handling, loading states, user-friendly error messages, and UI polish. Ensure the application gracefully handles all edge cases and provides clear feedback.

---

## What You'll Build

1. Global error handler
2. Loading states for all async operations
3. User-friendly error messages
4. Input validation and sanitization
5. Edge case handling
6. Progress indicators
7. Help text and tooltips
8. UI polish (spacing, alignment, icons)

---

## Step-by-Step Implementation

### Step 1: Create Error Handler Utility (45 min)

**File:** `src/utils/error_handler.py`

```python
"""
Error handling utilities
"""

import streamlit as st
import traceback
from typing import Optional, Callable, Any
from functools import wraps
from pathlib import Path


class HTAPError(Exception):
    """Base exception for HTAP application"""
    pass


class DataLoadError(HTAPError):
    """Error loading data files"""
    pass


class ValidationError(HTAPError):
    """Validation error"""
    pass


class ExportError(HTAPError):
    """Error during export"""
    pass


def handle_errors(
    error_message: str = "An error occurred",
    show_details: bool = False
):
    """
    Decorator for handling errors in functions

    Args:
        error_message: User-friendly error message
        show_details: Whether to show technical details
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except HTAPError as e:
                # Our errors - show user-friendly message
                st.error(f"❌ {error_message}: {str(e)}")
                if show_details:
                    with st.expander("🔍 Technical Details"):
                        st.code(traceback.format_exc())
                return None
            except FileNotFoundError as e:
                st.error(f"❌ File not found: {e.filename}")
                st.info("💡 Make sure HTAP is installed at C:/HTAP/")
                return None
            except PermissionError as e:
                st.error(f"❌ Permission denied: {str(e)}")
                st.info("💡 Check file permissions or try running as administrator")
                return None
            except Exception as e:
                # Unexpected errors
                st.error(f"❌ {error_message}")
                st.error(f"Details: {str(e)}")
                if show_details:
                    with st.expander("🔍 Stack Trace"):
                        st.code(traceback.format_exc())
                return None
        return wrapper
    return decorator


def safe_file_load(filepath: str, file_type: str = "file") -> bool:
    """
    Check if file exists and is readable

    Args:
        filepath: Path to file
        file_type: Type of file for error message

    Returns:
        True if file is accessible, False otherwise
    """
    path = Path(filepath)

    if not path.exists():
        st.error(f"❌ {file_type} not found: {filepath}")
        return False

    if not path.is_file():
        st.error(f"❌ Path is not a file: {filepath}")
        return False

    try:
        # Try to open file
        with open(path, 'r') as f:
            f.read(1)  # Read 1 byte to check permissions
        return True
    except PermissionError:
        st.error(f"❌ No permission to read {file_type}: {filepath}")
        return False
    except Exception as e:
        st.error(f"❌ Error accessing {file_type}: {str(e)}")
        return False


def validate_input(
    value: Any,
    field_name: str,
    required: bool = True,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None
) -> bool:
    """
    Validate user input

    Args:
        value: Value to validate
        field_name: Field name for error messages
        required: Whether field is required
        min_length: Minimum length (for strings/lists)
        max_length: Maximum length (for strings/lists)

    Returns:
        True if valid, False otherwise
    """
    # Check required
    if required and not value:
        st.error(f"❌ {field_name} is required")
        return False

    # Check length
    if value and min_length and len(value) < min_length:
        st.error(f"❌ {field_name} must be at least {min_length} characters/items")
        return False

    if value and max_length and len(value) > max_length:
        st.error(f"❌ {field_name} cannot exceed {max_length} characters/items")
        return False

    return True


def show_loading(message: str = "Loading..."):
    """
    Context manager for showing loading spinner

    Usage:
        with show_loading("Loading data..."):
            # Do work
            pass
    """
    return st.spinner(message)
```

---

### Step 2: Add Loading States (45 min)

**File:** `src/ui/loading_states.py`

```python
"""
Loading state management
"""

import streamlit as st
from typing import Callable, Any


def with_loading_state(
    func: Callable,
    loading_message: str = "Loading...",
    success_message: Optional[str] = None
) -> Any:
    """
    Execute function with loading state

    Args:
        func: Function to execute
        loading_message: Message to show while loading
        success_message: Message to show on success (optional)

    Returns:
        Result of function
    """
    with st.spinner(loading_message):
        result = func()

    if success_message and result is not None:
        st.success(success_message)

    return result


def initialize_app_with_loading():
    """
    Initialize app with proper loading states
    """
    # Load options database
    if 'options_db' not in st.session_state:
        with st.spinner("📂 Loading HTAP options database..."):
            try:
                from src.utils import load_options
                options_path = "C:/HTAP/HTAP-options.json"

                from src.utils.error_handler import safe_file_load
                if safe_file_load(options_path, "Options database"):
                    st.session_state.options_db = load_options(options_path)
                    st.success("✅ Loaded 34 option categories")
            except Exception as e:
                st.error(f"❌ Failed to load options: {e}")
                st.stop()

    # Load costs database
    if 'costs_db' not in st.session_state:
        with st.spinner("💰 Loading unit costs database..."):
            try:
                from src.utils import load_unit_costs
                costs_path = "C:/HTAP/HTAPUnitCosts.json"

                from src.utils.error_handler import safe_file_load
                if safe_file_load(costs_path, "Costs database"):
                    st.session_state.costs_db = load_unit_costs(costs_path)
                    st.success("✅ Loaded 351 cost components")
            except Exception as e:
                st.error(f"❌ Failed to load costs: {e}")
                st.stop()

    # Initialize cost resolver
    if 'cost_resolver' not in st.session_state:
        with st.spinner("⚙️ Initializing cost resolver..."):
            from src.utils.cost_resolver import CostResolver
            st.session_state.cost_resolver = CostResolver(st.session_state.costs_db)

    # Initialize search index
    if 'search_index' not in st.session_state:
        with st.spinner("🔍 Building search index..."):
            from src.utils.options_search import OptionsSearch
            st.session_state.search_index = OptionsSearch(st.session_state.options_db)

    # Initialize validators
    if 'validator' not in st.session_state:
        with st.spinner("✓ Initializing validators..."):
            from src.utils.validator import HTAPConfigValidator
            st.session_state.validator = HTAPConfigValidator(
                st.session_state.options_db,
                st.session_state.cost_resolver
            )

    if 'export_validator' not in st.session_state:
        from src.utils.export_validator import ExportValidator
        st.session_state.export_validator = ExportValidator(
            st.session_state.options_db,
            st.session_state.validator
        )
```

---

### Step 3: Add Help Text and Tooltips (30 min)

**File:** `src/ui/help_content.py`

```python
"""
Help content and tooltips
"""

HELP_TEXT = {
    "archetypes": """
        **Archetypes** are base building models in HOT2000 format (.h2k files).

        Each archetype represents a different building type, size, or configuration.
        Archetypes should be located in `C:/HTAP/archetypes/`.

        💡 Tip: You can select multiple archetypes to run simulations on different building types.
    """,

    "location": """
        **Location** determines the weather data used for the simulation.

        Each location has specific:
        - Temperature profiles
        - Solar radiation data
        - Heating/cooling degree days

        💡 Tip: Choose the location closest to your project site.
    """,

    "ruleset": """
        **Ruleset** defines building code compliance requirements.

        Common rulesets:
        - `as-found`: No code requirements, evaluate as-is
        - `NBC`: National Building Code
        - `BC-Step-3`: BC Energy Step Code Level 3

        💡 Tip: Use 'as-found' for baseline analysis.
    """,

    "cost_source": """
        **Cost Source** determines which cost database to use.

        Different sources have region-specific costs for:
        - Materials
        - Labour
        - Installation

        💡 Tip: Choose a source that matches your project location.
    """,

    "multi_select": """
        **Multi-Select Mode** allows selecting multiple options per category.

        This creates parametric runs:
        - Single-select: One simulation per configuration
        - Multi-select: Simulations for all combinations

        Example: 3 archetypes × 2 wall options = 6 simulations

        ⚠️ Warning: Be careful with large combinations (>100 runs).
    """,

    "export_validation": """
        **Export Validation** checks your configuration before export.

        Validation checks:
        - ✅ Required fields present
        - ✅ Options exist in database
        - ✅ File format is correct

        Errors must be fixed before export.
        Warnings are optional but recommended to review.
    """
}


def show_help_button(key: str):
    """
    Show help button with content

    Args:
        key: Key for help content
    """
    import streamlit as st

    if key in HELP_TEXT:
        with st.expander("❓ Help"):
            st.markdown(HELP_TEXT[key])
```

---

### Step 4: Add Input Validation (30 min)

**File:** `src/ui/input_validators.py`

```python
"""
Input validation for UI components
"""

import streamlit as st
from pathlib import Path
import re


def validate_filename(filename: str) -> tuple[bool, str]:
    """
    Validate filename for export

    Args:
        filename: Filename to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "Filename cannot be empty"

    # Check for invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        if char in filename:
            return False, f"Filename cannot contain '{char}'"

    # Check extension
    if not filename.endswith('.run'):
        return False, "Filename must end with .run"

    # Check length
    if len(filename) > 255:
        return False, "Filename too long (max 255 characters)"

    return True, ""


def validate_archetype_list(archetypes: list) -> tuple[bool, str]:
    """
    Validate archetype list

    Args:
        archetypes: List of archetype filenames

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not archetypes:
        return False, "At least one archetype must be selected"

    # Check each archetype
    for arch in archetypes:
        if not arch.endswith('.h2k'):
            return False, f"Invalid archetype file: {arch} (must be .h2k)"

    # Check for duplicates
    if len(archetypes) != len(set(archetypes)):
        return False, "Duplicate archetypes selected"

    return True, ""


def sanitize_path(path: str) -> str:
    """
    Sanitize file path for safety

    Args:
        path: Path to sanitize

    Returns:
        Sanitized path
    """
    # Remove any potentially dangerous path components
    path = path.replace('..', '')
    path = path.replace('//', '/')
    path = path.replace('\\\\', '\\')

    return path
```

---

### Step 5: Update App with Error Handling (30 min)

**File:** `src/app.py`

Add error handling to main app:

```python
"""
Main Streamlit application with error handling
"""

import streamlit as st
from src.ui.loading_states import initialize_app_with_loading
from src.utils.error_handler import handle_errors


# Page configuration
st.set_page_config(
    page_title="HTAP Configuration Editor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)


@handle_errors("Failed to initialize application", show_details=True)
def main():
    """Main application entry point"""

    st.title("🏠 HTAP Configuration Editor")
    st.caption("Create and manage HOT2000 parametric run configurations")

    # Initialize app with loading states
    try:
        initialize_app_with_loading()
    except Exception as e:
        st.error(f"❌ Application initialization failed: {e}")
        st.stop()

    # Render panels
    try:
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            from src.ui.left_panel import render_left_panel
            render_left_panel()

        with col2:
            from src.ui.middle_panel import render_middle_panel
            render_middle_panel()

        with col3:
            from src.ui.right_panel import render_right_panel
            render_right_panel()

    except Exception as e:
        st.error(f"❌ Error rendering UI: {e}")
        with st.expander("🔍 Details"):
            import traceback
            st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
```

---

### Step 6: Add UI Polish (30 min)

**File:** `src/ui/styles.py`

```python
"""
UI styles and polish
"""

import streamlit as st


def apply_custom_styles():
    """
    Apply custom CSS styles
    """
    st.markdown("""
        <style>
        /* Improve spacing */
        .stButton > button {
            margin: 2px 0;
        }

        /* Better metrics display */
        [data-testid="stMetricValue"] {
            font-size: 24px;
        }

        /* Improve expander appearance */
        .streamlit-expanderHeader {
            font-weight: 600;
        }

        /* Better divider visibility */
        hr {
            margin: 1.5rem 0;
            border-top: 2px solid #e0e0e0;
        }

        /* Improve info/warning/error boxes */
        .stAlert {
            padding: 1rem;
            border-radius: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)


def show_footer():
    """Show application footer"""
    st.markdown("---")
    st.caption(
        "HTAP Configuration Editor | "
        "Built with Streamlit | "
        "[Documentation](https://github.com/NRCan-IETS-CE-O-HBC/HTAP)"
    )
```

---

## Acceptance Criteria

✅ **Error handler utility created** with custom exceptions
✅ **Loading states** shown for all async operations
✅ **User-friendly error messages** replace technical errors
✅ **Input validation** prevents invalid data entry
✅ **Help text** available for all major features
✅ **File operations** check permissions and existence
✅ **UI polish** applied (spacing, styles, icons)
✅ **Progress indicators** shown for long operations

---

## Testing Checklist

```bash
# Test error scenarios:
# 1. Try loading with missing HTAP files
# 2. Try exporting with invalid filename
# 3. Select archetypes that don't exist
# 4. Try operations with no data loaded
# 5. Verify loading spinners appear
# 6. Check help text displays correctly
# 7. Test with slow network/disk
```

---

## Common Issues & Solutions

### Issue: Errors not being caught
**Solution:** Ensure @handle_errors decorator is applied to all public functions

### Issue: Loading states not showing
**Solution:** Use `with st.spinner()` context manager, ensure it wraps the operation

### Issue: Help text not displaying
**Solution:** Check that help key exists in HELP_TEXT dictionary

---

## Edge Cases to Handle

1. **Empty configuration**: Gracefully handle no selections
2. **Missing files**: Check file existence before loading
3. **Invalid JSON**: Handle malformed data files
4. **Large selections**: Warn about >100 combinations
5. **Duplicate selections**: Prevent same option selected twice
6. **Network issues**: Handle file access errors
7. **Memory limits**: Handle large result sets

---

## User Experience Improvements

1. **Clear feedback**: Every action has visual feedback
2. **Progress indicators**: Long operations show progress
3. **Help everywhere**: Tooltips and help text throughout
4. **Undo/reset**: Easy to reset configuration
5. **Keyboard shortcuts**: Common actions accessible via keyboard
6. **Mobile-friendly**: Responsive design (though not primary target)

---

## Next Steps

After completing this task:
1. Test all error scenarios
2. Verify loading states appear correctly
3. Review help text for clarity
4. Proceed to **Task 3.5: Testing & Documentation**

---

## Time Tracking

- Error handler utility: 45 min
- Loading states: 45 min
- Help text & tooltips: 30 min
- Input validation: 30 min
- App updates: 30 min
- UI polish: 30 min
- **Total: ~3 hours**
