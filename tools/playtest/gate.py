"""Playtest routine for a User-Ready Gate (docs/process/04 + 05 section 12): one command, by wave type.

    python tools/playtest/gate.py --gate PT-014 --profile combat --compare PB-010
    python tools/playtest/gate.py --gate PT-015 --profile flow --at route:to_netrun
    python tools/playtest/gate.py --gate PT-015 --profile city --dry-run          # the plan and the $ caps, no API calls
    python tools/playtest/gate.py --gate PT-020                                   # no profile = milestone

Profiles (PLAYTEST_COST_REVIEW section 4): flow, combat, access, city, balance, milestone. Each one fixes the tester
mix, where each tester starts (a route or a save at the changed area; novices on onboarding start at the title),
the time box and dollar cap per tier, and what is skipped (expert, motion, parity, LLM sweep ...). Motion is held:
no profile contains a motion tester.

1. Build and routes: points the build copy at main (roll_testers --build), replays every recorded route on a fresh
   copy (routes.py test). A route that breaks means the UI changed; it is listed in the gate summary to re-record
   and testers fall back to starting from the title.
2. State sweep (state_agent.py), when the profile has one: `--state-mode heuristic` (free, deterministic) or `llm`.
3. Screen batch (run_batch.py): the profile's mix, judged in batch (screen audit only on screens that changed since
   `--compare`), findings compared with --compare, combat skill from the replays (ground truth). Screen testers do
   not escalate on combat turn starts unless `--combat-escalation`.
4. Decision parity (parity.py), when the profile has it: on the first intermediate session; refuses to spend when
   0 turns pair.
Writes docs/playtest/claude/gates/<gate>.md. `--dry-run` prints the plan and the estimated dollars and stops.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS = ROOT / "tools" / "playtest"
DOCS = ROOT / "docs" / "playtest" / "claude"
sys.path.insert(0, str(TOOLS))

# Per tier box used by profiles: "minutes:dollar cap". Cheaper than run_batch.TIERS (60/1.5, 120/4.0, 240/14.0).
BOX_NOVICE = "40:1.0"
BOX_INTERMEDIATE = "60:2.0"
# `{at}` in a start spec = the --at option (the area the wave changed).
PROFILES: dict[str, dict] = {
    "flow": {
        "about": "flow bugs: routes, 2 novices + 1 intermediate at the fixed screens, soft-lock sweep",
        "mix": "novice=2,intermediate=1",
        "starts": {"novice": "{at}", "intermediate": "{at}"},
        "limits": {"novice": BOX_NOVICE, "intermediate": BOX_INTERMEDIATE},
        "state": "mode", "seeds": "1000-1019", "parity": False,
        "skips": "expert, motion, parity, LLM sweep",
    },
    "combat": {
        "about": "combat legibility: 2 novices + 2 intermediates (one keyboard_only) from a netrun save, no combat escalation",
        "mix": "novice=2,intermediate=1,keyboard_only=1",
        "starts": {"novice": "{at}", "intermediate": "{at}", "keyboard_only": "{at}"},
        "limits": {"novice": BOX_NOVICE, "intermediate": BOX_INTERMEDIATE},
        "state": "none", "seeds": "", "parity": True,
        "skips": "expert, motion, state sweep",
    },
    "access": {
        "about": "accessibility / text size / contrast: novice + keyboard_only intermediate at text 2.0 and high contrast",
        "mix": "novice=1:readability_accessibility,keyboard_only=1:readability_accessibility",
        "starts": {"novice": "{at}", "keyboard_only": "{at}"},
        "limits": {"novice": BOX_NOVICE, "intermediate": BOX_INTERMEDIATE},
        "state": "none", "seeds": "", "parity": False,
        "skips": "expert, motion, parity, state sweep",
    },
    "city": {
        "about": "city clarity: 3 novices from New Campaign + 1 intermediate explorer",
        "mix": "novice=3,explorer=1",
        "starts": {"novice": "title", "explorer": "{at}"},
        "limits": {"novice": BOX_NOVICE, "intermediate": BOX_INTERMEDIATE},
        "state": "none", "seeds": "", "parity": False,
        "skips": "expert, motion, parity, state sweep",
    },
    "balance": {
        "about": "boss / balance: state sweep (20 seeds, 2-turn lookahead when supported) + 1 expert from a strong save, 30 min",
        "mix": "expert=1",
        "starts": {"expert": "save:heat>=25"},
        "limits": {"expert": "30:3.0"},
        "state": "mode", "seeds": "1000-1019", "parity": False,
        "skips": "novices, motion, parity, rest of the screen batch",
    },
    "milestone": {
        "about": "milestone gate: 2 novices, 2 intermediates, 1 expert from saves, plus an LLM sweep (and the free heuristic sweep)",
        "mix": "novice=2,intermediate=2,expert=1",
        "starts": {"novice": "title", "intermediate": "{at}", "expert": "save:heat>=25"},
        "limits": {"novice": BOX_NOVICE, "intermediate": BOX_INTERMEDIATE, "expert": "120:8.0"},
        "state": "both", "seeds": "1000-1019", "parity": False,
        "skips": "motion",
    },
}
DEFAULT_PROFILE = "milestone"
# Typical (not cap) spend, from the measured gates (PLAYTEST_COST_REVIEW 1) after the savings.
TYPICAL = {"novice": 0.35, "intermediate": 1.0}
EXPERT_TYPICAL_OF_CAP = 0.8
JUDGE_BASE, JUDGE_PER_TESTER, JUDGE_RESERVE_PER_TESTER = 0.6, 0.15, 0.4
LLM_SWEEP_PER_5_SEEDS = 9.4
PARITY_TYPICAL = 0.5
DEFAULT_STATE_BUDGET = 12.0


def run(cmd: list[str], log: Path, timeout: float | None = None) -> int:
    with open(log, "w", encoding="utf-8") as f:
        return subprocess.run(cmd, cwd=str(ROOT), stdout=f, stderr=subprocess.STDOUT, timeout=timeout).returncode


def section(md: Path, start: str, stop: str) -> str:
    if not md.exists():
        return "(missing: %s)" % md.name
    text = md.read_text(encoding="utf-8")
    m = re.search(re.escape(start) + r"(.*?)(?=" + re.escape(stop) + r"|\Z)", text, re.S)
    return ((start if start.startswith("|") else "") + m.group(1)).strip() if m else "(no %s)" % start


def seed_count(seeds: str) -> int:
    lo, _, hi = seeds.partition("-")
    return int(hi or lo) - int(lo) + 1 if seeds else 0


LLM_SWEEP_SEEDS = "1000-1004"  # an LLM sweep is always the 5-seed calibration (about $9); the heuristic takes any number


def seeds_for(mode: str, seeds: str) -> str:
    return LLM_SWEEP_SEEDS if mode == "llm" and seed_count(seeds) > 5 else seeds


def state_runs(profile: dict, mode: str) -> list[str]:
    """The state sweeps this profile runs with --state-mode `mode`: 'heuristic' and/or 'llm'."""
    if profile["state"] == "none":
        return []
    if profile["state"] == "both":
        return ["llm", "heuristic"]
    return [mode]


def make_plan(name: str, a: argparse.Namespace) -> dict:
    """The whole plan of a gate, with no I/O beyond reading personas.json and the route library: used by the dry run,
    the real run and the tests."""
    import roll_testers
    import run_batch

    prof = PROFILES[name]
    roster = json.loads(roll_testers.ROSTER.read_text(encoding="utf-8"))
    slots = roll_testers.parse_mix(prof["mix"], roster)
    testers = [{"handle": "t%d" % (i + 1), "tier": tier, "persona": persona, "focus": focus}
               for i, (tier, persona, focus) in enumerate(slots)]
    starts = {k: v.replace("{at}", a.at) for k, v in prof["starts"].items()}
    limits = run_batch.parse_limits(",".join("%s=%s" % kv for kv in prof["limits"].items()))
    rows = run_batch.plan_for(testers, None, None, 0, starts, limits)
    rows.sort(key=lambda r: r["handle"])
    for r in rows:
        r["start"] = ("save " + r["save"]) if r["save"] else (("route " + r["route"]) if r["route"] else "title")
        r["typical"] = (r["cap"] * EXPERT_TYPICAL_OF_CAP) if r["tier"] == "expert" else TYPICAL[r["tier"]]
    n = len(rows)
    runs = state_runs(prof, a.state_mode)
    state_cap = {}
    state_est = {}
    for m in runs:
        state_cap[m] = a.state_budget if m == "llm" else 0.0
        state_est[m] = min(a.state_budget, LLM_SWEEP_PER_5_SEEDS * seed_count(seeds_for(m, prof["seeds"])) / 5) if m == "llm" else 0.0
    caps = sum(r["cap"] for r in rows)
    reserve = round(JUDGE_BASE + JUDGE_RESERVE_PER_TESTER * n, 2)
    plan = {
        "profile": name, "about": prof["about"], "testers": rows, "starts": starts, "limits": prof["limits"],
        "mix": prof["mix"], "state_runs": runs, "seeds": prof["seeds"], "state_cap": state_cap, "state_est": state_est,
        "parity": prof["parity"], "skips": prof["skips"], "judge_reserve": reserve, "caps_total": round(caps, 2),
        "screen_budget": round(caps + reserve, 2),
        "est_typical": round(sum(r["typical"] for r in rows) + JUDGE_BASE + JUDGE_PER_TESTER * n + sum(state_est.values())
                             + (PARITY_TYPICAL if prof["parity"] else 0.0), 2),
        "est_max": round(caps + reserve + sum(state_cap.values()) + (2.0 if prof["parity"] else 0.0), 2),
        "combat_escalation": a.combat_escalation, "audit_all": a.audit_all,
    }
    return plan


def print_plan(p: dict) -> str:
    lines = ["Profile %s: %s" % (p["profile"], p["about"]),
             "Skips: %s. Motion: held (no motion tester in any profile)." % p["skips"],
             "Combat escalation: %s. Screen audit: %s." % ("on" if p["combat_escalation"] else "off",
                                                          "all screens" if p["audit_all"] else "only screens changed since --compare"),
             "", "| Tester | Tier | Persona | Focus | Start | Box (min) | $ cap |", "|---|---|---|---|---|---|---|"]
    for r in p["testers"]:
        lines.append("| %s | %s | %s | %s | %s | %d | %.2f |" % (r["handle"], r["tier"], r["persona"] or "(rolled)",
                                                               r["focus"] or "(rolled)", r["start"], r["minutes"], r["cap"]))
    lines += ["", "Screen batch: caps $%.2f + judge reserve $%.2f = budget $%.2f" % (p["caps_total"], p["judge_reserve"], p["screen_budget"])]
    for m in p["state_runs"]:
        lines.append("State sweep (%s): seeds %s, cap $%.2f, typical $%.2f" % (m, seeds_for(m, p["seeds"]), p["state_cap"][m], p["state_est"][m]))
    if not p["state_runs"]:
        lines.append("State sweep: none")
    lines.append("Decision parity: %s" % ("yes (first intermediate session; refuses to spend on 0 paired turns)" if p["parity"] else "no"))
    lines.append("Estimated spend: typical $%.2f, worst case (every cap hit) $%.2f" % (p["est_typical"], p["est_max"]))
    return "\n".join(lines)


def state_cmd(mode: str, name: str, seeds: str, budget: float) -> list[str]:
    cmd = [sys.executable, str(TOOLS / "state_agent.py"), "--name", name, "--seeds", seeds]
    if mode == "heuristic":
        if "--strategist" in (TOOLS / "state_agent.py").read_text(encoding="utf-8"):
            return cmd + ["--strategist", "heuristic"]
        return cmd + ["--builtin", "all"]  # the strategist (slice T2) has not landed: the free built-in baseline
    return cmd + ["--tier", "intermediate", "--budget", str(budget)]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gate", required=True)
    ap.add_argument("--profile", choices=sorted(PROFILES), default=DEFAULT_PROFILE, help="wave type (default: milestone)")
    ap.add_argument("--compare", default="", help="previous screen batch, for trends and the changed-screens audit")
    ap.add_argument("--budget", type=float, default=0.0, help="hard cap in dollars for the whole gate (default: the profile's own)")
    ap.add_argument("--state-budget", type=float, default=DEFAULT_STATE_BUDGET)
    ap.add_argument("--seeds", default="", help="state sweep seeds (default: the profile's)")
    ap.add_argument("--state-mode", choices=["heuristic", "llm"], default="llm",
                    help="which strategist the state sweep uses (slice T2 flips the default to heuristic)")
    ap.add_argument("--at", default="route:to_netrun", help="start of the testers who play the changed area: route:NAME | save:SPEC | title")
    ap.add_argument("--build", default="main")
    ap.add_argument("--combat-escalation", action="store_true", help="screen testers escalate combat turn starts (a targeted probe)")
    ap.add_argument("--audit-all", action="store_true", help="audit every distinct screen, not only changed ones")
    ap.add_argument("--skip-screen", action="store_true")
    ap.add_argument("--skip-state", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print the plan and the dollar caps; no API calls, nothing is run")
    a = ap.parse_args()
    plan = make_plan(a.profile, a)
    if a.seeds:
        plan["seeds"] = a.seeds
    if a.dry_run:
        print(print_plan(plan))
        return 0
    if a.budget and a.budget < plan["est_max"]:
        print("gate: --budget $%.2f is below this profile's worst case $%.2f; the batch skips testers whose cap does not fit"
              % (a.budget, plan["est_max"]), file=sys.stderr)
    budget = a.budget or plan["est_max"]
    work = ROOT / ".playtest_sessions" / ("gate_" + a.gate)
    work.mkdir(parents=True, exist_ok=True)
    batch, sa = "PB-" + a.gate, "SA-" + a.gate
    out = ["# Playtest gate %s (%s) — %s" % (a.gate, a.profile, time.strftime("%Y-%m-%d")), "", "```", print_plan(plan), "```", ""]

    # 1. build + routes
    run([sys.executable, str(TOOLS / "roll_testers.py"), "--batch", "_gate_build", "--count", "0", "--build", a.build], work / "build.log")
    routes = sorted({p.stem for p in (TOOLS / "routes").glob("*/*.json")})
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT / ".claude" / "worktrees" / "playtest-build",
                         capture_output=True, text=True).stdout.strip()
    out += ["## 1. Build %s and routes" % sha[:8], ""]
    for r in routes:
        if not (TOOLS / "routes" / sha[:8] / ("%s.json" % r)).exists():
            out.append("- %s: **not recorded for this build** (re-record: `routes.py rec-start --name %s`)" % (r, r))
            continue
        code = run([sys.executable, str(TOOLS / "routes.py"), "test", "--name", r], work / ("route_%s.log" % r), timeout=600)
        out.append("- %s: %s" % (r, "ok" if code == 0 else "**broke** (UI changed; see %s)" % (work / ("route_%s.log" % r)).name))

    # State first (cheap, bounded), so the screen batch gets the rest of the budget.
    llm_spent_cap = 0.0
    ran_state: list[tuple[str, str]] = []
    if not a.skip_state and plan["state_runs"]:
        run([sys.executable, str(TOOLS / "state_agent.py"), "--name", sa + "-base", "--seeds", plan["seeds"], "--builtin", "all"],
            work / "state_base.log")
        for m in plan["state_runs"]:
            name = sa + ("-" + m if len(plan["state_runs"]) > 1 else "")
            run(state_cmd(m, name, seeds_for(m, plan["seeds"]), a.state_budget), work / ("state_%s.log" % m))
            ran_state.append((m, name))
            if m == "llm":
                llm_spent_cap = a.state_budget
    # 2. screen batch
    if not a.skip_screen:
        left = max(0.0, budget - llm_spent_cap)
        cmd = [sys.executable, str(TOOLS / "run_batch.py"), "--batch", batch, "--mix", plan["mix"], "--budget", str(left),
               "--judge-reserve", str(plan["judge_reserve"]),
               "--starts", ",".join("%s=%s" % kv for kv in plan["starts"].items()),
               "--limits", ",".join("%s=%s" % kv for kv in plan["limits"].items())]
        if a.compare:
            cmd += ["--compare", a.compare]
        if a.combat_escalation:
            cmd.append("--combat-escalation")
        if a.audit_all:
            cmd.append("--audit-all")
        run(cmd, work / "screen.log")
        out += ["", "## 2. Screen batch %s" % batch, "", section(DOCS / batch / "_FINDINGS.md", "## 1. Headline", "## 2."), "",
                "Skill (ground truth):", "", section(DOCS / batch / "_BATCH.md", "## Combat skill, ground truth (fights rebuilt from replays)", "## Top"),
                "", "Full findings: `docs/playtest/claude/%s/_FINDINGS.md`" % batch]
        if plan["parity"]:
            sessions = sorted(p for p in (ROOT / ".playtest_sessions" / batch).glob("*/combat_steps.jsonl"))
            if sessions:
                code = run([sys.executable, str(TOOLS / "parity.py"), "--session", str(sessions[0].parent)], work / "parity.log")
                out += ["", "## 2b. Decision parity", "", "%s: exit %d (2 = 0 turns paired, nothing spent); log `%s`" % (
                    sessions[0].parent.name, code, (work / "parity.log").name)]
            else:
                out += ["", "## 2b. Decision parity", "", "no session wrote combat_steps.jsonl; skipped"]
    for m, name in ran_state:
        out += ["", "## 3. State sweep, %s (seeds %s)" % (m, plan["seeds"]), "",
                "Baseline (built-in policy):", "", section(DOCS / "state" / (sa + "-base.md"), "| Seed", "## Reasons"), "",
                "%s:" % m, "", section(DOCS / "state" / (name + ".md"), "| Seed", "## Reasons")]
    gates = DOCS / "gates"
    gates.mkdir(parents=True, exist_ok=True)
    (gates / ("%s.md" % a.gate)).write_text("\n".join(out) + "\n", encoding="utf-8")
    print(gates / ("%s.md" % a.gate))
    return 0


if __name__ == "__main__":
    sys.exit(main())
