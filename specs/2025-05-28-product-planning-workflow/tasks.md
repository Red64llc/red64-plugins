# Task Breakdown: Product Planning Workflow

## Overview

This milestone implements the Product Planning Workflow feature for Red64, enabling users to define their product's mission, roadmap, and tech stack through three dedicated commands that create pre-filled template documents, with automatic context injection into all subsequent prompts.

**Total Tasks:** 24 tasks across 5 task groups

**Roadmap Items Covered:**
- Item 7: Product planning command (split into 3 separate commands)
- Item 8: Mission document template
- Item 9: Roadmap document template
- Item 10: Tech stack document template
- Item 11: Product context injection

---

## Task List

### Template Layer

#### Task Group 1: Document Templates
**Dependencies:** None
**Effort:** S (2-3 days total)

Templates are the foundation that commands will create. Building these first ensures commands have validated content to generate.

- [ ] 1.0 Complete document templates
  - [ ] 1.1 Write 3 focused tests for template content quality
    - Test mission template has all required sections (Pitch, Vision, Problem, Users, Differentiators, Key Features, Success Metrics)
    - Test roadmap template enforces exact checklist format with effort estimates
    - Test tech-stack template has category-based organization
  - [ ] 1.2 Create mission template content
    - Location: Define as embedded content in command (not separate file)
    - Sections: Pitch, Vision Statement, Problem, Users, Differentiators, Key Features, Success Metrics
    - Include HTML comment hints `<!-- -->` for each section
    - Use professional example content (not lorem ipsum)
    - Reference structure from: `/Users/yacin/Workspace/products/red64-framework-project/red64-001/agent-os/product/mission.md`
  - [ ] 1.3 Create roadmap template content
    - Enforce exact format: numbered items with `[ ]`/`[x]` checkboxes
    - Include effort estimates (XS/S/M/L/XL) on each item
    - Provide 2-3 example milestones with example items
    - Reference structure from: `/Users/yacin/Workspace/products/red64-framework-project/red64-001/agent-os/product/roadmap.md`
  - [ ] 1.4 Create tech-stack template content
    - Categories: Languages, Frameworks, Database, Infrastructure, Development Tools
    - Simple list format (no rationale columns per requirements)
    - Include example technologies for each category
  - [ ] 1.5 Ensure template tests pass
    - Validate all required sections present in templates
    - Verify format compliance

**Acceptance Criteria:**
- All 3 templates contain professional-quality example content
- Mission template has all 7 required sections
- Roadmap template uses exact checklist format with effort estimates
- Tech-stack template uses simple list format by category
- HTML comment hints guide users on what to edit

---

### Command Layer

#### Task Group 2: Planning Commands
**Dependencies:** Task Group 1 (templates)
**Effort:** M (1 week total)

- [ ] 2.0 Complete planning commands
  - [ ] 2.1 Write 4 focused tests for command behavior
    - Test `/red64:plan-mission` creates file at correct path when missing
    - Test `/red64:plan-mission` skips with message when file exists
    - Test success message includes created file path
    - Test skip message follows pattern from red64-init.md
  - [ ] 2.2 Create `/red64:plan-mission` command
    - Location: `plugins/core/commands/red64-plan-mission.md`
    - Follow exact structure from: `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/commands/red64-init.md`
    - Include sections: "What This Command Does", "Execution Steps"
    - Step 1: Check if `.red64/product/mission.md` exists
    - Step 2: If exists, output skip message and stop
    - Step 3: Create file with template from Task 1.2
    - Step 4: Output success message with file path
    - Ensure idempotency (safe to run multiple times)
  - [ ] 2.3 Create `/red64:plan-roadmap` command
    - Location: `plugins/core/commands/red64-plan-roadmap.md`
    - Follow same structure as plan-mission command
    - Create `.red64/product/roadmap.md` with template from Task 1.3
    - Include idempotency check and appropriate messages
  - [ ] 2.4 Create `/red64:plan-tech-stack` command
    - Location: `plugins/core/commands/red64-plan-tech-stack.md`
    - Follow same structure as plan-mission command
    - Create `.red64/product/tech-stack.md` with template from Task 1.4
    - Include idempotency check and appropriate messages
  - [ ] 2.5 Ensure command tests pass
    - Verify all 4 tests from 2.1 pass
    - Manually verify command execution flow

