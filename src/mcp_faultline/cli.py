"""``faultline`` command-line interface."""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .controls import CONTROLS, Control
from .experiments import fl001
from .export import regression_case, slug, standalone_repro
from .faults import FAULTS
from .jsonrpc import format_id
from .minimize import minimize
from .oracle import RULES, Verdict, evaluate
from .report import RESULTS_FORMAT, divergences, markdown, matrix
from .runner import RunResult, parallel_map, replay, run
from .scenario import Scenario
from .targets import PROTOCOL_REVISION, SDK_TARGETS, TARGETS, get_target, repo_root
from .trace import Trace, base_provenance


def _out(text: str = "") -> None:
    sys.stdout.write(text + "\n")
    sys.stdout.flush()


def _select(patterns: list[str] | None, seeds: list[int]) -> list[Scenario]:
    chosen = fl001.scenarios()
    if patterns:
        chosen = [s for s in chosen if any(fnmatch.fnmatch(s.name, p) for p in patterns)]
    chosen += [fl001.generate(seed) for seed in seeds]
    return chosen


def _summary(verdict: Verdict) -> str:
    if verdict.passed:
        obs = (
            f"  (observed: {', '.join(sorted({o.rule for o in verdict.observations}))})" if verdict.observations else ""
        )
        return "pass" + obs
    return "FAIL " + ",".join(sorted(verdict.signature))


def _result_record(result: RunResult, trace_path: Path | None) -> dict[str, Any]:
    record = result.verdict.to_json()
    record["implementation"] = result.trace.provenance.get("implementation")
    record["provenance"] = result.trace.provenance
    record["trace"] = str(trace_path) if trace_path else None
    return record


def cmd_targets(_: argparse.Namespace) -> int:
    _out(f"protocol revision: {PROTOCOL_REVISION}")
    for name, t in TARGETS.items():
        version = t.version() or "NOT INSTALLED"
        pin = t.provenance()["pinned_version"]
        flag = "" if pin is None or version == pin else f"  (pinned {pin})"
        _out(f"  {name:24} {t.implementation:15} {version:14} {t.transport:10} {t.description}{flag}")
    return 0


