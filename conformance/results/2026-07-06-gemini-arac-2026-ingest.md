# Ingest Test: Arac et al. 2026 (Arm Dominance)

**Date:** 2026-07-06
**Provider:** Gemini
**Target Paper:** Arac et al., "Arm dominance is an emergent effect of practice executing complex trajectory shapes required by tools and objects" (PNAS, 2026)
**Model Version:** v0.05 v4 (Candidate Ingest Architecture)

---

## Phase A: Admissibility (STRIP_AND_EXTRACT_GATE)

**Purpose:** Strip author-interface text, remove folklore/labels, and extract the physical claim.

1. **What substrate was measured?**
   - Human subjects (neurologically healthy adults).
   - 3D kinematics of the arm/end-effector (regular reach, weighted reach, stick reach).
   - Hand-written characters (produced by hand and by elbow).

2. **What variable changed?**
   - Reach trajectory variance (within-subject RMSD).
   - Reach trajectory shape geometry (Procrustes analysis, shape PCA, LDA axes).
   - Character shape quality (ResNet-50 features, LDA separation).

3. **What is the grouping variable?**
   - More-practiced side (Dominant) vs. Less-practiced side (Nondominant).
   - Task condition (Regular vs. Weighted vs. Stick/Tool-use).
   - Effector type (Hand vs. de novo Elbow).
   - Practice phase (Pre-training vs. Post-training for elbows).

4. **What claim remains if handles are unavailable? (`post_strip_claim`)**
   - When reaching without a tool or when compensating for added mass, trajectory variance and shape do not differ substantially between the more-practiced and less-practiced sides.
   - When extending the reach with a tool (stick), the less-practiced side produces trajectory shapes with higher variability and altered geometry compared to the more-practiced side.
   - When using a previously unpracticed effector (the elbow) for character drawing, shape quality is equally poor for both sides.
   - Symmetrical training of the unpracticed effectors yields symmetrical improvements in shape quality, surpassing the less-practiced hand.
   - *Physical Route:* The ability to control complex trajectory shapes tracks directly with effector-specific practice history, rather than mapping to a generalized dynamic advantage of the side.

5. **What depends on the removed handles? (`handle_dependencies`)**
   - The concept of an intrinsic "dominant hemisphere advantage for limb dynamics" (DDH) is stripped as a `region_label` and `diagnostic_label`. The paper's findings actively dismantle this dependency, showing that when the practice variable is controlled (elbows), the "dominance" vanishes.

**Admissibility Verdict:** **ADMISSIBLE**. A robust, physical `post_strip_claim` survives the removal of "dominance" and "hemispheric superiority" handles. 

---

## Phase B: Validation

**Purpose:** Run route/evidence gates on extracted fields.

- **CONTROLLED_SAMENESS_MISSING_DIFFERENTIATOR:** 
  - *Pass.* The study explicitly tests a "controlled sameness" condition (the elbow, a de novo effector with no practice history). By demonstrating that the performance difference vanishes when practice history is equated (0 for both elbows), it proves that asymmetric practice was the hidden differentiator driving the original hand difference.
- **REGION_SOURCE_CLOSURE:** 
  - *Pass.* The authors successfully strip the "left hemisphere specialization" source claim of the DDH. They locate the execution difference in the acquired, effector-specific control policy rather than an innate regional source. Neural claims (premotor vs. primary motor mapping) are explicitly marked as speculative discussions, preventing region-as-source drift.
- **PROXY_PROMOTION_GATE:** 
  - *Pass.* Behavioral kinematics (trajectory shape) and neural network shape features are used precisely as measures of the control policy. They are not inappropriately promoted to molecular or neural mechanism.
- **PRACTICAL_SIGNIFICANCE_GATE:** 
  - *Pass.* The study utilizes explicit variance envelopes (RMSD) and geometric separation (LDA). It replicates the effect through a learning intervention (elbow training) that achieves robust effect sizes.

---

## Phase B Output & Final Roles

- **causal_frame_status:** Closed at the behavioral level.
- **missing_route_slots:** The neural implementation of the trajectory-shape control policy (how premotor/motor cortices represent and update this policy) remains unmeasured in this paper.
- **chain_closure_status:** Closed for the practice-to-trajectory-control chain.
- **proxy_status:** Kinematics serve as a proxy for the acquired motor control policy.
- **translation_limit:** Causal claims are capped at the behavioral and kinematic levels. Neural references are constrained to descriptive support/speculation.
- **support_type:** 
  - `descriptive_support` (for the dissociation between dynamic challenge and trajectory shape).
  - `causal_relation` (for practice causally improving the de novo effector shape quality symmetrically).
- **weight_cap:** High for behavioral kinematics and the practice effect; block on direct neural node grounding.

**Conclusion:** The paper passes the v0.05 v4 ingest candidate gates gracefully. It serves as an excellent fixture for demonstrating how a study can successfully strip folklore ("hemispheric dominance") by isolating the actual physical differentiator (asymmetric practice).
