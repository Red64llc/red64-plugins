# List Standards Plugins

List all available standards plugins and show which are currently enabled.

## What This Command Does

This command displays all available standards plugins in the plugins directory and indicates which ones are currently enabled in the project configuration. It also shows the priority order for enabled standards.

Command syntax: `/red64:standards-list`

## Execution Steps

### Step 1: Check for Red64 Configuration

First, check if `.red64/config.yaml` exists in the current working directory.

```bash
test -f .red64/config.yaml && echo "exists" || echo "missing"
```

**If config.yaml is missing:**

Output the following message and stop:

```
Error: .red64/config.yaml not found. Run /red64:init first to initialize your project.
```

**If config.yaml exists:**

Continue to Step 2.

### Step 2: Find Available Standards Plugins

Scan the `plugins/` directory for directories matching the pattern `red64-standards-*`.

For each matching directory, verify it has:
1. `.claude-plugin/plugin.json` with `"category": "standards"`
2. `standards.json` with `file_patterns` array

### Step 3: Load Current Configuration

Read `.red64/config.yaml` and extract the `standards.enabled` list to determine which standards are currently enabled.

### Step 4: Output Standards List

Output the standards information in the following format:

```
Standards Plugins
=================

Enabled (in priority order):
  1. typescript - Applies to: *.ts, *.tsx
  2. python - Applies to: *.py
  ...

Available (not enabled):
  - react - Applies to: *.jsx, *.tsx
  - nextjs - Applies to: *.ts, *.tsx, *.js, *.jsx
  ...

(Or "No standards plugins available" if none found)
(Or "No standards currently enabled" if enabled list is empty)

Commands:
  Enable a standard:  /red64:standards-enable <name>
  Disable a standard: /red64:standards-disable <name>

Priority Notes:
  - Standards are applied in priority order (first = highest)
  - When multiple standards match a file, the highest priority wins
  - Edit .red64/config.yaml to change priority order
```

## Output Format Details

### For Enabled Standards

Enabled standards are listed in their configured priority order, showing:
- Priority number (1 = highest priority)
- Standard name (without `red64-standards-` prefix)
- File patterns the standard applies to

### For Available Standards

Available standards (plugins found but not enabled) are listed alphabetically, showing:
- Standard name
- File patterns the standard applies to

## Example Outputs

### With Multiple Standards

```
Standards Plugins
=================

Enabled (in priority order):
  1. typescript - Applies to: *.ts, *.tsx
  2. python - Applies to: *.py

Available (not enabled):
  - react - Applies to: *.jsx, *.tsx
  - nextjs - Applies to: *.ts, *.tsx

Commands:
  Enable a standard:  /red64:standards-enable <name>
  Disable a standard: /red64:standards-disable <name>

Priority Notes:
  - Standards are applied in priority order (first = highest)
  - When multiple standards match a file, the highest priority wins
  - Edit .red64/config.yaml to change priority order
```

### With No Standards Enabled

```
Standards Plugins
=================

Enabled (in priority order):
  No standards currently enabled.

Available (not enabled):
  - typescript - Applies to: *.ts, *.tsx
  - python - Applies to: *.py

Commands:
  Enable a standard:  /red64:standards-enable <name>
  Disable a standard: /red64:standards-disable <name>
```

### With No Standards Plugins Found

```
Standards Plugins
=================

No standards plugins found in plugins/ directory.

To create a standards plugin:
  1. Copy plugins/standards-template/ to plugins/red64-standards-{name}/
  2. Update plugin.json and standards.json with your configuration
  3. Add skills in the skills/ directory

Then enable with: /red64:standards-enable <name>
```

## Notes

- This command is read-only; it does not modify any configuration
- Standards plugins must follow the naming convention `red64-standards-{name}`
- The plugin must have `category: "standards"` in plugin.json to be recognized
- File patterns are read from each plugin's `standards.json`
