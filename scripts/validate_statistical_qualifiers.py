#!/usr/bin/env python3
"""Validate shared statistical qualifiers, neuroscience extensions, and quantitative fixtures."""
from __future__ import annotations

import json
import math
import pathlib
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = ROOT / "model"
POLICY = MODEL / "kernel" / "statistical_qualifiers.yaml"
FIXTURES = MODEL / "kernel" / "statistical_qualifier_fixtures.json"
NEURO = MODEL / "cartridges" / "neuroscience.yaml"
NEURO_FIXTURES = MODEL / "cartridges" / "neuroscience_fixtures.json"
MANIFESTS = (
    MODEL / "manifests" / "runtime.json",
    MODEL / "manifests" / "ingest.json",
)
POLICY_REF = "kernel/statistical_qualifiers.yaml"
FIXTURE_REF = "kernel/statistical_qualifier_fixtures.json"


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


def overlap_from_d(effect: float) -> float:
    return 2.0 * normal_cdf(-abs(effect) / 2.0)


def idealized_balanced_accuracy_from_d(effect: float) -> float:
    return normal_cdf(abs(effect) / 2.0)


def design_effect(mean_cluster_size: float, intraclass_correlation: float) -> float:
    return 1.0 + (mean_cluster_size - 1.0) * intraclass_correlation


def positive_predictive_value(prevalence: float, sensitivity: float, specificity: float) -> float:
    numerator = sensitivity * prevalence
    denominator = numerator + (1.0 - specificity) * (1.0 - prevalence)
    require(denominator > 0.0, "positive predictive value denominator must be positive")
    return numerator / denominator


def validate_manifest_reachability() -> None:
    for path in MANIFESTS:
        manifest = load_json(path)
        sources = manifest.get("source_files")
        require(isinstance(sources, list), f"{path.name}: source_files missing")
        require(POLICY_REF in sources, f"{path.name}: statistical qualifier policy is not reachable")
        require(FIXTURE_REF in sources, f"{path.name}: statistical qualifier fixtures are not reachable")
        require(sources.index(POLICY_REF) < sources.index(FIXTURE_REF), f"{path.name}: policy must precede fixtures")


def validate_policy() -> None:
    text = POLICY.read_text(encoding="utf-8")
    required_fragments = (
        "information_and_dependence:",
        "magnitude_and_precision:",
        "distributional_separation:",
        "classification_information:",
        "pipeline_isolation_and_selection:",
        "optimism_ledger:",
        "resampling_stability:",
        "learning_curve_and_assurance:",
        "calibration_and_proper_scoring:",
        "multiplicity_and_researcher_selection:",
        "transport_distribution:",
        "No universal sample-size, accuracy, overlap, AUC, calibration, or feature-count cutoff applies across claims.",
        "Accuracy alone receives no support weight.",
        "Stable average performance cannot rescue unstable individual assignments.",
        "One external validation establishes performance in one additional setting rather than universal validation.",
        "2 * Phi(-abs(d) / 2)",
        "Phi(abs(d) / 2)",
    )
    for fragment in required_fragments:
        require(fragment in text, f"statistical qualifier policy missing required fragment: {fragment}")
    require("http://" not in text and "https://" not in text, "statistical qualifier policy must remain resource-neutral")


