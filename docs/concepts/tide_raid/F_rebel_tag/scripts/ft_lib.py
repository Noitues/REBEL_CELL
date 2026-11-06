"""F Rebel Tag: shared library.

All vector drawing is on a 2x supersampled RGBA Layer using 1920x1080 frame coordinates
(callers pass 1x coordinates).  Spray / paint work is raster (numpy masks, noisy threshold + overspray).
World (plate px) -> frame px goes through W2S().
"""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from scipy.ndimage import gaussian_filter, distance_transform_edt

HERE = os.path.dirname(os.path.abspath(__file__))
PLATES = "D:/rc_scratch/tide_concepts/plates"
W, H = 1920, 1080
SS = 2

# ---- palette -------------------------------------------------------------------------
INK = (14, 10, 22)
BONE = (246, 240, 222)          # the Cell's paint
CORP = (226, 244, 255)          # corp AR cold white
CORP_DIM = (120, 150, 175)
BEAM = {"D": (58, 150, 255), "N": (255, 64, 214), "E": (255, 224, 26)}
UNTOUCHED = (191, 251, 240)     # mint / cyan-white (ruled)
HOLDS = (31, 184, 166)          # teal
LOST = (242, 154, 31)           # amber
DAMAGED = (255, 112, 20)        # orange
BREACH = (255, 59, 48)          # HARM red
TIER = {"untouched": UNTOUCHED, "holds": HOLDS, "lost": LOST, "damaged": DAMAGED, "breach": BREACH}
PLUM = (26, 11, 31)
PLUM2 = (58, 22, 62)
VEIN = (255, 63, 160)
HOT = (255, 150, 215)
LIME = (212, 255, 0)            # focus halo only
CRT_BG = (8, 18, 36)
CRT_EDGE = (92, 225, 255)
GREASE = (255, 74, 58)          # D28 grease pencil


def font(name, size):
    return ImageFont.truetype(os.path.join(HERE, name), size)


F_MONO = lambda s: font("ShareTechMono-Regular.ttf", s)
F_TAG = lambda s: font("PermanentMarker-Regular.ttf", s)
F_ANTON = lambda s: font("Anton-Regular.ttf", s)
F_STENCIL = lambda s: font("Anton-Regular.ttf", s)  # unused in the final frames

# ---- world -> frame ---------------------------------------------------------------------
ZOOM = 2.0
OX, OY = 208.0, 275.0
LIFT = 12.0   # polylines are ground level; the game's 3D wire hovers about this much above them


def W2S(p, lift=LIFT):
    return ((p[0] - OX) * ZOOM, (p[1] - lift - OY) * ZOOM)


def load_json(scn="default", beat="forecast"):
    return json.load(open(f"{PLATES}/coords/{scn}_{beat}.json"))


# ---- path utilities ----------------------------------------------------------------------
def spurs(pl):
    """indices i where pl[i-1]~pl[i+1] (a site stub); returns [(i, base, tip)]"""
    out = []
    for i in range(1, len(pl) - 1):
        a, b, c = pl[i - 1], pl[i], pl[i + 1]
        if abs(a[0] - c[0]) < 1.5 and abs(a[1] - c[1]) < 1.5:
            out.append((i, a, b))
    return out


def clean_path(pl):
    """drop the site stubs (A,B,A -> A)"""
    pl = [tuple(p) for p in pl]
    out = []
    i = 0
    while i < len(pl):
        if 0 < i < len(pl) - 1 and abs(pl[i - 1][0] - pl[i + 1][0]) < 1.5 and abs(pl[i - 1][1] - pl[i + 1][1]) < 1.5:
            i += 2
            continue
        out.append(pl[i])
        i += 1
    ded = [out[0]]
    for p in out[1:]:
        if math.hypot(p[0] - ded[-1][0], p[1] - ded[-1][1]) > 0.5:
            ded.append(p)
    return ded


def path_len(pts):
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))


def cum(pts):
    c = [0.0]
    for i in range(len(pts) - 1):
        c.append(c[-1] + math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]))
    return c


def point_at(pts, s, cl=None):
    cl = cl or cum(pts)
    s = max(0.0, min(cl[-1], s))
    for i in range(len(pts) - 1):
        if s <= cl[i + 1] or i == len(pts) - 2:
            seg = cl[i + 1] - cl[i]
            t = 0 if seg == 0 else (s - cl[i]) / seg
            x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t
            y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t
            ang = math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0])
            return (x, y), ang
    return pts[-1], 0.0


