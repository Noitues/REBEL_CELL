"""Build, submit and ingest the plan-2 W1 agent briefs (Message Batches, Sonnet 5.5).

    python tools/batch/build_w1_briefs.py --out <dir>                 # write <dir>/briefs_w1.jsonl, print the estimate
    python tools/batch/build_w1_briefs.py --out <dir> --submit        # also submit; id saved to <dir>/batch_ids.json
    python tools/batch/build_w1_briefs.py --out <dir> --ingest        # wait, fetch, write docs/handoff/plan2/drafts/briefs_w1/<slice>.md

Same pattern as build_design_drafts3.py (BRIEF_SLICES / BRIEF_ROLE / build_briefs / mk). Credentials: ANTHROPIC_API_KEY or the
Windows user variable of that name; never printed. Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_design_drafts3 as b3  # noqa: E402
from build_design_drafts import ROOT, read  # noqa: E402
from build_design_drafts2 import DRAFTS, strip_header  # noqa: E402

OUT_DIR = ROOT / "docs/handoff/plan2/drafts/briefs_w1"

BRIEF_SLICES = {
    "NA-11": ("Layout-rule port: frontage >= 6 floors, border streets 8 BU, hero sign rule, street r2 height passes, unique ids, on today's fixed city; Python layout.rules = Godot heights.", "fix-visual", "NA"),
    "NA-12": ("Per-seed CityGenerator (territories, HQ lot per corp, blocks, key locations) emitting the planner schema; NeonCity, CityLayoutRecorder, CityLayout and the bake cache key read it. Scope per D3.", "fix-rules (OPUS-BECAUSE: campaign determinism + save compatibility)", "NA"),
    "NA-21": ("GDScript twins + parity: NetrunArtDeriver, NetrunCameraRig, OcclusionHelper, reveal tiers, dress_<run>.json v1 reader twin (ported last). Byte-identical derive JSON for >= 10 fixture seeds.", "Batch (module ports) + fix-mechanical", "NA"),
    "NA-22": ("City shaders: city_building look_blend / section / z_cut / INSTANCE_CUSTOM; city_fog, beam_shaft, wet_street, streak_lane; emission_multiplier. look_blend 0 leaves the HQ page unchanged.", "fix-visual", "NA"),
    "NA-23": ("Street netrun view (23a perspective rig + rooms, 23b overlay + hover): route columns, DECISION / OVERVIEW / HOVER, mouse + number keys, Z, Enter, Esc; grease-pencil overlay, TARGET edge arrow, hover power cut.", "fix-visual", "NA"),
    "NA-24": ("Dressing + reveal tiers: signage, streak lanes, kerb lamps, beams, fog, plumes, always-alive loops; district languages; per-asset reveal via visibility_range.", "fix-visual", "NA"),
    "NA-25": ("Entry sequence: HQ select, plan pencil, JACK IN, binary rain, CRT collapse, 3.0 s dive, REVEAL, MARK, ZOOM, CHOOSE; one press skips (the route-skip key); jack-out reverses; MotionSkip.", "fix-visual", "NA"),
    "NA-26": ("Retire the old route page (RouteOverlay route uses, RouteCableRouter, RouteLinkLayout, RouteCover, D13 hidden-node code, show-all option, GRID VIEW per D6) and port its tests; never just delete a test.", "fix-mechanical", "NA"),
    "NA-ID": ("Godot ID capture: beauty.png + id.png + capture.json per PIPELINE_SPEC 12.0. id classes 0 sky, 1 landmark, 2 city, 3 link structure, 5 rooms, 6 movers; on class 5 G = room index (1-based) and B = layer (1-based). Unlit, nearest-sampled, no UI.", "fix-visual", "NA"),
    "N8": ("xN status stacks: slot statuses become {status: stacks}; save version 2 -> 3 with migration; xN badge.", "fix-rules (OPUS-BECAUSE: save format + determinism hash)", "N"),
    "N9": ("Status rules + corruption as a RAM cost: OUTPUT_DOWN, TIER_DOWN; PARASITE -> OUTPUT_DOWN x2; CORRUPTED = RAM x2 (Q36), enemy-wheel halving (Q37), self-damage retired, RAM forecast.", "fix-rules", "N"),
    "N20": ("Slice riders: hits, hits_per_target_status, perfect_multiplier, pierce (Q39: pierce bypasses BLOCK and SHIELD only).", "fix-rules (OPUS-BECAUSE: damage order)", "N"),
    "N6": ("Enemy listeners: reactions to ON_NUDGE / ON_CARD_PLAYED / ON_PERFECT, ON_RAM_SPENT, ON_HIT_DEALT; no random input, undo-clean; the preview shows listener results exactly (Q19).", "fix-rules (OPUS-BECAUSE: preview = result, determinism)", "N"),
    "N7": ("Block nudge / respin: nudge_locked / respin_locked, LOCK_* effects, refusals with reasons, overlay. Turn lifecycle per Q31: locks removed at end of turn except Freeze.", "fix-rules", "N"),
    "N12": ("Variable slice sizes 0-30 (Q20) + sub-tick map: size_ticks, tick_quality, WheelMath on cumulative boundaries, snap to nearest tick, lift the 6-slice cap, wedges, loadout sub-tick map. Start only; Calibrated limits is a follow-up.", "fix-rules (OPUS-BECAUSE: WheelMath determinism)", "N"),
    "Q19-PREVIEW": ("Preview shows the result of any nudge or card play; random outcomes show as '?' (a respin shows its direction and a '?' over a ghosted needle); compound plays show every known part exactly and only unknown parts as '?'. Rider chips and the Heat chip are follow-ups (do not decide).", "fix-rules (preview == result) + fix-visual for the chip", "X"),
    "MOTION-TIMINGS": ("Move inline motion timings (dur * 0.2 style fractions, fade spans) in combat_fx_layer and wheel_view into content/config/ui_motion.tres with REQUIRED_IDS entries and lab demos; end state under reduce effects unchanged.", "fix-mechanical", "X"),
    "RULE5-CMO": ("Rule-5 remainder of scripts/ui/city_map_overlay.gd (about 12 R5 lines): literal-for-const swaps with identical values, consts with ## docs; no behavior change. Raid map overlay stays (kept, not retired).", "Batch const_edits (Sonnet) + fix-mechanical", "X"),
}

DEPENDS = {  # REPLAN C.1 / C.3
    "NA-11": "NA-02, NA-03", "NA-12": "NA-11, D3, B1", "NA-21": "NA-02, NA-03", "NA-22": "NA-21", "NA-23": "NA-21, NA-22, D7",
    "NA-24": "NA-23", "NA-25": "NA-23, NA-24", "NA-26": "NA-25", "NA-ID": "NA-04, NA-23", "N8": "none", "N9": "N8",
    "N20": "N9", "N6": "none", "N7": "N6 (optional)", "N12": "none", "Q19-PREVIEW": "N6, N9 (sources of '?')",
    "MOTION-TIMINGS": "none", "RULE5-CMO": "none (raid maps stay; not NA-26)",
}

LANE_RULE = ("LANE RULE (binding): fix-rules defaults to Sonnet. Opus only with an `OPUS-BECAUSE:` line, and only for RNG, save format, damage order or "
             "determinism contracts. Put the lane in the brief; name Opus only if one of those applies.")

BRIEF_ROLE = """YOU WRITE ONE AGENT BRIEF in the repo's brief style (the W3 brief is shown as the style model). HARD LIMIT: the brief text must be under 2700 characters including markdown (about 380 words; drop prose, use terse bullets, never exceed this); a long list goes to a named file under docs/handoff/ that the brief tells the agent to read (say which file and what it must hold; do not write that file's content here). Output exactly:
# <slice id>: <title>
- **Goal** (2-4 lines), **Base / tag** (placeholders `<BASE_SHA>`, `<TEMP_TAG>`), **Agent type and lane** (fix-rules / fix-mechanical / fix-visual / Batch; Opus only with an OPUS-BECAUSE line), **Depends on** (slice ids).
- **Read first** (paths only: the designer rulings it must obey by Q number, and for NA slices NA02_FIELDS / DERIVE_V2_REVIEW "AD resolutions" / PIPELINE_SPEC 12.0 and 12.8 when relevant).
- **Files** (owned paths, from the system row's code area; real paths only, say "new" for new files).
- **Acceptance** (numbered, testable, each with a number or an observable).
- **Tests** (file names and tier, referencing the test plan docs/handoff/plan2/drafts/test_plans/<n#>.md when one exists; CLAUDE.md rule 6).
- **Not in scope** and **Conflicts** (shared files and ordering from REPLAN C.2).
- **Report**: the RESULT envelope from docs/process/agent_rules/common.md.
Apply the designer rulings given; do NOT guess a ruling. Anything the brief cannot settle goes at the very end as lines starting with `Q:` (max 3), each one sentence. If a ruling is marked pending/follow-up, say "placeholder default behind config" and add a Q:. Do not invent file paths beyond the code areas shown. Keep scope to the slice. US English."""


def rulings() -> str:
    t = read(ROOT / "docs/DECISIONS.md")
    a = t.index("### 2026-10-18 — Designer rulings: decision sheet")
    b = t.index("### 2026-10-18 — Plan 2 W0 N1b", a)
    return t[a:b]


def section(text: str, start: str, end: str) -> str:
    a = text.index(start)
    b = text.index(end, a + len(start)) if end else len(text)
    return text[a:b]


def row_of(replan: str, sid: str) -> str:
    for line in replan.splitlines():
        if line.startswith(f"| {sid} "):
            return line
    return ""


def build() -> list[dict]:
    replan = read(ROOT / "docs/handoff/gates/REPLAN_2026-10-16.md")
    w3 = read(ROOT / "docs/handoff/plan1/W3.md")[:3000]
    common = read(ROOT / "docs/process/agent_rules/common.md")
    rul = rulings()
    c1 = section(replan, "### C.1 Waves and gates", "### C.3")  # C.1 + C.2
    na02 = read(ROOT / "docs/handoff/plan2/NA02_FIELDS.md")[:9000]
    dv2 = read(ROOT / "docs/handoff/netrun_art/DERIVE_V2_REVIEW.md")
    ad = section(dv2, "## AD resolutions of the findings", "## Check input shapes")
    spec = read(ROOT / "docs/handoff/netrun_art/PIPELINE_SPEC.md")
    s120 = section(spec, "### 12.0 Where each check runs", "\n### 12.1")[:6000]
    s128 = section(spec, "### 12.8 Golden plates", "\n## ")[:2500]
    out = []
    for sid, (goal, lane, kind) in BRIEF_SLICES.items():
        if kind == "N":
            ctx = f"System row:\n{b3.n_row(sid)}\n"
            tp = DRAFTS / "test_plans" / f"{sid.lower()}.md"
            ctx += "\nTest plan (excerpt, to reference):\n" + (strip_header(read(tp))[:3500] if tp.exists() else "(none)") + "\n"
        elif kind == "NA":
            ctx = f"REPLAN row:\n{row_of(replan, sid) or '(NA-ID is a new slice: Godot ID capture for the section 12 checks on Godot captures)'}\n"
            ctx += ("\n=== Art-pass contract: NA02_FIELDS (head) ===\n" + na02 + "\n\n=== DERIVE_V2_REVIEW: AD resolutions ===\n" + ad
                    + "\n\n=== PIPELINE_SPEC 12.0 ===\n" + s120 + "\n\n=== PIPELINE_SPEC 12.8 ===\n" + s128 + "\n")
        else:
            ctx = ("Cross-cutting slice, no system row. Codebase facts: W0 RULE5b moved literals to consts; inline motion timings in combat_fx_layer / wheel_view "
                   "(dur * 0.2 style fractions, fade spans) belong in content/config/ui_motion.tres (REQUIRED_IDS + lab demo). city_map_overlay still has about 12 R5 lines. "
                   "Preview '?' rule is Q19.\n")
        user = (f"Write the brief for slice {sid}.\nGoal summary: {goal}\nSuggested lane: {lane}\nDepends on: {DEPENDS[sid]}\n\n{LANE_RULE}\n\n{ctx}\n"
                f"=== Designer rulings (DECISIONS 2026-10-18 decision sheet; Q9, Q19, Q20, Q31, Q35-Q37, Q40 apply to N6-N9/N12/N20) ===\n{rul}\n\n"
                f"=== REPLAN C.1 waves and C.2 ordering ===\n{c1}\n\n"
                f"=== Style model: W3 brief (head) ===\n{w3}\n\n=== RESULT envelope and rules (common.md) ===\n{common}")
        out.append(b3.mk(f"brief__{sid.lower().replace('-', '')}", user, 6000, BRIEF_ROLE))
    return out


LIMIT = 2700
COMPRESS_SYSTEM = ("You shorten an agent brief for REBEL_CELL. Keep every section heading and the structure, every acceptance number, file path, test name, "
                   "Q number and every trailing line that starts with `Q:`. Cut prose, merge bullets, drop examples. The result MUST be under 2600 "
                   "characters including markdown. Output the brief only, no preamble.")


def compress(d: Path) -> None:
    """Pass 2: one small request per brief over LIMIT characters (the model overshot the role's limit)."""
    import anthropic
    from ingest_drafts import api_key

    reqs = []
    for f in sorted(OUT_DIR.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        body = text.split("-->", 1)[1].strip()
        if len(body) <= LIMIT:
            continue
        reqs.append({"custom_id": "c__" + f.stem.replace("-", ""), "params": {
            "model": b3.MODEL if hasattr(b3, "MODEL") else "claude-sonnet-5-5", "max_tokens": 4000, "system": COMPRESS_SYSTEM,
            "messages": [{"role": "user", "content": f"Brief ({len(body)} chars, limit 2600):\n\n{body}"}]}})
    client = anthropic.Anthropic(api_key=api_key())
    b = client.messages.batches.create(requests=reqs)
    ids_path = d / "batch_ids.json"
    ids = json.loads(ids_path.read_text(encoding="utf-8"))
    ids["briefs_w1_c"] = b.id
    ids_path.write_text(json.dumps(ids), encoding="utf-8")
    print("compress submitted", len(reqs), b.id)


def ingest2(d: Path) -> None:
    import anthropic
    from ingest_drafts import api_key

    client = anthropic.Anthropic(api_key=api_key())
    bid = json.loads((d / "batch_ids.json").read_text(encoding="utf-8"))["briefs_w1_c"]
    while client.messages.batches.retrieve(bid).processing_status != "ended":
        time.sleep(20)
    names = {f"c__{s.lower().replace('-', '')}": s for s in BRIEF_SLICES}
    extra = 0.0
    for r in client.messages.batches.results(bid):
        sid = names[r.custom_id]
        f = OUT_DIR / f"{sid.lower()}.md"
        if r.result.type != "succeeded":
            print(sid, r.result.type)
            continue
        m = r.result.message
        text = "".join(bl.text for bl in m.content if bl.type == "text").strip()
        cost = (m.usage.input_tokens * 1.0 + m.usage.output_tokens * 5.0) / 1e6
        extra += cost
        if len(text) < 1500 or ("Q:" in f.read_text(encoding="utf-8") and "Q:" not in text):
            print(sid, "pass 2 rejected (empty or lost Q lines); pass-1 brief kept", len(text))
            continue
        old = f.read_text(encoding="utf-8").split("-->", 1)[0]
        f.write_text(old + f"-->\n<!-- shortened by a second pass (compress), cost ${cost:.3f} -->\n\n" + text + "\n", encoding="utf-8", newline="\n")
        print(sid, len(text), f"${cost:.3f}", "Q lines", sum(1 for ln in text.splitlines() if ln.strip().startswith("Q:")))
    print(f"PASS2 TOTAL ${extra:.3f}")


def ingest(d: Path) -> None:
    import anthropic
    from ingest_drafts import api_key

    client = anthropic.Anthropic(api_key=api_key())
    bid = json.loads((d / "batch_ids.json").read_text(encoding="utf-8"))["briefs_w1"]
    while True:
        b = client.messages.batches.retrieve(bid)
        if b.processing_status == "ended":
            break
        print(f"{b.processing_status} {b.request_counts.processing} processing", flush=True)
        time.sleep(30)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ids = {f"brief__{s.lower().replace('-', '')}": s for s in BRIEF_SLICES}
    rows = []
    for r in client.messages.batches.results(bid):
        sid = ids[r.custom_id]
        if r.result.type != "succeeded":
            rows.append({"slice": sid, "status": r.result.type, "cost": 0.0, "chars": 0, "q": []})
            continue
        m = r.result.message
        text = "".join(bl.text for bl in m.content if bl.type == "text").strip()
        u = m.usage
        cw, cr = u.cache_creation_input_tokens or 0, u.cache_read_input_tokens or 0
        cost = (u.input_tokens * 1.0 + cw * 1.25 + cr * 0.10 + u.output_tokens * 5.0) / 1e6
        status = "ok" if m.stop_reason == "end_turn" else f"TRUNCATED ({m.stop_reason})"
        head = (f"<!-- W1 brief via Message Batches, {m.model}, batch {bid}, custom_id {r.custom_id}; status {status}; "
                f"tokens in {u.input_tokens} cache-write {cw} cache-read {cr} out {u.output_tokens}; cost ${cost:.3f}. DRAFT brief: not yet dispatched. -->\n\n")
        (OUT_DIR / f"{sid.lower()}.md").write_text(head + text + "\n", encoding="utf-8", newline="\n")
        qs = [ln.strip() for ln in text.splitlines() if ln.strip().startswith("Q:")]
        rows.append({"slice": sid, "status": status, "cost": cost, "chars": len(text), "q": qs})
    (d / "ingest_summary.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    for x in sorted(rows, key=lambda x: x["slice"]):
        print(x["slice"], x["status"], x["chars"], f"${x['cost']:.3f}", len(x["q"]))
    print(f"TOTAL ${sum(x['cost'] for x in rows):.3f}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--ingest", action="store_true")
    ap.add_argument("--compress", action="store_true", help="second pass: shorten every brief over the limit (submit, then --ingest --pass2)")
    ap.add_argument("--pass2", action="store_true", help="with --ingest: read the compress batch (key briefs_w1_c) and overwrite the briefs")
    args = ap.parse_args()
    d = Path(args.out)
    d.mkdir(parents=True, exist_ok=True)
    if args.compress:
        compress(d)
        return 0
    if args.ingest:
        (ingest2 if args.pass2 else ingest)(d)
        return 0
    reqs = build()
    p = d / "briefs_w1.jsonl"
    with p.open("w", encoding="utf-8", newline="\n") as fh:
        for r in reqs:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    unc = sum(b3.est_tokens(r["params"]["messages"][0]["content"]) for r in reqs)
    cost = (unc * 1.0 + b3.COMMON_TOKENS * 1.25 + b3.COMMON_TOKENS * len(reqs) * 0.1 + len(reqs) * 3500 * 5.0) / 1e6
    print(f"{len(reqs)} requests, ~{unc:,} uncached input tokens, expected ${cost:.2f}")
    if args.submit:
        import anthropic
        from ingest_drafts import api_key

        client = anthropic.Anthropic(api_key=api_key())
        b = client.messages.batches.create(requests=reqs)
        (d / "batch_ids.json").write_text(json.dumps({"briefs_w1": b.id}), encoding="utf-8")
        print("submitted", b.id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
