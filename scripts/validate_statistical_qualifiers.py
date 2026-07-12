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
CHAIN = MODEL / "kernel" / "chain_contract.yaml"
POLICY = MODEL / "kernel" / "statistical_qualifiers.yaml"
FIXTURES = MODEL / "kernel" / "statistical_qualifier_fixtures.json"
NEURO = MODEL / "cartridges" / "neuroscience_statistics.yaml"
NEURO_FIXTURES = MODEL / "cartridges" / "neuroscience_statistical_fixtures.json"
MANIFESTS = (
    MODEL / "manifests" / "runtime.json",
    MODEL / "manifests" / "ingest.json",
)
POLICY_REF = "kernel/statistical_qualifiers.yaml"
FIXTURE_REF = "kernel/statistical_qualifier_fixtures.json"
NEURO_REF = "cartridges/neuroscience_statistics.yaml"
NEURO_FIXTURE_REF = "cartridges/neuroscience_statistical_fixtures.json"

REFINABLE_KERNEL_SECTIONS = {
    "information_and_dependence",
    "magnitude_and_precision",
    "distributional_separation",
    "classification_information",
    "pipeline_isolation_and_selection",
    "optimism_ledger",
    "resampling_stability",
    "learning_curve_and_assurance",
    "calibration_and_proper_scoring",
    "multiplicity_and_researcher_selection",
    "transport_distribution",
}
REQUIRED_NEURO_REFINEMENTS = {
    "independent_unit_hierarchy",
    "split_and_pipeline_isolation",
    "nuisance_baselines",
    "measurement_reliability",
    "circular_localization",
    "group_effect_classifier_consistency",
    "full_pipeline_permutation",
    "imaging_and_signal_specific_checks",
    "label_selected_sample_rule",
}
REQUIRED_BASIS_CODES = {
    "supported_by_reported_data",
    "missing_reporting",
    "insufficient_independent_information",
    "incompatible_design",
    "observed_overlap",
    "observed_instability",
    "observed_optimism",
    "observed_calibration_failure",
    "observed_transport_failure",
    "observed_multiplicity_failure",
    "not_applicable",
}


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


def line_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def find_block(
    lines: list[str],
    key: str,
    *,
    start: int = 0,
    end: int | None = None,
) -> tuple[int, int, int]:
    limit = len(lines) if end is None else end
    for index in range(start, limit):
        if lines[index].strip() != f"{key}:":
            continue
        indent = line_indent(lines[index])
        block_end = index + 1
        while block_end < limit:
            line = lines[block_end]
            if line.strip() and line_indent(line) <= indent:
                break
            block_end += 1
        return index, block_end, indent
    raise ValidationError(f"YAML block missing: {key}")


def extract_list(
    lines: list[str],
    key: str,
    *,
    start: int = 0,
    end: int | None = None,
) -> list[str]:
    list_start, list_end, indent = find_block(lines, key, start=start, end=end)
    values: list[str] = []
    for line in lines[list_start + 1 : list_end]:
        if not line.strip() or line_indent(line) <= indent:
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            values.append(stripped[2:].strip())
    return values


def extract_nested_list(text: str, outer_key: str, list_key: str) -> list[str]:
    lines = text.splitlines()
    outer_start, outer_end, _ = find_block(lines, outer_key)
    return extract_list(lines, list_key, start=outer_start + 1, end=outer_end)


def extract_scalar_in_block(text: str, outer_key: str, scalar_key: str) -> str:
    lines = text.splitlines()
    outer_start, outer_end, outer_indent = find_block(lines, outer_key)
    for line in lines[outer_start + 1 : outer_end]:
        if not line.strip() or line_indent(line) <= outer_indent:
            continue
        stripped = line.strip()
        prefix = f"{scalar_key}:"
        if stripped.startswith(prefix):
            return stripped[len(prefix) :].strip().strip('"\'')
    raise ValidationError(f"YAML scalar missing: {outer_key}.{scalar_key}")


