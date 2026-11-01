"""OUTER RINGS: the schedule bezel family (ticks, sector digits + nowords, needle, live cell, chevrons, HOLD cells, live HOLD, +N cells).
Every drawing takes the L2 layer and a variant letter. 'cur' reproduces E10 (bezel9 / cv_over.sector_digits)."""
import sys, math
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw
from e10lib import *
import e9lib as E9
import cv_over as O
from o_ground import BEZEL_MID, BEZEL_HI, BEZEL_LO

B0, B1 = RS['bz0'] + 3, RS['bz0'] + 29          # schedule band 358..384
RM = (B0 + B1) / 2
BZ0, BZ1 = RS['bz0'], RS['bz1']
ORG = (255, 140, 26)                             # SCHEDULE_ORANGE token
ORG_HI = (255, 176, 80)
ORG_PALE = (255, 214, 160)
ORG_EMBER = (118, 58, 16)
ORG_LIVE_OLD = (255, 150, 40)


# ----------------------------------------------------------------------------- text on an arc with optional bold and ink keyline
def arc_text2(L, r, a_mid, s, px, col, kind='mono', bold=0.0, keyline=0.0, kcol=INK, track=1.0):
    from bb_lib import anton as _an, mono as _mo, plex as _pl
    if not NOW['words']:
        return
    f = {'anton': _an, 'mono': _mo, 'plex': _pl}[kind](int(px * L.k))
    advs = [f.getlength(ch) * track / L.k for ch in s]
    tot = sum(advs)
    bottom = 90 < (a_mid % 360) < 270
    flip = False
    if bottom:
        s, advs, flip = s[::-1], advs[::-1], True
    a = a_mid - math.degrees(tot / 2 / r)
    for ch, adv in zip(s, advs):
        am = a + math.degrees(adv / 2 / r)
        if ch != ' ':
            x, y = ppx(C, r, am)
            tmp = Image.new('RGBA', (int(adv * L.k * 2 + 16), int(px * L.k * 2)), (0, 0, 0, 0))
            d = ImageDraw.Draw(tmp)
            cx, cy = tmp.width / 2, tmp.height / 2
            if keyline:
                d.text((cx, cy), ch, font=f, fill=tuple(kcol) + (255,), anchor='mm', stroke_width=int(keyline * L.k), stroke_fill=tuple(kcol) + (255,))
            d.text((cx, cy), ch, font=f, fill=tuple(col) + (255,), anchor='mm')
            if bold:
                d.text((cx + bold * L.k, cy), ch, font=f, fill=tuple(col) + (255,), anchor='mm')
            tmp = tmp.rotate(-am + (180 if flip else 0), resample=Image.BICUBIC, expand=True)
            L.im.alpha_composite(tmp, (int(x * L.k - tmp.width / 2), int(y * L.k - tmp.height / 2)))
        a += math.degrees(adv / r)


def cell_pts(b0, b1, a0, a1, cap_end='flat', cap_start='flat', tip=0.0):
    """polygon of a bezel cell. cap_end: flat | round | arrow ; the tip/round cap stays inside [a0,a1] so the cell's arc is exactly step x 60 deg"""
    rm = (b0 + b1) / 2
    pts = []
    n = max(8, int((a1 - a0) / 2.5))
    ae = a1
    if cap_end == 'arrow':
        ae = a1 - tip
    if cap_end == 'round':
        ae = a1 - math.degrees((b1 - b0) / 2 / rm)
    outer = [ppx(C, b1, a0 + (ae - a0) * i / n) for i in range(n + 1)]
    inner = [ppx(C, b0, ae - (ae - a0) * i / n) for i in range(n + 1)]
    if cap_end == 'arrow':
        mid = [ppx(C, rm, a1)]
    elif cap_end == 'round':
        mid = [ppx(C, rm + (b1 - b0) / 2 * math.cos(math.radians(t)), ae + math.degrees((b1 - b0) / 2 / rm) * math.sin(math.radians(t))) for t in range(80, -90, -20)]
        mid = [ppx(C, rm + (b1 - b0) / 2 * math.sin(math.radians(t)), ae + math.degrees((b1 - b0) / 2 / rm) * math.cos(math.radians(t))) for t in range(-90, 91, 20)][::-1]
    else:
        mid = []
    return outer + mid + inner


