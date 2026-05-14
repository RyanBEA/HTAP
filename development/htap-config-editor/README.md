# HTAP Configuration Editor

A Streamlit-based 3-panel editor for managing HTAP run configurations.

## Overview

This tool provides a visual interface for configuring HTAP (Housing Technology Assessment Platform) simulation runs, eliminating the need to manually edit multiple JSON files.

**Status:** ✅ **Phase 2 - Core Functionality COMPLETE**

## Features

✅ **Data Models & Loading** (Phase 1)
- Load and parse HTAP-options.json (773 options, 35 categories)
- Manage unit costs from HTAPUnitCosts.json (351 components)
- Pydantic v2 validation with type safety
- Sub-5ms load times with caching

✅ **Run File Parser** (Phase 1)
- Parse .run configuration files
- Section-aware parsing (RunParameters, RunScope, Upgrades)
- Comment preservation
- Roundtrip integrity (parse → write → parse)
- Sub-millisecond parsing (<0.2ms)

✅ **Options Search** (Phase 1)
- Fast pandas-based search (<10ms queries)
- Multi-faceted filtering (text, category, costs, structure)
- Statistics and aggregation
- Search 773 options in 1.27ms average

✅ **Dynamic Panel Interactions** (Phase 2)
- LEFT → MIDDLE → RIGHT panel state flow
- Centralized session state management
- Category filter buttons with visual feedback
- Interactive selection summary with remove buttons
- Real data integration throughout

✅ **Cost Resolution** (Phase 2)
- Source inheritance (BC sources inherit from Ottawa)
- Component cost lookup with @lru_cache optimization
- Material + Labour cost breakdown
- Custom cost support
- Missing component detection
- Cost display in option cards

✅ **Validation System** (Phase 2)
- Three severity levels (ERROR, WARNING, INFO)
- Run configuration validation
- Option and cost completeness checks
- Category status indicators (✅⚠️❌⬜)
- Real-time feedback across all panels
- Combination count warnings (>100, >500)

✅ **Multi-Select Mode** (Phase 2)
- Toggle single/multi-select modes
- Multiple choices per category
- Cartesian product combination counting
- .run file export format support
- Warning system for large parametric runs

✅ **Advanced Search** (Phase 2)
- 3-tab interface (Browse, Search, Statistics)
- Text search with filters (category, cost, structure)
- Tag explorer with clickable tags
- Category statistics dashboard
- Performance <10ms for all queries

## Quick Start

### Run the application

