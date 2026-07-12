#!/usr/bin/env python3
"""Validate external-resource retrieval policy, source boundaries, and manifest reachability."""
from __future__ import annotations

import json
import pathlib
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = ROOT / "model"
POLICY = MODEL / "kernel" / "resource_retrieval.yaml"
FIXTURES = MODEL / "kernel" / "resource_retrieval_fixtures.json"
MANIFESTS = (
    MODEL / "manifests" / "runtime.json",
    MODEL / "manifests" / "ingest.json",
)
POLICY_REF = "kernel/resource_retrieval.yaml"
FIXTURE_REF = "kernel/resource_retrieval_fixtures.json"


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
    require(isinstance(value, dict), f"{path.relative_to(ROOT)} must contain an object")
    return value


def validate_manifest_reachability() -> None:
    for path in MANIFESTS:
        manifest = load_json(path)
        sources = manifest.get("source_files")
        require(isinstance(sources, list), f"{path.name}: source_files missing")
        require(POLICY_REF in sources, f"{path.name}: retrieval policy is not reachable")
        require(FIXTURE_REF in sources, f"{path.name}: retrieval fixtures are not reachable")
        require(sources.index(POLICY_REF) < sources.index(FIXTURE_REF), f"{path.name}: policy must precede fixtures")


def validate_policy() -> None:
    text = POLICY.read_text(encoding="utf-8")
    required_fragments = (
        "retrieval_permission:",
        "user_source_boundary:",
        "freshness_policy:",
        "source_selection:",
        "universal_admission_rule:",
        "provider_memory_policy:",
        "quantitative_extraction:",
        "qualifier_ref: model/kernel/statistical_qualifiers.yaml",
        "premise_rejection_retrieval_scope:",
        "retrieval_to_answer_contract:",
        "Retrieval changes availability, not admissibility.",
        "Provider memory is a lead generator, not admitted evidence.",
        "Do not cross a user-imposed source boundary unless the user explicitly relaxes it.",
        "Pass those inputs to the shared",
        "statistical qualifier kernel.",
        "Premise rejection terminates only retrieval that requires or attempts to restore the failed entity.",
    )
    for fragment in required_fragments:
        require(fragment in text, f"retrieval policy missing required fragment: {fragment}")
    require("overlap_coefficient =" not in text, "retrieval policy must delegate overlap calculation to statistical qualifiers")
    require("http://" not in text and "https://" not in text, "retrieval policy must remain resource-neutral")


def validate_fixtures() -> None:
    data = load_json(FIXTURES)
    require(data.get("schema_version") == "v1", "retrieval fixture schema_version must be v1")
    require(data.get("fixture_set") == "resource_retrieval", "retrieval fixture_set mismatch")
    fixtures = data.get("fixtures")
    require(isinstance(fixtures, list) and fixtures, "retrieval fixtures missing")
    ids: set[str] = set()
    required_ids = {
        "external_retrieval_is_allowed",
        "user_source_boundary_controls_retrieval",
        "provider_memory_is_unverified",
        "recent_summary_does_not_outrank_primary_data",
        "quantitative_retrieval_delegates_qualification",
        "premise_rejection_does_not_stop_narrow_retrieval",
        "downstream_association_cannot_rescue_failed_construct",
    }
    for fixture in fixtures:
        require(isinstance(fixture, dict), "retrieval fixture must be an object")
        fixture_id = fixture.get("id")
        require(isinstance(fixture_id, str) and fixture_id, "retrieval fixture id missing")
        require(fixture_id not in ids, f"duplicate retrieval fixture id: {fixture_id}")
        ids.add(fixture_id)
        values = fixture.get("input")
        expected = fixture.get("expected")
        require(isinstance(values, dict), f"{fixture_id}: input missing")
        require(isinstance(expected, dict), f"{fixture_id}: expected missing")

        if fixture_id == "user_source_boundary_controls_retrieval":
            require(expected.get("retrieve_outside_supplied_files") is False, f"{fixture_id}: user source boundary must control retrieval")
            require(expected.get("claim_status") == "unresolved", f"{fixture_id}: unresolved claim required when bounded corpus is insufficient")

        if fixture_id == "quantitative_retrieval_delegates_qualification":
            require(expected.get("delegate_to_statistical_qualifiers") is True, f"{fixture_id}: statistical delegation required")
            require(expected.get("interpret_evidentiary_weight_inside_retrieval") is False, f"{fixture_id}: retrieval must not interpret statistical weight")

    require(required_ids <= ids, f"retrieval fixtures missing: {sorted(required_ids - ids)}")
    raw = FIXTURES.read_text(encoding="utf-8")
    require("overlap_coefficient" not in raw, "retrieval fixtures must delegate overlap calculation")
    require("http://" not in raw and "https://" not in raw, "retrieval fixtures must remain resource-neutral")


def main() -> int:
    try:
        validate_manifest_reachability()
        validate_policy()
        validate_fixtures()
    except (ValidationError, OSError) as exc:
        print(f"RESOURCE RETRIEVAL VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1
    print("resource retrieval validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
