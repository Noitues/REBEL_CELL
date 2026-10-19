"""Check a candidate plate against the golden-plate measures without touching the committed set.

python gcheck.py <stem> <plate.png> <index.npy> [outdir]
stem = a golden plate stem (hq_halcyon_overview ...). Writes the four plate files to outdir (default D:/rc_scratch/hq_fix/chk) and prints
the values and every non-pass check. Camera, class map and provenance come from build_all.entries().
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import build_all as BA  # noqa: E402
import make_plate as MP  # noqa: E402


def check(stem, plate, index, out="D:/rc_scratch/hq_fix/chk"):
    e = next(x for x in BA.entries() if x["stem"] == stem)
    e["beauty"] = plate
    e["index"] = index
    r = MP.build_plate(e, out)
    v = r["vals"]
    st = v["checks"]["status"]
    print("%s med %.4f u10 %.4f o85 %.4f ratio %s peak %s align %s" % (
        stem, v["median"], v["under_010"], v["over_085"], MP.r4(v["ratio_median"]), MP.r4(v["ratio_peak"]), MP.r4(r["align"])))
    print("  not pass:", {k: s for k, s in st.items() if s not in ("pass", "n/a")})
    print("  comp:", {k: MP.r4(x) for k, x in v["composition"].items() if x is not None})
    return r


if __name__ == "__main__":
    check(*sys.argv[1:])
