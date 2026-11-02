# MCP Faultline report: FL-001 Typed JSON-RPC request-id isolation

## Provenance

- **harness**: `mcp-faultline 0.1.0`
- **harness_commit**: `7a5db5a5457e7dd9dc7b1482b862da3e8cfa16d2`
- **python**: `3.12.14`
- **platform**: `Windows-11-10.0.26300-SP0`
- **started_utc**: `2026-11-02T20:37:33+00:00`
- **protocol_revision**: `2025-11-25`
- **fault**: `None`

## Targets

| target | implementation | version | pinned | transport |
|---|---|---|---|---|
| `py-stdio` | python-sdk | 2.3.1.dev17+d7845c0 | 2.3.0 | stdio |
| `py-http-sse` | python-sdk | 2.3.1.dev17+d7845c0 | 2.3.0 | http-sse |
| `py-http-json` | python-sdk | 2.3.1.dev17+d7845c0 | 2.3.0 | http-json |

## Result matrix

| scenario | `py-stdio` | `py-http-sse` | `py-http-json` |
|---|---|---|---|
| random/seed-1 | pass | pass | pass |
| random/seed-10 | pass | pass | pass |
| random/seed-11 | pass | pass | pass |
| random/seed-12 | pass | pass | pass |
| random/seed-13 | pass | pass | pass |
| random/seed-14 | pass | pass | pass |
| random/seed-15 | pass | pass | pass |
| random/seed-16 | pass | pass | pass |
| random/seed-17 | pass | pass | pass |
| random/seed-18 | pass | pass | pass |
| random/seed-19 | pass | pass | pass |
| random/seed-2 | pass | pass | pass |
| random/seed-20 | pass | pass | pass |
| random/seed-21 | pass | pass | pass |
| random/seed-22 | pass | pass | pass |
| random/seed-23 | pass | pass | pass |
| random/seed-24 | pass | pass | pass |
| random/seed-25 | pass | pass | pass |
| random/seed-26 | pass | pass | pass |
| random/seed-27 | pass | pass | pass |
| random/seed-28 | pass | pass | pass |
| random/seed-29 | pass | pass | pass |
| random/seed-3 | pass | pass | pass |
| random/seed-30 | pass | pass | pass |
| random/seed-31 | pass | pass | pass |
| random/seed-32 | pass | pass | pass |
| random/seed-33 | pass | pass | pass |
| random/seed-34 | pass | pass | pass |
| random/seed-35 | pass | pass | pass |
| random/seed-36 | pass | pass | pass |
| random/seed-37 | pass | pass | pass |
| random/seed-38 | pass | pass | pass |
| random/seed-39 | pass | pass | pass |
| random/seed-4 | pass | pass | pass |
| random/seed-40 | pass | pass | pass |
| random/seed-41 | pass | pass | pass |
| random/seed-42 | pass | pass | pass |
| random/seed-43 | pass | pass | pass |
| random/seed-44 | pass | pass | pass |
| random/seed-45 | pass | pass | pass |
| random/seed-46 | pass | pass | pass |
| random/seed-47 | pass | pass | pass |
| random/seed-48 | pass | pass | pass |
| random/seed-49 | pass | pass | pass |
| random/seed-5 | pass | pass | pass |
| random/seed-50 | pass | pass | pass |
| random/seed-6 | pass | pass | pass |
| random/seed-7 | pass | pass | pass |
| random/seed-8 | pass | pass | pass |
| random/seed-9 | pass | pass | pass |

**150 passed, 0 failed** of 150 runs.

## Cross-target divergences

### random/seed-1
- `py-http-json` (python-sdk): `[ok] "1"=result:g2 -1=cancelled:error:-32800 1=cancelled:error:-32800 7=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "1"=result:g2 -1=cancelled:error:-32800 1=cancelled:error:-32800 7=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "1"=result:g2 -1=cancelled:no-response 1=cancelled:no-response 7=cancelled:no-response`

