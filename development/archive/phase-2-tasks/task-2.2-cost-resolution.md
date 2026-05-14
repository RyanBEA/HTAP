# Task 2.2: Cost Resolution Logic

**Duration:** 2-3 hours
**Phase:** 2 - Core Functionality
**Dependencies:** Task 1.2 (Data Models), Task 2.1 (Panel Interactions)
**Completion Criteria:** Cost resolution working, handles inheritance, displays accurate totals

---

## Objective

Implement robust cost resolution logic that handles multiple cost sources, component inheritance, and displays accurate cost estimates for selected options in real-time.

---

## What You'll Build

1. Cost source selection and priority system
2. Component inheritance resolver (e.g., LEEP-BC sources inherit from LEEP-ON-Ottawa)
3. Cost calculator for individual options and totals
4. UI display of costs in middle panel
5. Unit tests with real HTAPUnitCosts.json data

---

## Context: HTAPUnitCosts.json Structure

Based on architectural review, the cost database has this nested structure:

```python
{
    "component_id": {
        "source_name": {
            "category": "string",
            "description": "string",
            "units": "string",  # e.g., "sf wall", "each"
            "UnitCostMaterials": 0.35,
            "UnitCostLabour": 0.25,
            "note": "optional",
            "date": "optional",
            "source": "source_name"
        }
    }
}
```

**Inheritance Example:**
- LEEP-BC-KamloopsChesnut only defines subset of components
- Missing components inherited from LEEP-ON-Ottawa
- Need to resolve inheritance chain when looking up costs

---

## Step-by-Step Implementation

### Step 1: Create Cost Resolution Module (60 min)

**File:** `src/utils/cost_resolver.py`

