#!/usr/bin/env python3
"""
Main script to process H2K files and generate NBC compliance forms.
Extracts data from reference and proposed H2K files and fills the NBC form template.
"""

import sys
import os
import argparse
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

            # XPath extraction for all matching elements (returns list)
            elif 'xpath_all' in mapping:
                xpath = mapping['xpath_all']
                attr = mapping.get('xpath_attr')
                value = extractor.extract_all_by_xpath(xpath, attr)

            # Multiple XPath extraction (concatenation)
            elif 'xpath_list' in mapping:
                xpath_list = mapping['xpath_list']
                separator = mapping.get('separator', ', ')
                value = extractor.extract_multiple(xpath_list, separator)

            else:
                # No extraction method specified, use default
                value = mapping.get('default', '')

            # Apply transformation if specified (but skip for "N/A" values)
            if value and 'transform' in mapping and value != "N/A":
                transformer = ValueTransformer(self.config)
                value = transformer.apply_transformation(value, mapping['transform'])

            # Apply format if specified (but skip for "N/A" values)
            if value and 'format' in mapping and value != "N/A":
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


def find_matching_pairs(reference_dir, proposed_dir):
    """
    Find matching .h2k file pairs in reference and proposed directories.

    Args:
        reference_dir: Path to directory containing reference .h2k files
        proposed_dir: Path to directory containing proposed .h2k files

    Returns:
        List of tuples: (reference_path, proposed_path, building_id)
    """
    ref_dir = Path(reference_dir)
    prop_dir = Path(proposed_dir)

    # Find all .h2k files in each directory
    ref_files = {f.stem: f for f in ref_dir.glob('*.h2k')}
    prop_files = {f.stem: f for f in prop_dir.glob('*.h2k')}

    # Find matching pairs
    matched_pairs = []
    unmatched_ref = []
    unmatched_prop = []

    for building_id in sorted(ref_files.keys()):
        if building_id in prop_files:
            matched_pairs.append((
                str(ref_files[building_id]),
                str(prop_files[building_id]),
                building_id
            ))
        else:
            unmatched_ref.append(building_id)

    # Check for proposed files without matching reference
    for building_id in prop_files.keys():
        if building_id not in ref_files:
            unmatched_prop.append(building_id)

    # Print summary
    print(f"\nFound {len(matched_pairs)} matching file pairs")

    if unmatched_ref:
        print(f"\nWarning: {len(unmatched_ref)} reference files without matching proposed:")
        for building_id in unmatched_ref:
            print(f"  - {building_id}")

    if unmatched_prop:
        print(f"\nWarning: {len(unmatched_prop)} proposed files without matching reference:")
        for building_id in unmatched_prop:
            print(f"  - {building_id}")

    return matched_pairs


def process_batch(reference_dir, proposed_dir, output_dir):
    """
    Process multiple H2K file pairs in batch mode.

    Args:
        reference_dir: Directory containing reference .h2k files
        proposed_dir: Directory containing proposed .h2k files
        output_dir: Directory for output .docx files
    """
    print("="*70)
    print("BATCH MODE: H2K to NBC Compliance Form Generator")
    print("="*70)
    print(f"Reference directory: {reference_dir}")
    print(f"Proposed directory: {proposed_dir}")
    print(f"Output directory: {output_dir}")

    # Find matching pairs
    pairs = find_matching_pairs(reference_dir, proposed_dir)

    if not pairs:
        print("\nError: No matching file pairs found!")
        sys.exit(1)

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Initialize processor once
    config_path = Path(__file__).parent / 'h2k_to_nbc_mapping.json'

    # Process each pair
    success_count = 0
    failure_count = 0
    failures = []

    print("\n" + "="*70)
    print(f"Processing {len(pairs)} building(s)...")
    print("="*70)

    for i, (ref_file, prop_file, building_id) in enumerate(pairs, 1):
        print(f"\n[{i}/{len(pairs)}] Processing: {building_id}")
        print("-" * 70)

        output_file = output_path / f"{building_id}_NBC_compliance.docx"

        try:
            # Create new processor for each building
            processor = H2KToNBCProcessor(config_path)

            # Validate configuration (only once, on first iteration)
            if i == 1:
                is_valid, errors = processor.config.validate_config()
                if not is_valid:
                    print("\nConfiguration validation failed:")
                    for error in errors:
                        print(f"  - {error}")
                    sys.exit(1)

            # Load H2K files
            processor.load_h2k_files(ref_file, prop_file)

            # Process all mappings
            form_values = processor.process_all_mappings()

            # Fill form template
            processor.fill_form_template(form_values, str(output_file))

            print(f"[OK] Success: Generated {output_file.name}")
            success_count += 1

        except Exception as e:
            print(f"[FAIL] ERROR: {e}")
            failure_count += 1
            failures.append((building_id, str(e)))

    # Print summary
    print("\n" + "="*70)
    print("BATCH PROCESSING COMPLETE")
    print("="*70)
    print(f"Successfully processed: {success_count}/{len(pairs)}")
    print(f"Failed: {failure_count}/{len(pairs)}")

    if failures:
        print("\nFailures:")
        for building_id, error in failures:
            print(f"  - {building_id}: {error}")

    print(f"\nOutput files saved to: {output_dir}/")


def main():
    """Main entry point."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Generate NBC compliance forms from H2K files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Single file mode:
    python process_h2k_to_nbc.py reference.h2k proposed.h2k output.docx

  Batch mode (uses default directories):
    python process_h2k_to_nbc.py --batch

  Batch mode (custom directories):
    python process_h2k_to_nbc.py --batch --ref-dir reference/ --prop-dir proposed/ --output-dir output/
        """
    )

    # Batch mode flag
    parser.add_argument('--batch', action='store_true',
                        help='Enable batch processing mode')

    # Batch mode arguments
    parser.add_argument('--ref-dir', default='reference',
                        help='Reference directory for batch mode (default: reference)')
    parser.add_argument('--prop-dir', default='proposed',
                        help='Proposed directory for batch mode (default: proposed)')
    parser.add_argument('--output-dir', default='output',
                        help='Output directory for batch mode (default: output)')

    # Single file mode arguments (positional)
    parser.add_argument('reference', nargs='?',
                        help='Reference .h2k file (single file mode)')
    parser.add_argument('proposed', nargs='?',
                        help='Proposed .h2k file (single file mode)')
    parser.add_argument('output', nargs='?',
                        help='Output .docx file (single file mode, optional)')

    args = parser.parse_args()

    # Determine mode
    if args.batch:
        # Batch mode
        process_batch(args.ref_dir, args.prop_dir, args.output_dir)

    else:
        # Single file mode
        if not args.reference or not args.proposed:
            parser.print_help()
            print("\nError: Single file mode requires reference and proposed .h2k files")
            sys.exit(1)

        reference_path = args.reference
        proposed_path = args.proposed

        # Generate output filename if not provided
        if args.output:
            output_path = args.output
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
