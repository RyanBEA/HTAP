# HTAP Configuration Editor - User Guide

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [User Interface](#user-interface)
4. [Typical Workflow](#typical-workflow)
5. [Advanced Features](#advanced-features)
6. [Tips & Best Practices](#tips--best-practices)
7. [Troubleshooting](#troubleshooting)
8. [Appendix](#appendix)

---

## Overview

### What is HTAP Configuration Editor?

The HTAP Configuration Editor is a Streamlit-based web application that simplifies the creation of parametric run configurations for the Housing Technology Assessment Platform (HTAP). Instead of manually editing .run files in a text editor, you can:

- Browse and search 769 building upgrade options across 34 categories
- Configure single or parametric runs with visual feedback
- Calculate costs for different upgrade combinations
- Validate configurations before running simulations
- Export production-ready .run files for htap-prm.rb

### Key Features

**Option Management:**
- Browse options by category with detailed descriptions
- Search across 769 options with filters
- Select single options or multiple options for parametric studies
- View real-time combination counts for parametric runs

**Cost Analysis:**
- Calculate costs for selected upgrades
- View detailed component breakdowns
- Compare costs across different regional sources
- Export cost reports to CSV

**Validation & Export:**
- Validate configurations before export
- Preview .run file contents
- One-click download of ready-to-use .run files
- Helpful error messages with resolution suggestions

**Performance:**
- Instant search (<10ms for 769 options)
- Fast cost calculations (<1s for large configs)
- Responsive UI with loading states
- Handles configurations with 500+ combinations

### Who Should Use It?

- **Energy Modelers**: Create parametric studies for housing energy analysis
- **Researchers**: Configure optimization runs for housing technology research
- **Policy Analysts**: Evaluate building code scenarios and compliance
- **HTAP Users**: Anyone who needs to create .run files for htap-prm.rb

---

## Installation

### Prerequisites

Before installing, ensure you have:

1. **Python 3.9 or higher**
   ```bash
   python --version  # Should show 3.9.x or higher
   ```

2. **HTAP installed at `C:/HTAP/`**
   - Required files:
     - `C:/HTAP/HTAP-options.json` (0.32 MB)
     - `C:/HTAP/HTAPUnitCosts.json` (0.19 MB)
     - `C:/HTAP/Archetypes/` (directory with .h2k files)

3. **Git** (optional, for cloning repository)

### Setup Steps

1. **Clone or download the repository**
   ```bash
   cd C:/HTAP/development
   git clone <repository-url> htap-config-editor
   cd htap-config-editor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   This installs:
   - `streamlit` - Web application framework
   - `pandas` - Data manipulation and search
   - `plotly` - Interactive cost charts
   - `pydantic` - Data validation

3. **Verify installation**
   ```bash
   # Check that files exist
   python -c "from pathlib import Path; print('OK' if Path('C:/HTAP/HTAP-options.json').exists() else 'MISSING')"
   ```

### Accessing the Application

**Start the application:**
```bash
streamlit run app.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501
```

**Open in browser:**
- Navigate to `http://localhost:8501`
- Application should load in 2-3 seconds
- You should see the three-panel interface

---

## User Interface

The application uses a three-panel layout for efficient workflow:

### LEFT Panel: Run Configuration

**Purpose**: Configure run parameters and scope

**Sections:**

1. **Run Mode**
   - `parametric`: Run all combinations of selected options
   - `mesh`: Grid search across option space
   - `sample`: Sample from option space

2. **File Paths**
   - Archetype directory (default: `C:/HTAP/Archetypes`)
   - Options file (default: `C:/HTAP/HTAP-options.json`)
   - Unit costs database (default: `C:/HTAP/HTAPUnitCosts.json`)

3. **Run Scope**
   - **Archetypes**: Select .h2k building files (e.g., BC-base.h2k)
   - **Locations**: Choose weather locations (e.g., Kelowna, Vancouver)
   - **Rulesets**: Apply building code rulesets (optional)

4. **Cost Source**
   - Select regional cost database (e.g., LEEP-ON-Ottawa)
   - Affects cost calculations in right panel

### MIDDLE Panel: Option Selection

**Purpose**: Browse and select upgrade options

**Tabs:**

1. **Browse Tab**
   - All 34 categories displayed as expandable sections
   - Each category shows:
     - Category name (e.g., Opt-Windows)
     - Number of options available
     - Whether category has cost data
     - Selection mode (single/multi-select)
   - Select options using radio buttons or multi-select

2. **Search Tab**
   - **Query**: Search across option names, tags, descriptions
   - **Filters**:
     - Categories: Filter by specific categories
     - Cost Availability: Show only options with costs
     - Structure: Filter by flat/tree structure
   - **Results**: Table with category, option name, tags, cost status
   - Click search results to select options

3. **Statistics Tab**
   - Summary of selected options
   - Category-level statistics
   - Option coverage metrics
   - Cost data availability

### RIGHT Panel: Review & Export

**Purpose**: Review, validate, and export configuration

**Tabs:**

1. **Validation Tab**
   - Real-time configuration validation
   - Three severity levels:
     - **Errors** (red): Must fix before export
     - **Warnings** (yellow): Recommended to address
     - **Info** (blue): Informational messages
   - File path checks
   - Upgrade validation
   - Combination count warnings (>100, >500)

2. **Costs Tab**
   - **Summary**: Total cost, option count, component count
   - **Breakdown**: Costs by category with bar chart
   - **Details**: Component-level costs with pie chart
   - **Export**: Download cost report as CSV
   - Uses selected cost source from left panel

3. **Export Tab**
   - **Preview**: View generated .run file contents
   - **Statistics**: File size, line count, estimated run time
   - **Download**: One-click download of .run file
   - **Copy**: Copy contents to clipboard (if supported)

---

## Typical Workflow

### 1. Basic Configuration

**Goal**: Set up run parameters and scope

**Steps:**

1. **Select Run Mode** (left panel)
   - For single run: Keep `parametric` (will run 1 configuration)
   - For parametric study: Use `parametric`

2. **Verify File Paths** (left panel)
   - Default paths should work if HTAP is at `C:/HTAP/`
   - Modify if HTAP is installed elsewhere

3. **Select Archetype** (left panel)
   - Choose base building file (e.g., `BC-base.h2k`)
   - Multiple archetypes = run will iterate over each

4. **Select Location** (left panel)
   - Choose weather location (e.g., `Kelowna`)
   - Multiple locations = parametric combinations

5. **Choose Cost Source** (left panel)
   - Select regional cost database
   - Default: `LEEP-ON-Ottawa`

**Result**: Basic run configuration ready for option selection

### 2. Select Options

**Method A: Browse by Category** (middle panel, Browse tab)

1. Expand category (e.g., "Opt-Windows")
2. Review available options
3. Select option using radio button (single) or checkboxes (multi)
4. Repeat for other categories

**Method B: Search** (middle panel, Search tab)

1. Enter search term (e.g., "triple glazed")
2. Apply filters if needed (category, costs)
3. Review search results
4. Click "Select" button to add option

**Tips:**
- Use search for finding specific options quickly
- Use browse for systematic category review
- Multi-select mode enabled by toggle in each category
- Selected options show with checkmark icon

### 3. Review Costs

**Goal**: Understand cost implications of selections

**Steps:**

1. Navigate to **Costs tab** (right panel)

2. Review **Summary**:
   - Total cost estimate
   - Number of costed options
   - Number of cost components

3. Check **Breakdown**:
   - Cost by category (bar chart)
   - Identifies most expensive categories

4. Examine **Details**:
   - Component-level costs
   - Material vs. labor breakdown
   - Component quantities and units

5. **Export to CSV** (optional):
   - Click "Export Cost Report"
   - Downloads detailed CSV file
   - Includes all component-level data

**Note**: Not all options have cost data. Options without costs will show as $0.

### 4. Export Configuration

**Goal**: Create .run file for htap-prm.rb

**Steps:**

1. Navigate to **Validation tab** (right panel)

2. **Check for errors**:
   - Red errors must be fixed
   - Yellow warnings should be reviewed
   - Blue info messages are optional

3. **Fix any issues**:
   - Invalid paths: Update in left panel
   - Missing files: Verify HTAP installation
   - Too many combinations: Reduce options or proceed

4. Navigate to **Export tab** (right panel)

5. **Preview .run file**:
   - Review generated content
   - Verify all options included
   - Check combination count

6. **Download**:
   - Click "Download .run file"
   - Save to desired location (e.g., `C:/HTAP/my-study.run`)

**Result**: Production-ready .run file ready for simulation

### 5. Run Simulation

**Goal**: Execute HTAP simulation with exported configuration

**Command:**
```bash
cd C:/HTAP
ruby htap-prm.rb -r my-study.run -c -k -t 7
```

**Flags:**
- `-r my-study.run`: Specify run file
- `-c`: Compute costs
- `-k`: Keep generated files
- `-t 7`: Use 7 parallel threads

**Monitor Progress:**
- Watch console output for progress
- Check `HTAP-prm_log.txt` for detailed logs
- Results written to `HTAP-prm-output.csv`

**Expected Duration:**
- Single run: 10-30 seconds
- 10 combinations: 1-3 minutes
- 100 combinations: 10-30 minutes
- 500+ combinations: 1-3 hours (depends on threads)

---

## Advanced Features

### Parametric Runs (Multi-Select Mode)

**Purpose**: Run multiple option combinations to explore design space

**How to use:**

1. **Enable multi-select** for categories you want to vary:
   - In Browse tab, toggle "Multi-Select" for category
   - Category changes from radio buttons to checkboxes

2. **Select multiple options** in each category:
   - Example: Select 3 wall insulation levels
   - Example: Select 4 HVAC systems

3. **View combination count** (Validation tab):
   - Shows total number of runs
   - Formula: multiply counts across categories
   - Example: 3 walls × 4 HVAC = 12 runs

4. **Warnings**:
   - >100 combinations: Yellow warning
   - >500 combinations: Red warning (confirm intended)

**Use cases:**
- Optimization studies (find lowest cost or energy)
- Sensitivity analysis (how does X affect Y?)
- Code compliance testing (test multiple approaches)

### Search with Filters

**Advanced search techniques:**

1. **Wildcard search**:
   - `window*`: Matches "window", "windows", "window-triple"
   - `*baseboard*`: Matches "elecBaseboard", "baseboardHeating"

2. **Combined filters**:
   - Query: "triple" + Category: "Opt-Windows"
   - Query: "insulation" + Costs: "Required"

3. **Tag-based search**:
   - Options tagged with keywords (e.g., "high-performance")
   - Search finds options by tags

4. **Result management**:
   - Limit: Control max results (default 100)
   - Sort: Results sorted by relevance

**Performance**:
- Search completes in <10ms for all 769 options
- No lag even with complex filters

### Cost Comparison (Multiple Sources)

**Compare costs across regions:**

1. Select baseline cost source (left panel)
2. Calculate costs (right panel, Costs tab)
3. Export cost report to CSV
4. Change cost source to different region
5. Export again with different filename
6. Compare CSVs in Excel or analysis tool

**Common sources:**
- `LEEP-ON-Ottawa`: Ontario costs
- `LEEP-BC-KamloopsChesnut`: BC Kamloops costs
- `LEEP-BC-Victoria`: BC Victoria costs

**Source inheritance**:
- Some sources inherit from others
- If component not found in selected source, falls back to parent
- Example: LEEP-BC-Kelowna → LEEP-ON-Ottawa

### Large Parametric Runs (>500 combinations)

**Managing large studies:**

1. **Start small**: Test with subset first
   - Select 1-2 options per category
   - Verify configuration works
   - Then expand to full study

2. **Chunk runs**: Break into smaller pieces
   - Create multiple .run files
   - Run separately and combine results
   - Safer for very large studies

3. **Resource planning**:
   - 500 runs @ 20s each = ~2.8 hours (7 threads)
   - Ensure adequate disk space (1-2 GB)
   - Monitor system resources

4. **Resume capability**:
   - htap-prm.rb can resume interrupted runs
   - Check `HTAP-prm.resume` file
   - Rerun same command to continue

---

## Tips & Best Practices

### Before Starting

**Verify HTAP installation:**
```bash
# Check files exist
dir C:\HTAP\HTAP-options.json
dir C:\HTAP\HTAPUnitCosts.json
dir C:\HTAP\Archetypes

# Check HOT2000 CLI (required for running simulations)
dir C:\H2K-CLI-Min\
```

**Understand your goal:**
- Single run vs. parametric study?
- Cost analysis needed?
- Which archetypes/locations relevant?

**Review available options:**
- Browse categories in middle panel
- Check Statistics tab for overview
- Understand option meanings (see HTAP documentation)

### While Configuring

**Start simple:**
- Begin with single archetype and location
- Add 2-3 key options
- Verify configuration exports correctly
- Then expand to full study

**Test before large runs:**
- Export small test configuration
- Run with htap-prm.rb to verify
- Check results look correct
- Then scale up to full parametric study

**Use meaningful names:**
- Save .run files with descriptive names
- Example: `bc-walls-windows-study.run`
- Include date or version: `sensitivity-2025-10-09.run`

**Document your choices:**
- Keep notes on why you selected options
- Save multiple versions as you iterate
- Export cost reports for reference

### Large Parametric Runs

**Warnings for >100 combinations:**
- Review if all combinations intended
- Consider if smaller study would suffice
- Estimate total runtime

**Warnings for >500 combinations:**
- Confirm this is necessary
- Plan for long runtime (hours)
- Ensure system won't be interrupted
- Consider breaking into chunks

**Optimization:**
- Use maximum threads (-t flag)
- Run during off-hours
- Monitor first few runs for issues
- Have contingency plan for failures

### Cost Analysis

**Understanding cost data:**
- Not all options have costs defined
- Costs are incremental (vs. baseline)
- Regional variation is significant
- Material + labor both included

**Using cost reports:**
- Export to CSV for detailed analysis
- Compare across scenarios
- Identify cost drivers
- Support decision-making

**Missing costs:**
- Some components may not have regional data
- Falls back to parent source if available
- Shows $0 if truly unavailable
- Review "source_used" column in CSV

---

## Troubleshooting

### File Not Found Errors

**Problem**: "Options file not found: C:/HTAP/HTAP-options.json"

**Solutions:**
1. Verify HTAP is installed at `C:/HTAP/`
2. Check file exists: `dir C:\HTAP\HTAP-options.json`
3. If HTAP is elsewhere, update paths in left panel
4. Ensure correct capitalization (case-sensitive on some systems)

**Problem**: "Archetype directory not found"

**Solutions:**
1. Check directory exists: `dir C:\HTAP\Archetypes`
2. Verify .h2k files are in directory
3. Update path in left panel if needed
4. Run `Archetypes/CopyToH2K.rb` if archetypes missing

### Options Not Loading

**Problem**: Categories show 0 options or missing

**Solutions:**
1. Check HTAP-options.json is valid JSON (not corrupted)
2. Restart application (may be cache issue)
3. Check browser console for errors (F12)
4. Verify file size is ~0.32 MB (if much smaller, may be truncated)

**Problem**: Search returns no results

**Solutions:**
1. Remove filters and try again
2. Check spelling in query
3. Try broader search term
4. Verify search index loaded (check Statistics tab)

### Export Validation Fails

**Problem**: "Cannot export - configuration has errors"

**Solutions:**
1. Review Validation tab for specific errors
2. Fix red errors (required)
3. Consider yellow warnings (recommended)
4. Check file paths are correct and accessible

**Problem**: "Too many combinations" warning

**Solutions:**
1. Reduce number of options in some categories
2. Remove multi-select from less important categories
3. Confirm large study is intended
4. Proceed if combination count is acceptable

### Costs Showing as $0

**Problem**: Options have costs defined but show $0

**Solutions:**
1. Check cost source is selected (left panel)
2. Verify cost source has data for components
3. Try different cost source (may have better coverage)
4. Some options may not have cost data (expected)

**Problem**: Cost report shows "Component not found"

**Solutions:**
1. Normal for some components in some regions
2. Try parent source (e.g., LEEP-ON-Ottawa)
3. Check if custom cost defined (should still show)
4. Review HTAPUnitCosts.json for component availability

### Application Won't Start

**Problem**: `streamlit run app.py` fails

**Solutions:**
1. Check Python version: `python --version` (need 3.9+)
2. Verify dependencies installed: `pip list | grep streamlit`
3. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
4. Check for error messages and search for solutions

**Problem**: Application loads but shows errors

**Solutions:**
1. Check browser console (F12) for JavaScript errors
2. Try different browser (Chrome, Firefox, Edge)
3. Clear browser cache
4. Check for conflicting Streamlit applications on same port

### Performance Issues

**Problem**: Application is slow or laggy

**Solutions:**
1. Close other applications to free memory
2. Restart Streamlit application
3. Clear browser cache
4. Check system resources (Task Manager)

**Problem**: Search is slow (>100ms)

**Solutions:**
1. Restart application (may need to rebuild index)
2. Check system resources
3. Reduce result limit
4. This shouldn't happen normally (<10ms typical)

---

## Appendix

### .run File Format Specification

**Structure:**
```
RunParameters_START
  run-mode = parametric|mesh|sample
  archetype-dir = C:/HTAP/Archetypes
  options-file = C:/HTAP/HTAP-options.json
  unit-costs-db = C:/HTAP/HTAPUnitCosts.json
RunParameters_END

RunScope_START
  archetypes = archetype1.h2k, archetype2.h2k
  locations = CITY1, CITY2
  rulesets = ruleset1, ruleset2
RunScope_END

Upgrades_START
  Opt-Attribute1 = choice1
  Opt-Attribute2 = choice1, choice2, choice3
  Opt-Attribute3 = choice1
Upgrades_END
```

**Sections:**

1. **RunParameters**: Configuration settings
   - `run-mode`: Type of run (parametric, mesh, sample)
   - `archetype-dir`: Path to .h2k files
   - `options-file`: Path to HTAP-options.json
   - `unit-costs-db`: Path to HTAPUnitCosts.json

2. **RunScope**: Scope of study
   - `archetypes`: Comma-separated list of .h2k files
   - `locations`: Comma-separated list of weather locations
   - `rulesets`: Optional rulesets to apply

3. **Upgrades**: Options to simulate
   - Format: `Opt-CategoryName = choice1, choice2, ...`
   - Single choice = fixed for all runs
   - Multiple choices = parametric variation
   - Order doesn't matter
   - Use "NA" to skip an option

### Example Configurations

**Example 1: Single Run**
```
RunParameters_START
  run-mode = parametric
  archetype-dir = C:/HTAP/Archetypes
  options-file = C:/HTAP/HTAP-options.json
  unit-costs-db = C:/HTAP/HTAPUnitCosts.json
RunParameters_END

RunScope_START
  archetypes = BC-base.h2k
  locations = Kelowna
RunScope_END

Upgrades_START
  Opt-ACH = ACH_3_0
  Opt-Windows = NC_2g_HG_u1.65
  Opt-Heating-Cooling = elecBaseboard
Upgrades_END
```
*Result: 1 simulation*

**Example 2: Parametric Study (12 runs)**
```
Upgrades_START
  Opt-ACH = ACH_2_5, ACH_3_0
  Opt-Windows = NC_2g_HG_u1.65, NC_3g_HG_u1.0
  Opt-Heating-Cooling = elecBaseboard, CCASHP, ASHP
Upgrades_END
```
*Result: 2 × 2 × 3 = 12 simulations*

**Example 3: Location Comparison (3 runs)**
```
RunScope_START
  archetypes = BC-base.h2k
  locations = Kelowna, Vancouver, Victoria
RunScope_END

Upgrades_START
  Opt-ACH = ACH_3_0
  Opt-Windows = NC_3g_HG_u1.0
Upgrades_END
```
*Result: 3 simulations (one per location)*

### Keyboard Shortcuts

**Browser shortcuts:**
- `Ctrl+F`: Find on page
- `Ctrl+R`: Reload application
- `F12`: Open browser console (for debugging)

**Streamlit shortcuts:**
- `R`: Rerun application (if in development mode)
- `C`: Clear cache
- `Esc`: Close dialogs

### Option Category Reference

**34 Categories** (abbreviated list):

**Building Envelope:**
- `Opt-ACH`: Air changes per hour (airtightness)
- `Opt-Windows`: Window specifications
- `Opt-Doors`: Door specifications
- `Opt-AboveGradeWall`: Wall insulation
- `Opt-AtticCeilings`: Attic/ceiling insulation
- `Opt-ExposedFloor`: Exposed floor insulation
- `Opt-FoundationWallExtIns`: Foundation wall exterior insulation
- `Opt-FoundationWallIntIns`: Foundation wall interior insulation
- `Opt-FoundationSlabOnGrade`: Slab-on-grade insulation
- `Opt-FoundationSlabBelowGrade`: Below-grade slab insulation

**HVAC Systems:**
- `Opt-Heating-Cooling`: Heating and cooling system
- `Opt-DHWSystem`: Domestic hot water system
- `Opt-VentSystem`: Ventilation system
- `Opt-HRVduct`: HRV ductwork configuration
- `Opt-DWHRandSDHW`: Drain water heat recovery

**Renewables:**
- `Opt-H2K-PV`: Photovoltaic system

**Configuration:**
- `Opt-Location`: Weather location
- `Opt-Archetype`: Base building archetype
- `Opt-Ruleset`: Building code ruleset
- `Opt-ResultHouseCode`: Output mode (General, SOC, HOC, etc.)

**Other:**
- `GOconfig_parameters`: Global optimization parameters
- `GOconfig_cost_source`: Cost data source
- `GOconfig_rulesets`: Ruleset configuration

### Cost Source Reference

**Available Sources:**
- `LEEP-ON-Ottawa`: Ontario (Ottawa) costs
- `LEEP-BC-KamloopsChesnut`: BC Kamloops costs
- `LEEP-BC-Victoria`: BC Victoria costs
- `LEEP-BC-Kelowna`: BC Kelowna costs (inherits from Ottawa)
- Additional sources may be available in HTAPUnitCosts.json

**Inheritance Chain:**
- LEEP-BC-Kelowna → LEEP-ON-Ottawa
- LEEP-BC-KamloopsChesnut → LEEP-ON-Ottawa
- LEEP-BC-Victoria → LEEP-ON-Ottawa

### Getting Help

**Resources:**
- HTAP Documentation: See `C:/HTAP/` repository
- HOT2000 Documentation: NRCan website
- Issues: Report bugs or request features via repository

**Support:**
- Check this guide first
- Review Troubleshooting section
- Check browser console for errors (F12)
- Contact HTAP maintainers with details

**Reporting Issues:**
Include:
- Error message (exact text)
- Steps to reproduce
- Screenshot if relevant
- Browser and OS version
- Configuration file (if applicable)

---

**Version**: 1.0.0
**Last Updated**: 2025-10-09
**Application**: HTAP Configuration Editor
