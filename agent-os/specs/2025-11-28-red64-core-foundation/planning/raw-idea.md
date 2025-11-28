# Raw Idea: Red64 Core Foundation

This spec covers 4 interconnected items from Milestone 1 of the Red64 roadmap:

1. **Project initialization command** - `/red64:init` command (in `plugins/core/commands/`) that creates `.red64/` directory structure with config.yaml

2. **Hook infrastructure** - Implement `hooks/hooks.json` with `UserPromptSubmit` hook that analyzes prompts and prepares for context injection

3. **Context loader script** - Python script (`scripts/context-loader.py`) that detects file types, keywords, and task type from user prompts

4. **Token budget management** - Configurable token budgets in `.red64/config.yaml` with priority-based selection when limits are reached

These components work together to form the core infrastructure that enables Red64's context-aware functionality.
