"""A minimal, dependency-free MCP server used as a reference and as a mutant host.

It speaks just enough of MCP (revision 2025-11-25) over stdio for FL-001:
``initialize``, ``ping``, ``tools/list``, ``tools/call`` (``gate``/``release``)
and ``notifications/cancelled``.

With ``--mutant`` it plants one known defect. Mutants are the negative
controls: an oracle that passes them is not testing anything.

=====================  ==========================================================
mutant                 planted defect
=====================  ==========================================================
``none``               correct behaviour (positive control)
``coerce-inflight``    in-flight table keyed by ``int("7")`` folding (cancel
                       cross-targets the twin id) - mirrors a real SDK design
``coerce-response-id`` replies to request ``"7"`` with response id ``7``
``str-key-route``      routes replies via ``str(id)`` keys, last writer wins
``ignore-cancel``      ignores ``notifications/cancelled`` (a SHOULD, not a MUST)
``drop-string-ids``    never replies to string-id requests
=====================  ==========================================================
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
from typing import Any

MUTANTS = ("none", "coerce-inflight", "coerce-response-id", "str-key-route", "ignore-cancel", "drop-string-ids")
PROTOCOL_VERSION = "2025-11-25"


def _coerce(request_id: Any) -> Any:
    if isinstance(request_id, str):
        try:
            return int(request_id)
        except ValueError:
            return request_id
    return request_id


def _obj(value: object) -> dict[str, Any]:
    # Deliberately independent of mcp_faultline.jsonrpc: the reference must not share code with the oracle.
    return value if isinstance(value, dict) else {}  # pyright: ignore[reportUnknownVariableType]


def _key(request_id: Any) -> Any:
    return (type(request_id).__name__, request_id)


class ReferenceServer:
    def __init__(self, mutant: str = "none", out: Any = None) -> None:
        if mutant not in MUTANTS:
            raise ValueError(f"unknown mutant {mutant!r}")
        self.mutant = mutant
        self.out = out if out is not None else sys.stdout
        self._write_lock = threading.Lock()
        self._state = threading.Lock()
        self._gates: dict[str, threading.Event] = {}
        self._in_flight: dict[Any, threading.Event] = {}  # key -> cancel flag
        self._routes: dict[str, Any] = {}  # str-key-route mutant only

    # -- plumbing ---------------------------------------------------------
    def _emit(self, message: dict[str, Any]) -> None:
        with self._write_lock:
            self.out.write(json.dumps(message, separators=(",", ":")) + "\n")
            self.out.flush()

    def _reply(
        self, request_id: Any, result: dict[str, Any] | None = None, error: dict[str, Any] | None = None
    ) -> None:
        if self.mutant == "drop-string-ids" and isinstance(request_id, str) and not request_id.startswith("fl-"):
            return
        wire_id = request_id
        if self.mutant == "coerce-response-id":
            wire_id = _coerce(request_id)
        elif self.mutant == "str-key-route":
            with self._state:
                wire_id = self._routes.get(str(request_id), request_id)
        message: dict[str, Any] = {"jsonrpc": "2.0", "id": wire_id}
        if error is not None:
            message["error"] = error
        else:
            message["result"] = result if result is not None else {}
        self._emit(message)

    def _flight_key(self, request_id: Any) -> Any:
        return _coerce(request_id) if self.mutant == "coerce-inflight" else _key(request_id)

    def _gate(self, tag: str) -> threading.Event:
        with self._state:
            event = self._gates.get(tag)
            if event is None:
                event = self._gates[tag] = threading.Event()
            return event

    # -- dispatch ---------------------------------------------------------
    def handle(self, message: dict[str, Any]) -> None:
        method = message.get("method")
        if "id" not in message:
            if method == "notifications/cancelled" and self.mutant != "ignore-cancel":
                params = _obj(message.get("params"))
                with self._state:
                    flag = self._in_flight.get(self._flight_key(params.get("requestId")))
                if flag is not None:
                    flag.set()
            return
        request_id = message["id"]
        if method == "initialize":
            self._reply(
                request_id,
                {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "faultline-reference", "version": self.mutant},
                },
            )
        elif method == "ping":
            self._reply(request_id, {})
        elif method == "tools/list":
            schema = {"type": "object", "properties": {"tag": {"type": "string"}}, "required": ["tag"]}
            tools = [{"name": n, "inputSchema": schema} for n in ("gate", "release")]
            self._reply(request_id, {"tools": tools})
        elif method == "tools/call":
            params = _obj(message.get("params"))
            name = params.get("name")
            tag = str(_obj(params.get("arguments")).get("tag", ""))
            if name == "release":
                self._gate(tag).set()
                self._reply(request_id, _text(tag))
            elif name == "gate":
                cancelled = threading.Event()
                with self._state:
                    self._in_flight[self._flight_key(request_id)] = cancelled
                    self._routes[str(request_id)] = request_id
                threading.Thread(target=self._run_gate, args=(request_id, tag, cancelled), daemon=True).start()
            else:
                self._reply(request_id, error={"code": -32602, "message": f"unknown tool {name!r}"})
        else:
            self._reply(request_id, error={"code": -32601, "message": "method not found"})

    def _run_gate(self, request_id: Any, tag: str, cancelled: threading.Event) -> None:
        gate = self._gate(tag)
        while not gate.wait(0.01):
            if cancelled.is_set():
                break
        with self._state:
            key = self._flight_key(request_id)
            if self._in_flight.get(key) is cancelled:
                del self._in_flight[key]
        if cancelled.is_set():
            return  # MCP: receivers SHOULD NOT respond to a cancelled request
        self._reply(request_id, _text(tag))

    def serve(self, stream: Any) -> None:
        for line in stream:
            line = line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                self._emit({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}})
                continue
            if isinstance(message, dict):
                self.handle(message)  # pyright: ignore[reportUnknownArgumentType]


def _text(tag: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": tag}], "isError": False}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--mutant", choices=MUTANTS, default="none")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    ReferenceServer(args.mutant).serve(sys.stdin)


if __name__ == "__main__":
    main()
