"""Build, submit and ingest the REPLAN2 draft (docs/handoff/gates/REPLAN_2026-10-19.md) on the Message Batches API (Sonnet 5.5).

    python tools/batch/build_replan2.py --out <dir>             # write <dir>/replan2.jsonl, print the size estimate
    python tools/batch/build_replan2.py --out <dir> --submit    # also submit; id saved to <dir>/batch_ids.json
    python tools/batch/build_replan2.py --out <dir> --ingest    # wait, fetch, write the draft to docs/handoff/gates/

One request. Inputs are excerpts (REPLAN_2026-10-16 sections A and C, the 2026-10-18 DECISIONS entries, theme rules,
S5 headline, W1 brief status, art-pass state). Credentials: ANTHROPIC_API_KEY or the Windows user variable; never printed.
Never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_design_drafts import ROOT, read  # noqa: E402

MODEL = "claude-sonnet-5-5"
MAX_TOKENS = 32000
OUT = ROOT / "docs/handoff/gates/REPLAN_2026-10-19.md"
THEMES = ROOT / "docs/handoff/plan2/drafts/themes"

W1_DONE = "NA-21, NA-22 (incl. 22a-d), NA-23, N8, N9, N20, N6"
W1_PROGRESS = "NA-11, NA-12, NA-24, NA-25, NA-26, NA-ID, NA-04b, OCC-OUTLINE, N7, N12, Q19-PREVIEW, MOTION-TIMINGS, RULE5-CMO"

ART_STATE = """ART-PASS STATE (2026-10-18/19, relayed): golden plates delivered (18 plates); all 7 landmark entries (LANDMARK_ENTRIES, art-pass 77cdfde9) and the face outlines (FACE_OUTLINE) are in; the exploit-building concepts were approved as DIRECTIONS (first picks: Aurelian leaning campanile / Intel, Meridian departures tower / Intel, Orbital spectrum radome / Virus, REBEL_CELL dossier house / Intel, Solace culture garden / Virus, Tethys harbourmaster's gauge / Intel, Halcyon the open leak / Virus). Blender stays with the art-pass session (D8 a). The art-pass session reviews one comparison sheet per group before merge."""

ROLE = """You write the REPLAN for waves W2 onward of the REBEL_CELL project (Godot 4.7 deckbuilder, build session of one orchestrator plus short-lived agents). Output ONE markdown document, no preamble, written the way REPLAN_2026-10-16 is: a status header (drafted by a Batch API request, a proposal; nothing is built), an Inputs list, then these sections in this order:
## 0. Facts that shape the plan   (table: Fact | Where | Consequence; include W1 status, the PT-004 result, the balance finding, the art state)
## A. Slices per wave   (one table per wave: Slice | Goal | Acceptance | Size, lane | Depends on. Waves: W1 close-out (what is left, short), W2, W3, W4 (balance track and gates), Later (Tethys, Aurelian corp wave). Lanes: BATCH (Batch API) first, then fix-mech / fix-visual / fix-rules (Sonnet), Opus only with an OPUS-BECAUSE line.)
## B. Corporation themes beside their HQ   (table: corp | theme | street light form | HQ full form | raid hook | wave | defaults taken)
## C. Conflicts and ordering   (table: Shared area | Touched by | Rule)
## D. Parallel slots   (the two-Godot + one-Python rule, GPU / windowed jobs one at a time, balance sims at most 2 processes in slots with no gate running, Batch API unlimited)
## E. Gates   (PT-006 and PT-007: the automated part only is required: full suite once alone, smoke, validate, push gate; the human/Claude-tester playtest list is written but is optional by designer ruling; art-pass sheets per group)
## F. Retire
## G. Decisions the designer may want to revisit   (a short bullet list, no blocking questions; every item states the default that is being taken and the wave where it would bite)

MUST include, with slice ids you invent as WH-xx (HQ / theme), EX-xx (exploit buildings), BAL-xx (balance), RD-xx (raid operatives), ST-xx (status audit), PV-xx (Q19 preview), RG-xx (run_graph v2 / D4 nodes):
(a) W2 order: Solace first (with the Genome Core and NA-31 shared HQ kit, NA-33 landmarks, NA-32 HQ netrun), then Halcyon, then REBEL_CELL (DISPATCH three routes, then the Sync Strike finale per Q34, with the Sync Strike pass), then Orbital (A DEAD ZONE), then Meridian (A PAYLOAD). Each corp's theme rules are built beside its HQ netrun: state, preview, numbers in config, tests. Tethys (THE WATER LEVEL) and Aurelian (colosseum rings) belong to the later corp wave (they are not playable corps yet, D1/NA-42) but their rules drafts are kept and their art needs answered.
(b) Exploit-building netruns: run-graph shape (outside route to the building, then >= 3 inside node layers ending at the exploit target), slot hooks (spec 8.8), a per-lot special-building hook, lot size and clearance, outside starts, occlusion host exemption; built with NA-41 / B2 / D5 (each access key equals an Exploit, each Exploit its own special building). Order: generator and key placement (B2/D5) first, one unique netrun per corp following that corp's HQ, the other two buildings per corp later.
(c) A balance track that does NOT tune to the sim bots (designer ruling: the S5 boss win of 6 percent mostly reflects the bot playing badly): first a better reference policy (heuristic lookahead bot, already measured at 17-21 dealt per turn against 14.4 for the builtin) and/or Claude-tester / designer play data, THEN a difficulty pass (boss HP and enrage first; phases are not shortened). Bot numbers, if used at all, get sharply lowered targets. No difficulty tuning before the reference exists.
(d) The raid-operative design pass (separate from netrun operative design; Q42 Ghost is an operative class, raid roles; operatives are never killed during raids), the status audit (Q40: audit Slay-the-Spire-style statuses against OUTPUT_DOWN / TIER_DOWN / CORRUPTED and propose gaps; a Batch draft, then rulings), the Q19 "?" preview (random outcomes show "?"; compound plays show known parts exactly), and the D4 nodes (REST: heal or swap Firmware locations; Workshop; Cache with a vetted mini-puzzle; no Intel/Relay/Ambush nodes in normal runs) with run_graph v2 (contract version bump; N16 map_edits and the Q23 validator never drop below 3 required Exploits).
(e) Keep the machine rule: two Godot processes + one Python-only agent at a time (three worktrees, under the cap of five); cheapest lanes first (Batch API, then Sonnet agents, Opus only OPUS-BECAUSE); the gates PT-006 and PT-007 with their automated part.
(f) End with section G; no blocking questions anywhere. Where a designer call is open, take the default and list it in G.
Respect: designer scope text 1.0 and mouse/keyboard only (no accessibility, gamepad); US English; the PT-004 playtest was skipped, so W0/W1 balance is re-tuned later; the dependency on shared files (netrun_session.gd, netrun_scene.gd, hq_scene.gd, run graph) follows the 2026-10-16 conflict rules. Do not invent mechanics beyond the inputs. Keep it concrete: every slice has an acceptance a test or a capture can check. Target 5000-7500 words."""


def section(text: str, start: str, end: str | None) -> str:
    a = text.index(start)
    b = text.index(end, a) if end else len(text)
    return text[a:b]


def decisions_excerpt() -> str:
    t = read(ROOT / "docs/DECISIONS.md")
    heads = ["Overnight: defaults taken on open calls", "PT-004 gate (automated) passed",
             "Designer ruling (relayed by the art-pass session; to confirm): exploit-building netruns",
             "Designer: PT-004 runs the automated gate only", "Designer rulings: corporation-wide themes",
             "Designer ruling (relayed by the art-pass session): Tethys THE WATER LEVEL",
             "Designer rulings: decision sheet follow-ups", "Designer rulings: decision sheet ("]
    parts = []
    for h in heads:
        m = re.search(r"^### 2026-10-18 — " + re.escape(h), t, re.M)
        if not m:
            raise SystemExit(f"DECISIONS heading not found: {h}")
        n = re.search(r"^##+ ", t[m.end():], re.M)
        parts.append(t[m.start(): m.end() + (n.start() if n else len(t))].rstrip())
    a = t.index("- **D2:** names are low effort")
    parts.append("(2026-10-16 replan rulings, excerpt)\n" + t[a: a + 2600])
    return "\n\n".join(parts)


def theme_rules() -> str:
    out = []
    for c in ["solace", "halcyon", "rebel_cell", "orbital", "meridian", "aurelian", "tethys"]:
        s = read(THEMES / f"{c}.md")
        m = re.search(r"^## 1\..*?(?=^## 2\.)", s, re.M | re.S)
        body = (m.group(0) if m else s)[:3200]
        out.append(f"--- {c} (rules summary, first 3200 chars of section 1) ---\n{body}")
    return "\n\n".join(out)


def s5_headline() -> str:
    t = read(ROOT / "docs/handoff/plan2/S5_RESULTS.md")
    return section(t, "## 0. Headline numbers", "## 1. Step 0")


def w1_status() -> str:
    t = read(ROOT / "docs/handoff/plan2/drafts/briefs_w1/README.md")
    table = "\n".join(ln[:140] for ln in t.splitlines() if ln.startswith("| ") and not ln.startswith("| ---"))
    return (f"W1 STATUS (orchestrator, 2026-10-19): DONE = {W1_DONE}. IN PROGRESS (briefs dispatched or queued) = {W1_PROGRESS}. "
            f"Brief table (slice | lane | depends):\n{table}")


def build() -> dict:
    p = read(ROOT / "docs/handoff/gates/REPLAN_2026-10-16.md")
    a = section(p, "## A. The netrun art build as slices", "## B. Game-design items")
    c = section(p, "## C. Combined roadmap", "## D. Designer decisions needed")
    user = (f"Draft docs/handoff/gates/REPLAN_2026-10-19.md.\n\n=== REPLAN_2026-10-16 section A (current slices) ===\n{a}\n\n"
            f"=== REPLAN_2026-10-16 section C (current W2 / W3 / Later, conflicts, slots, retire) ===\n{c}\n\n"
            f"=== DECISIONS 2026-10-18 (rulings, follow-ups, themes, overnight defaults, Q24.1, Q34) ===\n{decisions_excerpt()}\n\n"
            f"=== Themes README ===\n{read(THEMES / 'README.md')}\n\n=== Theme rules summaries ===\n{theme_rules()}\n\n"
            f"=== S5 headline ===\n{s5_headline()}\nDesigner ruling: do not tune difficulty to the sim bots.\n\n"
            f"=== {w1_status()} ===\n\n=== {ART_STATE} ===\n")
    return {"custom_id": "replan2", "params": {"model": MODEL, "max_tokens": MAX_TOKENS, "system": ROLE,
            "thinking": {"type": "adaptive"}, "output_config": {"effort": "medium"},
            "messages": [{"role": "user", "content": user}]}}


def build_finish() -> dict:
    """Second request: the first one hit max_tokens before section G; finish section F and write G (and only that)."""
    draft = read(OUT)
    draft = draft[draft.index("\n\n") + 2:] if draft.startswith("<!--") else draft
    cut = draft.rfind("\n- ")  # drop a possibly cut last bullet
    draft = draft[:cut]
    user = ("Below is a TRUNCATED replan draft (it stops inside section F). Output ONLY the continuation: first the missing "
            "bullets of '## F. Retire' (no repeats of bullets already shown), then '## G. Decisions the designer may want to "
            "revisit' exactly as specified (short bullets, each with the default taken and the wave where it would bite; at "
            "least 12 bullets covering: themes defaults, Orbital A and Meridian A picks, DISPATCH R1-R5 defaults, Aurelian "
            "and Tethys deferred, exploit-building order, balance reference policy, Q24.1 death, D4 node set and Cache "
            "vetting, Q40 audit, raid operative pass, PT-006/PT-007 automated-only gates, Heat chip). No preamble, no "
            "closing remarks.\n\n=== DRAFT ===\n" + draft)
    return {"custom_id": "replan2", "params": {"model": MODEL, "max_tokens": 12000, "system": ROLE,
            "messages": [{"role": "user", "content": user}]}}


def client():
    import anthropic
    from ingest_drafts import api_key
    return anthropic.Anthropic(api_key=api_key())


def ingest(d: Path, finish: bool = False) -> None:
    cl = client()
    bid = json.loads((d / "batch_ids.json").read_text(encoding="utf-8"))["replan2f" if finish else "replan2"]
    while True:
        b = cl.messages.batches.retrieve(bid)
        if b.processing_status == "ended":
            break
        print(f"{b.processing_status} {b.request_counts.processing} processing", flush=True)
        time.sleep(30)
    for r in cl.messages.batches.results(bid):
        if r.result.type != "succeeded":
            raise SystemExit(f"result {r.result.type}")
        m = r.result.message
        text = "".join(bl.text for bl in m.content if bl.type == "text").strip()
        u = m.usage
        cw, cr = u.cache_creation_input_tokens or 0, u.cache_read_input_tokens or 0
        cost = (u.input_tokens * 1.0 + cw * 1.25 + cr * 0.10 + u.output_tokens * 5.0) / 1e6
        status = "ok" if m.stop_reason == "end_turn" else f"TRUNCATED ({m.stop_reason})"
        if finish:
            old = read(OUT).rstrip()
            cut = old.rfind("\n- ")
            OUT.write_text(old[:cut] + "\n" + text + "\n" + f"\n<!-- continuation batch {bid}; tokens out {u.output_tokens}; cost ${cost:.3f} -->\n",
                           encoding="utf-8", newline="\n")
            print(status, len(text), f"${cost:.3f}")
            return
        head = (f"<!-- REPLAN2 draft via Message Batches, {m.model}, batch {bid}; status {status}; tokens in {u.input_tokens} "
                f"out {u.output_tokens}; cost ${cost:.3f}. PROPOSAL: nothing is built. -->\n\n")
        OUT.write_text(head + text + "\n", encoding="utf-8", newline="\n")
        print(status, len(text), f"${cost:.3f}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--ingest", action="store_true")
    ap.add_argument("--finish", action="store_true", help="continuation request when the first hit max_tokens (use with --submit / --ingest)")
    a = ap.parse_args()
    d = Path(a.out)
    d.mkdir(parents=True, exist_ok=True)
    if a.ingest:
        ingest(d, a.finish)
        return 0
    if a.finish:
        cl = client()
        b = cl.messages.batches.create(requests=[build_finish()])
        ids = json.loads((d / "batch_ids.json").read_text(encoding="utf-8"))
        ids["replan2f"] = b.id
        (d / "batch_ids.json").write_text(json.dumps(ids), encoding="utf-8")
        print("submitted continuation", b.id)
        return 0
    r = build()
    (d / "replan2.jsonl").write_text(json.dumps(r) + "\n", encoding="utf-8", newline="\n")
    chars = len(r["params"]["messages"][0]["content"]) + len(ROLE)
    print(f"chars {chars}, ~{chars // 4} input tokens, est cost ${chars / 4 * 0.5 / 1e6 + 12000 * 2.5 / 1e6:.2f}")
    if a.submit:
        cl = client()
        b = cl.messages.batches.create(requests=[r])
        (d / "batch_ids.json").write_text(json.dumps({"replan2": b.id}), encoding="utf-8")
        print("submitted", b.id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
