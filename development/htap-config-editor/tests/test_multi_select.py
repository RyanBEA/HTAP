"""
Unit tests for multi-select functionality
"""

import pytest
from unittest.mock import patch, MagicMock


# Mock streamlit session state for testing
class MockSessionState(dict):
    """Mock Streamlit session state that behaves like a dict"""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        self[key] = value


@pytest.fixture
def mock_session_state():
    """Fixture to provide clean mock session state for each test"""
    mock_state = MockSessionState()

    # Patch st.session_state
    with patch('streamlit.session_state', mock_state):
        # Also patch it in the state_manager module
        import src.ui.state_manager as sm
        sm.st.session_state = mock_state
        yield mock_state


class TestMultiSelectState:
    """Test multi-select state management"""

    def test_initialize_session_state(self, mock_session_state):
        """Test session state initialization"""
        from src.ui.state_manager import initialize_session_state

        initialize_session_state()

        assert 'multi_select_mode' in mock_session_state
        assert mock_session_state['multi_select_mode'] == False
        assert 'selected_options' in mock_session_state
        assert isinstance(mock_session_state['selected_options'], dict)

    def test_toggle_selection_mode(self, mock_session_state):
        """Test toggling selection mode"""
        from src.ui.state_manager import initialize_session_state, toggle_selection_mode

        initialize_session_state()

        # Initially False
        assert mock_session_state['multi_select_mode'] == False

        # Toggle to True
        toggle_selection_mode()
        assert mock_session_state['multi_select_mode'] == True

        # Toggle back to False
        toggle_selection_mode()
        assert mock_session_state['multi_select_mode'] == False

    def test_add_single_selection(self, mock_session_state):
        """Test adding single selection"""
        from src.ui.state_manager import initialize_session_state, add_option_selection

        initialize_session_state()
        mock_session_state['multi_select_mode'] = False

        add_option_selection("Opt-Windows", "Choice1")

        assert "Opt-Windows" in mock_session_state['selected_options']
        assert "Choice1" in mock_session_state['selected_options']["Opt-Windows"]

    def test_add_multiple_selections(self, mock_session_state):
        """Test adding multiple selections in multi-select mode"""
        from src.ui.state_manager import initialize_session_state, add_option_selection, get_selected_choices

        initialize_session_state()
        mock_session_state['multi_select_mode'] = True

        add_option_selection("Opt-Windows", "Choice1")
        add_option_selection("Opt-Windows", "Choice2")
        add_option_selection("Opt-Windows", "Choice3")

        choices = get_selected_choices("Opt-Windows")
        assert len(choices) == 3
        assert "Choice1" in choices
        assert "Choice2" in choices
        assert "Choice3" in choices

    def test_single_select_replaces(self, mock_session_state):
        """Test that single-select mode replaces previous selection"""
        from src.ui.state_manager import initialize_session_state, add_option_selection, get_selected_choices

        initialize_session_state()
        mock_session_state['multi_select_mode'] = False

        add_option_selection("Opt-Windows", "Choice1")
        add_option_selection("Opt-Windows", "Choice2")

        choices = get_selected_choices("Opt-Windows")
        assert len(choices) == 1
        assert "Choice2" in choices

    def test_remove_selection(self, mock_session_state):
        """Test removing a selection"""
        from src.ui.state_manager import (
            initialize_session_state,
            remove_option_selection,
            get_selected_choices
        )

        initialize_session_state()
        mock_session_state['selected_options'] = {
            "Opt-Windows": {"Choice1", "Choice2", "Choice3"}
        }

        remove_option_selection("Opt-Windows", "Choice2")

        choices = get_selected_choices("Opt-Windows")
        assert len(choices) == 2
        assert "Choice2" not in choices
        assert "Choice1" in choices
        assert "Choice3" in choices

    def test_remove_last_selection_cleans_up(self, mock_session_state):
        """Test that removing last selection cleans up empty category"""
        from src.ui.state_manager import (
            initialize_session_state,
            remove_option_selection
        )

        initialize_session_state()
        mock_session_state['selected_options'] = {
            "Opt-Windows": {"Choice1"}
        }

        remove_option_selection("Opt-Windows", "Choice1")

        assert "Opt-Windows" not in mock_session_state['selected_options']

    def test_clear_category(self, mock_session_state):
        """Test clearing all selections for a category"""
        from src.ui.state_manager import (
            initialize_session_state,
            clear_category_selections
        )

        initialize_session_state()
        mock_session_state['selected_options'] = {
            "Opt-Windows": {"Choice1", "Choice2"},
            "Opt-Walls": {"WallChoice1"}
        }

        clear_category_selections("Opt-Windows")

        assert "Opt-Windows" not in mock_session_state['selected_options']
        assert "Opt-Walls" in mock_session_state['selected_options']

    def test_is_choice_selected(self, mock_session_state):
        """Test checking if choice is selected"""
        from src.ui.state_manager import (
            initialize_session_state,
            is_choice_selected
        )

        initialize_session_state()
        mock_session_state['selected_options'] = {
            "Opt-Windows": {"Choice1", "Choice2"}
        }

        assert is_choice_selected("Opt-Windows", "Choice1") == True
        assert is_choice_selected("Opt-Windows", "Choice2") == True
        assert is_choice_selected("Opt-Windows", "Choice3") == False
        assert is_choice_selected("Opt-Walls", "Wall1") == False

    def test_toggle_to_single_reduces_selections(self, mock_session_state):
        """Test that toggling to single-select keeps only first choice"""
        from src.ui.state_manager import (
            initialize_session_state,
            toggle_selection_mode,
            get_selected_choices
        )

        initialize_session_state()
        mock_session_state['multi_select_mode'] = True
        mock_session_state['selected_options'] = {
            "Opt-Windows": {"Choice1", "Choice2", "Choice3"}
        }

        # Toggle to single-select
        toggle_selection_mode()

        choices = get_selected_choices("Opt-Windows")
        assert len(choices) == 1


