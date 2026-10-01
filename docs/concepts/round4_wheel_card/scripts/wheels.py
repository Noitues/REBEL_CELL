"""Round 4 wheels: W-A salvaged faceted, W-B instrument dial, W-C layered physical stack,
W-D segmented ring + sticker values. Each renders to a 1x RGBA layer centred on the hub."""
import math
import random
from common import *
import sticker_lib as SL

LIGHT_ANG = math.radians(-125)


def lam_at(a):
    return 0.5 + 0.5 * math.cos(a - LIGHT_ANG)


def wedge(d, cx, cy, r0, r1, a0, a1, stops, seed, nu=2, nv=2, base=0.5, spread=0.14, var=0.03, jit=0.25):
    def col(u, v, i, j, k, rc):
        a = a0 + (a1 - a0) * u
        return ramp(stops, base + spread * (lam_at(a) - 0.5) + rc.uniform(-var, var))
    facet(d, polar(cx, cy, 1, 1, a0, a1, r0, r1), max(1, nu), nv, col, seed, jit)


def ring(d, cx, cy, r0, r1, stops, seed, n=48, base=0.45, spread=0.5, var=0.05, fn=None):
    def col(u, v, i, j, k, rc):
        a = u * 2 * math.pi
        if fn:
            c = fn(a, i, rc)
            if c is not None:
                return c
        return ramp(stops, base + spread * (lam_at(a) - 0.5) + rc.uniform(-var, var))
    facet(d, polar(cx, cy, 1, 1, 0, 2 * math.pi, r0, r1), n, 1, col, seed, 0.15, wrap_u=True)


def overlay(img, draw_fn):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(lay))
    img.alpha_composite(lay)


def rim_fn(owner):
    """Pattern for the outer band per owner: hazard (player), container ribs (Meridian), spiked red (boss)."""
    def f(a, i, rc):
        if owner == 'enemy':
            if i % 8 == 7:
                return ramp(DARK, 0.5)
            return ramp(MER, (0.42 if i % 2 else 0.6) + 0.25 * (lam_at(a) - 0.5) + rc.uniform(-0.03, 0.03))
        if owner == 'boss':
            return ramp(BOSSR, (0.4 if i % 2 else 0.55) + 0.3 * (lam_at(a) - 0.5) + rc.uniform(-0.03, 0.03))
        aa = a % (2 * math.pi)
        if 3.3 < aa < 5.6:
            if rc.random() < 0.1:
                return ramp(RUST, 0.5)
            return ramp(HAZ if i % 2 == 0 else DARK, 0.42 + 0.3 * lam_at(a))
        if rc.random() < 0.25:
            return ramp(RUST, 0.3 + 0.5 * lam_at(a))
        return None
    return f


def boss_spikes(d, cx, cy, r):
    for k in range(12):
        a = -math.pi / 2 + k * math.pi / 6
        p0 = (cx + r * math.cos(a - 0.07), cy + r * math.sin(a - 0.07))
        p1 = (cx + r * math.cos(a + 0.07), cy + r * math.sin(a + 0.07))
        p2 = (cx + r * 1.14 * math.cos(a), cy + r * 1.14 * math.sin(a))
        fpoly(d, [p0, p1, p2], ramp(BOSSR, 0.35 + 0.35 * lam_at(a)))


def corrupted(img, d, cx, cy, r0, r1, a0, a1, s):
    """CORRUPTED: glitch-offset shards + magenta scan slivers + a broken-square badge at the outer edge."""
    rng = random.Random(int(r1 * 100))
    for k in range(5):
        rr = r0 + (r1 - r0) * rng.uniform(0.1, 0.9)
        aa = a0 + (a1 - a0) * rng.uniform(0.0, 0.7)
        L = (a1 - a0) * rng.uniform(0.2, 0.4)
        h = (r1 - r0) * 0.05
        pts = [(cx + (rr - h) * math.cos(aa), cy + (rr - h) * math.sin(aa)),
               (cx + (rr - h) * math.cos(aa + L), cy + (rr - h) * math.sin(aa + L)),
               (cx + (rr + h) * math.cos(aa + L), cy + (rr + h) * math.sin(aa + L)),
               (cx + (rr + h) * math.cos(aa), cy + (rr + h) * math.sin(aa))]
        fpoly(d, pts, ramp(SLICE['afflict'], 0.25 if k % 2 else 0.85))
    am = (a0 + a1) / 2
    bx, by = cx + (r1 - s * 0.6) * math.cos(am + (a1 - a0) * 0.32), cy + (r1 - s * 0.6) * math.sin(am + (a1 - a0) * 0.32)
    fpoly(d, circ(bx, by, s * 0.55, 4, 0), ramp(SLICE['afflict'], 0.3))
    fpoly(d, circ(bx, by, s * 0.44, 4, 0), ramp(SLICE['afflict'], 0.75))
    q = U(bx, by, s)
    fpoly(d, q([(-0.22, -0.2), (0.12, -0.2), (0.12, -0.02), (-0.22, -0.02)]), INK)
    fpoly(d, q([(-0.1, 0.04), (0.24, 0.04), (0.24, 0.22), (-0.1, 0.22)]), INK)


