# Roadmap

## v0.1 — Bootstrap ✅

- Portable Agent Skills.
- Codex plugin manifest.
- Canonical JSON entity model.
- Traceability graph.
- `validate`, `trace`, `impact`, `generate` CLI.
- VitePress + Mermaid WebUI shell.
- Working demo report.
- Upstream framework catalogue.

## v0.2 — Engineering Report SDK ✅

- Core refactored into SRP-oriented Python package:
  - IO/adapters,
  - schema validation,
  - graph semantics,
  - renderer,
  - CLI.
- JSON Schema 2020-12 validation.
- YAML + JSON canonical authoring.
- Interactive generated view model.
- Reusable Vue components:
  - report summary,
  - entity explorer,
  - status badge,
  - evidence card.
- Search/filter by entity ID, content, type, and status.
- Report profiles:
  - compliance,
  - validation,
  - test,
  - handoff.
- Cross-platform Python launcher for npm workflows.
- Python package/CLI installation via `pyproject.toml`.
- Unit/integration tests for schema, YAML, graph, scaffolding, generation, and skills.
- CI installs both Python and WebUI dependencies before validation/build.

## v0.3 — Evidence and citation hardening

- Evidence manifest hashing.
- Broken citation/link checks.
- Source locator validation.
- Page/clause deep-link metadata.
- Evidence gallery and provenance viewer.
- Source/evidence health dashboard.
- PDF export path.
- Release/version metadata embedded into report output.

## v0.4 — Multi-renderer

- Quarto adapter.
- Observable data-report adapter.
- Slidev presentation adapter.
- Shared renderer-neutral view-model contract.

## v0.5 — Plugin distribution

- Plugin install/eval workflow.
- Stable plugin metadata.
- Skill eval fixtures.
- Marketplace packaging.
- Optional Report MCP only if deterministic CLI + skills are insufficient.
