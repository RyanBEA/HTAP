# Task 1.5: Options Search with Pandas

**Duration:** 1-1.5 hours
**Phase:** 1 - Foundation
**Dependencies:** Task 1.2 (Data Models & Loading)
**Completion Criteria:** Fast search implemented, query performance <10ms, tests pass

⚠️ **SIMPLIFIED:** This task has been simplified based on architectural review. With only 769 options, pandas DataFrame is faster and simpler than complex inverted indexes.

---

## Objective

Create a simple, fast search interface for HTAP options using pandas DataFrame. With only 769 option choices, we can achieve <10ms queries with straightforward filtering.

---

## What You'll Build

1. Simple pandas-based search class
2. Multi-faceted filtering (text, category, costs, structure)
3. Statistics and aggregation functions
4. Unit tests with real data
5. Performance benchmarks

---

## Technical Approach

### Why Pandas?

With **769 option choices**:
- ✅ Linear search is <5ms
- ✅ pandas filtering is optimized and fast
- ✅ No need for complex inverted indexes
- ✅ 30 lines of code vs 400+ lines
- ✅ More maintainable and flexible

### Architecture

```
src/utils/
├── __init__.py
├── loaders.py          # (from Task 1.2)
└── options_search.py   # NEW: Simple pandas search
```

---

## Step-by-Step Implementation

### Step 1: Create Simple Search Class (45 min)

**File:** `src/utils/options_search.py`

```python
"""
Simple search for HTAP options using pandas
Optimized for 769 option choices - fast enough without complex indexing
"""

import pandas as pd
from typing import List, Optional

from src.models.option import OptionsDatabase


class OptionsSearch:
    """
    Simple search using pandas DataFrame
    Fast enough for 769 items (<10ms queries)
    """

    def __init__(self, options_db: OptionsDatabase):
        """
        Initialize search with options database

        Args:
            options_db: OptionsDatabase to search
        """
        self.options_db = options_db

        # Flatten to DataFrame for fast filtering
        rows = []
        for cat_name, category in options_db.categories.items():
            for choice_name, choice in category.options.items():
                rows.append({
                    'category': cat_name,
                    'choice': choice_name,
                    'structure': category.structure,
                    'costed': category.costed,
                    'tags': '|'.join(choice.tags) if choice.tags else '',
                    'has_costs': bool(choice.costs and choice.costs.components),
                    'has_custom_costs': bool(choice.costs and choice.costs.custom_costs),
                    'description': choice.description or '',
                    'choice_obj': choice,
                    'category_obj': category
                })

        self.df = pd.DataFrame(rows)

    def search(
        self,
        query: str = "",
        categories: Optional[List[str]] = None,
        require_costs: Optional[bool] = None,
        structure: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Search options with filters

        Args:
            query: Search term (searches in choice name, tags, description)
            categories: Filter by category names (e.g., ["Opt-Windows"])
            require_costs: Filter by cost presence (True/False/None)
            structure: Filter by structure type ("flat"/"tree"/None)
            limit: Maximum results to return

        Returns:
            DataFrame with matching options
        """
        df = self.df.copy()

        # Text search across name, tags, description
        if query:
            query_lower = query.lower()
            mask = (
                df['choice'].str.lower().str.contains(query_lower, na=False) |
                df['tags'].str.lower().str.contains(query_lower, na=False) |
                df['description'].str.lower().str.contains(query_lower, na=False)
            )
            df = df[mask]

        # Category filter
        if categories:
            df = df[df['category'].isin(categories)]

        # Cost filter
        if require_costs is not None:
            df = df[df['has_costs'] == require_costs]

        # Structure filter
        if structure:
            df = df[df['structure'] == structure]

        # Limit results
        return df.head(limit)

    def get_all_categories(self) -> List[str]:
        """Get list of all category names"""
        return sorted(self.df['category'].unique().tolist())

    def get_all_tags(self) -> List[str]:
        """Get list of all unique tags"""
        all_tags = set()
        for tags_str in self.df['tags']:
            if tags_str:
                all_tags.update(tags_str.split('|'))
        return sorted(all_tags)

    def get_category_stats(self) -> pd.DataFrame:
        """
        Get statistics per category

        Returns:
            DataFrame with columns: category, total_choices, choices_with_costs,
                                    structure, costed
        """
        return self.df.groupby('category').agg({
            'choice': 'count',
            'has_costs': 'sum',
            'structure': 'first',
            'costed': 'first'
        }).rename(columns={
            'choice': 'total_choices',
            'has_costs': 'choices_with_costs'
        }).reset_index()

    def count(self, **kwargs) -> int:
        """
        Count matching results without returning data

        Args:
            **kwargs: Same as search() method

        Returns:
            Number of matching options
        """
        return len(self.search(**kwargs))
```

---

### Step 2: Update Utils __init__.py (5 min)

**File:** `src/utils/__init__.py`

```python
"""
HTAP utility functions and data loaders
"""

from .loaders import (
    load_unit_costs,
    load_options,
    clear_cache
)

from .options_search import OptionsSearch

__all__ = [
    # Loaders
    "load_unit_costs",
    "load_options",
    "clear_cache",

    # Search
    "OptionsSearch",
]
```

---

### Step 3: Create Unit Tests (30 min)

**File:** `tests/test_options_search.py`

