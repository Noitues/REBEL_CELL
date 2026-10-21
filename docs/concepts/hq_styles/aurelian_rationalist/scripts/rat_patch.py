"""Rationalist Rome patch for the Aurelian HQ: patches the base modules IN MEMORY (palette + landmark geometry); nothing
in route_map_graph/hq_aurelian is edited. Called from rat_blender.py after aur_env.setup(blender=True) and before the
engine's hq_scene.py is exec'd. Units: city units in canonical (x ks = kit BU)."""
import math
import sys

sys.dont_write_bytecode = True
import aurelian_landmark as AL  # noqa: E402
import hq_preset as HP  # noqa: E402

VERD = (0.022, 0.72, 0.38)             # #29DBA6 as linear light (the base palette used the sRGB triplet as linear: minty)
VERD_HI = (0.05, 1.0, 0.60)
TRAV = (0.70, 0.74, 0.76)              # cold white travertine (linear)
RAT = {}


def patch_palette(cfg):
    P = HP.PRESET["hq"]["palette"]
    P.update({
        "travertine": TRAV,
        "gilt": VERD_HI, "loggia": tuple(cfg.get("loggia", (0.10, 0.42, 0.34))),
        "uplight": (0.55, 0.72, 0.90), "cavea_fill": (0.60, 0.78, 1.0),
        "server": (0.12, 1.0, 0.62), "rim_a": VERD_HI, "rim_b": (0.45, 0.62, 1.0),
        "district_a": VERD, "district_b": (0.30, 0.45, 0.85),
        "accent_warm": (0.40, 0.65, 1.0), "gold": (0.12, 0.8, 0.5), "scan": (0.5, 1.0, 0.8),
        "sodium": (0.20, 0.45, 1.0), "work": (0.10, 0.75, 0.60),
    })
    HP.PRESET["hq"]["light"].update({k[2:]: v for k, v in cfg.items() if k.startswith("L.")})


def arcade_tier_rat(SURF, SMOOTH, cyl, sc, hx, hy, A_, Bk_, z0, z1, tr, k, piers, ent=0.7, base=0.25, rec=1.7):
    """One tier of the rationalist arcade: flat slabs, identical round arches with deep reveals, no engaged columns, no
    archivolt. Each arch opening gets a thin verdigris light frame (RAT['NEON'])."""
    TAU = 2 * math.pi
    rf, rb = A_ + AL.ARC_RF, A_ - rec
    zb, zt = z0 + base, z1 - ent
    c_face, c_pier, c_sof, c_jam = sc(tr, 0.96), sc(tr, 0.96), sc(tr, 0.30), sc(tr, 0.52)
    NEON, bar, vcol, vw = RAT.get("NEON"), RAT.get("bar"), RAT["vcol"], RAT["vw"]
    n = len(piers)

    def pt(ta, s, rate, z, rr):
        t = ta + s / rate
        return (hx + rr * math.cos(t), hy + rr * Bk_ * math.sin(t), z)
    for i in range(n):
        ta, ha = piers[i]
        tb, hb = piers[(i + 1) % n]
        if tb <= ta:
            tb += TAU
        tm = (ta + tb) / 2
        rate = AL._arc_rate(A_, Bk_, tm)
        S = (tb - ta) * rate
        wd = S - ha - hb
        ri = wd / 2.0
        sc_ = ha + ri
        zs = max(zb + 0.8, zt - 0.06 - ri - 0.35)          # taller opening: a head closer to the entablature
        SURF.face([pt(ta, 0.0, rate, zb, rf), pt(ta, ha, rate, zb, rf), pt(ta, ha, rate, zt, rf), pt(ta, 0.0, rate, zt, rf)], c_pier)
        SURF.face([pt(ta, S - hb, rate, zb, rf), pt(ta, S, rate, zb, rf), pt(ta, S, rate, zt, rf), pt(ta, S - hb, rate, zt, rf)], c_pier)
        SURF.face([pt(ta, ha, rate, zb, rb), pt(ta, ha, rate, zb, rf), pt(ta, ha, rate, zs, rf), pt(ta, ha, rate, zs, rb)], c_jam)
        SURF.face([pt(ta, S - hb, rate, zb, rf), pt(ta, S - hb, rate, zb, rb), pt(ta, S - hb, rate, zs, rb), pt(ta, S - hb, rate, zs, rf)], c_jam)
        arc = []
        for j in range(AL.ARC_N + 1):
            ph = math.pi * j / AL.ARC_N
            arc.append((sc_ - ri * math.cos(ph), zs + ri * math.sin(ph)))
        for j in range(AL.ARC_N):
            a, b = arc[j], arc[j + 1]
            SURF.face([pt(ta, a[0], rate, a[1], rf), pt(ta, b[0], rate, b[1], rf), pt(ta, b[0], rate, zt, rf), pt(ta, a[0], rate, zt, rf)], c_face)
            SURF.face([pt(ta, a[0], rate, a[1], rb), pt(ta, b[0], rate, b[1], rb), pt(ta, b[0], rate, b[1], rf), pt(ta, a[0], rate, a[1], rf)], c_sof)
        # the light frame: a thin verdigris line round the opening, just proud of the face
        if NEON is not None and ri > 0.35:
            fo = rf + 0.05
            path = [pt(ta, ha, rate, zb + 0.05, fo), pt(ta, ha, rate, zs, fo)]
            for j in range(1, AL.ARC_N):
                path.append(pt(ta, arc[j][0], rate, arc[j][1], fo))
            path += [pt(ta, S - hb, rate, zs, fo), pt(ta, S - hb, rate, zb + 0.05, fo)]
            for p0, p1 in zip(path[:-1], path[1:]):
                bar(NEON, p0, p1, vw, vcol)


