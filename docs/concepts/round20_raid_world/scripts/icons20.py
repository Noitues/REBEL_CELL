"""Round 20: threat vehicle ICONS for the zoomed-out raid map (Pillow, drawn at 4x and downsampled).

Grammar (one rule per channel, so each reads alone and in greyscale):
  SHAPE  = corporation  Meridian crate (square, hazard foot) / Solace capsule (circle) / Halcyon shield /
                        Orbital diamond with fins / REBEL_CELL scrap octagon (jagged)
  FILL   = corp colour (v2 livery colours), ink outline, white die-cut rim (a printed map token, not a sticker)
  GLYPH  = unit role    fast >> / heavy = weight / special = its own verb (seal, dose, freeze, drop, burn)
  CROWN  = upgraded (+) white chevron crown on top + double rim
  NOTCH  = heading (a pointer on the rim, rotates with the unit; the badge itself stays upright)
  RING   = live HP (lit segments, same as the street threat ring)
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
GLYPHS = os.path.abspath(os.path.join(HERE, "..", "..", "round17_slice_system", "glyphs"))
CORP_RGB = {"MERIDIAN": (255, 128, 16), "SOLACE": (108, 255, 40), "HALCYON": (150, 92, 255), "ORBITAL": (120, 236, 255),
            "REBEL_CELL": (255, 26, 34)}
CORP_ACC = {"MERIDIAN": (255, 176, 40), "SOLACE": (226, 238, 226), "HALCYON": (255, 168, 30), "ORBITAL": (232, 246, 255),
            "REBEL_CELL": (255, 120, 80)}
INK = (14, 12, 20)
RIM = (246, 243, 236)
# role glyph per (corp, unit index): 0 fast, 1 heavy, 2 special
SPECIAL = {"MERIDIAN": "state_locked", "SOLACE": "special_dose", "HALCYON": "state_frozen", "ORBITAL": "DROP", "REBEL_CELL": "placeholder_burn"}
UNIT_NAMES = {"MERIDIAN": ("COURIER", "HAULER", "TOW TRUCK"), "SOLACE": ("PARAMEDIC", "COLLECTOR", "DOSER"),
              "HALCYON": ("INSPECTOR", "BAILIFF", "LOCKDOWN"), "ORBITAL": ("SKIMMER", "DEBRIS FIELD", "LANDER"),
              "REBEL_CELL": ("INFORMANT", "LOYALIST", "PURGER")}


def _shape(corp, c, r):
    """Badge outline polygon (or ellipse marker) for a corporation, centre c, radius r."""
    cx, cy = c
    if corp == "MERIDIAN":
        k = r * 0.86
        return [(cx - k, cy - k), (cx + k, cy - k), (cx + k, cy + k), (cx - k, cy + k)]
    if corp == "SOLACE":
        return [(cx + r * math.cos(2 * math.pi * i / 40), cy + r * math.sin(2 * math.pi * i / 40)) for i in range(40)]
    if corp == "HALCYON":
        return [(cx - r * 0.88, cy - r * 0.8), (cx + r * 0.88, cy - r * 0.8), (cx + r * 0.88, cy + r * 0.1), (cx, cy + r * 1.02),
                (cx - r * 0.88, cy + r * 0.1)]
    if corp == "ORBITAL":
        return [(cx, cy - r * 1.05), (cx + r * 0.62, cy - r * 0.2), (cx + r * 1.05, cy + r * 0.25), (cx + r * 0.5, cy + r * 0.3),
                (cx, cy + r * 1.05), (cx - r * 0.5, cy + r * 0.3), (cx - r * 1.05, cy + r * 0.25), (cx - r * 0.62, cy - r * 0.2)]
    # REBEL_CELL: scrappy octagon, uneven corners
    jit = (1.0, 0.86, 1.04, 0.9, 0.98, 0.84, 1.06, 0.92)
    return [(cx + r * jit[i] * math.cos(math.pi / 8 + i * math.pi / 4), cy + r * jit[i] * math.sin(math.pi / 8 + i * math.pi / 4))
            for i in range(8)]


def _glyph_mask(name, px):
    if name == "FAST":
        m = Image.new("L", (256, 256), 0)
        d = ImageDraw.Draw(m)
        for ox in (-46, 40):
            d.polygon([(70 + ox, 40), (150 + ox, 128), (70 + ox, 216), (110 + ox, 216), (190 + ox, 128), (110 + ox, 40)], fill=255)
        return m.resize((px, px), Image.LANCZOS)
    if name == "DROP":
        m = Image.new("L", (256, 256), 0)
        d = ImageDraw.Draw(m)
        d.polygon([(100, 20), (156, 20), (156, 110), (206, 110), (128, 196), (50, 110), (100, 110)], fill=255)
        d.rectangle([40, 214, 216, 238], fill=255)
        return m.resize((px, px), Image.LANCZOS)
    im = Image.open(os.path.join(GLYPHS, name + ".png")).convert("RGBA")
    return im.split()[3].resize((px, px), Image.LANCZOS)


def role_glyph(corp, ui):
    return ("FAST", "special_weight", SPECIAL[corp])[ui]


def vehicle_icon(corp, ui, up=False, size=56, heading=None, hp=None, ss=4, glow=True):
    """RGBA icon (size x size plus margin for the crown / ring). heading in screen radians (0 = right, y down)."""
    S = size * ss
    M = int(S * 0.42)
    W = S + 2 * M
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = (W / 2, W / 2 + S * 0.04)
    r = S * 0.4
    col, acc = CORP_RGB[corp], CORP_ACC[corp]
    if hp is not None:                                   # live HP ring (lit segments)
        R = r * 1.42
        n = 14
        for i in range(n):
            a0 = -math.pi / 2 + 2 * math.pi * i / n
            lit = (i + 0.5) / n <= hp
            d.arc([c[0] - R, c[1] - R, c[0] + R, c[1] + R], math.degrees(a0), math.degrees(a0 + 2 * math.pi / n * 0.7),
                  fill=(255, 68, 51, 255) if lit else (90, 30, 34, 200), width=max(2, int(S * 0.06)))
    poly = _shape(corp, c, r)
    rim_w = S * 0.07
    big = _shape(corp, c, r + rim_w * (2.4 if up else 1.4))
    if up:
        d.polygon(big, fill=RIM + (255,))
        d.polygon(_shape(corp, c, r + rim_w * 1.25), fill=INK + (255,))
        d.polygon(_shape(corp, c, r + rim_w * 0.7), fill=acc + (255,))
    else:
        d.polygon(big, fill=RIM + (255,))
    d.polygon(_shape(corp, c, r + rim_w * 0.35), fill=INK + (255,))
    d.polygon(poly, fill=col + (255,))
    if corp == "MERIDIAN":                               # hazard foot
        k = r * 0.86
        for i in range(5):
            x0 = c[0] - k + i * (2 * k / 5)
            if i % 2 == 0:
                d.polygon([(x0, c[1] + k * 0.62), (x0 + 2 * k / 5, c[1] + k * 0.62), (x0 + 2 * k / 5 - k * 0.18, c[1] + k), (x0 - k * 0.18, c[1] + k)],
                          fill=INK + (255,))
    if corp == "SOLACE":
        d.ellipse([c[0] - r * 0.84, c[1] - r * 0.84, c[0] + r * 0.84, c[1] + r * 0.84], outline=INK + (255,), width=max(1, int(S * 0.025)))
    g = _glyph_mask(role_glyph(corp, ui), int(r * 1.15))
    gl = Image.new("RGBA", g.size, INK + (255,))
    im.paste(gl, (int(c[0] - g.size[0] / 2), int(c[1] - g.size[1] / 2 - (r * 0.1 if corp == "MERIDIAN" else 0))), g)
    if up:                                               # crown: two white chevrons above the badge
        top = min(p[1] for p in big)
        for k in range(2):
            y = top - S * 0.05 - k * S * 0.11
            pts = [(c[0] - S * 0.2, y), (c[0], y - S * 0.1), (c[0] + S * 0.2, y), (c[0] + S * 0.2, y + S * 0.06), (c[0], y - S * 0.04),
                   (c[0] - S * 0.2, y + S * 0.06)]
            d.polygon([(px, py + S * 0.012) for px, py in pts], fill=INK + (255,))
            d.polygon(pts, fill=RIM + (255,))
    if heading is not None:                              # heading notch on the rim
        R = r + rim_w * (2.6 if up else 1.6)
        a = heading
        tip = (c[0] + (R + S * 0.13) * math.cos(a), c[1] + (R + S * 0.13) * math.sin(a))
        l = (c[0] + R * math.cos(a + 0.32), c[1] + R * math.sin(a + 0.32))
        rr = (c[0] + R * math.cos(a - 0.32), c[1] + R * math.sin(a - 0.32))
        d.polygon([tip, l, rr], fill=RIM + (255,), outline=INK + (255,))
    out = im.resize((W // ss, W // ss), Image.LANCZOS)
    if glow:                                             # corp-colour halo so the token glows on the night map
        a = out.split()[3].filter(ImageFilter.GaussianBlur(size * 0.12))
        halo = Image.new("RGBA", out.size, col + (0,))
        halo.putalpha(a.point(lambda v: int(v * 0.55)))
        halo.alpha_composite(out)
        out = halo
    return out
