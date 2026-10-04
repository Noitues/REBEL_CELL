"""Round 14 glyph set (512 box, white = filled, black = cut-out) after the designer's round 13 review.

Unchanged shapes come from glyphs13 (kept verbatim as the reference for the old -> new sheet).
Options are named "NAME@A", "NAME@B" ...; CHOICE maps the plain name to the chosen option.
SMALL maps a glyph to its reduced form, used at 24 px and below (CLEANSE's CTRL-ALT-DEL).
ONE shared flame: flame2() (two peaks) is used by every fire glyph (BURN, BURNING, FIREWALL).
"""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageChops

import glyphs13 as G13
from glyphs13 import _new, _rot, _flame_pts, _arrow_arc, _asterisk

S = 512
BYPASS = set()


def _text_mask(txt, box, px=None, var=b"Bold Condensed"):
    """White text fitted into box (x0, y0, x1, y1)."""
    import slicelib as SL
    m, d = _new()
    x0, y0, x1, y1 = box
    px = px or int((y1 - y0) * 1.25)
    while px > 8:
        f = SL.font("bahnschrift.ttf", px, var)
        bb = f.getbbox(txt)
        if bb[2] - bb[0] <= (x1 - x0) and bb[3] - bb[1] <= (y1 - y0):
            break
        px -= 4
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d.text((cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2), txt, font=f, fill=255)
    return m


def _paste(m, src, val=255):
    m.paste(val, (0, 0), src)


# ============================================================ the ONE flame (two peaks)
def flame2_polys(cx, base, w, h):
    """Main tongue leaning right + a shorter tongue to its left: one shape, two peaks."""
    main = _flame_pts(cx + 0.18 * w, base, w * 0.92, h, 0.10)
    side = _flame_pts(cx - 0.42 * w, base - 0.05 * h, w * 0.58, h * 0.66, -0.22)
    return [main, side]


def draw_flame2(d, cx, base, w, h, fill=255):
    for p in flame2_polys(cx, base, w, h):
        d.polygon(p, fill=fill)
    d.ellipse([cx - w * 0.95, base - 1.15 * w, cx + w * 1.05, base], fill=fill)


def flame2():
    m, d = _new()
    draw_flame2(d, 262, 490, 170, 470)
    draw_flame2(d, 262, 448, 66, 210, 0)  # inner cut-out: the same shape, small
    return m


def firewall():  # brick wall + the shared flame
    m, d = _new()
    d.rectangle([40, 270, 472, 482], fill=255)
    draw_flame2(d, 256, 300, 120, 290)
    d.line([(30, 274), (482, 274)], fill=0, width=14)
    for y in (340, 412):
        d.line([(30, y), (482, y)], fill=0, width=20)
    for y0, y1, xs in ((274, 340, (160, 352)), (340, 412, (256,)), (412, 482, (160, 352))):
        for x in xs:
            d.line([(x, y0), (x, y1)], fill=0, width=20)
    return m


# ============================================================ 1. WEIGHT (was INERTIA)
def weight_a():  # anvil (round 13)
    return G13.inertia()


def weight_b():  # cartoon "1 t" weight: trapezoid with a small flat ring
    m, d = _new()
    d.polygon([(150, 190), (362, 190), (470, 486), (42, 486)], fill=255)
    d.rounded_rectangle([196, 60, 316, 200], radius=44, outline=255, width=42)
    t = _text_mask("1t", (170, 280, 342, 440))
    _paste(m, t, 0)
    return m


def weight_c():  # dumbbell
    m, d = _new()
    d.rectangle([110, 226, 402, 286], fill=255)
    for x0 in (36, 382):
        d.rounded_rectangle([x0, 110, x0 + 94, 402], radius=24, fill=255)
    for x0 in (136, 316):
        d.rounded_rectangle([x0, 160, x0 + 60, 352], radius=18, fill=255)
    d.line([(130, 110), (130, 402)], fill=0, width=12)
    d.line([(382, 110), (382, 402)], fill=0, width=12)
    return m


