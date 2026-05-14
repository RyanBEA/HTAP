"""
Sidebar panel: Run configuration, status, and export
"""

import streamlit as st
from typing import Dict, List, Tuple
from src.ui.state_manager import (
    initialize_session_state,
    clear_all_selections
)
from src.utils import load_options, HTAPConfigValidator, ValidationSeverity
from src.utils.run_file_generator import RunFileGenerator


def render_left_panel():
    """Render the sidebar panel with run configuration, status, and export."""

    initialize_session_state()

    run_config = st.session_state.run_config
    selected_options = st.session_state.get("selected_options", {})

    _ensure_validator()

    st.subheader("📋 Run Scope")
    from src.ui.help_content import show_help_button
    from src.ui.input_validators import validate_archetype_list

    archetypes = st.multiselect(
        "Archetypes",
        options=_get_archetypes(),
        default=run_config.get("archetypes", []),
        key="archetypes_select",
        help="Select archetype .h2k files"
    )
    st.session_state.run_config["archetypes"] = archetypes
    show_help_button("archetypes")

    if archetypes:
        is_valid, error_msg = validate_archetype_list(archetypes)
        if not is_valid:
            st.error(f"❌ {error_msg}")

    location = st.selectbox(
        "Location",
        options=_get_locations(),
        index=0 if not run_config.get("location") else None,
        key="location_select"
    )
    st.session_state.run_config["location"] = location
    show_help_button("location")

    ruleset = st.selectbox(
        "Ruleset",
        options=["as-found", "NBC-9.36", "BC-Step-3"],
        index=0,
        key="ruleset_select"
    )
    st.session_state.run_config["ruleset"] = ruleset
    show_help_button("ruleset")

    st.markdown("---")

    st.subheader("💰 Cost Source")
    show_help_button("cost_source")

    available_sources = _get_cost_sources()
    current_source = run_config.get("cost_source", available_sources[0])
    if current_source not in available_sources:
        current_source = available_sources[0]

    selected_source = st.selectbox(
        "Select source",
        options=available_sources,
        index=available_sources.index(current_source),
        help="Cost source for calculating option costs",
        key="cost_source_select",
        label_visibility="collapsed"
    )
    st.session_state.run_config["cost_source"] = selected_source

    if "cost_resolver" in st.session_state:
        component_count = st.session_state.cost_resolver.get_source_component_count(selected_source)
        st.caption(f"📊 {component_count} components available")

    st.markdown("---")

    validator = st.session_state.get("validator")
    validation_view = _render_validation_summary(validator, run_config, selected_options, selected_source)
    st.session_state.validation_summary = validation_view

    st.markdown("---")
    _render_actions_section(validation_view, selected_options)


def _ensure_validator() -> None:
    """Lazy-load the validator once options are available."""
    if "validator" in st.session_state:
        return

    if "options_db" in st.session_state:
        st.session_state.validator = HTAPConfigValidator(
            st.session_state.options_db,
            st.session_state.get("cost_resolver")
        )


def _render_validation_summary(
    validator: HTAPConfigValidator,
    run_config: Dict,
    selected_options: Dict,
    cost_source: str
) -> Dict:
    """Render validation summary and return structured data for status bar."""
    if not validator:
        st.info("Validation will appear once data files load successfully.")
        return {
            "errors": 0,
            "warnings": 0,
            "infos": 0,
            "ready": False,
            "description": "Waiting for data files.",
            "messages": []
        }

    run_messages = validator.validate_run_config(run_config)
    option_messages = validator.validate_selected_options(selected_options, cost_source=cost_source)
    all_messages = run_messages + option_messages

    errors = sum(1 for msg in all_messages if msg.severity == ValidationSeverity.ERROR)
    warnings = sum(1 for msg in all_messages if msg.severity == ValidationSeverity.WARNING)
    infos = sum(1 for msg in all_messages if msg.severity == ValidationSeverity.INFO)

    description = _summarize_run(run_config, selected_options)

    cols = st.columns(3)
    with cols[0]:
        st.metric("Errors", errors, delta=None, delta_color="inverse")
    with cols[1]:
        st.metric("Warnings", warnings)
    with cols[2]:
        st.metric("Information", infos)

    if all_messages:
        with st.expander("📋 Validation details", expanded=errors > 0):
            for msg in all_messages:
                if msg.severity == ValidationSeverity.ERROR:
                    st.error(f"❌ {msg.message}")
                elif msg.severity == ValidationSeverity.WARNING:
                    st.warning(f"⚠️ {msg.message}")
                else:
                    st.info(f"ℹ️ {msg.message}")
    else:
        st.success("Configuration looks good.")

    ready = errors == 0 and bool(run_config.get("archetypes")) and bool(run_config.get("location"))

    return {
        "errors": errors,
        "warnings": warnings,
        "infos": infos,
        "ready": ready and bool(selected_options),
        "description": description,
        "messages": all_messages,
        "run_config": run_config,
        "selected_options": selected_options,
        "cost_source": cost_source
    }