# ----------------------------------------------------------------------------- bezel_ticks
def ticks(L, opt):
    for i in range(60):
        a = 6 * i
        major = i % 10 == 0
        if opt == 'cur':
            L.line([ppx(C, BZ1 - 7, a), ppx(C, BZ1 - (3 if i % 10 else 1), a)], (255, 190, 110) if major else (150, 100, 55), 1.2)
        elif opt == 'A':     # incised: ink line with a one-pixel pale lip, in the 5 px rim outside the cell band; majors longer
            r0, r1 = BZ1 - (6.5 if major else 4.5), BZ1 - 1.6
            L.line([ppx(C, r0, a), ppx(C, r1, a)], INK, 2.8 if major else 2.0)
            L.line([ppx(C, r0 + 0.5, a + 0.35), ppx(C, r1 - 0.5, a + 0.35)], BEZEL_HI, 1.0)
        elif opt == 'B':     # pale printed ticks, one value step above the bezel, majors reach down into the cell band as short pale bars
            if major:
                L.line([ppx(C, B1 - 1, a), ppx(C, BZ1 - 1.6, a)], INK, 3.6)
                L.line([ppx(C, B1 - 0.2, a), ppx(C, BZ1 - 2.4, a)], (226, 238, 232), 1.8)
            else:
                L.line([ppx(C, BZ1 - 5, a), ppx(C, BZ1 - 1.8, a)], (190, 214, 206), 1.5)
        elif opt == 'C':     # inside ruler: ticks hang from the inner edge toward the plate (never under the orange), majors 2x longer, ink under pale
            r1 = BZ0 + 0.8
            r0 = BZ0 - (7 if major else 3.6)
            L.line([ppx(C, r0, a), ppx(C, r1, a)], INK, 3.0 if major else 2.2)
            L.line([ppx(C, r0 + 0.6, a), ppx(C, r1, a)], (210, 228, 220) if major else (150, 176, 168), 1.4 if major else 1.1)


# ----------------------------------------------------------------------------- needle
def needle(L, opt):
    if opt == 'cur':
        x0, y0 = ppx(C, BZ0 - 6, 0)
        L.poly([(x0, y0 + 2), (x0 - 11, y0 - 26), (x0 + 11, y0 - 26)], fill=(245, 245, 250), outline=INK, w=2)
    elif opt == 'A':     # dial pointer: tall narrow kite on the plate side, tip touching the bezel under the digit; points outward at the sector it marks
        x, y = ppx(C, BZ0, 0)
        pts = [(x, y + 1), (x + 9, y + 21), (x, y + 31), (x - 9, y + 21)]
        L.poly(pts, fill=(246, 248, 252), outline=INK, w=2.6)
        L.line([(x, y + 7), (x, y + 26)], INK, 1.8)
    elif opt == 'B':     # reading line: a 3 px white radial index through the whole schedule band at 0 deg (the start line of every cell), short white foot on the plate
        for (w, c) in ((7.4, INK), (3.2, (248, 250, 255))):
            L.line([ppx(C, BZ0 - 12, 0), ppx(C, BZ1 - 2, 0)], c, w)
        L.poly([(ppx(C, BZ0 - 12, 0)[0] - 7, ppx(C, BZ0 - 12, 0)[1] + 1), (ppx(C, BZ0 - 12, 0)[0] + 7, ppx(C, BZ0 - 12, 0)[1] + 1), (ppx(C, BZ0 - 12, 0)[0], ppx(C, BZ0 - 12, 0)[1] - 8)], fill=(248, 250, 255), outline=INK, w=2)
    elif opt == 'C':     # keystone index: a flat-topped marker (stem + head) seated on the bezel's inner edge, the head wider than the stem so it is not a play arrow
        x, y = ppx(C, BZ0 + 1, 0)
        pts = [(x - 4.5, y), (x + 4.5, y), (x + 4.5, y + 9), (x + 11, y + 9), (x + 11, y + 15), (x, y + 25), (x - 11, y + 15), (x - 11, y + 9), (x - 4.5, y + 9)]
        L.poly(pts, fill=(246, 248, 252), outline=INK, w=2.6)


# ----------------------------------------------------------------------------- sector digits
def digit_ring_col(opt):
    return {'cur': ORG, 'A': BEZEL_HI, 'B': BEZEL_HI, 'C': BEZEL_HI}[opt]


DIGIT_R = 392


