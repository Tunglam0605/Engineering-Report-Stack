---
name: report-architecture
description: Design or refactor the architecture of an engineering report before implementation. Use when a report has duplicated data, manual HTML/Markdown edits, unclear module ownership, poor folder structure, or changes that affect data flow, dependencies, renderers, or multiple report sections.
---

# Report Architecture

## Objective

Produce a clean dependency model before code changes.

## Workflow

1. Identify constraints: report size, update frequency, source types, renderer, offline/online deployment, and required outputs.
2. Draw the current section/file tree.
3. Identify canonical data owners and duplicated facts.
4. Draw input -> transformation -> output flow.
5. Define domain entities and stable IDs.
6. Define module boundaries: ingest, domain, graph, validation, view-model, renderer.
7. List impacted modules and migration steps.
8. Only then implement.

## Rules

- Domain data must not depend on UI framework details.
- One responsibility per adapter/service/component.
- Renderer-specific code stays behind a renderer boundary.
- Prefer a small deterministic module over a large agent-only procedure.
- Do not introduce abstractions without a concrete reuse or isolation benefit.

Use Mermaid for architecture/data-flow diagrams when practical.
