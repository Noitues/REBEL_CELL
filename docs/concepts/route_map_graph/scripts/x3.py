"""Family X, variant X3 "Neon street" (from the designer's mockup designer_mockup_X3.webp: the idea, not its rendering).

python x3.py [rest hover gif]
A high 3/4 view straight down street i=26 (Blender, same city kit: render_street.py x3). The net layer draws the city
as neon line-art on black: every building's silhouette and face breaks in one of four neon inks (teal, pink, amber,
violet; picked per building, seeded), faint floor lines on the facades, the streets as thin kerb lines. The run winds
through the blocks at street level with right-angle turns, branching and rejoining: walked = solid lime, the two
options = thick orange, the rest of the future = dashed white side lanes, the past and cut-off = grey. Node stickers
are neon signs on their buildings' roofs; the TARGET is the red pencil at the far end.
Hover (option 2, the Rack): its branch fills to a thick hot lane (white core, orange glow) racing from the fork, and
the outlines of the buildings along it light up, node buildings in their type colour.
All randomness is seeded.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import frame as FR  # noqa: E402
import rgraph as G  # noqa: E402
import gbuf as GB  # noqa: E402
import kit44 as KT  # noqa: E402
import ui31 as K  # noqa: E402
import avariants as AV  # noqa: E402
import street as ST  # noqa: E402
os.environ.setdefault("NET36", "net_scope.json")
import layout36 as L  # noqa: E402
import citydata as CD  # noqa: E402

W, H = FR.W, FR.H
TAG = "x3_key"
HOVER = "L4_1"
INKS = [(64, 232, 214), (255, 76, 170), (255, 186, 64), (170, 110, 255)]      # teal, pink, amber, violet

NODE = {   # node: street point (lots) the lane reaches; the sign goes on the nearest building's roof
    "L3_0": (26.5, 15.5), "L4_0": (21.5, 12.6), "L4_1": (26.5, 12.4),
    "L5_0": (21.5, 7.6), "L5_1": (32.5, 7.6), "L6_0": (24.0, 4.5), "L6_1": (32.5, 1.6), "L7_0": (26.5, -0.5),
    "L3_1": (21.5, 17.2), "L3_2": (31.0, 15.5), "L4_2": (32.5, 12.6), "L5_2": (35.0, 7.6),
}
SIDE = {"L4_0": (-0.9, 0.0), "L4_1": (0.9, 0.0), "L5_0": (-0.9, 0.0), "L5_1": (0.9, 0.0), "L6_0": (0.0, 0.9),
        "L6_1": (0.9, 0.0), "L7_0": (0.0, -0.9), "L3_0": (0.9, 0.9), "L3_1": (-0.9, 0.0), "L3_2": (0.0, 0.9),
        "L4_2": (0.9, 0.0), "L5_2": (0.9, 0.0)}
LANES = {
    ("L3_0", "L4_0"): [(26.5, 15.5), (21.5, 15.5), (21.5, 12.6)],
    ("L3_0", "L4_1"): [(26.5, 15.5), (26.5, 12.4)],
    ("L4_0", "L5_0"): [(21.5, 12.6), (21.5, 7.6)],
    ("L4_1", "L5_0"): [(26.5, 12.4), (26.5, 10.5), (21.5, 10.5)],
    ("L4_1", "L5_1"): [(26.5, 12.4), (26.5, 10.5), (32.5, 10.5), (32.5, 7.6)],
    ("L5_0", "L6_0"): [(21.5, 7.6), (21.5, 4.5), (24.0, 4.5)],
    ("L5_1", "L6_0"): [(32.5, 7.6), (32.5, 4.5), (24.0, 4.5)],
    ("L5_1", "L6_1"): [(32.5, 7.6), (32.5, 1.6)],
    ("L6_0", "L7_0"): [(24.0, 4.5), (26.5, 4.5), (26.5, -0.5)],
    ("L6_1", "L7_0"): [(32.5, 1.6), (32.5, -0.5), (26.5, -0.5)],
    ("L3_2", "L4_2"): [(31.0, 15.5), (32.5, 15.5), (32.5, 12.6)],
    ("L4_2", "L5_2"): [(32.5, 12.6), (32.5, 10.5), (35.0, 10.5), (35.0, 7.6)],
    ("L2_x", "L3_1"): [(21.5, 19.5), (21.5, 17.2)],
}
WALKED = [(26.5, 21.5), (26.5, 15.5)]
_C = {}


def gb():
    if "g" not in _C:
        _C["g"] = GB.GBuf(TAG)
    return _C["g"]


# ---------------------------------------------------------------- the neon line city
def city(lit=None, t=1.0):
    """lit: {building index: (colour, k)} buildings whose outlines light up (hover)."""
    g = gb()
    img = np.zeros((H, W, 3), np.float32) + np.array([0.012, 0.01, 0.025], np.float32)
    ink = np.array(INKS, np.float32) / 255.0
    rng = np.random.RandomState(7)
    lut = rng.randint(0, len(INKS), 1 << 16)
    col = ink[lut[g.idc % (1 << 16)]]
    zf = np.clip(g.z / 40.0, 0, 1)
    e = g.edge.astype(np.float32)
    em = e[..., None] * col * (0.55 + 0.25 * zf)[..., None]
    floors = g.wall & (np.mod(g.z - 1.6, 1.9) < 0.14) & (g.z > 1.5)
    em += (floors * 0.22)[..., None] * col
    img[g.bld] = np.array([0.018, 0.014, 0.034], np.float32)
    # streets: thin kerb lines where street cells meet blocks (lot space)
    lx, ly = L.lots(g.gpos[..., 0], g.gpos[..., 1])
    st = {(s["i"], s["j"]) for s in CD.load()["streets"]}
    fi, fj = np.floor(lx).astype(int), np.floor(ly).astype(int)
    keys = fi * 10000 + fj
    sk = np.array(sorted(i * 10000 + j for i, j in st))
    isst = np.isin(keys, sk) & ~g.bld
    m8 = Image.fromarray((isst * 255).astype(np.uint8))
    kerb = (np.asarray(m8.filter(ImageFilter.FIND_EDGES)) > 0) & ~g.bld
    em += (kerb * 0.28)[..., None] * np.array([0.5, 0.55, 0.85], np.float32)
    if lit:
        for b, (c, k) in lit.items():
            m = (g.idc == b) & g.bld
            cc = np.array(c, np.float32) / 255.0
            em += ((g.edge & m) * 1.25 * k)[..., None] * cc
            em += ((floors & m) * 0.6 * k)[..., None] * cc
            em += ((g.wall & m) * 0.06 * k)[..., None] * cc
    out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    return GB.add_emission(out, em, glow_r=(3, 10), glow_k=(0.7, 0.45))


# ---------------------------------------------------------------- lanes
def lane(cv, cam, pts, col, width, a=1.0, dash=None, core=None):
    P = ST.ground_poly(cam, pts, step=0.2)
    if len(P) < 2:
        return
    d = ImageDraw.Draw(cv)
    S = cv.width / W
    acc = 0.0
    for (x0, y0, z0), (x1, y1, z1) in zip(P, P[1:]):
        k = cam.k / ((z0 + z1) / 2) / 11.0
        w = max(2.0, width * k)
        acc += 0.2
        if dash and (acc % (dash * 2)) > dash:
            continue
        d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=tuple(col) + (int(255 * a),), width=int(w * S))
        if core:
            d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=tuple(core) + (int(255 * a),), width=max(1, int(w * 0.35 * S)))


def sub_lane(pts, u):
    """The first fraction u of a lot polyline."""
    segs = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    tot = sum(segs) * u
    out = [pts[0]]
    for (a, b), s in zip(zip(pts, pts[1:]), segs):
        if tot >= s:
            out.append(b)
            tot -= s
        else:
            k = tot / (s or 1)
            out.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k))
            break
    return out


# ---------------------------------------------------------------- page
def build(t=None, chrome=True):
    cam = ST.Cam(TAG)
    g = gb()
    st, opts = G.states(G.WALK_MID)
    hover = t is not None
    branch = G.reach([HOVER]) if hover else set()
    # signs: each node's building (nearest to the side of its street point) and its roof point
    signs = {}
    for i, (lx, ly) in sorted(NODE.items()):
        sx, sy = SIDE.get(i, (0.9, 0.0))
        p = cam.lot(lx + sx, ly + sy, 0.0)
        b = g.building_at(p[0], p[1], 14) if p else None
        if b is not None:
            g.set_clip(b, (p[0] - 260, p[1] - 420, p[0] + 260, p[1] + 60))
            rx, ry = g.roof_point(b)
            if ry < 250 or G.KIND.get(i) == "target":   # far or tall: a street-level plate over the lane end instead
                q = cam.lot(lx, ly, 3.0)
                rx, ry = q[0], q[1]
        else:
            q = cam.lot(lx, ly, 3.0)
            rx, ry = q[0], q[1]
        signs[i] = (b, rx, ry)
    lit = {}
    if hover:
        for i in sorted(branch):
            b = signs.get(i, (None,))[0]
            if b is not None:
                c = AV.climb_t(t, G.LAYER[i] - G.LAYER[HOVER], dur=0.2, lead=0.15, step=0.17)
                if c > 0:
                    lit[b] = (AV.TYPE_COL[G.KIND[i]], c)
        for e, pts in sorted(LANES.items()):
            if e[0] in branch | {"L3_0"} and e[1] in branch:
                sp = [(x, y) for x, y, z in ST.ground_poly(cam, pts)]
                dpt = G.LAYER[e[0]] - G.LAYER[HOVER] if e[0] in G.LAYER else -1
                c = float(np.clip((t - 0.17 * (dpt + 1)) / 0.2, 0, 1))
                for b in g.buildings_near_path(sp, rad=22, min_px=700, exclude=set(lit))[:2]:
                    if c > 0:
                        lit[b] = (FR.ORANGE, 0.5 * c)
    img = city(lit)
    # lanes
    S = 2
    cv = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    lane(cv, cam, WALKED, FR.LIME, 26, 1.0, core=(250, 255, 210))
    for e, pts in sorted(LANES.items()):
        a, b = e
        sa = "grey" if a not in st else st[a]
        sb = st.get(b, "grey")
        if sb == "grey" or sa == "grey":
            lane(cv, cam, pts, FR.GREY, 12, FR.GREY_A)
        elif a == "L3_0":
            on = hover and b == HOVER
            lane(cv, cam, pts, FR.ORANGE, 26 if not hover or on else 18, 1.0 if not hover or on else 0.7,
                 core=(255, 236, 200) if on else None)
        else:
            lane(cv, cam, pts, FR.WHITE, 12, 0.9 if not hover else 0.5, dash=0.45)
    if hover:                                       # the hovered branch fills to a hot lane, racing out from the fork
        for e, pts in sorted(LANES.items()):
            if e[0] in branch and e[1] in branch:
                dpt = G.LAYER[e[0]] - G.LAYER[HOVER]
                u = float(np.clip((t - 0.17 * (dpt + 1)) / 0.2, 0, 1))
                if u > 0:
                    lane(cv, cam, sub_lane(pts, u), FR.ORANGE, 22, 1.0, core=(255, 240, 210))
    lay = cv.resize((W, H), Image.LANCZOS)
    img = K.add_glow(img, lay.split()[3], (255, 190, 120), 10, 0.55)
    img.alpha_composite(lay)
    # neon signs: our node stickers on their roofs, a neon stem down to the roof
    order = sorted(signs, key=lambda i: signs[i][2])
    pen = None
    for i in order:
        s = st.get(i, "grey")
        if s == "walked":
            continue
        b, rx, ry = signs[i]
        q = cam.lot(*NODE[i], 0.0)
        zc = q[2] if q else 100
        px = int(max(40, min(76, 5200 / zc)))
        if G.KIND[i] == "target":
            px = int(px * 1.3)
        y = ry - px * 0.75
        colr = {"current": FR.LIME, "option": FR.ORANGE, "reach": FR.WHITE, "target": (255, 60, 70), "grey": FR.GREY}[s]
        a = 1.0 if s != "grey" else FR.GREY_A
        dd = ImageDraw.Draw(img)
        dd.line([(rx, ry), (rx, y + px / 2)], fill=colr + (int(230 * a),), width=3)
        bak = dict(FR.STICKER_PX)
        for kk in FR.STICKER_PX:
            FR.STICKER_PX[kk] = px
        img = FR.draw_node(img, i, rx, y, s, hover=(hover and i == HOVER), alpha=a)
        FR.STICKER_PX.update(bak)
        if s != "grey":
            m = Image.new("L", (W, H), 0)
            ImageDraw.Draw(m).ellipse([rx - px * 0.62, y - px * 0.62, rx + px * 0.62, y + px * 0.62], outline=255, width=3)
            img = K.add_glow(img, m, colr, 9, 0.7)
        if i in opts:
            img = FR.number_chip(img, rx - px / 2 - 10, y - px / 2 - 8, opts.index(i) + 1)
        if G.KIND[i] == "target":
            pen = FR.target_pencil(rx, y, int(px * 0.6))
        signs[i] = (b, rx, y, px)
    # the operative token at the fork
    p = cam.lot(26.5, 15.5, 0.0)
    if p:
        img = FR.RL.place_sticker(img, FR.U32.token_sd(58), p[0] + 44, p[1] - 26, angle=-10, hover=0.6)
    if hover:
        b, rx, y, px = signs[HOVER]
        img = FR.tag(img, rx + px / 2 + 14, y, HOVER, "option")
    if not chrome:
        return img if pen is None else FR.finish_pencil(img, pen)
    img = FR.dossier(img)
    img = FR.chrome_top(img, "This is their wiring. Follow the lit street, not the pretty one.")
    img = FR.route_panel(img, len(opts), None)
    if hover:
        img = FR.node_file(img, HOVER, "52 / 60 on arrival")
    img, kbox = FR.legend(img, False)
    if pen:
        img = FR.finish_pencil(img, pen)
    if hover:
        b, rx, y, px = signs[HOVER]
        img = FR.cursor(img, rx + 8, y + 8)
    return img


def gif(n=15, ms=80):
    frames = []
    for k in range(n):
        im = FR.RL.bloom(build(k / (n - 1)), 0.10, 0.84, 8).convert("RGB")
        frames.append(im.crop((280, 130, 1600, 1010)).resize((880, 587), Image.LANCZOS))
    frames += [frames[-1]] * 6
    FR.save_gif(frames, [ms] * n + [ms] * 5 + [900], os.path.join(FR.OUT, "X3_motion.gif"))


if __name__ == "__main__":
    what = sys.argv[1:] or ["rest", "hover", "gif"]
    if "rest" in what:
        FR.save(build(None), "X3_rest.png")
    if "hover" in what:
        FR.save(build(1.0), "X3_hover.png")
    if "gif" in what:
        gif()
