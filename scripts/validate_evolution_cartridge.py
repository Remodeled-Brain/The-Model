#!/usr/bin/env python3
"""Validate the candidate evolution cartridge and its manifest integration."""
from __future__ import annotations
import json
import pathlib
import validate_repo as vr

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = ROOT / "model"
EVOLUTION = MODEL / "cartridges" / "evolution.yaml"
PHYSICAL = MODEL / "cartridges" / "evolution_physical_continuity.yaml"
FIXTURES = MODEL / "cartridges" / "evolution_fixtures.json"
RUNTIME = MODEL / "manifests" / "runtime.json"
INGEST = MODEL / "manifests" / "ingest.json"

MODULES = {
    "cartridges/evolution.yaml",
    "cartridges/evolution_physical_continuity.yaml",
    "cartridges/evolution_fixtures.json",
}
IDENTITY = {
    "generated_identity_closed",
    "generated_identity_conditional",
    "constructed_measurement_identity",
    "grouping_handle_only",
    "identity_unresolved",
    "premise_rejected",
}
CONSTRUCT = {"admitted", "grouping_handle_only", "premise_rejected", "underspecified"}
CAUSAL = {"causal_admitted", "causal_rejected", "causal_unresolved", "not_a_causal_question"}
ROLES = {"premise_breaking", "route_closing", "route_discriminating", "segment_supporting", "descriptive_only", "non_probative"}
CRITICAL_FIXTURES = {
    "evo-descriptive-frequency-change",
    "evo-selection-attribution-with-open-alternatives",
    "evo-manipulated-regime-selection-positive-control",
    "evo-drift-positive-control",
    "evo-neutrality-from-nonsignificance",
    "evo-fitness-formal-shortcut-positive-control",
    "evo-current-role-origin-separation",
    "evo-historical-adaptation-positive-control",
    "evo-conservation-descriptive-only",
    "evo-similarity-without-homology",
    "evo-homology-reconstruction-positive-control",
    "evo-experimental-evolution-standing-variation",
    "evo-laboratory-to-natural-transport",
    "evo-gene-association-versus-gene-for",
    "evo-direct-molecular-effect-positive-control",
    "evo-optimum-model-positive-control",
    "evo-phylogenetic-pseudoreplication",
    "evo-lineage-pseudoreplication",
}


