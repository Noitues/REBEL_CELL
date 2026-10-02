"""Round 6 wheel assembly in the Screens & Data style.

One function, render(spec), draws any roster wheel: 6 slices x 5 ticks from content data,
a class or corporation bezel, the class inner ring, hub (emblem, name, core), every pointer,
orbit indicators, docked drones, resistance badge, HP arc, and for bosses a heavier bezel,
a nameplate banner and phase pips.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from slicelib import (R_OUT, R_IN, PROGRAMS, CORPS, render_slice, paste_rgba, glyph_mask, glyph_rgba,
                      f_num, f_ui, f_mono, c01)

CW, CH = 1100, 1200
CX, CY = 550, 610
TICK = 12.0
HP_GREEN = (123, 224, 123)

CLASS_STYLE = {
    "breaker": dict(acc=(255, 61, 168), base=(0.11, 0.10, 0.13), kind="plates", emblem="EM_BREAKER"),
    "wrecker": dict(acc=(255, 110, 50), base=(0.13, 0.10, 0.09), kind="welded", emblem="EM_WRECKER"),
    "ghost": dict(acc=(92, 225, 255), base=(0.05, 0.08, 0.10), kind="flicker", emblem="EM_GHOST"),
    "phantom": dict(acc=(150, 130, 255), acc2=(92, 225, 255), base=(0.06, 0.07, 0.11), kind="double", emblem="EM_PHANTOM"),
    "rigger": dict(acc=(123, 224, 123), base=(0.07, 0.09, 0.07), kind="cable", emblem="EM_RIGGER"),
    "overclocker": dict(acc=(255, 176, 60), base=(0.10, 0.09, 0.07), kind="fins", emblem="EM_OVERCLOCKER"),
    "botnet": dict(acc=(176, 140, 255), base=(0.08, 0.07, 0.11), kind="dots", emblem="EM_BOTNET"),
    "hivemind": dict(acc=(200, 90, 255), base=(0.09, 0.06, 0.11), kind="hex", emblem="EM_HIVEMIND"),
}
CORP_EMBLEM = {"meridian": "EM_MERIDIAN", "solace": "EM_SOLACE", "halcyon": "EYE", "orbital": "EM_ORBITAL",
               "rebel_cell": "FIST"}
SEG_GLYPH = {"seg_x2": ("SEG_X2", "x2"), "seg_pierce": ("SEG_PIERCE", "PIERCE"), "seg_echo": ("SEG_ECHO", "ECHO"),
             "seg_corrupt": ("SEG_CORRUPT", "CORRUPT"), "seg_accelerator": ("SEG_ACCEL", "ACCEL"),
             "seg_anchor": ("SEG_ANCHOR", "ANCHOR"), "seg_blank": ("SEG_BLANK", "BLANK")}
SPECIAL_GLYPH = {"tariff": "JUDGEMENT", "citation": "CITATION", "solar_flare": "FLARE", "dose": "DOSE"}
LOD = dict(glyph_scale=1.45, number_scale=1.15, tex_gain=0.55, plate=0.85, skin_gain=0.6)


def P(r, ang, ss):
    a = math.radians(ang)
    return (CX * ss + r * ss * math.sin(a), CY * ss - r * ss * math.cos(a))


# ----------------------------------------------------------------- numpy ring base
def ring_base(canvas, ss, R0, R1, base, acc, alpha=1.0, rim=1.3, brushed=False, seed=0):
    H, W = canvas.shape[:2]
    pad = int((R1 + 12) * ss)
    y0, y1 = max(0, int(CY * ss) - pad), min(H, int(CY * ss) + pad)
    x0, x1 = max(0, int(CX * ss) - pad), min(W, int(CX * ss) + pad)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx, dy = xx + 0.5 - CX * ss, yy + 0.5 - CY * ss
    rho = np.hypot(dx, dy) / ss
    th = np.degrees(np.arctan2(dx, -dy)) % 360
    region = canvas[y0:y1, x0:x1]
    # back plate (visible in the slice gaps)
    bp = np.clip(R_OUT + 3 - rho, 0, 1)[..., None]
    region[..., :3] = region[..., :3] * (1 - bp) + np.array([0.025, 0.022, 0.035]) * bp
    region[..., 3:] = np.maximum(region[..., 3:], bp)
    ring = (np.clip(rho - R0, 0, 1) * np.clip(R1 - rho, 0, 1))[..., None] * alpha
    u = (rho - R0) / max(1.0, (R1 - R0))
    light = 0.8 + 0.35 * np.cos(np.radians(th - 315))
    col = np.array(base, np.float32)[None, None] * (0.7 + 0.6 * np.sin(np.pi * np.clip(u, 0, 1)))[..., None] * light[..., None]
    if brushed:
        rng = np.random.default_rng(seed)
        br = (rng.random(720).astype(np.float32) * 0.07)[(th * 2).astype(np.int32) % 720]
        col = col + br[..., None]
    region[..., :3] = region[..., :3] * (1 - ring) + col * ring
    region[..., 3:] = np.maximum(region[..., 3:], ring)
    a = c01(acc)
    for r, w, k in ((R1 - 1.5, 1.6, rim), (R0 + 1.5, 1.0, rim * 0.55)):
        g = (np.exp(-((rho - r) / w) ** 2) * k)[..., None]
        region[..., :3] = region[..., :3] + g * a
        region[..., 3:] = np.maximum(region[..., 3:], np.clip(g, 0, 1))


# ----------------------------------------------------------------- PIL helpers
def arc_poly(r0, r1, a0, a1, ss, n=24):
    pts = [P(r1, a0 + (a1 - a0) * i / n, ss) for i in range(n + 1)]
    pts += [P(r0, a1 - (a1 - a0) * i / n, ss) for i in range(n + 1)]
    return pts


def glow_layer(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))


def tinted_glyph(name, px, col, outline=(10, 8, 18)):
    g = glyph_rgba(name, px, max(2, px * 0.07))
    arr = np.asarray(g).copy()
    white = (arr[..., 0] > 200) & (arr[..., 1] > 200) & (arr[..., 2] > 200)
    arr[white, 0], arr[white, 1], arr[white, 2] = col
    return Image.fromarray(arr, "RGBA")


# ----------------------------------------------------------------- class ornaments
def class_ornament(d, gd, style, R0, R1, ss, rng, thin=False):
    """Draw a class's bezel identity between radii R0..R1. gd draws into a glow layer."""
    k = style["kind"]
    acc = style["acc"]
    mid = (R0 + R1) / 2
    w = R1 - R0
    if k in ("plates", "welded"):
        n = 12 if not thin else 9
        for i in range(n):
            a = i * 360 / n + 15
            d.line([P(R0 + 2, a, ss), P(R1 - 2, a, ss)], fill=(8, 6, 12, 255), width=int(3 * ss))
            for da in (-7, 7) if not thin else (0,):
                x, y = P(mid, a + 360 / n / 2 + da, ss)
                r = (3.6 if not thin else 2.4) * ss
                d.ellipse([x - r, y - r, x + r, y + r], fill=(120, 115, 130, 255), outline=(20, 18, 26, 255))
                d.ellipse([x - r * 0.45 - r * 0.2, y - r * 0.45 - r * 0.2, x + r * 0.1, y + r * 0.1], fill=(230, 230, 240, 255))
        if k == "welded":
            for i in range(n):
                a = i * 360 / n + 15
                for j in range(int(w / 3)):
                    rr = R0 + 2 + j * 3
                    x, y = P(rr, a + (1.2 if j % 2 else -1.2) * (R_OUT / rr), ss)
                    r = 1.8 * ss
                    gd.ellipse([x - r * 2, y - r * 2, x + r * 2, y + r * 2], fill=acc + (160,))
                    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 210, 150, 255))
            for i in range(6 if not thin else 3):  # dents
                a = rng.random() * 360
                x, y = P(mid, a, ss)
                r = w * 0.35 * ss
                d.ellipse([x - r * 1.6, y - r, x + r * 1.6, y + r], fill=(0, 0, 0, 90))
                d.arc([x - r * 1.6, y - r, x + r * 1.6, y + r], 200, 330, fill=(200, 190, 200, 120), width=max(1, ss))
    elif k in ("flicker", "double"):
        # broken neon dashes of varying brightness, translucent
        for i in range(48 if not thin else 30):
            a0 = i * 360 / (48 if not thin else 30)
            on = rng.random()
            if on < 0.18:
                continue
            al = int(90 + 165 * on)
            pts = [P(R1 - 3, a0 + j * 0.6, ss) for j in range(10)]
            gd.line(pts, fill=acc + (al,), width=int(5 * ss))
            d.line(pts, fill=(230, 250, 255, al), width=int(1.6 * ss))
        if k == "double":
            off = (7 * ss, -5 * ss) if not thin else (4 * ss, -3 * ss)
            acc2 = style["acc2"]
            bb = [CX * ss - (R1 + 4) * ss + off[0], CY * ss - (R1 + 4) * ss + off[1],
                  CX * ss + (R1 + 4) * ss + off[0], CY * ss + (R1 + 4) * ss + off[1]]
            gd.ellipse(bb, outline=acc2 + (150,), width=int(5 * ss))
            d.ellipse(bb, outline=acc2 + (170,), width=int(1.6 * ss))
            bb2 = [bb[0] + off[0], bb[1] + off[1], bb[2] + off[0], bb[3] + off[1]]
            d.ellipse(bb2, outline=acc2 + (70,), width=max(1, int(1.2 * ss)))
    elif k in ("cable", "fins"):
        n = 90 if not thin else 60
        for i in range(n):
            a = i * 360 / n
            d.line([P(R0 + 2, a, ss), P(R1 - 2, a + 360 / n * 0.9, ss)], fill=(30, 40, 30, 255) if k == "cable" else (40, 34, 26, 255), width=int(3.2 * ss))
            d.line([P(R0 + 3, a + 0.4, ss), P(R1 - 3, a + 360 / n * 0.9 + 0.4, ss)], fill=(110, 140, 110, 200) if k == "cable" else (150, 120, 80, 200), width=max(1, int(1 * ss)))
        if not thin:
            for i in range(4):  # cable ties / plugs
                a = 45 + i * 90
                x, y = P(mid, a, ss)
                r = w * 0.55 * ss
                d.rounded_rectangle([x - r * 0.5, y - r * 0.5, x + r * 0.5, y + r * 0.5], radius=3 * ss, fill=(20, 20, 20, 255), outline=acc + (255,), width=int(1.6 * ss))
        if k == "fins":
            nf = 40 if not thin else 24
            L = 18 if not thin else 8
            for i in range(nf):
                a = i * 360 / nf + 4.5
                if not thin and 125 < a < 235:
                    continue  # leave the HP arc clear
                p0, p1 = P(R1 - 2, a - 1.6, ss), P(R1 + L, a - 1.0, ss)
                p2, p3 = P(R1 + L, a + 1.0, ss), P(R1 - 2, a + 1.6, ss)
                d.polygon([p0, p1, p2, p3], fill=(70, 62, 52, 255), outline=(20, 16, 12, 255))
                x, y = P(R1 + L - 2, a, ss)
                gd.ellipse([x - 5 * ss, y - 5 * ss, x + 5 * ss, y + 5 * ss], fill=acc + (190,))
    elif k in ("dots", "hex"):
        n = 24 if not thin else 16
        rr = R1 + (12 if not thin else 4)
        pts = []
        for i in range(n):
            a = i * 360 / n + 7.5
            if not thin and 125 < a < 235:
                continue
            x, y = P(rr, a, ss)
            pts.append((x, y))
            big = (i % 6 == 0)
            r = (6.5 if big else 3.4) * ss if not thin else 2.2 * ss
            gd.ellipse([x - r * 2, y - r * 2, x + r * 2, y + r * 2], fill=acc + (150,))
            d.ellipse([x - r, y - r, x + r, y + r], fill=(240, 230, 255, 255) if big else acc + (255,))
        if k == "hex":
            # hex lattice band on the bezel
            m = 36 if not thin else 24
            for i in range(m):
                a = i * 360 / m
                for row, rad in enumerate((mid - w * 0.2, mid + w * 0.2)):
                    aa = a + (360 / m / 2 if row else 0)
                    x, y = P(rad, aa, ss)
                    hr = (w * 0.26 if not thin else w * 0.3) * ss
                    hexp = [(x + hr * math.cos(math.radians(60 * j)), y + hr * math.sin(math.radians(60 * j))) for j in range(6)]
                    d.polygon(hexp, outline=acc + (230,), width=max(1, int(1.3 * ss)))
            for p0, p1 in zip(pts, pts[1:]):
                d.line([p0, p1], fill=acc + (120,), width=max(1, int(1.2 * ss)))


