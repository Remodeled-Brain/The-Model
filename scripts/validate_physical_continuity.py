#!/usr/bin/env python3
"""Validate physical continuity and metabolic binding in semantic decision records."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import pathlib
import re
import sys
from typing import Any
import validate_conformance as vc
ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = ROOT / 'model'
CONF = ROOT / 'conformance'
SCHEMA = CONF / 'decision_record.schema.json'
RESULTS = CONF / 'results'
PASS = CONF / 'selftests/pass'
FAIL = CONF / 'physical_selftests/fail'
RUNTIME_MANIFEST = MODEL / 'manifests/runtime.json'
INGEST_MANIFEST = MODEL / 'manifests/ingest.json'
PHYSICAL_FILES = (MODEL / 'kernel/physical_continuity.yaml', MODEL / 'runtime/physical_answer_contract.yaml', MODEL / 'ingest/physical_extraction_contract.yaml', MODEL / 'cartridges/neuroscience_physical_continuity.yaml')
EXPLANATORY_SCOPE = {'physical', 'chemical', 'biological', 'behavioral', 'cross_scale', 'descriptive_noncausal'}
CHAIN_STATUS = {'closed', 'partial', 'not_required'}
BIOLOGICAL_SCOPES = {'biological', 'behavioral', 'cross_scale'}
CLAIM_ROLE = {'direct_answer', 'physical_chain', 'scope_limit', 'descriptive_context'}
SEGMENT_FIELDS = {'source_state', 'physical_change', 'carrier_or_constraint', 'target_state', 'timing', 'conditions'}
METABOLIC_FIELDS = {'required', 'status', 'physical_or_chemical_input', 'energetic_or_material_carrier', 'metabolic_state_change', 'biological_operation', 'organism_state_or_behavior'}
PHYSICAL_WORDS = re.compile('\\b(physical|chemical|material|electrical|mechanical|thermal|energy|energetic|ionic|molecular|force|constraint|carrier|substrate)\\b', re.I)
METABOLIC_WORDS = re.compile('\\b(metaboli\\w*|energy-dependent|energetically maintained)\\b', re.I)
MAGIC_METABOLISM = re.compile('\\b(?:metabolism|metabolics|metabolic activity)\\s+(?:cause[sd]?|drives?|controls?|produces?|creates?|makes?)\\b', re.I)
MAGIC_ENERGY = re.compile('\\benergy\\s+(?:cause[sd]?|did|drives?|controls?|produces?|creates?|makes?)\\b', re.I)
VAGUE = {'physics', 'physical forces', 'chemistry', 'biology', 'energy', 'metabolism', 'metabolics', 'metabolic change', 'metabolic activity', 'activation', 'signaling', 'processing', 'regulation', 'network change', 'information'}

class PhysicalConformanceError(RuntimeError):

    def __init__(self, code: str, message: str):
        super().__init__(f'{code}: {message}')
        self.code = code
        self.message = message

def req(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise PhysicalConformanceError(code, message)

def normalized(value: str) -> str:
    return re.sub('[^a-z0-9]+', ' ', value.casefold()).strip()

def get_path(value: Any, path: str) -> Any:
    target = value
    for part in path.split('.'):
        target = target[int(part)] if isinstance(target, list) else target[part]
    return target

def set_path(root: Any, path: str, value: Any) -> None:
    parts = path.split('.')
    target = root
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    last = parts[-1]
    if value == '__DELETE__':
        if isinstance(target, list):
            del target[int(last)]
        else:
            del target[last]
    elif isinstance(target, list):
        target[int(last)] = value
    else:
        target[last] = value

def physical_contract_hash() -> str:
    digest = hashlib.sha256()
    for path in PHYSICAL_FILES:
        digest.update(path.relative_to(ROOT).as_posix().encode('utf-8'))
        digest.update(b'\x00')
        digest.update(path.read_bytes())
        digest.update(b'\x00')
    return digest.hexdigest()

def validate_policy() -> None:
    schema = vc.load(SCHEMA)
    relation_required = set(schema['properties']['relations']['items'].get('required', []))
    req({'explanatory_scope', 'physical_chain'} <= relation_required, 'PHYSICAL_SCHEMA_FIELDS_MISSING', str(relation_required))
    claim_required = set(schema['properties']['claims']['items'].get('required', []))
    req('claim_role' in claim_required, 'PHYSICAL_SCHEMA_CLAIM_ROLE_MISSING', str(claim_required))
    runtime = vc.load(RUNTIME_MANIFEST)
    ingest = vc.load(INGEST_MANIFEST)
    req({'kernel/physical_continuity.yaml', 'runtime/physical_answer_contract.yaml'} <= set(runtime.get('source_files', [])), 'PHYSICAL_RUNTIME_MODULE_NOT_LOADED', runtime.get('name', '?'))
    req({'kernel/physical_continuity.yaml', 'ingest/physical_extraction_contract.yaml'} <= set(ingest.get('source_files', [])), 'PHYSICAL_INGEST_MODULE_NOT_LOADED', ingest.get('name', '?'))
    for manifest in (runtime, ingest):
        req('cartridges/neuroscience_physical_continuity.yaml' in manifest.get('domain_modules', []), 'NEURO_PHYSICAL_MODULE_NOT_LOADED', manifest.get('name', '?'))
    fragments = {PHYSICAL_FILES[0]: ['Every admitted cause, operation, state, constraint, and transition is physical.', 'Metabolics drives biology', 'causal_admission_distinct_from_mechanistic_closure: true', 'no_action_at_a_distance_between_components'], PHYSICAL_FILES[1]: ['exact_intervention_effect_with_partial_route: allowed', 'mechanism_claim_with_partial_route: forbidden', 'metabolism_caused_it'], PHYSICAL_FILES[2]: ['Metabolism or metabolic activity by itself does not close a chain segment.', 'unresolved_physical_chain_slots'], PHYSICAL_FILES[3]: ['Neural tissue has no separate causal currency.', 'metabolically maintained tissue', 'region_X_activated_then_behavior_changed']}
    for path, required in fragments.items():
        text = path.read_text(encoding='utf-8')
        for fragment in required:
            req(fragment in text, 'PHYSICAL_POLICY_FRAGMENT_MISSING', f'{path.relative_to(ROOT)}: {fragment}')

def validate_physical_chain(relation: dict[str, Any]) -> None:
    relation_id = relation['id']
    scope = relation.get('explanatory_scope')
    req(scope in EXPLANATORY_SCOPE, 'INVALID_EXPLANATORY_SCOPE', relation_id)
    chain = relation.get('physical_chain')
    req(isinstance(chain, dict), 'PHYSICAL_CHAIN_REQUIRED', relation_id)
    req(chain.get('universal_floor') == 'all_admitted_causes_and_operations_are_physical', 'UNIVERSAL_PHYSICAL_FLOOR_MISSING', relation_id)
    req(chain.get('status') in CHAIN_STATUS, 'INVALID_PHYSICAL_CHAIN_STATUS', relation_id)
    req(vc.strings(chain.get('unresolved_slots')), 'PHYSICAL_CHAIN_UNRESOLVED_SLOTS', relation_id)
    segments = chain.get('segments')
    req(isinstance(segments, list), 'PHYSICAL_CHAIN_SEGMENTS_REQUIRED', relation_id)
    for index, segment in enumerate(segments):
        req(isinstance(segment, dict), 'PHYSICAL_CHAIN_SEGMENT_OBJECT', f'{relation_id}[{index}]')
        req(SEGMENT_FIELDS <= set(segment), 'PHYSICAL_CHAIN_SEGMENT_FIELDS', f'{relation_id}[{index}]')
        for field in SEGMENT_FIELDS:
            req(vc.string(segment[field]), 'PHYSICAL_CHAIN_SEGMENT_VALUE', f'{relation_id}[{index}].{field}')
        for field in ('physical_change', 'carrier_or_constraint'):
            req(normalized(segment[field]) not in VAGUE, 'MAGIC_PHYSICAL_SEGMENT', f'{relation_id}[{index}].{field}')
    binding = chain.get('metabolic_binding')
    req(isinstance(binding, dict), 'METABOLIC_BINDING_REQUIRED', relation_id)
    req(METABOLIC_FIELDS <= set(binding), 'METABOLIC_BINDING_FIELDS', relation_id)
    req(isinstance(binding.get('required'), bool), 'METABOLIC_BINDING_REQUIRED_FLAG', relation_id)
    req(binding.get('status') in CHAIN_STATUS, 'INVALID_METABOLIC_BINDING_STATUS', relation_id)
    for field in METABOLIC_FIELDS - {'required', 'status'}:
        req(vc.string(binding.get(field)), 'METABOLIC_BINDING_VALUE', f'{relation_id}.{field}')
    for field in ('physical_or_chemical_input', 'energetic_or_material_carrier', 'metabolic_state_change', 'biological_operation'):
        req(normalized(binding[field]) not in VAGUE, 'METABOLISM_AS_MAGIC_OPERATOR', f'{relation_id}.{field}')
    if chain['status'] == 'closed':
        req(not chain['unresolved_slots'], 'CLOSED_CHAIN_HAS_UNRESOLVED_SLOTS', relation_id)
    if binding['status'] == 'closed':
        unresolved = [field for field in METABOLIC_FIELDS - {'required', 'status'} if normalized(binding[field]).startswith('unresolved')]
        req(not unresolved, 'CLOSED_METABOLIC_BINDING_HAS_UNRESOLVED_FIELDS', f'{relation_id}: {unresolved}')
    if scope in BIOLOGICAL_SCOPES:
        req(binding['required'] is True, 'BIOLOGICAL_SCOPE_WITHOUT_METABOLIC_BINDING', relation_id)
        req(chain['status'] != 'not_required', 'BIOLOGICAL_SCOPE_WITHOUT_PHYSICAL_CHAIN', relation_id)
        req(binding['status'] != 'not_required', 'BIOLOGICAL_SCOPE_WITHOUT_METABOLIC_STATUS', relation_id)
        req(bool(segments), 'BIOLOGICAL_SCOPE_WITHOUT_PHYSICAL_SEGMENT', relation_id)
    if relation['causal_disposition'] == 'causal_admitted' and scope != 'descriptive_noncausal':
        req(chain['status'] != 'not_required' and bool(segments), 'CAUSAL_ADMISSION_WITHOUT_PHYSICAL_CHAIN', relation_id)
    if relation['target_relation'] == 'mechanism_or_route' and relation['causal_disposition'] == 'causal_admitted':
        req(chain['status'] == 'closed', 'MECHANISM_WITH_PARTIAL_PHYSICAL_CHAIN', relation_id)
        if scope in BIOLOGICAL_SCOPES:
            req(binding['status'] == 'closed', 'MECHANISM_WITH_PARTIAL_METABOLIC_BINDING', relation_id)

def validate_claims(record: dict[str, Any], relation_map: dict[str, dict[str, Any]]) -> None:
    claim_map = vc.claims(record)
    order = record.get('answer_claim_order')
    req(vc.strings(order) and bool(order), 'ANSWER_CLAIM_ORDER_REQUIRED', 'answer_claim_order')
    req(any((claim_map[cid].get('claim_role') == 'direct_answer' for cid in order)), 'DIRECT_ANSWER_CLAIM_REQUIRED', 'answer_claim_order')
    for claim_id, claim in claim_map.items():
        req(claim.get('claim_role') in CLAIM_ROLE, 'CLAIM_ROLE_INVALID', claim_id)
        text = claim.get('text', '')
        if MAGIC_METABOLISM.search(text) or MAGIC_ENERGY.search(text):
            raise PhysicalConformanceError('METABOLISM_AS_MAGIC_OPERATOR', claim_id)
        relation = relation_map[claim['relation_id']]
        if claim.get('language_class') == 'mechanistic':
            req(relation['physical_chain']['status'] == 'closed', 'MECHANISM_LANGUAGE_WITH_PARTIAL_CHAIN', claim_id)
            if relation['explanatory_scope'] in BIOLOGICAL_SCOPES:
                req(relation['physical_chain']['metabolic_binding']['status'] == 'closed', 'MECHANISM_LANGUAGE_WITH_PARTIAL_METABOLIC_BINDING', claim_id)
    answered = {claim_map[cid]['relation_id'] for cid in order}
    for relation_id in answered:
        relation = relation_map[relation_id]
        if relation['explanatory_scope'] not in BIOLOGICAL_SCOPES:
            continue
        chain_claims = [claim_map[cid] for cid in order if claim_map[cid]['relation_id'] == relation_id and claim_map[cid].get('claim_role') == 'physical_chain']
        req(bool(chain_claims), 'BIOLOGICAL_ANSWER_WITHOUT_PHYSICAL_CHAIN_CLAIM', relation_id)
        for claim in chain_claims:
            req(PHYSICAL_WORDS.search(claim['text']) is not None, 'PHYSICAL_CHAIN_CLAIM_LACKS_PHYSICAL_CARRIER', claim['id'])
            req(METABOLIC_WORDS.search(claim['text']) is not None, 'PHYSICAL_CHAIN_CLAIM_LACKS_METABOLIC_BINDING', claim['id'])

def validate_decision_record(record: dict[str, Any]) -> None:
    relation_map = vc.relations(record)
    for relation in relation_map.values():
        validate_physical_chain(relation)
    validate_claims(record, relation_map)

def validate_expected(record: dict[str, Any], expected: dict[str, Any]) -> None:
    relation_map = vc.relations(record)
    physical = expected.get('physical_relations', {})
    req(isinstance(physical, dict), 'PHYSICAL_EXPECTATIONS_INVALID', 'physical_relations')
    for relation_id, constraints in physical.items():
        req(relation_id in relation_map, 'EXPECTED_PHYSICAL_RELATION_MISSING', relation_id)
        for path, value in constraints.items():
            actual = get_path(relation_map[relation_id], path)
            req(actual == value, 'PHYSICAL_FIXTURE_EXPECTATION_FAILED', f'{relation_id}.{path}: {actual!r} != {value!r}')

def validate_result(result: dict[str, Any], variants: dict[tuple[str, str, str], dict[str, Any]] | None=None) -> None:
    provider = result.get('provider')
    req(isinstance(provider, dict), 'PROVIDER_METADATA_REQUIRED', 'provider')
    value = provider.get('physical_contract_hash')
    req(vc.string(value) and re.fullmatch('[0-9a-f]{64}', value) is not None, 'PHYSICAL_CONTRACT_HASH_REQUIRED', 'provider.physical_contract_hash')
    record = result.get('decision_record')
    req(isinstance(record, dict), 'DECISION_RECORD_REQUIRED', 'decision_record')
    validate_decision_record(record)
    if variants is not None:
        key = (result['fixture_set'], result['fixture_id'], result['variant_id'])
        req(key in variants, 'UNKNOWN_FIXTURE_VARIANT', str(key))
        validate_expected(record, variants[key]['expected'])

def projection(record: dict[str, Any], fixture: dict[str, Any]) -> dict[str, Any]:
    relation_map = vc.relations(record)
    result: dict[str, Any] = {}
    for item in fixture.get('physical_invariant_relations', []):
        relation_id = item['relation_id']
        req(relation_id in relation_map, 'PHYSICAL_INVARIANT_RELATION_MISSING', relation_id)
        result[relation_id] = {field: get_path(relation_map[relation_id], field) for field in item['fields']}
    return result

def validate_mutation_groups(rows: list[dict[str, Any]], fixtures: dict[tuple[str, str], dict[str, Any]]) -> None:
    groups: dict[tuple[str, str, str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        provider = row['provider']
        key = (row['run_id'], provider['name'], provider['model'], row['fixture_set'], row['fixture_id'])
        groups.setdefault(key, []).append(row)
    for key, items in groups.items():
        fixture = fixtures[key[-2], key[-1]]
        if fixture.get('mutation_type') != 'narrative_invariance':
            continue
        projections = [projection(row['decision_record'], fixture) for row in items]
        if projections and projections[0]:
            req(all((item == projections[0] for item in projections[1:])), 'NARRATIVE_CHANGED_PHYSICAL_CHAIN', str(key))

def selftests() -> None:
    for path in sorted(PASS.glob('*.json')):
        result = vc.load(path)
        validate_result(result)
    for path in sorted(FAIL.glob('*.json')):
        wrapper = vc.load(path)
        expected = wrapper.get('expected_error_code')
        result = copy.deepcopy(vc.load((path.parent / wrapper['base']).resolve()))
        for mutation in wrapper.get('mutations', []):
            set_path(result, mutation['path'], mutation['value'])
        try:
            validate_result(result)
        except PhysicalConformanceError as exc:
            req(exc.code == expected, 'PHYSICAL_SELFTEST_WRONG_FAILURE', f'{path}: {exc.code}')
        else:
            raise PhysicalConformanceError('PHYSICAL_SELFTEST_FALSE_NEGATIVE', str(path))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('results', nargs='*', type=pathlib.Path)
    parser.add_argument('--fixtures-only', action='store_true')
    parser.add_argument('--adoption', action='store_true')
    args = parser.parse_args()
    try:
        validate_policy()
        variants, fixtures = vc.catalog()
        selftests()
        if not args.fixtures_only:
            paths = args.results or (sorted(RESULTS.rglob('*.json')) if RESULTS.exists() else [])
            rows = []
            for path in paths:
                row = vc.load(path)
                validate_result(row, variants)
                rows.append(row)
            if rows:
                validate_mutation_groups(rows, fixtures)
            if args.adoption:
                req(bool(rows), 'PHYSICAL_ADOPTION_RESULTS_REQUIRED', 'no provider results')
                current = physical_contract_hash()
                for row in rows:
                    req(row['provider'].get('physical_contract_hash') == current, 'STALE_PHYSICAL_CONFORMANCE_RESULT', row['fixture_id'])
    except (PhysicalConformanceError, OSError, json.JSONDecodeError) as exc:
        if isinstance(exc, PhysicalConformanceError):
            print(f'PHYSICAL CONFORMANCE FAILED [{exc.code}]: {exc.message}', file=sys.stderr)
        else:
            print(f'PHYSICAL CONFORMANCE FAILED: {exc}', file=sys.stderr)
        return 1
    print('physical conformance validation passed')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
