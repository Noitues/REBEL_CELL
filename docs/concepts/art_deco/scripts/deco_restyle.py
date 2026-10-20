"""Art-deco restyle, shared by every panel. Runs INSIDE Blender, after a base pipeline has built its scene and before it
renders (deco_blender_hq.py inserts `apply_hq(globals(), cfg)` in front of the render section of hq_scene.py).

What it does (see BRIEF.md "The deco vocabulary"):
  materials  facade / panel materials -> black lacquer + gold-leaf mullion and seam grid; metal -> brass / gold
  massing    setback stepping (3-5 tiers at ~80 %), corner and face piers running past the roofline, chevron bands,
             sunburst / fan crowns on the tallest towers in frame
  light      thin parallel-line neon (corp hue) on every setback edge and pier; floodlights from the base; the colour
             signs and blobs of the base city are hidden or recoloured to gold / corp hue
  air        Hugh Ferriss charcoal fog (warm grey scatter), towers dissolving upward
All randomness is seeded (random.Random(seed + index)); same job -> same scene.
"""
import math
import random

import bpy
from mathutils import Vector

CORP_HUES = {"halcyon": ((0.43, 0.16, 1.0), (1.0, 0.40, 0.03)), "meridian": ((1.0, 0.26, 0.01), (1.0, 0.03, 0.02)),
             "orbital": ((0.61, 0.87, 1.0), (1.0, 0.45, 0.06)), "solace": ((0.30, 1.0, 0.06), (1.0, 0.05, 0.30))}
GOLD_LIN = (1.0, 0.62, 0.16)        # gold leaf (linear)
BRASS_LIN = (0.80, 0.46, 0.14)
LACQ_LIN = (0.010, 0.010, 0.014)
GOLD_EMIT = 0.05                    # gold leaf never goes dead: a little self-light (lit by the street, not a lamp)


