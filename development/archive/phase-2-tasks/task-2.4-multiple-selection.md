# Task 2.4: Multiple Option Selection

**Duration:** 2-3 hours
**Phase:** 2 - Core Functionality
**Dependencies:** Task 2.1 (Panel Interactions), Task 2.3 (Validation)
**Completion Criteria:** Multi-select mode working, displays selected options, exports correctly to .run format

---

## Objective

Enable users to select multiple options per category for parametric runs, following HTAP's .run file format where categories can have comma-separated lists of choices. This allows generating multiple simulation combinations.

---

## What You'll Build

1. Toggle between single-select and multi-select modes
2. UI for adding/removing multiple options per category
3. Visual display of all selected options
4. Selected options summary in RIGHT panel
5. Support for .run file export format (comma-separated)
6. Unit tests

---

## Context: HTAP Parametric Runs

From `regions.run` file analysis, HTAP supports multiple choices per category:

```
Upgrades_START
  Opt-AboveGradeWall = NA, NC_2x6_r19nom_r16Eff, NC_R-23(eff)_2x6-16inOC_R22-batt+1inFoilFacedPolyiso_poly_vb
  Opt-AtticCeilings = CeilR40, CeilR50, CeilR60
  Opt-Windows = NC_Best-L
Upgrades_END
```

**Format:** `Opt-CategoryName = choice1, choice2, choice3, ...`

**Behavior:**
- Single choice → single simulation
- Multiple choices in one category → one sim per choice
- Multiple choices in multiple categories → cartesian product (all combinations)

**Example:**
- 3 archetypes × 2 wall options × 3 ceiling options = 18 simulations

---

## Step-by-Step Implementation

### Step 1: Update Session State Structure (30 min)

**File:** `src/ui/state_manager.py`

Update session state to support multiple selections:

```python
"""
Enhanced session state management with multi-select support
"""

import streamlit as st
from typing import Dict, List, Set


def initialize_session_state():
    """Initialize session state with multi-select support"""

    # Run configuration
    if 'run_config' not in st.session_state:
        st.session_state.run_config = {
            'archetypes': [],
            'location': None,
            'ruleset': 'as-found',
            'cost_source': 'LEEP-ON-Ottawa'
        }

    # Selection mode
    if 'multi_select_mode' not in st.session_state:
        st.session_state.multi_select_mode = False

    # Selected options - now supports multiple choices per category
    if 'selected_options' not in st.session_state:
        # Format: Dict[category_name, Set[choice_name]]
        st.session_state.selected_options = {}


def toggle_selection_mode():
    """Toggle between single and multi-select modes"""
    st.session_state.multi_select_mode = not st.session_state.multi_select_mode

    # When switching to single-select, keep only first selection per category
    if not st.session_state.multi_select_mode:
        for category, choices in st.session_state.selected_options.items():
            if isinstance(choices, set) and len(choices) > 1:
                # Keep only first choice
                st.session_state.selected_options[category] = {list(choices)[0]}


def add_option_selection(category: str, choice: str):
    """
    Add an option selection

    Args:
        category: Category name
        choice: Choice name to add
    """
    if category not in st.session_state.selected_options:
        st.session_state.selected_options[category] = set()

    if st.session_state.multi_select_mode:
        # Multi-select: add to set
        st.session_state.selected_options[category].add(choice)
    else:
        # Single-select: replace set with single item
        st.session_state.selected_options[category] = {choice}


def remove_option_selection(category: str, choice: str):
    """
    Remove an option selection

    Args:
        category: Category name
        choice: Choice name to remove
    """
    if category in st.session_state.selected_options:
        st.session_state.selected_options[category].discard(choice)

        # Clean up empty sets
        if not st.session_state.selected_options[category]:
            del st.session_state.selected_options[category]


def clear_category_selections(category: str):
    """Clear all selections for a category"""
    if category in st.session_state.selected_options:
        del st.session_state.selected_options[category]


def get_selected_choices(category: str) -> Set[str]:
    """
    Get selected choices for a category

    Args:
        category: Category name

    Returns:
        Set of selected choice names
    """
    return st.session_state.selected_options.get(category, set())


def is_choice_selected(category: str, choice: str) -> bool:
    """Check if a choice is selected"""
    return choice in get_selected_choices(category)


def get_total_combinations() -> int:
    """
    Calculate total number of simulation combinations

    Returns:
        Number of combinations that will be generated
    """
    total = 1

    # Multiply by number of archetypes
    archetypes = st.session_state.run_config.get('archetypes', [])
    if archetypes:
        total *= len(archetypes)

    # Multiply by number of choices in each category
    for choices in st.session_state.selected_options.values():
        if choices:
            total *= len(choices)

    return total
```

