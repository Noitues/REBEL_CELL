"""ATLANTIS STATION, round 2: the FLOATING PIER CITY (designer note 4, Kamino / Tipoca City). Reusable landmark module.

ENTRY POINTS
    import tethys_landmark as TL
    info = TL.build(ns, centre=None, water_z=None, bed_z=None, lot_r=None, seed=None)
    label, crown, hue = TL.landmark(ns)          # drop-in for city_all_corps landmarks.tethys()

`ns` is a city_all_corps build namespace (the exec globals of city_build.py), or any dict that provides:
    SURF, SMOOTH, NEON, GLASS          face accumulators (city_build.Acc: .face(pts, col, uv, wc, wl, wm, bid, wet))
    box, bar, cyl, dome, ring_line, annulus, sc       the city_build primitives
    spot_at(target, frm, col, power, cone)            landmark key lights (city_render turns them into spots)
    ZW (water z), W (lot -> world), O (zoning; O["hq"]["tethys"] = the HQ lot), ground_at(x, y) (seabed z; optional)
Defaults: centre = W(O["hq"]["tethys"]), water_z = ZW, bed_z = ground_at(centre) (or -110), lot_r = 34 BU
(city_preset.LANDMARK_FP["tethys"]), seed = tethys_preset.SEEDS["pier"]. All shapes are rules on tethys_preset.PIER.

What it builds (all inside the lot circle):
  MAIN STATION  the dominant structure: ten stilts, a flared skirt, a wide lit drum, a low flattened dome, a second
                tier with its own dome, a tapering mast with the abyss-blue halo and a red beacon (the hero beam source)
  PODS          18 small copies of the station (the same generator at scale s): 6 inner pods on the six piers, 6 at
                the pier ends, 6 between them on the ring walkway; s >= 0.4 pods keep the second tier
  PIERS         six radial glass-tube walkways on piles, and the ring walkway linking the outer pods
  BELOW         every stilt runs down to the seabed through the clear water; under the station the glass shaft with
                the lift core, five pressure decks hung down the trench, the ballast column (the tide gauge), and
                THE BLACK SMOKER at the trench floor: vent chimneys, the hot glow, the white server ring (the target)
Returns info: dict(label, crown, hue, rooms={name: xyz}, server xyz, pods [(x, y, s)], footprint radius).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))     # so the city's importlib hook finds tethys_preset / tkit
sys.dont_write_bytecode = True
import tethys_preset as TP
from tkit import frustum, obox, tube


def server_xy(hx, hy, PR=None):
    """Pure: the server's (x, y) for a station at (hx, hy) (the deep stair's end; map frame at yaw 135)."""
    ST = (PR or TP.PIER)["stair"]
    return (hx - 0.7071 * ST["seaward"] + 0.7071 * ST["lateral"], hy + 0.7071 * ST["seaward"] + 0.7071 * ST["lateral"])


def _stack(ns, cx, cy, s, hs, zb, bed, PR, bid, full=True, main=False):
    """One station at plan scale s and height scale hs, its skirt bottom at zb. -> (top z, rim z, mast top z)."""
    SURF, SMOOTH, NEON = (ns[k] for k in ("SURF", "SMOOTH", "NEON"))
    dome, ring_line, sc, box = ns["dome"], ns["ring_line"], ns["sc"], ns["box"]
    M = PR["main"]
    ek = PR["emit_k"]
    ZW = ns["ZW"]
    hull, dark, ti = PR["hull"], PR["hull_dark"], PR["titan"]
    nseg = 40 if main else 24
    # stilts: down through the water to the seabed, ring beams under the waterline, foam rings at the surface
    ns_ = M["stilts"] if main else (4 if s > 0.3 else 3)
    sr = M["stilt_r"] * s
    for k in range(ns_):
        a = 2 * math.pi * (k + 0.5) / ns_
        x, y = cx + sr * math.cos(a), cy + sr * math.sin(a)
        rad = 0.75 if main else 0.25 + 0.5 * s
        frustum(SMOOTH, x, y, bed, zb + 0.4, rad * 1.25, rad, 10, PR["stilt"], wet=1)
        ring_line(NEON, x, y, ZW + 0.04, rad + 0.25, 0.18, sc((0.8, 0.95, 1.0), 0.35), n=10)
    ring_line(SURF, cx, cy, ZW - 1.6, sr, 0.5 * max(s, 0.5), dark, n=ns_ * 2, wet=1)
    ring_line(SURF, cx, cy, ZW - 14.0, sr, 0.4 * max(s, 0.5), dark, n=ns_ * 2, wet=1)
    # the flared skirt (underside), the lit drum, the flattened dome cap
    r0, r1 = M["skirt"][0] * s, M["skirt"][1] * s
    zs1 = zb + (M["z_skirt"][1] - M["z_skirt"][0]) * hs
    PD = PR["pod_detail"]
    wcol = sc(PR["win_col"], PR["win_k"])                 # warm window detail (AD review 2)
    frustum(SURF, cx, cy, zb, zs1, r0, r1, nseg, dark, bottom=True, wc=wcol, wl=PD["port_wl"], wm=2, bid=bid + 0.21)
    rd = M["drum"][0] * s
    zd1 = zs1 + (M["drum"][2] - M["drum"][1]) * hs
    frustum(SURF, cx, cy, zs1, zd1, rd, rd, nseg, hull, wc=wcol, wl=0.82, wm=1, bid=bid)
    hue_k = sc(TP.ABYSS, PR["ring_k"])
    ring_line(NEON, cx, cy, zs1 + 0.05, r1 + 0.08, 0.32 * max(s, 0.5), hue_k, n=nseg)
    ring_line(NEON, cx, cy, zd1 + 0.04, rd + 0.08, 0.30 * max(s, 0.5), hue_k, n=nseg)
    cr = M["cap"][0] * s
    cz = M["cap"][1] * hs / s                 # the cap's height follows the height scale
    dome(SMOOTH, cx, cy, zd1, cr, hull, n=nseg, rings=7, zscale=cz, bid=bid)
    top = zd1 + cr * cz
    # porthole ring in the cap (lit)
    nph = 16 if main else 8
    for k in range(nph):
        a = 2 * math.pi * k / nph
        rr_ = cr * 0.78
        zz = zd1 + cr * cz * math.sqrt(max(0.0, 1 - 0.78 ** 2)) + 0.05
        x, y = cx + rr_ * math.cos(a), cy + rr_ * math.sin(a)
        box(NEON, x - 0.35 * s - 0.1, y - 0.35 * s - 0.1, zz - 0.1, x + 0.35 * s + 0.1, y + 0.35 * s + 0.1, zz + 0.12 * s + 0.05,
            sc(TP.DIVE, 0.8 * ek))
    crown = top
    if full:
        tr, tz0, tz1 = M["tier"][0] * s, M["tier"][1], M["tier"][2]
        # the tier stands on the cap: its base sinks just below the cap surface at the tier's radius
        z0 = zd1 + cr * cz * math.sqrt(max(0.0, 1.0 - (tr * 1.05 / cr) ** 2)) - 0.25 * hs
        z1 = z0 + (tz1 - tz0) * hs
        frustum(SURF, cx, cy, z0, z1, tr * 1.05, tr, 28 if main else 16, hull, wc=wcol, wl=0.9, wm=1, bid=bid + 0.37)
        ring_line(NEON, cx, cy, z1 + 0.04, tr + 0.08, 0.28 * max(s, 0.5), sc(TP.PHOTO, PR["ring_k"]), n=28)
        tcz = M["tier_cap"][1] * hs / s
        dome(SMOOTH, cx, cy, z1, tr, hull, n=28 if main else 16, rings=6, zscale=tcz, bid=bid)
        crown = z1 + tr * tcz
    # the mast (tapered), its halo ring and spokes (main only), a red beacon
    mr, mz0, mz1 = M["mast"]
    mh = (mz1 - mz0) * (hs if main else hs * 0.7)
    m0 = crown - 0.3
    frustum(SURF, cx, cy, m0, m0 + mh, mr * max(s, 0.3), mr * max(s, 0.3) * 0.3, 10, ti, top=True)
    if main:
        hr, hz = M["halo"]
        zh = m0 + (hz - mz0) * hs
        ring_line(NEON, cx, cy, zh, hr, 0.45, sc(TP.ABYSS, 0.8 * ek), n=36)
        ring_line(NEON, cx, cy, zh + 1.6, hr * 0.62, 0.3, sc(TP.ABYSS, ek), n=28)
        for k in range(6):
            a = 2 * math.pi * k / 6
            ns["bar"](SURF, (cx, cy, zh), (cx + hr * math.cos(a), cy + hr * math.sin(a), zh), 0.18, ti)
    box(NEON, cx - 0.3, cy - 0.3, m0 + mh, cx + 0.3, cy + 0.3, m0 + mh + 0.6, TP.RED)
    if not main:
        # pod detail (AD review 2): small antennae with tip lights round the cap, and a dish on most pods
        rp = random.Random(int(bid * 100003) + 17)
        na = rp.randint(*PD["antennas"])
        for k in range(na):
            a = rp.uniform(0, 2 * math.pi)
            rr_ = cr * rp.uniform(0.35, 0.6)
            ax_, ay_ = cx + rr_ * math.cos(a), cy + rr_ * math.sin(a)
            az = zd1 + cr * cz * math.sqrt(max(0.0, 1 - (rr_ / cr) ** 2)) - 0.1
            h_ = rp.uniform(*PD["ant_h"])
            ns["bar"](SURF, (ax_, ay_, az), (ax_, ay_, az + h_), 0.07, ti)
            box(NEON, ax_ - 0.09, ay_ - 0.09, az + h_, ax_ + 0.09, ay_ + 0.09, az + h_ + 0.18, PD["tip"] if k % 2 == 0 else (0.9, 0.95, 1.0))
        if rp.random() < PD["dish_p"]:
            a = rp.uniform(0, 2 * math.pi)
            rr_ = cr * 0.5
            dx_, dy_ = cx + rr_ * math.cos(a), cy + rr_ * math.sin(a)
            dz = zd1 + cr * cz * 0.85
            ns["bar"](SURF, (dx_, dy_, dz - 0.3), (dx_, dy_, dz + 0.4), 0.1, ti)
            obox(SURF, dx_, dy_, dz + 0.3, 0.12, 1.1 * max(s, 0.3) * 3, 1.1 * max(s, 0.3) * 3, a, (0.62, 0.64, 0.68), pitch=0.5)
    return top, zd1, m0 + mh


def build_ns(ns, centre=None, water_z=None, bed_z=None, lot_r=None, seed=None):
    PR = TP.PIER
    SURF, SMOOTH, NEON, GLASS = (ns[k] for k in ("SURF", "SMOOTH", "NEON", "GLASS"))
    box, bar, cyl, ring_line, sc, spot_at = ns["box"], ns["bar"], ns["cyl"], ns["ring_line"], ns["sc"], ns["spot_at"]
    ZW = ns["ZW"] if water_z is None else water_z
    hx, hy = centre or ns["W"](ns["O"]["hq"]["tethys"])
    gat = ns.get("ground_at")
    bed_here = bed_z if bed_z is not None else (gat(hx, hy) if gat else -110.0)
    lot_r = lot_r or PR["lot_r"]
    rr = random.Random(seed if seed is not None else TP.SEEDS["pier"])

    def bed_at(x, y):
        return gat(x, y) if gat else bed_here

    M = PR["main"]
    rooms = {}
    pods = []
    # -------------------------------------------------- the main station
    zb = ZW + M["z_skirt"][0]
    ms = PR["main_s"]
    top, rim, crown = _stack(ns, hx, hy, ms, PR["main_hs"], zb, bed_here, PR, 0.05, full=True, main=True)
    rooms["main_deck"] = (hx, hy, rim)
    rooms["crown"] = (hx, hy, top + 3.0)
    # -------------------------------------------------- pods on the six piers and the ring
    # one pier points at the DOCK LOCK (the causeway lands on its end pod); without a lock, PIER.arm0
    lk = ns["O"].get("tethys_lock") if isinstance(ns.get("O"), dict) else None
    ang0 = math.atan2(lk["P"][1] - hy, lk["P"][0] - hx) if lk else math.radians(PR["arm0"])
    arms = PR["arms"]
    ring_pods = []
    for k in range(arms):
        a = ang0 + 2 * math.pi * k / arms
        for key in ("inner", "outer"):
            r, s, hs = PR[key]["r"], PR[key]["s"], PR[key]["hs"]
            x, y = hx + r * math.cos(a), hy + r * math.sin(a)
            zbp = ZW + PR["deck_z"] - 2.0 * hs - 0.6
            t_, rim_, _ = _stack(ns, x, y, s, hs, zbp, bed_at(x, y), PR, 0.1 + 0.05 * k + (0.5 if key == "outer" else 0.0),
                                 full=hs >= PR["full_hs"])
            pods.append((x, y, s))
            rooms["%s_%d" % (key, k)] = (x, y, t_ + 1.0)
            if key == "outer":
                ring_pods.append((a, x, y, s))
        am = a + math.pi / arms
        r, s, hs = PR["mid"]["r"], PR["mid"]["s"], PR["mid"]["hs"]
        x, y = hx + r * math.cos(am), hy + r * math.sin(am)
        zbp = ZW + PR["deck_z"] - 2.0 * hs - 0.6
        t_, rim_, _ = _stack(ns, x, y, s, hs, zbp, bed_at(x, y), PR, 0.3 + 0.05 * k, full=False)
        pods.append((x, y, s))
        rooms["mid_%d" % k] = (x, y, t_ + 1.0)
        ring_pods.append((am, x, y, s))
    # -------------------------------------------------- walkways: six radial piers (glass tubes on piles) + the ring
    zw = ZW + PR["deck_z"]

    def walk(p0, p1, rt=1.0):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy)
        if L < 0.5:
            return
        ux, uy = dx / L, dy / L
        vx, vy = -uy, ux
        from tkit import seg_box
        seg_box(SURF, p0, p1, 2.0 * rt, zw - 0.45, zw, PR["hull_dark"])
        tube(GLASS, (p0[0], p0[1], zw + 0.9 * rt), (p1[0], p1[1], zw + 0.9 * rt), 1.15 * rt, 10, (0.6, 0.85, 1.0))
        for side in (-1, 1):
            bar(NEON, (p0[0] + vx * side * 0.95 * rt, p0[1] + vy * side * 0.95 * rt, zw - 0.2),
                (p1[0] + vx * side * 0.95 * rt, p1[1] + vy * side * 0.95 * rt, zw - 0.2), 0.1, sc(TP.PHOTO, 0.6))
        n = max(1, int(L / 2.6))
        for m in range(n + 1):
            f = m / n
            cxx, cyy = p0[0] + dx * f, p0[1] + dy * f
            prev = None
            for kk in range(9):
                an = math.pi * kk / 8
                pp = (cxx + vx * math.cos(an) * 1.2 * rt, cyy + vy * math.cos(an) * 1.2 * rt, zw + 0.9 * rt + math.sin(an) * 1.2 * rt - 0.0)
                if prev:
                    bar(SURF, prev, pp, 0.09, PR["titan"])
                prev = pp
        s_ = 3.0
        while s_ < L - 2.0:
            x, y = p0[0] + ux * s_, p0[1] + uy * s_
            tube(SMOOTH, (x, y, bed_at(x, y)), (x, y, zw - 0.45), 0.28, 6, PR["titan"], wet=1)
            s_ += 9.0
    for k in range(arms):
        a = ang0 + 2 * math.pi * k / arms
        ca, sa = math.cos(a), math.sin(a)
        ri = PR["inner"]["r"]
        ro = PR["outer"]["r"]
        rd_main = M["skirt"][1]
        rd_in = M["skirt"][1] * PR["inner"]["s"]
        rd_out = M["skirt"][1] * PR["outer"]["s"]
        r_m = M["skirt"][0] * ms + 1.2
        walk((hx + ca * r_m, hy + sa * r_m), (hx + ca * (ri - rd_in + 0.4), hy + sa * (ri - rd_in + 0.4)), 1.15)
        walk((hx + ca * (ri + rd_in - 0.4), hy + sa * (ri + rd_in - 0.4)), (hx + ca * (ro - rd_out + 0.4), hy + sa * (ro - rd_out + 0.4)), 0.9)
    ring_pods.sort(key=lambda t: t[0])
    for k in range(len(ring_pods)):
        a0, x0, y0, s0 = ring_pods[k]
        a1, x1, y1, s1 = ring_pods[(k + 1) % len(ring_pods)]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        r0_, r1_ = M["skirt"][1] * s0, M["skirt"][1] * s1
        walk((x0 + dx / L * (r0_ - 0.4), y0 + dy / L * (r0_ - 0.4)), (x1 - dx / L * (r1_ - 0.4), y1 - dy / L * (r1_ - 0.4)), 0.75)
    # moored craft at the outer pods (nav lights), a buoy line round the lot edge (the station's waterline fence)
    for (a, x, y, s) in ring_pods[::2]:
        ox, oy = x + math.cos(a) * (M["skirt"][1] * s + 2.2), y + math.sin(a) * (M["skirt"][1] * s + 2.2)
        yaw = a + math.pi / 2
        obox(SMOOTH, ox, oy, ZW - 0.5, 4.2, 1.3, 1.2, yaw, (0.62, 0.66, 0.72))
        box(NEON, ox - 0.12, oy - 0.12, ZW + 0.8, ox + 0.12, oy + 0.12, ZW + 1.0, (1.0, 0.1, 0.1))
    for k in range(36):
        a = 2 * math.pi * k / 36
        x, y = hx + (lot_r + 0.5) * math.cos(a), hy + (lot_r + 0.5) * math.sin(a)
        cyl(SURF, x, y, ZW - 0.6, ZW + 0.5, 0.35, 8, (0.62, 0.20, 0.22))
        if k % 3 == 0:
            box(NEON, x - 0.12, y - 0.12, ZW + 0.5, x + 0.12, y + 0.12, ZW + 0.75, sc(TP.ABYSS, 1.2))
    # -------------------------------------------------- THE BREAKWATER (AD review 2): the hex ring walkway stands on a
    # solid breakwater through the ring pods; inside it the water is glass-calm (the water material reads PIER.breakwater
    # .calm_r: no chop, low reflection), the see-through window down to the moon pool and the server
    BW = PR["breakwater"]
    from tkit import seg_box
    for k in range(len(ring_pods)):
        a0, x0, y0, s0 = ring_pods[k]
        a1, x1, y1, s1 = ring_pods[(k + 1) % len(ring_pods)]
        seg_box(SURF, (x0, y0), (x1, y1), BW["w"], ZW + BW["z0"], ZW + BW["z1"], PR["hull_dark"], wet=1)
        mx_, my_ = (x0 + x1) / 2 - hx, (y0 + y1) / 2 - hy
        L_ = math.hypot(mx_, my_) or 1.0
        ox_, oy_ = mx_ / L_ * (BW["w"] / 2 + 0.25), my_ / L_ * (BW["w"] / 2 + 0.25)
        bar(NEON, (x0 + ox_, y0 + oy_, ZW + 0.06), (x1 + ox_, y1 + oy_, ZW + 0.06), 0.35, sc((0.8, 0.92, 1.0), 0.22))   # surf line
        bar(NEON, (x0, y0, ZW + BW["z1"] + 0.02), (x1, y1, ZW + BW["z1"] + 0.02), 0.12, sc(TP.PHOTO, 0.5))
    # -------------------------------------------------- below the water: THE DEEP STAIR to the MOON POOL and the server
    bed = bed_here
    ST, MP = PR["stair"], PR["moonpool"]
    sea = (-0.7071, 0.7071)            # +b (seaward) at the map yaw 135
    lat = (0.7071, 0.7071)             # screen-right at the map yaw 135
    zsv = ZW + ST["server_z"]
    sx_, sy_ = hx + sea[0] * ST["seaward"] + lat[0] * ST["lateral"], hy + sea[1] * ST["seaward"] + lat[1] * ST["lateral"]

    def spine(z):
        """the stair's spine: from under the station (deck 1) to the server, linear in depth."""
        f = (z - (ZW + PR["decks"][0])) / (zsv - (ZW + PR["decks"][0]))
        f = 0.25 + 0.75 * max(0.0, min(1.0, f))
        return hx + (sx_ - hx) * f, hy + (sy_ - hy) * f
    # the station's own glass shaft (the lift core lit) down to deck 1
    d1 = spine(ZW + PR["decks"][0])
    tube(GLASS, (hx, hy, zb + 0.5), (d1[0], d1[1], ZW + PR["decks"][0]), PR["shaft_r"], 16, (0.6, 0.85, 1.0), wet=1)
    tube(NEON, (hx, hy, zb), (d1[0], d1[1], ZW + PR["decks"][0]), 0.5, 6, sc(TP.DIVE, 0.6), wet=1)
    prev = None
    for k, (dz, rdk) in enumerate(zip(PR["decks"], PR["deck_r"])):
        zd = ZW + dz
        dx_, dy_ = spine(zd)
        frustum(SURF, dx_, dy_, zd - 1.8, zd, rdk * 0.86, rdk, 32, PR["titan"], wet=1, top=True, bottom=True,
                wc=TP.DIVE, wl=0.85, wm=2, bid=0.2 + 0.1 * k)
        ring_line(NEON, dx_, dy_, zd + 0.05, rdk + 0.06, 0.4, sc(TP.ABYSS, PR["deep_k"]), n=32, wet=1)
        ring_line(NEON, dx_, dy_, zd - 1.85, rdk * 0.86 + 0.06, 0.28, sc(TP.PHOTO, PR["deep_k"]), n=32, wet=1)
        for m in range(4):                                  # rooms on the deck rim (lit pods)
            a = 2 * math.pi * m / 4 + k * 0.5
            x, y = dx_ + (rdk - 1.3) * math.cos(a), dy_ + (rdk - 1.3) * math.sin(a)
            box(SURF, x - 0.8, y - 0.8, zd, x + 0.8, y + 0.8, zd + 1.3, PR["titan"], wc=TP.DIVE, wl=0.95, wm=0, bid=0.4 + m * 0.07, wet=1)
        rooms["deck_%d" % (k + 1)] = (dx_, dy_, zd + 1.3)
        if prev is not None:                                # the glass drop from the deck above, the lift light inside
            tube(GLASS, (prev[0], prev[1], prev[2] - 1.8), (dx_, dy_, zd), 1.0, 10, (0.6, 0.85, 1.0), wet=1)
            tube(NEON, (prev[0], prev[1], prev[2] - 1.8), (dx_, dy_, zd), 0.25, 6, sc(TP.DIVE, PR["deep_k"] * 0.6), wet=1)
        prev = (dx_, dy_, zd)
    # the ballast column (the tide gauge) beside the station
    bx, by = hx - 11.0, hy + 8.0
    cyl(GLASS, bx, by, ZW - 40.0, ZW + 9.0, 1.5, 12, (0.6, 0.85, 1.0), wet=1)
    cyl(NEON, bx, by, ZW - 40.0, ZW - 18.0, 1.2, 12, sc(TP.ABYSS, 0.55), wet=1)
    ring_line(NEON, bx, by, ZW - 18.0, 1.6, 0.4, TP.PHOTO, n=12, wet=1)
    # THE MOON POOL: a lit well from the calm surface (a floating collar ring) straight down to the server
    ring_line(SURF, sx_, sy_, ZW + 0.2, MP["r"] + 0.5, 0.9, PR["hull_dark"], n=28)
    ring_line(NEON, sx_, sy_, ZW + 0.55, MP["r"] + 0.5, 0.8, sc(MP["cyan"], MP["collar_k"]), n=40)      # AD review 3: a bright cyan collar
    ring_line(NEON, sx_, sy_, ZW + 0.6, MP["r"] - 0.4, 0.35, sc((0.85, 0.99, 1.0), MP["collar_k"] * 0.8), n=40)
    frustum(NEON, sx_, sy_, zsv + 2.0, ZW - 0.8, MP["r"] - 0.3, MP["r"] - 0.3, 24, sc(MP["cyan"], MP["column_k"]), wet=1)   # the soft light column
    zz, m = ZW - 1.5, 0
    while zz > zsv + 2.0:
        ring_line(NEON, sx_, sy_, zz, MP["r"], 0.16, sc(MP["cyan"] if m % 2 == 0 else (0.85, 0.97, 1.0), MP["k"]), n=24, wet=1)
        zz -= MP["step"]
        m += 1
    for k in range(4):                                    # the well's guide rails
        a = 2 * math.pi * k / 4 + 0.3
        bar(SURF, (sx_ + MP["r"] * math.cos(a), sy_ + MP["r"] * math.sin(a), ZW - 0.5),
            (sx_ + MP["r"] * math.cos(a), sy_ + MP["r"] * math.sin(a), zsv + 1.0), 0.18, PR["titan"], wet=1)
    # THE BLACK SMOKER: its chimney stack rises from the trench floor (a vent mound, five black chimneys); the core caps
    # the stack at the foot of the moon pool: a dark hull ring, the white server ring (the target), the abyss ring
    SV = PR["server"]
    bsv = bed_at(sx_, sy_)
    frustum(SURF, sx_, sy_, bsv - 1.0, bsv + 6.0, 9.0, 4.0, 16, (0.06, 0.055, 0.05), wet=1)          # the vent mound
    for k, (ox, oy, dh) in enumerate(((0.0, 0.0, 0.0), (2.4, -1.6, -3.0), (-2.2, 1.4, -5.0), (1.0, 2.6, -7.0), (-1.4, -2.4, -4.0))):
        ztop = zsv - 1.2 + dh
        rr0 = SV["chimney_r"] * (1.0 - 0.12 * k)
        frustum(SURF, sx_ + ox, sy_ + oy, bsv + 4.0, ztop, rr0 * 1.7, rr0 * 0.55, 10, (0.07, 0.06, 0.06), wet=1)
        if k:
            cyl(NEON, sx_ + ox, sy_ + oy, ztop - 0.2, ztop + 0.8, rr0 * 0.5, 8, sc((1.0, 0.42, 0.14), SV["vent_k"]), wet=1)
    ring_line(SURF, sx_, sy_, zsv - 0.5, SV["ring_r"] + 0.7, 1.0, (0.10, 0.11, 0.13), n=32, wet=1)
    ring_line(NEON, sx_, sy_, zsv + 0.4, SV["ring_r"], SV["ring_w"], sc((0.9, 0.97, 1.0), SV["core_k"]), n=32, wet=1)
    ring_line(NEON, sx_, sy_, zsv - 0.9, SV["ring_r"] + 1.5, 0.35, sc(TP.ABYSS, SV["abyss_k"]), n=32, wet=1)
    ring_line(NEON, sx_, sy_, zsv + 0.1, SV["ring_r"] + 1.15, 0.6, sc(SV["rim_col"], SV["rim_k"]), n=40, wet=1)       # the server's own warm rim
    cyl(NEON, sx_, sy_, zsv - 0.6, zsv + 0.9, 0.9, 10, sc((1.0, 0.42, 0.14), SV["vent_k"]), wet=1)   # the hot core
    for m in range(4):                                     # the core's struts onto the ring
        a = 2 * math.pi * m / 4 + 0.4
        bar(SURF, (sx_, sy_, zsv + 0.4), (sx_ + SV["ring_r"] * math.cos(a), sy_ + SV["ring_r"] * math.sin(a), zsv + 0.4), 0.3, (0.10, 0.11, 0.13), wet=1)
    tube(GLASS, (prev[0], prev[1], prev[2] - 1.8), (sx_, sy_, zsv + 1.0), 1.0, 10, (0.6, 0.85, 1.0), wet=1)
    tube(NEON, (prev[0], prev[1], prev[2] - 1.8), (sx_, sy_, zsv + 1.0), 0.25, 6, sc(TP.DIVE, PR["deep_k"] * 0.6), wet=1)
    # THE RISER: the server's cable riser up the moon pool's axis to the collar
    tube(NEON, (sx_, sy_, zsv + 1.0), (sx_, sy_, ZW - 0.6), SV["riser_r"], 8, sc((0.75, 0.9, 1.0), SV["riser_k"]), wet=1)
    rooms["vent_cap"] = ((prev[0] + sx_) / 2, (prev[1] + sy_) / 2, (prev[2] - 1.8 + zsv) / 2)
    server = (sx_, sy_, zsv + 0.4)
    rooms["server"] = server
    # -------------------------------------------------- lights: the key (cool white, camera side), the hue fill, the vent
    cam = (0.7071, -0.7071)
    spot_at((hx, hy, ZW + 14.0), (hx + cam[0] * 70 - 25, hy + cam[1] * 70 - 10, ZW + 95.0), PR["key"]["col"], PR["key"]["power"],
            PR["key"]["cone"])
    spot_at((hx, hy, ZW + 8.0), (hx - cam[0] * 60, hy - cam[1] * 60, ZW + 60.0), TP.ABYSS, PR["fill"]["power"], PR["fill"]["cone"])
    spot_at((sx_, sy_, zsv - 4.0), (sx_ + 2.0, sy_ - 2.0, ZW - 1.0), (0.85, 0.95, 1.0), SV["light"], 60.0)
    spot_at((sx_, sy_, zsv), (sx_, sy_, ZW - 1.0), MP["cyan"], MP["light"], 40.0)                                  # the cyan column from the collar
    spot_at((sx_, sy_, zsv + 0.3), (sx_ + 7.0, sy_ + 7.0, zsv + 3.0), SV["rim_col"], SV["rim_light"], 50.0)         # the warm rim light
    label = (hx, hy, crown + 6.0)
    return dict(label=label, crown=(hx, hy, crown), hue=TP.ABYSS, rooms=rooms, server=server, pods=pods,
                footprint=lot_r, centre=(hx, hy), bed=bed, top=crown)


