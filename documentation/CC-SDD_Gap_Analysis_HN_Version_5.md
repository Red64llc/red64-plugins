# The Gap Between AI-Generated Specs and Production Code

**Why spec-driven development tools excel at planning but fail at the last mile**

*December 2025 - Yacin Bahi - v5 *

---

## TL;DR

After a year of building products at an AI-first venture studio, one thing is clear: **you cannot ship reliable software with AI coding agents without spec-driven development**. Vibe coding is fine for prototypes, but the moment you need predictable outcomes—consistent architecture, maintainable code, features that actually match requirements—you need specs. Without them, AI-generated code is a slot machine: sometimes brilliant, often unusable, always unpredictable.

Spec-driven development (SDD) solves this. Tools like cc-sdd, Agent OS, and GitHub Spec Kit give AI agents the structured context they need to produce consistent, production-quality code. We can't work without it.

**But there's a gap.** I've been using cc-sdd (a spec-driven development framework for Claude Code) for several months. It's genuinely excellent at the specification phase—requirements, designs, task decomposition. But the implementation phase has no Git integration, no automated quality checks, and no feedback loops.

This post documents the gap, compares approaches from Agent OS and other frameworks, and proposes a workflow that integrates Git worktrees, CodeRabbit CLI, and GitHub Actions. **I also discuss the uncomfortable vendor lock-in this creates and explore fully open source alternatives.**

**The core insight**: Spec-driven tools solve the "what" and "why" perfectly. What's missing is the "how"—specifically, automated enforcement that catches issues before code reaches main, and intelligent context management that doesn't waste tokens loading irrelevant standards or MCP tool definitions on every request.

---

## Part 1: The cc-sdd Gap Analysis

### What cc-sdd Does Exceptionally Well

cc-sdd (github.com/gotalab/cc-sdd) has transformed AI-assisted development by providing a structured workflow:

```
Requirements → Design → Tasks → Implementation
```

The framework delivers:

| Phase | Capability | Quality Rating |
|-------|------------|----------------|
| **Requirements** | Structured requirements documents with acceptance criteria | ★★★★★ |
| **Design** | Technical design with component diagrams, API contracts | ★★★★★ |
| **Tasks** | Decomposed, parallelizable tasks with dependencies | ★★★★★ |
| **Implementation** | AI-generated code based on specifications | ★★★☆☆ |

The first three phases produce professional-grade documentation that rivals human-authored specifications. The structured approach eliminates the 70% overhead traditionally spent on meetings, documentation ceremonies, and scattered context.

### The Current Implementation Workflow

The typical cc-sdd implementation flow today looks like this:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Current cc-sdd Workflow                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. /kiro-spec-create "feature-name"                                        │
│     ↓                                                                       │
│  2. /kiro-spec-design → Produces Requirements.md, Design.md                 │
│     ↓                                                                       │
│  3. /kiro-spec-tasks → Generates Tasks.md with N tasks                      │
│     ↓                                                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  IMPLEMENTATION LOOP (Manual, Sequential)                              │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │ │
│  │  │  For each Task N:                                                │  │ │
│  │  │    1. /kiro-task-impl N                    ← AI implements       │  │ │
│  │  │    2. Manual code review                   ← Human reviews       │  │ │
│  │  │    3. git add . && git commit              ← Manual commit       │  │ │
│  │  │    4. Move to Task N+1                     ← Repeat              │  │ │
│  │  └──────────────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│     ↓                                                                       │
│  4. Feature complete (hopefully...)                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Gap: What's Missing

The implementation phase has several critical gaps:

#### 1. No Git Flow Integration

- **No automatic branch creation** per feature or task
- **No pull request workflow** for code review
- **No isolation** between concurrent feature development
- **Manual commits** break the flow and introduce inconsistency

#### 2. No Automated Code Quality Gates

- **No code smell detection** before commit
- **No automated review** by tools like CodeRabbit or SonarQube
- **Manual review** is subjective and inconsistent
- Quality tools not integrated into the implementation loop

#### 3. No Feedback Loop to AI

- When code quality issues are found, there's no structured way to feed this back to Claude
- No integration with MCP servers that could provide real-time code analysis
- No automated fix-review-fix cycle

#### ✅ What cc-sdd DOES Have: Design Rules via Steering

**Important clarification**: cc-sdd already provides a mechanism for design rules through the `/kiro:steering-custom` command. This creates custom steering documents in `.kiro/steering/` with three inclusion modes:

| Inclusion Mode | When Loaded | Use Case |
|----------------|-------------|----------|
| **Always** | Every AI interaction | Universal security policies |
| **Conditional** | When editing matching files | `"src/api/**/*"` → API standards |
| **Manual** | When referenced with `@filename.md` | Specialized workflows |

**Common custom steering types already supported:**
- `api-standards.md` - REST/GraphQL conventions
- `testing.md` - Test organization, mocking strategies  
- `code-style.md` - Language conventions, formatting
- `security.md` - Input validation, auth patterns
- `database.md` - Schema design, migration strategies

The gap is not in *defining* design rules—cc-sdd handles this well. The gap is in **enforcing** those rules through automated tooling before code is committed.

### Impact Analysis

| Gap | Impact | Severity |
|-----|--------|----------|
| No branch isolation | Task implementations can conflict with each other | High |
| No automated quality gates | Code smells and anti-patterns reach main branch | High |
| Manual commit process | Breaks developer flow, inconsistent commit messages | Medium |
| No PR workflow | No audit trail, no automated CI/CD triggers | High |
| No feedback loop | Quality issues not automatically fed back to AI for fixing | Critical |

**Note**: Design rules definition is NOT a gap—cc-sdd's `/kiro:steering-custom` handles this. The gap is in automated *enforcement* of those rules.

---

## Part 2: The Proposed Solution

### The Integrated Workflow Vision