# ----------------------------------------------------------------------------------------------- mesh accumulator
class DAcc:
    """Quads and prisms of one material, built into one object (the same idea as the pipelines' Acc)."""

    def __init__(self, name, mat, coll=None, pass_index=2):
        self.name, self.mat, self.coll, self.idx = name, mat, coll, pass_index
        self.v, self.f = [], []

    def face(self, pts):
        b = len(self.v)
        self.v.extend(tuple(p) for p in pts)
        self.f.append(tuple(range(b, b + len(pts))))

    def box(self, x0, y0, z0, x1, y1, z1, bottom=False):
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        z0, z1 = min(z0, z1), max(z0, z1)
        p = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        fs = [(4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        if bottom:
            fs.append((0, 3, 2, 1))
        for f in fs:
            self.face([p[i] for i in f])

    def prism(self, poly, o, u, v, n, t):
        """Extrude a 2D polygon (list of (a, b)) that lives in the plane spanned by u, v at origin o, by t along n."""
        o, u, v, n = Vector(o), Vector(u), Vector(v), Vector(n)
        lo = [o + u * a + v * b for a, b in poly]
        hi = [p + n * t for p in lo]
        m = len(poly)
        self.face(list(reversed(lo)))
        self.face(hi)
        for i in range(m):
            j = (i + 1) % m
            self.face([lo[i], lo[j], hi[j], hi[i]])

    def bar(self, p0, p1, w, h=None):
        """A thin square bar between two points (w x h cross-section)."""
        p0, p1 = Vector(p0), Vector(p1)
        d = p1 - p0
        L = d.length
        if L < 1e-6:
            return
        d /= L
        ref = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
        a = d.cross(ref).normalized() * (w * 0.5)
        b = d.cross(a).normalized() * ((h if h is not None else w) * 0.5)
        c = [p0 - a - b, p0 + a - b, p0 + a + b, p0 - a + b]
        e = [q + d * L for q in c]
        self.face(list(reversed(c)))
        self.face(e)
        for i in range(4):
            j = (i + 1) % 4
            self.face([c[i], c[j], e[j], e[i]])

    def build(self):
        if not self.f:
            return None
        me = bpy.data.meshes.new(self.name)
        me.from_pydata(self.v, [], self.f)
        me.validate()
        ob = bpy.data.objects.new(self.name, me)
        (self.coll or bpy.context.scene.collection).objects.link(ob)
        ob.data.materials.append(self.mat)
        ob.pass_index = self.idx
        ob["pwo"] = 1.0
        try:
            ob.visible_shadow = True
        except AttributeError:
            pass
        return ob


# ----------------------------------------------------------------------------------------------- materials
def _mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes.clear()
    return m, m.node_tree


def principled(name, base, metal=0.0, rough=0.3, coat=0.0, coat_rough=0.05, emit=None, emit_k=0.0):
    m, nt = _mat(name)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = tuple(base)[:3] + (1.0,)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Coat Roughness"].default_value = coat_rough
    if emit is not None:
        b.inputs["Emission Color"].default_value = tuple(emit)[:3] + (1.0,)
        b.inputs["Emission Strength"].default_value = emit_k
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


def emission(name, col, k):
    m, nt = _mat(name)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = tuple(col)[:3] + (1.0,)
    e.inputs["Strength"].default_value = k
    nt.links.new(e.outputs[0], out.inputs[0])
    return m


class Mats:
    def __init__(self):
        self.lacquer = principled("deco_lacquer", LACQ_LIN, 0.0, 0.10, coat=1.0, coat_rough=0.03)
        self.gold = principled("deco_gold", GOLD_LIN, 1.0, 0.24, emit=GOLD_LIN, emit_k=GOLD_EMIT)
        self.brass = principled("deco_brass", BRASS_LIN, 1.0, 0.34)
        self._em = {}

    def neon(self, col, k):
        key = (round(col[0], 3), round(col[1], 3), round(col[2], 3), round(k, 2))
        if key not in self._em:
            self._em[key] = emission("deco_neon_%d" % len(self._em), col, k)
        return self._em[key]


def find_nodes(mat, kind):
    return [n for n in mat.node_tree.nodes if n.bl_idname == kind] if mat and mat.use_nodes else []


def _math(nt, op, a, b=None, c=None):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    for i, v in enumerate((a, b, c)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            nt.links.new(v, n.inputs[i])
    return n.outputs[0]


def _mix(nt, fac, a, b):
    n = nt.nodes.new("ShaderNodeMix")
    n.data_type = "RGBA"
    for sock, v in ((n.inputs[0], fac), (n.inputs[6], a), (n.inputs[7], b)):
        if isinstance(v, (int, float)):
            sock.default_value = v
        elif isinstance(v, tuple):
            sock.default_value = tuple(v)[:3] + (1.0,)
        else:
            nt.links.new(v, sock)
    return n.outputs[2]


def _linked_from(sock):
    return sock.links[0].from_socket if sock.is_linked else None


def lacquer_facade(mat, mull_u=2.1, mull_v=3.1, band_every=12, gold=GOLD_LIN, dark=0.16, window_tint=(1.0, 0.80, 0.50),
                   mull_w=0.06, span_w=0.06, band_w=0.032, rough_k=0.55, fade0=120.0, fade1=320.0, band_emit=0.45, win_boost=1.0):
    """Turn a procedural building material (Principled + position-driven window grid) into black lacquer with a gold-leaf
    mullion grid: vertical mullions each window cell, a spandrel line each floor, a thick gold band each `band_every`
    floors. Window emission stays (so the windows still light) but its colour is pulled toward warm gold."""
    nt = mat.node_tree
    for b in find_nodes(mat, "ShaderNodeBsdfPrincipled"):
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        sp = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(geo.outputs["Position"], sp.inputs[0])
        X, Y, Z = sp.outputs["X"], sp.outputs["Y"], sp.outputs["Z"]
        u = _math(nt, "ADD", X, Y)
        fu = _math(nt, "FRACT", _math(nt, "DIVIDE", u, mull_u))
        fv = _math(nt, "FRACT", _math(nt, "DIVIDE", Z, mull_v))
        fb = _math(nt, "FRACT", _math(nt, "DIVIDE", Z, mull_v * band_every))
        vm = _math(nt, "ADD", _math(nt, "LESS_THAN", fu, mull_w), _math(nt, "GREATER_THAN", fu, 1.0 - mull_w))
        hm = _math(nt, "ADD", _math(nt, "LESS_THAN", fv, span_w), _math(nt, "GREATER_THAN", fv, 1.0 - span_w * 0.3))
        bm = _math(nt, "LESS_THAN", fb, band_w)
        cd = nt.nodes.new("ShaderNodeCameraData")
        dist = cd.outputs["View Distance"]
        near = _math(nt, "MAXIMUM", _math(nt, "MINIMUM", _math(nt, "DIVIDE", _math(nt, "SUBTRACT", fade1, dist), fade1 - fade0), 1.0), 0.0)
        fine = _math(nt, "MULTIPLY", _math(nt, "ADD", vm, hm), near)
        nz_ = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(geo.outputs["Normal"], nz_.inputs[0])
        vert = _math(nt, "LESS_THAN", _math(nt, "ABSOLUTE", nz_.outputs["Z"]), 0.35)       # walls only: roofs stay lacquer
        gm = _math(nt, "MULTIPLY", _math(nt, "MINIMUM", _math(nt, "ADD", fine, bm), 1.0), vert)
        # base colour: lacquer, scaled original (keeps the per-building tint a little), gold on the grid
        bc = b.inputs["Base Color"]
        src = _linked_from(bc)
        orig = src
        if orig is not None:
            vs = nt.nodes.new("ShaderNodeVectorMath")
            vs.operation = "SCALE"
            nt.links.new(orig, vs.inputs[0])
            vs.inputs["Scale"].default_value = dark
            lac = vs.outputs[0]
        else:
            lac = tuple(c * dark for c in bc.default_value[:3])
        col = _mix(nt, gm, lac, tuple(gold))
        nt.links.new(col, bc)
        nt.links.new(gm, b.inputs["Metallic"])
        rs = _linked_from(b.inputs["Roughness"])
        base_r = rs if rs is not None else b.inputs["Roughness"].default_value
        if rs is not None:
            r0 = _math(nt, "MULTIPLY", rs, rough_k)
        else:
            r0 = base_r * rough_k
        nt.links.new(_math(nt, "ADD", _math(nt, "MULTIPLY", r0, _math(nt, "SUBTRACT", 1.0, gm)),
                           _math(nt, "MULTIPLY", gm, 0.26)), b.inputs["Roughness"])
        b.inputs["Coat Weight"].default_value = 1.0
        b.inputs["Coat Roughness"].default_value = 0.04
        ec = b.inputs["Emission Color"]
        es = _linked_from(ec)
        est = _linked_from(b.inputs["Emission Strength"])
        # the windows keep their light (tinted toward warm gold); the gold bands get a steady self-glow, so they read as
        # thin gold lines at any distance (gold leaf under the street light) instead of brown smears
        if es is not None:
            if window_tint is not None:
                vm2 = nt.nodes.new("ShaderNodeVectorMath")
                vm2.operation = "MULTIPLY"
                nt.links.new(es, vm2.inputs[0])
                vm2.inputs[1].default_value = tuple(window_tint)
                es = vm2.outputs[0]
            wl = nt.nodes.new("ShaderNodeVectorMath")
            wl.operation = "SCALE"
            nt.links.new(es, wl.inputs[0])
            if est is not None:
                nt.links.new(_math(nt, "MULTIPLY", est, win_boost), wl.inputs["Scale"])
            else:
                wl.inputs["Scale"].default_value = b.inputs["Emission Strength"].default_value * win_boost
            gl = nt.nodes.new("ShaderNodeVectorMath")
            gl.operation = "SCALE"
            gl.inputs[0].default_value = tuple(gold)
            nt.links.new(_math(nt, "MULTIPLY", gm, band_emit), gl.inputs["Scale"])
            ad = nt.nodes.new("ShaderNodeVectorMath")
            ad.operation = "ADD"
            nt.links.new(wl.outputs[0], ad.inputs[0])
            nt.links.new(gl.outputs[0], ad.inputs[1])
            for lk in list(b.inputs["Emission Strength"].links):
                nt.links.remove(lk)
            b.inputs["Emission Strength"].default_value = 1.0
            nt.links.new(ad.outputs[0], ec)


def lacquer_panels(mat, gold=GOLD_LIN, dark=0.22, seam_gold=0.85):
    """The landmark's composite panels: dark lacquer with the panel grid's mortar lines in gold leaf."""
    nt = mat.node_tree
    bricks = find_nodes(mat, "ShaderNodeTexBrick")
    for b in find_nodes(mat, "ShaderNodeBsdfPrincipled"):
        bc = b.inputs["Base Color"]
        src = _linked_from(bc)
        if src is None:
            continue
        vs = nt.nodes.new("ShaderNodeVectorMath")
        vs.operation = "SCALE"
        nt.links.new(src, vs.inputs[0])
        vs.inputs["Scale"].default_value = dark
        if bricks:
            mort = _math(nt, "SUBTRACT", 1.0, bricks[0].outputs["Fac"])
            mort = _math(nt, "MINIMUM", _math(nt, "MULTIPLY", mort, 4.0), 1.0)
            gm = _math(nt, "MULTIPLY", mort, seam_gold)
            nt.links.new(_mix(nt, gm, vs.outputs[0], tuple(gold)), bc)
            nt.links.new(gm, b.inputs["Metallic"])
        else:
            nt.links.new(vs.outputs[0], bc)
        b.inputs["Coat Weight"].default_value = 1.0
        b.inputs["Coat Roughness"].default_value = 0.04


def brass_metal(mat, tint=BRASS_LIN, metal=1.0, rough=0.42):
    for b in find_nodes(mat, "ShaderNodeBsdfPrincipled"):
        nt = mat.node_tree
        bc = b.inputs["Base Color"]
        src = _linked_from(bc)
        if src is not None:
            vm = nt.nodes.new("ShaderNodeVectorMath")
            vm.operation = "MULTIPLY"
            nt.links.new(src, vm.inputs[0])
            vm.inputs[1].default_value = tuple(t * 1.1 for t in tint)
            nt.links.new(vm.outputs[0], bc)
        else:
            bc.default_value = tuple(tint) + (1.0,)
        b.inputs["Metallic"].default_value = metal
        if not b.inputs["Roughness"].is_linked:
            b.inputs["Roughness"].default_value = rough


def recolor_attr(ob, fn):
    """Rewrite the per-corner 'col' attribute of a pipeline mesh: fn(rgb) -> rgb."""
    if ob is None:
        return
    ca = ob.data.color_attributes.get("col")
    if ca is None:
        return
    for d in ca.data:
        c = d.color
        r, g_, b = fn((c[0], c[1], c[2]))
        d.color = (r, g_, b, c[3])


def hue_close(c, ref, tol=0.55):
    a = Vector(c).normalized() if Vector(c).length > 1e-6 else Vector(c)
    r = Vector(ref).normalized()
    return (a - r).length < tol


# ----------------------------------------------------------------------------------------------- shared ornaments
def neon_lines(acc, cx, cy, hx, hy, z, n=3, gap=0.9, th=0.26, out=0.12):
    """n parallel thin neon loops round a rectangular tier at heights z, z+gap, ..."""
    for i in range(n):
        zz = z + i * gap
        x0, x1, y0, y1 = cx - hx - out, cx + hx + out, cy - hy - out, cy + hy + out
        acc.box(x0, y0, zz, x1, y0 + th, zz + th)
        acc.box(x0, y1 - th, zz, x1, y1, zz + th)
        acc.box(x0, y0, zz, x0 + th, y1, zz + th)
        acc.box(x1 - th, y0, zz, x1, y1, zz + th)


def vlines(acc, x, y, z0, z1, axis, n=3, gap=0.55, th=0.2):
    """n parallel vertical neon lines (spaced along `axis` 'x' or 'y')."""
    for i in range(n):
        o = (i - (n - 1) / 2.0) * gap
        if axis == "x":
            acc.box(x + o - th / 2, y - th / 2, z0, x + o + th / 2, y + th / 2, z1)
        else:
            acc.box(x - th / 2, y + o - th / 2, z0, x + th / 2, y + o + th / 2, z1)


def chevron_band(acc, o, u, v, n, du, z0, h, w, t):
    """A row of V chevrons on a plane: origin o, along u, up v (unit vectors), normal n = u x v out of the face."""
    nn = Vector(n)
    for k in range(int(du)):
        a = k * 2.0
        poly = [(a, z0 + h), (a + 1.0, z0), (a + 2.0, z0 + h), (a + 2.0 - w, z0 + h), (a + 1.0, z0 + w * 1.4), (a + w, z0 + h)]
        acc.prism(poly, o, u, v, nn, t)


def fan_crown(gold, lac, neon, cx, cy, cz, axis, R, rng, nray=11, t=0.8, ring_th=0.10, backing=True):
    """Sunburst / fan crown: a lacquer half-disc with concentric gold arcs, radial ribs and thin neon arcs, standing in
    the plane `axis` ('x': spans x, normal y; 'y': spans y, normal x). R = outer radius."""
    if axis == "x":
        o, u, n = (cx, cy - t / 2, cz), (1, 0, 0), (0, 1, 0)
    else:
        o, u, n = (cx - t / 2, cy, cz), (0, 1, 0), (1, 0, 0)
    v = (0, 0, 1)
    nseg = 22
    # lacquer half-disc backing
    pts = [(R * math.cos(math.pi * i / nseg), R * math.sin(math.pi * i / nseg)) for i in range(nseg + 1)]
    for i in range(nseg if backing else 0):
        lac.prism([(0, 0), pts[i], pts[i + 1]], o, u, v, n, t)
    # concentric gold arcs (outer rim thick) and neon arcs between them (parallel lines)
    radii = [(1.0, 0.075, "g"), (0.88, 0.022, "n"), (0.83, 0.022, "n"), (0.66, 0.05, "g"), (0.54, 0.02, "n"), (0.49, 0.02, "n"),
             (0.32, 0.05, "g")]
    for r_, w_, kind in radii:
        acc = gold if kind == "g" else neon
        r1, r0 = R * r_, R * (r_ - w_)
        tt = t * (1.5 if kind == "g" else 1.15)
        off = -(tt - t) / 2
        o2 = Vector(o) + Vector(n) * off
        for i in range(nseg):
            a0, a1 = math.pi * i / nseg, math.pi * (i + 1) / nseg
            quad = [(r0 * math.cos(a0), r0 * math.sin(a0)), (r1 * math.cos(a0), r1 * math.sin(a0)),
                    (r1 * math.cos(a1), r1 * math.sin(a1)), (r0 * math.cos(a1), r0 * math.sin(a1))]
            acc.prism(quad, o2, u, v, n, tt)
    # radial gold ribs with triangular windows (the gaps between ribs show the lacquer; neon core down each rib)
    for k in range(nray):
        a = math.pi * (k + 0.5) / nray
        d = (math.cos(a), math.sin(a))
        pw = 0.05 * R
        p = (-d[1] * pw, d[0] * pw)
        r0, r1 = R * 0.30, R * 0.98
        poly = [(d[0] * r0 - p[0], d[1] * r0 - p[1]), (d[0] * r1 - p[0] * 0.4, d[1] * r1 - p[1] * 0.4),
                (d[0] * r1 + p[0] * 0.4, d[1] * r1 + p[1] * 0.4), (d[0] * r0 + p[0], d[1] * r0 + p[1])]
        o2 = Vector(o) + Vector(n) * (-t * 0.25)
        gold.prism(poly, o2, u, v, n, t * 1.5)
    # base plinth
    if axis == "x":
        gold.box(cx - R * 1.04, cy - t, cz - R * 0.06, cx + R * 1.04, cy + t, cz + R * 0.02)
    else:
        gold.box(cx - t, cy - R * 1.04, cz - R * 0.06, cx + t, cy + R * 1.04, cz + R * 0.02)


def spire(gold, neon, cx, cy, z, h, w, n_lines=2):
    gold.box(cx - w, cy - w, z, cx + w, cy + w, z + h * 0.35)
    gold.box(cx - w * 0.6, cy - w * 0.6, z + h * 0.35, cx + w * 0.6, cy + w * 0.6, z + h * 0.7)
    gold.box(cx - w * 0.3, cy - w * 0.3, z + h * 0.7, cx + w * 0.3, cy + w * 0.3, z + h)
    for i in range(n_lines):
        o = (i - (n_lines - 1) / 2.0) * w * 0.9
        neon.box(cx + o - 0.08, cy - w * 1.02, z + h * 0.05, cx + o + 0.08, cy - w * 1.02 + 0.16, z + h * 0.34)
        neon.box(cx + o - 0.08, cy + w * 1.02 - 0.16, z + h * 0.05, cx + o + 0.08, cy + w * 1.02, z + h * 0.34)


# ----------------------------------------------------------------------------------------------- towers
def tower_deco(ctx, x, y, top, hx, hy, rng, tiers, fan, rank, th_k=1.0, ln_k=1.0, crown_k=1.0):
    """Setback the tower into `tiers` stepped lacquer tiers (each ~80 % of the one below), gold cornices, corner piers
    that run past the roofline, parallel neon on every setback edge, chevron band, optional fan crown."""
    L, G, N, NG = ctx["lac"], ctx["gold"], ctx["neon"], ctx["neon2"]
    z = top
    th = max(5.0, min(16.0, top * 0.17)) * (0.85 + 0.3 * rng.random()) * th_k
    sx, sy = hx, hy
    # face piers on the existing upper facade (the tower's top third), with a gold cornice at its top
    for sgn in (-1, 1):
        for q in range(2, int(max(hx, hy) * 2 / 3.4)):
            pass
    pz0 = top - 9.0
    for cxs in (-1, 1):
        for cys in (-1, 1):
            G.box(x + cxs * hx - 0.45, y + cys * hy - 0.45, pz0, x + cxs * hx + 0.45, y + cys * hy + 0.45, top + th * 0.5)
    for sgn in (-1, 1):
        nfx = int(hx * 2 / 7.0)
        for q in range(nfx):
            xx = x - hx + (q + 1) * 2 * hx / (nfx + 1)
            G.box(xx - 0.2, y + sgn * hy - 0.1, pz0, xx + 0.2, y + sgn * hy + 0.3 * sgn, top)
        nfy = int(hy * 2 / 7.0)
        for q in range(nfy):
            yy = y - hy + (q + 1) * 2 * hy / (nfy + 1)
            G.box(x + sgn * hx - 0.1, yy - 0.2, pz0, x + sgn * hx + 0.3 * sgn, yy + 0.2, top)
    G.box(x - hx - 0.4, y - hy - 0.4, top - 0.7, x + hx + 0.4, y + hy + 0.4, top + 0.25)       # cornice
    neon_lines(N, x, y, hx, hy, top - 2.6 * ln_k, n=3, gap=0.55 * ln_k, th=0.2 * ln_k, out=0.14 * ln_k)
    for i in range(tiers):
        h_i = th * (1.0 if i < tiers - 1 else 1.25)
        L.box(x - sx, y - sy, z, x + sx, y + sy, z + h_i)
        # corner piers rising past this tier's roof
        pr = 0.5 if i < tiers - 1 else 0.7
        for cxs in (-1, 1):
            for cys in (-1, 1):
                G.box(x + cxs * sx - pr, y + cys * sy - pr, z, x + cxs * sx + pr, y + cys * sy + pr,
                      z + h_i + (th * 0.5 if i == tiers - 1 else 0.9))
        G.box(x - sx - 0.35, y - sy - 0.35, z + h_i - 0.45, x + sx + 0.35, y + sy + 0.35, z + h_i + 0.15)   # gold parapet
        neon_lines(N, x, y, sx, sy, z + h_i * 0.55, n=3, gap=0.5 * ln_k, th=0.2 * ln_k, out=0.1 * ln_k)
        if i == 0 and sx > 2.5:
            vlines(NG, x + sx, y, z + 0.5, z + h_i - 1.0, "y", n=2, gap=0.5)
            vlines(NG, x - sx, y, z + 0.5, z + h_i - 1.0, "y", n=2, gap=0.5)
        if i < tiers - 1 and sx > 3.0 and rng.random() < 0.8:
            chevron_band(G, (x - sx, y - sy - 0.05, z + h_i * 0.18), (1, 0, 0), (0, 0, 1), (0, -1, 0), sx, 0.0, h_i * 0.22, 0.28, 0.12)
        z += h_i
        sx *= 0.8
        sy *= 0.8
    # crown
    if fan:
        R = max(hx, hy) * 1.15 * crown_k
        fan_crown(G, L, N, x, y, z, "x" if hx >= hy else "y", R, rng, nray=9 + 2 * int(rng.random() * 3), t=0.7)
        spire(G, N, x, y, z + R * 0.3, R * 1.5, 0.35 * min(crown_k, 3.0))
    else:
        spire(G, N, x, y, z, th * (1.4 + 0.6 * rng.random()) * crown_k, (0.45 + 0.1 * min(sx, 3)) * min(crown_k, 2.5))
    return z


def select_towers(g, cam_pose, n, min_top, margin=0.08, exclude_r=0.0, lm_box=None, max_top=380.0, pick="tall", min_cam_k=0.0):
    """Tallest city buildings (BLD) inside the frame, none standing between the camera and the landmark's screen
    rectangle (lm_box = (cx, cy, hx, hy, zmax), the landmark's world box)."""
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    g["set_cam"](cam_pose)
    bpy.context.view_layer.update()
    cam = sc.camera
    rect, ldist = None, 0.0
    if lm_box:
        cx, cy, hx, hy, zm = lm_box
        ps = [world_to_camera_view(sc, cam, Vector((cx + sx * hx, cy + sy * hy, z)))
              for sx in (-1, 1) for sy in (-1, 1) for z in (0.0, zm)]
        rect = (min(p.x for p in ps) - 0.03, max(p.x for p in ps) + 0.03, min(p.y for p in ps) - 0.03, max(p.y for p in ps) + 0.03)
        ldist = (cam.location - Vector((cx, cy, zm * 0.4))).length
    out = []
    for i, (x, y, top, hx, hy) in enumerate(g["BLD"]):
        if top < min_top or top > max_top:
            continue
        if math.hypot(x, y) < exclude_r:
            continue
        p = world_to_camera_view(sc, cam, Vector((x, y, top)))
        if not (-margin < p.x < 1 + margin and -margin < p.y < 1 + margin and p.z > 0):
            continue
        if rect:
            pb = world_to_camera_view(sc, cam, Vector((x, y, 0.0)))
            inr = rect[0] < p.x < rect[1] and pb.y < rect[3] and p.y > rect[2]
            if inr and (cam.location - Vector((x, y, top * 0.5))).length < ldist * 1.15:
                continue
        if min_cam_k and ldist and (cam.location - Vector((x, y, top * 0.5))).length < ldist * min_cam_k:
            continue
        out.append(((-top) if pick == "tall" else math.hypot(x - (lm_box[0] if lm_box else 0), y - (lm_box[1] if lm_box else 0)), x, y, i))
    out.sort()
    return [g["BLD"][i] + [i] for (_, _, _, i) in out[:n]]


# ----------------------------------------------------------------------------------------------- the entry point
def tune_fog(g, cfg):
    col = cfg.get("fog_col", (0.70, 0.66, 0.62))
    for nd in find_nodes(g["FOG_M"], "ShaderNodeVolumeScatter"):
        nd.inputs["Color"].default_value = tuple(col) + (1.0,)
        if "fog_aniso" in cfg:
            nd.inputs["Anisotropy"].default_value = cfg["fog_aniso"]


def fog_veil(g, cfg):
    """Ferriss fog massing: add a noise-banked upper veil (density `veil_k`, between z0 and z1, with a soft top) to the
    pipeline's HQ fog volume, so the towers dissolve upward into it (the base fog only thickens near the ground)."""
    k = cfg.get("veil_k", 0.006)
    if not k:
        return
    m = g["FOG_M"]
    nt = m.node_tree
    sc = find_nodes(m, "ShaderNodeVolumeScatter")[0]
    z0, z1 = cfg.get("veil_z", (90.0, 260.0))
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sp.inputs[0])
    Z = sp.outputs["Z"]
    # a smooth ramp: 0 below z0, rises to 1 at (z0+z1)/2, falls to 0 at z1 + a long tail
    up = nt.nodes.new("ShaderNodeMapRange")
    up.interpolation_type = "SMOOTHSTEP"
    up.inputs["From Min"].default_value, up.inputs["From Max"].default_value = z0, (z0 + z1) / 2
    nt.links.new(Z, up.inputs["Value"])
    dn = nt.nodes.new("ShaderNodeMapRange")
    dn.interpolation_type = "SMOOTHSTEP"
    dn.inputs["From Min"].default_value, dn.inputs["From Max"].default_value = (z0 + z1) / 2, z1
    nt.links.new(Z, dn.inputs["Value"])
    band = _math(nt, "MULTIPLY", up.outputs[0], _math(nt, "SUBTRACT", 1.0, dn.outputs[0]))
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = cfg.get("veil_scale", 0.006)
    nz.inputs["Detail"].default_value = 3.0
    mp = nt.nodes.new("ShaderNodeMapRange")
    mp.interpolation_type = "SMOOTHSTEP"
    mp.inputs["From Min"].default_value, mp.inputs["From Max"].default_value = 0.40, 0.65
    nt.links.new(nz.outputs["Fac"], mp.inputs["Value"])
    vec = nt.nodes.new("ShaderNodeVectorMath")
    vec.operation = "MULTIPLY"
    nt.links.new(geo.outputs["Position"], vec.inputs[0])
    vec.inputs[1].default_value = (1.0, 1.0, 2.2)
    nt.links.new(vec.outputs[0], nz.inputs["Vector"])
    veil = _math(nt, "MULTIPLY", _math(nt, "MULTIPLY", band, _math(nt, "ADD", 0.25, _math(nt, "MULTIPLY", mp.outputs[0], 0.75))), k)
    old = _linked_from(sc.inputs["Density"])
    if old is not None:
        nt.links.new(_math(nt, "ADD", old, veil), sc.inputs["Density"])
    else:
        nt.links.new(_math(nt, "ADD", sc.inputs["Density"].default_value, veil), sc.inputs["Density"])


def apply_hq(g, cfg):
    """Entry for the HQ pipelines (hq_scene.py globals `g`)."""
    corp = cfg.get("corp", "halcyon")
    if cfg.get("debug"):
        for k, o in g["OBJ"].items():
            if o is not None:
                zs = [v.co.z for v in o.data.vertices] or [0]
                print("[deco dbg]", k, len(o.data.polygons), "hide", o.hide_render, "z", round(min(zs), 1), round(max(zs), 1), o.data.materials[0].name if o.data.materials else None, flush=True)
    if cfg.get("off"):
        return
    import importlib
    sc = bpy.context.scene
    M = Mats()
    ctx = dict(mats=M)
    coll = bpy.data.collections.new("deco")
    sc.collection.children.link(coll)
    dh = CORP_HUES.get(corp, ((0.43, 0.16, 1.0), (1.0, 0.45, 0.06)))
    cfg.setdefault("hue", dh[0])
    cfg.setdefault("hue2", dh[1])
    hue = tuple(cfg["hue"])
    nk = cfg.get("neon_k", 2.5)
    ctx["coll"] = coll
    ctx["hue"] = hue
    ctx["lac"] = DAcc("deco_lacquer", M.lacquer, coll)
    ctx["gold"] = DAcc("deco_gold", M.gold, coll)
    ctx["brass"] = DAcc("deco_brass", M.brass, coll)
    ctx["neon"] = DAcc("deco_neon", M.neon(hue, nk), coll)
    ctx["neon2"] = DAcc("deco_neon2", M.neon(tuple(cfg.get("hue2", (1.0, 0.45, 0.06))), nk * 0.8), coll)
    ctx["gneon"] = DAcc("deco_goldneon", M.neon((1.0, 0.62, 0.20), nk * 0.7), coll)
    mod = importlib.import_module("deco_corp_" + corp)
    mod.restyle(g, cfg, ctx)
    for k in ("lac", "gold", "brass", "neon", "neon2", "gneon"):
        ctx[k].build()
    print("[deco] corp", corp, "objects", {k: len(ctx[k].f) for k in ("lac", "gold", "brass", "neon", "neon2", "gneon")}, flush=True)


def hq_common(g, cfg, ctx):
    """Everything the four HQ panels share: materials, signs, fog, tower massing, floodlights."""
    M = ctx["mats"]
    rng = random.Random(cfg.get("seed", 20261020))
    lacquer_facade(g["M_CITY"], **dict(dict(win_boost=cfg.get("win_boost", 1.8)), **cfg.get("facade", {})))
    lacquer_panels(g["M_CIVIC"])
    for k in ("M_METAL", "M_CMETAL"):
        if k in g:
            brass_metal(g[k])
    OBJ = g["OBJ"]
    # the base city's colour signs / billboards are signs-as-light: hidden; its crown neon recoloured corp hue / gold
    if OBJ.get("city_sign") is not None:
        OBJ["city_sign"].hide_render = True
    hue, hue2 = ctx["hue"], tuple(cfg.get("hue2", (1.0, 0.45, 0.06)))
    r2 = random.Random(5)

    def cneon(c):
        t = r2.random()
        base = hue if t < 0.55 else (1.0, 0.62, 0.2)
        return tuple(x * 1.0 for x in base)
    if OBJ.get("city_neon") is not None and cfg.get("hide_city_neon", True):
        OBJ["city_neon"].hide_render = True
    else:
        recolor_attr(OBJ.get("city_neon"), cneon)
    tune_fog(g, cfg)
    fog_veil(g, cfg)
    fr = g["JOB"]["frames"][0]
    towers = select_towers(g, fr["pose"], cfg.get("n_towers", 110), cfg.get("min_top", 40.0), exclude_r=cfg.get("exclude_r", 0.0), lm_box=cfg.get("lm_box"), max_top=cfg.get("max_top", 380.0), pick=cfg.get("pick", "tall"), min_cam_k=cfg.get("min_cam_k", 0.8))
    import statistics
    print("[deco] BLD", len(g["BLD"]), "tops p50/p90/max", statistics.median(b[2] for b in g["BLD"]), sorted(b[2] for b in g["BLD"])[int(0.9 * len(g["BLD"]))], max(b[2] for b in g["BLD"]), "selected", [(round(t[0]), round(t[1]), round(t[2]), round(t[3], 1)) for t in towers[:40]], flush=True)
    nfan = cfg.get("n_fans", 10)
    for k, (x, y, top, hx, hy, bi) in enumerate(towers):
        rr = random.Random(1000 + bi)
        tiers = 3 + (1 if top > 90 else 0) + (1 if k < 8 else 0)
        tower_deco(ctx, x, y, top, hx, hy, rr, tiers, k < nfan and rr.random() < 0.9, k)
    ctx["towers"] = towers
    # floodlights from the base: warm gold spots at the foot of the tallest towers, aimed up the facade
    add = g["add_light"]
    for k, (x, y, top, hx, hy, bi) in enumerate(towers[:cfg.get("n_flood", 28)]):
        rr = random.Random(2000 + bi)
        a = rr.random() * math.tau
        d = max(hx, hy) + 9.0
        loc = (x + math.cos(a) * d, y + math.sin(a) * d, 1.5)
        add("deco_flood_%d" % k, "SPOT", loc, cfg.get("flood_w", 8000.0), cfg.get("flood_col", (1.0, 0.78, 0.5)),
            aim=(x, y, top * 0.78), size=1.5, spot=34.0, blend=0.55, group="deco", shadow=False)
    # the fog glow lights (media only): neutral warm instead of the districts' colours, so the fog reads as charcoal / smoke
    for ob, e0, grp in g["LIGHTS"]:
        if ob.name.startswith(("cityglow_", "bankglow_")):
            ob.data.color = cfg.get("glow_col", (1.0, 0.84, 0.66))
    # warm the compound's cold floods (they keep their energies; apply_frame only rewrites the energy)
    for ob, e0, grp in g["LIGHTS"]:
        if grp in ("civic", "city", "start") and ob.data.type in ("SPOT", "POINT", "AREA"):
            c = ob.data.color
            if c[2] > c[0]:                      # cold light -> warm gold
                ob.data.color = cfg.get("warm_col", (1.0, 0.70, 0.36))
