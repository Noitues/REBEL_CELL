"""Physical spinner: machined bezel, glass dome, emissive slice inlays, hub screen, needle, HP arc.

The spinner is built in its own local space (disc facing +Z, radius 1) under an Empty, so it can be
parented to the camera and placed by pixel coordinates.
"""
import bpy
import bmesh
import math
import random
from mathutils import Vector
import diorama_lib as D

SLICE_COL = {"ATK": "#ff3da8", "CRIT": "#ff3da8", "DEF": "#5ce1ff", "EVD": "#7be07b", "AFF": "#c85aff",
             "DPL": "#b08cff", "MISS": "#6a6a6a"}


def ring_mesh(name, r_in, r_out, z0, z1, a0=0.0, a1=2 * math.pi, segs=96, mat=None, parent=None, bevel=0.0):
    full = abs((a1 - a0) - 2 * math.pi) < 1e-6
    n = segs if full else max(2, int(segs * (a1 - a0) / (2 * math.pi)) + 1)
    verts, faces = [], []
    for k in range(n + (0 if full else 1)):
        a = a0 + (a1 - a0) * k / n
        ca, sa = math.cos(a), math.sin(a)
        verts += [(r_in * ca, r_in * sa, z0), (r_out * ca, r_out * sa, z0), (r_out * ca, r_out * sa, z1), (r_in * ca, r_in * sa, z1)]
    cnt = n if full else n
    rings = len(verts) // 4
    for k in range(cnt):
        o = k * 4
        q = ((k + 1) % rings) * 4
        faces += [(o, q, q + 1, o + 1), (o + 1, q + 1, q + 2, o + 2), (o + 2, q + 2, q + 3, o + 3), (o + 3, q + 3, q, o)]
    if not full:
        faces += [(0, 1, 2, 3), ((rings - 1) * 4 + 3, (rings - 1) * 4 + 2, (rings - 1) * 4 + 1, (rings - 1) * 4)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    if mat:
        me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if bevel > 0:
        md = ob.modifiers.new("bev", "BEVEL")
        md.width = bevel
        md.segments = 3
        md.limit_method = "ANGLE"
    for p in ob.data.polygons:
        p.use_smooth = False
    if parent:
        ob.parent = parent
    return ob


def _child(ob, parent):
    ob.parent = parent
    return ob


def build_spinner(name, slices, owner="op", hub_text="BREAKER", hp=(60, 60), forecast_loss=0,
                  needle_tick=0.0, fonts=None, seed=1, corp_col="#ff8c1a"):
    """slices: list of (type, ticks, value). Returns the root Empty (radius 1 in local units)."""
    rng = random.Random(seed)
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    total = sum(t for _, t, _ in slices)
    op = owner == "op"
    # materials
    if op:
        bez = D.mat_pbr(name + "_bez", "#474c57", rough=0.32, metal=1.0)
        rim = D.mat_emit(name + "_rim", "#ff3da8", 7.0)
    else:
        bez = D.mat_pbr(name + "_bez", "#8a4a16", rough=0.26, metal=1.0)
        rim = D.mat_emit(name + "_rim", corp_col, 7.0)
    back = D.mat_pbr(name + "_back", "#0e1118", rough=0.5, metal=0.6)
    well = D.mat_pbr(name + "_well", "#05070c", rough=0.4, metal=0.2)
    tickm = D.mat_emit(name + "_tick", "#dfe8ff", 3.0)
    glass = D.mat_glass(name + "_glass", "#bfe8ff", alpha=0.10, rough=0.03)
    hubm = D.mat_pbr(name + "_hub", "#0a0e16", rough=0.25, metal=0.4)
    hubring = D.mat_emit(name + "_hubring", "#5ce1ff" if op else corp_col, 5.0)
    white = D.mat_emit(name + "_white", "#f2f6ff", 4.0)
    ink = D.mat_pbr(name + "_ink", "#0a0a0a", rough=0.6)
    needle = D.mat_emit(name + "_needle", "#d4ff00", 12.0)
    cap = D.mat_pbr(name + "_cap", "#c9ccd4", rough=0.2, metal=1.0)

    # back plate and slice well
    _child(D.cyl(name + "_backplate", (0, 0, -0.33), 1.2, 0.1, back, 96), root)
    _child(D.cyl(name + "_well", (0, 0, -0.03), 0.98, 0.04, well, 96), root)
    # bezel: machined ring with a stepped profile + emissive rim channel
    _child(ring_mesh(name + "_bezel", 0.97, 1.17, -0.3, 0.13, mat=bez, bevel=0.012), root)
    _child(ring_mesh(name + "_bezel_step", 1.0, 1.1, 0.13, 0.17, mat=bez, bevel=0.006), root)
    _child(ring_mesh(name + "_rimchan", 1.17, 1.19, -0.12, -0.04, mat=rim), root)
    # 30 ticks machined into the bezel top
    for k in range(30):
        a = math.pi / 2 - 2 * math.pi * k / 30
        big = k % 5 == 0
        L = 0.07 if big else 0.04
        t = D.box(name + "_tick", (math.cos(a) * (1.1 - L / 2 - 0.005), math.sin(a) * (1.1 - L / 2 - 0.005), 0.172),
                  (L, 0.012 if not big else 0.018, 0.006), tickm, rot=(0, 0, a))
        _child(t, root)
    if not op:
        # hostile notched edge + corp stripe pattern (Meridian: container stripes)
        for k in range(24):
            a = 2 * math.pi * (k + 0.5) / 24
            t = D.box(name + "_notch", (math.cos(a) * 1.21, math.sin(a) * 1.21, 0.03), (0.08, 0.09, 0.14), bez, rot=(0, 0, a))
            _child(t, root)
        for k in range(48):
            if k % 2:
                continue
            a0 = 2 * math.pi * k / 48
            _child(ring_mesh(name + "_stripe", 1.0, 1.1, 0.171, 0.176, a0, a0 + 2 * math.pi / 96, 8,
                             D.mat_emit(name + f"_st{k}", corp_col, 1.2)), root)
    else:
        # operative: riveted plates (Breaker ornament)
        for k in range(12):
            a = 2 * math.pi * (k + 0.5) / 12
            _child(D.cyl(name + "_rivet", (math.cos(a) * 1.135, math.sin(a) * 1.135, 0.14), 0.018, 0.03, cap, 10), root)

    # slice inlays (angles clockwise from 12 o'clock)
    acc = 0
    spill = []
    for typ, ticks, val in slices:
        a_start = math.pi / 2 - 2 * math.pi * acc / total
        a_end = math.pi / 2 - 2 * math.pi * (acc + ticks) / total
        gap = 0.012
        col = SLICE_COL[typ]
        body = D.mat_pbr(name + f"_sl{acc}", col, rough=0.35, emit=col, emit_str=0.45 if typ != "MISS" else 0.1)
        edge = D.mat_emit(name + f"_se{acc}", col, 3.0 if typ != "MISS" else 0.5)
        # frosted body (slightly recessed) and a bright outer lip
        _child(ring_mesh(name + "_slice", 0.47, 0.9, -0.01, 0.02, a_end + gap, a_start - gap, 120, body), root)
        _child(ring_mesh(name + "_slip", 0.9, 0.95, -0.01, 0.045, a_end + gap, a_start - gap, 120, edge), root)
        # divider fins between slices (raised metal)
        dv = D.box(name + "_div", (math.cos(a_start) * 0.72, math.sin(a_start) * 0.72, 0.02), (0.5, 0.018, 0.07), cap,
                   rot=(0, 0, a_start))
        _child(dv, root)
        mid = (a_start + a_end) / 2
        if val is not None:
            tx = D.text_obj(name + "_val", str(val), (math.cos(mid) * 0.72, math.sin(mid) * 0.72, 0.05), 0.2,
                            ink if typ != "MISS" else white, font=fonts.get("num") if fonts else None, extrude=0.008)
            _child(tx, root)
        if typ != "MISS":
            spill.append((mid, col))
        acc += ticks
    # light spill from inlays onto bezel, needle and glass (feedback 10)
    for k, (mid, col) in enumerate(spill):
        l = D.point_light(name + "_spill", (math.cos(mid) * 0.8, math.sin(mid) * 0.8, 0.12), col, 6.0, 0.15)
        l.data.use_soft_falloff = True
        _child(l, root)

    # hub
    _child(D.cyl(name + "_hub", (0, 0, 0.1), 0.44, 0.1, hubm, 64), root)
    _child(ring_mesh(name + "_hubring", 0.42, 0.46, 0.1, 0.16, mat=hubring), root)
    _child(D.cyl(name + "_hubscreen", (0, 0, 0.152), 0.38, 0.005, D.mat_emit(name + "_scr", "#0d1b2e", 1.0), 64), root)
    lines = hub_text.split("\n")
    for k, ln in enumerate(lines):
        tx = D.text_obj(name + "_hubtxt", ln, (0, 0.05 - k * 0.12 + (len(lines) - 1) * 0.04, 0.16), (0.1 if len(ln) < 10 else 0.075) if k == 0 else 0.055,
                        white if k == 0 else D.mat_emit(name + "_sub", "#9fb6d0", 2.0), font=fonts.get("mono") if fonts else None)
        _child(tx, root)

    # stylised glint on the glass: a soft reflected window of the key light
    gl = D.mat_emit(name + "_glint", "#e8f4ff", 1.2, alpha=0.07)
    _child(ring_mesh(name + "_glint", 0.74, 0.8, 0.27, 0.271, math.radians(105), math.radians(150), 40, gl), root)
    _child(ring_mesh(name + "_glint2", 0.88, 0.92, 0.2, 0.201, math.radians(95), math.radians(165), 40, gl), root)
    # glass dome over everything inside the bezel
    me = bpy.data.meshes.new(name + "_dome")
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=24, radius=1.0)
    for v in bm.verts:
        v.co.x *= 0.975
        v.co.y *= 0.975
        v.co.z = max(0.0, v.co.z) * 0.16 + 0.1
    bm.to_mesh(me)
    bm.free()
    me.materials.append(glass)
    for p in me.polygons:
        p.use_smooth = True
    dome = bpy.data.objects.new(name + "_dome", me)
    bpy.context.scene.collection.objects.link(dome)
    _child(dome, root)

    # needle (under the glass, over the hub)
    a = math.pi / 2 - 2 * math.pi * needle_tick / total
    nd = bpy.data.objects.new(name + "_needle_root", None)
    bpy.context.scene.collection.objects.link(nd)
    nd.parent = root
    nd.rotation_euler = (0, 0, a)
    nme = bpy.data.meshes.new(name + "_needle")
    nme.from_pydata([(0, -0.03, 0), (0.98, -0.006, 0), (0.98, 0.006, 0), (0, 0.03, 0),
                     (0, -0.03, 0.02), (0.98, -0.006, 0.02), (0.98, 0.006, 0.02), (0, 0.03, 0.02)], [],
                    [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)])
    nme.materials.append(needle)
    nob = bpy.data.objects.new(name + "_needle", nme)
    bpy.context.scene.collection.objects.link(nob)
    nob.location = (0, 0, 0.06)
    nob.parent = nd
    cw = D.cyl(name + "_cw", (-0.55, 0, 0.075), 0.06, 0.03, cap, 24)
    cw.parent = nd
    pc = None

    # HP arc: thick segmented arc under the wheel (feedback: HP never under the needle)
    seg = 24
    a0, a1 = math.radians(215), math.radians(325)
    frac = hp[0] / hp[1]
    lost = forecast_loss / hp[1]
    gain = D.mat_emit(name + "_hp", "#7be07b", 2.2)
    ghost = D.mat_emit(name + "_hpghost", "#ff4433", 2.2)
    empty = D.mat_pbr(name + "_hpempty", "#1a1f28", rough=0.5, metal=0.5)
    for k in range(seg):
        s0 = a0 + (a1 - a0) * k / seg
        s1 = a0 + (a1 - a0) * (k + 1) / seg - 0.012
        f = (k + 0.5) / seg
        m = gain if f <= frac - lost else (ghost if f <= frac else empty)
        _child(ring_mesh(name + "_hpseg", 1.27, 1.37, -0.03, 0.03, s0, s1, 8, m), root)
    return root


