from __future__ import annotations

import json
from typing import Any

import pytest

from mcp_faultline.trace import Trace, TraceEvent


class TraceBuilder:
    """Build synthetic traces so oracle rules can be tested without any process."""

    def __init__(self, transport: str = "stdio") -> None:
        self.events: list[TraceEvent] = []
        self.transport = transport

    def _add(self, direction: str, msg: Any, channel: str = "stdio") -> TraceBuilder:
        raw = msg if isinstance(msg, str) else json.dumps(msg)
        self.events.append(TraceEvent(len(self.events), float(len(self.events)), direction, channel, raw))  # type: ignore[arg-type]
        return self

    def call(self, rid: Any, tag: str, channel: str = "stdio") -> TraceBuilder:
        msg = {
            "jsonrpc": "2.0",
            "id": rid,
            "method": "tools/call",
            "params": {"name": "gate", "arguments": {"tag": tag}},
        }
        return self._add("out", msg, channel)

    def cancel(self, rid: Any) -> TraceBuilder:
        return self._add("out", {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": rid}})

    def result(self, rid: Any, text: str, channel: str = "stdio") -> TraceBuilder:
        return self._add(
            "in", {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": text}]}}, channel
        )

    def error(self, rid: Any, code: int = -32800, channel: str = "stdio") -> TraceBuilder:
        return self._add("in", {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": "x"}}, channel)

    def inbound(self, raw: Any) -> TraceBuilder:
        return self._add("in", raw)

    def recovered(self) -> TraceBuilder:
        self.call("fl-recovery", "fl-recovery")
        return self.result("fl-recovery", "fl-recovery")

    def build(self) -> Trace:
        return Trace("synthetic", {"name": "synthetic", "steps": []}, {"transport": self.transport}, self.events)


@pytest.fixture
def tb() -> TraceBuilder:
    return TraceBuilder()
