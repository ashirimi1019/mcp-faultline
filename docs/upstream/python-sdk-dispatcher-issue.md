<!-- DRAFT for owner approval. Not posted.
Target: https://github.com/modelcontextprotocol/python-sdk/issues/new (bug report form).
Before posting: (1) merge mcp-faultline PR #2 so the links below resolve; (2) re-check that no issue or PR
has appeared for this; (3) post this BEFORE the #3786 comment, which links it. -->

**Title:** `notifications/cancelled` for request `7` cancels a concurrent request `"7"` (`_in_flight` keyed by `coerce_request_id`)

### Initial checks

- Reproduced on 2.3.0 and on `main` d7845c0.
- Related, but a different code path:
  - #3786 is the Streamable HTTP stream keys (`str(id)`). This bug also reproduces over stdio.
  - #3432 is about which strings `coerce_request_id` folds (`"07"`, `"+7"`). This bug occurs with the canonical `"7"` the function folds by design.
  - #3060 and #2655 cover a client *reusing* one id. Here the ids differ.

### What happens

`JSONRPCDispatcher` stores inbound requests as `_in_flight[coerce_request_id(req.id)]`. With `7` and `"7"` in flight at once, they share a slot. A `notifications/cancelled` naming the earlier one cancels the later one, which then never answers, while the earlier one runs to completion and can no longer be cancelled.

### Reproduction (stdio, unmodified SDK)

A server whose tool blocks until released, receiving these frames in order:

```
{"jsonrpc":"2.0","id":"9007199254740991","method":"tools/call","params":{"name":"gate","arguments":{"tag":"g0"}}}
{"jsonrpc":"2.0","id":9007199254740991,"method":"tools/call","params":{"name":"gate","arguments":{"tag":"g3"}}}
{"jsonrpc":"2.0","method":"notifications/cancelled","params":{"requestId":"9007199254740991"}}
```

After both tools are released, `"9007199254740991"` (the one cancelled) answers and `9007199254740991` gets no response. A stdlib-only script that sends these frames to any stdio server command, and exits 1 on the defect: https://github.com/ashirimi1019/mcp-faultline/blob/main/evidence/fl001/minimized/repro_py_stdio_random_seed_6_min.py

### Expected

Cancelling one id never affects another. The TypeScript SDK servers (1.32.2 and 2.4.0) key handlers by the typed id and pass the same scenarios.

### Decision needed

Should `notifications/cancelled` match the request id **exactly**?

Fixing the slot (exact-id keys) is straightforward. But `test_cancelled_correlates_across_string_and_int_request_id_forms` pins a tolerance where a cancel for `"7"` cancels an in-flight `7`. That tolerance can't be kept safely: a late cancel for a just-completed `"7"` (a race the spec requires handling gracefully) is indistinguishable from a stringified cancel for `7`. Any fallback, even one that requires a single match, cancels the wrong request in that race. The spec says cancels for unknown or completed ids SHOULD be ignored, and both SDKs' own senders keep the id's type. The analysis is in https://github.com/ashirimi1019/mcp-faultline/blob/main/docs/upstream/exact-id-cancellation.md.

### Patch

A candidate change (8 lines in `jsonrpc_dispatcher.py`, plus regression tests including the late-cancel race) is ready if exact matching is acceptable: https://github.com/ashirimi1019/mcp-faultline/blob/main/docs/upstream/patches/0001-Cancel-only-the-exact-JSON-RPC-request-id.patch

Validated on Ubuntu from source (`https://github.com/ashirimi1019/mcp-faultline/actions/runs/41533686584`):
- upstream `scripts/test` passes with 100% coverage and strict-no-cover;
- `ruff` and `pyright` are clean;
- typed-id scenarios go from 19/24 to 24/24 over stdio;
- 150 randomised scenarios pass across stdio and HTTP. The HTTP part also needs the #3786 change.

I'd open a PR only if assigned.

<sub>AI disclosure: the defect was found by an automated harness, and this report, the patch and its tests were drafted with AI assistance (Claude Code). Results come from the linked CI run.</sub>
