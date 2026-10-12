"""Judge played sessions in the Message Batches API at half price (docs/process/05_CLAUDE_PLAYTESTER.md §7).

    python tools/playtest/judge_batch.py run --batch PB-004                 # everything below, waits for both stages
    python tools/playtest/judge_batch.py run --batch PB-004 --audit-model opus --audit-max 30
    python tools/playtest/judge_batch.py status --batch PB-004

Testers play live with `harness.py --defer`: the play loop needs answers in seconds, but nothing
the play depends on is judged during play. Afterwards this runs, per batch of sessions:

Stage A (one batch):
  - motion critiques for every contact sheet a --motion tester queued (motion/pending.jsonl)
  - a screen audit of the distinct screens each tester saw (shots/, near-duplicates dropped):
    clipped or overlapping text, placeholder strings, contrast, colour-only information, and
    "would a newcomer know what to do here?"
  - lessons: what each tester learned about playing, from its journal only (never code or docs)
Stage B (one batch, after A):
  - each tester's report, from its journal + motion judgements + audit findings
  - the playbook merge: every session's lessons into docs/playtest/claude/playbook.json, the
    shared, black-box knowledge that experienced testers start from (each rule with how many
    sessions confirmed it and which contradicted it)

Outputs per session: motion.jsonl, audit.jsonl + audit.md, lessons.json, the report. Batch
state and usage: .playtest_sessions/<batch>/judge/. Costs are priced at the batch rate (50 %).
API key and base URL handling as in harness.py (the user environment; the public API URL).

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as hz  # noqa: E402

ROOT = hz.ROOT
SESSIONS = ROOT / ".playtest_sessions"
PLAYBOOK = ROOT / "docs" / "playtest" / "claude" / "playbook.json"
REPORTS = ROOT / "docs" / "playtest" / "claude"
FINDINGS_TEMPLATE = ROOT / "docs" / "process" / "templates" / "PLAYTEST_FINDINGS.md"
SYNTH_RULES = """You turn a batch of game playtest reports into one findings document for the development
team, by filling the template exactly. Rules:
- Deduplicate across testers: one finding per underlying problem, listing every tester who hit it.
- Every finding cites evidence that exists in the inputs (tester handle + report section, shot file,
  or contact sheet). Never invent a finding, a number or a repro step.
- A click, drag or key press that "did nothing" is confidence unconfirmed-input unless another
  tester got past the same control: the testers' input is simulated and some controls ignore it.
- Screen-audit items count only when they are blocker/major or a tester also tripped on them;
  merge repeats of the same issue on near-identical screens.
- Balance and design opinions go to section 4 as questions with options for the designer; never
  propose numbers as decisions.
- Areas: combat (wheel fights, cards, hand), city (City Grid, raids, map), screens (title, HQ,
  menus, rewards, shops, dialogs, settings), rules (outcomes that contradict what the game told
  the player).
