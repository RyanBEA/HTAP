# Costing Module (inc/costing.rb)

## Purpose & Scope
- Provides the cost engine that translates HTAP option selections into capital-cost estimates, pulling unit pricing from HTAPUnitCosts.json and geometry metrics from H2KFile.getAllInfo.
- Consumed primarily by substitute-h2k.rb (stimateCosts) but also supports stand-alone costing/audit workflows.

## Key Data Inputs
- **Options catalogue** (HTAP-options.json processed into myOptions) ? defines costComponents, custom-costs, and optional costProxy values for each attribute/choice.
- **Unit cost database** (HTAPUnitCosts.json) ? structured as data[component][source] => {category, units, UnitCostMaterials, UnitCostLabour, ...}.
- **Choice set** (myChoices) ? validated attribute?choice map for the current run.
- **House descriptors** (myH2KHouseInfo) ? geometry/system hash from H2KFile.getAllInfo, used to scale units (e.g., sf of wall).
- **Regional factors** ? $RegionalCostFactors adjust costs by city unless a custom multiplier is provided.

## Primary Functions
- parseUnitCosts(path) ? JSON loader with basic error handling. Returns the nested hash used throughout costing.
- getCostComponentList(options, choices, attribute, choice) ? Resolves the list of cost component IDs for an attribute/choice, following costProxy chains recursively until a concrete component list is found.
- solveComponentConditionals(options, choices, attribute, component, house_info) ? Evaluates conditional component definitions. Supports lookups against H2KHouseInfo/... (geometry/system values) and HTAPOptions/... metadata, using HTAPData.simpleConditional to compare values.
- esolveCostingLogic(options, choices, house_info) ? Produces a simplified attribute?component tree after applying proxies and conditionals. Downstream calls reuse this pre-processed structure.
- getCosts(unit_costs, simplified_options, attribute, choice, sources) ? Retrieves pricing metadata for each component, honouring source precedence (mySpecdSrc["components"]) and inheriting defaults when a component is found in a different source set.
- computeCosts(spec_sources, unit_costs, options, choices, house_info) ? Main entry point. For each cost-supported attribute (CostingSupport set defined in inc/constants.rb):
  - Calls getCosts to pull unit pricing.
  - Determines the quantity measure based on attribute/unit pairs (e.g., wall area, ceiling area, number of windows) using house_info.
  - Applies regional cost factors (unless overridden) and accumulates totals by attribute, source, and building component.
  - Populates an udit structure capturing per-component detail for reports.
- getAttributeComponents, uditComponents, uditCosts ? Build textual or structured audit outputs for reporting/CSV export. uditCosts returns formatted strings (or JSON when requested) describing cost drivers per attribute.
- summarizeCosts(choices, costs, format="txt") ? Constructs a concise summary table for the run log or console.
- isExteriorInsulaiton(component) ? Helper to tag exterior insulation costing elements so wall-area calculations include headers correctly.

## Workflow Summary
1. substitute-h2k.rb (when --auto-cost-options) loads unit costs via parseUnitCosts and retrieves geometry with H2KFile.getAllInfo.
2. esolveCostingLogic expands each selected choice into concrete cost components, applying proxies and conditionals.
3. computeCosts iterates over the supported attributes, measures the appropriate surface counts (m?, t?, a, etc.), multiplies by material/labour unit costs, and aggregates totals.
4. Results are stored in $costEstimates, with totals in costs["total"], attribute slices in costs["byAttribute"], and detailed justification in costs["audit"] for audits/JSON output.

## Cost Multipliers & Sources
- Regional adjustments default to $RegionalCostFactors[locale]. If $gCustomCostAdjustment is set elsewhere, callers can override before invoking costing.
- Component sources are prioritised by mySpecdSrc["components"] (e.g., MiscNRCanEstimates2019, LEEP-BC-Vancouver). Components missing from the preferred source fall back to other defined sources (noted as inherited in the audit trail).
- mySpecdSrc["custom"] allows injecting bespoke cost entries (currently a placeholder for future extensions).

## Output Structure (myCosts)
- 	otal ? Aggregate cost delta.
- yAttribute ? Costs grouped by HTAP attribute (e.g., Opt-ACH).
- ySource ? Totals per cost source database.
- yBuildingComponent ? Categorised sums (e.g., insulation vs. mechanical) derived from component metadata.
- udit ? Nested hash capturing each component?s cost, units, quantity, source, and descriptive text (used by uditCosts and JSON exports).

## Integration Points
- substitute-h2k.rb ? Calls computeCosts, then serialises myCosts into the JSON result (cost-estimates) or audit reports (HTAP-cost-audit.txt).
- HTAPData.prepareResult4Json ? Reads cost-estimates to embed costing summaries in h2k_run_results.json.
- Reporting scripts rely on summarizeCosts and uditCosts for human-readable output.

## Authoring Tips
- When adding new options in HTAP-options.json, include "costed": true and populate costs.components to make them cost-able. Update CostingSupport in inc/constants.rb if the new attribute should be part of costing.
- Ensure unit labels in HTAPUnitCosts.json match the cases handled in computeCosts (e.g., "sf wall", "ea"). Add new measurement handlers where needed to avoid costsOK = false warnings.
- Test costing changes with --auto-cost-options --unit-cost-db path/to/HTAPUnitCosts.json to confirm no components fall back to 
o_costs_defined.
