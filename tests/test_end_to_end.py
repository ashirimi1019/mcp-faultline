"""End-to-end runs over real stdio processes (reference server + mutants; no SDK needed)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from mcp_faultline.cli import main
from mcp_faultline.controls import CONTROLS
from mcp_faultline.experiments import fl001
from mcp_faultline.export import regression_case, standalone_repro
from mcp_faultline.runner import parallel_map, replay, run
from mcp_faultline.scenario import Scenario
from mcp_faultline.trace import Trace

SCENARIOS = {s.name: s for s in fl001.scenarios()}


def _pick(control_must_fail: bool, control: object) -> Scenario | None:
    for s in fl001.scenarios():
        if control.must_fail(s) is control_must_fail:  # type: ignore[attr-defined]
            return s
    return None


CASES = [(c, s, expect) for c in CONTROLS for expect in (True, False) if (s := _pick(expect, c)) is not None]


def test_every_control_has_a_detecting_and_a_quiet_case() -> None:
    names = {c.name for c, _, expect in CASES if expect}
    negatives = {"reference", "mutant:ignore-cancel", "fault:hold-and-reverse"}
    assert names == {c.name for c in CONTROLS} - negatives


def test_controls_hold_on_representative_scenarios() -> None:
    """One must-fail and one must-pass scenario per control (full sweep: `faultline controls`)."""

    def one(case: tuple[object, Scenario, bool]) -> str | None:
        control, scenario, expect = case
        verdict = run(control.target, scenario, fault=control.fault, timeout=10).verdict  # type: ignore[attr-defined]
        if expect == verdict.passed:
            wanted = "FAIL" if expect else "pass"
            return f"{control.name} on {scenario.name}: expected {wanted}, got {sorted(verdict.signature)}"  # type: ignore[attr-defined]
        return None

    problems = [p for p in parallel_map(one, CASES, 8) if p]
    assert not problems, problems


def test_trace_roundtrip_replay_and_provenance(tmp_path: Path) -> None:
    result = run("ref:coerce-inflight", SCENARIOS["collide-7/cancel-first"])
    assert result.verdict.signature == {"R3", "R6"}
    prov = result.trace.provenance
    assert prov["protocol_revision"] == "2025-11-25" and prov["implementation"] == "reference"
    path = tmp_path / "t.json"
    result.trace.dump(path)
    loaded = Trace.load(path)
    assert loaded.to_json() == result.trace.to_json()
    again = replay(loaded)
    assert again.verdict.signature == result.verdict.signature


def test_trace_rejects_unknown_format() -> None:
    with pytest.raises(ValueError):
        Trace.from_json({"format": "other"})


def test_exported_standalone_repro_is_independent(tmp_path: Path) -> None:
    result = run("ref:coerce-inflight", SCENARIOS["collide-7/cancel-first"])
    script = standalone_repro(result.trace, result.verdict, tmp_path / "repro.py")
    server = [sys.executable, "-m", "mcp_faultline.reference_server", "--mutant"]
    bad = subprocess.run(
        [sys.executable, str(script), *server, "coerce-inflight"], capture_output=True, text=True, timeout=60
    )
    good = subprocess.run([sys.executable, str(script), *server, "none"], capture_output=True, text=True, timeout=60)
    assert bad.returncode == 1 and "defect reproduced" in bad.stdout
    assert good.returncode == 0 and "no defect observed" in good.stdout


def test_exported_regression_test_fails_while_defect_exists(tmp_path: Path) -> None:
    result = run("ref:coerce-inflight", SCENARIOS["collide-7/cancel-first"])
    case, test = regression_case(result.trace, result.verdict, tmp_path)
    assert case.exists()
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(test)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=tmp_path,
    )
    assert proc.returncode == 1, proc.stdout
    assert "R6" in proc.stdout


def test_cli_run_inspect_minimize_export(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = tmp_path / "run"
    assert (
        main(
            [
                "run",
                "-t",
                "ref:coerce-inflight",
                "-t",
                "ref",
                "-s",
                "collide-7/cancel-first",
                "-o",
                str(out),
                "--strict",
            ]
        )
        == 1
    )
    text = capsys.readouterr().out
    assert "FAIL R3,R6" in text and "diverge" in text
    assert (out / "report.md").read_text(encoding="utf-8").count("R6") >= 1
    assert main(["diff", str(out / "results.json")]) == 0
    assert "collide-7/cancel-first" in capsys.readouterr().out
    trace = next((out / "traces").glob("ref_coerce_inflight*.json"))
    assert main(["inspect", str(trace)]) == 1
    assert "!!" in capsys.readouterr().out
    assert main(["replay", str(trace), "-n", "1"]) == 0
    assert main(["minimize", str(trace), "-o", str(tmp_path / "min"), "--confirm", "2"]) == 0
    text = capsys.readouterr().out
    assert "6 -> 3 steps" in text and "(stable)" in text
    assert list((tmp_path / "min").glob("repro_*.py"))
    assert main(["export", str(trace), "-o", str(tmp_path / "exp"), "--standalone"]) == 0
    assert main(["report", str(out / "results.json"), "-o", str(tmp_path / "r.md")]) == 0


def test_cli_listing_and_errors(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["targets"]) == 0
    assert "ref:coerce-inflight" in capsys.readouterr().out
    assert main(["scenarios", "-s", "collide-7/*", "--random-seed", "3", "-v"]) == 0
    assert "random/seed-3" in capsys.readouterr().out
    assert main(["run", "-t", "no-such-target"]) == 2
