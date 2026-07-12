# The Model v0.05-v5-r2 runtime packets

These files are frozen, single-file browser-LLM handoffs generated from the
immutable source ref `c3d6f02536f153a29c995f53c981f46ebbb414bb`.

This is packet revision `r2` for Model version `v0.05-v5`.

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