---

### Step 2: Update MIDDLE Panel for Multi-Select (60 min)

**File:** `src/ui/middle_panel.py`

Add multi-select UI:

```python
def render_middle_panel():
    """Render MIDDLE panel with multi-select support"""
    st.header("2️⃣ Select Options")

    if 'options_db' not in st.session_state:
        st.info("👈 Load HTAP options in the left panel first")
        return

    # Import state manager functions
    from src.ui.state_manager import (
        is_choice_selected,
        add_option_selection,
        remove_option_selection,
        clear_category_selections,
        get_selected_choices
    )

    # Selection mode toggle
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Selection Mode")
    with col2:
        multi_mode = st.session_state.get('multi_select_mode', False)
        mode_icon = "🔢" if multi_mode else "1️⃣"
        mode_text = "Multi" if multi_mode else "Single"
        st.metric(mode_icon, mode_text)

    if st.button(
        "🔄 Switch to " + ("Single" if multi_mode else "Multi") + " Select",
        use_container_width=True
    ):
        from src.ui.state_manager import toggle_selection_mode
        toggle_selection_mode()
        st.rerun()

    if multi_mode:
        st.info("💡 Multi-select mode: Click options to add/remove. Generates parametric runs.")
    else:
        st.info("💡 Single-select mode: Click to select one option per category.")

    st.divider()

    # ... existing category selector ...

    if selected_category:
        category = st.session_state.options_db.categories[selected_category]
        selected_choices = get_selected_choices(selected_category)

        # Category header
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.subheader(f"Options in {selected_category}")
        with col2:
            if selected_choices:
                st.metric("Selected", len(selected_choices))
        with col3:
            if selected_choices and st.button("🗑️ Clear", key=f"clear_{selected_category}"):
                clear_category_selections(selected_category)
                st.rerun()

        # Show selected options summary
        if selected_choices:
            with st.expander("📋 Selected Options", expanded=False):
                for choice in sorted(selected_choices):
                    col_a, col_b = st.columns([4, 1])
                    with col_a:
                        st.write(f"✅ {choice}")
                    with col_b:
                        if st.button("❌", key=f"remove_{selected_category}_{choice}"):
                            remove_option_selection(selected_category, choice)
                            st.rerun()

        st.divider()

        # Get cost info
        cost_source = st.session_state.run_config.get('cost_source')
        cost_resolver = st.session_state.get('cost_resolver')

        # Display all options
        for choice_name, choice in category.options.items():
            is_selected = is_choice_selected(selected_category, choice_name)

            # Option row
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                # Selection button
                button_icon = "✅" if is_selected else "⬜"
                button_label = f"{button_icon} {choice_name}"

                if st.button(
                    button_label,
                    key=f"opt_{selected_category}_{choice_name}",
                    use_container_width=True
                ):
                    if is_selected:
                        remove_option_selection(selected_category, choice_name)
                    else:
                        add_option_selection(selected_category, choice_name)
                    st.rerun()

            with col2:
                # Cost display
                if cost_resolver and choice.costs:
                    total_cost, _ = cost_resolver.resolve_option_cost(choice, cost_source)
                    if total_cost > 0:
                        st.metric("Cost", f"${total_cost:,.0f}")
                    else:
                        st.caption("No cost")
                else:
                    st.caption("—")

            with col3:
                # Quick info
                if choice.description:
                    st.caption("ℹ️")

            # Description
            if choice.description:
                st.caption(choice.description)

            # Cost breakdown (expandable)
            if cost_resolver and choice.costs and is_selected:
                total_cost, details = cost_resolver.resolve_option_cost(choice, cost_source)
                if details:
                    with st.expander(f"💰 Cost Details - {choice_name}"):
                        for component in details:
                            if not component.get('error'):
                                st.write(
                                    f"**{component['description']}**: "
                                    f"${component['total_cost']:,.2f}"
                                )

            st.divider()
```

---

### Step 3: Create Selected Options Summary Widget (45 min)

**File:** `src/ui/right_panel.py`

Update RIGHT panel to show all selections:

