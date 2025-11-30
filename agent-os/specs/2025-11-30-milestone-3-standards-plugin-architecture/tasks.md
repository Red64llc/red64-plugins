# Task Breakdown: Milestone 3 - Standards Plugin Architecture

## Overview
Total Tasks: 6 Task Groups, approximately 35 sub-tasks

This milestone enables composable, stack-specific coding standards that integrate with the existing plugin system. Standards are automatically loaded via file-type detection and enforced through PreToolUse hooks that can block Edit/Write operations violating enabled standards.

## Task List

### Configuration Layer

#### Task Group 1: Config Schema Extension for Standards
**Dependencies:** None

- [ ] 1.0 Complete configuration schema extension for standards support
  - [ ] 1.1 Write 4-6 focused tests for config schema and utilities
    - Test `Standards` TypedDict structure validation
    - Test `merge_with_defaults` handles new standards section
    - Test default values: `standards.enabled: []`, `standards.token_budget_priority: 3`
    - Test loading config with standards section present vs absent
  - [ ] 1.2 Extend `plugins/core/scripts/config_schema.py` with Standards section
    - Add `Standards` TypedDict with `enabled: list[str]` and `token_budget_priority: int`
    - Extend `Red64Config` TypedDict to include `standards: Standards`
    - Update `get_default_config()` to include standards defaults
  - [ ] 1.3 Update `plugins/core/scripts/config_utils.py` for standards merging
    - Extend `merge_with_defaults()` to handle `standards` section
    - Follow existing merge pattern for nested config sections
  - [ ] 1.4 Update command template at `plugins/core/commands/red64-init.md`
    - Add `standards` section to default config.yaml example
    - Update Configuration Schema Reference table with new fields
  - [ ] 1.5 Ensure config schema tests pass
    - Run ONLY the 4-6 tests written in 1.1
    - Verify schema changes work correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 4-6 tests written in 1.1 pass
- Config schema includes `Standards` section with `enabled` and `token_budget_priority`
- Defaults are applied correctly when standards section is missing
- Existing config loading remains backward compatible

**Files to modify:**
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/scripts/config_schema.py`
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/scripts/config_utils.py`
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/commands/red64-init.md`

---

### Plugin Structure Layer

#### Task Group 2: Standards Plugin Template
**Dependencies:** Task Group 1

- [ ] 2.0 Complete standards plugin template structure
  - [ ] 2.1 Write 3-5 focused tests for plugin template validation
    - Test plugin.json has required `category: "standards"` field
    - Test standards.json file pattern parsing (glob matching)
    - Test plugin directory structure validation (skills/, hooks/ directories exist)
  - [ ] 2.2 Create standards template directory at `plugins/standards-template/`
    - Create `.claude-plugin/plugin.json` with `category: "standards"` field
    - Include all required metadata fields matching existing core plugin format
  - [ ] 2.3 Create `plugins/standards-template/standards.json` manifest
    - Define `file_patterns` array for file type matching (e.g., `["*.ts", "*.tsx"]`)
    - Include `name` and `description` fields for identification
  - [ ] 2.4 Create `plugins/standards-template/skills/` directory with example skill
    - Create `example-skill.md` demonstrating SKILL.md format
    - Include `## DO` section with positive patterns and code examples
    - Include `## DON'T` section with anti-patterns and explanations
    - Target 200-500 tokens per skill
  - [ ] 2.5 Create `plugins/standards-template/hooks/` directory with empty `hooks.json`
    - Standards plugins use core validator hook, not custom hooks
    - Include empty hooks.json: `{"hooks": {}}`
  - [ ] 2.6 Ensure plugin template tests pass
    - Run ONLY the 3-5 tests written in 2.1
    - Verify template structure is valid
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 3-5 tests written in 2.1 pass
- Template follows existing plugin structure
- plugin.json includes `category: "standards"`
- standards.json defines file patterns
- SKILL.md format includes DO and DON'T sections
- Plugin naming convention: `red64-standards-{language}`

**Files to create:**
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/standards-template/.claude-plugin/plugin.json`
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/standards-template/standards.json`
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/standards-template/skills/example-skill.md`
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/standards-template/hooks/hooks.json`

---

### CLI Commands Layer

#### Task Group 3: Standards Enable/Disable Commands
**Dependencies:** Task Group 1, Task Group 2

