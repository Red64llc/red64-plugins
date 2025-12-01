# Enable Standards Plugin

Enable a standards plugin to apply coding standards for specific file types.

## What This Command Does

This command enables a standards plugin by adding it to the `standards.enabled` list in `.red64/config.yaml`. Once enabled, the standards plugin's rules will be applied when editing files matching the plugin's file patterns.

Command syntax: `/red64:standards-enable <standard-name>`

Example: `/red64:standards-enable typescript`

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

### Step 2: Validate Standard Plugin Exists

Check if the standards plugin exists in the plugins directory. The plugin should be named `red64-standards-{name}` and have a valid structure.

Look for the plugin at: `plugins/red64-standards-{standard-name}/`

Validate the following:
1. Plugin directory exists
2. `.claude-plugin/plugin.json` exists and has `"category": "standards"`
3. `standards.json` exists with `file_patterns` array

**If plugin is not found or invalid:**

Output the following message and stop:

```
Error: Standards plugin 'red64-standards-{standard-name}' not found or invalid.

Available standards plugins can be listed with /red64:standards-list

To create a new standards plugin, copy the template from plugins/standards-template/
```

**If plugin is valid:**

Continue to Step 3.

### Step 3: Check If Already Enabled

Read the current `.red64/config.yaml` and check if the standard is already in the `standards.enabled` list.

**If standard is already enabled:**

Output the following message and stop:

```
Skipped: Standard '{standard-name}' is already enabled.

Currently enabled standards (in priority order):
  1. {first-standard}
  2. {second-standard}
  ...
```

**If standard is not yet enabled:**

Continue to Step 4.

### Step 4: Add Standard to Enabled List

Update `.red64/config.yaml` to add the standard name to the end of the `standards.enabled` list.

The standard should be appended to the end of the list because:
- First standard in list has highest priority
- Newly added standards have lowest priority by default
- User can reorder manually if needed

### Step 5: Output Success Message

Output the following success message:

```
Success: Enabled standards plugin '{standard-name}'.

Currently enabled standards (in priority order):
  1. {first-standard}
  2. {second-standard}
  ...
  N. {newly-added-standard}

Standards will be applied when editing files matching: {file_patterns}

To disable this standard: /red64:standards-disable {standard-name}
To view all standards: /red64:standards-list
```

## Configuration Changes

When a standard is enabled, the `standards` section of `config.yaml` is updated:

Before:
```yaml
standards:
  enabled: []
  token_budget_priority: 3
```

After enabling `typescript`:
```yaml
standards:
  enabled:
    - typescript
  token_budget_priority: 3
```

After enabling `python` as well:
```yaml
standards:
  enabled:
    - typescript
    - python
  token_budget_priority: 3
```

## Priority and Ordering

- Standards are listed in priority order (first = highest priority)
- When multiple standards apply to the same file type, the first one in the list takes precedence
- New standards are added at the end (lowest priority)
- Users can manually edit `config.yaml` to reorder standards

## Notes

- This command is idempotent: running it multiple times with the same standard has no effect after the first run
- The standard name should match the plugin directory name without the `red64-standards-` prefix
- Standards only apply to files matching the patterns defined in the plugin's `standards.json`
