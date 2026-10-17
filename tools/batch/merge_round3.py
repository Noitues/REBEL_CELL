"""Merge the round-3 Haiku shards locally (docs/handoff/plan2/BATCH_ROUND3.md).

    python tools/batch/merge_round3.py triage      # drafts/triage/*.md -> drafts/triage/BLOCKERS.md
    python tools/batch/merge_round3.py questions   # drafts/questions/*.md -> drafts/questions/DESIGNER_QUESTIONS.md

Shard lines (pipe separated) are written by the Haiku extractors; this script only groups and ranks, deterministically.
Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import difflib
import re
import sys
from collections import defaultdict
from pathlib import Path

DRAFTS = Path(__file__).resolve().parent.parent.parent / "docs/handoff/plan2/drafts"
HEADER = re.compile(r"^<!--.*?-->\s*", re.S)


def body(p: Path) -> str:
    return HEADER.sub("", p.read_text(encoding="utf-8"), count=1)


def rows(p: Path, tag: str) -> list[list[str]]:
    out = []
    for line in body(p).splitlines():
        line = line.strip().strip("`")
        if not line.startswith(tag):
            continue
        parts = [x.strip() for x in line.split("|")]
        if len(parts) >= 3:
            out.append(parts)
    return out


def triage() -> None:
    d = DRAFTS / "triage"
    per: dict[str, list[tuple[str, str]]] = {}
    for f in sorted(d.glob("*.md")):
        if f.name == "BLOCKERS.md":
            continue
        r = [(x[1], x[2]) for x in rows(f, "BLOCKER")]
        per[f.stem] = r
    ranked = sorted(per.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    themes: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for cid, rs in per.items():
        for text, theme in rs:
            themes[theme].append((cid, text))
    total = sum(len(v) for v in per.values())
    lines = ["# Critic BLOCKER triage (round 3)", "",
             f"{total} blockers over {len(per)} critic files ({sum(1 for v in per.values() if v)} with at least one). "
             "Source: `critic/<id>.md`; extracted by Haiku, merged by `tools/batch/merge_round3.py`.", "",
             "## Drafts ranked by blocker count", "", "| rank | critic file | draft id | blockers |", "|---|---|---|---|"]
    n = 0
    for cid, rs in ranked:
        if not rs:
            continue
        n += 1
        lines.append(f"| {n} | [{cid}](../critic/{cid}.md) | {cid.replace('__', '/', 1)} | {len(rs)} |")
    lines += ["", "## Blockers grouped by theme", ""]
    for theme, items in sorted(themes.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        lines += [f"### {theme} ({len(items)})", ""]
        for cid, text in sorted(items):
            lines.append(f"- [{cid}](../critic/{cid}.md): {text}")
        lines.append("")
    lines += ["## Per file", ""]
    for cid, rs in ranked:
        if not rs:
            continue
        lines.append(f"### {cid}")
        for text, theme in rs:
            lines.append(f"- {text} ({theme})")
        lines.append("")
    (d / "BLOCKERS.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"triage: {total} blockers, {sum(1 for v in per.values() if v)} files with blockers, {len(per)} shards")


def norm(t: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", t.lower())


def questions() -> None:
    d = DRAFTS / "questions"
    items = []  # (area, slug, text, source)
    shards = 0
    for f in sorted(d.glob("*.md")):
        if f.name == "DESIGNER_QUESTIONS.md":
            continue
        shards += 1
        src = f.stem.replace("__", "/", 1)
        for x in rows(f, "Q"):
            area = x[3] if len(x) > 3 else "rules"
            items.append((area, re.sub(r"[^a-z0-9-]", "", x[2].lower()) or "misc", x[1], src))
    # group by slug, then merge groups whose slugs are close
    groups: dict[str, list] = defaultdict(list)
    for it in items:
        groups[it[1]].append(it)
    keys = sorted(groups, key=lambda k: (-len(groups[k]), k))
    merged: dict[str, list] = {}
    for k in keys:
        for m in merged:
            if difflib.SequenceMatcher(None, k, m).ratio() >= 0.85:
                merged[m].extend(groups[k])
                break
        else:
            merged[k] = list(groups[k])
    # second pass: merge clusters whose first questions share most content words
    stop = {"should", "does", "would", "with", "that", "this", "than", "from", "have", "into", "their", "there", "which", "when", "what", "need", "needs", "stay", "keep", "or", "and", "the"}

    def toks(t: str) -> frozenset:
        return frozenset(w for w in norm(t).split() if len(w) > 3 and w not in stop)

    reps: list[tuple[str, frozenset]] = []
    final: dict[str, list] = {}
    for slug, its in sorted(merged.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        tk = toks(sorted(its, key=lambda t: (t[3], t[2]))[0][2])
        for rs, rt in reps:
            if tk and rt and len(tk & rt) / len(tk | rt) >= 0.4:
                final[rs].extend(its)
                break
        else:
            reps.append((slug, tk))
            final[slug] = list(its)
    merged = final
    out = []
    for slug, its in merged.items():
        # dedupe identical-ish wording inside the group
        uniq: list = []
        for it in sorted(its, key=lambda t: (t[3], t[2])):
            if not any(difflib.SequenceMatcher(None, norm(it[2]), norm(u[2])).ratio() >= 0.8 for u in uniq):
                uniq.append(it)
        out.append((slug, its, uniq))
    out.sort(key=lambda g: (-len(g[1]), g[0]))
    by_area: dict[str, list] = defaultdict(list)
    for slug, its, uniq in out:
        area = sorted(set(i[0] for i in its), key=lambda a: -sum(1 for i in its if i[0] == a))[0]
        by_area[area].append((slug, its, uniq))
    lines = ["# Designer questions (round 3 extraction)", "",
             f"{len(items)} raw questions from {shards} drafts, grouped into {len(out)} decisions (same decision across drafts = one entry, "
             "sources listed). Extracted by Haiku, grouped by `tools/batch/merge_round3.py`. Order: area, then most-raised first.", ""]
    n = 0
    for area in sorted(by_area):
        lines += [f"## {area}", ""]
        for slug, its, uniq in by_area[area]:
            n += 1
            srcs = sorted({i[3] for i in its})
            links = ", ".join(f"[{s}](../{s}.md)" for s in srcs[:8]) + (f" (+{len(srcs) - 8} more)" if len(srcs) > 8 else "")
            lines.append(f"{n}. **{slug.replace('-', ' ')}** ({len(srcs)} draft{'s' if len(srcs) != 1 else ''}): {uniq[0][2]}")
            for u in uniq[1:3]:
                lines.append(f"   - also: {u[2]}")
            lines.append(f"   - sources: {links}")
        lines.append("")
    (d / "DESIGNER_QUESTIONS.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"questions: {len(items)} raw -> {n} entries from {shards} shards")


if __name__ == "__main__":
    {"triage": triage, "questions": questions}[sys.argv[1]]()
