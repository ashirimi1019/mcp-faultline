"""Glue: target + optional fault + scenario -> trace + verdict."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import TypeVar

from .engine import execute
from .faults import FaultyConnection
from .oracle import Verdict, evaluate
from .scenario import Scenario
from .targets import get_target, repo_root
from .trace import Trace, base_provenance
from .transports import Connection


@dataclass(frozen=True)
class RunResult:
    trace: Trace
    verdict: Verdict


def run(
    target_name: str,
    scenario: Scenario,
    *,
    fault: str | None = None,
    seed: int = 0,
    timeout: float = 5.0,
    completion: float = 2.0,
    settle: float = 0.4,
) -> RunResult:
    target = get_target(target_name)
    provenance = {**base_provenance(repo_root()), **target.provenance(), "fault": fault, "seed": seed}
    conn: Connection = target.connect()
    if fault is not None:
        conn = FaultyConnection(conn, fault, seed)
    trace = execute(
        conn,
        scenario,
        target=target_name,
        provenance=provenance,
        timeout=timeout,
        completion=completion,
        settle=settle,
    )
    return RunResult(trace, evaluate(trace))


def replay(trace: Trace, *, timeout: float = 5.0) -> RunResult:
    """Re-execute the scenario recorded in ``trace`` against the same target and fault."""
    scenario = Scenario.from_json(trace.scenario)
    fault = trace.provenance.get("fault")
    seed = int(trace.provenance.get("seed") or 0)
    return run(trace.target, scenario, fault=fault, seed=seed, timeout=timeout)


T = TypeVar("T")
R = TypeVar("R")


def parallel_map(fn: Callable[[T], R], items: Iterable[T], jobs: int) -> Iterator[R]:
    """Map in input order. Runs are independent processes, so threads are enough."""
    if jobs <= 1:
        yield from map(fn, items)
        return
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        yield from pool.map(fn, items)
