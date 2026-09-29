"""Isometric night city for stills 02 (night) and 03 (high Heat).

Ortho iso camera, wet streets, elevated multi-level highways with traffic, flying vehicles, hologram
billboards, patchy fog volumes, the HQ tower fully in frame, and the grid net drawn on ONE plane (z = NET_Z).
Writes a depth pass and fog-patch screen positions for the tilt-shift/variable-blur post (tiltshift.py).
"""
import json, math, os, random
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from rn_lib import *  # noqa
from rn_parts import *  # noqa

NET_Z = 31.0
HQ = (-12.0, 14.0)
HQ_H = 56.0
TARGET = Vector((0, 0, 27))
ORTHO = 170.0
HWYS = [  # (axis, fixed coord, z, from, to)
    ("x", -30.0, 9.0, -110, 110),
    ("y", 24.0, 16.0, -110, 110),
    ("x", 38.0, 23.0, -110, 110),
]


class City:
    def __init__(self, heat=0.0, seed=4):
        self.heat = heat
        self.rng = random.Random(seed)
        self.ui = []        # objects excluded from tilt-shift (kept sharp)
        self.hide_depth = []  # volumes/transparent fx hidden in the depth pass
        self.fog = []       # (world centre, radius) of fog patches

    # ------------------------------------------------------------ camera
    def camera(self):
        cd = bpy.data.cameras.new("iso")
        cd.type = "ORTHO"
        cd.ortho_scale = ORTHO
        cd.clip_start = 1
        cd.clip_end = 900
        ob = bpy.data.objects.new("iso", cd)
        rot = Euler((math.radians(60), 0, math.radians(45)))
        fwd = rot.to_matrix() @ Vector((0, 0, -1))
        ob.location = TARGET - fwd * 300
        ob.rotation_euler = rot
        link(ob)
        bpy.context.scene.camera = ob
        self.cam = ob
        self.fwd = fwd
        return ob

    def cam_ui(self, x, y, z=-20.0):
        """Pixel -> camera-local point for UI parented to the ortho camera."""
        return Vector(((x / 1920 - 0.5) * ORTHO, (0.5 - y / 1080) * ORTHO * 1080 / 1920, z))

    def upx(self, px):
        return px / 1920 * ORTHO

    # ------------------------------------------------------------ city
    def under_hwy(self, x, y, w, d):
        for ax, c, z, a, b in HWYS:
            if ax == "x" and abs(y - c) < d / 2 + 4:
                return z
            if ax == "y" and abs(x - c) < w / 2 + 4:
                return z
        return None

    def build(self):
        h = self.heat
        world("#010204", 1.0)  # NB: a world volume extinguishes sun light on every surface in EEVEE; use a bounded haze box instead
        hz = box("haze_layer", (0, 0, 14), (240, 240, 28), mat_volume("haze_layer", 0.006 + 0.008 * h, "#7d8aa0"))
        self.hide_depth.append(hz)
        ee = bpy.context.scene.eevee
        ee.volumetric_start, ee.volumetric_end = 140.0, 480.0   # froxels only where the iso city is
        ee.use_volumetric_shadows = False
        sun((math.radians(-58), 0, math.radians(200)), "#8fa4c8", 5.0 - 2.0 * h, name="moon")
        sun((math.radians(50), 0, math.radians(35)), "#5a6e90", 1.5, name="bounce")  # faint cool fill on camera-facing facades
        area((0, 0, 140), (0, 0, 0), "#5a6f92", 60000 * (1 - 0.4 * h), size=260, name="sky_fill")
        wet_ground("ground", (0, 0, -0.05), (400, 400, 0.1), rough=(0.02, 0.28), scale=0.05)
        rng = self.rng
        walls = [mat_windows("w%d" % i, wall=["#2b3445", "#323c4f", "#262e3c"][i], lit=("#9fb2cc", "#d8c39a"), density=0.12 + 0.05 * i,
                             strength=1.3, scale=0.42 + 0.08 * i, seed=i * 2.7) for i in range(3)]
        roof = mat_pbr("roof", "#2a3342", 0.35, 0.2)
        m_road_line = mat_emit("roadline", "#5a6272", 0.8)
        # street lane markings (dashes) on a 16-unit grid
        for k in range(-6, 7):
            c = k * 16 - 8
            for t in range(-100, 100, 5):
                box("dash", (c, t, 0.02), (0.18, 2.0, 0.02), m_road_line)
                box("dash", (t, c, 0.02), (2.0, 0.18, 0.02), m_road_line)
        self.blocks = []
        for bx in range(-6, 6):
            for by in range(-6, 6):
                cx, cy = bx * 16, by * 16
                if abs(cx - HQ[0]) < 12 and abs(cy - HQ[1]) < 12:
                    continue
                n = rng.choice((1, 1, 2, 2, 3, 4))
                subs = [(0, 0, 11, 11)] if n == 1 else [(-3, 0, 5, 11), (3, 0, 5, 11)] if n == 2 else \
                       [(-3, -3, 5, 5), (3, -3, 5, 5), (0, 3, 11, 5)] if n == 3 else [(-3, -3, 5, 5), (3, -3, 5, 5), (-3, 3, 5, 5), (3, 3, 5, 5)]
                for sx, sy, w, d in subs:
                    x, y = cx + sx, cy + sy
                    dist = math.hypot(x, y)
                    hh = rng.uniform(4, 16) + (rng.random() ** 3) * 18
                    if rng.random() < 0.05 and dist > 30:
                        hh = rng.uniform(38, 48)  # a few towers pierce the net plane
                    lim = self.under_hwy(x, y, w, d)
                    if lim is not None:
                        hh = min(hh, lim - 2.5)
                    if hh < 2:
                        continue
                    box("b", (x, y, hh / 2), (w, d, hh), walls[rng.randrange(3)])
                    box("r", (x, y, hh + 0.25), (w + 0.3, d + 0.3, 0.5), roof)
                    self.blocks.append((x, y, w, d, hh))
                    # Grease Pencil silhouette linework on the roof edge (cool rim)
                    zt = hh + 0.5
                    rc = [Vector((x - w / 2 - 0.15, y - d / 2 - 0.15, zt)), Vector((x + w / 2 + 0.15, y - d / 2 - 0.15, zt)),
                          Vector((x + w / 2 + 0.15, y + d / 2 + 0.15, zt)), Vector((x - w / 2 - 0.15, y + d / 2 + 0.15, zt))]
                    self.gp_fx.stroke("roofline", rc, 0.045, self.gp_fx.mat("roofline", "#7f96b8", 0.5), 0.55, cyclic=True)
                    # rooftop clutter: AC units, a blinker
                    if rng.random() < 0.5:
                        box("ac", (x + rng.uniform(-w / 4, w / 4), y + rng.uniform(-d / 4, d / 4), hh + 1.0), (1.4, 1.4, 1.0), roof)
                    if hh > 24 and rng.random() < 0.35:
                        cyl("mast", 0.12, 4, roof, (x, y, hh + 2.5))
                        disc("blink", 0.35, 0.3, mat_emit("blink_red", "harm", 25), (x, y, hh + 4.6))
        self.hq()
        self.street_lamps()
        self.neon_signs()
        self.highways()
        self.flyers()
        self.holos()
        self.fog_patches()

    def hq(self):
        x, y = HQ
        m = mat_windows("hqw", wall="#1c2638", lit=("#bfe9ff", "#9fb2cc"), density=0.22, strength=2.0, scale=0.55, seed=9.0)
        m_strip = mat_emit("hq_strip", "#7fdcff", 3.0)
        m_trim = mat_emit("hq_trim", "cyan", 6.0)
        tiers = [(20, 20, 18), (15, 15, 20), (10, 10, 14), (6, 6, 4)]
        z = 0
        for i, (w, d, hh) in enumerate(tiers):
            box("hq%d" % i, (x, y, z + hh / 2), (w, d, hh), m)
            # vertical light strips on the camera-facing faces: the HQ reads as ONE landmark, not another window grid
            for k in range(1, int(w / 2.5)):
                o = -w / 2 + k * 2.5
                box("hqs", (x + w / 2 + 0.06, y + o, z + hh / 2), (0.1, 0.18, hh - 0.6), m_strip)
                box("hqs", (x + o, y - d / 2 - 0.06, z + hh / 2), (0.18, 0.1, hh - 0.6), m_strip)
            # cyan trim lines on each setback edge
            for sx, sy, lw, ld in ((0, -d / 2, w, 0.25), (w / 2, 0, 0.25, d), (0, d / 2, w, 0.25), (-w / 2, 0, 0.25, d)):
                box("hqt", (x + sx, y + sy, z + hh), (lw + 0.1, ld + 0.1, 0.3), m_trim)
            z += hh
        cyl("hq_mast", 0.3, 12, mat_pbr("mast", "#2a3140", 0.3, 0.8), (x, y, z + 6))
        disc("hq_blink", 0.5, 0.4, mat_emit("blink_red", "harm", 25), (x, y, z + 12.2))
        self.hq_top = z + 12.5
        # the Cell's pink hex sign on the HQ face (facing the camera: -Y face and +X face)
        m_pink = mat_emit("hq_pink", "pink", 14.0)
        hexp = [(math.cos(math.radians(30 + 60 * i)) * 4.2, 0, math.sin(math.radians(30 + 60 * i)) * 4.2) for i in range(7)]
        tube("hq_hex", hexp, 0.3, m_pink, loc=(x + 7.9, y, 28), rot=(0, 0, math.radians(90)))
        tube("hq_hex2", hexp, 0.3, m_pink, loc=(x, y - 7.9, 28))
        point((x + 12, y, 28), "pink", 9000, radius=2, name="hq_spill")   # pink pools onto the wet street below
        point((x, y - 12, 28), "pink", 9000, radius=2, name="hq_spill2")
        point((x + 6, y - 6, 3), "pink", 6000, radius=3, name="hq_spill_street")
        spot((x, y, z + 12), (x + 40, y - 30, 0), "#dfe8ff", 400000 * (0.4 + self.heat), angle=4, blend=0.3, name="hq_beacon")

    def street_lamps(self):
        """Pools of light on the wet asphalt at intersections (sodium warm / LED cool)."""
        rng = self.rng
        m_w = mat_emit("lamp_w", "#ffc98a", 30)
        m_c = mat_emit("lamp_c", "#cfe0ff", 30)
        for i in range(-5, 6):
            for j in range(-5, 6):
                if rng.random() < 0.45:
                    continue
                x, y = i * 16 - 8 + 1.6, j * 16 - 8 - 1.6
                warm = rng.random() < 0.6
                cyl("lamp_pole", 0.08, 5, mat_pbr("pole", "#222833", 0.4, 0.8), (x, y, 2.5), seg=8)
                disc("lamp", 0.3, 0.15, m_w if warm else m_c, (x, y, 5.1), seg=12)
                spot((x, y, 5.0), (x, y, 0), "#ffc98a" if warm else "#cfe0ff", 4000, angle=80, blend=0.9, radius=0.3, name="lamp_spot", vol=0.6)

    def neon_signs(self):
        rng = self.rng
        inks = ["pink", "cyan", "#B04DFF", "amber", "#FF8C1A", "cyan", "pink", "#7FA8FF"]
        for i in range(22):
            b = self.blocks[rng.randrange(len(self.blocks))]
            x, y, w, d, hh = b
            if hh < 10:
                continue
            c = inks[i % len(inks)]
            L = rng.uniform(4, min(10, hh - 2))
            z = rng.uniform(L / 2 + 1, hh - L / 2)
            # blade sign on the camera-facing side (+x or -y face)
            if rng.random() < 0.5:
                box("sign", (x + w / 2 + 0.5, y + rng.uniform(-d / 3, d / 3), z), (0.9, 0.25, L), mat_emit("sgn%d" % i, c, 9.0))
                point((x + w / 2 + 2.5, y, z), c, 1400, radius=1.0, name="sgn_spill")
            else:
                box("sign", (x + rng.uniform(-w / 3, w / 3), y - d / 2 - 0.5, z), (0.25, 0.9, L), mat_emit("sgn%d" % i, c, 9.0))
                point((x, y - d / 2 - 2.5, z), c, 1400, radius=1.0, name="sgn_spill")

    def highways(self):
        rng = self.rng
        deck = mat_pbr("deck", "#11151c", 0.3, 0.1, coat=0.6)
        m_sod = mat_emit("rail", "#9fb2cc", 1.8)
        m_head = mat_emit("head", "#f4f7ff", 30)
        m_tail = mat_emit("tail", "#ff3322", 25)
        g = self.gp_fx
        mtw = g.mat("trail_w", "#e8f0ff", 0.5)
        mtr = g.mat("trail_r", "#ff4433", 0.55)
        for (ax, c, z, a, b) in HWYS:
            L = b - a
            if ax == "x":
                box("hwy", ((a + b) / 2, c, z), (L, 7, 0.9), deck)
                box("hwy_rail", ((a + b) / 2, c - 3.6, z + 0.7), (L, 0.2, 0.5), m_sod)
                box("hwy_rail", ((a + b) / 2, c + 3.6, z + 0.7), (L, 0.2, 0.5), m_sod)
            else:
                box("hwy", (c, (a + b) / 2, z), (7, L, 0.9), deck)
                box("hwy_rail", (c + 3.6, (a + b) / 2, z + 0.7), (0.2, L, 0.5), m_sod)
                box("hwy_rail", (c - 3.6, (a + b) / 2, z + 0.7), (0.2, L, 0.5), m_sod)
            for t in range(int(a), int(b), 14):
                p = (t, c) if ax == "x" else (c, t)
                box("pillar", (p[0], p[1], z / 2), (1.4, 1.4, z), deck)
            # traffic: two lanes, long-exposure trails
            for lane, (mat, tm, sgn) in enumerate(((m_head, mtw, 1), (m_tail, mtr, -1))):
                off = -1.6 if lane == 0 else 1.6
                for k in range(int(L / 7)):
                    t = a + rng.uniform(0, L)
                    tl = rng.uniform(4, 11)
                    if ax == "x":
                        p0 = Vector((t, c + off, z + 0.75)); d = Vector((sgn, 0, 0))
                    else:
                        p0 = Vector((c + off, t, z + 0.75)); d = Vector((0, sgn, 0))
                    box("car", p0, (0.9 if ax == "x" else 0.5, 0.5 if ax == "x" else 0.9, 0.3), mat)
                    g.stroke("traffic", [p0 - d * tl, p0 - d * tl * 0.5, p0], [0.05, 0.12, 0.2], tm, [0.0, 0.35, 0.8])
        # street-level traffic too
        for k in range(70):
            c = rng.randrange(-6, 7) * 16 - 8
            t = rng.uniform(-90, 90)
            lane = rng.choice((0, 1))
            p0 = Vector((c + (-0.9 if lane else 0.9), t, 0.4)) if k % 2 else Vector((t, c + (-0.9 if lane else 0.9), 0.4))
            d = Vector((0, 1, 0)) if k % 2 else Vector((1, 0, 0))
            d = d if lane else -d
            box("scar", p0, (0.5, 0.5, 0.3), m_head if lane else m_tail)
            g.stroke("traffic", [p0 - d * 6, p0], [0.04, 0.16], mtw if lane else mtr, [0.0, 0.7])

    def flyers(self):
        rng = self.rng
        g = self.gp_fx
        m_b = mat_pbr("flyer", "#1a2030", 0.3, 0.7)
        m_l = mat_emit("flyer_l", "#dff4ff", 30)
        mt = g.mat("flyer_trail", "#bfe4ff", 0.5)
        for i in range(14):
            p = Vector((rng.uniform(-70, 70), rng.uniform(-70, 70), rng.uniform(36, 52)))
            a = rng.uniform(0, 2 * math.pi)
            d = Vector((math.cos(a), math.sin(a), 0))
            box("flyer", p, (1.8, 0.9, 0.5), m_b, rot=(0, 0, a))
            box("flyer_l", p + d * 1.0, (0.3, 0.6, 0.2), m_l, rot=(0, 0, a))
            curve = [p - d * (14 - k * 2) + Vector((0, 0, math.sin(k * 0.6) * 0.5)) + Vector((-d.y, d.x, 0)) * (0.05 * (7 - k) ** 2) for k in range(8)]
            g.stroke("flyers", curve, [0.02 + k * 0.03 for k in range(8)], mt, [k / 10 for k in range(8)])

    def holos(self):
        rng = self.rng
        colors = ["cyan", "pink", "#B04DFF", "amber", "cyan", "#7FA8FF"]
        cands = sorted([b for b in self.blocks if 12 < b[4] < 28], key=lambda b: (b[0], b[1]))
        rng.shuffle(cands)
        cam_yaw = math.radians(45)
        for i, (x, y, w, d, hh) in enumerate(cands[:7]):
            c = colors[i % len(colors)]
            W, H = rng.uniform(8, 13), rng.uniform(5, 8)
            zc = hh + 3 + H / 2
            ob = rrect("holo%d" % i, W, H, 0.1, (x, y, zc), mat_holo("holo%d" % i, c, 6.0, seed=i * 1.7 + 0.3, bands=70), rot=(R90, 0, cam_yaw))
            self.hide_depth.append(ob)
            ux = Vector((math.cos(cam_yaw), math.sin(cam_yaw), 0))
            cc = Vector((x, y, zc)) + Vector((-ux.y, ux.x, 0)) * -0.05
            fr = [cc + ux * sx * W / 2 + Vector((0, 0, sz * H / 2)) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            self.gp_fx.stroke("holoframe", fr, 0.09, self.gp_fx.mat("hf_" + c, c, 0.9), 0.9, cyclic=True)
            # a bright headline row and a flicker tear
            self.gp_fx.stroke("holoframe", [cc + ux * (-W * 0.42) + Vector((0, 0, H * 0.3)), cc + ux * (W * 0.1) + Vector((0, 0, H * 0.3))], 0.35, self.gp_fx.mat("hl_" + c, c, 0.9), 0.85)
            # projector: emitter + faint volumetric cone up to the board
            disc("proj", 0.5, 0.3, mat_emit("proj_" + c, c, 20), (x, y, hh + 0.7))
            cone = bpy.data.meshes.new("cone")
            import bmesh as _bm
            bm = _bm.new()
            _bm.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.4, radius2=W * 0.45, depth=3 + H)
            bm.to_mesh(cone); bm.free()
            co = bpy.data.objects.new("cone", cone)
            co.location = (x, y, hh + 0.7 + (3 + H) / 2)
            co.scale = (1, 0.25, 1)
            co.rotation_euler = (0, 0, cam_yaw)
            cone.materials.append(mat_volume("cone_" + c, 0.02, c, emit=c, emit_str=0.25))
            link(co)
            self.hide_depth.append(co)
            point((x, y, zc), c, 3000, radius=W / 3, name="holo_spill")

    def fog_patches(self):
        rng = self.rng
        for i in range(10):
            p = Vector((rng.uniform(-70, 60), rng.uniform(-70, 60), rng.uniform(2, 14)))
            r = rng.uniform(10, 24)
            dens = rng.uniform(0.04, 0.12) * (1 + self.heat)
            ob = disc("fog%d" % i, 1, 1, mat_volume("fog%d" % i, dens, "#8795ab", noise_scale=1.6, noise_contrast=2.2, seed=i * 1.3), p)
            ob.scale = (r, r * rng.uniform(0.6, 1.0), r * 0.35)
            self.hide_depth.append(ob)
            self.fog.append((p, r))

    # ------------------------------------------------------------ the net: nodes and links on one plane
    def net(self, claimed=("hq", "a", "b"), threat=("e", "f")):
        nodes = {"hq": (HQ[0], HQ[1]), "a": (22, -8), "b": (-40, -22), "c": (42, 40), "d": (-44, 36), "e": (8, -52), "f": (60, -34)}
        links = [("hq", "a"), ("hq", "b"), ("hq", "d"), ("a", "c"), ("a", "e"), ("e", "f"), ("b", "e"), ("c", "f")]
        g = self.gp_net
        # faint map grid on the net plane
        mg = g.mat("netgrid", "cyan", 0.22)
        for k in range(-80, 81, 16):
            g.stroke("grid", [Vector((k, -80, NET_Z)), Vector((k, 80, NET_Z))], 0.09, mg, 0.5)
            g.stroke("grid", [Vector((-80, k, NET_Z)), Vector((80, k, NET_Z))], 0.09, mg, 0.5)
        m_link = mat_emit("link", "cyan", 5)
        m_claim = mat_emit("claim", "acid", 7)
        m_threat = mat_emit("threat", "#FF8C1A", 7)
        mchev = g.mat("chev", "#FF8C1A", 0.95)
        for a, b in links:
            pa, pb = Vector((*nodes[a], NET_Z)), Vector((*nodes[b], NET_Z))
            cl = a in claimed and b in claimed
            th = a in threat or b in threat
            m = m_claim if cl else m_threat if th else m_link
            tube("link", [pa, pb], 0.32 if cl else 0.22, m)
            if th:  # corp chevrons along threat routes (Meridian stripes)
                d = (pb - pa)
                n = int(d.length / 6)
                dn = d.normalized()
                side = Vector((-dn.y, dn.x, 0))
                for k in range(1, n):
                    c = pa + d * (k / n)
                    g.stroke("chev", [c - dn * 1.2 + side * 1.2, c, c - dn * 1.2 - side * 1.2], 0.25, mchev, 1.0)
        for k, (x, y) in sorted(nodes.items()):
            cl = k in claimed
            c = "acid" if cl else "#FF8C1A" if k in threat else "cyan"
            r = 5.5 if k == "hq" else 3.0
            hexp = [Vector((x + r * math.cos(math.radians(60 * i)), y + r * math.sin(math.radians(60 * i)), NET_Z)) for i in range(7)]
            tube("node", hexp, 0.35, mat_emit("node_" + c, c, 9))
            disc("node_fill", r * 0.9, 0.05, mat_emit("nodefill_" + c, c, 1.5, alpha=0.25), (x, y, NET_Z), seg=6)
            if cl:  # turf hatch inside claimed nodes
                for j in range(-2, 3):
                    g.stroke("hatch", [Vector((x + j * r * 0.3 - r * 0.3, y - r * 0.5, NET_Z + 0.05)), Vector((x + j * r * 0.3 + r * 0.3, y + r * 0.5, NET_Z + 0.05))], 0.12, g.mat("hatch", "acid", 0.8), 0.8)
            point((x, y, NET_Z + 2), c, 2500 if k != "hq" else 6000, radius=2, name="node_glow")
        self.nodes = nodes

    # ------------------------------------------------------------ UI parented to the ortho camera
    def compute_focus(self, pt=None):
        pt = pt or Vector((HQ[0], HQ[1], 18))
        corners = [Vector((x, y, z)) for x in (-110, 110) for y in (-110, 110) for z in (0, 70)]
        ds = [(c - self.cam.location).dot(self.fwd) for c in corners]
        self.focus_value = ((pt - self.cam.location).dot(self.fwd) - min(ds)) / (max(ds) - min(ds))
        return self.focus_value

    def ui_gp(self):
        self.gp_ui = GP("gp_ui_cam")
        self.gp_ui.ob.parent = self.cam
        return self.gp_ui

    def ui_panel(self, x, y, w, h, title=None, edge="cyan", rule="pink", alpha=0.84):
        u = self.upx
        c = self.cam_ui(x + w / 2, y + h / 2, -20)
        ob = rrect("ui_panel", u(w), u(h), u(6), c, mat_pbr("ui_glass", "#050d1c", 0.3, 0.0, alpha=alpha), rot=(0, 0, 0), parent=self.cam)
        self.ui.append(ob)
        g = self.gp_ui
        pts = [self.cam_ui(px, py, -19.9) for px, py in ((x, y), (x + w, y), (x + w, y + h), (x, y + h))]
        g.stroke("ui", pts, u(0.8), g.mat("edge_" + edge, edge, 0.8), 0.9, cyclic=True)
        if title:
            self.ui_text(title, x + 14, y + 20, 17, "text_mid", 1.6)
            g.stroke("ui", [self.cam_ui(x + 14, y + 36, -19.9), self.cam_ui(x + w - 14, y + 36, -19.9)], u(1.1), g.mat("rule_" + rule, rule), 0.9)
        return ob

    def ui_text(self, body, x, y, size, color="text_hi", strength=1.8, fnt=MONO, align="LEFT", alpha=1.0):
        ob = text(body, self.cam_ui(x, y, -19.8), self.upx(size), mat_emit("uit_%s_%.1f_%.1f" % (color, strength, alpha), color, strength, alpha),
                  fnt, align, "CENTER", rot=(0, 0, 0), parent=self.cam, name="ui_txt")
        self.ui.append(ob)
        return ob

    def label_at(self, world_pt, body, color="text_hi", dx=18, dy=-18, size=16):
        """A glass tag pinned to a world point (drawn in screen space so it stays sharp)."""
        sc = bpy.context.scene
        v = world_to_camera_view(sc, self.cam, Vector(world_pt))
        x, y = v.x * 1920, (1 - v.y) * 1080
        w = len(body) * size * 0.56 + 24
        self.ui_panel(x + dx, y + dy - 16, w, 32, alpha=0.8, edge=color)
        self.ui_text(body, x + dx + 12, y + dy, size, color, 2.0)
        return x, y

    # ------------------------------------------------------------ rain
    def rain(self, n=6000):
        rain(self.gp_fx, n, 77, (-100, 100), (-100, 100), (0, 80), length=(2.5, 6.0), radius=(0.04, 0.08), slant=0.12, alpha=(0.15, 0.5))
        splashes(self.gp_fx, 900, 78, (-80, 80), (-80, 80), 0.0, size=(0.3, 0.9), alpha=0.35)

    # ------------------------------------------------------------ passes
    def depth_pass(self, path, focus_obj_names=()):
        """Render normalized camera depth (0 near .. 1 far) to PNG for tilt-shift. UI gets depth -> focus."""
        sc = bpy.context.scene
        corners = [Vector((x, y, z)) for x in (-110, 110) for y in (-110, 110) for z in (0, 70)]
        ds = [(c - self.cam.location).dot(self.fwd) for c in corners]
        dmin, dmax = min(ds), max(ds)
        m = bpy.data.materials.new("depth")
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        cd = nt.nodes.new("ShaderNodeCameraData")
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = dmin
        mr.inputs["From Max"].default_value = dmax
        em = nt.nodes.new("ShaderNodeEmission")
        nt.links.new(cd.outputs["View Z Depth"], mr.inputs["Value"])
        nt.links.new(mr.outputs[0], em.inputs["Strength"])
        nt.links.new(em.outputs[0], out.inputs["Surface"])
        mf = mat_emit("depth_focus", "#ffffff", self.focus_value)
        hide = set(o.name for o in self.hide_depth)
        for o in list(bpy.data.objects):
            if o.type in ("GREASEPENCIL", "LIGHT") or o.name in hide:
                o.hide_render = True
                continue
            if o.type in ("MESH", "CURVE", "FONT"):
                mm = mf if o in self.ui else m
                o.data.materials.clear()
                o.data.materials.append(mm)
        sc.world = world("#ffffff", 1.0)
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.look = "None"
        sc.compositing_node_group = None
        sc.eevee.taa_render_samples = 1
        render(path)

    def export_fog(self, path):
        sc = bpy.context.scene
        pts = []
        for p, r in self.fog:
            v = world_to_camera_view(sc, self.cam, p)
            pts.append({"x": v.x, "y": 1 - v.y, "r": r / ORTHO})
        with open(path, "w") as f:
            json.dump({"fog": pts, "focus": self.focus_value}, f)
