"""Round 21: threat ICONS v3 (zoomed-out raid map). Designer: one SHAPE per vehicle TYPE, shared by every corporation;
the corporation is the fill COLOUR only. No heading on the icon (heading = a ring arrow on hover / selection only).

  FAST     chevron badge (point up)      >>        courier, paramedic, inspector, skimmer, informant
  HEAVY    thick square block            weight    hauler, collector, bailiff, debris field, loyalist
  SPECIAL  hexagon + its verb glyph      seal / dose / freeze / burn    tow truck, doser, lockdown, purger
  LANDER   point-down triangle (pod)     drop      lander
  FLYING   winged diamond                rotor     choppers, gunships, drones (heat rigs, when they become targets)
  UPGRADED two white chevrons on top + double rim;  HP = lit ring segments (same as the street ring)
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
GLYPHS = os.path.abspath(os.path.join(HERE, "..", "..", "round17_slice_system", "glyphs"))
CORP_RGB = {"MERIDIAN": (255, 128, 16), "SOLACE": (108, 255, 40), "HALCYON": (150, 92, 255), "ORBITAL": (120, 236, 255),
            "REBEL_CELL": (255, 26, 34)}
INK = (14, 12, 20)
RIM = (246, 243, 236)
TYPES = ["FAST", "HEAVY", "SPECIAL", "LANDER", "FLYING"]
VERB = {"MERIDIAN": "state_locked", "SOLACE": "special_dose", "HALCYON": "state_frozen", "REBEL_CELL": "placeholder_burn"}
UNIT_NAMES = {"MERIDIAN": ("COURIER", "HAULER", "TOW TRUCK"), "SOLACE": ("PARAMEDIC", "COLLECTOR", "DOSER"),
              "HALCYON": ("INSPECTOR", "BAILIFF", "LOCKDOWN"), "ORBITAL": ("SKIMMER", "DEBRIS FIELD", "LANDER"),
              "REBEL_CELL": ("INFORMANT", "LOYALIST", "PURGER")}


def unit_type(corp, ui):
    if ui == 0:
        return "FAST"
    if ui == 1:
        return "HEAVY"
    return "LANDER" if corp == "ORBITAL" else "SPECIAL"


def shape(t, c, r):
    cx, cy = c
    if t == "FAST":
        return [(cx, cy - r * 1.08), (cx + r * 0.92, cy - r * 0.18), (cx + r * 0.92, cy + r * 0.86), (cx, cy + r * 0.4),
                (cx - r * 0.92, cy + r * 0.86), (cx - r * 0.92, cy - r * 0.18)]
    if t == "HEAVY":
        k = r * 0.9
        q = r * 0.16
        return [(cx - k + q, cy - k), (cx + k - q, cy - k), (cx + k, cy - k + q), (cx + k, cy + k - q), (cx + k - q, cy + k),
                (cx - k + q, cy + k), (cx - k, cy + k - q), (cx - k, cy - k + q)]
    if t == "SPECIAL":
        return [(cx + r * math.cos(math.pi / 6 + i * math.pi / 3), cy + r * math.sin(math.pi / 6 + i * math.pi / 3)) for i in range(6)]
    if t == "LANDER":
        return [(cx - r * 1.0, cy - r * 0.72), (cx + r * 1.0, cy - r * 0.72), (cx, cy + r * 1.1)]
    # FLYING: diamond with swept wings
    return [(cx, cy - r * 0.95), (cx + r * 0.42, cy - r * 0.2), (cx + r * 1.15, cy - r * 0.05), (cx + r * 0.45, cy + r * 0.25),
            (cx, cy + r * 0.95), (cx - r * 0.45, cy + r * 0.25), (cx - r * 1.15, cy - r * 0.05), (cx - r * 0.42, cy - r * 0.2)]


def _grow(t, c, r, k):
    return shape(t, c, r + k)


def glyph_mask(name, px):
    m = Image.new("L", (256, 256), 0)
    d = ImageDraw.Draw(m)
    if name == "FAST":
        for ox in (-46, 40):
            d.polygon([(70 + ox, 40), (150 + ox, 128), (70 + ox, 216), (110 + ox, 216), (190 + ox, 128), (110 + ox, 40)], fill=255)
    elif name == "DROP":
        d.polygon([(100, 20), (156, 20), (156, 110), (206, 110), (128, 196), (50, 110), (100, 110)], fill=255)
        d.rectangle([40, 214, 216, 238], fill=255)
    elif name == "ROTOR":
        d.ellipse([98, 98, 158, 158], fill=255)
        for a in (0.4, 0.4 + math.pi / 2, 0.4 + math.pi, 0.4 + 3 * math.pi / 2):
            d.line([(128, 128), (128 + 118 * math.cos(a), 128 + 118 * math.sin(a))], fill=255, width=30)
    else:
        return Image.open(os.path.join(GLYPHS, name + ".png")).convert("RGBA").split()[3].resize((px, px), Image.LANCZOS)
    return m.resize((px, px), Image.LANCZOS)


def glyph_for(t, corp):
    return {"FAST": "FAST", "HEAVY": "special_weight", "LANDER": "DROP", "FLYING": "ROTOR"}.get(t) or VERB.get(corp, "state_locked")


def icon(t, corp, up=False, size=44, hp=None, ss=4, glow=True, verb=None):
    S = size * ss
    M = int(S * 0.42)
    W = S + 2 * M
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = (W / 2, W / 2 + S * 0.03)
    r = S * 0.4
    col = CORP_RGB[corp]
    if hp is not None:
        R = r * 1.45
        n = 14
        for i in range(n):
            a0 = -math.pi / 2 + 2 * math.pi * i / n
            lit = (i + 0.5) / n <= hp
            d.arc([c[0] - R, c[1] - R, c[0] + R, c[1] + R], math.degrees(a0), math.degrees(a0 + 2 * math.pi / n * 0.7),
                  fill=(255, 68, 51, 255) if lit else (90, 30, 34, 200), width=max(2, int(S * 0.06)))
    rw = S * 0.07
    big = _grow(t, c, r, rw * (2.4 if up else 1.4))
    d.polygon(big, fill=RIM + (255,))
    if up:
        d.polygon(_grow(t, c, r, rw * 1.25), fill=INK + (255,))
        d.polygon(_grow(t, c, r, rw * 0.75), fill=RIM + (255,))
    d.polygon(_grow(t, c, r, rw * 0.35), fill=INK + (255,))
    d.polygon(shape(t, c, r), fill=col + (255,))
    gs = int(r * (1.0 if t in ("LANDER",) else 1.12))
    g = glyph_mask(verb or glyph_for(t, corp), gs)
    oy = -r * 0.28 if t == "LANDER" else (r * 0.08 if t == "FAST" else 0)
    im.paste(Image.new("RGBA", g.size, INK + (255,)), (int(c[0] - gs / 2), int(c[1] - gs / 2 + oy)), g)
    if up:
        top = min(p[1] for p in big)
        for k in range(2):
            y = top - S * 0.05 - k * S * 0.11
            pts = [(c[0] - S * 0.2, y), (c[0], y - S * 0.1), (c[0] + S * 0.2, y), (c[0] + S * 0.2, y + S * 0.06), (c[0], y - S * 0.04),
                   (c[0] - S * 0.2, y + S * 0.06)]
            d.polygon([(px, py + S * 0.012) for px, py in pts], fill=INK + (255,))
            d.polygon(pts, fill=RIM + (255,))
    out = im.resize((W // ss, W // ss), Image.LANCZOS)
    if glow:
        a = out.split()[3].filter(ImageFilter.GaussianBlur(size * 0.12))
        halo = Image.new("RGBA", out.size, col + (0,))
        halo.putalpha(a.point(lambda v: int(v * 0.55)))
        halo.alpha_composite(out)
        out = halo
    return out


def unit_icon(corp, ui, up=False, size=44, hp=None, glow=True):
    return icon(unit_type(corp, ui), corp, up=up, size=size, hp=hp, glow=glow)