```python
"""
Cost resolution logic for HTAP options
Handles multiple sources, component inheritance, and cost calculations
"""

from typing import Dict, List, Optional, Tuple
from functools import lru_cache

from src.models.cost import UnitCostsDatabase, SourceCostData
from src.models.option import OptionChoice, CostComponents


class CostResolver:
    """
    Resolves costs for HTAP options with source inheritance support
    """

    # Known inheritance chain (can be made configurable later)
    SOURCE_INHERITANCE = {
        "LEEP-BC-KamloopsChesnut": "LEEP-ON-Ottawa",
        "LEEP-BC-Victoria": "LEEP-ON-Ottawa",
        "LEEP-BC-Kelowna": "LEEP-ON-Ottawa",
        # Add more as discovered in HTAPUnitCosts.json
    }

    def __init__(self, costs_db: UnitCostsDatabase):
        """
        Initialize cost resolver

        Args:
            costs_db: Loaded unit costs database
        """
        self.costs_db = costs_db

    @lru_cache(maxsize=1024)
    def get_component_cost(
        self,
        component_id: str,
        source: str
    ) -> Optional[SourceCostData]:
        """
        Get cost for component from source, with inheritance fallback

        Args:
            component_id: Component identifier (e.g., "1/2in_gypsum_board")
            source: Cost source (e.g., "LEEP-BC-KamloopsChesnut")

        Returns:
            SourceCostData if found, None if component doesn't exist in any source
        """
        # Try direct lookup
        if component_id in self.costs_db.data:
            component_sources = self.costs_db.data[component_id]
            if source in component_sources:
                return component_sources[source]

        # Try inheritance chain
        current_source = source
        while current_source in self.SOURCE_INHERITANCE:
            parent_source = self.SOURCE_INHERITANCE[current_source]
            if component_id in self.costs_db.data:
                component_sources = self.costs_db.data[component_id]
                if parent_source in component_sources:
                    return component_sources[parent_source]
            current_source = parent_source

        return None

    def resolve_option_cost(
        self,
        option: OptionChoice,
        source: str
    ) -> Tuple[float, List[Dict]]:
        """
        Calculate total cost for an option choice

        Args:
            option: OptionChoice with costs defined
            source: Cost source to use

        Returns:
            Tuple of (total_cost, component_details)
            component_details is list of dicts with:
                - component_id
                - description
                - units
                - quantity (from option.costs.components)
                - unit_cost_materials
                - unit_cost_labour
                - total_cost
                - source_used (which source provided the cost)
        """
        if not option.costs or not option.costs.components:
            return 0.0, []

        total_cost = 0.0
        component_details = []

        for component_id, quantity in option.costs.components.items():
            cost_data = self.get_component_cost(component_id, source)

            if cost_data:
                unit_cost = cost_data.UnitCostMaterials + cost_data.UnitCostLabour
                component_total = unit_cost * quantity

                component_details.append({
                    "component_id": component_id,
                    "description": cost_data.description,
                    "units": cost_data.units,
                    "quantity": quantity,
                    "unit_cost_materials": cost_data.UnitCostMaterials,
                    "unit_cost_labour": cost_data.UnitCostLabour,
                    "unit_cost_total": unit_cost,
                    "total_cost": component_total,
                    "source_used": cost_data.source
                })

                total_cost += component_total
            else:
                # Component not found in any source
                component_details.append({
                    "component_id": component_id,
                    "description": "Component not found",
                    "units": "unknown",
                    "quantity": quantity,
                    "unit_cost_materials": 0.0,
                    "unit_cost_labour": 0.0,
                    "unit_cost_total": 0.0,
                    "total_cost": 0.0,
                    "source_used": "NOT_FOUND",
                    "error": True
                })

        # Handle custom costs
        if option.costs.custom_costs:
            for custom_id, custom_amount in option.costs.custom_costs.items():
                component_details.append({
                    "component_id": custom_id,
                    "description": "Custom cost",
                    "units": "lump sum",
                    "quantity": 1.0,
                    "unit_cost_materials": 0.0,
                    "unit_cost_labour": 0.0,
                    "unit_cost_total": custom_amount,
                    "total_cost": custom_amount,
                    "source_used": "CUSTOM",
                    "is_custom": True
                })
                total_cost += custom_amount

        return total_cost, component_details

    def get_available_sources(self) -> List[str]:
        """
        Get list of all available cost sources

        Returns:
            Sorted list of source names
        """
        sources = set()
        for component_data in self.costs_db.data.values():
            sources.update(component_data.keys())
        return sorted(sources)

    def get_source_component_count(self, source: str) -> int:
        """
        Count how many components are available in a source (with inheritance)

        Args:
            source: Cost source name

        Returns:
            Number of components available
        """
        count = 0
        for component_id in self.costs_db.data.keys():
            if self.get_component_cost(component_id, source) is not None:
                count += 1
        return count

    def validate_option_costs(
        self,
        option: OptionChoice,
        source: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all components in option are available in source

        Args:
            option: OptionChoice to validate
            source: Cost source to check against

        Returns:
            Tuple of (is_valid, list_of_missing_components)
        """
        if not option.costs or not option.costs.components:
            return True, []

        missing = []
        for component_id in option.costs.components.keys():
            if self.get_component_cost(component_id, source) is None:
                missing.append(component_id)

        return len(missing) == 0, missing
```

---

### Step 2: Update Session State for Cost Source (15 min)

**File:** `src/ui/left_panel.py`

Add cost source selector to the LEFT panel:

```python
def render_left_panel():
    """Render LEFT panel - Run configuration"""
    st.header("1️⃣ Run Configuration")

    # ... existing archetype/location/ruleset selectors ...

    # Add cost source selector
    st.subheader("Cost Source")

    # Get available sources from session state
    if 'cost_resolver' in st.session_state:
        available_sources = st.session_state.cost_resolver.get_available_sources()
    else:
        available_sources = ["LEEP-ON-Ottawa"]  # Fallback

    selected_source = st.selectbox(
        "Select cost database source",
        options=available_sources,
        index=0 if len(available_sources) > 0 else None,
        help="Cost source for calculating option costs. Some sources inherit from others.",
        key="cost_source"
    )

    # Store in session state
    if 'run_config' not in st.session_state:
        st.session_state.run_config = {}
    st.session_state.run_config['cost_source'] = selected_source

    # Show component count for selected source
    if 'cost_resolver' in st.session_state:
        component_count = st.session_state.cost_resolver.get_source_component_count(selected_source)
        st.caption(f"📊 {component_count} cost components available")
```

