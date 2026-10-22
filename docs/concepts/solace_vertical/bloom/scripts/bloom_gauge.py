"""Solace THE BLOOM v2: CRT-terminal gauges and the CAUGHT bits burst (PIL + numpy overlays).

Medium mapping (ART_BIBLE 1.2): the TIDE gauge is the CRT terminal (navy glass, cyan edge, Share Tech Mono, scanlines);
the live % is bare Anton (no box); CAUGHT is binary bits, pink; the what-if forecast is red grease pencil, dashed.
The tube fill uses the direction's own material (A necrosis / B mycelium / C culture) so the gauge shows what the Bloom
is made of. Bands never read by colour alone: each band has its own glyph (dash, 1 / 2 / 3 chevrons, X block) and the
current one is bracketed.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import solace_lib as L
import bloom_skins as S

SS = 2
ANTON = os.path.join(L.FONTS, "Anton-Regular.ttf")
CYAN = (56, 217, 255)
CYAN_D = (24, 110, 150)
NAVY = (5, 15, 32)
NAVY2 = (9, 28, 52)
PINK8 = (255, 70, 150)
LIME8 = (150, 255, 70)
RED8 = (232, 40, 44)
TUBE_RANGE = 3.6             # gap units (route layers) shown by the tube
BAND_GAP = {"DORMANT": 3.4, "CREEPING": 2.6, "CLOSE": 1.5, "CATCHING": 0.6, "CAUGHT": 0.0}
BANDS = ["DORMANT", "CREEPING", "CLOSE", "CATCHING", "CAUGHT"]

# per direction skin parameters for the small gauge fills (units = 8 px)
GP = {
    "A": dict(fq=0.20, zT=1.0, zM=3.0, seed=7, hpitch=7, vgain=1.0, ew=1.4, vw=1.4, keep_lo=0.42, body0=0.10, body1=0.0),
    "B": dict(fq=0.22, zT=0.8, zM=2.6, zC=3.2, cap=1.9, seed=7, tw=1.0, lump=30.0, matv=0.62, matw=1.0),
    "C": dict(fq=0.24, zT=0.6, zM=2.4, bub=2.7, seed=7, rip=70.0, alpha=0.95, see=0.4),
}
GU = 8.0


def mono(px):
    return ImageFont.truetype(L.MONO, int(px))


def anton(px):
    return ImageFont.truetype(ANTON, int(px))


def fill_array(kind, w, h, front_y, vertical=True, seed_off=0):
    """RGB float array (h, w): navy glass with the direction's material below `front_y` (vertical) / left of it."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    if not vertical:                       # horizontal bar: swap so the same field code runs
        yy, xx = xx, yy
        hh, ww = w, h
    else:
        hh, ww = h, w
    wob = 4.0 * (L.fbm(xx * 0.07, np.zeros_like(xx) + 3.0, 5 + seed_off, 3) - 0.5)
    if kind == "C":
        wob = wob + 5.0 * (np.cos((xx / max(ww - 1, 1) - 0.5) * math.pi) ** 2)   # meniscus climbs the glass
    d = (yy - (front_y + wob)) / GU
    glass = np.stack([4 + 6 * yy / hh, 14 + 14 * yy / hh, 30 + 18 * yy / hh], -1).astype(np.float32) / 255.0
    cover = S.SM(-0.15, 0.2, d)
    u, v = xx / GU, yy / GU
    c = dict(GP[kind])
    c["seed"] = c["seed"] + seed_off
    out = S.SKINS[kind](glass, cover, d, u, v, c)
    if not vertical:
        pass
    return out


def scan(img, strength=0.16, pitch=3):
    a = np.asarray(img.convert("RGB"), np.float32) / 255.0
    h = a.shape[0]
    row = ((np.arange(h) % pitch) == 0).astype(np.float32)[:, None, None]
    a = a * (1 - strength * row)
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def wobble_line(d, pts, col, w, dash=(14, 9), seed=1, amp=1.6):
    """Red grease-pencil style dashed polyline (double stroke, slight wobble). pts in output px, d is an SS draw."""
    rnd = np.random.RandomState(seed)
    for off in (0.0, 1.0):
        seg = []
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 3))
            for k in range(n):
                t = k / n
                seg.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
        seg.append(pts[-1])
        run, on = 0.0, True
        cur = []
        for i, (x, y) in enumerate(seg):
            wx = amp * math.sin(i * 0.31 + off * 2.0 + seed) + off * 1.1
            wy = amp * math.cos(i * 0.27 + seed) + off * 0.9
            if i:
                run += math.hypot(x - seg[i - 1][0], y - seg[i - 1][1])
            if run > (dash[0] if on else dash[1]):
                if on and len(cur) > 1:
                    d.line([(a * SS, b * SS) for a, b in cur], fill=col, width=int(w * SS * (1.0 if off == 0 else 0.6)), joint="curve")
                cur, on, run = [], not on, 0.0
            if on:
                cur.append((x + wx, y + wy))
        if on and len(cur) > 1:
            d.line([(a * SS, b * SS) for a, b in cur], fill=col, width=int(w * SS * (1.0 if off == 0 else 0.6)), joint="curve")


