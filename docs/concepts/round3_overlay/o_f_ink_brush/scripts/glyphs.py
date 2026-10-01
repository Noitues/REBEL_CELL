"""Brush-calligraphy skeleton alphabet (stroke order + direction matter) and seal carving."""
import math
import random
from PIL import Image, ImageDraw, ImageChops
import inklib as K

# glyph: (advance, [(mode, points, end), ...]); cap height = 1, y down
G = {
    'S': (0.80, [('c', [(0.76, 0.14), (0.55, 0.0), (0.25, 0.04), (0.12, 0.24), (0.3, 0.45), (0.62, 0.55), (0.8, 0.76), (0.66, 0.96), (0.36, 1.0), (0.04, 0.86)], 'f')]),
    'E': (0.74, [('l', [(0.15, 0.04), (0.12, 0.97), (0.76, 0.94)], 'f'), ('l', [(0.13, 0.04), (0.72, 0.0)], 'f'), ('l', [(0.16, 0.5), (0.6, 0.47)], 'f')]),
    'N': (0.88, [('l', [(0.10, 1.0), (0.12, 0.02), (0.78, 0.98), (0.82, -0.02)], 'f')]),
    'D': (0.84, [('l', [(0.13, 0.02), (0.11, 1.0)], 's'), ('c', [(0.12, 0.03), (0.5, 0.0), (0.8, 0.22), (0.84, 0.58), (0.6, 0.93), (0.08, 0.98)], 'f')]),
    'I': (0.36, [('l', [(0.2, 0.0), (0.17, 1.0)], 's')]),
    'T': (0.82, [('l', [(0.0, 0.06), (0.86, -0.01)], 'f'), ('l', [(0.44, 0.04), (0.41, 1.0)], 's')]),
    'O': (0.90, [('c', [(0.52, 0.0), (0.18, 0.1), (0.04, 0.52), (0.24, 0.94), (0.58, 1.0), (0.86, 0.68), (0.82, 0.22), (0.5, 0.01), (0.3, 0.1)], 'f')]),
    'W': (1.10, [('l', [(0.0, 0.0), (0.24, 1.0), (0.52, 0.28), (0.78, 1.0), (1.04, -0.02)], 'f')]),
    'H': (0.86, [('l', [(0.1, 0.0), (0.09, 1.0)], 's'), ('l', [(0.78, 0.0), (0.8, 1.0)], 's'), ('l', [(0.06, 0.53), (0.84, 0.47)], 'f')]),
    'U': (0.86, [('c', [(0.1, 0.0), (0.09, 0.6), (0.28, 0.97), (0.6, 0.97), (0.79, 0.6), (0.8, -0.02)], 'f')]),
    'R': (0.84, [('l', [(0.12, 0.0), (0.1, 1.0)], 's'), ('c', [(0.12, 0.03), (0.52, 0.0), (0.76, 0.2), (0.6, 0.45), (0.16, 0.52)], 's'), ('l', [(0.38, 0.5), (0.86, 1.0)], 'f')]),
    'M': (1.04, [('l', [(0.04, 1.0), (0.1, 0.0), (0.5, 0.72), (0.9, 0.0), (0.96, 1.0)], 'f')]),
    'B': (0.82, [('l', [(0.12, 0.0), (0.1, 1.0)], 's'), ('c', [(0.12, 0.02), (0.56, 0.0), (0.72, 0.22), (0.52, 0.46), (0.16, 0.5), (0.66, 0.54), (0.82, 0.78), (0.58, 0.98), (0.08, 0.98)], 'f')]),
    'Y': (0.86, [('l', [(0.0, 0.0), (0.42, 0.5)], 's'), ('l', [(0.88, -0.02), (0.44, 0.52), (0.4, 1.0)], 'f')]),
    'L': (0.72, [('l', [(0.14, 0.0), (0.11, 0.97), (0.78, 0.94)], 'f')]),
    'A': (0.92, [('l', [(0.0, 1.0), (0.44, 0.0), (0.92, 1.0)], 'f'), ('l', [(0.18, 0.64), (0.74, 0.6)], 'f')]),
    'V': (0.90, [('l', [(0.0, 0.0), (0.44, 1.0), (0.92, -0.02)], 'f')]),
    '!': (0.42, [('l', [(0.28, 0.0), (0.21, 0.7)], 's'), ('dot', [(0.18, 0.95)], 's')]),
    'F': (0.72, [('l', [(0.14, 0.04), (0.12, 1.0)], 's'), ('l', [(0.13, 0.04), (0.74, 0.0)], 'f'), ('l', [(0.14, 0.5), (0.58, 0.47)], 'f')]),
    'G': (0.92, [('c', [(0.8, 0.14), (0.52, 0.0), (0.18, 0.1), (0.04, 0.52), (0.24, 0.94), (0.58, 1.0), (0.84, 0.8), (0.86, 0.56)], 's'), ('l', [(0.5, 0.56), (0.92, 0.54)], 'f')]),
    'C': (0.84, [('c', [(0.8, 0.14), (0.52, 0.0), (0.18, 0.1), (0.04, 0.52), (0.24, 0.94), (0.58, 1.0), (0.86, 0.8)], 'f')]),
    'K': (0.84, [('l', [(0.12, 0.0), (0.1, 1.0)], 's'), ('l', [(0.8, 0.0), (0.14, 0.58)], 's'), ('l', [(0.34, 0.42), (0.86, 1.0)], 'f')]),
    'P': (0.80, [('l', [(0.12, 0.0), (0.1, 1.0)], 's'), ('c', [(0.12, 0.03), (0.55, 0.0), (0.78, 0.22), (0.6, 0.48), (0.14, 0.52)], 'f')]),
    'X': (0.86, [('l', [(0.0, 0.0), (0.86, 1.0)], 'f'), ('l', [(0.84, 0.0), (0.02, 1.0)], 'f')]),
    'Z': (0.80, [('l', [(0.04, 0.03), (0.78, 0.0), (0.06, 0.97), (0.82, 0.95)], 'f')]),
    '0': (0.76, [('c', [(0.44, 0.0), (0.12, 0.14), (0.04, 0.55), (0.24, 0.96), (0.54, 0.98), (0.74, 0.6), (0.66, 0.16), (0.42, 0.01), (0.26, 0.1)], 'f')]),
    '2': (0.78, [('c', [(0.08, 0.22), (0.36, 0.0), (0.68, 0.1), (0.68, 0.38), (0.36, 0.72), (0.06, 0.98)], 's'), ('l', [(0.06, 0.98), (0.8, 0.94)], 'f')]),
    '5': (0.76, [('l', [(0.78, 0.02), (0.22, 0.04), (0.16, 0.44)], 's'), ('c', [(0.16, 0.44), (0.5, 0.36), (0.78, 0.55), (0.74, 0.86), (0.44, 1.0), (0.06, 0.9)], 'f')]),
    '6': (0.78, [('c', [(0.68, 0.0), (0.34, 0.2), (0.1, 0.6), (0.24, 0.95), (0.56, 0.98), (0.76, 0.72), (0.56, 0.48), (0.16, 0.62)], 'f')]),
    '7': (0.76, [('l', [(0.04, 0.04), (0.8, 0.0), (0.34, 1.0)], 'f')]),
    '9': (0.78, [('c', [(0.66, 0.3), (0.42, 0.5), (0.12, 0.38), (0.18, 0.06), (0.5, 0.0), (0.7, 0.24), (0.62, 0.7), (0.3, 1.0)], 'f')]),
    ' ': (0.38, []),
    '.': (0.3, [('dot', [(0.12, 0.95)], 's')]),
}


