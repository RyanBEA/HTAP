# HOT2000 `.h2k` Parsing Guide

This guide synthesizes the structure observed in the `arch/` archetype library and provides reliable heuristics for machine parsing of HOT2000 `.h2k` files. Treat every file as XML with dynamic collections; never assume fixed ordering or counts.

## 1. Source Set Overview
- All `.h2k` assets under `arch/` share the same root contract but target different archetypes:
  - `227NN0152*.h2k`: 10 Halifax single-detached audit files using Imperial units and F280 weather region `HALIFAX INTL`.
  - `BC-Step-*.h2k`: BC Step Code prototypes (SFD, row, quad, MURB, NZEH variants). Most use Vancouver weather; some retain Imperial units for legacy step benchmarking.
  - `NRCan-*.h2k`: NRCan archetypes (A1–A11 series) in Metric units with Ottawa or Shearwater weather files.
- Two `.docx` stubs (`test_basement.docx`, `test_slab.docx`) sit alongside the archetypes but are not HOT2000 inputs.

## 2. Root Layout
```
HouseFile (attributes: xml:lang, uiUnits)
├─ Version
├─ HOT2000 (application metadata)
├─ ProgramInformation
├─ House
├─ Codes
├─ FuelCosts
└─ AllResults
```
- `uiUnits` toggles Imperial vs Metric numerics; always read it before interpreting areas, lengths, or rates.
- Node order is stable in the current library but should not be hard-coded.

## 3. ProgramInformation Fragment
- **Weather**: attributes `depthOfFrost`, `heatingDegreeDay`, `library`, and nested `Region`/`Location` tags.
- **File**: free-form identifiers (`Identification`, `EnrollmentId`, etc.). Names differ across archetype families.
- **Justifications**: multiple toggles (e.g., `<Walls selected="false" />`). Treat as optional flags.
- **Other metadata**: occupancy, billing, and previous file references are variably populated.

## 4. House Fragment
`House` is the main dynamic payload. Common children:

1. `Labels`
2. `Specifications` (attributes like `effectiveMassFraction`, `aboveGradeHeatedFloorArea`, `belowGradeHeatedFloorArea`; nested descriptors such as `HouseType`, `PlanShape`, `Storeys`, `ConstructionType`).
3. `WindowTightness`, `Temperatures`, `BaseLoads`, `Generation`, `NaturalAirInfiltration`, `Ventilation`: each holds calibration data and may appear empty or partially populated.
4. `HeatingCooling`: the HVAC model.
5. `Components`: envelope and service components.

### 4.1 HeatingCooling
- Encapsulates one or more system groupings (`Type1`, `Type2`, etc.). `Type1` often houses the primary space-heating plant (e.g., `<Furnace>`, `<HeatPump>`, `<HeatingSystem>`).
- Each equipment block exposes:
  - `<Equipment>` with `<EnergySource>` and `<EquipmentType>`.
  - `<Specifications>` including sizing/efficiency fields.
- Auxiliary modules (fans, pumps, cooling) may be empty or absent in all-electric archetypes.
- When iterating, enumerate `HeatingCooling.ChildNodes` and inspect descendant names rather than assuming `Type1` exists.

### 4.2 Components Container
`Components` is highly dynamic; each child is a component instance with its own nested payload. Common patterns observed:

| Component | Typical nested nodes | Notes on relationships |
|-----------|----------------------|------------------------|
| `Ceiling` | `Label`, `Construction`, `Measurements` | Attributes like `id`; may appear multiple times (hip roof + flat). |
| `Wall` | `Label`, `Construction`, `Measurements`, `FacingDirection`, nested `Components` | Nested `Components` contain `Door`, `Window`, `KneeWall`, etc. Windows inherit orientation from parent wall. |
| `Floor` | `Label`, `Construction`, `Measurements`, `Type` | Used for exposed floors or floors over unconditioned space. |
| `Basement` | `Label`, `Configuration`, `OpeningUpstairs`, `RoomType`, `<Floor>`, `<Wall>`, nested `Components` | Nested components include basement doors/windows and `FloorHeader`. Some basements report `isExposedSurface`. |
| `Crawlspace` | Similar to `Basement`, minus slab elements. |
| `HotWater` | `Label`, nested `System`/`Tank`/`Distribution` details. |

#### Nested Attachments
- `Wall.Components` → `Door`, `Window` (attributes: `id`, `number`, `er`, `shgc`, etc.).
- `Basement.Components` → `Door`, `Window`, `FloorHeader`.
- `Ceiling.Components` → `Window` (for skylights and roof hatches).
- Each nested element carries its own `Label`, `Construction` (with `Type` referencing a code), `Measurements`, and optional `Shading` / `FacingDirection`.

#### Skylights and Horizontal Glazing
Skylights are represented as `Window` elements with horizontal tilt nested within `Ceiling.Components`:

- **Location:** `House/Components/Ceiling/Components/Window`
- **Distinguishing feature:** `<Tilt code="2" value="0">` (horizontal) vs regular windows `<Tilt code="1" value="90">` (vertical)
- **Structure:** Identical to vertical windows with same attributes (`er`, `shgc`, `frameHeight`, `frameAreaFraction`, etc.)
- **Parent context:** Must be parsed within ceiling context; `FacingDirection` still applies for solar geometry

