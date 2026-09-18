---
name: report-review
description: Perform the final engineering review of a generated WebUI report or report change. Use after implementation, before release, or when checking traceability, duplicate content, diagrams, citations, evidence, data consistency, build health, and UI regressions.
---

# Report Review

Review the system, not only the page appearance.

## Review order

1. Canonical data and schema/structure.
2. ID uniqueness and reference integrity.
3. Traceability and impact completeness.
4. Sources/citations and locators.
5. Evidence paths/provenance.
6. Generated output freshness.
7. Build result.
8. Visual hierarchy, readability, responsive behavior.
9. Duplicate text/cards/sections.
10. Regression in unrelated sections.

## Severity guidance

- **Blocker:** broken build, invalid references, fabricated/wrong source, missing required evidence, generated output edited instead of canonical data.
- **Major:** duplicated canonical facts, misleading diagram, wrong status propagation, important content unreachable.
- **Minor:** visual inconsistency, wording/spacing issue with no semantic impact.

Do not approve solely because the WebUI looks correct.
