# Application Modules (inc/application_modules.rb)

## Purpose & Scope
- Collects domain-specific helpers that sit on top of core HTAP utilities.
- Currently implements:
  - **BCStepCode** ? logic for mapping climate zones and TEDI values to Step Code tiers.
  - **LEEPPathways** ? tooling to export HTAP run results into the LEEP Pathways CSV format (archetypes, locations, ECMs, runs).

## BCStepCode
- Constants BC_STEP_TEDI_MAX define maximum TEDI (kWh/m??yr) per Step Code tier for climate zones 4?8, matching Technical Bulletin B18-08.
- getStepByTEDI(climate_zone, tedi):
  - Validates the climate zone (calls help_out/atalerror if unknown).
  - Iterates the thresholds to find the highest step that still satisfies the TEDI requirement.
  - Returns a human-readable string (e.g., "Step 3").
- Typical usage: after a simulation, feed the computed TEDI and climate zone to classify compliance or report Step Code level.

## LEEPPathways Overview
- Designed to produce four CSVs expected by the LEEP Pathways tool:
  - Pathways_ListOfECMs.csv
  - Pathways_HTAPArchetypeData.csv
  - Pathways_HTAPLocationData.csv
  - Pathways_HTAPRunData.csv
- Uses a combination of global buffers ($LEEParchetypeDataBuffer, $LEEPecmDataBuffer, etc.) and persistent arrays ($LEEParchetypeData, $LEEPecmData, ?) to accumulate run data across batches.
- Requires flattened result JSON (prepareResult4Json) as input for ExtractPathwayData.

## LEEPPathways Data Maps
- PathwaysECMs ? maps attribute/choice pairs to canonical ECM IDs (e.g., Opt-ACH:+:New-Const-air_seal_to_1.50_ach ? lpACH_03). Unknown combinations receive generated IDs (id-<n>_X).
- GoodArchFields, GoodLocFields, GoodRunFields, GoodECMFields ? curated header lists passed to convertToCSV so exports have consistent column order.

## Core Functions
- EmptyBuffers() ? resets the per-batch buffers before processing a new chunk of runs (called by htap-prm each batch).
- OpenOutputFiles(mode="overwrite"|"append") ? opens CSV targets. In append mode it rehydrates previous data by parsing existing CSVs (ReconstituteDataStructure) and restores ECM/location/archetype sets.
- ExtractPathwayData(result) ? ingests a single HTAP result hash when the run succeeds:
  - Uses HTAPData.getOptionsData() to resolve proxies when needed.
  - Calls getArchID / getLocID to register archetype and location records (deduplicated via hashed keys).
  - Flattens input/configuration/output/costing dimensions into the run record and assigns incremental unID values.
  - Calls getECMs to translate selected options into ECM IDs.
- ExportPathwayData() ? writes buffered archetype/location/run/ECM records to disk via convertToCSV, respecting header printing on the first batch only.
- CloseOutputFiles() ? flushes and closes all file handles at the end of a job.
- ReconstituteDataStructure(csv_text) ? basic CSV parser that rebuilds an array of hashes (first row as header). Used in append mode to continue from previous output.
- getArchID(result) / getLocID(result) ? manage deduplication and ID assignment for archetypes and locations, storing dimension data (lattenHash) for reuse.
- getECMs(input_hash) ? loops over result inputs, matches against PathwaysECMs (or previously cached ECM records), creates IDs as needed, and returns a ;-delimited string of ECM identifiers.
- ListContainsID(id, list_string) ? helper for presence checks in semicolon-delimited ID lists.

## Integration Workflow
1. htap-prm.rb enables LEEP exports when --LEEP-Pathways is specified. It calls:
   - LEEPPathways.OpenOutputFiles (overwrite on first run, append for resumes).
   - LEEPPathways.EmptyBuffers at the start of each batch.
2. After each successful substitute-h2k run, PRM feeds the parsed JSON result to ExtractPathwayData.
3. Once the batch finishes, ExportPathwayData writes buffered records and clears per-batch caches.
4. At job completion CloseOutputFiles releases the CSV handles.

## Practical Notes
- LEEP exports rely on costing dimensions (cost-estimates["costing-dimensions"]) and geography data (esult["input"]["Run-Locale"]); ensure costing is enabled and results contain those fields.
- PathwaysECMs only covers common combinations; adding new HTAP options may require extending this map so ECM IDs align with LEEP expectations.
- Global variables ($LEEParchetypeData, $LEEPrunData, etc.) live in process memory; avoid concurrent runs in the same Ruby VM when using LEEP exports.
- CSV parsing in append mode assumes Windows-style newline-separated rows without embedded commas; if custom fields include commas, update ReconstituteDataStructure accordingly.
- Climate-zone calculations for Step Code classification (BCStepCode) are often paired with LEEP exports, so ensure $HDDs and climate-zone are populated in the JSON results.
