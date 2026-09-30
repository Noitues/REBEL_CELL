"""Gritty faceted UI pieces: worn sticker cards, salvaged spinners, dirty bars, tape labels."""
import math
import random
from PIL import Image, ImageDraw
from lowpoly import (SS, R, hexc, mix, ramp, toner, facet, bil, polar, panel, skew_rect, tri, gem, text, text_w, NEON,
                     line2, HAND)

# dirty, low-saturation kind ramps (the neon stays for highlights only)
KIND = {
    'attack': R('#1a0808', '#3e1010', '#6e1a18', '#9a2a20', '#c04a2a', '#d8784a', '#e8a878'),
    'block': R('#061418', '#0c2a32', '#124650', '#1c6a72', '#3a9090', '#7ab8b0', '#c0dcd0'),
    'hack': R('#1a0618', '#3a0c30', '#661848', '#8e2a62', '#b2487e', '#cc7ea0', '#e4b8c8'),
    'charge': R('#1a0e04', '#3e2008', '#6e3a0c', '#a05a14', '#c8802a', '#dca860', '#ecd09a'),
    'empty': R('#060608', '#0c0c10', '#141418', '#1c1c22', '#26262c', '#32323a', '#40404a'),
}
DARK = R('#040406', '#0a0a0c', '#121216', '#1c1c20', '#28272c', '#36343a')
METAL = R('#0c0c0e', '#1c1c1e', '#302f2e', '#484540', '#66625a', '#8c867a', '#b8b0a0')
RUST = R('#140806', '#2e120a', '#4e2010', '#6e3418', '#8e4e28', '#a86c44')
PAPER = R('#2a2620', '#4a443a', '#6e6656', '#948a74', '#b8ac90', '#d4c8aa', '#e8dcc0')
TAPE = R('#4a4230', '#7a6c48', '#a8966a', '#c8b688', '#dccca0', '#ece0bc')
CREAM = hexc('#ece0c8')
INK = hexc('#08070a')
KIND_LABEL = {'attack': 'ATTACK', 'block': 'GUARD', 'hack': 'HACK', 'charge': 'CHARGE'}
LIGHT_DIR = -math.radians(135)


# ------------------------------------------------------------------ icons (unit box)
def icon_tris(name):
    if name == 'blade':
        return [([(0.5, 0.06), (0.38, 0.62), (0.5, 0.62)], 0.9), ([(0.5, 0.06), (0.5, 0.62), (0.62, 0.62)], 0.55),
                ([(0.24, 0.62), (0.76, 0.62), (0.5, 0.72)], 0.35), ([(0.24, 0.62), (0.5, 0.72), (0.3, 0.72)], 0.7),
                ([(0.76, 0.62), (0.7, 0.72), (0.5, 0.72)], 0.2), ([(0.44, 0.72), (0.56, 0.72), (0.5, 0.95)], 0.6)]
    if name == 'shield':
        c = (0.5, 0.46)
        pts = [(0.5, 0.06), (0.84, 0.2), (0.78, 0.62), (0.5, 0.94), (0.22, 0.62), (0.16, 0.2)]
        return [([pts[k], pts[(k + 1) % 6], c], t) for k, t in enumerate([0.9, 0.65, 0.35, 0.25, 0.55, 0.8])]
    if name == 'eye':
        c = (0.5, 0.5)
        pts = [(0.06, 0.5), (0.5, 0.2), (0.94, 0.5), (0.5, 0.8)]
        out = [([pts[k], pts[(k + 1) % 4], c], t) for k, t in enumerate([0.85, 0.6, 0.3, 0.5])]
        p = [(0.36, 0.5), (0.5, 0.36), (0.64, 0.5), (0.5, 0.64)]
        return out + [([p[k], p[(k + 1) % 4], c], t) for k, t in enumerate([0.05, 0.15, 0.0, 0.1])]
    if name == 'bolt':
        return [([(0.64, 0.04), (0.24, 0.56), (0.56, 0.5)], 0.9), ([(0.64, 0.04), (0.56, 0.5), (0.5, 0.36)], 0.55),
                ([(0.42, 0.46), (0.78, 0.42), (0.34, 0.96)], 0.6), ([(0.42, 0.46), (0.6, 0.44), (0.34, 0.96)], 0.85)]
    if name == 'virus':
        out = []
        for k in range(8):
            a0, a1 = 2 * math.pi * k / 8, 2 * math.pi * (k + 1) / 8
            r = 0.46 if k % 2 == 0 else 0.3
            m = (0.5 + r * math.cos((a0 + a1) / 2), 0.5 + r * math.sin((a0 + a1) / 2))
            out.append(([(0.5, 0.5), (0.5 + 0.22 * math.cos(a0), 0.5 + 0.22 * math.sin(a0)), m], 0.4 + 0.25 * (k % 3)))
            out.append(([(0.5, 0.5), m, (0.5 + 0.22 * math.cos(a1), 0.5 + 0.22 * math.sin(a1))], 0.2 + 0.4 * (k % 2)))
        return out
    return []


