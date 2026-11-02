# MCP Faultline

Protocol fault injection, differential testing and failure minimisation for the
[Model Context Protocol](https://modelcontextprotocol.io).

MCP Faultline drives the **official MCP SDKs** over real transports (stdio and
Streamable HTTP) with raw JSON-RPC. It checks their behaviour against
assertions derived from the specification, compares SDKs against each other,
and shrinks any failure to a minimal, dependency-free reproduction. The
harness itself uses only the Python standard library and needs no API keys.

> **Status: alpha.** One experiment (FL-001) is complete. Results below are from
> the pinned SDK versions and can be regenerated with one command.

## What it found (FL-001: typed request-id isolation)

JSON-RPC treats `7` and `"7"` as different request ids. FL-001 runs 24
scenarios (concurrent twins, out-of-order completion, cancellation of one twin,
plus matched non-colliding controls) against 9 SDK targets at protocol revision
**2025-11-25**:

| SDK (pinned) | stdio | HTTP (SSE) | HTTP (JSON) |
|---|---|---|---|
| Python `mcp` 2.3.0 | 19/24 | 11/24 | 11/24 |
| TypeScript `@modelcontextprotocol/sdk` 1.32.2 | 24/24 ¹ | 24/24 ¹ | 24/24 ¹ |
| TypeScript `@modelcontextprotocol/server` 2.4.0 | 24/24 | 24/24 | 24/24 |

¹ One SHOULD-level observation: cancellation of request id `0` is ignored. This
is a known issue ([typescript-sdk#2283](https://github.com/modelcontextprotocol/typescript-sdk/issues/2283)), fixed in v2.

Every control scenario passes on every SDK, so the failures come from typed-id
handling and not from concurrency or cancellation in general. Details,
including which findings are already known upstream, are in
[docs/fl-001.md](docs/fl-001.md):

* **python-sdk, all transports:** the dispatcher keys in-flight requests by
  `coerce_request_id(id)`, so cancelling the earlier of `7`/`"7"` cancels the
  later one. Automatically minimised to 3 steps. Patch experiments show the
  Streamable HTTP fix proposed in
  [python-sdk#3786](https://github.com/modelcontextprotocol/python-sdk/issues/3786)
  is necessary but not sufficient.
* **python-sdk, Streamable HTTP:** response streams keyed by `str(id)`
  ([#3786](https://github.com/modelcontextprotocol/python-sdk/issues/3786), known; reproduced).
* **python-sdk:** non-canonical `"07"` folds to `7`
  ([#3432](https://github.com/modelcontextprotocol/python-sdk/issues/3432), known; reproduced).

## How it works

```
scenario ──► engine ──► transport (stdio | Streamable HTTP) ──► SDK fixture server
   ▲            │            ▲ optional fault injector
   │            ▼
 ddmin ◄── oracle (R1-R7, WIRE) ◄── trace (+ provenance)  ──► report / diff / export
```

* **Deterministic.** Tools block on gates that the harness opens, so
  completion order is part of the scenario. Nothing depends on sleeps.
* **Independent oracle.** Rules come from JSON-RPC 2.0 and MCP 2025-11-25, not
  from any SDK's schema. SHOULD-level behaviour is reported as an
  observation, never as a failure.
* **Proves it can fail.** `faultline controls` runs 5 planted-defect mutants of
  a stdlib reference server and 5 injected wire faults. Each one must be
  flagged exactly where it can occur and nowhere else: 11/11 controls hold.
* **Reproducible evidence.** Every run writes a trace containing every wire
  message, its channel and timing, the scenario, and provenance (SDK version
  vs pin, protocol revision, harness commit, interpreter, platform).
* **Minimisation and export.** Delta debugging shrinks a failing scenario,
  confirms the result is stable, then exports a pytest regression test and a
  stdlib-only reproduction script.

See [docs/architecture.md](docs/architecture.md).

## Quick start

Requirements: Python ≥ 3.10, and Node ≥ 20 for the TypeScript targets.

```sh
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[targets,dev]"                    # harness + pinned Python SDK
npm ci --prefix targets/ts && npm ci --prefix targets/ts-v2

faultline targets                                  # detected vs pinned SDK versions
faultline controls                                 # harness self-test (must be 11/11)
faultline run FL-001 -o runs/now                   # all SDK targets -> results.json, report.md, traces/
faultline inspect runs/now/traces/py_stdio__collide_7_cancel_first.json
faultline minimize runs/now/traces/py_stdio__collide_7_cancel_first.json -o regressions
faultline diff runs/now/results.json               # cross-SDK divergences
```

Run only the keyless, SDK-free tests with `pytest -m "not sdk"`, or everything
with `pytest`.

## Project layout

| path | purpose |
|---|---|
| `src/mcp_faultline/` | harness (stdlib only): transports, engine, oracle, faults, minimiser, export, CLI |
| `src/mcp_faultline/reference_server.py` | stdlib MCP server with switchable planted defects |
| `targets/python`, `targets/ts`, `targets/ts-v2` | fixture servers on the official SDKs (pinned) |
| `evidence/fl001/` | committed results, minimal trace and standalone reproduction |
| `scripts/fix_validation.py` | build patched SDK copies to test candidate fixes |
| `docs/` | architecture, FL-001, audit, threat model, upstream drafts |

## Responsible use

This is a testing tool for implementations you run locally. See
[SECURITY.md](SECURITY.md) and [docs/threat-model.md](docs/threat-model.md).
Defects in third-party SDKs are reported upstream, following each project's
process, and only after checking for existing reports.

## License

MIT
