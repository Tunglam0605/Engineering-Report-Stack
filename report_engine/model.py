from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ENTITY_DIRS: dict[str, str] = {
    "source": "sources",
    "requirement": "requirements",
    "test": "tests",
    "result": "results",
    "evidence": "evidence",
}

PREFIXES: dict[str, tuple[str, ...]] = {
    "source": ("STD-", "SRC-"),
    "requirement": ("REQ-",),
    "test": ("TEST-",),
    "result": ("RES-",),
    "evidence": ("EVD-",),
}


@dataclass(frozen=True)
class Entity:
    kind: str
    id: str
    data: dict[str, Any]
    path: Path


@dataclass
class Diagnostics:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def merge(self, other: "Diagnostics") -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


@dataclass
class Model:
    root: Path
    report: dict[str, Any]
    entities: dict[str, Entity]
    by_kind: dict[str, list[Entity]]
    outgoing: dict[str, list[tuple[str, str]]] = field(
        default_factory=lambda: defaultdict(list)
    )
    incoming: dict[str, list[tuple[str, str]]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def add_edge(self, src: str, dst: str, relation: str) -> None:
        self.outgoing[src].append((dst, relation))
        self.incoming[dst].append((src, relation))
