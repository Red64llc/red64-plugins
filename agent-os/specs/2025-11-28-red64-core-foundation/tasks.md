# Task Breakdown: Red64 Core Foundation

## Overview

**Total Tasks:** 38 (across 6 task groups)
**Estimated Total Effort:** M-L (medium to large)

This breakdown covers the foundational infrastructure for Red64's context-aware functionality, including project initialization, hook infrastructure, context loading pipeline, and token budget management.

## Task List

---

### Configuration & Schema Layer

#### Task Group 1: Configuration Schema and Initialization Command
**Dependencies:** None
**Effort:** S (Small)

- [ ] 1.0 Complete configuration schema and init command
  - [ ] 1.1 Write 4 focused tests for `/red64:init` command behavior (S)
    - Test: Creates `.red64/` directory structure when missing
    - Test: Generates valid `config.yaml` with default schema
    - Test: Skips overwrite when `config.yaml` already exists (idempotent)
    - Test: Creates subdirectories `product/`, `specs/`, `metrics/`
  - [ ] 1.2 Define configuration schema for `.red64/config.yaml` (XS)
    - Version field: `version: "1.0"`
    - `token_budget` section with `max_tokens`, `overflow_behavior`
    - `context_loader` section with `enabled`, `task_detection`, `file_type_detection`
    - `priorities` section for context item priority levels
    - `features` section for future feature flags
  - [ ] 1.3 Create `/red64:init` command markdown file (S)
    - Location: `plugins/core/commands/red64-init.md`
    - Implement directory creation logic
    - Generate default `config.yaml` from schema
    - Handle idempotent behavior (check existence before creating)
    - Provide clear success/skip messages
  - [ ] 1.4 Ensure configuration tests pass (XS)
    - Run ONLY the 4 tests written in 1.1
    - Verify command behavior matches spec

**Acceptance Criteria:**
- Running `/red64:init` creates `.red64/` with proper structure
- Running `/red64:init` twice does not overwrite existing config
- Generated `config.yaml` matches defined schema exactly
- Clear feedback messages for both new init and skip scenarios

---

### Hook Infrastructure Layer

#### Task Group 2: Hook Configuration and Entry Point
**Dependencies:** Task Group 1
**Effort:** S (Small)

- [ ] 2.0 Complete hook infrastructure
  - [ ] 2.1 Write 3 focused tests for hook configuration (XS)
    - Test: `hooks.json` is valid JSON matching Claude Code hook schema
    - Test: Hook correctly references `context-loader.py` script path
    - Test: Timeout is configured to 30 seconds
  - [ ] 2.2 Configure `hooks/hooks.json` with UserPromptSubmit hook (XS)
    - Location: `plugins/core/hooks/hooks.json`
    - Hook type: `command`
    - Command: `python3 plugins/core/scripts/context-loader.py`
    - Timeout: 30 seconds
  - [ ] 2.3 Create scripts directory structure (XS)
    - Create `plugins/core/scripts/` directory
    - Ensure proper permissions for script execution
  - [ ] 2.4 Ensure hook configuration tests pass (XS)
    - Run ONLY the 3 tests written in 2.1
    - Verify JSON schema compliance

**Acceptance Criteria:**
- `hooks.json` is valid JSON
- Hook matches Claude Code UserPromptSubmit schema
- Script path is correct and accessible
- Timeout configured at 30 seconds

---

### Context Detection Scripts Layer

#### Task Group 3: Task Detector Script
**Dependencies:** Task Group 2
**Effort:** S (Small)

- [ ] 3.0 Complete task detector script
  - [ ] 3.1 Write 6 focused tests for task detection (S)
    - Test: Detects `shape` task from keywords ("requirements", "scope", "define")
    - Test: Detects `implement` task from keywords ("implement", "build", "create")
    - Test: Detects `review` task from keywords ("review", "check", "audit")
    - Test: Detects `test` task from keywords ("test", "verify", "validate")
    - Test: Detects `debug` task from keywords ("debug", "fix", "error", "bug")
    - Test: Returns `unknown` for prompts with no matching keywords
  - [ ] 3.2 Create `task-detector.py` script (M)
    - Location: `plugins/core/scripts/task-detector.py`
    - Python 3.11+ with full type hints
    - Input: JSON via stdin with `prompt` field
    - Output: JSON to stdout with `task_type` field
    - Implement keyword patterns for all 7 task types:
      - `shape`, `write-spec`, `implement`, `review`, `test`, `debug`, `refactor`
    - Pattern matching using lowercase keyword search
  - [ ] 3.3 Ensure task detector tests pass (XS)
    - Run ONLY the 6 tests written in 3.1
    - Verify all task type detections work correctly

**Acceptance Criteria:**
- Script accepts JSON input via stdin
- Script outputs valid JSON to stdout
- All 7 task types are detectable
- Unknown prompts return `unknown` type
- Full type hints throughout code

