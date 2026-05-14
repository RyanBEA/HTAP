"""
Cost summary visualization widget
Displays cost breakdowns, charts, and export options
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Set

from src.utils.cost_report import CostReportGenerator, ConfigurationCost


def render_cost_summary():
    """
    Render comprehensive cost summary for selected configuration
    Displays totals, charts, breakdowns, and export options
    """
    # Import help content
    from src.ui.help_content import show_help_button

    # Get required session state objects
    if 'cost_report_gen' not in st.session_state:
        st.error("Cost report generator not initialized. Please restart the application.")
        st.info("Cost features require HTAPUnitCosts.json. Check that it's available at C:/HTAP/")
        return

    cost_gen: CostReportGenerator = st.session_state.cost_report_gen
    selected_options: Dict[str, Set[str]] = st.session_state.get('selected_options', {})
    cost_source = st.session_state.run_config.get('cost_source', 'LEEP-ON-Ottawa')

    # Check if any options are selected
    if not selected_options or all(len(opts) == 0 for opts in selected_options.values()):
        st.info("💰 No options selected. Select options from the middle panel to see cost estimates.")
        show_help_button("cost_summary")
        return

    # Calculate configuration cost
    with st.spinner("Calculating costs..."):
        config_cost = cost_gen.calculate_configuration_cost(selected_options, cost_source)

    # Display total costs
    col_head1, col_head2 = st.columns([5, 1])
    with col_head1:
        st.subheader("💵 Total Costs")
    with col_head2:
        show_help_button("cost_summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Materials",
            f"${config_cost.total_materials:,.0f}",
            help="Total materials cost"
        )

    with col2:
        st.metric(
            "Labour",
            f"${config_cost.total_labour:,.0f}",
            help="Total labour cost"
        )

    with col3:
        st.metric(
            "Total Cost",
            f"${config_cost.total_cost:,.0f}",
            help="Combined materials + labour"
        )

    st.caption(f"📍 Cost source: {cost_source}")

    st.markdown("---")

    # Check if there are category costs to display
    if not config_cost.category_costs:
        st.warning("No cost data available for selected options. Some options may not have cost components assigned.")
        return

    # Cost visualizations
    st.subheader("📊 Cost Distribution")

    # Create two tabs for different visualizations
    viz_tab1, viz_tab2 = st.tabs(["By Category", "Materials vs Labour"])

    with viz_tab1:
        _render_category_pie_chart(config_cost)

    with viz_tab2:
        _render_materials_labour_chart(config_cost)

    st.markdown("---")

    # Detailed category breakdown
    st.subheader("📋 Cost Breakdown by Category")

    category_df = cost_gen.get_category_summary(config_cost)

    if not category_df.empty:
        # Format currency columns
        display_df = category_df.copy()
        display_df['materials'] = display_df['materials'].apply(lambda x: f"${x:,.2f}")
        display_df['labour'] = display_df['labour'].apply(lambda x: f"${x:,.2f}")
        display_df['total_cost'] = display_df['total_cost'].apply(lambda x: f"${x:,.2f}")

        # Display as table
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'category': 'Category',
                'options_count': st.column_config.NumberColumn('# Options', format="%d"),
                'options': 'Selected Options',
                'materials': 'Materials',
                'labour': 'Labour',
                'total_cost': 'Total Cost',
                'component_count': st.column_config.NumberColumn('# Components', format="%d")
            }
        )

    st.markdown("---")

    # Top cost components
    st.subheader("🔝 Top Cost Components")

    if not config_cost.component_details.empty:
        # Slider to select number of top components
        num_components = len(config_cost.component_details)

        # Only show slider if there are multiple components
        if num_components > 1:
            top_n = st.slider(
                "Number of top components to display",
                min_value=min(5, num_components),
                max_value=min(20, num_components),
                value=min(10, num_components),
                step=1
            )
        else:
            # Single component - no slider needed
            top_n = 1
            st.caption("Showing the only cost component available")

        top_components = cost_gen.get_top_components(config_cost, top_n)

        if not top_components.empty:
            # Format for display
            display_top = top_components.copy()
            display_top['materials_formatted'] = display_top['total_materials'].apply(lambda x: f"${x:,.2f}")
            display_top['labour_formatted'] = display_top['total_labour'].apply(lambda x: f"${x:,.2f}")
            display_top['total_formatted'] = display_top['total_cost'].apply(lambda x: f"${x:,.2f}")

            st.dataframe(
                display_top[['component_id', 'description', 'quantity', 'units', 'materials_formatted', 'labour_formatted', 'total_formatted', 'source_used']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    'component_id': 'Component ID',
                    'description': 'Description',
                    'quantity': st.column_config.NumberColumn('Quantity', format="%.2f"),
                    'units': 'Units',
                    'materials_formatted': 'Materials',
                    'labour_formatted': 'Labour',
                    'total_formatted': 'Total Cost',
                    'source_used': 'Source'
                }
            )
    else:
        st.info("No component details available")

    st.markdown("---")

    # Export options
    st.subheader("💾 Export Options")

    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        # Download summary as markdown
        summary_text = cost_gen.generate_cost_summary_text(config_cost)

        st.download_button(
            label="📄 Download Summary (Markdown)",
            data=summary_text,
            file_name="htap_cost_summary.md",
            mime="text/markdown",
            use_container_width=True,
            help="Download cost summary as markdown document"
        )

    with col_exp2:
        # Download details as CSV
        if not config_cost.component_details.empty:
            csv_data = cost_gen.export_to_csv(config_cost)

            st.download_button(
                label="📊 Download Details (CSV)",
                data=csv_data,
                file_name="htap_cost_details.csv",
                mime="text/csv",
                use_container_width=True,
                help="Download detailed component costs as CSV"
            )
        else:
            st.button(
                "📊 Download Details (CSV)",
                disabled=True,
                use_container_width=True,
                help="No component details available"
            )


def _render_category_pie_chart(config_cost: ConfigurationCost):
    """Render pie chart showing cost distribution by category"""

    if not config_cost.category_costs:
        st.info("No category cost data to visualize")
        return

    # Prepare data for pie chart
    pie_data = []
    for cat_cost in config_cost.category_costs:
        pie_data.append({
            'category': cat_cost.category.replace('Opt-', ''),
            'cost': cat_cost.total_cost
        })

    pie_df = pd.DataFrame(pie_data)

    # Create pie chart
    fig_pie = px.pie(
        pie_df,
        values='cost',
        names='category',
        title='Cost Distribution by Category',
        hole=0.3  # Donut chart
    )

    # Update layout
    fig_pie.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Cost: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
    )

    fig_pie.update_layout(
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )

    st.plotly_chart(fig_pie, use_container_width=True)


def _render_materials_labour_chart(config_cost: ConfigurationCost):
    """Render stacked bar chart showing materials vs labour by category"""

    if not config_cost.category_costs:
        st.info("No category cost data to visualize")
        return

    # Prepare data for stacked bar chart
    bar_data = []
    for cat_cost in config_cost.category_costs:
        category_name = cat_cost.category.replace('Opt-', '')
        bar_data.append({
            'category': category_name,
            'type': 'Materials',
            'cost': cat_cost.total_materials
        })
        bar_data.append({
            'category': category_name,
            'type': 'Labour',
            'cost': cat_cost.total_labour
        })

    bar_df = pd.DataFrame(bar_data)

    # Create stacked bar chart
    fig_bar = px.bar(
        bar_df,
        x='category',
        y='cost',
        color='type',
        title='Materials vs Labour by Category',
        barmode='stack',
        color_discrete_map={
            'Materials': '#1f77b4',
            'Labour': '#ff7f0e'
        }
    )

    # Update layout
    fig_bar.update_layout(
        xaxis_title="Category",
        yaxis_title="Cost ($)",
        legend_title="Cost Type",
        hovermode='x unified'
    )

    fig_bar.update_traces(
        hovertemplate='%{y:$,.2f}<extra></extra>'
    )

    st.plotly_chart(fig_bar, use_container_width=True)


def render_cost_comparison():
    """
    Render cost comparison across multiple cost sources
    Allows selecting multiple sources and comparing totals
    """
    st.subheader("⚖️ Cost Source Comparison")

    # Get required session state objects
    if 'cost_report_gen' not in st.session_state:
        st.error("Cost report generator not initialized. Please restart the application.")
        return

    cost_gen: CostReportGenerator = st.session_state.cost_report_gen
    selected_options: Dict[str, Set[str]] = st.session_state.get('selected_options', {})

    # Check if any options are selected
    if not selected_options or all(len(opts) == 0 for opts in selected_options.values()):
        st.info("Select options to compare costs across different sources.")
        return

    # Get available sources
    available_sources = cost_gen.cost_resolver.get_available_sources()

    if not available_sources:
        st.warning("No cost sources available")
        return

    # Multi-select for sources
    selected_sources = st.multiselect(
        "Select cost sources to compare",
        options=available_sources,
        default=[st.session_state.run_config.get('cost_source', 'LEEP-ON-Ottawa')],
        help="Compare costs across different regional cost databases"
    )

    if not selected_sources:
        st.info("Select at least one cost source to compare")
        return

    # Calculate comparison
    with st.spinner("Comparing costs across sources..."):
        comparison_df = cost_gen.calculate_cost_comparison(selected_options, selected_sources)

    if comparison_df.empty:
        st.warning("No comparison data available")
        return

    # Display comparison table
    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'source': 'Cost Source',
            'total_materials': st.column_config.NumberColumn('Materials', format="$%.2f"),
            'total_labour': st.column_config.NumberColumn('Labour', format="$%.2f"),
            'total_cost': st.column_config.NumberColumn('Total Cost', format="$%.2f"),
            'component_count': st.column_config.NumberColumn('Components', format="%d")
        }
    )

    # Bar chart comparing sources
    if len(selected_sources) > 1:
        st.subheader("Cost Comparison Chart")

        fig_comparison = px.bar(
            comparison_df,
            x='source',
            y=['total_materials', 'total_labour'],
            title='Cost Comparison by Source',
            barmode='stack',
            labels={
                'value': 'Cost ($)',
                'source': 'Cost Source',
                'variable': 'Cost Type'
            }
        )

        # Update legend labels
        fig_comparison.for_each_trace(
            lambda t: t.update(name=t.name.replace('total_materials', 'Materials').replace('total_labour', 'Labour'))
        )

        fig_comparison.update_layout(
            xaxis_title="Cost Source",
            yaxis_title="Cost ($)",
            legend_title="Cost Type",
            hovermode='x unified'
        )

        st.plotly_chart(fig_comparison, use_container_width=True)

        # Show cost differences
        if len(selected_sources) == 2:
            source1, source2 = selected_sources[0], selected_sources[1]
            cost1 = comparison_df[comparison_df['source'] == source1]['total_cost'].values[0]
            cost2 = comparison_df[comparison_df['source'] == source2]['total_cost'].values[0]
            diff = cost2 - cost1
            pct_diff = (diff / cost1 * 100) if cost1 > 0 else 0

            st.metric(
                f"Cost Difference ({source2} vs {source1})",
                f"${diff:,.2f}",
                f"{pct_diff:+.1f}%"
            )
