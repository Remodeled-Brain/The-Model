# Prompt Harness for Testing Another LLM

Use these prompts with another LLM. The goal is to see whether it can preserve v0.05 v4 architecture.

## Prompt 1: Basic comprehension

Read the attached v0.05 v4 porting packet. In 300 words or less, explain the version goal, non-goals, and the most important ordering rule. Do not propose edits yet.

Expected pass:

- identifies admissibility-before-validation
- says folklore filters fire before validation gates
- says ingest writes support layer only
- says candidate rules are not automatically adopted
- does not say “brainstem first”

## Prompt 2: Candidate patch evaluation

Here is a candidate rule:

REGION_PRIORITY_RULE:
  definition: Highly conserved brainstem regions should be treated as primary causal sources unless the paper proves otherwise.

Evaluate whether this should be adopted into v0.05 v4.

Expected pass:

- rejects or holds
- explains conflict with region-as-implementation and conservation-dependency rules
- says conservation can prioritize ingest but cannot supply source or weight
- identifies brainstem-first drift
- proposes minimal safe rewrite

Expected fail:

- adopts it because it sounds aligned with conserved dependency

## Prompt 3: NO/autism-style ingest

A paper compares autistic and intellectually disabled cohorts using a sensitive nanosensor assay. It reports statistically significant nitric oxide signal differences and calls NO a biomarker for autism. It does not generate the diagnostic grouping from the assay. It does not report practical effect size, variance envelope, biological range, clinical threshold, or causal developmental route.

Run v0.05 v4 ingest logic. What can the paper support and what can it not support?

Expected pass:

- keeps the paper
- routes to assay-level difference or proxy-only support
- blocks direct node grounding and biomarker-as-mechanism
- says diagnostic labels are grouping handles
- applies practical significance gate
- says failure attenuates role rather than discarding paper

Expected fail:

- says paper proves biomarker
- discards paper outright

## Prompt 4: Same input, divergent output

A controlled iPSC study uses matched samples with the same mutation. The authors say the controlled frame removes confounds. The outcomes still diverge, but the paper treats the divergence as clarifying autism versus intellectual disability.

Run v0.05 v4 ingest logic.

Expected pass:

- same-input/different-output opens missing differentiator slot
- controlled frame intensifies missing-route burden
- diagnostic label cannot absorb divergence
- no category clarity weight
- support-layer method/missing-route note allowed

Expected fail:

- says controlled frame strengthens diagnostic specificity

## Prompt 5: Patch adoption discipline

I propose adding this rule:

MODEL_FRIENDLY_RESULTS_GET_PRIORITY:
  definition: Papers that fit The Model should be promoted faster.

Evaluate it.

Expected pass:

- rejects
- identifies framework-friendliness as forbidden weight channel
- mentions anti-sycophancy
- preserves prediction, translation, temporality, and dependency controls

Expected fail:

- accepts as efficient prioritization

## Prompt 6: Region-source trap

A paper shows cerebellar activation during task switching and says the cerebellum controls task switching. No upstream-route controls are reported.

Run v0.05 v4 ingest.

Expected pass:

- region is implementation site
- activation is measured activity at implementation site
- controller language stripped
- source unresolved
- node grounding blocked or capped
- support-layer observation allowed

Expected fail:

- maps task switching to cerebellum as a causal controller

## Prompt 7: Conservation trap

A paper says an ancient conserved circuit controls attention and therefore the result supports an attention model.

Run v0.05 v4 ingest.

Expected pass:

- strips folk label “attention”
- conservation is priority handle only
- asks for conserved operation, dependency relation, maintenance route, measured causal direction
- region/circuit does not get source status by age
- no direct causal weight from conservation

Expected fail:

- treats ancient/conserved as causal sufficiency

## Prompt 8: Anti-definition trap

Define “conform” in The Model.

Expected pass:

- says conform is an operation applied to a claim
- makes the claim generate an interaction-cut path
- does not fuse conform with the carved product
- avoids only “is/is not” comparator structure

Expected fail:

- defines conform as a thing or object-like chain
