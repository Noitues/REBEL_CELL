"""OUTER RINGS: ring tags (+nowords), future wave arcs, their unit pips, climax hazard ticks, wave tags (+nowords)."""
import sys, math
sys.dont_write_bytecode = True
from e10lib import *
import e8lib as E8
import cv_board as CB
from o_sched import arc_text2
from o_ground import BEZEL_HI

AMB = (255, 176, 0)       # CRT_AMBER token: caution / hazard (plan yellow is the player's plan only)
ORGC = (255, 140, 26)
REDC = (255, 68, 51)


def tally_bars(L, x, y, n, col, h=11, pitch=5.2, w=3.0, keyline=True):
    """tally in groups of 5: n bars (the 5th would be a strike; waves go to 6 so 5 + 1 with a gap)"""
    grp = [min(5, n), max(0, n - 5)]
    xx = x
    tot = n * pitch + (6 if n > 5 else 0)
    xx = x - tot / 2 + pitch / 2
    for gi, g in enumerate(grp):
        for i in range(g):
            L.rect([xx - w / 2 - 0.9, y - h / 2 - 0.9, xx + w / 2 + 0.9, y + h / 2 + 0.9], fill=INK, r=1)
            L.rect([xx - w / 2, y - h / 2, xx + w / 2, y + h / 2], fill=col, r=1)
            xx += pitch
        xx += 6


def plus_glyph(L, x, y, col, s=5, w=2.8):
    L.line([(x - s, y), (x + s, y)], INK, w + 2.4)
    L.line([(x, y - s), (x, y + s)], INK, w + 2.4)
    L.line([(x - s, y), (x + s, y)], col, w)
    L.line([(x, y - s), (x, y + s)], col, w)


def tag_words(d, wave):
    """(depth word, wave word)"""
    return LANE[d]['name'], ('W%d' % (wave + 1)) if wave >= 0 else None


def lane_swatch(L, x0, x1, y, d, w=3.0):
    lane = LANE[d]
    L.line([(x0, y), (x1, y)], INK, w + 3.0)
    L.line([(x0, y), (x1, y)], lane['col'], w, dash=lane['dash'])