def chevrons(d, cx, cy, n, size, col, w):
    for k in range(n):
        y = cy + (k - (n - 1) / 2) * size * 0.9
        d.line([((cx - size) * SS, (y - size * 0.45) * SS), (cx * SS, (y + size * 0.1) * SS), ((cx + size) * SS, (y - size * 0.45) * SS)], fill=col, width=int(w * SS))


def band_glyph(d, cx, cy, band, size, col, w=2):
    """DORMANT: dash.  CREEPING/CLOSE/CATCHING: 1/2/3 chevrons.  CAUGHT: block with an X."""
    if band == "DORMANT":
        d.line([((cx - size) * SS, cy * SS), ((cx + size) * SS, cy * SS)], fill=col, width=int(w * SS))
    elif band == "CAUGHT":
        d.rectangle([(cx - size * 0.9) * SS, (cy - size * 0.9) * SS, (cx + size * 0.9) * SS, (cy + size * 0.9) * SS], fill=col)
        d.line([((cx - size * 0.5) * SS, (cy - size * 0.5) * SS), ((cx + size * 0.5) * SS, (cy + size * 0.5) * SS)], fill=NAVY, width=int(w * SS))
        d.line([((cx - size * 0.5) * SS, (cy + size * 0.5) * SS), ((cx + size * 0.5) * SS, (cy - size * 0.5) * SS)], fill=NAVY, width=int(w * SS))
    else:
        chevrons(d, cx, cy, {"CREEPING": 1, "CLOSE": 2, "CATCHING": 3}[band], size, col, w)


