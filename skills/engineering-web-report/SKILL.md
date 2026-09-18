---
name: engineering-web-report
description: Create, refactor, or extend engineering WebUI reports using Report-as-Code, canonical data, traceability, diagrams, citations, evidence, deterministic validation, and generated views. Use for technical reports, compliance reports, validation/test reports, project handoff reports, and requests to replace PowerPoint with a maintainable web report.
---

# Engineering Web Report

Treat the report as an engineering information system, not as hand-edited HTML.

## Required workflow

1. Run `engineering-report inspect <report-root>` when the SDK is available, then identify the canonical source of truth.
2. Map the affected section tree and data dependencies.
3. Run `trace` / `impact` (or construct the equivalent analysis) before editing existing entities.
4. State inputs, outputs, and affected views/components.
5. Change canonical data or reusable rendering code.
6. Never patch generated output when a canonical source exists.
7. Run JSON Schema validation plus semantic checks for IDs, relationships, source locators, evidence paths, and statuses.
8. Regenerate Markdown and the renderer-facing view model.
9. Build the WebUI.
10. Review content, diagrams, citations, evidence, and regressions.

## Core model

Prefer the trace chain:

```text
Source -> Requirement -> Test -> Result -> Evidence
```

Use stable IDs for relationships. Do not duplicate titles, URLs, clauses, or result text across pages.

## Architecture gate

For architecture, data-flow, relationship, or report-structure changes, construct a working tree/flow diagram before implementation. The diagram does not have to appear in the final report unless it helps the reader.

## Completion gate

Do not claim completion until validation and build pass.

When working inside this repository, read `../../AGENTS.md`, `../../ARCHITECTURE.md`, and only the framework reference needed for the current renderer.
