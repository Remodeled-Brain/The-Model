# The Model — Purpose and Scope

**Status:** CANDIDATE architectural refactor.

## Primary purpose

The Model transforms questions expressed through folklore, reified categories, hidden operators, or incomplete causal language into questions the empirical chain can answer.

The runtime must:

1. preserve the observation, distinction, or requested relation carried by the source question;
2. identify labels and explanatory handles that cannot perform causal work;
3. reconstruct the question in physical variables, substrates, dependencies, timing, constraints, and organism-state transitions;
4. identify which chain segments must be closed to answer it;
5. bind available evidence to those segments;
6. return a bounded answer with explicit closure and missing-route status; and
7. translate the result back into language responsive to the source question without restoring the removed folklore as mechanism.

## Operating chain

`source question -> handle detection -> observation preservation -> physical reconstruction -> answerability plan -> evidence binding -> bounded answer -> responsive translation`

## Adaptation

Paper ingest is the evidence-maintenance subsystem. It keeps the evidence base current, provenance-bound, and resistant to folklore, proxy promotion, route breaks, and recency-biased academic framing. The runtime must remain operable against a frozen corpus. New ingest may alter available support, chain closure, and confidence. It may not silently alter the chain contract or question-compilation grammar.

## Confidence

Confidence remains attached to the operation that generated it:

- **compilation confidence:** security of the mapping from the source question to physical variables and relations;
- **chain confidence:** closure status for each required empirical segment;
- **translation confidence:** how directly the chain-bound result answers the source wording.

These dimensions must not collapse into one score.

## Non-goals

The Model does not:

- treat scientific labels as causal objects;
- answer by definition sorting in place of chain generation;
- require live paper ingest to operate;
- promote recency, publication venue, citation count, or framework agreement into causal weight;
- erase observations merely because their customary explanation fails; or
- allow evidence maintenance to rewrite settled runtime commitments without explicit adoption.