### random/seed-10
- `py-http-json` (python-sdk): `[ok] "-1"=result:g1 "0"=cancelled:error:-32800 "s42"=cancelled:result:g2 -1=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "-1"=result:g1 "0"=cancelled:error:-32800 "s42"=cancelled:result:g2 -1=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "-1"=result:g1 "0"=cancelled:no-response "s42"=cancelled:result:g2 -1=cancelled:no-response`

### random/seed-13
- `py-http-json` (python-sdk): `[ok] "7"=result:g3 "s7"=result:g2 2147483648=result:g0 7=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "7"=result:g3 "s7"=result:g2 2147483648=result:g0 7=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "7"=result:g3 "s7"=result:g2 2147483648=result:g0 7=cancelled:no-response`

### random/seed-14
- `py-http-json` (python-sdk): `[ok] "0"=result:g3 "s-1"=result:g1 "s9007199254740991"=cancelled:error:-32800 0=cancelled:result:g0`
- `py-http-sse` (python-sdk): `[ok] "0"=result:g3 "s-1"=result:g1 "s9007199254740991"=cancelled:error:-32800 0=cancelled:result:g0`
- `py-stdio` (python-sdk): `[ok] "0"=result:g3 "s-1"=result:g1 "s9007199254740991"=cancelled:no-response 0=cancelled:result:g0`

### random/seed-16
- `py-http-json` (python-sdk): `[ok] "1"=result:g0 "42"=cancelled:error:-32800 "7"=result:g2 7=result:g3`
- `py-http-sse` (python-sdk): `[ok] "1"=result:g0 "42"=cancelled:error:-32800 "7"=result:g2 7=result:g3`
- `py-stdio` (python-sdk): `[ok] "1"=result:g0 "42"=cancelled:no-response "7"=result:g2 7=result:g3`

### random/seed-18
- `py-http-json` (python-sdk): `[ok] "1"=cancelled:error:-32800 "42"=cancelled:error:-32800 "s0"=result:g0 1=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "1"=cancelled:error:-32800 "42"=cancelled:error:-32800 "s0"=result:g0 1=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "1"=cancelled:no-response "42"=cancelled:no-response "s0"=result:g0 1=cancelled:no-response`

### random/seed-19
- `py-http-json` (python-sdk): `[ok] "1"=cancelled:error:-32800 "2147483648"=result:g1 "s0"=result:g3 2147483648=result:g0`
- `py-http-sse` (python-sdk): `[ok] "1"=cancelled:error:-32800 "2147483648"=result:g1 "s0"=result:g3 2147483648=result:g0`
- `py-stdio` (python-sdk): `[ok] "1"=cancelled:no-response "2147483648"=result:g1 "s0"=result:g3 2147483648=result:g0`

### random/seed-20
- `py-http-json` (python-sdk): `[ok] "2147483648"=cancelled:error:-32800 "9007199254740991"=result:g1 "s7"=cancelled:result:g0 2147483648=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "2147483648"=cancelled:error:-32800 "9007199254740991"=result:g1 "s7"=cancelled:result:g0 2147483648=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "2147483648"=cancelled:no-response "9007199254740991"=result:g1 "s7"=cancelled:result:g0 2147483648=cancelled:no-response`

### random/seed-21
- `py-http-json` (python-sdk): `[ok] "1"=result:g3 "7"=result:g2 "s42"=cancelled:error:-32800 1=result:g1`
- `py-http-sse` (python-sdk): `[ok] "1"=result:g3 "7"=result:g2 "s42"=cancelled:error:-32800 1=result:g1`
- `py-stdio` (python-sdk): `[ok] "1"=result:g3 "7"=result:g2 "s42"=cancelled:no-response 1=result:g1`

### random/seed-23
- `py-http-json` (python-sdk): `[ok] "9007199254740991"=cancelled:error:-32800 "s0"=cancelled:error:-32800 7=result:g3 9007199254740991=result:g0`
- `py-http-sse` (python-sdk): `[ok] "9007199254740991"=cancelled:error:-32800 "s0"=cancelled:error:-32800 7=result:g3 9007199254740991=result:g0`
- `py-stdio` (python-sdk): `[ok] "9007199254740991"=cancelled:no-response "s0"=cancelled:no-response 7=result:g3 9007199254740991=result:g0`

