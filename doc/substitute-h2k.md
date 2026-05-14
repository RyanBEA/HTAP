# substitute-h2k.rb

## Purpose & Scope
- substitute-h2k.rb is the HTAP transformer that reads an archetype HOT2000 `.h2k` file, applies an option bundle, and (optionally) runs the HOT2000 CLI so the modified file contains fresh simulation outputs.
- Bridges abstract HTAP option definitions (`HTAP-options.json`) and user selections (`*.choices`) to the low-level XML expected by HOT2000.
- Can be driven directly by analysts or invoked as a worker by the run manager (`htap-prm.rb`) when iterating through scenarios.

## Typical Invocation
```powershell
ruby substitute-h2k.rb --choices testing\h2k-files\NRCan-arch4_2100sf_2storey_fullBsmt.choices --options HTAP-options.json --base_model testing\h2k-files\NRCan-arch4_2100sf_2storey_fullBsmt.h2k
```
- When `Opt-Archetype` is provided in the choice file the base model can be omitted; the script resolves the archetype path from `HTAP-options.json`.

## Inputs & CLI Surface
### Required
- `--choices FILE` (`-c`): Choice set to apply; parsed via `HTAPData.parse_choice_file` and validated later.
- `--options FILE` (`-o`): Option catalog. JSON (`HTAP-options.json`) is preferred; legacy `.options` are up-converted to the internal structure.

### Common optional flags
- `--base_model FILE` (`-b`): Explicit HOT2000 archetype. If omitted the `Opt-Archetype` choice must resolve the file.
- `--unit-cost-db FILE`: Supply `HTAPUnitCosts.json` (required when `--auto-cost-options` is used).
- `--rulesets FILE`: Load packaged upgrades or rules that can mutate the choice hash before validation.
- `--prm`: Indicates the process is under `htap-prm.rb`; skips copying the base file because the manager already staged it.
- `--auto-cost-options`: After a successful run, call `Costing.parseUnitCosts` and `estimateCosts` to attach capital-cost outputs.
- `--hourly-output`: Enable hourly extrapolation using the hourly utilities module.
- `--export-options-to-json`: Dump a JSON view of a legacy `.options` file and exit.
- `--keep_H2K_folder`: Leave the working `H2K` folder in place (useful for debugging the CLI payload).
- `--verbose`, `--warnings`, `--no-debug`, `--hints`: Control logging verbosity routed through `inc/msgs` helpers.

## Execution Flow
1. **Initialisation** - Sets `$program`, calls `HTAPInit()` (from `inc/HTAPUtils.rb`) to establish logging (`substitute-h2k_log.txt`, `..._summary.out`), load configuration, and record the working directory in `$gMasterPath`.
2. **Argument parsing** - `OptionParser` processes CLI flags, populating global state such as `$gChoiceFile`, `$gOptionFile`, `$unitCostFileName`, and execution flags (`$PRMcall`, `$autoEstimateCosts`, `$hourlyCalcs`, etc.).
3. **Option catalogue ingest** - `HTAPData.parse_json_options_file` (or `parse_legacy_options_file`) reads the options file, normalising each attribute into hashes with `tags`, `options`, default values, and metadata (e.g., `costComponents`).
4. **Choice ingest and augmentation** - `HTAPData.parse_choice_file` returns both `$gChoices` and `$gChoiceOrder`, preserving the author-defined substitution order. If `--rulesets` is supplied, upgrade packages are applied to the choice hash before validation.
5. **Base model resolution** - Either accept `--base_model` or look up the file specified by the `Opt-Archetype` choice. The script tracks the HOT2000 CLI source tree (`C:\H2K-CLI-Min`) and stages a working copy in `<repo>\H2K`.
6. **Working copy preparation** - Mirrors the HOT2000 CLI payload into the working `H2K` directory, verifies it via MD5 (`checksum` helper), fixes configuration (`H2KUtils.fix_H2K_INI`, `write_h2k_magic_files`), and clears large transient files (`ROutStr.txt`). When not in `--prm` mode it copies the base `.h2k` into the repository root.
7. **Choice validation** - `HTAPData.validate_options` ensures every requested option exists, enforces dependency logic, and updates `$gChoiceOrder`. Any auto-corrections are flagged via `$gChoicesChangedbyProgram` and logged as warnings.
8. **Substitution** - `processFile(h2kElements)` drives the bulk of the XML editing:
   - Loads the `.h2k` into memory (`H2KFile.get_elements_from_filename`) and iterates in `$gChoiceOrder`.
   - For attributes tagged as `internal`, maps schema tags to XML nodes and assigns values (e.g., fuel libraries, infiltration rates, envelope codes).
   - Special cases (windows, foundations, equipment sizing, etc.) call dedicated helpers from `H2KFile` or `HTAP2H2K`, often applying multiple related choices together.
   - Cross-cutting adjustments (foundations, permafrost handling, rule-based tweaks) run after the sequential pass.
   - Removes stale result nodes (`HouseFile/AllResults`), writes the altered model back to disk, and archives a copy as `file-postsub.h2k` for debugging.
