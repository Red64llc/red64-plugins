# Red64: Agent OS Reimagined
## A Modular Plugin Architecture with Code Mode for Claude Code

---

## Executive Summary

This document outlines a complete redesign strategy for Agent OS, reimagined as **Red64** — a modular plugin-based framework built natively on Claude Code's plugin system. The redesign addresses the key shortcomings of the current Agent OS while preserving its proven spec-driven development workflow.

**New in v2:** Integration of Anthropic's **Code Mode** pattern for MCP interactions, enabling 98%+ token savings on tool operations and context-efficient data handling.

### Key Design Principles

1. **Plugin-First Architecture** — Every component is a discrete, installable plugin
2. **Code Mode by Default** — MCP tools exposed as code APIs, not direct tool calls
3. **Filesystem-Based Discovery** — Standards and tools loaded on-demand via filesystem exploration
4. **Standards ≠ Skills** — Clear separation between coding guidelines and executable capabilities
5. **Composable Tech Stacks** — Stack-specific standards as independent, combinable plugins
6. **Context-Efficient Operations** — Filter and transform data in execution environment, not context
7. **Privacy-Preserving Workflows** — Sensitive data flows through execution, not the model
8. **Extension-Ready** — Clean interfaces for metrics, SDLC tools, and custom integrations

---

## Part 1: Analysis of Current Agent OS Shortcomings

### 1.1 Cumbersome Installation

**Current Problem:**
- Two-step installation (base to `~/agent-os`, compile to projects)
- Shell scripts that modify home directory
- Manual profile configuration before first use
- Complex inheritance system requiring upfront decisions

**Impact:** High friction to adoption, especially for teams

### 1.2 Context Bloat from Standards

**Current Problem:**
- Large standards files loaded into context regardless of task
- Conditional loading embedded in standards files themselves (pseudo-code IF/ELSE blocks)
- No intelligent filtering based on actual task requirements
- Standards inheritance creates duplication

**Impact:** Wasted tokens, slower responses, reduced effectiveness

### 1.3 Indiscriminate MCP Loading

**Current Problem:**
- MCPs bundled at project level, always loaded
- No task-based MCP activation
- Every session pays the cost of unused integrations
- All tool definitions loaded upfront (can be 100,000+ tokens)

**Impact:** Resource waste, potential security surface expansion, latency

### 1.4 Profile System Complexity

**Current Problem:**
- Profiles conflate tech stack, team preferences, and project types
- Inheritance hierarchies become hard to maintain
- Changes require re-compilation to projects
- No easy way to mix standards from different profiles

**Impact:** Maintenance burden, reduced flexibility

### 1.5 Standards Misrepresented as Skills

**Current Problem:**
- Coding standards converted to Claude Code Skills
- Skills are **model-invoked** (Claude decides when to use)
- Standards should be **always-applied guidelines**, not optional capabilities
- Creates inconsistent code quality when Claude doesn't invoke the "skill"

**Impact:** Unreliable standards adherence, defeats purpose of having standards

### 1.6 Intermediate Results Bloat Context (NEW)

**Current Problem:**
- MCP tool results flow through context window
- Large documents (specs, meeting transcripts, data exports) consume excessive tokens
- Data must be written back out when passed between tools
- Complex multi-step workflows multiply token usage

**Impact:** Token waste, hitting context limits, copy errors in data transfer

---

## Part 2: Code Mode Architecture (NEW)

This section introduces **Code Mode**, a pattern from Anthropic's engineering team that fundamentally changes how agents interact with MCP tools. Instead of direct tool calls that flow through context, agents write code that executes in a sandboxed environment.

### 2.1 The Problem with Direct Tool Calls

**Traditional MCP Pattern:**
```
User: "Get my spec from Google Drive and create Jira tickets for each task"

Agent (direct tool calls):
  TOOL CALL: gdrive.getDocument(id: "spec-123")
  → returns 15,000 tokens of spec content (loaded into context)
  
  TOOL CALL: jira.createIssue(summary: "Task 1", description: "[copies spec excerpt]")
  → spec content written out again
  
  TOOL CALL: jira.createIssue(summary: "Task 2", description: "[copies spec excerpt]")
  → spec content written out again
  ...
```

**Problems:**
- Spec content (15,000 tokens) loaded into context
- Content copied multiple times for each Jira ticket
- Total token usage: 50,000+ tokens
- Risk of copy errors in data transfer

### 2.2 Code Mode Solution

**Code Mode Pattern:**
```typescript
// Agent writes code that executes in sandbox
import * as gdrive from './servers/google-drive';
import * as jira from './servers/jira';

const spec = await gdrive.getDocument({ id: 'spec-123' });
const tasks = parseTasksFromSpec(spec.content);

for (const task of tasks) {
  await jira.createIssue({
    project: 'RED64',
    summary: task.title,
    description: task.description
  });
}

console.log(`Created ${tasks.length} Jira issues`);
```

**Benefits:**
- Spec content stays in execution environment
- Never flows through model context
- Agent sees only: `"Created 12 Jira issues"`
- Total token usage: ~500 tokens (98% reduction)

### 2.3 Progressive Tool Discovery

Instead of loading all tool definitions upfront, tools are represented as a filesystem:

```
.red64/servers/
├── google-drive/
│   ├── index.ts              # Server exports
│   ├── getDocument.ts        # Individual tool
│   ├── listFiles.ts
│   └── uploadFile.ts
├── jira/
│   ├── index.ts
│   ├── createIssue.ts
│   ├── getIssue.ts
│   └── searchIssues.ts
├── github/
│   ├── index.ts
│   ├── createPR.ts
│   └── ...
└── _catalog.json             # Tool search index
```

**Discovery Pattern:**
```typescript
// Agent explores filesystem to find tools
const servers = await fs.readdir('./servers');
// → ['google-drive', 'jira', 'github']

// Agent reads only the tool it needs
const getDocTool = await fs.readFile('./servers/google-drive/getDocument.ts');
// → Gets interface, description, parameters
```

**Token Impact:**
- Traditional: 150,000 tokens (all tool definitions upfront)
- Code Mode: 2,000 tokens (only tools actually used)
- **Savings: 98.7%**

