# MCP Faultline report: FL-001 Typed JSON-RPC request-id isolation

## Provenance

- **harness**: `mcp-faultline 0.1.0`
- **harness_commit**: `7a5db5a5457e7dd9dc7b1482b862da3e8cfa16d2`
- **python**: `3.12.14`
- **platform**: `Windows-11-10.0.26300-SP0`
- **started_utc**: `2026-11-02T20:36:07+00:00`
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
| random/seed-10 | pass | FAIL R5 | FAIL R5 |
| random/seed-11 | pass | FAIL R3,R5 | FAIL R3,R5 |
| random/seed-12 | pass | FAIL R3,R5 | FAIL R3,R5 |
| random/seed-13 | FAIL R3,R6 | FAIL R4,R6 | FAIL R4,R6 |
| random/seed-14 | FAIL R3,R6 | FAIL R3,R5,R6 | FAIL R3,R5,R6 |
| random/seed-15 | pass | FAIL R3 | FAIL R3 |
| random/seed-16 | pass | FAIL R3 | FAIL R3 |
| random/seed-17 | pass | FAIL R3 | FAIL R3 |
| random/seed-18 | pass | pass | pass |
| random/seed-19 | pass | FAIL R3 | FAIL R3 |
| random/seed-2 | pass | FAIL R3 | FAIL R3 |
| random/seed-20 | pass | pass | pass |
| random/seed-21 | pass | FAIL R3,R5 | FAIL R3,R5 |
| random/seed-22 | pass | FAIL R3 | FAIL R3 |
| random/seed-23 | pass | FAIL R3,R6 | FAIL R3,R6 |
| random/seed-24 | pass | FAIL R3 | FAIL R3 |
| random/seed-25 | pass | FAIL R3,R5 | FAIL R3,R5 |
| random/seed-26 | pass | FAIL R3 | FAIL R3 |
| random/seed-27 | FAIL R3,R6 | FAIL R4,R6 | FAIL R4,R6 |
| random/seed-28 | pass | FAIL R5 | FAIL R5 |
| random/seed-29 | pass | FAIL R3,R6 | FAIL R3,R6 |
| random/seed-3 | pass | FAIL R5 | FAIL R5 |
| random/seed-30 | pass | FAIL R3,R6 | FAIL R3,R6 |
| random/seed-31 | pass | FAIL R3 | FAIL R3 |
| random/seed-32 | pass | FAIL R3 | FAIL R3 |
| random/seed-33 | pass | FAIL R3,R6 | FAIL R3,R6 |
| random/seed-34 | pass | FAIL R3,R5 | FAIL R3,R5 |
| random/seed-35 | pass | FAIL R3,R5,R6 | FAIL R3,R5,R6 |
| random/seed-36 | pass | FAIL R3,R5 | FAIL R3,R5 |
| random/seed-37 | FAIL R3,R6 | FAIL R3,R5,R6 | FAIL R3,R5,R6 |
| random/seed-38 | pass | FAIL R5 | FAIL R5 |
| random/seed-39 | pass | FAIL R3,R6 | FAIL R3,R6 |
| random/seed-4 | pass | FAIL R3 | FAIL R3 |
| random/seed-40 | pass | FAIL R3 | FAIL R3 |
| random/seed-41 | FAIL R3,R6 | FAIL R4,R6 | FAIL R4,R6 |
| random/seed-42 | pass | FAIL R3,R5 | FAIL R3,R5 |
| random/seed-43 | pass | FAIL R5 | FAIL R5 |
| random/seed-44 | pass | FAIL R5 | FAIL R5 |
| random/seed-45 | pass | pass | pass |
| random/seed-46 | pass | FAIL R3,R5 | FAIL R3,R5 |
| random/seed-47 | FAIL R3,R6 | FAIL R4,R6 | FAIL R4,R6 |
| random/seed-48 | pass | FAIL R5 | FAIL R5 |
| random/seed-49 | pass | FAIL R3,R6 | FAIL R3,R6 |
| random/seed-5 | pass | FAIL R3,R5 | FAIL R3,R5 |
| random/seed-50 | FAIL R3,R6 | FAIL R4,R6 | FAIL R4,R6 |
| random/seed-6 | FAIL R3,R6 | FAIL R3,R5,R6 | FAIL R3,R5,R6 |
| random/seed-7 | pass | pass | pass |
| random/seed-8 | pass | FAIL R3,R6 | FAIL R3,R6 |
| random/seed-9 | pass | FAIL R3,R6 | FAIL R3,R6 |

**52 passed, 98 failed** of 150 runs.

## Violations

### `py-stdio` - random/seed-6
- **R3** (every non-cancelled request receives a response): request 9007199254740991 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "9007199254740991" suppressed the response to 9007199254740991
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_stdio__random_seed_6.json`

### `py-stdio` - random/seed-13
- **R3** (every non-cancelled request receives a response): request "7" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling 7 suppressed the response to "7"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_stdio__random_seed_13.json`

### `py-stdio` - random/seed-14
- **R3** (every non-cancelled request receives a response): request "0" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling 0 suppressed the response to "0"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_stdio__random_seed_14.json`

### `py-stdio` - random/seed-27
- **R3** (every non-cancelled request receives a response): request "2147483648" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling 2147483648 suppressed the response to "2147483648"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_stdio__random_seed_27.json`

### `py-stdio` - random/seed-37
- **R3** (every non-cancelled request receives a response): request 2147483648 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "2147483648" suppressed the response to 2147483648
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_stdio__random_seed_37.json`

### `py-stdio` - random/seed-41
- **R3** (every non-cancelled request receives a response): request "42" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling 42 suppressed the response to "42"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_stdio__random_seed_41.json`

### `py-stdio` - random/seed-47
- **R3** (every non-cancelled request receives a response): request "7" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling 7 suppressed the response to "7"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_stdio__random_seed_47.json`

### `py-stdio` - random/seed-50
- **R3** (every non-cancelled request receives a response): request "42" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling 42 suppressed the response to "42"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_stdio__random_seed_50.json`

