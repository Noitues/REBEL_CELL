"""Round 12 MODEM facade: post pass (Pillow + numpy).

Input: Blender passes <prefix>_beauty.npy (linear HDR), _id.npy (object index, view depth), _nrm.npy,
_ids.json. Adds: painted faceted sky, depth haze, wobbly ink (id / depth / normal edges, weight by
depth), bloom (screen blend), rain streaks tinted by nearby neon, splashes, paint texture, grain.
Usage: python post.py <prefix> <rain|day|night> <out.png>
"""
import json
import math
import random
import os
import sys
import zlib

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

INK = np.array([0x15, 0x11, 0x0f], np.float32) / 255

ST = {
    'rain': dict(fog='#56607a', fog_d=70.0, fog_max=0.75, sky=('#2f3850', '#6c7590'), bloom=0.9, thr=0.85,
                 rain=1500, rain_a=(30, 80), splash=170, ink=0.92),
    'day': dict(fog='#b9c0c4', fog_d=140.0, fog_max=0.5, sky=('#86a8c6', '#e3dccb'), bloom=0.22, thr=1.0,
                rain=0, rain_a=(0, 0), splash=0, ink=1.0),
    'night': dict(fog='#1d1a33', fog_d=90.0, fog_max=0.8, sky=('#07091a', '#33204a'), bloom=1.25, thr=0.7,
                  rain=650, rain_a=(25, 70), splash=90, ink=0.95),
}


def hexf(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255


def to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def _box(a, r, axis):
    """Box blur of radius r along axis (edge padded, cumsum)."""
    if r < 1:
        return a
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad, mode='edge'), axis=axis, dtype=np.float64)
    n = a.shape[axis]
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return ((hi - lo) / (2 * r + 1)).astype(np.float32)


