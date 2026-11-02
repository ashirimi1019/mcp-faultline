"""Build the Python SDK from upstream source, optionally with the proposed fix applied.

    python scripts/fix_validation.py <workdir> {unpatched,patched,rejected-fallback} [--commit SHA]
    FAULTLINE_TARGET_PYTHON=<printed path> faultline run -t py-stdio -t py-http-sse -t py-http-json

Clones modelcontextprotocol/python-sdk at ``--commit`` (default: the commit the
patches were developed and validated on), applies the patch series in
``docs/upstream/patches/`` with ``git apply`` for ``patched`` (plus
``docs/upstream/rejected/*.patch`` for ``rejected-fallback``, a design kept only to
demonstrate its failure), and installs the
checkout into a fresh stdlib ``venv`` with pip. Nothing outside ``<workdir>`` is
modified: no shared caches, no hard links, no edits to installed packages.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

UPSTREAM = "https://github.com/modelcontextprotocol/python-sdk.git"
BASE_COMMIT = "d7845c073a2b9ba5ab2817ecf93d3e45ef24cd14"  # python-sdk main on 2026-11-02 (after v2.3.0)
PATCHES = Path(__file__).resolve().parents[1] / "docs" / "upstream" / "patches"
REJECTED = PATCHES.parent / "rejected"


def run(*cmd: str, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("workdir", type=Path)
    parser.add_argument("variant", choices=["unpatched", "patched", "rejected-fallback"])
    parser.add_argument("--commit", default=BASE_COMMIT)
    args = parser.parse_args()

    src = args.workdir / f"python-sdk-{args.variant}"
    if not src.exists():
        run("git", "clone", "--quiet", "--filter=blob:none", UPSTREAM, str(src))
    # The script owns this checkout: reset it so re-runs never stack patches.
    run("git", "checkout", "--quiet", "--force", "--detach", args.commit, cwd=src)
    run("git", "clean", "--quiet", "-fdx", cwd=src)
    if args.variant != "unpatched":
        patches = sorted(str(p) for p in PATCHES.glob("*.patch"))
        if args.variant == "rejected-fallback":
            patches += sorted(str(p) for p in REJECTED.glob("*.patch"))
        if not patches:
            raise SystemExit(f"no patches found in {PATCHES}")
        # One at a time, in order: `git apply --check a b` checks each patch against the
        # untouched tree, which rejects a patch that builds on an earlier one.
        for patch in patches:
            run("git", "apply", "--check", patch, cwd=src)
            run("git", "apply", patch, cwd=src)

    venv = args.workdir / f"venv-{args.variant}"
    run(sys.executable, "-m", "venv", str(venv))
    python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    # `mcp` pins its in-tree workspace sibling `mcp-types` to the same dev version: install both.
    run(str(python), "-m", "pip", "install", "--quiet", "--no-cache-dir", str(src / "src" / "mcp-types"), str(src))
    print(f"FAULTLINE_TARGET_PYTHON={python}")


if __name__ == "__main__":
    main()
