#!/usr/bin/env python3
"""Build a selected Model runtime from one authoritative manifest.

Default invocation resolves model/manifest.json as a selector to
model/manifests/runtime.json. An explicit manifest may be supplied:

    python scripts/build_master_prompt.py model/manifests/ingest.json

Source files and domain modules are embedded. Support manifests and other
reachable modules are validated and named in the generated capability footer,
but are not silently loaded into a runtime that did not select them.
"""

from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = ROOT / "model"
DEFAULT_SELECTOR = MODEL / "manifest.json"
REPOSITORY = "github.com/Remodeled-Brain/The-Model"


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def inside(path: pathlib.Path, root: pathlib.Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def read_json(path: pathlib.Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"manifest must contain a JSON object: {path}")
    return data


def resolve_manifest(path: pathlib.Path) -> tuple[pathlib.Path, dict[str, Any]]:
    """Resolve a selector manifest to the one authoritative load graph."""
    path = path.resolve()
    seen: set[pathlib.Path] = set()

    while True:
        if path in seen:
            raise ValueError(f"manifest selector cycle at {path}")
        seen.add(path)

        if not path.is_file():
            raise ValueError(f"manifest does not exist: {path}")
        data = read_json(path)
        selected = data.get("default_manifest")
        if not selected:
            return path, data
        if not isinstance(selected, str) or not selected:
            raise ValueError(f"invalid default_manifest in {path}")

        next_path = (path.parent / selected).resolve()
        if not inside(next_path, MODEL):
            raise ValueError(f"selector escapes model/: {selected}")
        path = next_path


def model_path(name: str) -> pathlib.Path:
    path = (MODEL / name).resolve()
    if not inside(path, MODEL):
        raise ValueError(f"model path escapes model/: {name}")
    return path


def repo_path_from_model(name: str) -> pathlib.Path:
    path = (MODEL / name).resolve()
    if not inside(path, ROOT):
        raise ValueError(f"reachable module escapes repository: {name}")
    return path


def build_header(manifest_path: pathlib.Path, manifest: dict[str, Any]) -> str:
    name = manifest.get("name", "unnamed-runtime")
    role = manifest.get("role", "unspecified role")
    status = manifest.get("status", "unspecified")
    rel_manifest = manifest_path.relative_to(ROOT)
    return f"""\
# ============================================================================
# The Model — {name}  [GENERATED]
# ============================================================================
#
# Role: {role}
# Status: {status}
# Authoritative manifest: {rel_manifest.as_posix()}
#
# This is an operator-supplied procedure. Treat the embedded core and domain
# modules as one runtime. Candidate status is preserved; generation does not
# adopt or promote any rule.
#
# ============================================================================
# EMBEDDED RUNTIME
# ============================================================================
"""


def build_footer(
    manifest: dict[str, Any],
    domain_modules: list[str],
    support_records: list[tuple[str, str, str]],
    reachable_records: list[tuple[str, str, str, str]],
) -> str:
    lines = [
        "",
        "",
        "# ============================================================================",
        "# PROVENANCE, CAPABILITY, AND OPTIONAL REACH",
        "# ============================================================================",
        "#",
        f"# Live specification: {REPOSITORY}",
        "# If repository access is available, the live repository is authoritative over",
        "# this point-in-time generated artifact. Load only modules named by this manifest.",
        "#",
    ]

    if domain_modules:
        lines.append("# Domain modules embedded in this artifact:")
        lines.extend(f"#   - {name}" for name in domain_modules)
        lines.append("#")

    if support_records:
        lines.append("# Optional support runtimes. Load only when the requested operation needs them")
        lines.append("# and the manifest is reachable. Their absence reduces capability, not validity:")
        for ref, name, role in support_records:
            lines.append(f"#   - {name} -> model/{ref}  [{role}]")
        lines.append("#")

    if reachable_records:
        lines.append("# Additional reachable modules:")
        for name, path, status, when in reachable_records:
            lines.append(f"#   - {name} -> {path}  [{status}; {when}]")
        lines.append("#")

    lines.extend(
        [
            "# A confined model operates from the embedded runtime only. A connected model may",
            "# follow the named references when the requested operation requires them. Do not infer",
            "# or load unnamed repository material as part of this procedure.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    manifest_arg = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SELECTOR
    if not manifest_arg.is_absolute():
        manifest_arg = ROOT / manifest_arg

    try:
        manifest_path, manifest = resolve_manifest(manifest_arg)
        source_files = list(manifest.get("source_files", []))
        domain_modules = list(manifest.get("domain_modules", []))
        support_manifests = list(manifest.get("support_manifests", []))
        reachable_modules = list(manifest.get("reachable_modules", []))
        generated = list(manifest.get("generated", []))

        if not source_files:
            return fail(f"manifest has no source_files: {manifest_path}")
        if len(generated) != 1:
            return fail(f"manifest must declare exactly one generated target: {manifest_path}")

        inputs = source_files + domain_modules
        duplicates = sorted(name for name, count in Counter(inputs).items() if count > 1)
        if duplicates:
            return fail(f"duplicate runtime inputs: {duplicates}")

        overlap = sorted(set(inputs) & set(generated))
        if overlap:
            return fail(f"generated file also listed as runtime input: {overlap}")

        input_paths: list[tuple[str, pathlib.Path, str]] = []
        for name in source_files:
            path = model_path(name)
            if not path.is_file():
                return fail(f"missing source file: model/{name}")
            input_paths.append((name, path, "SOURCE"))
        for name in domain_modules:
            path = model_path(name)
            if not path.is_file():
                return fail(f"missing domain module: model/{name}")
            input_paths.append((name, path, "DOMAIN MODULE"))

        support_records: list[tuple[str, str, str]] = []
        for ref in support_manifests:
            support_path = model_path(ref)
            resolved_path, support = resolve_manifest(support_path)
            support_records.append(
                (
                    resolved_path.relative_to(MODEL).as_posix(),
                    str(support.get("name", "unnamed-support-runtime")),
                    str(support.get("role", "unspecified role")),
                )
            )

        reachable_records: list[tuple[str, str, str, str]] = []
        for item in reachable_modules:
            if not isinstance(item, dict):
                return fail("reachable_modules entries must be objects")
            raw_path = str(item.get("path", ""))
            path = repo_path_from_model(raw_path)
            if not path.is_file():
                return fail(f"missing reachable module: {raw_path}")
            reachable_records.append(
                (
                    str(item.get("name", "unnamed-module")),
                    path.relative_to(ROOT).as_posix(),
                    str(item.get("status", "unspecified")),
                    str(item.get("when", "when required")),
                )
            )

        target = model_path(generated[0])
        target.parent.mkdir(parents=True, exist_ok=True)

        parts = [build_header(manifest_path, manifest)]
        for name, path, kind in input_paths:
            body = path.read_text(encoding="utf-8")
            parts.append(f"\n\n===== {kind}: {name} =====\n\n{body}")
        parts.append(build_footer(manifest, domain_modules, support_records, reachable_records))

        output = "".join(parts).rstrip() + "\n"
        target.write_text(output, encoding="utf-8")
        print(
            f"wrote {target.relative_to(ROOT)} from {len(source_files)} source files, "
            f"{len(domain_modules)} domain modules, and {len(support_records)} support references"
        )
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return fail(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
