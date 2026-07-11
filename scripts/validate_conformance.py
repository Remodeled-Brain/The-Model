#!/usr/bin/env python3
"""Validate semantic target-identity and causal decision records plus mutation fixtures."""
from __future__ import annotations
import argparse, copy, hashlib, json, pathlib, re, subprocess, sys
from typing import Any
import target_identity_contract as ti

ROOT=pathlib.Path(__file__).resolve().parents[1]
CONF=ROOT/"conformance"
FIXTURE_FILES=(CONF/"fixtures/generic.json",CONF/"fixtures/neuroscience.json")
RESULTS=CONF/"results"
PASS=CONF/"selftests/pass"; FAIL=CONF/"selftests/fail"
POLICY=CONF/"required_runs.json"; SCHEMA=CONF/"decision_record.schema.json"
MODEL=ROOT/"model"; BUILDER=ROOT/"scripts/build_master_prompt.py"; RUNTIME=MODEL/"dist/the_model_runtime.txt"; KERNEL=MODEL/"kernel/chain_contract.yaml"; CARTRIDGE=MODEL/"cartridges/neuroscience.yaml"

CAUSAL={"causal_admitted","causal_rejected","causal_unresolved","not_a_causal_question"}
CLOSURE={"closed","partial","descriptive_only","source_scale_only","proxy_limited","label_dependent","contested","unresolved","contradicted"}
DESIGN={"observational","longitudinal_observational","natural_experiment","quasi_experimental","interventional","simulation_or_model","synthesis"}
TARGET={"descriptive_distribution","predictive_relation","intervention_to_outcome","endogenous_dependency","etiology_or_origin","mechanism_or_route","cross_scale_translation"}
CONSTRUCT={"construct_independent","construct_indexed","construct_internal"}
CONSTRUCT_DISPOSITION={"admitted","grouping_handle_only","underspecified","premise_rejected"}
MEASURE={"direct_target_measurement","direct_dependency_measurement","proxy","surrogate","composite_or_scale","self_report","model_derived"}
EXPOSURE={"observation_only","dependency_partially_exposed","dependency_directly_exposed"}
LANG={"descriptive","causal","mechanistic","predictive","causal_rejection"}
IDENTITY={"generated_identity_closed","generated_identity_conditional","constructed_measurement_identity","grouping_handle_only","identity_unresolved","premise_rejected"}
IDENTITY_CAUSAL_ELIGIBLE={"generated_identity_closed","generated_identity_conditional","constructed_measurement_identity"}
GENERATOR={"physical_invariant_or_stable_interaction_structure","equation_or_model_defined_state","algorithmic_reconstruction","measurement_or_realization_standard","demonstrated_organism_state_relation","explicit_conditional_construction","none_or_unresolved"}
DATA={"exact_outcome_definition","exact_exposure_or_intervention","baseline_distribution","comparator_or_counterfactual","sample_and_exclusion_flow","effect_distribution","effect_magnitude","uncertainty","overlap_and_response_heterogeneity","missingness_attrition_and_crossover","timing_and_durability","dose_or_exposure_relation","adverse_or_opposing_outcomes","measurement_validity_and_noise","preregistration_outcome_switching_and_analysis_multiplicity","replication_and_condition_stability"}
INTERVENTION={"manipulation_integrity","valid_comparator_or_counterfactual","temporal_precedence","measurement_validity","effect_magnitude_and_full_response_distribution","bounded_or_generated_heterogeneity","specificity_against_relevant_alternative_routes","durability_appropriate_to_claim","attrition_missingness_and_crossover_bounded","replication_or_internal_strength_proportionate_to_claim_scope","no_stronger_disconfirmation"}
OBSERVATIONAL={"construct_independent_target_and_measurement","temporal_order_appropriate_to_claim","relation_discriminates_proposed_dependency","stable_direction_and_magnitude","alternative_routes_and_confounding_tested","negative_controls_or_equivalent_failure_probes","practical_magnitude_relative_to_variance_overlap_and_noise","independent_replication_with_distinct_operationalization","required_scale_and_mechanism_bridges_closed"}
EFFECTIVE={"exact_target_outcome","valid_comparator","practical_effect_threshold","full_response_distribution","bounded_nonresponse_and_worsening","bounded_attrition_missingness_and_crossover","durability_matching_claim","adverse_outcome_scope","replication_or_equivalent_internal_strength"}
INDUCES={"temporal_precedence","direct_measurement_of_induced_change","comparator_control","persistence","specificity"}
CAUSAL_WORDS=re.compile(r"\b(cause[sd]?|causing|effective|effectively treats?|treats?|works for|induce[sd]?|inducing|mechanism|mechanistic|drives?|underl(?:y|ies|ain)|mediat(?:e|es|ed|ing)|controls?|normaliz(?:e|es|ed|ing)|responsible for)\b",re.I)
EFFECTIVE_WORDS=re.compile(r"\b(effective|effectively treats?|treats?|works for)\b",re.I)
INDUCES_WORDS=re.compile(r"\b(induce[sd]?|inducing)\b",re.I)