### random/seed-27
- `py-http-json` (python-sdk): `[ok] "2147483648"=result:g3 "7"=result:g0 "s42"=cancelled:error:-32800 2147483648=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "2147483648"=result:g3 "7"=result:g0 "s42"=cancelled:error:-32800 2147483648=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "2147483648"=result:g3 "7"=result:g0 "s42"=cancelled:no-response 2147483648=cancelled:no-response`

### random/seed-28
- `py-http-json` (python-sdk): `[ok] "0"=cancelled:error:-32800 "s-1"=cancelled:error:-32800 0=cancelled:result:g2 2147483648=result:g1`
- `py-http-sse` (python-sdk): `[ok] "0"=cancelled:error:-32800 "s-1"=cancelled:error:-32800 0=cancelled:result:g2 2147483648=result:g1`
- `py-stdio` (python-sdk): `[ok] "0"=cancelled:no-response "s-1"=cancelled:no-response 0=cancelled:result:g2 2147483648=result:g1`

### random/seed-29
- `py-http-json` (python-sdk): `[ok] "-1"=result:g1 "0"=cancelled:error:-32800 "s-1"=cancelled:error:-32800 -1=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "-1"=result:g1 "0"=cancelled:error:-32800 "s-1"=cancelled:error:-32800 -1=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "-1"=result:g1 "0"=cancelled:no-response "s-1"=cancelled:no-response -1=cancelled:no-response`

### random/seed-30
- `py-http-json` (python-sdk): `[ok] "-1"=cancelled:error:-32800 "9007199254740991"=cancelled:error:-32800 "s-1"=cancelled:error:-32800 -1=result:g1`
- `py-http-sse` (python-sdk): `[ok] "-1"=cancelled:error:-32800 "9007199254740991"=cancelled:error:-32800 "s-1"=cancelled:error:-32800 -1=result:g1`
- `py-stdio` (python-sdk): `[ok] "-1"=cancelled:no-response "9007199254740991"=cancelled:no-response "s-1"=cancelled:no-response -1=result:g1`

### random/seed-33
- `py-http-json` (python-sdk): `[ok] "-1"=result:g0 "1"=cancelled:error:-32800 "s1"=result:g2 -1=cancelled:result:g1`
- `py-http-sse` (python-sdk): `[ok] "-1"=result:g0 "1"=cancelled:error:-32800 "s1"=result:g2 -1=cancelled:result:g1`
- `py-stdio` (python-sdk): `[ok] "-1"=result:g0 "1"=cancelled:no-response "s1"=result:g2 -1=cancelled:result:g1`

### random/seed-35
- `py-http-json` (python-sdk): `[ok] "-1"=result:g3 "2147483648"=cancelled:error:-32800 -1=cancelled:result:g0 7=result:g1`
- `py-http-sse` (python-sdk): `[ok] "-1"=result:g3 "2147483648"=cancelled:error:-32800 -1=cancelled:result:g0 7=result:g1`
- `py-stdio` (python-sdk): `[ok] "-1"=result:g3 "2147483648"=cancelled:no-response -1=cancelled:result:g0 7=result:g1`

### random/seed-36
- `py-http-json` (python-sdk): `[ok] "7"=result:g0 "9007199254740991"=cancelled:error:-32800 0=result:g1 7=result:g3`
- `py-http-sse` (python-sdk): `[ok] "7"=result:g0 "9007199254740991"=cancelled:error:-32800 0=result:g1 7=result:g3`
- `py-stdio` (python-sdk): `[ok] "7"=result:g0 "9007199254740991"=cancelled:no-response 0=result:g1 7=result:g3`

