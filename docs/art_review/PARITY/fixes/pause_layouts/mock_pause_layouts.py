"""Pause menu layout mockups: every sticker is baked by the round 33 kit code (ui31.sticker / focus_sticker,
placed by sticker_lib31.place), unchanged, as tools/art/bake_menus_r33.py does. The panel, the code field and the
backdrop blur are Pillow approximations of the game's own."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(r"D:\Godot\rebel_cell\.claude\worktrees\agent-a98bfb9c903aaf206")
TMP = Path(r"C:\Users\noitu\AppData\Local\Temp\pf_pause")
SRC = TMP / "src" / "docs" / "concepts" / "round33_ui_chrome" / "scripts"
OUT = ROOT / "docs" / "art_review" / "PARITY" / "fixes" / "pause_layouts"
FONTS = ROOT / "assets" / "fonts"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT / "tools" / "art"))
import sticker_lib31 as SL  # noqa
import ui31 as U  # noqa
import menu33 as M  # noqa
import bake_menus_r33 as B  # noqa
B.point_fonts(SL, U, M)

HARM_FILL = ("grad", (255, 118, 96), (196, 28, 22))  # the kit's fill tuple with the HARM red (ui31.HARM 255,68,51)
CYAN = (79, 216, 240)
MONO = str(FONTS / "ShareTechMono-Regular.ttf")
_cache = {}


def baked(word, size, fill, seed, focus=False):
    key = (word, size, str(fill), seed, focus)
    if key in _cache:
        return _cache[key]
    sd = U.sticker(word, size, fill, seed=seed)
    if focus:
        sd = U.focus_sticker(sd)
    w, h = sd["img"].size
    cw, ch = int(w / SL.SS) + 240, int(h / SL.SS) + 240
    canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    canvas = SL.place(canvas, sd, cw / 2, ch / 2, angle=0.0, scale=1.0)
    img = canvas.crop(canvas.getbbox())
    vb = img.split()[3].point(lambda v: 255 if v > 200 else 0).getbbox()  # the sticker itself, without its shadow
    _cache[key] = (img, vb)
    return _cache[key]


ROLES = {  # word: (board size, fill, seed)
    "RESUME": (62, U.FILL_PINK, 40),
    "OPTIONS": (40, U.FILL_CALM, 41),
    "CODEX": (40, U.FILL_CALM, 42),
    "SAVE & QUIT": (40, U.FILL_CALM, 43),
    "QUIT TO DESKTOP": (40, U.FILL_CALM, 44),
    "ABANDON RUN": (40, HARM_FILL, 45),
    "ABANDON CAMPAIGN": (40, HARM_FILL, 46),
}


class Frame:
    def __init__(self, bg, ts):
        self.ts = ts  # text scale
        self.im = bg.copy().convert("RGBA")
        self.f = 0.5 * min(ts, 1.5)  # board px -> frame px; stickers scale to 1.5 at most (VerbSticker.SCALE_MAX)

    def font(self, px):
        return ImageFont.truetype(MONO, int(px * self.ts))

    def sticker(self, word, x, y, focus=False, k=1.0, angle=0.0):
        size, fill, seed = ROLES[word]
        img, vb = baked(word, size, fill, seed, focus)
        w, h = img.size
        s = self.f * k
        img = img.resize((max(2, int(w * s)), max(2, int(h * s))), Image.LANCZOS)
        vis = (int((vb[2] - vb[0]) * s), int((vb[3] - vb[1]) * s))
        off = (int(vb[0] * s), int(vb[1] * s))
        if angle:
            img = img.rotate(angle, Image.BICUBIC, expand=True)
            off = (off[0] + (img.size[0] - int(w * s)) // 2, off[1] + (img.size[1] - int(h * s)) // 2)
        self.im.alpha_composite(img, (int(x) - off[0], int(y) - off[1]))
        return vis

    def panel(self, x, y, w, h, title="> PAUSED"):
        d = ImageDraw.Draw(self.im, "RGBA")
        d.rectangle((x, y, x + w, y + h), fill=(4, 9, 24, 238), outline=CYAN + (255,), width=2)
        hh = int(34 * self.ts)
        d.rectangle((x + 2, y + 2, x + w - 2, y + hh), fill=(20, 48, 74, 255))
        d.text((x + 14, y + hh / 2), title, font=self.font(15), fill=CYAN, anchor="lm")
        d.rectangle((x + w - 22, y + hh / 2 - 4, x + w - 14, y + hh / 2 + 4), fill=CYAN)
        return y + hh

    def field(self, x, y, w, code, caption="Campaign code (share it: it starts this campaign)"):
        d = ImageDraw.Draw(self.im, "RGBA")
        d.text((x, y), caption, font=self.font(11), fill=(175, 192, 214), anchor="la")
        y2 = y + int(17 * self.ts)
        h = int(25 * self.ts)
        d.rectangle((x, y2, x + w - h - 8, y2 + h), fill=(6, 12, 30, 255), outline=(60, 150, 175, 255))
        px = 15
        while px > 8 and d.textlength(code, font=self.font(px)) > w - h - 30:
            px -= 1  # the real field widens to the whole code; the mockup shrinks the type instead
        d.text((x + 8, y2 + h / 2), code, font=self.font(px), fill=(125, 135, 150), anchor="lm")
        bx = x + w - h - 2
        d.rectangle((bx, y2, bx + h + 2, y2 + h), fill=(6, 12, 30, 255), outline=CYAN + (255,), width=2)
        c = int(h * 0.3)
        cx, cy = bx + (h + 2) / 2, y2 + h / 2
        d.rectangle((cx - c + 3, cy - c + 3, cx + c + 3, cy + c + 3), outline=(235, 245, 255), width=2)
        d.rectangle((cx - c - 3, cy - c - 3, cx + c - 3, cy + c - 3), fill=(6, 12, 30, 255), outline=(235, 245, 255), width=2)
        return y2 + h

    def text(self, x, y, s, px=13, col=(175, 192, 214), anchor="la"):
        ImageDraw.Draw(self.im, "RGBA").text((x, y), s, font=self.font(px), fill=col, anchor=anchor)

    def rule(self, x, y, w, col):
        ImageDraw.Draw(self.im, "RGBA").line((x, y, x + w, y), fill=col, width=1)


def backdrop(path):
    im = Image.open(path).convert("RGB").resize((1280, 720), Image.LANCZOS)
    im = im.filter(ImageFilter.GaussianBlur(6))
    tint = Image.new("RGB", im.size, (2, 3, 10))
    return Image.blend(im, tint, 0.55)


def tag(f, x, y, s, col):
    d = ImageDraw.Draw(f.im, "RGBA")
    ft = f.font(11)
    w = d.textlength(s, font=ft) + 12
    d.rectangle((x, y, x + w, y + int(17 * f.ts)), outline=col + (255,), width=1)
    d.text((x + 6, y + int(8.5 * f.ts)), s, font=ft, fill=col, anchor="lm")


def abandon_word(ctx):
    return "ABANDON CAMPAIGN" if ctx == "hq" else "ABANDON RUN"


def hint(f, x, y):
    f.text(x, y, "[Esc]", 16, (255, 190, 226), "lm")


CODE = "RC1-solace-0-7-home_standard-breaker"


# ---- Option A: one stack (reading order = priority), the harm row set apart under a red rule -----------------
def opt_a(bg, ctx, ts=1.0, focus="RESUME"):
    f = Frame(bg, ts)
    W = int(560 * ts) if ts <= 1 else 760
    H = 440 if ts <= 1 else 640
    x0 = (1280 - W) // 2
    y0 = (720 - H) // 2
    top = f.panel(x0, y0, W, H)
    y = top + int(16 * ts)
    gap = int(10 * ts)
    sz = f.sticker("RESUME", x0 + 22, y, focus == "RESUME", angle=1.5)
    hint(f, x0 + 22 + sz[0] + 10, y + sz[1] / 2)
    y += sz[1] + gap
    for w in ["OPTIONS", "CODEX", "SAVE & QUIT", "QUIT TO DESKTOP"]:
        sz = f.sticker(w, x0 + 26, y, focus == w, angle=-1.0)
        y += sz[1] + gap // 2
    y += gap
    f.rule(x0 + 20, y, W - 40, (255, 68, 51, 140))
    y += gap
    tag(f, x0 + 22, y, "CANNOT UNDO", (255, 68, 51))
    y += int(24 * ts)
    sz = f.sticker(abandon_word(ctx), x0 + 22, y, focus == "ABANDON", angle=1.0)
    y += sz[1] + gap
    f.field(x0 + 22, y, W - 44, CODE)
    return f.im


# ---- Option B: Resume across the top, a 2x2 grid of calm stickers, a harm strip with the code beside it ------
def opt_b(bg, ctx, ts=1.0, focus="RESUME"):
    f = Frame(bg, ts)
    W = int(700 * min(ts, 1.45)) if ts <= 1 else 1000
    H = 330 if ts <= 1 else 560
    x0 = (1280 - W) // 2
    y0 = (720 - H) // 2
    top = f.panel(x0, y0, W, H)
    pad = int(22 * ts)
    y = top + int(14 * ts)
    sz = f.sticker("RESUME", x0 + pad, y, focus == "RESUME", angle=1.0)
    hint(f, x0 + pad + sz[0] + 10, y + sz[1] / 2)
    y += sz[1] + int(10 * ts)
    f.rule(x0 + pad, y, W - 2 * pad, (79, 216, 240, 90))
    y += int(10 * ts)
    colw = (W - 2 * pad) // 2
    rows = [("OPTIONS", "QUIT TO DESKTOP"), ("CODEX", "SAVE & QUIT")]
    for a, b in rows:
        s1 = f.sticker(a, x0 + pad + 4, y, focus == a, angle=-0.8)
        s2 = f.sticker(b, x0 + pad + colw + 4, y, focus == b, angle=0.8)
        y += max(s1[1], s2[1]) + int(8 * ts)
    y += int(6 * ts)
    f.rule(x0 + pad, y, W - 2 * pad, (255, 68, 51, 140))
    y += int(10 * ts)
    tag(f, x0 + pad, y, "CANNOT UNDO", (255, 68, 51))
    y += int(24 * ts)
    sz = f.sticker(abandon_word(ctx), x0 + pad, y, focus == "ABANDON", angle=0.8)
    f.field(x0 + pad + sz[0] + int(30 * ts), y + sz[1] - int(44 * ts), W - 2 * pad - sz[0] - int(30 * ts), CODE)
    return f.im


# ---- Option C: dock, Resume big on the left with the code under it, the other stickers in a right-hand column -----
def opt_c(bg, ctx, ts=1.0, focus="RESUME"):
    f = Frame(bg, ts)
    W = int(740 * min(ts, 1.45)) if ts <= 1 else 1040
    H = 330 if ts <= 1 else 560
    x0 = (1280 - W) // 2
    y0 = (720 - H) // 2
    top = f.panel(x0, y0, W, H)
    pad = int(24 * ts)
    lw = int(W * 0.46)
    y = top + int(30 * ts)
    sz = f.sticker("RESUME", x0 + pad, y, focus == "RESUME", k=1.45, angle=-1.5)
    hint(f, x0 + pad + 8, y + sz[1] + int(14 * ts))
    f.text(x0 + pad + int(60 * ts), y + sz[1] + int(14 * ts), "resume the game", 13, anchor="lm")
    f.field(x0 + pad, y0 + H - int(56 * ts) - 8, lw - pad, CODE, "Campaign code (copy to share)")
    # vertical divider
    f.rule(x0 + lw, y0 + top - y0 + 6, 0, (79, 216, 240, 0))
    d = ImageDraw.Draw(f.im, "RGBA")
    d.line((x0 + lw + 6, top + 12, x0 + lw + 6, y0 + H - 14), fill=(79, 216, 240, 80), width=1)
    x = x0 + lw + pad
    y = top + int(16 * ts)
    for w in ["OPTIONS", "CODEX", "SAVE & QUIT", "QUIT TO DESKTOP"]:
        sz = f.sticker(w, x, y, focus == w, angle=-0.8 if w in ("OPTIONS", "SAVE & QUIT") else 0.8)
        y += sz[1] + int(5 * ts)
    y += int(8 * ts)
    f.rule(x, y, W - lw - 2 * pad, (255, 68, 51, 140))
    y += int(8 * ts)
    tag(f, x, y, "CANNOT UNDO", (255, 68, 51))
    y += int(24 * ts)
    f.sticker(abandon_word(ctx), x, y, focus == "ABANDON", angle=0.6)
    return f.im


def banner(im, s):
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((0, 0, 1280, 22), fill=(0, 0, 0, 170))
    d.text((8, 11), s, font=ImageFont.truetype(MONO, 14), fill=(230, 230, 230), anchor="lm")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bgs = {"hq": backdrop(TMP / "c1" / "hq.png"), "fight": backdrop(TMP / "c1" / "combat_start.png")}
    spec = [("A_stack", opt_a, "RESUME"), ("B_grid", opt_b, "OPTIONS"), ("C_dock", opt_c, "CODEX")]
    for name, fn, foc in spec:
        for ctx in ("hq", "fight"):
            im = fn(bgs[ctx], ctx, 1.0, foc)
            banner(im, "option %s, %s (%s); focus on %s; stickers = kit code" % (name, "HQ" if ctx == "hq" else "in a run",
                   "ABANDON CAMPAIGN" if ctx == "hq" else "ABANDON RUN", foc.title()))
            im.convert("RGB").save(OUT / ("opt%s_%s.png" % (name, ctx)))
    fav = opt_b(bgs["hq"], "hq", 2.0, "RESUME")
    banner(fav, "option B_grid at text scale 2.0 (stickers cap at 1.5x, as VerbSticker.SCALE_MAX), HQ")
    fav.convert("RGB").save(OUT / "optB_grid_hq_text2.0.png")
    fav = opt_b(bgs["fight"], "fight", 2.0, "RESUME")
    banner(fav, "option B_grid at text scale 2.0, in a run")
    fav.convert("RGB").save(OUT / "optB_grid_fight_text2.0.png")


main()
