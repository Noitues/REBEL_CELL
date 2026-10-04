"""Round 13 glyph set (512 box, white = filled, black = cut-out).

Same flat bold language as glyphs10 / slicelib: one solid white silhouette with a few dark
cut-outs, so slicelib.glyph_rgba gives it the dark rounded outline.  Rules used here:
  * strokes >= 40/512 (>= 1.25 px at 16 px), cut-outs >= 24/512;
  * the outer silhouette alone must identify the glyph (checked at 16 px in make_glyphs.py);
  * attacks are aggressive and pointed, defences are solid and blocky (designer taxonomy).

`mask(name)` returns None for names this module does not define (slicelib falls back to the
round 6 / round 10 shapes).  Names in OVERRIDES replace an older shape of the same name.
`BYPASS` lets the sheet render the OLD shape for the before/after confusion panel.
"""
import math
from PIL import Image, ImageDraw, ImageFilter

S = 512
BYPASS = set()


def _new():
    m = Image.new("L", (S, S), 0)
    return m, ImageDraw.Draw(m)


def _rot(pts, ang, cx=256, cy=256):
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in pts]


def _flame_pts(cx, base, w, h, lean=0.0, n=40):
    """Teardrop flame: round belly at the base, tip at base-h, an S lean to the right."""
    pts = []
    for i in range(n + 1):  # right side bottom -> tip
        s = i / n
        y = base - s * h
        hw = w * (math.sin(math.pi * min(1.0, s * 1.6 + 0.12)) ** 0.7 if s < 0.3 else (1 - (s - 0.3) / 0.7) ** 1.15 * 0.98)
        x = cx + hw + lean * h * s * s
        pts.append((x, y))
    for i in range(n, -1, -1):
        s = i / n
        y = base - s * h
        hw = w * (math.sin(math.pi * min(1.0, s * 1.6 + 0.12)) ** 0.7 if s < 0.3 else (1 - (s - 0.3) / 0.7) ** 1.15 * 0.98)
        x = cx - hw + lean * h * s * s
        pts.append((x, y))
    return pts


def _asterisk(d, cx, cy, r, w, fill):
    for k in range(3):
        a = math.radians(90 + k * 60)
        d.line([(cx - r * math.cos(a), cy - r * math.sin(a)), (cx + r * math.cos(a), cy + r * math.sin(a))], fill=fill, width=w)


def _arrow_arc(d, c, r, w, a0, a1, head=1.0, fill=255):
    """Thick arc from a0 to a1 (deg, PIL angles = clockwise from 3 o'clock) with an arrowhead at a1."""
    d.arc([c[0] - r, c[1] - r, c[0] + r, c[1] + r], min(a0, a1), max(a0, a1), fill=fill, width=w)
    sgn = 1 if a1 > a0 else -1
    a = math.radians(a1)
    tip_r = r - w / 2
    px, py = c[0] + tip_r * math.cos(a), c[1] + tip_r * math.sin(a)
    tx, ty = -math.sin(a) * sgn, math.cos(a) * sgn  # direction of travel
    nx, ny = math.cos(a), math.sin(a)
    L = 1.15 * w * head
    Wd = 1.25 * w * head
    d.polygon([(px + tx * L, py + ty * L), (px + nx * Wd, py + ny * Wd), (px - nx * Wd, py - ny * Wd)], fill=fill)


# ============================================================ slice types / programs
def firewall():  # brick wall with three flame tongues on top (was: shield with bricks; read as SHIELD)
    m, d = _new()
    d.rectangle([40, 250, 472, 478], fill=255)
    for (cx, w, h, ln) in ((130, 62, 190, 0.10), (256, 78, 236, 0.0), (382, 62, 190, -0.10)):
        d.polygon(_flame_pts(cx, 262, w, h, ln), fill=255)
    for y in (322, 400):
        d.line([(30, y), (482, y)], fill=0, width=20)
    for y0, y1, xs in ((250, 322, (160, 352)), (322, 400, (256,)), (400, 478, (160, 352))):
        for x in xs:
            d.line([(x, y0), (x, y1)], fill=0, width=20)
    d.line([(30, 252), (482, 252)], fill=0, width=14)  # flames sit ON the wall
    return m


