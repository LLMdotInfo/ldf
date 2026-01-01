# Ink + React CLI Migration v2

> **Research Date**: December 2025
> **Branch**: `research/ink-react-cli`
> **Status**: Updated with SAIL & Architecture Decisions
> **Supersedes**: `ink-react-cli-migration.md`

---

## Executive Summary

This document describes the migration plan for LDF CLI from Python (Click + Rich) to TypeScript (Ink + Pastel), incorporating all architecture decisions made during the evolution planning:

| Decision | Choice |
|----------|--------|
| **Core Library** | TypeScript only (ldf-core) |
| **Python Support** | CLI wrapper (shells to TS CLI) |
| **Methodology** | SAIL (Scope → Architect → Implement → Learn) |
| **Agent Architecture** | Boomerang pattern |
| **LLM Providers** | Multi-provider with reasoning levels |

---

## Migration Overview

### Before vs After

| Aspect | Current (Python) | Target (TypeScript) |
|--------|-----------------|---------------------|
| **Runtime** | Python 3.10+ | Node.js 18+ / Bun |
| **CLI Framework** | Click | Pastel (file-based routing) |
| **UI Framework** | Rich | Ink (React components) |
| **Validation** | Click types + manual | Zod schemas |
| **Type Safety** | Optional (typing) | Full (TypeScript) |
| **Interactivity** | Questionary + Rich | Ink UI components |
| **Distribution** | pip/pipx | npm (bundled executable) |
| **Core Logic** | Embedded in CLI | Separate ldf-core package |

### Package Structure

```
ldf-ecosystem/
├── ldf-core/                    # Core logic library
│   ├── src/
│   │   ├── guardrails/
│   │   ├── specs/
│   │   ├── projects/
│   │   ├── config/
│   │   ├── lint/
│   │   └── security/
│   ├── _framework/             # Embedded assets
│   └── package.json
│
├── ldf-cli/                     # Primary CLI
│   ├── src/
│   │   ├── commands/           # Pastel file-based routing
│   │   ├── components/         # Ink React components
│   │   ├── agents/             # Agent system
│   │   ├── providers/          # LLM providers
│   │   ├── permissions/        # Permission system
│   │   ├── settings/           # Settings hierarchy
│   │   └── onboarding/         # Onboarding flows
│   └── package.json
│
└── ldf-cli-python/              # Python wrapper
    └── (thin wrapper, shells to ldf-cli)
```

---

## Phase 1: Core Extraction (ldf-core)

### Modules to Extract

From current Python implementation, extract these pure logic modules:

| Python Module | TypeScript Module | Purpose |
|--------------|-------------------|---------|
| `utils/guardrail_loader.py` | `guardrails/` | Load and manage guardrails |
| `utils/spec_parser.py` | `specs/` | Parse markdown specs |
| `utils/security.py` | `security/` | Path validation, sanitization |
| `utils/config.py` | `config/` | Configuration management |
| `detection.py` | `projects/detection.ts` | Project state detection |
| `project_resolver.py` | `projects/resolver.ts` | Context resolution |
| `lint.py` | `lint/` | Spec validation engine |
| `models/workspace.py` | `models/` | Data models |

### ldf-core API Design

```typescript
// ldf-core/src/index.ts

// Guardrails
export { loadCoreGuardrails, loadPresetGuardrails, Guardrail } from './guardrails';

// Specs
export { parseSpec, extractTasks, SpecStatus, TaskItem } from './specs';

// Projects
export { detectProjectState, resolveContext, ProjectState } from './projects';

// Linting
export { lintSpec, lintProject, LintResult, LintReport } from './lint';

// Config
export { loadConfig, ConfigFile, mergeConfigs } from './config';

// Security
export { validatePath, validateSpecName, isPathSafe } from './security';

// SAIL
export { SAILPhase, SAILArtifacts, validatePhase } from './sail';
```

### Framework Assets

Embed framework assets in the package:

```typescript
// ldf-core/src/framework.ts
import coreGuardrails from './_framework/guardrails/core.yaml';
import presetEnterpriseSecure from './_framework/presets/enterprise-secure.yaml';
import templateRequirements from './_framework/templates/requirements.md';

export const framework = {
  guardrails: { core: coreGuardrails },
  presets: { enterpriseSecure: presetEnterpriseSecure },
  templates: { requirements: templateRequirements }
};
```

---

## Phase 2: CLI Foundation (ldf-cli)

### Pastel File-Based Routing

