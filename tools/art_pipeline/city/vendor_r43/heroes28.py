# Round 28: texture variants on the LOCKED Meridian "Container Wall" fortress (heroes27.fort_wall shape).
# NOT a module: hq_scene.py exec()s this after heroes27.py. It replaces obox() (every container of the fortress
# goes through it) and the wall / tower palettes per variant, then adds per-variant dressing (floodlights, tarps,
# cargo nets, hazard stripes, stencils, banners). STATE = t1 | t2 | t3 | t4 picks the variant.

TEX_VARIANTS = {
    # t1 RAW STEEL: real corrugation (raised and sunk ribs on every long face and roof), door ends with lock bars,
    #    unified Meridian orange (darker on walls), clean.
    "t1": dict(name="RAW CORRUGATED STEEL", wall=[(0.42, 0.18, 0.06), (0.36, 0.15, 0.05), (0.46, 0.20, 0.07)],
               tower=[(1.0, 0.52, 0.10), (0.96, 0.46, 0.08), (1.0, 0.58, 0.14)], ribs="deep", doors=True, rust=0.0, mixed=False,
               stencil=False, hazard=False, flood=False, tarps=False, nets=False),
    # t2 MIXED LIVERIES: real-world mixed container colours with rust patches and white stencil codes; the towers
    #    keep Meridian orange so the silhouette still reads.
    "t2": dict(name="MIXED LIVERIES + RUST", wall=[(0.55, 0.12, 0.08), (0.12, 0.26, 0.46), (0.10, 0.36, 0.34), (0.42, 0.42, 0.44), (0.50, 0.22, 0.06)],
               tower=[(0.78, 0.16, 0.10), (0.14, 0.32, 0.62), (1.0, 0.52, 0.10), (0.12, 0.48, 0.44), (0.86, 0.84, 0.78), (1.0, 0.52, 0.10)],
               ribs="deep", doors=True, rust=0.45, mixed=True, stencil=True, hazard=False, flood=False, tarps=False, nets=False, stripe=True),
    # t3 WEATHERED MERIDIAN: unified orange, heavy rust and grime streaks, stencilled MRDU codes, hazard stripes on the
    #    gate and tower feet, tarps and cargo nets slung over the battlements.
    "t3": dict(name="WEATHERED MERIDIAN", wall=[(0.40, 0.16, 0.06), (0.34, 0.13, 0.05), (0.44, 0.18, 0.07)],
               tower=[(0.78, 0.36, 0.08), (0.70, 0.30, 0.07), (0.84, 0.40, 0.10)], ribs="deep", doors=True, rust=1.0, mixed=False,
               stencil=True, hazard=True, flood=False, tarps=True, nets=True),
    # t4 LIT FORTRESS: charcoal walls, orange towers with a white Meridian stripe, lit seams on every course,
    #    floodlights washing the towers, banners, hazard stripes; a night spectacle.
    "t4": dict(name="LIT FORTRESS (charcoal + floods)", wall=[(0.14, 0.13, 0.15), (0.12, 0.11, 0.13), (0.16, 0.14, 0.15)],
               tower=[(1.0, 0.52, 0.10), (0.96, 0.46, 0.08), (1.0, 0.58, 0.14)], ribs="deep", doors=True, rust=0.25, mixed=False,
               stencil=True, hazard=True, flood=True, tarps=False, nets=False, seams=True, stripe=True),
}
TEX = TEX_VARIANTS.get(globals().get("STATE", "") or "t3", TEX_VARIANTS["t3"])
WALL_C[:] = TEX["wall"]
TOWER_C[:] = TEX["tower"]
_trng = random.Random(2828)
RUST = (0.30, 0.12, 0.05)
STENCILS = ["MRDU 4471", "MRDU 0447", "MRDU 1515", "MRDU 2026", "MRDU 7731", "MRDU 0915"]


def _mix(a, b, k):
    return tuple(a[i] * (1 - k) + b[i] * k for i in range(3))


