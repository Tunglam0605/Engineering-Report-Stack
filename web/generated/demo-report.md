---
title: Engineering Report Stack Demo
outline: deep
---

# Engineering Report Stack Demo

Minimal traceable report demonstrating one source-to-evidence engineering chain.

**Report ID:** `RPT-DEMO-001`  
**Version:** `0.1.0`

## Model summary

| Entity | Count |
|---|---:|
| Source | 1 |
| Requirement | 1 |
| Test | 1 |
| Result | 1 |
| Evidence | 1 |

## Traceability graph

```mermaid
flowchart LR
  n0["EVD-EMC-001\nevidence"]
  n1["REQ-EMC-001\nrequirement"]
  n2["RES-EMC-001\nresult"]
  n3["STD-DEMO-001\nsource"]
  n4["TEST-EMC-001\ntest"]
  n1 -->|verified-by| n4
  n2 -->|supported-by| n0
  n3 -->|derived-from| n1
  n4 -->|produces-result| n2
```

## Sources

| ID | Title | Type | Edition | Source |
|---|---|---|---|---|
| `STD-DEMO-001` | Demo Engineering Standard | standard | 1.0 | [open](https://github.com/Tunglam0605/Engineering-Report-Stack) |

## Requirements

| ID | Requirement | Status | Source locator | Acceptance |
|---|---|---|---|---|
| `REQ-EMC-001` | **Transient immunity requirement** — The controller shall remain operational during the defined transient-immunity verification scenario. | proposed | STD-DEMO-001 · page 1 · section Demo clause | No reset, unsafe output, or loss of required communication during the test window. |

## Verification tests

| ID | Test | Verifies | Status | Acceptance criteria |
|---|---|---|---|---|
| `TEST-EMC-001` | Controller transient-immunity bench test | `REQ-EMC-001` | completed | No reset, unsafe output, or persistent communication loss. |

## Results and evidence

| Result | Test | Status | Summary | Evidence |
|---|---|---|---|---|
| `RES-EMC-001` | `TEST-EMC-001` | pass | The demo controller state remained operational and the monitored communication state recovered without manual intervention. | `EVD-EMC-001` |

### Evidence catalogue

#### EVD-EMC-001 — Demo runtime log

- **Type:** log
- **Test:** `TEST-EMC-001`
- **Result:** `RES-EMC-001`
- **Locator:** `evidence/demo-runtime-log.txt`
- **Description:** Illustrative evidence artifact used to verify end-to-end report traceability.

## Data flow

```mermaid
flowchart LR
  A[Canonical JSON] --> B[Validate]
  B --> C[Relationship Graph]
  C --> D[Generated Markdown]
  D --> E[VitePress WebUI]
```

> This page is generated. Edit canonical report data, then regenerate.
