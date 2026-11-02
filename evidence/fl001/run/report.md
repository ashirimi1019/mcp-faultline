# MCP Faultline report: FL-001 Typed JSON-RPC request-id isolation

## Provenance

- **harness**: `mcp-faultline 0.1.0`
- **harness_commit**: `feeee275b946002402e1d5239065e363adb26062`
- **python**: `3.12.14`
- **platform**: `Windows-11-10.0.26300-SP0`
- **started_utc**: `2026-11-02T19:43:05+00:00`
- **protocol_revision**: `2025-11-25`
- **fault**: `None`

## Targets

| target | implementation | version | pinned | transport |
|---|---|---|---|---|
| `py-stdio` | python-sdk | 2.3.0 | 2.3.0 | stdio |
| `py-http-sse` | python-sdk | 2.3.0 | 2.3.0 | http-sse |
| `py-http-json` | python-sdk | 2.3.0 | 2.3.0 | http-json |
| `ts-stdio` | typescript-sdk | 1.32.2 | 1.32.2 | stdio |
| `ts-http-sse` | typescript-sdk | 1.32.2 | 1.32.2 | http-sse |
| `ts-http-json` | typescript-sdk | 1.32.2 | 1.32.2 | http-json |
| `ts2-stdio` | typescript-sdk-v2 | 2.4.0 | 2.4.0 | stdio |
| `ts2-http-sse` | typescript-sdk-v2 | 2.4.0 | 2.4.0 | http-sse |
| `ts2-http-json` | typescript-sdk-v2 | 2.4.0 | 2.4.0 | http-json |

## Result matrix

| scenario | `py-stdio` | `py-http-sse` | `py-http-json` | `ts-stdio` | `ts-http-sse` | `ts-http-json` | `ts2-stdio` | `ts2-http-sse` | `ts2-http-json` |
|---|---|---|---|---|---|---|---|---|---|
| collide-0/cancel-first | FAIL R3,R6 | FAIL R4,R6 | FAIL R4,R6 | pass | pass | pass | pass | pass | pass |
| collide-0/cancel-second | pass | FAIL R3,R6 | FAIL R3,R6 | pass | pass | pass | pass | pass | pass |
| collide-0/out-of-order | pass | FAIL R3 | FAIL R3 | pass | pass | pass | pass | pass | pass |
| collide-7-strfirst/cancel-first | FAIL R3,R6 | FAIL R4,R6 | FAIL R4,R6 | pass | pass | pass | pass | pass | pass |
| collide-7-strfirst/cancel-second | pass | FAIL R3,R6 | FAIL R3,R6 | pass | pass | pass | pass | pass | pass |
| collide-7-strfirst/out-of-order | pass | FAIL R3 | FAIL R3 | pass | pass | pass | pass | pass | pass |
| collide-7/cancel-first | FAIL R3,R6 | FAIL R4,R6 | FAIL R4,R6 | pass | pass | pass | pass | pass | pass |
| collide-7/cancel-second | pass | FAIL R3,R6 | FAIL R3,R6 | pass | pass | pass | pass | pass | pass |
| collide-7/out-of-order | pass | FAIL R3 | FAIL R3 | pass | pass | pass | pass | pass | pass |
| collide-neg/cancel-first | FAIL R3,R6 | FAIL R4,R6 | FAIL R4,R6 | pass | pass | pass | pass | pass | pass |
| collide-neg/cancel-second | pass | FAIL R3,R6 | FAIL R3,R6 | pass | pass | pass | pass | pass | pass |
| collide-neg/out-of-order | pass | FAIL R3 | FAIL R3 | pass | pass | pass | pass | pass | pass |
| control-int/cancel-first | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| control-int/cancel-second | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| control-int/out-of-order | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| control-mixed/cancel-first | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| control-mixed/cancel-second | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| control-mixed/out-of-order | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| control-str/cancel-first | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| control-str/cancel-second | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| control-str/out-of-order | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| noncanonical-07/cancel-first | FAIL R3 | FAIL R4 | FAIL R4 | pass | pass | pass | pass | pass | pass |
| noncanonical-07/cancel-second | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| noncanonical-07/out-of-order | pass | pass | pass | pass | pass | pass | pass | pass | pass |

**185 passed, 31 failed** of 216 runs.

