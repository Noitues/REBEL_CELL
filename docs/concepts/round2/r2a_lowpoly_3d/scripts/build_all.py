"""R2A LOW-POLY 3D: render all five stills, post-process them, and make the contact sheet.

python build_all.py [only_id ...]      e.g. python build_all.py 04
Raw renders go to R2A_SCRATCH (default: ../_tmp, deleted afterwards).
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "stills"))
TMP = os.environ.get("R2A_SCRATCH", os.path.normpath(os.path.join(HERE, "..", "_tmp")))
BLENDER = os.environ.get("BLENDER", r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")

JOBS = [
    ("01", "01_city_day.png", "still_city.py", ["day"], "day"),
    ("02", "02_city_night.png", "still_city.py", ["night"], "night"),
    ("03", "03_city_suspicion.png", "still_city.py", ["alert"], "alert"),
    ("04", "04_combat.png", "still_combat.py", [], "combat"),
    ("05", "05_shop.png", "still_shop.py", [], "shop"),
]


def main():
    only = set(sys.argv[1:])
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    for jid, name, script, pre, grade in JOBS:
        if only and jid not in only:
            continue
        raw = os.path.join(TMP, "raw_" + name)
        log = os.path.join(TMP, "log_" + jid + ".txt")
        cmd = [BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, script), "--"] + pre + [raw]
        with open(log, "w") as fh:
            subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, timeout=900, check=False)
        if not os.path.exists(raw):
            print("FAILED", jid, "see", log)
            continue
        subprocess.run([sys.executable, os.path.join(HERE, "post.py"), raw, os.path.join(OUT, name), grade], check=True)
    subprocess.run([sys.executable, os.path.join(HERE, "contact_sheet.py")], check=True)
    if TMP.endswith("_tmp") and os.path.isdir(TMP):
        shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
