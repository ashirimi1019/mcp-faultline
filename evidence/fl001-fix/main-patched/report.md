# MCP Faultline report: FL-001 Typed JSON-RPC request-id isolation

## Provenance

- **harness**: `mcp-faultline 0.1.0`
- **harness_commit**: `7a5db5a5457e7dd9dc7b1482b862da3e8cfa16d2`
- **python**: `3.12.14`
- **platform**: `Windows-11-10.0.26300-SP0`
- **started_utc**: `2026-11-02T20:34:17+00:00`
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
| collide-0/cancel-first | pass | pass | pass |
| collide-0/cancel-second | pass | pass | pass |
| collide-0/out-of-order | pass | pass | pass |
| collide-7-strfirst/cancel-first | pass | pass | pass |
| collide-7-strfirst/cancel-second | pass | pass | pass |
| collide-7-strfirst/out-of-order | pass | pass | pass |
| collide-7/cancel-first | pass | pass | pass |
| collide-7/cancel-second | pass | pass | pass |
| collide-7/out-of-order | pass | pass | pass |
| collide-neg/cancel-first | pass | pass | pass |
| collide-neg/cancel-second | pass | pass | pass |
| collide-neg/out-of-order | pass | pass | pass |
| control-int/cancel-first | pass | pass | pass |
| control-int/cancel-second | pass | pass | pass |
| control-int/out-of-order | pass | pass | pass |
| control-mixed/cancel-first | pass | pass | pass |
| control-mixed/cancel-second | pass | pass | pass |
| control-mixed/out-of-order | pass | pass | pass |
| control-str/cancel-first | pass | pass | pass |
| control-str/cancel-second | pass | pass | pass |
| control-str/out-of-order | pass | pass | pass |
| noncanonical-07/cancel-first | pass | pass | pass |
| noncanonical-07/cancel-second | pass | pass | pass |
| noncanonical-07/out-of-order | pass | pass | pass |

**72 passed, 0 failed** of 72 runs.

## Cross-target divergences

### collide-0/cancel-first
- `py-http-json` (python-sdk): `[ok] "0"=result:t-str-0 0=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "0"=result:t-str-0 0=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "0"=result:t-str-0 0=cancelled:no-response`

### collide-0/cancel-second
- `py-http-json` (python-sdk): `[ok] "0"=cancelled:error:-32800 0=result:t-int-0`
- `py-http-sse` (python-sdk): `[ok] "0"=cancelled:error:-32800 0=result:t-int-0`
- `py-stdio` (python-sdk): `[ok] "0"=cancelled:no-response 0=result:t-int-0`

### collide-7-strfirst/cancel-first
- `py-http-json` (python-sdk): `[ok] "7"=cancelled:error:-32800 7=result:t-int-7`
- `py-http-sse` (python-sdk): `[ok] "7"=cancelled:error:-32800 7=result:t-int-7`
- `py-stdio` (python-sdk): `[ok] "7"=cancelled:no-response 7=result:t-int-7`

### collide-7-strfirst/cancel-second
- `py-http-json` (python-sdk): `[ok] "7"=result:t-str-7 7=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "7"=result:t-str-7 7=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "7"=result:t-str-7 7=cancelled:no-response`

### collide-7/cancel-first
- `py-http-json` (python-sdk): `[ok] "7"=result:t-str-7 7=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "7"=result:t-str-7 7=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "7"=result:t-str-7 7=cancelled:no-response`

### collide-7/cancel-second
- `py-http-json` (python-sdk): `[ok] "7"=cancelled:error:-32800 7=result:t-int-7`
- `py-http-sse` (python-sdk): `[ok] "7"=cancelled:error:-32800 7=result:t-int-7`
- `py-stdio` (python-sdk): `[ok] "7"=cancelled:no-response 7=result:t-int-7`

### collide-neg/cancel-first
- `py-http-json` (python-sdk): `[ok] "-1"=result:t-str--1 -1=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "-1"=result:t-str--1 -1=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "-1"=result:t-str--1 -1=cancelled:no-response`

### collide-neg/cancel-second
- `py-http-json` (python-sdk): `[ok] "-1"=cancelled:error:-32800 -1=result:t-int--1`
- `py-http-sse` (python-sdk): `[ok] "-1"=cancelled:error:-32800 -1=result:t-int--1`
- `py-stdio` (python-sdk): `[ok] "-1"=cancelled:no-response -1=result:t-int--1`

### control-int/cancel-first
- `py-http-json` (python-sdk): `[ok] 7=cancelled:error:-32800 8=result:t-int-8`
- `py-http-sse` (python-sdk): `[ok] 7=cancelled:error:-32800 8=result:t-int-8`
- `py-stdio` (python-sdk): `[ok] 7=cancelled:no-response 8=result:t-int-8`

### control-int/cancel-second
- `py-http-json` (python-sdk): `[ok] 7=result:t-int-7 8=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] 7=result:t-int-7 8=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] 7=result:t-int-7 8=cancelled:no-response`

### control-mixed/cancel-first
- `py-http-json` (python-sdk): `[ok] "x7"=result:t-str-x7 7=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "x7"=result:t-str-x7 7=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "x7"=result:t-str-x7 7=cancelled:no-response`

### control-mixed/cancel-second
- `py-http-json` (python-sdk): `[ok] "x7"=cancelled:error:-32800 7=result:t-int-7`
- `py-http-sse` (python-sdk): `[ok] "x7"=cancelled:error:-32800 7=result:t-int-7`
- `py-stdio` (python-sdk): `[ok] "x7"=cancelled:no-response 7=result:t-int-7`

### control-str/cancel-first
- `py-http-json` (python-sdk): `[ok] "a7"=cancelled:error:-32800 "b7"=result:t-str-b7`
- `py-http-sse` (python-sdk): `[ok] "a7"=cancelled:error:-32800 "b7"=result:t-str-b7`
- `py-stdio` (python-sdk): `[ok] "a7"=cancelled:no-response "b7"=result:t-str-b7`

### control-str/cancel-second
- `py-http-json` (python-sdk): `[ok] "a7"=result:t-str-a7 "b7"=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "a7"=result:t-str-a7 "b7"=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "a7"=result:t-str-a7 "b7"=cancelled:no-response`

### noncanonical-07/cancel-first
- `py-http-json` (python-sdk): `[ok] "07"=result:t-str-07 7=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "07"=result:t-str-07 7=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "07"=result:t-str-07 7=cancelled:no-response`

### noncanonical-07/cancel-second
- `py-http-json` (python-sdk): `[ok] "07"=cancelled:error:-32800 7=result:t-int-7`
- `py-http-sse` (python-sdk): `[ok] "07"=cancelled:error:-32800 7=result:t-int-7`
- `py-stdio` (python-sdk): `[ok] "07"=cancelled:no-response 7=result:t-int-7`

## Rules

- **WIRE**: inbound message is valid JSON-RPC 2.0
- **R1**: response id matches an issued request id exactly (type and value)
- **R2**: at most one response per request
- **R3**: every non-cancelled request receives a response
- **R4**: response payload belongs to its own request
- **R5**: HTTP response delivered on its request's stream
- **R6**: cancelling one id never suppresses another id's response
- **R7**: session recovers and serves a fresh request