def trojan():  # the horse (designer list); was a gift box
    m, d = _new()
    body = [(150, 418), (176, 330), (206, 280), (176, 262), (112, 282), (74, 252), (84, 206), (162, 136),
            (190, 84), (222, 58), (244, 18), (272, 54), (334, 74), (394, 132), (420, 214), (412, 322), (380, 418)]
    d.polygon(body, fill=255)
    d.rounded_rectangle([96, 404, 416, 456], radius=12, fill=255)  # the wheeled platform
    for x in (152, 360):
        d.ellipse([x - 40, 430, x + 40, 510], fill=255)
        d.ellipse([x - 14, 456, x + 14, 484], fill=0)
    d.ellipse([196, 126, 240, 166], fill=0)  # eye
    for i in range(4):  # mane notches
        y = 110 + i * 62
        d.polygon([(372 + i * 9, y), (420, y + 18), (382 + i * 9, y + 36)], fill=0)
    d.line([(150, 420), (380, 420)], fill=0, width=14)
    return m


def flare():  # sun breaking the horizon (was: rayed disc, read as ZERO-DAY's burst)
    # flat horizon + half disc + a fan of rays on the top only: a silhouette no radial burst,
    # bomb or planet shares
    m, d = _new()
    c = (256, 352)
    d.pieslice([c[0] - 150, c[1] - 150, c[0] + 150, c[1] + 150], 180, 360, fill=255)
    for k in range(5):
        a = math.radians(-162 + k * 36)
        d.line([(c[0] + 196 * math.cos(a), c[1] + 196 * math.sin(a)), (c[0] + 270 * math.cos(a), c[1] + 270 * math.sin(a))],
               fill=255, width=50)
    d.rounded_rectangle([16, 366, 496, 414], radius=18, fill=255)
    d.rounded_rectangle([96, 436, 416, 476], radius=18, fill=255)
    d.arc([c[0] - 104, c[1] - 104, c[0] + 104, c[1] + 104], 200, 250, fill=0, width=28)
    return m



def null():  # tall slashed zero (was: round, read as the 'refusal' no-entry sign)
    m, d = _new()
    d.ellipse([128, 40, 384, 472], fill=255)
    d.ellipse([194, 110, 318, 402], fill=0)
    d.line([(408, 40), (104, 472)], fill=0, width=96)
    d.line([(400, 52), (112, 460)], fill=255, width=52)
    return m


def inertia():  # anvil: weight = resistance (a kettlebell read as LOCKED's padlock at 16 px)
    m, d = _new()
    d.polygon([(20, 120), (150, 120), (170, 100), (492, 100), (492, 210), (420, 230), (360, 250),
               (330, 330), (400, 380), (430, 440), (82, 440), (112, 380), (182, 330), (170, 250),
               (110, 220), (20, 160)], fill=255)
    d.rectangle([60, 440, 452, 480], fill=255)
    d.rectangle([200, 270, 312, 296], fill=0)  # waist cut
    return m



def phishing():  # fish hook with a bait envelope
    m, d = _new()
    d.line([(330, 80), (330, 330)], fill=255, width=52)
    d.ellipse([290, 20, 370, 100], outline=255, width=34)
    d.arc([130, 200, 356, 470], 0, 180, fill=255, width=52)
    d.polygon([(118, 356), (164, 210), (222, 336)], fill=255)  # barb
    d.rounded_rectangle([20, 70, 232, 210], radius=12, fill=255)  # bait: a mail
    d.line([(26, 80), (126, 150), (226, 80)], fill=0, width=22)
    return m


def shield():  # plain heater shield with a chevron band
    m, d = _new()
    d.polygon([(66, 40), (446, 40), (446, 220), (412, 340), (256, 488), (100, 340), (66, 220)], fill=255)
    d.line([(96, 176), (256, 290), (416, 176)], fill=0, width=40)
    return m


def encrypt():  # password field: pill with *** cut out
    m, d = _new()
    d.rounded_rectangle([14, 140, 498, 372], radius=70, fill=255)
    for x in (128, 256, 384):
        _asterisk(d, x, 256, 64, 32, 0)
    return m


def recon():  # magnifier
    m, d = _new()
    d.ellipse([40, 30, 350, 340], outline=255, width=62)
    d.line([(300, 290), (452, 442)], fill=255, width=96)
    d.ellipse([408, 398, 496, 486], fill=255)
    d.arc([96, 86, 294, 284], 190, 260, fill=255, width=30)  # lens glint
    return m


