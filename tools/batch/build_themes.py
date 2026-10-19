"""Build, submit and ingest the plan-2 corporation-wide theme drafts (Message Batches, Sonnet 5.5), round tag THEMES.

    python tools/batch/build_themes.py --out <dir> --art <dir-with-art_<corp>.md>   # write <dir>/themes.jsonl, print the estimate
    ... --submit      # also submit; id saved to <dir>/batch_ids.json
    ... --ingest      # wait, fetch, write docs/handoff/plan2/drafts/themes/<corp>.md and a summary

The art-pass files come from `git -C <art-pass clone> show aa32e1f2:docs/concepts/corp_themes/<corp>.md` (read-only), saved as art_<corp>.md in --art.
Credentials: ANTHROPIC_API_KEY or the Windows user variable of that name; never printed. Never run Python from stdin on this machine.
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

OUT_DIR = ROOT / "docs/handoff/plan2/drafts/themes"
HQ = ROOT / "docs/handoff/plan2/drafts/hq"

CORPS = {
    "solace": ("Solace: THE BLOOM", "settled", True,
               "A virus trails the operative through the netrun; if it catches up the operative is lost (DECISIONS Q24.1: 0 HP at any time is lost, the active netrun is abandoned, the raid unchanged; operatives are never killed during raids). In city raids a population infection percentage rises, and the longer the player delays the more die. If the player is too slow the city is infected, only Solace has the cure, and Solace wins. Confirm or rename the art plan's assumed names (bloom_front, bloom_gap, bloom_state, raid_infection_pct)."),
    "halcyon": ("Halcyon: the Eye (THE PANOPTICON)", "settled", True,
                "The Eye scans the city; runs through Spotted territory get some difficulty raised. The Eye moves; taking an Exploit makes the Eye focus on that area for 2 netruns before it starts moving again. The HQ run keeps the Eye effect. Confirm or rename the art plan's assumed state names."),
    "rebel_cell": ("REBEL_CELL: DISPATCH", "settled", True,
                   "A simultaneous infiltration: one operative by rooftop, one by street level, one by the sewer; each must reach its end point, then all three go for the mainframe HQ. RECONCILE with the Sync Strike ruling Q34 (in the decision-sheet rulings): the three routes ARE the run, the Sync Strike is the finale. Say exactly where the route phase ends and the Sync Strike begins, and what carries across. Confirm or rename the art plan's assumed state names."),
    "aurelian": ("Aurelian: colosseum rings", "settled", True,
                 "The city raid view becomes a larger colosseum of rings the player moves into, finding keys and opening gates to get closer to the HQ. Reuse the rim gates system being built (drafts/rim_gates) and the inner ring (drafts/inner_ring). Confirm or rename the art plan's assumed state names."),
    "tethys": ("Tethys: THE WATER LEVEL", "settled", False,
               "Adopt THE WATER LEVEL (Head LOW / RISING / HIGH / FALLING tick, UPPER / LOWER node Levels, sluices, Lock Cycle, Pressure Stair) from the HQ draft sections 1-3 (given). Your job is to EXTEND it: (a) street netruns: what floods in a street building, the water line per Head step; (b) raids: which defense nodes go under at HIGH and what that does. Art-pass needs: each node's Level, which node kinds are sluices, the street water line per Head step, the flooding raid nodes. There is no art-pass theme file for Tethys; state your assumed names for the art session."),
    "meridian": ("Meridian: 4 options", "options", False,
                 "The draft theme in the HQ draft is judged weak. Produce FOUR distinct theme OPTIONS for the designer to choose from (logistics / freight / tariffs / tracking / conveyors / WEIGHT / PRIORITY / AIRMAIL / Customs Seal are the corporation's identity, GDD 8.4b). Each option is a full short draft (street / HQ / raid, state, preview, numbers, tests) plus a one-line pitch, a cost estimate (new code vs reuse) and a risk. End with a ranked recommendation, clearly marked as advice."),
    "orbital": ("Orbital: 4 options", "options", False,
                "The draft theme in the HQ draft is judged bad. Produce FOUR distinct theme OPTIONS. Frame: they control satellites and communications and can bomb anyone. Leaning toward communication blackouts affecting netruns and city raids (make at least one option that, and at least one that is not a blackout). Each option is a full short draft (street / HQ / raid, state, preview, numbers, tests) plus a one-line pitch, cost (new code vs reuse) and risk. End with a ranked recommendation, clearly marked as advice."),
}

ROLE = """YOU WRITE ONE CORPORATION-WIDE THEME RULES DRAFT (plan 2, round THEMES). Output ONE markdown document, no preamble, with exactly these sections (for an OPTIONS corp, repeat sections 1-7 compactly for each option under "## Option A..D", then one shared section 8):
# <corp>: <theme name>
## 1. Rules: street (a LIGHT form in street netruns), HQ (the FULL form), raid (ONE hook). Numbered rules, each testable.
## 2. State and save fields (names, types, where they live: scripts/state/ objects, save version impact; deterministic, RngService streams only).
## 3. Preview (what the player sees before committing; random parts show as "?" per Q19).
## 4. Numbers (every number is a placeholder, marked `config: <file>.<key>`; no magic numbers).
## 5. Tests to write (name, tier fast/full, what it asserts; CLAUDE.md rule 6).
## 6. Art answers (answer the art-pass plan's "Questions for the build session" ONE BY ONE, numbered the same; where the plan assumed state names, confirm or rename them in a table). For corps without an art plan, list the state names and values the art session needs.
## 7. Reuse and dependencies (N# slices, Parasite ring, rim gates, enrage, resistance; what is NEW code).
## 8. Q-DESIGNER (lines that start exactly `Q-DESIGNER:`, one sentence each, max 6; only calls the designer alone can make).
Binding guardrails: one mechanic per corp; readable in the preview; reuse systems being built over new code; introduce in difficulty order; honor the designer rulings given (Q24.1 death, Q34 Sync Strike, Q36/Q37, Q39, Q40 etc.). Do not invent mechanics beyond the stated direction; where direction is silent, choose the simplest option behind config and put it in Q-DESIGNER. US English in every player-facing string."""


def rulings() -> str:
    t = read(ROOT / "docs/DECISIONS.md")
    a = t.index("### 2026-10-18 — Designer rulings: corporation-wide themes")
    b = t.index("### 2026-10-18 — Plan 2 W0 N1b", a)
    return t[a:b]


def build(art: Path, only: str = "", mx: int = 14000) -> list[dict]:
    rul = rulings()
    out = []
    for cid, (title, kind, has_art, direction) in CORPS.items():
        if only and cid not in only.split(","):
            continue
        hq = read(HQ / f"{cid}.md")
        if cid == "tethys":
            hq = hq[: hq.index("## 4. Node kit")]
        ap = art / f"art_{cid}.md"
        art_txt = ap.read_text(encoding="utf-8") if has_art and ap.exists() else "(no art-pass file for this corporation)"
        user = (f"Write the theme draft for {title} (status: {kind}).\n\nDESIGNER DIRECTION (binding):\n{direction}\n\n"
                f"=== HQ draft for this corporation ({'sections 1-3 only' if cid == 'tethys' else 'full'}) ===\n{hq}\n\n"
                f"=== Art-pass plan (read-only, aa32e1f2; answer its 'Questions for the build session') ===\n{art_txt}\n\n"
                f"=== DECISIONS: theme rulings, Tethys ruling, follow-ups and the decision-sheet rulings ===\n{rul}\n")
        out.append(b3.mk(f"theme__{cid}", user, mx, ROLE))
    return out


def ingest(d: Path, key: str = "themes") -> None:
    import anthropic
    from ingest_drafts import api_key

    client = anthropic.Anthropic(api_key=api_key())
    bid = json.loads((d / "batch_ids.json").read_text(encoding="utf-8"))[key]
    while True:
        b = client.messages.batches.retrieve(bid)
        if b.processing_status == "ended":
            break
        print(f"{b.processing_status} {b.request_counts.processing} processing", flush=True)
        time.sleep(30)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in client.messages.batches.results(bid):
        cid = r.custom_id.split("__", 1)[1]
        if r.result.type != "succeeded":
            rows.append({"corp": cid, "status": r.result.type, "cost": 0.0, "q": []})
            continue
        m = r.result.message
        text = "".join(bl.text for bl in m.content if bl.type == "text").strip()
        u = m.usage
        cw, cr = u.cache_creation_input_tokens or 0, u.cache_read_input_tokens or 0
        cost = (u.input_tokens * 1.0 + cw * 1.25 + cr * 0.10 + u.output_tokens * 5.0) / 1e6
        status = "ok" if m.stop_reason == "end_turn" else f"TRUNCATED ({m.stop_reason})"
        head = (f"<!-- THEMES draft via Message Batches, {m.model}, batch {bid}, custom_id {r.custom_id}; status {status}; "
                f"tokens in {u.input_tokens} cache-write {cw} cache-read {cr} out {u.output_tokens}; cost ${cost:.3f}. DRAFT: designer picks. -->\n\n")
        (OUT_DIR / f"{cid}.md").write_text(head + text + "\n", encoding="utf-8", newline="\n")
        qs = [ln.strip() for ln in text.splitlines() if ln.strip().startswith("Q-DESIGNER:")]
        rows.append({"corp": cid, "status": status, "cost": cost, "q": qs, "chars": len(text)})
    (d / "ingest_summary.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    for x in sorted(rows, key=lambda x: x["corp"]):
        print(x["corp"], x["status"], x.get("chars"), f"${x['cost']:.3f}", len(x["q"]))
    print(f"TOTAL ${sum(x['cost'] for x in rows):.3f}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--art", default="")
    ap.add_argument("--only", default="", help="comma list of corps (a re-run of truncated ones)")
    ap.add_argument("--key", default="themes", help="batch id key in batch_ids.json (use another for a re-run)")
    ap.add_argument("--max-tokens", type=int, default=14000)
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--ingest", action="store_true")
    args = ap.parse_args()
    d = Path(args.out)
    d.mkdir(parents=True, exist_ok=True)
    if args.ingest:
        ingest(d, args.key)
        return 0
    reqs = build(Path(args.art), args.only, args.max_tokens)
    with (d / "themes.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for r in reqs:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    unc = sum(b3.est_tokens(r["params"]["messages"][0]["content"]) for r in reqs)
    cost = (unc * 1.0 + b3.COMMON_TOKENS * 1.25 + b3.COMMON_TOKENS * len(reqs) * 0.1 + len(reqs) * 9000 * 5.0) / 1e6
    print(f"{len(reqs)} requests, ~{unc:,} uncached input tokens, expected ${cost:.2f}")
    if args.submit:
        import anthropic
        from ingest_drafts import api_key

        client = anthropic.Anthropic(api_key=api_key())
        b = client.messages.batches.create(requests=reqs)
        p = d / "batch_ids.json"
        ids = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
        ids[args.key] = b.id
        p.write_text(json.dumps(ids), encoding="utf-8")
        print("submitted", b.id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
