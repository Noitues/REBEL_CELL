"""holo.py - the crew photo as a holographic scanline card (additive light)."""
import numpy as np
from PIL import Image, ImageDraw
from lightpen import gblur, font, CYAN, WHITE, PINK


def facet_texture(w, h, cell, rng):
    """Jittered triangle tessellation with random flat values (low-poly facets)."""
    im = Image.new("L", (w, h), 128)
    d = ImageDraw.Draw(im)
    nx, ny = w // cell + 3, h // cell + 3
    pts = np.zeros((ny, nx, 2))
    for j in range(ny):
        for i in range(nx):
            pts[j, i] = ((i - 1) * cell + rng.uniform(-0.38, 0.38) * cell,
                         (j - 1) * cell + rng.uniform(-0.38, 0.38) * cell)
    for j in range(ny - 1):
        for i in range(nx - 1):
            a, b, c, e = pts[j, i], pts[j, i + 1], pts[j + 1, i], pts[j + 1, i + 1]
            for tri in ((a, b, c), (b, e, c)):
                d.polygon([tuple(p) for p in tri], fill=int(rng.uniform(0.62, 1.0) * 255))
    return np.asarray(im, np.float32) / 255.0


def portrait(w, h, rng):
    """A faceted hooded operative, grayscale 0..1, plus alpha mask."""
    sx, sy = w / 200.0, h / 240.0

    def P(pts):
        return [(x * sx, y * sy) for x, y in pts]
    val = Image.new("L", (w, h), 0)
    msk = Image.new("L", (w, h), 0)
    dv, dm = ImageDraw.Draw(val), ImageDraw.Draw(msk)
    shapes = [
        ([(4, 240), (22, 190), (62, 166), (138, 164), (176, 186), (196, 240)], 0.42),
        ([(52, 182), (40, 112), (56, 56), (98, 26), (142, 46), (162, 98), (152, 182)], 0.66),
        ([(74, 170), (68, 106), (84, 74), (120, 70), (134, 100), (130, 170)], 0.16),
        ([(82, 134), (126, 126), (124, 162), (94, 170)], 0.38),
        ([(70, 106), (134, 97), (136, 117), (72, 127)], 1.0),
        ([(88, 166), (114, 166), (110, 208), (92, 208)], 0.3),   # collar seam
    ]
    for pts, v in shapes:
        dv.polygon(P(pts), fill=int(v * 255))
        dm.polygon(P(pts), fill=255)
    g = np.asarray(val, np.float32) / 255.0
    m = np.asarray(msk, np.float32) / 255.0
    tex = facet_texture(w, h, int(16 * sx), rng)
    visor = (g > 0.95).astype(np.float32)
    g = g * np.where(visor > 0, 1.0, tex)
    # hood rim light from the left (where the pen light is)
    rim = np.clip(m - gblur(m, 3.0), 0, 1)
    g = g + rim * 0.9
    # soft key light gradient
    yy, xx = np.mgrid[0:h, 0:w]
    g = g * (0.75 + 0.35 * (1 - xx / w))
    return np.clip(g, 0, 1.4), m, visor


def holo_card(canvas_hw, x, y, w, h, rng, tint=CYAN, label="OP-03 // KIRA"):
    """Return (add HxWx3, veil HxW) for a holographic card placed at x, y."""
    H, W = canvas_hw
    add = np.zeros((H, W, 3), np.float32)
    veil = np.zeros((H, W), np.float32)
    pw, ph = w - 24, h - 46
    g, m, visor = portrait(pw, ph, rng)
    card = np.zeros((h, w), np.float32)
    card[34:34 + ph, 12:12 + pw] = g
    cm = np.zeros((h, w), np.float32)
    cm[34:34 + ph, 12:12 + pw] = m
    vis = np.zeros((h, w), np.float32)
    vis[34:34 + ph, 12:12 + pw] = visor
    # field: faint projected plane with a vertical gradient
    yy, xx = np.mgrid[0:h, 0:w]
    plane = 0.07 + 0.06 * (yy / h)
    # header micro-type (digital, belongs to the projection)
    hdr = Image.new("L", (w, h), 0)
    dh = ImageDraw.Draw(hdr)
    dh.text((12, 8), label, font=font(17, "SemiBold Condensed"), fill=230)
    dh.text((w - 12, 8), "LIVE", font=font(15, "SemiBold Condensed"), fill=150, anchor="ra")
    for i in range(18):  # tiny data ticks along the bottom
        hx = 12 + i * ((w - 24) / 18)
        hl = 4 + (i * 7 % 5) * 2
        dh.line([(hx, h - 6 - hl), (hx, h - 6)], fill=110, width=1)
    hdr = np.asarray(hdr, np.float32) / 255.0
    lum = plane + card * 0.95 + hdr * 0.9
    # scanlines + slow interference band
    scan = np.where((yy % 3) == 0, 0.45, 1.0)
    band = 1.0 + 0.35 * np.exp(-((yy - h * 0.62) / 7.0) ** 2)
    lum = lum * scan * band
    # glitch slices
    out = np.stack([lum, lum, lum], -1)
    for _ in range(3):
        y0 = int(rng.uniform(40, h - 40))
        hh = int(rng.uniform(3, 9))
        dx = int(rng.choice([-1, 1]) * rng.uniform(4, 11))
        out[y0:y0 + hh] = np.roll(out[y0:y0 + hh], dx, axis=1)
    # RGB split
    r = np.roll(out[..., 0], 2, axis=1)
    b = np.roll(out[..., 2], -2, axis=1)
    L = out[..., 1]
    col = np.stack([r * tint[0], L * tint[1], b * tint[2]], -1) * 0.95
    col += WHITE * (np.clip(L - 0.8, 0, 1) * 0.8)[..., None]
    # visor glows in the Cell's pink
    vg = gblur(vis, 1.0) + gblur(vis, 4) * 0.8
    col += PINK * vg[..., None] * 0.9
    # edge fade so the projection feels like light, not a sticker
    fade = np.clip(np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]) / 6.0, 0, 1)
    col *= fade[..., None]
    add[y:y + h, x:x + w] = col
    vm = np.zeros((H, W), np.float32)
    vm[y:y + h, x:x + w] = 1.0
    veil = np.clip(gblur(vm, 10), 0, 1) * 0.62
    return add, veil
