"""F Rebel Tag: the world (anchors, beam paths in frame px), corp AR layers and the Cell's layers."""
import math, json
import numpy as np
from ft_lib import *
from ft_marks import *

_D = load_json("default", "forecast")


def build_world():
    w = {}
    anch = {}
    stubs = {}
    beams = {b["name"]: b for b in _D["beams"]}
    for name in ("known0", "known1", "cand0"):
        b = beams[name]
        sp = spurs(b["polyline"])
        for (i, base, tip), sid in zip(sp, b["site_path"][1:-1]):
            anch.setdefault(sid, tip)
            stubs.setdefault(sid, (W2S(base), W2S(tip)))
    anch["t2_intel"] = beams["hunter0"]["polyline"][0]
    anch["t3_core"] = beams["hunter1"]["polyline"][0]
    anch["home"] = beams["known0"]["polyline"][-1]
    anch["core"] = beams["known0"]["polyline"][0]
    # t1_d: end of its home link
    for l in _D["links"]:
        if l["a"] == "home" and l["b"] == "t1_d":
            anch["t1_d"] = l["polyline"][-1]
    w["anchor"] = {k: W2S(v) for k, v in anch.items()}
    w["stub"] = stubs
    w["paths"] = {}
    for n, b in beams.items():
        w["paths"][n] = [W2S(p) for p in clean_path(b["polyline"])]
        w["paths"][n + "_raw"] = [W2S(p) for p in b["polyline"]]
    w["sites"] = {s["id"]: s for s in _D["sites"]}
    w["site_path"] = {n: b["site_path"] for n, b in beams.items()}
    # corp lattice (all links with geometry)
    w["links"] = [[W2S(p) for p in clean_path(l["polyline"])] for l in _D["links"] if len(l["polyline"]) > 1]
    return w


WORLD = build_world()
A = WORLD["anchor"]

LANE = {"known0": -9, "known1": 9, "cand0": 0, "cand1": 0, "cand2": 0}


def lane_path(name, lane=None):
    return offset_path(WORLD["paths"][name], LANE[name] if lane is None else lane)


def site_s(name, sid):
    """arclength along path `name` (frame px) nearest the anchor of site sid"""
    return nearest_s(WORLD["paths"][name], A[sid])


# ---------------------------------------------------------------------------------- corp AR layers
def corp_lattice(alpha=70):
    L = Layer()
    for pl in WORLD["links"]:
        for p in resample(pl, 13)[::2]:
            pass
        rs = resample(pl, 10)
        for k in range(0, len(rs) - 1, 2):
            L.line([rs[k], rs[k + 1]], CORP, 1.6, a=alpha, joints=False)
    return L


def scan_band(base, y, h=90, strength=0.22, x0=0, x1=W):
    """AR 'computing' sweep: bright thin line and a faded scanline band behind it"""
    a = np.asarray(base.convert("RGB")).astype(np.float32) / 255
    yy = np.arange(H, dtype=np.float32)[:, None]
    band = np.exp(-((yy - y) / h) ** 2) * (yy <= y + 4)
    xs = np.zeros((1, W), np.float32)
    xs[:, x0:x1] = 1
    lines = (0.5 + 0.5 * np.sin(yy * 1.9)) ** 3
    k = band * xs
    a = a + (k * (0.10 + 0.14 * lines))[..., None] * np.array([.55, .8, 1.0], np.float32)
    edge = np.exp(-((yy - y) / 2.0) ** 2) * xs
    a = a + edge[..., None] * np.array([.7, .9, 1.0], np.float32) * .4
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def fog_band(base, names, seed=4, strength=1.0, lock=True):
    """the sealed route: a corp censor band (black bar + static blocks + caution-tape edges) along the three routes"""
    rng = np.random.default_rng(seed)
    L = Layer()
    for n in names:
        L.line(WORLD["paths"][n], INK, 28, a=int(235 * strength))
    out = commit(base, L)
    L = Layer()
    for n in names:
        pts = WORLD["paths"][n]
        cl = cum(pts)
        s = 0
        while s < cl[-1]:
            ln = rng.uniform(5, 16)
            p, ang = point_at(pts, s + ln / 2, cl)
            d = (math.cos(ang), math.sin(ang))
            nrm = (-d[1], d[0])
            for _ in range(2):
                off = rng.uniform(-11, 11)
                g = int(rng.choice([55, 80, 105, 140, 235]))
                q = (p[0] + nrm[0] * off, p[1] + nrm[1] * off)
                L.line([(q[0] - d[0] * ln / 2, q[1] - d[1] * ln / 2), (q[0] + d[0] * ln / 2, q[1] + d[1] * ln / 2)], (g, g, min(255, g + 28)), rng.uniform(2.2, 5.0), a=int(215 * strength), joints=False)
            s += rng.uniform(3, 8)
        for sgn in (-1, 1):
            edge = offset_path(pts, 16 * sgn)
            e = 0
            ce = cum(edge)
            while e < ce[-1]:
                L.line(sub_path(edge, e, e + 7), (230, 235, 250), 1.8, a=int(200 * strength), joints=False)
                e += 14
    return commit(out, L)