### 2.4 Context-Efficient Data Filtering

When working with large datasets, filter in execution environment:

```typescript
// BAD: All rows flow through context
const allTasks = await red64.getTasks({ specId: 'feature-123' });
// → 500 tasks, 50,000 tokens in context

// GOOD: Filter in execution environment
const allTasks = await red64.getTasks({ specId: 'feature-123' });
const pendingTasks = allTasks.filter(t => t.status === 'pending');
const summary = pendingTasks.map(t => ({ id: t.id, title: t.title }));
console.log(`${pendingTasks.length} pending tasks:`, summary.slice(0, 5));
// → Agent sees: "47 pending tasks: [{id, title}, ...]"
```

### 2.5 Privacy-Preserving Operations

Sensitive data can flow through workflows without reaching the model:

```typescript
// PII stays in execution environment
const customers = await salesforce.getLeads({ status: 'new' });

for (const customer of customers) {
  await email.send({
    to: customer.email,      // Real email never seen by model
    subject: 'Welcome!',
    body: generateWelcome(customer.name)
  });
}

console.log(`Sent ${customers.length} welcome emails`);
// Agent sees only the count, not the PII
```

**Optional Tokenization:**
```typescript
// MCP client can tokenize PII before it reaches model
const customers = await salesforce.getLeads({ status: 'new' });
// What agent sees if it logs:
// [{ email: '[EMAIL_1]', name: '[NAME_1]' }, ...]
// Real data used in actual API calls
```

### 2.6 State Persistence and Skill Generation

Agents can persist state and generate reusable skills:

```typescript
// Persist intermediate results
const analysisResults = await analyzeCodebase();
await fs.writeFile('.red64/cache/analysis.json', JSON.stringify(analysisResults));

// Later session picks up where it left off
const cached = JSON.parse(await fs.readFile('.red64/cache/analysis.json'));
```

**Skill Generation:**
```typescript
// Agent develops a working pattern, saves as reusable skill
// .red64/skills/sync-spec-to-jira/skill.ts

import * as gdrive from '../servers/google-drive';
import * as jira from '../servers/jira';

export async function syncSpecToJira(specId: string, projectKey: string) {
  const spec = await gdrive.getDocument({ id: specId });
  const tasks = parseTasksFromSpec(spec.content);
  
  const created = [];
  for (const task of tasks) {
    const issue = await jira.createIssue({
      project: projectKey,
      summary: task.title,
      description: task.description,
      labels: ['red64-generated']
    });
    created.push(issue.key);
  }
  
  return { created, count: created.length };
}
```

With a `SKILL.md` file, this becomes a reusable capability:
```markdown
# Sync Spec to Jira

Syncs a Red64 specification document to Jira issues.

## Usage
Call `syncSpecToJira(specId, projectKey)` to create Jira issues from spec tasks.

## Parameters
- specId: Google Drive document ID of the spec
- projectKey: Jira project key (e.g., 'RED64')

## Returns
- created: Array of created issue keys
- count: Number of issues created
```

---

## Part 3: Red64 Architecture Design

### 3.1 Plugin Ecosystem Overview (Updated for Code Mode)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RED64 ECOSYSTEM                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────┐                                                  │
│  │   red64-runtime    │  ← NEW: Code execution sandbox                   │
│  │                    │                                                  │
│  │ • Sandboxed exec   │                                                  │
│  │ • MCP code bridges │                                                  │
│  │ • State persistence│                                                  │
│  │ • PII tokenization │                                                  │
│  └────────────────────┘                                                  │
│           │                                                              │
│  ┌────────┴─────────┐   ┌──────────────────┐   ┌──────────────────┐     │
│  │   red64-core     │   │ red64-standards- │   │  red64-workflows │     │
│  │                  │   │    [stack]       │   │                  │     │
│  │ • Base workflows │   │ • nextjs         │   │ • Orchestration  │     │
│  │ • Context mgmt   │   │ • rails          │   │ • Multi-agent    │     │
│  │ • Standards API  │   │ • python         │   │ • Task routing   │     │
│  │ • Hooks infra    │   │ • golang         │   │ • Verification   │     │
│  └──────────────────┘   │ • (composable)   │   └──────────────────┘     │
│           │             └──────────────────┘            │               │
│           │                      │                      │               │
│           └──────────────────────┼──────────────────────┘               │
│                                  │                                      │
│  ┌───────────────────────────────┴───────────────────────────────────┐  │
│  │                 CODE MODE EXTENSION PLUGINS                        │  │
│  ├───────────────┬───────────────┬───────────────┬──────────────────┤  │
│  │ red64-metrics │ red64-jira    │ red64-github  │ red64-[ext]      │  │
│  │               │               │               │                  │  │
│  │ Code bridges: │ Code bridges: │ Code bridges: │ • Custom         │  │
│  │ • logMetric() │ • createIssue │ • createPR()  │   integrations   │  │
│  │ • query()     │ • sync()      │ • review()    │ • Your MCP       │  │
│  │ • export()    │ • search()    │ • merge()     │   servers        │  │
│  └───────────────┴───────────────┴───────────────┴──────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Runtime Plugin: `red64-runtime` (NEW)

**Purpose:** Provides the sandboxed code execution environment for Code Mode operations.

**Directory Structure:**
```
red64-runtime/
├── .claude-plugin/
│   └── plugin.json
├── sandbox/
│   ├── executor.ts               # Sandboxed code runner
│   ├── resource-limits.ts        # CPU, memory, time limits
│   └── security-policy.ts        # Filesystem, network restrictions
├── bridges/
│   ├── mcp-bridge.ts             # Generic MCP → Code API bridge
│   ├── generator.ts              # Generates typed bridges from MCP schemas
│   └── templates/
│       └── tool-template.ts      # Template for generated tool files
├── privacy/
│   ├── tokenizer.ts              # PII tokenization
│   ├── detokenizer.ts            # Restore real values for API calls
│   └── patterns.json             # PII detection patterns
├── state/
│   ├── persistence.ts            # State save/restore
│   └── cache-manager.ts          # Intermediate result caching
├── skills/
│   ├── skill-generator.ts        # Generate skills from agent code
│   └── skill-registry.ts         # Track available generated skills
└── README.md
```