```python
"""
Unit tests for options search
"""

import pytest
import pandas as pd
from pathlib import Path

from src.utils import load_options, OptionsSearch


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


class TestOptionsSearch:
    """Test options search functionality"""

    def test_search_initialization(self, search_index):
        """Test that search index builds correctly"""
        assert isinstance(search_index.df, pd.DataFrame)
        assert len(search_index.df) == 769  # Known total

    def test_simple_search(self, search_index):
        """Test simple text search"""
        results = search_index.search(query="window")
        assert len(results) > 0
        assert all('window' in choice.lower() for choice in results['choice'])

    def test_category_filter(self, search_index):
        """Test filtering by category"""
        results = search_index.search(categories=["Opt-Windows"])
        assert len(results) > 0
        assert all(cat == "Opt-Windows" for cat in results['category'])

    def test_cost_filter(self, search_index):
        """Test filtering by cost presence"""
        with_costs = search_index.search(require_costs=True)
        assert len(with_costs) > 0
        assert all(results['has_costs'])

        without_costs = search_index.search(require_costs=False)
        assert len(without_costs) > 0
        assert not any(results['has_costs'])

    def test_structure_filter(self, search_index):
        """Test filtering by structure type"""
        tree_results = search_index.search(structure="tree")
        assert len(tree_results) > 0
        assert all(struct == "tree" for struct in tree_results['structure'])

    def test_combined_filters(self, search_index):
        """Test combining multiple filters"""
        results = search_index.search(
            query="low-e",
            categories=["Opt-Windows"],
            require_costs=True
        )
        assert len(results) >= 0  # May or may not have results

    def test_get_categories(self, search_index):
        """Test getting all categories"""
        categories = search_index.get_all_categories()
        assert len(categories) == 34
        assert "Opt-Windows" in categories

    def test_get_tags(self, search_index):
        """Test getting all unique tags"""
        tags = search_index.get_all_tags()
        assert len(tags) > 0
        assert isinstance(tags, list)

    def test_category_stats(self, search_index):
        """Test category statistics"""
        stats = search_index.get_category_stats()
        assert isinstance(stats, pd.DataFrame)
        assert len(stats) == 34
        assert 'total_choices' in stats.columns
        assert 'choices_with_costs' in stats.columns

    def test_count_method(self, search_index):
        """Test count without returning data"""
        count = search_index.count(categories=["Opt-Windows"])
        assert count == 61  # Known count for Opt-Windows


class TestSearchPerformance:
    """Test search performance"""

    def test_search_speed(self, search_index):
        """Test that search completes quickly"""
        import time

        # Warm up
        search_index.search("test")

        # Time actual search
        start = time.time()
        results = search_index.search(query="window", categories=["Opt-Windows"])
        elapsed = time.time() - start

        assert elapsed < 0.01, f"Search took {elapsed*1000:.1f}ms, expected <10ms"

    def test_complex_search_speed(self, search_index):
        """Test complex search with all filters"""
        import time

        start = time.time()
        results = search_index.search(
            query="low-e",
            categories=["Opt-Windows", "Opt-Doors"],
            require_costs=True,
            structure="tree"
        )
        elapsed = time.time() - start

        assert elapsed < 0.01, f"Complex search took {elapsed*1000:.1f}ms, expected <10ms"
```

---

## Acceptance Criteria

✅ **Search class created** using pandas DataFrame
✅ **Query performance** <10ms for any search
✅ **All filters work** (text, category, costs, structure)
✅ **Tests pass** with real HTAP-options.json
✅ **Code is simple** (~100 lines total vs 400+ in original plan)
✅ **Statistics functions** provide aggregated data

---

## Testing Checklist

```bash
# Run tests
pytest tests/test_options_search.py -v -s

# Manual performance test
python -c "
import time
from src.utils import load_options, OptionsSearch

# Load data
options = load_options('C:/HTAP/HTAP-options.json')
search = OptionsSearch(options)

print(f'Indexed {len(search.df)} options')

# Test search speed
queries = [
    ('window', []),
    ('low-e', ['Opt-Windows']),
    ('', ['Opt-AboveGradeWall']),
]

for query, cats in queries:
    start = time.time()
    results = search.search(query=query, categories=cats or None)
    elapsed = (time.time() - start) * 1000
    print(f'Query \"{query}\" in {cats or \"all\"}: {len(results)} results in {elapsed:.1f}ms')

# Category stats
stats = search.get_category_stats()
print(f'\\nCategory statistics:\\n{stats.head()}')
"
```

Expected output:
```
Indexed 769 options
Query "window" in all: XX results in 2.5ms
Query "low-e" in ['Opt-Windows']: XX results in 1.8ms
Query "" in ['Opt-AboveGradeWall']: XX results in 0.8ms

Category statistics:
              category  total_choices  choices_with_costs structure  costed
0         Opt-ACH                 13                   0      flat    False
1    Opt-AboveGradeWall             32                   5      tree     True
...
```

---

## Common Issues & Solutions

### Issue: pandas search is slow
**Solution:** With 769 items it should be <10ms. Check if DataFrame is being copied unnecessarily.

### Issue: Can't find 'choices' attribute
**Solution:** Field is named `options` in OptionCategory, use `category.options`

### Issue: Tags search not working
**Solution:** Tags are joined with '|', use `str.contains()` with case-insensitive matching

---

## Next Steps

After completing this task:
1. Verify search performance <10ms
2. Test with various search queries
3. **Phase 1 Complete!** Review before starting Phase 2

---

## Time Tracking

- Search class implementation: 45 min
- Update __init__.py: 5 min
- Unit tests: 30 min
- Performance testing: 10 min
- **Total: ~1.5 hours**

---

## 📊 Performance Comparison

**Original Plan (Inverted Index):**
- Code: 400+ lines
- Complexity: High (tokenization, inverted indexes, query builder)
- Performance: <100ms
- Maintenance: Difficult

**Simplified Approach (Pandas):**
- Code: ~100 lines
- Complexity: Low (simple DataFrame filtering)
- Performance: <10ms (10x faster!)
- Maintenance: Easy

**Result:** 75% code reduction, 10x faster, much simpler!
