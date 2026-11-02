<!-- DRAFTS: not opened. python-sdk closes outside PRs unless the linked issue is assigned to the author
     or labelled `help wanted`. Open each only after that, from a fork branch carrying the matching commit
     of docs/upstream/patches/. -->

# PR 1: dispatcher (patch 0001)

**Title:** Cancel only the exact JSON-RPC request id

Fixes #<dispatcher issue>

## Motivation and Context

`JSONRPCDispatcher` keyed `_in_flight` by `coerce_request_id(id)`, so concurrent requests `7` and `"7"` shared one slot. A `notifications/cancelled` for the earlier one cancelled the later one, and the earlier one could not be cancelled. This affects every transport.

## Changes

- `_in_flight` is keyed by the exact wire id; the completion path drops the exact key (the identity guard is unchanged).
- `notifications/cancelled` resolves by exact id only.

**Behaviour change (needs maintainer sign-off):** a cancel whose id differs from the request's only in JSON type (`"7"` for `7`) no longer cancels it. `test_cancelled_correlates_across_string_and_int_request_id_forms` pinned the old tolerance and now asserts the exact-id behaviour (renamed `test_cancelled_with_the_other_typed_form_of_an_id_does_not_cancel_it`). A narrower tolerance (fall back only when exactly one in-flight request matches) was tried and rejected. When a cancel for `"7"` arrives just after `"7"` completed, it cancels a still-running `7`, and the receiver cannot tell that case from a stringified id. `test_late_cancel_for_a_completed_request_does_not_cancel_its_in_flight_twin` pins this. Client-side response correlation (`_pending`) is untouched.

## How Has This Been Tested?

- New tests in `tests/shared/test_jsonrpc_dispatcher.py`: twins in flight × which is cancelled (4), a cancel id that coerces to both twins (`"+7"`), the late-cancel race, and the inverted tolerance test (2). Six of the eight fail on `main`. The two that pass there are the cancel-the-later-twin cases, which pass only by last-writer-wins.
- On Ubuntu 24.04 (Python 3.12.15, uv 0.12.7), built from source at `main` d7845c0 (https://github.com/ashirimi1019/mcp-faultline/actions/runs/41533686584): `scripts/test` passes with 6236 tests, 100% coverage and `strict-no-cover` (unpatched: 6226). `ruff check`, `ruff format --check` and `pyright` report no findings.
- Stands alone: with only this commit applied, `tests/shared` + `tests/server` pass (2390, Windows).
- End to end with the stdio, SSE and JSON servers, on the same Linux build: typed-id scenarios 19/11/11 → 24/24/24 of 24, randomised 52 → 150 of 150. Evidence: https://github.com/ashirimi1019/mcp-faultline/tree/main/evidence/fl001-fix

## Types of changes

- [x] Bug fix (non-breaking change which fixes an issue). The tolerance removal is called out above.

AI disclosure: the change and its tests were drafted with AI assistance (Claude Code). <!-- OWNER: before opening, add a sentence in your own words confirming you reviewed the diff and can explain it; CONTRIBUTING requires that the author owns the change. -->

---

# PR 2: Streamable HTTP (patch 0002)

**Title:** Key Streamable HTTP response streams by the typed request id

Fixes #3786

## Motivation and Context

The legacy transport keyed each POST's stream by `str(request_id)`, so `7` and `"7"` shared one stream: one POST received the other's response and the other never completed. A string id `"_GET_stream"` could also collide with the standalone GET stream's key.

## Changes

- `_stream_key()` at the three conversion sites: integers keep their text (stored event-stream ids are unchanged), and strings are prefixed `s:`, so no string id can equal `GET_STREAM_KEY`.
- `close_sse_stream(request_id)` derives the key from the request id it is given. Internal callers close by key via `_close_stream()`.
- `_create_session_message`'s `request_id` parameter is annotated `str`: it already received the derived key.

**Observable changes:** `close_sse_stream(7)` now closes integer request 7's stream (before, it looked up the int key against string keys and found nothing), and `close_sse_stream("7")` no longer closes integer request 7's stream. Stored event-stream ids for **string** request ids gain the `s:` prefix, so events stored by a previous version for string ids won't replay after an upgrade.

## How Has This Been Tested?

- `tests/server/test_streamable_http_router.py`: twin ids answered in reverse order (JSON and SSE; both time out on `main`), `_stream_key` injectivity including the GET sentinel, and `close_sse_stream` exact-id closing. `test_router_unconsumed_request_stream_does_not_block_siblings` registers its streams under `_stream_key(...)` because it writes the private table directly.
- Overlap: #3192 (open) rebuilds this transport and would subsume this change; this is the minimal fix for the current transport.

AI disclosure: the change and its tests were drafted with AI assistance (Claude Code). <!-- OWNER: before opening, add a sentence in your own words confirming you reviewed the diff and can explain it; CONTRIBUTING requires that the author owns the change. -->
