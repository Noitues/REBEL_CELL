"""Decision parity, visual vs headless (doc 05 §11): where a screen tester's turn was clearly worse than
the best plan, ask what on screen would have shown the better plan.

    python tools/playtest/parity.py --session .playtest_sessions/PB-014/<handle> [--max 20]

Needs a harness session with combat_steps.jsonl (every combat step's screenshot, and whether it
sent the turn). Steps:
1. Ground truth: every fight rebuilt from the game's combat replays (tools/agent/replay_audit.gd):
   per turn, what the tester did (in player words, with its exact result) and the best whole-turn plan.
2. Pairing: fight k of the session = the k-th of the last fights' replays; the first screenshot of
   each turn = that replay turn (fights whose turn counts disagree are skipped).
3. Disagreements: turns where the best plan deals 8+ more, takes 4+ less, or lands a Perfect the
   tester's did not.
4. For each (up to --max): Sonnet sees the turn-start screenshot (and both wheel close-ups) with both
   plans and their results, and says whether the better plan was visible, what was missing or
   misleading, and one concrete visual change.
5. One synthesis call ranks the visual changes by how many turns they would have fixed.
Report: docs/playtest/claude/parity/<batch>_<handle>.md (developer-facing).

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
DOCS = ROOT / "docs" / "playtest" / "claude" / "parity"
PROBE_SCHEMA = {"type": "object", "properties": {
    "better_plan_visible": {"type": "string", "enum": ["yes", "partly", "no"]},
    "missing_or_misleading": {"type": "string", "description": "what the screen did not show, or showed in a misleading way"},
    "visual_change": {"type": "string", "description": "one concrete change to the screen that would have shown the better plan"},
    "where": {"type": "string", "description": "the screen element it concerns (e.g. pointer, wheel rim, preview chips, card face)"}},
    "required": ["better_plan_visible", "missing_or_misleading", "visual_change", "where"], "additionalProperties": False}


def truth(session: Path, godot: str) -> list[dict]:
    out = session / "parity_truth.jsonl"
    with open(session / "parity_audit.log", "w", encoding="utf-8") as f:
        subprocess.run([godot, "--headless", "--path", str(ROOT), "-s", "tools/agent/replay_audit.gd", "--",
                        "in=%s" % (session / "game" / "saves" / "replays").resolve().as_posix(), "out=%s" % out.resolve().as_posix()],
                       stdout=f, stderr=subprocess.STDOUT, timeout=900)
    return [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]


def fights_from_steps(session: Path) -> list[list[str]]:
    """[[turn-start shot, ...] per fight] from combat_steps.jsonl."""
    steps = [json.loads(l) for l in (session / "combat_steps.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    fights, turns, new_turn = [], [], True
    for s in steps:
        if s["kind"] == "combat_result":
            if turns:
                fights.append(turns)
            turns, new_turn = [], True
            continue
        if new_turn:
            turns.append(s["shot"])
            new_turn = False
        if s["sends"]:
            new_turn = True
    if turns:
        fights.append(turns)
    return fights


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", required=True)
    ap.add_argument("--max", type=int, default=20)
    ap.add_argument("--godot", default="godot")
    a = ap.parse_args()
    import anthropic
    from PIL import Image

    session = Path(a.session).resolve()
    rows = truth(session, a.godot)
    by_replay: dict[str, list[dict]] = {}
    for r in rows:
        by_replay.setdefault(r["replay"], []).append(r)
    fights = fights_from_steps(session)
    tail = sorted(by_replay)[-len(fights):] if fights else []
    pairs, skipped = [], 0
    for shots, rep in zip(fights, tail):
        turns = by_replay[rep]
        if len(shots) != len(turns):
            skipped += 1
            continue
        pairs += [{"shot": s, "truth": t} for s, t in zip(shots, turns)]
    worse = [p for p in pairs if p["truth"]["best"]["dealt"] - p["truth"]["tester"]["dealt"] >= 8
             or p["truth"]["tester"]["taken"] - p["truth"]["best"]["taken"] >= 4
             or (p["truth"]["best"]["own_perfect"] and not p["truth"]["tester"]["own_perfect"])]
    print("%d fights, %d paired turns (%d fights skipped: turn counts differ), %d clearly worse than the best plan" % (
        len(fights), len(pairs), skipped, len(worse)))
    client = anthropic.Anthropic(api_key=hz.api_key(), base_url="https://api.anthropic.com", max_retries=5)
    usd, probes = 0.0, []
    for p in worse[: a.max]:
        t = p["truth"]
        img = Image.open(session / "shots" / p["shot"]).convert("RGB")
        content = [{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": hz.png_b64(img, (hz.SEND_W, hz.SEND_H))}}]
        for side in ("own", "enemy"):
            c = img.crop(hz.WHEEL_REGIONS[side])
            content += [{"type": "text", "text": "Close-up, %s wheel:" % ("your" if side == "own" else "enemy")},
                        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": hz.png_b64(c)}}]
        content.append({"type": "text", "text": (
            "This is the start of a turn in a wheel-combat deckbuilder (a Perfect = the pointer on the centre of a slice). "
            "A player looked at this screen and did: %s -> they dealt %d, took %d (pointers: %s). The best plan available was: "
            "%s. Judge the SCREEN, not the player: could a player have seen from this screen that the better plan was better? "
            "What did the screen not show, or show misleadingly? Give one concrete visual change that would have made the "
            "better plan visible." % (t["tester"].get("text", "?"), t["tester"]["dealt"], t["tester"]["taken"],
                                      "; ".join(t["tester"]["pointers"]), t["best"]["text"]))})
        r = client.messages.create(model=hz.MODELS["sonnet"], max_tokens=3000, messages=[{"role": "user", "content": content}],
                                   output_config={"effort": "medium", "format": {"type": "json_schema", "schema": PROBE_SCHEMA}})
        pin, pout, _, _ = hz.PRICES[hz.MODELS["sonnet"]]
        usd += ((r.usage.input_tokens or 0) * pin + (r.usage.output_tokens or 0) * pout) / 1e6
        ans = json.loads(next(b.text for b in r.content if b.type == "text"))
        probes.append({"shot": p["shot"], "tester": t["tester"], "best": t["best"], **ans})
        print(p["shot"], ans["better_plan_visible"], ans["where"], "|", ans["visual_change"][:120], flush=True)
    (session / "parity.json").write_text(json.dumps(probes, indent=1), encoding="utf-8")
    if not probes:
        print("nothing to probe")
        return 0
    synth = client.messages.create(model=hz.MODELS["sonnet"], max_tokens=6000, messages=[{"role": "user", "content": (
        "Below are per-turn findings from a playtest: at each turn the player made a clearly worse plan than the best "
        "available, and a reviewer said what the screen failed to show and one visual change. Group them into distinct "
        "visual changes, ranked by how many turns each would have fixed; for each: the change, the screen element, the "
        "turns (shot names) it covers, and why. Then list anything the screen DID show well. Markdown, concise, for the "
        "game's developers.\n\n" + json.dumps([{k: p[k] for k in ("shot", "better_plan_visible", "missing_or_misleading", "visual_change", "where")} for p in probes], indent=1))}],
        output_config={"effort": "medium"})
    usd += ((synth.usage.input_tokens or 0) * 2.0 + (synth.usage.output_tokens or 0) * 10.0) / 1e6
    DOCS.mkdir(parents=True, exist_ok=True)
    seen = {"yes": 0, "partly": 0, "no": 0}
    for p in probes:
        seen[p["better_plan_visible"]] += 1
    out = DOCS / ("%s_%s.md" % (session.parent.name, session.name))
    out.write_text("# Decision parity — %s/%s\n\n%d paired turns; %d clearly worse than the best plan; %d probed "
                   "(better plan visible from the screen: yes %d, partly %d, no %d). Cost $%.2f.\n\n%s\n" % (
                       session.parent.name, session.name, len(pairs), len(worse), len(probes), seen["yes"], seen["partly"],
                       seen["no"], usd, next(b.text for b in synth.content if b.type == "text")), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