def gblur(a, sigma):
    """Approximate Gaussian blur (3 box passes per axis; downsampled for large sigma)."""
    if sigma <= 0.3:
        return a
    a = a.astype(np.float32)
    k = 1
    while sigma / k > 10 and k < 8:
        k *= 2
    h, w = a.shape[:2]
    if k > 1:
        hh, ww = h // k * k, w // k * k
        sm = a[:hh, :ww].reshape(hh // k, k, ww // k, k, *a.shape[2:]).mean(axis=(1, 3))
    else:
        sm = a
    s = sigma / k
    r = max(1, int(round(math.sqrt(12 * s * s / 3 + 1) - 1) // 2)) if s >= 1 else 1
    for _ in range(3):
        sm = _box(_box(sm, r, 0), r, 1)
    if k > 1:
        sm = np.repeat(np.repeat(sm, k, 0), k, 1)
        sm = _box(_box(sm, k // 2, 0), k // 2, 1)
        out = np.empty_like(a)
        out[:hh, :ww] = sm
        out[hh:, :] = out[hh - 1:hh, :] if hh < h else out[hh:, :]
        out[:, ww:] = out[:, ww - 1:ww] if ww < w else out[:, ww:]
        return out
    return sm


def noise2(h, w, cell, seed):
    rng = np.random.default_rng(seed)
    g = rng.random((h // cell + 2, w // cell + 2)).astype(np.float32)
    im = Image.fromarray(g, 'F').resize((w + 2 * cell, h + 2 * cell), Image.BICUBIC)
    return np.asarray(im, np.float32)[cell:cell + h, cell:cell + w]


def sky_layer(h, w, top, bot, seed):
    """Faceted gradient sky (Cv2): jittered triangles, each a flat tone of the gradient."""
    rng = random.Random(str(('sky', seed)))
    im = Image.new('RGB', (w, h))
    d = ImageDraw.Draw(im)
    t0, t1 = hexf(top), hexf(bot)
    cw, ch = 150, 110
    nx, ny = w // cw + 2, h // ch + 3
    P = {}
    for i in range(nx + 1):
        for j in range(ny + 1):
            jx = rng.uniform(-0.4, 0.4) * cw if 0 < i < nx else 0
            jy = rng.uniform(-0.4, 0.4) * ch if 0 < j < ny else 0
            P[i, j] = (i * cw - cw + jx, j * ch - ch + jy)
    for i in range(nx):
        for j in range(ny):
            a, b, c, e = P[i, j], P[i + 1, j], P[i + 1, j + 1], P[i, j + 1]
            for tri in ((a, b, c), (a, c, e)) if rng.random() < 0.5 else ((a, b, e), (b, c, e)):
                cy = sum(p[1] for p in tri) / 3
                t = min(1, max(0, cy / (h * 0.7)))
                col = (t0 + (t1 - t0) * t) * rng.uniform(0.94, 1.06)
                d.polygon(tri, fill=tuple(int(min(255, x * 255)) for x in col))
    return np.asarray(im, np.float32) / 255


def edges(idx, depth, nrm, sign_ids):
    """Ink candidates between each pixel and its right / lower neighbour."""
    H, W = idx.shape
    m_id = np.zeros((H, W), bool)
    m_cr = np.zeros((H, W), bool)
    for dy, dx in ((0, 1), (1, 0)):
        a = (slice(0, H - dy), slice(0, W - dx))
        b = (slice(dy, H), slice(dx, W))
        i1, i2 = idx[a], idx[b]
        sg = np.isin(i1, sign_ids) | np.isin(i2, sign_ids)
        diff = (i1 != i2) & ~sg
        d1, d2 = depth[a], depth[b]
        dd = np.abs(d1 - d2) / np.maximum(np.minimum(d1, d2), 0.1)
        dep = (dd > 0.05) & ~sg & (i1 == i2)
        nd = (nrm[a] * nrm[b]).sum(-1)
        cr = (nd < 0.75) & ~sg & (i1 == i2)
        m_id[a] |= diff | dep
        m_cr[a] |= cr
    return m_id, m_cr


def dilate(m, r):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r + 0.5:
                out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out


def wobble(m, seed, amp=1.4):
    H, W = m.shape
    dx = (noise2(H, W, 40, seed) - 0.5) * 2 * amp
    dy = (noise2(H, W, 40, seed + 1) - 0.5) * 2 * amp
    yy, xx = np.mgrid[0:H, 0:W]
    sx = np.clip((xx + dx).round().astype(int), 0, W - 1)
    sy = np.clip((yy + dy).round().astype(int), 0, H - 1)
    return m[sy, sx]


def rain_layer(H, W, n, alpha, glow, seed, slant=0.16):
    rng = random.Random(str(('rain', seed)))
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    base = np.array([175, 185, 205], np.float32)
    for k in range(n):
        near = rng.random() < 0.25
        L = rng.uniform(60, 150) if near else rng.uniform(22, 60)
        x = rng.uniform(-100, W)
        y = rng.uniform(-150, H)
        gx, gy = int(min(W - 1, max(0, x))), int(min(H - 1, max(0, y)))
        g = glow[gy, gx]
        col = np.clip(base * 0.55 + g * 255 * 1.6, 0, 255)
        a = rng.randint(*alpha) * (1.25 if near else 0.8)
        a = min(255, a + int(g.max() * 120))
        d.line([(x, y), (x + slant * L, y + L)], fill=(int(col[0]), int(col[1]), int(col[2]), int(a)),
               width=2 if near else 1)
    return lay


def splash_layer(H, W, ground, n, glow, seed):
    rng = random.Random(str(('spl', seed)))
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    ys, xs = np.nonzero(ground[::4, ::4])
    if len(ys) == 0:
        return lay
    for k in range(n):
        i = rng.randrange(len(ys))
        y, x = ys[i] * 4, xs[i] * 4
        r = rng.uniform(2, 6) * (0.5 + y / H)
        g = glow[y, x]
        col = np.clip(np.array([190, 200, 215]) * 0.6 + g * 255 * 1.5, 0, 255).astype(int)
        a = rng.randint(50, 110)
        d.ellipse([x - r, y - r * 0.28, x + r, y + r * 0.28], outline=(*col, a), width=1)
        if rng.random() < 0.5:
            d.line([(x, y - 1), (x + rng.uniform(-2, 2), y - rng.uniform(4, 10))], fill=(*col, a), width=1)
    return lay


def glow_tint(bloom):
    g = gblur(bloom, 40)
    return np.clip(to_srgb(g), 0, 1)


def paint_texture(img, seed):
    """Painterly speckle + horizontal brush drag, overlay blend (mean-neutral)."""
    H, W = img.shape[:2]
    fine = noise2(H, W, 2, seed)
    blot = noise2(H, W, 18, seed + 7)
    tex = (0.4 * fine + 0.6 * blot - 0.5) * 0.08 + 0.5
    t = tex[..., None]
    over = np.where(img < 0.5, 2 * img * t, 1 - 2 * (1 - img) * (1 - t))
    return over


def run(prefix, state, out):
    st = ST[state]
    beauty = np.load(prefix + '_beauty.npy').astype(np.float32)
    aux = np.load(prefix + '_id.npy').astype(np.float32)
    nrm = np.load(prefix + '_nrm.npy').astype(np.float32) * 2 - 1
    kinds = {int(k): v for k, v in json.load(open(prefix + '_ids.json')).items()}
    H, W = beauty.shape[:2]
    idx = np.rint(aux[..., 0]).astype(np.int32)
    depth = aux[..., 1].copy()
    sky = idx == 0
    depth[sky] = 1000.0
    sign_ids = [k for k, v in kinds.items() if v[1] == 'sign']
    ground_ids = [k for k, v in kinds.items() if v[1] == 'ground']
    emis_ids = [k for k, v in kinds.items() if v[1] in ('window', 'sign', 'citywin')]
    sign = np.isin(idx, sign_ids)
    ground = np.isin(idx, ground_ids)
    emis = np.isin(idx, emis_ids)
    seed = zlib.crc32(os.path.basename(prefix).encode()) % 1000

    # sky
    skyc = to_lin(sky_layer(H, W, st['sky'][0], st['sky'][1], state))
    img = np.where(sky[..., None], skyc, beauty)

    # bloom source (HDR, before haze)
    lum = img.mean(-1, keepdims=True)
    src = np.maximum(img - st['thr'] * 0.5, 0) * (lum > st['thr'] * 0.6)
    src = src * np.where(emis[..., None], 1.0, np.where(lum > 1.3, 0.35, 0.0)) * (~sky[..., None])
    src = src * np.where(depth > 55, 0.3, 1.0)[..., None]
    bloom = 0.55 * gblur(src, 5) + 0.35 * gblur(src, 18) + 0.25 * gblur(src, 55)
    bloom *= st['bloom']

    # haze (not on sky, less on emissive)
    fog = hexf(st['fog'])
    fogl = to_lin(fog)
    f = 1 - np.exp(-np.maximum(depth - 20.0, 0) / st['fog_d'])
    f = np.minimum(f, st['fog_max'])
    f = np.where(sky, 0, f) * np.where(emis, 0.5, 1.0)
    img = img * (1 - f[..., None]) + fogl * f[..., None]

    # wet floor: neon reflections as broken vertical light columns under the sources (sign strongest)
    kref = {'rain': 0.9, 'day': 0.15, 'night': 1.2}[state]
    E = beauty * (sign[..., None] * 1.0 + (emis & ~sign)[..., None] * 0.25)
    pres = (E.max(-1) > 0.05).sum(0).astype(np.float32)
    colc = E.sum(0) / np.maximum(pres, 1)[:, None]
    colc *= np.minimum(pres / 120.0, 1.0)[:, None]
    colc = gblur(colc[None], 6)[0]
    rng = np.random.default_rng(seed + 21)
    rip = rng.random((H // 5 + 2, W // 45 + 2)).astype(np.float32)
    rip = np.asarray(Image.fromarray(rip, 'F').resize((W, H), Image.BICUBIC))
    pud = noise2(H, W, 60, seed + 22)
    wetm = np.clip((pud - 0.35) * 4, 0, 1) * (0.45 + 0.55 * (rip > 0.45))
    img = img + np.where(ground[..., None], colc[None] * wetm[..., None] * kref, 0)
    # plus the bloom dragged down a little (light trails on the wet floor)
    if state != 'day':
        refl = gblur(bloom, 3)
        streak = np.zeros_like(refl)
        for s in range(1, 60, 4):
            streak[s:] += refl[:-s] * (1 - s / 60)
        img = img + np.where(ground[..., None], streak / 8.0 * 0.6, 0)

    disp = to_srgb(img)

    # ink
    m_id, m_cr = edges(idx, depth, nrm, sign_ids)
    near = depth < 34
    mid = (depth >= 34) & (depth < 70)
    m_heavy = dilate(m_id & near, 1)
    m_mid = m_id & mid | dilate(m_cr & near, 1) & ~mid | (m_cr & mid)
    m_far = (m_id | m_cr) & (depth >= 70)
    a = np.zeros((H, W), np.float32)
    a = np.maximum(a, wobble(m_heavy, seed + 3) * 1.0)
    a = np.maximum(a, wobble(m_mid, seed + 5) * 0.85)
    a = np.maximum(a, m_far * 0.3)
    a = gblur(a, 0.6) * 1.15
    a = np.clip(a, 0, 1) * (1 - f * 0.85) * st['ink']
    a = np.where(sign, 0, a)
    disp = disp * (1 - a[..., None]) + INK * a[..., None]

    # bloom on top (screen)
    bl = np.clip(to_srgb(bloom) * 1.0, 0, 1)
    disp = 1 - (1 - disp) * (1 - bl)

    # steam from the alley vents / roof (layout from the Blender pass)
    try:
        vents = json.load(open(prefix + '_layout.json'))['vents_px']
    except Exception:
        vents = []
    if vents:
        nz = noise2(H, W, 22, seed + 31) * noise2(H, W, 70, seed + 32) * 2.2
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        acc = np.zeros((H, W), np.float32)
        for k, (vx, vy) in enumerate(vents):
            sc = 1.0 if k == 0 else 0.6
            dy = (vy - yy) / sc
            wdt = (22 + np.maximum(dy, 0) * 0.3) * sc
            m = np.exp(-((xx - vx - np.maximum(dy, 0) * 0.3 * sc) / wdt) ** 2) * np.clip((dy + 15) / 30, 0, 1)                 * np.exp(-np.maximum(dy, 0) / (170 * sc))
            acc += m
        acc = np.clip(acc * nz, 0, 1)
        stc = {'rain': 0.5, 'day': 0.22, 'night': 0.55}[state]
        tint = np.clip(0.75 + glow_tint(bloom) * 0.8, 0, 1)
        disp = 1 - (1 - disp) * (1 - acc[..., None] * stc * tint)

    # texture, vignette
    disp = paint_texture(disp, seed + 11)
    yy, xx = np.mgrid[0:H, 0:W]
    v = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
    disp = disp * (1 - 0.16 * np.clip(v - 0.3, 0, 1))[..., None]
    pil = Image.fromarray((np.clip(disp, 0, 1) * 255).astype(np.uint8)).convert('RGBA')

    # rain
    glow = np.clip(bl, 0, 1)
    if st['rain']:
        pil = Image.alpha_composite(pil, rain_layer(H, W, st['rain'], st['rain_a'], glow, seed))
        pil = Image.alpha_composite(pil, splash_layer(H, W, ground & (np.arange(H)[:, None] > H * 0.75),
                                                      st['splash'], glow, seed))
    pil.convert('RGB').save(out)
    print('wrote', out)


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2], sys.argv[3])
