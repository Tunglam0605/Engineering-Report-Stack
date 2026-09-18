# Agent Rules

Use these rules whenever an AI agent creates or modifies an engineering report with this repository.

## Required workflow

1. Inspect the report/project tree.
2. Identify the canonical entity or source of truth.
3. Run or construct a dependency trace for the affected IDs.
4. State the expected inputs, outputs, and affected derived views.
5. Modify canonical data or reusable component code only.
6. Never patch generated HTML/Markdown when a canonical source exists.
7. Validate IDs, references, source locators, evidence paths, and status consistency.
8. Regenerate derived views.
9. Build the WebUI.
10. Review the final output for content, traceability, diagram correctness, and regression.

## Architecture rules

- One fact has one canonical owner.
- Use stable IDs for relationships.
- Do not duplicate source URLs or standard metadata into requirements.
- Do not put engineering facts inside UI components.
- Do not create page-specific data copies to solve rendering problems.
- Do not mix ingest logic, domain logic, and rendering logic in one module.
- Prefer small deterministic tools with single responsibilities.
- Every reusable transformation needs a test or an explicit validation path.

## Diagram rule

For changes that affect architecture, data flow, relationships, or report structure, create/update a working tree/flow diagram before implementation. Only include a diagram in the final report when it helps the report reader.

## Completion gate

A change is not complete until:

```text
schema/structure valid
+ no duplicate IDs
+ references valid
+ evidence paths valid
+ generated output current
+ build passes
+ visual/content review passes
```
