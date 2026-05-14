"""
Export widget for generating and downloading .run files
"""

import streamlit as st
from pathlib import Path
from typing import Dict, Set, Any
from src.utils.run_file_generator import RunFileGenerator, RunFileTemplate
from src.utils.export_validator import ExportValidator, ExportReadiness
from src.utils.validator import ValidationSeverity
from src.ui.state_manager import get_total_combinations


def render_export_widget():
    """Render the export widget in the right panel"""

    st.subheader("📤 Export Configuration")

    # Get state
    run_config = st.session_state.get('run_config', {})
    selected_options = st.session_state.get('selected_options', {})

    # Initialize export validator if not exists
    if 'export_validator' not in st.session_state:
        if 'options_db' in st.session_state and 'validator' in st.session_state:
            st.session_state.export_validator = ExportValidator(
                st.session_state.options_db,
                st.session_state.validator
            )
        else:
            st.error("❌ Export validator not initialized. Please reload the application.")
            return

    # Check export readiness
    export_validator = st.session_state.export_validator
    readiness, validation_messages = export_validator.check_export_readiness(
        run_config,
        selected_options
    )

    # Import help content and validators
    from src.ui.help_content import show_help_button
    from src.ui.input_validators import validate_filename

    # Display readiness status
    if readiness == ExportReadiness.READY:
        st.success("✅ Configuration is ready to export")
    elif readiness == ExportReadiness.WARNINGS:
        st.warning("⚠️ Configuration has warnings but can be exported")
    else:
        st.error("❌ Configuration has errors and cannot be exported")

    # Show validation details in expander (auto-expand if blocked)
    col1, col2 = st.columns([5, 1])
    with col2:
        show_help_button("export_validation")

    with st.expander("📋 Validation Details", expanded=(readiness == ExportReadiness.BLOCKED)):
        # Separate by severity
        errors = [m for m in validation_messages if m.severity == ValidationSeverity.ERROR]
        warnings = [m for m in validation_messages if m.severity == ValidationSeverity.WARNING]
        infos = [m for m in validation_messages if m.severity == ValidationSeverity.INFO]

        if errors:
            st.markdown("**Errors (must fix to export):**")
            for msg in errors:
                st.error(f"• {msg.message}")

        if warnings:
            st.markdown("**Warnings (can export with caution):**")
            for msg in warnings:
                st.warning(f"• {msg.message}")

        if infos:
            st.markdown("**Information:**")
            for msg in infos:
                st.info(f"• {msg.message}")

        if not errors and not warnings and not infos:
            st.success("✅ No validation issues found")

    st.markdown("---")

    # Configuration Summary
    with st.expander("📊 Configuration Summary", expanded=True):
        _render_configuration_summary(run_config, selected_options)

    st.markdown("---")

    # Template selector
    st.subheader("📋 Template")

    template_options = ["Custom"] + [
        f"{name} - {RunFileTemplate.get_template(name)['name']}"
        for name in RunFileTemplate.get_template_names()
    ]

    selected_template_display = st.selectbox(
        "Choose a template",
        template_options,
        help="Templates provide pre-configured run parameters for common scenarios"
    )

    # Parse template selection
    if selected_template_display == "Custom":
        selected_template = None
        template_data = None
    else:
        # Extract template key from display string
        template_key = selected_template_display.split(" - ")[0]
        selected_template = template_key
        template_data = RunFileTemplate.get_template(template_key)

        if template_data:
            st.info(f"📝 {template_data['description']}")
            st.caption(f"💡 {template_data['example_note']}")

    # Advanced parameters
    with st.expander("⚙️ Advanced Parameters", expanded=False):
        custom_params = _render_advanced_parameters(template_data)

    st.markdown("---")

    # Generate run file
    generator = RunFileGenerator()

    try:
        run_file_content = generator.generate_run_file(
            run_config,
            selected_options,
            custom_params
        )

        # Validate
        is_valid, errors = generator.validate_format(run_file_content)

        # Preview
        st.subheader("👁️ Preview")

        with st.expander("📄 View Generated .run File", expanded=False):
            st.code(run_file_content, language='text')

        # Validation status
        if is_valid:
            st.success("✅ Run file format is valid")
        else:
            st.error("❌ Run file validation failed")
            for error in errors:
                st.error(f"  • {error}")

        st.markdown("---")

        # Export controls
        st.subheader("💾 Export")

        # Filename
        default_filename = _generate_default_filename(run_config)
        filename = st.text_input(
            "Filename",
            value=default_filename,
            help="Name for the .run file (with or without extension)"
        )

        # Validate filename
        filename_valid = True
        if filename:
            is_valid, error_msg = validate_filename(filename)
            if not is_valid:
                st.error(f"❌ Invalid filename: {error_msg}")
                filename_valid = False

        # Ensure .run extension
        if not filename.endswith('.run'):
            filename = filename + '.run'

        col1, col2 = st.columns(2)

        # Determine if export should be blocked
        export_disabled = readiness == ExportReadiness.BLOCKED or not is_valid or not filename_valid

        with col1:
            # Download button
            help_text = "Download the run file to your computer"
            if export_disabled:
                if readiness == ExportReadiness.BLOCKED:
                    help_text = "Export blocked: Fix validation errors in the Validation Details section above"
                elif not is_valid:
                    help_text = "Export blocked: Run file format validation failed"

            st.download_button(
                label="⬇️ Download .run File",
                data=run_file_content,
                file_name=filename,
                mime="text/plain",
                use_container_width=True,
                disabled=export_disabled,
                help=help_text
            )

        with col2:
            # Save to C:/HTAP button
            save_help_text = "Save directly to C:/HTAP directory"
            if export_disabled:
                if readiness == ExportReadiness.BLOCKED:
                    save_help_text = "Export blocked: Fix validation errors first"
                elif not is_valid:
                    save_help_text = "Export blocked: Run file format validation failed"

            if st.button(
                "💾 Save to C:/HTAP",
                use_container_width=True,
                disabled=export_disabled,
                help=save_help_text
            ):
                try:
                    output_path = Path("C:/HTAP") / filename
                    generator.save_to_file(run_file_content, str(output_path))
                    st.success(f"✅ Saved to {output_path}")
                except Exception as e:
                    st.error(f"❌ Failed to save: {e}")

        # Show warnings for large runs
        total_combos = get_total_combinations()
        if total_combos > 500:
            st.error(
                f"⚠️ **Warning:** This configuration will generate **{total_combos}** simulation runs. "
                "This may take hours to complete and could be impractical."
            )
        elif total_combos > 100:
            st.warning(
                f"⚠️ **Note:** This configuration will generate **{total_combos}** simulation runs. "
                "This may take significant time to complete."
            )
        else:
            st.info(f"ℹ️ This configuration will generate **{total_combos}** simulation run(s).")

    except Exception as e:
        st.error(f"❌ Error generating run file: {e}")
        import traceback
        with st.expander("🐛 Debug Info"):
            st.code(traceback.format_exc())


