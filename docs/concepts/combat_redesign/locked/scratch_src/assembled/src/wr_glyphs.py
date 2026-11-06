"""Unit-kind glyph options (512 grid masks, drawn at 2x and reduced).  Registered into crests15.CUSTOM under WR_<KIND>_<opt>.
Rules (BRIEF 3.8): white silhouette + ink keyline, 2-3 parts, no cut thinner than ~36 units (2 px at 37 px), no diamond, no media shape, no letter."""
import math
import crests15 as _c15
import bb_lib as B
from PIL import Image, ImageDraw

S2 = 1024


def _mask(fn):
    def f():
        m = Image.new('L', (S2, S2), 0)
        d = ImageDraw.Draw(m)
        fn(d)
        return m.resize((512, 512), Image.LANCZOS)
    return f


def P(pts):
    return [(x * 2, y * 2) for x, y in pts]


def box(b):
    return [v * 2 for v in b]


def circ(d, cx, cy, r, fill=255):
    d.ellipse(box([cx - r, cy - r, cx + r, cy + r]), fill=fill)


def thick(d, pts, w, fill=255):
    d.line(P(pts), fill=fill, width=int(w * 2), joint='curve')
    for p in (pts[0], pts[-1]):
        circ(d, p[0], p[1], w / 2, fill)


def bez(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        a = (1 - t) ** 3; b = 3 * (1 - t) ** 2 * t; c = 3 * (1 - t) * t * t; e = t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + e * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + e * p3[1]))
    return out


# ---------------------------------------------------------------- Packet: the data parcel
def packet_A(d):          # isometric parcel cube: hexagon with the three edges cut as a Y (reads 'box / packet', echoes the iso cutaway)
    R = 218
    cx, cy = 256, 262
    hx = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in (-90, -30, 30, 90, 150, 210)]
    d.polygon(P(hx), fill=255)
    for a in (150, 30, 270):
        x = cx + R * 0.98 * math.cos(math.radians(a)); y = cy + R * 0.98 * math.sin(math.radians(a))
        d.line(P([(cx, cy), (x, y)]), fill=0, width=2 * 34)
    circ(d, cx, cy, 17, 0)


def packet_B(d):          # sealed envelope: a flat rectangle with the flap V cut (message in transit)
    d.rounded_rectangle(box([40, 112, 472, 400]), radius=2 * 36, fill=255)
    d.line(P([(58, 132), (256, 292), (454, 132)]), fill=0, width=2 * 38, joint='curve')


def packet_C(d):          # three stacked slabs, each offset (a queue of data layers), not a media square
    for i, (x0, x1) in enumerate(((70, 440), (40, 410), (100, 470))):
        y0 = 70 + i * 140
        d.rounded_rectangle(box([x0, y0, x1, y0 + 104]), radius=2 * 30, fill=255)

# ---------------------------------------------------------------- Worm
def worm_A(d):            # bead chain climbing an S: four beads, the head biggest with an eye
    beads = [(88, 404, 56), (184, 312, 68), (284, 244, 76), (388, 166, 96)]
    for i in range(3):
        (x0, y0, r0), (x1, y1, r1) = beads[i], beads[i + 1]
        thick(d, [(x0, y0), (x1, y1)], min(r0, r1) * 1.3)
    for (x, y, r) in beads:
        circ(d, x, y, r)
    circ(d, 404, 148, 24, 0)

def worm_B(d):            # one thick S-curve snake, tapered tail, head with an eye
    pts = bez((60, 424), (60, 230), (440, 340), (420, 120), 50)
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        r = 30 + 46 * (i / (n - 1)) ** 0.7
        circ(d, x, y, r)
    hx, hy = pts[-1]
    circ(d, hx + 10, hy - 10, 24, 0)

def worm_C(d):            # a curled worm: a thick spiral coil with the head on the outside and an eye
    pts = []
    for i in range(70):
        t = i / 69
        a = math.radians(-90 + 520 * t)
        r = 52 + 150 * t
        pts.append((256 + r * math.cos(a), 262 + r * math.sin(a)))
    for i, (x, y) in enumerate(pts):
        circ(d, x, y, 30 + 20 * (i / 69))
    hx, hy = pts[-1]
    circ(d, hx, hy, 12, 0)

# ---------------------------------------------------------------- Payload (armored cargo): not a diamond, no equals sign
def payload_A(d):         # a bomb: round body, cap, fuse with a spark
    circ(d, 244, 296, 176)
    d.rectangle(box([192, 98, 296, 150]), fill=255)
    thick(d, [(260, 100), (310, 58), (378, 66)], 36)
    pts = []
    cx, cy = 410, 56
    for i in range(16):
        r = 56 if i % 2 == 0 else 22
        a = math.radians(-90 + 22.5 * i)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(P(pts), fill=255)
    circ(d, 244, 296, 54, 0)


