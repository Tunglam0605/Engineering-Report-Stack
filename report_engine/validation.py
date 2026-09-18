from __future__ import annotations

from pathlib import Path

from .graph import build_graph
from .io import load_raw_model
from .model import Diagnostics, Model
from .schema_validation import validate_schemas


def load_and_validate(
    root: Path,
    schema_dir: Path,
) -> tuple[Model, Diagnostics]:
    model, diag = load_raw_model(root)

    # Schema validation only runs on documents that parsed successfully.
    diag.merge(validate_schemas(model, schema_dir))
    diag.merge(_validate_evidence_paths(model))
    diag.merge(build_graph(model))
    return model, diag


def _validate_evidence_paths(model: Model) -> Diagnostics:
    diag = Diagnostics()
    report_root = model.root.resolve()

    for evidence in model.by_kind["evidence"]:
        file_value = evidence.data.get("file")
        if not isinstance(file_value, str):
            continue

        target = (report_root / file_value).resolve()
        try:
            target.relative_to(report_root)
        except ValueError:
            diag.errors.append(
                f"{evidence.id}: evidence file escapes report root: {file_value}"
            )
            continue

        if not target.exists():
            diag.errors.append(
                f"{evidence.id}: evidence file not found: {file_value}"
            )

    return diag
