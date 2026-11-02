# Contributing

## Setup

```sh
python -m venv .venv && . .venv/bin/activate
pip install -e ".[targets,dev]"
npm ci --prefix targets/ts && npm ci --prefix targets/ts-v2
```

## Before opening a PR

```sh
ruff format --check . && ruff check .
pyright                       # strict
pytest -m "not sdk"           # fast, keyless, no SDKs needed
pytest -m sdk                 # pinned official SDKs (Python + Node)
faultline controls            # must report 11/11 (or N/N after your change)
```

## Rules of the road

* **Every new oracle rule needs a negative control.** Add a mutant to
  `reference_server.py` or a fault to `faults.py`, and declare in
  `controls.py` exactly which scenarios it must fail. A rule that has never
  been seen to fail is not evidence.
* **Cite the spec.** Every rule names the JSON-RPC 2.0 or MCP clause it
  enforces and its strength (MUST vs SHOULD). SHOULD-level behaviour is an
  observation, never a violation.
* **No hand-edited results.** Files under `evidence/` are produced by the CLI.
  Regenerate them; never edit them.
* **Fixtures stay identical.** The Python, TS v1 and TS v2 fixture servers
  must expose identical tool behaviour, or differential results mean nothing.
* **Upstream etiquette.** Search for existing issues and PRs first, state
  overlap explicitly, follow the target repo's CONTRIBUTING/AGENTS files, and
  don't present known defects as new.

## Commit style

Imperative subject (≤ 72 characters), and a body explaining *why*.
