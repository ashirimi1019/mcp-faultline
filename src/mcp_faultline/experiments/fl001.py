"""FL-001: Typed JSON-RPC request-id isolation.

JSON-RPC 2.0 ids are a String or a Number, and ``7`` and ``"7"`` are different
ids. MCP 2025-11-25 restates this ("Requests MUST include a string or integer
ID") and adds cancellation by id. An implementation that keys any internal
table by ``str(id)`` or folds ``"7"`` to ``7`` merges two live requests.

The fixed matrix pairs every *collision* case with a *control* that differs
only in that the ids cannot collide, so a failure is attributable to typed-id
handling rather than to concurrency or cancellation in general.
"""

from __future__ import annotations

import random

from ..jsonrpc import RequestId
from ..scenario import SYNC, Scenario, Step, call, cancel, release

ID = "FL-001"
TITLE = "Typed JSON-RPC request-id isolation"


def _pair(a: RequestId, b: RequestId, name: str, desc: str, tags: tuple[str, ...]) -> list[Scenario]:
    ta, tb = f"t-{type(a).__name__}-{a}", f"t-{type(b).__name__}-{b}"
    return [
        Scenario(
            f"{name}/out-of-order",
            (call(a, ta), call(b, tb), SYNC, release(tb), release(ta)),
            f"{desc}: both in flight, second completes first.",
            tags,
        ),
        Scenario(
            f"{name}/cancel-first",
            (call(a, ta), call(b, tb), SYNC, cancel(a), SYNC, release(tb)),
            f"{desc}: cancel {a!r} only; {b!r} must still complete.",
            tags,
        ),
        Scenario(
            f"{name}/cancel-second",
            (call(a, ta), call(b, tb), SYNC, cancel(b), SYNC, release(ta)),
            f"{desc}: cancel {b!r} only; {a!r} must still complete.",
            tags,
        ),
    ]


def scenarios() -> list[Scenario]:
    out: list[Scenario] = []
    # Collision cases: same text, different JSON type.
    out += _pair(7, "7", "collide-7", 'integer 7 vs string "7"', ("collision",))
    out += _pair("7", 7, "collide-7-strfirst", 'string "7" then integer 7', ("collision",))
    out += _pair(0, "0", "collide-0", 'integer 0 vs string "0"', ("collision",))
    out += _pair(-1, "-1", "collide-neg", 'integer -1 vs string "-1"', ("collision",))
    # Non-canonical numeric string (cf. python-sdk#3432).
    out += _pair(7, "07", "noncanonical-07", 'integer 7 vs string "07"', ("noncanonical",))
    # Controls: identical shape, ids that cannot collide under any coercion.
    out += _pair(7, 8, "control-int", "integers 7 and 8", ("control",))
    out += _pair("a7", "b7", "control-str", 'strings "a7" and "b7"', ("control",))
    out += _pair(7, "x7", "control-mixed", 'integer 7 and string "x7"', ("control",))
    return out


ID_POOL: tuple[RequestId, ...] = (0, 1, 7, 42, -1, 2**31, 9007199254740991)


def generate(seed: int, size: int = 4) -> Scenario:
    """A random but fully seed-determined FL-001 scenario.

    Picks ``size`` distinct ids including at least one int/str twin pair,
    issues them in random order, then interleaves random cancels and releases.
    """
    rng = random.Random(seed)
    base = rng.choice(ID_POOL)
    ids: list[RequestId] = [base, str(base)]
    while len(ids) < size:
        n = rng.choice(ID_POOL)
        candidate: RequestId = rng.choice([n, str(n), f"s{n}"])
        if all(type(candidate) is not type(i) or candidate != i for i in ids):
            ids.append(candidate)
    rng.shuffle(ids)
    steps: list[Step] = [call(i, f"g{k}") for k, i in enumerate(ids)]
    steps.append(SYNC)
    tail: list[Step] = [release(f"g{k}") for k in range(len(ids))]
    for i in rng.sample(ids, rng.randint(0, len(ids) // 2 + 1)):
        tail.append(cancel(i))
    rng.shuffle(tail)
    # A sync before each release keeps cancel-vs-release ordering deterministic.
    for step in tail:
        if step.op == "release":
            steps.append(SYNC)
        steps.append(step)
    return Scenario(f"random/seed-{seed}", tuple(steps), f"seeded random FL-001 scenario (seed={seed})", ("random",))
