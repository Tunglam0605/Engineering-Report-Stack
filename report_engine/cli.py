from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .graph import impact, trace_lines
from .model import ENTITY_DIRS, Diagnostics
from .renderers.vitepress import write_outputs
from .validation import load_and_validate


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_DIR = REPO_ROOT / "schemas"


def print_diagnostics(diag: Diagnostics) -> None:
    for warning in diag.warnings:
        print(f"WARN  {warning}")
    for error in diag.errors:
        print(f"ERROR {error}")


def _model(root: str):
    return load_and_validate(Path(root), DEFAULT_SCHEMA_DIR)


def cmd_validate(args: argparse.Namespace) -> int:
    _, diag = _model(args.root)
    print_diagnostics(diag)
    if diag.ok:
        print(f"OK    validation passed ({len(diag.warnings)} warning(s))")
        return 0
    print(f"FAIL  validation failed ({len(diag.errors)} error(s))")
    return 2


def cmd_inspect(args: argparse.Namespace) -> int:
    model, diag = _model(args.root)
    print_diagnostics(diag)
    if not diag.ok:
        return 2

    print(f"REPORT {model.report.get('id', '')} — {model.report.get('name', '')}")
    print(f"ROOT   {model.root}")
    print("DATA")
    kinds = list(ENTITY_DIRS)
    for index, kind in enumerate(kinds):
        entities = sorted(model.by_kind[kind], key=lambda item: item.id)
        last_kind = index == len(kinds) - 1
        branch = "└─" if last_kind else "├─"
        print(f"{branch} {kind}s ({len(entities)})")
        prefix = "   " if last_kind else "│  "
        for entity_index, entity in enumerate(entities):
            entity_last = entity_index == len(entities) - 1
            entity_branch = "└─" if entity_last else "├─"
            print(
                f"{prefix}{entity_branch} {entity.id} — "
                f"{entity.data.get('title', '')}"
            )

    edge_count = sum(len(edges) for edges in model.outgoing.values())
    print(f"RELATIONS {edge_count}")
    return 0


def cmd_trace(args: argparse.Namespace) -> int:
    model, diag = _model(args.root)
    if not diag.ok:
        print_diagnostics(diag)
        return 2
    if args.entity_id not in model.entities:
        print(f"ERROR unknown entity id: {args.entity_id}")
        return 2
    print("\n".join(trace_lines(model, args.entity_id)))
    return 0


def cmd_impact(args: argparse.Namespace) -> int:
    model, diag = _model(args.root)
    if not diag.ok:
        print_diagnostics(diag)
        return 2
    if args.entity_id not in model.entities:
        print(f"ERROR unknown entity id: {args.entity_id}")
        return 2

    impacted, counts = impact(model, args.entity_id)
    print(f"CHANGE ROOT: {args.entity_id}")
    if not impacted:
        print("No downstream entities.")
        return 0

    for depth, entity_id, relation in impacted:
        entity = model.entities[entity_id]
        print(
            f"{'  ' * depth}└─ {relation}: {entity_id} [{entity.kind}]"
        )

    print("\nSUMMARY")
    for kind in ENTITY_DIRS:
        if counts.get(kind):
            print(f"{kind:12} {counts[kind]}")
    print(f"{'total':12} {len(impacted)}")
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    model, diag = _model(args.root)
    print_diagnostics(diag)
    if not diag.ok:
        print("FAIL  generation blocked because validation failed")
        return 2

    markdown_output = Path(args.output).resolve()
    view_model_output = Path(args.view_model_output).resolve()
    write_outputs(
        model,
        markdown_output=markdown_output,
        view_model_output=view_model_output,
        data_url=args.data_url,
    )
    print(f"OK    generated {markdown_output}")
    print(f"OK    generated {view_model_output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="engineering-report",
        description="Engineering Report Stack deterministic CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="validate canonical report data")
    validate.add_argument("root")
    validate.set_defaults(func=cmd_validate)

    inspect_cmd = sub.add_parser("inspect", help="show canonical report/entity tree")
    inspect_cmd.add_argument("root")
    inspect_cmd.set_defaults(func=cmd_inspect)

    trace = sub.add_parser("trace", help="show upstream/downstream relationships")
    trace.add_argument("root")
    trace.add_argument("entity_id")
    trace.set_defaults(func=cmd_trace)

    impact_cmd = sub.add_parser("impact", help="show downstream change impact")
    impact_cmd.add_argument("root")
    impact_cmd.add_argument("entity_id")
    impact_cmd.set_defaults(func=cmd_impact)

    generate = sub.add_parser("generate", help="generate VitePress outputs")
    generate.add_argument("root")
    generate.add_argument("output")
    generate.add_argument(
        "--view-model-output",
        default="web/public/generated/report.json",
    )
    generate.add_argument(
        "--data-url",
        default="./report.json",
    )
    generate.set_defaults(func=cmd_generate)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
