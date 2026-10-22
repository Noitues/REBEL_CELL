"""v5: v4 plus a GRAND portal: the entry (and the outer gate) rise two tiers as a tall round-arched opening with a deep reveal, wide
pilasters, an entablature carrying a lettered tablet and a cornice. The tier cornice / architrave rings are cut (gapped) across the portals,
tier 1's own bays are replaced by solid wall around the opening, the terrace light lines are thinner and dimmer, and no figures stand on
the wall top (the balustrade stays). In-memory patch; same module / rhythm as v4 for everything else."""
import math
import sys

sys.dont_write_bytecode = True
import aurelian_landmark as AL  # noqa: E402
import rat_patch as RP  # noqa: E402
import rat_patch2 as P2  # noqa: E402
import rat_patch4 as P4  # noqa: E402

RAT = RP.RAT
TAU = 2 * math.pi


def _in_gap(t, gaps):
    t = t % TAU
    return any(abs(((t - c + math.pi) % TAU) - math.pi) < w for (c, w) in gaps)


def band(SURF, hx, hy, A, BK, off, z0, z1, col, gaps, n=160):
    """A ring band (outer face only) on the ellipse of radius A + off, cut where the gaps are."""
    for j in range(n):
        t0, t1 = TAU * j / n, TAU * (j + 1) / n
        if _in_gap((t0 + t1) / 2, gaps):
            continue
        p = [(hx + (A + off) * math.cos(t), hy + (A + off) * BK * math.sin(t)) for t in (t0, t1)]
        SURF.face([(p[0][0], p[0][1], z0), (p[1][0], p[1][1], z0), (p[1][0], p[1][1], z1), (p[0][0], p[0][1], z1)], col)


def band_top(SURF, hx, hy, A, BK, r0, r1, z, col, gaps, n=160):
    for j in range(n):
        t0, t1 = TAU * j / n, TAU * (j + 1) / n
        if _in_gap((t0 + t1) / 2, gaps):
            continue
        SURF.face([(hx + r0 * math.cos(t0), hy + r0 * BK * math.sin(t0), z), (hx + r0 * math.cos(t1), hy + r0 * BK * math.sin(t1), z),
                   (hx + r1 * math.cos(t1), hy + r1 * BK * math.sin(t1), z), (hx + r1 * math.cos(t0), hy + r1 * BK * math.sin(t0), z)], col)


