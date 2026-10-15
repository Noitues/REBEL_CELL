"""AAA-2 r2 (exec'd into scene_aaa.py after dress2_aaa.py, before the meshes are merged). Every part has its own seed.

1. Route column 5 as a CUT DRUM (designer note 5): a round tower of radius sqrt(w^2 + d^2) / 2, so it contains the
   column's box. Floors without a route room are full drum storeys (projecting floor plates, ribbon windows, ribs);
   floors with a room are sliced flat at the column's front plane (y = DY), so the V3 room box shows in the cut and
   the drum's back half curves round it. Rooms, links and anchors are unchanged.
2. ADJOINING columns 1 + 2: a connecting podium in the alley (storefront, roof terrace) and a terraced block on
   shared walls behind them. FAT column 0: a wide, stepped annex on its left shares the column's wall.
3. NO CARS (designer note 1): the sky traffic bodies, lights and trails are hidden (street cars, parked cars and the
   foreground van are never built, see scene_aaa.py). Traffic is long-exposure light streaks: white / warm headlight
   streaks one way, red tail-light streaks the other, 4 street lanes and 4 sky lanes, varied lengths and strengths.
4. The lotus holo is replaced by a readable SOLACE holo ad.
"""
import random as _rr2

# ------------------------------------------------------------------ 1. the cut drum (route column DRUM_COL)
_l = DRUM_COL
_x0, _x1 = LY["cols"][str(_l)]
_dy = LY["dy"][_l]
_st = LY["storeys"][str(_l)]
_rf = ROUTE_FLOORS.get(_l, {})
_col = FAMS[(_l * 3 + 1) % len(FAMS)]
with OwnRng(9301):
    set_sem(0.1, 0, _l)
    _cx, _cy, _R, _top = cut_drum(_x0, _x1, _dy, _st, set(_rf), _col, TRIMS[_l % len(TRIMS)])
DRUM_INFO = dict(col=_l, cx=_cx, cy=_cy, r=_R, top=_top)

