"""OUTER RINGS: the landing arc family. One object per landing unit: frame (+caps), kind disc, wear, now dot, turn dots, chevrons, diamonds, check, soak, brace, twist.
Variants: 'cur' (E10), 'A','B','C'. Layout runs in px along the arc so every mark keeps its own size at every radius."""
import sys, math
sys.dont_write_bytecode = True
from e10lib import *
import e10lib as E
from o_ground import BEZEL_MID, BEZEL_HI

LANE_R = [425, 460, 495]
HALF = 15
REDC = (255, 68, 51)
GAINC = (123, 224, 123)
NETC = (92, 225, 255)
PLANC = (255, 226, 0)
SALMON = (255, 128, 118)
CREAMC = (255, 244, 214)
SOAKC = (255, 150, 40)           # SOAK token: placeholder, the hue is proposed by the slice owner (bible 3.3: must leave #FF8C1A)
INKD = (8, 5, 12)
REG = E.REG


def P(r, th, px_along):
    return ppx(C, r, th + px_along * 57.3 / r)


def tang(th):
    a = math.radians(th)
    return math.cos(a), math.sin(a)


# ----------------------------------------------------------------------------- the chevron / diamond / check primitives (px-sized)
def chev_one(L, r, th, hw, dp, col, ink_w, col_w, hollow=False, core=None):
    """one chevron at centre angle th, apex toward the tower (inward)"""
    p = [P(r + dp / 2, th, -hw), P(r - dp / 2, th, 0), P(r + dp / 2, th, hw)]
    if hollow:
        L.line(p, INK, ink_w + 2.2)
        L.line(p, col, col_w + 1.8)
        L.line(p, (8, 5, 12), max(1.6, col_w - 1.8))
    else:
        L.line(p, INK, ink_w)
        L.line(p, col, col_w)


def diamond(L, x, y, rw, rh, fill=None, outline=None, ink=2.2, ow=0):
    pts = [(x, y - rh), (x + rw, y), (x, y + rh), (x - rw, y)]
    L.poly(pts, fill=fill, outline=INK if outline is None else outline, w=ink if outline is None else ow)


def check(L, x, y, s=1.0, col=GAINC, inkw=7.2, w=3.8):
    p = [(x - 8 * s, y + 0.5 * s), (x - 2.4 * s, y + 6.5 * s), (x + 8.6 * s, y - 7 * s)]
    L.line(p, INK, inkw * s)
    L.line(p, col, w * s)


# ----------------------------------------------------------------------------- start cluster marks
def disc(L, r, th, px, u, lane, opt):
    """returns width"""
    x, y = P(r, th, px)
    kc = KCOL[u['kind']]
    col_lane = lane['col']
    if opt == 'cur':
        L.ellipse([x - 19, y - 19, x + 19, y + 19], fill=tuple(int(v * 0.62) for v in kc) + (255,), outline=col_lane, w=2.8)
        L.glyph(KIND[u['kind']][1], 28, (x, y), WHITE)
        return 38
    R = 13.5
    if opt == 'A':       # the board token, exact family: same fill (kind colour x0.72) and the lane-style base ring (solid / solid / 14 dashes)
        L.ellipse([x - R - 1.4, y - R - 1.4, x + R + 1.4, y + R + 1.4], fill=INK)
        lane_base_style(L, x, y, R, u['dep'], kc)
        L.glyph(KIND[u['kind']][1], 21, (x, y), WHITE)
    elif opt == 'B':     # lane-coloured cap tile: the start of the arc IS the badge (rounded tile in the lane colour, dark inner, white glyph)
        L.rect([x - 15, y - 14, x + 15, y + 14], fill=col_lane if lane['dash'] is None else (150, 156, 176), outline=INK, w=2.6, r=6)
        L.rect([x - 11.2, y - 10.4, x + 11.2, y + 10.4], fill=tuple(int(v * 0.5) for v in kc) + (255,), r=4)
        L.glyph(KIND[u['kind']][1], 19, (x, y), WHITE)
    else:                # C: programme-wash token: filled with the unit-screen mauve (KWASH) the body cell uses, lane ring, ink pool
        wc = E.KWASH.get(u['kind'], (118, 68, 106))
        L.ellipse([x - 16.5, y - 16.5, x + 16.5, y + 16.5], fill=(4, 6, 14, 190))
        L.ellipse([x - 13.5, y - 13.5, x + 13.5, y + 13.5], fill=wc, outline=col_lane, w=2.6)
        L.glyph(KIND[u['kind']][1], 21, (x, y), WHITE)
    return 33 if opt != 'B' else 36


