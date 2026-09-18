from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .model import Diagnostics, Model


SCHEMA_FILENAMES = {
    "report": "report.schema.json",
    "source": "source.schema.json",
    "requirement": "requirement.schema.json",
    "test": "test.schema.json",
    "result": "result.schema.json",
    "evidence": "evidence.schema.json",
}


@lru_cache(maxsize=None)
def _load_schema(schema_dir: str, kind: str) -> dict[str, Any]:
    path = Path(schema_dir) / SCHEMA_FILENAMES[kind]
    return json.loads(path.read_text(encoding="utf-8"))


def _validator(schema_dir: Path, kind: str) -> Draft202012Validator:
    schema = _load_schema(str(schema_dir.resolve()), kind)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate_schemas(model: Model, schema_dir: Path) -> Diagnostics:
    diag = Diagnostics()

    if model.report:
        for error in sorted(
            _validator(schema_dir, "report").iter_errors(model.report),
            key=lambda item: list(item.absolute_path),
        ):
            location = ".".join(str(p) for p in error.absolute_path) or "<root>"
            diag.errors.append(f"report schema {location}: {error.message}")

    for kind, entities in model.by_kind.items():
        validator = _validator(schema_dir, kind)
        for entity in entities:
            for error in sorted(
                validator.iter_errors(entity.data),
                key=lambda item: list(item.absolute_path),
            ):
                location = ".".join(str(p) for p in error.absolute_path) or "<root>"
                diag.errors.append(
                    f"{entity.id} schema {location}: {error.message}"
                )

    return diag
