"""HQ occlusion check (PIPELINE_SPEC 7.1 rules 0-1; Aurelian's occ_check.py, unchanged logic). Pure python, no Blender.

For one frame: every route room (and the vault) inside the frame and facing the camera is a target; a building is an
OCCLUDER of a room when the occlusion rule (downtown.occlusion_state) leaves it above stub height, it stands nearer the
camera than the room, and its projected silhouette overlaps the room's screen box grown by PAD px.

    in_frame_rooms(G, CR, pose, w)        -> ids of the rooms the cone must cover (in frame, facing the camera)
    cone_points(G, ids)                   -> the target volume's points for downtown.occlusion_params
    count(BLD, section, pose, G, ids, w)  -> dict(per_room={id: n}, buildings=n, rooms_hit=n)
"""
import math
import os
import sys

sys.dont_write_bytecode = True
PAD = 12.0
STUB_TOL = 0.5
FRAME = (2560, 1440)


def in_frame_rooms(G, CR, pose, w=2560, mt=None, margin_px=0.0):
    h = w * 9 / 16
    out = []
    for i in G.NODES:
        if i == "start":
            continue
        f = G.room_front(i, mt)
        q = [pose.proj(p, w=w) for p in f]
        if any(v is None for v in q):
            continue
        cx = sum(v[0] for v in q) / 4
        cy = sum(v[1] for v in q) / 4
        if not (-margin_px <= cx <= w + margin_px and -margin_px <= cy <= h + margin_px):
            continue
        if i != "srv" and not CR.visible_room(i, pose, mt):
            continue
        out.append(i)
    return out


def cone_points(G, ids, mt=None):
    return [c for i in ids for c in G.room_front(i, mt)]


def _hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def _clip_area(poly, x0, y0, x1, y1):
    """Area of a convex polygon clipped to the rectangle (Sutherland-Hodgman)."""
    def clip(P, inside, inter):
        out = []
        for k in range(len(P)):
            a, b = P[k], P[(k + 1) % len(P)]
            ia, ib = inside(a), inside(b)
            if ia:
                out.append(a)
            if ia != ib:
                out.append(inter(a, b))
        return out
    P = poly
    for ins, it in (
            (lambda p: p[0] >= x0, lambda a, b: (x0, a[1] + (b[1] - a[1]) * (x0 - a[0]) / (b[0] - a[0]))),
            (lambda p: p[0] <= x1, lambda a, b: (x1, a[1] + (b[1] - a[1]) * (x1 - a[0]) / (b[0] - a[0]))),
            (lambda p: p[1] >= y0, lambda a, b: (a[0] + (b[0] - a[0]) * (y0 - a[1]) / (b[1] - a[1]), y0)),
            (lambda p: p[1] <= y1, lambda a, b: (a[0] + (b[0] - a[0]) * (y1 - a[1]) / (b[1] - a[1]), y1))):
        if not P:
            return 0.0
        P = clip(P, ins, it)
    if len(P) < 3:
        return 0.0
    return abs(sum(P[k][0] * P[(k + 1) % len(P)][1] - P[(k + 1) % len(P)][0] * P[k][1] for k in range(len(P)))) / 2


def count(BLD, section, pose, G, ids, w=2560, mt=None, KDT=None):
    if KDT is None:
        from hq_kit import downtown as KDT  # noqa: N806
    f = pose.dir()
    cam = pose.loc()
    boxes = {}
    for i in ids:
        q = [pose.proj(p, w=w) for p in G.room_front(i, mt)]
        xs, ys = [v[0] for v in q], [v[1] for v in q]
        c = G.room_center(i, mt)
        dep = sum((c[k] - cam[k]) * f[k] for k in range(3))
        boxes[i] = (min(xs) - PAD, min(ys) - PAD, max(xs) + PAD, max(ys) + PAD, dep)
    per = {i: [] for i in ids}
    bset = set()
    for bi, b in enumerate(BLD):
        zc, _a = KDT.occlusion_state(section, b)
        if zc <= section["occ_stub"] + STUB_TOL:
            continue
        x, y, top, hx, hy = b
        zt = min(zc, top)
        dc = (x - cam[0]) * f[0] + (y - cam[1]) * f[1] + (zt * 0.5 - cam[2]) * f[2]
        pts = []
        for sx in (-1, 1):
            for sy in (-1, 1):
                for z in (0.0, zt):
                    q = pose.proj((x + sx * hx, y + sy * hy, z), w=w)
                    if q is None:
                        pts = None
                        break
                    pts.append(q)
                if pts is None:
                    break
            if pts is None:
                break
        if pts is None:
            continue                                 # a corner behind the camera: the camera is inside / past it
        hull = _hull(pts)
        for i, (x0, y0, x1, y1, dep) in boxes.items():
            if dc - math.hypot(hx, hy) > dep:
                continue
            if _clip_area(hull, x0, y0, x1, y1) > 4.0:
                per[i].append(bi)
                bset.add(bi)
    info = {str(bi): [round(v, 1) for v in BLD[bi]] + [round(KDT.occlusion_state(section, BLD[bi])[0], 1)] for bi in sorted(bset)}
    return dict(per_room={i: len(v) for i, v in per.items() if v}, buildings=len(bset), info=info,
                rooms_hit=sum(1 for v in per.values() if v), rooms=len(ids), detail={i: v for i, v in per.items() if v})


def count_band(BLD, section, pose, pts, w=2560, KDT=None):
    """Buildings above stub height in front of and overlapping the face band's screen box (+PAD px)."""
    if KDT is None:
        from hq_kit import downtown as KDT  # noqa: N806
    q = [pose.proj(p, w=w) for p in pts]
    q = [v for v in q if v]
    xs, ys = [v[0] for v in q], [v[1] for v in q]
    box = (min(xs) - PAD, min(ys) - PAD, max(xs) + PAD, max(ys) + PAD)
    f, cam = pose.dir(), pose.loc()
    dep = min(sum((p[k] - cam[k]) * f[k] for k in range(3)) for p in pts)
    n = 0
    for b in BLD:
        zc, _a = KDT.occlusion_state(section, b)
        if zc <= section["occ_stub"] + STUB_TOL:
            continue
        x, y, top, hx, hy = b
        zt = min(zc, top)
        dc = (x - cam[0]) * f[0] + (y - cam[1]) * f[1] + (zt * 0.5 - cam[2]) * f[2]
        if dc - math.hypot(hx, hy) > dep:
            continue
        hp = [pose.proj((x + sx * hx, y + sy * hy, z), w=w) for sx in (-1, 1) for sy in (-1, 1) for z in (0.0, zt)]
        if any(v is None for v in hp):
            continue
        if _clip_area(_hull(hp), *box) > 4.0:
            n += 1
    return n
