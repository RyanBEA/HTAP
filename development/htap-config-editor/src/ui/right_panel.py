"""
Right panel: Selection cart and option details
"""

import streamlit as st
from src.ui.state_manager import (
    initialize_session_state,
    get_total_combinations,
    is_choice_selected,
    remove_option_selection,
    add_option_selection
)


def render_right_panel():
    """Render the selection cart and option details"""

    initialize_session_state()

    # SELECTION CART - Always visible at top
    st.subheader("📦 Selection Cart")

    selected_options = st.session_state.get('selected_options', {})
    total_options = sum(len(v) for v in selected_options.values())

    if total_options == 0:
        st.caption("No options selected yet. Use the Browse tab to add upgrades.")
    else:
        total_combos = get_total_combinations()
        metrics = st.columns(2)
        with metrics[0]:
            st.metric("Options", total_options)
        with metrics[1]:
            st.metric("Total runs", total_combos)

        if total_combos > 500:
            st.error(f"{total_combos} runs may be too many for a single batch.")
        elif total_combos > 100:
            st.warning(f"{total_combos} runs will require extra processing time.")

        st.caption("Selections")
        for category in sorted(selected_options.keys()):
            choices = selected_options[category]
            if not choices:
                continue

            readable = category.replace('Opt-', '')
            st.markdown(f"**{readable}**")

            for choice in sorted(choices):
                row_cols = st.columns([6, 1])
                with row_cols[0]:
                    st.caption(choice)
                with row_cols[1]:
                    if st.button("Remove", key=f"remove_cart_{category}_{choice}"):
                        remove_option_selection(category, choice)

    st.markdown("---")

    # VALIDATION SUMMARY - reference status bar and sidebar
    st.subheader("✓ Validation quick view")
    summary = st.session_state.get("validation_summary")
    if not summary:
        st.caption("Validation results will appear once configuration data is available.")
    else:
        if summary["errors"]:
            st.error(f"{summary['errors']} error(s) remain. See the sidebar for details.")
        elif summary["warnings"]:
            st.warning(f"{summary['warnings']} warning(s) to review before exporting.")
        else:
            st.success("No blocking issues detected.")
        st.caption("Full validation breakdown is shown in the sidebar review panel.")

    st.markdown("---")

    # COST SUMMARY - Compact
    if total_options > 0:
        st.subheader("💰 Costs")
        from src.ui.cost_summary_widget import render_cost_summary
        with st.container():
            render_cost_summary()

        st.markdown("---")

    # OPTION DETAILS - When option is clicked
    st.subheader("💡 Option Details")

    selected = st.session_state.selected_option_detail

    if not selected:
        st.caption("Select an option to see its details here.")
        return

    # Option header
    st.markdown(f"### {selected['name']}")
    st.caption(f"📁 {selected['category'].replace('Opt-', '')}")

    choice = selected['choice_obj']
    category = selected['category_obj']

    # Tags
    if choice.tags:
        tag_line = "  ".join(f"`{tag}`" for tag in choice.tags)
        st.caption(tag_line)

    # Description
    if choice.description:
        st.write(choice.description)

    cost_source = st.session_state.run_config.get('cost_source', 'LEEP-ON-Ottawa')
    cost_resolver = st.session_state.get('cost_resolver')
    total_cost = 0.0
    cost_details = []
    if cost_resolver and choice.costs:
        total_cost, cost_details = cost_resolver.resolve_option_cost(choice, cost_source)

    if total_cost > 0:
        st.metric("Estimated cost", f"${total_cost:,.0f}")

    # Cost components
    if cost_details:
        with st.expander("💰 Cost components", expanded=False):
            _render_cost_table(cost_details)
    elif choice.cost_proxy:
        st.caption(f"Uses cost proxy: {choice.cost_proxy}")

    # H2K Mappings
    if choice.h2k_map:
        with st.expander("🔧 HOT2000 XML Mappings", expanded=False):
            st.json(choice.h2k_map)

    st.markdown("---")

    # Add to run button
    already_selected = is_choice_selected(selected['category'], selected['name'])

    button_col1, button_col2 = st.columns(2)

    with button_col1:
        if st.button(
            "Add to cart" if not already_selected else "Update cart",
            use_container_width=True,
            type="primary"
        ):
            add_option_selection(selected['category'], selected['name'])
            st.success("Option added to cart.")

    with button_col2:
        if already_selected:
            if st.button("Remove from cart", use_container_width=True):
                remove_option_selection(selected['category'], selected['name'])
        else:
            st.caption("Not currently selected.")


def _render_cost_table(cost_details):
    """Render cost components in a compact table."""
    try:
        import pandas as pd
    except ImportError:
        pd = None

    if not pd:
        for component in cost_details:
            st.write(
                f"{component['component_id']}: ${component['total_cost']:,.2f} "
                f"({component['source_used']})"
            )
        return

    df = pd.DataFrame(cost_details)
    if df.empty:
        st.info("No component details available.")
        return

    display_cols = [
        "component_id",
        "description",
        "quantity",
        "unit_cost_total",
        "total_cost",
        "source_used"
    ]
    for col in display_cols:
        if col not in df.columns:
            df[col] = None

    df = df[display_cols]
    df.rename(columns={
        "component_id": "Component",
        "description": "Description",
        "quantity": "Qty",
        "unit_cost_total": "Unit cost",
        "total_cost": "Total cost",
        "source_used": "Source"
    }, inplace=True)

    df["Unit cost"] = df["Unit cost"].apply(lambda x: f"${x:,.2f}" if isinstance(x, (int, float)) else x)
    df["Total cost"] = df["Total cost"].apply(lambda x: f"${x:,.2f}" if isinstance(x, (int, float)) else x)

    st.dataframe(df, use_container_width=True, hide_index=True)
