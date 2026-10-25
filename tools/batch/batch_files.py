"""Draft or fix whole files through the Message Batches API: one request per output file.

    python tools/batch/batch_files.py <job.json> --submit     # build the requests, submit, save the batch id next to the job
    python tools/batch/batch_files.py <job.json> --ingest     # wait (capped), fetch, write each file, print the cost

Job (JSON):
{
  "name": "l8_r1", "model": "claude-opus-5-5", "effort": "high", "max_tokens": 64000,
  "system": ["docs/handoff/raid_lab_l8/SPEC.md"],             # repo files joined into the cached system block
  "rules": "text appended to the system block",
  "requests": [
    {"id": "sweep_l8", "out": "tools/raid_concepts/sweep_l8.py", "lang": "python",
     "context": ["tools/raid_concepts/sweep_l5.py"],           # repo files put in the user turn
     "images": ["D:/rc_tmp/x.jpg"],                            # optional jpg/png attached to the user turn
     "task": "what to write"}
  ]
}
The answer must hold exactly one fenced block in `lang`, the whole file. It is written to `out` (LF). Credentials:
ANTHROPIC_API_KEY or the Windows user variable of that name (never printed). Written as a file on purpose: never run Python
from stdin on this machine.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_drafts import api_key  # noqa: E402

PRICE = {"claude-opus-5-5": (2.5, 12.5), "claude-sonnet-5-5": (1.5, 7.5), "claude-haiku-5-5": (0.5, 2.5)}  # $/MTok, batch
WAIT_CAP_S = 6 * 3600


def read(p: str) -> str:
    q = Path(p) if Path(p).is_absolute() else ROOT / p
    return q.read_text(encoding="utf-8")


def system_blocks(job: dict) -> list[dict]:
    parts = [f'<file path="{p}">\n{read(p)}\n</file>' for p in job.get("system", [])]
    parts.append(job.get("rules", ""))
    return [{"type": "text", "text": "\n\n".join(parts), "cache_control": {"type": "ephemeral"}}]


def user_content(r: dict) -> list[dict]:
    out: list[dict] = []
    for img in r.get("images", []):
        data = base64.standard_b64encode(Path(img).read_bytes()).decode()
        mt = "image/png" if img.lower().endswith(".png") else "image/jpeg"
        out.append({"type": "image", "source": {"type": "base64", "media_type": mt, "data": data}})
    ctx = "\n\n".join(f'<file path="{p}">\n{read(p)}\n</file>' for p in r.get("context", []))
    lang = r.get("lang", "")
    out.append({"type": "text", "text": f"{ctx}\n\n<task>\nWrite the whole file `{r['out']}`.\n{r['task']}\n</task>\n"
                                        f"Answer with exactly one fenced ```{lang} block holding the whole file, then at most 8 "
                                        "lines of notes (assumptions, doubts). No other prose."})
    return out


def build(job: dict) -> list[dict]:
    sysb = system_blocks(job)
    return [{"custom_id": f"{job['name']}__{r['id']}", "params": {
        "model": job["model"], "max_tokens": job.get("max_tokens", 64000), "system": sysb,
        "thinking": {"type": "adaptive"}, "output_config": {"effort": job.get("effort", "high")},
        "messages": [{"role": "user", "content": user_content(r)}]}} for r in job["requests"]]


def client():
    import anthropic
    return anthropic.Anthropic(api_key=api_key())


def submit(jp: Path, job: dict) -> None:
    reqs = build(job)
    b = client().messages.batches.create(requests=reqs)
    jp.with_suffix(".batch_id").write_text(b.id, encoding="utf-8")
    print("submitted", b.id, len(reqs), "requests")


def code_of(text: str, lang: str) -> str | None:
    m = re.search(r"```" + re.escape(lang) + r"[^\n]*\n(.*?)\n```", text, re.S) or re.search(r"```[^\n]*\n(.*?)\n```", text, re.S)
    return m.group(1) + "\n" if m else None


def ingest(jp: Path, job: dict) -> None:
    bid = jp.with_suffix(".batch_id").read_text(encoding="utf-8").strip()
    c = client()
    t0 = time.time()
    while True:
        b = c.messages.batches.retrieve(bid)
        if b.processing_status == "ended":
            break
        if time.time() - t0 > WAIT_CAP_S:
            print("still", b.processing_status, "after the wait cap; run --ingest again later")
            return
        time.sleep(60)
    by_id = {f"{job['name']}__{r['id']}": r for r in job["requests"]}
    pin, pout = PRICE.get(job["model"], (2.5, 12.5))
    total = 0.0
    notes_dir = jp.parent / (jp.stem + "_notes")
    notes_dir.mkdir(exist_ok=True)
    for res in c.messages.batches.results(bid):
        r = by_id[res.custom_id]
        if res.result.type != "succeeded":
            print(res.custom_id, res.result.type)
            continue
        m = res.result.message
        text = "".join(getattr(bk, "text", "") for bk in m.content)
        u = m.usage
        cost = ((u.input_tokens or 0) * pin + (getattr(u, "cache_creation_input_tokens", 0) or 0) * pin * 1.25
                + (getattr(u, "cache_read_input_tokens", 0) or 0) * pin * 0.1 + (u.output_tokens or 0) * pout) / 1e6
        total += cost
        code = code_of(text, r.get("lang", ""))
        print(res.custom_id, "stop", m.stop_reason, "out", u.output_tokens, f"${cost:.2f}", "written" if code else "NO CODE")
        (notes_dir / f"{r['id']}.md").write_text(text if not code else text.split("```")[-1].strip(), encoding="utf-8")
        if code:
            out = ROOT / r["out"]
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(code, encoding="utf-8", newline="\n")
    print(f"total ${total:.2f}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("job")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--ingest", action="store_true")
    a = ap.parse_args()
    jp = Path(a.job)
    job = json.loads(jp.read_text(encoding="utf-8"))
    if a.submit:
        submit(jp, job)
    if a.ingest:
        ingest(jp, job)


if __name__ == "__main__":
    main()