We propose an enhanced workflow that bridges cc-sdd specifications with Git Flow and automated code quality tools:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PROPOSED: Integrated SDD + Git Flow                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. /kiro-spec-create "feature-name"                                        │
│     ↓                                                                       │
│  2. /kiro-spec-design → Requirements.md, Design.md                          │
│     ↓                                                                       │
│  3. /kiro-spec-tasks → Tasks.md                                             │
│     ↓                                                                       │
│  4. CREATE FEATURE BRANCH (Automatic)                                       │
│     git checkout -b feature/feature-name                                    │
│     ↓                                                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  IMPLEMENTATION LOOP (Automated, With Quality Gates)                   │ │
│  │                                                                        │ │
│  │  For each Task N:                                                      │ │
│  │    ┌───────────────────────────────────────────────────────────────┐   │ │
│  │    │ a. Create task branch: task/feature-name-task-N               │   │ │
│  │    │    git worktree add ../task-N -b task/feature-name-N          │   │ │
│  │    └───────────────────────────────────────────────────────────────┘   │ │
│  │                          ↓                                             │ │
│  │    ┌───────────────────────────────────────────────────────────────┐   │ │
│  │    │ b. /kiro-task-impl N (Claude implements in isolated worktree) │   │ │
│  │    └───────────────────────────────────────────────────────────────┘   │ │
│  │                          ↓                                             │ │
│  │    ┌───────────────────────────────────────────────────────────────┐   │ │
│  │    │ c. CODE QUALITY GATE                                          │   │ │
│  │    │    • coderabbit review --prompt-only                          │   │ │
│  │    │    • sonarqube-mcp analyze                                    │   │ │
│  │    │    • semgrep scan                                             │   │ │
│  │    │    → Issues found? Claude fixes automatically                 │   │ │
│  │    │    → Loop until quality gate passes                           │   │ │
│  │    └───────────────────────────────────────────────────────────────┘   │ │
│  │                          ↓                                             │ │
│  │    ┌───────────────────────────────────────────────────────────────┐   │ │
│  │    │ d. Commit and Push                                            │   │ │
│  │    │    git commit -m "feat(task-N): implement <task summary>"     │   │ │
│  │    │    git push origin task/feature-name-N                        │   │ │
│  │    └───────────────────────────────────────────────────────────────┘   │ │
│  │                          ↓                                             │ │
│  │    ┌───────────────────────────────────────────────────────────────┐   │ │
│  │    │ e. Create Pull Request                                        │   │ │
│  │    │    gh pr create --base feature/feature-name                   │   │ │
│  │    │    → Triggers GitHub Actions: @claude reviews PR              │   │ │
│  │    │    → CodeRabbit automated review                              │   │ │
│  │    └───────────────────────────────────────────────────────────────┘   │ │
│  │                          ↓                                             │ │
│  │    ┌───────────────────────────────────────────────────────────────┐   │ │
│  │    │ f. Merge and Cleanup                                          │   │ │
│  │    │    gh pr merge --squash                                       │   │ │
│  │    │    git worktree remove ../task-N                              │   │ │
│  │    └───────────────────────────────────────────────────────────────┘   │ │
│  │                          ↓                                             │ │
│  │    Move to Task N+1                                                    │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│     ↓                                                                       │
│  5. All tasks complete → PR feature branch to main                          │
│     ↓                                                                       │
│  6. Final review, merge, deploy                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Components of the Solution

#### Component 1: Git Worktrees for Task Isolation

Claude Code's documentation explicitly recommends Git worktrees for parallel AI development. Each task gets its own isolated workspace:

```bash
# Create worktree for Task 1
git worktree add ../feature-auth-task-1 -b task/auth-task-1

# Navigate to worktree
cd ../feature-auth-task-1

# Run Claude Code in isolation
claude

# When done, clean up
git worktree remove ../feature-auth-task-1
```

**Benefits**:
- Complete file isolation between tasks
- Parallel implementation possible (multiple Claude instances)
- No context contamination
- Easy rollback (just delete worktree)

#### Component 2: CodeRabbit Integration for Quality Gates

CodeRabbit provides native Claude Code integration via CLI:

```bash
# Run code review before commit
coderabbit review --prompt-only

# Output goes directly to Claude for automatic fixes
# Claude reads issues, creates fix list, implements corrections
```

**The Review-Fix Loop**:
```
┌─────────────────────────────────────────────────────────────┐
│                   CodeRabbit + Claude Loop                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Claude implements task                                  │
│     ↓                                                       │
│  2. coderabbit review --prompt-only                         │
│     ↓                                                       │
│  3. Claude reads CodeRabbit output                          │
│     ↓                                                       │
│  4. Issues found?                                           │
│     ├── YES → Claude fixes issues → Go to step 2            │
│     └── NO  → Proceed to commit                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Component 3: Leveraging Existing `/kiro:steering-custom` for Design Rules

cc-sdd already provides a robust mechanism for defining design rules through the `/kiro:steering-custom` command. Rather than creating a new system, the integrated workflow should leverage this existing capability.

**How `/kiro:steering-custom` Works:**

```bash
# Run the command to create a custom steering document
/kiro:steering-custom

# Claude will guide you through:
# 1. Document type selection (API standards, testing, code style, etc.)
# 2. Inclusion mode (Always, Conditional, Manual)
# 3. File pattern matching (for Conditional mode)
# 4. Content generation
```

**Example: Creating Design Pattern Rules**

```bash
/kiro:steering-custom
# Select: Code Style
# Inclusion Mode: Conditional
# File Pattern: "**/*.ts"
# Content: Design patterns, anti-patterns, naming conventions
```

This creates `.kiro/steering/code-style.md`:

```markdown
---
inclusion: conditional
globs: ["**/*.ts"]

---

# TypeScript Code Style Standards

## Required Design Patterns

### Repository Pattern
All data access goes through repositories:
- `app/repositories/<Entity>Repository.ts`
- Never call database directly from services

### Service Layer Pattern
Business logic in services:
- Services are stateless
- Services call repositories
- Services handle business rules

## Forbidden Patterns

### No God Classes
- Maximum 300 lines per file
- Maximum 10 public methods per class

### No Deep Nesting
- Maximum 3 levels of indentation
- Use early returns

## Testing Requirements
- Unit tests for all public methods
- Minimum 80% code coverage
```

**Key Insight**: The steering documents are automatically loaded by Claude during `/kiro:spec-impl` based on file patterns. The missing piece is **automated enforcement**—connecting these rules to CodeRabbit/SonarQube to verify compliance before commit.

**Recommended Custom Steering Documents:**

| Document | Inclusion Mode | Pattern | Purpose |
|----------|---------------|---------|---------|
| `design-patterns.md` | Conditional | `"src/**/*.ts"` | Required/forbidden patterns |
| `api-standards.md` | Conditional | `"src/api/**/*"` | REST conventions, error handling |
| `testing.md` | Conditional | `"**/*.test.ts"` | Test organization, coverage rules |
| `security.md` | Always | - | Auth patterns, input validation |
| `database.md` | Conditional | `"**/repositories/**"` | Schema design, query patterns |

#### Component 4: GitHub Actions for PR Review

Claude Code provides official GitHub Actions for automated PR review:

```yaml
# .github/workflows/claude-review.yml
name: Claude Code PR Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          direct_prompt: |
            Review this PR for:
            1. Adherence to design patterns in .kiro/steering/Rules.md
            2. Code smells and anti-patterns
            3. Test coverage and quality
            4. Security vulnerabilities
            Provide specific, actionable feedback.