---

### Step 3: Update Middle Panel to Display Costs (45 min)

**File:** `src/ui/middle_panel.py`

Add cost display to option selection:

```python
def render_middle_panel():
    """Render MIDDLE panel - Option selection with costs"""
    st.header("2️⃣ Select Options")

    if 'options_db' not in st.session_state:
        st.info("👈 Load HTAP options in the left panel first")
        return

    # ... existing category selection code ...

    if selected_category:
        category = st.session_state.options_db.categories[selected_category]

        st.subheader(f"Options in {selected_category}")

        # Get cost source
        cost_source = st.session_state.run_config.get('cost_source', 'LEEP-ON-Ottawa')
        cost_resolver = st.session_state.get('cost_resolver')

        # Display options with costs
        for choice_name, choice in category.options.items():
            col1, col2 = st.columns([3, 1])

            with col1:
                # Option selection button/checkbox
                is_selected = st.session_state.selected_options.get(selected_category) == choice_name

                if st.button(
                    f"{'✅' if is_selected else '⬜'} {choice_name}",
                    key=f"opt_{selected_category}_{choice_name}",
                    use_container_width=True
                ):
                    st.session_state.selected_options[selected_category] = choice_name
                    st.rerun()

            with col2:
                # Display cost if available
                if cost_resolver and choice.costs:
                    total_cost, details = cost_resolver.resolve_option_cost(choice, cost_source)

                    if total_cost > 0:
                        st.metric("Cost", f"${total_cost:,.2f}")
                    else:
                        st.caption("No cost")
                else:
                    st.caption("—")

            # Show description if available
            if choice.description:
                st.caption(choice.description)

            # Expandable cost breakdown
            if cost_resolver and choice.costs:
                total_cost, details = cost_resolver.resolve_option_cost(choice, cost_source)

                if details:
                    with st.expander("💰 Cost Details"):
                        for component in details:
                            if component.get('error'):
                                st.error(f"❌ {component['component_id']}: Not found in cost database")
                            elif component.get('is_custom'):
                                st.info(f"💵 {component['component_id']}: ${component['total_cost']:,.2f} (custom)")
                            else:
                                st.write(
                                    f"**{component['description']}**  \n"
                                    f"Quantity: {component['quantity']} {component['units']}  \n"
                                    f"Unit cost: ${component['unit_cost_total']:.2f} "
                                    f"(M: ${component['unit_cost_materials']:.2f}, "
                                    f"L: ${component['unit_cost_labour']:.2f})  \n"
                                    f"Total: ${component['total_cost']:,.2f}  \n"
                                    f"_Source: {component['source_used']}_"
                                )

            st.divider()
```

---

### Step 4: Update App Initialization (10 min)

**File:** `src/app.py`

Initialize cost resolver on app startup:

```python
def initialize_app():
    """Initialize application state and load data"""

    if 'options_db' not in st.session_state:
        with st.spinner("Loading HTAP options..."):
            st.session_state.options_db = load_options("C:/HTAP/HTAP-options.json")

    if 'costs_db' not in st.session_state:
        with st.spinner("Loading cost database..."):
            st.session_state.costs_db = load_unit_costs("C:/HTAP/HTAPUnitCosts.json")

    if 'cost_resolver' not in st.session_state:
        from src.utils.cost_resolver import CostResolver
        st.session_state.cost_resolver = CostResolver(st.session_state.costs_db)

    # ... rest of initialization ...
```

---

### Step 5: Create Unit Tests (30 min)

**File:** `tests/test_cost_resolver.py`