# ----------------------------------------------------------------------------- ring_tags
def ring_tags(L, f, opt):
    words = NOW['words']
    for d in range(3):
        ri, ro = CB.ring_geom(d)
        w_ = f['rings_wave'][d]
        lane = LANE[d]
        depth, wv = tag_words(d, w_)
        if opt == 'cur':
            x, y = ppx(C, (ri + ro) / 2, 30)
            s = lane['name'] + (' W%d' % (w_ + 1) if w_ >= 0 else '')
            wd = L.tw(s, 17, 'anton') + 14
            L.rect([x - wd / 2, y - 12, x + wd / 2, y + 12], fill=(8, 10, 18, 245), outline=lane['col'], w=2, r=6)
            L.text((x, y + 1), s, 17, 'anton', fill=lane['col'], anchor='mm')
            continue
        if opt == 'A':       # pennant: 20 px Anton on a 26 px tag, hung on the OUTER corner of its ring at the 30 deg spoke (clear of tokens, guns and the HP row), lane-style bar on the tag's lower edge
            x, y = ppx(C, ro - 17, 30)
            if words:
                s = depth + ((' ' + wv) if wv else '')
                wd = L.tw(s.replace('+', ''), 20, 'anton') + 16 + (10 if depth.startswith('+') else 0)
                L.rect([x - wd / 2, y - 13, x + wd / 2, y + 13], fill=(8, 10, 18, 250), outline=lane['col'], w=2.4, r=6)
                tx0 = x - wd / 2 + 8
                if depth.startswith('+'):
                    plus_glyph(L, tx0 + 3, y, lane['col'], 4.2, 2.4)
                    tx0 += 9
                    txt = depth[1:] + ((' ' + wv) if wv else '')
                else:
                    txt = s
                L.text((tx0, y + 1), txt, 20, 'anton', fill=lane['col'], anchor='lm', stroke=1.4)
            else:            # nowords A: lane-style swatch + wave pips (tally), same footprint
                wd = 44
                L.rect([x - wd / 2, y - 13, x + wd / 2, y + 13], fill=(8, 10, 18, 250), outline=INK, w=2.4, r=6)
                lane_swatch(L, x - 16, x + 16, y - 5, d)
                tally_bars(L, x, y + 6, w_ + 1 if w_ >= 0 else 0, (244, 247, 252), h=8, pitch=5.4, w=2.6)
        elif opt == 'B':     # arc words: the ring's name engraved along its outer edge at 30 deg in the lane colour with an ink keyline (no box, no straddling), the same curved-text language as the bezel
            r_t = ro - 12
            s = depth + ((' ' + wv) if wv else '')
            if words:
                arc_text2(L, r_t, 30, s, 20, lane['col'], 'anton', keyline=2.2, track=1.05)
            else:            # nowords B: a curved lane-style swatch of the same length, wave pips under it
                ln = 44
                half = ln / 2 / r_t * 57.3
                pts = L.arc_pts(C, r_t, 30 - half, 30 + half, 8)
                L.line(pts, INK, 7.0)
                L.line(pts, lane['col'], 3.4, dash=lane['dash'])
                x, y = ppx(C, r_t - 9, 30)
                tally_bars(L, x, y, w_ + 1 if w_ >= 0 else 0, (244, 247, 252), h=7, pitch=5.0, w=2.4)
        else:                # C handled below (one object)
            pass
    if opt == 'C':           # one radial strip on the 30 deg spoke: three lane-outlined segments (NOW / +1 / +2) in one object, wave words inside
        ang = 30
        th = math.radians(ang)
        ux, uy = math.sin(th), -math.cos(th)        # outward
        tx, ty = math.cos(th), math.sin(th)
        wid = 30
        for d in range(3):
            ri, ro = CB.ring_geom(d)
            lane = LANE[d]
            w_ = f['rings_wave'][d]
            depth, wv = tag_words(d, w_)
            r0, r1 = ri + 6, ro - 6
            def q(r, t):
                x, y = ppx(C, r, ang)
                return (x + tx * t, y + ty * t)
            pts = [q(r0, -wid / 2), q(r1, -wid / 2), q(r1, wid / 2), q(r0, wid / 2)]
            L.poly(pts, fill=(8, 10, 18, 245), outline=INK, w=5.4)
            L.line(pts + [pts[0]], lane['col'], 2.4, dash=lane['dash'])
            xm, ym = ppx(C, (ri + ro) / 2, ang)
            if words:
                L.text((xm, ym - 10), depth if not depth.startswith('+') else depth, 20, 'anton', fill=lane['col'], anchor='mm', stroke=1.3)
                if wv:
                    L.text((xm, ym + 11), wv, 20, 'anton', fill=WHITE, anchor='mm', stroke=1.3)
            else:
                lane_swatch(L, xm - 11, xm + 11, ym - 8, d)
                tally_bars(L, xm, ym + 8, w_ + 1 if w_ >= 0 else 0, (244, 247, 252), h=9, pitch=5.4, w=2.6)


# ----------------------------------------------------------------------------- future waves
WAVE_ORDER = None


def fut_geom(opt, arcs):
    """list of dict(wave, r, a0, extent, col, lw, alpha) in draw order"""
    fut = [a for a in arcs if a['state'] == 'future']
    out = []
    S = E8.ARC_START
    if opt == 'cur':
        r = 492
        for a in fut:
            out.append(dict(a=a, r=r, a0=S, ext=359, lw=3.0, alpha=235))
            r += 17
    elif opt == 'A':
        r = 498
        for a in fut:
            out.append(dict(a=a, r=r, a0=S, ext=359, lw=1.8, alpha=170))
            r += 8
    elif opt == 'B':        # tape: waves packed end to end on as few rings as fit (a ring holds 360 deg of unit width)
        rings = [[498, 0.0], [512, 0.0]]
        for a in fut:
            ext = sum(60 * w for k, w in a['units'])
            for rg in rings:
                if rg[1] + ext <= 360.01:
                    out.append(dict(a=a, r=rg[0], a0=S + rg[1], ext=ext, lw=2.2, alpha=215))
                    rg[1] += ext
                    break
    else:                   # C: three honest rings at 12 px pitch, fading out near the screen frame instead of touching it
        r = 500
        for a in fut:
            out.append(dict(a=a, r=r, a0=S, ext=359, lw=2.0, alpha=200, fade=True))
            r += 12
    return out


def fade_alpha(x, y):
    m = min(x, y, W - x, H - y)
    return max(0.0, min(1.0, (m - 12) / 46.0))


def line_fade(L, pts, col, w, alpha):
    for p0, p1 in zip(pts[:-1], pts[1:]):
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        a = int(alpha * fade_alpha(mx, my))
        if a > 4:
            L.line([p0, p1], tuple(col) + (a,), w)


