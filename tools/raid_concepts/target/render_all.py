"""Render the raid target frames in headless Blender, then composite them.

    python render_all.py [--frames plan,reveal,impact] [--res 1920x1080] [--samples 48]
                         [--out D:/rc_tmp/raid_design_lab/target/final] [--no-composite]
"""
import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
TARGET = "D:/rc_tmp/raid_design_lab/target"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default="plan,reveal,impact")
    ap.add_argument("--res", default="1920x1080")
    ap.add_argument("--samples", default="48")
    ap.add_argument("--out", default=TARGET + "/final")
    ap.add_argument("--no-composite", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for f in a.frames.split(","):
        t0 = time.time()
        log = os.path.join(TARGET, "blender_%s.log" % f)
        with open(log, "w") as lf:
            subprocess.run([BLENDER, "-b", "--factory-startup", "-P", os.path.join(HERE, "raid_scene.py"), "--",
                            f, a.out, "--res", a.res, "--samples", a.samples],
                           stdout=lf, stderr=subprocess.STDOUT, check=False)
        txt = open(log, errors="ignore").read()
        ok = "RENDERED" in txt
        print(f, "ok" if ok else "FAILED", "%.0fs" % (time.time() - t0))
        if not ok:
            i = txt.find("Traceback")
            print(txt[i:i + 1500] if i >= 0 else txt[-1500:])
            sys.exit(1)
    if not a.no_composite:
        subprocess.run([sys.executable, os.path.join(HERE, "composite.py"), "--dir", a.out, "--frames", a.frames], check=True)


if __name__ == "__main__":
    main()
