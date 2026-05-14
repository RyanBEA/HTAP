"""
Unit tests for run file parser
"""

import pytest
from pathlib import Path

from src.parsers.run_parser import RunFileParser, parse_run_file
from src.parsers.run_writer import RunFileWriter, write_run_file
from src.parsers.validation import validate_run_configuration
from src.models.run_config import (
    RunConfiguration,
    RunMode,
    RunParameters,
    RunScope,
    OptionUpgrade,
)


@pytest.fixture
def sample_run_content():
    """Sample .run file content"""
    return """! Test run file
! Another comment
RunParameters_START
  run-mode                           = parametric
  archetype-dir                      = C:/HTAP/archetypes
  unit-costs-db                      = C:/HTAP/HTAPUnitCosts.json
  options-file                       = C:/HTAP/HTAP-options.json
RunParameters_END

RunScope_START
  archetypes                        = *.H2K
  locations                         = NA
  rulesets                          = as-found
RunScope_END

Upgrades_START
   Opt-Windows     = NA, DoubleGlazed-LowE
   Opt-ACH         = NA, 1.5
Upgrades_END
"""


@pytest.fixture
def regions_run_path():
    """Path to real regions.run file"""
    return "C:/HTAP/development/htap-config-editor/data/regions.run"


class TestRunFileParser:
    """Test run file parsing"""

    def test_parse_string_basic(self, sample_run_content):
        """Test basic parsing from string"""
        parser = RunFileParser()
        config = parser.parse_string(sample_run_content)

        assert config.parameters.run_mode == RunMode.PARAMETRIC
        assert config.parameters.archetype_dir == "C:/HTAP/archetypes"
        assert config.parameters.unit_costs_db == "C:/HTAP/HTAPUnitCosts.json"
        assert config.parameters.options_file == "C:/HTAP/HTAP-options.json"

    def test_parse_scope(self, sample_run_content):
        """Test parsing RunScope section"""
        parser = RunFileParser()
        config = parser.parse_string(sample_run_content)

        assert config.scope.archetypes == "*.H2K"
        assert config.scope.locations == "NA"
        assert config.scope.rulesets == "as-found"

    def test_parse_upgrades(self, sample_run_content):
        """Test upgrade parsing"""
        parser = RunFileParser()
        config = parser.parse_string(sample_run_content)

        assert len(config.upgrades) == 2

        windows = config.get_upgrade("Opt-Windows")
        assert windows is not None
        assert windows.choices == ["NA", "DoubleGlazed-LowE"]

        ach = config.get_upgrade("Opt-ACH")
        assert ach is not None
        assert ach.choices == ["NA", "1.5"]

    def test_parse_comments(self, sample_run_content):
        """Test comment preservation"""
        parser = RunFileParser()
        config = parser.parse_string(sample_run_content)

        assert len(config.comments) >= 1
        assert config.comments[0] == "! Test run file"

    def test_parse_real_file(self, regions_run_path):
        """Test parsing real regions.run file"""
        if not Path(regions_run_path).exists():
            pytest.skip("regions.run file not found")

        parser = RunFileParser()
        config = parser.parse_file(regions_run_path)

        # Verify structure
        assert config.parameters.run_mode == RunMode.PARAMETRIC
        assert config.scope.archetypes == "*.H2K"
        assert len(config.upgrades) > 0

        # Check specific upgrades
        result_code = config.get_upgrade("Opt-ResultHouseCode")
        assert result_code is not None
        assert result_code.choices == ["General"]

    def test_parse_file_not_found(self):
        """Test parsing non-existent file"""
        parser = RunFileParser()
        with pytest.raises(FileNotFoundError):
            parser.parse_file("nonexistent.run")

    def test_upgrade_operations(self, sample_run_content):
        """Test upgrade add/remove/get operations"""
        parser = RunFileParser()
        config = parser.parse_string(sample_run_content)

        # Add new upgrade
        config.add_upgrade("Opt-Heating-Cooling", ["NA", "ASHP"])
        assert "Opt-Heating-Cooling" in config.upgrades

        # Get upgrade
        heating = config.get_upgrade("Opt-Heating-Cooling")
        assert heating.choices == ["NA", "ASHP"]

        # List upgrades
        upgrade_list = config.list_upgrades()
        assert "Opt-Heating-Cooling" in upgrade_list

        # Remove upgrade
        removed = config.remove_upgrade("Opt-ACH")
        assert removed is True
        assert "Opt-ACH" not in config.upgrades