class TestCombinationCounting:
    """Test counting total combinations"""

    def test_single_category_single_choice(self, mock_session_state):
        """Test counting with one category, one choice"""
        from src.ui.state_manager import initialize_session_state, get_total_combinations

        initialize_session_state()
        mock_session_state['selected_options'] = {
            "Opt-Windows": {"Choice1"}
        }
        mock_session_state['run_config'] = {'archetypes': ['arch1.h2k']}

        total = get_total_combinations()
        assert total == 1

    def test_single_category_multiple_choices(self, mock_session_state):
        """Test counting with one category, multiple choices"""
        from src.ui.state_manager import initialize_session_state, get_total_combinations

        initialize_session_state()
        mock_session_state['selected_options'] = {
            "Opt-Windows": {"Choice1", "Choice2", "Choice3"}
        }
        mock_session_state['run_config'] = {'archetypes': ['arch1.h2k']}

        total = get_total_combinations()
        assert total == 3

    def test_multiple_categories(self, mock_session_state):
        """Test counting with multiple categories"""
        from src.ui.state_manager import initialize_session_state, get_total_combinations

        initialize_session_state()
        mock_session_state['selected_options'] = {
            "Opt-Windows": {"Choice1", "Choice2"},
            "Opt-Walls": {"Wall1", "Wall2", "Wall3"},
            "Opt-Ceilings": {"Ceil1"}
        }
        mock_session_state['run_config'] = {'archetypes': ['arch1.h2k']}

        total = get_total_combinations()
        assert total == 2 * 3 * 1  # 6

    def test_with_multiple_archetypes(self, mock_session_state):
        """Test counting with multiple archetypes"""
        from src.ui.state_manager import initialize_session_state, get_total_combinations

        initialize_session_state()
        mock_session_state['selected_options'] = {
            "Opt-Windows": {"Choice1", "Choice2"}
        }
        mock_session_state['run_config'] = {
            'archetypes': ['arch1.h2k', 'arch2.h2k', 'arch3.h2k']
        }

        total = get_total_combinations()
        assert total == 3 * 2  # 6

    def test_no_selections(self, mock_session_state):
        """Test counting with no selections"""
        from src.ui.state_manager import initialize_session_state, get_total_combinations

        initialize_session_state()
        mock_session_state['selected_options'] = {}
        mock_session_state['run_config'] = {'archetypes': ['arch1.h2k']}

        total = get_total_combinations()
        assert total == 1

    def test_no_archetypes(self, mock_session_state):
        """Test counting with no archetypes"""
        from src.ui.state_manager import initialize_session_state, get_total_combinations

        initialize_session_state()
        mock_session_state['selected_options'] = {
            "Opt-Windows": {"Choice1", "Choice2"}
        }
        mock_session_state['run_config'] = {'archetypes': []}

        total = get_total_combinations()
        # With no archetypes, still counts option combinations
        assert total == 2


