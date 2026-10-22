"""GPU final of the manta detail pass under the shared FIFO lock, with a 15-minute no-progress watchdog on our own Blender PID.
python run_final.py <tag> <res_k> <spp> [target_median]       1920 x 1080 = res_k 1.5
Progress = growth of blender.log or any new file in the output dir; if neither changes for 15 min, only our own PID is killed (taskkill /PID /T).
The lock is held for this one render only and released in a finally block (ours only)."""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
AB = os.path.normpath(os.path.join(HERE, "..", "..", "tethys_abyssal", "scripts"))
sys.path.insert(0, AB)
sys.dont_write_bytecode = True
import gpu_lock as GL  # noqa: E402

S = "D:/rc_scratch/hq_styles/tethys_ideas"
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
tag, rk, spp = sys.argv[1], sys.argv[2], sys.argv[3]
tg = sys.argv[4] if len(sys.argv) > 4 else "0.16"
out = os.path.join(S, tag)
os.makedirs(out, exist_ok=True)
GL.acquire("tethys manta v2 final %s spp %s" % (rk, spp), poll=180)
t0 = time.time()
try:
    env = dict(os.environ, IDEA=os.environ.get("IDEA", "M"), TETHYS_SCR="D:/rc_scratch/hq_styles/tethys_abyssal/scr", TETHYS_BORDER="",
               FILL_ZONED=S + "/zoned_fill.json", SHADOW_JSON=out + "/shadow.json")
    env.pop("TETHYS_CPU", None)
    logp = os.path.join(out, "blender.log")
    with open(logp, "w") as f:
        pr = subprocess.Popen([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "ideas_build.py"), "--", "aaa", "t_over", out, rk, spp],
                              stdout=f, stderr=subprocess.STDOUT, env=env)
    last_sig, last_t = None, time.time()
    while pr.poll() is None:
        time.sleep(30)
        sig = (os.path.getsize(logp), len(os.listdir(out)), max(os.path.getmtime(os.path.join(out, n)) for n in os.listdir(out)))
        if sig != last_sig:
            last_sig, last_t = sig, time.time()
        elif time.time() - last_t > 15 * 60:
            print("watchdog: no progress for 15 min, killing our own blender PID", pr.pid, flush=True)
            subprocess.run(["taskkill", "/PID", str(pr.pid), "/T", "/F"])
            break
    print("blender exit", pr.poll(), "wall %.0f s" % (time.time() - t0), flush=True)
finally:
    GL.release()
subprocess.run([sys.executable, os.path.join(AB, "abyssal_post.py"), out + "/t_over_aaa", out + "/plate.png", tg])
subprocess.run([sys.executable, os.path.join(HERE, "manta_post.py"), out + "/plate.png", out + "/shadow.json", out + "/t_over_aaa_index.npy", out + "/plate_sh.png", "0.8"])
print("done %.0f s" % (time.time() - t0), flush=True)
