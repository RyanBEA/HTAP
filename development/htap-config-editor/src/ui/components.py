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