def inner_ring(d, cx, cy, r0, r1, seed, owner):
    cols = [ramp(STEEL, 0.55), ramp(HAZ, 0.5), ramp(STEEL, 0.4)] if owner == 'player' else \
        [ramp(MER, 0.45), ramp(DARK, 0.6), ramp(MER, 0.35)]
    for k in range(3):
        a0 = -math.pi / 2 + 0.4 + k * 2 * math.pi / 3 + 0.05
        a1 = a0 + 2 * math.pi / 3 - 0.1
        facet(d, polar(cx, cy, 1, 1, a0, a1, r0, r1), 6, 1, lambda u, v, i, j, kk, rc, c=cols[k]: mix(c, (0, 0, 0),
                                                                                                    0.25 * (1 - lam_at(a0 + (a1 - a0) * u))),
              (seed, 'ir', k), 0.1)


def hp_bar(d, cx, y, w, h, frac, owner, label_txt):
    st = ramp_of('#5CE1FF') if owner == 'player' else ramp_of('#FF4656')
    panel(d, skew_rect(cx - w / 2, y, w, h, 8), DARK, 0.3, ('hpbg', cx, y), nu=6, nv=1, gv=-0.3)
    fw = (w - 10) * frac
    facet(d, bil(skew_rect(cx - w / 2 + 5, y + 4, fw, h - 8, 6)), max(2, int(fw / 30)), 1,
          lambda u, v, i, j, k, rc: ramp(st, 0.5 + 0.15 * (1 - v) + rc.uniform(-0.04, 0.04)), ('hpf', cx, y), 0.3)
    text(d, cx - w / 2 + 14, y + h / 2 + 1, label_txt, max(11, h * 0.62), CREAM, anchor='lm', style='Bold')


def value_txt(d, x, y, v, size, fill, path=ANTON):
    if v is None:
        return
    text(d, x, y, str(v), size, fill, anchor='mm', style=None, path=path)


