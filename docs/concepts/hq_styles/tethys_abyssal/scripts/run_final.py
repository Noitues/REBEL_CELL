"""GPU final under the shared lock (D:/rc_scratch/GPU_QUEUE.md): acquire, render, release (ours only), post.
python run_final.py <tag> <res_k> <spp> [target_median]      1920x1080 = res_k 1.5
"""
import os
import subprocess
import sys
import time

import gpu_lock as GL

HERE = os.path.dirname(os.path.abspath(__file__))
S = "D:/rc_scratch/hq_styles/tethys_abyssal"
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

tag, rk, spp = sys.argv[1], sys.argv[2], sys.argv[3]
tg = sys.argv[4] if len(sys.argv) > 4 else "0.16"
out = os.path.join(S, tag)
os.makedirs(out, exist_ok=True)
GL.acquire("tethys abyssal final %s spp %s" % (rk, spp), poll=180)
t0 = time.time()
try:
    env = dict(os.environ, TETHYS_SCR=S + "/scr", TETHYS_BORDER="")
    env.pop("TETHYS_CPU", None)
    with open(os.path.join(out, "blender.log"), "w") as f:
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "abyssal_build.py"), "--", "aaa", "t_over", out, rk, spp],
                           stdout=f, stderr=subprocess.STDOUT, env=env)
    print("blender exit", r.returncode, "wall %.0f s" % (time.time() - t0), flush=True)
finally:
    GL.release()
subprocess.run([sys.executable, os.path.join(HERE, "abyssal_post.py"), out + "/t_over_aaa", out + "/plate.png", tg])