# ----------------------------------------------------------------- corp ornaments
def corp_ornament(d, gd, corp, R0, R1, ss, rng, boss=False):
    acc = CORPS[corp]["col"]
    mid = (R0 + R1) / 2
    w = R1 - R0
    if corp == "meridian":
        band0, band1 = R0 + w * 0.25, R0 + w * 0.6
        for i in range(120):  # hazard stripes
            a = i * 3
            if i % 2:
                d.polygon([P(band0, a, ss), P(band1, a + 1.5, ss), P(band1, a + 3.0, ss), P(band0, a + 1.5, ss)], fill=(20, 16, 12, 255))
            else:
                d.polygon([P(band0, a, ss), P(band1, a + 1.5, ss), P(band1, a + 3.0, ss), P(band0, a + 1.5, ss)], fill=acc + (255,))
        for i in range(30):  # notched teeth
            a = i * 12
            d.polygon([P(R1 - 1, a - 2.5, ss), P(R1 + 6, a - 1.5, ss), P(R1 + 6, a + 1.5, ss), P(R1 - 1, a + 2.5, ss)], fill=(210, 110, 30, 255), outline=(60, 30, 8, 255))
    elif corp == "solace":
        for i in range(12):  # mint vial capsules
            a = i * 30 + 15
            x, y = P(mid, a, ss)
            L, r = w * 0.9 * ss, w * 0.22 * ss
            cap = Image.new("RGBA", (int(L * 2 + 8), int(L * 2 + 8)), (0, 0, 0, 0))
            dc = ImageDraw.Draw(cap)
            c = cap.width / 2
            dc.rounded_rectangle([c - L / 2, c - r, c + L / 2, c + r], radius=r, fill=(61, 255, 139, 200), outline=(220, 255, 235, 255), width=max(1, ss))
            dc.rectangle([c - 1 * ss, c - r, c + 1 * ss, c + r], fill=(240, 255, 245, 255))
            cap = cap.rotate(-(a + 90), resample=Image.BICUBIC)
            corp_ornament.gimg.alpha_composite(cap.filter(ImageFilter.GaussianBlur(3 * ss)), (int(x - c), int(y - c)))
            corp_ornament.img.alpha_composite(cap, (int(x - c), int(y - c)))
        gd.ellipse([CX * ss - (R1 + 3) * ss, CY * ss - (R1 + 3) * ss, CX * ss + (R1 + 3) * ss, CY * ss + (R1 + 3) * ss], outline=acc + (180,), width=int(5 * ss))
    elif corp == "halcyon":
        for i in range(60):  # colonnade
            a = i * 6
            d.line([P(R0 + 4, a, ss), P(R1 - 6, a, ss)], fill=(185, 175, 255, 255), width=int(2.2 * ss))
        d.ellipse([CX * ss - (R1 - 4) * ss, CY * ss - (R1 - 4) * ss, CX * ss + (R1 - 4) * ss, CY * ss + (R1 - 4) * ss], outline=(230, 225, 255, 255), width=int(2 * ss))
        hr = R1 + 12
        bb = [CX * ss - hr * ss, CY * ss - hr * ss, CX * ss + hr * ss, CY * ss + hr * ss]
        gd.arc(bb, -60 - 90, 60 - 90, fill=acc + (220,), width=int(6 * ss))
        d.arc(bb, -60 - 90, 60 - 90, fill=(225, 220, 255, 255), width=int(2 * ss))
        if boss:
            for i in range(90):
                a = i * 4
                d.line([P(R0 + w * 0.55, a, ss), P(R1 - 2, a, ss)], fill=(255, 210, 120, 220), width=max(1, int(1.2 * ss)))
    elif corp == "orbital":
        fm = f_mono(int(9 * ss))
        for i in range(180):
            a = i * 2
            L = 10 if i % 5 == 0 else 5
            d.line([P(R1 - 3, a, ss), P(R1 - 3 - L, a, ss)], fill=(170, 195, 255, 255), width=max(1, int((1.6 if i % 5 == 0 else 1) * ss)))
        for i in range(12):
            a = i * 30
            x, y = P(R0 + w * 0.32, a, ss)
            s = "%03d" % a
            tw = fm.getlength(s)
            d.text((x - tw / 2, y - 5 * ss), s, font=fm, fill=(200, 215, 255, 255))
    elif corp == "rebel_cell":
        for i in range(24):  # broken, radially offset segments
            a = i * 15
            off = rng.choice([-5, -2, 0, 0, 3, 6])
            d.polygon(arc_poly(R0 + 2 + off, R1 - 2 + off, a + 0.8, a + 14.2, ss, 6), fill=(30, 6, 9, 255), outline=(120, 10, 20, 255))
            if rng.random() < 0.5:
                gd.line([P(R0 + 4, a + 2, ss), P(R0 + 4, a + 11, ss)], fill=(232, 20, 30, 200), width=int(3 * ss))
            x, y = P(mid + off, a + 7.5, ss)
            r = 4 * ss
            hexp = [(x + r * math.cos(math.radians(90 + 60 * j)), y + r * math.sin(math.radians(90 + 60 * j))) for j in range(6)]
            d.polygon(hexp, fill=(232, 20, 30, 255))
        for k in range(5):  # scan bars
            a = rng.random() * 360
            gd.line([P(R0, a, ss), P(R1 + 8, a, ss)], fill=(255, 40, 50, 200), width=int(2 * ss))


