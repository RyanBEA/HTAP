# HTAP-options.json

## Purpose & Scope
- `HTAP-options.json` is the authoritative catalogue of HTAP attributes: every `Opt-*` setting that appears in `.choices` files is described here along with the XML tags it touches and the costing metadata it contributes.
- `substitute-h2k.rb` loads the file (via `HTAPData.parse_json_options_file`) to learn how each choice should be mapped into HOT2000, while costing and run-management logic rely on the same metadata for validation, pricing, and mesh generation.

## Top-Level Attribute Schema
Each top-level key (e.g., `Opt-Archetype`, `Opt-ACH`, `GOconfig_rotate`) is a JSON object with common fields:
- `structure` – Either `"flat"` or `"tree"`; drives how the parser interprets `options`.
- `costed` – Boolean indicating whether the attribute participates in the costing pipeline (`estimateCosts`).
- `options` – Dictionary whose keys are the legal choice values that can appear in `.choices` files or rulesets.
- `default` (optional) – Fallback option if a scenario omits the attribute.
- `stop-on-error` – When true, `HTAPData.validate_options` treats invalid or missing choices as fatal rather than silently coercing them.
- `h2kSchema` (tree attributes only) – Ordered list of placeholders that describe which HOT2000 tags this attribute controls. The parser uses the index to build `$gOptions[attrib]["tags"]` for downstream substitution.

## Option Entry Shapes
### Flat Attributes
Use `structure: "flat"` when a choice maps to a single primitive value. Example:
```json
"Opt-Archetype": {
  "structure": "flat",
  "costed": false,
  "options": {
    "NA": "NA",
    "SmallSFD": "C:\\H2K-CLI-Min\\User\\BC-Step-rev-SmallSFD.h2k",
    "Rowhouse": "C:\\H2K-CLI-Min\\User\\BC-Step-rev-Row.h2k"
  },
  "default": "NA",
  "stop-on-error": true
}
```
`substitute-h2k` will copy the selected string directly into the working directory (for archetypes) or onto an internal flag.

### Tree Attributes
Use `structure: "tree"` when a choice drives one or more HOT2000 tags. Each option provides an `h2kMap` with a `base` dictionary whose keys correspond to entries in `h2kSchema`:
```json
"Opt-ACH": {
  "structure": "tree",
  "costed": true,
  "h2kSchema": [
    "<Opt-ACH>",
    "Opt-BuildingSite",
    "Opt-WallShield",
    "Opt-FlueShield"
  ],
  "options": {
    "ACH_NBC": {
      "h2kMap": {
        "base": {
          "<Opt-ACH>": "2.5",
          "Opt-BuildingSite": "7",
          "Opt-WallShield": "4",
          "Opt-FlueShield": "2"
        }
      },
      "costs": {
        "proxy": "New-Const-air_seal_to_2.50_ach",
        "custom-costs": {}
      }
    },
    "ACH_8": {
      "h2kMap": { "base": { "<Opt-ACH>": "8.0", ... } },
      "costs": { "custom-costs": {}, "components": [] }
    }
  },
  "default": "NA",
  "stop-on-error": true
}
```
During parsing, each entry becomes an indexed hash (`values["1"]["conditions"]["all"] = "2.5"` etc.), ensuring substitutions happen in a predictable order.

## Mapping Conventions
- Strings wrapped in angle brackets (e.g., `<Opt-ACH>`) are a historical cue that the tag is handled specially in `processFile`. In practice they behave like normal tags, but the naming convention helps locate the relevant branch.
- Values of `"NA"` tell the substitution logic to skip modification for that particular HOT2000 field.
- Multi-context maps: some options include additional keys besides `base` (for example, staged foundation tweaks). The parser simply iterates each key and flattens them into the internal structure, so you can add contexts like `"ERS": { ... }` if the downstream code checks for them.

## Cost Metadata
When `costed` is true, include a `costs` object inside each option:
- `components`: Array of component IDs looked up in `HTAPUnitCosts.json` and multiplied by the appropriate surface areas from `H2KFile.getAllInfo`.
- `custom-costs`: Arbitrary key/value pairs for manual adjustments (e.g., `{ "labour": 1200, "markup": 15 }`). `Costing.computeCosts` merges these into the final summary.
- `proxy`: Optional string alias pointing to another option’s cost bundle. Use this when several selections share identical costing logic.
If you omit the `costs` block for a costed attribute, the costing pipeline treats the option as zero-cost.

## Integration Points
- `substitute-h2k.rb` calls `HTAPData.parse_json_options_file` to build `$gOptions` and `$gChoiceOrder`. Tree attributes translate into tag/value instructions executed by `processFile`. Flat attributes surface as direct lookups in conditional branches.
- `HTAPData.validate_options` ensures user-supplied choices exist, applies defaults, and honours `stop-on-error` when invalid data is encountered. The validation output also feeds pattern expansion in `.run` files (wildcards in run definitions are matched against the `options` keys defined here).
- Costing (`Costing.computeCosts` / `estimateCosts`) reads the `costed`, `components`, `custom-costs`, and `proxy` metadata to assemble capital cost schedules.
- Ruleset packages (`HTAP-rulesets.json`) reference attribute/choice names defined in this file. Any rename here must be reflected in the ruleset bundle and existing `.choices` templates.

## Editing Guidelines
- Keep attribute names stable and unique. Choose the `Opt-` prefix for scenario inputs, `GO` for global configuration toggles, and reserve leading `!` names (e.g., `!Opt-Archetype`) for manager-only bookkeeping.
- Always update `h2kSchema` when you add or remove tags in a tree attribute so index ordering stays deterministic.
- Supply a `default` whenever the option has a sensible baseline—`validate_options` will auto-fill it when the choice is omitted.
- Use double backslashes (`\\`) for Windows paths; the file is consumed by Ruby on Windows and needs escaped separators.
- If you introduce new costing components, add matching entries in `HTAPUnitCosts.json` and ensure any proxies point to valid component identifiers.
- Large edits can break wildcard expansion or run definitions. After modifications, run `ruby util\misc-dev-tests.rb` or a sample `htap-prm.rb` job to confirm parsing succeeds.

## Practical Usage Patterns
- When crafting `.choices` files, match the option keys exactly (case-sensitive). For example, `Opt-ACH : ACH_NBC` pulls the `ACH_NBC` object above.
- `.run` files enumerate combinations by listing these option keys; the run manager expands them into `.choices` files based on what `HTAP-options.json` allows.
- To add a brand new attribute, start from an existing tree or flat template, confirm `structure`/`h2kSchema` align with how you plan to edit the HOT2000 XML, and test with `substitute-h2k.rb --export-options-to-json` to verify round-tripping.
- Avoid deleting unused options outright if they appear in archived `.choices` or rulesets; instead, set `stop-on-error: false` and map the option to a fallback value, or update the dependent artifacts in tandem.

## References in Code
- Parsing: `inc/H2KUtils.rb` (`HTAPData.parse_json_options_file`).
- Validation: `substitute-h2k.rb` (`HTAPData.validate_options`).
- Costing: `substitute-h2k.rb` (`estimateCosts`), `inc/costing.rb`.
- Run manager expansion: `htap-prm.rb` (`parse_def_file`, `create_mesh_cartisian_combos`).
