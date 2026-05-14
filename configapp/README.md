# HTAP Run File Configuration Tool

A web-based GUI application for quickly creating HTAP .run files without manually looking up options in HTAP-options.json.

## Features

- **Visual Option Selection**: Select multiple options for each Opt-* category using checkboxes
- **Live Simulation Count**: Real-time calculation of total simulations based on your configuration
- **Search & Filter**: Quickly find options with built-in search functionality
- **Import/Export**: Load existing .run files, modify them, and export new ones
- **Auto-Save**: Automatically saves your work to browser localStorage
- **Keyboard Shortcuts**: Speed up your workflow with hotkeys

## Quick Start

### 1. Start the Server

```bash
cd C:\HTAP\configapp
python server.py
```

### 2. Open in Browser

Navigate to: `http://localhost:8000/index.html`

### 3. Start Configuring

1. Configure Run Parameters (run mode, directories)
2. Select Archetypes (enter .h2k filenames)
3. Select Locations (choose from list)
4. Select Upgrade Options (click Opt-* categories in left sidebar)
5. Export your .run file

## User Interface

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Header: New | Open | Export                                  │
├──────────┬──────────────────────────────┬──────────────────┤
│          │                              │                  │
│ Category │   Configuration Panel        │ Summary Panel    │
│  Tree    │   (Checkboxes, inputs)       │ (Sim count)      │
│          │                              │                  │
└──────────┴──────────────────────────────┴──────────────────┘
```

### Left Sidebar - Navigation

- **Run Parameters**: Basic settings and file paths
- **Run Scope**: Archetypes, Locations, Rulesets
- **Upgrades**: All Opt-* categories
  - Circle indicators show selection status
  - Badges show number of options selected

### Center Panel - Configuration

Different panel for each section:

- **Run Parameters**: Dropdowns and text inputs
- **Archetypes**: Text area (one per line)
- **Locations**: Searchable checkbox list
- **Opt-* Categories**: Searchable checkbox list with option details

### Right Sidebar - Summary

- Configuration overview
- Selected option counts
- **Total Simulations** (large display)
- Calculation formula
- Export button

## Workflow

### Creating a New Run File

1. Click "New" or press Ctrl+N
2. Configure Run Parameters:
   - Set run mode (parametric, mesh, sample)
   - Verify file paths
3. Configure Run Scope:
   - Enter archetype filenames (one per line)
   - Select locations from the list
   - Enter ruleset name
4. Select Upgrade Options:
   - Click on Opt-* categories in left sidebar
   - Check boxes next to desired options
   - Use search to filter large lists
   - Select All / Clear All buttons available
5. Review Summary:
   - Check total simulation count
   - Verify all selections
6. Export:
   - Click "Export .run" or press Ctrl+S
   - Save file to desired location

### Loading an Existing Run File

1. Click "Open" or press Ctrl+O
2. Select your .run file
3. Configuration will be loaded into the UI
4. Modify as needed
5. Export with new name

### Multi-Selection for Parametric Runs

To create parametric runs with multiple options:

1. Navigate to an Opt-* category (e.g., Opt-Windows)
2. Check multiple options:
   - ☑ dbl-clear-u3.85
   - ☑ dbl-clear-u3.33
   - ☑ tpl-HG-u1.08
3. Watch the simulation count update
4. Repeat for other categories

Example:
- 2 archetypes
- 3 locations
- 4 window options (Opt-Windows)
- 2 ACH options (Opt-ACH)

Total: 2 × 3 × 4 × 2 = **48 simulations**

## Keyboard Shortcuts

- **Ctrl+N**: New configuration
- **Ctrl+O**: Open .run file
- **Ctrl+S**: Export .run file
- **Space**: Toggle checkbox (when focused)

## Data Files

### Required Files (Already Included)

- `data/HTAP-options.json` - Copy of main HTAP options database
- Locations extracted from Opt-Location category

### Generated Files

- `.run` files exported to your chosen location
- Configuration auto-saved to browser localStorage

## Tips & Tricks

### Faster Selection

1. **Use Search**: Type keywords to filter options quickly
2. **Select All**: Click to select all filtered options
3. **Clear All**: Reset selections for a category

### Large Option Lists

Categories like Opt-Windows or Opt-Heating-Cooling have many options:
- Use search to narrow down
- Look at option details (U-value, characteristics)
- Start with "NA" if unsure

### Monitoring Simulation Count

Watch the right sidebar as you make selections:
- Yellow warning if > 1000 simulations
- Red warning if > 5000 simulations
- Consider reducing options if count is too high

### Saving Your Work

- Configuration automatically saves to browser
- Refresh the page to restore your session
- Export .run file periodically as backup

## File Format

The application generates standard HTAP .run files:

```
! HTAP-PRM RUN Configuration

RunParameters_START
  run-mode = parametric
  archetype-dir = C:/HTAP
  unit-costs-db = C:/HTAP/HTAPUnitCosts.json
  options-file = C:/HTAP/HTAP-options.json
RunParameters_END

RunScope_START
  archetypes = 227NN01552.h2k
  locations = HALIFAX, OTTAWA
  rulesets = as-found
RunScope_END

Upgrades_START
  Opt-Windows = dbl-clear-u3.85, tpl-HG-u1.08
  Opt-ACH = NA
  Opt-Doors = NA
  ...
Upgrades_END
```

## Troubleshooting

### "Failed to load HTAP options"

- Check that `data/HTAP-options.json` exists
- Verify server is running (`python server.py`)
- Try refreshing the browser

### Options not showing

- Make sure you clicked on the category in left sidebar
- Check if search filter is applied
- Verify HTAP-options.json loaded correctly

### Simulation count seems wrong

- Formula: archetypes × locations × (product of multi-selected options)
- Only options with >1 selection are multiplied
- NA (single selection) doesn't multiply

### Browser compatibility

- Works best in Chrome, Firefox, Edge
- Requires modern browser with ES6 support
- LocalStorage must be enabled

## Development

### Project Structure

```
configapp/
├── index.html           # Main application page
├── css/
│   └── styles.css      # Application styling
├── js/
│   ├── app.js          # Main controller
│   ├── optionsLoader.js # Options parser
│   ├── runFileParser.js # .run file handler
│   └── simCalculator.js # Simulation counter
├── data/
│   └── HTAP-options.json # Options database
├── examples/
│   └── sample.run      # Example run file
└── server.py           # Development server
```

### Modifying the Application

1. Edit files in `css/` or `js/`
2. Refresh browser to see changes
3. Check browser console for errors (F12)

### Adding Features

The application is built with vanilla JavaScript and is easy to extend:

- **New panels**: Add to `index.html` and handle in `app.js`
- **New data sources**: Modify `optionsLoader.js`
- **New calculations**: Update `simCalculator.js`
- **Styling**: Edit `css/styles.css`

## Future Enhancements

Planned for future versions:

- Cost estimation integration (HTAPUnitCosts.json)
- Configuration templates/presets
- Validation and error checking
- Batch run management
- Results visualization
- Export to JSON/CSV formats

## Support

For issues or questions:
1. Check this README
2. Review PLAN.md for technical details
3. Inspect browser console for errors
4. Contact HTAP development team

## License

Part of the HTAP (Housing Technology Assessment Platform) project.
Developed by NRCan-IETS-CE-O-HBC.

## Version

Version 1.0 - Initial Release
Date: 2025-01-21
