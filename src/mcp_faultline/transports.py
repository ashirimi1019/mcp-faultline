"""Wire-level MCP transports driven by the harness itself.

The harness never uses an SDK client: it writes and reads raw JSON-RPC so the
system under test cannot be "helped" by a client library's own id handling.

* :class:`StdioConnection` - newline-delimited JSON over a child process's stdio.
* :class:`HttpConnection`  - MCP Streamable HTTP (POST with JSON or SSE replies).

Both expose the same small interface (:class:`Connection`). Every inbound
message is recorded with the channel it arrived on, so a response delivered on
the wrong HTTP stream is visible in the trace.
"""

from __future__ import annotations

import http.client
import json
import os
import queue
import socket
import subprocess
import threading
import time
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from .jsonrpc import format_id


@dataclass(frozen=True)
class Inbound:
    """One message received from the target."""

    raw: str
    channel: str
    at: float  # seconds since connection start (monotonic)


class Connection(Protocol):
    def send(self, message: dict[str, Any]) -> str:
        """Send one message; return the channel name its replies are expected on."""
        ...

    def recv(self, timeout: float) -> Inbound | None: ...

    def close(self) -> None: ...

    def diagnostics(self) -> str: ...


class TransportError(RuntimeError):
    pass


def _encode(message: dict[str, Any]) -> str:
    return json.dumps(message, separators=(",", ":"), ensure_ascii=False)


@dataclass
class _Base:
    _inbox: queue.Queue[Inbound] = field(default_factory=lambda: queue.Queue[Inbound]())
    _t0: float = field(default_factory=time.monotonic)

    def _put(self, raw: str, channel: str) -> None:
        self._inbox.put(Inbound(raw=raw, channel=channel, at=time.monotonic() - self._t0))

    def recv(self, timeout: float) -> Inbound | None:
        try:
            return self._inbox.get(timeout=max(timeout, 0.0))
        except queue.Empty:
            return None


class StdioConnection(_Base):
    """Newline-delimited JSON-RPC over a child process's stdin/stdout."""

    def __init__(self, command: Sequence[str], cwd: str | None = None, env: dict[str, str] | None = None) -> None:
        super().__init__()
        self.command = list(command)
        self._stderr: list[str] = []
        self._proc = subprocess.Popen(
            self.command,
            cwd=cwd,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
        )
        threading.Thread(target=self._pump_stdout, daemon=True).start()
        threading.Thread(target=self._pump_stderr, daemon=True).start()

    def _pump_stdout(self) -> None:
        assert self._proc.stdout is not None
        for line in self._proc.stdout:
            line = line.rstrip("\r\n")
            if line:
                self._put(line, "stdio")

    def _pump_stderr(self) -> None:
        assert self._proc.stderr is not None
        for line in self._proc.stderr:
            self._stderr.append(line.rstrip("\r\n"))
            del self._stderr[:-200]

    def send(self, message: dict[str, Any]) -> str:
        if self._proc.poll() is not None:
            raise TransportError(f"target exited with code {self._proc.returncode}")
        assert self._proc.stdin is not None
        try:
            self._proc.stdin.write(_encode(message) + "\n")
            self._proc.stdin.flush()
        except OSError as exc:
            raise TransportError(f"write to target failed: {exc}") from exc
        return "stdio"

    def close(self) -> None:
        _terminate(self._proc)

    def diagnostics(self) -> str:
        return "\n".join(self._stderr[-40:])


def iter_sse_data(lines: Iterator[bytes]) -> Iterator[str]:
    """Yield the ``data`` payload of each server-sent event (WHATWG SSE framing)."""
    data: list[str] = []
    for raw in lines:
        line = raw.decode("utf-8").rstrip("\r\n")
        if not line:
            if data:
                yield "\n".join(data)
            data = []
        elif line.startswith(":"):
            continue
        else:
            name, _, value = line.partition(":")
            if name == "data":
                data.append(value[1:] if value.startswith(" ") else value)
    if data:
        yield "\n".join(data)


