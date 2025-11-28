# Spec Requirements: Red64 Core Foundation

## Initial Description

This spec covers 4 interconnected items from Milestone 1 of the Red64 roadmap:

1. **Project initialization command** - `/red64:init` command (in `plugins/core/commands/`) that creates `.red64/` directory structure with config.yaml

2. **Hook infrastructure** - Implement `hooks/hooks.json` with `UserPromptSubmit` hook that analyzes prompts and prepares for context injection

3. **Context loader script** - Python script (`scripts/context-loader.py`) that detects file types, keywords, and task type from user prompts

4. **Token budget management** - Configurable token budgets in `.red64/config.yaml` with priority-based selection when limits are reached

These components work together to form the core infrastructure that enables Red64's context-aware functionality.

## Requirements Discussion

### First Round Questions

**Q1:** Should `/red64:init` be idempotent (safe to run multiple times without breaking existing configuration)?
**Answer:** YES - `/red64:init` should be safe to run multiple times without overwriting existing configuration.

**Q2:** How should the hook output context to Claude Code - print JSON to stdout, or write to a file?
**Answer:** Write to a file (unless less efficient than printing JSON). Based on official Claude Code hooks documentation, the preferred method is JSON output to stdout with `hookSpecificOutput.additionalContext` structure.

**Q3:** What task type categories should the context loader detect?
**Answer:** Propose a default set based on spec-driven workflow. The recommended categories are:
- `shape` - Requirements shaping and refinement
- `write-spec` - Specification writing
- `implement` - Code implementation
- `review` - Code review tasks
- `test` - Test writing and verification
- `debug` - Debugging and issue resolution
- `refactor` - Code refactoring

**Q4:** When token budget is exceeded, what behavior is preferred - truncate, exclude items, or provide a summary of exclusions?
**Answer:** All three behaviors combined:
1. Truncate lower-priority items first
2. Exclude items if needed to stay within budget
3. Provide a summary of what was excluded so the user is aware

**Q5:** Should automation scripts be a single monolithic script or separate scripts that chain together?
**Answer:** Separate scripts that chain together for modularity and maintainability.

**Q6:** Should keyword detection patterns be configurable or use built-in patterns only?
**Answer:** Just built-in patterns for now (no custom patterns in config). Custom patterns can be added as a future enhancement.

**Q7:** If `.red64/config.yaml` is missing or malformed, should the hook fail gracefully or strictly?
**Answer:** FAIL strictly if `.red64/config.yaml` is missing or malformed. The hook should exit with error code 2 (blocking error) and provide a clear error message directing the user to run `/red64:init`.

**Q8:** Is there anything that should be explicitly excluded from this spec's scope?
**Answer:** Nothing excluded - all four components should be fully implemented.

### Existing Code to Reference

**Similar Features Identified:**
- Claude Code demo plugins repository: `https://github.com/anthropics/claude-code/tree/main` - Reference for plugin architecture
- Existing Red64 marketplace structure at `/Users/yacin/Workspace/products/red64/.claude-plugin/marketplace.json`
- Existing core plugin structure at `/Users/yacin/Workspace/products/red64/plugins/core/`

### Follow-up Questions

No follow-up questions were required - all requirements were clarified in the first round.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
Not applicable.

## Claude Code Hooks Technical Reference

The following technical details from the official Claude Code hooks documentation inform the implementation:

### hooks.json Format
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 script.py",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### UserPromptSubmit Hook Input (via stdin JSON)
- `session_id`: Unique session identifier
- `prompt`: The user's submitted text
- `cwd`: Current working directory
- `permission_mode`: Current permission level

### Output Methods
- Exit code 0 with stdout JSON = context injection
- Exit code 2 = blocking error (stops prompt processing)
- JSON output with `hookSpecificOutput.additionalContext` for structured context

### Python Pattern for Context Injection
```python
#!/usr/bin/env python3
import json
import sys

input_data = json.load(sys.stdin)
context = "Additional information to inject"
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": context
    }
}))
sys.exit(0)
```

## Requirements Summary

### Functional Requirements

#### Component 1: Project Initialization Command (`/red64:init`)
- Creates `.red64/` directory structure in current working directory
- Generates initial `config.yaml` with default settings
- Idempotent: safe to run multiple times
- Does NOT overwrite existing `config.yaml` if present
- Creates subdirectories: `product/`, `specs/`, `metrics/`
- Provides clear success/skip feedback to user

#### Component 2: Hook Infrastructure (`hooks/hooks.json`)
- Implements `UserPromptSubmit` hook
- Hook triggers Python context-loader script
- Configurable timeout (default 30 seconds)
- Reads prompt from stdin as JSON
- Outputs context via `hookSpecificOutput.additionalContext`
- Exits with code 2 if config missing (blocking error)

#### Component 3: Context Loader Script (`scripts/context-loader.py`)
- Receives prompt via stdin JSON
- Detects file types mentioned in prompt
- Identifies task type from keyword patterns
- Detects keywords indicating which standards/context to load
- Chains to other scripts as needed
- Returns structured context for injection

#### Component 4: Token Budget Management
- Configurable in `.red64/config.yaml`
- Default budget: 3000 tokens (per product mission metrics)
- Priority-based item selection when budget exceeded
- Three-tier overflow handling:
  1. Truncate lower-priority items
  2. Exclude items if still over budget
  3. Include summary of excluded items in context
- Budget applies to injected context only (not user prompt)

### Default Task Type Categories

Based on the spec-driven workflow pattern established in the product roadmap:

