#!/usr/bin/env python3
"""Publish frozen single-file runtime packets from an immutable source ref.

The normal builders continue to write disposable outputs under model/dist/. This
script checks out the requested source ref in a temporary worktree, runs those
builders there, and copies the exact results into packets/<packet-id>/ with a
provenance manifest and checksums.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKET_SPECS = (
    {
        "operation": "question_runtime",
        "manifest": "model/manifest.json",
        "build_args": [],
        "generated": "model/dist/the_model_runtime.txt",
        "packet": "the_model_runtime.txt",
    },
    {
        "operation": "paper_ingest_and_evidence_maintenance",
        "manifest": "model/manifests/ingest.json",
        "build_args": ["model/manifests/ingest.json"],
        "generated": "model/dist/ingest_support_runtime.txt",
        "packet": "ingest_support_runtime.txt",
    },
)


def run(
    command: list[str],
    *,
    cwd: pathlib.Path = ROOT,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        capture_output=capture,
    )


def git_value(*args: str) -> str:
    return run(["git", *args], capture=True).stdout.strip()


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_readme(
    destination: pathlib.Path,
    *,
    model_version: str,
    packet_id: str,
    source_ref: str,
    packet_revision: str | None,
) -> None:
    revision_line = (
        f"This is packet revision `{packet_revision}` for Model version `{model_version}`.\n"
        if packet_revision
        else f"This packet corresponds to Model version `{model_version}`.\n"
    )
    text = f"""# The Model {packet_id} runtime packets

These files are frozen, single-file browser-LLM handoffs generated from the
immutable source ref `{source_ref}`.

{revision_line}
- `the_model_runtime.txt` is the primary question-reconstruction and answering runtime.
- `ingest_support_runtime.txt` is the paper-ingest and evidence-maintenance runtime.

Upload the packet required for the operation directly to the receiving LLM. The
packet is self-contained for its declared operation. Do not combine the ingest
runtime with ordinary question work unless the requested task actually requires
paper or corpus ingestion.

`manifest.json` records the source commit and SHA-256 digest of each packet.
`SHA256SUMS` provides standard checksum lines.

These files preserve the released specification. They do not certify that any
particular provider follows it correctly.
"""
    (destination / "README.md").write_text(text, encoding="utf-8", newline="\n")


def publish(
    model_version: str,
    packet_id: str,
    source_ref: str,
    packet_revision: str | None,
) -> pathlib.Path:
    source_commit = git_value("rev-parse", f"{source_ref}^{{commit}}")
    source_date = git_value("show", "-s", "--format=%cI", source_commit)
    destination = ROOT / "packets" / packet_id
    destination.mkdir(parents=True, exist_ok=True)

    temporary_root = pathlib.Path(tempfile.mkdtemp(prefix="the-model-packet-"))
    worktree = temporary_root / "source"
    records: list[dict[str, Any]] = []
    try:
        run(["git", "worktree", "add", "--detach", str(worktree), source_commit])
        builder = worktree / "scripts" / "build_master_prompt.py"
        for spec in PACKET_SPECS:
            run([sys.executable, str(builder), *spec["build_args"]], cwd=worktree)
            generated = worktree / spec["generated"]
            if not generated.is_file():
                raise RuntimeError(f"builder did not create {spec['generated']}")
            packet = destination / spec["packet"]
            shutil.copyfile(generated, packet)
            records.append(
                {
                    "operation": spec["operation"],
                    "authoritative_manifest": spec["manifest"],
                    "path": packet.name,
                    "sha256": sha256(packet),
                    "bytes": packet.stat().st_size,
                }
            )
    finally:
        if worktree.exists():
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(worktree)],
                cwd=ROOT,
                check=False,
            )
        shutil.rmtree(temporary_root, ignore_errors=True)

    manifest: dict[str, Any] = {
        "schema_version": "v1",
        "version": model_version,
        "packet_id": packet_id,
        "status": "adopted",
        "source_repository": "Remodeled-Brain/The-Model",
        "source_ref": source_ref,
        "source_commit": source_commit,
        "source_commit_date": source_date,
        "packets": records,
        "provider_conformance_certified": False,
    }
    if packet_revision:
        manifest["packet_revision"] = packet_revision
    (destination / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    checksum_lines = [f"{record['sha256']}  {record['path']}" for record in records]
    (destination / "SHA256SUMS").write_text(
        "\n".join(checksum_lines) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_readme(
        destination,
        model_version=model_version,
        packet_id=packet_id,
        source_ref=source_ref,
        packet_revision=packet_revision,
    )
    return destination


def main() -> int:
    default_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=default_version)
    parser.add_argument("--packet-id", default=None)
    parser.add_argument("--packet-revision", default=None)
    parser.add_argument("--source-ref", default=None)
    args = parser.parse_args()
    packet_id = args.packet_id or args.version
    source_ref = args.source_ref or args.version
    try:
        destination = publish(
            args.version,
            packet_id,
            source_ref,
            args.packet_revision,
        )
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"PACKET PUBLICATION FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"published runtime packets to {destination.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
