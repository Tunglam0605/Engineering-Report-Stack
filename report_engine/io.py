from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .model import Diagnostics, ENTITY_DIRS, Entity, Model, PREFIXES


SUPPORTED_SUFFIXES = {".json", ".yaml", ".yml"}


def read_document(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        value = json.loads(text)
    elif path.suffix.lower() in {".yaml", ".yml"}:
        value = yaml.safe_load(text)
    else:
        raise ValueError(f"unsupported document type: {path.suffix}")

    if not isinstance(value, dict):
        raise ValueError("top-level document must be an object")
    return value


def _report_path(root: Path) -> Path | None:
    for name in ("report.json", "report.yaml", "report.yml"):
        path = root / name
        if path.is_file():
            return path
    return None


def load_raw_model(root: Path) -> tuple[Model, Diagnostics]:
    root = root.resolve()
    diag = Diagnostics()

    report: dict[str, Any] = {}
    report_path = _report_path(root)
    if report_path is None:
        diag.errors.append("missing report.json/report.yaml/report.yml")
    else:
        try:
            report = read_document(report_path)
        except Exception as exc:  # normalized into diagnostics at boundary
            diag.errors.append(f"{report_path.name}: {exc}")

    entities: dict[str, Entity] = {}
    by_kind: dict[str, list[Entity]] = {kind: [] for kind in ENTITY_DIRS}

    for kind, dirname in ENTITY_DIRS.items():
        directory = root / "data" / dirname
        if not directory.exists():
            diag.warnings.append(f"missing optional directory: data/{dirname}")
            continue

        paths = sorted(
            path for path in directory.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
        )
        for path in paths:
            try:
                data = read_document(path)
            except Exception as exc:
                diag.errors.append(f"{path.relative_to(root)}: {exc}")
                continue

            entity_id = data.get("id")
            if not isinstance(entity_id, str) or not entity_id:
                diag.errors.append(
                    f"{path.relative_to(root)}: missing non-empty string id"
                )
                continue

            if entity_id in entities:
                diag.errors.append(
                    f"duplicate id {entity_id}: "
                    f"{entities[entity_id].path.relative_to(root)} and "
                    f"{path.relative_to(root)}"
                )
                continue

            if not entity_id.startswith(PREFIXES[kind]):
                expected = " or ".join(PREFIXES[kind])
                diag.errors.append(
                    f"{path.relative_to(root)}: id {entity_id!r} must start with {expected}"
                )

            entity = Entity(kind=kind, id=entity_id, data=data, path=path)
            entities[entity_id] = entity
            by_kind[kind].append(entity)

    return (
        Model(root=root, report=report, entities=entities, by_kind=by_kind),
        diag,
    )
