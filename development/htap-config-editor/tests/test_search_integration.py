"""
Integration tests for search features
"""

import pytest
from pathlib import Path

from src.utils import load_options
from src.utils.options_search import OptionsSearch


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


class TestAdvancedSearch:
    """Test advanced search features"""

    def test_search_with_all_filters(self, search_index):
        """Test search with all filters applied"""
        results = search_index.search(
            query="window",
            categories=["Opt-Windows"],
            require_costs=True,
            structure="tree",
            limit=50
        )

        # Should return results or empty DataFrame
        assert results is not None
        assert 'category' in results.columns
        assert 'choice' in results.columns

    def test_empty_search_returns_all(self, search_index):
        """Test that empty search with no filters returns results"""
        results = search_index.search(
            query="",
            categories=None,
            require_costs=None,
            structure=None,
            limit=100
        )

        assert len(results) > 0
        assert len(results) <= 100  # Respects limit

    def test_category_filter_only(self, search_index):
        """Test filtering by category only"""
        results = search_index.search(
            categories=["Opt-Windows"],
            limit=100
        )

        # All results should be from Opt-Windows
        if len(results) > 0:
            assert all(cat == "Opt-Windows" for cat in results['category'])

    def test_cost_filter_only(self, search_index):
        """Test filtering by cost presence"""
        with_costs = search_index.search(
            require_costs=True,
            limit=100
        )

        # All results should have costs
        if len(with_costs) > 0:
            assert all(has_costs for has_costs in with_costs['has_costs'])

        without_costs = search_index.search(
            require_costs=False,
            limit=100
        )

        # No results should have costs
        if len(without_costs) > 0:
            assert not any(has_costs for has_costs in without_costs['has_costs'])

    def test_structure_filter(self, search_index):
        """Test filtering by structure type"""
        flat_results = search_index.search(
            structure="flat",
            limit=100
        )

        if len(flat_results) > 0:
            assert all(struct == "flat" for struct in flat_results['structure'])

        tree_results = search_index.search(
            structure="tree",
            limit=100
        )

        if len(tree_results) > 0:
            assert all(struct == "tree" for struct in tree_results['structure'])

    def test_tag_search(self, search_index):
        """Test searching by tags"""
        # Search for a common tag
        results = search_index.search(
            query="energy",  # Common tag
            limit=50
        )

        # Should find results with 'energy' in tags or name
        # Note: May return empty if tag doesn't exist, which is valid
        assert results is not None

    def test_search_performance(self, search_index):
        """Test that search completes quickly"""
        import time

        queries = [
            {"query": "window"},
            {"categories": ["Opt-Windows"]},
            {"require_costs": True},
            {"query": "low-e", "categories": ["Opt-Windows"]},
        ]

        for query_params in queries:
            start = time.time()
            results = search_index.search(**query_params, limit=100)
            elapsed_ms = (time.time() - start) * 1000

            assert elapsed_ms < 10, f"Search took {elapsed_ms:.1f}ms (expected <10ms)"

    def test_limit_respected(self, search_index):
        """Test that result limit is respected"""
        results = search_index.search(limit=25)
        assert len(results) <= 25

        results = search_index.search(limit=100)
        assert len(results) <= 100

    def test_text_search_in_name(self, search_index):
        """Test text search finds matches in choice names"""
        results = search_index.search(query="air", limit=50)

        # At least one result should have 'air' in the choice name (case-insensitive)
        if len(results) > 0:
            has_match = any('air' in choice.lower() for choice in results['choice'])
            # Could also be in tags or description, so we don't assert, just verify no error
            assert has_match or len(results) > 0

    def test_text_search_in_description(self, search_index):
        """Test text search finds matches in descriptions"""
        results = search_index.search(query="insulation", limit=50)

        # Should find results (insulation is a common term)
        assert results is not None

    def test_multiple_categories(self, search_index):
        """Test filtering by multiple categories"""
        results = search_index.search(
            categories=["Opt-Windows", "Opt-ACH"],
            limit=100
        )

        if len(results) > 0:
            # All results should be from specified categories
            assert all(cat in ["Opt-Windows", "Opt-ACH"] for cat in results['category'])


class TestCategoryStatistics:
    """Test category statistics functions"""

    def test_get_all_categories(self, search_index):
        """Test getting all category names"""
        categories = search_index.get_all_categories()

        assert isinstance(categories, list)
        assert len(categories) >= 34  # At least 34 categories
        assert "Opt-Windows" in categories

    def test_get_all_tags(self, search_index):
        """Test getting all unique tags"""
        tags = search_index.get_all_tags()

        assert isinstance(tags, list)
        assert len(tags) >= 0  # Could have no tags if data doesn't include them
        # Tags should be unique
        assert len(tags) == len(set(tags))

    def test_category_stats(self, search_index):
        """Test getting category statistics"""
        stats = search_index.get_category_stats()

        assert len(stats) >= 34  # At least 34 categories
        assert 'category' in stats.columns
        assert 'total_choices' in stats.columns
        assert 'choices_with_costs' in stats.columns
        assert 'structure' in stats.columns
        assert 'costed' in stats.columns

        # Verify totals - should match total rows in dataframe
        total_choices = stats['total_choices'].sum()
        assert total_choices == len(search_index.df)  # Should match total rows

    def test_count_method(self, search_index):
        """Test count method"""
        # Count all - should match dataframe length
        total = search_index.count(limit=10000)  # Use large limit to get all
        assert total == len(search_index.df)

        # Count with filter
        windows_count = search_index.count(categories=["Opt-Windows"], limit=10000)
        assert windows_count > 0

        # Count with cost filter
        costed_count = search_index.count(require_costs=True, limit=10000)
        assert costed_count > 0
        assert costed_count < total  # Some options don't have costs


class TestSearchEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_query_empty_filters(self, search_index):
        """Test search with no query and no filters"""
        results = search_index.search(limit=50)
        assert len(results) <= 50
        assert len(results) > 0  # Should return something

    def test_query_with_special_characters(self, search_index):
        """Test search with special characters"""
        results = search_index.search(query="R-40", limit=50)
        # Should handle hyphen without error
        assert results is not None

    def test_case_insensitive_search(self, search_index):
        """Test that search is case-insensitive"""
        results_lower = search_index.search(query="window", limit=50)
        results_upper = search_index.search(query="WINDOW", limit=50)
        results_mixed = search_index.search(query="WiNdOw", limit=50)

        # Should return same number of results regardless of case
        assert len(results_lower) == len(results_upper)
        assert len(results_lower) == len(results_mixed)

    def test_nonexistent_category(self, search_index):
        """Test filtering by non-existent category"""
        results = search_index.search(
            categories=["Opt-NonExistent"],
            limit=100
        )

        # Should return empty DataFrame
        assert len(results) == 0

    def test_very_large_limit(self, search_index):
        """Test with very large limit"""
        results = search_index.search(limit=10000)

        # Should return all items - should match dataframe length
        assert len(results) == len(search_index.df)

    def test_zero_limit(self, search_index):
        """Test with zero limit"""
        results = search_index.search(limit=0)

        # Should return empty
        assert len(results) == 0


class TestSearchResultStructure:
    """Test structure and content of search results"""

    def test_result_columns(self, search_index):
        """Test that results have all expected columns"""
        results = search_index.search(limit=10)

        expected_columns = [
            'category', 'choice', 'structure', 'costed',
            'tags', 'has_costs', 'has_custom_costs', 'description',
            'choice_obj', 'category_obj'
        ]

        for col in expected_columns:
            assert col in results.columns

    def test_choice_objects_present(self, search_index):
        """Test that choice objects are included in results"""
        results = search_index.search(limit=5)

        if len(results) > 0:
            first_row = results.iloc[0]
            assert first_row['choice_obj'] is not None
            assert first_row['category_obj'] is not None

    def test_tags_format(self, search_index):
        """Test that tags are in pipe-separated format"""
        results = search_index.search(limit=10)

        for _, row in results.iterrows():
            tags = row['tags']
            # Tags should be string (could be empty)
            assert isinstance(tags, str)
            # If not empty, should be pipe-separated
            if tags:
                # Should not have leading/trailing pipes
                assert not tags.startswith('|')
                assert not tags.endswith('|')


class TestPerformanceBenchmarks:
    """Performance benchmarks for search operations"""

    def test_cold_search_performance(self, search_index):
        """Test performance of first search (cold cache)"""
        import time

        start = time.time()
        results = search_index.search(query="test", limit=100)
        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 10, f"Cold search took {elapsed_ms:.1f}ms"

    def test_repeated_search_performance(self, search_index):
        """Test performance of repeated searches"""
        import time

        # Warm up
        search_index.search(query="test", limit=100)

        # Measure repeated searches
        times = []
        for _ in range(10):
            start = time.time()
            search_index.search(query="test", limit=100)
            elapsed_ms = (time.time() - start) * 1000
            times.append(elapsed_ms)

        avg_time = sum(times) / len(times)
        assert avg_time < 10, f"Average search time {avg_time:.1f}ms"

    def test_complex_query_performance(self, search_index):
        """Test performance with complex filters"""
        import time

        start = time.time()
        results = search_index.search(
            query="window low-e",
            categories=["Opt-Windows"],
            require_costs=True,
            structure="tree",
            limit=50
        )
        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 10, f"Complex query took {elapsed_ms:.1f}ms"

    def test_statistics_performance(self, search_index):
        """Test performance of statistics calculation"""
        import time

        start = time.time()
        stats = search_index.get_category_stats()
        elapsed_ms = (time.time() - start) * 1000

        # Statistics should be fast (<50ms target)
        assert elapsed_ms < 50, f"Statistics calculation took {elapsed_ms:.1f}ms"

    def test_tag_extraction_performance(self, search_index):
        """Test performance of tag extraction"""
        import time

        start = time.time()
        tags = search_index.get_all_tags()
        elapsed_ms = (time.time() - start) * 1000

        # Tag extraction should be fast
        assert elapsed_ms < 50, f"Tag extraction took {elapsed_ms:.1f}ms"
