# Specification: Product Planning Workflow

## Goal

Enable Red64 users to define their product's mission, roadmap, and tech stack through three dedicated commands that create pre-filled template documents, with automatic context injection into all subsequent prompts.

## User Stories

- As a developer starting a new project, I want to quickly scaffold product planning documents so that my AI assistant understands the product context in all future sessions
- As a technical lead, I want my roadmap to automatically highlight the current work item so that Claude stays focused on the active milestone

## Specific Requirements

**`/red64:plan-mission` Command**
- Create `plugins/core/commands/red64-plan-mission.md` following the pattern in `red64-init.md`
- Check if `.red64/product/mission.md` already exists; if so, output skip message and stop
- Create `.red64/product/mission.md` with pre-filled template containing example content and helpful comments
- Template sections: Pitch, Vision Statement, Problem, Users, Differentiators, Key Features, Success Metrics
- Example content should be realistic and demonstrate the expected format (not lorem ipsum)
- Output success message listing the created file path

**`/red64:plan-roadmap` Command**
- Create `plugins/core/commands/red64-plan-roadmap.md` following the pattern in `red64-init.md`
- Check if `.red64/product/roadmap.md` already exists; if so, output skip message and stop
- Create `.red64/product/roadmap.md` with pre-filled template enforcing exact checklist format
- Template format: numbered items with `[ ]`/`[x]` checkboxes, descriptions, and effort estimates (XS/S/M/L/XL)
- Include 2-3 example milestones with example items to demonstrate the structure
- Output success message listing the created file path

**`/red64:plan-tech-stack` Command**
- Create `plugins/core/commands/red64-plan-tech-stack.md` following the pattern in `red64-init.md`
- Check if `.red64/product/tech-stack.md` already exists; if so, output skip message and stop
- Create `.red64/product/tech-stack.md` with pre-filled template listing technologies by category
- Categories to include: Languages, Frameworks, Database, Infrastructure, Development Tools
- Simple list format without rationale columns (unlike the existing reference tech-stack.md)
- Output success message listing the created file path

**Mission-Lite Auto-Generation**
- Create Python script `plugins/core/scripts/mission-summarizer.py` that extracts a condensed summary from mission.md
- Use rule-based extraction (not LLM): extract first sentence from Pitch, first sentence from Problem, bulleted list from Key Features
- Target summary length: 150-300 tokens
- Return structured JSON output with `mission_lite` field containing the condensed text
- Script follows patterns from existing `context-loader.py` with TypedDict schemas and explicit error handling

**Roadmap Item Auto-Detection**
- Create Python script `plugins/core/scripts/roadmap-parser.py` that parses roadmap.md to find the current work item
- Parse the exact checklist format: numbered items with `[ ]` checkboxes
- Return the first unchecked item (first `[ ]` found, not `[x]`)
- Return structured JSON with `current_item` containing: item number, item title, effort estimate, parent milestone
- Handle edge cases: all items checked (return null), malformed format (return error), no roadmap file (return null)

**Product Context Injection Hook**
- Extend existing `UserPromptSubmit` hook in `plugins/core/hooks/hooks.json` to call a new product context script
- Create `plugins/core/scripts/product-context.py` that orchestrates mission-summarizer and roadmap-parser
- Format output as Markdown block with sections: "Product Context" header, mission-lite summary, current roadmap item
- Integrate with existing `context-loader.py` by adding product context to the `format_additional_context` output
- Respect existing token budget configuration from `.red64/config.yaml`

**Template Quality Standards**
- Example content in templates should be professional-quality, not placeholder text
- Comments in templates should use HTML comment syntax `<!-- -->` for sections users should edit
- Each template should include a brief header explaining the document's purpose
- Templates should match the quality and structure of existing docs in `agent-os/product/`

## Visual Design

No visual assets provided.

## Existing Code to Leverage

**`plugins/core/commands/red64-init.md`**
- Follow the exact structure: "What This Command Does", "Execution Steps", step-by-step numbered sections
- Replicate the idempotency pattern: check existence first, skip with message if exists
- Match the success/skip message format with file paths listed
- Use same bash code block patterns for file system operations

**`plugins/core/hooks/hooks.json`**
- Extend the existing `UserPromptSubmit` hook array rather than replacing
- Follow the same structure: type "command", command path, timeout value
- Hook already calls `context-loader.py` which can be extended to include product context

**`plugins/core/scripts/context-loader.py`**
- Follow the same patterns: TypedDict for input/output schemas, subprocess chaining to sub-scripts
- Use same error handling: try/except with fallback to safe defaults, no blocking errors for missing files
- Match the JSON I/O pattern: read from stdin, write to stdout
- Integrate product context into `format_additional_context` function

**`agent-os/product/mission.md`, `roadmap.md`, `tech-stack.md`**
- Use these as reference for template section structure and content quality
- Mission template should have same sections as the reference mission.md
- Roadmap template should use the exact same checklist format with effort estimates
- Tech-stack template can be simpler (no rationale columns per requirements)

## Out of Scope

- Interactive wizard or questionnaire within commands (commands just create templates)
- Validation of document content quality or completeness
- Migration of existing product docs to new template format
- LLM-based summarization of mission document (must be rule-based extraction)
- Manual marking of current roadmap item (must be auto-detected)
- Rationale columns in tech-stack template (requirement specifies simple list only)
- Any modifications to `.red64/config.yaml` schema
- Any new configuration options for product planning
- Product context injection for non-UserPromptSubmit hooks
