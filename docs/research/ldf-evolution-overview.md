# LDF Framework Evolution - Complete Vision

> **Research Date**: December 2025
> **Branch**: `research/ink-react-cli`
> **Status**: Vision Approved

---

## Executive Summary

Transform LDF from a spec-driven framework into a comprehensive AI-assisted development platform with:

1. **ldf-core** - Standalone TypeScript logic library (Python CLI wrapper for enterprise)
2. **ldf-cli** - Enhanced CLI with Claude Code-inspired features (Ink + Pastel)
3. **SAIL Methodology** - 4-phase product-led development (Scope → Architect → Implement → Learn)
4. **Multi-platform distribution** - CLI, VS Code extension, VM templates
5. **Configurable AI agents** - Multi-provider support with reasoning levels

---

## The SAIL Methodology

```
┌─────────────────────────────────────────────────────────────┐
│                     LDF SAIL METHODOLOGY                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   S ───────→ A ───────→ I ───────→ L ──────┐               │
│   Scope     Architect   Implement   Learn   │               │
│                                       │     │               │
│   Define    Design      Build with   Deploy,│               │
│   what &    how         TDD          monitor│               │
│   why                                iterate │               │
│                                       │     │               │
│   ←─────────────────────────────────────────┘               │
│              (Learnings inform next iteration)              │
│                                                             │
│   "SAIL from idea to iteration"                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

| Phase | Name | Focus | Agents | Artifacts |
|-------|------|-------|--------|-----------|
| **S** | Scope | Define boundaries, requirements, user stories, success criteria | 📋 Product Agent | requirements.md, user-stories.yaml |
| **A** | Architect | Design solution, system structure, pseudocode, decisions | 📐 Architect Agent | design.md, architecture/, decisions.md |
| **I** | Implement | Build with TDD, test, verify, security review | ⚡ Coder + 🧪 Tester + 🛡️ Security | code, tests, security-report.md |
| **L** | Learn | Deploy, monitor, gather feedback, iterate | 🚀 Deploy + 📊 Monitor | deployment.md, monitoring.md, learnings.md |

### Why SAIL?

1. **Journey metaphor** - Development is a voyage with course corrections
2. **"Learn" as final phase** - Explicitly captures the iteration loop
3. **Clear dev terminology** - "Architect" and "Implement" are unambiguous
4. **PM alignment** - "Scope" is fundamental product work
5. **Memorable word** - Positive, adventurous, implies forward movement

---

## All Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **ldf-core Language** | TypeScript only + Python CLI wrapper | Single codebase, simpler maintenance. Python devs use CLI, not library imports. Can add bindings later if enterprise demand. |
| **Methodology** | SAIL (Scope → Architect → Implement → Learn) | 4 phases with built-in iteration loop. Product-led, not stretched for acronym. |
| **Agent Architecture** | Single-agent + sub-agents (Boomerang pattern) | Isolated context execution with attempt_completion summaries. Max 1 level of sub-agent depth. |
| **Virtualization** | Local with OS sandboxing default | Docker/Colima/remote as opt-in. Follows Claude Code pattern. |
| **LLM Providers** | Multi-provider (Claude, OpenAI, Gemini) | Reasoning levels (low/medium/high/xhigh). Switchable at runtime. |
| **User Story Export** | Jira, GitHub Issues, Linear, CSV | YAML format with priority, points, labels. Export to multiple trackers. |
| **Python CLI Scope** | Full feature parity (goal) | Thin wrapper around TypeScript CLI. Same commands, same output. |
| **Enterprise Sync** | Config in company-controlled repo | Startup screen shows active profile. Settings hierarchy applies. |
| **Remote Environment** | Build in-house + Codespaces support | Docker templates for AWS, Azure, GCP. Add-on architecture. |
| **Versioning** | Major versions compatible within ecosystem | 1.x.x works with 1.x.x. Cross-major requires migration. |
| **Migration Path** | AI-assisted prompt + documentation only | No code-based migration tools. Prompt guides users through upgrade. |
| **Offline Mode** | All works except hosted API calls | Local model addon option (DeepSeek, etc.) for offline use. |

---

## Proposed Architecture

### Repository Structure

```
ldf-ecosystem/
├── ldf-core/                    # Core logic library (npm)
│   ├── src/
│   │   ├── guardrails/         # Guardrail loading, validation
│   │   ├── specs/              # Spec parsing, validation
│   │   ├── projects/           # Detection, resolution
│   │   ├── config/             # Configuration management
│   │   ├── lint/               # Linting engine
│   │   └── security/           # Path validation, secrets
│   ├── _framework/             # Embedded guardrails, templates, packs
│   └── package.json
│
├── ldf-cli/                     # Primary CLI (Ink + Pastel)
│   ├── src/
│   │   ├── commands/           # File-based command routing
│   │   ├── components/         # Ink React components
│   │   ├── permissions/        # Permission system
│   │   ├── settings/           # Hierarchical settings
│   │   ├── providers/          # LLM provider abstraction
│   │   ├── onboarding/         # Path-based onboarding
│   │   └── addons/             # Add-on management
│   └── package.json
│
├── ldf-cli-python/              # Python CLI (thin wrapper)
│   └── (shells out to bundled ldf-cli-ts)
│
├── ldf-vscode/                  # VS Code extension (already exists)
│   └── (enhance integration)
│
└── ldf-templates/               # VM templates
    ├── docker/
    ├── aws/
    └── azure/