def draw_icon(d, name, x, y, w, h, stops):
    for pts, t in icon_tris(name):
        tri(d, [(x + px * w, y + py * h) for px, py in pts], ramp(stops, t))


# ------------------------------------------------------------------ card: a battered sticker / data chip
CW, CH = 200, 290


def card_image(kind, title, cost, lines, icon, seed, tape=None):
    img = Image.new('RGBA', (CW * SS, CH * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rs = random.Random(str(seed))
    st = KIND[kind]

    # off-white sticker margin, scuffed
    def margin(u, v, i, j, k, rc):
        t = 0.62 + rc.uniform(-0.1, 0.1) - 0.15 * v
        if rc.random() < 0.15:
            t -= 0.3
        return ramp(PAPER, t)
    facet(d, bil([(0, 0), (CW, 0), (CW, CH), (0, CH)]), 6, 8, margin, ('cm', seed), 0.35)

    # body, worn at the edges
    bx0, by0, bx1, by1 = 7, 7, CW - 7, CH - 7

    def body(u, v, i, j, k, rc):
        t = 0.24 + 0.1 * (1 - v) + rc.uniform(-0.05, 0.05)
        edge = min(u, 1 - u, v, 1 - v)
        if edge < 0.12 and rc.random() < 0.35:
            return ramp(PAPER, rc.uniform(0.35, 0.6))  # rubbed through to the paper
        if rc.random() < 0.06:
            t += 0.18
        return ramp(st, t)
    facet(d, bil([(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)]), 6, 9, body, ('cb', seed), 0.35)
    ax, ay, aw, ah = 16, 44, CW - 32, 120

    def art(u, v, i, j, k, rc):
        t = 0.58 - 0.25 * (u - 0.5) - 0.3 * (v - 0.5) + rc.uniform(-0.1, 0.1)
        if rc.random() < 0.18:
            t += 0.2 if rc.random() < 0.5 else -0.2
        if rc.random() < 0.05:
            return ramp(PAPER, 0.5)
        return ramp(st, t)
    facet(d, bil([(ax, ay), (ax + aw, ay), (ax + aw, ay + ah), (ax, ay + ah)]), 6, 4, art, ('ca', seed), 0.35)
    draw_icon(d, icon, ax + aw / 2 - 46, ay + 12, 92, 96, DARK + [hexc('#5a5460'), CREAM])
    text(d, CW - 16, 26, KIND_LABEL[kind], 15, ramp(st, 0.85), anchor='rm', style='Bold SemiCondensed')
    text(d, CW / 2, 188, title, 23, CREAM, anchor='mm', style='Bold SemiCondensed')
    tri(d, [(30, 206), (CW / 2, 202), (CW / 2, 209)], ramp(st, 0.6))
    tri(d, [(CW - 30, 206), (CW / 2, 202), (CW / 2, 209)], ramp(st, 0.4))
    for n, ln in enumerate(lines):
        text(d, CW / 2, 230 + n * 23, ln, 18, hexc('#d8ccc4'), anchor='mm', style='SemiBold SemiCondensed')
    # scratches
    for _ in range(rs.randint(2, 4)):
        x = rs.uniform(10, CW - 40)
        y = rs.uniform(20, CH - 30)
        line2(d, (x, y), (x + rs.uniform(20, 60), y + rs.uniform(-12, 12)), 1.2, ramp(PAPER, 0.7) + (170,))
    # torn corner
    cx = rs.choice([0, 1])
    tear = [(CW, CH - rs.uniform(24, 34)), (CW, CH), (CW - rs.uniform(24, 34), CH),
            (CW - rs.uniform(8, 14), CH - rs.uniform(12, 18))] if cx else \
        [(0, rs.uniform(24, 34)), (0, 0), (rs.uniform(24, 34), 0), (rs.uniform(8, 14), rs.uniform(12, 18))]
    d.polygon([(p[0] * SS, p[1] * SS) for p in tear], fill=(0, 0, 0, 0))
    # cost gem (a chipped hex)
    gem(d, 30, 26, 23, 23, NEON['sodium'], ('cg', seed), n=6, base=0.55)
    text(d, 30, 27, str(cost), 25, INK, anchor='mm')
    if tape:
        tape_strip(d, tape[0], tape[1], tape[2], tape[3], ('ct', seed), alpha=205)
    return img


def paste_card(base, cimg, cx, cy, angle):
    r = cimg.rotate(angle, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(r, (int(cx * SS - r.width / 2), int(cy * SS - r.height / 2)))


def tape_strip(d, x, y, w, ang, seed, h=26, alpha=None):
    """Torn masking tape: a faceted strip with ragged ends."""
    rc = random.Random(str(seed))
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))

    def P(u, v):
        px, py = u - w / 2, v - h / 2
        return (x + px * ca - py * sa, y + px * sa + py * ca)
    left = [P(rc.uniform(0, 6), 0), P(rc.uniform(0, 6), h / 2), P(rc.uniform(0, 6), h)]
    right = [P(w - rc.uniform(0, 6), 0), P(w - rc.uniform(0, 6), h / 2), P(w - rc.uniform(0, 6), h)]
    q = [left[0], right[0], right[2], left[2]]
    facet(d, bil(q), max(2, int(w / 40)), 1, toner(TAPE, 0.6, gu=0.1, var=0.08, flip=0.1,
                                                     alpha=alpha), seed, 0.3)
    return P


# ------------------------------------------------------------------ spinner: salvaged hardware
def spinner(d, cx, cy, Rr, slices, seed, cracked=False, crack_ang=0.8, glyphs=False, needle=False, dense=1):
    total = 30
    tick = 2 * math.pi / total
    rs = random.Random(str(('sp', seed)))
    gap = (crack_ang - 0.09, crack_ang + 0.07)

    def in_gap(ang):
        a = ang % (2 * math.pi)
        return cracked and gap[0] % (2 * math.pi) <= a <= gap[1] % (2 * math.pi)

    # hazard-striped outer band with a scuffed metal back half
    def band(u, v, i, j, k, rc):
        ang = u * 2 * math.pi
        if in_gap(ang):
            return None
        lam = 0.5 + 0.5 * math.cos(ang - LIGHT_DIR)
        if 3.4 < ang < 5.4 or ang < 0.3:
            if rc.random() < 0.12:
                return ramp(METAL, 0.6)  # chipped paint
            return ramp(NEON['sodium'] if i % 2 == 0 else DARK, 0.35 + 0.35 * lam + rc.uniform(-0.05, 0.05))
        if rc.random() < 0.3:
            return ramp(RUST, 0.2 + 0.6 * lam + rc.uniform(-0.1, 0.1))
        return ramp(METAL, 0.1 + 0.55 * lam + rc.uniform(-0.08, 0.08))
    facet(d, polar(cx, cy, Rr, Rr, 0, 2 * math.pi, 1.0, 1.12), 48 * dense, 1, band, ('band', seed), 0.2, wrap_u=True)

    def rim(u, v, i, j, k, rc):
        ang = u * 2 * math.pi
        if in_gap(ang):
            return None
        lam = 0.5 + 0.5 * math.cos(ang - LIGHT_DIR)
        if rc.random() < 0.18:
            return ramp(RUST, 0.25 + 0.5 * lam)
        return ramp(METAL, 0.12 + 0.62 * lam + rc.uniform(-0.1, 0.1))
    facet(d, polar(cx, cy, Rr, Rr, 0, 2 * math.pi, 0.88, 1.0), 60 * dense, 2 if dense > 1 else 1, rim, ('rim', seed), 0.25, wrap_u=True)
    labels = []
    a = -math.pi / 2
    for n, (ticks, kind, value) in enumerate(slices):
        a0, a1 = a, a + ticks * tick
        st = KIND[kind]

        def col(u, v, i, j, k, rc, a0=a0, a1=a1, st=st, kind=kind):
            ang = a0 + (a1 - a0) * u
            lam = 0.5 + 0.5 * math.cos(ang - LIGHT_DIR)
            base = 0.3 + 0.45 * lam + 0.12 * (v - 0.5)
            if kind == 'empty':
                base = 0.25 + 0.4 * lam
            t = base + rc.uniform(-0.08, 0.08)
            r = rc.random()
            if r < 0.07 / dense ** 1.5:
                return ramp(RUST, 0.3 + 0.4 * lam)   # rust bloom
            if r < 0.11 / dense ** 1.5:
                return ramp(METAL, 0.55 + 0.3 * lam)  # chipped to bare metal
            if rc.random() < 0.14:
                t += 0.14 if rc.random() < 0.5 else -0.14
            return ramp(st, t)
        facet(d, polar(cx, cy, Rr, Rr, a0, a1, 0.26, 0.88), max(2, ticks * 2 * dense), 4 + 2 * dense, col, ('sl', seed, n), 0.3)
        if value is not None:
            labels.append(((a0 + a1) / 2, value, kind))
        a = a1
    for k in range(total):
        ang = -math.pi / 2 + k * tick
        if in_gap(ang):
            continue
        p0 = (cx + Rr * 0.99 * math.cos(ang), cy + Rr * 0.99 * math.sin(ang))
        p1 = (cx + Rr * 0.925 * math.cos(ang - 0.03), cy + Rr * 0.925 * math.sin(ang - 0.03))
        p2 = (cx + Rr * 0.925 * math.cos(ang + 0.03), cy + Rr * 0.925 * math.sin(ang + 0.03))
        tri(d, [p0, p1, p2], hexc('#d8ccb8') if k % 5 == 0 else hexc('#6e685e'))
    # bolts on the band
    for k in range(8):
        ang = -math.pi / 2 + (k + 0.5) * 2 * math.pi / 8
        if in_gap(ang):
            continue
        bx, by = cx + Rr * 1.06 * math.cos(ang), cy + Rr * 1.06 * math.sin(ang)
        gem(d, bx, by, max(7, Rr * 0.028), max(7, Rr * 0.028), METAL, ('bolt', seed, k), n=6, base=0.6)
    if cracked:
        # a jagged crack from the broken rim into the hub, dark core with a pale lip
        pts = []
        r = 1.1
        ang = crack_ang
        while r > 0.28:
            pts.append((cx + Rr * r * math.cos(ang), cy + Rr * r * math.sin(ang)))
            r -= rs.uniform(0.08, 0.16)
            ang += rs.uniform(-0.09, 0.09)
        for k in range(len(pts) - 1):
            w = 12 * (1 - k / len(pts)) + 3
            line2(d, pts[k], pts[k + 1], w, INK)
            line2(d, (pts[k][0] + 4, pts[k][1] - 3), (pts[k + 1][0] + 4, pts[k + 1][1] - 3), 2.2, ramp(METAL, 0.8))
        # a branch
        b0 = pts[len(pts) // 3]
        line2(d, b0, (b0[0] + 44, b0[1] + 30), 5, INK)
        b1 = pts[2 * len(pts) // 3]
        line2(d, b1, (b1[0] - 30, b1[1] + 34), 4, INK)
    gem(d, cx, cy, Rr * 0.27, Rr * 0.27, METAL, ('hub', seed), n=6, base=0.45)
    for k in range(3):
        ang = k * 2 * math.pi / 3 + 0.3
        gem(d, cx + Rr * 0.16 * math.cos(ang), cy + Rr * 0.16 * math.sin(ang), 6, 6, RUST, ('hb', seed, k), n=6,
            base=0.55)
    GLY = {'attack': 'blade', 'block': 'shield', 'hack': 'eye', 'charge': 'bolt'}
    for ang, value, kind in labels:
        rr = 0.7 if glyphs else 0.6
        x = cx + Rr * rr * math.cos(ang)
        y = cy + Rr * rr * math.sin(ang)
        text(d, x, y, str(value), max(34, Rr * 0.14), CREAM, anchor='mm', shadow=INK, sh=2 if Rr < 300 else 4)
        if glyphs and kind in GLY:
            gs = Rr * 0.17
            gx = cx + Rr * 0.45 * math.cos(ang)
            gy = cy + Rr * 0.45 * math.sin(ang)
            draw_icon(d, GLY[kind], gx - gs / 2, gy - gs / 2, gs, gs, R('#0c0a0e', '#2a2228', '#6a5e62', '#b8aca4', '#f0e6d4'))
    if needle:
        # a tapered steel needle from the hub toward the pointer, with a counterweight tail
        na = -math.pi / 2 + 0.05
        tip = (cx + Rr * 0.84 * math.cos(na), cy + Rr * 0.84 * math.sin(na))
        tail = (cx - Rr * 0.3 * math.cos(na), cy - Rr * 0.3 * math.sin(na))
        px, py = -math.sin(na) * Rr * 0.035, math.cos(na) * Rr * 0.035
        tri(d, [(cx + px, cy + py), tip, (cx, cy)], ramp(METAL, 0.85))
        tri(d, [(cx - px, cy - py), tip, (cx, cy)], ramp(METAL, 0.45))
        tri(d, [(cx + px * 2.2, cy + py * 2.2), tail, (cx, cy)], ramp(RUST, 0.55))
        tri(d, [(cx - px * 2.2, cy - py * 2.2), tail, (cx, cy)], ramp(RUST, 0.3))
        tri(d, [(tip[0] - px * 0.5, tip[1] - py * 0.5 + 18), tip, (tip[0] + px * 0.5, tip[1] + py * 0.5 + 18)],
            ramp(NEON['sodium'], 0.8))
        gem(d, cx, cy, Rr * 0.09, Rr * 0.09, NEON['sodium'], ('ncap', seed), n=6, base=0.5)
    # pointer: a bent steel blade with a hazard-striped mount
    tipy = cy - Rr * 0.8
    top = cy - Rr * 1.22
    w = Rr * 0.16
    pst = R('#1a0c06', '#4a1e0c', '#9a4412', '#e07a1c', '#ffc060', '#fff0c0')
    tri(d, [(cx - w, top), (cx, top - 8), (cx, tipy)], ramp(pst, 0.9))
    tri(d, [(cx, top - 8), (cx + w, top), (cx, tipy)], ramp(pst, 0.5))
    tri(d, [(cx - w, top), (cx - w * 0.45, top + (tipy - top) * 0.45), (cx, tipy)], ramp(pst, 0.7))
    tri(d, [(cx + w, top), (cx + w * 0.45, top + (tipy - top) * 0.45), (cx, tipy)], ramp(pst, 0.25))
    tri(d, [(cx - w * 0.3, top + 10), (cx + w * 0.1, top + 6), (cx - w * 0.05, top + 24)], ramp(RUST, 0.4))
    for k in range(4):
        x0 = cx - w * 1.1 + k * w * 0.55
        tri(d, [(x0, top - 16), (x0 + w * 0.3, top - 16), (x0 + w * 0.12, top - 4)],
            ramp(NEON['sodium'] if k % 2 == 0 else DARK, 0.55))


# ------------------------------------------------------------------ bars / buttons
def hp_bar(d, x, y, w, h, frac, stops, label, seed, shield=None):
    panel(d, skew_rect(x, y, w, h, 12), DARK, 0.3, ('hpf', seed), nu=10, nv=1, gv=-0.3)
    fw = (w - 12) * frac
    q = skew_rect(x + 6, y + 5, fw, h - 10, 8)

    def cf(u, v, i, j, k, rc):
        if rc.random() < 0.08:
            return ramp(RUST, 0.4)
        return ramp(stops, 0.5 + 0.2 * (1 - v) + rc.uniform(-0.1, 0.1))
    facet(d, bil(q), max(2, int(fw / 24)), 2, cf, ('hpb', seed), 0.35)
    # hazard ticks on the empty part
    for k in range(int((w - 12 - fw) / 22)):
        xx = x + 6 + fw + 8 + k * 22
        tri(d, [(xx + 8, y + 7), (xx + 16, y + 7), (xx + 4, y + h - 7)], ramp(DARK, 0.9))
    text(d, x + 22, y + h / 2 + 1, label, 22, CREAM, anchor='lm', shadow=INK)
    if shield is not None:
        sx = x + w + 40
        gem(d, sx, y + h / 2, 26, 30, KIND['block'], ('shd', seed), n=6, base=0.6)
        text(d, sx, y + h / 2 + 1, str(shield), 24, INK, anchor='mm')


def hex_button(d, cx, cy, rx, ry, stops, label, seed, size=56, sub=None, ink=INK):
    def cf(u, v, i, j, k, rc):
        lam = 0.5 + 0.5 * math.cos(-math.pi + 2 * math.pi * u - LIGHT_DIR)
        if rc.random() < 0.08:
            return ramp(METAL, 0.5)
        return ramp(stops, 0.3 + 0.45 * lam + 0.12 * (1 - v) + rc.uniform(-0.08, 0.08))
    # hazard collar
    facet(d, polar(cx, cy, rx * 1.12, ry * 1.12, -math.pi, math.pi, 0.9, 1.0), 24, 1,
          lambda u, v, i, j, k, rc: ramp(NEON['sodium'] if i % 2 == 0 else DARK, 0.5 + rc.uniform(-0.1, 0.1)),
          ('hbc', seed), 0.1, wrap_u=True)
    facet(d, polar(cx, cy, rx, ry, -math.pi, math.pi, 0, 1), 6, 3, cf, ('hb', seed), 0.2, wrap_u=True)
    text(d, cx, cy - (8 if sub else 0), label, size, ink, anchor='mm')
    if sub:
        text(d, cx, cy + size * 0.55, sub, 18, ink, anchor='mm', style='Bold SemiCondensed')
