"""JSON-RPC 2.0 message classification and independent wire validation.

These checks are written from the JSON-RPC 2.0 specification and the MCP
"Base Protocol" section (revision 2025-11-25), not from any SDK's schema, so
they can serve as an independent oracle for SDK behaviour.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal, TypeGuard

RequestId = int | str
"""MCP request ids: a string or an integer (MCP forbids ``null``)."""

IdKey = tuple[Literal["int", "str"], str]
"""An injective, hashable key for a request id: ``7`` and ``"7"`` never collide."""

MessageKind = Literal["request", "notification", "response", "error", "invalid"]


def id_key(request_id: RequestId) -> IdKey:
    """Return a collision-free key for ``request_id``.

    ``bool`` is rejected explicitly because ``True == 1`` in Python, which is
    exactly the kind of accidental coercion this project exists to detect.
    """
    if isinstance(request_id, bool):
        raise TypeError("bool is not a valid JSON-RPC request id")
    if isinstance(request_id, int):
        return ("int", str(request_id))
    if isinstance(request_id, str):  # pyright: ignore[reportUnnecessaryIsInstance]
        return ("str", request_id)
    raise TypeError(f"invalid request id type: {type(request_id).__name__}")


def format_id(request_id: object) -> str:
    """Render an id unambiguously (JSON form), so ``7`` and ``"7"`` look different in reports."""
    return json.dumps(request_id)


def obj(value: object) -> dict[str, Any]:
    """Narrow a decoded JSON value to an object; anything else becomes ``{}``."""
    return value if isinstance(value, dict) else {}  # pyright: ignore[reportUnknownVariableType]


def is_valid_id(value: object) -> TypeGuard[RequestId]:
    return (isinstance(value, int) and not isinstance(value, bool)) or isinstance(value, str)


@dataclass(frozen=True)
class Classified:
    kind: MessageKind
    problems: tuple[str, ...] = ()


def classify(message: object) -> Classified:
    """Classify one decoded JSON value and list every spec violation found."""
    if not isinstance(message, dict):
        return Classified("invalid", ("message is not a JSON object",))
    msg: dict[str, Any] = message  # pyright: ignore[reportUnknownVariableType]
    problems: list[str] = []
    if msg.get("jsonrpc") != "2.0":
        problems.append('"jsonrpc" member must be exactly "2.0"')

    has_method = "method" in msg
    has_result = "result" in msg
    has_error = "error" in msg

    if has_method:
        if not isinstance(msg["method"], str):
            problems.append('"method" must be a string')
        if has_result or has_error:
            problems.append("a request/notification must not carry result or error")
        if "params" in msg and not isinstance(msg["params"], dict | list):
            problems.append('"params" must be an object or array')
        if "id" in msg:
            if not is_valid_id(msg["id"]):
                problems.append(f"request id must be a string or integer, got {format_id(msg['id'])}")
            kind: MessageKind = "request"
        else:
            kind = "notification"
        return Classified("invalid" if problems else kind, tuple(problems))

    if has_result == has_error:
        problems.append("a response must carry exactly one of result or error")
    if "id" not in msg:
        problems.append('a response must carry an "id" member')
    elif not is_valid_id(msg["id"]) and not (has_error and msg["id"] is None):
        problems.append(f"response id must be a string or integer, got {format_id(msg['id'])}")
    if has_error:
        err = msg["error"]
        if not isinstance(err, dict):
            problems.append('"error" must be an object')
        else:
            code = err.get("code")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            if not isinstance(code, int) or isinstance(code, bool):
                problems.append('"error.code" must be an integer')
            if not isinstance(err.get("message"), str):  # pyright: ignore[reportUnknownMemberType]
                problems.append('"error.message" must be a string')
    if problems:
        return Classified("invalid", tuple(problems))
    return Classified("error" if has_error else "response")


def decode_line(line: str) -> tuple[object | None, str | None]:
    """Decode one framed message. Returns ``(value, None)`` or ``(None, reason)``."""
    try:
        return json.loads(line), None
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc.msg}"


def request(request_id: RequestId, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    msg: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        msg["params"] = params
    return msg


def notification(method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    msg: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        msg["params"] = params
    return msg