def arcade_tier_v5(SURF, SMOOTH, cyl, sc, hx, hy, A_, Bk_, z0, z1, tr, k, piers, ent=0.7, base=0.25, rec=1.7):
    rf, rb = A_ + AL.ARC_RF, A_ - rec
    base = 1.05 if k == 0 else base
    zb, zt = z0 + base, z1 - 1.5
    c_face, c_pier, c_sof, c_jam = sc(tr, 0.96), sc(tr, 0.98), sc(tr, 0.30), sc(tr, 0.50)
    c_fr, c_in, c_key, c_sill = sc(tr, 1.04), sc(tr, 0.80), sc(tr, 1.08), sc(tr, 1.02)
    NEON, bar, vcol, vw = RAT.get("NEON"), RAT.get("bar"), RAT["vcol"], RAT["vw"]
    n = len(piers)
    fw, pr = 0.17, 0.12
    th = AL.TIER_H
    ZTOP = 2 * th - 1.6                                   # the top of a portal's opening (through two tiers)

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
        SURF.face([pt(ta, 0.0, rate, zb, rf), pt(ta, ha, rate, zb, rf), pt(ta, ha, rate, zt, rf), pt(ta, 0.0, rate, zt, rf)], c_pier)
        SURF.face([pt(ta, S - hb, rate, zb, rf), pt(ta, S, rate, zb, rf), pt(ta, S, rate, zt, rf), pt(ta, S - hb, rate, zt, rf)], c_pier)
        # tier 1: the portal's tall opening and its pilasters replace the arches near a portal
        if k == 1:
            hit = None
            for (tc, w2) in RAT.get("portal_zone", ()):
                sp = (((tc - ta + math.pi) % TAU) - math.pi) * rate
                if sp - w2 < S - hb and sp + w2 > ha:
                    hit = sp
                    break
            if hit is not None:
                h0, h1 = hit - RAT["portal_ri"], hit + RAT["portal_ri"]
                for (a0, a1) in ((ha, min(h0, S - hb)), (max(h1, ha), S - hb)):
                    if a1 - a0 > 0.03:
                        SURF.face([pt(ta, a0, rate, zb, rf), pt(ta, a1, rate, zb, rf), pt(ta, a1, rate, zt, rf), pt(ta, a0, rate, zt, rf)], c_face)
                continue
        if wd < 0.9:
            SURF.face([pt(ta, ha, rate, zb, rf), pt(ta, S - hb, rate, zb, rf), pt(ta, S - hb, rate, zt, rf), pt(ta, ha, rate, zt, rf)], c_face)
            continue
        tc_ = tm % TAU
        portal = k == 0 and any(abs(((tc_ - c + math.pi) % TAU) - math.pi) < 0.03 for c in RAT.get("portal_t", ()))
        wide = k == 0 and wd > 1.9 and not portal
        if portal:
            zsp = ZTOP - ri
            ze = z1 + th - 1.0                              # the entablature starts here (top of tier 1 less the cornice)
            # jambs, soffit (the deep reveal), then the spandrel up to the entablature
            SURF.face([pt(ta, ha, rate, zb, rb), pt(ta, ha, rate, zb, rf), pt(ta, ha, rate, zsp, rf), pt(ta, ha, rate, zsp, rb)], c_jam)
            SURF.face([pt(ta, S - hb, rate, zb, rf), pt(ta, S - hb, rate, zb, rb), pt(ta, S - hb, rate, zsp, rb), pt(ta, S - hb, rate, zsp, rf)], c_jam)
            arc = [(sc_ - ri * math.cos(math.pi * j / 12), zsp + ri * math.sin(math.pi * j / 12)) for j in range(13)]
            for j in range(12):
                a, b = arc[j], arc[j + 1]
                SURF.face([pt(ta, a[0], rate, a[1], rf), pt(ta, b[0], rate, b[1], rf), pt(ta, b[0], rate, ze, rf), pt(ta, a[0], rate, ze, rf)], c_face)
                SURF.face([pt(ta, a[0], rate, a[1], rb), pt(ta, b[0], rate, b[1], rb), pt(ta, b[0], rate, b[1], rf), pt(ta, a[0], rate, a[1], rf)], c_sof)
                ao = (sc_ - (ri + fw) * math.cos(math.pi * j / 12), zsp + (ri + fw) * math.sin(math.pi * j / 12))
                bo = (sc_ - (ri + fw) * math.cos(math.pi * (j + 1) / 12), zsp + (ri + fw) * math.sin(math.pi * (j + 1) / 12))
                SURF.face([pt(ta, a[0], rate, a[1], rf + pr), pt(ta, b[0], rate, b[1], rf + pr), pt(ta, bo[0], rate, bo[1], rf + pr), pt(ta, ao[0], rate, ao[1], rf + pr)], c_fr)
                SURF.face([pt(ta, a[0], rate, a[1], rf - 1.0), pt(ta, b[0], rate, b[1], rf - 1.0),
                           pt(ta, sc_ - (ri - 0.2) * math.cos(math.pi * (j + 1) / 12), rate, zsp + (ri - 0.2) * math.sin(math.pi * (j + 1) / 12), rf - 1.0),
                           pt(ta, sc_ - (ri - 0.2) * math.cos(math.pi * j / 12), rate, zsp + (ri - 0.2) * math.sin(math.pi * j / 12), rf - 1.0)], c_in)
            # wide pilasters with base and capital, flat entablature, tablet, cornice
            pw, pp = 0.95, 0.55
            for (s0, s1) in ((ha - pw, ha - 0.02), (S - hb + 0.02, S - hb + pw)):
                P4._pbox(SURF, pt, ta, rate, s0, s1, zb, ze, rf, rf + pp, c_fr)
                P4._pbox(SURF, pt, ta, rate, s0 - 0.12, s1 + 0.12, ze - 0.42, ze, rf, rf + pp + 0.12, c_key)
                P4._pbox(SURF, pt, ta, rate, s0 - 0.10, s1 + 0.10, zb, zb + 0.34, rf, rf + pp + 0.10, c_key)
                for q in range(3):                              # fluting: three thin proud ribs
                    sx = s0 + (s1 - s0) * (q + 1) / 4.0
                    P4._pbox(SURF, pt, ta, rate, sx - 0.05, sx + 0.05, zb + 0.34, ze - 0.42, rf + pp, rf + pp + 0.06, c_key)
            w_all = (ha - pw - 0.25, S - hb + pw + 0.25)
            P4._pbox(SURF, pt, ta, rate, w_all[0], w_all[1], ze, ze + 0.40, rf, rf + 0.78, c_fr)                       # architrave
            P4._pbox(SURF, pt, ta, rate, w_all[0] + 0.05, w_all[1] - 0.05, ze + 0.40, ze + 0.92, rf, rf + 0.62, c_in)    # the tablet (recessed)
            P4._pbox(SURF, pt, ta, rate, w_all[0] - 0.12, w_all[1] + 0.12, ze + 0.92, ze + 1.18, rf, rf + 0.92, c_key)  # cornice
            RAT.setdefault("portals", []).append((ta + sc_ / rate, rate, ze + 0.48, S, ha))
            if NEON is not None:
                fo = rf + pr + 0.03
                path = [pt(ta, ha - fw, rate, zb + 0.35, fo), pt(ta, ha - fw, rate, zsp, fo)]
                for j in range(1, 12):
                    path.append(pt(ta, sc_ - (ri + fw) * math.cos(math.pi * j / 12), rate, zsp + (ri + fw) * math.sin(math.pi * j / 12), fo))
                path += [pt(ta, S - hb + fw, rate, zsp, fo), pt(ta, S - hb + fw, rate, zb + 0.35, fo)]
                for p0, p1 in zip(path[:-1], path[1:]):
                    bar(NEON, p0, p1, vw, vcol)
            continue
        if wide:
            zsp = zt - 0.55
            SURF.face([pt(ta, ha, rate, zb, rb), pt(ta, ha, rate, zb, rf), pt(ta, ha, rate, zsp, rf), pt(ta, ha, rate, zsp, rb)], c_jam)
            SURF.face([pt(ta, S - hb, rate, zb, rf), pt(ta, S - hb, rate, zb, rb), pt(ta, S - hb, rate, zsp, rb), pt(ta, S - hb, rate, zsp, rf)], c_jam)
            SURF.face([pt(ta, ha, rate, zsp, rb), pt(ta, S - hb, rate, zsp, rb), pt(ta, S - hb, rate, zsp, rf), pt(ta, ha, rate, zsp, rf)], c_sof)
            SURF.face([pt(ta, ha, rate, zsp, rf), pt(ta, S - hb, rate, zsp, rf), pt(ta, S - hb, rate, zt, rf), pt(ta, ha, rate, zt, rf)], c_face)
            for (s0, s1) in ((ha - fw, ha), (S - hb, S - hb + fw)):
                P4._pbox(SURF, pt, ta, rate, s0, s1, zb, zsp + fw, rf, rf + pr, c_fr)
            P4._pbox(SURF, pt, ta, rate, ha - fw, S - hb + fw, zsp, zsp + fw, rf, rf + pr, c_fr)
            P4._pbox(SURF, pt, ta, rate, ha - fw - 0.1, S - hb + fw + 0.1, zb, zb + 0.14, rf, rf + 0.38, c_sill)
            if NEON is not None:
                fo = rf + pr + 0.03
                path = [pt(ta, ha - fw, rate, zb + 0.15, fo), pt(ta, ha - fw, rate, zsp + fw, fo), pt(ta, S - hb + fw, rate, zsp + fw, fo), pt(ta, S - hb + fw, rate, zb + 0.15, fo)]
                for p0, p1 in zip(path[:-1], path[1:]):
                    bar(NEON, p0, p1, vw, vcol)
            continue
        # the ordinary module arch (identical to v2 / v4)
        zs = max(zb + 0.8, zt - 0.10 - ri - 0.12)
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
            SURF.face([pt(ta, a[0], rate, a[1], rf + pr), pt(ta, b[0], rate, b[1], rf + pr), pt(ta, b[4], rate, b[5], rf + pr), pt(ta, a[4], rate, a[5], rf + pr)], c_fr)
            SURF.face([pt(ta, a[0], rate, a[1], rf), pt(ta, b[0], rate, b[1], rf), pt(ta, b[0], rate, b[1], rf + pr), pt(ta, a[0], rate, a[1], rf + pr)], c_sof)
            SURF.face([pt(ta, a[0], rate, a[1], rf - 1.1), pt(ta, b[0], rate, b[1], rf - 1.1), pt(ta, b[2], rate, b[3], rf - 1.1), pt(ta, a[2], rate, a[3], rf - 1.1)], c_in)
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
        if NEON is not None and ri > 0.3:
            fo = rf + pr + 0.03
            path = [pt(ta, ha - fw, rate, zb + 0.15, fo), pt(ta, ha - fw, rate, zs, fo)]
            for j in range(1, AL.ARC_N):
                path.append(pt(ta, arc[j][4], rate, arc[j][5], fo))
            path += [pt(ta, S - hb + fw, rate, zs, fo), pt(ta, S - hb + fw, rate, zb + 0.15, fo)]
            for p0, p1 in zip(path[:-1], path[1:]):
                bar(NEON, p0, p1, vw, vcol)


