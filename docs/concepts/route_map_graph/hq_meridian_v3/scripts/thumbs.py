"""Meridian v3: three massing thumbnails (Workbench, fast) from the HQ overview angle (high 3/4 from the SSW).

blender -b --factory-startup --python thumbs.py -- <out_dir> [A,B,C]
Units: HQ kit BU (1 storey = 8 BU). North = +y. The lot is |x|, |y| <= 120; the dense city starts at the lot edge.
Common to all three: the high-speed freight line along the NORTH edge (y 100-114, continuing E-W through the city),
truck gates on the W, S, E sides, container curtain walls. What differs is the crane = the castle.
  A  GATEHOUSE GANTRY   a goliath gantry whose two legs are crenellated towers riding runways on the E / W curtain
                        walls; the span is a battlemented bridge; the trolley is the keep (the server); it rolls N-S
                        from the south truck lane to over the train
  B  SLEWING DONJON     a round crenellated donjon in the bailey whose roof slews a long jib + a castellated
                        counterweight; reach = a circle over walls, trucks and train
  C  QUAYSIDE KEEP      a ship-to-shore crane straddling the rail as the castle's gatehouse: crenellated portal legs,
                        the machinery house as the keep, the boom lowered south over the bailey
Seed 5401 (city), 5402 (stacks).
"""
import math
import os
import random
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
WHICH = (argv[1] if len(argv) > 1 else "A,B,C").split(",")
os.makedirs(OUT, exist_ok=True)

COL = {
    "city": (0.16, 0.17, 0.20), "city_hi": (0.22, 0.23, 0.27), "street": (0.06, 0.06, 0.07),
    "ground": (0.10, 0.10, 0.11), "lot": (0.18, 0.17, 0.16),
    "wall": (0.42, 0.20, 0.10), "wall2": (0.20, 0.26, 0.32), "wall3": (0.48, 0.36, 0.14),
    "tower": (0.30, 0.22, 0.18), "crane": (1.0, 0.50, 0.08), "keep": (0.95, 0.80, 0.55),
    "server": (1.0, 0.15, 0.10), "rail": (0.35, 0.35, 0.38), "train": (0.88, 0.92, 0.96),
    "truck": (1.0, 0.85, 0.10), "cont": (0.15, 0.42, 0.55), "stack1": (0.50, 0.18, 0.10), "stack2": (0.16, 0.30, 0.38),
    "stack3": (0.55, 0.45, 0.20), "gate": (0.85, 0.85, 0.80),
}


class Acc:
    def __init__(self):
        self.v, self.f = [], []

    def box(self, x0, y0, z0, x1, y1, z1):
        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))
        b = len(self.v)
        self.v += [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1),
                   (x0, y1, z1)]
        self.f += [(b, b + 3, b + 2, b + 1), (b + 4, b + 5, b + 6, b + 7), (b, b + 1, b + 5, b + 4),
                   (b + 1, b + 2, b + 6, b + 5), (b + 2, b + 3, b + 7, b + 6), (b + 3, b, b + 4, b + 7)]

    def cyl(self, cx, cy, r, z0, z1, n=24):
        b = len(self.v)
        for z in (z0, z1):
            for k in range(n):
                a = 2 * math.pi * k / n
                self.v.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
        for k in range(n):
            j = (k + 1) % n
            self.f.append((b + k, b + j, b + n + j, b + n + k))
        self.f.append(tuple(b + n + k for k in range(n)))
        self.f.append(tuple(b + k for k in reversed(range(n))))

    def beam(self, p, q, w, h):
        """A box beam from p to q (w wide, h tall), axis-aligned in plan or sloped in z along x or y."""
        dx, dy, dz = q[0] - p[0], q[1] - p[1], q[2] - p[2]
        L = math.hypot(dx, dy)
        if L < 1e-6:
            self.box(p[0] - w / 2, p[1] - w / 2, min(p[2], q[2]), p[0] + w / 2, p[1] + w / 2, max(p[2], q[2]))
            return
        ux, uy = dx / L, dy / L
        sx, sy = -uy * w / 2, ux * w / 2
        b = len(self.v)
        for (x, y, z) in (p, q):
            pass
        pts = []
        for zz in (0.0, h):
            pts += [(p[0] + sx, p[1] + sy, p[2] + zz), (q[0] + sx, q[1] + sy, q[2] + zz), (q[0] - sx, q[1] - sy, q[2] + zz),
                    (p[0] - sx, p[1] - sy, p[2] + zz)]
        self.v += pts
        self.f += [(b, b + 3, b + 2, b + 1), (b + 4, b + 5, b + 6, b + 7), (b, b + 1, b + 5, b + 4),
                   (b + 1, b + 2, b + 6, b + 5), (b + 2, b + 3, b + 7, b + 6), (b + 3, b, b + 4, b + 7)]


