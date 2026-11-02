"""Build a *patched copy* of the pinned Python SDK for fix-validation experiments.

    python scripts/fix_validation.py <venv-dir> {http,dispatcher,both}
    FAULTLINE_TARGET_PYTHON=<venv-dir>/bin/python faultline run -t py-stdio -t py-http-sse

The venv is created with the stdlib ``venv`` module and pip, so every installed
file is a private copy. Before editing anything the script refuses to touch a
file with more than one hard link: package managers that hardlink from a shared
cache (e.g. uv's default on some platforms) would otherwise propagate the patch
into the cache and into every other environment using it.

Variants:

* ``http``       - injective stream keys at the three ``str(id)`` sites in
                   ``mcp/server/streamable_http.py`` (the shape proposed in
                   python-sdk#3786).
* ``dispatcher`` - exact-typed ``_in_flight`` keys in
                   ``mcp/shared/jsonrpc_dispatcher.py``; the cancel lookup tries
                   the exact id first and falls back to the other-typed twin,
                   preserving the SDK's deliberate leniency for peers that
                   stringify ids.
* ``both``       - both of the above.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PIN = "mcp==2.3.0"

DISPATCHER_EDITS = [
    (
        "self._in_flight[coerce_request_id(req.id)] = _InFlight(scope=scope, dctx=dctx)",
        "self._in_flight[req.id] = _InFlight(scope=scope, dctx=dctx)",
    ),
    (
        "if rid is not None and (in_flight := self._in_flight.get(coerce_request_id(rid))) is not None:",
        "if rid is not None and (in_flight := _lookup_in_flight(self._in_flight, rid)) is not None:",
    ),
    (
        "                    key = coerce_request_id(req.id)\n",
        "                    key = req.id\n",
    ),
]
DISPATCHER_HELPER = '''

def _lookup_in_flight(table, rid):
    """Exact typed id first; fall back to the other-typed twin only if the exact id is absent."""
    hit = table.get(rid)
    if hit is not None:
        return hit
    if isinstance(rid, int) and not isinstance(rid, bool):
        return table.get(str(rid))
    coerced = coerce_request_id(rid)
    return table.get(coerced) if coerced is not rid else None
'''

HTTP_EDITS = [
    ("\n            request_id = str(message.id)\n", "\n            request_id = _stream_key(message.id)\n"),
    ("target_request_id = str(message.id)", "target_request_id = _stream_key(message.id)"),
    ("target_request_id = str(related_request_id)", "target_request_id = _stream_key(related_request_id)"),
]
HTTP_HELPER = '''

def _stream_key(request_id):
    """Injective stream key: 7 -> '7', "7" -> '"7"'; never equal to GET_STREAM_KEY."""
    import json as _json

    return _json.dumps(request_id)
'''


def _patch(path: Path, edits: list[tuple[str, str]], helper: str) -> None:
    if os.stat(path).st_nlink > 1:
        raise SystemExit(f"refusing to patch {path}: it is hard-linked ({os.stat(path).st_nlink} links)")
    text = path.read_text(encoding="utf-8")
    for old, new in edits:
        if text.count(old) != 1:
            raise SystemExit(f"{path.name}: expected exactly one occurrence of {old.strip()!r}")
        text = text.replace(old, new)
    path.write_text(text + helper, encoding="utf-8")
    print(f"patched {path}")


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[2] not in ("http", "dispatcher", "both"):
        raise SystemExit(__doc__)
    venv, variant = Path(sys.argv[1]), sys.argv[2]
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
    python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    subprocess.run([str(python), "-m", "pip", "install", "-q", "--no-cache-dir", PIN], check=True)
    site = Path(
        subprocess.run(
            [str(python), "-c", "import mcp, pathlib; print(pathlib.Path(mcp.__file__).parent)"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    if variant in ("dispatcher", "both"):
        _patch(site / "shared" / "jsonrpc_dispatcher.py", DISPATCHER_EDITS, DISPATCHER_HELPER)
    if variant in ("http", "both"):
        _patch(site / "server" / "streamable_http.py", HTTP_EDITS, HTTP_HELPER)
    print(f"FAULTLINE_TARGET_PYTHON={python}")


if __name__ == "__main__":
    main()
