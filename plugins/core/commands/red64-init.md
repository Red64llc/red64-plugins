# Initialize Red64 Project

Initialize the Red64 project structure in the current working directory.

## What This Command Does

This command creates the `.red64/` directory structure with proper configuration for context-aware development workflows.

## Execution Steps

### Step 1: Check for Existing Configuration

First, check if `.red64/config.yaml` already exists in the current working directory.

```bash
test -f .red64/config.yaml && echo "exists" || echo "missing"
```

### Step 2: Handle Based on Existence

**If config.yaml already exists:**

Output the following message and stop:

```
Skipped: .red64/config.yaml already exists. No changes made.

Your Red64 project is already initialized.
```

**If config.yaml does NOT exist:**

Continue to Step 3.

### Step 3: Create Directory Structure

Create the `.red64/` directory and its subdirectories:

```bash
mkdir -p .red64/product .red64/specs .red64/metrics
```

### Step 4: Generate Default Configuration

Create `.red64/config.yaml` with the following default configuration:

```yaml
version: "1.0"
token_budget:
  max_tokens: 3000
  overflow_behavior:
    truncate: true
    exclude: true
    summary: true
context_loader:
  enabled: true
  task_detection: true
  file_type_detection: true
priorities:
  product_mission: 1
  current_spec: 2
  relevant_standards: 3
  tech_stack: 4
  roadmap: 5
features:
  standards_injection: false
  multi_agent: false
  metrics: false
```

### Step 5: Output Success Message

Output the following success message:

```
Success: Created .red64/ directory with default configuration.

Directory structure created:
  .red64/
  .red64/config.yaml
  .red64/product/
  .red64/specs/
  .red64/metrics/

Your Red64 project is ready for context-aware development.
```

## Configuration Schema Reference

| Section | Field | Default | Description |
|---------|-------|---------|-------------|
| `version` | - | "1.0" | Schema version for future evolution |
| `token_budget` | `max_tokens` | 3000 | Maximum tokens for injected context |
| `token_budget` | `overflow_behavior.truncate` | true | Truncate lower-priority items first |
| `token_budget` | `overflow_behavior.exclude` | true | Exclude items if truncation insufficient |
| `token_budget` | `overflow_behavior.summary` | true | Include summary of excluded items |
| `context_loader` | `enabled` | true | Enable context loading on prompts |
| `context_loader` | `task_detection` | true | Detect task type from prompts |
| `context_loader` | `file_type_detection` | true | Detect file types from prompts |
| `priorities` | `product_mission` | 1 | Priority for product mission (highest) |
| `priorities` | `current_spec` | 2 | Priority for current spec |
| `priorities` | `relevant_standards` | 3 | Priority for coding standards |
| `priorities` | `tech_stack` | 4 | Priority for tech stack info |
| `priorities` | `roadmap` | 5 | Priority for roadmap (lowest) |
| `features` | `standards_injection` | false | Future: Auto-inject standards |
| `features` | `multi_agent` | false | Future: Multi-agent support |
| `features` | `metrics` | false | Future: Metrics collection |

## Notes

- This command is idempotent: running it multiple times will not overwrite existing configuration
- The default token budget of 3000 tokens aligns with the product mission metrics
- Priority values are lower number = higher priority
- All features flags default to false for this milestone