def tide_gauge(kind, band, gap=None, w=150, h=600, forecast_gap=None, seed_off=0, label=True):
    """The TIDE gauge as an RGBA image (w x h). Tube on the left, band lane on the right, bezel + scanlines."""
    gap = BAND_GAP[band] if gap is None else gap
    S2 = SS
    img = Image.new("RGBA", (w * S2, h * S2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = 10
    d.rounded_rectangle([0, 0, w * S2 - 1, h * S2 - 1], r * S2, fill=NAVY + (255,), outline=CYAN + (255,), width=2 * S2)
    d.rounded_rectangle([5 * S2, 5 * S2, (w - 5) * S2, (h - 5) * S2], (r - 3) * S2, outline=CYAN_D + (255,), width=S2)
    hdr = 40 if label else 12
    d.text((w * S2 / 2, 22 * S2), "TIDE", font=mono(24 * S2), fill=CYAN + (255,), anchor="mm") if label else None
    ty0, ty1 = hdr + 12, h - (46 if label else 16)
    tx0, tx1 = 16, 16 + int(w * 0.34)
    tw, th = tx1 - tx0, ty1 - ty0
    unit_px = th / TUBE_RANGE
    dormant = band == "DORMANT"
    front_y = th if dormant else gap * unit_px     # tube y of the front (the fill is BELOW it); top = the operative (gap 0)
    fill = fill_array(kind, tw, th, front_y, True, seed_off)
    if band == "CAUGHT":
        fill = np.maximum(fill, 0)
    tub = Image.fromarray((np.clip(fill, 0, 1) * 255 + 0.5).astype(np.uint8)).resize((tw * S2, th * S2), Image.BILINEAR)
    img.paste(tub.convert("RGBA"), (tx0 * S2, ty0 * S2))
    d.rectangle([tx0 * S2, ty0 * S2, tx1 * S2, ty1 * S2], outline=CYAN + (255,), width=2 * S2)
    # layer ticks (gap 1, 2, 3) with 45 degree hatch ticks in the dormant tube
    for g in (1, 2, 3):
        y = ty0 + g * unit_px
        d.line([((tx1 + 1) * S2, y * S2), ((tx1 + 9) * S2, y * S2)], fill=CYAN + (255,), width=2 * S2)
        d.line([((tx0 - 7) * S2, y * S2), (tx0 * S2, y * S2)], fill=CYAN + (255,), width=S2)
    if dormant:
        yy = ty0 + 3.4 * unit_px - 2
        wobble_dash = [(tx0 + 3, yy), (tx1 - 3, yy)]
        d.line([(wobble_dash[0][0] * S2, yy * S2), (wobble_dash[1][0] * S2, yy * S2)], fill=CYAN_D + (255,), width=2 * S2)
        for k in range(0, th, 14):                # dotted standby hatch
            d.line([((tx0 + 3) * S2, (ty0 + k) * S2), ((tx1 - 3) * S2, (ty0 + k - 10) * S2)], fill=(20, 60, 90, 255), width=S2)
    # the front mark: a short bar across the tube end + a notch pointing at the lane
    if not dormant:
        fy = ty0 + gap * unit_px
        d.line([((tx0 - 5) * S2, fy * S2), ((tx1 + 5) * S2, fy * S2)], fill=PINK8 + (255,), width=2 * S2)
    # operative marker: lime triangle at the top of the tube, pointing at the tube
    oy = ty0
    d.polygon([((tx0 - 12) * S2, (oy - 7) * S2), ((tx0 - 12) * S2, (oy + 7) * S2), ((tx0 - 2) * S2, oy * S2)], fill=LIME8 + (255,))
    # forecast: red dashed pencil tick at the what-if front
    if forecast_gap is not None:
        fy = ty0 + forecast_gap * unit_px
        wobble_line(d, [(tx0 - 8, fy), (tx1 + 12, fy)], RED8 + (255,), 2.4, dash=(7, 5), seed=3, amp=0.7)
    # band lane: the 4 band glyphs stacked at their zones (CAUGHT block top), current one bracketed
    lane_x = tx1 + 24 + (w - tx1 - 28) / 2 - 8
    zones = [("CAUGHT", 0.0, 0.0), ("CATCHING", 0.0, 1.0), ("CLOSE", 1.0, 2.0), ("CREEPING", 2.0, TUBE_RANGE)]
    for name, g0, g1 in zones:
        cy = ty0 + (g0 + g1) / 2 * unit_px if name != "CAUGHT" else ty0 + 4
        cur = name == band
        col = CYAN if cur else CYAN_D
        if name == "CAUGHT":
            band_glyph(d, lane_x, cy + 6, name, 7, PINK8 if cur else (110, 40, 80), 2)
            continue
        band_glyph(d, lane_x, cy, name, 8, col, 2.4 if cur else 1.6)
        if cur:
            bx0, bx1 = lane_x - 17, lane_x + 17
            by0, by1 = ty0 + g0 * unit_px + 3, ty0 + g1 * unit_px - 3
            for (xa, ya, xb, yb) in ((bx0, by0 + 9, bx0, by0), (bx0, by0, bx0 + 9, by0), (bx1, by0 + 9, bx1, by0), (bx1, by0, bx1 - 9, by0),
                                     (bx0, by1 - 9, bx0, by1), (bx0, by1, bx0 + 9, by1), (bx1, by1 - 9, bx1, by1), (bx1, by1, bx1 - 9, by1)):
                d.line([(xa * S2, ya * S2), (xb * S2, yb * S2)], fill=CYAN + (255,), width=2 * S2)
    if label:
        d.text((w * S2 / 2, (h - 22) * S2), band, font=mono(19 * S2), fill=(PINK8 if band == "CAUGHT" else CYAN) + (255,), anchor="mm")
    img = img.resize((w, h), Image.LANCZOS)
    rgb = scan(img.convert("RGB"), 0.18, 3)
    out = Image.new("RGBA", (w, h))
    out.paste(rgb)
    out.putalpha(img.getchannel("A"))
    return out


def raid_gauge(kind, pct, w=760, h=150, seed_off=0):
    """Raid CRT bar: navy glass, the direction's material filling to `pct`, the CITY LOST cap at 100 %. Returns (RGBA panel, bare Anton %)."""
    S2 = SS
    img = Image.new("RGBA", (w * S2, h * S2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w * S2 - 1, h * S2 - 1], 10 * S2, fill=NAVY + (255,), outline=CYAN + (255,), width=2 * S2)
    d.rounded_rectangle([5 * S2, 5 * S2, (w - 5) * S2, (h - 5) * S2], 7 * S2, outline=CYAN_D + (255,), width=S2)
    d.text((22 * S2, 24 * S2), "TIDE", font=mono(22 * S2), fill=CYAN + (255,), anchor="lm")
    bx0, bx1, by0, by1 = 22, w - 120, 50, h - 24
    bw, bh = bx1 - bx0, by1 - by0
    fx = pct * bw
    fill = fill_array(kind, bw, bh, fx, False, seed_off)
    # fill_array(vertical=False) works on swapped axes: rebuild as (bw x bh) by transposing a (bh x bw)-sized field
    yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)
    wob = 4.0 * (L.fbm(yy * 0.07, np.zeros_like(yy) + 3.0, 5 + seed_off, 3) - 0.5)
    if kind == "C":
        wob = wob + 5.0 * (np.cos((yy / max(bh - 1, 1) - 0.5) * math.pi) ** 2)
    dd = (fx + wob - xx) / GU                       # units behind the front: the fill is LEFT of the front
    glass = np.stack([4 + 6 * xx / bw, 14 + 14 * xx / bw, 30 + 18 * xx / bw], -1).astype(np.float32) / 255.0
    cover = S.SM(-0.15, 0.2, dd)
    c = dict(GP[kind])
    out = S.SKINS[kind](glass, cover, dd, yy / GU, xx / GU, c)
    bar = Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).resize((bw * S2, bh * S2), Image.BILINEAR)
    img.paste(bar.convert("RGBA"), (bx0 * S2, by0 * S2))
    d.rectangle([bx0 * S2, by0 * S2, bx1 * S2, by1 * S2], outline=CYAN + (255,), width=2 * S2)
    for q in (0.25, 0.5, 0.75):
        x = bx0 + q * bw
        d.line([(x * S2, (by1 - 9) * S2), (x * S2, by1 * S2)], fill=CYAN + (255,), width=2 * S2)
        d.line([(x * S2, by0 * S2), (x * S2, (by0 + 9) * S2)], fill=CYAN + (255,), width=2 * S2)
    # CITY LOST cap: a block with an X at the 100 % end (shape, not colour)
    band_glyph(d, bx1 + 22, (by0 + by1) / 2, "CAUGHT", 11, PINK8 + (255,), 2.4)
    d.line([((bx0 + fx) * S2, (by0 - 6) * S2), ((bx0 + fx) * S2, (by1 + 6) * S2)], fill=PINK8 + (255,), width=2 * S2)
    img = img.resize((w, h), Image.LANCZOS)
    rgb = scan(img.convert("RGB"), 0.18, 3)
    panel = Image.new("RGBA", (w, h))
    panel.paste(rgb)
    panel.putalpha(img.getchannel("A"))
    num = Image.new("RGBA", (260, 150), (0, 0, 0, 0))
    nd = ImageDraw.Draw(num)
    txt = "%d%%" % round(pct * 100)
    f = anton(112)
    nd.text((6, 80), txt, font=f, fill=(0, 0, 0, 200), anchor="lm", stroke_width=5, stroke_fill=(0, 0, 0, 200))
    nd.text((6, 80), txt, font=f, fill=(255, 238, 246, 255), anchor="lm")
    return panel, num


