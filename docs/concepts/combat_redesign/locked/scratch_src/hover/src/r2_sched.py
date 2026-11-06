"""R2 outer_rings SCHEDULE BEZEL: bezel_ticks, needle, sector_digits (+nowords), sched_this_turn, sched_chevrons, sched_hold_cells, sched_hold_live, sched_plus_cells.
Selectors 'P' = R2 pick, 'V' = the one allowed variant.  Everything is drawn on the L2 layer at 2x."""
import sys, math
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw
from e10lib import *
import o_sched as S
from o_sched import cell_pts, arc_text2, B0, B1, RM, BZ0, BZ1, ORG, ORG_HI, ORG_PALE, NAMES, tally
from o_ground import BEZEL_MID, BEZEL_HI, BEZEL_LO
import r2_glyphs as GL

LIVE_EDGE = (176, 84, 18)        # live cell: outer band; value kept under the HARM chevron (lum 105 vs 122)
LIVE_FILL = (200, 98, 22)        # inner panel, carries the INK text at contrast 4.7
LIVE_LIP = (255, 176, 80)
DIGIT_R = 386.5
BOSS_R = 14.3
WELL_R = 12.0
DIGIT_ANG = [-4.5, 60.0, 120.0, 180.0, 240.0, 300.0]     # O-29 fix 2: digit 0 sits 4.5 deg before the THIS TURN tape start (sector 0 spans -30..30)
DIGIT_GAP = 2.6                                           # px of bezel left clear round each digit boss (holes punched in the schedule layer)


def digit_xy(s):
    return ppx(C, DIGIT_R, DIGIT_ANG[s])


def punch_digits(L):
    """cut a round hole (boss radius + DIGIT_GAP) at every digit in an L2 layer: tape, hold plates and labels never run under a digit"""
    from PIL import ImageDraw as _ID
    d = _ID.Draw(L.im)
    k = L.k
    for s in range(6):
        x, y = digit_xy(s)
        r = (BOSS_R + DIGIT_GAP) * k
        d.ellipse([x * k - r, y * k - r, x * k + r, y * k + r], fill=(0, 0, 0, 0))


def pe(x, y, r, a):
    return ppx((x, y), r, a)


# ----------------------------------------------------------------------------- bezel_ticks
def ticks(L, opt):
    """incised: ink groove 1.4 px (majors 2.0) with a pale lip 1 px on the lit side, in the rim outside the cell band."""
    for i in range(60):
        a = 6 * i
        major = i % 10 == 0
        r0, r1 = BZ1 - (5.4 if major else 3.6), BZ1 - 1.2
        w = (2.0 if major else 1.4) if opt == 'P' else (2.4 if major else 1.8)
        L.line([ppx(C, r0, a), ppx(C, r1, a)], INK, w)
        th = math.radians(a)
        ox, oy = 0.9, 0.9      # lip on the lower-right wall of the groove (light from the top-left)
        p0, p1 = ppx(C, r0 + 0.4, a), ppx(C, r1 - 0.4, a)
        L.line([(p0[0] + ox, p0[1] + oy), (p1[0] + ox, p1[1] + oy)], BEZEL_HI + (200,), 0.8)


# ----------------------------------------------------------------------------- needle
def needle(L, opt):
    """pointer 10 x 26 px on the plate side, tip on the bezel's inner edge, 8 px stem into the cell band; a home-plate pentagon (V: hex shoulders 12 px)."""
    x, y = ppx(C, BZ0, 0)
    if opt == 'P':
        pts = [(x, y + 0.5), (x + 5, y + 11), (x + 5, y + 26), (x - 5, y + 26), (x - 5, y + 11)]
    else:
        pts = [(x, y + 0.5), (x + 6, y + 8), (x + 6, y + 26), (x - 6, y + 26), (x - 6, y + 8)]
    # stem first (under the pointer): 8 px into the band
    L.line([(x, y + 1), (x, y - 8)], INK, 5.4)
    L.line([(x, y + 1), (x, y - 7.2)], (246, 248, 252), 2.4)
    L.poly(pts, fill=(246, 248, 252), outline=INK, w=2.6)
    L.line([(x, y + 12), (x, y + 21)], INK, 1.8)


