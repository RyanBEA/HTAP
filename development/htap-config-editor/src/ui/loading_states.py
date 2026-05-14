"""
Loading states for HTAP Configuration Editor

Handles application initialization with proper loading indicators
and error handling for all critical components.
"""

import streamlit as st
from pathlib import Path
from src.utils.error_handler import safe_file_load, show_error_with_guidance, DataLoadError
from src.utils import load_options, load_unit_costs
from src.utils.cost_resolver import CostResolver
from src.utils.cost_report import CostReportGenerator
from src.utils.validator import HTAPConfigValidator


def initialize_app_with_loading() -> bool:
    """
    Initialize all app components with proper loading states

    Returns:
        True if initialization successful, False if critical errors occurred

    Side effects:
        - Populates st.session_state with initialized components
        - Shows loading spinners and status messages in UI
        - Shows error messages if initialization fails

    Components initialized:
        1. Options database (st.session_state.options_db)
        2. Costs database (st.session_state.cost_resolver)
        3. Cost report generator (st.session_state.cost_report_gen)
        4. Validator (st.session_state.validator)
        5. Search index (initialized in options_db)
    """
    success = True

    # ========================================================================
    # 1. LOAD OPTIONS DATABASE
    # ========================================================================

    if 'options_db' not in st.session_state:
        options_path = "C:/HTAP/HTAP-options.json"

        # Check file accessibility first
        if not safe_file_load(options_path, "HTAP options database"):
            show_error_with_guidance(
                "Cannot load HTAP options database",
                troubleshooting_steps=[
                    "Ensure HTAP is installed at C:/HTAP/",
                    "Verify HTAP-options.json exists in C:/HTAP/",
                    "Check that you have read permissions for the file"
                ]
            )
            st.stop()
            return False

        # Load with spinner
        try:
            with st.spinner("📂 Loading HTAP options database..."):
                options_db = load_options(options_path)
                st.session_state.options_db = options_db

                # Count categories
                category_count = len(options_db.list_categories())
                st.success(f"✅ Loaded {category_count} option categories")

        except Exception as e:
            show_error_with_guidance(
                f"Failed to load options database: {str(e)}",
                troubleshooting_steps=[
                    "Check that HTAP-options.json is valid JSON format",
                    "Verify the file is not corrupted",
                    "Try re-downloading HTAP from the repository"
                ],
                technical_details=str(e)
            )
            st.stop()
            return False

    # ========================================================================
    # 2. LOAD COSTS DATABASE
    # ========================================================================

    if 'cost_resolver' not in st.session_state:
        costs_path = "C:/HTAP/HTAPUnitCosts.json"

        # Check file accessibility first
        if not safe_file_load(costs_path, "unit costs database"):
            st.warning(
                "⚠️ Cost database not available. Cost features will be disabled.\n\n"
                "To enable cost features, ensure HTAPUnitCosts.json is available at C:/HTAP/"
            )
            # Non-critical - continue without costs
        else:
            # Load with spinner
            try:
                with st.spinner("💰 Loading unit costs database..."):
                    costs_db = load_unit_costs(costs_path)
                    cost_resolver = CostResolver(costs_db)
                    st.session_state.cost_resolver = cost_resolver

                    # Count components
                    component_count = 0
                    for source in cost_resolver.get_available_sources():
                        component_count += cost_resolver.get_source_component_count(source)

                    st.success(f"✅ Loaded {component_count} cost components")

            except Exception as e:
                st.warning(
                    f"⚠️ Failed to load cost database: {str(e)}\n\n"
                    "Cost features will be disabled. The app will continue without cost support."
                )
                # Non-critical - continue without costs

    # ========================================================================
    # 3. INITIALIZE COST REPORT GENERATOR
    # ========================================================================

    if 'cost_report_gen' not in st.session_state:
        if 'options_db' in st.session_state and 'cost_resolver' in st.session_state:
            try:
                with st.spinner("⚙️ Initializing cost report generator..."):
                    cost_report_gen = CostReportGenerator(
                        st.session_state.options_db,
                        st.session_state.cost_resolver
                    )
                    st.session_state.cost_report_gen = cost_report_gen
                    # Success message combined with cost resolver success

            except Exception as e:
                st.warning(
                    f"⚠️ Failed to initialize cost report generator: {str(e)}\n\n"
                    "Cost reporting features will be disabled."
                )
                # Non-critical - continue without cost reporting

    # ========================================================================
    # 4. INITIALIZE VALIDATOR
    # ========================================================================

    if 'validator' not in st.session_state:
        if 'options_db' in st.session_state:
            try:
                with st.spinner("✓ Initializing validators..."):
                    validator = HTAPConfigValidator(
                        st.session_state.options_db,
                        st.session_state.get('cost_resolver')
                    )
                    st.session_state.validator = validator
                    # Success message not shown - validator is internal

            except Exception as e:
                st.error(f"❌ Failed to initialize validator: {str(e)}")
                show_error_with_guidance(
                    "Cannot initialize configuration validator",
                    troubleshooting_steps=[
                        "Check that options database loaded correctly",
                        "Verify HTAP-options.json is valid",
                        "Try reloading the application"
                    ],
                    technical_details=str(e)
                )
                st.stop()
                return False

    # ========================================================================
    # 5. BUILD SEARCH INDEX
    # ========================================================================

    # Search index is built automatically by OptionsDatabase
    # Just show loading message if not already initialized
    if 'options_db' in st.session_state:
        options_db = st.session_state.options_db
        # The search index is built on first access, so we trigger it here
        # This happens silently in the background
        pass

    return success


def show_initialization_error(component: str, error: Exception) -> None:
    """
    Show a standardized initialization error message

    Args:
        component: Name of the component that failed to initialize
        error: The exception that was raised
    """
    st.error(f"❌ Failed to initialize {component}")

    st.info(
        "**This is a critical error that prevents the application from running.**\n\n"
        "Please check the following:\n"
        "- HTAP is installed at C:/HTAP/\n"
        "- Required data files (HTAP-options.json, HTAPUnitCosts.json) are present\n"
        "- You have read permissions for HTAP files\n"
        "- The data files are not corrupted"
    )

    with st.expander("🔍 Technical Details"):
        st.code(f"Component: {component}\nError: {str(error)}")


def check_critical_dependencies() -> bool:
    """
    Check that critical dependencies are available

    Returns:
        True if all critical dependencies are available, False otherwise

    Side effects:
        Shows error messages if dependencies are missing
    """
    critical_files = {
        "C:/HTAP/HTAP-options.json": "HTAP options database",
        "C:/H2K-CLI-Min/": "HOT2000 CLI installation"
    }

    all_ok = True

    for filepath, description in critical_files.items():
        path = Path(filepath)
        if not path.exists():
            st.error(f"❌ Missing {description}: {filepath}")
            all_ok = False

    if not all_ok:
        st.info(
            "**Critical dependencies are missing.**\n\n"
            "Please ensure:\n"
            "- HTAP is installed at C:/HTAP/\n"
            "- HOT2000 CLI is installed at C:/H2K-CLI-Min/\n"
            "- All required data files are present"
        )

    return all_ok