```

---

## Part 3: Implementation Guide

### Phase 1: Setting Up the Infrastructure

#### Step 1: Install Required Tools

```bash
# Install cc-sdd
npx cc-sdd@latest --claude

# Install CodeRabbit CLI
curl -fsSL https://cli.coderabbit.ai/install.sh | sh

# Install Claude Code GitHub Actions
claude /install-github-app

# Add SonarQube MCP
claude mcp add sonarqube --env SONARQUBE_TOKEN=<your-token>

# Add Semgrep MCP (optional, for security)
claude mcp add semgrep
```

#### Step 2: Create Custom Steering Documents (Using Existing cc-sdd Feature)

cc-sdd already provides `/kiro:steering-custom` for defining design rules. Use this existing feature:

```bash
# In Claude Code, run:
/kiro:steering-custom

# Follow the prompts to create:
# 1. design-patterns.md (Conditional: "src/**/*.ts")
# 2. testing.md (Conditional: "**/*.test.ts")
# 3. api-standards.md (Conditional: "src/api/**/*")
```

**Example session:**
```
> /kiro:steering-custom

Claude: What type of steering document would you like to create?
1. API Standards
2. Testing Approach
3. Code Style
4. Security Policies
5. Database Conventions
6. Custom...

> 3 (Code Style)

Claude: What inclusion mode?
1. Always - Universal standards for ALL code
2. Conditional - Triggered by file patterns
3. Manual - Referenced with @filename.md

> 2 (Conditional)

Claude: What file pattern should trigger this?

> "src/**/*.ts"

Claude: I'll create .kiro/steering/code-style.md with your design patterns...
```

This creates steering files that are **automatically loaded** during `/kiro:spec-impl` when Claude edits matching files.

#### Step 3: Create Custom Slash Commands

Add to `.claude/commands/`:

**implement-task-with-quality.md**:
```markdown
# Implement Task with Quality Gates

## Variables
TASK_NUMBER: $ARGUMENTS
FEATURE_NAME: (read from current spec context)

## Workflow

1. **Create Task Branch**
    ```bash
    git worktree add ../task-$TASK_NUMBER -b task/$FEATURE_NAME-$TASK_NUMBER
    cd ../task-$TASK_NUMBER
    ```

2. **Read Context**
   - Read .kiro/specs/$FEATURE_NAME/Tasks.md
   - Read .kiro/specs/$FEATURE_NAME/Design.md
   - Read .kiro/steering/Rules.md
   - Understand Task $TASK_NUMBER requirements

3. **Implement Task**
   - Follow design patterns in Rules.md
   - Write tests alongside implementation
   - Use conventional commits

4. **Quality Gate Loop**
    ```bash
    # Run CodeRabbit review
    coderabbit review --prompt-only > /tmp/review.md
    ```
   - If issues found: Fix them and re-run
   - Continue until clean review

5. **Commit and Push**
    ```bash
    git add .
    git commit -m "feat($FEATURE_NAME): implement task $TASK_NUMBER - <summary>"
    git push origin task/$FEATURE_NAME-$TASK_NUMBER
    ```

6. **Create Pull Request**
    ```bash
    gh pr create \
      --base feature/$FEATURE_NAME \
      --title "Task $TASK_NUMBER: <summary>" \
      --body "Implements task $TASK_NUMBER from $FEATURE_NAME specification"
    ```

7. **Report Completion**
   - Update Tasks.md with status
   - Return to main worktree
   - Report PR URL to user
```

**complete-task-cycle.md**:
```markdown
# Complete Task Implementation Cycle

Implements a single task with full Git Flow and quality gates.

## Arguments
$ARGUMENTS = task number

## Instructions

1. Parse task number from arguments
2. Determine current feature from .kiro/specs/ context
3. Execute the following sequence:

### Branch Creation
- Create worktree: `git worktree add ../task-impl -b task/<feature>-<task-num>`
- Change to worktree directory

### Implementation
- Implement the task according to Tasks.md
- Follow Rules.md design patterns
- Write accompanying tests

### Quality Validation
Run quality checks in a loop:
  while quality_issues_exist:
      run: coderabbit review --plain
      parse issues
      fix each issue
      re-run checks

### Git Operations
- Stage all changes: `git add .`
- Commit with conventional message
- Push to remote
- Create PR via `gh pr create`

### Cleanup
- Return to main worktree
- Report PR URL and status

## Success Criteria
- PR created and pushed
- All quality checks pass
- Tests written and passing
```

### Phase 2: The Enhanced Workflow in Action

Here's how the integrated workflow looks in practice:

```bash
# 1. Start with cc-sdd specification (unchanged - works great!)
> /kiro-spec-create user-authentication
> /kiro-spec-design
> /kiro-spec-tasks

# 2. Create feature branch
> git checkout -b feature/user-authentication

# 3. Implement tasks with new integrated command
> /implement-task-with-quality 1

# Claude will:
# - Create worktree: ../task-1
# - Implement task 1
# - Run CodeRabbit review
# - Fix any issues
# - Commit, push, create PR
# - Return to main workspace

# 4. Review PR (GitHub Actions runs @claude review)
# 5. Merge PR

# 6. Repeat for remaining tasks
> /implement-task-with-quality 2
> /implement-task-with-quality 3
# ... etc

# 7. Merge feature branch to main
> gh pr create --base main --title "feat: user authentication"
```

### Phase 3: Parallel Implementation (Advanced)

For larger features, implement multiple tasks in parallel using multiple worktrees:

```bash
# Terminal 1
cd ../task-1-worktree
claude
> /kiro-task-impl 1

# Terminal 2
cd ../task-2-worktree
claude
> /kiro-task-impl 2

# Terminal 3
cd ../task-3-worktree
claude
> /kiro-task-impl 3

# Each instance is isolated, no conflicts
# Each creates its own PR
# Merge PRs sequentially to feature branch
```

---

## Part 4: Quality Tool Integration Details

### CodeRabbit CLI Integration

```bash
# Authentication (one-time)
coderabbit auth login

# Review modes
coderabbit review                    # Interactive review
coderabbit review --plain            # Plain text output
coderabbit review --prompt-only      # Optimized for AI agents
coderabbit review --type uncommitted # Review uncommitted changes only

