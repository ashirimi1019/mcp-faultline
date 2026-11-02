"""Deterministic fault injection between the harness and a target.

Faults wrap a :class:`~mcp_faultline.transports.Connection` and rewrite what
the harness *receives*. Applied to a correct target they emulate a defective
one, which proves that the oracle actually detects each defect class (a
negative control) independently of any particular implementation.

Every fault is a pure function of the message stream plus an explicit seed,
so a faulty run replays identically.
"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from .transports import Connection, Inbound

FAULTS = ("coerce-response-ids", "duplicate-responses", "drop-one-response", "stale-result", "hold-and-reverse")


def _is_gate_response(msg: object) -> bool:
    if not isinstance(msg, dict) or "method" in msg or "id" not in msg:
        return False
    rid = msg.get("id")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    return not (isinstance(rid, str) and rid.startswith("fl-"))


@dataclass
class FaultyConnection:
    inner: Connection
    fault: str
    seed: int = 0
    _pending: deque[Inbound] = field(default_factory=lambda: deque[Inbound]())
    _held: list[Inbound] = field(default_factory=lambda: list[Inbound]())
    _seen: int = 0
    _victim: int = -1
    _previous: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.fault not in FAULTS:
            raise ValueError(f"unknown fault {self.fault!r}; choose from {FAULTS}")
        self._victim = self.seed % 2  # which gate response (0th or 1st) to drop

    def send(self, message: dict[str, Any]) -> str:
        return self.inner.send(message)

    def close(self) -> None:
        self.inner.close()

    def diagnostics(self) -> str:
        return f"[fault={self.fault} seed={self.seed}]\n" + self.inner.diagnostics()

    def recv(self, timeout: float) -> Inbound | None:
        if self._pending:
            return self._pending.popleft()
        item = self.inner.recv(timeout)
        if item is None:
            if self._held:  # flush held messages once the target goes quiet
                self._pending.extend(reversed(self._held))
                self._held.clear()
                return self._pending.popleft()
            return None
        try:
            msg = json.loads(item.raw)
        except ValueError:
            return item
        if not _is_gate_response(msg):
            return item
        self._seen += 1
        out = self._apply(msg, item)
        if not out:
            return self.recv(timeout)
        self._pending.extend(out[1:])
        return out[0]

    def _apply(self, msg: dict[str, Any], item: Inbound) -> list[Inbound]:
        def rewrite(new: dict[str, Any]) -> Inbound:
            return Inbound(json.dumps(new, separators=(",", ":")), item.channel, item.at)

        if self.fault == "coerce-response-ids":
            rid = msg["id"]
            if isinstance(rid, str):
                try:
                    msg = {**msg, "id": int(rid)}
                except ValueError:
                    pass
            return [rewrite(msg)]
        if self.fault == "duplicate-responses":
            return [item, item]
        if self.fault == "drop-one-response":
            return [] if self._seen - 1 == self._victim else [item]
        if self.fault == "stale-result":
            body = {k: v for k, v in msg.items() if k in ("result", "error")}
            previous, self._previous = self._previous, body
            if previous is None:
                return [item]
            return [rewrite({"jsonrpc": "2.0", "id": msg["id"], **previous})]
        # hold-and-reverse: benign reordering (a positive control for out-of-order tolerance)
        self._held.append(item)
        return []
