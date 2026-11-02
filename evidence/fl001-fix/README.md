# FL-001 fix validation: python-sdk typed request ids

Upstream base: `modelcontextprotocol/python-sdk` `main` at
`d7845c073a2b9ba5ab2817ecf93d3e45ef24cd14` (after v2.3.0). Both builds report
`mcp 2.3.1.dev17+d7845c0`. The only difference is the patch series in
[`docs/upstream/patches/`](../../docs/upstream/patches/).

| directory | SDK build | runs | result |
|---|---|---|---|
| `main-unpatched/` | base commit | FL-001, 24 scenarios × stdio / HTTP SSE / HTTP JSON | 19/24, 11/24, 11/24 |
| `main-patched/` | base + patches | same | **24/24, 24/24, 24/24** |
| `random50-main-unpatched/` | base commit | seeds 1-50 × 3 transports | 42/50, 5/50, 5/50 |
| `random50-main-patched/` | base + patches | same | **50/50, 50/50, 50/50** |

Traces of passing random runs were pruned to keep the repository small (the
`trace` field is `null` for them). Every run regenerates with:

```sh
python scripts/fix_validation.py /tmp/fv patched      # or: unpatched
FAULTLINE_TARGET_PYTHON=<printed path> faultline run -t py-stdio -t py-http-sse -t py-http-json -o <dir>
FAULTLINE_TARGET_PYTHON=<printed path> faultline run -t py-stdio -t py-http-sse -t py-http-json -s none \
    $(for i in $(seq 1 50); do printf -- '--random-seed %s ' $i; done) -o <dir>
```

Remaining observation on the patched build: over HTTP, a cancelled request is
answered with `-32800` (`cancel-answered`, a SHOULD NOT). This is pre-existing
and deliberate: the transport uses it to complete the POST
(`_terminate_unanswered_request`). It is unrelated to id typing and is not a
violation.

## A rejected design, kept for the record

The first candidate fix keyed `_in_flight` by the exact id but still resolved a
cancel to the *single* in-flight request it coerced to, to keep upstream's
tested tolerance for peers that stringify ids. It passed all 24 fixed
scenarios. The random sweep (seeds 1-20, stdio and HTTP SSE) then failed 4/40,
on seeds 6 and 14. In both, a cancel for `"X"` arrived after `"X"` had already
completed, and the fallback cancelled the still-running integer `X`. A
receiver cannot tell "peer stringified X" from "late cancel for the real
`"X"`", so any coercion fallback is ambiguous. The submitted patch matches
exact ids only.

## Linux re-verification

CI run https://github.com/ashirimi1019/mcp-faultline/actions/runs/41533686584 rebuilt all three variants
from source on Ubuntu 24.04 (Python 3.12.15, uv 0.12.7). Upstream `main` was still at
d7845c0, and the patches apply to it.

| variant | upstream `scripts/test` | ruff / pyright | FL-001 fixed | random 150 | repro |
|---|---|---|---|---|---|
| unpatched | 6226 passed, 100% | clean | 41/72 | 52/150 | exit 1 |
| patched | **6236 passed, 100%, strict-no-cover** | clean | **72/72** | **150/150** | exit 0 |
| rejected fallback | 3 targeted tests fail (as designed) | - | 72/72 | 138/150 (12 × R6) | exit 0 |

Every number here is asserted by the workflow, so the run fails if any one changes. Controls: 11/11.
