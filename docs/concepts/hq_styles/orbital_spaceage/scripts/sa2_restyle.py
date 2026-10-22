"""Orbital Commons v2: 1950s pulp retro-futurism / Raygun Gothic. Runs INSIDE Blender (hook inserted by sa2_blender_hq.py in front of the render
section of the untouched hq_scene.py). Fewer, bigger, nameable shapes:
  hero      a chrome / white-enamel finned rocket (V-2 / Moonliner / Bonestell proportions, four big swept fins, porthole band, chrome ogive nose)
            standing on its fins over a launch ring; four searchlights on the platform edge light it (no pad flood)
  atom      the truss antenna becomes an atom tower: tangerine nucleus, three orbit rings with turquoise electrons
  stations  two glass bubble domes (the rooms stay visible inside) and two saucer-topped bell towers (they swallow the room boxes)
  signs     Las Vegas style atomic starbursts: on the PAD station and on top of the service gantry
  monorail  a single beam loop with white pylons and a three-car bullet train round the complex
  deck      an atom emblem in ice neon (three orbits, tangerine electrons) around the launch ring
Material: polished chrome, white enamel, ice-white neon, sparing tangerine and turquoise. Base meshes are culled in memory, never edited on disk."""
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

ICE = (0.61, 0.87, 1.0)
TANG = (1.0, 0.36, 0.04)
TURQ = (0.10, 0.85, 0.78)


# ------------------------------------------------------------------------------------------------ helpers
def ellipsoid_along(acc, c, d, L, ru, rv, n=20, m=12):
    """A streamlined body (ellipsoid) along axis d, half length L, lateral radius ru, vertical radius rv."""
    c, d = Vector(c), Vector(d).normalized()
    u = d.cross(Vector((0, 0, 1))).normalized()
    v = u.cross(d).normalized()
    rings = []
    for i in range(m + 1):
        ph = math.pi * i / m
        x, s = -L * math.cos(ph), math.sin(ph)
        rings.append([c + d * x + u * (ru * s * math.cos(2 * math.pi * j / n)) + v * (rv * s * math.sin(2 * math.pi * j / n)) for j in range(n)])
    for i in range(m):
        for j in range(n):
            k = (j + 1) % n
            acc.face([rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]])


def sphere(acc, c, r, n=18, m=10):
    prof = [(r * math.sin(math.pi * i / m), c[2] - r * math.cos(math.pi * i / m)) for i in range(m + 1)]
    prof[0] = (0.0, prof[0][1])
    prof[-1] = (0.0, prof[-1][1])
    revolve(acc, c[0], c[1], prof, n=n)


def torus(acc, cx, cy, z, R, r, n=48, m=8):
    revolve(acc, cx, cy, [(R + r * math.cos(2 * math.pi * i / m), z + r * math.sin(2 * math.pi * i / m)) for i in range(m + 1)], n=n)


def poly_bars(acc, pts, w, h, closed=True):
    k = len(pts)
    for i in range(k if closed else k - 1):
        acc.bar(pts[i], pts[(i + 1) % k], w, h)


