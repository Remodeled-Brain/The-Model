#!/usr/bin/env python3
"""Generate a selected Model runtime from a manifest.

Default: model/manifest.json -> model/dist/the_model_runtime.txt
Optional: python scripts/build_master_prompt.py model/manifests/ingest.json
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = ROOT / "model"

HEADER = """\
# ============================================================================
# The Model — Question Reconstruction Runtime  [GENERATED]
# ============================================================================
#
# Primary operation:
# source question -> physical reconstruction -> answerability plan -> evidence
# binding -> bounded answer -> responsive translation.
#
# Paper ingest is an adaptive evidence-maintenance subsystem. The runtime remains
# valid against a frozen reviewed corpus.
# ============================================================================
"""


def main() -> int:
    manifest_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else MODEL / "manifest.json"
    if not manifest_path.is_absolute():
        manifest_path = ROOT / manifest_path
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_files = manifest["source_files"]
    generated = manifest.get("generated", [])
    if not generated:
        print("ERROR: manifest has no generated target", file=sys.stderr)
        return 1

    target = MODEL / generated[0]
    target.parent.mkdir(parents=True, exist_ok=True)
    parts = [HEADER]
    for name in source_files:
        source = MODEL / name
        body = source.read_text(encoding="utf-8")
        parts.append(f"\n\n===== {name} =====\n\n{body}")

    target.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {target.relative_to(ROOT)} from {len(source_files)} source files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
