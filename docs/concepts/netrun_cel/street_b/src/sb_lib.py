"""Campaign B street plates: shared kit (node kinds, stickers, state outlines, rooms, wax, pick B lane).

Builds on the locked netrun kit (read only, imported, never modified):
  route_map_graph/hq_halcyon/scripts/r32ui.py   node stickers (round 31/32 icons; MAINFRAME = the blue "M" modem)
  .../r31lib.py, sticker_lib19.py               glyph loader (round 17 glyphs), die-cut vinyl builder
  .../ui31.py (Pencil), kit44.py                wax grease pencil, terminal chips, key strip, cursor
  .../sidekit.py constants                      state colours (option orange, current/walked lime, ahead white, grey)
Room interiors are cut from the locked route-view render (sb_cells.py).
"""
import math
import os
import sys

HQ = "D:/rc_art/art-pass/docs/concepts/route_map_graph/hq_halcyon/scripts"
sys.path.insert(0, HQ)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps  # noqa: E402

import r31lib as L  # noqa: E402
import r32ui as U32  # noqa: E402
import ui31 as K  # noqa: E402
import kit44 as KT  # noqa: E402
import sb_cells  # noqa: E402

# r31lib / sticker_lib19 point at a font folder that no longer exists; use the repo fonts (same files, ui31 paths).
# This patches the imported module objects in this process only; the source files are untouched.
L.MONO = K.MONO
L.ANTON = K.ANTON
L.SL.MONO = K.MONO
L.SL.ANTON = K.ANTON

CONC = "D:/rc_art/art-pass/docs/concepts"
GOLDEN = CONC + "/golden_plates/street_overview.png"
OUTDIR = CONC + "/netrun_cel/street_b"
SCR = "D:/rc_scratch/street_b"
W, H = 1920, 1080

# state colours (bible 4.6 option A; sidekit.STATE_COL)
ORANGE = (255, 140, 26)
LIME = (212, 255, 0)
WHITE = (242, 246, 255)
GREY = (122, 118, 134)
INK = (14, 12, 20)
# round 7b pick B: edge (1.0, 0.18, 0.62), fill 0.22, line 4 px, beam_k 3.0
PICKB = (255, 46, 158)
PICKB_FILL = 0.22
PICKB_LINE = 4

# The six node kinds of Campaign B. word = BStreetRulesData.node_labels (port-campaign-b content/b/street_rules);
# type = StreetNodeState.T_*; locked = the r32ui sticker reused (None = no locked sticker exists).
# col / ring: sticker body and kind ring (sidekit.TYPE_COL; the locked r32ui rings for elite and rack are both MER
# orange, the proposal splits them: elite red-orange, rack amber).
KINDS = {
    "fight": dict(word="ROUTER", locked="router", shape="circle", col=(40, 36, 52), ring=(92, 225, 255), cell="router"),
    "elite": dict(word="ELITE ROUTER", locked="elite", shape="burst", col=(120, 40, 14), ring=(255, 96, 40), cell="elite"),
    "event": dict(word="TERMINAL", locked="terminal", shape="rsq", col=(14, 60, 36), ring=(61, 255, 139), cell="terminal"),
    "shop": dict(word="MAINFRAME", locked="modem", shape="tag", col=(20, 40, 96), ring=(90, 150, 255), cell="shop"),
    "rack": dict(word="SERVER RACK", locked="rack", shape="tall", col=(66, 44, 8), ring=(255, 196, 60), cell="rack"),
    "boss": dict(word="BLOCK SERVER", locked=None, shape="fort", col=(96, 10, 22), ring=(255, 44, 60), cell="rack"),
}
ORDER = ["fight", "elite", "event", "shop", "rack", "boss"]


# ------------------------------------------------------------------ silhouettes (proposal)
def _rrect(cx, cy, hw, hh, r, n=8):
    pts = []
    for qx, qy, a0 in ((1, -1, -90), (1, 1, 0), (-1, 1, 90), (-1, -1, 180)):
        ox, oy = cx + qx * (hw - r), cy + qy * (hh - r)
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((ox + r * math.cos(a), oy + r * math.sin(a)))
    return pts


