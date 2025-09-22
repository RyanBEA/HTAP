# H2KUtils.rb

## Purpose & Scope
- `inc/H2KUtils.rb` hosts the low-level HOT2000 utilities used across HTAP to mutate `.h2k` XML, interrogate simulation results, and prepare the HOT2000 CLI runtime.
- The file is organised as a set of Ruby modules that divide responsibilities: converting HTAP choices into HOT2000 structures, extracting geometry/system metadata, managing code libraries, parsing text reports, and maintaining the `H2K` working folder.
- These helpers are heavily relied on by `substitute-h2k.rb`, `htap-prm.rb`, and costing/hourly modules. Many functions assume the global logging helpers (`debug_out`, `warn_out`, `fatalerror`) from `inc/msgs.rb` are available.

## Module Overview
- **`HTAP2H2K`** – Domain logic that translates HTAP foundation choices into HOT2000 basement/crawlspace/slab elements.
- **`H2KFile`** – The workhorse for reading, writing, and interrogating `.h2k` XML. Provides geometry calculations, system summaries, weather metadata, and routines to add/remove envelope components.
- **`H2KLibs`** – Helpers to manage HOT2000 code-library entries (e.g., dynamically create/update window codes when a particular glazing package is not already present).
- **`H2KUtils`** – Runtime preparation utilities that adjust the staged HOT2000 CLI payload (INI rewriting, “magic” log files).
- **`H2KOutput`** – Parsers that convert HOT2000 outputs (`Browse.rpt` and `HouseFile/AllResults`) into structured hashes consumed by HTAP result aggregation.
- **Top-level helpers** – Functions such as `checksum(dir)` that operate outside a module but are imported throughout the stack.

## HTAP2H2K: Foundation Configuration
- `conf_foundations(myFdnData, myOptions, h2kElements)` is the key entry point. It:
  - Cross-references HTAP option metadata (`myOptions`) with the current choice bundle (`myFdnData`).
  - Determines whether insulation exists on exterior walls, interior walls, below-grade slabs, or on-grade slabs, then selects the appropriate HOT2000 configuration codes (`BCEN_2`, `SCB_25`, etc.).
  - Calls into `H2KFile.updBsmCrawlDef` and `H2KFile.updSlabDef` with calculated R-values so the `.h2k` XML reflects the requested assembly.
- Expectation: the caller supplies the raw choice names (sometimes “NA”). Anything unsupported triggers `fatalerror` to abort the run, making it safer to wire from `substitute-h2k.rb`.

## H2KFile: XML Accessors & Mutators
### File & XML handles
- `get_elements_from_filename(fileSpec)` loads `.h2k`, `.flc`, or `.cod` XML with REXML, storing the parsed document in global variables (`$XMLdoc`, `$XMLFueldoc`, …). Subsequent functions expect these globals to remain valid for the lifetime of the run.
- `createProgramXMLSection(elements)` can inject a missing `ProgramInformation` node when working from bare archetypes.

### Project metadata
- `getYearBuilt`, `getEvalDate`, `getBuilderName`, `getHouseType`, `getBuildingType`, `getMURBUnits`, `getStoreys`, and `getFrontOrientation` read key fields from `HouseFile/House/Specifications` and return scrubbed strings/numbers ready for CSV/JSON export.
- `getWeatherCity`, `getRegion`, and `getAddress` pull the weather and location metadata used by reporting and costing logic.

### Geometry & envelope calculations
- `getHeatedFloorArea` normalises the HOT2000 version differences (pre/post v11.58) and returns the aggregate heated area.
- `GetHouseVolume`, `getWindowArea`, `getCeilingArea`, `getAGWallDimensions`, `getFlrHeaderDimensions`, `getExpFloorDimensions`, and `getBGDimensions` compute surface areas and volumes, including orientation splits and header allowances.
- `getAllInfo(elements)` orchestrates the preceding calls, returning a nested hash keyed by `locale`, `dimensions`, `house-description`, etc. This is the main geometry payload used by costing and reporting.

### System introspection
- `getPrimaryHeatSys`, `getSecondaryHeatSys`, and `getPrimaryDHWSys` map the installed systems to their fuel types.
- `getSystemInfo(elements)` aggregates counts and capacities (kW or l/s) for space-conditioning and ventilation equipment, and appends design loads via `getDesignLoads`.

### Foundation & slab writers
- `updBsmCrawlDef` and `updSlabDef` rewrite the basement/crawlspace/slab sections using the data prepared by `HTAP2H2K`. They manage R-values, insulation nodes, and construction flags to keep HOT2000 happy.

