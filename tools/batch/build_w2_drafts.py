"""Build, submit and ingest the W2 batch-lane drafts (Message Batches, Sonnet 5.5): WH-01 (theme tables) and EX-01 (exploit-building rules).

    python tools/batch/build_w2_drafts.py --out <dir>                  # write <dir>/w2.jsonl, print the estimate
    python tools/batch/build_w2_drafts.py --out <dir> --submit         # also submit; id saved to <dir>/batch_ids.json
    python tools/batch/build_w2_drafts.py --out <dir> --ingest         # wait, fetch, write the drafts, print the cost

Outputs:
    WH-01: docs/handoff/plan2/drafts/themes/tables/<corp>.md        (5 playable corps)
    EX-01: docs/handoff/plan2/drafts/exploit_buildings/<corp>.md    (7 corps)
Options: --only wh01 | ex01 (a subset), --max-tokens-wh N, --max-tokens-ex N, --key NAME (batch id key for a re-run).
Credentials: ANTHROPIC_API_KEY or the Windows user variable of that name; never printed. Never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_design_drafts3 as b3  # noqa: E402
from build_design_drafts import ROOT, read  # noqa: E402

THEMES = ROOT / "docs/handoff/plan2/drafts/themes"
HQ = ROOT / "docs/handoff/plan2/drafts/hq"
TABLES = THEMES / "tables"
EXDIR = ROOT / "docs/handoff/plan2/drafts/exploit_buildings"
REPLAN = ROOT / "docs/handoff/gates/REPLAN_2026-10-19.md"
SPEC = ROOT / "docs/handoff/netrun_art/PIPELINE_SPEC.md"
DECISIONS = ROOT / "docs/DECISIONS.md"

# WH-01: the five playable corps. choice = the option picked by the overnight defaults (None = settled draft).
WH_CORPS = {
    "solace": ("Solace: THE BLOOM", None, ["2.7 ", "2.8 ", "2.9 "], "Solace"),
    "halcyon": ("Halcyon: the Eye (THE PANOPTICON)", None, ["2.13 ", "2.14 ", "2.15 "], "Halcyon"),
    "rebel_cell": ("REBEL_CELL: DISPATCH", None, ["2.16 ", "2.17 ", "2.18 ", "2.19 ", "2.20 "], "REBEL_CELL"),
    "orbital": ("Orbital: A DEAD ZONE", "A", ["2.21 ", "2.22 ", "2.23 ", "2.24 "], "Orbital"),
    "meridian": ("Meridian: A PAYLOAD", "A", ["2.25 ", "2.26 ", "2.27 ", "2.28 "], "Meridian"),
}

# EX-01: first picks (DECISIONS 2026-10-18 exploit-building ruling, art-pass ca2e3707): corp -> (building, Exploit, W2/W3 order note)
EX_CORPS = {
    "solace": ("culture garden", "Virus", "pilot in W2 (EX-11); BLOOM applies in its light form"),
    "halcyon": ("the open leak", "Virus", "W3 (EX-12)"),
    "rebel_cell": ("dossier house", "Intel", "W3 (EX-13)"),
    "orbital": ("spectrum radome", "Virus", "W3 (EX-14)"),
    "meridian": ("departures tower", "Intel", "W3 (EX-15)"),
    "aurelian": ("leaning campanile", "Intel", "Later wave (not a playable corp yet, D1 / NA-42)"),
    "tethys": ("harbourmaster's gauge", "Intel", "Later wave (not a playable corp yet, D1 / NA-42)"),
}

WH_ROLE = """YOU WRITE ONE WH-01 RECONCILIATION TABLE (plan 2, W2, round WH01) for ONE corporation. You are given the corp's theme draft (a design draft) and the rulings that bind it. Reconcile them into ONE markdown document of TABLES that a build agent will implement from, with no preamble and exactly these sections (headers verbatim):
# <corp>: WH-01 table
## 1. Config keys
A table `| key | default | unit / note | source |`. One row per key; the key cell is the backticked `file.key` form (file = campaign_config, or the theme file the draft names); every default is a concrete number or value. Include EVERY `config:` key the draft names (same key names, so a lint can match them), plus any key the rulings add (say "added by <ruling>" in source). A key you drop does NOT go in this table; list it in section 6 instead.
## 2. State and save fields
A table `| object | field | type | save impact |`. object = a scripts/state/ class or "derived (not saved)"; type in GDScript terms; save impact = none / additive default (corp_theme block, WH-02) / version bump. Deterministic; any randomness only via named RngService streams; integer thousandths where the draft uses them; ties by content id then node id.
## 3. Preview lines
A table `| surface | exact text pattern | "?" parts |`. Per Q19, random outcomes show as "?"; say "none" if nothing is random. Player-facing text in US English; every string is a TextDb key (give the key name `theme.<corp>.<id>`).
## 4. Tests
A table `| name | tier | assert |`. tier = fast (rules) or full (sweeps). Cover every numbered rule of the draft that survives, plus: determinism (same seed), preview equals result, Q24.1 where a death exists (an operative at 0 HP at any time is lost, the active netrun is abandoned, the raid unchanged, operatives are never killed in raids), and numbers only from config.
## 5. Q-DESIGNER disposition
A table `| # | draft line (first 6 words, verbatim) | DEFAULT or DROPPED | text |`, one row per `Q-DESIGNER:` line of the draft, numbered 1.. in the draft's order. Column 3 is exactly DEFAULT or DROPPED. DEFAULT: state the default taken and cite the ruling (THEMES_SHEET default, DECISIONS overnight defaults, or REPLAN section B / G). DROPPED: state why (a retired option, a cut mechanic, a ruling that already answers it). If a ruling and the draft differ, the ruling wins; REPLAN section G wins over THEMES_SHEET where they differ.
## 6. Reconciliation notes
Bullets: every place a ruling changed the draft; every DROPPED key as `DROPPED KEY `file.key`: reason` (one per line); every conflict between the sources (name both sides and the choice); the W2 slice rows (2.x) this table feeds. Max 25 bullets.
Rules: do not invent mechanics beyond the draft and the rulings; where both are silent choose the simplest option behind config and say so in section 6. One mechanic per corp. US English. Output only the document."""

EX_ROLE = """YOU WRITE ONE EX-01 EXPLOIT-BUILDING NETRUN RULES DRAFT (plan 2, W2, round EX01) for ONE corporation's first-pick exploit building. Output ONE markdown document, no preamble, exactly these sections (headers verbatim):
# <corp>: <building> (<Exploit> key) exploit-building netrun
## 1. Outside route
How the operative reaches the building from the street: layer count (at least 1), node kinds per layer, where the start sits (OUTSIDE every building footprint), what the route crosses (border street, plaza, rooftops...), the corp's light theme form on it. A table `| layer | node kinds | count | note |`.
## 2. Inside layers
At least 3 inside node layers (state the number), as a table `| layer | node kinds | count | note |`, ending at the exploit target. Floors / levels map to the building's real slots (spec 8.8 and 8.4). Fights use existing node kinds only (Fight, Elite, Rack, Rest, Workshop, Cache, Terminal, Mainframe...; Intel, Relay and Ambush are NOT normal-run nodes, except the Orbital Uplink Dish as a unique Relay). No new mechanics.
## 3. Exploit target
What the target node is, what taking it grants (the Exploit type key, per D5: key = the Exploit site building, one per drawn Exploit), fail/abandon behavior (Q24.1: 0 HP at any time is lost and the netrun abandoned), and what the player sees in the preview.
## 4. Slot hooks (spec 8.8, 8.4)
The corp's `key_landmarks.py` types, slot classes (frame, normal, size, tier / course / floor), allowed link geometries per step class, slots generated on demand for whatever graph the game sends (at least 7 layers of 2-4 nodes is the HQ rule; here the shape of section 1-2), the game graph being the topology (hard rule 8.4).
## 5. Lot size and clearance
A config table `| key | default | unit | note |`: lot footprint (BU), height class, clearance around the lot (default 8 BU, the border-street width, until art-pass answers), keys as `exploit_building.<corp>.<name>` style `file.key` (file = campaign_config).
## 6. Occlusion host exemption
The host building is excluded from the flatten/ghost set (all other buildings are still flattened or ghosted); occlusion never hides a route column; the occlusion rule applies to the exploit-building netrun view like every netrun view (spec 7.1 rule 0). State the host-exempt rule precisely and how the outside route's columns are protected.
## 7. Theme light form
How this corp's theme (given) shows in this netrun, light form only.
## 8. Validator and tests
Bullets: outside layers at least 1, inside layers at least 3, exactly one target, start outside every footprint, host excluded from the flatten set, 1,000 seeds produce valid shapes, same seed same shape (no gameplay stream advanced). Add 4-6 corp-specific tests (name, tier, assert).
## 9. Defaults taken
Every open point as one line `DEFAULT: <point> -> <value taken> (<why>)`. No question is left open; none may be addressed to the designer. If a fact you need is missing, state the default and mark it `(art-pass may overrule)`.
Rules: the designer ruling (exploit-building netruns ruled in, quoted in the input) and REPLAN rows 2.10 / 2.11 / 3.8 bind you. Do not invent mechanics beyond them. US English. Output only the document."""


def block_after(lines: list[str], start: int, stop_prefixes: tuple[str, ...]) -> str:
    out = [lines[start]]
    for ln in lines[start + 1:]:
        if any(ln.startswith(p) for p in stop_prefixes):
            break
        out.append(ln)
    return "\n".join(out).rstrip()


def decisions_q(ids: list[str], cap: int = 1700) -> str:
    """The DECISIONS bullets that start with '- **Q<id>' (one block each, capped)."""
    lines = read(DECISIONS).splitlines()
    got = []
    for qid in ids:
        pat = re.compile(r"^- \*\*" + re.escape(qid) + r"[\s:(*]")
        for i, ln in enumerate(lines):
            if pat.match(ln):
                got.append(block_after(lines, i, ("- **", "### ", "## "))[:cap])
                break
    return "\n".join(got)


def decisions_section(start_prefix: str, cap: int = 6000) -> str:
    lines = read(DECISIONS).splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith(start_prefix):
            return block_after(lines, i, ("### ",))[:cap]
    return f"(DECISIONS section not found: {start_prefix})"


def replan_rows(prefixes: list[str]) -> str:
    rows = []
    for ln in read(REPLAN).splitlines():
        if any(ln.startswith("| " + p) for p in prefixes):
            rows.append(ln)
    return "\n".join(rows)


def replan_section(head: str) -> str:
    lines = read(REPLAN).splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith(head):
            return block_after(lines, i, ("## ", "---"))
    return f"(REPLAN section not found: {head})"


def replan_table_row(corp_word: str) -> str:
    """The corp's row in REPLAN section B (header + that row)."""
    lines = replan_section("## B. Corporation themes").splitlines()
    out = [ln for ln in lines if ln.startswith("| Corp |") or ln.startswith("|---")]
    out += [ln for ln in lines if ln.startswith("| " + corp_word + " |")]
    return "\n".join(out)


