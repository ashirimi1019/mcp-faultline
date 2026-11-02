<!-- DRAFT for owner approval. Not posted.
Target: https://github.com/modelcontextprotocol/python-sdk/issues/3786
Before posting: (1) merge mcp-faultline PR #2 so links resolve; (2) post the dispatcher issue first and replace
#<DISPATCHER ISSUE>; (3) confirm @riszhkejksnd (claimed on 2026-10-31) has not opened a PR; if they have,
cut this down to the cancellation note and the test, addressed to their PR. -->

Two verified data points for whoever picks this up. @riszhkejksnd, these are offered for your PR, not to take it over.

**1. Fixing the stream keys doesn't fix the cancellation symptom.** On `main` d7845c0, after the three `str()` sites are fixed, cancelling the earlier of `7`/`"7"` over HTTP still hits the other request. The cause is the dispatcher, which folds ids into one `_in_flight` slot on every transport (stdio too). That's filed separately as #<DISPATCHER ISSUE> because it needs its own decision. #3432 is related only in that both go through `coerce_request_id`.

**2. A transport change that passes the full suite.** One helper, used at the three sites:

```python
def _stream_key(request_id: RequestId) -> str:
    return str(request_id) if isinstance(request_id, int) else f"s:{request_id}"
```

- Integer keys are unchanged, so stored event-stream ids for integer requests don't move.
- No string id can equal `GET_STREAM_KEY`.
- The public `close_sse_stream(request_id)` derives the key from the id it receives, and internal callers close by key. That keeps the raw-id contract described in the issue.
- One tradeoff: events stored for *string*-id requests before an upgrade won't replay afterwards, because their keys change.

The regression test sends two concurrent POSTs with ids `7` and `"7"` and answers them in reverse order. Each POST must receive exactly its own typed response. It fails on `main` (one POST never completes) in both JSON and SSE modes.

Patch: https://github.com/ashirimi1019/mcp-faultline/blob/main/docs/upstream/patches/0002-Key-Streamable-HTTP-response-streams-by-the-typed-re.patch

Validated on Ubuntu from source, together with the dispatcher change (`https://github.com/ashirimi1019/mcp-faultline/actions/runs/41533686584`):
- upstream `scripts/test` passes with 100% coverage and strict-no-cover;
- typed-id scenarios go from 11/24 to 24/24 over both SSE and JSON;
- 150 randomised scenarios pass.

#3192 would replace these sites. It keeps `coerce_request_id` for in-flight correlation, so the dispatcher issue would remain.

<sub>AI disclosure: found by an automated harness; this comment, the patch and its tests were drafted with AI assistance (Claude Code). Results come from the linked CI run.</sub>
