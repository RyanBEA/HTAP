# Pony Wall Support Implementation Plan for HTAP

## Executive Summary

Add automated pony wall insulation control to HTAP's Opt-H2KFoundation system. Currently affects 60% of archetypes (24/40) with pony walls representing ~43% of basement wall area on average.

## Implementation Overview

### Core Approach
- Extend existing Opt-H2KFoundation options with pony wall parameters
- Modify processing logic to detect and update PonyWallType XML elements
- Use graceful degradation for basements without pony walls
- Maintain backward compatibility with existing .choices files

---

## Phase 1: Core Implementation (Week 1)

### 1.1 Update HTAP-options.json

**File:** `C:\HTAP\HTAP-options.json`

Add pony wall parameter to existing foundation options:

```json
"NBC_936_2.98RSI": {
  "h2kMap": {
    "base": {
      "OPT-H2K-ConfigType": "BCIN_1_ALL",
      "OPT-H2K-IntWall-RValue": "16.93",
      "OPT-H2K-PonyWall-RValue": "16.93",  // NEW PARAMETER
      "OPT-H2K-ExtWall-RVal": "NA",
      "OPT-H2K-BelowSlab-RVal": "NA"
    }
  }
}
```

**Target Options to Modify:**
- All NBC_936_* options
- All NBC_BCIN_zone* options
- LEEP_Base_Case_FDN variants
- Any option with OPT-H2K-IntWall-RValue specified

**Schema Registration:**
```json
"h2kSchema": [
  "OPT-H2K-ConfigType",
  "OPT-H2K-IntWallCode",
  "OPT-H2K-IntWall-RValue",
  "OPT-H2K-ExtWall-RVal",
  "OPT-H2K-BelowSlab-RVal",
  "OPT-H2K-PonyWall-RValue"  // ADD TO SCHEMA
]
```

### 1.2 Process Pony Walls in substitute-h2k.rb

**File:** `C:\HTAP\substitute-h2k.rb`

**Location:** After line 1696 (end of BelowSlab-RVal processing)

```ruby
# =========================================================================
# Process pony wall insulation for basements with above-grade portions
# =========================================================================
elsif ( tag =~ /OPT-H2K-PonyWall-RValue/ && value != "NA" )

  # Determine which foundations to modify based on fndTypes
  locHouseStr = []

  if ( fndTypes == "B" )
    locHouseStr[0] = "HouseFile/House/Components/Basement"
  elsif ( fndTypes == "W" )
    # Legacy "W" type - treat as basement with pony walls
    warn_out("WARNING: fndTypes 'W' is deprecated. Treating as 'B' for pony walls.\n")
    locHouseStr[0] = "HouseFile/House/Components/Basement"
  elsif ( fndTypes == "ALL" )
    # When ALL specified with B-type config, apply to all basements
    if ( configType =~ /^B/ )
      locHouseStr[0] = "HouseFile/House/Components/Basement"
    end
  end

  # Process each basement
  locHouseStr.each do |locationString|
    if ( locationString != "" )
      h2kElements.each(locationString) do |basement|

        # Check if this basement has pony walls
        wall = basement.elements["Wall"]
        if wall && wall.attributes["hasPonyWall"] == "true"

          # Find the PonyWallType element
          ponyWallNode = wall.elements["Construction/PonyWallType"]

          if ponyWallNode
            # Calculate RSI from R-value
            ponyWallRsi = (value.to_f / R_PER_RSI).round(4)

            # Remove code library reference if present
            if ponyWallNode.attributes["idref"]
              ponyWallNode.attributes.delete("idref")
            end

            # Update nominal insulation
            ponyWallNode.attributes["nominalInsulation"] = ponyWallRsi.to_s

            # Update or create Description
            if ponyWallNode.elements["Description"]
              ponyWallNode.elements["Description"].text = "User specified"
            else
              ponyWallNode.add_element("Description")
              ponyWallNode.elements["Description"].text = "User specified"
            end

            # Clear existing Composite/Section
            if ponyWallNode.elements["Composite"]
              ponyWallNode.elements["Composite"].elements.delete_all("Section")
            else
              ponyWallNode.add_element("Composite")
            end

            # Add new Section with updated values
            composite = ponyWallNode.elements["Composite"]
            composite.add_element("Section")
            section = composite.elements["Section"]
            section.attributes["nominalRsi"] = ponyWallRsi.to_s
            section.attributes["rsi"] = ponyWallRsi.to_s
            section.attributes["percentage"] = "100"
            section.attributes["rank"] = "1"

            debug_out("Updated pony wall insulation to R-#{value} (RSI #{ponyWallRsi})\n")

          else
            warn_out("WARNING: Basement has hasPonyWall='true' but no PonyWallType element found\n")
          end

        else
          # Graceful degradation - pony wall value specified but no pony walls present
          debug_out("INFO: Pony wall R-value specified but basement has no pony walls - skipping\n")
        end

      end # each basement
    end
  end # each locationString

end # elsif OPT-H2K-PonyWall-RValue
```

