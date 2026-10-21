"""Solace district concept: geometry builders and materials (Blender 5.2, run inside blender -b).

Geometry goes into per-material mesh builders (MB). Every vertex carries three point attributes the shaders read:
  col  base colour (RGBA)      prm  (lit probability, lime weight, pink weight, building seed)      uv  (u BU along the wall, v = z BU)
"""
import math
import bpy

CEL_S = 1.0             # cel window emission strength
DAY = False            # daylight: windows read as dark reflective glass, not lit
EMIT_K = 1.0          # night emission multiplier (round 2 night fix)
EK_SCALE = 1.0          # v5: the HQ exposure factor (HQ post exposure is ~5.8x the district's), multiplies every emission strength
Z_FLAT = False          # set by the main script: flat shading everywhere in the cel map


class MB:
    def __init__(self, name):
        self.name = name
        self.V, self.C, self.P, self.U, self.F = [], [], [], [], []

    def v(self, p, col, prm, uv=(0.0, 0.0)):
        self.V.append((float(p[0]), float(p[1]), float(p[2])))
        self.C.append(col if len(col) == 4 else (col[0], col[1], col[2], 1.0))
        self.P.append(prm)
        self.U.append((uv[0], uv[1], 0.0))
        return len(self.V) - 1

    def f(self, *idx):
        self.F.append(tuple(idx))

    def build(self, mat, smooth, coll, sc=1.0):
        """sc (v5): a uniform scale about the origin, applied to the vertices AND the (u, v) wall coordinates, so the
        district kit is a true similarity copy at HQ scale (windows scale with the buildings)."""
        if not self.F:
            return None
        me = bpy.data.meshes.new(self.name)
        if sc != 1.0:
            self.V = [(p[0] * sc, p[1] * sc, p[2] * sc) for p in self.V]
            self.U = [(u[0] * sc, u[1] * sc, u[2]) for u in self.U]
        me.from_pydata(self.V, [], self.F)
        n = len(self.V)
        a = me.attributes.new("col", "FLOAT_COLOR", "POINT")
        a.data.foreach_set("color", [c for t in self.C for c in t])
        a = me.attributes.new("prm", "FLOAT_COLOR", "POINT")
        a.data.foreach_set("color", [c for t in self.P for c in (t + (1.0,) * (4 - len(t)))[:4]])
        a = me.attributes.new("cuv", "FLOAT_VECTOR", "POINT")
        a.data.foreach_set("vector", [c for t in self.U for c in t])
        sm = bool(smooth) and not Z_FLAT
        me.polygons.foreach_set("use_smooth", [sm] * len(me.polygons))
        me.update()
        ob = bpy.data.objects.new(self.name, me)
        ob.data.materials.append(mat)
        coll.objects.link(ob)
        return ob


# ------------------------------------------------------------------ primitives
def prism(mb, poly, z0, z1, col, prm, top=True, uvs=1.0):
    """Extrude a convex CCW polygon [(x, y)]: flat side walls (uv u = wall length), optional top cap."""
    u = 0.0
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        L = math.hypot(b[0] - a[0], b[1] - a[1]) * uvs
        i0 = mb.v((a[0], a[1], z0), col, prm, (u, z0))
        i1 = mb.v((b[0], b[1], z0), col, prm, (u + L, z0))
        i2 = mb.v((b[0], b[1], z1), col, prm, (u + L, z1))
        i3 = mb.v((a[0], a[1], z1), col, prm, (u, z1))
        mb.f(i0, i1, i2, i3)
        u += L
    if top:
        idx = [mb.v((p[0], p[1], z1), col, prm, (0, 0)) for p in poly]
        for k in range(1, n - 1):
            mb.f(idx[0], idx[k], idx[k + 1])


def rect(cx, cy, hw, hd, ang=0.0):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + c * x - s * y, cy + s * x + c * y) for x, y in ((-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd))]


def box(mb, x0, y0, z0, x1, y1, z1, col, prm, top=True):
    prism(mb, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, col, prm, top)


