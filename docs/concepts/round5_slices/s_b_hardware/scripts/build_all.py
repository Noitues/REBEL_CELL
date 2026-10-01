"""Rebuild every deliverable: textures -> Blender renders -> compose -> fx.

python build_all.py [samples]      (WORK dir from $SBH_WORK, default %TEMP%/sbh_work)
"""
import os
import subprocess
import sys

import common as C

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
HERE = os.path.dirname(os.path.abspath(__file__))


def run(args, log=None):
    print(">", " ".join(args))
    if log:
        with open(log, "w") as f:
            subprocess.run(args, check=True, stdout=f, stderr=subprocess.STDOUT, cwd=HERE, timeout=900)
    else:
        subprocess.run(args, check=True, cwd=HERE, timeout=900)


def main():
    samples = sys.argv[1] if len(sys.argv) > 1 else "96"
    os.makedirs(C.WORK, exist_ok=True)
    run([sys.executable, "make_textures.py"])
    for job in ("sheet", "player", "enemy"):
        run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "blend_tiles.py"), "--",
             job, os.path.join(C.WORK, job + ".png"), samples], log=os.path.join(C.WORK, job + ".log"))
    run([sys.executable, "compose.py"])
    run([sys.executable, "fx.py"])


if __name__ == "__main__":
    main()
