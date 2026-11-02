"""Failure minimisation by delta debugging (Zeller & Hildebrandt's ddmin).

Given a failing scenario, find a 1-minimal sub-sequence of its steps that still
fails with (a superset of) the same rule signature. Every candidate is
normalised first, so the harness itself never violates the protocol while
shrinking. The result is re-run ``confirm`` times; a minimisation that does
not reproduce every time is reported as unstable rather than returned.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .oracle import Verdict
from .scenario import Scenario, Step

Oracle = Callable[[Scenario], Verdict]


@dataclass
class Minimization:
    original: Scenario
    minimal: Scenario
    signature: frozenset[str]
    runs: int
    confirmed: int
    confirm: int
    log: list[str] = field(default_factory=lambda: list[str]())

    @property
    def stable(self) -> bool:
        return self.confirmed == self.confirm


def ddmin(steps: list[Step], fails: Callable[[list[Step]], bool]) -> list[Step]:
    """Classic ddmin: returns a 1-minimal failing subsequence of ``steps``."""
    n = 2
    while len(steps) >= 2:
        chunk = max(len(steps) // n, 1)
        subsets = [steps[i : i + chunk] for i in range(0, len(steps), chunk)]
        reduced = False
        for i, subset in enumerate(subsets):
            if fails(subset):
                steps, n, reduced = subset, 2, True
                break
            complement = [s for j, sub in enumerate(subsets) if j != i for s in sub]
            if fails(complement):
                steps, n, reduced = complement, max(n - 1, 2), True
                break
        if not reduced:
            if n >= len(steps):
                break
            n = min(n * 2, len(steps))
    return steps


def minimize(
    scenario: Scenario, oracle: Oracle, *, rules: frozenset[str] | None = None, confirm: int = 3
) -> Minimization:
    cache: dict[tuple[Step, ...], bool] = {}
    log: list[str] = []
    runs = 0

    baseline = oracle(scenario.normalized())
    runs += 1
    signature = rules if rules is not None else baseline.signature
    if not signature or not signature <= baseline.signature:
        raise ValueError(f"scenario does not fail with {sorted(signature)} (got {sorted(baseline.signature)})")

    def fails(candidate: list[Step]) -> bool:
        nonlocal runs
        normalized = scenario.with_steps(tuple(candidate)).normalized().steps
        if normalized in cache:
            return cache[normalized]
        runs += 1
        verdict = oracle(scenario.with_steps(normalized))
        result = signature <= verdict.signature
        cache[normalized] = result
        log.append(f"{'FAIL' if result else 'pass'} {len(normalized):>2} steps: {sorted(verdict.signature)}")
        return result

    steps = ddmin(list(scenario.normalized().steps), fails)
    minimal = scenario.with_steps(scenario.with_steps(tuple(steps)).normalized().steps, "/min")
    confirmed = 0
    for _ in range(confirm):
        runs += 1
        if signature <= oracle(minimal).signature:
            confirmed += 1
    return Minimization(scenario, minimal, signature, runs, confirmed, confirm, log)