def fresh():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return {k: Acc() for k in COL}


def flush(A):
    sc = bpy.context.scene
    for k, a in A.items():
        if not a.f:
            continue
        me = bpy.data.meshes.new(k)
        me.from_pydata(a.v, [], a.f)
        ob = bpy.data.objects.new(k, me)
        ob.color = COL[k] + (1.0,)
        sc.collection.objects.link(ob)


def merlons(acc, x0, y0, x1, y1, z, step=6.0, h=4.0, t=3.0):
    """Crenellations along the rectangle's perimeter (a ring of teeth t thick)."""
    for (ax, ay, bx, by) in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
        L = math.hypot(bx - ax, by - ay)
        n = max(1, int(L / step))
        for k in range(n):
            if k % 2:
                continue
            f0, f1 = k / n, (k + 1) / n
            px0, py0 = ax + (bx - ax) * f0, ay + (by - ay) * f0
            px1, py1 = ax + (bx - ax) * f1, ay + (by - ay) * f1
            if ay == by:
                acc.box(px0, py0 - (t if ay > y0 else 0), z, px1, py0 + (0 if ay > y0 else t), z + h)
            else:
                acc.box(px0 - (t if ax > x0 else 0), py0, z, px0 + (0 if ax > x0 else t), py1, z + h)


def merlon_ring(acc, cx, cy, r, z, n=12, h=4.0, t=3.0):
    for k in range(0, n, 2):
        a0 = 2 * math.pi * k / n
        a1 = 2 * math.pi * (k + 0.7) / n
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        acc.beam((x0, y0, z), (x1, y1, z), t, h)


def tower(A, cx, cy, hx, hy, h, key="tower"):
    A[key].box(cx - hx, cy - hy, 0, cx + hx, cy + hy, h)
    merlons(A[key], cx - hx, cy - hy, cx + hx, cy + hy, h, step=5.0)


def truck(A, x, y, ax):
    """A tractor + chassis + container, nose toward ax ('+x', '-x', '+y', '-y')."""
    L, W = 22.0, 5.0
    if ax in ("+x", "-x"):
        s = 1 if ax == "+x" else -1
        A["cont"].box(x - s * L / 2, y - W / 2, 1.6, x + s * 3.0, y + W / 2, 7.4)
        A["truck"].box(x + s * 3.5, y - W / 2, 0.6, x + s * L / 2, y + W / 2, 7.0)
    else:
        s = 1 if ax == "+y" else -1
        A["cont"].box(x - W / 2, y - s * L / 2, 1.6, x + W / 2, y + s * 3.0, 7.4)
        A["truck"].box(x - W / 2, y + s * 3.5, 0.6, x + W / 2, y + s * L / 2, 7.0)