def burn():  # flame with a cut-out inner flame
    m, d = _new()
    d.polygon(_flame_pts(256, 486, 190, 470, 0.08), fill=255)
    d.polygon(_flame_pts(262, 454, 84, 220, -0.12), fill=0)
    d.polygon(_flame_pts(262, 448, 40, 120, -0.05), fill=255)
    return m


def bomb():
    m, d = _new()
    d.ellipse([40, 130, 400, 490], fill=255)
    d.rectangle([270, 120, 350, 200], fill=255)
    d.line([(312, 130), (350, 70), (410, 60)], fill=255, width=30, joint="curve")
    pts = []
    for i in range(16):
        r = 70 if i % 2 == 0 else 26
        a = math.radians(i * 22.5)
        pts.append((440 + r * math.cos(a), 56 + r * math.sin(a)))
    d.polygon(pts, fill=255)
    d.arc([96, 186, 300, 390], 190, 250, fill=0, width=30)
    return m


def safe():  # steel vault door
    m, d = _new()
    d.rounded_rectangle([30, 40, 482, 470], radius=40, fill=255)
    d.rectangle([60, 470, 130, 500], fill=255)
    d.rectangle([382, 470, 452, 500], fill=255)
    d.ellipse([136, 116, 376, 356], fill=0)
    d.ellipse([170, 150, 342, 322], fill=255)
    for k in range(4):
        a = math.radians(45 + k * 90)
        d.line([(256, 236), (256 + 120 * math.cos(a), 236 + 120 * math.sin(a))], fill=255, width=28)
    d.ellipse([226, 206, 286, 266], fill=0)
    d.rectangle([60, 120, 86, 352], fill=0)  # hinge slot
    d.rectangle([426, 400, 470, 420], fill=0)
    return m


def key():
    m, d = _new()
    d.ellipse([30, 120, 250, 340], fill=255)
    d.ellipse([84, 174, 196, 286], fill=0)
    d.rectangle([220, 200, 490, 260], fill=255)
    d.rectangle([380, 260, 420, 340], fill=255)
    d.rectangle([440, 260, 480, 310], fill=255)
    return m


def fingerprint():
    m, d = _new()
    for k, r in enumerate((44, 104, 164, 224)):  # open ridges, gap at the bottom-left like a print
        bb = [256 - r * 0.82, 270 - r, 256 + r * 0.82, 270 + r]
        d.arc(bb, 150 + k * 6, 400 - k * 4, fill=255, width=36)
    d.line([(256, 250), (256, 330)], fill=255, width=36)
    return m


def storm():  # cloud + bolt
    m, d = _new()
    for (x, y, r) in ((150, 200, 100), (270, 150, 130), (380, 220, 92)):
        d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    d.rounded_rectangle([60, 200, 470, 310], radius=55, fill=255)
    bolt = [(280, 250), (176, 400), (250, 400), (206, 506), (352, 336), (276, 336), (330, 250)]
    d.polygon([(x, y) for x, y in bolt], fill=0)
    d.polygon(_rot(bolt, 0), fill=0)
    m2 = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m2).polygon([(x + 0, y + 20) for x, y in bolt], fill=255)
    m2 = m2.filter(ImageFilter.MinFilter(9))
    m.paste(255, (0, 0), m2)
    return m


# ============================================================ statuses (marks)
def corrupted():  # file split by a crack, halves offset (hurts)
    m, d = _new()
    L, R = Image.new("L", (S, S), 0), Image.new("L", (S, S), 0)
    page = [(90, 30), (330, 30), (422, 122), (422, 482), (90, 482)]
    crack = [(250, 0), (300, 120), (222, 210), (300, 300), (230, 400), (270, 512)]
    left = [(0, 0)] + crack + [(0, 512)]
    right = [(512, 0)] + crack + [(512, 512)]
    for img, poly, off in ((L, left, (-34, 22)), (R, right, (34, -22))):
        t = Image.new("L", (S, S), 0)
        td = ImageDraw.Draw(t)
        td.polygon(page, fill=255)
        td.polygon([(330, 30), (330, 122), (422, 122)], fill=0)
        for y in (200, 280, 360):
            td.rectangle([140, y, 372, y + 28], fill=0)
        cl = Image.new("L", (S, S), 0)
        ImageDraw.Draw(cl).polygon(poly, fill=255)
        from PIL import ImageChops
        t = ImageChops.multiply(t, cl)
        img.paste(t.rotate(0, translate=off))
    from PIL import ImageChops
    return ImageChops.lighter(L, R)


