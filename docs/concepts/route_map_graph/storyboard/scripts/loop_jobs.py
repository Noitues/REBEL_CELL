"""r3: launch a loop job (headless Blender, log in ../scratch). python loop_jobs.py <preset> [key=value ...]

stages (see loop_r3.py): statics, layers, beams, dyn (statics_vol is superseded by loop_media.py). Every stage writes into ../scratch/loop/.
key=value sets a job key; loop.key=value sets a loop key (e.g. loop.f0=0 loop.f1=8 for a partial frame range)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import jobs_aaa as J  # noqa: E402

PRESETS = {}


def main():
    name = sys.argv[1]
    job, tag = J.make("real", "test")
    job["loop"] = dict(PRESETS.get(name, {"mode": name}))
    job["hiprt"] = False          # plain BVH2: builds in seconds; HIP-RT's ~86 s build only pays off on long passes
    for extra in sys.argv[2:]:
        k, _, v = extra.partition("=")
        try:
            v = json.loads(v)
        except ValueError:
            pass
        if k.startswith("loop."):
            job["loop"][k[5:]] = v
        else:
            job[k] = v
    job["out"] = os.path.join(J.SCR, "loop")
    sys.exit(J.run(job, "loop_" + name))


if __name__ == "__main__":
    main()