def shape_pts(shape, P, k=1.0, margin=6):
    c = P / 2
    R = (P / 2 - margin) * k
    if shape == "circle":
        return [(c + R * math.cos(2 * math.pi * i / 72), c + R * math.sin(2 * math.pi * i / 72)) for i in range(72)]
    if shape == "burst":
        pts = []
        for i in range(16):
            rr = R * 1.04 if i % 2 == 0 else R * 0.70
            a = 2 * math.pi * i / 16 - math.pi / 2
            pts.append((c + rr * math.cos(a), c + rr * math.sin(a)))
        return pts
    if shape == "rsq":
        # a monitor: screen, neck and foot (the TERMINAL)
        sx0, sx1, sy0, sy1 = c - R * 0.94, c + R * 0.94, c - R * 0.82, c + R * 0.50
        return [(sx0, sy0), (sx1, sy0), (sx1, sy1), (c + R * 0.16, sy1), (c + R * 0.16, c + R * 0.70), (c + R * 0.52, c + R * 0.70),
                (c + R * 0.52, c + R * 0.92), (c - R * 0.52, c + R * 0.92), (c - R * 0.52, c + R * 0.70), (c - R * 0.16, c + R * 0.70),
                (c - R * 0.16, sy1), (sx0, sy1)]
    if shape == "tag":
        # a price tag (the shop's kraft tags, bible 4.10): pointed left end, square right end
        base = [(-1.0, 0.0), (-0.52, -0.70), (0.96, -0.70), (0.96, 0.70), (-0.52, 0.70)]
        return [(c + x * R, c + y * R) for x, y in base]
    if shape == "tall":
        return _rrect(c, c, R * 0.64, R * 1.0, R * 0.16)
    if shape == "octagon":
        return [(c + R * 1.02 * math.cos(2 * math.pi * i / 8 + math.pi / 8), c + R * 1.02 * math.sin(2 * math.pi * i / 8 + math.pi / 8))
                for i in range(8)]
    if shape == "fort":
        # a keep with three merlons: the HQ's last wall (BLOCK SERVER); wide, crenellated top
        base = [(-0.88, 0.88), (-0.88, -0.94), (-0.46, -0.94), (-0.46, -0.52), (-0.21, -0.52), (-0.21, -0.94), (0.21, -0.94),
                (0.21, -0.52), (0.46, -0.52), (0.46, -0.94), (0.88, -0.94), (0.88, 0.88)]
        return [(c + x * R, c + y * R) for x, y in base]
    raise ValueError(shape)


