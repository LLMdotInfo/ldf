# VS Code Extension

The LDF VS Code extension has moved to its own repository for easier maintenance and marketplace publishing.

## Installation

### From VS Code Marketplace

```bash
code --install-extension llmdotinfo.ldf-vscode
```

Or search for **"LDF Spec-Driven Development"** in the VS Code Extensions sidebar.

### From Source

See the [ldf-vscode repository](https://github.com/LLMdotInfo/ldf-vscode) for build instructions.

## Documentation

Full documentation is available in the extension repository:

- **[README](https://github.com/LLMdotInfo/ldf-vscode#readme)** - Features, installation, configuration
- **[CHANGELOG](https://github.com/LLMdotInfo/ldf-vscode/blob/main/CHANGELOG.md)** - Version history

## Quick Reference

### Features
- Spec Tree View with status indicators
- Guardrail Coverage Panel
- Task Progress View
- Markdown snippets for spec authoring

### Commands
| Command | Description |
|---------|-------------|
| `LDF: Create New Spec` | Create a new spec |
| `LDF: Lint Spec` | Lint a specific spec |
| `LDF: Lint All Specs` | Lint all specs |
| `LDF: Run Audit` | Run audit on a spec |
| `LDF: Initialize LDF Project` | Set up LDF in workspace |

### Settings
| Setting | Default | Description |
|---------|---------|-------------|
| `ldf.executablePath` | `ldf` | Path to ldf executable |
| `ldf.specsDirectory` | `.ldf/specs` | Specs directory |
| `ldf.guardrailsFile` | `.ldf/guardrails.yaml` | Guardrails config |
| `ldf.autoRefresh` | `true` | Auto-refresh on file changes |

## Multi-Root Workspace Support

The VS Code extension supports multi-root workspaces where multiple LDF projects are open simultaneously. Each workspace folder with a `.ldf/config.yaml` is treated as an independent LDF project.

### Features
- Separate spec tree views per workspace
- Independent guardrail tracking per workspace
- Workspace-aware commands (lint runs in correct project)

### Settings
| Setting | Description |
|---------|-------------|
| `ldf.primaryGuardrailWorkspace` | Apply one workspace's guardrails to all |

Use the `LDF: Select Primary Guardrail Workspace` command to set this interactively.

### CLI Behavior
The LDF CLI operates on the current working directory. When running CLI commands from VS Code's integrated terminal, ensure you're in the correct workspace folder.

## Repository

**GitHub:** [https://github.com/LLMdotInfo/ldf-vscode](https://github.com/LLMdotInfo/ldf-vscode)
