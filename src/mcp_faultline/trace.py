"""Structured execution traces with provenance.

A trace is the complete evidence for one run: every byte-level message the
harness sent and received (with channel and monotonic time), the scenario that
drove it, and enough provenance to reproduce it (target command, SDK version,
protocol revision, harness version, interpreter, platform, git commit).
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from . import __version__

Direction = Literal["out", "in", "note"]
TRACE_FORMAT = "mcp-faultline/trace@1"


@dataclass(frozen=True)
class TraceEvent:
    seq: int
    at: float
    dir: Direction
    channel: str
    raw: str
    step: int | None = None  # scenario step index that produced/preceded it

    def to_json(self) -> dict[str, Any]:
        out: dict[str, Any] = {"seq": self.seq, "at": round(self.at, 6), "dir": self.dir, "channel": self.channel}
        if self.step is not None:
            out["step"] = self.step
        out["raw"] = self.raw
        return out

    @staticmethod
    def from_json(data: dict[str, Any]) -> TraceEvent:
        return TraceEvent(
            seq=int(data["seq"]),
            at=float(data["at"]),
            dir=data["dir"],
            channel=str(data["channel"]),
            raw=str(data["raw"]),
            step=data.get("step"),
        )


@dataclass
class Trace:
    target: str
    scenario: dict[str, Any]
    provenance: dict[str, Any]
    events: list[TraceEvent] = field(default_factory=lambda: list[TraceEvent]())
    diagnostics: str = ""

    def to_json(self) -> dict[str, Any]:
        return {
            "format": TRACE_FORMAT,
            "target": self.target,
            "provenance": self.provenance,
            "scenario": self.scenario,
            "events": [e.to_json() for e in self.events],
            "diagnostics": self.diagnostics,
        }

    @staticmethod
    def from_json(data: dict[str, Any]) -> Trace:
        if data.get("format") != TRACE_FORMAT:
            raise ValueError(f"unsupported trace format {data.get('format')!r}")
        return Trace(
            target=str(data["target"]),
            scenario=dict(data["scenario"]),
            provenance=dict(data["provenance"]),
            events=[TraceEvent.from_json(e) for e in data["events"]],
            diagnostics=str(data.get("diagnostics", "")),
        )

    def dump(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_json(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    @staticmethod
    def load(path: Path) -> Trace:
        return Trace.from_json(json.loads(path.read_text(encoding="utf-8")))


def _git_commit(root: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, timeout=5, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None if out.returncode == 0 else None


def base_provenance(root: Path) -> dict[str, Any]:
    return {
        "harness": f"mcp-faultline {__version__}",
        "harness_commit": _git_commit(root),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "started_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