**MCP Bridge Generation:**

When an MCP server is connected, Red64 automatically generates typed code bridges:

```typescript
// bridges/generator.ts
export async function generateBridges(mcpServer: MCPServer): Promise<void> {
  const tools = await mcpServer.listTools();
  
  for (const tool of tools) {
    const bridgeCode = generateToolBridge(tool);
    await fs.writeFile(
      `.red64/servers/${mcpServer.name}/${tool.name}.ts`,
      bridgeCode
    );
  }
  
  // Generate index file
  const indexCode = generateServerIndex(tools);
  await fs.writeFile(
    `.red64/servers/${mcpServer.name}/index.ts`,
    indexCode
  );
}

function generateToolBridge(tool: MCPTool): string {
  return `
import { callMCPTool } from '../../runtime/mcp-client';

interface ${tool.name}Input {
  ${tool.inputSchema.properties.map(p => `${p.name}: ${p.type};`).join('\n  ')}
}

interface ${tool.name}Response {
  ${tool.outputSchema.properties.map(p => `${p.name}: ${p.type};`).join('\n  ')}
}

/**
 * ${tool.description}
 */
export async function ${tool.name}(input: ${tool.name}Input): Promise<${tool.name}Response> {
  return callMCPTool<${tool.name}Response>('${tool.fullName}', input);
}
`;
}
```

### 3.3 Core Plugin: `red64-core` (Updated)

**Purpose:** Foundation layer providing the spec-driven workflow, standards infrastructure, and Code Mode integration.

**Directory Structure:**
```
red64-core/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── init.md                    # Initialize Red64 in a project
│   ├── plan-product.md            # Product planning workflow
│   ├── shape-spec.md              # Requirements shaping
│   ├── write-spec.md              # Spec generation
│   ├── create-tasks.md            # Task breakdown
│   ├── implement-tasks.md         # Direct implementation
│   └── code-mode/                 # NEW: Code Mode utilities
│       ├── generate-bridges.md    # Generate MCP code bridges
│       ├── search-tools.md        # Search available tools
│       └── create-skill.md        # Save code as reusable skill
├── agents/
│   ├── spec-shaper.md             # Interactive requirements agent
│   ├── task-planner.md            # Task decomposition agent
│   ├── standards-advisor.md       # Standards consultation agent
│   └── code-executor.md           # NEW: Code Mode execution agent
├── hooks/
│   └── hooks.json                 # Context injection hooks
├── scripts/
│   ├── context-loader.py          # Intelligent context loading
│   ├── standards-injector.py      # Standards injection logic
│   ├── task-analyzer.py           # Task type detection
│   └── bridge-generator.py        # NEW: MCP bridge generation
├── servers/                        # NEW: Generated MCP code bridges
│   └── .gitkeep                   # Populated at runtime
├── templates/
│   ├── product/
│   │   ├── mission.md
│   │   ├── roadmap.md
│   │   └── tech-stack.md
│   └── spec/
│       ├── requirements.md
│       ├── specification.md
│       └── tasks.md
└── README.md
```

**Updated Hook Configuration (Code Mode Aware):**
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/bridge-generator.py"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/context-loader.py --code-mode"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command", 
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/standards-injector.py"
          }
        ]
      }
    ]
  }
}
```

### 3.4 Standards Plugins: `red64-standards-[stack]` (Updated for Filesystem Discovery)

**Key Change:** Standards are now organized as a filesystem for on-demand discovery, not injected wholesale.

**Example: `red64-standards-nextjs`**
```
red64-standards-nextjs/
├── .claude-plugin/
│   └── plugin.json
├── standards/                      # Filesystem-based discovery
│   ├── _index.json                 # Searchable catalog
│   ├── components/
│   │   ├── _summary.md             # Quick overview (50 tokens)
│   │   ├── naming.md               # Full details (500 tokens)
│   │   ├── structure.md
│   │   └── patterns.md
│   ├── routing/
│   │   ├── _summary.md
│   │   ├── app-router.md
│   │   └── api-routes.md
│   ├── state/
│   │   ├── _summary.md
│   │   ├── server-state.md
│   │   └── client-state.md
│   └── testing/
│       ├── _summary.md
│       ├── unit.md
│       └── e2e.md
├── hooks/
│   └── hooks.json
└── manifest.json
```

**Catalog Index (`_index.json`):**
```json
{
  "stack": "nextjs",
  "version": "14.x",
  "categories": [
    {
      "id": "components",
      "keywords": ["component", "tsx", "jsx", "react", "ui"],
      "summary_file": "standards/components/_summary.md",
      "detail_files": [
        "standards/components/naming.md",
        "standards/components/structure.md",
        "standards/components/patterns.md"
      ],
      "summary_tokens": 50,
      "detail_tokens": 1500
    },
    {
      "id": "routing",
      "keywords": ["route", "page", "api", "endpoint", "navigation"],
      "summary_file": "standards/routing/_summary.md",
      "detail_files": [
        "standards/routing/app-router.md",
        "standards/routing/api-routes.md"
      ],
      "summary_tokens": 40,
      "detail_tokens": 800
    }
  ]
}
```

**Progressive Standards Discovery:**

```typescript
// Agent discovers standards via filesystem
const standardsPlugins = await fs.readdir('.red64/standards/');
// → ['nextjs', 'typescript', 'testing-rtl']

// Agent reads index to understand what's available
const nextjsIndex = JSON.parse(
  await fs.readFile('.red64/standards/nextjs/_index.json')
);

// For quick context, agent reads summaries (50 tokens each)
const componentSummary = await fs.readFile(
  '.red64/standards/nextjs/standards/components/_summary.md'
);

