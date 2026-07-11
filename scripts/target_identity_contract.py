#!/usr/bin/env python3
"""Stable hash over the target-identity semantic contract."""
from __future__ import annotations

import hashlib
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = ROOT / "model"
CONF = ROOT / "conformance"

TARGET_IDENTITY_FILES = (
    MODEL / "kernel" / "target_identity.yaml",
    MODEL / "runtime" / "target_identity_gate.yaml",
    MODEL / "runtime" / "target_identity_answer_contract.yaml",
    MODEL / "ingest" / "target_identity_extraction.yaml",
    MODEL / "ingest" / "target_identity_record_schema.yaml",
    CONF / "decision_record.schema.json",
)


def target_identity_contract_hash() -> str:
    digest = hashlib.sha256()
    for path in TARGET_IDENTITY_FILES:
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\x00")
        digest.update(path.read_bytes())
        digest.update(b"\x00")
    return digest.hexdigest()


if __name__ == "__main__":
    print(target_identity_contract_hash())
