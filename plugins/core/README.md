  # Introduction
  ---
  Installing Red64 Plugins in a New Project

  Prerequisites

  - Claude Code CLI installed
  - Python 3.11+ (for hook scripts)
  - PyYAML package (pip install pyyaml)

  ---
  Method 1: Add Marketplace from Local Path

  From your new project directory (e.g., /Users/yacin/Workspace/products/testing-001):

  # Step 1: Open Claude Code in your project
  cd /Users/yacin/Workspace/products/testing-001
  claude

  # Step 2: Add the Red64 marketplace
  /plugin marketplace add /Users/yacin/Workspace/products/red64

  # Step 3: Install the core plugin
  /plugin install core@red64-plugins

  # Step 4: Initialize Red64 in your project
  /red64:init

  ---
  Method 2: Configure in settings.json (Team/Project Setup)

  Create .claude/settings.json in your project:

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

  Then run:
  cd /Users/yacin/Workspace/products/testing-001
  claude
  /red64:init

  ---
  Method 3: Git-based Installation (for distribution)

  Once Red64 is published to a git repository:

  # Add marketplace from GitHub
  /plugin marketplace add https://github.com/red64/plugins

  # Install core plugin
  /plugin install core@red64-plugins

  ---
  What Gets Installed

  | Component              | Description                                    |
  |------------------------|------------------------------------------------|
  | /red64:init            | Command to initialize .red64/ config directory |
  | UserPromptSubmit hook  | Analyzes prompts and injects context           |
  | Context loader scripts | Task detection, file detection, token budget   |

  ---
  Verify Installation

  # Check plugin is installed
  /plugin

  # Initialize Red64 in your project
  /red64:init

  # Verify .red64/ directory was created
  ls -la .red64/

  Expected output:
  .red64/
  ├── config.yaml
  ├── product/
  ├── specs/
  └── metrics/

  ---
  Quick Start Script

  For convenience, here's a one-liner:

  cd /Users/yacin/Workspace/products/testing-001 && claude -p "/plugin marketplace add /Users/yacin/Workspace/products/red64 &&
  /plugin install core@red64-plugins && /red64:init"