def draft_for(cid: str, choice: str | None) -> tuple[str, str]:
    """(draft text, a note on what was sliced). Options corps keep the chosen option and the shared Q-DESIGNER block."""
    text = read(THEMES / f"{cid}.md")
    text = re.sub(r"^<!--.*?-->\s*", "", text, count=1, flags=re.S)
    if choice is None:
        return text, "full draft"
    lines = text.splitlines()
    heads = [i for i, ln in enumerate(lines) if re.match(r"## Option [A-D]\b", ln)]
    a = next(i for i in heads if lines[i].startswith(f"## Option {choice}"))
    b = next((i for i in heads if i > a), None)
    if b is None:
        b = next(i for i, ln in enumerate(lines) if i > a and ln.startswith("## "))
    q0 = next(i for i, ln in enumerate(lines) if ln.startswith("## 8."))
    q1 = next((i for i, ln in enumerate(lines) if i > q0 and ln.startswith("## ")), len(lines))
    intro = "\n".join(lines[:heads[0]])
    return (intro + "\n" + "\n".join(lines[a:b]) + "\n\n" + "\n".join(lines[q0:q1]),
            f"Option {choice} only (the other options are retired by the overnight default); shared Q-DESIGNER block kept in full")


def wh_requests(max_tokens: int) -> list[dict]:
    sheet = read(THEMES / "THEMES_SHEET.md")
    overnight = decisions_section("### 2026-10-18 — Overnight: defaults taken on open calls", 5000)
    corp_rulings = decisions_section("### 2026-10-18 — Designer rulings: corporation-wide themes", 4200)
    qs = decisions_q(["Q16", "Q24.1", "Q31", "Q34", "Q36", "Q37", "Q38", "Q39"])
    gsec = replan_section("## G. Decisions the designer may want to revisit")
    debts = [ln for ln in read(REPLAN).splitlines() if ln.startswith("- **Solace debts:**") or ln.startswith("- **Superseded theme options:**") or ln.startswith("- **Solace tolls:**")]
    out = []
    for cid, (title, choice, rows, word) in WH_CORPS.items():
        draft, note = draft_for(cid, choice)
        user = (f"Write the WH-01 table for {title}.\n"
                f"Draft file: docs/handoff/plan2/drafts/themes/{cid}.md ({note}). Output file: docs/handoff/plan2/drafts/themes/tables/{cid}.md.\n"
                + (f"Chosen option: {choice} (Meridian A PAYLOAD / Orbital A DEAD ZONE; the Q-DESIGNER lines that only concern a retired option are DROPPED, and say so).\n" if choice else "")
                + f"\n=== THE THEME DRAFT (reconcile this) ===\n{draft}\n\n"
                f"=== THEMES_SHEET (designer sheet; '(default)' marks the draft's default; unanswered lines take it) ===\n{sheet}\n\n"
                f"=== DECISIONS: overnight defaults taken on open calls ===\n{overnight}\n\n"
                f"=== DECISIONS: corporation-wide theme rulings ===\n{corp_rulings}\n\n"
                f"=== DECISIONS: rulings Q16, Q24.1, Q31, Q34, Q36-Q39 (the decision-sheet and follow-up rulings) ===\n{qs}\n\n"
                f"=== REPLAN 2026-10-19 section B row for this corp ===\n{replan_table_row(word)}\n\n"
                f"=== REPLAN section G (defaults taken; wins over THEMES_SHEET where they differ) ===\n{gsec}\n\n"
                f"=== REPLAN retire list (relevant lines) ===\n" + "\n".join(debts) + "\n\n"
                f"=== REPLAN W2 slice rows this table feeds ===\n{replan_rows(rows)}\n")
        out.append(b3.mk(f"wh01__{cid}", user, max_tokens, WH_ROLE))
    return out


