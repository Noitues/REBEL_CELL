"""Round 21 UI additions: grease-pencil path rules (scribble-through, erase, tracking), the card drag model (parked
sticker + pencil targeting arrow), FROZEN frost (the slice FROZEN overlay language in screen space), the binary-bit
explosion, the decrypted / encrypted holo intel with the Halcyon corp symbol, the corporate after-action report and a
saturation-preserving gif writer.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as LY  # noqa: E402
import ui19 as U  # noqa: E402
import ui20 as V  # noqa: E402
from ui20 import T, SL, F, S, P, Frame  # noqa: E402,F401
from ui20 import PINK, CYAN, GREEN, VIOLET, AMBER, LIME, HARM, HALCYON, PAPER, INKC, ICE, Y_PEN, R_PEN  # noqa: E402,F401

HP_COLS = ((212, 255, 0), (255, 196, 40), (255, 128, 112))   # health float: high / mid / low (low brightened)


def hp_col(frac):
    return HP_COLS[0] if frac > 0.66 else HP_COLS[1] if frac > 0.33 else HP_COLS[2]


# ------------------------------------------------------------------ grease pencil v2
class Pencil(V.Pencil):
    def text(self, s, x, y, cap, col=R_PEN, w=4.4, progress=1.0, angle=-0.03, tracking=0.45):
        self.strokes(T.letter_strokes(s, x, y, cap, w, col, self.rng, angle=angle, tracking=tracking), progress)

    def bold_text(self, s, x, y, cap, col=R_PEN, w=8.5, progress=1.0, angle=-0.04, tracking=0.38):
        """Two overlapping passes, heavier wax: a word that has to shout (BREACHED)."""
        st1 = T.letter_strokes(s, x, y, cap, w, col, self.rng, angle=angle, tracking=tracking)
        st2 = T.letter_strokes(s, x + 2.5, y + 2, cap, w * 0.75, col, self.rng, angle=angle, tracking=tracking)
        self.strokes(st1 + st2, progress)

    def scribble(self, pts, col=R_PEN, w=4.0, progress=1.0, amp=11.0, pitch=9.0):
        """Scribble THROUGH a path (the part a what-if would remove): a tight zigzag across it."""
        p = T.resample(np.array(pts, float), 2)
        L = T.path_len(p)
        n = max(2, int(L / pitch))
        out = []
        d = np.sqrt(((p[1:] - p[:-1]) ** 2).sum(1))
        cs = np.concatenate([[0], np.cumsum(d)])
        for i in range(n + 1):
            s = L * i / n
            k = min(len(p) - 2, int(np.searchsorted(cs, s) - 1) if s > 0 else 0)
            k = max(0, k)
            t = (s - cs[k]) / max(1e-6, d[k])
            q = p[k] + (p[k + 1] - p[k]) * t
            tv = (p[k + 1] - p[k]) / max(1e-6, d[k])
            nv = np.array([-tv[1], tv[0]])
            sgn = 1 if i % 2 == 0 else -1
            out.append(q + nv * amp * sgn * self.rng.uniform(0.75, 1.1) + tv * self.rng.normal(0, 1.5))
        self.strokes([(np.array(out), w, col)], progress)


def cursor(fr, x, y, kind="arrow"):
    """The OS-level pointer (plain white arrow with a dark rim)."""
    lay = Image.new("RGBA", (fr.w, fr.h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    X, Y = x - fr.ox, y - fr.oy
    pts = [(X, Y), (X, Y + 26), (X + 7, Y + 19), (X + 12, Y + 30), (X + 17, Y + 28), (X + 12, Y + 17), (X + 21, Y + 17)]
    d.polygon(pts, fill=(250, 250, 250, 255), outline=(10, 10, 14, 255))
    a = np.asarray(lay, np.float32) / 255
    fr.img = fr.img * (1 - a[..., 3:4]) + a[..., :3] * a[..., 3:4]
    return fr


def parking(fr, x, y, w=180, h=210, label="PARKED"):
    """The sticker parking area: a dashed die-cut outline printed on the screen (a slot the card sits in)."""
    lay = Image.new("RGBA", (fr.w, fr.h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    X0, Y0 = x - w / 2 - fr.ox, y - h / 2 - fr.oy
    k = 0
    per = [(X0 + t, Y0) for t in range(0, w, 12)] + [(X0 + w, Y0 + t) for t in range(0, h, 12)] + \
          [(X0 + w - t, Y0 + h) for t in range(0, w, 12)] + [(X0, Y0 + h - t) for t in range(0, h, 12)]
    for i in range(0, len(per) - 1, 2):
        d.line([per[i], per[i + 1]], fill=(230, 236, 245, 170), width=2)
    d.text((X0 + w / 2, Y0 - 12), label, font=F(SL.MONO, 12), fill=(200, 210, 225, 220), anchor="mm")
    a = np.asarray(lay, np.float32) / 255
    fr.img = fr.img * (1 - a[..., 3:4]) + a[..., :3] * a[..., 3:4]
    return fr


def target_arrow(pen, start, end, state="free", progress=1.0, node_xy=None):
    """Pencil targeting from the parked card to the cursor; near a node it resolves into a yellow CIRCLE (valid)
    or a red X (invalid)."""
    sx, sy = start
    ex, ey = end
    mx, my = (sx + ex) / 2 + (ey - sy) * 0.18, (sy + ey) / 2 - (ex - sx) * 0.18
    path = T.bezier((sx, sy), (mx, my), (ex, ey), 40)
    if state == "valid":
        pen.arrow(path[:-6], Y_PEN, 6.5, 18, progress=progress)
        nx, ny = node_xy
        pen.circle(nx, ny, 76, 50, Y_PEN, 7.0, turns=1.2, progress=progress)
    elif state == "invalid":
        pen.line(path[:-6], R_PEN, 6.0, progress=progress)
        nx, ny = node_xy
        pen.x(nx, ny, 30, R_PEN, 8.0, progress=progress)
    else:
        pen.arrow(path, Y_PEN, 6.5, 18, progress=progress)


# ------------------------------------------------------------------ FROZEN (slice overlay language, screen space)
def _fbm(h, w, scale, seed, octaves=3):
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        cell = max(2, int(scale / (2 ** o)))
        out += _noise(h, w, cell, seed + o) * amp
        tot += amp
        amp *= 0.5
    return out / tot


def _noise(h, w, cell, seed):
    rng = np.random.default_rng(seed)
    n = rng.random((h // cell + 2, w // cell + 2)).astype(np.float32)
    im = Image.fromarray((n * 255).astype(np.uint8)).resize(((w // cell + 2) * cell, (h // cell + 2) * cell), Image.BICUBIC)
    return np.asarray(im, np.float32)[:h, :w] / 255.0


def frost(fr, mask, t=0.0, seed=3, k=1.0):
    """Ice crust over `mask` (float HxW in the Frame): cold tint, crust grown from the mask edge, crystal ridges at the
    crust front, white crack lines, twinkling glints. Same recipe as the slice FROZEN overlay."""
    h, w = mask.shape
    if mask.max() <= 0:
        return fr
    m = np.clip(mask, 0, 1) * k
    img = fr.img
    cold = img * np.array([0.62, 0.80, 1.0], np.float32) + np.array([0.06, 0.12, 0.2], np.float32)
    img = img * (1 - m[..., None] * 0.85) + cold * m[..., None] * 0.85
    inner = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
    edge = np.clip(m - inner * 0.8, 0, 1)
    n = _fbm(h, w, 24, seed)
    crust = np.clip((n * 0.8 + edge * 1.2 + m * 0.25 - 0.78) * 5, 0, 1) * m
    img = img * (1 - crust[..., None] * 0.85) + np.array([0.82, 0.93, 1.0], np.float32) * crust[..., None] * 0.85
    r2 = 1 - np.abs(2 * _fbm(h, w, 10, seed + 9) - 1)
    front = np.exp(-((n * 0.8 + edge * 1.2 + m * 0.25 - 0.74) / 0.07) ** 2)
    ridge = np.clip((r2 - 0.84) * 9, 0, 1) * front * m
    img = img + np.array([0.9, 0.97, 1.0], np.float32) * ridge[..., None] * 0.9
    lay = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(seed + 77)
    ys, xs = np.nonzero(m > 0.5)
    if len(xs):
        for _ in range(5):
            i = rng.integers(0, len(xs))
            x, y = float(xs[i]), float(ys[i])
            pts = [(x, y)]
            for s in range(7):
                x += rng.normal(0, 9)
                y += rng.normal(0, 9)
                pts.append((x, y))
            d.line(pts, fill=210, width=1)
        for g in range(8):
            i = rng.integers(0, len(xs))
            ph = rng.random()
            a = max(0.0, math.sin(2 * math.pi * (t * 2 + ph)))
            if a < 0.25:
                continue
            x, y = float(xs[i]), float(ys[i])
            L = 3 + 7 * a
            d.line([(x - L, y), (x + L, y)], fill=int(255 * a), width=1)
            d.line([(x, y - L), (x, y + L)], fill=int(255 * a), width=1)
    cr = np.asarray(lay, np.float32)[..., None] / 255 * m[..., None]
    fr.img = img * (1 - cr) + cr * np.array([0.95, 0.99, 1.0], np.float32)
    return fr


def poly_mask(fr, pts, feather=3):
    lay = Image.new("L", (fr.w, fr.h), 0)
    ImageDraw.Draw(lay).polygon([(x - fr.ox, y - fr.oy) for x, y in pts], fill=255)
    if feather:
        lay = lay.filter(ImageFilter.GaussianBlur(feather))
    return np.asarray(lay, np.float32) / 255


def link_mask(fr, a, b, amount=1.0, half=6.5, trim=10.5):
    """Screen mask of link a-b along its street polyline (round 40), from a, trimmed, cut at `amount`."""
    pts = [np.array(q, float) for q in LY.link_points(a, b)]
    segl = [float(np.linalg.norm(q1 - q0)) for q0, q1 in zip(pts, pts[1:])]
    L = sum(segl)
    s0, s1 = trim, trim + (L - 2 * trim) * amount
    lay = Image.new("L", (fr.w, fr.h), 0)
    d_ = ImageDraw.Draw(lay)
    acc = 0.0
    for (q0, q1), ls in zip(zip(pts, pts[1:]), segl):
        a0, a1 = max(s0, acc), min(s1, acc + ls)
        if a1 > a0 and ls > 1e-6:
            dv = (q1 - q0) / ls
            nv = np.array([-dv[1], dv[0]])
            p0, p1 = q0 + dv * (a0 - acc), q0 + dv * (a1 - acc)
            poly = [p0 + nv * half, p1 + nv * half, p1 - nv * half, p0 - nv * half]
            d_.polygon([(P(*v)[0] - fr.ox, P(*v)[1] - fr.oy) for v in poly], fill=255)
        acc += ls
    return np.asarray(lay.filter(ImageFilter.GaussianBlur(3)), np.float32) / 255.0


def ellipse_mask(fr, x, y, rx, ry):
    lay = Image.new("L", (fr.w, fr.h), 0)
    ImageDraw.Draw(lay).ellipse([x - rx - fr.ox, y - ry - fr.oy, x + rx - fr.ox, y + ry - fr.oy], fill=255)
    return np.asarray(lay.filter(ImageFilter.GaussianBlur(4)), np.float32) / 255


# ------------------------------------------------------------------ binary-bit explosion (home hit)
def bit_burst(fr, x, y, t, seed=9, n=140, col=(255, 70, 160), radius=150):
    """0/1 bits blasting out of a point: flash, shock ring, bits flying + falling and fading."""
    rng = np.random.default_rng(seed)
    lay = Image.new("RGBA", (fr.w, fr.h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    X, Y = x - fr.ox, y - fr.oy
    if t < 0.25:
        r = 20 + 220 * t
        a = int(255 * (1 - t / 0.25))
        d.ellipse([X - r, Y - r * 0.6, X + r, Y + r * 0.6], outline=(255, 230, 245, a), width=4)
        fl = int(200 * (1 - t / 0.25))
        d.ellipse([X - 40, Y - 26, X + 40, Y + 26], fill=(255, 240, 250, fl))
    for i in range(n):
        ang = rng.uniform(0, 2 * math.pi)
        sp = rng.uniform(0.3, 1.0) * radius
        rr = sp * (1 - (1 - min(1.0, t * 1.6)) ** 2)
        px = X + math.cos(ang) * rr
        py = Y + math.sin(ang) * rr * 0.6 - 40 * math.sin(math.pi * min(1, t * 1.6)) * rng.uniform(0.3, 1) + 60 * t * t
        a = int(255 * max(0.0, 1 - t * 1.1) * rng.uniform(0.6, 1.0))
        if a <= 0:
            continue
        size = int(rng.uniform(11, 22))
        c = col if rng.random() < 0.6 else (255, 240, 250)
        d.text((px, py), rng.choice(["0", "1"]), font=F(SL.MONO, size), fill=c + (a,), anchor="mm")
    return V._add(fr, lay, 1.0)


# ------------------------------------------------------------------ gifs: keep the saturation
def save_gif(frames, path, dur=90, max_kb=1950):
    """One shared palette built from a spread of frames (so no frame's colours get dropped), 255 colours,
    Floyd-Steinberg dither; falls back to fewer colours / no dither to fit the size cap."""
    k = len(frames)
    pick = [frames[i] for i in sorted(set([0, k // 4, k // 2, 3 * k // 4, k - 1]))]
    w, h = frames[0].size
    mont = Image.new("RGB", (w, h * len(pick)))
    for i, f in enumerate(pick):
        mont.paste(f.convert("RGB"), (0, i * h))
    for colors, dith in ((255, Image.Dither.FLOYDSTEINBERG), (192, Image.Dither.FLOYDSTEINBERG), (160, Image.Dither.NONE),
                         (96, Image.Dither.NONE), (64, Image.Dither.NONE)):
        pal = mont.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, kmeans=2)
        q = [f.convert("RGB").quantize(palette=pal, dither=dith) for f in frames]
        q[0].save(path, save_all=True, append_images=q[1:], duration=dur, loop=0, optimize=True, disposal=1)
        kb = os.path.getsize(path) // 1024
        if kb <= max_kb:
            return kb, colors
    return kb, colors


# ------------------------------------------------------------------ corp symbol + intel holo (decrypted / encrypted)
def halcyon_symbol(size=120, col=(170, 150, 255)):
    """Halcyon Civic mark: a tiered civic pyramid under a halo ring."""
    s = size * S
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = col + (255,)
    w = max(2, int(s * 0.035))
    d.ellipse([s * 0.18, s * 0.06, s * 0.82, s * 0.30], outline=c, width=w)
    for i in range(4):
        y0 = s * (0.38 + i * 0.13)
        half = s * (0.14 + i * 0.09)
        d.rectangle([s / 2 - half, y0, s / 2 + half, y0 + s * 0.10], outline=c, width=w)
    d.line([(s * 0.5, s * 0.30), (s * 0.5, s * 0.38)], fill=c, width=w)
    return im


def seal_overlay(img_rgba, cracked=True, stamp="DECRYPTED", stamp_col=(120, 255, 140)):
    """Crack the corp symbol (red fracture, offset halves) and slap a stamp across it."""
    w, h = img_rgba.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if cracked:
        left = img_rgba.crop((0, 0, w // 2 + 2, h))
        right = img_rgba.crop((w // 2 - 2, 0, w, h))
        out.alpha_composite(left, (-3, 2))
        out.alpha_composite(right, (w // 2 + 1, -2))
        d = ImageDraw.Draw(out)
        pts = [(w * 0.52, 0), (w * 0.46, h * 0.3), (w * 0.56, h * 0.55), (w * 0.47, h * 0.8), (w * 0.53, h)]
        d.line(pts, fill=(255, 68, 51, 255), width=max(2, w // 50))
    else:
        out.alpha_composite(img_rgba)
    if stamp:
        st = Image.new("RGBA", (w, h // 3), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        sd.rectangle([2, 2, w - 3, h // 3 - 3], outline=stamp_col + (235,), width=max(2, w // 45))
        fs = int(h * 0.22)
        while fs > 6 and F(SL.ANTON, fs).getlength(stamp) > w * 0.9:
            fs -= 1
        sd.text((w / 2, h / 6), stamp, font=F(SL.ANTON, fs), fill=stamp_col + (235,), anchor="mm")
        st = st.rotate(-14, expand=True, resample=Image.BICUBIC)
        out.alpha_composite(st, ((w - st.size[0]) // 2, (h - st.size[1]) // 2 + h // 8))
    return out


def garble(text, rng):
    pool = "#%&@$*!?/\\<>=+~^:;0123456789ABCDEFX"
    return "".join(c if c == " " else pool[rng.integers(0, len(pool))] for c in text)


def intel_holo(rows, w=330, col=(170, 150, 255), decrypted=True, seed=4):
    """Threat intel as a projected surveillance readout with the corp symbol.
    decrypted=True: readable rows, scanned silhouettes, the Halcyon mark cracked + DECRYPTED stamp.
    decrypted=False: rows garbled, a lock, ENCRYPTED stamp - what the Cell gets when the decrypt fails
    (proposal: a Heat consequence, e.g. at HEAT 75+ corp traffic is too hardened to crack)."""
    rng = np.random.default_rng(seed)
    if not decrypted:
        rows = [(r[0],) + tuple(garble(v, rng) if isinstance(v, str) and i > 0 and r[0] in ("t", "route") else v
                                 for i, v in enumerate(r[1:], 1)) for r in rows]
        rows = [r if r[0] != "route" else ("route", "?", r[2], r[3]) for r in rows]
    head = [("t", " ", (0, 0, 0))] * 4
    pn = V.intel_holo(head + rows, w=w, col=col) if decrypted else U.holo("THREAT INTEL // SCAN", head + rows + [("sep",), ("t", " ", (0, 0, 0)),
                                                                                                 ("t", " ", (0, 0, 0)), ("t", " ", (0, 0, 0))], w=w, col=col)
    im = pn["img"].copy()
    sym = halcyon_symbol(40, col if decrypted else (150, 140, 180)).resize((80, 80), Image.LANCZOS)
    sym = seal_overlay(sym, cracked=decrypted, stamp=None)
    im.alpha_composite(sym, (14, 34))
    st_col = (120, 255, 150) if decrypted else (255, 110, 100)
    word = "DECRYPTED" if decrypted else "ENCRYPTED"
    st = Image.new("RGBA", (190, 46), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    sd.rectangle([2, 2, 187, 43], outline=st_col + (240,), width=3)
    sd.text((95, 23), word, font=F(SL.ANTON, 30), fill=st_col + (240,), anchor="mm")
    st = st.rotate(-10, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(st, (w - st.size[0] - 10, 88))
    dd = ImageDraw.Draw(im)
    dd.text((104, 46), "HALCYON CIVIC  //  ENFORCEMENT NET", font=F(SL.MONO, 12), fill=col + (255,) if decrypted else (170, 160, 200, 255))
    dd.text((104, 66), ("DECRYPTED BY THE CELL  //  KEY 7F-A2" if decrypted else "ENCRYPTED  //  NO KEY"), font=F(SL.MONO, 11),
            fill=(140, 255, 160, 255) if decrypted else (255, 140, 125, 255))
    if not decrypted:
        d = ImageDraw.Draw(im)
        hb = U._measure(head + rows) + 56
        cx, cy = w // 2, hb - 52
        d.rounded_rectangle([cx - 22, cy - 8, cx + 22, cy + 26], 5, outline=(255, 120, 110, 255), width=3)
        d.arc([cx - 14, cy - 30, cx + 14, cy - 2], 180, 360, fill=(255, 120, 110, 255), width=3)
        d.text((cx, cy + 40), "DECRYPT FAILED  //  CORP TRAFFIC HARDENED (HEAT 75+)", font=F(SL.MONO, 10), fill=(255, 150, 140, 255), anchor="mm")
    return dict(img=im, kind="holo")


# ------------------------------------------------------------------ the raid report as a corporate document
def report_doc(rows, w=560, seed=7, title="AFTER-ACTION REPORT", sub="HALCYON CIVIC  //  ENFORCEMENT DIVISION  //  WO 50-HC-114"):
    """Halcyon's own after-action report, intercepted: same paper family as the work order. Returns RGBA + row y map."""
    sc = S
    lh = 30
    h = 190 + len(rows) * lh + 90
    paper = Image.new("RGBA", (w * sc, h * sc), (233, 223, 198, 255))
    rng = np.random.default_rng(seed)
    n = (rng.random((h * sc // 6 + 1, w * sc // 6 + 1)) * 18).astype(np.uint8)
    grain = Image.fromarray(n).resize((w * sc, h * sc), Image.BICUBIC)
    paper = Image.composite(Image.new("RGBA", paper.size, (210, 198, 170, 255)), paper, grain)
    d = ImageDraw.Draw(paper)
    ink, dim = (30, 26, 30), (110, 100, 92)
    sym = halcyon_symbol(36, (90, 70, 170))
    paper.alpha_composite(sym, (24 * sc, 18 * sc))
    d.text((80 * sc, 28 * sc), "HALCYON CIVIC", font=F(SL.ANTON, 22 * sc), fill=(70, 50, 150), anchor="lm")
    d.text((80 * sc, 52 * sc), "CIVIC ORDER  //  PUBLIC SAFETY  //  COMPLIANCE", font=F(SL.MONO, 10 * sc), fill=dim, anchor="lm")
    d.line([(24 * sc, 78 * sc), ((w - 24) * sc, 78 * sc)], fill=(70, 50, 150), width=2 * sc)
    d.text((24 * sc, 100 * sc), title, font=F(SL.ANTON, 30 * sc), fill=ink, anchor="lm")
    d.text((24 * sc, 128 * sc), sub, font=F(SL.MONO, 11 * sc), fill=dim, anchor="lm")
    d.text((24 * sc, 152 * sc), "OPERATION: COMPLIANCE SWEEP      TARGET: SITE 07 (CELL)      OUTCOME: FAILED", font=F(SL.MONO, 11 * sc), fill=ink, anchor="lm")
    ymap = {}
    y = 186
    for r in rows:
        key, label, val = r[0], r[1], r[2]
        d.text((24 * sc, y * sc), label, font=F(SL.MONO, 14 * sc), fill=ink, anchor="lm")
        fv = F(SL.ANTON, 18 * sc)
        d.text(((w - 24) * sc, y * sc), val, font=fv, fill=(150, 30, 20) if r[3] else ink, anchor="rm")
        d.line([(24 * sc, (y + 13) * sc), ((w - 24) * sc, (y + 13) * sc)], fill=(200, 188, 160), width=sc)
        ymap[key] = (y, w - 24 - fv.getlength(val) / sc, w - 24)
        y += lh
    for k in range(3):   # redacted footer
        yy = y + 18 + k * 16
        x = 24
        while x < w * 0.7:
            ln = rng.uniform(30, 80)
            d.rectangle([x * sc, yy * sc, (x + ln) * sc, (yy + 8) * sc], fill=(16, 14, 18))
            x += ln + rng.uniform(6, 14)
    d.text((24 * sc, (h - 18) * sc), "INTERNAL  //  DO NOT FORWARD  //  COPY 2 OF 3", font=F(SL.MONO, 10 * sc), fill=dim, anchor="lm")
    st = Image.new("RGBA", (250 * sc, 70 * sc), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    sd.rectangle([3 * sc, 3 * sc, 247 * sc, 67 * sc], outline=(175, 25, 25, 215), width=4 * sc)
    sd.text((125 * sc, 35 * sc), "CLASSIFIED", font=F(SL.ANTON, 38 * sc), fill=(175, 25, 25, 215), anchor="mm")
    st = st.rotate(9, expand=True, resample=Image.BICUBIC)
    paper.alpha_composite(st, ((w - 300) * sc, (h - 150) * sc))
    paper = paper.resize((w, h), Image.LANCZOS)
    return paper, ymap


def place_paper(fr, paper, x, y, angle=0.0):
    """Paper under glass at (x, y) top-left with a soft shadow (no sticker die-cut)."""
    p = paper.rotate(angle, expand=True, resample=Image.BICUBIC)
    a = np.asarray(p, np.float32) / 255
    h, w = a.shape[:2]
    X, Y = int(x - fr.ox), int(y - fr.oy)
    out = fr.img.copy()
    sh = Image.fromarray((a[..., 3] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10))
    sh = np.asarray(sh, np.float32) / 255 * 0.55
    ys, xs = slice(max(0, Y + 10), min(fr.h, Y + 10 + h)), slice(max(0, X + 8), min(fr.w, X + 8 + w))
    out[ys, xs] *= (1 - sh[ys.start - Y - 10:ys.stop - Y - 10, xs.start - X - 8:xs.stop - X - 8])[..., None]
    ys, xs = slice(max(0, Y), min(fr.h, Y + h)), slice(max(0, X), min(fr.w, X + w))
    sub = a[ys.start - Y:ys.stop - Y, xs.start - X:xs.stop - X]
    out[ys, xs] = out[ys, xs] * (1 - sub[..., 3:4]) + sub[..., :3] * sub[..., 3:4]
    fr.img = out
    return fr
