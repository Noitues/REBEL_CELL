"""hi_detail: city detail for the raid v3 plate (set 6), added to the hi capture inside hi_grade (linear light, before haze + tone,
so it goes under the raid's glass grade like the rest of the city).

Near-street band of netrun_cel/zoom_rules/ZOOM_RULES.md (screen ppb ~17), pruned for the raid zoom:
  - facade windows on the 3 m x 3.6 m module (1.5 x 1.8 BU) above a 2.4 BU ground floor: dark slots, ~25 % lit in short vertical
    runs (warm amber / cream / a few teal), floor lines and the ground-floor ledge (2.1.2, 2.1.7);
  - storefront bays (2 BU) on street-facing walls: lit shop windows with shelves, shutters on the rest, a fascia strip, and a
    warm spill pool on the pavement (2.1.4);
  - blade signs on street-facing walls, floors 2-4, one per ~10 BU at most, neon frame + glyph blocks, spill on the facade and
    the pavement (2.1.5 T3, glyph bars since letters are under 7 px here);
  - street lamps on the pavement 1.4-2.0 BU off the building line, ~1 per 7 BU block, 3.3 BU poles, sodium heads, ground pools
    (2.3, 3).
Everything is placed in WORLD space from the capture's own per-pixel world positions (recon), so it sits on real facades and
streets; facade parts only exist on visible facade pixels, lamps are depth-tested against the capture's depth.  Every choice is a
hash of world-lattice ids (salts 9810-9870 as in ZOOM_RULES), never an RNG and never the camera.
"""
import sys

sys.dont_write_bytecode = True
import numpy as np
from scipy import ndimage as ndi

M32 = np.uint64(0xFFFFFFFF)

WIN_U, WIN_V, GF = 1.5, 1.8, 2.4          # window module (BU) and the ground-floor height
BAY = 2.0                                 # storefront bay width (BU)
RES = 0.25                                # world ground light map resolution (BU)
LAMP_H = 3.3                              # pole height (BU)
LAMP_BLOCK = 7.0                          # one lamp candidate per block of this size (BU)
LAMP_KEEP = 0.72                          # share of blocks with a working lamp
LAMP_GAP = 5.0                            # minimum distance between lamps (BU)
SIGN_GAP = 10.0                           # minimum distance between blade signs (BU)
SIGN_MAX = 12

AMBER = (1.0, 0.62, 0.30); CREAM = (1.0, 0.88, 0.70); TEAL = (0.42, 0.88, 1.0)
PINK = (1.0, 0.36, 0.70); GREEN = (0.50, 1.0, 0.62)
WIN_PAL = (np.array([AMBER, CREAM, TEAL], np.float32), np.array([0.68, 0.86, 1.0]))
SHOP_PAL = (np.array([AMBER, CREAM, PINK, TEAL, GREEN], np.float32), np.array([0.40, 0.60, 0.75, 0.90, 1.0]))
SIGN_COLS = np.array([(1.0, 0.25, 0.62), (0.30, 0.88, 1.0), (1.0, 0.82, 0.22), (1.0, 0.28, 0.20), (0.35, 1.0, 0.55)], np.float32)
SOD = np.array((1.0, 0.58, 0.26), np.float32); LED = np.array((0.80, 0.90, 1.0), np.float32)


def hsh(salt, *vals):
    """a deterministic hash in [0, 1) of integer lattice ids (vectorised, wraps negatives)"""
    shape = np.broadcast(*[np.asarray(v) for v in vals]).shape
    x = np.full(shape, (salt * 2654435761) & 0xFFFFFFFF, np.uint64)
    for v in vals:
        v = np.broadcast_to(np.asarray(v).astype(np.int64), shape).astype(np.uint64) & M32
        x = ((x ^ v) * np.uint64(0x85EBCA6B)) & M32
        x ^= x >> np.uint64(13)
        x = (x * np.uint64(0xC2B2AE35)) & M32
        x ^= x >> np.uint64(16)
    return x.astype(np.float64) / 4294967296.0


def pick(pal, h):
    cols, cum = pal
    return cols[np.minimum(np.searchsorted(cum, h, side='right'), len(cols) - 1)]


