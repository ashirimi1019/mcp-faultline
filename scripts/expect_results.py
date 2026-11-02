"""Assert the outcome of a `faultline run` results.json (used by the fix-validation workflow).

python scripts/expect_results.py results.json --failed 0
python scripts/expect_results.py results.json --min-failed 1 --allowed-rules R3,R4,R6 --require-rule R6
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results")
    parser.add_argument("--failed", type=int, help="exact number of failing runs")
    parser.add_argument("--min-failed", type=int, help="minimum number of failing runs")
    parser.add_argument("--allowed-rules", help="comma-separated rules failures may violate")
    parser.add_argument("--require-rule", help="a rule at least one failure must violate")
    args = parser.parse_args()

    results = json.load(open(args.results, encoding="utf-8"))["results"]
    failed = [r for r in results if not r["passed"]]
    rules = Counter(v["rule"] for r in failed for v in r["violations"])
    by_target = Counter(r["target"] for r in failed)
    passed = len(results) - len(failed)
    print(f"{args.results}: {passed} passed, {len(failed)} failed; rules {dict(rules)}; {dict(by_target)}")

    problems: list[str] = []
    if args.failed is not None and len(failed) != args.failed:
        problems.append(f"expected exactly {args.failed} failures")
    if args.min_failed is not None and len(failed) < args.min_failed:
        problems.append(f"expected at least {args.min_failed} failures")
    if args.allowed_rules and set(rules) - set(args.allowed_rules.split(",")):
        problems.append(f"unexpected rules {sorted(set(rules) - set(args.allowed_rules.split(',')))}")
    if args.require_rule and args.require_rule not in rules:
        problems.append(f"no failure violates {args.require_rule}")
    for p in problems:
        print("EXPECTATION FAILED:", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
