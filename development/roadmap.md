# HTAP Configuration Editor - Development Roadmap

## 🎯 Project Overview
A Streamlit-based 3-panel editor for managing HTAP run configurations, eliminating the need to manually switch between multiple JSON files.

## 📊 Project Status
**Start Date:** 2025-10-09
**Target MVP:** 3 weeks
**Current Phase:** Planning

---

## 🏗️ Development Phases

### Phase 1: Foundation (Week 1)
Setting up core infrastructure and data loading capabilities.

- [ ] **Task 1.1:** Project Setup & Dependencies
- [ ] **Task 1.2:** Data Models & Loading
- [ ] **Task 1.3:** Basic UI Layout
- [ ] **Task 1.4:** Run File Parser
- [ ] **Task 1.5:** Options Data Structure

### Phase 2: Core Functionality (Week 2)
Implementing the main interaction flows.

- [ ] **Task 2.1:** Dynamic Panel Interactions
- [ ] **Task 2.2:** Option Selection Logic
- [ ] **Task 2.3:** Cost Component Management
- [ ] **Task 2.4:** Create New Option Feature
- [ ] **Task 2.5:** Session State Management

### Phase 3: Export & Polish (Week 3)
Finalizing export capabilities and user experience.

- [ ] **Task 3.1:** Export Run File
- [ ] **Task 3.2:** Export Options Snapshot
- [ ] **Task 3.3:** Validation & Warnings
- [ ] **Task 3.4:** Performance Optimization
- [ ] **Task 3.5:** Error Handling & Testing

---

## 📋 Task Details

### Phase 1: Foundation

#### Task 1.1: Project Setup & Dependencies (2-3 hours)
- Create project structure
- Set up virtual environment
- Install dependencies (Streamlit, pandas, etc.)
- Create requirements.txt
- Basic README.md

#### Task 1.2: Data Models & Loading (3-4 hours)
- Create Pydantic models for Options, Costs, RunConfig
- Implement JSON parsers for HTAP-options.json
- Implement JSON parser for HTAPUnitCosts.json
- Add caching layer for large files
- Unit tests for data loading

#### Task 1.3: Basic UI Layout (2-3 hours)
- Create 3-column Streamlit layout
- Add file upload widget for .run import
- Create placeholders for each panel
- Basic styling and headers
- Responsive layout testing

#### Task 1.4: Run File Parser (3-4 hours)
- Parse .run file format
- Extract Opt- elements
- Build run configuration data structure
- Handle malformed files gracefully
- Unit tests for parser

#### Task 1.5: Options Data Structure (2-3 hours)
- Create searchable options index
- Implement filtering by Opt type
- Optimize for 50MB file handling
- Add search functionality
- Performance benchmarking

### Phase 2: Core Functionality

#### Task 2.1: Dynamic Panel Interactions (3-4 hours)
- Wire LEFT → MIDDLE panel updates
- Wire MIDDLE → RIGHT panel updates
- Implement state management
- Add visual selection indicators
- Test interaction flows

#### Task 2.2: Option Selection Logic (3-4 hours)
- Implement option assignment to run
- Update progress indicators
- Handle option replacement
- Add confirmation dialogs
- Persist selections in session

#### Task 2.3: Cost Component Management (4-5 hours)
- Display cost components in RIGHT panel
- Implement add/remove components
- Calculate cost totals
- Show unit costs and sources
- Handle missing components

#### Task 2.4: Create New Option Feature (3-4 hours)
- Add "Create New" button and form
- Validate new option data
- Assign cost components to new options
- Store in session (not modifying source)
- Preview new option details

#### Task 2.5: Session State Management (2-3 hours)
- Implement undo/redo
- Add save/load session
- Handle browser refresh
- Progress auto-save
- Clear/reset functionality

### Phase 3: Export & Polish

#### Task 3.1: Export Run File (3-4 hours)
- Generate .run format from configuration
- Handle all Opt- types correctly
- Include run parameters
- Add timestamps and metadata
- Download functionality

#### Task 3.2: Export Options Snapshot (3-4 hours)
- Export new/modified options only
- Generate proper JSON format
- Include cost component assignments
- Add validation checksums
- Bundle with run file

#### Task 3.3: Validation & Warnings (3-4 hours)
- Check for missing cost components
- Validate option selections
- Display inline warnings
- Create validation summary
- Export validation report

#### Task 3.4: Performance Optimization (2-3 hours)
- Optimize large file loading
- Add progress bars
- Implement lazy loading
- Cache frequently accessed data
- Profile and fix bottlenecks

#### Task 3.5: Error Handling & Testing (3-4 hours)
- Add comprehensive error handling
- Create user-friendly error messages
- Write integration tests
- Test with real HTAP files
- Create troubleshooting guide

---

## 🎯 Milestones

| Milestone | Date | Deliverable |
|-----------|------|-------------|
| **M1: Data Loading** | End of Day 3 | Can load and parse all 3 file types |
| **M2: Basic UI** | End of Week 1 | 3-panel layout with basic interactions |
| **M3: Core Features** | End of Week 2 | Full option selection and cost management |
| **M4: MVP Complete** | End of Week 3 | Export capabilities and polish |

---

## 🚀 Quick Start Commands

```bash
# After each task, run these checks:
pytest tests/          # Run tests
streamlit run app.py   # Test UI
python validate.py     # Check data integrity
```

---

## 📝 Notes

- Each task is designed to be completed in one working session (2-5 hours)
- Tasks within a phase can sometimes be done in parallel
- Dependencies are minimized between tasks
- Focus on MVP features first, enhancements later

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2025-10-09 | Initial roadmap created |