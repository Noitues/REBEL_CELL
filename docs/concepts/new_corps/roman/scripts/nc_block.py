"""New corps: one GPU block (designer-approved queue jump, about 45 min). Waits for the current holder to release
D:/rc_scratch/GPU_LOCK, takes it (exclusive create), renders the finals in priority order, composes each, and releases
the lock when done or when the budget runs out (no new job starts after `budget` minutes).

python nc_block.py [budget=40] [jobs=aurelian:hq,tethys:hq,aurelian:district,tethys:district,aurelian:street,tethys:street]
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
NC = os.path.dirname(os.path.dirname(HERE))
SCR = r"D:\rc_scratch\new_corps"
LOCK = r"D:\rc_scratch\GPU_LOCK"
WAIT = r"D:\rc_scratch\GPU_WAITING_new_corps"
CORP = {"aurelian": ("roman", "roman_scene.py", "night"), "tethys": ("atlantis", "tethys_scene.py", "deep")}
SAMPLES = {"aurelian": 96, "tethys": 64}


def say(*a):
    line = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(line, flush=True)
    with open(os.path.join(SCR, "render_log.txt"), "a", encoding="utf-8") as f:
        f.write(line + "\n")


def take_lock():
    while True:
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, ("new_corps %s block (designer-approved jump)" % time.strftime("%Y-%m-%d %H:%M:%S")).encode())
            os.close(fd)
            if os.path.exists(WAIT):
                os.remove(WAIT)
            return
        except FileExistsError:
            time.sleep(20)


def main():
    kw = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
    budget = float(kw.get("budget", 40)) * 60
    jobs = [j.split(":") for j in kw.get("jobs", "aurelian:hq,tethys:hq,aurelian:district,tethys:district,aurelian:street,tethys:street").split(",")]
    say("waiting for the lock")
    take_lock()
    t0 = time.time()
    say("lock taken")
    try:
        for corp, shot in jobs:
            if time.time() - t0 > budget:
                say("budget reached, skipping", corp, shot)
                continue
            folder, scene, look = CORP[corp]
            sd = os.path.join(NC, folder, "scripts")
            t = time.time()
            r = subprocess.run([sys.executable, "nc_run.py", scene, shot, "cycles", "2560x1440", "samples=%d" % SAMPLES[corp]],
                               cwd=sd, capture_output=True, text=True)
            say(corp, shot, "render exit", r.returncode, "%.0f s" % (time.time() - t), r.stdout.strip().splitlines()[0] if r.stdout.strip() else "")
            if r.returncode != 0:
                say(r.stdout[-1500:])
                continue
            base = os.path.join(SCR, folder, "%s_final" % shot).replace("\\", "/")
            if shot == "district":
                args = ["nc_post.py", base + ".npy", os.path.join(NC, folder, "district.png"), "look=" + look,
                        "exposure=" + ("0.6" if look == "deep" else "1.0")]
            else:
                args = ["nc_compose.py", corp, shot, "plate=" + base + ".npy", "json=" + base + ".json", "res=[2560,1440]"]
            c = subprocess.run([sys.executable] + args, cwd=sd, capture_output=True, text=True)
            say(corp, shot, "compose exit", c.returncode, (c.stdout.strip().splitlines() or [""])[-1])
            if c.returncode != 0:
                say(c.stderr[-1500:])
    finally:
        if os.path.exists(LOCK) and "new_corps" in open(LOCK, encoding="utf-8", errors="ignore").read():
            os.remove(LOCK)
        say("lock released after %.1f min" % ((time.time() - t0) / 60))


if __name__ == "__main__":
    main()
