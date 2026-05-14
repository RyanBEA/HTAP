# Task 2.1: Dynamic Panel Interactions

**Duration:** 3-4 hours
**Phase:** 2 - Core Functionality
**Dependencies:** Task 1.3 (Basic UI Layout), Task 1.5 (Options Search)
**Completion Criteria:** Panels update dynamically, state management works, selections persist

---

## Objective

Wire the 3-panel UI together so that selecting items in one panel updates the others. Implement Streamlit session state management for persistent selections across interactions.

---

## What You'll Build

1. LEFT → MIDDLE: Category selection updates options browser
2. MIDDLE → RIGHT: Option selection shows cost details
3. Session state management for all selections
4. Visual feedback for active selections
5. State persistence across page interactions

---

## Technical Approach

### Streamlit Session State Strategy

```python
# Session state structure
st.session_state = {
    # Run configuration
    'run_config': {
        'archetypes': [],
        'location': 'Vancouver-BC',
        'ruleset': 'as-found'
    },

    # Selected options (for .run file export)
    'selected_options': {
        'Opt-Windows': 'DoubleGlazed-LowE',
        'Opt-ACH': '1.5',
        # ... more selections
    },

    # UI state
    'current_category': 'Opt-Windows',  # Active category filter
    'selected_option_detail': {...},     # Option being viewed in right panel
    'search_query': '',                  # Current search term
}
```

---

## Step-by-Step Implementation

### Step 1: Initialize Session State (30 min)

**File:** `src/ui/state_manager.py`

```python
"""
Streamlit session state management
"""

import streamlit as st
from typing import Dict, List, Optional, Any


def initialize_session_state():
    """Initialize all session state variables"""

    # Run configuration
    if 'run_config' not in st.session_state:
        st.session_state.run_config = {
            'archetypes': [],
            'location': None,
            'ruleset': 'as-found'
        }

    # Selected options (category -> choice mapping)
    if 'selected_options' not in st.session_state:
        st.session_state.selected_options = {}

    # UI state
    if 'current_category' not in st.session_state:
        st.session_state.current_category = None

    if 'selected_option_detail' not in st.session_state:
        st.session_state.selected_option_detail = None

    if 'search_query' not in st.session_state:
        st.session_state.search_query = ''

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0


def add_option_to_run(category: str, choice: str):
    """
    Add an option to the run configuration

    Args:
        category: Option category (e.g., 'Opt-Windows')
        choice: Choice name within category
    """
    st.session_state.selected_options[category] = choice


def remove_option_from_run(category: str):
    """Remove an option from the run configuration"""
    if category in st.session_state.selected_options:
        del st.session_state.selected_options[category]


def get_selected_option(category: str) -> Optional[str]:
    """Get the currently selected choice for a category"""
    return st.session_state.selected_options.get(category)


def clear_all_selections():
    """Clear all selected options"""
    st.session_state.selected_options = {}
    st.session_state.selected_option_detail = None


def set_category_filter(category: Optional[str]):
    """Set the current category filter for middle panel"""
    st.session_state.current_category = category
    st.session_state.current_page = 0  # Reset pagination


def set_option_detail(option_data: Optional[Dict[str, Any]]):
    """Set the option to display in right panel"""
    st.session_state.selected_option_detail = option_data
```

---

### Step 2: Update Left Panel with Interactions (45 min)

**File:** `src/ui/left_panel.py` (update existing)