def common(A, gate_sides=("W", "S", "E"), runway=False, rail_tower_arch=True):
    """City, lot, rail line + train, curtain walls (container courses), corner towers, gatehouses, trucks, yard stacks."""
    r = random.Random(5401)
    A["ground"].box(-1400, -1400, -0.5, 1400, 1400, -0.05)
    A["lot"].box(-120, -120, -0.05, 120, 120, 0.0)
    # the city: blocks of 30 BU (streets 8) right up to the lot; a rail corridor along y 92..122 (low sheds)
    spans = [(128 + 30 * k, 150 + 30 * k) for k in range(30)]
    spans += [(-b, -a) for (a, b) in spans]
    spans += [(-120 + 30 * k, -98 + 30 * k) for k in range(8)]
    spans.sort()
    for (xa, xb) in spans:
        for (ya, yb) in spans:
            cx, cy = (xa + xb) / 2, (ya + yb) / 2
            if abs(cx) < 124 and abs(cy) < 124:
                continue
            d = max(abs(cx), abs(cy))
            if d > 1000:
                continue
            h = r.uniform(16, 44) if d < 260 else r.uniform(30, 100)
            if r.random() < 0.06:
                h *= 1.8
            if 88 < cy < 126:
                h = min(h, 8.0)                       # the rail corridor: low sheds
                if 94 < cy < 118:
                    continue
            # the occlusion rule (section.py, simplified for massing): buildings in the camera's sight cone in front
            # of the lot are section-cut to a 1-2 storey stub
            ux_, uy_ = math.sin(math.radians(22.0)), math.cos(math.radians(22.0))
            al = cx * ux_ + cy * uy_
            la = cx * uy_ - cy * ux_
            if -420 < al < -100 and abs(la) < 150 + (-al - 100) * 0.35:
                h = min(h, 5.0)
            A["city_hi" if r.random() < 0.3 else "city"].box(xa, ya, 0, xb, yb, h)
    # the high-speed line: two tracks along the north edge (y 100, 112), through the city both ways
    for yy in (100.0, 112.0):
        A["rail"].box(-1400, yy - 3.2, 0.0, 1400, yy + 3.2, 1.0)
    # the train: a long sleek freight set on the inner track, nose pointing east, cars with containers
    x = -230.0
    A["train"].box(x, 96.5, 1.0, x + 30, 103.5, 8.5)
    x += 31
    for k in range(9):
        A["train"].box(x, 96.8, 1.0, x + 26, 103.2, 3.4)
        if k % 3 != 1:
            A[("stack1", "stack2", "stack3", "cont")[k % 4]].box(x + 1, 97.0, 3.4, x + 25, 103.0, 9.6)
        x += 27
    A["train"].box(x, 96.5, 1.0, x + 30, 103.5, 8.5)
    # curtain walls of containers: E / W full height x 106..120, S y -120..-106; the N side is the rail
    WT = 36.0

    def wall_run(x0, y0, x1, y1, gaps=()):
        horiz = abs(x1 - x0) > abs(y1 - y0)
        a, b = (x0, x1) if horiz else (y0, y1)
        k = 0
        for c in range(4):
            u = a
            while u < b - 0.5:
                v = min(u + 14.0, b)
                if not any(g0 < (u + v) / 2 < g1 for (g0, g1) in gaps) or c == 3 and False:
                    key = ("wall", "wall2", "wall3", "wall")[(k + c) % 4]
                    if not any(g0 < (u + v) / 2 < g1 for (g0, g1) in gaps):
                        if horiz:
                            A[key].box(u + 0.2, y0, c * 9, v - 0.2, y1, c * 9 + 8.6)
                        else:
                            A[key].box(x0, u + 0.2, c * 9, x1, v - 0.2, c * 9 + 8.6)
                k += 1
                u = v
        # merlons: half containers on the outer edge
        if horiz:
            merlons(A["wall"], x0, y0, x1, y1, WT, step=7.0, h=4.6, t=4.0)
        else:
            merlons(A["wall"], x0, y0, x1, y1, WT, step=7.0, h=4.6, t=4.0)
    gw = 9.0
    wall_run(-120, -120, -106, 92, gaps=((-30 - gw, -30 + gw),) if "W" in gate_sides else ())
    wall_run(106, -120, 120, 92, gaps=((-30 - gw, -30 + gw),) if "E" in gate_sides else ())
    wall_run(-106, -120, 106, -106, gaps=((-gw, gw),) if "S" in gate_sides else ())
    if runway:
        for sx in (-1, 1):
            A["rail"].box(sx * 113 - 4, -120, WT, sx * 113 + 4, 120, WT + 1.2)
    # corner towers: S pair plain; N pair straddle the rail with an arch (the rail gates)
    for sx in (-1, 1):
        tower(A, sx * 113, -113, 14, 14, 56)
        if rail_tower_arch:
            cx, cy = sx * 113, 106
            A["tower"].box(cx - 14, cy - 18, 18, cx + 14, cy + 18, 56)
            A["tower"].box(cx - 14, cy - 18, 0, cx + 14, cy - 12, 18)
            A["tower"].box(cx - 14, cy + 12, 0, cx + 14, cy + 18, 18)
            merlons(A["tower"], cx - 14, cy - 18, cx + 14, cy + 18, 56, step=5.0)
            A["gate"].box(cx - 14.5, cy - 12, 17, cx + 14.5, cy + 12, 18)
    # gatehouses: twin towers flanking the gate on W, S, E
    for side in gate_sides:
        if side == "S":
            for s in (-1, 1):
                tower(A, s * (gw + 7), -113, 7, 12, 52)
            A["tower"].box(-gw, -122, 16, gw, -104, 52)
            A["gate"].box(-gw, -122.5, 15, gw, -104, 16.5)
            for k in range(3):
                truck(A, -60 + k * 16, -138, "+y") if False else None
            truck(A, 0, -142, "+y")
            truck(A, 14, -150, "+y")
        else:
            sx = -1 if side == "W" else 1
            for s in (-1, 1):
                tower(A, sx * 113, -30 + s * (gw + 7), 12, 7, 52)
            A["tower"].box(sx * 122, -30 - gw, 16, sx * 104, -30 + gw, 52)
            A["gate"].box(sx * 122.5, -30 - gw, 15, sx * 104, -30 + gw, 16.5)
            truck(A, sx * 142, -30, "-x" if sx > 0 else "+x")
    # the truck lanes inside: S lane y -100, W / E lanes x +-96
    for k, xx in enumerate((-80, -56, -32, 32, 56, 80)):
        truck(A, xx, -97, "+x" if k % 2 else "-x")
    for sx in (-1, 1):
        for yy in (-80, 10, 34, 58):
            truck(A, sx * 96, yy, "+y")
    # yard stacks (the bailey): rows of containers 1-4 high
    rs = random.Random(5402)
    for gx in range(-4, 4):
        for gy in range(-3, 3):
            x0 = -80 + (gx + 4) * 20 + 2
            y0 = -82 + (gy + 3) * 26 + 2
            if abs(x0 + 7 + 6) < 38 and abs(y0 + 9 + 6) < 38 and "_clear_centre" in A:
                continue
            nh = rs.randint(1, 4)
            for k in range(nh):
                A[("stack1", "stack2", "stack3")[rs.randrange(3)]].box(x0, y0, k * 7.0, x0 + 14, y0 + 18, k * 7.0 + 6.6)