// For implementation, agent reads full details (500+ tokens)
const namingRules = await fs.readFile(
  '.red64/standards/nextjs/standards/components/naming.md'
);
```

**Token Efficiency:**
- Traditional injection: 5,000 tokens (all standards)
- Filesystem discovery: 100-600 tokens (only what's needed)
- **Savings: 88-98%**

### 3.5 Workflows Plugin: `red64-workflows` (Updated for Code Mode)

**Purpose:** Advanced multi-agent orchestration using Code Mode for efficient data passing.

**Code Mode Workflow Execution:**

```typescript
// Instead of passing data through context between agents,
// workflows use filesystem and execution environment

// orchestrator writes task assignments
await fs.writeFile('.red64/workspace/assignments.json', JSON.stringify({
  backend: ['task-1', 'task-2', 'task-3'],
  frontend: ['task-4', 'task-5'],
  testing: ['task-6']
}));

// Each agent reads its assignments and writes results
// backend-implementer.ts
const assignments = JSON.parse(
  await fs.readFile('.red64/workspace/assignments.json')
);
const myTasks = assignments.backend;

for (const taskId of myTasks) {
  const task = await fs.readFile(`.red64/specs/active/feature/tasks/${taskId}.md`);
  // ... implement task ...
  await fs.writeFile(`.red64/workspace/results/${taskId}.json`, result);
}

// orchestrator collects results without them flowing through context
const resultFiles = await fs.readdir('.red64/workspace/results/');
const summary = resultFiles.map(f => {
  const result = JSON.parse(fs.readFileSync(`.red64/workspace/results/${f}`));
  return { task: f, status: result.status };
});
console.log('Workflow complete:', summary);
```

### 3.6 Code Mode Extension Architecture

**Purpose:** Extensions use Code Mode for efficient integration with external tools.

**Extension Interface Contract (Updated):**
```
red64-extension-[name]/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json                       # MCP server definitions
├── servers/                        # Auto-generated code bridges
│   └── [extension-name]/
│       ├── index.ts
│       └── [tool].ts
├── skills/                         # Reusable operation patterns
│   └── [skill-name]/
│       ├── SKILL.md
│       └── skill.ts
├── commands/
│   └── [extension-specific commands]
├── hooks/
│   └── hooks.json
└── README.md
```

**Example: `red64-jira` (Code Mode)**
```
red64-jira/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json                       # Jira MCP server config
├── servers/
│   └── jira/                       # Generated code bridges
│       ├── index.ts
│       ├── createIssue.ts
│       ├── getIssue.ts
│       ├── searchIssues.ts
│       ├── updateIssue.ts
│       └── transitionIssue.ts
├── skills/
│   ├── sync-spec-to-jira/
│   │   ├── SKILL.md
│   │   └── skill.ts
│   └── import-epic-as-spec/
│       ├── SKILL.md
│       └── skill.ts
├── commands/
│   ├── sync-spec.md                # Sync current spec to Jira
│   ├── import-requirements.md      # Import from Jira epic
│   └── update-status.md            # Batch update issue statuses
└── hooks/
    └── hooks.json
    # Hook: On spec completion, offer to sync to Jira
    # Hook: On task completion, update Jira status
```

**Jira Skill Example (Code Mode):**
```typescript
// skills/sync-spec-to-jira/skill.ts
import * as jira from '../../servers/jira';
import * as fs from 'fs';

interface SyncResult {
  created: string[];
  updated: string[];
  errors: string[];
}

export async function syncSpecToJira(
  specPath: string, 
  projectKey: string,
  epicKey?: string
): Promise<SyncResult> {
  // Read spec from filesystem (not through context)
  const spec = JSON.parse(await fs.readFile(specPath, 'utf-8'));
  const tasks = spec.tasks || [];
  
  const result: SyncResult = { created: [], updated: [], errors: [] };
  
  for (const task of tasks) {
    try {
      if (task.jiraKey) {
        // Update existing issue
        await jira.updateIssue({
          issueKey: task.jiraKey,
          fields: {
            summary: task.title,
            description: task.description,
            labels: ['red64-managed']
          }
        });
        result.updated.push(task.jiraKey);
      } else {
        // Create new issue
        const issue = await jira.createIssue({
          project: projectKey,
          issuetype: 'Task',
          summary: task.title,
          description: task.description,
          parent: epicKey ? { key: epicKey } : undefined,
          labels: ['red64-managed']
        });
        
        // Update local spec with Jira key
        task.jiraKey = issue.key;
        result.created.push(issue.key);
      }
    } catch (error) {
      result.errors.push(`${task.id}: ${error.message}`);
    }
  }
  
  // Write updated spec back
  await fs.writeFile(specPath, JSON.stringify(spec, null, 2));
  
  return result;
}
```

**Example: `red64-metrics` (Privacy-Preserving)**
```
red64-metrics/
├── .claude-plugin/
│   └── plugin.json
├── servers/
│   └── metrics/
│       ├── index.ts
│       ├── logEvent.ts
│       ├── query.ts
│       └── export.ts
├── collectors/
│   ├── token-usage.ts              # Track token consumption
│   ├── task-velocity.ts            # Tasks completed over time
│   ├── quality-scores.ts           # Lint/test pass rates
│   └── privacy-filter.ts           # NEW: Remove PII before logging
├── commands/
│   ├── report.md
│   └── dashboard.md
└── storage/
    └── schema.sql
```

**Privacy-Preserving Metrics Collection:**
```typescript
// collectors/privacy-filter.ts
import { tokenize } from '../../runtime/privacy/tokenizer';

export function sanitizeMetricEvent(event: MetricEvent): MetricEvent {
  return {
    ...event,
    // Tokenize any potentially sensitive fields
    filePath: tokenize(event.filePath, 'PATH'),
    userName: tokenize(event.userName, 'NAME'),
    // Keep aggregate data as-is
    tokenCount: event.tokenCount,
    duration: event.duration,
    success: event.success
  };
}