```python
def render_right_panel():
    """Render RIGHT panel with selections summary"""
    st.header("3️⃣ Review & Export")

    from src.ui.state_manager import get_total_combinations

    # ... existing validation summary ...

    st.divider()

    # Selections summary
    st.subheader("📋 Selected Options")

    selected_options = st.session_state.get('selected_options', {})

    if not selected_options:
        st.info("No options selected yet")
    else:
        # Show total combinations
        total_combos = get_total_combinations()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Categories", len(selected_options))
        with col2:
            st.metric("Total Runs", total_combos)

        if total_combos > 100:
            st.warning(f"⚠️ {total_combos} combinations will take significant time to run")
        elif total_combos > 500:
            st.error(f"❌ {total_combos} combinations may be too many. Consider reducing selections.")

        # List all selections
        with st.expander("📄 All Selections", expanded=True):
            for category, choices in sorted(selected_options.items()):
                if choices:
                    st.markdown(f"**{category}**")
                    for choice in sorted(choices):
                        st.write(f"  • {choice}")

    # ... existing export button ...
```

---

### Step 4: Update Export Format Helper (15 min)

**File:** `src/utils/export_helpers.py`

Add function to format selections for .run file:

```python
"""
Helper functions for exporting configurations
"""

from typing import Dict, Set


def format_upgrades_section(selected_options: Dict[str, Set[str]]) -> str:
    """
    Format selected options as Upgrades section for .run file

    Args:
        selected_options: Dict mapping category -> set of choices

    Returns:
        Formatted string for Upgrades section
    """
    lines = ["Upgrades_START"]

    for category in sorted(selected_options.keys()):
        choices = selected_options[category]
        if choices:
            # Join choices with ", "
            choices_str = ", ".join(sorted(choices))
            lines.append(f"  {category} = {choices_str}")

    lines.append("Upgrades_END")

    return "\n".join(lines)


def count_combinations(selected_options: Dict[str, Set[str]]) -> int:
    """
    Count total number of combinations

    Args:
        selected_options: Dict mapping category -> set of choices

    Returns:
        Total number of combinations
    """
    total = 1
    for choices in selected_options.values():
        if choices:
            total *= len(choices)
    return total
```

---

### Step 5: Create Unit Tests (30 min)

**File:** `tests/test_multi_select.py`