def art(kind, px, shape=None):
    """Sticker art (before the die-cut border) for a kind, in the proposal silhouette (or `shape`)."""
    k = KINDS[kind]
    shape = shape or k["shape"]
    S = 2
    P = max(px, 120) * S
    im = Image.new("RGBA", (P, P), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    body = shape_pts(shape, P, 1.0, 3 * S)
    d.polygon(body, fill=k["col"] + (255,))
    d.line(body + [body[0]], fill=L.INK + (255,), width=3 * S, joint="curve")
    ring = shape_pts(shape, P, 0.86 if shape != "tall" else 0.88, 3 * S)
    d.line(ring + [ring[0]], fill=k["ring"] + (255,), width=4 * S, joint="curve")
    c = P / 2
    if kind == "fight":
        g = L.glyph("slice_exploit", int(P * 0.5), ow=2 * S)
        im.alpha_composite(g, (int(c - g.width / 2), int(c - g.height / 2)))
    elif kind == "elite":
        g = L.glyph("slice_zero_day", int(P * 0.46), fill=(255, 220, 160), ow=2 * S)
        im.alpha_composite(g, (int(c - g.width / 2), int(c - g.height / 2)))
    elif kind == "event":
        x0, y0, x1, y1 = P * 0.22, P * 0.20, P * 0.78, P * 0.58
        d.rounded_rectangle([x0, y0, x1, y1], radius=4 * S, fill=(10, 30, 18, 255), outline=(255, 255, 255, 255), width=3 * S)
        d.text((x0 + 8 * S, (y0 + y1) / 2), ">_", font=L.f_mono(int(P * 0.24)), fill=(61, 255, 139, 255), anchor="lm")
    elif kind == "shop":
        hx = c - 0.62 * (P / 2 - 3 * S)
        hr = 0.085 * P
        d.ellipse([hx - hr, c - hr, hx + hr, c + hr], fill=(6, 8, 18, 255), outline=k["ring"] + (255,), width=2 * S)
        x0, y0, x1, y1 = P * 0.36, P * 0.30, P * 0.80, P * 0.70
        d.rounded_rectangle([x0, y0, x1, y1], radius=5 * S, fill=(14, 30, 70, 255), outline=(255, 255, 255, 255), width=3 * S)
        d.text(((x0 + x1) / 2, (y0 + y1) / 2 + S), "M", font=L.font(L.ANTON, int(P * 0.27)), fill=(120, 190, 255, 255), anchor="mm")
    elif kind == "boss":
        # two server blades either side of the padlock (a locked server), inside the keep
        for sx in (0.20, 0.68):
            for j in range(3):
                y0 = P * (0.50 + j * 0.09)
                d.rectangle([P * sx, y0, P * (sx + 0.12), y0 + P * 0.06], fill=(28, 10, 14, 255), outline=(150, 60, 70, 255), width=S)
                d.ellipse([P * sx + 3 * S, y0 + P * 0.03 - 2 * S, P * sx + 7 * S, y0 + P * 0.03 + 2 * S], fill=(255, 70, 80, 255))
        g = L.glyph("state_locked", int(P * 0.40), ow=2 * S)
        im.alpha_composite(g, (int(c - g.width / 2), int(P * 0.36)))
    elif kind == "rack":
        x0, x1 = P * 0.30, P * 0.70
        ya, yb = P * 0.17, P * 0.83
        n = 5
        for j in range(n):
            y0 = ya + j * (yb - ya) / n
            y1 = y0 + (yb - ya) / n - 4 * S
            d.rectangle([x0, y0, x1, y1], fill=(28, 22, 18, 255), outline=(150, 110, 60, 255) if kind == "rack" else (150, 60, 70, 255), width=S)
            for q in range(3):
                on = (j + q) % 2
                col = ((255, 190, 60) if on else (80, 255, 140)) if kind == "rack" else ((255, 70, 80) if on else (120, 30, 40))
                d.ellipse([x0 + 5 * S + q * 9 * S, (y0 + y1) / 2 - 3 * S, x0 + 11 * S + q * 9 * S, (y0 + y1) / 2 + 3 * S], fill=col + (255,))
    return im.resize((px, px), Image.LANCZOS)


_sd = {}


def sticker_sd(kind, px, mode="proposal", grey=False):
    """Die-cut vinyl sticker dict. mode 'locked' = the r32ui icon as drawn in rounds 31/32 (circle / rounded square)."""
    key = (kind, px, mode, grey)
    if key not in _sd:
        if mode == "locked":
            a = U32.icon(KINDS[kind]["locked"], px)
        else:
            a = art(kind, px)
        sd = L.sticker_from_art(a, border=5, seed=sum(map(ord, kind)) % 97)
        _sd[key] = L.greyscale(sd, 0.7) if grey else sd
    return _sd[key]


def node_tile(kind, px, state=None, mode="proposal", grey=False, alpha=1.0, ring_w=4, angle=None, hover=0.0):
    """A node as it sits on the street: the sticker and its state outline (the outline follows the silhouette).
    Returns an RGBA tile; its centre is the node centre."""
    T = int(px * 2.2)
    tile = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    sd = sticker_sd(kind, px, mode, grey)
    ang = angle if angle is not None else ((sum(map(ord, kind)) % 9) - 4) * 0.6
    st = L.place_sticker(Image.new("RGBA", (T, T), (0, 0, 0, 0)), sd, T / 2, T / 2, angle=ang, hover=hover,
                         shadow=0.0 if grey else 1.0)
    if state:
        col = {"option": ORANGE, "current": LIME, "walked": LIME, "ahead": WHITE, "grey": GREY}[state]
        a = st.split()[3].point(lambda v: 255 if v > 90 else 0)
        gap = 3
        inner = a.filter(ImageFilter.MaxFilter(2 * gap + 1))
        outer = inner.filter(ImageFilter.MaxFilter(2 * ring_w + 1))
        rm = ImageChops.subtract(outer, inner).filter(ImageFilter.GaussianBlur(0.6))
        tile = K.over(tile, (6, 5, 10), K.SL.shift(rm, 1, 2), 0.9)
        tile = K.over(tile, col, rm)
    tile.alpha_composite(st)
    if alpha < 1.0:
        tile.putalpha(tile.split()[3].point(lambda v: int(v * alpha)))
    return tile


def put(img, tile, cx, cy):
    img.alpha_composite(tile, (int(round(cx - tile.width / 2)), int(round(cy - tile.height / 2))))
    return img


# ------------------------------------------------------------------ rooms (cutaways in the frontage)
_src = {}


def _cell(name):
    if not _src:
        _src["im"] = Image.open(sb_cells.SRC).convert("RGB")
    return _src["im"].crop(sb_cells.CELLS[name])


def room(img, kind, box, mode="full"):
    """Open a room in the facade at box (x0, y0, x1, y1). mode: full / dim / grey."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    c = _cell(KINDS[kind]["cell"]).resize((w, h), Image.LANCZOS)
    if kind == "boss":
        # staged: the rack room re-lit red (no BLOCK SERVER room exists in any render)
        g = ImageOps.grayscale(c)
        c = ImageOps.colorize(g, (20, 2, 6), (255, 90, 100))
    if mode == "dim":
        c = ImageEnhance.Color(c).enhance(0.6)
        c = ImageEnhance.Brightness(c).enhance(0.6)
    elif mode == "grey":
        c = ImageEnhance.Color(c).enhance(0.25)
        c = ImageEnhance.Brightness(c).enhance(0.34)
    # light spill from the open room onto the facade (full rooms only)
    if mode in ("full", "dim"):
        m = Image.new("L", img.size, 0)
        ImageDraw.Draw(m).rectangle(box, fill=255)
        mean = tuple(int(v) for v in np.asarray(c, np.float32).reshape(-1, 3).mean(axis=0))
        img = K.add_glow(img, m, mean, 22, 0.22 if mode == "full" else 0.10)
    img.paste(c, (x0, y0))
    d = ImageDraw.Draw(img)
    # cut edge: slab above, floor lip below, dark jambs (the cutaway frame of the route view)
    d.rectangle([x0 - 3, y0 - 6, x1 + 3, y0 - 1], fill=(14, 10, 22, 255))
    d.rectangle([x0 - 3, y1, x1 + 3, y1 + 4], fill=(30, 24, 40, 255))
    d.line([(x0 - 3, y1 + 4), (x1 + 3, y1 + 4)], fill=(70, 60, 90, 255), width=1)
    d.rectangle([x0 - 3, y0 - 1, x0 - 1, y1], fill=(10, 8, 16, 255))
    d.rectangle([x1, y0 - 1, x1 + 2, y1], fill=(10, 8, 16, 255))
    return img


def frame_room(img, box, col, w=2, alpha=1.0, glow=False):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = box
    d.rectangle([x0 - 4, y0 - 7, x1 + 4, y1 + 5], outline=tuple(col) + (int(255 * alpha),), width=w)
    if glow:
        m = Image.new("L", img.size, 0)
        ImageDraw.Draw(m).rectangle([x0 - 4, y0 - 7, x1 + 4, y1 + 5], outline=255, width=w)
        img = K.add_glow(img, m, col, 8, 0.7 * alpha)
    img.alpha_composite(lay)
    return img


# ------------------------------------------------------------------ wax pencil
def dashes(pts, on, off):
    out, cur, phase_on = [], [pts[0]], True
    left = on
    for a, b in zip(pts, pts[1:]):
        Lg = math.hypot(b[0] - a[0], b[1] - a[1])
        if Lg == 0:
            continue
        t = 0.0
        while Lg - t > left:
            t += left
            q = (a[0] + (b[0] - a[0]) * t / Lg, a[1] + (b[1] - a[1]) * t / Lg)
            if phase_on:
                cur.append(q)
                if len(cur) > 1:
                    out.append(cur)
                cur = []
            else:
                cur = [q]
            phase_on = not phase_on
            left = on if phase_on else off
        left -= Lg - t
        if phase_on:
            cur.append(b)
    if phase_on and len(cur) > 1:
        out.append(cur)
    return out


def link_path(a, b, bend=0.5):
    """A hand-drawn link between two node centres: leaves level, turns, arrives level (the route view's wax runs)."""
    (ax, ay), (bx, by) = a, b
    n = max(8, int(math.hypot(bx - ax, by - ay) / 8))
    out = []
    for i in range(n + 1):
        t = i / n
        # level out of a, a smooth S across, level into b (bend > 0.5 keeps it level longer at the start)
        u = min(1.0, max(0.0, (t - (bend - 0.5) * 0.8) / (1 - abs(bend - 0.5) * 0.8)))
        e = (1 - math.cos(math.pi * u)) / 2
        out.append((ax + (bx - ax) * t, ay + (by - ay) * e))
    return out


def wax(img, paths, col, width, alpha=1.0, dash=None, seed=501, clear=(), glow=0):
    """Ink a set of polylines in wax. clear = [(cx, cy, r)] discs kept free (the wax stops short of the stickers)."""
    pen = K.Pencil(img.size, col, seed=seed)
    for p in paths:
        p = [p[0]] + pen.wobble(p[1:-1], 0.6) + [p[-1]]
        for seg in (dashes(p, *dash) if dash else [p]):
            if len(seg) > 1:
                pen.stroke(seg, width)
    s = pen.mask.size[0] / img.size[0]
    dm = ImageDraw.Draw(pen.mask)
    for cx, cy, r in clear:
        dm.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s], fill=0)
    if alpha < 1.0:
        pen.mask = pen.mask.point(lambda v: int(v * alpha))
    if glow:
        m = pen.mask.resize(img.size, Image.LANCZOS)
        img = K.add_glow(img, m, col, 8, glow / 255)
    return pen.ink(img, shadow=0.85 * alpha)


