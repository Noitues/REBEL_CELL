"""Round 42: prepare the window views (the locked canyon renders, caption bar cropped off) and render
the HQ room in Blender for the home and DISPATCH variants.

python run_room.py [home|dispatch|all]
"""
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONCEPTS = os.path.dirname(ROOT)
SCR = os.path.join(ROOT, "scratch", "room")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
VIEWS = {"home": os.path.join(CONCEPTS, "round30_rebel_cell", "canyon_home.jpg"),
         "dispatch": os.path.join(CONCEPTS, "round34_rebel_cell", "canyon_dispatch.jpg")}


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    os.makedirs(SCR, exist_ok=True)
    for v in ("home", "dispatch"):
        if which not in (v, "all"):
            continue
        im = Image.open(VIEWS[v]).convert("RGB").crop((0, 60, 1920, 1080)).resize((1920, 1080), Image.LANCZOS)
        wp = os.path.join(SCR, "view_%s.png" % v)
        im.save(wp)
        log = os.path.join(SCR, "blender_%s.log" % v)
        with open(log, "w") as lf:
            subprocess.run([BLENDER, "-b", "--factory-startup", "-P", os.path.join(HERE, "hq_scene.py"), "--", SCR, wp, v],
                           stdout=lf, stderr=subprocess.STDOUT, check=False)
        txt = open(log, errors="ignore").read()
        print(v, "ok" if "RENDERED" in txt else "FAILED")
        if "Traceback" in txt:
            i = txt.index("Traceback")
            print(txt[i:i + 2500])


if __name__ == "__main__":
    main()
