# Review a spec for completeness

## Arguments
- `spec-name`: Name of the spec to review (required)

## Process

1. **Load Spec Files**
   - Check requirements.md exists
   - Check design.md exists
   - Check tasks.md exists

2. **Run Coverage-Gate Macro**
   - Validate guardrail coverage matrix
   - Check all active guardrails have entries
   - Verify no empty cells (or N/A with justification)

3. **Validate Answerpacks**
   - Check `.ldf/answerpacks/{spec}/` exists
   - Verify critical questions answered
   - Flag any template markers remaining

4. **Run Linter**
   - Execute `ldf lint {spec}`
   - Report errors and warnings

5. **Generate Report**
   - Summary of spec status
   - List of issues found
   - Recommendations for fixes
