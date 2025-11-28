# Specification: Red64 Core Foundation

## Goal

Implement the foundational infrastructure for Red64's context-aware functionality, including project initialization, hook infrastructure, context loading, and token budget management that enables intelligent, relevant context injection for every user prompt.

## User Stories

- As a developer, I want to initialize a Red64 project with a single command so that I have the proper directory structure and configuration for context-aware development workflows.
- As a Claude Code user, I want relevant context automatically injected into my prompts so that Claude understands my project standards and current work without manual context copying.

## Specific Requirements

**Project Initialization Command (`/red64:init`)**
- Create `.red64/` directory structure with subdirectories: `product/`, `specs/`, `metrics/`
- Generate default `config.yaml` with token budget settings, context loader settings, and priority levels
- Must be idempotent: safe to run multiple times without overwriting existing config.yaml
- Provide clear success message when initializing new project
- Provide clear skip message when `.red64/` already exists with config
- Command file location: `plugins/core/commands/red64-init.md`

**Hook Infrastructure (`hooks/hooks.json`)**
- Configure `UserPromptSubmit` hook in `plugins/core/hooks/hooks.json`
- Hook invokes `context-loader.py` script with 30-second timeout
- Input: JSON via stdin containing `session_id`, `prompt`, `cwd`, `permission_mode`
- Output: JSON to stdout with `hookSpecificOutput.additionalContext` structure
- Exit code 0 for success, exit code 2 for blocking errors (missing/malformed config)
- Hook must provide clear, actionable error message directing user to run `/red64:init` if config missing

**Context Loader Script (`scripts/context-loader.py`)**
- Main entry point script that orchestrates the context loading pipeline
- Receives prompt via stdin JSON, validates config presence
- Chains to modular sub-scripts: `task-detector.py`, `file-detector.py`, `budget-manager.py`
- Returns structured JSON with detected task type, file types, and prepared context
- Python 3.11+ with full type hints throughout
- Fail strictly (exit code 2) if `.red64/config.yaml` is missing or malformed

**Task Detector Script (`scripts/task-detector.py`)**
- Classify user prompts into task types using built-in keyword patterns
- Task categories: `shape`, `write-spec`, `implement`, `review`, `test`, `debug`, `refactor`
- Input: JSON with prompt text; Output: JSON with detected task type
- Use pattern matching for keywords like "implement", "review", "test", "debug", etc.
- No custom patterns in config for this milestone (built-in only)

**File Detector Script (`scripts/file-detector.py`)**
- Identify file extensions and types mentioned in user prompts
- Detect patterns like `.py`, `.ts`, `.md`, explicit filenames, and path references
- Input: JSON with prompt text; Output: JSON with list of detected file types
- Used to determine which standards might be relevant (future milestone)

**Token Budget Manager (`scripts/budget-manager.py`)**
- Read budget configuration from `.red64/config.yaml` `token_budget` section
- Default budget: 3000 tokens (per product mission metrics)
- Sort context items by configured priority (lower number = higher priority)
- Three-tier overflow handling: (1) truncate lower-priority items, (2) exclude items if needed, (3) include exclusion summary
- Use consistent token estimation (approximate 4 chars per token)
- Budget applies only to injected context, not user prompt

**Configuration Schema (`.red64/config.yaml`)**
- Version field for schema evolution (`version: "1.0"`)
- `token_budget` section: `max_tokens`, `overflow_behavior` with truncate/exclude/summary flags
- `context_loader` section: `enabled`, `task_detection`, `file_type_detection` booleans
- `priorities` section: priority levels for product_mission, current_spec, relevant_standards, tech_stack, roadmap
- `features` section: flags for future features (standards_injection, multi_agent, metrics) all defaulting to false

**Script Architecture and Chaining**
- Each script has single responsibility and can be tested independently
- All scripts use JSON for input (stdin) and output (stdout)
- Main script (`context-loader.py`) orchestrates by piping output between sub-scripts
- Scripts located in `plugins/core/scripts/` directory

## Visual Design

No visual assets provided for this specification.

## Existing Code to Leverage

**Existing Plugin Structure (`plugins/core/`)**
- Directory structure already exists with `commands/`, `agents/`, `hooks/`, `skills/` subdirectories
- `hooks/hooks.json` file exists (currently empty) - add UserPromptSubmit hook configuration
- `.claude-plugin/plugin.json` manifest exists with proper metadata

**Marketplace Configuration (`.claude-plugin/marketplace.json`)**
- Marketplace already configured with core plugin registered
- Follow existing naming conventions and metadata structure for consistency

**Claude Code Hooks Documentation Pattern**
- Use documented input/output format for UserPromptSubmit hooks
- Follow Python pattern: `json.load(sys.stdin)` for input, `print(json.dumps(...))` for output
- Use exit codes: 0 for success, 2 for blocking error

## Out of Scope

- Standards injection and enforcement (Milestone 3)
- Product planning workflow commands like `/red64:plan-product` (Milestone 2)
- Multi-agent orchestration (Milestone 5)
- Metrics collection and SQLite database (Milestone 6)
- Custom keyword patterns in configuration (future enhancement)
- GUI or web interface
- External service integrations
- Actual context file loading and injection (this spec prepares infrastructure only)
- GitHub/Jira/Linear integrations (Milestone 6)
- Migration utilities from Agent OS
