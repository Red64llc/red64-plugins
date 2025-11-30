# Spec Requirements: Product Planning Workflow

## Initial Description

Implement Milestone 2 from the Red64 roadmap: **Product Planning Workflow**

This milestone adds commands and templates for defining a product's mission, roadmap, and tech stack - creating persistent context that informs all subsequent development work.

**Roadmap Items:**
- Product planning command -- `/red64:plan-product` command that guides users through creating mission, roadmap, and tech-stack documents (M)
- Mission document template -- Template and workflow for capturing product pitch, users, problems, differentiators, and success metrics (S)
- Roadmap document template -- Template for structured feature roadmap with prioritized checklist format (S)
- Tech stack document template -- Template for documenting all technology choices with rationale (XS)
- Product context injection -- Hook that loads relevant product context (mission-lite, current roadmap item) into prompts (S)

**Output Location:** `.red64/product/` directory (created by `/red64:init`)
**Files:** `mission.md`, `roadmap.md`, `tech-stack.md`

## Requirements Discussion

### First Round Questions

**Q1:** Should this be a single unified command (`/red64:plan-product`) that walks through all three documents in sequence, or separate commands (`/red64:plan-mission`, `/red64:plan-roadmap`, `/red64:plan-tech-stack`) that can be run independently?
**Answer:** 3 separate commands (`/red64:plan-mission`, `/red64:plan-roadmap`, `/red64:plan-tech-stack`)

**Q2:** For the templates, should they be blank scaffolds with section headers only, or pre-filled with example content and helpful comments that users edit?
**Answer:** Pre-filled with example content and comments

**Q3:** For the "mission-lite" context injection, how should the condensed summary be generated -- should users manually create a summary section in mission.md, or should the hook auto-generate a condensed version?
**Answer:** Auto-generated condensed summary from the full document

**Q4:** Should the roadmap template enforce the exact checklist format shown in the existing roadmap.md (numbered items with `[ ]`, descriptions, effort estimates), or allow more flexibility?
**Answer:** Enforce the exact checklist format with effort estimates

**Q5:** For the "current roadmap item" injection, should the hook auto-detect which item is active (first unchecked item), or should users explicitly mark the current item?
**Answer:** Hook should auto-detect which roadmap item is currently active (first unchecked item)

**Q6:** For the tech-stack document, should it include a rationale column like the existing tech-stack.md has, or just list technologies by category?
**Answer:** Just list the technologies (no rationale columns)

**Q7:** Is there anything explicitly out of scope for this milestone?
**Answer:** Nothing explicitly out of scope mentioned

**Q8:** Visual assets?
**Answer:** None provided

### Existing Code to Reference

**Similar Features Identified:**
- Feature: Red64 Init Command - Path: `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/commands/red64-init.md`
- Feature: Existing Hook Infrastructure - Path: `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/hooks/hooks.json`
- Feature: Context Loader Script - Path: `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/scripts/context-loader.py` (if exists)
- Reference Documents: Existing product docs at `/Users/yacin/Workspace/products/red64-framework-project/red64-001/agent-os/product/` (mission.md, roadmap.md, tech-stack.md)

### Follow-up Questions

None required. User's answers were comprehensive and clear.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
N/A

## Requirements Summary

### Functional Requirements

**Commands (3 separate commands in `plugins/core/commands/`):**

1. `/red64:plan-mission`
   - Creates `.red64/product/mission.md` if it doesn't exist
   - Uses pre-filled template with example content and helpful comments
   - Template should include sections for: Pitch, Vision Statement, Problem, Users, Differentiators, Key Features, Success Metrics
   - Users edit the example content to reflect their product

2. `/red64:plan-roadmap`
   - Creates `.red64/product/roadmap.md` if it doesn't exist
   - Uses pre-filled template with example milestones and items
   - Enforces exact checklist format: numbered items with `[ ]`/`[x]`, descriptions, effort estimates (XS/S/M/L/XL)
   - Template includes example milestone structure

3. `/red64:plan-tech-stack`
   - Creates `.red64/product/tech-stack.md` if it doesn't exist
   - Uses pre-filled template with example technologies by category
   - Simple list format (no rationale columns)
   - Categories might include: Languages, Frameworks, Database, Infrastructure, Tools

**Hook Enhancement (in `plugins/core/hooks/hooks.json`):**

4. Product Context Injection
   - Extends existing `UserPromptSubmit` hook
   - Auto-generates condensed "mission-lite" summary from full mission.md
   - Auto-detects current roadmap item (first unchecked `[ ]` item)
   - Injects relevant product context into prompts to inform AI responses
   - Summary generation should be deterministic (not relying on LLM for condensation -- use rule-based extraction of key sections)

### Reusability Opportunities

- Command structure should follow pattern established by `red64-init.md`
- Hook enhancement should extend existing `hooks.json` infrastructure
- Templates should match the structure and quality of existing product docs in `agent-os/product/`
- Context injection should integrate with existing context-loader.py patterns

### Scope Boundaries

**In Scope:**
- Three separate planning commands for mission, roadmap, and tech-stack
- Pre-filled templates with example content for all three documents
- Hook that auto-generates condensed mission summary
- Hook that auto-detects current roadmap item (first unchecked)
- Product context injection into user prompts
- Documents created in `.red64/product/` directory

**Out of Scope:**
- No explicit exclusions mentioned by user
- Implied: No interactive wizard/questionnaire within commands (just template creation)
- Implied: No validation of document content quality
- Implied: No migration of existing product docs to new format

### Technical Considerations

- Commands are Markdown files following Claude Code command format
- Hooks configured in JSON (`hooks.json`)
- Context loader logic in Python (`context-loader.py`)
- All output goes to `.red64/product/` directory (created by `/red64:init`)
- Mission-lite summary should be generated programmatically (rule-based extraction), not via LLM
- Roadmap parsing needs to handle the exact checklist format to find first unchecked item
- Token budget management already exists -- product context injection should respect these limits