### random/seed-37
- `py-http-json` (python-sdk): `[ok] "2147483648"=cancelled:result:g1 "s-1"=cancelled:result:g0 -1=cancelled:error:-32800 2147483648=result:g3`
- `py-http-sse` (python-sdk): `[ok] "2147483648"=cancelled:result:g1 "s-1"=cancelled:result:g0 -1=cancelled:error:-32800 2147483648=result:g3`
- `py-stdio` (python-sdk): `[ok] "2147483648"=cancelled:result:g1 "s-1"=cancelled:result:g0 -1=cancelled:no-response 2147483648=result:g3`

### random/seed-39
- `py-http-json` (python-sdk): `[ok] "1"=cancelled:error:-32800 "7"=result:g0 0=cancelled:error:-32800 1=result:g1`
- `py-http-sse` (python-sdk): `[ok] "1"=cancelled:error:-32800 "7"=result:g0 0=cancelled:error:-32800 1=result:g1`
- `py-stdio` (python-sdk): `[ok] "1"=cancelled:no-response "7"=result:g0 0=cancelled:no-response 1=result:g1`

### random/seed-40
- `py-http-json` (python-sdk): `[ok] "42"=result:g0 "s-1"=result:g3 0=cancelled:error:-32800 42=result:g1`
- `py-http-sse` (python-sdk): `[ok] "42"=result:g0 "s-1"=result:g3 0=cancelled:error:-32800 42=result:g1`
- `py-stdio` (python-sdk): `[ok] "42"=result:g0 "s-1"=result:g3 0=cancelled:no-response 42=result:g1`

### random/seed-41
- `py-http-json` (python-sdk): `[ok] "1"=cancelled:error:-32800 "42"=result:g1 42=cancelled:error:-32800 7=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "1"=cancelled:error:-32800 "42"=result:g1 42=cancelled:error:-32800 7=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "1"=cancelled:no-response "42"=result:g1 42=cancelled:no-response 7=cancelled:no-response`

### random/seed-43
- `py-http-json` (python-sdk): `[ok] "0"=cancelled:error:-32800 "s7"=cancelled:result:g0 0=result:g1 9007199254740991=cancelled:result:g3`
- `py-http-sse` (python-sdk): `[ok] "0"=cancelled:error:-32800 "s7"=cancelled:result:g0 0=result:g1 9007199254740991=cancelled:result:g3`
- `py-stdio` (python-sdk): `[ok] "0"=cancelled:no-response "s7"=cancelled:result:g0 0=result:g1 9007199254740991=cancelled:result:g3`

### random/seed-44
- `py-http-json` (python-sdk): `[ok] "42"=cancelled:result:g3 "s-1"=cancelled:error:-32800 2147483648=result:g2 42=result:g1`
- `py-http-sse` (python-sdk): `[ok] "42"=cancelled:result:g3 "s-1"=cancelled:error:-32800 2147483648=result:g2 42=result:g1`
- `py-stdio` (python-sdk): `[ok] "42"=cancelled:result:g3 "s-1"=cancelled:no-response 2147483648=result:g2 42=result:g1`

### random/seed-45
- `py-http-json` (python-sdk): `[ok] "42"=cancelled:result:g1 "7"=cancelled:error:-32800 0=result:g3 7=result:g2`
- `py-http-sse` (python-sdk): `[ok] "42"=cancelled:result:g1 "7"=cancelled:error:-32800 0=result:g3 7=result:g2`
- `py-stdio` (python-sdk): `[ok] "42"=cancelled:result:g1 "7"=cancelled:no-response 0=result:g3 7=result:g2`

### random/seed-47
- `py-http-json` (python-sdk): `[ok] "-1"=cancelled:result:g1 "0"=cancelled:result:g3 "7"=result:g2 7=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "-1"=cancelled:result:g1 "0"=cancelled:result:g3 "7"=result:g2 7=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "-1"=cancelled:result:g1 "0"=cancelled:result:g3 "7"=result:g2 7=cancelled:no-response`