# ------------------------------------------------------------------ W-A salvaged faceted
def draw_A(img, d, cx, cy, r, slices, owner, rot, status, hp, name):
    act = active_index(slices, rot)
    # outer band + rim
    ring(d, cx, cy, r * 1.0, r * 1.12, METAL, 'A_band', n=48, fn=rim_fn(owner))
    if owner == 'boss':
        boss_spikes(d, cx, cy, r * 1.12)
    ring(d, cx, cy, r * 0.9, r * 1.0, METAL if owner == 'player' else (MER if owner == 'enemy' else BOSSR), 'A_rim',
         n=60, base=0.38)
    angs = slice_angles(slices, rot)
    for n, a0, a1, k, v in angs:
        if n == act:
            continue
        wedge(d, cx, cy, r * 0.36, r * 0.9, a0, a1, SLICE[k], ('A_sl', n), nu=max(1, int((a1 - a0) / TICK / 2)), nv=2,
              base=0.48, spread=0.16)
        line2(d, (cx + r * 0.36 * math.cos(a0), cy + r * 0.36 * math.sin(a0)),
              (cx + r * 0.9 * math.cos(a0), cy + r * 0.9 * math.sin(a0)), max(1.5, r * 0.012), INK)
    # tick teeth
    for t in range(30):
        a = -math.pi / 2 + t * TICK - rot * TICK
        p0 = (cx + r * 0.99 * math.cos(a), cy + r * 0.99 * math.sin(a))
        p1 = (cx + r * 0.93 * math.cos(a - 0.025), cy + r * 0.93 * math.sin(a - 0.025))
        p2 = (cx + r * 0.93 * math.cos(a + 0.025), cy + r * 0.93 * math.sin(a + 0.025))
        fpoly(d, [p0, p1, p2], CREAM if t % 5 == 0 else ramp(METAL, 0.75))
    # labels on the calm slices
    for n, a0, a1, k, v in angs:
        if n == act:
            continue
        am = (a0 + a1) / 2
        fg = INK if k != 'miss' else CREAM
        if status and n in status:
            corrupted(img, d, cx, cy, r * 0.36, r * 0.9, a0, a1, r * 0.12)
        glyph(d, k, cx + r * 0.76 * math.cos(am), cy + r * 0.76 * math.sin(am), r * 0.17, fg, ramp(SLICE[k], 0.5))
        value_txt(d, cx + r * 0.55 * math.cos(am), cy + r * 0.55 * math.sin(am), v, max(12, r * 0.19), fg)
    # active slice: lifted outward, brighter, cream outline
    n, a0, a1, k, v = angs[act]
    am = (a0 + a1) / 2
    ox, oy = r * 0.05 * math.cos(am), r * 0.05 * math.sin(am)
    sh = [(cx + rr * math.cos(a) + ox * 0.4 + r * 0.02, cy + rr * math.sin(a) + oy * 0.4 + r * 0.03)
          for rr, a in [(r * 0.36, a0)] + [(r * 0.96, a0 + (a1 - a0) * t / 8) for t in range(9)] + [(r * 0.36, a1)]]
    overlay(img, lambda dd: fpoly(dd, sh, (0, 0, 0, 150)))
    wedge(d, cx + ox, cy + oy, r * 0.36, r * 0.96, a0, a1, SLICE[k], ('A_act', n), nu=max(1, int((a1 - a0) / TICK / 2)),
          nv=2, base=0.62, spread=0.12)
    outl = [(cx + ox + r * 0.36 * math.cos(a0), cy + oy + r * 0.36 * math.sin(a0))] + \
           [(cx + ox + r * 0.96 * math.cos(a0 + (a1 - a0) * t / 12), cy + oy + r * 0.96 * math.sin(a0 + (a1 - a0) * t / 12))
            for t in range(13)] + [(cx + ox + r * 0.36 * math.cos(a1), cy + oy + r * 0.36 * math.sin(a1))]
    for p, q in zip(outl, outl[1:] + outl[:1]):
        line2(d, p, q, max(2, r * 0.022), CREAM)
    glyph(d, k, cx + ox + r * 0.79 * math.cos(am), cy + oy + r * 0.79 * math.sin(am), r * 0.2, INK, ramp(SLICE[k], 0.62))
    value_txt(d, cx + ox + r * 0.56 * math.cos(am), cy + oy + r * 0.56 * math.sin(am), v, max(14, r * 0.25), INK)
    if status and n in status:
        corrupted(img, d, cx + ox, cy + oy, r * 0.36, r * 0.96, a0, a1, r * 0.12)
    # inner ring + hub
    inner_ring(d, cx, cy, r * 0.27, r * 0.34, 'A', owner)
    gem(d, cx, cy, r * 0.25, r * 0.25, METAL, ('A_hub', owner), n=6, base=0.45)
    text(d, cx, cy + 1, name, max(9, r * 0.075), CREAM, anchor='mm', style='Bold Condensed')
    # pointer: big notched blade with a value window
    top, tip, w = cy - r * 1.36, cy - r * 0.84, r * 0.17
    pst = HAZ if owner == 'player' else ramp_of('#e8e2d4')
    fpoly(d, [(cx - w, top), (cx - w * 0.3, top + r * 0.06), (cx, top), (cx, tip)], ramp(pst, 0.75))
    fpoly(d, [(cx, top), (cx + w * 0.3, top + r * 0.06), (cx + w, top), (cx, tip)], ramp(pst, 0.5))
    fpoly(d, [(cx - w, top), (cx - w * 0.45, top + (tip - top) * 0.45), (cx, tip)], ramp(pst, 0.62))
    fpoly(d, [(cx + w, top), (cx + w * 0.45, top + (tip - top) * 0.45), (cx, tip)], ramp(pst, 0.32))
    wy = top + (tip - top) * 0.3
    fpoly(d, [(cx - w * 0.62, wy - r * 0.075), (cx + w * 0.62, wy - r * 0.075), (cx + w * 0.62, wy + r * 0.075),
              (cx - w * 0.62, wy + r * 0.075)], INK)
    value_txt(d, cx, wy + 1, v if v is not None else '-', max(10, r * 0.12), ramp(SLICE[k], 0.62))
    if hp:
        hp_bar(d, cx, cy + r * 1.2, r * 1.9, max(14, r * 0.15), hp[0] / hp[1], owner, f'HP {hp[0]}/{hp[1]}')


