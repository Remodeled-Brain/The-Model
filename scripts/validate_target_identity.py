#!/usr/bin/env python3
"""Validate generic target-identity reconstruction, load order, and regressions."""
from __future__ import annotations

import json
import pathlib

import validate_repo as vr

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = ROOT / "model"

KERNEL = MODEL / "kernel" / "target_identity.yaml"
RUNTIME_GATE = MODEL / "runtime" / "target_identity_gate.yaml"
DOWNSTREAM = MODEL / "runtime" / "target_identity_answer_contract.yaml"
RUNTIME_FIXTURES = MODEL / "runtime" / "target_identity_fixtures.json"
INGEST_GATE = MODEL / "ingest" / "target_identity_extraction.yaml"
INGEST_SCHEMA = MODEL / "ingest" / "target_identity_record_schema.yaml"
INGEST_FIXTURES = MODEL / "ingest" / "target_identity_fixtures.json"
NEURO_FIXTURES = MODEL / "cartridges" / "neuroscience_fixtures.json"
RUNTIME_MANIFEST = MODEL / "manifests" / "runtime.json"
INGEST_MANIFEST = MODEL / "manifests" / "ingest.json"
GENERIC_CONFORMANCE = ROOT / "conformance" / "fixtures" / "generic.json"
NEURO_CONFORMANCE = ROOT / "conformance" / "fixtures" / "neuroscience.json"

LEGACY_FOLK_FILES = [
    MODEL / "kernel" / "folk_behavior_construct.yaml",
    MODEL / "runtime" / "folk_behavior_compiler_gate.yaml",
    MODEL / "runtime" / "folk_behavior_fixtures.json",
    MODEL / "ingest" / "folk_behavior_extraction_gate.yaml",
    MODEL / "ingest" / "folk_behavior_fixtures.json",
    MODEL / "cartridges" / "neuroscience_folk_behavior.yaml",
    MODEL / "cartridges" / "neuroscience_folk_behavior_fixtures.json",
    ROOT / "scripts" / "validate_folk_behavior.py",
]


def require_text(path: pathlib.Path, fragments: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for fragment in fragments:
        vr.require(fragment in text, f"{path.relative_to(ROOT)} missing target-identity fragment: {fragment}")


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
        "kernel/target_identity.yaml",
        "runtime/target_identity_gate.yaml",
        "runtime/target_identity_answer_contract.yaml",
        "runtime/target_identity_fixtures.json",
    }
    ingest_required = {
        "kernel/target_identity.yaml",
        "ingest/target_identity_extraction.yaml",
        "ingest/target_identity_record_schema.yaml",
        "ingest/target_identity_fixtures.json",
    }
    vr.require(runtime_required <= set(runtime_sources), "runtime manifest omits target-identity modules")
    vr.require(ingest_required <= set(ingest_sources), "ingest manifest omits target-identity modules")

    vr.require(
        runtime_sources.index("kernel/target_identity.yaml")
        < runtime_sources.index("kernel/evidence_admission.yaml"),
        "target identity must load before evidence admission in runtime",
    )
    vr.require(
        runtime_sources.index("runtime/question_compiler.yaml")
        < runtime_sources.index("runtime/target_identity_gate.yaml")
        < runtime_sources.index("runtime/answerability_planner.yaml"),
        "target-identity gate must extend the compiler before planning",
    )
    vr.require(
        runtime_sources.index("runtime/answer_contract.yaml")
        < runtime_sources.index("runtime/target_identity_answer_contract.yaml")
        < runtime_sources.index("runtime/physical_answer_contract.yaml"),
        "target-identity answer contract must extend planning binding and answer behavior before physical rendering",
    )
    vr.require(
        ingest_sources.index("ingest/rules.yaml")
        < ingest_sources.index("ingest/target_identity_extraction.yaml")
        < ingest_sources.index("ingest/physical_extraction_contract.yaml"),
        "target-identity extraction must precede physical extraction and admission weighting",
    )
    vr.require(
        ingest_sources.index("ingest/target_identity_extraction.yaml")
        < ingest_sources.index("ingest/target_identity_record_schema.yaml")
        < ingest_sources.index("ingest/record_schema.yaml"),
        "target-identity record contract must load before the canonical ingest schema",
    )

    vr.require(
        not any("target_identity" in path for path in runtime_domains + ingest_domains),
        "target identity may not depend on a domain-specific cartridge module",
    )
    joined = "\n".join(runtime_sources + ingest_sources + runtime_domains + ingest_domains)
    vr.require("folk_behavior" not in joined, "authoritative manifests retain folklore-specific modules")


