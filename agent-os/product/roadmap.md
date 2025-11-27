# Product Roadmap

## Milestone 1: Core Foundation

1. [ ] Plugin manifest and structure -- Create `red64-core` plugin with `.claude-plugin/plugin.json`, directory structure for commands/agents/hooks/scripts, and README documentation `S`
2. [ ] Project initialization command -- `/red64:init` command that creates `.red64/` directory structure with config.yaml and generates minimal CLAUDE.md integration `S`
3. [ ] Hook infrastructure -- Implement `hooks.json` with `UserPromptSubmit` hook that analyzes prompts and prepares for context injection `M`
4. [ ] Context loader script -- Python script (`context-loader.py`) that detects file types, keywords, and task type from user prompts `M`
5. [ ] Token budget management -- Configurable token budgets in `.red64/config.yaml` with priority-based selection when limits are reached `S`

## Milestone 2: Product Planning Workflow

6. [ ] Product planning command -- `/red64:plan-product` command that guides users through creating mission, roadmap, and tech-stack documents `M`
7. [ ] Mission document template -- Template and workflow for capturing product pitch, users, problems, differentiators, and success metrics `S`
8. [ ] Roadmap document template -- Template for structured feature roadmap with prioritized checklist format `S`
9. [ ] Tech stack document template -- Template for documenting all technology choices with rationale `XS`
10. [ ] Product context injection -- Hook that loads relevant product context (mission-lite, current roadmap item) into prompts `S`

## Milestone 3: Standards Plugin Architecture

11. [ ] Standards manifest schema -- Define `manifest.json` schema for standards plugins including triggers, priorities, and composability declarations `S`
12. [ ] Standards injector script -- `standards-injector.py` that matches task signals against standards manifests and injects relevant content `M`
13. [ ] PreToolUse hook for standards -- Hook that triggers standards injection before Edit/Write/MultiEdit tool usage `S`
14. [ ] Reference standards plugin: TypeScript -- `red64-standards-typescript` with type system standards, organized by trigger patterns `M`
15. [ ] Reference standards plugin: Next.js -- `red64-standards-nextjs` with App Router, Server Components, and styling standards `M`
16. [ ] Reference standards plugin: Python -- `red64-standards-python` with PEP compliance, typing, and project structure standards `M`
17. [ ] Standards composability -- Enable multiple standards plugins to work together, merging and prioritizing their standards `S`

## Milestone 4: Spec-Driven Development Workflow

18. [ ] Shape spec command -- `/red64:shape-spec` interactive command that refines rough ideas into well-scoped requirements `M`
19. [ ] Write spec command -- `/red64:write-spec` command that transforms requirements.md into detailed specification.md `M`
20. [ ] Create tasks command -- `/red64:create-tasks` command that breaks specifications into actionable, grouped, prioritized tasks `M`
21. [ ] Implement tasks command -- `/red64:implement-tasks` command for direct implementation with progress tracking `M`
22. [ ] Spec file management -- Active/archive spec handling with proper directory structure and metadata `S`
23. [ ] Progress tracking -- Progress.md generation and updates as tasks are completed `S`
24. [ ] Spec validation agent -- Agent that validates spec completeness, consistency, and alignment with product mission `M`

## Milestone 5: Multi-Agent Orchestration

25. [ ] Orchestrator agent -- Meta-agent that coordinates multi-phase workflows and manages agent handoffs `L`
26. [ ] Implementer agent -- Specialized agent for code implementation with standards awareness `M`
27. [ ] Reviewer agent -- Agent for code review against specs and standards `M`
28. [ ] Tester agent -- Agent for test generation and verification `M`
29. [ ] Workflow definition schema -- YAML schema for defining custom multi-phase workflows with dependencies `S`
30. [ ] Built-in workflow: Feature development -- Standard workflow for implementing new features with all phases `M`
31. [ ] Built-in workflow: Bug fix -- Streamlined workflow for diagnosing and fixing bugs `S`
32. [ ] Parallel task execution -- Support for safe parallel implementation of independent tasks `L`
33. [ ] Verification gates -- Automated verification (lint, typecheck, test, build) between workflow phases `M`

## Milestone 6: Extensions and Integrations

34. [ ] Extension interface specification -- Define adapter contract, hook integration points, and MCP guidelines for extensions `S`
35. [ ] Metrics collector infrastructure -- Framework for collecting token usage, task velocity, and quality metrics `M`
36. [ ] Metrics storage -- Local SQLite database for session and project metrics `S`
37. [ ] Metrics reporting command -- `/red64:metrics` command for viewing productivity and quality reports `M`
38. [ ] GitHub extension -- `red64-github` plugin for PR workflow integration using gh CLI `L`
39. [ ] Migration utility -- `/red64:migrate-from-agent-os` command for users transitioning from Agent OS `M`

## Milestone 7: Distribution and Polish

40. [ ] Marketplace setup -- Configure official Red64 plugin marketplace repository structure `S`
41. [ ] Standards authoring guide -- Documentation for creating custom standards plugins `M`
42. [ ] Extension development guide -- Documentation for creating extension plugins with examples `M`
43. [ ] Getting started documentation -- Comprehensive onboarding guide with video tutorials `M`
44. [ ] Example project -- Sample project demonstrating full Red64 workflow from planning to implementation `L`

---

> Notes
> - Order reflects technical dependencies (hooks before standards injection, standards before spec workflow, etc.)
> - Each milestone builds a complete, testable layer of functionality
> - Effort estimates: XS (1 day), S (2-3 days), M (1 week), L (2 weeks), XL (3+ weeks)
> - Priorities guided by mission: core infrastructure first, then the spec-driven workflow that differentiates Red64
