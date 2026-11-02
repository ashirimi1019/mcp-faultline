"""Result aggregation, cross-target differential comparison and Markdown reports."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from .oracle import RULES

RESULTS_FORMAT = "mcp-faultline/results@1"


@dataclass(frozen=True)
class Divergence:
    scenario: str
    outcomes: dict[str, str]  # target -> compact outcome
    implementations: dict[str, str]  # target -> implementation


def compact(result: dict[str, Any]) -> str:
    """One comparable string per (scenario, target): verdict signature + per-request outcome."""
    rules = ",".join(sorted({v["rule"] for v in result["violations"]})) or "ok"
    outs = " ".join(f"{k}={v}" for k, v in sorted(result["outcomes"].items()))
    return f"[{rules}] {outs}"


def divergences(results: list[dict[str, Any]]) -> list[Divergence]:
    """Scenarios whose observable outcome differs between targets."""
    by_scenario: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for r in results:
        by_scenario[r["scenario"]][r["target"]] = r
    out: list[Divergence] = []
    for scenario, per_target in sorted(by_scenario.items()):
        outcomes = {t: compact(r) for t, r in sorted(per_target.items())}
        if len(set(outcomes.values())) > 1:
            out.append(
                Divergence(scenario, outcomes, {t: r.get("implementation", "?") for t, r in sorted(per_target.items())})
            )
    return out


def matrix(results: list[dict[str, Any]]) -> tuple[list[str], list[str], dict[tuple[str, str], str]]:
    scenarios = sorted({r["scenario"] for r in results})
    targets = list(dict.fromkeys(r["target"] for r in results))
    cells: dict[tuple[str, str], str] = {}
    for r in results:
        cells[(r["scenario"], r["target"])] = (
            "pass" if r["passed"] else "FAIL " + ",".join(sorted({v["rule"] for v in r["violations"]}))
        )
    return scenarios, targets, cells


def markdown(doc: dict[str, Any]) -> str:
    results: list[dict[str, Any]] = doc["results"]
    lines = [f"# MCP Faultline report: {doc.get('experiment', '')}", ""]
    env = doc.get("environment", {})
    if env:
        lines += ["## Provenance", ""]
        lines += [f"- **{k}**: `{v}`" for k, v in env.items()]
        lines.append("")
    lines += ["## Targets", "", "| target | implementation | version | pinned | transport |", "|---|---|---|---|---|"]
    seen: set[str] = set()
    for r in results:
        if r["target"] in seen:
            continue
        seen.add(r["target"])
        p = r.get("provenance", {})
        lines.append(
            f"| `{r['target']}` | {p.get('implementation')} | {p.get('implementation_version')} | "
            f"{p.get('pinned_version') or '-'} | {p.get('transport')} |"
        )
    scenarios, targets, cells = matrix(results)
    lines += ["", "## Result matrix", "", "| scenario | " + " | ".join(f"`{t}`" for t in targets) + " |"]
    lines.append("|---|" + "---|" * len(targets))
    for s in scenarios:
        lines.append(f"| {s} | " + " | ".join(cells.get((s, t), "-") for t in targets) + " |")
    failed = [r for r in results if not r["passed"]]
    passed = len(results) - len(failed)
    lines += ["", f"**{passed} passed, {len(failed)} failed** of {len(results)} runs.", ""]
    if failed:
        lines += ["## Violations", ""]
        for r in failed:
            lines.append(f"### `{r['target']}` - {r['scenario']}")
            for v in r["violations"]:
                lines.append(f"- **{v['rule']}** ({RULES.get(v['rule'], '')}): {v['message']}")
            if r.get("trace"):
                lines.append(f"- trace: `{r['trace']}`")
            lines.append("")
    divs = divergences(results)
    if divs:
        lines += ["## Cross-target divergences", ""]
        for d in divs:
            lines.append(f"### {d.scenario}")
            for t, o in d.outcomes.items():
                lines.append(f"- `{t}` ({d.implementations[t]}): `{o}`")
            lines.append("")
    lines += ["## Rules", ""] + [f"- **{k}**: {v}" for k, v in RULES.items()]
    return "\n".join(lines) + "\n"
