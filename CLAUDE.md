# Claude Code Guidelines for HTAP

## Project Overview
HTAP (Housing Technology Assessment Platform) is a Ruby-based energy modeling tool that wraps HOT2000 CLI for batch processing and analysis. It transforms building models through parametric/mesh/sample studies with automated costing and performance evaluation.

## Core Architecture
- **htap-prm.rb** - Parallel run manager for batch processing with threading
- **substitute-h2k.rb** - HOT2000 file transformer that applies option bundles
- **HTAP-options.json** - Master catalog of all available building upgrades
- **inc/** - Shared modules (H2KUtils, costing, hourly analysis)
- **lib/** - HOT2000 CLI support and archetype management
- **testing/** - Sample buildings, weather data, validation cases

## Key Commands
- **Single run**: `ruby substitute-h2k.rb --choices example.choices --options HTAP-options.json`
- **Batch analysis**: `ruby htap-prm.rb --run-def study.run --threads 4 --json`
- **Test/validate**: `ruby util\misc-dev-tests.rb`
- **Setup CLI assets**: `ruby lib\CopyToH2K.rb`
- **Compare results**: `perl util\compare_csv.pl baseline.csv candidate.csv`

## Development Workflow
1. Always run from repository root for correct relative paths
2. Stage HOT2000 CLI at `C:\H2K-CLI-Min` exactly as specified
3. Use deterministic .h2k test files from `testing\h2k-files\`
4. Validate against previous outputs using CSV comparison
5. Capture before/after energy/cost tables for any behavior changes

## File Structure & Types
- **.run files** - Define batch studies (mesh/parametric/sample modes)
- **.choices files** - Specify option selections for single runs
- **.h2k files** - HOT2000 building models (XML format)
- **HTAP-options.json** - Authoritative upgrade catalog with costing
- **HTAPUnitCosts.json** - Component cost database

## Code Style
- Two-space indentation, snake_case methods, SCREAMING_SNAKE_CASE constants
- Double quotes for JSON/interpolation, single quotes otherwise
- Module organization (H2KFile, HTAP2H2K, H2KUtils, etc.)
- Concise comments for policy logic and external assumptions
- Windows-safe paths with double backslashes in JSON

## Testing Strategy
- No unit tests - validation through deterministic HOT2000 runs
- Clone existing test cases and modify incrementally
- Compare CSV outputs between baseline and candidate runs
- Archive expected outputs for regression testing
- Use verbose logging for troubleshooting substitution logic

## Dependencies
- Ruby 2.7+
- HOT2000 CLI v11.3+ at `C:\H2K-CLI-Min`
- Perl for CSV comparison utilities
- Text editor (Notepad++ recommended)

## Configuration Management
- Keep HOT2000 CLI assets synced with `ruby lib\CopyToH2K.rb`
- Store proprietary data outside repository
- Document environment variables in doc/ not code
- Use double backslashes for Windows paths in JSON files

## Commit Guidelines
- Imperative mood with scoped prefixes: `inc: update foundation logic`
- Separate data updates from code changes
- Include validation commands and affected files
- Attach energy/cost comparison tables for behavior changes
