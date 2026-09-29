"""Rebuild every RISO PUNK ZINE still from scratch: textures -> Blender renders -> print pass
-> contact sheet. Intermediates go to a work dir outside the concept folder.

python build_all.py [work_dir]
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STILLS = os.path.join(ROOT, "stills")
WORK = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.environ.get("TEMP", "/tmp"), "c_riso_zine_work")
TEX = os.path.join(WORK, "tex")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
os.makedirs(TEX, exist_ok=True)
os.makedirs(STILLS, exist_ok=True)


def run(args, log):
    with open(os.path.join(WORK, log), "w") as f:
        r = subprocess.run(args, stdout=f, stderr=subprocess.STDOUT, timeout=900)
    if r.returncode != 0:
        raise SystemExit(f"failed: {args} (see {log})")


def blend(script, *extra, log):
    run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, script), "--", TEX, *extra], log)


def post(src, dst, *flags):
    run([sys.executable, os.path.join(HERE, "post.py"), src, os.path.join(STILLS, dst), *flags], "post_" + dst + ".log")


run([sys.executable, os.path.join(HERE, "make_textures.py"), TEX], "tex.log")
w = lambda n: os.path.join(WORK, n)
blend("still_01_combat.py", w("raw_01.png"), log="r01.log")
post(w("raw_01.png"), "01_combat.png", "--seed", "1")
blend("still_02_city.py", w("raw_02.png"), "base", log="r02.log")
blend("still_02_city.py", w("ov_02.png"), "overlay", log="o02.log")
post(w("raw_02.png"), "02_city_night.png", "--tiltshift", "0.3,0.85", "--overlay", w("ov_02.png"), "--seed", "2")
blend("still_03_heat.py", w("raw_03.png"), "base", log="r03.log")
blend("still_03_heat.py", w("ov_03.png"), "overlay", log="o03.log")
post(w("raw_03.png"), "03_heat.png", "--tiltshift", "0.3,0.85", "--overlay", w("ov_03.png"), "--glitch", "0.5", "--hunted", "--seed", "3")
blend("still_04_modem.py", w("raw_04.png"), log="r04.log")
post(w("raw_04.png"), "04_hq_modem.png", "--seed", "4")
blend("still_05_marker_strip.py", w("raw_05.png"), log="r05.log")
post(w("raw_05.png"), "05_marker_strip.png", "--seed", "5")
run([sys.executable, os.path.join(HERE, "contact_sheet.py")], "sheet.log")
print("done ->", STILLS)
