"""
Manual UI Testing Script for Task 1.3
Validates all UI components and interactions
"""

import sys
import io
from pathlib import Path

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from src.ui.components import (
            file_uploader_card,
            search_box,
            option_card,
            status_badge,
            cost_summary_card
        )
        print("  ✓ components.py imports successfully")
    except Exception as e:
        print(f"  ✗ Error importing components.py: {e}")
        return False

    try:
        from src.ui.left_panel import render_left_panel
        print("  ✓ left_panel.py imports successfully")
    except Exception as e:
        print(f"  ✗ Error importing left_panel.py: {e}")
        return False

    try:
        from src.ui.middle_panel import render_middle_panel
        print("  ✓ middle_panel.py imports successfully")
    except Exception as e:
        print(f"  ✗ Error importing middle_panel.py: {e}")
        return False

    try:
        from src.ui.right_panel import render_right_panel
        print("  ✓ right_panel.py imports successfully")
    except Exception as e:
        print(f"  ✗ Error importing right_panel.py: {e}")
        return False

    try:
        from src.ui.layout import render_main_layout, initialize_session_state
        print("  ✓ layout.py imports successfully")
    except Exception as e:
        print(f"  ✗ Error importing layout.py: {e}")
        return False

    try:
        import app
        print("  ✓ app.py imports successfully")
    except Exception as e:
        print(f"  ✗ Error importing app.py: {e}")
        return False

    return True


def test_placeholder_functions():
    """Test that placeholder functions return expected data types"""
    print("\nTesting placeholder functions...")

    try:
        from src.ui.left_panel import _get_archetypes, _get_locations, _get_rulesets

        archetypes = _get_archetypes()
        assert isinstance(archetypes, list), "Archetypes should be a list"
        assert len(archetypes) > 0, "Archetypes should not be empty"
        print(f"  ✓ _get_archetypes() returns {len(archetypes)} items")

        locations = _get_locations()
        assert isinstance(locations, list), "Locations should be a list"
        assert len(locations) > 0, "Locations should not be empty"
        print(f"  ✓ _get_locations() returns {len(locations)} items")

        rulesets = _get_rulesets()
        assert isinstance(rulesets, list), "Rulesets should be a list"
        assert len(rulesets) > 0, "Rulesets should not be empty"
        print(f"  ✓ _get_rulesets() returns {len(rulesets)} items")

    except Exception as e:
        print(f"  ✗ Error testing left_panel placeholders: {e}")
        return False

    try:
        from src.ui.middle_panel import _get_option_categories, _get_filtered_options

        categories = _get_option_categories()
        assert isinstance(categories, list), "Categories should be a list"
        assert len(categories) > 0, "Categories should not be empty"
        print(f"  ✓ _get_option_categories() returns {len(categories)} items")

        options = _get_filtered_options("", [])
        assert isinstance(options, list), "Options should be a list"
        print(f"  ✓ _get_filtered_options() returns {len(options)} items")

        # Test search filtering
        filtered = _get_filtered_options("window", [])
        assert len(filtered) <= len(options), "Filtered list should be smaller or equal"
        print(f"  ✓ Search filtering works (found {len(filtered)} matching items)")

        # Test category filtering
        if categories:
            filtered = _get_filtered_options("", [categories[0]])
            print(f"  ✓ Category filtering works (found {len(filtered)} items in {categories[0]})")

    except Exception as e:
        print(f"  ✗ Error testing middle_panel placeholders: {e}")
        return False

    try:
        from src.ui.right_panel import _get_option_cost_components

        components = _get_option_cost_components("DoubleGlazed-Air-LowE")
        assert isinstance(components, list), "Components should be a list"
        print(f"  ✓ _get_option_cost_components() returns {len(components)} items")

        if components:
            comp = components[0]
            assert "id" in comp, "Component should have 'id' field"
            assert "cost" in comp, "Component should have 'cost' field"
            assert "type" in comp, "Component should have 'type' field"
            print(f"  ✓ Cost components have correct structure")

    except Exception as e:
        print(f"  ✗ Error testing right_panel placeholders: {e}")
        return False

    return True


def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting file structure...")

    required_files = [
        "src/ui/__init__.py",
        "src/ui/components.py",
        "src/ui/left_panel.py",
        "src/ui/middle_panel.py",
        "src/ui/right_panel.py",
        "src/ui/layout.py",
        "app.py",
    ]

    all_exist = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"  ✓ {file} exists")
        else:
            print(f"  ✗ {file} NOT FOUND")
            all_exist = False

    return all_exist


def test_line_counts():
    """Verify files meet minimum line count requirements"""
    print("\nTesting file sizes (approximate line counts)...")

    file_requirements = {
        "src/ui/components.py": 120,
        "src/ui/left_panel.py": 100,
        "src/ui/middle_panel.py": 120,
        "src/ui/right_panel.py": 100,
        "src/ui/layout.py": 80,
        "app.py": 30,
    }

    all_pass = True
    for file, min_lines in file_requirements.items():
        path = Path(file)
        if path.exists():
            line_count = len(path.read_text(encoding='utf-8').splitlines())
            status = "✓" if line_count >= min_lines else "⚠"
            print(f"  {status} {file}: {line_count} lines (min: {min_lines})")
            if line_count < min_lines:
                all_pass = False
        else:
            print(f"  ✗ {file} NOT FOUND")
            all_pass = False

    return all_pass


def test_todo_markers():
    """Find all TODO markers in the code"""
    print("\nFinding TODO markers for future integration...")

    files_to_check = [
        "src/ui/left_panel.py",
        "src/ui/middle_panel.py",
        "src/ui/right_panel.py",
    ]

    todos = []
    for file in files_to_check:
        path = Path(file)
        if path.exists():
            content = path.read_text(encoding='utf-8')
            for i, line in enumerate(content.splitlines(), 1):
                if "TODO" in line:
                    todos.append((file, i, line.strip()))

    if todos:
        print(f"\n  Found {len(todos)} TODO markers:")
        for file, line_num, text in todos:
            print(f"    • {file}:{line_num} - {text}")
    else:
        print("  No TODO markers found")

    return True


def main():
    """Run all tests"""
    print("=" * 70)
    print("HTAP Configuration Editor - Task 1.3 UI Testing")
    print("=" * 70)

    results = []

    results.append(("File Structure", test_file_structure()))
    results.append(("Module Imports", test_imports()))
    results.append(("Placeholder Functions", test_placeholder_functions()))
    results.append(("File Line Counts", test_line_counts()))
    results.append(("TODO Markers", test_todo_markers()))

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:10} {test_name}")

    all_passed = all(result[1] for result in results)

    print("=" * 70)
    if all_passed:
        print("✓ All automated tests passed!")
        print("\nNext: Run 'streamlit run app.py' for manual UI testing")
    else:
        print("✗ Some tests failed. Please review errors above.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
