# Quick Start Guide

## Option 1: Double-Click Start (Easiest)

1. **Double-click** `start-server.bat`
2. Browser will open automatically
3. Start configuring your run file!
4. Press any key in the command window when done

## Option 2: Manual Start

1. Open command prompt
2. Navigate to the folder:
   ```
   cd C:\HTAP\configapp
   ```
3. Start the server:
   ```
   python server.py
   ```
4. Open browser and go to: `http://localhost:8000/index.html`

## First Steps

1. **Configure Run Parameters**
   - Click "Basic Settings" in left sidebar
   - Verify paths are correct (should auto-populate)

2. **Add Archetypes**
   - Click "Archetypes" in left sidebar
   - Enter .h2k filenames (one per line), e.g.:
     ```
     227NN01552.h2k
     228NN01553.h2k
     ```

3. **Select Locations**
   - Click "Locations" in left sidebar
   - Use search box to find cities
   - Check boxes next to desired locations

4. **Select Upgrade Options**
   - Click on any Opt-* category (e.g., "Opt-Windows")
   - Check multiple options for parametric runs:
     - ☑ dbl-clear-u3.85
     - ☑ dbl-clear-u3.33
     - ☑ tpl-HG-u1.08
   - Use search to filter options quickly
   - Click "Select All" or "Clear All" as needed

5. **Check Simulation Count**
   - Right sidebar shows total simulations
   - Updates automatically as you select options
   - Formula shown below count

6. **Export Run File**
   - Click "Export .run" button
   - Save to desired location
   - Run with htap-prm.rb as usual!

## Example Workflow

Create a window comparison study:

1. Select 1 archetype: `227NN01552.h2k`
2. Select 1 location: `HALIFAX`
3. Navigate to Opt-Windows
4. Select 4 window options:
   - dbl-clear-u3.85 (baseline)
   - dbl-clear-u3.33 (better)
   - tpl-HG-u1.08 (high performance)
   - quad-HG-u0.68 (premium)
5. All other Opt-* categories stay at NA
6. Total: **4 simulations**
7. Export as `window-comparison.run`

## Tips

- **Search is your friend**: Use it to find options quickly
- **Watch the simulation count**: Make sure it's reasonable
- **Auto-save works**: Your progress is saved automatically
- **Ctrl+S to export**: Quick keyboard shortcut

## Need Help?

See `README.md` for full documentation.