# ------------------------------------------------------------------ W-B instrument dial
def draw_B(img, d, cx, cy, r, slices, owner, rot, status, hp, name):
    act = active_index(slices, rot)
    bez = DARK if owner == 'player' else (MER if owner == 'enemy' else BOSSR)
    ring(d, cx, cy, r * 0.86, r * 1.02, bez, 'B_bez', n=40, base=0.36, spread=0.45,
         fn=(rim_fn('enemy') if owner == 'enemy' else None))
    if owner == 'boss':
        boss_spikes(d, cx, cy, r * 1.02)
    # dial face: calm
    facet(d, polar(cx, cy, 1, 1, 0, 2 * math.pi, 0, r * 0.86), 12, 2,
          lambda u, v, i, j, k, rc: ramp(STEEL, 0.2 + 0.12 * lam_at(u * 6.283) + rc.uniform(-0.02, 0.02)), 'B_face', 0.2,
          wrap_u=True)
    angs = slice_angles(slices, rot)
    for n, a0, a1, k, v in angs:
        inner = 0.7 if n == act else 0.76
        wedge(d, cx, cy, r * inner, r * 0.855, a0 + 0.012, a1 - 0.012, SLICE[k], ('B_band', n), nu=2, nv=1,
              base=0.62 if n == act else 0.5, spread=0.1)
    # printed ticks + numerals on the bezel (they turn with the wheel)
    for t in range(30):
        a = -math.pi / 2 + t * TICK - rot * TICK
        L = 0.06 if t % 5 == 0 else 0.03
        line2(d, (cx + r * 0.875 * math.cos(a), cy + r * 0.875 * math.sin(a)),
              (cx + r * (0.875 + L) * math.cos(a), cy + r * (0.875 + L) * math.sin(a)), max(1, r * (0.012 if t % 5 == 0 else 0.007)),
              CREAM)
        if t % 5 == 0 and r >= 90:
            text(d, cx + r * 0.975 * math.cos(a), cy + r * 0.975 * math.sin(a), str(t), r * 0.055, ramp_of('#b8b0a0')[4],
                 anchor='mm', style='Bold Condensed')
    # instrument needle from the centre
    nl, nw = r * 0.83, max(2, r * 0.028)
    fpoly(d, [(cx - nw, cy), (cx, cy - nl), (cx + nw, cy)], CREAM)
    fpoly(d, [(cx, cy), (cx, cy - nl), (cx + nw, cy)], ramp_of('#b8b0a0')[3])
    fpoly(d, [(cx - nw * 1.6, cy), (cx + nw * 1.6, cy), (cx, cy + r * 0.1)], ramp(SODIUM, 0.55))
    fpoly(d, [(cx - nw * 0.6, cy - nl + r * 0.12), (cx + nw * 0.6, cy - nl + r * 0.12), (cx, cy - nl)], ramp(SODIUM, 0.8))
    fpoly(d, circ(cx, cy, max(3, r * 0.045), 8), ramp(METAL, 0.7))
    # badges set inward
    for n, a0, a1, k, v in angs:
        am = (a0 + a1) / 2
        isact = n == act
        br = r * (0.155 if isact else 0.12)
        rr = r * (0.56 if not isact else 0.5)
        bx, by = cx + rr * math.cos(am), cy + rr * math.sin(am)
        fpoly(d, circ(bx, by, br * 1.12, 16), ramp(SLICE[k], 0.5 if not isact else 0.68))
        fpoly(d, circ(bx, by, br, 16), ramp(SLICE[k], 0.62) if isact else ramp(DARK, 0.2))
        fg = INK if isact else ramp(SLICE[k], 0.66)
        if k == 'miss':
            fg = CREAM if not isact else INK
        if v is None:
            glyph(d, k, bx, by, br * 1.2, fg, ramp(DARK, 0.2) if not isact else ramp(SLICE[k], 0.62))
        else:
            glyph(d, k, bx, by - br * 0.42, br * 0.78, fg, ramp(DARK, 0.2) if not isact else ramp(SLICE[k], 0.62))
            value_txt(d, bx, by + br * 0.38, v, max(9, br * 0.95), fg, path=BAHN)
        if status and n in status:
            corrupted(img, d, cx, cy, r * 0.7, r * 0.855, a0, a1, r * 0.1)
    inner_ring(d, cx, cy, r * 0.37, r * 0.41, 'B', owner)
    # hub screen with the live readout
    sw, shh = r * 0.42, r * 0.17
    sy = cy + r * 0.21
    fpoly(d, [(cx - sw / 2, sy - shh / 2), (cx + sw / 2, sy - shh / 2), (cx + sw / 2, sy + shh / 2), (cx - sw / 2, sy + shh / 2)],
          ramp(DARK, 0.05))
    n, a0, a1, k, v = angs[act]
    fpoly(d, [(cx - sw / 2 + 3, sy - shh / 2 + 3), (cx + sw / 2 - 3, sy - shh / 2 + 3), (cx + sw / 2 - 3, sy + shh / 2 - 3),
              (cx - sw / 2 + 3, sy + shh / 2 - 3)], mix(ramp(SLICE[k], 0.3), (0, 0, 0), 0.5))
    text(d, cx, sy + 1, f'{SHORT[k]} {v if v is not None else ""}'.strip(), max(8, shh * 0.62), ramp(SLICE[k], 0.7),
         anchor='mm', style=None, path=MONO)
    text(d, cx, cy - r * 0.24, name, max(8, r * 0.06), ramp_of('#b8b0a0')[4], anchor='mm', style='Bold Condensed')
    # HP arc across the bottom of the bezel
    if hp:
        frac = hp[0] / hp[1]
        a_start, a_end = math.radians(150), math.radians(30)
        st = ramp_of('#5CE1FF') if owner == 'player' else ramp_of('#FF4656')
        facet(d, polar(cx, cy, 1, 1, a_end, a_start, r * 1.06, r * 1.12), 20, 1, lambda u, v, i, j, k, rc: ramp(DARK, 0.4),
              'B_hpbg', 0.05)
        a_fill = a_start - (a_start - a_end) * frac
        facet(d, polar(cx, cy, 1, 1, a_fill, a_start, r * 1.065, r * 1.115), 20, 1,
              lambda u, v, i, j, k, rc: ramp(st, 0.55 + rc.uniform(-0.03, 0.03)), 'B_hp', 0.05)
        text(d, cx, cy + r * 1.22, f'HP {hp[0]}/{hp[1]}', max(10, r * 0.085), CREAM, anchor='mm', style='Bold')


