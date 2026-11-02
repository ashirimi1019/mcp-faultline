"""MCP Faultline target: official Python SDK server.

Exposes two deterministic tools so the harness, not wall-clock sleeps,
controls completion order:

* ``gate(tag)``    blocks until ``release(tag)`` is called, then returns ``tag``.
* ``release(tag)`` opens the gate for ``tag`` (idempotent; may precede ``gate``).

Usage::

    python server.py stdio
    python server.py http --port 8765 [--json-response]
"""

from __future__ import annotations

import argparse

import anyio
from mcp.server.mcpserver import MCPServer

server = MCPServer("faultline-python-target")
_gates: dict[str, anyio.Event] = {}


def _event(tag: str) -> anyio.Event:
    event = _gates.get(tag)
    if event is None:
        event = _gates[tag] = anyio.Event()
    return event


@server.tool()
async def gate(tag: str) -> str:
    """Block until ``release(tag)`` is called, then return ``tag``."""
    await _event(tag).wait()
    return tag


@server.tool()
async def release(tag: str) -> str:
    """Open the gate named ``tag``."""
    _event(tag).set()
    return tag


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("transport", choices=["stdio", "http"])
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--json-response", action="store_true")
    args = parser.parse_args()
    if args.transport == "stdio":
        server.run("stdio")
    else:
        server.run(
            "streamable-http",
            host="127.0.0.1",
            port=args.port,
            json_response=args.json_response,
        )


if __name__ == "__main__":
    main()
