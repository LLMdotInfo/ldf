/**
 * Task Tree View Provider
 *
 * Displays current tasks from active specs:
 * - Shows in-progress tasks at top
 * - Groups by spec
 * - Allows marking tasks complete
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

export interface TaskInfo {
    id: string;
    specName: string;
    title: string;
    status: 'pending' | 'in-progress' | 'complete';
    line: number; // Line number in tasks.md for editing
}

export class TaskTreeProvider implements vscode.TreeDataProvider<TaskTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<TaskTreeItem | undefined | null | void> =
        new vscode.EventEmitter<TaskTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<TaskTreeItem | undefined | null | void> =
        this._onDidChangeTreeData.event;

    private tasks: TaskInfo[] = [];
    private workspacePath: string;

    constructor(workspacePath: string) {
        this.workspacePath = workspacePath;
    }

    refresh(): void {
        this.loadTasks();
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: TaskTreeItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: TaskTreeItem): Thenable<TaskTreeItem[]> {
        if (!element) {
            return Promise.resolve(this.getTaskItems());
        }
        return Promise.resolve([]);
    }

    private loadTasks(): void {
        this.tasks = [];

        const config = vscode.workspace.getConfiguration('ldf');
        const specsDir = path.join(
            this.workspacePath,
            config.get('specsDirectory', '.ldf/specs')
        );

        if (!fs.existsSync(specsDir)) {
            return;
        }

        const specs = fs.readdirSync(specsDir, { withFileTypes: true })
            .filter((d) => d.isDirectory())
            .map((d) => d.name);

        for (const specName of specs) {
            const tasksPath = path.join(specsDir, specName, 'tasks.md');
            if (fs.existsSync(tasksPath)) {
                const content = fs.readFileSync(tasksPath, 'utf-8');
                const specTasks = this.parseTasksFile(specName, content);
                this.tasks.push(...specTasks);
            }
        }

        // Sort: in-progress first, then pending, then complete
        this.tasks.sort((a, b) => {
            const statusOrder = {
                'in-progress': 0,
                pending: 1,
                complete: 2,
            };
            const orderA = statusOrder[a.status];
            const orderB = statusOrder[b.status];
            if (orderA !== orderB) return orderA - orderB;
            return a.id.localeCompare(b.id);
        });

        // Limit to reasonable number
        this.tasks = this.tasks.slice(0, 50);
    }

    private parseTasksFile(specName: string, content: string): TaskInfo[] {
        const tasks: TaskInfo[] = [];
        const lines = content.split('\n');

        // Look for task patterns:
        // - [ ] Task 1.1: Description
        // - [x] Task 1.2: Description
        // * [ ] Task 2.1: Description
        const taskPattern = /^(\s*)[-*]\s+\[([ xX])\]\s+(Task\s+)?(\d+(?:\.\d+)?):?\s*(.+)$/;

        let lineNumber = 0;
        for (const line of lines) {
            lineNumber++;
            const match = line.match(taskPattern);
            if (match) {
                const isComplete = match[2].toLowerCase() === 'x';
                const taskId = match[4];
                const title = match[5].trim();

                tasks.push({
                    id: `${specName}:${taskId}`,
                    specName,
                    title: `${taskId}: ${title}`,
                    status: isComplete ? 'complete' : 'pending',
                    line: lineNumber,
                });
            }
        }

        // Mark first incomplete task as in-progress (heuristic)
        const firstIncomplete = tasks.find((t) => t.status === 'pending');
        if (firstIncomplete) {
            firstIncomplete.status = 'in-progress';
        }

        return tasks;
    }

    private getTaskItems(): TaskTreeItem[] {
        if (this.tasks.length === 0) {
            return [
                new TaskTreeItem({
                    id: 'no-tasks',
                    specName: '',
                    title: 'No tasks found',
                    status: 'pending',
                    line: 0,
                }),
            ];
        }

        return this.tasks
            .filter((t) => t.status !== 'complete') // Only show incomplete
            .map((task) => new TaskTreeItem(task));
    }

    getTasks(): TaskInfo[] {
        return this.tasks;
    }

    getTask(id: string): TaskInfo | undefined {
        return this.tasks.find((t) => t.id === id);
    }

    async markTaskComplete(taskId: string): Promise<boolean> {
        const task = this.getTask(taskId);
        if (!task) return false;

        const config = vscode.workspace.getConfiguration('ldf');
        const specsDir = path.join(
            this.workspacePath,
            config.get('specsDirectory', '.ldf/specs')
        );
        const tasksPath = path.join(specsDir, task.specName, 'tasks.md');

        if (!fs.existsSync(tasksPath)) return false;

        const content = fs.readFileSync(tasksPath, 'utf-8');
        const lines = content.split('\n');

        // Find and update the task line
        if (task.line > 0 && task.line <= lines.length) {
            const line = lines[task.line - 1];
            const updated = line.replace(/\[\s\]/, '[x]');
            if (updated !== line) {
                lines[task.line - 1] = updated;
                fs.writeFileSync(tasksPath, lines.join('\n'), 'utf-8');
                this.refresh();
                return true;
            }
        }

        return false;
    }
}

export class TaskTreeItem extends vscode.TreeItem {
    public readonly taskId: string;

    constructor(public readonly taskInfo: TaskInfo) {
        super(taskInfo.title, vscode.TreeItemCollapsibleState.None);

        this.taskId = taskInfo.id;
        this.contextValue = taskInfo.id === 'no-tasks' ? 'info' : 'task';
        this.description = taskInfo.specName;

        if (taskInfo.status === 'in-progress') {
            this.iconPath = new vscode.ThemeIcon(
                'play-circle',
                new vscode.ThemeColor('charts.blue')
            );
            this.tooltip = 'In Progress';
        } else if (taskInfo.status === 'complete') {
            this.iconPath = new vscode.ThemeIcon(
                'check',
                new vscode.ThemeColor('charts.green')
            );
            this.tooltip = 'Complete';
        } else {
            this.iconPath = new vscode.ThemeIcon('circle-outline');
            this.tooltip = 'Pending';
        }

        // Click to open tasks.md at the task line
        if (taskInfo.line > 0 && taskInfo.specName) {
            const config = vscode.workspace.getConfiguration('ldf');
            const specsDir = config.get('specsDirectory', '.ldf/specs');
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];

            if (workspaceFolder) {
                const tasksPath = path.join(
                    workspaceFolder.uri.fsPath,
                    specsDir,
                    taskInfo.specName,
                    'tasks.md'
                );
                this.command = {
                    command: 'vscode.open',
                    title: 'Open Task',
                    arguments: [
                        vscode.Uri.file(tasksPath),
                        {
                            selection: new vscode.Range(
                                taskInfo.line - 1,
                                0,
                                taskInfo.line - 1,
                                100
                            ),
                        },
                    ],
                };
            }
        }
    }
}
