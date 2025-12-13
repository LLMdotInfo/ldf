/**
 * Guardrail Coverage View Provider
 *
 * Displays guardrail coverage across all specs:
 * - Shows each guardrail with coverage status
 * - Indicates which specs cover each guardrail
 * - Highlights gaps in coverage
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

interface Guardrail {
    id: number;
    name: string;
    description: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
    enabled: boolean;
}

interface GuardrailCoverage {
    guardrail: Guardrail;
    coveredBy: string[]; // spec names
    status: 'covered' | 'partial' | 'not-covered' | 'not-applicable';
}

export class GuardrailTreeProvider implements vscode.TreeDataProvider<GuardrailTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<GuardrailTreeItem | undefined | null | void> =
        new vscode.EventEmitter<GuardrailTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<GuardrailTreeItem | undefined | null | void> =
        this._onDidChangeTreeData.event;

    private guardrails: Guardrail[] = [];
    private coverage: GuardrailCoverage[] = [];
    private workspacePath: string;

    constructor(workspacePath: string) {
        this.workspacePath = workspacePath;
        this.loadGuardrails();
    }

    refresh(): void {
        this.loadGuardrails();
        this.analyzeCoverage();
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: GuardrailTreeItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: GuardrailTreeItem): Thenable<GuardrailTreeItem[]> {
        if (!element) {
            // Root level - show guardrails grouped by severity
            return Promise.resolve(this.getGuardrailItems());
        } else if (element.contextValue === 'guardrail') {
            // Show specs that cover this guardrail
            return Promise.resolve(this.getCoverageItems(element.guardrailId!));
        }
        return Promise.resolve([]);
    }

    private loadGuardrails(): void {
        // Try to load from config, fall back to defaults
        const config = vscode.workspace.getConfiguration('ldf');
        const guardrailsPath = path.join(
            this.workspacePath,
            config.get('guardrailsFile', '.ldf/guardrails.yaml')
        );

        // Default guardrails if no config found
        this.guardrails = [
            { id: 1, name: 'Testing Coverage', description: 'Minimum test coverage thresholds', severity: 'critical', enabled: true },
            { id: 2, name: 'Security Basics', description: 'OWASP Top 10 prevention', severity: 'critical', enabled: true },
            { id: 3, name: 'Error Handling', description: 'Consistent error responses', severity: 'high', enabled: true },
            { id: 4, name: 'Logging & Observability', description: 'Structured logging, correlation IDs', severity: 'high', enabled: true },
            { id: 5, name: 'API Design', description: 'Versioning, pagination, error format', severity: 'high', enabled: true },
            { id: 6, name: 'Data Validation', description: 'Input validation at boundaries', severity: 'critical', enabled: true },
            { id: 7, name: 'Database Migrations', description: 'Reversible, separate from backfills', severity: 'high', enabled: true },
            { id: 8, name: 'Documentation', description: 'API docs, README, inline comments', severity: 'medium', enabled: true },
        ];

        // Try to load custom guardrails from YAML
        if (fs.existsSync(guardrailsPath)) {
            try {
                const content = fs.readFileSync(guardrailsPath, 'utf-8');
                // Basic YAML parsing for guardrails list
                // In production, use js-yaml library
                const customGuardrails = this.parseGuardrailsYaml(content);
                if (customGuardrails.length > 0) {
                    this.guardrails = customGuardrails;
                }
            } catch (e) {
                console.error('Failed to load guardrails:', e);
            }
        }
    }

    private parseGuardrailsYaml(content: string): Guardrail[] {
        // Simple YAML parsing - in production use js-yaml
        const guardrails: Guardrail[] = [];
        const lines = content.split('\n');
        let currentGuardrail: Partial<Guardrail> = {};

        for (const line of lines) {
            const idMatch = line.match(/id:\s*(\d+)/);
            const nameMatch = line.match(/name:\s*["']?([^"'\n]+)["']?/);
            const descMatch = line.match(/description:\s*["']?([^"'\n]+)["']?/);
            const severityMatch = line.match(/severity:\s*(critical|high|medium|low)/);
            const enabledMatch = line.match(/enabled:\s*(true|false)/);

            if (idMatch) currentGuardrail.id = parseInt(idMatch[1]);
            if (nameMatch) currentGuardrail.name = nameMatch[1].trim();
            if (descMatch) currentGuardrail.description = descMatch[1].trim();
            if (severityMatch) currentGuardrail.severity = severityMatch[1] as Guardrail['severity'];
            if (enabledMatch) currentGuardrail.enabled = enabledMatch[1] === 'true';

            // If we have a complete guardrail, add it
            if (currentGuardrail.id && currentGuardrail.name && line.trim() === '' || line.match(/^  - id:/)) {
                if (currentGuardrail.id && currentGuardrail.name) {
                    guardrails.push({
                        id: currentGuardrail.id,
                        name: currentGuardrail.name,
                        description: currentGuardrail.description || '',
                        severity: currentGuardrail.severity || 'medium',
                        enabled: currentGuardrail.enabled ?? true,
                    });
                }
                currentGuardrail = {};
            }
        }

        // Don't forget the last one
        if (currentGuardrail.id && currentGuardrail.name) {
            guardrails.push({
                id: currentGuardrail.id,
                name: currentGuardrail.name,
                description: currentGuardrail.description || '',
                severity: currentGuardrail.severity || 'medium',
                enabled: currentGuardrail.enabled ?? true,
            });
        }

        return guardrails;
    }

    private analyzeCoverage(): void {
        this.coverage = this.guardrails.map((g) => ({
            guardrail: g,
            coveredBy: [],
            status: 'not-covered' as const,
        }));

        // Scan specs for guardrail coverage
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
            const reqPath = path.join(specsDir, specName, 'requirements.md');
            if (fs.existsSync(reqPath)) {
                const content = fs.readFileSync(reqPath, 'utf-8');
                this.parseGuardrailCoverage(specName, content);
            }
        }

        // Update status based on coverage
        for (const cov of this.coverage) {
            if (cov.coveredBy.length === 0) {
                cov.status = 'not-covered';
            } else if (cov.coveredBy.length >= specs.length * 0.5) {
                cov.status = 'covered';
            } else {
                cov.status = 'partial';
            }
        }
    }

    private parseGuardrailCoverage(specName: string, content: string): void {
        // Look for guardrail coverage matrix in requirements
        // Format: | 1. Testing Coverage | [US-1] | [S3.2] | [T-1] | Alice | DONE |
        const matrixPattern = /\|\s*(\d+)\.\s*([^|]+)\s*\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|\s*(DONE|TODO|N\/A)\s*\|/gi;
        let match;

        while ((match = matrixPattern.exec(content)) !== null) {
            const guardrailId = parseInt(match[1]);
            const status = match[3].toUpperCase();

            if (status !== 'N/A') {
                const coverage = this.coverage.find((c) => c.guardrail.id === guardrailId);
                if (coverage && !coverage.coveredBy.includes(specName)) {
                    coverage.coveredBy.push(specName);
                }
            }
        }
    }

    private getGuardrailItems(): GuardrailTreeItem[] {
        // Group by severity
        const criticalItems = this.coverage
            .filter((c) => c.guardrail.severity === 'critical' && c.guardrail.enabled)
            .map((c) => new GuardrailTreeItem(c));

        const highItems = this.coverage
            .filter((c) => c.guardrail.severity === 'high' && c.guardrail.enabled)
            .map((c) => new GuardrailTreeItem(c));

        const mediumItems = this.coverage
            .filter((c) => c.guardrail.severity === 'medium' && c.guardrail.enabled)
            .map((c) => new GuardrailTreeItem(c));

        const lowItems = this.coverage
            .filter((c) => c.guardrail.severity === 'low' && c.guardrail.enabled)
            .map((c) => new GuardrailTreeItem(c));

        return [...criticalItems, ...highItems, ...mediumItems, ...lowItems];
    }

    private getCoverageItems(guardrailId: number): GuardrailTreeItem[] {
        const coverage = this.coverage.find((c) => c.guardrail.id === guardrailId);
        if (!coverage || coverage.coveredBy.length === 0) {
            return [
                new GuardrailTreeItem(
                    undefined,
                    'No specs cover this guardrail'
                ),
            ];
        }

        return coverage.coveredBy.map(
            (specName) =>
                new GuardrailTreeItem(undefined, specName, 'spec-reference')
        );
    }

    getCoverage(): GuardrailCoverage[] {
        return this.coverage;
    }
}

export class GuardrailTreeItem extends vscode.TreeItem {
    public readonly guardrailId?: number;

    constructor(
        coverage?: GuardrailCoverage,
        label?: string,
        contextValue?: string
    ) {
        if (coverage) {
            super(
                `${coverage.guardrail.id}. ${coverage.guardrail.name}`,
                vscode.TreeItemCollapsibleState.Collapsed
            );
            this.guardrailId = coverage.guardrail.id;
            this.contextValue = 'guardrail';
            this.tooltip = coverage.guardrail.description;
            this.description = `${coverage.coveredBy.length} specs`;
            this.iconPath = GuardrailTreeItem.getStatusIcon(coverage);
        } else {
            super(label || '', vscode.TreeItemCollapsibleState.None);
            this.contextValue = contextValue || 'info';
            if (contextValue === 'spec-reference') {
                this.iconPath = new vscode.ThemeIcon('file');
            }
        }
    }

    private static getStatusIcon(coverage: GuardrailCoverage): vscode.ThemeIcon {
        switch (coverage.status) {
            case 'covered':
                return new vscode.ThemeIcon(
                    'check',
                    new vscode.ThemeColor('charts.green')
                );
            case 'partial':
                return new vscode.ThemeIcon(
                    'warning',
                    new vscode.ThemeColor('charts.yellow')
                );
            case 'not-covered':
                return new vscode.ThemeIcon(
                    'circle-slash',
                    new vscode.ThemeColor('charts.red')
                );
            case 'not-applicable':
                return new vscode.ThemeIcon('dash');
            default:
                return new vscode.ThemeIcon('circle-outline');
        }
    }
}