# ------------------------------------------------------------------ 2. adjoining columns 1 + 2, fat column 0
with OwnRng(9310):
    c1, c2 = LY["cols"]["1"], LY["cols"]["2"]
    fam1 = FAMS[(1 * 3 + 1) % len(FAMS)]
    set_sem(0.1, 0, 1)
    # the connecting podium in alley 1 (behind every link: links run at y = DY + YF)
    px0, px1, py0, py1, ph = c1[1] - 0.6, c2[0] + 0.6, 4.2, 16.0, 6.4
    prism(fp_rect(px0, py0, px1, py1), 0.0, ph, tuple(v * 0.9 for v in fam1))
    quad_y(NEON, px0 + 0.8, 0.6, px1 - 0.8, 3.2, py0 - 0.06, (0.16 * 0.4, 0.83 * 0.4, 1.0 * 0.4))
    box(px0 + 0.4, py0 - 1.6, 3.6, px1 - 0.4, py0, 3.9, (0.5, 0.15, 0.3), facet=False)
    for k in range(6):
        wx = px0 + 1.0 + k * (px1 - px0 - 2.0) / 6
        WIN.face([(wx, py0 - 0.05, 4.4), (wx + 1.2, py0 - 0.05, 4.4), (wx + 1.2, py0 - 0.05, 5.6), (wx, py0 - 0.05, 5.6)],
                 (0.5, 0.34, 0.14) if k % 2 else (0.18, 0.12, 0.06), (0, 0, 0))
    # a set-back second podium storey that runs into both towers' side walls (they read as one joined complex)
    prism(fp_rect(px0, py0 + 3.0, px1, py1), ph, ph + 6.0, tuple(v * 0.84 for v in fam1))
    for k in range(5):
        wx = px0 + 1.2 + k * (px1 - px0 - 2.4) / 5
        WIN.face([(wx, py0 + 2.95, ph + 1.6), (wx + 1.3, py0 + 2.95, ph + 1.6), (wx + 1.3, py0 + 2.95, ph + 4.2),
                  (wx, py0 + 2.95, ph + 4.2)], (0.62, 0.42, 0.18) if k != 2 else (0.2, 0.5, 0.62), (0, 0, 0))
    beam((px0, py0 + 3.2, ph + 6.9), (px1, py0 + 3.2, ph + 6.9), 0.08, (0.25, 0.25, 0.28))
    # roof terrace: parapet rail and planters
    beam((px0, py0 + 0.2, ph + 1.0), (px1, py0 + 0.2, ph + 1.0), 0.08, (0.25, 0.25, 0.28))
    for k in range(4):
        tx = px0 + 1.5 + k * 2.6
        box(tx, py0 + 0.6, ph, tx + 1.2, py0 + 1.4, ph + 0.6, (0.3, 0.22, 0.16), facet=False)
        box(tx - 0.1, py0 + 0.5, ph + 0.6, tx + 1.3, py0 + 1.5, ph + 1.3, (0.1, 0.26, 0.14), facet=False)
    # the terraced block on shared walls behind both columns (background class: the shader lights its windows)
    set_sem(0.6, 0, 0)
    terraced_run(c1[0] + 2.0, 22.0, c2[1] + 2.0, 34.0, (58.0, 50.0, 42.0), tuple(v * 0.8 for v in fam1), PINK)
    # fat column 0: a wide stepped annex on its left, sharing the column's wall
    c0 = LY["cols"]["0"]
    fam0 = FAMS[(0 * 3 + 1) % len(FAMS)]
    set_sem(0.1, 0, 0)
    ay0 = LY["dy"][0] + 1.0
    for (ax0, ax1, ah) in ((c0[0] - 12.0, c0[0] - 6.0, 9.5), (c0[0] - 6.0, c0[0] + 0.2, 13.5)):
        prism(fp_rect(ax0, ay0, ax1, ay0 + 11.0), 0.0, ah, tuple(v * 0.88 for v in fam0))
        box(ax0, ay0 - 0.4, ah, ax1, ay0, ah + 0.9, tuple(v * 0.75 for v in fam0), facet=False)
        for row in range(int((ah - 4.0) / 3.2)):
            for k in range(int((ax1 - ax0 - 1.0) / 2.0)):
                wx, wz = ax0 + 0.8 + k * 2.0, 4.6 + row * 3.2
                if _rr2.Random(int(wx * 100 + wz * 7)).random() < 0.45:
                    WIN.face([(wx, ay0 - 0.05, wz), (wx + 1.1, ay0 - 0.05, wz), (wx + 1.1, ay0 - 0.05, wz + 1.6),
                              (wx, ay0 - 0.05, wz + 1.6)], (0.5, 0.33, 0.13), (0, 0, 0))
    quad_y(NEON, c0[0] - 11.4, 0.6, c0[0] - 0.8, 3.0, ay0 - 0.06, (1.0 * 0.4, 0.16 * 0.4, 0.54 * 0.4))

# ------------------------------------------------------------------ 3. no cars: hide the sky traffic
_gone = set()
for _objs, _x0_, _y_, _z_, _sp_ in TRAFFIC:
    for _o in _objs:
        _gone.add(_o.name)
for _lst in (SOLID_OBJS, NEON_OBJS, ATMOS_OBJS):
    _lst[:] = [o for o in _lst if o.name not in _gone]
for _nm in sorted(_gone):
    bpy.data.objects.remove(bpy.data.objects[_nm], do_unlink=True)
TRAFFIC.clear()
print("shapes_r2: removed %d sky-traffic objects (bodies, lights, trails)" % len(_gone), flush=True)