## Violations

### `py-stdio` - collide-7/cancel-first
- **R3** (every non-cancelled request receives a response): request "7" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling 7 suppressed the response to "7"
- trace: `evidence/fl001/run/traces/py_stdio__collide_7_cancel_first.json`

### `py-stdio` - collide-7-strfirst/cancel-first
- **R3** (every non-cancelled request receives a response): request 7 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "7" suppressed the response to 7
- trace: `evidence/fl001/run/traces/py_stdio__collide_7_strfirst_cancel_first.json`

### `py-stdio` - collide-0/cancel-first
- **R3** (every non-cancelled request receives a response): request "0" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling 0 suppressed the response to "0"
- trace: `evidence/fl001/run/traces/py_stdio__collide_0_cancel_first.json`

### `py-stdio` - collide-neg/cancel-first
- **R3** (every non-cancelled request receives a response): request "-1" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling -1 suppressed the response to "-1"
- trace: `evidence/fl001/run/traces/py_stdio__collide_neg_cancel_first.json`

### `py-stdio` - noncanonical-07/cancel-first
- **R3** (every non-cancelled request receives a response): request "07" never received a response
- trace: `evidence/fl001/run/traces/py_stdio__noncanonical_07_cancel_first.json`

### `py-http-sse` - collide-7/out-of-order
- **R3** (every non-cancelled request receives a response): request 7 never received a response
- trace: `evidence/fl001/run/traces/py_http_sse__collide_7_out_of_order.json`

