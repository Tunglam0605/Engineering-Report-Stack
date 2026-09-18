---
name: report-data-model
description: Model engineering report data as traceable canonical entities with stable IDs and explicit relationships. Use when adding standards, requirements, tests, results, evidence, metadata, source registries, schemas, or when replacing duplicated page data with a single source of truth.
---

# Report Data Model

## Canonical entities

Start with the minimum useful set:

- Source
- Requirement
- Test
- Result
- Evidence

Extend only when a new domain concept has independent identity/lifecycle.

## Relationship rule

Store relationships as IDs. Example:

```text
STD-... -> REQ-... -> TEST-... -> RES-... -> EVD-...
```

Do not duplicate the source URL inside every requirement or copy requirement text into test records.

## Schema workflow

1. Define entity ownership.
2. Define required/optional fields.
3. Define ID prefix and uniqueness constraints.
4. Define outbound references.
5. Define valid status values.
6. Validate referential integrity.
7. Add migration/versioning when changing persisted schema.

Prefer file-per-entity for small/medium Git-managed reports because it produces small diffs and low merge conflict. JSON and YAML are supported canonical authoring formats; both must satisfy the same JSON Schema and semantic relationship rules.
