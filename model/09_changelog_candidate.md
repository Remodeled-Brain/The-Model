# v0.05 v4 Candidate Changelog

## Status

Candidate. Not adopted unless explicitly approved.

## Summary

v0.05 v4 candidate work shifts paper ingest toward admissibility-before-validation. The model should strip folklore and regional interface text before validation and node mapping.

## Added candidate principle

INGEST.PRINCIPLE.05v4:

Ingest runs in two phases. Phase A (admissibility) strips folklore and regional interface text and extracts claim fields — measured substrate, measured variable, grouping variable, and the `post_strip_claim` that remains once labels are treated as handles. Phase B (validation) then weights evidence and assigns a role. Only the extracted `post_strip_claim` may map to model nodes, and only after Phase B. Diagnostic labels, region labels, biomarker labels, spectrum labels, and conserved-region labels are handles only. They cannot perform causal work.

## Added candidate ingest ordering (two-phase)

Phase A (admissibility, structural):

- strip_author_interface_text
- run_strip_and_extract_gate  (emits post_strip_claim + handle flags; no evidence weighting)

Phase B (validation, on extracted fields):

- controlled_sameness_missing_differentiator
- region_source_closure
- conservation_dependency
- proxy_promotion
- practical_significance
- map_post_strip_claim_to_nodes
- write_support_layer_only
- mark_promotion_candidates_only_after_gates_pass

## Added candidate rule cluster (consolidated)

- STRIP_AND_EXTRACT_GATE (Phase A; subsumes the former LABEL_REMOVAL_RESIDUE_TEST, FOLKLORE_FILTER_DIAGNOSTIC_LABEL, SPECTRUM_COMPRESSION_FILTER, CONTROLLER_LANGUAGE_FILTER, biomarker filter, region-label stripping) + handle-type table
- CONTROLLED_SAMENESS_MISSING_DIFFERENTIATOR (Phase B; merges CHAIN_BREAK_SAME_INPUT_DIFFERENT_OUTPUT + CONTROLLED_FRAME_INTENSIFIER)
- REGION_SOURCE_CLOSURE (Phase B)
- CONSERVATION_DEPENDENCY (Phase B)
- PROXY_PROMOTION_GATE (Phase B)
- PRACTICAL_SIGNIFICANCE_GATE (Phase B)

## Added failure semantics

Gate failure changes the role a source can play. It does not discard papers by default.

Failed gates usually:

- preserve paper record
- allow support-layer writes
- block or cap direct node grounding
- block promotion candidate status
- attenuate weight to the relevant channel

## Added workflow correction

Candidate patches must be evaluated before adoption.

Required checks:

- goal fit
- layer fit
- contradiction check
- reification check
- operation-product check
- chain-generation check
- redundancy check
- failure-mode check
- minimal-patch check

## Known assistant failure corrected

The assistant previously treated user-supplied candidate rules as if they were integrated. This packet corrects that behavior by adding the Patch Adoption Gate and marking v0.05 v4 material as candidate unless explicitly approved.

## Rationale

The NO/autism-style paper fails before evidence weighting when diagnostic labels, biomarker language, diagnosis, and spectrum language are doing causal work the assay did not generate. It can remain in the ingest record as attenuated support, but it cannot directly ground a mechanism or promotion candidate unless label-stripped physical residue and route closure survive.
