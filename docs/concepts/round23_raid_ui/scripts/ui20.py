"""Round 20 UI layer: crop-aware grease pencil (draw-on + WIPE), threat routes back in red pencil, Halcyon threat
sprites, tracers / floats, health hover floats, and the five panel-medium options (panel_mediums_v2).

Coordinates are always 1920 x 1080 frame px; a `Frame` carries the crop origin so the same drawing code serves
the full frames and the gif crops.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as LY  # noqa: E402
import ui19 as U  # noqa: E402
from ui19 import T, SL, F, S  # noqa: E402,F401
from ui19 import PINK, CYAN, GREEN, VIOLET, AMBER, LIME, HARM, HALCYON, PAPER, INKC, ICE, Y_PEN, R_PEN  # noqa: E402,F401
import netdecal19 as N19  # noqa: E402

ROOT = os.path.dirname(HERE)
BL = os.path.join(ROOT, "scratch", "bl")


def P(x, y, z=0.0):
    p = LY.project(x, y, z)
    return p[0], p[1]


class Frame:
    """An image (float RGB) that is the crop `box` of the 1920 x 1080 frame (box None = full frame)."""

    def __init__(self, img, box=None):
        self.img = img
        self.box = box or (0, 0, LY.W, LY.H)
        self.ox, self.oy = self.box[0], self.box[1]
        self.w, self.h = img.shape[1], img.shape[0]


# ------------------------------------------------------------------ grease pencil on a crop, draw-on and wipe
class Pencil:
    def __init__(self, fr, seed=7):
        self.fr = fr
        self.rng = np.random.default_rng(seed)
        self.L = T.Layer(self.rng, fr.ox, fr.oy, fr.w, fr.h)
        self.items = []     # (strokes, kind) kept so progress can cut them

    def strokes(self, st, progress=1.0):
        if progress <= 0:
            return
        if progress < 1:
            st = T.cut_strokes(st, progress)
        for s_ in st:
            if len(s_[0]) >= 2:
                self.L.wax_stroke(s_[0], s_[1], s_[2])

    def arrow(self, pts, col=R_PEN, w=6.0, head=20, dashed=False, progress=1.0, amp=1.4, dash=22, gap=14):
        path = U.jitter_path(pts, self.rng, amp, 4)
        st = T.arrow_strokes(path, w, col, self.rng, head=head, dashed=dashed, dash=dash, gap=gap)
        if dashed and progress < 1:   # dashes: reveal in order, then the head
            n = max(0, int(round(len(st) * progress)))
            st = st[:n]
            progress = 1.0
        self.strokes(st, progress)

    def line(self, pts, col=R_PEN, w=6.0, progress=1.0, dashed=False, amp=1.4):
        path = U.jitter_path(pts, self.rng, amp, 4)
        if dashed:
            st = T.arrow_strokes(path, w, col, self.rng, head=0, dashed=True, dash=22, gap=14)[:-2]
            n = int(round(len(st) * progress))
            self.strokes(st[:n])
        else:
            self.strokes([(path, w, col)], progress)

    def circle(self, x, y, rx, ry, col=R_PEN, w=6.0, progress=1.0, turns=1.12):
        self.strokes([(T.hand_circle(x, y, rx, ry, self.rng, turns=turns), w, col)], progress)

    def text(self, s, x, y, cap, col=R_PEN, w=4.4, progress=1.0, angle=-0.03):
        self.strokes(T.letter_strokes(s, x, y, cap, w, col, self.rng, angle=angle), progress)

    def x(self, x, y, r, col=R_PEN, w=6.5, progress=1.0):
        st = [(np.array([(x - r, y - r * 0.85), (x + r, y + r * 0.8)]), w, col),
              (np.array([(x + r, y - r * 0.85), (x - r * 0.95, y + r * 0.9)]), w, col)]
        self.strokes(st, progress)

    def composite(self, wipe=0.0, wipe_dir=(1.0, 0.35)):
        """Lay the wax on the frame. wipe 0..1: a cloth wipe sweeps across (left->right), leaving a faint smear."""
        L = self.L
        L.light()
        rgb, a = L.down()
        if wipe > 0:
            h, w = a.shape
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            ys, xs = np.nonzero(a > 0.02)
            if len(xs):
                u = (xx * wipe_dir[0] + yy * wipe_dir[1])
                u0, u1 = (xs * wipe_dir[0] + ys * wipe_dir[1]).min() - 20, (xs * wipe_dir[0] + ys * wipe_dir[1]).max() + 20
                front = u0 + (u1 - u0) * wipe
                gone = np.clip((front - u) / 18.0, 0, 1)
                smear = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5)),
                                   np.float32) / 255.0
                smear = np.roll(smear, 6, 1) * 0.16 * gone * (1 - wipe ** 3)
                keep = 1 - gone
                rgb = rgb * keep[..., None]
                a = a * keep
                rgb = rgb + np.array(R_PEN, np.float32) * smear[..., None] * 0.9
                a = np.clip(a + smear * (1 - a), 0, 1)
        base = self.fr.img
        out = base.copy()
        dk = U.T.blur(np.minimum(1, a * 2.5), 16)
        out *= (1 - 0.24 * dk)[..., None]
        sh = np.roll(np.roll(U.T.blur(a, 3.0), 6, 0), 4, 1)
        out *= (1 - 0.4 * sh)[..., None]
        out = rgb + out * (1 - a[..., None])
        self.fr.img = out
        return self.fr


# ------------------------------------------------------------------ threat routes in red pencil (round 18 style)
def route_screen(rid, pts=None):
    pts = pts or LY.route_points(rid)
    out = []
    for i in range(len(pts) - 1):
        a, b = np.array(pts[i], float), np.array(pts[i + 1], float)
        d = (b - a) / np.linalg.norm(b - a)
        nrm = np.array([-d[1], d[0]])
        off = -5.0
        t0 = N19.PAD_S * 1.0 if i == 0 else 0.0
        t1 = N19.PAD_S * (1.3 if i == len(pts) - 2 else 0.0)
        out.append(a + d * t0 + nrm * off)
        out.append(b - d * t1 + nrm * off)
    return [P(x, y) for x, y in out]


def pencil_routes(pen, routes=("r1", "r2", "r3"), progress=1.0, letters=True, ghost=()):
    for i, rid in enumerate(("r1", "r2", "r3")):
        if rid not in routes:
            continue
        pts = route_screen(rid)
        pen.arrow(pts, R_PEN, 6.0, 20, progress=progress)
        e = LY.pt(LY.ROUTES[rid][0])
        ex, ey = P(*e)
        pen.circle(ex, ey, 44, 29, R_PEN, 6.0, progress=min(1.0, progress * 2))
        if letters and progress >= 1:
            lx, ly = ex + (-60 if ex > 960 else 60), ey - 36
            pen.text("ABC"[i], lx, ly, 30, R_PEN, 5.5)


# ------------------------------------------------------------------ threat sprites (Halcyon, 4 headings)
_SPR = {}
HEADS = {0: 0, 1: 1, 2: 2, 3: 3}


def sprite(unit, head):
    """unit 'INSPECTOR' | 'BAILIFF'; head 0:+x 1:+y 2:-x 3:-y. Returns (RGBA PIL at map scale, glow RGB, anchor)."""
    key = (unit, head)
    if key in _SPR:
        return _SPR[key]
    lay = json.load(open(os.path.join(BL, "veh_layout.json")))
    it = next(d for d in lay["items"] if d["unit"] == unit and d["head"] == head)
    keep = dict(LY.CAM)
    LY.CAM["target"], LY.CAM["ortho"] = (0.0, 0.0, 0.0), lay["ortho"]
    px, py, _ = LY.project(it["x"], it["y"], 0.0)
    LY.CAM.update(keep)
    beauty = Image.open(os.path.join(BL, "veh_beauty.png")).convert("RGBA")
    glow = Image.open(os.path.join(BL, "veh_glow.png")).convert("RGB")
    R = 230
    bx = (int(px - R), int(py - R), int(px + R), int(py + R))
    sb, sg = beauty.crop(bx), glow.crop(bx)
    k = lay["ortho"] / LY.CAM["ortho"]
    n = int(2 * R * k)
    # ink rim: dilated alpha behind the sprite
    a = sb.split()[3]
    rim = a.filter(ImageFilter.MaxFilter(5))
    ink = Image.new("RGBA", sb.size, (12, 8, 22, 0))
    ink.putalpha(rim)
    ink.alpha_composite(sb)
    out = ink.resize((n, n), Image.LANCZOS)
    g = sg.resize((n, n), Image.LANCZOS)
    _SPR[key] = (out, g, (n / 2, n / 2))
    return _SPR[key]


def paste_sprite(fr, unit, head, x, y, tint=None, alpha=1.0, glow=0.8):
    im, g, (ax, ay) = sprite(unit, head)
    sx, sy = P(x, y)
    X0, Y0 = int(sx - ax - fr.ox), int(sy - ay - fr.oy)
    lay = Image.new("RGBA", (fr.w, fr.h), (0, 0, 0, 0))
    if X0 >= fr.w or Y0 >= fr.h or X0 + im.size[0] <= 0 or Y0 + im.size[1] <= 0:
        return fr
    lay.paste(im, (X0, Y0), im)
    a = np.asarray(lay, np.float32) / 255.0
    rgb, al = a[..., :3], a[..., 3:4] * alpha
    if tint is not None:
        rgb = rgb * 0.45 + np.array(tint, np.float32) / 255.0 * 0.55
    img = fr.img * (1 - al) + rgb * al
    gl = Image.new("RGB", (fr.w, fr.h))
    gl.paste(g, (X0, Y0))
    gb = np.asarray(gl.filter(ImageFilter.GaussianBlur(5)), np.float32) / 255.0
    fr.img = img + gb * glow * alpha
    return fr


def path_point(pts, u):
    """Point at fraction u (0..1) along a world polyline, plus heading index."""
    pts = [np.array(p, float) for p in pts]
    seg = [np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)]
    L = sum(seg)
    d = u * L
    for i, sl in enumerate(seg):
        if d <= sl or i == len(seg) - 1:
            t = min(1.0, d / max(sl, 1e-6))
            p = pts[i] + (pts[i + 1] - pts[i]) * t
            v = pts[i + 1] - pts[i]
            head = 0 if abs(v[0]) > abs(v[1]) and v[0] > 0 else 2 if abs(v[0]) > abs(v[1]) else 1 if v[1] > 0 else 3
            return (p[0], p[1]), head
        d -= sl


# ------------------------------------------------------------------ 2D effects on a Frame
def _layer(fr):
    return Image.new("RGBA", (fr.w, fr.h), (0, 0, 0, 0))


def _add(fr, lay, glow=0.7):
    fr.img = U._add_layer(fr.img, lay, glow)
    return fr


def tracer(fr, p0, p1, col=(120, 230, 255), w=3, k=1.0):
    lay = _layer(fr)
    d = ImageDraw.Draw(lay)
    a = (p0[0] - fr.ox, p0[1] - fr.oy)
    b = (p1[0] - fr.ox, p1[1] - fr.oy)
    d.line([a, b], fill=col + (int(255 * k),), width=w)
    d.ellipse([b[0] - 7, b[1] - 7, b[0] + 7, b[1] + 7], fill=(255, 250, 230, int(230 * k)))
    return _add(fr, lay, 0.9)


def shards(fr, x, y, rng, n=24, col=(255, 90, 70), spread=60, size=13, t=1.0):
    lay = _layer(fr)
    d = ImageDraw.Draw(lay)
    f = F(SL.MONO, size)
    for _ in range(n):
        a = rng.uniform(-math.pi * 0.95, -0.05)
        r = rng.uniform(8, spread) * (0.3 + 0.7 * t)
        px, py = x - fr.ox + math.cos(a) * r, y - fr.oy + math.sin(a) * r * 0.8 + 30 * t * t
        d.text((px, py), rng.choice(["0", "1"]), font=f, fill=col + (int(rng.uniform(150, 255) * (1 - t * 0.8)),), anchor="mm")
    return _add(fr, lay, 0.8)


def float_num(fr, x, y, txt, col=(255, 90, 70), size=30, alpha=1.0):
    lay = _layer(fr)
    d = ImageDraw.Draw(lay)
    f = F(SL.ANTON, size)
    X, Y = x - fr.ox, y - fr.oy
    d.text((X + 2, Y + 2), txt, font=f, fill=(0, 0, 0, int(160 * alpha)), anchor="mm")
    d.text((X, Y), txt, font=f, fill=col + (int(255 * alpha),), anchor="mm", stroke_width=1, stroke_fill=(255, 240, 230, int(255 * alpha)))
    return _add(fr, lay, 0.6)


def health_float(fr, key, now, mx, col=(212, 255, 0), alpha=1.0):
    """Hover / always-show: a diegetic numeral floating above the socket's north corner, with a thin holo bar."""
    x, y = P(*LY.NODES[key][:2])
    y -= 64
    lay = _layer(fr)
    d = ImageDraw.Draw(lay)
    X, Y = x - fr.ox, y - fr.oy
    d.line([(X, Y + 18), (X, Y + 44)], fill=col + (int(120 * alpha),), width=1)
    d.text((X, Y), "%d/%d" % (now, mx), font=F(SL.ANTON, 24), fill=col + (int(255 * alpha),), anchor="mm",
           stroke_width=1, stroke_fill=(10, 20, 10, int(200 * alpha)))
    segs = 10
    for i in range(segs):
        on = i < round(now / mx * segs)
        xa = X - 32 + i * 6.6
        d.rectangle([xa, Y + 14, xa + 4.6, Y + 19], fill=col + ((int(230 * alpha),) if on else (int(50 * alpha),)))
    return _add(fr, lay, 0.6)