def landmark(ns):
    """Drop-in for city_all_corps landmarks.tethys(): builds, fills ns["STATION"], returns (label, crown, hue)."""
    info = build_ns(ns)
    st = ns.get("STATION")
    if st is not None:
        st.update(centre=info["centre"], bed=info["bed"], decks=[ns["ZW"] + d for d in TP.PIER["decks"]],
                  rooms=info["rooms"], server=info["server"])
    ns["TETHYS_INFO"] = info
    return info["label"], info["crown"], info["hue"]


def build(ctx, **kw):
    """THE CITY HOOK (city_all_corps `city_preset.LANDMARK_MODULES["tethys"]`, NOTES.md "Landmark modules"):
    build(ctx) -> dict(label, crown, hue). Builds the pier city and its wildlife (fish shoals round the stilts and over
    the streets, the whale pod) with the city's accumulators and lights; sets ctx.station["centre"]. The dam, lock and
    drowned-street clutter (tethys_quarter.build_dam / build_clutter) need the reshaped zoning (prep_zoned) and are not
    part of the hook. A dict `ctx` (an exec namespace) keeps the old entry point: build(ns, centre=..., ...) -> info."""
    if isinstance(ctx, dict):
        return build_ns(ctx, **kw)
    ns = dict(SURF=ctx.SURF, SMOOTH=ctx.SMOOTH, NEON=ctx.NEON, GLASS=ctx.GLASS, box=ctx.box, bar=ctx.bar, cyl=ctx.cyl, dome=ctx.dome,
              ring_line=ctx.ring_line, annulus=ctx.annulus, sc=ctx.sc, spot_at=ctx.spot_at, ZW=ctx.zw, W=ctx.W, O=ctx.O,
              KH=ctx.CP.KH, STATION=ctx.station)
    info = build_ns(ns, centre=ctx.hq)
    ns["TETHYS_INFO"] = info
    from tethys_quarter import build_open_water_shoals, build_street_shoals
    build_street_shoals(ns)
    build_open_water_shoals(ns)
    build_whales(ns, info["centre"])
    ctx.station.update(centre=info["centre"], bed=info["bed"], decks=[ctx.zw + d for d in TP.PIER["decks"]], rooms=info["rooms"],
                       server=info["server"])
    return dict(label=info["label"], crown=info["crown"], hue=info["hue"])


