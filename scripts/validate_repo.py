#!/usr/bin/env python3
"""Validate active repository structure, shared vocabularies, builds, and fixtures."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
from collections.abc import Iterable
from typing import Any

VALIDATOR = pathlib.Path(__file__).resolve()
ROOT = VALIDATOR.parents[1]
MODEL = ROOT / "model"
BUILDER = ROOT / "scripts" / "build_master_prompt.py"
DEFAULT_SELECTOR = MODEL / "manifest.json"
RUNTIME_MANIFEST = MODEL / "manifests" / "runtime.json"
INGEST_MANIFEST = MODEL / "manifests" / "ingest.json"
KERNEL = MODEL / "kernel" / "chain_contract.yaml"
ANSWER_CONTRACT = MODEL / "runtime" / "answer_contract.yaml"
EVIDENCE_BINDER = MODEL / "runtime" / "evidence_binding_contract.yaml"
FAILURE_ROUTING = MODEL / "ingest" / "failure_routing.yaml"
RUNTIME_FIXTURES = MODEL / "runtime" / "fixtures.json"
INGEST_FIXTURES = MODEL / "ingest" / "fixtures.json"
CLOSURE_REF = "model/kernel/chain_contract.yaml#chain_contract.closure_vocabulary.states"
CROSSWALK_REF = "model/ingest/failure_routing.yaml#ingest_failure_routing.closure_state_crosswalk"
REPOSITORY = "github.com/Remodeled-Brain/The-Model"

LEGACY_PATHS = [
    MODEL / "00_readme_for_llms.md",
    MODEL / "01_version_goals_and_non_goals.md",
    MODEL / "02_runtime_behavior_contract.md",
    MODEL / "03_ingest_architecture.yaml",
    MODEL / "04_candidate_rule_adoption_gate.yaml",
    MODEL / "05_failure_semantics_and_weight_caps.yaml",
    MODEL / "06_candidate_ingest_rules_reference.yaml",
    MODEL / "07_fixtures_and_regression_tests.md",
    MODEL / "08_prompt_harness.md",
    MODEL / "09_changelog_candidate.md",
    MODEL / "10_single_file_master_prompt.txt",
    MODEL / "record_schema_v1.yaml",
]
STALE_REFERENCES = [path.relative_to(ROOT).as_posix() for path in LEGACY_PATHS]
ACTIVE_REFERENCE_ROOTS = [
    ROOT / "README.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "AGENTS.md",
    ROOT / "CLAUDE.md",
    ROOT / "GEMINI.md",
    ROOT / "FABLE.md",
    ROOT / "model",
    ROOT / "governance",
    ROOT / "providers",
    ROOT / "scripts",
    ROOT / ".github",
]


class ValidationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def load_json(path: pathlib.Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot parse {path.relative_to(ROOT)}: {exc}") from exc
    require(isinstance(value, dict), f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def tracked_files() -> list[pathlib.Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    )
    return [ROOT / value.decode("utf-8") for value in result.stdout.split(b"\0") if value]


def yaml_lines(path: pathlib.Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def indentation(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def find_yaml_key(lines: list[str], key: str) -> tuple[int, int]:
    target = f"{key}:"
    for index, line in enumerate(lines):
        if line.strip() == target:
            return index, indentation(line)
    raise ValidationError(f"YAML key {key!r} not found")


def yaml_list(path: pathlib.Path, key: str) -> list[str]:
    lines = yaml_lines(path)
    index, parent_indent = find_yaml_key(lines, key)
    values: list[str] = []
    for line in lines[index + 1 :]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        level = indentation(line)
        if level <= parent_indent:
            break
        if level == parent_indent + 2 and stripped.startswith("- "):
            values.append(stripped[2:].strip().strip('"\''))
    require(values, f"{path.relative_to(ROOT)}:{key} must contain a list")
    return values


def yaml_mapping(path: pathlib.Path, key: str) -> dict[str, str]:
    lines = yaml_lines(path)
    index, parent_indent = find_yaml_key(lines, key)
    values: dict[str, str] = {}
    for line in lines[index + 1 :]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        level = indentation(line)
        if level <= parent_indent:
            break
        if level != parent_indent + 2 or ":" not in stripped:
            continue
        name, raw = stripped.split(":", 1)
        value = raw.strip().strip('"\'')
        if value and value not in {">", "|"}:
            values[name.strip()] = value
    require(values, f"{path.relative_to(ROOT)}:{key} must contain a mapping")
    return values


def yaml_scalar(path: pathlib.Path, key: str) -> str:
    target = f"{key}:"
    for line in yaml_lines(path):
        stripped = line.strip()
        if stripped.startswith(target):
            value = stripped[len(target) :].strip().strip('"\'')
            if value:
                return value
    raise ValidationError(f"YAML scalar {key!r} not found in {path.relative_to(ROOT)}")


def validate_selector() -> None:
    selector = load_json(DEFAULT_SELECTOR)
    require(
        selector.get("default_manifest") == "manifests/runtime.json",
        "model/manifest.json must select manifests/runtime.json",
    )
    require("source_files" not in selector, "default selector must not duplicate a load graph")
    require("generated" not in selector, "default selector must not duplicate build outputs")


def validate_manifest(path: pathlib.Path) -> dict[str, Any]:
    manifest = load_json(path)
    source_files = manifest.get("source_files")
    domain_modules = manifest.get("domain_modules", [])
    support_manifests = manifest.get("support_manifests", [])
    reachable_modules = manifest.get("reachable_modules", [])
    generated = manifest.get("generated")

    require(isinstance(source_files, list) and source_files, f"{path.name}: source_files missing")
    require(isinstance(domain_modules, list), f"{path.name}: domain_modules must be a list")
    require(isinstance(support_manifests, list), f"{path.name}: support_manifests must be a list")
    require(isinstance(reachable_modules, list), f"{path.name}: reachable_modules must be a list")
    require(isinstance(generated, list) and len(generated) == 1, f"{path.name}: exactly one generated target required")

    inputs = source_files + domain_modules
    require(len(inputs) == len(set(inputs)), f"{path.name}: duplicate runtime input")
    require(not set(inputs) & set(generated), f"{path.name}: generated target appears in inputs")

    for relative in inputs:
        require(isinstance(relative, str) and relative, f"{path.name}: invalid input path")
        require((MODEL / relative).is_file(), f"{path.name}: missing model/{relative}")
    for relative in support_manifests:
        require((MODEL / relative).is_file(), f"{path.name}: missing support manifest model/{relative}")
    for record in reachable_modules:
        require(isinstance(record, dict), f"{path.name}: reachable module must be an object")
        relative = record.get("path")
        require(isinstance(relative, str) and relative, f"{path.name}: reachable module path missing")
        require((MODEL / relative).resolve().is_file(), f"{path.name}: missing reachable module {relative}")
    return manifest


def iter_active_reference_files() -> Iterable[pathlib.Path]:
    tracked = set(tracked_files())
    for root in ACTIVE_REFERENCE_ROOTS:
        if root.is_file():
            if root in tracked and root.resolve() != VALIDATOR:
                yield root
            continue
        if root.is_dir():
            for path in root.rglob("*"):
                if path.is_file() and path in tracked and path.resolve() != VALIDATOR:
                    yield path


def validate_closure_vocabulary() -> None:
    states = yaml_list(KERNEL, "states")
    require(len(states) == len(set(states)), "kernel closure vocabulary contains duplicate states")
    require("contested" in states, "kernel closure vocabulary must own contested")
    require("unresolved" in states, "kernel closure vocabulary must own unresolved")

    answer_text = ANSWER_CONTRACT.read_text(encoding="utf-8")
    binder_text = EVIDENCE_BINDER.read_text(encoding="utf-8")
    routing_text = FAILURE_ROUTING.read_text(encoding="utf-8")
    require(CLOSURE_REF in answer_text, "answer contract does not reference kernel closure vocabulary")
    require(CLOSURE_REF in binder_text, "evidence binder does not reference kernel closure vocabulary")
    require(CLOSURE_REF in routing_text, "ingest routing does not reference kernel closure vocabulary")
    require(CROSSWALK_REF in binder_text, "evidence binder does not reference ingest closure crosswalk")

    channels = yaml_list(FAILURE_ROUTING, "support_channels")
    crosswalk = yaml_mapping(FAILURE_ROUTING, "channels")
    require(set(crosswalk) == set(channels), "ingest closure crosswalk must cover every support channel exactly once")
    unknown = sorted(set(crosswalk.values()) - set(states))
    require(not unknown, f"ingest closure crosswalk targets unknown kernel states: {unknown}")

    conflict_state = yaml_scalar(EVIDENCE_BINDER, "surviving_conflict_state")
    require(conflict_state == "contested", "surviving evidence conflict must use contested")
    require(conflict_state in states, "binder conflict state is absent from kernel vocabulary")

    for path in iter_active_reference_files():
        if path == KERNEL or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        require("closure_states:" not in text, f"closure enum redefined outside kernel: {path.relative_to(ROOT)}")


def run_build(manifest_path: pathlib.Path | None) -> pathlib.Path:
    command = [sys.executable, str(BUILDER)]
    if manifest_path is not None:
        command.append(str(manifest_path))
    subprocess.run(command, cwd=ROOT, check=True)
    manifest = load_json(RUNTIME_MANIFEST if manifest_path is None else manifest_path)
    output = MODEL / manifest["generated"][0]
    require(output.is_file(), f"build did not create {output.relative_to(ROOT)}")
    return output


def parse_markers(text: str) -> dict[str, Any]:
    markers: dict[str, Any] = {}
    prefix = "# @model."
    for line in text.splitlines():
        if not line.startswith(prefix) or "=" not in line:
            continue
        name, raw = line[len(prefix) :].split("=", 1)
        try:
            markers[name] = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"invalid generated metadata marker {name}: {exc}") from exc
    return markers


def expected_reachable_paths(manifest: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for record in manifest.get("reachable_modules", []):
        path = (MODEL / record["path"]).resolve()
        paths.append(path.relative_to(ROOT).as_posix())
    return paths


def validate_output(output: pathlib.Path, manifest_path: pathlib.Path, manifest: dict[str, Any]) -> None:
    text = output.read_text(encoding="utf-8")
    markers = parse_markers(text)
    require(text.endswith("\n"), f"{output.relative_to(ROOT)} lacks trailing newline")
    require(markers.get("repository") == REPOSITORY, "generated runtime repository metadata is wrong")
    require(markers.get("named_modules_only") is True, "generated runtime named-module guard is absent")
    require(
        markers.get("authoritative_manifest") == manifest_path.relative_to(ROOT).as_posix(),
        "generated runtime authoritative-manifest metadata is wrong",
    )
    require(markers.get("domain_modules") == manifest.get("domain_modules", []), "generated runtime domain metadata drifted")
    require(markers.get("support_manifests") == manifest.get("support_manifests", []), "generated runtime support metadata drifted")
    require(markers.get("reachable_modules") == expected_reachable_paths(manifest), "generated runtime reachable-module metadata drifted")

    for name in manifest["source_files"]:
        require(f"===== SOURCE: {name} =====" in text, f"generated runtime omits source {name}")
    for name in manifest.get("domain_modules", []):
        require(f"===== DOMAIN MODULE: {name} =====" in text, f"generated runtime omits domain module {name}")


def validate_runtime_fixtures() -> None:
    data = load_json(RUNTIME_FIXTURES)
    required_answer_fields = data.get("required_answer_fields")
    fixtures = data.get("fixtures")
    require(isinstance(required_answer_fields, list) and required_answer_fields, "runtime answer schema missing")
    require(isinstance(fixtures, list) and fixtures, "runtime fixtures missing")
    ids: set[str] = set()
    for fixture in fixtures:
        require(isinstance(fixture, dict), "runtime fixture must be an object")
        fixture_id = fixture.get("id")
        require(isinstance(fixture_id, str) and fixture_id, "runtime fixture id missing")
        require(fixture_id not in ids, f"duplicate runtime fixture id: {fixture_id}")
        ids.add(fixture_id)
        require(fixture.get("mode") in {"question", "condition"}, f"{fixture_id}: invalid mode")
        require(isinstance(fixture.get("required"), list) and fixture["required"], f"{fixture_id}: required contract missing")
        require(isinstance(fixture.get("forbidden"), list) and fixture["forbidden"], f"{fixture_id}: forbidden contract missing")
        field = "source_question" if fixture["mode"] == "question" else "condition"
        require(isinstance(fixture.get(field), str) and fixture[field], f"{fixture_id}: {field} missing")


def validate_ingest_fixtures() -> None:
    data = load_json(INGEST_FIXTURES)
    sections = data.get("required_record_sections")
    fixtures = data.get("fixtures")
    require(isinstance(sections, list) and sections, "ingest record sections missing")
    require(isinstance(fixtures, list) and fixtures, "ingest fixtures missing")
    ids: set[str] = set()
    valid_channels = set(yaml_list(FAILURE_ROUTING, "support_channels"))
    for fixture in fixtures:
        require(isinstance(fixture, dict), "ingest fixture must be an object")
        fixture_id = fixture.get("id")
        require(isinstance(fixture_id, str) and fixture_id, "ingest fixture id missing")
        require(fixture_id not in ids, f"duplicate ingest fixture id: {fixture_id}")
        ids.add(fixture_id)
        for field in ("source_pattern", "required_gates", "allowed_channels", "blocked_roles"):
            require(fixture.get(field) not in (None, "", []), f"{fixture_id}: {field} missing")
        unknown = sorted(set(fixture["allowed_channels"]) - valid_channels)
        require(not unknown, f"{fixture_id}: unknown ingest support channels: {unknown}")


def validate_cleanup() -> None:
    for path in LEGACY_PATHS:
        require(not path.exists(), f"legacy active file still exists: {path.relative_to(ROOT)}")
    tracked = tracked_files()
    tracked_dist = [path for path in tracked if path.is_relative_to(MODEL / "dist")]
    require(not tracked_dist, "generated model/dist artifacts must not be tracked")
    failures: list[str] = []
    for path in iter_active_reference_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for stale in STALE_REFERENCES:
            if stale in text:
                failures.append(f"{path.relative_to(ROOT)} -> {stale}")
    require(not failures, "stale active references:\n  " + "\n  ".join(failures))


def validate_trailing_newlines() -> None:
    roots = [
        ROOT / "README.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "AGENTS.md",
        ROOT / "CLAUDE.md",
        ROOT / "GEMINI.md",
        ROOT / "FABLE.md",
        ROOT / ".gitignore",
        ROOT / ".github",
        ROOT / "governance",
        MODEL / "00_purpose_and_scope.md",
        MODEL / "kernel",
        MODEL / "runtime",
        MODEL / "ingest",
        MODEL / "cartridges",
        MODEL / "manifest.json",
        MODEL / "manifests",
        BUILDER,
        VALIDATOR,
    ]
    tracked = set(tracked_files())
    for root in roots:
        paths = [root] if root.is_file() else [path for path in root.rglob("*") if path.is_file()]
        for path in paths:
            if path not in tracked:
                continue
            content = path.read_bytes()
            try:
                content.decode("utf-8")
            except UnicodeDecodeError:
                continue
            require(content.endswith(b"\n"), f"{path.relative_to(ROOT)} lacks trailing newline")


def main() -> int:
    generated: list[pathlib.Path] = []
    try:
        validate_selector()
        runtime = validate_manifest(RUNTIME_MANIFEST)
        ingest = validate_manifest(INGEST_MANIFEST)
        validate_closure_vocabulary()
        validate_runtime_fixtures()
        validate_ingest_fixtures()
        validate_cleanup()
        validate_trailing_newlines()

        runtime_output = run_build(None)
        generated.append(runtime_output)
        validate_output(runtime_output, RUNTIME_MANIFEST, runtime)

        ingest_output = run_build(INGEST_MANIFEST)
        generated.append(ingest_output)
        validate_output(ingest_output, INGEST_MANIFEST, ingest)
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