# ============================================================ 2. SANDBOX: a kid's sandbox with a shovel
def _shovel(d, top, bottom, w=34, fill=255, blade=True):
    (x0, y0), (x1, y1) = top, bottom
    d.line([top, bottom], fill=fill, width=w)
    ang = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(ang), math.cos(ang)
    g = 50
    d.line([(x0 + nx * g, y0 + ny * g), (x0 - nx * g, y0 - ny * g)], fill=fill, width=w)  # T grip
    if blade:
        bx, by = x1, y1
        tx, ty = math.cos(ang), math.sin(ang)
        bw, bl = 62, 110
        d.polygon([(bx + nx * bw, by + ny * bw), (bx - nx * bw, by - ny * bw),
                   (bx - nx * bw * 0.8 + tx * bl * 0.7, by - ny * bw * 0.8 + ty * bl * 0.7), (bx + tx * bl, by + ty * bl),
                   (bx + nx * bw * 0.8 + tx * bl * 0.7, by + ny * bw * 0.8 + ty * bl * 0.7)], fill=fill)


def sandbox_a():  # front view: plank box, sand mound, shovel stuck in it
    m, d = _new()
    d.polygon([(30, 300), (482, 300), (452, 486), (60, 486)], fill=255)
    d.pieslice([70, 190, 442, 420], 180, 360, fill=255)
    d.line([(40, 300), (472, 300)], fill=0, width=18)  # box rim
    d.line([(52, 392), (460, 392)], fill=0, width=14)  # plank seam
    for (x, y) in ((170, 262), (236, 236), (330, 262)):
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=0)  # grains
    L = Image.new("L", (S, S), 0)
    _shovel(ImageDraw.Draw(L), (410, 40), (300, 250), 38, blade=False)
    _paste(m, L.filter(ImageFilter.MaxFilter(25)), 0)
    _paste(m, L)
    return m


def sandbox_b():  # top view: square frame, sand inside, shovel across and out of the corner
    m, d = _new()
    d.rounded_rectangle([40, 120, 432, 482], radius=26, fill=255)
    d.rounded_rectangle([100, 180, 372, 422], radius=12, fill=0)
    d.rounded_rectangle([126, 206, 346, 396], radius=40, fill=255)
    for (x, y) in ((170, 250), (300, 260), (210, 340), (300, 350)):
        d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=0)
    L = Image.new("L", (S, S), 0)
    _shovel(ImageDraw.Draw(L), (460, 40), (250, 300), 36)
    _paste(m, L.filter(ImageFilter.MaxFilter(25)), 0)
    _paste(m, L)
    return m


def sandbox_c():  # front view box with a bucket and the shovel
    m, d = _new()
    d.polygon([(30, 320), (482, 320), (452, 486), (60, 486)], fill=255)
    d.pieslice([110, 230, 470, 410], 180, 360, fill=255)
    d.line([(40, 320), (472, 320)], fill=0, width=18)
    d.polygon([(52, 140), (212, 140), (192, 300), (72, 300)], fill=255)  # bucket
    d.arc([60, 50, 204, 230], 200, 340, fill=255, width=22)
    d.line([(52, 150), (212, 150)], fill=0, width=14)
    L = Image.new("L", (S, S), 0)
    _shovel(ImageDraw.Draw(L), (430, 40), (330, 270), 36, blade=False)
    _paste(m, L.filter(ImageFilter.MaxFilter(25)), 0)
    _paste(m, L)
    return m


# ============================================================ 3. PATCH: two crossed band-aids, constant width
def _bandaid(angle):
    L = Image.new("L", (S, S), 0)
    dl = ImageDraw.Draw(L)
    dl.rounded_rectangle([24, 200, 488, 312], radius=56, fill=255)
    dl.rounded_rectangle([196, 218, 316, 294], radius=10, outline=0, width=12)  # pad, same width as the strip
    for x in (84, 124, 388, 428):
        dl.ellipse([x - 9, 247, x + 9, 265], fill=0)
    return L.rotate(angle, resample=Image.BICUBIC)


def patch():
    m, d = _new()
    A, B = _bandaid(45), _bandaid(-45)
    _paste(m, A)
    _paste(m, B.filter(ImageFilter.MaxFilter(27)), 0)
    _paste(m, B)
    return m


# ============================================================ 4. SHIELD placeholder: 3 options
_HEATER = [(66, 40), (446, 40), (446, 220), (412, 340), (256, 488), (100, 340), (66, 220)]


def shield_a():  # heraldic per pale: left half solid, right half an outline
    m, d = _new()
    d.polygon(_HEATER, fill=255)
    inner = [(x * 0.80 + 256 * 0.20, y * 0.80 + 256 * 0.20 + 4) for x, y in _HEATER]
    I = Image.new("L", (S, S), 0)
    ImageDraw.Draw(I).polygon(inner, fill=255)
    R = Image.new("L", (S, S), 0)
    ImageDraw.Draw(R).rectangle([270, 0, 512, 512], fill=255)
    _paste(m, ImageChops.multiply(I, R), 0)
    d.rectangle([242, 60, 270, 440], fill=255)
    return m