# ===================================================================== wildlife: the whale pod (fish: tethys_quarter)
def _sea_top(ns, x, y, rad, KH):
    """The highest drowned-building top (z) within rad BU of (x, y): the whales swim over it."""
    top = -1e9
    Wf = ns["W"]
    for b in ns["O"]["buildings"]:
        if not b.get("wet"):
            continue
        q = [Wf(p) for p in b["q"]]
        cx, cy = sum(p[0] for p in q) / len(q), sum(p[1] for p in q) / len(q)
        ext = max(max(p[0] for p in q) - min(p[0] for p in q), max(p[1] for p in q) - min(p[1] for p in q)) / 2
        if math.hypot(cx - x, cy - y) <= rad + ext:
            top = max(top, b["z0"] * KH - b.get("sub", 0.0) + b["h"] * KH)
    return top


def _whale(ns, nose, heading, L, pitch, phase, PW):
    """One whale (a humpback-ish body lofted along a gently swimming spine, long pectoral flippers, a dorsal fin and
    flukes) into SMOOTH. nose: (x, y, z); heading (rad): the swim direction; the body trails behind the nose."""
    SMOOTH = ns["SMOOTH"]
    n, m = PW["stations"], PW["section_n"]
    h = (math.cos(heading), math.sin(heading))
    sd = (-h[1], h[0])
    Rm = 0.115 * L

    def spine(t):
        s = t * L
        lat = 0.055 * L * math.sin(2 * math.pi * 0.8 * t + phase) * (0.25 + t)
        vert = 0.02 * L * math.sin(2 * math.pi * 0.8 * t + phase + 1.3) * t + math.tan(pitch) * s * -1.0
        return (nose[0] - h[0] * s + sd[0] * lat, nose[1] - h[1] * s + sd[1] * lat, nose[2] + vert)

    def prof(t):
        if t < 0.30:
            return math.sin(t / 0.30 * math.pi / 2) ** 0.6
        x = (t - 0.30) / 0.70
        return 0.07 + 0.93 * (1 - x) ** 1.2

    def frame(t):
        a, b = spine(max(0.0, t - 0.02)), spine(min(1.0, t + 0.02))
        T = (a[0] - b[0], a[1] - b[1], a[2] - b[2])          # towards the head
        Tl = math.sqrt(sum(c * c for c in T))
        T = tuple(c / Tl for c in T)
        S = (-T[1], T[0], 0.0)
        Sl = math.hypot(S[0], S[1]) or 1.0
        S = (S[0] / Sl, S[1] / Sl, 0.0)
        U = (T[1] * S[2] - T[2] * S[1], T[2] * S[0] - T[0] * S[2], T[0] * S[1] - T[1] * S[0])
        return T, S, U

    def smooth(a, b, x):
        u = max(0.0, min(1.0, (x - a) / (b - a)))
        return u * u * (3 - 2 * u)
    rings, cols = [], []
    for i in range(n):
        t = i / (n - 1)
        p, (T, S, U), R = spine(t), frame(t), Rm * prof(t)
        rings.append([tuple(p[c] + S[c] * math.cos(2 * math.pi * k / m) * R + U[c] * math.sin(2 * math.pi * k / m) * R * 0.88
                            for c in range(3)) for k in range(m)])
    top, belly = PW["top"], PW["belly"]
    for i in range(n - 1):
        t = (i + 0.5) / (n - 1)
        for k in range(m):
            th = 2 * math.pi * (k + 0.5) / m
            w = smooth(-0.45, 0.35, math.sin(th))
            col = tuple(belly[c] + (top[c] - belly[c]) * w for c in range(3))
            if t < 0.5 and math.sin(th) < -0.3 and i % 2 == 0:
                col = tuple(c * 0.80 for c in col)          # the throat pleats
            SMOOTH.face([rings[i][k], rings[i][(k + 1) % m], rings[i + 1][(k + 1) % m], rings[i + 1][k]], col, wet=1)
    # flukes
    Tt, St, Ut = frame(1.0)
    F = spine(1.0)
    span = 0.36 * L
    for sg in (-1, 1):
        tip = tuple(F[c] + St[c] * sg * span / 2 - Tt[c] * 0.11 * L + Ut[c] * 0.015 * L for c in range(3))
        SMOOTH.face([tuple(F[c] + Tt[c] * 0.05 * L for c in range(3)), tip, tuple(F[c] - Tt[c] * 0.08 * L for c in range(3))], top, wet=1)
        SMOOTH.face([tuple(F[c] + Tt[c] * 0.05 * L for c in range(3)), tuple(F[c] - Tt[c] * 0.08 * L for c in range(3)), tip],
                    belly, wet=1)
    # pectoral flippers (long) and the dorsal fin
    T3, S3, U3 = frame(0.31)
    A0 = spine(0.31)
    for sg in (-1, 1):
        A = tuple(A0[c] + S3[c] * sg * Rm * 0.92 - U3[c] * Rm * 0.35 for c in range(3))
        tip = tuple(A[c] + S3[c] * sg * 0.17 * L - U3[c] * 0.10 * L - T3[c] * 0.13 * L for c in range(3))
        SMOOTH.face([tuple(A[c] + T3[c] * 0.045 * L for c in range(3)), tip, tuple(A[c] - T3[c] * 0.05 * L for c in range(3))],
                    PW["flipper"], wet=1)
    t0, t1 = 0.70, 0.77
    Td, Sd, Ud = frame(0.73)
    b0, b1 = spine(t0), spine(t1)
    R0, R1 = Rm * prof(t0) * 0.88, Rm * prof(t1) * 0.88
    apex = tuple(spine(0.76)[c] + Ud[c] * (Rm * prof(0.76) * 0.88 + 0.045 * L) for c in range(3))
    SMOOTH.face([tuple(b0[c] + Ud[c] * R0 for c in range(3)), tuple(b1[c] + Ud[c] * R1 for c in range(3)), apex], top, wet=1)


