# Architecture

```
            ┌────────────┐   Step[]    ┌──────────┐  JSON-RPC   ┌──────────────┐  stdio/HTTP  ┌──────────────────┐
experiments │ Scenario   ├────────────►│  engine  ├────────────►│ Connection   ├─────────────►│ target fixture   │
 (fl001.py) └────────────┘             │ Recorder │◄────────────┤ (+FaultyConn)│◄─────────────┤ (SDK or ref)     │
                                       └────┬─────┘  Inbound     └──────────────┘              └──────────────────┘
                                            │ Trace (events + provenance)
                       ┌────────────────────┼─────────────────────┐
                       ▼                    ▼                     ▼
                  oracle.evaluate      report / diff         export (pytest, standalone)
                       │
                       ▼ Verdict.signature
                  minimize.ddmin ──► re-runs engine on candidate sub-scenarios
```

## Modules

| module | responsibility | depends on |
|---|---|---|
| `jsonrpc` | id typing (`id_key` is injective), wire validation | - |
| `scenario` | serialisable steps (`call`, `cancel`, `release`, `sync`), `normalized()` keeps candidates protocol-legal | `jsonrpc` |
| `transports` | `StdioConnection`, `HttpConnection` (one thread per POST, SSE + JSON bodies), process lifecycle | - |
| `faults` | `FaultyConnection`: deterministic inbound rewrites (negative controls) | `transports` |
| `targets` | registry: launch command, transport, detected vs pinned version | `transports` |
| `engine` | run one scenario: handshake, steps, finalise, recovery probe; record every message | `scenario`, `transports` |
| `oracle` | rules R1-R7 + WIRE over a trace; observations for SHOULD-level behaviour | `jsonrpc`, `trace` |
| `minimize` | ddmin with result cache and N-fold confirmation | `oracle`, `scenario` |
| `export` | regression case (JSON + pytest) and stdlib-only reproduction script | `trace`, `oracle` |
| `controls` | expected verdict of every mutant/fault on every scenario | `scenario` |
| `report` | results matrix, cross-target divergence, Markdown | `oracle` |
| `cli` | `faultline` subcommands | all |

The reference server (`reference_server.py`) deliberately does **not** import
`jsonrpc`. If it shared code with the oracle, one bug could hide in both.

## Key decisions

1. **The harness is the client, at the wire level.** Using an SDK client
   would let its id handling mask the server's. The engine writes raw frames
   and records the HTTP stream each response arrives on, which is what makes
   rule R5 (stream routing) checkable.
2. **Gates instead of sleeps.** `gate(tag)` blocks until `release(tag)`, so
   "the second request completes first" is a property of the scenario. The
   only timing parameters are upper bounds for detecting *missing* responses
   (`completion`, default 2 s) and duplicates (`settle`, default 0.4 s).
3. **Control ids cannot collide.** Harness ids are `fl-…` strings, which no
   numeric coercion can fold onto a scenario id.
4. **Finalise releases everything.** Every gate is opened after the scenario,
   including the gates of cancelled requests. That separates "cancelled and
   silent" (fine) from "cancellation ignored" (observation) and from
   "never answered" (violation).
5. **Minimisation works on steps, not bytes.** Every ddmin candidate is
   normalised (no id reuse, no cancel of an unissued id), so shrinking never
   makes the *harness* violate the protocol. A minimal case is exported only if
   it reproduces on every confirmation run.

## Extending: a new experiment

1. Add `src/mcp_faultline/experiments/flNNN.py` with `ID`, `TITLE`,
   `scenarios()` and `generate(seed)`.
2. If it needs new server behaviour, add the same tool to all three fixture
   servers and to the reference server. Behaviour must be identical across
   them, because differential results are only meaningful then.
3. Add oracle rules with a spec citation, unit tests on hand-built traces
   (`tests/conftest.py::TraceBuilder`), and **at least one mutant or fault**
   whose detection the new rules must prove in `controls.py`.

## Extending: a new target

Add a `Target` in `targets.py` with a launch function and a version detector,
add a pin to `PINNED`, and add the fixture under `targets/`. Run
`faultline controls` and the SDK test suite before publishing results.