# ----------------------------------------------------------------------------- sector_digits
def digits(L, opt):
    for s in range(6):
        x, y = digit_xy(s)
        R = BOSS_R if opt == 'P' else BOSS_R - 1.4
        well = WELL_R if opt == 'P' else WELL_R - 1.2
        L.ellipse([x - R, y - R, x + R, y + R], fill=BEZEL_MID, outline=INK, w=1.8)
        L.ellipse([x - R + 1.6, y - R + 1.6, x + R - 1.6, y + R - 1.6], fill=BEZEL_HI)           # lit lip (the bezel swelling round the well)
        L.ellipse([x - well, y - well, x + well, y + well], fill=(8, 10, 16))
        if NOW['words']:
            L.text((x, y + 1.6), str(s), 24 if opt == 'P' else 22, 'anton', fill=WHITE, stroke=1.4)
        else:
            nowords_code(L, x, y, s)


def nowords_code(L, x, y, s):
    """words off: zero ring for sector 0, tallies 1-5 (same disc)."""
    if s == 0:
        L.ellipse([x - 5.8, y - 8.0, x + 5.8, y + 8.0], outline=(244, 247, 252), w=2.6)
    else:
        w, pitch, h = 2.8, 4.1, 13.0
        x0 = x - (s - 1) * pitch / 2
        for i in range(s):
            xx = x0 + i * pitch
            L.rect([xx - w / 2 - 0.8, y - h / 2 - 0.8, xx + w / 2 + 0.8, y + h / 2 + 0.8], fill=INK, r=1)
            L.rect([xx - w / 2, y - h / 2, xx + w / 2, y + h / 2], fill=(244, 247, 252), r=1)


# ----------------------------------------------------------------------------- sched_this_turn
def live_cell(L, a0, a1, opt):
    a0 = a0 + 1.4
    tip = 5.5 if opt == 'P' else 6.5
    p = cell_pts(B0, B1, a0, a1 - 0.6, 'arrow', tip=tip)
    if opt == 'P':      # bloom: 4 px at 30 percent, behind the cell
        k = L.k
        L.glow(lambda d: d.polygon([(x * k, y * k) for x, y in p], fill=(255, 140, 26, 255)), blur=4, strength=0.30)
    L.poly(p, fill=LIVE_EDGE, outline=INK, w=3.2)
    L.poly(p, fill=None, outline=LIVE_LIP, w=1.0)
    inner = cell_pts(B0 + 2.6, B1 - 2.6, a0 + 1.0, a1 - 2.4, 'arrow', tip=tip - 1.0)
    L.poly(inner, fill=LIVE_FILL, outline=None)
    return a0 + 7


def live_label(L, a0, txt, n=2):
    """INK 19 with a drawn plus (bar-plus glyph, 2.8 px) then the number and word."""
    px = 19
    lab_deg = len(txt) * 11.6 / RM * 57.3
    a_start = a0 + 7
    x, y = ppx(C, RM, a_start + 0.9)
    th = math.radians(a_start + 0.9)
    arc_text2(L, RM - 0.5, a_start + 3.0 + (lab_deg - 3.4) / 2, txt[1:], px, INK, 'mono', bold=0.45)
    ux, uy = math.cos(th), math.sin(th)
    nx, ny = math.sin(th), -math.cos(th)
    L.line([(x - 5 * ux, y - 5 * uy), (x + 5 * ux, y + 5 * uy)], INK, 2.8)
    L.line([(x - 5 * nx, y - 5 * ny), (x + 5 * nx, y + 5 * ny)], INK, 2.8)
    if not NOW['words']:       # O4: nowords = '+' then an n-stroke white tally (same strokes as the ring tags and sector digits)
        for i in range(n):
            xx, yy = ppx(C, RM, a_start + 0.9 + (11.0 + i * 5.4) / RM * 57.3)
            L.rect([xx - 2.6, yy - 7.8, xx + 2.6, yy + 7.8], fill=INK, r=1)
            L.rect([xx - 1.4, yy - 7.0, xx + 1.4, yy + 7.0], fill=(244, 247, 252), r=1)
    return a_start + lab_deg + 4


# ----------------------------------------------------------------------------- sched_chevrons
def chevrons(L, a0, a1, a_text_end, opt):
    pitch = (26.0 if opt == 'P' else 22.0) / RM * 57.3
    am = a_text_end + pitch * 0.6
    amax = a1 - 9.0
    while am <= amax:
        p = [ppx(C, B1 - 5.0, am - 3.0), ppx(C, RM, am + 3.0), ppx(C, B0 + 5.0, am - 3.0)]
        L.line(p, (96, 44, 8), 4.6)
        L.line(p, (255, 236, 196), 2.4 if opt == 'P' else 2.0)
        am += pitch


