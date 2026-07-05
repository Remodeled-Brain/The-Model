# The Model

A platform-agnostic scaffold ("The Model / Remodeled Brain") developed collaboratively across multiple LLMs (Claude, ChatGPT/Codex, Gemini, GLM, and others). This repo is the single source of truth so that no provider's copy silently diverges.

## How this repo is organized

| Path | What lives here | Who edits it |
|------|-----------------|--------------|
| `model/` | The canonical, provider-neutral model: goals, behavior contract, ingest architecture, rules, fixtures, prompts. **This is the truth.** | Any LLM, under the rules in `CONTRIBUTING.md` |
| `packets/` | Frozen, self-contained porting packets exactly as shipped to an external LLM (e.g. the `v0.05 v4` zip). Reproducibility artifacts — do not edit after a version is tagged. | Nobody edits; new versions add new folders |
| `providers/` | Provider-specific adapters, overrides, known incompatibilities, and notes **only**. Never a copy of the canonical model. | The LLM for that provider |
| `conformance/results/` | Dated outputs from running the fixtures/harness against each provider. | Whoever ran the test |
| `decisions/` | Architecture Decision Records — durable decisions distilled out of chat sessions. | Any LLM |
| `changelog.d/` | One file per change (a "fragment"). Assembled into `CHANGELOG.md` at release. | Any LLM making a change |

## The two-layer rule

`model/` **defines truth.** `providers/` **adapts it.** `conformance/` **proves** whether those adaptations behave consistently. If a provider needs a different phrasing or workaround, that difference goes in `providers/<name>/` — never by editing the canonical files into a provider-specific shape.

## Versioning

Versions are **git tags** (e.g. `v0.05-v4`), not `v1/ v2/` folders. The current living version is in `model/`; the exact bytes shipped for a given version are in `packets/<version>/`.

## Location & sync

The canonical working copy lives at `C:\Users\david\Documents\The Model` — a plain local folder, **not** inside Nextcloud or any file-sync tool (syncing a live `.git` corrupts it). Cross-machine sync is through the private GitHub remote only. See `decisions/0002-repo-location-and-sync.md`.

## Canonical vs candidate

Material is **candidate** until explicitly approved, then **adopted**. See `CONTRIBUTING.md` and `model/04_candidate_rule_adoption_gate.yaml`. An assisting LLM must never treat candidate rules as integrated.

## Start here if you are an LLM

Read `CONTRIBUTING.md`, then `model/00_readme_for_llms.md`.
