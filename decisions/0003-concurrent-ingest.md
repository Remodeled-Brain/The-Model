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

1. **DOI normalization + path-safe encoding** — lowercase, strip resolver prefix, canonical form; DOI is primary `paper_id` when present. Raw DOIs contain `/` and other reserved characters and are **not path-safe**, so the id used as a directory name must be path-safe-encoded (percent-encode or a defined reversible substitution). The human-readable DOI is retained as a field on the record.
2. **Alternate-identifier table** — map PMID/arXiv/preprint ids to the canonical `paper_id`.
3. **Content-hash canonicalization (OPEN — noisy proxy, not solved).** Fallback when no DOI. An *exact* hash of "normalized text" will **not** collide reliably across different PDF-extraction pipelines (OCR, ligatures, hyphenation, figure text), so it can fragment the same paper — the very failure it targets. Treat as an unresolved blocker: needs a near-duplicate/similarity threshold, or explicit reliance on the late-DOI merge path rather than the hash alone.
4. **Late-arriving-DOI merge path** — when an agent later resolves a DOI for a hash-keyed paper, a serialized merge job re-parents the hash tree under the DOI `paper_id` and leaves a redirect.
5. **Pending/quarantine state** — unresolved identity writes to `ingest/_pending/<hash>/…`, never to a canonical `paper_id` path, until resolution.

## Record identity, schema, and crash semantics (revised)

- **Model identity vs run identity — keep them separate.** The `<agent>` path token is **model identity only**: `family/version` (e.g. `claude/opus-4-8`), which is the stable key comparisons group on. **Run identity (`run_id`) is a record field, not a path component** — putting run_id in the path explodes directory cardinality (a new tree per run) and fragments the very comparison inputs this design exists to keep clean. So: path = `ingest/<paper_id>/<family>/<version>/record.yaml`; `run_id`, timestamp, and tool version live inside the record as provenance.
- **Shared `record.yaml` schema, versioned, shipped before any checkpoint.** Checkpoint comparison over unschematized records has no defined meaning. Schema versioning lets comparisons detect and handle format drift.
- **Append-only + supersession (disambiguated).** Records are append-only. Each carries a monotonic `seq` (or ISO timestamp) and an optional `supersedes:` naming the record it replaces. The live record per (paper, model-identity) is chosen by a **serialized derived build** (not by concurrent writers): it is the newest record not named in any `supersedes:`, ties broken by `seq` then content hash. The `current` pointer is an output of that build, never hand-set. Retries append a new record and supersede the old; they never overwrite.
- **Crash/retry = temp-write-then-atomic-rename.** Write to a temp path, `fsync`, then atomic rename into place, so a crash mid-write never leaves a partial canonical record.

## Checkpoint 4 (weighting comparison) — RESERVED, input undecided (blocker)

Checkpoint 4 is **held**: its pre- vs post-consensus input is undecided, and its retirement criterion is ill-posed until that input is fixed. Specifying retirement machinery now would be premature elaboration for an undecided consumer, so it is **not** specified here.

Recorded only as the constraints any future design must satisfy (not adopted):

- **Input decides everything.** Pre-consensus input confounds weighting divergence with ingest divergence (→ likely cut). Post-consensus input makes divergence pure model-to-model variance (→ reframe as model-QA, not data-consensus).
- **If it ever ships,** retirement cannot be retire-on-agreement alone (agreement can be shared bias): it would need reset-on-model-change, reopen-on-drift, and correlation review. But none of that is designed until the input question closes.

## Open blockers (must resolve before adoption)

- **`paper_id` resolution + merge/quarantine policy** — the algorithm and the late-DOI merge/redirect behavior.
- **Path-safe `paper_id` encoding** — the exact reversible DOI→path scheme.
- **Model-identity path key** — confirm `family/version` as the path token, with `run_id` as a record field (not a path component).
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
