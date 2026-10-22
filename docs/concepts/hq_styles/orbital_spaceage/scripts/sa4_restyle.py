"""Orbital Commons v3: 1950s retro-futurism, a TV network + space corporation HQ. Runs INSIDE Blender (hook inserted by sa3_blender_hq.py).
Changes against v2 (designer notes): everything dimmer (forms read by shading, not glow); no atom sculpture, no starbursts; the launch bay
doors carry the atom symbol; the rocket is a finless Saturn V style stack (white, black roll bands, stage rings, escape tower) and four large
FIXED fin structures on the launch ring give the illusion of fins; the surrounding buildings each have a readable role and dishes / masts:
  se (top left)   mission control: a white drum with a curved glass window wall and a roof dish + radome
  ne (left)       broadcast studio: ON AIR sign, three-dish array, TV lattice mast
  start (top right) vehicle assembly hangar: tall door slot, low wings, emblem, roof dishes
  sw (far right)  crew tower: bell + shaft + observation saucer with a beacon
  nw (near right) fuel tank farm: spheres and horizontal tanks with pipes
  antenna (near left) uplink mast: the truss keeps its decks; dish array + a big uplink dish
  gantry          the orange service tower with white swing arms
  monorail        a single beam loop on white pylons, a station with an upswept canopy, a three-car bullet train
Base meshes are culled in memory (never edited on disk)."""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from sa_restyle import SAcc, _perp, annulus, cone_along, cull, revolve, saucer  # noqa: E402
import deco_restyle as D  # noqa: E402
from sa2_restyle import ellipsoid_along, poly_bars, sphere, torus  # noqa: E402

ICE = (0.61, 0.87, 1.0)
TANG = (1.0, 0.36, 0.04)
TURQ = (0.10, 0.85, 0.78)
FONT = {"O": ["01110", "10001", "10001", "10001", "01110"], "N": ["10001", "11001", "10101", "10011", "10001"],
        "A": ["01110", "10001", "11111", "10001", "10001"], "I": ["11111", "00100", "00100", "00100", "11111"],
        "R": ["11110", "10001", "11110", "10010", "10001"]}


# ------------------------------------------------------------------------------------------------ helpers
def arc_band(acc, cx, cy, r, z0, z1, a0, a1, n=24):
    """A cylinder wall segment between world azimuths a0..a1 (deg, 0 = +y)."""
    for i in range(n):
        b0, b1 = math.radians(a0 + (a1 - a0) * i / n), math.radians(a0 + (a1 - a0) * (i + 1) / n)
        acc.face([(cx + r * math.sin(b0), cy + r * math.cos(b0), z0), (cx + r * math.sin(b1), cy + r * math.cos(b1), z0),
                  (cx + r * math.sin(b1), cy + r * math.cos(b1), z1), (cx + r * math.sin(b0), cy + r * math.cos(b0), z1)])


def dish(ctx, c, axis, R, depth_k=0.24, n=24, rings=5):
    """A parabolic dish (white enamel bowl, chrome rim, three feed struts and a horn). c = bowl centre, axis = where it looks."""
    W, C = ctx["white"], ctx["alu"]
    c, d = Vector(c), Vector(axis).normalized()
    u, w = _perp(d)
    depth = R * depth_k
    for i in range(rings):
        for j in range(n):
            pts = []
            for ii, jj in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)):
                r, a = R * ii / rings, 2 * math.pi * jj / n
                pts.append(c + u * (r * math.cos(a)) + w * (r * math.sin(a)) + d * (depth * (r / R) ** 2))
            W.face(pts)
    rim = [c + u * (R * math.cos(2 * math.pi * k / 32)) + w * (R * math.sin(2 * math.pi * k / 32)) + d * depth for k in range(32)]
    poly_bars(C, rim, 0.45, 0.45, closed=True)
    tip = c + d * (depth + R * 0.62)
    for k in range(3):
        a = 2 * math.pi * k / 3
        C.bar(c + u * (R * 0.96 * math.cos(a)) + w * (R * 0.96 * math.sin(a)) + d * depth, tip, 0.22, 0.22)
    cone_along(C, tip - d * 0.8, tip + d * 0.8, 0.9, 0.5, n=8)


def dish_on(ctx, base, az_deg, elev_deg, R, ped=3.0):
    """A dish on a short pedestal at `base`, looking along azimuth az (0 = +y) and elevation."""
    x, y, z = base
    revolve(ctx["white"], x, y, [(R * 0.30, z), (R * 0.16, z + ped)], n=10)
    a, e = math.radians(az_deg), math.radians(elev_deg)
    d = Vector((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)))
    c = Vector((x, y, z + ped)) + Vector((0, 0, R * 0.30))
    ctx["alu"].bar((x, y, z + ped), tuple(c), 0.5, 0.5)
    dish(ctx, tuple(c), tuple(d), R)


def mast(ctx, cx, cy, z0, h, w0=3.2, w1=0.9):
    """A tapering lattice mast (TV / uplink): four legs, rings and X braces, crossbars and a beacon."""
    C = ctx["alu"]
    n = 6
    for k in range(4):
        ax, ay = (1 if k in (0, 3) else -1), (1 if k in (0, 1) else -1)
        C.bar((cx + ax * w0, cy + ay * w0, z0), (cx + ax * w1, cy + ay * w1, z0 + h), 0.45, 0.45)
    for i in range(n):
        za, zb_ = z0 + h * i / n, z0 + h * (i + 1) / n
        wa, wb = w0 + (w1 - w0) * i / n, w0 + (w1 - w0) * (i + 1) / n
        for (a0, b0, a1, b1) in ((1, 1, -1, 1), (-1, 1, -1, -1), (-1, -1, 1, -1), (1, -1, 1, 1)):
            C.bar((cx + a0 * wa, cy + b0 * wa, za), (cx + a1 * wb, cy + b1 * wb, zb_), 0.25, 0.25)
    for zz, ww in ((z0 + h * 0.55, 6.0), (z0 + h * 0.8, 4.2)):
        C.bar((cx - ww, cy, zz), (cx + ww, cy, zz), 0.35, 0.35)
        C.bar((cx, cy - ww, zz + 0.8), (cx, cy + ww, zz + 0.8), 0.35, 0.35)
    C.bar((cx, cy, z0 + h), (cx, cy, z0 + h + 8.0), 0.3, 0.3)
    sphere(ctx["oneon"], (cx, cy, z0 + h + 8.6), 1.1, n=10, m=6)


