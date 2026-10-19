"""Lint the WH-01 theme tables (and, with --ex, the EX-01 exploit-building drafts).

    python tools/batch/lint_w2_tables.py            # WH-01: tables/<corp>.md against themes/<corp>.md
    python tools/batch/lint_w2_tables.py --ex       # EX-01 structure checks too

WH-01 checks, per playable corp (solace, halcyon, rebel_cell, orbital, meridian):
  1. every `config:` key of the theme draft (the chosen option only, for Meridian / Orbital) appears in the table's
     "## 1. Config keys" section, or is listed in "## 6" as `DROPPED KEY`;
  2. every `Q-DESIGNER:` line of the draft has a row in "## 5" marked DEFAULT or DROPPED with a reason, and the
     quoted first words match the draft line;
  3. Solace: no debt / toll key is left in section 1 (REPLAN F: Solace debts cut, S4).
Exit code 0 = clean, 1 = findings. Keys match on the part after the last dot.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
THEMES = ROOT / "docs/handoff/plan2/drafts/themes"
TABLES = THEMES / "tables"
EXDIR = ROOT / "docs/handoff/plan2/drafts/exploit_buildings"
WH_CORPS = {"solace": None, "halcyon": None, "rebel_cell": None, "orbital": "A", "meridian": "A"}
EX_CORPS = ["solace", "halcyon", "rebel_cell", "orbital", "meridian", "aurelian", "tethys"]
DEBT_WORDS = ("debt", "copay", "co_pay", "referral", "audit", "quarantine", "toll", "waiting_room", "pressure_counter")
KEY_RE = re.compile(r"`([a-z][a-z0-9_]*(?:\.[a-z0-9_]+)+)`")
CFG_SLASH_RE = re.compile(r"config:\s*`?([a-z0-9_.]+(?:\s*/\s*[a-z0-9_.]+)*)`?")


def strip_comment(t: str) -> str:
    return re.sub(r"^<!--.*?-->\s*", "", t, count=1, flags=re.S)


def chosen_slice(text: str, choice: str | None) -> str:
    """Options corps: the chosen option plus the shared block (as the batch fed it)."""
    if choice is None:
        return text
    lines = text.splitlines()
    heads = [i for i, ln in enumerate(lines) if re.match(r"## Option [A-D]\b", ln)]
    a = next(i for i in heads if lines[i].startswith(f"## Option {choice}"))
    b = next((i for i in heads if i > a), len(lines))
    q0 = next(i for i, ln in enumerate(lines) if ln.startswith("## 8."))
    return "\n".join(lines[:heads[0]] + lines[a:b] + lines[q0:])


def draft_keys(text: str) -> set[str]:
    """Key names (after the last dot) named by `config:` phrases or backticked dotted tokens on lines that mention config."""
    keys: set[str] = set()
    for ln in text.splitlines():
        if "config" not in ln.lower():
            continue
        for m in KEY_RE.finditer(ln):
            tok = m.group(1)
            if tok.split(".")[0] in ("campaign_config",) or "config" in ln.lower():
                keys.add(tok.rsplit(".", 1)[1])
        for m in CFG_SLASH_RE.finditer(ln):
            for part in re.split(r"\s*/\s*", m.group(1)):
                part = part.strip(".")
                if part and ("." in part or part.islower()):
                    keys.add(part.rsplit(".", 1)[-1])
    # an exact-word filter: drop file-ish names that are not keys
    return {k for k in keys if k not in ("tres", "md", "gd", "csv", "json", "cfg")}


def section(text: str, num: int) -> str:
    m = re.search(rf"^## {num}\..*?$", text, re.M)
    if not m:
        return ""
    n = re.search(r"^## \d+\.", text[m.end():], re.M)
    return text[m.end():m.end() + n.start()] if n else text[m.end():]


def table_rows(sec: str) -> list[list[str]]:
    rows = []
    for ln in sec.splitlines():
        s = ln.strip()
        if s.startswith("|") and not re.match(r"^\|[\s:|-]+\|?$", s):
            rows.append([c.strip() for c in s.strip("|").split("|")])
    return rows[1:] if rows else []  # drop the header row


def words(s: str, n: int) -> list[str]:
    s = re.sub(r"[`*_\"'.,:;?!()\[\]]", " ", s.lower())
    return s.split()[:n]


def lint_wh(cid: str, choice: str | None) -> list[str]:
    errs: list[str] = []
    dp, tp = THEMES / f"{cid}.md", TABLES / f"{cid}.md"
    if not tp.exists():
        return [f"{cid}: table file missing ({tp.relative_to(ROOT)})"]
    draft = chosen_slice(strip_comment(dp.read_text(encoding="utf-8")), choice)
    table = strip_comment(tp.read_text(encoding="utf-8"))
    for n in range(1, 7):
        if not section(table, n):
            errs.append(f"{cid}: section ## {n}. missing or empty")
    keys = draft_keys(draft)
    sec1 = section(table, 1)
    sec1_keys = {m.group(1).rsplit(".", 1)[-1] for m in KEY_RE.finditer(sec1)}
    sec1_text = sec1
    dropped = {m.group(1).rsplit(".", 1)[-1] for m in re.finditer(r"DROPPED KEY\s+`([a-z0-9_.]+)`", section(table, 6))}
    for k in sorted(keys):
        if k in sec1_keys or k in dropped:
            continue
        if re.search(rf"\b{re.escape(k)}\b", sec1_text):
            continue
        errs.append(f"{cid}: config key `{k}` of the draft is not in the table (section 1) or DROPPED KEY (section 6)")
    # Q-DESIGNER lines
    qlines = [ln.strip() for ln in draft.splitlines() if ln.strip().startswith("Q-DESIGNER:")]
    rows = table_rows(section(table, 5))
    if len(rows) != len(qlines):
        errs.append(f"{cid}: {len(qlines)} Q-DESIGNER lines in the draft, {len(rows)} rows in section 5")
    for i, ql in enumerate(qlines):
        if i >= len(rows):
            errs.append(f"{cid}: Q-DESIGNER #{i + 1} has no row: {ql[:70]}")
            continue
        r = rows[i]
        if len(r) < 4:
            errs.append(f"{cid}: section 5 row {i + 1} has {len(r)} columns, need 4")
            continue
        status = re.sub(r"[`*]", "", r[2]).strip()
        if status not in ("DEFAULT", "DROPPED"):
            errs.append(f"{cid}: Q-DESIGNER #{i + 1} status is {status!r}, need DEFAULT or DROPPED")
        if len(r[3]) < 12:
            errs.append(f"{cid}: Q-DESIGNER #{i + 1} has no default / reason text")
        want = words(ql[len("Q-DESIGNER:"):], 4)
        if words(r[1], 8)[:4] != want and not all(w in words(r[1], 12) for w in want):
            errs.append(f"{cid}: Q-DESIGNER #{i + 1} quoted words do not match the draft line ({' '.join(want)})")
    if cid == "solace":
        for k in sorted(sec1_keys):
            if any(w in k for w in DEBT_WORDS):
                errs.append(f"solace: debt / toll key `{k}` left in section 1 (REPLAN F: cut, S4)")
    return errs


def lint_ex(cid: str) -> list[str]:
    errs: list[str] = []
    p = EXDIR / f"{cid}.md"
    if not p.exists():
        return [f"ex {cid}: file missing"]
    t = strip_comment(p.read_text(encoding="utf-8"))
    for n in range(1, 10):
        if not section(t, n):
            errs.append(f"ex {cid}: section ## {n}. missing or empty")
    inside = [r for r in table_rows(section(t, 2)) if r and r[0]]
    if len(inside) < 3:
        errs.append(f"ex {cid}: {len(inside)} inside layer rows (need at least 3)")
    if not table_rows(section(t, 1)):
        errs.append(f"ex {cid}: outside route has no layer rows")
    if "8 BU" not in section(t, 5) and not re.search(r"\b8(\.0)?\b", section(t, 5)):
        errs.append(f"ex {cid}: clearance default 8 BU not stated in section 5")
    if "Q-DESIGNER" in t:
        errs.append(f"ex {cid}: leftover Q-DESIGNER text (open points must be defaulted)")
    if not re.search(r"^[-* ]*DEFAULT:", section(t, 9), re.M):
        errs.append(f"ex {cid}: section 9 has no DEFAULT: lines")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ex", action="store_true", help="also check the EX-01 drafts")
    ap.add_argument("--only", default="", help="comma list of corps")
    args = ap.parse_args()
    only = set(args.only.split(",")) if args.only else None
    errs: list[str] = []
    for cid, choice in WH_CORPS.items():
        if only and cid not in only:
            continue
        e = lint_wh(cid, choice)
        errs += e
        nk = len(draft_keys(chosen_slice(strip_comment((THEMES / f'{cid}.md').read_text(encoding='utf-8')), choice)))
        print(f"WH-01 {cid}: {nk} draft keys, {'OK' if not e else str(len(e)) + ' finding(s)'}")
    if args.ex:
        for cid in EX_CORPS:
            if only and cid not in only:
                continue
            e = lint_ex(cid)
            errs += e
            print(f"EX-01 {cid}: {'OK' if not e else str(len(e)) + ' finding(s)'}")
    for e in errs:
        print("  FINDING:", e)
    print("LINT", "CLEAN" if not errs else f"{len(errs)} FINDINGS")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
