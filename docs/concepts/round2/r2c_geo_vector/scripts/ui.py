"""Faceted UI pieces: cards, spinners, buttons, bars, tags."""
import math
import random
from PIL import Image, ImageDraw
from lowpoly import (SS, R, hexc, mix, ramp, toner, facet, bil, polar, panel, skew_rect, tri, gem, text, text_w, NEON)

# card / slice families: deep -> pale ramps
KIND = {
    'attack': R('#2b0a24', '#6e1433', '#b01e3a', '#dc2f44', '#f0584a', '#f89070', '#fcd0a8'),
    'block': R('#04182a', '#0a3450', '#0e6080', '#1898b0', '#40c8d0', '#9ee8e0', '#e0fff4'),
    'hack': R('#1a0630', '#3e0c5a', '#7a1480', '#b8248e', '#e8489e', '#f890c0', '#ffd4e8'),
    'charge': R('#2a1206', '#6a2e0a', '#b0580e', '#e08a18', '#f4b830', '#fadc6a', '#fff4c0'),
    'empty': R('#07060e', '#100c1c', '#1a142a', '#261e3a', '#34284a', '#463660', '#5a4674'),
}
DARK = R('#05040a', '#0c0a16', '#161226', '#221a36', '#302448', '#42325c')
CREAM = hexc('#fbeed2')
INK = hexc('#0a0610')
KIND_LABEL = {'attack': 'ATTACK', 'block': 'GUARD', 'hack': 'HACK', 'charge': 'CHARGE'}


# ------------------------------------------------------------------ icons (unit box)
def icon_tris(name):
    if name == 'blade':
        return [([(0.5, 0.06), (0.38, 0.62), (0.5, 0.62)], 0.9), ([(0.5, 0.06), (0.5, 0.62), (0.62, 0.62)], 0.55),
                ([(0.24, 0.62), (0.76, 0.62), (0.5, 0.72)], 0.35), ([(0.24, 0.62), (0.5, 0.72), (0.3, 0.72)], 0.7),
                ([(0.76, 0.62), (0.7, 0.72), (0.5, 0.72)], 0.2), ([(0.44, 0.72), (0.56, 0.72), (0.5, 0.95)], 0.6)]
    if name == 'shield':
        c = (0.5, 0.46)
        pts = [(0.5, 0.06), (0.84, 0.2), (0.78, 0.62), (0.5, 0.94), (0.22, 0.62), (0.16, 0.2)]
        tones = [0.9, 0.65, 0.35, 0.25, 0.55, 0.8]
        return [([pts[k], pts[(k + 1) % 6], c], tones[k]) for k in range(6)]
    if name == 'eye':
        c = (0.5, 0.5)
        pts = [(0.06, 0.5), (0.5, 0.2), (0.94, 0.5), (0.5, 0.8)]
        out = [([pts[k], pts[(k + 1) % 4], c], t) for k, t in enumerate([0.85, 0.6, 0.3, 0.5])]
        p = [(0.36, 0.5), (0.5, 0.36), (0.64, 0.5), (0.5, 0.64)]
        out += [([p[k], p[(k + 1) % 4], c], t) for k, t in enumerate([0.05, 0.15, 0.0, 0.1])]
        return out
    if name == 'bolt':
        return [([(0.64, 0.04), (0.24, 0.56), (0.56, 0.5)], 0.9), ([(0.64, 0.04), (0.56, 0.5), (0.5, 0.36)], 0.55),
                ([(0.42, 0.46), (0.78, 0.42), (0.34, 0.96)], 0.6), ([(0.42, 0.46), (0.6, 0.44), (0.34, 0.96)], 0.85)]
    if name == 'virus':
        out = []
        for k in range(8):
            a0 = 2 * math.pi * k / 8
            a1 = 2 * math.pi * (k + 1) / 8
            r = 0.46 if k % 2 == 0 else 0.3
            out.append(([(0.5, 0.5), (0.5 + 0.22 * math.cos(a0), 0.5 + 0.22 * math.sin(a0)),
                         (0.5 + r * math.cos((a0 + a1) / 2), 0.5 + r * math.sin((a0 + a1) / 2))], 0.4 + 0.5 * (k % 3) / 2))
            out.append(([(0.5, 0.5), (0.5 + r * math.cos((a0 + a1) / 2), 0.5 + r * math.sin((a0 + a1) / 2)),
                         (0.5 + 0.22 * math.cos(a1), 0.5 + 0.22 * math.sin(a1))], 0.2 + 0.4 * (k % 2)))
        return out
    return []


