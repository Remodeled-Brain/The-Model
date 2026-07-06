# Fable 5 adversarial review — v0.05 v4 ingest batch + ADR 0003

**Type:** Adversarial review record. **Not an adopted decision.** Stress-test of the candidate batch relayed at commit `41f11df` (`docs/reviews/2026-07-05-relay-request.md`). Does not supersede `CONTRIBUTING.md`, `AGENTS.md`, ADR 0002/0003, or `model/00`–`07`; where it disagrees, they win. Everything gated here stays **candidate**.

**Reviewer:** Claude Fable 5 (role: reviewer, per `FABLE.md`).
**Date:** 2026-07-06.

## Repo state used for review

- HEAD: `e662e60` on `main`.
- **Working tree is corrupt.** `.git/index` fails sha1 (`fatal: index file corrupt`) and most tracked files on disk are truncated mid-line (e.g. `decisions/0003` is 4341 B on disk vs 8888 B at HEAD; `model/10` is 44767 vs 57639). **All files were therefore read from `HEAD` via `git show`, not the working copy.** Remote fetch is credential-gated from this environment. Repair (rebuild index + `reset --hard HEAD`) was offered and deferred by the user; it is a prerequisite before any commit. No commit made here — `FABLE.md` also forbids Fable committing to `main`.

## Files read (from HEAD)

`CONTRIBUTING.md`, `FABLE.md`, `model/00`, `02`, `03`, `04`, `05`, `06`, `07`, `record_schema_v1.yaml`, `decisions/0003-concurrent-ingest.md`, `docs/reviews/2026-07-05-opus-4-8-...md`, relay request, changelog fragments.

---

## Per-item verdicts

### Item 1 — Phase A/B split (`03`, `06`) · **accept-with-edits (invariant is contradicted)**

The split is a real improvement over the "residue" slogan and the operation/product fusion is correctly named out. But the claim that **Phase A is structural and weighs no evidence is contradicted by its own `fail_if` predicates.**

`03.validator_invariants.admissibility_is_structural_not_evidentiary: true` and `core_principle` ("asks only whether a physical claim survives stripping; it weighs no evidence"). Yet in `06.STRIP_AND_EXTRACT_GATE.handle_types`:

- `diagnostic_label.fail_if`: *"assay cannot generate the diagnostic distinction without prior labels"* and *"label imported before measurement then credited as discovered by measurement"* — both require an evidentiary judgment about what the method can support and about labeling provenance/timing. That is not text-stripping.
- `spectrum_label.fail_if`: *"divergent routes absorbed into a single diagnostic continuum"* — you cannot know routes are divergent without weighing route evidence.

So the split **relocates** part of the admissibility-vs-validation circularity rather than removing it, which is exactly the relay's worry. The purely structural test ("does a `post_strip_claim` exist once the handle term is removed?") is fine in Phase A. The evidentiary predicates are not.

