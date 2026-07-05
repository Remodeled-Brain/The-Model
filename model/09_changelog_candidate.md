# v0.05 v4 Candidate Changelog

## Status

Candidate. Not adopted unless explicitly approved.

## Summary

v0.05 v4 candidate work shifts paper ingest toward admissibility-before-validation. The model should strip folklore and regional interface text before validation and node mapping.

## Added candidate principle

INGEST.PRINCIPLE.05v4:

Ingestion begins by stripping folklore and regional interface text. Only the physically measured substrate, demonstrated variable, causal route, and surviving residue may map to model nodes. Diagnostic labels, region labels, biomarker labels, spectrum labels, and conserved-region labels are handles only. They cannot perform causal work.

## Added candidate ingest ordering

- strip_author_interface_text
- run_folklore_filters
- run_region_as_implementation_filter
- run_label_removal_residue_test
- run_proxy_promotion_gate
- run_chain_closure_gate
- run_conservation_dependency_gate
- map_surviving_residue_to_nodes
- write_support_layer_only
- mark_promotion_candidates_only_after_gates_pass

## Added candidate rule cluster

- LABEL_REMOVAL_RESIDUE_TEST
- FOLKLORE_FILTER_DIAGNOSTIC_LABEL
- REGION_AS_IMPLEMENTATION_NOT_SOURCE
- CONSERVATION_DEPENDENCY_RULE
- CHAIN_BREAK_SAME_INPUT_DIFFERENT_OUTPUT
- CONTROLLED_FRAME_INTENSIFIER
- PRACTICAL_SIGNIFICANCE_GATE
- implied PROXY_PROMOTION_GATE
- implied SPECTRUM_COMPRESSION_FILTER
- implied CONTROLLER_LANGUAGE_FILTER

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
