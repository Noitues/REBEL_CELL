"""Render all five stills + the contact sheet.

  python build_all.py [samples]      (default 32; intermediates go to a temp folder and are deleted)
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
STILLS = os.path.join(ROOT, "stills")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
SAMPLES = sys.argv[1] if len(sys.argv) > 1 else "32"
TMP = tempfile.mkdtemp(prefix="r2e_", dir=os.environ.get("R2E_TMP"))


def blender(script, *args):
    log = os.path.join(TMP, os.path.basename(script) + "_" + "_".join(a for a in args[1:2]) + ".log")
    with open(log, "w") as f:
        subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, script), "--", *args],
                       stdout=f, stderr=subprocess.STDOUT, timeout=900, check=True)
    print("done", script, args[:2])


def post(*args):
    subprocess.run([sys.executable, os.path.join(HERE, "post.py"), *args], check=True, timeout=300)


def t(name):
    return os.path.join(TMP, name)


def s(name):
    return os.path.join(STILLS, name)


os.makedirs(STILLS, exist_ok=True)
blender("scene_city.py", t("day.png"), "day", SAMPLES, "1")
blender("scene_city.py", t("night.png"), "night", SAMPLES, "1")
blender("scene_city.py", t("alarm.png"), "alarm", SAMPLES, "1")
blender("scene_city.py", t("plate.png"), "night", SAMPLES, "0")
blender("scene_combat.py", t("combat_fg.png"), SAMPLES)
blender("scene_shop.py", t("shop_fg.png"), SAMPLES)
post("city", t("day.png"), s("01_city_day.png"), "day")
post("city", t("night.png"), s("02_city_night.png"), "night")
post("city", t("alarm.png"), s("03_city_suspicion.png"), "alarm")
post("over", t("plate.png"), t("combat_fg.png"), s("04_combat.png"), "combat")
post("over", t("plate.png"), t("shop_fg.png"), s("05_shop.png"), "shop")
subprocess.run([sys.executable, os.path.join(HERE, "contact_sheet.py")], check=True, timeout=300)
shutil.rmtree(TMP, ignore_errors=True)
print("ALL DONE")
