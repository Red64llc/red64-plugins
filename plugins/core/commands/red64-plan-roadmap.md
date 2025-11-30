# Plan Product Roadmap

Create the product roadmap document with a pre-filled template.

## What This Command Does

This command creates the `.red64/product/roadmap.md` file with a structured template for tracking milestones and tasks using checkboxes and effort estimates.

## Execution Steps

### Step 1: Check for Existing Roadmap Document

First, check if `.red64/product/roadmap.md` already exists in the current working directory.

```bash
test -f .red64/product/roadmap.md && echo "exists" || echo "missing"
```

### Step 2: Handle Based on Existence

**If roadmap.md already exists:**

Output the following message and stop:

```
Skipped: .red64/product/roadmap.md already exists. No changes made.

Your product roadmap is already defined. Edit the file directly to make changes.
```

**If roadmap.md does NOT exist:**

Continue to Step 3.

### Step 3: Create Product Directory

Ensure the product directory exists:

```bash
mkdir -p .red64/product
```

### Step 4: Create Roadmap Document

Create `.red64/product/roadmap.md` with the following template content:

```markdown
# Product Roadmap

<!-- This document tracks your product's development milestones and tasks. Use checkboxes to track progress. Effort estimates: XS (1 day), S (2-3 days), M (1 week), L (2 weeks), XL (3+ weeks) -->

> **Progress Tracking**: Mark items as complete by changing `[ ]` to `[x]`. The first unchecked item is considered your current work item.

## Milestone 1: [Foundation/Core/MVP Name]

<!-- Define your first milestone. Include 4-8 items that together deliver a complete, testable layer of functionality. -->

1. [ ] [First task description] -- [Brief explanation of what this accomplishes] `S`
2. [ ] [Second task description] -- [Brief explanation of what this accomplishes] `M`
3. [ ] [Third task description] -- [Brief explanation of what this accomplishes] `S`
4. [ ] [Fourth task description] -- [Brief explanation of what this accomplishes] `XS`
5. [ ] [Fifth task description] -- [Brief explanation of what this accomplishes] `M`

## Milestone 2: [Feature Expansion Name]

<!-- Define your second milestone. Build on the foundation with additional capabilities. -->

6. [ ] [Task description] -- [Brief explanation of what this accomplishes] `M`
7. [ ] [Task description] -- [Brief explanation of what this accomplishes] `S`
8. [ ] [Task description] -- [Brief explanation of what this accomplishes] `L`
9. [ ] [Task description] -- [Brief explanation of what this accomplishes] `S`
10. [ ] [Task description] -- [Brief explanation of what this accomplishes] `M`

## Milestone 3: [Polish/Integration Name]

<!-- Define your third milestone. Focus on integration, polish, and production-readiness. -->

11. [ ] [Task description] -- [Brief explanation of what this accomplishes] `S`
12. [ ] [Task description] -- [Brief explanation of what this accomplishes] `M`
13. [ ] [Task description] -- [Brief explanation of what this accomplishes] `L`
14. [ ] [Task description] -- [Brief explanation of what this accomplishes] `M`

---

> **Notes**
> - Order reflects technical dependencies (earlier items should be completed before later ones)
> - Each milestone should build a complete, testable layer of functionality
> - Effort estimates: XS (1 day), S (2-3 days), M (1 week), L (2 weeks), XL (3+ weeks)
> - Update this document as priorities shift or scope changes
```

### Step 5: Output Success Message

Output the following success message:

```
Success: Created .red64/product/roadmap.md

Your product roadmap template is ready. Edit the file to define:
  - Milestones with clear goals
  - Tasks with checkboxes for progress tracking
  - Effort estimates (XS/S/M/L/XL) for each task

The first unchecked [ ] item is automatically detected as your current work item.

File location: .red64/product/roadmap.md
```

## Notes

- This command is idempotent: running it multiple times will not overwrite existing content
- The checklist format enables automatic detection of the current work item
- Effort estimates help with planning: XS (1 day), S (2-3 days), M (1 week), L (2 weeks), XL (3+ weeks)
