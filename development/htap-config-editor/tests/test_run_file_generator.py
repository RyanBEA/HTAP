"""
Tests for run file generator module
"""

import pytest
from pathlib import Path
import tempfile
from src.utils.run_file_generator import RunFileGenerator, RunFileTemplate


class TestRunFileGenerator:
    """Test RunFileGenerator class"""

    def test_basic_generation(self):
        """Test that all 3 sections are present in generated file"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }

        selected_options = {
            'Opt-Windows': {'NC_Best-L'},
            'Opt-AboveGradeWall': {'NC_2x6_r19nom_r16Eff'}
        }

        content = generator.generate_run_file(run_config, selected_options)

        # Check all sections present
        assert 'RunParameters_START' in content
        assert 'RunParameters_END' in content
        assert 'RunScope_START' in content
        assert 'RunScope_END' in content
        assert 'Upgrades_START' in content
        assert 'Upgrades_END' in content

    def test_run_parameters_section(self):
        """Test RunParameters section contains correct defaults"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }
        selected_options = {}

        content = generator.generate_run_file(run_config, selected_options)

        # Check default parameters
        assert 'run-mode' in content
        assert 'mesh' in content
        assert 'archetype-dir' in content
        assert 'C:/HTAP/archetypes' in content
        assert 'options-file' in content
        assert 'HTAP-options.json' in content
        assert 'unit-costs-db' in content
        assert 'HTAPUnitCosts.json' in content
        assert 'output-folder' in content
        assert './output' in content

    def test_run_scope_section(self):
        """Test RunScope section with archetypes, locations, rulesets"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': ['arch1.h2k', 'arch2.h2k'],
            'location': 'TORONTO',
            'ruleset': 'NBC9.36'
        }
        selected_options = {}

        content = generator.generate_run_file(run_config, selected_options)

        # Check RunScope content
        assert 'archetypes' in content
        assert 'arch1.h2k, arch2.h2k' in content
        assert 'locations' in content
        assert 'TORONTO' in content
        assert 'rulesets' in content
        assert 'NBC9.36' in content

    def test_run_scope_wildcard_archetypes(self):
        """Test RunScope with empty archetypes uses wildcard"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': [],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }
        selected_options = {}

        content = generator.generate_run_file(run_config, selected_options)

        assert '*.H2K' in content

    def test_run_scope_no_location(self):
        """Test RunScope with no location uses NA"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': ['test.h2k'],
            'location': None,
            'ruleset': 'as-found'
        }
        selected_options = {}

        content = generator.generate_run_file(run_config, selected_options)

        assert 'locations                         = NA' in content

    def test_upgrades_section_single_choice(self):
        """Test Upgrades section with single choice per category"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }

        selected_options = {
            'Opt-Windows': {'NC_Best-L'}
        }

        content = generator.generate_run_file(run_config, selected_options)

        # Check upgrade format
        assert 'Opt-Windows' in content
        assert 'NC_Best-L' in content

    def test_upgrades_section_multiple_choices(self):
        """Test Upgrades section with comma-separated multi-select"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }

        selected_options = {
            'Opt-AboveGradeWall': {
                'NA',
                'NC_2x6_r19nom_r16Eff',
                'NC_R-23(eff)_2x6-16inOC_R22-batt+1inFoilFacedPolyiso_poly_vb'
            },
            'Opt-AtticCeilings': {'CeilR40', 'CeilR50', 'CeilR60'}
        }

        content = generator.generate_run_file(run_config, selected_options)

        # Check comma-separated format
        assert 'Opt-AboveGradeWall' in content
        assert 'NA' in content
        assert 'NC_2x6_r19nom_r16Eff' in content

        assert 'Opt-AtticCeilings' in content
        assert 'CeilR40' in content
        assert 'CeilR50' in content
        assert 'CeilR60' in content

        # Verify comma separation (not line-by-line)
        lines = content.split('\n')
        wall_line = [l for l in lines if 'Opt-AboveGradeWall' in l and '=' in l][0]
        assert ',' in wall_line

    def test_upgrades_section_empty(self):
        """Test Upgrades section when no options selected"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }

        selected_options = {}

        content = generator.generate_run_file(run_config, selected_options)

        # Should have Upgrades section but with comment
        assert 'Upgrades_START' in content
        assert 'Upgrades_END' in content
        assert '! No upgrades selected' in content

    def test_custom_parameters(self):
        """Test custom parameters override defaults"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }
        selected_options = {}

        custom_params = {
            'run-mode': 'parametric',
            'archetype-dir': 'C:/CustomPath',
            'compute-costs': 'true'
        }

        content = generator.generate_run_file(run_config, selected_options, custom_params)

        # Check custom params applied
        assert 'parametric' in content
        assert 'C:/CustomPath' in content
        assert 'compute-costs' in content
        assert 'true' in content

    def test_validate_format_valid(self):
        """Test format validation with valid file"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }
        selected_options = {
            'Opt-Windows': {'NC_Best-L'}
        }

        content = generator.generate_run_file(run_config, selected_options)

        is_valid, errors = generator.validate_format(content)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_format_missing_section(self):
        """Test format validation detects missing sections"""
        generator = RunFileGenerator()

        # Invalid content missing Upgrades section
        content = """
RunParameters_START
  run-mode = mesh
RunParameters_END

RunScope_START
  archetypes = test.h2k
RunScope_END
"""

        is_valid, errors = generator.validate_format(content)

        assert is_valid is False
        assert any('Upgrades' in error for error in errors)

    def test_validate_format_mismatched_tags(self):
        """Test format validation detects mismatched START/END tags"""
        generator = RunFileGenerator()

        content = """
RunParameters_START
  run-mode = mesh

RunScope_START
  archetypes = test.h2k
RunScope_END

Upgrades_START
Upgrades_END
"""

        is_valid, errors = generator.validate_format(content)

        assert is_valid is False
        assert any('RunParameters_END' in error for error in errors)

    def test_validate_format_wrong_order(self):
        """Test format validation detects wrong section order"""
        generator = RunFileGenerator()

        # Wrong order: Upgrades before RunScope
        content = """
RunParameters_START
  run-mode = mesh
RunParameters_END

Upgrades_START
Upgrades_END

RunScope_START
  archetypes = test.h2k
RunScope_END
"""

        is_valid, errors = generator.validate_format(content)

        assert is_valid is False
        assert any('must come before' in error for error in errors)

    def test_save_to_file(self):
        """Test saving run file to disk"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }
        selected_options = {
            'Opt-Windows': {'NC_Best-L'}
        }

        content = generator.generate_run_file(run_config, selected_options)

        # Save to temp file
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / 'test.run'
            generator.save_to_file(content, str(filepath))

            # Verify file exists and content matches
            assert filepath.exists()

            with open(filepath, 'r', encoding='utf-8') as f:
                saved_content = f.read()

            assert saved_content == content

    def test_save_to_file_creates_directory(self):
        """Test save creates parent directories if needed"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }
        selected_options = {}

        content = generator.generate_run_file(run_config, selected_options)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / 'subdir' / 'nested' / 'test.run'
            generator.save_to_file(content, str(filepath))

            assert filepath.exists()

    def test_sorted_output(self):
        """Test that output is sorted for consistency"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }

        # Add options in random order
        selected_options = {
            'Opt-Windows': {'Choice3', 'Choice1', 'Choice2'},
            'Opt-AboveGradeWall': {'ChoiceB', 'ChoiceA'},
            'Opt-Heating-Cooling': {'ChoiceZ'}
        }

        content = generator.generate_run_file(run_config, selected_options)

        lines = content.split('\n')

        # Find Upgrades section
        upgrades_start = None
        upgrades_end = None
        for i, line in enumerate(lines):
            if 'Upgrades_START' in line:
                upgrades_start = i
            elif 'Upgrades_END' in line:
                upgrades_end = i

        upgrades_lines = lines[upgrades_start:upgrades_end]

        # Categories should be in sorted order
        categories = []
        for line in upgrades_lines:
            if 'Opt-' in line and '=' in line:
                category = line.split('=')[0].strip()
                categories.append(category)

        assert categories == sorted(categories)

        # Choices within each category should be sorted
        for line in upgrades_lines:
            if 'Opt-Windows' in line and '=' in line:
                choices_part = line.split('=')[1].strip()
                choices = [c.strip() for c in choices_part.split(',')]
                assert choices == sorted(choices)


class TestRunFileTemplates:
    """Test RunFileTemplate class"""

    def test_get_template_names(self):
        """Test get_template_names returns list of templates"""
        names = RunFileTemplate.get_template_names()

        assert isinstance(names, list)
        assert len(names) > 0
        assert 'simple_single_run' in names
        assert 'parametric_study' in names
        assert 'cost_optimization' in names
        assert 'location_comparison' in names

    def test_get_template_valid(self):
        """Test get_template returns template data"""
        template = RunFileTemplate.get_template('simple_single_run')

        assert template is not None
        assert 'name' in template
        assert 'description' in template
        assert 'run_mode' in template

    def test_get_template_invalid(self):
        """Test get_template returns None for invalid name"""
        template = RunFileTemplate.get_template('nonexistent_template')

        assert template is None

    def test_get_all_templates(self):
        """Test get_all_templates returns dict"""
        templates = RunFileTemplate.get_all_templates()

        assert isinstance(templates, dict)
        assert len(templates) >= 4
        assert 'simple_single_run' in templates
        assert 'parametric_study' in templates

    def test_template_structure(self):
        """Test each template has required fields"""
        templates = RunFileTemplate.get_all_templates()

        for name, template in templates.items():
            assert 'name' in template, f"Template {name} missing 'name'"
            assert 'description' in template, f"Template {name} missing 'description'"
            assert 'run_mode' in template, f"Template {name} missing 'run_mode'"
            assert 'example_note' in template, f"Template {name} missing 'example_note'"

    def test_template_with_generator(self):
        """Test template integration with generator"""
        generator = RunFileGenerator()
        template = RunFileTemplate.get_template('parametric_study')

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }
        selected_options = {
            'Opt-Windows': {'NC_Best-L'}
        }

        custom_params = {
            'run-mode': template['run_mode']
        }

        content = generator.generate_run_file(run_config, selected_options, custom_params)

        assert template['run_mode'] in content

    def test_cost_optimization_template(self):
        """Test cost optimization template has custom params"""
        template = RunFileTemplate.get_template('cost_optimization')

        assert 'custom_params' in template
        assert 'compute-costs' in template['custom_params']


class TestRealWorldScenarios:
    """Test real-world scenarios and edge cases"""

    def test_large_parametric_study(self):
        """Test large parametric study with multiple options"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': ['arch1.h2k', 'arch2.h2k', 'arch3.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'NBC9.36'
        }

        selected_options = {
            'Opt-Windows': {'NC_Best-L', 'NC_Med-L', 'NC_Low-L'},
            'Opt-AboveGradeWall': {'NA', 'NC_2x6_r19nom_r16Eff'},
            'Opt-AtticCeilings': {'CeilR40', 'CeilR50', 'CeilR60'},
            'Opt-Heating-Cooling': {'baseboard', 'ASHP'},
            'Opt-DHWSystem': {'elec', 'gas'}
        }

        content = generator.generate_run_file(run_config, selected_options)

        # Validate
        is_valid, errors = generator.validate_format(content)
        assert is_valid is True

        # Check all options present
        assert 'Opt-Windows' in content
        assert 'Opt-AboveGradeWall' in content
        assert 'Opt-AtticCeilings' in content
        assert 'Opt-Heating-Cooling' in content
        assert 'Opt-DHWSystem' in content

    def test_export_matches_real_run_file(self):
        """Test that generated file structure matches real regions.run file"""
        generator = RunFileGenerator()

        # Configuration similar to regions.run
        run_config = {
            'archetypes': [],  # Will use wildcard
            'location': None,  # Will use NA
            'ruleset': 'as-found'
        }

        selected_options = {
            'Opt-ResultHouseCode': {'General'},
            'Opt-ACH': {'NA'},
            'Opt-Windows': {'NA'},
            'Opt-AboveGradeWall': {
                'NA',
                'NC_2x6_r19nom_r16Eff',
                'NC_R-23(eff)_2x6-16inOC_R22-batt+1inFoilFacedPolyiso_poly_vb'
            },
            'Opt-H2KFoundation': {'NA'},
            'Opt-VentSystem': {'NA'},
            'Opt-DHWSystem': {'NA'},
            'Opt-Heating-Cooling': {'NA'}
        }

        content = generator.generate_run_file(run_config, selected_options)

        # Validate structure
        is_valid, errors = generator.validate_format(content)
        assert is_valid is True

        # Check key patterns from real file
        assert 'RunParameters_START' in content
        assert 'RunScope_START' in content
        assert 'Upgrades_START' in content
        assert '*.H2K' in content  # Wildcard archetypes
        assert 'locations                         = NA' in content
        assert 'as-found' in content

    def test_minimal_configuration(self):
        """Test minimal valid configuration"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': ['single.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }

        # No options selected
        selected_options = {}

        content = generator.generate_run_file(run_config, selected_options)

        is_valid, errors = generator.validate_format(content)
        assert is_valid is True

    def test_special_characters_in_choices(self):
        """Test handling of special characters in choice names"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }

        # Choices with special characters (common in HTAP)
        selected_options = {
            'Opt-AboveGradeWall': {
                'NC_R-23(eff)_2x6-16inOC_R22-batt+1inFoilFacedPolyiso_poly_vb'
            }
        }

        content = generator.generate_run_file(run_config, selected_options)

        # Should handle without errors
        is_valid, errors = generator.validate_format(content)
        assert is_valid is True

        # Check special chars preserved
        assert 'R-23(eff)' in content
        assert '2x6-16inOC' in content
        assert 'R22-batt+1in' in content

    def test_unicode_encoding(self):
        """Test UTF-8 encoding is used"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }
        selected_options = {}

        content = generator.generate_run_file(run_config, selected_options)

        # Save and read back
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / 'test.run'
            generator.save_to_file(content, str(filepath))

            # Read with explicit UTF-8 encoding
            with open(filepath, 'r', encoding='utf-8') as f:
                saved = f.read()

            assert saved == content

    def test_line_endings(self):
        """Test Unix line endings are used"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }
        selected_options = {}

        content = generator.generate_run_file(run_config, selected_options)

        # Should use \n not \r\n
        assert '\r\n' not in content
        assert '\n' in content

    def test_timestamp_in_header(self):
        """Test generated file includes timestamp"""
        generator = RunFileGenerator()

        run_config = {
            'archetypes': ['test.h2k'],
            'location': 'OTTAWA',
            'ruleset': 'as-found'
        }
        selected_options = {}

        content = generator.generate_run_file(run_config, selected_options)

        # Check for timestamp pattern
        assert 'Generated:' in content
        # Should have year in timestamp
        from datetime import datetime
        current_year = str(datetime.now().year)
        assert current_year in content
