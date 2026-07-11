#!/usr/bin/env python3
"""Validate folk-behavior construct translation modules, load graphs, and regressions."""
from __future__ import annotations

import json
import pathlib

import validate_repo as vr

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = ROOT / "model"

KERNEL = MODEL / "kernel" / "folk_behavior_construct.yaml"
RUNTIME_GATE = MODEL / "runtime" / "folk_behavior_compiler_gate.yaml"
INGEST_GATE = MODEL / "ingest" / "folk_behavior_extraction_gate.yaml"
NEURO = MODEL / "cartridges" / "neuroscience_folk_behavior.yaml"
RUNTIME_FIXTURES = MODEL / "runtime" / "folk_behavior_fixtures.json"
INGEST_FIXTURES = MODEL / "ingest" / "folk_behavior_fixtures.json"
NEURO_FIXTURES = MODEL / "cartridges" / "neuroscience_folk_behavior_fixtures.json"
RUNTIME_MANIFEST = MODEL / "manifests" / "runtime.json"
INGEST_MANIFEST = MODEL / "manifests" / "ingest.json"
GENERIC_CONFORMANCE = ROOT / "conformance" / "fixtures" / "generic.json"
NEURO_CONFORMANCE = ROOT / "conformance" / "fixtures" / "neuroscience.json"


def require_text(path: pathlib.Path, fragments: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for fragment in fragments:
        vr.require(fragment in text, f"{path.relative_to(ROOT)} missing folk-behavior fragment: {fragment}")


def load(path: pathlib.Path) -> dict:
    return vr.load_json(path)


def fixture_ids(path: pathlib.Path) -> set[str]:
    fixtures = load(path).get("fixtures")
    vr.require(isinstance(fixtures, list) and fixtures, f"{path.relative_to(ROOT)} fixtures missing")
    ids: set[str] = set()
    for fixture in fixtures:
        vr.require(isinstance(fixture, dict), f"{path.relative_to(ROOT)} fixture must be an object")
        fixture_id = fixture.get("id")
        vr.require(isinstance(fixture_id, str) and fixture_id, f"{path.relative_to(ROOT)} fixture id missing")
        vr.require(fixture_id not in ids, f"duplicate fixture id in {path.relative_to(ROOT)}: {fixture_id}")
        ids.add(fixture_id)
    return ids


def validate_manifests() -> None:
    runtime = load(RUNTIME_MANIFEST)
    ingest = load(INGEST_MANIFEST)
    runtime_sources = runtime.get("source_files", [])
    ingest_sources = ingest.get("source_files", [])
    runtime_domains = runtime.get("domain_modules", [])
    ingest_domains = ingest.get("domain_modules", [])

    runtime_required = {
        "kernel/folk_behavior_construct.yaml",
        "runtime/folk_behavior_compiler_gate.yaml",
        "runtime/folk_behavior_fixtures.json",
    }
    ingest_required = {
        "kernel/folk_behavior_construct.yaml",
        "ingest/folk_behavior_extraction_gate.yaml",
        "ingest/folk_behavior_fixtures.json",
    }
    domain_required = {
        "cartridges/neuroscience_folk_behavior.yaml",
        "cartridges/neuroscience_folk_behavior_fixtures.json",
    }

    vr.require(runtime_required <= set(runtime_sources), "runtime manifest omits folk-behavior compiler modules")
    vr.require(ingest_required <= set(ingest_sources), "ingest manifest omits folk-behavior extraction modules")
    vr.require(domain_required <= set(runtime_domains), "runtime manifest omits neuroscience folk-behavior cartridge")
    vr.require(domain_required <= set(ingest_domains), "ingest manifest omits neuroscience folk-behavior cartridge")

    vr.require(
        runtime_sources.index("kernel/folk_behavior_construct.yaml")
        < runtime_sources.index("kernel/evidence_admission.yaml"),
        "folk-behavior construct gate must load before evidence admission in runtime",
    )
    vr.require(
        runtime_sources.index("runtime/question_compiler.yaml")
        < runtime_sources.index("runtime/folk_behavior_compiler_gate.yaml")
        < runtime_sources.index("runtime/answerability_planner.yaml"),
        "folk-behavior compiler gate must extend the compiler before planning",
    )
    vr.require(
        ingest_sources.index("ingest/rules.yaml")
        < ingest_sources.index("ingest/folk_behavior_extraction_gate.yaml")
        < ingest_sources.index("ingest/physical_extraction_contract.yaml"),
        "folk-behavior ingest gate must run before physical extraction and admission weighting",
    )


def validate_policy() -> None:
    require_text(
        KERNEL,
        [
            "Translate the label into the exact measured organism-state relation before design strength",
            "construct: grouping_handle_only",
            "exact_independently_measured_relation: eligible_for_separate_review",
            "Ordinary-life task content does not establish real-world efficacy.",
            "Randomization and comparison apply to the object actually assigned.",
            "effect_magnitude_repairs_construct_identity",
        ],
    )
    require_text(
        RUNTIME_GATE,
        [
            "before: evaluate_construct_admission",
            "emit_construct_reconstruction_record",
            "continue_only_with_independently_measurable_target_relations",
            "procrastination_as_one_outcome_without_decomposition",
        ],
    )
    require_text(
        INGEST_GATE,
        [
            "runs_before:",
            "construct_level_causal_weight_remains_zero_without_independent_construct_escape",
            "assigned_protocol_to_exact_recorded_behavior",
            "daily_life_task_content_to_ecological_validity",
        ],
    )
    require_text(
        NEURO,
        [
            "procrastination",
            "programmed_device_output_is_not_target_engagement",
            "statistical_mediation_does_not_identify_a_physical_route",
            "paper_regression:",
            "withhold_actual_causality_when_manipulation_identity_attrition_analysis_or_replication_burdens_remain_open",
        ],
    )


def validate_fixtures() -> None:
    vr.require(
        {"folk-behavior-target-before-evidence", "folk-behavior-positive-narrow-control"}
        <= fixture_ids(RUNTIME_FIXTURES),
        "runtime folk-behavior fixtures incomplete",
    )
    vr.require(
        {"folk-behavior-construct-ingress", "folk-behavior-exact-relation-survives"}
        <= fixture_ids(INGEST_FIXTURES),
        "ingest folk-behavior fixtures incomplete",
    )
    vr.require(
        {"neuro-stimulation-procrastination", "neuro-folk-target-does-not-block-exact-effect"}
        <= fixture_ids(NEURO_FIXTURES),
        "neuroscience folk-behavior fixtures incomplete",
    )
    vr.require(
        "folk-behavior-target-reconstruction" in fixture_ids(GENERIC_CONFORMANCE),
        "generic semantic conformance lacks folk-behavior reconstruction fixture",
    )
    vr.require(
        "stimulation-procrastination-construct" in fixture_ids(NEURO_CONFORMANCE),
        "neuroscience semantic conformance lacks procrastination stimulation fixture",
    )


def main() -> int:
    try:
        validate_manifests()
        validate_policy()
        validate_fixtures()
    except (vr.ValidationError, OSError, json.JSONDecodeError) as exc:
        print(f"FOLK-BEHAVIOR VALIDATION FAILED: {exc}")
        return 1
    print("folk-behavior construct validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
