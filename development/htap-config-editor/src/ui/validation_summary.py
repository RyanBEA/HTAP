"""
Validation summary widget for RIGHT panel
"""

import streamlit as st
from src.utils.validator import ValidationSeverity


def render_validation_summary():
    """
    Render validation summary in RIGHT panel
    Shows overall configuration health
    """
    st.subheader("✓ Validation Summary")

    validator = st.session_state.get('validator')
    if not validator:
        st.info("Validation not available")
        return

    run_config = st.session_state.get('run_config', {})
    selected_options = st.session_state.get('selected_options', {})

    # Perform full validation
    validation_results = validator.validate_full_configuration(
        run_config,
        selected_options
    )

    # Count by severity
    all_messages = (
        validation_results['run_config'] +
        validation_results['options'] +
        validation_results['completeness'] +
        validation_results['summary']
    )

    error_count = sum(1 for msg in all_messages if msg.severity == ValidationSeverity.ERROR)
    warning_count = sum(1 for msg in all_messages if msg.severity == ValidationSeverity.WARNING)
    info_count = sum(1 for msg in all_messages if msg.severity == ValidationSeverity.INFO)

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Errors", error_count, delta=None if error_count == 0 else "Fix required")
    with col2:
        st.metric("Warnings", warning_count)
    with col3:
        st.metric("Info", info_count)

    # Overall status
    if error_count > 0:
        st.error("❌ Configuration has errors and cannot be exported")
    elif warning_count > 0:
        st.warning("⚠️ Configuration has warnings but can be exported")
    else:
        st.success("✅ Configuration is valid and ready to export")

    # Expandable details
    if all_messages:
        with st.expander("📋 Validation Details", expanded=error_count > 0):
            for section_name, messages in validation_results.items():
                if messages:
                    st.markdown(f"**{section_name.replace('_', ' ').title()}**")
                    for msg in messages:
                        if msg.severity == ValidationSeverity.ERROR:
                            st.error(msg.message)
                        elif msg.severity == ValidationSeverity.WARNING:
                            st.warning(msg.message)
                        else:
                            st.info(msg.message)
                    st.divider()
