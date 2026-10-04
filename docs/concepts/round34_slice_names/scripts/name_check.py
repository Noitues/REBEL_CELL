"""Round 34: check candidate slice-program names against every proper term in the game.

Corpus: docs/GDD.md, docs/DECISIONS.md, and every .tres under content/ (whole text: ids, display
names, descriptions). A candidate collides when it appears as a whole word (case-insensitive, also as
a snake_case id part) anywhere in the corpus. Writes ../scratch/check.json and prints a summary.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

CANDIDATES = {
    # type: (old, [options])  -- first option of each list is the recommendation
    "ATTACK": ("EXPLOIT", ["SHIM", "SHIV", "SPIKE", "STAB", "PAYLOAD"]),
    "CRIT": ("ZERO-DAY", ["OVERFLOW", "SEGFAULT", "KERNEL PANIC", "BLUESCREEN"]),
    "DEFEND": ("FIREWALL", ["DEFRAG", "BURNWALL", "IRONWALL", "BLACKWALL"]),
    "SHIELD": ("SANDBOX", ["SANDBOX", "BUBBLE", "QUARANTINE"]),
    "EVADE": ("PROXY", ["DETOUR", "REROUTE", "TUNNEL"]),
    "HEAL": ("PATCH", ["HOTFIX", "RESTORE", "DEBUG"]),
    "AFFLICT": ("VIRUS", ["CONTAGION", "INFECT", "PATHOGEN", "BLIGHT"]),
    "DEPLOY": ("TROJAN", ["TROJAN", "SPAWN", "FORK"]),
    "MISS": ("NULL", ["NULL", "VOID", "NOP"]),
}
OLD = ["EXPLOIT", "ZERO-DAY", "FIREWALL", "SANDBOX", "PROXY", "PATCH", "VIRUS", "TROJAN", "NULL"]


def corpus():
    files = [os.path.join(ROOT, "docs", "GDD.md"), os.path.join(ROOT, "docs", "DECISIONS.md")]
    for dp, _dn, fn in os.walk(os.path.join(ROOT, "content")):
        for f in fn:
            if f.endswith(".tres"):
                files.append(os.path.join(dp, f))
    out = []
    for f in sorted(files):
        try:
            txt = open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        out.append((os.path.relpath(f, ROOT).replace("\\", "/"), txt))
    return out


def hits(term, docs):
    words = re.split(r"[\s\-]+", term.strip())
    pat = r"(?<![A-Za-z0-9])" + r"[\s_\-]?".join(re.escape(w) for w in words) + r"(?![A-Za-z0-9])"
    rx = re.compile(pat, re.IGNORECASE)
    found = []
    for path, txt in docs:
        for m in rx.finditer(txt):
            a, b = max(0, m.start() - 40), min(len(txt), m.end() + 40)
            found.append((path, txt[a:b].replace("\n", " ")))
    return found


def main():
    docs = corpus()
    res = {"files": len(docs), "old": {}, "new": {}}
    for o in OLD:
        h = hits(o, docs)
        res["old"][o] = {"n": len(h), "where": sorted({p for p, _ in h})[:6], "sample": [s for _, s in h[:3]]}
    for ty, (old, opts) in CANDIDATES.items():
        for c in opts:
            h = hits(c, docs)
            res["new"][c] = {"type": ty, "n": len(h), "where": sorted({p for p, _ in h})[:6], "sample": [s for _, s in h[:3]]}
    os.makedirs(os.path.join(HERE, "..", "scratch"), exist_ok=True)
    json.dump(res, open(os.path.join(HERE, "..", "scratch", "check.json"), "w"), indent=1)
    print("corpus files:", res["files"])
    for k, v in res["old"].items():
        print("OLD %-10s %4d  %s" % (k, v["n"], v["where"][:3]))
    for k, v in res["new"].items():
        print("NEW %-8s %-13s %4d  %s  %s" % (v["type"], k, v["n"], v["where"][:3], v["sample"][:1]))


if __name__ == "__main__":
    main()
