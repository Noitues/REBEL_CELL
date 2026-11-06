"""R2 outer_rings: glyph stamping for the marks this cluster draws (HOLD hourglass, Twist, Brace clamp plate, unit-kind discs).
Ops are the bible 512-grid ops of the cards' card_icon_set A (hold / twist / brace copied verbatim from cards/src/kglyph.py);
the five unit-kind masters (cube, bomb, hook worm, relay pylon, chain links) are PROVISIONAL stand-ins drawn to the R1 ruling X8 until the
shared library lands; KIND_MASTER is the single swap point.  White silhouette, 7.5 percent ink, 2-3 parts."""
import sys, math
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFilter
from e10lib import INK

SS = 2


def _pol(cx, cy, r, a):
    t = math.radians(a)
    return (cx + r * math.cos(t), cy + r * math.sin(t))


OPS = {
    # hourglass (HOLD): two plates + two bowls
    'hold': [('P', [(92, 40), (420, 40), (420, 98), (92, 98)]), ('P', [(92, 414), (420, 414), (420, 472), (92, 472)]),
             ('P', [(118, 98), (394, 98), (278, 256), (234, 256)]), ('P', [(234, 256), (278, 256), (394, 414), (118, 414)])],
    # open circular arrow (Twist)
    'twist': [('R', 256, 256, 90, 44), ('A', 256, 256, 186, 150, 322, 58),
              ('P', [(_pol(256, 256, 186, 352)), _pol(256, 256, 186 + 66, 318), _pol(256, 256, 186 - 66, 318)])],
    # clamp plate (Brace): plate, two jaws, four rivets
    'brace': [('RR', [44, 56, 468, 456], 44), ('K', [(150, 104), (362, 104), (304, 408), (208, 408)]),
              ('P', [(190, 146), (322, 146), (282, 366), (230, 366)]),
              ('KC', 88, 104, 18), ('KC', 424, 104, 18), ('KC', 88, 408, 18), ('KC', 424, 408, 18)],
    # ---- provisional unit-kind masters
    'cube': [('P', [_pol(256, 262, 214, a) for a in (-90, -30, 30, 90, 150, 210)]),
             ('KL', [(256, 262), _pol(256, 262, 214, 90)], 30), ('KL', [(256, 262), _pol(256, 262, 214, -30)], 30), ('KL', [(256, 262), _pol(256, 262, 214, 210)], 30)],
    'bomb': [('C', 236, 300, 170), ('P', [(176, 160), (296, 160), (296, 96), (176, 96)]), ('L', [(296, 128), (372, 128), (410, 70)], 34), ('C', 420, 52, 34),
             ('KC', 180, 250, 26)],
    'worm': [('L', [(70, 440), (230, 440), (356, 330), (356, 214)], 92), ('C', 356, 158, 84), ('KC', 384, 142, 20)],
    'jammer': [('P', [(256, 170), (338, 456), (174, 456)]), ('K', [(256, 258), (292, 408), (220, 408)]), ('C', 256, 120, 40),
               ('A', 256, 120, 96, 195, 250, 34), ('A', 256, 120, 96, 290, 345, 34), ('A', 256, 120, 168, 190, 240, 30), ('A', 256, 120, 168, 300, 350, 30)],
    'chain': [('RRO', [40, 176, 300, 336], 80, 52), ('RRO', [212, 176, 472, 336], 80, 52)],
}
KIND_MASTER = {'Packet': 'cube', 'Payload': 'bomb', 'Worm': 'worm', 'Jammer': 'jammer', 'Ring': 'chain'}
_cache = {}


def _draw(ops):
    S = 512 * SS
    k = SS
    m = Image.new('L', (S, S), 0)
    d = ImageDraw.Draw(m)
    for op in ops:
        t = op[0]
        if t == 'P':
            d.polygon([(x * k, y * k) for x, y in op[1]], fill=255)
        elif t == 'K':
            d.polygon([(x * k, y * k) for x, y in op[1]], fill=0)
        elif t == 'KL':
            pts = [(x * k, y * k) for x, y in op[1]]
            d.line(pts, fill=0, width=int(op[2] * k), joint='curve')
        elif t == 'RR':
            d.rounded_rectangle([v * k for v in op[1]], radius=op[2] * k, fill=255)
        elif t == 'RRO':
            d.rounded_rectangle([v * k for v in op[1]], radius=op[2] * k, outline=255, width=int(op[3] * k))
        elif t == 'C':
            _, cx, cy, r = op
            d.ellipse([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], fill=255)
        elif t == 'KC':
            _, cx, cy, r = op
            d.ellipse([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], fill=0)
        elif t == 'R':
            _, cx, cy, r, w = op
            d.ellipse([(cx - r - w / 2) * k, (cy - r - w / 2) * k, (cx + r + w / 2) * k, (cy + r + w / 2) * k], outline=255, width=int(w * k))
        elif t == 'A':
            _, cx, cy, r, a0, a1, w = op
            d.arc([(cx - r - w / 2) * k, (cy - r - w / 2) * k, (cx + r + w / 2) * k, (cy + r + w / 2) * k], a0, a1, fill=255, width=int(w * k))
        elif t == 'L':
            pts = [(x * k, y * k) for x, y in op[1]]
            d.line(pts, fill=255, width=int(op[2] * k), joint='curve')
            for p in (pts[0], pts[-1]):
                rr = op[2] * k / 2
                d.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=255)
    return m.resize((512, 512), Image.LANCZOS)


MAP = {'hold': 'hold', 'twist': 'twist', 'brace': 'brace', 'cube': 'packet', 'bomb': 'payload', 'worm': 'worm', 'jammer': 'jammer', 'chain': 'ring'}


def mask(name):
    import asm_glyphs   # ASSEMBLY (Y3): the one master library
    return asm_glyphs.mask(MAP[name])


def stamp_img(name, px, k, col=(255, 255, 255), ink=0.075):
    """RGBA of the silhouette + ink outline at px*k pixels (padded)."""
    key = (name, px, k, tuple(col), ink)
    if key in _cache:
        return _cache[key]
    s = int(round(px * k))
    iw = max(1.5, s * ink)
    pad = int(iw) + 3
    m = mask(name).resize((s, s), Image.LANCZOS)
    big = Image.new('L', (s + 2 * pad, s + 2 * pad), 0)
    big.paste(m, (pad, pad))
    dil = big.filter(ImageFilter.GaussianBlur(iw * 0.55)).point(lambda v: 255 if v > 38 else int(v * 255 / 38))
    out = Image.new('RGBA', big.size, (0, 0, 0, 0))
    out.paste(tuple(INK) + (255,), mask=dil)
    out.paste(tuple(col) + (255,), mask=big)
    _cache[key] = out
    return out


def stamp(L, name, px, xy, col=(255, 255, 255), ink=0.075):
    im = stamp_img(name, px, L.k, col, ink)
    L.im.alpha_composite(im, (int(round(xy[0] * L.k - im.width / 2)), int(round(xy[1] * L.k - im.height / 2))))


def kind_glyph(L, kind, px, xy, col=(255, 255, 255)):
    stamp(L, KIND_MASTER[kind], px, xy, col)
