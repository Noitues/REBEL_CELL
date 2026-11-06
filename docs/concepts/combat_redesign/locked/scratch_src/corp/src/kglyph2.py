"""R2 GLYPH MASTER LIBRARY (cards own it; every cluster imports it).  Self-contained: nothing here depends on the other clusters' files.
Rules (BRIEF 3.8 / 3.11 item 5): white silhouette, 512 grid (drawn at 1024 and reduced), 2-3 parts, ink outline 7.5 percent added by the renderer,
no knock-out narrower than 20 units (= 1.1 px at 28 px, 2.7 px at 70 px; the tightest cuts are in the brick wall, the spin cuts and the chain gap).
Registered in crests15.CUSTOM as 'KM_<id>'.  mask(id) -> 512x512 'L' image.  export(dir) writes <id>.png (white on transparent) for non-Python consumers.
ids: nudge spin2 spin3 | brace firewall pull shove twist hold trigger strike | crest jammer ring packet payload worm
Plus variants for the twin sheet: spin1v (spin with every segment headed) etc. are NOT shipped; each id has exactly one master (VARIANTS = the one alternative of the AD asks).
"""
import sys, math, os
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import bb_lib  # noqa  (puts r41/scripts on the path)
import crests15 as _c15

S2 = 1024


def P(pts):
    return [(x * 2, y * 2) for x, y in pts]


def box(b):
    return [v * 2 for v in b]


def pol(cx, cy, r, a):
    t = math.radians(a)
    return (cx + r * math.cos(t), cy + r * math.sin(t))


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
        a, b, c, e = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + e * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + e * p3[1]))
    return out


def sector(d, cx, cy, r, w, a0, a1, fill=255, n=40):
    """annular sector, centre-line radius r, width w, angles in PIL degrees (clockwise from 3 o'clock), flat radial ends"""
    ro, ri = r + w / 2, r - w / 2
    pts = [pol(cx, cy, ro, a0 + (a1 - a0) * i / n) for i in range(n + 1)] + [pol(cx, cy, ri, a1 - (a1 - a0) * i / n) for i in range(n + 1)]
    d.polygon(P(pts), fill=fill)


def arrow_head(d, cx, cy, r, w, ang, sweep, flare=0.55, fill=255, ccw=False):
    """triangular head at angle `ang` on the ring: base across the ring (wider than the stroke by `flare`), tip `sweep` degrees further on"""
    s = -1 if ccw else 1
    b1 = pol(cx, cy, r + w * (0.5 + flare), ang)
    b2 = pol(cx, cy, r - w * (0.5 + flare), ang)
    tip = pol(cx, cy, r, ang + s * sweep)
    d.polygon(P([b1, tip, b2]), fill=fill)


# ------------------------------------------------------------------ cards
def spin_fn(n):
    """the tower hub inside one ring cut into n equal steps, the last step carries the arrow head (clockwise).  Same silhouette for every n: the count is the number of cuts."""
    def f(d):
        cx = cy = 256
        r, w = 156, 84
        gap = 40.0
        head = 28.0
        e = -28.0                                  # end of the last (headed) step
        seg = (360.0 - n * gap) / n
        circ(d, cx, cy, 54)
        for k in range(n):
            a1 = e - k * (seg + gap)
            sector(d, cx, cy, r, w, a1 - seg, a1)
        arrow_head(d, cx, cy, r, w, e, head)
    return f


def twist(d):
    """open circular arrow, counter-clockwise, no hub: one 270 degree arc, rounded tail, head (the wave ring turns by itself)"""
    cx = cy = 256
    r, w = 164, 76
    a0 = 200.0                                     # drawn clockwise, mirrored in mask() so the Twist turns the other way from every Spin
    a1 = a0 + 262.0
    sector(d, cx, cy, r, w, a0, a1)
    p = pol(cx, cy, r, a0)
    circ(d, p[0], p[1], w / 2)                     # round tail
    arrow_head(d, cx, cy, r, w, a1, 30)


def hold(d):
    """hourglass: two caps and two bulbs meeting in a 44 unit neck (never a media pause)"""
    d.rounded_rectangle(box([84, 32, 428, 92]), radius=22, fill=255)
    d.rounded_rectangle(box([84, 420, 428, 480]), radius=22, fill=255)
    # bulbs: curved flanks
    def bulb(sign):
        y_cap, y_neck = (92, 252) if sign < 0 else (420, 260)
        pts = []
        for i in range(0, 21):
            t = i / 20
            y = y_cap + (y_neck - y_cap) * t
            half = 154 * (1 - t) ** 0.8 + 24 * t ** 0.8
            if t < 0.15:
                half = 154
            pts.append((256 - half, y))
        for i in range(20, -1, -1):
            t = i / 20
            y = y_cap + (y_neck - y_cap) * t
            half = 154 * (1 - t) ** 0.8 + 24 * t ** 0.8
            if t < 0.15:
                half = 154
            pts.append((256 + half, y))
        return pts
    d.polygon(P(bulb(-1)), fill=255)
    d.polygon(P(bulb(1)), fill=255)