def concept_A(A):
    common(A, runway=True)
    gy = -22.0                                 # the gantry's travel position (overview: south of mid-yard)
    WT = 37.2
    for sx in (-1, 1):
        cx = sx * 113
        # the leg = a crenellated tower riding the wall runway (bogies), 16 x 24, up to z 108
        A["crane"].box(cx - 9, gy - 14, WT, cx + 9, gy + 14, WT + 5)          # the bogie sill
        A["crane"].box(cx - 8, gy - 12, WT + 5, cx + 8, gy + 12, 108)
        merlons(A["crane"], cx - 8, gy - 12, cx + 8, gy + 12, 108, step=4.0, h=5.0)
        for (tx, ty) in ((cx - 8, gy - 12), (cx + 8, gy - 12), (cx - 8, gy + 12), (cx + 8, gy + 12)):
            A["crane"].cyl(tx, ty, 3.2, 92, 114, n=12)                           # corner bartizans
            A["keep"].cyl(tx, ty, 2.0, 114, 119, n=12)
    # the span: a battlemented box girder between the legs, z 84..100, 14 deep; cantilevers N and S? (no: the
    # gantry rolls to the train; the span stays between the legs)
    A["crane"].box(-105, gy - 7, 84, 105, gy + 7, 100)
    merlons(A["crane"], -105, gy - 7, 105, gy + 7, 100, step=6.0, h=4.0, t=2.0)
    # machicolation brackets under the span
    for k in range(-16, 17):
        A["crane"].box(k * 6.2 - 1.2, gy - 8.5, 80, k * 6.2 + 1.2, gy + 8.5, 84)
    # the trolley keep: rides the span (x = -18): 28 x 24, z 100..134, corner turrets, the server crown
    kx = -18.0
    A["keep"].box(kx - 14, gy - 12, 100, kx + 14, gy + 12, 134)
    merlons(A["keep"], kx - 14, gy - 12, kx + 14, gy + 12, 134, step=4.0, h=5.0)
    for (tx, ty) in ((kx - 14, gy - 12), (kx + 14, gy - 12), (kx - 14, gy + 12), (kx + 14, gy + 12)):
        A["keep"].cyl(tx, ty, 3.6, 110, 142, n=12)
    A["server"].box(kx - 6, gy - 6, 134, kx + 6, gy + 6, 142)
    # the operator cab under the span + the hoist: 4 ropes to a spreader carrying a container (z 46)
    A["keep"].box(kx - 6, gy - 10, 72, kx + 6, gy - 2, 80)
    for (ox, oy) in ((-6, -3), (6, -3), (-6, 3), (6, 3)):
        A["rail"].box(kx + ox - 0.3, gy + oy - 0.3, 54, kx + ox + 0.3, gy + oy + 0.3, 80)
    A["crane"].box(kx - 8, gy - 4, 52, kx + 8, gy + 4, 54)
    A["stack2"].box(kx - 7, gy - 3, 45, kx + 7, gy + 3, 52)


