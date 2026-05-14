# HTAP Run File Configuration Tool - Implementation Plan

## Project Overview

A web-based GUI application for quickly creating HTAP .run files without manually looking up options in HTAP-options.json.

### Key Requirements (from user)
- **Web application** - runs in browser
- **Multi-option selection** - checkboxes for each Opt-* category (e.g., select multiple window types)
- **Simulation count display** - live calculation of total simulations
- **Flexible archetype/location selection** - varies by project
- **No validation needed** - focus on speed and simplicity
- **No templates needed** - direct configuration only
- **Isolated development** - all files in `/configapp`, no changes to main HTAP codebase

## Architecture

### Technology Stack
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Data Format**: JSON (HTAP-options.json)
- **Server**: Simple Python HTTP server for local development
- **Storage**: Browser localStorage for work-in-progress

### Directory Structure
```
C:\HTAP\configapp\
├── PLAN.md                    # This file
├── README.md                  # User documentation
├── index.html                 # Main application page
├── css/
│   └── styles.css            # Application styling
├── js/
│   ├── app.js                # Main application controller
│   ├── optionsLoader.js      # Load and parse HTAP-options.json
│   ├── runFileParser.js      # Parse and generate .run files
│   └── simCalculator.js      # Calculate total simulation count
├── data/
│   ├── HTAP-options.json     # Copy from C:\HTAP\HTAP-options.json
│   └── locations.json        # List of weather locations
├── examples/
│   └── sample.run            # Example .run file for reference
├── output/                    # Generated .run files (gitignored)
└── server.py                  # Python web server
```

## Implementation Phases

### Phase 1: Project Setup & Data Preparation
1. ✅ Create folder structure
2. Copy HTAP-options.json from main directory
3. Extract locations list from HTAP-options.json
4. Create sample .run file for testing
5. Create simple Python web server
6. Create README with usage instructions

### Phase 2: Core UI Layout
7. Build HTML structure with 3-column layout:
   - Left sidebar: Category navigation
   - Center panel: Option selection area
   - Right sidebar: Summary and simulation count
8. Implement responsive CSS styling
9. Create navigation between Opt-* categories
10. Add file menu (New, Open, Save, Export)

### Phase 3: Data Loading & Display
11. Load HTAP-options.json on startup
12. Parse all Opt-* categories
13. Display options with checkboxes for each category
14. Show option metadata (characteristics) where available
15. Implement search/filter for options

### Phase 4: Option Selection Logic
16. Implement checkbox selection for multiple options
17. Track selected options per category
18. Display selection count per category
19. Add "Select All" / "Clear All" buttons
20. Implement "NA" handling (default option)

### Phase 5: Run Scope Configuration
21. Archetype file browser/selector
22. Location multi-selector
23. Ruleset selector
24. Run parameters configuration (mode, paths)

### Phase 6: Simulation Calculator
25. Calculate total simulations dynamically
26. Formula: archetypes × locations × (product of multi-selected options)
27. Display breakdown in summary panel
28. Show warning for large runs (>1000 sims)

### Phase 7: File Generation
29. Parse .run file format
30. Generate RunParameters section
31. Generate RunScope section
32. Generate Upgrades section with selected options
33. Download/save functionality
34. Import existing .run files

### Phase 8: User Experience Enhancements
35. Keyboard shortcuts (Ctrl+S, Ctrl+O, etc.)
36. Auto-save to localStorage
37. Tooltips for options
38. Help documentation
39. Copy to clipboard functionality

## Key Components Design

### 1. Options Loader (optionsLoader.js)
```javascript
class OptionsLoader {
  async loadOptions() {
    // Fetch HTAP-options.json
    // Parse JSON
    // Extract Opt-* parameters
    // Return structured data
  }

  getCategories() {
    // Return list of Opt-* categories
  }

  getOptionsForCategory(category) {
    // Return available options for a category
  }
}
```

