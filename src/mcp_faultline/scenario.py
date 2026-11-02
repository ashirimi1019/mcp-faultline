"""Scenario model: a deterministic, serialisable sequence of protocol steps.

Completion order is controlled by gates, not sleeps: ``call`` starts a
``gate(tag)`` tool call that blocks inside the target until a ``release`` step
opens it. Out-of-order completion is therefore an exact, replayable property of
the scenario instead of a timing accident.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Literal

from .jsonrpc import IdKey, RequestId, id_key

Op = Literal["call", "cancel", "release", "sync"]


@dataclass(frozen=True)
class Step:
    op: Op
    id: RequestId | None = None
    tag: str | None = None

    def to_json(self) -> dict[str, Any]:
        out: dict[str, Any] = {"op": self.op}
        if self.id is not None:
            out["id"] = self.id
        if self.tag is not None:
            out["tag"] = self.tag
        return out

    @staticmethod
    def from_json(data: dict[str, Any]) -> Step:
        op = data.get("op")
        if op not in ("call", "cancel", "release", "sync"):
            raise ValueError(f"unknown step op {op!r}")
        step = Step(op=op, id=data.get("id"), tag=data.get("tag"))
        if op in ("call", "cancel"):
            if step.id is None:
                raise ValueError(f"{op} step requires an id")
            id_key(step.id)  # type-checks the id (rejects bool/float/null)
        if op in ("call", "release") and not isinstance(step.tag, str):
            raise ValueError(f"{op} step requires a string tag")
        return step

    def describe(self) -> str:
        if self.op == "call":
            return f"call   id={json.dumps(self.id)} gate({self.tag})"
        if self.op == "cancel":
            return f"cancel id={json.dumps(self.id)}"
        if self.op == "release":
            return f"release {self.tag}"
        return "sync"


def call(request_id: RequestId, tag: str) -> Step:
    return Step("call", request_id, tag)


def cancel(request_id: RequestId) -> Step:
    return Step("cancel", request_id)


def release(tag: str) -> Step:
    return Step("release", tag=tag)


SYNC = Step("sync")


@dataclass(frozen=True)
class Scenario:
    name: str
    steps: tuple[Step, ...]
    description: str = ""
    tags: tuple[str, ...] = field(default=())

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "tags": list(self.tags),
            "steps": [s.to_json() for s in self.steps],
        }

    @staticmethod
    def from_json(data: dict[str, Any]) -> Scenario:
        return Scenario(
            name=str(data["name"]),
            description=str(data.get("description", "")),
            tags=tuple(data.get("tags", ())),
            steps=tuple(Step.from_json(s) for s in data["steps"]),
        )

    def normalized(self) -> Scenario:
        """Drop steps that would make the *harness* violate the protocol.

        MCP forbids reusing a request id within a session and cancelling a
        request that was never issued. Minimisation deletes arbitrary steps, so
        this keeps every candidate a legal client trace.
        """
        issued: set[IdKey] = set()
        cancelled: set[IdKey] = set()
        kept: list[Step] = []
        for step in self.steps:
            if step.op == "call":
                assert step.id is not None
                key = id_key(step.id)
                if key in issued:
                    continue
                issued.add(key)
            elif step.op == "cancel":
                assert step.id is not None
                key = id_key(step.id)
                if key not in issued or key in cancelled:
                    continue
                cancelled.add(key)
            kept.append(step)
        return Scenario(self.name, tuple(kept), self.description, self.tags)

    def with_steps(self, steps: tuple[Step, ...], suffix: str = "") -> Scenario:
        return Scenario(self.name + suffix, steps, self.description, self.tags)
