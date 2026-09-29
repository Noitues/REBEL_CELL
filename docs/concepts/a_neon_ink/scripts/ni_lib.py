"""NEON INK shared library: hand-inked Grease Pencil (v3) strokes, planes composited
with per-plane blur, and a compositor bloom that only lights the glowing planes.

Coordinates are screen pixels (1920x1080, origin top-left). Every plane is its own
collection + view layer, so the compositor can blur it (fog, tilt-shift, receding
backdrops) and decide whether it feeds the bloom (marker and stickers never do).

Run through Blender 5.2:  blender -b --factory-startup --python still_xx.py -- <out.png>
"""
import bpy, math, random, os, sys
from mathutils import Matrix

W, H = 1920, 1080
U = 100.0  # pixels per world unit (ortho scale 19.2)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
FONT_MONO = os.path.join(REPO, "assets", "fonts", "ShareTechMono-Regular.ttf")
FONT_ANTON = os.path.join(REPO, "assets", "fonts", "Anton-Regular.ttf")
FONT_PLEX = os.path.join(REPO, "assets", "fonts", "IBMPlexSansCondensed-Medium.ttf")

# ---------------------------------------------------------------- palette
PAL = {
    "void": "#04050A", "wash": "#0A0E1A", "slate": "#10162A", "slate2": "#18203A",
    "pink": "#FF3DA8", "pink_hot": "#FF7AC6", "cyan": "#5CE1FF", "cyan_dim": "#2A7FA0",
    "acid": "#D4FF00", "violet": "#B04DFF", "harm": "#FF4433", "gain": "#7BE07B",
    "amber": "#FFB000", "white": "#F2F6FF", "paper": "#F2EEE4", "paper2": "#E9E4D6",
    "ink": "#111111", "note_yellow": "#F2DC7A", "note_pink": "#F4C3CF",
    "desat": "#35506A", "desat2": "#24364A", "halcyon": "#8C7BFF", "gold": "#FFD24D",
    "orange": "#FF7A1A", "police_red": "#FF2A3A", "police_blue": "#3A6BFF",
}


def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def col(h, a=1.0):
    h = PAL.get(h, h).lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return (srgb_to_lin(r), srgb_to_lin(g), srgb_to_lin(b), a)


def mix_hex(a, b, t):
    a = PAL.get(a, a).lstrip("#"); b = PAL.get(b, b).lstrip("#")
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]; cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join("%02X" % int(round(x + (y - x) * t)) for x, y in zip(ca, cb))


def to_world(x, y):
    return (x / U - W / U / 2, 0.0, H / U / 2 - y / U)


# ---------------------------------------------------------------- scene
def reset_scene(samples=16):
    sc = bpy.context.scene
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    try:
        sc.eevee.taa_render_samples = samples
    except Exception:
        pass
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    cam = bpy.data.cameras.new("cam"); cam.type = "ORTHO"; cam.ortho_scale = W / U
    cam.clip_start = 0.1; cam.clip_end = 100
    co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    co.location = (0, -20, 0); co.rotation_euler = (math.pi / 2, 0, 0)
    return sc


_MATS = {}


def gp_material(stroke_hex, fill_hex=None):
    key = (stroke_hex, fill_hex)
    if key in _MATS:
        return _MATS[key]
    m = bpy.data.materials.new("ni_%s_%s" % (stroke_hex, fill_hex))
    bpy.data.materials.create_gpencil_data(m)
    g = m.grease_pencil
    g.color = col(stroke_hex)
    g.show_stroke = True
    if fill_hex:
        g.show_fill = True
        g.fill_color = col(fill_hex)
    _MATS[key] = m
    return m


