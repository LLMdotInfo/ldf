/**
 * LDF VS Code Extension
 *
 * Provides visual tools for spec-driven development:
 * - Spec tree view with status indicators
 * - Guardrail coverage panel
 * - Task progress tracking
 * - Command palette actions
 */

import * as vscode from 'vscode';
import { SpecTreeProvider } from './specView';
import { GuardrailTreeProvider } from './guardrailView';
import { TaskTreeProvider } from './taskView';
import { registerCommands } from './commands';

let specProvider: SpecTreeProvider;
let guardrailProvider: GuardrailTreeProvider;
let taskProvider: TaskTreeProvider;

export function activate(context: vscode.ExtensionContext) {
    console.log('LDF extension is now active');

    // Get workspace folder
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showWarningMessage('LDF: No workspace folder open');
        return;
    }

    const workspacePath = workspaceFolder.uri.fsPath;

    // Initialize tree providers
    specProvider = new SpecTreeProvider(workspacePath);
    guardrailProvider = new GuardrailTreeProvider(workspacePath);
    taskProvider = new TaskTreeProvider(workspacePath);

    // Register tree views
    const specTreeView = vscode.window.createTreeView('ldf-specs', {
        treeDataProvider: specProvider,
        showCollapseAll: true,
    });

    const guardrailTreeView = vscode.window.createTreeView('ldf-guardrails', {
        treeDataProvider: guardrailProvider,
        showCollapseAll: true,
    });

    const taskTreeView = vscode.window.createTreeView('ldf-tasks', {
        treeDataProvider: taskProvider,
        showCollapseAll: false,
    });

    // Register commands
    registerCommands(context, {
        specProvider,
        guardrailProvider,
        taskProvider,
        workspacePath,
    });

    // Watch for file changes
    const config = vscode.workspace.getConfiguration('ldf');
    if (config.get('autoRefresh', true)) {
        const specsDir = config.get('specsDirectory', '.ldf/specs');
        const watcher = vscode.workspace.createFileSystemWatcher(
            new vscode.RelativePattern(workspaceFolder, `${specsDir}/**/*.md`)
        );

        watcher.onDidChange(() => refreshAll());
        watcher.onDidCreate(() => refreshAll());
        watcher.onDidDelete(() => refreshAll());

        context.subscriptions.push(watcher);
    }

    // Add disposables
    context.subscriptions.push(specTreeView);
    context.subscriptions.push(guardrailTreeView);
    context.subscriptions.push(taskTreeView);

    // Initial refresh
    refreshAll();
}

function refreshAll() {
    specProvider?.refresh();
    guardrailProvider?.refresh();
    taskProvider?.refresh();
}

export function deactivate() {
    console.log('LDF extension is now deactivated');
}
