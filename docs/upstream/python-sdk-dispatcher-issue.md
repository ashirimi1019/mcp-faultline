<!-- DRAFT: not posted. Target: https://github.com/modelcontextprotocol/python-sdk/issues/new (bug). Re-check for duplicates on the day of posting. -->

**Title:** Cancelling request `7` cancels a concurrent request `"7"` instead (dispatcher `_in_flight` keyed by `coerce_request_id`), on every transport

### Initial checks

- [x] Newest release of my line (2.3.0), and reproduced on `main` d7845c0.
- [x] Searched existing issues. Related but different: #3786 (Streamable HTTP `str(id)` stream keys), #3432 (non-canonical folds such as `"07"`), #3060/#2655 (a client *reusing* one id).

### What happens

`JSONRPCDispatcher` registers inbound requests as `self._in_flight[coerce_request_id(req.id)]`, so the two distinct JSON-RPC ids `7` and `"7"` share one slot. With both in flight, `notifications/cancelled {requestId: <earlier one>}` cancels the **later** one. The earlier one keeps running and can no longer be cancelled. This happens over stdio too, so it is independent of #3786.

### Reproduction (stdio, unmodified SDK)

A server with one tool that blocks until released. Frames in order:

```
-> {"jsonrpc":"2.0","id":"9007199254740991","method":"tools/call","params":{"name":"gate","arguments":{"tag":"g0"}}}
-> {"jsonrpc":"2.0","id":9007199254740991,"method":"tools/call","params":{"name":"gate","arguments":{"tag":"g3"}}}
-> {"jsonrpc":"2.0","method":"notifications/cancelled","params":{"requestId":"9007199254740991"}}
   (release both tools)
<- {"jsonrpc":"2.0","id":"9007199254740991","result":{...}}   # the cancelled request answers
   integer 9007199254740991 never gets a response
```

Stdlib-only script: https://github.com/ashirimi1019/mcp-faultline/blob/main/evidence/fl001/minimized/repro_py_stdio_random_seed_6_min.py (exits 1 on 2.3.0).

### Expected

A cancel names exactly one id; `7` and `"7"` are different ids (JSON-RPC 2.0 §5; MCP: "string or integer ID"). The TypeScript SDK server (1.32.2 and 2.4.0) keys handlers by the typed id and behaves this way.

### The decision this needs

Fixing the slot (exact-id keys) is uncontroversial. The cancel lookup is not: `test_cancelled_correlates_across_string_and_int_request_id_forms` pins a tolerance where a cancel for `"7"` cancels an in-flight `7`. I tried keeping that tolerance only when exactly one in-flight request matches. It still cancels the wrong request when a cancel for `"7"` arrives just after `"7"` completed, while `7` is running. That race is allowed by the spec, and the receiver can't tell it apart from a peer that stringified `7`. So the fix I'd propose matches exact ids only and drops the tolerance. Is that acceptable?

I have a patch with regression tests (full suite green and 100% coverage locally) and would be glad to open a PR if assigned.

<sub>Found with an automated harness (MCP Faultline) developed with AI assistance; I have reviewed and re-run the reproduction and the patch.</sub>
