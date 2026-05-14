# HTAPUtils.rb

## Purpose & Scope
- `inc/HTAPUtils.rb` bundles the shared plumbing used by every HTAP script: logging/bootstrap (`HTAPInit`), option/choice parsing (`HTAPData`), geometry summaries, git metadata collection, CSV helpers, and persistent configuration management (`HTAPConfig`).
- The module handles the heavy lifting for interpreting `HTAP-options.json`, validating `.choices`, normalising foundation selections, and preparing the JSON summary consumed downstream by reporting tools.

## HTAPInit & Global Context
- `HTAPInit()` must be called at the top of long-running scripts (`substitute-h2k.rb`, `htap-prm.rb`). It:
  - Records `$startProcessTime` and `$gMasterPath`.
  - Opens run-specific log/summary files via `openLogFiles` (from `inc/msgs.rb`).
  - Stores the script root (`$scriptLocation`) and logs it.
  - Loads the persistent configuration JSON (`ConfigDataFile`, typically `htap.config`) through `HTAPConfig.parseConfigData()`.
- The function assumes `$program` is defined by the caller (usually set to the script filename). It also initialises flags used by the logging system (`$gHelp`, `$gHelpMsgsSent`, etc.).

## Utility Helpers
- `flattenHash(hash, breadcrumbs="")` – Recursively flattens nested hashes into colon-delimited keys (`foo:bar:baz => value`). Used when exporting data to CSV or logs.
- `emptyOrNil(var)` / `emptyOrNilRecursive(var)` – Check for `nil`/empty strings (and nested empties for arrays/hashes). Prevents noisy logging and avoids raising on missing data.
- `convertToCSV(array_of_hashes, printHeader=true, header=[])` – Serialises an array of hashes into CSV text. If no header is supplied it infers one from the first element and preserves order for subsequent batches (e.g., when writing HTAP-prm outputs).

## HTAPData Module
Centralised data wrangling for options, choices, results, and metadata.

### Options & Rulesets
- `getOptionsData()` – Lazy-loads `HTAP-options.json` (path stored in `$gHTAPOptionsFile`), parsing it via `parse_json_options_file` and memoising the structure in `$gHTAPOptions`.
- `returnProxyIfExists(attribute, choice)` – Returns the proxy target defined in the options catalogue when costing metadata specifies `"proxy"`.
- `parse_json_options_file(filename)` – Converts the raw options JSON into the internal structure used by substitute:
  - Records tag order (`"tags"`) for tree attributes, default values, cost metadata (`costComponents`, `costCustom`, `costProxy`).
  - Normalises every `h2kMap` entry into the `[index]["conditions"]["all"]` format consumed in substitutions.
- `parse_upgrade_file(filename)` – Reads upgrade-package JSON (`HTAP-rulesets.json`) into a Ruby hash for ruleset expansion.

### Choices & Validation
- `parse_choice_file(path)` – Reads `.choices` files, stripping comments, enforcing order, and handling special cases:
  - Preserves the sequence in `order` (the substitution order used by `processFile`).
  - Normalises `GOconfig_rotate` and splits rule-set arguments (`Opt-Ruleset = Package[cond>value;...]`).
  - Mirrors `Opt-Ceilings` onto attic/cathedral/flat keys for backwards compatibility.
- `isAttribValid`, `isChoiceValid`, `isAttribIgnored` – Guard functions used during validation; they respect `$DoNotValidateOptions` and `$LegacyOptionsToIgnore` constants from `inc/constants.rb`.
- `queryAttribAliases(attribute)` – Maps deprecated attribute names to their canonical form using `AliasesForAttributes`, warning the user when a legacy name is detected.
- `validate_options(options, choices, order)` – Core sanity check that:
  - Logs the incoming choices and adds defaults for missing attributes when `stop-on-error` permits.
  - Verifies each choice exists in the options catalogue, respecting `stop-on-error` flags.
  - Calls `zeroInvalidFoundation` to resolve conflicts between whole-foundation and surface-by-surface definitions.
  - Returns `(error_flag, validated_choices, updated_order)` for the caller to act on.
- `zeroInvalidFoundation` / `whichFdnConfig` / `valOrNaOrNil` – Assist with foundation option management, ensuring invalid combinations (e.g., insulated slab with uninsulated walls) are corrected and flagging when HTAP had to modify user selections (`$gChoicesChangedbyProgram`).

