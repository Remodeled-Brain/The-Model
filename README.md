# The Model

A platform-agnostic scaffold developed collaboratively across multiple LLMs. The repository is the shared source of truth so provider copies do not silently diverge.

## Purpose

The Model evaluates constructs, causal targets, evidence designs, and physical-chain closure before producing an explanatory answer. Published narrative does not enter as evidence by default. The admissible claim is generated from the actual observations, comparator, effect distribution, heterogeneity, attrition, durability, measurement validity, and inferential bridges.

Purely observational evidence begins descriptive or more restricted. It earns causal scope only by affirmatively closing the burden appropriate to the exact target relation. Adjustment, recurrence, sample size, peer review, consensus, and meta-analysis do not create a counterfactual or physical dependency path.

Intervention evidence is neither automatically causal nor automatically non-causal. A strong controlled manipulation may establish causality for the exact intervention-to-outcome relation when manipulation integrity, comparison, timing, effect magnitude, response consistency, specificity, durability, missingness, replication, and disconfirmation requirements close. That result does not automatically establish etiology, endogenous mechanism, construct validity, or cross-scale explanation.

Construct-indexed work begins `label_dependent`. Proxy or surrogate work begins `proxy_limited`. These restrictions are independent of study design and remain until the exact construct or translation burden closes.

## Physical foundation

Every admitted cause, operation, state, constraint, and transition is physical. Chemistry, biology, and behavior remain organized descriptions of the same physical surface rather than separate causal realms. The physical interactions that sustain an organism belong to the same world that forms stars and drives fusion. Scale changes organization and reachable state, not ontology.

At biological scope, causal explanation binds through metabolically maintained state. Answers identify the physical perturbation, its energetic or material carrier, the change in metabolic maintenance, the biological operation, and the organism-state transition or behavior. Missing segments remain explicit. “Metabolism,” “energy,” “activation,” or “signaling” cannot substitute for a specified carrier and state change.

A decisive intervention can establish an exact effect while its internal metabolic route remains partial. The answer preserves the effect and marks the route open rather than rejecting the effect or inventing a mechanism.

## Generic kernel and domain cartridges

The shared kernel owns domain-neutral mechanics:

- universal physical continuity;
- biological metabolic binding;
- construct admission;
- target-specific causal admission;
- design and counterfactual classification;
- data-first evidence admission;
- observational and interventional burdens;
- inferential-bridge auditing;
- relation-specific closure and confidence;
- evidence-family weighting.

Domain cartridges own specialized handles, failure patterns, translation burdens, and regression fixtures. The neuroscience cartridge contains diagnostic folklore, region-as-agent, psychiatric treatment, rating-scale, imaging, biomarker, stimulation, and named-process examples such as “neuroplasticity.” It also applies physical continuity to neural tissue, energetic and material support, metabolic maintenance, and organism-state transitions. Those cases are not hard-coded into the generic runtime fixtures.

## Active structure

| Path | Role |
|------|------|
| `model/00_purpose_and_scope.md` | Candidate purpose and operating boundary |
| `model/kernel/` | Shared physical-chain, metabolic, construct, causal, and evidence-admission invariants |
| `model/runtime/` | Question compiler, answerability planner, evidence binder, answer contracts, and domain-neutral fixtures |
| `model/ingest/` | Data-first evidence maintenance, physical-chain extraction, design gates, routing, and record schema |
| `model/cartridges/` | Domain-specific rules, handles, physical-chain applications, translation vocabulary, and fixtures |
| `model/manifests/runtime.json` | Authoritative candidate question-runtime load graph |
| `model/manifests/ingest.json` | Authoritative candidate ingest load graph |
| `model/manifest.json` | Default-manifest selector only |
| `governance/` | Candidate review and adoption rules |
| `providers/` | Provider-specific adapters and incompatibility notes only |
| `conformance/` | Canonical decision-record schema, mutation fixtures, validator self-tests, provider results, and adoption-run policy |
| `decisions/` | Durable architecture decisions |
| `packets/` | Frozen externally shipped bundles |

## Build and validation

Generate the default runtime:

```bash
python scripts/build_master_prompt.py
```

Generate the ingest support runtime:

```bash
python scripts/build_master_prompt.py model/manifests/ingest.json
```

Generated artifacts are written under `model/dist/` and are not committed.

Validate repository structure and builds:

```bash
python scripts/validate_repo.py
```

Validate evidence policy, relation-specific causality, generic/domain separation, and required regression fixtures:

```bash
python scripts/validate_model_policy.py
```

Validate semantic decision records, physical continuity, metabolic binding, deterministic rendering, and validator self-tests:

```bash
python scripts/validate_conformance.py
python scripts/validate_physical_continuity.py --fixtures-only
```

Run semantic fixtures through a provider adapter that reads JSON on stdin and returns one decision-record JSON object:

```bash
python scripts/run_conformance.py \
  --provider-command "python providers/example/adapter.py" \
  --provider-name example \
  --model-id model-version \
  --fixture-set all
```

CI validates both conformance harnesses and any committed result bundles. It does not call external providers. Adoption requires fresh complete result bundles accepted by:

```bash
python scripts/validate_adoption.py
```

## Candidate status

This architectural refactor remains candidate until explicitly adopted. See `CONTRIBUTING.md`, `governance/reviewer_protocol.md`, and `governance/candidate_adoption_gate.yaml`.

## Start here for an LLM

Read `CONTRIBUTING.md`, then `model/00_purpose_and_scope.md` and `model/manifest.json`. Load only the manifest required by the operation.