def dice(L, x, y, n, col=(244, 247, 252), r=2.4):
    pat = {1: [(0, 0)], 2: [(-4.5, -4.5), (4.5, 4.5)], 3: [(-5, -5), (0, 0), (5, 5)], 4: [(-4.5, -4.5), (4.5, -4.5), (-4.5, 4.5), (4.5, 4.5)], 5: [(-5, -5), (5, -5), (0, 0), (-5, 5), (5, 5)]}[n]
    for dx, dy in pat:
        L.ellipse([x + dx - r - 0.8, y + dy - r - 0.8, x + dx + r + 0.8, y + dy + r + 0.8], fill=INK)
        L.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r], fill=col)


def tally(L, x, y, n, col=(244, 247, 252)):
    w = 3.0
    pitch = 4.6
    x0 = x - (n - 1) * pitch / 2
    for i in range(n):
        L.rect([x0 + i * pitch - w / 2 - 0.8, y - 8.8, x0 + i * pitch + w / 2 + 0.8, y + 8.8], fill=INK, r=1)
        L.rect([x0 + i * pitch - w / 2, y - 8, x0 + i * pitch + w / 2, y + 8], fill=col, r=1)


def digits(L, opt, nowords_opt='A'):
    for s in range(6):
        x, y = ppx(C, (385 if opt == 'cur' else (DIGIT_R if opt != 'C' else BZ1 + 9)), 60 * s)
        words = NOW['words']
        if opt == 'cur':
            L.ellipse([x - 15, y - 15, x + 15, y + 15], fill=(10, 9, 16), outline=ORANGE, w=3)
            L.text((x, y + 1), str(s), 22, 'anton', fill=WHITE)
            continue
        if opt == 'A':       # casting boss: the bezel swells round each digit (material, ink edge, top-left lip); dark engraved disc, pale ring, white Anton 22 with ink keyline
            L.ellipse([x - 15.6, y - 15.6, x + 15.6, y + 15.6], fill=BEZEL_MID, outline=INK, w=2.4)
            L.ellipse([x - 12.2, y - 12.2, x + 12.2, y + 12.2], fill=(8, 10, 16), outline=BEZEL_HI, w=1.6)
            core = (x, y)
            R = 12.2
        elif opt == 'B':     # flush tile: a rounded square slot cut into the rim (tag family: radius 6), the digit white on ink, pale hairline frame
            L.rect([x - 14, y - 14, x + 14, y + 14], fill=BEZEL_MID, outline=INK, w=2.4, r=7)
            L.rect([x - 11.2, y - 11.2, x + 11.2, y + 11.2], fill=(8, 10, 16), outline=BEZEL_HI, w=1.4, r=4.5)
            R = 11.2
        else:                # flag tab: a trapezoid tab hung on the outer edge, clear of every cell; digit centred on a dark face
            ang = 60 * s
            th = math.radians(ang)
            def q(dr, dt):
                px_, py_ = ppx(C, BZ1 - 1 + dr, ang)
                return (px_ + dt * math.cos(th), py_ + dt * math.sin(th))
            pts = [q(0, -15), q(0, 15), q(15, 12.5), q(15, -12.5)]
            L.poly(pts, fill=BEZEL_MID, outline=INK, w=2.4)
            x, y = ppx(C, BZ1 + 7.5, ang)
            R = 10.5
            L.ellipse([x - 10.2, y - 10.2, x + 10.2, y + 10.2], fill=(8, 10, 16), outline=BEZEL_HI, w=1.4)
        if words:
            L.text((x, y + 1), str(s), 22 if opt != 'C' else 19, 'anton', fill=WHITE, stroke=1.6)
        else:
            nowords_code(L, x, y, s, nowords_opt)


def nowords_code(L, x, y, s, opt):
    """words off: a non-digit sector code in the same disc. A: zero ring + tallies, B: zero ring + dice pips, C: rim notches only (disc stays dark, notches count on the bezel edge)"""
    if opt == 'A':
        if s == 0:
            L.ellipse([x - 5.8, y - 7.8, x + 5.8, y + 7.8], outline=(244, 247, 252), w=2.6)
        else:
            tally(L, x, y, s)
    elif opt == 'B':
        if s == 0:
            L.ellipse([x - 5.2, y - 5.2, x + 5.2, y + 5.2], outline=(244, 247, 252), w=2.6)
        else:
            dice(L, x, y, s)
    else:
        if s == 0:
            L.poly([(x, y - 7), (x + 6, y + 5), (x - 6, y + 5)], fill=(244, 247, 252), outline=INK, w=1.6)
        else:
            ang = 60 * s
            th = math.radians(ang)
            n = s
            for i in range(n):
                dt = (i - (n - 1) / 2) * 3.8
                for r_a, r_b, col, w in ((BZ1 - 1, BZ1 - 10, INK, 3.4), (BZ1 - 1.6, BZ1 - 9.4, (244, 247, 252), 1.6)):
                    p0 = ppx(C, r_a, ang); p1 = ppx(C, r_b, ang)
                    L.line([(p0[0] + dt * math.cos(th), p0[1] + dt * math.sin(th)), (p1[0] + dt * math.cos(th), p1[1] + dt * math.sin(th))], col, w)
            L.ellipse([x - 2.2, y - 2.2, x + 2.2, y + 2.2], fill=(244, 247, 252))


