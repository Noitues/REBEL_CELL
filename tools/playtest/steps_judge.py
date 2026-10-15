"""Judge the PT-003 scripted steps in the Message Batches API (vision, half price).

    python tools/playtest/steps_judge.py run [--dir .playtest_sessions/PT003-steps] [--max-usd 2]
    python tools/playtest/steps_judge.py estimate      # token / cost estimate only, nothing sent
    python tools/playtest/steps_judge.py report        # rewrite the .md from an already ingested results file

Input: <dir>/steps.json and the screenshots written by tools/playtest/steps/pt003_steps.gd (one windowed run).
One request per step: the screenshots (base64 JPEG), the step's where / action / adjusted PASS sentence and the
machine facts the script read. The model answers JSON {verdict: PASS|FAIL|PARTIAL, seen, reason}. Steps marked
SKIP are not sent. Hard budget: the estimate (with the output cap) must stay under --max-usd or nothing is sent.
Output: <dir>/judge/{requests.jsonl,results.jsonl,verdicts.json} and docs/playtest/claude/steps/PT-003_steps.md.
API key: ANTHROPIC_API_KEY from the environment or the Windows user environment (harness.api_key); never printed.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as hz  # noqa: E402

ROOT = hz.ROOT
MODEL = "claude-haiku-5-5"
PRICE_IN, PRICE_OUT = hz.PRICES[MODEL][0], hz.PRICES[MODEL][1]  # $ per million tokens, standard rate
BATCH_FACTOR = 0.5
MAX_OUT = 1500
MAX_EDGE = 1568
OUT_MD = ROOT / "docs" / "playtest" / "claude" / "steps" / "PT-003_steps.md"

SYSTEM = """You are a careful game QA tester judging ONE step of a playtest of REBEL_CELL (a cyberpunk deckbuilder) from screenshots
that a script captured while driving the real game. Judge only what the screenshots and the machine facts show.
Rules: PASS = the PASS sentence holds at first sight. FAIL = it does not, or the screen shows a crash, a raw KEY_ string,
broken or clipped text, or something clearly wrong. PARTIAL = it holds with a nit you would still ship (say what).
Designer rulings of 2026-10-14 apply: map name tags show only on hover of a node or when the map key is hovered, never at rest;
the rewards list also shows for a single pick; crew reads 'X (Stationed: Y)'; CELL HOLDS is a sticker.
Machine facts are read directly from the game state and are reliable; use them with the pictures. Multi-frame images are contact
sheets (left to right, then down, time order). If the screenshots cannot show what the step needs, say so in reason and use PARTIAL,
not PASS. Reply with ONLY a JSON object: {"verdict": "PASS"|"FAIL"|"PARTIAL", "seen": "<what the screenshots show, max 60 words>", "reason": "<why, max 40 words>"}. No prose, no code fence, no thinking out loud."""


def load_steps(d: Path) -> list[dict]:
    return json.loads((d / "steps.json").read_text(encoding="utf-8"))["steps"]


def image_block(path: Path) -> tuple[dict, int]:
    from PIL import Image

    im = Image.open(path).convert("RGB")
    w, h = im.size
    k = min(1.0, MAX_EDGE / max(w, h))
    if k < 1.0:
        im = im.resize((round(w * k), round(h * k)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=85)
    tokens = round(im.size[0] * im.size[1] / 750)
    block = {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}}
    return block, tokens


def build(d: Path) -> tuple[list[dict], int]:
    reqs, tokens = [], 0
    for s in load_steps(d):
        if s["status"].startswith("SKIP") or not s["shots"]:
            continue
        content: list[dict] = []
        for rel in s["shots"]:
            content.append({"type": "text", "text": f"Screenshot {rel}:"})
            blk, t = image_block(d / rel)
            content.append(blk)
            tokens += t + 20
        text = (f"STEP {s['id']}\nWhere: {s['where']}\nAction performed by the script: {s['action']}\n"
                f"PASS when: {s['pass_when']}\nMachine facts (read from the game): {json.dumps(s['facts'], ensure_ascii=False)}\n"
                "Judge now. JSON only.")
        content.append({"type": "text", "text": text})
        tokens += len(SYSTEM + text) // 4
        reqs.append({"custom_id": f"step-{s['id']}", "params": {"model": MODEL, "max_tokens": MAX_OUT, "system": SYSTEM,
                                                                 "messages": [{"role": "user", "content": content}]}})
    return reqs, tokens


def estimate_usd(in_tokens: int, n: int) -> float:
    return (in_tokens * PRICE_IN + n * MAX_OUT * PRICE_OUT) / 1e6 * BATCH_FACTOR


def client():
    import anthropic

    return anthropic.Anthropic(api_key=hz.api_key(), base_url="https://api.anthropic.com", max_retries=5)


def parse_verdict(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    try:
        v = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        v = {}
    if v.get("verdict") not in ("PASS", "FAIL", "PARTIAL"):
        # Lenient fallback: pull the fields out of near-JSON (unescaped quotes inside the strings).
        vm = re.search(r'"verdict"\s*:\s*"(PASS|FAIL|PARTIAL)"', text)
        sm = re.search(r'"seen"\s*:\s*"(.*?)"\s*,\s*"reason"', text, re.S)
        rm = re.search(r'"reason"\s*:\s*"(.*)', text, re.S)
        if vm:
            return {"verdict": vm.group(1), "seen": sm.group(1) if sm else text[:300],
                    "reason": rm.group(1).rstrip().rstrip("}").rstrip().rstrip('"') if rm else "(reply had broken JSON; fields recovered)"}
        return {"verdict": "PARTIAL", "seen": text[:300], "reason": "judge reply was not valid JSON"}
    return v


def run(d: Path, max_usd: float, estimate_only: bool) -> int:
    jd = d / "judge"
    jd.mkdir(exist_ok=True)
    reqs, in_tokens = build(d)
    est = estimate_usd(in_tokens, len(reqs))
    print(f"steps_judge: {len(reqs)} requests, ~{in_tokens} input tokens, estimated ${est:.3f} (batch rate, output cap included), budget ${max_usd}")
    if est > max_usd:
        print("steps_judge: over budget, nothing sent")
        return 2
    if estimate_only:
        return 0
    with (jd / "requests.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for r in reqs:
            fh.write(json.dumps(r) + "\n")
    cl = client()
    batch = cl.messages.batches.create(requests=reqs)
    print(f"steps_judge: submitted {batch.id}")
    (jd / "batch_id.txt").write_text(batch.id + "\n", encoding="utf-8")
    while True:
        b = cl.messages.batches.retrieve(batch.id)
        if b.processing_status == "ended":
            break
        print(f"  {b.processing_status}: {b.request_counts}")
        time.sleep(30)
    verdicts, usage_in, usage_out = {}, 0, 0
    with (jd / "results.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for r in cl.messages.batches.results(batch.id):
            fh.write(r.model_dump_json() + "\n")
            sid = r.custom_id.removeprefix("step-")
            if r.result.type == "succeeded":
                msg = r.result.message
                usage_in += msg.usage.input_tokens
                usage_out += msg.usage.output_tokens
                text = "".join(b.text for b in msg.content if b.type == "text")
                verdicts[sid] = parse_verdict(text)
            else:
                verdicts[sid] = {"verdict": "PARTIAL", "seen": "", "reason": f"batch request {r.result.type}"}
    cost = (usage_in * PRICE_IN + usage_out * PRICE_OUT) / 1e6 * BATCH_FACTOR
    (jd / "verdicts.json").write_text(json.dumps({"verdicts": verdicts, "input_tokens": usage_in, "output_tokens": usage_out,
                                                  "cost_usd": cost, "batch": batch.id}, indent=1), encoding="utf-8")
    print(f"steps_judge: ingested {len(verdicts)} verdicts, {usage_in} in / {usage_out} out tokens, ${cost:.3f}")
    return report(d)


def cell(s: str) -> str:
    return str(s).replace("|", "/").replace("\n", " ")


def report(d: Path) -> int:
    steps = load_steps(d)
    vd = json.loads((d / "judge" / "verdicts.json").read_text(encoding="utf-8"))
    v = vd["verdicts"]
    rows, counts, nonpass = [], {"PASS": 0, "FAIL": 0, "PARTIAL": 0, "SKIP": 0}, []
    for s in steps:
        sid = s["id"]
        shots = ", ".join(f"`.playtest_sessions/PT003-steps/{p}`" for p in s["shots"]) or "-"
        if s["status"].startswith("SKIP") or sid not in v:
            counts["SKIP"] += 1
            nonpass.append(f"{sid} SKIP")
            rows.append(f"| {sid} | {cell(s['pass_when'])} | SKIP | {cell(s['status'])} | {shots} |")
            continue
        x = v[sid]
        counts[x["verdict"]] += 1
        if x["verdict"] != "PASS":
            nonpass.append(f"{sid} {x['verdict']}")
        rows.append(f"| {sid} | {cell(s['pass_when'])} | {x['verdict']} | {cell(x['seen'])} Reason: {cell(x['reason'])} | {shots} |")
    status = "PASS" if counts["FAIL"] == 0 and counts["PARTIAL"] == 0 else ("FAIL" if counts["FAIL"] else "PARTIAL")
    notes = []
    for s in steps:
        x = v.get(s["id"])
        if x and x["verdict"] != "PASS":
            notes.append(f"{s['id']}: {x['reason']}")
    md = f"""# PT-003 scripted steps (batch-judged)

