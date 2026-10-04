"""Round 32: THE RED LIGHTS. The Cell's district keeps the city's own buildings (no fist streets: grid27.patch completes
the normal street grid; nothing is painted, nothing floats). The only mark is the WINDOW LIGHT: every lit window whose
position on the map falls inside the Cell's crest burns red, and more of them are lit, so the fist reads from the
pattern of red lights across many ordinary buildings.

  home     : warm signal red, ~3.5x the city's window density inside the crest, soft red glow.
  dispatch : harsher red, every window lit, the crest torn by glitch bands (rows shifted sideways), a few windows
             flashing white / dead, stronger glow.

Same pipeline as the city maps (round 6 restyler over the game's own layout, read-only; night theme; labels). The other
HQs are the round 6 map drawings (placeholders: the round 25-30 HQ sprites live in other rounds' scratch).
python map29.py [home|dispatch] -> ../scratch/map32_<state>.png (3840 x 2160 + crops)
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "city_r6"))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
SRC = os.path.join(OUT, "..", "round6_city_restyle")
DST = os.path.join(OUT, "scratch")

from PIL import Image
import lowpoly
from lowpoly import SS
import views as V
import restyle
from restyle import View, labels
import citydata as CD
import grid27

# round 30 variants (the round 29 fist was too big on the zoomed-out map):
#   A: a smaller red-window fist (fewer, dimmer red windows)
#   B: no light at all: the buildings inside the fist are red-TINTED (a subtle red district whose outline is the fist)
#   C: red rooftop warning beacons (aircraft lights) on every roof inside the fist: a constellation of red dots
VAR = {"A": dict(h=880.0, lift=300.0, win={"home": 0.9, "dispatch": 1.0}, glow=((4, 0.30), (14, 0.22)), dglow=((4, 0.6), (16, 0.5))),
       "B": dict(h=820.0, lift=150.0, win={"home": 0.0, "dispatch": 0.35}, glow=(), dglow=((4, 0.4), (14, 0.3))),
       "C": dict(h=820.0, lift=150.0, win={"home": 0.0, "dispatch": 0.0}, glow=((3, 1.0), (10, 0.7)), dglow=((3, 1.3), (12, 0.9)))}
V_ = VAR["A"]
CREST_H = 760.0
CREST_LIFT = 260.0
WIN_P = {"home": 0.80, "dispatch": 1.0}
RED = {"home": (226, 52, 48), "dispatch": (255, 16, 30)}


def crest_parts():
    parts = []
    for i in range(4):
        x0 = -5.2 + i * 2.65
        parts.append((x0, x0 + 2.15, 8.6, 13.3 + (0.7 if i in (1, 2) else 0)))
    parts.append((-5.2, 5.5, 5.3, 8.0))
    parts.append((-3.5, 3.5, 0.0, 4.9))
    return parts


FINGERS = [(-5.4, -2.75), (-2.75, -0.05), (-0.05, 2.75), (2.75, 5.6)]  # crest units (round 32: no gaps: the splits are dark lines)


class Crest:
    def __init__(self, cx, cy, state):
        self.cx, self.cy, self.k = cx, cy + CREST_H / 2, CREST_H / 14.8
        self.parts = crest_parts()
        self.disp = state == "dispatch"
        r = random.Random(29)
        self.bands = {}  # dispatch: screen-row bands shifted sideways (glitch)
        if self.disp:
            for b in range(-40, 40):
                self.bands[b] = r.choice([0, 0, 0, 0, r.uniform(-1.3, 1.3)])

    def uv(self, X, Y):
        u = (X - self.cx) / self.k
        v = (self.cy - Y) / self.k
        if self.disp:
            u -= self.bands.get(int(math.floor(v / 0.9)), 0.0)
        return u, v

    def zone(self, X, Y):
        """ROUND 32: 0 outside, 1 the red fist, 2 a BLACKED-OUT detail line inside it (finger splits, the thumb
        separation, knuckle creases, the wrist cuff, the thumb tip)."""
        u, v = self.uv(X, Y)
        # the solid silhouette: four fingers with rounded-ish tops, the thumb / palm row, the wrist
        if v < 0 or v > 14.2 or u < -5.4 or u > 5.6:
            return 0
        if v < 5.2 and not (-3.6 <= u <= 3.6):
            return 0
        if v > 13.3:  # finger tops: the two middle fingers stand higher, each top rounded
            for i, (a0, a1) in enumerate(FINGERS):
                top = 13.6 + (0.6 if i in (1, 2) else 0.0)
                c = (a0 + a1) / 2
                r = (a1 - a0) / 2
                if a0 <= u <= a1 and v <= top - (1 - math.sqrt(max(0.0, 1 - ((u - c) / r) ** 2))) * 0.9:
                    break
            else:
                return 0
        # the detail lines (blacked out)
        LW = 0.75
        for (a0, a1) in FINGERS[:-1]:  # the splits between fingers, down to the thumb
            if abs(u - (a1 + 0.12)) < LW / 2 and v > 8.3:
                return 2
        if abs(v - 8.25) < LW / 2 and -5.4 <= u <= 4.4:  # the thumb's upper edge, folded across the fingers
            return 2
        if 4.4 <= u <= 5.6 and abs(v - (8.25 - (u - 4.4) * 1.6)) < LW * 0.6:  # the thumb tip turning down
            return 2
        for (a0, a1) in FINGERS:  # knuckle creases: a short dash on each finger
            if a0 + 0.45 <= u <= a1 - 0.45 and abs(v - 11.4) < LW * 0.4:
                return 2
        if abs(v - 5.2) < LW / 2 and -3.6 <= u <= 5.0:  # palm / wrist cuff
            return 2
        if abs(v - 2.0) < LW * 0.4 and -3.6 <= u <= 3.6:  # the cuff band
            return 2
        return 1

    def inside(self, X, Y):
        return self.zone(X, Y) == 1


def install(crest, state):
    orig_ext = restyle.Restyler.ext

    def ext(self, d, pr, gl):
        self._gl = gl
        ci = pr.get("ctx", -1)
        b = pr["b"]
        n = len(b) // 2
        bx, by = sum(b[0::2]) / n, sum(b[1::2]) / n
        topy = by - pr["z0"] - pr["h"]
        isbld = ci >= 0 and self.ctxs[ci]["kind"] == "bld"
        hit = isbld and crest.inside(bx, by - pr["z0"] - pr["h"] * 0.5)
        if isbld and crest.zone(bx, by - pr["z0"] - pr["h"] * 0.5) == 2:  # round 32: a blacked-out building on a detail line
            stops, tcol = self.fam_for(ci)
            self.fams[ci] = ([lowpoly.mix(s_, (8, 6, 12), 0.62) for s_ in stops], tcol)
            orig_ext(self, d, pr, gl)
            self.fams[ci] = (stops, tcol)
            return
        if VARIANT == "B" and hit:  # tint this building's colour family toward a deep red-brown
            stops, tcol = self.fam_for(ci)
            kk = 0.85 if state == "dispatch" else 0.72
            red = (205, 22, 34) if state == "dispatch" else (175, 34, 40)
            self.fams[ci] = ([lowpoly.mix(s, lowpoly.mix(red, s, 0.35 * (k / 4.0)), kk) for k, s in enumerate(stops)], tcol)
            orig_ext(self, d, pr, gl)
            self.fams[ci] = (stops, tcol)
        else:
            orig_ext(self, d, pr, gl)
        if VARIANT == "C" and isbld and pr["ts"] > 0.05 and crest.inside(bx, topy):
            v = self.v
            x, y = v.p(bx, topy)
            r = random.Random(pr["key"] * 7 + 3)
            if state == "dispatch":
                col = (255, 240, 240) if r.random() < 0.12 else (255, 20, 34)
                rad = 3.4 * v.k
            else:
                if r.random() < 0.0:
                    return
                col = (240, 40, 40)
                rad = 2.8 * v.k
            d.ellipse([(x - rad) * SS, (y - rad) * SS, (x + rad) * SS, (y + rad) * SS], fill=col)
            REDL[0].ellipse([(x - rad * 1.6) * SS, (y - rad * 1.6) * SS, (x + rad * 1.6) * SS, (y + rad * 1.6) * SS], fill=col)

    def windows(self, d, a, b, hh, ink, seed, band):
        """The city's own windows outside the crest (unchanged rule); inside it a denser grid of red-lit windows."""
        v = self.v
        rng = random.Random(str(('w', seed)))
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        warm = lowpoly.hexc('#ffc872')
        gl = getattr(self, "_gl", None)

        def pos(u, z):
            x = a[0] + (b[0] - a[0]) * u
            y = a[1] + (b[1] - a[1]) * u - z
            zz = crest.zone(x / v.s + v.x0, y / v.s + v.y0)
            return x, y, (zz == 1) if zz != 2 else "dark"

        def quad(x, y, w2, h0, h1):
            dy = (b[1] - a[1]) / L * w2
            return [((x - w2) * SS, (y - dy - h1 * v.k) * SS), ((x + w2) * SS, (y + dy - h1 * v.k) * SS),
                    ((x + w2) * SS, (y + dy + h0 * v.k) * SS), ((x - w2) * SS, (y - dy + h0 * v.k) * SS)]

        nx = max(1, int(L / (7.0 * v.k)))
        ny = max(1, int(hh / (8.0 * v.k)))
        for i in range(nx):
            for j in range(ny):
                roll = rng.random()
                c2 = rng.random()
                x, y, red = pos((i + 0.5) / nx, (j + 0.6) / (ny + 0.4) * hh)
                if red == "dark" or (red and WIN_P[state] > 0) or roll > restyle.TH['win']:
                    continue
                if RING['p'] > 0 and ring_off(x / v.s + v.x0, y / v.s + v.y0, c2):  # round 31: the blackout ring
                    continue
                col = ink if c2 < 0.45 else warm
                if band == 0:
                    col = lowpoly.mix(col, (0, 0, 0), 0.25)
                d.polygon(quad(x, y, 1.6 * v.k, 1.0, 1.6), fill=col)
        # the Cell's red: a finer grid of lit windows, only where the facade lies inside the crest
        nx = max(1, int(L / (4.4 * v.k)))
        ny = max(1, int(hh / (5.2 * v.k)))
        for i in range(nx):
            for j in range(ny):
                roll, fl = rng.random(), rng.random()
                x, y, red = pos((i + 0.5) / nx, (j + 0.6) / (ny + 0.4) * hh)
                if red is not True or roll > WIN_P[state]:
                    continue
                col = RED[state]
                if crest.disp:
                    if fl < 0.06:
                        col = (255, 235, 235)
                    elif fl < 0.15:
                        continue
                if band == 0:
                    col = lowpoly.mix(col, (0, 0, 0), 0.18)
                q = quad(x, y, 1.45 * v.k, 1.2, 1.8)
                d.polygon(q, fill=col)
                if gl is not None:
                    gl.polygon(q, fill=tuple(int(c * (1.0 if crest.disp else 0.75)) for c in col))
                REDL[0].polygon(q, fill=col)
    restyle.Restyler.ext = ext
    restyle.Restyler.windows = windows