def require_text(path: pathlib.Path, fragments: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for fragment in fragments:
        vr.require(fragment in text, f"{path.relative_to(ROOT)} missing: {fragment}")


def validate_manifests() -> None:
    for path in (RUNTIME, INGEST):
        manifest = vr.load_json(path)
        source = manifest.get("source_files", [])
        domain = manifest.get("domain_modules", [])
        vr.require(MODULES <= set(domain), f"{path.name}: evolution modules missing")
        vr.require(not MODULES & set(source), f"{path.name}: evolution modules belong only in domain_modules")
        vr.require(len(source + domain) == len(set(source + domain)), f"{path.name}: duplicate runtime input")


def validate_cartridge_text() -> None:
    require_text(EVOLUTION, [
        "refinement_contract:",
        "Surface vocabulary triggers inspection only.",
        "evidence_failure_rewritten_as_identity_failure",
        "population_level_product_rewritten_as_process",
        "recognized_non_equivalent_generators:",
        "claim_burden_matrix:",
        "historical_adaptation:",
        "statistical_refinements:",
        "canonical_roles:",
        "Identity or causal failure at a broad target cannot erase",
    ])
    require_text(PHYSICAL, [
        "population_level_binding:",
        "carrier_phenotype_separation:",
        "finite_sampling_or_drift:",
        "differential_persistence_or_reproduction:",
        "current_trait_role:",
        "historical_adaptation:",
        "claim_sensitive_physical_burden:",
        "Exact causality may close for the manipulated relation",
        "selection_pressure_named_without_physical_regime",
    ])
    combined = EVOLUTION.read_text(encoding="utf-8") + "\n" + PHYSICAL.read_text(encoding="utf-8")
    forbidden = {
        "constructed_measurement_identity_conditional",
        "grouping_handle_only_or_identity_unresolved",
        "identity_unresolved_for_historical_origin",
        "selection is the observed outcome",
        "Ne * mu * generations",
    }
    leaked = sorted(value for value in forbidden if value in combined)
    vr.require(not leaked, f"evolution cartridge contains rejected forms: {leaked}")


def validate_fixtures() -> None:
    data = vr.load_json(FIXTURES)
    fixtures = data.get("fixtures")
    vr.require(data.get("schema_version") == "v1", "evolution fixtures must use schema v1")
    vr.require(isinstance(fixtures, list) and fixtures, "evolution fixtures missing")
    seen: set[str] = set()
    found_positive = False
    found_negative = False
    for fixture in fixtures:
        vr.require(isinstance(fixture, dict), "evolution fixture must be an object")
        fixture_id = fixture.get("id")
        vr.require(isinstance(fixture_id, str) and fixture_id, "evolution fixture id missing")
        vr.require(fixture_id not in seen, f"duplicate evolution fixture id: {fixture_id}")
        seen.add(fixture_id)
        mode = fixture.get("mode")
        vr.require(mode in {"question", "condition"}, f"{fixture_id}: invalid mode")
        source_field = "source_question" if mode == "question" else "condition"
        vr.require(isinstance(fixture.get(source_field), str) and fixture[source_field], f"{fixture_id}: {source_field} missing")
        vr.require(isinstance(fixture.get("required"), list) and fixture["required"], f"{fixture_id}: required missing")
        vr.require(isinstance(fixture.get("forbidden"), list) and fixture["forbidden"], f"{fixture_id}: forbidden missing")
        targets = fixture.get("expected_targets")
        vr.require(isinstance(targets, list) and targets, f"{fixture_id}: expected_targets missing")
        target_names: set[str] = set()
        for target in targets:
            vr.require(isinstance(target, dict), f"{fixture_id}: target must be an object")
            name = target.get("target")
            vr.require(isinstance(name, str) and name, f"{fixture_id}: target name missing")
            vr.require(name not in target_names, f"{fixture_id}: duplicate target {name}")
            target_names.add(name)
            identity = target.get("identity_disposition")
            construct = target.get("construct_disposition")
            causal = target.get("causal_disposition")
            role = target.get("evidence_role")
            vr.require(identity in IDENTITY, f"{fixture_id}.{name}: invalid identity disposition {identity}")
            vr.require(construct in CONSTRUCT, f"{fixture_id}.{name}: invalid construct disposition {construct}")
            vr.require(causal in CAUSAL, f"{fixture_id}.{name}: invalid causal disposition {causal}")
            vr.require(role in ROLES, f"{fixture_id}.{name}: invalid evidence role {role}")
            expected_construct = {
                "generated_identity_closed": "admitted",
                "generated_identity_conditional": "admitted",
                "constructed_measurement_identity": "admitted",
                "grouping_handle_only": "grouping_handle_only",
                "identity_unresolved": "underspecified",
                "premise_rejected": "premise_rejected",
            }[identity]
            vr.require(construct == expected_construct, f"{fixture_id}.{name}: identity/construct mapping mismatch")
            found_positive |= causal == "causal_admitted"
            found_negative |= causal == "causal_rejected"
    missing = CRITICAL_FIXTURES - seen
    vr.require(not missing, f"evolution fixtures missing critical cases: {sorted(missing)}")
    vr.require(found_positive, "evolution fixtures need a positive causal control")
    vr.require(found_negative, "evolution fixtures need a causal failure control")


if __name__ == "__main__":
    try:
        validate_manifests()
        validate_cartridge_text()
        validate_fixtures()
    except (vr.ValidationError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"EVOLUTION CARTRIDGE VALIDATION FAILED: {exc}") from exc
    print("evolution cartridge validation passed")
