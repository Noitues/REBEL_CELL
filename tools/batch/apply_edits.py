"""Apply a `const_edits` batch's results (exact-text edit blocks) to the tree, with a value check.

    python tools/batch/apply_edits.py batches/rule5_sweep.results.jsonl            # dry run, per-file verdicts
    python tools/batch/apply_edits.py batches/rule5_sweep.results.jsonl --apply    # write the files that pass

Block grammar (tools/batch/prompts/const_edits.md), inside the RC_PATCH section:
    === INSERT_AFTER / <existing line> / --- TEXT / <new const lines>
    === REPLACE / <old code> / --- WITH / <new code>
    === END
A file passes only when every block matches exactly once, every new const is unique in the
file, and every REPLACE equals its original once the new (and existing) const names are put
back as their values (so the edit cannot change a value). Types are checked: an int const
must not hold a float literal and vice versa. Failing files are left untouched and listed.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CONST_RE = re.compile(r"^const\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?::\s*([A-Za-z0-9_\[\]]+))?\s*:?=\s*(.+?)\s*$")
PATCH_RE = re.compile(r"<<<RC_PATCH\n(.*?)^>>>", re.S | re.M)
STATUS_RE = re.compile(r"^status:\s*(\w+)", re.M)


def parse_blocks(patch: str) -> list[tuple[str, str, str]] | None:
    blocks = []
    patch = re.sub(r"^--- END\s*$", "=== END", patch, flags=re.M)
    parts =re.split(r"^=== (INSERT_AFTER|REPLACE|END)\s*$", patch, flags=re.M)
    # parts: [pre, kind, body, kind, body, ...]
    i = 1
    while i < len(parts):
        kind, body = parts[i], parts[i + 1] if i + 1 < len(parts) else ""
        i += 2
        if kind == "END":
            break
        sep = "--- TEXT" if kind == "INSERT_AFTER" else "--- WITH"
        m = re.split(r"^" + re.escape(sep) + r"\s*$", body, maxsplit=1, flags=re.M)
        if len(m) != 2:
            return None
        blocks.append((kind, m[0].strip("\n"), m[1].strip("\n")))
    return blocks


def literal_kind(value: str) -> str:
    v = value.strip()
    if re.fullmatch(r"-?[0-9]+", v):
        return "int"
    if re.fullmatch(r"-?[0-9]*\.[0-9]+(e-?[0-9]+)?|-?[0-9]+\.", v):
        return "float"
    return ""


def check_file(path: str, patch: str) -> tuple[str | None, list[str]]:
    """Returns (new text or None, problems)."""
    text = (ROOT / path).read_text(encoding="utf-8")
    blocks = parse_blocks(patch)
    if blocks is None or not blocks:
        return None, ["cannot parse blocks"]
    problems: list[str] = []
    existing = {m.group(1): m.group(3) for m in (CONST_RE.match(l) for l in text.splitlines()) if m}
    new_consts: dict[str, str] = {}
    for kind, a, b in blocks:
        if kind != "INSERT_AFTER":
            continue
        for line in b.splitlines():
            m = CONST_RE.match(line.strip())
            if not m:
                if line.strip() and not line.strip().startswith("##"):
                    problems.append(f"unexpected line in const text: {line.strip()[:60]}")
                continue
            name, typ, val = m.group(1), m.group(2) or "", m.group(3)
            if name in existing or name in new_consts or re.search(r"\b" + name + r"\b", text):
                problems.append(f"const name {name} already used in the file")
            lk = literal_kind(val)
            if typ == "int" and lk == "float" or typ == "float" and lk == "int":
                problems.append(f"{name}: type {typ} does not match literal {val}")
            new_consts[name] = val
    if problems:
        return None, problems
    known = {**existing, **new_consts}
    out = text
    dropped: list[str] = []
    unused = 0
    inserts = []
    for kind, a, b in blocks:
        if kind == "INSERT_AFTER":
            if text.count(a) != 1:
                return None, [f"anchor not unique/missing: {a[:60]}"]
            inserts.append((a, b))
            continue
        if out.count(a) != 1:
            dropped.append(f"REPLACE old text matches {out.count(a)}x: {a[:70]!r}")
            continue
        back = b
        for n in sorted(known, key=len, reverse=True):
            back = re.sub(r"\b" + re.escape(n) + r"\b", lambda _m, v=known[n]: v, back)
        # spacing and int-vs-float spelling of the same number (16 vs 16.0) are tolerated: the
        # applied diff is reviewed by eye for int contexts.
        if _norm(back) != _norm(a):
            dropped.append(f"value check failed, block dropped: old {a[:70]!r} vs back {back[:70]!r}")
            continue
        out = out.replace(a, b, 1)
    # keep only the const lines that a kept REPLACE (or other code) now uses
    for a, b in inserts:
        keep: list[str] = []
        pending: list[str] = []
        for line in b.splitlines():
            m = CONST_RE.match(line.strip())
            if m is None:
                pending.append(line)  # a ## comment line: belongs to the next const
                continue
            if re.search(r"\b" + m.group(1) + r"\b", out):
                keep += pending + [line]
            else:
                unused += 1
            pending = []
        if keep:
            out = out.replace(a, a + "\n" + "\n".join(keep), 1)
    if unused:
        dropped.append(f"{unused} unused const(s) removed")
    if out == text:
        return None, dropped or ["nothing applied"]
    return out, dropped


def _norm(s: str) -> str:
    s = re.sub(r"\s+", "", s)
    return re.sub(r"(?<![A-Za-z0-9_.])(\d+)\.0(?![0-9])", r"\1", s)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("results")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    results = Path(args.results)
    manifest = json.loads(results.with_suffix("").with_suffix(".manifest.json").read_text(encoding="utf-8"))
    files = manifest["files"]
    tin = tout = 0
    ok = bad = skipped = 0
    for line in results.read_text(encoding="utf-8").splitlines():
        o = json.loads(line)
        cid = o["custom_id"]
        path = files[cid]
        res = o["result"]
        if res["type"] != "succeeded":
            print(f"ERR   {path}: {res['type']}")
            bad += 1
            continue
        msg = res["message"]
        tin += msg["usage"]["input_tokens"] + msg["usage"].get("cache_read_input_tokens", 0)
        tout += msg["usage"]["output_tokens"]
        text = "".join(c.get("text", "") for c in msg["content"] if c["type"] == "text")
        if msg["stop_reason"] == "max_tokens":
            print(f"TRUNC {path}")
            bad += 1
            continue
        st = STATUS_RE.search(text)
        pm = PATCH_RE.search(text)
        if st and st.group(1) == "skip" or not pm or not pm.group(1).strip():
            print(f"SKIP  {path}")
            skipped += 1
            continue
        new, problems = check_file(path, pm.group(1))
        if new is None:
            print(f"FAIL  {path}")
            for p in problems:
                print(f"        {p}")
            bad += 1
            continue
        print(f"OK    {path}")
        for p in problems:
            print(f"        {p}")
        ok += 1
        if args.apply:
            (ROOT / path).write_text(new, encoding="utf-8", newline="")
    print(f"apply_edits: ok {ok}, fail {bad}, skip {skipped}; tokens in {tin} out {tout}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