def lane_base_style(L, x, y, r, dep, fillcol):
    import cv_over as O
    O.lane_base_style(L, x, y, r, dep, fillcol)


def wear(L, r, th, px, opt):
    x, y = P(r, th, px)
    if opt == 'cur':
        L.rect([x - 9, y - 9, x + 9, y + 9], fill=GREEN, outline=INK, w=1.6, r=2)
        L.line([(x - 4, y - 9), (x, y - 2), (x - 2, y + 2), (x + 4, y + 9)], WHITE, 2.2)
        return 28
    ux, uy = tang(th)
    nx, ny = -uy, ux
    def q(a, b):      # a along the arc, b radial (outward +)
        return (x + ux * a + (-ny) * 0 + (math.sin(math.radians(th))) * b, y + uy * a - (math.cos(math.radians(th))) * b)
    if opt == 'A':       # a slice pip lost: salmon capsule (slice_pip_lost_harm family) with the white slash, ink keyline
        pts = [q(-10, -4.6), q(10, -4.6), q(10, 4.6), q(-10, 4.6)]
        L.rect([x - 11.5, y - 6.2, x + 11.5, y + 6.2], fill=SALMON, outline=INK, w=2.0, r=6) if False else None
        cx = [q(a, b) for a in (-10, 10) for b in (-5, 5)]
        L.poly([q(-8, -5), q(8, -5), q(11, 0), q(8, 5), q(-8, 5), q(-11, 0)], fill=SALMON, outline=INK, w=2.2)
        L.line([q(-4, 6), q(4, -6)], INK, 4.2)
        L.line([q(-4, 6), q(4, -6)], WHITE, 2.0)
    elif opt == 'B':     # cracked pip: the capsule in two offset halves with a gap
        L.poly([q(-11, -5), q(-1.5, -5), q(-3.5, 5), q(-8, 5), q(-11, 1)], fill=SALMON, outline=INK, w=2.0)
        L.poly([q(3.5, -5.5), q(8, -5.5), q(11, -1), q(11, 5.5), q(1.5, 5.5)], fill=SALMON, outline=INK, w=2.0)
    else:                # C: ghost pip: hollow salmon capsule with a diagonal hatch (a pip that WILL be lost)
        L.poly([q(-8, -5), q(8, -5), q(11, 0), q(8, 5), q(-8, 5), q(-11, 0)], fill=(30, 12, 14), outline=INK, w=4.2)
        L.poly([q(-8, -5), q(8, -5), q(11, 0), q(8, 5), q(-8, 5), q(-11, 0)], fill=None, outline=SALMON, w=2.0)
        for a in (-5, 0, 5):
            L.line([q(a - 2.5, 3.5), q(a + 2.5, -3.5)], SALMON, 1.6)
    return 28


def twist_mark(L, r, th, px, opt, dirn):
    x, y = P(r, th, px)
    if opt == 'cur':
        L.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(30, 26, 6), outline=PLANC, w=2.4)
        L.glyph('C_TWIST', 17, (x, y), PLANC)
        return 30
    if opt == 'A':       # quiet disc: 20 px ink disc, 1.8 px plan ring, glyph 16 (the floor) in plan yellow
        L.ellipse([x - 10.8, y - 10.8, x + 10.8, y + 10.8], fill=(12, 10, 4), outline=INK, w=3.2)
        L.ellipse([x - 9.4, y - 9.4, x + 9.4, y + 9.4], fill=(14, 12, 4), outline=PLANC, w=1.6)
        L.glyph('C_TWIST', 16, (x, y), PLANC)
        return 26
    if opt == 'B':       # glyph only with an ink keyline: no disc, so the mark carries no area
        L.glyph('C_TWIST', 19, (x, y), PLANC)
        return 22
    ux, uy = tang(th)    # C: the ring-tag badge in miniature: disc + the direction chevrons (one per step)
    L.ellipse([x - 10.8, y - 10.8, x + 10.8, y + 10.8], fill=(12, 10, 4), outline=INK, w=3.2)
    L.ellipse([x - 9.4, y - 9.4, x + 9.4, y + 9.4], fill=(14, 12, 4), outline=PLANC, w=1.6)
    L.glyph('C_TWIST', 15, (x, y), PLANC)
    for q_ in range(1 + (1 if abs(dirn) > 1 else 0)):
        xx = x + ux * (16 + q_ * 6.5)
        yy = y + uy * (16 + q_ * 6.5)
        p = [(xx - 2.6 * ux - 5 * -uy, yy - 2.6 * uy - 5 * ux), (xx + 2.6 * ux, yy + 2.6 * uy), (xx - 2.6 * ux + 5 * -uy, yy - 2.6 * uy + 5 * ux)]
        L.line(p, INK, 5.2)
        L.line(p, PLANC, 2.6)
    return 38 if abs(dirn) > 1 else 32


