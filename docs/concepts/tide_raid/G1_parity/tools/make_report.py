"""Builds metrics.md from the per-iteration metrics JSON files of parity_compare.py.
usage: python make_report.py <sheets dir> <out.md> iter_name ...  (the last name is the final one: its full per-band table and tolerance check are written)
Written as a file (no python from stdin)."""
import json
import os
import sys

sys.dont_write_bytecode = True

TOL = {"luma": 0.05, "sat": 0.08, "warm": 0.10, "light_points": 0.15, "refl_energy": 0.20}
BANDS = ["all", "top", "mid", "bottom", "left", "right"]


def rel(g, t):
    return (g - t) / t if t else 0.0


def main():
    d, out, names = sys.argv[1], sys.argv[2], sys.argv[3:]
    runs = [json.load(open(os.path.join(d, n + "_metrics.json"))) for n in names]
    L = ["# Parity metrics (live Godot city vs the plate city)", "",
         "Godot = the raid city at the plate camera (tools/look_parity/parity_capture.gd). Target = the offline plate pipeline on the same capture with no beams, UI or pressure layers, plus the plate's own Blender light-spill layer (tools/look_parity/make_city_target.py). Tolerances: luma +-5 %, saturation +-8 %, warm share +-10 %, light points +-15 %, street-reflection energy +-20 %, hue histogram distance small.", "",
         "## Every iteration (whole frame)", "", "| iteration | score | luma G/T | sat G/T | warm G/T | light points G/T | reflection G/T | hue L1 |", "|---|---|---|---|---|---|---|---|"]
    for r in runs:
        g, t = r["godot"]["all"], r["target"]["all"]
        hl1 = sum(abs(a - b) for a, b in zip(g["hue_hist"], t["hue_hist"]))
        L.append("| %s | %.4f | %.3f / %.3f (%+.0f %%) | %.3f / %.3f (%+.0f %%) | %.3f / %.3f (%+.0f %%) | %d / %d (%+.0f %%) | %.3f / %.3f (%+.0f %%) | %.3f |" % (
            r["name"], r["score"], g["luma"], t["luma"], 100 * rel(g["luma"], t["luma"]), g["sat"], t["sat"], 100 * rel(g["sat"], t["sat"]), g["warm"], t["warm"], 100 * rel(g["warm"], t["warm"]),
            g["light_points"], t["light_points"], 100 * rel(g["light_points"], t["light_points"]), g["refl_energy"], t["refl_energy"], 100 * rel(g["refl_energy"], t["refl_energy"]), hl1))
    f = runs[-1]
    L += ["", "## Final iteration `%s`, per band" % f["name"], "", "| band | metric | Godot | target | plate | error | tolerance | ok |", "|---|---|---|---|---|---|---|---|"]
    for b in BANDS:
        for m, tol in TOL.items():
            g, t, p = f["godot"][b][m], f["target"][b][m], f["plate"][b][m]
            e = rel(g, t)
            ok = abs(e) <= tol
            L.append("| %s | %s | %.3f | %.3f | %.3f | %+.1f %% | +-%d %% | %s |" % (b, m, g, t, p, 100 * e, int(tol * 100), "yes" if ok else "NO"))
        hl1 = sum(abs(a - c) for a, c in zip(f["godot"][b]["hue_hist"], f["target"][b]["hue_hist"]))
        L.append("| %s | hue histogram L1 | %.3f | | | | | |" % (b, hl1))
    open(out, "w", newline="\n").write("\n".join(L) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