### Window manipulation
- `deleteAllWin`, `addWin`, and `add_win_to_any_wall` provide programmatic control over fenestration when options swap out glazing packages. The helpers respect unit spacing (mm to m) and ensure orientation tags are updated consistently.

## H2KLibs: Code Library Helpers
- `AddWinToCodeLib(name, char, codeElements)` clones or creates user-defined window code entries on the fly when HTAP needs a glazing spec not already in the HOT2000 template.
- `getNextCodeIndex` finds the next available library ID (`Code ###`), and `findCodeInLib` searches both Favourite and UserDefined trees. These functions are typically called before adding windows through `H2KFile.addWin`.

## H2KUtils: Working-Dir Maintenance
- `write_h2k_magic_files(path)` ensures `WINMB.H2k` and `ROutstr.H2k` exist in the staged `H2K` folder so HOT2000 CLI diagnostics and log streaming work. The file contents come from `inc/h2kConfigFiles.rb`.
- `fix_H2K_INI(path)` rewrites `HOT2000.ini`, replacing placeholder tokens with the actual `H2K` working directory. `substitute-h2k.rb` calls this after copying the CLI payload so every parallel run points at the correct local assets.

## H2KOutput: Result Parsing
- `parse_BrowseRpt(path)` ingests the textual `Browse.rpt`, extracting monthly/annual data sets for heating loads, cooling loads, device energy consumption, weather statistics, DHW summaries, setpoints, and baseloads. The result is a nested hash keyed by `monthly`, `daily`, and `annual` sections that downstream analytics can consume.
- `parse_results(result_code, elements)` walks `HouseFile/AllResults` and returns a rich hash of energy, heat-loss, cost, and ventilation metrics for the requested house code (`SOC`, `Reference`, `General`, etc.). When `$ExtraOutput1` is true it captures detailed envelope heat-loss breakdowns and DHW load information as well.
- Both parsers rely on constants such as `MonthArrListAbbr` and `monthLong` defined in `inc/constants.rb`, and they honour global flags like `$ExtraOutput1` and `$PVIntModel` set by `substitute-h2k.rb`.

## Ancillary Helpers & Patterns
- `checksum(dir)` (defined at top level) calculates an MD5 signature for the HOT2000 installation directory while ignoring volatile files (`Browse.rpt`, `ROutStr.txt`, etc.). `substitute-h2k.rb` uses this to verify the copy in `HTAP-work-*` matches the master CLI install.
- Many functions leverage a shared lambda `$blk = lambda { |h,k| ... }` declared in `substitute-h2k.rb` for auto-vivifying nested hashes. When calling `H2KOutput.parse_results` directly, initialise `$blk` first to avoid `NameError`.
- Logging is central: `debug_out`, `stream_out`, `warn_out`, and `fatalerror` are assumed to exist in the caller’s scope. Wrap calls in try/catch only if you want to override the default fatal behaviour.

## Interaction Notes
- `substitute-h2k.rb` is the primary consumer: it uses `H2KUtils` to prep the run folder, `H2KFile` to read and modify the `.h2k` structure, `HTAP2H2K` to apply bundled foundation options, `H2KLibs` when custom window codes are needed, and `H2KOutput` to build the JSON result payload.
- `htap-prm.rb` leans on `H2KUtils.write_h2k_magic_files`/`fix_H2K_INI` while staging directories, and `H2KOutput.parse_results` when collecting simulation metrics for CSV/JSON aggregation.
- Costing modules call `H2KFile.getAllInfo` to determine dimensions, while hourly extrapolation plugs into the Browse report data built by `H2KOutput.parse_BrowseRpt`.

## Practical Tips
- Always pass the full REXML element tree returned by `get_elements_from_filename`; functions expect to traverse from the root (`HouseFile/…`).
- Before manipulating code libraries or foundation nodes, ensure the HOT2000 template actually includes those sections. When in doubt, call `createProgramXMLSection` to scaffold missing program information.
- Because the utilities modify in-memory REXML trees directly, remember to write the document back to disk yourself (`File.open(...); $XMLdoc.write`). `substitute-h2k.rb` handles this, but bespoke scripts must do so explicitly.
- When extending `H2KOutput.parse_results`, guard new attributes with checks: HOT2000 versions differ in element names, and absent nodes will raise if dereferenced blindly.
- The browse parser assumes English-language reports. If HOT2000 locale settings change, adjust the regex patterns or split logic accordingly.
