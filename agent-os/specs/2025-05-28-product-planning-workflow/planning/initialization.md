# Spec Initialization: Product Planning Workflow

## Raw Idea

Implement Milestone 2 from the Red64 roadmap: **Product Planning Workflow**

This milestone adds commands and templates for defining a product's mission, roadmap, and tech stack - creating persistent context that informs all subsequent development work.

## Roadmap Items (from roadmap.md)

> All commands below live in `plugins/core/commands/` directory

7. [ ] Product planning command -- `/red64:plan-product` command that guides users through creating mission, roadmap, and tech-stack documents `M`
8. [ ] Mission document template -- Template and workflow for capturing product pitch, users, problems, differentiators, and success metrics `S`
9. [ ] Roadmap document template -- Template for structured feature roadmap with prioritized checklist format `S`
10. [ ] Tech stack document template -- Template for documenting all technology choices with rationale `XS`
11. [ ] Product context injection -- Hook (in `hooks/hooks.json`) that loads relevant product context (mission-lite, current roadmap item) into prompts `S`

## Context

- **Project**: Red64 - modular plugin framework for Claude Code
- **Tech Stack**: Markdown commands, Python scripts, JSON hooks, YAML config
- **Milestone 1 Complete**: Core Foundation with `/red64:init`, hook infrastructure, context loader, token budget management
- **Output Location**: `.red64/product/` directory (created by `/red64:init`)
- **Files**: `mission.md`, `roadmap.md`, `tech-stack.md`

## Effort Estimate

- Total: ~2-3 weeks (1M + 2S + 1XS)
- Product planning command: M (1 week)
- Mission template: S (2-3 days)
- Roadmap template: S (2-3 days)
- Tech stack template: XS (1 day)
- Product context injection hook: S (2-3 days)