def place_sticker(fr, sd, x, y, angle=0.0, **kw):
    """Place a sticker at frame coords (x, y) on a cropped Frame."""
    c = U.f2pil(fr.img).convert("RGBA")
    c = SL.place(c, sd, x - fr.ox, y - fr.oy, angle=angle, **kw)
    fr.img = U.pil2f(c)
    return fr


def put_panel(fr, pn, x, y):
    fr.img = U.put_panel(fr.img, pn, x - fr.ox, y - fr.oy)
    return fr


# ------------------------------------------------------------------ PANEL MEDIUMS v2 -----------------------------
# Content per panel (what it IS in the fiction):
#   NODES   = your network's status (the Cell's own system)          -> a computer thing
#   ORDER   = the raid incoming: an intercepted corporate work order -> a corp document
#   INTEL   = threat intel: scanned / decrypted surveillance         -> a sensor readout
#   LOADOUT = your armory: physical defence assets                   -> stickers (static objects), unchanged
GLYPH = {"relay": "picto_all_targets", "firewall": "slice_firewall", "vault": "placeholder_vault", "proxy": "placeholder_spoof",
         "safe": "placeholder_key", "core": "picto_hp"}
OUT_COL = {"holds": GREEN, "disabled": AMBER, "seized": HARM, "home": PINK}
NODE_ROWS = [("relay", "RELAY", "holds", "15/15", "-"), ("firewall", "FIREWALL RELAY", "holds", "30/30", "TURRET + ICE LOCK"),
             ("vault", "VAULT TERMINAL", "disabled", "20/20", "RAILGUN"), ("proxy", "PROXY RELAY", "seized", "15/15", "-"),
             ("safe", "SAFEHOUSE", "holds", "20/20", "SENTRY"), ("core", "CORE (home)", "home", "50/50", "TURRET")]