class Frame:
    """world <-> hi px for the orthographic capture camera"""

    def __init__(self, O, size, nw, nh, right, up, fwd):
        self.O, self.ppb, self.nw, self.nh = np.asarray(O, float), nw / size, nw, nh
        self.R, self.U, self.F = right, up, fwd

    def px(self, Q):
        d = np.asarray(Q, float) - self.O
        return d @ self.R * self.ppb + self.nw / 2, self.nh / 2 - d @ self.U * self.ppb, d @ self.F


def _facades(P, geo, ppb):
    """the two visible facade orientations: masks, wall keys, (u, v) on the wall, outward sign, per-wall top and u extents"""
    n, idm, hag = geo['n'], geo['idm'], geo['hag']
    bld = idm == 2
    er = max(1, int(round(0.3 * ppb)))
    out = []
    for comp, uax in ((0, 2), (2, 0)):
        m = bld & (np.abs(n[..., comp]) > 0.9)
        m = ndi.binary_opening(m, iterations=2)
        lab, nl = ndi.label(m)
        idx = np.arange(1, nl + 1)
        v = hag
        u = P[..., uax]
        top = np.zeros(nl + 1, np.float32); top[1:] = ndi.maximum(v, lab, idx)
        u0 = np.zeros(nl + 1, np.float32); u0[1:] = ndi.minimum(u, lab, idx)
        u1 = np.zeros(nl + 1, np.float32); u1[1:] = ndi.maximum(u, lab, idx)
        pl = np.zeros(nl + 1, np.float32); pl[1:] = ndi.mean(P[..., comp], lab, idx)
        me = ndi.binary_erosion(m, iterations=er)
        out.append(dict(comp=comp, uax=uax, m=me, lab=lab, top=top, u0=u0, u1=u1, plane=pl,
                        key=np.round(pl * 2).astype(np.int64), s=np.sign(n[..., comp]).astype(np.int64)))
    return out


class GroundMap:
    """a world (X, Z) raster of the visible ground: open-ground cells, building-base cells, ground height; light is splatted here
    and read back at every visible ground pixel (so pools land only on ground the camera sees)"""

    def __init__(self, P, ground, base):
        X, Z = P[..., 0], P[..., 2]
        pts = ground | base
        self.x0, self.z0 = float(X[pts].min()) - 6, float(Z[pts].min()) - 6
        self.nx = int((float(X[pts].max()) + 6 - self.x0) / RES) + 1
        self.nz = int((float(Z[pts].max()) + 6 - self.z0) / RES) + 1
        gi = self.idx(X[ground], Z[ground])
        cnt = np.bincount(gi, minlength=self.nx * self.nz)
        ys = np.bincount(gi, P[..., 1][ground], minlength=self.nx * self.nz)
        self.open = (cnt > 0).reshape(self.nz, self.nx)
        self.gy = (ys / np.maximum(cnt, 1)).reshape(self.nz, self.nx)
        bi = self.idx(X[base], Z[base])
        self.base = (np.bincount(bi, minlength=self.nx * self.nz) > 0).reshape(self.nz, self.nx)
        self.light = np.zeros((3, 2, self.nz, self.nx), np.float32)       # rgb x (tight, wide)

    def idx(self, X, Z):
        ix = np.clip(((X - self.x0) / RES).astype(np.int64), 0, self.nx - 1)
        iz = np.clip(((Z - self.z0) / RES).astype(np.int64), 0, self.nz - 1)
        return iz * self.nx + ix

    def cell(self, X, Z):
        return (np.clip(((np.asarray(Z) - self.z0) / RES).astype(np.int64), 0, self.nz - 1),
                np.clip(((np.asarray(X) - self.x0) / RES).astype(np.int64), 0, self.nx - 1))

    def is_open(self, X, Z):
        iz, ix = self.cell(X, Z)
        return self.open[iz, ix]

    def splat(self, X, Z, col, w_tight, w_wide):
        iz, ix = self.cell(X, Z)
        for c in range(3):
            np.add.at(self.light[c, 0], (iz, ix), col[:, c] * w_tight)
            np.add.at(self.light[c, 1], (iz, ix), col[:, c] * w_wide)

    def field(self, s_tight, s_wide):
        L = np.zeros((self.nz, self.nx, 3), np.float32)
        for c in range(3):
            # unit-peak gaussians: the splat weight is the pool's centre intensity
            L[..., c] = (ndi.gaussian_filter(self.light[c, 0], s_tight / RES) * (2 * np.pi * (s_tight / RES) ** 2)
                         + ndi.gaussian_filter(self.light[c, 1], s_wide / RES) * (2 * np.pi * (s_wide / RES) ** 2))
        return L

    def sample(self, L, X, Z):
        iz, ix = self.cell(X, Z)
        return L[iz, ix]


