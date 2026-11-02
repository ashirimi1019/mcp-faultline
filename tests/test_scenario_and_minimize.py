from __future__ import annotations

import json

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from mcp_faultline.experiments import fl001
from mcp_faultline.jsonrpc import id_key
from mcp_faultline.minimize import ddmin, minimize
from mcp_faultline.oracle import Verdict
from mcp_faultline.scenario import SYNC, Scenario, Step, call, cancel, release


def test_normalized_drops_protocol_illegal_steps() -> None:
    s = Scenario("x", (cancel(1), call(1, "a"), call(1, "b"), cancel(1), cancel(1), cancel(2), release("a"), SYNC))
    assert s.normalized().steps == (call(1, "a"), cancel(1), release("a"), SYNC)


def test_normalized_keeps_typed_twins() -> None:
    s = Scenario("x", (call(7, "a"), call("7", "b"), cancel("7")))
    assert s.normalized().steps == s.steps


@given(st.integers(min_value=0, max_value=10_000))
def test_generate_is_deterministic_legal_and_has_twins(seed: int) -> None:
    a, b = fl001.generate(seed), fl001.generate(seed)
    assert a == b
    assert a.normalized() == a
    keys = {id_key(s.id) for s in a.steps if s.op == "call" and s.id is not None}
    assert any(("str", text) in keys for kind, text in keys if kind == "int")


@given(st.integers(min_value=0, max_value=500))
def test_scenario_json_roundtrip(seed: int) -> None:
    s = fl001.generate(seed)
    assert Scenario.from_json(json.loads(json.dumps(s.to_json()))) == s


def test_fixed_matrix_names_are_unique_and_paired_with_controls() -> None:
    names = [s.name for s in fl001.scenarios()]
    assert len(names) == len(set(names))
    tags = {t for s in fl001.scenarios() for t in s.tags}
    assert {"collision", "control", "noncanonical"} <= tags


@pytest.mark.parametrize(
    "bad",
    [{"op": "nope"}, {"op": "call", "tag": "a"}, {"op": "call", "id": True, "tag": "a"}, {"op": "release"}],
)
def test_step_validation(bad: dict[str, object]) -> None:
    with pytest.raises((ValueError, TypeError)):
        Step.from_json(bad)


def test_describe() -> None:
    assert call("7", "a").describe() == 'call   id="7" gate(a)'
    assert cancel(7).describe() == "cancel id=7"
    assert release("a").describe() == "release a" and SYNC.describe() == "sync"


@settings(max_examples=200)
@given(st.lists(st.integers(0, 30), max_size=25), st.sets(st.integers(0, 30), min_size=1, max_size=3))
def test_ddmin_is_one_minimal(items: list[int], needed: set[int]) -> None:
    steps = [Step("release", tag=str(i)) for i in items]
    need = {str(i) for i in needed}

    def fails(candidate: list[Step]) -> bool:
        return need <= {s.tag for s in candidate}

    if not fails(steps):
        return
    out = ddmin(steps, fails)
    assert fails(out)
    assert all(not fails(out[:i] + out[i + 1 :]) for i in range(len(out)))  # 1-minimal
    it = iter(steps)
    assert all(any(s == t for t in it) for s in out)  # subsequence of the input


def _verdict(sig: set[str]) -> Verdict:
    from mcp_faultline.oracle import Finding

    return Verdict("t", "s", tuple(Finding(r, r) for r in sorted(sig)), (), {})


def test_minimize_finds_cross_cancel_core_and_confirms() -> None:
    s = Scenario("m", (call(1, "x"), call(7, "a"), SYNC, call("7", "b"), release("x"), cancel(7), SYNC))

    def oracle(c: Scenario) -> Verdict:
        st = c.steps
        bug = call(7, "a") in st and call("7", "b") in st and cancel(7) in st
        return _verdict({"R3", "R6"} if bug else set())

    m = minimize(s, oracle, confirm=2)
    assert m.stable and m.signature == {"R3", "R6"}
    assert m.minimal.steps == (call(7, "a"), call("7", "b"), cancel(7))
    assert m.minimal.name == "m/min"


def test_minimize_rejects_passing_scenario() -> None:
    with pytest.raises(ValueError):
        minimize(Scenario("p", (call(1, "a"),)), lambda c: _verdict(set()))


def test_minimize_reports_instability() -> None:
    confirmations = iter([True, False, True])  # only the confirmation runs use the "/min" name

    def oracle(c: Scenario) -> Verdict:
        fails = call(1, "a") in c.steps and (not c.name.endswith("/min") or next(confirmations))
        return _verdict({"R3"} if fails else set())

    m = minimize(Scenario("f", (call(1, "a"), call(2, "b"))), oracle, confirm=3)
    assert not m.stable
