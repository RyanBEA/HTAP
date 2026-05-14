"""
Configuration validation for HTAP runs
Validates completeness, cost data, and configuration constraints
"""

from typing import Dict, List, Optional, Tuple, Set
from enum import Enum

from src.models.option import OptionsDatabase, OptionCategory, OptionChoice
from src.utils.cost_resolver import CostResolver


class ValidationSeverity(str, Enum):
    """Validation message severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ValidationMessage:
    """A validation message with severity and context"""

    def __init__(
        self,
        severity: ValidationSeverity,
        message: str,
        category: Optional[str] = None,
        field: Optional[str] = None
    ):
        self.severity = severity
        self.message = message
        self.category = category
        self.field = field

    def __repr__(self):
        context = f" [{self.category}]" if self.category else ""
        return f"{self.severity.value.upper()}{context}: {self.message}"

    def __eq__(self, other):
        """Allow equality comparison for testing"""
        if not isinstance(other, ValidationMessage):
            return False
        return (
            self.severity == other.severity and
            self.message == other.message and
            self.category == other.category and
            self.field == other.field
        )


class HTAPConfigValidator:
    """
    Validates HTAP run configurations
    """

    def __init__(
        self,
        options_db: OptionsDatabase,
        cost_resolver: Optional[CostResolver] = None
    ):
        """
        Initialize validator

        Args:
            options_db: Loaded options database
            cost_resolver: Optional cost resolver for cost validation
        """
        self.options_db = options_db
        self.cost_resolver = cost_resolver

    def validate_run_config(
        self,
        run_config: Dict
    ) -> List[ValidationMessage]:
        """
        Validate run configuration (LEFT panel data)

        Args:
            run_config: Dict with keys: archetypes, location, ruleset, cost_source

        Returns:
            List of validation messages
        """
        messages = []

        # Check archetypes
        archetypes = run_config.get('archetypes', [])
        if not archetypes:
            messages.append(ValidationMessage(
                ValidationSeverity.ERROR,
                "At least one archetype must be selected",
                field="archetypes"
            ))
        elif len(archetypes) > 10:
            messages.append(ValidationMessage(
                ValidationSeverity.WARNING,
                f"{len(archetypes)} archetypes selected. Large runs may take significant time.",
                field="archetypes"
            ))

        # Check location
        location = run_config.get('location')
        if not location:
            messages.append(ValidationMessage(
                ValidationSeverity.ERROR,
                "Location must be selected",
                field="location"
            ))

        # Check ruleset
        ruleset = run_config.get('ruleset')
        if not ruleset:
            messages.append(ValidationMessage(
                ValidationSeverity.WARNING,
                "No ruleset selected, using 'as-found'",
                field="ruleset"
            ))

        # Check cost source
        cost_source = run_config.get('cost_source')
        if not cost_source:
            messages.append(ValidationMessage(
                ValidationSeverity.WARNING,
                "No cost source selected, costs will not be calculated",
                field="cost_source"
            ))

        return messages

    def validate_selected_options(
        self,
        selected_options: Dict[str, Set[str]],
        cost_source: Optional[str] = None
    ) -> List[ValidationMessage]:
        """
        Validate selected options (MIDDLE panel data)

        Args:
            selected_options: Dict mapping category_name -> Set[choice_name]
            cost_source: Cost source for cost validation (optional)

        Returns:
            List of validation messages
        """
        messages = []

        for category_name, choice_set in selected_options.items():
            # Validate category exists
            if category_name not in self.options_db.categories:
                messages.append(ValidationMessage(
                    ValidationSeverity.ERROR,
                    f"Unknown category '{category_name}'",
                    category=category_name
                ))
                continue

            category = self.options_db.categories[category_name]

            # Iterate over each choice in the set
            for choice_name in choice_set:
                # Validate choice exists in category
                if choice_name not in category.options:
                    messages.append(ValidationMessage(
                        ValidationSeverity.ERROR,
                        f"Unknown choice '{choice_name}' in category '{category_name}'",
                        category=category_name
                    ))
                    continue

                choice = category.options[choice_name]

                # Validate cost completeness if category is costed
                if category.costed and self.cost_resolver and cost_source:
                    if not choice.costs or not choice.costs.components:
                        messages.append(ValidationMessage(
                            ValidationSeverity.WARNING,
                            f"Option '{choice_name}' has no cost data (category is marked as costed)",
                            category=category_name
                        ))
                    else:
                        # Check for missing cost components
                        is_valid, missing = self.cost_resolver.validate_option_costs(
                            choice,
                            cost_source
                        )
                        if not is_valid:
                            messages.append(ValidationMessage(
                                ValidationSeverity.WARNING,
                                f"Missing cost components: {', '.join(missing[:3])}"
                                + (f" and {len(missing)-3} more" if len(missing) > 3 else ""),
                                category=category_name
                            ))

        return messages

    def validate_configuration_completeness(
        self,
        selected_options: Dict[str, Set[str]]
    ) -> List[ValidationMessage]:
        """
        Check if configuration has selections for important categories

        Args:
            selected_options: Dict mapping category_name -> Set[choice_name]

        Returns:
            List of validation messages
        """
        messages = []

        # Define important categories that should have selections
        important_categories = [
            "Opt-Location",
            "Opt-Archetype",
            "Opt-Heating-Cooling",
            "Opt-DHWSystem",
            "Opt-VentSystem"
        ]

        for cat_name in important_categories:
            if cat_name in self.options_db.categories:
                if cat_name not in selected_options:
                    category = self.options_db.categories[cat_name]
                    default = category.default if hasattr(category, 'default') else None

                    if default:
                        messages.append(ValidationMessage(
                            ValidationSeverity.INFO,
                            f"No selection for '{cat_name}', will use default: '{default}'",
                            category=cat_name
                        ))
                    else:
                        messages.append(ValidationMessage(
                            ValidationSeverity.WARNING,
                            f"No selection for important category '{cat_name}'",
                            category=cat_name
                        ))

        return messages

    def get_category_status(
        self,
        category_name: str,
        selected_choice: Optional[str] = None,
        cost_source: Optional[str] = None
    ) -> Tuple[str, List[ValidationMessage]]:
        """
        Get status of a specific category

        Args:
            category_name: Category to check
            selected_choice: Currently selected choice (if any)
            cost_source: Cost source for cost validation

        Returns:
            Tuple of (status_icon, list_of_messages)
            status_icon: "✅" (valid), "⚠️" (warning), "❌" (error), "⬜" (not selected)
        """
        messages = []

        if category_name not in self.options_db.categories:
            return "❌", [ValidationMessage(
                ValidationSeverity.ERROR,
                f"Category '{category_name}' not found",
                category=category_name
            )]

        category = self.options_db.categories[category_name]

        # Not selected
        if not selected_choice:
            if category.default:
                return "⬜", [ValidationMessage(
                    ValidationSeverity.INFO,
                    f"Will use default: {category.default}",
                    category=category_name
                )]
            return "⬜", []

        # Selected but invalid choice
        if selected_choice not in category.options:
            return "❌", [ValidationMessage(
                ValidationSeverity.ERROR,
                f"Invalid choice '{selected_choice}'",
                category=category_name
            )]

        choice = category.options[selected_choice]

        # Check cost completeness
        has_warnings = False
        if category.costed and self.cost_resolver and cost_source:
            if not choice.costs or not choice.costs.components:
                messages.append(ValidationMessage(
                    ValidationSeverity.WARNING,
                    "No cost data available",
                    category=category_name
                ))
                has_warnings = True
            else:
                is_valid, missing = self.cost_resolver.validate_option_costs(
                    choice,
                    cost_source
                )
                if not is_valid:
                    messages.append(ValidationMessage(
                        ValidationSeverity.WARNING,
                        f"Missing {len(missing)} cost components",
                        category=category_name
                    ))
                    has_warnings = True

        if has_warnings:
            return "⚠️", messages

        return "✅", messages

    def validate_full_configuration(
        self,
        run_config: Dict,
        selected_options: Dict[str, Set[str]]
    ) -> Dict[str, List[ValidationMessage]]:
        """
        Perform comprehensive validation of entire configuration

        Args:
            run_config: Run configuration from LEFT panel
            selected_options: Selected options from MIDDLE panel (Dict[category -> Set[choices]])

        Returns:
            Dict with keys: 'run_config', 'options', 'completeness', 'summary'
            Each containing list of validation messages
        """
        cost_source = run_config.get('cost_source')

        return {
            'run_config': self.validate_run_config(run_config),
            'options': self.validate_selected_options(selected_options, cost_source),
            'completeness': self.validate_configuration_completeness(selected_options),
            'summary': self._generate_summary_messages(run_config, selected_options)
        }

    def _generate_summary_messages(
        self,
        run_config: Dict,
        selected_options: Dict[str, Set[str]]
    ) -> List[ValidationMessage]:
        """Generate overall configuration summary messages"""
        messages = []

        archetypes = run_config.get('archetypes', [])
        location = run_config.get('location')

        if archetypes and location:
            # Calculate number of combinations (multiply size of each set)
            num_combinations = 1
            for choice_set in selected_options.values():
                num_combinations *= len(choice_set)
            total_combinations = len(archetypes) * num_combinations

            if total_combinations > 500:
                messages.append(ValidationMessage(
                    ValidationSeverity.ERROR,
                    f"Configuration will generate {total_combinations} simulation runs. "
                    f"This is too large (max 500 recommended)."
                ))
            elif total_combinations > 100:
                messages.append(ValidationMessage(
                    ValidationSeverity.WARNING,
                    f"Configuration will generate {total_combinations} simulation runs. "
                    f"Large runs may take significant time."
                ))
            else:
                messages.append(ValidationMessage(
                    ValidationSeverity.INFO,
                    f"Configuration will generate {total_combinations} simulation runs"
                ))

        return messages

    def has_errors(self, messages: List[ValidationMessage]) -> bool:
        """Check if any messages are errors"""
        return any(msg.severity == ValidationSeverity.ERROR for msg in messages)

    def has_warnings(self, messages: List[ValidationMessage]) -> bool:
        """Check if any messages are warnings"""
        return any(msg.severity == ValidationSeverity.WARNING for msg in messages)
