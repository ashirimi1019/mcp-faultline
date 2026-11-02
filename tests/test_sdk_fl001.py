"""FL-001 against the pinned official SDKs (marker: ``sdk``).

These are characterisation tests. A test asserting correct behaviour on a
pinned SDK that is known to be defective is marked ``xfail(strict=True)``:
when an SDK upgrade fixes the defect the XPASS turns the suite red, which
forces the documentation of the finding to be updated rather than going stale.
"""

from __future__ import annotations

import shutil

import pytest

from mcp_faultline.experiments import fl001
from mcp_faultline.runner import parallel_map, run
from mcp_faultline.targets import PINNED, python_sdk_version, typescript_sdk_v2_version, typescript_sdk_version

pytestmark = pytest.mark.sdk

SCENARIOS = {s.name: s for s in fl001.scenarios()}
CONTROLS = [s for s in fl001.scenarios() if "control" in s.tags]

needs_py = pytest.mark.skipif(python_sdk_version() is None, reason="python mcp SDK not installed")
needs_ts = pytest.mark.skipif(
    typescript_sdk_version() is None or shutil.which("node") is None, reason="node or targets/ts not installed"
)

needs_ts2 = pytest.mark.skipif(
    typescript_sdk_v2_version() is None or shutil.which("node") is None, reason="node or targets/ts-v2 not installed"
)


@needs_py
def test_python_sdk_is_the_pinned_version() -> None:
    assert python_sdk_version() == PINNED["python-sdk"]


@needs_ts
def test_typescript_sdk_is_the_pinned_version() -> None:
    assert typescript_sdk_version() == PINNED["typescript-sdk"]


@needs_py
@pytest.mark.parametrize("target", ["py-stdio", "py-http-sse"])
def test_python_controls_pass(target: str) -> None:
    verdicts = list(parallel_map(lambda s: run(target, s).verdict, CONTROLS, 4))
    assert all(v.passed for v in verdicts), [(v.scenario, sorted(v.signature)) for v in verdicts if not v.passed]


@needs_py
@pytest.mark.xfail(strict=True, reason="python-sdk 2.3.0: dispatcher _in_flight keyed by coerce_request_id()")
def test_python_stdio_cancel_isolation() -> None:
    assert run("py-stdio", SCENARIOS["collide-7/cancel-first"]).verdict.passed


@needs_py
def test_python_stdio_cross_cancellation_signature() -> None:
    v = run("py-stdio", SCENARIOS["collide-7/cancel-first"]).verdict
    assert v.signature == {"R3", "R6"}
    assert v.outcomes == {"7": "cancelled:result:t-int-7", '"7"': "LOST"}


@needs_py
@pytest.mark.xfail(strict=True, reason="python-sdk#3786: streamable HTTP keys response streams by str(request_id)")
def test_python_http_out_of_order_twins() -> None:
    assert run("py-http-sse", SCENARIOS["collide-7/out-of-order"]).verdict.passed


@needs_ts
@pytest.mark.parametrize("target", ["ts-stdio", "ts-http-sse", "ts-http-json"])
def test_typescript_isolates_typed_ids(target: str) -> None:
    names = [n for n in SCENARIOS if n.startswith(("collide-7/", "collide-7-strfirst/", "control-"))]
    verdicts = list(parallel_map(lambda n: run(target, SCENARIOS[n]).verdict, names, 4))
    assert all(v.passed for v in verdicts), [(v.scenario, sorted(v.signature)) for v in verdicts if not v.passed]


@needs_ts
def test_typescript_ignores_cancel_of_request_id_zero() -> None:
    """typescript-sdk#2283 / v1.x backport #3043: `if (!requestId) return` drops id 0. SHOULD-level only."""
    v = run("ts-stdio", SCENARIOS["collide-0/cancel-first"]).verdict
    assert v.passed
    assert [o.rule for o in v.observations] == ["cancel-ignored"]


@needs_ts2
def test_typescript_v2_is_the_pinned_version() -> None:
    assert typescript_sdk_v2_version() == PINNED["typescript-sdk-v2"]


@needs_ts2
@pytest.mark.parametrize("target", ["ts2-stdio", "ts2-http-sse", "ts2-http-json"])
def test_typescript_v2_isolates_typed_ids(target: str) -> None:
    names = [n for n in SCENARIOS if n.startswith(("collide-7/", "collide-0/", "control-"))]
    verdicts = list(parallel_map(lambda n: run(target, SCENARIOS[n]).verdict, names, 4))
    assert all(v.passed and not v.observations for v in verdicts), [
        (v.scenario, sorted(v.signature), [o.rule for o in v.observations])
        for v in verdicts
        if v.observations or not v.passed
    ]


@needs_ts2
def test_typescript_v2_honours_cancel_of_request_id_zero() -> None:
    """Differential against v1.32.2: v2 checks `requestId === undefined`, so id 0 is cancellable."""
    v = run("ts2-stdio", SCENARIOS["collide-0/cancel-first"]).verdict
    assert v.passed and not v.observations
    assert v.outcomes == {"0": "cancelled:no-response", '"0"': "result:t-str-0"}
