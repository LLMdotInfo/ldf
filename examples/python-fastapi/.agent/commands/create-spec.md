# Create a new feature specification

## Arguments
- `feature-name`: Name of the feature to create (required)

## Process

1. **Load Question Packs**
   - Read `.ldf/config.yaml` for configured packs
   - Load pack files from `.ldf/question-packs/`

2. **Run Clarify-First Macro**
   - Ask all critical questions from loaded packs
   - Capture answers in `.ldf/answerpacks/{feature}/`
   - Block if critical questions unanswered

3. **Create Spec Directory**
   - Create `.ldf/specs/{feature}/`

4. **Generate requirements.md**
   - Use template from `.ldf/templates/requirements.md`
   - Include question-pack answers summary
   - Include guardrail coverage matrix
   - Add user stories based on answers

5. **Wait for Approval**
   - Present requirements to user
   - Run `ldf lint {feature}` to validate
   - Get explicit approval before continuing

6. **Generate design.md**
   - Use template from `.ldf/templates/design.md`
   - Map guardrails to design components
   - Include architecture diagrams
   - Define API endpoints and data models

7. **Wait for Approval**
   - Present design to user
   - Validate guardrail mapping complete
   - Get explicit approval before continuing

8. **Generate tasks.md**
   - Use template from `.ldf/templates/tasks.md`
   - Break work into <4 hour tasks
   - Include per-task guardrail checklist
   - Add dependencies and test requirements

9. **Final Validation**
   - Run `ldf lint {feature}`
   - Confirm all sections complete
   - Ready for implementation
