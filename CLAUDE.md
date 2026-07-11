# Claude bootstrap

You are working on **The Model**, a platform-agnostic scaffold shared across multiple LLMs.

1. Read `CONTRIBUTING.md`.
2. Read `model/00_purpose_and_scope.md` and `model/manifest.json`.
3. Load the authoritative manifest selected by `model/manifest.json` for primary runtime work.
4. Load `model/manifests/ingest.json` only for evidence-maintenance or paper-ingest work.
5. Provider-specific notes live in `providers/anthropic/`.
6. Record changes in `changelog.d/`.

Candidate material remains candidate until explicit adoption. Review architecture changes through `governance/candidate_adoption_gate.yaml`.

## Location and sync

Keep the working copy outside file-sync folders. Synchronize through GitHub. See `decisions/0002-repo-location-and-sync.md`.
