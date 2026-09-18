---
name: report-citations
description: Add, refactor, or validate citations and authoritative sources in engineering reports. Use for standards, IEC/ISO references, datasheets, papers, manuals, external claims, clause/page locators, source registries, and broken or duplicated source links.
---

# Report Citations

Treat sources as first-class entities.

## Canonical citation

A citation should resolve through:

```text
source_id + locator
```

The source entity owns publisher/title/version/URL. A locator owns clause/page/section/anchor relevant to the referencing claim.

## Workflow

1. Prefer authoritative/primary sources.
2. Record source metadata once.
3. Reference the source by stable ID.
4. Store clause/page/section separately from the base URL.
5. Verify the locator targets the intended evidence, not merely the document landing page.
6. Mark proposed interpretations separately from quoted/verified requirements.
7. Check for duplicated or broken links after modification.

Never fabricate a clause, page, edition, or source location.
