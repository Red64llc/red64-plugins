<p align="center">
  <img src="assets/bouncing-red64.gif" alt="Red64 Logo" width="80">
</p>

# Red64

**An open-source plugin framework for Claude Code**

> **Warning**
> This project is under active development and not yet ready for production use. APIs, commands, and functionality may change without notice. Use at your own risk.

Red64 transforms Claude Code from a capable assistant into a disciplined enterprise development partner. It captures your coding standards, tech stack specifics, and development workflows to help Claude produce quality code reliably and consistently.

---

## What is Red64?

Red64 is an open-source meta-framework built natively on Claude Code's plugin system. It addresses the enterprise software development lifecycle where **robustness, performance, predictability, compliance, and security** are critical to success.

### What Red64 is NOT

Red64 is not for vibe coding. It's for teams who need:
- Deterministic, spec-driven development workflows
- Consistent adherence to coding standards
- Measurable productivity improvements
- Enterprise-grade software quality

---

## Key Features

### Plugin-First Architecture
Every component is a discrete, installable plugin. Start with core functionality and add what you need.

### Intelligent Context Loading
Standards are loaded only when relevant—not dumped into every conversation. Hook-based injection analyzes your task and loads only what's needed, staying within token budgets.

### Composable Standards
Stack-specific coding standards as independent, combinable plugins. Mix TypeScript + Next.js + your team's custom conventions seamlessly.

### Spec-Driven Workflows
Structured development process from product planning through implementation, with verification gates at each step.

### Extension-Ready
Clean interfaces for metrics, SDLC tool integrations (GitHub, Jira), and custom workflows.

---

## Works With

- **Claude Code** — Built natively on Claude Code's plugin system
- **Any Tech Stack** — Composable standards plugins for TypeScript, Python, Next.js, and more
- **New or Existing Projects** — Initialize in any codebase
- **Teams of Any Size** — From solo developers to enterprise teams

---

## Installation

### Quick Start

```bash
# Open Claude Code in your project
cd /path/to/your/project
claude

# Add the Red64 marketplace
/plugin marketplace add https://github.com/Red64llc/red64-plugins

# Install the core plugin
/plugin install core@red64-plugins

# Initialize Red64 in your project
/red64:init
```

### Full Documentation

Visit **[red64.io](https://red64.io)** for comprehensive documentation, guides, and tutorials.

---

## Core Commands

| Command | Description |
|---------|-------------|
| `/red64:init` | Initialize Red64 in your project |
| `/red64:plan-mission` | Create product mission document |
| `/red64:plan-roadmap` | Create product roadmap |
| `/red64:plan-tech-stack` | Define your technology stack |
| `/red64:standards-enable` | Enable a coding standards plugin |
| `/red64:standards-list` | List available standards |

---

## Plugin Ecosystem

```
RED64 ECOSYSTEM
├── red64-core              — Base workflows, context management, hooks infrastructure
├── red64-standards-*       — Composable coding standards (typescript, python, nextjs...)
├── red64-workflows         — Multi-agent orchestration for complex features
└── red64-extensions        — Integrations (metrics, github, jira...)
```

### Standards Plugins

Standards are **not skills**. They are reference documents intelligently injected by hooks when relevant to your task. This ensures consistent code quality without wasting tokens.

Available standards:
- `red64-standards-typescript` — TypeScript best practices
- More coming soon...

---

## How It Works

### Intelligent Context Injection

```
User Prompt → Analyze Task → Detect File Types → Load Relevant Standards → Inject Context
                                    ↓
                            Only what's needed,
                            within token budget
```

### Project Structure

```
your-project/
├── .red64/                 # Red64 project data
│   ├── config.yaml         # Project configuration
│   ├── product/            # Product context (mission, roadmap, tech-stack)
│   ├── scripts/            # Hook scripts (auto-downloaded)
│   ├── specs/              # Feature specifications
│   └── metrics/            # Usage and quality metrics
└── src/                    # Your code
```

---

## Functional Goals

- Re-introduce deterministic approaches to SDLC
- Language and framework-specific coding standards
- Support for team-specific coding styles
- Productivity improvements through tool automations
- Feedback through productivity metrics
- Smart strategy for MCP server loading
- Measurable ROI for team augmentation

---

## Requirements

- Claude Code CLI
- Python 3.11+ (for hook scripts)
- PyYAML (`pip install pyyaml`)

---

## Contributing

Red64 is open source and welcomes contributions. See the [GitHub repository](https://github.com/Red64llc/red64-plugins) for:
- Bug reports and feature requests
- Standards plugin contributions
- Documentation improvements

---

## About

Red64 is a project sponsored by **[Red64 Consulting](https://red64.io)**.

The framework is heavily influenced by excellent projects like [Agent OS](https://github.com/buildermethods/agent-os) and reimagines their spec-driven workflow as a modular plugin architecture native to Claude Code.

---

## License

Copyright Red64 LLC, 2025. All rights reserved.

Author: Yacin Bahi <yacin@red64.io>

---

**[red64.io](https://red64.io)** | **[GitHub](https://github.com/Red64llc/red64-plugins)**