### `py-http-sse` - collide-7/cancel-first
- **R4** (response payload belongs to its own request): request "7" was never cancelled but got error -32800
- **R6** (cancelling one id never suppresses another id's response): cancelling 7 produced an error response for "7"
- trace: `evidence/fl001/run/traces/py_http_sse__collide_7_cancel_first.json`

### `py-http-sse` - collide-7/cancel-second
- **R3** (every non-cancelled request receives a response): request 7 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "7" suppressed the response to 7
- trace: `evidence/fl001/run/traces/py_http_sse__collide_7_cancel_second.json`

### `py-http-sse` - collide-7-strfirst/out-of-order
- **R3** (every non-cancelled request receives a response): request "7" never received a response
- trace: `evidence/fl001/run/traces/py_http_sse__collide_7_strfirst_out_of_order.json`

### `py-http-sse` - collide-7-strfirst/cancel-first
- **R4** (response payload belongs to its own request): request 7 was never cancelled but got error -32800
- **R6** (cancelling one id never suppresses another id's response): cancelling "7" produced an error response for 7
- trace: `evidence/fl001/run/traces/py_http_sse__collide_7_strfirst_cancel_first.json`

### `py-http-sse` - collide-7-strfirst/cancel-second
- **R3** (every non-cancelled request receives a response): request "7" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling 7 suppressed the response to "7"
- trace: `evidence/fl001/run/traces/py_http_sse__collide_7_strfirst_cancel_second.json`

### `py-http-sse` - collide-0/out-of-order
- **R3** (every non-cancelled request receives a response): request 0 never received a response
- trace: `evidence/fl001/run/traces/py_http_sse__collide_0_out_of_order.json`

### `py-http-sse` - collide-0/cancel-first
- **R4** (response payload belongs to its own request): request "0" was never cancelled but got error -32800
- **R6** (cancelling one id never suppresses another id's response): cancelling 0 produced an error response for "0"
- trace: `evidence/fl001/run/traces/py_http_sse__collide_0_cancel_first.json`

### `py-http-sse` - collide-0/cancel-second
- **R3** (every non-cancelled request receives a response): request 0 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "0" suppressed the response to 0
- trace: `evidence/fl001/run/traces/py_http_sse__collide_0_cancel_second.json`

### `py-http-sse` - collide-neg/out-of-order
- **R3** (every non-cancelled request receives a response): request -1 never received a response
- trace: `evidence/fl001/run/traces/py_http_sse__collide_neg_out_of_order.json`

### `py-http-sse` - collide-neg/cancel-first
- **R4** (response payload belongs to its own request): request "-1" was never cancelled but got error -32800
- **R6** (cancelling one id never suppresses another id's response): cancelling -1 produced an error response for "-1"
- trace: `evidence/fl001/run/traces/py_http_sse__collide_neg_cancel_first.json`

### `py-http-sse` - collide-neg/cancel-second
- **R3** (every non-cancelled request receives a response): request -1 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "-1" suppressed the response to -1
- trace: `evidence/fl001/run/traces/py_http_sse__collide_neg_cancel_second.json`

### `py-http-sse` - noncanonical-07/cancel-first
- **R4** (response payload belongs to its own request): request "07" was never cancelled but got error -32800
- trace: `evidence/fl001/run/traces/py_http_sse__noncanonical_07_cancel_first.json`

### `py-http-json` - collide-7/out-of-order
- **R3** (every non-cancelled request receives a response): request 7 never received a response
- trace: `evidence/fl001/run/traces/py_http_json__collide_7_out_of_order.json`

### `py-http-json` - collide-7/cancel-first
- **R4** (response payload belongs to its own request): request "7" was never cancelled but got error -32800
- **R6** (cancelling one id never suppresses another id's response): cancelling 7 produced an error response for "7"
- trace: `evidence/fl001/run/traces/py_http_json__collide_7_cancel_first.json`

### `py-http-json` - collide-7/cancel-second
- **R3** (every non-cancelled request receives a response): request 7 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "7" suppressed the response to 7
- trace: `evidence/fl001/run/traces/py_http_json__collide_7_cancel_second.json`

### `py-http-json` - collide-7-strfirst/out-of-order
- **R3** (every non-cancelled request receives a response): request "7" never received a response
- trace: `evidence/fl001/run/traces/py_http_json__collide_7_strfirst_out_of_order.json`

### `py-http-json` - collide-7-strfirst/cancel-first
- **R4** (response payload belongs to its own request): request 7 was never cancelled but got error -32800
- **R6** (cancelling one id never suppresses another id's response): cancelling "7" produced an error response for 7
- trace: `evidence/fl001/run/traces/py_http_json__collide_7_strfirst_cancel_first.json`

### `py-http-json` - collide-7-strfirst/cancel-second
- **R3** (every non-cancelled request receives a response): request "7" never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling 7 suppressed the response to "7"
- trace: `evidence/fl001/run/traces/py_http_json__collide_7_strfirst_cancel_second.json`

### `py-http-json` - collide-0/out-of-order
- **R3** (every non-cancelled request receives a response): request 0 never received a response
- trace: `evidence/fl001/run/traces/py_http_json__collide_0_out_of_order.json`

### `py-http-json` - collide-0/cancel-first
- **R4** (response payload belongs to its own request): request "0" was never cancelled but got error -32800
- **R6** (cancelling one id never suppresses another id's response): cancelling 0 produced an error response for "0"
- trace: `evidence/fl001/run/traces/py_http_json__collide_0_cancel_first.json`

### `py-http-json` - collide-0/cancel-second
- **R3** (every non-cancelled request receives a response): request 0 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "0" suppressed the response to 0
- trace: `evidence/fl001/run/traces/py_http_json__collide_0_cancel_second.json`

### `py-http-json` - collide-neg/out-of-order
- **R3** (every non-cancelled request receives a response): request -1 never received a response
- trace: `evidence/fl001/run/traces/py_http_json__collide_neg_out_of_order.json`

### `py-http-json` - collide-neg/cancel-first
- **R4** (response payload belongs to its own request): request "-1" was never cancelled but got error -32800
- **R6** (cancelling one id never suppresses another id's response): cancelling -1 produced an error response for "-1"
- trace: `evidence/fl001/run/traces/py_http_json__collide_neg_cancel_first.json`

### `py-http-json` - collide-neg/cancel-second
- **R3** (every non-cancelled request receives a response): request -1 never received a response
- **R6** (cancelling one id never suppresses another id's response): cancelling "-1" suppressed the response to -1
- trace: `evidence/fl001/run/traces/py_http_json__collide_neg_cancel_second.json`

### `py-http-json` - noncanonical-07/cancel-first
- **R4** (response payload belongs to its own request): request "07" was never cancelled but got error -32800
- trace: `evidence/fl001/run/traces/py_http_json__noncanonical_07_cancel_first.json`

## Cross-target divergences

### collide-0/cancel-first
- `py-http-json` (python-sdk): `[R4,R6] "0"=error:-32800 0=cancelled:no-response`
- `py-http-sse` (python-sdk): `[R4,R6] "0"=error:-32800 0=cancelled:no-response`
- `py-stdio` (python-sdk): `[R3,R6] "0"=LOST 0=cancelled:result:t-int-0`
- `ts-http-json` (typescript-sdk): `[ok] "0"=result:t-str-0 0=cancelled:result:t-int-0`
- `ts-http-sse` (typescript-sdk): `[ok] "0"=result:t-str-0 0=cancelled:result:t-int-0`
- `ts-stdio` (typescript-sdk): `[ok] "0"=result:t-str-0 0=cancelled:result:t-int-0`
- `ts2-http-json` (typescript-sdk-v2): `[ok] "0"=result:t-str-0 0=cancelled:no-response`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] "0"=result:t-str-0 0=cancelled:no-response`
- `ts2-stdio` (typescript-sdk-v2): `[ok] "0"=result:t-str-0 0=cancelled:no-response`

### collide-0/cancel-second
- `py-http-json` (python-sdk): `[R3,R6] "0"=cancelled:error:-32800 0=LOST`
- `py-http-sse` (python-sdk): `[R3,R6] "0"=cancelled:error:-32800 0=LOST`
- `py-stdio` (python-sdk): `[ok] "0"=cancelled:no-response 0=result:t-int-0`
- `ts-http-json` (typescript-sdk): `[ok] "0"=cancelled:no-response 0=result:t-int-0`
- `ts-http-sse` (typescript-sdk): `[ok] "0"=cancelled:no-response 0=result:t-int-0`
- `ts-stdio` (typescript-sdk): `[ok] "0"=cancelled:no-response 0=result:t-int-0`
- `ts2-http-json` (typescript-sdk-v2): `[ok] "0"=cancelled:no-response 0=result:t-int-0`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] "0"=cancelled:no-response 0=result:t-int-0`
- `ts2-stdio` (typescript-sdk-v2): `[ok] "0"=cancelled:no-response 0=result:t-int-0`

### collide-0/out-of-order
- `py-http-json` (python-sdk): `[R3] "0"=result:t-str-0 0=LOST`
- `py-http-sse` (python-sdk): `[R3] "0"=result:t-str-0 0=LOST`
- `py-stdio` (python-sdk): `[ok] "0"=result:t-str-0 0=result:t-int-0`
- `ts-http-json` (typescript-sdk): `[ok] "0"=result:t-str-0 0=result:t-int-0`
- `ts-http-sse` (typescript-sdk): `[ok] "0"=result:t-str-0 0=result:t-int-0`
- `ts-stdio` (typescript-sdk): `[ok] "0"=result:t-str-0 0=result:t-int-0`
- `ts2-http-json` (typescript-sdk-v2): `[ok] "0"=result:t-str-0 0=result:t-int-0`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] "0"=result:t-str-0 0=result:t-int-0`
- `ts2-stdio` (typescript-sdk-v2): `[ok] "0"=result:t-str-0 0=result:t-int-0`

### collide-7-strfirst/cancel-first
- `py-http-json` (python-sdk): `[R4,R6] "7"=cancelled:no-response 7=error:-32800`
- `py-http-sse` (python-sdk): `[R4,R6] "7"=cancelled:no-response 7=error:-32800`
- `py-stdio` (python-sdk): `[R3,R6] "7"=cancelled:result:t-str-7 7=LOST`
- `ts-http-json` (typescript-sdk): `[ok] "7"=cancelled:no-response 7=result:t-int-7`
- `ts-http-sse` (typescript-sdk): `[ok] "7"=cancelled:no-response 7=result:t-int-7`
- `ts-stdio` (typescript-sdk): `[ok] "7"=cancelled:no-response 7=result:t-int-7`
- `ts2-http-json` (typescript-sdk-v2): `[ok] "7"=cancelled:no-response 7=result:t-int-7`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] "7"=cancelled:no-response 7=result:t-int-7`
- `ts2-stdio` (typescript-sdk-v2): `[ok] "7"=cancelled:no-response 7=result:t-int-7`

### collide-7-strfirst/cancel-second
- `py-http-json` (python-sdk): `[R3,R6] "7"=LOST 7=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[R3,R6] "7"=LOST 7=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "7"=result:t-str-7 7=cancelled:no-response`
- `ts-http-json` (typescript-sdk): `[ok] "7"=result:t-str-7 7=cancelled:no-response`
- `ts-http-sse` (typescript-sdk): `[ok] "7"=result:t-str-7 7=cancelled:no-response`
- `ts-stdio` (typescript-sdk): `[ok] "7"=result:t-str-7 7=cancelled:no-response`
- `ts2-http-json` (typescript-sdk-v2): `[ok] "7"=result:t-str-7 7=cancelled:no-response`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] "7"=result:t-str-7 7=cancelled:no-response`
- `ts2-stdio` (typescript-sdk-v2): `[ok] "7"=result:t-str-7 7=cancelled:no-response`

### collide-7-strfirst/out-of-order
- `py-http-json` (python-sdk): `[R3] "7"=LOST 7=result:t-int-7`
- `py-http-sse` (python-sdk): `[R3] "7"=LOST 7=result:t-int-7`
- `py-stdio` (python-sdk): `[ok] "7"=result:t-str-7 7=result:t-int-7`
- `ts-http-json` (typescript-sdk): `[ok] "7"=result:t-str-7 7=result:t-int-7`
- `ts-http-sse` (typescript-sdk): `[ok] "7"=result:t-str-7 7=result:t-int-7`
- `ts-stdio` (typescript-sdk): `[ok] "7"=result:t-str-7 7=result:t-int-7`
- `ts2-http-json` (typescript-sdk-v2): `[ok] "7"=result:t-str-7 7=result:t-int-7`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] "7"=result:t-str-7 7=result:t-int-7`
- `ts2-stdio` (typescript-sdk-v2): `[ok] "7"=result:t-str-7 7=result:t-int-7`

### collide-7/cancel-first
- `py-http-json` (python-sdk): `[R4,R6] "7"=error:-32800 7=cancelled:no-response`
- `py-http-sse` (python-sdk): `[R4,R6] "7"=error:-32800 7=cancelled:no-response`
- `py-stdio` (python-sdk): `[R3,R6] "7"=LOST 7=cancelled:result:t-int-7`
- `ts-http-json` (typescript-sdk): `[ok] "7"=result:t-str-7 7=cancelled:no-response`
- `ts-http-sse` (typescript-sdk): `[ok] "7"=result:t-str-7 7=cancelled:no-response`
- `ts-stdio` (typescript-sdk): `[ok] "7"=result:t-str-7 7=cancelled:no-response`
- `ts2-http-json` (typescript-sdk-v2): `[ok] "7"=result:t-str-7 7=cancelled:no-response`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] "7"=result:t-str-7 7=cancelled:no-response`
- `ts2-stdio` (typescript-sdk-v2): `[ok] "7"=result:t-str-7 7=cancelled:no-response`

### collide-7/cancel-second
- `py-http-json` (python-sdk): `[R3,R6] "7"=cancelled:error:-32800 7=LOST`
- `py-http-sse` (python-sdk): `[R3,R6] "7"=cancelled:error:-32800 7=LOST`
- `py-stdio` (python-sdk): `[ok] "7"=cancelled:no-response 7=result:t-int-7`
- `ts-http-json` (typescript-sdk): `[ok] "7"=cancelled:no-response 7=result:t-int-7`
- `ts-http-sse` (typescript-sdk): `[ok] "7"=cancelled:no-response 7=result:t-int-7`
- `ts-stdio` (typescript-sdk): `[ok] "7"=cancelled:no-response 7=result:t-int-7`
- `ts2-http-json` (typescript-sdk-v2): `[ok] "7"=cancelled:no-response 7=result:t-int-7`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] "7"=cancelled:no-response 7=result:t-int-7`
- `ts2-stdio` (typescript-sdk-v2): `[ok] "7"=cancelled:no-response 7=result:t-int-7`

### collide-7/out-of-order
- `py-http-json` (python-sdk): `[R3] "7"=result:t-str-7 7=LOST`
- `py-http-sse` (python-sdk): `[R3] "7"=result:t-str-7 7=LOST`
- `py-stdio` (python-sdk): `[ok] "7"=result:t-str-7 7=result:t-int-7`
- `ts-http-json` (typescript-sdk): `[ok] "7"=result:t-str-7 7=result:t-int-7`
- `ts-http-sse` (typescript-sdk): `[ok] "7"=result:t-str-7 7=result:t-int-7`
- `ts-stdio` (typescript-sdk): `[ok] "7"=result:t-str-7 7=result:t-int-7`
- `ts2-http-json` (typescript-sdk-v2): `[ok] "7"=result:t-str-7 7=result:t-int-7`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] "7"=result:t-str-7 7=result:t-int-7`
- `ts2-stdio` (typescript-sdk-v2): `[ok] "7"=result:t-str-7 7=result:t-int-7`

### collide-neg/cancel-first
- `py-http-json` (python-sdk): `[R4,R6] "-1"=error:-32800 -1=cancelled:no-response`
- `py-http-sse` (python-sdk): `[R4,R6] "-1"=error:-32800 -1=cancelled:no-response`
- `py-stdio` (python-sdk): `[R3,R6] "-1"=LOST -1=cancelled:result:t-int--1`
- `ts-http-json` (typescript-sdk): `[ok] "-1"=result:t-str--1 -1=cancelled:no-response`
- `ts-http-sse` (typescript-sdk): `[ok] "-1"=result:t-str--1 -1=cancelled:no-response`
- `ts-stdio` (typescript-sdk): `[ok] "-1"=result:t-str--1 -1=cancelled:no-response`
- `ts2-http-json` (typescript-sdk-v2): `[ok] "-1"=result:t-str--1 -1=cancelled:no-response`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] "-1"=result:t-str--1 -1=cancelled:no-response`
- `ts2-stdio` (typescript-sdk-v2): `[ok] "-1"=result:t-str--1 -1=cancelled:no-response`

### collide-neg/cancel-second
- `py-http-json` (python-sdk): `[R3,R6] "-1"=cancelled:error:-32800 -1=LOST`
- `py-http-sse` (python-sdk): `[R3,R6] "-1"=cancelled:error:-32800 -1=LOST`
- `py-stdio` (python-sdk): `[ok] "-1"=cancelled:no-response -1=result:t-int--1`
- `ts-http-json` (typescript-sdk): `[ok] "-1"=cancelled:no-response -1=result:t-int--1`
- `ts-http-sse` (typescript-sdk): `[ok] "-1"=cancelled:no-response -1=result:t-int--1`
- `ts-stdio` (typescript-sdk): `[ok] "-1"=cancelled:no-response -1=result:t-int--1`
- `ts2-http-json` (typescript-sdk-v2): `[ok] "-1"=cancelled:no-response -1=result:t-int--1`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] "-1"=cancelled:no-response -1=result:t-int--1`
- `ts2-stdio` (typescript-sdk-v2): `[ok] "-1"=cancelled:no-response -1=result:t-int--1`

### collide-neg/out-of-order
- `py-http-json` (python-sdk): `[R3] "-1"=result:t-str--1 -1=LOST`
- `py-http-sse` (python-sdk): `[R3] "-1"=result:t-str--1 -1=LOST`
- `py-stdio` (python-sdk): `[ok] "-1"=result:t-str--1 -1=result:t-int--1`
- `ts-http-json` (typescript-sdk): `[ok] "-1"=result:t-str--1 -1=result:t-int--1`
- `ts-http-sse` (typescript-sdk): `[ok] "-1"=result:t-str--1 -1=result:t-int--1`
- `ts-stdio` (typescript-sdk): `[ok] "-1"=result:t-str--1 -1=result:t-int--1`
- `ts2-http-json` (typescript-sdk-v2): `[ok] "-1"=result:t-str--1 -1=result:t-int--1`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] "-1"=result:t-str--1 -1=result:t-int--1`
- `ts2-stdio` (typescript-sdk-v2): `[ok] "-1"=result:t-str--1 -1=result:t-int--1`

### control-int/cancel-first
- `py-http-json` (python-sdk): `[ok] 7=cancelled:error:-32800 8=result:t-int-8`
- `py-http-sse` (python-sdk): `[ok] 7=cancelled:error:-32800 8=result:t-int-8`
- `py-stdio` (python-sdk): `[ok] 7=cancelled:no-response 8=result:t-int-8`
- `ts-http-json` (typescript-sdk): `[ok] 7=cancelled:no-response 8=result:t-int-8`
- `ts-http-sse` (typescript-sdk): `[ok] 7=cancelled:no-response 8=result:t-int-8`
- `ts-stdio` (typescript-sdk): `[ok] 7=cancelled:no-response 8=result:t-int-8`
- `ts2-http-json` (typescript-sdk-v2): `[ok] 7=cancelled:no-response 8=result:t-int-8`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] 7=cancelled:no-response 8=result:t-int-8`
- `ts2-stdio` (typescript-sdk-v2): `[ok] 7=cancelled:no-response 8=result:t-int-8`

### control-int/cancel-second
- `py-http-json` (python-sdk): `[ok] 7=result:t-int-7 8=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] 7=result:t-int-7 8=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] 7=result:t-int-7 8=cancelled:no-response`
- `ts-http-json` (typescript-sdk): `[ok] 7=result:t-int-7 8=cancelled:no-response`
- `ts-http-sse` (typescript-sdk): `[ok] 7=result:t-int-7 8=cancelled:no-response`
- `ts-stdio` (typescript-sdk): `[ok] 7=result:t-int-7 8=cancelled:no-response`
- `ts2-http-json` (typescript-sdk-v2): `[ok] 7=result:t-int-7 8=cancelled:no-response`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] 7=result:t-int-7 8=cancelled:no-response`
- `ts2-stdio` (typescript-sdk-v2): `[ok] 7=result:t-int-7 8=cancelled:no-response`

