#!/usr/bin/env python3
"""Validate the model policies that prevent folklore rescue and evidence laundering."""

from __future__ import annotations

import pathlib

import validate_repo as vr

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = ROOT / "model"
KERNEL = MODEL / "kernel" / "chain_contract.yaml"
COMPILER = MODEL / "runtime" / "question_compiler.yaml"
PLANNER = MODEL / "runtime" / "answerability_planner.yaml"
BINDER = MODEL / "runtime" / "evidence_binding_contract.yaml"
ANSWER = MODEL / "runtime" / "answer_contract.yaml"
INGEST_RULES = MODEL / "ingest" / "rules.yaml"
RECORD_SCHEMA = MODEL / "ingest" / "record_schema.yaml"
RUNTIME_FIXTURES = MODEL / "runtime" / "fixtures.json"
INGEST_FIXTURES = MODEL / "ingest" / "fixtures.json"
CARTRIDGE = MODEL / "cartridges" / "neuroscience.yaml"

CONSTRUCT_REF = "model/kernel/chain_contract.yaml#chain_contract.construct_admission.dispositions"
EVIDENCE_ROLE_REF = "model/runtime/evidence_binding_contract.yaml#evidence_binding_contract.evidence_role_classes"
BODY_VERDICT_REF = "model/runtime/evidence_binding_contract.yaml#evidence_binding_contract.body_of_evidence_assessment.body_verdicts"


def require_text(path: pathlib.Path, fragments: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for fragment in fragments:
        vr.require(fragment in text, f"{path.relative_to(ROOT)} missing policy fragment: {fragment}")


def validate_construct_admission() -> None:
    dispositions = set(vr.yaml_list(KERNEL, "dispositions"))
    expected = {"admitted", "grouping_handle_only", "premise_rejected", "underspecified"}
    vr.require(dispositions == expected, f"construct dispositions drifted: {sorted(dispositions)}")

    for path in (COMPILER, PLANNER, BINDER, ANSWER, INGEST_RULES, RECORD_SCHEMA):
        require_text(path, [CONSTRUCT_REF])

    require_text(
        KERNEL,
        [
            "downstream_evidence_cannot_rescue_a_rejected_construct: true",
            "publication_volume_cannot_outweigh_failure_of_a_required_premise: true",
            "A rejected premise stops mechanism search for the labeled entity.",
        ],
    )
    require_text(
        COMPILER,
        [
            "stop_entity_level_mechanism_search",
            "do_not_retrieve_evidence_to_accommodate_the_rejected_construct",
            "inferred_trait_bundle_from_diagnostic_label",
        ],
    )
    require_text(
        ANSWER,
        [
            "state_the_rejection_in_the_first_sentence",
            "literature_laundry_list_after_premise_rejection",
            "A necessary premise failure outranks any volume of downstream literature",
        ],
    )
    require_text(
        CARTRIDGE,
        [
            "source_question: Is ADHD a defective prefrontal cortex?",
            "disposition: premise_rejected",
            "ADHD is a diagnostic folklore grouping",
        ],
    )


def validate_evidence_weighting() -> None:
    roles = set(vr.yaml_mapping(BINDER, "evidence_role_classes"))
    expected_roles = {
        "premise_breaking",
        "route_closing",
        "route_discriminating",
        "segment_supporting",
        "descriptive_only",
        "non_probative",
    }
    vr.require(roles == expected_roles, f"evidence role classes drifted: {sorted(roles)}")

    verdicts = set(vr.yaml_mapping(BINDER, "body_verdicts"))
    expected_verdicts = {
        "premise_rejected",
        "disconfirmed",
        "unsupported",
        "bounded_support",
        "supported",
        "contested",
    }
    vr.require(verdicts == expected_verdicts, f"body verdicts drifted: {sorted(verdicts)}")

    require_text(BINDER, [EVIDENCE_ROLE_REF, "unit_of_counting: independent_evidence_family", "no_numeric_average: true"])
    require_text(ANSWER, [BODY_VERDICT_REF, "exclude_non_probative_records_from_the_support_narrative"])
    require_text(INGEST_RULES, [EVIDENCE_ROLE_REF, "publication_volume_never_supplies_weight: true"])
    require_text(RECORD_SCHEMA, [EVIDENCE_ROLE_REF, "body_weight_inputs:", "evidence_family_id"])


def fixture_ids(path: pathlib.Path) -> set[str]:
    data = vr.load_json(path)
    fixtures = data.get("fixtures", [])
    return {item.get("id") for item in fixtures if isinstance(item, dict)}


def validate_regressions() -> None:
    runtime = vr.load_json(RUNTIME_FIXTURES)
    required_fields = set(runtime.get("required_answer_fields", []))
    vr.require(
        {"construct_disposition", "rejected_premises", "body_of_evidence"} <= required_fields,
        "runtime answer fields omit premise rejection or body-of-evidence output",
    )
    required_runtime_ids = {
        "diagnostic-category",
        "adhd-prefrontal-defect",
        "body-of-evidence-weighting",
    }
    missing_runtime = required_runtime_ids - fixture_ids(RUNTIME_FIXTURES)
    vr.require(not missing_runtime, f"missing runtime policy fixtures: {sorted(missing_runtime)}")

    required_ingest_ids = {
        "diagnostic-entity-premise",
        "correlated-volume",
        "premise-breaking-dominance",
    }
    missing_ingest = required_ingest_ids - fixture_ids(INGEST_FIXTURES)
    vr.require(not missing_ingest, f"missing ingest policy fixtures: {sorted(missing_ingest)}")


if __name__ == "__main__":
    try:
        validate_construct_admission()
        validate_evidence_weighting()
        validate_regressions()
    except (vr.ValidationError, OSError) as exc:
        raise SystemExit(f"POLICY VALIDATION FAILED: {exc}") from exc
    print("model policy validation passed")
