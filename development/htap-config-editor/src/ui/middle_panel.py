"""
Middle panel: Options browser with category filtering and advanced search
"""

import streamlit as st
from src.ui.help_content import show_help_button
from src.ui.state_manager import (
    initialize_session_state,
    set_option_detail,
    toggle_selection_mode,
    get_selected_choices,
    clear_category_selections
)
from src.utils import load_options, OptionsSearch, ValidationSeverity


def render_middle_panel():
    """Render the middle panel with browse and search tabs"""

    initialize_session_state()

    mode_cols = st.columns([3, 1])
    with mode_cols[0]:
        st.subheader("Selection Mode")
        previous_mode = st.session_state.get('multi_select_mode', False)
        multi_mode = st.toggle(
            "Enable parametric multi-select",
            value=previous_mode,
            help="Turn on to pick multiple options per category for parametric studies.",
            key="selection_mode_toggle"
        )
        if multi_mode != previous_mode:
            toggle_selection_mode()
    with mode_cols[1]:
        show_help_button("multi_select")

    if multi_mode:
        st.caption("Multi-select: combinations expand quickly. Keep an eye on total runs.")
    else:
        st.caption("Single-select: pick one option per category for a baseline configuration.")

    st.markdown("---")

    # Load options database
    try:
        if 'options_db' not in st.session_state:
            options_db = load_options("C:/HTAP/HTAP-options.json")
            st.session_state.options_db = options_db
    except Exception as e:
        st.error(f"Failed to load options database: {e}")
        st.info("👈 Make sure HTAP-options.json is available at C:/HTAP/")
        return

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📂 Browse", "🔍 Search", "📊 Statistics"])

    with tab1:
        # Existing category browser
        render_category_browser()

    with tab2:
        # New search interface
        from src.ui.search_widget import render_search_widget, render_search_results

        results = render_search_widget()
        if results is not None:
            render_search_results(results, enable_selection=True)

    with tab3:
        # Category statistics and tag explorer
        from src.ui.search_widget import render_category_statistics, render_tag_explorer

        render_category_statistics()
        st.divider()
        render_tag_explorer()


def render_category_browser():
    """
    Category browsing interface with integrated filters
    """
    st.subheader("🔍 Browse Options")

    # Load data
    try:
        options_db = st.session_state.options_db
        search = OptionsSearch(options_db)
    except Exception as e:
        st.error(f"Failed to initialize search: {e}")
        return

    from src.ui.state_manager import set_category_filter

    categories = sorted([cat for cat in options_db.list_categories() if cat.startswith('Opt-')])
    category_groups = {
        "All": categories,
        "Envelope": [c for c in categories if any(k in c for k in ['Wall', 'Window', 'Ceiling', 'Foundation', 'Door', 'Slab', 'Floor'])],
        "Mechanical": [c for c in categories if any(k in c for k in ['Heating', 'DHW', 'Vent', 'PV'])],
        "Other": []
    }
    used = set(category_groups["Envelope"]) | set(category_groups["Mechanical"])
    category_groups["Other"] = [c for c in categories if c not in used]

    group_choice = st.radio(
        "Category group",
        options=list(category_groups.keys()),
        horizontal=True,
        key="category_group_choice"
    )

    filtered_categories = category_groups[group_choice] if group_choice != "All" else categories
    display_map = {"All categories": None}
    for cat in filtered_categories:
        display_map[cat.replace('Opt-', '')] = cat

    current_category = st.session_state.current_category
    default_label = next((label for label, cat in display_map.items() if cat == current_category), "All categories")

    selected_label = st.selectbox(
        "Focus category",
        options=list(display_map.keys()),
        index=list(display_map.keys()).index(default_label),
        help="Choose a category to narrow results.",
        key="category_select"
    )

    target_category = display_map[selected_label]
    if target_category != st.session_state.current_category:
        set_category_filter(target_category)

    search_query = st.text_input(
        "Search",
        value=st.session_state.search_query,
        placeholder="Search options, tags, descriptions...",
        key="search_input",
        label_visibility="collapsed"
    )
    st.session_state.search_query = search_query

    st.markdown("---")

    # Show active category filter with selection count
    if st.session_state.current_category:
        selected_in_category = get_selected_choices(st.session_state.current_category)

        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.caption(f"Filtering: {st.session_state.current_category.replace('Opt-', '')}")
        with col2:
            if selected_in_category:
                st.metric("Selected", len(selected_in_category), label_visibility="collapsed")
        with col3:
            if selected_in_category:
                if st.button("Clear selections", key="clear_category", use_container_width=True):
                    clear_category_selections(st.session_state.current_category)

    # Show selected options summary for current category
    if st.session_state.current_category:
        selected_in_category = get_selected_choices(st.session_state.current_category)
        if selected_in_category:
            with st.expander(f"📋 Selected in {st.session_state.current_category.replace('Opt-', '')}", expanded=False):
                for choice in sorted(selected_in_category):
                    st.markdown(f"- ✅ {choice}")

    # Build category filter
    category_filter = None
    if st.session_state.current_category:
        category_filter = [st.session_state.current_category]

    # Search with filters
    results_df = search.search(
        query=search_query,
        categories=category_filter,
        limit=100
    )

    st.subheader(f"Results ({len(results_df)})")

    if len(results_df) == 0:
        st.warning("No options found. Try adjusting your search or category filter.")
        return

    # Pagination
    items_per_page = 10
    total_pages = (len(results_df) - 1) // items_per_page + 1

    start_idx = st.session_state.current_page * items_per_page
    end_idx = start_idx + items_per_page
    page_results = results_df.iloc[start_idx:end_idx]

    for _, row in page_results.iterrows():
        _render_option_card(row)

    # Pagination controls
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("◀ Previous", disabled=(st.session_state.current_page == 0)):
                st.session_state.current_page -= 1

        with col2:
            st.caption(f"Page {st.session_state.current_page + 1} of {total_pages}")

        with col3:
            if st.button("Next ▶", disabled=(st.session_state.current_page >= total_pages - 1)):
                st.session_state.current_page += 1