# Integration with Claude Code
# In your CLAUDE.md:
# "After implementing code, always run: coderabbit review --prompt-only"
# "Parse the output and fix all issues before committing"
```

### SonarQube MCP Integration

```bash
# Add MCP server
claude mcp add sonarqube --env SONARQUBE_TOKEN=<token>

# Available tools in Claude Code:
# - analyze_code_snippet: Analyze specific code
# - analyze_file_list: Analyze multiple files
# - toggle_automatic_analysis: Enable/disable auto-analysis

# In Claude Code session:
> Use SonarQube to analyze the implementation
> Fix all bugs and code smells identified
```

### Semgrep MCP for Security

```bash
# Add MCP server
claude mcp add semgrep

# Custom rules for project patterns
# .semgrep/rules/custom.yaml
rules:
  - id: no-raw-sql
    pattern: $DB.query($SQL)
    message: "Use parameterized queries instead of raw SQL"
    severity: ERROR
    languages: [javascript, typescript]
    
  - id: require-auth-middleware
    pattern-either:
      - pattern: app.get($PATH, $HANDLER)
      - pattern: app.post($PATH, $HANDLER)
    pattern-not: app.$METHOD($PATH, authMiddleware, $HANDLER)
    message: "All routes must use auth middleware"
    severity: WARNING
    languages: [javascript, typescript]
```

---

## Part 5: Comparison: Before vs After

### Before: Current cc-sdd Workflow

| Aspect | Status | Issues |
|--------|--------|--------|
| Specification | ★★★★★ | Excellent |
| Branch Strategy | ★☆☆☆☆ | None - all on main |
| Code Review | ★★☆☆☆ | Manual only |
| Quality Gates | ★☆☆☆☆ | None automated |
| CI/CD Integration | ★★☆☆☆ | Manual triggers |
| Parallel Work | ★☆☆☆☆ | Not supported |
| Feedback Loop | ★☆☆☆☆ | None |

### After: Integrated Workflow

| Aspect | Status | Improvements |
|--------|--------|--------------|
| Specification | ★★★★★ | Unchanged - excellent |
| Branch Strategy | ★★★★★ | Feature/task branches |
| Code Review | ★★★★★ | Automated + human |
| Quality Gates | ★★★★★ | CodeRabbit, SonarQube, Semgrep |
| CI/CD Integration | ★★★★★ | GitHub Actions, auto-PR |
| Parallel Work | ★★★★☆ | Git worktrees |
| Feedback Loop | ★★★★★ | AI reads and fixes issues |

### Metrics Impact (Estimated)

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Time per task | 30-60 min | 15-25 min | 50-60% faster |
| Code review cycles | 2-3 | 1-2 | 50% fewer iterations |
| Bugs reaching main | 15-20% | 3-5% | 75% reduction |
| Code smell density | High | Low | 80% reduction |
| Developer context switches | Many | Few | 70% reduction |

---

## Part 5.5: Framework Comparison — cc-sdd, Agent OS, and Red64 Plugins

The spec-driven development landscape for AI coding agents is rapidly evolving. Three frameworks deserve comparison: cc-sdd (the subject of this article), Agent OS, and Red64 Plugins. Each takes a different architectural approach to solving similar problems.

### Framework Overview

| Framework | Creator | Architecture | Status | License |
|-----------|---------|--------------|--------|---------|
| **cc-sdd** | gotalab | Slash commands + Steering files | Production | MIT |
| **Agent OS** | Builder Methods | Instructions + Subagents | Production | MIT |
| **Red64 Plugins** | Me (alpha) | Plugin-first + Hooks | Alpha | MIT |

### Architectural Comparison

#### cc-sdd: Kiro-Style Commands

cc-sdd implements a **Kiro-compatible workflow** through slash commands:

```
.kiro/
├── settings/        # Templates, configuration
├── specs/           # Feature specifications
│   └── <feature>/
│       ├── Requirements.md
│       ├── Design.md
│       └── Tasks.md
└── steering/        # Project context
    ├── product.md   # Always included
    ├── tech.md      # Always included
    ├── structure.md # Always included
    └── *.md         # Conditional/manual
```

**Strengths**: Kiro compatibility, structured 3-phase workflow, conditional context loading.
**Gap**: No Git Flow integration, no automated quality enforcement.

#### Agent OS: Instruction-Driven Subagents

Agent OS uses a **subagent architecture** with detailed instruction files:

```
.agent-os/
├── instructions/
│   ├── core/          # Main workflows
│   │   ├── create-spec.md
│   │   ├── execute-tasks.md
│   │   └── plan-product.md
│   └── meta/          # Support instructions
│       └── pre-flight.md
├── product/           # Product context
│   ├── mission.md
│   ├── roadmap.md
│   └── tech-stack.md
├── specs/             # Feature specs
└── standards/         # Coding standards
```

**Key Innovation**: Subagent delegation for specialized tasks (date-checker, file-creator, context-fetcher, project-manager).

**Strengths**: Sophisticated multi-agent orchestration, recaps for project history.
**Gap**: Complex setup, heavy instruction files, not plugin-based.

#### Red64 Plugins: Plugin-First Architecture

*Disclosure: This is my project, currently in alpha.*

Red64 reimagines spec-driven development as a **modular plugin ecosystem** native to Claude Code:

```
.red64/
├── config.yaml          # Project configuration
├── product/             # Product context
│   ├── mission.md
│   ├── roadmap.md
│   └── tech-stack.md
├── scripts/             # Hook scripts (auto-downloaded)
├── specs/               # Feature specifications
└── metrics/             # Usage and quality metrics

# Plugins installed via:
/plugin install core@red64-plugins
/plugin install red64-standards-typescript@red64-plugins
```

**The Context Window Problem**

Here's a dirty secret about spec-driven development: **context management is hard, and most naive approaches fail at scale**.

A typical SDD project (measured from our production codebase with 15 features) includes:
- Steering files: product.md, tech.md, structure.md (~11k tokens)
- Settings/templates (~17k tokens)
- **Specs for 15 features (~236k tokens)**
- Total: **265k tokens** — exceeds Claude's 200k context limit!

**The good news**: cc-sdd is smart about this. It uses a two-tier loading strategy:

| Directory | Loading Strategy | When Loaded |
|-----------|------------------|-------------|
| `.kiro/steering/` | **Always** (bulk injection) | Every session start |
| `.kiro/specs/` | **On-demand** (lazy loading) | Only when you run `/kiro:spec-implement feature-name` |
| `.kiro/settings/` | **Never** (internal use only) | Not sent to LLM context |

So when you run `/kiro:spec-implement user-login`, cc-sdd loads:
- Steering (~11k) + one spec folder (~16k) = **~27k tokens**

It does **not** load all 15 specs (236k). This is good design.

**So what's the problem?**

cc-sdd solves spec loading well. But the gap is in **coding standards, MCP tools, and cross-cutting concerns**:

1. **Coding standards** (TypeScript conventions, API patterns, testing rules) — cc-sdd's steering handles this, but you load ALL steering files regardless of whether you're editing TypeScript or Python
2. **MCP tool definitions** — loaded entirely upfront (see next section)
3. **No task-level intelligence** — cc-sdd knows which *spec* you're working on, but not which *files* within that spec

**Red64's Addition: File-Pattern-Based Injection**

Red64 builds on cc-sdd's smart spec loading by adding another layer of intelligence:

```python
# cc-sdd loads: steering (always) + current spec (on-demand)
# Red64 adds: file-pattern-based standards injection

