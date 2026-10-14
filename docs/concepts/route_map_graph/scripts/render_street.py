"""Family S (street level): render perspective shots of the same city (street39.py, one Blender child).
python render_street.py <set>   sets: test | key | walk
  key  -> s_key   1920x1080, the fork at intersection (26, 15) seen from behind, 20 deg down
  walk -> s_walk00..NN  960x540, a step forward down the right-hand street (option 2), 1.5 s at 12 fps
"""
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
os.environ.setdefault("NET36", "net_scope.json")
import layout36 as L  # noqa: E402

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
OUT = os.path.join(ROOT, "scratch", "bl")
FORK = (26.5, 15.5)                 # the intersection (lots) the operative stands at: streets i=26 and j=15
DIRV = (-math.sqrt(0.5), math.sqrt(0.5))   # world view direction (the city kit's window side faces the camera)
KEY = (16.0, 24.0, 52.0, 0.0, 16.0, 8.0)   # back, eye height, look distance, look z, lens, yaw: ~25 deg down


def view_dir(yaw):
    ang = math.radians(135.0 - yaw)            # yaw > 0 turns toward world +y (down the right-hand street)
    return math.cos(ang), math.sin(ang)


def cam_at(back, height, ahead, lift_look=0.0, lens=17.0, yaw=0.0):
    cx, cy = L.W(FORK)
    dx, dy = view_dir(yaw)
    lx, ly = cx - DIRV[0] * back, cy - DIRV[1] * back
    return dict(loc=[lx, ly, height], look=[lx + dx * ahead, ly + dy * ahead, lift_look], lens=lens)


def walk_cam(u):
    """A step forward: from the key camera onto the right-hand street (i=26, world +y), turning to face down it."""
    e = u * u * (3 - 2 * u)
    k = cam_at(*KEY)
    cx, cy = L.W(FORK)
    end = (cx + 3.0, cy + 20.0, 16.0)
    x = k["loc"][0] + (end[0] - k["loc"][0]) * e
    y = k["loc"][1] + (end[1] - k["loc"][1]) * e
    z = k["loc"][2] + (end[2] - k["loc"][2]) * e
    dx, dy = view_dir(KEY[5] + (45.0 - 10.0 - KEY[5]) * e)
    return dict(loc=[x, y, z], look=[x + dx * KEY[2], y + dy * KEY[2], 0.0], lens=KEY[4] + 2.0 * e)


def x3_cam(loc_lot, z, look_lot, lens=20.0, side=0.0):
    """X3: a high 3/4 camera straight down street i=26 (toward lot -y = world +y)."""
    lx, ly = L.W(loc_lot)
    tx, ty = L.W(look_lot)
    return dict(loc=[lx + side, ly, z], look=[tx + side, ty, 0.0], lens=lens)


X3_KEY = ((26.5, 23.5), 80.0, (26.5, 9.5), 24.0)     # ~48 deg down, straight down street i=26
X3_TEST = [((27.0, 24.0), 60.0, (27.0, 6.0), 20.0), ((27.0, 25.0), 78.0, (27.0, 6.0), 20.0),
           ((27.0, 27.0), 95.0, (27.0, 5.0), 22.0)]


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "key"
    os.makedirs(OUT, exist_ok=True)
    if which == "test":
        cams = [dict(tag="s_test%d" % k, persp=cam_at(*a), res=[1280, 720], samples=8, passes="lite")
                for k, a in enumerate([(4.0, 12.0, 40.0), (8.0, 18.0, 45.0), (2.0, 8.0, 35.0, 0.0, 15.0)])]
    elif which == "key":
        cams = [dict(tag="s_key", persp=cam_at(*KEY), res=[1920, 1080], samples=16, passes="lite")]
    elif which == "x3test":
        cams = [dict(tag="x3_test%d" % k, persp=x3_cam(*a), res=[1280, 720], samples=4, passes="lite")
                for k, a in enumerate(X3_TEST)]
    elif which == "x3":
        cams = [dict(tag="x3_key", persp=x3_cam(*X3_KEY), res=[1920, 1080], samples=8, passes="lite")]
    else:
        n = 18
        cams = [dict(tag="s_walk%02d" % k, persp=walk_cam(k / (n - 1)), res=[960, 540], samples=8, passes="lite")
                for k in range(n)]
    cf = os.path.join(ROOT, "scratch", "cams_street_%s.json" % which)
    json.dump(cams, open(cf, "w"), indent=1)
    log = os.path.join(ROOT, "scratch", "street_%s.log" % which)
    with open(log, "w") as f:
        subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "street39.py"), "--", "meridian_hq", OUT, cf],
                       stdout=f, stderr=subprocess.STDOUT)
    print("ok" if "DONE" in open(log).read() else "FAILED, see " + log)
