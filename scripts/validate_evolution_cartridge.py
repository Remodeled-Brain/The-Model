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
PHYSICAL_MODULE = "cartridges/evolution_physical_continuity.yaml"
FIXTURES = MODEL / "cartridges" / "evolution_fixtures.json"
SEMANTIC_FIXTURES = ROOT / "conformance" / "fixtures" / "evolution.json"
RUNTIME = MODEL / "manifests" / "runtime.json"
INGEST = MODEL / "manifests" / "ingest.json"
GENERIC_FIXTURES = (
    MODEL / "runtime" / "fixtures.json",
    MODEL / "ingest" / "fixtures.json",
    MODEL / "kernel" / "evidence_admission_fixtures.json",
)

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
CONSTRUCT_RELATIONS = {"construct_independent", "construct_indexed", "construct_internal"}
CRITICAL_FIXTURES = {
    "evo-descriptive-frequency-change",
    "evo-selection-attribution-with-open-alternatives",
    "evo-manipulated-regime-selection-positive-control",
    "evo-drift-positive-control",
    "evo-neutrality-from-nonsignificance",
    "evo-fitness-formal-shortcut-identity-control",
    "evo-constructed-and-grouped-quantity-identities",
    "evo-surface-vocabulary-inspection-only",
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
EXPECTED_CAUSAL_CONTROLS = {
    "evo-manipulated-regime-selection-positive-control": "causal_admitted",
    "evo-drift-positive-control": "causal_admitted",
    "evo-historical-adaptation-positive-control": "causal_admitted",
    "evo-selection-attribution-with-open-alternatives": "causal_rejected",
    "evo-neutrality-from-nonsignificance": "causal_rejected",
}
SEMANTIC_CRITICAL_FIXTURES = {
    "evolution-selection-data-sensitivity",
    "evolution-historical-adaptation-data-sensitivity",
    "evolution-drift-neutrality-scope-separation",
    "evolution-fitness-identity-separation",
    "evolution-dependence-scope-separation",
}
DOMAIN_LEAK_TERMS = {
    "natural selection",
    "fitness",
    "allele",
    "homology",
    "phylogeny",
    "genotype",
    "gene flow",
    "adaptation",
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
        physical = manifest.get("physical_continuity_modules", [])
        vr.require(MODULES <= set(domain), f"{path.name}: evolution modules missing")
        vr.require(PHYSICAL_MODULE in physical, f"{path.name}: evolution physical module not registered")
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
    identities_seen: set[str] = set()
    causal_by_fixture: dict[str, set[str]] = {}
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
            construct_relation = target.get("construct_relation")
            if construct_relation is not None:
                vr.require(
                    construct_relation in CONSTRUCT_RELATIONS,
                    f"{fixture_id}.{name}: invalid construct relation {construct_relation}",
                )
            expected_construct = {
                "generated_identity_closed": "admitted",
                "generated_identity_conditional": "admitted",
                "constructed_measurement_identity": "admitted",
                "grouping_handle_only": "grouping_handle_only",
                "identity_unresolved": "underspecified",
                "premise_rejected": "premise_rejected",
            }[identity]
            vr.require(construct == expected_construct, f"{fixture_id}.{name}: identity/construct mapping mismatch")
            identities_seen.add(identity)
            causal_by_fixture.setdefault(fixture_id, set()).add(causal)
    missing = CRITICAL_FIXTURES - seen
    vr.require(not missing, f"evolution fixtures missing critical cases: {sorted(missing)}")
    required_identities = {
        "generated_identity_conditional",
        "constructed_measurement_identity",
        "grouping_handle_only",
        "identity_unresolved",
        "premise_rejected",
    }
    vr.require(
        required_identities <= identities_seen,
        f"evolution fixture identity branches missing: {sorted(required_identities - identities_seen)}",
    )
    for fixture_id, disposition in EXPECTED_CAUSAL_CONTROLS.items():
        vr.require(
            disposition in causal_by_fixture.get(fixture_id, set()),
            f"{fixture_id}: expected causal control {disposition} missing",
        )


def validate_semantic_fixtures() -> None:
    data = vr.load_json(SEMANTIC_FIXTURES)
    vr.require(data.get("fixture_set") == "evolution", "evolution semantic fixture set missing")
    fixtures = data.get("fixtures")
    vr.require(isinstance(fixtures, list) and fixtures, "evolution semantic fixtures missing")
    ids = {item.get("id") for item in fixtures if isinstance(item, dict)}
    missing = SEMANTIC_CRITICAL_FIXTURES - ids
    vr.require(not missing, f"evolution semantic fixtures missing critical cases: {sorted(missing)}")
    for fixture in fixtures:
        vr.require(fixture.get("critical") is True, f"{fixture.get('id')}: evolution semantic fixture must be critical")


def validate_generic_domain_separation() -> None:
    for path in GENERIC_FIXTURES:
        text = path.read_text(encoding="utf-8").casefold()
        leaked = sorted(term for term in DOMAIN_LEAK_TERMS if term in text)
        vr.require(
            not leaked,
            f"evolution terms leaked into generic fixtures {path.relative_to(ROOT)}: {leaked}",
        )


if __name__ == "__main__":
    try:
        validate_manifests()
        validate_cartridge_text()
        validate_fixtures()
        validate_semantic_fixtures()
        validate_generic_domain_separation()
    except (vr.ValidationError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"EVOLUTION CARTRIDGE VALIDATION FAILED: {exc}") from exc
    print("evolution cartridge validation passed")
