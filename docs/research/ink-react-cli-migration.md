# Ink + React CLI Migration Research

> **Research Date**: December 2025
> **Branch**: `research/ink-react-cli`
> **Status**: Initial Investigation
> **Repository**: `ldf` (main CLI)

---

## Executive Summary

This document explores migrating the LDF CLI from its current **Python-based implementation** (Click + Rich) to a **TypeScript-based CLI** using **Ink** (React for terminals) with the **Pastel** framework for command routing.

The `ldf-vscode` extension would also need updates to work with the new CLI, but the core migration work happens here in the main `ldf` repository.

### Key Findings

| Aspect | Current (Python CLI) | Proposed (Ink + Pastel) |
|--------|---------------------|-------------------------|
| **Runtime** | Python 3.10+ | Node.js / Bun |
| **CLI Framework** | Click | Pastel (file-based routing) |
| **UI Framework** | Rich | Ink (React components) |
| **Validation** | Click types + manual | Zod schemas |
| **Type Safety** | Optional (typing module) | Full (TypeScript) |
| **Interactivity** | Questionary + Rich | Ink UI components |
| **Distribution** | pip/pipx | npm (single bundled file) |
| **Lines of Code** | ~2,500 (cli.py) | TBD |

---

## Current LDF CLI Architecture

### Dependencies (from pyproject.toml)

```toml
dependencies = [
    "click>=8.0.0",      # Command routing & argument parsing
    "pyyaml>=6.0",       # Config file handling
    "rich>=13.0.0",      # Terminal formatting (colors, tables, progress)
    "jinja2>=3.0.0",     # Template rendering
    "questionary>=2.0.0", # Interactive prompts
    "packaging>=21.0",   # Version parsing
]
```

### Command Structure

The CLI is organized as a Click group with ~25 commands:

```
ldf
├── init              # Initialize project
├── status            # Show project status
├── update            # Update framework files
├── lint              # Validate specs
├── audit             # Generate/import audit requests
├── coverage          # Check test coverage
├── create-spec       # Create new spec
├── list-specs        # List all specs
├── tasks             # List tasks across specs
├── hooks
│   ├── install       # Install pre-commit hooks
│   ├── uninstall     # Remove hooks
│   └── status        # Show hook status
├── workspace
│   ├── init          # Initialize workspace
│   ├── add           # Add project to workspace
│   └── list          # List projects
├── mcp-config        # Generate MCP config
├── mcp-health        # Check MCP server health
├── doctor            # Diagnose setup issues
├── preflight         # Run all CI checks
├── template
│   ├── export        # Export as template
│   ├── verify        # Verify template
│   └── list          # List templates
├── convert
│   ├── analyze       # Analyze codebase
│   └── import        # Import AI response
├── add-pack          # Add question pack
├── list-packs        # List question packs
├── list-presets      # List guardrail presets
└── export-docs       # Generate documentation
```

### Current Architecture Patterns

1. **Click decorators for command definition**
   ```python
   @main.command()
   @click.option("--all", "-a", "lint_all", is_flag=True)
   @click.option("--format", type=click.Choice(["rich", "ci", "json"]))
   def lint(lint_all, format): ...
   ```

2. **Rich console for output**
   ```python
   from ldf.utils.console import console
   console.print("[green]✓[/green] Success")
   ```

3. **Project context resolution**
   ```python
   @with_project_context
   def mycommand(project_context):
       print(f"Working in {project_context.project_root}")
   ```

4. **Multi-format output** (rich/json/text for CI compatibility)

---

## Technology Stack

### Core Dependencies

```json
{
  "dependencies": {
    "ink": "^5.0.0",
    "react": "^18.0.0",
    "@inkjs/ui": "^2.0.0",
    "pastel": "^3.0.0",
    "zod": "^3.0.0"
  }
}
```

### What Each Library Provides