def pre_task_hook(task_context):
    relevant_standards = []
    
    # Analyze files being touched within the current spec
    for file in task_context.files:
        if file.endswith('.ts') or file.endswith('.tsx'):
            relevant_standards.append('typescript-standards')
        if 'api/' in file or 'routes/' in file:
            relevant_standards.append('api-conventions')
        if '.test.' in file or '.spec.' in file:
            relevant_standards.append('testing-patterns')
    
    # Only inject standards relevant to THIS task's files
    return dedupe(relevant_standards)
```

**Real-world impact (actual production data):**

Here's what we measured in a real project with 15 feature specs:

| .kiro/ Folder | Size | Est. Tokens | % of Total |
|---------------|------|-------------|------------|
| `steering/` | 45 KB | ~11k | 4% |
| `settings/` | 69 KB | ~17k | 6% |
| `specs/` (15 features) | 945 KB | ~236k | **89%** |
| **TOTAL** | 1.06 MB | **~265k** | 100% |

**What actually gets loaded** (from `/context` command with full MCP setup):

| Component | Tokens | % of Context |
|-----------|--------|--------------|
| System prompt | 3.3k | 1.7% |
| System tools | 16.1k | 8.1% |
| **MCP tools** | **48.2k** | **24.1%** ⚠️ |
| Custom agents | 212 | 0.1% |
| Memory/CLAUDE.md | 600 | 0.3% |
| Messages | 1.6k | 0.8% |
| **Used** | **115k** | 57% of 200k limit |
| **Free** | **85k** | Room for actual work |

Notice the imbalance: MCP tool definitions (48.2k) consume **80x more tokens** than all 9 custom agents combined (212 tokens). Tool schemas are dominating context that should be used for actual work.

**The insight**: cc-sdd already handles spec loading intelligently. Red64's contribution is adding file-pattern awareness for coding standards and MCP tools.

**Contrast: Well-designed agents are lightweight.** Notice that 9 custom agents (spec-tasks-agent, validate-design-agent, steering-agent, etc.) consume only 212 tokens total—about 23 tokens each. That's the goal: minimal overhead, maximum utility.

| Scenario | What cc-sdd Loads | What Red64 Adds | Total |
|----------|-------------------|-----------------|-------|
| Work on TypeScript API task | 11k (steering) + 16k (spec) | +2k (TS + API standards) | ~29k |
| Work on Python data task | 11k (steering) + 16k (spec) | +1.5k (Python standards) | ~28.5k |
| Fix typo in README | 11k (steering) | Nothing extra | ~11k |

The savings aren't as dramatic as "265k → 11k" (because cc-sdd already prevents that), but the precision matters for output quality. Loading TypeScript standards when editing TypeScript means better code generation.

**Three-Tier Context Hierarchy**

Red64 organizes context into three tiers with different loading strategies:

| Tier | Content | Loading Strategy | Real Example | Tokens |
|------|---------|------------------|--------------|--------|
| **Always** | Core project identity | Every request | `steering/` (product.md, tech.md, structure.md) | ~11k |
| **Conditional** | Domain-specific standards | Pattern-matched | `specs/feature-x/` when working on feature X | ~16k per spec |
| **Manual** | Reference documentation | Explicit @mention | `settings/` templates, full spec history | ~17k |

This mirrors how human developers think: you don't mentally load your company's entire coding handbook when fixing a CSS bug—you load the relevant CSS conventions.

```
# Red64 intelligent context injection flow:
User Prompt → Analyze Task → Detect File Types → Load Relevant Standards → Inject Context
                                    ↓
                            Only what's needed,
                            within token budget
```

**Why This Matters Beyond Cost**

Token savings are nice, but the real benefit is **better output quality**. LLMs perform better with focused, relevant context than with a kitchen-sink dump of everything. By loading only TypeScript standards when working on TypeScript, the model isn't distracted by Python conventions it doesn't need.

This is also future-proofing: as we add more standards plugins (React, Next.js, database patterns, etc.), the naive "load everything" approach becomes untenable. Intelligent injection scales.

**The MCP Context Catastrophe**

The context overload problem gets *much worse* when you add MCP servers to the mix.

[Anthropic recently published a revealing article](https://www.anthropic.com/engineering/code-execution-with-mcp) acknowledging what many of us have experienced: **MCP doesn't scale**. As one developer [put it bluntly](https://medium.com/@cdcore/mcp-is-broken-and-anthropic-just-admitted-it-7eeb8ee41933): "MCP works beautifully in demos and breaks the moment you try to scale it."

The problem is architectural. Most MCP clients load **all tool definitions upfront** into the context window.

Here's actual data from a real programming setup (from `/context` command):

```
# MCP tools consuming 48.2k tokens (24.1% of context!) before any work begins

# GitHub MCP (32 tools) - ~24k tokens
├─ create_branch, create_pull_request, merge_pull_request...
├─ list_commits, get_commit, push_files...
├─ issue_read, issue_write, list_issues, search_issues...
├─ pull_request_read, pull_request_review_write...
└─ search_code, search_repositories, search_users...

# Terraform Registry MCP (12 tools) - ~8k tokens
├─ get_module_details, get_latest_module_version...
├─ get_provider_details, get_provider_capabilities...
├─ search_modules, search_providers, search_policies...
└─ get_policy_details...

# Apify MCP (6 tools) - ~6k tokens
├─ call-actor, get-actor-output, fetch-actor-details...
├─ search-actors, search-apify-docs, fetch-apify-docs...

# Context7 Library Docs MCP (2 tools) - ~1.7k tokens
├─ resolve-library-id, get-library-docs...

