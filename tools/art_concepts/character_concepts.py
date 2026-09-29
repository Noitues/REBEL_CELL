"""Pixel-art concept busts for the W5 character briefs (ART_BIBLE 7.1, 7.2; DECISIONS Q6).

Concepts only: they show a painter the silhouette, prop, accent and expression beats of
each character family. They are never shipped as game assets.

Draws 64x64 pixel busts with Pillow and scales them x6 (nearest neighbour, 384 px):
- the eight operative classes x four expressions (neutral, hurt, triumphant, flatlined);
- one agent and one machine bust per corporation (its hue and pattern);
- each boss (the_manifest, renewal_engine, civic_core, commons_array, dispatch_core);
- a labelled contact sheet of all of them.

Deterministic: no randomness; the same run gives the same pixels. Colours are the
Palette tokens (scripts/ui/kit/palette.gd), copied here because this is an offline tool.

    python tools/art_concepts/character_concepts.py [--out docs/art_review/W5/concepts]

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent
N = 64
SCALE = 6

# Palette tokens (scripts/ui/kit/palette.gd).
NIGHT = (6, 8, 22)
INK = (17, 17, 17)
TEXT_HI = (242, 246, 255)
TEXT_MID = (175, 192, 214)
HARM = (255, 68, 51)
PAPER = (242, 238, 228)
CLASS_ACCENTS = {
    "breaker": (255, 61, 168), "wrecker": (255, 122, 26), "ghost": (159, 232, 255), "phantom": (200, 182, 255),
    "rigger": (255, 210, 77), "overclocker": (255, 79, 216), "botnet": (123, 224, 123), "hivemind": (176, 77, 255),
}
CLASSES = list(CLASS_ACCENTS)
CORPS = {
    "solace": ((61, 255, 139), "helix"), "meridian": ((255, 140, 26), "stripes"), "halcyon": ((140, 123, 255), "rings"),
    "orbital": ((127, 168, 255), "stars"), "rebel_cell": ((232, 20, 30), "glitch"),
}
BOSSES = [("renewal_engine", "solace"), ("the_manifest", "meridian"), ("civic_core", "halcyon"),
          ("commons_array", "orbital"), ("dispatch_core", "rebel_cell")]
EXPRESSIONS = ["neutral", "hurt", "triumphant", "flatlined"]
FONT_PATH = ROOT / "assets" / "fonts" / "ShareTechMono-Regular.ttf"


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def grey(c):
    g = int(c[0] * 0.299 + c[1] * 0.587 + c[2] * 0.114)
    return (g, g, g)


class Bust:
    """One 64x64 bust. `k(c)` maps colours (grey when flatlined)."""

    def __init__(self, accent, flat=False):
        self.img = Image.new("RGB", (N, N), NIGHT)
        self.d = ImageDraw.Draw(self.img)
        self.flat = flat
        self.accent = accent
        self.dark = mix(NIGHT, accent, 0.08)
        self.rim = accent
        self.shade = mix(NIGHT, accent, 0.35)

    def k(self, c):
        return mix(grey(c), NIGHT, 0.3) if self.flat else c

    def backdrop(self):
        # Ordered dither from night to a dark accent toward the bottom (pixel-art gradient).
        low = mix(NIGHT, self.accent, 0.45)
        bayer = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
        for y in range(N):
            t = y / (N - 1)
            for x in range(N):
                self.img.putpixel((x, y), self.k(low if t * 16 > bayer[y % 4][x % 4] + 2 else NIGHT))
        for y in range(6, N, 10):
            self.d.line([(0, y), (N - 1, y)], fill=self.k(mix(NIGHT, self.accent, 0.18)))

    def poly(self, pts, fill=None, outline=None):
        self.d.polygon(pts, fill=self.k(fill) if fill else None, outline=self.k(outline) if outline else None)

    def ell(self, box, fill=None, outline=None):
        self.d.ellipse(box, fill=self.k(fill) if fill else None, outline=self.k(outline) if outline else None)

    def rect(self, box, fill=None, outline=None):
        self.d.rectangle(box, fill=self.k(fill) if fill else None, outline=self.k(outline) if outline else None)

    def line(self, pts, col, w=1):
        self.d.line(pts, fill=self.k(col), width=w)

    def px(self, x, y, col):
        if 0 <= x < N and 0 <= y < N:
            self.img.putpixel((int(x), int(y)), self.k(col))


def pattern(b: Bust, box, kind, col):
    """The corp pattern (ART_BIBLE 3.6) in pixels inside `box` where the bust is dark."""
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            if b.img.getpixel((x, y)) != b.k(b.dark):
                continue
            on = False
            if kind == "helix":
                on = (x % 6 == 0) and ((y + [0, 1, 2, 1][(x // 6) % 4]) % 5 == 0)
            elif kind == "stripes":
                on = (x + y) % 6 < 2
            elif kind == "rings":
                cx, cy = (x // 8) * 8 + 4, (y // 8) * 8 + 4
                dd = (x - cx) ** 2 + (y - cy) ** 2
                on = 5 <= dd <= 10 or dd == 0
            elif kind == "stars":
                on = (x % 6 == 3 and y % 6 == 3) or (x % 12 == 0 and y % 12 in (5, 6, 7)) or (y % 12 == 6 and x % 12 in (11, 0, 1))
            elif kind == "glitch":
                on = y % 4 == 0 and ((x * 7 + y * 13) % 23) > 6
            if on:
                b.px(x, y, col)


# --- Operatives ---------------------------------------------------------------------------------

def head(b, cx=32, cy=26, rx=9, ry=11, dx=0, dy=0):
    b.ell((cx - rx + dx, cy - ry + dy, cx + rx + dx, cy + ry + dy), fill=b.dark, outline=b.rim)


def shoulders(b, pts):
    b.poly(pts, fill=b.dark, outline=b.rim)


def eyes_band(b, dx, dy, h=3, col=None):
    b.rect((24 + dx, 24 + dy, 40 + dx, 24 + dy + h - 1), fill=col or b.accent)


def operative(cls: str, expr: str) -> Image.Image:
    acc = CLASS_ACCENTS[cls]
    flat = expr == "flatlined"
    b = Bust(acc, flat)
    b.backdrop()
    # Pose: head shift for the expression (hurt tilts, triumphant lifts, flatlined slumps).
    dx, dy = {"neutral": (0, 0), "hurt": (1, 1), "triumphant": (0, -2), "flatlined": (2, 3)}[expr]
    body = {
        "breaker": [(2, 63), (3, 50), (6, 42), (20, 37), (26, 42), (38, 42), (44, 37), (58, 42), (61, 50), (62, 63)],
        "wrecker": [(4, 63), (3, 46), (8, 38), (19, 38), (26, 42), (38, 42), (50, 46), (55, 52), (56, 63)],
        "ghost": [(8, 63), (10, 52), (16, 42), (48, 42), (54, 52), (56, 63)],
        "phantom": [(6, 63), (7, 52), (13, 43), (26, 41), (38, 41), (51, 43), (57, 52), (58, 63)],
        "rigger": [(6, 63), (7, 50), (13, 43), (51, 43), (57, 50), (58, 63)],
        "overclocker": [(6, 63), (7, 49), (13, 43), (23, 42), (23, 37), (41, 37), (41, 42), (51, 43), (57, 49), (58, 63)],
        "botnet": [(8, 63), (9, 51), (14, 44), (50, 44), (55, 51), (56, 63)],
        "hivemind": [(8, 63), (9, 50), (14, 43), (24, 43), (27, 39), (37, 39), (40, 43), (50, 43), (55, 50), (56, 63)],
    }[cls]
    # Back props (behind the body).
    if cls == "breaker":
        b.line([(51, 44), (49, 10), (46, 6), (42, 7)], b.dark, 3)
        b.line([(51, 44), (49, 10), (46, 6), (42, 7)], acc, 1)
        b.px(42, 7, TEXT_HI)
    if cls == "phantom":
        b.poly([(23, 42), (16, 18), (11, 13), (9, 30), (11, 44)], fill=b.dark, outline=acc)
        b.poly([(41, 42), (48, 18), (53, 13), (55, 30), (53, 44)], fill=b.dark, outline=acc)
    shoulders(b, body)
    if cls == "ghost":
        # The hood is the head's outline.
        b.poly([(33 + dx, 3 + dy), (42 + dx, 10 + dy), (47 + dx, 22 + dy), (48 + dx, 34 + dy), (50, 42), (14, 42), (16 + dx, 34 + dy), (17 + dx, 22 + dy), (23 + dx, 9 + dy)], fill=b.dark, outline=acc)
        b.ell((24 + dx, 17 + dy, 40 + dx, 38 + dy), fill=mix(b.dark, acc, 0.12))
        for x in range(26, 40, 3):
            b.line([(x + dx, 19 + dy), (x + dx, 36 + dy)], b.shade)
        for y in range(20, 37, 3):
            b.line([(26 + dx, y + dy), (38 + dx, y + dy)], b.shade)
    elif cls == "wrecker":
        b.rect((24 + dx, 14 + dy, 40 + dx, 38 + dy), fill=b.dark, outline=acc)
    else:
        head(b, dx=dx, dy=dy)
    # Front props and eyes per class.
    if cls == "breaker":
        b.line([(20, 37), (26, 42)], acc)
        b.line([(44, 37), (38, 42)], acc)
        b.line([(32, 42), (32, 63)], b.shade)
        b.poly([(24 + dx, 15 + dy), (27 + dx, 10 + dy), (30 + dx, 14 + dy), (33 + dx, 9 + dy), (36 + dx, 14 + dy), (39 + dx, 10 + dy), (41 + dx, 17 + dy)], fill=b.dark, outline=acc)
        if expr != "flatlined":
            eyes_band(b, dx, dy, 1 if expr == "hurt" else 3)
    elif cls == "wrecker":
        b.rect((21 + dx, 20 + dy, 43 + dx, 33 + dy), fill=b.dark, outline=acc)
        b.rect((19 + dx, 24 + dy, 21 + dx, 27 + dy), fill=acc)
        b.rect((43 + dx, 24 + dy, 45 + dx, 27 + dy), fill=acc)
        if expr != "flatlined":
            b.rect((24 + dx, 25 + dy, 40 + dx, 25 + dy + (0 if expr == "hurt" else 1)), fill=TEXT_HI if expr == "triumphant" else acc)
        b.line([(25 + dx, 21 + dy), (29 + dx, 31 + dy)], mix(acc, INK, 0.5))
        b.line([(36, 40), (40, 44)], mix(acc, INK, 0.3))
        b.rect((5, 39, 17, 45), fill=b.dark, outline=acc)
    elif cls == "ghost":
        if expr != "flatlined":
            h = 0 if expr == "hurt" else 1
            b.rect((27 + dx, 25 + dy, 29 + dx, 25 + dy + h), fill=TEXT_HI if expr == "triumphant" else acc)
            b.rect((35 + dx, 25 + dy, 37 + dx, 25 + dy + h), fill=TEXT_HI if expr == "triumphant" else acc)
    elif cls == "phantom":
        b.poly([(25 + dx, 17 + dy), (39 + dx, 17 + dy), (40 + dx, 28 + dy), (36 + dx, 35 + dy), (32 + dx, 37 + dy), (28 + dx, 35 + dy), (24 + dx, 28 + dy)], fill=mix(b.dark, acc, 0.35), outline=acc)
        b.line([(26, 42), (32, 60), (38, 42)], acc)
        if expr != "flatlined":
            col = TEXT_HI if expr == "triumphant" else acc
            b.line([(26 + dx, 22 + dy), (30 + dx, 25 + dy)], col, 1 if expr == "hurt" else 2)
            b.line([(38 + dx, 22 + dy), (34 + dx, 25 + dy)], col, 1 if expr == "hurt" else 2)
    elif cls == "rigger":
        for gx in (26, 38):
            b.ell((gx - 5 + dx, 14 + dy, gx + 5 + dx, 24 + dy), fill=b.dark, outline=acc)
            if expr != "flatlined":
                b.ell((gx - 3 + dx, 16 + dy, gx + 3 + dx, 22 + dy), fill=TEXT_HI if expr == "triumphant" else acc)
        b.line([(13, 44), (40, 63)], acc)
        b.line([(51, 44), (24, 63)], acc)
        b.line([(13, 45), (5, 40), (3, 48), (6, 56), (12, 57)], acc, 2)
        b.rect((11, 55, 15, 58), fill=acc)
    elif cls == "overclocker":
        b.rect((22 + dx, 13 + dy, 42 + dx, 16 + dy), fill=b.dark, outline=acc)
        for i, x in enumerate(range(23, 42, 3)):
            hgt = 3 + (3 - abs(i - 3)) * 3
            b.rect((x + dx, 13 - hgt + dy, x + 1 + dx, 13 + dy), fill=b.dark, outline=acc)
            b.px(x + dx, 12 - hgt + dy, TEXT_HI if not b.flat else TEXT_MID)
        if expr != "flatlined":
            for x in range(24, 41, 3):
                b.rect((x + dx, 24 + dy, x + 1 + dx, 25 + dy - (1 if expr == "hurt" else 0)), fill=TEXT_HI if expr == "triumphant" else acc)
        for y in range(38, 42):
            b.line([(26, y), (38, y)], b.shade)
    elif cls == "botnet":
        b.ell((12 + dx, 6 + dy, 52 + dx, 14 + dy), outline=b.shade)
        for i, (x, y) in enumerate([(14, 10), (24, 13), (40, 13), (50, 10), (32, 6)]):
            b.poly([(x - 3 + dx, y + dy), (x + dx, y - 2 + dy), (x + 3 + dx, y + dy), (x + dx, y + 2 + dy)], fill=b.dark, outline=acc)
            b.px(x + dx, y + dy, TEXT_HI)
        if expr != "flatlined":
            eyes_band(b, dx, dy, 1 if expr == "hurt" else 2)
        b.line([(46, 44), (48, 38)], acc)
    elif cls == "hivemind":
        b.d.arc((22 + dx, 14 + dy, 42 + dx, 38 + dy), 180, 360, fill=b.k(acc))
        nodes = [(19, 8), (32, 3), (45, 8)]
        for (x, y), (rx, ry) in zip(nodes, [(25, 18), (32, 15), (39, 18)]):
            b.line([(rx + dx, ry + dy), (x + dx, y + dy)], acc)
        for i in range(3):
            (x0, y0), (x1, y1) = nodes[i], nodes[(i + 1) % 3]
            b.line([(x0 + dx, y0 + dy), (x1 + dx, y1 + dy)], b.shade)
        for x, y in nodes:
            b.ell((x - 2 + dx, y - 2 + dy, x + 2 + dx, y + 2 + dy), fill=b.dark, outline=acc)
            b.px(x + dx, y + dy, TEXT_HI)
        for x in (21, 43):
            b.ell((x - 2 + dx, 24 + dy, x + 2 + dx, 28 + dy), fill=b.dark, outline=acc)
        if expr != "flatlined":
            eyes_band(b, dx, dy, 1 if expr == "hurt" else 2)
        for x in (26, 32, 38):
            b.poly([(x - 2, 52), (x, 50), (x + 2, 52), (x + 2, 54), (x, 56), (x - 2, 54)], outline=b.shade)
    # Mouth and expression marks.
    mx, my = 32 + dx, 33 + dy
    if expr == "neutral":
        b.line([(mx - 2, my), (mx + 2, my)], b.shade)
    elif expr == "hurt":
        b.line([(mx - 3, my), (mx - 1, my - 1), (mx + 1, my), (mx + 3, my - 1)], b.rim)
        b.line([(mx + 5, my - 6), (mx + 7, my - 3)], HARM)
        b.line([(mx + 7, my - 7), (mx + 9, my - 4)], HARM)
    elif expr == "triumphant":
        b.line([(mx - 3, my - 1), (mx - 1, my + 1), (mx + 1, my + 1), (mx + 3, my - 1)], TEXT_HI)
        b.rect((52, 40, 58, 46), fill=b.dark, outline=acc)
        b.rect((53, 46, 57, 63), fill=b.dark, outline=acc)
    else:
        for ex in (28, 36):
            b.line([(ex - 1 + dx, 24 + dy), (ex + 1 + dx, 26 + dy)], TEXT_MID)
            b.line([(ex - 1 + dx, 26 + dy), (ex + 1 + dx, 24 + dy)], TEXT_MID)
        b.line([(mx - 2, my), (mx + 2, my)], TEXT_MID)
        b.d.line([(0, 54), (9, 54), (11, 50), (13, 57), (15, 54), (63, 54)], fill=TEXT_MID)
    return b.img


# --- Enemies and bosses --------------------------------------------------------------------------

def enemy(corp: str, kind: str) -> Image.Image:
    col, pat = CORPS[corp]
    b = Bust(col)
    b.backdrop()
    if kind == "machine":
        b.poly([(24, 63), (27, 40), (37, 40), (40, 63)], fill=b.dark, outline=col)
        for x in (28, 32, 36):
            b.line([(x, 17), (x + (x - 32) // 2, 9)], col)
        b.rect((19, 16, 45, 38), fill=b.dark, outline=col)
        b.ell((25, 20, 39, 34), fill=col)
        b.ell((29, 24, 35, 30), fill=NIGHT)
        b.px(28, 22, TEXT_HI)
        pattern(b, (20, 40, 44, 64), pat, col)
    elif kind == "agent":
        b.poly([(6, 63), (8, 50), (14, 43), (50, 43), (56, 50), (58, 63)], fill=b.dark, outline=col)
        head(b)
        b.poly([(23, 22), (24, 15), (30, 12), (40, 14), (42, 20), (34, 17), (26, 19)], fill=mix(b.dark, col, 0.1), outline=col)
        b.rect((24, 25, 40, 26), fill=col)
        pattern(b, (6, 43, 58, 64), pat, col)
        b.poly([(30, 43), (34, 43), (35, 63), (29, 63)], fill=col)
        b.line([(26, 43), (32, 52)], col)
        b.line([(38, 43), (32, 52)], col)
    return b.img


def boss(corp: str, key: str) -> Image.Image:
    col, pat = CORPS[corp]
    b = Bust(col)
    b.backdrop()
    b.ell((8, 2, 56, 50), outline=col)
    for y in range(3, 50):
        for x in range(8, 57):
            dd = ((x - 32) ** 2 + (y - 26) ** 2) ** 0.5
            if 20 <= dd <= 23 and b.img.getpixel((x, y)) != b.k(col):
                b.img.putpixel((x, y), b.k(b.dark))
    pattern(b, (8, 2, 57, 50), pat, col)
    b.poly([(1, 63), (4, 52), (14, 44), (26, 39), (38, 39), (50, 44), (60, 52), (63, 63)], fill=b.dark, outline=col)
    pattern(b, (1, 40, 64, 64), pat, col)
    b.ell((22, 13, 42, 39), fill=b.dark, outline=col)
    for a in range(5):
        x0 = 22 + a * 5
        top = 5 if a == 2 else 8
        b.line([(x0, 14 + abs(a - 2)), (x0 + (a - 2), top)], col)
    b.rect((24, 24, 40, 26), fill=TEXT_HI)
    # Per boss: one mark so each reads apart (a bar code, a crane, a clock, a dish, a hex).
    mark = {"renewal_engine": [(28, 33), (36, 33)], "the_manifest": [(26, 31), (38, 31), (38, 35)],
            "civic_core": [(32, 30), (32, 34), (35, 34)], "commons_array": [(28, 34), (32, 30), (36, 34)],
            "dispatch_core": [(29, 30), (35, 30), (35, 35), (29, 35), (29, 30)]}[key]
    b.line(mark, col)
    return b.img


def big(img: Image.Image) -> Image.Image:
    return img.resize((N * SCALE, N * SCALE), Image.NEAREST)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(ROOT / "docs" / "art_review" / "W5" / "concepts"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    tiles: list[tuple[str, Image.Image]] = []
    for cls in CLASSES:
        for expr in EXPRESSIONS:
            img = operative(cls, expr)
            big(img).save(out / f"class_{cls}_{expr}.png", optimize=True)
            tiles.append((f"{cls} {expr}", img))
    for corp in CORPS:
        for kind in ("agent", "machine"):
            img = enemy(corp, kind)
            big(img).save(out / f"enemy_{corp}_{kind}.png", optimize=True)
            tiles.append((f"{corp} {kind}", img))
    for key, corp in BOSSES:
        img = boss(corp, key)
        big(img).save(out / f"boss_{key}.png", optimize=True)
        tiles.append((key, img))
    # Contact sheet: 8 columns of 3x tiles with a label under each.
    cols, t, lab, gap = 8, N * 3, 18, 8
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (gap + cols * (t + gap), 44 + rows * (t + lab + gap)), NIGHT)
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(str(FONT_PATH), 14)
        title = ImageFont.truetype(str(FONT_PATH), 22)
    except OSError:
        font = title = ImageFont.load_default()
    d.text((gap, 10), "W5 CHARACTER CONCEPTS (pixel art, 64 px x3; concepts only, never shipped)", fill=(212, 255, 0), font=title)
    for i, (name, img) in enumerate(tiles):
        x = gap + (i % cols) * (t + gap)
        y = 44 + (i // cols) * (t + lab + gap)
        sheet.paste(img.resize((t, t), Image.NEAREST), (x, y))
        d.text((x, y + t + 2), name, fill=TEXT_HI, font=font)
    sheet.save(out / "contact_sheet.png", optimize=True)
    print("CONCEPTS", len(tiles), "->", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
