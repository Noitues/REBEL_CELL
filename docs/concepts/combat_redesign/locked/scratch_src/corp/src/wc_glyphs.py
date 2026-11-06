"""wheel_core design glyphs (512 grid masks, registered in crests15.CUSTOM so slicelib.glyph_rgba draws the white + ink keyline)."""
import sys, math
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw
import crests15

S = 512


def _new():
    m = Image.new('L', (S, S), 0)
    return m, ImageDraw.Draw(m)


def _rot(m, ang, c=(256, 256)):
    return m.rotate(ang, resample=Image.BICUBIC, center=c)


def _bullet(d, cx, top, w, h):
    r = w / 2
    d.rectangle([cx - r, top + r * 1.3, cx + r, top + h], fill=255)
    d.pieslice([cx - r, top, cx + r, top + 2 * r * 1.3], 180, 360, fill=255)
    d.polygon([(cx - r, top + r * 1.3), (cx, top), (cx + r, top + r * 1.3)], fill=255)


# ------------------------------------------------------------------ BURST (two-shot) / TURRET (one-shot): A bullets, B pistol + rounds, C barrels
def burst_a():
    m, d = _new()
    _bullet(d, 170, 50, 110, 300); _bullet(d, 342, 50, 110, 300)
    for x in (170, 342):                      # base band + motion streaks
        d.rectangle([x - 55, 360, x + 55, 392], fill=255)
        d.rectangle([x - 40, 420, x - 22, 470], fill=255); d.rectangle([x + 22, 420, x + 40, 470], fill=255)
    return m


def turret_a():
    m, d = _new()
    _bullet(d, 256, 40, 150, 330)
    d.rectangle([181, 380, 331, 416], fill=255)
    d.rectangle([226, 440, 246, 490], fill=255); d.rectangle([266, 440, 286, 490], fill=255)
    return m


def _pistol():
    m, d = _new()
    d.rounded_rectangle([90, 170, 430, 262], radius=18, fill=255)         # slide
    d.polygon([(110, 250), (230, 250), (200, 430), (110, 430)], fill=255)  # grip
    d.rectangle([232, 262, 300, 292], fill=255)                              # trigger guard bar
    d.pieslice([225, 250, 335, 340], 0, 180, fill=255); d.pieslice([248, 262, 312, 322], 0, 180, fill=0)
    d.rectangle([410, 150, 430, 175], fill=255)
    return m


def burst_b():
    g = _rot(_pistol(), 90).resize((380, 380)); m, d = _new(); m.paste(g, (66, 120))
    d = ImageDraw.Draw(m)
    for x in (206, 306):
        d.ellipse([x - 26, 30, x + 26, 82], fill=255)
    return m


def turret_b():
    g = _rot(_pistol(), 90).resize((380, 380)); m, d = _new(); m.paste(g, (66, 120))
    d = ImageDraw.Draw(m)
    d.ellipse([256 - 30, 26, 256 + 30, 86], fill=255)
    return m


def burst_c():
    m, d = _new()
    d.rounded_rectangle([46, 140, 466, 372], radius=96, fill=255)
    for x in (160, 352):
        d.ellipse([x - 70, 186, x + 70, 326], fill=0)
        d.ellipse([x - 28, 228, x + 28, 284], fill=255)
    d.rectangle([236, 100, 276, 150], fill=255)
    return m


def turret_c():
    m, d = _new()
    d.rounded_rectangle([120, 130, 392, 382], radius=96, fill=255)
    d.ellipse([186, 196, 326, 316], fill=0)
    d.ellipse([228, 238, 284, 294], fill=255)
    d.rectangle([236, 84, 276, 136], fill=255)
    return m


# ------------------------------------------------------------------ SHIELD
def shield_a():          # heater, solid, two pips
    m, d = _new()
    pts = [(96, 70), (416, 70), (416, 250)]
    for i in range(1, 13):
        t = i / 12
        pts.append((416 - 160 * (1 - math.cos(t * math.pi / 2)) - 0 * t, 250 + 200 * math.sin(t * math.pi / 2)))
    pts += [(256, 452)]
    left = [(512 - x, y) for (x, y) in reversed(pts[3:15])]
    poly = [(96, 70), (416, 70), (416, 240)] + [(416 - 160 * (1 - math.cos(t * math.pi / 2)), 240 + 212 * math.sin(t * math.pi / 2)) for t in [i / 14 for i in range(1, 15)]]
    poly += [(512 - x, y) for (x, y) in reversed(poly[3:])] + [(96, 240)]
    d.polygon(poly, fill=255)
    for x in (196, 316):
        d.ellipse([x - 30, 150, x + 30, 210], fill=0)
    return m


