#!/usr/bin/env python3
"""
H2K file data extractor.
Extracts data from HOT2000 .h2k XML files using XPath queries.
"""

import xml.etree.ElementTree as ET
from pathlib import Path


class H2KExtractor:
    """Extracts data from HOT2000 .h2k XML files."""

    def __init__(self, h2k_path):
        """
        Initialize H2K extractor with a .h2k file.

        Args:
            h2k_path: Path to the .h2k file
        """
        self.h2k_path = Path(h2k_path)
        if not self.h2k_path.exists():
            raise FileNotFoundError(f"H2K file not found: {h2k_path}")

        # Parse the XML file
        self.tree = ET.parse(self.h2k_path)
        self.root = self.tree.getroot()

        # H2K files typically don't use XML namespaces
        self.namespaces = {}

    def extract_by_xpath(self, xpath, attribute=None):
        """
        Extract a single value using XPath expression.

        Args:
            xpath: XPath expression to locate the element
            attribute: Optional attribute name to extract (if None, extracts text content)

        Returns:
            Extracted value as string, or None if not found
        """
        # Use find to get the first matching element
        element = self.root.find(xpath)

        if element is None:
            return None

        # Extract attribute or text content
        if attribute:
            return element.get(attribute)
        else:
            # Return text content if available
            return element.text if element.text else None

    def extract_multiple(self, xpath_list, separator=', '):
        """
        Extract multiple values and concatenate them.

        Args:
            xpath_list: List of XPath expressions
            separator: String to join values with

        Returns:
            Concatenated string of values, or empty string if none found
        """
        values = []
        for xpath in xpath_list:
            value = self.extract_by_xpath(xpath)
            if value:
                values.append(value.strip())

        return separator.join(values) if values else ''

    def extract_all_by_xpath(self, xpath, attribute=None):
        """
        Extract all values matching an XPath expression.

        Args:
            xpath: XPath expression to locate elements
            attribute: Optional attribute name to extract

        Returns:
            List of extracted values
        """
        elements = self.root.findall(xpath)
        values = []

        for element in elements:
            if attribute:
                value = element.get(attribute)
            else:
                value = element.text

            if value:
                values.append(value)

        return values

    def extract_float(self, xpath, attribute=None, default=0.0):
        """
        Extract a numeric value and convert to float.

        Args:
            xpath: XPath expression to locate the element
            attribute: Optional attribute name to extract
            default: Default value if extraction fails

        Returns:
            Float value or default
        """
        value = self.extract_by_xpath(xpath, attribute)
        if value is None:
            return default

        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def extract_int(self, xpath, attribute=None, default=0):
        """
        Extract a numeric value and convert to integer.

        Args:
            xpath: XPath expression to locate the element
            attribute: Optional attribute name to extract
            default: Default value if extraction fails

        Returns:
            Integer value or default
        """
        value = self.extract_by_xpath(xpath, attribute)
        if value is None:
            return default

        try:
            return int(float(value))
        except (ValueError, TypeError):
            return default

    def extract_for_complex_mapping(self, component_spec):
        """
        Extract value for a complex mapping component.

        Args:
            component_spec: Dictionary specifying xpath, optional attr, and default

        Returns:
            Extracted value or default
        """
        xpath = component_spec.get('xpath')
        attr = component_spec.get('attr')
        default = component_spec.get('default', '')

        if not xpath:
            return default

        value = self.extract_by_xpath(xpath, attr)
        return value if value is not None else default

    def element_exists(self, xpath):
        """
        Check if an element exists at the given XPath.

        Args:
            xpath: XPath expression to check

        Returns:
            True if element exists, False otherwise
        """
        return self.root.find(xpath) is not None

    def get_file_info(self):
        """
        Get basic file information.

        Returns:
            Dictionary with file metadata
        """
        return {
            'path': str(self.h2k_path),
            'identification': self.extract_by_xpath('.//ProgramInformation/File/Identification'),
            'evaluation_date': self.extract_by_xpath('.//ProgramInformation/File', 'evaluationDate'),
            'location': self.extract_by_xpath('.//ProgramInformation/Weather/Location/English'),
            'builder': self.extract_by_xpath('.//ProgramInformation/File/BuilderName'),
            'entered_by': self.extract_by_xpath('.//ProgramInformation/File/EnteredBy')
        }


if __name__ == '__main__':
    # Test H2K extraction
    import sys

    if len(sys.argv) < 2:
        print("Usage: python h2k_extractor.py <h2k_file>")
        sys.exit(1)

    h2k_file = sys.argv[1]

    try:
        extractor = H2KExtractor(h2k_file)
        print(f"Successfully loaded H2K file: {h2k_file}")
        print("\nFile Information:")
        info = extractor.get_file_info()
        for key, value in info.items():
            print(f"  {key}: {value}")

        # Test some extractions
        print("\nSample Extractions:")
        print(f"  Heating Degree Days: {extractor.extract_by_xpath('.//ProgramInformation/Weather', 'heatingDegreeDay')}")
        print(f"  Orientation: {extractor.extract_by_xpath('.//House/Specifications/FacingDirection/English')}")
        print(f"  Annual Energy: {extractor.extract_by_xpath('.//AllResults/Results/Annual/Consumption', 'total')} GJ")
        print(f"  Blower Door ACH: {extractor.extract_by_xpath('.//House/NaturalAirInfiltration/Specifications/BlowerTest', 'airChangeRate')}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
