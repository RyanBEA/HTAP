"""
Parser for HTAP .run files
"""

import re
from pathlib import Path
from typing import Optional, List, Tuple

from src.models.run_config import (
    RunConfiguration,
    RunParameters,
    RunScope,
    OptionUpgrade,
    RunMode
)


class RunFileParser:
    """Parser for .run configuration files"""

    def __init__(self):
        self.current_section = None
        self.parameters_data = {}
        self.scope_data = {}
        self.upgrades_data = {}
        self.comments = []

    def parse_file(self, file_path: str) -> RunConfiguration:
        """
        Parse a .run file into RunConfiguration model

        Args:
            file_path: Path to .run file

        Returns:
            RunConfiguration model

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Run file not found: {file_path}")

        self._reset()

        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    self._parse_line(line)
                except Exception as e:
                    raise ValueError(
                        f"Error parsing line {line_num}: {line.strip()}\n{str(e)}"
                    )

        return self._build_configuration()

    def parse_string(self, content: str) -> RunConfiguration:
        """
        Parse .run file content from string

        Args:
            content: .run file content as string

        Returns:
            RunConfiguration model
        """
        self._reset()

        for line_num, line in enumerate(content.splitlines(), 1):
            try:
                self._parse_line(line)
            except Exception as e:
                raise ValueError(
                    f"Error parsing line {line_num}: {line.strip()}\n{str(e)}"
                )

        return self._build_configuration()

    def _reset(self) -> None:
        """Reset parser state"""
        self.current_section = None
        self.parameters_data = {}
        self.scope_data = {}
        self.upgrades_data = {}
        self.comments = []

    def _parse_line(self, line: str) -> None:
        """Parse a single line"""
        line = line.rstrip()

        # Skip empty lines
        if not line or line.isspace():
            return

        # Handle comments (preserve header comments only)
        if line.strip().startswith("!"):
            if self.current_section is None:
                self.comments.append(line.strip())
            return

        # Detect section markers
        if "RunParameters_START" in line:
            self.current_section = "parameters"
            return
        elif "RunParameters_END" in line:
            self.current_section = None
            return
        elif "RunScope_START" in line:
            self.current_section = "scope"
            return
        elif "RunScope_END" in line:
            self.current_section = None
            return
        elif "Upgrades_START" in line:
            self.current_section = "upgrades"
            return
        elif "Upgrades_END" in line:
            self.current_section = None
            return

        # Parse key-value pairs
        if "=" in line:
            key, value = self._parse_key_value(line)

            if self.current_section == "parameters":
                self.parameters_data[key] = value
            elif self.current_section == "scope":
                self.scope_data[key] = value
            elif self.current_section == "upgrades":
                self.upgrades_data[key] = value

    def _parse_key_value(self, line: str) -> Tuple[str, str]:
        """
        Parse key = value line

        Args:
            line: Line containing key = value

        Returns:
            Tuple of (key, value)
        """
        parts = line.split("=", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid key=value format: {line}")

        key = parts[0].strip()
        value = parts[1].strip()

        return key, value

    def _build_configuration(self) -> RunConfiguration:
        """Build RunConfiguration from parsed data"""

        # Build RunParameters
        parameters = RunParameters(
            run_mode=self.parameters_data.get("run-mode", "parametric"),
            archetype_dir=self.parameters_data.get(
                "archetype-dir",
                "C:/HTAP/archetypes"
            ),
            unit_costs_db=self.parameters_data.get(
                "unit-costs-db",
                "C:/HTAP/HTAPUnitCosts.json"
            ),
            options_file=self.parameters_data.get(
                "options-file",
                "C:/HTAP/HTAP-options.json"
            )
        )

        # Build RunScope
        scope = RunScope(
            archetypes=self.scope_data.get("archetypes", "*.H2K"),
            locations=self.scope_data.get("locations", "NA"),
            rulesets=self.scope_data.get("rulesets", "as-found")
        )

        # Build OptionUpgrades
        upgrades = {}
        for opt_type, choices_str in self.upgrades_data.items():
            if opt_type.startswith("Opt-"):
                upgrades[opt_type] = OptionUpgrade(
                    option_type=opt_type,
                    choices=choices_str
                )

        return RunConfiguration(
            parameters=parameters,
            scope=scope,
            upgrades=upgrades,
            comments=self.comments
        )


def parse_run_file(file_path: str) -> RunConfiguration:
    """
    Convenience function to parse a .run file

    Args:
        file_path: Path to .run file

    Returns:
        RunConfiguration model
    """
    parser = RunFileParser()
    return parser.parse_file(file_path)
