/**
 * LDF Extension Commands
 *
 * Registers and implements all extension commands:
 * - Create spec
 * - Lint spec/all specs
 * - Run audit
 * - Open spec files
 * - Mark task complete
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { SpecTreeProvider, SpecTreeItem, SpecInfo } from './specView';
import { GuardrailTreeProvider } from './guardrailView';
import { TaskTreeProvider, TaskTreeItem } from './taskView';

interface CommandContext {
    specProvider: SpecTreeProvider;
    guardrailProvider: GuardrailTreeProvider;
    taskProvider: TaskTreeProvider;
    workspacePath: string;
}

export function registerCommands(
    context: vscode.ExtensionContext,
    ctx: CommandContext
): void {
    const { specProvider, guardrailProvider, taskProvider, workspacePath } = ctx;

    // Refresh specs
    context.subscriptions.push(
        vscode.commands.registerCommand('ldf.refreshSpecs', () => {
            specProvider.refresh();
            guardrailProvider.refresh();
            taskProvider.refresh();
            vscode.window.showInformationMessage('LDF: Specs refreshed');
        })
    );

    // Create new spec
    context.subscriptions.push(
        vscode.commands.registerCommand('ldf.createSpec', async () => {
            const specName = await vscode.window.showInputBox({
                prompt: 'Enter spec name (e.g., user-authentication)',
                placeHolder: 'feature-name',
                validateInput: (value) => {
                    if (!value) return 'Spec name is required';
                    if (!/^[a-z0-9-]+$/.test(value)) {
                        return 'Use lowercase letters, numbers, and hyphens only';
                    }
                    return null;
                },
            });

            if (!specName) return;

            const config = vscode.workspace.getConfiguration('ldf');
            const specsDir = path.join(
                workspacePath,
                config.get('specsDirectory', '.ldf/specs')
            );
            const specPath = path.join(specsDir, specName);

            if (fs.existsSync(specPath)) {
                vscode.window.showErrorMessage(`Spec '${specName}' already exists`);
                return;
            }

            // Create spec directory and requirements.md
            fs.mkdirSync(specPath, { recursive: true });

            const requirementsTemplate = `# ${specName} - Requirements

## Overview

[Brief description of the feature]

## User Stories

### US-1: [Story Title]

**As a** [user type]
**I want to** [action]
**So that** [benefit]

**Acceptance Criteria:**
- [ ] AC-1.1: [Criterion]
- [ ] AC-1.2: [Criterion]

## Question-Pack Answers

### Security
- Authentication: [answer]
- Authorization: [answer]

### Data Model
- Tables: [answer]
- Relationships: [answer]

## Guardrail Coverage Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing Coverage | [US-1] | [TBD] | [TBD] | [TBD] | TODO |
| 2. Security Basics | [US-1] | [TBD] | [TBD] | [TBD] | TODO |
| 3. Error Handling | [US-1] | [TBD] | [TBD] | [TBD] | TODO |
| 4. Logging & Observability | [US-1] | [TBD] | [TBD] | [TBD] | TODO |
| 5. API Design | [US-1] | [TBD] | [TBD] | [TBD] | TODO |
| 6. Data Validation | [US-1] | [TBD] | [TBD] | [TBD] | TODO |
| 7. Database Migrations | [US-1] | [TBD] | [TBD] | [TBD] | TODO |
| 8. Documentation | [US-1] | [TBD] | [TBD] | [TBD] | TODO |

## Dependencies

- [List any dependencies]

## Out of Scope

- [What's explicitly not included]
`;

            fs.writeFileSync(
                path.join(specPath, 'requirements.md'),
                requirementsTemplate
            );

            specProvider.refresh();

            // Open the new requirements file
            const doc = await vscode.workspace.openTextDocument(
                path.join(specPath, 'requirements.md')
            );
            await vscode.window.showTextDocument(doc);

            vscode.window.showInformationMessage(`LDF: Created spec '${specName}'`);
        })
    );

    // Lint single spec
    context.subscriptions.push(
        vscode.commands.registerCommand(
            'ldf.lintSpec',
            async (item?: SpecTreeItem) => {
                let specName: string | undefined;

                if (item?.specInfo) {
                    specName = item.specInfo.name;
                } else {
                    // Prompt for spec name
                    const specs = specProvider.getSpecs();
                    const specNames = specs.map((s) => s.name);
                    specName = await vscode.window.showQuickPick(specNames, {
                        placeHolder: 'Select spec to lint',
                    });
                }

                if (!specName) return;

                await runLint(workspacePath, specName);
            }
        )
    );

    // Lint all specs
    context.subscriptions.push(
        vscode.commands.registerCommand('ldf.lintAllSpecs', async () => {
            await runLint(workspacePath);
        })
    );

    // Open spec (generic)
    context.subscriptions.push(
        vscode.commands.registerCommand(
            'ldf.openSpec',
            async (item?: SpecTreeItem) => {
                if (!item?.specInfo) return;
                // Open the requirements file by default
                await openSpecFile(workspacePath, item.specInfo.name, 'requirements');
            }
        )
    );

    // Open requirements
    context.subscriptions.push(
        vscode.commands.registerCommand(
            'ldf.openRequirements',
            async (item?: SpecTreeItem) => {
                if (!item?.specInfo) return;
                await openSpecFile(workspacePath, item.specInfo.name, 'requirements');
            }
        )
    );

    // Open design
    context.subscriptions.push(
        vscode.commands.registerCommand(
            'ldf.openDesign',
            async (item?: SpecTreeItem) => {
                if (!item?.specInfo) return;
                await openSpecFile(workspacePath, item.specInfo.name, 'design');
            }
        )
    );

    // Open tasks
    context.subscriptions.push(
        vscode.commands.registerCommand(
            'ldf.openTasks',
            async (item?: SpecTreeItem) => {
                if (!item?.specInfo) return;
                await openSpecFile(workspacePath, item.specInfo.name, 'tasks');
            }
        )
    );

    // Run audit
    context.subscriptions.push(
        vscode.commands.registerCommand(
            'ldf.runAudit',
            async (item?: SpecTreeItem) => {
                let specName: string | undefined;

                if (item?.specInfo) {
                    specName = item.specInfo.name;
                } else {
                    const specs = specProvider.getSpecs();
                    const specNames = specs.map((s) => s.name);
                    specName = await vscode.window.showQuickPick(specNames, {
                        placeHolder: 'Select spec to audit',
                    });
                }

                if (!specName) return;

                const auditType = await vscode.window.showQuickPick(
                    [
                        { label: 'Spec Review', value: 'spec-review' },
                        { label: 'Security Check', value: 'security-check' },
                        { label: 'Gap Analysis', value: 'gap-analysis' },
                        { label: 'Edge Cases', value: 'edge-cases' },
                    ],
                    { placeHolder: 'Select audit type' }
                );

                if (!auditType) return;

                await runAudit(workspacePath, specName, auditType.value);
            }
        )
    );

    // Show guardrail details
    context.subscriptions.push(
        vscode.commands.registerCommand(
            'ldf.showGuardrailDetails',
            async (guardrailId?: number) => {
                const coverage = guardrailProvider.getCoverage();
                const guardrail = coverage.find((c) => c.guardrail.id === guardrailId);

                if (!guardrail) {
                    vscode.window.showWarningMessage('Guardrail not found');
                    return;
                }

                const message = [
                    `**${guardrail.guardrail.name}**`,
                    ``,
                    guardrail.guardrail.description,
                    ``,
                    `Severity: ${guardrail.guardrail.severity}`,
                    `Status: ${guardrail.status}`,
                    `Covered by: ${guardrail.coveredBy.join(', ') || 'No specs'}`,
                ].join('\n');

                vscode.window.showInformationMessage(message, { modal: true });
            }
        )
    );

    // Mark task complete
    context.subscriptions.push(
        vscode.commands.registerCommand(
            'ldf.markTaskComplete',
            async (item?: TaskTreeItem) => {
                if (!item?.taskId) return;

                const success = await taskProvider.markTaskComplete(item.taskId);
                if (success) {
                    vscode.window.showInformationMessage(
                        `LDF: Task marked complete`
                    );
                } else {
                    vscode.window.showErrorMessage(
                        `LDF: Failed to mark task complete`
                    );
                }
            }
        )
    );

    // Initialize project
    context.subscriptions.push(
        vscode.commands.registerCommand('ldf.initProject', async () => {
            const config = vscode.workspace.getConfiguration('ldf');
            const specsDir = path.join(
                workspacePath,
                config.get('specsDirectory', '.ldf/specs')
            );

            if (fs.existsSync(specsDir)) {
                const result = await vscode.window.showWarningMessage(
                    'LDF directory already exists. Reinitialize?',
                    'Yes',
                    'No'
                );
                if (result !== 'Yes') return;
            }

            // Create directory structure
            const ldfDir = path.join(workspacePath, '.ldf');
            fs.mkdirSync(specsDir, { recursive: true });
            fs.mkdirSync(path.join(ldfDir, 'answerpacks'), { recursive: true });

            // Create config.yaml with schema matching LDF CLI expectations
            const projectName = path.basename(workspacePath);
            const timestamp = new Date().toISOString();
            const configYaml = `# LDF Configuration
version: "1.0"
framework_version: "0.1.0"
framework_updated: "${timestamp}"

project:
  name: "${projectName}"
  specs_dir: .ldf/specs

guardrails:
  preset: custom
  overrides: {}

question_packs:
  - security
  - testing
  - api-design
  - data-model

mcp_servers:
  - spec-inspector
  - coverage-reporter

lint:
  strict: false
  auto_fix: false
`;
            fs.writeFileSync(path.join(ldfDir, 'config.yaml'), configYaml);

            specProvider.refresh();
            guardrailProvider.refresh();
            taskProvider.refresh();

            vscode.window.showInformationMessage('LDF: Project initialized');
        })
    );
}

async function openSpecFile(
    workspacePath: string,
    specName: string,
    fileType: 'requirements' | 'design' | 'tasks'
): Promise<void> {
    const config = vscode.workspace.getConfiguration('ldf');
    const specsDir = path.join(
        workspacePath,
        config.get('specsDirectory', '.ldf/specs')
    );
    const filePath = path.join(specsDir, specName, `${fileType}.md`);

    if (!fs.existsSync(filePath)) {
        const create = await vscode.window.showQuickPick(['Create', 'Cancel'], {
            placeHolder: `${fileType}.md doesn't exist. Create it?`,
        });

        if (create !== 'Create') return;

        // Create with template
        const templates: Record<string, string> = {
            design: `# ${specName} - Design

## Architecture Overview

[High-level architecture description]

## Components

### Component 1

**Purpose:** [What it does]

**Interface:**
\`\`\`typescript
interface Component1 {
  // Define interface
}
\`\`\`

## Data Model

### Entity 1

| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK |

## API Endpoints

### POST /api/v1/resource

**Request:**
\`\`\`json
{
  "field": "value"
}
\`\`\`

**Response:**
\`\`\`json
{
  "id": "uuid"
}
\`\`\`

## Guardrail Mapping

| Guardrail | Implementation | Section |
|-----------|---------------|---------|
| 1. Testing | Unit tests + Integration | [T-1] |

## Security Considerations

- [Security consideration 1]
`,
            tasks: `# ${specName} - Tasks

## Phase 1: Setup

- [ ] Task 1.1: Create initial structure
- [ ] Task 1.2: Set up dependencies

## Phase 2: Implementation

- [ ] Task 2.1: Implement core functionality
- [ ] Task 2.2: Add error handling
- [ ] Task 2.3: Add validation

## Phase 3: Testing

- [ ] Task 3.1: Write unit tests
- [ ] Task 3.2: Write integration tests

## Phase 4: Documentation

- [ ] Task 4.1: Update API documentation
- [ ] Task 4.2: Add inline comments

## Completion Checklist

- [ ] All tasks completed
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Code reviewed
`,
        };

        const template = templates[fileType] || `# ${specName} - ${fileType}\n\n`;
        fs.writeFileSync(filePath, template);
    }

    const doc = await vscode.workspace.openTextDocument(filePath);
    await vscode.window.showTextDocument(doc);
}

async function runLint(workspacePath: string, specName?: string): Promise<void> {
    const terminal = vscode.window.createTerminal('LDF Lint');
    terminal.show();

    // Use --all flag when no specific spec is provided
    const command = specName
        ? `ldf lint ${specName}`
        : 'ldf lint --all';

    terminal.sendText(command);
}

async function runAudit(
    workspacePath: string,
    specName: string,
    auditType: string
): Promise<void> {
    const terminal = vscode.window.createTerminal('LDF Audit');
    terminal.show();

    terminal.sendText(`ldf audit --type ${auditType} --spec ${specName}`);
}
