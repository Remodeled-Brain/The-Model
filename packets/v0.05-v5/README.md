# The Model v0.05-v5 runtime packets

These files are frozen, single-file browser-LLM handoffs generated from the
immutable source ref `v0.05-v5`.

This packet corresponds to Model version `v0.05-v5`.

- `the_model_runtime.txt` is the primary question-reconstruction and answering runtime.
- `ingest_support_runtime.txt` is the paper-ingest and evidence-maintenance runtime.

Upload the packet required for the operation directly to the receiving LLM. The
packet is self-contained for its declared operation. Do not combine the ingest
runtime with ordinary question work unless the requested task actually requires
paper or corpus ingestion.

`manifest.json` records the source commit and SHA-256 digest of each packet.
`SHA256SUMS` provides standard checksum lines.

These files preserve the released specification. They do not certify that any
particular provider follows it correctly.