```python
"""
Left panel: Run configuration and category selection
"""

import streamlit as st
from typing import List
from src.ui.state_manager import (
    initialize_session_state,
    add_option_to_run,
    remove_option_from_run,
    set_category_filter,
    clear_all_selections
)
from src.utils import load_options


def render_left_panel():
    """Render the left panel"""

    initialize_session_state()

    st.header("⚙️ Run Configuration")

    # Run scope section
    st.markdown("---")
    st.subheader("Run Scope")

    # Archetypes
    archetypes = st.multiselect(
        "Archetypes",
        options=_get_archetypes(),
        default=st.session_state.run_config.get('archetypes', []),
        key="archetypes_select",
        help="Select archetype .h2k files"
    )
    st.session_state.run_config['archetypes'] = archetypes

    # Location
    location = st.selectbox(
        "Location",
        options=_get_locations(),
        index=0 if not st.session_state.run_config.get('location') else None,
        key="location_select"
    )
    st.session_state.run_config['location'] = location

    # Ruleset
    ruleset = st.selectbox(
        "Ruleset",
        options=['as-found', 'NBC-9.36', 'BC-Step-3'],
        index=0,
        key="ruleset_select"
    )
    st.session_state.run_config['ruleset'] = ruleset

    st.markdown("---")

    # Category filter buttons
    st.subheader("Filter by Category")

    # Load options to get categories
    options_db = load_options("C:/HTAP/HTAP-options.json")
    categories = sorted([cat for cat in options_db.list_categories() if cat.startswith('Opt-')])

    # Group categories for display
    envelope_cats = [c for c in categories if 'Wall' in c or 'Window' in c or 'Ceiling' in c or 'Foundation' in c or 'Door' in c or 'Slab' in c or 'Floor' in c]
    mech_cats = [c for c in categories if 'Heating' in c or 'DHW' in c or 'Vent' in c or 'PV' in c]
    other_cats = [c for c in categories if c not in envelope_cats and c not in mech_cats]

    with st.expander("🏠 Envelope", expanded=True):
        for cat in envelope_cats:
            short_name = cat.replace('Opt-', '')
            if st.button(
                short_name,
                key=f"cat_btn_{cat}",
                use_container_width=True,
                type="primary" if st.session_state.current_category == cat else "secondary"
            ):
                set_category_filter(cat)
                st.rerun()

    with st.expander("🔧 Mechanical", expanded=False):
        for cat in mech_cats:
            short_name = cat.replace('Opt-', '')
            if st.button(
                short_name,
                key=f"cat_btn_{cat}",
                use_container_width=True,
                type="primary" if st.session_state.current_category == cat else "secondary"
            ):
                set_category_filter(cat)
                st.rerun()

    with st.expander("📋 Other", expanded=False):
        for cat in other_cats:
            short_name = cat.replace('Opt-', '')
            if st.button(
                short_name,
                key=f"cat_btn_{cat}",
                use_container_width=True,
                type="primary" if st.session_state.current_category == cat else "secondary"
            ):
                set_category_filter(cat)
                st.rerun()

    # Show all button
    if st.button("Show All Categories", use_container_width=True):
        set_category_filter(None)
        st.rerun()

    st.markdown("---")

    # Selected options summary
    st.subheader("Selected Options")

    if st.session_state.selected_options:
        for opt_type, opt_choice in st.session_state.selected_options.items():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.caption(f"**{opt_type.replace('Opt-', '')}**")
                st.text(opt_choice)
            with col2:
                if st.button("✕", key=f"remove_{opt_type}"):
                    remove_option_from_run(opt_type)
                    st.rerun()
    else:
        st.info("No options selected yet. Browse options in the middle panel.")

    st.markdown("---")

    # Action buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Reset All", use_container_width=True):
            clear_all_selections()
            st.rerun()

    with col2:
        export_disabled = not bool(st.session_state.selected_options)
        st.button(
            "📦 Export",
            use_container_width=True,
            disabled=export_disabled,
            help="Export .run file (Phase 3)"
        )


def _get_archetypes() -> List[str]:
    """Get available archetypes"""
    # TODO: Scan archetype directory
    return ["AB-base.h2k", "BC-base.h2k", "ON-base.h2k"]


def _get_locations() -> List[str]:
    """Get available locations from options file"""
    try:
        options_db = load_options("C:/HTAP/HTAP-options.json")
        loc_category = options_db.get_category("Opt-Location")
        if loc_category:
            return sorted(loc_category.list_choices())
    except:
        pass
    return ["Vancouver-BC", "Toronto-ON", "Calgary-AB"]
```

---

### Step 3: Update Middle Panel with State Integration (1 hour)

**File:** `src/ui/middle_panel.py` (update existing)

```python
"""
Middle panel: Options browser with category filtering
"""

import streamlit as st
from src.ui.state_manager import initialize_session_state, set_option_detail
from src.utils import load_options, OptionsSearch


def render_middle_panel():
    """Render the middle panel"""

    initialize_session_state()

    st.header("🔍 Options Browser")

    # Load data
    options_db = load_options("C:/HTAP/HTAP-options.json")
    search = OptionsSearch(options_db)

    # Search box
    search_query = st.text_input(
        "Search",
        value=st.session_state.search_query,
        placeholder="Search options, tags, descriptions...",
        key="search_input",
        label_visibility="collapsed"
    )
    st.session_state.search_query = search_query

    st.markdown("---")

    # Show active category filter
    if st.session_state.current_category:
        st.info(f"📁 **Filtering:** {st.session_state.current_category.replace('Opt-', '')}")

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

    # Display results as cards
    for idx, row in page_results.iterrows():
        _render_option_card(row)

    # Pagination controls
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("◀ Prev", disabled=(st.session_state.current_page == 0)):
                st.session_state.current_page -= 1
                st.rerun()

        with col2:
            st.caption(f"Page {st.session_state.current_page + 1} of {total_pages}")

        with col3:
            if st.button("Next ▶", disabled=(st.session_state.current_page >= total_pages - 1)):
                st.session_state.current_page += 1
                st.rerun()


def _render_option_card(row):
    """Render a single option as a card"""

    with st.container():
        col1, col2 = st.columns([5, 1])

        with col1:
            st.markdown(f"**{row['choice']}**")

            # Tags
            if row['tags']:
                tags = row['tags'].split('|')[:3]
                st.caption(" • ".join(f"`{tag}`" for tag in tags))

            # Category badge
            st.caption(f"📁 {row['category'].replace('Opt-', '')}")

        with col2:
            # Cost indicator
            if row['has_costs']:
                st.caption("💰")

            # View details button
            if st.button("→", key=f"view_{row['category']}_{row['choice']}"):
                # Set option detail for right panel
                set_option_detail({
                    'category': row['category'],
                    'name': row['choice'],
                    'choice_obj': row['choice_obj'],
                    'category_obj': row['category_obj']
                })
                st.rerun()

        st.markdown("---")
```

