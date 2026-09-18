# Create New Engineering Web Report

Use Engineering Report Stack to create a new report.

## Before implementation

1. Identify report purpose and audience.
2. Choose a report profile:
   - compliance,
   - validation,
   - test,
   - handoff.
3. Identify available source types:
   standards, PDFs, datasheets, logs, measurements, images, APIs, databases.
4. Define the initial canonical entities and ID namespace.
5. Draw the intended input -> canonical data -> relations -> views -> output flow.

## Scaffold

Create the report with `tools/new_report.py` rather than hand-building folders.

Then populate canonical data in this order:

```text
Sources
  -> Requirements
  -> Tests
  -> Results
  -> Evidence
```

Run inspect/validate/trace before adding custom UI.

Only introduce a new UI component when a reusable presentation need cannot be represented by the existing report summary, entity explorer, status, evidence, tables, or Mermaid diagrams.

Do not put canonical facts into Vue/HTML components.
