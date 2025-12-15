# Red64 Framework: Plugin System vs Claude Agent SDK Analysis

## Executive Summary

This document evaluates whether the Claude Agent SDK offers advantages over the current Claude Code plugin-based approach for implementing the Red64 spec-driven development framework. Based on research into the SDK's capabilities, architecture, and intended use cases, we provide recommendations for the optimal implementation strategy.

**Key Finding**: The Claude Agent SDK is **highly relevant** to Red64 and could significantly simplify implementation, particularly for:
- Multi-agent orchestration (the "war room" approach)
- Session management and context persistence
- Custom tool integration
- Production deployment scenarios

However, the SDK works **in conjunction with** the plugin system, not as a replacement. The optimal approach is a **hybrid architecture** that leverages both.

---

## Understanding the Two Approaches

### Current Approach: Claude Code Plugin System

The plugin system provides a **file-system based configuration** mechanism:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # Metadata and configuration
├── commands/                # User-invoked slash commands
├── agents/                  # Specialized sub-agents (markdown files)
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

**Characteristics:**
- Declarative (markdown/JSON-based)
- Distributed via marketplaces
- Auto-discovery at runtime
- No code execution required for basic functionality
- Limited programmatic control

### New Approach: Claude Agent SDK

The Agent SDK provides a **programmatic interface** to the same underlying capabilities:

```typescript
import { query, ClaudeAgentOptions } from "@anthropic-ai/claude-agent-sdk";

const options: ClaudeAgentOptions = {
  systemPrompt: "You are a spec-driven development assistant...",
  agents: {
    'code-reviewer': {
      description: 'Expert code review specialist',
      prompt: '...',
      tools: ['Read', 'Grep', 'Glob'],
      model: 'sonnet'
    }
  },
  mcp_servers: { ... },
  plugins: [{ type: "local", path: "./red64-core" }],
  permissionMode: 'acceptEdits'
};

for await (const message of query({ prompt, options })) {
  // Handle streaming responses
}
```

**Characteristics:**
- Programmatic (TypeScript/Python)
- Full control over agent lifecycle
- Session management and persistence
- Custom hooks and tools as code
- Can load plugins programmatically
- Production deployment features (error handling, monitoring, context compaction)

---

## SDK Capabilities Relevant to Red64

### 1. Multi-Agent Orchestration (Subagents)

The SDK provides **programmatic subagent definition** - exactly what Red64's "war room" approach needs:

```typescript
const result = query({
  prompt: "Migrate the authentication module from Delphi 5 to Delphi 12",
  options: {
    agents: {
      'lead-architect': {
        description: 'Reviews architecture and creates migration strategy',
        prompt: `You are the Lead Architect...`,
        tools: ['Read', 'Grep', 'Glob', 'Write'],
        model: 'opus'
      },
      'code-migration-specialist': {
        description: 'Handles actual code migration',
        prompt: `You are the Code Migration Specialist...`,
        tools: ['Read', 'Write', 'Edit', 'Bash'],
        model: 'sonnet'
      },
      'qa-engineer': {
        description: 'Tests and validates migrations',
        prompt: `You are the QA Engineer...`,
        tools: ['Read', 'Bash', 'Grep'],
        model: 'sonnet'
      }
    }
  }
});
```

**Advantages over plugin-based agents:**
- **Isolated context**: Each subagent has its own context window
- **Parallel execution**: Multiple subagents can run concurrently
- **Tool restrictions**: Per-agent tool permissions
- **Model selection**: Different models for different agents (Opus for architect, Sonnet for implementation)

### 2. Context Management

The SDK provides automatic **context compaction** - critical for long-running migration tasks:

```typescript
const options = {
  // Auto-summarizes when context approaches limit
  contextManagement: 'auto-compact',
  
  // Session can be resumed later
  sessionId: 'migration-session-001'
};
```

This solves one of Red64's stated goals: "optimize context size."

### 3. Custom Tools (In-Process MCP)

The SDK allows defining tools **in-code** rather than as external MCP servers:

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions

@tool("analyze_delphi_unit", "Analyze a Delphi unit file", {"path": str})
async def analyze_delphi(args):
    # Custom Delphi parsing logic
    return {
        "content": [{
            "type": "text", 
            "text": f"Unit analysis: {result}"
        }]
    }

@tool("check_migration_status", "Check migration status", {"spec_id": str})
async def check_status(args):
    # Read from Red64's spec tracking
    return { ... }

delphi_tools = create_sdk_mcp_server(
    name="red64-delphi",
    version="1.0.0",
    tools=[analyze_delphi, check_status]
)
```

**Benefits:**
- No subprocess management
- Better performance (no IPC overhead)
- Simpler deployment (single process)
- Type safety

### 4. Hooks as Code

The SDK supports **programmatic hooks** rather than just JSON configuration:

```python
async def pre_tool_use_hook(tool_name, args):
    # Validate before any tool execution
    if tool_name == "Write":
        # Check against coding standards
        return validate_against_standards(args)
    return True

