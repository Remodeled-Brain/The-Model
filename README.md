# The Model

**Current release:** v0.05 v5, adopted July 11, 2026.

A platform-agnostic scaffold developed collaboratively across multiple LLMs. The repository is the shared source of truth so provider copies do not silently diverge.

## Purpose

The Model reconstructs target identity, constructs, causal targets, evidence designs, and physical-chain closure before producing an explanatory answer. Published narrative does not enter as evidence by default. The admissible claim is generated from speaker intent, corpus operations, actual observations, comparator, effect distribution, heterogeneity, attrition, durability, measurement validity, and inferential bridges.

Purely observational evidence begins descriptive or more restricted. It earns causal scope only by affirmatively closing the burden appropriate to the exact target relation. Adjustment, recurrence, sample size, peer review, consensus, and meta-analysis do not create a target identity, counterfactual, or physical dependency path.

Intervention evidence is neither automatically causal nor automatically non-causal. A strong controlled manipulation may establish causality for the exact intervention-to-outcome relation when manipulation integrity, comparison, timing, effect magnitude, response consistency, specificity, durability, missingness, replication, and disconfirmation requirements close. That result does not automatically establish target identity, transport, etiology, endogenous mechanism, construct validity, or cross-scale explanation.

Construct-indexed work begins `label_dependent`. Proxy or surrogate work begins `proxy_limited`. These restrictions are independent of study design and remain until the exact identity, construct, or translation burden closes.

## Target identity

Names may compress generated identities. They may not generate identities by compression.

The runtime separates:

- what the asker intends to ask about;
- what each source defines;
- what each source actually measures or constructs; and
- what broader target the source claims.

A named shortcut is accepted when it points to a recoverable generator such as a stable interaction structure, equation, algorithm, measurement standard, reproducible construction, or demonstrated organism-state relation. Its variables, realization procedure, conditions, uncertainty, alternate-construction sensitivity, and transport limits remain attached.

When one name groups non-equivalent measurements, the name remains a grouping handle and the relations are evaluated separately. Heterogeneity preserves common identity only when exposed variables and routes generate and predict the observed variation. Complexity, multidimensionality, heterogeneous presentation, individual variation, context dependence, and task impurity cannot protect an ungenerated identity.

The target-identity rule is fully generic. Domain cartridges provide adversarial examples and specialized measurement vocabulary. They do not provide blacklists or target-identity trigger lists.

## Physical foundation

Every admitted cause, operation, state, constraint, and transition is physical. Chemistry, biology, and behavior remain organized descriptions of the same physical surface rather than separate causal realms. The physical interactions that sustain an organism belong to the same world that forms stars and drives fusion. Scale changes organization and reachable state, not ontology.

At biological scope, causal explanation binds through metabolically maintained state. Answers identify the physical perturbation, its energetic or material carrier, the change in metabolic maintenance, the biological operation, and the organism-state transition or behavior. Missing segments remain explicit. “Metabolism,” “energy,” “activation,” or “signaling” cannot substitute for a specified carrier and state change.

A decisive intervention can establish an exact effect while its internal metabolic route remains partial. The answer preserves the effect and marks the route open rather than rejecting the effect or inventing a mechanism.

## Generic kernel and domain cartridges

The shared kernel owns domain-neutral mechanics:

- target-identity generation and identity shortcuts;
- speaker-intent and corpus-operation separation;
- operational-equivalence and heterogeneity testing;
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

Domain cartridges own specialized examples, failure patterns, translation burdens, and regression fixtures. The neuroscience cartridge contains diagnostic, region-as-agent, psychiatric treatment, rating-scale, imaging, biomarker, stimulation, and named-process examples such as “neuroplasticity.” It also applies physical continuity to neural tissue, energetic and material support, metabolic maintenance, and organism-state transitions. Those cases do not determine the generic identity rule.

## Active structure

| Path | Role |
|------|------|
| `model/00_purpose_and_scope.md` | Adopted v0.05 v5 purpose and operating boundary |
| `model/kernel/` | Shared target-identity, physical-chain, metabolic, construct, causal, and evidence-admission invariants |
| `model/runtime/` | Question compiler, target-identity gate, answerability planner, evidence binder, answer contracts, and domain-neutral fixtures |
| `model/ingest/` | Target-identity crosswalks, data-first evidence maintenance, physical-chain extraction, design gates, routing, and record contracts |
| `model/cartridges/` | Domain-specific examples, physical-chain applications, translation vocabulary, and fixtures |
| `model/manifests/runtime.json` | Authoritative v0.05 v5 question-runtime load graph |
| `model/manifests/ingest.json` | Authoritative v0.05 v5 ingest load graph |
| `model/manifest.json` | Default-manifest selector and release status |
| `governance/` | Review and adoption rules for later changes |
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

Validate evidence policy, target identity, relation-specific causality, generic/domain separation, and required regression fixtures:

```bash
python scripts/validate_model_policy.py
python scripts/validate_target_identity.py
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

CI validates the structural and deterministic harnesses and any committed result bundles. It does not call external providers. Fresh provider conformance remains required before claiming that a specific provider reliably executes the v0.05 v5 contracts:

```bash
python scripts/validate_adoption.py
```

## Release status

v0.05 v5 is the adopted repository snapshot. Structural and deterministic CI passed at release. Live-provider result bundles were not available during adoption, so provider compliance remains unverified and must be established separately for each provider and model version.

## Start here for an LLM

Read `CONTRIBUTING.md`, then `model/00_purpose_and_scope.md` and `model/manifest.json`. Load only the manifest required by the operation.
