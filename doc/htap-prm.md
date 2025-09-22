# htap-prm.rb

## Purpose & Scope
- `htap-prm.rb` is the HTAP parallel run manager that expands scenario definitions, orchestrates batches of `substitute-h2k.rb` executions, and aggregates the resulting performance/cost outputs.
- Designed to consume `.run` definition files (mesh/parametric/sample studies) but also accepts raw `.choices` files on the command line.
- Handles multi-threaded execution, progress tracking, resume bookkeeping, JSON/CSV exports, and optional downstream integrations (costing, LEEP Pathways, hourly extrapolation).

## Typical Invocation
```powershell
ruby htap-prm.rb --run-def testing\runs\trial-mesh.run --threads 8 --json
```
- When no `--run-def` is supplied, any `.choices` files passed on the CLI are executed verbatim.

## CLI Surface
- `--run-def FILE` (`-r`): Required for structured studies; points at a `.run` file that defines archetypes, locations, rulesets, and upgrade lists.
- `--threads X` (`-t`): Caps concurrent HOT2000 runs. Manager allocates `HTAP-work-<idx>` directories up to this number (default 3).
- `--compute-costs`: Instructs PRM to pass `--auto-cost-options` and `--unit-cost-db` to each `substitute-h2k.rb` call. Requires either a `unit-costs-db=` entry in the `.run` file or prior configuration.
- `--confirm` (`-c`): Prompt for approval after estimating the batch duration using historical throughput (persisted via `HTAPConfig`).
- `--extra-output` (`-e`): Propagates `-e` to substitute to retain extended result bundles.
- `--hourly-output`: Adds `-g` when launching substitute and implicitly enables `--keep-all-files` so hourly CSVs survive cleanup.
- `--keep-all-files` (`-k`): Copies the full contents of each `HTAP-work` directory into `HTAP-sim-<n>` regardless of success.
- `--json` (`-j`): Append `HTAP-prm-output.json` to the standard CSV export.
- `--LEEP-Pathways`: Activates the LEEP export pipeline in `inc/application_modules.rb`.
- `--include_audit_data`: Keep the verbose costing audit block in JSON output (otherwise removed to keep files lighter).
- `--resume`: Attempt to continue from an existing `HTAP-prm.resume` file; only run definitions generated previously are skipped.
- `--stop-on-error`: Abort the job after the first failed simulation.
- `--log-debug-msgs`: Drops the `--no-debug` guard when spawning substitute so its verbose logs and debug artifacts are retained.
- `--help` (`-h`): Usage summary.

## `.run` Definition Anatomy
`parse_def_file` expects the configuration to be segmented with sentinel lines:
```
RunParameters_START ... RunParameters_END
RunScope_START ... RunScope_END
Upgrades_START ... Upgrades_END
```
Within these blocks, tokens are written as `key=value` (whitespace and `!` comments removed). Key directives include:
- **RunParameters**
  - `options-file=path\to\HTAP-options.json`
  - `archetype-dir=path\to\*.h2k`
  - `substitute-file=path\to\substitute-h2k.rb` (defaults to `C:/HTAP/substitute-h2k.rb`)
  - `rulesets-file=path\to\HTAP-rulesets.json`
  - `unit-costs-db=path\to\HTAPUnitCosts.json` (enables costing without needing `--compute-costs`)
  - `run-mode=mesh | parametric | sample{n:###;seed:###}`
- **RunScope**
  - `archetypes=NRCan-arch1.h2k,NRCan-arch2.h2k`
  - `locations=AB-Calgary,BC-Vancouver` (supports `*` wildcards which expand against `Opt-Location` choices)
  - `rulesets=NA,BCStepCode`
- **Upgrades**
  - Attribute names (aliases resolved through `HTAPData.queryAttribAliases`) mapped to comma separated choices. Wildcards expand against `HTAP-options.json`; `upgrade-package-list` is resolved via the ruleset JSON.

Sample skeleton:
```text
RunParameters_START
  options-file=C:\HTAP\HTAP-options.json
  archetype-dir=testing\h2k-files
  run-mode=mesh
RunParameters_END
RunScope_START
  archetypes=NRCan-arch4_2100sf_2storey_fullBsmt.h2k
  locations=BC-Vancouver,AB-* 
  rulesets=NA
RunScope_END
Upgrades_START
  Opt-WallAssembly=ref,stepCodeTier2
  Opt-HeatingSystem=Baseboards,HP-
  upgrade-package-list=BC-StepCode-Tier3
Upgrades_END
```

## Scenario Expansion Modes
- **Mesh (default)**: `create_mesh_cartisian_combos` recursively evaluates the Cartesian product of scope selections and upgrade choices, writing each combination to an in-memory `.choices` blob (`ChoiceFileContents`).
- **Sample**: Generates the full mesh first, then down-samples using Ruby’s `shuffle` (optionally seeded). Use `sample{n:250;seed:42}` to specify size/seed.
- **Parametric**: For every archetype-location-ruleset tuple, runs a baseline with the first choice of each attribute and then creates a variant for each remaining choice on a one-at-a-time basis.
- Wildcards in locations or upgrades are expanded before combinations are generated. Invalid attributes/choices, non-existent files, or unsupported run-modes trigger `fatalerror`.

