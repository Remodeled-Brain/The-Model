# Active ingest subsystem

The files in this directory define adaptive evidence maintenance for The Model. The authoritative load graph is `model/manifests/ingest.json`.

The subsystem is support-layer only. It extracts actual data, classifies evidence design and causal target, audits inferential bridges, and emits relation-level evidence records for the primary runtime binder. It does not compile source questions, transfer source conclusions, or determine the final answer shape.