### control-mixed/cancel-first
- `py-http-json` (python-sdk): `[ok] "x7"=result:t-str-x7 7=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "x7"=result:t-str-x7 7=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "x7"=result:t-str-x7 7=cancelled:no-response`
- `ts-http-json` (typescript-sdk): `[ok] "x7"=result:t-str-x7 7=cancelled:no-response`
- `ts-http-sse` (typescript-sdk): `[ok] "x7"=result:t-str-x7 7=cancelled:no-response`
- `ts-stdio` (typescript-sdk): `[ok] "x7"=result:t-str-x7 7=cancelled:no-response`
- `ts2-http-json` (typescript-sdk-v2): `[ok] "x7"=result:t-str-x7 7=cancelled:no-response`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] "x7"=result:t-str-x7 7=cancelled:no-response`
- `ts2-stdio` (typescript-sdk-v2): `[ok] "x7"=result:t-str-x7 7=cancelled:no-response`

### control-mixed/cancel-second
- `py-http-json` (python-sdk): `[ok] "x7"=cancelled:error:-32800 7=result:t-int-7`
- `py-http-sse` (python-sdk): `[ok] "x7"=cancelled:error:-32800 7=result:t-int-7`
- `py-stdio` (python-sdk): `[ok] "x7"=cancelled:no-response 7=result:t-int-7`
- `ts-http-json` (typescript-sdk): `[ok] "x7"=cancelled:no-response 7=result:t-int-7`
- `ts-http-sse` (typescript-sdk): `[ok] "x7"=cancelled:no-response 7=result:t-int-7`
- `ts-stdio` (typescript-sdk): `[ok] "x7"=cancelled:no-response 7=result:t-int-7`
- `ts2-http-json` (typescript-sdk-v2): `[ok] "x7"=cancelled:no-response 7=result:t-int-7`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] "x7"=cancelled:no-response 7=result:t-int-7`
- `ts2-stdio` (typescript-sdk-v2): `[ok] "x7"=cancelled:no-response 7=result:t-int-7`

