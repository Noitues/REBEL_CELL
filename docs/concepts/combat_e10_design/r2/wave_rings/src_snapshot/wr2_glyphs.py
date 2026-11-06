"""R2 unit-kind glyph masters (512 grid, white silhouette, drawn at 2x, 2-3 parts, no cut under ~2 px at 28 px = 37 units).
Registered as WR_<KIND>_R (the AD-directed pick) and WR_<KIND>_V (the one variant) so the existing glyph hook (wr_glyphs.glyph_name) renders them.
Master-library note: these five are the unit-kind masters this cluster owns; neighbours for the twin check come from the cards library (kglyph KA_*)."""
import math
import numpy as np
import crests15 as _c15
from PIL import Image, ImageDraw, ImageChops, ImageFilter
import wr_glyphs as G
from wr_glyphs import P, box, circ, thick, bez, S2


def _m(fn):
    def f():
        m = Image.new('L', (S2, S2), 0)
        fn(ImageDraw.Draw(m), m)
        return m.resize((512, 512), Image.LANCZOS)
    return f


def _taper(d, pts, r0, r1, pw=0.8):
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        t = i / (n - 1)
        circ(d, x, y, r0 + (r1 - r0) * t ** pw)


# ----------------------------------------------------------------------------- Packet: the parcel cube
def packet_R(d, m):
    """isometric cube: hexagon with the three inner edges cut as a Y.  Cut 38 units (2.7 px at 37 px, 1.4 px at 20 px); the centre keeps no dot."""
    R = 222
    cx, cy = 256, 262
    hx = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in (-90, -30, 30, 90, 150, 210)]
    d.polygon(P(hx), fill=255)
    for a in (150, 30, 270):
        x = cx + R * 1.0 * math.cos(math.radians(a)); y = cy + R * 1.0 * math.sin(math.radians(a))
        d.line(P([(cx, cy), (x, y)]), fill=0, width=2 * 38)
    circ(d, cx, cy, 19, 0)


def packet_V(d, m):
    """cube with the right-hand face hollow (an opened parcel): top and left faces solid, the right face a 40 unit outline"""
    packet_R(d, m)
    cx, cy, R = 256, 262, 222
    face = [(cx, cy), (cx + R * math.cos(math.radians(30)), cy + R * math.sin(math.radians(30))), (cx + R * math.cos(math.radians(-30)), cy + R * math.sin(math.radians(-30))), (cx, cy - R * 0.0 - 0)]
    # hollow the right face: knock out an inset copy of it
    f = [(cx + 38, cy - 4), (cx + 38, cy + R * 0.5 + 8), (cx + R * 0.8, cy + R * 0.34 + 2), (cx + R * 0.8, cy - R * 0.5 - 4)]
    d.polygon(P(f), fill=0)


# ----------------------------------------------------------------------------- Worm: ONE bend (a hook), head bulge, eye, tapered tail
def worm_R(d, m):
    """a hook / J: upright body, a single bend at the foot, tail tapering up-left; the head is a bulge with an eye (never S, never M)"""
    pts = bez((296, 118), (306, 330), (262, 452), (100, 392), 60)
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        t = i / (n - 1)
        r = 70 - 52 * t ** 0.9 if t > 0.12 else 70
        circ(d, x, y, r)
    circ(d, 300, 112, 84)                  # head bulge
    circ(d, 324, 94, 27, 0)                # eye


def worm_V(d, m):
    """a comma: the body bows in one arc (one bend), thick head at the top, the tail curling in; a tadpole read"""
    pts = bez((306, 112), (140, 150), (130, 430), (330, 428), 60)
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        t = i / (n - 1)
        circ(d, x, y, 56 - 42 * t ** 0.8)
    circ(d, 312, 112, 76)
    circ(d, 334, 96, 25, 0)


# ----------------------------------------------------------------------------- Payload: the bomb, fuse >= 2 px at 28 px (>= 37 units)
def _spark(d, cx, cy, ro, ri):
    pts = []
    for i in range(16):
        r = ro if i % 2 == 0 else ri
        a = math.radians(-90 + 22.5 * i)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(P(pts), fill=255)


def payload_R(d, m):
    circ(d, 240, 300, 178)
    d.rectangle(box([186, 96, 294, 152]), fill=255)                       # cap
    thick(d, [(262, 100), (318, 56), (384, 66)], 46)                       # fuse 46 units = 2.5 px at 28 px
    _spark(d, 416, 54, 60, 24)
    circ(d, 240, 300, 56, 0)                                                # the bomb's eye (core)