def rows_nodes():
    rows = []
    for k, nm, st, integ, assets in NODE_ROWS:
        chip = {"holds": "HOLDS", "disabled": "DISABLED", "seized": "SEIZED", "home": "HOME -8"}[st]
        rows.append(("node", GLYPH[k], nm, chip, OUT_COL[st], "INT %s  %s" % (integ, assets)))
    return rows


def rows_order():
    return [("big", "COMPLIANCE SWEEP", (230, 240, 255)), ("t", "HALCYON CIVIC  //  WORK ORDER 50-HC-114", HALCYON), ("sep",),
            ("kv", "TARGET", "SITE 07 (CELL)", (230, 240, 255)), ("kv", "UNITS", "6 IN 1 WAVE", HARM), ("kv", "ENTRY SITES", "3", (230, 240, 255)),
            ("sep",), ("kv", "IF IT RAN NOW: HOME", "50 > 42", PINK), ("kv", "DISABLED / SEIZED", "1 / 1", AMBER)]


def rows_intel():
    return [("t", "6 THREATS  //  STRENGTH +52% (HEAT)", HALCYON),
            ("route", "A", "BAILIFF  +  COURIER", "> weakest node  /  > VAULT (priority)"),
            ("route", "B", "HAULER  +  INSPECTOR", "> weakest node  /  > VAULT (priority)"),
            ("route", "C", "CUSTOMS  +  LANDER", "seals link behind / drops in")]


