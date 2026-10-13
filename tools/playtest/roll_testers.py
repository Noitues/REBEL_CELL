"""Roll a batch of Claude playtesters (docs/process/05_CLAUDE_PLAYTESTER.md).

    python tools/playtest/roll_testers.py --batch PB-001 --count 4 --seed 7 --build main
    python tools/playtest/roll_testers.py --batch PB-002 --count 2 --focus raids --persona strategist

Each tester gets a persona, a focus and one or two quirks drawn from tools/playtest/personas.json
with a seeded RNG (same --seed, same batch), a handle, its own session folder under
.playtest_sessions/<batch>/<handle>/ (screenshots, journal, its own user:// so saves never
collide), and a brief.md that is the only thing the playtester agent is given. The report goes
to docs/playtest/claude/<batch>/<handle>.md.

--build REF (re)points the shared game copy (.claude/worktrees/playtest-build) at REF and
imports it; every tester in the batch plays that one build. Without --build the existing copy
is used as is (its sha goes into the briefs).

Prints one line per tester: the brief path to hand to a `playtester` agent.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BUILD = ROOT / ".claude" / "worktrees" / "playtest-build"
SESSIONS = ROOT / ".playtest_sessions"
REPORTS = ROOT / "docs" / "playtest" / "claude"
ROSTER = ROOT / "tools" / "playtest" / "personas.json"
TEMPLATE = ROOT / "docs" / "process" / "templates" / "CLAUDE_PLAYTEST_FEEDBACK.md"
BLACKBOX = ROOT / "tools" / "playtest" / "blackbox.py"


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", check=False).stdout.strip()


def prepare_build(ref: str, godot: str) -> None:
    sha = git("rev-parse", "--verify", ref + "^{commit}")
    if not sha:
        sys.exit("roll_testers: unknown ref %s" % ref)
    if not (BUILD / "project.godot").exists():
        r = subprocess.run(["git", "worktree", "add", "--detach", str(BUILD), sha], cwd=ROOT,
                           capture_output=True, text=True)
        if r.returncode:
            sys.exit("roll_testers: git worktree add failed: %s" % r.stderr.strip())
    else:
        if (BUILD / ".quiet_runs").exists() and any((BUILD / ".quiet_runs").glob("*.pid")):
            sys.exit("roll_testers: playtesters are still running on the build copy; finish or stop them first")
        r = subprocess.run(["git", "checkout", "--detach", sha], cwd=BUILD, capture_output=True, text=True)
        if r.returncode:
            sys.exit("roll_testers: checkout in the build copy failed: %s" % r.stderr.strip())
    log = BUILD / "import.log"
    with open(log, "w", encoding="utf-8", errors="replace") as f:
        code = subprocess.run([godot, "--headless", "--path", str(BUILD), "--import"],
                              stdout=f, stderr=subprocess.STDOUT, timeout=1800).returncode
    if code:
        sys.exit("roll_testers: import failed (%d), see %s" % (code, log))
    print("build: %s @ %s (imported)" % (BUILD, sha[:8]))


def parse_mix(spec: str, roster: dict) -> list[tuple[str, str, str]]:
    """'novice=2,keyboard_only=1:readability_accessibility' -> [(tier, persona id or '', focus id or '')] per tester.
    A key is a skill tier or a persona id (which fixes the tier); ':focus' pins the focus (profiles in gate.py)."""
    pids = {p["id"]: p["tier"] for p in roster["personas"]}
    focuses = {f["id"] for f in roster["focuses"]}
    plan: list[tuple[str, str, str]] = []
    for tok in spec.split(","):
        key, _, rest = tok.partition("=")
        n, _, focus = rest.partition(":")
        if key in roster["tiers"]:
            tier, persona = key, ""
        elif key in pids:
            tier, persona = pids[key], key
        else:
            sys.exit("roll_testers: mix key %r is neither a tier nor a persona id" % key)
        if focus and focus not in focuses:
            sys.exit("roll_testers: mix focus %r unknown" % focus)
        plan += [(tier, persona, focus)] * int(n)
    return plan


def pick(rng: random.Random, items: list[dict], wanted: str | None) -> dict:
    if wanted:
        for it in items:
            if it["id"] == wanted:
                return it
        sys.exit("roll_testers: no entry with id %r" % wanted)
    return rng.choice(items)


def brief_text(batch: str, handle: str, persona: dict, focus: dict, quirks: list[str],
               sha: str, session: Path, report: Path, hours: float) -> str:
    bb = "python %s --session %s" % (BLACKBOX.as_posix(), session.as_posix())
    settings = "; ".join(focus["settings"]) if focus["settings"] else "leave every option at its default"
    q = "\n".join("- %s" % x for x in quirks)
    fq = "\n".join("%d. %s" % (i + 1, x) for i, x in enumerate(focus["questions"]))
    tutorial = ("Take the tutorial first (TUTORIAL on the title screen), then start a new campaign."
                if persona["tutorial"] == "take" else
                "Skip the tutorial: go straight to NEW CAMPAIGN (you may open it later if you are lost).")
    tier = persona["tier"]
    return f"""# Playtester brief — {handle} ({batch})