def obox(cx, cy, z0, L, Wd, H, ang, col, ribs=True, acc=None, bid=None):
    """Round 28 container: body + corrugation (raised/sunk ribs), door end with lock bars, rust streaks, white
    stencil patch, optional lit seam - all as geometry so the cel shading and ink pick them up."""
    acc = acc or SOLID
    ca, sa = math.cos(ang), math.sin(ang)

    def P(u, v, z):
        return (cx + u * ca - v * sa, cy + u * sa + v * ca, z)
    hl, hw = L / 2, Wd / 2
    b = [P(-hl, -hw, z0), P(hl, -hw, z0), P(hl, hw, z0), P(-hl, hw, z0)]
    t = [P(-hl, -hw, z0 + H), P(hl, -hw, z0 + H), P(hl, hw, z0 + H), P(-hl, hw, z0 + H)]
    bid = bid or rid()
    for i in range(4):
        j = (i + 1) % 4
        acc.facet_quad(b[i], b[j], t[j], t[i], col, bid)
    acc.facet_quad(t[0], t[1], t[2], t[3], col, bid, jit=0.01)
    if not ribs or L <= 3:
        return
    dark = tuple(c * 0.62 for c in col)
    lite = tuple(min(1.0, c * 1.18) for c in col)
    n = max(3, int(L / 0.9))
    for sv in (-1, 1):  # deep corrugation: alternating raised (lit) and sunk (dark) ribs on both long faces
        v = sv * (hw + 0.06)
        for k in range(1, n):
            u = -hl + L * k / n
            c = lite if k % 2 else dark
            vv = v + sv * (0.10 if k % 2 else 0.0)
            acc.face([P(u - 0.2, vv, z0 + 0.3), P(u + 0.2, vv, z0 + 0.3), P(u + 0.2, vv, z0 + H - 0.3), P(u - 0.2, vv, z0 + H - 0.3)], c, bid)
        # top and bottom rails
        acc.face([P(-hl, v + sv * 0.12, z0 + H - 0.35), P(hl, v + sv * 0.12, z0 + H - 0.35), P(hl, v + sv * 0.12, z0 + H - 0.05), P(-hl, v + sv * 0.12, z0 + H - 0.05)], dark, bid)
        acc.face([P(-hl, v + sv * 0.12, z0 + 0.05), P(hl, v + sv * 0.12, z0 + 0.05), P(hl, v + sv * 0.12, z0 + 0.35), P(-hl, v + sv * 0.12, z0 + 0.35)], dark, bid)
        # rust streaks running down from the top rail
        if TEX["rust"] > 0:
            for _ in range(int(TEX["rust"] * 7 + 0.5)):
                if _trng.random() > TEX["rust"] + 0.2:
                    continue
                u = _trng.uniform(-hl + 0.6, hl - 0.6)
                ln = _trng.uniform(0.4, 1.0) * H
                w = _trng.uniform(0.35, 0.9) * (1.3 if TEX["rust"] > 0.8 else 1.0)
                rc = _mix(col, RUST, 0.55 + 0.3 * _trng.random())
                acc.face([P(u - w, v + sv * 0.2, z0 + H - 0.4), P(u + w, v + sv * 0.2, z0 + H - 0.4), P(u, v + sv * 0.2, z0 + H - 0.4 - ln)], rc, bid)
        # white stencil patch (code plate) on some faces
        if TEX["stencil"] and _trng.random() < 0.35 and L > 6:
            u = _trng.uniform(-hl + 1.5, hl - 3.5)
            zs = z0 + H * 0.62
            for r in range(2):  # two rows of "characters" as small white blocks
                for ch in range(6 if r == 0 else 4):
                    if _trng.random() < 0.15:
                        continue
                    x0 = u + ch * 0.36
                    acc.face([P(x0, v + sv * 0.22, zs - r * 0.55), P(x0 + 0.24, v + sv * 0.22, zs - r * 0.55), P(x0 + 0.24, v + sv * 0.22, zs - r * 0.55 + 0.38),
                              P(x0, v + sv * 0.22, zs - r * 0.55 + 0.38)], (0.92, 0.90, 0.84), bid)
        if TEX.get("stripe") and (col in TOWER_C or acc is LIT):  # Meridian white band across the tower containers
            acc.face([P(-hl, v + sv * 0.21, z0 + H * 0.42), P(hl, v + sv * 0.21, z0 + H * 0.42), P(hl, v + sv * 0.21, z0 + H * 0.58), P(-hl, v + sv * 0.21, z0 + H * 0.58)],
                     (0.95, 0.93, 0.88), bid)
    if TEX["doors"]:  # door end: two leaves with four vertical lock bars and cam handles
        for su in (1,):
            u = su * (hl + 0.06)
            acc.face([P(u, -hw + 0.15, z0 + 0.2), P(u, 0.0, z0 + 0.2), P(u, 0.0, z0 + H - 0.2), P(u, -hw + 0.15, z0 + H - 0.2)], dark, bid)
            for vb in (-hw * 0.7, -hw * 0.25, hw * 0.25, hw * 0.7):
                acc.face([P(u + 0.12, vb - 0.07, z0 + 0.3), P(u + 0.12, vb + 0.07, z0 + 0.3), P(u + 0.12, vb + 0.07, z0 + H - 0.3), P(u + 0.12, vb - 0.07, z0 + H - 0.3)],
                         (0.75, 0.72, 0.68), bid)
    if TEX.get("seams"):  # lit seam under each container (course lines glow at night)
        for sv in (-1, 1):
            v = sv * (hw + 0.24)
            NEON.face([P(-hl, v, z0 + 0.02), P(hl, v, z0 + 0.02), P(hl, v, z0 + 0.14), P(-hl, v, z0 + 0.14)], (1.0, 0.55, 0.14), (0, 0, 0))