def overclocked():  # gauge with the needle pegged in the red (helps, then hurts)
    m, d = _new()
    d.pieslice([24, 70, 488, 534], 180, 360, fill=255)
    d.rectangle([24, 300, 488, 360], fill=255)
    d.pieslice([118, 164, 394, 440], 180, 360, fill=0)
    for k in range(5):
        a = math.radians(180 + k * 45)
        d.line([(256 + 160 * math.cos(a), 302 + 160 * math.sin(a)), (256 + 230 * math.cos(a), 302 + 230 * math.sin(a))], fill=0, width=18)
    a = math.radians(-22)
    d.line([(256, 302), (256 + 200 * math.cos(a), 302 + 200 * math.sin(a))], fill=255, width=44)
    d.ellipse([206, 252, 306, 352], fill=255)
    d.rounded_rectangle([60, 400, 452, 470], radius=20, fill=255)  # base plate
    return m


def encrypted():  # *** over a field underline (status mark of ENCRYPT)
    m, d = _new()
    for x in (96, 256, 416):
        _asterisk(d, x, 220, 84, 46, 255)
    d.rounded_rectangle([30, 364, 482, 420], radius=20, fill=255)
    return m


def parasite():  # tick: fat body hanging head-down, 8 legs, biting mouthparts (drains output)
    m, d = _new()
    d.ellipse([126, 40, 386, 380], fill=255)  # abdomen
    d.ellipse([186, 330, 326, 450], fill=255)  # head
    d.polygon([(226, 430), (256, 506), (286, 430)], fill=255)  # proboscis
    for s in (-1, 1):
        for k, (yy, dx, dy) in enumerate(((150, 118, -70), (220, 130, -10), (290, 124, 50), (350, 100, 110))):
            x0 = 256 + s * 110
            d.line([(x0, yy), (x0 + s * dx * 0.55, yy + dy * 0.2 - 30), (x0 + s * dx, yy + dy)], fill=255, width=30, joint="curve")
    d.arc([176, 90, 336, 250], 200, 340, fill=0, width=24)  # shell plate cut
    d.line([(256, 250), (256, 340)], fill=0, width=22)
    d.line([(170, 360), (342, 360)], fill=0, width=20)  # neck gap
    return m


def cleanse():  # droplet + sparkle
    m, d = _new()
    d.ellipse([60, 190, 340, 470], fill=255)
    d.polygon([(200, 20), (72, 290), (328, 290)], fill=255)
    d.arc([110, 240, 290, 420], 110, 170, fill=0, width=28)
    pts = []
    for i in range(8):
        r = 110 if i % 2 == 0 else 30
        a = math.radians(i * 45 - 90)
        pts.append((390 + r * math.cos(a), 150 + r * math.sin(a)))
    d.polygon(pts, fill=255)
    return m


# ============================================================ temporary slice states (marks)
def frozen():  # snowflake
    m, d = _new()
    c = 256
    for k in range(6):
        a = math.radians(k * 60 - 90)
        ex, ey = c + 230 * math.cos(a), c + 230 * math.sin(a)
        d.line([(c, c), (ex, ey)], fill=255, width=48)
        for (t, L) in ((0.55, 86), (0.82, 60)):
            bx, by = c + 230 * t * math.cos(a), c + 230 * t * math.sin(a)
            for s in (-1, 1):
                b = a + s * math.radians(50)
                d.line([(bx, by), (bx + L * math.cos(b), by + L * math.sin(b))], fill=255, width=36)
    d.polygon(_rot([(c + 70 * math.cos(math.radians(k * 60)), c + 70 * math.sin(math.radians(k * 60))) for k in range(6)], 30), fill=255)
    d.ellipse([c - 26, c - 26, c + 26, c + 26], fill=0)
    return m


def locked():  # padlock
    m, d = _new()
    d.rounded_rectangle([60, 224, 452, 490], radius=36, fill=255)
    d.arc([126, 30, 386, 330], 180, 360, fill=255, width=56)
    d.rectangle([126, 178, 182, 236], fill=255)
    d.rectangle([330, 178, 386, 236], fill=255)
    d.ellipse([220, 300, 292, 372], fill=0)
    d.polygon([(236, 350), (276, 350), (290, 440), (222, 440)], fill=0)
    return m