---

#### Task Group 4: File Detector Script
**Dependencies:** Task Group 2
**Effort:** S (Small)

- [ ] 4.0 Complete file detector script
  - [ ] 4.1 Write 5 focused tests for file type detection (S)
    - Test: Detects `.py` extension from prompt mentioning Python files
    - Test: Detects `.ts` extension from prompt mentioning TypeScript files
    - Test: Detects `.md` extension from prompt mentioning markdown files
    - Test: Detects explicit filenames (e.g., "config.yaml", "hooks.json")
    - Test: Detects path references (e.g., "plugins/core/scripts/")
  - [ ] 4.2 Create `file-detector.py` script (M)
    - Location: `plugins/core/scripts/file-detector.py`
    - Python 3.11+ with full type hints
    - Input: JSON via stdin with `prompt` field
    - Output: JSON to stdout with `file_types` array
    - Detect common extensions: `.py`, `.ts`, `.js`, `.md`, `.yaml`, `.json`, `.html`, `.css`
    - Detect explicit filenames using regex patterns
    - Detect path references using path separator detection
  - [ ] 4.3 Ensure file detector tests pass (XS)
    - Run ONLY the 5 tests written in 4.1
    - Verify all file type detections work correctly

**Acceptance Criteria:**
- Script accepts JSON input via stdin
- Script outputs valid JSON with file_types array
- Common extensions are detected
- Explicit filenames are captured
- Path references are identified
- Full type hints throughout code

---

### Token Budget Management Layer

#### Task Group 5: Budget Manager Script
**Dependencies:** Task Groups 3, 4
**Effort:** M (Medium)

- [ ] 5.0 Complete budget manager script
  - [ ] 5.1 Write 6 focused tests for token budget management (S)
    - Test: Reads budget from `config.yaml` token_budget section
    - Test: Uses default 3000 tokens if not specified
    - Test: Sorts context items by priority (lower number = higher priority)
    - Test: Truncates lower-priority items when budget exceeded
    - Test: Excludes items entirely if truncation insufficient
    - Test: Includes exclusion summary when items removed
  - [ ] 5.2 Create `budget-manager.py` script (M)
    - Location: `plugins/core/scripts/budget-manager.py`
    - Python 3.11+ with full type hints
    - Input: JSON via stdin with `context_items` array and `config_path`
    - Output: JSON to stdout with `selected_items` and optional `exclusion_summary`
    - Implement token estimation (4 chars per token)
    - Implement priority-based sorting
    - Implement three-tier overflow handling:
      1. Truncate lower-priority items
      2. Exclude items if still over budget
      3. Generate exclusion summary
  - [ ] 5.3 Create config validation utilities (S)
    - Location: `plugins/core/scripts/config_utils.py`
    - Function to load and validate `.red64/config.yaml`
    - Raise appropriate errors for missing/malformed config
    - Return typed config object
  - [ ] 5.4 Ensure budget manager tests pass (XS)
    - Run ONLY the 6 tests written in 5.1
    - Verify all budget behaviors work correctly

**Acceptance Criteria:**
- Budget read correctly from config
- Priority sorting works correctly
- Truncation applies to lower-priority items first
- Exclusion happens when truncation insufficient
- Exclusion summary is accurate
- Token estimation is consistent (4 chars per token)

---

### Main Context Loader Layer

#### Task Group 6: Context Loader Main Script and Integration
**Dependencies:** Task Groups 3, 4, 5
**Effort:** M (Medium)

- [ ] 6.0 Complete context loader main script
  - [ ] 6.1 Write 8 focused tests for context loader integration (M)
    - Test: Receives prompt via stdin JSON correctly
    - Test: Validates config presence and exits code 2 if missing
    - Test: Validates config format and exits code 2 if malformed
    - Test: Chains to task-detector.py and captures output
    - Test: Chains to file-detector.py and captures output
    - Test: Chains to budget-manager.py and captures output
    - Test: Returns valid JSON with `hookSpecificOutput.additionalContext`
    - Test: Error message directs user to run `/red64:init` if config missing
  - [ ] 6.2 Create `context-loader.py` main script (M)
    - Location: `plugins/core/scripts/context-loader.py`
    - Python 3.11+ with full type hints
    - Main entry point for UserPromptSubmit hook
    - Read prompt from stdin JSON (`session_id`, `prompt`, `cwd`, `permission_mode`)
    - Validate `.red64/config.yaml` presence and format
    - Chain to sub-scripts using subprocess:
      - `task-detector.py` for task classification
      - `file-detector.py` for file type detection
      - `budget-manager.py` for token budget enforcement
    - Output JSON with `hookSpecificOutput.additionalContext` structure
    - Exit code 0 for success, exit code 2 for blocking errors
  - [ ] 6.3 Implement error handling and user feedback (S)
    - Clear, actionable error messages
    - Direct users to run `/red64:init` when config missing
    - Validate JSON input format
    - Handle sub-script failures gracefully
  - [ ] 6.4 Ensure context loader tests pass (XS)
    - Run ONLY the 8 tests written in 6.1
    - Verify end-to-end flow works correctly

