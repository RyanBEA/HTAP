# Task 3.3: Cost Summary Report

**Duration:** 2-3 hours
**Phase:** 3 - Export & Polish
**Dependencies:** Task 2.2 (Cost Resolution), Task 3.1 (Export Run File)
**Completion Criteria:** Cost reports generated, charts displayed, CSV export working

---

## Objective

Generate comprehensive cost summary reports for the selected configuration, including total costs, per-category breakdowns, component-level details, and visual cost charts. Enable export to CSV for further analysis.

---

## What You'll Build

1. Cost calculator for entire configuration
2. Per-category cost breakdown
3. Component-level cost details
4. Visual cost charts (pie chart, bar chart)
5. Cost comparison (multiple options)
6. CSV export of cost data
7. Unit tests

---

## Context: Cost Calculation

From Task 2.2, we have `CostResolver` that can:
- Get component costs from cost database
- Handle source inheritance
- Calculate total cost per option

Now we need to:
- Aggregate costs across all selected options
- Break down by category, component, material/labour
- Visualize costs for user understanding
- Export for external analysis

---

## Step-by-Step Implementation

### Step 1: Create Cost Report Generator (75 min)

**File:** `src/utils/cost_report.py`

```python
"""
Cost summary report generator
Calculates and formats costs for selected configurations
"""

from typing import Dict, Set, List, Tuple
from dataclasses import dataclass
import pandas as pd

from src.models.option import OptionsDatabase
from src.utils.cost_resolver import CostResolver


@dataclass
class CategoryCost:
    """Cost summary for a category"""
    category: str
    options: List[str]
    total_materials: float
    total_labour: float
    total_cost: float
    component_count: int


@dataclass
class ConfigurationCost:
    """Total cost summary for configuration"""
    total_materials: float
    total_labour: float
    total_cost: float
    category_costs: List[CategoryCost]
    component_details: pd.DataFrame


class CostReportGenerator:
    """
    Generates cost reports for configurations
    """

    def __init__(
        self,
        options_db: OptionsDatabase,
        cost_resolver: CostResolver
    ):
        """
        Initialize cost report generator

        Args:
            options_db: Loaded options database
            cost_resolver: Cost resolver from Task 2.2
        """
        self.options_db = options_db
        self.cost_resolver = cost_resolver

    def calculate_configuration_cost(
        self,
        selected_options: Dict[str, Set[str]],
        cost_source: str
    ) -> ConfigurationCost:
        """
        Calculate total cost for configuration

        Args:
            selected_options: Dict mapping category -> set of choices
            cost_source: Cost source to use

        Returns:
            ConfigurationCost with all cost details
        """
        category_costs = []
        all_components = []

        total_materials = 0.0
        total_labour = 0.0

        # Calculate costs per category
        for category_name, choices in selected_options.items():
            if category_name not in self.options_db.categories:
                continue

            category = self.options_db.categories[category_name]

            cat_materials = 0.0
            cat_labour = 0.0
            cat_components = 0

            # For multiple choices, calculate average or sum
            # (Here we'll sum - this represents "all options selected")
            for choice_name in choices:
                if choice_name not in category.options:
                    continue

                choice = category.options[choice_name]

                # Get cost for this option
                option_cost, details = self.cost_resolver.resolve_option_cost(
                    choice,
                    cost_source
                )

                # Aggregate
                for component in details:
                    if not component.get('error'):
                        cat_materials += component['unit_cost_materials'] * component['quantity']
                        cat_labour += component['unit_cost_labour'] * component['quantity']
                        cat_components += 1

                        # Add to all components list
                        all_components.append({
                            'category': category_name,
                            'option': choice_name,
                            'component': component['component_id'],
                            'description': component['description'],
                            'quantity': component['quantity'],
                            'units': component['units'],
                            'unit_cost_materials': component['unit_cost_materials'],
                            'unit_cost_labour': component['unit_cost_labour'],
                            'total_materials': component['unit_cost_materials'] * component['quantity'],
                            'total_labour': component['unit_cost_labour'] * component['quantity'],
                            'total_cost': component['total_cost'],
                            'source': component['source_used']
                        })

            # Create category cost summary
            category_costs.append(CategoryCost(
                category=category_name,
                options=sorted(choices),
                total_materials=cat_materials,
                total_labour=cat_labour,
                total_cost=cat_materials + cat_labour,
                component_count=cat_components
            ))

            total_materials += cat_materials
            total_labour += cat_labour

        # Create DataFrame of components
        components_df = pd.DataFrame(all_components) if all_components else pd.DataFrame()

        return ConfigurationCost(
            total_materials=total_materials,
            total_labour=total_labour,
            total_cost=total_materials + total_labour,
            category_costs=category_costs,
            component_details=components_df
        )

    def generate_cost_summary_text(
        self,
        config_cost: ConfigurationCost
    ) -> str:
        """
        Generate text summary of costs

        Args:
            config_cost: Configuration cost data

        Returns:
            Markdown-formatted cost summary
        """
        lines = []

        lines.append("# Cost Summary Report")
        lines.append("")

        # Total costs
        lines.append("## Total Costs")
        lines.append("")
        lines.append(f"- **Materials:** ${config_cost.total_materials:,.2f}")
        lines.append(f"- **Labour:** ${config_cost.total_labour:,.2f}")
        lines.append(f"- **Total:** ${config_cost.total_cost:,.2f}")
        lines.append("")

        # Cost by category
        lines.append("## Cost by Category")
        lines.append("")

        if config_cost.category_costs:
            # Sort by total cost descending
            sorted_cats = sorted(
                config_cost.category_costs,
                key=lambda c: c.total_cost,
                reverse=True
            )

            for cat in sorted_cats:
                if cat.total_cost > 0:
                    lines.append(f"### {cat.category}")
                    lines.append(f"- Options: {', '.join(cat.options)}")
                    lines.append(f"- Materials: ${cat.total_materials:,.2f}")
                    lines.append(f"- Labour: ${cat.total_labour:,.2f}")
                    lines.append(f"- **Total: ${cat.total_cost:,.2f}**")
                    lines.append(f"- Components: {cat.component_count}")
                    lines.append("")

        # Component details
        if not config_cost.component_details.empty:
            lines.append("## Top Cost Components")
            lines.append("")

            # Get top 10 most expensive components
            top_components = config_cost.component_details.nlargest(10, 'total_cost')

            for idx, row in top_components.iterrows():
                lines.append(f"- **{row['description']}** ({row['category']})")
                lines.append(f"  - Quantity: {row['quantity']} {row['units']}")
                lines.append(f"  - Cost: ${row['total_cost']:,.2f}")
                lines.append("")

        return "\n".join(lines)

    def export_to_csv(
        self,
        config_cost: ConfigurationCost
    ) -> str:
        """
        Export cost data to CSV format

        Args:
            config_cost: Configuration cost data

        Returns:
            CSV string
        """
        if config_cost.component_details.empty:
            return "No cost data available"

        return config_cost.component_details.to_csv(index=False)

    def calculate_cost_comparison(
        self,
        selected_options: Dict[str, Set[str]],
        cost_sources: List[str]
    ) -> pd.DataFrame:
        """
        Compare costs across multiple sources

        Args:
            selected_options: Selected options
            cost_sources: List of cost sources to compare

        Returns:
            DataFrame with comparison
        """
        comparison_data = []

        for source in cost_sources:
            config_cost = self.calculate_configuration_cost(
                selected_options,
                source
            )

            comparison_data.append({
                'cost_source': source,
                'total_materials': config_cost.total_materials,
                'total_labour': config_cost.total_labour,
                'total_cost': config_cost.total_cost,
                'categories': len(config_cost.category_costs)
            })

        return pd.DataFrame(comparison_data)
```