**Minimal safe form:** either (a) move the evidentiary `fail_if`s (assay-can't-generate-distinction; label-imported-then-credited; routes-divergent) to the matching Phase-B gate, leaving Phase A with survives-stripping only; or (b) drop the `not_evidentiary` invariant and rename Phase A "structural + provenance," which is the weaker but honest claim. (a) is preferred — it keeps the invariant true.

### Item 2 — `gate_intersection_semantics` (`05`) · **accept — but NOT independently adopt-ready**

The rule is deterministic and clean: notes union (no info lost), permissions collapse to most-restrictive. Good. Two caveats block the "adopt-ready" label:

1. **It depends on Item 3.** `support_weight: min_across_failed_gates` presupposes a **total order** over support levels. That order exists only in `support_type_ladder` — which is itself a forward-declaration flagged in Item 3 for possible "reserved/cut." If the ladder is cut or its ordering marked reserved, `min_across_...` has no defined meaning. So Item 2 cannot be adopted ahead of, or independently of, the ladder. Bundle them.
2. **Scope of the `min` is ambiguous.** Is the min taken over {failed-gate caps} only, or {failed-gate caps ∪ the source's surviving baseline role}? A source can fail gates B/C yet retain a valid `descriptive_support` role from Phase A. State explicitly that the cap is the min over imposed caps and cannot demote a *surviving* role below what it independently earned.

**Minimal safe form:** adopt jointly with the ladder; add one line fixing the min scope.

### Item 3 — forward-declarations · **split the verdict; do not treat as one bucket**

They are not all the same maturity. Grouping them hides that some have live consumers and some guard a v0.07 consumer.

- **Keep active (live consumer now):** `descriptive_support`, `over_stripping_guard`, `aggregation_limit`. These constrain *current* ingest routing (Type-II guard; no-grounding-by-count). Not forward declarations.
- **Mark "reserved for v0.07" (no current consumer):** the **ordering** semantics of `support_type_ladder` (levels can be named now; the strongest→weakest *order* only feeds Item 2's `min`), `visibility_priority_cap` (asserts an invariant over an *ingest-priority* quantity that nothing computes yet), and `record_schema_v1.yaml` (self-declared BLOCKED on ADR 0003).
- **Portability cost is the reason to reserve, not keep.** Top goal = scaffold survives unchanged across platforms; every named noun/table each LLM must reproduce is drift surface. `record_schema_v1` in particular sits in `model/` looking like active scaffold while guarding a checkpoint consumer that does not exist. Quarantine it (or a `reserved/` marker) until ADR 0003 identity closes.

### Item 4 — proxy vs practical-significance kept separate · **accept (do not merge)**

Genuinely orthogonal axes: `PROXY_PROMOTION_GATE` = mechanistic translation (is the correlate the mechanism?); `PRACTICAL_SIGNIFICANCE_GATE` = magnitude/replication (is the effect real/large?). A large well-replicated effect can be proxy-only; a clean mechanism can have a tiny effect. Merging would fuse two independent failure modes. The shared `assay_level_cap` output is idempotent, so separation is not cosmetic and there is no double-penalty. The reciprocal "distinct from …" cross-references are good anti-drift. Keep as-is.

### Item 5 — deferring numeric visibility scaling + full 8-field causal form · **accept (correct call)**

Numeric scaling without calibration data would be inventing constants — reification of arbitrary numbers, and forbidden by non-goal `01` (no corpus weight from fixtures). Trimming the causal form 8→4 (`substrate_A`, `direction`, `substrate_B`, `unresolved_route_slots`) reduces portable surface while still forcing slotting. Checked: no current fixture requires the dropped fields, so "expand only if fixtures require it" is safe. Correct.

### Item 6 — ADR 0003 · **HOLD; one item is a design bug, not just an open blocker**

Consistent with candidate + open blockers, but three findings need action beyond "confirm still open":

1. **`run_id` must come out of the path key (design correction).** `<agent> = family/version/run_id` as a canonical path component means every run/retry spawns a new leaf: `ingest/<paper_id>/<family>/<version>/<run_id>/record.yaml`. Combined with append-only + supersession, per-(paper,agent) records grow unbounded, and the >100k migration trigger is hit as `N_papers × families × versions × runs`. Worse, it **fragments the comparison unit the design exists to create** — checkpoints want one *current* record per (paper, agent-version), not per run. `run_id` belongs *inside* the record (provenance) and in the supersession chain; the path key should be `family/version`, with the generated `current` pointer selecting the live run. This is an operation/event-vs-record fusion, not merely an unresolved format.
2. **Checkpoint 4 is HOLD, so stop shipping its retirement mechanics.** The ADR itself says the retirement criterion is ill-posed until the pre/post-consensus input is decided, then still specifies retirement guards. Specifying retirement machinery for an undecided consumer is premature elaboration. Collapse checkpoint-4 text to "reserved; input undecided (blocker)" and drop the guard mechanics until the input question closes.
3. **Content-hash identity is stated as if solved; it is a noisy proxy.** Exact-hashing "normalized text" across different PDF-extraction pipelines (OCR, ligatures, hyphenation, figure text) will *not* collide reliably, so it can fragment the same paper — the exact failure it targets. Treat as an unresolved blocker (near-duplicate/similarity threshold, or explicit reliance on the late-DOI merge), not a closed mechanism.

Minor: the "single-writer serialized index job" has no named owner/lock — a coordinator asserted but unmodeled; and `run_id` timestamps need a uniqueness guarantee (UUID) for parallel same-version runs.

### Item 7 — `07` resync + Fixture 11 · **accept; note two couplings**

- **Mapping verified faithful.** All ten retired names in the `07` legend match `06.consolidation_map` exactly (`LABEL_REMOVAL_RESIDUE_TEST`→`STRIP_AND_EXTRACT_GATE`; both controlled-sameness rules→`CONTROLLED_SAMENESS_MISSING_DIFFERENTIATOR`; region/conservation split into Phase-A handle + Phase-B gate; etc.).
- **Fixture 11 tests what it claims** — 40 correlated descriptive papers vs one route-closing source; expects correlated-sources-count-once, volume→watchlist-only, and the route-closer outranking the pile. But it **asserts an "ingest priority" outcome that no mechanism computes** (same gap as Item 3's `visibility_priority_cap`). It is really an LLM-behavior fixture testing the reviewer's application of the guard, not a mechanized rule. Label it as such, and note it cannot pass/fail deterministically until an ingest-priority consumer exists.

---

## Cross-cutting blocker (portability)

`model/10_single_file_master_prompt.txt` is generated and was **not** regenerated after the `03/05/06/07` edits (Opus flagged the truncated `manifest.json`; the on-disk copy is also truncated here). Since pasting `10` into another LLM is the whole portability path, a stale `10` means cross-platform reviewers are reading pre-consolidation rules. Regenerate (`python scripts/build_master_prompt.py`) **after** the working tree is repaired, and before relaying `10` to any other model. Until then, point reviewers at the modular `03`–`07`, not `10`.

## Minimal change set I would actually adopt now

Nothing claim-layer; all candidate. In order: (1) fix the Phase-A `not_evidentiary` contradiction (Item 1a); (2) reserve `record_schema_v1` + ladder-ordering + `visibility_priority_cap`, keep `descriptive_support`/`aggregation_limit`/`over_stripping_guard` active (Item 3); (3) move `run_id` out of the ADR 0003 path key and reduce checkpoint-4 to "reserved" (Item 6.1–6.2). Items 4 and 5 stand as-is. Item 2 adopts only bundled with the ladder.

## Blockers that must close before adoption

Phase-A evidentiary predicates (Item 1); ladder ordering + gate-intersection coupling (Items 2–3); ADR 0003 `run_id`-in-path, checkpoint-4 input, content-hash identity (Item 6); regeneration of `model/10` and repair of the corrupt working tree (cross-cutting).

## Not superseding

Audit record only. Canonical `model/`, `CONTRIBUTING.md`, `AGENTS.md`, ADR 0002/0003 remain authoritative. No claim-layer changes. Nothing adopted.
