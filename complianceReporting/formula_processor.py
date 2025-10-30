#!/usr/bin/env python3
"""
Formula processor for H2K to NBC form mapping.
Evaluates formulas defined in configuration using extracted H2K data.
"""


class FormulaProcessor:
    """Processes formulas defined in configuration."""

    def __init__(self, config_loader, h2k_extractor):
        """
        Initialize formula processor.

        Args:
            config_loader: ConfigLoader instance with formula definitions
            h2k_extractor: H2KExtractor instance for data extraction
        """
        self.config = config_loader
        self.extractor = h2k_extractor

    def calculate(self, formula_name):
        """
        Execute a formula from the configuration.

        Args:
            formula_name: Name of the formula to execute

        Returns:
            Calculated result as formatted string, or empty string on error
        """
        formula = self.config.get_formula(formula_name)
        if not formula:
            print(f"Warning: Formula '{formula_name}' not found in configuration")
            return ''

        try:
            # Extract input values
            inputs = self._extract_formula_inputs(formula)

            # Evaluate calculation
            result = self._evaluate_calculation(formula['calculation'], inputs)

            # Format result
            format_str = formula.get('format', '%s')
            return self._format_result(result, format_str)

        except Exception as e:
            print(f"Error calculating formula '{formula_name}': {e}")
            return ''

    def _extract_formula_inputs(self, formula):
        """
        Extract all input values for a formula.

        Args:
            formula: Formula definition dict

        Returns:
            Dictionary of input name -> numeric value
        """
        inputs = {}
        input_xpaths = formula.get('inputs', {})
        input_attrs = formula.get('input_attrs', {})

        for input_name, xpath in input_xpaths.items():
            # Get attribute name if specified
            attr = input_attrs.get(input_name)

            # Extract value
            value = self.extractor.extract_float(xpath, attr, default=0.0)
            inputs[input_name] = value

        return inputs

    def _evaluate_calculation(self, calculation_expr, inputs):
        """
        Safely evaluate a calculation expression.

        Args:
            calculation_expr: Python expression string
            inputs: Dictionary of variable name -> value

        Returns:
            Calculation result
        """
        # Create a safe environment for evaluation
        # Only allow basic math operations and the input variables
        safe_builtins = {
            'abs': abs,
            'max': max,
            'min': min,
            'round': round,
            'sum': sum
        }

        try:
            result = eval(calculation_expr, {"__builtins__": safe_builtins}, inputs)
            return result
        except Exception as e:
            print(f"Error evaluating calculation '{calculation_expr}': {e}")
            print(f"  Inputs: {inputs}")
            raise

    def _format_result(self, result, format_str):
        """
        Format a calculation result.

        Args:
            result: Numeric result
            format_str: Format string (e.g., '%.1f')

        Returns:
            Formatted string
        """
        try:
            if '%' in format_str:
                return format_str % result
            else:
                return str(result)
        except Exception as e:
            print(f"Error formatting result {result} with format '{format_str}': {e}")
            return str(result)

    def calculate_fdwr(self):
        """
        Calculate FDWR (Fenestration and Door to Wall Ratio) percentage.
        This is a convenience method for the most commonly used calculation.

        Returns:
            FDWR as formatted percentage string
        """
        return self.calculate('fdwr_calculation')


class ComplexMappingProcessor:
    """Processes complex mappings that combine multiple H2K values."""

    def __init__(self, config_loader, h2k_extractor):
        """
        Initialize complex mapping processor.

        Args:
            config_loader: ConfigLoader instance
            h2k_extractor: H2KExtractor instance
        """
        self.config = config_loader
        self.extractor = h2k_extractor

    def process(self, mapping_name):
        """
        Process a complex mapping.

        Args:
            mapping_name: Name of the complex mapping to process

        Returns:
            Formatted string combining multiple H2K values
        """
        mapping = self.config.get_complex_mapping(mapping_name)
        if not mapping:
            print(f"Warning: Complex mapping '{mapping_name}' not found")
            return ''

        try:
            # Extract component values
            components = mapping.get('components', [])
            values = []

            for component in components:
                value = self.extractor.extract_for_complex_mapping(component)
                values.append(value)

            # Check if we have optional components with no values
            # If the last components are optional and empty, use simple format
            has_optional = any(c.get('optional', False) for c in components)
            if has_optional:
                # Check if optional components have values
                optional_indices = [i for i, c in enumerate(components) if c.get('optional', False)]
                has_optional_values = any(values[i] for i in optional_indices)

                if not has_optional_values:
                    # Use simple format if available
                    format_str = mapping.get('format_simple', mapping.get('format'))
                    # Only use non-optional components
                    non_optional_values = [v for i, v in enumerate(values) if i not in optional_indices]
                    return format_str.format(*non_optional_values)

            # Apply format string
            format_str = mapping.get('format', '')
            return format_str.format(*values)

        except Exception as e:
            print(f"Error processing complex mapping '{mapping_name}': {e}")
            return ''


if __name__ == '__main__':
    # Test formula processor
    import sys
    from config_loader import ConfigLoader
    from h2k_extractor import H2KExtractor

    if len(sys.argv) < 3:
        print("Usage: python formula_processor.py <config_file> <h2k_file>")
        sys.exit(1)

    config_file = sys.argv[1]
    h2k_file = sys.argv[2]

    try:
        config = ConfigLoader(config_file)
        extractor = H2KExtractor(h2k_file)
        processor = FormulaProcessor(config, extractor)

        print(f"Loaded configuration: {config_file}")
        print(f"Loaded H2K file: {h2k_file}")
        print("\nTesting formulas:")

        # Test FDWR calculation
        fdwr = processor.calculate_fdwr()
        print(f"  FDWR: {fdwr}%")

        # Test complex mappings
        complex_proc = ComplexMappingProcessor(config, extractor)

        heating = complex_proc.process('heating_system')
        print(f"  Heating System: {heating}")

        dhw = complex_proc.process('dhw_system')
        print(f"  DHW System: {dhw}")

        hrv = complex_proc.process('hrv_system')
        print(f"  HRV System: {hrv}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
