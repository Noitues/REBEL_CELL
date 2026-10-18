#!/usr/bin/env python3
"""BalanceSim driver (docs/handoff/plan2/BALANCE_SIM.md S1-S3).

  python tools/balance/balance.py run <mode> --name NAME [--seeds 1000:1019] [-j 2] [--out-dir DIR]
         [any balance_sim.gd option: --policy heuristic --lookahead 2 --skill 0.8 --ice 5
          --set path=value --variant file.json --enemy ID --tiers 1,2 --tier 1 --source fresh ...]
      Shards the seeds over -j Godot processes, merges the records (sorted, so the shard count never
      changes the result) into DIR/NAME.json and writes DIR/NAME.md.
  python tools/balance/balance.py report NAME.json [--md out.md]
  python tools/balance/balance.py compare A.json B.json --name NAME [--out docs/balance/CMP_NAME.md]
      Delta B - A per group and metric with a 90 % bootstrap interval over the seeds; a delta whose
      interval contains 0 is flagged "noise".

Godot output goes to files (never a pipe). Stdlib only.
"""
import argparse
import json
import math
import os
import random
import statistics
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import phase_metrics as pm  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SIM = "tools/balance/balance_sim.gd"
BOOTSTRAP = 2000
BOOT_SEED = 20261015
CI = 0.90


# --- Statistics -----------------------------------------------------------------------------

def pct(sorted_vals, p):
    """Linear-interpolated percentile (p in 0..1) of a sorted list."""
    if not sorted_vals:
        return float("nan")
    k = (len(sorted_vals) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    if lo == hi:
        return float(sorted_vals[lo])
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def dist(vals):
    """{n, mean, median, p10, p90} of a list of numbers."""
    v = sorted(float(x) for x in vals)
    if not v:
        return {"n": 0}
    return {"n": len(v), "mean": sum(v) / len(v), "median": pct(v, 0.5), "p10": pct(v, 0.1), "p90": pct(v, 0.9)}


def record_metrics(rec):
    """name -> list of values one record contributes (scalars: 1, series: one per index, pools: many)."""
    out = {}
    for k, v in rec.get("scalars", {}).items():
        out[k] = [v]
    for k, vals in rec.get("series", {}).items():
        for i, v in enumerate(vals):
            out["%s[%d]" % (k, i + 1)] = [v]
    for k, vals in rec.get("pools", {}).items():
        if vals:
            out[k] = list(vals)
    return out


def group_stats(records):
    """group -> metric -> dist, over all values of the group's records."""
    acc = {}
    for r in records:
        g = acc.setdefault(r["group"], {})
        for k, vals in record_metrics(r).items():
            g.setdefault(k, []).extend(vals)
    return {g: {k: dist(v) for k, v in m.items()} for g, m in acc.items()}


def per_record_means(records):
    """group -> metric -> [one number per record that has it] (pools reduce to their mean)."""
    acc = {}
    for r in records:
        g = acc.setdefault(r["group"], {})
        for k, vals in record_metrics(r).items():
            g.setdefault(k, []).append(sum(vals) / len(vals))
    return acc


def bootstrap_delta(a, b, rng):
    """(delta of means, lo, hi) of b - a with a 90 % bootstrap interval."""
    delta = sum(b) / len(b) - sum(a) / len(a)
    ds = []
    na, nb = len(a), len(b)
    for _ in range(BOOTSTRAP):
        ma = sum(rng.choices(a, k=na)) / na
        mb = sum(rng.choices(b, k=nb)) / nb
        ds.append(mb - ma)
    ds.sort()
    return delta, pct(ds, (1 - CI) / 2), pct(ds, 1 - (1 - CI) / 2)


# --- Running ------------------------------------------------------------------------------------

def parse_seeds(text):
    if ":" in text:
        a, b = text.split(":")
        return list(range(int(a), int(b) + 1))
    return [int(x) for x in text.split(",") if x]


def merge(shards, mode, extra_meta):
    first = shards[0]
    records = [r for s in shards for r in s["records"]]
    records.sort(key=lambda r: (r["group"], r["seed"]))
    return {"schema": first["schema"], "mode": mode, "opts": first["opts"], "overrides": first["overrides"],
            "meta": extra_meta, "records": records}


def run_chunk(task):
    """One Godot process over a chunk of seeds; returns (index, output path, exit code)."""
    idx, chunk, mode, passthrough, godot, work = task
    out = work / ("chunk%03d.json" % idx)
    cmd = [godot, "--headless", "--path", str(ROOT), "-s", SIM, "--", mode, "--seeds", ",".join(map(str, chunk)),
           "--out", str(out)] + passthrough
    with open(work / ("chunk%03d.log" % idx), "w") as log:
        rc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, cwd=str(ROOT)).returncode
    return idx, out, rc