REDL = [None]
DARK = [None]
# ROUND 31: THE BLACKOUT RING. Around the fist the city's own window lights flicker off in a rough ring, so the red fist
# stands in a dark moat. RING p = how far the blackout has gone (0..1), f = animation frame (flicker near the edge).
RING = dict(p=0.0, f=0, cx=0.0, cy=0.0, rx=1.0, ry=1.0)
CREST = [None]


def ring_rho(X, Y):
    dx, dy = (X - RING["cx"]) / RING["rx"], (Y - RING["cy"]) / RING["ry"]
    a = math.atan2(dy, dx)
    rough = 1.0 + 0.10 * math.sin(3 * a + 0.7) + 0.07 * math.sin(7 * a + 2.1) + 0.04 * math.sin(13 * a)  # a rough circle
    return math.hypot(dx, dy) / rough


def ring_weight(X, Y):
    """1 inside the ring band (between the fist and the outer edge), fading out past the edge; 0 on the fist itself."""
    r = ring_rho(X, Y)
    if r < 0.5 or CREST[0].inside(X, Y):
        return 0.0
    if r < 1.7:
        return 1.0
    return max(0.0, 1.0 - (r - 1.7) / 0.4)


def ring_off(X, Y, t):
    """Window at city px X, Y with its own seeded value t: off once the blackout reaches it, flickering at the front."""
    w = ring_weight(X, Y)
    if w <= 0:
        return False
    p = RING["p"] * w
    if t < p - 0.12:
        return True
    if t < p + 0.12:  # the flicker front: on / off by frame
        return random.Random(int(t * 1e6) * 31 + RING["f"]).random() < 0.55
    return False


