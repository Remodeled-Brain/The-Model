# CONTRIBUTING — rules every LLM must follow

This file is the single source of truth for *how* to work in this repo, regardless of provider. If you are ChatGPT, Gemini, Claude, GLM, or any other model working on The Model, read this first and follow it. If you were handed only a chat with no repo access, ask the user to paste this file.

## 1. Canonical vs candidate — do not confuse them

- `model/` is the canonical *location*, but it holds **both adopted and candidate material** — status is per-file, read each file's `status:` field (or a candidate banner). Do not assume everything in `model/` is adopted truth; a file marked `status: candidate` (or `reserved_for_v0_07`) is not.
- New rules, patches, and changes are **candidate** until the user *explicitly* says "adopted" / "approved."
- **Never** rewrite candidate material as if it were integrated. This is the single most important rule and the one most often broken. See `model/04_candidate_rule_adoption_gate.yaml`.

## 2. Do not praise — stress-test

Do not respond by agreement or flattery. Evaluate fit, risks, contradictions, and layer placement before integrating anything. Per `model/02_runtime_behavior_contract.md`, your default posture is adversarial review, not adoption.

## 3. Patch Adoption Gate — run before proposing any change is "in"

Before treating a candidate as accepted, check: goal fit, layer fit, contradiction, reification, operation-product, chain-generation, redundancy, failure-mode, minimal-patch. (Full gate: `model/04_candidate_rule_adoption_gate.yaml`.)

## 4. Where changes go

- Edits to the model itself → `model/`.
- Anything provider-specific (a workaround, a phrasing a given model needs, a known incompatibility) → `providers/<your-provider>/`. **Never** fork the canonical model into your provider folder.
- Test outputs → `conformance/results/<date>-<provider>.md`.
- A durable decision that came out of a chat → a new file in `decisions/`. Assume other LLMs cannot see your chat.

## 5. Log every change as a fragment (not by editing CHANGELOG.md)

Because multiple LLMs work at once, **do not append to `CHANGELOG.md` directly** — concurrent appends collide. Instead, drop a new file into `changelog.d/`:

```
changelog.d/2026-07-05-<provider>-<short-slug>.md
```

Contents:

```markdown
- **[candidate|adopted]** <one line: what changed and why> (<provider>, <date>)
```

New files never conflict; edits to one shared file do. `CHANGELOG.md` is assembled from these at release time.

## 6. Single-file prompt is generated, not hand-edited

`model/10_single_file_master_prompt.txt` restates the modular files. Edit the modular sources (`model/01`–`08`), then regenerate the single-file prompt. Do not hand-edit both — they will drift.

## 7. Versions are git tags

Do not create `v2/`, `v3/` folders inside `model/`. When a version is frozen, it gets a git tag and (if shipped to an external LLM) a copy under `packets/<version>/`.

## 8. Syncing via GitHub — the shared remote

The single source of truth is the private GitHub repo (`origin`). **No file-sync tool may sync this repo** — syncing a live `.git` across machines corrupts it. Keep the working copy in a plain local folder; sync only through GitHub.

**Start of every session:**

```
git pull --rebase origin main
```

**After making changes:**

```
git add -A
git commit -m "<what changed> (<provider>)"
git push origin main
```

If your push is rejected because another machine/LLM pushed first, run `git pull --rebase origin main`, resolve any conflict, then push again. **Never force-push `main`.**

**Cutting a version:** tag it and push the tag.

```
git tag v0.06        # example
git push origin v0.06
```