- [ ] 3.0 Complete CLI commands for standards management
  - [ ] 3.1 Write 4-6 focused tests for standards commands
    - Test enable command adds standard to config.yaml `standards.enabled` list
    - Test disable command removes standard from config.yaml
    - Test validation rejects non-existent standard plugins
    - Test ordering is preserved (first enabled = highest priority)
  - [ ] 3.2 Create `plugins/core/commands/red64-standards-enable.md`
    - Follow command format from `red64-init.md` template
    - Include "What This Command Does" section
    - Include "Execution Steps" with numbered steps
    - Validate standard plugin exists in plugins directory before enabling
    - Update `.red64/config.yaml` with new enabled standard
    - Maintain ordering (append to end of list)
    - Include idempotency check (skip if already enabled)
  - [ ] 3.3 Create `plugins/core/commands/red64-standards-disable.md`
    - Follow command format from `red64-init.md` template
    - Remove standard from `standards.enabled` list in config.yaml
    - Include idempotency check (skip if not enabled)
    - Output success/skip message matching existing style
  - [ ] 3.4 Create `plugins/core/commands/red64-standards-list.md` (optional utility)
    - List all available standards plugins in plugins directory
    - Show which standards are currently enabled
    - Display priority order for enabled standards
  - [ ] 3.5 Ensure CLI command tests pass
    - Run ONLY the 4-6 tests written in 3.1
    - Verify commands execute correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 4-6 tests written in 3.1 pass
- Enable command validates plugin existence
- Config.yaml is updated correctly with proper ordering
- Disable command removes standards cleanly
- Commands are idempotent (safe to run multiple times)

**Files to create:**
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/commands/red64-standards-enable.md`
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/commands/red64-standards-disable.md`
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/commands/red64-standards-list.md` (optional)

---

### Hook Infrastructure Layer

#### Task Group 4: PreToolUse Hook for Standards Validation
**Dependencies:** Task Group 1, Task Group 2

- [ ] 4.0 Complete PreToolUse hook infrastructure for standards validation
  - [ ] 4.1 Write 5-8 focused tests for standards validator hook
    - Test hook receives correct input (tool_name, tool_input with file paths)
    - Test hook returns `{"decision": "allow"}` for compliant operations
    - Test hook returns `{"decision": "block", "reason": "..."}` for violations
    - Test file extension matching against standards.json patterns
    - Test multiple standards precedence based on config ordering
  - [ ] 4.2 Update `plugins/core/hooks/hooks.json` with PreToolUse configuration
    - Add `PreToolUse` hook alongside existing `UserPromptSubmit`
    - Configure to call `standards-validator.py` script
    - Set appropriate timeout (recommend 30 seconds)
  - [ ] 4.3 Create `plugins/core/hooks/standards-validator.py` script
    - Accept JSON input via stdin with `tool_name` and `tool_input`
    - Detect target file path from Edit/Write tool input
    - Load enabled standards from `.red64/config.yaml`
    - Match file extension against `standards.json` file patterns
    - Check operation against DON'T patterns from applicable skills
    - Return JSON with `decision` field: `"allow"`, `"block"`, or `"suggest"`
  - [ ] 4.4 Implement blocking capability in validator
    - Return format: `{"decision": "block", "reason": "violates X standard: <explanation>"}`
    - Include `suggestion` field for advisory guidance when blocking seems too strict
    - Log blocked operations for debugging (optional)
  - [ ] 4.5 Add standards skill loading utility function
    - Create helper to load and parse SKILL.md files from enabled standards
    - Extract DON'T patterns for validation checking
    - Cache loaded skills to avoid repeated file I/O
  - [ ] 4.6 Ensure hook infrastructure tests pass
    - Run ONLY the 5-8 tests written in 4.1
    - Verify hook integration works correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 5-8 tests written in 4.1 pass
- PreToolUse hook is registered in hooks.json
- Validator correctly identifies applicable standards
- Blocking works with clear error messages
- Advisory mode fallback available via suggestion field

**Files to modify:**
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/hooks/hooks.json`

