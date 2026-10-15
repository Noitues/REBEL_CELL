"""Storyboard: build the CITY FILL (cityfill.py rule) into the AAA scene (exec'd by scene_aaa.py after shapes_r2.py when
the job has "fill"). Everything is built inside OwnRng streams, so the shared build stream (4207) and every r3 rule input
(the heightfield covers only the stage) are unchanged.

  ground   wet ground (sem 0.2) round the r3 ground box, roads (darker), lane dashes, kerb lights, static long-exposure
           traffic streaks (red / white, the r2 "no car geometry" rule) on every fill street
  blocks   one building per lot in the AAA kit: block, setback, tower, slab, drum (round_tower); sem 0.6, so the mid-row
           window grid shader lights them; roof trims, rooftop plant, red beacons on the tall ones
Only lots that some storyboard camera can see are built (the aerial frame + the dive path).
"""
import json as _json
import random as _rnd
import sys as _sys

if HERE not in _sys.path:
    _sys.path.insert(0, HERE)
import cityfill as _CF  # noqa: E402
import sb_cams as _SB  # noqa: E402

_FD = _CF.build()
_dive = [_SB.dive_pose(k / 12.0) for k in range(13)] + [_SB.AERIAL]


def _seen(pts, margin=260):
    for p in _dive:
        if _CF._in_frame(p, pts, margin):
            return True
    return False


def trim_runs(x0, y0, x1, y1, z, col, w):
    """A roof trim broken into lit runs (about 45 % of each edge), so from above it reads as neon edges, not a box."""
    for (a, b) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        u = rng.uniform(0.0, 0.3)
        while u < 1.0:
            v = min(1.0, u + rng.uniform(0.12, 0.3))
            if rng.random() < 0.6:
                beam((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, z),
                     (a[0] + (b[0] - a[0]) * v, a[1] + (b[1] - a[1]) * v, z), w, col, acc=NEON)
            u = v + rng.uniform(0.08, 0.25)


