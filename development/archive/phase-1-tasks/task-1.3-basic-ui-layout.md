# Task 1.3: Basic UI Layout

**Duration:** 2-3 hours
**Phase:** 1 - Foundation
**Dependencies:** Task 1.1 (Project Setup), Task 1.2 (Data Models)
**Completion Criteria:** 3-panel Streamlit layout created, file upload working, placeholders for all panels

---

## Objective

Create the foundational 3-panel Streamlit UI layout with file upload capabilities and navigation structure.

---

## What You'll Build

1. **LEFT Panel**: Run configuration and file upload
2. **MIDDLE Panel**: Options browser and selector
3. **RIGHT Panel**: Cost components viewer
4. File upload widget for .run files
5. Session state management
6. Basic styling and responsive layout

---

## UI Layout Design

```
┌─────────────────────────────────────────────────────────────┐
│  🏠 HTAP Configuration Editor                    [Settings] │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┬─────────────────┬─────────────────────┐   │
│  │   LEFT      │     MIDDLE      │       RIGHT         │   │
│  │  Run Config │  Options Browser│  Cost Components    │   │
│  │             │                 │                     │   │
│  │ [Upload]    │  Search: [____] │  Selected Option:   │   │
│  │             │                 │  [option name]      │   │
│  │ Archetypes: │  Category:      │                     │   │
│  │ [_______]   │  ☐ Opt-Windows  │  Components:        │   │
│  │             │  ☐ Opt-ACH      │  • component_1      │   │
│  │ Location:   │  ☐ Opt-Heating  │  • component_2      │   │
│  │ [_______]   │                 │                     │   │
│  │             │  Results: (250) │  Total Cost:        │   │
│  │ Ruleset:    │  ┌────────────┐ │  $1,234.56          │   │
│  │ [_______]   │  │ Option 1   │ │                     │   │
│  │             │  │ tags...    │ │  [Add to Run]       │   │
│  │ Options:    │  └────────────┘ │                     │   │
│  │ • Windows   │  ┌────────────┐ │                     │   │
│  │ • ACH       │  │ Option 2   │ │                     │   │
│  │             │  │ tags...    │ │                     │   │
│  └─────────────┴─────────────────┴─────────────────────┘   │
│                                                               │
│  Status: Ready to configure              [Export] [Reset]   │
└─────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Implementation

### Step 1: Create UI Components Module Structure (15 min)

```
src/ui/
├── __init__.py
├── layout.py          # Main 3-panel layout
├── left_panel.py      # Run configuration panel
├── middle_panel.py    # Options browser panel
├── right_panel.py     # Cost components panel
└── components.py      # Reusable UI components
```

### Step 2: Create Reusable Components (30 min)

**File:** `src/ui/components.py`

```python
"""
Reusable Streamlit UI components
"""

import streamlit as st
from typing import List, Optional, Callable


def file_uploader_card(
    label: str,
    file_types: List[str],
    help_text: Optional[str] = None,
    key: Optional[str] = None
) -> Optional[bytes]:
    """
    Styled file uploader in a card

    Args:
        label: Upload button label
        file_types: Accepted file extensions
        help_text: Help tooltip text
        key: Streamlit widget key

    Returns:
        Uploaded file contents or None
    """
    with st.container():
        st.markdown("### 📁 " + label)
        if help_text:
            st.caption(help_text)

        uploaded_file = st.file_uploader(
            "Choose file",
            type=file_types,
            key=key,
            label_visibility="collapsed"
        )

        if uploaded_file:
            return uploaded_file.getvalue()
        return None


def search_box(
    placeholder: str = "Search...",
    key: Optional[str] = None,
    on_change: Optional[Callable] = None
) -> str:
    """
    Styled search input box

    Args:
        placeholder: Placeholder text
        key: Streamlit widget key
        on_change: Callback function

    Returns:
        Search query string
    """
    return st.text_input(
        "Search",
        placeholder=placeholder,
        key=key,
        on_change=on_change,
        label_visibility="collapsed"
    )


def option_card(
    title: str,
    tags: List[str],
    has_costs: bool = False,
    cost_count: int = 0,
    on_click: Optional[Callable] = None
) -> bool:
    """
    Display an option as a clickable card

    Args:
        title: Option title
        tags: List of tags
        has_costs: Whether option has cost components
        cost_count: Number of cost components
        on_click: Click handler

    Returns:
        True if clicked
    """
    with st.container():
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(f"**{title}**")
            if tags:
                tag_str = " • ".join(f"`{tag}`" for tag in tags[:3])
                st.caption(tag_str)

        with col2:
            if has_costs:
                st.caption(f"💰 {cost_count}")

            clicked = st.button("→", key=f"btn_{title}", help="View details")

        st.markdown("---")

        return clicked