def lbox(acc, C, t3, v3, lx0, lx1, ly0, ly1, z0, z1):
    """An axis-aligned (in the t, v frame) box at station centre C."""
    acc.prism([(lx0, ly0), (lx1, ly0), (lx1, ly1), (lx0, ly1)], (C[0], C[1], z0), t3, v3, (0, 0, 1), z1 - z0)


def sign_onair(ctx, c, r_vec, n_vec, cs=1.35):
    """An ON AIR sign: navy panel with tangerine letters, in the plane of (r_vec = reading direction, up), facing n_vec."""
    B, ON = ctx["black"], ctx["oneon"]
    word = "ON AIR"
    wd = sum(5 * cs + cs if ch != " " else 3 * cs for ch in word) - cs
    c = Vector(c)
    r_vec, n_vec = Vector(r_vec).normalized(), Vector(n_vec).normalized()
    B.prism([(-wd / 2 - 2.0, -4.5), (wd / 2 + 2.0, -4.5), (wd / 2 + 2.0, 4.5), (-wd / 2 - 2.0, 4.5)], c - n_vec * 0.4, r_vec, (0, 0, 1), n_vec, 0.8)
    x = -wd / 2
    for ch in word:
        if ch == " ":
            x += 3 * cs
            continue
        for row, bits in enumerate(FONT[ch]):
            for col, bit in enumerate(bits):
                if bit == "1":
                    x0 = x + col * cs
                    ON.prism([(x0, 2.5 * cs - row * cs), (x0 + cs * 0.95, 2.5 * cs - row * cs), (x0 + cs * 0.95, 2.5 * cs - (row + 1) * cs * 0.95),
                              (x0, 2.5 * cs - (row + 1) * cs * 0.95)], c + n_vec * 0.42, r_vec, (0, 0, 1), n_vec, 0.25)
        x += 5 * cs + cs


def stack_rocket(ctx, zb):
    """Finless Saturn V style stack: white stages, black roll pattern, black interstages, chrome stage rings, capsule and escape tower."""
    W, C, B, T, HOT, NE = ctx["rwhite"], ctx["rchrome"], ctx["black"], ctx["orange"], ctx["hot"], ctx["dim"]
    r1, r2 = 7.0, 6.2
    h1, hi1, h2, hi2, h3 = 42.0, 3.0, 22.0, 2.5, 11.0
    z = zb
    revolve(C, 0, 0, [(3.0, z - 2.5), (4.8, z), (6.0, z + 4.5), (r1, z + 9.0)], n=36)                    # engine skirt
    revolve(W, 0, 0, [(r1, z + 9.0), (r1, z + h1)], n=36)                                                # S-IC
    for k in range(8):                                                                                   # roll pattern: black panels, alternating
        if k % 2 == 0:
            for (za, zz) in ((z + 12.0, z + 24.0), (z + 28.0, z + 40.0)):
                arc_band(B, 0, 0, r1 + 0.1, za, zz, k * 45.0 + 4.0, k * 45.0 + 41.0, n=4)
    z += h1
    revolve(B, 0, 0, [(r1 + 0.08, z), (r1 + 0.08, z + hi1)], n=36)                                      # interstage
    revolve(C, 0, 0, [(r1 + 0.14, z - 0.5), (r1 + 0.14, z + 0.2)], n=36)
    z += hi1
    revolve(W, 0, 0, [(r1, z), (r1, z + h2)], n=36)                                                      # S-II
    for k in range(8):
        if k % 2 == 1:
            arc_band(B, 0, 0, r1 + 0.1, z + 4.0, z + 16.0, k * 45.0 + 4.0, k * 45.0 + 41.0, n=4)
    revolve(C, 0, 0, [(r1 + 0.14, z + h2 - 0.6), (r1 + 0.14, z + h2)], n=36)
    z += h2
    revolve(B, 0, 0, [(r1 + 0.08, z), (r2 + 0.08, z + hi2)], n=36)                                       # interstage 2
    z += hi2
    revolve(W, 0, 0, [(r2, z), (r2, z + h3)], n=36)                                                      # S-IVB
    for k in range(10):                                                                                  # portholes ring on the upper stage
        a = math.radians(k * 36.0 + 10.0)
        c, s = math.cos(a), math.sin(a)
        circ = [(1.1 * math.cos(2 * math.pi * i / 12), 1.1 * math.sin(2 * math.pi * i / 12)) for i in range(12)]
        HOT.prism(circ, (c * (r2 + 0.08), s * (r2 + 0.08), z + 6.0), (-s, c, 0), (0, 0, 1), (c, s, 0), 0.2)
    z += h3
    revolve(C, 0, 0, [(r2, z), (r2 * 0.8, z + 3.0), (2.6, z + 9.0), (1.8, z + 11.0)], n=32)               # capsule
    revolve(T, 0, 0, [(1.8, z + 11.0), (1.0, z + 12.0), (0.0, z + 12.4)], n=12)
    for k in range(3):                                                                                   # escape tower
        a = 2 * math.pi * k / 3
        ctx["alu"].bar((math.cos(a) * 1.3, math.sin(a) * 1.3, z + 11.0), (0, 0, z + 21.0), 0.18, 0.18)
    cone_along(T, (0, 0, z + 16.5), (0, 0, z + 23.0), 0.9, 0.6, n=8)
    ctx["alu"].bar((0, 0, z + 23.0), (0, 0, z + 27.0), 0.2, 0.2)
    return z + 27.0


