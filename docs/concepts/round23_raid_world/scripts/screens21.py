"""Round 21 raid world: R3 class beacons, station bonus proposals, vehicle icons v3 + toggle v2, the corporate dossier.

python screens21.py [name ...]  names: r3 r3gif bonuses icons toggle dossier dossiergif contact
Inputs: ../scratch/bl (run_blender21.py + vehicles20.py), ../scratch/emblems (emblems20.py).
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as LY  # noqa: E402
import finish19 as FN  # noqa: E402
import ui19 as U  # noqa: E402
import roof20 as RF  # noqa: E402
import screens20 as S20  # noqa: E402
import icons21 as IC  # noqa: E402

OUT = os.path.dirname(HERE)
S20.OUT = OUT
SL = U.SL
W, H = LY.W, LY.H
BG = S20.BG
canvas, paste, crop, label, title, wrap = S20.canvas, S20.paste, S20.crop, S20.label, S20.title, S20.wrap
to_pil, to_f, P, scene_cam, paste_rgba = S20.to_pil, S20.to_f, S20.P, S20.scene_cam, S20.paste_rgba
TXT, DIM = S20.TXT, S20.DIM
CLASSES = S20.CLASSES
CRGB = RF.CLASS_RGB


def save(img, name):
    to_pil(img).save(os.path.join(OUT, name), optimize=True)
    print("saved", name, flush=True)


KEY_COLS = list(RF.CLASS_RGB.values()) + [(212, 255, 0), (92, 225, 255), (255, 68, 51), (255, 176, 0), (150, 92, 255),
                                           (255, 128, 16), (108, 255, 40), (120, 236, 255), (178, 235, 255)]


def save_gif(frames, name, durations, colors=255):
    """Saturation-safe GIF. A median-cut palette from a mosaic of the frames averages neon toward grey, so the palette
    is 196 median-cut colours + the key neon colours (class, corp, Cell lime, harm, ...) at 4 intensities and a pastel
    tint each: saturated pixels snap to a saturated entry. No dither."""
    n = len(frames)
    step = max(1, n // 12)
    sub = [frames[i].resize((frames[0].size[0] // 2, frames[0].size[1] // 2)) for i in range(0, n, step)]
    probe = Image.new("RGB", (sub[0].size[0], sub[0].size[1] * len(sub)))
    for k, sb in enumerate(sub):
        probe.paste(sb, (0, k * sub[0].size[1]))
    base = probe.quantize(colors=196, method=Image.Quantize.MEDIANCUT).getpalette()[:196 * 3]
    extra = []
    for c in KEY_COLS:
        for k in (1.0, 0.78, 0.56, 0.36):
            extra += [int(v * k) for v in c]
        extra += [int(v + (255 - v) * 0.55) for v in c]
    palv = (base + extra)[:256 * 3]
    palv += [0] * (768 - len(palv))
    pal = Image.new("P", (1, 1))
    pal.putpalette(palv)
    q = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
    path = os.path.join(OUT, name)
    q[0].save(path, save_all=True, append_images=q[1:], duration=durations, loop=0, optimize=True, disposal=1)
    mb = os.path.getsize(path) / 1e6
    print("saved %s %.2f MB (%d frames)" % (name, mb, n), flush=True)
    return mb


# ------------------------------------------------------------------ 1. R3 class beacon projection, one idle per class
IDLE = {"breaker": "crowbar swing: the emblem cocks back and strikes, a spark burst at the tip",
        "wrecker": "hammer slam: the emblem lifts and drops, a shock ring runs over the roof",
        "ghost": "fade drift: the emblem bobs, flickers out in glitch slices and comes back",
        "phantom": "afterimage: a cyan double splits off and snaps back into the emblem",
        "rigger": "cable coils: three rings climb the cone and lock round the emblem",
        "overclocker": "heat sink: the cone flutters twice as fast, embers rise, the fins glow",
        "botnet": "drone halo: six drone dots orbit the emblem on a tilted ring",
        "hivemind": "hive pulse: hex cells ripple out of the emblem and fade"}
BONUS_MAP = {"breaker": "A  DAMAGE AURA (GDD)", "ghost": "B  SLOW FIELD (GDD delay)", "rigger": "E  FIELD REPAIR (GDD)",
             "botnet": "free asset per raid (GDD)", "wrecker": "C  SNIPER (proposal)", "hivemind": "D  DRONE OPERATOR (proposal)",
             "phantom": "F  ECHO DECOY (proposal)", "overclocker": "G  OVERCLOCK (proposal)"}


EMBLEM_OVERRIDE = {}   # round 22: cls -> L mask (512) used by beacon() for this frame (rigger blink / angry)


def emblem_mask(cls, size):
    g = Image.open(os.path.join(RF.EMBLEMS, cls + ".png")).split()[3].resize((size, size), Image.LANCZOS)
    return np.asarray(g, np.float32) / 255.0


def beacon(img, px, py, cls, t, scale=1.0):
    """Additive class beacon over img (float HxWx3) from the pad at (px, py). The light is a CONE that opens upward from
    the pad projector and ends at a cap ring UNDER the emblem: no light behind the icon. Each class has its own idle."""
    h, w = img.shape[:2]
    col = np.array(CRGB[cls], np.float32) / 255.0
    s = scale
    Hc, r0, r1 = 210 * s, 7 * s, 62 * s
    es = int(118 * s)
    bob = 0.0
    ex_off = 0.0
    em_alpha = 1.0
    em_rot = 0.0
    em_scale = 1.0
    flutter = 1.0
    if cls == "ghost":
        bob = 10 * s * math.sin(2 * math.pi * t)
        em_alpha = 0.55 + 0.45 * abs(math.sin(2 * math.pi * t * 2))
    elif cls == "wrecker":
        ph = t % 1.0
        bob = -26 * s * math.sin(math.pi * min(1.0, ph / 0.7)) if ph < 0.7 else 6 * s * math.sin((ph - 0.7) / 0.3 * math.pi)
    elif cls == "breaker":
        em_rot = 18 * math.sin(2 * math.pi * t) if t < 0.5 else -26 * math.sin(2 * math.pi * (t - 0.5) * 2) * (t < 0.75)
    elif cls == "overclocker":
        ex_off = 2.5 * s * math.sin(2 * math.pi * t * 7)
        flutter = 0.75 + 0.25 * math.sin(2 * math.pi * t * 4)
    elif cls == "hivemind":
        em_scale = 1.0 + 0.08 * math.sin(2 * math.pi * t * 2)
    top = py - Hc + bob * 0.3
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    sp = np.clip((py - yy) / max(1.0, py - top), 0, 1)
    rad = r0 + (r1 - r0) * sp
    inside = (yy <= py) & (yy >= top)
    dxn = np.abs(xx - px) / np.maximum(rad, 1)
    body = np.clip(1 - dxn, 0, 1) ** 0.4 * (dxn < 1)
    edge = np.exp(-((dxn - 0.96) / 0.06) ** 2)
    bands = 0.82 + 0.18 * np.sin(2 * math.pi * (sp * 7 - t * (4 if cls == "overclocker" else 2)))
    fade = (0.35 + 0.65 * (1 - sp) ** 0.7)
    cone = (body * 0.28 + edge * 0.85) * bands * fade * inside * flutter
    if cls == "ghost":
        cone *= 0.75 + 0.25 * np.sin(yy * 0.08 + t * 12)
    # cap ring (ellipse) at the cone mouth + projector glow at the pad
    capr = np.hypot((xx - px) / r1, (yy - top) / (r1 * 0.32))
    cap = np.exp(-((capr - 1.0) / 0.08) ** 2)
    base = np.exp(-(np.hypot((xx - px) / (18 * s), (yy - py) / (7 * s))) ** 2)
    lay = (cone + cap * 0.9 + base * 1.2)[..., None] * col
    # emblem (holo with scanlines) sitting above the cap; the cone is cut by the emblem's dilated silhouette
    ec_x, ec_y = px + ex_off, top - es * 0.58 + bob
    sz = int(es * em_scale)
    g = (EMBLEM_OVERRIDE[cls] if cls in EMBLEM_OVERRIDE else Image.open(os.path.join(RF.EMBLEMS, cls + ".png")).split()[3]).resize((sz, sz), Image.LANCZOS)
    if em_rot:
        g = g.rotate(em_rot, Image.BICUBIC, center=(sz * 0.2, sz * 0.8))
    em = np.zeros((h, w), np.float32)
    x0, y0 = int(ec_x - sz / 2), int(ec_y - sz / 2)
    ga = np.asarray(g, np.float32) / 255.0
    if 0 <= x0 and x0 + sz <= w and 0 <= y0 and y0 + sz <= h:
        em[y0:y0 + sz, x0:x0 + sz] = ga
    halo = np.asarray(to_pil(np.repeat(em[..., None], 3, 2)).filter(ImageFilter.MaxFilter(9)).convert("L"), np.float32) / 255.0
    lay = lay * (1 - halo[..., None])                       # nothing of the beam shows behind the icon
    scan = 0.78 + 0.22 * ((yy.astype(np.int32) // max(1, int(2 * s))) % 2)
    emc = em * scan * em_alpha
    extra = np.zeros((h, w), np.float32)
    extra_col = col
    # ---- signature idles
    if cls == "breaker" and 0.5 <= t < 0.7:                 # spark burst at the strike
        rng = np.random.default_rng(int(t * 100))
        for _ in range(12):
            a = rng.uniform(0, 2 * math.pi)
            L = rng.uniform(20, 60) * s * (1 - (t - 0.5) * 3)
            sx, sy = ec_x + es * 0.32, ec_y - es * 0.3
            im = Image.new("L", (w, h), 0)
            ImageDraw.Draw(im).line([(sx, sy), (sx + L * math.cos(a), sy + L * math.sin(a))], fill=255, width=max(1, int(3 * s)))
            extra = np.maximum(extra, np.asarray(im, np.float32) / 255.0)
        extra_col = np.array([1.0, 0.95, 0.8], np.float32)
    if cls == "wrecker" and t >= 0.68:                      # shock ring on the roof
        k = (t - 0.68) / 0.32
        rr = np.hypot((xx - px) / (40 * s + 140 * s * k), (yy - py) / ((40 * s + 140 * s * k) * 0.45))
        extra = np.exp(-((rr - 1) / 0.05) ** 2) * (1 - k)
    if cls == "ghost":                                      # glitch slices through the emblem
        sl = ((yy.astype(np.int32) // max(1, int(6 * s)) + int(t * 20)) % 5 == 0)
        emc = emc * np.where(sl & (abs(math.sin(2 * math.pi * t * 2)) < 0.5), 0.0, 1.0)
    if cls == "phantom":                                    # afterimage double (cyan) splits and returns
        d = 22 * s * abs(math.sin(math.pi * t))
        sh = np.roll(np.roll(em, int(d), 1), int(-d * 0.3), 0)
        lay = lay + (sh * 0.7 * scan)[..., None] * np.array([0.36, 0.88, 1.0], np.float32)
    if cls == "rigger":                                     # rings climbing the cone
        for k in range(3):
            q = (t + k / 3) % 1.0
            yc = py - (py - top) * q
            rr_ = r0 + (r1 - r0) * q
            ell = np.hypot((xx - px) / rr_, (yy - yc) / (rr_ * 0.3))
            extra = np.maximum(extra, np.exp(-((ell - 1) / 0.07) ** 2) * (1 - q * 0.4))
    if cls == "overclocker":                                # embers
        rng = np.random.default_rng(5)
        for k in range(14):
            q = (t * 1.5 + rng.uniform(0, 1)) % 1.0
            exn = px + rng.uniform(-0.8, 0.8) * (r0 + (r1 - r0) * q) + 4 * s * math.sin(q * 9 + k)
            eyn = py - (py - top) * q
            extra = np.maximum(extra, np.exp(-(np.hypot(xx - exn, yy - eyn) / (2.6 * s)) ** 2) * (1 - q))
        extra_col = np.array([1.0, 0.55, 0.15], np.float32)
    if cls == "botnet":                                     # orbiting drone dots
        for k in range(6):
            a = 2 * math.pi * (t + k / 6)
            ox, oy = ec_x + 78 * s * math.cos(a), ec_y + 26 * s * math.sin(a)
            front = math.sin(a) > -0.2 or True
            extra = np.maximum(extra, np.exp(-(np.hypot(xx - ox, yy - oy) / (5 * s)) ** 2) * (1.0 if math.sin(a) > 0 else 0.55))
    if cls == "hivemind":                                   # hex cells rippling out
        for k in range(2):
            q = (t + k * 0.5) % 1.0
            R = (60 + 120 * q) * s
            hexr = Image.new("L", (w, h), 0)
            dd = ImageDraw.Draw(hexr)
            for j in range(6):
                a = math.pi / 6 + j * math.pi / 3
                cx, cy = ec_x + R * math.cos(a), ec_y + R * 0.55 * math.sin(a)
                dd.regular_polygon((cx, cy, 13 * s), 6, outline=255, width=max(1, int(2 * s)))
            extra = np.maximum(extra, np.asarray(hexr, np.float32) / 255.0 * (1 - q))
    lay = lay + (emc * 0.7)[..., None] * col + (extra * 1.1)[..., None] * extra_col
    blur = np.asarray(to_pil(np.clip(lay, 0, 1)).filter(ImageFilter.GaussianBlur(7 * s)), np.float32) / 255.0
    out = img + lay + blur * 0.8
    # the emblem stays readable: a soft dark plate just behind it (it is a projection in front of the city)
    plate = np.asarray(to_pil(np.repeat(em[..., None], 3, 2)).filter(ImageFilter.GaussianBlur(5 * s)).convert("L"), np.float32) / 255.0
    out = out * (1 - 0.45 * plate[..., None]) + (emc * 1.0)[..., None] * (0.22 + 0.8 * col)
    return np.clip(out, 0, 1)


_r3_base = {}


def r3_base(cls):
    if cls not in _r3_base:
        img = FN.finish("B_r3", "night", decorate=S20.world_decor("B", slot="stationed", cls=cls, boosts=[("safe", cls)], t=0.3),
                        seed=1, tilt=0.0, rain=False, fog=0.0)
        _r3_base[cls] = img
    return _r3_base[cls]


def r3_tile(cls, t, size):
    """Crop around the Safehouse pad (pad at ~80 % height, room above for the cone + emblem), aspect of `size`."""
    img = r3_base(cls)
    px, py = S20.pad_screen("B_r3", img.shape[1], img.shape[0])
    bw = 720
    bh = int(bw * size[1] / size[0])
    x0, y0 = int(px - bw / 2), int(py - bh * 0.8)
    sub = img[y0:y0 + bh, x0:x0 + bw].copy()
    sub = beacon(sub, px - x0, py - y0 - 3, cls, t, scale=1.25)
    return np.asarray(to_pil(sub).resize(size, Image.LANCZOS), np.float32) / 255.0


def operators_r3():
    cv = canvas()
    cv = title(cv, "STATION BEACONS R3", "LOCKED R3: A CLASS-COLOUR LIGHT CONE OPENS FROM THE SAFEHOUSE PAD AND STOPS UNDER THE EMBLEM (NO LIGHT BEHIND "
                                         "THE ICON)  //  8 CLASSES, 8 COLOURS, 8 IDLE LOOPS")
    tw, th = 440, 464
    for i, c in enumerate(CLASSES):
        x, y = 40 + (i % 4) * (tw + 20), 140 + (i // 4) * (th + 2)
        tile = r3_tile(c, 0.55 if c in ("breaker", "wrecker") else 0.3, (tw, 360))
        cv = paste(cv, tile, x, y)
        cv = label(cv, x, y + 366, c.upper(), 22, CRGB[c], font=SL.ANTON)
        cv = label(cv, x + 440, y + 374, BONUS_MAP[c], 11, (235, 240, 250), anchor="ra")
        cv, _ = wrap(cv, x, y + 404, IDLE[c], 70, 12, TXT, lh=16)
    return cv


def operator_gif():
    n = 16
    tw, th = 300, 246
    gap = 10
    cols, rows = 4, 2
    GW, GH = cols * tw + (cols + 1) * gap, 54 + rows * (th + 30) + gap
    base = Image.new("RGB", (GW, GH), (8, 7, 14))
    d = ImageDraw.Draw(base)
    d.text((gap, 12), "STATION BEACONS  //  ONE IDLE PER CLASS", font=U.F(SL.ANTON, 26), fill=(255, 222, 30))
    for i, c in enumerate(CLASSES):
        x, y = gap + (i % cols) * (tw + gap), 54 + (i // cols) * (th + 30)
        d.text((x + 4, y + th + 4), c.upper(), font=U.F(SL.MONO, 16), fill=CRGB[c])
    frames = []
    for f in range(n):
        im = base.copy()
        for i, c in enumerate(CLASSES):
            x, y = gap + (i % cols) * (tw + gap), 54 + (i // cols) * (th + 30)
            tile = r3_tile(c, f / n, (tw, th))
            im.paste(to_pil(tile), (x, y))
        frames.append(im)
        print("r3 frame", f, flush=True)
    return save_gif(frames, "operator_classes.gif", [90] * n)


# ------------------------------------------------------------------ 2. station bonus effects (PROPOSALS)
BCAM = "S_bonus"
CROP = (120, 40, 1720, 940)          # panel crop of the 1920 x 1080 bonus frame
PW, PH = 640, 360
ICE = np.array([0.72, 0.92, 1.0], np.float32)


def PS(x, y, z=0.0):
    return P(x, y, z, cam=scene_cam(BCAM))


def threat_px(i, z=2.5):
    t = LY.THREATS_BONUS[i]
    return PS(t[2], t[3], z)


def heli_px(t=0.62):
    a = 3.3 + 2 * math.pi * t
    return PS(10 + 40 * math.cos(a), -120 + 40 * math.sin(a), 62)


def ground_poly(wx, wy, r, n=48):
    return [PS(wx + r * math.cos(2 * math.pi * i / n), wy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


class Fx:
    """Additive light layer + an opaque text layer for one frame, composited with bloom."""

    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.add = np.zeros((h, w, 3), np.float32)
        self.txt = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    def _mask(self, fn):
        m = Image.new("L", (self.w, self.h), 0)
        fn(ImageDraw.Draw(m))
        return np.asarray(m, np.float32) / 255.0

    def paint(self, fn, col, k=1.0):
        self.add += (self._mask(fn) * k)[..., None] * (np.array(col, np.float32) / (255.0 if max(col) > 1.5 else 1.0))

    def line(self, pts, col, width=3, k=1.0):
        self.paint(lambda d: d.line(pts, fill=255, width=int(width), joint="curve"), col, k)

    def poly(self, pts, col, k=1.0, outline=None, width=3):
        if outline is None:
            self.paint(lambda d: d.polygon(pts, fill=255), col, k)
        else:
            self.paint(lambda d: d.line(list(pts) + [pts[0]], fill=255, width=width), col, k)

    def disc(self, x, y, r, col, k=1.0):
        self.paint(lambda d: d.ellipse([x - r, y - r, x + r, y + r], fill=255), col, k)

    def ring(self, x, y, rx, ry, col, width=3, k=1.0):
        self.paint(lambda d: d.ellipse([x - rx, y - ry, x + rx, y + ry], outline=255, width=int(width)), col, k)

    def text(self, x, y, s, size, col, anchor="mm", font=None):
        d = ImageDraw.Draw(self.txt)
        f = U.F(font or SL.ANTON, size)
        d.text((x, y), s, font=f, fill=tuple(col) + (255,), anchor=anchor, stroke_width=max(2, size // 9), stroke_fill=(10, 8, 16, 255))

    def comp(self, img, glow=1.0):
        b = np.asarray(to_pil(np.clip(self.add, 0, 1)).filter(ImageFilter.GaussianBlur(9)), np.float32) / 255.0
        out = to_pil(np.clip(img + self.add + b * glow, 0, 1)).convert("RGBA")
        out.alpha_composite(self.txt)
        return to_f(out)


def float_up(fx, x, y, s, col, age, size=44):
    """Damage / repair number rising and fading, age 0..1."""
    if 0 <= age < 1:
        fx.text(x, y - 60 * age, s, int(size * (1.15 - 0.2 * age)), tuple(int(c * (1 - 0.5 * age) + 20) for c in col))


def tracer(fx, p0, p1, col, k=1.0, width=4):
    fx.line([p0, p1], col, width, k)
    fx.line([p0, p1], (255, 250, 235), max(1, width // 2), k)
    fx.disc(p1[0], p1[1], 16, (255, 245, 220), 0.9 * k)


_bases = {}


def bonus_base(cls, heat=True, shares=(), integ=None, rings="live", core_boost=False):
    key = (cls, heat, tuple(shares), json.dumps(integ, sort_keys=True), rings, core_boost)
    if key not in _bases:
        if len(_bases) > 10:
            _bases.clear()

        def extra(net):
            for (corp, ui, x, y, a, up, hp) in LY.THREATS_BONUS:
                net.threat_ring(x, y, hp=hp, state=rings)
        boosts = [("safe", cls)]
        dec = S20.world_decor("B", slot="stationed", cls=cls, t=0.3, boosts=boosts, shares=list(shares), routes=("r3",),
                              exposed=("safe",) if heat else (), integ=integ, extra=extra)
        img = FN.finish(BCAM if heat else "S_bonus_nh", "night", decorate=dec, seed=1, tilt=0.0, rain=False, fog=0.0)
        _bases[key] = img
    return _bases[key].copy()


def with_beacon(img, cls, t):
    """The stationed operative's R3 beacon on the Safehouse pad, at map scale (applied on a crop for speed)."""
    px, py = S20.pad_screen(BCAM, img.shape[1], img.shape[0])
    x0, y0 = int(px - 140), int(py - 230)
    sub = img[y0:y0 + 270, x0:x0 + 280].copy()
    img[y0:y0 + 270, x0:x0 + 280] = beacon(sub, px - x0, py - y0 - 2, cls, t, scale=0.5)
    return img