def _content(rows, w, mode):
    h = U._measure(rows) + 12
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    gd = U._draw_rows(d, rows, 12, 6, w - 24, mode)
    U._paste_glyphs(im, gd, S, mode)
    return im, h


def _finish(im, w, h):
    return im.resize((w, h), Image.LANCZOS)


def crt_bezel(title, rows, w=330, accent=CYAN, seed=1):
    """CRT MONITOR BEZEL: a physical little monitor - plastic bezel, curved glass, power LED, brand plate."""
    inner = U.terminal(title, rows, w=w - 36, accent=accent, seed=seed)["img"]
    iw, ih = inner.size
    W, H = w, ih + 64
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, W * S - 1, H * S - 1], 18 * S, fill=(58, 56, 64, 255), outline=(20, 18, 24, 255), width=2 * S)
    d.rounded_rectangle([6 * S, 6 * S, (W - 6) * S, (H - 6) * S], 14 * S, outline=(92, 90, 98, 255), width=2 * S)
    d.rounded_rectangle([12 * S, 12 * S, (W - 12) * S, (ih + 26) * S], 12 * S, fill=(6, 10, 18, 255))
    sc = inner.resize((iw * S, ih * S), Image.LANCZOS)
    # barrel vignette
    a = np.asarray(sc, np.float32)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]].astype(np.float32)
    v = 1 - 0.35 * (((xx / a.shape[1] - 0.5) * 2) ** 4 + ((yy / a.shape[0] - 0.5) * 2) ** 4)
    a[..., :3] *= v[..., None]
    im.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), (18 * S, 19 * S))
    d = ImageDraw.Draw(im)
    d.text((22 * S, (H - 20) * S), "CELL-OS  //  " + title, font=F(SL.MONO, 11 * S), fill=(150, 146, 158), anchor="lm")
    d.ellipse([(W - 30) * S, (H - 25) * S, (W - 20) * S, (H - 15) * S], fill=(120, 255, 120, 255))
    for k in range(5):
        d.line([((W - 110 + k * 12) * S, (H - 26) * S), ((W - 110 + k * 12) * S, (H - 14) * S)], fill=(36, 34, 40), width=2 * S)
    # glass glare
    g = Image.new("L", im.size, 0)
    ImageDraw.Draw(g).polygon([(14 * S, 14 * S), (W * 0.5 * S, 14 * S), (W * 0.25 * S, (ih + 24) * S), (14 * S, (ih + 24) * S)], fill=26)
    im = Image.composite(Image.new("RGBA", im.size, (255, 255, 255, 255)), im, g)
    return dict(img=_finish(im, W, H), kind="dossier")


