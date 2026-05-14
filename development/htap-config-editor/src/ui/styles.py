"""
Custom styles and UI polish for HTAP Configuration Editor

Provides custom CSS styling and footer component.
"""

import streamlit as st


def apply_custom_styles() -> None:
    """
    Apply custom CSS styles to improve UI appearance

    Styles applied:
        - Button spacing and sizing
        - Metric font sizes
        - Expander header styling
        - Divider visibility
        - Alert box styling
        - General spacing improvements
    """
    st.markdown("""
    <style>
        /* Main container padding */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 4rem;
            max-width: 100%;
            overflow-x: hidden;
        }

        /* Header styling */
        h1 {
            padding-bottom: 1rem;
            border-bottom: 2px solid #e0e0e0;
            margin-bottom: 1.5rem;
        }

        h2 {
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }

        h3 {
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }

        /* Button styling */
        .stButton button {
            width: 100%;
            margin: 2px 0;
            font-weight: 500;
            transition: all 0.2s ease;
        }

        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        /* Download button special styling */
        .stDownloadButton button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
        }

        /* Metric styling */
        [data-testid="stMetric"] {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #e0e0e0;
        }

        [data-testid="stMetricValue"] {
            font-size: 24px;
            font-weight: 600;
            color: #1f2937;
        }

        [data-testid="stMetricLabel"] {
            font-size: 14px;
            font-weight: 500;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Expander styling */
        .streamlit-expanderHeader {
            font-weight: 600;
            font-size: 16px;
            color: #1f2937;
            background-color: #f8f9fa;
            border-radius: 0.5rem;
            padding: 0.75rem 1rem;
        }

        .streamlit-expanderHeader:hover {
            background-color: #e9ecef;
        }

        /* Divider styling */
        hr {
            margin: 1.5rem 0;
            border: none;
            border-top: 2px solid #e0e0e0;
            opacity: 1;
        }

        /* Alert boxes */
        .stAlert {
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid;
            margin: 0.5rem 0;
        }

        /* Error alert */
        .stAlert[data-baseweb="notification"][kind="error"] {
            background-color: #fee;
            border-left-color: #dc3545;
        }

        /* Warning alert */
        .stAlert[data-baseweb="notification"][kind="warning"] {
            background-color: #fff3cd;
            border-left-color: #ffc107;
        }

        /* Success alert */
        .stAlert[data-baseweb="notification"][kind="success"] {
            background-color: #d4edda;
            border-left-color: #28a745;
        }

        /* Info alert */
        .stAlert[data-baseweb="notification"][kind="info"] {
            background-color: #d1ecf1;
            border-left-color: #17a2b8;
        }

        /* Code blocks */
        .stCodeBlock {
            border-radius: 0.5rem;
            border: 1px solid #e0e0e0;
        }

        /* Text input */
        .stTextInput input {
            border-radius: 0.5rem;
            border: 1px solid #d1d5db;
            padding: 0.5rem 0.75rem;
        }

        .stTextInput input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        /* Select box */
        .stSelectbox > div > div {
            border-radius: 0.5rem;
        }

        /* Multiselect */
        .stMultiSelect > div > div {
            border-radius: 0.5rem;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background-color: #f8f9fa;
            padding: 0.5rem;
            border-radius: 0.5rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 0.375rem;
            padding: 0.4rem 0.6rem;
            font-weight: 500;
            white-space: nowrap;
            overflow: visible;
            min-width: fit-content;
        }

        /* Spinner */
        .stSpinner > div {
            border-top-color: #667eea;
        }

        /* Caption */
        .caption {
            color: #6b7280;
            font-size: 14px;
            margin-top: 0.25rem;
        }

        /* Sidebar */
        .css-1d391kg {
            padding: 2rem 1rem;
        }

        /* Remove extra padding from columns and prevent overflow */
        [data-testid="column"] {
            padding: 0 0.25rem;
            min-width: 0;
            overflow-x: auto;
        }

        [data-testid="column"]:first-child {
            padding-left: 0;
        }

        [data-testid="column"]:last-child {
            padding-right: 0;
        }

        /* Ensure text wrapping in headers and prevent truncation */
        h1, h2, h3, h4, h5, h6 {
            word-wrap: break-word;
            overflow-wrap: break-word;
            white-space: normal !important;
        }

        /* Balanced text display - prevent excessive truncation without breaking layout */
        p, span {
            overflow-wrap: break-word;
        }

        /* Prevent tab text from being truncated */
        button[role="tab"] {
            white-space: nowrap;
            font-size: 0.9rem;
        }

        /* Footer */
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #f8f9fa;
            border-top: 1px solid #e0e0e0;
            padding: 0.75rem 2rem;
            text-align: center;
            font-size: 14px;
            color: #6b7280;
            z-index: 999;
        }

        .footer a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }

        .footer a:hover {
            text-decoration: underline;
        }
    </style>
    """, unsafe_allow_html=True)


def show_footer() -> None:
    """
    Display application footer with branding and links

    Shows:
        - Application name
        - Technology (Streamlit)
        - Documentation link
        - Version info (if available)
    """
    footer_html = """
    <div class="footer">
        <strong>HTAP Configuration Editor</strong> |
        Built with <a href="https://streamlit.io" target="_blank">Streamlit</a> |
        <a href="https://github.com/NRCan-IETS-CE-O-HBC/HTAP" target="_blank">Documentation</a> |
        <span style="color: #9ca3af;">v1.0.0</span>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)


def show_section_divider(label: str = None, icon: str = None) -> None:
    """
    Show a styled section divider with optional label and icon

    Args:
        label: Optional section label
        icon: Optional emoji icon

    Usage:
        show_section_divider()
        show_section_divider("Configuration", "⚙️")
    """
    if label:
        if icon:
            st.markdown(f"### {icon} {label}")
        else:
            st.markdown(f"### {label}")
    st.markdown("---")


def show_metric_card(label: str, value: str, delta: str = None, help_text: str = None) -> None:
    """
    Show a styled metric card

    Args:
        label: Metric label
        value: Metric value
        delta: Optional delta value (change indicator)
        help_text: Optional help text

    Usage:
        show_metric_card("Total Runs", "42")
        show_metric_card("Cost", "$1,234", delta="+$200")
    """
    st.metric(
        label=label,
        value=value,
        delta=delta,
        help=help_text
    )


def apply_compact_mode() -> None:
    """
    Apply compact mode styling for denser layouts

    Reduces spacing between elements for more information density.
    """
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        h1, h2, h3 {
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }

        hr {
            margin: 0.75rem 0;
        }

        .stButton button {
            margin: 1px 0;
            padding: 0.4rem 0.8rem;
        }
    </style>
    """, unsafe_allow_html=True)
