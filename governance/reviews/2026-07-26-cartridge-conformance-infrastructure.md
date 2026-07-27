# Cartridge conformance infrastructure candidate review — 2026-07-26

**Verdict:** ACCEPT FOR CANDIDATE TESTING; HOLD FOR ADOPTION.

## Layer

Shared conformance discovery, provider execution, freshness hashing, and physical-contract validation.

## Fit

The patch removes domain-name branching from shared conformance discovery and hashing. Fixture sets are discovered from `conformance/fixtures/`; active cartridge inputs are read from `domain_modules`; and their physical-continuity subset is declared explicitly in `physical_continuity_modules`. A cartridge can therefore register its own fixtures and manifest entries without teaching the general runner its domain name.

## Consistency and risks

- Required fixture sets must exactly match the discovered fixture-set catalog.
- Cartridge freshness hashes cover the ordered active domain-module bundle rather than one privileged cartridge, and runtime/ingest domain-module declarations must match exactly.
- Physical freshness hashes cover the generic physical contracts and every module explicitly listed in `physical_continuity_modules`; no filename convention selects hash membership.
- Runtime and ingest manifests must expose the same ordered physical-continuity declaration, and every declared physical module must also be loaded as a domain module.
- Optional target-identity expectations are validated generically for any fixture set, declared in the generic target-identity reconstruction fixture, and exercised through positive and negative self-tests against the decisive-intervention fixture.
- Malformed, duplicate, missing, or unconfigured fixture sets fail validation rather than being skipped; the provider runner reports the same structured discovery errors, including during `--help` setup.

## Redundancy and minimal form

The shared layer owns discovery, registration parity, and hashing only. Domain semantics, required-domain membership, fragment assertions, forbidden-term checks, and other cartridge-specific structural checks remain in each cartridge change. “Register data, not code” therefore applies to shared discovery and freshness, not to complete semantic validation of a new cartridge. The manifest additions only classify the already-loaded neuroscience physical module; they do not load or adopt candidate cartridge content.

## Adoption status

Candidate. Merging this infrastructure would immediately change what structural CI enforces, including intentional failure when a fixture file is added without matching `required_runs.json` registration. That enforcement is intended. It does not adopt any candidate Model or cartridge text; later adoption still requires fresh provider results under the active runtime, cartridge bundle, fixture, target-identity, and physical-contract hashes. This review adopts nothing.
