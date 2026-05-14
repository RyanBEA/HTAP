"""
Run file generator for HTAP configuration files

This module generates .run files compatible with htap-prm.rb
"""

from typing import Dict, List, Optional, Set, Any, Tuple
from datetime import datetime
from pathlib import Path


class RunFileGenerator:
    """Generates HTAP .run configuration files"""

    DEFAULT_PARAMS = {
        'run-mode': 'mesh',
        'archetype-dir': 'C:/HTAP/archetypes',
        'options-file': 'C:/HTAP/HTAP-options.json',
        'unit-costs-db': 'C:/HTAP/HTAPUnitCosts.json',
        'output-folder': './output'
    }

    def __init__(self):
        """Initialize the run file generator"""
        pass

    def generate_run_file(
        self,
        run_config: Dict[str, Any],
        selected_options: Dict[str, Set[str]],
        custom_params: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate a complete .run file content

        Args:
            run_config: Dict with keys 'archetypes', 'location', 'ruleset', 'cost_source'
            selected_options: Dict[category_name, Set[choice_name]]
            custom_params: Optional dict to override DEFAULT_PARAMS

        Returns:
            Complete .run file content as string
        """
        lines = []

        # Header comment with timestamp
        lines.append("! Definitions file for HTAP-PRM RUN")
        lines.append(f"! Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # RunParameters section
        lines.append("! Run-Mode: Parameters that affect how htap-prm is configured.")
        lines.extend(self._generate_run_parameters(custom_params))
        lines.append("")
        lines.append("")

        # RunScope section
        lines.append("! Parameters controlling archetypes, locations, reference rulesets.")
        lines.extend(self._generate_run_scope(run_config))
        lines.append("")

        # Upgrades section
        lines.append("! Parameters controlling the design of the building")
        lines.extend(self._generate_upgrades(selected_options))
        lines.append("")

        return "\n".join(lines)

    def _generate_run_parameters(self, custom_params: Optional[Dict[str, str]] = None) -> List[str]:
        """
        Generate RunParameters section

        Args:
            custom_params: Optional dict to override defaults

        Returns:
            List of lines for RunParameters section
        """
        lines = ["RunParameters_START"]

        # Merge default and custom parameters
        params = self.DEFAULT_PARAMS.copy()
        if custom_params:
            params.update(custom_params)

        # Sort for consistency and format
        max_key_len = max(len(k) for k in params.keys())
        for key in sorted(params.keys()):
            value = params[key]
            # Format with alignment
            padded_key = key.ljust(max_key_len + 2)
            lines.append(f"  {padded_key} = {value}")

        lines.append("RunParameters_END")
        return lines

    def _generate_run_scope(self, run_config: Dict[str, Any]) -> List[str]:
        """
        Generate RunScope section

        Args:
            run_config: Dict with keys 'archetypes', 'location', 'ruleset'

        Returns:
            List of lines for RunScope section
        """
        lines = ["RunScope_START", ""]

        # Archetypes - can be list of filenames or wildcard
        archetypes = run_config.get('archetypes', [])
        if archetypes:
            if isinstance(archetypes, list) and archetypes:
                # Specific archetypes
                archetype_str = ", ".join(archetypes)
            else:
                archetype_str = "*.H2K"
        else:
            archetype_str = "*.H2K"

        lines.append(f"  archetypes                        = {archetype_str}")

        # Location
        location = run_config.get('location')
        if location:
            lines.append(f"  locations                         = {location}")
        else:
            lines.append("  locations                         = NA")

        # Ruleset
        ruleset = run_config.get('ruleset', 'as-found')
        lines.append(f"  rulesets                          = {ruleset}")

        lines.append("")
        lines.append("RunScope_END")
        return lines

    def _generate_upgrades(self, selected_options: Dict[str, Set[str]]) -> List[str]:
        """
        Generate Upgrades section

        Args:
            selected_options: Dict[category_name, Set[choice_name]]

        Returns:
            List of lines for Upgrades section
        """
        lines = ["Upgrades_START", ""]

        if not selected_options:
            lines.append("   ! No upgrades selected")
        else:
            # Sort categories for consistency
            for category in sorted(selected_options.keys()):
                choices = selected_options[category]
                if choices:
                    # Format: Opt-Category = choice1, choice2, choice3
                    # Sort choices for consistency
                    choices_str = ", ".join(sorted(choices))

                    # Pad category name for alignment (like HTAP does)
                    padded_category = category.ljust(20)
                    lines.append(f"   {padded_category} = {choices_str}")

        lines.append("")
        lines.append("Upgrades_END")
        return lines

    def save_to_file(self, content: str, filepath: str) -> None:
        """
        Save run file content to disk

        Args:
            content: The .run file content
            filepath: Path where to save the file

        Raises:
            IOError: If file cannot be written
        """
        path = Path(filepath)

        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write with UTF-8 encoding and Unix line endings
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)

    def validate_format(self, content: str) -> Tuple[bool, List[str]]:
        """
        Validate .run file format

        Args:
            content: The .run file content to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        lines = content.split('\n')

        # Check for required sections
        sections_found = {
            'RunParameters': False,
            'RunScope': False,
            'Upgrades': False
        }

        section_starts = {
            'RunParameters': False,
            'RunScope': False,
            'Upgrades': False
        }

        section_ends = {
            'RunParameters': False,
            'RunScope': False,
            'Upgrades': False
        }

        for line in lines:
            stripped = line.strip()

            # Check section starts
            if 'RunParameters_START' in stripped:
                section_starts['RunParameters'] = True
                sections_found['RunParameters'] = True
            elif 'RunScope_START' in stripped:
                section_starts['RunScope'] = True
                sections_found['RunScope'] = True
            elif 'Upgrades_START' in stripped:
                section_starts['Upgrades'] = True
                sections_found['Upgrades'] = True

            # Check section ends
            elif 'RunParameters_END' in stripped:
                section_ends['RunParameters'] = True
            elif 'RunScope_END' in stripped:
                section_ends['RunScope'] = True
            elif 'Upgrades_END' in stripped:
                section_ends['Upgrades'] = True

        # Validate all sections present
        for section in ['RunParameters', 'RunScope', 'Upgrades']:
            if not sections_found[section]:
                errors.append(f"Missing {section} section")
            else:
                if not section_starts[section]:
                    errors.append(f"Missing {section}_START tag")
                if not section_ends[section]:
                    errors.append(f"Missing {section}_END tag")

        # Check section order (RunParameters, RunScope, Upgrades)
        param_idx = -1
        scope_idx = -1
        upgrade_idx = -1

        for i, line in enumerate(lines):
            if 'RunParameters_START' in line:
                param_idx = i
            elif 'RunScope_START' in line:
                scope_idx = i
            elif 'Upgrades_START' in line:
                upgrade_idx = i

        if param_idx != -1 and scope_idx != -1 and param_idx > scope_idx:
            errors.append("RunParameters section must come before RunScope")

        if scope_idx != -1 and upgrade_idx != -1 and scope_idx > upgrade_idx:
            errors.append("RunScope section must come before Upgrades")

        is_valid = len(errors) == 0
        return (is_valid, errors)


class RunFileTemplate:
    """Provides templates for common run file configurations"""

    TEMPLATES = {
        'simple_single_run': {
            'name': 'Simple Single Run',
            'description': 'Single archetype, single location, minimal options',
            'run_mode': 'mesh',
            'example_note': 'Basic template for testing a single configuration'
        },
        'parametric_study': {
            'name': 'Parametric Study',
            'description': 'Multiple options across categories for comprehensive analysis',
            'run_mode': 'parametric',
            'example_note': 'Compare multiple options systematically'
        },
        'cost_optimization': {
            'name': 'Cost Optimization',
            'description': 'Run with cost calculations enabled',
            'run_mode': 'mesh',
            'example_note': 'Evaluate cost-effectiveness of upgrades',
            'custom_params': {
                'compute-costs': 'true'
            }
        },
        'location_comparison': {
            'name': 'Location Comparison',
            'description': 'Same configuration across multiple locations',
            'run_mode': 'mesh',
            'example_note': 'Compare building performance across regions'
        }
    }

    @classmethod
    def get_template_names(cls) -> List[str]:
        """
        Get list of available template names

        Returns:
            List of template names
        """
        return list(cls.TEMPLATES.keys())

    @classmethod
    def get_template(cls, name: str) -> Optional[Dict[str, Any]]:
        """
        Get template configuration by name

        Args:
            name: Template name

        Returns:
            Template dict or None if not found
        """
        return cls.TEMPLATES.get(name)

    @classmethod
    def get_all_templates(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get all templates

        Returns:
            Dict of all templates
        """
        return cls.TEMPLATES.copy()
