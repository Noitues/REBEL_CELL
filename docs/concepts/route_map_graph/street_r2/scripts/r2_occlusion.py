"""Street round 2: the "route never occluded" check (PIPELINE_SPEC 7.1 rule 0, 12.6), measured from the index pass.

python r2_occlusion.py <index.npy> <z.npy> <anchors.json> [plan.json] [--stub 3.8] [--pad 12] [--min-px 150]

For every route room in frame, the screen box of its front opening is grown by `pad` px. A pixel is an occluder when:
  - the index pass says class 2 (the city: a non-route, non-landmark object);
  - it lies inside a grown room box;
  - it is nearer to the camera than the room's front plane by more than `near` BU (so a board on the same facade, or a
    neighbour beside the room, is not an occluder);
  - its world height (from the Z pass and the camera) is above `stub` (3.8 BU = 2 floors, spec 7.2): a lit stub in front
    of a room is the rule's allowed result.
The mask is eroded by `erode_r` px first (anything thinner than 2r+1 px, lamp posts and cables, is not a building), then
blobs under `min_px` are dropped.
Prints the number of occluder blobs and pixels per room. Pure CPU. The scene's cut (section) removes the near row; this
check proves it from the image, in OVERVIEW, DECISION and HOVER.
"""
import json
import sys

import numpy as np


def load_pass(path):
    a = np.load(path)
    return a[..., 0] if a.ndim == 3 else a


def unproject(anch, z, W=1920, H=1080):
    """World position of every pixel from the Z pass (Blender z-depth) and the camera of the anchors."""
    M = np.array(anch["cam_world"])
    lens, sensor = anch["lens"], anch["sensor"]
    sx, sy = anch["shift"]
    fx = lens / sensor * W
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    xc = (xs + 0.5 - W / 2 + sx * W) / fx
    yc = -(ys + 0.5 - H / 2 - sy * W) / fx
    P = np.stack([xc * z, yc * z, -z, np.ones_like(z)], -1)
    return P @ M.T


def erode(m, r):
    """Binary erosion by a (2r+1) square: wipes out anything thinner than 2r+1 px (lamp posts, cables, antialiased edges)."""
    out = m.copy()
    for k in range(1, r + 1):
        out[:, k:] &= m[:, :-k]
        out[:, :-k] &= m[:, k:]
    o2 = out.copy()
    for k in range(1, r + 1):
        o2[k:, :] &= out[:-k, :]
        o2[:-k, :] &= out[k:, :]
    return o2


def blobs(mask, min_px):
    """4-connected components of a boolean mask (iterative flood, small masks only)."""
    from collections import deque
    H, W = mask.shape
    seen = np.zeros_like(mask)
    out = []
    ys, xs = np.nonzero(mask)
    for y0, x0 in zip(ys, xs):
        if seen[y0, x0]:
            continue
        q = deque([(y0, x0)])
        seen[y0, x0] = True
        pts = []
        while q:
            y, x = q.popleft()
            pts.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and mask[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    q.append((yy, xx))
        if len(pts) >= min_px:
            out.append(pts)
    return out


def measure(index_path, z_path, anchors, stub=3.8, pad=12, min_px=40, near=1.0, only=None, plan=None, erode_r=4):
    idx = load_pass(index_path)
    z = load_pass(z_path)
    H, W = idx.shape
    anch = json.load(open(anchors)) if isinstance(anchors, str) else anchors
    world = unproject(anch, z, W, H)
    lamps = []
    if plan:
        pl = json.load(open(plan)) if isinstance(plan, str) else plan
        lamps = [l["pos"][:2] for l in pl.get("lamps", [])]
    res = dict(rooms=0, occluder_blobs=0, occluder_px=0, per_room={})
    for rid, r in sorted(anch["rooms"].items()):
        if only and rid not in only:
            continue
        q = np.array(r["front"])
        x0, y0, x1, y1 = q[:, 0].min(), q[:, 1].min(), q[:, 0].max(), q[:, 1].max()
        vis = (min(x1, W) - max(x0, 0)) * (min(y1, H) - max(y0, 0)) / max(1.0, (x1 - x0) * (y1 - y0))
        if vis < 0.5:
            continue
        res["rooms"] += 1
        bx0, by0 = int(max(0, x0 - pad)), int(max(0, y0 - pad))
        bx1, by1 = int(min(W, x1 + pad)) + 1, int(min(H, y1 + pad)) + 1
        zr = float(np.median(z[int(max(0, (y0 + y1) / 2 - 3)):int((y0 + y1) / 2 + 4), int(max(0, (x0 + x1) / 2 - 3)):int((x0 + x1) / 2 + 4)]))
        zroom = float(np.mean(r.get("depth_front", [zr])))
        m = np.zeros((H, W), bool)
        sub = (idx[by0:by1, bx0:bx1] == 2) & (z[by0:by1, bx0:bx1] < zr - near) & (world[by0:by1, bx0:bx1, 2] > stub)
        for lx, ly in lamps:                                  # kerb lamp posts are street furniture (12.4 item 5), not buildings
            sub &= ~((world[by0:by1, bx0:bx1, 0] - lx) ** 2 + (world[by0:by1, bx0:bx1, 1] - ly) ** 2 < 1.6 ** 2)
        m[by0:by1, bx0:bx1] = erode(sub, erode_r) if False else sub
        m = erode(m, erode_r)
        bl = blobs(m, min_px)
        npx = sum(len(b) for b in bl)
        res["per_room"][rid] = dict(blobs=len(bl), px=npx, box=[bx0, by0, bx1, by1])
        res["occluder_blobs"] += len(bl)
        res["occluder_px"] += npx
    return res


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    kw = {}
    for x in sys.argv[1:]:
        if x.startswith("--"):
            k, v = x[2:].split("=") if "=" in x else (x[2:], None)
            kw[k.replace("-", "_")] = float(v) if v else True
    r = measure(a[0], a[1], a[2], plan=a[3] if len(a) > 3 else None, **{k: v for k, v in kw.items() if k in ("stub", "pad", "min_px", "near")})
    bad = {k: v for k, v in r["per_room"].items() if v["blobs"]}
    print("rooms in frame %d, occluder blobs %d, px %d" % (r["rooms"], r["occluder_blobs"], r["occluder_px"]))
    for k, v in bad.items():
        print("  ", k, v)
    sys.exit(1 if r["occluder_blobs"] else 0)