def layout(text, x, y, cap, seed, slant=-0.16, track=0.07, jitter=1.0, rot=4.0, bounce=0.05):
    """Return [(mode, pts_px, end, stroke_seed)] for a word whose cap-top-left is (x, y)."""
    rng = random.Random(seed)
    strokes = []
    cx = x
    for ch in text:
        adv, sts = G[ch]
        sc = 1 + rng.uniform(-0.07, 0.07) * jitter
        ang = math.radians(rng.uniform(-rot, rot) * jitter)
        by = rng.uniform(-bounce, bounce) * cap * jitter
        c, s = math.cos(ang), math.sin(ang)
        pivot = (adv * 0.5, 0.5)
        for (mode, pts, end) in sts:
            out = []
            for (gx, gy) in pts:
                lx, ly = (gx - pivot[0]) * sc, (gy - pivot[1]) * sc
                lx, ly = lx * c - ly * s, lx * s + ly * c
                lx, ly = lx + pivot[0], ly + pivot[1]
                lx += slant * (ly - 1.0)  # italic lean (bottom anchored)
                out.append((cx + lx * cap, y + ly * cap + by))
            strokes.append((mode, out, end, rng.randrange(1 << 30)))
        cx += (adv * sc + track) * cap
    return strokes


def word_width(text, cap, track=0.07):
    return sum((G[ch][0] + track) * cap for ch in text) - track * cap