# MCP Docker Management (7 tools) - ~5k tokens
├─ mcp-add, mcp-remove, mcp-find, mcp-exec...
├─ mcp-config-set, code-mode...
└─ (Useful: dynamically add/remove MCP servers mid-session)

────────────────────────────────────────────────────────
TOTAL: 64 tools → 48,200 tokens (24% of 200k context)
```

**This is a modest setup** — just GitHub, Terraform, Apify, and docs. A full enterprise environment might add:
- Slack MCP (notifications, channel search)
- Linear/Jira MCP (issue tracking)
- Database MCP (Postgres, MySQL introspection)
- Cloud provider MCPs (AWS, GCP, Azure)

Each additional server adds 5-15k tokens. At 100+ tools, you've consumed half your context before asking a question.

**The real cost**: In this setup, MCP tool definitions (48.2k) consume **more tokens than the entire steering folder** (11k) and **more than all custom agents combined** (212 tokens). This is backwards — tool schemas shouldn't dominate your context.

Then there's the **intermediate results problem**. When tools return data, it flows through the context window:

```
# Example: "Download transcript from Drive, attach to Salesforce lead"

TOOL CALL: gdrive.getDocument("abc123")
        → Returns 50,000 tokens of meeting transcript
        → Loaded into context

TOOL CALL: salesforce.updateRecord(data: [entire transcript again])
        → Model must write the entire transcript again
        → Another 50,000 tokens
        
# Total: 100,000+ tokens for a simple copy operation
```

This is why Anthropic introduced Skills and "Code Mode" — the model writes code to call tools instead of calling them directly, keeping intermediate results in the execution environment rather than flowing through context.

**Red64's Approach: Smart MCP Loading**

Red64 applies the same hook-based philosophy to MCP servers:

```python
# Instead of loading all 64 tools (48K tokens) always:
def get_relevant_mcp_servers(task_context):
    servers = []
    
    # Only load what the task needs
    if task_context.mentions('PR') or task_context.involves_code_review:
        servers.append('github-mcp')  # 32 tools, ~24k tokens
    if task_context.mentions('terraform') or task_context.involves_infrastructure:
        servers.append('terraform-registry-mcp')  # 12 tools, ~8k tokens
    if task_context.mentions('scraping') or task_context.involves_data_collection:
        servers.append('apify-mcp')  # 6 tools, ~6k tokens
    if task_context.needs_library_docs:
        servers.append('context7-mcp')  # 2 tools, ~1.7k tokens
    
    # Progressive disclosure: load server, then specific tools
    return servers  # Typical task: 1-2 servers instead of all 4
```

Combined with a **progressive disclosure pattern** (load server → search for relevant tools → load only those tool definitions), this reduces MCP overhead by 50-90% for typical tasks. A code review task loads only GitHub MCP (~24k) instead of all servers (48k). A simple coding task with no external integrations loads nothing.

The insight from Anthropic's article is correct: **code execution is the solution**. But it's not enough on its own. You also need intelligent orchestration that decides *which* servers and tools to even consider. Red64's hook system provides that orchestration layer.

| Problem | Naive MCP | Red64 Approach |
|---------|-----------|----------------|
| Tool definitions | Load all upfront (~48K tokens) | Load relevant servers on-demand (~5K tokens) |
| Intermediate results | Flow through context | Stay in execution environment |
| Tool discovery | Model searches 64+ tools | Hook pre-filters to ~10 relevant tools |
| Scaling | Breaks at 100+ tools | Handles 1000+ tools efficiently |

This isn't just optimization — it's necessary for production use. Without intelligent MCP management, you can't build agents that connect to real enterprise systems with dozens of integrations.

**Strengths**: Native plugin architecture, intelligent context management, composable standards, metrics-ready.
**Status**: Alpha—APIs may change, not yet production-ready.

### Feature Matrix

| Feature | cc-sdd | Agent OS | Red64 Plugins |
|---------|--------|----------|---------------|
| **Spec-Driven Workflow** | ✅ Kiro-style | ✅ Custom | ✅ Planned |
| **Requirements → Design → Tasks** | ✅ Full | ✅ Full | ✅ Planned |
| **Conditional Context Loading** | ✅ Steering globs | ⚠️ Manual | ✅ Hooks |
| **Composable Standards** | ⚠️ Manual files | ⚠️ Manual files | ✅ Plugins |
| **MCP Context Management** | ❌ | ❌ | ✅ Smart loading |
| **Plugin Architecture** | ❌ | ❌ | ✅ Native |
| **Multi-Agent Orchestration** | ❌ | ✅ Subagents | ⚠️ Planned |
| **Git Flow Integration** | ❌ | ❌ | ⚠️ Planned |
| **Quality Gate Automation** | ❌ | ❌ | ⚠️ Planned |
| **Metrics Collection** | ❌ | ❌ | ✅ Built-in |
| **Tool Integrations** | ❌ | ⚠️ Limited | ✅ Extension system |
| **Production Ready** | ✅ | ✅ | ❌ Alpha |
| **Multi-Agent Support** | ✅ 7 agents | ✅ Multiple | ⚠️ Claude Code only |

### Philosophy Comparison

| Aspect | cc-sdd | Agent OS | Red64 Plugins |
|--------|--------|----------|---------------|
| **Primary Goal** | Kiro-compatible SDD | Better AI agent planning | Enterprise determinism |
| **Context Strategy** | Steering files | Instruction files | Hook-based injection |
| **Standards Approach** | Manual steering | Manual standards | Plugin marketplace |
| **Token Management** | Conditional globs | spec-lite.md | Intelligent hooks |
| **Extensibility** | Templates | Subagents | Plugin system |
| **Target User** | Any AI agent user | Any AI agent user | Enterprise teams |

### Why Red64 Plugins Matters (Even in Alpha)

While Red64 Plugins is not production-ready, its architectural ideas address several gaps:

**1. Plugin Marketplace Model**
```bash
/plugin marketplace add https://github.com/Red64llc/red64-plugins
/plugin install core@red64-plugins
/plugin install red64-standards-typescript@red64-plugins
```

This enables:
- Shareable, versioned standards across teams
- Community-contributed plugins
- Easy updates without manual file management

**2. Intelligent Hook System**

Instead of dumping all context into every conversation (wasting tokens), Red64's hooks analyze the task and inject only relevant standards:

```python
# Simplified hook concept
def analyze_task(prompt, files_in_context):
    if any(f.endswith('.ts') for f in files_in_context):
        inject('red64-standards-typescript')
    if any('api' in f for f in files_in_context):
        inject('red64-standards-api')
