"""S2 (E format) asset models: chunky, wonky, hand-painted gritty toon props with thick ink; the
digital layer (holograms, gems, data) is faceted crystal (tt_facet, no ink).

Every builder takes an rng and builds at the world origin, facing -Y (toward the camera).
render_item.py frames and renders one builder to a transparent PNG.
Seeded randomness only.
"""
import math
import random
import bmesh
import bpy
from mathutils import Vector
import tt_lib as T
import tt_facet as Fc

INK = "#1c1210"
CORP = {
    "meridian": ("#e8782a", "#2a2c30"),     # orange + soot, container stripes
    "solace": ("#5fd8b0", "#e8f4ee"),       # mint + white, helix dots
    "halcyon": ("#3f7fd8", "#e8e2cc"),      # civic blue + limestone
    "orbital": ("#9a7ae8", "#d8dce8"),      # violet + satellite white
}


def M(h, **kw):
    return T.paint(h, **kw)


def obj_from_bm(bm, name, mat):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    T.link_obj(o)
    if mat:
        me.materials.append(mat)
    return o


def blob(r, loc, mat, rng, scale=(1, 1, 1), wob=0.04, subd=2, name="blob", smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subd, radius=r)
    for v in bm.verts:
        v.co *= 1 + rng.uniform(-wob, wob)
        v.co.x *= scale[0]
        v.co.y *= scale[1]
        v.co.z *= scale[2]
    for f in bm.faces:
        f.smooth = smooth
    o = obj_from_bm(bm, name, mat)
    o.location = loc
    return o