```
ldf-cli/src/commands/
├── index.tsx                    # ldf (status/help)
├── init.tsx                     # ldf init
├── lint.tsx                     # ldf lint
├── status.tsx                   # ldf status
├── doctor.tsx                   # ldf doctor
├── sail/
│   ├── index.tsx               # ldf sail
│   ├── scope.tsx               # ldf sail scope
│   ├── architect.tsx           # ldf sail architect
│   ├── implement.tsx           # ldf sail implement
│   └── learn.tsx               # ldf sail learn
├── agents/
│   ├── index.tsx               # ldf agents
│   ├── status.tsx              # ldf agents status
│   ├── config.tsx              # ldf agents config
│   └── run.tsx                 # ldf agents run
├── workspace/
│   ├── index.tsx               # ldf workspace
│   ├── init.tsx                # ldf workspace init
│   ├── add.tsx                 # ldf workspace add
│   └── list.tsx                # ldf workspace list
└── config/
    ├── index.tsx               # ldf config
    ├── provider.tsx            # ldf config provider
    └── model.tsx               # ldf config model
```

### Ink Component Library

```tsx
// ldf-cli/src/components/

// Status displays
export { StatusBadge } from './StatusBadge';
export { ProgressBar } from './ProgressBar';
export { Spinner } from './Spinner';

// Tables and lists
export { SpecTable } from './SpecTable';
export { TaskList } from './TaskList';
export { GuardrailMatrix } from './GuardrailMatrix';

// Interactive
export { Confirm } from './Confirm';
export { Select } from './Select';
export { TextInput } from './TextInput';

// Layout
export { Panel } from './Panel';
export { Divider } from './Divider';
export { Header } from './Header';

// SAIL-specific
export { PhaseIndicator } from './sail/PhaseIndicator';
export { ArtifactChecklist } from './sail/ArtifactChecklist';
```

### Example Command

```tsx
// ldf-cli/src/commands/status.tsx
import React from 'react';
import { Box, Text } from 'ink';
import { z } from 'zod';
import { detectProjectState, resolveContext } from 'ldf-core';
import { StatusBadge, SpecTable, PhaseIndicator } from '../components';

export const args = z.object({
  verbose: z.boolean().default(false).describe('Show detailed output'),
});

export default function Status({ options }: { options: z.infer<typeof args> }) {
  const projectState = detectProjectState();
  const context = resolveContext();

  return (
    <Box flexDirection="column" gap={1}>
      <Box>
        <Text bold>Project: </Text>
        <Text>{context.projectName}</Text>
        <StatusBadge status={projectState.status} />
      </Box>

      <PhaseIndicator currentPhase={context.currentSAILPhase} />

      {options.verbose && (
        <SpecTable specs={context.specs} />
      )}
    </Box>
  );
}
```

---

## Phase 3: Permission System

### 3-State Permissions

```typescript
// ldf-cli/src/permissions/types.ts
type PermissionDecision = 'allow' | 'deny' | 'allow_always';

interface PermissionRequest {
  action: string;           // e.g., 'file.write', 'shell.execute'
  target: string;           // e.g., '/path/to/file', 'rm -rf'
  context: {
    command: string;
    workingDir: string;
  };
}

interface PermissionConfig {
  enterprise?: EnterprisePermissions;
  system?: SystemPermissions;
  workspace?: WorkspacePermissions;
  project?: ProjectPermissions;
}
```

### Permission Hierarchy

```
Precedence (High to Low):
1. Enterprise (synced from company repo)
2. System (~/.ldf/permissions.yaml)
3. Workspace (ldf-workspace.yaml)
4. Project (.ldf/permissions.yaml)
```

### Static Analysis Integration

```typescript
// ldf-cli/src/permissions/analyzer.ts
interface StaticAnalysisResult {
  command: string;
  risk: 'low' | 'medium' | 'high' | 'critical';
  reasons: string[];
  suggestedAction: PermissionDecision;
}

function analyzeCommand(command: string): StaticAnalysisResult {
  const risks: string[] = [];

  // Destructive patterns
  if (/rm\s+-rf/.test(command)) risks.push('Recursive delete');
  if (/>\s*\//.test(command)) risks.push('Write to root');

  // Network access
  if (/curl|wget|fetch/.test(command)) risks.push('Network access');

  // Elevated permissions
  if (/sudo/.test(command)) risks.push('Elevated permissions');

  return {
    command,
    risk: calculateRisk(risks),
    reasons: risks,
    suggestedAction: risks.length > 0 ? 'deny' : 'allow'
  };
}
```

