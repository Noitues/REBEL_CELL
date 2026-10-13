"""Cheap black-box playtester: a Python loop that plays REBEL_CELL through the Claude API.

    python tools/playtest/harness.py --brief .playtest_sessions/PB-001/<handle>/brief.md --minutes 240
    python tools/playtest/harness.py --brief <...> --minutes 30 --max-usd 3 --actor haiku

Same black box as the `playtester` agent (docs/process/05_CLAUDE_PLAYTESTER.md): the game is
launched quietly through blackbox.py, seen only as screenshots and driven only by mouse and
keyboard messages. What changes is who holds the context. Instead of one long conversation
that re-reads every past screenshot, each step is a fresh, stateless request:

    cached system prompt (rules + persona from the brief)
  + the tester's own notes (NOW block, recent log lines, last actions and whether the screen changed)
  + the current screenshot at 960x540
  -> one JSON decision: a short plan of 1-6 actions, a journal note, optional zoom.

Cost levers: no history, small images, frames are taken only once the screen is still (no
"wait" steps), several actions per decision, and the cheap model (Haiku) acts while the
decision-heavy screens are escalated to Sonnet. Every call's usage is logged to
<session>/usage.jsonl and summed in <session>/cost.json; the report is written at the end by
one text-only Sonnet call from the journal.

API key: ANTHROPIC_API_KEY from the environment or, on Windows, from the user environment in
the registry (set after the shell started). The base URL is pinned to the public API.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blackbox as bb  # noqa: E402
import routes  # noqa: E402
import streamline  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATE = ROOT / "docs" / "process" / "templates" / "CLAUDE_PLAYTEST_FEEDBACK.md"
BUILD = ROOT / ".claude" / "worktrees" / "playtest-build"
SEND_W, SEND_H = 960, 540
SCALE = bb.GAME_W / SEND_W

MODELS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}
ROSTER = ROOT / "tools" / "playtest" / "personas.json"
PLAYBOOK = ROOT / "docs" / "playtest" / "claude" / "playbook.json"
# $ per million tokens: input, output, cache read, cache write (5 min)
PRICES = {
    "claude-haiku-5-5": (0.10, 0.50, 0.01, 0.125),
    "claude-sonnet-5-5": (2.00, 10.00, 0.20, 2.50),
    "claude-opus-5-5": (4.00, 20.00, 0.20, 5.00),
}


def playbook_text(level: str) -> str:
    """The shared playbook as prompt text: 'observed' rules confirmed by 2+ sessions, or 'all'."""
    if level == "none" or not PLAYBOOK.exists():
        return ""
    rules = json.loads(PLAYBOOK.read_text(encoding="utf-8")).get("rules", [])
    if level == "observed":
        rules = [r for r in rules if r["certainty"] == "observed" and r["confirmations"] >= 2]
    rules = [r for r in rules if r["confirmations"] > r["contradictions"]]
    if not rules:
        return ""
    lines = ["- [%s%s] %s" % (r["category"], "" if r["certainty"] == "observed" else ", unconfirmed", r["rule"]) for r in rules]
    return ("\n\n# What you already know from earlier sessions\nYou have played this game before. These are things "
            "you (and other players) learned by playing. They may be outdated on a new build: trust the screen.\n"
            + "\n".join(lines))

ACTION_TYPES = ["click", "right_click", "double_click", "move", "key", "type", "scroll", "wait"]
SCREEN_KINDS = ["menu", "dialog_or_tutorial_text", "combat_turn_start", "combat_mid_turn", "combat_result",
                "reward_choice", "shop", "map_choice", "event_choice", "hq_or_city", "raid_setup",
                "raid_playout", "summary_or_end", "pause_menu", "other"]
# Moments that shape a run: the harness hands them to the stronger model whatever the actor says.
DECISION_KINDS = {"combat_turn_start", "reward_choice", "shop", "map_choice", "event_choice", "raid_setup", "hq_or_city"}
STUCK_STEPS = 6
# Where the two wheels (with their HP and result chips) sit on the 1280x720 screen. The close-up is a
# player leaning in to read small numbers; it carries no game state. Re-measure if the combat layout moves.
WHEEL_REGIONS = {"own": (80, 140, 420, 560), "enemy": (850, 140, 1240, 560)}
COMBAT_KINDS = {"combat_turn_start", "combat_mid_turn"}
MOTION_TEMPLATE = ROOT / "docs" / "process" / "templates" / "CLAUDE_MOTION_FEEDBACK.md"
BURST_FPS = 15
BURST_MAX_S = 5.0
SHEET_FRAMES = 12
MOTION_VERDICTS = ["clear_and_satisfying", "clear_but_flat", "too_slow", "too_fast", "hard_to_follow",
                   "janky_or_glitchy", "flash_or_comfort_risk", "no_animation_seen"]
MOTION_SCHEMA = {
    "type": "object",
    "properties": {
        "moment": {"type": "string", "description": "moment type, e.g. card played, SEND IT resolution, reward reveal, map move"},
        "what_happened": {"type": "string", "description": "what moves, in order, as seen in the frames"},
        "duration_s": {"type": "number", "description": "how long the motion lasted, from the timestamps"},
        "verdict": {"type": "string", "enum": MOTION_VERDICTS},
        "notes": {"type": "string", "description": "why: readability of cause and effect, timing, impact, glitches, flashes"},
    },
    "required": ["moment", "what_happened", "duration_s", "verdict", "notes"],
    "additionalProperties": False,
}
MOTION_RULES = """You are a game feel and animation reviewer. You see a contact sheet: frames captured
from a game window at about 15 frames per second right after the player acted, in time order left to
right, top to bottom, each labelled with its time since the action. The last frame is the settled
screen. Judge the motion as a player would feel it:
- Does the motion show cause and effect (what the action did, to what, by how much)?
- Timing: is it long enough to read and short enough not to drag on the tenth viewing?
- Impact: does a big moment (a hit, a Perfect, a win) feel big?
- Glitches: popping, jumps, overlapping or clipped elements, text flicker, things moving the wrong way.
- Comfort: rapid full-screen flashes (more than ~3 per second) or strobing are a flash risk.
Be concrete and cite frame times. You cannot see smoothness between frames or hear sound; do not judge
those. If nothing moves, say no_animation_seen."""  # same screen, no visible change for this many steps -> the escape hint
DECISION_SCHEMA = {
    "type": "object",
    "properties": {
        "screen": {"type": "string", "description": "short name of the screen you are looking at"},
        "kind": {"type": "string", "enum": SCREEN_KINDS,
                 "description": "what kind of moment this is (decision moments go to the stronger player)"},
        "thought": {"type": "string", "description": "1-3 sentences in your persona's voice: what you see and why you act"},
        "zoom": {
            "type": "object",
            "description": "set w>0 to see a region enlarged before acting (actions are then ignored this step)",
            "properties": {"x": {"type": "integer"}, "y": {"type": "integer"},
                           "w": {"type": "integer"}, "h": {"type": "integer"}},
            "required": ["x", "y", "w", "h"], "additionalProperties": False,
        },
        "actions": {
            "type": "array",
            "description": "1-6 actions run in order; coordinates are pixels of the 960x540 image",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ACTION_TYPES},
                    "x": {"type": "integer"}, "y": {"type": "integer"},
                    "keys": {"type": "string", "description": "for key: e.g. space, esc, enter, q, ctrl+z"},
                    "text": {"type": "string", "description": "for type"},
                    "amount": {"type": "integer", "description": "for scroll: notches, >0 up"},
                    "seconds": {"type": "number", "description": "for wait: 1-10"},
                },
                "required": ["type", "x", "y", "keys", "text", "amount", "seconds"],
                "additionalProperties": False,
            },
        },
        "note": {"type": "string", "description": "journal line for anything worth reporting, or empty"},
        "now": {"type": "string", "description": "rewrite of your NOW block when the state changed, or empty"},
        "watch": {"type": "boolean", "description": "true when these actions should set off an animation worth watching"},
        "escalate": {"type": "boolean", "description": "true to hand this exact screen to a stronger player before acting"},
        "done": {"type": "string", "enum": ["", "won", "lost", "stuck", "time"]},
    },
    "required": ["screen", "kind", "thought", "zoom", "actions", "note", "now", "watch", "escalate", "done"],
    "additionalProperties": False,
}

RULES = """You are a human playtester for a video game. You only see the screen and use the mouse and
keyboard: you know nothing about the game's code or design documents, only what the game has
shown you and what your notes say. Each message gives you your notes and the current screenshot
(960x540; give coordinates in that image). You answer with one JSON decision.

