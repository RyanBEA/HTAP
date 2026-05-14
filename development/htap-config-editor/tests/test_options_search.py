"""
Unit tests for options search
"""

import pytest
import pandas as pd
from pathlib import Path
import time

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
        assert len(search_index.df) == 773, f"Expected 773 options, got {len(search_index.df)}"

        # Verify all required columns exist
        required_cols = ['category', 'choice', 'structure', 'costed', 'tags',
                        'has_costs', 'has_custom_costs', 'description',
                        'choice_obj', 'category_obj']
        for col in required_cols:
            assert col in search_index.df.columns, f"Missing column: {col}"

    def test_simple_search(self, search_index):
        """Test simple text search"""
        results = search_index.search(query="window")
        assert len(results) > 0, "Should find results for 'window'"

        # Check that 'window' appears in choice name, tags, or description
        for idx, row in results.iterrows():
            found = (
                'window' in row['choice'].lower() or
                'window' in row['tags'].lower() or
                'window' in row['description'].lower()
            )
            assert found, f"'window' not found in {row['choice']}"

    def test_category_filter(self, search_index):
        """Test filtering by category"""
        results = search_index.search(categories=["Opt-Windows"])
        assert len(results) > 0, "Should find Opt-Windows options"
        assert all(cat == "Opt-Windows" for cat in results['category']), \
            "All results should be from Opt-Windows category"

    def test_cost_filter_with_costs(self, search_index):
        """Test filtering for options with costs"""
        with_costs = search_index.search(require_costs=True)
        assert len(with_costs) > 0, "Should find options with costs"
        assert all(with_costs['has_costs']), "All results should have costs"

    def test_cost_filter_without_costs(self, search_index):
        """Test filtering for options without costs"""
        without_costs = search_index.search(require_costs=False)
        assert len(without_costs) > 0, "Should find options without costs"
        assert not any(without_costs['has_costs']), "No results should have costs"

    def test_structure_filter_tree(self, search_index):
        """Test filtering by tree structure"""
        tree_results = search_index.search(structure="tree")
        assert len(tree_results) > 0, "Should find tree structure options"
        assert all(struct == "tree" for struct in tree_results['structure']), \
            "All results should have tree structure"

    def test_structure_filter_flat(self, search_index):
        """Test filtering by flat structure"""
        flat_results = search_index.search(structure="flat")
        assert len(flat_results) > 0, "Should find flat structure options"
        assert all(struct == "flat" for struct in flat_results['structure']), \
            "All results should have flat structure"

    def test_combined_filters(self, search_index):
        """Test combining multiple filters"""
        results = search_index.search(
            query="insulation",
            structure="tree",
            require_costs=True
        )
        # May or may not have results - just verify it executes without error
        assert isinstance(results, pd.DataFrame), "Should return DataFrame"

        # If there are results, verify filters applied correctly
        if len(results) > 0:
            assert all(results['structure'] == "tree"), "All results should be tree structure"
            assert all(results['has_costs']), "All results should have costs"

    def test_limit_parameter(self, search_index):
        """Test that limit parameter works"""
        results = search_index.search(limit=10)
        assert len(results) <= 10, "Results should respect limit parameter"

    def test_get_all_categories(self, search_index):
        """Test getting all categories"""
        categories = search_index.get_all_categories()
        assert len(categories) == 35, f"Expected 35 categories, got {len(categories)}"
        assert "Opt-Windows" in categories, "Should include Opt-Windows"
        assert "Opt-ACH" in categories, "Should include Opt-ACH"
        assert categories == sorted(categories), "Categories should be sorted"

    def test_get_all_tags(self, search_index):
        """Test getting all unique tags"""
        tags = search_index.get_all_tags()
        assert isinstance(tags, list), "Should return a list"
        assert tags == sorted(tags), "Tags should be sorted"

        # Check for duplicates
        assert len(tags) == len(set(tags)), "Tags should be unique"

        # Some options may not have tags, so just verify structure is correct
        if len(tags) > 0:
            assert all(isinstance(tag, str) for tag in tags), "All tags should be strings"

    def test_category_stats(self, search_index):
        """Test category statistics"""
        stats = search_index.get_category_stats()
        assert isinstance(stats, pd.DataFrame), "Should return DataFrame"
        assert len(stats) == 35, f"Expected 35 categories, got {len(stats)}"

        # Check required columns
        required_cols = ['category', 'total_choices', 'choices_with_costs', 'structure', 'costed']
        for col in required_cols:
            assert col in stats.columns, f"Missing column: {col}"

        # Verify Opt-Windows has correct count
        windows_stats = stats[stats['category'] == 'Opt-Windows']
        assert len(windows_stats) == 1, "Should have exactly one row for Opt-Windows"
        assert windows_stats.iloc[0]['total_choices'] == 61, \
            f"Opt-Windows should have 61 choices, got {windows_stats.iloc[0]['total_choices']}"

    def test_count_method(self, search_index):
        """Test count without returning data"""
        count = search_index.count(categories=["Opt-Windows"])
        assert count == 61, f"Opt-Windows should have 61 choices, got {count}"

        # Verify count matches search results
        results = search_index.search(categories=["Opt-Windows"])
        assert count == len(results), "count() should match length of search()"

    def test_count_with_filters(self, search_index):
        """Test count with multiple filters"""
        count = search_index.count(structure="tree", require_costs=True)
        results = search_index.search(structure="tree", require_costs=True)
        assert count == len(results), "count() should match search() with same filters"

    def test_empty_query_returns_all(self, search_index):
        """Test that empty query returns all options (up to limit)"""
        results = search_index.search(query="", limit=1000)
        assert len(results) == 773, "Empty query should return all options"


