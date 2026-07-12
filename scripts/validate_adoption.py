#!/usr/bin/env python3
"""Run structural, retrieval, statistical, target-identity, causal, and physical adoption gates."""
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    results = sys.argv[1:]
    commands = [
        [sys.executable, str(ROOT / "scripts/validate_repo.py")],
        [sys.executable, str(ROOT / "scripts/validate_resource_retrieval.py")],
        [sys.executable, str(ROOT / "scripts/validate_statistical_qualifiers.py")],
        [sys.executable, str(ROOT / "scripts/validate_model_policy.py")],
        [sys.executable, str(ROOT / "scripts/validate_target_identity.py")],
        [sys.executable, str(ROOT / "scripts/validate_conformance.py"), *results, "--adoption"],
        [sys.executable, str(ROOT / "scripts/validate_physical_continuity.py"), *results, "--adoption"],
    ]
    for command in commands:
        completed = subprocess.run(command, cwd=ROOT, check=False)
        if completed.returncode:
            return completed.returncode
    print("combined structural and semantic adoption validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
