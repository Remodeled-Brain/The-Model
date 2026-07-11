#!/usr/bin/env python3
"""Run semantic fixtures through a provider command and validate canonical records."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, pathlib, shlex, subprocess, sys, uuid
from typing import Any
import validate_conformance as vc

ROOT=pathlib.Path(__file__).resolve().parents[1]
MODEL=ROOT/"model"
BUILDER=ROOT/"scripts/build_master_prompt.py"
RUNTIME_MANIFEST=MODEL/"manifests/runtime.json"
RUNTIME_OUTPUT=MODEL/"dist/the_model_runtime.txt"
KERNEL=MODEL/"kernel/chain_contract.yaml"
CARTRIDGE=MODEL/"cartridges/neuroscience.yaml"
SCHEMA=ROOT/"conformance/decision_record.schema.json"

def sha_bytes(value:bytes)->str: return hashlib.sha256(value).hexdigest()
def sha_file(path:pathlib.Path)->str: return sha_bytes(path.read_bytes())
def catalogs():
    rows=[]
    for path in vc.FIXTURE_FILES:
        data=vc.load(path)
        for fixture in data["fixtures"]: rows.append((data["fixture_set"],fixture,path))
    return rows

def build_runtime()->str:
    subprocess.run([sys.executable,str(BUILDER)],cwd=ROOT,check=True)
    if not RUNTIME_OUTPUT.is_file(): raise RuntimeError("runtime build output missing")
    return RUNTIME_OUTPUT.read_text(encoding="utf-8")

def call_provider(command:list[str],payload:dict[str,Any])->dict[str,Any]:
    run=subprocess.run(command,cwd=ROOT,input=json.dumps(payload),text=True,capture_output=True,check=False)
    if run.returncode:
        raise RuntimeError(f"provider exited {run.returncode}\nstdout:\n{run.stdout}\nstderr:\n{run.stderr}")
    try: value=json.loads(run.stdout)
    except json.JSONDecodeError as e: raise RuntimeError(f"provider stdout is not JSON: {e}") from e
    if isinstance(value,dict) and "decision_record" in value: value=value["decision_record"]
    if not isinstance(value,dict): raise RuntimeError("provider must return a decision-record object")
    return value

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--provider-command",required=True,help="command reading fixture payload JSON on stdin")
    p.add_argument("--provider-name",required=True); p.add_argument("--model-id",required=True)
    p.add_argument("--fixture-set",choices=("generic","neuroscience","all"),default="all")
    p.add_argument("--fixture-id",action="append",default=[])
    p.add_argument("--output-dir",type=pathlib.Path,default=ROOT/"conformance/results")
    p.add_argument("--temperature",type=float,default=0.0); p.add_argument("--seed",default="unspecified")
    p.add_argument("--run-id"); p.add_argument("--keep-runtime",action="store_true")
    args=p.parse_args(); command=shlex.split(args.provider_command)
    if not command: print("provider command is empty",file=sys.stderr); return 2
    run_id=args.run_id or dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"-"+uuid.uuid4().hex[:8]
    output_root=args.output_dir/run_id; output_root.mkdir(parents=True,exist_ok=False)
    generated=[]
    try:
        runtime=build_runtime(); schema=vc.load(SCHEMA)
        runtime_hash=sha_bytes(runtime.encode()); kernel_hash=sha_file(KERNEL); cartridge_hash=sha_file(CARTRIDGE)
        selected=[]
        for fixture_set,fixture,path in catalogs():
            if args.fixture_set!="all" and fixture_set!=args.fixture_set: continue
            if args.fixture_id and fixture["id"] not in args.fixture_id: continue
            selected.append((fixture_set,fixture,path))
        if not selected: raise RuntimeError("no fixtures selected")
        variants,_=vc.catalog()
        for fixture_set,fixture,path in selected:
            fixture_hash=sha_file(path)
            for variant in fixture["variants"]:
                payload={
                  "protocol":"the-model-semantic-conformance-v1",
                  "runtime":{"manifest":RUNTIME_MANIFEST.relative_to(ROOT).as_posix(),"sha256":runtime_hash,"text":runtime},
                  "decision_record_schema":schema,
                  "fixture":{"fixture_set":fixture_set,"fixture_id":fixture["id"],"mutation_type":fixture["mutation_type"],"variant_id":variant["id"],"input":variant["input"]},
                  "instruction":"Return only a decision_record JSON object. Extract actual data before narrative, separate every target relation, and place final wording only in structured claims."
                }
                record=call_provider(command,payload)
                result={
                  "schema_version":"v1","run_id":run_id,"fixture_set":fixture_set,"fixture_id":fixture["id"],"variant_id":variant["id"],
                  "provider":{"name":args.provider_name,"model":args.model_id,"runtime_hash":runtime_hash,"kernel_hash":kernel_hash,"cartridge_hash":cartridge_hash,"fixture_hash":fixture_hash,"temperature":args.temperature,"seed":str(args.seed)},
                  "decision_record":record,"rendered_answer":vc.render_answer(record)
                }
                vc.validate_result(result,variants)
                out=output_root/f"{fixture_set}__{fixture['id']}__{variant['id']}.json"
                out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
                generated.append(result)
        _,fixtures=vc.catalog(); vc.validate_mutation_groups(generated,fixtures)
    except (OSError,RuntimeError,subprocess.CalledProcessError,vc.ConformanceError) as e:
        print(f"CONFORMANCE RUN FAILED: {e}",file=sys.stderr); return 1
    finally:
        if not args.keep_runtime:
            RUNTIME_OUTPUT.unlink(missing_ok=True)
            if RUNTIME_OUTPUT.parent.exists() and not any(RUNTIME_OUTPUT.parent.iterdir()): RUNTIME_OUTPUT.parent.rmdir()
    print(f"semantic conformance passed: {len(generated)} results -> {output_root.relative_to(ROOT)}")
    return 0
if __name__=="__main__": raise SystemExit(main())