def status_badge(
    status: str,
    badge_type: str = "info"
) -> None:
    """
    Display a colored status badge

    Args:
        status: Status text
        badge_type: "info", "success", "warning", or "error"
    """
    colors = {
        "info": "#0066CC",
        "success": "#00AA00",
        "warning": "#FFAA00",
        "error": "#CC0000"
    }

    color = colors.get(badge_type, colors["info"])

    st.markdown(
        f'<span style="background-color: {color}; color: white; '
        f'padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">'
        f'{status}</span>',
        unsafe_allow_html=True
    )


def cost_summary_card(
    total_cost: float,
    component_count: int,
    currency: str = "CAD"
) -> None:
    """
    Display cost summary card

    Args:
        total_cost: Total cost amount
        component_count: Number of components
        currency: Currency code
    """
    st.markdown("### 💰 Cost Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total Cost",
            f"${total_cost:,.2f} {currency}"
        )

    with col2:
        st.metric(
            "Components",
            component_count
        )
```

### Step 3: Create Left Panel (30 min)

**File:** `src/ui/left_panel.py`

```python
"""
Left panel: Run configuration and file upload
"""

import streamlit as st
from typing import Optional
from src.ui.components import file_uploader_card, status_badge


def render_left_panel() -> None:
    """Render the left panel for run configuration"""

    st.header("⚙️ Run Configuration")

    # File upload section
    st.markdown("---")
    uploaded_run = file_uploader_card(
        label="Import .run File",
        file_types=["run"],
        help_text="Upload existing .run file to edit",
        key="run_file_upload"
    )

    if uploaded_run:
        st.success("✅ File loaded successfully")
        if st.button("Clear", key="clear_upload"):
            st.session_state.pop("run_file_upload")
            st.rerun()

    st.markdown("---")

    # Run scope section
    st.subheader("Run Scope")

    # Archetypes
    archetypes = st.multiselect(
        "Archetypes",
        options=_get_archetypes(),
        default=st.session_state.get("selected_archetypes", []),
        key="selected_archetypes",
        help="Select one or more archetype files"
    )

    # Location
    location = st.selectbox(
        "Location",
        options=_get_locations(),
        index=0,
        key="selected_location",
        help="Weather location for simulation"
    )

    # Ruleset
    ruleset = st.selectbox(
        "Ruleset",
        options=_get_rulesets(),
        index=0,
        key="selected_ruleset",
        help="Building code ruleset"
    )

    st.markdown("---")

    # Selected options summary
    st.subheader("Selected Options")

    if "run_options" in st.session_state and st.session_state.run_options:
        for opt_type, opt_choice in st.session_state.run_options.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(f"{opt_type}: {opt_choice}")
            with col2:
                if st.button("✕", key=f"remove_{opt_type}"):
                    del st.session_state.run_options[opt_type]
                    st.rerun()
    else:
        st.caption("No options selected yet")

    st.markdown("---")

    # Action buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Reset", use_container_width=True):
            _reset_configuration()

    with col2:
        export_disabled = not bool(
            st.session_state.get("run_options")
        )
        if st.button(
            "📦 Export",
            use_container_width=True,
            disabled=export_disabled,
            help="Export .run file" if not export_disabled else "Add options first"
        ):
            st.session_state.show_export = True


def _get_archetypes() -> list:
    """Get available archetypes (placeholder)"""
    # TODO: Load from actual archetype directory
    return [
        "AB-base.h2k",
        "BC-base.h2k",
        "ON-base.h2k",
        "QC-base.h2k"
    ]


def _get_locations() -> list:
    """Get available locations (placeholder)"""
    # TODO: Load from HTAP-options.json Opt-Location
    return [
        "Vancouver-BC",
        "Toronto-ON",
        "Montreal-QC",
        "Calgary-AB"
    ]


def _get_rulesets() -> list:
    """Get available rulesets (placeholder)"""
    # TODO: Load from configuration
    return [
        "as_found",
        "NBC-9.36",
        "BC-Step-3"
    ]


def _reset_configuration() -> None:
    """Reset all configuration state"""
    keys_to_reset = [
        "run_options",
        "selected_archetypes",
        "selected_location",
        "selected_ruleset",
        "selected_option_detail"
    ]

    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

    st.rerun()
```

### Step 4: Create Middle Panel (30 min)

**File:** `src/ui/middle_panel.py`

```python
"""
Middle panel: Options browser and selector
"""

import streamlit as st
from typing import Dict, List
from src.ui.components import search_box, option_card