def fx_damage(t, lev):
    cls, col = "breaker", CRGB["breaker"]
    img = bonus_base(cls, heat=False, shares=(("safe", "core", cls),) if lev else ())
    img = with_beacon(img, cls, t)
    fx = Fx()
    sx, sy = PS(10, -120)
    for (wx, wy, on) in ((10, -120, True), (10, -50, lev)):
        if not on:
            continue
        for k in range(2):
            q = (t + k * 0.5) % 1.0
            fx.poly(ground_poly(wx, wy, 13 + 9 * q), col, k=1.2 * (1 - q), outline=True, width=4)
        cx, cy = PS(wx, wy)
        for k in range(3):                                         # rising damage chevrons
            q = (t * 1.5 + k / 3) % 1.0
            yy = cy - 40 - 90 * q
            fx.line([(cx - 16, yy + 10), (cx, yy), (cx + 16, yy + 10)], col, 5, 1.3 * (1 - q))
        fx.text(cx + 54, cy - 70, "+50%", 26, col)
    shots = [((9, -121, 6), 0, 0.08), ((9, -121, 6), 1, 0.42), ((9, -121, 6), 0, 0.75)]
    if lev:
        shots += [((8.5, -51.5, 6), 1, 0.25), ((8.5, -51.5, 6), 1, 0.6)]
    for (m, ti, t0) in shots:
        p0, p1 = PS(*m), threat_px(ti)
        age = (t - t0) % 1.0
        if age < 0.07:
            tracer(fx, p0, p1, col, 1.3, 6)
        float_up(fx, p1[0] + 20, p1[1] - 40, "-6" if m[1] < -100 else "-9", col, age / 0.35)
    return fx.comp(img)