## Execution Flow
1. **Init & estimation**
   - `HTAPInit` sets up logging (`htap-prm_log.txt`, `htap-prm_summary.out`) and loads config values via `HTAPConfig`.
   - Option parsing stores flags (`$gExtendedOutputFlag`, `$gHourlySimulationFlag`, `$gSaveAllRuns`, etc.).
   - For `.run` jobs the manager calls `parse_def_file`, validates attributes with `HTAPData.isAttribValid/isChoiceValid`, and estimates runtime from historic evaluation speeds.
2. **Choice file generation**
   - Each combination becomes a synthetic `.choices` file (kept in memory unless `choicesInMemory` is disabled). Metadata tables record the paired archetype, location, and ruleset for downstream logging.
3. **Batch execution** (`run_these_cases`)
   - Allocates per-thread run directories `HTAP-work-<n>` and rotates through the pending combinations.
   - For each thread: copies the archetype, options, and generated `.choices` into the run dir, then spawns `substitute-h2k.rb --prm` via `Process.spawn`, passing through costing, ruleset, extended output, and hourly switches as needed.
   - Supports legacy 936 HRV Perl hooks (triggered by specific ruleset names) before invoking substitute.
   - Updates a shared `update_run_status` buffer so other processes/UI can poll batch state.
4. **Monitoring & retries**
   - Waits on each spawned PID. Non-zero exits mark the run as failed and log errors in `substitute-h2k-errors.txt`.
5. **Result harvesting**
   - Consumes `h2k_run_results.json` when present (preferred) or falls back to `substitute-h2k_summary.out` token/value pairs.
   - Merges status, configuration, outputs, and optional cost audits into a per-run hash, appended to `$gJSONAllData` for later serialization.
   - If costing JSON contains `audit` blocks and `--include_audit_data` is not set, they are stripped before aggregation.
6. **Persistence & cleanup**
   - Successful runs contribute rows to `HTAP-prm-output.csv`; the header is emitted on the first batch.
   - Optional JSON appends to `HTAP-prm-output.json`, carefully rewriting the trailing configuration block between batches.
   - LEEP pathway exports are streamed through `LEEPPathways` helper methods when enabled.
   - Run directories are copied to `HTAP-sim-<run>` if `--keep-all-files`, `--hourly-output`, or the run failed; otherwise only key artifacts remain and `sim-output` folders are trimmed.
   - `HTAP-prm.resume` is updated with each finished run so `--resume` can skip already-completed combinations; `HTAP-prm-failures.txt` captures any errors.
7. **Final reporting**
   - Summaries of success/failure counts are written to stdout and logs. Historical evaluation speed and run counts are persisted via `HTAPConfig` for later duration estimates.

## Resume & Recovery
- `--resume` reuses `HTAP-prm-output.csv`/`.json`, parses `HTAP-prm.resume`, and only schedules combinations that are not listed.
- New runs append to the resume file and the CSV/JSON; failed runs remain in the queue unless manually removed.
- If resume parsing fails, the job aborts because the manager cannot safely determine which runs to skip.

## Key Outputs & Directories
- Logs: `htap-prm_log.txt`, `htap-prm_summary.out` (from `HTAPInit`).
- Aggregates: `HTAP-prm-output.csv`, optional `HTAP-prm-output.json`, and `HTAP-prm.resume`/`HTAP-prm-failures.txt`.
- Working dirs: `HTAP-work-<thread>` (live execution), `HTAP-sim-<run>` (saved artifacts when requested or on failure).
- Downstream files: each run’s `h2k_run_results.json`, `substitute-h2k_log.txt`, `sim-output/Browse.rpt`, costing audits, etc., organized per `HTAP-sim-<run>`.

## Integration Touchpoints
- **substitute-h2k.rb**: Spawned for every combination with `--prm` so it reuses the manager’s staging and skips certain cleanup.
- **HTAP-options.json**: Parsed once via `HTAPData.getOptionsData()`; all upgrade validation and wildcard expansion rely on the schema defined there.
- **inc/H2KUtils.rb**: Provides `HTAPInit`, logging helpers, git metadata, CLI configuration reads, and formatters (`formatTimeInterval`).
- **inc/application_modules.rb**: Supplies status callbacks (`update_run_status`) and the `LEEPPathways` export helpers.
- **Ruleset and costing JSON**: When `rulesets-file` or `unit-costs-db` are specified, PRM passes the paths to substitute so ruleset packages and costing logic execute consistently across runs.

## Troubleshooting Tips
- Review `htap-prm_log.txt` and `HTAP-prm-failures.txt` first; they list runs that exited with non-zero status or produced no output.
- Inspect the corresponding `HTAP-sim-<run>` folder for `substitute-h2k-errors.txt`, preserved `.h2k` files, `file-postsub.h2k`, and HOT2000 logs.
- If batches stall, check disk I/O contention—consider lowering `--threads` or reviving the commented `--snailStart` logic (introduces delays between first-batch spawns).
- Wildcard expansions depend on the current `HTAP-options.json`. When attributes or choices are renamed, update `.run` files to avoid fatal validation errors.
- `--resume` only works when `HTAP-prm.resume` reflects the exact combinations previously generated; editing the `.run` file mid-resume may lead to mismatches.