def now_dot(L, r, th, px, opt):
    x, y = P(r, th, px)
    if opt == 'cur':
        L.ellipse([x - 8, y - 8, x + 8, y + 8], fill=REDC, outline=WHITE, w=2.2)
        return 24
    if opt == 'A':       # 18 px dot in the turn-dot slot: red, white ring, ink outside
        L.ellipse([x - 10.4, y - 10.4, x + 10.4, y + 10.4], fill=INK)
        L.ellipse([x - 9, y - 9, x + 9, y + 9], fill=REDC, outline=WHITE, w=2.4)
        return 26
    if opt == 'B':       # target dot: red core, white ring, with four short white ticks at the cardinals (impact reticle, not a badge)
        L.ellipse([x - 8.6, y - 8.6, x + 8.6, y + 8.6], fill=INK)
        L.ellipse([x - 7.2, y - 7.2, x + 7.2, y + 7.2], fill=REDC, outline=WHITE, w=2.0)
        for a in range(0, 360, 90):
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            L.line([(x + c * 10.5, y + s * 10.5), (x + c * 13.8, y + s * 13.8)], INK, 3.6)
            L.line([(x + c * 10.5, y + s * 10.5), (x + c * 13.4, y + s * 13.4)], WHITE, 1.8)
        return 32
    L.ellipse([x - 10.4, y - 10.4, x + 10.4, y + 10.4], fill=INK)    # C: red dot with two red rays either side (a landing burst), no white ring
    L.ellipse([x - 8, y - 8, x + 8, y + 8], fill=REDC, outline=(255, 214, 206), w=1.6)
    ux, uy = tang(th)
    for sg in (-1, 1):
        p0 = (x + ux * sg * 13, y + uy * sg * 13)
        p1 = (x + ux * sg * 19, y + uy * sg * 19)
        L.line([p0, p1], INK, 5.2)
        L.line([p0, p1], REDC, 2.8)
    return 40


def turn_dots(L, r, th, px, k, opt):
    if opt == 'cur':
        for i in range(k):
            x, y = P(r, th, px + 7 + i * 14)
            L.ellipse([x - 5, y - 5, x + 5, y + 5], fill=WHITE, outline=INK, w=1.4)
        return 14 * k + 4
    if opt == 'A':       # dots in a pill slot: the pill (ink capsule, lane-neutral hairline) says "a count of turns", the dots are white
        w = 12 + k * 13
        x0, y0 = P(r, th, px + w / 2)
        pts = [P(r + 8.5, th, px), P(r + 8.5, th, px + w), P(r - 8.5, th, px + w), P(r - 8.5, th, px)]
        L.poly(pts, fill=(14, 16, 28), outline=INK, w=3.2)
        L.poly(pts, fill=None, outline=(150, 164, 190), w=1.2)
        for i in range(k):
            x, y = P(r, th, px + 12 + i * 13)
            L.ellipse([x - 4.8, y - 4.8, x + 4.8, y + 4.8], fill=WHITE, outline=INK, w=1.2)
        return w + 6
    if opt == 'B':       # tallies: upright white bars 3 x 14 (the tally family used in the bill), one per turn
        for i in range(k):
            x, y = P(r, th, px + 6 + i * 8)
            ux, uy = tang(th)
            nx, ny = math.sin(math.radians(th)), -math.cos(math.radians(th))
            a_, b_ = (x + nx * 7, y + ny * 7), (x - nx * 7, y - ny * 7)
            L.line([a_, b_], INK, 6.0)
            L.line([a_, b_], WHITE, 3.0)
        return 8 * k + 10
    for i in range(k):   # C: hollow rings (white outline, dark core): distinct from the filled wave-arc width dots and from the white dashes
        x, y = P(r, th, px + 8 + i * 17)
        L.ellipse([x - 7.2, y - 7.2, x + 7.2, y + 7.2], fill=INK)
        L.ellipse([x - 5.4, y - 5.4, x + 5.4, y + 5.4], fill=(14, 16, 28), outline=WHITE, w=2.2)
    return 17 * k + 6


