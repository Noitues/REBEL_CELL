"""Revise the corporation theme drafts with the designer's THEMES_SHEET answers (Message Batches, Sonnet), round tag THEMES2.

    python tools/batch/build_themes2.py --out <dir>             # write <dir>/themes2.jsonl, print the estimate
    ... --submit      # also submit; id saved to <dir>/batch_ids.json (key themes2)
    ... --ingest      # wait, fetch, write docs/handoff/plan2/drafts/themes/v2/<corp>.md and a summary

Inputs: the current draft docs/handoff/plan2/drafts/themes/<corp>.md and the DECISIONS entry
"2026-10-19 — Designer rulings: corporation theme sheet". Credentials: ANTHROPIC_API_KEY (or the Windows user variable); never
printed. Never run Python from stdin on this machine.
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

SRC = ROOT / "docs/handoff/plan2/drafts/themes"
OUT_DIR = SRC / "v2"

CORPS = {
    "meridian": "The designer chose ALL FOUR options together: A PAYLOAD + B CUSTOMS + C DELIVERY WINDOW + D SUPPLY LINE. Merge them "
                "into ONE coherent theme with one identity (logistics / freight): say which part lives in the street light form, the HQ "
                "full form and the raid hook, how they interact, and how they are introduced in difficulty order so the player is not "
                "hit by four systems at once (the O4-style escalation over the campaign is allowed). M1 the theme may cost power; M2 "
                "the faster-finish bonus is good; M3 surrendered items are lost permanently; M4 the Grid clear order becomes a "
                "strategic choice.",
    "orbital": "The designer chose options A DEAD ZONE + B OVERWATCH together. Merge into ONE theme (satellites and comms: blackouts "
               "AND telegraphed orbital strikes). O1 the theme may lock nudges; O2 strikes never ignore SANDBOX and a sandboxed "
               "slice / node is a legal strike target; O3 player nodes only; O4 the theme is strong in every part of the game "
               "(street, HQ, raid) and GROWS IN INTENSITY or UNLOCKS THEME PHASES over the campaign: define the escalation (by "
               "campaign tier / ICE / Exploits taken), deterministic and previewable; O5 permanent run costs are OK (keep or "
               "adapt Kessler-style debris as a run cost if it fits).",
    "solace": "Revise THE BLOOM (already built on a branch with the old defaults; say exactly what changes). S1 raid infection is a "
              "CAMPAIGN figure that may diminish toward zero (define the decay / reduction rule, config); S2 Heat also speeds the "
              "street Bloom; S3 NO exemption: elites, mini-bosses and bosses pay the per-turn cost (punishing long fights); S4 HQ "
              "Waiting Room debts are cut (orchestrator call); S5 NO T1 free dose; S6 EVERY Exploit (Intel, Breach, Virus) slows "
              "the Bloom: give each its own form or a stacking pace cut.",
    "halcyon": "H1 keep ALL the HQ extras (Alert and Lockdown, Annex rooms, Stall, Cut the Power); H2 the Eye moves every CAMPAIGN "
               "TURN (a failed netrun is a campaign turn); H3 level 2 puts the Blade rider on every normal fight; H4 non-fight HQ "
               "nodes inside the eye are SHUTTERED; H5 threats inside the sector hit harder.",
    "rebel_cell": "R1 three operatives; R2 an operative lost in the route phase is REPLACED from the backup roster if one exists, "
                  "otherwise the whole run is abandoned (define how the replacement enters the lane); R3 NO lead limit between "
                  "lanes (keep one clock: say what still couples the lanes); R4 default lane effects; R5 the regroup heal scales "
                  "with ICE: full heal at ICE 0, about 20 % at ICE 5-7 (linear in between, 20 % floor above; config).",
    "aurelian": "A1 HQ only; A2 default (1 step, Intel extends to 4); A3 random order: ANY Exploit can unlock ANY gate; A4 the arch "
                "is cosmetic (no Cache); A5 same layout on retry; A6 the full 9-level HQ.",
    "tethys": "T1 default (street start Head by tier); T2 a raid continues from the last netrun's Head; T3 Submerged mutes turrets "
              "only; T4 NO Dry salvage bonus; T5 'wait for the tide' costs Heat; T6 Divert is permanent for the run.",
}

ROLE = """YOU REVISE ONE CORPORATION THEME RULES DRAFT WITH THE DESIGNER'S ANSWERS (plan 2, round THEMES2). Output ONE markdown
document, no preamble, with exactly these sections:
# <corp>: <theme name> (v2)
## 0. What changed from v1 (bullets: each designer answer -> the rule it changes; for a corp already built, what code must change).
## 1. Rules: street (light form), HQ (full form), raid (one hook), and campaign escalation if any. Numbered, each testable.
## 2. State and save fields (names, types, where they live; deterministic; RngService streams only; save impact).
## 3. Preview (exact where nothing is random; "?" only where a stream is read, per Q19).
## 4. Numbers (placeholders, each `config: <file>.<key>`).
## 5. Tests to write (name, tier fast/full, what it asserts).
## 6. Build slices (ordered list of rules / UI slices with size S/M/L and dependencies; art-pass owns the 3D look).
## 7. Q-DESIGNER (lines that start exactly `Q-DESIGNER:`, one sentence each, max 6, each with your recommended default in
parentheses; ONLY calls the designer alone can make, raised by the answers or by merging options).
Binding: the designer's answers are rulings; keep the existing designer rulings in the v1 draft (Q24.1 death: 0 HP or caught = operative
lost, netrun abandoned, raid unchanged, operatives never killed in raids; Q34 Sync Strike; Q19 preview). Readable in the preview; reuse
over new code; introduce in difficulty order. Do not invent beyond the answers and the v1 draft; where silent, choose the simplest
option behind config and raise it as Q-DESIGNER. US English in every player-facing string."""


def rulings() -> str:
    t = read(ROOT / "docs/DECISIONS.md")
    a = t.index("### 2026-10-19 — Designer rulings: corporation theme sheet")
    b = t.index("\n### ", a + 10)
    return t[a:b]


def build(only: str = "", mx: int = 16000) -> list[dict]:
    rul = rulings()
    out = []
    for cid, direction in CORPS.items():
        if only and cid not in only.split(","):
            continue
        v1 = read(SRC / f"{cid}.md")
        user = (f"Revise the theme draft for {cid}.\n\nDESIGNER ANSWERS FOR THIS CORP (binding):\n{direction}\n\n"
                f"=== DECISIONS: the 2026-10-19 theme-sheet rulings (all corps) ===\n{rul}\n\n"
                f"=== v1 draft ({cid}) ===\n{v1}\n")
        out.append(b3.mk(f"themes2__{cid}", user, mx, ROLE))
    return out


def ingest(d: Path, key: str = "themes2") -> None:
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
        head = (f"<!-- THEMES2 draft via Message Batches, {m.model}, batch {bid}, custom_id {r.custom_id}; status {status}; "
                f"tokens in {u.input_tokens} cache-write {cw} cache-read {cr} out {u.output_tokens}; cost ${cost:.3f}. "
                f"v2: designer answers 2026-10-19 applied. -->\n\n")
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
    ap.add_argument("--only", default="")
    ap.add_argument("--key", default="themes2")
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--ingest", action="store_true")
    args = ap.parse_args()
    d = Path(args.out)
    d.mkdir(parents=True, exist_ok=True)
    if args.ingest:
        ingest(d, args.key)
        return 0
    reqs = build(args.only, args.max_tokens)
    with (d / "themes2.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for r in reqs:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    unc = sum(b3.est_tokens(r["params"]["messages"][0]["content"]) for r in reqs)
    cost = (unc * 1.0 + b3.COMMON_TOKENS * 1.25 + b3.COMMON_TOKENS * len(reqs) * 0.1 + len(reqs) * 10000 * 5.0) / 1e6
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
