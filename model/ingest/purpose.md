# Ingest Support Runtime

**Status:** CANDIDATE.

## Role

Ingest maintains the evidence substrate used by the question runtime. It strips author framing, extracts the physical claim, tests route and translation limits, records provenance, and assigns support roles. It does not define the user’s question or the shape of the final answer.

## Required boundary

Ingest may update available evidence, supersession status, chain-segment closure, disconfirmation, and confidence attached to evidence bindings. It may not silently change the chain kernel, question-compilation grammar, or settled claim layer.

## Operating sequence

`paper -> identity resolution -> author-interface stripping -> claim extraction -> evidence validation -> support record -> evidence binder`

## Recency

Recent evidence receives retrieval and supersession priority. Recency does not provide causal weight. A newer paper replaces an older result only when it measures or tests the same variable, route, dependency, or translation step with stronger or disconfirming evidence.

## Output

The ingest runtime emits reviewed support records. Canonical integration remains serialized behind explicit adoption.