def chunk_size(mode, n_seeds, jobs):
    """Seeds per Godot process. Small chunks let idle workers steal work (campaigns vary 17-96 s); big ones
    amortise the ~4 s engine start-up for the quick modes."""
    if mode in ("campaign", "boss"):
        return 1
    return max(1, math.ceil(n_seeds / (jobs * 2)))


def cmd_run(args, passthrough):
    from concurrent.futures import ThreadPoolExecutor
    mode = args.mode
    seeds = parse_seeds(args.seeds)
    jobs = max(1, min(args.j, len(seeds)))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    work = out_dir / ("_" + args.name)
    work.mkdir(parents=True, exist_ok=True)
    size = args.chunk or chunk_size(mode, len(seeds), jobs)
    tasks = [(i, seeds[k:k + size], mode, passthrough, args.godot, work) for i, k in enumerate(range(0, len(seeds), size))]
    t0 = time.time()
    # dynamic scheduling: `jobs` workers pull the next chunk as soon as they are free (work stealing)
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        results = list(pool.map(run_chunk, tasks))
    shards, failed = [], False
    for idx, out, rc in results:
        if rc != 0 or not out.exists():
            print("chunk failed: %s (exit %s); see %s" % (out.name, rc, out.with_suffix(".log")), file=sys.stderr)
            failed = True
        else:
            shards.append(json.loads(out.read_text(encoding="utf-8")))
    if failed or not shards:
        return 1
    wall = time.time() - t0
    meta = {"name": args.name, "seeds": seeds, "jobs": jobs, "chunk": size, "wall_s": round(wall, 1), "args": passthrough}
    merged = merge(shards, mode, meta)
    (out_dir / (args.name + ".json")).write_text(json.dumps(merged, sort_keys=True), encoding="utf-8")
    (out_dir / (args.name + ".md")).write_text(render_report(merged), encoding="utf-8")
    for idx, out, rc in results:
        out.unlink(missing_ok=True)
    per_hour = len(seeds) * 3600.0 / wall if mode == "campaign" else 0
    print("balance: %d records, %.1f s wall (-j %d, chunk %d)%s -> %s" % (
        len(merged["records"]), wall, jobs, size, (", %.0f campaigns/hour" % per_hour) if per_hour else "", out_dir / (args.name + ".md")))
    return 0


# --- Report -----------------------------------------------------------------------------------

def f(x, nd=1):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    return ("%." + str(nd) + "f") % x


def row_stats(st, key, nd=1, scale=1.0):
    d = st.get(key)
    if not d or d.get("n", 0) == 0:
        return ["-", "-", "-", "-"]
    return [f(d["mean"] * scale, nd), f(d["median"] * scale, nd), f(d["p10"] * scale, nd), f(d["p90"] * scale, nd)]


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out) + "\n"


