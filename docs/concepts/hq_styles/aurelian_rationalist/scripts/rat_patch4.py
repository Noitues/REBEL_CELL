"""v4: v2's landmark plus (1) one arch module: piers re-spaced at equal arc length so every grid arch is the same width on every tier,
(2) the ground tier's wide room bays become rectangular-lintel bays with the same frame, slivers become solid pier wall, (3) the entry and
the outer gate become designed double-height portals (pilasters, entablature, inscription tablet), (4) a balustrade of posts and rails
round the wall top (v1's fence), (5) the base's lit arch frames (the oversized leftover arches) are suppressed. In-memory patch."""
import math
import sys

sys.dont_write_bytecode = True
import aurelian_landmark as AL  # noqa: E402
import hq_preset as HP  # noqa: E402
import rat_patch as RP  # noqa: E402
import rat_patch2 as P2  # noqa: E402

RAT = RP.RAT
_TAB = {}


def _table():
    if not _TAB:
        n = 4000
        s = [0.0]
        for i in range(1, n + 1):
            t0, t1 = 2 * math.pi * (i - 1) / n, 2 * math.pi * i / n
            s.append(s[-1] + AL._arc_rate(AL.A, AL.BK, (t0 + t1) / 2) * (t1 - t0))
        _TAB["s"], _TAB["n"] = s, n
    return _TAB


def s_of_t(t):
    T = _table()
    t = t % (2 * math.pi)
    f = t / (2 * math.pi) * T["n"]
    i = min(int(f), T["n"] - 1)
    return T["s"][i] + (T["s"][i + 1] - T["s"][i]) * (f - i)


def t_of_s(s):
    T = _table()
    P = T["s"][-1]
    s = s % P
    lo, hi = 0, T["n"]
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if T["s"][mid] <= s:
            lo = mid
        else:
            hi = mid
    f = lo + (s - T["s"][lo]) / max(1e-9, T["s"][lo + 1] - T["s"][lo])
    return f / T["n"] * 2 * math.pi


def uniform_piers(A_, Bk_, ncols, open_arcs=()):
    """Piers [(t, half)] with equal arc-length bays; the room / portal openings keep their clear width, the stretches between
    them are divided into equal module bays (a stretch too short for one bay becomes a solid thick pier)."""
    h = AL.ARC_PIER_H
    P = _table()["s"][-1]
    sp = P / ncols
    ops = []
    for (t0, t1) in open_arcs:
        a, b = s_of_t(t0), s_of_t(t1)
        if b < a:
            b += P
        ops.append((a, b))
    ops.sort()
    out = []
    if not ops:
        return [(t_of_s(i * sp), h) for i in range(ncols)]
    m = len(ops)
    # pier groups at each opening edge, merging touching openings
    edges = []                                  # (s, half)
    for i, (a, b) in enumerate(ops):
        edges.append([a - h, h, "L"])
        edges.append([b + h, h, "R"])
    # stretch i runs from the right pier of opening i to the left pier of opening i+1
    res = []
    for i in range(m):
        aL, aR = edges[2 * i][0], edges[2 * i + 1][0]
        nL = edges[(2 * i + 2) % (2 * m)][0]
        if nL < aR:
            nL += P
        D = nL - aR
        res.append((aL, h))
        if D < 2 * h + 0.9:                     # no room for a module bay: one thick pier replaces both edge piers
            mid = (aR + nL) / 2
            res.append((mid, D / 2 + h))
            edges[(2 * i + 2) % (2 * m)][1] = -1.0       # mark: the next left pier is merged
            continue
        res.append((aR, h))
        nb = max(1, round(D / sp))
        for j in range(1, nb):
            res.append((aR + D * j / nb, h))
    # drop the merged left piers
    keep = []
    merged = {round(edges[(2 * i + 2) % (2 * m)][0] % P, 3) for i in range(m) if edges[(2 * i + 2) % (2 * m)][1] < 0}
    for (s, hh) in res:
        if round(s % P, 3) in merged and hh == h:
            continue
        keep.append((s, hh))
    keep.sort()
    return [(t_of_s(s), hh) for (s, hh) in keep]