// Usage in token-usage.ts
export async function logTokenUsage(session: Session): Promise<void> {
  const event = {
    sessionId: session.id,
    filePath: session.activeFile,
    userName: session.user,
    tokenCount: session.tokensUsed,
    duration: session.duration,
    success: session.success
  };
  
  // Sanitize before logging - PII never reaches storage
  const sanitized = sanitizeMetricEvent(event);
  await metrics.logEvent(sanitized);
  
  // Agent sees only: "Logged session metrics"
  console.log('Logged session metrics');
}
```

---

## Part 4: Intelligent Context Management (Updated)

### 4.1 The Context Loading Problem (Expanded)

Agent OS's current approach has multiple inefficiencies:
1. **Standards loaded all at once** — Wastes tokens on irrelevant standards
2. **Standards as Skills** — Claude may not invoke them when needed
3. **MCP tools defined upfront** — 100,000+ tokens before any work
4. **Intermediate results in context** — Data copied between tool calls

### 4.2 Red64's Multi-Layer Solution

**Layer 1: Filesystem-Based Tool Discovery**
```
.red64/servers/           # MCP tools as code APIs
├── google-drive/
├── jira/
├── github/
└── _catalog.json         # Searchable index

Agent explores → reads only needed tools → 98% token reduction
```

**Layer 2: Progressive Standards Disclosure**
```
.red64/standards/         # Standards as filesystem
├── nextjs/
│   ├── _index.json       # Searchable catalog
│   ├── components/
│   │   ├── _summary.md   # Quick overview (50 tokens)
│   │   └── naming.md     # Full details (500 tokens)
│   └── ...
└── typescript/

Agent reads summary → reads details only if implementing → 88% token reduction
```

**Layer 3: Hook-Based Context Injection**
```python
# For code editing, inject ONLY relevant standards
# PreToolUse hook on Edit|Write

def inject_standards(tool_input):
    file_path = tool_input.get('file_path', '')
    
    # Determine which standards apply
    standards = []
    if file_path.endswith('.tsx'):
        standards.append(read_summary('nextjs/components'))
        standards.append(read_summary('typescript/types'))
    
    # Inject minimal context
    return format_context(standards, max_tokens=500)
```

**Layer 4: Execution Environment Data Handling**
```typescript
// Large data stays in execution environment
const allTasks = await loadAllTasks();           // 500 tasks
const pending = allTasks.filter(t => !t.done);   // Filter in sandbox
console.log(`${pending.length} pending tasks`);  // Agent sees count only

// Pass data between tools without context
await fs.writeFile('.red64/temp/data.json', JSON.stringify(data));
const data = JSON.parse(await fs.readFile('.red64/temp/data.json'));
```

### 4.3 Token Budget Architecture

```yaml
# .red64/config.yaml
context:
  budgets:
    standards_summary: 200      # Quick standard overviews
    standards_detail: 1000      # Full standards when implementing
    product_context: 300        # Mission, current spec
    tool_discovery: 500         # Tool definitions loaded on-demand
    
  strategies:
    standards: progressive      # summary → detail as needed
    tools: filesystem           # explore → read specific tools
    data: execution             # filter in sandbox, not context
    
  priorities:
    - active_spec_context       # Current feature being built
    - relevant_standards        # Standards matching file types
    - tool_definitions          # Tools being used
    - product_mission           # High-level guidance
```

### 4.4 Tool Search Capability

For large tool ecosystems, provide search:

```typescript
// .red64/servers/_search.ts
interface ToolSearchResult {
  server: string;
  tool: string;
  description: string;
  relevance: number;
}

export async function searchTools(
  query: string,
  options: { detailLevel: 'name' | 'description' | 'full' } = { detailLevel: 'description' }
): Promise<ToolSearchResult[]> {
  const catalog = JSON.parse(await fs.readFile('.red64/servers/_catalog.json'));
  
  const results = catalog.tools
    .filter(t => matchesQuery(t, query))
    .sort((a, b) => b.relevance - a.relevance)
    .slice(0, 10);
  
  if (options.detailLevel === 'name') {
    return results.map(t => ({ server: t.server, tool: t.name }));
  } else if (options.detailLevel === 'description') {
    return results.map(t => ({ 
      server: t.server, 
      tool: t.name, 
      description: t.description 
    }));
  } else {
    // Full: include parameter schemas
    return Promise.all(results.map(async t => ({
      ...t,
      schema: await loadToolSchema(t.server, t.name)
    })));
  }
}
```

---

## Part 5: Project Data Structure (Updated)

### 5.1 Complete Directory Structure

```
project/
├── .claude/                        # Claude Code native config
│   ├── settings.json               # Plugin configuration
│   └── CLAUDE.md                   # Minimal project context
│
├── .red64/                         # Red64 project data
│   ├── config.yaml                 # Project configuration
│   │
│   ├── product/                    # Product context layer
│   │   ├── mission.md
│   │   ├── roadmap.md
│   │   └── tech-stack.md
│   │
│   ├── specs/                      # Feature specs
│   │   ├── active/
│   │   │   └── feature-name/
│   │   │       ├── requirements.md
│   │   │       ├── specification.md
│   │   │       ├── tasks.json
│   │   │       └── progress.md
│   │   └── archive/
│   │
│   ├── standards/                  # Linked from plugins (symlinks)
│   │   ├── nextjs -> ~/.red64/plugins/red64-standards-nextjs/standards
│   │   └── typescript -> ~/.red64/plugins/red64-standards-typescript/standards
│   │
│   ├── servers/                    # NEW: Generated MCP code bridges
│   │   ├── google-drive/
│   │   │   ├── index.ts
│   │   │   └── getDocument.ts
│   │   ├── jira/
│   │   │   ├── index.ts
│   │   │   └── createIssue.ts
│   │   └── _catalog.json           # Searchable tool index
│   │
│   ├── skills/                     # NEW: Generated reusable skills
│   │   ├── sync-spec-to-jira/
│   │   │   ├── SKILL.md
│   │   │   └── skill.ts
│   │   └── generate-pr-description/
│   │       ├── SKILL.md
│   │       └── skill.ts
│   │
│   ├── workspace/                  # NEW: Code Mode working directory
│   │   ├── temp/                   # Temporary files
│   │   ├── results/                # Workflow results
│   │   └── cache/                  # Cached intermediate data
│   │
│   └── metrics/                    # Usage and quality metrics
│       └── sessions.db
│
└── src/                            # Your actual code
```

### 5.2 CLAUDE.md Integration (Updated)

```markdown
# Project Context