class TestExportFormat:
    """Test export format for .run files"""

    def test_format_single_category(self):
        """Test formatting single category"""
        from src.utils.export_helpers import format_upgrades_section

        selected = {
            "Opt-Windows": {"Choice1", "Choice2"}
        }

        output = format_upgrades_section(selected)

        assert "Upgrades_START" in output
        assert "Upgrades_END" in output
        assert "Opt-Windows = Choice1, Choice2" in output or \
               "Opt-Windows = Choice2, Choice1" in output

    def test_format_multiple_categories(self):
        """Test formatting multiple categories"""
        from src.utils.export_helpers import format_upgrades_section

        selected = {
            "Opt-Windows": {"WinChoice1"},
            "Opt-Walls": {"Wall1", "Wall2"},
            "Opt-Ceilings": {"Ceil1"}
        }

        output = format_upgrades_section(selected)

        assert "Opt-Windows = WinChoice1" in output
        assert "Opt-Walls" in output
        assert "Wall1" in output
        assert "Wall2" in output
        assert "Opt-Ceilings = Ceil1" in output

    def test_format_sorted_categories(self):
        """Test that categories are sorted alphabetically"""
        from src.utils.export_helpers import format_upgrades_section

        selected = {
            "Opt-Walls": {"Wall1"},
            "Opt-Ceilings": {"Ceil1"},
            "Opt-AboveGradeWall": {"AGW1"}
        }

        output = format_upgrades_section(selected)
        lines = output.split('\n')

        # Should be sorted: AboveGradeWall, Ceilings, Walls
        assert lines[1].strip().startswith("Opt-AboveGradeWall")
        assert lines[2].strip().startswith("Opt-Ceilings")
        assert lines[3].strip().startswith("Opt-Walls")

    def test_format_empty_selections(self):
        """Test formatting with no selections"""
        from src.utils.export_helpers import format_upgrades_section

        selected = {}

        output = format_upgrades_section(selected)

        assert output == "Upgrades_START\nUpgrades_END"

    def test_count_combinations_helper(self):
        """Test standalone combination counter"""
        from src.utils.export_helpers import count_combinations

        selected = {
            "Opt-Windows": {"Choice1", "Choice2"},
            "Opt-Walls": {"Wall1", "Wall2", "Wall3"}
        }

        count = count_combinations(selected, num_archetypes=1)
        assert count == 2 * 3  # 6

        count = count_combinations(selected, num_archetypes=2)
        assert count == 2 * 2 * 3  # 12

    def test_validate_export_ready_valid(self):
        """Test export validation with valid config"""
        from src.utils.export_helpers import validate_export_ready

        is_valid, errors = validate_export_ready(
            selected_options={"Opt-Windows": {"Choice1"}},
            archetypes=["arch1.h2k"],
            location="Ottawa"
        )

        assert is_valid == True
        assert len(errors) == 0

    def test_validate_export_ready_missing_archetypes(self):
        """Test export validation with missing archetypes"""
        from src.utils.export_helpers import validate_export_ready

        is_valid, errors = validate_export_ready(
            selected_options={"Opt-Windows": {"Choice1"}},
            archetypes=[],
            location="Ottawa"
        )

        assert is_valid == False
        assert "No archetypes selected" in errors

    def test_validate_export_ready_missing_location(self):
        """Test export validation with missing location"""
        from src.utils.export_helpers import validate_export_ready

        is_valid, errors = validate_export_ready(
            selected_options={"Opt-Windows": {"Choice1"}},
            archetypes=["arch1.h2k"],
            location=None
        )

        assert is_valid == False
        assert "No location selected" in errors

    def test_validate_export_ready_missing_options(self):
        """Test export validation with missing options"""
        from src.utils.export_helpers import validate_export_ready

        is_valid, errors = validate_export_ready(
            selected_options={},
            archetypes=["arch1.h2k"],
            location="Ottawa"
        )

        assert is_valid == False
        assert "No options selected" in errors


class TestBackwardCompatibility:
    """Test backward compatibility with old single-select format"""

    def test_get_selected_option_returns_first(self, mock_session_state):
        """Test that get_selected_option returns first choice"""
        from src.ui.state_manager import initialize_session_state, get_selected_option

        initialize_session_state()
        mock_session_state['selected_options'] = {
            "Opt-Windows": {"Choice1", "Choice2", "Choice3"}
        }

        result = get_selected_option("Opt-Windows")
        assert result in ["Choice1", "Choice2", "Choice3"]

    def test_get_selected_choices_handles_string(self, mock_session_state):
        """Test that get_selected_choices handles old string format"""
        from src.ui.state_manager import initialize_session_state, get_selected_choices

        initialize_session_state()
        # Simulate old format where value was a string
        mock_session_state['selected_options'] = {
            "Opt-Windows": "Choice1"
        }

        choices = get_selected_choices("Opt-Windows")
        assert isinstance(choices, set)
        assert "Choice1" in choices
        assert len(choices) == 1
