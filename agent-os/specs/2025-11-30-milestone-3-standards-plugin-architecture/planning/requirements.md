# Spec Requirements: Milestone 3 - Standards Plugin Architecture

## Initial Description

Milestone 3 from the product roadmap focuses on building the Standards Plugin Architecture for Red64. This includes:

- Standards plugin template structure with `skills/` for guidelines and `hooks/` for enforcement
- Standards skill format (`SKILL.md`) that Claude autonomously uses when editing relevant file types
- PreToolUse hook for standards validation before Edit/Write tool usage
- Reference standards plugins (TypeScript, Next.js, Python)
- Standards composability enabling multiple standards plugins to work together

The goal is to enable composable, stack-specific coding standards that are intelligently loaded via hooks and autonomously applied by Claude through skills.

## Requirements Discussion

### First Round Questions

**Q1:** Will standards plugins follow the existing plugin structure (`.claude-plugin/plugin.json`, `skills/`, `hooks/` directories)?
**Answer:** Yes, standards plugins will follow the existing plugin structure - CONFIRMED.

**Q2:** Should skills (`SKILL.md` files) include positive guidance only, or also negative examples (what NOT to do)?
**Answer:** Skills should include BOTH positive guidance AND negative examples (what NOT to do).

**Q3:** For the PreToolUse hook, should it be advisory (warn but allow) or blocking (prevent operations that violate standards)?
**Answer:** The hook should be able to BLOCK operations that violate standards (not just advisory).

**Q4:** How should users configure which standards plugins are active? Options: command-line interface, config.yaml editing, interactive prompt?
**Answer:** A command-line interface that saves enabled standards into `.red64/config.yaml` (e.g., `/red64:standards-enable typescript`).

**Q5:** Should token budget priority for standards be configurable per-plugin (in manifest) or at the project level (in config.yaml)?
**Answer:** Token budget priority for standards is set at the PROJECT LEVEL in config.yaml (not per-plugin manifest).

**Q6:** For the reference implementation, should we build all three plugins (TypeScript, Next.js, Python) or focus on one fully-featured example first?
**Answer:** Build only ONE fully-featured reference plugin (likely TypeScript) - others are out of scope for this milestone.

**Q7:** When multiple standards plugins are enabled, how should conflicts be resolved? Options: ordering/priority, merge strategies, error on conflict?
**Answer:** When multiple standards overlap, use ORDERING for conflict resolution (order in config determines precedence).

**Q8:** Is there anything explicitly out of scope for this milestone that I should note?
**Answer:** Nothing explicitly marked as out of scope by user (beyond limiting to one reference plugin).

### Existing Code to Reference

**Similar Features Identified:**
- Feature: Core Plugin - Path: `/Users/yacin/Workspace/products/red64-framework-project/red64-001/plugins/core/`
- Components to potentially reuse: Plugin structure (`.claude-plugin/plugin.json`), `skills/`, `hooks/` directory patterns
- Backend logic to reference: Existing hooks infrastructure in `plugins/core/hooks/`, context loader in `plugins/core/scripts/context-loader.py`

### Follow-up Questions

No follow-up questions were needed - all requirements were clearly specified.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
N/A

## Requirements Summary

### Functional Requirements
- Standards plugin template that follows existing plugin structure with `skills/` and `hooks/` directories
- `SKILL.md` format specification including both positive guidance AND negative examples (anti-patterns)
- PreToolUse hook that can BLOCK Edit/Write operations that violate enabled standards
- Command-line interface (`/red64:standards-enable <standard>`) for enabling/disabling standards plugins
- Configuration storage in `.red64/config.yaml` for enabled standards and their priority order
- Token budget priority management at project level in config.yaml
- One fully-featured reference plugin: TypeScript standards (`red64-standards-typescript`)
- Standards composability with ordering-based conflict resolution (config order = precedence)

### Reusability Opportunities
- Existing plugin structure in `plugins/core/.claude-plugin/plugin.json` as template
- Existing `hooks/` directory pattern and `hooks.json` format
- Existing `skills/` directory structure
- Context loader script patterns in `plugins/core/scripts/context-loader.py`
- Token budget management logic already implemented in Milestone 1

### Scope Boundaries

**In Scope:**
- Standards plugin template definition
- SKILL.md format specification with positive/negative guidance
- PreToolUse hook for standards enforcement (blocking capability)
- `/red64:standards-enable` command for CLI-based configuration
- Project-level token budget priority in config.yaml
- One reference plugin: TypeScript standards
- Ordering-based conflict resolution for multiple standards

**Out of Scope:**
- Next.js reference standards plugin (deferred)
- Python reference standards plugin (deferred)
- Per-plugin token budget priority (using project-level instead)
- Advisory-only hooks (implementing blocking capability)
- Interactive prompt-based configuration (using CLI instead)

### Technical Considerations
- Standards plugins must integrate with existing marketplace structure
- PreToolUse hook must analyze file types and operation context to determine applicable standards
- Hook must be able to block operations, requiring clear error messaging for violations
- Config.yaml schema needs extension for standards configuration section
- Ordering in config.yaml determines conflict resolution precedence
- Skills should be comprehensive with both do's and don'ts for better Claude guidance
- TypeScript plugin should serve as template for future standards plugins
