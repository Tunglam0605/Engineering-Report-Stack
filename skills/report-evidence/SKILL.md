---
name: report-evidence
description: Structure, import, and review engineering test evidence for WebUI reports. Use for screenshots, photos, logs, CSV measurements, oscilloscope captures, videos, runtime metrics, test artifacts, provenance metadata, and linking evidence to tests/results.
---

# Report Evidence

Evidence is data, not a loose image pasted into a page.

## Evidence record

Capture at minimum:

- stable evidence ID,
- evidence type,
- producing/related test,
- path or external locator,
- concise description.

When available, also capture timestamp, device, environment, build/firmware version, and checksum.

## Workflow

1. Identify the test/result the evidence supports.
2. Preserve the original artifact.
3. Add canonical metadata.
4. Validate the file/locator exists.
5. Render through a reusable evidence component/view.
6. Keep captions factual and traceable.
7. Do not reuse the same artifact under conflicting meanings.

Prefer derived thumbnails/previews over modifying the original evidence file.