# ----------------------------------------------------------------------------- schedule cells
NAMES = ['THIS TURN', 'NEXT', 'THEN']


def hold_glyph(L, x, y, opt, col, ang=0, size=1.0):
    """0-step glyph (not a pause button). A: wheel on a stop block, B: ring with a bar through it (zero change), C: two rails side by side ALONG travel (equals)"""
    s = size
    th = math.radians(ang)
    tx, ty = math.cos(th), math.sin(th)
    if opt == 'cur':
        L.ellipse([x - 13, y - 13, x + 13, y + 13], fill=(10, 9, 16), outline=col, w=2.6)
        L.glyph('C_HOLD', 15, (x, y), col)
        return
    L.ellipse([x - 14 * s, y - 14 * s, x + 14 * s, y + 14 * s], fill=(10, 9, 16), outline=INK, w=3.0)
    L.ellipse([x - 12.4 * s, y - 12.4 * s, x + 12.4 * s, y + 12.4 * s], fill=(10, 9, 16), outline=col, w=1.8)
    if opt == 'A':
        L.ellipse([x - 6 * s, y - 8 * s, x + 4 * s, y + 2 * s], outline=col, w=2.2)
        L.poly([(x - 8 * s, y + 8 * s), (x + 9 * s, y + 8 * s), (x + 9 * s, y + 1 * s)], fill=col)
    elif opt == 'B':
        L.ellipse([x - 7.5 * s, y - 7.5 * s, x + 7.5 * s, y + 7.5 * s], outline=col, w=2.2)
        L.line([(x - 10 * s, y), (x + 10 * s, y)], INK, 4.6)
        L.line([(x - 9 * s, y), (x + 9 * s, y)], col, 2.4)
    else:
        for off in (-3.6, 3.6):
            nx, ny = -ty, tx           # normal (outward-ish)
            p0 = (x + tx * -8 * s + nx * off * s, y + ty * -8 * s + ny * off * s)
            p1 = (x + tx * 8 * s + nx * off * s, y + ty * 8 * s + ny * off * s)
            L.line([p0, p1], col, 2.6)


def live_cell(L, opt, a0, a1, step):
    """the live +N THIS TURN cell"""
    if opt == 'cur':
        L.poly(L.band(C, B0, B1, a0, a1), fill=ORG_LIVE_OLD, outline=ORANGE, w=1.6)
        return a0 + 6
    if opt == 'A':       # arrow-end cell: lower value fill (a lit panel, not a flood), arrow tip at exactly step x 60, ink edge, hi lip, flat start flush on the needle line
        a0 = a0 + 1.4
        p = cell_pts(B0, B1, a0, a1 - 0.6, 'arrow', tip=5.5)
        L.poly(p, fill=(238, 120, 22), outline=INK, w=3.2)
        L.poly(p, fill=None, outline=ORG_HI, w=1.0)
        inner = cell_pts(B0 + 2.6, B1 - 2.6, a0 + 1.0, a1 - 2.4, 'arrow', tip=4.6)
        L.poly(inner, fill=(255, 150, 40), outline=None)
        return a0 + 7
    if opt == 'B':       # ratchet cell: one segment per step (a visible divider at 60), square end cap with a stop tab; fill ORG, ink dividers and edge
        for k in range(step):
            sa0 = a0 + k * 60 + (1.4 if k == 0 else 0.7)
            sa1 = a0 + (k + 1) * 60 - 0.7
            pts = L.band(C, B0, B1, sa0, sa1)
            L.poly(pts, fill=(250, 134, 24), outline=INK, w=2.6)
            L.poly(L.band(C, B0 + 3, B1 - 3, sa0 + 1.4, sa1 - 1.4), fill=(255, 150, 40))
        xe, ye = ppx(C, (B0 + B1) / 2, a0 + step * 60 - 0.7)
        # stop tab at the end
        tb = [ppx(C, B1 + 2, a0 + step * 60 - 0.2), ppx(C, B0 - 2, a0 + step * 60 - 0.2), ppx(C, B0 - 2, a0 + step * 60 - 2.3), ppx(C, B1 + 2, a0 + step * 60 - 2.3)]
        L.poly(tb, fill=INK)
        return a0 + 8
    if opt == 'C':       # lit tube: dark glass cell with a thick bright orange rim and a half-value orange core; a smaller warm mass, ink text is replaced by pale text
        p = cell_pts(B0, B1, a0 + 1.0, a1 - 0.6, 'round')
        L.poly(p, fill=(150, 72, 12), outline=INK, w=3.4)
        L.poly(cell_pts(B0 + 1.8, B1 - 1.8, a0 + 1.6, a1 - 1.2, 'round'), fill=(214, 108, 20), outline=ORG_HI, w=2.2)
        return a0 + 7


