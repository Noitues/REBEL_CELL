"""r3 loop: the static media for the loop, rendered through the still's own volume pass (render_aaa.py) so they match
the still exactly, with every medium together. (Rendering the strata alone came out ~5x brighter: with overlapping
volume objects, a light linked to one medium only lights the parts its receivers dominate, so the media must not be
split; the 2D drift is applied to the sum.)

python loop_media.py  ->  ../scratch/loop/{vol_static,beams_full}_combined.npy (1280 x 720)
"""
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LD = os.path.join(ROOT, "scratch", "loop")
CASES = [
    # every medium together (as in the still: with overlapping media, a light linked to one medium only lights the
    # parts its receivers dominate, so splitting the media changes the look; the drift is done in 2D on the sum)
    ("vol_static", ['hide_prefix="beam_"']),
    ("beams_full", ['vol_only_prefix="beam_"']),
]


def main():
    for name, extra in CASES:
        t0 = time.time()
        args = [sys.executable, os.path.join(HERE, "jobs_aaa.py"), "real", "test", "idle", "vol", "hiprt=false",
                "vol_res=[1280,720]", "vol_samples=48", "out=loop_media_" + name] + extra
        with open(os.path.join(ROOT, "scratch", "run_media_%s.txt" % name), "w") as f:
            subprocess.run(args, stdout=f, stderr=subprocess.STDOUT)
        src = os.path.join(ROOT, "scratch", "loop_media_" + name, "O_overview_vol_combined.npy")
        shutil.copyfile(src, os.path.join(LD, name + "_combined.npy"))
        print(name, "%.0f s" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
