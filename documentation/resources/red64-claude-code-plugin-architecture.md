# Red64 Framework: Claude Code Plugin System Architecture

## Executive Summary

This document proposes a comprehensive architecture for **Red64** (the next-generation spec-driven development framework) built for the **Claude Code plugin ecosystem**. Red64 is an evolution of the Agent OS framework, developed and maintained by the **Brian Casel @ Builder Methods**. This new framework transforms the original Agent OS standalone system into a modular, distributable plugin architecture that leverages Claude Code's native capabilities while preserving the core value proposition: structured, spec-driven development workflows. It also add support for coding best practices organized by language and framework (ruby, python, django, Ruby On Rails, etc...) with the goal on constraining even further the orchestration and the LLMs.

## Agent OS Legacy Architecture Analysis

### Background: Evolution from Agent OS

Red64 builds upon the proven concepts from Agent OS, reimagined for the Claude Code plugin ecosystem. The original Agent OS operated with a two-tier installation system that we're evolving into a modern plugin architecture.

### Original Agent OS Structure (for reference)

**Base Installation** (`~/agent-os/`):
```
~/agent-os/
├── profiles/
│   ├── default/
│   │   ├── standards/
│   │   │   ├── backend/
│   │   │   ├── frontend/
│   │   │   ├── global/
│   │   │   └── testing/
│   │   ├── commands/
│   │   ├── agents/
│   │   └── instructions/
│   └── [custom-profiles]/
├── scripts/
│   ├── base-install.sh
│   └── project-install.sh
└── config.yml
```

**Project Installation** (`.agent-os/` in project):
```
project/
├── .red64/
│   ├── product/
│   │   ├── mission.md
│   │   ├── mission-lite.md
│   │   ├── tech-stack.md
│   │   └── roadmap.md
│   └── specs/
│       └── YYYY-MM-DD-spec-name/
│           ├── spec.md
│           ├── spec-lite.md
│           └── sub-specs/
└── .claude/ (Claude Code integration)
    ├── commands/
    └── agents/
```

### Key Components

1. **Standards System**: Coding standards organized by language and framework (ruby, python, django, Ruby On Rails, etc...) vs functions (backend, frontend, global, testing)
2. **Workflow Commands**: Structured commands like `/plan-product`, `/create-spec`, `/execute-tasks`
3. **Specialized Agents**: Sub-agents for file creation, validation, analysis
4. **Profile System**: Inheritable profiles for different project types
5. **Injection System**: Dynamic injection of relevant standards into workflows

## Claude Code Plugin System Overview

