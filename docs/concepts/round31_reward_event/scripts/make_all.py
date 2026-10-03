"""Round 31: rebuild everything (slice tiles + wheels, the two Blender busts, every screen, the GIF, the sheet).

python make_all.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.join(os.path.dirname(HERE), "scratch")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


def run(*args):
    print(">", " ".join(args), flush=True)
    subprocess.run(list(args), cwd=HERE, check=True)


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    run(sys.executable, "assets.py")
    for v in ("breaker", "fixer"):
        run(BLENDER, "-b", "--factory-startup", "-P", "bust_blender.py", "--", os.path.join(SCRATCH, "bust_%s.png" % v), v)
    for s in ("reward.py", "server_rack.py", "event.py", "dialogue.py", "netrun_map.py", "shop.py", "contact.py"):
        run(sys.executable, s)


if __name__ == "__main__":
    main()
