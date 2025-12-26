# Implement a specific task from a spec

## Arguments
- `spec-name`: Name of the spec (required)
- `task-number`: Task number to implement (e.g., "2.1") (required)

## Process

1. **Load Spec Context**
   - Read `.ldf/specs/{spec}/requirements.md`
   - Read `.ldf/specs/{spec}/design.md`
   - Read `.ldf/specs/{spec}/tasks.md`
   - Find the specific task

2. **Check Dependencies**
   - Verify dependent tasks are complete
   - Block if dependencies not met

3. **Run Task-Guardrails Macro**
   - Load active guardrails from `.ldf/guardrails.yaml`
   - Present checklist for this task
   - Verify each applicable guardrail addressed
   - Block if critical guardrails not addressed

4. **Implement Code**
   - Follow the design from design.md
   - Implement the task description
   - Add proper error handling
   - Follow project coding patterns

5. **Write Tests**
   - Unit tests for business logic
   - Integration tests for APIs
   - Meet coverage threshold

6. **Update Task Status**
   - Mark task as complete in tasks.md
   - Add commit reference

7. **Commit**
   - Stage changes
   - Commit with reference to spec and task