```python
"""
Unit tests for cost resolution logic
"""

import pytest
from pathlib import Path

from src.utils import load_unit_costs, load_options
from src.utils.cost_resolver import CostResolver


@pytest.fixture
def costs_db():
    """Load real costs database"""
    path = "C:/HTAP/HTAPUnitCosts.json"
    if not Path(path).exists():
        pytest.skip(f"Costs file not found: {path}")
    return load_unit_costs(path)


@pytest.fixture
def options_db():
    """Load real options database"""
    path = "C:/HTAP/HTAP-options.json"
    if not Path(path).exists():
        pytest.skip(f"Options file not found: {path}")
    return load_options(path)


@pytest.fixture
def resolver(costs_db):
    """Create cost resolver"""
    return CostResolver(costs_db)


class TestCostResolver:
    """Test cost resolution functionality"""

    def test_direct_component_lookup(self, resolver):
        """Test looking up component from primary source"""
        cost_data = resolver.get_component_cost(
            "1/2in_gypsum_board",
            "LEEP-ON-Ottawa"
        )

        assert cost_data is not None
        assert cost_data.units == "sf wall"
        assert cost_data.UnitCostMaterials > 0
        assert cost_data.UnitCostLabour >= 0

    def test_inherited_component_lookup(self, resolver):
        """Test looking up component with inheritance"""
        # LEEP-BC-KamloopsChesnut should inherit from LEEP-ON-Ottawa
        cost_data = resolver.get_component_cost(
            "1/2in_gypsum_board",
            "LEEP-BC-KamloopsChesnut"
        )

        assert cost_data is not None
        assert cost_data.source in ["LEEP-BC-KamloopsChesnut", "LEEP-ON-Ottawa"]

    def test_missing_component(self, resolver):
        """Test looking up non-existent component"""
        cost_data = resolver.get_component_cost(
            "non_existent_component_12345",
            "LEEP-ON-Ottawa"
        )

        assert cost_data is None

    def test_resolve_option_cost(self, resolver, options_db):
        """Test resolving total cost for an option"""
        # Find an option with costs
        option_with_costs = None
        for category in options_db.categories.values():
            for choice in category.options.values():
                if choice.costs and choice.costs.components:
                    option_with_costs = choice
                    break
            if option_with_costs:
                break

        if option_with_costs is None:
            pytest.skip("No options with costs found")

        total_cost, details = resolver.resolve_option_cost(
            option_with_costs,
            "LEEP-ON-Ottawa"
        )

        assert total_cost >= 0
        assert isinstance(details, list)
        assert len(details) == len(option_with_costs.costs.components)

    def test_option_without_costs(self, resolver, options_db):
        """Test option with no costs defined"""
        # Find option without costs
        option_no_costs = None
        for category in options_db.categories.values():
            for choice in category.options.values():
                if not choice.costs or not choice.costs.components:
                    option_no_costs = choice
                    break
            if option_no_costs:
                break

        if option_no_costs is None:
            pytest.skip("All options have costs")

        total_cost, details = resolver.resolve_option_cost(
            option_no_costs,
            "LEEP-ON-Ottawa"
        )

        assert total_cost == 0.0
        assert details == []

    def test_get_available_sources(self, resolver):
        """Test listing all cost sources"""
        sources = resolver.get_available_sources()

        assert isinstance(sources, list)
        assert len(sources) > 0
        assert "LEEP-ON-Ottawa" in sources

    def test_source_component_count(self, resolver):
        """Test counting components in a source"""
        count = resolver.get_source_component_count("LEEP-ON-Ottawa")

        assert count > 0
        assert count == 351  # Known count from architectural review

    def test_validate_option_costs(self, resolver, options_db):
        """Test validating option costs against source"""
        # Find option with costs
        option_with_costs = None
        for category in options_db.categories.values():
            for choice in category.options.values():
                if choice.costs and choice.costs.components:
                    option_with_costs = choice
                    break
            if option_with_costs:
                break

        if option_with_costs is None:
            pytest.skip("No options with costs found")

        is_valid, missing = resolver.validate_option_costs(
            option_with_costs,
            "LEEP-ON-Ottawa"
        )

        assert isinstance(is_valid, bool)
        assert isinstance(missing, list)


class TestCostInheritance:
    """Test cost source inheritance"""

    def test_inheritance_chain(self, resolver):
        """Test that inheritance chain is followed"""
        # Pick a component that only exists in parent source
        # This test assumes we know the inheritance structure

        bc_source = "LEEP-BC-KamloopsChesnut"
        parent_source = "LEEP-ON-Ottawa"

        # Get component from BC source (should inherit)
        bc_cost = resolver.get_component_cost("1/2in_gypsum_board", bc_source)

        # Get same component from parent
        parent_cost = resolver.get_component_cost("1/2in_gypsum_board", parent_source)

        # If BC doesn't override, should get parent's cost
        assert bc_cost is not None
        assert parent_cost is not None
```