# ----------------------------------------------------------------------------- per-sector marks
CH = {'cur': dict(hw=8, dp=13, pitch=21, ink=9.5, col=5.4), 'A': dict(hw=11, dp=10, pitch=25, ink=9.8, col=5.8), 'B': dict(hw=10, dp=6, pitch=6.2, ink=7.4, col=4.0),
      'C': dict(hw=7.5, dp=11, pitch=15, ink=9.0, col=5.0)}


def chev_width(n, opt):
    p = CH[opt]
    if opt == 'B':
        return p['hw'] * 2 + 2
    if opt == 'C':
        return n * p['pitch'] + 8
    return n * p['pitch']


def chevrons(L, r, th, x0, ns, ng, opt):
    """x0 = px offset (from sector centre) of the first chevron's left edge"""
    p = CH[opt]
    n = ns + ng
    if opt == 'cur' or opt == 'A':
        for i in range(n):
            chev_one(L, r, th + (x0 + p['pitch'] / 2 + i * p['pitch']) * 57.3 / r, p['hw'], p['dp'], REDC, p['ink'], p['col'], hollow=i >= ns) if False else None
            chev_one_at(L, r, th, x0 + p['pitch'] / 2 + i * p['pitch'], p, i >= ns)
    elif opt == 'B':     # nested radial stack, exactly the body-chevron grammar (inward V, hollow outermost) at lane scale
        for i in range(n):
            rr = r - 9 + i * p['pitch'] + 3 if False else r + 9 - i * p['pitch'] * (-1)
        for i in range(n):
            rr = r - (n - 1) * p['pitch'] / 2 + i * p['pitch']
            hollow = i >= ns
            # body stack: solid chevrons innermost (i=0 nearest the tower), hollow outward
            rr = r - ((n - 1) * p['pitch']) / 2 + i * p['pitch']
            q = [P(rr + p['dp'], th, x0 + p['hw']), P(rr, th, x0 + p['hw'] * 0 + 0) if False else P(rr, th, x0 + p['hw']), P(rr + p['dp'], th, x0 + p['hw'])]
            xc = x0 + p['hw']
            q = [P(rr + p['dp'], th, xc - p['hw']), P(rr, th, xc), P(rr + p['dp'], th, xc + p['hw'])]
            if hollow:
                L.line(q, INK, p['ink'] + 2)
                L.line(q, REDC, p['col'] + 1.6)
                L.line(q, INKD, max(1.4, p['col'] - 1.6))
            else:
                L.line(q, INK, p['ink'])
                L.line(q, REDC, p['col'])
    else:                # C: continuous zig-zag saw: n chevrons joined; the hollow tail is an outlined (dark core) zig-zag continuing the stroke
        pts = []
        for i in range(n):
            xa = x0 + 4 + i * p['pitch']
            pts += [(xa, p['dp'] / 2), (xa + p['pitch'] / 2, -p['dp'] / 2)]
        pts.append((x0 + 4 + n * p['pitch'], p['dp'] / 2))
        sc = [P(r + dy, th, xa) for xa, dy in pts]
        # r+dy with dy>0 outward; the V apex (inward) is the -dy points
        sc = []
        for i in range(n):
            xa = x0 + 4 + i * p['pitch']
            sc.append((P(r + p['dp'] / 2, th, xa), P(r - p['dp'] / 2, th, xa + p['pitch'] / 2)))
        solid = []
        for i in range(n + 1):
            xa = x0 + 4 + i * p['pitch']
            solid.append(P(r + p['dp'] / 2, th, xa))
            if i < n:
                solid.append(P(r - p['dp'] / 2, th, xa + p['pitch'] / 2))
        cut = 2 * ns + 1
        a = solid[:cut]
        b = solid[cut - 1:]
        if len(a) > 1:
            L.line(a, INK, p['ink'])
            L.line(a, REDC, p['col'])
        if ng and len(b) > 1:
            L.line(b, INK, p['ink'] + 2)
            L.line(b, REDC, p['col'] + 1.6)
            L.line(b, INKD, max(1.4, p['col'] - 1.6))