def decor_fin(ctx, zbase, ang_deg, r_in=7.35):
    """A tall FIXED tail-fin structure standing on the launch ring, tight against the stack: classic 1950s profile (raked leading edge, short
    vertical trailing edge, tip above the first stage ring). White enamel with an orange leading edge; not part of the rocket."""
    C, T, W, NE = ctx["alu"], ctx["orange"], ctx["rwhite"], ctx["dim"]
    a = math.radians(ang_deg)
    c, s = math.cos(a), math.sin(a)
    r0 = r_in
    reach, th = 12.8, 1.9
    fin = [(r0, zbase + 1.0), (r0 + reach, zbase + 0.6), (r0 + reach, zbase + 11.0), (r0 + reach * 0.55, zbase + 33.0), (r0, zbase + 60.0)]
    W.prism(fin, (s * th / 2, -c * th / 2, 0.0), (c, s, 0), (0, 0, 1), (-s, c, 0), th)
    p_out, p_tip = (c * (r0 + reach), s * (r0 + reach), zbase + 11.0), (c * r0, s * r0, zbase + 60.0)
    p_mid = (c * (r0 + reach * 0.55), s * (r0 + reach * 0.55), zbase + 33.0)
    T.bar(p_out, p_mid, 2.3, 1.1)
    T.bar(p_mid, p_tip, 2.3, 1.1)
    NE.bar((c * (r0 + reach), s * (r0 + reach), zbase + 1.4), p_out, 0.35, 0.35)
    W.prism([(r0 - 0.4, 0.0), (r0 + reach + 1.5, 0.0), (r0 + reach + 1.5, 3.0), (r0 - 0.4, 3.0)], (s * 2.0, -c * 2.0, zbase - 2.0), (c, s, 0), (0, 0, 1), (-s, c, 0), 4.0)
    for zz in (zbase + 10.0, zbase + 30.0):
        C.bar((c * (r0 + 0.1), s * (r0 + 0.1), zz), (c * 6.0, s * 6.0, zz + 1.5), 0.45, 0.45)


def bell_tower(ctx, cx, cy):
    """The crew tower: a white bell that swallows the room box, a tapering shaft, an observation saucer with a beacon."""
    W, C, NE, T = ctx["white"], ctx["alu"], ctx["dim"], ctx["turq"]
    revolve(W, cx, cy, [(22.0, 0.0), (21.0, 5.0), (17.5, 11.5), (11.0, 18.0), (6.0, 26.0), (4.2, 36.0), (3.4, 52.0)], n=36)
    for (z0, r0) in ((4.0, 21.2), (10.0, 18.2)):
        revolve(NE, cx, cy, [(r0 + 0.05, z0), (r0 + 0.35, z0 + 0.9)], n=36)
    torus(C, cx, cy, 0.9, 22.0, 0.9, n=36, m=5)
    revolve(C, cx, cy, [(4.3, 36.0), (3.5, 52.0)], n=14)
    zs = 58.0
    saucer(dict(ctx, orange=T), cx, cy, zs, 17.0, 9.0, n=24)
    C.bar((cx, cy, zs + 6.0), (cx, cy, zs + 17.0), 0.5, 0.5)
    sphere(ctx["oneon"], (cx, cy, zs + 17.8), 1.4, n=10, m=6)


def searchlight(ctx, g, name, az_deg, PH, PR, rh, Wt):
    a = math.radians(az_deg)
    px, py = math.sin(a) * (PR - 3.0), math.cos(a) * (PR - 3.0)
    WH, C, NE = ctx["white"], ctx["alu"], ctx["hot"]
    revolve(WH, px, py, [(2.4, PH), (1.5, PH + 3.0), (1.2, PH + 5.0)], n=10)
    for k, (zt, spot, wat) in enumerate(((rh * 0.30, 30.0, Wt * 0.8), (rh * 0.80, 22.0, Wt))):
        lp = Vector((px, py, PH + 6.0 + 3.6 * k))
        aim = Vector((0.0, 0.0, PH + zt))
        d = (aim - lp).normalized()
        cone_along(C, lp - d * 1.0, lp + d * 5.0, 2.3, 2.8, n=14)
        u, v = _perp(d)
        NE.prism([(2.3 * math.cos(2 * math.pi * i / 14), 2.3 * math.sin(2 * math.pi * i / 14)) for i in range(14)], lp + d * 5.05, u, v, d, 0.06)
        g["add_light"]("sa3_spot_%s_%d" % (name, k), "SPOT", tuple(lp + d * 4.4), wat, (0.88, 0.94, 1.0), aim=tuple(aim), size=0.8, spot=spot,
                       blend=0.5, group="deco", shadow=True)


