# Red64 Core Plugin

Installing Red64 Plugins in a New Project

---

## Prerequisites

- Claude Code CLI installed
- Python 3.11+ (for hook scripts)
- PyYAML package (`pip install pyyaml`)
- curl (standard on macOS/Linux, for downloading scripts)

---

## Method 1: Install from GitHub (Recommended)

From your new project directory:

```bash
# Step 1: Open Claude Code in your project
cd /path/to/your/project
claude

# Step 2: Add the Red64 marketplace from GitHub
/plugin marketplace add https://github.com/Red64llc/red64-plugins

# Step 3: Install the core plugin
/plugin install core@red64-plugins

# Step 4: Initialize Red64 in your project (downloads scripts automatically)
/red64:init
```

---

## Method 2: Configure in settings.json (Team/Project Setup)

Create `.claude/settings.json` in your project:

```json
{
  "permissions": {
    "allow": []
  },
  "marketplaces": [
    "https://github.com/Red64llc/red64-plugins"
  ],
  "plugins": {
    "core@red64-plugins": {
      "enabled": true
    }
  }
}
```

Then run:
```bash
cd /path/to/your/project
claude
/red64:init
```

---

## Method 3: Local Development Installation

For local development or offline use:

```bash
# Step 1: Clone the plugins repo
git clone git@github.com:Red64llc/red64-plugins.git ~/red64-plugins

# Step 2: Add marketplace from local path
/plugin marketplace add ~/red64-plugins

# Step 3: Install and initialize
/plugin install core@red64-plugins
/red64:init
```

Or set the `RED64_PLUGIN_DIR` environment variable:
```bash
export RED64_PLUGIN_DIR=~/red64-plugins/core
```

---

## What Gets Installed

### Commands

| Command                | Description                                      |
|------------------------|--------------------------------------------------|
| `/red64:init`          | Initialize .red64/ config directory              |
| `/red64:plan-mission`  | Create product mission document                  |
| `/red64:plan-roadmap`  | Create product roadmap document                  |
| `/red64:plan-tech-stack` | Create tech stack document                     |

### Hooks & Scripts

| Component              | Description                                      |
|------------------------|--------------------------------------------------|
| UserPromptSubmit hook  | Analyzes prompts and injects context             |
| context-loader.py      | Task detection, file detection, token budget     |
| mission-summarizer.py  | Extracts condensed mission summary               |
| roadmap-parser.py      | Detects current roadmap item                     |
| product-context.py     | Orchestrates product context injection           |

---

## Product Planning Workflow

After initializing Red64, set up your product context:

```bash
# Create your product planning documents
/red64:plan-mission
/red64:plan-roadmap
/red64:plan-tech-stack
```

This creates three documents in `.red64/product/`:

| Document        | Purpose                                          |
|-----------------|--------------------------------------------------|
| mission.md      | Product pitch, vision, problem, users, features  |
| roadmap.md      | Checklist of milestones with effort estimates    |
| tech-stack.md   | Technologies organized by category               |

Once created, product context is automatically injected into every prompt:
- **Mission-lite summary**: Condensed pitch, problem, and key features
- **Current work item**: First unchecked roadmap item is auto-detected

---

## Verify Installation

```bash
# Check plugin is installed
/plugin

# Initialize Red64 in your project
/red64:init

# Verify .red64/ directory was created
ls -la .red64/
```

Expected output:
```
.red64/
├── config.yaml
├── product/
├── scripts/
│   ├── context-loader.py
│   ├── context-loader.sh
│   ├── config_utils.py
│   └── ... (other scripts)
├── specs/
└── metrics/
```

After running planning commands:
```
.red64/
├── config.yaml
├── product/
│   ├── mission.md
│   ├── roadmap.md
│   └── tech-stack.md
├── scripts/
├── specs/
└── metrics/
```

---

## Quick Start Script

For convenience, here's a one-liner:

```bash
cd /path/to/your/project && claude -p "/plugin marketplace add https://github.com/Red64llc/red64-plugins && /plugin install core@red64-plugins && /red64:init"
```

Full setup with product planning:

```bash
cd /path/to/your/project && claude -p "/plugin marketplace add https://github.com/Red64llc/red64-plugins && /plugin install core@red64-plugins && /red64:init && /red64:plan-mission && /red64:plan-roadmap && /red64:plan-tech-stack"
```