You are **{handle}**, a human playtester. You have never seen this game's code, design
documents or files and you never will: you only see the screen and use the mouse and
keyboard. Your agent rules (`.claude/agents/playtester.md`) say how; this brief says who
you are and what to play.

## Who you are: {persona['label']}
Skill tier: {tier}
{persona['bio']}
- Reading habits: {persona['reading']}
- Risk: {persona['risk']}
- Pace: {persona['pace']}
- How you write feedback: {persona['voice']}

Quirks (do these whenever they apply):
{q}

## Your focus: {focus['label']}
{focus['brief']}

Focus questions to answer in section 5 of the report:
{fq}

## What to play
- The game is REBEL_CELL, build `main @ {sha[:8]}`, a cyberpunk roguelite deckbuilder.
  That sentence is all you know about it; learn the rest from the game.
- Settings before you start: {settings}.
- {tutorial}
- Play **one full campaign from NEW CAMPAIGN to its end screen: won, lost, or truly stuck**.
  Pick the corporation, classes and choices your persona would pick.
- Time box: {hours:g} hours of wall-clock play. If it runs out, use the in-game Quit (the
  game saves), and report INCOMPLETE with how far you got.

## Your tools (Bash, exactly these; coordinates are pixels of the 1280x720 screenshot)
```
{bb} start --private-copy --project {BUILD.as_posix()}
{bb} shot [--grid]            # look (add --grid when you need coordinates)
{bb} move X Y                 # hover (tooltips)
{bb} click X Y [--right] [--double]
{bb} key NAME [NAME ...]      # e.g. space, esc, enter, tab, q, e, z, ctrl+z, x
{bb} type "text"
{bb} scroll X Y N             # N>0 up, N<0 down
{bb} wait SECONDS             # let animations/raid playouts run (max 30 per call)
{bb} status                   # running? minutes since start, shot count
{bb} stop                     # only at the very end
```
Every action prints the path of a fresh screenshot: Read it to see the result.

