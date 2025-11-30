# Specification: Standards Plugin Architecture

## Goal

Enable composable, stack-specific coding standards that integrate with the existing plugin system, are automatically loaded via file-type detection, and enforced through PreToolUse hooks that can block Edit/Write operations violating enabled standards.

## User Stories

- As a developer, I want to enable TypeScript standards via a CLI command so that Claude automatically applies coding conventions when editing TypeScript files
- As a team lead, I want to configure which standards plugins are active and their priority order so that multiple standards can coexist without conflicts

## Specific Requirements

**Standards Plugin Template Structure**
- Standards plugins follow existing plugin structure: `.claude-plugin/plugin.json`, `skills/`, `hooks/` directories
- Plugin manifest must include `category: "standards"` to distinguish from other plugin types
- Create template at `plugins/standards-template/` as reference for new standards plugins
- Include `standards.json` manifest in plugin root declaring file types this standard applies to (e.g., `["*.ts", "*.tsx"]`)
- Plugin directory naming convention: `red64-standards-{language}` (e.g., `red64-standards-typescript`)

**SKILL.md Format Specification**
- Skills located in `skills/` directory, one file per skill (e.g., `naming-conventions.md`, `error-handling.md`)
- Each SKILL.md must include both positive guidance (DO) and negative examples (DON'T) sections
- Format: `## DO` section with good patterns, `## DON'T` section with anti-patterns and explanations
- Include code examples in fenced code blocks with language identifiers
- Skills are loaded into context when editing relevant file types, guiding Claude's code generation
- Target skill length: 200-500 tokens per skill to balance comprehensiveness with token budget

**PreToolUse Hook for Standards Validation**
- Create `plugins/core/hooks/standards-validator.py` script invoked on PreToolUse events
- Hook analyzes target file path to determine applicable standards based on file extension
- Hook has BLOCKING capability: returns `decision: "block"` with `reason` for standards violations
- Block conditions: attempting to use patterns explicitly listed in DONT sections of active standards
- Advisory mode fallback: if blocking seems too strict, include `suggestion` field with guidance
- Hook must respect enabled standards list from `.red64/config.yaml`

**Standards Enable/Disable CLI Command**
- Create command file `plugins/core/commands/red64-standards-enable.md`
- Command syntax: `/red64:standards-enable <standard-name>` (e.g., `/red64:standards-enable typescript`)
- Command reads current `.red64/config.yaml`, adds standard to `standards.enabled` list
- Command validates that referenced standard plugin exists in plugins directory
- Saves updated config with ordering preserved (first enabled = highest priority)
- Create companion command `red64-standards-disable.md` to remove standards from config

**Config.yaml Schema Extension for Standards**
- Add new `standards` section to config schema in `config_schema.py`
- `standards.enabled`: ordered list of enabled standard plugin names (order = precedence)
- `standards.token_budget_priority`: integer for priority of standards in overall token budget
- Extend `merge_with_defaults` in `config_utils.py` to handle new standards section
- Default: `standards.enabled: []`, `standards.token_budget_priority: 3`

**Token Budget Priority at Project Level**
- Standards token budget priority configured in `config.yaml` under `standards.token_budget_priority`
- Value integrates with existing `priorities` section (lower number = higher priority)
- Budget manager script must be updated to include standards skills in budget calculations
- When multiple standards enabled, their skills share the allocated token budget proportionally

**TypeScript Reference Standards Plugin**
- Create fully-featured reference plugin at `plugins/red64-standards-typescript/`
- Include `.claude-plugin/plugin.json` with metadata, `category: "standards"`
- Include `standards.json` with file patterns: `["*.ts", "*.tsx"]`
- Create skills for: naming-conventions, type-safety, error-handling, module-structure, async-patterns
- Each skill follows SKILL.md format with DO/DON'T sections and code examples
- Include `hooks/` directory with empty `hooks.json` (standards use core validator hook)

**Ordering-Based Conflict Resolution**
- When multiple standards plugins define rules for same file type, order in config determines precedence
- First standard in `standards.enabled` list wins for conflicting rules
- Context loader should note when multiple standards apply and which takes precedence
- No merge strategy: later standards supplement but don't override earlier ones

**Integration with Context Loader**
- Extend `context-loader.py` to load relevant standards skills based on detected file types
- Match file types in prompt against `standards.json` file patterns from enabled plugins
- Include matched skills in context output with `## Standards: {plugin-name}` header
- Respect token budget: standards skills prioritized according to `standards.token_budget_priority`

**Hook Infrastructure Extension**
- Add `PreToolUse` hook configuration to `plugins/core/hooks/hooks.json`
- PreToolUse hook receives: `tool_name`, `tool_input`, including file paths for Edit/Write
- Hook must return JSON with `decision` field: `"allow"`, `"block"`, or `"suggest"`
- Blocking response format: `{"decision": "block", "reason": "violates X standard"}`

## Visual Design

No visual assets provided for this specification.

## Existing Code to Leverage

**Plugin Structure (`plugins/core/.claude-plugin/plugin.json`)**
- Use exact same manifest format for standards plugins
- Extend with `category` field to distinguish standards plugins
- Follow existing `skills/`, `hooks/` directory structure pattern

**Hooks Infrastructure (`plugins/core/hooks/hooks.json`)**
- Extend existing hooks.json to add PreToolUse hook alongside UserPromptSubmit
- Follow same structure: array of hook configurations with type, command, timeout
- Reference `plugins/core/scripts/context-loader.py` pattern for stdin/stdout JSON I/O

**Context Loader Pipeline (`plugins/core/scripts/context-loader.py`)**
- Extend `format_additional_context` function to include standards skills
- Use existing `run_sub_script` pattern to call new standards-related scripts
- Follow TypedDict schema pattern for standards-related input/output types

**Configuration Utilities (`plugins/core/scripts/config_schema.py`, `config_utils.py`)**
- Extend `Red64Config` TypedDict with new `Standards` section
- Add standards to `get_default_config()` with empty enabled list
- Update `merge_with_defaults` to handle standards section merging

**Command Structure (`plugins/core/commands/red64-init.md`)**
- Follow exact command file format: "What This Command Does", "Execution Steps", numbered steps
- Include idempotency checks (e.g., validate standard exists before enabling)
- Match success/skip message formatting style

## Out of Scope

- Next.js reference standards plugin (deferred to future milestone)
- Python reference standards plugin (deferred to future milestone)
- Per-plugin token budget configuration (project-level only per requirements)
- Advisory-only mode without blocking capability (blocking is required)
- Interactive prompt-based configuration (CLI command only)
- GUI or web interface for standards management
- Automatic standards detection/recommendation based on project analysis
- Standards versioning or update mechanisms
- Remote/marketplace distribution of standards plugins
- Custom pattern matching beyond file extension globs