def place_on_camera(root, cam, px, py, radius_px, depth, tilt=(0.0, 0.0, 0.0), res=(1920, 1080)):
    """Parent the spinner to an ortho camera so it lands at pixel (px, py) with a pixel radius."""
    S = cam.data.ortho_scale
    upx = S / res[0]
    root.parent = cam
    root.location = ((px - res[0] / 2) * upx, (res[1] / 2 - py) * upx, -depth)
    root.rotation_euler = tilt
    root.scale = (radius_px * upx,) * 3
    return root


def binary_shards(cam, px, py, count, seed, spread=(100, 175), dist=(40, 360), size_px=(14, 40), depth=18.0,
                  res=(1920, 1080), fonts=None):
    """0/1 shards thrown from a hit point (feedback 5): 3D text, tumbling, with streaks back to the hit."""
    rng = random.Random(seed)
    S = cam.data.ortho_scale
    upx = S / res[0]
    hot = D.mat_emit("shard_hot", "#fff4f6", 5.0)
    harm = D.mat_emit("shard_harm", "#ff4433", 4.0)
    pink = D.mat_emit("shard_pink", "#ff3da8", 4.0)
    streak = D.mat_emit("shard_streak", "#ff6a55", 1.5, alpha=0.22)
    hub = bpy.data.objects.new("shards", None)
    bpy.context.scene.collection.objects.link(hub)
    hub.parent = cam
    hub.location = ((px - res[0] / 2) * upx, (res[1] / 2 - py) * upx, -depth)
    for k in range(count):
        ang = math.radians(rng.uniform(*spread))
        dd = rng.uniform(*dist) * (0.4 + 0.6 * rng.random())
        x, y = math.cos(ang) * dd * upx, math.sin(ang) * dd * upx
        sz = rng.uniform(*size_px) * (1.15 - 0.6 * dd / dist[1]) * upx
        mat = rng.choice([hot, harm, harm, harm, pink])
        t = D.text_obj("shard", rng.choice("01"), (x, y, rng.uniform(-1, 1)), sz, mat,
                       rot=(rng.uniform(-0.45, 0.45), rng.uniform(-0.45, 0.45), rng.uniform(-0.5, 0.5)),
                       extrude=sz * 0.18, font=fonts.get("mono") if fonts else None)
        t.parent = hub
        # streak: a thin tapered quad from the shard back toward the hit point
        L = min(dd * 0.55, 140) * upx
        ux, uy = math.cos(ang), math.sin(ang)
        nx, ny = -uy, ux
        w = sz * 0.12
        me = bpy.data.meshes.new("streak")
        me.from_pydata([(x - ux * sz * 0.4 + nx * w, y - uy * sz * 0.4 + ny * w, -0.2),
                        (x - ux * sz * 0.4 - nx * w, y - uy * sz * 0.4 - ny * w, -0.2),
                        (x - ux * (L + sz * 0.4), y - uy * (L + sz * 0.4), -0.2)], [], [(0, 1, 2)])
        me.materials.append(streak)
        so = bpy.data.objects.new("streak", me)
        bpy.context.scene.collection.objects.link(so)
        so.parent = hub
    # hit flash + light that spills onto the enemy bezel
    fl = D.cyl("hitflash", (0, 0, 0.5), 22 * upx, 0.01, D.mat_emit("flash", "#fff0f4", 25.0), 32,
               rot=(0, 0, 0))
    fl.parent = hub
    ring = ring_mesh("hitring", 30 * upx, 36 * upx, 0.3, 0.32, mat=D.mat_emit("hitring_m", "#ff4433", 12.0))
    ring.parent = hub
    l = D.point_light("hitlight", (0, 0, 1.5), "#ff5a4a", 900.0, 0.3)
    l.parent = hub
    return hub
