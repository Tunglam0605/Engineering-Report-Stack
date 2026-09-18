---
name: report-diagrams
description: Create or update engineering report diagrams as maintainable diagram-as-code. Use for architecture diagrams, block diagrams, data flows, state machines, sequences, traceability graphs, test flows, deployment views, and when a report change requires a logical tree or dependency diagram.
---

# Report Diagrams

Use diagrams to expose structure and flow, not as decoration.

## Diagram selection

- `flowchart`: architecture, data flow, traceability, process.
- `sequenceDiagram`: request/response, test protocol, service interaction.
- `stateDiagram-v2`: device/system states.
- `classDiagram`: domain/entity relationships when useful.
- plain text tree: file/section hierarchy.

## Rules

1. Keep Mermaid source in Git.
2. Use stable IDs/names where possible.
3. Avoid manually drawn duplicated diagrams when one canonical graph can generate the view.
4. Update diagrams in the same change that alters the represented architecture.
5. Separate working diagrams from reader-facing diagrams; not every internal diagram belongs in the report.

For small edits, still inspect the affected tree. Create a full block diagram only if structure or flow changes.