def cmd_scenarios(args: argparse.Namespace) -> int:
    for s in _select(args.scenario, args.random_seed or []):
        _out(f"{s.name}  [{', '.join(s.tags)}]  {s.description}")
        if args.verbose:
            for i, step in enumerate(s.steps):
                _out(f"    {i:>2}. {step.describe()}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    targets = args.target or list(SDK_TARGETS)
    for t in targets:
        get_target(t)
    scenarios = _select(args.scenario, args.random_seed or [])
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.out or f"runs/{stamp}")
    records: list[dict[str, Any]] = []
    jobs = [(t, s) for t in targets for s in scenarios]

    def one(job: tuple[str, Scenario]) -> RunResult:
        return run(job[0], job[1], fault=args.fault, seed=args.seed, timeout=args.timeout)

    current = None
    for (target, scenario), result in zip(jobs, parallel_map(one, jobs, args.jobs), strict=True):
        if target != current:
            current = target
            _out(f"== {target}")
        trace_path = out_dir / "traces" / f"{slug(target)}__{slug(scenario.name)}.json"
        result.trace.dump(trace_path)
        records.append(_result_record(result, trace_path))
        _out(f"   {scenario.name:34} {_summary(result.verdict)}")
        if not result.verdict.passed and args.verbose:
            for v in result.verdict.violations:
                _out(f"      {v.rule}: {v.message}")
    doc = {
        "format": RESULTS_FORMAT,
        "experiment": f"{fl001.ID} {fl001.TITLE}",
        "environment": {**base_provenance(repo_root()), "protocol_revision": PROTOCOL_REVISION, "fault": args.fault},
        "results": records,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    (out_dir / "report.md").write_text(markdown(doc), encoding="utf-8")
    failed = sum(1 for r in records if not r["passed"])
    _out(f"\n{len(records) - failed} passed, {failed} failed. Results: {out_dir / 'results.json'}")
    divs = divergences(records)
    if divs and len(targets) > 1:
        _out(f"{len(divs)} scenario(s) diverge across targets; see {out_dir / 'report.md'}")
    return 1 if failed and args.strict else 0


def cmd_diff(args: argparse.Namespace) -> int:
    doc = json.loads(Path(args.results).read_text(encoding="utf-8"))
    divs = divergences(doc["results"])
    if not divs:
        _out("no divergences")
        return 0
    for d in divs:
        _out(d.scenario)
        for t, o in d.outcomes.items():
            _out(f"   {t:16} {o}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    doc = json.loads(Path(args.results).read_text(encoding="utf-8"))
    text = markdown(doc)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        _out(f"wrote {args.output}")
    else:
        _out(text)
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    trace = Trace.load(Path(args.trace))
    verdict = evaluate(trace)
    p = trace.provenance
    _out(
        f"target   {trace.target}  ({p.get('implementation')} {p.get('implementation_version')}, {p.get('transport')})"
    )
    _out(f"protocol {p.get('protocol_revision')}   fault {p.get('fault')}   seed {p.get('seed')}")
    _out(f"scenario {trace.scenario['name']}")
    for i, step in enumerate(Scenario.from_json(trace.scenario).steps):
        _out(f"   {i:>2}. {step.describe()}")
    flagged = {seq for f in verdict.violations for seq in f.evidence}
    _out("\ntimeline")
    for e in trace.events:
        if not args.all and ('"fl-ctl-' in e.raw or e.dir == "note"):
            continue
        mark = "!!" if e.seq in flagged else "  "
        arrow = {"out": "->", "in": "<-", "note": "##"}[e.dir]
        _out(f" {mark}{e.seq:>4} {e.at:8.3f}s {arrow} {e.channel:22} {e.raw[:140]}")
    _out("\nverdict  " + _summary(verdict))
    for v in verdict.violations:
        _out(f"   {v.rule} {RULES[v.rule]}: {v.message}")
    for o in verdict.observations:
        _out(f"   (observation) {o.rule}: {o.message}")
    return 0 if verdict.passed else 1


def cmd_replay(args: argparse.Namespace) -> int:
    trace = Trace.load(Path(args.trace))
    recorded = evaluate(trace)
    reproduced = 0
    for i in range(args.times):
        result = replay(trace, timeout=args.timeout)
        same = result.verdict.signature == recorded.signature
        reproduced += same
        _out(
            f"replay {i + 1}: {_summary(result.verdict)}  {'(matches recorded)' if same else '(DIFFERS from recorded)'}"
        )
    _out(f"recorded {_summary(recorded)}; reproduced {reproduced}/{args.times}")
    return 0 if reproduced == args.times else 1


def cmd_minimize(args: argparse.Namespace) -> int:
    trace = Trace.load(Path(args.trace))
    scenario = Scenario.from_json(trace.scenario)
    fault = trace.provenance.get("fault")
    seed = int(trace.provenance.get("seed") or 0)
    last: dict[str, RunResult] = {}

    def oracle(candidate: Scenario) -> Verdict:
        result = run(trace.target, candidate, fault=fault, seed=seed, timeout=args.timeout)
        last[json.dumps(candidate.to_json()["steps"])] = result
        return result.verdict

    rules = frozenset(args.rule) if args.rule else None
    m = minimize(scenario, oracle, rules=rules, confirm=args.confirm)
    for line in m.log:
        _out("  " + line)
    _out(f"\n{len(m.original.steps)} -> {len(m.minimal.steps)} steps in {m.runs} runs; signature {sorted(m.signature)}")
    _out(f"confirmed {m.confirmed}/{m.confirm} {'(stable)' if m.stable else '(UNSTABLE - not exported)'}")
    for i, step in enumerate(m.minimal.steps):
        _out(f"   {i:>2}. {step.describe()}")
    if not m.stable:
        return 1
    result = last[json.dumps(m.minimal.to_json()["steps"])]
    out_dir = Path(args.out)
    trace_path = out_dir / f"{slug(trace.target)}__{slug(m.minimal.name)}.trace.json"
    result.trace.dump(trace_path)
    case, test = regression_case(result.trace, result.verdict, out_dir)
    _out(f"\nminimal trace : {trace_path}\nregression    : {test}\ncase          : {case}")
    if result.trace.provenance.get("transport") == "stdio" and fault is None:
        repro = standalone_repro(
            result.trace, result.verdict, out_dir / f"repro_{slug(trace.target)}_{slug(m.minimal.name)}.py"
        )
        _out(f"standalone    : {repro}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    trace = Trace.load(Path(args.trace))
    verdict = evaluate(trace)
    case, test = regression_case(trace, verdict, Path(args.out))
    _out(f"regression: {test}\ncase      : {case}")
    if args.standalone:
        path = standalone_repro(
            trace, verdict, Path(args.out) / f"repro_{slug(trace.target)}_{slug(trace.scenario['name'])}.py"
        )
        _out(f"standalone: {path}")
    return 0


def cmd_controls(args: argparse.Namespace) -> int:
    scenarios = fl001.scenarios()
    held = 0
    for control in CONTROLS:
        if args.only and not any(fnmatch.fnmatch(control.name, p) for p in args.only):
            continue
        wrong: list[str] = []
        caught = 0

        def one(s: Scenario, control: Control = control) -> Verdict:
            return run(control.target, s, fault=control.fault, seed=0, timeout=args.timeout).verdict

        for s, verdict in zip(scenarios, parallel_map(one, scenarios, args.jobs), strict=True):
            expect_fail = control.must_fail(s)
            caught += expect_fail and not verdict.passed
            if expect_fail == verdict.passed:
                wrong.append(f"{s.name}: expected {'FAIL' if expect_fail else 'pass'}, got {_summary(verdict)}")
        ok = not wrong
        held += ok
        expected = sum(control.must_fail(s) for s in scenarios)
        _out(f"{'HOLDS ' if ok else 'BROKEN'} {control.name:28} detected {caught}/{expected}  - {control.rationale}")
        for w in wrong:
            _out(f"        {w}")
    total = len([c for c in CONTROLS if not args.only or any(fnmatch.fnmatch(c.name, p) for p in args.only)])
    _out(f"\n{held}/{total} controls hold")
    return 0 if held == total else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="faultline", description="MCP protocol fault injection and differential testing."
    )
    parser.add_argument("--version", action="version", version=f"mcp-faultline {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("targets", help="list targets with detected SDK versions")
    p.set_defaults(func=cmd_targets)

    def scenario_opts(p: argparse.ArgumentParser) -> None:
        p.add_argument("-s", "--scenario", action="append", help="glob over scenario names (repeatable)")
        p.add_argument("--random-seed", type=int, action="append", help="add a seeded random scenario (repeatable)")

    p = sub.add_parser("scenarios", help="list FL-001 scenarios")
    scenario_opts(p)
    p.add_argument("-v", "--verbose", action="store_true")
    p.set_defaults(func=cmd_scenarios)

    p = sub.add_parser("run", help="run FL-001 against one or more targets")
    p.add_argument("experiment", nargs="?", default=fl001.ID, choices=[fl001.ID])
    p.add_argument("-t", "--target", action="append", help=f"target (repeatable; default: {', '.join(SDK_TARGETS)})")
    scenario_opts(p)
    p.add_argument("--fault", choices=FAULTS)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--timeout", type=float, default=5.0)
    p.add_argument("-o", "--out", help="output directory (default runs/<utc-timestamp>)")
    p.add_argument("--strict", action="store_true", help="exit 1 if any run fails")
    p.add_argument("-j", "--jobs", type=int, default=4, help="parallel runs (each run is its own target process)")
    p.add_argument("-v", "--verbose", action="store_true")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("diff", help="show cross-target divergences in a results.json")
    p.add_argument("results")
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("report", help="render a Markdown report from results.json")
    p.add_argument("results")
    p.add_argument("-o", "--output")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("inspect", help="show a trace timeline with oracle findings")
    p.add_argument("trace")
    p.add_argument("-a", "--all", action="store_true", help="include harness control traffic")
    p.set_defaults(func=cmd_inspect)

    p = sub.add_parser("replay", help="re-execute a trace and compare verdicts")
    p.add_argument("trace")
    p.add_argument("-n", "--times", type=int, default=3)
    p.add_argument("--timeout", type=float, default=5.0)
    p.set_defaults(func=cmd_replay)

    p = sub.add_parser("minimize", help="delta-debug a failing trace to a minimal reproduction")
    p.add_argument("trace")
    p.add_argument("-o", "--out", default="regressions")
    p.add_argument("--rule", action="append", help="rule(s) the minimal case must still violate")
    p.add_argument("--confirm", type=int, default=3)
    p.add_argument("--timeout", type=float, default=5.0)
    p.set_defaults(func=cmd_minimize)

    p = sub.add_parser("export", help="export a trace as a regression test (and standalone repro)")
    p.add_argument("trace")
    p.add_argument("-o", "--out", default="regressions")
    p.add_argument("--standalone", action="store_true")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("controls", help="harness self-test: mutants and injected faults must be detected")
    p.add_argument("--only", action="append", help="glob over control names")
    p.add_argument("-j", "--jobs", type=int, default=8)
    p.add_argument("--timeout", type=float, default=5.0)
    p.set_defaults(func=cmd_controls)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (KeyError, ValueError) as exc:
        _out(f"error: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["main", "format_id", "matrix"]