def payload_V(d, m):
    """armoured bomb: the same body with a cut band across it (a plated shell)"""
    payload_R(d, m)
    d.rectangle(box([50, 258, 430, 282]), fill=0)


# ----------------------------------------------------------------------------- Jammer: relay pylon with BROKEN broadcast arcs
def _pylon(d):
    d.polygon(P([(256, 150), (352, 484), (160, 484)]), fill=255)           # tower
    d.polygon(P([(256, 232), (300, 484 - 130), (212, 484 - 130)]), fill=0)  # open the lattice: a dark triangle in the tower
    circ(d, 256, 140, 52)                                                    # ball


def _arc(d, r, a0, a1, w=40, cy=140):
    d.arc(box([256 - r, cy - r, 256 + r, cy + r]), a0, a1, fill=255, width=2 * w)


def jammer_R(d, m):
    """relay pylon; the broadcast is BROKEN: left inner arc whole, left outer arc in two pieces, right inner arc cut by a gap, right outer arc lost"""
    _pylon(d)
    _arc(d, 118, 196, 252)
    _arc(d, 206, 194, 220); _arc(d, 206, 232, 256)
    _arc(d, 118, -72, -52); _arc(d, 118, -36, -16)


def jammer_V(d, m):
    """the same pylon, symmetric: each side has the inner arc whole and the outer arc cut in two"""
    _pylon(d)
    for (a0, a1) in ((196, 252), (-72, -16)):
        _arc(d, 118, a0, a1)
    for (a0, a1, b0, b1) in ((194, 220, 232, 256), (-76, -52, -40, -16)):
        _arc(d, 206, a0, a1); _arc(d, 206, b0, b1)


# ----------------------------------------------------------------------------- Ring unit: two interlocked chain links, over / under cut
def _stadium(w, h, cx, cy, ang, stroke):
    im = Image.new('L', (S2, S2), 0)
    t = Image.new('L', (S2, S2), 0)
    dd = ImageDraw.Draw(t)
    dd.rounded_rectangle(box([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]), radius=int(h) , outline=255, width=2 * stroke)
    return t.rotate(ang, center=(cx * 2, cy * 2), resample=Image.BICUBIC)


def ring_R(d, m):
    """two stadium links crossing at 104 degrees, one over / one under at the two crossings (a 22 unit gap shows which link passes through)"""
    stroke = 50
    a = np.asarray(_stadium(330, 190, 190, 256, -52, stroke), np.uint8) > 127
    b = np.asarray(_stadium(330, 190, 322, 256, 52, stroke), np.uint8) > 127
    ys, xs = np.nonzero(a & b)
    top = ys < S2 // 2
    yy, xx = np.mgrid[0:S2, 0:S2]
    for sel, b_over in ((top, True), (~top, False)):
        if not sel.any():
            continue
        cx_, cy_ = xs[sel].mean(), ys[sel].mean()
        near = (xx - cx_) ** 2 + (yy - cy_) ** 2 < 150 ** 2
        over = b if b_over else a
        dil = np.asarray(Image.fromarray((over * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * 22 + 1))) > 127
        if b_over:
            a = a & ~(dil & near & ~over)
        else:
            b = b & ~(dil & near & ~over)
    m.paste(Image.fromarray(((a | b) * 255).astype(np.uint8)), (0, 0))


def ring_V(d, m):
    """three links in a short chain (a longer read: the Ring is a whole chain)"""
    stroke = 44
    comb = np.zeros((S2, S2), bool)
    for cx in (120, 256, 392):
        comb |= np.asarray(_stadium(150, 250, cx, 256, 0, stroke)) > 127
    m.paste(Image.fromarray((comb * 255).astype(np.uint8)), (0, 0))


FUNCS = dict(PACKET_R=packet_R, PACKET_V=packet_V, WORM_R=worm_R, WORM_V=worm_V, PAYLOAD_R=payload_R, PAYLOAD_V=payload_V,
             JAMMER_R=jammer_R, JAMMER_V=jammer_V, RING_R=ring_R, RING_V=ring_V)
for k, fn in FUNCS.items():
    _c15.CUSTOM['WR_' + k] = _m(fn)
