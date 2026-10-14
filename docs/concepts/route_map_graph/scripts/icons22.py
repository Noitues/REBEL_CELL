"""Round 22: threat icons v4.

  SHAPE   = vehicle type, shared by every corp:  FAST chevron badge / HEAVY block / SPECIAL hexagon (+ its verb;
            Orbital's special is the old lander: DROP) / FLYING diamond with rotor circles at its corners (glyph:
            2 x 2 black circles = a drone without its body).
  FILL    = corp colour = HEALTH: full at max HP, drains from the TOP DOWN as the unit takes damage.
  RING    = a dashed circle, bigger than the icon, in the corp colour (REBEL_CELL red paled toward white so it reads):
            it carries status pips (slowed, frozen, burning, exposed, corrupted) and, on hover / selection only, the
            heading arrow riding it.
  CROWN   = upgraded (two white chevrons) + double rim.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
GLYPHS = os.path.abspath(os.path.join(HERE, "..", "..", "round17_slice_system", "glyphs"))
CORP_RGB = {"MERIDIAN": (255, 128, 16), "SOLACE": (108, 255, 40), "HALCYON": (150, 92, 255), "ORBITAL": (120, 236, 255),
            "REBEL_CELL": (255, 26, 34)}
RING_RGB = dict(CORP_RGB, REBEL_CELL=(255, 170, 172))          # red dashes paled toward white
INK = (14, 12, 20)
RIM = (246, 243, 236)
TYPES = ["FAST", "HEAVY", "SPECIAL", "FLYING"]
VERB = {"MERIDIAN": "state_locked", "SOLACE": "special_dose", "HALCYON": "state_frozen", "ORBITAL": "DROP", "REBEL_CELL": "placeholder_burn"}
UNIT_NAMES = {"MERIDIAN": ("COURIER", "HAULER", "TOW TRUCK"), "SOLACE": ("PARAMEDIC", "COLLECTOR", "DOSER"),
              "HALCYON": ("INSPECTOR", "BAILIFF", "LOCKDOWN"), "ORBITAL": ("SKIMMER", "DEBRIS FIELD", "LANDER"),
              "REBEL_CELL": ("INFORMANT", "LOYALIST", "PURGER")}
STATUS = {"SLOWED": ((90, 170, 255), "SLOW"), "FROZEN": ((190, 240, 255), "state_frozen"), "BURNING": ((255, 120, 40), "state_burning"),
          "EXPOSED": ((255, 255, 255), "EYE"), "CORRUPTED": ((200, 90, 255), "status_corrupted")}


def unit_type(corp, ui):
    return ("FAST", "HEAVY", "SPECIAL")[ui]


def shape(t, c, r):
    cx, cy = c
    if t == "FAST":
        return [(cx, cy - r * 1.08), (cx + r * 0.92, cy - r * 0.18), (cx + r * 0.92, cy + r * 0.86), (cx, cy + r * 0.4),
                (cx - r * 0.92, cy + r * 0.86), (cx - r * 0.92, cy - r * 0.18)]
    if t == "HEAVY":
        k, q = r * 0.9, r * 0.16
        return [(cx - k + q, cy - k), (cx + k - q, cy - k), (cx + k, cy - k + q), (cx + k, cy + k - q), (cx + k - q, cy + k),
                (cx - k + q, cy + k), (cx - k, cy + k - q), (cx - k, cy - k + q)]
    if t == "SPECIAL":
        return [(cx + r * math.cos(math.pi / 6 + i * math.pi / 3), cy + r * math.sin(math.pi / 6 + i * math.pi / 3)) for i in range(6)]
    k = r * 0.86                                              # FLYING: diamond body
    return [(cx, cy - k), (cx + k, cy), (cx, cy + k), (cx - k, cy)]


def rotor_circles(c, r, grow=0.0):
    k = r * 0.86
    rr = r * 0.34 + grow
    return [(c[0] + dx * k, c[1] + dy * k, rr) for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0))]


def glyph_mask(name, px):
    m = Image.new("L", (256, 256), 0)
    d = ImageDraw.Draw(m)
    if name == "FAST":
        for ox in (-46, 40):
            d.polygon([(70 + ox, 40), (150 + ox, 128), (70 + ox, 216), (110 + ox, 216), (190 + ox, 128), (110 + ox, 40)], fill=255)
    elif name == "DROP":
        d.polygon([(100, 20), (156, 20), (156, 110), (206, 110), (128, 196), (50, 110), (100, 110)], fill=255)
        d.rectangle([40, 214, 216, 238], fill=255)
    elif name == "DRONE4":
        for x in (72, 184):
            for y in (72, 184):
                d.ellipse([x - 46, y - 46, x + 46, y + 46], fill=255)
    elif name == "SLOW":                                      # clock with a slowed hand
        d.ellipse([20, 20, 236, 236], fill=255)
        d.ellipse([46, 46, 210, 210], fill=0)
        d.rectangle([118, 60, 138, 136], fill=255)
        d.polygon([(128, 128), (190, 160), (180, 178), (120, 140)], fill=255)
    elif name == "EYE":
        d.ellipse([10, 70, 246, 186], fill=255)
        d.ellipse([40, 90, 216, 166], fill=0)
        d.ellipse([92, 92, 164, 164], fill=255)
    else:
        return Image.open(os.path.join(GLYPHS, name + ".png")).convert("RGBA").split()[3].resize((px, px), Image.LANCZOS)
    return m.resize((px, px), Image.LANCZOS)


def glyph_for(t, corp):
    return {"FAST": "FAST", "HEAVY": "special_weight", "FLYING": "DRONE4"}.get(t) or VERB[corp]


def _dashed_circle(d, c, R, col, width, n=22, phase=0.0, gap=0.42):
    for i in range(n):
        a0 = 360.0 * (i + phase) / n
        d.arc([c[0] - R, c[1] - R, c[0] + R, c[1] + R], a0, a0 + 360.0 / n * (1 - gap), fill=col, width=width)


def icon(t, corp, up=False, size=44, hp=1.0, statuses=(), heading=None, ring=True, ring_phase=0.0, ss=4, glow=True, verb=None):
    S = size * ss
    M = int(S * 0.75)
    W = S + 2 * M
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = (W / 2, W / 2)
    r = S * 0.4
    col = CORP_RGB[corp]
    R = r * 1.78
    if ring:
        _dashed_circle(d, c, R, INK + (255,), max(3, int(S * 0.075)), phase=ring_phase)
        _dashed_circle(d, c, R, RING_RGB[corp] + (255,), max(2, int(S * 0.045)), phase=ring_phase)
    rw = S * 0.07
    grow = rw * (2.4 if up else 1.4)
    if t == "FLYING":
        for (x, y, rr) in rotor_circles(c, r, grow):
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=RIM + (255,))
    d.polygon(shape(t, c, r + grow), fill=RIM + (255,))
    if up:
        d.polygon(shape(t, c, r + rw * 1.25), fill=INK + (255,))
        d.polygon(shape(t, c, r + rw * 0.75), fill=RIM + (255,))
    inner = shape(t, c, r + rw * 0.35)
    if t == "FLYING":
        for (x, y, rr) in rotor_circles(c, r, rw * 0.35):
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=INK + (255,))
    d.polygon(inner, fill=INK + (255,))
    # health fill: the shape (and rotors) filled in the corp colour from the bottom up to hp; the drained top is dark
    fm = Image.new("L", (W, W), 0)
    dm = ImageDraw.Draw(fm)
    dm.polygon(shape(t, c, r), fill=255)
    if t == "FLYING":
        for (x, y, rr) in rotor_circles(c, r):
            dm.ellipse([x - rr, y - rr, x + rr, y + rr], fill=255)
    ys = [p[1] for p in shape(t, c, r)]
    top, bot = min(ys), max(ys)
    if t == "FLYING":
        top, bot = top - r * 0.34, bot + r * 0.34
    level = bot - (bot - top) * max(0.0, min(1.0, hp))
    empty = Image.new("RGBA", (W, W), tuple(int(v * 0.22 + 10) for v in col) + (255,))
    im.paste(empty, (0, 0), fm)
    lm = Image.new("L", (W, W), 0)
    ImageDraw.Draw(lm).rectangle([0, level, W, W], fill=255)
    from PIL import ImageChops
    im.paste(Image.new("RGBA", (W, W), col + (255,)), (0, 0), ImageChops.multiply(fm, lm))
    if 0.0 < hp < 1.0:                                        # the drain line
        xs = [x for x in range(int(c[0] - r * 1.2), int(c[0] + r * 1.2)) if fm.getpixel((x, int(level))) > 128]
        if xs:
            d.line([(xs[0], level), (xs[-1], level)], fill=RIM + (255,), width=max(2, int(S * 0.025)))
    gs = int(r * 1.05)
    g = glyph_mask(verb or glyph_for(t, corp), gs)
    oy = -r * 0.14 if t == "FAST" else 0                      # v4: >> raised clear of the badge notch (was +0.08 r)
    im.paste(Image.new("RGBA", g.size, INK + (255,)), (int(c[0] - gs / 2), int(c[1] - gs / 2 + oy)), g)
    if up:
        topy = min(p[1] for p in shape(t, c, r + grow)) - (r * 0.34 if t == "FLYING" else 0)
        for k in range(2):
            y = topy - S * 0.06 - k * S * 0.11
            pts = [(c[0] - S * 0.2, y), (c[0], y - S * 0.1), (c[0] + S * 0.2, y), (c[0] + S * 0.2, y + S * 0.06), (c[0], y - S * 0.04),
                   (c[0] - S * 0.2, y + S * 0.06)]
            d.polygon([(px, py + S * 0.012) for px, py in pts], fill=INK + (255,))
            d.polygon(pts, fill=RIM + (255,))
    # status pips riding the ring (clockwise from the top-right)
    for i, st in enumerate(statuses):
        scol, gname = STATUS[st]
        a = -math.pi / 4 + i * 0.62
        x, y = c[0] + R * math.cos(a), c[1] + R * math.sin(a)
        pr = S * 0.17
        d.ellipse([x - pr - S * 0.02, y - pr - S * 0.02, x + pr + S * 0.02, y + pr + S * 0.02], fill=INK + (255,))
        d.ellipse([x - pr, y - pr, x + pr, y + pr], fill=scol + (255,))
        gm = glyph_mask(gname, int(pr * 1.35))
        im.paste(Image.new("RGBA", gm.size, INK + (255,)), (int(x - gm.size[0] / 2), int(y - gm.size[1] / 2)), gm)
    if heading is not None:                                   # hover / select: arrow riding the ring
        a = heading
        tip = (c[0] + (R + S * 0.2) * math.cos(a), c[1] + (R + S * 0.2) * math.sin(a))
        l = (c[0] + (R - S * 0.05) * math.cos(a + 0.3), c[1] + (R - S * 0.05) * math.sin(a + 0.3))
        rr = (c[0] + (R - S * 0.05) * math.cos(a - 0.3), c[1] + (R - S * 0.05) * math.sin(a - 0.3))
        d.polygon([tip, l, rr], fill=(255, 222, 30, 255), outline=INK + (255,))
    out = im.resize((W // ss, W // ss), Image.LANCZOS)
    if glow:
        a = out.split()[3].filter(ImageFilter.GaussianBlur(size * 0.1))
        halo = Image.new("RGBA", out.size, col + (0,))
        halo.putalpha(a.point(lambda v: int(v * 0.45)))
        halo.alpha_composite(out)
        out = halo
    return out


def unit_icon(corp, ui, up=False, size=44, **kw):
    return icon(unit_type(corp, ui), corp, up=up, size=size, **kw)
