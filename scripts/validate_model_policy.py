#!/usr/bin/env python3
"""Validate generic evidence policy, physical continuity, and domain-cartridge separation."""

from __future__ import annotations

import json
import pathlib

import validate_repo as vr

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = ROOT / "model"
KERNEL = MODEL / "kernel" / "chain_contract.yaml"
PHYSICAL_KERNEL = MODEL / "kernel" / "physical_continuity.yaml"
EVIDENCE = MODEL / "kernel" / "evidence_admission.yaml"
EVIDENCE_FIXTURES = MODEL / "kernel" / "evidence_admission_fixtures.json"
COMPILER = MODEL / "runtime" / "question_compiler.yaml"
PLANNER = MODEL / "runtime" / "answerability_planner.yaml"
BINDER = MODEL / "runtime" / "evidence_binding_contract.yaml"
ANSWER = MODEL / "runtime" / "answer_contract.yaml"
PHYSICAL_ANSWER = MODEL / "runtime" / "physical_answer_contract.yaml"
RUNTIME_FIXTURES = MODEL / "runtime" / "fixtures.json"
INGEST_ARCHITECTURE = MODEL / "ingest" / "architecture.yaml"
INGEST_RULES = MODEL / "ingest" / "rules.yaml"
PHYSICAL_INGEST = MODEL / "ingest" / "physical_extraction_contract.yaml"
FAILURE_ROUTING = MODEL / "ingest" / "failure_routing.yaml"
RECORD_SCHEMA = MODEL / "ingest" / "record_schema.yaml"
INGEST_FIXTURES = MODEL / "ingest" / "fixtures.json"
NEURO_CARTRIDGE = MODEL / "cartridges" / "neuroscience.yaml"
NEURO_PHYSICAL = MODEL / "cartridges" / "neuroscience_physical_continuity.yaml"
NEURO_FIXTURES = MODEL / "cartridges" / "neuroscience_fixtures.json"
RUNTIME_MANIFEST = MODEL / "manifests" / "runtime.json"
INGEST_MANIFEST = MODEL / "manifests" / "ingest.json"

CONSTRUCT_REF = "model/kernel/chain_contract.yaml#chain_contract.construct_admission.dispositions"
CAUSAL_REF = "model/kernel/chain_contract.yaml#chain_contract.causal_claim_admission.dispositions"
PHYSICAL_REF = "model/kernel/physical_continuity.yaml#physical_continuity"
EVIDENCE_REF = "model/kernel/evidence_admission.yaml#evidence_admission"
ROLE_REF = "model/runtime/evidence_binding_contract.yaml#evidence_binding_contract.evidence_role_classes"
BODY_REF = "model/runtime/evidence_binding_contract.yaml#evidence_binding_contract.body_of_evidence_assessment.body_verdicts"


