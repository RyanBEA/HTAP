# Task 2.5: Advanced Search Features

**Duration:** 2-3 hours
**Phase:** 2 - Core Functionality
**Dependencies:** Task 1.5 (Options Search), Task 2.1 (Panel Interactions)
**Completion Criteria:** Advanced search UI working, filters functional, performance <10ms

---

## Objective

Enhance the MIDDLE panel with advanced search capabilities, allowing users to quickly find options using text search, filters, and tags. Build an intuitive search interface that leverages the pandas-based search from Task 1.5.

---

## What You'll Build

1. Search bar with live results in MIDDLE panel
2. Tag-based filtering with tag selector
3. Cost presence filter
4. Structure type filter (flat vs tree)
5. Category statistics dashboard
6. Search results display with highlighting
7. Integration tests

---

## Context: Search Capabilities

From Task 1.5, we have `OptionsSearch` class with:
- Text search across choice names, tags, descriptions
- Category filtering
- Cost presence filtering
- Structure filtering
- Performance <10ms for all queries

Now we need to build UI around these capabilities.

---

## Step-by-Step Implementation

### Step 1: Create Advanced Search Widget (75 min)

**File:** `src/ui/search_widget.py`

```python
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
            st.warning("Options database not loaded")
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
        add_option_selection,
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
                        add_option_selection(category_name, choice_name)
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
```

---

### Step 2: Update MIDDLE Panel with Search Tab (30 min)

**File:** `src/ui/middle_panel.py`

Add tabbed interface with search:

```python
def render_middle_panel():
    """Render MIDDLE panel with browse and search tabs"""
    st.header("2️⃣ Select Options")

    if 'options_db' not in st.session_state:
        st.info("👈 Load HTAP options in the left panel first")
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
    Original category browsing interface
    (Existing code from previous tasks)
    """
    # ... existing category selection and option display code ...
    pass
```

---

### Step 3: Add Search Performance Monitor (15 min)

**File:** `src/ui/search_widget.py`

Add performance monitoring:

```python
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
```

---

### Step 4: Create Integration Tests (30 min)

**File:** `tests/test_search_integration.py`

```python
"""
Integration tests for search features
"""

import pytest
from pathlib import Path

from src.utils import load_options
from src.utils.options_search import OptionsSearch


@pytest.fixture
def options_db():
    """Load real options database"""
    path = "C:/HTAP/HTAP-options.json"
    if not Path(path).exists():
        pytest.skip(f"Options file not found: {path}")
    return load_options(path)


@pytest.fixture
def search_index(options_db):
    """Create search index"""
    return OptionsSearch(options_db)


class TestAdvancedSearch:
    """Test advanced search features"""

    def test_search_with_all_filters(self, search_index):
        """Test search with all filters applied"""
        results = search_index.search(
            query="window",
            categories=["Opt-Windows"],
            require_costs=True,
            structure="tree",
            limit=50
        )

        # Should return results or empty DataFrame
        assert results is not None
        assert 'category' in results.columns
        assert 'choice' in results.columns

    def test_empty_search_returns_all(self, search_index):
        """Test that empty search with no filters returns results"""
        results = search_index.search(
            query="",
            categories=None,
            require_costs=None,
            structure=None,
            limit=100
        )

        assert len(results) > 0
        assert len(results) <= 100  # Respects limit

    def test_category_filter_only(self, search_index):
        """Test filtering by category only"""
        results = search_index.search(
            categories=["Opt-Windows"],
            limit=100
        )

        # All results should be from Opt-Windows
        assert all(cat == "Opt-Windows" for cat in results['category'])

    def test_cost_filter_only(self, search_index):
        """Test filtering by cost presence"""
        with_costs = search_index.search(
            require_costs=True,
            limit=100
        )

        # All results should have costs
        assert all(has_costs for has_costs in with_costs['has_costs'])

        without_costs = search_index.search(
            require_costs=False,
            limit=100
        )

        # No results should have costs
        assert not any(has_costs for has_costs in without_costs['has_costs'])

    def test_structure_filter(self, search_index):
        """Test filtering by structure type"""
        flat_results = search_index.search(
            structure="flat",
            limit=100
        )

        assert all(struct == "flat" for struct in flat_results['structure'])

        tree_results = search_index.search(
            structure="tree",
            limit=100
        )

        assert all(struct == "tree" for struct in tree_results['structure'])

    def test_tag_search(self, search_index):
        """Test searching by tags"""
        # Search for a common tag
        results = search_index.search(
            query="energy",  # Common tag
            limit=50
        )

        # Should find results with 'energy' in tags or name
        assert len(results) > 0

    def test_search_performance(self, search_index):
        """Test that search completes quickly"""
        import time

        queries = [
            {"query": "window"},
            {"categories": ["Opt-Windows"]},
            {"require_costs": True},
            {"query": "low-e", "categories": ["Opt-Windows"]},
        ]

        for query_params in queries:
            start = time.time()
            results = search_index.search(**query_params, limit=100)
            elapsed_ms = (time.time() - start) * 1000

            assert elapsed_ms < 10, f"Search took {elapsed_ms:.1f}ms (expected <10ms)"

    def test_limit_respected(self, search_index):
        """Test that result limit is respected"""
        results = search_index.search(limit=25)
        assert len(results) <= 25

        results = search_index.search(limit=100)
        assert len(results) <= 100


class TestCategoryStatistics:
    """Test category statistics functions"""

    def test_get_all_categories(self, search_index):
        """Test getting all category names"""
        categories = search_index.get_all_categories()

        assert isinstance(categories, list)
        assert len(categories) == 34  # Known count
        assert "Opt-Windows" in categories

    def test_get_all_tags(self, search_index):
        """Test getting all unique tags"""
        tags = search_index.get_all_tags()

        assert isinstance(tags, list)
        assert len(tags) > 0
        # Tags should be unique
        assert len(tags) == len(set(tags))

    def test_category_stats(self, search_index):
        """Test getting category statistics"""
        stats = search_index.get_category_stats()

        assert len(stats) == 34  # Known number of categories
        assert 'category' in stats.columns
        assert 'total_choices' in stats.columns
        assert 'choices_with_costs' in stats.columns
        assert 'structure' in stats.columns
        assert 'costed' in stats.columns

        # Verify totals
        total_choices = stats['total_choices'].sum()
        assert total_choices == 769  # Known total

    def test_count_method(self, search_index):
        """Test count method"""
        # Count all
        total = search_index.count()
        assert total == 769

        # Count with filter
        windows_count = search_index.count(categories=["Opt-Windows"])
        assert windows_count > 0

        # Count with cost filter
        costed_count = search_index.count(require_costs=True)
        assert costed_count > 0
        assert costed_count < total  # Some options don't have costs
```

