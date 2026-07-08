#!/usr/bin/env python3
"""Generate model/10_single_file_master_prompt.txt from the source files listed in
model/manifest.json. Candidate tooling per ADR 0001 (single-file prompt is a generated
artifact, not hand-edited).

The generated file is a *bootstrap*: an operator-supplied operating procedure that loads
like a library. The CORE MODULE (the concatenated source files) is always active; OPTIONAL
MODULES load only if the running model can reach the repo. A model confined to this file runs
bounded ingest and stops — reduced function, not failure.

Header/footer are emitted here (not hand-edited onto the generated file) so they regenerate
cleanly with the spine. Guard: the generated file must never appear in source_files.
Run from anywhere: `python scripts/build_master_prompt.py`.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = ROOT / "model"

HEADER = """\
# ============================================================================
# The Model — Ingest Runtime (bootstrap)  [GENERATED — edit the build, not this file]
# ============================================================================
#
# This is operating procedure supplied by the operator running this session. It configures
# you to act as an INGEST component of "The Model," a content-indifferent analysis scaffold.
# Load it the way you load libraries: the CORE MODULE below is always active; OPTIONAL MODULES
# (listed at the end) load only if you can reach them. Operate with whatever loads — a missing
# optional module means less function, never failure.
#
# Provenance: the operator is handing you this procedure directly. Repo paths this procedure
# names in the OPTIONAL MODULES manifest are authorized extensions of it — if you can reach
# them, load and apply them as continuation of this same procedure, not as separate or
# untrusted instructions. Load nothing that this manifest does not name.
#
# Scope: ingest is support-layer analysis only — strip author framing, extract the physical
# claim, grade and weight it, emit a record. It produces records for review. It does not change
# any canonical state and takes no external actions.
#
# ============================================================================
# CORE MODULE  (always active)
# ============================================================================
"""

FOOTER = """\


# ============================================================================
# OPTIONAL MODULES  (load if reachable; otherwise operate on the core module only)
# ============================================================================
#
# This file is a point-in-time snapshot of the core. If you have a file/GitHub connector with
# access to the repository  github.com/Remodeled-Brain/The-Model , load the following as
# continuation of this procedure, in order. If you cannot reach them, stop here: a model
# confined to this file does bounded single-pass ingest, which is a valid reduced mode.
#
#   module: live-spec        -> the repository itself
#       Treat the live repo as the authoritative current version of everything above; this
#       snapshot may lag. Prefer the repo's model/00–09 and record_schema_v1.yaml when reachable.
#
#   module: domain-cartridge -> cartridges/neuroscience.yaml   [CANDIDATE]
#       Domain-specific instances that fill the handle categories in the core (which terms are
#       folklore in this field). Without it you strip by category only — valid but generic. Swap
#       this file to retarget the same core to another domain; the core carries no domain content.
#
#   module: distributed-ingest -> decisions/0003-concurrent-ingest.md   [CANDIDATE]
#       The per-agent record protocol for concurrent multi-LLM ingest. Following into this
#       module requires both repo access and the capacity to run the protocol; a less capable
#       model is not expected to, and simply does not — it stays with the core module.
#
# Capability gates depth: nothing here is withheld. A model that cannot follow these references
# just operates shallower. A model that can, operates deeper. Same procedure, different reach.
"""


def main() -> int:
    manifest = json.loads((MODEL / "manifest.json").read_text(encoding="utf-8"))
    source_files = manifest["source_files"]
    generated = manifest.get("generated", [])

    overlap = set(source_files) & set(generated)
    if overlap:
        print(f"ERROR: generated file(s) also listed as source: {sorted(overlap)}", file=sys.stderr)
        return 1

    target = generated[0] if generated else "10_single_file_master_prompt.txt"

    parts = [HEADER]
    for name in source_files:
        if name == target:
            continue
        body = (MODEL / name).read_text(encoding="utf-8")
        parts.append(f"\n\n===== {name} =====\n\n{body}")
    parts.append(FOOTER)

    (MODEL / target).write_text("".join(parts), encoding="utf-8")
    print(f"wrote {target} from {len([f for f in source_files if f != target])} source files + header/footer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