def live_label(L, opt, a0, step, txt):
    lab_deg = len(txt) * 10.2 / RM * 57.3
    if opt == 'cur':
        L.arc_text(C, RM - 1, a0 + 6 + lab_deg / 2, txt, 17, INK, 'mono')
        return a0 + 6 + lab_deg + 4
    if opt == 'A':       # mono 19 ink, faux-bold, with the plus sign drawn as its own bar-plus glyph (font plus is thin at arc scale)
        px = 19
        lab_deg = len(txt) * 11.6 / RM * 57.3
        a_start = a0 + 7
        # custom plus
        x, y = ppx(C, RM, a_start + 0.9)
        th = math.radians(a_start + 0.9)
        arc_text2(L, RM - 0.5, a_start + 3.0 + (lab_deg - 3.4) / 2, txt[1:], px, INK, 'mono', bold=0.45)
        for (dx, dy) in ((-4.2, 0), (4.2, 0)):
            pass
        ux, uy = math.cos(th), math.sin(th)
        nx, ny = math.sin(th), -math.cos(th)
        L.line([(x - 5 * ux, y - 5 * uy), (x + 5 * ux, y + 5 * uy)], INK, 2.8)
        L.line([(x - 5 * nx, y - 5 * ny), (x + 5 * nx, y + 5 * ny)], INK, 2.8)
        return a_start + lab_deg + 4
    if opt == 'B':       # mono 18, ink, keylined in pale so it reads on the mid-value orange; tracked +6 percent
        lab_deg = len(txt) * 10.9 / RM * 57.3
        arc_text2(L, RM - 0.5, a0 + 7 + lab_deg / 2, txt, 18, INK, 'mono', bold=0.4, track=1.06)
        return a0 + 7 + lab_deg + 4
    if opt == 'C':       # pale-cream text on the dark core: highest contrast of the three
        lab_deg = len(txt) * 11.0 / RM * 57.3
        arc_text2(L, RM - 0.5, a0 + 8 + lab_deg / 2, txt, 18, (255, 238, 205), 'mono', bold=0.35, keyline=1.4)
        return a0 + 8 + lab_deg + 4