9. **Orientation setup** - Orientation behaviour comes from the `GOconfig_rotate` option: if set to `AVG` it queues runs for S/N/E/W, otherwise it runs the specified azimuth. `$angles` translates cardinal directions to rotation degrees for reporting.
10. **Simulation loop** - For each queued orientation, `runsims` copies `file-postsub.h2k` to `run_file_file_<n>.h2k`, launches `HOT2000.exe -inp ...`, and enforces `$maxRunTime`/`$maxTries`. Successful runs copy the resulting `.h2k` back to the working root so it contains the fresh `HouseFile/AllResults` payload.
11. **Post-processing** - `postprocess` reloads the updated `.h2k`, reads summary metrics (energy, loads, ERS outputs), and supplements them with data parsed from `Browse.rpt` and optionally `ROutStr.txt`. Results are accumulated in `$gResults` and exported through `HTAPData.prepareResult4Json` to `h2k_run_results.json`.
12. **Costing & metrics** - If requested, `estimateCosts` combines selections, unit costs, and the persisted choice order to build cost tables. Additional KPIs such as TEDI/MEUI and utility proxies are computed before logging.
13. **Cleanup** - Copies `Browse.rpt` into `sim-output/`, deletes transient `WMB_*` files, and (unless `--keep_H2K_folder`) removes the replicated `H2K` directory. Finally, logs are closed via `ReportMsgs`.

## Applying Choices to HOT2000
- `HTAP-options.json` entries define an `h2kSchema` (list of tags) and an `h2kMap` that supplies values per option. The parser translates these into numeric indices so `processFile` can address XML nodes by schema position.
- `$gChoiceOrder` preserves author-defined sequencing, which matters for dependencies (e.g., weather library before location-specific tweaks). Skip lists (`$DoNotValidateOptions`) allow certain attributes to bypass validation.
- Many attributes trigger bespoke logic beyond simple tag replacement - for example: `Opt-ACH` toggles blower-door test flags, `Opt-Ceilings` hunts code-library entries via `findCeilingCodeInLibrary`, and foundation options call `HTAP2H2K.conf_foundations` to coordinate wall/slab settings.
- Ruleset packages provide higher-level bundles (e.g., Step Code tiers). After they mutate `$gChoices`, validation re-runs to ensure the modified selections still align with available options.

## Simulation & Post-Processing Details
- `runsims` executes inside the staged `H2K` directory, isolating HOT2000 assets from the repository. It maintains retries, tracks elapsed time in `$runH2KTime`, and records attempt counts for downstream reporting.
- HOT2000 writes a `.run` file alongside the `.h2k`; however, the script primarily consumes the embedded `HouseFile/AllResults` section in the modified `.h2k` plus textual diagnostics (`Browse.rpt`, `ROutStr.txt`). `.run` artifacts remain useful for manual inspection if diagnosing CLI crashes.
- `postprocess` aggregates results per orientation and per HOT2000 house code (SOC, Reference, etc.), storing them in `$gResults`. The helper eventually creates `h2k_run_results.json`, the canonical machine-readable summary consumed downstream by `htap-prm.rb` and analytics tooling.

## Key Outputs & Side Effects
- Logs: `substitute-h2k_log.txt`, `substitute-h2k_summary.out`, and the legacy `SubstitutePL-log.txt` created by shared logging helpers.
- Working artifacts: replicated `H2K/` CLI payload, `file-postsub.h2k` (pre-run snapshot), `run_file_file_<n>.h2k` during retries, and the final `.h2k` with run results.
- Results: `sim-output/Browse.rpt`, optional `sim-output/ROutStr.txt`, `h2k_run_results.json`, costing summaries (when enabled), and updated `$gResults` passed back to callers.

## Integration Points to Track
- **htap-prm.rb** - When the run manager spawns this script with `--prm`, it handles orchestration (option set iteration, resume logic). substitute-h2k reports status via logs and the JSON result file, which the manager reads to build portfolio outputs.
- **inc/H2KUtils.rb** - Provides `H2KFile` (XML convenience layer), run-folder preparation (`fix_H2K_INI`, `write_h2k_magic_files`), and checksum utilities used throughout the setup and processing phases.
- **HTAP-options.json** - Primary data source for option schemas, default values, costing metadata, and archetype file paths. Any adjustment to the JSON schema must be mirrored in `HTAPData.parse_json_options_file`.
- **.run files** - HOT2000 CLI produces `Hot2000.run` alongside the `.h2k` file in the working directory. While substitute-h2k does not parse it directly, retaining the file helps diagnose simulations and is often zipped by `htap-prm` for audit trails.

## Troubleshooting & Debugging
- Start by inspecting `substitute-h2k_log.txt`; verbose mode (`--verbose`) adds per-tag substitution traces. `SubstitutePL-log.txt` retains legacy messaging used by external wrappers.
- `file-postsub.h2k` shows the exact XML handed to HOT2000. Compare it with the post-run `.h2k` (or `Hot2000.run`) to isolate simulation-side issues.
- Keep `--keep_H2K_folder` on when debugging HOT2000 CLI behaviour; it preserves the executable payload along with intermediate run files.
- If substitutions fail validation, `validate_options` logs the offending attribute and, when possible, adjusts the choice to a compatible fallback; watch for warnings about program-changed selections.
