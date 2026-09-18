# Engineering Report Rules

## Canonical-data rules

1. One fact has one canonical owner.
2. Entity identity is stable even when titles change.
3. Relationships are stored as IDs.
4. Sources and evidence are first-class entities.
5. Generated artifacts are never hand-edited.
6. Derived summaries are generated from canonical facts.

## Traceability contract

A result should be explainable through a chain such as:

```text
source -> requirement -> test -> result -> evidence
```

Not every project must use every entity type, but every displayed conclusion must expose its provenance.

## Change contract

Before changing an existing report entity:

```text
inspect -> trace -> impact -> modify -> validate -> generate -> build -> review
```

## UI contract

UI components may contain rendering logic and design tokens. They may not own:

- standard clauses,
- acceptance criteria,
- test outcomes,
- evidence metadata,
- canonical source URLs,
- engineering requirement text.

Those belong to report data.

## Citation contract

A citation consists of:

```text
source_id + locator
```

A locator can contain clause, page, section, anchor, or other source-specific information. Avoid duplicating the source URL in each requirement.

## Evidence contract

Evidence should record:

- stable ID,
- evidence type,
- producing test/result relationship,
- local file or external locator,
- timestamp when available,
- description,
- optional checksum in later versions.

## Diagram contract

Use diagrams as executable documentation. Prefer Mermaid source checked into Git over raster-only architecture diagrams.

Working diagrams are required for architecture/data-flow changes. Final-report diagrams are included only when they help the intended reader.
