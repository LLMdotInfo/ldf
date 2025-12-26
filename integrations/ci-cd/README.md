# CI/CD Integrations

Continuous integration workflows for validating LDF specs and coverage.

## Available Workflows

| File | Platform | Description |
|------|----------|-------------|
| `github-actions.yaml` | GitHub Actions | Full workflow with lint, test, coverage, audit |
| `gitlab-ci.yaml` | GitLab CI | Equivalent pipeline for GitLab |

## Features

### Spec Linting
Validates all specs pass the LDF linter:
- Question-pack answers present
- Guardrail coverage matrix complete
- Per-task checklists included

### Coverage Validation
Checks test coverage meets thresholds:
- Default: 80%
- Critical services: 90%

### Change Detection
Identifies when specs are modified in PRs:
- Warns developers to run audits
- Can trigger automated audits

### Automated Audits (Optional)
Sends changed specs to ChatGPT for review:
- Requires `OPENAI_API_KEY` secret
- Runs on spec changes only
- Results uploaded as artifacts

## Setup Instructions

### GitHub Actions

1. Copy workflow to your repo:
   ```bash
   mkdir -p .github/workflows
   cp github-actions.yaml .github/workflows/ldf.yaml
   ```

2. Configure secrets (optional for automated audit):
   - Go to Settings > Secrets > Actions
   - Add `OPENAI_API_KEY`

3. Adjust paths if needed in the workflow file

### GitLab CI

1. Copy pipeline to your repo:
   ```bash
   cp gitlab-ci.yaml .gitlab-ci.yml
   ```

2. Configure variables (optional for automated audit):
   - Go to Settings > CI/CD > Variables
   - Add `OPENAI_API_KEY`

3. Adjust paths if needed in the pipeline file

## Workflow Stages

```
┌──────────────────────────────────────────────────────────┐
│                    Pull Request                          │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │   Lint Specs    │ ← Validate all specs
              └────────┬────────┘
                       │
           ┌───────────┴───────────┐
           ▼                       ▼
    ┌─────────────┐       ┌──────────────┐
    │  Run Tests  │       │ Check Changes│ ← Detect spec changes
    └──────┬──────┘       └──────┬───────┘
           │                     │
           ▼                     ▼
   ┌───────────────┐     ┌──────────────┐
   │Coverage Check │     │Automated Audit│ ← Optional
   └───────────────┘     └──────────────┘
```

## Customization

### Adjust Coverage Thresholds

In your `.ldf/config.yaml`:
```yaml
coverage:
  default_threshold: 80
  critical_threshold: 90
  critical_services:
    - auth
    - billing
```

### Skip Audit for Draft PRs

GitHub Actions:
```yaml
automated-audit:
  if: github.event.pull_request.draft == false
```

### Add Custom Linting Rules

Create custom guardrails in `.ldf/guardrails.yaml`:
```yaml
guardrails:
  preset: saas
  custom:
    - id: 9
      name: Custom Rule
      severity: high
```

## Troubleshooting

### "ldf command not found"
Ensure the installation step runs:
```yaml
- run: pip install llm-ldf
```

### "No specs found"
Check that `.ldf/specs/` exists and contains spec directories.

### "Coverage validation failed"
Lower thresholds or increase test coverage:
```bash
ldf coverage --verbose
```

### "Audit failed"
Check API key is set and has credits:
```bash
echo $OPENAI_API_KEY
```