def extract_refinement_map(text: str) -> dict[str, list[str]]:
    lines = text.splitlines()
    contract_start, contract_end, _ = find_block(lines, "refinement_contract")
    map_start, map_end, map_indent = find_block(
        lines,
        "refinement_map",
        start=contract_start + 1,
        end=contract_end,
    )
    entry_lines = [
        (index, line_indent(lines[index]), lines[index].strip())
        for index in range(map_start + 1, map_end)
        if lines[index].strip()
    ]
    require(entry_lines, "neuroscience refinement_map is empty")
    entry_indent = min(indent for _, indent, _ in entry_lines if indent > map_indent)
    entries: dict[str, list[str]] = {}
    for offset, (index, indent, stripped) in enumerate(entry_lines):
        if indent != entry_indent or not stripped.endswith(":") or stripped == "refines:":
            continue
        key = stripped[:-1]
        next_index = map_end
        for later_index, later_indent, _ in entry_lines[offset + 1 :]:
            if later_indent == entry_indent:
                next_index = later_index
                break
        refs = extract_list(lines, "refines", start=index + 1, end=next_index)
        require(refs, f"neuroscience refinement {key} has no kernel refs")
        entries[key] = refs
    return entries


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
        domains = manifest.get("domain_modules")
        require(isinstance(sources, list), f"{path.name}: source_files missing")
        require(isinstance(domains, list), f"{path.name}: domain_modules missing")
        require(POLICY_REF in sources, f"{path.name}: statistical qualifier policy is not reachable")
        require(FIXTURE_REF in sources, f"{path.name}: statistical qualifier fixtures are not reachable")
        require(sources.index(POLICY_REF) < sources.index(FIXTURE_REF), f"{path.name}: policy must precede fixtures")
        require(NEURO_REF in domains, f"{path.name}: neuroscience statistical cartridge is not reachable")
        require(NEURO_FIXTURE_REF in domains, f"{path.name}: neuroscience statistical fixtures are not reachable")
        require(domains.index(NEURO_REF) < domains.index(NEURO_FIXTURE_REF), f"{path.name}: neuroscience statistical policy must precede fixtures")


def validate_policy() -> set[str]:
    text = POLICY.read_text(encoding="utf-8")
    required_fragments = (
        "qualifier_basis:",
        "information_and_dependence:",
        "magnitude_and_precision:",
        "distributional_separation:",
        "classification_information:",
        "raw_accuracy_default:",
        "closure_state: unresolved",
        "basis: missing_reporting",
        "pipeline_isolation_and_selection:",
        "optimism_ledger:",
        "resampling_stability:",
        "learning_curve_and_assurance:",
        "calibration_and_proper_scoring:",
        "multiplicity_and_researcher_selection:",
        "transport_distribution:",
        "Missing reporting blocks promotion for the affected claim but does not count as disconfirmation.",
        "Every qualifier status must pair one closure_vocabulary state with one or more allowed basis codes.",
        "No universal sample-size, accuracy, overlap, AUC, calibration, or feature-count cutoff applies across claims.",
        "Accuracy alone receives no support weight.",
        "Stable average performance cannot rescue unstable individual assignments.",
        "One external validation establishes performance in one additional setting rather than universal validation.",
        "qualifier_basis_by_status",
        "observed_failure_evidence",
        "2 * Phi(-abs(d) / 2)",
        "Phi(abs(d) / 2)",
    )
    for fragment in required_fragments:
        require(fragment in text, f"statistical qualifier policy missing required fragment: {fragment}")
    require("unresolved_without_context" not in text, "statistical qualifier policy defines a noncanonical closure state")
    require("http://" not in text and "https://" not in text, "statistical qualifier policy must remain resource-neutral")

    chain_text = CHAIN.read_text(encoding="utf-8")
    closure_states = set(extract_nested_list(chain_text, "closure_vocabulary", "states"))
    require(closure_states, "chain closure vocabulary is empty")
    raw_accuracy_state = extract_scalar_in_block(text, "raw_accuracy_default", "closure_state")
    require(raw_accuracy_state in closure_states, f"raw accuracy uses noncanonical closure state: {raw_accuracy_state}")

    basis_codes = set(extract_nested_list(text, "qualifier_basis", "allowed"))
    require(REQUIRED_BASIS_CODES <= basis_codes, f"statistical qualifier basis codes missing: {sorted(REQUIRED_BASIS_CODES - basis_codes)}")
    return basis_codes


