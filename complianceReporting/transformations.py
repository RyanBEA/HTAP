#!/usr/bin/env python3
"""
Value transformations for H2K to NBC form mapping.
Applies transformations to extracted values based on configuration.
"""


class ValueTransformer:
    """Applies transformations to extracted values."""

    def __init__(self, config_loader):
        """
        Initialize value transformer with configuration.

        Args:
            config_loader: ConfigLoader instance with transformation definitions
        """
        self.config = config_loader

    def apply_transformation(self, value, transform_name, transform_config=None):
        """
        Apply a transformation to a value.

        Args:
            value: Value to transform
            transform_name: Name of the transformation
            transform_config: Optional transformation configuration (from config or mapping)

        Returns:
            Transformed value
        """
        if value is None or value == '':
            return ''

        # Get transformation definition
        if transform_config is None:
            transform_config = self.config.get_transformation(transform_name)

        if not transform_config:
            # Unknown transformation, return value as-is
            return str(value)

        transform_type = transform_config.get('type')

        # Apply transformation based on type
        if transform_type == 'passthrough':
            return self._passthrough(value)
        elif transform_type == 'join':
            return self._join(value, transform_config)
        elif transform_type == 'lookup':
            return self._lookup(value, transform_config)
        elif transform_type == 'map':
            return self._map(value, transform_config)
        elif transform_type == 'calculation':
            return self._calculation(value, transform_config)
        elif transform_type == 'round':
            return self._round(value, transform_config)
        elif transform_type == 'average':
            return self._average(value, transform_config)
        else:
            # Unknown type, return value as-is
            return str(value)

    def _passthrough(self, value):
        """Return value as-is."""
        return str(value).strip() if value else ''

    def _join(self, values, config):
        """Join multiple values with separator."""
        if not isinstance(values, list):
            values = [values]

        separator = config.get('separator', ', ')
        clean_values = [str(v).strip() for v in values if v]
        return separator.join(clean_values)

    def _lookup(self, value, config):
        """Lookup value in ranges or exact matches."""
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            return str(value)

        # Check if we have ranges
        ranges = config.get('ranges', [])
        for range_def in ranges:
            min_val = range_def.get('min', float('-inf'))
            max_val = range_def.get('max', float('inf'))
            if min_val <= numeric_value <= max_val:
                return range_def.get('value', str(value))

        return str(value)

    def _map(self, value, config):
        """Map value using lookup table."""
        mapping = config.get('mapping', {})
        value_str = str(value).strip()
        return mapping.get(value_str, value_str)

    def _calculation(self, value, config):
        """Apply a calculation formula to value."""
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            return ''

        formula = config.get('formula', 'value')

        # Safe evaluation with only the value available
        try:
            result = eval(formula, {"__builtins__": {}}, {'value': numeric_value})
            return str(result)
        except Exception:
            return str(value)

    def _round(self, value, config):
        """Round numeric value to specified decimals."""
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            return str(value)

        decimals = config.get('decimals', 0)
        return f"{numeric_value:.{decimals}f}"

    def _average(self, values, config):
        """Calculate average of numeric values."""
        # Handle single value
        if not isinstance(values, list):
            values = [values]

        # Filter out empty values and convert to floats
        numeric_values = []
        for v in values:
            try:
                if v is not None and v != '':
                    numeric_values.append(float(v))
            except (ValueError, TypeError):
                continue

        # Calculate average
        if not numeric_values:
            return ''

        avg = sum(numeric_values) / len(numeric_values)

        # Apply optional rounding
        decimals = config.get('decimals', 2)
        return f"{avg:.{decimals}f}"

    def apply_format(self, value, format_string):
        """
        Apply a format string to a value.

        Args:
            value: Value to format
            format_string: Format string (e.g., '%.2f')

        Returns:
            Formatted value
        """
        if not format_string or value == '':
            return str(value)

        try:
            # Try to convert to float for numeric formats
            if '%' in format_string:
                numeric_value = float(value)
                return format_string % numeric_value
            else:
                return format_string.format(value)
        except (ValueError, TypeError):
            return str(value)


def transform_climate_zone(hdd_value):
    """
    Convert heating degree days to climate zone string.

    Args:
        hdd_value: Heating degree days (numeric)

    Returns:
        Climate zone string
    """
    try:
        hdd = float(hdd_value)
    except (ValueError, TypeError):
        return "Unknown"

    if hdd < 3000:
        return "Zone 4 (<3000 HDD)"
    elif hdd < 4000:
        return "Zone 5 (3000-3999 HDD)"
    elif hdd < 5000:
        return "Zone 6 (4000-4999 HDD)"
    elif hdd < 6000:
        return "Zone 7A (5000-5999 HDD)"
    else:
        return "Zone 7B/8 (≥6000 HDD)"


def transform_orientation_abbr(orientation):
    """
    Convert full orientation name to abbreviation.

    Args:
        orientation: Full orientation name (e.g., 'Southwest')

    Returns:
        Abbreviated orientation (e.g., 'SW')
    """
    mapping = {
        'North': 'N',
        'Northeast': 'NE',
        'East': 'E',
        'Southeast': 'SE',
        'South': 'S',
        'Southwest': 'SW',
        'West': 'W',
        'Northwest': 'NW'
    }
    return mapping.get(str(orientation).strip(), orientation)


def transform_r_to_u(r_value):
    """
    Convert R-value to U-value (U = 1/R).

    Args:
        r_value: R-value (numeric)

    Returns:
        U-value as formatted string
    """
    try:
        r = float(r_value)
        if r > 0:
            u = 1.0 / r
            return f"{u:.2f}"
        else:
            return "0.00"
    except (ValueError, TypeError):
        return ""


if __name__ == '__main__':
    # Test transformations
    print("Testing transformations:")
    print(f"Climate zone (4111 HDD): {transform_climate_zone(4111)}")
    print(f"Orientation (Southwest): {transform_orientation_abbr('Southwest')}")
    print(f"R to U (0.6551): {transform_r_to_u(0.6551)}")
    print(f"R to U (2.97): {transform_r_to_u(2.97)}")