class Plane:
    """One compositing plane: a GP object (layers bottom->top) plus optional mesh text."""

    def __init__(self, name, layers=("ink",), blur=0.0, glow=True, opacity=1.0, blend=None):
        self.name = name; self.blur = blur; self.glow = glow; self.opacity = opacity
        self.layer_order = list(layers); self.blend = blend or {}
        self.buf = {l: [] for l in self.layer_order}
        self.coll = bpy.data.collections.new("C_" + name)
        bpy.context.scene.collection.children.link(self.coll)
        self.gp = bpy.data.grease_pencils.new("G_" + name)
        self.obj = bpy.data.objects.new("O_" + name, self.gp)
        self.coll.objects.link(self.obj)
        self.mat_index = {}
        self.fill_counter = 1
        self.texts = 0
        self.tcoll = None

    def _mi(self, stroke_hex, fill_hex):
        key = (stroke_hex, fill_hex)
        if key not in self.mat_index:
            self.gp.materials.append(gp_material(stroke_hex, fill_hex))
            self.mat_index[key] = len(self.gp.materials) - 1
        return self.mat_index[key]

    def add(self, layer, pts, radii, ops, color, fill=None, fill_op=1.0, cyclic=False, hide_stroke=False):
        if len(pts) < 2:
            return
        if layer not in self.buf:
            self.buf[layer] = []; self.layer_order.append(layer)
        self.buf[layer].append(dict(pts=pts, rad=radii, op=ops, mi=self._mi(color, fill),
                                    fill=fill is not None, fill_op=fill_op, cyclic=cyclic, hide=hide_stroke))

    def text(self, s, x, y, size, color, font=FONT_MONO, align="LEFT", rot=0.0, strength=1.0,
             alpha=1.0, spacing=1.0, emissive=True, valign="BASELINE"):
        """Mesh text (legible UI type). x,y = pixel anchor; size = cap height-ish in px."""
        cu = bpy.data.curves.new("T_%s_%d" % (self.name, self.texts), "FONT")
        self.texts += 1
        cu.body = s
        try:
            cu.font = bpy.data.fonts.load(font, check_existing=True)
        except Exception:
            pass
        cu.size = size / U
        cu.space_character = spacing
        cu.align_x = {"LEFT": "LEFT", "CENTER": "CENTER", "RIGHT": "RIGHT"}[align]
        cu.align_y = {"BASELINE": "BOTTOM_BASELINE", "CENTER": "CENTER", "TOP": "TOP"}[valign]
        ob = bpy.data.objects.new(cu.name, cu)
        if self.tcoll is None:
            self.tcoll = bpy.data.collections.new("T_" + self.name)
            bpy.context.scene.collection.children.link(self.tcoll)
        self.tcoll.objects.link(ob)
        wx, _, wz = to_world(x, y)
        ob.matrix_world = Matrix.Translation((wx, -1.0, wz)) @ Matrix.Rotation(rot, 4, "Y") @ Matrix.Rotation(math.pi / 2, 4, "X")
        m = bpy.data.materials.new(cu.name + "_m")
        m.use_nodes = True
        nt = m.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = col(color)
        em.inputs["Strength"].default_value = strength
        if alpha < 1.0:
            tr = nt.nodes.new("ShaderNodeBsdfTransparent")
            mx = nt.nodes.new("ShaderNodeMixShader")
            mx.inputs[0].default_value = alpha
            nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
            nt.links.new(mx.outputs[0], out.inputs["Surface"])
            try:
                m.surface_render_method = "BLENDED"
            except Exception:
                pass
        else:
            nt.links.new(em.outputs[0], out.inputs["Surface"])
        cu.materials.append(m)
        return ob

    def flush(self):
        for lname in self.layer_order:
            strokes = self.buf.get(lname) or []
            if not strokes:
                continue
            L = self.gp.layers.new(lname)
            L.use_lights = False
            if lname in self.blend:
                try:
                    L.blend_mode = self.blend[lname]
                except Exception as e:
                    print("blend fail", e)
            D = L.frames.new(1).drawing
            D.add_strokes([len(s["pts"]) for s in strokes])

            def attr(name, typ, dom):
                a = D.attributes.get(name)
                if a is None:
                    a = D.attributes.new(name, typ, dom)
                return a
            pos, rad, op = [], [], []
            for s in strokes:
                for (x, y), r, o in zip(s["pts"], s["rad"], s["op"]):
                    pos.extend(to_world(x, y)); rad.append(r / U); op.append(o)
            attr("position", "FLOAT_VECTOR", "POINT").data.foreach_set("vector", pos)
            attr("radius", "FLOAT", "POINT").data.foreach_set("value", rad)
            attr("opacity", "FLOAT", "POINT").data.foreach_set("value", op)
            attr("material_index", "INT", "CURVE").data.foreach_set("value", [s["mi"] for s in strokes])
            attr("cyclic", "BOOLEAN", "CURVE").data.foreach_set("value", [s["cyclic"] for s in strokes])
            fid = []
            for s in strokes:
                if s["fill"]:
                    fid.append(self.fill_counter); self.fill_counter += 1
                else:
                    fid.append(0)
            attr("fill_id", "INT", "CURVE").data.foreach_set("value", fid)
            attr("hide_stroke", "BOOLEAN", "CURVE").data.foreach_set("value", [s["hide"] for s in strokes])
            attr("fill_opacity", "FLOAT", "CURVE").data.foreach_set("value", [s["fill_op"] for s in strokes])
            D.tag_positions_changed()


