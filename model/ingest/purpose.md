# Ingest Support Runtime

**Status:** CANDIDATE.

## Role

Ingest maintains the evidence substrate used by the question runtime. It extracts the actual data, classifies evidence design and target relation, separates observations from narrative, audits inferential bridges, and assigns relation-specific support roles. It does not define the user’s question or transfer a source conclusion into the final answer.

## Required boundary

Ingest may update available observations, data-supported scope, evidence-family membership, bridge closure, supersession status, chain-segment closure, disconfirmation, and target-specific confidence. It may not silently change the chain kernel, question-compilation grammar, domain cartridge, or settled claim layer.

## Operating sequence

`source -> identity resolution -> data extraction -> design and target classification -> narrative stripping -> bridge audit -> relation-specific validation -> support record -> evidence binder`

Observational evidence begins descriptive or more restricted. Intervention evidence may earn causality for the exact manipulated relation when the comparator, effect distribution, heterogeneity, durability, missingness, measurement, replication, and disconfirmation burden closes. Neither evidence class receives causal status by name.

## Recency

Recent evidence receives retrieval and supersession priority. Recency does not provide causal weight. A newer source supersedes an older relation only when it tests the same target under compatible conditions with stronger, more direct, or disconfirming evidence.

## Output

The ingest runtime emits audited relation-level support records. Canonical integration remains serialized behind explicit adoption.
