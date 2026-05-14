"""
Performance benchmark for options search
Tests various query types and generates statistics
"""

import time
from src.utils import load_options, OptionsSearch


def benchmark_search():
    """Run comprehensive search benchmarks"""
    print("=" * 80)
    print("HTAP Options Search Performance Benchmark")
    print("=" * 80)
    print()

    # Load data
    print("Loading data...")
    start = time.time()
    options = load_options('C:/HTAP/HTAP-options.json')
    load_time = (time.time() - start) * 1000
    print(f"  Data loaded in {load_time:.1f}ms")
    print()

    # Create search index
    print("Building search index...")
    start = time.time()
    search = OptionsSearch(options)
    index_time = (time.time() - start) * 1000
    print(f"  Index built in {index_time:.1f}ms")
    print(f"  Indexed {len(search.df)} options from {len(search.get_all_categories())} categories")
    print()

    # Test queries
    test_queries = [
        # (query, categories, require_costs, structure, description)
        ("window", None, None, None, "Simple text search: 'window'"),
        ("insulation", None, None, None, "Simple text search: 'insulation'"),
        ("low-e", ["Opt-Windows"], None, None, "Text + category: 'low-e' in Windows"),
        ("", ["Opt-Windows"], None, None, "All options in category: Windows"),
        ("", ["Opt-AboveGradeWall"], None, None, "All options in category: AboveGradeWall"),
        ("", None, True, None, "All options with costs"),
        ("", None, False, None, "All options without costs"),
        ("", None, None, "tree", "All options with tree structure"),
        ("", None, None, "flat", "All options with flat structure"),
        ("insulation", None, True, "tree", "Complex: text + costs + structure"),
        ("", ["Opt-AboveGradeWall", "Opt-AtticCeilings"], True, "tree",
         "Complex: multiple categories + costs + structure"),
    ]

    print("Search Performance Tests")
    print("-" * 80)
    print(f"{'Query Description':<50} {'Results':<10} {'Time (ms)':<10}")
    print("-" * 80)

    timings = []
    for query, cats, costs, struct, desc in test_queries:
        # Warm up
        search.search(query=query, categories=cats, require_costs=costs, structure=struct)

        # Time the search
        start = time.time()
        results = search.search(query=query, categories=cats, require_costs=costs, structure=struct)
        elapsed = (time.time() - start) * 1000
        timings.append(elapsed)

        print(f"{desc:<50} {len(results):<10} {elapsed:<10.2f}")

    print("-" * 80)
    print(f"{'Average query time:':<50} {'':<10} {sum(timings)/len(timings):.2f}")
    print(f"{'Max query time:':<50} {'':<10} {max(timings):.2f}")
    print(f"{'Min query time:':<50} {'':<10} {min(timings):.2f}")
    print()

    # Test statistics functions
    print("Statistics Functions Performance")
    print("-" * 80)

    # get_all_categories
    start = time.time()
    categories = search.get_all_categories()
    elapsed = (time.time() - start) * 1000
    print(f"get_all_categories(): {len(categories)} categories in {elapsed:.2f}ms")

    # get_all_tags
    start = time.time()
    tags = search.get_all_tags()
    elapsed = (time.time() - start) * 1000
    print(f"get_all_tags(): {len(tags)} unique tags in {elapsed:.2f}ms")

    # get_category_stats (warm up first)
    search.get_category_stats()
    start = time.time()
    stats = search.get_category_stats()
    elapsed = (time.time() - start) * 1000
    print(f"get_category_stats(): {len(stats)} categories in {elapsed:.2f}ms")

    # count
    start = time.time()
    count = search.count(categories=["Opt-Windows"])
    elapsed = (time.time() - start) * 1000
    print(f"count(categories=['Opt-Windows']): {count} options in {elapsed:.2f}ms")
    print()

    # Sample query results
    print("Sample Query Results")
    print("=" * 80)

    # Windows category
    print("\n1. All window options:")
    results = search.search(categories=["Opt-Windows"], limit=5)
    for idx, row in results.iterrows():
        print(f"   - {row['choice']}")
    print(f"   ... and {len(search.search(categories=['Opt-Windows'])) - 5} more")

    # Search for insulation
    print("\n2. Search for 'insulation' with costs:")
    results = search.search(query="insulation", require_costs=True, limit=5)
    for idx, row in results.iterrows():
        print(f"   - {row['category']}: {row['choice']}")
    if len(results) >= 5:
        total = search.count(query="insulation", require_costs=True)
        print(f"   ... and {total - 5} more")

    # Tree structure with costs
    print("\n3. Tree structure options with costs (sample):")
    results = search.search(structure="tree", require_costs=True, limit=5)
    for idx, row in results.iterrows():
        print(f"   - {row['category']}: {row['choice']}")
    total = search.count(structure="tree", require_costs=True)
    print(f"   ... and {total - 5} more")

    print()

    # Category statistics
    print("Category Statistics (Top 10 by option count)")
    print("-" * 80)
    stats = search.get_category_stats()
    stats_sorted = stats.sort_values('total_choices', ascending=False).head(10)
    print(f"{'Category':<30} {'Choices':<10} {'With Costs':<12} {'Structure':<10}")
    print("-" * 80)
    for idx, row in stats_sorted.iterrows():
        print(f"{row['category']:<30} {row['total_choices']:<10} {row['choices_with_costs']:<12} {row['structure']:<10}")

    print()
    print("=" * 80)
    print("Benchmark Complete!")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  - Total options: {len(search.df)}")
    print(f"  - Total categories: {len(search.get_all_categories())}")
    print(f"  - Total unique tags: {len(search.get_all_tags())}")
    print(f"  - Average search time: {sum(timings)/len(timings):.2f}ms")
    print(f"  - All searches completed in <10ms: {'YES' if max(timings) < 10 else 'NO'}")
    print()


if __name__ == "__main__":
    benchmark_search()
