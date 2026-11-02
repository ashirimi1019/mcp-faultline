"""Each oracle rule, exercised on hand-built traces (no processes involved)."""

from __future__ import annotations

from conftest import TraceBuilder

from mcp_faultline.oracle import evaluate


def rules(tb: TraceBuilder) -> set[str]:
    return set(evaluate(tb.build()).signature)


def test_clean_out_of_order_trace_passes(tb: TraceBuilder) -> None:
    tb.call(7, "a").call("7", "b").result("7", "b").result(7, "a").recovered()
    v = evaluate(tb.build())
    assert v.passed, v.violations
    assert v.outcomes == {"7": "result:a", '"7"': "result:b"}


def test_r1_coerced_response_id_is_named(tb: TraceBuilder) -> None:
    tb.call("7", "b").result(7, "b").recovered()
    v = evaluate(tb.build())
    assert {"R1", "R3"} <= v.signature
    assert any("coerced" in f.message for f in v.violations if f.rule == "R1")


def test_r2_duplicate_response(tb: TraceBuilder) -> None:
    tb.call(1, "a").result(1, "a").result(1, "a").recovered()
    assert rules(tb) == {"R2"}


def test_r3_lost_response(tb: TraceBuilder) -> None:
    tb.call(1, "a").recovered()
    assert rules(tb) == {"R3"}


def test_r4_wrong_payload(tb: TraceBuilder) -> None:
    tb.call(1, "a").call(2, "b").result(1, "b").result(2, "b").recovered()
    assert rules(tb) == {"R4"}


def test_r4_and_r6_error_after_twin_cancel(tb: TraceBuilder) -> None:
    tb.call(7, "a").call("7", "b").cancel(7).error("7").recovered()
    assert rules(tb) == {"R4", "R6"}


def test_r6_cross_cancellation(tb: TraceBuilder) -> None:
    tb.call(7, "a").call("7", "b").cancel(7).result(7, "a").recovered()
    v = evaluate(tb.build())
    assert v.signature == {"R3", "R6"}
    assert [o.rule for o in v.observations] == ["cancel-ignored"]


def test_r5_wrong_http_stream() -> None:
    tb = TraceBuilder(transport="http-sse")
    tb.call(7, "a", channel="post#1").call("7", "b", channel="post#2")
    tb.result(7, "a", channel="post#2").result("7", "b", channel="post#2")
    tb.call("fl-recovery", "fl-recovery", channel="post#3").result("fl-recovery", "fl-recovery", channel="post#3")
    assert rules(tb) == {"R5"}


def test_r5_not_applied_to_stdio(tb: TraceBuilder) -> None:
    tb.call(7, "a", channel="x").result(7, "a", channel="y").recovered()
    assert rules(tb) == set()


def test_r7_no_recovery(tb: TraceBuilder) -> None:
    tb.call(1, "a").result(1, "a").call("fl-recovery", "fl-recovery")
    assert rules(tb) == {"R7"}


def test_r7_unanswered_control_request(tb: TraceBuilder) -> None:
    tb.call("fl-ctl-1", "x").recovered()
    assert rules(tb) == {"R7"}


def test_wire_violations(tb: TraceBuilder) -> None:
    tb.inbound("not json").inbound({"jsonrpc": "2.0", "id": 1}).recovered()
    assert rules(tb) == {"WIRE"}


def test_null_id_error_is_r1(tb: TraceBuilder) -> None:
    tb.call(1, "a").result(1, "a").inbound({"jsonrpc": "2.0", "id": None, "error": {"code": -1, "message": "m"}})
    assert rules(tb.recovered()) == {"R1"}


def test_cancel_observations_are_not_failures(tb: TraceBuilder) -> None:
    tb.call(1, "a").call(2, "b").cancel(1).cancel(2).result(1, "a").error(2).recovered()
    v = evaluate(tb.build())
    assert v.passed
    assert sorted(o.rule for o in v.observations) == ["cancel-answered", "cancel-ignored"]
    assert v.outcomes == {"1": "cancelled:result:a", "2": "cancelled:error:-32800"}


def test_response_before_cancel_is_not_an_observation(tb: TraceBuilder) -> None:
    tb.call(1, "a").result(1, "a").cancel(1).recovered()
    v = evaluate(tb.build())
    assert v.passed and not v.observations


def test_server_requests_and_notifications_are_ignored(tb: TraceBuilder) -> None:
    tb.inbound({"jsonrpc": "2.0", "method": "notifications/message", "params": {}})
    tb.inbound({"jsonrpc": "2.0", "id": 99, "method": "ping"})
    assert rules(tb.recovered()) == set()


def test_noncanonical_twin_gets_no_r6(tb: TraceBuilder) -> None:
    # "07" is not the canonical text of 7, so its loss is R3 but not attributed as a twin.
    tb.call(7, "a").call("07", "b").cancel(7).result(7, "a").recovered()
    assert rules(tb) == {"R3"}


def test_redact_home_directory() -> None:
    import os
    from pathlib import Path

    from mcp_faultline.engine import redact

    home = str(Path.home())
    native = os.path.join(home, "pkg", "x.py")
    posix = home.replace(os.sep, "/") + "/pkg/x.py"
    out = redact(f"{native} | {posix}")
    assert home not in out and home.replace(os.sep, "/") not in out
    assert out.startswith("~")
