from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from mcp_faultline.jsonrpc import classify, decode_line, format_id, id_key, notification, request

ids = st.one_of(st.integers(min_value=-(2**63), max_value=2**63), st.text(max_size=12))


@given(ids, ids)
def test_id_key_is_injective(a: int | str, b: int | str) -> None:
    same_id = type(a) is type(b) and a == b
    assert (id_key(a) == id_key(b)) is same_id


@pytest.mark.parametrize("n", [0, 7, -1, 2**53 + 1])
def test_twins_never_share_a_key(n: int) -> None:
    assert id_key(n) != id_key(str(n))
    assert format_id(n) != format_id(str(n))


@pytest.mark.parametrize("bad", [True, False, 1.0, None, [1]])
def test_id_key_rejects_non_ids(bad: object) -> None:
    with pytest.raises(TypeError):
        id_key(bad)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("msg", "kind"),
    [
        (request(1, "ping"), "request"),
        (request("a", "ping", {}), "request"),
        (notification("notifications/initialized"), "notification"),
        ({"jsonrpc": "2.0", "id": 1, "result": {}}, "response"),
        ({"jsonrpc": "2.0", "id": "1", "error": {"code": -1, "message": "m"}}, "error"),
        ({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse"}}, "error"),
    ],
)
def test_classify_valid(msg: object, kind: str) -> None:
    c = classify(msg)
    assert c.kind == kind and c.problems == ()


@pytest.mark.parametrize(
    ("msg", "problem"),
    [
        ([], "not a JSON object"),
        ({"jsonrpc": "1.0", "id": 1, "result": {}}, '"jsonrpc"'),
        ({"jsonrpc": "2.0", "id": 1, "result": {}, "error": {"code": 1, "message": "m"}}, "exactly one"),
        ({"jsonrpc": "2.0", "id": 1}, "exactly one"),
        ({"jsonrpc": "2.0", "result": {}}, '"id"'),
        ({"jsonrpc": "2.0", "id": 1.5, "result": {}}, "string or integer"),
        ({"jsonrpc": "2.0", "id": True, "result": {}}, "string or integer"),
        ({"jsonrpc": "2.0", "id": None, "result": {}}, "string or integer"),
        ({"jsonrpc": "2.0", "id": 1, "error": {"code": "x", "message": "m"}}, "error.code"),
        ({"jsonrpc": "2.0", "id": 1, "error": {"code": 1}}, "error.message"),
        ({"jsonrpc": "2.0", "id": 1, "error": "boom"}, '"error" must be an object'),
        ({"jsonrpc": "2.0", "id": 1, "method": 5}, '"method"'),
        ({"jsonrpc": "2.0", "id": 1, "method": "m", "params": 3}, '"params"'),
        ({"jsonrpc": "2.0", "id": 1.0, "method": "m"}, "request id"),
        ({"jsonrpc": "2.0", "id": 1, "method": "m", "result": {}}, "must not carry"),
    ],
)
def test_classify_reports_violations(msg: object, problem: str) -> None:
    c = classify(msg)
    assert c.kind == "invalid"
    assert any(problem in p for p in c.problems), c.problems


def test_decode_line() -> None:
    assert decode_line('{"a": 1}') == ({"a": 1}, None)
    value, reason = decode_line("{nope")
    assert value is None and reason is not None and "invalid JSON" in reason