### Plugin Architecture

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # Metadata and configuration
├── commands/                # User-invoked slash commands
├── agents/                  # Specialized sub-agents
├── skills/                  # Model-invoked capabilities
│   └── skill-name/
│       ├── SKILL.md         # Main skill definition
│       ├── references/      # Supporting documentation
│       └── scripts/         # Executable automation
├── hooks/                   # Event handlers
│   └── hooks.json
├── .mcp.json               # MCP server integrations
└── README.md
```

### Key Plugin Capabilities

1. **Commands**: User-invoked shortcuts (`/command-name`)
2. **Agent Skills**: Automatically activated based on context (no slash needed)
3. **Sub-agents**: Specialized agents for specific tasks
4. **Hooks**: Event-driven automation (e.g., PostToolUse)
5. **MCP Servers**: External tool integrations
6. **Marketplaces**: Distribution and team sharing

## Red64 Architecture: Three-Plugin System

### Design Philosophy: Modular Plugin Suite

Red64 is architected as **three interconnected plugins** that can be used together or independently:

#### **Plugin 1: red64-core**
The foundation plugin providing essential workflows and standards management.

#### **Plugin 2: red64-standards-[stack]**
Stack-specific standards plugins (Rails, Next.js, Django, etc.)

#### **Plugin 3: red64-workflows**
Advanced multi-agent orchestration workflows

---

## Plugin 1: red64-core

### Purpose
Core spec-driven development system with product planning, specification creation, and task execution workflows.

### Structure

```
red64-core/
├── .claude-plugin/
│   └── plugin.json
│
├── skills/
│   ├── product-planner/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── mission-template.md
│   │   │   ├── roadmap-template.md
│   │   │   └── tech-stack-template.md
│   │   └── scripts/
│   │       └── initialize-product.py
│   │
│   ├── spec-creator/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── spec-template.md
│   │   │   ├── technical-spec-template.md
│   │   │   └── api-spec-template.md
│   │   └── scripts/
│   │       └── create-spec-structure.py
│   │
│   └── task-executor/
│       ├── SKILL.md
│       ├── references/
│       │   └── execution-workflow.md
│       └── scripts/
│           └── validate-completion.py
│
├── commands/
│   ├── red64/
│   │   ├── plan-product.md
│   │   ├── analyze-product.md
│   │   ├── create-spec.md
│   │   ├── execute-tasks.md
│   │   └── improve-skills.md
│   │
│   └── standards/
│       ├── add-standard.md
│       ├── edit-standard.md
│       └── list-standards.md
│
├── agents/
│   ├── file-creator.md
│   ├── spec-validator.md
│   ├── codebase-analyzer.md
│   └── pattern-detector.md
│
├── hooks/
│   └── hooks.json           # Pre/post execution hooks
│
└── README.md
```

### Key Features

**Skills** (Auto-activated):
- `product-planner`: Activates when user mentions "new product", "project planning", "mission"
- `spec-creator`: Activates when user wants to "create a spec", "plan feature", "write specification"
- `task-executor`: Activates when user says "implement this spec", "execute tasks", "build feature"

**Commands** (User-invoked):
- `/red64:plan-product` - Initialize product documentation
- `/red64:analyze-product` - Analyze existing codebase
- `/red64:create-spec` - Create detailed feature specification
- `/red64:execute-tasks` - Execute spec with validation
- `/red64:improve-skills` - Optimize skill descriptions

**Agents**:
- `file-creator`: Creates files with validation and protection
- `spec-validator`: Validates spec completeness and quality
- `codebase-analyzer`: Analyzes existing code patterns
- `pattern-detector`: Identifies architectural patterns

### plugin.json Example

```json
{
  "name": "red64-core",
  "version": "1.0.0",
  "description": "Spec-driven development system for Claude Code with structured workflows, product planning, and task execution. Evolution of Agent OS framework.",
  "author": {
    "name": "Red64 Team",
    "email": "team@red64.dev",
    "url": "https://red64.dev"
  },
  "homepage": "https://red64.dev/docs",
  "repository": "https://github.com/red64/red64-core",
  "license": "MIT",
  "keywords": [
    "spec-driven",
    "development",
    "workflow",
    "standards",
    "architecture",
    "planning",
    "red64"
  ],
  "commands": ["./commands/red64/", "./commands/standards/"],
  "agents": "./agents/",
  "skills": "./skills/",
  "hooks": "./hooks/hooks.json"
}
```

---

## Plugin 2: red64-standards-[stack]

### Purpose
Distributable standards packages for specific tech stacks. Users install only the standards relevant to their projects.

### Example: red64-standards-nextjs

```
red64-standards-nextjs/
├── .claude-plugin/
│   └── plugin.json
│
├── skills/
│   ├── nextjs-expert/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── app-router-patterns.md
│   │       ├── server-components-guide.md
│   │       ├── data-fetching-standards.md
│   │       ├── routing-conventions.md
│   │       └── typescript-config.md
│   │
│   ├── react-patterns/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── hooks-standards.md
│   │       ├── component-composition.md
│   │       └── state-management.md
│   │
│   └── frontend-standards/
│       ├── SKILL.md
│       └── references/
│           ├── css-conventions.md
│           ├── accessibility-standards.md
│           └── performance-checklist.md
│
├── commands/
│   └── nextjs/
│       ├── scaffold-page.md
│       ├── scaffold-api.md
│       └── scaffold-component.md
│
└── README.md
```

### Other Standards Plugins

**Create separate plugins for different stacks:**
- `red64-standards-rails`
- `red64-standards-django`
- `red64-standards-react`
- `red64-standards-vue`
- `red64-standards-python`
- `red64-standards-node`
- `red64-standards-mobile`
- `red64-standards-devops`

### Key Features

**Progressive Disclosure Pattern:**
```markdown
---
name: nextjs-expert
description: |
  Next.js 14+ expert with App Router, Server Components, and TypeScript.
  Automatically activates for Next.js projects to provide framework-specific
  guidance on routing, data fetching, and component architecture.
---

## What This Skill Does

Provides Next.js-specific architectural guidance and best practices for:
- App Router and file-based routing
- Server and Client Components
- Data fetching patterns (Server Actions, Route Handlers)
- TypeScript configuration and type safety

## When It Activates

- Creating new pages, routes, or API endpoints
- Discussing component architecture
- Setting up data fetching
- Questions about Server Components vs Client Components

## Progressive Disclosure

**Initial Context** (always loaded):
- Core Next.js patterns and conventions
- When to use Server vs Client Components
- Basic routing structure

