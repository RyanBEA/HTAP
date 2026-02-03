---
name: nbc-compliance
description: "Generate NBC 2020 Energy Compliance Forms from HOT2000 (.h2k) building models. Use when user asks to: generate compliance forms, create NBC reports, process h2k files for code compliance, or run the compliance workflow. Handles any number of input files with automatic equipment/foundation classification."
---

# NBC Compliance Form Workflow

Generate NBC 2020 Energy Compliance Forms from HOT2000 building models with automatic reference house selection.

## Workflow

### Phase 1: Analyze Inputs
Run the analyzer to classify input files by equipment type:
```bash
python complianceReporting/skills/nbc-workflow/scripts/h2k_analyzer.py <input_dir>
```
Output: JSON with runfile groupings, manual intervention flags, and summary.

### Phase 2: Generate Reference Houses
Run HTAP batch for each fuel-type group identified in Phase 1:
```bash
ruby htap-prm.rb --run-def <project>/referencehouse_T1gasfurnace_T2ASHP.run --threads 4 --json --keep-all-files
ruby htap-prm.rb --run-def <project>/referencehouse_T1elecfurnace_T2ASHP.run --threads 4 --json --keep-all-files
```
Copy archetype files from `HTAP-sim-*/` to `complianceReporting/reference/`. The archetype file is the `.h2k` file matching the input filename (NOT `file-postsub.h2k`, `file-presub.h2k`, or `run_file_file_1.h2k`).

### Phase 3: Generate Proposed Houses
Run HTAP batch with proposed building configuration:
```bash
ruby htap-prm.rb --run-def <project>/proposed.run --threads 4 --json --keep-all-files
```
Copy archetype files from `HTAP-sim-*/` to `complianceReporting/proposed/`. The archetype file is the `.h2k` file matching the input filename (NOT `file-postsub.h2k`, `file-presub.h2k`, or `run_file_file_1.h2k`).

### Phase 4: Manual Checkpoint
Review files flagged for manual intervention:
| Flag | Action Required |
|------|-----------------|
| `pony_wall` | Verify pony wall configuration in reference model |
| `dwhr` | Add DWHR to proposed if present in original |
| `skylights` | Verify skylight areas match between models |
| `heated_floors` | Verify radiant floor configuration |

### Phase 5: Generate Reports
Run batch form generation:
```bash
cd complianceReporting && python process_h2k_to_nbc.py --batch
```
Output: NBC compliance forms in `complianceReporting/output/`.

### Phase 6: Validate
Spot-check key values in generated forms:
- FDWR percentages (Table 3, Table 5)
- Energy consumption totals (Table 11)
- Equipment descriptions in Table 5 (heating, cooling, ventilation, DHW)

## Run File Selection

| Type1 Fuel | Run File |
|------------|----------|
| Natural gas, Propane | `referencehouse_T1gasfurnace_T2ASHP.run` |
| Electric, Baseboard | `referencehouse_T1elecfurnace_T2ASHP.run` |
| Oil | Not yet supported (manual reference house creation required) |

## References

- [XPath Patterns](references/xpath-patterns.md) - Equipment and foundation classification XPaths
- [Batch Workflow](../../doc/batch-compliance-workflow.md) - Detailed step-by-step instructions
- [Field Mapping](../../README.md) - NBC form field mapping documentation

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| No files in runfile group | Unknown fuel type | Check h2k_analyzer output for classification_reason |
| Missing proposed file | Archetype not in proposed.run | Add archetype to RunScope section |
| Form shows "HOT2000" | Placeholder field | 49 fields require manual completion |