def build_whales(ns, centre=None, seed=None):
    """The migrating pod: WILDLIFE.whales.adults adults and a calf, on an arc (arc_r BU) round the station, in the open
    water beyond the breakwater (the map frame at yaw 135: the arc starts phi_deg from screen-right towards seaward). They swim
    clockwise, staggered in radius and depth, each one raised over any drowned tower below it, the calf alongside the
    second adult. One soft cool spot under the surface lights the pod. -> info (positions, depths, lengths)."""
    PW = TP.WILDLIFE["whales"]
    ZW, KH = ns["ZW"], ns.get("KH", 0.1657)
    hx, hy = centre or ns["W"](ns["O"]["hq"]["tethys"])
    rng = random.Random(seed if seed is not None else TP.SEEDS["whales"])
    sea, lat = (-0.7071, 0.7071), (0.7071, 0.7071)
    phi0 = math.radians(PW["phi_deg"])
    R0 = PW["arc_r"]
    out = []
    pod_c = [0.0, 0.0, 0.0]

    def place(x, y, hd, L, zc, pitch, phase, calf=False):
        rad = 0.115 * L
        top = _sea_top(ns, x, y, L * 0.55, KH)
        z = max(zc, top + PW["clear"] + rad)
        z = min(z, ZW - 2.0 - rad)
        nose = (x + math.cos(hd) * L / 2, y + math.sin(hd) * L / 2, z)
        _whale(ns, nose, hd, L, pitch, phase, PW)
        out.append(dict(x=round(x, 1), y=round(y, 1), z=round(z, 1), L=round(L, 1), calf=calf, heading=round(math.degrees(hd), 1)))
        return z

    na = PW["adults"]
    zs = []
    for i in range(na):
        ang = phi0 + PW["along"][i % len(PW["along"])] / R0
        rr = R0 + PW["dr"][i % len(PW["dr"])]
        ux, uy = lat[0] * math.cos(ang) + sea[0] * math.sin(ang), lat[1] * math.cos(ang) + sea[1] * math.sin(ang)
        x, y = hx + ux * rr, hy + uy * rr
        hd = math.atan2(math.sin(ang) * lat[1] - math.cos(ang) * sea[1], math.sin(ang) * lat[0] - math.cos(ang) * sea[0])
        hd += math.radians(rng.uniform(-7, 7))
        L = rng.uniform(*PW["L"])
        z = place(x, y, hd, L, ZW + PW["z"][i % len(PW["z"])], math.radians(rng.uniform(-4, 5)), rng.uniform(0, 6.28))
        zs.append((x, y, z, hd, L, rr, ang))
        pod_c[0] += x / na
        pod_c[1] += y / na
        pod_c[2] += z / na
    if PW["calf"] and na >= 2:
        x, y, z, hd, L, rr, ang = zs[1]
        Lc = L * PW["calf_k"]
        ux, uy = lat[0] * math.cos(ang) + sea[0] * math.sin(ang), lat[1] * math.cos(ang) + sea[1] * math.sin(ang)
        cx_, cy_ = x + ux * (0.30 * L) - math.cos(hd) * 0.10 * L, y + uy * (0.30 * L) - math.sin(hd) * 0.10 * L
        place(cx_, cy_, hd + math.radians(3.0), Lc, z + 0.8, math.radians(2.0), rng.uniform(0, 6.28), calf=True)
    LP = PW["light"]
    zl = min(ZW - 2.0, pod_c[2] + LP["up"])
    ns["spot_at"]((pod_c[0], pod_c[1], pod_c[2]), (pod_c[0] + 2.0, pod_c[1] - 2.0, zl), LP["col"], LP["power"], LP["cone"])
    print("TETHYS whales", out, flush=True)
    return dict(whales=out, centre=tuple(pod_c))
