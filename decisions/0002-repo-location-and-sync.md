# ADR 0002 — Repository location and sync model

**Date:** 2026-07-05
**Status:** Adopted (supersedes any earlier assumption that the home was the Nextcloud path)

## Context

The Model is worked on by several LLMs across machines. An earlier setup placed the repo under Nextcloud (`...\Nextcloud\Documents\The Model`) so Nextcloud would sync it. During setup that Nextcloud folder **silently emptied itself** — a file-sync tool and git fighting over the same `.git` directory. At that point different LLMs held different assumptions about where the repo lived (ChatGPT still assumed Nextcloud), which is exactly the drift this project's structure exists to prevent.

## Decision

1. **Canonical working copy lives at `C:\Users\david\Documents\The Model`** — a plain local folder that is **not** inside Nextcloud or any other file-sync folder.
2. **Cross-machine sync is via a private GitHub repo (`origin`) only.** No file-sync tool may sync the repo, and especially not `.git`.
3. The local path may differ on other machines, but the **sync source of truth is always the GitHub remote**, not a synced folder.

## Consequences

- Every LLM/machine clones or pulls from GitHub; nobody relies on Nextcloud for this repo.
- Any prior note (memory, chat, doc) that names the Nextcloud path as the home is void — this ADR overrides it.
- Nextcloud returns to syncing ordinary documents only.

## Propagation

Because this changes a project-wide fact, it is recorded here and referenced from `README.md` and the bootstrap files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) so any LLM re-reading the repo picks it up. Other LLMs already in flight (e.g. ChatGPT) must be pointed at this ADR to correct their assumption.