VARIANT = "A"


def render(job):
    global VARIANT, V_, CREST_H, CREST_LIFT, WIN_P
    from PIL import ImageDraw, ImageFilter, ImageChops
    parts = job.split(":")
    VARIANT, state = parts[0], parts[1]
    ring = len(parts) > 2 and parts[2] == "ring"
    RING["p"] = float(parts[3]) if ring else 0.0
    RING["f"] = int(parts[4]) if ring and len(parts) > 4 else 0
    tag = "%s_%s%s" % (VARIANT, state, ("_ring_%02d" % RING["f"]) if len(parts) > 4 else ("_ring" if ring else ""))
    V_ = VAR[VARIANT]
    CREST_H, CREST_LIFT, WIN_P = V_["h"], V_["lift"], V_["win"]
    d = json.load(open(os.path.join(SRC, "city_layout.json")))
    info = grid27.patch(d)  # no fist streets: the normal grid through the district
    L = CD.Lots(d)
    X, Y = L.iso(*info["palm"])
    crest = Crest(X, Y - CREST_LIFT, state)
    RING.update(cx=X, cy=Y - CREST_LIFT, rx=CREST_H * 0.62, ry=CREST_H * 0.55)
    CREST[0] = crest
    install(crest, state)
    V.set_theme("night")
    vw = d["view"]
    full = View(0, 0, vw["zoom"], vw["w"], vw["h"])
    lowpoly.W, lowpoly.H = full.w, full.h
    red_img = Image.new("RGB", (full.w * SS, full.h * SS), (0, 0, 0))
    REDL[0] = ImageDraw.Draw(red_img)
    R = V.ViewRestyler(d, full, "night", False)
    R.terr_col["rebel_cell"] = R.terr_col.get("", (200, 200, 200))  # normal city buildings: no district tint
    img = R.render().convert("RGB")
    # round 32: the detail lines read crisp: a screen-space darkening of the blacked-out lines (and their red spill)
    import numpy as np
    zz_ = vw["zoom"]
    q = 3
    hq, wq = full.h // q, full.w // q
    m = np.zeros((hq, wq), np.float32)
    x0q = int((crest.cx - 7 * crest.k) * zz_ / q)
    x1q = int((crest.cx + 7 * crest.k) * zz_ / q)
    y0q = int((crest.cy - 15 * crest.k) * zz_ / q)
    y1q = int((crest.cy + 1 * crest.k) * zz_ / q)
    for yq in range(max(0, y0q), min(hq, y1q)):
        for xq in range(max(0, x0q), min(wq, x1q)):
            if crest.zone((xq + 0.5) * q / zz_, (yq + 0.5) * q / zz_) == 2:
                m[yq, xq] = 1.0
    mi = Image.fromarray((m * 255).astype(np.uint8)).resize((full.w, full.h), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.5))
    mask = np.asarray(mi, np.float32) / 255
    DARK[0] = mask
    if RING["p"] > 0:  # the blackout also dims the roof trims and street glow inside the ring (power cut)
        import numpy as np
        z_ = vw["zoom"]
        yy, xx = np.mgrid[0:full.h, 0:full.w].astype(np.float32)
        Xc, Yc = xx / z_, yy / z_
        dx, dy = (Xc - RING["cx"]) / RING["rx"], (Yc - RING["cy"]) / RING["ry"]
        a = np.arctan2(dy, dx)
        rough = 1.0 + 0.10 * np.sin(3 * a + 0.7) + 0.07 * np.sin(7 * a + 2.1) + 0.04 * np.sin(13 * a)
        r = np.hypot(dx, dy) / rough
        wgt = np.clip((r - 0.5) / 0.15, 0, 1) * np.clip(1 - (r - 1.7) / 0.4, 0, 1)
        u = (Xc - crest.cx) / crest.k
        vv = (crest.cy - Yc) / crest.k
        inside = np.zeros_like(u, bool)
        for (a0, a1, b0, b1) in crest.parts:
            inside |= (u >= a0 - 0.3) & (u <= a1 + 0.3) & (vv >= b0 - 0.3) & (vv <= b1 + 0.3)
        wgt = wgt * (1 - inside)
        from PIL import ImageFilter as _IF
        wgt = np.asarray(Image.fromarray((wgt * 255).astype(np.uint8)).filter(_IF.GaussianBlur(4)), np.float32) / 255
        dim = 1 - 0.55 * RING["p"] * wgt
        arr = np.asarray(img, np.float32) * dim[..., None]
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    # the red lights spill: a soft glow of the red windows over the streets and facades between them
    rl = red_img.resize((full.w // 2, full.h // 2), Image.BILINEAR)
    for rad, k in (V_["dglow"] if state == "dispatch" else V_["glow"]):
        g = rl.filter(ImageFilter.GaussianBlur(rad)).resize((full.w, full.h), Image.BILINEAR).point(lambda x, k=k: min(255, int(x * k * 2.2)))
        img = ImageChops.screen(img, g)
    if DARK[0] is not None:
        arr = np.asarray(img, np.float32) * (1 - 0.62 * DARK[0][..., None])
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    z = vw["zoom"]
    cx, cy = X * z, (Y - CREST_LIFT) * z  # the crop is centred on the crest
    w_, h_ = 1500, 1080
    x0_ = int(min(max(cx - w_ / 2, 0), img.width - w_))
    y0_ = int(min(max(cy - h_ / 2, 0), img.height - h_))
    img.crop((x0_, y0_, x0_ + w_, y0_ + h_)).save(os.path.join(DST, "map32_%s_crop.png" % tag))
    if len(parts) > 4:  # an animation frame: the crop is enough
        print("frame", tag, flush=True)
        return
    img = labels(img, d, full)
    img.save(os.path.join(DST, "map32_%s.png" % tag))
    print("map", VARIANT, state, flush=True)


if __name__ == "__main__":
    import subprocess
    os.makedirs(DST, exist_ok=True)
    jobs = sys.argv[1:] or ["A:home", "A:dispatch", "A:home:ring:1.0", "A:dispatch:ring:1.0"]
    if len(jobs) == 1:
        render(jobs[0])
    else:
        for j in jobs:
            subprocess.run([sys.executable, os.path.abspath(__file__), j], check=True)
