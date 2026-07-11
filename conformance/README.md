# Semantic conformance

The canonical runtime output is a structured causal decision record. Provider prose is not authoritative. A provider run returns the decision record defined by `decision_record.schema.json`; `scripts/run_conformance.py` validates that record and renders the final answer deterministically from validated claims.

## Enforcement boundary

The validator fails when a result:

- admits causality with a failed or open required check;
- assigns causal or mechanistic language to a relation that is not `causal_admitted`;
- promotes observational evidence without the observational causal burden;
- promotes a proxy without physical translation;
- transfers an intervention result into etiology, endogenous mechanism, or cross-scale explanation without the target-specific bridge;
- uses `effective`, `treats`, or `works for` without comparator, practical magnitude, full response distribution, nonresponse, attrition, durability, adverse-outcome, and replication checks;
- uses `induces` without temporal precedence, direct measurement, comparator control, persistence, and specificity;
- changes causal or closure state when only the source narrative changes; or
- returns prose that differs from the deterministic rendering of its validated claims.

The fixtures include positive controls. A decisive controlled intervention must be admitted for the exact manipulated relation when its required checks close. Rejecting all causal claims is therefore a conformance failure.

## Run a provider

The provider command reads one JSON payload from stdin and returns one decision-record JSON object on stdout:

```bash
python scripts/run_conformance.py \
  --provider-command "python providers/example/adapter.py" \
  --provider-name example \
  --model-id model-version \
  --fixture-set all
```

Results are written under `conformance/results/<run-id>/`. Validate committed or supplied results with:

```bash
python scripts/validate_conformance.py
python scripts/validate_conformance.py path/to/result.json
```

## Mutation fixtures

Narrative invariance holds the data constant and changes only the source interpretation. The relation disposition and closure state must remain unchanged.

Data sensitivity holds the question and framing constant while changing the actual outcome distribution and controls. The decision must follow the data.

Scope separation places an exact intervention relation beside a broader etiologic or mechanistic claim. Strength may attach only to the relation whose bridge closes.

## Adoption requirement

Structural CI proves that the schemas, fixtures, validator, renderer, and self-tests remain consistent. It does not prove a provider follows them. Candidate adoption requires fresh provider result bundles satisfying `required_runs.json`. Runtime, kernel, cartridge, fixture, or provider-version changes invalidate earlier results.

The strict adoption check verifies current hashes and requires the configured number of complete independent runs for every critical generic and neuroscience variant:

```bash
python scripts/validate_conformance.py --adoption
```