### random/seed-48
- `py-http-json` (python-sdk): `[ok] "-1"=cancelled:result:g0 "s-1"=cancelled:error:-32800 -1=cancelled:error:-32800 7=result:g3`
- `py-http-sse` (python-sdk): `[ok] "-1"=cancelled:result:g0 "s-1"=cancelled:error:-32800 -1=cancelled:error:-32800 7=result:g3`
- `py-stdio` (python-sdk): `[ok] "-1"=cancelled:result:g0 "s-1"=cancelled:no-response -1=cancelled:no-response 7=result:g3`

### random/seed-49
- `py-http-json` (python-sdk): `[ok] "0"=result:g0 "7"=result:g2 "s9007199254740991"=cancelled:error:-32800 0=cancelled:result:g3`
- `py-http-sse` (python-sdk): `[ok] "0"=result:g0 "7"=result:g2 "s9007199254740991"=cancelled:error:-32800 0=cancelled:result:g3`
- `py-stdio` (python-sdk): `[ok] "0"=result:g0 "7"=result:g2 "s9007199254740991"=cancelled:no-response 0=cancelled:result:g3`

### random/seed-50
- `py-http-json` (python-sdk): `[ok] "42"=result:g3 "9007199254740991"=cancelled:error:-32800 "s7"=result:g1 42=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "42"=result:g3 "9007199254740991"=cancelled:error:-32800 "s7"=result:g1 42=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "42"=result:g3 "9007199254740991"=cancelled:no-response "s7"=result:g1 42=cancelled:no-response`

### random/seed-6
- `py-http-json` (python-sdk): `[ok] "42"=cancelled:error:-32800 "9007199254740991"=cancelled:result:g0 -1=cancelled:error:-32800 9007199254740991=result:g3`
- `py-http-sse` (python-sdk): `[ok] "42"=cancelled:error:-32800 "9007199254740991"=cancelled:result:g0 -1=cancelled:error:-32800 9007199254740991=result:g3`
- `py-stdio` (python-sdk): `[ok] "42"=cancelled:no-response "9007199254740991"=cancelled:result:g0 -1=cancelled:no-response 9007199254740991=result:g3`

### random/seed-7
- `py-http-json` (python-sdk): `[ok] "1"=cancelled:result:g2 "7"=cancelled:error:-32800 2147483648=result:g1 7=result:g3`
- `py-http-sse` (python-sdk): `[ok] "1"=cancelled:result:g2 "7"=cancelled:error:-32800 2147483648=result:g1 7=result:g3`
- `py-stdio` (python-sdk): `[ok] "1"=cancelled:result:g2 "7"=cancelled:no-response 2147483648=result:g1 7=result:g3`

### random/seed-8
- `py-http-json` (python-sdk): `[ok] "1"=result:g0 "7"=result:g1 1=cancelled:error:-32800 2147483648=result:g2`
- `py-http-sse` (python-sdk): `[ok] "1"=result:g0 "7"=result:g1 1=cancelled:error:-32800 2147483648=result:g2`
- `py-stdio` (python-sdk): `[ok] "1"=result:g0 "7"=result:g1 1=cancelled:no-response 2147483648=result:g2`

### random/seed-9
- `py-http-json` (python-sdk): `[ok] "-1"=cancelled:error:-32800 "42"=cancelled:result:g3 42=result:g1 7=result:g0`
- `py-http-sse` (python-sdk): `[ok] "-1"=cancelled:error:-32800 "42"=cancelled:result:g3 42=result:g1 7=result:g0`
- `py-stdio` (python-sdk): `[ok] "-1"=cancelled:no-response "42"=cancelled:result:g3 42=result:g1 7=result:g0`

## Rules

- **WIRE**: inbound message is valid JSON-RPC 2.0
- **R1**: response id matches an issued request id exactly (type and value)
- **R2**: at most one response per request
- **R3**: every non-cancelled request receives a response
- **R4**: response payload belongs to its own request
- **R5**: HTTP response delivered on its request's stream
- **R6**: cancelling one id never suppresses another id's response
- **R7**: session recovers and serves a fresh request
