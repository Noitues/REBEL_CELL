"""Build an Anthropic Message Batches payload (.jsonl) from a task spec (docs/process/02_MULTI_AGENT_BATCH_ARCHITECTURE.md).

    python tools/batch/make_batch.py tools/batch/specs/docstrings_core.json
    python tools/batch/make_batch.py spec.json --out batches/2026-10-10_docstrings.jsonl
    python tools/batch/make_batch.py spec.json --dry-run      # print custom_ids and token estimate only

Spec (JSON):
{
  "name": "docstrings_core",                     # batch name; custom_id prefix
  "kind": "docstrings",                          # picks tools/batch/prompts/<kind>.md as the system prompt
  "model": "claude-haiku-5-5",                   # optional; default per kind (see KIND_DEFAULTS)
  "effort": "low",                               # optional; default per kind
  "max_tokens": 8000,                            # optional
  "files": ["scripts/core/*.gd"],                # globs, repo-relative; one request per file
  "exclude": ["scripts/core/handlers/*"],        # optional globs
  "context": {"deps": true, "diff": "main"},     # optional: add referenced class signatures / the diff
  "instructions": "Only public functions."       # optional per-batch text appended to every user turn
}

Every line of the output follows the Batches API request schema:
  {"custom_id": "<name>-<nnn>-<slug>", "params": {model, max_tokens, system: [...], messages: [...], output_config: {effort}}}

Prompt caching: the system prompt is [stable rules block (cache_control ephemeral)] and nothing
else, byte-identical on every line, so requests in the batch share one cache prefix. Everything
that varies (file text, diff, per-batch instructions) goes in the user turn. Caching only applies
when the shared prefix exceeds the model's minimum cacheable length; check cache_read_input_tokens
in the results (ingest_results.py reports it).

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PROMPTS = Path(__file__).resolve().parent / "prompts"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from context_slice import class_index, git_diff, referenced_classes, signatures  # noqa: E402

COMMON_RULES = PROMPTS / "_common_rules.md"
# Defaults per task kind: the cheapest model that does the job; effort low for mechanical work.
KIND_DEFAULTS = {
    "docstrings": {"model": "claude-haiku-5-5", "effort": "low", "max_tokens": 8000},
    "cleanup": {"model": "claude-haiku-5-5", "effort": "low", "max_tokens": 8000},
    "lint_report": {"model": "claude-haiku-5-5", "effort": "low", "max_tokens": 4000},
    "rename": {"model": "claude-haiku-5-5", "effort": "low", "max_tokens": 8000},
    "unit_tests": {"model": "claude-sonnet-5-5", "effort": "medium", "max_tokens": 16000},
    "refactor": {"model": "claude-sonnet-5-5", "effort": "medium", "max_tokens": 16000},
    "decisions_digest": {"model": "claude-sonnet-5-5", "effort": "medium", "max_tokens": 8000},
    "text_audit": {"model": "claude-haiku-5-5", "effort": "low", "max_tokens": 4000},
}
CUSTOM_ID_RE = re.compile(r"[^A-Za-z0-9_-]")


def slug(path: str) -> str:
    return CUSTOM_ID_RE.sub("-", Path(path).stem)[:30]


def expand(globs: list[str], exclude: list[str]) -> list[str]:
    files: set[Path] = set()
    for g in globs:
        files.update(p for p in ROOT.glob(g) if p.is_file())
    for g in exclude:
        files.difference_update(ROOT.glob(g))
    return sorted(p.relative_to(ROOT).as_posix() for p in files if not p.name.endswith(".uid"))


def system_blocks(kind: str) -> list[dict]:
    rules = COMMON_RULES.read_text(encoding="utf-8")
    task = (PROMPTS / f"{kind}.md").read_text(encoding="utf-8")
    # One stable block, one breakpoint at its end: tools(none) + system cache together.
    return [{"type": "text", "text": rules.strip() + "\n\n" + task.strip(), "cache_control": {"type": "ephemeral"}}]


def user_turn(path: str, spec: dict, idx: dict) -> str:
    p = ROOT / path
    parts = [f"<file path=\"{path}\">", p.read_text(encoding="utf-8", errors="replace").rstrip(), "</file>"]
    ctx = spec.get("context", {})
    if ctx.get("diff"):
        d = git_diff(ctx["diff"], path)
        if d:
            parts += [f"<diff base=\"{ctx['diff']}\">", d, "</diff>"]
    if ctx.get("deps") and path.endswith(".gd"):
        for n in referenced_classes(p, idx):
            parts += [f"<signatures class=\"{n}\" path=\"{idx[n].relative_to(ROOT).as_posix()}\">", "\n".join(signatures(idx[n])), "</signatures>"]
    if spec.get("instructions"):
        parts += ["<instructions>", spec["instructions"].strip(), "</instructions>"]
    parts.append(f"Work on {path} only. Answer in the RC envelope.")
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--out", default="")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    kind = spec["kind"]
    if kind not in KIND_DEFAULTS:
        print(f"make_batch: unknown kind {kind!r}; known: {', '.join(KIND_DEFAULTS)}")
        return 2
    d = KIND_DEFAULTS[kind]
    model = spec.get("model", d["model"])
    effort = spec.get("effort", d["effort"])
    max_tokens = int(spec.get("max_tokens", d["max_tokens"]))
    files = expand(spec["files"], spec.get("exclude", []))
    if not files:
        print("make_batch: no files matched")
        return 2
    idx = class_index() if spec.get("context", {}).get("deps") else {}
    system = system_blocks(kind)
    out = Path(args.out) if args.out else ROOT / "batches" / f"{spec['name']}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    for i, f in enumerate(files, 1):
        custom_id = f"{spec['name']}-{i:03d}-{slug(f)}"[:64]
        params = {
            "model": model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user_turn(f, spec, idx)}],
            "output_config": {"effort": effort},
        }
        lines.append({"custom_id": custom_id, "params": params})

    approx_tokens = sum(len(json.dumps(l["params"]["messages"])) for l in lines) // 4
    shared = len(system[0]["text"]) // 4
    print(f"make_batch: {len(lines)} requests, model {model}, effort {effort}, ~{shared} shared tokens (cached), ~{approx_tokens} varying tokens")
    if args.dry_run:
        for l in lines:
            print("  " + l["custom_id"])
        return 0
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        for l in lines:
            fh.write(json.dumps(l, ensure_ascii=False, sort_keys=True) + "\n")
    manifest = {"name": spec["name"], "kind": kind, "model": model, "files": {l["custom_id"]: f for l, f in zip(lines, files)}, "base": spec.get("context", {}).get("diff", "")}
    out.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True), encoding="utf-8")
    print(f"make_batch: wrote {out} and its .manifest.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