def ex_requests(max_tokens: int) -> list[dict]:
    ruling = decisions_section("### 2026-10-18 — Designer ruling (relayed by the art-pass session; to confirm): exploit-building netruns", 2500)
    occl = [ln for ln in decisions_section("### 2026-10-18 — Designer rulings: corporation-wide themes", 6000).splitlines() if "Occlusion" in ln or "flatten" in ln]
    spec_lines = read(SPEC).splitlines()
    i88 = next(i for i, ln in enumerate(spec_lines) if ln.startswith("### 8.8"))
    s88 = block_after(spec_lines, i88, ("---", "## "))
    i84 = next(i for i, ln in enumerate(spec_lines) if ln.startswith("### 8.4"))
    s84 = block_after(spec_lines, i84, ("### 8.5",))[:3200]
    i71 = next(i for i, ln in enumerate(spec_lines) if ln.startswith("0. **Scope (Designer 2026-10-18)"))
    s71 = "\n".join(ln[:700] for ln in spec_lines[i71:i71 + 8])
    rows = replan_rows(["2.2 ", "2.3 ", "2.10 ", "2.11 ", "3.8 ", "3.9 "])
    gsec = replan_section("## G. Decisions the designer may want to revisit")
    d5 = [ln for ln in read(ROOT / "docs/handoff/gates/REPLAN_2026-10-16.md").splitlines() if ln.startswith("| D5 ") or ln.startswith("| B2 ")]
    secb = replan_section("## B. Corporation themes")
    out = []
    for cid, (bld, exploit, order) in EX_CORPS.items():
        hq = read(HQ / f"{cid}.md")
        j = hq.find("## 4.")
        hq = (hq[:j] if j > 0 else hq)[:9000]
        th = read(THEMES / f"{cid}.md")
        k = th.find("## 2.")
        th1 = re.sub(r"^<!--.*?-->\s*", "", th[:k] if k > 0 else th[:6000], count=1, flags=re.S)[:6500]
        word = {"rebel_cell": "REBEL_CELL"}.get(cid, cid.capitalize())
        row = [ln for ln in secb.splitlines() if ln.startswith("| " + word + " |")]
        user = (f"Write the exploit-building netrun rules draft for {word}: {bld} ({exploit} key). First pick (art-pass ca2e3707, DECISIONS 2026-10-18). Build order: {order}.\n"
                f"Output file: docs/handoff/plan2/drafts/exploit_buildings/{cid}.md.\n\n"
                f"=== DECISIONS: the exploit-building ruling (quoted) ===\n{ruling}\n\n"
                f"=== DECISIONS: occlusion ruling lines ===\n" + "\n".join(occl) + "\n\n"
                f"=== D5 / B2 (REPLAN 2026-10-16) ===\n" + "\n".join(d5) + "\n\n"
                f"=== REPLAN 2026-10-19 rows 2.2 EX-01, 2.3 EX-02, 2.10 EX-03, 2.11 EX-11, 3.8 EX-12..15, 3.9 NA-41 ===\n{rows}\n\n"
                f"=== REPLAN section G (defaults taken) ===\n{gsec}\n\n"
                f"=== PIPELINE_SPEC 8.8 ===\n{s88}\n\n=== PIPELINE_SPEC 8.4 (graph onto slots) ===\n{s84}\n\n=== PIPELINE_SPEC 7.1 rule 0 (occlusion scope) ===\n{s71}\n\n"
                f"=== This corp's theme row (REPLAN B) ===\n" + "\n".join(row) + "\n\n"
                f"=== This corp's theme draft, rules summary (docs/handoff/plan2/drafts/themes/{cid}.md, up to section 2) ===\n{th1}\n\n"
                f"=== This corp's HQ draft (docs/handoff/plan2/drafts/hq/{cid}.md, sections before the node kit) ===\n{hq}\n")
        out.append(b3.mk(f"ex01__{cid}", user, max_tokens, EX_ROLE))
    return out


