"""Decision parity, visual vs headless (doc 05 §11): where a screen tester's turn was clearly worse than
the best plan, ask what on screen would have shown the better plan.

    python tools/playtest/parity.py --session .playtest_sessions/PB-014/<handle> [--max 20]

Needs a harness session with combat_steps.jsonl (every combat step's screenshot, and whether it
sent the turn). Steps:
1. Ground truth: every fight rebuilt from the game's combat replays (tools/agent/replay_audit.gd):
   per turn, what the tester did (in player words, with its exact result) and the best whole-turn plan.
2. Pairing (pair_turns): the last K step-fights in play order = the K replays by end time (or the fight ending
   within 30 s of the replay's end); the n-th turn start = replay turn n when the counts agree, else the turn
   start whose on-screen TURN header says n. With 0 paired turns it exits 2 and spends nothing.
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


def fights_from_steps(steps: list[dict]) -> list[list[dict]]:
    """[[first step of each turn, ...] per fight] from the combat_steps rows. A fight ends at a combat_result step; a turn
    ends at a step that sends (SEND IT). Each row keeps its shot, the TURN number the tester read on screen and epoch_ms."""
    fights, turns, new_turn = [], [], True
    for s in steps:
        if s["kind"] == "combat_result":
            if turns:
                fights.append(turns)
            turns, new_turn = [], True
            continue
        if new_turn:
            turns.append(s)
            new_turn = False
        if s.get("sends"):
            new_turn = True
    if turns:
        fights.append(turns)
    return fights


def pair_turns(by_replay: dict[str, list[dict]], steps: list[dict]) -> tuple[list[dict], int]:
    """Pairs the replays' turns with the first screenshot of each turn: ([{shot, truth}], fights left unpaired).

    1. Fights: replay files sort by their write time (replay_<ms>_<seed>.json, the fight's end), and the harness logs
       fights in play order, so the last K step-fights are matched to the K replays in order (extra earlier step-fights,
       e.g. a fight whose replay was not written, fall off the front). When the end times are usable (every
       step row has epoch_ms) a step-fight whose last row is within 30 s of the replay's end is preferred.
    2. Turns: replay turn n is the n-th turn start of its fight when the counts agree; otherwise it is the turn start
       whose on-screen TURN header says n (PB-014 paired nothing because it matched only on that header).
    """
    names = sorted(by_replay)
    fights = fights_from_steps(steps)
    pairs, unpaired = [], 0
    offset = max(0, len(fights) - len(names))
    for k, rep in enumerate(names):
        idx = k + offset
        # prefer the step-fight that ends nearest this replay's end time, when the times are there
        end = int(rep.split("_")[1]) if rep.split("_")[1].isdigit() else 0
        timed = [(abs(f[-1].get("epoch_ms", 0) - end), i) for i, f in enumerate(fights) if f and f[-1].get("epoch_ms")]
        if end and timed:
            gap, best = min(timed)
            if gap <= 30000:
                idx = best
        if idx >= len(fights):
            unpaired += 1
            continue
        starts, truth = fights[idx], by_replay[rep]
        by_header = {int(r.get("turn", 0)): r for r in starts if r.get("turn")}
        got = 0
        for i, t in enumerate(truth):
            row = starts[i] if len(starts) == len(truth) else by_header.get(t["turn"])
            if row is not None:
                pairs.append({"shot": row["shot"], "truth": t})
                got += 1
        if not got:
            unpaired += 1
    return pairs, unpaired


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
    steps = [json.loads(l) for l in (session / "combat_steps.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    pairs, skipped = pair_turns(by_replay, steps)
    fights = sorted(by_replay)
    worse = [p for p in pairs if p["truth"]["best"]["dealt"] - p["truth"]["tester"]["dealt"] >= 8
             or p["truth"]["tester"]["taken"] - p["truth"]["best"]["taken"] >= 4
             or (p["truth"]["best"]["own_perfect"] and not p["truth"]["tester"]["own_perfect"])]
    print("%d fights, %d paired turns (%d fights without screenshots), %d clearly worse than the best plan" % (
        len(fights), len(pairs), skipped, len(worse)))
    if not pairs:  # nothing to show a model: do not spend (PB-014 paid $1.18 for 0 paired turns)
        print("parity: 0 paired turns; refusing to spend on probes (check combat_steps.jsonl and the replays)", file=sys.stderr)
        return 2
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