def fx_slow(t, lev):
    cls, col = "ghost", CRGB["ghost"]
    img = bonus_base(cls, heat=False)
    img = with_beacon(img, cls, t)
    R = 30
    freeze = lev and 0.45 <= t < 0.85
    fx = Fx()
    fx.poly(ground_poly(10, -120, R), ICE * 255 if freeze else col, k=0.12 if not freeze else 0.16)
    fx.poly(ground_poly(10, -120, R), (255, 255, 255) if freeze else col, k=1.3, outline=True, width=4)
    for k in range(3):                                             # ripples run inward (time is slower in here)
        q = (t + k / 3) % 1.0
        fx.poly(ground_poly(10, -120, R * (1 - q)), col, k=0.7 * q, outline=True, width=3)
    tx, ty = threat_px(0)
    out = fx.comp(img)
    # the slowed unit leaves afterimages behind it (copies of its own pixels, back along its route)
    patch = img[int(ty) - 60:int(ty) + 40, int(tx) - 70:int(tx) + 70]
    res = out.copy()
    for k, a in ((1, 0.32), (2, 0.16)):
        dx = int(26 * k)
        y0, x0 = int(ty) - 60, int(tx) - 70 + dx
        reg = res[y0:y0 + patch.shape[0], x0:x0 + patch.shape[1]]
        lum = patch.mean(axis=2, keepdims=True)
        reg[:] = reg * (1 - a) + (lum * 0.5 + np.array(col, np.float32) / 255 * 0.5) * a
    fx2 = Fx()
    fx2.ring(tx, ty + 6, 46, 18, col, 3, 1.2)
    for k in range(8):                                             # slow clock ticks round the unit
        a = 2 * math.pi * (k / 8 + t * 0.1)
        fx2.line([(tx + 46 * math.cos(a), ty + 6 + 18 * math.sin(a)), (tx + 56 * math.cos(a), ty + 6 + 22 * math.sin(a))], col, 3, 1.0)
    if freeze:
        q = (t - 0.45) / 0.4
        g = np.asarray(Image.open(os.path.join(S20.U.GLYPHS, "state_frozen.png")).split()[3].resize((56, 56)), np.float32) / 255
        fx2.add[int(ty) - 110:int(ty) - 54, int(tx) - 28:int(tx) + 28] += g[..., None] * ICE * 1.4
        reg = res[int(ty) - 50:int(ty) + 30, int(tx) - 60:int(tx) + 60]
        reg[:] = reg * 0.45 + (reg.mean(axis=2, keepdims=True) * 0.6 + 0.35) * ICE * 0.55
        fx2.text(tx, ty + 56, "FROZEN 1 STEP", 24, (190, 240, 255))
        if q < 0.15:
            fx2.poly(ground_poly(10, -120, R + 3), (255, 255, 255), k=2.0, outline=True, width=10)
    else:
        fx2.text(tx, ty + 56, "SLOWED  -1 STEP", 22, col)
    return fx2.comp(res)