def brace(d):
    """clamp plate (verbatim from card_icon_set A, X4): plate with a trapezoid jaw and four rivets cut out"""
    d.rounded_rectangle(box([44, 56, 468, 456]), radius=88, fill=255)
    d.polygon(P([(150, 104), (362, 104), (304, 408), (208, 408)]), fill=0)
    d.polygon(P([(190, 146), (322, 146), (282, 366), (230, 366)]), fill=255)
    for cx, cy in ((88, 104), (424, 104), (88, 408), (424, 408)):
        circ(d, cx, cy, 18, 0)


def firewall(d):
    """brick wall only (the flame now means Heat): a plate of 4 staggered courses, mortar 22 units (1.2 px at 28 px, 3 px at 70 px)"""
    x0, x1, y0, y1 = 40, 472, 100, 412
    d.rounded_rectangle(box([x0, y0, x1, y1]), radius=34, fill=255)
    mortar = 22
    rows = 4
    rh = (y1 - y0) / rows
    for r in range(1, rows):
        y = y0 + r * rh
        d.rectangle(box([x0 - 2, y - mortar / 2, x1 + 2, y + mortar / 2]), fill=0)
    bw = (x1 - x0) / 3.0
    for r in range(rows):
        ya, yb = y0 + r * rh + (mortar / 2 if r else -4), y0 + (r + 1) * rh - (mortar / 2 if r < rows - 1 else -4)
        xs = [x0 + bw * (1 + j) for j in range(2)] if r % 2 == 0 else [x0 + bw * 0.5 + bw * j for j in range(3)]
        for x in xs:
            d.rectangle(box([x - mortar / 2, ya, x + mortar / 2, yb]), fill=0)


def pull(d):
    """a unit ring drawn down into the tower point"""
    d.ellipse(box([256 - 48 - 20, 82 - 48 - 20, 256 + 48 + 20, 82 + 48 + 20]), fill=255)
    d.ellipse(box([256 - 48 + 20, 82 - 48 + 20, 256 + 48 - 20, 82 + 48 - 20]), fill=0)
    d.polygon(P([(228, 160), (284, 160), (284, 290), (356, 290), (256, 388), (156, 290), (228, 290)]), fill=255)
    circ(d, 256, 446, 44)


def shove(d):
    d.rounded_rectangle(box([36, 168, 196, 344]), radius=22, fill=255)
    d.polygon(P([(66, 198), (166, 198), (166, 314), (66, 314)]), fill=0)
    d.polygon(P([(222, 220), (340, 220), (340, 150), (476, 256), (340, 362), (340, 292), (222, 292)]), fill=255)


def trigger(d):
    cx = cy = 256
    d.ellipse(box([cx - 166 - 25, cy - 166 - 25, cx + 166 + 25, cy + 166 + 25]), fill=255)
    d.ellipse(box([cx - 166 + 25, cy - 166 + 25, cx + 166 - 25, cy + 166 - 25]), fill=0)
    for b in ([232, 20, 280, 130], [232, 382, 280, 492], [20, 232, 130, 280], [382, 232, 492, 280]):
        d.rectangle(box(b), fill=255)
    circ(d, cx, cy, 46)


def strike(d):
    d.polygon(P([(318, 18), (118, 288), (238, 288), (190, 494), (404, 200), (282, 200)]), fill=255)


# ------------------------------------------------------------------ unit / identity glyphs (ported from the other clusters' picks, then tuned for the twin check)
def crest(d):
    """BREAKER crest: a cracked ring, the crack a zig knocked out of the ring, a core dot in the bore"""
    d.ellipse(box([40, 40, 472, 472]), fill=255)
    d.ellipse(box([132, 132, 380, 380]), fill=0)
    zig = [(306, 14), (240, 188), (310, 226), (214, 334), (266, 372), (196, 500)]
    thick(d, zig, 50, 0)
    circ(d, 256, 256, 30)


def packet(d):
    """parcel cube: hexagon with the three inner edges cut as a Y (cut 38 units)"""
    R, cx, cy = 222, 256, 262
    hx = [pol(cx, cy, R, a) for a in (-90, -30, 30, 90, 150, 210)]
    d.polygon(P(hx), fill=255)
    for a in (150, 30, 270):
        x, y = pol(cx, cy, R, a)
        d.line(P([(cx, cy), (x, y)]), fill=0, width=2 * 38)
    circ(d, cx, cy, 19, 0)


def worm(d):
    """hook: one bend, tapered tail, head bulge with an eye (never S, never M)"""
    pts = bez((296, 118), (306, 330), (262, 452), (100, 392), 60)
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        t = i / (n - 1)
        r = 70 - 52 * t ** 0.9 if t > 0.12 else 70
        circ(d, x, y, r)
    circ(d, 300, 112, 84)
    circ(d, 324, 94, 27, 0)


def payload(d):
    """bomb: body, cap, fuse, spark; the core eye is knocked out"""
    circ(d, 240, 300, 178)
    d.rectangle(box([186, 96, 294, 152]), fill=255)
    thick(d, [(262, 100), (318, 56), (384, 66)], 46)
    pts = []
    for i in range(16):
        r = 60 if i % 2 == 0 else 24
        pts.append(pol(416, 54, r, -90 + 22.5 * i))
    d.polygon(P(pts), fill=255)
    circ(d, 240, 300, 56, 0)


