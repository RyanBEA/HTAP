#!/usr/bin/env python3
"""
Configuration loader for H2K to NBC form mapping.
Loads and provides access to mapping configuration.
"""

import json
from pathlib import Path


class ConfigLoader:
    """Loads and provides access to H2K to NBC mapping configuration."""

    def __init__(self, config_path):
        """
        Initialize configuration loader.

        Args:
            config_path: Path to the JSON configuration file
        """
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    def get_metadata(self):
        """Get configuration metadata."""
        return self.config.get('metadata', {})

    def get_data_sources(self):
        """Get data source configuration."""
        return self.config.get('data_sources', {})

    def get_field_mappings(self):
        """Get all field mappings."""
        return self.config.get('field_mappings', [])

    def get_formula(self, formula_name):
        """
        Get a formula definition by name.

        Args:
            formula_name: Name of the formula to retrieve

        Returns:
            Formula definition dict or None if not found
        """
        return self.config.get('formulas', {}).get(formula_name)

    def get_all_formulas(self):
        """Get all formula definitions."""
        return self.config.get('formulas', {})

    def get_transformation(self, transform_name):
        """
        Get a transformation definition by name.

        Args:
            transform_name: Name of the transformation to retrieve

        Returns:
            Transformation definition dict or None if not found
        """
        return self.config.get('transformations', {}).get(transform_name)

    def get_all_transformations(self):
        """Get all transformation definitions."""
        return self.config.get('transformations', {})

    def get_complex_mapping(self, mapping_name):
        """
        Get a complex mapping definition by name.

        Args:
            mapping_name: Name of the complex mapping to retrieve

        Returns:
            Complex mapping definition dict or None if not found
        """
        return self.config.get('complex_mappings', {}).get(mapping_name)

    def get_all_complex_mappings(self):
        """Get all complex mapping definitions."""
        return self.config.get('complex_mappings', {})

    def get_fields_by_source(self, source):
        """
        Get all field mappings for a specific data source.

        Args:
            source: Data source name ('reference' or 'proposed')

        Returns:
            List of field mappings for the specified source
        """
        return [
            mapping for mapping in self.get_field_mappings()
            if mapping.get('source') == source
        ]

    def validate_config(self):
        """
        Validate the configuration structure.

        Returns:
            Tuple of (is_valid, errors) where errors is a list of validation error messages
        """
        errors = []

        # Check required top-level keys
        required_keys = ['metadata', 'data_sources', 'field_mappings', 'transformations']
        for key in required_keys:
            if key not in self.config:
                errors.append(f"Missing required configuration key: {key}")

        # Validate field mappings
        for i, mapping in enumerate(self.get_field_mappings()):
            if 'nbc_field' not in mapping:
                errors.append(f"Field mapping {i} missing 'nbc_field'")
            if 'source' not in mapping:
                errors.append(f"Field mapping {i} ({mapping.get('nbc_field', 'unknown')}) missing 'source'")

            # Must have one of: xpath, xpath_list, formula, or complex_mapping
            has_data_source = any(key in mapping for key in ['xpath', 'xpath_list', 'formula', 'complex_mapping'])
            if not has_data_source:
                errors.append(f"Field mapping {mapping.get('nbc_field', 'unknown')} missing data source (xpath/xpath_list/formula/complex_mapping)")

        # Validate formula references
        for mapping in self.get_field_mappings():
            if 'formula' in mapping:
                formula_name = mapping['formula']
                if formula_name not in self.get_all_formulas():
                    errors.append(f"Field {mapping.get('nbc_field')} references undefined formula: {formula_name}")

        # Validate transformation references
        for mapping in self.get_field_mappings():
            if 'transform' in mapping:
                transform_name = mapping['transform']
                if transform_name not in self.get_all_transformations():
                    errors.append(f"Field {mapping.get('nbc_field')} references undefined transformation: {transform_name}")

        # Validate complex mapping references
        for mapping in self.get_field_mappings():
            if 'complex_mapping' in mapping:
                complex_name = mapping['complex_mapping']
                if complex_name not in self.get_all_complex_mappings():
                    errors.append(f"Field {mapping.get('nbc_field')} references undefined complex mapping: {complex_name}")

        return (len(errors) == 0, errors)


if __name__ == '__main__':
    # Test configuration loading
    import sys

    config_file = 'h2k_to_nbc_mapping.json'
    if len(sys.argv) > 1:
        config_file = sys.argv[1]

    try:
        loader = ConfigLoader(config_file)
        print(f"Successfully loaded configuration: {config_file}")
        print(f"Version: {loader.get_metadata().get('version')}")
        print(f"Field mappings: {len(loader.get_field_mappings())}")
        print(f"Formulas: {len(loader.get_all_formulas())}")
        print(f"Transformations: {len(loader.get_all_transformations())}")
        print(f"Complex mappings: {len(loader.get_all_complex_mappings())}")

        # Validate
        is_valid, errors = loader.validate_config()
        if is_valid:
            print("\n✓ Configuration is valid")
        else:
            print("\n✗ Configuration validation failed:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