---

### Step 2: Create Cost Visualization Widget (60 min)

**File:** `src/ui/cost_summary_widget.py`

```python
"""
Cost summary visualization widget
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.utils.cost_report import CostReportGenerator


def render_cost_summary():
    """
    Render cost summary with charts
    """
    st.subheader("💰 Cost Summary")

    # Check dependencies
    if 'options_db' not in st.session_state:
        st.info("Load options database first")
        return

    if 'cost_resolver' not in st.session_state:
        st.info("Cost resolver not initialized")
        return

    # Initialize cost report generator
    if 'cost_report_gen' not in st.session_state:
        st.session_state.cost_report_gen = CostReportGenerator(
            st.session_state.options_db,
            st.session_state.cost_resolver
        )

    cost_gen = st.session_state.cost_report_gen

    # Get configuration
    selected_options = st.session_state.get('selected_options', {})
    cost_source = st.session_state.run_config.get('cost_source', 'LEEP-ON-Ottawa')

    if not selected_options:
        st.info("Select some options to see cost estimates")
        return

    # Calculate costs
    with st.spinner("Calculating costs..."):
        config_cost = cost_gen.calculate_configuration_cost(
            selected_options,
            cost_source
        )

    # Display total costs
    st.markdown("### Total Estimated Costs")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Materials",
            f"${config_cost.total_materials:,.0f}",
            help="Total material costs"
        )
    with col2:
        st.metric(
            "Labour",
            f"${config_cost.total_labour:,.0f}",
            help="Total labour costs"
        )
    with col3:
        st.metric(
            "Total Cost",
            f"${config_cost.total_cost:,.0f}",
            help="Total estimated cost"
        )

    st.divider()

    # Cost breakdown by category
    st.markdown("### Cost by Category")

    if config_cost.category_costs:
        # Filter out zero-cost categories
        non_zero_cats = [c for c in config_cost.category_costs if c.total_cost > 0]

        if non_zero_cats:
            # Create pie chart
            pie_data = {
                'category': [c.category for c in non_zero_cats],
                'cost': [c.total_cost for c in non_zero_cats]
            }

            fig_pie = px.pie(
                pie_data,
                values='cost',
                names='category',
                title='Cost Distribution by Category'
            )

            st.plotly_chart(fig_pie, use_container_width=True)

            # Bar chart with materials vs labour
            bar_data = []
            for cat in non_zero_cats:
                bar_data.append({
                    'category': cat.category,
                    'type': 'Materials',
                    'cost': cat.total_materials
                })
                bar_data.append({
                    'category': cat.category,
                    'type': 'Labour',
                    'cost': cat.total_labour
                })

            import pandas as pd
            bar_df = pd.DataFrame(bar_data)

            fig_bar = px.bar(
                bar_df,
                x='category',
                y='cost',
                color='type',
                title='Materials vs Labour by Category',
                barmode='stack'
            )

            st.plotly_chart(fig_bar, use_container_width=True)

            # Detailed table
            with st.expander("📊 Detailed Cost Breakdown", expanded=False):
                table_data = []
                for cat in sorted(non_zero_cats, key=lambda c: c.total_cost, reverse=True):
                    table_data.append({
                        'Category': cat.category,
                        'Options': ', '.join(cat.options),
                        'Materials': f"${cat.total_materials:,.2f}",
                        'Labour': f"${cat.total_labour:,.2f}",
                        'Total': f"${cat.total_cost:,.2f}",
                        'Components': cat.component_count
                    })

                import pandas as pd
                st.dataframe(
                    pd.DataFrame(table_data),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("No cost data available for selected options")

    st.divider()

    # Component details
    if not config_cost.component_details.empty:
        st.markdown("### Top Cost Components")

        top_n = st.slider("Number of components to show", 5, 20, 10)

        top_components = config_cost.component_details.nlargest(top_n, 'total_cost')

        # Display as table
        display_df = top_components[[
            'category', 'component', 'description', 'quantity', 'units',
            'total_materials', 'total_labour', 'total_cost'
        ]].copy()

        # Format currency columns
        for col in ['total_materials', 'total_labour', 'total_cost']:
            display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}")

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # Export options
    st.markdown("### Export Cost Data")

    col1, col2 = st.columns(2)

    with col1:
        # Text summary
        summary_text = cost_gen.generate_cost_summary_text(config_cost)

        st.download_button(
            label="📄 Download Summary (Markdown)",
            data=summary_text,
            file_name="cost_summary.md",
            mime="text/markdown",
            use_container_width=True
        )

    with col2:
        # CSV export
        csv_data = cost_gen.export_to_csv(config_cost)

        st.download_button(
            label="📊 Download Details (CSV)",
            data=csv_data,
            file_name="cost_details.csv",
            mime="text/csv",
            use_container_width=True
        )


def render_cost_comparison():
    """
    Render cost comparison across sources
    """
    st.subheader("📊 Cost Source Comparison")

    if 'cost_report_gen' not in st.session_state:
        st.info("Cost reports not initialized")
        return

    cost_gen = st.session_state.cost_report_gen

    # Get available sources
    available_sources = st.session_state.cost_resolver.get_available_sources()

    # Select sources to compare
    selected_sources = st.multiselect(
        "Select cost sources to compare",
        options=available_sources,
        default=available_sources[:3] if len(available_sources) >= 3 else available_sources
    )

    if len(selected_sources) < 2:
        st.info("Select at least 2 sources to compare")
        return

    # Get configuration
    selected_options = st.session_state.get('selected_options', {})

    if not selected_options:
        st.info("Select some options first")
        return

    # Calculate comparison
    with st.spinner("Comparing costs across sources..."):
        comparison_df = cost_gen.calculate_cost_comparison(
            selected_options,
            selected_sources
        )

    # Display comparison
    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )

    # Bar chart comparison
    fig = px.bar(
        comparison_df,
        x='cost_source',
        y=['total_materials', 'total_labour'],
        title='Cost Comparison by Source',
        barmode='stack'
    )

    st.plotly_chart(fig, use_container_width=True)
```