class TestRunFileWriter:
    """Test run file writing"""

    def test_write_file_basic(self, tmp_path):
        """Test writing configuration to file"""
        config = RunConfiguration(
            parameters=RunParameters(
                run_mode=RunMode.PARAMETRIC,
                archetype_dir="C:/HTAP/archetypes",
                unit_costs_db="C:/HTAP/HTAPUnitCosts.json",
                options_file="C:/HTAP/HTAP-options.json"
            ),
            scope=RunScope(
                archetypes="*.H2K",
                locations="NA",
                rulesets="as-found"
            ),
            upgrades={}
        )

        output_file = tmp_path / "output.run"
        write_run_file(config, str(output_file), include_timestamp=False)

        assert output_file.exists()
        content = output_file.read_text()
        assert "RunParameters_START" in content
        assert "RunScope_START" in content
        assert "Upgrades_START" in content

    def test_write_with_upgrades(self, tmp_path):
        """Test writing configuration with upgrades"""
        config = RunConfiguration(
            parameters=RunParameters(),
            scope=RunScope(),
            upgrades={}
        )

        config.add_upgrade("Opt-Windows", ["NA", "TripleGlazed"])
        config.add_upgrade("Opt-ACH", ["NA", "1.5", "2.5"])

        output_file = tmp_path / "test.run"
        writer = RunFileWriter()
        writer.write_file(config, str(output_file), include_timestamp=False)

        content = output_file.read_text()
        assert "Opt-Windows" in content
        assert "Opt-ACH" in content
        assert "TripleGlazed" in content

    def test_roundtrip(self, sample_run_content, tmp_path):
        """Test parse → write → parse gives same result"""
        parser = RunFileParser()
        writer = RunFileWriter()

        # Parse original
        config1 = parser.parse_string(sample_run_content)

        # Write to file
        output_file = tmp_path / "test.run"
        writer.write_file(config1, str(output_file), include_timestamp=False)

        # Parse written file
        config2 = parser.parse_file(str(output_file))

        # Compare
        assert config1.parameters.run_mode == config2.parameters.run_mode
        assert config1.parameters.archetype_dir == config2.parameters.archetype_dir
        assert config1.scope.archetypes == config2.scope.archetypes
        assert config1.scope.locations == config2.scope.locations
        assert len(config1.upgrades) == len(config2.upgrades)

        # Compare specific upgrades
        for key in config1.upgrades:
            assert key in config2.upgrades
            assert config1.upgrades[key].choices == config2.upgrades[key].choices

    def test_roundtrip_real_file(self, regions_run_path, tmp_path):
        """Test roundtrip with real regions.run file"""
        if not Path(regions_run_path).exists():
            pytest.skip("regions.run file not found")

        parser = RunFileParser()
        writer = RunFileWriter()

        # Parse real file
        config1 = parser.parse_file(regions_run_path)

        # Write to temp file
        output_file = tmp_path / "regions_copy.run"
        writer.write_file(config1, str(output_file), include_timestamp=False)

        # Parse written file
        config2 = parser.parse_file(str(output_file))

        # Verify same structure
        assert len(config1.upgrades) == len(config2.upgrades)
        assert config1.parameters.run_mode == config2.parameters.run_mode


class TestValidation:
    """Test configuration validation"""

    def test_validate_minimal_config(self):
        """Test validation of minimal valid configuration"""
        config = RunConfiguration(
            parameters=RunParameters(),
            scope=RunScope(),
            upgrades={}
        )

        is_valid, errors = validate_run_configuration(config)

        # Should have warnings about missing files, but config structure is valid
        # Check that we got some validation feedback
        assert isinstance(errors, list)

    def test_validate_with_upgrades(self):
        """Test validation with upgrades"""
        config = RunConfiguration(
            parameters=RunParameters(),
            scope=RunScope(),
            upgrades={}
        )

        config.add_upgrade("Opt-Windows", ["NA", "DoubleGlazed"])

        is_valid, errors = validate_run_configuration(config)

        # Should not have warning about no upgrades
        upgrade_warnings = [e for e in errors if "No upgrades" in e.message]
        assert len(upgrade_warnings) == 0


class TestRunScope:
    """Test RunScope helper methods"""

    def test_get_archetype_list_wildcard(self):
        """Test archetype list parsing with wildcard"""
        scope = RunScope(archetypes="*.H2K")
        arch_list = scope.get_archetype_list()
        assert arch_list == []  # Wildcard returns empty (to be expanded later)

    def test_get_archetype_list_specific(self):
        """Test archetype list parsing with specific files"""
        scope = RunScope(archetypes="house1.H2K, house2.H2K, house3.H2K")
        arch_list = scope.get_archetype_list()
        assert arch_list == ["house1.H2K", "house2.H2K", "house3.H2K"]

    def test_get_location_list_na(self):
        """Test location list parsing with NA"""
        scope = RunScope(locations="NA")
        loc_list = scope.get_location_list()
        assert loc_list == []  # NA means all locations

    def test_get_location_list_specific(self):
        """Test location list parsing with specific locations"""
        scope = RunScope(locations="OTTAWA, TORONTO, VANCOUVER")
        loc_list = scope.get_location_list()
        assert loc_list == ["OTTAWA", "TORONTO", "VANCOUVER"]


class TestOptionUpgrade:
    """Test OptionUpgrade model"""

    def test_parse_choices_string(self):
        """Test parsing choices from string"""
        upgrade = OptionUpgrade(
            option_type="Opt-Windows",
            choices="NA, DoubleGlazed, TripleGlazed"
        )
        assert upgrade.choices == ["NA", "DoubleGlazed", "TripleGlazed"]

    def test_parse_choices_list(self):
        """Test parsing choices from list"""
        upgrade = OptionUpgrade(
            option_type="Opt-Windows",
            choices=["NA", "DoubleGlazed"]
        )
        assert upgrade.choices == ["NA", "DoubleGlazed"]

    def test_to_run_format(self):
        """Test export to .run format"""
        upgrade = OptionUpgrade(
            option_type="Opt-ACH",
            choices=["NA", "1.5", "2.5"]
        )
        output = upgrade.to_run_format()
        assert "Opt-ACH" in output
        assert "NA, 1.5, 2.5" in output
        assert output.startswith("   ")  # Should have indentation