# ----------------------------------------------------------------------------- hold glyph (hourglass)
def hold_glyph(L, x, y, col, size=1.0, ink_disc=True):
    """disc 28 px: ink edge, ring in the cell colour, library hourglass 17 px"""
    s = size
    L.ellipse([x - 14 * s, y - 14 * s, x + 14 * s, y + 14 * s], fill=(10, 9, 16), outline=INK, w=3.0)
    L.ellipse([x - 12.4 * s, y - 12.4 * s, x + 12.4 * s, y + 12.4 * s], fill=(10, 9, 16), outline=col, w=1.8)
    GL.stamp(L, 'hold', 16.5 * s, (x, y), col)


SKIP_LABELS = [False]      # O2: the hold glyph + label text are drawn in a later pass (above the bezel spokes)


def hold_label(L, a0, k, opt, live=False):
    x, y = ppx(C, RM, a0 + 7.2)
    if live:
        hold_glyph(L, x, y, ORG_HI)
        arc_text2(L, RM - 0.5, a0 + 28, 'HOLD THIS TURN', 18, (255, 240, 214), 'mono', bold=0.4, keyline=1.4)
    else:
        hold_glyph(L, x, y, ORG_HI, 1.0 if opt == 'P' else 0.92)
        arc_text2(L, RM - 0.5, a0 + 27.2, 'HOLD ' + NAMES[k].split()[0], 18, ORG_PALE if opt == 'P' else ORG_HI, 'mono', bold=0.3)


def labels(L, sched, sel={}):
    """O2: every hold cell's glyph and text, drawn after the bezel spoke layer"""
    cum = 0
    for k, v in enumerate(sched):
        if v == 0:
            hold_label(L, cum, k, sel.get('hold', 'P'), live=(k == 0))
            cum += 40
        else:
            cum += 60 * v


def hold_cell(L, a0, a1, k, opt):
    nm = NAMES[k].split()[0]
    p = cell_pts(B0, B1, a0 + 0.8, a1 - 0.8)
    L.poly(p, fill=(16, 12, 10), outline=INK, w=4.4 if opt == 'P' else 5.0)
    L.poly(p, fill=None, outline=ORG, w=2.0 if opt == 'P' else 2.8)
    if SKIP_LABELS[0]:
        return
    x, y = ppx(C, RM, a0 + 7.2)
    hold_glyph(L, x, y, ORG_HI, 1.0 if opt == 'P' else 0.92)
    arc_text2(L, RM - 0.5, a0 + 25, 'HOLD ' + nm, 18, ORG_PALE if opt == 'P' else ORG_HI, 'mono', bold=0.3)


def hold_live(L, a0, a1, opt):
    p = cell_pts(B0, B1, a0 + 1.4, a1 - 0.6)
    L.poly(p, fill=(18, 12, 8), outline=INK, w=5.4)
    L.poly(p, fill=None, outline=ORG, w=4.0 if opt == 'P' else 3.2)
    for q in range(int((a1 - a0) / 3.0)):
        am = a0 + 2 + q * 3.0
        L.line([ppx(C, B0 + 3, am), ppx(C, B1 - 3, am + 2.0)], (150, 76, 18), 1.6 if opt == 'P' else 1.2)
    if SKIP_LABELS[0]:
        return
    x, y = ppx(C, RM, a0 + 7.2)
    hold_glyph(L, x, y, ORG_HI)
    arc_text2(L, RM - 0.5, a0 + 28, 'HOLD THIS TURN', 18, (255, 240, 214), 'mono', bold=0.4, keyline=1.4)


# ----------------------------------------------------------------------------- the whole bezel
def schedule(L, sched, sel):
    ticks(L, sel.get('ticks', 'P'))
    cum = 0
    for k, v in enumerate(sched):
        live = k == 0
        if v == 0:
            span_ = 40
            if live:
                hold_live(L, cum, cum + span_, sel.get('hold_live', 'P'))
            else:
                hold_cell(L, cum, cum + span_, k, sel.get('hold', 'P'))
            cum += span_
            continue
        span_ = 60 * v
        a0, a1 = cum + 0.8, cum + span_ - 0.8
        txt = '+%d %s' % (v, NAMES[k])
        if live:
            live_cell(L, cum, cum + span_, sel.get('live', 'P'))
            a_end = live_label(L, cum, txt, v)
            chevrons(L, a0, a1, a_end, sel.get('chev', 'P'))
        else:
            S.plus_cell(L, 'A' if sel.get('plus', 'P') == 'P' else 'B', cum, cum + span_, v, k)
        cum += span_