def _render_actions_section(validation_view: Dict, selected_options: Dict) -> None:
    """Show reset and export controls."""
    st.subheader("📤 Review & Export")

    options_count = sum(len(v) for v in selected_options.values())
    st.caption(f"{options_count} option{'s' if options_count != 1 else ''} selected across {len(selected_options)} categories.")

    cols = st.columns([1, 1])
    with cols[0]:
        if st.button("🔄 Reset all selections", use_container_width=True):
            clear_all_selections()
            st.success("Selections cleared.")

    export_ready, blocker_reason = _export_state(validation_view, selected_options)

    with st.expander("🔎 Review summary", expanded=not export_ready):
        _render_review_summary(validation_view, selected_options, blocker_reason)

    filename_default = st.text_input(
        "File name",
        value=st.session_state.get("export_filename", "htap-config.run"),
        help="Provide a descriptive filename. .run extension is added automatically if omitted."
    )
    st.session_state.export_filename = filename_default

    if export_ready:
        content = _generate_run_file(validation_view, filename_default)
        st.download_button(
            "📦 Download .run file",
            data=content.encode("utf-8"),
            file_name=_ensure_run_extension(filename_default),
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.button(
            "📦 Download .run file",
            disabled=True,
            use_container_width=True,
            help="Complete the required items above before exporting."
        )


def _render_review_summary(validation_view: Dict, selected_options: Dict, blocker_reason: str) -> None:
    """Detailed summary shown before export."""
    run_config = validation_view.get("run_config", {})

    st.markdown("**Configuration snapshot**")
    st.markdown(
        f"- Archetypes: `{', '.join(run_config.get('archetypes', []) or ['None'])}`\n"
        f"- Location: `{run_config.get('location') or 'None'}`\n"
        f"- Ruleset: `{run_config.get('ruleset') or 'None'}`\n"
        f"- Cost source: `{run_config.get('cost_source') or 'None'}`\n"
    )

    if selected_options:
        st.markdown("**Selected options**")
        for category, choices in sorted(selected_options.items()):
            readable = category.replace("Opt-", "")
            st.write(f"- **{readable}**: {', '.join(sorted(choices))}")
    else:
        st.info("No options selected yet.")

    if blocker_reason:
        st.warning(blocker_reason)


def _generate_run_file(validation_view: Dict, filename: str) -> str:
    """Generate .run file contents using the current configuration."""
    generator = st.session_state.get("run_file_generator")
    if not generator:
        generator = RunFileGenerator()
        st.session_state.run_file_generator = generator

    content = generator.generate_run_file(
        validation_view.get("run_config", {}),
        validation_view.get("selected_options", {}),
        custom_params=None
    )

    header = [
        "! Review summary",
        f"! Exported as: {_ensure_run_extension(filename)}",
        f"! Archetypes: {', '.join(validation_view.get('run_config', {}).get('archetypes', []) or ['None'])}",
        f"! Location: {validation_view.get('run_config', {}).get('location') or 'None'}",
        f"! Ruleset: {validation_view.get('run_config', {}).get('ruleset') or 'None'}",
        ""
    ]

    return "\n".join(header) + content


def _ensure_run_extension(filename: str) -> str:
    """Add .run extension when missing."""
    filename = filename.strip() or "htap-config.run"
    return filename if filename.lower().endswith(".run") else f"{filename}.run"


def _export_state(validation_view: Dict, selected_options: Dict) -> Tuple[bool, str]:
    """Determine if export is allowed and provide blocker message."""
    if not validation_view.get("ready"):
        return False, "Resolve validation errors and ensure mandatory fields are filled."

    if not selected_options:
        return False, "Select at least one option before exporting."

    return True, ""


def _summarize_run(run_config: Dict, selected_options: Dict) -> str:
    """Create a short sentence summarizing the run configuration."""
    archetypes = len(run_config.get("archetypes") or [])
    categories = len(selected_options.keys())
    location = run_config.get("location") or "no location"
    return f"{archetypes} archetype(s), {categories} category selections, targeting {location}."


def _get_cost_sources() -> List[str]:
    """Return available cost sources."""
    if "cost_resolver" in st.session_state:
        sources = st.session_state.cost_resolver.get_available_sources()
        return sources or ["LEEP-ON-Ottawa"]
    return ["LEEP-ON-Ottawa"]


def _get_archetypes() -> List[str]:
    """Get available archetypes."""
    # TODO: Replace with dynamic discovery.
    return ["AB-base.h2k", "BC-base.h2k", "ON-base.h2k"]


def _get_locations() -> List[str]:
    """Get available locations from options file."""
    try:
        options_db = load_options("C:/HTAP/HTAP-options.json")
        loc_category = options_db.get_category("Opt-Location")
        if loc_category:
            return sorted(loc_category.list_choices())
    except Exception:
        pass
    return ["Vancouver-BC", "Toronto-ON", "Calgary-AB"]
