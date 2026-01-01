# LDF Agent Architecture

> **Research Date**: December 2025
> **Branch**: `research/ink-react-cli`
> **Status**: Approved
> **Pattern**: Boomerang Task Delegation

---

## Overview

LDF uses a **single-agent + sub-agents** architecture inspired by [Boomerang Tasks](https://www.linkedin.com/pulse/boomerang-tasks-automating-code-development-roo-sparc-reuven-cohen-nr3zc/) and Claude Code's design. This provides the benefits of specialized agents while maintaining a coherent main context.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    LDF AGENT ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                 MAIN ORCHESTRATOR AGENT                     │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │ • Single-threaded master loop                        │  │ │
│  │  │ • Maintains full conversation context                │  │ │
│  │  │ • Routes tasks to appropriate sub-agents             │  │ │
│  │  │ • Integrates results back into main context          │  │ │
│  │  │ • Configurable primary LLM (Claude/GPT/Gemini)       │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│              ┌───────────────┼───────────────┐                  │
│              │               │               │                  │
│              ▼               ▼               ▼                  │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐│
│  │   SAIL AGENTS    │ │  REVIEW AGENTS   │ │  UTILITY AGENTS  ││
│  ├──────────────────┤ ├──────────────────┤ ├──────────────────┤│
│  │ 📋 Scope Agent   │ │ 🛡️ Security Agent│ │ 🔍 Explorer Agent││
│  │ 📐 Architect     │ │ 🧪 Tester Agent  │ │ 📚 Docs Agent    ││
│  │ ⚡ Coder Agent   │ │ 🔬 Reviewer Agent│ │ 🚀 Deploy Agent  ││
│  │ 📊 Learn Agent   │ │ 🧹 Optimizer     │ │ 📈 Monitor Agent ││
│  └──────────────────┘ └──────────────────┘ └──────────────────┘│
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    BOOMERANG PATTERN                        │ │
│  │  1. Main agent creates isolated sub-task                   │ │
│  │  2. Sub-agent executes with focused context                │ │
│  │  3. Sub-agent returns via attempt_completion               │ │
│  │  4. Main agent integrates result                           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Principles

### 1. Single Orchestrator

The main agent maintains the full conversation context and makes all high-level decisions:

```typescript
interface OrchestratorAgent {
  // Full conversation history
  context: ConversationContext;

  // Primary LLM configuration
  provider: LLMProvider;
  model: string;

  // Spawn sub-agents for specific tasks
  delegate(task: SubTask): Promise<SubAgentResult>;

  // Integrate results back into main context
  integrate(result: SubAgentResult): void;
}
```

### 2. Isolated Sub-Agent Context

Sub-agents receive only the context they need, not the full conversation:

```typescript
interface SubAgentContext {
  // Task-specific context only
  task: TaskDescription;
  relevantFiles: string[];
  relevantCode: CodeSnippet[];

  // Constraints
  maxTokens: number;
  timeoutMs: number;

  // Sub-agents cannot spawn their own sub-agents
  canDelegate: false;
}
```

### 3. Structured Completion

Every sub-agent must return a structured result:

```typescript
interface SubAgentResult {
  // Status
  success: boolean;

  // Summary for main agent
  summary: string;

  // Artifacts produced
  artifacts: {
    files?: FileChange[];
    analysis?: string;
    recommendations?: string[];
  };

  // Metadata
  tokensUsed: number;
  duration: number;
}
```

### 4. No Recursion

Sub-agents cannot spawn their own sub-agents:

```
Main Agent
    └── Sub-Agent (max depth 1)
            └── ❌ Cannot spawn further sub-agents
```

This prevents unbounded recursion and keeps context manageable.

---

## The Boomerang Pattern

The "boomerang" pattern describes how tasks are delegated and results returned:

```
┌────────────────────────────────────────────────────────────────┐
│                      BOOMERANG TASK FLOW                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  MAIN AGENT                                                    │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ 1. User requests: "Add user authentication"            │   │
│  │ 2. Main agent analyzes and breaks into subtasks        │   │
│  │ 3. Delegates: "Design auth architecture"               │   │
│  └────────────────────────────────────────────────────────┘   │
│              │                                                 │
│              │ THROW (isolated context)                        │
│              ▼                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ SUB-AGENT: Architect                                    │   │
│  │                                                         │   │
│  │ Receives:                                               │   │
│  │ • Task: "Design auth architecture"                     │   │
│  │ • Context: requirements.md, user-stories.yaml          │   │
│  │ • Constraints: 10 min timeout, 50k tokens              │   │
│  │                                                         │   │
│  │ Executes:                                               │   │
│  │ • Analyzes requirements                                 │   │
│  │ • Designs system components                             │   │
│  │ • Creates architecture diagrams                         │   │
│  │ • Documents decisions                                   │   │
│  │                                                         │   │
│  │ Returns via attempt_completion:                         │   │
│  │ • design.md                                             │   │
│  │ • architecture diagrams                                 │   │
│  │ • decisions.md                                          │   │
│  └────────────────────────────────────────────────────────┘   │
│              │                                                 │
│              │ RETURN (structured result)                      │
│              ▼                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ MAIN AGENT                                              │   │
│  │ 4. Integrates architecture into context                 │   │
│  │ 5. Continues with next subtask or responds to user      │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Agent Definitions

### SAIL Phase Agents

#### 📋 Scope Agent

**Purpose**: Product requirements and user story creation

```typescript
interface ScopeAgent {
  name: 'scope';
  phase: 'S';

  capabilities: [
    'requirements_gathering',
    'user_story_creation',
    'acceptance_criteria',
    'tdd_anchor_generation',
    'success_metrics'
  ];

  inputs: {
    businessContext: string;
    userResearch?: string;
    previousLearnings?: string;
  };

  outputs: {
    requirements: 'requirements.md';
    stories: 'user-stories.yaml';
    criteria: 'acceptance-criteria.md';
  };
}
```

#### 📐 Architect Agent

**Purpose**: System design and technical planning

```typescript
interface ArchitectAgent {
  name: 'architect';
  phase: 'A';

  capabilities: [
    'system_design',
    'data_modeling',
    'api_design',
    'diagram_creation',
    'decision_documentation'
  ];

  inputs: {
    requirements: 'requirements.md';
    stories: 'user-stories.yaml';
    existingArchitecture?: string[];
  };

  outputs: {
    design: 'design.md';
    diagrams: 'architecture/';
    decisions: 'decisions.md';
  };
}
```

#### ⚡ Coder Agent

**Purpose**: TDD implementation

```typescript
interface CoderAgent {
  name: 'coder';
  phase: 'I';

  capabilities: [
    'tdd_implementation',
    'code_generation',
    'refactoring',
    'test_writing'
  ];

  inputs: {
    design: 'design.md';
    tddAnchors: TDDAnchor[];
    existingCode?: string[];
  };

  outputs: {
    code: FileChange[];
    tests: FileChange[];
  };
}
```

#### 📊 Learn Agent

**Purpose**: Deployment and learning documentation

```typescript
interface LearnAgent {
  name: 'learn';
  phase: 'L';

  capabilities: [
    'deployment_planning',
    'monitoring_setup',
    'metrics_analysis',
    'learnings_documentation'
  ];

  inputs: {
    successMetrics: string;
    deploymentConfig: string;
    productionData?: string;
  };

  outputs: {
    deployment: 'deployment.md';
    monitoring: 'monitoring.md';
    learnings: 'learnings.md';
  };
}
```

### Review Agents

#### 🛡️ Security Agent

**Purpose**: Security review and vulnerability detection

```typescript
interface SecurityAgent {
  name: 'security';

  capabilities: [
    'owasp_review',
    'injection_detection',
    'auth_review',
    'secrets_detection',
    'dependency_audit'
  ];

  inputs: {
    code: FileChange[];
    apiContracts?: string;
  };

  outputs: {
    report: 'security-report.md';
    vulnerabilities: Vulnerability[];
    recommendations: string[];
  };
}
```

#### 🧪 Tester Agent

**Purpose**: Test generation and coverage analysis

```typescript
interface TesterAgent {
  name: 'tester';

  capabilities: [
    'unit_test_generation',
    'integration_test_generation',
    'coverage_analysis',
    'edge_case_identification'
  ];

  inputs: {
    code: FileChange[];
    tddAnchors: TDDAnchor[];
    acceptanceCriteria: string[];
  };

  outputs: {
    tests: FileChange[];
    coverage: 'coverage-report.md';
  };
}
```

#### 🔬 Reviewer Agent

**Purpose**: Code review and quality analysis

```typescript
interface ReviewerAgent {
  name: 'reviewer';

  capabilities: [
    'code_review',
    'style_checking',
    'complexity_analysis',
    'best_practice_validation'
  ];

  inputs: {
    code: FileChange[];
    styleguide?: string;
  };

  outputs: {
    review: CodeReview;
    suggestions: Suggestion[];
  };
}
```

#### 🧹 Optimizer Agent

**Purpose**: Performance optimization

```typescript
interface OptimizerAgent {
  name: 'optimizer';

  capabilities: [
    'performance_profiling',
    'bundle_analysis',
    'query_optimization',
    'memory_analysis'
  ];

  inputs: {
    code: FileChange[];
    profileData?: string;
  };

  outputs: {
    recommendations: Optimization[];
    before_after: PerformanceMetrics;
  };
}
```

### Utility Agents

#### 🔍 Explorer Agent

**Purpose**: Codebase exploration and understanding

```typescript
interface ExplorerAgent {
  name: 'explorer';

  capabilities: [
    'codebase_search',
    'pattern_identification',
    'dependency_mapping',
    'architecture_inference'
  ];

  inputs: {
    query: string;
    scope?: string[];
  };

  outputs: {
    findings: Finding[];
    relevantFiles: string[];
  };
}
```

#### 📚 Docs Agent

**Purpose**: Documentation generation

```typescript
interface DocsAgent {
  name: 'docs';

  capabilities: [
    'api_documentation',
    'readme_generation',
    'changelog_creation',
    'inline_comments'
  ];

  inputs: {
    code: FileChange[];
    existingDocs?: string[];
  };

  outputs: {
    docs: FileChange[];
  };
}
```

#### 🚀 Deploy Agent

**Purpose**: Deployment execution

```typescript
interface DeployAgent {
  name: 'deploy';

  capabilities: [
    'deployment_execution',
    'rollback_planning',
    'environment_validation',
    'health_checking'
  ];

  inputs: {
    deploymentPlan: string;
    environment: string;
  };

  outputs: {
    result: DeploymentResult;
    logs: string;
  };
}
```

#### 📈 Monitor Agent

**Purpose**: Production monitoring and alerting

```typescript
interface MonitorAgent {
  name: 'monitor';

  capabilities: [
    'metrics_collection',
    'alert_configuration',
    'anomaly_detection',
    'dashboard_creation'
  ];

  inputs: {
    successMetrics: string;
    endpoints: string[];
  };

  outputs: {
    monitoring: 'monitoring.md';
    dashboards: Dashboard[];
  };
}
```

---

## Multi-Provider Support

### Provider Configuration

```typescript
interface LLMProvider {
  name: 'claude' | 'openai' | 'gemini' | 'local';
  apiKey?: string;
  baseUrl?: string;
  models: ModelConfig[];
}

interface ModelConfig {
  id: string;                    // e.g., "claude-3-opus"
  alias?: string;                // e.g., "opus"
  supportsReasoning: boolean;
  reasoningEffort?: 'low' | 'medium' | 'high' | 'xhigh';
  verbosity?: 'minimal' | 'normal' | 'detailed';
  purpose?: 'coding' | 'planning' | 'review' | 'all';
}
```

### Agent-Provider Mapping

Different agents can use different providers:

```yaml
# .ldf/settings.yaml
agents:
  orchestrator:
    provider: claude
    model: claude-3-opus
    reasoning: high

  scope:
    provider: claude
    model: claude-3-sonnet
    reasoning: medium

  coder:
    provider: openai
    model: gpt-4-turbo
    reasoning: high

  security:
    provider: claude
    model: claude-3-opus
    reasoning: xhigh  # Maximum reasoning for security
```

### Reasoning Levels

Inspired by [Codex CLI](https://github.com/openai/codex/blob/main/docs/config.md):

| Level | Token Budget | Use Case |
|-------|--------------|----------|
| `low` | Minimal | Quick lookups, simple tasks |
| `medium` | Moderate | Standard development work |
| `high` | Extended | Complex architecture, debugging |
| `xhigh` | Maximum | Security review, critical decisions |

---

## Context Management

### Context Isolation

Each sub-agent receives isolated context:

```typescript
function createSubAgentContext(
  mainContext: ConversationContext,
  task: SubTask
): SubAgentContext {
  return {
    // Only task-relevant context
    task: task.description,
    relevantFiles: extractRelevantFiles(mainContext, task),
    relevantCode: extractRelevantCode(mainContext, task),

    // Constraints
    maxTokens: task.tokenBudget,
    timeoutMs: task.timeout,

    // No delegation allowed
    canDelegate: false
  };
}
```

### Context Preservation

Main agent preserves full context across delegations:

```typescript
class OrchestratorAgent {
  private context: ConversationContext;

  async delegate(task: SubTask): Promise<SubAgentResult> {
    // Create isolated context
    const subContext = createSubAgentContext(this.context, task);

    // Execute sub-agent
    const result = await this.executeSubAgent(task.agent, subContext);

    // Integrate result into main context
    this.integrate(result);

    return result;
  }

  private integrate(result: SubAgentResult): void {
    // Add summary to conversation history
    this.context.addMessage({
      role: 'assistant',
      content: `[${result.agentName}] ${result.summary}`
    });

    // Track artifacts
    for (const artifact of result.artifacts) {
      this.context.trackArtifact(artifact);
    }
  }
}
```

---

## Error Handling

### Sub-Agent Failures

```typescript
interface SubAgentError {
  agent: string;
  task: string;
  error: {
    type: 'timeout' | 'token_limit' | 'provider_error' | 'task_error';
    message: string;
    recoverable: boolean;
  };
  partialResult?: Partial<SubAgentResult>;
}
```

### Recovery Strategies

```typescript
async function handleSubAgentError(
  error: SubAgentError
): Promise<RecoveryAction> {
  switch (error.error.type) {
    case 'timeout':
      // Retry with extended timeout
      return { action: 'retry', timeout: error.timeout * 2 };

    case 'token_limit':
      // Break into smaller subtasks
      return { action: 'split', subtasks: breakdownTask(error.task) };

    case 'provider_error':
      // Try alternate provider
      return { action: 'fallback', provider: getAlternateProvider() };

    case 'task_error':
      // Surface to user for clarification
      return { action: 'escalate', message: error.error.message };
  }
}
```

---

## Implementation Notes

### Technology Choices

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Agent Runtime | TypeScript | Type safety, async/await |
| Message Passing | JSON-RPC | Standard, debuggable |
| Context Storage | In-memory | Speed, simplicity |
| Provider Clients | Official SDKs | Reliability |

### Performance Considerations

1. **Parallel Delegation**: Independent sub-tasks can run in parallel
2. **Streaming Results**: Sub-agents stream results back as they work
3. **Context Caching**: Frequently-used context is cached
4. **Token Budgeting**: Strict limits prevent runaway costs

### Security Considerations

1. **API Key Isolation**: Each provider has separate key management
2. **Context Sanitization**: Secrets removed before delegation
3. **Sandboxed Execution**: Sub-agents run in sandboxed environment
4. **Audit Logging**: All delegations logged for review

---

## CLI Integration

```bash
# View agent status
ldf agents status

# Configure agent providers
ldf agents config coder --provider openai --model gpt-4

# Run specific agent manually
ldf agents run security --input ./src

# View agent logs
ldf agents logs --agent coder --last 10
```

---

## Related Documents

- [LDF Evolution Overview](./ldf-evolution-overview.md)
- [SAIL Methodology](./sail-methodology.md)
- [Ink + React CLI Migration](./ink-react-cli-migration-v2.md)