def bits_burst(base, cx, cy, k, fade=0.0, seed=3, scale=1.0):
    """Binary-bits burst on an RGB PIL image (in place copy). k 0..1 expansion; fade 0..1 sends it to black."""
    W, H = base.size
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    rnd = np.random.RandomState(seed)
    n = int(380 * min(1.0, k * 1.4))
    for i in range(n):
        ang = rnd.rand() * 2 * math.pi
        rr = (rnd.rand() ** 0.7) * k * max(W, H) * 0.55 * scale
        x, y = cx + math.cos(ang) * rr * 1.25, cy + math.sin(ang) * rr * 0.8
        sz = (10 + rnd.rand() * 26) * scale * (1.0 - 0.45 * k)
        al = int(255 * np.clip(1.0 - (rr / (max(W, H) * 0.6 * scale)) ** 2 * 0.6, 0.25, 1.0))
        ch = "1" if rnd.rand() < 0.5 else "0"
        d.text((x, y), ch, font=mono(sz), fill=PINK8 + (al,), anchor="mm")
        if rnd.rand() < 0.14:          # a streak of bits: damage / transition
            for j in range(1, 5):
                d.text((x - math.cos(ang) * sz * 0.9 * j, y - math.sin(ang) * sz * 0.7 * j), "1" if rnd.rand() < 0.5 else "0", font=mono(sz * 0.8), fill=PINK8 + (int(al * (1 - j / 5.0)),), anchor="mm")
    out = base.convert("RGBA")
    glow = ov.filter(ImageFilter.GaussianBlur(5 * scale))
    out = Image.alpha_composite(out, glow)
    out = Image.alpha_composite(out, ov)
    a = np.asarray(out.convert("RGB"), np.float32) / 255.0
    a = a * (1 - 0.94 * fade)
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))