options = ClaudeAgentOptions(
    hooks={
        'pre_tool_use': pre_tool_use_hook
    }
)
```

This is perfect for Red64's standards enforcement.

### 5. Plugin Loading

**Critical**: The SDK can **load plugins programmatically**:

```typescript
const result = query({
  prompt: "...",
  options: {
    plugins: [
      { type: "local", path: "./red64-core" },
      { type: "local", path: "./red64-standards-delphi" }
    ],
    settingSources: ["project"]  // Load CLAUDE.md, skills, etc.
  }
});
```

This means **plugins and SDK are complementary**, not competing approaches.

---

## Recommended Hybrid Architecture

Based on this analysis, Red64 should use a **layered hybrid approach**:

### Layer 1: Plugin Packages (Distribution)

Keep the plugin structure for **distribution and sharing**:

```
red64-core/                     # Plugin package
├── .claude-plugin/plugin.json
├── skills/                     # Auto-discovered skills
├── commands/                   # Slash commands
└── agents/                     # Markdown-based agents (fallback)

red64-standards-delphi/         # Standards plugin
├── .claude-plugin/plugin.json
└── skills/
    └── delphi-expert/
        └── SKILL.md
```

**Rationale**: Plugins provide the marketplace/distribution model and work with vanilla Claude Code users.

### Layer 2: Agent SDK Application (Orchestration)

Build a **Red64 CLI/Application** using the Agent SDK that:

1. **Loads plugins programmatically**
2. **Defines sophisticated agent orchestration**
3. **Manages sessions and state**
4. **Provides production monitoring**

```typescript
// red64-cli/src/migrate.ts
import { ClaudeSDKClient, ClaudeAgentOptions } from "@anthropic-ai/claude-agent-sdk";
import { loadDelphiTools } from "./tools/delphi";
import { loadMigrationAgents } from "./agents/migration";

async function runMigration(specPath: string) {
  const options: ClaudeAgentOptions = {
    systemPrompt: await loadSystemPrompt(),
    
    // Load plugins for skills/standards
    plugins: [
      { type: "local", path: "./plugins/red64-core" },
      { type: "local", path: "./plugins/red64-standards-delphi" }
    ],
    
    // Programmatic agents for war room
    agents: loadMigrationAgents(),
    
    // Custom tools
    mcp_servers: {
      "delphi": loadDelphiTools()
    },
    
    // Production settings
    permissionMode: 'acceptEdits',
    maxBudgetTokens: 100000
  };

  const client = new ClaudeSDKClient({ options });
  
  try {
    await client.query(`Execute migration spec: ${specPath}`);
    
    for await (const msg of client.receive_response()) {
      await handleMessage(msg);
    }
  } finally {
    await client.close();
  }
}
```

### Layer 3: Enterprise Features (Optional)

For enterprise deployments, the SDK enables:

- **Session persistence** across restarts
- **Cost tracking** with budget limits
- **Audit logging** via hooks
- **Custom authentication** (Bedrock/Vertex)

---

## Comparison Matrix

| Capability | Plugin System | Agent SDK | Hybrid |
|------------|--------------|-----------|--------|
| **Distribution** | ✅ Marketplace | ❌ Code-based | ✅ Plugins for distribution |
| **Multi-agent orchestration** | ⚠️ Basic | ✅ Sophisticated | ✅ SDK orchestration |
| **Context management** | ❌ Manual | ✅ Auto-compact | ✅ SDK manages |
| **Custom tools** | ⚠️ External MCP | ✅ In-process | ✅ Both options |
| **Session persistence** | ❌ None | ✅ Built-in | ✅ SDK provides |
| **Standards enforcement** | ⚠️ Skills | ✅ Hooks | ✅ Hooks + Skills |
| **Production monitoring** | ❌ None | ✅ Built-in | ✅ SDK provides |
| **Vanilla Claude Code** | ✅ Works | ❌ Requires app | ✅ Plugins still work |
| **Ease of authoring** | ✅ Markdown | ⚠️ Code | ✅ Best of both |

---

## Implementation Recommendations

### Phase 1: Keep Plugin Architecture (Weeks 1-4)

Continue developing:
- `red64-core` plugin
- `red64-standards-*` plugins
- Skills and commands

This ensures compatibility with vanilla Claude Code users.

### Phase 2: Build SDK-Based CLI (Weeks 5-8)

Create `@red64/cli` using the Agent SDK:

```bash
npm install @red64/cli

# Simple usage (loads plugins, basic orchestration)
red64 migrate --spec ./specs/auth-module

