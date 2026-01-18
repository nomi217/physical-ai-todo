---
description: "Task breakdown for Phase I Basic CRUD Operations"
feature: "001-phase-1-basics"
branch: "001-phase-1-basics"
generated: "2025-12-05"
---

# Tasks: Phase I Basic CRUD Operations

**Input**: Design documents from `/specs/001-phase-1-basics/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-commands.md, quickstart.md

**Organization**: Tasks are grouped by implementation layer and feature to enable systematic implementation of the 5 basic CRUD operations.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- User Stories:
  - US1: Create task (add command)
  - US2: View tasks (list command)
  - US3: Update task (update command)
  - US4: Delete task (delete command)
  - US5: Mark complete (complete command)

## Path Conventions

Single project structure (repository root):
- `src/todo/` - Source code
- `tests/` - Test files

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create project structure and basic configuration

- [X] T001 Create src/todo/ directory structure
- [X] T002 Create tests/ directory structure
- [X] T003 [P] Create src/todo/__init__.py package initialization file
- [X] T004 [P] Create tests/__init__.py package initialization file
- [X] T005 [P] Create empty requirements.txt (zero external dependencies)

**Checkpoint**: Project structure ready for implementation

---

## Phase 2: Validation Layer (Foundation)

**Purpose**: Core validation functions needed by all CRUD operations

**⚠️ CRITICAL**: This layer must be complete before storage layer implementation

- [X] T006 [P] Implement validate_title() function in src/todo/models.py
- [X] T007 [P] Implement validate_description() function in src/todo/models.py
- [X] T008 Implement validate_task_data() function in src/todo/models.py (depends on T006, T007)

**Checkpoint**: Validation layer complete - storage layer can begin

---

## Phase 3: Storage Layer (CRUD Operations)

**Purpose**: Implement in-memory storage and all CRUD operations

**Dependencies**: Requires Phase 2 (validation layer) completion

### Module Setup

- [X] T009 Create module-level storage (_tasks list and _next_id counter) in src/todo/storage.py
- [X] T010 [P] Import models module and datetime in src/todo/storage.py

### User Story 1: Create Task (Add)

- [X] T011 [US1] Implement add_task() function in src/todo/storage.py

### User Story 2: View Tasks (List)

- [X] T012 [P] [US2] Implement list_tasks() function in src/todo/storage.py
- [X] T013 [P] [US2] Implement get_task() helper function in src/todo/storage.py

### User Story 3: Update Task

- [X] T014 [US3] Implement update_task() function in src/todo/storage.py (depends on T013)

### User Story 4: Delete Task

- [X] T015 [US4] Implement delete_task() function in src/todo/storage.py

### User Story 5: Mark Complete

- [X] T016 [US5] Implement mark_complete() function in src/todo/storage.py

### Testing Utilities

- [X] T017 [P] Implement reset_storage() function for testing in src/todo/storage.py

**Checkpoint**: All CRUD operations implemented - CLI layer can begin

---

## Phase 4: CLI Layer (Command-Line Interface)

**Purpose**: Implement argparse-based CLI for all 5 commands

**Dependencies**: Requires Phase 3 (storage layer) completion

### CLI Infrastructure

- [X] T018 Import argparse, sys, and storage module in src/todo/app.py
- [X] T019 [P] Implement format_task() display function in src/todo/app.py
- [X] T020 [P] Implement format_task_table() display function in src/todo/app.py
- [X] T021 Create main() function with argparse parser setup in src/todo/app.py

### User Story 1: Add Command

- [X] T022 [US1] Implement cmd_add() command handler in src/todo/app.py
- [X] T023 [US1] Configure 'add' subparser with title and --description arguments in src/todo/app.py

### User Story 2: List Command

- [X] T024 [P] [US2] Implement cmd_list() command handler in src/todo/app.py
- [X] T025 [P] [US2] Configure 'list' subparser in src/todo/app.py

### User Story 3: Update Command

- [X] T026 [P] [US3] Implement cmd_update() command handler in src/todo/app.py
- [X] T027 [P] [US3] Configure 'update' subparser with id, --title, --description arguments in src/todo/app.py

### User Story 4: Delete Command

- [X] T028 [P] [US4] Implement cmd_delete() command handler in src/todo/app.py
- [X] T029 [P] [US4] Configure 'delete' subparser with id argument in src/todo/app.py

### User Story 5: Complete Command

- [X] T030 [P] [US5] Implement cmd_complete() command handler in src/todo/app.py
- [X] T031 [P] [US5] Configure 'complete' subparser with id and --incomplete arguments in src/todo/app.py

### CLI Entry Point

- [X] T032 Add argument parsing and command routing to main() in src/todo/app.py
- [X] T033 Add if __name__ == '__main__': main() entry point in src/todo/app.py

**Checkpoint**: All 5 CLI commands implemented - ready for testing

---

## Phase 5: Testing (80%+ Coverage Target)

**Purpose**: Comprehensive test suite for storage and CLI layers

**Dependencies**: Requires Phase 3 and Phase 4 completion

### Unit Tests (Storage Layer)

- [X] T034 Create test class setup with reset_storage() in tests/test_storage.py
- [X] T035 [P] [US1] Implement test_add_task_success in tests/test_storage.py
- [X] T036 [P] [US1] Implement test_add_task_empty_title_fails in tests/test_storage.py
- [X] T037 [P] [US1] Implement test_add_task_long_title_fails in tests/test_storage.py
- [X] T038 [P] [US2] Implement test_list_tasks_empty in tests/test_storage.py
- [X] T039 [P] [US2] Implement test_list_tasks_with_data in tests/test_storage.py
- [X] T040 [P] [US3] Implement test_update_task_success in tests/test_storage.py
- [X] T041 [P] [US3] Implement test_update_nonexistent_task_fails in tests/test_storage.py
- [X] T042 [P] [US4] Implement test_delete_task_success in tests/test_storage.py
- [X] T043 [P] [US4] Implement test_delete_nonexistent_task_fails in tests/test_storage.py
- [X] T044 [P] [US5] Implement test_mark_complete_success in tests/test_storage.py
- [X] T045 [P] [US5] Implement test_mark_incomplete_success in tests/test_storage.py
- [X] T046 [P] Implement test_id_not_reused_after_delete in tests/test_storage.py

### Integration Tests (CLI Layer)

- [X] T047 Create test class with CLI helper function in tests/test_cli.py
- [X] T048 [P] [US1] Implement test_add_command_success in tests/test_cli.py
- [X] T049 [P] [US1] Implement test_add_command_empty_title_fails in tests/test_cli.py
- [X] T050 [P] [US2] Implement test_list_command_empty in tests/test_cli.py
- [X] T051 [P] [US2] Implement test_list_command_with_tasks in tests/test_cli.py
- [X] T052 [P] [US5] Implement test_complete_command_success in tests/test_cli.py
- [X] T053 [P] [US3] Implement test_update_command_success in tests/test_cli.py
- [X] T054 [P] [US4] Implement test_delete_command_success in tests/test_cli.py

### Test Execution & Validation

- [X] T055 Run all tests: python -m unittest discover tests
- [X] T056 Verify 80%+ coverage manually (all functions in app.py, storage.py, models.py tested)
- [X] T057 Fix any failing tests and re-run until all pass

**Checkpoint**: All tests passing, 80%+ coverage achieved

---

## Phase 6: Manual Testing & Documentation

**Purpose**: End-to-end validation and user documentation

**Dependencies**: Requires Phase 5 (tests passing) completion

### Manual Testing Scenarios

- [X] T058 [P] [US1] Test add command: python -m todo.app add "Buy groceries" -d "Milk, eggs"
- [X] T059 [P] [US1] Test add command edge cases (long title, special characters, unicode)
- [X] T060 [P] [US2] Test list command with empty list and populated list
- [X] T061 [P] [US5] Test complete command: mark task complete and incomplete
- [X] T062 [P] [US3] Test update command: update title, description, and both
- [X] T063 [P] [US4] Test delete command and verify ID not reused
- [X] T064 Test help command: python -m todo.app --help and subcommand help

### Documentation

- [X] T065 [P] Update README.md with installation instructions
- [X] T066 [P] Update README.md with usage examples for all 5 commands
- [X] T067 [P] Update README.md with Phase I limitations (in-memory only)

### Final Validation

- [X] T068 Verify all 5 user stories work end-to-end
- [X] T069 Verify constitution compliance (zero dependencies, 80%+ coverage, all requirements met)
- [X] T070 Run quickstart.md validation checklist

**Checkpoint**: Phase I implementation complete and validated

---

## Dependencies & Execution Order

### Phase Dependencies (Sequential)

1. **Phase 1: Setup** → No dependencies - can start immediately
2. **Phase 2: Validation Layer** → Depends on Phase 1 completion - BLOCKS storage layer
3. **Phase 3: Storage Layer** → Depends on Phase 2 completion - BLOCKS CLI layer
4. **Phase 4: CLI Layer** → Depends on Phase 3 completion - BLOCKS testing
5. **Phase 5: Testing** → Depends on Phase 3 & 4 completion
6. **Phase 6: Documentation** → Depends on Phase 5 completion (tests passing)

### Within Each Phase (Parallel Opportunities)

**Phase 1 (Setup)**: T003, T004, T005 can run in parallel

**Phase 2 (Validation)**: T006, T007 can run in parallel

**Phase 3 (Storage)**:
- T010 parallel with T009
- T012, T013 can run in parallel (both US2)
- T017 can run in parallel with any other storage task

**Phase 4 (CLI)**:
- T019, T020 can run in parallel
- Command pairs can run in parallel: (T024, T025), (T026, T027), (T028, T029), (T030, T031)

**Phase 5 (Testing)**:
- All unit tests (T035-T046) can run in parallel (different test functions)
- All integration tests (T048-T054) can run in parallel (different test functions)

**Phase 6 (Manual Testing & Docs)**:
- All manual testing tasks (T058-T064) can run in parallel
- All documentation tasks (T065-T067) can run in parallel

### User Story Coverage

- **US1 (Create Task)**: T011, T022, T023, T035-T037, T048, T049, T058, T059
- **US2 (View Tasks)**: T012, T013, T024, T025, T038, T039, T050, T051, T060
- **US3 (Update Task)**: T014, T026, T027, T040, T041, T053, T062
- **US4 (Delete Task)**: T015, T028, T029, T042, T043, T054, T063
- **US5 (Mark Complete)**: T016, T030, T031, T044, T045, T052, T061

---

## Implementation Strategy

### Sequential Implementation (Recommended for Single Developer)

1. Complete **Phase 1: Setup** (T001-T005)
2. Complete **Phase 2: Validation Layer** (T006-T008) - CRITICAL BLOCKER
3. Complete **Phase 3: Storage Layer** (T009-T017) - Implement all CRUD operations
4. Complete **Phase 4: CLI Layer** (T018-T033) - Implement all 5 commands
5. Complete **Phase 5: Testing** (T034-T057) - Achieve 80%+ coverage
6. Complete **Phase 6: Manual Testing & Docs** (T058-T070) - Final validation

**Validation Points**:
- After Phase 2: Run simple validation tests on models.py functions
- After Phase 3: Test storage functions with Python REPL
- After Phase 4: Test each CLI command manually
- After Phase 5: All automated tests must pass
- After Phase 6: Complete end-to-end validation

### Parallel Opportunities (If Multiple Developers)

Once Phase 2 (Validation Layer) is complete:

**Developer A**: Phase 3 (Storage Layer) - T009-T017
**Developer B**: Phase 4 (CLI Layer) infrastructure - T018-T021

Wait for Phase 3 completion, then:

**Developer A**: Phase 5 (Unit Tests) - T034-T046
**Developer B**: Phase 4 (Command Handlers) - T022-T033

Wait for both, then:

**Developer A**: Phase 5 (Integration Tests) - T047-T057
**Developer B**: Phase 6 (Documentation) - T065-T067

Both: Phase 6 (Manual Testing) - T058-T064

---

## Task Statistics

- **Total Tasks**: 70
- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Validation)**: 3 tasks
- **Phase 3 (Storage)**: 9 tasks (US1: 1, US2: 2, US3: 1, US4: 1, US5: 1, shared: 3)
- **Phase 4 (CLI)**: 16 tasks (US1: 2, US2: 2, US3: 2, US4: 2, US5: 2, shared: 6)
- **Phase 5 (Testing)**: 24 tasks (13 unit tests, 8 integration tests, 3 validation)
- **Phase 6 (Documentation)**: 13 tasks (7 manual testing, 3 documentation, 3 validation)

- **Parallel Tasks**: 42 tasks marked [P] (60% of total)
- **Sequential Tasks**: 28 tasks with dependencies

**Coverage by User Story**:
- US1 (Create): 11 tasks
- US2 (View): 10 tasks
- US3 (Update): 8 tasks
- US4 (Delete): 8 tasks
- US5 (Complete): 8 tasks
- Shared/Infrastructure: 25 tasks

---

## Notes

- **[P] marker**: Tasks that can run in parallel (different files, no shared state)
- **[Story] marker**: Maps task to specific user story for traceability
- **File paths**: All paths are exact and match quickstart.md implementation guide
- **Testing**: All tests follow unittest framework (standard library)
- **Dependencies**: Zero external dependencies (constitution requirement)
- **Coverage**: Target 80%+ line coverage (constitution requirement)
- **Validation**: Each phase has checkpoint for verification before proceeding
- **Commit strategy**: Commit after each phase completion or logical task group
- **Constitution**: All tasks comply with Phase I requirements (no Phase II features)

---

## Success Criteria

Phase I is complete when all checkpoints pass:

- ✅ **Setup**: Project structure created (src/todo/, tests/)
- ✅ **Validation**: All validation functions working correctly
- ✅ **Storage**: All 5 CRUD operations implemented and working
- ✅ **CLI**: All 5 commands (add, list, update, delete, complete) functional
- ✅ **Testing**: All tests passing with 80%+ coverage
- ✅ **Documentation**: README.md complete with usage instructions
- ✅ **Manual Testing**: All user stories verified end-to-end
- ✅ **Constitution**: Zero dependencies, all Phase I requirements met
- ✅ **Quality**: No Phase II features, clean code, proper error handling

---

## Next Steps

After tasks.md generation:

1. Review task breakdown for completeness
2. Run `/sp.implement` to begin automated implementation
3. Execute tasks in order (or parallelize where marked [P])
4. Validate at each checkpoint
5. Create git commit after all tests pass
6. Document implementation in PHR

**Ready for**: `/sp.implement` command to execute task-by-task implementation