```

### ldf-core Module Design

```typescript
// ldf-core/src/index.ts
export {
  // Guardrails
  loadCoreGuardrails,
  loadPresetGuardrails,
  getActiveGuardrails,
  Guardrail,

  // Specs
  parseSpec,
  extractTasks,
  extractGuardrailMatrix,
  SpecStatus,
  TaskItem,

  // Projects
  detectProjectState,
  ProjectState,
  DetectionResult,
  resolveProjectContext,

  // Linting
  lintSpec,
  lintProject,
  LintResult,
  LintReport,

  // Config
  loadConfig,
  ConfigFile,

  // Security
  validateSpecName,
  validatePath,
  isPathSafe,
} from './modules';
```

---

## Claude Code Patterns to Adopt

| Pattern | Claude Code | LDF Adaptation |
|---------|-------------|----------------|
| **Permissions** | 3-state (Yes/Yes-always/No) | Graduated trust with static analysis |
| **Settings** | Enterprise → Project → User | Company → System → Workspace → Project |
| **Output Styles** | Expert/Explanatory/Learning | Same + custom styles |
| **Sandboxing** | OS-level (no VMs by default) | Optional Docker/Colima layer |
| **Plugins** | MCP + marketplace | Enhanced MCP management |
| **Onboarding** | CLAUDE.md pattern | Path-based persona onboarding |

### Permission System

```typescript
interface PermissionDecision {
  action: 'allow' | 'deny' | 'allow_always';
  scope?: 'command' | 'directory' | 'session';
  target?: string; // e.g., "rm", "/Users/dev/*"
}

interface PermissionConfig {
  enterprise?: EnterprisePermissions;  // Company-wide (fetched)
  system?: SystemPermissions;          // ~/.ldf/permissions.yaml
  workspace?: WorkspacePermissions;    // ldf-workspace.yaml
  project?: ProjectPermissions;        // .ldf/permissions.yaml
}
```

### Settings Hierarchy

```
Precedence (High to Low):
1. Enterprise/Company Profile (synced from company repo)
2. System User (~/.ldf/settings.yaml)
3. Workspace (ldf-workspace.yaml)
4. Project (.ldf/settings.yaml)
5. Local Override (.ldf/settings.local.yaml) - gitignored
```

### Output Styles

- **Expert Mode**: Minimal output, action-focused
- **Explanatory Mode**: Step-by-step breakdowns, reasoning
- **Learning Mode**: Educational, fundamentals-focused, TODO(human) markers

### Onboarding Paths

```
Path 1: New Developer
├── Dev directory setup (/user/dev)
├── Tooling scan & install (git, brew, ssh, vscode)
├── Single-project workspace recommendation
├── Virtualization guidance
└── Local backup best practices