def render_report(m):
    mode = m["mode"]
    meta = m.get("meta", {})
    o = m["opts"]
    stats = group_stats(m["records"])
    n_seeds = len({r["seed"] for r in m["records"]})
    lines = ["# Balance report: %s (%s)\n" % (meta.get("name", "?"), mode)]
    lines.append("- policy: %s%s, skill %s, ICE %s, corp %s, class %s" % (
        o.get("policy"), (" lookahead " + str(o.get("lookahead"))) if o.get("policy") == "heuristic" else "", o.get("skill"),
        o.get("ice"), o.get("corp"), o.get("class")))
    lines.append("- seeds: %d (%s..%s), records: %d" % (n_seeds, min((r["seed"] for r in m["records"]), default="-"),
                                                       max((r["seed"] for r in m["records"]), default="-"), len(m["records"])))
    lines.append("- overrides: %s" % (", ".join("`%s`" % s for s in m["overrides"]) if m["overrides"] else "none (content as committed)"))
    if "wall_s" in meta:
        lines.append("- wall time: %s s with -j %s" % (meta["wall_s"], meta.get("jobs")))
    lines.append("")
    body = {"campaign": report_campaign, "fight": report_fight, "boss": report_boss, "netrun": report_netrun}[mode]
    lines.append(body(m, stats))
    lines.append(phase_section(m))
    return "\n".join(lines) + "\n"


def stat_rows(st, spec):
    rows = []
    for label, key, nd, scale in spec:
        rows.append([label] + row_stats(st, key, nd, scale))
    return rows


def report_campaign(m, stats):
    out = []
    for g, st in sorted(stats.items()):
        out.append("## %s\n" % g)
        won = st.get("won", {})
        out.append("Win rate **%s %%** over %d campaigns (loss %s %%).\n" % (f(100 * won.get("mean", float("nan"))), won.get("n", 0),
                                                                                f(100 * st.get("lost", {}).get("mean", float("nan")))))
        spec = [("runs", "runs", 1, 1), ("completed runs", "completed", 1, 1), ("deaths", "deaths", 1, 1), ("raids", "raids", 1, 1),
                ("raids won", "raids_won", 1, 1), ("raids lost", "raids_lost", 1, 1), ("Heat peak", "heat_peak", 1, 1), ("Heat at end", "heat_end", 1, 1),
                ("Heat at breach", "heat_at_breach", 1, 1), ("minutes (GDD 11.8: ~395)", "minutes", 0, 1), ("fights", "fights", 1, 1),
                ("raids from flatline Heat", "raids_from_flatline", 2, 1), ("raids from Heat of actions", "raids_from_heat_actions", 2, 1),
                ("raids from other sources", "raids_other", 2, 1), ("Schematics income", "schematics_income", 0, 1),
                ("Schematics spent", "schematics_spent", 0, 1), ("Schematics unspent at end", "schematics_unspent", 0, 1),
                ("operatives recruited", "recruits", 1, 1), ("layers per run", "layers_per_run", 2, 1),
                ("heal HP per run", "heal_hp_per_run", 2, 1), ("heals available per run", "heals_available_per_run", 2, 1),
                ("heals used per run", "heals_used_per_run", 2, 1), ("stuck fights", "stuck", 2, 1)]
        out.append(table(["metric", "mean", "median", "p10", "p90"], stat_rows(st, spec)))
        out.append(heat_curve_table(st))
        out.append(attrition_table(st))
        out.append(fight_pool_table(st))
    return "\n".join(out)


def heat_curve_table(st):
    pts = [i for i in (1, 3, 5, 8, 12, 16, 20, 25, 30, 40, 50, 60) if "heat_curve[%d]" % i in st]
    if not pts:
        return ""
    rows = [[str(i)] + row_stats(st, "heat_curve[%d]" % i, 1) + [str(st["heat_curve[%d]" % i]["n"])] for i in pts]
    return "### Heat after run N\n\n" + table(["run", "mean", "median", "p10", "p90", "n campaigns"], rows)


