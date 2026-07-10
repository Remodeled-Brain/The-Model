# The Model

A platform-agnostic scaffold developed collaboratively across multiple LLMs. The repository is the shared source of truth so that no provider copy silently diverges.

## Purpose

The Model transforms questions expressed through folklore, reified categories, hidden operators, or incomplete causal language into chain-bound questions that empirical work can answer. It then binds reviewed evidence to the required physical chain and returns a bounded answer with explicit closure and translation limits.

Paper ingest is essential but subordinate. It is the adaptive evidence-maintenance subsystem that keeps the corpus current and internally consistent. The primary runtime remains operable against a frozen reviewed corpus.

## Repository map

| Path | Role |
|------|------|
| `model/00_purpose_and_scope.md` | Primary purpose and operating boundary |
| `model/kernel/` | Chain invariants shared by runtime and ingest |
| `model/runtime/` | Question compiler, answerability planner, evidence binder, answer contract, and end-to-end fixtures |
| `model/manifests/runtime.json` | Primary runtime load graph |
| `model/manifests/ingest.json` | Adaptive evidence-maintenance load graph |
| `model/cartridges/` | Domain-specific handle instances and translation vocabulary |
| `providers/` | Provider-specific adapters and incompatibility notes only |
| `conformance/results/` | Results from standardized provider tests |
| `decisions/` | Architecture Decision Records |
| `changelog.d/` | One fragment per change, assembled at release |
| `packets/` | Frozen shipped artifacts |

## Default load graph

`model/manifest.json` points to the candidate question runtime. The ingest subsystem is loaded only when evidence maintenance or paper assessment is required.

Generate the default runtime with:

```bash
python scripts/build_master_prompt.py
```

Generate the ingest support runtime with:

```bash
python scripts/build_master_prompt.py model/manifests/ingest.json
```

## Canonical and candidate material

Material remains candidate until explicitly approved. A canonical location does not imply adopted status. See `CONTRIBUTING.md` and `model/04_candidate_rule_adoption_gate.yaml`.

## Start here for an LLM

Read `CONTRIBUTING.md`, then `model/00_purpose_and_scope.md`. Provider-specific instructions belong under `providers/<provider>/`.