# ------------------------------------------------------------------ W-C layered physical stack
def draw_C(img, d, cx, cy, r, slices, owner, rot, status, hp, name):
    act = active_index(slices, rot)
    # drop shadow of the whole stack
    overlay(img, lambda dd: fpoly(dd, circ(cx + r * 0.05, cy + r * 0.08, r * 1.06, 40), (0, 0, 0, 120)))
    angs = slice_angles(slices, rot)
    # slice disc (lower layer)
    for n, a0, a1, k, v in angs:
        wedge(d, cx, cy, r * 0.0, r * 0.86, a0, a1, SLICE[k], ('C_sl', n), nu=max(1, int((a1 - a0) / TICK / 2)), nv=2,
              base=0.44 if n != act else 0.58, spread=0.1)
        if status and n in status:
            corrupted(img, d, cx, cy, r * 0.25, r * 0.86, a0, a1, r * 0.1)
    # bezel shadow cast onto the disc (upper-left inner crescent)
    def shadow(dd):
        for t in range(40):
            a = 2 * math.pi * t / 40
            k = max(0.0, math.cos(a - LIGHT_ANG))
            if k <= 0:
                continue
            w = r * 0.1 * k
            pts = [(cx + r * 0.86 * math.cos(a), cy + r * 0.86 * math.sin(a)),
                   (cx + r * 0.86 * math.cos(a + 2 * math.pi / 40), cy + r * 0.86 * math.sin(a + 2 * math.pi / 40)),
                   (cx + (r * 0.86 - w) * math.cos(a + 2 * math.pi / 40), cy + (r * 0.86 - w) * math.sin(a + 2 * math.pi / 40)),
                   (cx + (r * 0.86 - w) * math.cos(a), cy + (r * 0.86 - w) * math.sin(a))]
            fpoly(dd, pts, (0, 0, 0, 140))
    overlay(img, shadow)
    # raised chips with shadows
    for n, a0, a1, k, v in angs:
        am = (a0 + a1) / 2
        isact = n == act
        s = 1.25 if isact else 1.0
        bx, by = cx + r * 0.6 * math.cos(am), cy + r * 0.6 * math.sin(am)
        cw, ch = r * 0.27 * s, r * 0.15 * s
        box = [(bx - cw / 2, by - ch / 2), (bx + cw / 2, by - ch / 2), (bx + cw / 2, by + ch / 2), (bx - cw / 2, by + ch / 2)]
        sh = [(x + r * 0.025, y + r * 0.04) for x, y in box]
        overlay(img, lambda dd, sh=sh: fpoly(dd, sh, (0, 0, 0, 150)))
        side = [(x, y + r * 0.02) for x, y in box]
        fpoly(d, side, ramp(METAL, 0.3))
        fpoly(d, box, ramp(SLICE[k], 0.7) if isact else ramp_of('#d8d2c4')[4])
        fpoly(d, [box[0], box[1], (box[1][0], box[1][1] + ch * 0.18), (box[0][0], box[0][1] + ch * 0.18)],
              ramp(SLICE[k], 0.5))
        fg = INK
        if v is None:
            glyph(d, k, bx, by + ch * 0.06, ch * 0.8, fg, ramp_of('#d8d2c4')[4])
        else:
            glyph(d, k, bx - cw * 0.24, by + ch * 0.08, ch * 0.66, fg, ramp_of('#d8d2c4')[4] if not isact else ramp(SLICE[k], 0.7))
            value_txt(d, bx + cw * 0.2, by + ch * 0.08, v, max(9, ch * 0.78), fg)
    # machined bezel (upper layer)
    bez = METAL if owner == 'player' else (MER if owner == 'enemy' else BOSSR)
    ring(d, cx, cy, r * 0.86, r * 1.04, bez, 'C_bez', n=60, base=0.48, spread=0.6,
         fn=(rim_fn('enemy') if owner == 'enemy' else None))
    ring(d, cx, cy, r * 0.86, r * 0.89, bez, 'C_lip', n=60, base=0.75, spread=-0.6)
    for t in range(30):
        a = -math.pi / 2 + t * TICK - rot * TICK
        p0 = (cx + r * 1.04 * math.cos(a), cy + r * 1.04 * math.sin(a))
        p1 = (cx + r * 0.98 * math.cos(a - 0.03), cy + r * 0.98 * math.sin(a - 0.03))
        p2 = (cx + r * 0.98 * math.cos(a + 0.03), cy + r * 0.98 * math.sin(a + 0.03))
        fpoly(d, [p0, p1, p2], ramp(METAL, 0.15) if t % 5 else CREAM)
    if owner == 'boss':
        boss_spikes(d, cx, cy, r * 1.04)
    # glass dome sheen
    def glass(dd):
        pts = [(cx + r * 0.84 * math.cos(a), cy + r * 0.84 * math.sin(a)) for a in
               [math.radians(x) for x in range(150, 291, 10)]]
        pts += [(cx + r * 0.6 * math.cos(a) - r * 0.06, cy + r * 0.6 * math.sin(a) - r * 0.08) for a in
                [math.radians(x) for x in range(290, 149, -10)]]
        fpoly(dd, pts, (255, 255, 255, 34))
        fpoly(dd, [(cx - r * 0.6, cy - r * 0.42), (cx - r * 0.5, cy - r * 0.56), (cx - r * 0.44, cy - r * 0.52),
                   (cx - r * 0.55, cy - r * 0.38)], (255, 255, 255, 90))
        fpoly(dd, [(cx + r * 0.42, cy + r * 0.56), (cx + r * 0.62, cy + r * 0.3), (cx + r * 0.66, cy + r * 0.34),
                   (cx + r * 0.46, cy + r * 0.6)], (255, 255, 255, 40))
    overlay(img, glass)
    # physical needle with counterweight + cast shadow
    nl, nw = r * 0.9, max(2.5, r * 0.04)

    def needle(dd, ox, oy, colA, colB, colC):
        fpoly(dd, [(cx + ox - nw, cy + oy), (cx + ox, cy + oy - nl), (cx + ox + nw, cy + oy)], colA)
        fpoly(dd, [(cx + ox, cy + oy), (cx + ox, cy + oy - nl), (cx + ox + nw, cy + oy)], colB)
        fpoly(dd, [(cx + ox - nw * 0.9, cy + oy), (cx + ox + nw * 0.9, cy + oy), (cx + ox + nw * 0.6, cy + oy + r * 0.2),
                   (cx + ox - nw * 0.6, cy + oy + r * 0.2)], colB)
        fpoly(dd, circ(cx + ox, cy + oy + r * 0.24, r * 0.075, 8), colC)
    overlay(img, lambda dd: needle(dd, r * 0.035, r * 0.055, (0, 0, 0, 130), (0, 0, 0, 130), (0, 0, 0, 130)))
    needle(d, 0, 0, ramp_of('#e8e2d4')[4], ramp_of('#e8e2d4')[2], ramp(METAL, 0.55))
    fpoly(d, [(cx - nw * 0.8, cy - nl + r * 0.14), (cx + nw * 0.8, cy - nl + r * 0.14), (cx, cy - nl)],
          ramp_of('#FF4656')[4])
    gem(d, cx, cy, r * 0.11, r * 0.11, METAL, ('C_cap', owner), n=6, base=0.55)
    # name plate + HP plate under the stack
    text(d, cx, cy + r * 1.13, name, max(9, r * 0.08), CREAM, anchor='mm', style='Bold Condensed')
    if hp:
        n_led = 10
        on = round(hp[0] / hp[1] * n_led)
        pw = r * 1.4
        fpoly(d, [(cx - pw / 2, cy + r * 1.22), (cx + pw / 2, cy + r * 1.22), (cx + pw / 2, cy + r * 1.36), (cx - pw / 2, cy + r * 1.36)],
              ramp(METAL, 0.35))
        st = ramp_of('#5CE1FF') if owner == 'player' else ramp_of('#FF4656')
        for kk in range(n_led):
            x0 = cx - pw / 2 + 6 + kk * (pw - 12) / n_led
            fpoly(d, [(x0 + 2, cy + r * 1.245), (x0 + (pw - 12) / n_led - 2, cy + r * 1.245),
                      (x0 + (pw - 12) / n_led - 2, cy + r * 1.335), (x0 + 2, cy + r * 1.335)],
                  ramp(st, 0.6) if kk < on else ramp(DARK, 0.3))
        text(d, cx + pw / 2 + 8, cy + r * 1.29, f'{hp[0]}', max(10, r * 0.1), CREAM, anchor='lm', style='Bold')