def chev_one_at(L, r, th, xpx, p, hollow):
    chev_one(L, r, th + xpx * 57.3 / r, p['hw'], p['dp'], REDC, p['ink'], p['col'], hollow)


DI = {'cur': dict(pitch=19), 'A': dict(pitch=22), 'B': dict(pitch=24), 'C': dict(pitch=24)}


def diam_width(n, opt):
    return n * DI[opt]['pitch']


def diamonds(L, r, th, x0, n, opt, k):
    pitch = DI[opt]['pitch']
    for i in range(n):
        x, y = P(r, th, x0 + pitch / 2 + i * pitch)
        if opt == 'cur':
            diamond(L, x, y, 8, 9.5, fill=REDC)
        elif opt == 'A':     # 11 x 13: bigger than any chevron on the arc; later turns darker (the sum of the SOLID bright ones = THROUGH)
            col = REDC if k == 0 else (178, 48, 38)
            diamond(L, x, y, 10.5, 12.5, fill=col, ink=2.6)
        elif opt == 'B':     # socket tile (the HP-pip socket language): the diamond sits in a dark tile; later turns get a dashed lane-grey tile edge
            L.rect([x - 10.5, y - 13.5, x + 10.5, y + 13.5], fill=(14, 8, 14), outline=INK, w=2.6, r=3) if False else None
            tx, ty = tang(th)
            nx, ny = math.sin(math.radians(th)), -math.cos(math.radians(th))
            tile = [(x - tx * 10.5 - nx * 13, y - ty * 10.5 - ny * 13), (x + tx * 10.5 - nx * 13, y + ty * 10.5 - ny * 13), (x + tx * 10.5 + nx * 13, y + ty * 10.5 + ny * 13), (x - tx * 10.5 + nx * 13, y - ty * 10.5 + ny * 13)]
            L.poly(tile, fill=(30, 10, 16), outline=INK, w=3.0)
            if k:
                L.line(tile + [tile[0]], (170, 100, 100), 1.4, dash=(3, 3))
            diamond(L, x, y, 7.6, 9.6, fill=REDC, ink=2.0)
        else:                # C: 12 x 14 with a white glint on the upper-left facet; later turns: outline only (ghost) so they never add to THROUGH by eye
            if k == 0:
                diamond(L, x, y, 11, 13, fill=REDC, ink=2.8)
                L.line([(x - 5.5, y - 1.5), (x - 0.5, y - 7)], (255, 214, 206), 1.8)
            else:
                diamond(L, x, y, 11, 13, fill=(40, 12, 16), ink=2.8)
                diamond(L, x, y, 8.6, 10.6, fill=None, outline=REDC, ow=2.6)


def check_mark(L, r, th, x0, opt, width=24):
    x, y = P(r, th, x0 + width / 2)
    if opt == 'cur':
        check(L, x, y)
    elif opt == 'A':     # big check, 24 px
        check(L, x, y, 1.3, GAINC, 7.6, 4.2)
    elif opt == 'B':     # check inside the diamond slot's outline: "the diamond is empty"
        diamond(L, x, y, 12, 14, fill=(8, 22, 12), outline=INK, ow=4.4)
        diamond(L, x, y, 12, 14, fill=None, outline=GAINC, ow=2.0)
        check(L, x, y + 0.5, 0.78, GAINC, 6.4, 3.2)
    else:                # C: check in a rounded pip tile (the resource-pip shape, not a heal cross)
        L.rect([x - 12, y - 11, x + 12, y + 11], fill=(8, 22, 12), outline=INK, w=4.0, r=5)
        L.rect([x - 12, y - 11, x + 12, y + 11], fill=None, outline=GAINC, w=1.8, r=5)
        check(L, x, y, 0.8, (210, 255, 210), 6.0, 3.0)


