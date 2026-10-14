"""Family S, street level: the run as streets and alleys ahead of the operative (perspective camera, ~22 deg down,
at the fork of streets i=26 / j=15 of the same city; renders from render_street.py).

python street.py [rest hover gif]
  rest   the fork: option 1 = the left street (a fight), option 2 = the right street (the Rack); each option's
         building carries a blade sign with its node sticker; downstream nodes stand further along as smaller
         holo beacons over their roofs, the TARGET a tall red-pencilled beacon; links are ground lanes in the streets.
  hover  option 2 hovered: its street blooms up its facades (the deferred facade bloom of gbuf.py), its lane runs hot.
  gif    S_motion.gif: a step forward down the chosen (right) street, 1.5 s, 18 real Blender frames.
All randomness is seeded.
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance  # noqa: E402

import frame as FR  # noqa: E402
import rgraph as G  # noqa: E402
import gbuf as GB  # noqa: E402
import kit44 as KT  # noqa: E402
import ui31 as K  # noqa: E402
import r32ui as U32  # noqa: E402
import avariants as AV  # noqa: E402
os.environ.setdefault("NET36", "net_scope.json")
import layout36 as L  # noqa: E402

W, H = FR.W, FR.H
BL = GB.BL
HOVER = "L4_1"

# ---------------------------------------------------------------- the run on the streets (lots; z = sign height BU)
F = (26.5, 15.5)                                  # the fork (current node: the shop behind the operative)
NODE = {   # node: (lot x, lot y, sign z, kind of mount)
    "L4_0": (23.0, 16.15, 5.5, "blade"),         # option 1: down the left street, south side
    "L4_1": (27.15, 12.4, 5.5, "blade"),         # option 2: down the right street, east side
    "L5_0": (22.4, 9.6, 11.0, "beacon"),         # the merge, over the far corner
    "L5_1": (27.4, 6.8, 9.0, "beacon"),
    "L6_0": (22.4, 3.8, 12.0, "beacon"),
    "L6_1": (27.4, 1.2, 12.0, "beacon"),
    "L7_0": (19.6, -2.6, 17.0, "beacon"),
    "L4_2": (33.4, 11.6, 8.0, "beacon"),         # cut off (reachable only from the paths not taken)
    "L5_2": (33.4, 5.6, 10.0, "beacon"),
    "L3_2": (31.4, 12.4, 6.0, "beacon"),
}
LANES = {  # edge: ground polyline (lots, street centres)
    ("L3_0", "L4_0"): [F, (23.0, 15.5)],
    ("L3_0", "L4_1"): [F, (26.5, 12.4)],
    ("L4_0", "L5_0"): [(23.0, 15.5), (21.5, 15.5), (21.5, 10.5), (22.4, 10.5)],
    ("L4_1", "L5_0"): [(26.5, 12.4), (26.5, 10.5), (22.4, 10.5)],
    ("L4_1", "L5_1"): [(26.5, 12.4), (26.5, 6.8)],
    ("L5_0", "L6_0"): [(21.5, 10.5), (21.5, 4.5), (22.4, 4.5)],
    ("L5_1", "L6_0"): [(26.5, 6.8), (26.5, 4.5), (22.4, 4.5)],
    ("L5_1", "L6_1"): [(26.5, 6.8), (26.5, 1.2)],
    ("L6_0", "L7_0"): [(21.5, 4.5), (21.5, -0.5), (19.6, -0.5)],
    ("L6_1", "L7_0"): [(26.5, 1.2), (26.5, -0.5), (19.6, -0.5)],
    ("L3_2", "L4_2"): [(32.5, 12.4), (32.5, 11.6)],
    ("L4_2", "L5_2"): [(32.5, 11.6), (32.5, 5.6)],
}
WALKED_LANE = [(33.5, 15.5), (29.0, 15.5), F]      # the walked street, coming in from behind-right


class Cam:
    def __init__(self, tag):
        sc = json.load(open(os.path.join(BL, tag + "_scene.json")))
        pp = sc["cam"]["persp"]
        self.loc = np.array(pp["loc"], float)
        f = np.array(pp["look"], float) - self.loc
        self.f = f / np.linalg.norm(f)
        r = np.cross(self.f, [0, 0, 1.0])
        self.r = r / np.linalg.norm(r)
        self.u = np.cross(self.r, self.f)
        self.k = pp["lens"] / 36.0 * W

    def prj(self, p):
        d = np.array(p, float) - self.loc
        zc = d @ self.f
        if zc < 0.5:
            return None
        return (W / 2 + (d @ self.r) / zc * self.k, H / 2 - (d @ self.u) / zc * self.k, zc)

    def lot(self, lx, ly, z=0.0):
        wx, wy = L.W((lx, ly))
        return self.prj((wx, wy, z))


# ---------------------------------------------------------------- the night finish of the raw street render
def finish(tag, cam):
    b = os.path.join(BL, tag + "_")
    beauty = np.asarray(Image.open(b + "beauty_night.png").convert("RGB").resize((W, H), Image.LANCZOS), np.float32) / 255
    glow = np.asarray(Image.open(b + "glow_night.png").convert("RGB").resize((W, H), Image.LANCZOS), np.float32) / 255
    pos = GB._rs(np.load(b + "pos.npy").astype(np.float32), tag)
    sky = np.abs(pos).max(axis=2) > 3000
    dist = np.linalg.norm(pos - cam.loc[None, None, :].astype(np.float32), axis=2)
    dist[sky] = 2000
    img = beauty * np.array([0.60, 0.56, 0.74], np.float32)              # night grade, violet kept
    fog = 1 - np.exp(-dist / 260.0)
    fogc = np.array([0.10, 0.06, 0.18], np.float32)
    img = img * (1 - fog[..., None] * 0.75) + fogc * fog[..., None] * 0.75
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    skyc = np.array([0.03, 0.02, 0.07], np.float32) * (1 - yy) + np.array([0.16, 0.07, 0.22], np.float32) * yy
    img[sky] = np.broadcast_to(skyc[..., None, :] if skyc.ndim == 2 else skyc, img.shape)[sky]
    img = img + glow * 0.5
    out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    gm = Image.fromarray((np.clip(glow.max(axis=2), 0, 1) * 255).astype(np.uint8))
    out = K.add_glow(out, gm, (255, 160, 230), 10, 0.22)
    # rain: seeded thin streaks
    rng = random.Random(12)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(900):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        ln = rng.uniform(12, 34)
        d.line([(x, y), (x - ln * 0.12, y + ln)], fill=(190, 200, 255, rng.randint(18, 50)), width=1)
    out.alpha_composite(lay)
    return out


# ---------------------------------------------------------------- lanes, signs
def ground_poly(cam, pts, step=0.25):
    out = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(bx - ax, by - ay) / step))
        for k in range(n + 1):
            t = k / n
            p = cam.lot(ax + (bx - ax) * t, ay + (by - ay) * t, 0.06)
            if p:
                out.append(p)
    return out


def draw_lane(cv, cam, pts, col, a=1.0, dashed=False, w=0.9, hot=False):
    """A lane on the street ground: width in world units (perspective-correct), dashed in world units."""
    P = ground_poly(cam, pts)
    d = ImageDraw.Draw(cv)
    S = cv.width / W
    for (x0, y0, z0), (x1, y1, z1) in zip(P, P[1:]):
        k = cam.k / ((z0 + z1) / 2)
        wpx = max(1.5, w * k)
        seg = int(((z0 + z1) / 2) / 1.1) % 2 == 0 if dashed else True
        if not seg:
            continue
        d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=FR.CASING + (int(200 * a),), width=int((wpx + 4) * S))
    for (x0, y0, z0), (x1, y1, z1) in zip(P, P[1:]):
        k = cam.k / ((z0 + z1) / 2)
        wpx = max(1.0, w * k * 0.62)
        if dashed and int(((z0 + z1) / 2) / 1.1) % 2:
            continue
        d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=tuple(col) + (int(255 * a),), width=int(wpx * S))
    return P


def sign(img, cam, i, state, hover=False, alpha=1.0, number=None):
    lx, ly, z, mount = NODE[i]
    p = cam.lot(lx, ly, z)
    if p is None:
        return img, None
    x, y, zc = p
    s = max(0.38, min(1.25, 60.0 / zc))
    px = int((84 if G.KIND[i] == "target" else 66) * s)
    col = {"option": FR.ORANGE, "reach": FR.WHITE, "target": (255, 60, 70), "grey": FR.GREY}[state]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if mount == "beacon":                          # a holo beacon: a light column down to the roofs
        b = cam.lot(lx, ly, max(0.0, z - 8))
        if b:
            d.line([(x, y + px / 2), (b[0], b[1])], fill=col + (int(170 * alpha),), width=max(2, int(4 * s)))
    else:                                          # a blade sign: a bracket to the wall and a dark plate
        wpt = cam.lot(lx + (0.0 if i == "L4_0" else 0.35), ly + (0.35 if i == "L4_0" else 0.0), z)
        if wpt:
            d.line([(x, y), (wpt[0], wpt[1])], fill=(20, 18, 26, int(255 * alpha)), width=max(3, int(6 * s)))
        pw, ph = px * 0.66, px * 0.9
        d.rounded_rectangle([x - pw, y - ph, x + pw, y + ph], 10, fill=(8, 6, 14, int(230 * alpha)),
                            outline=col + (int(255 * alpha),), width=max(2, int(5 * s)))
    img.alpha_composite(lay)
    st = state if state != "target" else "target"
    if state != "grey" and alpha >= 0.99:
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).ellipse([x - px * 0.7, y - px * 0.7, x + px * 0.7, y + px * 0.7], fill=255)
        img = K.add_glow(img, m, col, int(12 * s) + 4, 0.55)
    G_KIND = G.KIND[i]
    FR.STICKER_PX_BAK = dict(FR.STICKER_PX)
    for kk in FR.STICKER_PX:
        FR.STICKER_PX[kk] = px
    img = FR.draw_node(img, i, x, y, state, hover=hover, alpha=alpha, glow=False)
    FR.STICKER_PX.update(FR.STICKER_PX_BAK)
    if number:
        img = FR.number_chip(img, x - px / 2 - 10, y - px / 2 - 8, number)
    return img, (x, y, px)


# ---------------------------------------------------------------- page
def build(t=None, tag="s_key", chrome=True):
    cam = Cam(tag)
    img = finish(tag, cam)
    gb = None
    hover = t is not None
    if hover:
        gb = _gb(tag)
        em = np.zeros((H, W, 3), np.float32)
        branch = G.reach([HOVER])
        lanes = [(e, p) for e, p in LANES.items() if e[0] in branch | {"L3_0"} and e[1] in branch]
        seen = set()
        for e, pts in sorted(lanes):
            dpt = G.LAYER[e[0]] - G.LAYER[HOVER]
            sp = [(x, y) for x, y, z in ground_poly(cam, pts)]
            if len(sp) < 2:
                continue
            ids = gb.buildings_near_path(sp, rad=40, min_px=1600, exclude=seen)[:3]
            for b in ids:
                seen.add(b)
                c = AV.climb_t(t, dpt + 1, dur=0.35, lead=0.05, step=0.16)
                em += gb.bloom(b, c * 0.7, (255, 170, 90), k=0.32, seed=4, trace=True, wash=0.18)
        for i in sorted(branch):
            if i not in NODE:
                continue
            lx, ly, z, mount = NODE[i]
            p = cam.lot(lx, ly, max(0.5, z - 9 if mount == "beacon" else 3.0))
            if not p:
                continue
            b = gb.building_at(p[0], p[1] + 10, 16)
            if b is not None and b not in seen:
                seen.add(b)
                c = AV.climb_t(t, G.LAYER[i] - G.LAYER[HOVER], dur=0.35, lead=0.12, step=0.16)
                em += gb.bloom(b, c, AV.TYPE_COL[G.KIND[i]], k=1.5, seed=3, wash=0.5)
        img = GB.add_emission(img, em)
    # lanes
    S = 2
    cv = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    draw_lane(cv, cam, WALKED_LANE, FR.LIME, 1.0, False, 1.1)
    branch = G.reach([HOVER]) if hover else set()
    for e, pts in sorted(LANES.items()):
        a, b = e
        if a == "L3_0":
            draw_lane(cv, cam, pts, FR.ORANGE, 1.0 if (not hover or b == HOVER) else 0.75, True, 1.2)
        elif b in ("L4_2", "L5_2"):
            draw_lane(cv, cam, pts, FR.GREY, FR.GREY_A, False, 0.7)
        else:
            on = hover and a in branch and b in branch
            draw_lane(cv, cam, pts, FR.ORANGE if on else FR.WHITE, 1.0 if (on or not hover) else 0.6, True, 0.9 if on else 0.75)
    lay = cv.resize((W, H), Image.LANCZOS)
    img = K.add_glow(img, lay.split()[3], (255, 200, 150), 8, 0.35)
    img.alpha_composite(lay)
    # signs, far to near
    st, opts = G.states(G.WALK_MID)
    order = sorted(NODE, key=lambda i: -(Cam.lot(cam, NODE[i][0], NODE[i][1], NODE[i][2]) or (0, 0, 1e9))[2])
    boxes = {}
    for i in order:
        s = st[i]
        if s == "current" or s == "walked":
            continue
        a = FR.GREY_A if s == "grey" else 1.0
        num = (opts.index(i) + 1) if i in opts else None
        img, bx = sign(img, cam, i, s, hover=(hover and i == HOVER), alpha=a, number=num)
        boxes[i] = bx
    # the operative token at the fork (you are here)
    p = cam.lot(F[0] + 0.2, F[1] + 0.2, 0.0)
    if p:
        img = FR.RL.place_sticker(img, U32.token_sd(58), p[0], p[1] - 30, angle=-10, hover=0.6)
    pen = None
    if boxes.get("L7_0"):
        x, y, px = boxes["L7_0"]
        pen = FR.target_pencil(x, y, int(px * 0.62))
    if hover and boxes.get(HOVER):
        x, y, px = boxes[HOVER]
        img = FR.tag(img, x + px / 2 + 16, y, HOVER, "option")
    if not chrome:
        return img if pen is None else FR.finish_pencil(img, pen)
    img = rear_view(img)
    img = FR.chrome_top(img, "Two streets. Left is a fight. Right is the Rack, and it's lit up like a target.")
    img = FR.route_panel(img, 2, None)
    if hover:
        img = FR.node_file(img, HOVER, "52 / 60 on arrival")
    img, kbox = FR.legend(img, False)
    if pen:
        img = FR.finish_pencil(img, pen)
    if hover and boxes.get(HOVER):
        x, y, px = boxes[HOVER]
        img = FR.cursor(img, x + 8, y + 8)
    return img


def rear_view(img):
    """S keeps the full graph rule with a rear-view strip: the walked path behind you (lime) and what you cut off
    (grey count), plus the dossier folded to a tab (the left street needs the screen)."""
    box = (16, 138, 262, 252)
    img = KT.term(img, box, "BEHIND YOU", accent=FR.LIME, seed=51)
    xs = [44, 104, 164]
    for x, k in zip(xs, ("router", "terminal", "modem")):
        ic = U32.icon(k, 40)
        img.alpha_composite(ic, (x - 20, 182))
    d = K.BD(img)
    for a, b in zip(xs, xs[1:]):
        d.line([(a + 22, 202), (b - 22, 202)], fill=FR.LIME + (255,), width=4)
    d.ellipse([164 - 25, 202 - 25, 164 + 25, 202 + 25], outline=FR.LIME + (255,), width=3)
    K.text(img, (200, 194), "8 CUT", K.F(K.MONO, 13), (160, 156, 176), "lm", 0.6)
    K.text(img, (200, 212), "OFF", K.F(K.MONO, 13), (160, 156, 176), "lm", 0.6)
    K.text(img, (24, 238), "full map: GRID VIEW [G]", K.F(K.MONO, 12), (150, 200, 210), "lm", 0.4)
    # the dossier, folded: name strip only (opens on hover)
    img = KT.term(img, (16, 262, 262, 300), None, accent=(255, 140, 26), header=False, seed=52, chamfer=8)
    K.text(img, (28, 281), "CELL-9  BREAKER  R1   [D] FILE", K.F(K.MONO, 13), (240, 220, 200), "lm", 0.5)
    return img


_GBS = {}


def _gb(tag):
    if tag not in _GBS:
        _GBS[tag] = GB.GBuf(tag)
    return _GBS[tag]


def gif(n=18, ms=83):
    """A step forward down the right-hand street: real camera frames; the lanes / signs reprojected per frame."""
    frames = []
    for k in range(n):
        tag = "s_walk%02d" % k
        im = build(1.0, tag, chrome=False).convert("RGB").resize((960, 540), Image.LANCZOS)
        frames.append(im)
    frames = [frames[0]] * 4 + frames + [frames[-1]] * 8
    FR.save_gif(frames, [ms] * (len(frames) - 1) + [900], os.path.join(FR.OUT, "S_motion.gif"))


if __name__ == "__main__":
    what = sys.argv[1:] or ["rest", "hover", "gif"]
    if "rest" in what:
        FR.save(build(None), "S_rest.png")
    if "hover" in what:
        FR.save(build(1.0), "S_hover.png")
    if "gif" in what:
        gif()
