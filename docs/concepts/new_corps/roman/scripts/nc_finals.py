"""New corps: the final Cycles batch (both corps) and the composes. Run ONLY while D:/rc_scratch/GPU_LOCK names
new_corps (nc_run refuses otherwise). Times go to D:/rc_scratch/new_corps/render_log.txt.

python nc_finals.py [aurelian|tethys|both] [shots=district,hq,street,kit]
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
NC = os.path.dirname(os.path.dirname(HERE))
SCR = r"D:\rc_scratch\new_corps"
JOBS = {
    "aurelian": dict(folder="roman", scene="roman_scene.py", look="night",
                     samples={"district": 96, "hq": 96, "street": 96, "kit": 64}),
    "tethys": dict(folder="atlantis", scene="tethys_scene.py", look="deep",
                   samples={"district": 64, "hq": 64, "street": 64, "kit": 64}),
}


def run(args, cwd):
    t = time.time()
    r = subprocess.run([sys.executable] + args, cwd=cwd, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    return r.returncode, time.time() - t, out


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    kw = dict(a.split("=", 1) for a in sys.argv[2:] if "=" in a)
    shots = kw.get("shots", "district,hq,street,kit").split(",")
    corps = ["aurelian", "tethys"] if which == "both" else [which]
    log = open(os.path.join(SCR, "render_log.txt"), "a", encoding="utf-8")
    for corp in corps:
        J = JOBS[corp]
        sd = os.path.join(NC, J["folder"], "scripts")
        for shot in shots:
            code, dt, out = run(["nc_run.py", J["scene"], shot, "cycles", "2560x1440", "samples=%d" % J["samples"][shot]], sd)
            line = "%s %s %s exit %d render %.0f s" % (time.strftime("%H:%M"), corp, shot, code, dt)
            print(line, flush=True)
            log.write(line + "\n")
            log.flush()
            if code != 0 or "refused" in out:
                print(out[-2000:])
                return
            base = os.path.join(SCR, J["folder"], "%s_final" % shot).replace("\\", "/")
            if shot == "district":
                exp = "0.6" if J["look"] == "deep" else "1.0"
                c, dt2, o = run(["nc_post.py", base + ".npy", os.path.join(NC, J["folder"], "district.png"), "look=" + J["look"], "exposure=" + exp], sd)
            else:
                c, dt2, o = run(["nc_compose.py", corp, shot, "plate=" + base + ".npy", "json=" + base + ".json", "res=[2560,1440]"], sd)
            line = "   compose %s exit %d %.0f s" % (shot, c, dt2)
            print(line, o.strip().splitlines()[-1:] if o.strip() else "", flush=True)
            log.write(line + "\n")
            if c != 0:
                print(o[-2000:])
    log.close()


if __name__ == "__main__":
    main()
