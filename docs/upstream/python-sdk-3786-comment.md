<!-- DRAFT: not posted. Target: https://github.com/modelcontextprotocol/python-sdk/issues/3786 -->

One more layer for whoever picks up the fix: fixing the Streamable HTTP stream keys alone doesn't fix the cancellation half, because `JSONRPCDispatcher` independently merges the twins on **every** transport, stdio included.

**Where.** `src/mcp/shared/jsonrpc_dispatcher.py` (v2.3.0) registers inbound requests as `self._in_flight[coerce_request_id(req.id)]` (~:608). `notifications/cancelled` looks them up with `coerce_request_id(rid)` (~:642). With `7` and `"7"` both in flight, the second registration overwrites the first, so:

- `notifications/cancelled {requestId: <earlier twin>}` cancels the **later** twin, and
- the earlier twin can no longer be cancelled at all.

**Minimal repro (stdio, unmodified 2.3.0, protocol 2025-11-25).** Automatically minimised from a 16-step randomised scenario to 3 steps, and stable over 3 confirmation runs:

```
-> {"jsonrpc":"2.0","id":"9007199254740991","method":"tools/call","params":{"name":"gate","arguments":{"tag":"g0"}}}
-> {"jsonrpc":"2.0","id":9007199254740991,"method":"tools/call","params":{"name":"gate","arguments":{"tag":"g3"}}}
-> {"jsonrpc":"2.0","method":"notifications/cancelled","params":{"requestId":"9007199254740991"}}
   (both gates then released)
<- {"jsonrpc":"2.0","id":"9007199254740991","result":{... "g0" ...}}   # the cancelled request completes
   ...and integer 9007199254740991 never gets a response
```

`gate(tag)` is a tool that blocks until a `release(tag)` call, so completion order is deterministic. A stdlib-only script that replays the exact frames against any stdio server command: <link to evidence/fl001/repro_py_stdio_random_seed_6_min.py>.

**Matrix.** 8 id pairs × {out-of-order, cancel-first, cancel-second}. The collision pairs are `7`/`"7"`, `"7"`/`7`, `0`/`"0"` and `-1`/`"-1"`; `7`/`"07"` is the #3432 case; the controls are `7`/`8`, `"a7"`/`"b7"` and `7`/`"x7"`. Results on patched **copies** of 2.3.0:

| patch | stdio (24) | HTTP SSE (24) |
|---|---|---|
| none | 19 pass | 11 pass |
| stream keys only (`str(id)` → injective key at the three sites in the issue) | 19 pass | 19 pass |
| dispatcher only (exact-typed `_in_flight`; cancel lookup tries the exact id, then the other-typed twin) | 24 pass | 12 pass |
| both | 24 pass | 24 pass (JSON response mode too) |

All 9 control scenarios pass in every row. The 5 remaining failures with stream keys only are exactly the `cancel-first` cases: four collision pairs plus `"07"` (#3432). On HTTP they show up as the never-cancelled twin receiving `{"code":-32800,"message":"Request cancelled"}`. On stdio its response is simply never sent.

**On TS parity.** The `coerce_request_id` docstring says it matches the TS SDK. That holds for the TS *client's* response correlation (`Number(response.id)`). The TS *server* keys in-flight handlers by the typed id. typescript-sdk 1.32.2 and v2 2.4.0 pass all 24 scenarios on stdio and both HTTP modes. So exact-typed `_in_flight` keys with a twin fallback keep the leniency for peers that stringify ids, and remove the cross-cancellation.

Happy to share the dispatcher diff and regression tests if useful, but I won't open a PR unless a maintainer wants one, given the assignment policy. The harness is MCP Faultline (<repo link>), and the experiment write-up is at <link to docs/fl-001.md>.

<sub>Disclosure: found and minimised with an automated harness developed with AI assistance; the reproduction and every number above were re-run and checked by hand.</sub>
