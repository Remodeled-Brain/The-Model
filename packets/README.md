# Frozen runtime packets

This directory contains exact, externally usable single-file runtime bundles for released versions of The Model.

Normal generated build outputs remain under `model/dist/` and are not committed. Release packets are generated from an immutable Git ref by `scripts/publish_runtime_packets.py`, then preserved here with source provenance and SHA-256 checksums.

Each version directory may contain separate packets for distinct operations. Load only the packet required by the task. A primary question runtime should not silently absorb an ingest runtime, and an ingest runtime should not be treated as the default answer runtime.

A packet is a frozen specification handoff. It does not certify provider compliance. Private-repository URLs require authenticated GitHub access. For an unauthenticated browser LLM, upload the packet directly or publish an approved public mirror.
