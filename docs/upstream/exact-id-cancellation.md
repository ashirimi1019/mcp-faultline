# Exact-id cancellation: compatibility audit

Scope: patch `0001` (python-sdk `JSONRPCDispatcher`) makes `notifications/cancelled` match the
request id exactly. Upstream `main` d7845c0 matches through `coerce_request_id`, which folds a
string of digits to an integer.

## What the specifications require

| source | text | strength |
|---|---|---|
| JSON-RPC 2.0 §4 | `id`: "An identifier established by the Client that MUST contain a String, Number, or NULL value" | `7` and `"7"` are different ids |
| JSON-RPC 2.0 §5 | the response id "MUST be the same as the value of the id member in the Request Object" | MUST (responses) |
| MCP 2025-11-25 cancellation | cancellations "MUST only reference requests that were previously issued in the same direction [and] are believed to still be in-progress" | MUST, **on the sender** |
| same | "Invalid cancellation notifications SHOULD be ignored: unknown request IDs, already completed requests" | SHOULD, on the receiver |
| same | "cancellation notifications may arrive after request processing has completed … Both parties MUST handle these race conditions gracefully" | MUST, on both |

A cancel whose id differs from the request's only in JSON type references an id that was never
issued. The receiver SHOULD ignore it. No text asks receivers to fold types. The current
tolerance is an **interoperability choice**, not a spec requirement.

## Why any fallback cancels the wrong request

The receiver sees only the cancel id and the set of requests still in flight. Take a cancel for
`"7"` while only integer `7` is in flight. Two histories produce exactly that input:

1. A peer issued `7` and sent its cancel as `"7"` (a non-conforming peer; the fallback is meant
   for this case).
2. A peer issued `"7"` and `7`; `"7"` completed; the peer's cancel for `"7"` was already in
   flight (the race the spec says MUST be handled gracefully).

A fallback that cancels `7` is correct in history 1 and cancels a live, uncancelled request in
history 2. An exact-only receiver ignores the cancel in both: in history 1 the request runs to
completion, which the spec permits (receivers MAY ignore cancellations), and in history 2 it is
correct. Restricting the fallback to "exactly one in-flight match" does not help, because history
2 has exactly one match.

Executable evidence:
- `test_late_cancel_for_a_completed_request_does_not_cancel_its_in_flight_twin` in patch `0001`
  passes with the patch and fails on `main` and with the rejected fallback
  (`docs/upstream/rejected/coercion-fallback-on-cancel.patch`).
- Linux CI run https://github.com/ashirimi1019/mcp-faultline/actions/runs/41533686584, job
  `python-sdk rejected-fallback`: all 72 fixed FL-001 scenarios pass, yet 12 of 150 randomised
  scenarios fail (4 per transport, every one R6). The fallback also fails exactly three upstream
  tests: the late-cancel race and the two type-changed-cancel cases. Locally, seeds 6 and 14
  reproduce it: a late cancel for `"X"` lands on a running `X`.

## Backward compatibility

| who | before | after | evidence |
|---|---|---|---|
| Python SDK peers | cancels use the request id object unchanged (`_cancel_outbound` sends `requestId: request_id`) | unaffected | `src/mcp/shared/jsonrpc_dispatcher.py` `_cancel_outbound` |
| TypeScript SDK peers (v1, v2) | cancels send `requestId: messageId`, the same number as the request | unaffected | TS `Protocol.request` |
| a peer that changes the id's type between request and cancel | cancel honoured | cancel ignored; the request runs to completion and is answered | inverted upstream test, now `test_cancelled_with_the_other_typed_form_of_an_id_does_not_cancel_it` |
| a peer that cancels `"07"` / `"+7"` for `7` (python-sdk#3432 forms) | cancel honoured, and can hit the wrong twin | ignored | `test_cancel_id_matching_two_in_flight_requests_only_by_coercion_cancels_neither` |

The only observable regression affects peers that violate the sender-side MUST, and its effect
is that work isn't cancelled, which is never a correctness error. Response correlation
(`_pending`) and progress routing still use `coerce_request_id` and are untouched. That client-side
leniency for peers that echo `"7"` for request `7` is out of scope.

## HTTP patch (0002) compatibility

- Integer request ids keep their stream key text, so stored event-stream ids are unchanged.
- String request ids gain an `s:` prefix. Events stored by an older version for a string-id
  request won't replay after an upgrade. Only resumption across an upgrade is affected.
- `close_sse_stream(7)` now closes integer request 7's stream; before, it found nothing.
  `close_sse_stream("7")` no longer closes integer request 7's stream.

## Should the commits stay separate?

Yes, as two PRs:

- They fix independent root causes in different modules: the dispatcher, used by every transport,
  and the Streamable HTTP transport.
- Each passes the suite on its own: patch `0001` alone passes `tests/shared` + `tests/server`.
- They map to different issues: #3786 for HTTP, and a new issue for the dispatcher.
- Only `0001` needs a behaviour decision. `0002` can merge without waiting for it.
- Open maintainer PR #3192 rewrites the HTTP transport and would supersede `0002`, but keeps
  `coerce_request_id` for in-flight correlation, so `0001` still applies.

## Edge cases and what covers them

| case | covered by |
|---|---|
| twins in flight, either order, either cancelled | `test_cancel_with_int_and_string_twins_in_flight_reaches_only_the_exact_id` (4) |
| cancel id coercing to two in-flight ids (`"+7"`) | `test_cancel_id_matching_two_in_flight_requests_only_by_coercion_cancels_neither` |
| late cancel racing completion | `test_late_cancel_...` |
| same-type id reuse (identity guard on completion) | existing `test_completed_handler_does_not_evict_reused_request_id_from_in_flight` |
| `bool` ids | existing `as_request_id` rejects `bool` |
| HTTP twins answered out of order (JSON and SSE) | `test_int_and_string_twin_ids_each_get_their_own_response` |
| string id spelling the GET sentinel | `test_stream_keys_are_injective_and_never_the_get_stream_sentinel` (unit level) |
| end to end, 150 random interleavings × 3 transports | FL-001 random matrix |

Not covered by an end-to-end test, only at unit level:

- a POST whose id is literally `"_GET_stream"` while a standalone GET stream is open;
- resuming (`Last-Event-ID`) a string-id request's stream.

Existing resumption tests pass with the new keys. Progress-token routing for typed twins
(`_pending`) is unchanged and untested for twins; that is client-side and outside this change.