def empowered():  # solid up arrow on a base bar
    m, d = _new()
    d.polygon([(256, 20), (476, 250), (350, 250), (350, 400), (162, 400), (162, 250), (36, 250)], fill=255)
    d.rounded_rectangle([60, 432, 452, 492], radius=18, fill=255)
    d.line([(150, 236), (256, 132), (362, 236)], fill=0, width=26)
    return m


# ============================================================ card pictograms
def spin_cw():
    m, d = _new()
    _arrow_arc(d, (256, 268), 186, 78, 150, 375, 1.45)
    return m


def spin_ccw():
    return spin_cw().transpose(Image.FLIP_LEFT_RIGHT)


def respin():  # die face: random
    m, d = _new()
    L = Image.new("L", (S, S), 0)
    dl = ImageDraw.Draw(L)
    dl.rounded_rectangle([70, 70, 442, 442], radius=60, fill=255)
    for (x, y) in ((160, 160), (352, 160), (256, 256), (160, 352), (352, 352)):
        dl.ellipse([x - 38, y - 38, x + 38, y + 38], fill=0)
    return L.rotate(14, resample=Image.BICUBIC)


def nudge():  # tick ruler + double-headed arrow: one tick either way
    m, d = _new()
    d.rectangle([40, 420, 472, 470], fill=255)
    for x, h in ((70, 70), (256, 170), (442, 70)):
        d.rectangle([x - 22, 420 - h, x + 22, 430], fill=255)
    d.rectangle([110, 130, 402, 182], fill=255)
    d.polygon([(20, 156), (140, 60), (140, 252)], fill=255)
    d.polygon([(492, 156), (372, 60), (372, 252)], fill=255)
    return m


def nudge_inner():  # same arrow over a ring with its centre dot
    m, d = _new()
    d.ellipse([136, 250, 376, 490], outline=255, width=50)
    d.ellipse([222, 336, 290, 404], fill=255)
    d.rectangle([110, 110, 402, 162], fill=255)
    d.polygon([(20, 136), (140, 40), (140, 232)], fill=255)
    d.polygon([(492, 136), (372, 40), (372, 232)], fill=255)
    return m


def flip():  # mirror: solid and hollow triangle across a dashed axis
    m, d = _new()
    d.polygon([(226, 70), (226, 442), (20, 256)], fill=255)
    d.polygon([(286, 70), (286, 442), (492, 256)], fill=255)
    d.polygon([(316, 160), (316, 352), (420, 256)], fill=0)
    for y in (20, 150, 280, 410):
        d.rectangle([244, y, 268, y + 82], fill=255)
    return m


def draw():  # two cards, the front one with a +
    m, d = _new()
    L = Image.new("L", (S, S), 0)
    ImageDraw.Draw(L).rounded_rectangle([140, 40, 380, 400], radius=30, fill=255)
    m.paste(255, (0, 0), L.rotate(16, resample=Image.BICUBIC, center=(260, 220), translate=(-60, -10)))
    d.rounded_rectangle([170, 110, 438, 494], radius=30, fill=0)
    d.rounded_rectangle([190, 130, 418, 474], radius=24, fill=255)
    d.rectangle([284, 220, 324, 384], fill=0)
    d.rectangle([222, 282, 386, 322], fill=0)
    return m


def ram():  # memory chip: square die with pins on all sides (was: a long stick, read as ENCRYPT's pill)
    m, d = _new()
    d.rounded_rectangle([110, 110, 402, 402], radius=26, fill=255)
    for k in range(4):
        t = 150 + k * 70
        d.rectangle([t - 16, 30, t + 16, 120], fill=255)
        d.rectangle([t - 16, 392, t + 16, 482], fill=255)
        d.rectangle([30, t - 16, 120, t + 16], fill=255)
        d.rectangle([392, t - 16, 482, t + 16], fill=255)
    d.rounded_rectangle([176, 176, 336, 336], radius=12, fill=0)
    d.rectangle([216, 216, 296, 296], fill=255)
    return m