def jammer(d):
    """relay pylon with BROKEN broadcast arcs"""
    d.polygon(P([(256, 150), (352, 484), (160, 484)]), fill=255)
    d.polygon(P([(256, 232), (300, 354), (212, 354)]), fill=0)
    circ(d, 256, 140, 52)

    def arc(r, a0, a1, w=40):
        d.arc(box([256 - r, 140 - r, 256 + r, 140 + r]), a0, a1, fill=255, width=2 * w)
    arc(118, 196, 252)
    arc(206, 194, 220); arc(206, 232, 256)
    arc(118, -72, -52); arc(118, -36, -16)


def _stadium(w, h, cx, cy, ang, stroke):
    t = Image.new('L', (S2, S2), 0)
    ImageDraw.Draw(t).rounded_rectangle(box([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]), radius=int(h), outline=255, width=2 * stroke)
    return t.rotate(ang, center=(cx * 2, cy * 2), resample=Image.BICUBIC)


def ring_chain(m):
    """Ring unit: two interlocked chain links, over / under cut at the two crossings"""
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


DRAW = {
    'nudge': spin_fn(1), 'spin2': spin_fn(2), 'spin3': spin_fn(3), 'brace': brace, 'firewall': firewall, 'pull': pull, 'shove': shove,
    'twist': twist, 'hold': hold, 'trigger': trigger, 'strike': strike,
    'crest': crest, 'jammer': jammer, 'packet': packet, 'payload': payload, 'worm': worm,
}
RAW = {'ring': ring_chain}
IDS = ['nudge', 'spin2', 'spin3', 'brace', 'firewall', 'pull', 'shove', 'twist', 'hold', 'trigger', 'strike', 'crest', 'jammer', 'ring', 'packet', 'payload', 'worm']
CARD_ID = {'Nudge': 'nudge', 'Spin2': 'spin2', 'Spin3': 'spin3', 'Brace': 'brace', 'Firewall': 'firewall', 'Pull': 'pull', 'Shove': 'shove',
           'Twist': 'twist', 'Hold': 'hold', 'Trigger': 'trigger', 'Strike': 'strike'}
USES = {
    'nudge': 'card Nudge; spin_ghost / nudge_ghost family', 'spin2': 'card Spin 2', 'spin3': 'card Spin 3 (plan glyph, chain)',
    'brace': 'card Brace (white) ; board brace plate, arc brace glyph, chain, plan glyph (NET_CYAN)', 'firewall': 'card Firewall (brick wall only)',
    'pull': 'card Pull', 'shove': 'card Shove', 'twist': 'card Twist, twist badge, arc twist mark, chain', 'hold': 'card Hold, bezel HOLD cells, plan glyphs',
    'trigger': 'card Trigger, plan glyph', 'strike': 'card Strike', 'crest': 'hub emblem, nameplate, nowords sticker (Breaker)',
    'jammer': 'Jammer unit token, arc disc', 'ring': 'Ring unit token, arc disc', 'packet': 'Packet unit token, arc disc',
    'payload': 'Payload unit token, arc disc', 'worm': 'Worm unit token, arc disc, wear mark host',
}

_cache = {}
MIRROR = {'twist'}


def mask(gid):
    if gid in _cache:
        return _cache[gid]
    m = Image.new('L', (S2, S2), 0)
    if gid in RAW:
        RAW[gid](m)
    else:
        DRAW[gid](ImageDraw.Draw(m))
    out = m.resize((512, 512), Image.LANCZOS)
    if gid in MIRROR:
        out = out.transpose(Image.FLIP_LEFT_RIGHT)
    _cache[gid] = out
    return out


def name(gid):
    return 'KM_' + gid


def register():
    for g in IDS:
        _c15.CUSTOM['KM_' + g] = (lambda g=g: mask(g).copy())


register()


def card_glyph(card):
    return 'KM_' + CARD_ID[card]


def export(dirpath):
    os.makedirs(dirpath, exist_ok=True)
    for g in IDS:
        m = mask(g)
        im = Image.new('RGBA', m.size, (255, 255, 255, 0))
        im.putalpha(m)
        im.save(os.path.join(dirpath, g + '.png'))


def iou(a, b, px=28):
    """twin metric: silhouette IoU of two masks at px (each fitted to its bbox, centred)"""
    def prep(m):
        bb = m.point(lambda v: 255 if v > 100 else 0).getbbox()
        c = m.crop(bb)
        s = (px - 2) / max(c.size)
        c = c.resize((max(1, int(c.width * s)), max(1, int(c.height * s))), Image.LANCZOS)
        o = Image.new('L', (px, px), 0)
        o.paste(c, ((px - c.width) // 2, (px - c.height) // 2))
        return np.asarray(o) > 100
    A, B = prep(a), prep(b)
    return float((A & B).sum()) / max(1, float((A | B).sum()))