def ingest(d: Path, key: str) -> None:
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
    TABLES.mkdir(parents=True, exist_ok=True)
    EXDIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in client.messages.batches.results(bid):
        kind, cid = r.custom_id.split("__", 1)
        if r.result.type != "succeeded":
            rows.append({"id": r.custom_id, "status": r.result.type, "cost": 0.0})
            continue
        m = r.result.message
        text = "".join(bl.text for bl in m.content if bl.type == "text").strip()
        u = m.usage
        cw, cr = u.cache_creation_input_tokens or 0, u.cache_read_input_tokens or 0
        cost = (u.input_tokens * 1.0 + cw * 1.25 + cr * 0.10 + u.output_tokens * 5.0) / 1e6
        status = "ok" if m.stop_reason == "end_turn" else f"TRUNCATED ({m.stop_reason})"
        tag = "WH-01" if kind == "wh01" else "EX-01"
        head = (f"<!-- {tag} draft via Message Batches, {m.model}, batch {bid}, custom_id {r.custom_id}; status {status}; "
                f"tokens in {u.input_tokens} cache-write {cw} cache-read {cr} out {u.output_tokens}; cost ${cost:.3f}. DRAFT. -->\n\n")
        dest = (TABLES if kind == "wh01" else EXDIR) / f"{cid}.md"
        dest.write_text(head + text + "\n", encoding="utf-8", newline="\n")
        rows.append({"id": r.custom_id, "status": status, "cost": cost, "chars": len(text), "out": u.output_tokens})
    (d / "ingest_summary.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    for x in sorted(rows, key=lambda x: x["id"]):
        print(x["id"], x["status"], x.get("chars"), x.get("out"), f"${x['cost']:.3f}")
    print(f"TOTAL ${sum(x['cost'] for x in rows):.3f}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="", choices=["", "wh01", "ex01"])
    ap.add_argument("--corps", default="", help="comma list of corps (a re-run of truncated ones)")
    ap.add_argument("--key", default="w2", help="batch id key in batch_ids.json (use another for a re-run)")
    ap.add_argument("--max-tokens-wh", type=int, default=20000)
    ap.add_argument("--max-tokens-ex", type=int, default=14000)
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--ingest", action="store_true")
    args = ap.parse_args()
    d = Path(args.out)
    d.mkdir(parents=True, exist_ok=True)
    if args.ingest:
        ingest(d, args.key)
        return 0
    reqs: list[dict] = []
    if args.only in ("", "wh01"):
        reqs += wh_requests(args.max_tokens_wh)
    if args.only in ("", "ex01"):
        reqs += ex_requests(args.max_tokens_ex)
    if args.corps:
        keep = set(args.corps.split(","))
        reqs = [r for r in reqs if r["custom_id"].split("__", 1)[1] in keep]
    with (d / "w2.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for r in reqs:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    unc = sum(b3.est_tokens(r["params"]["messages"][0]["content"] + r["params"]["system"][-1]["text"]) for r in reqs)
    cap_out = sum(r["params"]["max_tokens"] for r in reqs)
    exp = (unc * 1.0 + b3.COMMON_TOKENS * 1.25 + b3.COMMON_TOKENS * len(reqs) * 0.1 + len(reqs) * 9000 * 5.0) / 1e6
    worst = (unc * 1.0 + b3.COMMON_TOKENS * 1.25 + b3.COMMON_TOKENS * len(reqs) * 0.1 + cap_out * 5.0) / 1e6
    biggest = max(b3.est_tokens(r["params"]["messages"][0]["content"] + r["params"]["system"][-1]["text"]) for r in reqs)
    print(f"{len(reqs)} requests, ~{unc:,} uncached input tokens (largest ~{biggest:,}), expected ${exp:.2f}, cap-worst ${worst:.2f}")
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
