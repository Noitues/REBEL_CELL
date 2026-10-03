"""Round 29: THE RED LIGHTS. The Cell's district keeps the city's own buildings (no fist streets: grid27.patch completes
the normal street grid; nothing is painted, nothing floats). The only mark is the WINDOW LIGHT: every lit window whose
position on the map falls inside the Cell's crest burns red, and more of them are lit, so the fist reads from the
pattern of red lights across many ordinary buildings.

  home     : warm signal red, ~3.5x the city's window density inside the crest, soft red glow.
  dispatch : harsher red, every window lit, the crest torn by glitch bands (rows shifted sideways), a few windows
             flashing white / dead, stronger glow.

Same pipeline as the city maps (round 6 restyler over the game's own layout, read-only; night theme; labels). The other
HQs are the round 6 map drawings (placeholders: the round 25-30 HQ sprites live in other rounds' scratch).
python map29.py [home|dispatch] -> ../scratch/map29_<state>.png (3840 x 2160 + crops)
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

CREST_H = 1500.0  # crest height, city px (the whole district)
CREST_LIFT = 500.0  # crest centre above the palm's ground point, city px (windows sit up the facades)
WIN_P = {"home": 0.80, "dispatch": 1.0}
RED = {"home": (238, 46, 44), "dispatch": (255, 16, 30)}


def crest_parts():
    parts = []
    for i in range(4):
        x0 = -5.2 + i * 2.65
        parts.append((x0, x0 + 2.15, 8.6, 13.3 + (0.7 if i in (1, 2) else 0)))
    parts.append((-5.2, 5.5, 5.3, 8.0))
    parts.append((-3.5, 3.5, 0.0, 4.9))
    return parts


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

    def inside(self, X, Y):
        u = (X - self.cx) / self.k
        v = (self.cy - Y) / self.k
        if self.disp:
            u -= self.bands.get(int(math.floor(v / 0.9)), 0.0)
        return any(a0 <= u <= a1 and b0 <= v <= b1 for (a0, a1, b0, b1) in self.parts)


def install(crest, state):
    orig_ext = restyle.Restyler.ext

    def ext(self, d, pr, gl):
        self._gl = gl
        orig_ext(self, d, pr, gl)

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
            return x, y, crest.inside(x / v.s + v.x0, y / v.s + v.y0)

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
                if red or roll > restyle.TH['win']:
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
                if not red or roll > WIN_P[state]:
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


def render(state):
    from PIL import ImageDraw, ImageFilter, ImageChops
    d = json.load(open(os.path.join(SRC, "city_layout.json")))
    info = grid27.patch(d)  # no fist streets: the normal grid through the district
    L = CD.Lots(d)
    X, Y = L.iso(*info["palm"])
    crest = Crest(X, Y - CREST_LIFT, state)
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
    # the red lights spill: a soft glow of the red windows over the streets and facades between them
    rl = red_img.resize((full.w // 2, full.h // 2), Image.BILINEAR)
    for rad, k in (((5, 0.75), (20, 0.75)) if state == "dispatch" else ((5, 0.45), (20, 0.38))):
        g = rl.filter(ImageFilter.GaussianBlur(rad)).resize((full.w, full.h), Image.BILINEAR).point(lambda x, k=k: min(255, int(x * k * 2.2)))
        img = ImageChops.screen(img, g)
    z = vw["zoom"]
    cx, cy = X * z, (Y - CREST_LIFT) * z  # the crop is centred on the crest
    w_, h_ = 1500, 1080
    x0_ = int(min(max(cx - w_ / 2, 0), img.width - w_))
    y0_ = int(min(max(cy - h_ / 2, 0), img.height - h_))
    img.crop((x0_, y0_, x0_ + w_, y0_ + h_)).save(os.path.join(DST, "map29_%s_crop.png" % state))
    img = labels(img, d, full)
    img.save(os.path.join(DST, "map29_%s.png" % state))
    print("map", state, flush=True)


if __name__ == "__main__":
    import subprocess
    os.makedirs(DST, exist_ok=True)
    jobs = sys.argv[1:] or ["home", "dispatch"]
    if len(jobs) == 1:
        render(jobs[0])
    else:
        for j in jobs:
            subprocess.run([sys.executable, os.path.abspath(__file__), j], check=True)
