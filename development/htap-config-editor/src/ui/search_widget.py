"""
Advanced search widget for HTAP options
"""

import streamlit as st
import pandas as pd
from typing import List, Optional

from src.utils.options_search import OptionsSearch


def render_search_widget() -> Optional[pd.DataFrame]:
    """
    Render advanced search widget in MIDDLE panel

    Returns:
        DataFrame of search results, or None if no search performed
    """
    st.subheader("🔍 Search Options")

    # Initialize search index
    if 'search_index' not in st.session_state:
        if 'options_db' in st.session_state:
            st.session_state.search_index = OptionsSearch(st.session_state.options_db)
        else:
            # Try to load options
            try:
                from src.utils import load_options
                options_db = load_options("C:/HTAP/HTAP-options.json")
                st.session_state.options_db = options_db
                st.session_state.search_index = OptionsSearch(options_db)
            except Exception as e:
                st.warning(f"Options database not loaded: {e}")
                return None

    search_index = st.session_state.search_index

    # Search input
    col1, col2 = st.columns([3, 1])

    with col1:
        search_query = st.text_input(
            "Search term",
            placeholder="e.g., 'window', 'low-e', 'R-40'...",
            key="search_query",
            help="Search in option names, tags, and descriptions"
        )

    with col2:
        search_limit = st.number_input(
            "Max results",
            min_value=10,
            max_value=500,
            value=50,
            step=10,
            key="search_limit"
        )

    # Advanced filters (expandable)
    with st.expander("🎛️ Advanced Filters", expanded=False):
        # Category filter
        all_categories = search_index.get_all_categories()
        selected_categories = st.multiselect(
            "Filter by categories",
            options=all_categories,
            default=None,
            help="Leave empty to search all categories"
        )

        # Tag filter
        col_a, col_b = st.columns(2)

        with col_a:
            # Cost filter
            cost_filter = st.radio(
                "Cost data",
                options=["Any", "With costs", "Without costs"],
                index=0,
                horizontal=True
            )

            cost_filter_value = None
            if cost_filter == "With costs":
                cost_filter_value = True
            elif cost_filter == "Without costs":
                cost_filter_value = False

        with col_b:
            # Structure filter
            structure_filter = st.radio(
                "Structure type",
                options=["Any", "Flat", "Tree"],
                index=0,
                horizontal=True
            )

            structure_value = None
            if structure_filter == "Flat":
                structure_value = "flat"
            elif structure_filter == "Tree":
                structure_value = "tree"

    # Perform search
    if search_query or selected_categories or cost_filter_value is not None or structure_value:
        results = search_index.search(
            query=search_query,
            categories=selected_categories if selected_categories else None,
            require_costs=cost_filter_value,
            structure=structure_value,
            limit=search_limit
        )

        # Display results count
        st.metric("Results Found", len(results))

        if len(results) > 0:
            return results
        else:
            st.info("No results found. Try adjusting your search criteria.")
            return None

    return None


def render_search_results(
    results: pd.DataFrame,
    enable_selection: bool = True
):
    """
    Render search results with selection buttons

    Args:
        results: DataFrame from search
        enable_selection: If True, show selection buttons
    """
    if results is None or len(results) == 0:
        return

    st.subheader(f"📋 Search Results ({len(results)} found)")

    # Import selection functions
    from src.ui.state_manager import (
        add_option_to_run,
        is_choice_selected
    )

    # Display results
    for idx, row in results.iterrows():
        category_name = row['category']
        choice_name = row['choice']
        description = row['description']
        has_costs = row['has_costs']
        structure = row['structure']
        tags = row['tags']

        # Result card
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                # Choice name
                st.markdown(f"**{choice_name}**")
                st.caption(f"Category: {category_name}")

                # Description
                if description:
                    st.caption(f"_{description}_")

                # Tags
                if tags:
                    tag_list = tags.split('|')
                    tags_display = " • ".join([f"`{tag}`" for tag in tag_list[:5]])
                    if len(tag_list) > 5:
                        tags_display += f" • ... +{len(tag_list)-5} more"
                    st.caption(tags_display)

            with col2:
                # Metadata
                st.caption(f"Structure: {structure}")
                if has_costs:
                    st.caption("💰 Has costs")

            with col3:
                # Selection button
                if enable_selection:
                    is_selected = is_choice_selected(category_name, choice_name)
                    button_label = "✅ Selected" if is_selected else "➕ Select"

                    if st.button(
                        button_label,
                        key=f"search_select_{category_name}_{choice_name}_{idx}",
                        disabled=is_selected
                    ):
                        add_option_to_run(category_name, choice_name)
                        st.success(f"Added {choice_name} to {category_name}")
                        st.rerun()

            st.divider()


def render_category_statistics():
    """
    Render category statistics dashboard
    """
    st.subheader("📊 Category Statistics")

    if 'search_index' not in st.session_state:
        st.info("Search index not initialized")
        return

    search_index = st.session_state.search_index

    # Get statistics
    stats = search_index.get_category_stats()

    # Display metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Categories", len(stats))

    with col2:
        total_choices = stats['total_choices'].sum()
        st.metric("Total Options", total_choices)

    with col3:
        total_with_costs = stats['choices_with_costs'].sum()
        st.metric("Options with Costs", total_with_costs)

    # Detailed table
    with st.expander("📄 Detailed Statistics", expanded=False):
        # Format for display
        display_df = stats.copy()
        display_df['% with costs'] = (
            (display_df['choices_with_costs'] / display_df['total_choices'] * 100)
            .round(1)
        )

        # Sort by total choices
        display_df = display_df.sort_values('total_choices', ascending=False)

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


def render_tag_explorer():
    """
    Render tag explorer for browsing all available tags
    """
    st.subheader("🏷️ Tag Explorer")

    if 'search_index' not in st.session_state:
        st.info("Search index not initialized")
        return

    search_index = st.session_state.search_index

    # Get all tags
    all_tags = search_index.get_all_tags()

    st.metric("Total Tags", len(all_tags))

    # Search tags
    tag_search = st.text_input(
        "Filter tags",
        placeholder="Type to filter tags...",
        key="tag_search"
    )

    # Filter tags
    if tag_search:
        filtered_tags = [t for t in all_tags if tag_search.lower() in t.lower()]
    else:
        filtered_tags = all_tags

    # Display tags as pills (using columns)
    st.caption(f"Showing {len(filtered_tags)} tags:")

    # Group tags in rows of 3
    for i in range(0, len(filtered_tags), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(filtered_tags):
                tag = filtered_tags[i + j]
                with cols[j]:
                    if st.button(f"`{tag}`", key=f"tag_btn_{tag}_{i}_{j}"):
                        # Set search query to this tag
                        st.session_state.search_query = tag
                        st.rerun()


def render_search_performance():
    """
    Display search performance metrics (for debugging)
    """
    if not st.session_state.get('show_debug', False):
        return

    st.caption("🔧 Search Performance")

    if 'search_index' in st.session_state:
        import time

        search_index = st.session_state.search_index

        # Benchmark search
        start = time.time()
        results = search_index.search("test", limit=100)
        elapsed_ms = (time.time() - start) * 1000

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Last Query", f"{elapsed_ms:.1f}ms")
        with col2:
            st.metric("Total Options", len(search_index.df))
        with col3:
            target = "10ms"
            status = "✅" if elapsed_ms < 10 else "⚠️"
            st.metric("Target", f"{target} {status}")
