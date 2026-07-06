# Opus 4.8 adversarial review — v0.05 v4 ingest packet + ADR 0003 (before patch)

**Type:** Adversarial review record. **Not an adopted decision.** This note documents a stress-test and the verdicts that informed the accompanying candidate patch. It does **not** supersede `AGENTS.md`, ADR 0002, ADR 0003, or the modular model files (`model/00`–`06`); where it disagrees with those, they win. All patched material remains **candidate** until the user explicitly adopts it.

**Reviewer:** Claude Opus 4.8.
**Date:** 2026-07-05.

## Repo state used for review

- origin: `Remodeled-Brain/The-Model`
- commit: `0389819` ("Add candidate ADR 0003: concurrent multi-LLM ingest with two comparison checkpoints")
- branch: `main`
- working tree: one uncommitted changelog fragment present at review time (`changelog.d/2026-07-05-claude-push-access.md`, modified). Network fetch to GitHub was credential-gated from the review environment; the local checkout at commit `0389819` was used as the source of truth.

## Files read

- `AGENTS.md`
- all files in `decisions/` (`0001-repo-structure.md`, `0002-repo-location-and-sync.md`, `0003-concurrent-ingest.md`)
- `model/00_readme_for_llms.md` through `model/06_candidate_ingest_rules_reference.yaml`

## Provenance note on the review inputs

The task framing referenced "two Opus 4.8 before-patch reviews." Only one Opus 4.8 review exists in the originating thread; the converged A/B/C finding list was supplied by ChatGPT as a synthesis. Findings were evaluated on their merits regardless of origin. Where a finding could not be cross-checked against a second independent review, that is noted as convergence-unverified rather than confirmed convergence.

## Converged findings (summary)

**A — Ingest-rule cluster.** One good idea, over-reified and over-multiplied. Collapse the label-family filters into one author-interface stripping / claim-field extraction gate plus a handle-type table; merge the two controlled-sameness rules; keep proxy-promotion and practical-significance separate but with shared assay-level handling; rename the structural noun `residue`; rewrite the "folklore before validation" slogan as an operational Phase A / Phase B split; add an over-stripping guard so descriptive/epi/phenomenological/association/first-report research routes to a positive descriptive channel; add a support-channel aggregation cap so weak notes cannot become node grounding by raw count; extract all claim fields first, then run interacting role tests; add named support-type levels instead of pure discretion.

**B — Failure semantics and adoption gate.** Distinguish mechanism-role hard-zero from paper discard; hard-zero applies to role permissions while preserving provenance, descriptive support, method notes, source-tree handles, and disconfirmation/watch notes; the adoption gate should apply to itself; `hold` needs an exit/expiry; the candidate-review checklist should explicitly include calibration-anchor and nonmechanistic-research-safety checks.

**C — ADR 0003 engineering.** "Conflict-free by construction" holds only for disjoint leaf files, not indexes/commits/pushes/identity; the Nextcloud-specific concern is stale under ADR 0002 but the git-concurrency critique stands; paper-identity canonicalization is the real conflict source; define `paper_id` resolution (DOI normalization, alternate-id table, content-hash canonicalization, late-DOI merge, quarantine); define `<agent>` granularity as family/version/run-id; ship a shared `record.yaml` schema before checkpoints; define append-only vs supersession; define crash/retry (temp-write-then-atomic-rename); serialized derived indexes; a concrete git→DB migration trigger; specify checkpoint-4 input (pre/post consensus) or hold/cut it, and reframe as model-QA if it survives; retire-on-agreement needs reset-on-model-change, reopen-on-drift, disagreement sampling, and correlation review.

## Verdicts

**Accept:** A1, A3, A4, A7, A8, A10, A11, A12, A13; B1, B2, B3, B4; C1, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13.

**Accept with edits:**
- A2 — collapse applies to the label family; route/evidence gates stay separate in Phase B, not folded into one gate.
- A6 — rename `residue`; also tag the `terminology_guard.prefer` nouns (`transition-control surface`, etc.) as descriptive handles, not causal objects, but retain them.
- A14 / B5 — add *named support-type levels* and two missing checklist items (calibration-anchor, nonmechanistic-research-safety); reject numeric calibration anchors as out of scope for this candidate (non-goal in `model/01`).

**Hold:**
- A5 — do **not** merge `PROXY_PROMOTION_GATE` and `PRACTICAL_SIGNIFICANCE_GATE`; they are orthogonal (mechanistic translation vs effect magnitude). Kept separate with a shared `assay_level_cap` output. Held the merge, patched the separation.
- B "gate applies to itself" beyond a single trigger line — the existing gate 04 already covers external-model proposals; no new gate added.

**Reject / mark stale:**
- C2 (Nextcloud portion of the earlier critique) — stale under ADR 0002; withdrawn. Broader git-concurrency critique retained.

## Patched files (all changes candidate)

