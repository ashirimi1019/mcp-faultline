<!-- DRAFT: not posted. Target: https://github.com/modelcontextprotocol/conformance/issues/new -->

**Title:** Proposal: server scenario for typed request-id isolation (`7` vs `"7"`) under concurrency and cancellation

**Spec requirement.** Base protocol (2025-11-25): requests "MUST include a string or integer ID". JSON-RPC 2.0 §5: the response id "MUST be the same as the value of the id member in the Request Object". Cancellation (2025-11-25): `notifications/cancelled` references "the ID of the request to cancel". Taken together, `7` and `"7"` are distinct requests: each must get its own response, and cancelling one must not affect the other.

**Gap.** #508 checks the type of an echoed id for a single request, and #450 covers cancellation of one request. Nothing exercises **two concurrent requests whose ids differ only in JSON type**, which is where implementations that key internal tables by `str(id)` or fold `"7"` to `7` fail.

**Evidence that it catches real defects.** Run against official SDKs at 2025-11-25 over Streamable HTTP:

| SDK | result |
|---|---|
| python-sdk 2.3.0 | fails (lost or misrouted responses: python-sdk#3786; cross-cancellation via dispatcher id coercion) |
| typescript-sdk 1.32.2, v2 2.4.0 | pass |

**Proposed shape** (one scenario, several checks, per AGENTS.md):

- `request-id-type-isolation`: issue `7` and `"7"` concurrently to a blocking tool, release them in reverse order, then
  1. each response id equals its request id, type included (MUST);
  2. exactly one response per id (MUST);
  3. each response carries its own request's payload;
  4. issue a fresh twin pair and cancel one twin: the other still completes successfully (no `-32800`).
- Failing fixture: a server variant whose response routing is keyed by `str(id)`.

**Dependency.** Needs a tool that blocks until released (or a slow tool). #450 adds `test_tool_slow` to the everything-server. I'd build on that rather than add another tool.

I have a working out-of-tree implementation (MCP Faultline, <repo link>) with negative controls, and I'm happy to port it as a scenario if this direction is welcome.