This project uses Red64 for spec-driven development with Code Mode.

## Active Work
See `.red64/specs/active/` for current feature specifications.

## Standards (Filesystem Discovery)
Standards are available via filesystem exploration:
- List available: `ls .red64/standards/`
- Read index: `cat .red64/standards/[stack]/_index.json`
- Read summary: `cat .red64/standards/[stack]/[category]/_summary.md`
- Read details: `cat .red64/standards/[stack]/[category]/[file].md`

Enabled stacks: nextjs, typescript, testing-rtl

## Tools (Code Mode)
MCP tools are available as code APIs:
- List servers: `ls .red64/servers/`
- Search tools: `import { searchTools } from '.red64/servers/_search'`
- Use tool: `import * as jira from '.red64/servers/jira'`

## Commands
- `/red64:status` - View current spec and task progress
- `/red64:implement` - Continue implementing current tasks
- `/red64:verify` - Run verification checks
- `/red64:search-tools [query]` - Find available tools
- `/red64:create-skill` - Save code pattern as reusable skill
```

---

## Part 6: Implementation Roadmap (Updated)

### Phase 0: Runtime Foundation (Weeks 1-2) — NEW

**Goal:** Establish the Code Mode execution environment.

**Deliverables:**
1. `red64-runtime` plugin with:
   - Sandboxed TypeScript execution environment
   - MCP bridge generator (MCP schema → typed code API)
   - Basic state persistence (filesystem-based)
   - Resource limits and security policy

2. Proof-of-concept Code Mode:
   - Connect one MCP server (e.g., filesystem)
   - Generate code bridges automatically
   - Execute agent-written code in sandbox
   - Demonstrate 90%+ token reduction

**Success Criteria:**
- Can generate typed bridges from any MCP server
- Agent can write and execute code against bridges
- Execution is sandboxed with appropriate limits
- Token usage reduced by >90% vs direct tool calls

### Phase 1: Core Foundation (Weeks 3-5)

**Goal:** Establish the base plugin with Code Mode integration.

**Deliverables:**
1. `red64-core` plugin with:
   - `/red64:init` command (project initialization)
   - `/red64:plan-product` command (product planning workflow)
   - Filesystem-based standards discovery
   - Hook infrastructure for context loading
   - Integration with `red64-runtime`

2. Tool discovery system:
   - `_catalog.json` generation for all connected MCPs
   - `searchTools()` function for finding tools
   - Progressive detail loading (name → description → full schema)

**Success Criteria:**
- Can initialize a project with Red64
- Can run product planning workflow
- Tools discoverable via filesystem exploration
- Standards loadable on-demand

### Phase 2: Standards Plugins (Weeks 6-8)

**Goal:** Create the modular standards plugin architecture with filesystem discovery.

**Deliverables:**
1. Standards plugin specification:
   - `_index.json` schema for searchable catalogs
   - `_summary.md` convention for quick overviews
   - Progressive loading hooks

2. Reference implementations:
   - `red64-standards-typescript`
   - `red64-standards-nextjs`
   - `red64-standards-python`

3. Standards discovery:
   - Symlink standards into `.red64/standards/`
   - Search across all enabled standards
   - Priority-based selection for injection

**Success Criteria:**
- Can install multiple standards plugins
- Standards discoverable via filesystem
- Only needed standards loaded (88%+ token savings)
- Easy to create new standards plugins

### Phase 3: Spec-Driven Workflow (Weeks 9-11)

**Goal:** Implement the full feature development cycle with Code Mode.

**Deliverables:**
1. Complete workflow commands:
   - `/red64:shape-spec`
   - `/red64:write-spec`
   - `/red64:create-tasks`
   - `/red64:implement-tasks`

2. Code Mode workflow operations:
   - Large specs handled in execution environment
   - Task data passed via filesystem, not context
   - Progress tracking without context bloat

3. Basic agents:
   - `spec-shaper` agent
   - `task-planner` agent
   - `code-executor` agent (Code Mode specialist)

**Success Criteria:**
- Can run complete feature development cycle
- Large specs don't bloat context
- Tasks executed efficiently via Code Mode
- Verification gates work

### Phase 4: Orchestration (Weeks 12-14)

**Goal:** Multi-agent orchestration with Code Mode data passing.

**Deliverables:**
1. `red64-workflows` plugin:
   - `/red64:orchestrate-tasks` command
   - Workflow definition format (YAML)
   - Built-in workflow templates

2. Code Mode orchestration:
   - Agents share data via `.red64/workspace/`
   - Results aggregated without context bloat
   - Parallel execution with filesystem coordination

3. Skill generation:
   - `/red64:create-skill` command
   - Auto-generate SKILL.md from working code
   - Skill registry for discovery

**Success Criteria:**
- Can orchestrate multi-phase feature development
- Data passes between agents without context bloat
- Generated skills are reusable
- Parallel tasks execute correctly

### Phase 5: Extensions (Weeks 15-18)

**Goal:** Code Mode extension architecture and reference integrations.

**Deliverables:**
1. Extension interface specification:
   - Code bridge generation for extension MCPs
   - Skill packaging for extension operations
   - Privacy-preserving patterns

2. Reference extensions:
   - `red64-metrics` (privacy-preserving usage tracking)
   - `red64-github` (PR workflow with Code Mode)
   - `red64-jira` (issue sync with Code Mode)

3. Documentation:
   - Extension development guide
   - Code Mode patterns and best practices
   - Privacy implementation guide

**Success Criteria:**
- Can create Code Mode extensions
- Metrics collected with PII protection
- GitHub/Jira integrations work efficiently
- Extensions are 90%+ more token-efficient than direct MCP

### Phase 6: Polish & Release (Weeks 19-20)

**Goal:** Production readiness and community release.

**Deliverables:**
1. Marketplace setup:
   - Official Red64 marketplace
   - Plugin discovery and installation
   - Version management

2. Migration tooling:
   - Agent OS to Red64 migration script
   - Standards conversion utility

3. Documentation & Examples:
   - Getting started guide
   - Code Mode cookbook
   - Video tutorials
   - Example projects

**Success Criteria:**
- Easy installation via marketplace
- Existing Agent OS users can migrate
- Community can contribute plugins
- Code Mode patterns well-documented

---

## Part 7: Technical Specifications (Updated)

### 7.1 Plugin Manifest Schema (Updated)

```json
{
  "$schema": "https://red64.dev/schemas/plugin.json",
  "name": "red64-core",
  "version": "1.0.0",
  "description": "Core Red64 framework with Code Mode support",
  "author": {
    "name": "Red64 Team"
  },
  "red64": {
    "type": "core",
    "version": "2.0",
    "requires": ["red64-runtime"],
    "features": {
      "codeMode": true,
      "filesystemDiscovery": true,
      "privacyTokenization": false
    }
  },
  "components": {
    "commands": "commands/",
    "agents": "agents/",
    "hooks": "hooks/hooks.json",
    "scripts": "scripts/",
    "servers": "servers/"
  }
}
```

### 7.2 MCP Code Bridge Schema

```typescript
// Generated bridge file structure
interface MCPBridgeFile {
  // Import statement
  import: "import { callMCPTool } from '../../runtime/mcp-client';";
  