How to play:
- Do what your persona would do. Play to win, at your persona's skill and habits.
- Plan 1-6 actions per decision. Chain actions only when you are sure where each lands (e.g. a
  card, then its target; several clicks in one stable menu). After a click that changes the
  screen, stop the chain: you will see the new screen next.
- Each previous action is reported back with whether the screen changed. If a click changed
  nothing, try a different spot or the keyboard; if that also fails, note it as a possible bug.
- Hover (move) or right-click to read tooltips when your persona would. Use zoom to read small
  numbers or text before acting (it costs one step; do not overuse it).
- Cards cannot be dragged: click the card, then click its target.
- Some dialog buttons (confirm boxes over a blurred screen) may not take your clicks. Use the
  keyboard there: arrow keys or Tab move the highlight, Enter presses it, Esc cancels. That is a
  limit of your controls, not a game bug: do not report it.
- Frames are taken once the screen is still, so you never need to wait for animations, except for
  long automatic playouts (use wait 3-10).
- escalate=true hands this screen to a stronger player who will act instead of you. Escalate on
  decisions that shape the run: planning a combat turn (at its start), card/Firmware/Daemon
  rewards, shop purchases, map path or Site choice, event choices with costs, raid setup, HQ
  spending. Do not escalate for menus, confirmations, Next buttons, or carrying out a plan
  already in your notes.
- Keep playing the campaign to its end screen (won or lost). An operative's death is not the end.

Notes (your memory; you see only these and the screenshot):
- note: never repeat a note you already wrote (see Recent log). One line whenever something is worth reporting later: fight results (turns, HP), offers
  and picks, purchases, Heat changes, raids and outcomes, and every impression, confusion, bug,
  frustration or delight as it happens, in your persona's voice. Empty otherwise.
- now: rewrite your NOW block whenever the campaign state changes (screen, Heat, home server,
  roster, Schematics, run/layer, HP, deck highlights, current plan). Empty keeps the old one.
- watch: true when your actions will set off an animation (a card played, a spin or nudge, SEND IT,
  a reward reveal, a map move, a screen transition, a raid playout); false for plain menu clicks.
- When a fight ends, write the note as: FIGHT won|lost turns=N hp_lost=N perfects=N (your own Perfects
  you saw land), then anything else about the fight.
