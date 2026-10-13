"""Perfect-legibility quiz (doc 05 §11): can a player tell from the screen where their pointer lands?

    python tools/playtest/perfect_quiz.py --session .playtest_sessions/PB-013/nullpoint

Needs a session played with `harness.py --probe-perfect N` (in fights it only screenshots each turn
start and sends, so screenshot k of a fight is exactly turn k of that fight's combat replay).
Steps: rebuild the fights headless (tools/agent/replay_audit.gd) for the ground truth per turn
(would the player's pointer land on a Perfect if they send now; what is the best plan), pair each
screenshot with its turn, then ask vision models the same question a player faces, in variants:

  A  Sonnet, the whole screen (960x540, as the testers see it)
  B  Sonnet, the whole screen + a full-resolution close-up of the player's wheel
  C  Haiku, the whole screen

Scores: accuracy on "Perfect if I send now?" against the truth, and the stated reason (what on
screen the model read). Report: docs/playtest/claude/probes/perfect_<batch>_<handle>.md.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as hz  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
DOCS = ROOT / "docs" / "playtest" / "claude" / "probes"
SCHEMA = {"type": "object", "properties": {
    "lands_perfect_if_send_now": {"type": "boolean"},
    "where_it_lands": {"type": "string", "description": "the slice your pointer would land on, and centre or edge"},
    "what_you_read": {"type": "string", "description": "what on the screen told you that"},
    "change_to_make_it_perfect": {"type": "string", "description": "one change (card or nudge, which wheel, which way), or 'none'"}},
    "required": ["lands_perfect_if_send_now", "where_it_lands", "what_you_read", "change_to_make_it_perfect"],
    "additionalProperties": False}
QUESTION = ("You are playing a wheel-combat deckbuilder. Each wheel's pointer (needle) lands on a slice when you SEND IT; "
            "landing on the CENTRE of a slice is a Perfect (the strongest result). This is the start of your turn and "
            "you have not acted yet. Looking only at the screen: if you sent the turn right now, would YOUR pointer "
            "land on a Perfect? Answer from what the screen shows, and say what you read.")
VARIANTS = {"A_sonnet_screen": ("sonnet", False), "B_sonnet_closeup": ("sonnet", True), "C_haiku_screen": ("haiku", False)}


def ground_truth(session: Path, godot: str) -> list[dict]:
    replays = session / "game" / "saves" / "replays"
    out = session / "probe" / "truth.jsonl"
    log = session / "probe" / "audit.log"
    with open(log, "w", encoding="utf-8") as f:
        subprocess.run([godot, "--headless", "--path", str(ROOT), "-s", "tools/agent/replay_audit.gd", "--",
                        "in=%s" % replays.resolve().as_posix(), "out=%s" % out.resolve().as_posix()],
                       stdout=f, stderr=subprocess.STDOUT, timeout=600)
    return [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]


def pair(session: Path, truth: list[dict]) -> list[dict]:
    shots = [json.loads(l) for l in (session / "probe" / "probe.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    by_replay: dict[str, list[dict]] = {}
    for t in truth:
        by_replay.setdefault(t["replay"], []).append(t)
    replays = sorted(by_replay)  # names carry the fight's end time: fight order
    fights: dict[int, list[dict]] = {}
    for s in shots:
        fights.setdefault(s["fight"], []).append(s)
    pairs = []
    # The probe's fights are the last len(fights) replays (earlier ones: fights played before the probe started).
    tail = replays[-len(fights):] if fights else []
    for k, (fight, fshots) in enumerate(sorted(fights.items())):
        if k >= len(tail):
            break
        rows = by_replay[tail[k]]
        if len(rows) < len(fshots):
            print("fight %d: %d shots but %d replay turns: skipped (the counts must match)" % (fight, len(fshots), len(rows)))
            continue
        for s in fshots:
            pairs.append({"shot": s["shot"], "fight": fight, "turn": s["turn"], "truth": rows[s["turn"]]})
    return pairs


def ask(client, model: str, img, closeup) -> tuple[dict | None, float]:
    content = [{"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                            "data": hz.png_b64(img, (hz.SEND_W, hz.SEND_H))}}]
    if closeup is not None:
        content += [{"type": "text", "text": "Close-up of your wheel at full resolution:"},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": hz.png_b64(closeup)}}]
    content.append({"type": "text", "text": QUESTION})
    r = client.messages.create(model=hz.MODELS[model], max_tokens=2000, messages=[{"role": "user", "content": content}],
                               output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}})
    pin, pout, pcr, pcw = hz.PRICES[hz.MODELS[model]]
    usd = ((r.usage.input_tokens or 0) * pin + (r.usage.output_tokens or 0) * pout) / 1e6
    try:
        return json.loads(next(b.text for b in r.content if b.type == "text")), usd
    except (StopIteration, json.JSONDecodeError):
        return None, usd


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", required=True)
    ap.add_argument("--godot", default="godot")
    ap.add_argument("--max", type=int, default=30, help="most screenshots quizzed")
    a = ap.parse_args()
    import anthropic
    from PIL import Image

    session = Path(a.session).resolve()
    truth = ground_truth(session, a.godot)
    pairs = pair(session, truth)[: a.max]
    if not pairs:
        print("no screenshot could be paired with a replay turn")
        return 1
    client = anthropic.Anthropic(api_key=hz.api_key(), base_url="https://api.anthropic.com", max_retries=5)
    usd, rows = 0.0, []
    for p in pairs:
        img = Image.open(session / "probe" / p["shot"]).convert("RGB")
        close = img.crop(hz.WHEEL_REGIONS["own"])
        close = close.resize((close.width * 3 // 2, close.height * 3 // 2))
        row = {"shot": p["shot"], "truth_perfect": p["truth"]["no_action"]["own_perfect"],
               "truth_best": p["truth"]["best"]["text"], "truth_pointers": p["truth"]["tester"]["pointers"]}
        for v, (model, with_close) in VARIANTS.items():
            ans, c = ask(client, model, img, close if with_close else None)
            usd += c
            row[v] = ans
        rows.append(row)
        print(p["shot"], "truth", row["truth_perfect"], {v: (row[v] or {}).get("lands_perfect_if_send_now") for v in VARIANTS}, flush=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    name = "perfect_%s_%s" % (session.parent.name, session.name)
    (session / "probe" / "quiz.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    lines = ["# Perfect-legibility quiz — %s/%s" % (session.parent.name, session.name), "",
             "%d turn-start screenshots paired with replay ground truth; cost $%.2f." % (len(rows), usd),
             "Question: *if you sent the turn now, would your pointer land on a Perfect?* (no action taken yet)", "",
             "| Variant | Accuracy | Says Perfect when it is not | Misses a real Perfect |", "|---|---|---|---|"]
    for v in VARIANTS:
        ok = [r for r in rows if r[v] is not None]
        acc = sum(r[v]["lands_perfect_if_send_now"] == r["truth_perfect"] for r in ok)
        fp = sum(r[v]["lands_perfect_if_send_now"] and not r["truth_perfect"] for r in ok)
        fn = sum((not r[v]["lands_perfect_if_send_now"]) and r["truth_perfect"] for r in ok)
        lines.append("| %s | %d/%d (%d%%) | %d | %d |" % (v, acc, len(ok), round(100 * acc / max(1, len(ok))), fp, fn))
    base = sum(r["truth_perfect"] for r in rows)
    lines += ["", "Truth: a Perfect with no action on %d of %d turns (always answering \"no\" scores %d%%)." % (
        base, len(rows), round(100 * (len(rows) - base) / max(1, len(rows)))), "", "## What the models read (sample)", ""]
    for r in rows[:12]:
        b = r.get("B_sonnet_closeup") or {}
        lines.append("- %s — truth: %s (%s) | B says %s, lands on *%s*, read: %s | fix: %s" % (
            r["shot"], "Perfect" if r["truth_perfect"] else "not Perfect", "; ".join(r["truth_pointers"])[:140],
            b.get("lands_perfect_if_send_now"), b.get("where_it_lands", "")[:80], b.get("what_you_read", "")[:160],
            b.get("change_to_make_it_perfect", "")[:100]))
    out = DOCS / ("%s.md" % name)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
