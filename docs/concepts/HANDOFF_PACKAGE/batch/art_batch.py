"""Art-pass Message Batches lane (designer 2026-10-18: drafts and patches go to the Batch API).

    python art_batch.py submit <job.json>     # writes <job>.ids.json next to the job
    python art_batch.py collect <job.json>    # polls, writes each item's text to <out_dir>/<id>.md, and a cost line

job.json: {"out_dir": "...", "items": [{"id", "model", "max_tokens", "system", "prompt", "attach": [paths]}]}
Attachments are inlined as <file path="..."> blocks. Text only. The key is ANTHROPIC_API_KEY (env or Windows user var), never printed.
Written as a file on purpose: never run Python from stdin on this machine.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import anthropic

PRICE = {"claude-sonnet-5-5": (1.0, 5.0), "claude-haiku-4-5": (0.5, 2.5)}  # batch $/MTok in, out


def api_key() -> str:
    k = os.environ.get("ANTHROPIC_API_KEY")
    if k:
        return k
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as h:
        return winreg.QueryValueEx(h, "ANTHROPIC_API_KEY")[0]


def content(item: dict) -> str:
    parts = [item["prompt"]]
    for p in item.get("attach", []):
        parts.append(f'<file path="{p}">\n{Path(p).read_text(encoding="utf-8", errors="replace")}\n</file>')
    return "\n\n".join(parts)


def submit(job_path: Path) -> None:
    job = json.loads(job_path.read_text(encoding="utf-8"))
    reqs = [{"custom_id": it["id"], "params": {
        "model": it.get("model", "claude-sonnet-5-5"), "max_tokens": it.get("max_tokens", 16000),
        "system": it.get("system", ""), "messages": [{"role": "user", "content": content(it)}], **it.get("params", {})}} for it in job["items"]]
    b = anthropic.Anthropic(api_key=api_key()).messages.batches.create(requests=reqs)
    job_path.with_suffix(".ids.json").write_text(json.dumps({"batch": b.id}), encoding="utf-8")
    print("submitted", b.id, len(reqs))


def collect(job_path: Path, poll: int = 60) -> None:
    job = json.loads(job_path.read_text(encoding="utf-8"))
    bid = json.loads(job_path.with_suffix(".ids.json").read_text(encoding="utf-8"))["batch"]
    c = anthropic.Anthropic(api_key=api_key())
    while c.messages.batches.retrieve(bid).processing_status != "ended":
        time.sleep(poll)
    out = Path(job["out_dir"]); out.mkdir(parents=True, exist_ok=True)
    cost = 0.0
    for r in c.messages.batches.results(bid):
        if r.result.type != "succeeded":
            print(r.custom_id, r.result.type); continue
        m = r.result.message
        text = "".join(b.text for b in m.content if b.type == "text")
        (out / f"{r.custom_id}.md").write_text(text, encoding="utf-8", newline="\n")
        pi, po = PRICE.get(m.model, (1.0, 5.0))
        cost += m.usage.input_tokens / 1e6 * pi + m.usage.output_tokens / 1e6 * po
        print(r.custom_id, m.stop_reason, m.usage.input_tokens, m.usage.output_tokens, "chars", len(text), "EMPTY" if not text else "")
    print(f"cost about {cost:.3f} USD")


if __name__ == "__main__":
    {"submit": submit, "collect": collect}[sys.argv[1]](Path(sys.argv[2]))