def shield_b():  # riot shield: tall rounded slab with a view slot and a rim
    m, d = _new()
    d.rounded_rectangle([96, 20, 416, 492], radius=110, fill=255)
    d.rounded_rectangle([150, 92, 362, 160], radius=24, fill=0)
    d.rounded_rectangle([140, 200, 372, 440], radius=70, outline=0, width=20)
    return m


def shield_c():  # double wall: shield outline + inner solid shield
    m, d = _new()
    d.polygon(_HEATER, fill=255)
    for k, f in ((0.82, 0), (0.62, 255)):
        p = [(x * k + 256 * (1 - k), y * k + 256 * (1 - k) - (1 - k) * 30) for x, y in _HEATER]
        d.polygon(p, fill=f)
    return m


# ============================================================ 5. RECON: binoculars
def recon():
    m, d = _new()
    for x0 in (36, 286):
        d.rounded_rectangle([x0 + 30, 70, x0 + 160, 220], radius=30, fill=255)  # eye tubes
        d.ellipse([x0, 190, x0 + 190, 480], fill=255)  # objective barrels
        d.ellipse([x0 + 40, 300, x0 + 150, 430], fill=0)
        d.ellipse([x0 + 70, 330, x0 + 120, 380], fill=255)
    d.rounded_rectangle([196, 150, 316, 260], radius=20, fill=255)  # bridge
    d.ellipse([230, 170, 282, 222], fill=0)
    return m


# ============================================================ 6. NULL options
def null_a():
    return G13.null()


def null_b():
    return _text_mask("÷0", (20, 60, 492, 452))


def null_c():
    return _text_mask("1/0", (20, 60, 492, 452))


def null_d():
    return _text_mask("x/0", (20, 60, 492, 452))


# ============================================================ 7 + 8. JUDGEMENT (gavel) / CITATION (receipt)
# ============================================================ 9. SPOOF: a whole fingerprint
def fingerprint():
    m, d = _new()
    d.ellipse([76, 16, 436, 496], fill=255)
    cx, cy = 256, 236
    for k, r in enumerate(range(40, 260, 42)):
        ry = r * 1.18
        d.ellipse([cx - r, cy - ry + k * 6, cx + r, cy + ry + k * 6], outline=0, width=17)
    d.ellipse([cx - 16, cy - 30, cx + 16, cy + 30], fill=0)
    d.line([(150, 420), (300, 300), (330, 180)], fill=255, width=20, joint="curve")  # ridge breaks
    d.line([(370, 330), (420, 380)], fill=255, width=20)
    return m


# ============================================================ 10. CLEANSE: CTRL-ALT-DEL ; ALT-F4
def _keycap(m, box, txt, txt2=None):
    d = ImageDraw.Draw(m)
    x0, y0, x1, y1 = box
    w = x1 - x0
    r = max(10, int(w * 0.16))
    ins = w * 0.07
    K = Image.new("L", (S, S), 0)
    ImageDraw.Draw(K).polygon([(x0 + ins, y0), (x1 - ins, y0), (x1, y1), (x0, y1)], fill=255)
    K = K.filter(ImageFilter.GaussianBlur(max(4, w * 0.035))).point(lambda v: 255 if v > 128 else 0)
    _paste(m, K)
    g = max(6, int(w * 0.055))
    face = (x0 + g * 2, y0 + g * 1.4, x1 - g * 2, y1 - g * 3.2)
    d.rounded_rectangle(face, radius=max(6, r - g), outline=0, width=g)
    fx0, fy0, fx1, fy1 = face
    pad = g * 1.8
    if txt2:
        hh = (fy1 - fy0 - 2 * pad)
        _paste(m, _text_mask(txt2, (fx0 + pad, fy0 + pad, fx1 - pad, fy0 + pad + hh * 0.36)), 0)
        _paste(m, _text_mask(txt, (fx0 + pad, fy0 + pad + hh * 0.44, fx1 - pad, fy1 - pad)), 0)
    else:
        _paste(m, _text_mask(txt, (fx0 + pad, fy0 + pad, fx1 - pad, fy1 - pad)), 0)


def cleanse_a():  # three keycaps in a row
    m, d = _new()
    for i, t in enumerate(("CTRL", "ALT", "DEL")):
        x0 = 8 + i * 170
        _keycap(m, (x0, 150, x0 + 156, 362), t)
    return m