# ---------------------------------------------------------------- the hand
class Hand:
    """Deterministic 'hand' that turns clean geometry into inked strokes."""

    def __init__(self, seed):
        self.r = random.Random(seed)

    def wobble_fn(self, amp):
        ph = [self.r.uniform(0, 6.283) for _ in range(3)]
        fr = [self.r.uniform(0.004, 0.009), self.r.uniform(0.015, 0.03), self.r.uniform(0.05, 0.09)]
        am = [amp, amp * 0.45, amp * 0.18]
        return lambda d: sum(a * math.sin(f * d + p) for a, f, p in zip(am, fr, ph))


def densify(pts, step=6.0, closed=False):
    out = []
    seq = list(pts) + ([pts[0]] if closed else [])
    for i in range(len(seq) - 1):
        (x0, y0), (x1, y1) = seq[i], seq[i + 1]
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for k in range(n):
            t = k / n
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    if not closed:
        out.append(seq[-1])
    return out


def catmull(pts, n=8, closed=False):
    if len(pts) < 3:
        return list(pts)
    P = list(pts)
    out = []
    m = len(P)
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0 = P[(i - 1) % m] if closed else P[max(i - 1, 0)]
        p1 = P[i]; p2 = P[(i + 1) % m]
        p3 = P[(i + 2) % m] if closed else P[min(i + 2, m - 1)]
        for k in range(n):
            t = k / n; t2 = t * t; t3 = t2 * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    if not closed:
        out.append(P[-1])
    return out


