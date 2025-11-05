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
            # Check if this is a parallel path RSI calculation
            if formula.get('type') == 'parallel_path_rsi':
                result = self._calculate_parallel_path_rsi(formula)
                # If result is "N/A" string, return it directly without formatting
                if isinstance(result, str) and result == "N/A":
                    return result
                format_str = formula.get('format', '%.2f')
                return self._format_result(result, format_str)

            # Check if this is a weighted average calculation
            if formula.get('type') == 'weighted_average':
                result = self._calculate_weighted_average(formula)
                format_str = formula.get('format', '%.3f')
                return self._format_result(result, format_str)

            # Standard formula calculation
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
            result: Numeric result or "N/A" string
            format_str: Format string (e.g., '%.1f')

        Returns:
            Formatted string
        """
        # Pass through "N/A" without formatting
        if result == "N/A":
            return "N/A"

        try:
            if '%' in format_str:
                return format_str % result
            else:
                return str(result)
        except Exception as e:
            print(f"Error formatting result {result} with format '{format_str}': {e}")
            return str(result)

    def _calculate_parallel_path_rsi(self, formula):
        """
        Calculate area-weighted average RSI using parallel path method.
        Formula: Average RSI = (Total Area) / Σ(Area_i / RSI_i)

        Args:
            formula: Formula definition with parallel path RSI parameters

        Returns:
            Calculated average RSI value, or "N/A" string if component doesn't exist
        """
        # Check if we should return "N/A" for missing components
        return_na_if_no_elements = formula.get('return_na_if_no_elements', False)

        # Build parent map for the entire tree to support parent navigation
        parent_map = {c: p for p in self.extractor.root.iter() for c in p}

        # Extract all elements (e.g., Wall components)
        # ElementTree doesn't support pipe operator in XPath, so split and combine
        elements_xpath = formula.get('elements_xpath')

        # Split on pipe and strip whitespace
        xpath_list = [x.strip() for x in elements_xpath.split('|')]

        # Find elements using each XPath and combine results
        elements = []
        for xpath in xpath_list:
            found = self.extractor.root.findall(xpath, self.extractor.namespaces)
            elements.extend(found)

        if not elements:
            print(f"Warning: No elements found for xpath '{elements_xpath}'")
            if return_na_if_no_elements:
                return "N/A"
            return 0.0

        # Get type filter if specified
        type_filter = formula.get('type_filter', None)
        type_xpath = formula.get('type_xpath', './Construction/Type/English')

        # Normalize type_filter to list
        if type_filter and not isinstance(type_filter, list):
            type_filter = [type_filter]

        # Get attribute filter if specified
        attribute_filter = formula.get('attribute_filter', None)
        attribute_filter_xpath = formula.get('attribute_filter_xpath', None)

        # Extract RSI and area for each element
        total_area = 0.0
        sum_area_over_rsi = 0.0

        for element in elements:
            # Apply type filter if specified
            if type_filter:
                type_elem = element.find(type_xpath, self.extractor.namespaces)
                if type_elem is None or type_elem.text not in type_filter:
                    continue

            # Apply attribute filter if specified
            if attribute_filter and attribute_filter_xpath:
                filter_elem = element.find(attribute_filter_xpath, self.extractor.namespaces) if attribute_filter_xpath != '.' else element
                if filter_elem is None:
                    continue

                # Check all attribute conditions
                match = True
                for attr_name, attr_value in attribute_filter.items():
                    elem_attr_value = filter_elem.get(attr_name)
                    if elem_attr_value != attr_value:
                        match = False
                        break

                if not match:
                    continue
            # Extract R-value
            rvalue_xpath = formula.get('rvalue_xpath', './Construction/Type')
            rvalue_attr = formula.get('rvalue_attr', 'rValue')
            allow_missing_rvalue = formula.get('allow_missing_rvalue', False)
            rvalue_elem = element.find(rvalue_xpath, self.extractor.namespaces)

            # Handle missing rValue element
            if rvalue_elem is None:
                if allow_missing_rvalue:
                    # Treat missing element as rValue=0 (no insulation)
                    # Return 0 immediately since any uninsulated floor makes overall RSI = 0
                    return 0.0
                else:
                    continue

            try:
                rvalue = float(rvalue_elem.get(rvalue_attr, 0))
            except (ValueError, TypeError):
                if allow_missing_rvalue:
                    return 0.0
                continue

            # If rValue is 0, the floor is uninsulated
            if rvalue <= 0:
                if allow_missing_rvalue:
                    # Any uninsulated floor makes overall RSI = 0
                    return 0.0
                else:
                    continue

            # Extract area
            # Check if we have direct area or need to calculate from height * perimeter
            if 'area_xpath' in formula:
                # Direct area (for ceilings, floors)
                area_xpath = formula.get('area_xpath', './Measurements')
                area_attr = formula.get('area_attr', 'area')

                area_elem = element.find(area_xpath, self.extractor.namespaces)
                if area_elem is None:
                    continue

                try:
                    area = float(area_elem.get(area_attr, 0))
                except (ValueError, TypeError):
                    continue
            else:
                # Calculate area from height * perimeter (for walls) or height * width (for windows)
                area_height_xpath = formula.get('area_height_xpath', './Measurements')
                area_height_attr = formula.get('area_height_attr', 'height')

                # Check if width-based calculation (for windows)
                area_width_xpath = formula.get('area_width_xpath', None)
                area_width_attr = formula.get('area_width_attr', None)

                # Get height from height element
                height_elem = element.find(area_height_xpath, self.extractor.namespaces)
                if height_elem is None:
                    continue

                # Determine if using width or perimeter
                if area_width_xpath and area_width_attr:
                    # Width-based calculation (for windows: height × width)
                    width_elem = element.find(area_width_xpath, self.extractor.namespaces)
                    if width_elem is None:
                        continue

                    try:
                        height = float(height_elem.get(area_height_attr, 0))
                        width = float(width_elem.get(area_width_attr, 0))
                        # Windows measurements are in mm, convert to m²
                        area = (height * width) / 1_000_000
                    except (ValueError, TypeError):
                        continue
                else:
                    # Perimeter-based calculation (for walls: height × perimeter)
                    area_perimeter_xpath = formula.get('area_perimeter_xpath', './Measurements')
                    area_perimeter_attr = formula.get('area_perimeter_attr', 'perimeter')

                    # Get perimeter from perimeter element (may be same or different from height element)
                    # Handle parent-relative XPaths (starting with ../)
                    if area_perimeter_xpath.startswith('../'):
                        parent = parent_map.get(element)
                        if parent is not None:
                            # Remove ../ prefix and search from parent
                            relative_path = area_perimeter_xpath[3:]  # Remove "../"
                            perimeter_elem = parent.find(relative_path, self.extractor.namespaces)
                        else:
                            perimeter_elem = None
                    else:
                        perimeter_elem = element.find(area_perimeter_xpath, self.extractor.namespaces)

                    if perimeter_elem is None:
                        continue

                    try:
                        height = float(height_elem.get(area_height_attr, 0))
                        perimeter = float(perimeter_elem.get(area_perimeter_attr, 0))
                        area = height * perimeter
                    except (ValueError, TypeError):
                        continue

            if area <= 0:
                continue

            # Accumulate for parallel path calculation
            total_area += area
            sum_area_over_rsi += (area / rvalue)

        # Calculate parallel path average
        if sum_area_over_rsi > 0:
            average_rsi = total_area / sum_area_over_rsi
            return average_rsi
        else:
            # No valid elements found after filtering
            if return_na_if_no_elements:
                return "N/A"
            return 0.0

    def _calculate_weighted_average(self, formula):
        """
        Calculate area-weighted average of an attribute (e.g., SHGC).
        Formula: Weighted Avg = Σ(attribute_i × Area_i) / Σ(Area_i)

        Args:
            formula: Formula definition with weighted average parameters

        Returns:
            Calculated weighted average value, or "N/A" string if component doesn't exist
        """
        # Check if we should return "N/A" for missing components
        return_na_if_no_elements = formula.get('return_na_if_no_elements', False)

        # Extract all elements (e.g., Window components)
        elements_xpath = formula.get('elements_xpath')

        # Split on pipe and strip whitespace (support multiple XPaths)
        xpath_list = [x.strip() for x in elements_xpath.split('|')]

        # Find elements using each XPath and combine results
        elements = []
        for xpath in xpath_list:
            found = self.extractor.root.findall(xpath, self.extractor.namespaces)
            elements.extend(found)

        if not elements:
            print(f"Warning: No elements found for xpath '{elements_xpath}'")
            if return_na_if_no_elements:
                return "N/A"
            return 0.0

        # Extract attribute and area for each element
        total_area = 0.0
        weighted_sum = 0.0

        # Get attribute configuration
        attribute_name = formula.get('attribute_name')
        attribute_xpath = formula.get('attribute_xpath', '.')  # Default to element itself

        for element in elements:
            # Extract attribute value
            if attribute_xpath == '.':
                # Attribute is on the element itself
                attr_elem = element
            else:
                # Navigate to sub-element
                attr_elem = element.find(attribute_xpath, self.extractor.namespaces)
                if attr_elem is None:
                    continue

            try:
                attribute_value = float(attr_elem.get(attribute_name, 0))
            except (ValueError, TypeError):
                continue

            # Extract area (using same logic as parallel path RSI)
            if 'area_xpath' in formula:
                # Direct area
                area_xpath = formula.get('area_xpath', './Measurements')
                area_attr = formula.get('area_attr', 'area')

                area_elem = element.find(area_xpath, self.extractor.namespaces)
                if area_elem is None:
                    continue

                try:
                    area = float(area_elem.get(area_attr, 0))
                except (ValueError, TypeError):
                    continue
            else:
                # Calculate area from height * width (for windows)
                area_height_xpath = formula.get('area_height_xpath', './Measurements')
                area_height_attr = formula.get('area_height_attr', 'height')
                area_width_xpath = formula.get('area_width_xpath', './Measurements')
                area_width_attr = formula.get('area_width_attr', 'width')

                height_elem = element.find(area_height_xpath, self.extractor.namespaces)
                width_elem = element.find(area_width_xpath, self.extractor.namespaces)

                if height_elem is None or width_elem is None:
                    continue

                try:
                    height = float(height_elem.get(area_height_attr, 0))
                    width = float(width_elem.get(area_width_attr, 0))
                    # Windows measurements are in mm, convert to m²
                    area = (height * width) / 1_000_000
                except (ValueError, TypeError):
                    continue

            if area <= 0:
                continue

            # Accumulate weighted sum
            total_area += area
            weighted_sum += (attribute_value * area)

        # Calculate weighted average
        if total_area > 0:
            weighted_avg = weighted_sum / total_area
            return weighted_avg
        else:
            # No valid elements found after processing
            if return_na_if_no_elements:
                return "N/A"
            return 0.0

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

            for i, component in enumerate(components):
                result = self.extractor.extract_for_complex_mapping(component)

                # Check if result is a tuple (value, check_attr_value)
                if isinstance(result, tuple):
                    value, check_attr_value = result

                    # Apply conversion if specified
                    conversion = component.get('conversion')
                    if conversion and value:
                        # Apply COP to HSPF conversion based on isCop attribute
                        if conversion == 'cop_to_hspf_conditional':
                            # If isCop is "true", convert COP to HSPF
                            # If isCop is not "true", value is already HSPF, use as-is
                            if check_attr_value == "true":
                                # Value is COP, convert to HSPF: HSPF = (COP - 0.78) / 0.376
                                try:
                                    cop_value = float(value)
                                    hspf_value = (cop_value - 0.78) / 0.376
                                    value = f"{hspf_value:.2f}"
                                except (ValueError, TypeError):
                                    pass  # Keep original value if conversion fails
                            # else: value is already HSPF, use as-is

                    values.append(value)
                else:
                    values.append(result)

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