_cnt = [0, 0]
with OwnRng(9960):
    set_sem(0.2, 0, 0)
    gc = (0.16, 0.14, 0.2)
    rx0, ry0, rx1, ry1 = _FD["region"]
    # ground round the r3 ground box (x -120..330, y -320..80, top z 0)
    for (a, b, c_, d) in ((rx0, ry0, -120, ry1), (330, ry0, rx1, ry1), (-120, ry0, 330, -320), (-120, 80, 330, ry1)):
        box(a, b, -9, c_, d, -0.02, gc, facet=False)
    xs, ys, sw = _FD["streets"]["xs"], _FD["streets"]["ys"], _FD["streets"]["w"]
    road = (0.12, 0.11, 0.16)
    rr = _rnd.Random(9961)
    # v2: the traffic on the major streets MOVES: four periodic lane patterns (E-W both ways, N-S both ways), one
    # pattern per lane repeated along every street; each lane object slides one period per loop (sb_r set_loop_time)
    LANE_P = 240.0
    _lr = _rnd.Random(9962)
    LANE_PAT, LANE_ACC = {}, {}
    for ax in ("x", "y"):
        for lane in (0, 1):
            pat, c_ = [], _lr.uniform(0, 30)
            while True:
                L_ = _lr.uniform(14, 60)
                if c_ + L_ > LANE_P - 6:
                    break
                pat.append((c_, L_, _lr.uniform(0.6, 1.5)))
                c_ += L_ + _lr.uniform(25, 90)
            LANE_PAT[(ax, lane)] = pat
            LANE_ACC[(ax, lane)] = Acc("filllane_%s%d" % (ax, lane))
    ry_main = sum(_FD["road_y"]) / 2.0
    for y in ys:
        main = abs(y - ry_main) < 1
        segs = [(rx0, -120.0), (330.0, rx1)] if main else [(rx0, rx1)]
        for (a, b) in segs:
            if not main:
                box(a, y - sw / 2, -0.02, b, y + sw / 2, 0.06, road, facet=False)
            ya, yb = (_FD["road_y"] if main else (y - sw / 2, y + sw / 2))
            if main:
                box(a, ya, -0.02, b, yb, 0.08, road, facet=False)
            # lane dashes
            x = a
            while x < b:
                NEON.face([(x, (ya + yb) / 2 - 0.2, 0.1), (x + 3, (ya + yb) / 2 - 0.2, 0.1), (x + 3, (ya + yb) / 2 + 0.2, 0.1),
                           (x, (ya + yb) / 2 + 0.2, 0.1)], (0.5, 0.45, 0.3), (0, 0, 0))
                x += 9.0
            # kerb lights and long-exposure streaks
            x = a + rr.uniform(0, 20)
            while x < b:
                for yk in (ya + 1.0, yb - 1.0):
                    if _seen([(x, yk, 0)], 60):
                        c = rr.choice([(1.0, 0.7, 0.35), (1.0, 0.7, 0.35), (0.5, 0.85, 1.0)])
                        box(x - 0.5, yk - 0.5, 5.6, x + 0.5, yk + 0.5, 6.4, tuple(v * 1.2 for v in c), facet=False, acc=NEON)
                x += 26.0
            for lane, (yl, col) in enumerate((((ya + yb) / 2 - (yb - ya) * 0.22, (0.85, 0.08, 0.05)),
                                              ((ya + yb) / 2 + (yb - ya) * 0.22, (1.0, 0.85, 0.6)))):
                if main:
                    break       # the netrun street carries the r3 loop lanes
                acc = LANE_ACC[("x", lane)]
                for (cx, L, k) in LANE_PAT[("x", lane)]:
                    for rep in range(int((b - a) / LANE_P) + 3):
                        x = a - LANE_P + rep * LANE_P + cx
                        if x + L < a - LANE_P or x > b:
                            continue
                        if _seen([(x, yl, 0), (x + L, yl, 0), (x + LANE_P, yl, 0)], 60):
                            acc.face([(x, yl - 0.3, 0.35), (x + L, yl - 0.3, 0.35), (x + L, yl + 0.3, 0.35), (x, yl + 0.3, 0.35)],
                                     tuple(v * k for v in col), (0, 0, 0))
    for x in xs:
        box(x - sw / 2, ry0, -0.02, x + sw / 2, ry1, 0.06, road, facet=False)
        for side, col in ((-0.22, (0.85, 0.08, 0.05)), (0.22, (1.0, 0.85, 0.6))):
            xl = x + sw * side
            lane = 0 if side < 0 else 1
            acc = LANE_ACC[("y", lane)]
            for (cy, L, k) in LANE_PAT[("y", lane)]:
                for rep in range(int((ry1 - ry0) / LANE_P) + 3):
                    y = ry0 - LANE_P + rep * LANE_P + cy
                    if _seen([(xl, y, 0), (xl, y + L, 0), (xl, y + LANE_P, 0)], 60):
                        acc.face([(xl - 0.3, y, 0.35), (xl + 0.3, y, 0.35), (xl + 0.3, y + L, 0.35), (xl - 0.3, y + L, 0.35)],
                                 tuple(v * k for v in col), (0, 0, 0))
        y = ry0 + rr.uniform(0, 20)
        while y < ry1:
            for xk in (x - sw / 2 + 1, x + sw / 2 - 1):
                if _seen([(xk, y, 0)], 60):
                    c = rr.choice([(1.0, 0.7, 0.35), (1.0, 0.7, 0.35), (0.5, 0.85, 1.0)])
                    box(xk - 0.5, y - 0.5, 5.6, xk + 0.5, y + 0.5, 6.4, tuple(v * 1.2 for v in c), facet=False, acc=NEON)
            y += 26.0

def _lane_mat():
    m = bpy.data.materials.new("fill_lane")
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(attr(nt, "col").outputs["Color"], em.inputs["Color"])
    em.inputs["Strength"].default_value = float(LK["neon"]) * 0.35     # the street-paint class level (CLASS_EMIT 0.2)
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


_LM = _lane_mat()
FILL_LANES = []      # (object, axis, direction)
for (ax, lane), acc in sorted(LANE_ACC.items()):
    ob = acc.obj(_LM, "filllane_%s%d" % (ax, lane))
    FILL_LANES.append((ob, ax, 1 if lane == 1 else -1))

