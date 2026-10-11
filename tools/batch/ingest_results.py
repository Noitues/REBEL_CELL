"""Fold a batch's results back into the project (docs/process/02_MULTI_AGENT_BATCH_ARCHITECTURE.md, "Ingestion protocol").

    python tools/batch/ingest_results.py batches/docstrings_core.results.jsonl
    python tools/batch/ingest_results.py batches/docstrings_core.results.jsonl --apply     # apply patches on a branch
    python tools/batch/ingest_results.py batches/docstrings_core.results.jsonl --apply --branch batch/docstrings-core

What it does, per result line (keyed by custom_id, never by position):
  1. Parses the RC envelope the prompts demand:
       <<<RC_RESULT ... >>>   status: ok | skip | error, summary: one line
       <<<RC_PATCH ... >>>    a unified diff (paths repo-relative, a/ b/ prefixes)
       <<<RC_NOTES ... >>>    anything the orchestrator should know (findings, open questions)
  2. Writes <results dir>/<name>_out/<custom_id>.patch and .notes.md.
  3. `git apply --check` on every patch; with --apply, applies the good ones on the branch
     (created from HEAD if missing) and commits each with the summary line.
  4. Writes INGEST_REPORT.md: one row per request (status, applied?, check result, cache hit,
     tokens), the retry list (errored/expired custom_ids -> a resubmit .jsonl), and the notes
     worth reading. The orchestrator reads only this report.

Retry rules: result.type "errored" with error type "invalid_request" -> fix the payload line;
any other error, "expired" or "canceled" -> resubmit unchanged. Both land in <name>.retry.jsonl.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ENV_RE = re.compile(r"<<<(RC_RESULT|RC_PATCH|RC_NOTES)\n(.*?)\n>>>", re.S)


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)


def parse_envelope(text: str) -> dict[str, str]:
    parts = {m.group(1): m.group(2).strip("\n") for m in ENV_RE.finditer(text)}
    return parts


def parse_result_block(block: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip().lower()] = v.strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("results")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--branch", default="")
    args = ap.parse_args()

    results = Path(args.results)
    name = results.name.replace(".results.jsonl", "")
    payload = results.with_name(name + ".jsonl")
    manifest_path = results.with_name(name + ".manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {"files": {}}
    payload_lines = {}
    if payload.exists():
        for line in payload.read_text(encoding="utf-8").splitlines():
            if line.strip():
                obj = json.loads(line)
                payload_lines[obj["custom_id"]] = line
    out_dir = results.with_name(name + "_out")
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    retry: list[str] = []
    notes_all: list[str] = []
    total_in = total_out = total_cached = 0

    for line in results.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        cid = r["custom_id"]
        res = r["result"]
        row = {"custom_id": cid, "file": manifest["files"].get(cid, ""), "type": res["type"], "status": "", "summary": "", "check": "", "applied": "", "cache": "", "tokens": ""}
        if res["type"] != "succeeded":
            err = res.get("error", {}) or {}
            row["summary"] = f"{res['type']}: {err.get('type', '')} {err.get('message', '')}".strip()
            if cid in payload_lines:
                retry.append(payload_lines[cid])
            rows.append(row)
            continue
        msg = res["message"]
        usage = msg.get("usage", {})
        total_in += usage.get("input_tokens", 0)
        total_out += usage.get("output_tokens", 0)
        total_cached += usage.get("cache_read_input_tokens", 0) or 0
        row["cache"] = str(usage.get("cache_read_input_tokens", 0) or 0)
        row["tokens"] = f"{usage.get('input_tokens', 0)}/{usage.get('output_tokens', 0)}"
        if msg.get("stop_reason") == "refusal":
            row["status"] = "refusal"
            row["summary"] = str(msg.get("stop_details"))
            rows.append(row)
            continue
        if msg.get("stop_reason") == "max_tokens":
            row["status"] = "truncated"
            row["summary"] = "hit max_tokens; raise it and resubmit"
            if cid in payload_lines:
                retry.append(payload_lines[cid])
            rows.append(row)
            continue
        text = "".join(b.get("text", "") for b in msg.get("content", []) if b.get("type") == "text")
        env = parse_envelope(text)
        meta = parse_result_block(env.get("RC_RESULT", ""))
        row["status"] = meta.get("status", "no-envelope")
        row["summary"] = meta.get("summary", "")[:120]
        if env.get("RC_NOTES"):
            (out_dir / f"{cid}.notes.md").write_text(env["RC_NOTES"] + "\n", encoding="utf-8")
            notes_all.append(f"### {cid} ({row['file']})\n{env['RC_NOTES']}\n")
        patch = env.get("RC_PATCH", "").strip()
        if patch and row["status"] == "ok":
            patch_path = out_dir / f"{cid}.patch"
            patch_path.write_text(patch + "\n", encoding="utf-8", newline="\n")
            chk = git("apply", "--check", str(patch_path))
            row["check"] = "ok" if chk.returncode == 0 else "FAIL: " + (chk.stderr.strip().splitlines() or [""])[-1][:100]
        rows.append(row)

    if args.apply:
        branch = args.branch or f"batch/{name.replace('_', '-')}"
        cur = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        if cur != branch:
            if git("rev-parse", "--verify", branch).returncode != 0:
                git("branch", branch)
            co = git("checkout", branch)
            if co.returncode != 0:
                print("ingest: cannot check out", branch, co.stderr)
                return 1
        for row in rows:
            if row["check"] == "ok":
                patch_path = out_dir / f"{row['custom_id']}.patch"
                ap_ = git("apply", "--index", str(patch_path))
                if ap_.returncode == 0:
                    msg = f"batch {name}: {row['summary'] or row['custom_id']}\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
                    git("commit", "-q", "-m", msg)
                    row["applied"] = "yes"
                else:
                    row["applied"] = "FAIL"

    if retry:
        results.with_name(name + ".retry.jsonl").write_text("\n".join(retry) + "\n", encoding="utf-8", newline="\n")

    ok = sum(1 for r in rows if r["status"] == "ok")
    applied = sum(1 for r in rows if r["applied"] == "yes")
    bad = [r for r in rows if r["type"] != "succeeded" or r["status"] in ("error", "no-envelope", "refusal", "truncated") or r["check"].startswith("FAIL")]
    lines = [
        f"# Ingest report: {name}",
        "",
        f"- requests: {len(rows)}, ok: {ok}, skip: {sum(1 for r in rows if r['status'] == 'skip')}, needs attention: {len(bad)}, applied: {applied}",
        f"- tokens in/out: {total_in}/{total_out}, cache read: {total_cached} ({(100 * total_cached // total_in) if total_in else 0}% of input)",
        f"- retry payload: {name}.retry.jsonl ({len(retry)} lines)" if retry else "- nothing to retry",
        "",
        "| custom_id | file | status | check | applied | cache | tokens | summary |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['custom_id']} | {r['file']} | {r['status'] or r['type']} | {r['check']} | {r['applied']} | {r['cache']} | {r['tokens']} | {r['summary'].replace('|', '/')} |")
    if notes_all:
        lines += ["", "## Notes from the requests", ""] + notes_all
    report = out_dir / "INGEST_REPORT.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"ingest: {ok} ok, {len(bad)} need attention, {applied} applied -> {report}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