---

### Step 3: Update RIGHT Panel (15 min)

**File:** `src/ui/right_panel.py`

Add cost summary tab:

```python
def render_right_panel():
    """Render RIGHT panel with costs"""
    st.header("3️⃣ Review & Export")

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["✓ Validation", "💰 Costs", "💾 Export"])

    with tab1:
        # Existing validation summary
        from src.ui.validation_summary import render_validation_summary
        render_validation_summary()

    with tab2:
        # New cost summary
        from src.ui.cost_summary_widget import render_cost_summary, render_cost_comparison

        render_cost_summary()
        st.divider()
        render_cost_comparison()

    with tab3:
        # Existing export widget
        from src.ui.export_widget import render_export_widget
        render_export_widget()
```

---

### Step 4: Create Unit Tests (30 min)

**File:** `tests/test_cost_report.py`

```python
"""
Unit tests for cost reporting
"""

import pytest
from pathlib import Path

from src.utils import load_options, load_unit_costs
from src.utils.cost_resolver import CostResolver
from src.utils.cost_report import CostReportGenerator


@pytest.fixture
def options_db():
    """Load real options database"""
    path = "C:/HTAP/HTAP-options.json"
    if not Path(path).exists():
        pytest.skip(f"Options file not found: {path}")
    return load_options(path)


@pytest.fixture
def costs_db():
    """Load real costs database"""
    path = "C:/HTAP/HTAPUnitCosts.json"
    if not Path(path).exists():
        pytest.skip(f"Costs file not found: {path}")
    return load_unit_costs(path)


@pytest.fixture
def cost_resolver(costs_db):
    """Create cost resolver"""
    return CostResolver(costs_db)


@pytest.fixture
def cost_gen(options_db, cost_resolver):
    """Create cost report generator"""
    return CostReportGenerator(options_db, cost_resolver)


class TestCostCalculation:
    """Test cost calculation"""

    def test_calculate_single_option(self, cost_gen, options_db):
        """Test calculating cost for single option"""
        # Find option with costs
        for cat_name, category in options_db.categories.items():
            for choice_name, choice in category.options.items():
                if choice.costs and choice.costs.components:
                    selected_options = {cat_name: {choice_name}}

                    config_cost = cost_gen.calculate_configuration_cost(
                        selected_options,
                        'LEEP-ON-Ottawa'
                    )

                    assert config_cost.total_cost >= 0
                    assert config_cost.total_materials >= 0
                    assert config_cost.total_labour >= 0
                    assert len(config_cost.category_costs) == 1
                    return

        pytest.skip("No options with costs found")

    def test_calculate_multiple_options(self, cost_gen, options_db):
        """Test calculating costs for multiple options"""
        # Find two categories with costs
        selected_options = {}
        for cat_name, category in options_db.categories.items():
            for choice_name, choice in category.options.items():
                if choice.costs and choice.costs.components:
                    selected_options[cat_name] = {choice_name}
                    if len(selected_options) == 2:
                        break
            if len(selected_options) == 2:
                break

        if len(selected_options) < 2:
            pytest.skip("Not enough options with costs found")

        config_cost = cost_gen.calculate_configuration_cost(
            selected_options,
            'LEEP-ON-Ottawa'
        )

        assert config_cost.total_cost > 0
        assert len(config_cost.category_costs) == 2

    def test_component_details_dataframe(self, cost_gen, options_db):
        """Test that component details are returned as DataFrame"""
        # Find option with costs
        for cat_name, category in options_db.categories.items():
            for choice_name, choice in category.options.items():
                if choice.costs and choice.costs.components:
                    selected_options = {cat_name: {choice_name}}

                    config_cost = cost_gen.calculate_configuration_cost(
                        selected_options,
                        'LEEP-ON-Ottawa'
                    )

                    assert not config_cost.component_details.empty
                    assert 'component' in config_cost.component_details.columns
                    assert 'total_cost' in config_cost.component_details.columns
                    return

        pytest.skip("No options with costs found")


class TestCostReports:
    """Test cost report generation"""

    def test_generate_summary_text(self, cost_gen, options_db):
        """Test generating text summary"""
        # Find option with costs
        for cat_name, category in options_db.categories.items():
            for choice_name, choice in category.options.items():
                if choice.costs and choice.costs.components:
                    selected_options = {cat_name: {choice_name}}

                    config_cost = cost_gen.calculate_configuration_cost(
                        selected_options,
                        'LEEP-ON-Ottawa'
                    )

                    summary = cost_gen.generate_cost_summary_text(config_cost)

                    assert "Cost Summary Report" in summary
                    assert "Total Costs" in summary
                    assert "$" in summary
                    return

        pytest.skip("No options with costs found")

    def test_export_to_csv(self, cost_gen, options_db):
        """Test CSV export"""
        # Find option with costs
        for cat_name, category in options_db.categories.items():
            for choice_name, choice in category.options.items():
                if choice.costs and choice.costs.components:
                    selected_options = {cat_name: {choice_name}}

                    config_cost = cost_gen.calculate_configuration_cost(
                        selected_options,
                        'LEEP-ON-Ottawa'
                    )

                    csv_data = cost_gen.export_to_csv(config_cost)

                    assert isinstance(csv_data, str)
                    assert len(csv_data) > 0
                    assert ',' in csv_data  # CSV format
                    return

        pytest.skip("No options with costs found")


class TestCostComparison:
    """Test cost source comparison"""

    def test_compare_sources(self, cost_gen, options_db):
        """Test comparing costs across sources"""
        # Find option with costs
        for cat_name, category in options_db.categories.items():
            for choice_name, choice in category.options.items():
                if choice.costs and choice.costs.components:
                    selected_options = {cat_name: {choice_name}}

                    comparison = cost_gen.calculate_cost_comparison(
                        selected_options,
                        ['LEEP-ON-Ottawa', 'LEEP-BC-KamloopsChesnut']
                    )

                    assert len(comparison) == 2
                    assert 'cost_source' in comparison.columns
                    assert 'total_cost' in comparison.columns
                    return

        pytest.skip("No options with costs found")
```