class ConformanceError(RuntimeError):
    def __init__(self,code:str,msg:str): super().__init__(f"{code}: {msg}"); self.code=code; self.message=msg
def req(ok:bool,code:str,msg:str):
    if not ok: raise ConformanceError(code,msg)
def load(path:pathlib.Path)->dict[str,Any]:
    try: value=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as e: raise ConformanceError("JSON_PARSE",f"{path}: {e}") from e
    req(isinstance(value,dict),"JSON_OBJECT_REQUIRED",str(path)); return value
def string(v:Any)->bool: return isinstance(v,str) and bool(v.strip())
def strings(v:Any)->bool: return isinstance(v,list) and all(string(x) for x in v)
def sha(path:pathlib.Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()

def validate_policy():
    schema=load(SCHEMA); req(schema.get("type")=="object","DECISION_SCHEMA_INVALID","schema type")
    required={"schema_version","speaker_intent","target_identities","relations","claims","answer_claim_order"}
    req(required<=set(schema.get("required",[])),"DECISION_SCHEMA_INVALID","required target-identity fields")
    relation_required=set(schema.get("properties",{}).get("relations",{}).get("items",{}).get("required",[]))
    req("target_identity_id" in relation_required,"DECISION_SCHEMA_INVALID","relation target_identity_id")
    policy=load(POLICY).get("policy"); req(isinstance(policy,dict),"ADOPTION_POLICY_REQUIRED","policy")
    req(policy.get("semantic_results_required_for_adoption") is True,"ADOPTION_POLICY_INVALID","semantic results")
    req(set(policy.get("required_fixture_sets",[]))=={"generic","neuroscience"},"ADOPTION_POLICY_INVALID","fixture sets")
    req(policy.get("critical_fixture_failure_tolerance")==0,"ADOPTION_POLICY_INVALID","failure tolerance")
    req(isinstance(policy.get("minimum_independent_runs_per_critical_variant"),int) and policy["minimum_independent_runs_per_critical_variant"]>=1,"ADOPTION_POLICY_INVALID","run count")
    req(policy.get("positive_causal_control_required") is True,"ADOPTION_POLICY_INVALID","positive control")
    return policy

def current_hashes():
    subprocess.run([sys.executable,str(BUILDER)],cwd=ROOT,check=True)
    try: return {"runtime_hash":sha(RUNTIME),"kernel_hash":sha(KERNEL),"cartridge_hash":sha(CARTRIDGE),"target_identity_contract_hash":ti.target_identity_contract_hash()}
    finally:
        RUNTIME.unlink(missing_ok=True)
        if RUNTIME.parent.exists() and not any(RUNTIME.parent.iterdir()): RUNTIME.parent.rmdir()

def validate_speaker_intent(record:dict[str,Any]):
    intent=record.get("speaker_intent")
    req(isinstance(intent,dict),"SPEAKER_INTENT_REQUIRED","speaker_intent")
    for field in ("source_wording","selected_or_inferred_referent","requested_scope"):
        req(string(intent.get(field)),"SPEAKER_INTENT_FIELD_REQUIRED",field)
    for field in ("intended_referent_candidates","distinctions_that_change_answer","unresolved_material_ambiguity"):
        req(strings(intent.get(field)),"SPEAKER_INTENT_LIST_REQUIRED",field)

def target_identities(record:dict[str,Any])->dict[str,dict[str,Any]]:
    rows=record.get("target_identities")
    req(isinstance(rows,list) and rows,"TARGET_IDENTITIES_REQUIRED","target_identities")
    out={}
    expected_map={
        "generated_identity_closed":"admitted",
        "generated_identity_conditional":"admitted",
        "constructed_measurement_identity":"admitted",
        "grouping_handle_only":"grouping_handle_only",
        "identity_unresolved":"underspecified",
        "premise_rejected":"premise_rejected",
    }
    for row in rows:
        req(isinstance(row,dict),"TARGET_IDENTITY_OBJECT_REQUIRED","target identity")
        iid=row.get("id"); req(string(iid),"TARGET_IDENTITY_ID_REQUIRED","id"); req(iid not in out,"DUPLICATE_TARGET_IDENTITY_ID",iid)
        for field in ("source_label","speaker_intended_referent","source_defined_target","generator_pointer","boundary_conditions_and_regime","operational_equivalence_evidence","heterogeneity_generator","transport_status"):
            req(string(row.get(field)),"TARGET_IDENTITY_FIELD_REQUIRED",f"{iid}.{field}")
        for field in ("exact_relations_after_label_removal","measurement_or_construction_operations","identity_breaking_evidence","unresolved_identity_slots"):
            req(strings(row.get(field)),"TARGET_IDENTITY_LIST_REQUIRED",f"{iid}.{field}")
        disposition=row.get("identity_disposition")
        req(disposition in IDENTITY,"INVALID_IDENTITY_DISPOSITION",f"{iid}.{disposition}")
        generator=row.get("generator_type")
        req(generator in GENERATOR,"INVALID_IDENTITY_GENERATOR",f"{iid}.{generator}")
        mapped=row.get("mapped_construct_disposition")
        req(mapped in CONSTRUCT_DISPOSITION,"INVALID_MAPPED_CONSTRUCT_DISPOSITION",f"{iid}.{mapped}")
        req(mapped==expected_map[disposition],"IDENTITY_CONSTRUCT_MAPPING_MISMATCH",iid)
        if disposition in IDENTITY_CAUSAL_ELIGIBLE:
            req(generator!="none_or_unresolved","ADMITTED_IDENTITY_WITHOUT_GENERATOR",iid)
        if disposition=="generated_identity_closed":
            req(not row["unresolved_identity_slots"],"CLOSED_IDENTITY_WITH_OPEN_SLOTS",iid)
        out[iid]=row
    return out

def relations(record:dict[str,Any])->dict[str,dict[str,Any]]:
    rows=record.get("relations"); req(isinstance(rows,list) and rows,"RELATIONS_REQUIRED","relations")
    out={}
    for row in rows:
        req(isinstance(row,dict),"RELATION_OBJECT_REQUIRED","relation")
        rid=row.get("id"); req(string(rid),"RELATION_ID_REQUIRED","id"); req(rid not in out,"DUPLICATE_RELATION_ID",rid)
        out[rid]=row
    return out

def claims(record:dict[str,Any])->dict[str,dict[str,Any]]:
    rows=record.get("claims"); req(isinstance(rows,list) and rows,"CLAIMS_REQUIRED","claims")
    out={}
    for row in rows:
        req(isinstance(row,dict),"CLAIM_OBJECT_REQUIRED","claim")
        cid=row.get("id"); req(string(cid),"CLAIM_ID_REQUIRED","id"); req(cid not in out,"DUPLICATE_CLAIM_ID",cid)
        out[cid]=row
    return out

def validate_relation(r:dict[str,Any],identities:dict[str,dict[str,Any]]):
    rid=r["id"]
    iid=r.get("target_identity_id")
    req(string(iid),"RELATION_TARGET_IDENTITY_REQUIRED",rid)
    req(iid in identities,"RELATION_TARGET_IDENTITY_UNKNOWN",f"{rid}: {iid}")
    identity=identities[iid]
    for field,allowed in (("design_mode",DESIGN),("target_relation",TARGET),("construct_relation",CONSTRUCT),("measurement_relation",MEASURE),("chain_exposure",EXPOSURE),("causal_disposition",CAUSAL),("closure_state",CLOSURE)):
        req(r.get(field) in allowed,"INVALID_RELATION_ENUM",f"{rid}.{field}")
    req(string(r.get("scope")),"RELATION_SCOPE_REQUIRED",rid)
    for f in ("required_checks","passed_checks","failed_checks"): req(strings(r.get(f)),"CHECK_LIST_REQUIRED",f"{rid}.{f}")
    needed=set(r["required_checks"]); passed=set(r["passed_checks"]); failed=set(r["failed_checks"])
    req(not passed&failed,"CHECK_STATE_CONFLICT",rid); req((passed|failed)<=needed,"CHECK_NOT_REQUIRED",rid)
    data=r.get("data"); req(isinstance(data,dict),"RELATION_DATA_REQUIRED",rid)
    missing=DATA-set(data); req(not missing,"RELATION_DATA_FIELDS_MISSING",f"{rid}: {sorted(missing)}")
    req(all(string(data[f]) for f in DATA),"RELATION_DATA_VALUE_MISSING",rid)
    d=r["causal_disposition"]
    if d=="causal_admitted":
        req(identity["identity_disposition"] in IDENTITY_CAUSAL_ELIGIBLE,"CAUSAL_ADMISSION_WITH_UNRESOLVED_IDENTITY",rid)
        req(not failed,"CAUSAL_ADMISSION_WITH_FAILED_CHECKS",rid); req(needed<=passed,"CAUSAL_ADMISSION_WITH_OPEN_CHECKS",rid)
    elif d=="causal_rejected": req(bool(failed),"CAUSAL_REJECTION_WITHOUT_FAILURE",rid)
    elif d=="causal_unresolved":
        req(not failed,"UNRESOLVED_WITH_POSITIVE_FAILURE",rid); req(bool(needed-passed),"UNRESOLVED_WITHOUT_OPEN_CHECK",rid)
    else: req(r["target_relation"]=="descriptive_distribution","NONCAUSAL_DISPOSITION_SCOPE",rid)
    if d!="causal_admitted": return
    if r["design_mode"]=="interventional" and r["target_relation"]=="intervention_to_outcome": req(INTERVENTION<=passed,"INTERVENTION_CAUSAL_BURDEN_OPEN",f"{rid}: {sorted(INTERVENTION-passed)}")
    if r["design_mode"] in {"observational","longitudinal_observational"} and r["target_relation"]!="descriptive_distribution": req(OBSERVATIONAL<=passed,"OBSERVATIONAL_CAUSAL_BURDEN_OPEN",f"{rid}: {sorted(OBSERVATIONAL-passed)}")
    if r["construct_relation"]!="construct_independent": req("construct_escape_complete" in passed,"CONSTRUCT_DEPENDENCE_NOT_ESCAPED",rid)
    if r["measurement_relation"] in {"proxy","surrogate","model_derived"}: req("physical_translation_closed" in passed,"PROXY_CAUSAL_PROMOTION",rid)
    target_checks={"etiology_or_origin":"etiology_independently_closed","endogenous_dependency":"endogenous_route_independently_closed","mechanism_or_route":"physical_dependency_path_closed","cross_scale_translation":"cross_scale_translation_closed","predictive_relation":"predictive_adequacy_closed"}
    check=target_checks.get(r["target_relation"])
    if check: req(check in passed,"TARGET_SCOPE_TRANSFER",f"{rid}: {check}")

def validate_claims(record:dict[str,Any],rels:dict[str,dict[str,Any]]):
    cs=claims(record); order=record.get("answer_claim_order")
    req(strings(order) and bool(order),"ANSWER_CLAIM_ORDER_REQUIRED","answer_claim_order")
    req(len(order)==len(set(order)),"DUPLICATE_ANSWER_CLAIM","answer_claim_order"); req(set(order)<=set(cs),"UNKNOWN_ANSWER_CLAIM",str(set(order)-set(cs)))
    for cid,c in cs.items():
        rid=c.get("relation_id"); req(rid in rels,"CLAIM_RELATION_UNKNOWN",cid)
        cls=c.get("language_class"); text=c.get("text"); req(cls in LANG,"CLAIM_LANGUAGE_CLASS_INVALID",cid); req(string(text),"CLAIM_TEXT_REQUIRED",cid)
        r=rels[rid]; disposition=r["causal_disposition"]; passed=set(r["passed_checks"])
        if cls in {"causal","mechanistic"}: req(disposition=="causal_admitted","CAUSAL_LANGUAGE_WITHOUT_ADMISSION",cid)
        if cls=="causal_rejection": req(disposition=="causal_rejected","CAUSAL_REJECTION_LANGUAGE_MISMATCH",cid)
        if cls=="descriptive" and CAUSAL_WORDS.search(text): raise ConformanceError("CAUSAL_VERB_HIDDEN_AS_DESCRIPTIVE",cid)
        if cls in {"causal","mechanistic"} and EFFECTIVE_WORDS.search(text): req(EFFECTIVE<=passed,"EFFECTIVENESS_LANGUAGE_OVERREACH",f"{cid}: {sorted(EFFECTIVE-passed)}")
        if cls in {"causal","mechanistic"} and INDUCES_WORDS.search(text): req(INDUCES<=passed,"INDUCES_LANGUAGE_OVERREACH",f"{cid}: {sorted(INDUCES-passed)}")
        if cls=="mechanistic": req("physical_dependency_path_closed" in passed,"MECHANISM_LANGUAGE_WITHOUT_ROUTE",cid)

def render_answer(record:dict[str,Any])->str:
    cs=claims(record); return " ".join(cs[cid]["text"].strip() for cid in record["answer_claim_order"]).strip()

def validate_decision_record(record:dict[str,Any]):
    req(record.get("schema_version")=="v1","DECISION_SCHEMA_VERSION","v1 required"); req(string(record.get("query")),"QUERY_REQUIRED","query")
    validate_speaker_intent(record)
    identities=target_identities(record)
    for f in ("admitted_observations","stripped_assertions"): req(isinstance(record.get(f),list) and all(string(x) for x in record[f]),"AUDIT_LIST_REQUIRED",f)
    rels=relations(record)
    for r in rels.values(): validate_relation(r,identities)
    validate_claims(record,rels)

def catalog():
    variants={}; fixtures={}
    for path in FIXTURE_FILES:
        data=load(path); fs=data.get("fixture_set"); req(string(fs),"FIXTURE_SET_REQUIRED",str(path))
        rows=data.get("fixtures"); req(isinstance(rows,list) and rows,"FIXTURES_REQUIRED",str(path))
        for fixture in rows:
            fid=fixture.get("id"); req(string(fid),"FIXTURE_ID_REQUIRED",str(path))
            key=(fs,fid); req(key not in fixtures,"DUPLICATE_FIXTURE_ID",str(key)); fixtures[key]=fixture
            kind=fixture.get("mutation_type"); req(kind in {"single","narrative_invariance","data_sensitivity","scope_separation"},"FIXTURE_MUTATION_TYPE",fid)
            rows2=fixture.get("variants"); req(isinstance(rows2,list) and rows2,"FIXTURE_VARIANTS_REQUIRED",fid)
            seen=set()
            for v in rows2:
                vid=v.get("id"); req(string(vid) and vid not in seen,"FIXTURE_VARIANT_ID",fid); seen.add(vid)
                req(isinstance(v.get("input"),dict) and isinstance(v.get("expected"),dict),"FIXTURE_VARIANT_FIELDS",f"{fid}/{vid}")
                variants[(fs,fid,vid)]=v
            if kind=="narrative_invariance": req(isinstance(fixture.get("invariant_relations"),list) and fixture["invariant_relations"],"INVARIANT_RELATIONS_REQUIRED",fid)
    return variants,fixtures

def validate_expected(record:dict[str,Any],expected:dict[str,Any]):
    rels=relations(record); er=expected.get("relations"); req(isinstance(er,dict) and er,"EXPECTED_RELATIONS_REQUIRED","expected.relations")
    for rid,constraints in er.items():
        req(rid in rels,"EXPECTED_RELATION_MISSING",rid)
        for field,value in constraints.items(): req(rels[rid].get(field)==value,"FIXTURE_EXPECTATION_FAILED",f"{rid}.{field}")
    actual={x.casefold() for x in record.get("stripped_assertions",[])}
    missing=[x for x in expected.get("required_stripped_assertions",[]) if x.casefold() not in actual]
    req(not missing,"REQUIRED_STRIPPED_ASSERTION_MISSING",str(missing))

def validate_result(result:dict[str,Any],variants=None):
    req(result.get("schema_version")=="v1","RESULT_SCHEMA_VERSION","v1 required")
    for f in ("run_id","fixture_set","fixture_id","variant_id"): req(string(result.get(f)),"RESULT_IDENTITY_REQUIRED",f)
    provider=result.get("provider"); req(isinstance(provider,dict),"PROVIDER_METADATA_REQUIRED","provider")
    for f in ("name","model"): req(string(provider.get(f)),"PROVIDER_METADATA_FIELD",f)
    for f in ("runtime_hash","kernel_hash","cartridge_hash","fixture_hash","target_identity_contract_hash"): req(string(provider.get(f)) and re.fullmatch(r"[0-9a-f]{64}",provider[f]) is not None,"PROVIDER_HASH_FIELD",f)
    req(isinstance(provider.get("temperature"),(int,float)),"PROVIDER_METADATA_FIELD","temperature"); req(string(provider.get("seed")),"PROVIDER_METADATA_FIELD","seed")
    record=result.get("decision_record"); req(isinstance(record,dict),"DECISION_RECORD_REQUIRED","decision_record"); validate_decision_record(record)
    req(result.get("rendered_answer")==render_answer(record),"RENDERED_ANSWER_DRIFT","rendered answer")
    if variants is not None:
        key=(result["fixture_set"],result["fixture_id"],result["variant_id"]); req(key in variants,"UNKNOWN_FIXTURE_VARIANT",str(key)); validate_expected(record,variants[key]["expected"])

def projection(record,fixture):
    rels=relations(record); out={}
    for item in fixture["invariant_relations"]:
        rid=item["relation_id"]; req(rid in rels,"INVARIANT_RELATION_MISSING",rid); out[rid]={f:rels[rid].get(f) for f in item["fields"]}
    return out

def validate_mutation_groups(rows,fixtures):
    groups={}
    for row in rows:
        p=row["provider"]; key=(row["run_id"],p["name"],p["model"],row["fixture_set"],row["fixture_id"]); groups.setdefault(key,[]).append(row)
    for key,items in groups.items():
        fixture=fixtures[(key[-2],key[-1])]; expected={v["id"] for v in fixture["variants"]}; present={r["variant_id"] for r in items}
        req(present==expected,"INCOMPLETE_MUTATION_GROUP",str((expected,present)))
        if fixture["mutation_type"]=="narrative_invariance":
            ps=[projection(r["decision_record"],fixture) for r in items]; req(all(p==ps[0] for p in ps[1:]),"NARRATIVE_CHANGED_CAUSAL_RESULT",str(key))

def validate_adoption(rows,fixtures,policy):
    req(bool(rows),"ADOPTION_RESULTS_REQUIRED","no provider results")
    current=current_hashes(); fixture_hashes={path.stem:sha(path) for path in FIXTURE_FILES}
    for row in rows:
        p=row["provider"]
        for field,value in current.items(): req(p.get(field)==value,"STALE_PROVIDER_RESULT",f"{row['fixture_id']}: {field}")
        req(p.get("fixture_hash")==fixture_hashes[row["fixture_set"]],"STALE_PROVIDER_RESULT",f"{row['fixture_id']}: fixture_hash")
    required_sets=set(policy["required_fixture_sets"])
    critical={(fs,fid,v["id"]) for (fs,fid),f in fixtures.items() if fs in required_sets and f.get("critical") for v in f["variants"]}
    minimum=policy["minimum_independent_runs_per_critical_variant"]
    groups={}
    for row in rows:
        p=row["provider"]; groups.setdefault((p["name"],p["model"]),{}).setdefault((row["fixture_set"],row["fixture_id"],row["variant_id"]),set()).add(row["run_id"])
    complete=[]
    for provider,counts in groups.items():
        missing={key:minimum-len(counts.get(key,set())) for key in critical if len(counts.get(key,set()))<minimum}
        if not missing: complete.append(provider)
    req(bool(complete),"ADOPTION_RUN_COUNT_INCOMPLETE",f"need {minimum} complete runs per critical variant for one provider/model")

def set_path(root,path,value):
    parts=path.split("."); target=root
    for part in parts[:-1]: target=target[int(part)] if isinstance(target,list) else target[part]
    last=parts[-1]
    if value=="__DELETE__":
        if isinstance(target,list): del target[int(last)]
        else: del target[last]
    elif isinstance(target,list): target[int(last)]=value
    else: target[last]=value

def selftests():
    for path in sorted(PASS.glob("*.json")): validate_result(load(path))
    for path in sorted(FAIL.glob("*.json")):
        wrapper=load(path); expected=wrapper.get("expected_error_code"); result=wrapper.get("result")
        if result is None and string(wrapper.get("base")):
            result=copy.deepcopy(load((path.parent/wrapper["base"]).resolve()))
            for mutation in wrapper.get("mutations",[]): set_path(result,mutation["path"],mutation["value"])
        req(string(expected) and isinstance(result,dict),"SELFTEST_FORMAT",str(path))
        try: validate_result(result)
        except ConformanceError as e: req(e.code==expected,"SELFTEST_WRONG_FAILURE",f"{path}: {e.code}")
        else: raise ConformanceError("SELFTEST_FALSE_NEGATIVE",str(path))

def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("results",nargs="*",type=pathlib.Path); parser.add_argument("--fixtures-only",action="store_true"); parser.add_argument("--adoption",action="store_true"); args=parser.parse_args()
    try:
        req(not (args.fixtures_only and args.adoption),"ARGUMENT_CONFLICT","fixtures-only with adoption")
        policy=validate_policy(); variants,fixtures=catalog(); selftests()
        if not args.fixtures_only:
            paths=args.results or (sorted(RESULTS.rglob("*.json")) if RESULTS.exists() else []); rows=[]
            for path in paths:
                row=load(path); validate_result(row,variants); rows.append(row)
            if rows: validate_mutation_groups(rows,fixtures)
            if args.adoption: validate_adoption(rows,fixtures,policy)
    except (ConformanceError,subprocess.CalledProcessError,OSError) as e:
        if isinstance(e,ConformanceError): print(f"CONFORMANCE FAILED [{e.code}]: {e.message}",file=sys.stderr)
        else: print(f"CONFORMANCE FAILED: {e}",file=sys.stderr)
        return 1
    print("conformance validation passed"); return 0
if __name__=="__main__": raise SystemExit(main())
