# LDF Documentation

Welcome to the LDF (LLM Development Framework) documentation. Choose your learning path based on your experience level.

---

## 🚀 Getting Started Paths

### Path 1: Complete Beginner (Never used a terminal)
**Total Time: ~90 minutes**

1. **[Install LDF →](installation/)** (30-45 min)
   - Choose your platform: [macOS](installation/macos.md) | [Windows](installation/windows.md) | [Linux Ubuntu](installation/linux-ubuntu.md) | [Linux Fedora](installation/linux-fedora.md)
   - Step-by-step installation with troubleshooting

2. **[Your First LDF Spec →](tutorials/01-first-spec.md)** (20 min)
   - Hands-on tutorial creating a "Hello World" spec
   - Learn the three-phase workflow

3. **[Understanding Guardrails →](tutorials/02-guardrails.md)** (25 min)
   - Deep dive into the 8 core quality constraints
   - Practice filling out coverage matrices

4. **[Continue Learning →](#tutorial-series)**
   - Progressive tutorials building on each other

---

### Path 2: Experienced Developer (Familiar with terminal/Python)
**Total Time: ~30 minutes**

1. **[5-Minute Quickstart →](quickstart.md)** (5 min)
   - Fast installation and first project setup

2. **[Core Concepts →](concepts.md)** (10 min)
   - Philosophy and methodology overview

3. **[Command Reference →](reference/commands.md)** (5 min)
   - Quick command cheat sheet

4. **[Example Projects →](/examples/)** (10 min)
   - Real-world specs for Python/TypeScript/Go

---

### Path 3: Team Lead (Setting up LDF for team)
**Total Time: ~45 minutes**

1. **[Customization Guide →](customization.md)** (20 min)
   - Custom guardrails and question-packs
   - Team templates and presets

2. **[CI/CD Integration →](/integrations/ci-cd/)** (15 min)
   - GitHub Actions and GitLab CI setup

3. **[Multi-Agent Workflow →](multi-agent-workflow.md)** (10 min)
   - Using ChatGPT/Gemini for spec review

---

## 📚 Core Documentation

### Installation

**Start here if you haven't installed LDF yet**

- **[Installation Hub →](installation/)** - Choose your platform
  - [macOS Installation](installation/macos.md) - Intel & Apple Silicon
  - [Windows Installation](installation/windows.md) - Windows 10/11
  - [Ubuntu/Debian Installation](installation/linux-ubuntu.md) - Ubuntu 20.04+
  - [Fedora/RHEL Installation](installation/linux-fedora.md) - Fedora 36+, RHEL 9+

---

### Tutorial Series

**Progressive hands-on learning** (recommended order)

1. **[Your First LDF Spec](tutorials/01-first-spec.md)** ⭐ Start here
   - Create a simple "Hello World" spec
   - Learn requirements, design, tasks workflow
   - Time: 20 minutes

2. **[Understanding Guardrails](tutorials/02-guardrails.md)**
   - The 8 core quality constraints explained
   - How to fill out coverage matrices
   - Time: 25 minutes

3. **[Working with Question-Packs](tutorials/03-question-packs.md)**
   - Answer security, testing, API design questions
   - Create and customize answerpacks
   - Time: 20 minutes

4. **[Multi-Agent Review Workflow](tutorials/04-multi-agent-review.md)**
   - Generate audit requests for ChatGPT/Gemini
   - Import feedback and iterate
   - Time: 30 minutes

5. **[MCP Setup for AI Assistants](tutorials/05-mcp-setup.md)**
   - 90% token savings with Model Context Protocol
   - Integration with Claude Code
   - Time: 25 minutes

---

### Core Concepts

**Understanding LDF's philosophy and approach**

- **[Concepts & Philosophy](concepts.md)**
  - Spec-first development methodology
  - The three-phase workflow
  - When to use (and not use) LDF
  - Guardrails explained

- **[Task Format Guide](task-format.md)**
  - Task numbering conventions
  - Status detection
  - Dependencies and checklists

- **[Answerpacks](answerpacks.md)**
  - Design decision capture
  - Question-pack usage
  - Rationale documentation

- **[Glossary](glossary.md)**
  - Technical terms explained
  - RLS, HIPAA, OWASP definitions

---

### Visual Guides

**Diagrams and examples for visual learners**

- **[Workflow Diagrams](visual-guides/workflows.md)**
  - Three-phase workflow visualized
  - Multi-agent review flow
  - MCP architecture
  - Decision trees

- **[Guardrail Examples](visual-guides/guardrail-examples.md)**
  - Real coverage matrix examples
  - Hello World example
  - Authentication system example
  - Multi-tenant SaaS example
  - Fintech payment example

---

### Quick Reference

**Fast lookups when you need them**

- **[Command Reference](reference/commands.md)**
  - CLI command cheat sheet
  - Common workflows
  - Parameter quick reference

- **[File Structure Reference](reference/file-structure.md)**
  - Project layout
  - Config file formats
  - Spec organization

- **[Troubleshooting Guide](reference/troubleshooting.md)**
  - Common installation issues
  - Lint errors and solutions
  - Platform-specific problems
  - FAQ

---

## 🔧 Advanced Topics

### Integrations

- **[VS Code Extension](https://github.com/LLMdotInfo/ldf-vscode)**
  - Visual spec management
  - Guardrails view
  - Task progress tracking

- **[MCP Servers](../ldf/_mcp_servers/MCP_SETUP.md)**
  - spec_inspector setup
  - coverage_reporter usage
  - Token efficiency

- **[Multi-Agent Workflow](multi-agent-workflow.md)**
  - ChatGPT/Gemini spec audits
  - API-based automation
  - Feedback import

- **[CI/CD Integration](/integrations/ci-cd/)**
  - GitHub Actions
  - GitLab CI
  - Automated linting
  - Coverage validation

---

### Customization

- **[Customization Guide](customization.md)**
  - Custom guardrails
  - Custom question-packs
  - Domain presets
  - Team templates

---

### For Contributors

- **[Architecture](architecture.md)**
  - Internal module structure
  - Design decisions
  - Extension points

- **[Contributing Guide](../CONTRIBUTING.md)**
  - Development setup
  - Code style (Black, Ruff, MyPy)
  - Testing requirements
  - Pull request process

---

## 📦 Examples

**Real-world specifications and projects**

Located in `/examples/`:

- **[Python FastAPI](/examples/python-fastapi/)** - Microservice with async endpoints
- **[Python Flask](/examples/python-flask/)** - Web application with templates
- **[Python Django](/examples/python-django/)** - Full-stack web framework
- **[TypeScript Node](/examples/typescript-node/)** - Express.js REST API
- **[Go Service](/examples/go-service/)** - Microservice in Go

Each example includes complete requirements.md, design.md, and tasks.md files.

---

## 🎯 Use Case Guides

### By Project Type

**Building a SaaS application?**
1. [Install LDF](installation/)
2. Initialize with `saas` preset: `ldf init --preset saas`
3. Read [Multi-Tenancy Guardrail Example](visual-guides/guardrail-examples.md#example-3-saas-multi-tenant-feature)
4. Review [SaaS Example Project](/examples/python-fastapi/)

**Building a Fintech application?**
1. [Install LDF](installation/)
2. Initialize with `fintech` preset: `ldf init --preset fintech`
3. Read [Payment Processing Example](visual-guides/guardrail-examples.md#example-4-fintech-payment-processing)
4. Study double-entry ledger requirements

**Building a Healthcare application?**
1. [Install LDF](installation/)
2. Initialize with `healthcare` preset: `ldf init --preset healthcare`
3. Review HIPAA compliance guardrails
4. Understand PHI handling requirements

**Building an API-only service?**
1. [Install LDF](installation/)
2. Initialize with `api-only` preset: `ldf init --preset api-only`
3. Review [API Design Guardrail](concepts.md#5-api-design)
4. Check [Go Service Example](/examples/go-service/)

---

### By Role

**Developer (implementing features)**
- Start: [First Spec Tutorial](tutorials/01-first-spec.md)
- Use: [Task Format Guide](task-format.md)
- Reference: [Command Reference](reference/commands.md)

**Architect (designing systems)**
- Start: [Concepts Guide](concepts.md)
- Use: [Workflow Diagrams](visual-guides/workflows.md)
- Reference: [Example Projects](/examples/)

**Security Engineer (reviewing specs)**
- Start: [Guardrails Deep Dive](tutorials/02-guardrails.md)
- Use: [Security Question-Pack](customization.md#question-packs)
- Reference: [Security Examples](visual-guides/guardrail-examples.md)

**Team Lead (setting up process)**
- Start: [Customization Guide](customization.md)
- Use: [CI/CD Integration](/integrations/ci-cd/)
- Reference: [Multi-Agent Workflow](multi-agent-workflow.md)

---

## 🆘 Getting Help

### Common Issues

**Installation problems?**
- See platform-specific troubleshooting in [Installation Guides](installation/)
- Run `ldf doctor` for diagnostics
- Check [Troubleshooting Guide](reference/troubleshooting.md)

**Lint errors?**
- Common errors explained in [Troubleshooting](reference/troubleshooting.md#lint-errors)
- Guardrail matrix help in [Guardrail Examples](visual-guides/guardrail-examples.md)

**Not sure how to start?**
- Follow [Path 1: Complete Beginner](#path-1-complete-beginner-never-used-a-terminal) above
- Watch the [First Spec Tutorial](tutorials/01-first-spec.md)

---

### Support Channels

**Found a bug?**
- Report at: [GitHub Issues](https://github.com/LLMdotInfo/ldf/issues)
- Include output from `ldf doctor`

**Have a question?**
- Check [FAQ in Troubleshooting](reference/troubleshooting.md#faq)
- Search [existing GitHub issues](https://github.com/LLMdotInfo/ldf/issues)

**Want to contribute?**
- Read [Contributing Guide](../CONTRIBUTING.md)
- Check [Architecture docs](architecture.md)

---

## 📈 Documentation Version

This documentation is for **LDF version 1.0.0**.

Check your installed version:
```bash
ldf --version
```

Upgrade to latest:
```bash
pip install --upgrade ldf
```

---

## 🗺️ Documentation Map

```
docs/
├── README.md (you are here)
│
├── installation/              # Platform-specific installation guides
│   ├── README.md             # Platform selector
│   ├── macos.md
│   ├── windows.md
│   ├── linux-ubuntu.md
│   └── linux-fedora.md
│
├── tutorials/                 # Progressive learning path
│   ├── 01-first-spec.md      # ⭐ Start here for beginners
│   ├── 02-guardrails.md
│   ├── 03-question-packs.md
│   ├── 04-multi-agent-review.md
│   └── 05-mcp-setup.md
│
├── visual-guides/             # Diagrams and examples
│   ├── workflows.md
│   └── guardrail-examples.md
│
├── reference/                 # Quick references
│   ├── commands.md
│   ├── file-structure.md
│   └── troubleshooting.md
│
├── quickstart.md              # 5-minute quick start
├── concepts.md                # Core philosophy
├── customization.md           # Advanced configuration
├── answerpacks.md             # Design decisions
├── task-format.md             # Task formatting rules
├── glossary.md                # Terms explained
├── multi-agent-workflow.md    # AI-based audits
└── architecture.md            # For contributors
```

---

## 🎓 Learning Resources

### Recommended Reading Order

**Week 1: Basics**
1. Day 1-2: [Installation](installation/) + [First Spec](tutorials/01-first-spec.md)
2. Day 3: [Guardrails](tutorials/02-guardrails.md)
3. Day 4: [Question-Packs](tutorials/03-question-packs.md)
4. Day 5: [Concepts](concepts.md) + [Examples](/examples/)

**Week 2: Advanced**
5. Day 1: [Multi-Agent Workflow](tutorials/04-multi-agent-review.md)
6. Day 2: [MCP Setup](tutorials/05-mcp-setup.md)
7. Day 3: [Customization](customization.md)
8. Day 4-5: Build your first real project

---

## 🔄 Documentation Feedback

Help us improve! If you find:
- Broken links
- Unclear explanations
- Missing information
- Errors or typos

Please [open an issue](https://github.com/LLMdotInfo/ldf/issues) with the label `documentation`.

---

**Ready to start?** Choose your path above, or jump straight to:
- **Beginners**: [Installation Guide](installation/) → [First Spec Tutorial](tutorials/01-first-spec.md)
- **Experienced**: [5-Minute Quickstart](quickstart.md) → [Examples](/examples/)
