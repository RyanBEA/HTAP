#!/usr/bin/env python3
"""
Main script to process H2K files and generate NBC compliance forms.
Extracts data from reference and proposed H2K files and fills the NBC form template.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'util'))

from config_loader import ConfigLoader
from h2k_extractor import H2KExtractor
from transformations import ValueTransformer
from formula_processor import FormulaProcessor, ComplexMappingProcessor
from fill_form_dummy_data import generate_document


class H2KToNBCProcessor:
    """Main processor for converting H2K files to NBC compliance forms."""

    def __init__(self, config_path='h2k_to_nbc_mapping.json'):
        """
        Initialize processor with configuration.

        Args:
            config_path: Path to configuration file
        """
        self.config = ConfigLoader(config_path)
        self.reference_extractor = None
        self.proposed_extractor = None
        self.extractors = {}

    def load_h2k_files(self, reference_path, proposed_path):
        """
        Load reference and proposed H2K files.

        Args:
            reference_path: Path to reference.h2k file
            proposed_path: Path to proposed.h2k file
        """
        print(f"Loading reference H2K file: {reference_path}")
        self.reference_extractor = H2KExtractor(reference_path)
        self.extractors['reference'] = self.reference_extractor

        print(f"Loading proposed H2K file: {proposed_path}")
        self.proposed_extractor = H2KExtractor(proposed_path)
        self.extractors['proposed'] = self.proposed_extractor

    def process_field_mapping(self, mapping):
        """
        Process a single field mapping.

        Args:
            mapping: Field mapping definition from configuration

        Returns:
            Tuple of (field_id, value)
        """
        field_id = mapping['nbc_field']
        source = mapping.get('source', 'proposed')

        # Get appropriate extractor
        extractor = self.extractors.get(source)
        if not extractor:
            print(f"Warning: Unknown data source '{source}' for field {field_id}")
            return (field_id, mapping.get('default', ''))

        try:
            # Check if this is a static value (hard-coded)
            if 'static_value' in mapping:
                value = mapping['static_value']

            # Check if this is a formula-based field
            elif 'formula' in mapping:
                formula_processor = FormulaProcessor(self.config, extractor)
                value = formula_processor.calculate(mapping['formula'])

            # Check if this is a complex mapping
            elif 'complex_mapping' in mapping:
                complex_processor = ComplexMappingProcessor(self.config, extractor)
                value = complex_processor.process(mapping['complex_mapping'])

            # Standard XPath extraction
            elif 'xpath' in mapping:
                xpath = mapping['xpath']
                attr = mapping.get('xpath_attr')
                value = extractor.extract_by_xpath(xpath, attr)

            # Multiple XPath extraction (concatenation)
            elif 'xpath_list' in mapping:
                xpath_list = mapping['xpath_list']
                separator = mapping.get('separator', ', ')
                value = extractor.extract_multiple(xpath_list, separator)

            else:
                # No extraction method specified, use default
                value = mapping.get('default', '')

            # Apply transformation if specified
            if value and 'transform' in mapping:
                transformer = ValueTransformer(self.config)
                value = transformer.apply_transformation(value, mapping['transform'])

            # Apply format if specified
            if value and 'format' in mapping:
                transformer = ValueTransformer(self.config)
                value = transformer.apply_format(value, mapping['format'])

            # Use default if value is empty
            if not value:
                value = mapping.get('default', '')

            return (field_id, str(value))

        except Exception as e:
            print(f"Error processing field {field_id}: {e}")
            import traceback
            traceback.print_exc()
            return (field_id, mapping.get('default', ''))

    def process_all_mappings(self):
        """
        Process all field mappings and return a dictionary of field values.

        Returns:
            Dictionary of NBC field ID -> value
        """
        print("\nProcessing field mappings...")
        form_values = {}

        mappings = self.config.get_field_mappings()
        total_fields = len(mappings)

        for i, mapping in enumerate(mappings, 1):
            field_id, value = self.process_field_mapping(mapping)
            form_values[field_id] = value

            if (i % 5 == 0) or (i == total_fields):
                print(f"  Processed {i}/{total_fields} fields")

        return form_values

    def fill_form_template(self, form_values, output_path):
        """
        Fill the NBC form template with extracted values.

        Args:
            form_values: Dictionary of field ID -> value
            output_path: Path to output .docx file
        """
        # Get template path from configuration or use default
        template_path = Path(__file__).parent / 'form_template.docx'

        if not template_path.exists():
            raise FileNotFoundError(f"Form template not found: {template_path}")

        print(f"\nGenerating NBC compliance form...")
        print(f"  Template: {template_path}")
        print(f"  Output: {output_path}")

        generate_document(template_path, Path(output_path), form_values)
        print(f"  Successfully generated form!")

    def generate_report(self, form_values):
        """
        Generate a summary report of extracted data.

        Args:
            form_values: Dictionary of field ID -> value
        """
        print("\n" + "="*70)
        print("DATA EXTRACTION SUMMARY")
        print("="*70)

        # Group by table
        tables = {}
        for field_id, value in sorted(form_values.items()):
            table_num = field_id.split('_')[0][1:]  # Extract table number from T#_R#_C#
            if table_num not in tables:
                tables[table_num] = []
            tables[table_num].append((field_id, value))

        # Print by table
        for table_num in sorted(tables.keys(), key=int):
            print(f"\nTable {table_num}:")
            for field_id, value in tables[table_num]:
                display_value = value if len(value) < 60 else value[:57] + '...'
                print(f"  {field_id}: {display_value}")


def main():
    """Main entry point."""
    # Parse command line arguments
    if len(sys.argv) < 3:
        print("Usage: python process_h2k_to_nbc.py <reference.h2k> <proposed.h2k> [output.docx]")
        print("\nExample:")
        print("  python process_h2k_to_nbc.py reference.h2k proposed.h2k NBC_compliance.docx")
        sys.exit(1)

    reference_path = sys.argv[1]
    proposed_path = sys.argv[2]

    # Generate output filename if not provided
    if len(sys.argv) > 3:
        output_path = sys.argv[3]
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'NBC_compliance_{timestamp}.docx'

    # Create output directory if it doesn't exist
    output_dir = Path(output_path).parent
    if output_dir and not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    print("="*70)
    print("H2K to NBC Compliance Form Generator")
    print("="*70)

    try:
        # Initialize processor
        config_path = Path(__file__).parent / 'h2k_to_nbc_mapping.json'
        processor = H2KToNBCProcessor(config_path)

        # Validate configuration
        is_valid, errors = processor.config.validate_config()
        if not is_valid:
            print("\nConfiguration validation failed:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)

        # Load H2K files
        processor.load_h2k_files(reference_path, proposed_path)

        # Process all mappings
        form_values = processor.process_all_mappings()

        # Generate report
        processor.generate_report(form_values)

        # Fill form template
        processor.fill_form_template(form_values, output_path)

        print("\n" + "="*70)
        print("COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"\nGenerated NBC compliance form: {output_path}")
        print(f"Total fields populated: {len(form_values)}")

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