Path 2: Experienced Developer
├── Dev directory confirmation
├── Quick tooling check
├── Workspace vs project selection
├── Local vs Docker vs Remote decision
└── Skip to project setup

Path 3: Expert Mode
├── Company structure setup
├── Enterprise permissions profile
├── Advanced workspace configuration
└── Multi-project/team setup
```

---

## Agent Architecture

Inspired by [Boomerang Tasks](https://www.linkedin.com/pulse/boomerang-tasks-automating-code-development-roo-sparc-reuven-cohen-nr3zc/):

```
┌─────────────────────────────────────────────────────────────┐
│                    LDF AGENT ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              MAIN ORCHESTRATOR AGENT                  │   │
│  │  - Single-threaded master loop (Claude Code style)   │   │
│  │  - Configurable primary LLM (Claude/GPT/Gemini)      │   │
│  │  - Spawns sub-agents with depth limit (max 1 level)  │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│            ┌─────────────┼─────────────┐                    │
│            ▼             ▼             ▼                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ SAIL Modes   │ │ Review Modes │ │ Utility Modes│        │
│  ├──────────────┤ ├──────────────┤ ├──────────────┤        │
│  │ 📋 Scope     │ │ 🛡️ Security  │ │ 🔍 Explorer  │        │
│  │ 📐 Architect │ │ 🧪 Tester    │ │ 📚 Docs      │        │
│  │ ⚡ Implement │ │ 🔬 Reviewer  │ │ 🚀 Deploy    │        │
│  │ 📊 Learn     │ │ 🧹 Optimizer │ │ 📈 Monitor   │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│                                                              │
│  Boomerang Pattern:                                          │
│  1. Main agent creates isolated sub-task                     │
│  2. Sub-agent executes with focused context                  │
│  3. Sub-agent returns via attempt_completion                 │
│  4. Main agent integrates result                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key Principles:**
- **Isolated Context**: Each sub-agent gets only relevant context
- **Structured Completion**: Mandatory summary on task completion
- **No Recursion**: Sub-agents cannot spawn their own sub-agents
- **Provider Flexibility**: Sub-agents can use different LLM than main agent
- **Mode Awareness**: Clear which specialist handles each task type

---

## Multi-Provider Support