def attrition_table(st):
    tiers = sorted({int(k.split(".")[1][1:]) for k in st if k.startswith("hp_frac_arrival.")})
    if not tiers:
        return ""
    out = ["### HP on arrival per layer (fraction of max HP, mean [p10-p90])\n"]
    layers = sorted({int(k.split(".")[2][1:]) for k in st if k.startswith("hp_frac_arrival.")})
    rows = []
    for t in tiers:
        row = ["T%d" % t]
        for l in layers:
            d = st.get("hp_frac_arrival.t%d.l%d" % (t, l))
            row.append("%s [%s-%s] n=%d" % (f(d["mean"], 2), f(d["p10"], 2), f(d["p90"], 2), d["n"]) if d else "-")
        rows.append(row)
    out.append(table(["tier"] + ["L%d" % l for l in layers], rows))
    return "\n".join(out)


def fight_pool_table(st):
    keys = sorted({k[len("fight_turns."):] for k in st if k.startswith("fight_turns.")})
    if not keys:
        return ""
    rows = []
    for k in keys:
        t, hl, w = st.get("fight_turns." + k), st.get("fight_hp_lost." + k), st.get("fight_win." + k)
        rows.append([k, t["n"], f(t["mean"]), f(t["p90"]), f(hl["mean"]) if hl else "-", f(100 * w["mean"], 0) if w else "-"])
    return "### Fights in the campaigns (category.tier)\n\n" + table(["category.tier", "fights", "turns mean", "turns p90", "HP lost mean", "win %"], rows)


def report_netrun(m, stats):
    out = []
    for g, st in sorted(stats.items()):
        out.append("## %s\n" % g)
        died = st.get("died", {})
        out.append("Death rate **%s %%** over %d runs.\n" % (f(100 * died.get("mean", float("nan"))), died.get("n", 0)))
        spec = [("layers reached", "layers", 2, 1), ("HP at end (fraction)", "hp_end_frac", 2, 1), ("Cycles", "cycles", 0, 1),
                ("heal HP gained", "heal_hp", 1, 1), ("heals available (Terminals)", "heals_available", 2, 1), ("heals used", "heals_used", 2, 1)]
        out.append(table(["metric", "mean", "median", "p10", "p90"], stat_rows(st, spec)))
        layers = sorted({int(k.split("[")[1][:-1]) for k in st if k.startswith("layer_hp_frac[")})
        rows = [["L%d" % l] + row_stats(st, "layer_hp_frac[%d]" % l, 2) + [str(st["layer_hp_frac[%d]" % l]["n"])] for l in layers]
        out.append("### HP on arrival per layer (fraction of max HP)\n\n" + table(["layer", "mean", "median", "p10", "p90", "n"], rows))
        out.append(fight_pool_table(st))
    return "\n".join(out)


def report_boss(m, stats):
    out = []
    for g, st in sorted(stats.items()):
        out.append("## %s\n" % g)
        won = st.get("won", {})
        out.append("Win rate **%s %%** over %d fights (no breach reached: %s).\n" % (
            f(100 * won.get("mean", float("nan"))), won.get("n", 0), f(st.get("no_breach", {}).get("n", 0), 0)))
        spec = [("turns, total", "turns", 1, 1), ("phases", "phases", 1, 1)]
        spec += [("turns in phase %d" % i, "turns_phase_%d" % i, 1, 1) for i in range(1, 8) if "turns_phase_%d" % i in st]
        spec += [("operative HP at the end", "hp_end", 1, 1), ("HP lost (fraction)", "hp_lost_frac", 2, 1), ("damage dealt per turn", "dealt_per_turn", 1, 1),
                 ("damage taken per turn", "taken_per_turn", 2, 1), ("Perfect rate", "perfect_rate", 2, 1), ("boss heal turns", "heal_turns", 1, 1),
                 ("operative rank", "operative_rank", 1, 1), ("operative max HP", "operative_hp_max", 1, 1), ("deck size", "deck_size", 1, 1),
                 ("Heat at breach", "heat", 1, 1)]
        out.append(table(["metric", "mean", "median", "p10", "p90"], stat_rows(st, spec)))
        turns = sorted({int(k.split("[")[1][:-1]) for k in st if k.startswith("boss_hp_frac[")})
        pts = [t for t in turns if t in (1, 2, 3, 5, 8, 10, 15, 20, 25, 30, 40, 50, 60)]
        rows = []
        for t in pts:
            rows.append([str(t)] + row_stats(st, "boss_hp_frac[%d]" % t, 2) + row_stats(st, "player_hp[%d]" % t, 0)[:1] + [str(st["boss_hp_frac[%d]" % t]["n"])])
        if rows:
            out.append("### Curves by turn (fights still running)\n\n" + table(["turn", "boss HP frac mean", "median", "p10", "p90", "operative HP mean", "n"], rows))
    return "\n".join(out)