- kind: label the moment honestly. combat_turn_start = your turn begins and nothing is played yet.
- When you cannot find a way forward: note it as a possible bug with what you tried, then get out
  the way a player would: the pause menu (Esc or the gear icon), back to the title or HQ, Continue,
  and carry on with the campaign. Being stuck on one screen is a finding, not the end of the test.
- done: "won"/"lost" only when the campaign's end screen says so; "stuck" only when even the pause
  menu, the title and Continue cannot get you playing again; "time" after you used the in-game Quit
  when told time is up.
"""


def api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key and os.name == "nt":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                key = winreg.QueryValueEx(k, "ANTHROPIC_API_KEY")[0]
        except OSError:
            key = ""
    if not key:
        sys.exit("harness: no ANTHROPIC_API_KEY in the environment or the user environment")
    return key


# ---------------------------------------------------------------- frames

def _sig(img) -> bytes:
    # 160x90 greyscale, the bottom ticker strip dropped (it scrolls forever)
    small = img.convert("L").resize((160, 90))
    return small.crop((0, 0, 160, 85)).tobytes()


def changed_fraction(a: bytes, b: bytes) -> float:
    return sum(1 for p, q in zip(a, b) if abs(p - q) > 14) / max(1, len(a))


def stable_frame(hwnd: int, timeout: float = 8.0, still: float = 0.012):
    """Polls until two frames 0.35 s apart barely differ (or timeout); returns the last frame."""
    prev = bb.grab(hwnd)
    prev_sig = _sig(prev)
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(0.35)
        cur = bb.grab(hwnd)
        cur_sig = _sig(cur)
        if changed_fraction(prev_sig, cur_sig) < still:
            return cur
        prev, prev_sig = cur, cur_sig
    return prev


def jpeg_b64(img, quality: int = 88) -> str:
    """JPEG for images that only travel in batch requests (a fifth of a PNG; the batch limit is 256 MB)."""
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=quality, optimize=True)
    return base64.standard_b64encode(buf.getvalue()).decode("ascii")


def png_b64(img, size: tuple[int, int] | None = None) -> str:
    if size:
        img = img.resize(size)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.standard_b64encode(buf.getvalue()).decode("ascii")


def burst(hwnd: int) -> list:
    """Frames at ~BURST_FPS from now until the screen has been still for 0.6 s (or BURST_MAX_S)."""
    frames, prev, still_since = [], None, None
    t0 = time.time()
    while True:
        img = bb.grab(hwnd)
        t = time.time() - t0
        frames.append((t, img))
        sig = _sig(img)
        if prev is not None and changed_fraction(prev, sig) < 0.012:
            still_since = t if still_since is None else still_since
            if t - still_since >= 0.6 and t > 0.3:
                break
        else:
            still_since = None
        prev = sig
        if t >= BURST_MAX_S:
            break
        time.sleep(max(0.0, 1.0 / BURST_FPS - (time.time() - t0 - t)))
    return frames


def contact_sheet(frames: list):
    """Up to SHEET_FRAMES frames (first and last kept, the rest evenly spaced), 4 per row, time-labelled."""
    from PIL import Image, ImageDraw

    if len(frames) > SHEET_FRAMES:
        step = (len(frames) - 1) / (SHEET_FRAMES - 1)
        frames = [frames[round(i * step)] for i in range(SHEET_FRAMES)]
    tw, th, cols = 320, 180, 4
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (tw * cols, th * rows), (0, 0, 0))
    d = ImageDraw.Draw(sheet)
    for i, (t, img) in enumerate(frames):
        x, y = (i % cols) * tw, (i // cols) * th
        sheet.paste(img.resize((tw, th)), (x, y))
        d.rectangle([x, y, x + 62, y + 14], fill=(0, 0, 0))
        d.text((x + 3, y + 2), "t=%.2fs" % t, fill=(255, 255, 0))
        d.rectangle([x, y, x + tw - 1, y + th - 1], outline=(80, 80, 80))
    return sheet


# ---------------------------------------------------------------- requests shared with judge_batch.py

def motion_request(meta: dict, sheet_path: Path) -> dict:
    """Messages API params that judge one captured moment (live call or batch request)."""
    from PIL import Image

    sheet = Image.open(sheet_path).convert("RGB")
    content = [{"type": "text", "text": "Moment kind: %s. The player did: %s. Burst: %d frames over %.2f s; "
                                        "the sheet shows %d of them." % (meta["kind"], meta["actions"], meta["frames"],
                                                                        meta["burst_s"], min(meta["frames"], SHEET_FRAMES))},
               {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": jpeg_b64(sheet)}},
               {"type": "text", "text": "Judge this motion."}]
    return dict(model=MODELS["sonnet"], max_tokens=4000,
                system=[{"type": "text", "text": MOTION_RULES, "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": content}],
                output_config={"effort": "low", "format": {"type": "json_schema", "schema": MOTION_SCHEMA}})


def motion_digest(session_dir: Path) -> str:
    f = session_dir / "motion.jsonl"
    if not f.exists():
        return ""
    rows = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    return "\n\n## Motion verdicts (one per captured moment)\n" + "\n".join(
        "- %s %.1fm %s | %s | %.2fs | %s | %s | sheet motion/%s" % (r["kind"], r["t_min"], r["moment"], r["verdict"],
                                                                 r["duration_s"], r["what_happened"], r["notes"], r["sheet"])
        for r in rows)


def report_request(session_dir: Path, extra: str = "") -> dict:
    """Messages API params that write a session's report from its journal (live call or batch request)."""
    end = json.loads((session_dir / "session_end.json").read_text(encoding="utf-8"))
    brief = (session_dir / "brief.md").read_text(encoding="utf-8").split("## Your tools")[0].strip()
    template = (MOTION_TEMPLATE if end.get("motion") else TEMPLATE).read_text(encoding="utf-8")
    prompt = ("You were the playtester described below. Your journal from the session follows. Write your "
              "feedback report by filling the template exactly (all sections, the SUMMARY block keys "
              "unchanged). Opinions in your persona's voice; facts only from the journal; write 'not "
              "encountered' where the journal has nothing. Platform/hardware line stays as the template "
              "says. Output only the markdown report.\n\n# Session facts\n"
              "build: %s\noutcome reason: %s\nwall-clock minutes: %.0f\nsteps: %d\nactions: %d\n\n"
              "# Persona brief\n%s\n\n# Journal\n%s%s%s\n\n# Template\n%s" % (
                  end["build"], end["outcome"], end["minutes"], end["steps"], end["actions"], brief,
                  (session_dir / "journal.md").read_text(encoding="utf-8"), motion_digest(session_dir), extra, template))
    return dict(model=MODELS["sonnet"], max_tokens=16000, output_config={"effort": "medium"},
                messages=[{"role": "user", "content": prompt}])