def fx_sniper(t, lev):
    cls, col = "wrecker", CRGB["wrecker"]
    img = bonus_base(cls, heat=False)
    img = with_beacon(img, cls, t)
    px, py = S20.pad_screen(BCAM, W, H)
    muzzle = (px, py - 40)
    fx = Fx()
    if not lev:
        tgt = threat_px(1)
    else:
        a, b = np.array(threat_px(1)), np.array(threat_px(2))
        u = min(1.0, max(0.0, (t - 0.08) / 0.34))
        u = u * u * (3 - 2 * u)
        tgt = tuple(a * (1 - u) + b * u)
    fire = 0.5 <= t < 0.56
    if t < 0.5:
        jit = 3 * math.sin(t * 40)
        L = math.hypot(tgt[0] - muzzle[0], tgt[1] - muzzle[1])
        n = int(L / 14)
        for k in range(n):
            if k % 2 == 0:
                q0, q1 = k / n, (k + 1) / n
                fx.line([(muzzle[0] + (tgt[0] - muzzle[0]) * q0, muzzle[1] + (tgt[1] - muzzle[1]) * q0 + jit * q0),
                         (muzzle[0] + (tgt[0] - muzzle[0]) * q1, muzzle[1] + (tgt[1] - muzzle[1]) * q1 + jit * q1)], (255, 70, 40), 2, 1.2)
        charge = t / 0.5
        rr = 60 - 36 * charge
        fx.ring(tgt[0], tgt[1], rr, rr * 0.5, col, 3, 1.4)
        if lev:
            fx.line([(tgt[0] - 30, tgt[1]), (tgt[0] - 10, tgt[1])], (255, 255, 255), 3, 1.4)
            fx.line([(tgt[0] + 10, tgt[1]), (tgt[0] + 30, tgt[1])], (255, 255, 255), 3, 1.4)
            fx.line([(tgt[0], tgt[1] - 30), (tgt[0], tgt[1] - 10)], (255, 255, 255), 3, 1.4)
            fx.line([(tgt[0], tgt[1] + 10), (tgt[0], tgt[1] + 30)], (255, 255, 255), 3, 1.4)
            fx.text(tgt[0] + 30, tgt[1] - 56, "AIM: DRAG  //  CLICK: FIRE", 20, (246, 243, 236), anchor="lm", font=SL.MONO)
            cur = (tgt[0] + 14, tgt[1] + 14)
            ImageDraw.Draw(fx.txt).polygon([cur, (cur[0] + 6, cur[1] + 26), (cur[0] + 12, cur[1] + 18), (cur[0] + 24, cur[1] + 17)],
                                           fill=(246, 243, 236, 255), outline=(14, 12, 20, 255))
    if fire:
        tracer(fx, muzzle, tgt, col, 2.0, 12)
        fx.disc(muzzle[0], muzzle[1], 26, (255, 240, 200), 1.5)
    age = (t - 0.5) / 0.4
    float_up(fx, tgt[0] + 20, tgt[1] - 50, "-18" if lev else "-14", col, age, 60)
    if t >= 0.56:
        fx.text(muzzle[0] + 70, muzzle[1] - 20, "RELOAD 2", 18, col, font=SL.MONO)
    return fx.comp(img)