def cleanse_small():  # the reduced form: a single DEL keycap
    m, d = _new()
    _keycap(m, (40, 60, 472, 452), "DEL")
    return m


def cleanse_b():  # stacked keycaps, DEL in front (same shape at every size)
    m, d = _new()
    for i, t in enumerate(("CTRL", "ALT")):
        o = i * 70
        _keycap(m, (20 + o, 20 + o, 320 + o, 290 + o), t)
        d.rounded_rectangle([20 + o + 70 - 22, 20 + o + 70 - 22, 320 + o + 70 + 22, 290 + o + 70 + 22], radius=60, fill=0)
    _keycap(m, (160, 160, 492, 470), "DEL")
    return m


def alt_f4():  # placeholder "kill process": ALT + F4, two keys side by side (wide, unlike CLEANSE's one key)
    m, d = _new()
    _keycap(m, (6, 150, 236, 380), "ALT")
    _keycap(m, (276, 150, 506, 380), "F4")
    return m


def receipt():  # the old tariff receipt, now CITATION: tilted, deep tear teeth top and bottom
    L, d = _new()
    pts = []
    for i in range(9):
        x = 130 + i * 31.5
        pts.append((x, 30 if i % 2 == 0 else 80))
    for i in range(9):
        x = 382 - i * 31.5
        pts.append((x, 482 if i % 2 == 0 else 432))
    d.polygon(pts, fill=255)
    for y in (130, 190, 250):
        d.rectangle([170, y, 342, y + 24], fill=0)
    d.ellipse([206, 300, 306, 400], fill=0)
    d.ellipse([226, 320, 286, 380], fill=255)
    d.rectangle([248, 308, 264, 392], fill=0)
    return L.rotate(-14, resample=Image.BICUBIC)


def storm():  # cloud on top, the bolt dropping out of it
    m, d = _new()
    for (x, y, r) in ((150, 170, 96), (270, 120, 120), (380, 186, 86)):
        d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    d.rounded_rectangle([56, 170, 466, 272], radius=50, fill=255)
    bolt = [(270, 250), (170, 400), (246, 400), (200, 510), (352, 350), (276, 350), (330, 250)]
    B = Image.new("L", (S, S), 0)
    ImageDraw.Draw(B).polygon(bolt, fill=255)
    _paste(m, B.filter(ImageFilter.MaxFilter(25)), 0)
    _paste(m, B)
    return m


def ring_lock():  # inner ring with a big padlock hanging off its lower right
    m, d = _new()
    d.ellipse([20, 20, 340, 340], outline=255, width=56)
    P = Image.new("L", (S, S), 0)
    dp = ImageDraw.Draw(P)
    dp.rounded_rectangle([250, 300, 496, 490], radius=26, fill=255)
    dp.arc([290, 190, 456, 380], 180, 360, fill=255, width=40)
    dp.rectangle([290, 280, 330, 310], fill=255)
    dp.rectangle([416, 280, 456, 310], fill=255)
    _paste(m, P.filter(ImageFilter.MaxFilter(27)), 0)
    _paste(m, P)
    d.ellipse([350, 360, 396, 406], fill=0)
    d.rectangle([362, 390, 384, 450], fill=0)
    return m


# ============================================================ 11. EMPOWERED: 3 options
def empowered_a():  # three stacked bold up chevrons
    m, d = _new()
    for k in range(3):
        y = 60 + k * 140
        d.polygon([(256, y), (476, y + 170), (476, y + 260), (256, y + 90), (36, y + 260), (36, y + 170)], fill=255)
    return m


def empowered_b():  # up arrow breaking through a bar
    m, d = _new()
    d.polygon([(20, 330), (200, 330), (180, 400), (20, 400)], fill=255)  # broken bar, left
    d.polygon([(312, 330), (492, 330), (492, 400), (334, 400)], fill=255)
    d.polygon([(186, 296), (222, 280), (214, 316)], fill=255)  # shards
    d.polygon([(300, 286), (336, 296), (312, 316)], fill=255)
    A = Image.new("L", (S, S), 0)
    ImageDraw.Draw(A).polygon([(256, 14), (440, 214), (330, 214), (330, 496), (182, 496), (182, 214), (72, 214)], fill=255)
    _paste(m, A.filter(ImageFilter.MaxFilter(29)), 0)
    _paste(m, A)
    return m