```python
"""
Unit tests for multi-select functionality
"""

import pytest
from src.ui.state_manager import (
    add_option_selection,
    remove_option_selection,
    get_selected_choices,
    is_choice_selected,
    clear_category_selections,
    get_total_combinations
)
from src.utils.export_helpers import format_upgrades_section, count_combinations


class TestMultiSelectState:
    """Test multi-select state management"""

    def test_add_single_selection(self):
        """Test adding single selection"""
        # Mock session state
        import streamlit as st
        st.session_state.selected_options = {}
        st.session_state.multi_select_mode = False

        add_option_selection("Opt-Windows", "Choice1")

        assert "Opt-Windows" in st.session_state.selected_options
        assert "Choice1" in st.session_state.selected_options["Opt-Windows"]

    def test_add_multiple_selections(self):
        """Test adding multiple selections in multi-select mode"""
        import streamlit as st
        st.session_state.selected_options = {}
        st.session_state.multi_select_mode = True

        add_option_selection("Opt-Windows", "Choice1")
        add_option_selection("Opt-Windows", "Choice2")
        add_option_selection("Opt-Windows", "Choice3")

        choices = get_selected_choices("Opt-Windows")
        assert len(choices) == 3
        assert "Choice1" in choices
        assert "Choice2" in choices
        assert "Choice3" in choices

    def test_single_select_replaces(self):
        """Test that single-select mode replaces previous selection"""
        import streamlit as st
        st.session_state.selected_options = {}
        st.session_state.multi_select_mode = False

        add_option_selection("Opt-Windows", "Choice1")
        add_option_selection("Opt-Windows", "Choice2")

        choices = get_selected_choices("Opt-Windows")
        assert len(choices) == 1
        assert "Choice2" in choices

    def test_remove_selection(self):
        """Test removing a selection"""
        import streamlit as st
        st.session_state.selected_options = {
            "Opt-Windows": {"Choice1", "Choice2", "Choice3"}
        }

        remove_option_selection("Opt-Windows", "Choice2")

        choices = get_selected_choices("Opt-Windows")
        assert len(choices) == 2
        assert "Choice2" not in choices

    def test_clear_category(self):
        """Test clearing all selections for a category"""
        import streamlit as st
        st.session_state.selected_options = {
            "Opt-Windows": {"Choice1", "Choice2"},
            "Opt-Walls": {"WallChoice1"}
        }

        clear_category_selections("Opt-Windows")

        assert "Opt-Windows" not in st.session_state.selected_options
        assert "Opt-Walls" in st.session_state.selected_options


class TestCombinationCounting:
    """Test counting total combinations"""

    def test_single_category_single_choice(self):
        """Test counting with one category, one choice"""
        import streamlit as st
        st.session_state.selected_options = {
            "Opt-Windows": {"Choice1"}
        }
        st.session_state.run_config = {'archetypes': ['arch1.h2k']}

        total = get_total_combinations()
        assert total == 1

    def test_single_category_multiple_choices(self):
        """Test counting with one category, multiple choices"""
        import streamlit as st
        st.session_state.selected_options = {
            "Opt-Windows": {"Choice1", "Choice2", "Choice3"}
        }
        st.session_state.run_config = {'archetypes': ['arch1.h2k']}

        total = get_total_combinations()
        assert total == 3

    def test_multiple_categories(self):
        """Test counting with multiple categories"""
        import streamlit as st
        st.session_state.selected_options = {
            "Opt-Windows": {"Choice1", "Choice2"},
            "Opt-Walls": {"Wall1", "Wall2", "Wall3"},
            "Opt-Ceilings": {"Ceil1"}
        }
        st.session_state.run_config = {'archetypes': ['arch1.h2k']}

        total = get_total_combinations()
        assert total == 2 * 3 * 1  # 6

    def test_with_multiple_archetypes(self):
        """Test counting with multiple archetypes"""
        import streamlit as st
        st.session_state.selected_options = {
            "Opt-Windows": {"Choice1", "Choice2"}
        }
        st.session_state.run_config = {
            'archetypes': ['arch1.h2k', 'arch2.h2k', 'arch3.h2k']
        }

        total = get_total_combinations()
        assert total == 3 * 2  # 6


class TestExportFormat:
    """Test export format for .run files"""

    def test_format_single_category(self):
        """Test formatting single category"""
        selected = {
            "Opt-Windows": {"Choice1", "Choice2"}
        }

        output = format_upgrades_section(selected)

        assert "Upgrades_START" in output
        assert "Upgrades_END" in output
        assert "Opt-Windows = Choice1, Choice2" in output or \
               "Opt-Windows = Choice2, Choice1" in output

    def test_format_multiple_categories(self):
        """Test formatting multiple categories"""
        selected = {
            "Opt-Windows": {"WinChoice1"},
            "Opt-Walls": {"Wall1", "Wall2"},
            "Opt-Ceilings": {"Ceil1"}
        }

        output = format_upgrades_section(selected)

        assert "Opt-Windows = WinChoice1" in output
        assert "Opt-Walls" in output
        assert "Wall1" in output
        assert "Wall2" in output
        assert "Opt-Ceilings = Ceil1" in output

    def test_count_combinations_helper(self):
        """Test standalone combination counter"""
        selected = {
            "Opt-Windows": {"Choice1", "Choice2"},
            "Opt-Walls": {"Wall1", "Wall2", "Wall3"}
        }

        count = count_combinations(selected)
        assert count == 2 * 3  # 6
```

---

## Acceptance Criteria

✅ **Multi-select mode toggle** works correctly
✅ **Multiple choices per category** can be selected/deselected
✅ **Selected options display** in both MIDDLE and RIGHT panels
✅ **Total combinations** calculated correctly
✅ **Clear category** function works
✅ **Export format** matches .run file spec (comma-separated)
✅ **Warning shown** for large number of combinations
✅ **Tests pass** for all state management

---

## Testing Checklist

```bash
# Run unit tests
pytest tests/test_multi_select.py -v -s

# Manual testing in Streamlit:
# 1. Toggle between single and multi-select modes
# 2. Select multiple options in one category
# 3. Verify combinations count updates
# 4. Clear a category
# 5. Export and verify .run format
```

---

## Common Issues & Solutions

### Issue: State not persisting across reruns
**Solution:** Ensure all state updates use `st.session_state` directly

### Issue: Combinations count incorrect
**Solution:** Verify using `len(choices)` for each category, multiply all together

### Issue: Export format wrong
**Solution:** Check that choices are joined with `", "` (comma space)

---

## Next Steps

After completing this task:
1. Test with various multi-select scenarios
2. Verify export format matches HTAP expectations
3. Proceed to **Task 2.5: Advanced Search Features**

---

## Time Tracking

- Session state updates: 30 min
- MIDDLE panel multi-select UI: 60 min
- RIGHT panel summary: 45 min
- Export helpers: 15 min
- Unit tests: 30 min
- **Total: ~3 hours**
