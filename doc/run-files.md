# HTAP `.run` Definition Files

## Purpose & Scope
- `.run` files describe scenario batches for `htap-prm.rb`. They declare which archetypes, locations, rulesets, and option permutations the run manager should expand into `.choices` files before spawning `substitute-h2k.rb` workers.
- The parser in `htap-prm.rb` (`parse_def_file`) consumes the file, sanitises whitespace/comments, and populates internal hashes (`$gRunUpgrades`, `$gLocations`, etc.) used when generating mesh/parametric/sample combinations.

## File Layout & Sections
`.run` files are plain text and support `!`-prefixed comments. The content is organised into three sentinel-delimited blocks:
- `RunParameters_START` / `RunParameters_END` – Core configuration for the run manager.
- `RunScope_START` / `RunScope_END` – Lists archetypes, weather locations, and rulesets to iterate.
- `Upgrades_START` / `Upgrades_END` – Enumerates HTAP attributes (`Opt-*`) and the option keys (from `HTAP-options.json`) to include in the study.
Whitespace is ignored and key/value pairs use `key = value` syntax (case-insensitive keys).

## Run Parameters
Supported directives (all optional unless noted):
- `run-mode` – Selects expansion strategy: `mesh`, `parametric`, or `sample{n:###;seed:###}`. See “Expansion Modes” below.
- `archetype-dir` – Folder containing the base `.h2k` files. Wildcards in `RunScope` match against this directory.
- `options-file` – Path to the options catalogue (defaults to `HTAP-options.json` if omitted).
- `substitute-file` – Path to `substitute-h2k.rb` (default `C:/HTAP/substitute-h2k.rb`).
- `unit-costs-db` – Path to `HTAPUnitCosts.json`; enables costing without needing `--compute-costs` on the CLI.
- `rulesets-file` – Path to `HTAP-rulesets.json` for upgrade packages referenced in the `Upgrades` section.
Any additional whitespace is stripped by the parser, so both absolute and relative Windows-style paths work (remember to avoid escaping backslashes).

## Run Scope
Defines which base models and contexts every combination should include:
- `archetypes` – Comma-separated list of `.h2k` filenames or glob patterns (e.g., `*.h2k`). Evaluated against `archetype-dir`.
- `locations` – List of `Opt-Location` keys. Wildcards (`*`) are expanded using the names in `HTAP-options.json` (e.g., `AB-*`).
- `rulesets` – List of rule-bundle names (e.g., `as-found`, `BCStepCode`). These are simply carried through to each generated choice file.
If a value contains `*`, the run manager replaces it with the set of matching options at run time.

## Upgrades Section
Each non-comment line sets one HTAP attribute to one or more option keys. Example:
```
Opt-ACH = ACH_NBC, ACH_8, ACH_6_5
Opt-Windows = NBC-zone4-window
Opt-ResultHouseCode = General
```
### Notes
- Attribute names are case-insensitive; aliases defined in `HTAPData.queryAttribAliases` are resolved automatically.
- Choices must match the keys declared in `HTAP-options.json`. Wildcards are allowed (`Opt-Windows = NBC-zone4-*`).
- `upgrade-package-list = PackageName` triggers ruleset expansion. Those packages must exist in the ruleset JSON provided via `rulesets-file`.
- Values are comma-separated; surrounding whitespace is removed.
- Use `NA` for attributes you want to leave untouched (consistent with `.choices` files).

## Expansion Modes
- **Mesh (default)** – Builds the full Cartesian product of every listed option per attribute, archetype, location, and ruleset.
- **Parametric** – Generates a base case (first option for each attribute) then toggles each additional choice one-at-a-time while holding others at baseline.
- **Sample** – Syntax `sample{n:250;seed:42}`. HTAP creates the mesh then randomly samples `n` combinations (optionally seeded for repeatability).

## Wildcards & Aliases
- `*` tokens in `RunScope` or `Upgrades` are expanded using the available keys from `HTAP-options.json` (or the ruleset file for upgrade packages). This allows patterns such as `archetypes = NBC-*.h2k` or `Opt-ACH = ACH_*`.
- Attribute aliases (e.g., legacy names) are mapped via `HTAPData.queryAttribAliases`, so you can use either the canonical `Opt-FoundationWallExtIns` or known aliases.

## Integration & Execution Flow
1. `htap-prm.rb --run-def path/to/file.run` parses the file and populates `$gRunUpgrades`, `$gLocations`, `$gRulesets`, etc.
2. Run mode determines how `create_mesh_cartisian_combos` or `create_parametric_combos` produces the list of synthetic `.choices` files (kept in memory by default).
3. For each generated combination, `htap-prm` pairs the choices with their archetype, location, and ruleset, then spawns `substitute-h2k.rb` using those inputs.
4. Resume support (`--resume`) hinges on the combination names derived from these sections; altering the `.run` structure mid-resume can create mismatches.

## Authoring Tips
- Start from `doc/examples/example.run` for a template.
- Keep comments (`! ...`) for documentation; they are stripped automatically.
- Maintain consistent casing with `HTAP-options.json` to avoid validation warnings.
- When introducing new attributes, ensure `HTAP-options.json` already defines their options and costing metadata.
- Use absolute paths for shared network environments; relative paths are resolved from the repository root where `htap-prm` is executed.
- After edits, perform a dry run (`ruby htap-prm.rb --run-def yourfile.run --confirm`) to review estimated combination counts before launching a long batch.

## Example Skeleton
```text
! Definitions file for HTAP-PRM RUN
RunParameters_START
  run-mode      = mesh
  archetype-dir = C:/HTAP/testing/h2k-files
  options-file  = C:/HTAP/HTAP-options.json
  unit-costs-db = C:/HTAP/HTAPUnitCosts.json
RunParameters_END

RunScope_START
  archetypes = NRCan-arch4_2100sf_2storey_fullBsmt.h2k
  locations  = AB-Calgary, AB-* 
  rulesets   = as-found, BCStepCode
RunScope_END

Upgrades_START
  Opt-ACH             = ACH_NBC, ACH_3.0
  Opt-Windows         = NBC-zone4-window
  Opt-Heating-Cooling = NA
  upgrade-package-list = StepCode-Tier3
Upgrades_END
```
