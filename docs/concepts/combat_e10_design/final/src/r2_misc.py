"""R2 outer_rings: ring_tags (+nowords, + LATENT ring_tag_no_wave, + the twist anchor), future_wave_arcs, wave_arc_unit_pips, climax_hazard_ticks, wave_tags (+nowords).
Selectors 'P' pick, 'V' variant."""
import sys, math
sys.dont_write_bytecode = True
from e10lib import *
import e8lib as E8
import cv_board as CB
from o_misc import tally_bars, plus_glyph, tag_words, lane_swatch
from o_ground import BEZEL_HI
import r2_glyphs as GL

AMB = (255, 176, 0)
ORGC = (255, 140, 26)
HARM = (255, 68, 51)
HARM_UP = __import__("asm_tokens").HARM_UP      # fix 2
TAPE_R = [490.0, 499.0, 508.0]      # two tape rings + one hairline ring; outermost edge 511.4 keeps the 24 px margin (left edge x = 536 - r)
S0 = E8.ARC_START


# ----------------------------------------------------------------------------- ring_tags
def tag_geom(L, d, w_, opt):
    ri, ro = CB.ring_geom(d)
    x, y = ppx(C, ro - 17, 30)
    depth, wv = tag_words(d, w_)
    if NOW['words']:
        s = depth + ((' ' + wv) if wv else '')
        wd = L.tw(s.replace('+', ''), 20, 'anton') + 18 + (10 if depth.startswith('+') else 0)
    else:
        wd = 44
    return x, y, wd, depth, wv


def tag_anchor(L, f, d):
    """anchor for actions' twist badge: (x_right_edge, y) of ring d's tag"""
    x, y, wd, _, _ = tag_geom(L, d, f['rings_wave'][d], 'P')
    return x + wd / 2, y


def ring_tags(L, f, opt):
    for d in range(3):
        w_ = f['rings_wave'][d]
        lane = dict(LANE[d], col=HARM_UP) if d == 0 else LANE[d]      # fix 2: the NOW W1 tag one value step up
        x, y, wd, depth, wv = tag_geom(L, d, w_, opt)
        if NOW['words']:
            if opt == 'P':
                L.rect([x - wd / 2, y - 13, x + wd / 2, y + 13], fill=(8, 10, 18, 250), outline=lane['col'], w=2.4, r=6)
            else:   # V: pennant, pointed on the clockwise end
                pts = [(x - wd / 2, y - 13), (x + wd / 2 - 6, y - 13), (x + wd / 2 + 4, y), (x + wd / 2 - 6, y + 13), (x - wd / 2, y + 13)]
                L.poly(pts, fill=(8, 10, 18, 250), outline=INK, w=4.6)
                L.line(pts + [pts[0]], lane['col'], 2.4)
            tx0 = x - wd / 2 + 9
            if depth.startswith('+'):
                plus_glyph(L, tx0 + 3, y, lane['col'], 4.2, 2.4)
                tx0 += 10
                txt = depth[1:] + ((' ' + wv) if wv else '')
            else:
                txt = depth + ((' ' + wv) if wv else '')
            L.text((tx0, y + 1), txt, 20, 'anton', fill=lane['col'], anchor='lm', stroke=1.4)
        else:
            L.rect([x - wd / 2, y - 13, x + wd / 2, y + 13], fill=(8, 10, 18, 250), outline=INK, w=2.4, r=6)
            lane_swatch(L, x - 16, x + 16, y - 5, d)
            if w_ >= 0:
                tally_bars(L, x, y + 6, w_ + 1, (244, 247, 252), h=8, pitch=5.4, w=2.6)


# ----------------------------------------------------------------------------- future_wave_arcs (true angles, tape rings, hairline third)
def circ_overlap(a0, e0, b0, e1):
    for sh in (-360, 0, 360):
        if a0 < b0 + e1 + sh and b0 + sh < a0 + e0:
            return True
    return False


def fut_geom(arcs, opt):
    fut = [a for a in arcs if a['state'] == 'future']
    placed = [[], []]
    out = []
    for a in fut:
        ext = sum(60 * w for k, w in a['units'])
        ring = None
        for ri in (0, 1):
            if not any(circ_overlap(S0, ext, S0, e) for e in placed[ri]):
                ring = ri
                break
        if ring is None:
            ring = 2
        if ring < 2:
            placed[ring].append(ext)
        out.append(dict(a=a, r=TAPE_R[ring], ring=ring, a0=S0, ext=min(ext, 359.5), full=ext))
    return out


def draw_tape(L, g, opt):
    a = g['a']
    col = HARM if a.get('climax') else ORGC
    pts = L.arc_pts(C, g['r'], g['a0'], g['a0'] + g['ext'], max(8, int(g['ext'] / 3)))
    if g['ring'] < 2:           # tape: ink keyline + coloured line (A weight) + end ticks (B tape)
        L.line(pts, INK, 5.0)
        L.line(pts, col + (225,), 2.4 if opt == 'P' else 3.0)
        for aa_ in (g['a0'], g['a0'] + g['ext']):
            L.line([ppx(C, g['r'] - 5, aa_), ppx(C, g['r'] + 5, aa_)], INK, 4.2)
            L.line([ppx(C, g['r'] - 4.4, aa_), ppx(C, g['r'] + 4.4, aa_)], col, 2.2)
    else:                       # third overlap: 2 px hairline at 60 percent
        L.line(pts, INK + (120,), 3.6)
        L.line(pts, col + (153,), 2.0)


