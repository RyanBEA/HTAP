# Manual Testing Guide for Task 1.3

## Quick Start

```bash
cd C:\HTAP\development\htap-config-editor
streamlit run app.py
```

The app will open at http://localhost:8501

---

## Testing Checklist

### 1. Initial Load ✓

**Expected:**
- Page loads with title "🏠 HTAP Configuration Editor"
- 3 columns visible side-by-side
- LEFT: Run Configuration panel
- MIDDLE: Options Browser panel
- RIGHT: Cost Components panel (shows "Select an option" message)
- Footer shows "Configuration: 0 options selected"

**Actions:**
- [ ] Verify wide layout
- [ ] Check all three columns visible
- [ ] Confirm header and footer present

---

### 2. Left Panel - Run Configuration ✓

**Expected:**
- File upload widget at top
- Archetypes multiselect (4 options: AB, BC, ON, QC)
- Location dropdown (4 options: Vancouver, Toronto, Montreal, Calgary)
- Ruleset dropdown (3 options: as_found, NBC-9.36, BC-Step-3)
- "No options selected yet" message
- Reset and Export buttons (Export disabled)

**Actions:**
- [ ] Try uploading test-sample.run file
  - [ ] "File loaded successfully" message appears
  - [ ] "Clear" button appears
- [ ] Select multiple archetypes
- [ ] Select a location
- [ ] Select a ruleset
- [ ] Click Export (should be disabled)

---

### 3. Middle Panel - Options Browser ✓

**Expected:**
- Search box at top
- "Filter by Category" expander with 7 checkboxes
- Results count: "Results (12)"
- 10 option cards displayed
- Pagination controls (if >10 results)

**Actions:**
- [ ] Type "window" in search
  - [ ] Results filter to 2 options
  - [ ] Count updates
- [ ] Clear search
- [ ] Check "Opt-Windows" category
  - [ ] Results filter to 2 window options
- [ ] Uncheck all categories
- [ ] Click on an option card (→ button)
  - [ ] Right panel updates

---

### 4. Right Panel - Cost Components ✓

**Expected (after selecting "DoubleGlazed-Air-LowE"):**
- Option name as header
- Tags displayed: low-e, double-glazed, air-filled
- "Cost Components" section
- 3 expandable component sections
- Cost summary card showing total $65.50 CAD, 3 components
- "Add to Run Configuration" button

**Actions:**
- [ ] Select "DoubleGlazed-Air-LowE" from middle panel
- [ ] Expand first cost component
  - [ ] Verify fields: Unit, Type, Cost, Source, Description
- [ ] Check cost summary matches sum of components
- [ ] Click "Add to Run Configuration"
  - [ ] Success message appears
  - [ ] Balloons animation plays
  - [ ] Left panel "Selected Options" updates

---

### 5. Interaction Flow ✓

**Test Complete Workflow:**

1. **Select first option:**
   - [ ] Click "DoubleGlazed-Air-LowE" in middle panel
   - [ ] Verify details in right panel
   - [ ] Click "Add to Run"
   - [ ] Verify appears in left panel under "Selected Options"
   - [ ] Footer shows "1 options selected"

2. **Select second option:**
   - [ ] Search "ACH" in middle panel
   - [ ] Click "ACH-1.5"
   - [ ] Click "Add to Run"
   - [ ] Verify appears in left panel
   - [ ] Footer shows "2 options selected"

3. **Remove option:**
   - [ ] Click "✕" next to "ACH-1.5" in left panel
   - [ ] Option removed from list
   - [ ] Footer shows "1 options selected"

4. **Reset all:**
   - [ ] Click "Reset" button in left panel
   - [ ] All selections cleared
   - [ ] Right panel shows "Select an option" message
   - [ ] Footer shows "0 options selected"

---

### 6. Pagination ✓

**Expected:**
- When >10 results: Prev/Next buttons appear
- When =10 or fewer: No pagination controls

**Actions:**
- [ ] Ensure all categories unchecked (should show 12 results)
- [ ] Verify "Page 1 of 2" displayed
- [ ] "Prev" button disabled on page 1
- [ ] Click "Next"
  - [ ] Page 2 displays (2 remaining options)
  - [ ] "Next" button disabled on last page
- [ ] Click "Prev"
  - [ ] Returns to page 1

---

### 7. Category Filtering ✓

**Test each category:**

| Category | Expected Count |
|----------|----------------|
| Opt-Windows | 2 |
| Opt-ACH | 2 |
| Opt-AboveGradeWall | 2 |
| Opt-AtticCeilings | 2 |
| Opt-Heating-Cooling | 2 |
| Opt-VentSystem | 2 |
| All unchecked | 12 |

**Actions:**
- [ ] Check only "Opt-Windows"
  - [ ] Verify 2 results
- [ ] Check "Opt-ACH" also
  - [ ] Verify 4 results (2+2)
- [ ] Uncheck all
  - [ ] Verify 12 results

---

### 8. Search Functionality ✓

**Test search queries:**

| Query | Expected Results |
|-------|------------------|
| "window" | 2 (both window options) |
| "argon" | 1 (TripleGlazed-Argon-LowE) |
| "r-" | 4 (R-20-Wall, R-30-Wall, R-50-Attic, R-60-Attic) |
| "heat-pump" | 1 (ASHP-CCASHP) |
| "ventilation" | 2 (HRV, ERV) |