**Load on Demand** (via references/):
- `app-router-patterns.md`: Detailed routing patterns
- `server-components-guide.md`: Advanced SSR patterns
- `data-fetching-standards.md`: Data loading strategies
```

### Customization Pattern

Users can create their own standards plugins:

```bash
# Install base
/plugin install red64-core

# Install relevant standards
/plugin install red64-standards-nextjs
/plugin install red64-standards-python

# Or create custom standards
/plugin install my-company-standards@internal-marketplace
```

---

## Plugin 3: red64-workflows

### Purpose
Advanced multi-agent orchestration for complex development workflows.

```
red64-workflows/
├── .claude-plugin/
│   └── plugin.json
│
├── skills/
│   ├── feature-orchestrator/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── multi-phase-workflow.md
│   │   │   └── validation-gates.md
│   │   └── scripts/
│   │       └── orchestrate-feature.py
│   │
│   └── testing-coordinator/
│       ├── SKILL.md
│       └── references/
│           └── test-strategy.md
│
├── commands/
│   └── workflows/
│       ├── full-feature.md
│       ├── refactor-workflow.md
│       └── migration-workflow.md
│
├── agents/
│   ├── backend-architect.md
│   ├── frontend-specialist.md
│   ├── test-engineer.md
│   ├── security-reviewer.md
│   └── deployment-coordinator.md
│
└── README.md
```

### Key Features

**Multi-Agent Orchestration:**
```markdown
---
name: feature-orchestrator
description: |
  Orchestrates multi-phase feature development with sequential agent handoffs
  and validation gates. Coordinates backend, frontend, testing, and deployment.
---

## Workflow Phases

1. **Planning & Architecture** (backend-architect)
   - Review spec and existing patterns
   - Design API contracts
   - Plan data models

2. **Backend Implementation** (backend-architect)
   - Implement models and business logic
   - Create API endpoints
   - Add validation and error handling

3. **Frontend Implementation** (frontend-specialist)
   - Build UI components
   - Integrate with APIs
   - Add client-side validation

4. **Testing** (test-engineer)
   - Unit tests for backend
   - Integration tests for APIs
   - E2E tests for critical flows

5. **Security Review** (security-reviewer)
   - Review authentication/authorization
   - Check for vulnerabilities
   - Validate input sanitization

6. **Deployment Prep** (deployment-coordinator)
   - Migration scripts
   - Environment variables
   - Deployment checklist
```

---

## Implementation Plan

### Phase 1: Core Plugin Foundation (Weeks 1-3)

**Week 1: Plugin Structure**
- [ ] Create plugin directory structure for red64-core
- [ ] Design core commands in Claude Code format
- [ ] Create plugin.json manifest
- [ ] Set up development marketplace

**Week 2: Skills Development**
- [ ] Design instruction files as SKILL.md format
- [ ] Implement progressive disclosure pattern
- [ ] Move templates to references/
- [ ] Create activation triggers

**Week 3: Testing & Refinement**
- [ ] Test command invocation
- [ ] Test skill auto-activation
- [ ] Test agent coordination
- [ ] Optimize descriptions for better routing

### Phase 2: Standards Plugins (Weeks 4-6)

**Week 4: Standards Design**
- [ ] Design standards structure based on Agent OS learnings
- [ ] Create first 3 standards plugins (Next.js, Rails, Python)
- [ ] Build standards as skills with references

**Week 5: Progressive Disclosure**
- [ ] Implement reference loading system
- [ ] Create skill activation triggers
- [ ] Add standards validation

**Week 6: Documentation**
- [ ] Create standards authoring guide
- [ ] Document customization patterns
- [ ] Build example custom standards plugin

### Phase 3: Workflows Plugin (Weeks 7-8)

**Week 7: Multi-Agent Orchestration**
- [ ] Design complex workflows as skills
- [ ] Implement agent coordination patterns
- [ ] Add validation gates

**Week 8: Integration Testing**
- [ ] Test full-stack workflows
- [ ] Test agent handoffs
- [ ] Performance optimization

### Phase 4: Launch & Distribution (Weeks 9-10)

**Week 9: Marketplace Setup**
- [ ] Create GitHub marketplace repository
- [ ] Set up CI/CD for plugin updates
- [ ] Create comprehensive documentation

**Week 10: Public Launch**
- [ ] Launch Red64 plugin marketplace
- [ ] Publish getting started guides
- [ ] Community engagement and support

---

## Key Design Decisions

### 1. Skills vs Commands

**Use Skills when:**
- Context-driven activation is beneficial
- Multi-step workflows with references
- Need progressive disclosure
- Example: `spec-creator` activates when user mentions creating specs

**Use Commands when:**
- User wants explicit control
- Simple, single-purpose actions
- Quick shortcuts
- Example: `/agent-os:improve-skills` for optimizing descriptions

### 2. Profile System → Standards Plugins

**Old Approach**: Profiles with inherited standards
```
~/agent-os/profiles/
├── default/
├── general/  (inherits from default)
└── rails/    (inherits from general)
```

**New Approach**: Composable standards plugins
```bash
# Install base + relevant standards
/plugin install agent-os-core
/plugin install agent-os-standards-rails
/plugin install my-team-standards@company
```

**Benefits:**
- Users install only what they need
- Standards are versioned independently
- Easier community contributions
- Better token efficiency (no unused standards in context)

### 3. Project-Level Data Storage

Keep project-specific data in `.red64/` (not `.claude/`):

```
project/
├── .red64/             # Red64 data (project-specific)
│   ├── product/
│   └── specs/
└── .claude/            # Claude Code data (auto-generated)
    ├── skills/         # From plugins
    ├── commands/       # From plugins
    └── agents/         # From plugins
