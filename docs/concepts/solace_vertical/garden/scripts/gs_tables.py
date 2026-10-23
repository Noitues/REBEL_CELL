"""Markdown tables for NOTES.md from the finals' info jsons: slot geometry per level (x, y, z extents in lot BU, slot counts and widths), render times and post values."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import types
sys.modules.setdefault("bpy", types.ModuleType("bpy"))
import gs_garden as GG  # noqa: E402

O = "D:/rc_scratch/solace_v1/garden/out/"
for k in "ABC":
    info = json.load(open(O + "F_inside_%s_info.json" % k))
    lev = info["levels"]
    for n, lv in lev.items():
        for key in ("x", "y", "z"):
            lv[key] = tuple(lv[key])
    SL = GG.slot_list(lev)
    print("\n### %s slots (lot frame BU: x across, y depth from the front edge -21, z up)" % k)
    print("| level | x | y | z | height | nodes | slot width | note |")
    print("|---|---|---|---|---|---|---|---|")
    NAME = {"I1": "ground hall", "I2": "lower terrace", "I3": "upper terrace", "I4": "glasshouse", "I5": "seed vault"}
    for n in ("I1", "I2", "I3", "I4", "I5"):
        lv = lev[n]
        w = SL[n][0][1] if n != "I5" else SL[n][0][1]
        print("| %s %s | %.1f..%.1f | %.1f..%.1f | %.1f..%.1f | %.1f | %d | %.1f | %s |" % (n, NAME[n], lv["x"][0], lv["x"][1], lv["y"][0], lv["y"][1], lv["z"][0], lv["z"][1], lv["z"][1] - lv["z"][0],
                                                                                            GG.SLOT_N[n], w, "LARGE slot (target Rack)" if n == "I5" else ""))
    if "I3_workshop" in lev:
        lw = lev["I3_workshop"]
        print("\nWORKSHOP alcove (I3 last slot): x %.1f..%.1f, y %.1f..%.1f, z %.1f..%.1f" % (lw["x"][0], lw["x"][1], lw["y"][0], lw["y"][1], lw["z"][0], lw["z"][1]))
print("\n### render times (Cycles HIP, s) and post values")
for v in ("street", "inside"):
    for k in "ABC":
        i = json.load(open(O + "F_%s_%s_info.json" % (v, k)))
        pj = json.load(open(O + "F_%s_%s.png.json" % (v, k)))
        print("- %s %s: %.1f s, %s, exposure %.2f, median %.4f, under 0.10 %.3f, over 0.85 %.4f" % (v, k, i["render_seconds"], "x".join(map(str, i["size"])), pj["exposure"], pj["median"], pj["under10"], pj["over85"]))