def validate_fixtures() -> None:
    data = load_json(FIXTURES)
    require(data.get("schema_version") == "v1", "statistical fixture schema_version must be v1")
    require(data.get("fixture_set") == "statistical_qualifiers", "statistical fixture_set mismatch")
    fixtures = data.get("fixtures")
    require(isinstance(fixtures, list) and fixtures, "statistical fixtures missing")
    required_ids = {
        "nominal_rows_do_not_create_independent_n",
        "cluster_design_effect_reduces_information",
        "tiny_precise_effect_remains_tiny",
        "small_group_effect_blocks_individual_separator",
        "raw_accuracy_without_confusion_matrix_is_unresolved",
        "balanced_case_control_accuracy_does_not_supply_deployment_ppv",
        "global_preprocessing_invalidates_internal_test",
        "stable_average_cannot_rescue_unstable_people",
        "small_sample_peak_that_declines_is_optimism_evidence",
        "one_external_setting_does_not_establish_transport_distribution",
        "good_discrimination_does_not_supply_calibration",
        "selected_winner_from_unreported_search_has_unresolved_optimism",
    }
    ids: set[str] = set()
    for fixture in fixtures:
        require(isinstance(fixture, dict), "statistical fixture must be an object")
        fixture_id = fixture.get("id")
        require(isinstance(fixture_id, str) and fixture_id, "statistical fixture id missing")
        require(fixture_id not in ids, f"duplicate statistical fixture id: {fixture_id}")
        ids.add(fixture_id)
        values = fixture.get("input")
        expected = fixture.get("expected")
        require(isinstance(values, dict), f"{fixture_id}: input missing")
        require(isinstance(expected, dict), f"{fixture_id}: expected missing")

        if fixture_id == "cluster_design_effect_reduces_information":
            deff = design_effect(float(values["mean_cluster_size"]), float(values["intraclass_correlation"]))
            effective_n = float(values["nominal_n"]) / deff
            require(math.isclose(deff, float(expected["design_effect"]), rel_tol=1e-9), f"{fixture_id}: design effect mismatch")
            require(math.isclose(effective_n, float(expected["effective_n"]), rel_tol=1e-9), f"{fixture_id}: effective n mismatch")

        if fixture_id == "small_group_effect_blocks_individual_separator":
            effect = float(values["effect_value"])
            overlap = overlap_from_d(effect)
            balanced = idealized_balanced_accuracy_from_d(effect)
            require(float(expected["overlap_coefficient_min"]) <= overlap <= float(expected["overlap_coefficient_max"]), f"{fixture_id}: overlap outside range")
            require(float(expected["idealized_balanced_accuracy_min"]) <= balanced <= float(expected["idealized_balanced_accuracy_max"]), f"{fixture_id}: idealized balanced accuracy outside range")

        if fixture_id == "balanced_case_control_accuracy_does_not_supply_deployment_ppv":
            ppv = positive_predictive_value(
                float(values["deployment_prevalence"]),
                float(values["sensitivity"]),
                float(values["specificity"]),
            )
            require(float(expected["deployment_positive_predictive_value_min"]) <= ppv <= float(expected["deployment_positive_predictive_value_max"]), f"{fixture_id}: deployment PPV outside range")

    require(required_ids <= ids, f"statistical fixtures missing: {sorted(required_ids - ids)}")
    raw = FIXTURES.read_text(encoding="utf-8")
    require("http://" not in raw and "https://" not in raw, "statistical fixtures must remain resource-neutral")


def validate_neuroscience_extension() -> None:
    text = NEURO.read_text(encoding="utf-8")
    required_fragments = (
        "quantitative_neuroscience_policy:",
        "independent_unit_hierarchy:",
        "split_and_pipeline_isolation:",
        "nuisance_baselines:",
        "measurement_reliability:",
        "circular_localization:",
        "group_effect_classifier_consistency:",
        "full_pipeline_permutation:",
        "leave_site_scanner_cohort_or_time_out",
        "voxels_trials_time_points_scans_or_augmented_images_as_independent_population_n",
    )
    for fragment in required_fragments:
        require(fragment in text, f"neuroscience cartridge missing statistical extension: {fragment}")

    data = load_json(NEURO_FIXTURES)
    fixtures = data.get("fixtures")
    require(isinstance(fixtures, list), "neuroscience fixtures missing")
    fixture_ids = {item.get("id") for item in fixtures if isinstance(item, dict)}
    required_ids = {
        "neuro-classifier-row-leakage",
        "neuro-nuisance-only-classifier",
        "neuro-small-effect-high-classifier-contradiction",
        "neuro-reliability-ceiling",
        "neuro-full-pipeline-permutation",
    }
    require(required_ids <= fixture_ids, f"neuroscience statistical fixtures missing: {sorted(required_ids - fixture_ids)}")


def main() -> int:
    try:
        validate_manifest_reachability()
        validate_policy()
        validate_fixtures()
        validate_neuroscience_extension()
    except (ValidationError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"STATISTICAL QUALIFIER VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1
    print("statistical qualifier validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