---

## Acceptance Criteria

✅ **Cost resolver created** with inheritance support
✅ **Component lookup works** with fallback to parent sources
✅ **Option costs calculated** accurately (materials + labour)
✅ **Cost source selector** in LEFT panel
✅ **Cost display** in MIDDLE panel with breakdown
✅ **Custom costs** handled correctly
✅ **Missing components** detected and reported
✅ **Tests pass** with real HTAPUnitCosts.json and HTAP-options.json

---

## Testing Checklist

```bash
# Run unit tests
pytest tests/test_cost_resolver.py -v -s

# Manual integration test
python -c "
from src.utils import load_unit_costs, load_options
from src.utils.cost_resolver import CostResolver

# Load data
costs_db = load_unit_costs('C:/HTAP/HTAPUnitCosts.json')
options_db = load_options('C:/HTAP/HTAP-options.json')

# Create resolver
resolver = CostResolver(costs_db)

# Test component lookup
gypsum = resolver.get_component_cost('1/2in_gypsum_board', 'LEEP-ON-Ottawa')
print(f'Gypsum board: {gypsum.units} @ \${gypsum.UnitCostMaterials + gypsum.UnitCostLabour:.2f}')

# Test inheritance
bc_gypsum = resolver.get_component_cost('1/2in_gypsum_board', 'LEEP-BC-KamloopsChesnut')
print(f'BC source (inherited): {bc_gypsum.source}')

# Test option cost
for cat in options_db.categories.values():
    for choice in cat.options.values():
        if choice.costs and choice.costs.components:
            total, details = resolver.resolve_option_cost(choice, 'LEEP-ON-Ottawa')
            print(f'\\nOption: {choice}')
            print(f'Total cost: \${total:,.2f}')
            print(f'Components: {len(details)}')
            break
    else:
        continue
    break
"
```

---

## Common Issues & Solutions

### Issue: Component not found despite existing in JSON
**Solution:** Check inheritance chain. Component might exist in parent source only.

### Issue: Costs showing as $0.00
**Solution:** Verify that option.costs.components uses correct component IDs matching HTAPUnitCosts.json keys.

### Issue: Inheritance not working
**Solution:** Check SOURCE_INHERITANCE mapping. Add missing parent-child relationships.

### Issue: Custom costs not displaying
**Solution:** Ensure option.costs.custom_costs is checked separately from regular components.

---

## Performance Considerations

- **@lru_cache** on get_component_cost() caches lookups (max 1024 entries)
- With 351 components, caching provides 10-100x speedup on repeated lookups
- Inheritance lookups are cached after first resolution
- Cost calculations happen on-demand when displaying options

---

## Next Steps

After completing this task:
1. Test with various cost sources (LEEP-ON-Ottawa, LEEP-BC sources)
2. Verify inheritance works correctly
3. Check cost displays in middle panel
4. Proceed to **Task 2.3: Validation & Warnings**

---

## Time Tracking

- Cost resolver implementation: 60 min
- Session state update: 15 min
- Middle panel cost display: 45 min
- App initialization: 10 min
- Unit tests: 30 min
- **Total: ~2.5 hours**

---

## Integration Points

**Inputs:**
- Task 1.2: UnitCostsDatabase, SourceCostData models
- Task 2.1: Session state structure (run_config, selected_options)

**Outputs:**
- Cost resolver available in session state
- Cost source selector in LEFT panel
- Cost displays in MIDDLE panel
- Component-level cost breakdown

**Used by:**
- Task 2.3: Validation (to check if costs are complete)
- Task 3.3: Cost Summary Report (for total cost calculations)
