"""Execute a :class:`~mcp_faultline.scenario.Scenario` against a target and record a trace.

Protocol of one run:

1. ``initialize`` (id ``"fl-init"``) at :data:`~mcp_faultline.targets.PROTOCOL_REVISION`,
   then ``notifications/initialized``.
2. Each scenario step in order. ``release`` and ``sync`` are control requests
   with ids ``"fl-ctl-N"`` and are awaited, so they also act as barriers.
3. Finalise: release every gate still closed (including those of cancelled
   requests, to observe whether cancellation was honoured), then wait until
   every non-cancelled request has answered or ``completion`` elapses (all gates
   are open and a control round trip has finished, so a healthy target answers
   in milliseconds), then stay
   quiet for ``settle`` seconds to catch duplicate or late responses.
4. Recovery probe: ``ping`` plus a fresh gate/release round trip, proving the
   session still works after the scenario.

Harness-generated ids all start with ``fl-`` and are non-numeric strings, so
they cannot collide with scenario ids under any coercion rule.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .jsonrpc import IdKey, RequestId, id_key, is_valid_id, notification, request
from .scenario import Scenario
from .targets import PROTOCOL_REVISION
from .trace import Trace, TraceEvent
from .transports import Connection, HttpConnection, TransportError

RECOVERY_ID = "fl-recovery"
RECOVERY_TAG = "fl-recovery"


class Recorder:
    def __init__(self, conn: Connection) -> None:
        self.conn = conn
        self.events: list[TraceEvent] = []
        self.responses: dict[IdKey, int] = {}
        self.step: int | None = None
        self._t0 = time.monotonic()

    def _add(self, direction: str, channel: str, raw: str, at: float | None = None) -> None:
        self.events.append(
            TraceEvent(
                seq=len(self.events),
                at=time.monotonic() - self._t0 if at is None else at,
                dir=direction,  # type: ignore[arg-type]
                channel=channel,
                raw=raw,
                step=self.step,
            )
        )

    def note(self, text: str) -> None:
        self._add("note", "harness", text)

    def send(self, message: dict[str, Any]) -> None:
        raw = json.dumps(message, separators=(",", ":"), ensure_ascii=False)
        channel = self.conn.send(message)
        self._add("out", channel, raw)

    def pump(self, until: Callable[[], bool], timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        while not until():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            item = self.conn.recv(min(remaining, 0.05))
            if item is None:
                continue
            self._add("in", item.channel, item.raw, time.monotonic() - self._t0)
            try:
                msg = json.loads(item.raw)
            except ValueError:
                continue
            if isinstance(msg, dict) and "method" not in msg and is_valid_id(msg.get("id")):  # pyright: ignore
                key = id_key(msg["id"])  # pyright: ignore[reportUnknownArgumentType]
                self.responses[key] = self.responses.get(key, 0) + 1
        return True

    def answered(self, request_id: RequestId) -> bool:
        return self.responses.get(id_key(request_id), 0) > 0

    def roundtrip(self, message: dict[str, Any], timeout: float) -> bool:
        self.send(message)
        ok = self.pump(lambda: self.answered(message["id"]), timeout)
        if not ok:
            self.note(f"timeout waiting for response to {json.dumps(message['id'])}")
        return ok


def redact(text: str) -> str:
    """Replace the user's home directory in captured stderr so traces are safe to publish."""
    home = str(Path.home())
    return text.replace(home, "~").replace(home.replace("\\", "/"), "~")


def _gate_call(request_id: RequestId, tag: str) -> dict[str, Any]:
    return request(request_id, "tools/call", {"name": "gate", "arguments": {"tag": tag}})


def _release(control_id: str, tag: str) -> dict[str, Any]:
    return request(control_id, "tools/call", {"name": "release", "arguments": {"tag": tag}})


def execute(
    conn: Connection,
    scenario: Scenario,
    *,
    target: str,
    provenance: dict[str, Any],
    timeout: float = 5.0,
    completion: float = 2.0,
    settle: float = 0.4,
) -> Trace:
    """Run ``scenario`` over an already-open ``conn``. Never raises for target misbehaviour."""
    rec = Recorder(conn)
    ctl = 0

    def next_ctl() -> str:
        nonlocal ctl
        ctl += 1
        return f"fl-ctl-{ctl}"

    scenario = scenario.normalized()
    try:
        init = request(
            "fl-init",
            "initialize",
            {
                "protocolVersion": PROTOCOL_REVISION,
                "capabilities": {},
                "clientInfo": {"name": "mcp-faultline", "version": provenance.get("harness", "")},
            },
        )
        if not rec.roundtrip(init, timeout=max(timeout, 15.0)):
            raise TransportError("initialize did not complete")
        if isinstance(conn, HttpConnection):
            conn.protocol_version = PROTOCOL_REVISION
        rec.send(notification("notifications/initialized"))

        tags: dict[str, bool] = {}  # tag -> released
        calls: list[tuple[RequestId, str]] = []
        cancelled: set[IdKey] = set()
        for index, step in enumerate(scenario.steps):
            rec.step = index
            if step.op == "call":
                assert step.id is not None and step.tag is not None
                calls.append((step.id, step.tag))
                tags.setdefault(step.tag, False)
                rec.send(_gate_call(step.id, step.tag))
            elif step.op == "cancel":
                assert step.id is not None
                cancelled.add(id_key(step.id))
                rec.send(notification("notifications/cancelled", {"requestId": step.id, "reason": "mcp-faultline"}))
            elif step.op == "release":
                assert step.tag is not None
                tags[step.tag] = True
                rec.roundtrip(_release(next_ctl(), step.tag), timeout)
            else:
                rec.roundtrip(request(next_ctl(), "ping"), timeout)
            rec.pump(lambda: False, 0.02)  # collect anything already in flight

        rec.step = None
        rec.note("finalize: releasing remaining gates")
        for tag, released in tags.items():
            if not released:
                rec.roundtrip(_release(next_ctl(), tag), timeout)
        live = [rid for rid, _ in calls if id_key(rid) not in cancelled]
        rec.pump(lambda: all(rec.answered(r) for r in live), completion)
        rec.pump(lambda: False, settle)

        rec.note("recovery probe")
        rec.roundtrip(request(next_ctl(), "ping"), timeout)
        rec.send(_gate_call(RECOVERY_ID, RECOVERY_TAG))
        rec.roundtrip(_release(next_ctl(), RECOVERY_TAG), timeout)
        rec.pump(lambda: rec.answered(RECOVERY_ID), timeout)
        rec.pump(lambda: False, 0.05)
    except TransportError as exc:
        rec.note(f"transport error: {exc}")
    finally:
        diagnostics = redact(conn.diagnostics())
        conn.close()
    return Trace(
        target=target, scenario=scenario.to_json(), provenance=provenance, events=rec.events, diagnostics=diagnostics
    )