def padlock(L, c, letter, big=1.0, open_=False):
    """corp padlock tag with a spray letter (the Cell's guess)"""
    g_lock(L, (c[0], c[1] + 2), 17 * big, (170, 180, 200))
    return c


def cell_letter(base, c, ch, size=40, col=BONE, seed=1, tilt=-0.12):
    L = Layer()
    L.text((0, 0), ch, f2(F_TAG, size), col, anchor="mm")
    m = layer_to_mask(L)
    return base  # placeholder (see tag_text)


def tag_text(base, c, s, size, col=BONE, seed=1, tilt=-0.1, outline=INK, over_r=4.5, drip=True):
    """Cell marker tag: spray-painted PermanentMarker text with black outline, overspray and drips"""
    L = Layer()
    L.text((960, 540), s, f2(F_TAG, size), (255, 255, 255), anchor="mm")
    im = L.down()
    # rotate + translate the text mask around the target
    bbox = im.getbbox()
    if bbox is None:
        return base
    crop = im.crop(bbox)
    crop = crop.rotate(math.degrees(-tilt), expand=True, resample=Image.BICUBIC)
    m = Image.new("L", (W, H), 0)
    # place
    px, py = int(c[0] - crop.size[0] / 2 + 0), int(c[1] - crop.size[1] / 2)
    m.paste(crop.split()[3], (px, py))
    mm = mask_np(m)
    rng = np.random.default_rng(seed)
    if drip:
        mi = Image.fromarray((mm * 255).astype(np.uint8))
        d = ImageDraw.Draw(mi)
        ys, xs = np.where(mm > 0.5)
        if len(xs):
            for _ in range(2):
                i = rng.integers(0, len(xs))
                x, y = xs[i], ys[i]
                ln = rng.uniform(10, 30)
                d.line([(x, y), (x, y + ln)], fill=255, width=2)
                d.ellipse((x - 2.2, y + ln - 2, x + 2.2, y + ln + 3), fill=255)
        mm = mask_np(mi)
    out = base
    if outline is not None:
        mo = np.clip(gaussian_filter(mm, 2.6) * 3.2, 0, 1)
        out = over(out, spray_rgba(mo, outline, seed + 3, over_r=2, over_k=.1, rough=.3, alpha=.92))
    return over(out, spray_rgba(mm, col, seed, over_r=over_r, rough=.5))


def stencil_text(base, c, s, size, col, seed=1, tilt=0.0, outline=None):
    L = Layer()
    L.text((c[0], c[1]), s, f2(F_STENCIL, size), col, anchor="mm")
    return spray_layer(base, L, col, seed, outline=outline, over_r=5, rough=.45)


