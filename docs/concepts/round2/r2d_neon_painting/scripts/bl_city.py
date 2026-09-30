"""The city: seeded blocks, landmark buildings, neon, traffic, shards, fog, nav overlay."""
import math
import random
import bpy
from mathutils import Vector

import layout as L
from bl_kit import (m_emit, m_pbr, m_screen, m_volume, _nodes, _set, rgba, ramp, MeshBuf,
                    mesh_obj, curve_obj, arc, swirl, fog_box, point_light, spot_light, sun,
                    world)

MOODS = {
    "day": dict(
        sky_top=(0.25, 0.32, 0.95), sky_hor=(0.95, 0.55, 0.7), sky_str=0.42,
        wall_lo=(0.16, 0.10, 0.40), wall_hi=(0.95, 0.55, 0.62), glass=(0.18, 0.30, 0.75),
        win_str=0.35, lit=0.25, win_pal=[(1.0, 0.75, 0.45), (0.6, 0.9, 1.0), (1.0, 0.55, 0.8)],
        neon=0.45, trims=[(1.0, 0.35, 0.7), (0.3, 0.85, 1.0), (1.0, 0.6, 0.2)],
        ground=(0.16, 0.10, 0.30), slab=(0.30, 0.20, 0.45),
        fog=(1.0, 0.75, 0.85), fog_d=0.0015, fog_e=(1.0, 0.6, 0.75), fog_es=0.0,
        far=(1.0, 0.7, 0.8), far_d=0.012, far_e=(1.0, 0.5, 0.55), far_es=0.03,
        traffic=0.6, shard_e=0.5, frag=1.2, halo=1.1, spill=0.0, spill_e=0.05,
        halo_pal=[(1.0, 0.95, 0.9), (1.0, 0.45, 0.7), (1.0, 0.6, 0.25), (0.4, 0.8, 1.0)],
        path=1.0),
    "night": dict(
        sky_top=(0.015, 0.005, 0.04), sky_hor=(0.30, 0.04, 0.22), sky_str=0.45,
        wall_lo=(0.015, 0.01, 0.04), wall_hi=(0.10, 0.06, 0.20), glass=(0.02, 0.02, 0.06),
        win_str=2.2, lit=0.42, win_pal=[(1.0, 0.55, 0.18), (0.2, 0.85, 1.0), (1.0, 0.2, 0.6), (1.0, 0.9, 0.7)],
        neon=1.0, trims=[(1.0, 0.1, 0.55), (0.1, 0.8, 1.0), (1.0, 0.45, 0.05)],
        ground=(0.02, 0.012, 0.04), slab=(0.04, 0.03, 0.07),
        fog=(0.6, 0.4, 0.9), fog_d=0.0035, fog_e=(0.35, 0.05, 0.4), fog_es=0.0015,
        far=(0.6, 0.3, 0.7), far_d=0.012, far_e=(0.8, 0.15, 0.45), far_es=0.012,
        traffic=2.2, shard_e=1.0, frag=2.5, halo=2.2, spill=1.0, spill_e=0.17,
        halo_pal=[(1.0, 0.9, 0.95), (1.0, 0.25, 0.6), (1.0, 0.5, 0.12), (0.3, 0.7, 1.0)],
        path=1.0),
    "alarm": dict(
        sky_top=(0.03, 0.0, 0.015), sky_hor=(0.35, 0.02, 0.06), sky_str=0.3,
        wall_lo=(0.012, 0.005, 0.02), wall_hi=(0.08, 0.03, 0.08), glass=(0.02, 0.01, 0.03),
        win_str=1.8, lit=0.3, win_pal=[(1.0, 0.25, 0.08), (1.0, 0.55, 0.1), (1.0, 0.08, 0.2), (0.9, 0.8, 0.7)],
        neon=0.9, trims=[(1.0, 0.05, 0.12), (1.0, 0.35, 0.05), (1.0, 0.1, 0.4)],
        ground=(0.025, 0.008, 0.02), slab=(0.05, 0.02, 0.04),
        fog=(0.75, 0.6, 0.7), fog_d=0.009, fog_e=(0.5, 0.02, 0.06), fog_es=0.0008,
        far=(0.8, 0.3, 0.35), far_d=0.014, far_e=(0.9, 0.08, 0.1), far_es=0.015,
        traffic=1.6, shard_e=0.9, frag=2.0, halo=2.4,  spill=1.0, spill_e=0.2,
        halo_pal=[(1.0, 0.85, 0.7), (1.0, 0.1, 0.15), (1.0, 0.4, 0.05), (1.0, 0.15, 0.4)],
        path=1.0),
}

