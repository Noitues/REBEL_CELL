"""v2 (refined detail) landmark for the rationalist Aurelian: taller, narrower arches with a proud flat frame, keystone line, sill and a
recessed inner frame; rusticated base courses; architrave + stepped cornice; an abstract relief inscription band on the attic;
pilaster rhythm and stringcourses on the square towers; lit white risers; a two-stage white drum. In-memory patch like rat_patch."""
import math
import random
import sys

sys.dont_write_bytecode = True
import aurelian_landmark as AL  # noqa: E402
import hq_preset as HP  # noqa: E402
import rat_patch as RP  # noqa: E402

RAT = RP.RAT
VERD2 = (0.024, 0.52, 0.275)           # #2BBF8F-ish oxidised copper, linear


def arcade_tier_v2(SURF, SMOOTH, cyl, sc, hx, hy, A_, Bk_, z0, z1, tr, k, piers, ent=0.7, base=0.25, rec=1.7):
    TAU = 2 * math.pi
    rf, rb = A_ + AL.ARC_RF, A_ - rec
    base = 1.05 if k == 0 else base                        # rusticated plinth courses under the ground tier
    zb, zt = z0 + base, z1 - 1.5                           # an architrave band replaces the thin entablature
    c_face, c_pier, c_sof, c_jam = sc(tr, 0.96), sc(tr, 0.98), sc(tr, 0.30), sc(tr, 0.50)
    c_fr, c_in, c_key, c_sill = sc(tr, 1.04), sc(tr, 0.80), sc(tr, 1.08), sc(tr, 1.02)
    NEON, bar, vcol, vw = RAT.get("NEON"), RAT.get("bar"), RAT["vcol"], RAT["vw"]
    n = len(piers)
    fw, fp_, pr = 0.17, 0.10, 0.12                         # proud frame width / projection

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
        zs = max(zb + 0.8, zt - 0.10 - ri - 0.12)
        SURF.face([pt(ta, 0.0, rate, zb, rf), pt(ta, ha, rate, zb, rf), pt(ta, ha, rate, zt, rf), pt(ta, 0.0, rate, zt, rf)], c_pier)
        SURF.face([pt(ta, S - hb, rate, zb, rf), pt(ta, S, rate, zb, rf), pt(ta, S, rate, zt, rf), pt(ta, S - hb, rate, zt, rf)], c_pier)
        SURF.face([pt(ta, ha, rate, zb, rb), pt(ta, ha, rate, zb, rf), pt(ta, ha, rate, zs, rf), pt(ta, ha, rate, zs, rb)], c_jam)
        SURF.face([pt(ta, S - hb, rate, zb, rf), pt(ta, S - hb, rate, zb, rb), pt(ta, S - hb, rate, zs, rb), pt(ta, S - hb, rate, zs, rf)], c_jam)
        arc = []
        for j in range(AL.ARC_N + 1):
            ph = math.pi * j / AL.ARC_N
            arc.append((sc_ - ri * math.cos(ph), zs + ri * math.sin(ph), sc_ - (ri - 0.22) * math.cos(ph), zs + (ri - 0.22) * math.sin(ph),
                        sc_ - (ri + fw) * math.cos(ph), zs + (ri + fw) * math.sin(ph)))
        for j in range(AL.ARC_N):
            a, b = arc[j], arc[j + 1]
            SURF.face([pt(ta, a[0], rate, a[1], rf), pt(ta, b[0], rate, b[1], rf), pt(ta, b[0], rate, zt, rf), pt(ta, a[0], rate, zt, rf)], c_face)
            SURF.face([pt(ta, a[0], rate, a[1], rb), pt(ta, b[0], rate, b[1], rb), pt(ta, b[0], rate, b[1], rf), pt(ta, a[0], rate, a[1], rf)], c_sof)
            # proud flat frame band around the opening
            SURF.face([pt(ta, a[0], rate, a[1], rf + pr), pt(ta, b[0], rate, b[1], rf + pr), pt(ta, b[4], rate, b[5], rf + pr),
                       pt(ta, a[4], rate, a[5], rf + pr)], c_fr)
            SURF.face([pt(ta, a[0], rate, a[1], rf), pt(ta, b[0], rate, b[1], rf), pt(ta, b[0], rate, b[1], rf + pr), pt(ta, a[0], rate, a[1], rf + pr)], c_sof)
            # recessed inner frame: a ring set back in the reveal
            SURF.face([pt(ta, a[0], rate, a[1], rf - 1.1), pt(ta, b[0], rate, b[1], rf - 1.1), pt(ta, b[2], rate, b[3], rf - 1.1),
                       pt(ta, a[2], rate, a[3], rf - 1.1)], c_in)
        # frame jamb strips, sill and keystone
        for (s0, s1) in ((ha - fw, ha), (S - hb, S - hb + fw)):
            SURF.face([pt(ta, s0, rate, zb, rf + pr), pt(ta, s1, rate, zb, rf + pr), pt(ta, s1, rate, zs, rf + pr), pt(ta, s0, rate, zs, rf + pr)], c_fr)
        sw = ri + fw
        SURF.face([pt(ta, sc_ - sw - 0.12, rate, zb, rf + 0.38), pt(ta, sc_ + sw + 0.12, rate, zb, rf + 0.38),
                   pt(ta, sc_ + sw + 0.12, rate, zb + 0.14, rf + 0.38), pt(ta, sc_ - sw - 0.12, rate, zb + 0.14, rf + 0.38)], c_sill)
        SURF.face([pt(ta, sc_ - sw - 0.12, rate, zb + 0.14, rf + 0.38), pt(ta, sc_ + sw + 0.12, rate, zb + 0.14, rf + 0.38),
                   pt(ta, sc_ + sw + 0.12, rate, zb + 0.14, rf + pr), pt(ta, sc_ - sw - 0.12, rate, zb + 0.14, rf + pr)], c_sill)
        kt = zs + ri + fw
        SURF.face([pt(ta, sc_ - 0.17, rate, kt - 0.45, rf + pr + 0.07), pt(ta, sc_ + 0.17, rate, kt - 0.45, rf + pr + 0.07),
                   pt(ta, sc_ + 0.17, rate, kt + 0.2, rf + pr + 0.07), pt(ta, sc_ - 0.17, rate, kt + 0.2, rf + pr + 0.07)], c_key)
        # the light line: thin, on the outer edge of the proud frame
        if NEON is not None and ri > 0.3:
            fo = rf + pr + 0.03
            path = [pt(ta, ha - fw, rate, zb + 0.15, fo), pt(ta, ha - fw, rate, zs, fo)]
            for j in range(1, AL.ARC_N):
                path.append(pt(ta, arc[j][4] - 0.0, rate, arc[j][5], fo))
            path += [pt(ta, S - hb + fw, rate, zs, fo), pt(ta, S - hb + fw, rate, zb + 0.15, fo)]
            for p0, p1 in zip(path[:-1], path[1:]):
                bar(NEON, p0, p1, vw, vcol)