# --------------------------------------------------------------------------------- the Cell's marks
def stencil_guard(base, c, t, seed=1, size=34, ang=-0.12):
    """GUARD = a stencil block: a slab of spray in the beam's colour, a white stencilled shield with the type glyph, drips."""
    L = Layer()
    w, h = size * 1.8, size * 1.55
    pts = [rot((c[0] + x, c[1] + y), ang, c) for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
    L.poly(pts, fill=(255, 255, 255))
    m = layer_to_mask(L)
    rng = np.random.default_rng(seed)
    mi = Image.fromarray((m * 255).astype(np.uint8))
    d = ImageDraw.Draw(mi)
    for k in range(3):
        x = c[0] + (k - 1) * w * .32 + rng.normal(0, 4)
        y = c[1] + h * .5 - 4
        ln = rng.uniform(16, 44)
        d.line([(x, y), (x, y + ln)], fill=255, width=4)
        d.ellipse((x - 4.5, y + ln - 3, x + 4.5, y + ln + 6), fill=255)
    m = mask_np(mi)
    col = BEAM[t]
    out = over(base, spray_rgba(np.clip(gaussian_filter(m, 3) * 3, 0, 1), INK, seed + 2, over_r=2, over_k=.1, rough=.3, alpha=.88))
    out = over(out, spray_rgba(m, col, seed, over_r=8, rough=.6), glow=0.3, glow_r=10)
    # the stencilled shield (bone) with the type glyph cut in dark
    S = Layer()
    s = size * .62
    g_shield(S, (c[0], c[1] - 1), s, (255, 255, 255))
    for k in (-.15, .4):  # stencil bridges
        br = [rot((c[0] - s, c[1] + s * k), ang, c), rot((c[0] + s, c[1] + s * k), ang, c)]
        S.d.line([(p[0] * SS, p[1] * SS) for p in br], fill=(0, 0, 0, 0), width=int(3 * SS))
    out = spray_layer(out.convert("RGB"), S, BONE, seed + 4, outline=INK, over_r=4, rough=.4).convert("RGBA")
    L2 = Layer()
    g_type(L2, t, (c[0], c[1] + 1), s * .6, line=INK)
    return commit(out, L2)


def spray_shift(base, p0, p1, seed=1, col=BONE, w=15):
    """SHIFT = a spray arrow (a hand-sprayed curved arrow with a fat head)"""
    mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L_ = math.hypot(dx, dy) or 1
    nx, ny = -dy / L_, dx / L_
    c1 = (mid[0] + nx * L_ * .28, mid[1] + ny * L_ * .28)
    pts = []
    for t in np.linspace(0, 1, 18):
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c1[0] + t * t * p1[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c1[1] + t * t * p1[1]
        pts.append((x, y))
    ang = math.atan2(pts[-1][1] - pts[-3][1], pts[-1][0] - pts[-3][0])
    hd = [(pts[-1][0] + math.cos(ang) * 10, pts[-1][1] + math.sin(ang) * 10)]
    hd += [(pts[-1][0] + math.cos(ang + a) * -38, pts[-1][1] + math.sin(ang + a) * -38) for a in (.55, -.55)]
    m = stroke_mask(pts[:-2], w)
    ImageDraw.Draw(m).polygon([hd[0], hd[1], hd[2]], fill=255)
    rng = np.random.default_rng(seed)
    drips(m, pts, rng, 2, 10, 30, 2.5)
    out = over(base, spray_rgba(np.clip(gaussian_filter(mask_np(m), 3) * 3, 0, 1), INK, seed + 2, over_r=2, over_k=.1, rough=.3, alpha=.85))
    return over(out, spray_rgba(mask_np(m), col, seed, over_r=7, rough=.6))


def glitch_sticker(base, c, seed=1, size=30, ang=0.14, col=(255, 255, 255)):
    """GHOST = a glitched vinyl sticker: ghost glyph with RGB split and sliced scan offsets"""
    L = Layer()
    w, h = size * 1.6, size * 1.7
    pts = [rot((c[0] + x, c[1] + y), ang, c) for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
    L.poly(pts, fill=(246, 244, 252), outline=INK, w=2.2)
    out = commit(base, L)
    # ghost body, RGB-split, sliced
    rng = np.random.default_rng(seed)
    for off, colr in ((-3.5, (255, 40, 120)), (3.5, (40, 230, 255))):
        G = Layer()
        s = size * .5
        x, y = c[0] + off, c[1]
        G.circle((x, y - s * .25), s * .72, fill=colr, a=215)
        G.poly([(x - s * .72, y - s * .25), (x + s * .72, y - s * .25), (x + s * .72, y + s * .85), (x + s * .4, y + s * .6), (x, y + s * .85), (x - s * .4, y + s * .6), (x - s * .72, y + s * .85)], fill=colr, a=215)
        out = commit(out, G)
    G = Layer()
    s = size * .5
    G.circle((c[0], c[1] - s * .25), s * .72, fill=(255, 255, 255), a=255)
    G.poly([(c[0] - s * .72, c[1] - s * .25), (c[0] + s * .72, c[1] - s * .25), (c[0] + s * .72, c[1] + s * .85), (c[0] + s * .4, c[1] + s * .6), (c[0], c[1] + s * .85), (c[0] - s * .4, c[1] + s * .6), (c[0] - s * .72, c[1] + s * .85)], fill=(255, 255, 255))
    for ex in (-.3, .3):
        G.d.ellipse([(c[0] + ex * s - s * .17) * SS, (c[1] - s * .3 - s * .2) * SS, (c[0] + ex * s + s * .17) * SS, (c[1] - s * .3 + s * .2) * SS], fill=(0, 0, 0, 0))
    out = commit(out, G)
    # glitch slices: shift horizontal bands
    a = np.asarray(out.convert("RGB")).copy()
    x0, x1 = int(c[0] - w * .7), int(c[0] + w * .7)
    for _ in range(3):
        y = int(c[1] + rng.uniform(-h * .45, h * .45))
        hh = int(rng.uniform(3, 7))
        sh = int(rng.uniform(-10, 10))
        a[y:y + hh, x0:x1] = np.roll(a[y:y + hh, x0:x1], sh, axis=1)
    return Image.fromarray(a).convert("RGBA")


def home_mark(base, c, big=1.0, hit=0.0, seed=2):
    """HOME = the Cell's own hand-sprayed destination: a spray ring on the ground, a heart-roof tag and a stencilled arrow-down."""
    L = Layer()
    ground_ring(L, c, 64 * big, BONE, w=8)
    out = spray_layer(base, L, BONE, seed, outline=INK, over_r=5, rough=.6)
    L = Layer()
    top = (c[0], c[1] - 92 * big)
    L.line([c, top], BONE, 3, a=200)
    g_heart(L, top, 34 * big, (255, 80, 110), INK)
    return commit(out, L)


def lock_on(L, c, r, col=BEAM["E"], t=0.0, pts=4):
    """corner brackets that snap on a target (HUNTER lock)"""
    for k in range(4):
        ang = math.pi / 4 + k * math.pi / 2
        a = (c[0] + math.cos(ang) * r, c[1] + math.sin(ang) * r)
        da = (math.cos(ang + math.pi / 2), math.sin(ang + math.pi / 2))
        db = (math.cos(ang - math.pi / 2), math.sin(ang - math.pi / 2))
        pa = (a[0] + da[0] * r * .5, a[1] + da[1] * r * .5)
        pb = (a[0] + db[0] * r * .5, a[1] + db[1] * r * .5)
        L.line([pa, a, pb], INK, 11)
        L.line([pa, a, pb], col, 6)


def spray_cut(base, S, E, col=BONE, seed=1, outline=INK, over_r=3.5, rough=.35):
    """spray a glyph silhouette S with the shapes of Layer E cut out of it (stencil)"""
    m = layer_to_mask(S) * (1 - np.clip(layer_to_mask(E) * 1.5, 0, 1))
    out = base.convert("RGBA")
    if outline is not None:
        mo = np.clip(gaussian_filter(layer_to_mask(S), 2.6) * 3.2, 0, 1)
        out = over(out, spray_rgba(mo, outline, seed + 3, over_r=2, over_k=.1, rough=.3, alpha=.9))
    return over(out, spray_rgba(m, col, seed, over_r=over_r, rough=rough))


def glyph_disc(base, c, key, seed=1, col=BONE):
    S, E = Layer(), Layer()
    if key == "wrench":
        g_wrench(S, c, 34, (255, 255, 255))
    elif key == "shield+":
        g_shield(S, c, 36, (255, 255, 255), None)
        E.line([(c[0], c[1] - 14), (c[0], c[1] + 14)], (0, 0, 0), 8)
        E.line([(c[0] - 14, c[1]), (c[0] + 14, c[1])], (0, 0, 0), 8)
    elif key == "flame-":
        g_flame(S, c, 34, (255, 255, 255))
        E.line([(c[0] - 30, c[1] + 24), (c[0] + 30, c[1] - 24)], (0, 0, 0), 8)
    elif key == "card":
        L = S
        pts = [rot((c[0] + x, c[1] + y), -.1, c) for x, y in ((-24, -32), (24, -32), (24, 32), (-24, 32))]
        S.poly(pts, fill=(255, 255, 255))
        g_x(E, c, 15, (0, 0, 0), w=8)
    elif key == "plus":
        S.line([(c[0] - 26, c[1]), (c[0] + 26, c[1])], (255, 255, 255), 14)
        S.line([(c[0], c[1] - 26), (c[0], c[1] + 26)], (255, 255, 255), 14)
    elif key == "deploy":
        g_hex(S, c, 38, fill=(255, 255, 255))
        g_arrow(E, c, 20, (0, 0, 0), ang=-math.pi / 2)
    elif key == "hold":
        g_shield(S, c, 38, (255, 255, 255), None)
        E.line([(c[0] - 15, c[1] + 2), (c[0] - 3, c[1] + 15), (c[0] + 17, c[1] - 14)], (0, 0, 0), 9)
    elif key == "move":
        g_arrow(S, (c[0] - 4, c[1] - 15), 30, (255, 255, 255), ang=0)
        g_arrow(S, (c[0] + 4, c[1] + 17), 30, (255, 255, 255), ang=math.pi)
    elif key == "sac":
        g_skull(S, c, 36, (255, 255, 255))
    return spray_cut(base, S, E, col, seed)
