#!/usr/bin/env python3
"""Enforce fresh repeated provider conformance before candidate adoption."""
from __future__ import annotations
import argparse, hashlib, pathlib, subprocess, sys
import validate_conformance as vc

ROOT=pathlib.Path(__file__).resolve().parents[1]
CONF=ROOT/"conformance"
POLICY=CONF/"required_runs.json"
SCHEMA=CONF/"decision_record.schema.json"
MODEL=ROOT/"model"
BUILDER=ROOT/"scripts/build_master_prompt.py"
RUNTIME=MODEL/"dist/the_model_runtime.txt"
KERNEL=MODEL/"kernel/chain_contract.yaml"
CARTRIDGE=MODEL/"cartridges/neuroscience.yaml"

def req(ok,code,msg):
    if not ok: raise vc.ConformanceError(code,msg)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def validate_policy():
    schema=vc.load(SCHEMA)
    req(schema.get("type")=="object","DECISION_SCHEMA_INVALID","schema type")
    req({"schema_version","relations","claims","answer_claim_order"}<=set(schema.get("required",[])),"DECISION_SCHEMA_INVALID","required fields")
    policy=vc.load(POLICY).get("policy")
    req(isinstance(policy,dict),"ADOPTION_POLICY_REQUIRED","policy")
    req(policy.get("semantic_results_required_for_adoption") is True,"ADOPTION_POLICY_INVALID","semantic results")
    req(set(policy.get("required_fixture_sets",[]))=={"generic","neuroscience"},"ADOPTION_POLICY_INVALID","fixture sets")
    req(policy.get("critical_fixture_failure_tolerance")==0,"ADOPTION_POLICY_INVALID","failure tolerance")
    count=policy.get("minimum_independent_runs_per_critical_variant")
    req(isinstance(count,int) and count>=1,"ADOPTION_POLICY_INVALID","run count")
    req(policy.get("positive_causal_control_required") is True,"ADOPTION_POLICY_INVALID","positive control")
    return policy

def current_hashes():
    subprocess.run([sys.executable,str(BUILDER)],cwd=ROOT,check=True)
    try:
        return {"runtime_hash":sha(RUNTIME),"kernel_hash":sha(KERNEL),"cartridge_hash":sha(CARTRIDGE)}
    finally:
        RUNTIME.unlink(missing_ok=True)
        if RUNTIME.parent.exists() and not any(RUNTIME.parent.iterdir()): RUNTIME.parent.rmdir()

def validate_adoption(rows,fixtures,policy):
    req(bool(rows),"ADOPTION_RESULTS_REQUIRED","no provider results")
    current=current_hashes()
    fixture_hashes={path.stem:sha(path) for path in vc.FIXTURE_FILES}
    for row in rows:
        provider=row["provider"]
        for field,value in current.items():
            req(provider.get(field)==value,"STALE_PROVIDER_RESULT",f"{row['fixture_id']}: {field}")
        req(provider.get("fixture_hash")==fixture_hashes[row["fixture_set"]],"STALE_PROVIDER_RESULT",f"{row['fixture_id']}: fixture_hash")

    required_sets=set(policy["required_fixture_sets"])
    critical={(fixture_set,fixture_id,variant["id"])
              for (fixture_set,fixture_id),fixture in fixtures.items()
              if fixture_set in required_sets and fixture.get("critical")
              for variant in fixture["variants"]}
    minimum=policy["minimum_independent_runs_per_critical_variant"]
    groups={}
    for row in rows:
        provider=row["provider"]
        key=(provider["name"],provider["model"])
        variant=(row["fixture_set"],row["fixture_id"],row["variant_id"])
        groups.setdefault(key,{}).setdefault(variant,set()).add(row["run_id"])

    complete=[]; diagnostics={}
    for provider,counts in groups.items():
        missing={key:minimum-len(counts.get(key,set())) for key in critical if len(counts.get(key,set()))<minimum}
        diagnostics[provider]=missing
        if not missing: complete.append(provider)
    req(bool(complete),"ADOPTION_RUN_COUNT_INCOMPLETE",f"need {minimum} complete fresh runs per critical variant for one provider/model: {diagnostics}")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("results",nargs="*",type=pathlib.Path)
    parser.add_argument("--policy-only",action="store_true")
    args=parser.parse_args()
    try:
        policy=validate_policy(); variants,fixtures=vc.catalog(); vc.selftests()
        if not args.policy_only:
            paths=args.results or (sorted(vc.RESULTS.rglob("*.json")) if vc.RESULTS.exists() else [])
            rows=[]
            for path in paths:
                row=vc.load(path); vc.validate_result(row,variants); rows.append(row)
            if rows: vc.validate_mutation_groups(rows,fixtures)
            validate_adoption(rows,fixtures,policy)
    except (vc.ConformanceError,subprocess.CalledProcessError,OSError) as exc:
        if isinstance(exc,vc.ConformanceError):
            print(f"ADOPTION CONFORMANCE FAILED [{exc.code}]: {exc.message}",file=sys.stderr)
        else:
            print(f"ADOPTION CONFORMANCE FAILED: {exc}",file=sys.stderr)
        return 1
    print("adoption conformance validation passed")
    return 0
if __name__=="__main__": raise SystemExit(main())
