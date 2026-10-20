"""Build, submit and ingest the W3 batch-lane drafts (Message Batches, Sonnet 5.5): RD-01 (raid operative design, one request per operative class) and ST-01 (status audit, Q40).

    python tools/batch/build_w3_drafts.py --out <dir>                  # write <dir>/w3.jsonl, print the estimate
    python tools/batch/build_w3_drafts.py --out <dir> --submit         # also submit; id saved to <dir>/batch_ids.json
    python tools/batch/build_w3_drafts.py --out <dir> --ingest         # wait, fetch, write the drafts, print the cost

Outputs:
    RD-01: docs/handoff/plan2/drafts/raid_operatives/<class>.md   (8 operative classes in content/classes/)
    ST-01: docs/handoff/plan2/drafts/status_audit/ST01.md          (one audit, Q40)
Options: --only rd01 | st01 (a subset), --max-tokens-rd N, --max-tokens-st N, --key NAME (batch id key for a re-run).
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

RAID_OPS = ROOT / "docs/handoff/plan2/drafts/raid_operatives"
STATUS_AUDIT = ROOT / "docs/handoff/plan2/drafts/status_audit"
CLASSES = ROOT / "content/classes"
UNIFIED = ROOT / "docs/handoff/plan2/drafts/raids/unified.md"
GDD = ROOT / "docs/GDD.md"
DECISIONS = ROOT / "docs/DECISIONS.md"
RC = ROOT / "scripts/data/rc.gd"
CORE = ROOT / "scripts/core"

# RD-01: the operative classes. Fence is NOT a class (the Black Market trade-in, DECISIONS Q42).
RD_CLASSES = ["botnet", "breaker", "ghost", "hivemind", "overclocker", "phantom", "rigger", "wrecker"]

# GDD 5.2 class rows (the four classes the GDD table lists); other classes read from their .tres only.
GDD_CLASS_ROW = {"botnet": "Botnet", "breaker": "Breaker", "ghost": "Ghost", "rigger": "Rigger"}

RD_ROLE = """YOU WRITE ONE RD-01 RAID OPERATIVE DESIGN DRAFT (plan 2, W3, round RD01) for ONE operative class. The raid design pass (designer Q14, DECISIONS Q42) is the unified raid model in the input: four rules R1 EXPOSED spotlight, R2 encrypted routes, R3 vehicle types, R4 Heat-scaled second wave with an ULTIMATUM (the Schematics sink). Your draft says what this class DOES in a raid (its raid role), not how it fights in a netrun.
Binding rules, stated in the draft and checked in section 5:
- Q24.1: operatives are never killed in raids. An operative at 0 HP at any time, for any reason, is lost and the active netrun is abandoned; the raid is unchanged.
- Q42 defaults: the Schematics sink is paid once per raid; defenses are shared (every operative in the cell defends the same network, no per-operative copy); no re-setup mid-raid.
Output ONE markdown document, no preamble, exactly these sections (headers verbatim):
# <Class>: raid operative design
## 1. Raid role
One paragraph plus bullets: what the operative contributes in the raid setup phase and the playout (which of R1-R4 it touches, the station bonus from the input if given, the Hub Core passive read as a raid effect only where the input supports it). No new mechanic: if the class's netrun kit has no raid analogue, say so and give the simplest role behind config.
## 2. Numbers
A table `| key | default | unit / note |`. Every number is written as a placeholder in the key cell: `config: campaign_config.<key>` (or `config: <file>.<key>` for another content file). Use the GDD 7 / unified-draft key names where they exist; a new key is named `config: campaign_config.raid_<class>_<name>`. Defaults are concrete numbers; the unit column says the unit. No literal number may appear in the rules text outside this table.
## 3. Preview lines
A table `| surface | exact text pattern | "?" parts |`. Per Q19 random outcomes show as "?"; say "none" if nothing is random. Player-facing text in US English; each string is a TextDb key `raid.<class>.<id>`.
## 4. Tests
A table `| name | tier | assert |`. tier = fast (rules) or full (sweeps). Cover every numbered rule of the role, plus: determinism (same seed, same result), preview equals result, Q24.1 (an operative at 0 HP is lost and the netrun abandoned; the raid itself is unchanged; no operative is killed by a raid step), Q42 (Schematics sink once per raid; shared defenses; no re-setup), numbers only from config.
## 5. Binding rule check
Three bullets, one per rule (Q24.1, Q42 sink, Q42 shared defenses / no re-setup), each stating how this draft satisfies it.
## 6. Q-DESIGNER lines
At most 4 lines, each exactly one line of the form:
Q-DESIGNER: <one question> | DEFAULT: <the recommended default, concrete>
Rules: do not invent mechanics beyond the unified raid draft, the GDD, and the rulings above; where the sources are silent choose the simplest option behind config and say so in section 1. One class per document. US English. Output only the document."""

ST_ROLE = """YOU WRITE THE ST-01 STATUS AUDIT (plan 2, W3, round ST01, designer Q40). Question: compare Slay-the-Spire-style statuses against the game's existing statuses and say, for each, whether it is a real gap worth a new status. Output ONE markdown document, no preamble, exactly these sections (headers verbatim):
# Status audit (ST-01, Q40)
## 1. Existing statuses
A table `| status | rule (one line) | where in code |`. Source of truth is the code: scripts/data/rc.gd `enum Status` (NONE, CORRUPTED, OVERCLOCKED, ENCRYPTED, PARASITE, OUTPUT_DOWN, TIER_DOWN), where PARASITE is RETIRED (today it is OUTPUT_DOWN x2, plan 2 N8 / R8) and STORED_STATUSES lists the five live ones. The Q40 ruling in DECISIONS names only OUTPUT_DOWN, TIER_DOWN and CORRUPTED; the code also has OVERCLOCKED and ENCRYPTED, and the GDD 2.9 table lists CORRUPTED, OVERCLOCKED and ENCRYPTED. Say in one line which list is right and why (the code wins for what is live).
## 2. Audit
A table `| status | nearest existing | gap yes/no | cost | risk |`. Rows: poison, burn, weak, frail, vulnerable, strength, dexterity, thorns, artifact, intangible, and up to 6 more similar Slay-the-Spire-style statuses you judge relevant (name them). Every row ties to an existing system: name the nearest existing Status value, EffectType, CLEANSE mode, config key (campaign_config.status_stack_cap, parasite_output_down_stacks, and so on) or combat rule (the stack model in combat_resolver.gd: OUTPUT_DOWN takes a share per stack, TIER_DOWN lowers the tier, OVERCLOCKED is 1.5x, CORRUPTED self-damages and costs RAM). A row with gap yes must say which existing system cannot express it, in one line. cost = the work in one short phrase (config only / new effect type / new enum value with save migration / new combat rule with tests). risk = one short phrase (determinism, preview parity, save, balance, UI).
## 3. Recommendation
Default: no new status ships. One paragraph: the rows whose gap is real, and the smallest change that would close each one through an existing system (no new enum value unless no existing system can express it). Numbers are config placeholders `config: campaign_config.<key>`.
## 4. Q-DESIGNER lines
At most 4 lines, each exactly one line of the form:
Q-DESIGNER: <one question> | DEFAULT: <the recommended default, concrete>
Rules: no new mechanics beyond the audit; determinism (no RNG added); no magic numbers; US English; output only the document."""


def block_after(lines: list[str], start: int, stop_prefixes: tuple[str, ...]) -> str:
    out = [lines[start]]
    for ln in lines[start + 1:]:
        if any(ln.startswith(p) for p in stop_prefixes):
            break
        out.append(ln)
    return "\n".join(out).rstrip()


def decisions_q(ids: list[str], cap: int = 1500) -> str:
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


def gdd_raid_sections() -> str:
    """GDD lines that mention raids (section 4.4 and section 7), capped."""
    lines = read(GDD).splitlines()
    keep = []
    for i, ln in enumerate(lines):
        if "Raid" in ln or "raid" in ln:
            keep.append(f"{i + 1}: {ln[:400]}")
    s7 = next((i for i, ln in enumerate(lines) if ln.startswith("## 7. Cell Defense")), None)
    body = ""
    if s7 is not None:
        body = "\n".join(ln[:400] for ln in lines[s7:s7 + 40])
    return "\n".join(keep[:60]) + "\n\n--- GDD 7 Cell Defense (first 40 lines) ---\n" + body


def class_excerpt(cid: str) -> str:
    """The class .tres without ext_resource / sub_resource plumbing (first 90 useful lines, capped)."""
    lines = read(CLASSES / f"{cid}.tres").splitlines()
    keep = [ln[:200] for ln in lines if ln.strip() and not ln.startswith("[ext_resource") and not ln.startswith("[sub_resource")]
    return "\n".join(keep[:90])


def rc_status_enum() -> str:
    lines = read(RC).splitlines()
    out = []
    for i, ln in enumerate(lines):
        if ln.startswith("enum Status") or ln.startswith("const UNCAPPED_STATUSES") or ln.startswith("const STORED_STATUSES"):
            out.append(ln[:300])
    return "\n".join(out)


def core_status_lines() -> str:
    pat = re.compile(r"OUTPUT_DOWN|TIER_DOWN|CORRUPTED|OVERCLOCKED|ENCRYPTED|PARASITE")
    out = []
    for f in sorted(CORE.rglob("*.gd")):
        for i, ln in enumerate(read(f).splitlines(), 1):
            if pat.search(ln):
                out.append(f"{f.relative_to(ROOT).as_posix()}:{i}: {ln.strip()[:220]}")
    return "\n".join(out[:120])


def rd_requests(max_tokens: int) -> list[dict]:
    unified = read(UNIFIED)
    unified = re.sub(r"^<!--.*?-->\s*", "", unified, count=1, flags=re.S)
    q242 = decisions_q(["Q24.1", "Q42", "Q14", "Q19"])
    gdd = gdd_raid_sections()
    out = []
    for cid in RD_CLASSES:
        row = ""
        if cid in GDD_CLASS_ROW:
            gdd_lines = read(GDD).splitlines()
            row = "\n".join(ln for ln in gdd_lines if ln.startswith("| ") and GDD_CLASS_ROW[cid] in ln and "|" in ln)
        if not row:
            row = "(no GDD 5.2 row for this class; use the .tres excerpt below)"
        user = (f"Write the RD-01 raid operative design draft for the {cid.capitalize()} class.\n"
                f"Output file: docs/handoff/plan2/drafts/raid_operatives/{cid}.md.\n"
                f"Class data file: content/classes/{cid}.tres (excerpt below; ids and values are read from it, numbers become config placeholders).\n\n"
                f"=== THE UNIFIED RAID DRAFT (docs/handoff/plan2/drafts/raids/unified.md; the rules this operative plugs into) ===\n{unified}\n\n"
                f"=== GDD raid lines (grep 'Raid' in docs/GDD.md, section 4.4 and section 7) ===\n{gdd}\n\n"
                f"=== DECISIONS rulings: Q24.1, Q42, Q14, Q19 ===\n{q242}\n\n"
                f"=== GDD 5.2 class row ===\n{row}\n\n"
                f"=== {cid}.tres excerpt ===\n{class_excerpt(cid)}\n")
        out.append(b3.mk(f"rd01__{cid}", user, max_tokens, RD_ROLE))
    return out


def st_request(max_tokens: int) -> dict:
    gdd_lines = read(GDD).splitlines()
    i = next((k for k, ln in enumerate(gdd_lines) if ln.startswith("### 2.9 Statuses")), 0)
    gdd_status = block_after(gdd_lines, i, ("### 2.10",))
    q40 = decisions_q(["Q40", "Q36", "Q24.1"])
    user = (f"Write the ST-01 status audit (Q40).\n"
            f"Output file: docs/handoff/plan2/drafts/status_audit/ST01.md.\n"
            f"Compare these Slay-the-Spire-style statuses against the game's existing ones: poison, burn, weak, frail, vulnerable, strength, dexterity, thorns, artifact, intangible, and similar.\n\n"
            f"=== scripts/data/rc.gd status enum and stored-status lists ===\n{rc_status_enum()}\n\n"
            f"=== GDD 2.9 Statuses (docs/GDD.md) ===\n{gdd_status}\n\n"
            f"=== DECISIONS Q40 (status types), Q36, Q24.1 ===\n{q40}\n\n"
            f"=== scripts/core grep: OUTPUT_DOWN, TIER_DOWN, CORRUPTED, OVERCLOCKED, ENCRYPTED, PARASITE (file:line: text, capped) ===\n{core_status_lines()}\n")
    return b3.mk("st01__audit", user, max_tokens, ST_ROLE)


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
    RAID_OPS.mkdir(parents=True, exist_ok=True)
    STATUS_AUDIT.mkdir(parents=True, exist_ok=True)
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
        tag = "RD-01" if kind == "rd01" else "ST-01"
        head = (f"<!-- {tag} draft via Message Batches, {m.model}, batch {bid}, custom_id {r.custom_id}; status {status}; "
                f"tokens in {u.input_tokens} cache-write {cw} cache-read {cr} out {u.output_tokens}; cost ${cost:.3f}. DRAFT. -->\n\n")
        dest = (RAID_OPS / f"{cid}.md") if kind == "rd01" else (STATUS_AUDIT / "ST01.md")
        dest.write_text(head + text + "\n", encoding="utf-8", newline="\n")
        rows.append({"id": r.custom_id, "status": status, "cost": cost, "chars": len(text), "out": u.output_tokens})
    (d / "ingest_summary.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    for x in sorted(rows, key=lambda x: x["id"]):
        print(x["id"], x["status"], x.get("chars"), x.get("out"), f"${x['cost']:.3f}")
    print(f"TOTAL ${sum(x['cost'] for x in rows):.3f}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="", choices=["", "rd01", "st01"])
    ap.add_argument("--key", default="w3", help="batch id key in batch_ids.json (use another for a re-run)")
    ap.add_argument("--max-tokens-rd", type=int, default=9000)
    ap.add_argument("--max-tokens-st", type=int, default=9000)
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--ingest", action="store_true")
    args = ap.parse_args()
    d = Path(args.out)
    d.mkdir(parents=True, exist_ok=True)
    if args.ingest:
        ingest(d, args.key)
        return 0
    reqs: list[dict] = []
    if args.only in ("", "rd01"):
        reqs += rd_requests(args.max_tokens_rd)
    if args.only in ("", "st01"):
        reqs.append(st_request(args.max_tokens_st))
    with (d / "w3.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for r in reqs:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    unc = sum(b3.est_tokens(r["params"]["messages"][0]["content"] + r["params"]["system"][-1]["text"]) for r in reqs)
    cap_out = sum(r["params"]["max_tokens"] for r in reqs)
    exp = (unc * 1.0 + b3.COMMON_TOKENS * 1.25 + b3.COMMON_TOKENS * len(reqs) * 0.1 + len(reqs) * 6000 * 5.0) / 1e6
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