---

### Step 4: Update Right Panel with Interactive Actions (1 hour)

**File:** `src/ui/right_panel.py` (update existing)

```python
"""
Right panel: Cost components and option details
"""

import streamlit as st
from src.ui.state_manager import initialize_session_state, add_option_to_run, get_selected_option
from src.utils import load_unit_costs


def render_right_panel():
    """Render the right panel"""

    initialize_session_state()

    st.header("💰 Option Details")

    selected = st.session_state.selected_option_detail

    if not selected:
        st.info("👈 Select an option from the browser to view details")
        return

    # Option header
    st.subheader(selected['name'])
    st.caption(f"📁 Category: {selected['category'].replace('Opt-', '')}")

    choice = selected['choice_obj']
    category = selected['category_obj']

    # Tags
    if choice.tags:
        st.markdown("**Tags:**")
        st.caption(" • ".join(f"`{tag}`" for tag in choice.tags))

    # Description
    if choice.description:
        st.markdown("**Description:**")
        st.info(choice.description)

    st.markdown("---")

    # H2K Mappings
    if choice.h2k_map:
        with st.expander("🔧 HOT2000 XML Mappings", expanded=False):
            st.json(choice.h2k_map)

    st.markdown("---")

    # Cost components
    st.subheader("Cost Components")

    if not choice.costs or not choice.costs.components:
        st.warning("⚠️ No cost components assigned to this option")
        if choice.cost_proxy:
            st.caption(f"Uses cost proxy: {choice.cost_proxy}")
    else:
        _display_cost_components(choice.costs.components)

    st.markdown("---")

    # Add to run button
    already_selected = get_selected_option(selected['category']) == selected['name']

    button_col1, button_col2 = st.columns(2)

    with button_col1:
        if already_selected:
            st.success("✅ Already in configuration")
        else:
            if st.button(
                "➕ Add to Run",
                use_container_width=True,
                type="primary"
            ):
                add_option_to_run(selected['category'], selected['name'])
                st.success(f"✅ Added {selected['name']}")
                st.balloons()
                st.rerun()

    with button_col2:
        if already_selected:
            if st.button("Remove from Run", use_container_width=True):
                from src.ui.state_manager import remove_option_from_run
                remove_option_from_run(selected['category'])
                st.rerun()


def _display_cost_components(component_ids):
    """Display cost component details"""

    try:
        costs_db = load_unit_costs("C:/HTAP/HTAPUnitCosts.json")
    except:
        st.error("Could not load cost database")
        return

    total_cost = 0
    sources_used = set()

    for comp_id in component_ids:
        comp_data = costs_db.get_component(comp_id)

        if not comp_data:
            st.warning(f"⚠️ Component not found: `{comp_id}`")
            continue

        # Get first available source
        source_name = list(comp_data.keys())[0]
        source_data = comp_data[source_name]
        sources_used.add(source_name)

        with st.expander(f"**{comp_id}**", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                st.caption("**Category:**")
                st.text(source_data.category)
                st.caption("**Units:**")
                st.text(source_data.units)

            with col2:
                st.caption("**Materials:**")
                st.text(f"${source_data.UnitCostMaterials:.2f}")
                st.caption("**Labour:**")
                st.text(f"${source_data.UnitCostLabour:.2f}")

            st.caption("**Total:**")
            st.text(f"${source_data.total_cost():.2f} per {source_data.units}")

            if source_data.description:
                st.caption("**Description:**")
                st.caption(source_data.description)

        total_cost += source_data.total_cost()

    # Summary
    if total_cost > 0:
        st.success(f"**Estimated Cost:** ${total_cost:.2f}")
        st.caption(f"Sources: {', '.join(sources_used)}")
```

---

## Acceptance Criteria

✅ **Left panel category buttons** filter middle panel
✅ **Middle panel option cards** update right panel on click
✅ **Right panel "Add to Run"** updates left panel summary
✅ **Session state persists** across all interactions
✅ **Visual feedback** shows active selections
✅ **Remove buttons work** in left panel summary
✅ **Pagination maintains** state when filtering

---

## Testing Checklist

```bash
# Run the app
streamlit run app.py

# Manual testing:
1. Click a category button in left panel → Middle panel filters
2. Click an option card → Right panel shows details
3. Click "Add to Run" → Option appears in left panel summary
4. Click remove (✕) → Option disappears
5. Search in middle panel → Results update
6. Navigate pages → State persists
7. Refresh browser → State is lost (expected in Streamlit)
```

---

## Next Steps

After completing this task:
1. Test all panel interactions
2. Verify state management works correctly
3. Move to **Task 2.2: Option Selection Logic**

---

## Time Tracking

- State manager: 30 min
- Left panel updates: 45 min
- Middle panel updates: 60 min
- Right panel updates: 60 min
- Testing: 30 min
- **Total: ~3.5 hours**
