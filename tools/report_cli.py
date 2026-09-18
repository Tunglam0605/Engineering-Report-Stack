#!/usr/bin/env python3
"""Engineering Report Stack deterministic CLI.

Commands:
- validate: structural and referential integrity checks
- trace: upstream/downstream dependency inspection
- impact: downstream change impact
- generate: canonical model to VitePress-compatible Markdown

The v0.1 CLI uses only the Python standard library. JSON Schema files under
schemas are the formal contracts; this CLI enforces key invariants and graph
semantics without requiring a Python dependency install.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

BT = chr(96)
FENCE = BT * 3

ENTITY_DIRS = {
    "source": "sources",
    "requirement": "requirements",
    "test": "tests",
    "result": "results",
    "evidence": "evidence",
}

PREFIXES = {
    "source": ("STD-", "SRC-"),
    "requirement": ("REQ-",),
    "test": ("TEST-",),
    "result": ("RES-",),
    "evidence": ("EVD-",),
}

STATUS_VALUES = {
    "requirement": {"proposed", "verified", "accepted", "deprecated"},
    "test": {"planned", "ready", "running", "completed", "deprecated"},
    "result": {"pass", "fail", "partial", "not-tested"},
}


@dataclass(frozen=True)
class Entity:
    kind: str
    id: str
    data: dict[str, Any]
    path: Path


@dataclass
class Model:
    root: Path
    report: dict[str, Any]
    entities: dict[str, Entity]
    by_kind: dict[str, list[Entity]]
    outgoing: dict[str, list[tuple[str, str]]]
    incoming: dict[str, list[tuple[str, str]]]


@dataclass
class Diagnostics:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("top-level JSON value must be an object")
    return value


def load_model(root: Path) -> tuple[Model, Diagnostics]:
    errors: list[str] = []
    warnings: list[str] = []

    report_path = root / "report.json"
    report: dict[str, Any] = {}
    if not report_path.is_file():
        errors.append("missing report.json")
    else:
        try:
            report = read_json(report_path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"report.json: {exc}")

    entities: dict[str, Entity] = {}
    by_kind: dict[str, list[Entity]] = {kind: [] for kind in ENTITY_DIRS}

    for kind, dirname in ENTITY_DIRS.items():
        directory = root / "data" / dirname
        if not directory.exists():
            warnings.append(f"missing optional directory: data/{dirname}")
            continue

        for path in sorted(directory.glob("*.json")):
            try:
                data = read_json(path)
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                errors.append(f"{path.relative_to(root)}: {exc}")
                continue

            entity_id = data.get("id")
            if not isinstance(entity_id, str) or not entity_id:
                errors.append(f"{path.relative_to(root)}: missing non-empty string id")
                continue

            if entity_id in entities:
                errors.append(
                    f"duplicate id {entity_id}: "
                    f"{entities[entity_id].path.relative_to(root)} and {path.relative_to(root)}"
                )
                continue

            if not entity_id.startswith(PREFIXES[kind]):
                expected = " or ".join(PREFIXES[kind])
                errors.append(
                    f"{path.relative_to(root)}: id {entity_id!r} must start with {expected}"
                )

            entity = Entity(kind=kind, id=entity_id, data=data, path=path)
            entities[entity_id] = entity
            by_kind[kind].append(entity)

    model = Model(
        root=root,
        report=report,
        entities=entities,
        by_kind=by_kind,
        outgoing=defaultdict(list),
        incoming=defaultdict(list),
    )

    _validate_report(model, errors, warnings)
    _build_and_validate_graph(model, errors, warnings)

    return model, Diagnostics(errors=errors, warnings=warnings)


def _require_text(entity: Entity, field: str, errors: list[str]) -> None:
    value = entity.data.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{entity.id}: {field} must be a non-empty string")


def _validate_report(model: Model, errors: list[str], warnings: list[str]) -> None:
    report = model.report
    if report:
        for field in ("id", "name", "version"):
            value = report.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"report.json: {field} must be a non-empty string")
        rid = report.get("id")
        if isinstance(rid, str) and not rid.startswith("RPT-"):
            errors.append("report.json: id must start with RPT-")

    for kind, items in model.by_kind.items():
        for entity in items:
            _require_text(entity, "title", errors)

            if kind == "source":
                _require_text(entity, "source_type", errors)

            elif kind == "requirement":
                _require_text(entity, "statement", errors)
                status = entity.data.get("status")
                if status not in STATUS_VALUES[kind]:
                    errors.append(
                        f"{entity.id}: invalid status {status!r}; "
                        f"expected one of {sorted(STATUS_VALUES[kind])}"
                    )
                refs = entity.data.get("source_refs")
                if not isinstance(refs, list):
                    errors.append(f"{entity.id}: source_refs must be an array")

            elif kind == "test":
                _require_text(entity, "method", errors)
                status = entity.data.get("status")
                if status not in STATUS_VALUES[kind]:
                    errors.append(
                        f"{entity.id}: invalid status {status!r}; "
                        f"expected one of {sorted(STATUS_VALUES[kind])}"
                    )
                verifies = entity.data.get("verifies")
                if not isinstance(verifies, list) or not verifies:
                    errors.append(f"{entity.id}: verifies must be a non-empty array")

            elif kind == "result":
                status = entity.data.get("status")
                if status not in STATUS_VALUES[kind]:
                    errors.append(
                        f"{entity.id}: invalid status {status!r}; "
                        f"expected one of {sorted(STATUS_VALUES[kind])}"
                    )
                if not isinstance(entity.data.get("test_id"), str):
                    errors.append(f"{entity.id}: test_id must be a string")

            elif kind == "evidence":
                _require_text(entity, "type", errors)
                _require_text(entity, "description", errors)
                if not isinstance(entity.data.get("test_id"), str):
                    errors.append(f"{entity.id}: test_id must be a string")
                file_value = entity.data.get("file")
                url_value = entity.data.get("url")
                if not file_value and not url_value:
                    errors.append(f"{entity.id}: evidence requires file or url")
                if isinstance(file_value, str):
                    evidence_path = (model.root / file_value).resolve()
                    try:
                        evidence_path.relative_to(model.root.resolve())
                    except ValueError:
                        errors.append(f"{entity.id}: evidence file escapes report root: {file_value}")
                    else:
                        if not evidence_path.exists():
                            errors.append(f"{entity.id}: evidence file not found: {file_value}")


def _add_edge(model: Model, src: str, dst: str, relation: str) -> None:
    model.outgoing[src].append((dst, relation))
    model.incoming[dst].append((src, relation))


def _ref(
    model: Model,
    src_entity: Entity,
    target_id: Any,
    target_kind: str,
    relation: str,
    errors: list[str],
) -> None:
    if not isinstance(target_id, str) or not target_id:
        errors.append(f"{src_entity.id}: {relation} contains an invalid target id")
        return

    target = model.entities.get(target_id)
    if target is None:
        errors.append(f"{src_entity.id}: {relation} references missing id {target_id}")
        return
    if target.kind != target_kind:
        errors.append(
            f"{src_entity.id}: {relation} target {target_id} is {target.kind}, expected {target_kind}"
        )
        return

    _add_edge(model, target_id, src_entity.id, relation)


def _build_and_validate_graph(
    model: Model, errors: list[str], warnings: list[str]
) -> None:
    for req in model.by_kind["requirement"]:
        refs = req.data.get("source_refs", [])
        if isinstance(refs, list):
            for item in refs:
                if not isinstance(item, dict):
                    errors.append(f"{req.id}: each source_refs item must be an object")
                    continue
                _ref(
                    model,
                    req,
                    item.get("source_id"),
                    "source",
                    "derived-from",
                    errors,
                )

    for test in model.by_kind["test"]:
        verifies = test.data.get("verifies", [])
        if isinstance(verifies, list):
            for requirement_id in verifies:
                _ref(
                    model,
                    test,
                    requirement_id,
                    "requirement",
                    "verified-by",
                    errors,
                )

    for result in model.by_kind["result"]:
        _ref(
            model,
            result,
            result.data.get("test_id"),
            "test",
            "produces-result",
            errors,
        )

        evidence_ids = result.data.get("evidence", [])
        if evidence_ids is None:
            evidence_ids = []
        if not isinstance(evidence_ids, list):
            errors.append(f"{result.id}: evidence must be an array")
        else:
            for evidence_id in evidence_ids:
                evidence = model.entities.get(evidence_id)
                if evidence is None:
                    errors.append(f"{result.id}: evidence references missing id {evidence_id}")
                elif evidence.kind != "evidence":
                    errors.append(
                        f"{result.id}: evidence target {evidence_id} is {evidence.kind}, expected evidence"
                    )
                else:
                    _add_edge(model, result.id, evidence_id, "supported-by")

    for evidence in model.by_kind["evidence"]:
        test_id = evidence.data.get("test_id")
        target = model.entities.get(test_id) if isinstance(test_id, str) else None
        if target is None:
            errors.append(f"{evidence.id}: test_id references missing id {test_id}")
        elif target.kind != "test":
            errors.append(f"{evidence.id}: test_id {test_id} is not a test")

        result_id = evidence.data.get("result_id")
        if result_id:
            result = model.entities.get(result_id)
            if result is None:
                errors.append(f"{evidence.id}: result_id references missing id {result_id}")
            elif result.kind != "result":
                errors.append(f"{evidence.id}: result_id {result_id} is not a result")
            else:
                listed = result.data.get("evidence", [])
                if isinstance(listed, list) and evidence.id not in listed:
                    warnings.append(
                        f"{evidence.id}: result_id={result_id} but {result_id}.evidence does not list it"
                    )

    tested_requirements = {
        requirement_id
        for test in model.by_kind["test"]
        for requirement_id in test.data.get("verifies", [])
        if isinstance(requirement_id, str)
    }
    for req in model.by_kind["requirement"]:
        if req.id not in tested_requirements and req.data.get("status") != "deprecated":
            warnings.append(f"{req.id}: no test verifies this requirement")

    tests_with_result = {
        result.data.get("test_id")
        for result in model.by_kind["result"]
        if isinstance(result.data.get("test_id"), str)
    }
    for test in model.by_kind["test"]:
        if test.id not in tests_with_result and test.data.get("status") == "completed":
            warnings.append(f"{test.id}: completed test has no result")


def print_diagnostics(diag: Diagnostics) -> None:
    for warning in diag.warnings:
        print(f"WARN  {warning}")
    for error in diag.errors:
        print(f"ERROR {error}")


def cmd_validate(args: argparse.Namespace) -> int:
    _, diag = load_model(Path(args.root).resolve())
    print_diagnostics(diag)
    if diag.ok:
        print(f"OK    validation passed ({len(diag.warnings)} warning(s))")
        return 0
    print(f"FAIL  validation failed ({len(diag.errors)} error(s))")
    return 2


def _neighbors(
    graph: dict[str, list[tuple[str, str]]], entity_id: str
) -> Iterable[tuple[str, str]]:
    return sorted(graph.get(entity_id, []), key=lambda item: (item[1], item[0]))


def _print_tree(
    model: Model,
    start: str,
    graph: dict[str, list[tuple[str, str]]],
    direction: str,
    max_depth: int = 20,
) -> None:
    print(direction)
    seen: set[str] = {start}

    def walk(node: str, prefix: str, depth: int) -> None:
        if depth >= max_depth:
            print(prefix + "... depth limit")
            return

        children = list(_neighbors(graph, node))
        for index, (child, relation) in enumerate(children):
            last = index == len(children) - 1
            branch = "└─ " if last else "├─ "
            entity = model.entities.get(child)
            label = entity.data.get("title", "") if entity else ""
            print(f"{prefix}{branch}{relation}: {child} {label}".rstrip())

            next_prefix = prefix + ("   " if last else "│  ")
            if child in seen:
                print(next_prefix + "└─ (already shown)")
                continue
            seen.add(child)
            walk(child, next_prefix, depth + 1)

    walk(start, "", 0)


def cmd_trace(args: argparse.Namespace) -> int:
    model, diag = load_model(Path(args.root).resolve())
    if not diag.ok:
        print_diagnostics(diag)
        return 2

    entity = model.entities.get(args.entity_id)
    if entity is None:
        print(f"ERROR unknown entity id: {args.entity_id}")
        return 2

    print(f"{entity.id} [{entity.kind}] {entity.data.get('title', '')}")
    _print_tree(model, entity.id, model.incoming, "UPSTREAM")
    _print_tree(model, entity.id, model.outgoing, "DOWNSTREAM")
    return 0


def cmd_impact(args: argparse.Namespace) -> int:
    model, diag = load_model(Path(args.root).resolve())
    if not diag.ok:
        print_diagnostics(diag)
        return 2

    if args.entity_id not in model.entities:
        print(f"ERROR unknown entity id: {args.entity_id}")
        return 2

    queue: deque[tuple[str, int]] = deque([(args.entity_id, 0)])
    seen = {args.entity_id}
    impacted: list[tuple[int, str, str]] = []

    while queue:
        node, depth = queue.popleft()
        for child, relation in _neighbors(model.outgoing, node):
            if child in seen:
                continue
            seen.add(child)
            impacted.append((depth + 1, child, relation))
            queue.append((child, depth + 1))

    print(f"CHANGE ROOT: {args.entity_id}")
    if not impacted:
        print("No downstream entities.")
        return 0

    counts: dict[str, int] = defaultdict(int)
    for depth, entity_id, relation in impacted:
        entity = model.entities[entity_id]
        counts[entity.kind] += 1
        indent = "  " * depth
        print(f"{indent}└─ {relation}: {entity_id} [{entity.kind}]")

    print("\nSUMMARY")
    for kind in ENTITY_DIRS:
        if counts[kind]:
            print(f"{kind:12} {counts[kind]}")
    print(f"{'total':12} {len(impacted)}")
    return 0


def _md(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def _source_ref_text(ref: dict[str, Any]) -> str:
    source_id = ref.get("source_id", "")
    locator = ref.get("locator") or {}
    pieces = [source_id]
    if isinstance(locator, dict):
        if locator.get("clause"):
            pieces.append(f"clause {locator['clause']}")
        if locator.get("page") is not None:
            pieces.append(f"page {locator['page']}")
        if locator.get("section"):
            pieces.append(f"section {locator['section']}")
    return " · ".join(str(x) for x in pieces if x != "")


def _mermaid_graph(model: Model) -> str:
    lines = ["flowchart LR"]
    id_map: dict[str, str] = {}
    for index, entity_id in enumerate(sorted(model.entities)):
        node = f"n{index}"
        id_map[entity_id] = node
        kind = model.entities[entity_id].kind
        lines.append(f'  {node}["{entity_id}\\n{kind}"]')

    for src in sorted(model.outgoing):
        for dst, relation in _neighbors(model.outgoing, src):
            lines.append(f"  {id_map[src]} -->|{relation}| {id_map[dst]}")
    return "\n".join(lines)


def render_markdown(model: Model) -> str:
    report_name = model.report.get("name", "Engineering Report")
    report_version = model.report.get("version", "")
    report_description = model.report.get("description", "")

    out: list[str] = [
        "---",
        f"title: {_md(report_name)}",
        "outline: deep",
        "---",
        "",
        f"# {_md(report_name)}",
        "",
    ]

    if report_description:
        out.extend([_md(report_description), ""])

    out.extend(
        [
            f"**Report ID:** {BT}{_md(model.report.get('id'))}{BT}  ",
            f"**Version:** {BT}{_md(report_version)}{BT}",
            "",
            "## Model summary",
            "",
            "| Entity | Count |",
            "|---|---:|",
        ]
    )
    for kind in ENTITY_DIRS:
        out.append(f"| {kind.title()} | {len(model.by_kind[kind])} |")

    out.extend(
        [
            "",
            "## Traceability graph",
            "",
            FENCE + "mermaid",
            _mermaid_graph(model),
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
            f"| {BT}{entity.id}{BT} | **{_md(data.get('title'))}** — {_md(data.get('statement'))} | "
            f"{_md(data.get('status'))} | {_md(source_text)} | {_md(data.get('acceptance'))} |"
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
        verifies = ", ".join(f"{BT}{x}{BT}" for x in data.get("verifies", []))
        out.append(
            f"| {BT}{entity.id}{BT} | {_md(data.get('title'))} | {verifies} | "
            f"{_md(data.get('status'))} | {_md(data.get('acceptance_criteria'))} |"
        )

    out.extend(
        [
            "",
            "## Results and evidence",
            "",
            "| Result | Test | Status | Summary | Evidence |",
            "|---|---|---|---|---|",
        ]
    )
    for entity in model.by_kind["result"]:
        data = entity.data
        evidence = ", ".join(f"{BT}{x}{BT}" for x in data.get("evidence", []))
        out.append(
            f"| {BT}{entity.id}{BT} | {BT}{_md(data.get('test_id'))}{BT} | {_md(data.get('status'))} | "
            f"{_md(data.get('summary'))} | {evidence} |"
        )

    out.extend(["", "### Evidence catalogue", ""])
    for entity in model.by_kind["evidence"]:
        data = entity.data
        locator = data.get("file") or data.get("url") or ""
        out.extend(
            [
                f"#### {entity.id} — {_md(data.get('title'))}",
                "",
                f"- **Type:** {_md(data.get('type'))}",
                f"- **Test:** {BT}{_md(data.get('test_id'))}{BT}",
                f"- **Result:** {BT}{_md(data.get('result_id'))}{BT}" if data.get("result_id") else "",
                f"- **Locator:** {BT}{_md(locator)}{BT}",
                f"- **Description:** {_md(data.get('description'))}",
                "",
            ]
        )

    out.extend(
        [
            "## Data flow",
            "",
            FENCE + "mermaid",
            "flowchart LR",
            "  A[Canonical JSON] --> B[Validate]",
            "  B --> C[Relationship Graph]",
            "  C --> D[Generated Markdown]",
            "  D --> E[VitePress WebUI]",
            FENCE,
            "",
            "> This page is generated. Edit canonical report data, then regenerate.",
            "",
        ]
    )

    return "\n".join(line for line in out if line is not None)


def cmd_generate(args: argparse.Namespace) -> int:
    model, diag = load_model(Path(args.root).resolve())
    print_diagnostics(diag)
    if not diag.ok:
        print("FAIL  generation blocked because validation failed")
        return 2

    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_markdown(model), encoding="utf-8")
    print(f"OK    generated {output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="report_cli.py",
        description="Engineering Report Stack deterministic CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="validate canonical report data")
    validate.add_argument("root", help="report project root")
    validate.set_defaults(func=cmd_validate)

    trace = sub.add_parser("trace", help="show upstream and downstream relationships")
    trace.add_argument("root", help="report project root")
    trace.add_argument("entity_id", help="stable entity ID")
    trace.set_defaults(func=cmd_trace)

    impact = sub.add_parser("impact", help="show downstream impact of changing an entity")
    impact.add_argument("root", help="report project root")
    impact.add_argument("entity_id", help="stable entity ID")
    impact.set_defaults(func=cmd_impact)

    generate = sub.add_parser("generate", help="generate Markdown from canonical data")
    generate.add_argument("root", help="report project root")
    generate.add_argument("output", help="output Markdown path")
    generate.set_defaults(func=cmd_generate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
