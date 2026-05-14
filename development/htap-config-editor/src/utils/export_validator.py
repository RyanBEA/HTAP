"""
Export validation for HTAP run configurations

This module validates configurations before export to ensure they are complete
and will generate valid .run files. It provides comprehensive pre-export checks
with clear, actionable feedback.
"""

from typing import Dict, List, Set, Tuple, Optional
from enum import Enum
from pathlib import Path

from src.models.option import OptionsDatabase
from src.utils.validator import HTAPConfigValidator, ValidationMessage, ValidationSeverity
from src.utils.run_file_generator import RunFileGenerator


class ExportReadiness(str, Enum):
    """Export readiness states"""
    READY = "ready"  # Configuration is valid, can export
    WARNINGS = "warnings"  # Has warnings but can export
    BLOCKED = "blocked"  # Has errors, cannot export


class ExportValidator:
    """
    Validates configurations for export readiness

    Performs comprehensive validation before allowing export to ensure:
    - Run configuration is complete (archetypes, location)
    - Selected options are valid
    - Configuration will generate valid .run file
    - No critical errors that would cause htap-prm.rb to fail
    """

    def __init__(
        self,
        options_db: OptionsDatabase,
        config_validator: HTAPConfigValidator
    ):
        """
        Initialize export validator

        Args:
            options_db: Loaded options database
            config_validator: Configuration validator instance
        """
        self.options_db = options_db
        self.config_validator = config_validator
        self.run_file_generator = RunFileGenerator()

    def check_export_readiness(
        self,
        run_config: Dict,
        selected_options: Dict[str, Set[str]]
    ) -> Tuple[ExportReadiness, List[ValidationMessage]]:
        """
        Check if configuration is ready for export

        Args:
            run_config: Dict with keys: archetypes, location, ruleset, cost_source
            selected_options: Dict[category_name, Set[choice_name]]

        Returns:
            Tuple of (readiness_state, list_of_validation_messages)
        """
        messages = []

        # 1. Validate run configuration
        messages.extend(self._validate_run_config(run_config))

        # 2. Validate selected options
        messages.extend(self._validate_options(selected_options))

        # 3. Validate completeness
        messages.extend(self._validate_completeness(run_config, selected_options))

        # 4. Validate export format
        messages.extend(self._validate_export_format(run_config, selected_options))

        # Determine readiness state
        has_errors = any(msg.severity == ValidationSeverity.ERROR for msg in messages)
        has_warnings = any(msg.severity == ValidationSeverity.WARNING for msg in messages)

        if has_errors:
            return ExportReadiness.BLOCKED, messages
        elif has_warnings:
            return ExportReadiness.WARNINGS, messages
        else:
            return ExportReadiness.READY, messages

    def _validate_run_config(self, run_config: Dict) -> List[ValidationMessage]:
        """
        Validate run configuration

        Args:
            run_config: Run configuration dict

        Returns:
            List of validation messages
        """
        messages = []

        # Check archetypes (CRITICAL - blocks export)
        archetypes = run_config.get('archetypes', [])
        if not archetypes or len(archetypes) == 0:
            messages.append(ValidationMessage(
                ValidationSeverity.ERROR,
                "At least one archetype must be selected. Configure archetypes in the left panel.",
                field="archetypes"
            ))
        elif len(archetypes) > 10:
            messages.append(ValidationMessage(
                ValidationSeverity.WARNING,
                f"{len(archetypes)} archetypes selected. Large runs may take significant time "
                f"(estimated {len(archetypes) * 2} minutes per option combination).",
                field="archetypes"
            ))

        # Check location (CRITICAL - blocks export)
        location = run_config.get('location')
        if not location:
            messages.append(ValidationMessage(
                ValidationSeverity.ERROR,
                "Location must be selected. Choose a location in the left panel.",
                field="location"
            ))

        # Check ruleset (WARNING - will use 'as-found')
        ruleset = run_config.get('ruleset')
        if not ruleset:
            messages.append(ValidationMessage(
                ValidationSeverity.WARNING,
                "No ruleset selected. Will use 'as-found' (no building code compliance checks).",
                field="ruleset"
            ))

        # Optional: Check archetype files exist (WARNING only, don't block)
        if archetypes:
            archetype_dir = Path("C:/HTAP/archetypes")
            if archetype_dir.exists():
                missing_files = []
                for arch in archetypes:
                    arch_path = archetype_dir / arch
                    if not arch_path.exists():
                        missing_files.append(arch)

                if missing_files:
                    messages.append(ValidationMessage(
                        ValidationSeverity.WARNING,
                        f"Archetype files not found: {', '.join(missing_files[:3])}"
                        + (f" and {len(missing_files)-3} more" if len(missing_files) > 3 else ""),
                        field="archetypes"
                    ))

        return messages

    def _validate_options(self, selected_options: Dict[str, Set[str]]) -> List[ValidationMessage]:
        """
        Validate selected options

        Args:
            selected_options: Dict[category_name, Set[choice_name]]

        Returns:
            List of validation messages
        """
        messages = []

        # Check if any options selected (INFO only, not blocking)
        if not selected_options or len(selected_options) == 0:
            messages.append(ValidationMessage(
                ValidationSeverity.INFO,
                "No upgrade options selected. Run will use archetype defaults for all parameters.",
                field="options"
            ))
            return messages

        # Validate each category and choice exists
        for category_name, choices in selected_options.items():
            # Validate category exists
            if category_name not in self.options_db.categories:
                messages.append(ValidationMessage(
                    ValidationSeverity.ERROR,
                    f"Unknown category '{category_name}'. This category does not exist in HTAP-options.json.",
                    category=category_name
                ))
                continue

            category = self.options_db.categories[category_name]

            # Validate each choice exists in category
            for choice_name in choices:
                if choice_name not in category.options:
                    messages.append(ValidationMessage(
                        ValidationSeverity.ERROR,
                        f"Unknown choice '{choice_name}' in category '{category_name}'. "
                        f"This choice does not exist in HTAP-options.json.",
                        category=category_name
                    ))

        return messages

    def _validate_completeness(
        self,
        run_config: Dict,
        selected_options: Dict[str, Set[str]]
    ) -> List[ValidationMessage]:
        """
        Validate configuration completeness

        Args:
            run_config: Run configuration dict
            selected_options: Dict[category_name, Set[choice_name]]

        Returns:
            List of validation messages
        """
        messages = []

        # Check for important categories without selections (INFO only)
        important_categories = [
            "Opt-Heating-Cooling",
            "Opt-DHWSystem",
            "Opt-VentSystem",
            "Opt-Windows",
            "Opt-Ceilings"
        ]

        unselected_important = []
        for cat_name in important_categories:
            if cat_name in self.options_db.categories:
                if cat_name not in selected_options or not selected_options[cat_name]:
                    unselected_important.append(cat_name)

        if unselected_important:
            messages.append(ValidationMessage(
                ValidationSeverity.INFO,
                f"No selections for important categories: {', '.join(unselected_important[:3])}"
                + (f" and {len(unselected_important)-3} more" if len(unselected_important) > 3 else "")
                + ". These will use archetype defaults.",
                field="completeness"
            ))

        # Check total combinations
        num_combinations = self._count_combinations(run_config, selected_options)

        if num_combinations == 0:
            messages.append(ValidationMessage(
                ValidationSeverity.ERROR,
                "Configuration will generate 0 simulation runs. Select at least one archetype.",
                field="combinations"
            ))
        elif num_combinations > 1000:
            estimated_hours = (num_combinations * 2) / 60  # 2 min per run
            messages.append(ValidationMessage(
                ValidationSeverity.WARNING,
                f"Configuration will generate {num_combinations} simulation runs. "
                f"This may take {estimated_hours:.1f} hours to complete. "
                f"Consider reducing the number of options or archetypes.",
                field="combinations"
            ))
        elif num_combinations > 100:
            estimated_minutes = num_combinations * 2  # 2 min per run
            messages.append(ValidationMessage(
                ValidationSeverity.WARNING,
                f"Configuration will generate {num_combinations} simulation runs. "
                f"This may take approximately {estimated_minutes} minutes to complete.",
                field="combinations"
            ))
        else:
            estimated_minutes = num_combinations * 2
            messages.append(ValidationMessage(
                ValidationSeverity.INFO,
                f"Configuration will generate {num_combinations} simulation run(s). "
                f"Estimated time: {estimated_minutes} minutes.",
                field="combinations"
            ))

        return messages

    def _validate_export_format(
        self,
        run_config: Dict,
        selected_options: Dict[str, Set[str]]
    ) -> List[ValidationMessage]:
        """
        Validate that configuration can generate valid .run file

        Args:
            run_config: Run configuration dict
            selected_options: Dict[category_name, Set[choice_name]]

        Returns:
            List of validation messages
        """
        messages = []

        try:
            # Generate run file content
            run_file_content = self.run_file_generator.generate_run_file(
                run_config,
                selected_options
            )

            # Validate format
            is_valid, format_errors = self.run_file_generator.validate_format(run_file_content)

            if not is_valid:
                for error in format_errors:
                    messages.append(ValidationMessage(
                        ValidationSeverity.ERROR,
                        f"Run file format error: {error}",
                        field="format"
                    ))

        except Exception as e:
            messages.append(ValidationMessage(
                ValidationSeverity.ERROR,
                f"Failed to generate run file: {str(e)}",
                field="format"
            ))

        return messages

    def _count_combinations(
        self,
        run_config: Dict,
        selected_options: Dict[str, Set[str]]
    ) -> int:
        """
        Count total number of simulation combinations

        Args:
            run_config: Run configuration dict
            selected_options: Dict[category_name, Set[choice_name]]

        Returns:
            Number of combinations
        """
        total = 1

        # Multiply by number of archetypes
        archetypes = run_config.get('archetypes', [])
        if archetypes:
            total *= len(archetypes)
        else:
            return 0  # No archetypes = 0 runs

        # Multiply by number of choices in each category
        for choices in selected_options.values():
            if choices:
                total *= len(choices)

        return total

    def generate_validation_report(
        self,
        run_config: Dict,
        selected_options: Dict[str, Set[str]]
    ) -> str:
        """
        Generate a detailed validation report in markdown format

        Args:
            run_config: Run configuration dict
            selected_options: Dict[category_name, Set[choice_name]]

        Returns:
            Markdown formatted validation report
        """
        readiness, messages = self.check_export_readiness(run_config, selected_options)

        lines = []
        lines.append("# HTAP Configuration Validation Report")
        lines.append("")
        lines.append(f"**Generated:** {self._get_timestamp()}")
        lines.append("")

        # Overall status
        lines.append("## Export Readiness")
        lines.append("")
        if readiness == ExportReadiness.READY:
            lines.append("✅ **READY** - Configuration is valid and ready for export")
        elif readiness == ExportReadiness.WARNINGS:
            lines.append("⚠️ **WARNINGS** - Configuration has warnings but can be exported")
        else:
            lines.append("❌ **BLOCKED** - Configuration has errors and cannot be exported")
        lines.append("")

        # Configuration summary
        lines.append("## Configuration Summary")
        lines.append("")
        archetypes = run_config.get('archetypes', [])
        location = run_config.get('location', 'NA')
        ruleset = run_config.get('ruleset', 'as-found')
        num_combinations = self._count_combinations(run_config, selected_options)

        lines.append(f"- **Archetypes:** {len(archetypes)}")
        lines.append(f"- **Location:** {location}")
        lines.append(f"- **Ruleset:** {ruleset}")
        lines.append(f"- **Option Categories:** {len(selected_options)}")
        lines.append(f"- **Total Simulation Runs:** {num_combinations}")
        lines.append("")

        # Validation messages
        errors = [m for m in messages if m.severity == ValidationSeverity.ERROR]
        warnings = [m for m in messages if m.severity == ValidationSeverity.WARNING]
        infos = [m for m in messages if m.severity == ValidationSeverity.INFO]

        if errors:
            lines.append("## ❌ Errors")
            lines.append("")
            for msg in errors:
                category_tag = f" [{msg.category}]" if msg.category else ""
                field_tag = f" ({msg.field})" if msg.field else ""
                lines.append(f"- {msg.message}{category_tag}{field_tag}")
            lines.append("")

        if warnings:
            lines.append("## ⚠️ Warnings")
            lines.append("")
            for msg in warnings:
                category_tag = f" [{msg.category}]" if msg.category else ""
                field_tag = f" ({msg.field})" if msg.field else ""
                lines.append(f"- {msg.message}{category_tag}{field_tag}")
            lines.append("")

        if infos:
            lines.append("## ℹ️ Information")
            lines.append("")
            for msg in infos:
                category_tag = f" [{msg.category}]" if msg.category else ""
                field_tag = f" ({msg.field})" if msg.field else ""
                lines.append(f"- {msg.message}{category_tag}{field_tag}")
            lines.append("")

        # Next steps
        lines.append("## Next Steps")
        lines.append("")
        if readiness == ExportReadiness.BLOCKED:
            lines.append("1. Fix all errors listed above")
            lines.append("2. Re-run validation")
            lines.append("3. Export when validation passes")
        elif readiness == ExportReadiness.WARNINGS:
            lines.append("1. Review warnings above")
            lines.append("2. Export if warnings are acceptable")
            lines.append("3. Or modify configuration to address warnings")
        else:
            lines.append("1. Review configuration summary")
            lines.append("2. Export .run file")
            lines.append("3. Run with htap-prm.rb")
        lines.append("")

        return "\n".join(lines)

    def _get_timestamp(self) -> str:
        """Get current timestamp for report"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