def draw_icon(d, name, x, y, w, h, stops):
    for pts, t in icon_tris(name):
        tri(d, [(x + px * w, y + py * h) for px, py in pts], ramp(stops, t))


# ------------------------------------------------------------------ card
CW, CH = 200, 290


def card_image(kind, title, cost, lines, icon, seed, hover=False):
    img = Image.new('RGBA', (CW * SS, CH * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    st = KIND[kind]
    # body: dark end of the kind ramp, lit from the top-left
    panel(d, [(0, 0), (CW, 0), (CW, CH), (0, CH)], st, 0.2, ('cb', seed), nu=5, nv=7, gu=-0.08, gv=-0.12, var=0.05, flip=0.1)
    # art window
    ax, ay, aw, ah = 14, 44, CW - 28, 122
    facet(d, bil([(ax, ay), (ax + aw, ay), (ax + aw, ay + ah), (ax, ay + ah)]), 6, 4,
              toner(st, 0.6, gu=-0.25, gv=-0.3, var=0.1, flip=0.2, famt=0.2), ('ca', seed))
    draw_icon(d, icon, ax + aw / 2 - 48, ay + 12, 96, 98, DARK + [hexc('#6a5a80'), CREAM])
    # kind strip
    text(d, CW - 16, 25, KIND_LABEL[kind], 15, ramp(st, 0.85), anchor='rm', style='Bold SemiCondensed')
    # title
    text(d, CW / 2, 190, title, 23, CREAM, anchor='mm', style='Bold SemiCondensed')
    # rule made of two slim triangles
    tri(d, [(30, 208), (CW / 2, 204), (CW / 2, 211)], ramp(st, 0.7))
    tri(d, [(CW - 30, 208), (CW / 2, 204), (CW / 2, 211)], ramp(st, 0.45))
    for n, ln in enumerate(lines):
        text(d, CW / 2, 232 + n * 24, ln, 18, hexc('#e8d8e8'), anchor='mm', style='SemiBold SemiCondensed')
    # cut corner (bottom-right) for silhouette
    d.polygon([(CW * SS, (CH - 22) * SS), (CW * SS, CH * SS), ((CW - 22) * SS, CH * SS)], fill=(0, 0, 0, 0))
    # cost gem
    gem(d, 30, 26, 24, 24, NEON['amber'], ('cg', seed), n=6, base=0.6)
    text(d, 30, 27, str(cost), 26, INK, anchor='mm')
    return img


def paste_card(base, cimg, cx, cy, angle):
    r = cimg.rotate(angle, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(r, (int(cx * SS - r.width / 2), int(cy * SS - r.height / 2)))


# ------------------------------------------------------------------ spinner
LIGHT_DIR = -math.radians(135)  # light from the upper-left


def spinner(d, cx, cy, Rr, slices, seed, pointer_at=None):
    """slices: list of (ticks, kind, value); 30 ticks start at 12 o'clock, clockwise."""
    total = 30
    tick = 2 * math.pi / total
    a = -math.pi / 2
    # outer shadow ring and rim
    facet(d, polar(cx, cy, Rr, Rr, 0, 2 * math.pi, 1.0, 1.1), 30, 1, toner(DARK, 0.2, var=0.1), ('sr', seed), 0.2,
          wrap_u=True)

    def rim_col(u, v, i, j, k, rc):
        ang = u * 2 * math.pi
        lam = 0.5 + 0.5 * math.cos(ang - LIGHT_DIR)
        return ramp(R('#120e1e', '#2a2238', '#4a3c5c', '#7a6888', '#c0b0c8'), 0.15 + 0.7 * lam + rc.uniform(-0.08, 0.08))
    facet(d, polar(cx, cy, Rr, Rr, 0, 2 * math.pi, 0.88, 1.0), 60, 1, rim_col, ('rim', seed), 0.2, wrap_u=True)
    labels = []
    for n, (ticks, kind, value) in enumerate(slices):
        a0, a1 = a, a + ticks * tick
        st = KIND[kind]

        def col(u, v, i, j, k, rc, a0=a0, a1=a1, st=st, kind=kind):
            ang = a0 + (a1 - a0) * u
            lam = 0.5 + 0.5 * math.cos(ang - LIGHT_DIR)
            base = 0.28 + 0.5 * lam + 0.12 * (v - 0.5)
            if kind == 'empty':
                base = 0.2 + 0.4 * lam
            t = base + rc.uniform(-0.08, 0.08)
            if rc.random() < 0.15:
                t += 0.14 if rc.random() < 0.5 else -0.14
            return ramp(st, t)
        facet(d, polar(cx, cy, Rr, Rr, a0, a1, 0.26, 0.88), max(1, ticks), 3, col, ('sl', seed, n), 0.28)
        if value is not None:
            labels.append(((a0 + a1) / 2, value, kind))
        a = a1
    # tick teeth on the rim
    for k in range(total):
        ang = -math.pi / 2 + k * tick
        p0 = (cx + Rr * 0.99 * math.cos(ang), cy + Rr * 0.99 * math.sin(ang))
        p1 = (cx + Rr * 0.925 * math.cos(ang - 0.03), cy + Rr * 0.925 * math.sin(ang - 0.03))
        p2 = (cx + Rr * 0.925 * math.cos(ang + 0.03), cy + Rr * 0.925 * math.sin(ang + 0.03))
        tri(d, [p0, p1, p2], hexc('#e8dcf0') if k % 5 == 0 else hexc('#8a7a9a'))
    # hub
    gem(d, cx, cy, Rr * 0.27, Rr * 0.27, R('#0a0814', '#1a1428', '#302640', '#4e4062', '#7a6a8e', '#b4a6c4'), ('hub', seed),
        n=6, base=0.5)
    for ang, value, kind in labels:
        x = cx + Rr * 0.6 * math.cos(ang)
        y = cy + Rr * 0.6 * math.sin(ang)
        text(d, x, y, str(value), 34, CREAM, anchor='mm', shadow=INK, sh=2)
    # pointer at 12 o'clock
    tipy = cy - Rr * 0.8
    top = cy - Rr * 1.2
    w = Rr * 0.17
    pst = R('#3a0a10', '#8a1a1a', '#e0502a', '#ffb040', '#fff0b0')
    tri(d, [(cx - w, top), (cx, top - 8), (cx, tipy)], ramp(pst, 0.95))
    tri(d, [(cx, top - 8), (cx + w, top), (cx, tipy)], ramp(pst, 0.55))
    tri(d, [(cx - w, top), (cx - w * 0.45, top + (tipy - top) * 0.45), (cx, tipy)], ramp(pst, 0.75))
    tri(d, [(cx + w, top), (cx + w * 0.45, top + (tipy - top) * 0.45), (cx, tipy)], ramp(pst, 0.3))


# ------------------------------------------------------------------ bars / buttons / tags
def hp_bar(d, x, y, w, h, frac, stops, label, seed, shield=None):
    panel(d, skew_rect(x, y, w, h, 12), DARK, 0.25, ('hpf', seed), nu=10, nv=1, gv=-0.3)
    fw = (w - 12) * frac
    q = skew_rect(x + 6, y + 5, fw, h - 10, 8)
    facet(d, bil(q), max(2, int(fw / 26)), 2, toner(stops, 0.62, gu=0.2, gv=-0.3, var=0.1, flip=0.15), ('hpb', seed), 0.3)
    text(d, x + 22, y + h / 2 + 1, label, 22, CREAM, anchor='lm', shadow=INK)
    if shield is not None:
        sx = x + w + 40
        gem(d, sx, y + h / 2, 26, 30, KIND['block'], ('shd', seed), n=6, base=0.6)
        text(d, sx, y + h / 2 + 1, str(shield), 24, INK, anchor='mm')


def hex_button(d, cx, cy, rx, ry, stops, label, seed, size=56, sub=None, ink=INK):
    facet(d, polar(cx, cy, rx, ry, -math.pi, math.pi, 0, 1), 6, 3,
          lambda u, v, i, j, k, rc: ramp(stops, 0.35 + 0.45 * (0.5 + 0.5 * math.cos(-math.pi + 2 * math.pi * u - LIGHT_DIR))
                                         + 0.12 * (1 - v) + rc.uniform(-0.08, 0.08)),
          ('hb', seed), 0.2, wrap_u=True)
    text(d, cx, cy - (8 if sub else 0), label, size, ink, anchor='mm')
    if sub:
        text(d, cx, cy + size * 0.55, sub, 18, ink, anchor='mm', style='Bold SemiCondensed')


def price_tag(d, cx, y, price, seed, stops=None):
    stops = stops or NEON['amber']
    s = f'{price} CR'
    w = text_w(s, 24) + 44
    panel(d, skew_rect(cx - w / 2, y, w, 40, 10), stops, 0.62, ('pt', seed), nu=4, nv=1, gv=-0.3, var=0.08)
    tri(d, [(cx - w / 2 + 2, y + 20), (cx - w / 2 + 16, y + 6), (cx - w / 2 + 16, y + 34)], ramp(stops, 0.2))
    text(d, cx + 6, y + 21, s, 24, INK, anchor='mm')