---

## Acceptance Criteria

✅ **Cost report generator created** with full calculations
✅ **Total costs calculated** (materials + labour)
✅ **Per-category breakdown** displayed
✅ **Component details** available in DataFrame
✅ **Visual charts** (pie chart, bar chart) rendered
✅ **CSV export** working
✅ **Cost comparison** across sources working
✅ **Tests pass** with real data

---

## Testing Checklist

```bash
# Run unit tests
pytest tests/test_cost_report.py -v -s

# Manual testing in Streamlit:
# 1. Select options with costs
# 2. View cost summary with charts
# 3. Download cost summary (markdown)
# 4. Download cost details (CSV)
# 5. Compare costs across different sources
# 6. Verify totals are accurate
```

---

## Common Issues & Solutions

### Issue: Charts not displaying
**Solution:** Ensure plotly is installed (`pip install plotly`)

### Issue: Costs showing as $0
**Solution:** Verify options have cost data and cost source is valid

### Issue: CSV export empty
**Solution:** Check that component_details DataFrame is populated

---

## Next Steps

After completing this task:
1. Test cost calculations with various configurations
2. Verify CSV exports correctly
3. Proceed to **Task 3.4: Error Handling & Polish**

---

## Time Tracking

- Cost report generator: 75 min
- Cost visualization widget: 60 min
- RIGHT panel integration: 15 min
- Unit tests: 30 min
- **Total: ~3 hours**
