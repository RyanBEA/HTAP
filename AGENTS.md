# Repository Guidelines

## Project Structure & Module Organization
HTAP scripts sit at the repository root: `htap-prm.rb` acts as the run manager and `substitute-h2k.rb` patches HOT2000 project files. Shared Ruby modules live in `inc/` (rulesets, costing, hourly utilities). `lib/` stores the HOT2000 support payload plus `CopyToH2K.rb` for seeding `C:\H2K-cli-min\User`. Scenario inputs reside in `testing/` (notably `testing\h2k-files` sample dwelling files and `testing\hourly` weather runs). Data-prep and analysis helpers live in `util/`, while reference material stays in `doc/`.

Key documentation resources:
- `doc/substitute-h2k.md` – HOT2000 substitution script overview and workflow.
- `doc/htap-prm.md` – Run manager CLI, batching, resume handling, and integration notes.
- `doc/H2KUtils.md` – Shared initialization, choice/option parsing, and configuration helpers.
- `doc/HTAP-options.md` – Attribute schema, option formats, and costing metadata.
- `doc/costing.md` – Cost engine inputs, proxy/conditional handling, and audit outputs.
- `doc/application-modules.md` – BC Step Code utilities and LEEP Pathways exporters.
- `doc/run-files.md` – `.run` definition anatomy, supported directives, and wildcards.

## Build, Test, and Development Commands
Use Ruby 2.7+ alongside the HOT2000 CLI installed at `C:\H2K-cli-min`. Typical workflows:
- `ruby htap-prm.rb --help` lists run-manager options.
- `ruby htap-prm.rb --options HTAP-options.json --h2k testing\h2k-files\NRCan-arch4_2100sf_2storey_fullBsmt.h2k` runs a baseline scenario and writes logs next to the input.
- `ruby substitute-h2k.rb --source testing\h2k-files\NRCan-arch4_2100sf_2storey_fullBsmt.h2k --choices HTAP-options.json` applies option bundles to an archetype.
- `ruby util\misc-dev-tests.rb` performs smoke checks of HTAP initialization and logging.
Always run from the repository root so relative paths resolve correctly.

## Coding Style & Naming Conventions
Ruby files keep two-space indentation and snake_case method names (see `inc\HTAPUtils.rb`). Constants stay SCREAMING_SNAKE_CASE. Prefer double quotes when strings touch JSON or need interpolation; use single quotes otherwise. Group functionality inside modules (e.g., `BCStepCode`) and add concise comments for policy logic or external data assumptions. JSON resources remain UTF-8, minified, and use Windows-safe paths.

## Testing Guidelines
There is no automated unit-test harness; verification relies on deterministic HOT2000 runs. Clone an existing `testing\h2k-files\*.h2k` case, adjust inputs, then process it via `htap-prm.rb` while keeping previous outputs for comparison. For costing adjustments, diff CSV results with `perl util\compare_csv.pl baseline.csv candidate.csv`. Add scenario folders under `testing/` when introducing new pathways and capture expected outputs for reviewers.

## Commit & Pull Request Guidelines
Write commits in imperative mood with a scoped prefix, e.g., `inc: tighten BC step code thresholds`. Separate data updates (such as `HTAPUnitCosts.json`) from code to simplify review. Pull requests should summarise modelling intent, include the commands and files used for validation, and link the related NRCan ticket or issue. Attach before/after cost or energy tables whenever behaviour changes.

## Configuration Notes
Ensure the HOT2000 CLI assets stay synced by running `ruby lib\CopyToH2K.rb` after CLI updates. Keep proprietary cost spreadsheets and credentials outside the repository, and document any required environment variables in `doc/` rather than embedding paths in code.
