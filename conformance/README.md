# Semantic conformance

The canonical runtime output is a structured target-identity and physical-causal decision record. Provider prose is not authoritative. A provider run returns the decision record defined by `decision_record.schema.json`; `scripts/run_conformance.py` validates that record and renders the final answer deterministically from validated claims.

## Enforcement boundary

The validator fails when a result:

- collapses speaker intent, source-defined target, exact measurement, and broader claimed target into one relation;
- binds evidence to a shared name before operational equivalence and a recoverable identity generator close;
- treats unexplained heterogeneity as construct protection;
- uses randomization or effect magnitude to establish target identity or transport;
- admits causality with a failed or open required check;
- assigns causal or mechanistic language to a relation that is not `causal_admitted`;
- promotes observational evidence without the observational causal burden;
- promotes a proxy without physical translation;
- transfers an intervention result into target identity, transport, etiology, endogenous mechanism, or cross-scale explanation without the target-specific bridge;
- uses `effective`, `treats`, or `works for` without comparator, practical magnitude, full response distribution, nonresponse, attrition, durability, adverse-outcome, and replication checks;
- uses `induces` without temporal precedence, direct measurement, comparator control, persistence, and specificity;
- omits a physical chain from a biological or behavioral answer;
- omits metabolic binding at biological scope;
- closes a mechanism while its physical or metabolic route remains partial;
- uses metabolism, energy, activation, signaling, or a named component as a replacement operator;
- changes causal or closure state when only the source narrative changes; or
- returns prose that differs from the deterministic rendering of its validated claims.

The fixtures include positive controls. A decisive controlled intervention must be admitted for the exact manipulated relation when its required checks close. Failure of a broader target identity cannot erase that exact relation. The internal metabolic route may remain partial, but the answer must expose that open route. Rejecting all causal claims is therefore a conformance failure.

## Target-identity reconstruction

Before causal weighting, the runtime must:

1. identify the relation and scope the asker intends;
2. remove the target name and enumerate surviving observations and constructions;
3. reconstruct how each source selects, measures, aggregates, thresholds, and transports the target;
4. locate a recoverable identity generator or leave identity unresolved;
5. compare operationalizations and search for identity-breaking heterogeneity;
6. bind evidence first to each exact measured or constructed relation; and
7. treat broader shared targets as separate relations requiring operational equivalence and transport.

A scientific shortcut can pass when its generator is recoverable and scope-bounded. A familiar word, validated scale, factor structure, repeated citation, or intervention response cannot create identity.

The generic fixtures test target identity before evidence, recoverable shortcuts, speaker/corpus mismatch, unexplained heterogeneity, and preservation of decisive narrow effects. The neuroscience fixture applies the same generic rule to the stimulation/procrastination paper without relying on a term blacklist.

## Physical decision record

Each relation records:

- explanatory scope;
- universal physical-floor commitment;
- physical-chain status;
- explicit physical segments;
- unresolved segments and joins;
- whether metabolic binding is required;
- physical or chemical input;
- energetic or material carrier;
- metabolic state change;
- biological operation; and
- organism-state transition or behavior.

Biological and behavioral answers must include a rendered `physical_chain` claim. A bare statement such as “metabolism caused it” fails validation.

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
python scripts/validate_target_identity.py
python scripts/validate_conformance.py
python scripts/validate_physical_continuity.py
```

## Mutation fixtures

Narrative invariance holds the data constant and changes only the source interpretation. The relation disposition, closure state, explanatory scope, physical-chain status, and metabolic-binding status must remain unchanged.

Data sensitivity holds the question and framing constant while changing the actual outcome distribution and controls. The decision must follow the data.

Scope separation places an exact intervention relation beside a broader target-identity, etiologic, transport, or mechanistic claim. Strength may attach only to the relation whose bridge closes.

Physical-chain fixtures hold a component-to-outcome narrative against missing carrier, energetic, metabolic, and state-transition evidence. The result must retain the observation and expose the open chain rather than inventing action at a distance.

## Adoption requirement

Structural CI proves that the schemas, fixtures, validators, renderer, target-identity modules, physical-continuity modules, and self-tests remain consistent. It does not prove a provider follows them. Candidate adoption requires fresh provider result bundles satisfying `required_runs.json`. Runtime, kernel, cartridge, fixture, physical-contract, or provider-version changes invalidate earlier results.

The strict adoption check verifies current hashes and requires the configured number of complete independent runs for every critical generic and neuroscience variant:

```bash
python scripts/validate_adoption.py
```
