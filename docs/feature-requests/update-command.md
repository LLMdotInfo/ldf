# Feature Request: `ldf update` Command

## Summary

Add a `ldf update` command that allows projects to pull updates from the LDF framework source while preserving local customizations.

## Problem Statement

Currently, `ldf init` is a one-time operation that copies framework files into a project. After initialization:

- No mechanism exists to pull framework updates (new guardrails, improved templates, bug fixes)
- Users must manually track LDF releases and diff/merge changes
- Custom guardrails and project-specific configurations risk being overwritten during manual updates
- Projects fall behind on framework improvements over time

### Real-World Impact

A project using LDF v0.1.0 with custom guardrails (e.g., Content Moderation #101, SEO Requirements #102) has no way to receive framework updates without:

1. Manually checking LDF repo for changes
2. Diffing each file category (templates, macros, question-packs)
3. Selectively merging while avoiding overwrites to customizations
4. Re-running `ldf lint` to ensure nothing broke

This manual process is error-prone and discourages adoption of a living framework.

## Proposed Solution

Add a `ldf update` command with the following capabilities:

```bash
# Check for available updates
ldf update --check

# Preview changes without applying
ldf update --dry-run

# Apply updates interactively
ldf update

# Apply updates non-interactively (CI/CD)
ldf update --yes

# Update specific components only
ldf update --only templates
ldf update --only guardrails
ldf update --only question-packs
ldf update --only macros
```

### Behavior

1. **Source Tracking**: Store the LDF source version/commit in `.ldf/config.yaml`:
   ```yaml
   ldf:
     source: "/path/to/ldf"  # or "pip:ldf==0.1.0" or "git:LLMdotInfo/ldf@v0.2.0"
     installed_version: "0.1.0"
     last_updated: "2025-12-07"
   ```

2. **Smart Merging**:
   - Framework files (templates, macros, question-packs): Replace with new versions
   - User customizations (custom guardrails, answerpacks, specs): Never touch
   - `guardrails.yaml`: Merge new core guardrails, preserve custom IDs (100+)
   - `config.yaml`: Preserve user settings, add new framework defaults

3. **Diff Preview**:
   ```
   $ ldf update --dry-run

   LDF Update Preview (0.1.0 -> 0.2.0)

   New files:
     + .ldf/templates/adr.md
     + .ldf/question-packs/performance.yaml

   Modified files:
     ~ .ldf/templates/requirements.md (12 lines changed)
     ~ .ldf/macros/coverage-gate.md (bug fix)

   Preserved (no changes):
     = .ldf/guardrails.yaml (custom guardrails 101, 102 preserved)
     = .ldf/specs/* (user specs unchanged)
     = .ldf/answerpacks/* (user answers unchanged)

   Run `ldf update` to apply changes.
   ```

4. **Conflict Resolution**:
   - If user modified a framework file, show diff and prompt for resolution
   - Option to keep local, take upstream, or merge manually

## Implementation Notes

### Files to Track

| Category | Framework Source | User Customizable | Update Strategy |
|----------|------------------|-------------------|-----------------|
| `templates/*.md` | Yes | No | Replace |
| `macros/*.md` | Yes | No | Replace |
| `question-packs/*.yaml` | Yes | No | Replace |
| `guardrails.yaml` | Partial | Yes (custom IDs) | Merge |
| `config.yaml` | Partial | Yes | Merge new keys |
| `specs/*` | No | Yes | Never touch |
| `answerpacks/*` | No | Yes | Never touch |
| `.claude/commands/*` | Yes | Possible | Replace or merge |

### Version Detection

For local source installs:
```python
def get_source_version(source_path: Path) -> str:
    # Check pyproject.toml version
    # Or check git tag/commit
    pass
```

For pip installs:
```python
import importlib.metadata
version = importlib.metadata.version("ldf")
```

## Success Criteria

1. `ldf update --check` shows available updates without modifying files
2. `ldf update --dry-run` shows exact changes that would be applied
3. `ldf update` applies framework updates while preserving:
   - All files in `specs/`
   - All files in `answerpacks/`
   - Custom guardrails (ID >= 100)
   - User-specific `config.yaml` values
4. `ldf lint` passes after update
5. Works with both local source (`-e` install) and pip package installs

## Priority

**Medium-High** - Essential for framework adoption at scale. Without this, projects either:
- Miss important framework improvements
- Risk breaking customizations during manual updates
- Avoid updating entirely

---

**Submitted:** 2025-12-07
**Submitter:** llm.info project (LDF adopter)
**Related:** Initial adoption experience with 5 backfilled specs