def validate_policy() -> None:
    require_text(
        KERNEL,
        [
            "Names may compress generated identities. They may not generate identities by compression.",
            "speaker_intent:",
            "corpus_operations:",
            "generated_identity_closed:",
            "generated_identity_conditional:",
            "constructed_measurement_identity:",
            "grouping_handle_only:",
            "identity_unresolved:",
            "premise_rejected:",
            "Heterogeneity preserves a common identity only when an exposed generator accounts for the variation",
            "Evidence binds first to the exact measured or constructed relation.",
            "Randomization applies to the object actually assigned",
        ],
    )
    require_text(
        RUNTIME_GATE,
        [
            "build_speaker_intent_record",
            "build_corpus_identity_record_from_source_operations",
            "ask_smallest_useful_fork_when:",
            "no_blacklist_rule:",
            "Causal weighting must wait until the exact target relation",
        ],
    )
    require_text(
        DOWNSTREAM,
        [
            "planner_extension:",
            "binder_extension:",
            "answer_extension:",
            "bind_to_exact_measured_or_constructed_relation",
            "final_wording_cannot_restore_failed_identity: true",
        ],
    )
    require_text(
        INGEST_GATE,
        [
            "corpus_crosswalk:",
            "same_label_operationalizations",
            "heterogeneity_audit:",
            "Randomization and comparison apply only to the assigned object",
            "Preserve exact observations and constructed measures when shared identity fails.",
        ],
    )
    require_text(
        INGEST_SCHEMA,
        [
            "speaker_intent_record:",
            "per_target_record:",
            "identity_disposition_enum:",
            "corpus_crosswalk:",
            "relation_ledger:",
        ],
    )


def validate_fixtures() -> None:
    vr.require(
        {
            "target-identity-before-evidence",
            "recoverable-identity-shortcut",
            "speaker-corpus-target-mismatch",
            "heterogeneity-must-be-generated",
            "exact-relation-positive-control",
        }
        <= fixture_ids(RUNTIME_FIXTURES),
        "runtime target-identity fixtures incomplete",
    )
    vr.require(
        {
            "shared-label-non-equivalent-operationalizations",
            "recoverable-conditional-identity",
            "heterogeneity-without-generator",
            "exact-relation-survives-identity-failure",
        }
        <= fixture_ids(INGEST_FIXTURES),
        "ingest target-identity fixtures incomplete",
    )
    vr.require(
        {"neuro-stimulation-target-identity", "neuro-target-identity-positive-control"}
        <= fixture_ids(NEURO_FIXTURES),
        "neuroscience target-identity regressions incomplete",
    )
    vr.require(
        "target-identity-reconstruction" in fixture_ids(GENERIC_CONFORMANCE),
        "generic semantic conformance lacks target-identity reconstruction fixture",
    )
    vr.require(
        "stimulation-target-identity" in fixture_ids(NEURO_CONFORMANCE),
        "neuroscience semantic conformance lacks target-identity fixture",
    )


def validate_cleanup() -> None:
    remaining = [path.relative_to(ROOT).as_posix() for path in LEGACY_FOLK_FILES if path.exists()]
    vr.require(not remaining, f"folklore-specific architecture remains: {remaining}")


def main() -> int:
    try:
        validate_manifests()
        validate_policy()
        validate_fixtures()
        validate_cleanup()
    except (vr.ValidationError, OSError, json.JSONDecodeError) as exc:
        print(f"TARGET-IDENTITY VALIDATION FAILED: {exc}")
        return 1
    print("target-identity validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
