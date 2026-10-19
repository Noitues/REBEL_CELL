"""Street round 2: the sign texture library as draw lists (port of the art-pass `r2_signs.py`, without PIL).

One texture per planned sign, from its style, word and hue. Styles: box (shop / secondary box sign), blade (vertical stacked
letters), wall (hero poster board), ad (one of the storyboard's ad plates, cropped to the aspect at render time), holo (black =
additive), shop (lit shopfront glazing with a fascia word). The pixel size follows the sign's aspect; text is fitted to the sign,
so a sign never clips its word.

The plate drew these with PIL. Here each style returns `dict(w, h, ops)`: the same draw calls in order, as data (`grad`, `text`,
`rect`, `ellipse`, `line`, `glow`, `holo_shift`, `ad`), which the renderer (step 2) replays with Godot's draw calls. The one thing a
draw list cannot know is how wide a word is, so the text rule takes `measure(font, size, text) -> (w, h)` (the glyph box of the
word at that size, PIL `textbbox` anchor "lt") and fits the largest size whose box is inside the sign's field: the word never clips.
Fonts are the names "anton" and "mono" (assets/fonts/Anton-Regular.ttf, ShareTechMono-Regular.ttf)."""
import random
from typing import Any, Callable, Dict, List

from .config import SIGN_TEX

Measure = Callable[[str, int, str], Any]
PALE = tuple(SIGN_TEX["pale"])


def c8(col, k=1.0):
    """Colour 0..1 to ints 0..255, scaled by k."""
    return tuple(int(max(0, min(255, v * 255 * k))) for v in col)


class TableMeasure:
    """`measure` from recorded rows `[font, size, text, w, h]` (the glyph boxes the plate's PIL fonts gave): a query outside the table is an
    error, so a fit search that asks something the plate never asked fails loudly."""

    def __init__(self, rows) -> None:
        self.table = {(r[0], int(r[1]), r[2]): (r[3], r[4]) for r in rows}

    def __call__(self, font: str, size: int, text: str):
        return self.table[(font, size, text)]


def fit_font(measure: Measure, s: str, font: str, w: int, h: int) -> int:
    """The largest font size (6..600) whose glyph box for `s` is inside w x h: the fit-to-sign rule."""
    lo, hi = SIGN_TEX["fit_lo"], SIGN_TEX["fit_hi"]
    while hi - lo > 1:
        m = (lo + hi) // 2
        bw, bh = measure(font, m, s)
        if bw <= w and bh <= h:
            lo = m
        else:
            hi = m
    return lo


def size_for(aspect, long_px=SIGN_TEX["long_px"]):
    """Texture size (w, h) by the sign's aspect: the long side is `long_px`."""
    if aspect >= 1:
        return long_px, max(SIGN_TEX["min_px"], int(long_px / aspect))
    return max(SIGN_TEX["min_px"], int(long_px * aspect)), long_px


class Draw:
    """The draw list of one texture."""

    def __init__(self, w: int, h: int) -> None:
        self.w, self.h = w, h
        self.ops: List[Dict[str, Any]] = []

    def grad(self, top, bot):
        self.ops.append(dict(op="grad", w=self.w, h=self.h, top=list(top), bot=list(bot)))

    def text(self, xy, s, font, size, fill, anchor):
        self.ops.append(dict(op="text", xy=list(xy), s=s, font=font, size=size, fill=list(fill), anchor=anchor))

    def rect(self, box, fill=None, outline=None, width=1):
        self.ops.append(dict(op="rect", box=list(box), fill=list(fill) if fill is not None else None,
                             outline=list(outline) if outline is not None else None, width=width))

    def ellipse(self, box, outline, width):
        self.ops.append(dict(op="ellipse", box=list(box), outline=list(outline), width=width))

    def line(self, pts, fill, width=0):
        self.ops.append(dict(op="line", pts=[list(p) for p in pts], fill=list(fill), width=width))

    def glow(self, k=0.55, r=8):
        self.ops.append(dict(op="glow", k=k, r=r))

    def spec(self) -> Dict[str, Any]:
        return dict(w=self.w, h=self.h, ops=self.ops)