Inspired by [Codex CLI's configuration](https://github.com/openai/codex/blob/main/docs/config.md):

```typescript
interface LLMProvider {
  name: 'claude' | 'openai' | 'gemini' | 'local';
  apiKey?: string;
  baseUrl?: string;
  models: ModelConfig[];
}

interface ModelConfig {
  id: string;                    // e.g., "claude-3-opus", "gpt-5-codex"
  alias?: string;                // e.g., "opus", "codex"
  supportsReasoning: boolean;
  reasoningEffort?: 'low' | 'medium' | 'high' | 'xhigh';
  verbosity?: 'minimal' | 'normal' | 'detailed';
  purpose?: 'coding' | 'planning' | 'review' | 'all';
}
```

**Runtime switching:**
```bash
ldf config provider claude      # Switch primary provider
ldf config model opus           # Switch model
ldf config reasoning high       # Set reasoning effort
/model gpt-5-codex             # In-session switch
```

---

## User Story Export

Export user stories to multiple issue trackers:

```yaml
# .ldf/specs/{feature}/user-stories.yaml
stories:
  - id: US-001
    title: User Registration
    as_a: new visitor
    i_want_to: create an account
    so_that: I can access the platform
    acceptance_criteria:
      - AC-001: Valid email required
      - AC-002: Password meets complexity
    priority: high
    points: 5
    labels: [auth, mvp]
```

**Supported exports:**
- **Jira** - Native import format
- **GitHub Issues** - Markdown with labels
- **Linear** - Linear API format
- **CSV** - Universal fallback

---

## Implementation Phases

### Phase 1: Research Documentation (Current)
- [x] Create evolution overview document
- [ ] Create SAIL methodology guide
- [ ] Create agent architecture document
- [ ] Update CLI migration spec

### Phase 2: Core Extraction (2-3 weeks)
- Extract pure business logic to ldf-core package
- TypeScript implementation
- Publish as npm package
- Maintain backward compatibility with current Python CLI

### Phase 3: Enhanced CLI Foundation (3-4 weeks)
- Ink + Pastel CLI scaffold
- Permission system (3-state with static analysis)
- Settings hierarchy (Enterprise → Project)
- Basic command migration (status, lint, init)
- Multi-provider abstraction layer

### Phase 4: SAIL Methodology (2-3 weeks)
- New spec templates (decisions.md, learnings.md)
- TDD anchors in requirements template
- User story YAML format with export
- Enhanced linting for SAIL phases

### Phase 5: Agent System (2-3 weeks)
- Single-agent master loop
- Sub-agent spawning with Boomerang pattern
- Specialized modes (Scope, Architect, Implement, Learn)
- Reasoning effort configuration

### Phase 6: Onboarding & Output Styles (2 weeks)
- Three onboarding paths (New Dev, Experienced, Expert)
- Output style system (Expert, Explanatory, Learning)
- Tooling detection and guided install

### Phase 7: Environment & Distribution (2-3 weeks)
- OS-level sandboxing (default)
- Docker/Colima integration (optional)
- Remote environment add-on
- Cross-platform packaging
- VS Code extension updates

---

## Feasibility Assessment

### High Feasibility (Low Risk)

1. **Core Extraction** - Architecture already supports separation
2. **SAIL Methodology** - Evolutionary from current 3-phase
3. **Permission System** - Well-documented patterns from Claude Code
4. **Settings Hierarchy** - Standard configuration pattern
5. **Output Styles** - System prompt modification approach

### Medium Effort (Medium Risk)

1. **Multi-Provider LLM** - API differences, rate limiting, error handling
2. **Agent Boomerang Pattern** - Context isolation, completion integration
3. **User Story Export** - Each tracker has different API/format
4. **Python CLI Wrapper** - Bundling TypeScript for Python distribution

### Requires Research/Prototyping (Higher Risk)

1. **OS-Level Sandboxing** - Platform-specific (seccomp, AppArmor, macOS Sandbox)
2. **Remote Environment Add-on** - Cloud provider integration complexity
3. **Enterprise Sync** - Authentication, distribution mechanisms

---

## Items for Further Exploration

| Topic | Notes |
|-------|-------|
| **MCP Enhancement Priority** | Evaluate which MCP improvements provide most value |
| **Documentation Standards** | Define required vs optional artifacts; lead by example |
| **Testing Agent System** | How to test Boomerang delegation patterns effectively |
| **Rate Limiting Strategy** | Monitor API usage, explore local model addon |
| **Local Model Addon** | Support running models locally (DeepSeek, etc.) |
| **Model Training Addon** | Custom model training for organization-specific needs |

---

## References

- [How Claude Code is built](https://newsletter.pragmaticengineer.com/p/how-claude-code-is-built) - Pragmatic Engineer
- [Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices) - Anthropic
- [Claude Code sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing) - Security approach
- [Boomerang Tasks](https://www.linkedin.com/pulse/boomerang-tasks-automating-code-development-roo-sparc-reuven-cohen-nr3zc/) - Task delegation pattern
- [Codex CLI config](https://github.com/openai/codex/blob/main/docs/config.md) - Reasoning levels
- [Ink documentation](https://github.com/vadimdemedes/ink) - React for terminals
- [Pastel framework](https://github.com/vadimdemedes/pastel) - File-based CLI routing

---

## Related Documents

- [SAIL Methodology Guide](./sail-methodology.md)
- [Agent Architecture](./agent-architecture.md)
- [Ink + React CLI Migration](./ink-react-cli-migration-v2.md)