def sub_path(pts, s0, s1):
    cl = cum(pts)
    s0 = max(0, s0)
    s1 = min(cl[-1], s1)
    out = [point_at(pts, s0, cl)[0]]
    for i in range(1, len(pts) - 1):
        if s0 < cl[i] < s1:
            out.append(pts[i])
    out.append(point_at(pts, s1, cl)[0])
    return out


def resample(pts, step):
    cl = cum(pts)
    n = max(2, int(cl[-1] / step) + 1)
    return [point_at(pts, cl[-1] * k / (n - 1), cl)[0] for k in range(n)]


def offset_path(pts, d):
    """lateral offset (screen space) with averaged vertex normals"""
    if d == 0:
        return list(pts)
    out = []
    for i, p in enumerate(pts):
        nx = ny = 0.0
        for a, b in ((i - 1, i), (i, i + 1)):
            if 0 <= a and b < len(pts):
                dx, dy = pts[b][0] - pts[a][0], pts[b][1] - pts[a][1]
                L = math.hypot(dx, dy) or 1
                nx += -dy / L
                ny += dx / L
        L = math.hypot(nx, ny) or 1
        # miter scale limited
        out.append((p[0] + nx / L * d, p[1] + ny / L * d))
    return out


def nearest_s(pts, q):
    best, bs = 1e18, 0
    cl = cum(pts)
    for i in range(len(pts) - 1):
        ax, ay = pts[i]
        bx, by = pts[i + 1]
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy or 1
        t = max(0, min(1, ((q[0] - ax) * dx + (q[1] - ay) * dy) / L2))
        px, py = ax + dx * t, ay + dy * t
        d = (px - q[0]) ** 2 + (py - q[1]) ** 2
        if d < best:
            best, bs = d, cl[i] + t * math.sqrt(L2)
    return bs


# ---- vector layer ---------------------------------------------------------------------------
class Layer:
    def __init__(self):
        self.im = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    @staticmethod
    def s(p):
        return (p[0] * SS, p[1] * SS)

    def line(self, pts, col, w, a=255, joints=True):
        if len(pts) < 2:
            return
        c = tuple(col[:3]) + (a,)
        sp = [self.s(p) for p in pts]
        self.d.line(sp, fill=c, width=max(1, int(round(w * SS))))
        if joints and w > 2.5:
            r = w * SS / 2
            for p in (sp[0], sp[-1]) + tuple(sp[1:-1]):
                self.d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=c)

    def circle(self, c, r, fill=None, outline=None, w=1.0, a=255):
        x, y = self.s(c)
        r *= SS
        f = tuple(fill[:3]) + (a,) if fill is not None else None
        o = tuple(outline[:3]) + (a,) if outline is not None else None
        self.d.ellipse((x - r, y - r, x + r, y + r), fill=f, outline=o, width=max(1, int(w * SS)) if o else 0)

    def ellipse(self, c, rx, ry, fill=None, outline=None, w=1.0, a=255):
        x, y = self.s(c)
        f = tuple(fill[:3]) + (a,) if fill is not None else None
        o = tuple(outline[:3]) + (a,) if outline is not None else None
        self.d.ellipse((x - rx * SS, y - ry * SS, x + rx * SS, y + ry * SS), fill=f, outline=o,
                       width=max(1, int(w * SS)) if o else 0)

    def poly(self, pts, fill=None, outline=None, w=1.0, a=255):
        f = tuple(fill[:3]) + (a,) if fill is not None else None
        o = tuple(outline[:3]) + (a,) if outline is not None else None
        sp = [self.s(p) for p in pts]
        self.d.polygon(sp, fill=f)
        if o:
            self.d.line(sp + [sp[0]], fill=o, width=max(1, int(w * SS)), joint="curve")

    def rrect(self, box, r, fill=None, outline=None, w=1.0, a=255):
        f = tuple(fill[:3]) + (a,) if fill is not None else None
        o = tuple(outline[:3]) + (a,) if outline is not None else None
        b = [box[0] * SS, box[1] * SS, box[2] * SS, box[3] * SS]
        self.d.rounded_rectangle(b, radius=r * SS, fill=f, outline=o, width=max(1, int(w * SS)) if o else 0)

    def text(self, xy, s, f, fill, anchor="mm", a=255, stroke=0, stroke_fill=(0, 0, 0)):
        # fonts passed at 1x size; scale by building a 2x font
        fn = f
        self.d.text(self.s(xy), s, font=fn, fill=tuple(fill[:3]) + (a,), anchor=anchor,
                    stroke_width=int(stroke * SS), stroke_fill=tuple(stroke_fill[:3]) + (a,))

    def down(self):
        return self.im.resize((W, H), Image.LANCZOS)


