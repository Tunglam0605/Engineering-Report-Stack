# Upstream Framework Catalogue

This project **references and composes** upstream projects; it does not vendor or fork them by default.

| Project | Repository | Primary role in this stack | License | Adoption decision |
|---|---|---|---|---|
| VitePress | https://github.com/vuejs/vitepress | Default WebUI renderer; Markdown + Vue + Vite | MIT | **Use now** |
| Mermaid | https://github.com/mermaid-js/mermaid | Diagram-as-code for architecture/data flow/traceability | MIT | **Use now** |
| Quarto | https://github.com/quarto-dev/quarto-cli | Technical/scientific publishing, citations, cross-references, PDF/book output | MIT | Adapter target |
| Observable Framework | https://github.com/observablehq/framework | Data apps, interactive dashboards/reports, build-time loaders | ISC | Adapter target |
| Evidence | https://github.com/evidence-dev/evidence | SQL + Markdown data reporting as code | MIT | Data-heavy alternative |
| Docusaurus | https://github.com/facebook/docusaurus | Large versioned documentation portals | MIT | Optional portal renderer |
| Slidev | https://github.com/slidevjs/slidev | Markdown/Vue presentation output | MIT | Presentation adapter |
| reveal.js | https://github.com/hakimel/reveal.js | HTML presentation engine | MIT | Lightweight presentation alternative |
| Agent Skills | https://github.com/agentskills/agentskills | Portable `SKILL.md` format | Open standard | **Use now** |
| OpenAI Plugins | https://github.com/openai/plugins | Codex plugin packaging/examples | OpenAI repository terms / per-plugin licenses | **Use manifest model now** |
| JSON Schema | https://github.com/json-schema-org/json-schema-spec | Data-contract validation | Specification repository | **Use schemas now** |

## Why VitePress first

The first renderer needs to be:

- small enough to bootstrap quickly,
- Markdown-native,
- component-extensible,
- static-hostable,
- compatible with diagram-as-code,
- independent of the core data model.

VitePress meets those constraints while keeping the domain model renderer-independent.

## Why not merge upstream source code

Vendoring all upstream repositories would create:

- license and update complexity,
- huge dependency surface,
- duplicated responsibilities,
- difficult security maintenance,
- unclear ownership of modifications.

Instead, this stack keeps a small integration boundary and records upstream role/version/license.

## Selection guide

```text
Need technical publication/citations?  -> Quarto
Need maintainable engineering WebUI?   -> VitePress
Need interactive data/report app?      -> Observable Framework
Need SQL-first analytics reporting?    -> Evidence
Need large documentation portal?       -> Docusaurus
Need presenter/slides mode?            -> Slidev / reveal.js
Need diagrams in any path?             -> Mermaid
```