def box(word, sub, col, aspect, r, measure):
    """Shop / secondary box sign."""
    w, h = size_for(aspect)
    d = Draw(w, h)
    d.grad(c8(col, 0.10), (6, 4, 12))
    f = fit_font(measure, word, "anton", int(w * 0.84), int(h * (0.50 if sub else 0.62)))
    d.text((w // 2, int(h * (0.42 if sub else 0.5))), word, "anton", f, c8(col), "mm")
    if sub:
        f2 = fit_font(measure, sub, "mono", int(w * 0.6), int(h * 0.16))
        d.text((w // 2, int(h * 0.80)), sub, "mono", f2, PALE, "mm")
    t = max(4, h // 18)
    d.rect((t, t, w - t, h - t), outline=c8(col, 0.9), width=t)
    d.glow()
    return d.spec()


def blade(word, sub, col, aspect, r, measure):
    """Vertical stacked letters on a dark board."""
    w, h = size_for(aspect)
    d = Draw(w, h)
    d.grad((16, 4, 24), (4, 2, 10))
    ch = [c for c in word if c != " "]
    n = len(ch) + (1 if sub else 0)
    pitch = (h - 0.08 * h) / max(1, n)
    f = fit_font(measure, "W", "anton", int(w * 0.78), int(pitch * 0.86))
    y = 0.04 * h + pitch / 2
    for c in ch:
        d.text((w // 2, int(y)), c, "anton", f, c8(col), "mm")
        y += pitch
    if sub:
        f2 = fit_font(measure, sub, "mono", int(w * 0.8), int(pitch * 0.4))
        d.text((w // 2, int(y)), sub, "mono", f2, PALE, "mm")
    t = max(4, w // 22)
    d.rect((t, t, w - t, h - t), outline=c8(col, 0.9), width=t)
    d.glow(0.6)
    return d.spec()


def wall(word, sub, col, aspect, r, measure):
    """A hero poster: a hue field, a graphic (rings / bars / chevrons by seed), the word large, a sub line."""
    w, h = size_for(aspect, SIGN_TEX["long_px_big"])
    d = Draw(w, h)
    d.grad(c8(col, 0.30), c8(col, 0.05))
    g = r.randrange(3)
    acc = c8(col, 1.0)
    if g == 0:
        cx, cy = int(w * 0.78), int(h * 0.45)
        for k in range(5):
            rr = int(h * (0.12 + 0.08 * k))
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), c8(col, 0.9 - 0.15 * k), max(3, h // 70))
    elif g == 1:
        for k in range(7):
            x = int(w * (0.62 + 0.05 * k))
            d.rect((x, int(h * (0.15 + 0.07 * (k % 3))), x + max(6, w // 60), int(h * 0.85)), fill=c8(col, 0.9 - 0.08 * k))
    else:
        for k in range(4):
            y = int(h * (0.25 + 0.15 * k))
            d.line([(int(w * 0.62), y), (int(w * 0.78), y + int(h * 0.08)), (int(w * 0.94), y)], c8(col, 0.95 - 0.15 * k), max(4, h // 40))
    f = fit_font(measure, word, "anton", int(w * 0.56), int(h * 0.42))
    d.text((int(w * 0.06), int(h * 0.42)), word, "anton", f, (250, 248, 255), "lm")
    d.line([(int(w * 0.06), int(h * 0.66)), (int(w * 0.5), int(h * 0.66))], acc, max(3, h // 60))
    f2 = fit_font(measure, sub or "24 H", "mono", int(w * 0.4), int(h * 0.11))
    d.text((int(w * 0.06), int(h * 0.78)), sub or "24 H", "mono", f2, PALE, "lm")
    t = max(6, h // 40)
    d.rect((t, t, w - t, h - t), outline=acc, width=t)
    d.glow(0.45)
    return d.spec()


def ad(name, aspect):
    """An ad plate: the renderer crops the plate to `aspect` (centre crop) at render time."""
    return dict(w=None, h=None, ops=[dict(op="ad", name=name, aspect=aspect)])


def holo(word, sub, col, aspect, r, measure):
    """Holo sign: black = additive, scanlines, red / blue channel shift."""
    w, h = size_for(aspect)
    d = Draw(w, h)
    d.ops.append(dict(op="fill", w=w, h=h, col=[0, 0, 0]))
    f = fit_font(measure, word, "anton", int(w * 0.8), int(h * 0.5))
    d.text((w // 2, int(h * 0.42)), word, "anton", f, c8(col), "mm")
    if sub:
        f2 = fit_font(measure, sub, "mono", int(w * 0.6), int(h * 0.14))
        d.text((w // 2, int(h * 0.78)), sub, "mono", f2, PALE, "mm")
    d.rect((6, 6, w - 6, h - 6), outline=c8(col), width=5)
    for y in range(0, h, 4):
        d.line([(0, y), (w, y)], (0, 0, 0), 1)
    d.ops.append(dict(op="holo_shift", r=-3, b=3))
    return d.spec()


def shop(word, col, aspect, r, measure):
    """Lit shopfront glazing: a warm / hue interior gradient, mullions, shelf silhouettes, a fascia band with a word."""
    w, h = size_for(aspect, SIGN_TEX["long_px_big"])
    d = Draw(w, h)
    warm = r.random() < 0.5
    top = (255, 214, 160) if warm else c8(col, 0.95)
    d.grad(tuple(int(v * 0.55) for v in top), tuple(int(v * 0.95) for v in top))
    fb = int(h * 0.26)
    d.rect((0, 0, w, fb), fill=(14, 10, 20))
    f = fit_font(measure, word, "anton", int(w * 0.35), int(fb * 0.7))
    d.text((int(w * 0.05), fb // 2), word, "anton", f, c8(col), "lm")
    # shelves with small lit goods, a dark door, mullions over all
    for k in range(3):
        y = int(fb + (h - fb) * (0.3 + 0.22 * k))
        d.rect((0, y, w, y + 4), fill=(40, 30, 44))
        x = r.randint(4, 30)
        while x < w - 20:
            gw = r.randint(8, 22)
            gc = r.choice([c8(col), (255, 240, 220), (120, 220, 255), (255, 120, 190)])
            d.rect((x, y - r.randint(10, 26), x + gw, y), fill=tuple(int(v * 0.8) for v in gc))
            x += gw + r.randint(4, 28)
    dx = int(w * r.uniform(0.15, 0.75))
    d.rect((dx, int(h * 0.38), dx + int(h * 0.38), h), fill=(18, 14, 22))
    n = max(2, int(aspect * 1.4))
    xs, xk = [], 0.0
    for k in range(n):                       # irregular bays (repetition.guard): the mullion pitch varies by +-40 %
        xk += r.uniform(0.6, 1.4)
        xs.append(xk)
    for xv in xs[:-1]:
        x = int(w * xv / xs[-1])
        d.rect((x - 3, fb, x + 3, h), fill=(20, 16, 26))
    return d.spec()


def sign_spec(s: Dict[str, Any], measure: Measure) -> Dict[str, Any]:
    """The draw list of one planned sign (`plan["signs"][i]`)."""
    t = s["tex"]
    r = random.Random(t["seed"])
    aspect = (s["u1"] - s["u0"]) / max(0.05, s["z1"] - s["z0"])
    st = t["style"]
    if st == "box":
        return box(t["word"], t.get("sub", ""), s["col"], aspect, r, measure)
    if st == "blade":
        return blade(t["word"], t.get("sub", ""), s["col"], aspect, r, measure)
    if st == "wall":
        return wall(t["word"], t.get("sub", ""), s["col"], aspect, r, measure)
    if st == "ad":
        return ad(t["ad"], aspect)
    if st == "holo":
        return holo(t["word"], t.get("sub", ""), s["col"], aspect, r, measure)
    return shop(t["word"], s["col"], aspect, r, measure)


def make(plan: Dict[str, Any], measure: Measure) -> Dict[str, Any]:
    """Draw lists of every sign of a plan, by sign id, plus the megastructure plate (`mega`) when the plan has one."""
    out = {s["id"]: sign_spec(s, measure) for s in plan["signs"]}
    m = plan.get("mega")
    if m:
        out["mega"] = ad(m["tex"]["ad"], 2.4 if m["kind"] == "arch" else 16 / 9)
    return out
