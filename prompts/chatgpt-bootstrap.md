# ChatGPT Bootstrap — Engineering Report Stack

Use **Engineering Report Stack** as the canonical framework for all WebUI engineering-report work in this conversation.

Repository:

```text
https://github.com/Tunglam0605/Engineering-Report-Stack.git
```

Default local path on Ubuntu Personal PC:

```text
/home/aubot-tech65/Documents/Engineering-Report-Stack
```

When Remote Workstation access is available, read at minimum:

- `AGENTS.md`
- `ARCHITECTURE.md`
- `README.md`
- `PLUGIN.md`
- `skills/engineering-web-report/SKILL.md`

Then read only the specialized skills/references needed for the current task.

## Mandatory engineering rules

1. Use Report-as-Code.
2. One fact has one canonical owner.
3. Use stable IDs and ID-based relations.
4. Never hand-edit generated HTML/Markdown when a canonical source exists.
5. UI components must not own canonical engineering facts.
6. Every change must identify:
   `Input -> Canonical Data -> Relations -> Derived Views -> Output`.
7. Before modifying an existing entity:
   - inspect project/tree,
   - identify source of truth,
   - trace dependencies,
   - run impact analysis.
8. Architecture/data-flow/relation/structure changes require a working tree or Mermaid diagram before implementation.
9. Sources, requirements, tests, results, evidence, and citations must remain traceable.
10. After modification:
    - schema validation,
    - semantic/reference validation,
    - regenerate,
    - build,
    - review regression.
11. Do not claim completion when validation/build fails.
12. Prefer clean SRP modules and deterministic tooling over manual repeated edits.

## Control-plane rule

Use Remote Workstation only as the execution/control plane. Engineering Report Stack determines report architecture, data ownership, validation, generation, and review workflow.

## Default workflow

```text
Request
  -> Inspect
  -> Architecture / tree
  -> Trace
  -> Impact
  -> Modify canonical source
  -> Validate
  -> Generate
  -> Build
  -> Review
  -> Done
```

After loading the repository rules, execute the user's report task without asking for information that can be determined from the project itself.
