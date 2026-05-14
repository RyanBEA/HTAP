"""
HTAP Configuration Editor
Main Streamlit application
"""

import streamlit as st
import traceback
from src.ui.layout import render_main_layout
from src.ui.state_manager import initialize_session_state
from src.ui.loading_states import initialize_app_with_loading
from src.ui.styles import apply_custom_styles, show_footer
from src.utils.error_handler import handle_errors


# Page configuration
st.set_page_config(
    page_title="HTAP Configuration Editor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@handle_errors("Failed to initialize application", show_details=True)
def main():
    """Main application entry point with error handling"""

    # Apply custom styles
    apply_custom_styles()

    # Initialize session state
    initialize_session_state()

    # Initialize app components with loading states
    try:
        success = initialize_app_with_loading()
        if not success:
            st.error("❌ Application initialization failed")
            st.stop()
    except Exception as e:
        st.error(f"❌ Critical error during initialization: {str(e)}")
        st.info(
            "**The application cannot start due to initialization errors.**\n\n"
            "Please check:\n"
            "- HTAP is installed at C:/HTAP/\n"
            "- Required data files exist (HTAP-options.json, HTAPUnitCosts.json)\n"
            "- You have read permissions for HTAP files"
        )
        with st.expander("🔍 Technical Details"):
            st.code(traceback.format_exc())
        st.stop()

    # Render main layout with error handling
    try:
        render_main_layout()
    except Exception as e:
        st.error("❌ Error rendering user interface")
        st.warning(
            "An unexpected error occurred while rendering the UI. "
            "Please try refreshing the page."
        )
        with st.expander("🔍 Technical Details"):
            st.code(f"Error: {str(e)}\n\n{traceback.format_exc()}")

    # Show footer
    show_footer()


# Run main application
if __name__ == "__main__":
    main()
