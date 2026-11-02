# MCP Faultline report: FL-001 Typed JSON-RPC request-id isolation

## Provenance

- **harness**: `mcp-faultline 0.1.0`
- **harness_commit**: `feeee275b946002402e1d5239065e363adb26062`
- **python**: `3.12.14`
- **platform**: `Windows-11-10.0.26300-SP0`
- **started_utc**: `2026-11-02T19:44:09+00:00`
- **protocol_revision**: `2025-11-25`
- **fault**: `None`

## Targets

| target | implementation | version | pinned | transport |
|---|---|---|---|---|
| `py-stdio` | python-sdk | 2.3.0 | 2.3.0 | stdio |

## Result matrix

| scenario | `py-stdio` |
|---|---|
| random/seed-6 | FAIL R3,R6 |

**0 passed, 1 failed** of 1 runs.

## Violations

### `py-stdio` - random/seed-6
- **R3** (every non-cancelled request receives a response): request 9007199254740991 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "9007199254740991" suppressed the response to 9007199254740991
- trace: `evidence/fl001/random-seed-6/traces/py_stdio__random_seed_6.json`

## Rules

- **WIRE**: inbound message is valid JSON-RPC 2.0
- **R1**: response id matches an issued request id exactly (type and value)
- **R2**: at most one response per request
- **R3**: every non-cancelled request receives a response
- **R4**: response payload belongs to its own request
- **R5**: HTTP response delivered on its request's stream
- **R6**: cancelling one id never suppresses another id's response
- **R7**: session recovers and serves a fresh request