def arm(p0, p1, r, mat, name="arm"):
    """Chunky limb (tapered cylinder) between two points."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    o = T.cyl(r, d.length, (0, 0, 0), mat, verts=10, bev=0.04, r2=r * 0.85, name=name)
    o.location = p0
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return o


# =============================================================== operatives (B1)
SKIN = ["#c98a64", "#8a5a3e", "#e0b090"]


def face(z, rng, state, skin, eyes_glow=None, hood=False):
    """Eyes, brows, mouth on a head centred at (0, 0, z) of radius ~0.62 (front at y=-0.58)."""
    ink = M("#24181a", flat=True)
    fy = -0.6
    if state == "flatlined":
        for sx in (-1, 1):
            for a in (45, -45):
                T.box((0.2, 0.05, 0.05), (sx * 0.22, fy, z + 0.08), ink, bev=0, rot=(0, a, 0))
        T.box((0.24, 0.05, 0.04), (0, fy + 0.02, z - 0.24), ink, bev=0, rot=(0, 8, 0))
        return
    for sx in (-1, 1):
        if eyes_glow:
            T.box((0.17, 0.06, 0.07), (sx * 0.22, fy, z + 0.06), T.glow(eyes_glow, 3.0), bev=0.01)
        elif state == "hurt" and sx > 0:
            T.box((0.17, 0.05, 0.035), (sx * 0.22, fy, z + 0.05), ink, bev=0)            # squint
        else:
            o = T.cyl(0.07, 0.06, (sx * 0.22, fy, z + 0.06), ink, verts=8, bev=0, rot=(90, 0, 0), origin_bottom=False)
            o.scale = (1.0, 1.4 if state != "triumphant" else 0.9, 1.0)
        if not hood:
            brow_rot = {"neutral": sx * -6, "hurt": sx * 18, "triumphant": sx * -14}.get(state, 0)
            T.box((0.24, 0.07, 0.06), (sx * 0.22, fy - 0.01, z + 0.22 + (0.03 if state == "triumphant" else 0)),
                  M("#2a1c18"), bev=0.01, rot=(0, brow_rot, 0))
    if state == "triumphant":
        T.box((0.36, 0.06, 0.12), (0, fy + 0.02, z - 0.24), M("#3a1418"), bev=0.03)        # open grin
        T.box((0.3, 0.07, 0.04), (0, fy + 0.0, z - 0.2), M("#f4ecd8"), bev=0.0)
    elif state == "hurt":
        T.box((0.26, 0.05, 0.04), (0.02, fy + 0.02, z - 0.25), ink, bev=0, rot=(0, -10, 0))
        T.box((0.18, 0.05, 0.14), (-0.3, fy + 0.03, z + 0.0), M("#7a3a4a", flat=True), bev=0)   # bruise
    else:
        T.box((0.24, 0.05, 0.04), (0, fy + 0.02, z - 0.25), ink, bev=0)


def bust(cls, state, rng):
    """Polaroid bust: Breaker (heavy jacket, antenna-crowbar) or Ghost (hood, crystal face mesh)."""
    skin = SKIN[0] if cls == "breaker" else SKIN[2]
    sk = M(skin, stroke=0.12, grime=0.1)
    tilt = {"hurt": 8, "flatlined": -18, "triumphant": -4}.get(state, 0)
    root = T.empty("root")
    objs_before = set(bpy.data.objects)
    hz = 1.95
    if cls == "breaker":
        jacket = M("#6e4a2e", stroke=0.3, streak_axis=2, seed=2)
        T.box((2.2, 1.35, 1.4), (0, 0.1, 0), jacket, bev=0.22, wonk=0.04, rng=rng, taper=0.12)
        T.box((2.4, 1.15, 0.42), (0, 0.05, 1.0), jacket, bev=0.2, wonk=0.05, rng=rng)                  # shoulders
        for sx in (-1, 1):                                                                            # pads
            T.box((0.6, 0.95, 0.32), (sx * 1.0, 0.05, 1.3), M("#4a4e52", gloss=0.3), bev=0.12, wonk=0.06, rng=rng,
                  rot=(0, sx * -14, 0))
            T.cyl(0.07, 0.05, (sx * 1.0, -0.46, 1.48), M("#a8a8a0", gloss=0.8), verts=8, bev=0.01, rot=(90, 0, 0))
        T.box((1.3, 0.5, 0.55), (0, -0.35, 1.2), M("#4e3220", stroke=0.25), bev=0.15, rot=(-15, 0, 0))   # collar
        T.box((0.16, 0.06, 1.1), (0.0, -0.69, 0.1), M("#c8a030", gloss=0.5), bev=0.02)               # zip
        T.box((0.55, 0.08, 0.45), (-0.55, -0.7, 0.4), M("#5a3a24", pattern="plank"), bev=0.04, rot=(0, 6, 0))   # patch
        T.cyl(0.32, 0.4, (0, 0, 1.45), sk, verts=12, bev=0.03)
        head = blob(0.66, (0, 0, hz), sk, rng, (1.0, 0.92, 1.05), name="head")
        head.rotation_euler = (0, math.radians(tilt), 0)
        # knit beanie (rolled cuff) + stubble jaw + ears
        blob(0.7, (0, 0.05, hz + 0.3), M("#3a4a44", stroke=0.35), rng, (1.0, 0.98, 0.75), name="beanie")
        T.cyl(0.71, 0.2, (0, 0.03, hz + 0.18), M("#2e3a36", stroke=0.3), verts=16, bev=0.06, wonk=0.04, rng=rng)
        blob(0.5, (0, -0.12, hz - 0.36), M("#5e4a3e", stroke=0.35), rng, (1.05, 0.82, 0.45), name="jaw")
        for sx in (-1, 1):
            blob(0.16, (sx * 0.64, 0.0, hz + 0.0), sk, rng, (0.6, 1.0, 1.2), name="ear")
        face(hz, rng, state, skin)
        # antenna-crowbar over the right shoulder (raised overhead when triumphant)
        if state == "triumphant":
            arm((1.15, -0.2, 1.3), (1.35, -0.4, 2.6), 0.3, jacket)
            blob(0.32, (1.35, -0.45, 2.75), sk, rng, name="fist")
            cb0, cb1 = Vector((0.6, -0.55, 4.0)), Vector((2.1, -0.35, 1.6))
        elif state == "flatlined":
            cb0, cb1 = Vector((-1.6, -0.6, -0.2)), Vector((1.4, -0.7, 0.3))
        else:
            cb0, cb1 = Vector((-0.4, 0.4, 3.5)), Vector((1.6, -0.6, 0.2))
        arm(cb1, cb0, 0.09, M("#8e3a2a", gloss=0.4), name="crowbar")
        T.box((0.4, 0.14, 0.12), tuple(cb1 + Vector((0.12, 0, -0.1))), M("#8e3a2a", gloss=0.4), bev=0.02, rot=(0, 30, 0))
        arm(cb0, cb0 + (cb0 - cb1).normalized() * 0.9, 0.025, M("#4a4a4e"), name="antenna")
        tip = cb0 + (cb0 - cb1).normalized() * 0.9
        T.cyl(0.08, 0.1, tuple(tip), T.glow("#ff4a3a", 4), verts=8, bev=0)
        if state == "hurt":
            T.box((1.4, 1.36, 0.18), (0, 0.0, hz + 0.05), M("#e8e0cc", stroke=0.3), bev=0.06, rot=(0, -12, 0))   # bandage
            T.box((0.3, 0.06, 0.08), (0.3, -0.69, hz + 0.08), M("#a03030", flat=True), bev=0)
    else:   # ghost
        cloak = M("#3a4250", stroke=0.3, seed=5)
        T.box((2.0, 1.3, 1.4), (0, 0.1, 0), cloak, bev=0.25, wonk=0.04, rng=rng, taper=0.2)
        T.box((2.2, 1.05, 0.4), (0, 0.05, 1.0), cloak, bev=0.18, wonk=0.05, rng=rng)
        T.cyl(0.3, 0.4, (0, 0, 1.45), sk, verts=12, bev=0.03)
        head = blob(0.6, (0, 0, hz), sk, rng, (0.95, 0.92, 1.05), name="head")
        # hood: a big wonky shell, open at the front
        hood = blob(0.92, (0, 0.18, hz + 0.12), M("#2c3240", stroke=0.35, seed=7), rng, (1.05, 1.0, 1.12), name="hood")
        bm = bmesh.new()
        bm.from_mesh(hood.data)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_center_median().y < -0.25 and
                                   abs(f.calc_center_median().x) < 0.62 and f.calc_center_median().z < 0.55], context="FACES")
        bm.to_mesh(hood.data)
        bm.free()
        T.cyl(0.95, 0.5, (0, 0.2, 1.25), M("#2c3240", stroke=0.3), r2=0.7, verts=14, bev=0.06)       # hood drape
        face(hz, rng, state, SKIN[2], eyes_glow=(None if state == "flatlined" else "#3ff0ff"), hood=True)
        # crystal face mesh over the lower face (digital layer)
        if state != "flatlined":
            Fc.tri_panel(0.95, 0.5, 5, 3, ["#3ff0ff", "#1c6a7a"], loc=(0, -0.66, hz - 0.28), rot=(90, 0, 0),
                         glow=1.1, seed=3, alpha=0.85)
        else:
            Fc.tri_panel(0.95, 0.5, 5, 3, ["#3a4a50"], loc=(0, -0.66, hz - 0.28), rot=(90, 0, 0), glow=0.6, seed=3,
                         image=lambda u, v: None if (u * 3 + v) % 1 < 0.3 else 0)
        # chest rig: wrist deck with crystal data shards
        T.box((0.9, 0.25, 0.5), (0.45, -0.72, 0.35), M("#2a2e36", gloss=0.4), bev=0.08, rot=(0, -10, 0))
        T.box((0.62, 0.05, 0.28), (0.45, -0.86, 0.4), T.glow("#3ff0ff", 1.4), bev=0.02, rot=(0, -10, 0))
        for k in range(3):   # hood toggles / straps
            T.cyl(0.05, 0.7, (-0.25 + k * 0.25, -0.62, 0.6), M("#6a6e70"), verts=6, bev=0)
        if state == "triumphant":
            arm((-1.1, -0.2, 1.2), (-1.4, -0.5, 2.6), 0.28, cloak)
            blob(0.3, (-1.4, -0.55, 2.75), M(SKIN[2]), rng, name="fist")
            for k in range(7):
                Fc.shard(0.1, (-1.4 + rng.uniform(-0.6, 0.6), -0.7, 3.0 + rng.uniform(0, 0.8)), "#3ff0ff", 2.0, rng)
        if state == "hurt":
            for k in range(5):
                Fc.shard(0.07, (rng.uniform(-0.6, 0.6), -0.9, hz + rng.uniform(-0.6, 0.4)), "#ff4a5a", 1.6, rng)
    if state in ("hurt", "flatlined"):
        for o in set(bpy.data.objects) - objs_before:
            if o.parent is None and o.location.z > 1.3:
                o.rotation_euler.y += math.radians(tilt) * 0.6
    return root


# =============================================================== enemies (B2) + bezels
def hologram_base(col, r=1.4):
    T.cyl(r, 0.35, (0, 0, -0.35), M("#3a3c42", gloss=0.3), verts=16, bev=0.06)
    T.cyl(r * 0.8, 0.06, (0, 0, 0.0), T.glow(col, 2.0), verts=16, bev=0)
    beam = T.cyl(r * 0.8, 3.4, (0, 0, 0.0), T.beam(col, 0.9, 0.0, 0.18, "holo"), r2=r * 1.1, verts=16, bev=0,
                 coll=T.noline_coll())


def enemy(kind, rng):
    if kind == "manifest":
        # Meridian routing core: a painted armoured core cage with a faceted crystal heart, orbiting containers
        or_, soot = CORP["meridian"]
        T.cyl(1.9, 0.5, (0, 0, -0.5), M("#3a3c42", gloss=0.3), verts=8, bev=0.08, wonk=0.03, rng=rng)
        Fc.cut_gem(1.05, 1.1, 1.3, n=8, loc=(0, 0, 1.9), col=or_, glow=1.3, seed=4, table=0.4)
        for k in range(6):                       # cage ribs
            a = k / 6 * math.tau
            arm((math.cos(a) * 1.0, math.sin(a) * 1.0, 0.0), (math.cos(a) * 1.55, math.sin(a) * 1.55, 1.9), 0.12,
                M(soot, gloss=0.3))
            arm((math.cos(a) * 1.55, math.sin(a) * 1.55, 1.9), (math.cos(a) * 0.8, math.sin(a) * 0.8, 3.7), 0.12,
                M(soot, gloss=0.3))
        T.cyl(0.6, 0.4, (0, 0, 3.6), M(soot), verts=8, bev=0.06)
        for k in range(5):                       # orbiting containers with stripes
            a = k / 5 * math.tau + 0.3
            c = (math.cos(a) * 2.5, math.sin(a) * 2.5 * 0.6, 1.4 + math.sin(a * 2) * 0.9)
            b = T.box((0.9, 0.45, 0.45), c, M(rng.choice((or_, "#3a6a8a", "#8e3a2a", or_)), pattern="plank", pat_scale=1.6),
                      bev=0.04, wonk=0.04, rng=rng, rot=(0, rng.uniform(-15, 15), math.degrees(a) + 90))
        ring = T.cyl(2.5, 0.03, (0, 0, 1.4), T.glow(or_, 1.3, alpha=0.5), verts=32, bev=0, coll=T.noline_coll())
        ring.scale = (1, 0.6, 1)
    elif kind == "adjuster":
        # Solace elite: an insurance claims adjuster in a mint suit, twin reading lenses, two floating claim holograms
        mint, white = CORP["solace"]
        suit = M(mint, stroke=0.25, seed=3)
        T.box((2.5, 1.3, 1.5), (0, 0.1, 0), suit, bev=0.2, wonk=0.03, rng=rng, taper=0.2)
        T.box((2.7, 1.1, 0.4), (0, 0.05, 1.1), suit, bev=0.18, wonk=0.04, rng=rng)
        T.box((0.6, 0.1, 1.2), (0, -0.66, 0.6), M(white), bev=0.04)                                   # shirt
        T.box((0.18, 0.08, 0.9), (0, -0.72, 0.55), M("#2a6a5a"), bev=0.02, taper=-0.5)               # tie
        for k in range(5):                                                                           # helix dots lapel
            T.cyl(0.05, 0.04, (-0.55 + 0.08 * math.sin(k), -0.68, 0.3 + k * 0.18), M(white, flat=True), verts=8, bev=0,
                  rot=(90, 0, 0))
        T.cyl(0.3, 0.4, (0, 0, 1.45), M(SKIN[2]), verts=12, bev=0.03)
        blob(0.62, (0, 0, 1.95), M(SKIN[2], stroke=0.1), rng, (0.95, 0.9, 1.08), name="head")
        blob(0.64, (0, 0.08, 2.25), M("#2a2420", stroke=0.3), rng, (1.0, 0.95, 0.5), name="hair")
        for sx in (-1, 1):                                                                           # twin lenses
            T.cyl(0.2, 0.08, (sx * 0.24, -0.6, 2.0), M("#2a2c30", gloss=0.5), verts=14, bev=0.02, rot=(90, 0, 0),
                  origin_bottom=False)
            T.cyl(0.14, 0.04, (sx * 0.24, -0.66, 2.0), T.glow(mint, 2.0), verts=14, bev=0, rot=(90, 0, 0),
                  origin_bottom=False)
        T.box((0.26, 0.05, 0.03), (0, -0.62, 1.68), M("#3a2420", flat=True), bev=0)
        for sx in (-1, 1):                                                                           # two claims read at once
            Fc.tri_panel(1.0, 1.3, 4, 5, [mint, white], loc=(sx * 1.85, -0.5, 2.4), rot=(90, 0, sx * -18), glow=1.2,
                         seed=10 + sx, alpha=0.8, image=lambda u, v: 1 if (abs(v - 0.8) < 0.05 or abs(v - 0.55) < 0.04
                                                                          or abs(v - 0.35) < 0.04) else 0)
            arm((sx * 1.15, -0.2, 1.2), (sx * 1.6, -0.55, 1.9), 0.25, suit)
    else:   # collections drone (Meridian regular machine, per the spec)
        or_, soot = CORP["meridian"]
        body = blob(0.9, (0, 0, 1.6), M(soot, gloss=0.3, stroke=0.25), rng, (1.15, 0.9, 0.75), subd=1, smooth=False,
                    name="dbody")
        T.box((1.6, 0.3, 0.35), (0, -0.55, 1.6), M(or_, pattern="plank", pat_scale=2.2), bev=0.06)    # container stripe band
        T.cyl(0.32, 0.2, (0, -0.72, 1.62), M("#2a2c30"), verts=12, bev=0.03, rot=(90, 0, 0), origin_bottom=False)
        T.cyl(0.2, 0.1, (0, -0.84, 1.62), T.glow("#ff4a3a", 3.5), verts=12, bev=0, rot=(90, 0, 0), origin_bottom=False)
        for sx in (-1, 1):
            arm((sx * 0.9, 0, 1.7), (sx * 1.7, 0, 2.0), 0.08, M("#4a4a4e"))
            T.cyl(0.7, 0.08, (sx * 1.7, 0, 2.05), M("#8e928c", gloss=0.3), verts=12, bev=0.02)
            T.cyl(0.65, 0.02, (sx * 1.7, 0, 2.14), T.glow(or_, 0.8, alpha=0.4), verts=16, bev=0, coll=T.noline_coll())
        arm((0, 0, 0.95), (-0.4, -0.3, 0.3), 0.07, M("#4a4a4e"))                                     # grabber claw
        arm((-0.4, -0.3, 0.3), (-0.2, -0.45, -0.1), 0.06, M("#4a4a4e"))
        T.box((0.5, 0.4, 0.4), (0.2, -0.2, 0.1), M("#a8743a", pattern="plank"), bev=0.04, rot=(0, 0, 15))   # parcel
        # HP readout + aim mark (crystal)
        Fc.cut_gem(0.18, 0.1, 0.05, n=6, loc=(0.9, -0.6, 2.4), col="#ff4a5a", glow=1.4, rot=(90, 0, 0), seed=3)


def bezel(corp, rng):
    """Wheel bezel ring segment (an arc of the corporate frame)."""
    col, sec = CORP[corp]
    R, r = 3.0, 2.3
    n = 9
    for k in range(n):
        a0 = math.radians(25 + k * 130 / n)
        a1 = math.radians(25 + (k + 1) * 130 / n) - 0.02
        pts = [(math.cos(a0 + (a1 - a0) * i / 4) * R, math.sin(a0 + (a1 - a0) * i / 4) * R) for i in range(5)]
        pts += [(math.cos(a1 - (a1 - a0) * i / 4) * r, math.sin(a1 - (a1 - a0) * i / 4) * r) for i in range(5)]
        if corp == "meridian":
            c = col if k % 2 == 0 else "#2a2c30"                 # container stripes
            o = T.prism(pts, 0.45 + rng.uniform(-0.04, 0.04), (0, 0, 0), M(c, pattern="plank", pat_scale=2.5, stroke=0.3),
                        bev=0.05)
        else:
            o = T.prism(pts, 0.45, (0, 0, 0), M(col, stroke=0.25, gloss=0.3), bev=0.06)
        o.rotation_euler = (math.radians(90), 0, 0)
    if corp == "solace":                                         # helix dots: two sine rows of white beads
        for i in range(26):
            a = math.radians(28 + i * 124 / 25)
            for ph in (0, math.pi):
                rr = (R + r) / 2 + 0.22 * math.sin(i * 0.9 + ph)
                T.cyl(0.08, 0.06, (math.cos(a) * rr, -0.48, math.sin(a) * rr), M(sec, flat=True), verts=8, bev=0,
                      rot=(90, 0, 0), origin_bottom=False)
    else:
        for i in range(8):                                       # rivets
            a = math.radians(32 + i * 116 / 7)
            T.cyl(0.08, 0.08, (math.cos(a) * (R - 0.12), -0.48, math.sin(a) * (R - 0.12)), M("#b8b4a8", gloss=0.8),
                  verts=8, bev=0.02, rot=(90, 0, 0), origin_bottom=False)


# =============================================================== landmarks (A2)
def plinth(rng, r=3.6):
    T.cyl(r, 0.5, (0, 0, -0.5), M("#6e695e", stroke=0.3, pattern="tiles"), verts=8, bev=0.1, wonk=0.03, rng=rng)
    T.cyl(r + 0.25, 0.25, (0, 0, -0.75), M("#4a4640"), verts=8, bev=0.06)
    for i in range(10):
        a = rng.uniform(0, math.tau)
        T.rock(rng.uniform(0.12, 0.25), (math.cos(a) * r * 0.9, math.sin(a) * r * 0.9, 0.0), M("#8a8478"), rng, flat=0.6)


def landmark(kind, rng):
    plinth(rng)
    if kind == "ziggurat":
        or_, soot = CORP["meridian"]
        for k, (w, h) in enumerate(((5.0, 1.0), (4.0, 1.0), (3.0, 1.0), (2.0, 1.0))):
            T.box((w, w * 0.85, h), (0, 0.2, k * 1.0), M(rng.choice(("#5a5048", "#6a5a48", "#4e4a44")), pattern="brick"),
                  bev=0.08, wonk=0.03, rng=rng)
            T.box((w + 0.05, w * 0.85 + 0.05, 0.12), (0, 0.2, k * 1.0 + 0.55), M(or_), bev=0.02)    # orange band
        T.box((1.0, 0.8, 0.8), (0, 0.2, 4.0), M(soot), bev=0.06)
        T.cyl(0.05, 1.0, (0.2, 0.2, 4.8), M("#4a4a4e"), verts=6, bev=0)
        T.cyl(0.1, 0.12, (0.2, 0.2, 5.8), T.glow("#ff4a3a", 4), verts=8, bev=0)
        cols = (or_, "#3a6a8a", "#8e3a2a", "#4a6a4a", or_)
        for i in range(9):                                                 # container yard
            x = -2.6 + (i % 3) * 0.95
            y = -1.9 + (i // 3) * 0.5
            for j in range(rng.randint(1, 3)):
                T.box((0.85, 0.42, 0.42), (x, y - 0.4, j * 0.43), M(rng.choice(cols), pattern="plank", pat_scale=2.0),
                      bev=0.03, wonk=0.03, rng=rng)
        # gantry crane
        for sx in (1.4, 3.0):
            for sy in (-2.2, -1.0):
                T.box((0.14, 0.14, 3.2), (sx, sy, 0), M(or_), bev=0.02)
        T.box((1.9, 1.5, 0.22), (2.2, -1.6, 3.2), M(or_, pattern="plank", pat_scale=3), bev=0.03)
        T.box((0.5, 0.4, 0.35), (2.0, -1.6, 2.85), M(soot), bev=0.04)
        arm((2.0, -1.6, 2.85), (2.0, -1.6, 1.6), 0.03, M("#2a2a2e"))
        T.box((0.85, 0.42, 0.42), (2.0, -1.6, 1.2), M("#3a6a8a", pattern="plank", pat_scale=2.0), bev=0.03)
    elif kind == "pyramid":
        blue, lime = CORP["halcyon"]
        for k in range(5):
            w = 5.0 - k * 0.95
            T.box((w, w, 0.8), (0, 0, k * 0.8), M(lime, pattern="brick", stroke=0.25), bev=0.06, wonk=0.02, rng=rng,
                  taper=0.06)
            n = max(3, int(w / 0.5))
            for c in range(n):                                             # colonnade on each tier front
                x = -w / 2 + 0.25 + c * (w - 0.5) / (n - 1)
                T.cyl(0.07, 0.6, (x, -w / 2 - 0.08, k * 0.8 + 0.05), M("#e8e2d0"), verts=8, bev=0.01)
            T.box((w * 0.8, 0.08, 0.2), (0, -w / 2 - 0.05, k * 0.8 + 0.45), T.glow(blue, 1.0) if k % 2 else M(blue),
                  bev=0.01)
        T.box((0.9, 0.9, 0.9), (0, 0, 4.0), M(blue, gloss=0.3), bev=0.06, taper=0.6)
        halo_z = 5.6
        import tt_props as Pr
        Pr.ring(1.7, 2.05, 0.18, (0, 0, halo_z), M("#d8d4c8", gloss=0.5), None, bev=0.03, segs=24)
        Fc.facet_ribbon([(math.cos(a / 24 * math.tau) * 1.9, math.sin(a / 24 * math.tau) * 1.9) for a in range(25)],
                        0.18, halo_z + 0.15, blue, glow=1.4, seed=2, thick=0.06)
        for k in range(3):
            a = k / 3 * math.tau
            arm((math.cos(a) * 0.3, math.sin(a) * 0.3, 4.6), (math.cos(a) * 1.9, math.sin(a) * 1.9, halo_z), 0.04,
                M("#4a4a4e"))
    else:   # orbital tether
        vio, white = CORP["orbital"]
        T.cyl(1.6, 0.8, (0, 0, 0), M("#5a5866", pattern="tiles"), verts=8, bev=0.08, wonk=0.03, rng=rng)
        for sx in range(3):                                                # buttress legs
            a = sx / 3 * math.tau
            arm((math.cos(a) * 2.6, math.sin(a) * 2.6, 0.0), (math.cos(a) * 0.5, math.sin(a) * 0.5, 4.0), 0.18,
                M(white, stroke=0.25))
        T.cyl(0.95, 7.0, (0, 0, 0.8), M(white, stroke=0.3, streak_axis=2), r2=0.45, verts=8, bev=0.06, wonk=0.04, rng=rng)
        for z in (2.2, 3.8, 5.4, 7.0):
            T.cyl(1.02 - z * 0.07, 0.22, (0, 0, z), M(vio), verts=8, bev=0.04)
            T.cyl(1.0 - z * 0.07, 0.06, (0, 0, z + 0.24), T.glow(vio, 2.0), verts=8, bev=0)
        T.cyl(1.25, 0.7, (0, 0, 7.8), M("#4a4a58", gloss=0.4), r2=0.8, verts=8, bev=0.08)           # anchor pod
        T.cyl(1.4, 0.15, (0, 0, 8.0), T.glow(vio, 1.6), verts=8, bev=0)
        # the tether: a crystal (digital) cable rising into the sky + a climber car
        Fc.crystal(0.14, 5.5, 0.1, n=4, loc=(0, 0, 8.5), col=vio, glow=1.6, seed=9)
        T.box((0.7, 0.7, 0.6), (0, 0, 11.0), M(white, gloss=0.3), bev=0.08)
        T.box((0.75, 0.75, 0.1), (0, 0, 11.3), T.glow(vio, 2), bev=0)
        for k in range(5):
            Fc.shard(0.18, (rng.uniform(-0.9, 0.9), rng.uniform(-0.3, 0.3), 9 + k * 1.0), vio, 2.0, rng)
        # dish
        T.cyl(0.9, 0.3, (1.6, -0.6, 1.0), M("#d8d4c8", gloss=0.3), r2=0.2, verts=16, bev=0.03, rot=(-45, 0, 30),
              origin_bottom=False)


# =============================================================== threats (B4)
def token_base(corp, rng):
    col, _ = CORP[corp]
    T.cyl(1.75, 0.35, (0, 0, -0.35), M("#3a3c42", gloss=0.2), verts=24, bev=0.1)
    T.cyl(1.8, 0.14, (0, 0, -0.1), M(col, stroke=0.2), verts=24, bev=0.04)


def threat(kind, rng):
    if kind == "bailiff":                      # armoured, slow, heavy (Solace repossession unit)
        corp = "solace"
        token_base(corp, rng)
        col = CORP[corp][0]
        T.box((2.2, 1.6, 1.1), (0, 0.1, 0.1), M("#4a5050", gloss=0.3, stroke=0.3), bev=0.2, wonk=0.04, rng=rng, taper=0.12)
        T.box((2.4, 0.6, 0.6), (0, -0.85, 0.15), M("#2e3034"), bev=0.15)                            # tracks
        T.box((2.4, 0.6, 0.6), (0, 1.05, 0.15), M("#2e3034"), bev=0.15)
        T.box((1.4, 1.2, 0.8), (0, 0.15, 1.2), M(col, stroke=0.3), bev=0.15, wonk=0.04, rng=rng)
        T.box((2.3, 0.25, 0.9), (0, -0.9, 0.9), M("#6a6e70", gloss=0.4, pattern="plank"), bev=0.06)   # ram plow
        T.box((0.9, 0.08, 0.18), (0, -0.62, 1.4), T.glow("#ff4a3a", 3), bev=0.01)                    # visor
        for sx in (-1, 1):
            T.cyl(0.12, 0.1, (sx * 0.95, -1.04, 0.95), M("#b8b4a8", gloss=0.8), verts=8, bev=0.02, rot=(90, 0, 0))
    elif kind == "courier":                    # fast, fragile (Meridian)
        corp = "meridian"
        token_base(corp, rng)
        col, soot = CORP[corp]
        T.box((0.7, 2.2, 0.35), (0, 0, 0.7), M(col, stroke=0.25), bev=0.15, taper=0.4, rot=(0, 0, 0))  # sleek hull
        T.box((0.5, 0.9, 0.3), (0, 0.25, 1.0), M("#2c3a42", gloss=0.8), bev=0.12, taper=0.4)
        for sx in (-1, 1):                                                                         # swept wings
            T.prism([(0, 0.6), (sx * 1.4, 1.2), (sx * 1.2, 1.5), (0, 1.0)], 0.08, (0, -0.2, 0.7), M(soot), bev=0.02)
        T.box((0.45, 0.45, 0.4), (0, 0.55, 0.35), M("#a8743a", pattern="plank"), bev=0.04)           # parcel
        for k in range(4):                                                                         # speed lines (crystal)
            Fc.crystal(0.05, 0.6, 0.6, n=3, loc=(rng.uniform(-0.6, 0.6), 1.6 + k * 0.1, 0.5 + k * 0.2), col=col,
                       glow=1.6, rot=(90, 0, 0), seed=k)
        T.box((0.3, 0.08, 0.1), (0, -1.1, 0.8), T.glow("#ffd080", 3), bev=0.01)
    else:                                      # customs agent: seals the link behind it (Meridian)
        corp = "meridian"
        token_base(corp, rng)
        col, soot = CORP[corp]
        T.box((1.0, 0.8, 1.3), (0, 0.2, 0.0), M("#2e3a4a", stroke=0.3), bev=0.2, wonk=0.04, rng=rng, taper=0.15)
        blob(0.42, (0, 0.2, 1.6), M(SKIN[0]), rng, name="head")
        T.cyl(0.55, 0.12, (0, 0.2, 1.9), M("#1e2a3a"), verts=12, bev=0.03)                          # cap
        T.box(( 0.6, 0.6, 0.35), (0, 0.15, 1.95), M("#1e2a3a"), bev=0.08)
        T.box((0.4, 0.05, 0.1), (0, -0.2, 1.62), T.glow(col, 2.5), bev=0.0)
        # the seal it drops behind: a barrier gate with a stamped seal + crystal lock
        for sx in (-1, 1):
            T.box((0.18, 0.18, 1.4), (sx * 1.15, 1.0, 0), M(col), bev=0.03)
        T.box((2.5, 0.12, 0.35), (0, 1.0, 1.0), M(col, pattern="plank", pat_scale=3), bev=0.03)
        T.box((2.5, 0.12, 0.35), (0, 1.0, 0.45), M("#2a2c30"), bev=0.03)
        Fc.cut_gem(0.32, 0.12, 0.05, n=6, loc=(0, 0.9, 0.75), col=col, glow=1.4, rot=(90, 0, 0), seed=2)
        T.box((0.7, 0.5, 0.35), (0.65, -0.3, 0.4), M("#8e3a2a"), bev=0.05, rot=(0, 0, -10))          # seal stamp
        T.cyl(0.08, 0.4, (0.65, -0.3, 0.75), M("#3a2420"), verts=8, bev=0)


# =============================================================== items (F2) + currencies
def daemon(rng):
    """Adrenal Loop: daemon program token - a painted metal coin with a crystal sigil (loop + heart pulse)."""
    T.cyl(1.6, 0.4, (0, 0, -0.2), M("#5a5866", gloss=0.4, stroke=0.25), verts=12, bev=0.1, wonk=0.02, rng=rng,
          rot=(90, 0, 0), origin_bottom=False)
    T.cyl(1.7, 0.25, (0, 0.05, 0), M("#c8a030", gloss=0.6), verts=12, bev=0.06, rot=(90, 0, 0), origin_bottom=False)
    T.cyl(1.25, 0.1, (0, -0.25, 0), M("#2a1c2c"), verts=24, bev=0.02, rot=(90, 0, 0), origin_bottom=False)
    pts = [(math.cos(a / 30 * math.tau) * 0.85, math.sin(a / 30 * math.tau) * 0.85) for a in range(31)]
    rib = Fc.facet_ribbon(pts, 0.2, 0.0, "#5fd8b0", glow=1.5, seed=3, thick=0.08)
    rib.rotation_euler = (math.radians(90), 0, 0)
    rib.location = (0, -0.32, 0)
    pulse = [(-0.6, 0.0), (-0.25, 0.0), (-0.1, 0.35), (0.05, -0.4), (0.2, 0.15), (0.3, 0.0), (0.6, 0.0)]
    rib2 = Fc.facet_ribbon(pulse, 0.12, 0.0, "#ff4a5a", glow=1.8, seed=5, thick=0.05)
    rib2.rotation_euler = (math.radians(90), 0, 0)
    rib2.location = (0, -0.34, 0)
    for k in range(2):                       # rarity pips: Uncommon = 2
        Fc.cut_gem(0.14, 0.07, 0.03, n=6, loc=(-0.2 + k * 0.4, -0.3, -1.4), col="#5fd8b0", glow=1.3, rot=(90, 0, 0),
                   seed=k)


def chip(rng):
    """Barbed Wire: firmware chip with pins, a crystal die, wrapped in painted barbed wire."""
    T.box((3.0, 2.2, 0.3), (0, 0, 0), M("#2e4a3a", stroke=0.3, gloss=0.2), bev=0.06, wonk=0.02, rng=rng)
    for i in range(7):
        for sy in (-1, 1):
            T.box((0.15, 0.45, 0.08), (-1.2 + i * 0.4, sy * 1.25, 0.05), M("#c8a030", gloss=0.7), bev=0.01)
    T.box((1.4, 1.2, 0.25), (0, 0, 0.3), M("#1e1e22", gloss=0.4), bev=0.05)
    Fc.cut_gem(0.42, 0.14, 0.06, n=4, loc=(0, 0, 0.62), col="#7ab8d8", glow=1.3, rot=(0, 0, 45), seed=1)
    for k in range(6):                       # traces
        T.box((0.8, 0.05, 0.02), (-1.0 + (k % 2) * 2.0, -0.7 + (k // 2) * 0.7, 0.16), M("#c8a030", flat=True), bev=0)
    # barbed wire loop
    for i in range(32):
        a = i / 32 * math.tau
        x, y = math.cos(a) * 1.75, math.sin(a) * 1.3
        T.cyl(0.035, 0.25, (x, y, 0.35 + 0.05 * math.sin(a * 6)), M("#6a6e70", gloss=0.5), verts=5, bev=0,
              rot=(90, 0, math.degrees(a)), origin_bottom=False)
        if i % 3 == 0:
            T.box((0.28, 0.03, 0.03), (x, y, 0.38), M("#6a6e70"), bev=0, rot=(0, 45, math.degrees(a) + 45))
            T.box((0.28, 0.03, 0.03), (x, y, 0.38), M("#6a6e70"), bev=0, rot=(0, -45, math.degrees(a) + 45))


def slice_tile(rng):
    """ATK 6 spinner slice for sale: painted wedge on a crate tray with a crystal glyph."""
    T.box((3.4, 2.4, 0.3), (0, 0.2, -0.3), M("#6a5038", pattern="plank", stroke=0.3), bev=0.06, wonk=0.03, rng=rng)
    pts = [(0, -0.9)] + [(math.cos(math.radians(a)) * 2.5, math.sin(math.radians(a)) * 2.5 - 0.9) for a in range(62, 119, 4)]
    T.prism(pts, 0.35, (0, 0, 0), M("#cc442e", stroke=0.25, gloss=0.3), bev=0.06)
    Fc.cut_gem(0.28, 0.12, 0.04, n=3, loc=(0, 0.6, 0.4), col="#ff8a7a", glow=1.3, rot=(0, 0, 90), seed=6)


def currency(kind, rng):
    if kind == "cycles":       # run currency: a stamped coin with a cycle arrow
        T.cyl(1.2, 0.35, (0, 0, 0), M("#d9a032", gloss=0.6, stroke=0.2), verts=10, bev=0.1, rot=(90, 0, 0),
              origin_bottom=False, wonk=0.02, rng=rng)
        pts = [(math.cos(a / 20 * 4.5) * 0.6, math.sin(a / 20 * 4.5) * 0.6) for a in range(21)]
        r = Fc.facet_ribbon(pts, 0.16, 0.0, "#fff0b0", glow=1.0, seed=1, thick=0.05)
        r.rotation_euler = (math.radians(90), 0, 0)
        r.location = (0, -0.2, 0)
        T.prism([(0.55, 0.0), (0.85, 0.0), (0.7, -0.3)], 0.08, (0, -0.2, 0), M("#fff0b0"), bev=0, rot=(90, 0, 0))
    elif kind == "schematics":  # campaign currency: a rolled blueprint
        T.cyl(0.55, 2.2, (-1.1, 0, 0), M("#2e5a8a", stroke=0.3), verts=10, bev=0.06, rot=(0, 90, 0), origin_bottom=False)
        T.box((1.6, 0.06, 1.3), (0.4, -0.2, -0.2), M("#3a6a9a", stroke=0.3), bev=0.03, rot=(0, -6, 0))
        for k in range(4):
            T.box((1.2, 0.02, 0.04), (0.4, -0.25, -0.5 + k * 0.25), M("#d8e8f8", flat=True), bev=0)
        T.box((0.2, 0.7, 0.2), (-0.4, 0, 0), M("#c03a2a"), bev=0.02)
    elif kind == "ram":         # combat energy: a cut crystal
        Fc.cut_gem(1.0, 0.45, 0.9, n=6, loc=(0, 0, 0), col="#3ff0ff", glow=1.25, rot=(70, 0, 0), seed=2)
    else:                       # heat: a painted flame on a gauge
        T.cyl(1.0, 0.3, (0, 0.1, 0), M("#3a3c42", gloss=0.3), verts=12, bev=0.08, rot=(90, 0, 0), origin_bottom=False)
        T.prism([(-0.55, -0.6), (0.55, -0.6), (0.62, 0.0), (0.2, 0.4), (0.25, 0.9), (-0.1, 0.5), (-0.35, 0.8), (-0.6, 0.1)],
                0.3, (0, -0.25, 0), M("#ff6a2a", stroke=0.25), bev=0.06, rot=(90, 0, 0))
        T.prism([(-0.25, -0.5), (0.25, -0.5), (0.3, -0.1), (0.05, 0.3), (-0.25, -0.05)], 0.3, (0, -0.42, 0),
                M("#ffd040"), bev=0.04, rot=(90, 0, 0))


# =============================================================== card art props (E5)
def card_art(kind, rng):
    if kind == "backspin":
        T.cyl(1.6, 0.3, (0, 0, 0), M("#3a3c42"), verts=24, bev=0.06, rot=(90, 0, 0), origin_bottom=False)
        cols = ["#cc442e", "#2a9e94", "#d9a032", "#cc442e", "#2a9e94", "#8a50c8"]
        for i, c in enumerate(cols):
            a0, a1 = i / 6 * math.tau + 0.03, (i + 1) / 6 * math.tau - 0.03
            pts = [(0, 0)] + [(math.cos(a0 + (a1 - a0) * k / 6) * 1.35, math.sin(a0 + (a1 - a0) * k / 6) * 1.35) for k in range(7)]
            T.prism(pts, 0.15, (0, -0.15, 0), M(c), bev=0.03, rot=(90, 0, 0))
        T.cyl(0.3, 0.2, (0, -0.32, 0), M("#c8a030", gloss=0.6), verts=12, bev=0.04, rot=(90, 0, 0), origin_bottom=False)
        # counter-clockwise crystal arrow arc
        pts = [(math.cos(math.radians(a)) * 2.0, math.sin(math.radians(a)) * 2.0) for a in range(20, 300, 10)]
        r = Fc.facet_ribbon(pts, 0.3, 0.0, "#3ff0ff", glow=1.5, seed=2, thick=0.1)
        r.rotation_euler = (math.radians(90), 0, 0)
        r.location = (0, -0.4, 0)
        a = math.radians(20)
        Fc.crystal(0.32, 0.5, 0.05, n=3, loc=(math.cos(a) * 2.0, -0.4, math.sin(a) * 2.0), col="#3ff0ff", glow=1.5,
                   rot=(0, 160, 0), seed=3)
    elif kind == "arcflash":
        for sx in (-1, 1):
            T.cyl(0.35, 2.2, (sx * 1.6, 0, -1.2), M("#4a4e52", gloss=0.3), r2=0.2, verts=8, bev=0.05)
            T.cyl(0.4, 0.3, (sx * 1.6, 0, 1.0), M("#c8a030", gloss=0.5), verts=8, bev=0.04)
        zig = [(-1.6, 1.15), (-1.0, 1.6), (-0.6, 0.9), (0.0, 1.5), (0.5, 0.8), (1.0, 1.4), (1.6, 1.15)]
        r = Fc.facet_ribbon(zig, 0.28, 0.0, "#d0e8ff", glow=2.2, seed=4, thick=0.1)
        r.rotation_euler = (math.radians(90), 0, 0)
        r.location = (0, -0.3, 0)
        for k in range(10):
            Fc.shard(0.1, (rng.uniform(-2, 2), -0.4, rng.uniform(0.5, 2.0)), "#ffe080", 2.0, rng)
        for sx in (-1.4, 0.0, 1.4):           # three enemy silhouettes zapped below
            blob(0.35, (sx * 0.8, 0.3, -0.9), M("#2a2c30"), rng, (1, 0.7, 1.2), name="foe")
    else:   # bulwark
        for k in range(5):
            T.box((0.9, 0.5, 2.4 - abs(k - 2) * 0.3), (-1.8 + k * 0.9, 0, -1.2), M(rng.choice(("#5a6068", "#4e5a58", "#6a5a48")),
                  pattern="plank", stroke=0.3), bev=0.08, wonk=0.05, rng=rng, rot=(0, 0, rng.uniform(-4, 4)))
        T.box((4.6, 0.6, 0.25), (0, -0.05, 0.5), M("#e8c030"), bev=0.05)
        Fc.cut_gem(0.9, 0.3, 0.1, n=6, loc=(0, -0.45, -0.2), col="#2a9e94", glow=1.3, rot=(90, 0, 0), seed=7)


def card_back(rng):
    T.box((2.0, 0.2, 2.0), (0, 0, -1.0), M("#2a2c30", gloss=0.3), bev=0.15, rot=(0, 45, 0))
    blob(0.55, (0, -0.2, 0.0), M("#cc442e", stroke=0.25), rng, (1.0, 0.6, 1.1), subd=1, smooth=False, name="fist")
    for k in range(4):
        T.box((0.22, 0.4, 0.3), (-0.33 + k * 0.22, -0.4, 0.45), M("#cc442e"), bev=0.06)
    Fc.cut_gem(0.25, 0.1, 0.05, n=6, loc=(0, -0.5, -0.7), col="#3ff0ff", glow=1.4, rot=(90, 0, 0), seed=1)


BUILDERS = {}
for c in ("breaker", "ghost"):
    for s in ("neutral", "hurt", "triumphant", "flatlined"):
        BUILDERS["op_%s_%s" % (c, s)] = (lambda c=c, s=s: (lambda rng: bust(c, s, rng)))()
for k in ("manifest", "adjuster", "drone"):
    BUILDERS["en_" + k] = (lambda k=k: (lambda rng: enemy(k, rng)))()
for k in ("meridian", "solace"):
    BUILDERS["bz_" + k] = (lambda k=k: (lambda rng: bezel(k, rng)))()
for k in ("ziggurat", "pyramid", "tether"):
    BUILDERS["lm_" + k] = (lambda k=k: (lambda rng: landmark(k, rng)))()
for k in ("bailiff", "courier", "customs"):
    BUILDERS["th_" + k] = (lambda k=k: (lambda rng: threat(k, rng)))()
for k in ("cycles", "schematics", "ram", "heat"):
    BUILDERS["cu_" + k] = (lambda k=k: (lambda rng: currency(k, rng)))()
for k in ("backspin", "arcflash", "bulwark"):
    BUILDERS["ca_" + k] = (lambda k=k: (lambda rng: card_art(k, rng)))()
BUILDERS["ca_back"] = card_back
BUILDERS["it_daemon"] = daemon
BUILDERS["it_chip"] = chip
BUILDERS["it_slice"] = slice_tile
BUILDERS["gem_ram"] = lambda rng: Fc.cut_gem(1.0, 0.4, 0.15, n=6, loc=(0, 0, 0), col="#3ff0ff", glow=1.25, rot=(90, 0, 0),
                                             seed=3, table=0.6)