**Detection strategy:**
1. Iterate all `Ceiling` nodes in `House/Components`
2. Check for nested `Components/Window` children
3. Inspect `Measurements/Tilt/@code` and `@value` to confirm horizontal orientation (code="2", value="0")

**Example XPath:** `/HouseFile/House/Components/Ceiling/Components/Window[Measurements/Tilt[@code='2']]`

**Observed in:** BC Step Code quad prototypes (BC-Step-Quad-BCH.h2k, BC-Step-Quad-BCH-v118.h2k, BC-Step-Quad-mkt.h2k, BC-Step-rev-Quad.h2k). Most archetypes in the library do not include skylights; do not assume presence.

**Tilt code enumeration:**
- `code="1"` `value="90"` — Vertical (standard walls)
- `code="2"` `value="0"` — Horizontal (skylights, roof hatches)
- Other tilt values (sloped glazing) not observed in current archetype library

#### Doors and Opaque Openings
Doors are `Door` elements nested within `Wall.Components` or `Basement.Components`, representing opaque or partially-glazed openings in the building envelope.

**Basic door structure:**
```xml
<Door rValue="1.14" adjacentEnclosedSpace="false" id="2">
    <Label>Door - 1</Label>
    <Construction energyStar="false">
        <Type code="5" value="1.14">
            <English>Steel Medium density spray foam core</English>
            <French>Acier / âme en mousse à vaporiser de densité moyenne</French>
        </Type>
    </Construction>
    <Measurements height="2.1" width="0.91" />
</Door>
```

**Key attributes and elements:**

- **`@rValue`**: Thermal resistance in RSI units (m²·K/W); higher values indicate better insulation
- **`@adjacentEnclosedSpace`**: Boolean flag indicating if door opens to unconditioned space (garage, porch) vs exterior
- **`@id`**: Unique component identifier referenced in results sections
- **`Label`**: Human-readable descriptor
- **`Construction/Type/@code`**: Door type enumeration (observed codes: 5=steel foam core, 8=user specified)
- **`Construction/Type/@value`**: Nominal R-value matching component `@rValue`
- **`Construction/@energyStar`**: Boolean certification flag
- **`Measurements/@height`** and **`@width`**: Physical dimensions in meters (Metric) or feet (Imperial)

**Doors with glazing inserts:**
Some doors contain nested `Window` components representing glass inserts or sidelights:

```xml
<Door rValue="0.5547" adjacentEnclosedSpace="false" id="3">
    <Label>Basement</Label>
    <Construction energyStar="true">
        <Type code="8" value="0.5547">
            <English>User specified</English>
            <French>Spécifié par l'utilisateur</French>
        </Type>
    </Construction>
    <Measurements height="2.032" width="0.9144" />
    <Components>
        <Window number="2" er="-50.3589" shgc="0.1967" ...>
            <Label>Inset</Label>
            <!-- Standard window structure -->
        </Window>
    </Components>
</Door>
```

When present, nested `Window` components follow identical structure to wall-mounted windows, including glazing performance attributes and tilt specifications.

**Location patterns:**

- **Above-grade exterior doors:** `House/Components/Wall/Components/Door`
- **Garage/adjacent space doors:** `House/Components/Wall/Components/Door[@adjacentEnclosedSpace='true']`
- **Basement doors (rare):** `House/Components/Basement/Components/Door`

**Parsing strategy:**

1. Traverse all `Wall` and `Basement` nodes in `House/Components`
2. Enumerate `Components/Door` children for each surface
3. Extract `@rValue`, `@adjacentEnclosedSpace`, and physical dimensions
4. Resolve `Construction/Type/@code` if needed through `Codes` section
5. Check for nested `Components/Window` to identify glazing inserts
6. Record `@id` for cross-referencing with `AllResults` heat loss and area summaries

**Example XPath queries:**
- All doors: `//House/Components//Door[@rValue]`
- Exterior doors only: `//House/Components//Door[@adjacentEnclosedSpace='false']`
- Doors with glazing: `//House/Components//Door[Components/Window]`

**Coverage:** 39 of 48 files in `arch/` contain door components. All NRCan and BC Step Code archetypes include at least one exterior door; some Halifax audit files (227NN series) may omit doors in certain unit configurations.

**Observed door type codes:**
- `code="5"` — Steel door with medium density spray foam core (R-1.14 typical)
- `code="8"` — User-specified custom door assembly (R-value varies)

**Related elements:**
- `Basement/Configuration/OpeningUpstairs/@code` — Describes doorway between basement and main floor (not a physical door component; affects air flow modeling)
- `AllResults/Results/HeatLoss/Doors` — Monthly aggregated heat loss through all doors (Watts)
- `AllResults/Results/GrossArea/Door` — Total door area and weighted RSI for results summary