# ------------------------------------------------------------------ W-D segmented ring + sticker values
_STICKER_CACHE = {}


def value_sticker(k, v, big=False):
    key = (k, v, big)
    if key in _STICKER_CACHE:
        return _STICKER_CACHE[key]
    S = SL.SS
    D = 64
    P = 30 * S
    Wd = int(D * S) + 2 * P
    art = Image.new('RGBA', (Wd, Wd), (0, 0, 0, 0))
    dr = ImageDraw.Draw(art)
    c = Wd / 2
    rr = D * S / 2
    col = tuple(hexc(SLICE_HEX[k]))
    dr.rounded_rectangle([c - rr, c - rr, c + rr, c + rr], radius=int(12 * S), fill=SL.INK + (255,))
    dr.rounded_rectangle([c - rr + 3 * S, c - rr + 3 * S, c + rr - 3 * S, c + rr - 3 * S], radius=int(10 * S),
                         fill=col + (255,))
    # glyph in ink on the top half, value in Anton below (sticker coords are already SS)
    # lowpoly draws in 1x units x SS; the sticker canvas is also SS=2, so 1x = pixel / 2
    assert SS == S
    if v is None:
        glyph(dr, k, c / S, c / S, D * 0.62, SL.INK + (255,), col + (255,))
    else:
        glyph(dr, k, c / S, (c - rr * 0.44) / S, D * 0.36, SL.INK + (255,), col + (255,))
    if v is not None:
        SL.text_img(dr, (c, c + rr * 0.36), str(v), SL.ANTON, D * 0.56, SL.INK + (255,))
    sd = SL.build_sticker(art, border=6, material='gloss', close=4, gloss_pos=0.3, seed=hash(key) % 997)
    _STICKER_CACHE[key] = sd
    return sd


