"""Aurelian HQ: the occlusion check measured on the render's object-index pass (DESIGN.md 14.1).

python occ_index.py <dir holding <name>_index.npy> <frame names,..> [res_w]

For every route room in frame (facing the camera) the room's front quad bounding box, and the same box grown by 12 px: the
number of city pixels (index 2) in it. A city pixel inside a room's own front box is a building standing in front of it.
The raw Cycles index pass is speckled (about 22-25 % of the landmark's own pixels carry the city index: transparent
city faces, see golden_plates/INDEX.md note 1), so the test is the DENSITY of city pixels in the box: a building in front
fills the box (above 50 %), the speckle stays under 35 %. Pixels in the 12 px margin are advisory: at the landmark's
silhouette they can be the city BEHIND it (the index pass has no depth).
"""
import json
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aur_env  # noqa: E402

aur_env.setup()
import hq_cam as CR  # noqa: E402
import hq_graph as G  # noqa: E402
import occ_check as OC  # noqa: E402

CITY = 2
OCCLUDED = 0.5


def measure(src, name, w):
    idx = np.round(np.load(os.path.join(src, name + "_index.npy"))[..., 0]).astype(np.int32)
    ov = json.load(open(os.path.join(aur_env.SCR, "ov_stills.json")))[name]
    pose = CR.pose_of(ov["pose"])
    zoom = ov["zoom"]
    mt = int(ov["mt"])
    if zoom < 0.5:
        ids = [i for i in G.NODES if i != "start"]
    else:
        ids = OC.in_frame_rooms(G, CR, pose, w=w, mt=mt)
    s = idx.shape[1] / float(w)
    H, W = idx.shape
    out = {}
    for i in ids:
        q = [pose.proj(p, w=w) for p in G.room_front(i, mt)]
        if any(v is None for v in q):
            continue
        xs, ys = [v[0] * s for v in q], [v[1] * s for v in q]
        x0, x1, y0, y1 = int(max(0, min(xs))), int(min(W, max(xs) + 1)), int(max(0, min(ys))), int(min(H, max(ys) + 1))
        if x1 <= x0 or y1 <= y0:
            continue
        box = idx[y0:y1, x0:x1]
        pad = int(round(OC.PAD * s))
        bx0, bx1, by0, by1 = max(0, x0 - pad), min(W, x1 + pad), max(0, y0 - pad), min(H, y1 + pad)
        big = idx[by0:by1, bx0:bx1]
        out[i] = dict(front_city_px=int((box == CITY).sum()), front_px=int(box.size), pad_city_px=int((big == CITY).sum()),
                      front_frac=float((box == CITY).mean()), pad_frac=float((big == CITY).mean()))
    return out


if __name__ == "__main__":
    src = sys.argv[1]
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 2560
    for n in sys.argv[2].split(","):
        m = measure(src, n, w)
        hit = {i: v for i, v in m.items() if v["front_frac"] > OCCLUDED}
        print(n, "rooms", len(m), "occluded (city > %.0f %% of the front box): %d" % (100 * OCCLUDED, len(hit)),
              "max city share %.2f" % max(v["front_frac"] for v in m.values()), {i: round(v["front_frac"], 2) for i, v in hit.items()})
