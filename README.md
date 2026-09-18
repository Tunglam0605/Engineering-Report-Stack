# Engineering Report Stack

> **Report-as-Code for traceable engineering documentation.**  
> Build maintainable WebUI engineering reports from canonical data, explicit relationships, deterministic validation, diagrams, citations, test results, and evidence — instead of hand-editing pages.

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](./ROADMAP.md)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](./LICENSE)
[![Renderer](https://img.shields.io/badge/reference%20renderer-VitePress-646CFF.svg)](https://vitepress.dev/)
[![Diagram as Code](https://img.shields.io/badge/diagrams-Mermaid-FF3670.svg)](https://mermaid.js.org/)

Engineering Report Stack treats an engineering report as an **information system and compiler pipeline**, not as a collection of manually maintained HTML/Markdown pages.

A report starts from authoritative sources and canonical engineering entities. The stack validates their relationships, computes traceability and change impact, then generates presentation views such as a WebUI.

---

## Why this exists

Engineering reports often degrade over time because the same requirement, source URL, test result, status, image, or conclusion is copied into many pages. A small engineering change then requires many manual edits, creates inconsistent information, and makes it difficult to answer basic questions such as:

- Where did this requirement come from?
- Which test verifies it?
- Which result and evidence support the conclusion?
- What will be affected if this standard, requirement, or result changes?
- Is the page being edited the source of truth or only a generated view?

Engineering Report Stack solves this by enforcing a simple rule:

> **Change engineering facts once at their canonical source; regenerate every derived view from that source.**

### Core principles

1. **One fact, one canonical owner.**
2. **Stable IDs instead of copied text.**
3. **Relationships are explicit and machine-checkable.**
4. **Generated views are read-only outputs.**
5. **Claims must be traceable to sources, tests, results, or evidence.**
6. **Impact is inspected before an existing entity is changed.**
7. **Architecture and data flow come before UI patches.**
8. **Deterministic tooling handles repeatable work; agents handle reasoning and orchestration.**
9. **The domain model is independent from the renderer.**
10. **A visually correct page is not considered complete if traceability or validation is broken.**

---

## Architecture at a glance

~~~mermaid
flowchart LR
  A[External Sources<br/>Standards / PDFs / APIs / Logs] --> B[Ingest / Normalize]
  B --> C[Canonical Report Data]
  C --> D[Relationship Graph]
  D --> E[Validate / Trace / Impact]
  E --> F[View Model / Generator]
  F --> G[WebUI]
  F --> H[Future PDF]
  F --> I[Future Presentation]
~~~

The dependency direction is intentionally strict:

~~~text
Presentation / Renderer
        ↓
Application / Generator
        ↓
Domain Model
        ↑
Infrastructure / Adapters
~~~

The domain model must not depend on VitePress, Vue, React, Quarto, a database, or a browser.

For the detailed design, see [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## Canonical engineering model

The v0.1 model contains five primary engineering entities:

| Entity | Typical ID | Responsibility |
|---|---|---|
| Source | STD-..., SRC-... | Standard, datasheet, manual, paper, authoritative document |
| Requirement | REQ-... | Engineering requirement or traceable claim |
| Test | TEST-... | Verification procedure |
| Result | RES-... | Verification outcome |
| Evidence | EVD-... | Log, image, measurement, screenshot, file, or artifact supporting a result |

Default trace chain:

~~~mermaid
flowchart LR
  SRC[Source] --> REQ[Requirement]
  REQ --> TEST[Test]
  TEST --> RES[Result]
  RES --> EVD[Evidence]
~~~

Relationships are stored by **stable ID**, not by duplicated titles, URLs, or prose.

A typical report project therefore looks like:

~~~text
my-report/
├── report.json
├── data/
│   ├── sources/
│   ├── requirements/
│   ├── tests/
│   ├── results/
│   └── evidence/
└── evidence/
    ├── images/
    ├── logs/
    └── measurements/
~~~

The canonical engineering facts live in the report project's data tree. Generated Markdown or HTML is a projection of those facts.

---

## End-to-end change flow

Every meaningful change should follow the same path:

~~~mermaid
flowchart TD
  A[Change request] --> B[Inspect project tree]
  B --> C[Identify source of truth]
  C --> D[Trace dependencies]
  D --> E[Impact analysis]
  E --> F[Modify canonical data or reusable code]
  F --> G[Validate]
  G -->|Fail| F
  G -->|Pass| H[Regenerate derived views]
  H --> I[Build WebUI]
  I --> J[Content + visual + regression review]
~~~

In compact form:

~~~text
Input
  -> Canonical Data
  -> Relations
  -> Validation / Trace / Impact
  -> Derived View Model
  -> Generated Output
  -> Review
~~~

Do **not** patch generated HTML/Markdown when a canonical source exists.

---

## Repository layout

~~~text
Engineering-Report-Stack/
├── .codex-plugin/                  # Plugin manifest
├── .github/                        # Repository automation/configuration
├── skills/                         # Portable Agent Skills
│   ├── engineering-web-report/     # Primary orchestration skill
│   ├── report-architecture/
│   ├── report-data-model/
│   ├── report-diagrams/
│   ├── report-citations/
│   ├── report-evidence/
│   └── report-review/
├── schemas/                        # JSON Schema contracts
├── references/                     # Engineering rules + renderer catalogue
├── tools/
│   ├── report_cli.py               # validate / trace / impact / generate
│   └── new_report.py               # create a new report project
├── scripts/
│   ├── bootstrap.sh                # install + test + build bootstrap
│   └── install-codex-skills.sh     # install local Codex skills
├── examples/
│   └── demo-report/                # Working Source -> Requirement -> Test -> Result -> Evidence example
├── tests/                           # Python/unit/skill tests
├── web/                             # Reference VitePress WebUI
├── AGENTS.md                        # Mandatory agent operating rules
├── ARCHITECTURE.md                  # Architecture and invariants
├── PLUGIN.md                        # Plugin/skill integration
├── ROADMAP.md                       # Planned evolution
└── package.json
~~~

---

## Quick start

### Requirements

- Node.js 18+
- npm
- Python 3.10+
- Bash for the helper scripts

Clone the repository:

~~~bash
git clone https://github.com/Tunglam0605/Engineering-Report-Stack.git
cd Engineering-Report-Stack
~~~

### Recommended bootstrap

~~~bash
./scripts/bootstrap.sh
~~~

The bootstrap script checks the required commands, installs Node dependencies, runs the Python test suite, validates/generates the demo report, and builds the WebUI.

Then start the development server:

~~~bash
npm run docs:dev
~~~

### Manual setup

~~~bash
npm ci
npm run test:py
npm run report:check
npm run report:generate
npm run docs:dev
~~~

Production build:

~~~bash
npm run docs:build
~~~

Preview the built documentation:

~~~bash
npm run docs:preview
~~~

---

## Create a new engineering report

Generate a new report project:

~~~bash
python3 tools/new_report.py ../My-Engineering-Report \
  --id RPT-MY-PROJECT \
  --name "My Engineering Report"
~~~

Then place canonical entities under its data directories and preserve real artifacts under its evidence directory.

The intended authoring model is:

~~~text
Author / Agent
     |
     v
Canonical JSON entities
     |
     v
validate -> trace -> impact -> generate
     |
     v
Generated report view
~~~

---

## CLI

The deterministic CLI is the core safety layer for repeatable report operations.

### Validate

~~~bash
python3 tools/report_cli.py validate examples/demo-report
~~~

Checks report structure, IDs, references, and evidence relationships.

### Trace

~~~bash
python3 tools/report_cli.py trace examples/demo-report REQ-EMC-001
~~~

Shows how an entity participates in the report relationship graph.

### Impact

~~~bash
python3 tools/report_cli.py impact examples/demo-report STD-DEMO-001
~~~

Shows downstream entities/views that can be affected by changing an existing canonical entity.

### Generate

~~~bash
python3 tools/report_cli.py generate \
  examples/demo-report \
  web/generated/demo-report.md
~~~

Generates a derived Markdown view from validated canonical data.

### npm shortcuts

| Command | Purpose |
|---|---|
| npm run report:check | Validate the demo report |
| npm run report:trace | Run the reference trace query |
| npm run report:impact | Run the reference impact query |
| npm run report:generate | Regenerate demo Markdown |
| npm run test:py | Run Python tests |
| npm run docs:dev | Generate and run VitePress dev server |
| npm run docs:build | Validate, regenerate, and build WebUI |
| npm test | Run tests and production documentation build |

---

## Agent Skills

Engineering Report Stack is **skill-first**. The primary skill orchestrates the full workflow and delegates focused reasoning to specialized skills.

| Skill | Responsibility |
|---|---|
| engineering-web-report | Full report workflow and completion gate |
| report-architecture | Architecture, boundaries, dependency flow, refactoring |
| report-data-model | Canonical entities, IDs, schemas, relationships |
| report-diagrams | Mermaid and diagram-as-code |
| report-citations | Sources, standards, locators, citation integrity |
| report-evidence | Images, logs, measurements, provenance |
| report-review | Final engineering, traceability, build, and UI review |

Install the skills into local Codex discovery:

~~~bash
./scripts/install-codex-skills.sh
~~~

By default they are copied to:

~~~text
${CODEX_HOME:-~/.codex}/skills
~~~

Restart Codex after installation. Use <code>--force</code> only when intentionally replacing an existing installed copy.

For plugin details, see [PLUGIN.md](./PLUGIN.md).

---

## Using the stack with ChatGPT / Codex / Remote Workstation

The responsibilities are intentionally separated:

~~~mermaid
flowchart TD
  ERS[Engineering Report Stack<br/>rules + architecture + skills + deterministic tools]
  AGENT[ChatGPT / Codex / Engineering Agent]
  RWMCP[Remote Workstation<br/>execution and computer control]
  PROJECT[Target report repository]

  ERS -->|defines HOW work should be performed| AGENT
  AGENT -->|plans / reasons / orchestrates| RWMCP
  RWMCP -->|filesystem / git / build / browser actions| PROJECT
~~~

**Engineering Report Stack is the report methodology and knowledge layer.**  
**Remote Workstation is the execution/control plane.**

Do not move report-domain logic into Remote Workstation.

### Recommended agent bootstrap prompt

When starting a new conversation or agent session with access to this repository, use a prompt similar to:

~~~text
Use Engineering Report Stack as the mandatory framework for this engineering WebUI report.

Repository:
https://github.com/Tunglam0605/Engineering-Report-Stack.git

Before changing the target report, read at minimum:
- AGENTS.md
- ARCHITECTURE.md
- README.md
- PLUGIN.md
- skills/engineering-web-report/SKILL.md

Then read only the specialized skills/references needed for the current task.

Mandatory workflow:
1. Inspect the target project tree.
2. Identify the canonical source of truth.
3. Trace dependencies and determine impact.
4. State Input -> Canonical Data -> Relations -> Derived Views -> Output.
5. Modify canonical data or reusable code only.
6. Never patch generated HTML/Markdown when a canonical source exists.
7. Validate IDs, references, source locators, evidence paths, and statuses.
8. Regenerate derived views.
9. Build the WebUI.
10. Review content, traceability, diagrams, evidence, and regressions before declaring completion.
~~~

The prompt does not replace the repository rules; it tells the agent to load and obey them.

---

## Agent completion gate

Any AI agent modifying a report through this stack must follow [AGENTS.md](./AGENTS.md).

A report change is not complete until:

~~~text
schema / structure valid
+ no duplicate IDs
+ references valid
+ evidence paths valid
+ generated output current
+ build passes
+ visual/content review passes
~~~

For architecture, data-flow, relationship, or report-structure changes, create or update a working diagram before implementation.

---

## Renderer strategy

The canonical data model is **renderer-independent**.

v0.1 uses **VitePress + Mermaid** as the reference implementation because it is lightweight, Markdown-native, version-control friendly, and easy to extend.

The architecture is designed so future rendering adapters can sit behind the same canonical model:

~~~text
Canonical Model
├── VitePressRenderer        # current reference renderer
├── QuartoRenderer           # planned
├── ObservableRenderer       # planned
├── EvidenceRenderer         # planned
└── SlidevRenderer           # planned
~~~

The repository tracks renderer/framework options in [references/framework-catalog.md](./references/framework-catalog.md).

The presence of a framework in the catalogue does **not** mean the adapter is already implemented.

---

## Typical use cases

This stack is intended for engineering information that changes over time and must remain traceable, including:

- system architecture and project handoff reports,
- verification and validation reports,
- requirements-to-test traceability,
- standards/compliance reports,
- firmware/hardware qualification evidence,
- robotics deployment reports,
- runtime/performance evidence,
- commissioning and acceptance reports,
- engineering reports that would otherwise become large manually maintained PowerPoint/Word/Web pages.

It is especially useful when the same engineering entities must appear in multiple views without being copied.

---

## What this project is not

Engineering Report Stack is **not**:

- a drag-and-drop website builder,
- a CMS where engineering facts are authored directly in UI cards,
- a replacement for source standards or original evidence,
- a reason to duplicate data for each page,
- a VitePress-only domain architecture,
- an agent that should bypass deterministic validation,
- a license to treat generated Markdown/HTML as canonical data.

---

## Development rules

When extending the stack itself:

- preserve domain/renderer separation,
- keep transformations deterministic where practical,
- keep modules single-purpose,
- avoid importing or forking large upstream frameworks into this repository,
- reference upstream projects by URL/version/license,
- add validation/tests for reusable transformations,
- keep schema changes backward compatible or version them explicitly,
- update architecture/diagrams in the same change when structure or flow changes.

Run the complete local gate before considering a change ready:

~~~bash
npm test
~~~

---

## Status

Current package/plugin version: **v0.1.0 — Bootstrap**

Implemented:

- canonical JSON entity model,
- Source -> Requirement -> Test -> Result -> Evidence trace chain,
- relationship validation,
- trace and impact analysis,
- report generation,
- VitePress + Mermaid reference WebUI,
- demo report,
- Agent Skills,
- Codex plugin manifest,
- tests and build workflow.

Planned work is tracked in [ROADMAP.md](./ROADMAP.md), including stronger schema validation, reusable report components, evidence/citation hardening, additional report templates, PDF/export paths, and future renderer adapters.

---

## Key documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) — system architecture, invariants, data/change paths.
- [AGENTS.md](./AGENTS.md) — mandatory rules for AI agents.
- [PLUGIN.md](./PLUGIN.md) — plugin/skill installation and Remote Workstation boundary.
- [ROADMAP.md](./ROADMAP.md) — version roadmap.
- [references/report-rules.md](./references/report-rules.md) — report engineering rules.
- [references/framework-catalog.md](./references/framework-catalog.md) — evaluated renderer/framework catalogue.
- [examples/demo-report](./examples/demo-report) — working canonical report example.

---

## License

Licensed under the [Apache License 2.0](./LICENSE).

---

<p align="center">
  <strong>Engineering facts belong in canonical data. Reports are generated views of those facts.</strong>
</p>