def arrow_sticker():
    if 'arrow' in _STICKER_CACHE:
        return _STICKER_CACHE['arrow']
    S = SL.SS
    P = 30 * S
    w, h = 70 * S + 2 * P, 70 * S + 2 * P
    art = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(art)
    x0, y0 = P, P
    pts = [(x0 + 10 * S, y0), (x0 + 60 * S, y0), (x0 + 60 * S, y0 + 34 * S), (x0 + 70 * S, y0 + 34 * S), (x0 + 35 * S, y0 + 70 * S),
           (x0, y0 + 34 * S), (x0 + 10 * S, y0 + 34 * S)]
    dr.polygon(pts, fill=SL.INK + (255,))
    inner = [(x0 + 14 * S, y0 + 4 * S), (x0 + 56 * S, y0 + 4 * S), (x0 + 56 * S, y0 + 38 * S), (x0 + 62 * S, y0 + 38 * S),
             (x0 + 35 * S, y0 + 64 * S), (x0 + 8 * S, y0 + 38 * S), (x0 + 14 * S, y0 + 38 * S)]
    dr.polygon(inner, fill=SL.YELLOW + (255,))
    SL.text_img(dr, (x0 + 35 * S, y0 + 20 * S), 'NOW', SL.ANTON, 20, SL.INK + (255,))
    sd = SL.build_sticker(art, border=7, material='gloss', close=5, gloss_pos=0.3, seed=77)
    _STICKER_CACHE['arrow'] = sd
    return sd


def draw_D(img, d, cx, cy, r, slices, owner, rot, status, hp, name):
    act = active_index(slices, rot)
    angs = slice_angles(slices, rot)
    lip = METAL if owner == 'player' else (MER if owner == 'enemy' else BOSSR)
    ring(d, cx, cy, r * 0.96, r * 1.03, lip, 'D_lip', n=48, base=0.42, fn=(rim_fn('enemy') if owner == 'enemy' else None))
    if owner == 'boss':
        boss_spikes(d, cx, cy, r * 1.03)
    gap = TICK * 0.18
    for n, a0, a1, k, v in angs:
        isact = n == act
        r1 = r * (1.0 if isact else 0.93)
        r0 = r * (0.58 if isact else 0.62)
        wedge(d, cx, cy, r0, r1, a0 + gap, a1 - gap, SLICE[k], ('D_seg', n), nu=max(1, int((a1 - a0) / TICK / 2)), nv=1,
              base=0.62 if isact else 0.46, spread=0.12)
        if isact:
            for rr in (r0, r1):
                pts = [(cx + rr * math.cos(a0 + gap + (a1 - a0 - 2 * gap) * t / 10),
                        cy + rr * math.sin(a0 + gap + (a1 - a0 - 2 * gap) * t / 10)) for t in range(11)]
                for p, q in zip(pts, pts[1:]):
                    line2(d, p, q, max(2, r * 0.02), CREAM)
        if status and n in status:
            corrupted(img, d, cx, cy, r0, r1, a0 + gap, a1 - gap, r * 0.09)
    # open centre: hub disc, HP arc, name, inner ring
    facet(d, polar(cx, cy, 1, 1, 0, 2 * math.pi, 0, r * 0.5), 10, 2,
          lambda u, v, i, j, k, rc: ramp(DARK, 0.3 + 0.15 * lam_at(u * 6.283) + rc.uniform(-0.02, 0.02)), 'D_hub', 0.2,
          wrap_u=True)
    inner_ring(d, cx, cy, r * 0.5, r * 0.56, 'D', owner)
    if hp:
        frac = hp[0] / hp[1]
        st = ramp_of('#5CE1FF') if owner == 'player' else ramp_of('#FF4656')
        a0h = -math.pi / 2 - math.pi * 0.8
        facet(d, polar(cx, cy, 1, 1, a0h, a0h + 2 * math.pi * 0.8, r * 0.4, r * 0.45), 24, 1,
              lambda u, v, i, j, k, rc: ramp(DARK, 0.55), 'D_hpbg', 0.05)
        facet(d, polar(cx, cy, 1, 1, a0h, a0h + 2 * math.pi * 0.8 * frac, r * 0.4, r * 0.45), 24, 1,
              lambda u, v, i, j, k, rc: ramp(st, 0.56), 'D_hp', 0.05)
        text(d, cx, cy + r * 0.04, str(hp[0]), max(12, r * 0.24), CREAM, anchor='mm', style=None, path=ANTON)
        text(d, cx, cy + r * 0.24, 'HP', max(8, r * 0.07), ramp_of('#b8b0a0')[4], anchor='mm', style='Bold')
    text(d, cx, cy - r * 0.24, name, max(8, r * 0.075), CREAM, anchor='mm', style='Bold Condensed')
    # sticker placements (applied after downsampling)
    stick = []
    for n, a0, a1, k, v in angs:
        isact = n == act
        am = (a0 + a1) / 2
        rr = r * (0.8 if isact else 0.775)
        sc = r * (0.34 if isact else 0.26) / 64
        jit = ((hsh(n, 3) - 0.5) * 14)
        stick.append((value_sticker(k, v), cx + rr * math.cos(am), cy + rr * math.sin(am), jit, sc))
    stick.append((arrow_sticker(), cx, cy - r * 1.17, 0, r * 0.32 / 70))
    return stick


