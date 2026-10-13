"""Spend testers' time where the feedback is (docs/process/05_CLAUDE_PLAYTESTER.md §10).

Used by harness.py and run_batch.py; also a small CLI for the save library:

    python tools/playtest/streamline.py saves list
    python tools/playtest/streamline.py saves harvest --batch PB-010      # from finished sessions

- Watchdog: notices a tester spending minutes on navigation screens or making no progress, and
  escalates in three levels: a hint, a stronger look, then recovery (restart + Continue, or a route)
  or an early end ("blocked at <screen>"). Also caps the setup phase for testers whose focus is not
  the opening.
- Blockers: a per-batch list of obstacles testers already hit (and how they got past), shown to the
  others so the second tester does not rediscover the first one's dead end.
- Save library: campaign saves collected from testers' private copies at milestones (HQ visits by
  Heat band, raid setup), so a tester whose focus is the late game starts there via Continue, like
  a player handed a save file. Saves are tied to the build they came from.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SESSIONS = ROOT / ".playtest_sessions"
SAVES = ROOT / ".playtest_saves"
SAVE_FILES = ("campaign_1.json", "profile.json")

# Screens that are navigation, not decisions: long stays here are waste unless the focus is the menus.
NAV_KINDS = {"menu", "dialog_or_tutorial_text", "pause_menu", "other"}
# Screens that mean the run is moving.
MILESTONE_KINDS = {"combat_result", "reward_choice", "raid_playout", "map_choice", "summary_or_end"}
COMBAT = {"combat_turn_start", "combat_mid_turn"}
# Focuses whose subject is the opening and the menus: they play every screen, no setup cap.
FULL_FOCUSES = {"onboarding", "ui_flow", "readability_accessibility", "story_world"}
HEAT = re.compile(r"Heat\D{0,4}(\d{1,3})", re.I)


# ---------------------------------------------------------------- watchdog

class Watchdog:
    """Levels: 0 fine, 1 hint, 2 stronger look, 3 recover or end."""

    def __init__(self, nav_limit: float = 5.0, idle_limit: float = 15.0, setup_cap: float | None = 10.0):
        self.nav_limit, self.idle_limit, self.setup_cap = nav_limit, idle_limit, setup_cap
        self.nav_since: float | None = None
        self.nav_kind = ""
        self.last_milestone = 0.0
        self.fought = False
        self.reason = ""

    def observe(self, kind: str, note: str, now: float) -> int:
        if kind in NAV_KINDS:
            if self.nav_since is None:
                self.nav_since, self.nav_kind = now, kind
        else:
            self.nav_since = None
        if kind in MILESTONE_KINDS or note.startswith("FIGHT"):
            self.last_milestone = now
        if kind in COMBAT:
            self.fought = True
            self.last_milestone = max(self.last_milestone, now - self.idle_limit / 2)
        nav = now - self.nav_since if self.nav_since is not None else 0.0
        idle = now - self.last_milestone
        level, self.reason = 0, ""
        for lvl, extra_nav, extra_idle in ((1, 0, 0), (2, 3, 5), (3, 6, 10)):
            if nav >= self.nav_limit + extra_nav:
                level, self.reason = lvl, "%.0f min on %s screens" % (nav, self.nav_kind)
            elif idle >= self.idle_limit + extra_idle:
                level, self.reason = lvl, "no progress (fight, reward, map move) in %.0f min" % idle
        if self.setup_cap is not None and not self.fought and now >= self.setup_cap:
            level, self.reason = 3, "%.0f min without reaching a fight (setup cap)" % now
        return level

    def reset(self, now: float) -> None:
        self.nav_since, self.last_milestone, self.reason = None, now, ""


def hint(level: int, reason: str) -> str:
    if level == 1:
        return ("WATCHDOG: %s. This is not what you are here to test. Note the obstacle ONCE (if you have not), "
                "then take the most direct way forward: the main action button, Continue / Start / Next, Enter, "
                "or Esc to back out and try another path." % reason)
    if level >= 2:
        return ("WATCHDOG (second warning): %s. Stop exploring this screen. Find the single control that moves "
                "the game forward and use it now; if there is none, open the pause menu and go back to the title "
                "or HQ." % reason)
    return ""


# ---------------------------------------------------------------- blockers shared within a batch

class Blockers:
    def __init__(self, batch_dir: Path, handle: str):
        self.file, self.handle = batch_dir / "blockers.jsonl", handle

    def add(self, kind: str, screen: str, what: str, escape: str = "") -> None:
        with open(self.file, "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": time.strftime("%H:%M"), "tester": self.handle, "kind": kind,
                                "screen": screen[:80], "what": what[:240], "escape": escape[:200]}) + "\n")

    def others(self, limit: int = 6) -> str:
        if not self.file.exists():
            return ""
        rows = [json.loads(l) for l in self.file.read_text(encoding="utf-8").splitlines() if l.strip()]
        rows = [r for r in rows if r["tester"] != self.handle][-limit:]
        if not rows:
            return ""
        return ("## Already reported by other testers this batch (do not re-investigate: note \"seen\" in one line "
                "and get past it the quickest way)\n" + "\n".join(
                    "- [%s] %s: %s%s" % (r["kind"], r["screen"], r["what"], (" | got past by: " + r["escape"]) if r["escape"] else "")
                    for r in rows))


# ---------------------------------------------------------------- save library

def heat_of(text: str) -> int | None:
    m = HEAT.search(text or "")
    return int(m.group(1)) if m else None


HOME = re.compile(r"Home\D{0,3}(\d{1,3})\s*/\s*(\d{1,3})", re.I)


CREW_GONE = re.compile(r"crew\D{0,3}0\s*/|total wipe|no crew", re.I)


def healthy(state_text: str) -> bool:
    m = HOME.search(state_text or "")
    if CREW_GONE.search(state_text or ""):
        return False
    return m is None or int(m.group(1)) * 2 >= int(m.group(2))


def harvest(session: Path, build: str, label: str, now_text: str, meta: dict) -> Path | None:
    """Copies the session's current saves into the library under build/label."""
    src = session / "game" / "saves"
    if not (src / SAVE_FILES[0]).exists():
        return None
    heat = heat_of(now_text)
    dest = SAVES / build[:8] / ("%s_%s_%s" % (label, session.name, time.strftime("%H%M%S")))
    dest.mkdir(parents=True, exist_ok=True)
    for f in SAVE_FILES:
        if (src / f).exists():
            shutil.copy2(src / f, dest / f)
    info = {"label": label, "heat": heat, "tester": session.name, "batch": session.parent.name,
            "saved": time.strftime("%Y-%m-%d %H:%M:%S"), "state": now_text[:600]}
    info.update(meta)
    (dest / "meta.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    return dest


def library(build: str) -> list[dict]:
    out = []
    for m in sorted((SAVES / build[:8]).glob("*/meta.json")):
        d = json.loads(m.read_text(encoding="utf-8"))
        d["path"] = str(m.parent)
        out.append(d)
    return out


def pick_save(build: str, spec: str) -> dict | None:
    """spec: a folder name, 'raid_setup', or 'heat>=N' / 'heat<N'. Latest match wins."""
    # A start point should be a campaign a player could still turn around: home at half integrity or more.
    saves = [s for s in library(build) if healthy(s.get("state", ""))]
    if not saves:
        return None
    m = re.match(r"heat(>=|<)(\d+)$", spec)
    if m:
        op, n = m.group(1), int(m.group(2))
        saves = [s for s in saves if s["heat"] is not None and (s["heat"] >= n if op == ">=" else s["heat"] < n)]
        # Prefer saves taken on arrival at HQ (full HP, between runs) over end-of-session ones (often mid-netrun, hurt).
        saves.sort(key=lambda s: (-s["heat"] if op == ">=" else s["heat"], s["label"] == "hq", s["saved"]))
    else:
        saves = [s for s in saves if Path(s["path"]).name == spec or s["label"] == spec]
        saves.sort(key=lambda s: s["saved"])
    return saves[-1] if saves else None


def install_save(save: dict, game_copy: Path) -> None:
    dest = game_copy / "saves"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / ".gdignore").touch()
    for f in SAVE_FILES:
        p = Path(save["path"]) / f
        if p.exists():
            shutil.copy2(p, dest / f)