### 1.3 Add Missing XML Section Handler

**File:** `C:\HTAP\substitute-h2k.rb`

**Location:** After line 4078 (existing addMissingExteriorAddedInsulation function)

```ruby
# =========================================================================================
#  Add missing "PonyWallType" section to Wall Construction if hasPonyWall="true"
# =========================================================================================
def addMissingPonyWallType(theElement)
  # theElement is the Configuration element
  # The Wall element is always four elements from the Configuration element
  theWallElement = theElement.next_element.next_element.next_element.next_element

  if theWallElement && theWallElement.attributes["hasPonyWall"] == "true"
    theWallConstElement = theWallElement[1]

    # Check if PonyWallType already exists
    if theWallConstElement.elements["PonyWallType"].nil?
      # Create PonyWallType with default insulation
      thePonyWallElement = theWallConstElement.add_element("PonyWallType",
        {"nominalInsulation" => "2.11"})
      thePonyWallElement.add_element("Description").text = "Default pony wall"

      theCompositeElement = thePonyWallElement.add_element("Composite")
      theCompositeElement.add_element("Section", {
        "rank" => "1",
        "percentage" => "100",
        "rsi" => "2.11",
        "nominalRsi" => "2.11"
      })

      warn_out("WARNING: Added missing PonyWallType element to basement with hasPonyWall='true'\n")
    end
  end
end
```

**Also modify the configuration type checking (lines 1481-1492):**

```ruby
# Check if PonyWallType section needs to be added
if wall && wall.attributes["hasPonyWall"] == "true"
  if wall.elements["Construction/PonyWallType"].nil?
    addMissingPonyWallType(element)
  end
end
```

---

## Phase 2: Surface-by-Surface Mode Support (Week 2)

### 2.1 Extend H2KUtils.rb

**File:** `C:\HTAP\inc\H2KUtils.rb`

**Location 1:** In conf_foundations function (around line 56)

```ruby
# Check if pony wall insulation is specified
bPonyWallInsul = false
rEff_PonyWall = "NA"

if myFdnData.key?("FoundationWallIntIns") && myFdnData["FoundationWallIntIns"] != "NA"
  # Check if option includes pony wall specification
  if myOptions["Opt-FoundationWallIntIns"]["options"][myFdnData["FoundationWallIntIns"]].key?("values")
    ponyWallData = myOptions["Opt-FoundationWallIntIns"]["options"][myFdnData["FoundationWallIntIns"]]["values"]["1"]["conditions"]["all"]

    # Look for H2K-Fdn-PonyWallReff parameter
    if ponyWallData.key?("H2K-Fdn-PonyWallReff") && ponyWallData["H2K-Fdn-PonyWallReff"] != "NA"
      bPonyWallInsul = true
      rEff_PonyWall = ponyWallData["H2K-Fdn-PonyWallReff"].to_f
    elsif bIntWallInsul
      # Default: pony walls match interior walls if not specified
      bPonyWallInsul = true
      rEff_PonyWall = rEff_IntWall
    end
  end
end
```

**Location 2:** After line 153 (add to h2kFdnData hash)