  // Input interface
  inputInterface: {
    name: string;           // e.g., "GetDocumentInput"
    properties: Property[];
  };
  
  // Output interface
  outputInterface: {
    name: string;           // e.g., "GetDocumentResponse"
    properties: Property[];
  };
  
  // Function definition
  function: {
    name: string;           // e.g., "getDocument"
    description: string;    // JSDoc comment
    async: true;
    parameters: string;     // "input: GetDocumentInput"
    returnType: string;     // "Promise<GetDocumentResponse>"
    body: string;           // "return callMCPTool<...>(...)"
  };
}

interface Property {
  name: string;
  type: string;
  required: boolean;
  description?: string;
}
```

### 7.3 Tool Catalog Schema

```json
{
  "$schema": "https://red64.dev/schemas/catalog.json",
  "version": "1.0",
  "generated": "2025-11-28T10:00:00Z",
  "servers": [
    {
      "name": "google-drive",
      "description": "Google Drive file operations",
      "tools": [
        {
          "name": "getDocument",
          "description": "Retrieve a document from Google Drive",
          "keywords": ["document", "file", "read", "gdrive"],
          "inputSummary": "documentId: string, fields?: string",
          "bridgePath": "servers/google-drive/getDocument.ts"
        }
      ]
    }
  ],
  "totalTools": 47,
  "searchIndex": {
    "document": ["google-drive/getDocument", "notion/getPage"],
    "issue": ["jira/createIssue", "jira/getIssue", "github/createIssue"]
  }
}
```

### 7.4 Skill Definition Schema

```typescript
// SKILL.md frontmatter
interface SkillMetadata {
  name: string;
  description: string;
  version: string;
  author?: string;
  tags: string[];
  triggers: string[];         // Keywords that suggest this skill
  dependencies: string[];     // Required MCP servers
  privacy: {
    piiHandled: boolean;
    tokenization: boolean;
  };
}

// skill.ts interface
interface SkillFunction {
  name: string;
  description: string;
  parameters: SkillParameter[];
  returns: SkillReturn;
  implementation: string;     // The actual code
}

interface SkillParameter {
  name: string;
  type: string;
  description: string;
  required: boolean;
  default?: any;
}

interface SkillReturn {
  type: string;
  description: string;
  properties?: Property[];
}
```

### 7.5 Privacy Tokenization Schema

```typescript
interface TokenizationConfig {
  patterns: {
    EMAIL: RegExp;
    PHONE: RegExp;
    SSN: RegExp;
    CREDIT_CARD: RegExp;
    NAME: RegExp;
    PATH: RegExp;
    API_KEY: RegExp;
  };
  
  // Which fields to always tokenize
  alwaysTokenize: string[];   // ['email', 'phone', 'ssn']
  
  // Which MCP servers can receive untokenized data
  trustedServers: string[];   // ['salesforce', 'hubspot']
  
  // Token format
  tokenFormat: '[TYPE_N]';    // e.g., [EMAIL_1], [NAME_2]
}

interface TokenMap {
  token: string;              // '[EMAIL_1]'
  original: string;           // 'user@example.com'
  type: string;               // 'EMAIL'
  created: string;            // ISO timestamp
  expiresAt: string;          // ISO timestamp (session-scoped)
}
```

---

## Part 8: Code Mode Patterns Cookbook (NEW)

### 8.1 Basic Tool Usage

```typescript
// Discover and use a tool
const servers = await fs.readdir('.red64/servers/');
console.log('Available servers:', servers);

// Read tool definition
const createIssueDef = await fs.readFile('.red64/servers/jira/createIssue.ts', 'utf-8');
console.log('Tool interface:', createIssueDef);

// Use the tool
import * as jira from '.red64/servers/jira';
const issue = await jira.createIssue({
  project: 'RED64',
  summary: 'Implement feature X',
  description: 'Details here...'
});
console.log('Created:', issue.key);
```

### 8.2 Large Data Handling

```typescript
// Filter large datasets in execution environment
import * as sheets from '.red64/servers/google-sheets';

const data = await sheets.getSheet({ sheetId: 'abc123' });
// data has 10,000 rows - don't log it all!

const summary = {
  totalRows: data.rows.length,
  columns: data.headers,
  preview: data.rows.slice(0, 3)
};
console.log('Sheet summary:', summary);

// Filter to what we need
const activeUsers = data.rows.filter(r => r.status === 'active');
console.log(`Found ${activeUsers.length} active users`);
```

### 8.3 Multi-Tool Workflows

```typescript
// Chain tools with data staying in execution environment
import * as gdrive from '.red64/servers/google-drive';
import * as jira from '.red64/servers/jira';
import * as slack from '.red64/servers/slack';

// Get spec from Drive
const spec = await gdrive.getDocument({ id: 'spec-123' });
const tasks = parseTasksFromSpec(spec.content);

// Create Jira issues
const createdIssues = [];
for (const task of tasks) {
  const issue = await jira.createIssue({
    project: 'RED64',
    summary: task.title,
    description: task.description
  });
  createdIssues.push(issue.key);
}

