# Product Roadmap

> **Architecture Note**: All Red64 functionality is delivered through Claude Code plugins. Plugins live within marketplaces and contain commands, agents, skills, and hooks. There is no functionality outside the plugin system.

## Milestone 1: Core Foundation & Marketplace

1. [ ] Red64 marketplace repository -- Create `red64-marketplace` repo with `.claude-plugin/marketplace.json` listing all Red64 plugins `S`
2. [ ] Plugin manifest and structure -- Create `red64-core` plugin with `.claude-plugin/plugin.json`, directory structure for `commands/`, `agents/`, `skills/`, `hooks/`, and README documentation `S`
3. [ ] Project initialization command -- `/red64:init` command (in `red64-core/commands/`) that creates `.red64/` directory structure with config.yaml `S`
4. [ ] Hook infrastructure -- Implement `hooks/hooks.json` with `UserPromptSubmit` hook that analyzes prompts and prepares for context injection `M`
5. [ ] Context loader script -- Python script (`scripts/context-loader.py`) that detects file types, keywords, and task type from user prompts `M`
6. [ ] Token budget management -- Configurable token budgets in `.red64/config.yaml` with priority-based selection when limits are reached `S`

## Milestone 2: Product Planning Workflow

> All commands below live in `red64-core/commands/` directory

7. [ ] Product planning command -- `/red64:plan-product` command that guides users through creating mission, roadmap, and tech-stack documents `M`
8. [ ] Mission document template -- Template and workflow for capturing product pitch, users, problems, differentiators, and success metrics `S`
9. [ ] Roadmap document template -- Template for structured feature roadmap with prioritized checklist format `S`
10. [ ] Tech stack document template -- Template for documenting all technology choices with rationale `XS`
11. [ ] Product context injection -- Hook (in `hooks/hooks.json`) that loads relevant product context (mission-lite, current roadmap item) into prompts `S`

## Milestone 3: Standards Plugin Architecture

> Standards are separate plugins in the Red64 marketplace. Each standards plugin uses **Skills** (`skills/SKILL.md`) that Claude autonomously applies based on task context, plus **Hooks** for enforcement.

12. [ ] Standards plugin template -- Define standard plugin structure with `skills/` for guidelines and `hooks/` for enforcement `S`
13. [ ] Standards skill format -- Define `SKILL.md` format that Claude autonomously uses when editing relevant file types `S`
14. [ ] PreToolUse hook for standards -- Hook that triggers standards validation before Edit/Write tool usage `S`
15. [ ] Reference standards plugin: TypeScript -- `red64-standards-typescript` plugin with skills for type system standards `M`
16. [ ] Reference standards plugin: Next.js -- `red64-standards-nextjs` plugin with App Router, Server Components skills `M`
17. [ ] Reference standards plugin: Python -- `red64-standards-python` plugin with PEP compliance and typing skills `M`
18. [ ] Standards composability -- Enable multiple standards plugins to work together via marketplace multi-install `S`

## Milestone 4: Spec-Driven Development Workflow

> All commands and agents below live in `red64-core` plugin

19. [ ] Shape spec command -- `/red64:shape-spec` interactive command that refines rough ideas into well-scoped requirements `M`
20. [ ] Write spec command -- `/red64:write-spec` command that transforms requirements.md into detailed specification.md `M`
21. [ ] Create tasks command -- `/red64:create-tasks` command that breaks specifications into actionable, grouped, prioritized tasks `M`
22. [ ] Implement tasks command -- `/red64:implement-tasks` command for direct implementation with progress tracking `M`
23. [ ] Spec file management -- Active/archive spec handling with proper directory structure and metadata `S`
24. [ ] Progress tracking -- Progress.md generation and updates as tasks are completed `S`
25. [ ] Spec validation agent -- Agent (in `agents/`) that validates spec completeness and alignment with product mission `M`

## Milestone 5: Multi-Agent Orchestration

> All agents below live in `red64-core/agents/` directory

26. [ ] Orchestrator agent -- Meta-agent that coordinates multi-phase workflows and manages agent handoffs `L`
27. [ ] Implementer agent -- Specialized agent for code implementation with standards awareness `M`
28. [ ] Reviewer agent -- Agent for code review against specs and standards `M`
29. [ ] Tester agent -- Agent for test generation and verification `M`
30. [ ] Workflow definition schema -- YAML schema for defining custom multi-phase workflows with dependencies `S`
31. [ ] Built-in workflow: Feature development -- Standard workflow for implementing new features with all phases `M`
32. [ ] Built-in workflow: Bug fix -- Streamlined workflow for diagnosing and fixing bugs `S`
33. [ ] Parallel task execution -- Support for safe parallel implementation of independent tasks `L`
34. [ ] Verification gates -- Automated verification (lint, typecheck, test, build) between workflow phases `M`

## Milestone 6: Extensions and Integrations

> Extensions are separate plugins in the Red64 marketplace

35. [ ] Extension plugin template -- Define extension plugin structure with MCP integration guidelines `S`
36. [ ] Metrics collector infrastructure -- Framework for collecting token usage, task velocity, and quality metrics `M`
37. [ ] Metrics storage -- Local SQLite database for session and project metrics `S`
38. [ ] Metrics reporting command -- `/red64:metrics` command (in `red64-core`) for viewing productivity reports `M`
39. [ ] GitHub extension plugin -- `red64-github` plugin for PR workflow integration using gh CLI `L`
40. [ ] Migration utility -- `/red64:migrate-from-agent-os` command for users transitioning from Agent OS `M`

## Milestone 7: Documentation and Polish

41. [ ] Standards authoring guide -- Documentation for creating custom standards plugins `M`
42. [ ] Extension development guide -- Documentation for creating extension plugins with examples `M`
43. [ ] Getting started documentation -- Comprehensive onboarding guide with video tutorials `M`
44. [ ] Example project -- Sample project demonstrating full Red64 workflow from planning to implementation `L`

---

> **Notes**
> - **Plugin-first architecture**: All functionality lives within plugins distributed through the Red64 marketplace
> - **Plugin types**: `red64-core` (commands, agents, hooks), `red64-standards-*` (skills for coding standards), `red64-*` extensions (integrations)
> - **Skills vs Hooks**: Standards use Skills (Claude applies autonomously) + Hooks (enforcement validation)
> - Order reflects technical dependencies (marketplace before plugins, hooks before standards, etc.)
> - Each milestone builds a complete, testable layer of functionality
> - Effort estimates: XS (1 day), S (2-3 days), M (1 week), L (2 weeks), XL (3+ weeks)