## Your files
- Session folder: `{session.as_posix()}` (shots/, actions.log, godot.log).
- Journal (your memory, keep it current): `{(session / 'journal.md').as_posix()}`
- Report (the deliverable): `{report.as_posix()}`, from the template
  `{TEMPLATE.relative_to(ROOT).as_posix()}`.
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--batch", required=True, help="batch id, e.g. PB-001")
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--seed", type=int, default=None, help="roster RNG seed (default: from the clock, printed)")
    ap.add_argument("--persona", help="force this persona id for every tester")
    ap.add_argument("--mix", help="testers per skill tier or persona id, e.g. novice=6,intermediate=3,expert=1 or "
                                  "keyboard_only=1:readability_accessibility (':focus' pins the focus; overrides --count)")
    ap.add_argument("--focus", help="force this focus id for every tester")
    ap.add_argument("--hours", type=float, default=4.0, help="wall-clock time box per tester")
    ap.add_argument("--build", metavar="REF", help="point the shared game copy at REF and import it first")
    ap.add_argument("--godot", default="godot")
    a = ap.parse_args()

    if a.build:
        prepare_build(a.build, a.godot)
    if not (BUILD / "project.godot").exists():
        sys.exit("roll_testers: no game copy at %s; pass --build main" % BUILD)
    sha = git("rev-parse", "HEAD", cwd=BUILD)

    seed = a.seed if a.seed is not None else int(dt.datetime.now().timestamp())
    rng = random.Random("%s/%d" % (a.batch, seed))
    roster = json.loads(ROSTER.read_text(encoding="utf-8"))
    handles = list(roster["handles"])
    rng.shuffle(handles)
    batch_dir = SESSIONS / a.batch
    used = {p.name for p in batch_dir.iterdir()} if batch_dir.exists() else set()
    handles = [h for h in handles if h not in used]
    if len(handles) < a.count:
        sys.exit("roll_testers: not enough unused handles in personas.json")

    # Spread personas and focuses across the batch before repeating any.
    personas = list(roster["personas"])
    mix_focus: list[str] = []
    if a.mix:
        plan = parse_mix(a.mix, roster)
        a.count = len(plan)
        by_tier = {t: [p for p in personas if p["tier"] == t] for t in roster["tiers"]}
        for t in by_tier.values():
            rng.shuffle(t)
        personas = [by_tier[t][i % len(by_tier[t])] for i, (t, _, _) in enumerate(plan)]
        pid = {p["id"]: p for p in roster["personas"]}
        personas = [pid[x[1]] if x[1] else p for x, p in zip(plan, personas)]
        mix_focus = [x[2] for x in plan]
    focuses = [f for f in roster["focuses"] if not f.get("motion_only")]  # the motion focus is only dealt on request
    if not a.mix:  # a mix is dealt in order so pinned personas and focuses stay with their slot
        rng.shuffle(personas)
    rng.shuffle(focuses)
    manifest = []
    for i in range(a.count):
        handle = handles[i]
        persona = pick(rng, roster["personas"], a.persona) if a.persona else personas[i % len(personas)]
        wanted_focus = a.focus or (mix_focus[i] if i < len(mix_focus) else "")
        focus = pick(rng, roster["focuses"], wanted_focus) if wanted_focus else focuses[i % len(focuses)]
        quirks = rng.sample(roster["quirks"], rng.choice([1, 2]))
        session = batch_dir / handle
        session.mkdir(parents=True, exist_ok=True)
        report = REPORTS / a.batch / ("%s.md" % handle)
        report.parent.mkdir(parents=True, exist_ok=True)
        brief = session / "brief.md"
        brief.write_text(brief_text(a.batch, handle, persona, focus, quirks, sha, session, report, a.hours),
                         encoding="utf-8")
        manifest.append({"handle": handle, "persona": persona["id"], "tier": persona["tier"], "focus": focus["id"],
                         "quirks": quirks, "brief": brief.as_posix(), "report": report.as_posix()})
        print(brief.as_posix())
    mf = batch_dir / "batch.json"
    earlier = json.loads(mf.read_text(encoding="utf-8")) if mf.exists() else {}
    rolls = earlier.get("rolls", []) + [{"seed": seed, "mix": a.mix or "", "count": a.count,
                                         "rolled": dt.datetime.now().isoformat(timespec="seconds")}]
    mf.write_text(json.dumps({"batch": a.batch, "build": sha, "rolls": rolls,
                              "testers": earlier.get("testers", []) + manifest}, indent=1), encoding="utf-8")
    print("seed: %d | build: %s | %d tester(s) in %s" % (seed, sha[:8], a.count, batch_dir.as_posix()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
