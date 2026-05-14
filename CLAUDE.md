# HTAP — bea-11.12 branch

This is the BEA fork of HTAP at the `bea-11.12` branch (based on upstream `support-11.12b`), paired with **HOT2000 11.12** at `C:\H2K-CLI-11.12`.

## When you're working here

This directory is HTAP **the tool**. If you're editing HTAP itself (Ruby modules, options database, run-time logic), this is the right place. If you're using HTAP to analyze a building, you probably want to be in `C:\BEAtools\projects\<project>\` instead — that's where per-client / per-study work lives.

## Running HTAP from here

```powershell
$env:H2K_CLI_HOME = 'C:\H2K-CLI-11.12'
cd <some working dir, NOT this one — outputs go in CWD>
ruby C:\HTAP-11.12\htap-prm.rb -r <runfile>.run -t 8 -c -k
```

## Remote setup

- `origin` = `https://github.com/RyanBEA/HTAP` (push enabled)
- `upstream` = `https://github.com/NRCan-IETS-CE-O-HBC/HTAP` (fetch-only; push is set to `DISABLED` for safety — see `git remote -v`)

To pull upstream fixes: `git fetch upstream && git merge upstream/support-11.12b`.

## BEA commits on top of upstream

- `feat: read CLI install path from H2K_CLI_HOME env var (BEA)` — three-file env-var patch
- `fix(h2k): correct isCop attribute + value field for HeatingEfficiency` — HSPF/COP attribute-name fix
- `perf(htap-prm): write HTAP-prm-output.json compact instead of pretty` — compact JSON output
- `fix(options): correct RSI units + update ASHP COP/rating-temp` — HTAP-options.json BEA edits
- `docs: add BEA-authored module reference docs` — `doc/*.md` module guides

## See also

- `C:\BEAtools\design\2026-05-12-htap-multiversion-agentic-workflow-design.md` — overall BEA HTAP layout design
- `C:\BEAtools\design\2026-05-12-htap-multiversion-phase-a-infrastructure.md` — Phase A migration plan
- `C:\BEAtools\projects\CLAUDE.md` — convention for invoking HTAP from a project
- `doc/` — BEA-authored module docs (H2KUtils, HTAP-options, HTAPUtils, application-modules, costing, htap-prm, run-files, substitute-h2k)
- `C:\HTAP-11.8\` — the parallel bea-11.8 clone (HOT2000 11.8)
- `C:\HTAP2015code\` — the separate BEA fork for NBC 2015 compliance work
