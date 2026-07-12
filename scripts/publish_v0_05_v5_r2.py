#!/usr/bin/env python3
"""Generate and package the v0.05-v5-r2 runtime packets."""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "c3d6f02536f153a29c995f53c981f46ebbb414bb"
SOURCE_COMMIT_DATE = "2026-07-11T19:23:06-07:00"
QUESTION_SHA256 = "d176d8e5f4543c8215e1fc4960af204ebe31c6bc86d8a5ac63ba06598006147a"
INGEST_SHA256 = "629fd90ad90a4717af25947cecd14fa40bb3072597b5db9d4e549387fc1ffa70"
PACKET_DIR = ROOT / "packets" / "v0.05-v5-r2"


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    run("git", "diff", "--exit-code", SOURCE_COMMIT, "--", "model", "scripts/build_master_prompt.py")
    run(sys.executable, "scripts/build_master_prompt.py")
    run(sys.executable, "scripts/build_master_prompt.py", "model/manifests/ingest.json")

    PACKET_DIR.mkdir(parents=True, exist_ok=True)
    records = [
        {
            "source": ROOT / "model" / "dist" / "the_model_runtime.txt",
            "target": PACKET_DIR / "the_model_runtime.txt",
            "operation": "question_runtime",
            "authoritative_manifest": "model/manifest.json",
            "expected_sha256": QUESTION_SHA256,
        },
        {
            "source": ROOT / "model" / "dist" / "ingest_support_runtime.txt",
            "target": PACKET_DIR / "ingest_support_runtime.txt",
            "operation": "paper_ingest_and_evidence_maintenance",
            "authoritative_manifest": "model/manifests/ingest.json",
            "expected_sha256": INGEST_SHA256,
        },
    ]

    packets: list[dict[str, object]] = []
    checksum_lines: list[str] = []
    for record in records:
        source = pathlib.Path(record["source"])
        target = pathlib.Path(record["target"])
        data = source.read_bytes()
        digest = sha256(data)
        expected = str(record["expected_sha256"])
        if digest != expected:
            raise RuntimeError(
                f"{source.name}: generated SHA-256 {digest} does not match uploaded LF-normalized SHA-256 {expected}"
            )
        target.write_bytes(data)
        packets.append(
            {
                "authoritative_manifest": record["authoritative_manifest"],
                "bytes": len(data),
                "operation": record["operation"],
                "path": target.name,
                "sha256": digest,
            }
        )
        checksum_lines.append(f"{digest}  {target.name}")

    manifest = {
        "packet_revision": "r2",
        "packets": packets,
        "provider_conformance_certified": False,
        "schema_version": "v1",
        "source_commit": SOURCE_COMMIT,
        "source_commit_date": SOURCE_COMMIT_DATE,
        "source_ref": f"main@{SOURCE_COMMIT}",
        "source_repository": "Remodeled-Brain/The-Model",
        "status": "adopted",
        "version": "v0.05-v5",
    }
    (PACKET_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    (PACKET_DIR / "SHA256SUMS").write_text(
        "\n".join(checksum_lines) + "\n", encoding="utf-8", newline="\n"
    )

    readme = f"""# The Model v0.05-v5 runtime packets, revision 2

These are refreshed, single-file browser-LLM handoffs generated from the
pinned source commit `{SOURCE_COMMIT}` after integration of the
external-retrieval and statistical-qualification architecture.

- `the_model_runtime.txt` is the primary question-reconstruction and answering runtime.
- `ingest_support_runtime.txt` is the paper-ingest and evidence-maintenance runtime.

Revision 2 adds source-bounded external retrieval, shared mathematical statistical
qualifiers, and neuroscience-specific dependency, leakage, nuisance, reliability,
circularity, classifier-consistency, permutation, and transport checks.

`v0.05-v5-r2` is a packet revision, not a Model version increment. The original
`packets/v0.05-v5/` release remains unchanged and preserves the immutable
`v0.05-v5` tag. `manifest.json` records the pinned source commit and SHA-256
digest of each refreshed packet. `SHA256SUMS` provides standard checksum lines.

Upload only the packet required for the operation. Do not combine the ingest
runtime with ordinary question work unless the requested task requires paper or
corpus ingestion.

These packets preserve the adopted source specification. They do not certify
that a particular provider follows it correctly. Live-provider conformance
remains explicit validation debt.
"""
    (PACKET_DIR / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    run("git", "checkout", "--", "model/dist")
    print(f"prepared {PACKET_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
