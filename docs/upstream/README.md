# Upstream contribution candidates

Nothing in this directory has been posted. Each draft needs owner approval and
a final re-check for overlap on the day it is posted.

| # | target | type | status | readiness |
|---|---|---|---|---|
| 1 | [python-sdk#3786](https://github.com/modelcontextprotocol/python-sdk/issues/3786) | issue comment: the HTTP-only fix is insufficient; the dispatcher `_in_flight` coercion cross-cancels on every transport | draft: [python-sdk-3786-comment.md](python-sdk-3786-comment.md) | **Ready for review.** Reproduced on unmodified 2.3.0, minimised, fix validated on patched copies. Re-check that the volunteer's PR has not already covered the dispatcher. |
| 2 | python-sdk, new issue *only if* maintainers prefer it separate from #3786 | bug: canonical twin cross-cancellation via `coerce_request_id` in `_in_flight` | covered by draft 1 | Hold. The repo auto-closes PRs from contributors not assigned to the linked issue, so the right path is discussion on the issue first, then a PR once assigned. |
| 3 | [modelcontextprotocol/conformance](https://github.com/modelcontextprotocol/conformance) | issue proposing a server scenario `request-id-type-isolation` (concurrent `7`/`"7"`, out-of-order, cancel one twin) | draft: [conformance-issue.md](conformance-issue.md) | **Ready for review.** CONTRIBUTING requires an issue first. Depends on a blocking tool in the everything-server. #450 (open) adds `test_tool_slow`; coordinate rather than duplicate. |
| 4 | typescript-sdk v1.x | `requestId: 0` cancel ignored | already tracked: #2283 (fixed in v2 by #2654), backport #3043 / PR #3044 | **No action.** At most a +1 with FL-001 evidence on #3044 if maintainers ask for verification. |
| 5 | python-sdk#3432 | non-canonical `"07"` folding | already tracked, fix ready on a fork, author awaiting assignment | **No action.** FL-001 `noncanonical-07` reproduces it, and the *dispatcher* fix in draft 1 also resolves it. Mention in draft 1, don't open anything new. |
| - | langchain-ai/langgraph, UKGovernmentBEIS/inspect_ai | - | searched open MCP issues on 2026-11-02 | No FL-001-related defect found. LangGraph #8952 concerns MCP tool annotations in the hosted API, which needs a different experiment. |

## Checklist applied before any post

1. Issue still open and the defect still reproduces on the latest release.
2. No overlapping PR (search by file name, function name and issue number).
3. Independent reproduction attached (stdlib script from `evidence/`).
4. Focused fix tested (`scripts/fix_validation.py` + full FL-001 matrix).
5. The repository's CONTRIBUTING.md / AGENTS.md re-read (python-sdk:
   assignment-gated PRs; conformance: issue first, prove pass and fail).
6. AI-assistance disclosure where the repository asks for it.