### 4.3 ID and Reference Model
- Every major component includes an `id` attribute unique within the file. These IDs are reused in `AllResults` and sometimes in other cross-references.
- Many `<Type>` nodes carry `idref` values (`Code N`) that tie back to entries in `Codes`. Always resolve `idref` through the matching table before consuming U-values, SHGCs, etc.
- Enumerated `code` attributes map to HOT2000 master lists (months, orientations, equipment classes). Treat them as enumerations; the English/French labels are the authoritative strings inside the file.

## 5. Codes Fragment
- Organized by category (`Lintel`, `Window`, `FloorsAbove`, etc.).
- Each category may contain `Default` listings and optional `UserDefined` blocks.
- Every `Code` element exposes:
  - `id` (used by component `idref`)
  - `Label`/`Description`
  - Specialized payload (`WindowLegacy`, `FloorAssembly`, etc.) with thermophysical data.
- Parsing strategy: hydrate dictionaries keyed by `id` at load time; attach resolved data to referencing components.

## 6. FuelCosts Fragment
- Breaks down by fuel type (`Electricity`, `NaturalGas`, …).
- Each `<Fuel>` child contains an `id`, `Label`, `Units`, minimum charges, and up to four `RateBlocks`.
- Billing structures differ across archetypes; treat missing fuels as absent nodes rather than nulls.

## 7. AllResults Fragment
- Sequence of `<Results>` nodes keyed by a `type` attribute (e.g., `AllUpgrades`, `Audit Inputs`, `Reference`).
- Each result houses:
  - `Labels` (English/French description)
  - Aggregations (`Annual`, `Peak`, `Emissions`, etc.) with nested metrics.
  - Optional `Components` section linking performance back to component `id` values.
- `sha256` attributes provide file-integrity hints for HOT2000 but are not required for parsing.

## 8. Parsing Workflow (LLM / MCP Friendly)
1. **Load XML:** Read with an XML-aware parser; preserve attribute order but do not rely on whitespace.
2. **Capture Global Context:** Record `HouseFile.@uiUnits`, `ProgramInformation.Weather`, and file identifiers for metadata outputs.
3. **Build Reference Tables:** Iterate `Codes.*.Code` nodes into dictionaries keyed by `@id`. Also build maps from component `id` to human-readable labels.
4. **Traverse Dynamic Collections:**
   - For each `House.Components` child, emit a component record using its `Name`, `@id`, and `Label`.
   - Recursively inspect nested `Components` blocks (walls, basements) to bind doors/windows to their parent surfaces.
   - When present, pull HVAC equipment out of `HeatingCooling` by scanning child nodes; multiple systems can co-exist.
5. **Resolve Cross-References:** When a node carries `@idref`, attach the corresponding entry from `Codes`. For window/door performance, prefer the resolved values over raw attributes.
6. **Handle Optional Fields:** Many fields appear only in certain archetypes (e.g., `Generation`, `Ventilation.HeatRecovery`). Guard each access with existence checks.
7. **Extract Results:** Iterate `AllResults.Results`; use `@type` to categorize and match back to component IDs when available.
8. **Normalize Units:** Apply `HouseFile.@uiUnits` and the `Units` nodes under `FuelCosts` when exporting numeric data.

## 9. Cardinality Expectations
- Counts vary widely: walls range from 1–6 per file, with anywhere from 0–10 windows nested within.
- Components appear in logical groups but ordering is not enforced (e.g., two `Ceiling` entries can bracket walls).
- Enumerations like `RateBlocks` always define placeholders (up to four blocks) even when zeroed out.

## 10. Practical Extraction Snippets
- Root metadata: `/HouseFile/ProgramInformation/File/Identification`
- Weather file: `/HouseFile/ProgramInformation/Weather/@library`
- Above-grade floor area: `/HouseFile/House/Specifications/@aboveGradeHeatedFloorArea`
- Primary heating fuel label: `/HouseFile/House/HeatingCooling/Type1//EnergySource/English`
- Wall inventory: iterate `/HouseFile/House/Components/Wall`
- Windows on a wall: `./Components/Window` relative to each wall node
- Code lookup example: `/HouseFile/Codes/Window//Code[@id='Code 2']`
- Annual energy use summary: `/HouseFile/AllResults/Results[@type='AllUpgrades']/Annual/Consumption/@total`

## 11. Data Quality Signals from `arch/`
- Metric vs Imperial units correlate with archetype family; conversions may be required when merging data.
- Many French labels contain accented characters (UTF-8). Preserve encoding during parsing.
- Some files (e.g., `227NN01540.h2k`) switch to electric primary heat; do not assume natural gas.
- `BC-Step-*` prototypes may omit certain HVAC subnodes (e.g., no dedicated cooling); treat missing XML as intentional.

## 12. Recommended Validation Steps
- After parsing, cross-check component counts with `AllResults` component breakdowns when available.
- Verify each `idref` resolves to a known code; unresolved references typically indicate library drift.
- Compare extracted fuel tariffs against the requested weather region to ensure correct file selection.

By following the adaptive traversal patterns above, an automated agent (human or LLM) can digest any HOT2000 `.h2k` file in the repository, despite variation in component counts, ordering, or archetype-specific payloads.