| Library | Purpose | Key Features |
|---------|---------|--------------|
| **Ink** | React renderer for terminals | Flexbox layouts (Yoga), component model, hooks |
| **@inkjs/ui** | Pre-built UI components | TextInput, Select, Spinner, ProgressBar, Alerts |
| **Pastel** | CLI framework | File-based routing, auto-generated help, Commander.js under the hood |
| **Zod** | Schema validation | Type-safe argument parsing, auto-documentation |

---

## Architecture Deep Dive

### Ink: React for Terminals

Ink provides the same component-based UI building experience as React for browsers, but renders to the terminal. It uses **Yoga** (Facebook's flexbox implementation) for layouts.

#### Core Primitives

```tsx
import { Box, Text, render } from 'ink';

const App = () => (
  <Box flexDirection="column" padding={1}>
    <Text color="green">✓ Success</Text>
    <Box marginTop={1}>
      <Text dimColor>Processing...</Text>
    </Box>
  </Box>
);

render(<App />);
```

#### Available Hooks

- `useInput()` - Keyboard input handling
- `useApp()` - Access to app instance (exit, etc.)
- `useStdin()` - Raw stdin access
- `useStdout()` - Terminal dimensions, write access
- `useFocus()` / `useFocusManager()` - Focus management

### Ink UI Components

Pre-built, themeable components for common CLI patterns:

#### Input Components
- **TextInput** - Single-line input with autocomplete
- **EmailInput** - Email with domain suggestions
- **PasswordInput** - Masked input
- **ConfirmInput** - Y/n prompts

#### Selection Components
- **Select** - Single choice from list
- **MultiSelect** - Multiple choices

#### Feedback Components
- **Spinner** - Animated processing indicator
- **ProgressBar** - Percentage-based progress
- **Badge** - Status indicators (success, error, warning, info)
- **StatusMessage** - Extended status with descriptions
- **Alert** - Attention-grabbing messages

#### List Components
- **OrderedList** - Numbered lists with nesting
- **UnorderedList** - Bulleted lists with custom markers

### Pastel: File-Based Command Routing

Pastel provides Next.js-style file-based routing for CLI commands.

#### Project Structure

```
my-cli/
├── source/
│   ├── cli.ts              # Entry point
│   └── commands/
│       ├── index.tsx       # Default command
│       ├── lint.tsx        # `my-cli lint`
│       ├── audit.tsx       # `my-cli audit`
│       └── workspace/
│           ├── init.tsx    # `my-cli workspace init`
│           └── list.tsx    # `my-cli workspace list`
├── build/
└── package.json
```

#### Command Definition with Zod

```tsx
// commands/lint.tsx
import React from 'react';
import { Text, Box } from 'ink';
import { Spinner } from '@inkjs/ui';
import zod from 'zod';

// Define options with Zod - auto-generates --help
export const options = zod.object({
  all: zod.boolean().default(false).describe('Lint all specs'),
  fix: zod.boolean().default(false).describe('Auto-fix issues'),
  verbose: zod.boolean().default(false).describe('Verbose output'),
});

// Define positional arguments
export const args = zod.tuple([
  zod.string().optional().describe('Spec name to lint'),
]);

type Props = {
  options: zod.infer<typeof options>;
  args: zod.infer<typeof args>;
};

export default function Lint({ options, args }: Props) {
  const [specName] = args;
  const [status, setStatus] = React.useState<'running' | 'done'>('running');

  React.useEffect(() => {
    // Run linting logic...
    runLint(specName, options).then(() => setStatus('done'));
  }, []);

  if (status === 'running') {
    return (
      <Box>
        <Spinner label={`Linting ${specName || 'all specs'}...`} />
      </Box>
    );
  }

  return <Text color="green">✓ Linting complete</Text>;
}
```

#### Entry Point

```typescript
// source/cli.ts
import Pastel from 'pastel';

const app = new Pastel({
  importMeta: import.meta,
  name: 'ldf',
  version: '2.0.0',
  description: 'LLM Development Framework CLI',
});

await app.run();
```

---

## Migration Analysis

### Commands to Migrate (Priority Order)

#### Tier 1: Core Commands (Most Used)
| Command | Current Python | Proposed Ink/Pastel |
|---------|---------------|---------------------|
| `init` | Click + Questionary prompts | `commands/init.tsx` + `<Select>`, `<TextInput>` |
| `lint` | Click + Rich tables | `commands/lint.tsx` + streaming output |
| `status` | Click + Rich formatting | `commands/status.tsx` + `<Badge>`, `<Box>` |
| `create-spec` | Click + file operations | `commands/create-spec.tsx` |

#### Tier 2: Development Workflow
| Command | Current Python | Proposed Ink/Pastel |
|---------|---------------|---------------------|
| `audit` | Click + Rich + file I/O | `commands/audit.tsx` + enum select |
| `coverage` | Click + Rich tables | `commands/coverage.tsx` + `<ProgressBar>` |
| `tasks` | Click + Rich formatting | `commands/tasks.tsx` + grouped display |
| `doctor` | Click + check system | `commands/doctor.tsx` + status badges |
| `preflight` | Click + multi-step | `commands/preflight.tsx` + progress |

#### Tier 3: Advanced Features
| Command | Current Python | Proposed Ink/Pastel |
|---------|---------------|---------------------|
| `hooks/*` | Click group + shell ops | `commands/hooks/*.tsx` |
| `workspace/*` | Click group + YAML | `commands/workspace/*.tsx` |
| `template/*` | Click group + file ops | `commands/template/*.tsx` |
| `convert/*` | Click group + analysis | `commands/convert/*.tsx` |

#### Tier 4: Utilities
| Command | Notes |
|---------|-------|
| `mcp-config`, `mcp-health` | JSON output, straightforward |
| `list-*`, `add-pack` | Table displays |
| `export-docs` | Markdown generation |
| `update` | File sync operations |

### Feature Mapping: Python → TypeScript

| Current (Python) | Library | Proposed (TypeScript) | Library |
|------------------|---------|----------------------|---------|
| `@click.command()` | Click | `export default function` | Pastel |
| `@click.option()` | Click | `export const options = zod.object()` | Zod |
| `@click.argument()` | Click | `export const args = zod.tuple()` | Zod |
| `@click.group()` | Click | Folder structure | Pastel |
| `console.print("[green]✓[/green]")` | Rich | `<Text color="green">✓</Text>` | Ink |
| `Table()` | Rich | Custom component or `<Box>` layout | Ink |
| `with console.status("...")` | Rich | `<Spinner label="..." />` | Ink UI |
| `questionary.select()` | Questionary | `<Select>` | Ink UI |
| `questionary.confirm()` | Questionary | `<ConfirmInput>` | Ink UI |
| `questionary.text()` | Questionary | `<TextInput>` | Ink UI |
| JSON output mode | Built-in | Same pattern (conditional render) | - |

### Migration Strategy

Given the scope (~2,500 lines of CLI code + supporting modules), this is a significant undertaking.

#### Phase 1: Foundation & Proof of Concept (1-2 weeks)

1. **Scaffold Ink + Pastel project**
   ```bash
   npx create-pastel-app ldf-cli --typescript
   cd ldf-cli && npm install @inkjs/ui zod
   ```

2. **Implement 2-3 core commands as PoC**
   - `status.tsx` - Good test of Rich → Ink formatting
   - `lint.tsx` - Tests streaming output + exit codes
   - `list-specs.tsx` - Tests table rendering

3. **Port shared utilities**
   - Project context resolution
   - Config file parsing (YAML)
   - Spec file parsing

4. **Validate approach**
   - Benchmark startup time vs Python
   - Test CI integration (exit codes, JSON output)
   - Verify ldf-vscode compatibility

#### Phase 2: Core Command Migration (2-3 weeks)

1. **Tier 1 commands** (init, lint, status, create-spec)
2. **Tier 2 commands** (audit, coverage, tasks, doctor, preflight)
3. **Port business logic modules**
   - `ldf/lint.py` → TypeScript
   - `ldf/audit.py` → TypeScript
   - `ldf/coverage.py` → TypeScript
   - `ldf/detection.py` → TypeScript

#### Phase 3: Advanced Features (2-3 weeks)

1. **Command groups** (hooks, workspace, template, convert)
2. **Interactive prompts** (init wizard, conflict resolution)
3. **MCP integration** (mcp-config, mcp-health)

#### Phase 4: Polish & Integration (1-2 weeks)

1. **Update ldf-vscode extension**
   - Same `execFileAsync` pattern works
   - Parse structured JSON output from CLI
   - Update executable detection logic

2. **Distribution**
   - npm package setup
   - Update installation docs
   - Migration guide for existing users

3. **Testing**
   - Port test suite
   - CI/CD pipeline updates

#### Total Estimated Timeline: 6-10 weeks

### Hybrid Approach Alternative

If full migration is too risky, consider keeping Python for business logic:

```
┌─────────────────────────────────────────────┐
│           Node.js (Ink + Pastel)            │
│  ┌───────────────────────────────────────┐  │
│  │  CLI Interface Layer                  │  │
│  │  - Command routing (Pastel)           │  │
│  │  - Interactive UI (Ink)               │  │
│  │  - Argument parsing (Zod)             │  │
│  └───────────────────────────────────────┘  │
│                     │                        │
│                     ▼                        │
│  ┌───────────────────────────────────────┐  │
│  │  Python Subprocess Layer              │  │
│  │  - Core linting logic                 │  │
│  │  - Spec parsing                       │  │
│  │  - Audit algorithms                   │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

---

## Competitive Landscape: What Other Coding CLIs Use

The coding CLI agent space has converged on **three main approaches**:

### Approach 1: TypeScript + Ink (React)

| Tool | UI Framework | Runtime | Notes |
|------|-------------|---------|-------|
| **Claude Code** | Ink (React) | Bun | Custom renderer for streaming |
| **Gemini CLI** | Ink (React) | Node.js | Listed on Ink's GitHub |
| **GitHub Copilot CLI** | Ink (React) | Node.js | Listed on Ink's GitHub |
| **Cloudflare Wrangler** | Ink (React) | Node.js | Listed on Ink's GitHub |

### Approach 2: TypeScript + SolidJS

| Tool | UI Framework | Runtime | Notes |
|------|-------------|---------|-------|
| **sst/opencode** | @opentui/solid | Bun | 41k+ GitHub stars, client/server architecture |

OpenCode (sst) uses **SolidJS** instead of React for its TUI rendering via `@opentui/solid`. Key differentiators:
- Client/server architecture (TUI is just one client, can also drive via mobile app)
- Bun workspaces for monorepo management
- Turbo for build orchestration
- Not coupled to any provider (works with Claude, OpenAI, Gemini, local models)

### Approach 3: Go + Bubble Tea

| Tool | UI Framework | Runtime | Notes |
|------|-------------|---------|-------|
| **opencode-ai/opencode** | Bubble Tea | Go | Archived Sept 2025, became "Crush" |
| **Charm tools** | Bubble Tea | Go | Glow, mods, etc. |

Bubble Tea is a Go framework based on **The Elm Architecture**:
- Functional approach: Init, Update, View methods
- **Bubbles** component library (spinners, text input, tables, progress)
- Used by Charm's suite of terminal tools
- The opencode-ai version was archived and development continues as "Crush"

### Landscape Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    Coding CLI Landscape                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TypeScript Ecosystem (dominant)                            │
│  ├── React/Ink: Claude Code, Gemini CLI, Copilot CLI       │
│  └── SolidJS: sst/opencode                                  │
│                                                             │
│  Go Ecosystem                                               │
│  └── Bubble Tea: opencode-ai (archived), Charm tools        │
│                                                             │
│  Python Ecosystem                                           │
│  └── Rich/Textual: No major coding agents using this       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Key Observation**: No major coding CLI agents are using Python for their TUI layer. The industry has converged on TypeScript (Ink/SolidJS) or Go (Bubble Tea).

---

## Lessons from Claude Code

Based on public information about Claude Code's implementation:

### What They Did Right

1. **TypeScript + React**: Chosen because Claude (the model) knows these technologies well, making it easier for Claude to help maintain the codebase

2. **Single bundled file**: ~7.6MB with zero runtime dependencies, simplifies distribution

3. **npm distribution**: Most popular package manager, widest reach

### Challenges They Faced

1. **Custom renderer**: Had to rewrite Ink's renderer for fine-grained incremental updates during streaming

2. **IME issues**: Known problems with CJK input (200-500ms latency) due to Ink's TextInput

3. **Flickering**: Terminal UI flicker is a known issue with Ink-based TUIs

### Implications for LDF

- For simpler use cases, stock Ink should be sufficient
- Streaming LLM responses may require custom rendering work
- Consider IME impact if targeting international users

---

## Proof of Concept

### Minimal Example: Lint Command

```tsx
// commands/lint.tsx
import React, { useState, useEffect } from 'react';
import { Text, Box } from 'ink';
import { Spinner, Alert, Badge } from '@inkjs/ui';
import zod from 'zod';

export const options = zod.object({
  all: zod.boolean().default(false).describe('Lint all specs'),
  project: zod.string().optional().describe('Project alias for workspace mode'),
});

export const args = zod.tuple([
  zod.string().optional().describe('Spec name'),
]);

type LintResult = {
  file: string;
  errors: number;
  warnings: number;
};

export default function Lint({ options, args }: Props) {
  const [specName] = args;
  const [status, setStatus] = useState<'idle' | 'running' | 'done' | 'error'>('idle');
  const [results, setResults] = useState<LintResult[]>([]);

  useEffect(() => {
    setStatus('running');

    // Simulate linting (replace with actual logic)
    const runLint = async () => {
      try {
        const specs = options.all ? await getAllSpecs() : [specName];
        for (const spec of specs) {
          const result = await lintSpec(spec);
          setResults(prev => [...prev, result]);
        }
        setStatus('done');
      } catch (err) {
        setStatus('error');
      }
    };

    runLint();
  }, []);

  if (status === 'running') {
    return (
      <Box flexDirection="column">
        <Spinner label="Linting specs..." />
        {results.map(r => (
          <Text key={r.file}>
            <Badge color={r.errors > 0 ? 'red' : 'green'}>
              {r.errors > 0 ? 'FAIL' : 'PASS'}
            </Badge>
            {' '}{r.file}
          </Text>
        ))}
      </Box>
    );
  }

  if (status === 'error') {
    return <Alert variant="error">Linting failed</Alert>;
  }

  const totalErrors = results.reduce((sum, r) => sum + r.errors, 0);

  return (
    <Box flexDirection="column">
      {results.map(r => (
        <Text key={r.file}>
          <Badge color={r.errors > 0 ? 'red' : 'green'}>
            {r.errors > 0 ? 'FAIL' : 'PASS'}
          </Badge>
          {' '}{r.file}: {r.errors} errors, {r.warnings} warnings
        </Text>
      ))}
      <Box marginTop={1}>
        <Text color={totalErrors > 0 ? 'red' : 'green'}>
          {totalErrors === 0 ? '✓ All specs passed' : `✗ ${totalErrors} errors found`}
        </Text>
      </Box>
    </Box>
  );
}
```

---

## Alternative: SolidJS Approach (What OpenCode Uses)

sst/opencode uses SolidJS instead of React via `@opentui/solid`. This is worth considering:

### Advantages of SolidJS for TUI

1. **Fine-grained reactivity**: No virtual DOM diffing, updates only what changes
2. **Smaller bundle size**: SolidJS is lighter than React
3. **Better performance**: Direct DOM (terminal) manipulation
4. **Similar syntax**: JSX, familiar to React developers

### OpenCode's Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     sst/opencode                            │
├─────────────────────────────────────────────────────────────┤
│  packages/                                                  │
│  ├── opencode/           # Core CLI (HTTP server, agent)   │
│  │   └── src/tui/        # @opentui/solid TUI              │
│  ├── desktop/            # Tauri + SolidJS desktop app     │
│  └── @opencode-ai/sdk    # API types                       │
│                                                             │
│  Build: Bun workspaces + Turbo                             │
│  Distribution: curl install script                          │
└─────────────────────────────────────────────────────────────┘
```

### Key Differentiator: Client/Server Split

OpenCode's architecture separates compute from UI:
- HTTP server runs AI agent orchestration
- TUI connects as a client via SSE (`/global/event`)
- Desktop app is another client (Tauri)
- Mobile app can also connect remotely

This is more sophisticated than Claude Code's approach but adds complexity.

---

## Decision Matrix

| Factor | Weight | Python (Rich/Textual) | Ink + Pastel | SolidJS | Go + Bubble Tea |
|--------|--------|----------------------|--------------|---------|-----------------|
| Development speed | 15% | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★☆☆☆ |
| UI polish | 20% | ★★★★☆ | ★★★★★ | ★★★★★ | ★★★★☆ |
| Distribution ease | 20% | ★★★☆☆ | ★★★★★ | ★★★★★ | ★★★★★ |
| Type safety | 10% | ★★★☆☆ | ★★★★★ | ★★★★★ | ★★★★☆ |
| AI model familiarity | 15% | ★★★☆☆ | ★★★★★ | ★★★★☆ | ★★☆☆☆ |
| Ecosystem maturity | 10% | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★★★☆ |
| Performance | 10% | ★★★☆☆ | ★★★★☆ | ★★★★★ | ★★★★★ |
| **Weighted Score** | | **3.5** | **4.5** | **4.3** | **3.8** |

---

## Recommendations

### If Starting Fresh: **Ink + Pastel**

The ecosystem is mature, well-documented, and used by major tools (Claude Code, Gemini CLI, GitHub Copilot CLI). The React component model enables rapid iteration.

### If Preserving Python Investment: **Hybrid**

Keep Python for business logic, add Ink layer for UI. Best of both worlds but increased complexity.

### Quick Wins Without Full Migration

1. Add `rich` library to existing Python CLI for colors/tables
2. Use `typer` for better argument parsing
3. Keep VS Code extension as primary interface

---

## References

### Ink + React Ecosystem
- [Ink - React for interactive command-line apps](https://github.com/vadimdemedes/ink)
- [Ink UI - Pre-built components](https://github.com/vadimdemedes/ink-ui)
- [Pastel - Next.js-like CLI framework](https://github.com/vadimdemedes/pastel)
- [Building CLIs with Ink and Pastel](https://medium.com/trabe/building-cli-tools-with-react-using-ink-and-pastel-2e5b0d3e2793)
- [Migration to React Ink Experience](https://ivanleo.com/blog/migrating-to-react-ink)
- [LogRocket: Using Ink UI](https://blog.logrocket.com/using-ink-ui-react-build-interactive-custom-clis/)

### SolidJS / OpenCode
- [sst/opencode - The open source coding agent](https://github.com/sst/opencode)
- [OpenCode Documentation](https://opencode.ai/docs/)

### Go + Bubble Tea
- [Bubble Tea - TUI framework for Go](https://github.com/charmbracelet/bubbletea)
- [Bubbles - TUI components](https://github.com/charmbracelet/bubbles)
- [opencode-ai/opencode (archived)](https://github.com/opencode-ai/opencode)

### Industry Analysis
- [How Claude Code is built](https://newsletter.pragmaticengineer.com/p/how-claude-code-is-built)

---

## Next Steps

1. [ ] Create minimal Ink + Pastel PoC with single `lint` command
2. [ ] Benchmark startup time vs current Python CLI
3. [ ] Test streaming output for LLM responses
4. [ ] Evaluate IME behavior (if applicable)
5. [ ] Decide on hybrid vs full migration approach