def _bez(p0, p1, p2, u):
    return ((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0], (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1])


def drone(fx, x, y, col, a=0.0):
    for k in range(4):
        ang = a + math.pi / 4 + k * math.pi / 2
        fx.line([(x, y), (x + 13 * math.cos(ang), y + 7 * math.sin(ang))], (230, 230, 240), 3, 1.0)
        fx.disc(x + 13 * math.cos(ang), y + 7 * math.sin(ang), 4, col, 1.3)
    fx.disc(x, y, 5, col, 1.6)


def fx_drones(t, lev):
    cls, col = "hivemind", CRGB["hivemind"]
    hx, hy = heli_px()
    down = lev and t >= 0.62
    img = bonus_base(cls, heat=True)
    if lev and t >= 0.55:                                          # the chopper goes down: the spot + EXPOSED go away
        nh = bonus_base(cls, heat=False)
        sx, sy = PS(10, -120)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        ax, ay, bx, by = hx, hy, sx, sy
        abx, aby = bx - ax, by - ay
        q = np.clip(((xx - ax) * abx + (yy - ay) * aby) / (abx * abx + aby * aby), 0, 1)
        dist = np.hypot(xx - (ax + q * abx), yy - (ay + q * aby))
        m = np.clip(1 - (dist - (90 + 60 * q)) / 40, 0, 1)
        m = np.maximum(m, np.clip(1 - (np.hypot(xx - hx, yy - hy) - 150) / 40, 0, 1))
        k = min(1.0, (t - 0.55) / 0.1)
        img = img * (1 - m[..., None] * k) + nh * m[..., None] * k
    img = with_beacon(img, cls, t)
    fx = Fx()
    px, py = S20.pad_screen(BCAM, W, H)
    start = (px, py - 30)
    targets = [threat_px(1), threat_px(1), threat_px(2)]
    if lev:
        targets = [threat_px(1), threat_px(2), (hx, hy + 10), (hx + 30, hy + 20)]
    for i, tg in enumerate(targets):
        air = lev and i >= 2
        if t < 0.3:
            u = t / 0.3
            p = _bez(start, ((start[0] + tg[0]) / 2, min(start[1], tg[1]) - 120), (tg[0], tg[1] - 50), u)
        elif t < 0.78:
            a = 2 * math.pi * (t - 0.3) * 3 + i * 2.1
            p = (tg[0] + 40 * math.cos(a), tg[1] - 50 + 16 * math.sin(a))
            if int((t - 0.3) * 30 + i) % 3 == 0 and not (air and down):
                tracer(fx, p, (tg[0] + (8 if not air else 0), tg[1] + (0 if not air else 10)), col, 1.0, 3)
            if not air and int((t - 0.3) * 30 + i) % 6 == 0:
                float_up(fx, tg[0] - 30 + 20 * i, tg[1] - 70, "-2", col, 0.3, 30)
        else:
            u = (t - 0.78) / 0.22
            p = _bez((tg[0], tg[1] - 50), ((start[0] + tg[0]) / 2, min(start[1], tg[1]) - 120), start, u)
        drone(fx, p[0], p[1], col, t * 20 + i)
    if lev:
        if 0.4 <= t < 0.66:                                        # sparks + the hit
            rng = np.random.default_rng(int(t * 100))
            for _ in range(10):
                a = rng.uniform(0, 2 * math.pi)
                L = rng.uniform(10, 50)
                fx.line([(hx, hy), (hx + L * math.cos(a), hy + L * math.sin(a))], (255, 220, 160), 2, 1.3)
        if 0.6 <= t < 0.7:
            fx.disc(hx, hy, 70 * (1 - (t - 0.6) * 5), (255, 200, 120), 1.6)
        if down:
            fx.text(hx + 10, hy + 90, "CHOPPER DOWN  //  EXPOSED CLEARED", 24, col)
        else:
            fx.text(px + 150, py + 40, "SAFEHOUSE EXPOSED", 22, (255, 255, 255))
    return fx.comp(img)


def fx_repair(t, lev):
    cls, col = "rigger", CRGB["rigger"]
    u = min(1.0, max(0.0, (t - 0.12) / 0.6))
    integ = {"safe": round(0.3 + 0.7 * u, 2)}
    if lev:
        integ["core"] = round(0.45 + 0.55 * u, 2)
    img = bonus_base(cls, heat=False, integ=integ, rings="down", shares=(("safe", "core", cls),) if lev else ())
    img = with_beacon(img, cls, t)
    fx = Fx()
    for (wx, wy, on) in ((10, -120, True), (10, -50, lev)):
        if not on:
            continue
        cx, cy = PS(wx, wy)
        for k in range(8):                                         # green sparks spiral up into the socket
            q = (t * 2 + k / 8) % 1.0
            a = 2 * math.pi * (q + k / 8)
            fx.disc(cx + 50 * (1 - q) * math.cos(a), cy - 10 + 22 * (1 - q) * math.sin(a) - 60 * q, 4, col, 1.4 * (1 - q))
        for k in range(3):
            q = (t + k / 3) % 1.0
            fx.line([(cx - 10, cy - 40 - 70 * q), (cx + 10, cy - 40 - 70 * q)], col, 5, 1.2 * (1 - q))
            fx.line([(cx, cy - 50 - 70 * q), (cx, cy - 30 - 70 * q)], col, 5, 1.2 * (1 - q))
        if 0.12 <= t < 0.8:
            float_up(fx, cx + 60, cy - 60, "+INT", col, ((t - 0.12) * 2.5) % 1.0, 30)
    fx.text(560, 380, "WAVE 1 CLEARED", 40, (235, 240, 250))
    return fx.comp(img)