def _pbox(SURF, pt, ta, rate, s0, s1, z0, z1, r0, r1, col):
    """A box on the ellipse wall: bay coordinate s (along), height z, radius r (outward)."""
    q = [(s0, r0), (s1, r0), (s1, r1), (s0, r1)]
    SURF.face([pt(ta, s, rate, z1, r) for (s, r) in q], col)
    for i in range(4):
        (sa, ra_), (sb, rb_) = q[i], q[(i + 1) % 4]
        SURF.face([pt(ta, sa, rate, z0, ra_), pt(ta, sb, rate, z0, rb_), pt(ta, sb, rate, z1, rb_), pt(ta, sa, rate, z1, ra_)], col)


def arcade_tier_v4(SURF, SMOOTH, cyl, sc, hx, hy, A_, Bk_, z0, z1, tr, k, piers, ent=0.7, base=0.25, rec=1.7, skip=()):
    TAU = 2 * math.pi
    rf, rb = A_ + AL.ARC_RF, A_ - rec
    base = 1.05 if k == 0 else base
    zb, zt = z0 + base, z1 - 1.5
    c_face, c_pier, c_sof, c_jam = sc(tr, 0.96), sc(tr, 0.98), sc(tr, 0.30), sc(tr, 0.50)
    c_fr, c_in, c_key, c_sill = sc(tr, 1.04), sc(tr, 0.80), sc(tr, 1.08), sc(tr, 1.02)
    NEON, bar, vcol, vw = RAT.get("NEON"), RAT.get("bar"), RAT["vcol"], RAT["vw"]
    n = len(piers)
    fw, pr = 0.17, 0.12
    th = AL.TIER_H

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
        # the pier faces (full height) on both sides of the bay
        SURF.face([pt(ta, 0.0, rate, zb, rf), pt(ta, ha, rate, zb, rf), pt(ta, ha, rate, zt, rf), pt(ta, 0.0, rate, zt, rf)], c_pier)
        SURF.face([pt(ta, S - hb, rate, zb, rf), pt(ta, S, rate, zb, rf), pt(ta, S, rate, zt, rf), pt(ta, S - hb, rate, zt, rf)], c_pier)
        solid = wd < 0.9 or any(a0 <= tm % TAU <= a1 for (a0, a1) in skip)
        if solid:
            SURF.face([pt(ta, ha, rate, zb, rf), pt(ta, S - hb, rate, zb, rf), pt(ta, S - hb, rate, zt, rf), pt(ta, ha, rate, zt, rf)], c_face)
            continue
        tc_ = tm % TAU
        portal = k == 0 and any(abs(((tc_ - c + math.pi) % TAU) - math.pi) < 0.03 for c in RAT.get("portal_t", ()))
        wide = k == 0 and wd > 1.9 and not portal
        if portal or wide:
            zsp = zt - (0.30 if portal else 0.55)
            SURF.face([pt(ta, ha, rate, zb, rb), pt(ta, ha, rate, zb, rf), pt(ta, ha, rate, zsp, rf), pt(ta, ha, rate, zsp, rb)], c_jam)
            SURF.face([pt(ta, S - hb, rate, zb, rf), pt(ta, S - hb, rate, zb, rb), pt(ta, S - hb, rate, zsp, rb), pt(ta, S - hb, rate, zsp, rf)], c_jam)
            if portal:
                SURF.face([pt(ta, ha, rate, zsp, rb), pt(ta, S - hb, rate, zsp, rb), pt(ta, S - hb, rate, zsp, rf), pt(ta, ha, rate, zsp, rf)], c_sof)
                SURF.face([pt(ta, ha, rate, zsp, rf), pt(ta, S - hb, rate, zsp, rf), pt(ta, S - hb, rate, zt, rf), pt(ta, ha, rate, zt, rf)], c_face)
                # pilasters either side (up past the architrave), capitals, a heavy lintel frame and lit frame line
                for (s0, s1) in ((ha - 0.72, ha + 0.04), (S - hb - 0.04, S - hb + 0.72)):
                    _pbox(SURF, pt, ta, rate, s0, s1, zb, z1 - 0.62, rf, rf + 0.42, c_fr)
                    _pbox(SURF, pt, ta, rate, s0 - 0.12, s1 + 0.12, z1 - 0.62, z1 - 0.40, rf, rf + 0.52, c_key)
                    _pbox(SURF, pt, ta, rate, s0 - 0.08, s1 + 0.08, zb, zb + 0.22, rf, rf + 0.50, c_key)
                _pbox(SURF, pt, ta, rate, ha - 0.04, S - hb + 0.04, zsp, zsp + 0.26, rf, rf + 0.36, c_fr)
                RAT.setdefault("portals", []).append((ta + (ha + ri) / rate, rate, z1 - 1.30, S, ha))
                if NEON is not None:
                    fo = rf + 0.4
                    path = [pt(ta, ha, rate, zb + 0.30, fo), pt(ta, ha, rate, zsp, fo), pt(ta, S - hb, rate, zsp, fo), pt(ta, S - hb, rate, zb + 0.30, fo)]
                    for p0, p1 in zip(path[:-1], path[1:]):
                        bar(NEON, p0, p1, vw, vcol)
            else:
                # a rectangular room bay: flat lintel, proud frame, sill
                SURF.face([pt(ta, ha, rate, zsp, rb), pt(ta, S - hb, rate, zsp, rb), pt(ta, S - hb, rate, zsp, rf), pt(ta, ha, rate, zsp, rf)], c_sof)
                SURF.face([pt(ta, ha, rate, zsp, rf), pt(ta, S - hb, rate, zsp, rf), pt(ta, S - hb, rate, zt, rf), pt(ta, ha, rate, zt, rf)], c_face)
                for (s0, s1) in ((ha - fw, ha), (S - hb, S - hb + fw)):
                    _pbox(SURF, pt, ta, rate, s0, s1, zb, zsp + fw, rf, rf + pr, c_fr)
                _pbox(SURF, pt, ta, rate, ha - fw, S - hb + fw, zsp, zsp + fw, rf, rf + pr, c_fr)
                _pbox(SURF, pt, ta, rate, ha - fw - 0.1, S - hb + fw + 0.1, zb, zb + 0.14, rf, rf + 0.38, c_sill)
                if NEON is not None:
                    fo = rf + pr + 0.03
                    path = [pt(ta, ha - fw, rate, zb + 0.15, fo), pt(ta, ha - fw, rate, zsp + fw, fo), pt(ta, S - hb + fw, rate, zsp + fw, fo),
                            pt(ta, S - hb + fw, rate, zb + 0.15, fo)]
                    for p0, p1 in zip(path[:-1], path[1:]):
                        bar(NEON, p0, p1, vw, vcol)
            continue
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
            SURF.face([pt(ta, a[0], rate, a[1], rf + pr), pt(ta, b[0], rate, b[1], rf + pr), pt(ta, b[4], rate, b[5], rf + pr),
                       pt(ta, a[4], rate, a[5], rf + pr)], c_fr)
            SURF.face([pt(ta, a[0], rate, a[1], rf), pt(ta, b[0], rate, b[1], rf), pt(ta, b[0], rate, b[1], rf + pr), pt(ta, a[0], rate, a[1], rf + pr)], c_sof)
            SURF.face([pt(ta, a[0], rate, a[1], rf - 1.1), pt(ta, b[0], rate, b[1], rf - 1.1), pt(ta, b[2], rate, b[3], rf - 1.1),
                       pt(ta, a[2], rate, a[3], rf - 1.1)], c_in)
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