### `py-http-sse` - random/seed-2
- **R3** (every non-cancelled request receives a response): request 9007199254740991 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_2.json`

### `py-http-sse` - random/seed-3
- **R5** (HTTP response delivered on its request's stream): response for "1" arrived on post#6(1), request was sent on post#3("1")
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_3.json`

### `py-http-sse` - random/seed-4
- **R3** (every non-cancelled request receives a response): request "1" never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_4.json`

### `py-http-sse` - random/seed-5
- **R5** (HTTP response delivered on its request's stream): response for "-1" arrived on post#6(-1), request was sent on post#5("-1")
- **R3** (every non-cancelled request receives a response): request -1 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_5.json`

### `py-http-sse` - random/seed-6
- **R5** (HTTP response delivered on its request's stream): response for "9007199254740991" arrived on post#6(9007199254740991), request was sent on post#3("9007199254740991")
- **R3** (every non-cancelled request receives a response): request 9007199254740991 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "9007199254740991" suppressed the response to 9007199254740991
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_6.json`

### `py-http-sse` - random/seed-8
- **R3** (every non-cancelled request receives a response): request "1" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling 1 suppressed the response to "1"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_8.json`

### `py-http-sse` - random/seed-9
- **R3** (every non-cancelled request receives a response): request 42 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "42" suppressed the response to 42
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_9.json`

### `py-http-sse` - random/seed-10
- **R5** (HTTP response delivered on its request's stream): response for "-1" arrived on post#6(-1), request was sent on post#4("-1")
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_10.json`

### `py-http-sse` - random/seed-11
- **R5** (HTTP response delivered on its request's stream): response for "42" arrived on post#4(42), request was sent on post#3("42")
- **R3** (every non-cancelled request receives a response): request 42 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_11.json`

### `py-http-sse` - random/seed-12
- **R5** (HTTP response delivered on its request's stream): response for "42" arrived on post#5(42), request was sent on post#4("42")
- **R3** (every non-cancelled request receives a response): request 42 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_12.json`

### `py-http-sse` - random/seed-13
- **R4** (response payload belongs to its own request): request "7" was never cancelled but got error -32800
- **R6** (cancelling one id never suppresses another id's response): cancelling 7 produced an error response for "7"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_13.json`

### `py-http-sse` - random/seed-14
- **R5** (HTTP response delivered on its request's stream): response for 0 arrived on post#6("0"), request was sent on post#3(0)
- **R3** (every non-cancelled request receives a response): request "0" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling 0 suppressed the response to "0"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_14.json`

### `py-http-sse` - random/seed-15
- **R3** (every non-cancelled request receives a response): request 1 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_15.json`

### `py-http-sse` - random/seed-16
- **R3** (every non-cancelled request receives a response): request "7" never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_16.json`

### `py-http-sse` - random/seed-17
- **R3** (every non-cancelled request receives a response): request -1 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_17.json`

### `py-http-sse` - random/seed-19
- **R3** (every non-cancelled request receives a response): request 2147483648 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_19.json`

### `py-http-sse` - random/seed-21
- **R5** (HTTP response delivered on its request's stream): response for 1 arrived on post#6("1"), request was sent on post#4(1)
- **R3** (every non-cancelled request receives a response): request "1" never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_21.json`

### `py-http-sse` - random/seed-22
- **R3** (every non-cancelled request receives a response): request "1" never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_22.json`

### `py-http-sse` - random/seed-23
- **R3** (every non-cancelled request receives a response): request 9007199254740991 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "9007199254740991" suppressed the response to 9007199254740991
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_23.json`

### `py-http-sse` - random/seed-24
- **R3** (every non-cancelled request receives a response): request 2147483648 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_24.json`

### `py-http-sse` - random/seed-25
- **R5** (HTTP response delivered on its request's stream): response for "42" arrived on post#5(42), request was sent on post#4("42")
- **R3** (every non-cancelled request receives a response): request 42 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_25.json`

### `py-http-sse` - random/seed-26
- **R3** (every non-cancelled request receives a response): request "2147483648" never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_26.json`

### `py-http-sse` - random/seed-27
- **R4** (response payload belongs to its own request): request "2147483648" was never cancelled but got error -32800
- **R6** (cancelling one id never suppresses another id's response): cancelling 2147483648 produced an error response for "2147483648"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_27.json`

### `py-http-sse` - random/seed-28
- **R5** (HTTP response delivered on its request's stream): response for 0 arrived on post#6("0"), request was sent on post#5(0)
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_28.json`

### `py-http-sse` - random/seed-29
- **R3** (every non-cancelled request receives a response): request "-1" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling -1 suppressed the response to "-1"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_29.json`

### `py-http-sse` - random/seed-30
- **R3** (every non-cancelled request receives a response): request -1 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "-1" suppressed the response to -1
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_30.json`

### `py-http-sse` - random/seed-31
- **R3** (every non-cancelled request receives a response): request 0 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_31.json`

### `py-http-sse` - random/seed-32
- **R3** (every non-cancelled request receives a response): request 0 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_32.json`

### `py-http-sse` - random/seed-33
- **R3** (every non-cancelled request receives a response): request "-1" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling -1 suppressed the response to "-1"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_33.json`

### `py-http-sse` - random/seed-34
- **R5** (HTTP response delivered on its request's stream): response for "-1" arrived on post#6(-1), request was sent on post#5("-1")
- **R3** (every non-cancelled request receives a response): request -1 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_34.json`

### `py-http-sse` - random/seed-35
- **R5** (HTTP response delivered on its request's stream): response for -1 arrived on post#6("-1"), request was sent on post#3(-1)
- **R3** (every non-cancelled request receives a response): request "-1" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling -1 suppressed the response to "-1"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_35.json`

### `py-http-sse` - random/seed-36
- **R5** (HTTP response delivered on its request's stream): response for "7" arrived on post#6(7), request was sent on post#3("7")
- **R3** (every non-cancelled request receives a response): request 7 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_36.json`

### `py-http-sse` - random/seed-37
- **R5** (HTTP response delivered on its request's stream): response for "2147483648" arrived on post#6(2147483648), request was sent on post#4("2147483648")
- **R3** (every non-cancelled request receives a response): request 2147483648 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "2147483648" suppressed the response to 2147483648
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_37.json`

### `py-http-sse` - random/seed-38
- **R5** (HTTP response delivered on its request's stream): response for "2147483648" arrived on post#6(2147483648), request was sent on post#4("2147483648")
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_38.json`

### `py-http-sse` - random/seed-39
- **R3** (every non-cancelled request receives a response): request 1 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "1" suppressed the response to 1
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_39.json`

### `py-http-sse` - random/seed-40
- **R3** (every non-cancelled request receives a response): request "42" never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_40.json`

### `py-http-sse` - random/seed-41
- **R4** (response payload belongs to its own request): request "42" was never cancelled but got error -32800
- **R6** (cancelling one id never suppresses another id's response): cancelling 42 produced an error response for "42"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_41.json`

### `py-http-sse` - random/seed-42
- **R5** (HTTP response delivered on its request's stream): response for 2147483648 arrived on post#6("2147483648"), request was sent on post#4(2147483648)
- **R3** (every non-cancelled request receives a response): request "2147483648" never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_42.json`

### `py-http-sse` - random/seed-43
- **R5** (HTTP response delivered on its request's stream): response for 0 arrived on post#5("0"), request was sent on post#4(0)
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_43.json`

### `py-http-sse` - random/seed-44
- **R5** (HTTP response delivered on its request's stream): response for 42 arrived on post#6("42"), request was sent on post#4(42)
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_44.json`

### `py-http-sse` - random/seed-46
- **R5** (HTTP response delivered on its request's stream): response for 0 arrived on post#6("0"), request was sent on post#4(0)
- **R3** (every non-cancelled request receives a response): request "0" never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_46.json`

### `py-http-sse` - random/seed-47
- **R4** (response payload belongs to its own request): request "7" was never cancelled but got error -32800
- **R6** (cancelling one id never suppresses another id's response): cancelling 7 produced an error response for "7"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_47.json`

### `py-http-sse` - random/seed-48
- **R5** (HTTP response delivered on its request's stream): response for "-1" arrived on post#4(-1), request was sent on post#3("-1")
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_48.json`

### `py-http-sse` - random/seed-49
- **R3** (every non-cancelled request receives a response): request "0" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling 0 suppressed the response to "0"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_49.json`

### `py-http-sse` - random/seed-50
- **R4** (response payload belongs to its own request): request "42" was never cancelled but got error -32800
- **R6** (cancelling one id never suppresses another id's response): cancelling 42 produced an error response for "42"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_sse__random_seed_50.json`

### `py-http-json` - random/seed-2
- **R3** (every non-cancelled request receives a response): request 9007199254740991 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_2.json`

### `py-http-json` - random/seed-3
- **R5** (HTTP response delivered on its request's stream): response for "1" arrived on post#6(1), request was sent on post#3("1")
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_3.json`

### `py-http-json` - random/seed-4
- **R3** (every non-cancelled request receives a response): request "1" never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_4.json`

### `py-http-json` - random/seed-5
- **R5** (HTTP response delivered on its request's stream): response for "-1" arrived on post#6(-1), request was sent on post#5("-1")
- **R3** (every non-cancelled request receives a response): request -1 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_5.json`

### `py-http-json` - random/seed-6
- **R5** (HTTP response delivered on its request's stream): response for "9007199254740991" arrived on post#6(9007199254740991), request was sent on post#3("9007199254740991")
- **R3** (every non-cancelled request receives a response): request 9007199254740991 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "9007199254740991" suppressed the response to 9007199254740991
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_6.json`

### `py-http-json` - random/seed-8
- **R3** (every non-cancelled request receives a response): request "1" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling 1 suppressed the response to "1"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_8.json`

### `py-http-json` - random/seed-9
- **R3** (every non-cancelled request receives a response): request 42 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "42" suppressed the response to 42
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_9.json`

### `py-http-json` - random/seed-10
- **R5** (HTTP response delivered on its request's stream): response for "-1" arrived on post#6(-1), request was sent on post#4("-1")
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_10.json`

### `py-http-json` - random/seed-11
- **R5** (HTTP response delivered on its request's stream): response for "42" arrived on post#4(42), request was sent on post#3("42")
- **R3** (every non-cancelled request receives a response): request 42 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_11.json`

### `py-http-json` - random/seed-12
- **R5** (HTTP response delivered on its request's stream): response for "42" arrived on post#5(42), request was sent on post#4("42")
- **R3** (every non-cancelled request receives a response): request 42 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_12.json`

### `py-http-json` - random/seed-13
- **R4** (response payload belongs to its own request): request "7" was never cancelled but got error -32800
- **R6** (cancelling one id never suppresses another id's response): cancelling 7 produced an error response for "7"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_13.json`

### `py-http-json` - random/seed-14
- **R5** (HTTP response delivered on its request's stream): response for 0 arrived on post#6("0"), request was sent on post#3(0)
- **R3** (every non-cancelled request receives a response): request "0" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling 0 suppressed the response to "0"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_14.json`

### `py-http-json` - random/seed-15
- **R3** (every non-cancelled request receives a response): request 1 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_15.json`

### `py-http-json` - random/seed-16
- **R3** (every non-cancelled request receives a response): request "7" never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_16.json`

### `py-http-json` - random/seed-17
- **R3** (every non-cancelled request receives a response): request -1 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_17.json`

### `py-http-json` - random/seed-19
- **R3** (every non-cancelled request receives a response): request 2147483648 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_19.json`

### `py-http-json` - random/seed-21
- **R5** (HTTP response delivered on its request's stream): response for 1 arrived on post#6("1"), request was sent on post#4(1)
- **R3** (every non-cancelled request receives a response): request "1" never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_21.json`

### `py-http-json` - random/seed-22
- **R3** (every non-cancelled request receives a response): request "1" never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_22.json`

### `py-http-json` - random/seed-23
- **R3** (every non-cancelled request receives a response): request 9007199254740991 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "9007199254740991" suppressed the response to 9007199254740991
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_23.json`

### `py-http-json` - random/seed-24
- **R3** (every non-cancelled request receives a response): request 2147483648 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_24.json`

### `py-http-json` - random/seed-25
- **R5** (HTTP response delivered on its request's stream): response for "42" arrived on post#5(42), request was sent on post#4("42")
- **R3** (every non-cancelled request receives a response): request 42 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_25.json`

### `py-http-json` - random/seed-26
- **R3** (every non-cancelled request receives a response): request "2147483648" never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_26.json`

### `py-http-json` - random/seed-27
- **R4** (response payload belongs to its own request): request "2147483648" was never cancelled but got error -32800
- **R6** (cancelling one id never suppresses another id's response): cancelling 2147483648 produced an error response for "2147483648"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_27.json`

### `py-http-json` - random/seed-28
- **R5** (HTTP response delivered on its request's stream): response for 0 arrived on post#6("0"), request was sent on post#5(0)
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_28.json`

### `py-http-json` - random/seed-29
- **R3** (every non-cancelled request receives a response): request "-1" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling -1 suppressed the response to "-1"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_29.json`

### `py-http-json` - random/seed-30
- **R3** (every non-cancelled request receives a response): request -1 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "-1" suppressed the response to -1
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_30.json`

### `py-http-json` - random/seed-31
- **R3** (every non-cancelled request receives a response): request 0 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_31.json`

### `py-http-json` - random/seed-32
- **R3** (every non-cancelled request receives a response): request 0 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_32.json`

### `py-http-json` - random/seed-33
- **R3** (every non-cancelled request receives a response): request "-1" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling -1 suppressed the response to "-1"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_33.json`

### `py-http-json` - random/seed-34
- **R5** (HTTP response delivered on its request's stream): response for "-1" arrived on post#6(-1), request was sent on post#5("-1")
- **R3** (every non-cancelled request receives a response): request -1 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_34.json`

### `py-http-json` - random/seed-35
- **R5** (HTTP response delivered on its request's stream): response for -1 arrived on post#6("-1"), request was sent on post#3(-1)
- **R3** (every non-cancelled request receives a response): request "-1" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling -1 suppressed the response to "-1"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_35.json`

### `py-http-json` - random/seed-36
- **R5** (HTTP response delivered on its request's stream): response for "7" arrived on post#6(7), request was sent on post#3("7")
- **R3** (every non-cancelled request receives a response): request 7 never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_36.json`

### `py-http-json` - random/seed-37
- **R5** (HTTP response delivered on its request's stream): response for "2147483648" arrived on post#6(2147483648), request was sent on post#4("2147483648")
- **R3** (every non-cancelled request receives a response): request 2147483648 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "2147483648" suppressed the response to 2147483648
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_37.json`

### `py-http-json` - random/seed-38
- **R5** (HTTP response delivered on its request's stream): response for "2147483648" arrived on post#6(2147483648), request was sent on post#4("2147483648")
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_38.json`

### `py-http-json` - random/seed-39
- **R3** (every non-cancelled request receives a response): request 1 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "1" suppressed the response to 1
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_39.json`

### `py-http-json` - random/seed-40
- **R3** (every non-cancelled request receives a response): request "42" never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_40.json`

### `py-http-json` - random/seed-41
- **R4** (response payload belongs to its own request): request "42" was never cancelled but got error -32800
- **R6** (cancelling one id never suppresses another id's response): cancelling 42 produced an error response for "42"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_41.json`

### `py-http-json` - random/seed-42
- **R5** (HTTP response delivered on its request's stream): response for 2147483648 arrived on post#6("2147483648"), request was sent on post#4(2147483648)
- **R3** (every non-cancelled request receives a response): request "2147483648" never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_42.json`

### `py-http-json` - random/seed-43
- **R5** (HTTP response delivered on its request's stream): response for 0 arrived on post#5("0"), request was sent on post#4(0)
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_43.json`

### `py-http-json` - random/seed-44
- **R5** (HTTP response delivered on its request's stream): response for 42 arrived on post#6("42"), request was sent on post#4(42)
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_44.json`

### `py-http-json` - random/seed-46
- **R5** (HTTP response delivered on its request's stream): response for 0 arrived on post#6("0"), request was sent on post#4(0)
- **R3** (every non-cancelled request receives a response): request "0" never received a response
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_46.json`

### `py-http-json` - random/seed-47
- **R4** (response payload belongs to its own request): request "7" was never cancelled but got error -32800
- **R6** (cancelling one id never suppresses another id's response): cancelling 7 produced an error response for "7"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_47.json`

### `py-http-json` - random/seed-48
- **R5** (HTTP response delivered on its request's stream): response for "-1" arrived on post#4(-1), request was sent on post#3("-1")
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_48.json`

### `py-http-json` - random/seed-49
- **R3** (every non-cancelled request receives a response): request "0" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling 0 suppressed the response to "0"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_49.json`

### `py-http-json` - random/seed-50
- **R4** (response payload belongs to its own request): request "42" was never cancelled but got error -32800
- **R6** (cancelling one id never suppresses another id's response): cancelling 42 produced an error response for "42"
- trace: `evidence/fl001-fix/random50-main-unpatched/traces/py_http_json__random_seed_50.json`

## Cross-target divergences

### random/seed-1
- `py-http-json` (python-sdk): `[ok] "1"=result:g2 -1=cancelled:error:-32800 1=cancelled:no-response 7=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "1"=result:g2 -1=cancelled:error:-32800 1=cancelled:no-response 7=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "1"=result:g2 -1=cancelled:no-response 1=cancelled:result:g0 7=cancelled:no-response`

### random/seed-10
- `py-http-json` (python-sdk): `[R5] "-1"=result:g1 "0"=cancelled:error:-32800 "s42"=cancelled:result:g2 -1=cancelled:no-response`
- `py-http-sse` (python-sdk): `[R5] "-1"=result:g1 "0"=cancelled:error:-32800 "s42"=cancelled:result:g2 -1=cancelled:no-response`
- `py-stdio` (python-sdk): `[ok] "-1"=result:g1 "0"=cancelled:no-response "s42"=cancelled:result:g2 -1=cancelled:no-response`

### random/seed-11
- `py-http-json` (python-sdk): `[R3,R5] "42"=result:g0 "9007199254740991"=cancelled:result:g3 "s9007199254740991"=result:g2 42=LOST`
- `py-http-sse` (python-sdk): `[R3,R5] "42"=result:g0 "9007199254740991"=cancelled:result:g3 "s9007199254740991"=result:g2 42=LOST`
- `py-stdio` (python-sdk): `[ok] "42"=result:g0 "9007199254740991"=cancelled:result:g3 "s9007199254740991"=result:g2 42=result:g1`

### random/seed-12
- `py-http-json` (python-sdk): `[R3,R5] "42"=result:g1 "s-1"=result:g0 "s7"=result:g3 42=LOST`
- `py-http-sse` (python-sdk): `[R3,R5] "42"=result:g1 "s-1"=result:g0 "s7"=result:g3 42=LOST`
- `py-stdio` (python-sdk): `[ok] "42"=result:g1 "s-1"=result:g0 "s7"=result:g3 42=result:g2`

### random/seed-13
- `py-http-json` (python-sdk): `[R4,R6] "7"=error:-32800 "s7"=result:g2 2147483648=result:g0 7=cancelled:no-response`
- `py-http-sse` (python-sdk): `[R4,R6] "7"=error:-32800 "s7"=result:g2 2147483648=result:g0 7=cancelled:no-response`
- `py-stdio` (python-sdk): `[R3,R6] "7"=LOST "s7"=result:g2 2147483648=result:g0 7=cancelled:result:g1`

### random/seed-14
- `py-http-json` (python-sdk): `[R3,R5,R6] "0"=LOST "s-1"=result:g1 "s9007199254740991"=cancelled:error:-32800 0=cancelled:result:g0`
- `py-http-sse` (python-sdk): `[R3,R5,R6] "0"=LOST "s-1"=result:g1 "s9007199254740991"=cancelled:error:-32800 0=cancelled:result:g0`
- `py-stdio` (python-sdk): `[R3,R6] "0"=LOST "s-1"=result:g1 "s9007199254740991"=cancelled:no-response 0=cancelled:result:g0`

### random/seed-15
- `py-http-json` (python-sdk): `[R3] "1"=result:g3 "s0"=result:g1 1=LOST 2147483648=result:g0`
- `py-http-sse` (python-sdk): `[R3] "1"=result:g3 "s0"=result:g1 1=LOST 2147483648=result:g0`
- `py-stdio` (python-sdk): `[ok] "1"=result:g3 "s0"=result:g1 1=result:g2 2147483648=result:g0`

### random/seed-16
- `py-http-json` (python-sdk): `[R3] "1"=result:g0 "42"=cancelled:error:-32800 "7"=LOST 7=result:g3`
- `py-http-sse` (python-sdk): `[R3] "1"=result:g0 "42"=cancelled:error:-32800 "7"=LOST 7=result:g3`
- `py-stdio` (python-sdk): `[ok] "1"=result:g0 "42"=cancelled:no-response "7"=result:g2 7=result:g3`

### random/seed-17
- `py-http-json` (python-sdk): `[R3] "-1"=result:g3 "42"=result:g2 "7"=result:g1 -1=LOST`
- `py-http-sse` (python-sdk): `[R3] "-1"=result:g3 "42"=result:g2 "7"=result:g1 -1=LOST`
- `py-stdio` (python-sdk): `[ok] "-1"=result:g3 "42"=result:g2 "7"=result:g1 -1=result:g0`

### random/seed-18
- `py-http-json` (python-sdk): `[ok] "1"=cancelled:error:-32800 "42"=cancelled:error:-32800 "s0"=result:g0 1=cancelled:no-response`
- `py-http-sse` (python-sdk): `[ok] "1"=cancelled:error:-32800 "42"=cancelled:error:-32800 "s0"=result:g0 1=cancelled:no-response`
- `py-stdio` (python-sdk): `[ok] "1"=cancelled:no-response "42"=cancelled:no-response "s0"=result:g0 1=cancelled:result:g2`

### random/seed-19
- `py-http-json` (python-sdk): `[R3] "1"=cancelled:error:-32800 "2147483648"=result:g1 "s0"=result:g3 2147483648=LOST`
- `py-http-sse` (python-sdk): `[R3] "1"=cancelled:error:-32800 "2147483648"=result:g1 "s0"=result:g3 2147483648=LOST`
- `py-stdio` (python-sdk): `[ok] "1"=cancelled:no-response "2147483648"=result:g1 "s0"=result:g3 2147483648=result:g0`

### random/seed-2
- `py-http-json` (python-sdk): `[R3] "9007199254740991"=result:g2 0=result:g3 7=result:g0 9007199254740991=LOST`
- `py-http-sse` (python-sdk): `[R3] "9007199254740991"=result:g2 0=result:g3 7=result:g0 9007199254740991=LOST`
- `py-stdio` (python-sdk): `[ok] "9007199254740991"=result:g2 0=result:g3 7=result:g0 9007199254740991=result:g1`

### random/seed-20
- `py-http-json` (python-sdk): `[ok] "2147483648"=cancelled:error:-32800 "9007199254740991"=result:g1 "s7"=cancelled:result:g0 2147483648=cancelled:no-response`
- `py-http-sse` (python-sdk): `[ok] "2147483648"=cancelled:error:-32800 "9007199254740991"=result:g1 "s7"=cancelled:result:g0 2147483648=cancelled:no-response`
- `py-stdio` (python-sdk): `[ok] "2147483648"=cancelled:no-response "9007199254740991"=result:g1 "s7"=cancelled:result:g0 2147483648=cancelled:result:g2`

### random/seed-21
- `py-http-json` (python-sdk): `[R3,R5] "1"=LOST "7"=result:g2 "s42"=cancelled:error:-32800 1=result:g1`
- `py-http-sse` (python-sdk): `[R3,R5] "1"=LOST "7"=result:g2 "s42"=cancelled:error:-32800 1=result:g1`
- `py-stdio` (python-sdk): `[ok] "1"=result:g3 "7"=result:g2 "s42"=cancelled:no-response 1=result:g1`

### random/seed-22
- `py-http-json` (python-sdk): `[R3] "-1"=result:g2 "1"=LOST "s1"=result:g0 1=result:g3`
- `py-http-sse` (python-sdk): `[R3] "-1"=result:g2 "1"=LOST "s1"=result:g0 1=result:g3`
- `py-stdio` (python-sdk): `[ok] "-1"=result:g2 "1"=result:g1 "s1"=result:g0 1=result:g3`

### random/seed-23
- `py-http-json` (python-sdk): `[R3,R6] "9007199254740991"=cancelled:error:-32800 "s0"=cancelled:error:-32800 7=result:g3 9007199254740991=LOST`
- `py-http-sse` (python-sdk): `[R3,R6] "9007199254740991"=cancelled:error:-32800 "s0"=cancelled:error:-32800 7=result:g3 9007199254740991=LOST`
- `py-stdio` (python-sdk): `[ok] "9007199254740991"=cancelled:no-response "s0"=cancelled:no-response 7=result:g3 9007199254740991=result:g0`

### random/seed-24
- `py-http-json` (python-sdk): `[R3] "2147483648"=result:g3 "s42"=result:g1 1=result:g0 2147483648=LOST`
- `py-http-sse` (python-sdk): `[R3] "2147483648"=result:g3 "s42"=result:g1 1=result:g0 2147483648=LOST`
- `py-stdio` (python-sdk): `[ok] "2147483648"=result:g3 "s42"=result:g1 1=result:g0 2147483648=result:g2`

### random/seed-25
- `py-http-json` (python-sdk): `[R3,R5] "1"=result:g3 "42"=result:g1 42=LOST 9007199254740991=result:g0`
- `py-http-sse` (python-sdk): `[R3,R5] "1"=result:g3 "42"=result:g1 42=LOST 9007199254740991=result:g0`
- `py-stdio` (python-sdk): `[ok] "1"=result:g3 "42"=result:g1 42=result:g2 9007199254740991=result:g0`

### random/seed-26
- `py-http-json` (python-sdk): `[R3] "1"=result:g2 "2147483648"=LOST "s1"=result:g0 2147483648=result:g3`
- `py-http-sse` (python-sdk): `[R3] "1"=result:g2 "2147483648"=LOST "s1"=result:g0 2147483648=result:g3`
- `py-stdio` (python-sdk): `[ok] "1"=result:g2 "2147483648"=result:g1 "s1"=result:g0 2147483648=result:g3`

### random/seed-27
- `py-http-json` (python-sdk): `[R4,R6] "2147483648"=error:-32800 "7"=result:g0 "s42"=cancelled:error:-32800 2147483648=cancelled:no-response`
- `py-http-sse` (python-sdk): `[R4,R6] "2147483648"=error:-32800 "7"=result:g0 "s42"=cancelled:error:-32800 2147483648=cancelled:no-response`
- `py-stdio` (python-sdk): `[R3,R6] "2147483648"=LOST "7"=result:g0 "s42"=cancelled:no-response 2147483648=cancelled:result:g2`

### random/seed-28
- `py-http-json` (python-sdk): `[R5] "0"=cancelled:no-response "s-1"=cancelled:error:-32800 0=cancelled:result:g2 2147483648=result:g1`
- `py-http-sse` (python-sdk): `[R5] "0"=cancelled:no-response "s-1"=cancelled:error:-32800 0=cancelled:result:g2 2147483648=result:g1`
- `py-stdio` (python-sdk): `[ok] "0"=cancelled:no-response "s-1"=cancelled:no-response 0=cancelled:result:g2 2147483648=result:g1`

### random/seed-29
- `py-http-json` (python-sdk): `[R3,R6] "-1"=LOST "0"=cancelled:error:-32800 "s-1"=cancelled:error:-32800 -1=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[R3,R6] "-1"=LOST "0"=cancelled:error:-32800 "s-1"=cancelled:error:-32800 -1=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "-1"=result:g1 "0"=cancelled:no-response "s-1"=cancelled:no-response -1=cancelled:no-response`

### random/seed-3
- `py-http-json` (python-sdk): `[R5] "-1"=result:g1 "1"=cancelled:result:g0 "s-1"=cancelled:result:g2 1=cancelled:no-response`
- `py-http-sse` (python-sdk): `[R5] "-1"=result:g1 "1"=cancelled:result:g0 "s-1"=cancelled:result:g2 1=cancelled:no-response`
- `py-stdio` (python-sdk): `[ok] "-1"=result:g1 "1"=cancelled:result:g0 "s-1"=cancelled:result:g2 1=cancelled:no-response`

### random/seed-30
- `py-http-json` (python-sdk): `[R3,R6] "-1"=cancelled:error:-32800 "9007199254740991"=cancelled:error:-32800 "s-1"=cancelled:error:-32800 -1=LOST`
- `py-http-sse` (python-sdk): `[R3,R6] "-1"=cancelled:error:-32800 "9007199254740991"=cancelled:error:-32800 "s-1"=cancelled:error:-32800 -1=LOST`
- `py-stdio` (python-sdk): `[ok] "-1"=cancelled:no-response "9007199254740991"=cancelled:no-response "s-1"=cancelled:no-response -1=result:g1`

### random/seed-31
- `py-http-json` (python-sdk): `[R3] "0"=result:g3 "9007199254740991"=cancelled:result:g0 0=LOST 42=result:g2`
- `py-http-sse` (python-sdk): `[R3] "0"=result:g3 "9007199254740991"=cancelled:result:g0 0=LOST 42=result:g2`
- `py-stdio` (python-sdk): `[ok] "0"=result:g3 "9007199254740991"=cancelled:result:g0 0=result:g1 42=result:g2`

### random/seed-32
- `py-http-json` (python-sdk): `[R3] "0"=result:g3 "s7"=result:g2 0=LOST 1=result:g0`
- `py-http-sse` (python-sdk): `[R3] "0"=result:g3 "s7"=result:g2 0=LOST 1=result:g0`
- `py-stdio` (python-sdk): `[ok] "0"=result:g3 "s7"=result:g2 0=result:g1 1=result:g0`

### random/seed-33
- `py-http-json` (python-sdk): `[R3,R6] "-1"=LOST "1"=cancelled:error:-32800 "s1"=result:g2 -1=cancelled:result:g1`
- `py-http-sse` (python-sdk): `[R3,R6] "-1"=LOST "1"=cancelled:error:-32800 "s1"=result:g2 -1=cancelled:result:g1`
- `py-stdio` (python-sdk): `[ok] "-1"=result:g0 "1"=cancelled:no-response "s1"=result:g2 -1=cancelled:result:g1`

### random/seed-34
- `py-http-json` (python-sdk): `[R3,R5] "-1"=result:g2 "s7"=result:g1 -1=LOST 0=result:g0`
- `py-http-sse` (python-sdk): `[R3,R5] "-1"=result:g2 "s7"=result:g1 -1=LOST 0=result:g0`
- `py-stdio` (python-sdk): `[ok] "-1"=result:g2 "s7"=result:g1 -1=result:g3 0=result:g0`

### random/seed-35
- `py-http-json` (python-sdk): `[R3,R5,R6] "-1"=LOST "2147483648"=cancelled:error:-32800 -1=cancelled:result:g0 7=result:g1`
- `py-http-sse` (python-sdk): `[R3,R5,R6] "-1"=LOST "2147483648"=cancelled:error:-32800 -1=cancelled:result:g0 7=result:g1`
- `py-stdio` (python-sdk): `[ok] "-1"=result:g3 "2147483648"=cancelled:no-response -1=cancelled:result:g0 7=result:g1`

### random/seed-36
- `py-http-json` (python-sdk): `[R3,R5] "7"=result:g0 "9007199254740991"=cancelled:error:-32800 0=result:g1 7=LOST`
- `py-http-sse` (python-sdk): `[R3,R5] "7"=result:g0 "9007199254740991"=cancelled:error:-32800 0=result:g1 7=LOST`
- `py-stdio` (python-sdk): `[ok] "7"=result:g0 "9007199254740991"=cancelled:no-response 0=result:g1 7=result:g3`

### random/seed-37
- `py-http-json` (python-sdk): `[R3,R5,R6] "2147483648"=cancelled:result:g1 "s-1"=cancelled:result:g0 -1=cancelled:error:-32800 2147483648=LOST`
- `py-http-sse` (python-sdk): `[R3,R5,R6] "2147483648"=cancelled:result:g1 "s-1"=cancelled:result:g0 -1=cancelled:error:-32800 2147483648=LOST`
- `py-stdio` (python-sdk): `[R3,R6] "2147483648"=cancelled:result:g1 "s-1"=cancelled:result:g0 -1=cancelled:no-response 2147483648=LOST`

### random/seed-38
- `py-http-json` (python-sdk): `[R5] "2147483648"=result:g1 "42"=cancelled:result:g0 "s9007199254740991"=cancelled:result:g2 2147483648=cancelled:no-response`
- `py-http-sse` (python-sdk): `[R5] "2147483648"=result:g1 "42"=cancelled:result:g0 "s9007199254740991"=cancelled:result:g2 2147483648=cancelled:no-response`
- `py-stdio` (python-sdk): `[ok] "2147483648"=result:g1 "42"=cancelled:result:g0 "s9007199254740991"=cancelled:result:g2 2147483648=cancelled:result:g3`

### random/seed-39
- `py-http-json` (python-sdk): `[R3,R6] "1"=cancelled:error:-32800 "7"=result:g0 0=cancelled:error:-32800 1=LOST`
- `py-http-sse` (python-sdk): `[R3,R6] "1"=cancelled:error:-32800 "7"=result:g0 0=cancelled:error:-32800 1=LOST`
- `py-stdio` (python-sdk): `[ok] "1"=cancelled:no-response "7"=result:g0 0=cancelled:no-response 1=result:g1`

### random/seed-4
- `py-http-json` (python-sdk): `[R3] "1"=LOST "2147483648"=result:g3 1=result:g2 7=result:g1`
- `py-http-sse` (python-sdk): `[R3] "1"=LOST "2147483648"=result:g3 1=result:g2 7=result:g1`
- `py-stdio` (python-sdk): `[ok] "1"=result:g0 "2147483648"=result:g3 1=result:g2 7=result:g1`

### random/seed-40
- `py-http-json` (python-sdk): `[R3] "42"=LOST "s-1"=result:g3 0=cancelled:error:-32800 42=result:g1`
- `py-http-sse` (python-sdk): `[R3] "42"=LOST "s-1"=result:g3 0=cancelled:error:-32800 42=result:g1`
- `py-stdio` (python-sdk): `[ok] "42"=result:g0 "s-1"=result:g3 0=cancelled:no-response 42=result:g1`

### random/seed-41
- `py-http-json` (python-sdk): `[R4,R6] "1"=cancelled:error:-32800 "42"=error:-32800 42=cancelled:no-response 7=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[R4,R6] "1"=cancelled:error:-32800 "42"=error:-32800 42=cancelled:no-response 7=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[R3,R6] "1"=cancelled:no-response "42"=LOST 42=cancelled:result:g0 7=cancelled:no-response`

### random/seed-42
- `py-http-json` (python-sdk): `[R3,R5] "2147483648"=LOST 0=result:g2 1=result:g0 2147483648=result:g1`
- `py-http-sse` (python-sdk): `[R3,R5] "2147483648"=LOST 0=result:g2 1=result:g0 2147483648=result:g1`
- `py-stdio` (python-sdk): `[ok] "2147483648"=result:g3 0=result:g2 1=result:g0 2147483648=result:g1`

### random/seed-43
- `py-http-json` (python-sdk): `[R5] "0"=cancelled:no-response "s7"=cancelled:result:g0 0=result:g1 9007199254740991=cancelled:result:g3`
- `py-http-sse` (python-sdk): `[R5] "0"=cancelled:no-response "s7"=cancelled:result:g0 0=result:g1 9007199254740991=cancelled:result:g3`
- `py-stdio` (python-sdk): `[ok] "0"=cancelled:no-response "s7"=cancelled:result:g0 0=result:g1 9007199254740991=cancelled:result:g3`

### random/seed-44
- `py-http-json` (python-sdk): `[R5] "42"=cancelled:no-response "s-1"=cancelled:error:-32800 2147483648=result:g2 42=result:g1`
- `py-http-sse` (python-sdk): `[R5] "42"=cancelled:no-response "s-1"=cancelled:error:-32800 2147483648=result:g2 42=result:g1`
- `py-stdio` (python-sdk): `[ok] "42"=cancelled:result:g3 "s-1"=cancelled:no-response 2147483648=result:g2 42=result:g1`

### random/seed-45
- `py-http-json` (python-sdk): `[ok] "42"=cancelled:result:g1 "7"=cancelled:no-response 0=result:g3 7=result:g2`
- `py-http-sse` (python-sdk): `[ok] "42"=cancelled:result:g1 "7"=cancelled:no-response 0=result:g3 7=result:g2`
- `py-stdio` (python-sdk): `[ok] "42"=cancelled:result:g1 "7"=cancelled:result:g0 0=result:g3 7=result:g2`

### random/seed-46
- `py-http-json` (python-sdk): `[R3,R5] "0"=LOST "s-1"=result:g0 0=result:g1 42=result:g2`
- `py-http-sse` (python-sdk): `[R3,R5] "0"=LOST "s-1"=result:g0 0=result:g1 42=result:g2`
- `py-stdio` (python-sdk): `[ok] "0"=result:g3 "s-1"=result:g0 0=result:g1 42=result:g2`

### random/seed-47
- `py-http-json` (python-sdk): `[R4,R6] "-1"=cancelled:result:g1 "0"=cancelled:result:g3 "7"=error:-32800 7=cancelled:no-response`
- `py-http-sse` (python-sdk): `[R4,R6] "-1"=cancelled:result:g1 "0"=cancelled:result:g3 "7"=error:-32800 7=cancelled:no-response`
- `py-stdio` (python-sdk): `[R3,R6] "-1"=cancelled:result:g1 "0"=cancelled:result:g3 "7"=LOST 7=cancelled:result:g0`

### random/seed-48
- `py-http-json` (python-sdk): `[R5] "-1"=cancelled:result:g0 "s-1"=cancelled:error:-32800 -1=cancelled:no-response 7=result:g3`
- `py-http-sse` (python-sdk): `[R5] "-1"=cancelled:result:g0 "s-1"=cancelled:error:-32800 -1=cancelled:no-response 7=result:g3`
- `py-stdio` (python-sdk): `[ok] "-1"=cancelled:result:g0 "s-1"=cancelled:no-response -1=cancelled:no-response 7=result:g3`

### random/seed-49
- `py-http-json` (python-sdk): `[R3,R6] "0"=LOST "7"=result:g2 "s9007199254740991"=cancelled:error:-32800 0=cancelled:result:g3`
- `py-http-sse` (python-sdk): `[R3,R6] "0"=LOST "7"=result:g2 "s9007199254740991"=cancelled:error:-32800 0=cancelled:result:g3`
- `py-stdio` (python-sdk): `[ok] "0"=result:g0 "7"=result:g2 "s9007199254740991"=cancelled:no-response 0=cancelled:result:g3`

### random/seed-5
- `py-http-json` (python-sdk): `[R3,R5] "-1"=result:g2 "s7"=result:g0 "s9007199254740991"=result:g1 -1=LOST`
- `py-http-sse` (python-sdk): `[R3,R5] "-1"=result:g2 "s7"=result:g0 "s9007199254740991"=result:g1 -1=LOST`
- `py-stdio` (python-sdk): `[ok] "-1"=result:g2 "s7"=result:g0 "s9007199254740991"=result:g1 -1=result:g3`

### random/seed-50
- `py-http-json` (python-sdk): `[R4,R6] "42"=error:-32800 "9007199254740991"=cancelled:error:-32800 "s7"=result:g1 42=cancelled:no-response`
- `py-http-sse` (python-sdk): `[R4,R6] "42"=error:-32800 "9007199254740991"=cancelled:error:-32800 "s7"=result:g1 42=cancelled:no-response`
- `py-stdio` (python-sdk): `[R3,R6] "42"=LOST "9007199254740991"=cancelled:no-response "s7"=result:g1 42=cancelled:result:g0`

### random/seed-6
- `py-http-json` (python-sdk): `[R3,R5,R6] "42"=cancelled:error:-32800 "9007199254740991"=cancelled:result:g0 -1=cancelled:error:-32800 9007199254740991=LOST`
- `py-http-sse` (python-sdk): `[R3,R5,R6] "42"=cancelled:error:-32800 "9007199254740991"=cancelled:result:g0 -1=cancelled:error:-32800 9007199254740991=LOST`
- `py-stdio` (python-sdk): `[R3,R6] "42"=cancelled:no-response "9007199254740991"=cancelled:result:g0 -1=cancelled:no-response 9007199254740991=LOST`

### random/seed-7
- `py-http-json` (python-sdk): `[ok] "1"=cancelled:result:g2 "7"=cancelled:no-response 2147483648=result:g1 7=result:g3`
- `py-http-sse` (python-sdk): `[ok] "1"=cancelled:result:g2 "7"=cancelled:no-response 2147483648=result:g1 7=result:g3`
- `py-stdio` (python-sdk): `[ok] "1"=cancelled:result:g2 "7"=cancelled:result:g0 2147483648=result:g1 7=result:g3`

### random/seed-8
- `py-http-json` (python-sdk): `[R3,R6] "1"=LOST "7"=result:g1 1=cancelled:error:-32800 2147483648=result:g2`
- `py-http-sse` (python-sdk): `[R3,R6] "1"=LOST "7"=result:g1 1=cancelled:error:-32800 2147483648=result:g2`
- `py-stdio` (python-sdk): `[ok] "1"=result:g0 "7"=result:g1 1=cancelled:no-response 2147483648=result:g2`

### random/seed-9
- `py-http-json` (python-sdk): `[R3,R6] "-1"=cancelled:error:-32800 "42"=cancelled:result:g3 42=LOST 7=result:g0`
- `py-http-sse` (python-sdk): `[R3,R6] "-1"=cancelled:error:-32800 "42"=cancelled:result:g3 42=LOST 7=result:g0`
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
