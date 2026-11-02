# Phase 1 audit and gap analysis (2026-11-02)

## What existed

Nothing. The working directory `MCP Faultline/` was empty and not a Git
repository; `github.com/ashirimi1019/mcp-faultline` returned 404; no copy was
found elsewhere on the machine. The brief stated that a previous
implementation "reported 19 passing tests". **That claim could not be
verified**: no code, tests, CI configuration or history were available to run.
Everything in this repository was written from scratch on 2026-11-02, and no
earlier result is reused or quoted.

The reference project `ashirimi1019/knowledge-augmentation-lab` was used only
for conventions (src layout, strict pyright, ruff, hash-pinned CI, ADR-style
docs). No code was copied.

## Ecosystem facts that shaped the design (verified, not assumed)

| item | finding |
|---|---|
| Python SDK | `mcp` **2.3.0** (PyPI latest). Default revision `2026-07-28`; also serves `2025-11-25` via `initialize`. |
| TypeScript SDK v1 | `@modelcontextprotocol/sdk` **1.32.2** (npm latest of the v1 line). Latest revision `2025-11-25`. |
| TypeScript SDK v2 | `@modelcontextprotocol/server` **2.4.0**. Latest revision `2025-11-25`. |
| Common revision | **`2025-11-25`** is the newest revision all three serve, so every cross-SDK run uses it. |
| Python request-id handling | `mcp/shared/dispatcher.py::coerce_request_id` folds `"7"` to `7` *by design* ("matches the TS SDK") and is applied to `_pending`, `_in_flight` (server side) and progress routing. |
| TS request-id handling | Server side keys by the typed id (`Map`), client side correlates responses with `Number(response.id)`. v1 `_oncancel` drops `requestId: 0` (`if (!requestId)`); v2 checks `=== undefined`. |

## Prior art and overlap (checked 2026-11-02)

| upstream | status | relation to FL-001 |
|---|---|---|
| python-sdk#3786 | open | Streamable HTTP keys response streams by `str(request_id)`; `7`/`"7"` share a stream. **Known; FL-001 reproduces it, does not claim it.** |
| python-sdk#3432 | open | `coerce_request_id` folds non-canonical strings (`"07"`). **Known; reproduced by `noncanonical-07`.** |
| python-sdk#3060, #2655 | open | Client *reusing* one id. Different class (FL-001 never reuses ids). |
| typescript-sdk#2283 (fixed on v2 by #2654), #3043/#3044 | v1.x backport open | `notifications/cancelled` with `requestId: 0` ignored. **Known; FL-001 rediscovered it as an observation on v1.32.2 and confirms the v2 fix.** |
| conformance#450 | open PR | Cancellation scenarios; no typed-id twin coverage. |
| conformance#508 | open PR | Checks the *type* of an echoed id for one request; no concurrent twins. |

## Gaps this project fills

1. No existing tool drove the official SDKs with **concurrent typed-id twins**
   across stdio *and* Streamable HTTP and compared SDKs differentially.
2. Existing reports are hand-built reproductions. Nothing **minimises** a
   failing interaction or exports a dependency-free reproduction automatically.
3. No public harness demonstrates, with **negative controls**, that its
   oracle detects each defect class rather than merely observing successes.

## Known limitations (deliberately not hidden)

* The harness acts as the *client*; SDK **client-side** correlation (e.g.
  `Number(response.id)` in TS) is not yet exercised. See roadmap.
* HTTP ordering between concurrent POSTs relies on sequential sends plus a
  `ping` barrier; it is reliable in practice but is not a transport guarantee.
* The GET-stream sentinel variant of python-sdk#3786 (`"_GET_stream"`) is not
  yet a scenario.
