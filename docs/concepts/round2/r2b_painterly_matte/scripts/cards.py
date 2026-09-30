"""r2b_painterly_matte - card and slice-glyph renderer shared by the combat and shop stills.
Cards are drawn crisp (2x supersampled) with a painted art window cut from the city plates."""
import math, textwrap
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import paintlib as P

KIND_RGB = {"ATTACK": (206, 56, 42), "BLOCK": (44, 158, 156), "HACK": (140, 78, 214), "CREDIT": (232, 172, 60),
            "BLANK": (70, 70, 82)}

def rounded_clip(w, h, n):
    return [(n, 0), (w - n, 0), (w, n), (w, h - n), (w - n, h), (n, h), (0, h - n), (0, n)]

def glyph(d, kind, cx, cy, r, ss=1, fill=(250, 242, 222, 255), outline=(20, 14, 10, 255)):
    """Vector glyphs for slice kinds: blade, shield, eye, coin."""
    def S(pts):
        return [(x * ss, y * ss) for (x, y) in pts]
    ow = max(1, int(r * 0.10 * ss))
    if kind == "ATTACK":
        blade = [(cx, cy - r), (cx + r * 0.3, cy - r * 0.55), (cx + r * 0.3, cy + r * 0.35), (cx - r * 0.3, cy + r * 0.35), (cx - r * 0.3, cy - r * 0.55)]
        guard = [(cx - r * 0.5, cy + r * 0.35), (cx + r * 0.5, cy + r * 0.35), (cx + r * 0.5, cy + r * 0.5), (cx - r * 0.5, cy + r * 0.5)]
        grip = [(cx - r * 0.13, cy + r * 0.5), (cx + r * 0.13, cy + r * 0.5), (cx + r * 0.13, cy + r * 0.95), (cx - r * 0.13, cy + r * 0.95)]
        for poly in (blade, guard, grip):
            d.polygon(S(poly), fill=fill, outline=outline, width=ow)
    elif kind == "BLOCK":
        pts = []
        for k in range(21):
            t = k / 20
            x = cx - r * 0.75 + r * 1.5 * t
            y = cy - r * 0.8 + math.sin(t * math.pi) * -r * 0.08
            pts.append((x, y))
        for k in range(21):
            t = k / 20
            ang = math.pi * t
            pts.append((cx + r * 0.75 * math.cos(ang), cy + r * 0.05 + r * 0.9 * math.sin(ang)))
        d.polygon(S(pts), fill=fill, outline=outline, width=ow)
        d.line(S([(cx, cy - r * 0.7), (cx, cy + r * 0.85)]), fill=outline, width=ow)
    elif kind == "HACK":
        eye = [(cx - r, cy)] + [(cx - r + 2 * r * k / 16, cy - math.sin(k / 16 * math.pi) * r * 0.62) for k in range(17)] + \
              [(cx + r - 2 * r * k / 16, cy + math.sin(k / 16 * math.pi) * r * 0.62) for k in range(17)]
        d.polygon(S(eye), fill=fill, outline=outline, width=ow)
        d.ellipse(S([(cx - r * 0.36, cy - r * 0.36), (cx + r * 0.36, cy + r * 0.36)]), fill=outline)
        d.ellipse(S([(cx - r * 0.14, cy - r * 0.3), (cx + r * 0.04, cy - r * 0.12)]), fill=fill)
    elif kind == "CREDIT":
        d.ellipse(S([(cx - r * 0.85, cy - r * 0.85), (cx + r * 0.85, cy + r * 0.85)]), fill=fill, outline=outline, width=ow)
        d.arc(S([(cx - r * 0.42, cy - r * 0.45), (cx + r * 0.42, cy + r * 0.45)]), 40, 320, fill=outline, width=ow)
        d.line(S([(cx + r * 0.05, cy - r * 0.62), (cx - r * 0.05, cy + r * 0.62)]), fill=outline, width=max(1, ow // 2 + 1))
    else:
        d.line(S([(cx - r * 0.5, cy), (cx + r * 0.5, cy)]), fill=fill, width=ow * 2)

def make_card(title, cost, kind, text, art, w=210, h=300, ss=2, glow=None):
    """Returns an RGBA card image (w x h at 1x, plus a margin for the glow)."""
    M = 24
    im = Image.new("RGBA", ((w + 2 * M) * ss, (h + 2 * M) * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    def S(pts):
        return [((x + M) * ss, (y + M) * ss) for (x, y) in pts]
    shape = rounded_clip(w, h, 14)
    if glow:
        g = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).polygon(S(shape), fill=glow + (230,))
        g = g.filter(ImageFilter.GaussianBlur(14 * ss))
        im = Image.alpha_composite(im, g); d = ImageDraw.Draw(im)
    # drop shadow
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(x + 6 * ss, y + 8 * ss) for (x, y) in S(shape)], fill=(0, 0, 0, 150))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(6 * ss))); d = ImageDraw.Draw(im)
    d.polygon(S(shape), fill=(24, 26, 32, 255))
    # art window
    ax0, ay0, ax1, ay1 = 12, 50, w - 12, 172
    a = ImageOps.fit(art.convert("RGB"), ((ax1 - ax0) * ss, (ay1 - ay0) * ss), Image.LANCZOS)
    im.paste(a, ((ax0 + M) * ss, (ay0 + M) * ss))
    d.rectangle(S([(ax0, ay0), (ax1, ay1)]), outline=P.GOLD + (255,), width=2 * ss)
    # kind ribbon
    kc = KIND_RGB[kind]
    rib = [(6, 178), (w - 6, 178), (w - 14, 200), (14, 200)]
    d.polygon(S(rib), fill=kc + (255,))
    d.line(S(rib + [rib[0]]), fill=P.GOLD_SH + (255,), width=1 * ss)
    f_kind = P.font("georgiab.ttf", 12 * ss)
    d.text(((w / 2 + M) * ss, (189 + M) * ss), kind, font=f_kind, fill=(255, 250, 238, 255), anchor="mm")
    # title
    f_t = P.font("georgiab.ttf", 17 * ss)
    tw = d.textlength(title, font=f_t)
    if tw > (w - 70) * ss:
        f_t = P.font("georgiab.ttf", 14 * ss)
    d.text(((w / 2 + 12 + M) * ss, (28 + M) * ss), title, font=f_t, fill=(248, 234, 204, 255), anchor="mm")
    d.line(S([(44, 43), (w - 16, 43)]), fill=P.GOLD_SH + (255,), width=1 * ss)
    # rules text
    f_b = P.font("georgia.ttf", 13 * ss)
    lines = textwrap.wrap(text, 26)
    for i, ln in enumerate(lines[:5]):
        d.text(((w / 2 + M) * ss, (220 + i * 17 + M) * ss), ln, font=f_b, fill=(226, 216, 196, 255), anchor="mm")
    # brass frame
    d.line(S(shape + [shape[0]]), fill=P.GOLD + (255,), width=3 * ss, joint="curve")
    inner = rounded_clip(w - 10, h - 10, 11)
    d.line([((x + 5 + M) * ss, (y + 5 + M) * ss) for (x, y) in inner + [inner[0]]], fill=P.GOLD_SH + (255,), width=1 * ss)
    # cost gem
    cx, cy, r = 22, 24, 19
    d.ellipse(S([(cx - r - 3, cy - r - 3), (cx + r + 3, cy + r + 3)]), fill=(20, 14, 8, 255))
    d.ellipse(S([(cx - r, cy - r), (cx + r, cy + r)]), fill=P.GOLD + (255,))
    d.ellipse(S([(cx - r + 4, cy - r + 4), (cx + r - 4, cy + r - 4)]), fill=(24, 92, 104, 255))
    d.ellipse(S([(cx - r + 7, cy - r + 6), (cx + 2, cy - 4)]), fill=(120, 230, 222, 120))
    d.text(((cx + M) * ss, (cy + 1 + M) * ss), str(cost), font=P.font("georgiab.ttf", 20 * ss), fill=(255, 255, 255, 255), anchor="mm")
    # kind glyph small on art corner
    glyph(d, kind, w - 26 + M, 66 + M, 11, ss)
    return im.resize((im.size[0] // ss, im.size[1] // ss), Image.LANCZOS), M

CARD_SET = [
    ("Monowire Lash", 1, "ATTACK", "Spin 5 ticks. Landing on ATTACK deals 7 damage."),
    ("Riot Shield", 1, "BLOCK", "Gain 6 armour. Your next BLOCK slice counts twice."),
    ("Overclock", 2, "HACK", "Spin the enemy wheel back 4 ticks."),
    ("Skim Account", 0, "CREDIT", "Spin 3 ticks. On CREDIT gain 25 credits."),
    ("Ghost Protocol", 2, "HACK", "Turn one enemy ATTACK slice to BLANK this round."),
]
