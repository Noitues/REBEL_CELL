"""wp_lib: WPAP FACETED shared kit.  Flat planes, straight cuts, no gradients, no hand wobble.
facet_assign() cuts a mask with k random straight lines into convex planes and gives each plane ONE flat colour from a lit ramp
(light from the top left, a pinch of jitter, one accent plane, one glint plane).  All colours are flat; edges are crisp at SS and AA on the down-sample."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

VAR = ['A']
WINK = (22, 8, 38)            # aubergine ink: the one dark of the whole set
INK_ = WINK
WHITE_ = (252, 250, 246)
CREAM = (246, 240, 228)
PINK_ = (255, 61, 168)
SHADOW_DIR = (0.62, 0.78)

PAL = {
    'A': dict(          # PINK RIOT: pink planes, teal as the one complementary ink, deep indigo/teal plate
        ramp=[(84, 16, 142), (170, 20, 150), (255, 61, 168), (255, 108, 192), (255, 170, 156)],
        accent=(22, 198, 202), accent_dk=(10, 120, 140), glint=(255, 226, 242),
        page=[(14, 34, 88), (22, 66, 122), (10, 92, 124), (46, 30, 108), (8, 54, 88)], page_acc=(10, 128, 134), page_edge=(24, 190, 196),
        hub=[(120, 24, 150), (255, 61, 168), (255, 108, 192), (22, 198, 202), (255, 170, 156)],
        card_band=[(70, 12, 120), (150, 18, 140), (255, 61, 168), (255, 96, 186), (255, 150, 150)],
        tower_band=(22, 198, 202), wave_band=(150, 96, 255), slab=[(180, 20, 140), (255, 61, 168), (255, 112, 196), (22, 198, 202), (255, 170, 156)],
    ),
    'B': dict(          # ACID SUNBURST: violet and pink planes, hot orange as the one complementary ink, wine/aubergine plate
        ramp=[(104, 30, 190), (200, 24, 150), (255, 61, 168), (255, 120, 150), (255, 196, 110)],
        accent=(255, 146, 28), accent_dk=(200, 90, 20), glint=(255, 240, 214),
        page=[(58, 18, 76), (92, 24, 84), (44, 16, 92), (112, 38, 80), (34, 10, 60)], page_acc=(150, 60, 52), page_edge=(255, 146, 28),
        hub=[(104, 30, 190), (255, 61, 168), (255, 120, 150), (255, 146, 28), (255, 196, 110)],
        card_band=[(90, 24, 170), (200, 24, 150), (255, 61, 168), (255, 110, 160), (255, 190, 100)],
        tower_band=(255, 146, 28), wave_band=(160, 110, 255), slab=[(200, 24, 150), (255, 61, 168), (255, 120, 150), (255, 146, 28), (255, 196, 110)],
    ),
}


def P():
    return PAL[VAR[0]]


def facet_assign(sub, S, ramp, seed, k=4, accent=None, accent_max=0.30, glint=None, glint_max=0.16, minfrac=0.05, jit=0.20, bias=0.0,
                 light=SHADOW_DIR, spread=0.30, tries=60, flip=False):
    """sub: float mask (h,w) at S px per 1x px.  returns (rgb float32 (h,w,3), ids int (h,w), n_cells)."""
    h, w = sub.shape
    inside = sub > 0.5
    n_in = max(1, int(inside.sum()))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xx /= S
    yy /= S
    cx, cy = float(xx[inside].mean()) if inside.any() else w / 2 / S, float(yy[inside].mean()) if inside.any() else h / 2 / S
    rad = math.sqrt(n_in / (S * S)) * 0.62 + 1e-3
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(tries):
        ids = np.zeros((h, w), np.int32)
        for i in range(k):
            a = rng.uniform(0, math.pi)
            off = rng.normal(0, spread * rad)
            d = (xx - cx) * math.cos(a) + (yy - cy) * math.sin(a) - off
            ids |= (d > 0).astype(np.int32) << i
        cnt = np.bincount(ids[inside], minlength=2 ** k)
        nz = cnt[cnt > 0]
        score = nz.min() / n_in
        if best is None or score > best[0]:
            best = (score, ids)
        if score >= minfrac:
            break
    ids = best[1]
    cnt = np.bincount(ids[inside], minlength=2 ** k)
    cells = [u for u in range(2 ** k) if cnt[u] > 0]
    lx, ly = light
    info = []
    for u in cells:
        m = (ids == u) & inside
        mx, my = float(xx[m].mean()), float(yy[m].mean())
        lit = -(((mx - cx) * lx + (my - cy) * ly) / rad)
        t = 0.5 + 0.5 * float(np.clip(lit, -1, 1)) + float(rng.normal(0, jit)) + bias
        if flip:
            t = 1 - t
        info.append([u, t, cnt[u] / n_in])
    rgb = np.zeros((h, w, 3), np.float32)
    nr = len(ramp)
    cols = {}
    for u, t, fr in info:
        cols[u] = ramp[int(np.clip(t, 0, 0.999) * nr)]
    if accent is not None:
        cand = sorted([c for c in info if c[2] <= accent_max], key=lambda c: c[1])
        if cand:
            cols[cand[0][0]] = accent
    if glint is not None:
        cand = sorted([c for c in info if c[2] <= glint_max and cols[c[0]] != accent], key=lambda c: -c[1])
        if cand:
            cols[cand[0][0]] = glint
    for u in cells:
        rgb[ids == u] = cols[u]
    return rgb, ids, len(cells)


def hatch_mask_local(h, w, S, ang, pitch, width, cross=False):
    """exact, even hatch lines (no jitter) over an (h,w) SS box, pitch/width in 1x px"""
    im = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(im)
    diag = math.hypot(h, w)
    cx, cy = w / 2, h / 2
    for a in ((ang, ang + 90) if cross else (ang,)):
        th = math.radians(a)
        dx, dy = math.cos(th), math.sin(th)
        nx, ny = -dy, dx
        k = -diag / 2
        while k < diag / 2:
            d.line([(cx + nx * k - dx * diag, cy + ny * k - dy * diag), (cx + nx * k + dx * diag, cy + ny * k + dy * diag)], fill=255, width=max(1, int(round(width * S))))
            k += pitch * S
    return np.asarray(im, np.float32) / 255.0


def poly_stroke_mask(shape_hw, S, pts, width, cap=True, origin=(0, 0)):
    """constant-width straight polyline mask on an (h,w) SS canvas; pts in 1x coords; origin = SS px offset of the box"""
    im = Image.new('L', (shape_hw[1], shape_hw[0]), 0)
    d = ImageDraw.Draw(im)
    P_ = [(x * S - origin[0], y * S - origin[1]) for x, y in pts]
    wpx = max(1, int(round(width * S)))
    d.line(P_, fill=255, width=wpx, joint='curve')
    if cap:
        r = wpx / 2.0
        for (x, y) in (P_[0], P_[-1]):
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    return np.asarray(im, np.float32) / 255.0


# ---------------------------------------------------------------- per-slice-type colours (ART CALL 52 slice pass)
# every type: ramp dark->light (5 flat planes), one accent plane (the neighbour hue), one glint plane, a pattern name, a hatch tint
SLICE = {
    'A': {   # RIOT SET: orange / cobalt / hot pink / acid green
        'BURST':  dict(ramp=[(176, 54, 10), (226, 80, 14), (255, 122, 26), (255, 160, 56), (255, 204, 110)], accent=(255, 214, 40), glint=(255, 242, 206), pat='DOTS', tint=0.32),
        'SHIELD': dict(ramp=[(14, 28, 138), (28, 64, 206), (50, 108, 255), (92, 156, 255), (150, 196, 255)], accent=(32, 214, 232), glint=(226, 240, 255), pat='HEX', tint=0.26),
        'TURRET': dict(ramp=[(110, 12, 104), (196, 20, 138), (255, 61, 168), (255, 106, 192), (255, 166, 214)], accent=(150, 70, 255), glint=(255, 226, 242), pat='RINGS', tint=0.30),
        'REPAIR': dict(ramp=[(12, 98, 54), (30, 156, 56), (96, 214, 36), (162, 238, 64), (212, 255, 126)], accent=(24, 206, 170), glint=(240, 255, 214), pat='PLUS', tint=0.28),
    },
    'B': {   # NIGHT SHIFT: acid yellow / cyan / violet / pink
        'BURST':  dict(ramp=[(150, 104, 0), (222, 160, 0), (255, 208, 18), (255, 232, 84), (255, 246, 168)], accent=(255, 132, 24), glint=(255, 252, 226), pat='DOTS', tint=0.34),
        'SHIELD': dict(ramp=[(6, 72, 104), (8, 124, 156), (18, 186, 210), (84, 224, 236), (168, 246, 248)], accent=(44, 110, 255), glint=(230, 252, 252), pat='HEX', tint=0.26),
        'TURRET': dict(ramp=[(56, 16, 132), (96, 36, 196), (138, 66, 255), (178, 118, 255), (214, 170, 255)], accent=(255, 61, 168), glint=(240, 228, 255), pat='RINGS', tint=0.30),
        'REPAIR': dict(ramp=[(130, 14, 100), (200, 22, 140), (255, 61, 168), (255, 112, 192), (255, 172, 216)], accent=(255, 150, 40), glint=(255, 232, 244), pat='PLUS', tint=0.30),
    },
}
PATNAME = {'DOTS': 'HALFTONE DOTS', 'HEX': 'HONEYCOMB', 'RINGS': 'TARGET RINGS', 'PLUS': 'PLUS STITCH'}