def breach():  # hub ring broken open with shards
    m, d = _new()
    d.ellipse([50, 50, 462, 462], outline=255, width=78)
    d.ellipse([186, 186, 326, 326], fill=255)
    d.polygon([(250, 0), (330, 130), (270, 170), (340, 250), (512, 170), (512, 0)], fill=0)
    d.polygon([(400, 40), (470, 20), (450, 100)], fill=255)
    d.polygon([(370, 140), (440, 130), (400, 190)], fill=255)
    return m


def snap():  # magnet
    m, d = _new()
    d.arc([70, 120, 442, 492], 0, 180, fill=255, width=120)
    d.rectangle([70, 60, 190, 310], fill=255)
    d.rectangle([322, 60, 442, 310], fill=255)
    d.rectangle([60, 110, 200, 136], fill=0)
    d.rectangle([312, 110, 452, 136], fill=0)
    return m


def again():  # rectangular repeat loop
    m, d = _new()
    d.line([(90, 300), (90, 120), (380, 120)], fill=255, width=56, joint="curve")
    d.polygon([(370, 40), (480, 120), (370, 200)], fill=255)
    d.line([(422, 212), (422, 392), (132, 392)], fill=255, width=56, joint="curve")
    d.polygon([(142, 312), (32, 392), (142, 472)], fill=255)
    return m


def free_tag():  # price tag with a hole (free nudge)
    m, d = _new()
    d.polygon([(40, 256), (170, 90), (480, 90), (480, 422), (170, 422)], fill=255)
    d.ellipse([130, 220, 202, 292], fill=0)
    d.line([(260, 200), (400, 200)], fill=0, width=30)
    d.line([(260, 312), (400, 312)], fill=0, width=30)
    return m


def ring_lock():  # ring with a padlock in it
    m, d = _new()
    d.ellipse([20, 20, 492, 492], outline=255, width=50)
    d.rounded_rectangle([160, 250, 352, 390], radius=20, fill=255)
    d.arc([190, 140, 322, 300], 180, 360, fill=255, width=34)
    d.rectangle([190, 214, 222, 254], fill=255)
    d.rectangle([290, 214, 322, 254], fill=255)
    d.ellipse([238, 290, 274, 326], fill=0)
    return m


def perfect():  # the perfect mark: diamond with a centre pip
    m, d = _new()
    d.polygon([(256, 20), (492, 256), (256, 492), (20, 256)], fill=255)
    d.polygon([(256, 110), (402, 256), (256, 402), (110, 256)], fill=0)
    d.ellipse([200, 200, 312, 312], fill=255)
    return m


def undock():  # bay bracket, drone leaving along an arrow
    m, d = _new()
    d.line([(150, 60), (40, 60), (40, 452), (150, 452)], fill=255, width=50)
    d.ellipse([90, 176, 250, 336], fill=255)
    d.ellipse([140, 226, 200, 286], fill=0)
    d.rectangle([270, 228, 410, 284], fill=255)
    d.polygon([(400, 160), (500, 256), (400, 352)], fill=255)
    return m


def all_targets():  # three arrows fanning from one point
    m, d = _new()
    o = (256, 470)
    for ang in (-40, 0, 40):
        a = math.radians(ang - 90)
        tip = (o[0] + 400 * math.cos(a), o[1] + 400 * math.sin(a))
        base = (o[0] + 280 * math.cos(a), o[1] + 280 * math.sin(a))
        d.line([o, base], fill=255, width=46)
        nx, ny = -math.sin(a), math.cos(a)
        d.polygon([tip, (base[0] + nx * 62, base[1] + ny * 62), (base[0] - nx * 62, base[1] - ny * 62)], fill=255)
    d.ellipse([206, 420, 306, 512], fill=255)
    return m


def heart():  # HP
    m, d = _new()
    d.ellipse([30, 60, 270, 300], fill=255)
    d.ellipse([242, 60, 482, 300], fill=255)
    d.polygon([(42, 220), (470, 220), (256, 470)], fill=255)
    return m


def self_damage():  # cracked heart: take damage
    m = heart()
    d = ImageDraw.Draw(m)
    d.line([(262, 90), (220, 200), (300, 270), (236, 360), (262, 480)], fill=0, width=34, joint="curve")
    return m


