# LDF VS Code Extension

Visual tools for spec-driven development with LDF (LLM Development Framework).

## Features

### Spec Tree View
Browse all specs in your project with status indicators:
- **Draft** (orange edit icon): Requirements incomplete
- **In Review** (yellow eye icon): Awaiting approval
- **Approved** (green check icon): Ready for implementation
- **In Progress** (blue sync icon): Implementation started
- **Complete** (green double-check icon): All tasks done

### Guardrail Coverage Panel
Track guardrail coverage across all specs:
- See which guardrails are covered by which specs
- Identify gaps in coverage
- Visual status indicators (covered, partial, not covered)

### Task Progress View
Track implementation progress:
- Shows current in-progress tasks
- Click to jump to task in tasks.md
- Mark tasks complete directly from the view

### Commands

| Command | Description |
|---------|-------------|
| `LDF: Create New Spec` | Create a new spec with templates |
| `LDF: Lint Spec` | Run linter on a specific spec |
| `LDF: Lint All Specs` | Run linter on all specs |
| `LDF: Run Audit` | Run audit on a spec |
| `LDF: Initialize LDF Project` | Set up LDF in current workspace |
| `LDF: Refresh Specs` | Refresh all views |

### Snippets

Type these prefixes in markdown files to insert templates:

| Prefix | Description |
|--------|-------------|
| `ldf-story` | User story with EARS format |
| `ldf-ac` | Acceptance criterion |
| `ldf-matrix` | Guardrail coverage matrix |
| `ldf-task` | Task checkbox |
| `ldf-phase` | Task phase with multiple tasks |
| `ldf-api` | API endpoint documentation |
| `ldf-component` | Design component |
| `ldf-model` | Data model entity |
| `ldf-security` | Security considerations section |
| `ldf-req-template` | Complete requirements template |

## Installation

### From VSIX (Development)

1. Build the extension:
   ```bash
   cd vscode-extension
   npm install
   npm run compile
   npm run package
   ```

2. Install the VSIX:
   - Open VS Code
   - Press `Cmd+Shift+P` (or `Ctrl+Shift+P`)
   - Type "Install from VSIX"
   - Select the generated `.vsix` file

### From Marketplace

1. Open VS Code
2. Go to Extensions (Cmd+Shift+X / Ctrl+Shift+X)
3. Search for "LDF Spec-Driven Development"
4. Click Install

Or install from command line:
```bash
code --install-extension llmdotinfo.ldf-vscode
```

## Configuration

### Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `ldf.specsDirectory` | `.ldf/specs` | Directory containing spec files |
| `ldf.guardrailsFile` | `.ldf/guardrails.yaml` | Path to guardrails configuration |
| `ldf.autoRefresh` | `true` | Auto-refresh when files change |
| `ldf.showInlineWarnings` | `true` | Show inline warnings for spec issues |

### Recommended Workspace Settings

```json
{
  "ldf.specsDirectory": ".ldf/specs",
  "ldf.autoRefresh": true,
  "files.associations": {
    "*.md": "markdown"
  }
}
```

## Requirements

- VS Code 1.85.0 or higher
- LDF CLI installed (`pip install ldf`)
- An LDF-initialized project (`.ldf/` directory)

## Getting Started

1. Install the extension
2. Open a project with LDF initialized
3. Look for the "LDF Specs" icon in the Activity Bar
4. Create your first spec with `LDF: Create New Spec`

## Extension Views

### LDF Specs Panel

Located in the Activity Bar (checklist icon), contains three views:

1. **Specifications** - Tree of all specs with status
2. **Guardrail Coverage** - Coverage matrix visualization
3. **Current Tasks** - In-progress and pending tasks

## Development

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch for changes
npm run watch

# Run linting
npm run lint

# Package for distribution
npm run package
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Related

- [LDF Documentation](../docs/)
- [LDF CLI](../ldf/)
- [MCP Servers](../mcp-servers/)