```ruby
h2kFdnData["?PonyWallIns"] = bPonyWallInsul
h2kFdnData["rEffPonyWall"] = rEff_PonyWall
```

**Location 3:** After line 355 (process pony walls)

```ruby
# =========================================================================
# Process pony wall insulation if present and specified
# =========================================================================
if node.name == "Basement" && fdnData["?PonyWallIns"]

  wall_element = node.elements[".//Wall"]

  if wall_element && wall_element.attributes["hasPonyWall"] == "true"

    loc = ".//Wall/Construction/PonyWallType"
    ponyWallNode = node.elements[loc]

    if ponyWallNode
      debug_out "Updating pony wall insulation\n"

      # Calculate RSI value
      ponyWallRsi = (fdnData["rEffPonyWall"].to_f / R_PER_RSI).round(4)

      # Update nominal insulation
      ponyWallNode.attributes["nominalInsulation"] = ponyWallRsi.to_s

      # Remove code reference if present
      if ponyWallNode.attributes["idref"]
        ponyWallNode.attributes.delete("idref")
      end

      # Update Description
      if ponyWallNode.elements["Description"]
        ponyWallNode.elements["Description"].text = "User specified"
      else
        ponyWallNode.add_element("Description").text = "User specified"
      end

      # Clear and rebuild Composite/Section
      ponyWallNode.elements.delete("Composite")
      ponyWallNode.add_element("Composite")
      composite = ponyWallNode.elements["Composite"]
      composite.add_element("Section")

      section = composite.elements["Section"]
      section.attributes["nominalRsi"] = ponyWallRsi.to_s
      section.attributes["rsi"] = ponyWallRsi.to_s
      section.attributes["percentage"] = "100"
      section.attributes["rank"] = "1"

      debug_out "Pony wall RSI set to: #{ponyWallRsi} (R-#{fdnData["rEffPonyWall"]})\n"

    else
      warn_out "WARNING: Basement has hasPonyWall='true' but no PonyWallType element\n"
    end

  elsif wall_element && wall_element.attributes["hasPonyWall"] == "false" && fdnData["?PonyWallIns"]
    debug_out "INFO: Pony wall insulation specified but basement has hasPonyWall='false' - skipping\n"

  elsif !wall_element
    warn_out "WARNING: Basement has no Wall element - cannot process pony walls\n"
  end

end
```

---

## Phase 3: Testing & Validation (Week 3)

### 3.1 Create Test Cases

**Directory:** `C:\HTAP\testing\pony-wall-tests\`

**Test 1: Basic Pony Wall Application**
```json
// test1-basic.choices
{
  "Opt-H2KFoundation": "NBC_936_2.98RSI"
}
```

**Test 2: No Pony Walls Present (Graceful Degradation)**
```json
// test2-no-pony-walls.choices
{
  "Opt-H2KFoundation": "NBC_936_2.98RSI",
  "Opt-Archetype": "slab-on-grade"  // Has no pony walls
}
```

**Test 3: Surface-by-Surface Mode**
```json
// test3-surface-mode.choices
{
  "Opt-FoundationWallIntIns": "NBC_936_2.98RSI"
}
```

### 3.2 Validation Script

**File:** `C:\HTAP\testing\validate-pony-walls.rb`

```ruby
#!/usr/bin/env ruby

require 'rexml/document'
include REXML

# Test archetype with known pony walls
test_file = "arch/227NN01521.h2k"
output_dir = "HTAP-sim-test"
choices_file = "testing/pony-wall-tests/test1-basic.choices"

# Run substitute-h2k
system("ruby substitute-h2k.rb --file #{test_file} --choices #{choices_file} --options HTAP-options.json")

# Parse output file
output_h2k = "#{output_dir}/run_file_file_1.h2k"
doc = Document.new(File.open(output_h2k))

# Extract pony wall values
pony_wall_element = doc.elements["//Basement/Wall/Construction/PonyWallType"]

