from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..graph import neighbors
from ..model import ENTITY_DIRS, Model

BT = chr(96)
FENCE = BT * 3


def _md(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def _source_ref_text(ref: dict[str, Any]) -> str:
    source_id = ref.get("source_id", "")
    locator = ref.get("locator") or {}
    parts = [source_id]
    if isinstance(locator, dict):
        if locator.get("clause"):
            parts.append(f"clause {locator['clause']}")
        if locator.get("page") is not None:
            parts.append(f"page {locator['page']}")
        if locator.get("section"):
            parts.append(f"section {locator['section']}")
        if locator.get("anchor"):
            parts.append(f"anchor {locator['anchor']}")
    return " · ".join(str(value) for value in parts if value != "")


def mermaid_graph(model: Model) -> str:
    lines = ["flowchart LR"]
    id_map: dict[str, str] = {}
    for index, entity_id in enumerate(sorted(model.entities)):
        node = f"n{index}"
        id_map[entity_id] = node
        entity = model.entities[entity_id]
        title = str(entity.data.get("title", "")).replace('"', "'")
        lines.append(
            f'  {node}["{entity_id}\\n{entity.kind}\\n{title}"]'
        )

    for src in sorted(model.outgoing):
        for dst, relation in neighbors(model.outgoing, src):
            lines.append(f"  {id_map[src]} -->|{relation}| {id_map[dst]}")
    return "\n".join(lines)


def build_view_model(model: Model) -> dict[str, Any]:
    entities = []
    for entity_id in sorted(model.entities):
        entity = model.entities[entity_id]
        data = entity.data
        entities.append(
            {
                "id": entity.id,
                "kind": entity.kind,
                "title": data.get("title", ""),
                "status": data.get("status"),
                "summary": (
                    data.get("statement")
                    or data.get("summary")
                    or data.get("description")
                    or data.get("method")
                    or ""
                ),
                "data": data,
            }
        )

    edges = []
    for src in sorted(model.outgoing):
        for dst, relation in neighbors(model.outgoing, src):
            edges.append({"source": src, "target": dst, "relation": relation})

    return {
        "report": model.report,
        "summary": {
            kind: len(model.by_kind[kind])
            for kind in ENTITY_DIRS
        },
        "entities": entities,
        "edges": edges,
    }


def render_markdown(model: Model, data_url: str) -> str:
    report_name = model.report.get("name", "Engineering Report")
    version = model.report.get("version", "")
    description = model.report.get("description", "")

    out: list[str] = [
        "---",
        f"title: {_md(report_name)}",
        "outline: deep",
        "---",
        "",
        f"# {_md(report_name)}",
        "",
    ]
    if description:
        out.extend([_md(description), ""])

    out.extend(
        [
            f"**Report ID:** {BT}{_md(model.report.get('id'))}{BT}  ",
            f"**Version:** {BT}{_md(version)}{BT}",
            "",
            "## Report overview",
            "",
            f'<ReportSummary data-url="{data_url}" />',
            "",
            "## Explore canonical entities",
            "",
            f'<EntityExplorer data-url="{data_url}" />',
            "",
            "## Traceability graph",
            "",
            FENCE + "mermaid",
            mermaid_graph(model),
            FENCE,
            "",
            "## Sources",
            "",
            "| ID | Title | Type | Edition | Source |",
            "|---|---|---|---|---|",
        ]
    )

    for entity in model.by_kind["source"]:
        data = entity.data
        url = data.get("url")
        link = f"[open]({url})" if url else ""
        out.append(
            f"| {BT}{entity.id}{BT} | {_md(data.get('title'))} | "
            f"{_md(data.get('source_type'))} | {_md(data.get('edition'))} | {link} |"
        )

    out.extend(
        [
            "",
            "## Requirements",
            "",
            "| ID | Requirement | Status | Source locator | Acceptance |",
            "|---|---|---|---|---|",
        ]
    )
    for entity in model.by_kind["requirement"]:
        data = entity.data
        refs = data.get("source_refs") or []
        source_text = "<br>".join(
            _source_ref_text(ref) for ref in refs if isinstance(ref, dict)
        )
        out.append(
            f"| {BT}{entity.id}{BT} | **{_md(data.get('title'))}** — "
            f"{_md(data.get('statement'))} | {_md(data.get('status'))} | "
            f"{_md(source_text)} | {_md(data.get('acceptance'))} |"
        )

    out.extend(
        [
            "",
            "## Verification tests",
            "",
            "| ID | Test | Verifies | Status | Acceptance criteria |",
            "|---|---|---|---|---|",
        ]
    )
    for entity in model.by_kind["test"]:
        data = entity.data
        verifies = ", ".join(
            f"{BT}{item}{BT}" for item in data.get("verifies", [])
        )
        out.append(
            f"| {BT}{entity.id}{BT} | {_md(data.get('title'))} | {verifies} | "
            f"{_md(data.get('status'))} | "
            f"{_md(data.get('acceptance_criteria'))} |"
        )

    out.extend(
        [
            "",
            "## Results",
            "",
            "| Result | Test | Status | Summary | Evidence |",
            "|---|---|---|---|---|",
        ]
    )
    for entity in model.by_kind["result"]:
        data = entity.data
        evidence = ", ".join(
            f"{BT}{item}{BT}" for item in data.get("evidence", [])
        )
        out.append(
            f"| {BT}{entity.id}{BT} | {BT}{_md(data.get('test_id'))}{BT} | "
            f"{_md(data.get('status'))} | {_md(data.get('summary'))} | "
            f"{evidence} |"
        )

    out.extend(["", "## Evidence catalogue", ""])
    for entity in model.by_kind["evidence"]:
        data = entity.data
        locator = data.get("file") or data.get("url") or ""
        out.extend(
            [
                f'<EvidenceCard title="{_md(data.get("title"))}" '
                f'evidence-id="{entity.id}" type="{_md(data.get("type"))}" '
                f'test-id="{_md(data.get("test_id"))}" '
                f'result-id="{_md(data.get("result_id"))}" '
                f'locator="{_md(locator)}">',
                "",
                _md(data.get("description")),
                "",
                "</EvidenceCard>",
                "",
            ]
        )

    out.extend(
        [
            "## Generation flow",
            "",
            FENCE + "mermaid",
            "flowchart LR",
            "  A[JSON / YAML canonical data] --> B[JSON Schema]",
            "  B --> C[Semantic graph validation]",
            "  C --> D[View model]",
            "  D --> E[VitePress components]",
            "  E --> F[Static WebUI]",
            FENCE,
            "",
            "> This page is generated. Edit canonical report data, then regenerate.",
            "",
        ]
    )
    return "\n".join(out)


def write_outputs(
    model: Model,
    markdown_output: Path,
    view_model_output: Path,
    data_url: str,
) -> None:
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    view_model_output.parent.mkdir(parents=True, exist_ok=True)

    markdown_output.write_text(
        render_markdown(model, data_url=data_url),
        encoding="utf-8",
    )
    view_model_output.write_text(
        json.dumps(build_view_model(model), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