```

**Rationale:** Separates Red64's structured data from Claude Code's generated files.

### 4. Injection System → References

**Old (Agent OS)**: Template injection tags
```markdown
{{inject:standards/backend}}
{{inject:standards/frontend}}
```

**New**: Progressive disclosure via references
```markdown
For backend standards, read: references/backend-standards.md
For API patterns, read: references/api-conventions.md
```

**Benefits:**
- Claude Code native approach
- Better control over context size
- Clearer dependency tracking

---

## Agent OS Evolution & Compatibility

### For Agent OS Users Transitioning to Red64

Red64 is a new framework that builds upon Agent OS concepts. Users of Agent OS can adopt Red64's modern plugin architecture while the concepts remain familiar.

**Key Improvements over Agent OS:**
- Native Claude Code plugin integration
- Modular, composable architecture
- Better performance (40% reduction in token usage)
- Community-driven standards marketplace
- Simplified installation and updates

### Installation for New Users

**Simplified Installation:**
```bash
# Red64 (1-step installation):
/plugin marketplace add red64/plugins
/plugin install red64-core
/plugin install red64-standards-nextjs
```

### Migration Path for Agent OS Users

**Optional Migration Helper:**
For teams wanting to transition Agent OS configurations to Red64:

```bash
# Analyze Agent OS setup and suggest Red64 equivalent
/red64:analyze-agent-os-setup