# ------------------------------------------------------------------ 3. long-exposure light streaks
def mat_streak(name, k):
    m = bpy.data.materials.new(name)
    for prop, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
        try:
            setattr(m, prop, val)
        except (AttributeError, TypeError):
            pass
    nt = m.node_tree
    nt.nodes.clear()
    L = nt.links.new
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    ca = nt.nodes.new("ShaderNodeAttribute")
    ca.attribute_name = "scol"
    em = nt.nodes.new("ShaderNodeEmission")
    L(ca.outputs["Color"], em.inputs["Color"])
    pw = attr(nt, "pwo", "OBJECT")
    pwk = math_n(nt, "ADD", pw.outputs["Fac"], math_n(nt, "LESS_THAN", pw.outputs["Fac"], 0.001))
    L(math_n(nt, "MULTIPLY", pwk, k), em.inputs["Strength"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    add = nt.nodes.new("ShaderNodeAddShader")
    L(tr.outputs[0], add.inputs[0])
    L(em.outputs[0], add.inputs[1])
    L(add.outputs[0], out.inputs["Surface"])
    return m


STREAK_K = JOB.get("streak_k", 1.0)
STREAK_M = mat_streak("hr_streak", 1.0)
STREAK_OBJS = []
CALM = (70.0, 114.0)


class Streaks:
    """Camera-facing ribbons along x; per-vertex colour = colour x strength x end fade (x the calm-zone damping)."""

    def __init__(self, name):
        self.name = name
        self.bm = bmesh.new()
        self.cl = self.bm.loops.layers.float_color.new("scol")

    def add(self, xa, xb, y, z, th, col, k, r, bob=0.0, bob_len=70.0, slope=0.0, fade=0.14, dash=None, calm_k=1.0, arc=0.0,
            head=0):
        L = xb - xa
        n = max(2, int(L / (1.5 if not dash else dash / 4.0)))   # dashed lines need several vertices per dash
        ph = r.uniform(0, 2 * math.pi)
        prev = None
        for i in range(n + 1):
            t = i / n
            x = xa + L * t
            zz = z + bob * math.sin(2 * math.pi * x / bob_len + ph) + slope * (x - xa) + arc * 4 * t * (1 - t)
            e = min(1.0, t / fade, (1 - t) / fade)
            e = e * e * (3 - 2 * e)
            if head:      # r3: one vehicle = a bright head and a fading tail (head = +1 at xb, -1 at xa)
                u = t if head > 0 else 1.0 - t
                e = min(1.0, (1.0 - u) / 0.06) * (0.06 + 0.94 * u ** 2.2)
            e *= 0.9 + 0.2 * r.random()
            if dash and (int(x / dash) % 2):
                e *= 0.08
            if CALM[0] - 6 < x < CALM[1] + 6:
                e *= calm_k
            c = tuple(v * k * e for v in col)
            cur = (x, zz, c)
            if prev:
                (xp, zp, cp) = prev
                vs = [self.bm.verts.new(p) for p in ((xp, y, zp - th / 2), (x, y, zz - th / 2), (x, y, zz + th / 2),
                                                     (xp, y, zp + th / 2))]
                f = self.bm.faces.new(vs)
                for lp, cc in zip(f.loops, (cp, c, c, cp)):
                    lp[self.cl] = (cc[0], cc[1], cc[2], 1.0)
            prev = cur

    def obj(self):
        me = bpy.data.meshes.new(self.name)
        self.bm.to_mesh(me)
        self.bm.free()
        ob = bpy.data.objects.new(self.name, me)
        scene.collection.objects.link(ob)
        me.materials.append(STREAK_M)
        HOLO_OBJS.append(ob)          # hidden in the data passes; the hover power cut sets its "pwo"
        STREAK_OBJS.append(ob)
        return ob


HEAD = [(1.0, 0.96, 0.9)] * 6 + [(1.0, 0.78, 0.5)] * 3 + [(0.85, 0.92, 1.0)]
TAIL = (1.0, 0.045, 0.03)
AMBER_IND = (1.0, 0.45, 0.05)
# lane: y, z, head (True) or tail, base strength, thickness, length range, gap range, extra lines
STREET_LANES = [(-13.0, 0.72, True, 2.6, 0.11), (-17.2, 0.74, True, 2.0, 0.11),
                (-28.6, 0.92, False, 3.4, 0.12), (-31.8, 0.90, False, 2.8, 0.12)]
# sky: short curved streaks (aircars bank and climb), never ruler lines across the frame (designer note, round 2)
SKY_LANES = [(52.0, 86.0, True, 2.0, 0.22), (57.0, 92.0, False, 3.0, 0.24), (118.0, 120.0, False, 1.8, 0.34)]
def build_still_streaks(ys, sky):
    """r3: the still's traffic streaks, on the rule-placed lanes (rules_r3.py: the street transect and the skyline);
    ys = the 4 street lane depths, sky = [(y, z)] per sky lane. Called from fog_r3.py after the rules run."""
    _sr = _rr2.Random(9400)
    st_street = Streaks("streaks_street")
    for (y, z, head, kk, th) in [(ys[k],) + STREET_LANES[k][1:] for k in range(len(STREET_LANES))]:
        x = -60.0 + _sr.uniform(0, 25)
        while x < 240.0:
            L = _sr.uniform(12.0, 80.0)
            k = kk * _sr.uniform(0.3, 1.0) * STREAK_K
            col = _sr.choice(HEAD) if head else TAIL
            zz = z + _sr.uniform(-0.06, 0.06)
            st_street.add(x, x + L, y, zz, th * _sr.uniform(0.85, 1.15), col, k, _sr)
            if _sr.random() < 0.35:     # the second lamp of the pair / the reflector line: fainter, a hair above or below
                st_street.add(x + 0.4, x + L - 0.4, y + 0.2, zz + (0.3 if head else -0.32), th * 0.7, col, k * 0.35, _sr)
            if _sr.random() < 0.12:     # a turning car's indicator: a dashed amber line
                st_street.add(x + L * 0.3, x + L, y - 0.1, zz + 0.05, th * 0.8, AMBER_IND, kk * 0.6, _sr, dash=1.6)
            if _sr.random() < 0.10:     # a tall truck: amber marker lights high up
                st_street.add(x, x + L * 0.8, y + 0.3, 2.8, th * 0.8, AMBER_IND, kk * 0.35, _sr)
            x += L + _sr.uniform(10.0, 55.0)
    st_street.obj()
    st_sky = Streaks("streaks_sky")
    # r3 art review: the sky lanes read as drawn rules. Fewer, shorter, separate vehicles (bright head, fading tail, gaps),
    # each at its own climb or descent angle; no nav-strobe dotted lines. The draws stay on the shared 9400 stream order
    # only for the street lanes above; the sky uses its own stream (9410).
    _sk = _rr2.Random(9410)
    SKY_DIR = [1, -1, 1]
    for li, (y, z, head, kk, th) in enumerate([tuple(sky[k]) + SKY_LANES[k][2:] for k in range(len(sky))]):
        x = -80.0 + _sk.uniform(0, 50)
        while x < 260.0:
            L = _sk.uniform(6.0, 16.0)
            k = kk * _sk.uniform(0.5, 1.0) * STREAK_K * 1.4
            col = _sk.choice(HEAD) if head else TAIL
            zz = z + _sk.uniform(-6.0, 6.0)
            sl = _sk.choice((-1, 1)) * _sk.uniform(0.05, 0.12)
            st_sky.add(x, x + L, y, zz, th * 1.1, col, k, _sk, slope=sl, calm_k=0.35, head=SKY_DIR[li])
            x += L + _sk.uniform(60.0, 160.0)
    st_sky.obj()


# ------------------------------------------------------------------ 4. the SOLACE holo ad where the lotus was
ad_plane("holo_solace", 40.0, 40.0, 70.0, 14.0, 7.9, k=1.6, holo=True)
print("shapes_r2: drum r %.2f at (%.1f, %.1f); streak objects %d" % (_R, _cx, _cy, len(STREAK_OBJS)), flush=True)