if pony_wall_element
  nominal_insulation = pony_wall_element.attributes["nominalInsulation"].to_f
  expected_rsi = (16.93 / 5.678).round(4)  # R-16.93 converted to RSI

  if (nominal_insulation - expected_rsi).abs < 0.01
    puts "✓ PASS: Pony wall insulation correctly set to RSI #{nominal_insulation}"
  else
    puts "✗ FAIL: Expected RSI #{expected_rsi}, got #{nominal_insulation}"
  end
else
  puts "✗ FAIL: PonyWallType element not found"
end

# Check energy results
results = doc.elements["//AllResults/Results/Annual/HeatLoss"]
if results
  pony_wall_loss = results.attributes["ponyWall"].to_f
  puts "Pony wall heat loss: #{pony_wall_loss} GJ/year"
end
```

### 3.3 Regression Testing

**Compare Against Manual Runs:**
```bash
# Run automated version
ruby htap-prm.rb --run-def testing/pony-wall-automated.run --output auto-results.csv

# Compare with manual baseline
perl util/compare_csv.pl manual-baseline.csv auto-results.csv > validation-report.txt

# Key metrics to validate:
# - Pony wall heat loss (should decrease)
# - Total envelope heat loss
# - Annual energy consumption
# - Effective R-values
```

---

## Phase 4: Clean Up & Documentation (Week 4)

### 4.1 Remove Dead Code

**File:** `C:\HTAP\substitute-h2k.rb`

Mark lines 1458-1696 referencing non-existent Walkout elements:
```ruby
# DEPRECATED: Walkout elements don't exist in H2K schema
# Left for reference only - see pony wall handling above
# Original lines 1458-1696 commented out
```

### 4.2 Add Logging

**Enhanced Debug Output:**
```ruby
if $gDebug
  stream_out("\n=== PONY WALL PROCESSING SUMMARY ===\n")
  stream_out("Archetypes processed: #{pony_wall_count}\n")
  stream_out("With pony walls: #{pony_walls_found}\n")
  stream_out("Modified: #{pony_walls_modified}\n")
  stream_out("Average height: #{avg_pony_height}m\n")
  stream_out("=====================================\n")
end
```

### 4.3 Update Documentation

**Files to Update:**
- `HTAP-quick-start.md` - Add pony wall option examples
- `HTAP-options.json` - Document new parameters in comments
- `substitute-h2k.md` - Explain pony wall processing
- `CLAUDE.md` - Note pony wall support availability

---

## Implementation Timeline

| Week | Phase | Deliverables | Validation |
|------|-------|--------------|------------|
| 1 | Core Implementation | Modified substitute-h2k.rb, Updated HTAP-options.json | Basic function tests |
| 2 | Surface Mode | H2KUtils.rb changes, Extended options | Surface-by-surface tests |
| 3 | Testing | Test suite, Validation scripts | Regression against manual |
| 4 | Cleanup | Dead code removal, Documentation | Code review complete |

## Success Metrics

1. **Functional:** Pony wall RSI values correctly updated in output .h2k files
2. **Energy:** Pony wall heat loss changes proportionally to insulation changes
3. **Compatibility:** No errors with existing .choices files
4. **Coverage:** Works with all 24 archetypes having pony walls
5. **Validation:** Results match manual modification baseline within 1%

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing runs | Graceful degradation, extensive backward compatibility testing |
| Invalid XML generation | Validate against HOT2000 CLI before release |
| Incorrect RSI calculations | Unit tests for R-value to RSI conversion |
| Missing PonyWallType elements | Auto-create with defaults if hasPonyWall="true" |
| Performance impact | Profile with large batch runs, optimize if >5% slower |

## Future Enhancements

1. **Climate-zone-aware defaults** - Pony walls match main walls in cold climates
2. **Code library support** - Allow pony walls to reference code libraries
3. **Separate control** - Independent `Opt-PonyWallStrategy` option
4. **Reporting** - Add pony wall metrics to standard output
5. **GUI support** - Visual indicators for pony wall configurations

---

## Notes for Implementation

- R-value to RSI conversion: RSI = R-value ÷ 5.678
- Pony walls typically 25-68% of total basement wall height
- 60% of archetypes affected - high priority feature
- Default behavior: pony walls match interior wall insulation
- Always use graceful degradation for missing elements