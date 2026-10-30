"""Round 40 COMPAT layout: the round-19 layout API (used by the locked raid-UI scripts, rounds 20-23) backed by the
ONE CITY at real scope (../scratch/layout/layout40.json from build40.py). World units = real BU x K."""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_D = json.load(open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "scratch", "layout", "layout40.json")))
K = _D["K"]
W, H = 1920, 1080
RW, RH = 2880, 1620
CAM = dict(_D["cam"])
CAM["target"] = tuple(CAM["target"])
NODES = {k: (v[0], v[1], v[2], v[3], v[4], tuple(v[5])) for k, v in _D["nodes"].items()}
SITE = {k: v[6] for k, v in _D["nodes"].items()}
LINKS = [tuple(p) for p in _D["links"]]
LINK_PTS = {tuple(k.split("|")): [tuple(q) for q in v] for k, v in _D["link_pts"].items()}
ENTRIES = {k: tuple(v) for k, v in _D["entries"].items()}
ROUTES = {k: [v["keys"][0]] + [tuple(q) for q in v["pts"][1:]] for k, v in _D["routes"].items()}
CORP = "meridian"
NODE_BUILDINGS = {}
LOT = 18.0
LINK_COLOURS = {"lime": (0.83, 1.0, 0.0), "cyan": (0.36, 0.88, 1.0)}
STREETS_X, STREETS_Y = [], []
SW, AW = 9.0, 9.0


def cam_basis():
    yw, pt = math.radians(CAM["yaw"]), math.radians(CAM["pitch"])
    fwd = (math.cos(yw) * math.cos(pt), math.sin(yw) * math.cos(pt), -math.sin(pt))
    right = (math.sin(yw), -math.cos(yw), 0.0)
    up = (right[1] * fwd[2] - right[2] * fwd[1], right[2] * fwd[0] - right[0] * fwd[2], right[0] * fwd[1] - right[1] * fwd[0])
    return right, up, fwd


def cam_location():
    _, _, f = cam_basis()
    t = CAM["target"]
    return (t[0] - f[0] * CAM["dist"], t[1] - f[1] * CAM["dist"], t[2] - f[2] * CAM["dist"])


def project(x, y, z=0.0, w=W, h=H):
    r, u, f = cam_basis()
    t = CAM["target"]
    d = (x - t[0], y - t[1], z - t[2])
    xc = d[0] * r[0] + d[1] * r[1] + d[2] * r[2]
    yc = d[0] * u[0] + d[1] * u[1] + d[2] * u[2]
    zc = d[0] * f[0] + d[1] * f[1] + d[2] * f[2]
    s = CAM["ortho"]
    return ((xc / s + 0.5) * w, (0.5 - yc / (s * h / w)) * h, zc)


def street_w(axis, v):
    return SW


def pt(k):
    if isinstance(k, tuple):
        return k
    if isinstance(k, list):
        return tuple(k)
    if k in NODES:
        return NODES[k][0], NODES[k][1]
    return ENTRIES[k]


def route_points(rid):
    return [pt(k) for k in ROUTES[rid]]


def link_points(a, b):
    if (a, b) in LINK_PTS:
        return LINK_PTS[(a, b)]
    if (b, a) in LINK_PTS:
        return LINK_PTS[(b, a)][::-1]
    return [pt(a), pt(b)]


def is_intersection_reserved(x, y, pad):
    return any(abs(x - n[0]) < pad and abs(y - n[1]) < pad for n in NODES.values())


def node_lot(key):
    x, y = NODES[key][0], NODES[key][1]
    return (x + 5, y + 5, x + 5 + LOT, y + 5 + LOT)


def riser_paths(key):
    return []
