"""Round 18 / 1: the sticker card lifecycle on the D4 combat screen.

HEAVY SPIN (WHEEL, 2 RAM, spin a wheel 9 ticks) is peeled out of the hand, dragged onto the boss
wheel with a grease-pencil aim line, slapped on, dissolved into a 0/1 bit stream that spirals into the
hub, and the wheel spins 9 ticks (108 deg).

python card_play.py            # card_play.gif + card_play_storyboard.png
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import plates as P
import make_combat as MC
import fxlib as FX
from fxlib import seg, lerp, lerp2, bez, ease_out_cubic, ease_in_cubic, ease_in_out, ease_out_back
from slicelib import f_num, f_ui, f_mono

OUT = P.OUT
HOV = 4                      # HEAVY SPIN, the right-most card
TYPE_COL = (255, 196, 40)    # WHEEL type colour
HUB = P.BOSS["c"]
R_B = P.BOSS["r"]
SPIN_DEG = 108.0             # 9 ticks x 12 deg

# timeline (ms)
T_HOVER = (560, 860)
T_PEEL = (860, 1000)
T_POP = (1000, 1100)
T_DRAG = (1100, 1700)
T_AIM_DRAW = (1120, 1280)
T_SNAP = 1580
T_DROP = (1700, 1780)
T_SQUASH = (1780, 1940)
T_DISSOLVE = (1940, 2240)    # scan front top -> bottom
T_HUB = (2380, 2560)         # hub charge ring
T_SPIN = (2520, 3420)
T_CLOSE = (3500, 3800)
T_END = 4400

SLOT = P.hand_slot(HOV, 5)
SLOT_C = (SLOT[0], SLOT[1] + 96)  # hand card centre (the slot y is its top)
HOVER_C = (SLOT[0], SLOT[1] - 4)
SLAP_C = (HUB[0], HUB[1] + 6)
SLAP_ANG = -4.0


# ------------------------------------------------------------------ card faces
_F = {}


def card_face(i, w, h):
    """C-C sticker card: die-cut white margin, no baked shadow (shadows are per state)."""
    key = (i, w, h)
    if key in _F:
        return _F[key]
    orig = MC.vinyl
    MC.vinyl = lambda body, border=6, tilt=0.0, shadow=0.55, gloss=True: orig(body, border=border, tilt=tilt, shadow=0, gloss=gloss)
    try:
        c = MC.card_img(MC.CARDS[i], w, h)
    finally:
        MC.vinyl = orig
    bb = c.getbbox()
    c = c.crop(bb)
    _F[key] = c
    return c


def big_face():
    return card_face(HOV, 196, 262)


# ------------------------------------------------------------------ path of the moving card
def cursor_at(t):
    """Cursor position and pressed flag."""
    if t < 200:
        return (1830, 1060), False
    if t < T_HOVER[0]:
        p = ease_in_out(seg(t, 200, T_HOVER[0]))
        return lerp2((1830, 1060), (HOVER_C[0] + 30, HOVER_C[1] + 60), p), False
    if t < T_PEEL[0]:
        p = ease_out_cubic(seg(t, T_HOVER[0], T_HOVER[1]))
        return lerp2((HOVER_C[0] + 30, HOVER_C[1] + 60), (HOVER_C[0] + 62, HOVER_C[1] - 70), p), False
    if t < T_DRAG[0]:
        return (HOVER_C[0] + 62 - 10 * seg(t, T_PEEL[0], T_DRAG[0]), HOVER_C[1] - 70 - 30 * seg(t, T_PEEL[0], T_DRAG[0])), True
    if t < T_DROP[0]:
        p = ease_in_out(seg(t, T_DRAG[0], T_SNAP))
        a = (HOVER_C[0] + 52, HOVER_C[1] - 100)
        b = (SLAP_C[0] + 40, SLAP_C[1] - 50)
        q = bez(a, (880, 420), b, p)  # swings out over the centre gap, then onto the wheel
        if t > T_SNAP:  # small settle wiggle over the target
            w = seg(t, T_SNAP, T_DROP[0])
            q = (q[0] + 6 * math.sin(w * 7) * (1 - w), q[1] + 3 * math.cos(w * 5) * (1 - w))
        return q, True
    return (SLAP_C[0] + 40 + 30 * ease_out_cubic(seg(t, T_DROP[0], T_DROP[0] + 500)), SLAP_C[1] - 50 + 60 * ease_out_cubic(seg(t, T_DROP[0], T_DROP[0] + 500))), False


GRAB = (-52, 100)  # card centre relative to the cursor while dragging


def card_state(t):
    """Moving card: centre, scale x/y, angle, peel amount, shadow (offset, blur, alpha). None once gone."""
    k_hand = 144 / 196
    if t < T_HOVER[0]:
        bob = 2 * math.sin(2 * math.pi * (t / 2400 + HOV * 0.17))
        return dict(c=(SLOT_C[0], SLOT_C[1] + bob), sx=k_hand, sy=k_hand, ang=SLOT[2], peel=0.03 + 0.01 * math.sin(t / 380),
                    sh=((3, 5), 3, 0.55))
    if t < T_PEEL[0]:
        p = ease_out_back(seg(t, *T_HOVER), 1.3)
        k = lerp(k_hand, 1.0, p)
        return dict(c=lerp2(SLOT_C, HOVER_C, p), sx=k, sy=k, ang=lerp(SLOT[2], -3, p), peel=lerp(0.03, 0.17, p),
                    sh=(lerp2((3, 5), (9, 15), p), lerp(3, 8, p), lerp(0.55, 0.5, p)))
    if t < T_POP[0]:
        p = ease_in_out(seg(t, *T_PEEL))
        return dict(c=(HOVER_C[0], HOVER_C[1] - 8 * p), sx=1.0, sy=1.0, ang=-3, peel=lerp(0.17, 0.28, p),
                    sh=((9, 15), 8, 0.5))
    if t < T_DRAG[0]:
        p = ease_out_back(seg(t, *T_POP), 1.6)
        return dict(c=(HOVER_C[0] - 10 * p, HOVER_C[1] - 8 - 26 * p), sx=lerp(1.0, 1.1, p), sy=lerp(1.0, 1.1, p), ang=lerp(-3, 2, p),
                    peel=lerp(0.28, 0.07, ease_out_cubic(seg(t, *T_POP))), sh=(lerp2((9, 15), (22, 34), p), lerp(8, 16, p), lerp(0.5, 0.38, p)))
    if t < T_DROP[0]:
        # follow the cursor with lag (spring), tilt with velocity
        cur, _ = cursor_at(t)
        prv, _ = cursor_at(t - 60)
        lag = 0.0
        tx, ty = cur[0] + GRAB[0], cur[1] + GRAB[1]
        px, py = prv[0] + GRAB[0], prv[1] + GRAB[1]
        c = (lerp(tx, px, 0.35), lerp(ty, py, 0.35))
        vx = (cur[0] - prv[0]) / 0.06
        ang = max(-12, min(12, -vx * 0.012)) + 2
        g = seg(t, T_SNAP - 80, T_DROP[0])
        ang = lerp(ang, SLAP_ANG - 2, g)
        c = lerp2(c, (SLAP_C[0], SLAP_C[1] - 14), ease_in_out(g))
        return dict(c=c, sx=1.1, sy=1.1, ang=ang, peel=0.07 + 0.03 * math.sin(t / 90), sh=((22, 34), 16, 0.38))
    if t < T_SQUASH[0]:
        p = ease_in_cubic(seg(t, *T_DROP))
        k = lerp(1.1, 1.0, p)
        return dict(c=lerp2((SLAP_C[0], SLAP_C[1] - 14), SLAP_C, p), sx=k, sy=k, ang=lerp(SLAP_ANG - 2, SLAP_ANG, p), peel=lerp(0.07, 0.0, p),
                    sh=(lerp2((22, 34), (2, 3), p), lerp(16, 2, p), lerp(0.38, 0.7, p)))
    if t < T_DISSOLVE[0]:
        q = seg(t, *T_SQUASH)
        # squash 1.13 / 0.86 at contact, overshoot to 0.97 / 1.04, settle
        if q < 0.35:
            w = ease_out_cubic(q / 0.35)
            sx, sy = lerp(1.0, 1.13, w), lerp(1.0, 0.86, w)
        elif q < 0.7:
            w = ease_in_out((q - 0.35) / 0.35)
            sx, sy = lerp(1.13, 0.97, w), lerp(0.86, 1.04, w)
        else:
            w = ease_in_out((q - 0.7) / 0.3)
            sx, sy = lerp(0.97, 1.0, w), lerp(1.04, 1.0, w)
        return dict(c=SLAP_C, sx=sx, sy=sy, ang=SLAP_ANG, peel=0.0, sh=((2, 3), 2, 0.7))
    return dict(c=SLAP_C, sx=1.0, sy=1.0, ang=SLAP_ANG, peel=0.0, sh=((2, 3), 2, 0.7), dissolving=True)


def draw_card(img, st, face=None, gloss_t=None):
    face = face or big_face()
    if st["peel"] > 0.004:
        f, pad = FX.peel(face, st["peel"], "tr")
    else:
        f = face
    if gloss_t is not None:
        f = gloss_sweep(f, gloss_t)
    FX.place(img, f, st["c"][0], st["c"][1], st["sx"], st["sy"], st["ang"], shadow=st["sh"])


def gloss_sweep(face, p):
    """A white shine band crossing the vinyl right after the slap."""
    w, h = face.size
    g = Image.new("L", face.size, 0)
    d = ImageDraw.Draw(g)
    x = lerp(-0.4 * w, 1.3 * w, p)
    d.polygon([(x, 0), (x + 0.22 * w, 0), (x + 0.02 * w, h), (x - 0.2 * w, h)], fill=150)
    g = g.filter(ImageFilter.GaussianBlur(6))
    g = Image.fromarray(np.minimum(np.asarray(g), np.asarray(face.split()[3])).astype(np.uint8))
    out = face.copy()
    wl = Image.new("RGBA", face.size, (255, 255, 255, 0))
    wl.putalpha(g)
    out.alpha_composite(wl)
    return out


# ------------------------------------------------------------------ hand
def draw_hand(img, t, skip_hov=True):
    n = 5
    close = ease_in_out(seg(t, *T_CLOSE))
    spread = ease_out_cubic(seg(t, *T_HOVER)) * (1 - seg(t, T_POP[1], T_POP[1] + 250))
    idx = [i for i in range(n) if i != HOV]
    for j, i in enumerate(idx):
        x0, y0, r0 = P.hand_slot(i, n)
        x1, y1, r1 = P.hand_slot(j, n - 1)
        x, y, r = lerp(x0, x1, close), lerp(y0, y1, close), lerp(r0, r1, close)
        x -= 14 * spread * (1 if i == 3 else 0.5 if i == 2 else 0.25)
        idle = 1 - seg(t, T_HOVER[0], T_HOVER[1])  # the idle loop rests while a card is in play
        bob = 2 * math.sin(2 * math.pi * (t / 2400 + i * 0.17)) * idle
        face = card_face(i, 144, 192)
        f, pad = FX.peel(face, 0.025 + 0.012 * math.sin(t / 420 + i) * idle, "tr")
        FX.place(img, f, x, y + 96 + bob, 1, 1, r, shadow=((3, 5), 3, 0.55))
    # the empty liner left behind in the slot: a faint die-cut line, fades as the hand closes
    if t >= T_POP[0]:
        a = 0.55 * (1 - close)
        if a > 0.02:
            liner = Image.new("RGBA", (156, 206), (0, 0, 0, 0))
            d = ImageDraw.Draw(liner)
            d.rounded_rectangle([2, 2, 153, 203], radius=18, fill=(236, 232, 222, int(60 * a)))
            for k in range(0, 600, 16):  # dashed cut line
                pass
            d.rounded_rectangle([2, 2, 153, 203], radius=18, outline=(250, 248, 240, int(255 * a)), width=2)
            liner = liner.rotate(SLOT[2], resample=Image.BICUBIC, expand=True)
            img.alpha_composite(liner, (int(SLOT_C[0] - liner.width / 2), int(SLOT_C[1] - liner.height / 2 + 4)))


# ------------------------------------------------------------------ grease pencil aim
def aim_points(t):
    """From the dragged card's leading (top) edge to the edge of the target hub: the line shortens as
    the card closes in, so the pencil always says 'this goes there'."""
    st = card_state(t)
    c = st["c"]
    h = 262 * st["sy"] * 0.5
    start = (c[0] + 30, c[1] - h + 10)
    dx, dy = start[0] - HUB[0], start[1] - HUB[1]
    L = max(1.0, math.hypot(dx, dy))
    end = (HUB[0] + dx / L * R_B * 0.28, HUB[1] + dy / L * R_B * 0.28)
    ctrl = ((start[0] + end[0]) / 2 + 0.25 * (end[1] - start[1]), (start[1] + end[1]) / 2 - 0.25 * (end[0] - start[0]))
    return [bez(start, ctrl, end, s) for s in np.linspace(0, 1, 24)], L


def loop_points(t):
    rr = R_B * 1.12 * (1 + 0.012 * math.sin((t - T_SNAP) / 50))
    pts = []
    N = 60
    for i in range(int(N * 1.1) + 1):
        th = i / N * 2 * math.pi + 0.9
        kk = 1 + 0.025 * math.sin(i * 0.5)
        pts.append((HUB[0] + rr * kk * math.cos(th), HUB[1] + rr * 0.97 * kk * math.sin(th)))
    return pts


def draw_aim(layer, t):
    """Grease pencil never fades (it is opaque wax): it writes on, and is wiped off stroke-first."""
    if t < T_AIM_DRAW[0] or t >= T_SQUASH[1]:
        return
    pts, L = aim_points(t)
    w = seg(t, *T_AIM_DRAW)
    n = max(2, int(len(pts) * ease_out_cubic(w)))
    if L > R_B * 0.75 and t < T_SNAP:
        MC.grease(layer, pts[:n], MC.GP_YELLOW, 7, seed=11)
        if w >= 0.999:
            (xa, ya), (xb, yb) = pts[-4], pts[-1]
            ang = math.atan2(yb - ya, xb - xa)
            for s in (-1, 1):
                a = ang + math.pi + s * 0.5
                MC.grease(layer, [(xb, yb), (xb + 26 * math.cos(a), yb + 26 * math.sin(a))], MC.GP_YELLOW, 7, seed=14 + s)
    # valid target: a loop around the wheel writes on as the card nears it, holds, then wipes off
    if t >= T_SNAP - 160:
        pts2 = loop_points(t)
        q = ease_out_cubic(seg(t, T_SNAP - 160, T_SNAP + 40))
        wipe = ease_in_out(seg(t, T_DROP[0], T_SQUASH[1]))
        a, b = int(len(pts2) * wipe), max(2, int(len(pts2) * q))
        if b - a > 1:
            MC.grease(layer, pts2[a:b], MC.GP_YELLOW, 6, seed=5)


def aim_chip(img, t):
    if not (T_SNAP <= t < T_DROP[0] + 60):
        return
    d = ImageDraw.Draw(img)
    fa = f_ui(16, b"Bold SemiCondensed")
    s = "SPIN 9: THE MANIFEST"
    x, y = HUB[0] - fa.getlength(s) / 2 - 10, HUB[1] + R_B * 1.18
    d.rounded_rectangle([x, y, x + fa.getlength(s) + 20, y + 26], radius=6, fill=(10, 9, 15, 235))
    d.text((x + 10, y + 3), s, font=fa, fill=MC.YELLOW + (255,))


# ------------------------------------------------------------------ dissolve A: 0/1 bit stream
class BitStream:
    """The card face cut into 9 px cells. A scan front runs top -> bottom; each cell it passes decodes
    into a 0/1 glyph (white-hot for 80 ms) and then spirals clockwise into the hub along a Bezier."""

    def __init__(self, face, centre, ang, t0, t1, seed=7, cell=13):
        self.face = face
        self.centre = centre
        self.ang = ang
        self.t0, self.t1 = t0, t1
        rng = np.random.default_rng(seed)
        a = np.asarray(face, np.float32)
        h, w = a.shape[:2]
        self.cell = cell
        self.cells = []
        ca, sa = math.cos(math.radians(-ang)), math.sin(math.radians(-ang))
        for y in range(0, h, cell):
            for x in range(0, w, cell):
                blk = a[y:y + cell, x:x + cell]
                al = blk[..., 3].mean() / 255
                if al < 0.35:
                    continue
                col = (blk[..., :3] * blk[..., 3:] / 255).sum(axis=(0, 1)) / max(1, blk[..., 3].sum() / 255)
                lum = col.max() / 255
                white = col.min() > 200
                gcol = (250, 248, 240) if white else tuple(int(min(255, v * (0.55 + 0.6 * lum) + 20)) for v in TYPE_COL)
                lx, ly = x + cell / 2 - w / 2, y + cell / 2 - h / 2
                sx = centre[0] + lx * ca - ly * sa
                sy = centre[1] + lx * sa + ly * ca
                rel = t0 + (t1 - t0) * (y / h) + rng.random() * 70
                travel = 260 + rng.random() * 170
                ch = "01"[int(rng.random() < 0.5)]
                # clockwise swirl: control point = start rotated +70 deg about the hub, pulled in
                vx, vy = sx - HUB[0], sy - HUB[1]
                th = math.radians(55 + rng.random() * 35)
                kr = 1.5 + 0.8 * rng.random()  # swing out over the slices, then dive into the hub
                cx = HUB[0] + (vx * math.cos(th) - vy * math.sin(th)) * kr + 40 * math.cos(th)
                cy = HUB[1] + (vx * math.sin(th) + vy * math.cos(th)) * kr + 40 * math.sin(th)
                end = (HUB[0] + rng.normal(0, 6), HUB[1] + rng.normal(0, 6))
                self.cells.append(dict(x=x, y=y, s=(sx, sy), c=(cx, cy), e=end, rel=rel, tr=travel, ch=ch, col=gcol,
                                       px=14 + rng.random() * 6, flip=rng.random() * 300))
        self.h, self.w = h, w

    def arrivals(self, t):
        return sum(1 for c in self.cells if t >= c["rel"] + 40 + c["tr"])

    def front_y(self, t):
        return self.h * seg(t, self.t0, self.t1)

    def card_left(self, t):
        """The face with already-decoded cells cut out, plus a bright scan line at the front."""
        m = np.asarray(self.face.split()[3], np.float32).copy()
        for c in self.cells:
            if t >= c["rel"]:
                m[c["y"]:c["y"] + self.cell, c["x"]:c["x"] + self.cell] = 0
        out = self.face.copy()
        out.putalpha(Image.fromarray(m.astype(np.uint8)))
        if self.t0 <= t <= self.t1 + 80:
            fy = int(self.front_y(t))
            d = ImageDraw.Draw(out)
            ln = Image.new("RGBA", out.size, (0, 0, 0, 0))
            dl = ImageDraw.Draw(ln)
            dl.rectangle([0, fy - 1, self.w, fy + 2], fill=(255, 250, 220, 255))
            for k in range(1, 5):  # faint scan lines trailing below the front
                dl.line([(0, fy + 5 * k), (self.w, fy + 5 * k)], fill=TYPE_COL + (int(110 / k),), width=1)
            ln.putalpha(Image.fromarray(np.minimum(np.asarray(ln.split()[3]), m.astype(np.uint8) | 0).astype(np.uint8)))
            out.alpha_composite(ln)
        return out

    def draw(self, layer, t):
        for c in self.cells:
            if t < c["rel"]:
                continue
            age = t - c["rel"]
            if age < 40:  # decode in place
                p = c["s"]
                FX.paste_c(layer, FX.glyph(c["ch"], c["px"], c["col"], core=1.0), p[0], p[1])
                continue
            q = (age - 40) / c["tr"]
            if q >= 1:
                continue
            ch = c["ch"] if int((age + c["flip"]) / 90) % 2 == 0 else ("1" if c["ch"] == "0" else "0")
            core = max(0.0, 1 - age / 80)
            px = lerp(c["px"], 7, q)
            sink = 1 - seg(q, 0.7, 1.0)  # absorbed by the hub: no pile-up
            for k, (lagq, al) in enumerate(((0, 1.0), (0.08, 0.45), (0.16, 0.2))):
                qq = max(0.0, q - lagq) ** 1.5
                p = bez(c["s"], c["c"], c["e"], qq)
                FX.paste_c(layer, FX.glyph(ch, px, c["col"], core=core if k == 0 else 0, outline=(k == 0)), p[0], p[1], alpha=al * sink)


# ------------------------------------------------------------------ dissolve B: scanline decode wipe
def dissolve_B(layer, face, centre, ang, p, seed=3):
    """Rows behind the front become lines of streaming code, squeeze to bright 2 px scan lines and
    retract along the row into a beam that bends to the hub."""
    rng = np.random.default_rng(seed)
    w, h = face.size
    loc = Image.new("RGBA", (w + 260, h + 40), (0, 0, 0, 0))
    ox, oy = 130, 20
    fy = h * min(1, p / 0.7)
    rest = face.copy()
    m = np.asarray(rest.split()[3]).copy()
    m[:int(fy)] = 0
    rest.putalpha(Image.fromarray(m))
    loc.alpha_composite(rest, (ox, oy))
    d = ImageDraw.Draw(loc)
    f = P.mono(9)
    for row in range(0, int(fy), 6):
        age = (fy - row) / h  # 0 at the front
        bits = "".join("01"[int(v)] for v in rng.integers(0, 2, 30))
        if age < 0.12:  # fresh decode: code text in the type colour
            sh = int(rng.normal(0, 3) + age * 120)
            d.text((ox + sh, oy + row - 2), bits, font=f, fill=TYPE_COL + (255,))
        else:
            ln = max(4, int(w * (1 - (age - 0.12) * 1.6)))  # the line retracts towards the right edge
            x0 = ox + w - ln + int(age * 60)
            col = (255, 240, 200, int(255 * max(0.2, 1 - age)))
            d.line([(x0, oy + row), (x0 + ln, oy + row)], fill=col, width=2)
    d.rectangle([ox, oy + fy - 1, ox + w, oy + fy + 1], fill=(255, 252, 230, 255))
    loc = loc.rotate(ang, resample=Image.BICUBIC, expand=True)
    layer.alpha_composite(loc, (int(centre[0] - loc.width / 2), int(centre[1] - loc.height / 2)))
    # the beam: from the card's right edge to the hub
    if p > 0.2:
        dd = ImageDraw.Draw(layer)
        a0 = (centre[0] + w * 0.5, centre[1] - h * 0.2 + h * 0.5 * min(1, p))
        pts = [bez(a0, (centre[0] + w * 0.9, centre[1] + h * 0.1), HUB, s) for s in np.linspace(0, 1, 20)]
        dd.line(pts, fill=TYPE_COL + (220,), width=3)


# ------------------------------------------------------------------ dissolve C: glyph-pixel crumble
def dissolve_C(layer, face, centre, ang, p, seed=5):
    """The face pixelates (blocks 4 -> 14 px), blocks turn into 0/1 tiles, crumble with gravity, and
    are pulled into the hub."""
    rng = np.random.default_rng(seed)
    w, h = face.size
    bs = int(lerp(4, 14, min(1, p / 0.35)))
    small = face.resize((max(1, w // bs), max(1, h // bs)), Image.BILINEAR)
    a = np.asarray(small, np.float32)
    ca, sa = math.cos(math.radians(-ang)), math.sin(math.radians(-ang))
    fall = max(0.0, (p - 0.35) / 0.65)
    for yy in range(a.shape[0]):
        for xx in range(a.shape[1]):
            al = a[yy, xx, 3] / 255
            if al < 0.4:
                continue
            col = tuple(int(v) for v in a[yy, xx, :3])
            lx = (xx + 0.5) * bs - w / 2
            ly = (yy + 0.5) * bs - h / 2
            delay = rng.random() * 0.4 + (1 - yy / a.shape[0]) * 0.2
            q = max(0.0, fall - delay) / (1 - delay + 1e-6)
            lx += rng.normal(0, 30) * q
            ly += 160 * q * q
            sx = centre[0] + lx * ca - ly * sa
            sy = centre[1] + lx * sa + ly * ca
            if q > 0.55:  # pulled into the hub
                k = ease_in_cubic((q - 0.55) / 0.45)
                sx, sy = lerp(sx, HUB[0], k), lerp(sy, HUB[1], k)
            tile = Image.new("RGBA", (bs, bs), col + (255,))
            if p > 0.3:
                g = FX.glyph("01"[int(rng.random() < 0.5)], bs * 1.1, (20, 16, 10), outline=False)
                tile.alpha_composite(g.resize((bs, bs), Image.BILINEAR))
            FX.paste_c(layer, tile, sx, sy, alpha=1 - 0.6 * q, angle=rng.normal(0, 40) * q)


# ------------------------------------------------------------------ spin
def spin_rot(t):
    p = seg(t, *T_SPIN)
    return SPIN_DEG * ease_out_back(p, 1.25) if p < 1 else SPIN_DEG


def tick_trail(layer, t):
    """Yellow arc on the telemetry ring from the pointer back to where the old pointer slice started:
    the distance travelled, with one notch per tick. Fades after landing."""
    if t < T_SPIN[0]:
        return
    rot = spin_rot(t)
    al = 1 - seg(t, T_SPIN[1] + 100, T_SPIN[1] + 600)
    if al <= 0:
        return
    d = ImageDraw.Draw(layer)
    rr = R_B * 1.075
    # PIL angles: -90 = top, clockwise positive; the old pointer slice has travelled -90 -> -90 + rot
    d.arc([HUB[0] - rr, HUB[1] - rr, HUB[0] + rr, HUB[1] + rr], -90, -90 + rot, fill=MC.GP_YELLOW + (int(230 * al),), width=7)
    n = int(rot // 12 + 1e-6)
    for k in range(1, min(9, n) + 1):
        th = math.radians(-90 + k * 12)
        x0, y0 = HUB[0] + (rr - 10) * math.cos(th), HUB[1] + (rr - 10) * math.sin(th)
        x1, y1 = HUB[0] + (rr + 10) * math.cos(th), HUB[1] + (rr + 10) * math.sin(th)
        d.line([(x0, y0), (x1, y1)], fill=(255, 250, 220, int(255 * al)), width=3)
    # tick counter beside the blade
    f = f_num(30)
    s = "%d / 9" % min(9, n)
    d.text((HUB[0] + 64, HUB[1] - R_B * 1.42), s, font=f, fill=MC.YELLOW + (int(255 * al),), stroke_width=2, stroke_fill=MC.INK + (int(255 * al),))


def hub_charge(layer, t, arrivals, total):
    """Hub glow grows with each arrival; a ring snaps out when the spin starts."""
    d = ImageDraw.Draw(layer)
    if T_DISSOLVE[0] < t < T_SPIN[0] + 200:
        k = arrivals / max(1, total)
        r = R_B * 0.37
        a = int(150 * k * (1 - seg(t, T_SPIN[0], T_SPIN[0] + 200)))
        d.ellipse([HUB[0] - r, HUB[1] - r, HUB[0] + r, HUB[1] + r], outline=TYPE_COL + (a,), width=int(4 + 10 * k))
    if T_HUB[0] <= t <= T_HUB[1] + 120:
        q = seg(t, T_HUB[0], T_HUB[1] + 120)
        r = R_B * lerp(0.37, 0.9, ease_out_cubic(q))
        d.ellipse([HUB[0] - r, HUB[1] - r, HUB[0] + r, HUB[1] + r], outline=(255, 245, 210, int(200 * (1 - q))), width=5)


# ------------------------------------------------------------------ frame
_STREAM = {}


def stream():
    if "a" not in _STREAM:
        face = big_face()
        _STREAM["a"] = BitStream(face, SLAP_C, SLAP_ANG, *T_DISSOLVE)
    return _STREAM["a"]


def frame(t, style="A"):
    # wheel (spinning: real renders, blurred by angular velocity)
    if T_SPIN[0] <= t < T_SPIN[1] + 40:
        rot = spin_rot(t)
        v = (spin_rot(t) - spin_rot(t - FX.DT)) if t > T_SPIN[0] else 0
        rr = round(rot * 2) / 2
        if seg(t, *T_SPIN) > 0.82:
            img = P.scene(boss_sprite=P.spin_sprite(rr, abs(v) * 0.5, ss=2))
        else:
            img = P.scene(boss_sprite=P.spin_sprite(rr, abs(v) * 0.6, ss=1))
    elif t >= T_SPIN[1] + 40:
        img = P.scene(SPIN_DEG)
    else:
        img = P.scene(0.0)
    paid = t >= T_SQUASH[0]
    hov = T_HOVER[0] <= t < T_SQUASH[0]
    P.hud(img, ram=3 if paid else 5, ram_spend=2 if hov else 0, ram_label="-2 on HEAVY SPIN" if hov else "")
    P.stickers(img)
    draw_hand(img, t)
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    st = card_state(t)
    if not st.get("dissolving"):
        gl = seg(t, T_SQUASH[0], T_SQUASH[0] + 160) if T_SQUASH[0] <= t <= T_SQUASH[0] + 160 else None
        draw_card(img, st, gloss_t=gl)
        if T_SQUASH[0] <= t < T_SQUASH[0] + 120:  # contact ring
            q = seg(t, T_SQUASH[0], T_SQUASH[0] + 120)
            d = ImageDraw.Draw(fx)
            r = lerp(150, 230, ease_out_cubic(q))
            d.ellipse([SLAP_C[0] - r, SLAP_C[1] - r * 1.15, SLAP_C[0] + r, SLAP_C[1] + r * 1.15], outline=(255, 255, 255, int(150 * (1 - q))), width=4)
    else:
        bs = stream()
        if style == "A":
            left = bs.card_left(t)
            if left.getbbox():
                FX.place(img, left, SLAP_C[0], SLAP_C[1], 1, 1, SLAP_ANG, shadow=((2, 3), 2, 0.7))
            bs.draw(fx, t)
        elif style == "B":
            dissolve_B(fx, big_face(), SLAP_C, SLAP_ANG, seg(t, T_DISSOLVE[0], T_DISSOLVE[1] + 200))
        elif style == "C":
            dissolve_C(fx, big_face(), SLAP_C, SLAP_ANG, seg(t, T_DISSOLVE[0], T_DISSOLVE[1] + 260))
        hub_charge(fx, t, bs.arrivals(t), len(bs.cells))
    tick_trail(fx, t)
    # emissive FX light the screen around them (light spill), then composite them on top
    if fx.getbbox():
        img = FX.glow_add(img, fx, 5, 22, 0.55)
        img.alpha_composite(fx)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw_aim(ov, t)
    img.alpha_composite(ov)
    aim_chip(img, t)
    cur, pressed = cursor_at(t)
    if t < T_DROP[0] + 500:
        FX.cursor(img, cur[0], cur[1], pressed)
    return img


KEYS = [
    (200, "01 IDLE", ["Hand cards bob 2 px (2.4 s loop), corner", "curl breathes 0.02-0.04."]),
    (760, "02 HOVER", ["Lift 100 px + scale 1.36, ease-out-back;", "peel corner lifts to 0.17, shadow grows."]),
    (1000, "03 PEEL OFF", ["Press: the fold sweeps to 0.28, then pops", "free (x1.1); a liner outline stays behind."]),
    (1360, "04 DRAG / AIM", ["Card trails the cursor (spring, tilt by", "speed); grease line writes on to the wheel."]),
    (1800, "05 SLAP", ["Drop 80 ms ease-in, squash 1.13 / 0.86,", "shadow snaps to 2 px, contact ring, shine."]),
    (2120, "06 DISSOLVE (A)", ["Scan front top->bottom 300 ms; cells decode", "to 0/1 glyphs, white-hot for 80 ms."]),
    (2400, "07 STREAM IN", ["Glyphs spiral clockwise into the hub", "(ease-in 260-430 ms); hub charges."]),
    (2880, "08 SPIN 9", ["Ring snaps, wheel spins 108 deg (ease-out-", "back), blur by speed, 9-tick trail."]),
]


def main():
    frames, durs = [], []
    key_t = {k[0]: k for k in KEYS}
    crops = {}
    CROP = (940, 236, 1760, 1080)
    times = list(range(0, T_END, int(FX.DT)))
    for t in times:
        img = frame(t)
        frames.append(img.convert("RGB").resize((960, 540), Image.LANCZOS))
        durs.append(int(FX.DT))
        if t in key_t:
            crops[t] = img.convert("RGB").crop(CROP)
            if t == 2880:
                img.convert("RGB").save(os.path.join(P.SCR, "cp_full_2880.png"))
        if t % 400 == 0:
            print("t", t, flush=True)
    durs[-1] = 900
    size = FX.save_gif(frames, durs, os.path.join(OUT, "card_play.gif"))
    print("gif", size // 1024, "KB", flush=True)
    for i, f in enumerate(frames[::6]):
        f.save(os.path.join(P.SCR, "cp_f%03d.png" % (i * 6)))
    # dissolve options: three frames each, 1:1 crops around the slapped card
    OC = (SLAP_C[0] - 170, SLAP_C[1] - 190, SLAP_C[0] + 170, SLAP_C[1] + 190)
    opts = []
    for style, ts, name, lines in (
            ("A", (2020, 2140, 2300), "A  BIT STREAM  (picked)", ["cells decode to 0/1 and spiral into the hub;", "reads as 'the card's data enters the wheel'"]),
            ("B", (2020, 2140, 2300), "B  SCANLINE DECODE WIPE", ["rows turn to code, squeeze to scan lines,", "retract into one beam; calm, very legible"]),
            ("C", (2020, 2160, 2340), "C  GLYPH-PIXEL CRUMBLE", ["mosaic -> 0/1 tiles that crumble and get", "sucked in; most physical, busiest"])):
        row = []
        for t in ts:
            row.append(frame(t, style).convert("RGB").crop(OC))
        opts.append((style, ts, name, lines, row))
    cw, chh = OC[2] - OC[0], OC[3] - OC[1]
    gap = 10
    bw = 3 * cw + 2 * gap
    ex = Image.new("RGB", (3 * bw + 2 * 40, chh + 120), (14, 13, 20))
    d = ImageDraw.Draw(ex)
    for k, (style, ts, name, lines, row) in enumerate(opts):
        x0 = k * (bw + 40)
        d.text((x0, 0), name, font=f_num(34), fill=(255, 214, 64) if style == "A" else (255, 255, 255))
        for j, im in enumerate(row):
            ex.paste(im, (x0 + j * (cw + gap), 46))
            d.text((x0 + j * (cw + gap) + 6, 50), "+%d ms" % (ts[j] - T_DISSOLVE[0]), font=P.mono(18), fill=(255, 214, 64))
        for i, ln in enumerate(lines):
            d.text((x0, 46 + chh + 8 + i * 26), ln, font=f_ui(20, b"SemiBold"), fill=(200, 200, 214))
    cells = []
    for t, lab, caps in KEYS:
        cells.append((crops[t], lab, "%d ms" % t, caps))
    FX.storyboard(cells, os.path.join(OUT, "card_play_storyboard.png"),
                  "CARD PLAY  -  sticker lifecycle (HEAVY SPIN onto THE MANIFEST)",
                  "1:1 crops of the 1920x1080 combat screen (D4). Timings are from the start of the clip (hover begins at 560 ms). Dissolve options below: same slap, three decodes.",
                  cols=4, extra=ex,
                  note_lines=["layer order (back to front): city + spill | wheels | HUD | overlay stickers | hand | moving card + shadow | FX glyphs (additive glow) | grease pencil | cursor",
                              "reduce effects: no peel/curl, card slides to the wheel (150 ms) and fades out with a 1-frame white outline; no glyphs; spin plays at 2x with no blur."])
    print("done", flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "test":
        style = "A"
        for a in sys.argv[2:]:
            if a in "ABC":
                style = a
                continue
            frame(int(a), style).convert("RGB").save(os.path.join(P.SCR, "cpt_%s_%s.png" % (style, a)))
            print("test", a, flush=True)
    else:
        main()