FILL_BOXES = []
for _b in _FD["buildings"]:
    x0, y0, x1, y1 = _b["rect"]
    h = _b["h"]
    if not _seen([(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (0.0, h)]):
        continue
    _cnt[0] += 1
    FILL_BOXES.append((x0, y0, x1, y1, h))
    with OwnRng(_b["seed"]):
        set_sem(0.6, 0, 0)
        c = tuple(v * 0.78 for v in rng.choice(FAMS))
        st = _b["style"]
        trim = tuple(v * 0.22 for v in rng.choice(TRIMS))
        w, d = x1 - x0, y1 - y0
        if st == "drum" and min(w, d) > 14:
            round_tower((x0 + x1) / 2, (y0 + y1) / 2, min(w, d) / 2 - 0.5, h, c, crown=trim if rng.random() < 0.07 else None, spire_h=6.0 + rng.random() * 8)
        elif st == "tower" and min(w, d) > 12 and h > 70:
            box(x0, y0, 0, x1, y1, h, c, facet=False)
            box(x0 + 1.2, y0 + 1.2, h, x1 - 1.2, y1 - 1.2, h + 4, tuple(v * 0.85 for v in c), facet=False)
            if rng.random() < 0.17:
                trim_runs(x0 + 1.3, y0 + 1.3, x1 - 1.3, y1 - 1.3, h + 4.05, trim, 0.3)
            beam(((x0 + x1) / 2, (y0 + y1) / 2, h + 4), ((x0 + x1) / 2, (y0 + y1) / 2, h + 14), 0.4, (0.25, 0.25, 0.3))
            box((x0 + x1) / 2 - 0.6, (y0 + y1) / 2 - 0.6, h + 14, (x0 + x1) / 2 + 0.6, (y0 + y1) / 2 + 0.6, h + 15.2, RED,
                facet=False, acc=NEON)
        elif st == "setback" and min(w, d) > 14 and h > 30:
            hb = h * 0.62
            box(x0, y0, 0, x1, y1, hb, c, facet=False)
            z = hb
            for t in range(3):
                ins = 2.0 * (t + 1)
                if (x1 - x0) - 2 * ins < 4 or (y1 - y0) - 2 * ins < 4 or z >= h:
                    break
                zt = min(h, z + (h - hb) / 2 + 2)
                box(x0 + ins, y0 + ins, z, x1 - ins, y1 - ins, zt, tuple(v * (0.95 - 0.04 * t) for v in c), facet=False)
                if (t == 2 or zt >= h) and rng.random() < 0.05:
                    trim_runs(x0 + ins + 0.1, y0 + ins + 0.1, x1 - ins - 0.1, y1 - ins - 0.1, zt + 0.05, trim, 0.25)
                z = zt
        else:
            box(x0, y0, 0, x1, y1, h, c, facet=False)
            if rng.random() < 0.025:
                trim_runs(x0 + 0.2, y0 + 0.2, x1 - 0.2, y1 - 0.2, h + 0.05, trim, 0.3)
            for k in range(rng.randint(0, 3)):
                ax, ay = rng.uniform(x0 + 2, max(x0 + 2.1, x1 - 6)), rng.uniform(y0 + 2, max(y0 + 2.1, y1 - 6))
                box(ax, ay, h, ax + rng.uniform(2, 4), ay + rng.uniform(2, 4), h + rng.uniform(1.0, 2.6), (0.3, 0.3, 0.34),
                    facet=False)
            if st == "slab" and rng.random() < 0.6:
                # a lit sign band round the crown
                box(x0 - 0.1, y0 - 0.1, h - 3.0, x1 + 0.1, y0 + 0.05, h - 2.2, tuple(v * 0.8 for v in trim), facet=False,
                    acc=NEON)
        if h > 60 and rng.random() < 0.6:
            box((x0 + x1) / 2 - 0.5, (y0 + y1) / 2 - 0.5, h + 0.2, (x0 + x1) / 2 + 0.5, (y0 + y1) / 2 + 0.5, h + 1.2, RED,
                facet=False, acc=NEON)
print("fill: %d buildings built (of %d), network %d nodes" % (_cnt[0], len(_FD["buildings"]), len(_FD["network"]["nodes"])),
      flush=True)