def empowered_c():  # power-up star with an up arrow cut through it
    m, d = _new()
    pts = []
    for i in range(10):
        r = 250 if i % 2 == 0 else 112
        a = math.radians(-90 + i * 36)
        pts.append((256 + r * math.cos(a), 276 + r * math.sin(a)))
    d.polygon(pts, fill=255)
    d.polygon([(256, 150), (346, 250), (296, 250), (296, 370), (216, 370), (216, 250), (166, 250)], fill=0)
    return m


# ============================================================ 12. MOMENTUM (spin 2, or 5 if you already spun)
def momentum_a():  # spin arc with a chain link in the middle
    m = G13.spin_cw()
    d = ImageDraw.Draw(m)
    L = Image.new("L", (S, S), 0)
    dl = ImageDraw.Draw(L)
    dl.rounded_rectangle([150, 222, 290, 310], radius=44, outline=255, width=26)
    dl.rounded_rectangle([222, 222, 362, 310], radius=44, outline=255, width=26)
    L = L.rotate(-30, resample=Image.BICUBIC, center=(256, 266))
    _paste(m, L)
    return m


def momentum_b():  # two concentric spin arrows: small then big (it escalates)
    m, d = _new()
    _arrow_arc(d, (256, 268), 214, 58, 150, 380, 1.3)
    _arrow_arc(d, (256, 268), 104, 46, 150, 380, 1.3)
    return m


def momentum_c():  # spin arc with two rising steps inside
    m = G13.spin_cw()
    d = ImageDraw.Draw(m)
    d.rectangle([186, 286, 240, 350], fill=255)
    d.rectangle([262, 214, 316, 350], fill=255)
    return m


# ============================================================ 13. NUDGE INNER: bullseye, middle ring highlighted, +-1 arrows
def nudge_inner():
    m, d = _new()
    c = (256, 276)
    d.ellipse([c[0] - 232, c[1] - 232, c[0] + 232, c[1] + 232], outline=255, width=22)  # outer ring, thin
    d.ellipse([c[0] - 52, c[1] - 52, c[0] + 52, c[1] + 52], fill=255)  # bullseye
    # the inner (middle) ring is the highlighted one: thick, and itself a two-headed arrow (+-1)
    _two_head_arc(d, c, 160, 56, -46, 226, 1.0)
    return m


# ============================================================ 14. NUDGE: short two-headed arc, +-1
def _two_head_arc(d, c, r, w, a0, a1, head=1.3):
    mid = (a0 + a1) / 2
    _arrow_arc(d, c, r, w, mid, a1, head)
    _arrow_arc(d, c, r, w, mid, a0, head)


def nudge_a():  # short arc with heads both ends + one tick below
    m, d = _new()
    _two_head_arc(d, (256, 470), 300, 56, 238, 302)
    d.rounded_rectangle([230, 250, 282, 420], radius=14, fill=255)
    return m


def nudge_b():  # short arc + "+-1" under it
    m, d = _new()
    _two_head_arc(d, (256, 470), 300, 56, 238, 302)
    _paste(m, _text_mask("±1", (120, 250, 392, 480)))
    return m


def nudge_c():  # short arc over a rim ruler with three ticks
    m, d = _new()
    _two_head_arc(d, (256, 520), 330, 54, 240, 300)
    d.arc([16, 330, 496, 810], 236, 304, fill=255, width=40)
    for ang, L in ((256, 50), (270, 100), (284, 50)):
        a = math.radians(ang)
        d.line([(256 + 240 * math.cos(a), 570 + 240 * math.sin(a)), (256 + (240 + L) * math.cos(a), 570 + (240 + L) * math.sin(a))], fill=255, width=30)
    return m


# ============================================================ 15. UNDOCK
def undock_a():  # drone + outward arrow
    m, d = _new()
    import slicelib as SL
    D = SL.glyph_mask_extra("DRONE").resize((300, 300), Image.LANCZOS)
    m.paste(D, (10, 202))
    d.line([(300, 212), (420, 92)], fill=255, width=56)
    d.polygon([(470, 42), (470, 210), (302, 42)], fill=255)
    return m


def undock_b():  # open ball-and-socket: the socket, and the ball leaving it
    m, d = _new()
    d.arc([20, 120, 292, 392], 50, 310, fill=255, width=64)
    d.rectangle([20, 230, 70, 282], fill=255)
    d.ellipse([290, 156, 490, 356], fill=255)
    for y in (196, 316):
        d.line([(200, y), (260, y)], fill=255, width=22)  # motion lines
    return m


