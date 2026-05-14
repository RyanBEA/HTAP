# HTAP — bea-11.8 branch

This is the BEA fork of HTAP at the `bea-11.8` branch (based on upstream `general-dev`), paired with **HOT2000 11.8** at `C:\H2K-CLI-11.8`.

## When you're working here

This directory is HTAP **the tool**. If you're editing HTAP itself (Ruby modules, options database, run-time logic), this is the right place. If you're using HTAP to analyze a building, you probably want to be in `C:\BEAtools\projects\<project>\` instead — that's where per-client / per-study work lives.

## Running HTAP from here

```powershell
$env:H2K_CLI_HOME = 'C:\H2K-CLI-11.8'
cd <some working dir, NOT this one — outputs go in CWD>
ruby C:\HTAP-11.8\htap-prm.rb -r <runfile>.run -t 8 -c -k
```

## Remote setup

- `origin` = `https://github.com/RyanBEA/HTAP` (push enabled)
- `upstream` = `https://github.com/NRCan-IETS-CE-O-HBC/HTAP` (fetch-only; push is set to `DISABLED` for safety — see `git remote -v`)

To pull upstream fixes: `git fetch upstream && git merge upstream/general-dev`.

## BEA commits on top of upstream

- `feat: read CLI install path from H2K_CLI_HOME env var (BEA)` — three-file env-var patch
- `feat(lib): BEA code library extensions` — replaces upstream `lib/codeLib.cod` and adds `lib/rylib.cod`
- `feat: add FDWR analysis run configuration` — `fdwr.run` for NBC 9.36.8.6 studies
- `feat: add BEA custom HTAP options` — `HTAP-options-custom.json`
- `feat(configapp): add HTAP run-file web editor` — `configapp/` browser-based editor
- `feat(development): add htap-config-editor (Streamlit) + planning archive` — `development/`
- `docs+config: add regression-baseline .run files and getting-started guide` — `recover/regions.run`, `recover/test.run`, `gettingStarted.md`
- `feat(archetypes): add ERS-EX test archetypes` — 7 ERS-EX test h2k files

## See also

- `C:\BEAtools\design\2026-05-12-htap-multiversion-agentic-workflow-design.md` — overall BEA HTAP layout design
- `C:\BEAtools\design\2026-05-12-htap-multiversion-phase-a-infrastructure.md` — Phase A migration plan
- `C:\BEAtools\projects\CLAUDE.md` — convention for invoking HTAP from a project
- `C:\HTAP-11.12\` — the parallel bea-11.12 clone (HOT2000 11.12)
- `C:\HTAP2015code\` — the separate BEA fork for NBC 2015 compliance work