def ink(pl, layer, pts, color, w=2.0, op=1.0, hand=None, jit=1.0, closed=False, taper=0.35,
        overshoot=0.0, fill=None, fill_op=1.0, passes=1, smooth=False, step=6.0, hide_stroke=False,
        w_profile=None):
    """Hand-ink a polyline. w = stroke width in px. passes>1 re-traces for a sketchy look."""
    if len(pts) < 2:
        return
    pts = [tuple(p) for p in pts]
    if smooth:
        pts = catmull(pts, 8, closed)
    if overshoot and not closed:
        (x0, y0), (x1, y1) = pts[0], pts[1]
        d = math.hypot(x1 - x0, y1 - y0) or 1
        pts[0] = (x0 - (x1 - x0) / d * overshoot, y0 - (y1 - y0) / d * overshoot)
        (x0, y0), (x1, y1) = pts[-1], pts[-2]
        d = math.hypot(x1 - x0, y1 - y0) or 1
        pts[-1] = (x0 - (x1 - x0) / d * overshoot, y0 - (y1 - y0) / d * overshoot)
    base = densify(pts, step, closed)
    if closed and len(base) > 2:
        pass
    for p in range(passes):
        wob = hand.wobble_fn(jit * (1 + 0.6 * p)) if hand and jit > 0 else (lambda d: 0.0)
        out = []; rad = []; ops = []
        dist = 0.0
        n = len(base)
        for i, (x, y) in enumerate(base):
            if i > 0:
                dist += math.hypot(x - base[i - 1][0], y - base[i - 1][1])
            a = base[max(i - 1, 0)]; b = base[min(i + 1, n - 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]; dl = math.hypot(dx, dy) or 1
            nx, ny = -dy / dl, dx / dl
            o = wob(dist + p * 37.0)
            out.append((x + nx * o, y + ny * o))
            t = i / max(n - 1, 1)
            if w_profile:
                pr = w_profile(t)
            elif closed or taper <= 0:
                pr = 1.0
            else:
                pr = min(1.0, (t / 0.12) ** 0.6 if t < 0.12 else 1.0, ((1 - t) / 0.18) ** 0.6 if t > 0.82 else 1.0)
                pr = taper + (1 - taper) * pr
            ww = w * (1.0 if p == 0 else 0.55)
            rad.append(max(ww * 0.5 * pr, 0.25))
            ops.append(op * (1.0 if p == 0 else 0.55))
        pl.add(layer, out, rad, ops, color, fill=fill if p == 0 else None, fill_op=fill_op,
               cyclic=closed, hide_stroke=hide_stroke if p == 0 else False)


def fill_poly(pl, layer, pts, color, op=1.0, outline=None, w=1.5, hand=None, jit=0.0, line_op=1.0):
    """A fill (optionally with an inked outline in another colour)."""
    pts = [tuple(p) for p in pts]
    pl.add(layer, pts, [0.3] * len(pts), [1.0] * len(pts), color, fill=color, fill_op=op,
           cyclic=True, hide_stroke=True)
    if outline:
        ink(pl, layer, pts, outline, w, line_op, hand, jit, closed=True)


def ellipse(cx, cy, rx, ry, n=64, a0=0.0, a1=2 * math.pi, rot=0.0):
    out = []
    for i in range(n + 1):
        t = a0 + (a1 - a0) * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return out


def rect(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def rot_pts(pts, cx, cy, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def sketch_rect(pl, layer, x, y, w, h, color, lw=2, hand=None, over=6, op=1.0, jit=0.8):
    """Rectangle drawn as four overshooting strokes (concept-art corners)."""
    P = rect(x, y, w, h)
    for i in range(4):
        ink(pl, layer, [P[i], P[(i + 1) % 4]], color, lw, op, hand, jit, overshoot=over, taper=0.5)


def glow_halo(pl, layer, pts, color, w, op=0.18, closed=False):
    """Wide low-opacity stroke under a neon line: the light it throws onto neighbours."""
    ink(pl, layer, pts, color, w, op, None, 0, closed=closed, taper=0.0)


# ---------------------------------------------------------------- marker alphabet
# Single-stroke hand letters on a 0..1 box (y up). Each letter: list of strokes.
_E = [[(0.72, 1), (0.12, 1), (0.1, 0.02), (0.74, 0)], [(0.1, 0.52), (0.58, 0.54)]]
GLYPHS = {
    "S": [[(0.78, 0.86), (0.52, 1.0), (0.2, 0.9), (0.14, 0.66), (0.45, 0.52), (0.78, 0.38), (0.78, 0.12), (0.46, 0.0), (0.08, 0.14)]],
    "E": _E,
    "N": [[(0.1, 0.0), (0.12, 1.0), (0.72, 0.02), (0.76, 1.02)]],
    "D": [[(0.12, 0.0), (0.1, 1.0), (0.46, 0.96), (0.74, 0.74), (0.8, 0.44), (0.66, 0.14), (0.4, 0.02), (0.12, 0.0)]],
    "I": [[(0.22, 1.02), (0.2, 0.0)]],
    "T": [[(0.0, 0.98), (0.82, 1.02)], [(0.42, 1.0), (0.4, 0.0)]],
    "L": [[(0.12, 1.02), (0.1, 0.0), (0.7, 0.02)]],
    "A": [[(0.04, 0.0), (0.4, 1.02), (0.78, 0.0)], [(0.18, 0.38), (0.64, 0.4)]],
    "V": [[(0.02, 1.02), (0.4, 0.0), (0.78, 1.02)]],
    "J": [[(0.72, 1.02), (0.7, 0.26), (0.54, 0.02), (0.28, 0.0), (0.08, 0.2)]],
    "C": [[(0.8, 0.82), (0.56, 1.0), (0.24, 0.94), (0.08, 0.6), (0.1, 0.26), (0.34, 0.01), (0.62, 0.02), (0.82, 0.2)]],
    "K": [[(0.12, 1.02), (0.1, 0.0)], [(0.74, 1.02), (0.14, 0.44), (0.78, 0.0)]],
    "O": [[(0.44, 1.0), (0.12, 0.84), (0.06, 0.46), (0.2, 0.08), (0.48, 0.0), (0.74, 0.14), (0.82, 0.54), (0.68, 0.9), (0.4, 1.0), (0.3, 0.96)]],
    "U": [[(0.1, 1.02), (0.1, 0.3), (0.24, 0.04), (0.48, 0.0), (0.7, 0.18), (0.76, 1.02)]],
    "H": [[(0.1, 1.02), (0.1, 0.0)], [(0.74, 1.02), (0.72, 0.0)], [(0.06, 0.5), (0.8, 0.54)]],
    "R": [[(0.1, 0.0), (0.12, 1.0), (0.56, 0.98), (0.76, 0.8), (0.7, 0.56), (0.44, 0.48), (0.12, 0.5)], [(0.4, 0.5), (0.8, 0.0)]],
    "P": [[(0.1, 0.0), (0.12, 1.0), (0.56, 1.0), (0.76, 0.84), (0.72, 0.6), (0.48, 0.5), (0.12, 0.5)]],
    "G": [[(0.8, 0.82), (0.56, 1.0), (0.24, 0.94), (0.08, 0.6), (0.1, 0.26), (0.34, 0.01), (0.62, 0.02), (0.82, 0.22), (0.82, 0.46), (0.5, 0.46)]],
    "M": [[(0.04, 0.0), (0.1, 1.02), (0.44, 0.36), (0.78, 1.02), (0.84, 0.0)]],
    "X": [[(0.04, 1.02), (0.76, 0.0)], [(0.76, 1.02), (0.04, 0.0)]],
    "Y": [[(0.02, 1.02), (0.4, 0.5), (0.78, 1.02)], [(0.4, 0.5), (0.38, 0.0)]],
    "F": [[(0.72, 1.0), (0.12, 1.0), (0.1, 0.0)], [(0.1, 0.52), (0.56, 0.54)]],
    "B": [[(0.1, 0.0), (0.12, 1.0), (0.5, 0.98), (0.68, 0.8), (0.56, 0.56), (0.12, 0.52)], [(0.48, 0.54), (0.76, 0.36), (0.7, 0.1), (0.44, 0.0), (0.1, 0.0)]],
    "!": [[(0.22, 1.02), (0.2, 0.3)], [(0.2, 0.08), (0.21, 0.0)]],
    " ": [],
}
ADV = {"I": 0.5, " ": 0.45, "!": 0.45, "M": 1.0, "O": 0.92, "D": 0.9, "C": 0.9, "G": 0.92}


def marker_word_strokes(text, x, y, h, slant=0.18, hand=None, kern=0.12, jit=0.035):
    """Return list of (letter_index, stroke_points) in pixels. x,y = baseline-left."""
    r = hand.r if hand else random.Random(1)
    out = []
    cx = x
    for li, ch in enumerate(text):
        g = GLYPHS.get(ch, [])
        sc = h * r.uniform(0.94, 1.06)
        dy = r.uniform(-0.04, 0.04) * h
        lrot = r.uniform(-0.05, 0.05)
        for s in g:
            pts = []
            for (u, v) in s:
                u2 = u + r.uniform(-jit, jit); v2 = v + r.uniform(-jit, jit)
                px = cx + u2 * sc * 0.82 + v2 * sc * slant
                py = y - v2 * sc + dy
                pts.append((px, py))
            pts = rot_pts(pts, cx + sc * 0.4, y - sc * 0.5, lrot)
            out.append((li, pts))
        cx += (ADV.get(ch, 0.86) + kern) * h * 0.82
    return out, cx


def marker_width(text, h, kern=0.12):
    return sum((ADV.get(ch, 0.86) + kern) * h * 0.82 for ch in text)


def marker_profile(t):
    # felt marker: blunt start blob, steady body, dry flick at the end
    if t < 0.06:
        return 1.08
    if t > 0.9:
        return max(0.55, 1 - (t - 0.9) * 4.5)
    return 0.96 + 0.06 * math.sin(t * 9)


def drip(pl, layer, x, y, length, w, color, op=1.0, bulb=1.25, hand=None, taper_top=True):
    """A drip hanging from (x,y): a thinning run plus a heavy bead at its end."""
    r = hand.r if hand else random.Random(3)
    pts = []
    n = max(3, int(length / 6))
    for i in range(n + 1):
        t = i / n
        pts.append((x + math.sin(t * 3.0 + r.uniform(0, 1)) * 1.2, y + length * t))
    prof = lambda t: (0.75 - 0.3 * t) if t < 0.85 else 0.6
    ink(pl, layer, pts, color, w, op, None, 0, w_profile=prof)
    bx, by = pts[-1]
    fill_poly(pl, layer, ellipse(bx, by + w * 0.15, w * 0.5 * bulb, w * 0.62 * bulb, 18), color, op)


def neon_line(pl, layer, pts, color, w=4, hand=None, jit=0.6, core=True, halo=True, closed=False,
              halo_layer=None, smooth=False, op=1.0):
    """Neon tube: wide halo, coloured body, near-white core."""
    if halo:
        ink(pl, halo_layer or layer, pts, color, w * 4.5, 0.12 * op, None, 0, closed=closed, taper=0, smooth=smooth)
    ink(pl, layer, pts, color, w, op, hand, jit, closed=closed, taper=0.8, smooth=smooth)
    if core:
        ink(pl, layer, pts, mix_hex(color, "#FFFFFF", 0.75), max(1.0, w * 0.35), op, hand, jit * 0.3,
            closed=closed, taper=0.6, smooth=smooth)


# ---------------------------------------------------------------- scribble text (illegible)
def scribble_text(pl, layer, x, y, w, h, color, hand, op=1.0, lw=1.2, lines=1):
    r = hand.r
    for li in range(lines):
        yy = y + li * h * 1.5
        cx = x
        while cx < x + w:
            gw = r.uniform(0.35, 0.8) * h
            if cx + gw > x + w:
                break
            k = r.randint(0, 4)
            if k == 0:
                pts = [(cx, yy + h), (cx + gw * 0.5, yy), (cx + gw, yy + h)]
            elif k == 1:
                pts = [(cx, yy), (cx, yy + h), (cx + gw, yy + h * 0.5), (cx, yy + h * 0.5)]
            elif k == 2:
                pts = ellipse(cx + gw / 2, yy + h / 2, gw / 2, h / 2, 10)
            elif k == 3:
                pts = [(cx + gw, yy), (cx, yy), (cx, yy + h), (cx + gw, yy + h)]
            else:
                pts = [(cx, yy), (cx + gw, yy + h), (cx + gw, yy), (cx, yy + h)]
            ink(pl, layer, pts, color, lw, op, None, 0, taper=0.9)
            cx += gw + h * 0.3
            if r.random() < 0.18:
                cx += h * 0.6


# ---------------------------------------------------------------- compositor
def build_compositor(sc, planes, bg_hex="#04050A", bloom=(0.12, 0.9, 0.82), chroma=0.0,
                     post_bloom_planes=None):
    """Stack planes (bottom->top). Glow planes are bloomed together; non-glow planes are
    laid over the bloom afterwards (marker + stickers never light their neighbours)."""
    # view layers
    base_vl = sc.view_layers[0]
    vls = {}
    for p in planes:
        for key, cl in ((p.name, p.coll), (p.name + "__text", p.tcoll)):
            if cl is None:
                continue
            vl = sc.view_layers.new("VL_" + key)
            for lc in vl.layer_collection.children:
                lc.exclude = (lc.collection != cl)
            vls[key] = vl
    sc.view_layers.remove(base_vl)

    ng = bpy.data.node_groups.new("NI_comp", "CompositorNodeTree")
    sc.compositing_node_group = ng
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    out = ng.nodes.new("NodeGroupOutput")
    bgn = ng.nodes.new("CompositorNodeRGB")
    try:
        bgn.outputs[0].default_value = col(bg_hex)
    except Exception:
        bgn.value = col(bg_hex)
    cur = bgn.outputs[0]

    def layer_img(p, key):
        rl = ng.nodes.new("CompositorNodeRLayers"); rl.layer = vls[key].name
        img = rl.outputs["Image"]
        if p.blur > 0:
            bl = ng.nodes.new("CompositorNodeBlur")
            bl.inputs["Size"].default_value = (p.blur, p.blur)
            try:
                bl.inputs["Type"].default_value = "Gaussian"
            except Exception:
                pass
            ng.links.new(img, bl.inputs["Image"]); img = bl.outputs["Image"]
        return img

    def over(cur, img, fac):
        ao = ng.nodes.new("CompositorNodeAlphaOver")
        ao.inputs["Factor"].default_value = fac
        ng.links.new(cur, ao.inputs["Background"]); ng.links.new(img, ao.inputs["Foreground"])
        return ao.outputs["Image"]

    glow_planes = [p for p in planes if p.glow]
    top_planes = [p for p in planes if not p.glow]
    def stack(cur, p):
        cur = over(cur, layer_img(p, p.name), p.opacity)
        if p.tcoll is not None:
            cur = over(cur, layer_img(p, p.name + "__text"), p.opacity)
        return cur
    for p in glow_planes:
        cur = stack(cur, p)
    gl = ng.nodes.new("CompositorNodeGlare")
    gl.inputs["Type"].default_value = "Bloom"
    gl.inputs["Threshold"].default_value = bloom[0]
    gl.inputs["Strength"].default_value = bloom[1]
    gl.inputs["Size"].default_value = bloom[2]
    try:
        gl.inputs["Quality"].default_value = "High"
    except Exception:
        pass
    ng.links.new(cur, gl.inputs["Image"]); cur = gl.outputs["Image"]
    for p in top_planes:
        cur = stack(cur, p)
    if chroma > 0:
        sep = ng.nodes.new("CompositorNodeSeparateColor")
        ng.links.new(cur, sep.inputs[0])
        comb = ng.nodes.new("CompositorNodeCombineColor")
        tr = ng.nodes.new("CompositorNodeTranslate"); tb = ng.nodes.new("CompositorNodeTranslate")
        tr.inputs["X"].default_value = chroma; tb.inputs["X"].default_value = -chroma
        ng.links.new(sep.outputs[0], tr.inputs[0]); ng.links.new(tr.outputs[0], comb.inputs[0])
        ng.links.new(sep.outputs[1], comb.inputs[1])
        ng.links.new(sep.outputs[2], tb.inputs[0]); ng.links.new(tb.outputs[0], comb.inputs[2])
        cur = comb.outputs[0]
    ng.links.new(cur, out.inputs[0])


def render(sc, planes, path, **kw):
    for p in planes:
        p.flush()
    build_compositor(sc, planes, **kw)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path)


def out_path(default_name):
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if argv:
        return os.path.abspath(argv[0])
    return os.path.join(HERE, "..", "stills", default_name)