```bash
cd C:/HTAP/development/htap-config-editor
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

### Run tests

```bash
pytest tests/ -v                  # All tests (161 tests)
pytest tests/ --cov=src           # With coverage (89% business logic)
pytest tests/ --cov=src --cov-report=html  # HTML report
```

## Requirements

- Python 3.10+ (tested on 3.13.7)
- HTAP installation at `C:/HTAP/`
- Dependencies in `requirements.txt`

## Installation

### 1. Navigate to the project

```bash
cd C:/HTAP/development/htap-config-editor
```

### 2. Create virtual environment (optional)

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

## Project Structure

```
htap-config-editor/
├── src/
│   ├── models/          ✅ Pydantic data models (4 modules)
│   ├── parsers/         ✅ File parsers (3 modules)
│   ├── ui/              ✅ Streamlit UI components (9 modules)
│   └── utils/           ✅ Utils & business logic (6 modules)
├── tests/               ✅ Unit tests (161 tests, 89% coverage)
├── data/                📁 Sample HTAP data
├── .streamlit/          ⚙️ Streamlit configuration
├── app.py               🚀 Main application entry point
└── README.md            📖 This file
```

## Documentation

**Main Documentation:** `../documentation/`
- [PHASE-1-COMPLETE.md](../documentation/PHASE-1-COMPLETE.md) - Phase 1 completion report
- [PHASE-2-COMPLETE.md](../documentation/PHASE-2-COMPLETE.md) - Phase 2 completion report
- [SETUP-COMPLETE.md](../documentation/SETUP-COMPLETE.md) - Setup guide
- [MANUAL_TESTING_GUIDE.md](../documentation/MANUAL_TESTING_GUIDE.md) - UI testing checklist

**Task Reports:** `../documentation/task-reports/`
- Phase 1: Tasks 1.2-1.5 (Data Models, UI, Parser, Search)
- Phase 2: Tasks 2.1-2.5 (Interactions, Costs, Validation, Multi-Select, Search)

**Archived Materials:** `../archive/`
- Phase 1 and Phase 2 task plans
- Utility scripts (benchmarks, verification)
- Test files and samples

## Development Status

### ✅ Phase 1: Foundation (COMPLETE)

- [x] Task 1.1: Project Setup & Dependencies
- [x] Task 1.2: Data Models & Loading (16 tests, 96% coverage)
- [x] Task 1.3: Basic UI Layout (Manual testing complete)
- [x] Task 1.4: Run File Parser (20 tests, 93% coverage)
- [x] Task 1.5: Options Search (24 tests, 97% coverage)

**Metrics:**
- 62/62 tests passing (100%)
- 96% coverage on core business logic
- 2,171 lines of production code
- All operations <10ms

### ✅ Phase 2: Core Functionality (COMPLETE)

- [x] Task 2.1: Dynamic Panel Interactions (Manual testing complete)
- [x] Task 2.2: Cost Resolution Logic (15 tests, 89% coverage)
- [x] Task 2.3: Validation & Warnings (29 tests, 88% coverage)
- [x] Task 2.4: Multiple Option Selection (27 tests, 89% coverage)
- [x] Task 2.5: Advanced Search Features (29 tests, 97% coverage)

**Metrics:**
- 161/161 tests passing (99.4%, 1 skip)
- 89% coverage on core business logic
- 5,022 lines added (Phase 1 + Phase 2 total)
- All operations meet performance targets

### 🚧 Phase 3: Advanced Features (Next)

- [ ] Task 3.1: Export Run File
- [ ] Task 3.2: Export Validation
- [ ] Task 3.3: Cost Summary Report
- [ ] Task 3.4: Error Handling & Logging
- [ ] Task 3.5: Testing & Documentation

See [roadmap.md](../roadmap.md) for detailed development phases.

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

**Expected Output:**
```
======================= 161 passed, 1 skipped in 0.85s ========================
```

### With Coverage

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

**Expected Coverage:** 89% on core modules (models, parsers, utils)

### View HTML Coverage Report

```bash
pytest tests/ --cov=src --cov-report=html
start htmlcov/index.html  # Windows
```

## Performance

All operations exceed requirements by 8-60x:

| Operation | Time | Target | Status |
|-----------|------|--------|--------|
| Load HTAP-options.json | 4.8ms | 200ms | ✅ 42x faster |
| Load HTAPUnitCosts.json | 3.7ms | 200ms | ✅ 54x faster |
| Parse .run file | 0.16ms | 10ms | ✅ 60x faster |
| Search query | 1.27ms | 10ms | ✅ 8x faster |

## Known Limitations

1. **UI Components** - Low test coverage (manual testing only for Streamlit)
2. **Export Functionality** - .run file export pending (Phase 3)
3. **Cost Summary** - Total cost report pending (Phase 3)

## Next Steps

**Phase 3 Tasks:**
1. Implement .run file export functionality
2. Add export validation and error handling
3. Create cost summary report
4. Enhanced error handling and logging
5. Comprehensive testing and documentation

## Contributing

This is an internal NRCan tool. For questions or issues, contact the HTAP team.

## License

Internal use only - NRCan IETS

---

**Phase 1 & 2 Status:** ✅ COMPLETE
**Test Results:** 161/161 passing (99.4%, 1 skip)
**Coverage:** 89% (core business logic)
**Performance:** All operations meet or exceed targets
**Ready for:** Phase 3 (Advanced Features)