# ----------------------------------------------------------------- pieces
def draw_pointer(d, gd, ang, R_piv, ss, acc, ghost=False, label=None):
    tip = R_OUT - 16
    pw = 11
    pts = [P(R_piv - 6, ang - pw * 0.9 / (R_piv / 40), ss), P(R_piv - 6, ang + pw * 0.9 / (R_piv / 40), ss), P(tip, ang, ss)]
    # base width in degrees from px
    half_deg = math.degrees(pw / R_piv)
    pts = [P(R_piv - 4, ang - half_deg, ss), P(R_piv - 4, ang + half_deg, ss), P(tip, ang, ss)]
    if ghost:
        d.polygon(pts, outline=(255, 255, 255, 170), width=int(2 * ss))
        return
    gd.polygon(pts, fill=acc + (220,))
    d.polygon(pts, fill=(245, 245, 250, 255), outline=(10, 8, 16, 255), width=int(2.5 * ss))
    x, y = P(R_piv, ang, ss)
    r = 13 * ss
    d.ellipse([x - r, y - r, x + r, y + r], fill=(60, 60, 72, 255), outline=(10, 8, 16, 255), width=int(2.5 * ss))
    d.ellipse([x - r * 0.5, y - r * 0.55, x - r * 0.05, y - r * 0.1], fill=(210, 210, 220, 255))
    if label:
        f = f_num(int(13 * ss))
        tw = f.getlength(label)
        d.text((x - tw / 2, y - 8 * ss), label, font=f, fill=(255, 255, 255, 255), stroke_width=int(1.5 * ss), stroke_fill=(10, 8, 16, 255))