def render_middle_panel() -> None:
    """Render the middle panel for browsing options"""

    st.header("🔍 Options Browser")

    # Search box
    search_query = search_box(
        placeholder="Search options, tags, or descriptions...",
        key="options_search"
    )

    st.markdown("---")

    # Category filter
    st.subheader("Categories")

    categories = _get_option_categories()
    selected_categories = []

    # Create collapsible category filters
    with st.expander("Filter by Category", expanded=True):
        for category in categories:
            if st.checkbox(category, key=f"cat_{category}"):
                selected_categories.append(category)

    st.markdown("---")

    # Results section
    options_list = _get_filtered_options(search_query, selected_categories)

    st.subheader(f"Results ({len(options_list)})")

    if not options_list:
        st.info("No options found. Try adjusting your search or filters.")
    else:
        # Pagination
        items_per_page = 10
        total_pages = (len(options_list) - 1) // items_per_page + 1

        if "current_page" not in st.session_state:
            st.session_state.current_page = 0

        start_idx = st.session_state.current_page * items_per_page
        end_idx = start_idx + items_per_page
        page_options = options_list[start_idx:end_idx]

        # Display options as cards
        for option in page_options:
            if option_card(
                title=option["name"],
                tags=option.get("tags", []),
                has_costs=option.get("has_costs", False),
                cost_count=option.get("cost_count", 0)
            ):
                st.session_state.selected_option_detail = option
                st.rerun()

        # Pagination controls
        if total_pages > 1:
            col1, col2, col3 = st.columns([1, 2, 1])

            with col1:
                if st.button("◀ Prev", disabled=(st.session_state.current_page == 0)):
                    st.session_state.current_page -= 1
                    st.rerun()

            with col2:
                st.caption(
                    f"Page {st.session_state.current_page + 1} of {total_pages}"
                )

            with col3:
                if st.button(
                    "Next ▶",
                    disabled=(st.session_state.current_page >= total_pages - 1)
                ):
                    st.session_state.current_page += 1
                    st.rerun()


def _get_option_categories() -> List[str]:
    """Get list of option categories (placeholder)"""
    # TODO: Load from OptionsDatabase
    return [
        "Opt-Windows",
        "Opt-ACH",
        "Opt-AboveGradeWall",
        "Opt-AtticCeilings",
        "Opt-Heating-Cooling",
        "Opt-DHWSystem",
        "Opt-VentSystem"
    ]


def _get_filtered_options(
    search_query: str,
    categories: List[str]
) -> List[Dict]:
    """
    Get filtered options based on search and categories (placeholder)

    TODO: Implement actual filtering with OptionsDatabase
    """
    # Mock data for now
    mock_options = [
        {
            "name": "DoubleGlazed-Air-LowE",
            "category": "Opt-Windows",
            "tags": ["low-e", "double-glazed", "air-filled"],
            "has_costs": True,
            "cost_count": 3
        },
        {
            "name": "TripleGlazed-Argon-LowE",
            "category": "Opt-Windows",
            "tags": ["low-e", "triple-glazed", "argon"],
            "has_costs": True,
            "cost_count": 4
        },
        # Add more mock options...
    ]

    # Filter by search query
    if search_query:
        mock_options = [
            opt for opt in mock_options
            if search_query.lower() in opt["name"].lower()
            or any(search_query.lower() in tag for tag in opt.get("tags", []))
        ]

    # Filter by categories
    if categories:
        mock_options = [
            opt for opt in mock_options
            if opt["category"] in categories
        ]

    return mock_options
```

### Step 5: Create Right Panel (30 min)

**File:** `src/ui/right_panel.py`

```python
"""
Right panel: Cost components and details
"""

import streamlit as st
from typing import Dict, Optional
from src.ui.components import cost_summary_card, status_badge


