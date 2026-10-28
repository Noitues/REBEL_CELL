"""P2 emissive signage on hero facades (punch #7). Walls are found from the depth recon (planar +X / +Z facades), signs are procedural pictograms (no words)
evaluated per pixel in wall (u, v) BU coordinates, so at 2x capture they are natively sharper.
signs(geo, P, seed) -> dict(emis=linear RGB emissive (H,W,3), walls=[dict], hero=dict)"""
import numpy as np
from scipy import ndimage as ndi
import p1lib as L
import p1_comp as C

W, H = C.W, C.H
S = C.S
SOD = np.array([1.0, 0.42, 0.10], np.float32)
ICE = np.array([0.80, 0.93, 1.0], np.float32)
JADE = np.array([0.12, 0.85, 0.62], np.float32)
ROSE = np.array([1.0, 0.30, 0.22], np.float32)
COLS = [SOD, ICE, SOD, JADE, ICE, ROSE]


def find_walls(geo, P, min_w=4.5, min_h=12.0):
    n = geo['n'].astype(np.float32); idm = geo['idm']; hag = geo['hag']
    out = []
    for kind, comp, uax in (('Z', 2, 0), ('X', 0, 2)):
        m = (n[..., comp] > 0.85) & (idm == 2) & (hag > 4)
        m = ndi.binary_opening(m, iterations=S)
        lab, nl = ndi.label(m)
        objs = ndi.find_objects(lab)
        for i, sl in enumerate(objs, 1):
            mm = lab[sl] == i
            area = int(mm.sum())
            if area < 700 * S * S:
                continue
            c = P[sl][..., 2 if kind == 'Z' else 0][mm]
            if c.std() > 0.5:
                continue
            u = P[sl][..., uax][mm]; v = P[sl][..., 1][mm]
            wu = u.max() - u.min(); wv = v.max() - v.min()
            if wu < min_w or wv < min_h:
                continue
            cy, cx = ndi.center_of_mass(mm)
            out.append(dict(kind=kind, lab=i, sl=sl, plane=float(np.median(c)), u0=float(u.min()), u1=float(u.max()), v0=float(v.min()), v1=float(v.max()),
                            area=area / (S * S), cx=float(cx + sl[1].start) / S, cy=float(cy + sl[0].start) / S, mask=(lab == i)))
    return out


def _sign_pattern(u, v, kind, typ, seed):
    """u, v in [0,1] across the sign rect -> (ink, glow) float masks."""
    ink = np.zeros_like(u); on = np.zeros_like(u)
    if typ == 0:     # stacked bars + hex pip
        for k in range(4):
            y0 = 0.1 + k * 0.22
            on = np.maximum(on, ((v > y0) & (v < y0 + 0.11) & (u > 0.18) & (u < 0.9 - 0.12 * ((k * 7 + seed) % 4))).astype(np.float32))
        on = np.maximum(on, ((np.hypot((u - 0.08) * 1.0, (v - 0.5) * 0.45) < 0.07)).astype(np.float32))
    elif typ == 1:   # ring + cross
        r = np.hypot((u - 0.5) * 1.0, (v - 0.5) * 0.5)
        on = ((r > 0.30) & (r < 0.40)).astype(np.float32)
        on = np.maximum(on, ((np.abs(u - 0.5) < 0.04) & (np.abs(v - 0.5) < 0.40)).astype(np.float32))
        on = np.maximum(on, ((np.abs(v - 0.5) < 0.07) & (np.abs(u - 0.5) < 0.25)).astype(np.float32))
    elif typ == 2:   # chevrons stack
        for k in range(3):
            c = 0.2 + k * 0.28
            vv = np.abs(u - 0.5) * 0.6
            on = np.maximum(on, ((np.abs(v - (c + vv)) < 0.06) & (np.abs(u - 0.5) < 0.42)).astype(np.float32))
    else:            # vertical hanging strip: segmented bar
        on = ((u > 0.30) & (u < 0.70) & ((v * 7) % 1.0 < 0.72)).astype(np.float32)
    return on


def signs(geo, P, n_signs=15, seed=3, sel=None):
    rng = np.random.RandomState(seed)
    walls = find_walls(geo, P)
    # score: tall, wide, large visible area; prefer the dense downtown (left of the HQ park, below the water)
    def ok(w):
        return not (w['cx'] > 1300 and w['cy'] < 700) and w['cy'] > 60
    walls = [w for w in walls if ok(w)]
    walls.sort(key=lambda w: -(w['area'] * min(w['v1'] - w['v0'], 40)))
    chosen = []
    for w in walls:
        if all(np.hypot(w['cx'] - c['cx'], w['cy'] - c['cy']) > 150 for c in chosen):
            chosen.append(w)
        if len(chosen) >= n_signs:
            break
    emis = np.zeros((H, W, 3), np.float32)
    body = np.zeros((H, W), np.float32)    # sign plate (dark backing)
    hero = None
    # hero = chosen wall nearest to HERO point (warm landmark)
    HX, HY = 1300.0, 760.0
    hero_i = int(np.argmin([np.hypot(w['cx'] - HX, w['cy'] - HY) for w in chosen])) if chosen else -1
    uax = {'Z': 0, 'X': 2}
    for i, w in enumerate(chosen):
        col = COLS[(i * 5 + seed) % len(COLS)]
        typ = (i + seed) % 4
        wu = w['u1'] - w['u0']; wv = w['v1'] - w['v0']
        sw = min(wu * 0.85, 13.0) if typ != 3 else min(wu * 0.35, 3.2)
        sh = min(wv * 0.36, 14.0) if typ != 3 else min(wv * 0.62, 30.0)
        uc = (w['u0'] + w['u1']) / 2; vc = w['v0'] + wv * (0.62 if typ != 3 else 0.5)
        uu = P[..., uax[w['kind']]]; vv = P[..., 1]
        m = w['mask'] & (np.abs(uu - uc) < sw / 2) & (np.abs(vv - vc) < sh / 2)
        if i == hero_i:
            # hero: the whole lit facade breathes warm, with a tall sign
            m_all = w['mask']
            fac = 0.22 + 0.16 * (((uu * 1.7) % 1.0 < 0.5) & ((vv * 0.6) % 1.0 < 0.55))
            emis += (SOD * 0.9)[None, None] * (m_all * fac)[..., None]
            hero = dict(cx=w['cx'], cy=w['cy'], kind=w['kind'])
        uloc = np.clip((uu - (uc - sw / 2)) / sw, 0, 1); vloc = np.clip(1 - (vv - (vc - sh / 2)) / sh, 0, 1)
        pat = _sign_pattern(uloc, vloc, w['kind'], typ, i)
        body = np.maximum(body, m.astype(np.float32))
        emis += col[None, None] * (m * (0.12 + 2.6 * pat))[..., None]
    return dict(emis=emis, body=body, walls=[{k: v for k, v in w.items() if k not in ('mask', 'sl')} for w in chosen], hero=hero)