# ---------------------------------------------------------------- the tester

class Tester:
    def __init__(self, a):
        import anthropic

        self.anthropic = anthropic
        self.client = anthropic.Anthropic(api_key=api_key(), base_url="https://api.anthropic.com", max_retries=5)
        self.brief_path = Path(a.brief).resolve()
        self.dir = self.brief_path.parent
        brief = self.brief_path.read_text(encoding="utf-8")
        m = re.search(r"Report \(the deliverable\): `([^`]+)`", brief)
        self.report = Path(m.group(1)) if m else self.dir / "report.md"
        self.persona = brief.split("## Your tools")[0].strip()
        tiers = json.loads(ROSTER.read_text(encoding="utf-8"))["tiers"]
        m = re.search(r"^Skill tier: (\w+)", brief, re.M)
        self.tier = a.tier or (m.group(1) if m else "intermediate")
        tier = tiers[self.tier]
        coaching = ("\n\n# Coaching\n" + tier["coaching"]) if tier.get("coaching") else ""
        self.closeups = tier.get("wheel_closeup", [])
        self.system = [{"type": "text", "text": RULES + "\n\n# Your brief\n\n" + self.persona + coaching
                        + playbook_text(tier["playbook"]), "cache_control": {"type": "ephemeral"}}]
        self.session = bb.Session(self.dir)
        self.actor = MODELS[a.actor or tier["actor"]]
        self.escalate_to = MODELS[tier["escalate_to"]] if tier["escalate_to"] and not a.actor else (
            MODELS["sonnet"] if a.actor == "haiku" else None)
        self.minutes, self.max_usd, self.max_steps = a.minutes, a.max_usd, a.max_steps
        self.journal = self.dir / "journal.md"
        self.now = "Just started. Nothing known yet."
        self.log: list[str] = []
        self.last_actions: list[str] = []
        self.cost = {"calls": {}, "usd": 0.0, "steps": 0, "actions": 0, "zooms": 0, "escalations": 0}
        self.t0 = time.time()
        self.no_change = 0
        self.end_claimed = ""
        # Streamlining (doc 05 §10): routes, a start save, the watchdog, shared blockers, save harvest.
        self.routes = [r for r in (a.route or "").split(",") if r]
        self.start_save = a.start_save
        self.build = subprocess.run(["git", "rev-parse", "HEAD"], cwd=BUILD, capture_output=True, text=True).stdout.strip()
        focus = re.search(r"^## Your focus: (.+)$", brief, re.M)
        full = any(f.replace("_", " ") in (focus.group(1).lower() if focus else "") for f in ("onboarding", "menus", "readability", "story"))
        cap = None if (a.setup_cap == 0 or (a.setup_cap is None and (full or not self.routes))) else (a.setup_cap or 10.0)
        self.watchdog = streamline.Watchdog(setup_cap=cap)
        self.wd_level = 0
        self.wd_reported = ""
        self.recoveries = 0
        self.blockers = streamline.Blockers(self.dir.parent, self.dir.name)
        self.prev_kind = ""
        self.last_esc_step = -99
        self.raid_saved = False
        # Perfect probe (doc 05 §11): in fights, only screenshot each turn start and press SEND IT, so the
        # k-th screenshot is exactly the replay's turn k (no other combat input is made).
        self.probe_fights = a.probe_perfect
        self.probe_fight = 0
        self.probe_turn = 0
        self.probe_in_fight = False
        self.motion = a.motion
        self.defer = a.defer
        self.motion_left = a.motion_max
        self.motion_seen: dict[str, int] = {}
        if self.motion:
            self.motion_system = [{"type": "text", "text": MOTION_RULES, "cache_control": {"type": "ephemeral"}}]
        if self.journal.exists():  # resume
            text = self.journal.read_text(encoding="utf-8")
            if "## NOW" in text and "## Log" in text:
                self.now = text.split("## NOW", 1)[1].split("## Log", 1)[0].strip()
                self.log = [l for l in text.split("## Log", 1)[1].splitlines() if l.strip()]
        cost_file = self.dir / "cost.json"
        if cost_file.exists():
            self.cost = json.loads(cost_file.read_text())

    # -- bookkeeping
    def elapsed_min(self) -> float:
        return self.cost.get("elapsed_min_before", 0.0) + (time.time() - self.t0) / 60

    def save_journal(self) -> None:
        self.journal.write_text("# Journal\n\n## NOW\n%s\n\n## Log\n%s\n" % (self.now, "\n".join(self.log)),
                                encoding="utf-8")

    def account(self, model: str, usage, kind: str) -> None:
        pin, pout, pcr, pcw = PRICES[model]
        u = {"in": usage.input_tokens or 0, "out": usage.output_tokens or 0,
             "cache_read": getattr(usage, "cache_read_input_tokens", 0) or 0,
             "cache_write": getattr(usage, "cache_creation_input_tokens", 0) or 0}
        usd = (u["in"] * pin + u["out"] * pout + u["cache_read"] * pcr + u["cache_write"] * pcw) / 1e6
        c = self.cost["calls"].setdefault(model, {"n": 0, "in": 0, "out": 0, "cache_read": 0, "cache_write": 0, "usd": 0.0})
        c["n"] += 1
        for k in u:
            c[k] += u[k]
        c["usd"] += usd
        self.cost["usd"] += usd
        with open(self.dir / "usage.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": round(time.time() - self.t0, 1), "model": model, "kind": kind, **u, "usd": round(usd, 6)}) + "\n")
        self.cost["elapsed_min"] = round(self.elapsed_min(), 2)
        (self.dir / "cost.json").write_text(json.dumps(self.cost, indent=1))

    # -- one decision
    def ask(self, model: str, content: list, effort: str, schema: dict | None = None, system=None,
            kind: str = "decide") -> dict | None:
        kwargs = dict(model=model, max_tokens=4000, system=system or self.system,
                      messages=[{"role": "user", "content": content}],
                      output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema or DECISION_SCHEMA}})
        try:
            if model in (MODELS["sonnet"], MODELS["opus"]):
                r = self.client.beta.messages.create(betas=["server-side-fallback-2026-07-01"],
                                                     extra_body={"fallbacks": "default"}, **kwargs)
            else:
                r = self.client.messages.create(**kwargs)
        except self.anthropic.BadRequestError as e:
            print("harness: request rejected: %s" % e, file=sys.stderr)
            raise
        except self.anthropic.APIStatusError as e:
            print("harness: API error %s; retrying the step" % e.status_code, file=sys.stderr)
            time.sleep(5)
            return None
        except self.anthropic.APIConnectionError:
            time.sleep(5)
            return None
        self.account(model, r.usage, kind)
        if r.stop_reason in ("refusal", "max_tokens"):
            print("harness: stop_reason=%s" % r.stop_reason, file=sys.stderr)
            return None
        text = next((b.text for b in r.content if b.type == "text"), "")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def context_text(self, time_up: bool) -> str:
        parts = ["Elapsed %.0f of %d minutes. Step %d." % (self.elapsed_min(), self.minutes, self.cost["steps"] + 1)]
        if self.end_claimed:
            parts.append("You said the campaign is %s. Check the screen: if there is any way to keep playing (Continue, "
                         "back to HQ, another operative, a new netrun), it is NOT over: an operative's death or a lost "
                         "fight is not the end of the campaign. Keep playing. Set done again only if this is the "
                         "campaign's final screen." % self.end_claimed)
        if self.no_change >= STUCK_STEPS:
            parts.append("You have had %d steps in a row with NO visible change. Note it once as a possible bug, then get out through the pause menu (Esc or the gear icon, top right) to the title or HQ and carry on." % self.no_change)
        if self.wd_level:
            parts.append(streamline.hint(self.wd_level, self.watchdog.reason))
        known = self.blockers.others()
        if known:
            parts.append(known)
        if time_up:
            parts.append("TIME IS UP: open the pause menu, use the in-game Quit (it saves), then set done=\"time\".")
        parts.append("## NOW\n" + self.now)
        parts.append("## Recent log\n" + ("\n".join(self.log[-15:]) or "(empty)"))
        parts.append("## Your last actions and what happened\n" + ("\n".join(self.last_actions[-8:]) or "(none yet)"))
        return "\n\n".join(parts)

    # -- actions
    def run_actions(self, hwnd: int, actions: list[dict], before_sig: bytes, watch_kind: str = "") -> list[str]:
        out = []
        for act in actions[:6]:
            t = act["type"]
            x, y = int(act["x"] * SCALE), int(act["y"] * SCALE)
            if t in ("click", "right_click", "double_click"):
                bb.click(hwnd, x, y, right=(t == "right_click"), double=(t == "double_click"))
                desc = "%s %d,%d" % (t, act["x"], act["y"])
            elif t == "move":
                bb.mouse_move(hwnd, x, y)
                desc = "move %d,%d" % (act["x"], act["y"])
            elif t == "key":
                for k in (act["keys"] or "").split():
                    bb.key(hwnd, k)
                desc = "key %s" % act["keys"]
            elif t == "type":
                bb.type_text(hwnd, act["text"])
                desc = "type %r" % act["text"]
            elif t == "scroll":
                bb.scroll(hwnd, x, y, int(act["amount"] or -1))
                desc = "scroll %d at %d,%d" % (act["amount"], act["x"], act["y"])
            else:
                time.sleep(max(0.5, min(10.0, float(act["seconds"] or 2))))
                desc = "wait %.0fs" % (act["seconds"] or 2)
            self.session.log(desc)
            self.cost["actions"] += 1
            out.append(desc)
            if act is not actions[:6][-1] or not watch_kind:
                time.sleep(0.25)
        if watch_kind:
            frames = burst(hwnd)
            frame = frames[-1][1]
            self.critique(frames, watch_kind, " ; ".join(out))
        else:
            frame = stable_frame(hwnd)
        frac = changed_fraction(before_sig, _sig(frame))
        verdict = "screen changed a lot" if frac > 0.25 else "screen changed" if frac > 0.02 else "NO visible change"
        return ["%s -> %s" % (" ; ".join(out), verdict)]

    def step(self, time_up: bool) -> str:
        hwnd = self.session.hwnd()
        frame = stable_frame(hwnd)
        shot = self.session.next_shot(None)
        frame.save(shot)
        content = [{"type": "text", "text": self.context_text(time_up)},
                   {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                                "data": png_b64(frame, (SEND_W, SEND_H))}},
                   {"type": "text", "text": "Current screen (960x540). Decide."}]
        d = self.ask(self.actor, content, "low")
        if d and d["zoom"]["w"] > 0:
            z = d["zoom"]
            box = [int(v * SCALE) for v in (z["x"], z["y"], z["x"] + z["w"], z["y"] + z["h"])]
            box = [max(0, box[0]), max(0, box[1]), min(bb.GAME_W, box[2]), min(bb.GAME_H, box[3])]
            if box[2] - box[0] > 8 and box[3] - box[1] > 8:
                crop = frame.crop(box)
                ratio = min(SEND_W / crop.width, SEND_H / crop.height, 4.0)
                crop = crop.resize((int(crop.width * ratio), int(crop.height * ratio)))
                self.cost["zooms"] += 1
                content = content[:-1] + [
                    {"type": "text", "text": "You asked to zoom on %d,%d %dx%d. Enlarged:" % (z["x"], z["y"], z["w"], z["h"])},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": png_b64(crop)}},
                    {"type": "text", "text": "Decide now (no further zoom this step)."}]
                d = self.ask(self.actor, content, "low")
        if d and self.probe_fights and d["kind"] in COMBAT_KINDS:
            return self.probe_step(hwnd, frame)
        if d and self.probe_fights and self.probe_in_fight and d["kind"] not in COMBAT_KINDS:
            self.probe_in_fight = False
            self.probe_fight += 1
            self.log.append("%5.1fm [system] probe: fight %d done after %d turns" % (self.elapsed_min(), self.probe_fight, self.probe_turn))
            if self.probe_fight >= self.probe_fights:
                return "time"
        stuck = self.no_change >= STUCK_STEPS or self.wd_level >= 2
        steps = self.cost["steps"]
        fresh = d and (d["kind"] == "combat_turn_start" or d["kind"] != self.prev_kind or steps - self.last_esc_step >= 4)
        if d and self.escalate_to and (d["escalate"] or (d["kind"] in DECISION_KINDS and fresh) or stuck):
            self.last_esc_step = steps
            self.cost["escalations"] += 1
            extra = []
            if d["kind"] in COMBAT_KINDS:
                for side in self.closeups:
                    crop = frame.crop(WHEEL_REGIONS[side])
                    crop = crop.resize((crop.width * 3 // 2, crop.height * 3 // 2))
                    extra += [{"type": "text", "text": "Close-up of %s wheel (needle, slices, HP and result chips):"
                                                       % ("your" if side == "own" else "the enemy's")},
                              {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                                           "data": png_b64(crop)}}]
            plan = ""
            if d["kind"] == "combat_turn_start" and self.closeups:
                plan = (" Combat turn start: in `thought`, first write your alignment plan: where your needle points now "
                        "(which slice, centre or edge), the slice you want it on and its value, how many ticks and with "
                        "which cards or nudges, what the result chips say for that setup" + (
                            ", and the same for the enemy needle (push it off centre onto low damage or block)"
                            if "enemy" in self.closeups else "") + ". Then act on that plan.")
            content2 = content[:-1] + extra + [{"type": "text", "text": "Current screen (960x540). You are the stronger "
                                                "player this step: decide fully (escalate is ignored)." + plan}]
            d2 = self.ask(self.escalate_to, content2, "medium")
            d = d2 or d
        self.cost["steps"] += 1
        if not d:
            self.last_actions.append("(no decision this step)")
            return ""
        stamp = "%5.1fm" % self.elapsed_min()
        if d["note"]:
            self.log.append("%s [%s] %s (%s)" % (stamp, d["screen"], d["note"], shot.name))
        if d["now"]:
            self.now = d["now"]
        print("%s %-22s %s" % (stamp, d["screen"][:22], d["thought"][:110]), flush=True)
        self.after_decision(d)
        if d["actions"] and not d["done"]:
            watch_kind = ""
            if self.motion and d["watch"] and self.motion_left > 0:
                sig = "%s/%s" % (d["kind"], d["actions"][-1]["type"])
                if self.motion_seen.get(sig, 0) < 3:
                    self.motion_seen[sig] = self.motion_seen.get(sig, 0) + 1
                    watch_kind = d["kind"]
            result = self.run_actions(hwnd, d["actions"], _sig(frame), watch_kind)
            self.last_actions += result
            self.no_change = self.no_change + 1 if result[0].endswith("NO visible change") else 0
        self.save_journal()
        self.cost["elapsed_min"] = round(self.elapsed_min(), 2)
        (self.dir / "cost.json").write_text(json.dumps(self.cost, indent=1))
        return d["done"]

    def probe_step(self, hwnd: int, frame) -> str:
        self.watchdog.observe("combat_turn_start", "", self.elapsed_min())  # probe turns are fights too
        if not self.probe_in_fight:
            self.probe_in_fight, self.probe_turn = True, 0
        pdir = self.dir / "probe"
        pdir.mkdir(exist_ok=True)
        frame.save(pdir / ("f%02d_t%02d.png" % (self.probe_fight, self.probe_turn)))
        with open(pdir / "probe.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({"fight": self.probe_fight, "turn": self.probe_turn,
                                "shot": "f%02d_t%02d.png" % (self.probe_fight, self.probe_turn), "t": round(self.elapsed_min(), 2)}) + "\n")
        self.probe_turn += 1
        before = _sig(frame)
        bb.key(hwnd, "space")
        self.session.log("key space (probe)")
        self.cost["steps"] += 1
        after = stable_frame(hwnd)
        if changed_fraction(before, _sig(after)) < 0.02:  # SEND IT did not take: try the button
            bb.click(hwnd, 1145, 625, right=False, double=False)
            self.session.log("click 1145,625 (probe SEND IT)")
            stable_frame(hwnd)
        self.save_journal()
        return ""

    def after_decision(self, d: dict) -> None:
        now = self.elapsed_min()
        level = self.watchdog.observe(d["kind"], d["note"], now)
        if level and self.watchdog.reason != self.wd_reported:
            self.wd_reported = self.watchdog.reason
            last = next((l for l in reversed(self.log) if "[system]" not in l), "")
            self.blockers.add(d["kind"], d["screen"], "%s; last note: %s" % (self.watchdog.reason, last[-160:]))
            self.log.append("%5.1fm [system] watchdog level %d: %s" % (now, level, self.watchdog.reason))
        if not level and self.wd_level >= 1 and self.wd_reported:
            self.blockers.add(self.prev_kind, d["screen"], "got past: " + self.wd_reported, "; ".join(self.last_actions[-2:])[:200])
            self.wd_reported = ""
        self.wd_level = level
        # Save library: an HQ arrival (by Heat) and the first raid setup are good start points for others.
        if d["kind"] == "hq_or_city" and self.prev_kind != "hq_or_city":
            streamline.harvest(self.dir, self.build, "hq", self.now, {"minutes": round(now, 1)})
        if d["kind"] == "raid_setup" and not self.raid_saved:
            self.raid_saved = bool(streamline.harvest(self.dir, self.build, "raid_setup", self.now, {"minutes": round(now, 1)}))
        self.prev_kind = d["kind"]

    def recover(self) -> bool:
        """Watchdog level 3: restart the game and Continue (or replay the start route) once; else give up."""
        self.recoveries += 1
        self.log.append("%5.1fm [system] watchdog: %s; recovering (%d)" % (self.elapsed_min(), self.watchdog.reason, self.recoveries))
        if self.recoveries > 2:
            return False
        subprocess.run([sys.executable, str(Path(bb.__file__)), "--session", str(self.dir), "stop"], capture_output=True)
        self.session.state["launcher_pid"] = 0
        self.ensure_game()
        has_save = (self.dir / "game" / "saves" / streamline.SAVE_FILES[0]).exists()
        plan = ["continue"] if has_save else self.routes[:1]
        for name in plan:
            ok, where = routes.play(self.session.hwnd, name, self.build, log=lambda m: None)
            self.log.append("%5.1fm [system] recovery route %s: %s" % (self.elapsed_min(), name, "ok" if ok else "broke at " + where))
            if not ok:
                return False
        self.watchdog.reset(self.elapsed_min())
        self.wd_level, self.no_change = 0, 0
        return bool(plan)

    def start(self) -> None:
        """First launch: install the start save, start the game, run the start routes."""
        fresh = self.cost["steps"] == 0 and not (self.dir / "game" / "saves" / streamline.SAVE_FILES[0]).exists()
        if self.start_save and fresh:
            save = streamline.pick_save(self.build, self.start_save)
            if save:
                bb.private_copy(BUILD, self.dir / "game")
                streamline.install_save(save, self.dir / "game")
                self.log.append("0.0m [system] started from a saved campaign (%s, Heat %s): you have played up to here "
                                "before; press on from where it is." % (Path(save["path"]).name, save["heat"]))
                self.now = "Resuming a campaign you were playing: " + save.get("state", "")[:400]
                self.routes = ["continue"]
            else:
                self.log.append("0.0m [system] no library save matches %r; starting fresh" % self.start_save)
        self.ensure_game()
        if not fresh:
            return
        for name in self.routes:
            ok, where = routes.play(self.session.hwnd, name, self.build, log=lambda m: None)
            r = routes.load(name, self.build) or {}
            if ok:
                self.log.append("%5.1fm [system] autopilot: %s -> %s. You have done this part before; it was skipped "
                                "to save time. Carry on from here." % (self.elapsed_min(), name, r.get("end", "")))
            else:
                self.log.append("%5.1fm [system] autopilot route %s broke (%s): play on from this screen yourself."
                                % (self.elapsed_min(), name, where))
                break
        self.save_journal()

    # -- motion
    def critique(self, frames: list, kind: str, actions: str) -> None:
        self.motion_left -= 1
        mdir = self.dir / "motion"
        mdir.mkdir(exist_ok=True)
        n = len(list(mdir.glob("*.png"))) + 1
        sheet_path = mdir / ("%04d_%s.png" % (n, kind))
        sheet = contact_sheet(frames)
        sheet.save(sheet_path)
        meta = {"sheet": sheet_path.name, "kind": kind, "actions": actions, "frames": len(frames),
                "burst_s": round(frames[-1][0], 2), "t_min": round(self.elapsed_min(), 1)}
        if self.defer:  # judged later in a batch (judge_batch.py), at half price
            with open(mdir / "pending.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(meta) + "\n")
            return
        params = motion_request(meta, sheet_path)
        m = self.ask(params["model"], params["messages"][0]["content"], "low", MOTION_SCHEMA, params["system"], "motion")
        if not m:
            return
        m.update(meta)
        with open(self.dir / "motion.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(m) + "\n")
        self.log.append("%5.1fm [MOTION %s] %s: %s (%s)" % (self.elapsed_min(), m["verdict"], m["moment"],
                                                            m["notes"][:200], sheet_path.name))

    # -- the session
    def ensure_game(self) -> None:
        st = self.session.state
        if st.get("launcher_pid") and bb._alive(st["launcher_pid"]):
            return
        if st.get("launcher_pid"):
            self.log.append("%5.1fm [system] the game was not running; restarted it (crash or closed?)" % self.elapsed_min())
        r = subprocess.run([sys.executable, str(Path(bb.__file__)), "--session", str(self.dir), "--settle", "4",
                            "start", "--private-copy", "--project", str(BUILD)], capture_output=True, text=True)
        if r.returncode:
            sys.exit("harness: could not start the game: %s" % (r.stderr or r.stdout).strip())
        self.session = bb.Session(self.dir)

    def play(self) -> str:
        self.start()
        outcome, grace = "", 0
        while True:
            time_up = self.elapsed_min() >= self.minutes or self.cost["usd"] >= self.max_usd
            if time_up:
                grace += 1
                if grace > 15:
                    return "time"
            if self.cost["steps"] >= self.max_steps:
                return "time"
            try:
                done = self.step(time_up)
            except SystemExit as e:  # game window gone
                print("harness: %s" % e, file=sys.stderr)
                self.ensure_game()
                continue
            if self.wd_level >= 3 and not done:
                if not self.recover():
                    self.blockers.add(self.prev_kind, "", "ended the session: " + self.watchdog.reason)
                    return "blocked: " + self.watchdog.reason
                continue
            if done == "time" and not time_up:
                self.log.append("%5.1fm [system] ignored done=time before the time box" % self.elapsed_min())
                continue
            if done in ("won", "lost") and not self.end_claimed:
                # An operative's death or one fight is not the campaign's end: make the tester look again.
                self.end_claimed = done
                continue
            if done:
                return done
            self.end_claimed = ""

    def write_end(self, outcome: str) -> None:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=BUILD, capture_output=True, text=True).stdout.strip()
        (self.dir / "session_end.json").write_text(json.dumps({
            "outcome": outcome, "build": sha, "minutes": round(self.elapsed_min(), 1), "steps": self.cost["steps"],
            "actions": self.cost["actions"], "motion": self.motion, "report": self.report.as_posix()}, indent=1))

    def write_report(self, outcome: str) -> None:
        with self.client.messages.stream(**report_request(self.dir)) as s:
            r = s.get_final_message()
        self.account(MODELS["sonnet"], r.usage, "report")
        text = next((b.text for b in r.content if b.type == "text"), "")
        self.report.parent.mkdir(parents=True, exist_ok=True)
        self.report.write_text(text, encoding="utf-8")
        print("report:", self.report.as_posix())


def main() -> int:
    # Output goes to log files; the Windows console code page cannot encode every character a model writes.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--brief", required=True)
    ap.add_argument("--minutes", type=float, default=240)
    ap.add_argument("--max-usd", type=float, default=15.0, help="stop (in-game Quit) when the session costs this much")
    ap.add_argument("--max-steps", type=int, default=5000)
    ap.add_argument("--tier", choices=["novice", "intermediate", "expert"],
                    help="skill tier (default: the brief's 'Skill tier:' line)")
    ap.add_argument("--actor", choices=["haiku", "sonnet"], help="override the tier's actor model (escalation to Sonnet when haiku)")
    ap.add_argument("--no-report", action="store_true")
    ap.add_argument("--probe-perfect", type=int, default=0,
                    help="Perfect probe: in N fights only screenshot each turn start and send (pairs with replay_audit)")
    ap.add_argument("--route", default="", help="comma-separated routes (routes.py) to play at the start, e.g. to_netrun")
    ap.add_argument("--start-save", default="", help="start from a library save (streamline.py): a name, raid_setup, heat>=N")
    ap.add_argument("--setup-cap", type=float, default=None,
                    help="minutes allowed before the first fight (default 10 with a route, off for opening focuses; 0 = off)")
    ap.add_argument("--motion", action="store_true",
                    help="motion tester: capture a frame burst after actions that should animate and have Sonnet judge it")
    ap.add_argument("--motion-max", type=int, default=40, help="most motion verdicts per session")
    ap.add_argument("--defer", action="store_true",
                    help="play only: queue motion sheets and leave the report to tools/playtest/judge_batch.py (Batch API, half price)")
    a = ap.parse_args()
    t = Tester(a)
    t.cost["elapsed_min_before"] = t.cost.get("elapsed_min", 0.0)
    outcome = t.play()
    t.save_journal()
    t.write_end(outcome)
    if not a.no_report and not a.defer:
        t.write_report(outcome)
    subprocess.run([sys.executable, str(Path(bb.__file__)), "--session", str(t.dir), "stop"], capture_output=True)
    c = t.cost
    print("outcome=%s steps=%d actions=%d escalations=%d zooms=%d usd=%.3f minutes=%.1f" % (
        outcome, c["steps"], c["actions"], c["escalations"], c["zooms"], c["usd"], t.elapsed_min()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