def canonical_rat(ctx, hx, hy, open_bays=()):
    """The Circus Aurelius, rationalist: the arcade grid, white stepped terraces, a pure white columnar drum with a
    verdigris core, square campanile shafts. Same footprint, tiers, ring radii and Rostrum height as the base."""
    SURF, SMOOTH, NEON = ctx.SURF, ctx.SMOOTH, ctx.NEON
    prism, box, cyl, bar = ctx.prism, ctx.box, ctx.cyl, ctx.bar
    ring_line, annulus, circle, sc = ctx.ring_line, ctx.annulus, ctx.circle, ctx.sc
    D = ctx.district
    tr, sec = D["mat"][0], D["sec"]
    LM = AL._lm(ctx)
    A, BK, TIERS, TIER_H, ATTIC_H = AL.A, AL.BK, AL.TIERS, AL.TIER_H, AL.ATTIC_H
    rec, n, th, attic = LM["recess"], AL.NSEG, TIER_H, ATTIC_H
    RAT.update(NEON=NEON, bar=bar, vcol=sec)
    for k in range(TIERS):
        z0, z1 = k * th, (k + 1) * th
        prism(SURF, circle(hx, hy, A - rec, n, ry=(A - rec) * BK), z0, z1, sc(tr, 0.50), top=False)
        arcade_tier_rat(SURF, SMOOTH, cyl, sc, hx, hy, A, BK, z0, z1, tr, k,
                        AL.arcade_piers(A, BK, LM["cols"], [(t0, t1) for (kb, t0, t1) in open_bays if kb == k]), rec=rec)
        # a flat plinth lip and a flat, heavy entablature slab (no mouldings)
        prism(SURF, circle(hx, hy, A + 0.45, n, ry=A * BK + 0.45), z0, z0 + 0.25, sc(tr, 0.92), top=False)
        prism(SURF, circle(hx, hy, A + 0.55, n, ry=A * BK + 0.55), z1 - 0.7, z1, sc(tr, 1.0), top=False)
        k1 = (A * BK + 0.55) / (A + 0.55)
        annulus(SURF, hx, hy, z1, A - rec, A + 0.55, sc(tr, 1.0), n=n, k0=BK, k1=k1)
        annulus(SURF, hx, hy, z1 - 0.7, A - rec, A + 0.55, sc(tr, 0.6), n=n, k0=BK, k1=k1)
        # the tier's horizontal light line under the slab: a single thin verdigris ring (the grid glows both ways)
        ring_line(NEON, hx, hy, z1 - 0.78, A + 0.58, 0.05, sec, n=n, ry=A * BK + 0.58)
    zt = TIERS * th
    prism(SURF, circle(hx, hy, A + 0.2, n, ry=A * BK + 0.2), zt, zt + attic, sc(tr, 0.97), top=False)
    ring_line(SURF, hx, hy, zt + attic, A + 0.35, 0.5, sc(tr, 1.05), n=n, ry=A * BK + 0.35)
    ring_line(NEON, hx, hy, zt + attic + 0.3, A + 0.4, 0.07, sec, n=n, ry=A * BK + 0.4)
    # the stepped white terraces: bright, stark
    T = AL.terraces(LM["steps"])
    for i, (ro, ri, zm, k, m) in enumerate(T):
        zn = T[i + 1][2] if i + 1 < len(T) else AL.RING_Z[4]
        annulus(SURF, hx, hy, zm, ri, ro, sc(tr, 1.00 if m % 2 == 0 else 0.90), n=n, k0=BK, k1=BK)
        prism(SURF, circle(hx, hy, ri, n, ry=ri * BK), zn, zm, sc(tr, 0.62), top=False)
        if m == LM["steps"] - 1:
            ring_line(NEON, hx, hy, zm + 0.05, ri, 0.05, sec, n=n, ry=ri * BK)
    prism(SURF, circle(hx, hy, AL.RING_R[4], n, ry=AL.RING_R[4] * BK), 0.0, 3.0, sc(tr, 0.80), top=True)
    ring_line(NEON, hx, hy, 3.02, AL.RING_R[4] * 0.55, 0.06, sec, n=n, ry=AL.RING_R[4] * BK * 0.55)
    # the Rostrum: a pure white columnar drum on a porphyry pad, verdigris-lit core
    R = AL.ROSTRUM
    cyl(SURF, hx, hy, R["plinth_z"][0], R["plinth_z"][1], R["plinth_r"], 24, (0.040, 0.010, 0.022))      # porphyry #3A1426
    zA, zB = R["tholos_z"]
    WH = (0.95, 0.97, 0.98)
    NC = 24
    for kk in range(NC):
        t = 2 * math.pi * (kk + 0.5) / NC
        x, y = hx + R["tholos_r"] * math.cos(t), hy + R["tholos_r"] * math.sin(t)
        bar(SURF, (x, y, zA), (x, y, zB), 0.5, WH)
    cyl(SURF, hx, hy, zB, zB + 0.55, 4.9, 24, WH)
    cyl(SURF, hx, hy, zB + 0.55, zB + 0.80, 4.5, 24, sc(WH, 0.9))
    cyl(NEON, hx, hy, zA + 0.2, R["core_top"], R["core_r"], 14, sc(sec, 0.55), top=True)       # the verdigris-lit core
    for zz in R["rings_z"]:
        cyl(SURF, hx, hy, zz, zz + 0.35, 2.15, 14, WH)
    ring_line(ctx.LAUREL, hx, hy, R["laurel_z"], R["laurel_r"], 0.20, sc(sec, 1.2), n=64)
    box(NEON, hx - 0.8, hy - 0.8, 22.0, hx + 0.8, hy + 0.8, 23.6, (0.5, 1.0, 0.85))
    # square campanile shafts (the base's four round towers): flat white blocks with slit lights, flat roofs
    for kk in range(4):
        t = math.radians(45 + 90 * kk)
        cx, cy = hx + (A + AL.CAMP_OFF) * math.cos(t), hy + (A * BK + AL.CAMP_OFF) * math.sin(t)
        hw = 2.0
        box(SURF, cx - hw * 1.3, cy - hw * 1.3, 0, cx + hw * 1.3, cy + hw * 1.3, 3.0, sc(tr, 0.9))
        box(SURF, cx - hw, cy - hw, 3.0, cx + hw, cy + hw, 31.0, sc(tr, 0.95))
        box(SURF, cx - hw * 1.12, cy - hw * 1.12, 31.0, cx + hw * 1.12, cy + hw * 1.12, 32.2, sc(tr, 1.02))
        for s_ in (-1, 1):
            for z_ in (8.0, 14.0, 20.0, 26.0):
                box(NEON, cx + s_ * hw + (0.02 if s_ > 0 else -0.14), cy - 0.14, z_, cx + s_ * hw + (0.14 if s_ > 0 else -0.02), cy + 0.14, z_ + 4.0, (0.3, 1.0, 0.7))
        box(NEON, cx - hw * 1.12, cy - hw * 1.12, 32.2, cx + hw * 1.12, cy + hw * 1.12, 32.4, sec)
    return dict(label=(hx, hy, 40.0), crown=(hx, hy, 26.0), hue=tuple(sec))


def apply_pre(cfg):
    patch_palette(cfg)
    RAT["vw"] = float(cfg.get("frame_w", 0.10))
    AL.canonical = canonical_rat