def hazard_band(p0, p1, z0, z1, n=10):
    """Yellow/black hazard stripes on a vertical face from p0 to p1 (2D)."""
    for i in range(n):
        a = (p0[0] + (p1[0] - p0[0]) * i / n, p0[1] + (p1[1] - p0[1]) * i / n)
        b = (p0[0] + (p1[0] - p0[0]) * (i + 1) / n, p0[1] + (p1[1] - p0[1]) * (i + 1) / n)
        c = (1.0, 0.80, 0.10) if i % 2 == 0 else (0.05, 0.05, 0.05)
        (NEON if i % 2 == 0 else SOLID).face([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], c, (0, 0, 0))


def tarp(p0, p1, z, drop, col):
    """A tarp slung over a battlement edge (p0-p1 along the wall), hanging `drop` down the outer face (+X side)."""
    SOLID.face([(p0[0] - 1.2, p0[1], z + 0.4), (p1[0] - 1.2, p1[1], z + 0.4), (p1[0] + 0.2, p1[1], z - 0.2), (p0[0] + 0.2, p0[1], z - 0.2)], col, rid())
    SOLID.face([(p0[0] + 0.2, p0[1], z - 0.2), (p1[0] + 0.2, p1[1], z - 0.2), (p1[0] + 0.5, p1[1] - 0.4, z - drop), (p0[0] + 0.5, p0[1] + 0.4, z - drop * 0.85)],
               tuple(c * 0.8 for c in col), rid())


def cargo_net(x, y0, y1, z0, z1, n=8):
    for i in range(n + 1):
        y = y0 + (y1 - y0) * i / n
        beam((x, y, z0), (x, y, z1), 0.12, (0.15, 0.13, 0.10))
    for k in range(int((z1 - z0) / 1.2) + 1):
        z = z0 + k * 1.2
        beam((x, y0, z), (x, y1, z), 0.12, (0.15, 0.13, 0.10))


def fort_wall28():
    fort_wall()  # the locked shape (round 27 A); every container now goes through the round 28 obox()
    S = 21.0
    gx = S
    if TEX["hazard"]:
        hazard_band((gx + 3.45, -3.6), (gx + 3.45, 3.6), 0.2, 1.4, n=8)  # gate threshold
        for sy in (-1, 1):  # gate-tower feet and corner-tower feet facing +X
            hazard_band((gx + 3.6, sy * 7.6 - 3.4), (gx + 3.6, sy * 7.6 + 3.4), 0.2, 2.0, n=6)
            hazard_band((S + 5.1, sy * S - 4.8), (S + 5.1, sy * S + 4.8), 0.2, 2.0, n=8)
    if TEX["stencil"]:  # big stencilled codes on the two front corner towers and the gate block
        for sy in (-1, 1):
            text_obj(STENCILS[1 + sy], (S + 5.4, sy * S, 3 * HC + 2.5), (math.radians(90), 0, math.radians(90)), 1.4, SIGNM)
    if TEX["tarps"]:
        for (y0, y1, c) in ((-17, -11, (0.20, 0.36, 0.52)), (10, 16, (0.30, 0.42, 0.20))):
            pass
        for (x, y0, y1, z, c) in ((S + 5.2, -S - 4, -S + 4, 7 * HC, (0.20, 0.36, 0.52)), (S + 5.2, S - 4, S + 4, 6 * HC, (0.30, 0.42, 0.20)),
                                  (gx + 3.7, 4.2, 10.6, 6 * HC, (0.62, 0.58, 0.48))):  # tarps hung down the front tower faces
            tarp((x - 2.6, y0), (x - 2.6, y1), z, 14.0, c)
        for (y0, y1, c) in ():
            tarp((S + 2.4, y0), (S + 2.4, y1), 4 * HC + 0.4, 12.0, c)
    if TEX["nets"]:
        cargo_net(S + 2.6, 11.0, 15.5, 1.0, 4 * HC - 1.0)
        cargo_net(S + 2.6, -15.5, -11.0, 2.0, 4 * HC - 2.0)
    if TEX["flood"]:  # floodlight pairs at every tower foot, cones washing up the tower faces
        for (tx, ty, sz) in ((S, -S, 10.0), (S, S, 10.0), (gx, -7.6, 7.0), (gx, 7.6, 7.0), (-S, -S, 10.0), (-S, S, 10.0)):
            for dy in (-sz * 0.3, sz * 0.3):
                fx = tx + sz / 2 + 3.0
                box(fx - 0.5, ty + dy - 0.5, 0, fx + 0.5, ty + dy + 0.5, 1.2, (0.2, 0.2, 0.22), facet=False)
                NEON.face([(fx - 0.55, ty + dy - 0.55, 1.25), (fx + 0.55, ty + dy - 0.55, 1.25), (fx + 0.55, ty + dy + 0.55, 1.25), (fx - 0.55, ty + dy + 0.55, 1.25)],
                          (1.0, 0.92, 0.75), (0, 0, 0))
                cone(Vector((fx, ty + dy, 1.3)), Vector((tx + sz / 2 + 0.6, ty + dy, 7 * HC * 0.85)), 0.4, 2.6, (0.85, 0.50, 0.16), n=10)


HEROES26["meridian"] = fort_wall28