def shield_b():          # round buckler with boss
    m, d = _new()
    d.ellipse([50, 50, 462, 462], fill=255)
    d.ellipse([112, 112, 400, 400], fill=0)
    d.ellipse([172, 172, 340, 340], fill=255)
    return m


def shield_c():          # tall tower shield, notched top, two bars
    m, d = _new()
    d.polygon([(110, 40), (230, 40), (256, 76), (282, 40), (402, 40), (402, 330), (256, 472), (110, 330)], fill=255)
    for y in (170, 270):
        d.rectangle([156, y, 356, y + 40], fill=0)
    return m


# ------------------------------------------------------------------ REPAIR
def _cap(ang, w=120, l=470):
    m, d = _new()
    d.rounded_rectangle([256 - l / 2, 256 - w / 2, 256 + l / 2, 256 + w / 2], radius=w / 2, fill=255)
    return _rot(m, ang)


def repair_a():          # crossed bandages, pad ring + square
    m = Image.new('L', (S, S), 0)
    for a in (45, -45):
        c = _cap(a)
        m = Image.composite(Image.new('L', (S, S), 255), m, c)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([166, 166, 346, 346], radius=24, fill=0)
    d.rounded_rectangle([196, 196, 316, 316], radius=14, fill=255)
    return m


def repair_b():          # crossed bandages, plus knocked out
    m = Image.new('L', (S, S), 0)
    for a in (45, -45):
        m = Image.composite(Image.new('L', (S, S), 255), m, _cap(a, 130))
    d = ImageDraw.Draw(m)
    d.rectangle([226, 176, 286, 336], fill=0); d.rectangle([176, 226, 336, 286], fill=0)
    return m


def repair_c():          # one wide diagonal strip, pad + perforations
    m, d = _new()
    d.rounded_rectangle([20, 156, 492, 356], radius=100, fill=255)
    m = _rot(m, 40)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([166, 196, 346, 316], radius=18, fill=0)
    d.rounded_rectangle([190, 214, 322, 298], radius=10, fill=255)
    return m


# ------------------------------------------------------------------ BREAKER class emblems
def emb_a():             # cracked ring
    m, d = _new()
    d.ellipse([46, 46, 466, 466], fill=255)
    d.ellipse([126, 126, 386, 386], fill=0)
    zig = [(300, 20), (236, 190), (306, 230), (216, 330), (262, 372), (190, 500)]
    d.line(zig, fill=0, width=46, joint='curve')
    d.ellipse([226, 226, 286, 286], fill=255)
    return m


def emb_b():             # crowbar
    m, d = _new()
    d.line([(300, 110), (230, 250), (210, 420)], fill=255, width=70, joint="curve")
    d.polygon([(300, 110), (390, 60), (450, 140), (350, 180)], fill=255)
    d.polygon([(160, 420), (260, 420), (250, 480), (170, 480)], fill=255)
    return m


def emb_c():             # wedge splitting a bar
    m, d = _new()
    d.rectangle([40, 120, 220, 200], fill=255); d.rectangle([292, 120, 472, 200], fill=255)
    d.polygon([(200, 120), (312, 120), (256, 440)], fill=255)
    d.rectangle([40, 250, 160, 300], fill=255); d.rectangle([352, 250, 472, 300], fill=255)
    return m


for n, f in dict(WC_BURST_A=burst_a, WC_TURRET_A=turret_a, WC_BURST_B=burst_b, WC_TURRET_B=turret_b, WC_BURST_C=burst_c, WC_TURRET_C=turret_c,
                 WC_SHIELD_A=shield_a, WC_SHIELD_B=shield_b, WC_SHIELD_C=shield_c, WC_REPAIR_A=repair_a, WC_REPAIR_B=repair_b, WC_REPAIR_C=repair_c,
                 WC_EMB_A=emb_a, WC_EMB_B=emb_b, WC_EMB_C=emb_c).items():
    crests15.CUSTOM[n] = f