### 2. Run File Parser (runFileParser.js)
```javascript
class RunFileParser {
  parse(fileContent) {
    // Parse .run file format
    // Extract sections: RunParameters, RunScope, Upgrades
    // Return configuration object
  }

  generate(config) {
    // Take configuration object
    // Generate .run file content
    // Match exact HTAP format
    // Return string content
  }
}
```

### 3. Simulation Calculator (simCalculator.js)
```javascript
class SimCalculator {
  calculate(config) {
    // archetypes count
    // locations count
    // For each Opt-* with multiple selections, multiply
    // Return total simulation count
  }

  getBreakdown(config) {
    // Return human-readable breakdown
    // "2 archetypes × 3 locations × 4 windows × 6 HVAC = 144 sims"
  }
}
```

### 4. Main App Controller (app.js)
```javascript
class HTAPConfigApp {
  constructor() {
    this.optionsLoader = new OptionsLoader();
    this.runFileParser = new RunFileParser();
    this.simCalculator = new SimCalculator();
    this.config = {};
  }

  init() {
    // Load HTAP-options.json
    // Setup UI
    // Bind events
    // Load localStorage state if exists
  }

  updateSimCount() {
    // Recalculate and display simulation count
  }

  exportRunFile() {
    // Generate .run file
    // Trigger download
  }
}
```

## UI Layout Design

### Left Sidebar - Category Navigation
```
┌────────────────────┐
│ RUN PARAMETERS     │
│  ○ Basic Settings  │
│  ○ File Paths      │
├────────────────────┤
│ RUN SCOPE          │
│  ○ Archetypes      │
│  ○ Locations       │
│  ○ Rulesets        │
├────────────────────┤
│ UPGRADES           │
│  ● Windows      [4]│
│  ● ACH          [2]│
│  ○ Doors           │
│  ● Heating      [6]│
│  ○ Ventilation     │
│  ...               │
└────────────────────┘
```
- Filled circle (●) = has selections
- Empty circle (○) = no selections
- [N] = number of options selected

### Center Panel - Option Selection
```
┌──────────────────────────────────────┐
│ Opt-Windows                          │
│ Search: [____________]               │
├──────────────────────────────────────┤
│ ☐ NA (No modification)               │
│ ☑ dbl-clear-u3.85  (U=3.85, 2 panes) │
│ ☑ dbl-clear-u3.33  (U=3.33, 2 panes) │
│ ☐ tpl-HG-u1.08     (U=1.08, 3 panes) │
│ ☑ quad-HG-u0.68    (U=0.68, 4 panes) │
│ ...                                  │
├──────────────────────────────────────┤
│ 3 options selected                   │
│ [Select All] [Clear All]             │
└──────────────────────────────────────┘
```

### Right Sidebar - Summary
```
┌─────────────────────┐
│ CONFIGURATION       │
├─────────────────────┤
│ Archetypes: 2       │
│ Locations: 3        │
│ Rulesets: 1         │
├─────────────────────┤
│ SELECTED OPTIONS    │
│ Opt-Windows: 3      │
│ Opt-ACH: 2          │
│ Opt-Heating: 6      │
│ (23 others: NA)     │
├─────────────────────┤
│ TOTAL SIMULATIONS   │
│                     │
│      432            │
│                     │
│ 2 × 3 × 3 × 2 × 6  │
├─────────────────────┤
│ [Export .run File]  │
└─────────────────────┘
```

## Data Format Examples

### HTAP-options.json Structure (input)
```json
{
  "Opt-Windows": {
    "structure": "tree",
    "costed": true,
    "options": {
      "NA": { ... },
      "dbl-clear-u3.85": {
        "characteristics": {
          "panes": 2,
          "fill": "air",
          "coat": "clear",
          "u-value": 3.85
        },
        "h2kMap": { ... }
      }
    }
  }
}
```