BONUSES = [
    ("damage", "A  DAMAGE AURA", "BREAKER  (GDD: node assets +50% damage)", fx_damage,
     "this node's assets hit +50% (pink aura, rising chevrons, boosted numbers)",
     "the aura runs down the links: adjacent nodes' assets get it too"),
    ("slow", "B  SLOW FIELD", "GHOST  (GDD: entering threats delayed 1 step)", fx_slow,
     "a 30 m field; units inside lose a step (ripples run inward, afterimages, clock ticks)",
     "every few steps the field freezes the units inside it for 1 step"),
    ("sniper", "C  SNIPER", "WRECKER  (proposal, alt of Breaker)", fx_sniper,
     "a roof sniper locks the toughest unit in range (sight + charge ring) and fires once per 3 steps",
     "the player drags the reticle to pick the target, click to fire"),
    ("drones", "D  DRONE OPERATOR", "HIVEMIND  (proposal, alt of Botnet)", fx_drones,
     "drones launch from the pad, orbit incoming units and chip them",
     "drones also hunt enemy drones / choppers: the chopper goes down, its spot and EXPOSED with it"),
    ("repair", "E  FIELD REPAIR", "RIGGER  (GDD: node regains integrity after each wave)", fx_repair,
     "after each wave the node's integrity track refills (green sparks into the socket)",
     "adjacent nodes are repaired too"),
]


BCROP = {"damage": (150, 300, 1430, 1020), "repair": (150, 300, 1430, 1020), "slow": (420, 330, 1500, 938),
         "sniper": (500, 300, 1700, 975), "drones": (250, 40, 1530, 760)}


def bonus_panel(fn, t, lev, head, key):
    img = fn(t, lev)
    pil = to_pil(img).crop(BCROP[key]).resize((PW, PH), Image.LANCZOS)
    d = ImageDraw.Draw(pil)
    d.rectangle([0, 0, 190 if not lev else 230, 26], fill=(5, 13, 28))
    d.text((8, 13), head, font=U.F(SL.MONO, 15), fill=(92, 225, 255) if not lev else (255, 222, 30), anchor="lm")
    return pil


def bonus_gifs():
    n = 18
    for key, nm, who, fn, b_txt, l_txt in [b for b in BONUSES if not os.environ.get("BONUS_ONLY") or b[0] in os.environ["BONUS_ONLY"].split(",")]:
        GW, GH = 2 * PW + 30, PH + 112
        base = Image.new("RGB", (GW, GH), (8, 7, 14))
        d = ImageDraw.Draw(base)
        d.text((10, 8), "PROPOSAL  //  " + nm, font=U.F(SL.ANTON, 26), fill=(255, 222, 30))
        d.text((10 + U.F(SL.ANTON, 26).getlength("PROPOSAL  //  " + nm) + 20, 22), who, font=U.F(SL.MONO, 15), fill=(92, 225, 255))
        d.text((10, 52 + PH + 8), b_txt, font=U.F(SL.MONO, 13), fill=(190, 225, 240))
        d.text((20 + PW, 52 + PH + 8), l_txt, font=U.F(SL.MONO, 13), fill=(255, 222, 30))
        frames = []
        for f in range(n):
            im = base.copy()
            im.paste(bonus_panel(fn, f / n, False, "BASE", key), (10, 50))
            im.paste(bonus_panel(fn, f / n, True, "LEVELLED UP", key), (20 + PW, 50))
            frames.append(im)
            print(key, f, flush=True)
        save_gif(frames, "bonus_%s.gif" % key, [100] * n)