def glass_pane(title, rows, w=330, pencil=None, seed=1):
    """TABLET / HUD GLASS PANE: smoked glass with a thin steel edge, white-cyan type; grease pencil may go on it."""
    con, ch = _content(rows, w - 20, "holo")
    W, H = w, ch + 52
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, W * S - 1, H * S - 1], 16 * S, fill=(14, 22, 30, 190), outline=(180, 196, 210, 230), width=2 * S)
    d.rounded_rectangle([4 * S, 4 * S, (W - 4) * S, (H - 4) * S], 13 * S, outline=(60, 74, 90, 255), width=S)
    d.text((16 * S, 22 * S), title, font=F(SL.ANTON, 22 * S), fill=(235, 245, 255), anchor="lm")
    d.ellipse([(W - 24) * S, 16 * S, (W - 14) * S, 26 * S], outline=(160, 180, 200), width=S)
    im.alpha_composite(con, (10 * S, 40 * S))
    a = np.asarray(im, np.float32) / 255.0
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]].astype(np.float32)
    t = xx / a.shape[1] * 0.8 + yy / a.shape[0] * 0.5
    sheen = np.exp(-((t - 0.3) / 0.06) ** 2) * 0.12 * (a[..., 3] > 0)
    a[..., :3] = a[..., :3] * (1 - sheen[..., None]) + sheen[..., None]
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return dict(img=_finish(im, W, H), kind="dossier")