**Files to create:**
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/hooks/standards-validator.py`

---

### Context Loader Integration

#### Task Group 5: Context Loader Standards Integration
**Dependencies:** Task Group 1, Task Group 2, Task Group 4

- [ ] 5.0 Complete context loader integration for standards skills
  - [ ] 5.1 Write 4-6 focused tests for context loader standards integration
    - Test standards skills are included in context output
    - Test file type matching loads correct standards
    - Test token budget respects `standards.token_budget_priority`
    - Test multiple standards skills are included with precedence header
  - [ ] 5.2 Extend `plugins/core/scripts/context-loader.py` for standards loading
    - Add function to detect applicable standards based on file types in prompt
    - Match detected file types against `standards.json` patterns from enabled plugins
    - Load relevant SKILL.md content from matched standards plugins
  - [ ] 5.3 Update `format_additional_context()` function
    - Add `## Standards: {plugin-name}` header for included standards
    - Include skill content under standards header
    - Note when multiple standards apply and which takes precedence
  - [ ] 5.4 Integrate with budget manager for token allocation
    - Pass standards skills to budget manager with configured priority
    - Use `standards.token_budget_priority` from config for priority value
    - When multiple standards enabled, share allocated budget proportionally
  - [ ] 5.5 Create standards skill loader utility script
    - Create `plugins/core/scripts/standards-loader.py` for loading standards
    - Accept file types as input, return matched standards skills
    - Follow existing `run_sub_script` pattern from context-loader.py
  - [ ] 5.6 Ensure context loader integration tests pass
    - Run ONLY the 4-6 tests written in 5.1
    - Verify standards are correctly loaded into context
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 4-6 tests written in 5.1 pass
- Standards skills appear in context when editing relevant files
- Token budget priority is respected
- Multiple standards show precedence information
- Context output includes `## Standards: {name}` headers

**Files to modify:**
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/scripts/context-loader.py`
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/scripts/budget-manager.py`

**Files to create:**
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/scripts/standards-loader.py`

---

### Reference Implementation

#### Task Group 6: TypeScript Standards Plugin
**Dependencies:** Task Group 2, Task Group 3, Task Group 4, Task Group 5

- [ ] 6.0 Complete TypeScript reference standards plugin
  - [ ] 6.1 Write 4-6 focused tests for TypeScript standards plugin
    - Test plugin structure matches template requirements
    - Test standards.json correctly matches TypeScript files
    - Test skills follow SKILL.md format with DO/DON'T sections
    - Test integration with standards validator hook
  - [ ] 6.2 Create plugin directory at `plugins/red64-standards-typescript/`
    - Create `.claude-plugin/plugin.json` with metadata
    - Set `category: "standards"` in manifest
    - Include author information and description
  - [ ] 6.3 Create `plugins/red64-standards-typescript/standards.json`
    - Set file patterns: `["*.ts", "*.tsx"]`
    - Include plugin name and description
  - [ ] 6.4 Create `skills/naming-conventions.md`
    - `## DO`: PascalCase for types/interfaces, camelCase for variables/functions
    - `## DON'T`: Hungarian notation, single-letter names, inconsistent casing
    - Include TypeScript code examples in fenced blocks
    - Target 200-500 tokens
  - [ ] 6.5 Create `skills/type-safety.md`
    - `## DO`: Explicit types, strict null checks, discriminated unions
    - `## DON'T`: `any` type usage, type assertions without validation, ignoring null
    - Include code examples demonstrating good vs bad patterns
  - [ ] 6.6 Create `skills/error-handling.md`
    - `## DO`: Custom error types, Result pattern, proper async error handling
    - `## DON'T`: Empty catch blocks, swallowing errors, generic Error throws
    - Include TypeScript-specific error handling patterns
  - [ ] 6.7 Create `skills/module-structure.md`
    - `## DO`: Barrel exports, clear public API, index files
    - `## DON'T`: Circular dependencies, deep nesting, mixed concerns
    - Include import/export patterns and file organization
  - [ ] 6.8 Create `skills/async-patterns.md`
    - `## DO`: async/await, Promise.all for parallelism, proper cancellation
    - `## DON'T`: Mixing callbacks and promises, unhandled rejections, race conditions
    - Include async TypeScript patterns
  - [ ] 6.9 Create `plugins/red64-standards-typescript/hooks/hooks.json`
    - Empty hooks file: `{"hooks": {}}`
    - Standards use core validator hook
  - [ ] 6.10 Ensure TypeScript plugin tests pass
    - Run ONLY the 4-6 tests written in 6.1
    - Verify plugin integrates correctly with standards system
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 4-6 tests written in 6.1 pass
- Plugin follows template structure exactly
- All 5 skills follow SKILL.md format with DO/DON'T sections
- Each skill is 200-500 tokens
- Plugin integrates with enable command and validator hook
- Serves as reference for future standards plugins

