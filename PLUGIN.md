# Plugin and Skill Usage

Engineering Report Stack is packaged as a **skill-first Codex plugin**.

## Plugin manifest

The repository root contains:

```text
.codex-plugin/plugin.json
skills/
```

This follows the current OpenAI Codex plugin layout: a plugin manifest plus optional skills.

## Immediate local use

To install the skills into local Codex discovery:

```bash
./scripts/install-codex-skills.sh
```

The installer copies the canonical skill folders into:

```text
${CODEX_HOME:-~/.codex}/skills
```

Restart Codex after installation.

Use `--force` only when replacing an existing installed copy is intentional.

## Primary skill

`engineering-web-report` is the orchestration skill. It enforces:

```text
inspect
  -> trace
  -> impact
  -> modify canonical data
  -> validate
  -> generate
  -> build
  -> review
```

Specialized skills are available for architecture, data modelling, diagrams, citations, evidence, and final review.

## Remote Workstation integration

Remote Workstation remains the execution/control plane. This plugin provides the engineering-report knowledge and workflow.

```text
Engineering Report Stack
          |
          | decides HOW the report should be changed
          v
Agent / ChatGPT / Codex
          |
          | executes filesystem/git/build/browser tasks
          v
Remote Workstation
          |
          v
Report repository
```

Do not couple report-domain logic into Remote Workstation itself.