def payload_B(d):         # a sealed drum: tall rounded body with a lid band and a round hatch
    d.rounded_rectangle(box([112, 44, 400, 472]), radius=2 * 56, fill=255)
    d.rectangle(box([112, 118, 400, 152]), fill=0)
    circ(d, 256, 316, 64, 0)
    circ(d, 256, 316, 28, 255)


def payload_C(d):         # a rocket: slender ogive pointing up, two fins, a round window (armoured delivery)
    d.polygon(P(bez((256, 20), (370, 120), (372, 250), (372, 400), 20) + [(140, 400)] + bez((140, 400), (140, 250), (142, 120), (256, 20), 20)), fill=255)
    d.polygon(P([(140, 300), (60, 420), (60, 480), (160, 400)]), fill=255)
    d.polygon(P([(372, 300), (452, 420), (452, 480), (352, 400)]), fill=255)
    d.rectangle(box([180, 392, 332, 484]), fill=255)
    circ(d, 256, 190, 44, 0)

# ---------------------------------------------------------------- Jammer (added: latent) and Ring (added: latent)
def jammer_A(d):          # a signal ring cut into three arcs around a dead centre dot (the link, jammed)
    for k in range(3):
        a0 = 120 * k - 90 + 14
        d.arc(box([50, 50, 462, 462]), a0, a0 + 92, fill=255, width=2 * 62)
    circ(d, 256, 256, 62)

def jammer_B(d):          # a relay pylon: tapered tower, ball on top, a broadcast arc on each side
    d.polygon(P([(256, 120), (330, 480), (182, 480)]), fill=255)
    circ(d, 256, 120, 46)
    for r in (118, 200):
        d.arc(box([256 - r, 120 - r, 256 + r, 120 + r]), -72, -18, fill=255, width=2 * 34)
        d.arc(box([256 - r, 120 - r, 256 + r, 120 + r]), 198, 252, fill=255, width=2 * 34)

def jammer_C(d):          # static comb: seven bars of uneven height on a noise floor, symmetric like a waveform
    hs = [150, 300, 220, 440, 220, 300, 150]
    for i, h in enumerate(hs):
        x = 40 + i * 64
        d.rounded_rectangle(box([x, 256 - h / 2, x + 44, 256 + h / 2]), radius=2 * 22, fill=255)

def ring_A(d):            # orbit ring with three beads
    d.ellipse(box([60, 60, 452, 452]), fill=255)
    d.ellipse(box([140, 140, 372, 372]), fill=0)
    for a in (0, 120, 240):
        x = 256 + 196 * math.sin(math.radians(a)); y = 256 - 196 * math.cos(math.radians(a))
        circ(d, x, y, 58)
        circ(d, x, y, 22, 0)


def ring_B(d):            # a ring cut into six segments (one per sector)
    for k in range(6):
        a0 = 60 * k - 90 + 7
        d.arc(box([50, 50, 462, 462]), a0, a0 + 46, fill=255, width=2 * 78)

def ring_C(d):            # chain loop: two interlocked links
    d.rounded_rectangle(box([30, 150, 300, 362]), radius=2 * 106, outline=255, width=2 * 52)
    d.rounded_rectangle(box([212, 150, 482, 362]), radius=2 * 106, outline=255, width=2 * 52)


FUNCS = dict(PACKET_A=packet_A, PACKET_B=packet_B, PACKET_C=packet_C, WORM_A=worm_A, WORM_B=worm_B, WORM_C=worm_C,
             PAYLOAD_A=payload_A, PAYLOAD_B=payload_B, PAYLOAD_C=payload_C, JAMMER_A=jammer_A, JAMMER_B=jammer_B, JAMMER_C=jammer_C,
             RING_A=ring_A, RING_B=ring_B, RING_C=ring_C)
for k, fn in FUNCS.items():
    _c15.CUSTOM['WR_' + k] = _mask(fn)

KIND_OF = {'glyph_packet': 'Packet', 'glyph_worm': 'Worm', 'glyph_payload': 'Payload', 'glyph_jammer': 'Jammer', 'glyph_ring': 'Ring'}
E_NAME = {'Packet': 'U_PACKET', 'Worm': 'U_WORM', 'Payload': 'U_PAYLOAD', 'Jammer': 'U_JAMMER', 'Ring': 'U_RING'}


def glyph_name(el, kind, o):
    return E_NAME[kind] if o == 'E' else 'WR_%s_%s' % (kind.upper(), o)


def mask_area(name):
    import slicelib as SL
    m = SL.glyph_mask(name)
    import numpy as np
    return float((np.asarray(m) > 127).mean())
