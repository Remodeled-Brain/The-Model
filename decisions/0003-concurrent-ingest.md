# ADR 0003 — Concurrent multi-LLM ingest (CANDIDATE)

**Date:** 2026-07-05
**Status:** CANDIDATE — not adopted. Recorded for the other LLMs to stress-test before any adoption. Per project rules, treat as candidate, not integrated. Revised 2026-07-05 to absorb the Opus 4.8 adversarial review (see `docs/reviews/2026-07-05-opus-4-8-v0-05-v4-before-patch-review.md`); the revisions are themselves candidate.

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
   Different agents write different files, so simultaneous work is conflict-free *for the leaf record only* (see the concurrency scope note below), and the per-agent duplication needed for each comparison is preserved automatically.
2. **`paper_id` is a canonical identifier resolved before any write** — see *Identity resolution* below. DOI is primary; content hash is a fallback; unresolved identity goes to a quarantine state, never to a canonical path.
3. **Records are append-only with explicit supersession on the hot path.** No agent edits another agent's record or any shared file during a replicated pass. See *Record identity, schema, and crash semantics*.
4. **Aggregates/indexes are serialized derived builds** — generated from records by a single writer, never hand-edited and never written concurrently. This includes the coverage view of which agents have covered which papers.
5. **Two comparison checkpoints:** after ingest (heavy, durable) and after weighting (light, provisional). The weighting checkpoint exists only to hedge model uncertainty in early versions; its input and retirement are specified below.
6. **Canonical-truth changes (integration/promotion) stay serialized** behind explicit adoption, exactly as the current model requires.

## Concurrency scope (revised)

"Conflict-free by construction" holds **only for disjoint leaf record files**. It does **not** hold for generated indexes, aggregate files, or the substrate's own concurrency unit. Explicit handling:

- **Substrate = git (for now).** Git's concurrency unit is the commit / index / ref, not the file. Disjoint paths prevent *content* merge conflicts but not `index.lock` contention or non-fast-forward push rejection. Rule: agents commit their own leaf records; **index/aggregate builds run as a single-writer serialized job**, not inside each agent's hot path. Push contention is handled by `git pull --rebase` then retry, per CONTRIBUTING §8; never force-push `main`.
- **Prior Nextcloud concern is stale.** ADR 0002 makes sync GitHub-only, so the earlier "sync conflict-copy" critique does not apply. The git-concurrency critique above stands.
- **Migration trigger (git → DB).** Move the hot path off git when any of: record count > ~100k, full index rebuild > ~60 s, or `git status`/index-op latency becomes the bottleneck in a run. Exact thresholds to be confirmed against real runs (open blocker).

## Identity resolution (revised — the real conflict source)

Two agents can independently assign different ids to the same paper (DOI vs preprint vs PDF-render variant), fragmenting one paper into multiple record trees. Resolve identity **before** writing a canonical path:

1. **DOI normalization** — lowercase, strip resolver prefix, canonical form; DOI is primary `paper_id` when present.
2. **Alternate-identifier table** — map PMID/arXiv/preprint ids to the canonical `paper_id`.
3. **Content-hash canonicalization** — fallback when no DOI: hash normalized text (strip whitespace, encoding, and PDF-render variance) so re-exports of the same paper collide rather than fragment.
4. **Late-arriving-DOI merge path** — when an agent later resolves a DOI for a hash-keyed paper, a serialized merge job re-parents the hash tree under the DOI `paper_id` and leaves a redirect.
5. **Pending/quarantine state** — unresolved identity writes to `ingest/_pending/<hash>/…`, never to a canonical `paper_id` path, until resolution.

## Record identity, schema, and crash semantics (revised)

- **`<agent>` granularity.** `<agent>` is not just "claude"/"chatgpt". It is a composite key `family/version/run_id` (e.g. `claude/opus-4-8/2026-07-05T…`). Weighting comparison across unpinned model versions is otherwise meaningless.
- **Shared `record.yaml` schema, versioned, shipped before any checkpoint.** Checkpoint comparison over unschematized records has no defined meaning. Schema versioning lets comparisons detect and handle format drift.
- **Append-only + supersession.** Records are append-only; a `supersedes:` field plus a generated `current` pointer selects the live record per (paper, agent). Retries do not silently overwrite.
- **Crash/retry = temp-write-then-atomic-rename.** Write to a temp path, `fsync`, then atomic rename into place, so a crash mid-write never leaves a partial canonical record.

## Checkpoint 4 (weighting comparison) — specified

- **Input must be stated.** If checkpoint 4 runs on **pre-consensus** ingest, weighting divergence is confounded with ingest divergence and the retirement criterion is ill-posed → in that case **hold or cut**. If it runs on **post-consensus** ingest, all agents weight identical input, so divergence is model-to-model scoring variance → **reframe checkpoint 4 as model-QA, not data-consensus.**
- **Retirement guards.** Retire-on-agreement is unsafe for swappable/correlated LLMs. Any retirement criterion must include: reset-on-model-change, reopen-on-drift, disagreement sampling, and bias/correlation review (agreement can be shared bias, not correctness). A retire-only, never-reopen gate is not acceptable for a non-stationary agent set.

## Open blockers (must resolve before adoption)

- **`paper_id` resolution + merge/quarantine policy** — the algorithm and the late-DOI merge/redirect behavior.
- **`<agent>` composite-key format** — exact `family/version/run_id` encoding.
- **`record.yaml` schema v1** — fields and version marker, shipped before any checkpoint.
- **Append-only vs supersession details** — `current`-pointer generation and conflict handling.
- **Substrate + migration trigger numbers** — confirm the git→DB thresholds against real runs.
- **Checkpoint 4 input (pre- vs post-consensus) and framing** — blocking; if unanswerable, hold or cut the checkpoint.
- **Retirement metric + guards** — concrete disagreement metric and the reset/reopen/correlation rules.
- **Consensus mechanisms (checkpoints 2 and 4)** — still deferred to ~v0.07; this ADR only reserves their place.

## Consequences

- Simultaneous ingest and weighting are safe **at the leaf-record level** with no locking; index/aggregate builds are serialized, and push contention uses rebase-and-retry.
- Every agent's take on paper X sits together under `ingest/<paper_id>/` (and `weighting/<paper_id>/`) once identity is canonicalized, so both comparisons have clean, non-fragmented inputs.
- The weighting checkpoint is deliberately temporary and now carries an explicit input spec and retirement guards, so it neither calcifies nor retires unsafely.
- Nothing here adopts consensus, weighting, or integration; those remain candidate future passes.