def lathe(mb, cx, cy, profile, n, col, prm, closed=False):
    """Surface of revolution: profile [(r, z)] bottom to top; n segments, shared ring vertices (smooth capable).
    u = arc length around at the widest radius (BU), v = z."""
    R = max(p[0] for p in profile) or 1.0
    rings = []
    for (r, z) in profile:
        if r < 1e-6:
            rings.append(mb.v((cx, cy, z), col, prm, (0, z)))
        else:
            rings.append([mb.v((cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n), z), col, prm,
                               (2 * math.pi * R * k / n, z)) for k in range(n + 1)])
    for i in range(len(profile) - 1):
        a, b = rings[i], rings[i + 1]
        for k in range(n):
            if isinstance(a, int) and isinstance(b, int):
                continue
            if isinstance(a, int):
                mb.f(a, b[k + 1], b[k])
            elif isinstance(b, int):
                mb.f(a[k], a[k + 1], b)
            else:
                mb.f(a[k], a[k + 1], b[k + 1], b[k])


def cyl(mb, cx, cy, z0, z1, r, n, col, prm, cap=True):
    prof = [(r, z0), (r, z1)]
    if cap:
        prof = [(0.0, z0), (r, z0), (r, z1), (0.0, z1)]
    lathe(mb, cx, cy, prof, n, col, prm)


def dome_profile(r, z, rings=4, squash=1.0):
    return [(r * math.cos(math.pi / 2 * k / rings), z + r * squash * math.sin(math.pi / 2 * k / rings)) for k in range(rings + 1)]


def dome(mb, cx, cy, z, r, n, col, prm, rings=4, squash=1.0):
    lathe(mb, cx, cy, dome_profile(r, z, rings, squash), n, col, prm)