### control-str/cancel-first
- `py-http-json` (python-sdk): `[ok] "a7"=cancelled:error:-32800 "b7"=result:t-str-b7`
- `py-http-sse` (python-sdk): `[ok] "a7"=cancelled:error:-32800 "b7"=result:t-str-b7`
- `py-stdio` (python-sdk): `[ok] "a7"=cancelled:no-response "b7"=result:t-str-b7`
- `ts-http-json` (typescript-sdk): `[ok] "a7"=cancelled:no-response "b7"=result:t-str-b7`
- `ts-http-sse` (typescript-sdk): `[ok] "a7"=cancelled:no-response "b7"=result:t-str-b7`
- `ts-stdio` (typescript-sdk): `[ok] "a7"=cancelled:no-response "b7"=result:t-str-b7`
- `ts2-http-json` (typescript-sdk-v2): `[ok] "a7"=cancelled:no-response "b7"=result:t-str-b7`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] "a7"=cancelled:no-response "b7"=result:t-str-b7`
- `ts2-stdio` (typescript-sdk-v2): `[ok] "a7"=cancelled:no-response "b7"=result:t-str-b7`

### control-str/cancel-second
- `py-http-json` (python-sdk): `[ok] "a7"=result:t-str-a7 "b7"=cancelled:error:-32800`
- `py-http-sse` (python-sdk): `[ok] "a7"=result:t-str-a7 "b7"=cancelled:error:-32800`
- `py-stdio` (python-sdk): `[ok] "a7"=result:t-str-a7 "b7"=cancelled:no-response`
- `ts-http-json` (typescript-sdk): `[ok] "a7"=result:t-str-a7 "b7"=cancelled:no-response`
- `ts-http-sse` (typescript-sdk): `[ok] "a7"=result:t-str-a7 "b7"=cancelled:no-response`
- `ts-stdio` (typescript-sdk): `[ok] "a7"=result:t-str-a7 "b7"=cancelled:no-response`
- `ts2-http-json` (typescript-sdk-v2): `[ok] "a7"=result:t-str-a7 "b7"=cancelled:no-response`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] "a7"=result:t-str-a7 "b7"=cancelled:no-response`
- `ts2-stdio` (typescript-sdk-v2): `[ok] "a7"=result:t-str-a7 "b7"=cancelled:no-response`

