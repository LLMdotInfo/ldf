# LDF Framework Prompts

This directory contains reusable prompts for AI-assisted LDF workflows.

## Available Prompts

### `ldf-init-from-research.md`

**Purpose**: Initialize an LDF project from a research/solution document.

**Use When**: You have a comprehensive research document (like a migration analysis, feature specification, or technical proposal) and want to bootstrap an LDF-managed project from it.

**What It Does**:
1. Parses your research document to extract key decisions
2. Configures LDF settings (preset, question packs, coverage thresholds)
3. Creates spec structure based on identified features
4. Populates answer packs from documented decisions
5. Generates an audit trail for traceability

**How to Use**:

```bash
# 1. Copy the prompt to your AI assistant (Claude, ChatGPT, etc.)
# 2. Provide your research document path when prompted
# 3. Follow the 8 interactive phases with confirmations

# Example with Claude Code:
cat .ldf/_framework/prompts/ldf-init-from-research.md | pbcopy
# Then paste into a new Claude Code session
```

**Checkpoint Files**: The prompt writes intermediate files to `docs/_init/` during the process. After successful completion, these are moved to `docs/_init-audit/` for permanent documentation of how the project was initialized.

---

## Creating New Prompts

When adding new prompts to this directory:

1. **Use markdown format** - For readability and syntax highlighting
2. **Include phases** - Break complex workflows into numbered phases
3. **Add confirmations** - Include `✋ CONFIRM:` checkpoints for user validation
4. **Write checkpoints** - Persist state to files for context recovery
5. **Document inputs/outputs** - Be explicit about what the prompt expects and produces

## Related Framework Components

- `macros/` - Reusable markdown snippets for spec documents
- `templates/` - Boilerplate templates for requirements, design, tasks
- `question-packs/` - Domain-specific question templates