DRAW = {'A': draw_A, 'B': draw_B, 'C': draw_C, 'D': draw_D}
NAMES = {'A': ('W-A', 'SALVAGED FACETED'), 'B': ('W-B', 'INSTRUMENT DIAL'), 'C': ('W-C', 'LAYERED PHYSICAL STACK'),
         'D': ('W-D', 'SEGMENTED RING + STICKER VALUES')}


def render_wheel(ver, r, slices=PLAYER, owner='player', rot=0.0, status=None, hp=(36, 50), name='CELL-9'):
    Wl, Hl = int(2.6 * r + 60), int(2.95 * r + 70)
    cx, cy = Wl / 2, 1.45 * r + 30
    img, d = new_layer(Wl, Hl)
    stick = DRAW[ver](img, d, cx, cy, r, slices, owner, rot, status, hp, name)
    lay = to1x(img)
    if stick:
        for sd, x, y, ang, sc in stick:
            lay = SL.place(lay, sd, x, y, angle=ang, scale=sc, shadow=0.8 if sc > 0.3 else 0.5)
    lay.info['center'] = (cx, cy)
    return lay


def paste_wheel(base, lay, cx, cy):
    ox, oy = lay.info['center']
    base.alpha_composite(lay, (int(cx - ox), int(cy - oy)))


def wheel_sheet(ver):
    base = sheet_bg()
    d1 = ImageDraw.Draw(base)
    code, nm = NAMES[ver]
    title(d1, code, nm, 'judge first: which slice is under the pointer, and its value')
    hero = render_wheel(ver, 200, PLAYER, 'player', rot=2.5, status={5})
    paste_wheel(base, hero, 330, 470)
    label(d1, 330, 790, '1  PLAYER  r=200  (one slice CORRUPTED)', 17)
    en = render_wheel(ver, 165, ENEMY, 'enemy', rot=3.0, hp=(33, 60), name='VANTA ICE')
    paste_wheel(base, en, 830, 450)
    label(d1, 830, 790, '2  ENEMY  MERIDIAN  r=165', 17)
    # greyscale copy
    g = grey(render_wheel(ver, 120, PLAYER, 'player', rot=2.5, status={5}))
    g.info['center'] = (g.width / 2, 1.45 * 120 + 30)
    paste_wheel(base, g, 1240, 340)
    label(d1, 1240, 600, '4  GREYSCALE', 17)
    # zooms: under-pointer highlight + corrupted slice
    hx, hy = hero.info['center']
    z1 = hero.crop((int(hx - 150), int(hy - 290), int(hx + 150), int(hy - 40)))
    z1 = z1.resize((int(z1.width * 0.95), int(z1.height * 0.95)), Image.LANCZOS)
    frame_panel(base, z1, 1660, 220, '6  SLICE UNDER POINTER')
    # corrupted slice is index 5 -> find its mid-angle on the hero wheel
    for n, a0, a1, k, v in slice_angles(PLAYER, 2.5):
        if n == 5:
            am = (a0 + a1) / 2
    zx, zy = hx + 200 * 0.62 * math.cos(am), hy + 200 * 0.62 * math.sin(am)
    z2 = hero.crop((int(zx - 120), int(zy - 100), int(zx + 120), int(zy + 100)))
    frame_panel(base, z2, 1660, 560, '5  CORRUPTED SLICE')
    # small size r=60
    for k, (sl, own, nm2, rot) in enumerate(((PLAYER, 'player', 'CELL-9', 2.5), (ENEMY, 'enemy', 'ICE', 3.0),
                                             (BOSS, 'boss', 'BOSS', 2.0))):
        sm = render_wheel(ver, 60, sl, own, rot=rot, hp=(36, 50) if own == 'player' else (40, 60), name=nm2)
        paste_wheel(base, sm, 1150 + k * 170, 830)
    label(d1, 1320, 1010, '3  SMALL  r=60  (player / Meridian / boss)', 17)
    for k, (sl, own, nm2, rot) in enumerate(((PLAYER, 'player', 'CELL-9', 2.5),)):
        sm = grey(render_wheel(ver, 60, sl, own, rot=rot, name=nm2))
        sm.info['center'] = (sm.width / 2, 1.45 * 60 + 30)
        paste_wheel(base, sm, 1720, 830)
    label(d1, 1720, 1010, 'r=60 grey', 17)
    out = os.path.join(OUT, f'wheel_{ver}.png')
    base.convert('RGB').save(out, optimize=True)
    print('wrote', os.path.basename(out))
    return hero


if __name__ == '__main__':
    import sys as _s
    for v in (_s.argv[1:] or ['A', 'B', 'C', 'D']):
        wheel_sheet(v)
