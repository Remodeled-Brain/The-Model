# Cartridge conformance infrastructure candidate review — 2026-07-26

**Verdict:** ACCEPT FOR CANDIDATE TESTING; HOLD FOR ADOPTION.

## Layer

Shared conformance discovery, provider execution, freshness hashing, and physical-contract validation.

## Fit

The patch removes domain-name branching from shared conformance code. Fixture sets are discovered from `conformance/fixtures/`; active cartridge and physical-continuity inputs are discovered from the authoritative runtime manifest. A cartridge can therefore register its own fixtures and manifest entries without teaching the general runner its domain name.

## Consistency and risks

- Required fixture sets must exactly match the discovered fixture-set catalog.
- Cartridge freshness hashes cover the ordered active domain-module bundle rather than one privileged cartridge.
- Physical freshness hashes cover the generic physical contracts and every active domain physical-continuity module.
- Runtime and ingest manifests must expose the same active domain physical-continuity modules.
- Optional target-identity expectations are validated generically for any fixture set.
- Discovery is filename- and manifest-driven; malformed, duplicate, missing, or unconfigured fixture sets fail validation rather than being skipped.

## Redundancy and minimal form

The shared layer owns discovery and hashing only. Domain semantics, fixture content, and cartridge-specific structural checks remain in each cartridge change. The minimal patch changes the two conformance validators, the provider runner, conformance documentation, this review, and one candidate changelog fragment.

## Adoption status

Candidate. Structural validation is required, and any later adoption still requires fresh provider results under the active runtime, cartridge bundle, fixture, target-identity, and physical-contract hashes. This review adopts nothing.