def number_chip(img, x, y, n, col=ORANGE, alpha=1.0):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    box = (x - 12, y - 13, x + 12, y + 13)
    lay = KT.panel_shadow(lay, box, 0, blur=5, k=0.55, off=(0, 3))
    d = ImageDraw.Draw(lay)
    d.rectangle(box, fill=col + (255,), outline=(10, 8, 14, 255), width=2)
    K.text(lay, (x, y + 1), str(n), K.F(K.ANTON, 20), (14, 10, 6), "mm", 0)
    if alpha < 1:
        lay.putalpha(lay.split()[3].point(lambda v: int(v * alpha)))
    img.alpha_composite(lay)
    return img


# ------------------------------------------------------------------ pick B lane highlight
def lane_mask(size, pts, width):
    S = 2
    m = Image.new("L", (size[0] * S, size[1] * S), 0)
    d = ImageDraw.Draw(m)
    sp = [(x * S, y * S) for x, y in pts]
    r = width * S / 2
    # stamp discs densely along the path (wide PIL lines leave butt-cap teeth on curves)
    for (ax, ay), (bx, by) in zip(sp, sp[1:]):
        n = max(1, int(math.hypot(bx - ax, by - ay) / 3))
        for i in range(n + 1):
            x, y = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    return m.resize(size, Image.LANCZOS)