def chevrons(L, opt, a0, a1, a_text_end, live=True, live_opt='cur', dark=False):
    """direction chevrons along the cell after the label"""
    if opt == 'cur':
        span = a1 - a0 + 0.8
        nch = int(span / 12)
        for j in range(nch):
            am = a0 - 0.8 + (a1 - a0) * (j + 0.5) / nch if False else a0 + (a1 - a0) * (j + 0.5) / nch
            if am < a_text_end:
                continue
            p = [ppx(C, B0 + 5, am - 2.4), ppx(C, RM, am + 2.4), ppx(C, B1 - 5, am - 2.4)]
            L.line(p, (255, 230, 170) if live else (170, 100, 35), 1.8)
        return
    pitch_deg = 26.0 / RM * 57.3         # fixed pitch of 26 px along the arc
    am = a_text_end + pitch_deg * 0.6
    amax = a1 - (9.0 if live_opt in ('A', 'cur') else 5.0)
    k = 0
    n_tot = max(1, int((amax - am) / pitch_deg) + 1)
    while am <= amax:
        t = k / max(1, n_tot - 1)
        if opt == 'A':       # fine pale chevrons, 2.6 px with ink under: 12 px deep, wide, constant pitch
            p = [ppx(C, B0 + 5.5, am - 2.9), ppx(C, B1 - 5.5, am + 0.0 + 0.0), ppx(C, B0 + 5.5, am + 2.9)] if False else [ppx(C, B1 - 5.0, am - 3.0), ppx(C, RM, am + 3.0), ppx(C, B0 + 5.0, am - 3.0)]
            L.line(p, (200, 100, 14), 4.8)
            L.line(p, (255, 236, 196), 2.4)
        elif opt == 'B':     # tone-on-tone solid wedges that brighten toward the end cap (travel gets "faster")
            k_ = 0.35 + 0.65 * t
            col = (int(214 + 41 * k_), int(100 + 120 * k_), int(18 + 120 * k_))
            p = [ppx(C, B1 - 4.5, am - 3.4), ppx(C, RM, am + 3.4), ppx(C, B0 + 4.5, am - 3.4), ppx(C, RM, am - 1.2)]
            L.poly(p, fill=col)
        else:                # C: no repeats: a dashed rail along the cell centre ending in ONE arrowhead at the cap
            pass
        am += pitch_deg
        k += 1
    if opt == 'C':
        r_ = RM
        L.line(L.arc_pts(C, r_, a_text_end + 1.5, amax - 2.5), INK, 4.0)
        L.line(L.arc_pts(C, r_, a_text_end + 1.5, amax - 2.5), (255, 236, 196), 1.8, dash=(7, 5))
        p = [ppx(C, B1 - 5.2, amax - 6.5), ppx(C, r_, amax - 0.5), ppx(C, B0 + 5.2, amax - 6.5)]
        L.line(p, INK, 6.0)
        L.line(p, (255, 244, 220), 3.0)


def hold_cell(L, opt, a0, a1, k, glyph_opt='A'):
    """HOLD NEXT / HOLD THEN: dark cell, family-resembling the live cell but off"""
    nm = NAMES[k].split()[0]
    col = (255, 190, 110)
    live = False
    if opt == 'cur':
        L.poly(L.band(C, B0, B1, a0, a1), fill=(14, 10, 6, 235), outline=col, w=2.4)
        x, y = ppx(C, RM, a0 + 6)
        hold_glyph(L, x, y, 'cur', col)
        L.arc_text(C, RM - 1, a0 + 24, 'HOLD ' + nm, 16, col, 'mono')
        return
    if opt == 'A':       # dark glass, 2.4 px orange outline with ink under, cap bars at both ends, pale-orange 18 px text; glyph disc after the start cap
        p = cell_pts(B0, B1, a0 + 0.8, a1 - 0.8)
        L.poly(p, fill=(16, 12, 10), outline=INK, w=4.4)
        L.poly(p, fill=None, outline=ORG, w=2.0)
        x, y = ppx(C, RM, a0 + 7.2)
        hold_glyph(L, x, y, glyph_opt, ORG_HI, ang=a0 + 7.2)
        arc_text2(L, RM - 0.5, a0 + 25, 'HOLD ' + nm, 18, ORG_PALE, 'mono', bold=0.3)
    elif opt == 'B':     # ember cell: desaturated warm-grey fill (value above the bezel, below the live cell) with hatch; text cream with keyline
        p = cell_pts(B0, B1, a0 + 0.8, a1 - 0.8)
        L.poly(p, fill=(70, 44, 22), outline=INK, w=3.6)
        L.poly(p, fill=None, outline=(200, 110, 30), w=1.4)
        for q in range(int((a1 - a0) / 3.2)):
            am = a0 + 2 + q * 3.2
            L.line([ppx(C, B0 + 2, am), ppx(C, B1 - 2, am + 2.0)], (92, 58, 28), 1.2)
        x, y = ppx(C, RM, a0 + 7.2)
        hold_glyph(L, x, y, glyph_opt, ORG_PALE, ang=a0 + 7.2)
        arc_text2(L, RM - 0.5, a0 + 25, 'HOLD ' + nm, 18, (255, 236, 200), 'mono', bold=0.3, keyline=1.3)
    else:                # C: outline-only slot, 3 px orange rule on the INNER edge and a dim rule on the outer: reads as an unfilled track; text in orange-pale, disc outlined
        p = cell_pts(B0, B1, a0 + 0.8, a1 - 0.8)
        L.poly(p, fill=(10, 9, 16), outline=INK, w=3.4)
        L.line(L.arc_pts(C, B0 + 1.4, a0 + 1.8, a1 - 1.8), ORG, 2.6)
        L.line(L.arc_pts(C, B1 - 1.4, a0 + 1.8, a1 - 1.8), (140, 78, 24), 1.6)
        for aa_ in (a0 + 1.2, a1 - 1.2):
            L.line([ppx(C, B0 + 1.4, aa_), ppx(C, B1 - 1.4, aa_)], ORG, 2.2)
        x, y = ppx(C, RM, a0 + 7.2)
        hold_glyph(L, x, y, glyph_opt, ORG, ang=a0 + 7.2)
        arc_text2(L, RM - 0.5, a0 + 25, 'HOLD ' + nm, 18, ORG_HI, 'mono', bold=0.3)


