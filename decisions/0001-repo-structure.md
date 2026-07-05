# ADR 0001 — Repository structure for multi-LLM development

**Date:** 2026-07-05
**Status:** Adopted

## Context

The Model is developed by several LLMs at once (Claude, ChatGPT/Codex, Gemini, GLM) and must stay platform-agnostic. Two failure modes to avoid: (a) each provider forking its own copy of the model, which diverges; (b) concurrent edits to shared files (especially the changelog) colliding.

## Decision

1. **One canonical copy** in `model/`. Providers get `providers/<name>/` for adapters and notes only — never a full copy.
2. **Versions are git tags**, not `v1/ v2/` folders. Exact shipped bundles are frozen under `packets/<version>/` for reproducibility.
3. **Changelog by fragments** (`changelog.d/`, one file per change) instead of a shared `CHANGELOG.md` that every LLM appends to. New files don't merge-conflict; shared-file appends do.
4. **Bootstrap files** (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) are thin pointers to `CONTRIBUTING.md`. They auto-load only in CLI/agent tools; browser chats require pasting `CONTRIBUTING.md`. GLM has no standard convention file, so `providers/glm/` carries its notes.

## Open item — single-file prompt drift

`model/10_single_file_master_prompt.txt` (~1,400 lines) restates the modular files `01`–`08`. Maintaining both by hand guarantees drift. **Decision needed:** make the single-file prompt a *generated artifact* (a build step that concatenates/renders the modular sources) rather than a hand-edited file. Until that build exists, edit the modular sources and regenerate manually.

## Consequences

- Reproducibility: any shipped version can be recovered from its `packets/` folder or git tag.
- Concurrency: multiple LLMs can record changes simultaneously without conflicts.
- Enforcement is honor-system until CI is added to check that every change ships a `changelog.d/` fragment.
