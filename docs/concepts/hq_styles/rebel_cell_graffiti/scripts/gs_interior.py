"""Graffiti MAINFRAME shop interior: runs the round-34 shop_v5 layout (imported, never edited) with run-time patches.

python gs_interior.py <exterior.png> <out.png>
Patches: the backdrop (graffiti wall + the red-sign exterior), pegboard frame, marker-tagged kraft price tags, spray-stencilled
section labels, a sticker-bombed clerk-screen bezel, extra slaps on the board edge, the LEAVE sticker as a peeling slap.
All round-34 scratch (tiles, wheel) is rebuilt under D:/rc_scratch, nothing is written into the repo.
"""
import math
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
CON = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
R34 = os.path.join(CON, "round34_firmware_daemons", "scripts")
S = r"D:/rc_scratch/hq_styles/rebel_cell_graffiti"
sys.path.insert(0, R34)
sys.path.insert(1, os.path.join(CON, "street_graffiti", "scripts"))
EXT, OUTP = sys.argv[1], sys.argv[2]

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

import sticker_lib19 as _SL
_FD = os.path.normpath(os.path.join(CON, "..", "..", "assets", "fonts"))     # the module hard-codes a stale C: worktree path
_SL.FONT_DIR = _FD
_SL.ANTON, _SL.MARKER = _FD + "/Anton-Regular.ttf", _FD + "/PermanentMarker-Regular.ttf"
_SL.PLEX, _SL.MONO = _FD + "/IBMPlexSansCondensed-Medium.ttf", _FD + "/ShareTechMono-Regular.ttf"
import r31lib as L
L.SCRATCH = S + "/r34"
L.ASSETS = S + "/r34/assets"
L.OUT = S + "/r34out"
for d in (L.SCRATCH, L.ASSETS, L.OUT):
    os.makedirs(d, exist_ok=True)
import fwlib as F          # noqa: E402
import assets as A         # noqa: E402
A.CACHE = L.ASSETS
import shop as S1          # noqa: E402
import shop2 as S2         # noqa: E402
import shop_layout as SL3  # noqa: E402
import shop_v5 as V5       # noqa: E402
import graf_atlas as GA    # noqa: E402

_STALE = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass" + r"\assets\fonts"


def _fix_defaults():
    """round-34 modules bind font paths from a stale C: worktree as default arguments: rebind them to this checkout."""
    import types
    for mod in list(sys.modules.values()):
        if mod is None or not getattr(mod, "__file__", None) or not os.path.abspath(mod.__file__).startswith(os.path.abspath(R34)):
            continue
        fns = []
        for o in vars(mod).values():
            if isinstance(o, type):
                fns += list(vars(o).values())
            else:
                fns.append(o)
        for fn in fns:
            if isinstance(fn, types.FunctionType):
                if fn.__defaults__:
                    fn.__defaults__ = tuple(d.replace(_STALE, _FD) if isinstance(d, str) else d for d in fn.__defaults__)
                if fn.__kwdefaults__:
                    fn.__kwdefaults__ = {k: (v.replace(_STALE, _FD) if isinstance(v, str) else v) for k, v in fn.__kwdefaults__.items()}


_fix_defaults()
FLUO = GA.FLUO
FW ="C:/Windows/Fonts/"
rngm = random.Random(11)