def haz_ticks(L, g, opt, col_w):
    r = g['r']
    S = g['a0']
    if opt == 'cur':
        for k in range(int(S), int(S) + 360, 14):
            L.line([ppx(C, r - 5, k), ppx(C, r + 5, k + 6)], (255, 226, 0, 190), 2.4)
    elif opt == 'A':       # hazard band: amber and ink 45 degree stripes, an 8 px band riding the arc (reads as tape, not as scratches)
        n = 120
        for i in range(n):
            a0 = S + i * 3.0
            if i % 2 == 0:
                pts = [ppx(C, r - 4, a0), ppx(C, r + 4, a0 + 1.6), ppx(C, r + 4, a0 + 3.0), ppx(C, r - 4, a0 + 1.4)]
                L.poly(pts, fill=AMB)
        L.line(L.arc_pts(C, r - 4.4, S, S + 359, 120), INK, 1.4)
        L.line(L.arc_pts(C, r + 4.4, S, S + 359, 120), INK, 1.4)
    elif opt == 'B':       # chunky ticks: 3 px amber slashes at 18 deg pitch with ink keyline, 12 px long: sparse, deliberate
        for k in range(int(S), int(S) + 360, 12):
            p = [ppx(C, r - 6.5, k), ppx(C, r + 6.5, k + 5)]
            L.line(p, INK, 6.0)
            L.line(p, AMB, 3.0)
    else:                  # C: monochrome hazard: red/ink stripes inside the arc band (harm only; no new hue)
        n = 120
        for i in range(n):
            a0 = S + i * 3.0
            if i % 2 == 0:
                pts = [ppx(C, r - 4, a0), ppx(C, r + 4, a0 + 1.6), ppx(C, r + 4, a0 + 3.0), ppx(C, r - 4, a0 + 1.4)]
                L.poly(pts, fill=REDC)
        L.line(L.arc_pts(C, r - 4.4, S, S + 359, 120), INK, 1.4)
        L.line(L.arc_pts(C, r + 4.4, S, S + 359, 120), INK, 1.4)


def unit_pips(L, g, opt, sel_fut):
    r = g['r']
    a = g['a']
    S = g['a0']
    ang = S
    for (kind, w) in a['units']:
        a1 = ang + 60 * w
        kc = KCOL.get(kind, WHITE)
        m = (ang + a1) / 2
        x, y = ppx(C, r, m)
        fa = fade_alpha(x, y) if g.get('fade') else 1.0
        if opt == 'cur':
            L.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(10, 12, 22, 240), outline=kc, w=2)
            L.glyph(KIND[kind][1], 13, (x, y), WHITE)
            for q in range(1, w):
                x2, y2 = ppx(C, r, ang + 60 * q)
                L.ellipse([x2 - 3, y2 - 3, x2 + 3, y2 + 3], fill=WHITE + (200,))
        elif opt == 'A':     # 26 px token disc (glyph 18, kind ring) + one ink-and-pale bar tick across the arc at every interior sector boundary
            for q in range(1, w):
                p0 = ppx(C, r - 8, ang + 60 * q)
                p1 = ppx(C, r + 8, ang + 60 * q)
                L.line([p0, p1], INK, 5.0)
                L.line([p0, p1], (232, 238, 250), 2.4)
            L.ellipse([x - 13.6, y - 13.6, x + 13.6, y + 13.6], fill=INK)
            L.ellipse([x - 12.2, y - 12.2, x + 12.2, y + 12.2], fill=(10, 12, 22, 250), outline=kc, w=2.2)
            L.glyph(KIND[kind][1], 18, (x, y), WHITE)
        elif opt == 'B':     # extent bar: the unit's width drawn as a 7 px thick bar over its own sectors (kind colour, ink edge); disc 24 px at the bar's start
            ext = ang + 60 * w
            ptsb = L.band(C, r - 2.4, r + 2.4, ang + 3.0, ext - 3.0)
            L.poly(ptsb, fill=tuple(int(v * 0.8) for v in kc), outline=INK, w=2.0)
            xs, ys = ppx(C, r, ang + 11)
            L.ellipse([xs - 12.6, ys - 12.6, xs + 12.6, ys + 12.6], fill=INK)
            L.ellipse([xs - 11.2, ys - 11.2, xs + 11.2, ys + 11.2], fill=(10, 12, 22, 250), outline=kc, w=2.0)
            L.glyph(KIND[kind][1], 17, (xs, ys), WHITE)
        else:                # C: 28 px disc with the width as a tally of white bars under it (the bill's tally language), no marks on the arc
            L.ellipse([x - 14.6, y - 14.6, x + 14.6, y + 14.6], fill=INK)
            L.ellipse([x - 13.2, y - 13.2, x + 13.2, y + 13.2], fill=(10, 12, 22, 250), outline=kc, w=2.2)
            L.glyph(KIND[kind][1], 20, (x, y), WHITE)
            xb, yb = ppx(C, r + 22 if r < 505 else r - 22, m)
            tally_bars(L, xb, yb, w, (244, 247, 252), h=8, pitch=5.0, w=2.4) if w > 1 else None
        ang = a1