GLYPHS = {
    "I": [((0.5, 0.0), (0.5, 1.0))], "L": [((0.1, 1.0), (0.1, 0.0)), ((0.1, 0.0), (0.8, 0.0))],
    "T": [((0.0, 1.0), (1.0, 1.0)), ((0.5, 1.0), (0.5, 0.0))], "E": [((0.1, 0.0), (0.1, 1.0)), ((0.1, 1.0), (0.8, 1.0)), ((0.1, 0.5), (0.7, 0.5)), ((0.1, 0.0), (0.8, 0.0))],
    "O": [((0.1, 0.0), (0.1, 1.0)), ((0.1, 1.0), (0.9, 1.0)), ((0.9, 1.0), (0.9, 0.0)), ((0.9, 0.0), (0.1, 0.0))],
    "A": [((0.0, 0.0), (0.5, 1.0)), ((0.5, 1.0), (1.0, 0.0)), ((0.2, 0.35), (0.8, 0.35))], "V": [((0.0, 1.0), (0.5, 0.0)), ((0.5, 0.0), (1.0, 1.0))],
    "N": [((0.1, 0.0), (0.1, 1.0)), ((0.1, 1.0), (0.9, 0.0)), ((0.9, 0.0), (0.9, 1.0))], "M": [((0.0, 0.0), (0.0, 1.0)), ((0.0, 1.0), (0.5, 0.4)), ((0.5, 0.4), (1.0, 1.0)), ((1.0, 1.0), (1.0, 0.0))],
    "S": [((0.9, 1.0), (0.1, 1.0)), ((0.1, 1.0), (0.1, 0.5)), ((0.1, 0.5), (0.9, 0.5)), ((0.9, 0.5), (0.9, 0.0)), ((0.9, 0.0), (0.1, 0.0))],
    "C": [((0.9, 1.0), (0.1, 1.0)), ((0.1, 1.0), (0.1, 0.0)), ((0.1, 0.0), (0.9, 0.0))], "R": [((0.1, 0.0), (0.1, 1.0)), ((0.1, 1.0), (0.9, 1.0)), ((0.9, 1.0), (0.9, 0.5)), ((0.9, 0.5), (0.1, 0.5)), ((0.4, 0.5), (0.9, 0.0))],
}


