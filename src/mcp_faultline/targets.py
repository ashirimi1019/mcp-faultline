"""Target registry: how to launch each system under test, and what it is.

A target couples an implementation (official Python SDK, official TypeScript
SDK, or the in-repo reference server and its mutants) with a transport. SDK
versions are pinned (``PINNED``) and the *installed* version is detected at
run time and recorded in the trace, so a result can never silently refer to
a different SDK build than the one that produced it.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any, Literal

from .reference_server import MUTANTS
from .transports import Connection, ManagedHttpConnection, StdioConnection, free_port

PINNED = {"python-sdk": "2.3.0", "typescript-sdk": "1.32.2", "typescript-sdk-v2": "2.4.0"}
"""SDK versions this release of the harness was validated against."""

PROTOCOL_REVISION = "2025-11-25"
"""Newest revision supported by *both* pinned SDKs; used for every FL-001 run."""

Transport = Literal["stdio", "http-sse", "http-json"]


def repo_root() -> Path:
    env = os.environ.get("FAULTLINE_ROOT")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2]


def targets_dir() -> Path:
    return repo_root() / "targets"


def target_python() -> str:
    """Interpreter that has the pinned ``mcp`` package installed."""
    return os.environ.get("FAULTLINE_TARGET_PYTHON", sys.executable)


@dataclass(frozen=True)
class Target:
    name: str
    implementation: str  # "python-sdk" | "typescript-sdk" | "reference"
    transport: Transport
    description: str
    _connect: Callable[[], Connection]
    _version: Callable[[], str | None]

    def connect(self) -> Connection:
        return self._connect()

    def version(self) -> str | None:
        return self._version()

    def provenance(self) -> dict[str, Any]:
        detected = self.version()
        pinned = PINNED.get(self.implementation)
        return {
            "target": self.name,
            "implementation": self.implementation,
            "implementation_version": detected,
            "pinned_version": pinned,
            "version_matches_pin": None if pinned is None else detected == pinned,
            "transport": self.transport,
            "protocol_revision": PROTOCOL_REVISION,
        }


@cache
def python_sdk_version() -> str | None:
    try:
        out = subprocess.run(
            [target_python(), "-c", "import importlib.metadata as m; print(m.version('mcp'))"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None if out.returncode == 0 else None


def _npm_version(directory: str, package: str) -> str | None:
    pkg = targets_dir() / directory / "node_modules" / package / "package.json"
    try:
        return str(json.loads(pkg.read_text(encoding="utf-8"))["version"])
    except (OSError, ValueError, KeyError):
        return None


@cache
def typescript_sdk_version() -> str | None:
    return _npm_version("ts", "@modelcontextprotocol/sdk")


@cache
def typescript_sdk_v2_version() -> str | None:
    return _npm_version("ts-v2", "@modelcontextprotocol/server")


def _py_stdio() -> Connection:
    return StdioConnection([target_python(), str(targets_dir() / "python" / "server.py"), "stdio"])


def _py_http(json_response: bool) -> Callable[[], Connection]:
    def connect() -> Connection:
        port = free_port()
        cmd = [target_python(), str(targets_dir() / "python" / "server.py"), "http", "--port", str(port)]
        if json_response:
            cmd.append("--json-response")
        return ManagedHttpConnection(cmd, port, "/mcp")

    return connect


def _ts_stdio(directory: str) -> Callable[[], Connection]:
    def connect() -> Connection:
        return StdioConnection(["node", str(targets_dir() / directory / "server.mjs"), "stdio"])

    return connect


def _ts_http(directory: str, json_response: bool) -> Callable[[], Connection]:
    def connect() -> Connection:
        port = free_port()
        cmd = ["node", str(targets_dir() / directory / "server.mjs"), "http", "--port", str(port)]
        if json_response:
            cmd.append("--json-response")
        return ManagedHttpConnection(cmd, port, "/mcp")

    return connect


def _reference(mutant: str) -> Callable[[], Connection]:
    def connect() -> Connection:
        return StdioConnection([sys.executable, "-m", "mcp_faultline.reference_server", "--mutant", mutant])

    return connect


def _build() -> dict[str, Target]:
    from . import __version__

    targets = [
        Target("py-stdio", "python-sdk", "stdio", "Python SDK MCPServer over stdio", _py_stdio, python_sdk_version),
        Target(
            "py-http-sse",
            "python-sdk",
            "http-sse",
            "Python SDK MCPServer, Streamable HTTP, SSE responses",
            _py_http(False),
            python_sdk_version,
        ),
        Target(
            "py-http-json",
            "python-sdk",
            "http-json",
            "Python SDK MCPServer, Streamable HTTP, JSON responses",
            _py_http(True),
            python_sdk_version,
        ),
        Target(
            "ts-stdio",
            "typescript-sdk",
            "stdio",
            "TS SDK v1 McpServer over stdio",
            _ts_stdio("ts"),
            typescript_sdk_version,
        ),
        Target(
            "ts-http-sse",
            "typescript-sdk",
            "http-sse",
            "TS SDK v1 McpServer, Streamable HTTP, SSE responses",
            _ts_http("ts", False),
            typescript_sdk_version,
        ),
        Target(
            "ts-http-json",
            "typescript-sdk",
            "http-json",
            "TS SDK v1 McpServer, Streamable HTTP, JSON responses",
            _ts_http("ts", True),
            typescript_sdk_version,
        ),
        Target(
            "ts2-stdio",
            "typescript-sdk-v2",
            "stdio",
            "TS SDK v2 McpServer over stdio",
            _ts_stdio("ts-v2"),
            typescript_sdk_v2_version,
        ),
        Target(
            "ts2-http-sse",
            "typescript-sdk-v2",
            "http-sse",
            "TS SDK v2 McpServer, Streamable HTTP, SSE responses",
            _ts_http("ts-v2", False),
            typescript_sdk_v2_version,
        ),
        Target(
            "ts2-http-json",
            "typescript-sdk-v2",
            "http-json",
            "TS SDK v2 McpServer, Streamable HTTP, JSON responses",
            _ts_http("ts-v2", True),
            typescript_sdk_v2_version,
        ),
    ]
    for mutant in MUTANTS:
        name = "ref" if mutant == "none" else f"ref:{mutant}"
        desc = (
            "In-repo reference server (correct)" if mutant == "none" else f"Reference server, planted defect: {mutant}"
        )
        targets.append(Target(name, "reference", "stdio", desc, _reference(mutant), lambda: __version__))
    return {t.name: t for t in targets}


TARGETS = _build()
SDK_TARGETS = tuple(n for n, t in TARGETS.items() if t.implementation != "reference")


def get_target(name: str) -> Target:
    try:
        return TARGETS[name]
    except KeyError:
        raise KeyError(f"unknown target {name!r}; choose from: {', '.join(TARGETS)}") from None