---

## Phase 4: Settings Hierarchy

### Settings Schema

```typescript
// ldf-cli/src/settings/schema.ts
import { z } from 'zod';

export const SettingsSchema = z.object({
  // LLM Configuration
  provider: z.enum(['claude', 'openai', 'gemini', 'local']).default('claude'),
  model: z.string().default('claude-3-sonnet'),
  reasoning: z.enum(['low', 'medium', 'high', 'xhigh']).default('medium'),

  // Output
  outputStyle: z.enum(['expert', 'explanatory', 'learning']).default('explanatory'),
  colorScheme: z.enum(['auto', 'light', 'dark']).default('auto'),

  // Agent Configuration
  agents: z.record(z.object({
    provider: z.string().optional(),
    model: z.string().optional(),
    reasoning: z.enum(['low', 'medium', 'high', 'xhigh']).optional(),
  })).optional(),

  // SAIL
  sail: z.object({
    autoAdvance: z.boolean().default(false),
    requiredArtifacts: z.record(z.array(z.string())).optional(),
  }).optional(),

  // Permissions
  permissions: PermissionConfigSchema.optional(),
});
```

### Settings Loading

```typescript
// ldf-cli/src/settings/loader.ts
async function loadSettings(): Promise<Settings> {
  const layers = [
    await loadEnterpriseSettings(),
    await loadSystemSettings(),
    await loadWorkspaceSettings(),
    await loadProjectSettings(),
    await loadLocalOverride(),
  ];

  return mergeSettings(layers);
}
```

---

## Phase 5: SAIL Integration

### SAIL Commands

```bash
# Phase management
ldf sail status                   # Show current phase
ldf sail scope start             # Begin Scope phase
ldf sail scope validate          # Validate Scope artifacts
ldf sail scope complete          # Complete with validation

ldf sail architect start         # Begin Architect phase
ldf sail architect validate      # Validate design artifacts
ldf sail architect complete      # Complete with validation

ldf sail implement start         # Begin Implement phase
ldf sail implement tdd-check     # Check TDD coverage
ldf sail implement complete      # Complete with validation

ldf sail learn deploy            # Deploy and begin Learn
ldf sail learn document          # Generate learnings template
ldf sail learn complete          # Complete iteration

# Quick commands
ldf sail next                    # Advance to next phase
ldf sail artifacts               # List required artifacts
ldf sail validate                # Validate current phase
```

### Phase Validation

```typescript
// ldf-cli/src/sail/validation.ts
interface PhaseValidation {
  phase: SAILPhase;
  artifacts: {
    required: ArtifactCheck[];
    optional: ArtifactCheck[];
  };
  checks: ValidationCheck[];
}

const phaseValidations: Record<SAILPhase, PhaseValidation> = {
  scope: {
    phase: 'scope',
    artifacts: {
      required: [
        { path: 'requirements.md', validator: validateRequirements },
        { path: 'user-stories.yaml', validator: validateUserStories },
      ],
      optional: [
        { path: 'acceptance-criteria.md' },
        { path: 'success-metrics.md' },
      ],
    },
    checks: [
      { name: 'TDD anchors present', check: checkTDDAnchors },
      { name: 'Acceptance criteria linked', check: checkACLinks },
    ],
  },
  // ... other phases
};
```

---

## Phase 6: Agent System

### Agent Runtime

```typescript
// ldf-cli/src/agents/runtime.ts
class AgentRuntime {
  private orchestrator: OrchestratorAgent;
  private subAgents: Map<string, SubAgent>;
  private providers: Map<string, LLMProvider>;

  async delegate(task: SubTask): Promise<SubAgentResult> {
    const agent = this.subAgents.get(task.agentType);
    const provider = this.getProviderForAgent(task.agentType);

    const context = this.createIsolatedContext(task);
    const result = await agent.execute(context, provider);

    return result;
  }

  private createIsolatedContext(task: SubTask): SubAgentContext {
    return {
      task: task.description,
      relevantFiles: this.extractRelevantFiles(task),
      relevantCode: this.extractRelevantCode(task),
      maxTokens: task.tokenBudget,
      timeoutMs: task.timeout,
      canDelegate: false,
    };
  }
}
```

### Provider Abstraction

