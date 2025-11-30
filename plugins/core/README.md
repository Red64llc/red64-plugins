# Red64 Core Plugin

Installing Red64 Plugins in a New Project

---

## Prerequisites

- Claude Code CLI installed
- Python 3.11+ (for hook scripts)
- PyYAML package (pip install pyyaml)

---

## Method 1: Add Marketplace from Local Path

From your new project directory (e.g., /Users/yacin/Workspace/products/testing-001):

```bash
# Step 1: Open Claude Code in your project
cd /Users/yacin/Workspace/products/testing-001
claude

# Step 2: Add the Red64 marketplace
/plugin marketplace add /Users/yacin/Workspace/products/red64

# Step 3: Install the core plugin
/plugin install core@red64-plugins

# Step 4: Initialize Red64 in your project
/red64:init
```

---

## Method 2: Configure in settings.json (Team/Project Setup)

Create .claude/settings.json in your project:

```json
{
  "permissions": {
    "allow": []
  },
  "marketplaces": [
    "/Users/yacin/Workspace/products/red64"
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
cd /Users/yacin/Workspace/products/testing-001
claude
/red64:init
```

---

## Method 3: Git-based Installation (for distribution)

Once Red64 is published to a git repository:

```bash
# Add marketplace from GitHub
/plugin marketplace add https://github.com/red64/plugins

# Install core plugin
/plugin install core@red64-plugins
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
├── specs/
└── metrics/
```

---

## Quick Start Script

For convenience, here's a one-liner:

```bash
cd /Users/yacin/Workspace/products/testing-001 && claude -p "/plugin marketplace add /Users/yacin/Workspace/products/red64 && /plugin install core@red64-plugins && /red64:init"
```

Full setup with product planning:

```bash
cd /Users/yacin/Workspace/products/testing-001 && claude -p "/plugin marketplace add /Users/yacin/Workspace/products/red64 && /plugin install core@red64-plugins && /red64:init && /red64:plan-mission && /red64:plan-roadmap && /red64:plan-tech-stack"
```
