# Architecture

Engineering Report Stack separates **engineering facts** from **presentation**.

```mermaid
flowchart TB
  subgraph Inputs
    S[Standards / Datasheets / APIs / Logs]
    E[Evidence Files]
  end

  subgraph Core
    C[Canonical Entities]
    G[Relationship Graph]
    V[Validation]
  end

  subgraph Outputs
    W[WebUI]
    P[PDF]
    D[Presentation]
  end

  S --> C
  E --> C
  C --> G
  G --> V
  V --> W
  V -. adapter .-> P
  V -. adapter .-> D
```

## Dependency contract

```text
source -> requirement -> test -> result -> evidence
```

The CLI exposes this contract through:

```bash
python3 tools/report_cli.py trace examples/demo-report REQ-EMC-001
python3 tools/report_cli.py impact examples/demo-report STD-DEMO-001
```

## Change workflow

```mermaid
flowchart TD
  R[Change request] --> I[Inspect tree]
  I --> T[Trace dependencies]
  T --> M[Modify canonical source]
  M --> V[Validate]
  V -->|fail| M
  V -->|pass| G[Generate]
  G --> B[Build WebUI]
  B --> Q[Review]
```

For the full design contract, see `ARCHITECTURE.md` in the repository root.
