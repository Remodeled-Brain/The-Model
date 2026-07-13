# Generator-Family Synthesis Review

**Date:** 2026-07-13  
**Provider:** OpenAI  
**Status:** CANDIDATE  
**Verdict:** ACCEPT WITH EDITS, pending structural validation and fresh semantic conformance

## Layer

Evidence-maintenance ingest and synthesis. No claim-layer or kernel causal-content change.

## Fit

The proposal operationalizes the adopted v0.05-v5 commitments that evidence binds by independent family and exact chain contribution rather than paper count, that meta-analysis cannot repair invalid inputs, and that repeated inferential bridges do not create independent convergence.

The added repair ledger extends failure reporting without changing admission status. It converts a failed or unresolved relation into an explicit evidentiary instruction: the missing dependency, the minimal operation needed, the comparator, the independence burden, a passing observation, a disconfirming observation, and the residual scope after a pass.

## Consistency effects

- Preserves target identity as generated rather than named.
- Preserves speaker/corpus separation because family analysis operates only on corpus-defined target relations.
- Preserves narrow observations when a broader family-level claim fails.
- Preserves intervention-to-outcome causality at exact scope.
- Makes independence relation-specific rather than paper-global.
- Preserves the locked asymmetry: shared-prior confirmations are discounted, while a direct valid failure of a necessary shared premise propagates to dependent descendants.
- Adds no domain-specific study, resource, or hard-coded target.

## Risks and guards

### Over-collapse

Risk: papers could be grouped merely because they share a laboratory, author, funder, or broad theory.

Guard: those links are provenance-only unless an operational dependency is identified. Collapse requires a load-bearing generator capable of jointly producing the positive result or jointly invalidating the claim.

### False independence

Risk: different samples or sites could appear independent while sharing the same construct, proxy, pipeline, task, or bridge.

Guard: missing generator information yields `provisional_shared_family`, never inferred independence.

### Non-equivalent pooling

Risk: different operationalizations could be counted as convergent evidence for one target.

Guard: operational equivalence or explicit translation is required before cross-family accumulation. Otherwise the relations remain parallel and bounded.

### Loss of useful recurrence

Risk: collapsing a family could erase legitimate precision, heterogeneity, reliability, or boundary information.

Guard: the contract separately preserves within-family contributions while denying only the closure that recurrence cannot add.

### Repair advice as smuggled evidence

Risk: a plausible proposed experiment could be narrated as though the current claim were nearly closed.

Guard: repair instructions remain non-evidentiary, require both passing and disconfirming observations, preserve residual scope limits, and can be completed only by a new ordinarily admitted record.

### Generic or infeasible instruction

Risk: the runtime could emit “more research,” “larger samples,” or an invented ideal experiment.

Guard: each instruction must name an executable measurement or perturbation, comparator, scale, independence burden, and disconfirmation condition. It must use `currently_non_executable` when no operational test can be specified.

## Calibration requirements

Semantic fixtures must verify:

1. a large correlated literature collapses without losing family-specific estimates;
2. genuinely independent routes accumulate only for an operationally equivalent target;
3. shared-prior confirmation and shared-prior failure are handled asymmetrically;
4. a failed proxy or postdictive bridge emits an operational repair rather than a larger-sample recommendation;
5. target reconstruction precedes repair when one name groups non-equivalent targets;
6. decisive independent causal evidence is not weakened merely because other literature is immature.

## Minimal safe form

The candidate patch adds:

- `model/ingest/generator_family_synthesis.yaml`
- `model/ingest/generator_family_record_extension.yaml`
- ingest-purpose and architecture integration
- generator-family and repair-ledger fixtures
- ingest-manifest entries
- one changelog fragment

No frozen packet is modified. No version increment is created.

## Adoption status

Candidate. Structural validation and fresh provider conformance are still required. The active v0.05-v5 runtime remains adopted; this extension is not represented as adopted merely because it is loaded on the review branch.
