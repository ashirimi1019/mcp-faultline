# Upstream contributions

Items 1 and 2 were posted by the owner's account on 2026-11-02 with explicit approval; everything else is
still a draft. Each draft needs owner approval and a final re-check for overlap on the day it is posted.
No maintainer has responded yet, and nothing here has been accepted.

| # | target | type | status | ownership / blockers |
|---|---|---|---|---|
| 1 | [python-sdk#3807](https://github.com/modelcontextprotocol/python-sdk/issues/3807) | bug: dispatcher `_in_flight` keyed by `coerce_request_id` cross-cancels `7`/`"7"` on every transport | **posted 2026-11-02**, open, unassigned, awaiting triage. Source: [python-sdk-dispatcher-issue.md](python-sdk-dispatcher-issue.md) | Opened by ashirimi1019. Pending maintainer decision: exact-id cancellation vs the tested cross-type tolerance. |
| 2 | [python-sdk#3786 comment](https://github.com/modelcontextprotocol/python-sdk/issues/3786#issuecomment-6590624510) | the stream-key fix alone is insufficient; minimal transport patch and test | **posted 2026-11-02**. Source: [python-sdk-3786-comment.md](python-sdk-3786-comment.md) | #3786 is unassigned; riszhkejksnd volunteered on 2026-10-31 (no PR as of posting). The comment offers the patch to them; we do not take the issue. |
| 3 | python-sdk PRs (patch 0001 → #3807, patch 0002 → #3786) | fix + regression tests | not opened. [patches/](patches/), descriptions: [python-sdk-prs.md](python-sdk-prs.md) | **Blocked by repo policy until a maintainer assigns the issue to ashirimi1019 or labels it `help wanted`.** The two patches stay independent PRs. Both apply cleanly to `main` d7845c0 (re-checked 2026-11-02) and are validated (see `evidence/fl001-fix/`). |
| 4 | [modelcontextprotocol/conformance](https://github.com/modelcontextprotocol/conformance) | issue proposing a typed-id isolation scenario | draft: [conformance-issue.md](conformance-issue.md) | Ready for owner review (CONTRIBUTING: issue first). |
| 5 | typescript-sdk v1.x `requestId: 0`; python-sdk#3432 | - | already tracked upstream | No action. Patch 0001 also stops `"07"` from cancelling `7` (exact-id cancel). #3432's response-correlation half (`_pending`) is untouched. |
| - | langchain-ai/langgraph, UKGovernmentBEIS/inspect_ai | - | searched 2026-11-02 | No FL-001-related defect found. |

Items 1 and 2 claim only results from the Linux CI run they link
(`.github/workflows/upstream-fix-validation.yml`), and none of them says the owner re-ran anything. Compatibility
analysis: [exact-id-cancellation.md](exact-id-cancellation.md). Posting order followed: mcp-faultline PR #2 merged
(https://github.com/ashirimi1019/mcp-faultline/pull/2), then #3807, then the #3786 comment; PRs only after assignment.

## Checklist applied before any post

1. Issue still open and the defect still reproduces on the latest release.
2. No overlapping PR (search by file name, function name and issue number).
3. Independent reproduction attached (stdlib script from `evidence/`).
4. Focused fix tested (`scripts/fix_validation.py` + full FL-001 matrix).
5. The repository's CONTRIBUTING.md / AGENTS.md re-read (python-sdk:
   assignment-gated PRs; conformance: issue first, prove pass and fail).
6. AI-assistance disclosure where the repository asks for it.