def require_text(path: pathlib.Path, fragments: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for fragment in fragments:
        vr.require(fragment in text, f"{path.relative_to(ROOT)} missing policy fragment: {fragment}")


def fixture_data(path: pathlib.Path) -> dict:
    return vr.load_json(path)


def fixture_ids(path: pathlib.Path) -> set[str]:
    fixtures = fixture_data(path).get("fixtures", [])
    return {item.get("id") for item in fixtures if isinstance(item, dict)}


def require_fixture_ids(path: pathlib.Path, expected: set[str]) -> None:
    missing = expected - fixture_ids(path)
    vr.require(not missing, f"{path.relative_to(ROOT)} missing fixtures: {sorted(missing)}")


def validate_fixture_shape(path: pathlib.Path, *, modes: bool) -> None:
    fixtures = fixture_data(path).get("fixtures")
    vr.require(isinstance(fixtures, list) and fixtures, f"{path.relative_to(ROOT)} fixtures missing")
    seen: set[str] = set()
    for fixture in fixtures:
        vr.require(isinstance(fixture, dict), f"{path.relative_to(ROOT)} fixture must be an object")
        fixture_id = fixture.get("id")
        vr.require(isinstance(fixture_id, str) and fixture_id, f"{path.relative_to(ROOT)} fixture id missing")
        vr.require(fixture_id not in seen, f"duplicate fixture id in {path.relative_to(ROOT)}: {fixture_id}")
        seen.add(fixture_id)
        if modes:
            vr.require(fixture.get("mode") in {"question", "condition"}, f"{fixture_id}: invalid mode")
            source_field = "source_question" if fixture["mode"] == "question" else "condition"
            vr.require(isinstance(fixture.get(source_field), str) and fixture[source_field], f"{fixture_id}: {source_field} missing")
            vr.require(isinstance(fixture.get("required"), list) and fixture["required"], f"{fixture_id}: required missing")
            vr.require(isinstance(fixture.get("forbidden"), list) and fixture["forbidden"], f"{fixture_id}: forbidden missing")


def validate_manifests() -> None:
    runtime_required = {
        "kernel/evidence_admission.yaml",
        "kernel/evidence_admission_fixtures.json",
        "kernel/physical_continuity.yaml",
        "runtime/physical_answer_contract.yaml",
    }
    ingest_required = {
        "kernel/evidence_admission.yaml",
        "kernel/evidence_admission_fixtures.json",
        "kernel/physical_continuity.yaml",
        "ingest/physical_extraction_contract.yaml",
    }
    required_domain = {
        "cartridges/neuroscience.yaml",
        "cartridges/neuroscience_physical_continuity.yaml",
        "cartridges/neuroscience_fixtures.json",
    }
    runtime = fixture_data(RUNTIME_MANIFEST)
    ingest = fixture_data(INGEST_MANIFEST)
    vr.require(runtime_required <= set(runtime.get("source_files", [])), "runtime manifest omits shared evidence or physical kernel")
    vr.require(ingest_required <= set(ingest.get("source_files", [])), "ingest manifest omits shared evidence or physical kernel")
    for path, manifest in ((RUNTIME_MANIFEST, runtime), (INGEST_MANIFEST, ingest)):
        vr.require(required_domain <= set(manifest.get("domain_modules", [])), f"{path.name}: neuroscience cartridge, physical application, or fixtures omitted")


def validate_construct_and_causal_kernel() -> None:
    dispositions = set(vr.yaml_list(KERNEL, "dispositions"))
    expected = {"admitted", "grouping_handle_only", "premise_rejected", "underspecified"}
    vr.require(dispositions == expected, f"construct dispositions drifted: {sorted(dispositions)}")

    for path in (COMPILER, PLANNER, BINDER, ANSWER, INGEST_RULES, RECORD_SCHEMA):
        require_text(path, [CONSTRUCT_REF, CAUSAL_REF])

    require_text(
        KERNEL,
        [
            "physical_continuity_ref: model/kernel/physical_continuity.yaml#physical_continuity",
            "every_biological_explanation_must_bind_through_metabolically_maintained_state: true",
            "causal_admission_does_not_imply_mechanistic_closure: true",
            "causal_admission_is_target_relation_specific: true",
            "intervention_status_neither_grants_nor_denies_causality: true",
            "required_tests_by_target:",
            "intervention_to_outcome:",
            "observational_causal_relation:",
            "endogenous_dependency_or_mechanism:",
            "A decisive controlled intervention can close the exact manipulated",
            "no_intervention_scope_transfer",
            "no_metabolism_as_magic_operator",
        ],
    )
    require_text(
        PLANNER,
        [
            PHYSICAL_REF,
            "physical_chain_planning:",
            "metabolically maintained state",
            "target_relation_plans:",
            "observational_causal_relation:",
            "intervention_to_outcome:",
            "A decisive intervention must not be rejected merely because it is therapeutic.",
            "Exact intervention causality may coexist with partial internal physical or metabolic route closure.",
        ],
    )


def validate_physical_continuity() -> None:
    require_text(
        PHYSICAL_KERNEL,
        [
            "Every admitted cause, operation, state, constraint, and transition is physical.",
            "forms stars",
            "Metabolics drives biology",
            "metabolically maintained state",
            "causal_admission_distinct_from_mechanistic_closure: true",
            "no_action_at_a_distance_between_components",
            "no_metabolism_as_magic_noun",
        ],
    )
    require_text(
        PHYSICAL_ANSWER,
        [
            PHYSICAL_REF,
            "exact_intervention_effect_with_partial_route: allowed",
            "mechanism_claim_with_partial_route: forbidden",
            "metabolism_caused_it",
        ],
    )
    require_text(
        PHYSICAL_INGEST,
        [
            PHYSICAL_REF,
            "Metabolism or metabolic activity by itself does not close a chain segment.",
            "unresolved_physical_chain_slots",
        ],
    )
    require_text(
        ANSWER,
        [
            PHYSICAL_REF,
            "universal_physical_rule:",
            "biological_metabolic_rule:",
            "causal_mechanistic_separation_rule:",
            "action_at_a_distance_between_named_components",
            "metabolism_as_magic_operator",
        ],
    )
    require_text(
        NEURO_PHYSICAL,
        [
            "Neural tissue has no separate causal currency.",
            "metabolically maintained tissue",
            "region_X_activated_then_behavior_changed",
        ],
    )


def validate_data_first_admission() -> None:
    for path in (BINDER, ANSWER, INGEST_ARCHITECTURE, INGEST_RULES, RECORD_SCHEMA):
        require_text(path, [EVIDENCE_REF])

    require_text(
        EVIDENCE,
        [
            "source_claim_status: unadmitted_assertion",
            "causal_weight: zero",
            "data_first_admission:",
            "The admissible claim is generated from the actual observations and design.",
            "observational_record:",
            "intervention_record:",
            "A decisive intervention may establish intervention-to-outcome causality",
            "statistically_significant_as_effective",
            "measured_proxy_change_as_named_biological_process",
        ],
    )
    require_text(
        INGEST_RULES,
        [
            "actual_data_outranks_source_narrative: true",
            "observational_evidence_defaults_to_noncausal: true",
            "intervention_evidence_is_target_specific: true",
            "statistical_significance_does_not_establish_effectiveness: true",
            "named_process_language_does_not_establish_measured_process: true",
        ],
    )
    require_text(
        RECORD_SCHEMA,
        [
            "data_record:",
            "effect_distribution",
            "comparator_or_counterfactual",
            "missingness_attrition_and_crossover",
            "timing_and_durability",
            "intervention_label_neither_grants_nor_denies_causality: true",
        ],
    )
    require_text(
        BINDER,
        [
            "The actual data outrank the source narrative.",
            "A strong controlled intervention can outweigh many observational associations for the exact manipulated relation.",
            "Intervention efficacy cannot be transferred automatically to etiology endogenous mechanism or construct validity.",
            "Observational evidence begins descriptive or more restricted",
        ],
    )
    require_text(
        ANSWER,
        [
            "The actual data outrank the source narrative.",
            "Use effective only with an explicit target, comparator, practical threshold, full response distribution, durability,",
            "A strong intervention must be allowed to close the exact manipulated relation.",
            "A named process cannot be inferred from a proxy or pre-post change.",
        ],
    )


def validate_shared_fixtures() -> None:
    validate_fixture_shape(EVIDENCE_FIXTURES, modes=False)
    validate_fixture_shape(RUNTIME_FIXTURES, modes=True)
    require_fixture_ids(
        EVIDENCE_FIXTURES,
        {
            "observational-defaults-noncausal",
            "decisive-intervention-can-close-manipulated-relation",
            "intervention-scope-does-not-transfer",
            "narrative-effective-exceeds-data",
            "named-process-claim-needs-direct-data",
            "construct-indexed-defaults-label-dependent",
            "proxy-requires-translation",
            "meta-analysis-inherits-input-failure",
        },
    )
    require_fixture_ids(
        RUNTIME_FIXTURES,
        {
            "reified-category-as-entity",
            "observational-hard-causality",
            "decisive-intervention",
            "intervention-scope-transfer",
            "narrative-data-conflict",
            "descriptive-question",
            "competing-routes",
            "narrow-answer-from-partial-chain",
        },
    )
    require_fixture_ids(
        INGEST_FIXTURES,
        {
            "observational-causal-overreach",
            "decisive-controlled-intervention",
            "weak-intervention-effectiveness-narrative",
            "intervention-scope-transfer",
            "construct-indexed-observation",
            "proxy-named-as-mechanism",
            "named-process-without-measurement",
            "synthesis-inherits-input-failure",
            "premise-breaking-dominance",
        },
    )


def validate_domain_separation() -> None:
    forbidden = {
        "adhd",
        "autism",
        "prefrontal",
        "cortex",
        "nitric oxide",
        "cbt",
        "depression",
        "neuroplasticity",
        "ocd",
        "striatum",
    }
    for path in (RUNTIME_FIXTURES, INGEST_FIXTURES, EVIDENCE_FIXTURES):
        text = path.read_text(encoding="utf-8").lower()
        leaked = sorted(term for term in forbidden if term in text)
        vr.require(not leaked, f"domain-specific terms leaked into generic fixtures {path.relative_to(ROOT)}: {leaked}")

    validate_fixture_shape(NEURO_FIXTURES, modes=True)
    require_fixture_ids(
        NEURO_FIXTURES,
        {
            "neuro-region-as-agent",
            "neuro-diagnostic-entity",
            "neuro-adhd-prefrontal-defect",
            "neuro-diagnostic-biomarker",
            "neuro-cbt-depression-effectiveness",
            "neuro-therapy-neuroplasticity",
            "neuro-decisive-stimulation",
            "neuro-same-mutation-divergent-labels",
            "neuro-cross-species-translation",
        },
    )
    require_text(
        NEURO_CARTRIDGE,
        [
            "fixture_ref: model/cartridges/neuroscience_fixtures.json",
            "therapy_and_intervention_policy:",
            "psychotherapy_and_rating_scale_policy:",
            "named_process_policy:",
            "neuroplasticity:",
            "decisive_intervention_rule:",
            "CBT treats depression without a stated causal contrast",
        ],
    )


def validate_evidence_vocabularies() -> None:
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
        "causal_claim_rejected",
        "disconfirmed",
        "unsupported",
        "bounded_support",
        "supported",
        "contested",
    }
    vr.require(verdicts == expected_verdicts, f"body verdicts drifted: {sorted(verdicts)}")
    require_text(ANSWER, [BODY_REF])
    require_text(INGEST_RULES, [ROLE_REF])


def validate_runtime_answer_fields() -> None:
    fields = set(fixture_data(RUNTIME_FIXTURES).get("required_answer_fields", []))
    required = {
        "direct_answer",
        "construct_disposition",
        "evidence_admission",
        "body_of_evidence",
        "closure_report",
        "conclusions",
        "confidence",
    }
    vr.require(required <= fields, f"runtime answer fields missing: {sorted(required - fields)}")


if __name__ == "__main__":
    try:
        validate_manifests()
        validate_construct_and_causal_kernel()
        validate_physical_continuity()
        validate_data_first_admission()
        validate_shared_fixtures()
        validate_domain_separation()
        validate_evidence_vocabularies()
        validate_runtime_answer_fields()
    except (vr.ValidationError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"POLICY VALIDATION FAILED: {exc}") from exc
    print("model policy validation passed")