def corp_seal(d, cx, cy, r, sc, cracked=True, col=(140, 123, 255)):
    d.ellipse([(cx - r) * sc, (cy - r) * sc, (cx + r) * sc, (cy + r) * sc], outline=col + (255,), width=int(3 * sc))
    d.ellipse([(cx - r * 0.72) * sc, (cy - r * 0.72) * sc, (cx + r * 0.72) * sc, (cy + r * 0.72) * sc], outline=col + (200,), width=int(2 * sc))
    d.arc([(cx - r * 0.45) * sc, (cy - r * 0.62) * sc, (cx + r * 0.45) * sc, (cy - r * 0.1) * sc], 180, 360, fill=col + (255,), width=int(2 * sc))
    d.rectangle([(cx - r * 0.38) * sc, (cy - r * 0.1) * sc, (cx + r * 0.38) * sc, (cy + r * 0.35) * sc], outline=col + (255,), width=int(2 * sc))
    if cracked:
        pts = [(cx - r * 0.9, cy - r * 0.3), (cx - r * 0.3, cy - r * 0.05), (cx - r * 0.1, cy + r * 0.4), (cx + r * 0.35, cy + r * 0.2), (cx + r * 0.95, cy + r * 0.6)]
        d.line([(x * sc, y * sc) for x, y in pts], fill=(255, 68, 51, 255), width=int(2 * sc))
        d.line([((cx - r * 0.1) * sc, (cy + r * 0.4) * sc), ((cx - r * 0.2) * sc, (cy + r) * sc)], fill=(255, 68, 51, 255), width=int(2 * sc))


def decrypt_window(title, rows, w=330, accent=HALCYON, seal=True, seed=1, exe="DECRYPT_v3"):
    """DECRYPTED TERMINAL WINDOW: OS window chrome around a C-screen, the corp seal cracked by the Cell's decrypt."""
    con, ch = _content(rows, w - 20, "terminal")
    W, H = w, ch + 62
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W * S - 1, H * S - 1], fill=(5, 13, 28, 236), outline=accent + (255,), width=S)
    d.rectangle([0, 0, W * S - 1, 24 * S], fill=(22, 18, 44, 255))
    d.text((8 * S, 12 * S), "%s.exe  //  %s" % (exe, title), font=F(SL.MONO, 12 * S), fill=accent, anchor="lm")
    for k, c in enumerate(((255, 90, 90), (255, 200, 80), (120, 220, 120))):
        d.rectangle([(W - 16 - k * 14) * S, 7 * S, (W - 6 - k * 14) * S, 17 * S], outline=c, width=S)
    d.rectangle([8 * S, 30 * S, (W - 8) * S, 38 * S], outline=(70, 90, 110), width=S)
    d.rectangle([9 * S, 31 * S, (W - 30) * S, 37 * S], fill=accent)
    d.text(((W - 9) * S, 34 * S), "92%", font=F(SL.MONO, 8 * S), fill=(200, 210, 230), anchor="rm")
    im.alpha_composite(con, (10 * S, 44 * S))
    if seal:
        corp_seal(ImageDraw.Draw(im), W - 44, H - 40, 26, S)
    rng = np.random.default_rng(seed)
    a = np.asarray(im, np.float32)
    for _ in range(5):   # glitch slices
        y = int(rng.uniform(30, H - 10) * S)
        hh = int(rng.uniform(2, 5) * S)
        a[y:y + hh] = np.roll(a[y:y + hh], int(rng.uniform(-8, 8) * S), 1)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return dict(img=_finish(im, W, H), kind="terminal")