# ============================================================ 16. BREACH: bolt over a bullseye
def breach():
    m, d = _new()
    c = (256, 256)
    d.ellipse([20, 20, 492, 492], outline=255, width=44)
    d.ellipse([110, 110, 402, 402], outline=255, width=44)
    d.ellipse([206, 206, 306, 306], fill=255)
    bolt = [(300, 0), (130, 290), (250, 290), (196, 512), (392, 210), (272, 210), (350, 0)]
    B = Image.new("L", (S, S), 0)
    ImageDraw.Draw(B).polygon(bolt, fill=255)
    _paste(m, B.filter(ImageFilter.MaxFilter(31)), 0)
    _paste(m, B)
    return m


# ============================================================ 17. EXHAUST: a card tearing in two
def exhaust():
    m, d = _new()
    card = Image.new("L", (S, S), 0)
    ImageDraw.Draw(card).rounded_rectangle([96, 40, 416, 480], radius=34, fill=255)
    zig = [(256, 0), (276, 70), (240, 140), (278, 220), (238, 300), (276, 380), (246, 450), (260, 512)]
    for side, ang, dx in ((0, 7, -28), (1, -7, 28)):
        clip = Image.new("L", (S, S), 0)
        pts = ([(0, 0)] + zig + [(0, 512)]) if side == 0 else ([(512, 0)] + zig + [(512, 512)])
        ImageDraw.Draw(clip).polygon(pts, fill=255)
        half = ImageChops.multiply(card, clip).filter(ImageFilter.MinFilter(9))
        half = half.rotate(ang, resample=Image.BICUBIC, center=(256, 470), translate=(dx, 0))
        _paste(m, half)
    return m


# ============================================================ registry
OPTIONS = {
    "WEIGHT@A": weight_a, "WEIGHT@B": weight_b, "WEIGHT@C": weight_c,
    "SANDBOX@A": sandbox_a, "SANDBOX@B": sandbox_b, "SANDBOX@C": sandbox_c,
    "SHIELD@A": shield_a, "SHIELD@B": shield_b, "SHIELD@C": shield_c,
    "NULL@A": null_a, "NULL@B": null_b, "NULL@C": null_c, "NULL@D": null_d,
    "ST_CLEANSE@A": cleanse_a, "ST_CLEANSE@B": cleanse_b,
    "ST_EMPOWERED@A": empowered_a, "ST_EMPOWERED@B": empowered_b, "ST_EMPOWERED@C": empowered_c,
    "PI_MOMENTUM@A": momentum_a, "PI_MOMENTUM@B": momentum_b, "PI_MOMENTUM@C": momentum_c,
    "PI_NUDGE@A": nudge_a, "PI_NUDGE@B": nudge_b, "PI_NUDGE@C": nudge_c,
    "PI_UNDOCK@A": undock_a, "PI_UNDOCK@B": undock_b,
}
CHOICE = {"WEIGHT": "WEIGHT@C", "SANDBOX": "SANDBOX@A", "SHIELD": "SHIELD@A", "NULL": "NULL@B",
          "ST_CLEANSE": "ST_CLEANSE@A", "ST_EMPOWERED": "ST_EMPOWERED@B", "PI_MOMENTUM": "PI_MOMENTUM@B",
          "PI_NUDGE": "PI_NUDGE@A", "PI_UNDOCK": "PI_UNDOCK@A"}
SMALL = {"ST_CLEANSE@A": "ST_CLEANSE@S"}
NEW = {
    "PATCH": patch, "RECON": recon, "JUDGEMENT": G13.citation, "CITATION": receipt, "FINGERPRINT": fingerprint,
    "ST_CLEANSE@S": cleanse_small, "ALT_F4": alt_f4, "PI_NUDGE_INNER": nudge_inner, "PI_BREACH": breach,
    "PI_EXHAUST": exhaust, "STORM": storm, "PI_RING_LOCK": ring_lock, "BURN": flame2, "ST_BURNING": flame2, "FIREWALL": firewall,
}
_cache = {}


def resolve(name, px=None):
    name = CHOICE.get(name, name)
    if px is not None and px <= 48 and name in SMALL:
        name = SMALL[name]
    return name


def mask(name):
    if name in BYPASS:
        return None
    name = resolve(name)
    f = NEW.get(name) or OPTIONS.get(name)
    if f is None:
        if name in ("INERTIA",):
            return None
        return G13.mask(name)
    if name not in _cache:
        _cache[name] = f()
    return _cache[name].copy()
