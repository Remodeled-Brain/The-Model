# The Model

A platform-agnostic scaffold developed collaboratively across multiple LLMs. The repository is the shared source of truth so provider copies do not silently diverge.

## Purpose

The Model rejects invalid constructs and failed causal propositions before reconstruction. Questions expressed through folklore, reified categories, hidden operators, or incomplete causal language enter a construct-admission gate. Hard causality questions also enter a causal-admission gate.

The evidence burden is deliberately inverted. Scientific records do not enter as neutral evidence. Construct-indexed work starts `label_dependent`, proxy work starts `proxy_limited`, and treatment-response records are limited to the measured intervention-outcome relation. A record can receive a stronger role only after it affirmatively escapes its presumption and closes the exact inferential bridge and chain segment. Publication count, consensus, peer review, or meta-analysis cannot supply that escape.

Causal admission requires construct coherence, temporal direction, dependency or intervention evidence, route-specific out-of-sample prediction, realistic baseline and comparator performance, bounded heterogeneity, practical magnitude, physical scale translation, independent convergence, and survival of disconfirmation. Failure of any necessary test rejects the requested causal proposition. Heterogeneous, poorly predictive, postdictive, label-selected, proxy-limited, broad-overlap, treatment-response, or practically trivial work cannot be restated as causal contribution, mechanism, defect, dysfunction, or biological basis.

Only admitted questions proceed to physical-chain reconstruction. The runtime binds construct-independent admitted observations and closed inferential bridges to the required path and returns a bounded answer with explicit construct, causal, evidence-admission, closure, and translation status.

Paper ingest is the adaptive evidence-maintenance subsystem under that runtime. It keeps a recency-sensitive corpus current without making live ingest a prerequisite for operation or allowing recency, publication volume, correlated evidence families, proxies, or treatment indication to become causal weight.

## Active structure

| Path | Role |
|------|------|
| `model/00_purpose_and_scope.md` | Candidate purpose and operating boundary |
| `model/kernel/` | Shared physical-chain invariants, construct admission, causal admission, restrictive evidence presumptions, and canonical closure vocabulary |
| `model/runtime/` | Question compiler, answerability planner, evidence binder, answer contract, and machine-readable conformance contracts |
| `model/ingest/` | Adaptive evidence-maintenance architecture, presumptions, gates, routing, records, and fixtures |
| `model/cartridges/` | Domain-specific handle instances and translation vocabulary |
| `model/manifests/runtime.json` | Authoritative candidate question-runtime load graph |
| `model/manifests/ingest.json` | Authoritative candidate ingest load graph |
| `model/manifest.json` | Default-manifest selector only |
| `governance/` | Candidate review and adoption rules |
| `providers/` | Provider-specific adapters and incompatibility notes only |
| `conformance/results/` | Semantic conformance results from standardized provider runs |
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

Validate manifest authority, shared closure vocabulary, ingest-to-kernel crosswalks, cartridge inclusion, capability reach, fixture structure, stale references, and generated outputs:

```bash
python scripts/validate_repo.py
```

Validate the policy invariants that prevent folklore rescue, hard-causality laundering, neutral admission of construct-indexed evidence, proxy promotion, treatment-response inference, and publication-count weighting:

```bash
python scripts/validate_model_policy.py
```

CI validates repository structure, load graphs, vocabulary alignment, fixture shape, generated-artifact integrity, construct rejection, causal rejection, restrictive evidence presumptions, and evidence-weighting policy presence. No provider execution harness exists in this PR. Scientific semantic behavior is therefore not tested by CI. Provider runs must execute the fixture questions separately and record their results under `conformance/results/`.

## Candidate status

This architectural refactor remains candidate until explicitly adopted. See `CONTRIBUTING.md`, `governance/reviewer_protocol.md`, and `governance/candidate_adoption_gate.yaml`.

## Start here for an LLM

Read `CONTRIBUTING.md`, then `model/00_purpose_and_scope.md` and `model/manifest.json`. Load only the manifest required by the operation.