### Configuration Object (internal)
```javascript
{
  runParameters: {
    runMode: "parametric",
    archetypeDir: "C:/HTAP",
    unitCostsDb: "C:/HTAP/HTAPUnitCosts.json",
    optionsFile: "C:/HTAP/HTAP-options.json"
  },
  runScope: {
    archetypes: ["227NN01552.h2k", "228NN01553.h2k"],
    locations: ["HALIFAX", "OTTAWA", "VANCOUVER"],
    rulesets: ["as-found"]
  },
  upgrades: {
    "Opt-Windows": ["dbl-clear-u3.85", "dbl-clear-u3.33", "quad-HG-u0.68"],
    "Opt-ACH": ["NA", "ACH_1_5"],
    "Opt-Heating-Cooling": ["NG-furnace-94%", "elec-baseboard", "ASHP-std"],
    // ... all other Opt-* default to NA
  }
}
```

### Generated .run File (output)
```
! HTAP-PRM RUN Configuration
! Generated by HTAP Config Tool

RunParameters_START
  run-mode = parametric
  archetype-dir = C:/HTAP
  unit-costs-db = C:/HTAP/HTAPUnitCosts.json
  options-file = C:/HTAP/HTAP-options.json
RunParameters_END

RunScope_START
  archetypes = 227NN01552.h2k, 228NN01553.h2k
  locations = HALIFAX, OTTAWA, VANCOUVER
  rulesets = as-found
RunScope_END

Upgrades_START
  Opt-Windows = dbl-clear-u3.85, dbl-clear-u3.33, quad-HG-u0.68
  Opt-ACH = NA, ACH_1_5
  Opt-Heating-Cooling = NG-furnace-94%, elec-baseboard, ASHP-std
  Opt-Skylights = NA
  Opt-Doors = NA
  ...
Upgrades_END
```

## Development Workflow

1. **Start server**: `python server.py`
2. **Open browser**: Navigate to `http://localhost:8000`
3. **Make changes**: Edit HTML/CSS/JS files
4. **Refresh browser**: See changes immediately
5. **Test**: Load HTAP-options.json, create run file, export

## Testing Strategy

### Manual Testing Checklist
- [ ] Load HTAP-options.json successfully
- [ ] Display all Opt-* categories
- [ ] Select multiple options with checkboxes
- [ ] Calculate simulation count correctly
- [ ] Generate valid .run file format
- [ ] Import existing .run file
- [ ] Search/filter options works
- [ ] Auto-save/restore from localStorage
- [ ] Download .run file works

### Test Cases
1. **Simple run**: 1 archetype, 1 location, all NA → 1 simulation
2. **Basic parametric**: 2 archetypes, 3 locations, 4 window options → 24 simulations
3. **Complex parametric**: Multiple Opt-* with selections → verify calculation
4. **Import/Export**: Load existing fdwr.run, modify, export, verify format

## Future Enhancements (Phase 2)

### Deferred Features
- Cost estimation integration (HTAPUnitCosts.json)
- Templates/presets system
- Validation and error checking
- Bulk operations across parameters
- Results viewer integration
- Comparison view for multiple runs
- Dark mode
- Mobile responsive design

## Success Criteria

✅ Application loads HTAP-options.json correctly
✅ Can select multiple options per Opt-* category using checkboxes
✅ Displays real-time simulation count
✅ Generates valid .run files matching HTAP format
✅ Saves/loads configuration from browser
✅ Works without requiring changes to main HTAP codebase
✅ Simple enough to use without training

## Timeline Estimate

- Phase 1 (Setup): 1 hour
- Phase 2 (UI Layout): 2 hours
- Phase 3 (Data Loading): 2 hours
- Phase 4 (Selection Logic): 2 hours
- Phase 5 (Run Scope): 1 hour
- Phase 6 (Calculator): 1 hour
- Phase 7 (File Generation): 2 hours
- Phase 8 (UX Polish): 2 hours

**Total: ~13 hours** (can be completed in 2-3 work sessions)

## Notes

- Keep it simple - no frameworks, no complex dependencies
- Focus on core functionality first
- Iterate based on user feedback
- All development isolated to `/configapp` folder
- Make copies of any HTAP files needed (don't modify originals)
