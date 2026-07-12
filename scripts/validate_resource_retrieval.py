#!/usr/bin/env python3
"""Validate external-resource retrieval policy, manifest reachability, and quantitative fixtures."""
from __future__ import annotations

import json
import math
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


def normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


def overlap_from_standardized_mean_difference(effect: float) -> float:
    return 2.0 * normal_cdf(-abs(effect) / 2.0)


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
        "freshness_policy:",
        "source_selection:",
        "universal_admission_rule:",
        "provider_memory_policy:",
        "quantitative_extraction:",
        "premise_rejection_retrieval_scope:",
        "retrieval_to_answer_contract:",
        "Retrieval changes availability, not admissibility.",
        "Provider memory is a lead generator, not admitted evidence.",
        "overlap_coefficient = 2 * Phi(-abs(d) / 2)",
        "Statistical significance cannot substitute for magnitude",
        "Premise rejection terminates only retrieval that requires or attempts to restore the failed entity.",
    )
    for fragment in required_fragments:
        require(fragment in text, f"retrieval policy missing required fragment: {fragment}")
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
        "provider_memory_is_unverified",
        "recent_summary_does_not_outrank_primary_data",
        "small_standardized_difference_requires_overlap",
        "incompatible_metric_keeps_overlap_open",
        "premise_rejection_does_not_stop_narrow_retrieval",
        "downstream_association_cannot_rescue_failed_construct",
    }
    for fixture in fixtures:
        require(isinstance(fixture, dict), "retrieval fixture must be an object")
        fixture_id = fixture.get("id")
        require(isinstance(fixture_id, str) and fixture_id, "retrieval fixture id missing")
        require(fixture_id not in ids, f"duplicate retrieval fixture id: {fixture_id}")
        ids.add(fixture_id)
        require(isinstance(fixture.get("input"), dict), f"{fixture_id}: input missing")
        require(isinstance(fixture.get("expected"), dict), f"{fixture_id}: expected missing")

        values = fixture["input"]
        expected = fixture["expected"]
        if values.get("effect_metric") == "standardized_mean_difference":
            require(values.get("approximately_normal") is True, f"{fixture_id}: normality assumption required")
            require(values.get("equal_variance") is True, f"{fixture_id}: equal-variance assumption required")
            effect = values.get("effect_value")
            require(isinstance(effect, (int, float)), f"{fixture_id}: numeric effect required")
            overlap = overlap_from_standardized_mean_difference(float(effect))
            lower = expected.get("overlap_coefficient_min")
            upper = expected.get("overlap_coefficient_max")
            require(isinstance(lower, (int, float)) and isinstance(upper, (int, float)), f"{fixture_id}: overlap bounds required")
            require(float(lower) <= overlap <= float(upper), f"{fixture_id}: overlap {overlap:.6f} outside expected range")
            require(expected.get("statistical_significance_overrides_overlap") is False, f"{fixture_id}: significance must not override overlap")

        if values.get("effect_metric") not in {None, "standardized_mean_difference"}:
            require(expected.get("compute_normal_overlap_approximation") is False, f"{fixture_id}: incompatible metric used for normal overlap")

    require(required_ids <= ids, f"retrieval fixtures missing: {sorted(required_ids - ids)}")
    raw = FIXTURES.read_text(encoding="utf-8")
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