def memo_glass(title, rows, w=310, seed=1):
    """INTERCEPTED CORP MEMO under glass: Halcyon letterhead printout, redacted lines in the footer, INTERCEPTED stamp."""
    pad_rows = rows + [("sep",), ("t", " ", (0, 0, 0)), ("t", " ", (0, 0, 0)), ("t", " ", (0, 0, 0))]
    d0 = U.dossier(title, pad_rows, w=w, seed=seed, stamp="INTERCEPTED")
    im = d0["img"].copy()
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(seed)
    W, H = im.size
    for k in range(3):   # redacted lines in the footer
        y = H - 88 + k * 16
        x = 36
        while x < W * 0.55:
            ln = rng.uniform(30, 70)
            d.rectangle([x, y, x + ln, y + 8], fill=(16, 14, 18, 255))
            x += ln + rng.uniform(6, 14)
    corp_seal(d, W - 52, 52, 18, 1, cracked=False, col=(110, 90, 200))
    d.text((30, H - 26), "HALCYON CIVIC  //  INTERNAL  //  DO NOT FORWARD", font=F(SL.MONO, 10), fill=(110, 100, 120), anchor="lm")
    return dict(img=im, kind="dossier")


def intel_holo(rows, w=330, col=(170, 150, 255)):
    """Surveillance holo with scanned vehicle silhouettes (the threat sprites, scanlined) in a strip at the bottom."""
    pad_rows = rows + [("sep",), ("t", " ", (0, 0, 0)), ("t", " ", (0, 0, 0)), ("t", " ", (0, 0, 0))]
    pn = U.holo("THREAT INTEL // SCAN", pad_rows, w=w, col=col)
    im = pn["img"].copy()
    hb = U._measure(pad_rows) + 56          # holo body height (the emitter fan sits below)
    for i, unit in enumerate(("BAILIFF", "INSPECTOR", "BAILIFF")):
        sp, _, _ = sprite(unit, [2, 2, 1][i])
        sp = sp.resize((int(sp.size[0] * 0.9), int(sp.size[1] * 0.9)), Image.LANCZOS)
        bb = sp.split()[3].getbbox()
        sp = sp.crop(bb)
        a = np.asarray(sp, np.float32)
        lum = a[..., :3].mean(axis=2, keepdims=True)
        a[..., :3] = np.clip(lum / 255 * 1.4, 0, 1) * np.array(col, np.float32)
        a[::3, :, 3] *= 0.4
        a[..., 3] *= 0.8
        sp = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        x = 24 + i * (w - 48) // 3
        y = hb - 16 - sp.size[1]
        im.alpha_composite(sp, (int(x), int(y)))
        ImageDraw.Draw(im).text((x, hb - 12), ["A1 BAILIFF", "B2 INSPECTOR", "A1 (rear)"][i], font=F(SL.MONO, 10), fill=col + (220,))
    return dict(img=im, kind="holo")


# speed / skip per medium
def speed_ctrl(medium, active="2x", step="07 / 30"):
    if medium in ("terminal", "decrypt", "mixed"):
        return U.speed_terminal(active, step, accent=CYAN if medium != "decrypt" else HALCYON)
    W, H = 430, 54
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    labs = ("1x", "2x", "4x", "SKIP")
    if medium == "holo":
        col = (120, 230, 255)
        x = 10
        for lab in labs:
            bw = 56 if lab != "SKIP" else 74
            on = lab == active
            d.rectangle([x * S, 10 * S, (x + bw) * S, 40 * S], fill=col + ((120,) if on else (30,)), outline=col + (220,), width=S)
            d.text(((x + bw / 2) * S, 25 * S), lab, font=F(SL.ANTON, 18 * S), fill=col + (255,), anchor="mm")
            x += bw + 8
        d.text(((x + 6) * S, 25 * S), "STEP " + step, font=F(SL.MONO, 14 * S), fill=col + (255,), anchor="lm")
        d.rectangle([60 * S, 48 * S, 300 * S, 52 * S], fill=(200, 210, 220, 255))
        return dict(img=im.resize((W, H), Image.LANCZOS), kind="holo")
    if medium == "bezel":      # chunky hardware keys under a little monitor
        d.rounded_rectangle([0, 0, W * S - 1, H * S - 1], 10 * S, fill=(58, 56, 64, 255), outline=(20, 18, 24, 255), width=2 * S)
        x = 10
        for lab in labs:
            bw = 56 if lab != "SKIP" else 74
            on = lab == active
            top = 8 if not on else 12
            d.rounded_rectangle([x * S, (top + 4) * S, (x + bw) * S, (top + 34) * S], 5 * S, fill=(30, 28, 34, 255))
            d.rounded_rectangle([x * S, top * S, (x + bw) * S, (top + 30) * S], 5 * S, fill=(196, 190, 176, 255) if not on else (255, 176, 0, 255))
            d.text(((x + bw / 2) * S, (top + 15) * S), lab, font=F(SL.ANTON, 16 * S), fill=(30, 28, 34), anchor="mm")
            x += bw + 8
        d.rectangle([(x + 4) * S, 14 * S, (x + 100) * S, 40 * S], fill=(6, 10, 18, 255))
        d.text(((x + 52) * S, 27 * S), step, font=F(SL.MONO, 14 * S), fill=(255, 176, 0), anchor="mm")
        return dict(img=im.resize((W, H), Image.LANCZOS), kind="dossier")
    # glass: touch buttons etched on the pane
    d.rounded_rectangle([0, 0, W * S - 1, H * S - 1], 14 * S, fill=(14, 22, 30, 190), outline=(180, 196, 210, 230), width=2 * S)
    x = 12
    for lab in labs:
        bw = 56 if lab != "SKIP" else 74
        on = lab == active
        d.ellipse([x * S, 10 * S, (x + 34) * S, 44 * S], outline=(220, 235, 250, 255) if on else (120, 140, 160, 255), width=2 * S)
        d.text(((x + 17) * S, 27 * S), lab, font=F(SL.MONO, 13 * S), fill=(235, 245, 255) if on else (150, 170, 190), anchor="mm")
        x += bw + 8
    d.text(((x + 2) * S, 27 * S), "STEP " + step, font=F(SL.MONO, 14 * S), fill=(220, 235, 250), anchor="lm")
    return dict(img=im.resize((W, H), Image.LANCZOS), kind="dossier")


