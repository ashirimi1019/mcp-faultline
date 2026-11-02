# Upstream contribution candidates

Nothing in this directory has been posted. Each draft needs owner approval and
a final re-check for overlap on the day it is posted.

| # | target | type | status | readiness |
|---|---|---|---|---|
| 1 | python-sdk, **new issue** | bug: dispatcher `_in_flight` keyed by `coerce_request_id` cross-cancels `7`/`"7"` on every transport | draft: [python-sdk-dispatcher-issue.md](python-sdk-dispatcher-issue.md) | **Ready for owner review.** No existing issue covers it (checked #3786, #3432, #3060, #2655, open PRs). Needs a maintainer decision: the fix removes a tested tolerance for type-changed cancel ids. |
| 2 | [python-sdk#3786](https://github.com/modelcontextprotocol/python-sdk/issues/3786) | comment: the stream-key fix alone is insufficient; minimal transport patch and test | draft: [python-sdk-3786-comment.md](python-sdk-3786-comment.md) | **Ready for owner review.** Post after #1 so it can link it. A volunteer claimed #3786 on 2026-10-31, so the draft offers the work rather than taking it. |
| 3 | python-sdk PRs (patch 0001 → #1, patch 0002 → #3786) | fix + regression tests | [patches/](patches/), descriptions: [python-sdk-prs.md](python-sdk-prs.md) | **Blocked by repo policy until a maintainer assigns the issue or labels it `help wanted`.** Patches apply cleanly to `main` d7845c0 and are validated (see `evidence/fl001-fix/`). |
| 4 | [modelcontextprotocol/conformance](https://github.com/modelcontextprotocol/conformance) | issue proposing a typed-id isolation scenario | draft: [conformance-issue.md](conformance-issue.md) | Ready for owner review (CONTRIBUTING: issue first). |
| 5 | typescript-sdk v1.x `requestId: 0`; python-sdk#3432 | - | already tracked upstream | No action. Patch 0001 also stops `"07"` from cancelling `7` (exact-id cancel). #3432's response-correlation half (`_pending`) is untouched. |
| - | langchain-ai/langgraph, UKGovernmentBEIS/inspect_ai | - | searched 2026-11-02 | No FL-001-related defect found. |

Nothing here has been posted. The drafts claim only results from the Linux CI run they link
(`.github/workflows/upstream-fix-validation.yml`), and none of them says the owner re-ran anything. Compatibility
analysis: [exact-id-cancellation.md](exact-id-cancellation.md). Posting order: merge mcp-faultline PR #2 (so links
resolve), then the dispatcher issue, then the #3786 comment, and PRs only after assignment.

## Checklist applied before any post

1. Issue still open and the defect still reproduces on the latest release.
2. No overlapping PR (search by file name, function name and issue number).
3. Independent reproduction attached (stdlib script from `evidence/`).
4. Focused fix tested (`scripts/fix_validation.py` + full FL-001 matrix).
5. The repository's CONTRIBUTING.md / AGENTS.md re-read (python-sdk:
   assignment-gated PRs; conformance: issue first, prove pass and fail).
6. AI-assistance disclosure where the repository asks for it.
