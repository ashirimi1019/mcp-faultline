"""Export failures as regression tests and standalone reproductions.

* :func:`regression_case` - a JSON case + pytest module that replays the
  scenario through the harness and asserts the oracle passes. It fails while
  the defect exists and passes once it is fixed.
* :func:`standalone_repro` - a single stdlib-only Python script that replays the
  exact wire messages against a stdio server command, with no dependency on
  MCP Faultline, suitable for attaching to an upstream issue.
"""

from __future__ import annotations

import json
import pprint
import re
import textwrap
from pathlib import Path
from typing import Any

from .oracle import Verdict
from .trace import Trace

_TEST_TEMPLATE = '''"""Regression test exported by mcp-faultline {version}.

Scenario : {scenario}
Target   : {target} ({implementation} {impl_version}, protocol {protocol})
Violated : {rules}

This test FAILS while the defect is present and passes once it is fixed.
"""

import json
from pathlib import Path

import pytest

from mcp_faultline.runner import run
from mcp_faultline.scenario import Scenario

CASE = json.loads(Path(__file__).with_suffix(".json").read_text(encoding="utf-8"))


@pytest.mark.sdk
def test_{func}() -> None:
    result = run(CASE["target"], Scenario.from_json(CASE["scenario"]))
    assert result.verdict.passed, [f"{{v.rule}}: {{v.message}}" for v in result.verdict.violations]
'''


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def regression_case(trace: Trace, verdict: Verdict, out_dir: Path) -> tuple[Path, Path]:
    from . import __version__

    name = slug(f"{trace.target}_{trace.scenario['name']}")
    out_dir.mkdir(parents=True, exist_ok=True)
    case_path = out_dir / f"test_{name}.json"
    test_path = out_dir / f"test_{name}.py"
    case = {
        "format": "mcp-faultline/case@1",
        "target": trace.target,
        "scenario": trace.scenario,
        "expected": "no-violations",
        "observed_violations": [f.to_json() for f in verdict.violations],
        "provenance": trace.provenance,
    }
    case_path.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    prov = trace.provenance
    test_path.write_text(
        _TEST_TEMPLATE.format(
            version=__version__,
            scenario=trace.scenario["name"],
            target=trace.target,
            implementation=prov.get("implementation"),
            impl_version=prov.get("implementation_version"),
            protocol=prov.get("protocol_revision"),
            rules=", ".join(sorted(verdict.signature)) or "none",
            func=name,
        ),
        encoding="utf-8",
    )
    return case_path, test_path


_REPRO_TEMPLATE = '''#!/usr/bin/env python3
"""Standalone reproduction exported by mcp-faultline {version} (stdlib only).

Target   : {implementation} {impl_version} over stdio, MCP protocol {protocol}
Scenario : {scenario}
Expected : {expected}
Observed : {observed}

Usage: python {filename} <server command...>
   e.g. python {filename} python server.py stdio
"""

import json
import queue
import subprocess
import sys
import threading
import time

# (message, wait_for_response_id) pairs, in wire order. A wait id of None means fire-and-forget.
SCRIPT = {script}
EXPECTED_RESPONSES = {expected_ids}  # typed ids that must each receive exactly one response


def main() -> int:
    proc = subprocess.Popen(sys.argv[1:], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding="utf-8")
    inbox = queue.Queue()
    threading.Thread(target=lambda: [inbox.put(line) for line in proc.stdout], daemon=True).start()
    received = []

    def drain(until, timeout):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and not until():
            try:
                line = inbox.get(timeout=0.05)
            except queue.Empty:
                continue
            msg = json.loads(line)
            received.append(msg)
            print("<-", json.dumps(msg))

    def responses_to(rid):
        # Typed comparison: 7 and "7" are different JSON-RPC ids.
        return [m for m in received if "method" not in m and type(m.get("id")) is type(rid) and m.get("id") == rid]

    def answered(rid):
        return bool(responses_to(rid))

    for message, wait_id in SCRIPT:
        print("->", json.dumps(message))
        proc.stdin.write(json.dumps(message) + "\\n")
        proc.stdin.flush()
        if wait_id is not None:
            drain(lambda rid=wait_id: answered(rid), 10)
    drain(lambda: all(answered(r) for r in EXPECTED_RESPONSES), 5)
    drain(lambda: False, 0.5)
    proc.kill()

    failed = False
    for rid in EXPECTED_RESPONSES:
        n = len(responses_to(rid))
        if n != 1:
            failed = True
            print(f"FAIL: request id {{json.dumps(rid)}} received {{n}} responses (expected exactly 1)")
        else:
            resp = responses_to(rid)[0]
            if "error" in resp:
                failed = True
                print(f"FAIL: request id {{json.dumps(rid)}} was never cancelled but got error {{resp['error']}}")
    print("RESULT:", "defect reproduced" if failed else "no defect observed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
'''


def standalone_repro(trace: Trace, verdict: Verdict, path: Path) -> Path:
    """Write a dependency-free script replaying the trace's outbound messages."""
    from . import __version__

    script: list[tuple[dict[str, Any], Any]] = []
    expected: list[Any] = []
    cancelled: set[str] = set()
    outbound = [json.loads(e.raw) for e in trace.events if e.dir == "out"]
    for msg in outbound:
        if msg.get("method") == "notifications/cancelled":
            cancelled.add(json.dumps(msg["params"]["requestId"]))
    for msg in outbound:
        rid = msg.get("id")
        is_gate = msg.get("method") == "tools/call" and msg.get("params", {}).get("name") == "gate"
        harness_ctl = isinstance(rid, str) and rid.startswith("fl-")
        if rid is not None and is_gate and not harness_ctl and json.dumps(rid) not in cancelled:
            expected.append(rid)
        wait = rid if rid is not None and (harness_ctl or not is_gate) else None
        script.append((msg, wait))
    prov = trace.provenance
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        _REPRO_TEMPLATE.format(
            version=__version__,
            implementation=prov.get("implementation"),
            impl_version=prov.get("implementation_version"),
            protocol=prov.get("protocol_revision"),
            scenario=trace.scenario["name"],
            expected="every non-cancelled request receives exactly one successful response with its own typed id",
            observed=textwrap.fill(
                "; ".join(f"{f.rule}: {f.message}" for f in verdict.violations) or "no violations",
                width=100,
                subsequent_indent=" " * 11,
            ),
            filename=path.name,
            script=pprint.pformat(script, width=110, sort_dicts=False),
            expected_ids=repr(expected),
        ),
        encoding="utf-8",
    )
    return path