def report_fight(m, stats):
    out = []
    cats = {}
    for r in m["records"]:
        cats[r["group"]] = r.get("category", "")
    tiers = sorted({int(g.split("@t")[1]) for g in stats})
    for t in tiers:
        out.append("## Tier %d\n" % t)
        rows = []
        for g, st in sorted(stats.items()):
            if not g.endswith("@t%d" % t):
                continue
            tn, hl = st.get("turns"), st.get("hp_lost")
            if not tn:
                continue
            rows.append([g.split(":")[1].split("@")[0], cats.get(g, ""), tn["n"], f(100 * st["won"]["mean"], 0), f(tn["mean"]), f(tn["median"], 0), f(tn["p90"], 0),
                         f(hl["mean"]), f(hl["p90"], 0), f(st["dealt_per_turn"]["mean"]), f(st["taken_per_turn"]["mean"], 2),
                         f(100 * st["perfect_rate"]["mean"], 0), f(st["heal_turns"]["mean"], 1)])
        out.append(table(["enemy", "category", "n", "win %", "turns mean", "median", "p90", "HP lost mean", "p90", "dealt/turn", "taken/turn", "Perfect %", "heal turns"], rows))
    # by category and tier, pooled over enemies
    pooled = {}
    for r in m["records"]:
        sc = r["scalars"]
        if "turns" not in sc:
            continue
        t = int(r["group"].split("@t")[1])
        pooled.setdefault((r.get("category", ""), t), []).append(sc)
    rows = []
    for (c, t), scs in sorted(pooled.items()):
        tv = sorted(s["turns"] for s in scs)
        rows.append([c, t, len(scs), f(sum(tv) / len(tv)), f(pct(tv, 0.5), 0), f(pct(tv, 0.9), 0),
                     f(sum(s["hp_lost"] for s in scs) / len(scs)), f(100 * sum(s["won"] for s in scs) / len(scs), 0)])
    out.append("## By enemy category and tier (pooled over enemies and seeds)\n\n" + table(
        ["category", "tier", "fights", "turns mean", "median", "p90", "HP lost mean", "win %"], rows))
    return "\n".join(out)


def phase_section(m):
    """N19: the per-phase metrics table and its warnings; empty for files without metrics."""
    groups = pm.by_group(m["records"])
    if not any(groups.values()):
        return ""
    lines = ["## Phase metrics (N19)\n", pm.render_table(groups)]
    warn = [w for g, a in sorted(groups.items()) for w in pm.warnings(g, a, boss=m["mode"] == "boss")]
    if warn:
        lines.append("Warnings:\n\n" + "\n".join("- " + w for w in warn) + "\n")
    return "\n".join(lines)


def cmd_report(args):
    m = json.loads(Path(args.file).read_text(encoding="utf-8"))
    text = render_report(m)
    if args.md:
        Path(args.md).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


# --- Compare ----------------------------------------------------------------------------------

HEADLINE = ["won", "turns", "hp_lost", "runs", "raids", "heat_peak", "minutes", "deaths", "died", "schematics_unspent", "schematics_income",
            "taken_per_turn", "dealt_per_turn", "layers", "hp_end_frac", "recruits", "parked", "intake", "resistance_absorbed", "enrage_step",
            "turns_both_share"]