One windowed capture run of `tools/playtest/steps/pt003_steps.gd` drove the real game to each step of
`docs/playtest/PT-003_plan-1-waves-3-to-5-city-clarity.md` section 2; `{MODEL}` judged the screenshots through the Message Batches API
(`tools/playtest/steps_judge.py`). The PASS sentences are adjusted for the 2026-10-14 rulings (map tags only on hover or map-key hover,
never at rest; the rewards list for a single pick; crew "X (Stationed: Y)"; CELL HOLDS a sticker). Where a UI gesture was
driven through the method it calls (select_card, open_reward, the drop handler), the step's action says so in `steps.json`.
A model judge on a screenshot is evidence, not a verdict: the designer's own pass overrules it.

| step | adjusted PASS | verdict | what was seen | screenshots |
|---|---|---|---|---|
""" + "\n".join(rows) + f"""

**Summary:** {counts['PASS']} PASS, {counts['PARTIAL']} PARTIAL, {counts['FAIL']} FAIL, {counts['SKIP']} SKIP of {len(steps)} steps.
**Cost:** ${vd['cost_usd']:.3f} at the batch rate ({vd['input_tokens']} input / {vd['output_tokens']} output tokens, {vd['batch']}); budget $2.

```
PLAYTEST: PT-003
STATUS: {status}
STEPS: {', '.join(nonpass) if nonpass else 'none'}
NOTES: {'; '.join(notes) if notes else 'none'}
```
"""
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(md, encoding="utf-8", newline="\n")
    print(f"steps_judge: wrote {OUT_MD}")
    print(json.dumps(counts), "cost", round(vd["cost_usd"], 4))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["run", "estimate", "report"])
    ap.add_argument("--dir", default=str(ROOT / ".playtest_sessions" / "PT003-steps"))
    ap.add_argument("--max-usd", type=float, default=2.0)
    a = ap.parse_args()
    d = Path(a.dir)
    if a.cmd == "report":
        # Re-ingest the stored batch results (no API call), then rewrite the .md.
        jd = d / "judge"
        old = json.loads((jd / "verdicts.json").read_text(encoding="utf-8"))
        verdicts = {}
        for line in (jd / "results.jsonl").read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            sid = r["custom_id"].removeprefix("step-")
            if r["result"]["type"] == "succeeded":
                text = "".join(b.get("text", "") for b in r["result"]["message"]["content"])
                verdicts[sid] = parse_verdict(text)
            else:
                verdicts[sid] = {"verdict": "PARTIAL", "seen": "", "reason": f"batch request {r['result']['type']}"}
        old["verdicts"] = verdicts
        (jd / "verdicts.json").write_text(json.dumps(old, indent=1), encoding="utf-8")
        return report(d)
    return run(d, a.max_usd, a.cmd == "estimate")


if __name__ == "__main__":
    sys.exit(main())
