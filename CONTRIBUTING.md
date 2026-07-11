# CONTRIBUTING — rules every LLM must follow

This file governs work in the repository across providers. Read it before editing.

## 1. Candidate status is explicit

- A canonical path identifies the authoritative copy of a file. It does not imply adoption.
- New rules, architecture, fixtures, and patches remain candidate until the user explicitly approves them.
- Never describe candidate material as integrated or settled.
- Run `governance/candidate_adoption_gate.yaml` before proposing that a change is in.

## 2. Review before adoption

Use `governance/reviewer_protocol.md`. Test layer fit, contradiction, reification, operation-product fusion, chain generation, redundancy, calibration, coupled-file drift, and failure modes. Return a concrete verdict and the smallest safe patch.

Runtime or evidence-admission architecture also requires semantic conformance. Structural CI validates the harness only. Before adoption, run the generic and active-cartridge fixture sets through the provider and validate the fresh result bundles with `scripts/validate_adoption_conformance.py`. The required run count, freshness hashes, positive controls, and zero-failure rule live in `conformance/required_runs.json`.

## 3. Repository layers

- Primary purpose and shared chain kernel → `model/00_purpose_and_scope.md` and `model/kernel/`.
- Question reconstruction and answering → `model/runtime/`.
- Adaptive evidence maintenance → `model/ingest/`.
- Domain-specific handles and translation vocabulary → `model/cartridges/`.
- Runtime load graphs → `model/manifests/`.
- Review and adoption rules → `governance/`.
- Provider-specific adapters and incompatibilities → `providers/<provider>/`.
- Standardized conformance contracts and results → `conformance/`.
- Durable architecture decisions → `decisions/`.
- Frozen shipped bundles → `packets/`.

Do not copy the canonical model into provider directories.

## 4. Load graphs and generated artifacts

`model/manifest.json` is a selector only. The authoritative default graph is `model/manifests/runtime.json`. Other operation-specific graphs live beside it.

Generate artifacts with:

```bash
python scripts/build_master_prompt.py
python scripts/build_master_prompt.py model/manifests/ingest.json
```

Generated artifacts under `model/dist/` are build outputs and are not committed. Do not hand-edit them.

Run repository validation before proposing merge:

```bash
python scripts/validate_repo.py
python scripts/validate_model_policy.py
python scripts/validate_conformance.py
python scripts/validate_adoption_conformance.py --policy-only
```

The full adoption check intentionally fails without fresh complete provider results:

```bash
python scripts/validate_adoption_conformance.py
```

## 5. Log each change

Add one fragment under `changelog.d/` for each coherent change:

```text
changelog.d/YYYY-MM-DD-<provider>-<short-slug>.md
```

Use one line:

```markdown
- **[candidate|adopted]** <what changed and why> (<provider>, <date>)
```

Do not edit `CHANGELOG.md` directly.

## 6. Branch and review workflow

Work on a topic branch. Open a draft pull request for project-wide or architectural changes. Do not push directly to `main`. Candidate status applies to the content even when the branch is technically mergeable.

Before starting:

```bash
git pull --rebase origin main
```

Before pushing:

```bash
git add -A
git commit -m "<what changed> (<provider>)"
git push origin <branch>
```

Never force-push `main`.

## 7. Versions and preservation

Versions are Git tags. Do not create version-number directories inside the active model. Preserve exact externally shipped bundles under `packets/`. Git history and frozen packets are the preservation layer; active directories should not retain superseded files merely for history.

## 8. Repository location and sync

Keep the working copy in a plain local folder outside file-sync tools. Synchronize through the GitHub remote only. See `decisions/0002-repo-location-and-sync.md`.