- Rank by how many testers it affected, then severity. Keep it tight: the team reads this first.
Output only the markdown document."""
AUDIT_MODELS = {"sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}
BATCH_DISCOUNT = 0.5
OPUS_PRICE = (4.00, 20.00, 0.40, 5.00)  # in, out, cache read, cache write
DISTINCT = 0.30  # a shot is a new screen when it differs this much from every kept one

AUDIT_KINDS = ["clipped_text", "overlap", "placeholder_text", "low_contrast", "colour_only", "unclear_next_step",
               "inconsistent_term", "visual_glitch", "other"]
AUDIT_SCHEMA = {
    "type": "object",
    "properties": {
        "screen": {"type": "string"},
        "clarity": {"type": "integer", "description": "1 = baffling, 5 = obvious what this is and what to do"},
        "newcomer_next_step": {"type": "string", "description": "what a first-time player would try next here"},
        "issues": {"type": "array", "items": {
            "type": "object",
            "properties": {"type": {"type": "string", "enum": AUDIT_KINDS},
                           "where": {"type": "string"}, "detail": {"type": "string"},
                           "severity": {"type": "string", "enum": ["blocker", "major", "minor", "polish"]}},
            "required": ["type", "where", "detail", "severity"], "additionalProperties": False}},
    },
    "required": ["screen", "clarity", "newcomer_next_step", "issues"],
    "additionalProperties": False,
}
AUDIT_RULES = """You review one screenshot of a video game (1280x720) for a playtest. You know only what the
screen shows. Report concrete, visible problems: text cut off or overlapping, placeholder or
programmer strings (KEY_..., TODO, raw ids), text hard to read against its background, information
shown by colour alone, visual glitches, terms that look inconsistent, and whether a first-time
player could tell what this screen is and what to do next. Do not report taste, and do not report a
deliberate stylistic effect (glitch styling, stickers, handwriting) as a glitch unless it hurts reading.
Severity: blocker = a player cannot proceed or read something essential; major = likely to mislead or
confuse; minor = noticeable; polish = nice to fix. Name where on the screen each issue is. An empty
issues list is a fine answer."""

LESSON_CATS = ["controls", "combat", "cards_and_pickups", "map_and_nodes", "economy", "heat", "raids",
               "hq_and_campaign", "ui", "other"]
LESSONS_SCHEMA = {
    "type": "object",
    "properties": {"lessons": {"type": "array", "items": {
        "type": "object",
        "properties": {"rule": {"type": "string", "description": "practical advice for a player, one sentence"},
                       "category": {"type": "string", "enum": LESSON_CATS},
                       "certainty": {"type": "string", "enum": ["observed", "inferred"]},
                       "evidence": {"type": "string", "description": "what in the journal shows it"}},
        "required": ["rule", "category", "certainty", "evidence"], "additionalProperties": False}}},
    "required": ["lessons"], "additionalProperties": False,
}
LESSONS_RULES = """From a playtester's journal, extract what the tester learned about how to play this game:
controls that work (and ones that do not), how combat resolves, what cards and pickups do, how the
map, economy, Heat, raids and the campaign behave, and tactics that worked or failed. Only what the
journal shows the tester saw on screen; mark a rule "inferred" when the tester guessed. No advice
about the tester's own persona. Skip bugs (they go to the report). At most 25 lessons, the most useful first."""

PLAYBOOK_SCHEMA = {
    "type": "object",
    "properties": {"rules": {"type": "array", "items": {
        "type": "object",
        "properties": {"id": {"type": "string"}, "rule": {"type": "string"},
                       "category": {"type": "string", "enum": LESSON_CATS},
                       "certainty": {"type": "string", "enum": ["observed", "inferred"]},
                       "confirmations": {"type": "integer"}, "contradictions": {"type": "integer"},
                       "builds": {"type": "array", "items": {"type": "string"}}},
        "required": ["id", "rule", "category", "certainty", "confirmations", "contradictions", "builds"],
        "additionalProperties": False}}},
    "required": ["rules"], "additionalProperties": False,
}
PLAYBOOK_RULES = """You maintain a shared playbook for game playtesters: practical rules learned by playing,
never from the game's code. Merge the new sessions' lessons into the existing playbook: merge
duplicates (confirmations += number of sessions that state it), count contradictions, raise
"inferred" to "observed" when a session observed it, keep the build ids each rule was seen on, and
drop a rule only when contradictions clearly outweigh confirmations. Keep ids stable (new ids:
category-short-slug). At most 150 rules, most useful first within each category."""


def client():
    import anthropic

    return anthropic.Anthropic(api_key=hz.api_key(), base_url="https://api.anthropic.com", max_retries=5)


def sessions_of(batch: str) -> list[Path]:
    return sorted(p for p in (SESSIONS / batch).iterdir() if (p / "session_end.json").exists())


def distinct_shots(session: Path, cap: int) -> list[Path]:
    from PIL import Image

    kept: list[tuple[Path, bytes]] = []
    for shot in sorted((session / "shots").glob("*.png")):
        if shot.stem.endswith("_start"):  # the engine splash at launch
            continue
        try:
            sig = hz._sig(Image.open(shot).convert("RGB"))
        except OSError:
            continue
        if all(hz.changed_fraction(sig, k) > DISTINCT for _, k in kept):
            kept.append((shot, sig))
    paths = [p for p, _ in kept]
    if len(paths) > cap:
        step = (len(paths) - 1) / (cap - 1)
        paths = [paths[round(i * step)] for i in range(cap)]
    return paths


