"""Builds perf.md from the PERF lines of the run_perf.sh logs. usage: python make_perf.py <perf dir> <out.md> <notes...>. Written as a file (no python from stdin)."""
import os
import re
import sys

sys.dont_write_bytecode = True
d, out = sys.argv[1], sys.argv[2]


def grab(name):
    p = os.path.join(d, "log_%s.log" % name)
    if not os.path.exists(p):
        return None
    t = open(p, errors="replace").read()
    r = {}
    for kind in ("wall", "gpu_city", "gpu_window"):
        m = re.search(r"PERF name=%s .*?%s mean_ms=([0-9.]+) p50_ms=([0-9.]+) p95_ms=([0-9.]+) p99_ms=([0-9.]+) max_ms=([0-9.]+)" % (re.escape(name), kind), t)
        if m:
            r[kind] = [float(x) for x in m.groups()]
    return r


rows = [("legacy post (grade off, level 0)", "perf_legacy"), ("level 1 (lite)", "perf_l1"), ("level 2 (+ wet reflections, shafts, pool glow)", "perf_l2"), ("level 3 (full, 2D finish)", "perf_l3"),
        ("level 3 without wet reflection (lamp streaks, light taps, sheen)", "perf_off4"), ("level 3 without bloom", "perf_off8"), ("level 3 without rain", "perf_off16"), ("level 3 without lamp pools", "perf_off1"), ("level 3 without bloom and rain", "perf_off28")]
L = ["# Perf: the raid city at the plate camera", "", "RX 6700 XT, 1920 x 1080 window through `tools/run_windowed.py` (the window stays at its 60 Hz cap, so wall clock only shows p95 headroom). The numbers that count are the GPU times from `RenderingServer.viewport_get_measured_render_time_gpu` (city view = the 3D viewport; window = the 2D finish and UI). Other agents were rendering on the machine; GPU lock held during every capture batch.", "",
     "| configuration | city GPU mean | p50 | p95 | p99 | window GPU p50 | wall p95 |", "|---|---|---|---|---|---|---|"]
for label, name in rows:
    r = grab(name)
    if not r or "gpu_city" not in r:
        L.append("| %s | (not run) | | | | | |" % label)
        continue
    g = r["gpu_city"]
    w = r.get("gpu_window", [0, 0, 0, 0, 0])
    wl = r.get("wall", [0, 0, 0, 0, 0])
    L.append("| %s | %.2f ms | %.2f | %.2f | %.2f | %.2f | %.2f |" % (label, g[0], g[1], g[2], g[3], w[1], wl[2]))
L += [""] + sys.argv[3:]
open(out, "w", newline="\n").write("\n".join(L) + "\n")
print("wrote", out)