def f2(fname_fn, size):
    """font at SS scale (use with Layer.text)"""
    return fname_fn(int(size * SS))


def over(base, rgba, glow=0.0, glow_r=10):
    """alpha-composite RGBA (1x) onto base RGB(A).  glow > 0 adds a screened blur of the colour."""
    base = base.convert("RGBA")
    if glow > 0:
        a = np.asarray(rgba).astype(np.float32) / 255
        col = a[..., :3] * a[..., 3:4]
        g = np.stack([gaussian_filter(col[..., k], glow_r) for k in range(3)], -1) * glow
        b = np.asarray(base).astype(np.float32)[..., :3] / 255
        b = 1 - (1 - b) * (1 - np.clip(g, 0, 1))
        base = Image.fromarray((np.clip(b, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    return Image.alpha_composite(base, rgba)


def commit(base, layer, glow=0.0, glow_r=10):
    return over(base, layer.down(), glow, glow_r)


# ---- raster masks & spray paint -----------------------------------------------------------------------
def new_mask():
    return Image.new("L", (W, H), 0)


def mask_np(m):
    return np.asarray(m).astype(np.float32) / 255


def spray_rgba(mask, col, seed=1, over_r=7.0, over_k=0.55, rough=0.55, alpha=1.0, grain=0.12):
    """mask: float HxW 0..1 -> RGBA uint8 with rough edges, overspray speckle and faint density grain"""
    rng = np.random.default_rng(seed)
    soft = gaussian_filter(mask, 1.4)
    n = gaussian_filter(rng.random(mask.shape).astype(np.float32), 1.2)
    n = (n - n.mean()) / (n.std() + 1e-6)
    core = ((soft + n * 0.16 * rough) > 0.5).astype(np.float32)
    halo = gaussian_filter(mask, over_r)
    spk = (rng.random(mask.shape) < halo * over_k * 1.6).astype(np.float32) * (1 - core)
    fine = gaussian_filter(mask, over_r * 0.4) * 0.10
    dens = 1.0 - grain * gaussian_filter(rng.random(mask.shape).astype(np.float32), 0.8) * 2
    a = np.clip(core * 0.97 * dens + spk * 0.7 + fine * (1 - core), 0, 1) * alpha
    out = np.zeros(mask.shape + (4,), np.uint8)
    out[..., 0], out[..., 1], out[..., 2] = col[0], col[1], col[2]
    out[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def stroke_mask(pts, w, m=None, round_ends=True):
    m = m or new_mask()
    d = ImageDraw.Draw(m)
    d.line(pts, fill=255, width=int(w), joint="curve")
    if round_ends:
        r = w / 2
        for p in (pts[0], pts[-1]):
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=255)
    return m


def drips(m, pts, rng, n=4, lmin=18, lmax=70, w=3.0):
    """paint drips running down from random points on a path"""
    d = ImageDraw.Draw(m)
    for _ in range(n):
        p = pts[rng.integers(0, len(pts))]
        ln = rng.uniform(lmin, lmax)
        x = p[0] + rng.normal(0, 3)
        d.line([(x, p[1]), (x, p[1] + ln)], fill=255, width=int(w))
        d.ellipse((x - w * 0.9, p[1] + ln - w * 0.9, x + w * 0.9, p[1] + ln + w * 1.3), fill=255)
    return m


def wobble(pts, rng, amp=2.0, step=10):
    """hand-wobble a path (frame px)"""
    rp = resample(pts, step)
    out = []
    ph = rng.uniform(0, 6.28)
    for i, p in enumerate(rp):
        out.append((p[0] + amp * math.sin(i * 0.7 + ph) + rng.normal(0, amp * 0.25),
                    p[1] + amp * math.cos(i * 0.55 + ph) + rng.normal(0, amp * 0.25)))
    return out


def spray_path(base, pts, col, w, seed=1, drip_n=2, outline=None, over_r=6.0, rough=0.6, amp=1.8):
    rng = np.random.default_rng(seed)
    wp = wobble(pts, rng, amp)
    m = stroke_mask(wp, w)
    if drip_n:
        drips(m, wp, rng, drip_n, 14, 50, max(2.5, w * 0.28))
    out = base
    if outline is not None:
        mo = stroke_mask(wp, w + 7)
        if drip_n:
            pass
        out = over(out, spray_rgba(mask_np(mo), outline, seed + 7, over_r=3, over_k=0.2, rough=0.3, alpha=0.9))
    return over(out, spray_rgba(mask_np(m), col, seed, over_r=over_r, rough=rough))


def layer_to_mask(layer, thresh=0.0):
    return np.asarray(layer.down())[..., 3].astype(np.float32) / 255


def spray_layer(base, layer, col, seed=1, outline=None, over_r=6.0, rough=0.6, glow=0.0):
    """spray-paint any vector Layer's alpha silhouette"""
    m = layer_to_mask(layer)
    out = base
    if outline is not None:
        mo = gaussian_filter(m, 3.0)
        mo = np.clip(mo * 3.0, 0, 1)
        out = over(out, spray_rgba(mo, outline, seed + 5, over_r=3, over_k=0.2, rough=0.3, alpha=0.85))
    return over(out, spray_rgba(m, col, seed, over_r=over_r, rough=rough), glow, 8)


# ---- plate & grade ---------------------------------------------------------------------------------------
def load_plate(name="city_noraid_nonet.png", zoom=True):
    im = Image.open(f"{PLATES}/{name}").convert("RGB")
    if zoom:
        box = (OX, OY, OX + W / ZOOM, OY + H / ZOOM)
        im = im.crop(tuple(int(round(v)) for v in box)).resize((W, H), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=70, threshold=2))
    return im


def grade(im, sat=1.45, dark=0.9, bloom=1.0, seed=3, rain=True, vignette=0.45):
    """night stays night, but vivid: windows bloom, saturation up, mids down so the AR layer can sing"""
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255
    lum = (a * np.array([0.3, 0.59, 0.11], np.float32)).sum(-1, keepdims=True)
    a = lum + (a - lum) * sat
    a = np.clip(a, 0, 1) ** 1.18 * dark + 0.012
    # cool the shadows toward indigo
    a[..., 2] += (1 - lum[..., 0]) * 0.02
    lum2 = (a * np.array([0.3, 0.59, 0.11], np.float32)).sum(-1, keepdims=True)
    bright = np.clip((lum2 - 0.30) / 0.30, 0, 1) * a
    bl = np.stack([gaussian_filter(bright[..., k], 4) * 1.1 + gaussian_filter(bright[..., k], 16) * 1.0 for k in range(3)], -1)
    a = 1 - (1 - a) * (1 - np.clip(bl * bloom, 0, 1))
    if vignette:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        a *= (1 - vignette * np.clip(r - 0.55, 0, 1) ** 1.6)[..., None]
    out = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    if rain:
        out = add_rain(out, seed)
    return out


def add_rain(im, seed=3, n=520):
    rng = np.random.default_rng(seed)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        ln = rng.uniform(14, 34)
        d.line([(x, y), (x - ln * 0.22, y + ln)], fill=(190, 215, 255, int(rng.uniform(25, 70))), width=1)
    return Image.alpha_composite(im.convert("RGBA"), L)


def darken(im, k, region=None):
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    if region is None:
        a *= k
    else:
        a *= (1 - (1 - k) * region[..., None])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ---- colour-blind sim ----------------------------------------------------------------------------------------
_M = {
    "deutan": np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
    "tritan": np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]),
}


def cvd(img, kind):
    a = np.asarray(img.convert("RGB")).astype(np.float32) / 255
    lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    out = np.clip(lin @ _M[kind].T, 0, 1)
    srgb = np.where(out <= 0.0031308, out * 12.92, 1.055 * out ** (1 / 2.4) - 0.055)
    return Image.fromarray((np.clip(srgb, 0, 1) * 255).astype(np.uint8))
