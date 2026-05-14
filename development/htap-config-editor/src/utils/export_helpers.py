"""
Helper functions for exporting configurations to .run file format
"""

from typing import Dict, Set


def format_upgrades_section(selected_options: Dict[str, Set[str]]) -> str:
    """
    Format selected options as Upgrades section for .run file

    Args:
        selected_options: Dict mapping category -> set of choices

    Returns:
        Formatted string for Upgrades section

    Example:
        >>> selected = {
        ...     "Opt-Windows": {"Choice1", "Choice2"},
        ...     "Opt-Walls": {"Wall1"}
        ... }
        >>> print(format_upgrades_section(selected))
        Upgrades_START
          Opt-Walls = Wall1
          Opt-Windows = Choice1, Choice2
        Upgrades_END
    """
    lines = ["Upgrades_START"]

    for category in sorted(selected_options.keys()):
        choices = selected_options[category]
        if choices:
            # Join choices with ", " (comma + space)
            choices_str = ", ".join(sorted(choices))
            lines.append(f"  {category} = {choices_str}")

    lines.append("Upgrades_END")

    return "\n".join(lines)


def count_combinations(selected_options: Dict[str, Set[str]], num_archetypes: int = 1) -> int:
    """
    Count total number of combinations

    Args:
        selected_options: Dict mapping category -> set of choices
        num_archetypes: Number of archetypes (default 1)

    Returns:
        Total number of combinations

    Example:
        >>> selected = {
        ...     "Opt-Windows": {"Choice1", "Choice2"},
        ...     "Opt-Walls": {"Wall1", "Wall2", "Wall3"}
        ... }
        >>> count_combinations(selected, num_archetypes=2)
        12
    """
    total = num_archetypes if num_archetypes > 0 else 1

    # Multiply by number of choices in each category
    for choices in selected_options.values():
        if choices:
            total *= len(choices)

    return total


def validate_export_ready(
    selected_options: Dict[str, Set[str]],
    archetypes: list,
    location: str
) -> tuple[bool, list[str]]:
    """
    Validate that configuration is ready for export

    Args:
        selected_options: Selected options dict
        archetypes: List of archetype file paths
        location: Weather location

    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []

    if not archetypes:
        errors.append("No archetypes selected")

    if not location:
        errors.append("No location selected")

    if not selected_options:
        errors.append("No options selected")

    return len(errors) == 0, errors
