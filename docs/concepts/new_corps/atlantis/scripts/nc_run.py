"""Launch one headless Blender job (never Godot; never the designer's live Blender). Logs go to D:/rc_scratch.

python nc_run.py <scene.py> <shot> <eevee|cycles> <WxH> [key=value ...]
Cycles jobs refuse to start unless D:/rc_scratch/GPU_LOCK names new_corps (the GPU queue protocol).
"""
import json
import os
import subprocess
import sys
import time

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
SCR = r"D:\rc_scratch\new_corps"
LOCK = r"D:\rc_scratch\GPU_LOCK"


def main():
    scene, shot, eng, res = sys.argv[1:5]
    extra = sys.argv[5:]
    w, h = [int(v) for v in res.lower().split("x")]
    corp = os.path.basename(os.path.dirname(HERE))
    tag = "final" if eng == "cycles" else "prev"
    out = os.path.join(SCR, corp, "%s_%s" % (shot, tag)).replace("\\", "/")
    for e in extra:
        if e.startswith("out="):
            out = os.path.join(SCR, corp, json.loads(e[4:])).replace("\\", "/")
    extra = [e for e in extra if not e.startswith("out=")]
    if eng == "cycles" and "cpu=true" not in extra:
        if not os.path.exists(LOCK) or "new_corps" not in open(LOCK, encoding="utf-8", errors="ignore").read():
            print("refused: GPU_LOCK is not held by new_corps")
            sys.exit(2)
    os.makedirs(os.path.join(SCR, "logs"), exist_ok=True)
    logp = os.path.join(SCR, "logs", "%s_%s_%s.log" % (corp, shot, tag))
    cmd = [BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, scene), "--",
           "shot=" + json.dumps(shot), "engine=" + json.dumps(eng), "res=" + json.dumps([w, h]), "out=" + json.dumps(out)] + extra
    t = time.time()
    with open(logp, "w", encoding="utf-8") as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    print("exit", r.returncode, "%.1fs" % (time.time() - t), "log", logp, "out", out)
    with open(logp, encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()
    for ln in lines:
        if "Error" in ln or "Traceback" in ln or "[nc]" in ln or "error" in ln.lower()[:40]:
            print("  ", ln[:240])
    if r.returncode != 0:
        print("\n".join(lines[-25:]))


if __name__ == "__main__":
    main()