def station_bonuses():
    cv = canvas()
    cv = title(cv, "STATION BONUSES", "PROPOSALS (GDD GAP): WHAT A STATIONED OPERATIVE DOES TO ITS SAFEHOUSE (AND, LEVELLED UP, ITS NEIGHBOURS)  //  "
                                      "BASE  |  LEVELLED UP  //  ONE GIF EACH")
    tw, th = 420, 236
    stills = {"damage": 0.06, "slow": 0.6, "sniper": 0.52, "drones": 0.5, "repair": 0.5}
    for i, (key, nm, who, fn, b_txt, l_txt) in enumerate(BONUSES):
        x, y = 40 + (i % 2) * 940, 132 + (i // 2) * 312
        for j, lev in enumerate((False, True)):
            t = stills[key] if not (key == "drones" and lev) else 0.64
            pan = bonus_panel(fn, t, lev, "BASE" if not lev else "LEVELLED UP", key)
            cv = paste(cv, to_f(pan.resize((tw, th), Image.LANCZOS)), x + j * (tw + 10), y)
        cv = label(cv, x, y + th + 4, nm, 20, (235, 240, 250), font=SL.ANTON)
        cv = label(cv, x + 230, y + th + 12, who, 12, U.CYAN)
        cv = label(cv, x, y + th + 36, "BASE: " + b_txt, 11, TXT)
        cv = label(cv, x, y + th + 54, "LEVELLED: " + l_txt, 11, (255, 222, 30))
    # mapping table
    x, y = 980, 132 + 2 * 312
    rows = [("BREAKER", "A damage aura", "GDD"), ("GHOST", "B slow field", "GDD delay"), ("RIGGER", "E field repair", "GDD"),
            ("BOTNET", "free asset / raid", "GDD"), ("WRECKER", "C sniper", "new"), ("HIVEMIND", "D drone operator", "new"),
            ("PHANTOM", "F echo decoy", "new"), ("OVERCLOCKER", "G overclock", "new")]
    pan = S20.term_blank("CLASS -> BONUS (PROPOSAL)", 860, 300, accent=U.LIME)
    dd = ImageDraw.Draw(pan["img"])
    for i, (c, b, src) in enumerate(rows):
        yy = 42 + i * 24
        dd.text((14, yy), c, font=U.F(SL.MONO, 15), fill=CRGB[c.lower()] + (255,))
        dd.text((180, yy), b, font=U.F(SL.MONO, 15), fill=(230, 236, 245, 255))
        dd.text((380, yy), src, font=U.F(SL.MONO, 13), fill=(150, 190, 205, 255) if src != "new" else (255, 222, 30, 255))
    dd.text((470, 44), "F echo decoy: a phantom copy of the node pulls", font=U.F(SL.MONO, 12), fill=(150, 190, 205, 255))
    dd.text((470, 62), "  threats one step (DECOY rule); lev: 2 copies", font=U.F(SL.MONO, 12), fill=(150, 190, 205, 255))
    dd.text((470, 96), "G overclock: assets fire twice, +1 Heat a raid;", font=U.F(SL.MONO, 12), fill=(150, 190, 205, 255))
    dd.text((470, 114), "  lev: no Heat cost", font=U.F(SL.MONO, 12), fill=(150, 190, 205, 255))
    cv = U.put_panel(cv, pan, x, y)
    return cv


# ------------------------------------------------------------------ 3. vehicle icons v3 + toggle v2
def heading_ring(fx, cam, x, y, a, r=16.0, selected=False, tag=None, k=1.0):
    """Hover / selection only: a ring on the street round the unit with a small arrow riding it in the heading direction."""
    pts = [P(x + r * math.cos(2 * math.pi * i / 64), y + r * math.sin(2 * math.pi * i / 64), 0.1, cam=cam) for i in range(64)]
    col = (246, 243, 236)
    if selected:
        fx.line(pts + [pts[0]], col, 6, 1.6 * k)
    else:
        for i in range(0, 64, 4):
            fx.line([pts[i], pts[i + 1], pts[(i + 2) % 64]], col, 5, 1.6 * k)
    tip = P(x + (r + 8.5) * math.cos(a), y + (r + 6.5) * math.sin(a), 0.1, cam=cam)
    l = P(x + (r - 1.5) * math.cos(a + 0.34), y + (r - 1.5) * math.sin(a + 0.34), 0.1, cam=cam)
    rr = P(x + (r - 1.5) * math.cos(a - 0.34), y + (r - 1.5) * math.sin(a - 0.34), 0.1, cam=cam)
    fx.poly([tip, l, rr], (255, 222, 30), 2.0 * k)
    if tag:
        c = P(x, y, 0, cam=cam)
        d = ImageDraw.Draw(fx.txt)
        f = U.F(SL.MONO, 18)
        wdt = f.getlength(tag) + 20
        x0, y0 = c[0] + 70, c[1] - 120
        d.rectangle([x0, y0, x0 + wdt, y0 + 30], fill=(5, 13, 28, 235), outline=(92, 225, 255, 255), width=2)
        d.text((x0 + 10, y0 + 15), tag, font=f, fill=(190, 225, 240, 255), anchor="lm")
        d.line([(c[0] + 20, c[1] - 40), (x0, y0 + 30)], fill=(92, 225, 255, 255), width=2)


def vehicle_icons_v3():
    cv = canvas()
    cv = title(cv, "VEHICLE ICONS V3", "ONE SHAPE PER VEHICLE TYPE, SHARED BY EVERY CORP  //  THE CORP IS THE COLOUR ONLY  //  "
                                       "NO HEADING ON THE ICON (HOVER / SELECT SHOWS IT ON THE STREET)")
    corps = list(IC.CORP_RGB)
    x0, y0 = 300, 150
    for j, c in enumerate(corps):
        cv = label(cv, x0 + j * 150, y0, c, 16, IC.CORP_RGB[c], font=SL.ANTON, anchor="ma")
    desc = {"FAST": "chevron badge  //  >>", "HEAVY": "thick block  //  weight", "SPECIAL": "hexagon  //  its verb glyph",
            "LANDER": "pod, point down  //  drop", "FLYING": "winged diamond  //  rotor"}
    for i, t in enumerate(IC.TYPES):
        y = y0 + 70 + i * 128
        cv = label(cv, 40, y - 10, t, 30, (235, 240, 250), font=SL.ANTON)
        cv = label(cv, 40, y + 30, desc[t], 12, DIM)
        for j, c in enumerate(corps):
            names = [IC.UNIT_NAMES[c][ui] for ui in range(3) if IC.unit_type(c, ui) == t]
            if t == "FLYING":
                names = ["CHOPPER / DRONE"]
            if not names:
                cv = label(cv, x0 + j * 150, y + 4, "-", 20, (70, 70, 90), anchor="ma")
                continue
            verb = None
            if t == "SPECIAL":
                verb = {"MERIDIAN": "state_locked", "SOLACE": "special_dose", "HALCYON": "state_frozen", "REBEL_CELL": "placeholder_burn"}[c]
            cv = paste_rgba(cv, IC.icon(t, c, size=58, verb=verb), x0 + j * 150, y + 6)
            cv = label(cv, x0 + j * 150, y + 50, " / ".join(names), 11, (230, 236, 245), anchor="ma")
    cv = label(cv, 40, 830, "UPGRADED +  and  LIVE HP", 16, U.CYAN)
    demo = [("HEAVY", "HALCYON", False, None), ("HEAVY", "HALCYON", True, None), ("HEAVY", "HALCYON", True, 0.64),
            ("FAST", "MERIDIAN", True, 0.9), ("SPECIAL", "SOLACE", False, 0.4)]
    for i, (t, c, up, hp) in enumerate(demo):
        cv = paste_rgba(cv, IC.icon(t, c, up=up, size=58, hp=hp, verb="special_dose" if t == "SPECIAL" else None), 110 + i * 150, 920)
    for i, s in enumerate(("base", "upgraded", "+ live HP", "fast + HP", "special + HP")):
        cv = label(cv, 110 + i * 150, 975, s, 11, DIM, anchor="ma")
    cv = label(cv, 40, 1010, "the shape answers 'what does it do' at a glance; colour answers 'whose'. Glyphs repeat the type for greyscale.", 12, TXT)
    # right: map scale, the 30 units as models and as v3 icons
    img = S20.vehicle_matrix_img()
    lay = json.load(open(os.path.join(FN.SRC, "veh_layout.json")))
    k = lay["ortho"] / 440.0
    full = to_pil(img).resize((int(W * k), int(H * k)), Image.LANCZOS)
    xs = [it["px"] for it in lay["items"]]
    ys = [it["py"] for it in lay["items"]]
    bx = (int((min(xs) - 70) * k), int((min(ys) - 60) * k), int((max(xs) + 70) * k), int((max(ys) + 40) * k))
    strip = full.crop(bx)
    fit = min(560 / strip.size[0], 300 / strip.size[1])
    strip = strip.resize((int(strip.size[0] * fit), int(strip.size[1] * fit)), Image.LANCZOS)
    sx, sy = 1100, 170
    cv = paste(cv, np.asarray(strip, np.float32) / 255, sx, sy)
    cv = label(cv, sx, sy - 22, "MAP SCALE: the 30 models", 13, U.CYAN)
    tile = np.zeros((strip.size[1], strip.size[0], 3), np.float32) + np.array([0.09, 0.08, 0.14], np.float32)
    for it in lay["items"]:
        tile = paste_rgba(tile, IC.unit_icon(it["corp"], it["col"] // 2, up=it["up"], size=22),
                          (it["px"] * k - bx[0]) * fit, (it["py"] * k - bx[1]) * fit)
    cv = paste(cv, tile, sx, sy + strip.size[1] + 40)
    cv = label(cv, sx, sy + strip.size[1] + 18, "THE SAME 30 AS V3 ICONS (rows = corps: colour; columns = type: shape)", 13, U.CYAN)
    # hover heading demo (close-up)
    cam = scene_cam("W_close")
    base = FN.finish("W_close", "night", decorate=S20.world_decor("B", routes=("r1", "r3"), extra=lambda n: S20.threat_rings(n)), seed=1, tilt=0.0)
    fx = Fx()
    c, ui, x, y, a, up, hp = LY.THREATS_V2[2]
    heading_ring(fx, cam, x, y, a, selected=False, tag="HAULER +  MERIDIAN  HP 9/15  > CORE")
    out = fx.comp(base)
    cx, cy = P(x, y, 0, cam=cam)
    sub = crop(out, (int(cx - 480), int(cy - 330), int(cx + 480), int(cy + 210)), (560, 315))
    hy = sy + 2 * strip.size[1] + 70
    cv = paste(cv, sub, sx, hy)
    cv = label(cv, sx, hy - 22, "HOVER / SELECT ONLY: heading = an arrow riding a ring round the unit", 13, U.CYAN)
    return cv


def vehicle_toggle_v2():
    cv = canvas()
    cv = title(cv, "VEHICLE / ICON TOGGLE V2", "V3 ICONS (SHAPE = TYPE, COLOUR = CORP)  //  HEADING ONLY ON HOVER / SELECTION, AS A RING ARROW ON THE STREET")
    cam = scene_cam("W_close")
    dec = S20.world_decor("B", routes=("r1", "r3"), extra=lambda n: S20.threat_rings(n))
    close = FN.finish("W_close", "night", decorate=dec, seed=1, tilt=0.0)
    fx = Fx()
    T = LY.THREATS_V2
    heading_ring(fx, cam, T[1][2], T[1][3], T[1][4], selected=False, tag="INSPECTOR +  HP 6/6  > VAULT")
    heading_ring(fx, cam, T[2][2], T[2][3], T[2][4], selected=True, tag="HAULER +  HP 9/15  > CORE")
    close = fx.comp(close)
    cv = paste(cv, close, 40, 150, (1000, 563))
    cv = label(cv, 40, 724, "CLOSE-UP: models + livery; dashed ring = hover, solid ring = selected; the arrow on the ring = heading", 14, (235, 240, 250))
    full_cam = scene_cam("B_full")
    cx, cy = P(104, -82, 0, cam=full_cam)
    cw, ch = 1150, 647
    box = (int(cx - cw / 2), int(cy - ch / 2) + 30, int(cx + cw / 2), int(cy + ch / 2) + 30)
    dw, dh = 820, 461
    sk = dw / cw
    iv = crop(FN.finish("B_full", "night", decorate=S20.world_decor("B", routes=("r1", "r3")), seed=1), box, (dw, dh))
    for (corp, ui, x, y, a, up, hp) in T:
        px, py = P(x, y, 0, cam=full_cam)
        iv = paste_rgba(iv, IC.unit_icon(corp, ui, up=up, size=26, hp=hp), (px - box[0]) * sk, (py - box[1]) * sk)
    im = to_pil(iv)
    d = ImageDraw.Draw(im)
    fw, fh = 1920 * 150 / 440 * sk, 1080 * 150 / 440 * sk
    fx_, fy_ = (cx - box[0]) * sk, (cy - box[1]) * sk
    d.rectangle([fx_ - fw / 2, fy_ - fh / 2, fx_ + fw / 2, fy_ + fh / 2], outline=(92, 225, 255), width=2)
    cv = paste(cv, to_f(im), 1060, 150)
    cv = label(cv, 1060, 622, "ZOOMED OUT (< 0.6x): v3 icons; no heading (the routes already show it)", 14, (235, 240, 250))
    rows = [("kv", "MAP ZOOM", "0.45x", (190, 225, 240)), ("kv", "UNITS", "ICONS (auto)", U.LIME), ("t", "hold [V]: show models", (150, 190, 205)),
            ("t", "hover: ring + heading + tag", (150, 190, 205))]
    cv = U.put_panel(cv, U.terminal("VIEW", rows, w=330), 1060, 680)
    for i, (corp, ui, x, y, a, up, hp) in enumerate(T[:7]):
        cv = paste_rgba(cv, IC.unit_icon(corp, ui, up=up, size=46, hp=hp), 90 + i * 135, 860)
        cv = label(cv, 90 + i * 135, 912, IC.UNIT_NAMES[corp][ui] + (" +" if up else ""), 12, (230, 236, 245), anchor="ma")
        cv = label(cv, 90 + i * 135, 930, IC.unit_type(corp, ui), 10, IC.CORP_RGB[corp], anchor="ma")
    cv = label(cv, 40, 780, "Swap = 0.15 s crossfade at the zoom threshold (0.55 / 0.65 hysteresis); HP ring stays on the street in both.", 13, TXT)
    cv = label(cv, 40, 804, "Mixed corps only to compare colours; a real raid is usually one corporation.", 13, TXT)
    cv = label(cv, 40, 970, "this wave's units as v3 icons (46 px hover size)", 12, DIM)
    return cv


# ------------------------------------------------------------------ 4. the corporate dossier
def dossier_photos():
    import lost20 as LO
    rs = LO.raid_screen()
    cam = scene_cam("W_full")
    cx, cy = P(10, -50, 0, cam=cam)
    p1 = to_pil(rs).crop((int(cx - 230), int(cy - 230), int(cx + 230), int(cy + 230)))
    p2 = to_pil(r3_tile("breaker", 0.3, (460, 460)))
    p3 = to_pil(rs).crop((560, 260, 1360, 1060))
    return [p1, p2, p3]


def dossier():
    import dossier21 as DS
    return to_f(DS.compose(dossier_photos(), 1.0))


def dossier_gif():
    import dossier21 as DS
    photos = dossier_photos()
    frames, durs = [], []
    seq = [0.0] * 3 + [i / 12 for i in range(1, 13)] + [1.0]
    for u in seq:
        u2 = 0.5 - 0.5 * math.cos(math.pi * u)
        frames.append(DS.compose(photos, u2).resize((960, 540), Image.LANCZOS))
        durs.append(90)
        print("dossier", u, flush=True)
    durs[0] = 600
    durs[-1] = 2000
    return save_gif(frames, "campaign_dossier_open.gif", durs)


def contact():
    from PIL import ImageSequence
    names = ["operators_r3.png", "operator_classes.gif", "station_bonuses.png", "bonus_damage.gif", "bonus_slow.gif", "bonus_sniper.gif",
             "bonus_drones.gif", "bonus_repair.gif", "vehicle_icons_v3.png", "vehicle_toggle_v2.png", "campaign_dossier.png",
             "campaign_dossier_open.gif"]
    tw, th, cols = 600, 338, 3
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGB", (tw * cols + 40, th * rows + 24 * rows + 80), (10, 9, 16))
    d = ImageDraw.Draw(sheet)
    d.text((14, 16), "ROUND 21  RAID WORLD: CLASS BEACONS, STATION BONUS PROPOSALS, ICONS V3, CORPORATE DOSSIER", font=U.F(SL.ANTON, 30), fill=(255, 222, 30))
    for i, n in enumerate(names):
        im = Image.open(os.path.join(OUT, n))
        if n.endswith(".gif"):
            fr = [f.convert("RGB") for f in ImageSequence.Iterator(im)]
            im = fr[len(fr) * 2 // 3]
        im = im.convert("RGB")
        k = min(tw / im.size[0], th / im.size[1])
        im = im.resize((int(im.size[0] * k), int(im.size[1] * k)), Image.LANCZOS)
        x, y = 10 + (i % cols) * (tw + 10), 70 + (i // cols) * (th + 24)
        sheet.paste(im, (x, y))
        d.text((x + 4, y + th + 2), n, font=U.F(SL.MONO, 15), fill=(92, 225, 255))
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=86)
    print("saved contact_sheet.jpg")


if __name__ == "__main__":
    which = sys.argv[1:] or ["r3", "r3gif", "bonuses", "icons", "toggle", "dossier", "dossiergif", "contact"]
    if "r3" in which:
        save(operators_r3(), "operators_r3.png")
    if "r3gif" in which:
        operator_gif()
    if "bonuses" in which:
        save(station_bonuses(), "station_bonuses.png")
    if "bonusgifs" in which:
        bonus_gifs()
    if "icons" in which:
        save(vehicle_icons_v3(), "vehicle_icons_v3.png")
    if "toggle" in which:
        save(vehicle_toggle_v2(), "vehicle_toggle_v2.png")
    if "dossier" in which:
        save(dossier(), "campaign_dossier.png")
    if "dossiergif" in which:
        dossier_gif()
    if "contact" in which:
        contact()