def paint(ink, strokes, width, cut=None, dry=0.55, wet=0.5, splat=0.4, head=True, **kw):
    """Paint laid-out strokes into ink. cut = px of total length to paint (None = all).
    Returns total length."""
    total = 0.0
    remaining = cut
    for (mode, pts, end, sd) in strokes:
        if mode == 'dot':
            if remaining is None or remaining > 0:
                rng = random.Random(sd)
                x, y = pts[0]
                ink.blob(x * K.SS, y * K.SS, width * 0.62 * K.SS, rng, val=255)
            total += width
            if remaining is not None:
                remaining -= width
            continue
        L = K.path_length(K.catmull(pts) if mode == 'c' else pts)
        if remaining is None:
            K.brush_stroke(ink, pts, width, sd, end=end, dry=dry, wet=wet, splat=splat, mode=mode, **kw)
        elif remaining > 0:
            c = remaining if remaining < L else None
            K.brush_stroke(ink, pts, width, sd, end=end, dry=dry, wet=wet, splat=splat, mode=mode, cut=c,
                           head=head, **kw)
            remaining -= L
        total += L
    return total


# seals -----------------------------------------------------------------------------------
def seal_patch(rows, w, h, seed, shape='rect', negative=True, line=0.14, round_r=None, border=0.07):
    """A carved seal impression (hanko). rows: list of strings; w,h in 1x px. Returns RGBA at SS."""
    rng = random.Random(seed)
    S = K.SS * 2  # carve at higher res for crisp edges
    PW, PH = int(w * S), int(h * S)
    m = Image.new("L", (PW, PH), 0)
    d = ImageDraw.Draw(m)
    bt = int(min(PW, PH) * border)
    if shape == 'round':
        d.ellipse((0, 0, PW - 1, PH - 1), fill=255)
        if not negative:
            d.ellipse((bt, bt, PW - 1 - bt, PH - 1 - bt), fill=0)
    else:
        rr = int(min(PW, PH) * 0.08)
        d.rounded_rectangle((0, 0, PW - 1, PH - 1), radius=rr, fill=255)
        if not negative:
            d.rounded_rectangle((bt, bt, PW - 1 - bt, PH - 1 - bt), radius=max(1, rr - bt), fill=0)
    # glyph field
    inset = bt * 1.9
    fw, fh = PW - 2 * inset, PH - 2 * inset
    if shape == 'round':
        inset = min(PW, PH) * 0.2
        fw, fh = PW - 2 * inset, PH - 2 * inset
    nrows = len(rows)
    rh = fh / nrows
    lw = max(2, int(min(PW, PH) * line / max(1, max(len(r) for r in rows)) * 1.6))
    lw = max(lw, int(rh * line))
    for ri, row in enumerate(rows):
        n = len(row)
        cw = fw / n
        for ci, ch in enumerate(row):
            adv, sts = G[ch]
            gx0 = inset + ci * cw + cw * 0.1
            gy0 = inset + ri * rh + rh * 0.1
            gw, gh = cw * 0.8, rh * 0.8
            for (mode, pts, end) in sts:
                if mode == 'dot':
                    x = gx0 + pts[0][0] / adv * gw
                    y = gy0 + pts[0][1] * gh
                    d.ellipse((x - lw * 0.6, y - lw * 0.6, x + lw * 0.6, y + lw * 0.6), fill=0 if negative else 255)
                    continue
                pp = [(gx0 + clampx(px / max(adv, 0.5)) * gw, gy0 + min(max(py, 0), 1) * gh) for px, py in pts]
                if mode == 'c':
                    pp = K.catmull(pp, 10)
                d.line(pp, fill=0 if negative else 255, width=lw, joint='curve')
                for (x, y) in (pp[0], pp[-1]):
                    d.ellipse((x - lw / 2, y - lw / 2, x + lw / 2, y + lw / 2), fill=0 if negative else 255)
    # carving wear: chipped edges, uneven ink pickup, paper voids
    u = min(PW, PH)
    n1 = K.noise(PW, PH, max(2, u // 4), rng)
    n2 = K.noise(PW, PH, max(2, u // 45), rng)
    hf = K.white(PW, PH, rng, max(1.0, u / 260))
    e = K.addn(K.addn(K.blur(m, max(1.0, u / 160)), n2, 0.55), hf, 0.35)
    m2 = K.ramp(e, 112, 150)
    press = n1.point([int(K.clamp(150 + v * 0.42, 0, 255)) for v in range(256)])
    voids = K.ramp(hf, 210, 245)
    m2 = ImageChops.multiply(m2, press)
    m2 = ImageChops.subtract(m2, K.scale_l(voids, 0.85))
    m2 = m2.resize((int(w * K.SS), int(h * K.SS)), Image.LANCZOS)
    tone = K.ramp(m2, 150, 255)
    col = Image.composite(Image.new("RGB", m2.size, K.SEAL_RED_DEEP), Image.new("RGB", m2.size, K.SEAL_RED), tone)
    out = col.convert("RGBA")
    out.putalpha(K.scale_l(m2, 1.05))
    return out


def clampx(v):
    return min(max(v, 0.0), 1.0)
