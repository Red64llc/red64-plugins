# Disable Standards Plugin

Disable a standards plugin to stop applying its coding standards.

## What This Command Does

This command disables a standards plugin by removing it from the `standards.enabled` list in `.red64/config.yaml`. Once disabled, the standards plugin's rules will no longer be applied when editing files.

Command syntax: `/red64:standards-disable <standard-name>`

Example: `/red64:standards-disable typescript`

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

### Step 2: Check If Standard Is Currently Enabled

Read the current `.red64/config.yaml` and check if the standard is in the `standards.enabled` list.

**If standard is not enabled:**

Output the following message and stop:

```
Skipped: Standard '{standard-name}' is not currently enabled.

Currently enabled standards (in priority order):
  1. {first-standard}
  2. {second-standard}
  ...

(Empty if no standards are enabled)
```

**If standard is enabled:**

Continue to Step 3.

### Step 3: Remove Standard from Enabled List

Update `.red64/config.yaml` to remove the standard name from the `standards.enabled` list.

The ordering of remaining standards is preserved.

### Step 4: Output Success Message

Output the following success message:

```
Success: Disabled standards plugin '{standard-name}'.

Currently enabled standards (in priority order):
  1. {first-standard}
  2. {second-standard}
  ...

(Or "No standards currently enabled" if the list is empty)

To re-enable this standard: /red64:standards-enable {standard-name}
To view all standards: /red64:standards-list
```

## Configuration Changes

When a standard is disabled, the `standards` section of `config.yaml` is updated:

Before (with typescript and python enabled):
```yaml
standards:
  enabled:
    - typescript
    - python
  token_budget_priority: 3
```

After disabling `typescript`:
```yaml
standards:
  enabled:
    - python
  token_budget_priority: 3
```

After disabling `python` as well:
```yaml
standards:
  enabled: []
  token_budget_priority: 3
```

## Notes

- This command is idempotent: running it multiple times with the same standard has no effect after the first run
- The standard name should match exactly what was used when enabling
- Disabling a standard does not delete the plugin; it can be re-enabled at any time
- Other settings like `token_budget_priority` are not affected
