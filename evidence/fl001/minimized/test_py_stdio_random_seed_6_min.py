"""Regression test exported by mcp-faultline 0.1.0.

Scenario : random/seed-6/min
Target   : py-stdio (python-sdk 2.3.0, protocol 2025-11-25)
Violated : R3, R6

This test FAILS while the defect is present and passes once it is fixed.
"""

import json
from pathlib import Path

import pytest

from mcp_faultline.runner import run
from mcp_faultline.scenario import Scenario

CASE = json.loads(Path(__file__).with_suffix(".json").read_text(encoding="utf-8"))


@pytest.mark.sdk
def test_py_stdio_random_seed_6_min() -> None:
    result = run(CASE["target"], Scenario.from_json(CASE["scenario"]))
    assert result.verdict.passed, [f"{v.rule}: {v.message}" for v in result.verdict.violations]