def harvest_batch(batch: str) -> list[Path]:
    """Seeds the library from finished sessions' last saves (a session that ended mid-campaign)."""
    out = []
    for s in sorted((SESSIONS / batch).iterdir()):
        end, journal = s / "session_end.json", s / "journal.md"
        if not end.exists() or not journal.exists():
            continue
        e = json.loads(end.read_text(encoding="utf-8"))
        if e["outcome"] in ("lost", "won"):
            continue  # an ended campaign is no start point
        text = journal.read_text(encoding="utf-8")
        now = text.split("## NOW", 1)[1].split("## Log", 1)[0].strip() if "## NOW" in text else ""
        p = harvest(s, e["build"], "end", now, {"minutes": e["minutes"]})
        if p:
            out.append(p)
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("saves")
    s.add_argument("what", choices=["list", "harvest"])
    s.add_argument("--batch")
    s.add_argument("--build", default="")
    a = ap.parse_args()
    if a.what == "harvest":
        for p in harvest_batch(a.batch):
            print(p)
        return 0
    builds = [a.build[:8]] if a.build else sorted(p.name for p in SAVES.glob("*") if p.is_dir())
    for b in builds:
        for d in library(b):
            print("%s  %-40s heat=%-4s %s  %s" % (b, Path(d["path"]).name, d["heat"], d["label"], d["state"][:80].replace("\n", " ")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
