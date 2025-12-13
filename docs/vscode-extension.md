# VS Code Extension Guide

The LDF VS Code extension provides visual tools for managing specs, tracking guardrail coverage, and monitoring task progress.

## Installation

### From VSIX (Private)

```bash
# Build the extension
cd vscode-extension
npm install
npm run package

# Install in VS Code
code --install-extension ldf-0.1.0.vsix
```

### From Marketplace (Coming Soon)

```bash
# When published
code --install-extension ldf.ldf-extension
```

## Features

### 1. Spec Tree View

The Spec Tree View appears in the Explorer sidebar and shows all specs in your project.

**Status Icons:**
- `○` Not Started - No requirements yet
- `◐` Requirements Draft - Requirements in progress
- `◑` Design Draft - Design in progress
- `◕` Tasks Draft - Tasks in progress
- `●` Ready - Ready for implementation
- `✓` Complete - All tasks done

**Actions:**
- Click a spec to open its files
- Right-click for context menu (lint, create spec, etc.)

### 2. Guardrail Coverage Panel

Shows a matrix of guardrail coverage for the selected spec.

| Guardrail | Req | Design | Tasks | Status |
|-----------|-----|--------|-------|--------|
| 1. Testing | ✓ | ✓ | ✓ | Ready |
| 2. Security | ✓ | ✓ | - | Pending |
| 3. Error Handling | ✓ | - | - | Draft |

**Colors:**
- Green: Complete
- Yellow: In Progress
- Red: Missing
- Gray: N/A

### 3. Task Progress View

Tracks task completion for the active spec.

```
Phase 1: Setup
  ✓ 1.1 Create project structure
  ✓ 1.2 Configure database
  ○ 1.3 Set up authentication

Phase 2: Core Logic
  ○ 2.1 Implement service
  ○ 2.2 Add validation
```

**Click a task to:**
- Open the task in tasks.md
- Run `/project:implement-task` command

### 4. Command Palette

Access LDF commands from the command palette (`Cmd/Ctrl + Shift + P`):

| Command | Description |
|---------|-------------|
| `LDF: Create Spec` | Create a new spec |
| `LDF: Lint Spec` | Lint the current spec |
| `LDF: Lint All Specs` | Lint all specs in project |
| `LDF: Run Audit` | Generate audit request |
| `LDF: Open Spec` | Quick-open a spec by name |
| `LDF: Refresh Views` | Refresh all LDF views |

### 5. Inline Diagnostics

LDF highlights issues directly in spec files:

**Errors (red squiggle):**
- Missing required sections
- Empty guardrail matrix
- Tasks without checklists

**Warnings (yellow squiggle):**
- Missing optional sections
- Unfilled template markers
- Incomplete answerpacks

### 6. Snippets

Quick-insert spec templates with snippets:

| Prefix | Description |
|--------|-------------|
| `ldf-story` | User story template |
| `ldf-ac` | Acceptance criteria |
| `ldf-matrix` | Guardrail coverage matrix |
| `ldf-task` | Task with checklist |
| `ldf-api` | API endpoint definition |
| `ldf-component` | Component design section |
| `ldf-schema` | Database schema section |
| `ldf-test` | Test plan section |
| `ldf-phase` | Task phase header |
| `ldf-checklist` | Guardrail checklist |
| `ldf-requirements` | Full requirements template |

**Usage:**
Type the prefix and press `Tab` to expand.

## Configuration

### Extension Settings

Access via `Settings > Extensions > LDF`:

```json
{
  "ldf.specsDirectory": ".ldf/specs",
  "ldf.showStatusBarItem": true,
  "ldf.autoRefresh": true,
  "ldf.refreshInterval": 5000,
  "ldf.lintOnSave": true,
  "ldf.showInlineHints": true
}
```

| Setting | Default | Description |
|---------|---------|-------------|
| `specsDirectory` | `.ldf/specs` | Location of specs |
| `showStatusBarItem` | `true` | Show spec count in status bar |
| `autoRefresh` | `true` | Auto-refresh views on file changes |
| `refreshInterval` | `5000` | Refresh interval (ms) |
| `lintOnSave` | `true` | Run lint when saving spec files |
| `showInlineHints` | `true` | Show inline hints in specs |

### Keybindings

Default keybindings (customizable in Keyboard Shortcuts):

| Key | Command |
|-----|---------|
| `Cmd+Shift+W L` | Lint current spec |
| `Cmd+Shift+W A` | Lint all specs |
| `Cmd+Shift+W N` | Create new spec |
| `Cmd+Shift+W O` | Open spec picker |

## Workspace Setup

### Recommended Extensions

LDF works best with these extensions:

- **Markdown All in One** - Better markdown editing
- **YAML** - YAML syntax highlighting
- **AI Assistants** - MCP-compatible tool integration

### Settings.json

Recommended workspace settings:

```json
{
  "files.associations": {
    "*.md": "markdown"
  },
  "editor.wordWrap": "on",
  "[markdown]": {
    "editor.formatOnSave": false,
    "editor.quickSuggestions": {
      "other": true,
      "comments": false,
      "strings": false
    }
  }
}
```

## Troubleshooting

### Views Not Showing

1. Check that `.ldf/specs/` exists
2. Try `LDF: Refresh Views` command
3. Reload VS Code window

### Lint Not Working

1. Ensure `ldf` is installed: `pip install ldf`
2. Check that `ldf lint` works in terminal
3. Check Output panel for errors

### Snippets Not Appearing

1. Ensure you're in a `.md` file
2. Check that snippets are enabled for markdown
3. Type prefix and wait for suggestions

### Performance Issues

1. Reduce `refreshInterval` to `10000` or higher
2. Disable `autoRefresh` if not needed
3. Close unused spec files

## Development

### Building from Source

```bash
cd vscode-extension
npm install
npm run compile

# Run in development
npm run watch
# Press F5 to launch Extension Development Host
```

### Project Structure

```
vscode-extension/
├── package.json          # Extension manifest
├── tsconfig.json         # TypeScript config
├── src/
│   ├── extension.ts      # Entry point
│   ├── specView.ts       # Spec tree provider
│   ├── guardrailView.ts  # Guardrail panel
│   ├── taskView.ts       # Task progress view
│   └── commands.ts       # Command implementations
├── snippets/
│   └── spec-snippets.json
└── README.md
```

### Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.