**Acceptance Criteria:**
- Main script orchestrates all sub-scripts correctly
- Config validation fails strictly with exit code 2
- Error messages are clear and actionable
- Output format matches Claude Code hook specification
- All sub-script outputs are integrated correctly

---

### Testing & Validation Layer

#### Task Group 7: Test Review and Gap Analysis
**Dependencies:** Task Groups 1-6
**Effort:** S (Small)

- [ ] 7.0 Review existing tests and fill critical gaps
  - [ ] 7.1 Review tests from Task Groups 1-6 (XS)
    - Review 4 tests from Task 1.1 (configuration/init)
    - Review 3 tests from Task 2.1 (hook infrastructure)
    - Review 6 tests from Task 3.1 (task detector)
    - Review 5 tests from Task 4.1 (file detector)
    - Review 6 tests from Task 5.1 (budget manager)
    - Review 8 tests from Task 6.1 (context loader)
    - Total existing tests: 32 tests
  - [ ] 7.2 Analyze test coverage gaps for Core Foundation feature (XS)
    - Identify end-to-end workflow gaps
    - Check integration points between scripts
    - Focus ONLY on gaps related to this spec's requirements
    - Do NOT assess entire application coverage
  - [ ] 7.3 Write up to 6 additional integration tests if needed (S)
    - Integration test: Full hook flow from prompt to context output
    - Integration test: Config validation across all scripts
    - Integration test: Token budget with multiple context items
    - Integration test: Error propagation through script chain
    - Add maximum of 6 new tests for critical gaps only
  - [ ] 7.4 Run feature-specific tests only (XS)
    - Run ONLY tests related to Core Foundation feature
    - Expected total: approximately 32-38 tests
    - Do NOT run entire application test suite
    - Verify all critical workflows pass

**Acceptance Criteria:**
- All 32+ feature-specific tests pass
- Critical integration points are covered
- No more than 6 additional tests added
- End-to-end workflow verified

---

## Execution Order

Recommended implementation sequence:

1. **Task Group 1: Configuration Schema and Init Command** (No dependencies)
   - Define the config schema first as other components depend on it
   - Create the init command to bootstrap projects

2. **Task Group 2: Hook Configuration and Entry Point** (Depends on Group 1)
   - Set up the hook infrastructure
   - Create scripts directory structure

3. **Task Group 3: Task Detector Script** (Depends on Group 2)
   - Implement task type classification logic
   - Can be developed in parallel with Group 4

4. **Task Group 4: File Detector Script** (Depends on Group 2)
   - Implement file type detection logic
   - Can be developed in parallel with Group 3

5. **Task Group 5: Budget Manager Script** (Depends on Groups 3, 4)
   - Implement token budget calculation
   - Requires understanding of context item structure

6. **Task Group 6: Context Loader Main Script** (Depends on Groups 3, 4, 5)
   - Orchestrate all sub-scripts
   - Implement final hook output format

7. **Task Group 7: Test Review and Gap Analysis** (Depends on Groups 1-6)
   - Review all existing tests
   - Fill critical integration gaps

---

## File Locations Summary

| File | Location | Task Group |
|------|----------|------------|
| `/red64:init` command | `plugins/core/commands/red64-init.md` | 1 |
| Hook configuration | `plugins/core/hooks/hooks.json` | 2 |
| Context loader | `plugins/core/scripts/context-loader.py` | 6 |
| Task detector | `plugins/core/scripts/task-detector.py` | 3 |
| File detector | `plugins/core/scripts/file-detector.py` | 4 |
| Budget manager | `plugins/core/scripts/budget-manager.py` | 5 |
| Config utilities | `plugins/core/scripts/config_utils.py` | 5 |
| Project config | `.red64/config.yaml` (generated) | 1 |

---

## Technical Notes

- **Python Version:** 3.11+ required (per tech-stack.md)
- **Dependencies:** PyYAML for config parsing
- **Type Hints:** Required throughout all Python code
- **Linting:** Use `ruff` for code quality
- **Testing:** Use `pytest` for all tests
- **Error Messages:** User-friendly, no technical internals exposed
- **Exit Codes:** 0 for success, 2 for blocking errors

---

## Parallelization Opportunities

The following task groups can be developed in parallel:

- **Groups 3 and 4** (Task Detector and File Detector) can be developed simultaneously after Group 2 is complete
- Within each group, tests (x.1) should be written before implementation (x.2)
