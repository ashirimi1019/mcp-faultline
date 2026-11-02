"""Harness self-test: positive and negative controls for the FL-001 oracle.

Each control names a defect source (a reference-server mutant or a fault
injected on a correct target) and, for every FL-001 scenario, whether the
oracle MUST fail it or MUST pass it. A control "holds" only if the oracle
agrees on every scenario - so the oracle is shown both to detect each
defect class *and* not to over-report on scenarios where it cannot occur.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .scenario import Scenario

Expect = Callable[[Scenario], bool]  # True -> the oracle must report a violation


def _collision_or_noncanonical(s: Scenario) -> bool:
    return "collision" in s.tags or "noncanonical" in s.tags


def _collision_cancel_earlier(s: Scenario) -> bool:
    # A last-writer-wins cancel table only mis-targets when the *earlier* twin is cancelled.
    return _collision_or_noncanonical(s) and s.name.endswith("/cancel-first")


def _live_numeric_string(s: Scenario) -> bool:
    # Coercing "7" -> 7 on the wire is only visible when a numeric-string id is actually answered.
    cancelled = {repr(st.id) for st in s.steps if st.op == "cancel"}
    for st in s.steps:
        if st.op == "call" and isinstance(st.id, str) and repr(st.id) not in cancelled:
            try:
                int(st.id)
                return True
            except ValueError:
                pass
    return False


def _collision_route(s: Scenario) -> bool:
    # Last-writer-wins routing only misroutes a reply when the completing request
    # is not the most recently registered twin; cancel-first completes exactly that one.
    return "collision" in s.tags and not s.name.endswith("/cancel-first")


def _never(_: Scenario) -> bool:
    return False


def _always(_: Scenario) -> bool:
    return True


def _has_live_string_id(s: Scenario) -> bool:
    cancelled = {repr(st.id) for st in s.steps if st.op == "cancel"}
    return any(st.op == "call" and isinstance(st.id, str) and repr(st.id) not in cancelled for st in s.steps)


def _out_of_order(s: Scenario) -> bool:
    return s.name.endswith("/out-of-order")


@dataclass(frozen=True)
class Control:
    name: str
    target: str
    fault: str | None
    must_fail: Expect
    rationale: str


CONTROLS: tuple[Control, ...] = (
    Control("reference", "ref", None, _never, "correct implementation: no scenario may fail (no false positives)"),
    Control(
        "mutant:coerce-inflight",
        "ref:coerce-inflight",
        None,
        _collision_cancel_earlier,
        "int()-folded cancel table, last writer wins: cancelling the earlier twin hits the later one",
    ),
    Control(
        "mutant:coerce-response-id",
        "ref:coerce-response-id",
        None,
        _live_numeric_string,
        "'7' answered as 7: visible whenever a numeric-string id is answered",
    ),
    Control(
        "mutant:str-key-route",
        "ref:str-key-route",
        None,
        _collision_route,
        "str(id)-keyed reply routing, last writer wins: only same-text ids collide",
    ),
    Control(
        "mutant:ignore-cancel",
        "ref:ignore-cancel",
        None,
        _never,
        "ignoring cancellation is SHOULD-level: observation only, never a violation",
    ),
    Control(
        "mutant:drop-string-ids",
        "ref:drop-string-ids",
        None,
        _has_live_string_id,
        "lost responses for string ids: fails exactly where a non-cancelled string id exists",
    ),
    Control(
        "fault:coerce-response-ids",
        "ref",
        "coerce-response-ids",
        _live_numeric_string,
        "wire-level id coercion injected on a correct server",
    ),
    Control("fault:duplicate-responses", "ref", "duplicate-responses", _always, "every gate response duplicated"),
    Control("fault:drop-one-response", "ref", "drop-one-response", _always, "first gate response dropped (seed 0)"),
    Control(
        "fault:stale-result",
        "ref",
        "stale-result",
        _out_of_order,
        "second gate response carries the first one's payload (only scenarios with two answers)",
    ),
    Control(
        "fault:hold-and-reverse",
        "ref",
        "hold-and-reverse",
        _never,
        "benign reordering of responses: out-of-order delivery is legal and must not be flagged",
    ),
)
