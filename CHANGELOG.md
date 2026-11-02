# Changelog

## Unreleased

- Upstream-ready python-sdk fix for typed request-id isolation (`docs/upstream/patches/`): exact-id cancellation in the
  dispatcher and injective Streamable HTTP stream keys. Validated on python-sdk `main` d7845c0: FL-001 72/72 and
  150/150 random scenarios patched, versus 41/72 and 52/150 unpatched (`evidence/fl001-fix/`).
- `scripts/fix_validation.py` now builds unpatched/patched SDKs from upstream source with `git apply` into a fresh
  venv, instead of string-editing installed files.
- docs: record the rejected coercion-fallback design and the late-cancel race that disproved it.

## 0.1.0 - 2026-11-02

First release, written from scratch (see docs/audit.md).

- Wire-level stdio and Streamable HTTP (SSE and JSON) transports; the harness itself uses only the stdlib.
- Gate-based deterministic scenarios, execution traces with provenance, replay.
- Spec-based oracle (R1-R7, WIRE) with MUST violations separated from SHOULD-level observations.
- Fault injection and a stdlib reference server with 5 planted mutants; `faultline controls` self-test (11/11).
- ddmin minimisation with stability confirmation; export as pytest regression and stdlib-only reproduction.
- Targets pinned to python-sdk 2.3.0, typescript-sdk 1.32.2 and typescript-sdk v2 2.4.0 at protocol 2025-11-25.
- FL-001 typed request-id isolation: 24 fixed scenarios plus seeded random generation.