def star(ctx, c, lat, R, th=0.9):
    """A Las Vegas atomic starburst in the vertical plane spanned by lat and up: 8 long + 8 short spikes, ice neon face, tip lamps, tangerine core."""
    W, NE, HOT, ON = ctx["white"], ctx["ice"], ctx["hot"], ctx["oneon"]
    lat = Vector(lat).normalized()
    nrm = lat.cross(Vector((0, 0, 1))).normalized()
    c = Vector(c)

    def poly(scale):
        pts = []
        for k in range(32):
            a = math.radians(k * 11.25)
            r = (R if (k // 2) % 2 == 0 else 0.60 * R) if k % 2 == 0 else 0.20 * R
            pts.append((math.sin(a) * r * scale, math.cos(a) * r * scale))
        return pts
    W.prism(poly(1.0), c - nrm * (th / 2), lat, (0, 0, 1), nrm, th)
    for sgn in (-1, 1):
        NE.prism(poly(0.93), c + nrm * (sgn * (th / 2 + 0.02)) - (nrm * 0.1 if sgn < 0 else Vector((0, 0, 0))), lat, (0, 0, 1), nrm, 0.1)
    for k in range(8):
        a = math.radians(k * 45.0)
        tip = c + lat * (math.sin(a) * R * 1.0) + Vector((0, 0, math.cos(a) * R * 1.0))
        HOT.box(tip.x - 0.8, tip.y - 0.8, tip.z - 0.8, tip.x + 0.8, tip.y + 0.8, tip.z + 0.8)
    for sgn in (-1, 1):
        ON.prism([(0.22 * R * math.cos(2 * math.pi * i / 16), 0.22 * R * math.sin(2 * math.pi * i / 16)) for i in range(16)],
                 c + nrm * (sgn * (th / 2 + 0.2)) - (nrm * 0.1 if sgn < 0 else Vector((0, 0, 0))), lat, (0, 0, 1), nrm, 0.1)


def dome(ctx, cx, cy, R):
    """A glass bubble dome (chrome meridians, white enamel skirt, ice ring) over a station."""
    G, C, W, NE = ctx["glass"], ctx["alu"], ctx["white"], ctx["ice"]
    prof = [(R * math.cos(math.radians(a)), R * 0.95 * math.sin(math.radians(a))) for a in range(0, 90, 10)] + [(0.0, R * 0.95)]
    revolve(G, cx, cy, prof, n=40)
    for k in range(10):
        a = 2 * math.pi * k / 10
        pts = [(cx + math.cos(a) * r * 1.012, cy + math.sin(a) * r * 1.012, z * 1.012 + 0.1) for r, z in prof[:-1]] + [(cx, cy, R * 0.95 * 1.012)]
        poly_bars(C, pts, 0.55, 0.55, closed=False)
    for z, r in ((R * 0.95 * math.sin(math.radians(40)), R * math.cos(math.radians(40))),):
        torus(C, cx, cy, z, r * 1.012, 0.28, n=40, m=5)
    revolve(W, cx, cy, [(R + 3.2, 0.0), (R + 3.2, 1.5), (R + 0.2, 3.2), (R - 0.8, 3.2)], n=40)
    annulus(NE, cx, cy, R + 3.3, R + 3.9, 0.35, n=48)


def bell_tower(ctx, cx, cy, az_vec, lat_v):
    """A saucer-topped tower (Jetsons / Space Needle): a white enamel bell that swallows the bunker, a tapering chrome shaft, a saucer on top."""
    W, C, NE, T = ctx["white"], ctx["alu"], ctx["ice"], ctx["turq"]
    prof = [(22.0, 0.0), (21.0, 5.0), (17.5, 11.5), (11.0, 18.0), (6.0, 26.0), (4.2, 36.0), (3.4, 50.0)]
    revolve(W, cx, cy, prof, n=36)
    for (z0, r0) in ((4.0, 21.2), (10.0, 18.2)):
        revolve(NE, cx, cy, [(r0 + 0.05, z0), (r0 + 0.35, z0 + 0.9)], n=36)
    torus(C, cx, cy, 0.9, 22.0, 0.9, n=36, m=5)
    revolve(C, cx, cy, [(4.3, 36.0), (3.5, 50.0)], n=14)
    zs = 56.0
    ctx2 = dict(ctx, orange=T)
    saucer(ctx2, cx, cy, zs, 17.0, 9.0, n=24)
    C.bar((cx, cy, zs + 6.0), (cx, cy, zs + 17.0), 0.5, 0.5)
    C.bar((cx, cy, zs + 17.0), (cx, cy, zs + 24.0), 0.7, 0.7)
    star(ctx, (cx, cy, zs + 33.0), lat_v, 11.0)


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
        g["add_light"]("sa2_spot_%s_%d" % (name, k), "SPOT", tuple(lp + d * 4.4), wat, (0.88, 0.94, 1.0), aim=tuple(aim), size=0.8, spot=spot,
                       blend=0.5, group="deco", shadow=True)


def rocket(ctx, zb):
    """The hero: base of the body at z = zb. Chrome skirt + nose, white enamel body, tangerine stripe, navy porthole band with 12 portholes,
    four big swept fins (chrome with tangerine inset) that stand on the deck."""
    W, C, T, B, NE, HOT, ON = ctx["rwhite"], ctx["rchrome"], ctx["orange"], ctx["black"], ctx["ice"], ctx["hot"], ctx["oneon"]
    r0, hb, L = 7.4, 66.0, 42.0
    revolve(C, 0, 0, [(3.2, zb - 3.0), (5.0, zb), (6.4, zb + 5.0), (r0, zb + 11.0)], n=40)
    revolve(W, 0, 0, [(r0, zb + 11.0), (r0, zb + hb)], n=40)
    for z0, z1 in ((zb + 22.0, zb + 24.0), (zb + 60.0, zb + 62.5)):
        revolve(C, 0, 0, [(r0 + 0.12, z0), (r0 + 0.12, z1)], n=40)
    revolve(T, 0, 0, [(r0 + 0.14, zb + 28.0), (r0 + 0.14, zb + 32.0)], n=40)
    revolve(B, 0, 0, [(r0 + 0.1, zb + 38.0), (r0 + 0.1, zb + 50.0)], n=40)
    for k in range(12):
        a = math.radians(k * 30.0 + 15.0)
        c, s = math.cos(a), math.sin(a)
        po = (c * (r0 + 0.1), s * (r0 + 0.1), zb + 44.0)
        circ = lambda rad: [(rad * math.cos(2 * math.pi * i / 14), rad * math.sin(2 * math.pi * i / 14)) for i in range(14)]
        C.prism(circ(2.4), po, (-s, c, 0), (0, 0, 1), (c, s, 0), 0.6)
        HOT.prism(circ(1.8), (po[0] + c * 0.5, po[1] + s * 0.5, po[2]), (-s, c, 0), (0, 0, 1), (c, s, 0), 0.25)
    rho = (r0 * r0 + L * L) / (2 * r0)
    prof = [(r0, zb + hb)]
    for i in range(1, 16):
        x = L * i / 16
        prof.append((max(0.12, math.sqrt(rho * rho - x * x) + r0 - rho), zb + hb + x))
    prof.append((0.0, zb + hb + L))
    revolve(C, 0, 0, prof, n=40)
    revolve(T, 0, 0, [(r * 1.03, z) for r, z in prof[-5:]], n=40)
    revolve(NE, 0, 0, [(r0 + 0.2, zb + 64.5), (r0 + 0.2, zb + 65.0)], n=40)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        c, s = math.cos(a), math.sin(a)
        o = (-(-s) * 0.7, -c * 0.7, 0.0)
        o = (s * 0.7, -c * 0.7, 0.0)
        fin = [(r0 - 0.6, zb + 0.0), (r0 + 4.0, zb - 11.0), (r0 + 27.0, zb - 11.0), (r0 + 27.0, zb - 4.0), (r0 - 0.6, zb + 50.0)]
        C.prism(fin, o, (c, s, 0), (0, 0, 1), (-s, c, 0), 1.4)
        inset = [(r0 + 7.0, zb - 9.0), (r0 + 24.5, zb - 9.0), (r0 + 24.5, zb - 5.0), (r0 + 7.0, zb + 14.0)]
        T.prism(inset, (-s * 0.7, c * 0.7, 0.0), (c, s, 0), (0, 0, 1), (-s, c, 0), 0.3)
        T.prism(inset, (s * 1.0, -c * 1.0, 0.0), (c, s, 0), (0, 0, 1), (-s, c, 0), 0.3)
        e0, e1 = (c * (r0 + 27.0), s * (r0 + 27.0), zb - 4.0), (c * (r0 - 0.6), s * (r0 - 0.6), zb + 50.0)
        NE.bar((e0[0], e0[1], e0[2] + 0.4), (e1[0], e1[1], e1[2] + 0.4), 0.35, 0.35)
        revolve(C, c * (r0 + 24.0), s * (r0 + 24.0), [(2.4, zb - 11.0), (2.0, zb - 10.0)], n=8)
    # launch table under the bell: a white enamel disc over the silo, chrome ring, neon rings
    return r0


def atom_tower(ctx, tx, ty, zc, view_az):
    C, NE, HOT, T, ON = ctx["alu"], ctx["dim"], ctx["hot"], ctx["turq_neon"], ctx["oneon"]
    sphere(ON, (tx, ty, zc), 7.0, n=20, m=12)
    torus(C, tx, ty, zc, 8.4, 0.5, n=24, m=5)
    lat = Vector((math.cos(math.radians(view_az)), -math.sin(math.radians(view_az)), 0.0))     # horizontal, perpendicular to the view
    for k in range(3):
        rot = math.radians(60 * k + 15)
        pts = []
        for i in range(48):
            t = 2 * math.pi * i / 48
            x, y = 31.0 * math.cos(t), 11.5 * math.sin(t)
            xr, yr = x * math.cos(rot) - y * math.sin(rot), x * math.sin(rot) + y * math.cos(rot)
            pts.append(Vector((tx, ty, zc)) + lat * xr + Vector((0, 0, yr)))
        poly_bars(NE, pts, 0.8, 0.8, closed=True)
        for fi in (0.17 + 0.31 * k,):
            t = 2 * math.pi * fi * 3
            x, y = 31.0 * math.cos(t), 11.5 * math.sin(t)
            xr, yr = x * math.cos(rot) - y * math.sin(rot), x * math.sin(rot) + y * math.cos(rot)
            p = Vector((tx, ty, zc)) + lat * xr + Vector((0, 0, yr))
            sphere(T, (p.x, p.y, p.z), 3.0, n=14, m=8)


def apply(g, cfg):
    if cfg.get("off"):
        return
    CP = g["CP"]
    PR, PH, SR, RR = CP["podium_r"], CP["podium_h"], CP["silo_r"], CP["ring_r"]
    AN, RK = CP["antenna"], CP["rocket"]
    OBJ, G = g["OBJ"], g["G"]
    sc = bpy.context.scene
    coll = bpy.data.collections.new("spaceage2")
    sc.collection.children.link(coll)

    # ---- materials: polished chrome, white enamel, ice neon, sparing tangerine / turquoise
    ek = cfg.get("ice_k", 3.2)
    wk = cfg.get("white_emit", 0.22)
    M_W = D.principled("sa2_white", (0.84, 0.87, 0.92), 0.0, 0.16, coat=1.0, coat_rough=0.03, emit=(0.80, 0.88, 1.0), emit_k=wk)
    M_C = D.principled("sa2_chrome", (0.93, 0.95, 0.98), 1.0, 0.10, emit=(0.8, 0.9, 1.0), emit_k=cfg.get("chrome_emit", 0.30))
    M_T = D.principled("sa2_tangerine", (0.95, 0.20, 0.01), 0.0, 0.25, coat=0.8, emit=(1.0, 0.30, 0.02), emit_k=0.20)
    M_TQ = D.principled("sa2_turq", (0.05, 0.60, 0.55), 0.0, 0.25, coat=0.8, emit=(0.1, 0.85, 0.78), emit_k=0.25)
    M_B = D.principled("sa2_navy", (0.01, 0.02, 0.05), 0.0, 0.15, coat=1.0)
    M_G = D.principled("sa2_glass", (0.75, 0.92, 1.0), 0.0, 0.03, emit=(0.6, 0.85, 1.0), emit_k=0.07)
    for b in D.find_nodes(M_G, "ShaderNodeBsdfPrincipled"):
        try:
            b.inputs["Alpha"].default_value = cfg.get("glass_alpha", 0.16)
            b.inputs["IOR"].default_value = 1.05
        except KeyError:
            pass
    M_I = D.emission("sa2_ice", ICE, ek)
    M_IH = D.emission("sa2_ice_hot", (0.85, 0.95, 1.0), ek * 3.0)
    M_ID = D.emission("sa2_ice_dim", ICE, ek * 0.5)
    M_RW = D.principled("sa2_rwhite", (0.88, 0.90, 0.95), 0.0, 0.14, coat=1.0, coat_rough=0.03, emit=(0.85, 0.92, 1.0), emit_k=cfg.get("rocket_emit", 0.55))
    M_RC = D.principled("sa2_rchrome", (0.95, 0.97, 1.0), 1.0, 0.10, emit=(0.85, 0.93, 1.0), emit_k=cfg.get("rocket_chrome_emit", 0.7))
    M_ON = D.emission("sa2_tangerine_neon", TANG, 2.6)
    M_TN = D.emission("sa2_turq_neon", TURQ, 3.0)
    ctx = dict(white=SAcc("sa2_white", M_W, coll, True), alu=SAcc("sa2_chrome", M_C, coll, True), orange=SAcc("sa2_tang", M_T, coll, True),
               turq=SAcc("sa2_turq", M_TQ, coll, True), black=SAcc("sa2_navy", M_B, coll, True), glass=SAcc("sa2_glass", M_G, coll, True),
               dim=SAcc("sa2_dim", M_ID, coll), rwhite=SAcc("sa2_rwhite", M_RW, coll, True), rchrome=SAcc("sa2_rchrome", M_RC, coll, True),
               ice=SAcc("sa2_ice", M_I, coll), hot=SAcc("sa2_hot", M_IH, coll), oneon=SAcc("sa2_oneon", M_ON, coll, True),
               turq_neon=SAcc("sa2_tneon", M_TN, coll, True))

    # ---- city fill: dark, cool, steel-blue (the HQ wins)
    D.lacquer_facade(g["M_CITY"], gold=cfg.get("grid", (0.20, 0.30, 0.42)), dark=0.14, window_tint=cfg.get("win_tint", (0.62, 0.82, 1.0)),
                     win_boost=cfg.get("win_boost", 0.45), band_emit=0.15)
    D.brass_metal(g["M_CMETAL"], tint=(0.40, 0.50, 0.64), metal=0.8, rough=0.38)
    for k in ("city_sign", "city_neon"):
        if OBJ.get(k) is not None:
            OBJ[k].hide_render = True
    for b in D.find_nodes(g["M_CIVIC"], "ShaderNodeBsdfPrincipled"):
        for lk in list(b.inputs["Base Color"].links):
            g["M_CIVIC"].node_tree.links.remove(lk)
        b.inputs["Base Color"].default_value = (0.84, 0.87, 0.92, 1.0)
        b.inputs["Roughness"].default_value = 0.16
        b.inputs["Coat Weight"].default_value = 1.0
        b.inputs["Coat Roughness"].default_value = 0.04
        b.inputs["Emission Color"].default_value = (0.8, 0.88, 1.0, 1.0)
        b.inputs["Emission Strength"].default_value = wk
    D.brass_metal(g["M_METAL"], tint=(0.85, 0.88, 0.95), metal=0.9, rough=0.3)

    def orangeify(c):
        return (1.0, 0.25, 0.02) if (c[0] > 0.35 and c[1] < 0.15) else c
    D.recolor_attr(OBJ.get("metal"), orangeify)
    D.recolor_attr(OBJ.get("city_small"), lambda c: (0.55, 0.80, 1.0) if c[0] > c[2] * 1.3 else c)
    D.tune_fog(g, dict(fog_col=cfg.get("fog_col", (0.46, 0.60, 0.80))))
    D.fog_veil(g, dict(veil_k=cfg.get("veil_k", 0.0025), veil_z=(110.0, 300.0)))
    for ob, e0, grp in g["LIGHTS"]:
        if ob.name.startswith(("cityglow_", "bankglow_")):
            ob.data.color = cfg.get("glow_col", (0.62, 0.80, 1.0))

    # ---- cull what is replaced: rocket, hack bands, door leaves + rails, pad paint, dishes / crest on the stations
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
    pk = cfg.get("pad_k", 0.35)
    for i, (ob, e0, grp) in enumerate(g["LIGHTS"]):
        k_ = None
        if ob.name.startswith("pad_flood"):
            k_ = pk
        elif ob.name.startswith("rocket_svc"):
            k_ = 0.2
        elif ob.name == "ant_red":
            k_ = 0.2
        if k_ is not None:
            g["LIGHTS"][i] = (ob, e0 * k_, grp)
            ob.data.energy = e0 * k_

    W, C, T, NE, HOT, ON = ctx["white"], ctx["alu"], ctx["orange"], ctx["ice"], ctx["hot"], ctx["oneon"]
    z = PH + 0.12

    # ---- deck: ice rim lines, a white cornice, and the atom emblem (three orbits, tangerine electrons) round the launch ring
    annulus(NE, 0, 0, PR - 3.6, PR - 3.0, z, n=120)
    annulus(ON, 0, 0, PR - 7.0, PR - 6.5, z, n=120)
    revolve(W, 0, 0, [(PR + 0.2, PH - 1.8), (PR + 1.8, PH - 0.9), (PR + 1.8, PH + 0.5), (PR - 0.2, PH + 0.5)], n=120)
    annulus(NE, 0, 0, PR + 1.5, PR + 1.9, PH + 0.55, n=120)
    for k in range(3):
        rot = math.radians(60 * k + 20)
        pts = []
        for i in range(120):
            t = 2 * math.pi * i / 120
            x, y = 50.0 * math.cos(t), 19.0 * math.sin(t)
            pts.append((x * math.cos(rot) - y * math.sin(rot), x * math.sin(rot) + y * math.cos(rot), z + 0.02))
        poly_bars(ctx["dim"], pts, 0.7, 0.14, closed=True)
        t = math.radians(40 + 100 * k)
        x, y = 50.0 * math.cos(t), 19.0 * math.sin(t)
        ex, ey = x * math.cos(rot) - y * math.sin(rot), x * math.sin(rot) + y * math.cos(rot)
        sphere(ON, (ex, ey, z + 1.8), 2.6, n=14, m=8)
    # launch table: enamel disc over the silo, chrome ring, neon rings, tangerine hold-down cone
    revolve(W, 0, 0, [(0.0, PH + 0.5), (SR + 1.0, PH + 0.5), (SR + 1.0, PH + 0.2)], n=48)
    annulus(NE, 0, 0, 5.0, 5.6, PH + 0.62, n=48)
    annulus(NE, 0, 0, 11.0, 11.6, PH + 0.62, n=48)
    torus(C, 0, 0, PH + 1.2, SR + 1.6, 2.2, n=64, m=8)
    annulus(ON, 0, 0, SR + 3.6, SR + 4.1, z, n=96)

    # ---- the hero rocket, standing on its fins
    zb = PH + 10.0
    rocket(ctx, zb)
    rtop = zb + 66.0 + 42.0
    # swing arms (white, tangerine tips) from the orange gantry to the rocket
    gy = CP["control"]["y"]
    for zz in (PH + 20.0, PH + 40.0, PH + 62.0):
        W.box(-1.4, -8.0, zz, 1.4, gy + 3.5, zz + 2.4)
        T.box(-1.6, -9.0, zz - 0.1, 1.6, -6.6, zz + 2.5)
        NE.box(-0.2, -6.6, zz + 2.4, 0.2, gy + 4.0, zz + 2.6)
    # the starburst on the gantry mast
    gz = PH + 70.0
    pass
    view_az = cfg.get("view_az", 150.0)
    lat = (math.cos(math.radians(view_az)), -math.sin(math.radians(view_az)), 0.0)
    pass

    # ---- four searchlights on the platform edge light the rocket (no pad flood)
    for i, az in enumerate((0.0, 90.0, 180.0, 270.0)):
        searchlight(ctx, g, "p%d" % i, az, PH, PR, rtop - PH, cfg.get("spot_w", 4.5e6))

    # ---- stations: domes (se, ne), saucer bell towers (nw, sw), starburst + dome on the PAD station
    for nid, a in sorted(G.STATION.items()):
        v = G.az_vec(a)
        cx, cy = v[0] * (RR + 3.0), v[1] * (RR + 3.0)
        if nid in ("se", "ne"):
            dome(ctx, cx, cy, 19.5)
        elif nid in ("nw", "sw"):
            bell_tower(ctx, cx, cy, v, lat)
        else:
            dome(ctx, cx, cy, 19.5)
            C.bar((cx, cy, 14.0), (cx, cy, 44.0), 0.9, 0.9)
            star(ctx, (cx, cy, 58.0), lat, 17.0)

    # ---- the atom tower: the antenna's truss keeps its decks and rooms; a nucleus and three orbits crown it
    av = G.az_vec(AN["az"])
    tx, ty = av[0] * AN["r"], av[1] * AN["r"]
    atom_tower(ctx, tx, ty, AN["h"] + 18.0, view_az)

    # ---- monorail: a single beam on white pylons looping the complex, with a three-car bullet train
    Rm, zbm = cfg.get("mono_r", 75.0), cfg.get("mono_z", 26.0)
    n = 120
    ring = [(Rm * math.sin(2 * math.pi * i / n), Rm * math.cos(2 * math.pi * i / n)) for i in range(n)]
    for i in range(n):
        p0, p1 = ring[i], ring[(i + 1) % n]
        C.bar((p0[0], p0[1], zbm), (p1[0], p1[1], zbm), 3.4, 1.8)
        NE.bar((p0[0] * 0.972, p0[1] * 0.972, zbm - 0.7), (p1[0] * 0.972, p1[1] * 0.972, zbm - 0.7), 0.3, 0.3)
    for i in range(18):
        a = 2 * math.pi * (i + 0.5) / 18
        px, py = Rm * math.sin(a), Rm * math.cos(a)
        revolve(W, px, py, [(3.0, 0.0), (1.9, 10.0), (1.3, zbm - 1.0)], n=10)
        revolve(C, px, py, [(2.2, zbm - 1.0), (2.2, zbm - 0.6)], n=10)
    a0 = math.radians(cfg.get("train_az", 330.0))
    for ci in range(3):
        a = a0 + ci * (24.0 / Rm)
        px, py = Rm * math.sin(a), Rm * math.cos(a)
        d = (math.cos(a), -math.sin(a), 0.0)
        cz = zbm + 3.1
        ellipsoid_along(ctx["turq"], (px, py, cz), d, 10.5, 4.0, 3.6)
        ellipsoid_along(ctx["hot"], (px, py, cz + 0.7), d, 9.6, 4.07, 1.1)
        ellipsoid_along(W, (px, py, cz + 3.0), d, 8.5, 2.6, 0.9)

    for k in ctx:
        ctx[k].build()
    print("[sa2] faces", {k: len(ctx[k].f) for k in ctx}, flush=True)