**Files to create:**
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/red64-standards-typescript/.claude-plugin/plugin.json`
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/red64-standards-typescript/standards.json`
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/red64-standards-typescript/skills/naming-conventions.md`
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/red64-standards-typescript/skills/type-safety.md`
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/red64-standards-typescript/skills/error-handling.md`
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/red64-standards-typescript/skills/module-structure.md`
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/red64-standards-typescript/skills/async-patterns.md`
- `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/red64-standards-typescript/hooks/hooks.json`

---

### Final Integration

#### Task Group 7: Test Review and Integration Verification
**Dependencies:** Task Groups 1-6

- [ ] 7.0 Review existing tests and verify full integration
  - [ ] 7.1 Review tests from Task Groups 1-6
    - Review 4-6 tests from config schema (Task 1.1)
    - Review 3-5 tests from plugin template (Task 2.1)
    - Review 4-6 tests from CLI commands (Task 3.1)
    - Review 5-8 tests from hook infrastructure (Task 4.1)
    - Review 4-6 tests from context loader (Task 5.1)
    - Review 4-6 tests from TypeScript plugin (Task 6.1)
    - Total existing tests: approximately 24-37 tests
  - [ ] 7.2 Analyze test coverage gaps for standards feature
    - Focus ONLY on gaps related to standards plugin architecture
    - Identify missing end-to-end workflow tests
    - Do NOT assess entire application test coverage
  - [ ] 7.3 Write up to 10 additional strategic tests
    - End-to-end: Enable standards via command, edit TS file, verify context includes standards
    - End-to-end: Trigger PreToolUse hook, verify blocking works for DON'T patterns
    - Integration: Multiple standards enabled, verify ordering precedence
    - Integration: Token budget allocation respects standards priority
    - Focus on user workflows, not exhaustive unit coverage
  - [ ] 7.4 Run feature-specific tests only
    - Run ONLY tests related to standards plugin architecture
    - Expected total: approximately 34-47 tests maximum
    - Do NOT run the entire application test suite
    - Verify all critical workflows pass
  - [ ] 7.5 Verify complete integration
    - Test full workflow: init -> enable standards -> edit file -> verify context
    - Confirm PreToolUse hook blocks violations correctly
    - Verify config.yaml changes persist correctly
    - Check standards skills appear in context output

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 34-47 tests total)
- End-to-end workflows function correctly
- No more than 10 additional tests added
- Standards enable/disable/validate workflow complete
- TypeScript standards plugin fully functional

---

## Execution Order

Recommended implementation sequence:

1. **Task Group 1: Config Schema Extension** - Foundation for all standards configuration
2. **Task Group 2: Standards Plugin Template** - Defines structure for all standards plugins
3. **Task Group 3: CLI Commands** - User interface for managing standards
4. **Task Group 4: PreToolUse Hook** - Enforcement mechanism for standards validation
5. **Task Group 5: Context Loader Integration** - Loads standards into Claude's context
6. **Task Group 6: TypeScript Standards Plugin** - Reference implementation
7. **Task Group 7: Integration Verification** - Final testing and validation

## Dependencies Graph

```
Task Group 1 (Config)
        |
        v
Task Group 2 (Template) ----+
        |                   |
        v                   |
Task Group 3 (CLI) ---------+----> Task Group 6 (TypeScript Plugin)
        |                   |              |
        v                   |              v
Task Group 4 (Hook) --------+----> Task Group 7 (Integration)
        |                   |              ^
        v                   |              |
Task Group 5 (Context) -----+--------------+
```

## Key File Paths Summary

**Configuration:**
- `plugins/core/scripts/config_schema.py`
- `plugins/core/scripts/config_utils.py`

**Template:**
- `plugins/standards-template/` (new directory)

**Commands:**
- `plugins/core/commands/red64-standards-enable.md`
- `plugins/core/commands/red64-standards-disable.md`

**Hooks:**
- `plugins/core/hooks/hooks.json`
- `plugins/core/hooks/standards-validator.py`

**Context Loader:**
- `plugins/core/scripts/context-loader.py`
- `plugins/core/scripts/standards-loader.py`
- `plugins/core/scripts/budget-manager.py`

**Reference Plugin:**
- `plugins/red64-standards-typescript/` (new directory)
