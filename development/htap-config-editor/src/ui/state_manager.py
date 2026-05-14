"""
Streamlit session state management
"""

import streamlit as st
from typing import Dict, List, Optional, Any, Set


def initialize_session_state():
    """Initialize all session state variables"""

    # Run configuration
    if 'run_config' not in st.session_state:
        st.session_state.run_config = {
            'archetypes': [],
            'location': None,
            'ruleset': 'as-found',
            'cost_source': 'LEEP-ON-Ottawa'  # Default cost source
        }

    # Selection mode
    if 'multi_select_mode' not in st.session_state:
        st.session_state.multi_select_mode = False

    # Selected options - now supports multiple choices per category
    # Format: Dict[category_name, Set[choice_name]]
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


def toggle_selection_mode():
    """Toggle between single and multi-select modes"""
    st.session_state.multi_select_mode = not st.session_state.multi_select_mode

    # When switching to single-select, keep only first selection per category
    if not st.session_state.multi_select_mode:
        for category, choices in st.session_state.selected_options.items():
            if isinstance(choices, set) and len(choices) > 1:
                # Keep only first choice
                st.session_state.selected_options[category] = {list(choices)[0]}


def add_option_to_run(category: str, choice: str):
    """
    Add an option to the run configuration

    Args:
        category: Option category (e.g., 'Opt-Windows')
        choice: Choice name within category
    """
    if category not in st.session_state.selected_options:
        st.session_state.selected_options[category] = set()

    if st.session_state.multi_select_mode:
        # Multi-select: add to set
        st.session_state.selected_options[category].add(choice)
    else:
        # Single-select: replace set with single item
        st.session_state.selected_options[category] = {choice}


def remove_option_from_run(category: str):
    """Remove an option from the run configuration"""
    if category in st.session_state.selected_options:
        del st.session_state.selected_options[category]


def remove_option_selection(category: str, choice: str):
    """
    Remove a specific choice from a category

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


def get_selected_option(category: str) -> Optional[str]:
    """
    Get the currently selected choice for a category (single-select compatibility)

    Returns:
        First choice if any are selected, None otherwise
    """
    choices = st.session_state.selected_options.get(category)
    if choices and len(choices) > 0:
        return list(choices)[0]
    return None


def get_selected_choices(category: str) -> Set[str]:
    """
    Get selected choices for a category

    Args:
        category: Category name

    Returns:
        Set of selected choice names
    """
    choices = st.session_state.selected_options.get(category, set())
    # Ensure it's a set (handles migration from old single-select format)
    if isinstance(choices, str):
        return {choices}
    return choices if isinstance(choices, set) else set()


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


def is_choice_selected(category: str, choice: str) -> bool:
    """
    Check if a specific choice is currently selected

    Args:
        category: Option category (e.g., 'Opt-Windows')
        choice: Choice name within category

    Returns:
        True if the choice is selected, False otherwise
    """
    choices = get_selected_choices(category)
    return choice in choices


def add_option_selection(category: str, choice: str):
    """
    Alias for add_option_to_run for consistency

    Args:
        category: Option category (e.g., 'Opt-Windows')
        choice: Choice name within category
    """
    add_option_to_run(category, choice)


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
