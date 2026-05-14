"""
Main layout for HTAP Configuration Editor using sidebar + two-column design
"""

import streamlit as st
from src.ui.left_panel import render_left_panel
from src.ui.middle_panel import render_middle_panel
from src.ui.right_panel import render_right_panel
from src.ui.state_manager import initialize_session_state


def render_main_layout() -> None:
    """Render the main layout using sidebar + two-column structure for better UX"""

    # Initialize state
    initialize_session_state()

    # Page header
    st.title("🏠 HTAP Configuration Editor")
    st.markdown("Build and export HTAP run configurations with visual cost tracking")
    st.markdown("---")

    # SIDEBAR: Run Configuration, Status, Export
    with st.sidebar:
        st.header("⚙️ Configuration")
        render_left_panel()

    _render_status_bar()

    # MAIN AREA: Two columns for Browse + Selection Cart
    col_browse, col_cart = st.columns([1.5, 1], gap="medium")

    with col_browse:
        st.header("🔍 Browse & Select Options")
        render_middle_panel()

    with col_cart:
        st.header("📦 Selection & Details")
        render_right_panel()


def _render_status_bar() -> None:
    """Display a compact validation summary strip below the header."""
    summary = st.session_state.get("validation_summary")

    with st.container():
        if not summary:
            st.info("Ready to configure your run. Start by picking archetypes and a location.")
            return

        cols = st.columns([2, 1, 1, 1])

        with cols[0]:
            st.markdown(f"**Run Overview**  \n{summary.get('description', 'No configuration yet.')}")

        with cols[1]:
            st.metric("Errors", summary["errors"], delta=None, delta_color="inverse")

        with cols[2]:
            st.metric("Warnings", summary["warnings"])

        with cols[3]:
            st.metric("Ready To Export", "Yes" if summary.get("ready") else "No")


def show_help_dialog() -> None:
    """Show help dialog"""
    with st.expander("📖 Help & Instructions", expanded=True):
        st.markdown("""
        ### How to Use This Tool

        **SIDEBAR** - Configuration
        - Select archetypes, location, and ruleset
        - Set cost database source
        - View validation status
        - Export when ready

        **LEFT Column** - Browse & Select
        - Search and filter options by category
        - Browse available options
        - Add options to your configuration

        **RIGHT Column** - Selection Cart
        - View selected options
        - See cost breakdown
        - Review validation messages
        - View option details

        **Workflow**: Configure → Browse → Select → Review → Export
        """)