**Actions:**
- [ ] Test each search query
- [ ] Verify correct filtering
- [ ] Verify search is case-insensitive
- [ ] Clear search returns all results

---

### 9. Export Button State ✓

**Expected:**
- Disabled when no options selected
- Enabled when ≥1 option selected
- Tooltip changes based on state

**Actions:**
- [ ] With 0 options: Verify disabled, tooltip "Add options first"
- [ ] Add 1 option: Verify enabled, tooltip "Export .run file"
- [ ] Click Export (currently just sets session state flag)

---

### 10. Help Dialog ✓

**Expected:**
- Help button (ℹ️) in footer
- Clicking opens expander with instructions
- Instructions describe all three panels

**Actions:**
- [ ] Click "ℹ️ Help" in footer
- [ ] Verify help content displays
- [ ] Verify instructions clear and helpful
- [ ] Click to collapse

---

### 11. Visual Styling ✓

**Check styling elements:**

**Colors:**
- [ ] Blue badges/accents for info
- [ ] Status badges have correct colors

**Icons/Emojis:**
- [ ] 🏠 in title
- [ ] ⚙️ Run Configuration
- [ ] 🔍 Options Browser
- [ ] 💰 Cost Components
- [ ] 📁 Import
- [ ] 🔄 Reset
- [ ] 📦 Export
- [ ] ℹ️ Help

**Layout:**
- [ ] Proper spacing between sections
- [ ] Divider lines (---) render correctly
- [ ] Cards have clear boundaries
- [ ] Buttons full width
- [ ] Text readable and well-formatted

---

### 12. Cost Component Details ✓

**Test different options with varying cost structures:**

1. **DoubleGlazed-Air-LowE (3 components):**
   - [ ] Material: $45.50
   - [ ] Labour: $15.00
   - [ ] Removal: $5.00
   - [ ] Total: $65.50

2. **ASHP-CCASHP (5 components):**
   - [ ] Equipment: $8,500
   - [ ] Labour: $2,500
   - [ ] Electrical: $1,200
   - [ ] Material: $800
   - [ ] Equipment: $350
   - [ ] Total: $13,350

3. **ACH-1.5 (2 components):**
   - [ ] Labour: $2.50/sqft
   - [ ] Material: $1.25/sqft
   - [ ] Total: $3.75/sqft

**Actions:**
- [ ] Select each option
- [ ] Expand all component expanders
- [ ] Verify all fields populated
- [ ] Check totals calculate correctly

---

## Error Scenarios

### 1. No Option Selected
- [ ] Right panel shows info message
- [ ] No errors in console

### 2. Empty Search
- [ ] All results displayed
- [ ] No "No results" message

### 3. No Category Selected
- [ ] All results displayed
- [ ] Same as unchecking all

### 4. Search with No Matches
- [ ] Type "xyz123nonexistent"
- [ ] "No options found" message displays
- [ ] Helpful text to adjust filters

---

## Performance Checks

- [ ] Initial load time < 2 seconds
- [ ] Search response immediate
- [ ] Category filter response immediate
- [ ] Pagination instant
- [ ] Option selection instant
- [ ] No lag when adding options

---

## Browser Compatibility

Test in:
- [ ] Chrome
- [ ] Firefox
- [ ] Edge
- [ ] Safari (if available)

---

## Responsive Layout

Test at different widths:
- [ ] 1920x1080 (Full HD)
- [ ] 1366x768 (Laptop)
- [ ] Minimum width (how does it handle narrow screens?)

**Note:** Streamlit wide layout optimized for ≥1024px width

---

## Console Checks

Open browser developer console (F12):

- [ ] No JavaScript errors
- [ ] No 404 errors
- [ ] No warnings (except Streamlit's normal warnings)
- [ ] Network requests complete successfully

---

## Session Persistence

- [ ] Add several options
- [ ] Refresh page (Streamlit reruns)
- [ ] **Expected:** State resets (no persistence yet)
- [ ] Verify app reloads cleanly

---

## Final Verification

After completing all tests:

- [ ] All major features work
- [ ] No blocking bugs found
- [ ] UI is intuitive and easy to use
- [ ] Performance is acceptable
- [ ] Ready for integration with data models

---

## Known Issues/Limitations

Document any issues found:

1. **Export button**: Only sets state flag, doesn't generate file yet
   - Expected behavior: Will be implemented in Task 1.6

2. **File upload**: Accepts file but doesn't parse yet
   - Expected behavior: Will be implemented in Task 1.4

3. **Placeholder data**: All data is hardcoded
   - Expected behavior: Will integrate with Task 1.2 data models

---

## Success Criteria

Task 1.3 testing complete when:
- ✅ All acceptance criteria met
- ✅ No blocking bugs
- ✅ UI is visually correct
- ✅ All interactions work as expected
- ✅ Ready for data model integration

---

## Next Steps After Testing

1. Document any bugs found
2. Create GitHub issues for improvements
3. Proceed to Task 1.4: Run File Parser
4. Begin integration with Task 1.2 data models

---

**Testing Date:** ________
**Tester:** ________
**Browser/OS:** ________
**Issues Found:** ________

---

**END OF MANUAL TESTING GUIDE**