| Task Type | Keywords/Patterns | Priority Items to Load |
|-----------|------------------|----------------------|
| `shape` | "requirements", "scope", "define", "clarify" | Product mission, roadmap context |
| `write-spec` | "specification", "spec", "document", "design" | Requirements, templates |
| `implement` | "implement", "build", "create", "add feature" | Spec, relevant standards, tech stack |
| `review` | "review", "check", "audit", "look at" | Standards, spec for comparison |
| `test` | "test", "verify", "validate", "coverage" | Spec requirements, test standards |
| `debug` | "debug", "fix", "error", "issue", "bug" | Error logs, related code context |
| `refactor` | "refactor", "clean up", "improve", "optimize" | Standards, existing patterns |

### Configuration Schema for `.red64/config.yaml`

```yaml
# Red64 Project Configuration
version: "1.0"

# Token budget for context injection
token_budget:
  max_tokens: 3000
  overflow_behavior:
    truncate: true
    exclude_low_priority: true
    show_exclusion_summary: true

# Context loading settings
context_loader:
  enabled: true
  task_detection: true
  file_type_detection: true

# Priority levels for context items (lower number = higher priority)
priorities:
  product_mission: 1
  current_spec: 2
  relevant_standards: 3
  tech_stack: 4
  roadmap: 5

# Enabled features (for future extensibility)
features:
  standards_injection: false  # Milestone 3
  multi_agent: false          # Milestone 5
  metrics: false              # Milestone 6
```

### Script Chaining Approach

The scripts are designed to be modular and chain together:

```
UserPromptSubmit Hook
        |
        v
context-loader.py (main entry point)
        |
        +---> task-detector.py (classify task type)
        |
        +---> file-detector.py (identify file types in prompt)
        |
        +---> budget-manager.py (apply token budget limits)
        |
        v
    JSON Output (hookSpecificOutput.additionalContext)
```

Each script:
- Takes JSON input via stdin
- Outputs JSON to stdout
- Can be tested independently
- Has a single responsibility

### Component Interaction Flow

```
1. User submits prompt in Claude Code
                |
                v
2. UserPromptSubmit hook triggers
                |
                v
3. context-loader.py receives prompt via stdin
                |
                v
4. Script checks for .red64/config.yaml
   - Missing? Exit code 2 with error message
   - Malformed? Exit code 2 with validation error
                |
                v
5. Parse prompt for:
   - Task type (shape, write-spec, implement, etc.)
   - File types mentioned (.py, .ts, .md, etc.)
   - Keywords indicating needed context
                |
                v
6. Determine context items to load based on:
   - Detected task type
   - File types present
   - Keyword matches
                |
                v
7. Apply token budget:
   - Sort items by priority
   - Calculate token estimates
   - Truncate/exclude as needed
   - Build exclusion summary if items removed
                |
                v
8. Output JSON with hookSpecificOutput.additionalContext
                |
                v
9. Claude Code receives injected context with prompt
```

### Scope Boundaries

**In Scope:**
- `/red64:init` command implementation
- `hooks/hooks.json` configuration
- `scripts/context-loader.py` main script
- Supporting scripts for task detection, file detection, budget management
- `.red64/config.yaml` schema and default generation
- Error handling for missing/malformed config
- Token budget calculation and enforcement
- Built-in keyword patterns for task type detection

**Out of Scope:**
- Standards injection (Milestone 3)
- Product planning workflow (Milestone 2)
- Multi-agent orchestration (Milestone 5)
- Metrics collection (Milestone 6)
- Custom keyword patterns in config
- GUI or web interface
- External service integrations

### Technical Considerations

- **Language:** Python 3.11+ for all scripts (per tech-stack.md)
- **Dependencies:** PyYAML required for config parsing
- **Type hints:** Required throughout Python code
- **Code quality:** Use `ruff` for linting/formatting
- **Testing:** Unit tests with `pytest` for all scripts
- **Error messages:** User-friendly, actionable, no technical internals exposed
- **File format:** YAML for config (human-editable), JSON for hooks (strict schema)

### Acceptance Criteria

#### Component 1: `/red64:init` Command
- [ ] Running `/red64:init` in a directory without `.red64/` creates the full structure
- [ ] Running `/red64:init` in a directory with existing `.red64/` does not overwrite config.yaml
- [ ] Created config.yaml matches the defined schema with all default values
- [ ] Subdirectories created: `product/`, `specs/`, `metrics/`
- [ ] Clear success message shown after initialization
- [ ] Clear skip message shown if already initialized

#### Component 2: Hook Infrastructure
- [ ] `hooks/hooks.json` valid JSON matching Claude Code hook schema
- [ ] Hook triggers on every `UserPromptSubmit` event
- [ ] Hook correctly invokes `context-loader.py` script
- [ ] Timeout configured (30 seconds default)
- [ ] Hook output correctly structured for context injection

#### Component 3: Context Loader Script
- [ ] Correctly reads prompt from stdin JSON
- [ ] Detects task type from built-in keyword patterns
- [ ] Identifies file extensions mentioned in prompt
- [ ] Returns valid JSON with `hookSpecificOutput.additionalContext`
- [ ] Exits with code 2 and clear message if config missing
- [ ] Exits with code 2 and clear message if config malformed
- [ ] All Python code has type hints
- [ ] Unit tests pass with `pytest`

#### Component 4: Token Budget Management
- [ ] Budget read from config.yaml `token_budget.max_tokens`
- [ ] Items sorted by configured priority before selection
- [ ] Lower-priority items truncated first when over budget
- [ ] Items excluded entirely if truncation insufficient
- [ ] Exclusion summary included in output when items removed
- [ ] Budget calculation uses consistent token estimation