### noncanonical-07/cancel-first
- `py-http-json` (python-sdk): `[R4] "07"=error:-32800 7=cancelled:result:t-int-7`
- `py-http-sse` (python-sdk): `[R4] "07"=error:-32800 7=cancelled:result:t-int-7`
- `py-stdio` (python-sdk): `[R3] "07"=LOST 7=cancelled:result:t-int-7`
- `ts-http-json` (typescript-sdk): `[ok] "07"=result:t-str-07 7=cancelled:no-response`
- `ts-http-sse` (typescript-sdk): `[ok] "07"=result:t-str-07 7=cancelled:no-response`
- `ts-stdio` (typescript-sdk): `[ok] "07"=result:t-str-07 7=cancelled:no-response`
- `ts2-http-json` (typescript-sdk-v2): `[ok] "07"=result:t-str-07 7=cancelled:no-response`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] "07"=result:t-str-07 7=cancelled:no-response`
- `ts2-stdio` (typescript-sdk-v2): `[ok] "07"=result:t-str-07 7=cancelled:no-response`

### noncanonical-07/cancel-second
- `py-http-json` (python-sdk): `[ok] "07"=cancelled:error:-32800 7=result:t-int-7`
- `py-http-sse` (python-sdk): `[ok] "07"=cancelled:error:-32800 7=result:t-int-7`
- `py-stdio` (python-sdk): `[ok] "07"=cancelled:no-response 7=result:t-int-7`
- `ts-http-json` (typescript-sdk): `[ok] "07"=cancelled:no-response 7=result:t-int-7`
- `ts-http-sse` (typescript-sdk): `[ok] "07"=cancelled:no-response 7=result:t-int-7`
- `ts-stdio` (typescript-sdk): `[ok] "07"=cancelled:no-response 7=result:t-int-7`
- `ts2-http-json` (typescript-sdk-v2): `[ok] "07"=cancelled:no-response 7=result:t-int-7`
- `ts2-http-sse` (typescript-sdk-v2): `[ok] "07"=cancelled:no-response 7=result:t-int-7`
- `ts2-stdio` (typescript-sdk-v2): `[ok] "07"=cancelled:no-response 7=result:t-int-7`

## Rules

- **WIRE**: inbound message is valid JSON-RPC 2.0
- **R1**: response id matches an issued request id exactly (type and value)
- **R2**: at most one response per request
- **R3**: every non-cancelled request receives a response
- **R4**: response payload belongs to its own request
- **R5**: HTTP response delivered on its request's stream
- **R6**: cancelling one id never suppresses another id's response
- **R7**: session recovers and serves a fresh request