def sphere(mb, cx, cy, cz, r, n, col, prm, rings=None):
    rings = rings or max(3, n // 2)
    prof = [(r * math.sin(math.pi * k / rings), cz - r * math.cos(math.pi * k / rings)) for k in range(rings + 1)]
    prof[0] = (0.0, prof[0][1])
    prof[-1] = (0.0, prof[-1][1])
    lathe(mb, cx, cy, prof, n, col, prm)


def torus(mb, cx, cy, z, R, rt, n, sides, col, prm):
    prof = [(R + rt * math.cos(2 * math.pi * k / sides), z + rt * math.sin(2 * math.pi * k / sides)) for k in range(sides + 1)]
    lathe(mb, cx, cy, prof, n, col, prm)


def sweep(mb, pts, nrms, rt, sides, col, prm, uvscale=1.0):
    """Tube along pts with given radial normal frame per point (unit vectors); uv u around, v along."""
    rings = []
    L = 0.0
    for i, c in enumerate(pts):
        if i > 0:
            L += math.dist(c, pts[i - 1])
        if i == 0:
            T = _unit(_sub(pts[1], pts[0]))
        elif i == len(pts) - 1:
            T = _unit(_sub(pts[-1], pts[-2]))
        else:
            T = _unit(_sub(pts[i + 1], pts[i - 1]))
        nr = nrms[i]
        nr = _unit(_sub(nr, _mul(T, _dot(nr, T))))
        bn = _unit(_cross(T, nr))
        circ = 2 * math.pi * rt
        rings.append([mb.v(tuple(c[j] + (nr[j] * math.cos(2 * math.pi * m / sides) + bn[j] * math.sin(2 * math.pi * m / sides)) * rt
                                 for j in range(3)), col, prm, (circ * m / sides * uvscale, L * uvscale)) for m in range(sides + 1)])
    for i in range(len(pts) - 1):
        for m in range(sides):
            mb.f(rings[i][m], rings[i][m + 1], rings[i + 1][m + 1], rings[i + 1][m])


def seg_tube(mb, a, b, rt, sides, col, prm, up=(0, 0, 1)):
    T = _unit(_sub(b, a))
    nr = _cross(T, up)
    if _len(nr) < 1e-4:
        nr = _cross(T, (1, 0, 0))
    nr = _unit(nr)
    sweep(mb, [a, b], [nr, nr], rt, sides, col, prm)


def flat_poly(mb, pts, col, prm):
    idx = [mb.v(p, col, prm, (0, 0)) for p in pts]
    for k in range(1, len(idx) - 1):
        mb.f(idx[0], idx[k], idx[k + 1])


def strip(mb, a, b, w, z, col, prm):
    """A flat ribbon from a to b (xy), half-width w, at height z (faces up)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L * w, dx / L * w
    flat_poly(mb, [(a[0] - nx, a[1] - ny, z), (b[0] - nx, b[1] - ny, z), (b[0] + nx, b[1] + ny, z), (a[0] + nx, a[1] + ny, z)], col, prm)


def disc(mb, cx, cy, z, r, n, col, prm):
    flat_poly(mb, [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n), z) for k in range(n)], col, prm)


def cross_shape(mb, cx, cy, cz, size, th, ang, col, prm, depth=0.5):
    """A standing plus sign (vertical plane, facing direction ang), as a thin extruded slab: two crossing bars."""
    ca, sa = math.cos(ang), math.sin(ang)
    # plane axis (horizontal) = (-sa, ca), vertical = z
    def P(h, v, d):
        return (cx - sa * h + ca * d, cy + ca * h + sa * d, cz + v)
    hs, ts = size / 2, th / 2
    for (h0, h1, v0, v1) in ((-hs, hs, -ts, ts), (-ts, ts, -hs, hs)):
        c = [P(h0, v0, -depth), P(h1, v0, -depth), P(h1, v1, -depth), P(h0, v1, -depth),
             P(h0, v0, depth), P(h1, v0, depth), P(h1, v1, depth), P(h0, v1, depth)]
        for q in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
            idx = [mb.v(c[i], col, prm) for i in q]
            mb.f(*idx)


# ------------------------------------------------------------------ vector helpers
def _sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def _mul(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _len(a): return math.sqrt(_dot(a, a))
def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def _unit(a):
    n = _len(a) or 1.0
    return (a[0] / n, a[1] / n, a[2] / n)


# ------------------------------------------------------------------ materials
class NB:
    """Tiny node-builder helper."""
    def __init__(self, nt):
        self.nt = nt
        self.x = 0

    def node(self, t, **kw):
        n = self.nt.nodes.new(t)
        for k, v in kw.items():
            setattr(n, k, v)
        return n

    def link(self, o, i):
        self.nt.links.new(o, i)

    def val(self, node_input, v):
        if isinstance(v, (int, float)):
            node_input.default_value = v
        else:
            self.link(v, node_input)

    def m(self, op, a, b=None, c=None, clamp=False):
        n = self.node("ShaderNodeMath", operation=op)
        n.use_clamp = clamp
        self.val(n.inputs[0], a)
        if b is not None:
            self.val(n.inputs[1], b)
        if c is not None:
            self.val(n.inputs[2], c)
        return n.outputs[0]

    def attr(self, name):
        return self.node("ShaderNodeAttribute", attribute_name=name, attribute_type="GEOMETRY")

    def sep(self, vec):
        n = self.node("ShaderNodeSeparateXYZ")
        self.link(vec, n.inputs[0])
        return n.outputs[0], n.outputs[1], n.outputs[2]

    def sepc(self, col):
        n = self.node("ShaderNodeSeparateColor")
        self.link(col, n.inputs[0])
        return n.outputs[0], n.outputs[1], n.outputs[2]

    def comb(self, x, y, z):
        n = self.node("ShaderNodeCombineXYZ")
        self.val(n.inputs[0], x)
        self.val(n.inputs[1], y)
        self.val(n.inputs[2], z)
        return n.outputs[0]

    def mix(self, a, b, fac):
        n = self.node("ShaderNodeMix", data_type="RGBA", blend_type="MIX")
        self.val(n.inputs[0], fac)
        if isinstance(a, tuple):
            n.inputs[6].default_value = a + (1.0,)
        else:
            self.link(a, n.inputs[6])
        if isinstance(b, tuple):
            n.inputs[7].default_value = b + (1.0,)
        else:
            self.link(b, n.inputs[7])
        return n.outputs[2]

    def mulc(self, col, f):
        n = self.node("ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY")
        n.inputs[0].default_value = 1.0
        self.link(col, n.inputs[6])
        if isinstance(f, tuple):
            n.inputs[7].default_value = f + (1.0,)
        else:
            self.link(f, n.inputs[7])
        return n.outputs[2]

    def noise(self, vec, w=None):
        n = self.node("ShaderNodeTexWhiteNoise", noise_dimensions="3D")
        self.link(vec, n.inputs[0])
        return n.outputs[0]


WARM = (1.0, 0.72, 0.38)
LIME = (0.55, 1.0, 0.22)
PINK = (1.0, 0.2, 0.55)


def _toon(nb, base_col, bands):
    """Cel shading: diffuse -> ShaderToRGB -> constant 3-stop ramp -> multiply the base colour."""
    d = nb.node("ShaderNodeBsdfDiffuse")
    d.inputs[0].default_value = (1, 1, 1, 1)
    s = nb.node("ShaderNodeShaderToRGB")
    nb.link(d.outputs[0], s.inputs[0])
    bw = nb.node("ShaderNodeRGBToBW")
    nb.link(s.outputs[0], bw.inputs[0])
    r = nb.node("ShaderNodeValToRGB")
    r.color_ramp.interpolation = "CONSTANT"
    el = r.color_ramp.elements
    el[0].position = 0.0
    tc = lambda b: (tuple(b) if isinstance(b, tuple) else (b,) * 3) + (1,)
    el[0].color = tc(bands[0])
    el[1].position = bands[3]
    el[1].color = tc(bands[1])
    e3 = el.new(bands[4])
    e3.color = tc(bands[2])
    nb.link(bw.outputs[0], r.inputs[0])
    return nb.mulc(base_col, r.outputs[0])


def make_material(name, kind, mode, **o):
    """kind: win (windowed walls), glass, neon, ground, hwin (helix oval windows).  mode: 'night' (Cycles/AAA-2) or 'map' (cel)."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    nb = NB(nt)
    out = nb.node("ShaderNodeOutputMaterial")
    cel = mode in ("map", "ink")
    if mode == "ink":
        # id / normal / depth pass for the ink lines: R = building id, G = facing, B = depth (post-detected edges)
        out_ = out
        pN = nb.attr("prm")
        sd_ = nb.m("FRACT", nb.m("MULTIPLY", pN.outputs["Alpha"], 37.17))
        g_ = nb.node("ShaderNodeNewGeometry")
        _x, _y, nz_ = nb.sep(g_.outputs["Normal"])
        cdn = nb.node("ShaderNodeCameraData")
        dep = nb.m("DIVIDE", cdn.outputs["View Z Depth"], 1500.0)
        col_ = nb.comb(sd_, nb.m("ADD", nb.m("MULTIPLY", nz_, 0.5), 0.5), dep)
        e_ = nb.node("ShaderNodeEmission")
        nb.link(col_, e_.inputs[0])
        e_.inputs[1].default_value = 1.0
        nb.link(e_.outputs[0], out_.inputs[0])
        return mat
    bands = o.get("bands", (0.40, 0.72, 1.0, 0.22, 0.58))
    colN = nb.attr("col")
    prmN = nb.attr("prm")
    uvN = nb.attr("cuv")
    pr, pg, pb = nb.sepc(prmN.outputs["Color"])
    pa = prmN.outputs["Alpha"]
    PW = nb.node("ShaderNodeAttribute", attribute_name="pwo", attribute_type="OBJECT").outputs["Fac"]   # v5: the HQ power cut

    if kind == "neon":
        e = nb.node("ShaderNodeEmission")
        nb.link(colN.outputs["Color"], e.inputs[0])
        e.inputs[1].default_value = o.get("strength", 6.0) * (0.35 if cel and False else 1.0)
        nb.val(e.inputs[1], nb.m("MULTIPLY", nb.m("MULTIPLY", pr, PW), o.get("strength", 6.0) * o.get("ek", EMIT_K) * EK_SCALE))
        nb.link(e.outputs[0], out.inputs[0])
        return mat

    if kind == "water":
        if cel:
            c = _toon(nb, colN.outputs["Color"], bands)
            e = nb.node("ShaderNodeEmission")
            nb.link(c, e.inputs[0])
            nb.link(e.outputs[0], out.inputs[0])
            return mat
        bsdf = nb.node("ShaderNodeBsdfPrincipled")
        nb.link(colN.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.03
        bsdf.inputs["Specular IOR Level"].default_value = 1.0
        bsdf.inputs["Coat Weight"].default_value = 0.6
        bsdf.inputs["Coat Roughness"].default_value = 0.02
        nb.link(bsdf.outputs[0], out.inputs[0])
        return mat

    if kind == "ground":
        if cel:
            c = _toon(nb, colN.outputs["Color"], bands)
            e = nb.node("ShaderNodeEmission")
            nb.link(c, e.inputs[0])
            nb.link(e.outputs[0], out.inputs[0])
            return mat
        bsdf = nb.node("ShaderNodeBsdfPrincipled")
        nb.link(colN.outputs["Color"], bsdf.inputs["Base Color"])
        nz = nb.node("ShaderNodeTexNoise", noise_dimensions="3D")
        nz.inputs["Scale"].default_value = 0.09
        nz.inputs["Detail"].default_value = 3.0
        gp = nb.node("ShaderNodeNewGeometry")
        nb.link(gp.outputs["Position"], nz.inputs["Vector"])
        # wet streets (prm.g flag): low roughness with puddle variation; dry pads rougher
        wet = nb.m("MULTIPLY", pg, 1.0)
        rough = nb.m("ADD", nb.m("MULTIPLY", nb.m("SUBTRACT", 1.0, wet), pr), nb.m("MULTIPLY", wet, nb.m("ADD", 0.07, nb.m("MULTIPLY", nz.outputs["Fac"], 0.35))))
        nb.link(rough, bsdf.inputs["Roughness"])
        bsdf.inputs["Specular IOR Level"].default_value = 0.6
        nb.link(bsdf.outputs[0], out.inputs[0])
        return mat

    if kind == "glass":
        if cel:
            c = _toon(nb, colN.outputs["Color"], bands)
            e = nb.node("ShaderNodeEmission")
            nb.link(c, e.inputs[0])
            em = nb.node("ShaderNodeEmission")
            nb.link(colN.outputs["Color"], em.inputs[0])
            nb.val(em.inputs[1], nb.m("MULTIPLY", pr, o.get("cel_strength", 0.22)))
            add = nb.node("ShaderNodeAddShader")
            nb.link(e.outputs[0], add.inputs[0])
            nb.link(em.outputs[0], add.inputs[1])
            tr = nb.node("ShaderNodeBsdfTransparent")
            mx = nb.node("ShaderNodeMixShader")
            mx.inputs[0].default_value = o.get("alpha", 0.62)
            nb.link(tr.outputs[0], mx.inputs[1])
            nb.link(add.outputs[0], mx.inputs[2])
            nb.link(mx.outputs[0], out.inputs[0])
            mat.surface_render_method = "DITHERED"
            return mat
        bsdf = nb.node("ShaderNodeBsdfPrincipled")
        nb.link(colN.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.06
        bsdf.inputs["Transmission Weight"].default_value = o.get("trans", 0.9)
        bsdf.inputs["IOR"].default_value = 1.2
        nb.link(colN.outputs["Color"], bsdf.inputs["Emission Color"])
        nb.val(bsdf.inputs["Emission Strength"], nb.m("MULTIPLY", nb.m("MULTIPLY", pr, PW), o.get("strength", 2.0) * o.get("ek", EMIT_K) * EK_SCALE))
        nb.link(bsdf.outputs[0], out.inputs[0])
        return mat

    # ---- win / hwin: surface + a procedural lit-window layer
    u, v, _z = nb.sep(uvN.outputs["Vector"])
    base = colN.outputs["Color"]
    if kind == "hwin":
        # helix oval window: faux interior (warm floor glow, dark ceiling, a mullion), uv in 0..1 across the oval
        floor = nb.m("MULTIPLY", nb.m("SUBTRACT", 1.0, nb.m("MULTIPLY", v, 1.0)), 1.0)
        grad = nb.m("ADD", 0.25, nb.m("MULTIPLY", floor, 0.9))
        mull = nb.m("SUBTRACT", 1.0, nb.m("MULTIPLY", nb.m("LESS_THAN", nb.m("ABSOLUTE", nb.m("SUBTRACT", u, 0.5)), 0.018), 0.85))
        wcol = nb.mix(nb.mix(WARM, LIME, pg), PINK, pb)
        emc = nb.mulc(wcol, nb.comb(1.0, 1.0, 1.0))
        strength = nb.m("MULTIPLY", nb.m("MULTIPLY", grad, mull), nb.m("MULTIPLY", nb.m("MULTIPLY", pr, PW), o.get("strength", 6.0) * o.get("ek", EMIT_K) * EK_SCALE))
        if cel:
            e = nb.node("ShaderNodeEmission")
            nb.link(wcol, e.inputs[0])
            nb.val(e.inputs[1], nb.m("MULTIPLY", nb.m("ADD", 0.45, nb.m("MULTIPLY", grad, 0.55)), mull))
            nb.link(e.outputs[0], out.inputs[0])
            return mat
        bsdf = nb.node("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Base Color"].default_value = (0.02, 0.04, 0.03, 1)
        bsdf.inputs["Roughness"].default_value = 0.05
        bsdf.inputs["Transmission Weight"].default_value = 0.3
        nb.link(wcol, bsdf.inputs["Emission Color"])
        nb.val(bsdf.inputs["Emission Strength"], strength)
        nb.link(bsdf.outputs[0], out.inputs[0])
        return mat

    cw, ch = o.get("cw", 3.0), o.get("ch", 3.6)
    x0, x1, y0, y1 = o.get("win", (0.2, 0.8, 0.25, 0.75))
    plain = o.get("plain", False)
    ux = nb.m("DIVIDE", u, cw)
    vy = nb.m("DIVIDE", v, ch)
    fx = nb.m("FRACT", ux)
    fy = nb.m("FRACT", vy)
    inx = nb.m("MULTIPLY", nb.m("GREATER_THAN", fx, x0), nb.m("LESS_THAN", fx, x1))
    iny = nb.m("MULTIPLY", nb.m("GREATER_THAN", fy, y0), nb.m("LESS_THAN", fy, y1))
    cell = nb.comb(nb.m("FLOOR", ux), nb.m("FLOOR", vy), nb.m("MULTIPLY", pa, 97.0))
    n1 = nb.noise(cell)
    lit = nb.m("LESS_THAN", n1, pr)
    cell2 = nb.comb(nb.m("ADD", nb.m("FLOOR", ux), 5.3), nb.m("ADD", nb.m("FLOOR", vy), 2.1), nb.m("MULTIPLY", pa, 53.0))
    n2 = nb.noise(cell2)
    isl = nb.m("LESS_THAN", n2, pg)
    isp = nb.m("MULTIPLY", nb.m("GREATER_THAN", n2, pg), nb.m("LESS_THAN", n2, nb.m("ADD", pg, pb)))
    wcol = nb.mix(nb.mix(WARM, LIME, isl), PINK, isp)
    if o.get("day", DAY) and cel:
        wcol = (0.30, 0.44, 0.66, 1.0)[:3]
        wcol = nb.mix(wcol, wcol, 0.0)
    gn = nb.node("ShaderNodeNewGeometry")
    _nx, _ny, nz = nb.sep(gn.outputs["Normal"])
    vert = nb.m("LESS_THAN", nb.m("ABSOLUTE", nz), o.get("nzmax", 0.6))
    flick = nb.m("ADD", 0.55, nb.m("MULTIPLY", n2, 0.9))
    mask = nb.m("MULTIPLY", nb.m("MULTIPLY", inx if o.get("cut_x", True) else 1.0, iny), nb.m("MULTIPLY", lit, vert))
    if plain:
        mask = 0.0
    if o.get("dbg"):
        mask = {"inx": inx, "iny": iny, "lit": lit, "vert": vert, "n1": n1, "one": 1.0, "fy": fy, "vy": vy}[o["dbg"]]
    S = o.get("strength", 5.0) * o.get("ek", EMIT_K) * EK_SCALE
    glow = o.get("glow")
    if cel:
        c = _toon(nb, base, bands)
        if glow:
            c = nb.mix(c, glow[0], glow[1])
        e = nb.node("ShaderNodeEmission")
        nb.link(c, e.inputs[0])
        ew = nb.node("ShaderNodeEmission")
        nb.link(wcol, ew.inputs[0])
        nb.val(ew.inputs[1], nb.m("MULTIPLY", mask, o.get("cel_strength", CEL_S)))
        add = nb.node("ShaderNodeAddShader")
        nb.link(e.outputs[0], add.inputs[0])
        nb.link(ew.outputs[0], add.inputs[1])
        # windows replace the toon surface rather than add to it: mix by mask
        mx = nb.node("ShaderNodeMixShader")
        nb.val(mx.inputs[0], mask)
        nb.link(e.outputs[0], mx.inputs[1])
        nb.link(ew.outputs[0], mx.inputs[2])
        ew.inputs[1].default_value = 1.0
        nb.link(mx.outputs[0], out.inputs[0])
        if o.get("alpha") is not None:
            tr = nb.node("ShaderNodeBsdfTransparent")
            m2 = nb.node("ShaderNodeMixShader")
            m2.inputs[0].default_value = o["alpha"]
            nb.link(tr.outputs[0], m2.inputs[1])
            nb.link(mx.outputs[0], m2.inputs[2])
            nb.link(m2.outputs[0], out.inputs[0])
            mat.surface_render_method = "DITHERED"
        return mat
    bsdf = nb.node("ShaderNodeBsdfPrincipled")
    if DAY and not plain:
        # daylight: the window cells are dark reflective glass (sky reflections), not lit
        wm = nb.m("MULTIPLY", mask, 1.0)
        base = nb.mix(base, (0.05, 0.12, 0.20), nb.m("MULTIPLY", wm, 0.85))
        nb.link(base, bsdf.inputs["Base Color"])
        nb.val(bsdf.inputs["Roughness"], nb.m("SUBTRACT", o.get("rough", 0.35), nb.m("MULTIPLY", wm, o.get("rough", 0.35) - 0.06)))
        nb.val(bsdf.inputs["Metallic"], nb.m("ADD", o.get("metal", 0.0), nb.m("MULTIPLY", wm, 0.5)))
    else:
        nb.link(base, bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = o.get("rough", 0.35)
        bsdf.inputs["Metallic"].default_value = o.get("metal", 0.0)
    bsdf.inputs["Specular IOR Level"].default_value = 0.6
    if o.get("coat"):
        bsdf.inputs["Coat Weight"].default_value = o["coat"]
        bsdf.inputs["Coat Roughness"].default_value = 0.05
    if glow:
        bsdf.inputs["Emission Color"].default_value = glow[0] + (1.0,)
        bsdf.inputs["Emission Strength"].default_value = glow[2] * o.get("ek", EMIT_K) * EK_SCALE
    else:
        nb.link(wcol, bsdf.inputs["Emission Color"])
        nb.val(bsdf.inputs["Emission Strength"], nb.m("MULTIPLY", nb.m("MULTIPLY", nb.m("MULTIPLY", mask, flick), PW), S))
    nb.link(bsdf.outputs[0], out.inputs[0])
    return mat