// Notify team on Slack
await slack.postMessage({
  channel: '#dev-team',
  text: `Created ${createdIssues.length} issues from spec: ${createdIssues.join(', ')}`
});

// Agent sees only this summary
console.log(`Workflow complete: ${createdIssues.length} issues created and team notified`);
```

### 8.4 State Persistence

```typescript
// Save progress for later sessions
const analysisState = {
  filesAnalyzed: 47,
  issuesFound: 12,
  lastFile: 'src/components/Button.tsx',
  timestamp: new Date().toISOString()
};

await fs.writeFile('.red64/workspace/cache/analysis-state.json', 
  JSON.stringify(analysisState, null, 2)
);

// In a later session, resume
const savedState = JSON.parse(
  await fs.readFile('.red64/workspace/cache/analysis-state.json', 'utf-8')
);
console.log(`Resuming from ${savedState.lastFile}, ${savedState.filesAnalyzed} files done`);
```

### 8.5 Privacy-Preserving Operations

```typescript
// Handle PII without exposing to model
import { tokenize, detokenize } from '.red64/runtime/privacy';
import * as crm from '.red64/servers/salesforce';

const leads = await crm.getLeads({ status: 'new' });

// If we need to log, tokenize first
const safeLeads = leads.map(l => ({
  id: l.id,
  email: tokenize(l.email, 'EMAIL'),
  name: tokenize(l.name, 'NAME')
}));
console.log('Processing leads:', safeLeads);

// When sending to trusted destination, real data flows through
for (const lead of leads) {
  await crm.updateLead({
    id: lead.id,
    status: 'contacted'
  });
}

console.log(`Updated ${leads.length} leads`);
```

### 8.6 Generating Reusable Skills

```typescript
// After developing a working pattern, save it as a skill
const skillCode = `
import * as gdrive from '../servers/google-drive';
import * as notion from '../servers/notion';

export async function syncDriveToNotion(folderId: string, notionDbId: string) {
  const files = await gdrive.listFiles({ folderId });
  
  for (const file of files) {
    const content = await gdrive.getDocument({ id: file.id });
    await notion.createPage({
      database: notionDbId,
      title: file.name,
      content: content.body
    });
  }
  
  return { synced: files.length };
}
`;

const skillMd = `
# Sync Drive to Notion

Syncs all documents from a Google Drive folder to a Notion database.

## Usage
\`syncDriveToNotion(folderId, notionDbId)\`

## Parameters
- folderId: Google Drive folder ID
- notionDbId: Notion database ID

## Returns
- synced: Number of documents synced
`;

await fs.mkdir('.red64/skills/sync-drive-to-notion', { recursive: true });
await fs.writeFile('.red64/skills/sync-drive-to-notion/skill.ts', skillCode);
await fs.writeFile('.red64/skills/sync-drive-to-notion/SKILL.md', skillMd);

console.log('Skill saved: sync-drive-to-notion');
```

---

## Part 9: Migration Strategy from Agent OS (Updated)

### 9.1 Compatibility Mapping

| Agent OS Feature | Red64 Equivalent | Migration Path |
|-----------------|------------------|----------------|
| `~/agent-os/` base | Marketplace plugins | Install `red64-core` + `red64-runtime` |
| Profiles | Standards plugins | Map profiles to plugin combos |
| Standards files | Filesystem-discoverable standards | Convert with migration tool |
| `.agent-os/` project dir | `.red64/` directory | Automated migration |
| Slash commands | Plugin commands | Namespace changes |
| Subagents | Plugin agents | Compatible format |
| Skills (from standards) | Filesystem standards + hooks | Architectural change |
| Direct MCP calls | Code Mode bridges | Automatic generation |

### 9.2 Migration Benefits

| Metric | Agent OS | Red64 | Improvement |
|--------|----------|-------|-------------|
| Tool definition tokens | 150,000 | 2,000 | 98.7% reduction |
| Standards tokens | 5,000 | 300-600 | 88-94% reduction |
| Intermediate data tokens | Variable | ~0 | 100% (in execution env) |
| Installation time | 10+ minutes | < 1 minute | 90% faster |
| Context efficiency | Low | High | Dramatic improvement |

---

## Part 10: Success Metrics (Updated)

### 10.1 Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Installation time | < 1 minute | Time to first command |
| Tool definition tokens | < 2,000 | Per session average |
| Standards tokens | < 600 | Per task average |
| Intermediate data tokens | < 100 | Passed through context |
| Total context efficiency | > 95% reduction | vs Agent OS baseline |
| Plugin load time | < 500ms | Startup measurement |
| Workflow completion | > 95% | Tasks completed successfully |
| Code Mode execution | < 2s | Average operation time |

### 10.2 Adoption Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Migration rate | > 80% of Agent OS users | Survey + analytics |
| Plugin ecosystem | 20+ standards plugins | Marketplace count |
| Community skills | 50+ generated skills | Skill registry count |
| Community contributions | 10+ community plugins | GitHub PRs |
| Documentation coverage | 100% of features | Doc audit |

---

## Conclusion

Red64 v2 represents a fundamental advancement over both Agent OS and the initial Red64 design. By incorporating Anthropic's **Code Mode** pattern for MCP interactions, we achieve:

1. **98%+ token reduction** on tool definitions and operations
2. **Filesystem-based discovery** for both tools and standards
3. **Privacy-preserving workflows** where sensitive data never reaches the model
4. **State persistence and skill generation** for evolving agent capabilities
5. **Context-efficient orchestration** where multi-agent workflows don't bloat context

The key insight is that LLMs are excellent at writing code. By presenting MCP tools as code APIs rather than direct tool calls, and by handling data transformations in an execution environment rather than context, Red64 enables dramatically more efficient and capable agents.

Combined with the plugin-first architecture and proper separation of standards from skills, Red64 provides a modern, scalable foundation for spec-driven development with AI agents.

---

*Document Version: 2.0*
*Last Updated: November 2025*
*Key Addition: Code Mode Architecture from Anthropic Engineering*
*Author: Claude (with direction from Yacin)*