### Result & Reporting Utilities
- `getResultsForChoice(options, attribute, choice)` – Extracts the resolved tag/value hash for a given option. Used heavily in substitution logic and costing.
- `simpleConditional(modelValue, operator, queryValue)` – Evaluates simple conditionals found in legacy rules (`<`, `=`, `inc`, `per`, `else`).
- `parse_results(filename)` – Convenience wrapper to load a JSON results file (`h2k_run_results.json`).
- `summarizeArchetype(myH2KHouseInfo, secLevel)` – Formats geometry and system details (using `MDRpts` helpers) for inclusion in summary reports. Takes the nested hash produced by `H2KFile.getAllInfo`.
- `getGitInfo()` – Returns `(branch_name, revision)` from the repository. Used by `htap-prm` and report headers.
- `prepareResult4Json()` – Constructs the final HTAP result payload using global values populated during substitution (e.g., `$gResults`, `$ArchetypeData`, `$HDDs`). Any script writing JSON output should call this to ensure consistent structure.

## HTAPConfig Module
Persists run-manager telemetry and misc settings in `htap.config`.
- `parseConfigData()` – Loads the JSON config into `$gConfigData` on startup.
- `getData(keys)` / `setData(keys, value)` – Generic nested hash accessors (keys supplied as arrays). Auto-creates branches when needed.
- `checkKeys(object, keys, action)` – Helper for recursively ensuring path existence.
- `setPrmSpeed(time_per_eval)` / `getPrmSpeed()` – Store historical evaluation times so `htap-prm` can estimate run length.
- `countSuccessfulEvals(evals)` / `reportSuccessfulEvals()` – Track cumulative HOT2000 simulations.
- `getCreationDate()` / `setCreationDate()` – Record when the config was first created (used for fun facts in logs).
- `checkOddities()` – Optional flag to surface interesting stats at the end of runs.
- `writeConfigData()` – Writes the updated config back to disk (pretty-printed JSON) and stamps `updateTime`.

## Key Globals & Dependencies
- Logging & messaging rely on `inc/msgs.rb` for `debug_out`, `info_out`, `warn_out`, `err_out`, `fatalerror`, and `openLogFiles`.
- Constants such as `$LegacyOptionsToIgnore`, `$DoNotValidateOptions`, `AliasesForAttributes`, `ConfigDataFile`, and the long-form aliases (`$aliasLongConfig`, etc.) are defined in `inc/constants.rb`.
- Several helpers (e.g., `summarizeArchetype`) depend on `inc/MDRpts.rb` for report formatting and on geometry packed by `H2KFile`.
- `prepareResult4Json` expects numerous globals (e.g., `$gResults`, `$FloorArea`, `$AreaWin_sum`) set elsewhere in the substitution pipeline. Ensure those variables are defined before calling it directly.

## Practical Usage Notes
- Always call `HTAPInit()` once at startup before invoking any other helper. It wires up logging and loads config state so later writes succeed.
- After altering `HTAP-options.json` or `htap.config`, rerun a small scenario (`util/misc-dev-tests.rb` or a simple `.run`) to confirm `parse_json_options_file` and validation still succeed.
- When adding new attributes, update: `HTAP-options.json`, any necessary aliases (`AliasesForAttributes`), and consider whether they require entries in `$DoNotValidateOptions` or `$LegacyOptionsToIgnore`.
- If you extend costing metadata, ensure `returnProxyIfExists` and `prepareResult4Json` still produce meaningful output—add the new keys to costing JSON as needed.
- `HTAPConfig` writes to disk every time `htap-prm` completes a batch. If you introduce new statistics, follow the existing pattern (retrieve with `getData`, update, and rely on `writeConfigData`).

## Where It’s Used
- `substitute-h2k.rb` – Invokes almost every helper: initializes via `HTAPInit`, parses choices/options, validates selections, merges foundation rules, and builds JSON results.
- `htap-prm.rb` – Uses `HTAPInit`, `HTAPData` to parse `.run` expansions and defaults, `HTAPConfig` for duration estimates/history, and `prepareResult4Json` to collate run outputs.
- Reporting utilities in `util/` and `doc/` rely on `summarizeArchetype`, `convertToCSV`, and `flattenHash` to build human-readable summaries.