```

This is similar to cc-sdd's conditional steering, but automated via hooks rather than manual glob patterns.

**3. Built-in Metrics**

Red64 includes metrics collection from day one:
```
.red64/metrics/
├── task-completion.json
├── quality-scores.json
└── time-tracking.json
```

This enables ROI measurement—critical for enterprise adoption.

**4. Extension System for Integrations**

```
red64-extensions/
├── metrics/     # Quality and productivity metrics
├── github/      # GitHub integration
└── jira/        # Jira integration
```

### Recommendation: Combine the Best Ideas

For production use today, **cc-sdd** remains the most mature and feature-complete option. However, the architectural innovations from Agent OS and Red64 Plugins suggest future directions:

| From cc-sdd | From Agent OS | From Red64 |
|-------------|---------------|------------|
| ✅ Use today | ✅ Learn subagent patterns | ⏳ Watch for maturity |
| Kiro compatibility | Instruction delegation | Plugin architecture |
| Steering system | Project manager agent | Intelligent hooks |
| Multi-agent support | Recap system | Metrics collection |

**Proposed Hybrid Approach**:

1. **Use cc-sdd for spec workflow** (Requirements → Design → Tasks)
2. **Use `/kiro:steering-custom`** for design rules (already exists)
3. **Add custom slash commands** for Git Flow integration (this article)
4. **Integrate CodeRabbit CLI** for automated quality gates (this article)
5. **Watch Red64 Plugins** for plugin marketplace and metrics when it matures

### References

- **cc-sdd**: [github.com/gotalab/cc-sdd](https://github.com/gotalab/cc-sdd)
- **Agent OS**: [github.com/buildermethods/agent-os](https://github.com/buildermethods/agent-os)
- **Red64 Plugins**: [github.com/Red64llc/red64-plugins](https://github.com/Red64llc/red64-plugins)
- **GitHub Spec Kit**: [github.blog/spec-driven-development](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)

---

## Part 6: Recommendations for cc-sdd Enhancement

Based on this analysis, we recommend the following enhancements to the cc-sdd framework:

### What cc-sdd Already Does Well

✅ **Steering System** - `/kiro:steering` and `/kiro:steering-custom` already provide excellent mechanisms for:
- Project memory (product.md, tech.md, structure.md)
- Custom design rules with conditional loading
- File pattern-based context injection
- Three inclusion modes (Always, Conditional, Manual)

### Short-Term (v1.x Updates)

1. **Add `/kiro:task-impl-pr` command** that wraps implementation with Git operations:
   - Create task branch automatically
   - Run implementation
   - Commit with conventional message
   - Create PR to feature branch

2. **Document CodeRabbit CLI integration** in official docs:
   - Add `coderabbit review --prompt-only` to implementation workflow
   - Show how to create review-fix loops

3. **Add worktree setup guidance** to initialization:
   - Explain parallel task execution pattern
   - Provide directory structure recommendations

### Medium-Term (v2.0 Features)

1. **Built-in Git Flow support** with configurable branching strategy:
   - Auto-detect feature name from spec context
   - Branch naming conventions
   - Worktree management helpers

2. **Quality gate hooks** that integrate with steering:
   - Pre-commit validation against steering rules
   - CodeRabbit/SonarQube MCP integration
   - Automated fix loops

3. **Steering → Quality Tool mapping**:
   - Translate steering rules into CodeRabbit configurations
   - Generate .coderabbit.yml from steering documents

### Long-Term (Vision)

1. **Full CI/CD integration** with GitHub Actions templates
2. **Quality dashboard** showing spec adherence + steering compliance
3. **Learning system** that updates steering based on CodeRabbit feedback
4. **Team collaboration features** with role-based approvals

### What I'm Building: A Refactored Approach

Full disclosure: I'm working on a refactoring of cc-sdd that addresses these gaps. It's called [Red64 Plugins](https://github.com/Red64llc/red64-plugins) and it's currently alpha-quality (don't use it in production yet). The goals:

- **Native Git Flow integration** with automatic branch creation, worktrees, and PR automation
- **Quality gate automation** via CodeRabbit and SonarQube integration (with pluggable open source alternatives)
- **Claude Code SDK integration** for more deterministic AI behavior
- **Intelligent context injection** — this builds on cc-sdd's smart spec loading by adding file-pattern awareness. cc-sdd already loads specs on-demand (not all 265k at once). Red64 adds another layer: analyzing which *files* you're touching to inject only relevant coding standards. Working on TypeScript? Load TypeScript conventions. Editing an API route? Add API patterns. This precision improves output quality.
- **Smart MCP management** — the same hook system applies to MCP servers. Instead of loading all tool definitions upfront (which [Anthropic admits doesn't scale](https://www.anthropic.com/engineering/code-execution-with-mcp)), Red64 loads only relevant servers and uses progressive disclosure to minimize context bloat. This is essential for enterprise agents with dozens of integrations.
- **Built-in metrics** for measuring what actually works

The refactored framework maintains Kiro compatibility while adding the missing pieces. It's open source and I'd welcome feedback on the approach.

I'm not claiming this solves everything—the space is moving fast and there are other good approaches (Agent OS, GitHub Spec Kit). But the gap is real, and someone needs to close it.

---

## Limitations and Open Questions

To be intellectually honest, here's what I'm uncertain about:

**1. Is this over-engineering for small projects?**

For quick prototypes or solo projects, the overhead of Git worktrees + automated quality gates might not be worth it. The sweet spot seems to be teams of 2-5 working on production code.

**2. Token costs still matter**

cc-sdd already handles spec loading intelligently (~27k for steering + one spec instead of 265k for everything). Red64's additional file-pattern analysis adds precision rather than dramatic savings. The real token wins come from MCP management (see below). But running CodeRabbit analysis and feeding results back still uses significant tokens.

**3. The tooling is fragile**

CodeRabbit CLI is still evolving. SonarQube MCP has limitations. Claude Code's plugin system is underdocumented. A lot can break when any of these change.

**4. Is spec-driven development the right abstraction?**

Some argue that AI coding agents should be more autonomous, not more constrained. Maybe the solution isn't better specs but better models. I'm betting on specs + constraints, but I could be wrong.

**5. Local vs. CI integration**

The proposed workflow focuses on local development. How this integrates with CI/CD pipelines in larger teams needs more thought.

**6. Vendor lock-in is a real problem**

This brings me to something that's been bothering me about my own proposal.

---

## The Vendor Lock-in Problem

Let's be honest: the workflow I've proposed has uncomfortable dependencies on closed-source, proprietary tools:

| Tool | Owner | Open Source? | Lock-in Risk |
|------|-------|--------------|--------------|
| **CodeRabbit** | CodeRabbit Inc. | ❌ Proprietary | High — pricing can change, API can break |
| **GitHub Actions** | Microsoft | ❌ Proprietary | Medium — GitLab CI, Forgejo exist |
| **Claude Code** | Anthropic | ❌ Proprietary | High — the whole workflow depends on it |
| **SonarQube** | SonarSource | ⚠️ Open core | Medium — community edition is limited |

For a framework that's supposed to bring *predictability* to AI development, building on closed foundations feels hypocritical. What happens when CodeRabbit raises prices? When GitHub Actions changes their free tier? When Anthropic deprecates Claude Code?

### Open Source Alternatives Worth Exploring

I'd like to open this discussion to the community. Here's what I've found so far:

**Code Quality / Static Analysis (replacing CodeRabbit):**
- **Semgrep** — Fully open source, excellent rule ecosystem, has MCP server
- **ESLint/Biome** — For JS/TS projects, mature and battle-tested
- **Rubocop/Ruff** — Language-specific linters with auto-fix
- **MegaLinter** — Meta-linter that aggregates 50+ linters, fully open source
- **Qodana** (JetBrains) — Open core, but Community edition is capable

**CI/CD (replacing GitHub Actions):**
- **Forgejo Actions** — GitHub Actions-compatible, fully open source
- **GitLab CI** — Open core, self-hostable
- **Woodpecker CI** — Lightweight, open source, Drone fork
- **Dagger** — Container-native CI, open source

**AI Coding Agents (reducing Claude Code dependency):**
- **Aider** — Open source, works with any LLM (local or API)
- **Continue** — Open source IDE extension, model-agnostic  
- **OpenHands** (formerly OpenDevin) — Open source autonomous agent
- **Local models via Ollama** — Qwen2.5-Coder, DeepSeek-Coder, CodeLlama

### A Possible Fully Open Stack

```
Spec-Driven Workflow (open source)
├── Aider or Continue (AI coding)
├── Local LLM via Ollama (DeepSeek-Coder, Qwen2.5-Coder)
├── Semgrep + MegaLinter (code quality)
├── Forgejo + Woodpecker CI (Git + CI/CD)
└── Self-hosted on $20/mo Hetzner box
```

This eliminates all proprietary dependencies. The tradeoff: Claude/GPT-4 quality is still ahead of local models for complex reasoning. But the gap is closing fast.

### What I'd Like Help With

I'm genuinely uncertain how to balance pragmatism vs. principles here:

1. **Should Red64 Plugins prioritize open source alternatives from day one?** Even if they're less polished?

2. **Is a "pluggable backend" approach feasible?** Where you can swap CodeRabbit for Semgrep, GitHub for Forgejo, Claude for Aider?

3. **What's the minimum viable open source stack** that actually works for production spec-driven development today?

If you've built something similar with fully open tools, I'd love to hear about it in the comments.

---

## Conclusion

cc-sdd has revolutionized the specification phase of AI-assisted development, delivering professional-grade requirements, designs, and task breakdowns. The framework also provides excellent **design rule definition** through `/kiro:steering-custom` with conditional loading based on file patterns.

However, the implementation phase remains disconnected from modern development practices. The gaps are not in *defining* rules, but in *enforcing* them:

| What cc-sdd Has | What's Missing |
|-----------------|----------------|
| ✅ Spec-driven workflow | ❌ Git Flow integration |
| ✅ Design rules via steering | ❌ Automated enforcement |
| ✅ Quality gate commands (validate-*) | ❌ External tool integration |
| ✅ Task decomposition | ❌ Branch-per-task automation |
| ✅ Project memory | ❌ PR workflow automation |

By integrating Git Flow, automated code quality tools, and feedback loops, we can close this gap and achieve true end-to-end AI-assisted development. The proposed workflow:

1. **Leverages existing `/kiro:steering-custom`** for design rules
2. **Adds Git worktree automation** for task isolation
3. **Integrates CodeRabbit CLI** for quality enforcement
4. **Creates PR workflows** with GitHub Actions

The technology exists today—Git worktrees, CodeRabbit CLI, SonarQube MCP, Claude Code GitHub Actions—we just need to connect the pieces. This integration transforms AI-assisted development from "AI generates, human reviews manually" to "AI generates → automated quality validation → AI fixes → human approves."

---

## References

### SDD Frameworks
- [cc-sdd GitHub Repository](https://github.com/gotalab/cc-sdd)
- [Spec-Driven Development Guide (cc-sdd)](https://github.com/gotalab/cc-sdd/blob/main/docs/guides/ja/spec-driven.md)
- [Agent OS](https://github.com/buildermethods/agent-os)
- [Red64 Plugins](https://github.com/Red64llc/red64-plugins)
- [GitHub Spec Kit](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)

### Claude Code Documentation
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions)
- [Common Workflows](https://code.claude.com/docs/en/common-workflows)

### Git Worktrees
- [Official Git Worktree Documentation](https://git-scm.com/docs/git-worktree)
- [Mastering Git Worktrees with Claude Code](https://medium.com/@dtunai/mastering-git-worktrees-with-claude-code-for-parallel-development-workflow-41dc91e645fe)
- [How incident.io Ships Faster with Git Worktrees](https://incident.io/blog/shipping-faster-with-claude-code-and-git-worktrees)

### Code Quality Tools
- [CodeRabbit CLI Documentation](https://docs.coderabbit.ai/cli/claude-code-integration)
- [SonarQube MCP Server](https://github.com/SonarSource/sonarqube-mcp-server)
- [Semgrep MCP Server](https://github.com/semgrep/mcp)

### MCP Context Management
- [Code Execution with MCP: Building More Efficient Agents](https://www.anthropic.com/engineering/code-execution-with-mcp) — Anthropic's acknowledgment of MCP scaling issues
- [MCP Is Broken and Anthropic Just Admitted It](https://medium.com/@cdcore/mcp-is-broken-and-anthropic-just-admitted-it-7eeb8ee41933) — Community analysis of the problem
- [Cloudflare Code Mode](https://blog.cloudflare.com/code-mode/) — Cloudflare's similar findings on MCP efficiency

---

*This is based on several months of production use. The proposed workflow works for my use cases but YMMV. Happy to discuss approaches in the comments.*

*Some of the code for the proposed slash commands and GitHub Actions is available at [github.com/Red64llc/red64-plugins](https://github.com/Red64llc/red64-plugins) but this is still in early stages and active development is ongoing. Do not expect it to work out of the box.*
