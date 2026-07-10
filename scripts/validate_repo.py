#!/usr/bin/env python3
"""Validate runtime manifests, generated artifacts, and machine-readable fixtures."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = ROOT / "model"
BUILDER = ROOT / "scripts" / "build_master_prompt.py"
DEFAULT_SELECTOR = MODEL / "manifest.json"
RUNTIME_MANIFEST = MODEL / "manifests" / "runtime.json"
INGEST_MANIFEST = MODEL / "manifests" / "ingest.json"
FIXTURES = MODEL / "runtime" / "fixtures.json"
STALE_ARTIFACT = MODEL / "10_single_file_master_prompt.txt"


class ValidationError(RuntimeError):
    pass


def load_json(path: pathlib.Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot parse {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def validate_selector() -> None:
    selector = load_json(DEFAULT_SELECTOR)
    require(
        selector.get("default_manifest") == "manifests/runtime.json",
        "model/manifest.json must be a selector for manifests/runtime.json",
    )
    require("source_files" not in selector, "default selector must not duplicate a load graph")


def validate_manifest(path: pathlib.Path) -> dict:
    manifest = load_json(path)
    source_files = manifest.get("source_files")
    domain_modules = manifest.get("domain_modules", [])
    generated = manifest.get("generated")

    require(isinstance(source_files, list) and source_files, f"{path.name}: source_files missing")
    require(isinstance(domain_modules, list), f"{path.name}: domain_modules must be a list")
    require(isinstance(generated, list) and len(generated) == 1, f"{path.name}: exactly one generated target required")

    inputs = source_files + domain_modules
    require(len(inputs) == len(set(inputs)), f"{path.name}: duplicate runtime input")
    require(not set(inputs) & set(generated), f"{path.name}: generated target appears in runtime inputs")

    for relative in inputs:
        require((MODEL / relative).is_file(), f"{path.name}: missing model/{relative}")
    return manifest


def run_build(path: pathlib.Path) -> pathlib.Path:
    subprocess.run([sys.executable, str(BUILDER), str(path)], cwd=ROOT, check=True)
    manifest = load_json(path)
    output = MODEL / manifest["generated"][0]
    require(output.is_file(), f"build did not create {output.relative_to(ROOT)}")
    return output


def validate_output(output: pathlib.Path, manifest: dict, expect_support: bool) -> None:
    text = output.read_text(encoding="utf-8")
    require(text.endswith("\n"), f"{output.relative_to(ROOT)} lacks trailing newline")
    require("cartridges/neuroscience.yaml" in text, f"{output.relative_to(ROOT)} omits neuroscience cartridge")
    require("neuroscience_cartridge:" in text, f"{output.relative_to(ROOT)} does not embed cartridge content")
    require("Live specification: github.com/Remodeled-Brain/The-Model" in text, "provenance/reach footer missing")
    if expect_support:
        require("model/manifests/ingest.json" in text, "runtime omits reachable ingest manifest")
    if manifest.get("reachable_modules"):
        require("decisions/0003-concurrent-ingest.md" in text, "ingest runtime omits distributed-ingest reach")


def validate_fixtures() -> None:
    fixtures = load_json(FIXTURES)
    required_answer_fields = fixtures.get("required_answer_fields")
    records = fixtures.get("fixtures")
    require(isinstance(required_answer_fields, list) and required_answer_fields, "fixture answer schema missing")
    require(isinstance(records, list) and records, "fixtures list missing")

    ids: set[str] = set()
    for record in records:
        require(isinstance(record, dict), "fixture entries must be objects")
        fixture_id = record.get("id")
        require(isinstance(fixture_id, str) and fixture_id, "fixture id missing")
        require(fixture_id not in ids, f"duplicate fixture id: {fixture_id}")
        ids.add(fixture_id)
        require(record.get("mode") in {"question", "condition"}, f"{fixture_id}: invalid mode")
        require(isinstance(record.get("required"), list) and record["required"], f"{fixture_id}: required contract missing")
        require(isinstance(record.get("forbidden"), list) and record["forbidden"], f"{fixture_id}: forbidden contract missing")
        if record["mode"] == "question":
            require(isinstance(record.get("source_question"), str), f"{fixture_id}: source_question missing")
        else:
            require(isinstance(record.get("condition"), str), f"{fixture_id}: condition missing")


def validate_cleanup() -> None:
    require(not STALE_ARTIFACT.exists(), "stale model/10_single_file_master_prompt.txt still exists")


def validate_trailing_newlines() -> None:
    paths = [
        ROOT / "README.md",
        ROOT / "changelog.d" / "2026-07-10-chatgpt-question-runtime-refactor.md",
        MODEL / "00_purpose_and_scope.md",
        MODEL / "kernel" / "chain_contract.yaml",
        MODEL / "manifest.json",
        RUNTIME_MANIFEST,
        INGEST_MANIFEST,
        MODEL / "runtime" / "question_compiler.yaml",
        MODEL / "runtime" / "answerability_planner.yaml",
        MODEL / "runtime" / "evidence_binding_contract.yaml",
        MODEL / "runtime" / "answer_contract.yaml",
        FIXTURES,
        BUILDER,
        pathlib.Path(__file__),
    ]
    for path in paths:
        require(path.read_bytes().endswith(b"\n"), f"{path.relative_to(ROOT)} lacks trailing newline")


def main() -> int:
    generated: list[pathlib.Path] = []
    try:
        validate_selector()
        runtime = validate_manifest(RUNTIME_MANIFEST)
        ingest = validate_manifest(INGEST_MANIFEST)
        validate_fixtures()
        validate_cleanup()
        validate_trailing_newlines()

        runtime_output = run_build(RUNTIME_MANIFEST)
        generated.append(runtime_output)
        validate_output(runtime_output, runtime, expect_support=True)

        ingest_output = run_build(INGEST_MANIFEST)
        generated.append(ingest_output)
        validate_output(ingest_output, ingest, expect_support=False)
    except (ValidationError, subprocess.CalledProcessError, OSError) as exc:
        print(f"VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1
    finally:
        for output in generated:
            output.unlink(missing_ok=True)
        dist = MODEL / "dist"
        if dist.exists() and not any(dist.iterdir()):
            dist.rmdir()

    print("repository validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
