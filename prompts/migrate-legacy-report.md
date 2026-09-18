# Migrate Legacy Report

Migrate an existing hand-authored HTML/Markdown/WebUI report into Engineering Report Stack.

Required order:

1. Inspect the complete source/component/data tree.
2. Build a current-state diagram:
   `Input -> Hard-coded/duplicated data -> Components -> Pages -> Output`.
3. Inventory duplicated/hard-coded facts.
4. Classify facts into canonical entities:
   Source, Requirement, Test, Result, Evidence.
5. Assign stable IDs and define relationships.
6. Create a migration map from each legacy location to one canonical owner.
7. Introduce schemas/adapters without changing report meaning.
8. Replace page-local data with generated/view-model data.
9. Validate and build after each migration slice.
10. Remove obsolete duplicated sources only after all references migrate.
11. Review the final report for semantic and visual regression.

Do not rewrite the whole UI first. Migrate data ownership and traceability first.
