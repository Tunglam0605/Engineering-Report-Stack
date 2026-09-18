---
layout: home

hero:
  name: Engineering Report Stack
  text: Report-as-Code for Engineering
  tagline: Canonical data, traceability, evidence, diagrams, validation, and clean WebUI rendering instead of hand-edited reports.
  actions:
    - theme: brand
      text: Open Demo Report
      link: /generated/demo-report
    - theme: alt
      text: Architecture
      link: /guide/architecture

features:
  - title: Single Source of Truth
    details: Standards, requirements, tests, results and evidence are canonical entities with stable IDs.
  - title: Traceability Graph
    details: Follow input to output and calculate downstream impact before changing report data.
  - title: Diagram-as-Code
    details: Architecture, flows and relationships are maintained as Mermaid source, not disconnected drawings.
  - title: Schema + Semantic Validation
    details: JSON Schema validates JSON/YAML structure; graph checks block broken references, missing evidence, duplicate IDs and inconsistent relationships.
  - title: Renderer Independent
    details: VitePress is the first renderer; the canonical model is designed to support Quarto, Observable and presentation adapters.
  - title: Agent Skills
    details: Reusable report architecture, data modelling, citation, evidence, diagram and review workflows live in the repo.
---

## Data flow

```mermaid
flowchart LR
  A[Authoritative Sources] --> B[Canonical Data]
  B --> C[Traceability Graph]
  C --> D[Validation]
  D --> E[Generated View Model]
  E --> F[VitePress WebUI]
  E -. future .-> G[PDF / Quarto]
  E -. future .-> H[Slidev]
```

## Start locally

```bash
./scripts/bootstrap.sh
npm run report:inspect
npm run docs:dev
```

The generated report is deliberately not the canonical source. Edit the data under a report project's `data/` tree and regenerate.