---

## Acceptance Criteria

✅ **Search widget rendered** in MIDDLE panel
✅ **Text search works** across names, tags, descriptions
✅ **Category filter** limits results to selected categories
✅ **Cost filter** shows only options with/without costs
✅ **Structure filter** filters by flat/tree structure
✅ **Tag explorer** displays all tags and enables tag search
✅ **Category statistics** shows counts and percentages
✅ **Search results** display with selection buttons
✅ **Performance <10ms** for all search queries
✅ **Tests pass** for all search scenarios

---

## Testing Checklist

```bash
# Run unit tests
pytest tests/test_search_integration.py -v -s

# Manual testing in Streamlit:
# 1. Search for "window" - should return results quickly
# 2. Filter by category "Opt-Windows"
# 3. Filter by "With costs"
# 4. Combine filters (search + category + costs)
# 5. View category statistics
# 6. Browse tags and click to search
# 7. Select options from search results
# 8. Verify performance <10ms in debug mode
```

---

## Common Issues & Solutions

### Issue: Search results not updating
**Solution:** Ensure st.rerun() is called after state changes

### Issue: Tag filtering not working
**Solution:** Verify tags are stored as pipe-separated strings in DataFrame

### Issue: Slow search performance
**Solution:** With 769 items, should be <10ms. Check if DataFrame is being copied unnecessarily.

---

## Performance Targets

| Operation | Target | Actual (Expected) |
|-----------|--------|-------------------|
| Text search | <10ms | ~2-5ms |
| Category filter | <10ms | ~1-3ms |
| Combined filters | <10ms | ~5-8ms |
| Statistics calculation | <50ms | ~20-30ms |

---

## UI/UX Enhancements

**Search hints:**
- Show recent searches
- Suggest common terms
- Auto-complete based on tags

**Results display:**
- Highlight search terms in results
- Show result snippets
- Quick-add to selections

**Future enhancements:**
- Save search presets
- Search history
- Advanced Boolean queries

---

## Next Steps

After completing this task:
1. Test search performance with various queries
2. Verify all filters work correctly
3. **Phase 2 Complete!** Review before starting Phase 3
4. Proceed to **Task 3.1: Export Run File**

---

## Time Tracking

- Advanced search widget: 75 min
- MIDDLE panel integration: 30 min
- Performance monitor: 15 min
- Integration tests: 30 min
- **Total: ~2.5 hours**

---

## Integration Points

**Inputs:**
- Task 1.5: OptionsSearch class with pandas DataFrame
- Task 2.1: Session state for selections

**Outputs:**
- Search results that can be selected
- Category statistics for overview
- Tag explorer for discovery

**Used by:**
- Task 3.1: Export (all selected options regardless of how they were selected)