# ------------------------------------------------------------------ backdrop: the red-sign exterior + a bombed wall behind the board
def wall_bg():
    ext = Image.open(EXT).convert("RGB").resize((1920, 1080), Image.LANCZOS)
    ext = ext.filter(ImageFilter.GaussianBlur(2.2))
    a = np.asarray(ext, np.float32) / 255
    a = a * 0.62
    # the bombed wall: a crop of the graffiti atlas over concrete, dimmed, washed pink / cyan
    atl = Image.open(S + "/tex/graf_albedo.png").convert("RGBA")
    W, H = 1500, 1080
    crop = atl.crop((700, 300, 700 + W, 300 + H))
    base = Image.new("RGBA", (W, H), (46, 40, 52, 255))
    nz = np.random.default_rng(4).normal(0, 6, (H, W, 1))
    bb = np.asarray(base, np.float32)
    bb[..., :3] += nz
    base = Image.fromarray(np.clip(bb, 0, 255).astype(np.uint8), "RGBA")
    # brick courses
    d = ImageDraw.Draw(base)
    for y in range(0, H, 36):
        d.line([(0, y), (W, y)], fill=(30, 26, 36, 255), width=2)
        for x in range((y // 36 % 2) * 40, W, 80):
            d.line([(x, y), (x, y + 36)], fill=(30, 26, 36, 255), width=2)
    base.alpha_composite(crop)
    wallim = np.asarray(base.convert("RGB").filter(ImageFilter.GaussianBlur(2.2)), np.float32) / 255 * 0.34
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    pink = np.exp(-((xx / 700.0) ** 2 + ((yy - 300) / 600.0) ** 2))[..., None] * np.array([0.22, 0.03, 0.12], np.float32)
    cyan = np.exp(-(((xx - W) / 600.0) ** 2 + ((yy - H) / 500.0) ** 2))[..., None] * np.array([0.02, 0.12, 0.16], np.float32)
    wallim = wallim + pink + cyan
    x0 = 1920 - W
    m = np.clip((xx - 0) / 60.0, 0, 1)[..., None]       # soft left edge into the exterior
    a[:, x0:] = a[:, x0:] * (1 - m) + wallim * m
    # steel mullion between the street view and the bombed wall, with slaps on it
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle([x0 - 6, 0, x0 + 14, 1080], fill=(18, 18, 24, 255))
    return L.vignette(im, 0.5)


def stencil_text(text, size, col, seed):
    """Spray stencil lettering: heavy font, bridge gaps, overspray halo, dark under-edge, a drip or two."""
    rg = random.Random(seed)
    f = L.font(L.ANTON, size)
    tw = int(f.getlength(text)) + 40
    th = int(size * 1.5)
    m = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(m).text((20, size * 0.12), text, font=f, fill=255)
    br = Image.new("L", (tw, th), 0)
    bd = ImageDraw.Draw(br)
    x = 20
    for ch in text:
        cw = f.getlength(ch)
        if ch != " ":
            ym = size * 0.12 + size * 0.50
            bd.line([(x + cw * 0.02, ym), (x + cw * 0.30, ym)], fill=255, width=3)      # stencil bridge on the left stem
            bd.line([(x + cw * 0.72, ym + size * 0.16), (x + cw * 0.98, ym + size * 0.16)], fill=255, width=3)
        x += cw
    st = ImageChops.subtract(m, br)
    # spray noise on the edge
    nz = Image.fromarray((np.random.default_rng(seed).random((th, tw)) * 255).astype(np.uint8))
    halo = st.filter(ImageFilter.GaussianBlur(size * 0.09)).point(lambda v: int(v * 0.5))
    edge = ImageChops.multiply(st.filter(ImageFilter.GaussianBlur(1.2)), nz.point(lambda v: 255 if v > 40 else 150))
    im = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    sh = Image.new("RGBA", (tw, th), (8, 6, 12, 0))
    sh.putalpha(ImageChops.offset(st, 2, 3).filter(ImageFilter.GaussianBlur(1.5)))
    im.alpha_composite(sh)
    ha = Image.new("RGBA", (tw, th), col + (0,))
    ha.putalpha(halo)
    im.alpha_composite(ha)
    fl = Image.new("RGBA", (tw, th), col + (0,))
    fl.putalpha(edge)
    im.alpha_composite(fl)
    # drips
    a = np.asarray(st) > 0
    d = ImageDraw.Draw(im)
    for _ in range(max(2, len(text) // 3)):
        c = rg.randrange(20, tw - 20)
        ys = np.nonzero(a[:, c])[0]
        if len(ys):
            y = ys.max()
            L_ = rg.uniform(6, size * 0.45)
            d.line([(c, y), (c, y + L_)], fill=col + (235,), width=max(2, size // 16))
            d.ellipse([c - 2, y + L_ - 2, c + 2, y + L_ + 2], fill=col + (235,))
    return im


_SEC_COL = {"CARDS": (255, 61, 168), "FIRMWARE": (176, 255, 40), "DAEMONS": (92, 225, 255), "RECYCLE BIN": (255, 226, 0)}
_orig_dymo = S1.dymo


def dymo_stencil(text, size=26):
    if size < 24:
        return _orig_dymo(text, size)
    col = _SEC_COL.get(text, (240, 240, 245))
    big = stencil_text(text, int(size * 1.15), col, sum(map(ord, text)))
    # a dark spray-shadow panel so the label reads on any wall (ink slab, ragged)
    pad = Image.new("RGBA", (big.width + 16, big.height + 6), (0, 0, 0, 0))
    pm = Image.new("L", pad.size, 0)
    ImageDraw.Draw(pm).rounded_rectangle([2, 4, pad.width - 3, pad.height - 3], radius=6, fill=170)
    pad.putalpha(pm.filter(ImageFilter.GaussianBlur(3)))
    pad.alpha_composite(big, (8, 0))
    return pad


S1.dymo = dymo_stencil


# ------------------------------------------------------------------ marker-tagged kraft price tags
_orig_tag_on = S1.tag_on
_orig_price_tag = L.price_tag


def marker_price_tag(price, w=96, h=46, sold=False, afford=True, seed=3):
    t = _orig_price_tag(price, w=w, h=h, sold=sold, afford=afford, seed=seed)
    rg = random.Random(seed * 7 + 1)
    d = ImageDraw.Draw(t)
    W_, H_ = t.size
    ink = (14, 12, 18, 235)
    # marker underline under the price, a quick star, and a tag signature in the hole end, all below / left of the digits
    y = H_ - max(7, H_ // 5)
    pts = [(W_ * 0.30 + i * (W_ * 0.62) / 6, y + math.sin(i * 1.7 + seed) * 1.6) for i in range(7)]
    d.line(pts, fill=ink, width=max(3, H_ // 10))
    sx, sy = W_ * 0.17, H_ * 0.28
    r_ = H_ * 0.12
    for k in range(5):
        a0 = k * 2 * math.pi * 2 / 5 - math.pi / 2
        a1 = (k + 1) * 2 * math.pi * 2 / 5 - math.pi / 2
        d.line([(sx + r_ * math.cos(a0), sy + r_ * math.sin(a0)), (sx + r_ * math.cos(a1), sy + r_ * math.sin(a1))], fill=ink, width=1)
    sig = rg.choice(["kz", "vex", "oni", "NYX", "zer0", "hex", "ume"])
    f = ImageFont.truetype(rg.choice(GA.F_TAG), max(9, H_ // 4))
    d.text((W_ * 0.86, H_ * 0.08), sig, font=f, fill=ink if not sold else (200, 30, 40, 235))
    if rg.random() < 0.5:
        d.line([(W_ * 0.93, H_ * 0.06), (W_ * 0.93, H_ * 0.06 + 6)], fill=ink, width=1)
    return t


L.price_tag = marker_price_tag


# ------------------------------------------------------------------ sticker kit for slaps
def slap_art(text, bg, fg, w, h, font_path=None, seed=0):
    rg = random.Random(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([2, 2, w - 3, h - 3], radius=rg.choice([4, 10, 16]), fill=bg + (255,))
    d.rounded_rectangle([7, 7, w - 8, h - 8], radius=6, outline=fg + (255,), width=2)
    if any(ord(c) > 0xAC00 and ord(c) < 0xD7A4 for c in text):
        fp = FW + "malgunbd.ttf"
    elif any(ord(c) > 127 for c in text):
        fp = GA.F_JP
    else:
        fp = font_path or rg.choice([GA.F_HEAVY[0], GA.F_HEAVY[1]])
    fs = int(h * 0.55)
    f = ImageFont.truetype(fp, fs)
    while d.textlength(text, font=f) > w - 24 and fs > 8:
        fs -= 2
        f = ImageFont.truetype(fp, fs)
    bb = d.textbbox((0, 0), text, font=f)
    d.text(((w - (bb[2] - bb[0])) / 2 - bb[0], (h - (bb[3] - bb[1])) / 2 - bb[1]), text, font=f, fill=fg + (255,))
    return im


SLAPS = [("NO CORP", (255, 61, 168), (20, 18, 24)), ("反乱", (212, 255, 0), (20, 18, 24)), ("FREE NET", (20, 18, 24), (92, 225, 255)),
         ("해킹", (255, 226, 0), (20, 18, 24)), ("ZERO", (250, 250, 245), (255, 40, 90)), ("ネット", (176, 77, 255), (250, 250, 245)),
         ("駭客", (255, 140, 26), (20, 18, 24)), ("GHOST", (20, 18, 24), (212, 255, 0)), ("JACK IN", (92, 225, 255), (20, 18, 24)),
         ("REBEL", (255, 40, 90), (250, 250, 245)), ("電脳", (60, 255, 170), (20, 18, 24)), ("VANDAL", (250, 250, 245), (20, 18, 24))]
_slap_cache = {}


def put_slap(img, i, cx, cy, ang, scale=1.0, w=96, h=60):
    key = (i, w, h)
    if key not in _slap_cache:
        t, bg, fg = SLAPS[i % len(SLAPS)]
        _slap_cache[key] = L.sticker_from_art(slap_art(t, bg, fg, w, h, seed=i), border=4, seed=i)
    return L.place_sticker(img, _slap_cache[key], cx, cy, angle=ang, scale=scale)


def tag_layer(img, text, x, y, size, col, ang=0.0, seed=1):
    rg = random.Random(seed)
    f = ImageFont.truetype(rg.choice(GA.F_TAG), size)
    bb = f.getbbox(text)
    m = Image.new("L", (bb[2] - bb[0] + size, bb[3] - bb[1] + size * 2), 0)
    d = ImageDraw.Draw(m)
    d.text((size // 2 - bb[0], size // 2 - bb[1]), text, font=f, fill=255, stroke_width=max(1, size // 22), stroke_fill=255)
    pts = [(size * 0.3 + i * (m.width - size * 0.6) / 8, size // 2 + bb[3] - bb[1] + size * 0.15 + math.sin(i * 0.9) * size * 0.08) for i in range(9)]
    d.line(pts, fill=255, width=max(2, size // 14))
    m = ImageChops.lighter(m, GA.drips(m, rg, 3, size * 0.7, max(2, size // 18)))
    m = m.rotate(ang, resample=Image.BICUBIC, expand=True)
    lay = Image.new("RGBA", m.size, col + (0,))
    lay.putalpha(m)
    img.alpha_composite(lay, (int(x), int(y)))
    return img


# ------------------------------------------------------------------ patches into the round-34 layout
S2.facade = wall_bg
_orig_peg = S1.pegboard


def peg_graf(w, h):
    im = _orig_peg(w, h)
    # overspray on the frame: dark ink + a faint fluoro haze at the top-left and bottom-right corners (UI area stays clean)
    d = ImageDraw.Draw(im)
    for (x, y, c) in ((0, 0, (255, 61, 168)), (w, h, (92, 225, 255))):
        haze = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(haze).ellipse([x - 90, y - 70, x + 90, y + 70], fill=c + (50,))
        im.alpha_composite(haze.filter(ImageFilter.GaussianBlur(26)))
    return im


S1.pegboard = peg_graf


def bomb_clerk(img):
    X0, Y0, X1, Y1 = 60, 728, 480, 1058
    # big marker tag across the lower-left corner (outside the screen) and sticker bombing along the bezel
    pass
    img = tag_layer(img, "kz", 330, 612, 56, (212, 255, 0), 8, 6)
    spots = [(X0 + 4, Y0 + 80, -12, 0), (X0 + 6, Y1 - 60, -6, 2), (X0 + 260, Y1 - 2, -9, 4), (X1 - 2, Y0 + 200, -8, 6), (X0 - 6, Y0 - 12, 14, 9),
             (X1 + 8, Y0 + 20, -12, 10), (X0 + 400, Y1 + 4, 7, 11)]
    for (x, y, a, i) in spots:
        img = put_slap(img, i, x, y, a, 0.5, 100, 62)
    return img


def board_edge(img):
    spots = [(500, 250, -10, 0), (900, 86, -8, 3), (1560, 300, 9, 5), (1582, 60, -6, 6), (1500, 696, 6, 9)]
    for (x, y, a, i) in spots:
        img = put_slap(img, i, x, y, a, 0.5, 100, 62)
    return img


def wall_art(img):
    """Pieces and tags painted on the wall beside the board (right column above the bin, top strip, left of the clerk)."""
    rg = random.Random(21)
    big, g = GA.piece(rg, 140, 0.5)
    k = 330 / big.width
    big = big.resize((330, int(big.height * k)), Image.LANCZOS)
    img.alpha_composite(big, (1572, 150))
    big2, _ = GA.piece(rg, 120, 0.3)
    k = 300 / big2.width
    big2 = big2.resize((300, int(big2.height * k)), Image.LANCZOS)
    for (t, x, y, sz, c, a) in (("rebel", 1640, 40, 54, (255, 226, 0), 4), ("ghost", 1590, 470, 44, (92, 225, 255), -5), ("oni", 40, 600, 42, (212, 255, 0), 6),
                                ("VEX", 1796, 880, 54, (255, 61, 168), 8)):
        img = tag_layer(img, t, x, y, sz, c, a, sz)
    tj, _ = GA.jp_tag(rg, 70)
    img.alpha_composite(tj, (1700, 450))
    return img


_orig_place_leave = S2.place_leave


def leave_slap(img, wiggle=0.0):
    """LEAVE as a hard slap: tilted harder, a curl peeling at the corner, a spray tag over its edge, impact ticks."""
    lv, ar, tg = S2.leave_sticker()
    img = L.place_sticker(img, ar, 1790 + wiggle * 8, 985, angle=-4, scale=0.7)
    img = L.place_sticker(img, lv, 1580, 985, angle=-9, scale=0.88)
    img = L.place_sticker(img, tg, 1610, 1045, angle=4, scale=0.95)
    d = ImageDraw.Draw(img)
    # impact ticks around the slap
    for k in range(9):
        a = math.radians(-165 + k * 20)
        d.line([(1580 + 200 * math.cos(a), 985 + 112 * math.sin(a)), (1580 + 232 * math.cos(a), 985 + 130 * math.sin(a))], fill=(255, 226, 0, 255), width=4)
    # peeling corner: a curled triangle at the lower-right of the sticker
    peel = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
    pd = ImageDraw.Draw(peel)
    pd.polygon([(0, 60), (60, 60), (60, 0)], fill=(240, 238, 246, 255))
    pd.polygon([(8, 60), (60, 60), (60, 8)], fill=(200, 196, 214, 255))
    peel = L.rotate_rgba(peel, -9)
    img = L.drop_shadow(img, peel, 1700, 1010, blur=3, off=(2, 3), op=0.6)
    img = tag_layer(img, "kz", 1360, 905, 44, (255, 61, 168), -12, 9)
    return img


S2.place_leave = leave_slap


def main():
    SL3.POINTER = False
    SL3.CENTRE_TH = 0.0
    SL3.PRICE[0] = 80
    A.shop_wheel12()
    img = SL3.compose()
    img = V5.firmware_row(img)
    img = V5.daemon_row(img)
    p = L.pen(L.GP_YELLOW, seed=88)
    p.text("pins in the foam", 1468, 128, 22, angle=-3)
    img = L.ink(img, p)
    img = wall_art(img)
    img = bomb_clerk(img)
    img = board_edge(img)
    img = L.bloom(img, 0.2, 0.8, 8)
    img.convert("RGB").save(OUTP)
    print("wrote", OUTP)


if __name__ == "__main__":
    main()
