"""
Validation report widget for displaying detailed validation reports
"""

import streamlit as st
from datetime import datetime


def render_validation_report():
    """
    Render validation report widget

    Generates and displays a comprehensive markdown validation report
    that can be downloaded for documentation purposes.
    """
    st.subheader("📋 Validation Report")

    # Get state
    run_config = st.session_state.get('run_config', {})
    selected_options = st.session_state.get('selected_options', {})

    # Get export validator
    export_validator = st.session_state.get('export_validator')
    if not export_validator:
        st.error("❌ Export validator not initialized. Please reload the application.")
        return

    # Generate report button
    if st.button("📊 Generate Validation Report", use_container_width=True):
        st.session_state.show_validation_report = True

    # Display report if generated
    if st.session_state.get('show_validation_report', False):
        with st.spinner("Generating validation report..."):
            report_content = export_validator.generate_validation_report(
                run_config,
                selected_options
            )

        st.markdown("---")

        # Display report
        st.markdown(report_content)

        st.markdown("---")

        # Download button for report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"htap_validation_report_{timestamp}.md"

        st.download_button(
            label="⬇️ Download Report",
            data=report_content,
            file_name=report_filename,
            mime="text/markdown",
            use_container_width=True,
            help="Download validation report as markdown file"
        )

        # Close button
        if st.button("✖️ Close Report", use_container_width=True):
            st.session_state.show_validation_report = False
            st.rerun()