def canonical_v5(ctx, hx, hy, open_bays=()):
    SURF, SMOOTH, NEON = ctx.SURF, ctx.SMOOTH, ctx.NEON
    prism, box, cyl, bar = ctx.prism, ctx.box, ctx.cyl, ctx.bar
    ring_line, annulus, circle, sc = ctx.ring_line, ctx.annulus, ctx.circle, ctx.sc
    D = ctx.district
    tr, sec = D["mat"][0], D["sec"]
    LM = AL._lm(ctx)
    A, BK, TIERS, TIER_H, ATTIC_H = AL.A, AL.BK, AL.TIERS, AL.TIER_H, AL.ATTIC_H
    rec, n, th, attic = LM["recess"], AL.NSEG, TIER_H, ATTIC_H
    RAT.update(NEON=NEON, bar=bar, vcol=sec)
    RAT["portals"] = []
    RAT["portal_t"] = [math.radians(AL.ENTRY_T)] + [math.radians(g["t"]) for g in AL.gates(getattr(__import__("hq_graph"), "CONCEPT", "R")) if g["kind"] == "outer"]
    RAT["portal_ri"] = AL.ENTRY_OPEN / 2.0
    rate0 = AL._arc_rate(A, BK, math.radians(AL.ENTRY_T))
    zone_s = AL.ENTRY_OPEN / 2.0 + 1.25                    # the pilasters stand in this zone either side of the opening
    RAT["portal_zone"] = [(c, zone_s) for c in RAT["portal_t"]]
    gaps = [(c, (zone_s + 0.35) / rate0) for c in RAT["portal_t"]]          # angular half widths for the ring gaps
    piers_fn = P4.uniform_piers
    for k in range(TIERS):
        z0, z1 = k * th, (k + 1) * th
        prism(SURF, circle(hx, hy, A - rec, n, ry=(A - rec) * BK), z0, z1, sc(tr, 0.50), top=False)
        arcade_tier_v5(SURF, SMOOTH, cyl, sc, hx, hy, A, BK, z0, z1, tr, k,
                       piers_fn(A, BK, LM["cols"], [(t0, t1) for (kb, t0, t1) in open_bays if kb == k]), rec=rec)
        g = gaps if k < 2 else []
        if k == 0:
            for (za, zb_, off, kk) in ((0.0, 0.42, 0.62, 0.90), (0.50, 0.92, 0.58, 0.96)):
                prism(SURF, circle(hx, hy, A + off, n, ry=A * BK + off), za, zb_, sc(tr, kk), top=False)
            prism(SURF, circle(hx, hy, A + 0.50, n, ry=A * BK + 0.50), 0.42, 0.50, sc(tr, 0.30), top=False)
        else:
            band(SURF, hx, hy, A, BK, 0.48, z0, z0 + 0.3, sc(tr, 0.94), g if k == 1 else [])
        band(SURF, hx, hy, A, BK, 0.40, z1 - 1.5, z1 - 0.75, sc(tr, 1.00), g)
        band(SURF, hx, hy, A, BK, 0.50, z1 - 0.75, z1 - 0.55, sc(tr, 0.86), g)
        band(SURF, hx, hy, A, BK, 0.70, z1 - 0.55, z1 - 0.18, sc(tr, 1.04), g)
        band(SURF, hx, hy, A, BK, 0.95, z1 - 0.18, z1, sc(tr, 1.08), g)
        band_top(SURF, hx, hy, A, BK, A - rec, A + 0.95, z1, sc(tr, 1.0), g)
        band_top(SURF, hx, hy, A, BK, A - rec, A + 0.70, z1 - 0.55, sc(tr, 0.5), g)
        # the tier light line (thin), cut at the portals
        m_ = 96
        for j in range(m_):
            t0, t1 = TAU * j / m_, TAU * (j + 1) / m_
            if g and _in_gap((t0 + t1) / 2, g):
                continue
            r_ = A + 0.45
            bar(NEON, (hx + r_ * math.cos(t0), hy + r_ * BK * math.sin(t0), z1 - 0.9), (hx + r_ * math.cos(t1), hy + r_ * BK * math.sin(t1), z1 - 0.9), 0.04, sec)
    zt = TIERS * th
    prism(SURF, circle(hx, hy, A + 0.2, n, ry=A * BK + 0.2), zt, zt + attic, sc(tr, 0.97), top=False)
    prism(SURF, circle(hx, hy, A + 0.45, n, ry=A * BK + 0.45), zt + 0.2, zt + 0.5, sc(tr, 1.0), top=False)
    prism(SURF, circle(hx, hy, A + 0.45, n, ry=A * BK + 0.45), zt + attic - 0.55, zt + attic - 0.2, sc(tr, 1.0), top=False)
    prism(SURF, circle(hx, hy, A + 0.80, n, ry=A * BK + 0.80), zt + attic - 0.2, zt + attic, sc(tr, 1.08), top=False)
    ring_line(SURF, hx, hy, zt + attic, A + 0.35, 0.5, sc(tr, 1.05), n=n, ry=A * BK + 0.35)
    ring_line(NEON, hx, hy, zt + attic + 0.3, A + 0.4, 0.04, sec, n=n, ry=A * BK + 0.4)
    # the inscription band on the attic (as v2)
    import random
    rng = random.Random(1942)
    letters = "AEILMNOSTVCR"
    ra, rb_ = A + 0.28, A * BK + 0.28
    per = 2 * math.pi * math.sqrt((ra * ra + rb_ * rb_) / 2)
    nl = int(per / 1.55)
    lh, zl = 1.5, zt + 0.95
    col_l = sc(tr, 1.08)
    for q in range(nl):
        ch = rng.choice(letters)
        if rng.random() < 0.11:
            continue
        tt = 2 * math.pi * q / nl
        ex, ey = ra * math.cos(tt), rb_ * math.sin(tt)
        tang = (-ra * math.sin(tt), rb_ * math.cos(tt))
        tl = math.hypot(*tang)
        tx, ty = tang[0] / tl, tang[1] / tl
        for (a0, a1) in P2.GLYPHS[ch]:
            p0 = (hx + ex + tx * (a0[0] - 0.5) * 0.95, hy + ey + ty * (a0[0] - 0.5) * 0.95, zl + a0[1] * lh)
            p1 = (hx + ex + tx * (a1[0] - 0.5) * 0.95, hy + ey + ty * (a1[0] - 0.5) * 0.95, zl + a1[1] * lh)
            bar(SURF, p0, p1, 0.17, col_l)
    # terraces: white risers, thin dim light lines (v5: width 0.04, the sec line at 45 %)
    T = AL.terraces(LM["steps"])
    for i, (ro, ri, zm, k, m) in enumerate(T):
        zn = T[i + 1][2] if i + 1 < len(T) else AL.RING_Z[4]
        annulus(SURF, hx, hy, zm, ri, ro, sc(tr, 1.06 if m % 2 == 0 else 0.98), n=n, k0=BK, k1=BK)
        prism(SURF, circle(hx, hy, ri, n, ry=ri * BK), zn, zm, sc(tr, 1.00), top=False)
        ring_line(NEON, hx, hy, zm - 0.12, ri - 0.03, 0.04, (0.28, 0.46, 0.40), n=n, ry=(ri - 0.03) * BK)
        if m == LM["steps"] - 1:
            ring_line(NEON, hx, hy, zm + 0.05, ri, 0.04, sc(sec, 0.45), n=n, ry=ri * BK)
    prism(SURF, circle(hx, hy, AL.RING_R[4], n, ry=AL.RING_R[4] * BK), 0.0, 2.9, sc(tr, 0.80), top=False)
    # the Rostrum: two-stage white drum (as v2)
    R = AL.ROSTRUM
    cyl(SURF, hx, hy, R["plinth_z"][0], R["plinth_z"][1], R["plinth_r"], 24, (0.040, 0.010, 0.022))
    zA, zB = R["tholos_z"]
    WH = (0.97, 0.98, 1.0)
    cyl(SURF, hx, hy, zA, zA + 0.18, 4.75, 24, WH)
    for kk in range(24):
        tt = 2 * math.pi * (kk + 0.5) / 24
        bar(SURF, (hx + R["tholos_r"] * math.cos(tt), hy + R["tholos_r"] * math.sin(tt), zA), (hx + R["tholos_r"] * math.cos(tt), hy + R["tholos_r"] * math.sin(tt), zB), 0.5, WH)
    cyl(SURF, hx, hy, zB, zB + 0.55, 4.95, 24, WH)
    cyl(SURF, hx, hy, zB + 0.55, zB + 0.80, 4.55, 24, sc(WH, 0.9))
    z2 = zB + 0.8
    cyl(SURF, hx, hy, z2, z2 + 3.6, 3.5, 24, sc(WH, 0.95))
    for kk in range(24):
        tt = 2 * math.pi * kk / 24
        bar(SURF, (hx + 3.62 * math.cos(tt), hy + 3.62 * math.sin(tt), z2 + 0.2), (hx + 3.62 * math.cos(tt), hy + 3.62 * math.sin(tt), z2 + 3.3), 0.34, WH)
    cyl(SURF, hx, hy, z2 + 3.6, z2 + 4.1, 4.0, 24, WH)
    cyl(SURF, hx, hy, z2 + 4.1, z2 + 4.4, 3.2, 24, sc(WH, 0.92))
    ring_line(NEON, hx, hy, z2 + 3.6, 3.9, 0.04, sec, n=48)
    cyl(NEON, hx, hy, z2 + 4.4, R["core_top"], R["core_r"] * 0.8, 14, sc(sec, 0.45), top=True)
    for zz in R["rings_z"]:
        if zz > z2 + 4.4:
            cyl(SURF, hx, hy, zz, zz + 0.3, 2.0, 14, WH)
    ring_line(ctx.LAUREL, hx, hy, R["laurel_z"], R["laurel_r"], 0.06, sc(sec, 1.2), n=64)
    ctx.box(NEON, hx - 0.7, hy - 0.7, 22.0, hx + 0.7, hy + 0.7, 23.4, (0.5, 1.0, 0.85))
    # square towers with pilasters and stringcourses (as v2)
    for kk in range(4):
        tt = math.radians(45 + 90 * kk)
        cx, cy = hx + (A + AL.CAMP_OFF) * math.cos(tt), hy + (A * BK + AL.CAMP_OFF) * math.sin(tt)
        hw = 2.0
        box(SURF, cx - hw * 1.35, cy - hw * 1.35, 0, cx + hw * 1.35, cy + hw * 1.35, 1.2, sc(tr, 0.9))
        box(SURF, cx - hw * 1.2, cy - hw * 1.2, 1.2, cx + hw * 1.2, cy + hw * 1.2, 3.0, sc(tr, 0.95))
        box(SURF, cx - hw, cy - hw, 3.0, cx + hw, cy + hw, 31.0, sc(tr, 0.96))
        for zc in (9.0, 16.0, 23.0):
            box(SURF, cx - hw * 1.08, cy - hw * 1.08, zc, cx + hw * 1.08, cy + hw * 1.08, zc + 0.4, sc(tr, 1.04))
        for u in (-1.35, -0.45, 0.45, 1.35):
            for sg in (-1, 1):
                box(SURF, cx + sg * hw, cy + u - 0.14, 3.0, cx + sg * (hw + 0.16), cy + u + 0.14, 30.4, sc(tr, 1.02))
                box(SURF, cx + u - 0.14, cy + sg * hw, 3.0, cx + u + 0.14, cy + sg * (hw + 0.16), 30.4, sc(tr, 1.02))
        box(SURF, cx - hw * 1.15, cy - hw * 1.15, 30.4, cx + hw * 1.15, cy + hw * 1.15, 31.0, sc(tr, 1.04))
        box(SURF, cx - hw * 1.3, cy - hw * 1.3, 31.0, cx + hw * 1.3, cy + hw * 1.3, 32.2, sc(tr, 1.08))
        box(NEON, cx - hw * 1.3, cy - hw * 1.3, 32.2, cx + hw * 1.3, cy + hw * 1.3, 32.3, sec)
    # portal tablets
    for (tcen, rate, zc, S, ha) in RAT.get("portals", []):
        P4._letters_on_wall(bar, SURF, hx, hy, A, BK, tcen, rate, zc, "CRVNT", 0.36, 0.40, 0.58, sc(tr, 1.14), A + 0.45 + 0.64)
    # balustrade (v1's fence), no figures on it in v5
    P = P4._table()["s"][-1]
    npost = int(P / 1.15)
    col = sc(tr, 1.05)
    zt2 = zt + attic
    for q in range(npost):
        tt = P4.t_of_s(q * P / npost)
        x, y = hx + (A + 0.35) * math.cos(tt), hy + (A + 0.35) * BK * math.sin(tt)
        ctx.cyl(SURF, x, y, zt2 + 0.25, zt2 + 1.35, 0.17, 8, col)
        ctx.cyl(SURF, x, y, zt2 + 1.35, zt2 + 1.55, 0.26, 8, sc(tr, 1.1))
        ctx.cyl(SURF, x, y, zt2 + 0.25, zt2 + 0.45, 0.27, 8, sc(tr, 1.1))
    ctx.ring_line(SURF, hx, hy, zt2 + 1.6, A + 0.35, 0.34, sc(tr, 1.1), n=AL.NSEG, ry=(A + 0.35) * BK)
    ctx.ring_line(SURF, hx, hy, zt2 + 0.32, A + 0.35, 0.28, sc(tr, 1.0), n=AL.NSEG, ry=(A + 0.35) * BK)
    return dict(label=(hx, hy, 40.0), crown=(hx, hy, 26.0), hue=tuple(sec))


def apply_pre(cfg):
    P4.apply_pre(cfg)
    AL.canonical = canonical_v5