class TestSearchPerformance:
    """Test search performance"""

    def test_search_speed_simple(self, search_index):
        """Test that simple search completes quickly"""
        # Warm up
        search_index.search("test")

        # Time actual search
        start = time.time()
        results = search_index.search(query="window")
        elapsed = time.time() - start

        assert elapsed < 0.01, f"Search took {elapsed*1000:.1f}ms, expected <10ms"
        assert len(results) > 0, "Should find results"

    def test_search_speed_category_filter(self, search_index):
        """Test search with category filter"""
        start = time.time()
        results = search_index.search(query="window", categories=["Opt-Windows"])
        elapsed = time.time() - start

        assert elapsed < 0.01, f"Category search took {elapsed*1000:.1f}ms, expected <10ms"

    def test_complex_search_speed(self, search_index):
        """Test complex search with all filters"""
        start = time.time()
        results = search_index.search(
            query="insulation",
            categories=["Opt-AboveGradeWall", "Opt-AtticCeilings"],
            require_costs=True,
            structure="tree"
        )
        elapsed = time.time() - start

        assert elapsed < 0.01, f"Complex search took {elapsed*1000:.1f}ms, expected <10ms"

    def test_get_stats_speed(self, search_index):
        """Test that statistics generation is fast"""
        # Warm up
        search_index.get_category_stats()

        start = time.time()
        stats = search_index.get_category_stats()
        elapsed = time.time() - start

        # Stats generation uses groupby which can take ~30ms first time, <10ms after warm-up
        assert elapsed < 0.05, f"Stats generation took {elapsed*1000:.1f}ms, expected <50ms"
        assert len(stats) == 35, "Should return stats for all categories"


class TestSearchEdgeCases:
    """Test edge cases and error handling"""

    def test_search_nonexistent_category(self, search_index):
        """Test searching for non-existent category"""
        results = search_index.search(categories=["Opt-NonExistent"])
        assert len(results) == 0, "Should return empty results for non-existent category"

    def test_search_case_insensitive(self, search_index):
        """Test that search is case-insensitive"""
        results_lower = search_index.search(query="window")
        results_upper = search_index.search(query="WINDOW")
        results_mixed = search_index.search(query="WiNdOw")

        assert len(results_lower) == len(results_upper) == len(results_mixed), \
            "Case-insensitive search should return same results"

    def test_search_special_characters(self, search_index):
        """Test search with special characters"""
        # Search for options with hyphens
        results = search_index.search(query="low-e")
        # Should execute without error (may or may not find results)
        assert isinstance(results, pd.DataFrame), "Should handle special characters"

    def test_multiple_categories_filter(self, search_index):
        """Test filtering by multiple categories"""
        results = search_index.search(categories=["Opt-Windows", "Opt-Doors"])
        assert len(results) > 0, "Should find results in multiple categories"
        assert all(cat in ["Opt-Windows", "Opt-Doors"] for cat in results['category']), \
            "Results should only be from specified categories"

    def test_tags_search(self, search_index):
        """Test searching by tags"""
        # Get a sample tag
        tags = search_index.get_all_tags()
        if len(tags) > 0:
            sample_tag = tags[0]
            results = search_index.search(query=sample_tag)
            # Should find at least one result with this tag
            found = False
            for idx, row in results.iterrows():
                if sample_tag in row['tags'].split('|'):
                    found = True
                    break
            assert found or len(results) == 0, "If tag exists, should find it in results"
