"""Render every S2 3D asset tile (transparent PNGs) with Blender, 3 processes at a time.

usage: python build_items.py <tile_dir> [samples] [item ...]
"""
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
OUT = sys.argv[1]
SAMPLES = sys.argv[2] if len(sys.argv) > 2 else "24"
SIZE = {"op": 512, "en": 640, "bz": 512, "lm": 720, "th": 512, "cu": 320, "ca": 512, "it": 512, "gem": 256}
ITEMS = ["op_%s_%s" % (c, s) for c in ("breaker", "ghost") for s in ("neutral", "hurt", "triumphant", "flatlined")]
ITEMS += ["en_manifest", "en_adjuster", "en_drone", "bz_meridian", "bz_solace", "lm_ziggurat", "lm_pyramid", "lm_tether",
          "th_bailiff", "th_courier", "th_customs", "cu_cycles", "cu_schematics", "cu_ram", "cu_heat", "ca_backspin",
          "ca_arcflash", "ca_bulwark", "ca_back", "it_daemon", "it_chip", "it_slice", "gem_ram"]
if len(sys.argv) > 3:
    ITEMS = sys.argv[3:]
os.makedirs(OUT, exist_ok=True)


def run(item):
    px = SIZE[item.split("_")[0]]
    log = os.path.join(OUT, item + ".log")
    with open(log, "w") as f:
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "render_item.py"), "--",
                            item, os.path.join(OUT, item + ".png"), str(px), SAMPLES],
                           stdout=f, stderr=subprocess.STDOUT, timeout=900)
    ok = os.path.exists(os.path.join(OUT, item + ".png")) and "Traceback" not in open(log).read()
    print(("ok   " if ok else "FAIL ") + item, flush=True)
    return ok


with ThreadPoolExecutor(3) as ex:
    res = list(ex.map(run, ITEMS))
print("ALL OK" if all(res) else "SOME FAILED")