def draw_orbit(d, gd, ang, n, R, ss, acc):
    a0, a1 = ang + 4, ang + n * TICK
    steps = max(4, int(abs(a1 - a0) / 1.5))
    for i in range(0, steps, 2):
        p0 = P(R, a0 + (a1 - a0) * i / steps, ss)
        p1 = P(R, a0 + (a1 - a0) * (i + 1) / steps, ss)
        gd.line([p0, p1], fill=acc + (200,), width=int(6 * ss))
        d.line([p0, p1], fill=(255, 255, 255, 255), width=int(2.6 * ss))
    # arrowhead
    tip = P(R, a1 + 2.5, ss)
    l = P(R + 7, a1 - 1.5, ss)
    r = P(R - 7, a1 - 1.5, ss)
    d.polygon([tip, l, r], fill=(255, 255, 255, 255))
    f = f_num(int(20 * ss))
    x, y = P(R + 30, (a0 + a1) / 2, ss)
    s = "+%d" % n
    tw = f.getlength(s)
    d.text((x - tw / 2, y - 12 * ss), s, font=f, fill=(255, 255, 255, 255), stroke_width=int(2 * ss), stroke_fill=(10, 8, 16, 255))


def draw_drone(img, d, gd, ang, R, ss, acc, name, hp, theme_col):
    x, y = P(R, ang, ss)
    rx, ry = P(R - 64, ang, ss)
    # tether to the rim
    for i in range(6):
        t0, t1 = i / 6, (i + 0.5) / 6
        d.line([(rx + (x - rx) * t0, ry + (y - ry) * t0), (rx + (x - rx) * t1, ry + (y - ry) * t1)], fill=acc + (230,), width=int(2.4 * ss))
    d.ellipse([rx - 5 * ss, ry - 5 * ss, rx + 5 * ss, ry + 5 * ss], fill=acc + (255,), outline=(10, 8, 16, 255))
    r = 46 * ss
    gd.ellipse([x - r - 4 * ss, y - r - 4 * ss, x + r + 4 * ss, y + r + 4 * ss], fill=acc + (120,))
    d.ellipse([x - r, y - r, x + r, y + r], fill=(26, 26, 32, 255), outline=acc + (255,), width=int(3 * ss))
    r2 = r - 7 * ss
    d.ellipse([x - r2, y - r2, x + r2, y + r2], fill=tuple(int(v * 0.16) for v in theme_col) + (255,), outline=(10, 8, 16, 255), width=max(1, ss))
    for k in range(-int(r2), int(r2), int(3 * ss)):
        hw = math.sqrt(max(0, r2 * r2 - k * k))
        d.line([(x - hw, y + k), (x + hw, y + k)], fill=(0, 0, 0, 60), width=max(1, ss // 2))
    g = glyph_rgba("DRONE", int(50 * ss), 3 * ss)
    img.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2 - 2 * ss)))
    # HP pill + name
    f = f_num(int(19 * ss))
    s = "%d" % hp
    tw = f.getlength(s)
    py = y + r - 6 * ss
    d.rounded_rectangle([x - tw / 2 - 10 * ss, py, x + tw / 2 + 10 * ss, py + 24 * ss], radius=8 * ss, fill=(10, 30, 14, 255), outline=HP_GREEN + (255,), width=max(1, int(1.6 * ss)))
    d.text((x - tw / 2, py + 1 * ss), s, font=f, fill=HP_GREEN + (255,))
    fn = f_ui(int(17 * ss), b"Bold SemiCondensed")
    tw = fn.getlength(name.upper())
    d.text((x - tw / 2, y - r - 24 * ss), name.upper(), font=fn, fill=(235, 235, 245, 255), stroke_width=int(1.5 * ss), stroke_fill=(10, 8, 16, 255))