def concept_B(A):
    A["_clear_centre"] = Acc()
    common(A)
    cx, cy = -6.0, -6.0
    A["tower"].cyl(cx, cy, 28, 0, 70, n=36)
    merlon_ring(A["tower"], cx, cy, 27, 70, n=28, h=5.0)
    A["keep"].cyl(cx, cy, 18, 70, 96, n=32)                   # the slewing turret
    merlon_ring(A["keep"], cx, cy, 17, 96, n=24, h=4.0)
    A["server"].cyl(cx, cy, 6, 96, 104, n=16)
    # the jib toward the NE over the train (azimuth 35 deg from north) + the counter-jib with a crenellated weight
    az = math.radians(62)
    ux, uy = math.sin(az), math.cos(az)
    L = 150.0
    A["crane"].beam((cx + ux * 14, cy + uy * 14, 98), (cx + ux * L, cy + uy * L, 98), 8, 7)
    A["crane"].beam((cx, cy, 104), (cx + ux * 10, cy + uy * 10, 104), 6, 22)
    for k in range(1, 9):
        p = (cx + ux * (14 + k * 16), cy + uy * (14 + k * 16), 105)
        A["crane"].beam((p[0], p[1], 105), (p[0] + ux * 0.1, p[1] + uy * 0.1, 105), 1.2, 3)
    A["crane"].beam((cx - ux * 14, cy - uy * 14, 98), (cx - ux * 56, cy - uy * 56, 98), 9, 7)
    wx, wy = cx - ux * 50, cy - uy * 50
    A["tower"].box(wx - 9, wy - 9, 84, wx + 9, wy + 9, 105)
    merlons(A["tower"], wx - 9, wy - 9, wx + 9, wy + 9, 105, step=4.0, h=4.0)
    tx, ty = cx + ux * 120, cy + uy * 120
    A["rail"].box(tx - 0.3, ty - 0.3, 40, tx + 0.3, ty + 0.3, 98)
    A["stack1"].box(tx - 7, ty - 3, 33, tx + 7, ty + 3, 40)
    for sx in (-1, 1):                                       # drum towers on the S corners reshaped round
        pass