def _render_option_card(row):
    """Render a single option as a card with cost information"""

    with st.container():
        cost_source = st.session_state.run_config.get('cost_source', 'LEEP-ON-Ottawa')
        cost_resolver = st.session_state.get('cost_resolver')
        validator = st.session_state.get('validator')

        total_cost = 0.0
        cost_details = []
        if cost_resolver and row['has_costs'] and row['choice_obj'].costs:
            total_cost, cost_details = cost_resolver.resolve_option_cost(
                row['choice_obj'],
                cost_source
            )

        from src.ui.state_manager import is_choice_selected, add_option_selection, remove_option_selection
        is_selected = is_choice_selected(row['category'], row['choice'])

        status_label = row['category'].replace('Opt-', '')
        header_cols = st.columns([4, 1])
        with header_cols[0]:
            st.markdown(f"### {row['choice']}")
            st.caption(f"Category · {status_label}")
        with header_cols[1]:
            if total_cost > 0:
                st.metric("Cost", f"${total_cost:,.0f}")
            elif row['has_costs']:
                st.caption("💰 Cost data available")

        if row['description']:
            st.write(row['description'])

        if row['tags']:
            tags = "  ".join(f"`{tag}`" for tag in row['tags'].split('|')[:5])
            st.caption(tags)

        if validator and is_selected:
            choice_messages = validator.validate_selected_options(
                {row['category']: row['choice']},
                cost_source
            )
            if choice_messages:
                warning_count = sum(1 for m in choice_messages if m.severity == ValidationSeverity.WARNING)
                error_count = sum(1 for m in choice_messages if m.severity == ValidationSeverity.ERROR)
                if error_count:
                    st.error(f"{error_count} validation error(s) for this choice.")
                elif warning_count:
                    st.warning(f"{warning_count} validation warning(s) for this choice.")

        action_cols = st.columns([1, 1, 1])
        with action_cols[0]:
            label = "Remove from selection" if is_selected else "Add to selection"
            if st.button(label, key=f"toggle_{row['category']}_{row['choice']}"):
                if is_selected:
                    remove_option_selection(row['category'], row['choice'])
                else:
                    add_option_selection(row['category'], row['choice'])
        with action_cols[1]:
            if st.button("View details →", key=f"view_{row['category']}_{row['choice']}"):
                set_option_detail({
                    'category': row['category'],
                    'name': row['choice'],
                    'choice_obj': row['choice_obj'],
                    'category_obj': row['category_obj']
                })
        with action_cols[2]:
            st.caption(f"Selected · {'Yes' if is_selected else 'No'}")

        if cost_resolver and cost_details:
            with st.expander("💰 Cost breakdown"):
                _render_cost_table(cost_details)

        st.divider()


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
