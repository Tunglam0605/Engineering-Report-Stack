from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable

from .model import Diagnostics, Entity, Model


def _reference(
    model: Model,
    owner: Entity,
    target_id: object,
    target_kind: str,
    relation: str,
    diag: Diagnostics,
) -> None:
    if not isinstance(target_id, str) or not target_id:
        diag.errors.append(f"{owner.id}: {relation} contains an invalid target id")
        return

    target = model.entities.get(target_id)
    if target is None:
        diag.errors.append(
            f"{owner.id}: {relation} references missing id {target_id}"
        )
        return
    if target.kind != target_kind:
        diag.errors.append(
            f"{owner.id}: {relation} target {target_id} is "
            f"{target.kind}, expected {target_kind}"
        )
        return

    # Direction follows provenance -> derived verification output.
    model.add_edge(target_id, owner.id, relation)


def build_graph(model: Model) -> Diagnostics:
    diag = Diagnostics()

    for requirement in model.by_kind["requirement"]:
        for item in requirement.data.get("source_refs", []):
            if not isinstance(item, dict):
                diag.errors.append(
                    f"{requirement.id}: each source_refs item must be an object"
                )
                continue
            _reference(
                model,
                requirement,
                item.get("source_id"),
                "source",
                "derived-from",
                diag,
            )

    for test in model.by_kind["test"]:
        for requirement_id in test.data.get("verifies", []):
            _reference(
                model,
                test,
                requirement_id,
                "requirement",
                "verified-by",
                diag,
            )

    for result in model.by_kind["result"]:
        _reference(
            model,
            result,
            result.data.get("test_id"),
            "test",
            "produces-result",
            diag,
        )

        evidence_ids = result.data.get("evidence", [])
        if not isinstance(evidence_ids, list):
            continue
        for evidence_id in evidence_ids:
            evidence = model.entities.get(evidence_id)
            if evidence is None:
                diag.errors.append(
                    f"{result.id}: evidence references missing id {evidence_id}"
                )
            elif evidence.kind != "evidence":
                diag.errors.append(
                    f"{result.id}: evidence target {evidence_id} is "
                    f"{evidence.kind}, expected evidence"
                )
            else:
                model.add_edge(result.id, evidence_id, "supported-by")

    for evidence in model.by_kind["evidence"]:
        test_id = evidence.data.get("test_id")
        test = model.entities.get(test_id) if isinstance(test_id, str) else None
        if test is None:
            diag.errors.append(
                f"{evidence.id}: test_id references missing id {test_id}"
            )
        elif test.kind != "test":
            diag.errors.append(f"{evidence.id}: test_id {test_id} is not a test")

        result_id = evidence.data.get("result_id")
        if result_id:
            result = model.entities.get(result_id)
            if result is None:
                diag.errors.append(
                    f"{evidence.id}: result_id references missing id {result_id}"
                )
            elif result.kind != "result":
                diag.errors.append(
                    f"{evidence.id}: result_id {result_id} is not a result"
                )
            elif evidence.id not in (result.data.get("evidence") or []):
                diag.warnings.append(
                    f"{evidence.id}: result_id={result_id} but "
                    f"{result_id}.evidence does not list it"
                )

    _append_completeness_warnings(model, diag)
    _append_cycle_error(model, diag)
    return diag


def _append_completeness_warnings(model: Model, diag: Diagnostics) -> None:
    tested_requirements = {
        requirement_id
        for test in model.by_kind["test"]
        for requirement_id in test.data.get("verifies", [])
        if isinstance(requirement_id, str)
    }
    for requirement in model.by_kind["requirement"]:
        if (
            requirement.id not in tested_requirements
            and requirement.data.get("status") != "deprecated"
        ):
            diag.warnings.append(
                f"{requirement.id}: no test verifies this requirement"
            )

    tests_with_result = {
        result.data.get("test_id")
        for result in model.by_kind["result"]
        if isinstance(result.data.get("test_id"), str)
    }
    for test in model.by_kind["test"]:
        if (
            test.id not in tests_with_result
            and test.data.get("status") == "completed"
        ):
            diag.warnings.append(f"{test.id}: completed test has no result")


def _append_cycle_error(model: Model, diag: Diagnostics) -> None:
    indegree: dict[str, int] = {entity_id: 0 for entity_id in model.entities}
    for src, edges in model.outgoing.items():
        if src not in indegree:
            continue
        for dst, _ in edges:
            indegree[dst] = indegree.get(dst, 0) + 1

    queue = deque(sorted(k for k, value in indegree.items() if value == 0))
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for dst, _ in model.outgoing.get(node, []):
            indegree[dst] -= 1
            if indegree[dst] == 0:
                queue.append(dst)

    if visited != len(indegree):
        diag.errors.append("relationship graph contains a cycle")


def neighbors(
    graph: dict[str, list[tuple[str, str]]], entity_id: str
) -> Iterable[tuple[str, str]]:
    return sorted(graph.get(entity_id, []), key=lambda item: (item[1], item[0]))


def trace_lines(model: Model, entity_id: str) -> list[str]:
    entity = model.entities[entity_id]
    lines = [f"{entity.id} [{entity.kind}] {entity.data.get('title', '')}".rstrip()]
    lines.extend(_tree_lines(model, entity_id, model.incoming, "UPSTREAM"))
    lines.extend(_tree_lines(model, entity_id, model.outgoing, "DOWNSTREAM"))
    return lines


def _tree_lines(
    model: Model,
    start: str,
    graph: dict[str, list[tuple[str, str]]],
    heading: str,
    max_depth: int = 20,
) -> list[str]:
    lines = [heading]
    seen: set[str] = {start}

    def walk(node: str, prefix: str, depth: int) -> None:
        if depth >= max_depth:
            lines.append(prefix + "... depth limit")
            return
        children = list(neighbors(graph, node))
        for index, (child, relation) in enumerate(children):
            last = index == len(children) - 1
            branch = "└─ " if last else "├─ "
            entity = model.entities.get(child)
            label = entity.data.get("title", "") if entity else ""
            lines.append(
                f"{prefix}{branch}{relation}: {child} {label}".rstrip()
            )
            next_prefix = prefix + ("   " if last else "│  ")
            if child in seen:
                lines.append(next_prefix + "└─ (already shown)")
                continue
            seen.add(child)
            walk(child, next_prefix, depth + 1)

    walk(start, "", 0)
    return lines


def impact(model: Model, entity_id: str) -> tuple[list[tuple[int, str, str]], dict[str, int]]:
    queue: deque[tuple[str, int]] = deque([(entity_id, 0)])
    seen = {entity_id}
    impacted: list[tuple[int, str, str]] = []
    counts: dict[str, int] = defaultdict(int)

    while queue:
        node, depth = queue.popleft()
        for child, relation in neighbors(model.outgoing, node):
            if child in seen:
                continue
            seen.add(child)
            impacted.append((depth + 1, child, relation))
            counts[model.entities[child].kind] += 1
            queue.append((child, depth + 1))

    return impacted, counts