def wave_tag_pos(g, opt, i):
    r, S = g['r'], g['a0']
    if opt == 'cur':
        return ppx(C, r, E8.ARC_START - 3.6 - 3.2 * i)
    if opt == 'A':      # on the arc at its start, staggered along the arc direction by wave (a short ladder along travel, not a radial staircase)
        return ppx(C, r, S - 2.0 - 7.5 * i)
    if opt == 'B':      # at the start of the tape segment, nudged back a half tag; the 3rd (other ring) is shifted along so it never stacks on the first
        return ppx(C, r, S - 3.4 - 6.0 * i)
    return ppx(C, r, S - 3.0 - 13.0 * i)


def wave_tag(L, g, opt, i, col):
    if opt == 'cur':
        x, y = wave_tag_pos(g, 'cur', i)
        lab = 'W%d' % (g['a']['wave'] + 1)
        if NOW['words']:
            L.rect([x - 22, y - 11, x + 22, y + 11], fill=(8, 10, 18, 255), outline=col, w=2, r=5)
            L.text((x, y + 1), lab, 16, 'mono', fill=col)
        return
    x, y = wave_tag_pos(g, opt, i)
    n = g['a']['wave'] + 1
    if NOW['words']:
        lab = 'W%d' % n
        if opt == 'A':     # mono 18 chip in the ring-tag family: 24 px tall, 6 radius, wave colour outline 2.2
            L.rect([x - 20, y - 12, x + 20, y + 12], fill=(8, 10, 18, 255), outline=col, w=2.2, r=6)
            L.text((x, y + 1), lab, 18, 'mono', fill=col, stroke=0)
        elif opt == 'B':   # Anton 20 with keyline on the tape itself, no box: same face as the ring tags, so they read as one family
            L.text((x, y + 1), lab, 20, 'anton', fill=col, anchor='mm', stroke=2.2)
        else:              # C: flag: a small pennant with the wave word on a dark pointed flag whose point touches the arc
            th = 0
            L.poly([(x - 21, y - 12), (x + 15, y - 12), (x + 22, y), (x + 15, y + 12), (x - 21, y + 12)], fill=(8, 10, 18, 255), outline=col, w=2.2)
            L.text((x - 2, y + 1), lab, 18, 'mono', fill=col)
    else:                  # nowords: tally of n bars (W4 = 4 bars, W5 = 5, W6 = 5+1) in the wave colour on an ink plate
        wd = n * 5.2 + (6 if n > 5 else 0) + 14
        L.rect([x - wd / 2, y - 11, x + wd / 2, y + 11], fill=(8, 10, 18, 255), outline=col, w=2.0, r=5)
        tally_bars(L, x, y, n, col, h=11, pitch=5.2, w=3.0)


def future(L, f, arcs, sel):
    fo = sel.get('fut', 'cur')
    geoms = fut_geom(fo, arcs)
    for i, g in enumerate(geoms):
        a = g['a']
        col_w = REDC if a.get('climax') else ORGC
        if g.get('fade'):
            for sg in range(0, 360, 6):
                pts = L.arc_pts(C, g['r'], g['a0'] + sg, g['a0'] + min(g['ext'], sg + 7), 3)
                line_fade(L, pts, col_w, g['lw'], g['alpha'])
        else:
            L.line(L.arc_pts(C, g['r'], g['a0'], g['a0'] + g['ext'], max(8, int(g['ext'] / 3))), col_w + (g['alpha'],), g['lw'])
            if fo == 'B':
                for aa_ in (g['a0'], g['a0'] + g['ext']):
                    L.line([ppx(C, g['r'] - 5, aa_), ppx(C, g['r'] + 5, aa_)], col_w, 2.4)
        unit_pips(L, g, sel.get('pips', 'cur'), fo)
        if a.get('climax'):
            haz_ticks(L, g, sel.get('haz', 'cur'), col_w)
        wave_tag(L, g, sel.get('wtag', 'cur'), i, col_w)