def _greedy(xz, order, gap, cap=None):
    keep = []
    for i in order:
        if all((xz[i, 0] - xz[j, 0]) ** 2 + (xz[i, 1] - xz[j, 1]) ** 2 >= gap * gap for j in keep):
            keep.append(i)
            if cap and len(keep) >= cap:
                break
    return np.array(keep, np.int64)


def detail(img, P, geo, dep, st, gv, fr, log=print):
    """img: the graded city (linear, H x W x 3) -> (img with detail, emission for the wet reflections, stats)"""
    idm, hag = geo['idm'], geo['hag']
    H, W = idm.shape
    img = img.copy()
    emis = np.zeros_like(img)
    fac = _facades(P, geo, fr.ppb)
    ground = st & gv
    base = (idm == 2) & (hag < 1.0)
    gm = GroundMap(P, ground, base)
    stats = dict(windows_lit=0, bays=0, bays_lit=0, signs=0, lamps=0)
    bays_all = []                                     # (comp, key, cb, s, plane, top) of street-facing bays, for signs
    spill_xz, spill_col = [], []

    for f in fac:
        comp, uax, m, lab = f['comp'], f['uax'], f['m'], f['lab']
        ys, xs = np.nonzero(m)
        u = P[ys, xs, uax]; v = hag[ys, xs]; L = lab[ys, xs]
        key = f['key'][L]; s = f['s'][ys, xs]; top = f['top'][L]
        plane = P[ys, xs, comp]
        # ---------------------------------------------------------------- upper floors: windows, floor lines
        up = (v > GF) & (top > GF + 1.2)
        cu = np.floor(u / WIN_U).astype(np.int64); fu = u / WIN_U - cu
        cvf = (v - GF) / WIN_V; cv = np.floor(cvf).astype(np.int64); fv = cvf - cv
        wtop = GF + cv * WIN_V + 0.74 * WIN_V
        win = up & (np.abs(fu - 0.5) < 0.29) & (fv > 0.24) & (fv < 0.74) & (wtop < top - 0.35)
        bias = hsh(9810, comp, key) * 0.2 - 0.1
        run = hsh(9811, comp, key, cu) < 0.30
        share = np.where(run, 0.66, 0.20) + bias
        lit = win & (hsh(9812, comp, key, cu, cv) < share)
        floor_line = up & (np.abs(fv - 0.0) < 0.035) | ((v > GF - 0.16) & (v < GF) & (top > GF + 1.2))
        k = np.ones(len(ys), np.float32)
        k[floor_line] = 0.72
        k[win & ~lit] = 0.45
        img[ys, xs] *= k[:, None]
        # unlit glass: a dark slot with a faint cool sky reflection, lighter towards the top of the pane
        dk = win & ~lit
        img[ys[dk], xs[dk]] += (np.array([0.006, 0.010, 0.024], np.float32)[None] * (1.4 - (fv[dk] - 0.24) / 0.5)[:, None]).astype(np.float32)
        wcol = pick(WIN_PAL, hsh(9813, comp, key, cu, cv)[lit]) * (0.26 + 0.22 * hsh(9814, comp, key, cu, cv)[lit])[:, None]
        # a lit window is a little brighter at the top (the ceiling light) and has a dark sill
        wcol = wcol * (0.8 + 0.35 * (fv[lit] - 0.24) / 0.5)[:, None].astype(np.float32)
        img[ys[lit], xs[lit]] = img[ys[lit], xs[lit]] * 0.2 + wcol
        emis[ys[lit], xs[lit]] += wcol
        stats['windows_lit'] += int(len(np.unique(np.stack([key[lit], cu[lit], cv[lit]], 1), axis=0))) if lit.any() else 0
        # ---------------------------------------------------------------- ground floor: storefront bays on street-facing walls
        gf = (v > 0.08) & (v < GF - 0.18) & (top > 2.6)
        probe = np.zeros(len(ys), bool)
        oX = P[ys, xs, 0].copy(); oZ = P[ys, xs, 2].copy()
        if comp == 0:
            oX += s * 1.6
        else:
            oZ += s * 1.6
        probe[gf] = gm.is_open(oX[gf], oZ[gf])
        cb = np.floor(u / BAY).astype(np.int64); fb = u / BAY - cb
        shop = gf & probe
        hb = hsh(9820, comp, key, cb, s)
        blit = shop & (hb < 0.62)
        pil = shop & (np.abs(fb - 0.5) > 0.44)
        fascia = shop & (v > 1.62) & ~pil
        glass = blit & (v < 1.52) & ~pil
        shut = shop & ~blit & (v < 1.52) & ~pil
        scol = pick(SHOP_PAL, hsh(9821, comp, key, cb, s))
        inten = (0.42 + 0.25 * hsh(9822, comp, key, cb, s)).astype(np.float32)
        gc = scol[glass] * inten[glass][:, None]
        # shelves: two dark bars, goods blocks between them
        shelf = (np.abs(v[glass] - 0.55) < 0.05) | (np.abs(v[glass] - 1.0) < 0.05)
        goods = ((v[glass] > 0.60) & (v[glass] < 0.85) | (v[glass] > 1.05) & (v[glass] < 1.28)) & \
                (hsh(9823, comp, key[glass], np.floor(u[glass] / 0.22).astype(np.int64), (v[glass] > 1.0).astype(np.int64)) < 0.55)
        gc[shelf] *= 0.25
        gc[goods] *= 0.55
        img[ys[glass], xs[glass]] = img[ys[glass], xs[glass]] * 0.15 + gc
        emis[ys[glass], xs[glass]] += gc
        # shutters: ribbed, dark, with a faint warm seam light at the bottom
        rib = (np.floor(v[shut] / 0.11) % 2 == 0)
        img[ys[shut], xs[shut]] *= np.where(rib, 0.55, 0.78)[:, None].astype(np.float32)
        seam = shut & (v < 0.16)
        img[ys[seam], xs[seam]] += np.array(AMBER, np.float32) * 0.10
        # pilasters and the fascia board
        img[ys[pil], xs[pil]] *= 0.5
        img[ys[fascia], xs[fascia]] *= 0.42
        txt = fascia & blit & (hsh(9824, comp, key, cb, s) < 0.55) & (np.abs(fb - 0.5) < 0.34) & (np.abs(v - 1.86) < 0.11) & \
            (hsh(9825, comp, key, np.floor(u / 0.16).astype(np.int64)) < 0.7)
        tc = scol[txt] * 1.0
        img[ys[txt], xs[txt]] = img[ys[txt], xs[txt]] * 0.2 + tc
        emis[ys[txt], xs[txt]] += tc
        # the bays: lit ones spill onto the pavement in front; street-facing ones are sign candidates
        if shop.any():
            kk = np.stack([key[shop], cb[shop], s[shop]], 1)
            uk, inv = np.unique(kk, axis=0, return_inverse=True)
            inv = inv.ravel()
            cnt = np.bincount(inv)
            pl_m = np.bincount(inv, plane[shop]) / cnt
            top_m = np.bincount(inv, top[shop]) / cnt
            u0_m = np.bincount(inv, f['u0'][L[shop]]) / cnt
            u1_m = np.bincount(inv, f['u1'][L[shop]]) / cnt
            stats['bays'] += len(uk)
            hb_u = hsh(9820, comp, uk[:, 0], uk[:, 1], uk[:, 2])
            on = (hb_u < 0.62) & (cnt > 40)
            stats['bays_lit'] += int(on.sum())
            uc = (uk[:, 1] + 0.5) * BAY
            off = pl_m + uk[:, 2] * 0.9
            sx_, sz_ = (off, uc) if comp == 0 else (uc, off)
            col = pick(SHOP_PAL, hsh(9821, comp, uk[:, 0], uk[:, 1], uk[:, 2])) * \
                (0.42 + 0.25 * hsh(9822, comp, uk[:, 0], uk[:, 1], uk[:, 2]))[:, None].astype(np.float32)
            spill_xz.append(np.stack([sx_[on], sz_[on]], 1)); spill_col.append(col[on])
            for i in range(len(uk)):
                if cnt[i] > 60:
                    bays_all.append((comp, int(uk[i, 0]), int(uk[i, 1]), int(uk[i, 2]), float(pl_m[i]), float(top_m[i]),
                                     float(u0_m[i]), float(u1_m[i])))
    if spill_xz:
        sxz = np.concatenate(spill_xz); scl = np.concatenate(spill_col)
        gm.splat(sxz[:, 0], sxz[:, 1], scl, 0.30, 0.10)

    # -------------------------------------------------------------------- blade signs
    sign_emis = np.zeros_like(img)
    cand = [b for b in bays_all if b[5] > 6.6 and b[6] + 0.8 < b[2] * BAY < b[7] - 0.8]
    if cand:
        ca = np.array([[b[0], b[1], b[2], b[3]] for b in cand], np.int64)
        xz = np.array([[(b[4] if b[0] == 0 else b[2] * BAY), (b[2] * BAY if b[0] == 0 else b[4])] for b in cand])
        order = np.argsort(hsh(9830, ca[:, 0], ca[:, 1], ca[:, 2], ca[:, 3]), kind='stable')
        chosen = _greedy(xz, order, SIGN_GAP, SIGN_MAX)
        for n_, i in enumerate(chosen):
            comp, key, cb, s, pl, top = cand[i][:6]
            f = fac[0] if comp == 0 else fac[1]
            uax = f['uax']
            us = cb * BAY
            v0, v1 = 2.7, min(2.7 + 3.4, top - 0.6)
            m = f['m'] & (f['key'][f['lab']] == key) & (f['s'] == s)
            ys, xs = np.nonzero(m)
            u = P[ys, xs, uax]; v = hag[ys, xs]
            sel = (np.abs(u - us) < 0.45) & (v > v0) & (v < v1)
            ys, xs, u, v = ys[sel], xs[sel], u[sel], v[sel]
            if len(ys) < 50:
                continue
            col = SIGN_COLS[(n_ * 2 + int(hsh(9832, comp, key, cb) * 5)) % len(SIGN_COLS)]
            lu = (u - (us - 0.45)) / 0.9; lv = (v1 - v) / (v1 - v0)
            frame = (lu < 0.09) | (lu > 0.91) | (lv < 0.025) | (lv > 0.975)
            gl = (lv - 0.05) / 0.9 * 5; gi = np.floor(gl).astype(np.int64); gfv = gl - gi
            gx = np.floor((lu - 0.2) / 0.6 * 3).astype(np.int64); gfx = (lu - 0.2) / 0.6 * 3 - gx
            gy = np.floor(gfv * 3).astype(np.int64)
            glyph = (lu > 0.2) & (lu < 0.8) & (gfv > 0.12) & (gfv < 0.88) & (gi >= 0) & (gi < 5) & \
                (hsh(9831, n_, gi, gx, gy) < 0.55) & (np.abs(gfx - 0.5) < 0.42)
            e = np.zeros((len(ys), 3), np.float32)
            e[frame] = col * 1.5
            e[glyph & ~frame] = col * 1.05
            img[ys, xs] = img[ys, xs] * 0.22 + e
            sign_emis[ys, xs] += e
            stats['signs'] += 1
            sx_, sz_ = (pl + s * 1.4, us) if comp == 0 else (us, pl + s * 1.4)
            gm.splat(np.array([sx_]), np.array([sz_]), col[None] * 1.0, 0.45, 0.28)
    # sign light on the facades around it (screen glow masked to buildings) and in the reflections
    glow = np.stack([ndi.gaussian_filter(sign_emis[..., c], 0.9 * fr.ppb) for c in range(3)], -1)
    img += glow * ((idm == 2)[..., None] * 1.6 + 0.35)
    emis += sign_emis

    # -------------------------------------------------------------------- street lamps
    dist = ndi.distance_transform_edt(~gm.base) * RES
    open_ = gm.open & ndi.binary_erosion(gm.open, iterations=2)
    cz, cx = np.nonzero(open_ & (dist >= 1.4) & (dist <= 2.0))
    lx = gm.x0 + (cx + 0.5) * RES; lz = gm.z0 + (cz + 0.5) * RES
    bx = np.floor(lx / LAMP_BLOCK).astype(np.int64); bz = np.floor(lz / LAMP_BLOCK).astype(np.int64)
    h = hsh(9860, np.floor(lx / RES).astype(np.int64), np.floor(lz / RES).astype(np.int64))
    o = np.lexsort((h, bz, bx))
    first = np.ones(len(o), bool); first[1:] = (bx[o][1:] != bx[o][:-1]) | (bz[o][1:] != bz[o][:-1])
    li = o[first]
    li = li[hsh(9861, bx[li], bz[li]) < LAMP_KEEP]
    xz = np.stack([lx[li], lz[li]], 1)
    keep = li[_greedy(xz, np.argsort(hsh(9862, bx[li], bz[li]), kind='stable'), LAMP_GAP)]
    lamp_col = np.where((hsh(9863, bx[keep], bz[keep]) < 0.78)[:, None], SOD[None], LED[None]).astype(np.float32)
    gy = gm.gy[cz[keep], cx[keep]]
    head_emis = np.zeros((H, W), np.float32)
    head_rgb = np.zeros_like(img)
    nvis = 0
    for i, li_ in enumerate(keep):
        X, Z, Y = lx[li_], lz[li_], gy[i]
        # pole: depth-tested per pixel
        ts = np.arange(0.0, LAMP_H, 0.5 / fr.ppb)
        Q = np.stack([np.full_like(ts, X), Y + ts, np.full_like(ts, Z)], 1)
        px, py, d = fr.px(Q)
        pxi = np.round(px).astype(np.int64); pyi = np.round(py).astype(np.int64)
        for dx in (-1, 0, 1):
            ok = (pxi + dx >= 0) & (pxi + dx < W) & (pyi >= 0) & (pyi < H)
            a, b, dd = pyi[ok], pxi[ok] + dx, d[ok]
            vis = dep[a, b] >= dd - 0.25
            img[a[vis], b[vis]] = img[a[vis], b[vis]] * 0.25 + np.array([0.010, 0.010, 0.018], np.float32)
        hx, hy, hd = fr.px(np.array([X, Y + LAMP_H, Z]))
        hxi, hyi = int(round(hx)), int(round(hy))
        if not (3 <= hxi < W - 3 and 3 <= hyi < H - 3) or dep[hyi, hxi] < hd - 0.3:
            pass
        else:
            nvis += 1
            # luminaire: a dark housing with a bright underside
            img[hyi - 4:hyi + 1, hxi - 8:hxi + 9] = np.array([0.012, 0.012, 0.02], np.float32)
            yy, xx = np.mgrid[-3:4, -9:10]
            ell = ((xx / 7.0) ** 2 + (yy / 2.4) ** 2) <= 1
            ys_, xs_ = hyi + 2 + yy[ell], hxi + xx[ell]
            img[ys_, xs_] = lamp_col[i] * 2.4
            emis[ys_, xs_] += lamp_col[i] * 0.9           # (reflection source: kept low so the streaks stay short)
            head_emis[hyi + 2, hxi] += 1.0
            head_rgb[hyi + 2, hxi] += lamp_col[i]
    stats['lamps'] = int(len(keep)); stats['lamps_head_visible'] = nvis
    gm.splat(lx[keep], lz[keep], lamp_col * 1.0, 0.50, 0.16)
    # halo around the heads (screen space, atmospheric)
    halo = np.stack([ndi.gaussian_filter(head_rgb[..., c], 0.35 * fr.ppb) * (2 * np.pi * (0.35 * fr.ppb) ** 2) * 0.10
                     + ndi.gaussian_filter(head_rgb[..., c], 1.1 * fr.ppb) * (2 * np.pi * (1.1 * fr.ppb) ** 2) * 0.035
                     for c in range(3)], -1)
    img += halo

    # -------------------------------------------------------------------- ground light: pools and spill on the visible ground,
    # and a little on the facade foot just above it
    Lf = gm.field(0.9, 2.6)
    ys, xs = np.nonzero(gv & (idm != 7))
    lg = gm.sample(Lf, P[ys, xs, 0], P[ys, xs, 2])
    img[ys, xs] += lg * 0.25
    emis[ys, xs] += lg * 0.12
    for f in fac:
        ys, xs = np.nonzero(f['m'] & (hag < 2.4))
        comp = f['comp']
        oX = P[ys, xs, 0].copy(); oZ = P[ys, xs, 2].copy()
        sgn = f['s'][ys, xs]
        if comp == 0:
            oX += sgn * 0.7
        else:
            oZ += sgn * 0.7
        lw = gm.sample(Lf, oX, oZ) * np.exp(-hag[ys, xs] / 1.2)[:, None] * 0.22
        img[ys, xs] += lw
    log('detail:', stats)
    return img, emis, stats