def exhaust():  # card burning away from the top
    m, d = _new()
    d.rounded_rectangle([110, 120, 402, 492], radius=30, fill=255)
    d.polygon(_flame_pts(256, 330, 96, 300, 0.05), fill=0)
    d.polygon(_flame_pts(256, 300, 70, 280, 0.05), fill=255)
    d.polygon(_flame_pts(256, 290, 30, 120, 0.0), fill=0)
    return m


def reticle():  # target reticle
    m, d = _new()
    d.ellipse([60, 60, 452, 452], outline=255, width=50)
    for (a, b) in (((256, 10), (256, 170)), ((256, 342), (256, 502)), ((10, 256), (170, 256)), ((342, 256), (502, 256))):
        d.line([a, b], fill=255, width=50)
    d.ellipse([226, 226, 286, 286], fill=255)
    return m


def refusal():  # no entry: refused / no damage
    m, d = _new()
    d.ellipse([30, 30, 482, 482], fill=255)
    d.rounded_rectangle([90, 216, 422, 296], radius=14, fill=0)
    return m


def block():  # plain brick wall (block points)
    m, d = _new()
    d.rectangle([30, 90, 482, 440], fill=255)
    for y in (174, 258, 342):
        d.line([(20, y), (492, y)], fill=0, width=22)
    for y0, y1, xs in ((90, 174, (180, 332)), (174, 258, (106, 256, 406)), (258, 342, (180, 332)), (342, 440, (106, 256, 406))):
        for x in xs:
            d.line([(x, y0), (x, y1)], fill=0, width=22)
    return m


def citation():  # gavel over its sound block (was: ticket, read as TARIFF's receipt at 16 px)
    m, d = _new()
    L = Image.new("L", (S, S), 0)
    dl = ImageDraw.Draw(L)
    dl.rounded_rectangle([96, 90, 400, 220], radius=26, fill=255)  # head
    dl.rectangle([128, 74, 164, 236], fill=255)
    dl.rectangle([332, 74, 368, 236], fill=255)
    dl.rectangle([176, 148, 192, 162], fill=0)
    dl.rectangle([226, 214, 270, 470], fill=255)  # handle
    m.paste(255, (0, 0), L.rotate(38, resample=Image.BICUBIC, center=(248, 200), translate=(-10, 10)))
    d.rounded_rectangle([250, 410, 500, 470], radius=14, fill=255)  # sound block
    d.rectangle([280, 470, 470, 494], fill=255)
    return m


OVERRIDES = {"FIREWALL": firewall, "TROJAN": trojan, "FLARE": flare, "NULL": null, "CITATION": citation}
NEW = {
    "INERTIA": inertia,
    # placeholders (not in game)
    "PHISHING": phishing, "SHIELD": shield, "ENCRYPT": encrypt, "RECON": recon, "BURN": burn,
    "BOMB": bomb, "SAFE": safe, "KEY": key, "FINGERPRINT": fingerprint, "STORM": storm,
    # statuses
    "ST_CORRUPTED": corrupted, "ST_OVERCLOCKED": overclocked, "ST_ENCRYPTED": encrypted,
    "ST_PARASITE": parasite, "ST_CLEANSE": cleanse,
    # states (overlay marks)
    "ST_FROZEN": frozen, "ST_LOCKED": locked, "ST_BURNING": burn, "ST_EMPOWERED": empowered,
    # card pictograms
    "PI_SPIN_CW": spin_cw, "PI_SPIN_CCW": spin_ccw, "PI_RESPIN": respin, "PI_NUDGE": nudge,
    "PI_NUDGE_INNER": nudge_inner, "PI_FLIP": flip, "PI_DRAW": draw, "PI_RAM": ram,
    "PI_BREACH": breach, "PI_SNAP": snap, "PI_AGAIN": again, "PI_FREE": free_tag,
    "PI_RING_LOCK": ring_lock, "PI_PERFECT": perfect, "PI_UNDOCK": undock, "PI_ALL": all_targets,
    "PI_HP": heart, "PI_SELF_DMG": self_damage, "PI_EXHAUST": exhaust, "PI_RETICLE": reticle,
    "PI_REFUSAL": refusal, "PI_BLOCK": block,
}
_cache = {}


def mask(name):
    if name in BYPASS:
        return None
    f = OVERRIDES.get(name) or NEW.get(name)
    if f is None:
        return None
    if name not in _cache:
        _cache[name] = f()
    return _cache[name].copy()