**Acceptance Criteria:**
- All 3 commands follow exact structure from red64-init.md
- Commands are idempotent (skip if file exists)
- Success/skip messages include file paths
- Commands create files in `.red64/product/` directory
- All tests pass

---

### Python Scripts Layer

#### Task Group 3: Context Processing Scripts
**Dependencies:** Task Group 1 (templates for parsing patterns)
**Effort:** M (1 week total)

- [ ] 3.0 Complete context processing scripts
  - [ ] 3.1 Write 6 focused tests for script functionality
    - Test mission-summarizer extracts first sentence from Pitch section
    - Test mission-summarizer extracts first sentence from Problem section
    - Test mission-summarizer extracts Key Features as bullet list
    - Test roadmap-parser returns first unchecked `[ ]` item
    - Test roadmap-parser returns null when all items checked
    - Test roadmap-parser handles missing file gracefully
  - [ ] 3.2 Create mission-summarizer.py script
    - Location: `plugins/core/scripts/mission-summarizer.py`
    - Follow patterns from: `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/scripts/context-loader.py`
    - Use TypedDict for input/output schemas
    - Rule-based extraction (NOT LLM): extract first sentence from Pitch, first sentence from Problem, bulleted list from Key Features
    - Target summary length: 150-300 tokens
    - Return JSON with `mission_lite` field
    - Handle missing file gracefully (return null, no blocking errors)
  - [ ] 3.3 Create roadmap-parser.py script
    - Location: `plugins/core/scripts/roadmap-parser.py`
    - Follow same patterns as mission-summarizer.py
    - Parse exact checklist format: numbered items with `[ ]` checkboxes
    - Return first unchecked item (first `[ ]` found, not `[x]`)
    - Return JSON with `current_item` containing: item_number, item_title, effort_estimate, parent_milestone
    - Edge cases: all items checked (return null), malformed format (return error), no file (return null)
  - [ ] 3.4 Create product-context.py orchestrator script
    - Location: `plugins/core/scripts/product-context.py`
    - Orchestrates mission-summarizer.py and roadmap-parser.py
    - Use subprocess chaining pattern from context-loader.py
    - Format output as Markdown block with "Product Context" header
    - Include mission-lite summary and current roadmap item
    - Handle failures gracefully (partial output if one script fails)
  - [ ] 3.5 Ensure script tests pass
    - Run all 6 tests from 3.1
    - Verify JSON output format compliance

**Acceptance Criteria:**
- Scripts follow patterns from existing context-loader.py
- TypedDict schemas defined for all inputs/outputs
- Mission-summarizer uses rule-based extraction (no LLM)
- Roadmap-parser finds first unchecked item correctly
- All edge cases handled with graceful degradation
- All tests pass

---

### Hook Integration Layer

#### Task Group 4: Context Injection Hook
**Dependencies:** Task Group 3 (scripts)
**Effort:** S (2-3 days)

- [ ] 4.0 Complete hook integration
  - [ ] 4.1 Write 3 focused tests for hook integration
    - Test product-context.py is called on UserPromptSubmit
    - Test product context appears in additionalContext output
    - Test integration respects token budget from config.yaml
  - [ ] 4.2 Integrate product-context.py into context-loader.py
    - Modify: `plugins/core/scripts/context-loader.py`
    - Add call to product-context.py in the orchestration pipeline
    - Include product context in `format_additional_context` output
    - Add new section after existing Red64 Context sections
    - Handle product-context.py failures gracefully (continue without product context)
  - [ ] 4.3 Update format_additional_context function
    - Add "Product Context" section to output
    - Include mission-lite summary under "Product Mission" subheader
    - Include current roadmap item under "Current Work Item" subheader
    - Respect existing token budget configuration from `.red64/config.yaml`
  - [ ] 4.4 Ensure hook integration tests pass
    - Run tests from 4.1
    - Verify end-to-end flow from prompt submission to context injection

**Acceptance Criteria:**
- Product context appears in UserPromptSubmit hook output
- Integration extends existing hook (does not replace)
- Graceful degradation if product docs missing
- Token budget respected
- All tests pass

---

### Verification Layer

#### Task Group 5: Test Review and End-to-End Verification
**Dependencies:** Task Groups 1-4
**Effort:** S (2-3 days)