def pick_b(img, mask, fill=PICKB_FILL, line=PICKB_LINE, col=PICKB):
    """Round 7b candB on a mask: pink fill at 0.22, a 4 px pink edge with its bloom."""
    img = K.over(img, col, mask, fill)
    hard = mask.point(lambda v: 255 if v > 127 else 0)
    edge = ImageChops.subtract(hard, hard.filter(ImageFilter.MinFilter(2 * line + 1))).filter(ImageFilter.GaussianBlur(0.5))
    img = K.add_glow(img, edge, col, 9, 0.9)
    img = K.over(img, col, edge)
    return img


def beam(img, x, y_top, y_bottom, col=PICKB, k=3.0):
    """The pick B beam (beam_k 3.0): a thin vertical light rising from the highlight, fading upward."""
    a = np.asarray(img, np.float32)
    hgt = y_bottom - y_top
    ys = np.arange(H, dtype=np.float32)
    fade = np.clip((ys - y_top) / max(1, hgt), 0, 1) ** 0.6
    fade[ys > y_bottom] = 0
    xs = np.arange(W, dtype=np.float32)
    core = np.exp(-((xs - x) / 1.6) ** 2)
    halo = np.exp(-((xs - x) / 14.0) ** 2) * 0.35
    prof = (core + halo) * k / 3.0
    m = fade[:, None] * prof[None, :]
    a[..., :3] = np.clip(a[..., :3] + m[..., None] * np.array(col, np.float32) * 0.85
                         + (core[None, :] * fade[:, None] * 120 * k / 3.0)[..., None], 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def grade(img, mask, k_out=0.80, desat_out=0.15):
    """Mild hover grade: outside the hovered lane slightly down (the bible's x0.20 power cut is reserved for hover-all)."""
    rgb = img.convert("RGB")
    dim = ImageEnhance.Brightness(ImageEnhance.Color(rgb).enhance(1 - desat_out)).enhance(k_out).convert("RGBA")
    soft = mask.filter(ImageFilter.GaussianBlur(40)).point(lambda v: min(255, v * 2))
    return Image.composite(img, dim, soft)


def font_mono(px):
    return K.F(K.MONO, px)


def font_anton(px):
    return K.F(K.ANTON, px)