def _render_configuration_summary(run_config: Dict[str, Any], selected_options: Dict[str, Set[str]]):
    """Render summary of current configuration"""

    col1, col2 = st.columns(2)

    with col1:
        # Archetypes
        archetypes = run_config.get('archetypes', [])
        st.metric("Archetypes", len(archetypes) if archetypes else 0)

        if archetypes:
            with st.expander("📁 Archetype Files"):
                for arch in archetypes:
                    st.write(f"• {arch}")

    with col2:
        # Options
        st.metric("Option Categories", len(selected_options))

        total_choices = sum(len(choices) for choices in selected_options.values())
        st.metric("Total Choices", total_choices)

    # Location and ruleset
    col3, col4 = st.columns(2)
    with col3:
        location = run_config.get('location', 'NA')
        st.caption(f"📍 **Location:** {location}")

    with col4:
        ruleset = run_config.get('ruleset', 'as-found')
        st.caption(f"📏 **Ruleset:** {ruleset}")

    # Total combinations
    total_combos = get_total_combinations()
    st.metric("Total Simulation Runs", total_combos)


def _render_advanced_parameters(template_data: Dict[str, Any] | None) -> Dict[str, str]:
    """
    Render advanced parameters controls

    Args:
        template_data: Template data if a template is selected

    Returns:
        Dict of custom parameters
    """
    custom_params = {}

    # Run mode
    run_mode_options = ['mesh', 'parametric', 'sample']

    # Default from template or default
    if template_data and 'run_mode' in template_data:
        default_mode_idx = run_mode_options.index(template_data['run_mode'])
    else:
        default_mode_idx = 0  # mesh

    run_mode = st.selectbox(
        "Run Mode",
        run_mode_options,
        index=default_mode_idx,
        help="mesh: All combinations | parametric: Systematic variation | sample: Random sampling"
    )
    custom_params['run-mode'] = run_mode

    # Directories
    archetype_dir = st.text_input(
        "Archetype Directory",
        value="C:/HTAP/archetypes",
        help="Directory containing archetype .h2k files"
    )
    custom_params['archetype-dir'] = archetype_dir

    options_file = st.text_input(
        "Options File",
        value="C:/HTAP/HTAP-options.json",
        help="Path to HTAP options definition file"
    )
    custom_params['options-file'] = options_file

    unit_costs_db = st.text_input(
        "Unit Costs Database",
        value="C:/HTAP/HTAPUnitCosts.json",
        help="Path to unit costs database"
    )
    custom_params['unit-costs-db'] = unit_costs_db

    output_folder = st.text_input(
        "Output Folder",
        value="./output",
        help="Directory for simulation outputs"
    )
    custom_params['output-folder'] = output_folder

    # Apply template custom params if available
    if template_data and 'custom_params' in template_data:
        custom_params.update(template_data['custom_params'])

    return custom_params


def _generate_default_filename(run_config: Dict[str, Any]) -> str:
    """
    Generate a default filename based on configuration

    Args:
        run_config: Run configuration dict

    Returns:
        Default filename
    """
    from datetime import datetime

    # Use location if available
    location = run_config.get('location')
    if location and location != 'NA':
        base_name = location.lower().replace(' ', '_')
    else:
        base_name = "htap_run"

    # Add timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    return f"{base_name}_{timestamp}.run"
