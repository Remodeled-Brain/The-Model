# ADR 0003 — Concurrent multi-LLM ingest (CANDIDATE)

**Date:** 2026-07-05
**Status:** CANDIDATE — not adopted. Recorded for the other LLMs to stress-test before any adoption. Per project rules, treat as candidate, not integrated.

## Context

Multiple LLMs (Claude, ChatGPT, Gemini, GLM, …) will ingest papers **simultaneously**. The design choice is **replication, not partitioning**: every LLM independently ingests the *same* paper. The duplication is deliberate — the differing outputs are the raw material for comparison/consensus.

Intended multi-pass pipeline, with **two comparison checkpoints** in the early stage:

1. **Independent ingest** *(current line of versions)* — each LLM ingests each paper on its own, following the v0.05 ingest architecture (support-layer writes only; folklore filters before validation; no unilateral node grounding).
2. **Ingest comparison / consensus — "thunderdome" (heavy, durable)** *(~v0.07, not specified here)* — the per-agent ingest outputs for the same paper are compared and reconciled toward a consensus. This is the expensive stage.
3. **Weighting** — weights are applied. In the early stage each agent weights independently so the outputs can be compared; this can collapse to a single weighting pass once checkpoint 4 is retired.
4. **Weighting comparison (light, EARLY-STAGE check)** — the per-agent weighting outputs are compared as a cheap confidence check while the underlying models' consistency is still unproven. Much lighter than checkpoint 2. **This checkpoint is expected to retire itself** once weighting proves consistent against the ingest output — see the retirement criterion below.
5. **Integration** — the result is integrated into canonical nodes. Only this step changes canonical truth; it stays serialized behind the existing candidate→adopted gate.

## Decision (candidate)

1. **Record unit = paper × agent, at every replicated pass.**
   - Ingest: `ingest/<paper_id>/<agent>/record.yaml`
   - Weighting (early stage): `weighting/<paper_id>/<agent>/record.yaml`
   Different agents write different files, so simultaneous work is conflict-free *by construction*, and the per-agent duplication needed for each comparison is preserved automatically.
2. **`paper_id` is a stable, shared identifier** — DOI when available, content hash as fallback.
3. **Records are atomic and append-only on the hot path.** No agent edits another agent's record or any shared file during a replicated pass.
4. **Aggregates/indexes are generated from records, never hand-edited** — including a coverage view of which agents have covered which papers.
5. **Two comparison checkpoints:** after ingest (heavy, durable) and after weighting (light, provisional). The weighting checkpoint exists only to hedge model uncertainty in early versions.
6. **Canonical-truth changes (integration/promotion) stay serialized** behind explicit adoption, exactly as the current model requires.

## Open questions (decide when real volume / real runs appear)

- **Storage substrate.** Git now vs a database. Recommendation: git now (atomic files version cleanly and migrate as whole units); move the hot path to a DB only if sustained throughput outgrows git. *Migration trigger: to be defined.*
- **Coverage, not dedup.** Because duplication is intended, no claim/dedup mechanism is needed. A generated **coverage matrix** (which agents covered which papers) is what's useful.
- **Consensus mechanisms.** Both checkpoints (ingest and weighting) are deferred to ~v0.07. Not designed here — this ADR only reserves their place.
- **Retirement criterion for the weighting checkpoint.** Define the consistency threshold (how closely per-agent weighting outputs must agree, over how many papers) at which checkpoint 4 is dropped and weighting collapses to a single pass.

## Consequences

- Simultaneous ingest and weighting by many LLMs are safe with no locking — atomic per-agent files.
- Every agent's take on paper X sits together under `ingest/<paper_id>/` (and `weighting/<paper_id>/`), so both comparisons have clean inputs.
- The weighting checkpoint is deliberately temporary; the ADR names the condition for removing it, so it doesn't calcify into permanent overhead.
- Nothing here adopts consensus, weighting, or integration; those remain candidate future passes.