def hold_live(L, opt, a0, a1, glyph_opt='A'):
    """LATENT: the current step is 0. Live geometry (full-height cell, cap bars) but never orange fill."""
    col = (240, 244, 250)
    p = cell_pts(B0, B1, a0 + 1.4, a1 - 0.6)
    if opt == 'cur':
        L.poly(L.band(C, B0, B1, a0 + 0.8, a1 - 0.8), fill=(14, 10, 6, 235), outline=WHITE, w=2.4)
        x, y = ppx(C, RM, a0 + 6.8)
        hold_glyph(L, x, y, 'cur', WHITE)
        L.arc_text(C, RM - 1, a0 + 24, 'HOLD THIS', 16, (255, 190, 110), 'mono')
    elif opt == 'A':     # bone panel: neutral warm-white fill, ink text: clearly "the live one" by value, never orange
        L.poly(p, fill=(222, 214, 196), outline=INK, w=3.4)
        x, y = ppx(C, RM, a0 + 7.2)
        hold_glyph(L, x, y, glyph_opt, (40, 36, 32), ang=a0 + 7.2)
        L.ellipse([x - 12.4, y - 12.4, x + 12.4, y + 12.4], fill=(240, 236, 224), outline=INK, w=1.8)
        hold_glyph_inner(L, x, y, glyph_opt, (30, 26, 22), a0 + 7.2)
        arc_text2(L, RM - 0.5, a0 + 28, 'HOLD THIS TURN', 18, INK, 'mono', bold=0.4)
    elif opt == 'B':     # live outline: dark glass with a 4 px bright orange rule all round (the live weight) + hatch stripes at 35 percent: orange as border, never fill
        L.poly(p, fill=(18, 12, 8), outline=INK, w=5.4)
        L.poly(p, fill=None, outline=ORG, w=3.4)
        for q in range(int((a1 - a0) / 3.0)):
            am = a0 + 2 + q * 3.0
            L.line([ppx(C, B0 + 3, am), ppx(C, B1 - 3, am + 2.0)], (150, 76, 18), 1.6)
        x, y = ppx(C, RM, a0 + 7.2)
        hold_glyph(L, x, y, glyph_opt, ORG_HI, ang=a0 + 7.2)
        arc_text2(L, RM - 0.5, a0 + 28, 'HOLD THIS TURN', 18, (255, 240, 214), 'mono', bold=0.4, keyline=1.4)
    else:                # C: steel-pale cell (STEEL family): cold metal vs warm orange: the one cold live cell
        L.poly(p, fill=(150, 162, 182), outline=INK, w=3.4)
        L.poly(cell_pts(B0 + 2.4, B1 - 2.4, a0 + 2.4, a1 - 1.6), fill=(180, 192, 210))
        x, y = ppx(C, RM, a0 + 7.2)
        L.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(34, 40, 52), outline=INK, w=3.0)
        hold_glyph_inner(L, x, y, glyph_opt, (230, 236, 248), a0 + 7.2)
        arc_text2(L, RM - 0.5, a0 + 28, 'HOLD THIS TURN', 18, INK, 'mono', bold=0.4)


def hold_glyph_inner(L, x, y, opt, col, ang):
    s = 1.0
    th = math.radians(ang)
    tx, ty = math.cos(th), math.sin(th)
    if opt == 'A':
        L.ellipse([x - 6, y - 8, x + 4, y + 2], outline=col, w=2.2)
        L.poly([(x - 8, y + 8), (x + 9, y + 8), (x + 9, y + 1)], fill=col)
    elif opt == 'B':
        L.ellipse([x - 7.5, y - 7.5, x + 7.5, y + 7.5], outline=col, w=2.2)
        L.line([(x - 9, y), (x + 9, y)], col, 2.4)
    else:
        for off in (-3.6, 3.6):
            nx, ny = -ty, tx
            L.line([(x - tx * 8 + nx * off, y - ty * 8 + ny * off), (x + tx * 8 + nx * off, y + ty * 8 + ny * off)], col, 2.6)