def render_right_panel() -> None:
    """Render the right panel for cost components"""

    st.header("💰 Cost Components")

    selected_option = st.session_state.get("selected_option_detail")

    if not selected_option:
        st.info("👈 Select an option from the browser to view cost details")
        return

    # Option details header
    st.subheader(selected_option["name"])

    # Tags
    if selected_option.get("tags"):
        st.caption(" • ".join(f"`{tag}`" for tag in selected_option["tags"]))

    st.markdown("---")

    # Cost components list
    st.subheader("Cost Components")

    components = _get_option_cost_components(selected_option["name"])

    if not components:
        st.warning("⚠️ No cost components assigned to this option")
        st.caption("Cost components need to be added in HTAP-options.json")
    else:
        for component in components:
            with st.expander(f"{component['id']}", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    st.caption("**Unit:**")
                    st.text(component["unit"])
                    st.caption("**Type:**")
                    st.text(component["type"])

                with col2:
                    st.caption("**Cost:**")
                    st.text(f"${component['cost']:.2f}")
                    st.caption("**Source:**")
                    st.text(component["source"])

                if component.get("description"):
                    st.caption("**Description:**")
                    st.caption(component["description"])

    st.markdown("---")

    # Cost summary
    if components:
        total_cost = sum(c["cost"] for c in components)
        cost_summary_card(
            total_cost=total_cost,
            component_count=len(components)
        )

    st.markdown("---")

    # Add to run button
    if st.button(
        "➕ Add to Run Configuration",
        use_container_width=True,
        type="primary"
    ):
        _add_option_to_run(selected_option)
        st.success(f"✅ Added {selected_option['name']} to configuration")
        st.balloons()


def _get_option_cost_components(option_name: str) -> list:
    """
    Get cost components for an option (placeholder)

    TODO: Load from OptionsDatabase and UnitCostsDatabase
    """
    # Mock data
    return [
        {
            "id": "windows:dg:vinyl:low-e_soft",
            "unit": "sqft",
            "type": "material",
            "cost": 45.50,
            "source": "LEEP-BC-KamloopsChesnut",
            "description": "Double-glazed vinyl window with soft-coat low-e"
        },
        {
            "id": "window_installation:labour",
            "unit": "sqft",
            "type": "labour",
            "cost": 15.00,
            "source": "LEEP-BC-KamloopsChesnut",
            "description": "Window installation labour"
        }
    ]


def _add_option_to_run(option: Dict) -> None:
    """Add selected option to run configuration"""
    if "run_options" not in st.session_state:
        st.session_state.run_options = {}

    category = option["category"]
    st.session_state.run_options[category] = option["name"]
```

### Step 6: Create Main Layout (30 min)

**File:** `src/ui/layout.py`

```python
"""
Main 3-panel layout for HTAP Configuration Editor
"""

import streamlit as st
from src.ui.left_panel import render_left_panel
from src.ui.middle_panel import render_middle_panel
from src.ui.right_panel import render_right_panel


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables"""
    if "run_options" not in st.session_state:
        st.session_state.run_options = {}

    if "selected_option_detail" not in st.session_state:
        st.session_state.selected_option_detail = None

    if "current_page" not in st.session_state:
        st.session_state.current_page = 0


def render_main_layout() -> None:
    """Render the main 3-panel layout"""

    # Initialize state
    initialize_session_state()

    # Page header
    st.title("🏠 HTAP Configuration Editor")
    st.markdown("Build and export HTAP run configurations with visual cost tracking")
    st.markdown("---")

    # Create 3-column layout
    col_left, col_middle, col_right = st.columns([1, 2, 1.5])

    with col_left:
        render_left_panel()

    with col_middle:
        render_middle_panel()

    with col_right:
        render_right_panel()

    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        options_count = len(st.session_state.get("run_options", {}))
        st.caption(f"📊 Configuration: {options_count} options selected")

    with col2:
        st.caption("v0.1.0 | Phase 1")

    with col3:
        if st.button("ℹ️ Help"):
            show_help_dialog()


def show_help_dialog() -> None:
    """Show help dialog"""
    with st.expander("📖 Help & Instructions", expanded=True):
        st.markdown("""
        ### How to Use This Tool

        **LEFT Panel** - Run Configuration
        - Upload existing .run files or start fresh
        - Select archetypes, location, and ruleset
        - View selected options

        **MIDDLE Panel** - Options Browser
        - Search and filter options
        - Browse by category
        - Click an option to view details

        **RIGHT Panel** - Cost Components
        - View cost breakdown for selected option
        - See component details and sources
        - Add options to your configuration

        **Export** - When ready, click Export to download your .run file
        """)
```

### Step 7: Update Main App (15 min)

**File:** `app.py` (replace existing)

```python
"""
HTAP Configuration Editor
Main Streamlit application
"""

import streamlit as st
from src.ui.layout import render_main_layout

# Page configuration
st.set_page_config(
    page_title="HTAP Configuration Editor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1 {
        padding-bottom: 1rem;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Render main layout
render_main_layout()
```

---

## Acceptance Criteria

✅ **3-panel layout** displays correctly in wide mode
✅ **File upload widget** accepts .run files
✅ **Left panel** shows run configuration options
✅ **Middle panel** displays searchable options list with pagination
✅ **Right panel** shows cost component details
✅ **Session state** persists selections across interactions
✅ **Responsive layout** works on different screen sizes
✅ **UI is styled** and visually organized

---

## Testing Checklist

```bash
# Run the app
streamlit run app.py

# Manual testing:
# 1. Verify 3 columns display side-by-side
# 2. Try uploading a .run file
# 3. Select categories in middle panel
# 4. Search for options
# 5. Click an option card - details appear in right panel
# 6. Click "Add to Run" - option appears in left panel summary
# 7. Click "Reset" - all selections clear
# 8. Test pagination if >10 options displayed
```

---

## Next Steps

After completing this task:
1. Test layout on different screen sizes
2. Gather user feedback on UI organization
3. Move to **Task 1.4: Run File Parser**

---

## Time Tracking

- Components module: 30 min
- Left panel: 30 min
- Middle panel: 30 min
- Right panel: 30 min
- Main layout: 30 min
- Update app.py: 15 min
- **Total: ~2.5 hours**
