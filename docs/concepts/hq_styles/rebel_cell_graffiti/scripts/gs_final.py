"""Final exterior: take the GPU lock (FIFO), render with Cycles HIP, release, then post.

python gs_final.py <res_w> <spp>      -> D:/rc_scratch/hq_styles/rebel_cell_graffiti/final_*
"""
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpu_lock as GL

S = r"D:/rc_scratch/hq_styles/rebel_cell_graffiti"
B = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
res, spp = sys.argv[1], sys.argv[2]
log = open(S + "/final_run.log", "a")


def lg(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(s, flush=True)
    log.write(s + "\n")
    log.flush()


GL.acquire("graffiti shop exterior %sx spp %s" % (res, spp), poll=150, log=lg)
try:
    t0 = time.time()
    with open(S + "/final_blender.log", "w") as f:
        p = subprocess.Popen([B, "-b", "--factory-startup", "--python", os.path.join(HERE, "gs_scene.py"), "--", S + "/final", res, spp],
                             stdout=f, stderr=subprocess.STDOUT, env=dict(os.environ, GS_TIME_LIMIT="1080"))
        lg("blender pid", p.pid)
        while p.poll() is None:
            if time.time() - t0 > 20 * 60:
                lg("over 20 min: killing own blender pid", p.pid)
                p.kill()
                break
            time.sleep(5)
    lg("render exit", p.returncode, "wall %.0f s" % (time.time() - t0))
finally:
    GL.release(log=lg)