```typescript
// ldf-cli/src/providers/index.ts
interface LLMProvider {
  name: string;
  chat(messages: Message[], options: ChatOptions): AsyncGenerator<string>;
  complete(prompt: string, options: CompletionOptions): Promise<string>;
}

// Provider implementations
export { ClaudeProvider } from './claude';
export { OpenAIProvider } from './openai';
export { GeminiProvider } from './gemini';
export { LocalProvider } from './local';
```

---

## Phase 7: Onboarding

### Onboarding Paths

```typescript
// ldf-cli/src/onboarding/paths.ts
const onboardingPaths = {
  newDev: {
    name: 'New Developer',
    steps: [
      'devDirectorySetup',
      'toolingScan',
      'toolingInstall',
      'workspaceRecommendation',
      'virtualizationGuidance',
      'backupBestPractices',
    ],
  },
  experienced: {
    name: 'Experienced Developer',
    steps: [
      'devDirectoryConfirm',
      'quickToolingCheck',
      'workspaceSelection',
      'environmentDecision',
      'projectSetup',
    ],
  },
  expert: {
    name: 'Expert Mode',
    steps: [
      'companyStructure',
      'enterpriseProfile',
      'advancedWorkspace',
      'multiProjectSetup',
    ],
  },
};
```

### Onboarding Components

```tsx
// ldf-cli/src/onboarding/components/WelcomeScreen.tsx
import React from 'react';
import { Box, Text } from 'ink';
import { Select } from '../components';

export function WelcomeScreen({ onSelect }: { onSelect: (path: string) => void }) {
  return (
    <Box flexDirection="column" gap={1}>
      <Text bold>Welcome to LDF</Text>
      <Text dimColor>Let's get you set up. How would you describe yourself?</Text>

      <Select
        options={[
          { value: 'newDev', label: 'New to development' },
          { value: 'experienced', label: 'Experienced developer' },
          { value: 'expert', label: 'Expert (skip guidance)' },
        ]}
        onSelect={onSelect}
      />
    </Box>
  );
}
```

---

## Phase 8: Python Wrapper

### Thin Wrapper Design

```python
# ldf-cli-python/ldf_cli/__main__.py
import subprocess
import sys
import os

def get_bundled_cli_path():
    """Get path to bundled Node.js CLI."""
    package_dir = os.path.dirname(__file__)
    return os.path.join(package_dir, 'bin', 'ldf')

def main():
    cli_path = get_bundled_cli_path()
    result = subprocess.run(
        [cli_path] + sys.argv[1:],
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    sys.exit(result.returncode)

if __name__ == '__main__':
    main()
```

### Bundling Strategy

```toml
# ldf-cli-python/pyproject.toml
[project]
name = "ldf-cli"
version = "2.0.0"
description = "LDF CLI (Python wrapper)"

[tool.hatch.build]
include = [
    "ldf_cli/**",
    "ldf_cli/bin/ldf",  # Bundled Node.js executable
]
```

---

## Migration Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **1. Core Extraction** | 2-3 weeks | ldf-core npm package |
| **2. CLI Foundation** | 3-4 weeks | Basic ldf-cli with status, lint, init |
| **3. Permission System** | 1-2 weeks | 3-state permissions |
| **4. Settings Hierarchy** | 1 week | Settings loading and merging |
| **5. SAIL Integration** | 2-3 weeks | SAIL commands and validation |
| **6. Agent System** | 2-3 weeks | Boomerang agent runtime |
| **7. Onboarding** | 1-2 weeks | Three onboarding paths |
| **8. Python Wrapper** | 1 week | ldf-cli-python package |

**Total: 14-19 weeks**

---

## Backward Compatibility

### Python CLI Deprecation

```
Timeline:
- v1.x: Current Python CLI (maintained)
- v2.0: TypeScript CLI released, Python wrapper available
- v2.1: Python CLI marked deprecated
- v3.0: Python CLI removed (Python wrapper only)
```

### Migration Guide

Users migrate via:
1. Uninstall `ldf` Python package
2. Install `ldf` npm package
3. OR install `ldf-cli` Python package (wrapper)

Configuration files remain compatible:
- `.ldf/` directory structure unchanged
- `ldf.yaml` / `ldf-workspace.yaml` compatible
- Spec markdown format unchanged

---

## Related Documents

- [LDF Evolution Overview](./ldf-evolution-overview.md)
- [SAIL Methodology](./sail-methodology.md)
- [Agent Architecture](./agent-architecture.md)
- [Original CLI Migration Research](./ink-react-cli-migration.md)