def journal_text(session: Path) -> str:
    return (session / "journal.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------- stage builders

def stage_a(batch: str, audit_model: str, audit_max: int) -> tuple[list[dict], dict]:
    from PIL import Image

    reqs, index = [], {}
    for s in sessions_of(batch):
        h = s.name
        pending = s / "motion" / "pending.jsonl"
        if pending.exists():
            for line in pending.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                meta = json.loads(line)
                cid = "m-%s-%s" % (h, meta["sheet"].split("_")[0])
                reqs.append({"custom_id": cid, "params": hz.motion_request(meta, s / "motion" / meta["sheet"])})
                index[cid] = {"session": str(s), "kind": "motion", "meta": meta}
        if audit_max > 0:
            for shot in distinct_shots(s, audit_max):
                cid = "a-%s-%s" % (h, shot.stem.split("_")[0])
                img = Image.open(shot).convert("RGB")
                reqs.append({"custom_id": cid, "params": dict(
                    model=AUDIT_MODELS[audit_model], max_tokens=4000,
                    system=[{"type": "text", "text": AUDIT_RULES, "cache_control": {"type": "ephemeral"}}],
                    messages=[{"role": "user", "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": hz.png_b64(img)}},
                        {"type": "text", "text": "Audit this screen."}]}],
                    output_config={"effort": "low", "format": {"type": "json_schema", "schema": AUDIT_SCHEMA}})})
                index[cid] = {"session": str(s), "kind": "audit", "shot": shot.name}
        cid = "l-%s" % h
        reqs.append({"custom_id": cid, "params": dict(
            model=hz.MODELS["sonnet"], max_tokens=8000,
            system=[{"type": "text", "text": LESSONS_RULES}],
            messages=[{"role": "user", "content": "Journal:\n\n" + journal_text(s)}],
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": LESSONS_SCHEMA}})})
        index[cid] = {"session": str(s), "kind": "lessons"}
    return reqs, index


def audit_digest(session: Path) -> str:
    f = session / "audit.jsonl"
    if not f.exists():
        return ""
    rows = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    lines = []
    for r in rows:
        for i in r["issues"]:
            lines.append("- %s (%s, clarity %d): %s %s at %s: %s" % (r["shot"], r["screen"], r["clarity"], i["severity"],
                                                                    i["type"], i["where"], i["detail"]))
    return ("\n\n## Screen audit after the session (a reviewer looked at each distinct screen you saw; use these as "
            "bugs/clarity findings with their shot names)\n" + ("\n".join(lines) or "- no issues found"))


def stage_b(batch: str) -> tuple[list[dict], dict]:
    reqs, index = [], {}
    lessons = {}
    for s in sessions_of(batch):
        cid = "r-%s" % s.name
        reqs.append({"custom_id": cid, "params": hz.report_request(s, audit_digest(s))})
        index[cid] = {"session": str(s), "kind": "report"}
        lf = s / "lessons.json"
        if lf.exists():
            end = json.loads((s / "session_end.json").read_text(encoding="utf-8"))
            lessons[s.name] = {"build": end["build"][:8], "lessons": json.loads(lf.read_text(encoding="utf-8"))["lessons"]}
    if lessons:
        current = PLAYBOOK.read_text(encoding="utf-8") if PLAYBOOK.exists() else '{"rules": []}'
        reqs.append({"custom_id": "p-merge", "params": dict(
            model=hz.MODELS["sonnet"], max_tokens=32000,
            system=[{"type": "text", "text": PLAYBOOK_RULES}],
            messages=[{"role": "user", "content": "Existing playbook:\n%s\n\nNew sessions' lessons:\n%s" % (
                current, json.dumps(lessons, indent=1))}],
            output_config={"effort": "medium", "format": {"type": "json_schema", "schema": PLAYBOOK_SCHEMA}})})
        index["p-merge"] = {"session": "", "kind": "playbook"}
    return reqs, index


def stage_c(batch: str, compare: str) -> tuple[list[dict], dict]:
    """One Opus request: the batch's reports, audits and motion problems into _FINDINGS.md."""
    folder = REPORTS / batch
    parts = []
    bp = folder / "_BATCH.md"
    if bp.exists():
        parts.append("# Batch statistics\n" + bp.read_text(encoding="utf-8"))
    mf = SESSIONS / batch / "batch.json"
    if mf.exists():
        m = json.loads(mf.read_text(encoding="utf-8"))
        parts.append("# Testers\n" + "\n".join("- %s: tier %s, persona %s, focus %s" % (
            t["handle"], t.get("tier", "?"), t["persona"], t["focus"]) for t in m["testers"]))
    for rp in sorted(p for p in folder.glob("*.md") if not p.name.startswith("_")):
        parts.append("# Report: %s\n%s" % (rp.stem, rp.read_text(encoding="utf-8")))
    for sdir in sessions_of(batch):
        af = sdir / "audit.jsonl"
        if af.exists():
            rows = [json.loads(l) for l in af.read_text(encoding="utf-8").splitlines() if l.strip()]
            hits = ["- %s %s (%s) %s at %s: %s" % (r["shot"], i["severity"], r["screen"][:50], i["type"], i["where"], i["detail"])
                    for r in rows for i in r["issues"] if i["severity"] in ("blocker", "major")]
            if hits:
                parts.append("# Screen audit, blocker/major only: %s\n%s" % (sdir.name, "\n".join(hits)))
        mj = sdir / "motion.jsonl"
        if mj.exists():
            rows = [json.loads(l) for l in mj.read_text(encoding="utf-8").splitlines() if l.strip()]
            bad = ["- motion/%s %s %s (%.2fs): %s" % (r["sheet"], r["verdict"], r["moment"], r["duration_s"], r["notes"])
                   for r in rows if r["verdict"] not in ("clear_and_satisfying", "clear_but_flat")]
            if bad:
                parts.append("# Motion problems: %s\n%s" % (sdir.name, "\n".join(bad)))
    if compare:
        prev = REPORTS / compare / "_FINDINGS.md"
        if prev.exists():
            parts.append("# Previous batch findings (%s), for the trend column and to mark fixed or recurring items\n%s"
                         % (compare, prev.read_text(encoding="utf-8")))
    prompt = "\n\n".join(parts) + "\n\n# Template\n" + FINDINGS_TEMPLATE.read_text(encoding="utf-8")
    req = {"custom_id": "s-findings", "params": dict(
        model=AUDIT_MODELS["opus"], max_tokens=32000, system=[{"type": "text", "text": SYNTH_RULES}],
        messages=[{"role": "user", "content": prompt}], output_config={"effort": "medium"})}
    return [req], {"s-findings": {"session": "", "kind": "findings", "batch": batch}}


# ---------------------------------------------------------------- batch plumbing

def submit_and_wait(c, reqs: list[dict], work: Path, name: str, poll: int) -> list[dict]:
    work.mkdir(parents=True, exist_ok=True)
    state_f = work / ("%s.json" % name)
    state = json.loads(state_f.read_text()) if state_f.exists() else {}
    if not state.get("id"):
        b = c.messages.batches.create(requests=reqs)
        state = {"id": b.id, "n": len(reqs), "submitted": time.strftime("%Y-%m-%d %H:%M:%S")}
        state_f.write_text(json.dumps(state, indent=1))
        print("%s: submitted %s (%d requests)" % (name, b.id, len(reqs)), flush=True)
    while True:
        b = c.messages.batches.retrieve(state["id"])
        if b.processing_status == "ended":
            break
        time.sleep(poll)
    out = []
    for r in c.messages.batches.results(state["id"]):
        out.append(r.model_dump() if hasattr(r, "model_dump") else dict(r))
    (work / ("%s.results.jsonl" % name)).write_text("\n".join(json.dumps(r) for r in out), encoding="utf-8")
    state["ended"] = time.strftime("%Y-%m-%d %H:%M:%S")
    state_f.write_text(json.dumps(state, indent=1))
    return out


def price(model: str, usage: dict) -> float:
    pin, pout, pcr, pcw = hz.PRICES.get(model, OPUS_PRICE)
    return BATCH_DISCOUNT * ((usage.get("input_tokens") or 0) * pin + (usage.get("output_tokens") or 0) * pout
                             + (usage.get("cache_read_input_tokens") or 0) * pcr
                             + (usage.get("cache_creation_input_tokens") or 0) * pcw) / 1e6


def ingest(results: list[dict], index: dict, cost: dict) -> None:
    for r in results:
        cid = r["custom_id"]
        res = r["result"]
        meta = index.get(cid)
        if not meta:
            continue
        if res["type"] != "succeeded":
            print("judge: %s %s" % (cid, res["type"]), file=sys.stderr)
            cost["failed"] = cost.get("failed", 0) + 1
            continue
        msg = res["message"]
        usd = price(msg["model"], msg.get("usage") or {})
        k = cost.setdefault(meta["kind"], {"n": 0, "usd": 0.0})
        k["n"] += 1
        k["usd"] += usd
        cost["usd"] = cost.get("usd", 0.0) + usd
        text = next((b["text"] for b in msg["content"] if b.get("type") == "text"), "")
        s = Path(meta["session"]) if meta["session"] else None
        if meta["kind"] == "findings":
            out = REPORTS / meta["batch"] / "_FINDINGS.md"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
            continue
        if meta["kind"] == "report":
            end = json.loads((s / "session_end.json").read_text(encoding="utf-8"))
            out = Path(end["report"])
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
            continue
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            cost["failed"] = cost.get("failed", 0) + 1
            continue
        if meta["kind"] == "motion":
            data.update(meta["meta"])
            with open(s / "motion.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(data) + "\n")
        elif meta["kind"] == "audit":
            data["shot"] = meta["shot"]
            with open(s / "audit.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(data) + "\n")
        elif meta["kind"] == "lessons":
            (s / "lessons.json").write_text(json.dumps(data, indent=1), encoding="utf-8")
        elif meta["kind"] == "findings":
            (REPORTS / meta["batch"] / "_FINDINGS.md").write_text(text, encoding="utf-8")
        elif meta["kind"] == "playbook":
            PLAYBOOK.parent.mkdir(parents=True, exist_ok=True)
            PLAYBOOK.write_text(json.dumps(data, indent=1), encoding="utf-8")


def write_audit_md(session: Path) -> None:
    f = session / "audit.jsonl"
    if not f.exists():
        return
    rows = sorted((json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()), key=lambda r: r["shot"])
    rank = {"blocker": 0, "major": 1, "minor": 2, "polish": 3}
    issues = sorted(((rank.get(i["severity"], 4), r, i) for r in rows for i in r["issues"]),
                    key=lambda x: (x[0], x[1]["shot"]))
    lines = ["# Screen audit — %s" % session.name, "",
             "%d distinct screens, %d issues (%d blocker/major). Blocker and major first; polish last." % (
                 len(rows), len(issues), sum(1 for x in issues if x[0] <= 1)), "",
             "| Severity | Shot | Screen | Clarity | Issue | Where | Detail |", "|---|---|---|---|---|---|---|"]
    for _, r, i in issues:
        lines.append("| %s | shots/%s | %s | %d | %s | %s | %s |" % (i["severity"], r["shot"], r["screen"][:60], r["clarity"],
                                                                    i["type"], i["where"], i["detail"].replace("|", "/")))
    lines += ["", "## What a newcomer would try next", ""] + ["- %s (%s): %s" % (r["shot"], r["screen"], r["newcomer_next_step"]) for r in rows]
    (session / "audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["run", "status"])
    ap.add_argument("--batch", required=True)
    ap.add_argument("--audit-model", choices=sorted(AUDIT_MODELS), default="sonnet")
    ap.add_argument("--audit-max", type=int, default=40, help="most distinct screens audited per session (0 = no audit)")
    ap.add_argument("--poll", type=int, default=60, help="seconds between status polls")
    ap.add_argument("--compare", default="", help="previous batch id, for trends in the findings")
    ap.add_argument("--no-synthesis", action="store_true", help="skip stage C (_FINDINGS.md)")
    a = ap.parse_args()
    work = SESSIONS / a.batch / "judge"
    c = client()
    if a.cmd == "status":
        for f in sorted(work.glob("stage_*.json")):
            st = json.loads(f.read_text())
            b = c.messages.batches.retrieve(st["id"])
            print("%s %s %s %s" % (f.stem, st["id"], b.processing_status, b.request_counts))
        return 0
    cost_f = work / "cost.json"
    cost = json.loads(cost_f.read_text()) if cost_f.exists() else {}
    if not (work / "stage_a.results.jsonl").exists():
        reqs, index = stage_a(a.batch, a.audit_model, a.audit_max)
        work.mkdir(parents=True, exist_ok=True)
        (work / "stage_a.index.json").write_text(json.dumps(index))
        res = submit_and_wait(c, reqs, work, "stage_a", a.poll)
        ingest(res, index, cost)
        for s in sessions_of(a.batch):
            write_audit_md(s)
        cost_f.write_text(json.dumps(cost, indent=1))
    if not (work / "stage_b.results.jsonl").exists():
        reqs, index = stage_b(a.batch)
        (work / "stage_b.index.json").write_text(json.dumps(index))
        res = submit_and_wait(c, reqs, work, "stage_b", a.poll)
        ingest(res, index, cost)
        cost_f.write_text(json.dumps(cost, indent=1))
    if not a.no_synthesis and not (work / "stage_c.results.jsonl").exists():
        import subprocess
        subprocess.run([sys.executable, str(Path(__file__).parent / "aggregate.py"), "--batch", a.batch])
        reqs, index = stage_c(a.batch, a.compare)
        res = submit_and_wait(c, reqs, work, "stage_c", a.poll)
        ingest(res, index, cost)
        cost_f.write_text(json.dumps(cost, indent=1))
    print("judge done: usd=%.3f %s" % (cost.get("usd", 0.0), {k: v for k, v in cost.items() if isinstance(v, dict)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