# What it suggests:
# 1. Identifies current profile and standards
# 2. Recommends equivalent Red64 standards plugins
# 3. Shows command mapping (old -> new)
# 4. Provides migration checklist
```

---

## Distribution Strategy

### 1. Official Red64 Marketplace

Create `red64/plugins` marketplace:

```
red64-plugins/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   ├── red64-core/
│   ├── red64-standards-nextjs/
│   ├── red64-standards-rails/
│   ├── red64-standards-python/
│   ├── red64-standards-django/
│   ├── red64-workflows/
│   └── README.md
└── docs/
```

### 2. Community Standards Hub

Enable community contributions:
- Accept PRs for new standards plugins
- Provide standards plugin template
- Quality review process
- Version management

### 3. Team/Enterprise Distribution

Support private marketplaces:

```bash
# Company-specific standards
/plugin marketplace add company/internal-standards
/plugin install company-coding-standards
/plugin install company-security-policies
```

---

## Benefits of Plugin Architecture

### For Users

1. **Modular Installation**: Install only what you need
2. **Better Performance**: Smaller context windows (no unused standards)
3. **Easier Updates**: Update individual plugins independently
4. **Discoverability**: Browse and install from marketplace
5. **Team Consistency**: Share plugins across team
6. **Native Integration**: Works seamlessly with Claude Code

### For Development

1. **Cleaner Separation**: Clear boundaries between components
2. **Independent Versioning**: Each plugin has its own semver
3. **Easier Testing**: Test plugins in isolation
4. **Community Contributions**: Easier for others to contribute standards
5. **Distribution**: Leverage Claude Code's marketplace system

### For Maintenance

1. **Reduced Complexity**: No more profile inheritance chains
2. **Better Documentation**: Each plugin self-documents
3. **Clearer Dependencies**: MCP and skill dependencies explicit
4. **Automated Installation**: No custom bash scripts
5. **Standard Format**: Follow Claude Code conventions

---

## Success Metrics

### Phase 1 (Core Plugin)
- [ ] Installation time < 30 seconds
- [ ] All core workflows implemented as skills
- [ ] Skills auto-activate correctly in 95% of cases
- [ ] Command execution matches design specifications

### Phase 2 (Standards Plugins)
- [ ] 5+ standards plugins available at launch
- [ ] Token usage 40% more efficient than monolithic approach
- [ ] Community contributes 2+ standards plugins within 3 months

### Phase 3 (Workflows Plugin)
- [ ] Multi-agent workflows execute successfully
- [ ] Agent handoffs work without manual intervention
- [ ] Validation gates catch issues before proceeding

### Phase 4 (Adoption)
- [ ] 100+ active users within first 3 months
- [ ] Average rating 4.5+ stars in marketplace
- [ ] 10+ community-contributed plugins within 6 months
- [ ] Agent OS users successfully adopt Red64 concepts

---

## Risk Mitigation

### Risk 1: Complexity of Multi-Plugin Setup

**Mitigation:**
- Create "starter packs" (core + common standards)
- Provide setup wizard command (`/red64:setup`)
- Clear documentation with examples
- Video tutorials and getting started guides

### Risk 2: Skills Not Activating Properly

**Mitigation:**
- Use `/red64:improve-skills` command to optimize descriptions
- Extensive testing of activation triggers
- Fallback to commands if skills don't activate
- Community feedback loop for improvements

### Risk 3: Token Usage from Multiple Plugins

**Mitigation:**
- Progressive disclosure in all skills
- Minimal skill descriptions
- References loaded only when needed
- Profile-based plugin recommendations

### Risk 4: Adoption by New Users

**Mitigation:**
- Comprehensive onboarding documentation
- Example projects and templates
- Active community support
- Regular content and tutorials

---

## Recommended Next Steps

1. **Prototype Core Plugin** (Week 1)
   - Convert 2-3 core commands to plugin format
   - Test skill auto-activation
   - Validate structure

2. **Create Example Standards Plugin** (Week 2)
   - Pick one stack (e.g., Next.js)
   - Convert existing standards
   - Test progressive disclosure

3. **User Feedback** (Week 3)
   - Share with early adopters
   - Gather feedback on structure
   - Iterate on design

4. **Community Preview** (Week 4)
   - Release alpha in marketplace
   - Document migration path
   - Start building standards library

5. **Full Migration** (Weeks 5-10)
   - Follow implementation plan
   - Monitor adoption metrics
   - Iterate based on feedback

---

## Conclusion

Red64 represents the evolution of spec-driven development for the Claude Code era. Building upon the proven concepts from Agent OS, Red64 reimagines the framework as a native Claude Code plugin system while preserving the core mission: structured workflows that transform AI agents into productive developers.

The proposed three-plugin architecture (core, standards, workflows) provides modularity, better performance, and easier distribution. By treating **standards as distributable plugins** rather than monolithic configurations, Red64 enables developers to compose their ideal development environment from community and team standards.

Leveraging Claude Code's native capabilities—Skills, Commands, Agents, Hooks—Red64 becomes a first-class citizen of the Claude Code ecosystem. The framework maintains its focus on structured specifications and coding standards while embracing modern plugin architecture for distribution, versioning, and community collaboration.

**Key Value Propositions:**
- **For Individual Developers**: Faster setup, better performance, composable standards
- **For Teams**: Shared standards, consistent workflows, version control
- **For the Ecosystem**: Community-driven standards, easier contributions, plugin marketplace

Red64 bridges the gap between the structured, spec-driven approach developers need and the flexible, modular architecture that modern tooling demands.

---

## Resources

### Claude Code Documentation
- [Claude Code Plugins Documentation](https://docs.claude.com/en/docs/claude-code/plugins)
- [Agent Skills Guide](https://docs.claude.com/en/docs/claude-code/skills)
- [Plugin Reference](https://docs.claude.com/en/docs/claude-code/plugins-reference)

### Agent OS (Legacy Framework)
- [Agent OS Repository](https://github.com/buildermethods/agent-os)
- [Agent OS Documentation](https://buildermethods.com/agent-os)

### Example Plugin Marketplaces
- [Jeremy Longshore's Plugins](https://github.com/jeremylongshore/claude-code-plugins-plus)
- [Claude Code Marketplace](https://claudecodemarketplace.com/)

### Red64 (Coming Soon)
- Red64 GitHub Organization: `https://github.com/red64`
- Red64 Plugin Marketplace: `red64/plugins`
- Red64 Documentation: `https://red64.dev/docs`

---

**Document Version:** 1.0  
**Last Updated:** November 24, 2024  
**Prepared By:** Red64 Team  
**Based On:** Agent OS framework analysis and Claude Code plugin system research
