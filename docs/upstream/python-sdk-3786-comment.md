<!-- DRAFT: not posted. Target: https://github.com/modelcontextprotocol/python-sdk/issues/3786. Before posting: confirm no PR has appeared from the volunteer (riszhkejksnd, 2026-10-31) and link the dispatcher issue once filed. -->

Two data points for whoever takes this. @riszhkejksnd, happy to hand these over if you're on it.

**1. The stream-key fix alone doesn't fix the cancellation symptom.** Over HTTP, cancelling the earlier of `7`/`"7"` still lands on the wrong request after the three `str()` sites are fixed. The dispatcher folds the ids too (`_in_flight[coerce_request_id(id)]`), on every transport. I filed that separately as #<dispatcher issue> since it needs its own decision.

**2. A minimal shape for the transport half that passes the full suite.** One helper at the three sites:

```python
def _stream_key(request_id: RequestId) -> str:
    return str(request_id) if isinstance(request_id, int) else f"s:{request_id}"
```

Integer keys are unchanged, so stored event-stream ids for integer requests stay the same. String keys can never equal `GET_STREAM_KEY`. The public `close_sse_stream(request_id)` derives the key from the id it's given, and internal callers (the per-request callback, `close_standalone_sse_stream`) close by key. That keeps the raw-id contract the issue mentions.

Regression test: two concurrent POSTs with ids `7` and `"7"`, answered in reverse order, each must receive exactly its own typed response (JSON and SSE modes). It times out on `main` and passes with the change.

Measured on `main` d7845c0 with both changes (stdio, SSE, JSON): 24/24 typed-id scenarios each, versus 19/11/11 unmodified, and 50/50 randomised scenarios per transport. Details and traces: https://github.com/ashirimi1019/mcp-faultline/blob/main/docs/fl-001.md

Note that #3192 (open) rebuilds this transport and would remove these sites. It keeps `coerce_request_id` for in-flight correlation, so the dispatcher issue would survive it.

<sub>Found with an automated harness developed with AI assistance; reproduction and patch reviewed and re-run by me.</sub>
