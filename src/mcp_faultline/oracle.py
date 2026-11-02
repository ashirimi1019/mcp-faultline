"""Specification-based oracle for FL-001 (typed request-id isolation).

The oracle reads only a :class:`~mcp_faultline.trace.Trace`; it never talks to
the target. Rules are derived from JSON-RPC 2.0 and MCP 2025-11-25:

======  =========================================================================
rule    requirement
======  =========================================================================
WIRE    every inbound message is well-formed JSON-RPC 2.0 (JSON-RPC 2.0 §4-5)
R1      a response id equals the id of an issued request, *including its type*;
        "The id ... MUST be the same as the value of the id member in the
        Request Object" (JSON-RPC 2.0 §5)
R2      at most one response per request id (JSON-RPC 2.0 §5: the Server MUST
        reply with *a* Response)
R3      every request that was not cancelled gets a response (JSON-RPC 2.0 §4:
        "the Server MUST reply"; MCP cancellation only exempts cancelled ones)
R4      a response carries the payload of its own request (gate(tag) -> tag)
R5      Streamable HTTP: the response arrives on the HTTP stream of the POST
        that carried the request (MCP 2025-11-25 Transports, "Sending Messages
        to the Server": the POST's SSE stream or JSON body carries its response)
R6      cancellation isolation: cancelling id X must not suppress the response
        to a different id Y, notably Y = the other-typed twin of X ("7" vs 7)
R7      recovery: after the scenario the session still serves a fresh request
======  =========================================================================

SHOULD-level behaviour is reported as an *observation*, never a failure:

* ``cancel-ignored``      a cancelled request still returned its normal result
  (MCP: receivers SHOULD stop processing; races are explicitly allowed)
* ``cancel-answered``     an error response was sent for a cancelled request
  (MCP: receivers SHOULD NOT respond)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from .engine import RECOVERY_ID
from .jsonrpc import IdKey, classify, format_id, id_key, is_valid_id, obj
from .trace import Trace

RULES: dict[str, str] = {
    "WIRE": "inbound message is valid JSON-RPC 2.0",
    "R1": "response id matches an issued request id exactly (type and value)",
    "R2": "at most one response per request",
    "R3": "every non-cancelled request receives a response",
    "R4": "response payload belongs to its own request",
    "R5": "HTTP response delivered on its request's stream",
    "R6": "cancelling one id never suppresses another id's response",
    "R7": "session recovers and serves a fresh request",
}


@dataclass(frozen=True)
class Finding:
    rule: str
    message: str
    ids: tuple[str, ...] = ()
    evidence: tuple[int, ...] = ()  # trace event seq numbers

    def to_json(self) -> dict[str, Any]:
        return {"rule": self.rule, "message": self.message, "ids": list(self.ids), "evidence": list(self.evidence)}


@dataclass
class _Req:
    id: Any
    tag: str | None
    channel: str
    seq: int
    cancel_seq: int | None = None
    responses: list[tuple[int, dict[str, Any], str]] = field(
        default_factory=lambda: list[tuple[int, dict[str, Any], str]]()
    )


@dataclass(frozen=True)
class Verdict:
    target: str
    scenario: str
    violations: tuple[Finding, ...]
    observations: tuple[Finding, ...]
    outcomes: dict[str, str]

    @property
    def passed(self) -> bool:
        return not self.violations

    @property
    def signature(self) -> frozenset[str]:
        """Rule ids violated - the identity of a failure for minimisation."""
        return frozenset(f.rule for f in self.violations)

    def to_json(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "scenario": self.scenario,
            "passed": self.passed,
            "violations": [f.to_json() for f in self.violations],
            "observations": [f.to_json() for f in self.observations],
            "outcomes": self.outcomes,
        }


def _twin(key: IdKey) -> IdKey | None:
    kind, text = key
    if kind == "int":
        return ("str", text)
    try:
        return ("int", str(int(text))) if str(int(text)) == text else None
    except ValueError:
        return None


def _text_of(result: Any) -> str | None:
    if isinstance(result, dict):
        content = result.get("content")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        if isinstance(content, list) and content and isinstance(content[0], dict):
            text = content[0].get("text")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            return text if isinstance(text, str) else None
    return None


def evaluate(trace: Trace) -> Verdict:
    violations: list[Finding] = []
    observations: list[Finding] = []
    issued: dict[IdKey, _Req] = {}
    http = trace.provenance.get("transport", "stdio") != "stdio"

    for event in trace.events:
        if event.dir == "note":
            continue
        try:
            msg = json.loads(event.raw)
        except ValueError:
            if event.dir == "in":
                violations.append(Finding("WIRE", "inbound message is not valid JSON", evidence=(event.seq,)))
            continue
        if event.dir == "out":
            out = obj(msg)
            params = obj(out.get("params"))
            if "id" in out and "method" in out and is_valid_id(out["id"]):
                tag = obj(params.get("arguments")).get("tag") if params.get("name") == "gate" else None
                issued[id_key(out["id"])] = _Req(out["id"], tag, event.channel, event.seq)
            elif out.get("method") == "notifications/cancelled":
                rid = params.get("requestId")
                if is_valid_id(rid) and (req := issued.get(id_key(rid))) is not None:
                    req.cancel_seq = event.seq
            continue

        shape = classify(msg)
        if shape.kind == "invalid":
            violations.append(Finding("WIRE", "; ".join(shape.problems), evidence=(event.seq,)))
            continue
        if shape.kind not in ("response", "error"):
            continue
        rid = msg["id"]
        if rid is None:
            violations.append(
                Finding("R1", "error response with null id (request id was valid)", evidence=(event.seq,))
            )
            continue
        key = id_key(rid)
        req = issued.get(key)
        if req is None:
            twin = _twin(key)
            hint = ""
            if twin is not None and twin in issued:
                hint = f"; an issued request has id {format_id(issued[twin].id)} - the id type was coerced"
            violations.append(
                Finding(
                    "R1",
                    f"response id {format_id(rid)} matches no issued request{hint}",
                    (format_id(rid),),
                    (event.seq,),
                )
            )
            continue
        req.responses.append((event.seq, msg, event.channel))

    outcomes: dict[str, str] = {}
    for key, req in issued.items():
        shown = format_id(req.id)
        ctl = isinstance(req.id, str) and req.id.startswith("fl-")
        seqs = tuple(s for s, _, _ in req.responses)
        if len(req.responses) > 1:
            violations.append(Finding("R2", f"{len(req.responses)} responses for id {shown}", (shown,), seqs))
        if http:
            for seq, _, channel in req.responses:
                if channel != req.channel:
                    violations.append(
                        Finding(
                            "R5",
                            f"response for {shown} arrived on {channel}, request was sent on {req.channel}",
                            (shown,),
                            (seq,),
                        )
                    )
        if req.id == RECOVERY_ID:
            if not req.responses:
                violations.append(Finding("R7", "session did not serve the post-scenario recovery request", (shown,)))
            continue
        if ctl:
            if not req.responses and req.id != "fl-init":
                violations.append(Finding("R7", f"control request {shown} got no response", (shown,), (req.seq,)))
            continue

        cancelled = req.cancel_seq is not None
        after_cancel = [r for r in req.responses if cancelled and r[0] > (req.cancel_seq or 0)]
        if not req.responses:
            outcomes[shown] = "cancelled:no-response" if cancelled else "LOST"
            if not cancelled:
                violations.append(Finding("R3", f"request {shown} never received a response", (shown,), (req.seq,)))
                twin = _twin(key)
                if twin is not None and twin in issued and issued[twin].cancel_seq is not None:
                    violations.append(
                        Finding(
                            "R6",
                            f"cancelling {format_id(issued[twin].id)} suppressed the response to {shown}",
                            (format_id(issued[twin].id), shown),
                            (issued[twin].cancel_seq or 0, req.seq),
                        )
                    )
            continue

        seq, first, _ = req.responses[0]
        if "error" in first:
            code = first["error"].get("code")
            outcomes[shown] = f"{'cancelled:' if cancelled else ''}error:{code}"
            if req.tag is not None and not cancelled:
                # gate(tag) cannot fail on its own; an error here was caused by something else.
                violations.append(
                    Finding("R4", f"request {shown} was never cancelled but got error {code}", (shown,), (seq,))
                )
                twin = _twin(key)
                if twin is not None and twin in issued and issued[twin].cancel_seq is not None:
                    violations.append(
                        Finding(
                            "R6",
                            f"cancelling {format_id(issued[twin].id)} produced an error response for {shown}",
                            (format_id(issued[twin].id), shown),
                            (issued[twin].cancel_seq or 0, seq),
                        )
                    )
        else:
            text = _text_of(first.get("result"))
            outcomes[shown] = f"{'cancelled:' if cancelled else ''}result:{text}"
            if req.tag is not None and text != req.tag:
                violations.append(
                    Finding(
                        "R4", f"response to {shown} carries payload {text!r}, expected {req.tag!r}", (shown,), (seq,)
                    )
                )
        for s, resp, _ in after_cancel:
            kind = "cancel-answered" if "error" in resp else "cancel-ignored"
            observations.append(Finding(kind, f"{kind.replace('-', ' ')} for {shown}", (shown,), (s,)))

    return Verdict(
        target=trace.target,
        scenario=str(trace.scenario.get("name", "")),
        violations=tuple(violations),
        observations=tuple(observations),
        outcomes=outcomes,
    )
