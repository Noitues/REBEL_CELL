"""Plan 2 decision sheet: shard DESIGNER_QUESTIONS.md by theme (map), then one reduce, via the Message Batches API.

    python tools/batch/build_decision_sheet.py <work> build-map
    python tools/batch/build_decision_sheet.py <work> submit map            # batch id -> <work>/ids.json
    python tools/batch/build_decision_sheet.py <work> collect map          # waits; writes <work>/out/<id>.json + retry list
    python tools/batch/build_decision_sheet.py <work> build-reduce
    python tools/batch/build_decision_sheet.py <work> submit reduce
    python tools/batch/build_decision_sheet.py <work> collect reduce
    python tools/batch/build_decision_sheet.py <work> render <out.md>

<work> is a scratchpad directory. Retries of truncated requests: `build-map --retry id1,id2` / `build-reduce --retry x`
rebuild only those requests at max_tokens 64000 into retry.jsonl; `submit retry`; `collect retry`.
Credentials: ANTHROPIC_API_KEY or the Windows user variable of that name; never printed.
Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import anthropic

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_drafts import api_key  # noqa: E402

MODEL = "claude-sonnet-5-5"
QFILE = ROOT / "docs/handoff/plan2/drafts/questions/DESIGNER_QUESTIONS.md"
ENTRY_RE = re.compile(r"^(\d+)\. \*\*(.+?)\*\* \((\d+) drafts?\): (.*)$")
SRC_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

ART_QUESTIONS = [
    'Does "Renewal Engine" survive as Solace\'s boss name (GDD 714/720) or become THE GENOME CORE?',
    "Orbital Central Server: Launch Control, the Commons Array, or the missile bay?",
    "Aurelian Central Server name (THE CONCORDAT VAULT proposed) and options in drafts/names/.",
    "Meridian: keep THE MASTER MANIFEST vs drafts/names/ options.",
    "Halcyon pyramid: cyan-white or violet? (art director)",
    "Tethys: spec 3.4 blue or the frames' teal? (art director)",
    "Is the TARGET edge arrow (spec 9.5b) a Godot overlay? (build session)",
]
ART_LIST = "\n".join(f"{i + 1}. {q}" for i, q in enumerate(ART_QUESTIONS))

MAP_SYS = """You condense designer questions for a Godot deckbuilder (REBEL_CELL) into DECISION-LEVEL questions.
You get the content-design rules, the designer's rulings, and a shard of raw extracted questions (numbered entries; many are the same decision phrased per draft, or per card/enemy).
Do:
1. Merge entries that need the SAME designer decision (e.g. "should X scale with tier" across 12 enemies = one question).
2. Mark a cluster `answered` if an existing ruling (DECISIONS 2026-10-14 / 2026-10-16, REPLAN D1-D10, content rules R1-R13, G1-G16) already answers it; cite it in `ruling` (short: "D3", "R7", "2026-10-16 phases", ...). Otherwise answered=false.
3. For open clusters give 2-4 short options, a RECOMMENDED option index (0-based `rec`) and a one-line why (pick the simplest option consistent with the GDD pillars and the rulings).
4. If a cluster concerns one of the art/naming questions below, set `art` to its number (1-7), else null.
5. Every entry number in the shard must appear in exactly one cluster (put pure noise or build detail with no designer decision in a cluster with `drop`: true, no options needed).
Be terse. Output ONLY a JSON array, no prose, no code fence. Each element:
{"theme": "<2-3 word theme>", "question": "<one sentence>", "options": ["..."], "rec": 0, "why": "<one line>", "answered": false, "ruling": "", "art": null, "drop": false, "entries": [1, 2]}
Art/naming list:
""" + ART_LIST

REDUCE_SYS = """You produce the final DESIGNER DECISION SHEET for the REBEL_CELL plan-2 content drafts.
Input: content-design rules, the designer's rulings, the critic BLOCKERS triage, and a list of candidate clusters (each with an id `c<N>`, theme, question, options, rec, why, n_entries) produced by shard passes over 655 raw questions.
Produce:
- `open`: 40-60 decision-level questions (merge near-duplicate clusters across shards; keep only things the designer must rule on; art/naming clusters go to `art`, not here). Each: theme (short header, reuse a small set of 8-10 themes), question (one sentence), options (2-4 strings), rec (0-based index), why (one line), clusters (list of the cluster ids merged in). Prefer questions that BLOCKERS shows blocking build. Skip clusters flagged answered=true or drop=true here.
- `answered`: clusters already answered by a ruling, merged into rows: question (short), ruling (citation), clusters.
- `art`: exactly 7 entries numbered 1-7 for the Art and naming list below, same fields as open plus "n": the number; clusters = ids of related clusters (may be empty).
- `dropped`: cluster ids that are noise.
Every cluster id should land in exactly one of the clusters lists. Output ONLY JSON: {"open": [...], "answered": [...], "art": [...], "dropped": [...]}. No prose, no code fence.
Art/naming list:
""" + ART_LIST


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def rulings_text() -> str:
    lines = read("docs/DECISIONS.md").splitlines()
    out = "\n".join(lines[111:374])  # 2026-10-14 ART-R*, 2026-10-16 rulings, 2026-10-14 PT-003 / map rulings
    replan = read("docs/handoff/gates/REPLAN_2026-10-16.md")
    m = re.search(r"## D\. Designer decisions needed.*?\*\*Critical files", replan, re.S)
    return out + "\n\n=== REPLAN_2026-10-16 section D (D1-D10 as asked) ===\n" + (m.group(0) if m else "")


def parse_entries() -> list[dict]:
    es: list[dict] = []
    area = ""
    for ln in QFILE.read_text(encoding="utf-8").splitlines():
        if ln.startswith("## "):
            area = ln[3:].strip()
            continue
        m = ENTRY_RE.match(ln)
        if m:
            es.append({"n": int(m.group(1)), "area": area, "title": m.group(2), "k": int(m.group(3)), "q": m.group(4), "also": [], "src": []})
        elif es and ln.strip().startswith("- also:"):
            es[-1]["also"].append(ln.split("- also:", 1)[1].strip())
        elif es and ln.strip().startswith("- sources:"):
            es[-1]["src"] = [(a, b) for a, b in SRC_RE.findall(ln)]
    return es


def shards(es: list[dict]) -> dict[str, list[dict]]:
    by: dict[str, list[dict]] = {}
    for e in es:
        by.setdefault(e["area"], []).append(e)
    out: dict[str, list[dict]] = {}
    for a, lst in by.items():
        if len(lst) > 100:
            k = -(-len(lst) // 85)
            sz = -(-len(lst) // k)
            for i in range(k):
                out[f"{a}-{i + 1}"] = lst[i * sz:(i + 1) * sz]
        else:
            out[a] = lst
    small = {a: out.pop(a) for a in ["economy", "narrative", "process", "new-system", "ui-and-art"] if a in out}
    out["small-a"] = small.get("economy", []) + small.get("narrative", []) + small.get("process", [])
    out["small-b"] = small.get("new-system", []) + small.get("ui-and-art", [])
    return out


def entry_text(e: dict) -> str:
    s = f"#{e['n']} [{e['area']}] ({e['k']} drafts) {e['title']}: {e['q']}"
    for a in e["also"]:
        s += f"\n   also: {a}"
    return s


def req(cid: str, system: str, user: str, max_tokens: int) -> dict:
    return {"custom_id": cid, "params": {"model": MODEL, "max_tokens": max_tokens,
            "system": [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            "messages": [{"role": "user", "content": user}]}}


def map_reqs() -> dict[str, dict]:
    ctx = "=== CONTENT_DESIGN_V2 ===\n" + read("docs/handoff/plan2/CONTENT_DESIGN_V2.md") + "\n\n=== DESIGNER RULINGS ===\n" + rulings_text()
    out = {}
    for name, lst in shards(parse_entries()).items():
        user = f"{ctx}\n\n=== SHARD {name}: {len(lst)} entries ===\n" + "\n".join(entry_text(e) for e in lst)
        out[f"map-{name}"] = req(f"map-{name}", MAP_SYS, user, 24000)
    return out


def write_jsonl(path: Path, reqs: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(r) for r in reqs) + "\n", encoding="utf-8")


def client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=api_key())


def parse_json(text: str):
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    return json.loads(t)


def cmd_collect(work: Path, name: str) -> int:
    ids = json.loads((work / "ids.json").read_text())
    c = client()
    bid = ids[name]
    while True:
        b = c.messages.batches.retrieve(bid)
        if b.processing_status == "ended":
            break
        print(name, b.processing_status, b.request_counts, flush=True)
        time.sleep(45)
    od = work / "out"
    od.mkdir(exist_ok=True)
    cost = 0.0
    retry = []
    for r in c.messages.batches.results(bid):
        cid = r.custom_id
        if r.result.type != "succeeded":
            print("FAIL", cid, r.result.type)
            retry.append(cid)
            continue
        m = r.result.message
        u = m.usage
        cost += 0.5 * (3 * (u.input_tokens + (u.cache_creation_input_tokens or 0) * 1.25 + (u.cache_read_input_tokens or 0) * 0.1) + 15 * u.output_tokens) / 1e6
        text = "".join(b.text for b in m.content if b.type == "text")
        (od / f"{cid}.txt").write_text(text, encoding="utf-8")
        try:
            (od / f"{cid}.json").write_text(json.dumps(parse_json(text), indent=1), encoding="utf-8")
        except Exception as ex:  # noqa: BLE001
            print("BADJSON", cid, m.stop_reason, ex)
            retry.append(cid)
    prev = float((work / "cost.txt").read_text()) if (work / "cost.txt").exists() else 0.0
    (work / "cost.txt").write_text(str(prev + cost))
    (work / f"retry_{name}.txt").write_text(",".join(retry))
    print(f"collected {name}: cost~${cost:.3f} (running total ${prev + cost:.3f}), retry={retry}")
    return 0


def render(work: Path, out: Path) -> int:
    es = {e["n"]: e for e in parse_entries()}
    clusters = {c["id"]: c for c in json.loads((work / "clusters.json").read_text())}
    res = json.loads((work / "out/reduce.json").read_text())

    def drafts(cids: list[str]) -> list[tuple[str, str]]:
        seen: dict[str, str] = {}
        for cid in cids:
            for n in clusters.get(cid, {}).get("entries", []):
                for label, link in es.get(n, {"src": []})["src"]:
                    seen.setdefault(label, link)
        return sorted(seen.items())

    def link_line(ds: list[tuple[str, str]], limit: int = 6) -> str:
        shown = ", ".join(f"[{lab}](../{p[3:] if p.startswith('../') else p})" for lab, p in ds[:limit])
        more = f" +{len(ds) - limit} more" if len(ds) > limit else ""
        return f"{len(ds)} drafts" + (f": {shown}{more}" if ds else "")

    def opts(q: dict) -> list[str]:
        rec = q.get("rec", 0)
        return [f"{chr(97 + i)}) {o}{'  **(RECOMMENDED)**' if i == rec else ''}" for i, o in enumerate(q["options"])]

    openq = [(len(drafts(q["clusters"])), q) for q in res["open"]]
    openq.sort(key=lambda t: (-t[0], t[1]["question"]))
    L = ["# Plan 2 decision sheet", "",
         f"{len(openq)} decision-level questions distilled from the 655 entries of [DESIGNER_QUESTIONS](DESIGNER_QUESTIONS.md), "
         f"plus {len(res['art'])} art and naming questions (A1-A7). Themes ordered by drafts unblocked; within a theme, most-unblocking first. "
         "Generated by `tools/batch/build_decision_sheet.py` (Message Batches, Sonnet 5.5); recommendations are proposals, not rulings.", ""]
    themes: dict[str, list] = {}
    for n, q in openq:
        themes.setdefault(q["theme"], []).append((n, q))
    order = sorted(themes, key=lambda t: -max(n for n, _ in themes[t]))
    num = 1
    for t in order:
        L += [f"## {t}", ""]
        for _n, q in themes[t]:
            L += [f"**Q{num}. {q['question']}**"]
            L += [f"- {o}" for o in opts(q)]
            L += [f"- Why: {q['why']}", f"- Unblocks {link_line(drafts(q['clusters']))}", ""]
            num += 1
    L += ["## Art and naming", ""]
    for q in sorted(res["art"], key=lambda x: x["n"]):
        L += [f"**A{q['n']}. {q['question']}**"]
        L += [f"- {o}" for o in opts(q)]
        L += [f"- Why: {q['why']}", f"- Unblocks {link_line(drafts(q.get('clusters', [])))}", ""]
    L += ["## Answered by existing rulings", "", "| Question | Ruling | Drafts |", "|---|---|---|"]
    ans = sorted(res["answered"], key=lambda r: -len(drafts(r["clusters"])))
    for r in ans:
        L.append(f"| {r['question']} | {r['ruling']} | {len(drafts(r['clusters']))} |")
    L.append("")
    covered = {c for q in res["open"] + res["answered"] + res["art"] for c in q.get("clusters", [])} | set(res.get("dropped", []))
    miss = [c for c in clusters if c not in covered]
    L.append(f"Coverage: {len(covered & set(clusters))}/{len(clusters)} candidate clusters placed; unplaced: {len(miss)}; dropped as noise: {len(res.get('dropped', []))}.")
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"open={len(openq)} answered={len(ans)} art={len(res['art'])} unplaced={len(miss)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("cmd")
    ap.add_argument("arg", nargs="?")
    ap.add_argument("--retry", default="")
    a = ap.parse_args()
    work = Path(a.work)
    work.mkdir(parents=True, exist_ok=True)
    if a.cmd == "build-map":
        rs = map_reqs()
        want = [x for x in a.retry.split(",") if x]
        sel = [rs[k] for k in rs if not want or k in want]
        if want:
            for r in sel:
                r["params"]["max_tokens"] = 64000
        write_jsonl(work / ("retry.jsonl" if want else "map.jsonl"), sel)
        print(len(sel), "requests", [(r["custom_id"], len(json.dumps(r)) // 1000) for r in sel])
    elif a.cmd == "build-reduce":
        clusters = []
        for f in sorted((work / "out").glob("map-*.json")):
            for c in json.loads(f.read_text(encoding="utf-8")):
                c["id"] = f"c{len(clusters) + 1}"
                clusters.append(c)
        (work / "clusters.json").write_text(json.dumps(clusters, indent=1), encoding="utf-8")
        slim = []
        for c in clusters:
            s = {k: v for k, v in c.items() if k != "entries"}
            s["n_entries"] = len(c.get("entries", []))
            slim.append(s)
        ctx = ("=== CONTENT_DESIGN_V2 ===\n" + read("docs/handoff/plan2/CONTENT_DESIGN_V2.md") + "\n\n=== DESIGNER RULINGS ===\n" + rulings_text()
               + "\n\n=== BLOCKERS triage ===\n" + read("docs/handoff/plan2/drafts/triage/BLOCKERS.md"))
        user = ctx + f"\n\n=== CANDIDATE CLUSTERS ({len(slim)}) ===\n" + json.dumps(slim, ensure_ascii=False)
        mt = 64000 if a.retry else 32000
        write_jsonl(work / ("retry.jsonl" if a.retry else "reduce.jsonl"), [req("reduce", REDUCE_SYS, user, mt)])
        print(len(slim), "clusters;", len(user) // 1000, "KB")
    elif a.cmd == "submit":
        reqs = [json.loads(ln) for ln in (work / f"{a.arg}.jsonl").read_text(encoding="utf-8").splitlines() if ln.strip()]
        b = client().messages.batches.create(requests=reqs)
        p = work / "ids.json"
        ids = json.loads(p.read_text()) if p.exists() else {}
        ids[a.arg] = b.id
        p.write_text(json.dumps(ids))
        print(a.arg, len(reqs), b.id)
    elif a.cmd == "collect":
        return cmd_collect(work, a.arg)
    elif a.cmd == "render":
        return render(work, Path(a.arg))
    return 0


if __name__ == "__main__":
    sys.exit(main())
