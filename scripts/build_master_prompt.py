#!/usr/bin/env python3
"""Generate model/10_single_file_master_prompt.txt from the source files listed in
model/manifest.json. Candidate tooling per ADR 0001 (single-file prompt is a generated
artifact, not hand-edited).

Guard: the generated file must never appear in source_files (recursive inclusion).
Run from anywhere: `python scripts/build_master_prompt.py`.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = ROOT / "model"


def main() -> int:
    manifest = json.loads((MODEL / "manifest.json").read_text(encoding="utf-8"))
    source_files = manifest["source_files"]
    generated = manifest.get("generated", [])

    overlap = set(source_files) & set(generated)
    if overlap:
        print(f"ERROR: generated file(s) also listed as source: {sorted(overlap)}", file=sys.stderr)
        return 1

    target = generated[0] if generated else "10_single_file_master_prompt.txt"

    parts = [
        "# v0.05 v4 single-file master prompt (GENERATED — do not hand-edit)\n",
        "# Built from model/manifest.json source_files by scripts/build_master_prompt.py\n",
    ]
    for name in source_files:
        if name == target:
            continue
        body = (MODEL / name).read_text(encoding="utf-8")
        parts.append(f"\n\n===== {name} =====\n\n{body}")

    (MODEL / target).write_text("".join(parts), encoding="utf-8")
    print(f"wrote {target} from {len([f for f in source_files if f != target])} source files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