def canonical_v2(ctx, hx, hy, open_bays=()):
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
        arcade_tier_v2(SURF, SMOOTH, cyl, sc, hx, hy, A, BK, z0, z1, tr, k,
                       AL.arcade_piers(A, BK, LM["cols"], [(t0, t1) for (kb, t0, t1) in open_bays if kb == k]), rec=rec)
        if k == 0:                                           # rusticated base courses: proud bands with a dark groove between
            for (za, zb_, off, kk) in ((0.0, 0.42, 0.62, 0.90), (0.50, 0.92, 0.58, 0.96)):
                prism(SURF, circle(hx, hy, A + off, n, ry=A * BK + off), za, zb_, sc(tr, kk), top=False)
            prism(SURF, circle(hx, hy, A + 0.50, n, ry=A * BK + 0.50), 0.42, 0.50, sc(tr, 0.30), top=False)
        else:
            prism(SURF, circle(hx, hy, A + 0.48, n, ry=A * BK + 0.48), z0, z0 + 0.3, sc(tr, 0.94), top=False)
        # architrave band (a little proud of the wall) and a stepped cornice
        prism(SURF, circle(hx, hy, A + 0.40, n, ry=A * BK + 0.40), z1 - 1.5, z1 - 0.75, sc(tr, 1.00), top=False)
        prism(SURF, circle(hx, hy, A + 0.50, n, ry=A * BK + 0.50), z1 - 0.75, z1 - 0.55, sc(tr, 0.86), top=False)
        prism(SURF, circle(hx, hy, A + 0.70, n, ry=A * BK + 0.70), z1 - 0.55, z1 - 0.18, sc(tr, 1.04), top=False)
        prism(SURF, circle(hx, hy, A + 0.95, n, ry=A * BK + 0.95), z1 - 0.18, z1, sc(tr, 1.08), top=False)
        k1 = (A * BK + 0.95) / (A + 0.95)
        annulus(SURF, hx, hy, z1, A - rec, A + 0.95, sc(tr, 1.0), n=n, k0=BK, k1=k1)
        annulus(SURF, hx, hy, z1 - 0.55, A - rec, A + 0.70, sc(tr, 0.5), n=n, k0=BK, k1=(A * BK + 0.70) / (A + 0.70))
        ring_line(NEON, hx, hy, z1 - 0.9, A + 0.45, 0.04, sec, n=n, ry=A * BK + 0.45)
    zt = TIERS * th
    prism(SURF, circle(hx, hy, A + 0.2, n, ry=A * BK + 0.2), zt, zt + attic, sc(tr, 0.97), top=False)
    prism(SURF, circle(hx, hy, A + 0.45, n, ry=A * BK + 0.45), zt + 0.2, zt + 0.5, sc(tr, 1.0), top=False)
    prism(SURF, circle(hx, hy, A + 0.45, n, ry=A * BK + 0.45), zt + attic - 0.55, zt + attic - 0.2, sc(tr, 1.0), top=False)
    prism(SURF, circle(hx, hy, A + 0.80, n, ry=A * BK + 0.80), zt + attic - 0.2, zt + attic, sc(tr, 1.08), top=False)
    ring_line(SURF, hx, hy, zt + attic, A + 0.35, 0.5, sc(tr, 1.05), n=n, ry=A * BK + 0.35)
    ring_line(NEON, hx, hy, zt + attic + 0.3, A + 0.4, 0.05, sec, n=n, ry=A * BK + 0.4)
    # the inscription: abstract monumental capitals in relief (no real words) on the attic band
    rng = random.Random(1942)
    letters = "AEILMNOSTVCR"
    ra, rb_ = A + 0.28, A * BK + 0.28
    per = 2 * math.pi * math.sqrt((ra * ra + rb_ * rb_) / 2)
    nl = int(per / 1.55)
    lh, zl = 1.5, zt + 0.95
    col_l = sc(tr, 1.08)
    t = 0.0
    for q in range(nl):
        ch = rng.choice(letters)
        if rng.random() < 0.11:
            continue                                         # a word space
        tt = 2 * math.pi * q / nl
        ex, ey = ra * math.cos(tt), rb_ * math.sin(tt)
        tang = (-ra * math.sin(tt), rb_ * math.cos(tt))
        tl = math.hypot(*tang)
        tx, ty = tang[0] / tl, tang[1] / tl
        nx_, ny_ = ty, -tx
        wdl = 0.95
        for (a0, a1) in GLYPHS[ch]:
            p0 = (hx + ex + tx * (a0[0] - 0.5) * wdl, hy + ey + ty * (a0[0] - 0.5) * wdl, zl + a0[1] * lh)
            p1 = (hx + ex + tx * (a1[0] - 0.5) * wdl, hy + ey + ty * (a1[0] - 0.5) * wdl, zl + a1[1] * lh)
            bar(SURF, p0, p1, 0.17, col_l)
    # the stepped white terraces with lit risers
    T = AL.terraces(LM["steps"])
    for i, (ro, ri, zm, k, m) in enumerate(T):
        zn = T[i + 1][2] if i + 1 < len(T) else AL.RING_Z[4]
        annulus(SURF, hx, hy, zm, ri, ro, sc(tr, 1.06 if m % 2 == 0 else 0.98), n=n, k0=BK, k1=BK)
        prism(SURF, circle(hx, hy, ri, n, ry=ri * BK), zn, zm, sc(tr, 1.00), top=False)
        ring_line(NEON, hx, hy, zm - 0.12, ri - 0.03, 0.05, (0.28, 0.46, 0.40), n=n, ry=(ri - 0.03) * BK)       # a soft riser light
        if m == LM["steps"] - 1:
            ring_line(NEON, hx, hy, zm + 0.05, ri, 0.04, sec, n=n, ry=ri * BK)
    prism(SURF, circle(hx, hy, AL.RING_R[4], n, ry=AL.RING_R[4] * BK), 0.0, 2.9, sc(tr, 0.80), top=False)          # the paved floor is added by rat_style
    # the Rostrum: two-stage white drum on a porphyry pad, verdigris-lit core
    R = AL.ROSTRUM
    cyl(SURF, hx, hy, R["plinth_z"][0], R["plinth_z"][1], R["plinth_r"], 24, (0.040, 0.010, 0.022))
    zA, zB = R["tholos_z"]
    WH = (0.97, 0.98, 1.0)
    cyl(SURF, hx, hy, zA, zA + 0.18, 4.75, 24, WH)
    NC = 24
    for kk in range(NC):
        tt = 2 * math.pi * (kk + 0.5) / NC
        x, y = hx + R["tholos_r"] * math.cos(tt), hy + R["tholos_r"] * math.sin(tt)
        bar(SURF, (x, y, zA), (x, y, zB), 0.5, WH)
    cyl(SURF, hx, hy, zB, zB + 0.55, 4.95, 24, WH)
    cyl(SURF, hx, hy, zB + 0.55, zB + 0.80, 4.55, 24, sc(WH, 0.9))
    z2 = zB + 0.8                                               # the upper drum: a pilastered cylinder under a stepped cap
    cyl(SURF, hx, hy, z2, z2 + 3.6, 3.5, 24, sc(WH, 0.95))
    for kk in range(NC):
        tt = 2 * math.pi * kk / NC
        x, y = hx + 3.62 * math.cos(tt), hy + 3.62 * math.sin(tt)
        bar(SURF, (x, y, z2 + 0.2), (x, y, z2 + 3.3), 0.34, WH)
    cyl(SURF, hx, hy, z2 + 3.6, z2 + 4.1, 4.0, 24, WH)
    cyl(SURF, hx, hy, z2 + 4.1, z2 + 4.4, 3.2, 24, sc(WH, 0.92))
    ring_line(NEON, hx, hy, z2 + 3.6, 3.9, 0.05, sec, n=48)
    cyl(NEON, hx, hy, z2 + 4.4, R["core_top"], R["core_r"] * 0.8, 14, sc(sec, 0.45), top=True)
    for zz in R["rings_z"]:
        if zz > z2 + 4.4:
            cyl(SURF, hx, hy, zz, zz + 0.3, 2.0, 14, WH)
    ring_line(ctx.LAUREL, hx, hy, R["laurel_z"], R["laurel_r"], 0.07, sc(sec, 1.2), n=64)
    box(NEON, hx - 0.7, hy - 0.7, 22.0, hx + 0.7, hy + 0.7, 23.4, (0.5, 1.0, 0.85))
    # square towers: stepped plinth, four pilasters per face, stringcourses, a heavy cornice (the figure stands on top; see rat_style)
    for kk in range(4):
        tt = math.radians(45 + 90 * kk)
        cx, cy = hx + (A + AL.CAMP_OFF) * math.cos(tt), hy + (A * BK + AL.CAMP_OFF) * math.sin(tt)
        hw = 2.0
        box(SURF, cx - hw * 1.35, cy - hw * 1.35, 0, cx + hw * 1.35, cy + hw * 1.35, 1.2, sc(tr, 0.9))
        box(SURF, cx - hw * 1.2, cy - hw * 1.2, 1.2, cx + hw * 1.2, cy + hw * 1.2, 3.0, sc(tr, 0.95))
        box(SURF, cx - hw, cy - hw, 3.0, cx + hw, cy + hw, 31.0, sc(tr, 0.96))
        for zc in (9.0, 16.0, 23.0):                          # stringcourses
            box(SURF, cx - hw * 1.08, cy - hw * 1.08, zc, cx + hw * 1.08, cy + hw * 1.08, zc + 0.4, sc(tr, 1.04))
        for u in (-1.35, -0.45, 0.45, 1.35):                  # pilasters
            for (ax, ay) in ((1, 0), (0, 1)):
                for sg in (-1, 1):
                    if ax:
                        box(SURF, cx + sg * hw, cy + u - 0.14, 3.0, cx + sg * (hw + 0.16), cy + u + 0.14, 30.4, sc(tr, 1.02))
                    else:
                        box(SURF, cx + u - 0.14, cy + sg * hw, 3.0, cx + u + 0.14, cy + sg * (hw + 0.16), 30.4, sc(tr, 1.02))
        box(SURF, cx - hw * 1.15, cy - hw * 1.15, 30.4, cx + hw * 1.15, cy + hw * 1.15, 31.0, sc(tr, 1.04))
        box(SURF, cx - hw * 1.3, cy - hw * 1.3, 31.0, cx + hw * 1.3, cy + hw * 1.3, 32.2, sc(tr, 1.08))
        box(NEON, cx - hw * 1.3, cy - hw * 1.3, 32.2, cx + hw * 1.3, cy + hw * 1.3, 32.3, sec)
    return dict(label=(hx, hy, 40.0), crown=(hx, hy, 26.0), hue=tuple(sec))


def apply_pre(cfg):
    P = HP.PRESET["hq"]["palette"]
    P["gilt"] = VERD2
    AL.ARC_PIER_H = float(cfg.get("pier_h", 0.78))        # wider grid piers: narrower, taller arches (room bays keep their openings)
    AL.canonical = canonical_v2