- [ ] 5.0 Review existing tests and fill critical gaps
  - [ ] 5.1 Review tests from Task Groups 1-4
    - Review 3 template tests (Task 1.1)
    - Review 4 command tests (Task 2.1)
    - Review 6 script tests (Task 3.1)
    - Review 3 hook tests (Task 4.1)
    - Total existing tests: 16 tests
  - [ ] 5.2 Analyze test coverage gaps for Product Planning Workflow
    - Identify critical end-to-end workflows lacking coverage
    - Focus ONLY on this feature's requirements
    - Prioritize integration points over unit test gaps
  - [ ] 5.3 Write up to 8 additional strategic tests if needed
    - End-to-end: Run all 3 planning commands, verify files created
    - End-to-end: Create product docs, submit prompt, verify context injection
    - Integration: Verify mission-summarizer output meets token budget (150-300)
    - Integration: Verify roadmap-parser handles all milestone formats
    - Edge case: Empty mission.md file handling
    - Edge case: Roadmap with only completed items
    - Edge case: Product docs directory missing
    - Error case: Malformed roadmap format
  - [ ] 5.4 Run feature-specific tests only
    - Run all tests from Task Groups 1-4 plus new tests from 5.3
    - Expected total: approximately 16-24 tests
    - Verify all critical workflows pass
  - [ ] 5.5 Manual verification checklist
    - Run `/red64:plan-mission` in fresh project, verify file created
    - Run `/red64:plan-mission` again, verify skip message
    - Edit mission.md with custom content
    - Verify mission-lite summary reflects edits
    - Create roadmap with mix of checked/unchecked items
    - Verify current roadmap item detection
    - Submit prompt, verify product context appears in response

**Acceptance Criteria:**
- All 16-24 tests pass
- End-to-end workflows verified manually
- All edge cases handled gracefully
- Feature integrates correctly with existing Red64 infrastructure

---

## Execution Order

Recommended implementation sequence:

1. **Task Group 1: Document Templates** (2-3 days)
   - Foundation for all other work
   - Can be developed independently
   - Validates template quality before commands use them

2. **Task Group 2: Planning Commands** (1 week)
   - Depends on templates from Group 1
   - User-facing deliverables
   - Follow existing command patterns closely

3. **Task Group 3: Context Processing Scripts** (1 week)
   - Can begin in parallel with Group 2 after templates done
   - Core logic for context injection
   - Follow existing Python script patterns

4. **Task Group 4: Hook Integration** (2-3 days)
   - Depends on scripts from Group 3
   - Connects everything to the context loading pipeline
   - Minimal changes to existing infrastructure

5. **Task Group 5: Test Review and Verification** (2-3 days)
   - Depends on all previous groups
   - Final validation before feature complete
   - Fill any critical testing gaps

---

## Reference Files

**Patterns to Follow:**
- Command structure: `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/commands/red64-init.md`
- Hook configuration: `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/hooks/hooks.json`
- Python script patterns: `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/scripts/context-loader.py`

**Reference Documents:**
- Mission structure: `/Users/yacin/Workspace/products/red64-framework-project/red64-001/agent-os/product/mission.md`
- Roadmap structure: `/Users/yacin/Workspace/products/red64-framework-project/red64-001/agent-os/product/roadmap.md`
- Tech-stack structure: `/Users/yacin/Workspace/products/red64-framework-project/red64-001/agent-os/product/tech-stack.md`

**Output Locations:**
- Commands: `plugins/core/commands/red64-plan-*.md`
- Scripts: `plugins/core/scripts/mission-summarizer.py`, `roadmap-parser.py`, `product-context.py`
- User files (created by commands): `.red64/product/mission.md`, `roadmap.md`, `tech-stack.md`

---

## Effort Summary

| Task Group | Effort | Dependencies |
|------------|--------|--------------|
| 1. Document Templates | S (2-3 days) | None |
| 2. Planning Commands | M (1 week) | Group 1 |
| 3. Context Processing Scripts | M (1 week) | Group 1 |
| 4. Hook Integration | S (2-3 days) | Group 3 |
| 5. Test Review & Verification | S (2-3 days) | Groups 1-4 |

**Total Estimated Effort:** 3-4 weeks (with Groups 2 and 3 partially parallelizable)