def haz_ticks(L, g, opt):
    """CRT_AMBER / INK tape: slanted amber blocks with ink keyline riding the hairline ring"""
    r, S = g['r'], g['a0']
    step = 5.2 if opt == 'P' else 7.0
    n = int(359 / step)
    for i in range(n):
        a0 = S + i * step
        pts = [ppx(C, r - 3.4, a0), ppx(C, r + 3.4, a0 + 1.5), ppx(C, r + 3.4, a0 + 3.1), ppx(C, r - 3.4, a0 + 1.6)]
        L.poly(pts, fill=AMB, outline=INK, w=1.4)


# ----------------------------------------------------------------------------- wave tags
def tag_pos(i, g):
    return ppx(C, g['r'], S0 + 8 + 11.5 * i)


def wave_tags(L, geoms, opt):
    for i, g in enumerate(geoms):
        col = HARM if g['a'].get('climax') else ORGC
        x, y = tag_pos(i, g)
        n = g['a']['wave'] + 1
        if NOW['words']:
            tw_ = L.tw('W%d' % n, 20, 'anton')
            L.rect([x - tw_ / 2 - 5, y - 13, x + tw_ / 2 + 5, y + 13], fill=INK + (255,), r=6)      # ASSEMBLY: 3 px INK knockout, the tape breaks under the text
            L.text((x, y + 1), 'W%d' % n, 20 if opt == 'P' else 18, 'anton', fill=col, anchor='mm', stroke=2.2 if opt == 'P' else 2.0)
        else:
            wd = n * 5.2 + (6 if n > 5 else 0) + 12
            L.rect([x - wd / 2, y - 11, x + wd / 2, y + 11], fill=(8, 10, 18, 255), outline=col, w=2.0, r=5)
            tally_bars(L, x, y, n, col, h=11, pitch=5.2, w=3.0)


# ----------------------------------------------------------------------------- unit pips
def pip_positions(geoms):
    tags = [tag_pos(i, g) for i, g in enumerate(geoms)]
    placed = []
    res = {}
    for gi, g in enumerate(geoms):
        ang = g['a0']
        for ui, (kind, w) in enumerate(g['a']['units']):
            a1 = ang + 60 * w
            mid = (ang + a1) / 2
            lim = (a1 - ang) / 2 - 7.5
            cand = [0]
            for st in (7, 14, 21, 28, 35):
                cand += [st, -st]
            cand = [c for c in cand if abs(c) <= lim] or [0]
            pick = None
            for c in cand:
                p = ppx(C, g['r'], mid + c)
                if all(math.hypot(p[0] - q[0], p[1] - q[1]) >= 34 for q in placed) and all(math.hypot(p[0] - q[0], p[1] - q[1]) >= 38 for q in tags):
                    pick = (p, mid + c)
                    break
            if pick is None:
                pick = (ppx(C, g['r'], mid), mid)
            placed.append(pick[0])
            res[(gi, ui)] = pick
            ang = a1
    return res


def unit_pips(L, geoms, opt):
    pos = pip_positions(geoms)
    for gi, g in enumerate(geoms):
        r = g['r']
        ang = g['a0']
        for ui, (kind, w) in enumerate(g['a']['units']):
            a1 = ang + 60 * w
            kc = KCOL.get(kind, WHITE)
            for q in range(1, w):          # boundary bar ticks across the tape at every interior sector boundary
                p0, p1 = ppx(C, r - 8, ang + 60 * q), ppx(C, r + 8, ang + 60 * q)
                L.line([p0, p1], INK, 5.0)
                L.line([p0, p1], (232, 238, 250), 2.4)
            if ui > 0:                      # unit joint: a longer notch
                p0, p1 = ppx(C, r - 6, ang), ppx(C, r + 6, ang)
                L.line([p0, p1], INK, 4.4)
                L.line([p0, p1], (232, 238, 250), 1.8)
            ang = a1
    for gi, g in enumerate(geoms):
        for ui, (kind, w) in enumerate(g['a']['units']):
            (x, y), _ = pos[(gi, ui)]
            kc = KCOL.get(kind, WHITE)
            R = 13.5 if opt == 'P' else 12.0
            L.ellipse([x - R - 1.4, y - R - 1.4, x + R + 1.4, y + R + 1.4], fill=INK)
            L.ellipse([x - R, y - R, x + R, y + R], fill=(10, 12, 22, 250), outline=kc, w=2.2)
            GL.kind_glyph(L, kind, 20 if opt == 'P' else 17.5, (x, y))


def future(L, f, arcs, sel):
    geoms = fut_geom(arcs, sel.get('fut', 'P'))
    for g in geoms:
        draw_tape(L, g, sel.get('fut', 'P'))
    for g in geoms:
        if g['a'].get('climax'):
            haz_ticks(L, g, sel.get('haz', 'P'))
    unit_pips(L, geoms, sel.get('pips', 'P'))
    wave_tags(L, geoms, sel.get('wtag', 'P'))
    return geoms