MEDIUMS = {
    "holo": dict(name="A  PROJECTED HOLO", desc="every panel a projected readout from the deck; translucent, scanlined, emitter fan"),
    "bezel": dict(name="B  CRT MONITOR BEZELS", desc="each panel is a little physical CRT on the deck: plastic bezel, curved glass, power LED"),
    "glass": dict(name="C  TABLET GLASS PANE", desc="a tactical glass slate; the Cell's grease pencil can mark the intel right on it"),
    "decrypt": dict(name="D  DECRYPTED WINDOWS", desc="OS windows around C screens; corp files show the Halcyon seal cracked by the decrypt"),
    "mixed": dict(name="E  BY FICTION (recommended)", desc="network = Cell CRT terminal; order = intercepted memo under glass; intel = surveillance holo"),
}


def panels_for(medium):
    """Returns [(panel, x, y)] for the setup screen, plus the speed control."""
    if medium == "holo":
        return [(U.holo("YOUR NETWORK", rows_nodes(), w=330), 22, 130),
                (U.holo("RAID INCOMING", rows_order(), w=300, col=(255, 120, 110)), 1590, 110),
                (intel_holo(rows_intel(), w=330), 22, 430)]
    if medium == "bezel":
        return [(crt_bezel("YOUR NETWORK", rows_nodes(), w=350), 18, 126),
                (crt_bezel("RAID INCOMING", rows_order(), w=320, accent=HARM), 1582, 106),
                (crt_bezel("THREAT INTEL", rows_intel(), w=350, accent=HALCYON), 18, 470)]
    if medium == "glass":
        return [(glass_pane("YOUR NETWORK", rows_nodes(), w=340), 20, 130),
                (glass_pane("RAID INCOMING", rows_order(), w=310), 1588, 110),
                (glass_pane("THREAT INTEL", rows_intel(), w=340), 20, 450)]
    if medium == "decrypt":
        return [(decrypt_window("YOUR NETWORK", rows_nodes(), w=340, accent=CYAN, seal=False, exe="CELL_NET"), 20, 130),
                (decrypt_window("RAID INCOMING", rows_order(), w=320), 1580, 110),
                (decrypt_window("THREAT INTEL", rows_intel(), w=340), 20, 450)]
    return [(U.terminal("YOUR NETWORK", rows_nodes(), w=330), 22, 130),
            (memo_glass("WORK ORDER", rows_order(), w=290), 1574, 96),
            (intel_holo(rows_intel(), w=330), 22, 430)]
