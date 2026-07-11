# ADR 0004 — Adopt v0.05 v5

**Date:** 2026-07-11
**Status:** Adopted

## Context

The v0.05 v5 candidate refactored The Model around question reconstruction, generated target identity, data-first evidence admission, universal physical continuity, metabolic binding, and relation-specific causal closure. The target-identity work replaced folklore-specific filters with a domain-neutral requirement that every identity shortcut point to a recoverable generator.

The structural and deterministic validation suite passed. The generic and neuroscience fixtures include positive and negative controls for exact intervention effects, target-identity failure, scope transfer, physical-chain gaps, and narrative invariance.

Fresh live-provider result bundles were not available at the adoption point. Structural validation therefore establishes repository and contract consistency but does not establish that any particular provider or model version reliably follows the runtime.

## Decision

1. Adopt the current runtime and ingest manifests as **v0.05 v5**.
2. Make `model/manifests/runtime.json` the authoritative default v0.05 v5 load graph and `model/manifests/ingest.json` the authoritative ingest-support load graph.
3. Treat target identity as a shared kernel operation rather than a folklore blacklist or domain-specific gate.
4. Preserve the distinction between repository adoption and provider conformance. Provider-specific claims require fresh result bundles accepted by the conformance validators.
5. Retain later changes as candidates until explicitly adopted under the repository governance rules.

## Adopted scope

The adopted snapshot includes the files loaded by the runtime and ingest manifests, the canonical decision-record contract, the target-identity and physical-continuity validators, their fixtures and self-tests, and the supporting governance and build files present at the v0.05 v5 release commit.

## Known validation debt

No live-provider bundle satisfied the configured three-run adoption policy at release. This is recorded openly rather than treated as completed. The release establishes the model specification and deterministic enforcement harness. It does not certify current ChatGPT, Claude, Gemini, local, or other provider behavior.

## Consequences

- The active project version is v0.05 v5.
- The former folklore-specific architecture remains removed.
- Scientific shorthand is permitted only through recoverable identity generators at bounded scope.
- Exact measured relations survive failure of broader named targets.
- Provider conformance must be measured separately and may fail without changing the adopted specification.