- `model/03_ingest_architecture.yaml` — two-phase A/B structure; `residue` → `post_strip_claim`; one `strip_and_extract` stage + `handle_types`; updated validator invariants (incl. no-grounding-by-count).
- `model/05_failure_semantics_and_weight_caps.yaml` — `support_type_ladder`; `over_stripping_guard` (descriptive_support as positive role); `aggregation_limit`; hard-zero reframed to role, not paper; merged controlled-sameness route.
- `model/06_candidate_ingest_rules_reference.yaml` — `STRIP_AND_EXTRACT_GATE` + handle-type table; `CONTROLLED_SAMENESS_MISSING_DIFFERENTIATOR` merge; proxy vs practical-significance kept separate; `consolidation_map` for traceability.
- `decisions/0003-concurrent-ingest.md` — kept **CANDIDATE**; added concurrency-scope, identity-resolution, record-schema/crash, and checkpoint-4 sections; open blockers preserved.

Changelog fragment: `changelog.d/2026-07-05-claude-v0-05-v4-ingest-patch.md`.

## Open blockers preserved before adoption

Ingest packet: support-type ladder level boundaries (named, still discretionary); whether the `prefer` nouns need the same verb/product discipline as `post_strip_claim`.

ADR 0003: `paper_id` resolution + merge/quarantine policy; `<agent>` composite-key format; `record.yaml` schema v1; append-only-vs-supersession details; substrate + concrete git→DB migration numbers; checkpoint-4 input (pre/post consensus) and framing; retirement metric + guards. Consensus mechanisms (checkpoints 2 and 4) remain deferred to ~v0.07.

## Second batch — Gemini/ChatGPT ingest queue (candidate)

A follow-up round relayed Gemini feedback (via ChatGPT). It was gated the same way and executed as a queue; all candidate except the manifest split. Changelog: `changelog.d/2026-07-05-claude-ingest-queue-gemini-items.md`.

- **Accept:** automate master-prompt assembly — `model/manifest.json` split into `source_files`/`generated`/`build`; added `scripts/build_master_prompt.py` (recursion-guarded). Manifest `files` array previously listed the generated `10` alongside sources (confirmed hazard).
- **Accept (adopt-ready, low surface):** `gate_intersection_semantics` in `05` — failed-gate notes accumulate; support/grounding/promotion collapse to the most-restrictive surviving cap.
- **Accept (principle) / defer (mechanism):** `visibility_priority_cap` in `05` — qualitative only (volume → watchlist; correlated sources count once); numeric scaling deferred as out-of-scope per non-goal 01. Regression Fixture 11 added to `07`.
- **Modify:** structured `post_strip_claim` — accepted the four-slot taxonomy (`post_strip_claim_form` in `06`, referenced from `03`); trimmed the causal form to a 4-field minimum; candidate.
- **Accept (candidate, blocked):** `model/record_schema_v1.yaml` — `depends_on` ADR 0003 `paper_id` resolution and `<agent>` key; not adoptable until those close.
- **Debt paid:** `07` fixtures resynced from retired rule names to the consolidated names (legend added), correcting drift the first-batch consolidation introduced.

Not done in-sandbox: regeneration of `10_single_file_master_prompt.txt` — build tooling is correct and compiles, but the mounted `manifest.json` was served truncated (file-sync artifact); regenerate with `python scripts/build_master_prompt.py` locally.

## Third round — external reviews reconciled (candidate)

The batch was sent to the other LLMs to gate. Two reviews returned; Fable did not (safeguard bounce). Both remain candidate.

- **ChatGPT** — hold-from-adoption plus concrete defects and a minimal safe-adoption set. Verified independently: `01`/`09` still carried retired `residue`/rule names; `record_schema_v1` omitted `grouping_variable`; `min_across_failed_gates` is not implementable across orthogonal string outputs. Conceded.
- **Gemini** — accept, but on a partial read (opened `00`, `02`, `09`, `03`, `06`, CONTRIBUTING only; never `05`, `07`, `record_schema_v1`, or ADR 0003 — the files holding the defects), and praise-weighted. Treated as confirmation of the core it did read, not as a rebuttal of ChatGPT.

The two **converge on the core** (two-phase A/B split, `STRIP_AND_EXTRACT_GATE`, `post_strip_claim`, failure-routing); divergence is confined to files Gemini skipped.

Applied (changelog `changelog.d/2026-07-05-claude-review-reconciliation.md`): `01`/`09` terminology sync; `grouping_variable` + `not_applicable`/`unresolved` gate states; dropped the unimplementable `min`; `reserved_for_v0_07` on the ladder / visibility cap / claim form / (implicitly) record schema; Phase-A conditions → `handle_flags` adjudicated in Phase B; controlled-sameness non-reject guard; Fixture 11 tightened; ADR 0003 DOI path-safety + model/run identity split + supersession (still CANDIDATE); CONTRIBUTING adopted-vs-candidate clarification.

Still open: checkpoint-4 input/framing, retirement guards, consensus mechanisms (ADR 0003); support-type ladder boundaries.

## Not superseding

This note is an audit record only. `AGENTS.md`, ADR 0002, ADR 0003, and `model/00`–`06` remain authoritative. No claim-layer changes were made. Nothing here is adopted.
