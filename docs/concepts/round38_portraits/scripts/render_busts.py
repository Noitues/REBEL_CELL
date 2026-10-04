"""Round 38: write the bust job list and run bust_rig.py once in Blender (headless).
python render_busts.py [classes|states|contacts|all]
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "scratch", "busts")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
CLASSES = ["breaker", "wrecker", "ghost", "phantom", "rigger", "overclocker", "botnet", "hivemind"]
SEEDS = [1, 2, 3]


def jobs(which):
    j = []
    if which in ("classes", "all"):
        for c in CLASSES:
            for s in SEEDS:
                j.append(dict(name="%s_%d" % (c, s), cls=c, seed=s))
    if which in ("states", "all"):
        j.append(dict(name="state_talk", cls="rigger", seed=1, mouth="open"))
        j.append(dict(name="state_hurt", cls="rigger", seed=1, mouth="grimace", eyes="squint"))
        j.append(dict(name="state_dead", cls="rigger", seed=1, eyes="shut"))
    if which in ("contacts", "all"):
        j.append(dict(name="contact_fixer", cls="fixer", seed=4))
        j.append(dict(name="contact_merc", cls="merc", seed=5))
        j.append(dict(name="contact_merc_talk", cls="merc", seed=5, mouth="open"))
    return j


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    os.makedirs(OUT, exist_ok=True)
    jf = os.path.join(os.path.dirname(OUT), "jobs_%s.json" % which)
    with open(jf, "w") as f:
        json.dump(jobs(which), f)
    log = os.path.join(os.path.dirname(OUT), "blender_%s.log" % which)
    with open(log, "w") as lf:
        subprocess.run([BLENDER, "-b", "--factory-startup", "-P", os.path.join(HERE, "bust_rig.py"), "--", jf, OUT],
                       stdout=lf, stderr=subprocess.STDOUT, check=False)
    txt = open(log, errors="ignore").read()
    print("rendered", txt.count("RENDERED"), "errors:", "Traceback" in txt)
    if "Traceback" in txt:
        i = txt.index("Traceback")
        print(txt[i:i + 2000])


if __name__ == "__main__":
    main()