def concept_C(A):
    common(A, rail_tower_arch=False)
    # the quayside keep: an STS crane straddling the two tracks (legs at y 90 and 122), portal 60 wide, at x = 10
    px = 10.0
    for lx in (px - 30, px + 30):
        for ly in (88.0, 124.0):
            A["crane"].box(lx - 4, ly - 4, 0, lx + 4, ly + 4, 70)
            merlons(A["crane"], lx - 4, ly - 4, lx + 4, ly + 4, 70, step=3.0, h=3.0, t=1.5)
        A["crane"].box(lx - 4, 84, 62, lx + 4, 128, 72)
    A["crane"].box(px - 34, 84, 66, px + 34, 128, 74)
    # the machinery house = the keep, crenellated, on the portal (z 74..108), the cab
    A["keep"].box(px - 20, 92, 74, px + 20, 122, 108)
    merlons(A["keep"], px - 20, 92, px + 20, 122, 108, step=4.0, h=5.0)
    for (tx, ty) in ((px - 20, 92), (px + 20, 92), (px - 20, 122), (px + 20, 122)):
        A["keep"].cyl(tx, ty, 3.4, 96, 116, n=12)
    A["server"].box(px - 6, 101, 108, px + 6, 113, 116)
    # the A-frame + the boom lowered south over the bailey to the south wall (y -100), back-reach north
    A["crane"].beam((px - 12, 106, 108), (px - 12, 106, 150), 4, 1)
    A["crane"].beam((px + 12, 106, 108), (px + 12, 106, 150), 4, 1)
    A["crane"].box(px - 14, 104, 148, px + 14, 108, 152)
    A["crane"].box(px - 5, -104, 78, px + 5, 160, 86)
    merlons(A["crane"], px - 5, -104, px + 5, 160, 86, step=5.0, h=3.0, t=1.5)
    for yy in (-60.0, 20.0):
        A["rail"].beam((px, 106, 150), (px, yy, 86), 1.0, 1.0)
    A["rail"].box(px - 0.3, -20 - 0.3, 40, px + 0.3, -20 + 0.3, 78)
    A["stack3"].box(px - 7, -23, 33, px + 7, -17, 40)


def render(name):
    sc = bpy.context.scene
    try:
        sc.render.engine = "BLENDER_WORKBENCH"
    except TypeError:
        sc.render.engine = "WORKBENCH"
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.color_type = "OBJECT"
    sh.show_cavity = True
    sh.cavity_type = "BOTH"
    sh.show_shadows = True
    sh.shadow_intensity = 0.55
    sh.background_type = "VIEWPORT" if hasattr(sh, "background_type") else None
    try:
        sh.background_color = (0.02, 0.025, 0.04)
    except AttributeError:
        pass
    sc.display.light_direction = (0.35, -0.55, 0.75)
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.color = (0.02, 0.025, 0.04)
    sc.render.film_transparent = False
    sc.render.resolution_x, sc.render.resolution_y = 960, 540
    sc.render.resolution_percentage = 100
    sc.display.render_aa = "8"
    sc.view_settings.view_transform = "Standard"
    cd = bpy.data.cameras.new("cam")
    cd.lens = 36.0
    cd.sensor_width = 36.0
    cd.clip_end = 5000
    cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    # the overview: high 3/4 from the SSW (camera azimuth 205 deg from north = looking NNE), pitch 36
    from mathutils import Vector
    tgt = Vector((0.0, 4.0, 30.0))
    yaw, pitch, dist = math.radians(22.0), math.radians(36.0), 610.0
    d = Vector((math.sin(yaw) * math.cos(pitch), math.cos(yaw) * math.cos(pitch), -math.sin(pitch)))
    cam.location = tgt - d * dist
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)


for which in WHICH:
    A = fresh()
    {"A": concept_A, "B": concept_B, "C": concept_C}[which](A)
    A.pop("_clear_centre", None)
    flush(A)
    render("thumb_" + which)
    print("rendered", which, flush=True)