def draw_res_badge(img, d, gd, ss, value, hub_r, label="RES", lock=False, acc=(255, 210, 90)):
    x, y = P(hub_r + 6, 42, ss)
    r = 25 * ss
    hexp = [(x + r * math.cos(math.radians(30 + 60 * j)), y + r * math.sin(math.radians(30 + 60 * j))) for j in range(6)]
    gd.polygon(hexp, fill=acc + (160,))
    d.polygon(hexp, fill=(20, 16, 10, 255), outline=acc + (255,), width=int(2.6 * ss))
    f = f_num(int(24 * ss))
    s = "R%d" % value
    tw = f.getlength(s)
    d.text((x - tw / 2, y - 15 * ss), s, font=f, fill=(255, 245, 220, 255))
    fs = f_ui(int(10 * ss), b"Bold Condensed")
    lab = ("HUB LOCK" if lock else label)
    tw = fs.getlength(lab)
    d.rounded_rectangle([x - tw / 2 - 4 * ss, y + r - 4 * ss, x + tw / 2 + 4 * ss, y + r + 11 * ss], radius=3 * ss, fill=acc + (255,))
    d.text((x - tw / 2, y + r - 3 * ss), lab, font=fs, fill=(20, 16, 10, 255))


def draw_inner_ring(img, d, gd, segs, ss, acc, style):
    r0, r1 = 101, 127
    for i, sid in enumerate(segs):
        a0 = i * 120 - 60 + 1.5
        a1 = a0 + 117
        d.polygon(arc_poly(r0, r1, a0, a1, ss, 40), fill=(14, 13, 20, 255), outline=(6, 5, 9, 255))
        d.polygon(arc_poly(r0 + 3, r1 - 3, a0 + 1.2, a1 - 1.2, ss, 40), fill=tuple(int(v * 0.12) for v in acc) + (255,))
        for k in range(int(r0 + 4), int(r1 - 3), 3):  # scanlines
            bb = [CX * ss - k * ss, CY * ss - k * ss, CX * ss + k * ss, CY * ss + k * ss]
            d.arc(bb, a0 - 90 + 1.5, a1 - 90 - 1.5, fill=(0, 0, 0, 70), width=max(1, ss // 2))
        bbo = [CX * ss - (r1 - 3) * ss, CY * ss - (r1 - 3) * ss, CX * ss + (r1 - 3) * ss, CY * ss + (r1 - 3) * ss]
        gd.arc(bbo, a0 - 90 + 1, a1 - 90 - 1, fill=acc + (200,), width=int(3 * ss))
        d.arc(bbo, a0 - 90 + 1, a1 - 90 - 1, fill=acc + (255,), width=max(1, int(1.3 * ss)))
        gname, lab = SEG_GLYPH.get(sid, ("SEG_BLANK", sid))
        mid = (a0 + a1) / 2
        g = glyph_rgba(gname, int(19 * ss), 2 * ss)
        fs = f_ui(int(12 * ss), b"Bold Condensed")
        tw = fs.getlength(lab)
        blk = Image.new("RGBA", (int(g.width + tw + 6 * ss), int(max(g.height, 18 * ss))), (0, 0, 0, 0))
        blk.alpha_composite(g, (0, (blk.height - g.height) // 2))
        ImageDraw.Draw(blk).text((g.width + 3 * ss, blk.height / 2 - 8 * ss), lab, font=fs, fill=(255, 255, 255, 255),
                                 stroke_width=int(1.2 * ss), stroke_fill=(10, 8, 16, 255))
        rot = -mid if not (90 < mid % 360 < 270) else -(mid + 180)
        blk = blk.rotate(rot, resample=Image.BICUBIC, expand=True)
        x, y = P((r0 + r1) / 2, mid, ss)
        img.alpha_composite(blk, (int(x - blk.width / 2), int(y - blk.height / 2)))
    if style:
        class_ornament(d, gd, style, r0 - 4, r0, ss, np.random.default_rng(3), thin=True)


def draw_hub(img, d, gd, ss, hub_r, acc, emblem, name, sub, fill=(14, 12, 20)):
    c = (CX * ss, CY * ss)
    R = hub_r * ss
    d.ellipse([c[0] - R, c[1] - R, c[0] + R, c[1] + R], fill=fill + (255,), outline=acc + (255,), width=int(2.5 * ss))
    for rr in range(16, int(hub_r) - 6, 9):
        d.ellipse([c[0] - rr * ss, c[1] - rr * ss, c[0] + rr * ss, c[1] + rr * ss], outline=(255, 255, 255, 10), width=ss)
    if emblem:
        es = 40 if hub_r < 110 else 50
        g = tinted_glyph(emblem, int(es * ss), acc)
        img.alpha_composite(g, (int(c[0] - g.width / 2), int(c[1] - hub_r * 0.62 * ss - g.height / 2)))
    words = name.upper().split()
    lines = []
    cur = ""
    maxc = 10 if hub_r < 110 else 12
    for wd in words:
        if cur and len(cur) + 1 + len(wd) > maxc:
            lines.append(cur)
            cur = wd
        else:
            cur = (cur + " " + wd).strip()
    lines.append(cur)
    fs = 27 if len(lines) == 1 else 23
    if max(len(l) for l in lines) > 11:
        fs -= 4
    fb = f_num(int(fs * ss))
    y = c[1] - (8 if len(lines) == 1 else 20) * ss
    for ln in lines:
        w = fb.getlength(ln)
        d.text((c[0] - w / 2, y), ln, font=fb, fill=(255, 255, 255, 255), stroke_width=int(1.5 * ss), stroke_fill=(10, 8, 16, 255))
        y += (fs + 1) * ss
    fsub = f_ui(int(11 * ss))
    w = fsub.getlength(sub)
    d.text((c[0] - w / 2, y + 5 * ss), sub, font=fsub, fill=(205, 205, 215, 255))


def draw_hp(d, gd, ss, R, hp, hpmax, phases=None, active_phase=1):
    n = 30
    a0, a1 = 130, 230
    r0, r1 = R + 16, R + 40
    for i in range(n):
        aa = a0 + (a1 - a0) * (i + 0.12) / n
        ab = a0 + (a1 - a0) * (i + 0.88) / n
        on = i < round(n * hp / hpmax)
        col = HP_GREEN if on else (38, 58, 42)
        d.polygon(arc_poly(r0, r1, aa, ab, ss, 3), fill=col + (255,))
        if on:
            gd.polygon(arc_poly(r0, r1, aa, ab, ss, 3), fill=HP_GREEN + (110,))
    if phases:
        for k, frac in enumerate(phases):
            a = a0 + (a1 - a0) * frac
            x, y = P(r1 + 13, a, ss)
            r = 9 * ss
            on = (k + 2) <= active_phase
            col = (255, 210, 90) if on else (120, 110, 90)
            d.line([P(r0 - 4, a, ss), P(r1 + 4, a, ss)], fill=(255, 220, 120, 255), width=int(3 * ss))
            d.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=col + (255,), outline=(10, 8, 16, 255))
            if on:
                gd.ellipse([x - r * 2, y - r * 2, x + r * 2, y + r * 2], fill=(255, 210, 90, 160))
            f = f_num(int(15 * ss))
            s = "P%d" % (k + 2)
            xx, yy = P(r1 + 32, a, ss)
            tw = f.getlength(s)
            d.text((xx - tw / 2, yy - 9 * ss), s, font=f, fill=col + (255,), stroke_width=int(1.5 * ss), stroke_fill=(10, 8, 16, 255))
    txt = "%d/%d" % (hp, hpmax)
    f = f_num(int(60 * ss))
    w = f.getlength(txt)
    d.text((CX * ss - w / 2, (CY + R + 44) * ss), txt, font=f, fill=HP_GREEN + (255,), stroke_width=int(2 * ss), stroke_fill=(8, 20, 10, 255))


def draw_banner(img, d, gd, ss, R, title, sub, acc):
    f = f_num(int(46 * ss))
    fs = f_ui(int(15 * ss), b"Bold SemiCondensed")
    tw = max(f.getlength(title), fs.getlength(sub)) + 70 * ss
    y1 = (CY - R - 34) * ss
    y0 = y1 - 82 * ss
    x0, x1 = CX * ss - tw / 2, CX * ss + tw / 2
    poly = [(x0 - 18 * ss, y0), (x1 + 18 * ss, y0), (x1, y1), (x0, y1)]
    gd.polygon(poly, fill=acc + (150,))
    d.polygon(poly, fill=(14, 12, 18, 255), outline=acc + (255,), width=int(3 * ss))
    d.line([(x0 + 10 * ss, y1 - 8 * ss), (x1 - 10 * ss, y1 - 8 * ss)], fill=acc + (255,), width=int(2 * ss))
    w = f.getlength(title)
    d.text((CX * ss - w / 2, y0 + 6 * ss), title, font=f, fill=(255, 255, 255, 255), stroke_width=int(2 * ss), stroke_fill=(10, 8, 16, 255))
    w = fs.getlength(sub)
    d.text((CX * ss - w / 2, y0 + 56 * ss), sub, font=fs, fill=acc + (255,))
    # chain down to the bezel
    for sx in (-1, 1):
        xa = CX * ss + sx * tw * 0.3
        for k in range(4):
            yy = y1 + k * 7 * ss
            d.ellipse([xa - 3 * ss, yy, xa + 3 * ss, yy + 6 * ss], outline=(140, 140, 150, 255), width=max(1, ss))


# ----------------------------------------------------------------- main
def render(spec, ss=2, lod=False):
    """spec keys: theme ('player' or corp id), slots [dict(program,value,glyph,badge,special)],
    pointers [ticks], orbit, resistance, lock, hub dict(name, sub, emblem), ring [seg ids],
    cls (class id for player bezel), drones [dict(name,hp)], hp (cur,max), boss dict or None."""
    theme = spec["theme"]
    boss = spec.get("boss")
    rng = np.random.default_rng(spec.get("seed", 1))
    canvas = np.zeros((CH * ss, CW * ss, 4), np.float32)
    if theme == "player":
        st = CLASS_STYLE[spec["cls"]]
        acc = st["acc"]
        R1 = R_OUT + 40
        ring_base(canvas, ss, R_OUT + 1, R1, st["base"], acc, alpha=0.62 if st["kind"] in ("flicker", "double") else 1.0)
    else:
        st = None
        acc = CORPS[theme]["col"]
        R1 = R_OUT + (58 if boss else 40)
        ring_base(canvas, ss, R_OUT + 1, R1, CORPS[theme]["bezel"] if theme != "solace" else (0.62, 0.66, 0.64), acc,
                  brushed=theme in ("meridian", "orbital"), seed=spec.get("seed", 1))
        if boss:
            ring_base(canvas, ss, R1 - 16, R1, tuple(min(1, v * 1.4) for v in CORPS[theme]["bezel"]), acc, rim=1.6)
    opts = dict(LOD) if lod else {}
    if boss:
        opts.update(boss=True, phase=boss.get("phase", 1))
    a = -30.0
    for i, sl in enumerate(spec["slots"]):
        val = sl["value"]
        if val in (0,) and sl["program"] == "NULL":
            val = None
        if sl.get("special") and sl["special"] != "tariff":
            val = None
        render_slice(canvas, CX * ss, CY * ss, sl["program"], a, 60, val, (0.3 + i * 0.137) % 1.0, theme, ss,
                     opts, seed=i + spec.get("seed", 1) * 7, glyph=SPECIAL_GLYPH.get(sl.get("special")),
                     badge=sl.get("badge"), special=sl.get("special"))
        a += 60
    over = Image.new("RGBA", (CW * ss, CH * ss), (0, 0, 0, 0))
    glow = Image.new("RGBA", (CW * ss, CH * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    gd = ImageDraw.Draw(glow)
    # bezel identity
    if theme == "player":
        class_ornament(d, gd, st, R_OUT + 1, R1, ss, rng)
    else:
        corp_ornament.img, corp_ornament.gimg = over, glow
        corp_ornament(d, gd, theme, R_OUT + 1, R1 - (16 if boss else 0), ss, rng, boss=bool(boss))
        if boss:  # crown studs on the heavy outer band
            for i in range(36):
                x, y = P(R1 - 8, i * 10 + 5, ss)
                r = 3.4 * ss
                d.ellipse([x - r, y - r, x + r, y + r], fill=(235, 230, 220, 255), outline=(10, 8, 16, 255))
    # inner ring + hub
    if spec.get("ring"):
        draw_inner_ring(over, d, gd, spec["ring"], ss, acc, st)
        hub_r = 96
    else:
        hub_r = 126
    hub = spec["hub"]
    draw_hub(over, d, gd, ss, hub_r, acc, hub.get("emblem"), hub["name"], hub.get("sub", ""),
             fill=(14, 12, 20) if theme != "solace" else (16, 26, 24))
    if spec.get("resistance"):
        draw_res_badge(over, d, gd, ss, spec["resistance"], hub_r, lock=spec.get("lock", False))
    # pointers (+ orbit)
    R_piv = R_OUT + (44 if boss else 30)
    ptrs = spec.get("pointers", [0])
    for k, tk in enumerate(ptrs):
        ang = tk * TICK
        if spec.get("orbit"):
            draw_orbit(d, gd, ang, spec["orbit"], R_OUT + 18, ss, acc)
            draw_pointer(d, gd, ang + spec["orbit"] * TICK, R_piv, ss, acc, ghost=True)
        draw_pointer(d, gd, ang, R_piv, ss, acc, label=str(k + 1) if len(ptrs) > 1 else None)
    # drones
    cand = [-58, 58, -100, 100, -28, 28]
    used = [p * TICK for p in ptrs]
    angs = [c for c in cand if all(abs(((c - u + 180) % 360) - 180) > 18 for u in used)]
    for k, dr in enumerate(spec.get("drones", [])):
        draw_drone(over, d, gd, angs[k % len(angs)], R1 + 104, ss, acc, dr["name"], dr["hp"],
                   CORPS[theme]["col"] if theme in CORPS else acc)
    # HP + boss dress
    hp = spec.get("hp")
    if hp:
        draw_hp(d, gd, ss, R1, hp[0], hp[1], phases=boss.get("pips") if boss else None,
                active_phase=boss.get("phase", 1) if boss else 1)
    if boss:
        draw_banner(over, d, gd, ss, R1, boss["title"], boss["sub"], acc)
    glow = glow.filter(ImageFilter.GaussianBlur(7 * ss))
    g = np.asarray(glow, np.float32) / 255
    o = np.asarray(over, np.float32) / 255
    canvas[..., :3] = canvas[..., :3] + g[..., :3] * g[..., 3:] * 0.9
    canvas[..., 3:] = np.maximum(canvas[..., 3:], g[..., 3:] * 0.9)
    oa = o[..., 3:]
    canvas[..., :3] = canvas[..., :3] * (1 - oa) + o[..., :3] * oa
    canvas[..., 3:] = canvas[..., 3:] * (1 - oa) + oa
    im = Image.fromarray((np.clip(canvas, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")
    return im.resize((CW, CH), Image.LANCZOS)