def cmd_compare(args):
    A = json.loads(Path(args.a).read_text(encoding="utf-8"))
    B = json.loads(Path(args.b).read_text(encoding="utf-8"))
    if A["mode"] != B["mode"]:
        print("compare: modes differ (%s vs %s)" % (A["mode"], B["mode"]), file=sys.stderr)
        return 1
    rng = random.Random(BOOT_SEED)
    ma, mb = per_record_means(A["records"]), per_record_means(B["records"])
    rows_out, rows_head, outside, total = [], [], 0, 0
    for g in sorted(set(ma) & set(mb)):
        for k in sorted(set(ma[g]) & set(mb[g])):
            a, b = ma[g][k], mb[g][k]
            if len(a) < 2 or len(b) < 2 or "[" in k:
                continue  # series points are shown in the reports, not compared one by one
            delta, lo, hi = bootstrap_delta(a, b, rng)
            total += 1
            noise = lo <= 0.0 <= hi
            base = sum(a) / len(a)
            rel = ("%+.1f %%" % (100 * delta / base)) if abs(base) > 1e-9 else "-"
            row = [g, k, f(base, 3), f(sum(b) / len(b), 3), "%+.3f" % delta, "[%+.3f, %+.3f]" % (lo, hi), rel, "noise" if noise else "**CHANGED**"]
            if not noise:
                outside += 1
                rows_out.append(row)
            if k in HEADLINE:
                rows_head.append(row)
    head = ["group", "metric", "A mean", "B mean", "delta B-A", "90 % interval", "rel.", "verdict"]
    lines = ["# Balance comparison: %s\n" % args.name,
             "- A: `%s` (overrides: %s)" % (Path(args.a).name, ", ".join(A["overrides"]) or "none"),
             "- B: `%s` (overrides: %s)" % (Path(args.b).name, ", ".join(B["overrides"]) or "none"),
             "- mode %s; A %d records, B %d records; interval = %d-resample bootstrap of the difference of means over the seeds, %d %%" % (
                 A["mode"], len(A["records"]), len(B["records"]), BOOTSTRAP, int(CI * 100)),
             "- %d of %d metrics moved outside the noise (the interval excludes 0)\n" % (outside, total),
             "## Changed outside noise\n", table(head, rows_out) if rows_out else "None: every difference is within noise.\n",
             "## Headline metrics\n", table(head, rows_head)]
    ga, gb = pm.by_group(A["records"]), pm.by_group(B["records"])
    if any(ga.values()) or any(gb.values()):
        both = {}
        for g in sorted(set(ga) | set(gb)):
            both["A " + g], both["B " + g] = ga.get(g), gb.get(g)
        lines += ["## Phase metrics (N19), A then B per group\n", pm.render_table(both)]
    out = Path(args.out) if args.out else ROOT / "docs" / "balance" / ("CMP_%s.md" % args.name)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("compare: %d/%d metrics outside noise -> %s" % (outside, total, out))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, allow_abbrev=False)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", allow_abbrev=False)
    r.add_argument("mode", choices=["campaign", "fight", "boss", "netrun"])
    r.add_argument("--name", required=True)
    r.add_argument("--seeds", default="1000:1004")
    r.add_argument("-j", type=int, default=2)
    r.add_argument("--out-dir", default=str(ROOT / "docs" / "balance" / "runs"))
    r.add_argument("--godot", default="godot")
    r.add_argument("--chunk", type=int, default=0, help="seeds per Godot process (default: 1 for campaign/boss)")
    rp = sub.add_parser("report")
    rp.add_argument("file")
    rp.add_argument("--md")
    c = sub.add_parser("compare")
    c.add_argument("a")
    c.add_argument("b")
    c.add_argument("--name", required=True)
    c.add_argument("--out")
    args, rest = ap.parse_known_args()
    if args.cmd == "run":
        return cmd_run(args, rest)
    if rest:
        ap.error("unknown arguments: %s" % rest)
    return cmd_report(args) if args.cmd == "report" else cmd_compare(args)


if __name__ == "__main__":
    sys.exit(main())