# Advanced usage (full war room)
red64 migrate --spec ./specs/auth-module \
  --agents lead-architect,code-migration,qa \
  --parallel \
  --session migration-001
```

### Phase 3: Enterprise Features (Weeks 9-12)

Add enterprise capabilities:
- Cost tracking and budgets
- Audit logging
- Custom authentication
- Session resumption
- Integration with SDLC tools (Jira, GitHub)

---

## Code Example: Red64 Migration Agent

Here's a complete example of how the SDK-based Red64 migration could work:

```python
# red64/migration_agent.py
import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient, 
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server
)

# Custom tools for Delphi migration
@tool("parse_delphi_unit", "Parse a Delphi .pas file", {"path": str})
async def parse_delphi(args):
    # Delphi parsing logic
    return {"content": [{"type": "text", "text": "..."}]}

@tool("validate_migration", "Validate migrated code", {"original": str, "migrated": str})
async def validate_migration(args):
    # Migration validation logic
    return {"content": [{"type": "text", "text": "..."}]}

# War room agents
MIGRATION_AGENTS = {
    'lead-architect': {
        'description': 'Reviews architecture, creates migration strategy, coordinates team',
        'prompt': '''You are the Lead Architect for Delphi migrations.
Your responsibilities:
1. Analyze the legacy codebase structure
2. Create migration strategies
3. Delegate tasks to specialized agents
4. Review and approve final implementations''',
        'tools': ['Read', 'Grep', 'Glob', 'mcp__delphi__parse_delphi_unit'],
        'model': 'opus'
    },
    'code-migration': {
        'description': 'Handles actual code migration from Delphi 5 to Delphi 12+',
        'prompt': '''You are the Code Migration Specialist.
Focus on:
1. Translating legacy patterns to modern equivalents
2. Updating deprecated APIs
3. Maintaining functionality while improving code quality''',
        'tools': ['Read', 'Write', 'Edit', 'Bash', 'mcp__delphi__parse_delphi_unit'],
        'model': 'sonnet'
    },
    'qa-engineer': {
        'description': 'Tests and validates migrations',
        'prompt': '''You are the QA Engineer.
Ensure:
1. All tests pass after migration
2. No regressions in functionality
3. Performance meets requirements''',
        'tools': ['Read', 'Bash', 'mcp__delphi__validate_migration'],
        'model': 'sonnet'
    }
}

async def run_migration(spec_path: str, session_id: str = None):
    # Create MCP server for Delphi tools
    delphi_server = create_sdk_mcp_server(
        name="delphi",
        version="1.0.0",
        tools=[parse_delphi, validate_migration]
    )
    
    options = ClaudeAgentOptions(
        system_prompt="""You are the Red64 Migration Orchestrator.
Coordinate with your team of specialized agents to execute the migration spec.
Follow the spec-driven development process: analyze → plan → implement → validate.""",
        
        # Load Red64 plugins
        plugins=[
            {"type": "local", "path": "./plugins/red64-core"},
            {"type": "local", "path": "./plugins/red64-standards-delphi"}
        ],
        
        # War room agents
        agents=MIGRATION_AGENTS,
        
        # Custom tools
        mcp_servers={"delphi": delphi_server},
        
        # Production settings
        permission_mode="acceptEdits",
        setting_sources=["project"],  # Load CLAUDE.md
        max_budget_tokens=500000
    )
    
    async with ClaudeSDKClient(options=options) as client:
        # Load and execute spec
        with open(spec_path) as f:
            spec_content = f.read()
        
        await client.query(f"Execute this migration spec:\n\n{spec_content}")
        
        async for msg in client.receive_response():
            if msg.type == "assistant":
                print(f"[Orchestrator] {msg.content}")
            elif msg.type == "tool_use":
                print(f"[Tool] {msg.tool_name}: {msg.input}")
            elif msg.type == "subagent":
                print(f"[{msg.agent_name}] {msg.content}")

if __name__ == "__main__":
    asyncio.run(run_migration("./specs/2024-01-15-auth-migration/spec.md"))
```

---

## Conclusion

The Claude Agent SDK is **highly relevant** to Red64 and addresses many of the pain points identified with the pure plugin approach:

| Pain Point | SDK Solution |
|------------|--------------|
| Verbose/fragile plugin configs | Programmatic definition with type safety |
| Limited multi-agent control | Sophisticated subagent orchestration |
| Context management | Auto-compaction and session persistence |
| Standards enforcement | In-code hooks for validation |
| Production readiness | Built-in monitoring and error handling |

**Recommendation**: Adopt a **hybrid architecture** where:
1. **Plugins** handle distribution and vanilla Claude Code compatibility
2. **Agent SDK** provides the orchestration layer for sophisticated workflows
3. **Custom CLI** wraps everything for a seamless user experience

This approach gives Red64 the best of both worlds: easy distribution via plugins and powerful orchestration via the SDK.
