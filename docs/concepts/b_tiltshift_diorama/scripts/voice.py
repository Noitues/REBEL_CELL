"""The Cell's voice layer as data (pure Python): marker words, drips, sticker cards, tape.

Builds Grease Pencil spec items (pixel space) shared by gp_overlay.py (Blender) and post.py (Pillow).
"""
import math
import random
import stroke_font as SF

PINK = "#ff3da8"
PAPER = "#f2eee4"
NOTE_YELLOW = "#f2dc7a"
NOTE_PINK = "#f4c3cf"
STICKER_PINK = "#f5afcb"
INK = "#111111"
TAPE = "#e9dfc6"


def rot_pts(pts, cx, cy, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    # visually counter-clockwise in a y-down space (matches PIL rotate)
    return [(cx + (x - cx) * ca + (y - cy) * sa, cy - (x - cx) * sa + (y - cy) * ca) for x, y in pts]


def rrect(cx, cy, w, h, r, deg=0.0, n=6, peel=0.0):
    """Rounded rect polygon; peel>0 chamfers the bottom-right corner (the peeling corner)."""
    pts = []
    corners = [(cx + w / 2 - r, cy + h / 2 - r, 0), (cx - w / 2 + r, cy + h / 2 - r, 90),
               (cx - w / 2 + r, cy - h / 2 + r, 180), (cx + w / 2 - r, cy - h / 2 + r, 270)]
    for k, (ox, oy, a0) in enumerate(corners):
        if k == 0 and peel > 0:
            pts.append((cx + w / 2, cy + h / 2 - peel))
            pts.append((cx + w / 2 - peel, cy + h / 2))
            continue
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((ox + r * math.cos(a), oy + r * math.sin(a)))
    return rot_pts(pts, cx, cy, deg)


def sticker(cx, cy, w, h, fill, deg=0.0, border=7, radius=12, shadow=(9, 13, 0.45), peel=0.0, lift=0.0):
    """Die-cut sticker: soft shadow, white border, coloured face, optional peeling corner.

    lift: 0 = pressed flat, 1 = mid-slap (bigger shadow offset, softer)."""
    items = []
    sx, sy, sa = shadow
    sx, sy = sx * (1 + 3 * lift), sy * (1 + 3 * lift)
    sa = sa * (1 - 0.35 * lift)
    B = border
    items.append({"type": "poly", "pts": rrect(cx + sx, cy + sy, w + 2 * B + 4, h + 2 * B + 4, radius + B, deg,
                                             peel=peel + B * 0.6 if peel else 0),
                  "fill": "#000000", "alpha": sa * 0.5})
    items.append({"type": "poly", "pts": rrect(cx + sx * 0.6, cy + sy * 0.6, w + 2 * B, h + 2 * B, radius + B, deg,
                                             peel=peel + B * 0.6 if peel else 0),
                  "fill": "#000000", "alpha": sa})
    items.append({"type": "poly", "pts": rrect(cx, cy, w + 2 * B, h + 2 * B, radius + B, deg,
                                             peel=peel + B * 0.6 if peel else 0), "fill": "#fbfaf6"})
    items.append({"type": "poly", "pts": rrect(cx, cy, w, h, radius, deg, peel=peel), "fill": fill})
    if peel:
        # the folded flap: mirror of the cut corner across the chamfer, with a shadow under it
        P = peel + B * 0.6
        c1 = (cx + w / 2 + B, cy + h / 2 + B - P)
        c2 = (cx + w / 2 + B - P, cy + h / 2 + B)
        tip = (c1[0] - P * 0.95, c1[1] - P * 0.05 + 0)
        tip = (cx + w / 2 + B - P * 0.92, cy + h / 2 + B - P * 0.92)
        fl = rot_pts([c1, c2, tip], cx, cy, deg)
        sh = rot_pts([c1, c2, (tip[0] - 6, tip[1] - 3)], cx, cy, deg)
        items.append({"type": "poly", "pts": sh, "fill": "#000000", "alpha": 0.35})
        items.append({"type": "poly", "pts": fl, "fill": "#dcd6c8"})
    return items


def tape(cx, cy, w, h, deg, seed, alpha=0.72):
    rng = random.Random(seed)
    pts = []
    # torn ends: zig-zag on the short sides
    n = 6
    for i in range(n + 1):
        pts.append((cx - w / 2 + rng.uniform(-3, 3), cy - h / 2 + h * i / n))
    for i in range(n + 1):
        pts.append((cx + w / 2 + rng.uniform(-3, 3), cy + h / 2 - h * i / n))
    pts = [pts[0]] + pts[1:]
    # order: left side top->bottom, right side bottom->top
    return {"type": "poly", "pts": rot_pts(pts, cx, cy, deg), "fill": TAPE, "alpha": alpha}


def marker(text, x, y, height, seed, width=None, color=PINK, frac=1.0, rot=-4.0, slant=0.18):
    strokes = SF.layout_word(text, x, y, height, seed, slant=slant, rot_deg=rot)
    full = strokes
    if frac < 1.0:
        strokes = SF.truncate(strokes, frac)
    w = width or height * 0.16
    return {"type": "marker", "strokes": strokes, "color": color, "width": w}, full


def drips(full_strokes, seed, count, width, lengths, color=PINK, streak=False):
    items = []
    src = SF.drip_sources(full_strokes, seed, count, 0)
    for (px, py, k), L in zip(src, lengths):
        items.append({"type": "drip", "x": px, "y": py - width * 0.2, "len": L * k if not streak else L,
                      "width": width, "color": color, "streak": streak})
    return items


def pen_nib(x, y, deg=62):
    """The marker that is writing: felt nib at (x, y), barrel leaning up-right out of frame."""
    a = math.radians(deg)
    ax, ay = math.cos(a), -math.sin(a)          # barrel axis (up-right on screen)
    nx, ny = -ay, ax                             # its normal

    def quad(s0, s1, w0, w1):
        return [(x + ax * s0 + nx * w0, y + ay * s0 + ny * w0), (x + ax * s1 + nx * w1, y + ay * s1 + ny * w1),
                (x + ax * s1 - nx * w1, y + ay * s1 - ny * w1), (x + ax * s0 - nx * w0, y + ay * s0 - ny * w0)]
    sh = [(px + 14, py + 18) for px, py in quad(26, 330, 20, 24)]
    return [{"type": "poly", "pts": sh, "fill": "#000000", "alpha": 0.35},
            {"type": "poly", "pts": quad(0, 16, 5, 8), "fill": "#ff5cb6"},
            {"type": "poly", "pts": quad(14, 40, 9, 17), "fill": "#d9d9df"},
            {"type": "poly", "pts": quad(38, 330, 20, 22), "fill": "#1c1c22"},
            {"type": "poly", "pts": quad(60, 110, 20.5, 21), "fill": PINK},
            {"type": "poly", "pts": quad(140, 320, 6, 6), "fill": "#34343c"}]


def marker_fit(text, x0, x1, base_y, seed, max_h, rot=-4.0, width_ratio=0.2, color=PINK, frac=1.0):
    """Marker word sized to span [x0, x1] (centred), baseline near base_y."""
    probe = SF.layout_word(text, 0, 0, 100, seed, rot_deg=rot)
    ex = SF.word_extent(probe)
    h = min(max_h, 100 * (x1 - x0) / (ex[2] - ex[0]))
    st = SF.layout_word(text, 0, base_y, h, seed, rot_deg=rot)
    ex = SF.word_extent(st)
    dx = x0 + ((x1 - x0) - (ex[2] - ex[0])) / 2 - ex[0]
    st = [[(p[0] + dx, p[1], p[2]) for p in s] for s in st]
    full = st
    if frac < 1.0:
        st = SF.truncate(st, frac)
    w = max(6, h * width_ratio)
    return {"type": "marker", "strokes": st, "color": color, "width": w}, full