LANDMARKS = {
    "spire": (-27.5, 104.5),
    "arco": (38.5, 115.5),
    "twin_a": (-60.5, 71.5),
    "twin_b": (-60.5, 82.5),
    "halo": (0.0, 66.0, 25.0),
    "screen": (60.5, 60.5),
}


def building_material(M):
    mat = bpy.data.materials.new("bldg")
    nodes, links = _nodes(mat)
    out = nodes.new("ShaderNodeOutputMaterial")
    p = nodes.new("ShaderNodeBsdfPrincipled")
    tc = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tc.outputs["Object"], sep.inputs[0])
    h = nodes.new("ShaderNodeMath"); h.operation = "ADD"
    links.new(sep.outputs["X"], h.inputs[0]); links.new(sep.outputs["Y"], h.inputs[1])
    vec = nodes.new("ShaderNodeCombineXYZ")
    links.new(h.outputs[0], vec.inputs["X"]); links.new(sep.outputs["Z"], vec.inputs["Y"])
    br = nodes.new("ShaderNodeTexBrick")
    br.offset = 0.0
    br.squash = 1.0
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Mortar Size"].default_value = 0.32
    br.inputs["Brick Width"].default_value = 0.8
    br.inputs["Row Height"].default_value = 1.3
    links.new(vec.outputs[0], br.inputs["Vector"])
    win = nodes.new("ShaderNodeMath"); win.operation = "SUBTRACT"
    win.inputs[0].default_value = 1.0
    links.new(br.outputs["Factor"], win.inputs[1])
    snap = nodes.new("ShaderNodeVectorMath"); snap.operation = "SNAP"
    snap.inputs[1].default_value = (0.8, 1.3, 1.0)
    links.new(vec.outputs[0], snap.inputs[0])
    wn = nodes.new("ShaderNodeTexWhiteNoise")
    links.new(snap.outputs[0], wn.inputs["Vector"])
    lit = nodes.new("ShaderNodeMath"); lit.operation = "GREATER_THAN"
    lit.inputs[1].default_value = 1.0 - M["lit"]
    links.new(wn.outputs["Value"], lit.inputs[0])
    off = nodes.new("ShaderNodeVectorMath"); off.operation = "ADD"
    off.inputs[1].default_value = (3.3, 7.7, 1.1)
    links.new(snap.outputs[0], off.inputs[0])
    wn2 = nodes.new("ShaderNodeTexWhiteNoise")
    links.new(off.outputs[0], wn2.inputs["Vector"])
    pal = M["win_pal"]
    wr = ramp(nodes, [(i / len(pal), c) for i, c in enumerate(pal)], "CONSTANT")
    links.new(wn2.outputs["Value"], wr.inputs[0])
    geo = nodes.new("ShaderNodeNewGeometry")
    sn = nodes.new("ShaderNodeSeparateXYZ")
    links.new(geo.outputs["Normal"], sn.inputs[0])
    ab = nodes.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"
    links.new(sn.outputs["Z"], ab.inputs[0])
    fac = nodes.new("ShaderNodeMath"); fac.operation = "LESS_THAN"
    fac.inputs[1].default_value = 0.5
    links.new(ab.outputs[0], fac.inputs[0])
    m1 = nodes.new("ShaderNodeMath"); m1.operation = "MULTIPLY"
    links.new(win.outputs[0], m1.inputs[0]); links.new(fac.outputs[0], m1.inputs[1])
    bn = nodes.new("ShaderNodeTexNoise")
    bn.inputs["Scale"].default_value = 0.045
    links.new(tc.outputs["Object"], bn.inputs["Vector"])
    bm = nodes.new("ShaderNodeMath"); bm.operation = "GREATER_THAN"
    bm.inputs[1].default_value = 0.44
    links.new(bn.outputs["Fac"], bm.inputs[0])
    lit2 = nodes.new("ShaderNodeMath"); lit2.operation = "MULTIPLY"
    links.new(lit.outputs[0], lit2.inputs[0]); links.new(bm.outputs[0], lit2.inputs[1])
    m2 = nodes.new("ShaderNodeMath"); m2.operation = "MULTIPLY"
    links.new(m1.outputs[0], m2.inputs[0]); links.new(lit2.outputs[0], m2.inputs[1])
    m3 = nodes.new("ShaderNodeMath"); m3.operation = "MULTIPLY"
    m3.inputs[1].default_value = M["win_str"]
    links.new(m2.outputs[0], m3.inputs[0])
    # wall colour: vertical painted gradient + per-block tint
    zr = nodes.new("ShaderNodeMapRange")
    zr.inputs["From Max"].default_value = 55.0
    links.new(sep.outputs["Z"], zr.inputs["Value"])
    gr = ramp(nodes, [(0.0, M["wall_lo"]), (1.0, M["wall_hi"])])
    links.new(zr.outputs["Result"], gr.inputs[0])
    mix = nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    links.new(m1.outputs[0], mix.inputs["Factor"])
    links.new(gr.outputs[0], mix.inputs[6])
    mix.inputs[7].default_value = rgba(M["glass"])
    links.new(mix.outputs[2], p.inputs["Base Color"])
    rr = nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = 0.55
    rr.inputs["To Max"].default_value = 0.12
    links.new(m1.outputs[0], rr.inputs["Value"])
    links.new(rr.outputs["Result"], p.inputs["Roughness"])
    _set(p, "Metallic", 0.25)
    # emission = window colour * window strength + neon spill (hue by facing, fades with height)
    wv = nodes.new("ShaderNodeVectorMath"); wv.operation = "SCALE"
    links.new(wr.outputs[0], wv.inputs[0]); links.new(m3.outputs[0], wv.inputs["Scale"])
    nx = nodes.new("ShaderNodeMapRange")
    nx.inputs["From Min"].default_value = -1.0
    links.new(sn.outputs["X"], nx.inputs["Value"])
    sr = ramp(nodes, [(0.0, M["trims"][2]), (0.5, (0.45, 0.12, 1.0)), (1.0, M["trims"][0])])
    links.new(nx.outputs["Result"], sr.inputs[0])
    zf = nodes.new("ShaderNodeMapRange")
    zf.inputs["From Max"].default_value = 30.0
    zf.inputs["To Min"].default_value = M.get("spill_e", 0.0)
    zf.inputs["To Max"].default_value = 0.0
    links.new(sep.outputs["Z"], zf.inputs["Value"])
    sf = nodes.new("ShaderNodeMath"); sf.operation = "MULTIPLY"
    links.new(zf.outputs["Result"], sf.inputs[0]); links.new(fac.outputs[0], sf.inputs[1])
    sv = nodes.new("ShaderNodeVectorMath"); sv.operation = "SCALE"
    links.new(sr.outputs[0], sv.inputs[0]); links.new(sf.outputs[0], sv.inputs["Scale"])
    em = nodes.new("ShaderNodeVectorMath"); em.operation = "ADD"
    links.new(wv.outputs[0], em.inputs[0]); links.new(sv.outputs[0], em.inputs[1])
    links.new(em.outputs[0], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = 1.0
    links.new(p.outputs[0], out.inputs["Surface"])
    return mat


def _occlusion_samples():
    pts = []
    for a, b in L.EDGES:
        na = next(n for n in L.NODES if n[0] == a)
        nb = next(n for n in L.NODES if n[0] == b)
        poly = L.edge_polyline(L.node_world(na), L.node_world(nb))
        for (x0, y0), (x1, y1) in zip(poly, poly[1:]):
            ln = math.hypot(x1 - x0, y1 - y0)
            k = max(1, int(ln / 0.7))
            for s in range(k + 1):
                t = s / k
                pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    for n in L.NODES:
        x, y = L.node_world(n)
        rr = 3.2
        pts.append((x, y))
        for k in range(12):
            a = k * math.pi / 6
            pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
        for dz in range(1, 5):   # keep the marker's beacon column clear too
            pts.append((x, y, dz * 1.5))
    return pts


def compute_caps(lots):
    """Max height per lot so no building hides a path/node from the city camera."""
    cam = Vector(L.CITY_CAM_LOC)
    blocks = {}
    for idx, (cx, cy, sx, sy) in enumerate(lots):
        blocks.setdefault((math.floor(cx / L.PITCH), math.floor(cy / L.PITCH)), []).append(idx)
    caps = [1e9] * len(lots)
    for p in _occlusion_samples():
        pz = p[2] if len(p) > 2 else 0.1
        P = Vector((p[0], p[1], pz))
        d = cam - P
        dxy = math.hypot(d.x, d.y)
        ux, uy = d.x / dxy, d.y / dxy
        slope = d.z / dxy
        step = 0.3
        s = 0.0
        while s < 40.0:
            qx, qy = P.x + ux * s, P.y + uy * s
            qz = pz + slope * s
            for idx in blocks.get((math.floor(qx / L.PITCH), math.floor(qy / L.PITCH)), ()):
                cx, cy, sx, sy = lots[idx]
                if abs(qx - cx) <= sx / 2 + 0.3 and abs(qy - cy) <= sy / 2 + 0.3:
                    caps[idx] = min(caps[idx], qz)
            s += step
    return caps


def _in_landmark(x, y):
    for k in ("spire", "arco", "twin_a", "twin_b", "screen"):
        lx, ly = LANDMARKS[k][:2]
        rad = 16.0 if k == "arco" else 7.0
        if abs(x - lx) < rad and abs(y - ly) < rad:
            return True
    return False


def build_city(M, caps_on=True, nav=True, seed=L.SEED, j_range=None, tall_bias=1.0):
    rng = random.Random(seed)
    bmat = building_material(M)
    world(M["sky_top"], M["sky_hor"], M["sky_str"])

    # ground + block slabs
    g = MeshBuf()
    g.poly([(-400, -300, 0), (400, -300, 0), (400, 500, 0), (-400, 500, 0)])
    mesh_obj("ground", g.v, g.f, m_pbr(M["ground"], rough=0.12, metal=0.3, coat=0.6))
    slabs = MeshBuf()
    lots = []
    inner = L.PITCH - L.STREET
    jr = j_range or L.GRID_J
    for i in L.GRID_I:
        for j in jr:
            if j == max(jr):
                continue
            cx, cy = i * L.PITCH + L.PITCH / 2, j * L.PITCH + L.PITCH / 2
            slabs.box(cx, cy, 0, inner, inner, 0.15)
            if _in_landmark(cx, cy):
                continue
            ins = 0.7
            usable = inner - 2 * ins
            split = rng.choice([1, 2, 2, 4, 4])
            if split == 1:
                parts = [(cx, cy, usable, usable)]
            elif split == 2:
                if rng.random() < 0.5:
                    parts = [(cx - usable / 4, cy, usable / 2 - 0.4, usable), (cx + usable / 4, cy, usable / 2 - 0.4, usable)]
                else:
                    parts = [(cx, cy - usable / 4, usable, usable / 2 - 0.4), (cx, cy + usable / 4, usable, usable / 2 - 0.4)]
            else:
                q = usable / 4
                parts = [(cx + dx * q, cy + dy * q, usable / 2 - 0.4, usable / 2 - 0.4) for dx in (-1, 1) for dy in (-1, 1)]
            lots.extend(p for p in parts if rng.random() > 0.12)
    mesh_obj("slabs", slabs.v, slabs.f, m_pbr(M["slab"], rough=0.5, metal=0.1))

    caps = compute_caps(lots) if caps_on else [1e9] * len(lots)
    bb = MeshBuf()
    trims = [MeshBuf() for _ in M["trims"]]
    boards = MeshBuf()
    tall_tops = []
    for (cx, cy, sx, sy), cap in zip(lots, caps):
        near = cy / (L.PITCH * 12)
        base_h = rng.uniform(3, 9) + min(near, 1.0) * rng.uniform(3, 26) * tall_bias
        if rng.random() < 0.08:
            base_h *= 1.8
        h = min(base_h, cap - 0.2)
        if h < 1.0:
            continue
        rot = 0.0
        bb.box(cx, cy, 0.15, sx, sy, h)
        top = h + 0.15
        if h > 10 and rng.random() < 0.6:
            f = rng.uniform(0.55, 0.8)
            h2 = rng.uniform(0.2, 0.5) * h
            bb.box(cx, cy, top, sx * f, sy * f, h2)
            top += h2
            if rng.random() < 0.5:
                tb = trims[rng.randrange(len(trims))]
                zt = top - h2 - 0.02
                tb.box(cx, cy - sy / 2, zt, sx, 0.14, 0.14)
                tb.box(cx, cy + sy / 2, zt, sx, 0.14, 0.14)
                tb.box(cx - sx / 2, cy, zt, 0.14, sy, 0.14)
                tb.box(cx + sx / 2, cy, zt, 0.14, sy, 0.14)
        if h > 6 and rng.random() < 0.45:
            tb = trims[rng.randrange(len(trims))]
            tb.box(cx, cy, top, sx * 0.9 * (0.8 if h > 10 else 1), sy * 0.08 + 0.1, 0.12)
        if h > 14 and rng.random() < 0.3:   # billboard on the camera-facing facade
            bw = min(sx * 0.8, rng.uniform(2.5, 5.0))
            bh = bw * rng.uniform(0.5, 1.4)
            bz = rng.uniform(h * 0.4, h * 0.85)
            y0 = cy - sy / 2 - 0.12
            boards.poly([(cx - bw / 2, y0, bz), (cx + bw / 2, y0, bz), (cx + bw / 2, y0, bz + bh), (cx - bw / 2, y0, bz + bh)])
        if top > 25:
            tall_tops.append((cx, cy, top))
    bb.build("buildings", [bmat])
    for tb, col in zip(trims, M["trims"]):
        if tb.v:
            tb.build("trim", [m_emit(col, 1.6 * M["neon"])])
    scr_stops = [(0.0, (0.95, 0.15, 0.55)), (0.35, (1.0, 0.55, 0.1)), (0.55, (1.0, 0.85, 0.3)),
                 (0.75, (0.2, 0.8, 1.0)), (1.0, (0.6, 0.2, 1.0))]
    if boards.v:
        boards.build("boards", [m_screen(scr_stops, 1.3 * M["neon"], scale=0.35)])
    # antenna blinkers on tall roofs
    bl = MeshBuf()
    for cx, cy, top in tall_tops[::2]:
        bl.box(cx, cy, top, 0.12, 0.12, 2.5)
        bl.box(cx, cy, top + 2.5, 0.35, 0.35, 0.35)
    if bl.v:
        bl.build("antenna", [m_emit((1.0, 0.1, 0.1), 2.0)])

    build_landmarks(M, rng, bmat)
    build_traffic(M, rng)
    build_shards(M, rng)
    # fog: city haze + glowing far haze (bounded boxes, not a world volume)
    fog_box((0, 70, 22), (260, 230, 44), m_volume(M["fog"], M["fog_d"], M["fog_e"], M["fog_es"]))
    fog_box((0, 190, 45), (340, 110, 90), m_volume(M["far"], M["far_d"], M["far_e"], M["far_es"]))
    if M["spill"] > 0:
        cols = [(1.0, 0.2, 0.6), (0.2, 0.7, 1.0), (1.0, 0.5, 0.1)]
        for k in range(26):
            point_light((rng.uniform(-70, 70), rng.uniform(-5, 130), rng.uniform(2, 9)),
                        cols[k % 3] if M is not MOODS["alarm"] else (1.0, 0.2, 0.1),
                        rng.uniform(150, 450) * M["spill"] * (0.5 if M is MOODS["alarm"] else 1.0), radius=2.0)
    if nav:
        build_nav(M, rng)
    return rng


def build_landmarks(M, rng, bmat):
    tr = M["trims"]
    # Spire: octagonal needle tower with light-ring crowns
    sx, sy = LANDMARKS["spire"]
    b = MeshBuf()
    oct_pts = lambda r: [(r * math.cos(math.radians(22.5 + 45 * k)), r * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]
    zs = [(0, 40, 6.5), (40, 62, 5.0), (62, 80, 3.6), (80, 92, 2.0)]
    for z0, z1, r in zs:
        b.prism(oct_pts(r), z0, z1, xf=lambda p: (p[0] + sx, p[1] + sy, p[2]))
    b.box(sx, sy, 92, 0.4, 0.4, 16)
    b.build("spire", [bmat])
    for z, r, c in ((40.3, 7.6, tr[0]), (62.3, 6.0, tr[1]), (80.3, 4.6, tr[2]), (100, 1.5, tr[0])):
        arc("spire_ring", r, 0, 360, 0.18, m_emit(c, 2.5 * M["neon"]), loc=(sx, sy, z), taper=False)
    # Arcology: stepped pyramid with glowing edges
    ax, ay = LANDMARKS["arco"]
    b = MeshBuf()
    steps = 7
    for k in range(steps):
        s = 30 - k * 4
        b.box(ax, ay, k * 7.0, s, s, 7.0)
    b.build("arco", [bmat])
    for k in range(steps):
        s = 30 - k * 4
        z = (k + 1) * 7.0 + 0.05
        pts = [(ax - s / 2, ay - s / 2, z), (ax + s / 2, ay - s / 2, z), (ax + s / 2, ay + s / 2, z), (ax - s / 2, ay + s / 2, z)]
        curve_obj("arco_edge", pts, 0.14, m_emit(tr[2] if k % 2 else tr[0], 2.2 * M["neon"]), cyclic=True)
    point_light((ax, ay, 52), tr[2], 20000 * max(0.2, M["neon"]), radius=4)
    # Twin towers + skybridges
    for key, hgt in (("twin_a", 58), ("twin_b", 66)):
        x, y = LANDMARKS[key]
        b = MeshBuf()
        b.box(x, y, 0, 8, 8, hgt)
        b.box(x, y, hgt, 5, 5, 6)
        b.build(key, [bmat])
        curve_obj("twin_crown", [(x - 4.05, y - 4.05, hgt), (x + 4.05, y - 4.05, hgt), (x + 4.05, y + 4.05, hgt), (x - 4.05, y + 4.05, hgt)],
                  0.15, m_emit(tr[1], 2.2 * M["neon"]), cyclic=True)
    (xa, ya), (xb, yb) = LANDMARKS["twin_a"], LANDMARKS["twin_b"]
    b = MeshBuf()
    for z in (26, 40):
        b.box(xa, (ya + yb) / 2, z, 3, yb - ya - 8, 1.6)
    b.build("bridges", [m_pbr((0.1, 0.08, 0.2), rough=0.2, metal=0.5, emit=tr[1], es=0.8 * M["neon"], film=380)])
    # Megascreen tower
    mx, my = LANDMARKS["screen"]
    b = MeshBuf()
    b.box(mx, my, 0, 9, 9, 48)
    b.build("screen_tower", [bmat])
    scr_stops = [(0.0, (1.0, 0.2, 0.55)), (0.4, (1.0, 0.6, 0.15)), (0.6, (1.0, 0.9, 0.5)), (0.8, (0.15, 0.85, 1.0)), (1.0, (0.5, 0.2, 1.0))]
    b = MeshBuf()
    b.poly([(mx - 4.6, my - 4.7, 22), (mx + 4.6, my - 4.7, 22), (mx + 4.6, my - 4.7, 42), (mx - 4.6, my - 4.7, 42)])
    b.build("megascreen", [m_screen(scr_stops, 0.9 * M["neon"] + 0.3, scale=0.2)])
    # The Halo: a giant hologram swirl of light over the city (the reference's ring vortex)
    hx, hy, hz = LANDMARKS["halo"]
    rot = (math.radians(74), 0, 0)
    swirl(rng, "halo", (hx, hy, hz), rot, 7, 15, 90, M["halo_pal"][1:] + M["halo_pal"][1:2], M["halo"], thick=(0.03, 0.2), tilt=0.12, spiral=(-0.3, 0.45), span=(50, 230))
    swirl(rng, "halo_core", (hx, hy, hz), rot, 2.5, 8, 34, M["halo_pal"][:2], M["halo"] * 1.1, thick=(0.02, 0.1), tilt=0.15, spiral=(-0.3, 0.5), span=(60, 260))
    point_light((hx, hy, hz), M["halo_pal"][1], 15000 * M["halo"] / 2.2, radius=8)


def build_traffic(M, rng):
    heads, tails = MeshBuf(), MeshBuf()
    for i in L.GRID_I:
        x = i * L.PITCH
        for k in range(22):
            y = rng.uniform(-20, 190)
            lane = rng.choice([-0.75, 0.75])
            (heads if lane > 0 else tails).box(x + lane, y, 0.2, 0.28, 0.9, 0.15)
    for j in L.GRID_J:
        y = j * L.PITCH
        for k in range(14):
            x = rng.uniform(-90, 90)
            lane = rng.choice([-0.75, 0.75])
            (heads if lane > 0 else tails).box(x, y + lane, 0.2, 0.9, 0.28, 0.15)
    # aerial lanes of car-light streaks
    for y, z in ((24, 13), (58, 17), (90, 21), (130, 26)):
        for k in range(40):
            x = rng.uniform(-110, 110)
            ln = rng.uniform(0.8, 2.6)
            (heads if rng.random() < 0.5 else tails).box(x, y + rng.uniform(-1, 1), z + rng.uniform(-1, 1), ln, 0.18, 0.12)
    for x, z in ((-38.5, 16), (38.5, 19)):
        for k in range(30):
            y = rng.uniform(-10, 170)
            (heads if rng.random() < 0.5 else tails).box(x + rng.uniform(-1, 1), y, z, 0.18, rng.uniform(0.8, 2.4), 0.12)
    heads.build("heads", [m_emit((1.0, 0.85, 0.65), 2.0 * M["traffic"])])
    tails.build("tails", [m_emit((1.0, 0.08, 0.2), 2.0 * M["traffic"])])


def shard_material(M, tint):
    return m_pbr((0.06, 0.04, 0.12), rough=0.08, metal=0.7, emit=tint, es=0.5 * M["shard_e"], film=520, alpha=0.85)


def build_shards(M, rng, region=((-80, 80), (-10, 140), (8, 42)), n=160, nfrag=420, parent=None, size=(0.3, 1.6)):
    tints = [(1.0, 0.25, 0.6), (0.2, 0.8, 1.0), (1.0, 0.55, 0.15)]
    bufs = [MeshBuf() for _ in tints]
    for k in range(n):
        x, y, z = (rng.uniform(*region[0]), rng.uniform(*region[1]), rng.uniform(*region[2]))
        s = rng.uniform(*size)
        tri = [(0, s), (-s * rng.uniform(0.3, 0.7), -s * 0.6), (s * rng.uniform(0.3, 0.8), -s * rng.uniform(0.2, 0.7))]
        ax, ay, az = [rng.uniform(0, math.tau) for _ in range(3)]
        th = s * 0.06

        def xf(p, ax=ax, ay=ay, az=az, x=x, y=y, z=z):
            v = Vector(p)
            v.rotate(__import__("mathutils").Euler((ax, ay, az)))
            return (v.x + x, v.y + y, v.z + z)
        bufs[k % 3].prism(tri, -th, th, xf=xf)
    for b, t in zip(bufs, tints):
        b.build("shards", [shard_material(M, t)], parent=parent)
    fr = [MeshBuf() for _ in tints]
    for k in range(nfrag):
        x, y, z = (rng.uniform(*region[0]), rng.uniform(*region[1]), rng.uniform(*region[2]))
        s = rng.uniform(0.12, 0.5) * (size[1] / 1.6)
        fr[k % 3].box(x, y, z, s, s * rng.uniform(0.3, 1.0), s * 0.1, rot=rng.uniform(0, math.pi), bottom=True)
    for b, t in zip(fr, tints):
        b.build("frags", [m_emit(t, 1.2 * M["frag"])], parent=parent)


def build_nav(M, rng):
    nodes = {n[0]: n for n in L.NODES}
    hot = L.YOU_ARE_HERE
    bright, dim = MeshBuf(), MeshBuf()
    dots = MeshBuf()
    for a, b in L.EDGES:
        poly = L.edge_polyline(L.node_world(nodes[a]), L.node_world(nodes[b]))
        reach = hot in (a, b)
        buf = bright if reach else dim
        w = 0.9 if reach else 0.6
        for (x0, y0), (x1, y1) in zip(poly, poly[1:]):
            ln = math.hypot(x1 - x0, y1 - y0)
            rot = math.atan2(y1 - y0, x1 - x0)
            buf.box((x0 + x1) / 2, (y0 + y1) / 2, 0.02, ln + w, w, 0.1, rot=rot - math.pi / 2 + math.pi / 2)
            if reach:
                k = int(ln / 2.2)
                for s in range(1, k):
                    t = s / k
                    dots.box(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, 0.1, 0.55, 0.55, 0.1, rot=math.pi / 4)
    # boxes were built along x; rotate to the segment direction is handled by rot above
    bright.build("paths_hot", [m_emit((0.45, 0.95, 1.0), 2.4 * M["path"])])
    dim.build("paths", [m_emit((0.65, 0.35, 1.0), 1.5 * M["path"])])
    dots.build("path_dots", [m_emit((1.0, 1.0, 1.0), 3.0)])
    for n in L.NODES:
        x, y = L.node_world(n)
        col = L.NODE_COLORS[n[3]]
        big = n[0] == hot
        r = 2.2 if big else 1.7
        base = MeshBuf()
        seg = 32
        base.prism([(r * 1.5 * math.cos(math.tau * k / seg), r * 1.5 * math.sin(math.tau * k / seg)) for k in range(seg)], 0.0, 0.08,
                   xf=lambda p, x=x, y=y: (p[0] + x, p[1] + y, p[2]))
        base.build("node_base", [m_pbr((0.03, 0.02, 0.06), rough=0.15, metal=0.6, emit=col, es=0.25, film=400)])
        core = MeshBuf()
        core.prism([(r * math.cos(math.tau * k / seg), r * math.sin(math.tau * k / seg)) for k in range(seg)], 0.08, 0.22,
                   xf=lambda p, x=x, y=y: (p[0] + x, p[1] + y, p[2]))
        core.build("node_core", [m_emit(col, 2.2)])
        arc("node_ring", r * 1.5, 0, 360, 0.14, m_emit(col, 3.0), loc=(x, y, 0.25), taper=False)
        arc("node_ring2", r * 1.9, 20, 160, 0.08, m_emit(col, 2.0), loc=(x, y, 0.25))
        arc("node_ring3", r * 1.9, 200, 340, 0.08, m_emit(col, 2.0), loc=(x, y, 0.25))
        beam = MeshBuf()
        beam.prism([(0.35 * math.cos(math.tau * k / 12), 0.35 * math.sin(math.tau * k / 12)) for k in range(12)], 0.2, 9.0 if big else 5.0,
                   xf=lambda p, x=x, y=y: (p[0] + x, p[1] + y, p[2]))
        beam.build("node_beam", [m_emit(col, 0.9, additive=True)])
        point_light((x, y, 2.0), col, 900 if M["spill"] else 300, radius=1.0)
        if big:
            swirl(rng, "here", (x, y, 0.6), (0, 0, 0), r * 1.9, r * 3.0, 26,
                  [(0.6, 1.0, 1.0), (1.0, 1.0, 1.0), (1.0, 0.4, 0.8)], 2.6, thick=(0.04, 0.12), tilt=0.12)
            # hovering chevron marker
            chev = MeshBuf()
            chev.prism([(0, -1.2), (1.1, 0.6), (0, 0.1), (-1.1, 0.6)], -0.18, 0.18,
                       xf=lambda p, x=x, y=y: (p[0] + x, p[2] + y, p[1] + 11.0))
            chev.build("chevron", [m_emit((0.7, 1.0, 1.0), 3.0)])
