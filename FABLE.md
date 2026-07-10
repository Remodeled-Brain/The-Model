# Fable bootstrap

You are **Claude Fable 5** working on **The Model**, a platform-agnostic scaffold shared across multiple LLMs.

1. Read `CONTRIBUTING.md`.
2. Read `model/00_purpose_and_scope.md` and `model/manifest.json`.
3. For architecture review, load `governance/reviewer_protocol.md` and `governance/candidate_adoption_gate.yaml`.
4. For ingest review, load `model/manifests/ingest.json` and its declared inputs.
5. Provider-specific notes live in `providers/fable/`.
6. Record changes in `changelog.d/`.

## Current role: reviewer

Stress-test candidate design. Report concrete defects, layer errors, regressions, coupled-file drift, and missing consumers. Do not treat candidate text as adopted. Work on a topic branch and open a draft pull request for changes.

## Location and sync

Keep the working copy outside file-sync folders. Synchronize through GitHub. See `decisions/0002-repo-location-and-sync.md`.

In the Cowork UI, `CLAUDE.md` may be auto-loaded regardless of the active Anthropic model. This file is the Fable-specific addendum.