def soak_mark(L, r, th, x0, opt, width=22):
    x, y = P(r, th, x0 + width / 2)
    tx, ty = tang(th)
    nx, ny = math.sin(math.radians(th)), -math.cos(math.radians(th))
    def q(a, b):
        return (x + tx * a + nx * b, y + ty * a + ny * b)
    if opt == 'cur':
        p = [P(r + 6, th, x0 + 7.5 - 6.5), P(r - 5, th, x0 + 7.5), P(r + 6, th, x0 + 7.5 + 6.5)]
        L.line(p, INK, 8.5)
        L.line(p, SOAKC, 5)
        return
    if opt == 'A':       # one slice pip, soak colour: the capsule of slice_pip_lost_soak, 9 x 21, with ink keyline and a dark core stripe
        pts = [q(-4.5, -10.5), q(4.5, -10.5), q(4.5, 10.5), q(-4.5, 10.5)]
        L.poly([q(-4.5, -8), q(-2, -10.5), q(2, -10.5), q(4.5, -8), q(4.5, 8), q(2, 10.5), q(-2, 10.5), q(-4.5, 8)], fill=SOAKC, outline=INK, w=2.4)
        L.line([q(0, -6), q(0, 6)], (120, 60, 8), 1.6)
    elif opt == 'B':     # catcher: a cup (U) that holds the pip: the slice absorbs it. cup in soak colour, pip is the ink-edged capsule inside
        cup = [q(-9, 9), q(-9, -1), q(-9, 9)]
        L.line([q(-10, 4), q(-10, -9), q(10, -9), q(10, 4)], INK, 6.6)
        L.line([q(-10, 4), q(-10, -9), q(10, -9), q(10, 4)], SOAKC, 3.0)
        L.poly([q(-3.6, 5.5), q(3.6, 5.5), q(3.6, -5), q(-3.6, -5)], fill=SOAKC, outline=INK, w=2.0)
    else:                # C: split pip: half the capsule filled soak, half hollow (one pip, soaked into the slice instead of HP)
        L.poly([q(-4.5, -8), q(-2, -10.5), q(2, -10.5), q(4.5, -8), q(4.5, 8), q(2, 10.5), q(-2, 10.5), q(-4.5, 8)], fill=(22, 12, 4), outline=INK, w=4.2)
        L.poly([q(-4.5, 0), q(4.5, 0), q(4.5, 8), q(2, 10.5), q(-2, 10.5), q(-4.5, 8)], fill=SOAKC)
        L.poly([q(-4.5, -8), q(-2, -10.5), q(2, -10.5), q(4.5, -8), q(4.5, 8), q(2, 10.5), q(-2, 10.5), q(-4.5, 8)], fill=None, outline=SOAKC, w=1.8)


def brace_mark(L, r, th, x0, opt, width=24):
    x, y = P(r, th, x0 + width / 2)
    if opt == 'cur':
        L.glyph('C_BRACE', 28, (x, y), CREAMC)
        return
    tx, ty = tang(th)
    nx, ny = math.sin(math.radians(th)), -math.cos(math.radians(th))
    def q(a, b):
        return (x + tx * a + nx * b, y + ty * a + ny * b)
    if opt == 'A':       # clamp jaws round a slot, player-side cyan, 22 px: two C-jaws and a spine
        L.line([q(-9, 8), q(-9, -8), q(9, -8), q(9, 8)], INK, 8.0)
        L.line([q(-9, 8), q(-9, -8), q(9, -8), q(9, 8)], NETC, 4.0)
        L.line([q(-9, 0), q(-3, 0)], INK, 7.0); L.line([q(-9, 0), q(-3, 0)], NETC, 3.2)
        L.line([q(9, 0), q(3, 0)], INK, 7.0); L.line([q(9, 0), q(3, 0)], NETC, 3.2)
    elif opt == 'B':     # plate in miniature: the brace_plate's rounded plate with two rivets, cream plate, ink keyline (colour stays open call 2)
        L.rect([x - 11.5, y - 9.5, x + 11.5, y + 9.5], fill=(70, 62, 44), outline=INK, w=3.6, r=4)
        L.rect([x - 11.5, y - 9.5, x + 11.5, y + 9.5], fill=None, outline=CREAMC, w=2.2, r=4)
        for dx in (-7, 7):
            L.ellipse([x + dx - 2.2, y - 2.2, x + dx + 2.2, y + 2.2], fill=INK, outline=CREAMC, w=1.0)
        L.line([(x - 3, y), (x + 3, y)], CREAMC, 2.2)
    else:                # C: glyph token: C_BRACE 18 px white in a 24 px dark disc with a cyan ring (same token family as the arc kind disc)
        L.ellipse([x - 12.5, y - 12.5, x + 12.5, y + 12.5], fill=(8, 18, 26), outline=INK, w=3.4)
        L.ellipse([x - 11, y - 11, x + 11, y + 11], fill=(8, 18, 26), outline=NETC, w=1.8)
        L.glyph('C_BRACE', 17, (x, y), WHITE)