# ------------------------------------------------------------------------------------------------ entry
def apply(g, cfg):
    if cfg.get("off"):
        return
    CP = g["CP"]
    PR, PH, SR, RR = CP["podium_r"], CP["podium_h"], CP["silo_r"], CP["ring_r"]
    AN = CP["antenna"]
    OBJ, G = g["OBJ"], g["G"]
    sc = bpy.context.scene
    coll = bpy.data.collections.new("spaceage3")
    sc.collection.children.link(coll)
    view_az = cfg.get("view_az", 150.0)
    dir_v = Vector((math.sin(math.radians(view_az)), math.cos(math.radians(view_az)), 0.0))      # camera looks along this
    toc = -dir_v                                                                                   # from the scene toward the camera
    right = Vector((math.cos(math.radians(view_az)), -math.sin(math.radians(view_az)), 0.0))

    # ---- materials (dimmer than v2: forms read by shading)
    ek = cfg.get("ice_k", 1.6)
    wk = cfg.get("white_emit", 0.08)
    M_W = D.principled("sa3_white", (0.84, 0.87, 0.92), 0.0, 0.18, coat=1.0, coat_rough=0.03, emit=(0.80, 0.88, 1.0), emit_k=wk)
    M_C = D.principled("sa3_chrome", (0.93, 0.95, 0.98), 1.0, 0.12, emit=(0.8, 0.9, 1.0), emit_k=cfg.get("chrome_emit", 0.10))
    M_T = D.principled("sa3_tangerine", (0.95, 0.20, 0.01), 0.0, 0.25, coat=0.8, emit=(1.0, 0.30, 0.02), emit_k=0.10)
    M_TQ = D.principled("sa3_turq", (0.05, 0.60, 0.55), 0.0, 0.25, coat=0.8, emit=(0.1, 0.85, 0.78), emit_k=0.12)
    M_B = D.principled("sa3_navy", (0.012, 0.02, 0.05), 0.0, 0.2, coat=1.0)
    M_RW = D.principled("sa3_rwhite", (0.88, 0.90, 0.95), 0.0, 0.16, coat=1.0, coat_rough=0.03, emit=(0.85, 0.92, 1.0), emit_k=cfg.get("rocket_emit", 0.22))
    M_RC = D.principled("sa3_rchrome", (0.95, 0.97, 1.0), 1.0, 0.12, emit=(0.85, 0.93, 1.0), emit_k=cfg.get("rocket_chrome_emit", 0.25))
    M_I = D.emission("sa3_ice", ICE, ek)
    M_ID = D.emission("sa3_ice_dim", ICE, ek * 0.45)
    M_IH = D.emission("sa3_ice_hot", (0.85, 0.95, 1.0), ek * 2.2)
    M_WIN = D.emission("sa3_window", (0.55, 0.80, 1.0), cfg.get("window_k", 2.0))
    M_WINW = D.emission("sa4_window_warm", (1.0, 0.70, 0.36), cfg.get("warm_k", 2.2))
    M_ON = D.emission("sa3_tangerine_neon", TANG, 2.0)
    ctx = dict(white=SAcc("sa3_white", M_W, coll, True), alu=SAcc("sa3_chrome", M_C, coll, True), orange=SAcc("sa3_tang", M_T, coll, True),
               turq=SAcc("sa3_turq", M_TQ, coll, True), black=SAcc("sa3_navy", M_B, coll, True),
               dim=SAcc("sa3_dim", M_ID, coll), rwhite=SAcc("sa3_rwhite", M_RW, coll, True), rchrome=SAcc("sa3_rchrome", M_RC, coll, True),
               ice=SAcc("sa3_ice", M_I, coll), hot=SAcc("sa3_hot", M_IH, coll), oneon=SAcc("sa3_oneon", M_ON, coll, True),
               win=SAcc("sa3_win", M_WIN, coll, True), winw=SAcc("sa4_winw", M_WINW, coll, True))

    # ---- city fill: darkest, cool, steel-blue
    D.lacquer_facade(g["M_CITY"], gold=cfg.get("grid", (0.16, 0.24, 0.34)), dark=0.12, window_tint=cfg.get("win_tint", (0.55, 0.75, 1.0)),
                     win_boost=cfg.get("win_boost", 0.20), band_emit=0.10)
    D.brass_metal(g["M_CMETAL"], tint=(0.34, 0.42, 0.55), metal=0.8, rough=0.4)
    for k in ("city_sign", "city_neon"):
        if OBJ.get(k) is not None:
            OBJ[k].hide_render = True
    for b in D.find_nodes(g["M_CIVIC"], "ShaderNodeBsdfPrincipled"):
        for lk in list(b.inputs["Base Color"].links):
            g["M_CIVIC"].node_tree.links.remove(lk)
        b.inputs["Base Color"].default_value = (0.84, 0.87, 0.92, 1.0)
        b.inputs["Roughness"].default_value = 0.18
        b.inputs["Coat Weight"].default_value = 1.0
        b.inputs["Coat Roughness"].default_value = 0.04
        b.inputs["Emission Color"].default_value = (0.8, 0.88, 1.0, 1.0)
        b.inputs["Emission Strength"].default_value = wk
    D.brass_metal(g["M_METAL"], tint=(0.85, 0.88, 0.95), metal=0.9, rough=0.3)
    D.recolor_attr(OBJ.get("metal"), lambda c: (1.0, 0.25, 0.02) if (c[0] > 0.35 and c[1] < 0.15) else c)
    D.recolor_attr(OBJ.get("city_small"), lambda c: (0.22, 0.32, 0.46) if c[0] > c[2] * 1.3 else c)
    D.tune_fog(g, dict(fog_col=cfg.get("fog_col", (0.40, 0.54, 0.74))))
    D.fog_veil(g, dict(veil_k=cfg.get("veil_k", 0.0025), veil_z=(110.0, 300.0)))
    for ob, e0, grp in g["LIGHTS"]:
        if ob.name.startswith(("cityglow_", "bankglow_")):
            ob.data.color = cfg.get("glow_col", (0.55, 0.72, 0.95))

    # ---- cull what is replaced
    for k, ob in list(OBJ.items()):
        if k.startswith(("mv_rocket_", "mv_door_", "band_")) or k == "pad_paint":
            cull(ob, lambda c: True)
    cull(OBJ.get("metal"), lambda c: c.z >= PH - 0.05 and math.hypot(c.x, c.y) < 48.0 and abs(c.y) < 21.0)
    cull(OBJ.get("civic"), lambda c: 36.0 < abs(c.x) < 40.8 and abs(c.y) < 21.0 and c.z > PH + 0.1)
    for nid, a in G.STATION.items():
        v = G.az_vec(a)
        cx, cy = v[0] * (RR + 3.0), v[1] * (RR + 3.0)
        for k in ("civic", "metal", "trim", "small"):
            cull(OBJ.get(k), lambda c, cx=cx, cy=cy: c.z > 11.4 and math.hypot(c.x - cx, c.y - cy) < 17.0)
    for i, (ob, e0, grp) in enumerate(g["LIGHTS"]):
        k_ = cfg.get("pad_k", 0.3) if ob.name.startswith("pad_flood") else (0.2 if ob.name.startswith(("rocket_svc", "ant_red")) else None)
        if k_ is not None:
            g["LIGHTS"][i] = (ob, e0 * k_, grp)
            ob.data.energy = e0 * k_

    W, C, T, B, NE, ICEN, HOT, ON, WIN = (ctx["white"], ctx["alu"], ctx["orange"], ctx["black"], ctx["dim"], ctx["ice"], ctx["hot"], ctx["oneon"], ctx["win"])
    z = PH + 0.12

    # ---- platform: dim rim lines, white cornice
    annulus(NE, 0, 0, PR - 3.6, PR - 3.0, z, n=120)
    annulus(ON, 0, 0, PR - 7.0, PR - 6.6, z, n=120)
    revolve(W, 0, 0, [(PR + 0.2, PH - 1.8), (PR + 1.8, PH - 0.9), (PR + 1.8, PH + 0.5), (PR - 0.2, PH + 0.5)], n=120)
    annulus(NE, 0, 0, PR + 1.5, PR + 1.9, PH + 0.55, n=120)

    # ---- launch bay doors: two navy half-discs with a chrome rim and seam, the atom symbol (nucleus + 3 orbits) as their graphic
    Rd = cfg.get("door_r", 40.0)
    zd = PH + 1.4
    for sgn in (-1, 1):
        a0, a1 = (0.0, 180.0) if sgn > 0 else (180.0, 360.0)
        for i in range(30):
            b0, b1 = math.radians(a0 + (a1 - a0) * i / 30), math.radians(a0 + (a1 - a0) * (i + 1) / 30)
            B.face([(0, 0, zd), (Rd * math.sin(b0), Rd * math.cos(b0), zd), (Rd * math.sin(b1), Rd * math.cos(b1), zd)])
            B.face([(Rd * math.sin(b0), Rd * math.cos(b0), zd), (Rd * math.sin(b0), Rd * math.cos(b0), PH), (Rd * math.sin(b1), Rd * math.cos(b1), PH),
                    (Rd * math.sin(b1), Rd * math.cos(b1), zd)])
    torus(C, 0, 0, zd, Rd + 0.3, 0.9, n=72, m=6)
    C.bar((0, -Rd, zd + 0.1), (0, Rd, zd + 0.1), 0.7, 0.35)
    for k in range(3):                     # three orbits that clear the fins (minor radius 20 > fin reach); the nucleus is a ring round the stack's base
        rot = math.radians(60 * k + 30)
        pts = []
        for i in range(112):
            t = 2 * math.pi * i / 112
            x, y = 38.5 * math.cos(t), 20.5 * math.sin(t)
            pts.append((x * math.cos(rot) - y * math.sin(rot), x * math.sin(rot) + y * math.cos(rot), zd + 0.12))
        poly_bars(ICEN, pts, 1.2, 0.14, closed=True)
        t = math.radians(35 + 120 * k)
        x, y = 38.5 * math.cos(t), 20.5 * math.sin(t)
        ex, ey = x * math.cos(rot) - y * math.sin(rot), x * math.sin(rot) + y * math.cos(rot)
        sphere(ON, (ex, ey, zd + 1.3), 2.5, n=12, m=8)
    annulus(ON, 0, 0, 10.5, 12.3, zd + 0.15, n=72)
    annulus(ICEN, 0, 0, 13.0, 13.5, zd + 0.15, n=72)

    # ---- the Saturn V style stack, plus four large fixed fin structures round its base
    zb = zd + 9.0
    rtop = stack_rocket(ctx, zb)
    for k in range(4):
        decor_fin(ctx, zd, 45 + 90 * k)
    # swing arms from the orange gantry to the stack
    gy = CP["control"]["y"]
    for zz in (PH + 22.0, PH + 44.0, PH + 66.0):
        W.box(-1.4, -8.0, zz, 1.4, gy + 3.5, zz + 2.4)
        T.box(-1.6, -9.0, zz - 0.1, 1.6, -6.6, zz + 2.5)
        NE.box(-0.2, -6.6, zz + 2.4, 0.2, gy + 4.0, zz + 2.6)
    for i, az in enumerate((0.0, 90.0, 180.0, 270.0)):
        searchlight(ctx, g, "p%d" % i, az, PH, PR, rtop - PH, cfg.get("spot_w", 4.5e6))

    # ---- the surrounding buildings, each with a role
    for nid, a in sorted(G.STATION.items()):
        v = G.az_vec(a)
        vv = Vector((v[0], v[1], 0.0))
        t3 = (-vv.y, vv.x, 0.0)
        v3 = (vv.x, vv.y, 0.0)
        C0 = (v[0] * (RR + 3.0), v[1] * (RR + 3.0))
        az_in = a + 180.0
        if nid == "se":                                   # MISSION CONTROL: a drum with a curved window wall, roof dish and radome
            revolve(W, C0[0], C0[1], [(21.0, 0.0), (21.0, 13.0), (19.0, 14.4), (0.0, 14.4)], n=40)
            arc_band(ctx["winw"], C0[0], C0[1], 21.2, 3.0, 11.6, az_in - 78.0, az_in + 78.0, n=30)        # warm panoramic window wall
            for rowz, deskh, monh in ((3.0, 1.5, 1.9), (6.6, 1.0, 1.7)):                                   # console rows: desk strips + monitor blocks, as silhouettes
                half = 74.0 if rowz < 5 else 66.0
                arc_band(B, C0[0], C0[1], 21.32, rowz, rowz + deskh, az_in - half, az_in + half, n=30)
                ang = -half + 3.0
                while ang < half - 2.0:
                    arc_band(B, C0[0], C0[1], 21.32, rowz + deskh, rowz + deskh + monh, az_in + ang - 1.0, az_in + ang + 1.0, n=2)
                    ang += 5.2
            for k in range(7):
                ak = az_in - 78.0 + 26.0 * k
                C.bar((C0[0] + 21.45 * math.sin(math.radians(ak)), C0[1] + 21.45 * math.cos(math.radians(ak)), 2.6),
                      (C0[0] + 21.45 * math.sin(math.radians(ak)), C0[1] + 21.45 * math.cos(math.radians(ak)), 12.0), 0.5, 0.5)
            torus(C, C0[0], C0[1], 13.2, 21.0, 0.7, n=40, m=5)
            revolve(W, C0[0], C0[1], [(12.0, 14.4), (12.0, 18.5), (10.5, 19.5), (0.0, 19.5)], n=30)
            arc_band(NE, C0[0], C0[1], 12.15, 15.8, 17.2, az_in - 78.0, az_in + 78.0, n=20)
            sphere(W, (C0[0] - vv.x * 2.0, C0[1] - vv.y * 2.0, 19.5), 4.0, n=16, m=10)
            dish_on(ctx, (C0[0] + t3[0] * 11.0 - vv.x * 4, C0[1] + t3[1] * 11.0 - vv.y * 4, 14.4), 330.0, 32.0, 8.5)
            dish_on(ctx, (C0[0] - t3[0] * 12.0 - vv.x * 4, C0[1] - t3[1] * 12.0 - vv.y * 4, 14.4), 300.0, 30.0, 5.0)
        elif nid == "ne":                                 # BROADCAST STUDIO: ON AIR sign, dish array, TV mast
            lbox(W, C0, t3, v3, -15.0, 15.0, -10.5, 10.5, 0.0, 16.0)
            lbox(T, C0, t3, v3, -15.15, 15.15, -10.65, 10.65, 11.0, 12.6)
            for q in range(-2, 3):
                lbox(WIN, C0, t3, v3, q * 5.6 - 1.7, q * 5.6 + 1.7, -10.7, -10.6, 3.0, 8.5)
            for sgn in (-1, 1):
                for yy in (-4.0, 4.0):
                    W.bar((C0[0] + t3[0] * sgn * 15.0 * 0.0 + 0.0, C0[1], 0.0), (C0[0], C0[1], 0.0), 0.01, 0.01) if False else None
            spos = Vector((C0[0], C0[1], 16.0)) + vv * 0.0
            for sgn in (-1, 1):
                lp = Vector((C0[0], C0[1], 16.0)) + Vector(t3) * (sgn * 9.0) + toc * 3.0
                C.bar(tuple(lp), (lp.x, lp.y, 22.0), 0.5, 0.5)
            sign_onair(ctx, (C0[0] + toc.x * 3.0 - right.x * 9.0, C0[1] + toc.y * 3.0 - right.y * 9.0, 28.0), right, toc)
            dish_on(ctx, (C0[0] + t3[0] * 9.0 - vv.x * 4.0, C0[1] + t3[1] * 9.0 - vv.y * 4.0, 16.0), az_in + 15.0, 50.0, 6.5)
            dish_on(ctx, (C0[0] - t3[0] * 9.0 - vv.x * 4.0, C0[1] - t3[1] * 9.0 - vv.y * 4.0, 16.0), az_in - 25.0, 45.0, 5.5)
            dish_on(ctx, (C0[0] + vv.x * 6.0, C0[1] + vv.y * 6.0, 16.0), az_in + 60.0, 60.0, 4.5)
            mast(ctx, C0[0] + vv.x * 7.0 + t3[0] * 0.0, C0[1] + vv.y * 7.0, 16.0, 46.0)
        elif nid == "start":                              # VEHICLE ASSEMBLY HANGAR: tall door slot, low wings, emblem, roof dishes
            Cv = (C0[0] + vv.x * 6.0, C0[1] + vv.y * 6.0)
            HB = 64.0                                                                                   # VAB: a tall high bay with a huge vertical door slot
            lbox(W, Cv, t3, v3, -13.0, 13.0, -12.0, 12.0, 0.0, HB)
            lbox(W, Cv, t3, v3, -34.0, -13.0, -10.0, 10.0, 0.0, 26.0)
            lbox(W, Cv, t3, v3, 13.0, 34.0, -10.0, 10.0, 0.0, 26.0)
            lbox(B, Cv, t3, v3, -5.0, 5.0, -12.5, -11.8, 0.0, 56.0)                                     # the door slot: 10 wide, 56 tall
            lbox(C, Cv, t3, v3, -5.7, 5.7, -12.7, -12.2, 56.0, 57.2)
            lbox(C, Cv, t3, v3, -5.7, -5.0, -12.7, -12.2, 0.0, 56.0)
            lbox(C, Cv, t3, v3, 5.0, 5.7, -12.7, -12.2, 0.0, 56.0)
            for zz in range(7, 56, 7):
                lbox(NE, Cv, t3, v3, -4.6, 4.6, -12.55, -12.4, zz, zz + 0.4)
            for sgn in (-1, 1):                                                                           # Orbital stripes down the facade: tangerine + ice
                lbox(T, Cv, t3, v3, sgn * 7.0 - 1.2, sgn * 7.0 + 1.2, -12.1, -12.0, 0.0, HB)
                lbox(ICEN, Cv, t3, v3, sgn * 9.6 - 0.5, sgn * 9.6 + 0.5, -12.1, -12.0, 0.0, HB)
            lbox(T, Cv, t3, v3, -34.1, -13.0, -10.1, 10.1, 20.0, 21.4)
            lbox(T, Cv, t3, v3, 13.0, 34.1, -10.1, 10.1, 20.0, 21.4)
            fb = Vector((Cv[0], Cv[1], HB))
            C.bar(tuple(fb), (fb.x, fb.y, HB + 17.0), 0.5, 0.5)                                           # flag mast with a big banner facing the camera
            fc = fb + Vector((0, 0, 12.5)) + right * (-8.0) + toc * 0.0
            for q, acc in enumerate((T, W, B)):
                acc.prism([(-7.0, 2.8 - q * 2.6), (7.0, 2.8 - q * 2.6), (7.0, 0.2 - q * 2.6), (-7.0, 0.2 - q * 2.6)], tuple(fc + right * 8.0), tuple(right), (0, 0, 1), tuple(toc), 0.4)
            ON.prism([(2.0 * math.cos(2 * math.pi * i / 16), 2.0 * math.sin(2 * math.pi * i / 16)) for i in range(16)], tuple(fc + right * 8.0 + toc * 0.4 + Vector((0, 0, -1.2))), tuple(right), (0, 0, 1), tuple(toc), 0.1)
        elif nid == "sw":                                 # CREW TOWER
            bell_tower(ctx, C0[0], C0[1])
        elif nid == "nw":                                 # FUEL TANK FARM: spheres on legs and horizontal tanks, pipes
            RW_ = ctx["rwhite"]
            for q, lx in enumerate((-21.0, 0.0, 21.0)):                                                  # bright white spheres with orange bands, on legs
                px = C0[0] + t3[0] * lx + vv.x * 2.0
                py = C0[1] + t3[1] * lx + vv.y * 2.0
                zc = 21.0 if q == 1 else 14.0
                sphere(RW_, (px, py, zc), 8.8, n=24, m=12)
                torus(T, px, py, zc, 8.85, 1.0, n=24, m=5)
                torus(T, px, py, zc + 5.2, 6.9, 0.7, n=24, m=5)
                for k in range(6):
                    ak = 2 * math.pi * k / 6
                    C.bar((px + 6.2 * math.cos(ak), py + 6.2 * math.sin(ak), zc - 6.0), (px + 7.0 * math.cos(ak), py + 7.0 * math.sin(ak), 0.0 if q != 1 else 11.0), 0.55, 0.55)
                    C.bar((px + 6.2 * math.cos(ak), py + 6.2 * math.sin(ak), zc - 6.0), (px + 6.2 * math.cos(ak + 2.1), py + 6.2 * math.sin(ak + 2.1), zc - 6.0 - 3.0), 0.2, 0.2) if False else None
            for sgn in (-1, 1):
                pc = Vector((C0[0] + t3[0] * sgn * 10.0 - vv.x * 13.0, C0[1] + t3[1] * sgn * 10.0 - vv.y * 13.0, 3.8))
                ellipsoid_along(RW_, tuple(pc), t3, 12.0, 3.8, 3.8, n=16, m=10)
                ellipsoid_along(T, tuple(pc), t3, 2.2, 3.9, 3.9, n=16, m=4)

            def fp(r, lat, zz):
                return (vv.x * r + t3[0] * lat, vv.y * r + t3[1] * lat, zz)
            for sgn in (-1, 1):                                                                           # pipe runs from the tanks up the podium wall to the launch ring
                lat0, lat1 = sgn * 10.0, sgn * 2.8
                path = [fp(88.0, lat0, 3.8), fp(82.0, lat0, 3.8), fp(69.5, lat0, 3.8), fp(68.0, lat0, PH + 3.2), fp(60.0, lat0 * 0.7, PH + 3.2),
                        fp(52.0, lat1, PH + 3.2), fp(44.5, lat1, PH + 3.2)]
                for i in range(len(path) - 1):
                    C.bar(path[i], path[i + 1], 0.9, 0.9)
                for r_ in (78.0, 74.0, 56.0, 48.0):
                    p_ = fp(r_, lat0 if r_ > 69 else lat1, 0.0)
                    z_ = 3.8 if r_ > 69 else PH + 3.2
                    W.bar((p_[0], p_[1], z_ - 3.4 if r_ > 69 else PH + 0.4), (p_[0], p_[1], z_), 0.7, 0.7)
            p_ = fp(43.5, 0.0, PH + 3.2)
            C.box(p_[0] - 2.2, p_[1] - 2.2, PH + 1.6, p_[0] + 2.2, p_[1] + 2.2, PH + 4.8)

    # ---- uplink mast: the antenna truss keeps its decks and rooms, gains a big uplink dish and a dish array
    av = G.az_vec(AN["az"])
    tx, ty = av[0] * AN["r"], av[1] * AN["r"]
    for k in range(4):
        aa = 45 + 90 * k
        va = G.az_vec(aa)
        dish_on(ctx, (tx + va[0] * 9.5, ty + va[1] * 9.5, 78.5), aa + 20.0, 40.0, 5.0)
    dish(ctx, (tx - toc.x * 4.0, ty - toc.y * 4.0, 122.0), (toc.x * 0.8, toc.y * 0.8, 0.6), 10.5)
    C.bar((tx, ty, 104.0), (tx - toc.x * 4.0, ty - toc.y * 4.0, 121.0), 0.9, 0.9)

    # ---- monorail: beam on white pylons, a station with an upswept canopy, a three-car bullet train
    Rm, zbm = cfg.get("mono_r", 75.0), cfg.get("mono_z", 26.0)
    n = 120
    ring = [(Rm * math.sin(2 * math.pi * i / n), Rm * math.cos(2 * math.pi * i / n)) for i in range(n)]
    for i in range(n):
        p0, p1 = ring[i], ring[(i + 1) % n]
        C.bar((p0[0], p0[1], zbm), (p1[0], p1[1], zbm), 3.4, 1.8)
    for i in range(18):
        a = 2 * math.pi * (i + 0.5) / 18
        px, py = Rm * math.sin(a), Rm * math.cos(a)
        revolve(W, px, py, [(3.0, 0.0), (1.9, 10.0), (1.3, zbm - 1.0)], n=10)
        revolve(C, px, py, [(2.2, zbm - 1.0), (2.2, zbm - 0.6)], n=10)
    a_st = math.radians(cfg.get("station_az", 330.0))
    ts = Vector((math.cos(a_st), -math.sin(a_st), 0.0))                  # tangent
    os_ = Vector((math.sin(a_st), math.cos(a_st), 0.0))                  # outward
    cs_ = Vector((Rm * math.sin(a_st), Rm * math.cos(a_st), 0.0))
    # station: a platform BESIDE the beam (outer side) with a streamlined upswept canopy over the platform only; the train stands at it on the beam
    plat = [(3.4, 0.0), (11.0, 0.0), (11.0, 1.3), (3.4, 1.3)]
    W.prism(plat, cs_ + ts * -26.0 + Vector((0, 0, zbm - 0.3)), tuple((-os_)), (0, 0, 1), tuple(ts), 52.0)
    ICEN.prism([(3.3, 0.0), (3.7, 0.0), (3.7, 0.3), (3.3, 0.3)], cs_ + ts * -26.0 + Vector((0, 0, zbm + 1.0)), tuple((-os_)), (0, 0, 1), tuple(ts), 52.0)
    for sx in (-22.0, -7.0, 8.0, 22.0):
        p = cs_ + ts * sx + (-os_) * 8.0
        revolve(W, p.x, p.y, [(1.9, 0.0), (1.2, zbm - 0.3)], n=8)
    prof = []
    for i in range(11):                                                                              # canopy: swoops up and out (Googie boomerang)
        l = 4.6 + 9.4 * i / 10
        prof.append((l, zbm + 9.5 + 0.045 * (l - 4.6) ** 2))
    cpoly = prof + [(p[0], p[1] + 0.9) for p in reversed(prof)]
    W.prism(cpoly, cs_ + ts * -26.0, tuple((-os_)), (0, 0, 1), tuple(ts), 52.0)
    T.prism([(prof[-1][0] - 0.2, prof[-1][1] - 0.3), (prof[-1][0] + 0.3, prof[-1][1] - 0.3), (prof[-1][0] + 0.3, prof[-1][1] + 1.2), (prof[-1][0] - 0.2, prof[-1][1] + 1.2)],
            cs_ + ts * -26.0, tuple((-os_)), (0, 0, 1), tuple(ts), 52.0)
    for sx in (-23.0, -8.0, 8.0, 23.0):                                                              # slim raked columns from platform to canopy
        p0 = cs_ + ts * sx + (-os_) * 10.2
        C.bar((p0.x, p0.y, zbm + 1.0), (p0.x + (-os_).x * 1.8, p0.y + (-os_).y * 1.8, zbm + 10.6 + 0.045 * 36.0), 0.6, 0.6)
    sgp = cs_ + (-os_) * 14.5 + ts * -29.0
    C.bar((sgp.x, sgp.y, zbm), (sgp.x, sgp.y, zbm + 17.0), 0.8, 0.8)
    ctx["turq"].prism([(4.6 * math.cos(2 * math.pi * i / 20), 4.6 * math.sin(2 * math.pi * i / 20)) for i in range(20)], (sgp.x, sgp.y, zbm + 19.0), tuple(ts), (0, 0, 1), tuple((-os_)), 0.8)
    WIN.prism([(3.2 * math.cos(2 * math.pi * i / 20), 3.2 * math.sin(2 * math.pi * i / 20)) for i in range(20)], (sgp.x, sgp.y, zbm + 19.0), tuple(ts), (0, 0, 1), tuple((-os_)), 0.85)
    a0 = a_st
    for ci in range(3):
        a = a0 + (ci - 1) * (17.4 / Rm)
        px, py = Rm * math.sin(a), Rm * math.cos(a)
        d = (math.cos(a), -math.sin(a), 0.0)
        cz = zbm + 3.1
        ellipsoid_along(ctx["turq"], (px, py, cz), d, 7.6, 3.4, 3.3)
        ellipsoid_along(WIN, (px, py, cz + 0.7), d, 7.0, 3.47, 1.05)
        ellipsoid_along(W, (px, py, cz + 2.9), d, 6.2, 2.3, 0.8)


    for k in ctx:
        ctx[k].build()
    print("[sa4] faces", {k: len(ctx[k].f) for k in ctx}, flush=True)