def _letters_on_wall(bar, SURF, hx, hy, A_, Bk_, tc, rate, z, text, lh, wdl, sp, col, rad):
    """A row of abstract capitals centred on parameter tc, on the ellipse of radius rad."""
    n = len(text)
    for q, ch in enumerate(text):
        off = (q - (n - 1) / 2.0) * sp / rate
        tt = tc + off
        ex, ey = rad * math.cos(tt), rad * Bk_ * math.sin(tt)
        tang = (-rad * math.sin(tt), rad * Bk_ * math.cos(tt))
        tl = math.hypot(*tang)
        tx, ty = tang[0] / tl, tang[1] / tl
        for (a0, a1) in P2.GLYPHS[ch]:
            p0 = (hx + ex + tx * (a0[0] - 0.5) * wdl, hy + ey + ty * (a0[0] - 0.5) * wdl, z + a0[1] * lh)
            p1 = (hx + ex + tx * (a1[0] - 0.5) * wdl, hy + ey + ty * (a1[0] - 0.5) * wdl, z + a1[1] * lh)
            bar(SURF, p0, p1, 0.12, col)


def canonical_v4(ctx, hx, hy, open_bays=()):
    base = P2.canonical_v2
    # re-route the v2 tier builder and the pier builder to the v4 ones, then run v2's body (cornices, drum, towers, ...)
    saved = (P2.arcade_tier_v2, AL.arcade_piers)
    RAT["portals"] = []
    RAT["portal_t"] = [math.radians(AL.ENTRY_T)] + [math.radians(g["t"]) for g in AL.gates(getattr(__import__("hq_graph"), "CONCEPT", "R")) if g["kind"] == "outer"]

    def piers_v4(A_, Bk_, ncols, open_arcs=()):
        return uniform_piers(A_, Bk_, ncols, open_arcs)

    def tier_v4(SURF, SMOOTH, cyl, sc, hx_, hy_, A_, Bk_, z0, z1, tr, k, piers, **kw):
        arcade_tier_v4(SURF, SMOOTH, cyl, sc, hx_, hy_, A_, Bk_, z0, z1, tr, k, piers, **kw)
    P2.arcade_tier_v2 = tier_v4
    AL.arcade_piers = piers_v4
    try:
        info = base(ctx, hx, hy, open_bays)
    finally:
        P2.arcade_tier_v2, AL.arcade_piers = saved
    SURF, NEON, bar, sc = ctx.SURF, ctx.NEON, ctx.bar, ctx.sc
    D = ctx.district
    tr, sec = D["mat"][0], D["sec"]
    A, BK, TIERS, TIER_H, ATTIC_H = AL.A, AL.BK, AL.TIERS, AL.TIER_H, AL.ATTIC_H
    # portal inscription tablets
    for (tcen, rate, zc, S, ha) in RAT.get("portals", []):
        _letters_on_wall(bar, SURF, hx, hy, A, BK, tcen, rate, zc, "CONCORDIA"[:5], 0.30, 0.34, 0.50, sc(tr, 1.12), A + 0.5)
    # balustrade: posts and rails round the wall top (v1's fence)
    zt = TIERS * TIER_H + ATTIC_H
    skip_deg = RAT.get("statue_deg", (212, 250, 290, 328, 32, 70, 110, 148))
    P = _table()["s"][-1]
    npost = int(P / 1.15)
    col = sc(tr, 1.05)
    for q in range(npost):
        tt = t_of_s(q * P / npost)
        if any(abs(((math.degrees(tt) - d + 180) % 360) - 180) < 3.4 for d in skip_deg):
            continue
        x, y = hx + (A + 0.35) * math.cos(tt), hy + (A + 0.35) * BK * math.sin(tt)
        ctx.cyl(SURF, x, y, zt + 0.25, zt + 1.35, 0.17, 8, col)
        ctx.cyl(SURF, x, y, zt + 1.35, zt + 1.55, 0.26, 8, sc(tr, 1.1))
        ctx.cyl(SURF, x, y, zt + 0.25, zt + 0.45, 0.27, 8, sc(tr, 1.1))
    ctx.ring_line(SURF, hx, hy, zt + 1.6, A + 0.35, 0.34, sc(tr, 1.1), n=AL.NSEG, ry=(A + 0.35) * BK)
    ctx.ring_line(SURF, hx, hy, zt + 0.32, A + 0.35, 0.28, sc(tr, 1.0), n=AL.NSEG, ry=(A + 0.35) * BK)
    return info


def apply_pre(cfg):
    P2.apply_pre(cfg)
    AL.ENTRY_OPEN = float(cfg.get("portal_w", 2.6))
    AL.canonical = canonical_v4
    if cfg.get("kill_frames", True):
        _p_bar = AL.p_bar

        def p_bar_filtered(acc, p0, p1, w, col, **kw):
            if sys._getframe(1).f_code.co_name == "arch_frame":       # the base's oversized lit gate frames: replaced by the portals
                return None
            return _p_bar(acc, p0, p1, w, col, **kw)
        AL.p_bar = p_bar_filtered