class HttpConnection(_Base):
    """MCP Streamable HTTP client side, one HTTP request per JSON-RPC message.

    Each POST runs on its own thread so many requests can be in flight at once,
    which is the situation in which per-request stream bookkeeping matters.
    """

    def __init__(self, host: str, port: int, path: str, header_wait: float = 0.5) -> None:
        super().__init__()
        self.host, self.port, self.path = host, port, path
        self.header_wait = header_wait
        self.session_id: str | None = None
        self.protocol_version: str | None = None
        self._lock = threading.Lock()
        self._seq = 0
        self._log: list[str] = []

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        if self.protocol_version:
            headers["Mcp-Protocol-Version"] = self.protocol_version
        return headers

    def send(self, message: dict[str, Any]) -> str:
        with self._lock:
            self._seq += 1
            seq = self._seq
        label = format_id(message["id"]) if "id" in message else message.get("method", "?")
        channel = f"post#{seq}({label})"
        got_headers = threading.Event()
        threading.Thread(target=self._post, args=(message, channel, got_headers), daemon=True).start()
        got_headers.wait(self.header_wait)
        return channel

    def _post(self, message: dict[str, Any], channel: str, got_headers: threading.Event) -> None:
        conn = http.client.HTTPConnection(self.host, self.port, timeout=60)
        try:
            conn.request("POST", self.path, body=_encode(message).encode("utf-8"), headers=self._headers())
            resp = conn.getresponse()
            sid = resp.getheader("mcp-session-id")
            if sid and self.session_id is None:
                self.session_id = sid
            got_headers.set()
            ctype = (resp.getheader("content-type") or "").split(";")[0].strip()
            self._log.append(f"{channel}: HTTP {resp.status} {ctype or '-'}")
            if ctype == "text/event-stream":
                for data in iter_sse_data(iter(resp.readline, b"")):
                    if data.strip():
                        self._put(data, channel)
            else:
                body = resp.read().decode("utf-8")
                if resp.status >= 400:
                    self._log.append(f"{channel}: body {body[:300]}")
                if ctype == "application/json" and body.strip():
                    parsed: Any = json.loads(body)
                    items: list[Any] = parsed if isinstance(parsed, list) else [parsed]  # pyright: ignore[reportUnknownVariableType]
                    for item in items:
                        self._put(_encode(item), channel)
        except (OSError, http.client.HTTPException, ValueError) as exc:
            self._log.append(f"{channel}: {type(exc).__name__}: {exc}")
        finally:
            got_headers.set()
            conn.close()

    def close(self) -> None:
        if not self.session_id:
            return
        conn = http.client.HTTPConnection(self.host, self.port, timeout=5)
        try:
            conn.request("DELETE", self.path, headers=self._headers())
            conn.getresponse().read()
        except (OSError, http.client.HTTPException):
            pass
        finally:
            conn.close()

    def diagnostics(self) -> str:
        return "\n".join(self._log[-40:])


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_port(port: int, timeout: float, alive: Callable[[], bool]) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not alive():
            raise TransportError("target process exited before listening")
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise TransportError(f"target did not listen on port {port} within {timeout}s")


class ManagedHttpConnection(HttpConnection):
    """An :class:`HttpConnection` that owns the server process it talks to."""

    def __init__(self, command: Sequence[str], port: int, path: str, cwd: str | None = None) -> None:
        super().__init__("127.0.0.1", port, path)
        self._proc = subprocess.Popen(
            list(command),
            cwd=cwd,
            env=os.environ.copy(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            wait_for_port(port, 30.0, lambda: self._proc.poll() is None)
        except TransportError:
            _terminate(self._proc)
            raise

    def close(self) -> None:
        try:
            super().close()
        finally:
            _terminate(self._proc)


def _terminate(proc: subprocess.Popen[Any]) -> None:
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
    for stream in (proc.stdin, proc.stdout, proc.stderr):
        if stream is not None:
            try:
                stream.close()
            except OSError:
                pass
