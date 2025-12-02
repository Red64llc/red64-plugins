# Initialize Red64 Project

Initialize the Red64 project structure in the current working directory.

## What This Command Does

This command creates the `.red64/` directory structure with proper configuration for context-aware development workflows, and copies the necessary hook scripts.

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
mkdir -p .red64/product .red64/specs .red64/metrics .red64/scripts
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
standards:
  enabled: []
  token_budget_priority: 3
```

### Step 5: Download Hook Scripts from GitHub

Download the Red64 hook scripts to `.red64/scripts/` from the official GitHub repository.

**GitHub Repository:** `https://github.com/Red64llc/red64-plugins`

**Base URL for raw files:** `https://raw.githubusercontent.com/Red64llc/red64-plugins/main/plugins/core`

Use `curl` to download each script (works on macOS and Linux):

```bash
# Base URL for raw GitHub content
BASE_URL="https://raw.githubusercontent.com/Red64llc/red64-plugins/main/plugins/core"

# Scripts from scripts/ directory
SCRIPTS=(
  "context-loader.py"
  "context-loader.sh"
  "config_utils.py"
  "config_schema.py"
  "budget-manager.py"
  "file-detector.py"
  "task-detector.py"
  "mission-summarizer.py"
  "product-context.py"
  "roadmap-parser.py"
  "standards-loader.py"
)

# Scripts from hooks/ directory
HOOKS=(
  "standards-validator.py"
  "standards-validator.sh"
)

# Download scripts
echo "Downloading Red64 scripts from GitHub..."
for script in "${SCRIPTS[@]}"; do
  curl -sSL "$BASE_URL/scripts/$script" -o ".red64/scripts/$script"
done

for hook in "${HOOKS[@]}"; do
  curl -sSL "$BASE_URL/hooks/$hook" -o ".red64/scripts/$hook"
done

# Make shell scripts executable
chmod +x .red64/scripts/*.sh

echo "Scripts downloaded successfully."
```

**Fallback: If curl fails or no internet connection:**

If downloading fails, you can manually copy scripts from a local Red64 installation:

```bash
# Option A: Use RED64_PLUGIN_DIR environment variable
if [ -n "$RED64_PLUGIN_DIR" ]; then
  cp "$RED64_PLUGIN_DIR/scripts/"*.py .red64/scripts/
  cp "$RED64_PLUGIN_DIR/scripts/"*.sh .red64/scripts/
  cp "$RED64_PLUGIN_DIR/hooks/"*.py .red64/scripts/
  cp "$RED64_PLUGIN_DIR/hooks/"*.sh .red64/scripts/
  chmod +x .red64/scripts/*.sh
fi
```

**Required scripts:**

| Script | Purpose |
|--------|---------|
| `context-loader.py` | Main context loading hook |
| `context-loader.sh` | Shell wrapper for portability |
| `config_utils.py` | Configuration utilities |
| `config_schema.py` | Configuration schema definitions |
| `budget-manager.py` | Token budget management |
| `file-detector.py` | File type detection |
| `task-detector.py` | Task type detection |
| `mission-summarizer.py` | Mission file summarization |
| `product-context.py` | Product context loading |
| `roadmap-parser.py` | Roadmap file parsing |
| `standards-loader.py` | Standards plugin loading |
| `standards-validator.py` | PreToolUse standards validation |
| `standards-validator.sh` | Shell wrapper for portability |

### Step 6: Output Success Message

Output the following success message:

```
Success: Created .red64/ directory with default configuration.

Directory structure created:
  .red64/
  .red64/config.yaml
  .red64/product/
  .red64/specs/
  .red64/metrics/
  .red64/scripts/

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
| `standards` | `enabled` | [] | List of enabled standard plugin names (order = precedence) |
| `standards` | `token_budget_priority` | 3 | Priority for standards in token budget allocation |

## Notes

- This command is idempotent: running it multiple times will not overwrite existing configuration
- The default token budget of 3000 tokens aligns with the product mission metrics
- Priority values are lower number = higher priority
- All features flags default to false for this milestone
- Standards enabled list is empty by default; use `/red64:standards-enable` to add standards
