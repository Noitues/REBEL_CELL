"""Parity tuner: coordinate search over CityGradeConfig numbers against the parity score (parity_compare.py), one windowed capture per trial under the GPU lock.
usage: python tune.py <base_tres> <work_dir> <target.png> <plate.png> <rounds> name=factor_step ...   e.g. wet_lamp_gain=0.25 light_gain=0.25
Each trial writes <work_dir>/trial_N.tres (the base with the overrides appended), captures with --grade=, compares, and keeps a change when the score drops.
Written as a file (no python from stdin); kills nothing (run_windowed.py owns its Godot process)."""
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = "D:/rc_art/godot_look_tide"
BASH = "C:/Program Files/Git/bin/bash.exe"


def read_overrides(path):
    vals = {}
    for line in open(path).read().splitlines():
        m = re.match(r"^([a-z_0-9]+) = (-?[0-9.]+)$", line.strip())
        if m:
            vals[m.group(1)] = float(m.group(2))
    return vals


def write_tres(base, overrides, out):
    text = open(base).read().rstrip("\n") + "\n"
    kept = [l for l in text.splitlines() if not (re.match(r"^([a-z_0-9]+) = -?[0-9.]+$", l) and l.split(" = ")[0] in overrides)]
    kept += ["%s = %s" % (k, repr(round(v, 5))) for k, v in sorted(overrides.items())]
    open(out, "w", newline="\n").write("\n".join(kept) + "\n")


def trial(n, base, overrides, work, target, plate):
    tres = os.path.join(work, "trial_%d.tres" % n).replace("\\", "/")
    write_tres(base, overrides, tres)
    cap = subprocess.run([BASH, ROOT + "/tools/look_parity/run_capture.sh", work, "trial_%d" % n, "--grade=" + tres], capture_output=True, text=True)
    cmp = subprocess.run([sys.executable, ROOT + "/tools/look_parity/parity_compare.py", "--godot", work + "/trial_%d.png" % n, "--target", target, "--plate", plate, "--out", work + "/sheets", "--name", "trial_%d" % n], capture_output=True, text=True)
    m = re.search(r"score ([0-9.]+)", cmp.stdout)
    return float(m.group(1)) if m else 9.0


def main():
    base, work, target, plate, rounds = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
    steps = {a.split("=")[0]: float(a.split("=")[1]) for a in sys.argv[6:]}
    os.makedirs(work, exist_ok=True)
    cur = read_overrides(base)
    # defaults of keys not yet in the tres come from the config class (read once from the .gd)
    gd = open(ROOT + "/scripts/city3d/city_grade_config.gd").read()
    for k in steps:
        if k not in cur:
            m = re.search(r"var %s: [A-Za-z0-9]+ = (-?[0-9.]+)" % k, gd)
            cur[k] = float(m.group(1))
    n = 0
    best = trial(n, base, cur, work, target, plate)
    n += 1
    log = open(os.path.join(work, "tune.log"), "w")
    log.write("start %.4f %s\n" % (best, {k: cur[k] for k in steps}))
    log.flush()
    for r in range(rounds):
        for k, st in steps.items():
            for sign in (1.0, -1.0):
                cand = dict(cur)
                cand[k] = cur[k] * (1.0 + sign * st)
                s = trial(n, base, cand, work, target, plate)
                n += 1
                log.write("round %d %s=%.4f score %.4f\n" % (r, k, cand[k], s))
                log.flush()
                if s < best - 1e-4:
                    best = s
                    cur = cand
                    break
        steps = {k: v * 0.6 for k, v in steps.items()}
    log.write("best %.4f %s\n" % (best, {k: round(cur[k], 5) for k in cur}))
    write_tres(base, cur, os.path.join(work, "best.tres"))
    log.close()


if __name__ == "__main__":
    main()
