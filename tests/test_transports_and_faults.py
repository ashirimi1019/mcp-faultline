from __future__ import annotations

import json
from typing import Any

import pytest

from mcp_faultline.faults import FAULTS, FaultyConnection
from mcp_faultline.transports import Inbound, iter_sse_data


def test_sse_framing() -> None:
    raw = b': comment\nevent: message\ndata: {"a":\ndata: 1}\nid: 3\n\ndata:x\n\n\ndata: tail'
    lines = [line + b"\n" for line in raw.split(b"\n")]
    assert list(iter_sse_data(iter(lines))) == ['{"a":\n1}', "x", "tail"]


class FakeConn:
    def __init__(self, messages: list[dict[str, Any]]) -> None:
        self.items = [Inbound(json.dumps(m), "c", float(i)) for i, m in enumerate(messages)]
        self.sent: list[dict[str, Any]] = []
        self.closed = False

    def send(self, message: dict[str, Any]) -> str:
        self.sent.append(message)
        return "c"

    def recv(self, timeout: float) -> Inbound | None:
        return self.items.pop(0) if self.items else None

    def close(self) -> None:
        self.closed = True

    def diagnostics(self) -> str:
        return "inner"


def _resp(rid: Any, text: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": text}]}}


def drain(conn: FaultyConnection) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    while (item := conn.recv(0)) is not None:
        out.append(json.loads(item.raw))
    return out


STREAM = [_resp("7", "a"), _resp("fl-ctl-1", "c"), _resp(8, "b"), {"jsonrpc": "2.0", "method": "n"}]


def test_coerce_response_ids() -> None:
    out = drain(FaultyConnection(FakeConn(list(STREAM)), "coerce-response-ids"))
    assert [m.get("id") for m in out] == [7, "fl-ctl-1", 8, None]


def test_duplicate_responses_leaves_control_traffic_alone() -> None:
    out = drain(FaultyConnection(FakeConn(list(STREAM)), "duplicate-responses"))
    assert [m.get("id") for m in out] == ["7", "7", "fl-ctl-1", 8, 8, None]


@pytest.mark.parametrize(("seed", "survivor"), [(0, 8), (1, "7")])
def test_drop_one_response_is_seeded(seed: int, survivor: Any) -> None:
    out = drain(FaultyConnection(FakeConn(list(STREAM)), "drop-one-response", seed))
    gate_ids = [m["id"] for m in out if "id" in m and m["id"] != "fl-ctl-1"]
    assert gate_ids == [survivor]


def test_stale_result_reuses_previous_payload() -> None:
    out = drain(FaultyConnection(FakeConn(list(STREAM)), "stale-result"))
    assert out[2] == _resp(8, "a")
    assert out[0] == _resp("7", "a")


def test_hold_and_reverse_flushes_reversed_when_quiet() -> None:
    out = drain(FaultyConnection(FakeConn(list(STREAM)), "hold-and-reverse"))
    assert [m.get("id") for m in out] == ["fl-ctl-1", None, 8, "7"]


def test_fault_wrapper_delegates_and_validates() -> None:
    inner = FakeConn([])
    conn = FaultyConnection(inner, FAULTS[0], seed=5)
    assert conn.send({"x": 1}) == "c" and inner.sent == [{"x": 1}]
    assert "fault=coerce-response-ids seed=5" in conn.diagnostics()
    conn.close()
    assert inner.closed
    with pytest.raises(ValueError):
        FaultyConnection(inner, "nope")


def test_non_json_passes_through() -> None:
    inner = FakeConn([])
    inner.items = [Inbound("garbage", "c", 0.0)]
    assert FaultyConnection(inner, "duplicate-responses").recv(0) == Inbound("garbage", "c", 0.0)