def plus_cell(L, opt, a0, a1, step, k, label_ang=None):
    """LATENT: a later non-zero step (+N NEXT / THEN): coming, not now. live geometry, off value."""
    txt = '+%d %s' % (step, NAMES[k])
    lab_deg = len(txt) * 10.2 / RM * 57.3
    if opt == 'cur':
        L.poly(L.band(C, B0, B1, a0, a1), fill=ORG_EMBER[:1] + (30, 8) if False else (60, 30, 8), outline=ORANGE, w=1.6)
        chevrons(L, 'cur', a0, a1, a0 + 6 + lab_deg + 4, live=False)
        L.arc_text(C, RM - 1, a0 + 6 + lab_deg / 2, txt, 17, (255, 190, 110), 'mono')
        return
    p = cell_pts(B0, B1, a0 + 0.8, a1 - 0.8, 'arrow' if opt != 'C' else 'flat', tip=5.0)
    if opt == 'A':       # ember: 40 percent orange mixed into the bezel, bright orange 2 px edge, pale text; arrow end like the live cell
        L.poly(p, fill=(124, 62, 18), outline=INK, w=3.6)
        L.poly(p, fill=None, outline=(236, 124, 24), w=1.6)
        tc = ORG_PALE
        chev = (255, 190, 120)
    elif opt == 'B':     # half-tone: the live fill under a 55 percent dark scanline mask (horizontal-to-ring stripes): same hue and geometry as live, plainly dimmer
        L.poly(p, fill=(150, 76, 18), outline=INK, w=3.6)
        for q in range(int((a1 - a0) / 2.4)):
            am = a0 + 1.2 + q * 2.4
            L.line([ppx(C, B0 + 1, am), ppx(C, B1 - 1, am)], (96, 48, 14), 1.1)
        L.poly(p, fill=None, outline=(255, 150, 40), w=1.4)
        tc = (255, 232, 196)
        chev = (255, 190, 120)
    else:                # C: outlined track: bright 3 px orange outline, 25 percent orange tint inside, square caps: "empty slot waiting for its step"
        pf = cell_pts(B0, B1, a0 + 0.8, a1 - 0.8)
        L.poly(pf, fill=(54, 30, 12), outline=INK, w=5.0)
        L.poly(pf, fill=None, outline=ORG, w=3.0)
        tc = ORG_PALE
        chev = ORG
    arc_text2(L, RM - 0.5, a0 + 7 + lab_deg / 2, txt, 18, tc, 'mono', bold=0.3, track=1.0)
    pitch = 26.0 / RM * 57.3
    am = a0 + 7 + lab_deg + 5
    while am < a1 - 8:
        pp = [ppx(C, B1 - 5.5, am - 2.8), ppx(C, RM, am + 2.8), ppx(C, B0 + 5.5, am - 2.8)]
        L.line(pp, chev, 2.2)
        am += pitch


# ----------------------------------------------------------------------------- the whole schedule bezel
def schedule(L, sched, sel, hold_glyph_opt=None):
    """sel keys: ticks, live, chev, hold, hold_live, plus, hold_glyph"""
    gl = sel.get('hold_glyph', 'A')
    ticks(L, sel.get('ticks', 'cur'))
    cum = 0
    for k, v in enumerate(sched):
        live = k == 0
        if v == 0:
            span_ = 40
            a0, a1 = cum + 0.8, cum + span_ - 0.8
            if live:
                hold_live(L, sel.get('hold_live', 'cur'), cum, cum + span_, gl)
            else:
                hold_cell(L, sel.get('hold', 'cur'), cum, cum + span_, k, gl)
            cum += span_
            continue
        span_ = 60 * v
        a0, a1 = cum + 0.8, cum + span_ - 0.8
        txt = '+%d %s' % (v, NAMES[k])
        if live:
            lo = sel.get('live', 'cur')
            live_cell(L, lo, cum, cum + span_, v)
            a_end = live_label(L, lo, cum, v, txt)
            chevrons(L, sel.get('chev', 'cur'), a0, a1, a_end, True, lo)
        else:
            plus_cell(L, sel.get('plus', 'cur'), cum, cum + span_, v, k)
        cum += span_
