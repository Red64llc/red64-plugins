# Tech Stack

## Overview

Red64 is a Claude Code plugin framework. The codebase consists of plugin definitions (commands, agents, hooks), automation scripts, configuration schemas, and documentation. There is no traditional frontend/backend architecture -- Red64 extends Claude Code's capabilities through its native plugin system.

---

## Core Plugin Technologies

### Commands and Agents
- **Format:** Markdown (`.md`)
- **Location:** `commands/`, `agents/` directories within plugins
- **Rationale:** Claude Code's native format for defining slash commands and specialized agents. Markdown provides clear structure and is readable by both humans and Claude.

### Automation Scripts
- **Language:** Python 3.11+
- **Location:** `scripts/` directory within plugins
- **Key Scripts:**
  - `context-loader.py` -- Analyzes prompts and determines relevant context
  - `standards-injector.py` -- Injects matching standards based on task signals
  - `task-analyzer.py` -- Classifies task types for workflow routing
- **Rationale:** Python provides robust text processing, JSON/YAML handling, and is the most common language for Claude Code plugin scripts. Type hints used throughout.

### Hook Configuration
- **Format:** JSON (`hooks.json`)
- **Location:** `hooks/` directory within plugins
- **Rationale:** Claude Code's native format for event-driven automation. JSON provides strict schema validation.

---

## Configuration and Data Formats

### Plugin Manifests
- **Format:** JSON (`plugin.json`)
- **Schema:** Claude Code plugin specification
- **Location:** `.claude-plugin/` directory
- **Rationale:** Required format for Claude Code plugin registration and marketplace distribution.

### Standards Manifests
- **Format:** JSON (`manifest.json`)
- **Purpose:** Declares standards metadata, trigger patterns, priorities, and composability
- **Rationale:** JSON provides strict typing for programmatic matching logic while remaining human-editable.

### Workflow Definitions
- **Format:** YAML (`.yaml`)
- **Location:** `workflows/` directory
- **Purpose:** Define multi-phase workflows with agent assignments, dependencies, and verification gates
- **Rationale:** YAML's readability and support for complex nested structures makes it ideal for workflow definitions that humans need to author and review.

### Project Configuration
- **Format:** YAML (`config.yaml`)
- **Location:** `.red64/` project directory
- **Purpose:** Project-specific settings (token budgets, enabled standards, custom workflows)
- **Rationale:** YAML is more readable than JSON for configuration files that users will edit.

### Product Documentation
- **Format:** Markdown (`.md`)
- **Location:** `.red64/product/` directory
- **Files:** `mission.md`, `roadmap.md`, `tech-stack.md`
- **Rationale:** Markdown is human-readable, version-control friendly, and can be directly consumed by Claude.

### Specifications
- **Format:** Markdown (`.md`)
- **Location:** `.red64/specs/` directory
- **Files:** `requirements.md`, `specification.md`, `tasks.md`, `progress.md`
- **Rationale:** Structured markdown with consistent heading conventions enables both human editing and programmatic parsing.

---

## Data Storage

### Metrics Database
- **Technology:** SQLite
- **Location:** `.red64/metrics/sessions.db`
- **Purpose:** Local storage for usage analytics, task velocity, and quality metrics
- **Rationale:** SQLite requires no external dependencies, works offline, and provides SQL querying for reports.

### Project State
- **Technology:** File-based (Markdown + YAML)
- **Location:** `.red64/` directory
- **Rationale:** No database needed for project state -- files provide version control integration, human readability, and portability.

---

## External Dependencies

### Claude Code Plugin System
- **Requirement:** Claude Code with plugin support
- **Components Used:** Commands, Agents, Skills, Hooks, MCP integration
- **Rationale:** Red64 is built as a native Claude Code plugin ecosystem, not a standalone tool.

### Python Standard Library
- **Key Modules:** `json`, `yaml` (via PyYAML), `pathlib`, `sqlite3`, `re`, `typing`
- **Rationale:** Minimize external dependencies for plugin scripts.

### Optional: PyYAML
- **Purpose:** YAML parsing in Python scripts
- **Installation:** `pip install pyyaml`
- **Rationale:** Required for workflow definition parsing.

---

## Development Tools

### Version Control
- **Tool:** Git
- **Branching:** Feature branches, PR-based workflow
- **Rationale:** Standard for all development; Red64's file-based architecture is designed for clean diffs.

### Code Quality
- **Python:** `ruff` for linting and formatting
- **Markdown:** `markdownlint` for documentation consistency
- **Rationale:** Automated checks ensure consistent style across plugin development.

### Testing
- **Python Scripts:** `pytest` with type checking via `mypy`
- **Integration:** Manual testing via Claude Code plugin loading
- **Rationale:** Scripts need unit tests; plugin behavior requires manual validation in Claude Code.

---

## Distribution

### Marketplace
- **Platform:** Claude Code Plugin Marketplace
- **Repository:** GitHub (`red64/plugins`)
- **Versioning:** Semantic versioning (semver)
- **Rationale:** Native Claude Code distribution mechanism enables one-command installation.

### Plugin Packaging
- **Format:** Directory-based plugins (no compilation/bundling)
- **Installation:** `/plugin install red64-core`
- **Rationale:** Claude Code plugins are installed as directories, not packages.

---

## Design Decisions and Rationale

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Plugin scripts language | Python | Most supported in Claude Code ecosystem, excellent text processing |
| Configuration format | YAML | Human-readable, supports comments, better for files users edit |
| Schema/manifest format | JSON | Strict typing, better for programmatic parsing |
| Documentation format | Markdown | Universal, version-control friendly, Claude-native |
| Local storage | SQLite | Zero-config, portable, SQL querying |
| No build step | Direct files | Simpler development, easier debugging, standard Claude Code pattern |
| No external services | Local-only | Works offline, no account requirements, privacy-preserving |