# ----------------------------------------------------------------------------- the frame
def frame(L, r, a0, a1, lane, opt, dep):
    col_lane = lane['col']
    dash = lane['dash']
    if opt == 'cur':
        pts = L.band(C, r - HALF, r + HALF, a0, a1)
        L.poly(pts, fill=(7, 9, 17, 205), outline=None)
        L.line(pts + [pts[0]], INK, 6)
        L.line(pts + [pts[0]], col_lane, 2.6, dash=dash)
        return
    da = 57.3 / r
    if opt == 'A':       # capsule: round start cap (holds the kind disc), arrow-point end (clockwise), lane-style 3 px outline
        cap = HALF * da
        pts = []
        n = max(8, int((a1 - a0) / 3))
        outer = [ppx(C, r + HALF, a0 + cap + (a1 - 2 * cap - a0) * i / n) for i in range(n + 1)] if False else None
        ae = a1 - 0.9 * HALF * da
        outer = [ppx(C, r + HALF, a0 + cap + (ae - a0 - cap) * i / n) for i in range(n + 1)]
        inner = [ppx(C, r - HALF, ae - (ae - a0 - cap) * i / n) for i in range(n + 1)]
        tipp = [ppx(C, r, a1)]
        start = [ppx(C, r + HALF * math.sin(math.radians(t)), a0 + cap - cap * math.cos(math.radians(t))) for t in range(0, 181, 15)][::-1]
        start = [ppx(C, r - HALF * math.cos(math.radians(t)), a0 + cap - cap * math.sin(math.radians(t))) for t in range(0, 181, 20)]
        start = [ppx(C, r + HALF * math.cos(math.radians(t)), a0 + cap - cap * math.sin(math.radians(t))) for t in range(0, 181, 20)]
        pts = outer + tipp + inner + start
        L.poly(pts, fill=(7, 9, 17, 214))
        L.line(pts + [pts[0]], INK, 6.4)
        L.line(pts + [pts[0]], col_lane, 2.8, dash=dash)
    elif opt == 'B':     # compartment ticket: square caps (thick start bar, thin end bar) + a hairline divider on every sector boundary so each landing sector is its own compartment
        pts = L.band(C, r - HALF, r + HALF, a0, a1)
        L.poly(pts, fill=(7, 9, 17, 214))
        L.line(pts + [pts[0]], INK, 6.2)
        L.line(pts + [pts[0]], col_lane, 2.6, dash=dash)
        L.line([ppx(C, r - HALF - 1, a0), ppx(C, r + HALF + 1, a0)], INK, 8.4)
        L.line([ppx(C, r - HALF, a0 + 0.1), ppx(C, r + HALF, a0 + 0.1)], col_lane, 4.2)
        L.line([ppx(C, r - HALF - 1, a1), ppx(C, r + HALF + 1, a1)], INK, 6.0)
        L.line([ppx(C, r - HALF, a1), ppx(C, r + HALF, a1)], col_lane, 2.2)
    else:                # C: bracket frame: no band fill beyond a 45 percent glass; lane outline only on the long edges; corner brackets at both ends
        pts = L.band(C, r - HALF, r + HALF, a0, a1)
        L.poly(pts, fill=(7, 9, 17, 150))
        L.line(L.arc_pts(C, r + HALF, a0, a1), INK, 5.6); L.line(L.arc_pts(C, r + HALF, a0, a1), col_lane, 2.4, dash=dash)
        L.line(L.arc_pts(C, r - HALF, a0, a1), INK, 5.6); L.line(L.arc_pts(C, r - HALF, a0, a1), col_lane, 2.4, dash=dash)
        for (aa_, sg) in ((a0, 1), (a1, -1)):
            br = [ppx(C, r + HALF, aa_ + sg * 8 * da), ppx(C, r + HALF, aa_), ppx(C, r - HALF, aa_), ppx(C, r - HALF, aa_ + sg * 8 * da)]
            L.line(br, INK, 7.0)
            L.line(br, col_lane, 3.4)