def validate_fixtures(basis_codes: set[str]) -> None:
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
        "underreported_validation_is_unresolved_not_negative",
        "observed_external_collapse_is_positive_failure",
        "balanced_case_control_accuracy_does_not_supply_deployment_ppv",
        "global_preprocessing_invalidates_internal_test",
        "stable_average_cannot_rescue_unstable_people",
        "small_sample_peak_that_declines_is_optimism_evidence",
        "one_external_setting_does_not_establish_transport_distribution",
        "good_discrimination_does_not_supply_calibration",
        "selected_winner_from_unreported_search_has_unresolved_optimism",
    }
    ids: set[str] = set()
    fixtures_by_id: dict[str, dict[str, Any]] = {}
    for fixture in fixtures:
        require(isinstance(fixture, dict), "statistical fixture must be an object")
        fixture_id = fixture.get("id")
        require(isinstance(fixture_id, str) and fixture_id, "statistical fixture id missing")
        require(fixture_id not in ids, f"duplicate statistical fixture id: {fixture_id}")
        ids.add(fixture_id)
        fixtures_by_id[fixture_id] = fixture
        values = fixture.get("input")
        expected = fixture.get("expected")
        require(isinstance(values, dict), f"{fixture_id}: input missing")
        require(isinstance(expected, dict), f"{fixture_id}: expected missing")
        basis = expected.get("qualifier_basis")
        if basis is not None:
            require(isinstance(basis, str) and basis in basis_codes, f"{fixture_id}: unknown qualifier basis {basis}")

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
    underreported = fixtures_by_id["underreported_validation_is_unresolved_not_negative"]["expected"]
    observed_failure = fixtures_by_id["observed_external_collapse_is_positive_failure"]["expected"]
    require(underreported.get("counts_as_disconfirmation") is False, "missing reporting fixture must not count as disconfirmation")
    require(observed_failure.get("counts_as_disconfirmation") is True, "observed transport collapse must count as positive failure evidence")
    raw = FIXTURES.read_text(encoding="utf-8")
    require("http://" not in raw and "https://" not in raw, "statistical fixtures must remain resource-neutral")


def validate_neuroscience_extension() -> None:
    text = NEURO.read_text(encoding="utf-8")
    required_fragments = (
        "neuroscience_statistics:",
        "refinement_contract:",
        "refinement_map:",
        "independent_unit_hierarchy:",
        "split_and_pipeline_isolation:",
        "nuisance_baselines:",
        "measurement_reliability:",
        "circular_localization:",
        "group_effect_classifier_consistency:",
        "deterministic: true",
        "distributional_or_group_effect_result_for_the_target",
        "classifier_performance_claim_for_the_same_target",
        "full_pipeline_permutation:",
        "leave_site_scanner_cohort_or_time_out",
        "voxels_trials_time_points_scans_or_augmented_images_as_independent_population_n",
    )
    for fragment in required_fragments:
        require(fragment in text, f"neuroscience statistical cartridge missing required fragment: {fragment}")
    require("small_univariate_or_group_effect_with_high_reported_classifier_performance" not in text, "neuroscience consistency audit remains discretion-gated")
    require("http://" not in text and "https://" not in text, "neuroscience statistical cartridge must remain resource-neutral")

    refinement_map = extract_refinement_map(text)
    require(REQUIRED_NEURO_REFINEMENTS <= set(refinement_map), f"neuroscience refinement map missing: {sorted(REQUIRED_NEURO_REFINEMENTS - set(refinement_map))}")
    for section, refs in refinement_map.items():
        require(section in REQUIRED_NEURO_REFINEMENTS, f"unexpected neuroscience refinement section: {section}")
        require(len(refs) == len(set(refs)), f"duplicate kernel refs in neuroscience refinement: {section}")
        invalid = set(refs) - REFINABLE_KERNEL_SECTIONS
        require(not invalid, f"{section}: unknown kernel refinement refs: {sorted(invalid)}")
        for ref in refs:
            require(f"  {ref}:" in POLICY.read_text(encoding="utf-8"), f"{section}: kernel section is not present: {ref}")

    data = load_json(NEURO_FIXTURES)
    fixtures = data.get("fixtures")
    require(isinstance(fixtures, list), "neuroscience statistical fixtures missing")
    fixture_ids = {item.get("id") for item in fixtures if isinstance(item, dict)}
    required_ids = {
        "neuro-classifier-row-leakage",
        "neuro-nuisance-only-classifier",
        "neuro-group-classifier-consistency-audit",
        "neuro-small-effect-high-classifier-contradiction",
        "neuro-reliability-ceiling",
        "neuro-full-pipeline-permutation",
        "neuro-circular-roi-selection",
        "neuro-pooled-multisite-performance",
    }
    require(required_ids <= fixture_ids, f"neuroscience statistical fixtures missing: {sorted(required_ids - fixture_ids)}")
    raw = NEURO_FIXTURES.read_text(encoding="utf-8")
    require("skip the audit because small and high thresholds were not crossed" in raw, "neuroscience fixtures do not prohibit discretion-gated audit skipping")
    require("http://" not in raw and "https://" not in raw, "neuroscience statistical fixtures must remain resource-neutral")


def main() -> int:
    try:
        validate_manifest_reachability()
        basis_codes = validate_policy()
        validate_fixtures(basis_codes)
        validate_neuroscience_extension()
    except (ValidationError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"STATISTICAL QUALIFIER VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1
    print("statistical qualifier validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