# ----------------------------------------------------------------------------- the whole arc
def landing_arcs(L, f, sel, only=None):
    items = []
    for u in f['units']:
        if u['consumed'] or u['trigdead']:
            continue
        if only is not None and u['id'] not in only:
            continue
        fz = u['fate']
        if fz['kind'] != 'lands' or 'land_hit' not in u:
            continue
        s0 = E._land_start(u['land_sectors'])
        a0, a1 = 60 * s0 - 29, 60 * (s0 + u['w'] - 1) + 29
        items.append(dict(u=u, k=fz['k'], a0=a0, a1=a1, s0=s0))
    items.sort(key=lambda it: (it['k'], it['a0'] % 360))
    lanes = []
    for it in items:
        e0, e1 = it['a0'] % 360, it['a0'] % 360 + (it['a1'] - it['a0'])
        lane = 0
        while True:
            clash = False
            for (l_, g0, g1) in lanes:
                if l_ != lane:
                    continue
                for sh in (-360, 0, 360):
                    if e0 < g1 + 2 + sh and g0 + sh < e1 + 2:
                        clash = True
            if not clash:
                break
            lane += 1
        lanes.append((lane, e0, e1))
        it['lane'] = lane
    S = lambda key: sel.get(key, 'cur')
    for it in items:
        u, k = it['u'], it['k']
        r = LANE_R[min(it['lane'], 2)]
        a0, a1 = it['a0'], it['a1']
        lane = LANE[u['dep']]
        da = 57.3 / r
        frame(L, r, a0, a1, lane, S('frame'), u['dep'])
        cur = 6 if S('frame') in ('cur',) else 8
        if S('disc') == 'cur':
            cur = 24
        px = cur
        wd = disc(L, r, a0, px + (19 if S('disc') == 'cur' else 17) * 0 + 0, u, lane, S('disc')) if False else None
        # start cluster, px measured from a0
        if S('disc') == 'cur':
            wd = disc(L, r, a0, 24 / da * da if False else 24, u, lane, 'cur'); px = 24 + 24
        else:
            wd = disc(L, r, a0, 22, u, lane, S('disc')); px = 22 + wd / 2 + 6
        if u.get('wear'):
            w_ = wear(L, r, a0, px + 12, S('wear'))
            px += w_ if S('wear') != 'cur' else 28
        if f.get('twr') and f['twr'][1] and f['twr'][0] == u['dep'] and k > 0:
            w_ = twist_mark(L, r, a0, px + 13, S('twist'), f['twr'][1])
            px += w_
        if k == 0:
            w_ = now_dot(L, r, a0, px + 11, S('now'))
            px += w_
        else:
            w_ = turn_dots(L, r, a0, px, k, S('turn'))
            px += w_
        ng = max(0, u['land_hit'] - min(u['hit'], u['land_hit']))
        ns = u['land_hit'] - ng
        for q in range(u['w']):
            sec = (it['s0'] + q) % 6
            th = 60 * (it['s0'] + q)
            thr = u['land_through'].get(str(sec), 0)
            sk = u['land_soak'].get(str(sec), 0)
            br = u['land_brace'].get(str(sec), 0)
            REG['arcs'].append(dict(uid=u['id'], sector=sec, solid=ns, hollow=ng, diamonds=thr, soak=sk, brace=br, check=int(not thr and not br and not sk), k=k, now_dot=int(k == 0), wear=int(bool(u.get('wear'))), lane=it['lane']))
            n_items = ns + ng
            wch = chev_width(n_items, S('achev'))
            gap = 14
            sl_w = 24
            wdi = diam_width(thr, S('diam')) + (sk * (22 if S('soak') != 'cur' else 15)) + (26 if br else 0) + (26 if (not thr and not br and not sk) else 0)
            tot = wch + gap + wdi
            x0 = -tot / 2
            chevrons(L, r, th, x0, ns, ng, S('achev'))
            x1 = x0 + wch + gap
            if br:
                brace_mark(L, r, th, x1, S('brace'))
                x1 += 26
            if thr:
                diamonds(L, r, th, x1, thr, S('diam'), k)
                x1 += diam_width(thr, S('diam'))
            for i in range(sk):
                soak_mark(L, r, th, x1, S('soak'))
                x1 += 22 if S('soak') != 'cur' else 15
            if not thr and not br and not sk:
                check_mark(L, r, th, x1, S('check'))
    return items
