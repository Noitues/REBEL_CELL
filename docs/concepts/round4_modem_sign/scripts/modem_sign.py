"""modem_sign.py - the MODEM / CYBER SHOP circuit-board neon sign, Cv2 edition.

Layers (all deterministic, seeded numpy Generator):
  plate    : dark triangulated low-poly PCB panel, a few copper-tone facets, faceted bezel
  tubes    : double-line (hollow) emissive glass neon letters + frame tube
  traces   : PCB traces routed on a grid with 45-degree bends, solder pads, vias, SMD chips
  pulses   : data packets travelling along the traces (idle)
Emission is HDR; the plate is lit by its own tubes; the same emission drives the light
spill onto the shop scene (see shop_with_sign.py).

Plate-local units are 1x pixels; masks are drawn at SS=2 and reduced.
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))  # docs/concepts
OUT = os.path.join(ROOT, "round4_modem_sign")
sys.path.insert(0, os.path.join(ROOT, "round3_overlay", "o_d_light_pen", "scripts"))
from lightpen import gblur, tonemap  # noqa: E402  (the shared spill/glow pass)

SS = 2
R = 1          # output scale (1 = 1x; the close-up renders at R=3)
SR = SS * R


def set_scale(r):
    global R, SR
    R, SR = r, SS * r
PW, PH = 250, 1034            # plate size
MARGIN = 70                   # glow margin around the plate in the RGBA canvas
CW, CH = PW + 2 * MARGIN, PH + 2 * MARGIN
SHOP_PLATE_XY = (22, 22)      # plate top-left in the 1920x1080 shop composition

PINK = np.array([1.0, 0.16, 0.6], np.float32)
CYAN = np.array([0.28, 0.88, 1.0], np.float32)
PINK_OFF = np.array([0.30, 0.16, 0.24], np.float32)
CYAN_OFF = np.array([0.14, 0.24, 0.28], np.float32)

# ------------------------------------------------------------------ letters
LET = {
    "M": [[(0, 1), (0, 0), (0.5, 0.42), (1, 0), (1, 1)]],
    "O": [[(0.28, 0), (0.72, 0), (1, 0.16), (1, 0.84), (0.72, 1), (0.28, 1), (0, 0.84), (0, 0.16),
           (0.28, 0)]],
    "D": [[(0, 0), (0.62, 0), (1, 0.24), (1, 0.76), (0.62, 1), (0, 1), (0, 0)]],
    "E": [[(1, 0), (0, 0), (0, 1), (1, 1)], [(0, 0.5), (0.74, 0.5)]],
    "C": [[(1, 0.16), (0.84, 0), (0.16, 0), (0, 0.16), (0, 0.84), (0.16, 1), (0.84, 1), (1, 0.84)]],
    "Y": [[(0, 0), (0.5, 0.48), (1, 0)], [(0.5, 0.48), (0.5, 1)]],
    "B": [[(0, 0.5), (0.78, 0.5), (1, 0.64), (1, 0.86), (0.82, 1), (0, 1), (0, 0), (0.74, 0),
           (0.94, 0.12), (0.94, 0.36), (0.78, 0.5)]],
    "R": [[(0, 1), (0, 0), (0.8, 0), (1, 0.14), (1, 0.38), (0.8, 0.5), (0, 0.5)], [(0.46, 0.5), (1, 1)]],
    "S": [[(1, 0.12), (0.86, 0), (0.14, 0), (0, 0.12), (0, 0.38), (0.14, 0.5), (0.86, 0.5), (1, 0.62),
           (1, 0.88), (0.86, 1), (0.14, 1), (0, 0.88)]],
    "H": [[(0, 0), (0, 1)], [(1, 0), (1, 1)], [(0, 0.5), (1, 0.5)]],
    "P": [[(0, 1), (0, 0), (0.8, 0), (1, 0.15), (1, 0.38), (0.8, 0.5), (0, 0.5)]],
}

MODEM_BOX = dict(x=73, w=104, h=124, y0=46, step=146, W=22, t=3.6)
CYBER_BOX = dict(y=800, h=54, w=32, gap=5, W=11, t=2.5)
SHOP_BOX = dict(y=872, h=54, w=34, gap=6, W=11, t=2.5)
FRAME = dict(inset=13, W=11, t=2.6, r=30)


def element_list():
    """[(name, letter, x, y, w, h, W, t, colour)] in plate coords."""
    out = []
    b = MODEM_BOX
    for i, ch in enumerate("MODEM"):
        out.append((f"modem{i}", ch, b["x"], b["y0"] + i * b["step"], b["w"], b["h"], b["W"], b["t"], "pink"))
    for word, box, key in (("CYBER", CYBER_BOX, "cyber"), ("SHOP", SHOP_BOX, "shop")):
        tot = len(word) * box["w"] + (len(word) - 1) * box["gap"]
        x0 = (PW - tot) / 2
        for i, ch in enumerate(word):
            out.append((key, ch, x0 + i * (box["w"] + box["gap"]), box["y"], box["w"], box["h"],
                        box["W"], box["t"], "cyan"))
    return out


def _canvas(v=0):
    return Image.new("L", (CW * SR, CH * SR), v)


def _P(x, y):  # plate coords -> supersampled canvas coords
    return ((x + MARGIN) * SR, (y + MARGIN) * SR)


def _poly_stroke(draw, pts, width, fill=255):
    pp = [_P(*p) for p in pts]
    draw.line(pp, fill=fill, width=int(round(width * SR)), joint="curve")
    r = width * SR / 2
    for q in (pp[0], pp[-1]):
        draw.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=fill)


def _arr(im):
    return np.asarray(im.reduce(SS), np.float32) / 255.0


def tube_masks():
    """Per-element hollow tube outline masks + letter 'solid' masks (for routing)."""
    tubes, solids = {}, {}
    for name, ch, x, y, w, h, W, t, col in element_list():
        A, B = _canvas(), _canvas()
        da, db = ImageDraw.Draw(A), ImageDraw.Draw(B)
        for stroke in LET[ch]:
            pts = [(x + W / 2 + u * (w - W), y + W / 2 + v * (h - W)) for u, v in stroke]
            _poly_stroke(da, pts, W)
            _poly_stroke(db, pts, W - 2 * t)
        a, bb = np.asarray(A, np.float32), np.asarray(B, np.float32)
        ring = Image.fromarray(np.clip(a - bb, 0, 255).astype(np.uint8))
        key = name
        tubes[key] = np.maximum(tubes.get(key, 0), _arr(ring))
        solids[key] = np.maximum(solids.get(key, 0), _arr(A))
    # frame tube: hollow rounded rectangle
    f = FRAME
    A, B = _canvas(), _canvas()
    box = [*_P(f["inset"], f["inset"]), *_P(PW - f["inset"], PH - f["inset"])]
    ImageDraw.Draw(A).rounded_rectangle(box, radius=f["r"] * SR, outline=255, width=int(f["W"] * SR))
    inner = [box[0] + f["t"] * SR, box[1] + f["t"] * SR, box[2] - f["t"] * SR, box[3] - f["t"] * SR]
    ImageDraw.Draw(B).rounded_rectangle(inner, radius=(f["r"] - f["t"]) * SR, outline=255,
                                        width=int((f["W"] - 2 * f["t"]) * SR))
    ring = np.clip(np.asarray(A, np.float32) - np.asarray(B, np.float32), 0, 255).astype(np.uint8)
    tubes["frame"] = _arr(Image.fromarray(ring))
    solids["frame"] = _arr(A)
    return tubes, solids


def plate_mask():
    im = _canvas()
    ImageDraw.Draw(im).rounded_rectangle([*_P(0, 0), *_P(PW, PH)], radius=40 * SR, fill=255)
    return _arr(im)


# ------------------------------------------------------------------ backing plate
def facet_plate(rng):
    """Triangulated low-poly PCB panel (albedo, canvas sized)."""
    W, H = CW * SR, CH * SR
    im = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(im)
    cell = 30 * SR
    nx, ny = W // cell + 3, H // cell + 3
    pts = np.zeros((ny, nx, 2))
    for j in range(ny):
        for i in range(nx):
            pts[j, i] = ((i - 1) * cell + rng.uniform(-0.4, 0.4) * cell,
                         (j - 1) * cell + rng.uniform(-0.4, 0.4) * cell)
    base = np.array([0.050, 0.068, 0.066])       # dark solder-mask green-black
    copper = np.array([0.30, 0.16, 0.075])        # copper pour showing through
    for j in range(ny - 1):
        for i in range(nx - 1):
            a, b, c, e = pts[j, i], pts[j, i + 1], pts[j + 1, i], pts[j + 1, i + 1]
            for tri in ((a, b, c), (b, e, c)):
                cy = np.mean([p[1] for p in tri]) / H
                cx = np.mean([p[0] for p in tri]) / W
                k = rng.uniform(0.72, 1.22) * (1.08 - 0.25 * cy) * (1.05 - 0.15 * cx)
                col = base * k
                if rng.random() < 0.12:
                    col = col * 0.6 + copper * rng.uniform(0.18, 0.36)
                d.polygon([tuple(p) for p in tri], fill=tuple(int(255 * min(1, v)) for v in col))
    alb = np.asarray(im.reduce(SS), np.float32) / 255.0
    # faceted metal bezel band around the edge
    pm = plate_mask()
    inner = Image.new("L", (CW * SR, CH * SR), 0)
    ImageDraw.Draw(inner).rounded_rectangle([*_P(7, 7), *_P(PW - 7, PH - 7)], radius=34 * SR, fill=255)
    inner = _arr(inner)
    bez = np.clip(pm - inner, 0, 1)[..., None]
    gray = alb.mean(-1, keepdims=True) * np.array([1.9, 1.85, 2.1]) + 0.03
    alb = alb * (1 - bez) + gray * bez
    return alb, pm


# ------------------------------------------------------------------ PCB traces
class Trace:
    def __init__(self, pts, kind_end):
        self.pts = np.asarray(pts, np.float64)
        d = np.sqrt(((self.pts[1:] - self.pts[:-1]) ** 2).sum(1))
        self.s = np.concatenate([[0], np.cumsum(d)])
        self.L = self.s[-1]
        self.end = kind_end
        self.dense = self._dense()

    def _dense(self):
        n = max(2, int(self.L) + 1)
        u = np.linspace(0, self.L, n)
        return np.stack([np.interp(u, self.s, self.pts[:, 0]), np.interp(u, self.s, self.pts[:, 1])], 1)


CHIPS = [  # x, y, w, h (plate coords), pins on the long sides
    (36, 958, 44, 22), (118, 954, 58, 26), (194, 970, 26, 16),
    (32, 430, 30, 16), (190, 262, 30, 16), (190, 650, 30, 16),
]

DIRS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


def route_traces(solids, rng, cell=6, n_try=2500):
    nx, ny = PW // cell, PH // cell
    # blocked cells: plate edge band, tubes (dilated), chips
    blocked = np.zeros((ny, nx), bool)
    occ = np.zeros((CH * R, CW * R), np.float32)
    for k, m in solids.items():
        occ = np.maximum(occ, m)
    occ = gblur(occ, 3.0 * R) > 0.03
    for j in range(ny):
        for i in range(nx):
            x0, y0 = (MARGIN + i * cell) * R, (MARGIN + j * cell) * R
            if occ[y0:y0 + cell * R, x0:x0 + cell * R].any():
                blocked[j, i] = True
    for _, ch, x, y, w, h, W, t, col in element_list():  # letter counters stay clean
        i0, i1 = int((x - 4) // cell), int((x + w + 4) // cell)
        j0, j1 = int((y - 4) // cell), int((y + h + 4) // cell)
        blocked[max(0, j0):j1 + 1, max(0, i0):i1 + 1] = True
    edge = 28
    for j in range(ny):
        for i in range(nx):
            cx, cy = i * cell + cell / 2, j * cell + cell / 2
            if cx < edge or cx > PW - edge or cy < edge or cy > PH - edge:
                blocked[j, i] = True
    pins = []
    for (x, y, w, h) in CHIPS:
        i0, i1 = int(x // cell), int((x + w - 1) // cell)
        j0, j1 = int(y // cell), int((y + h - 1) // cell)
        blocked[max(0, j0):j1 + 1, max(0, i0):i1 + 1] = True
        horiz = w >= h
        npin = max(2, int((w if horiz else h) // 10))
        for k in range(npin):
            f = (k + 0.5) / npin
            if horiz:
                px = x + f * w
                pins.append(((px, y), (0, -1)))
                pins.append(((px, y + h), (0, 1)))
            else:
                py = y + f * h
                pins.append(((x, py), (-1, 0)))
                pins.append(((x + w, py), (1, 0)))
    used = blocked.copy()
    traces = []

    def walk(i, j, d, budget):
        path = [(i, j)]
        di = DIRS.index(d)
        seg = rng.integers(2, 7)
        own = {(i, j)}
        for _ in range(budget):
            if seg <= 0:
                turn = rng.choice([-1, 1]) * (1 if rng.random() < 0.8 else 2)
                di = (di + turn) % 8
                seg = rng.integers(2, 9)
            dx, dy = DIRS[di]
            ni, nj = path[-1][0] + dx, path[-1][1] + dy
            if not (0 <= ni < nx and 0 <= nj < ny) or used[nj, ni] or (ni, nj) in own:
                break
            if dx and dy and (used[path[-1][1], ni] and used[nj, path[-1][0]]):
                break
            path.append((ni, nj))
            own.add((ni, nj))
            seg -= 1
        return path

    def commit(path, start_px=None, spacing=True):
        for (i, j) in path:
            if spacing:
                used[max(0, j - 1):j + 2, max(0, i - 1):i + 2] = True
            else:
                used[j, i] = True
        pts = [((i + 0.5) * cell, (j + 0.5) * cell) for i, j in path]
        if start_px is not None:
            pts = [start_px] + pts
        traces.append(Trace(pts, "pad" if rng.random() < 0.7 else "via"))

    # 1) traces leaving chip pins
    for (px, py), (dx, dy) in pins:
        i, j = int((px + dx * cell * 0.6) // cell), int((py + dy * cell * 0.6) // cell)
        if not (0 <= i < nx and 0 <= j < ny) or used[j, i]:
            continue
        p = walk(i, j, (dx, dy), int(rng.integers(6, 26)))
        if len(p) >= 2:
            commit(p, start_px=(px, py), spacing=False)
    # 2) traces leaving the tubes / frame edge
    for _ in range(n_try):
        i, j = int(rng.integers(0, nx)), int(rng.integers(0, ny))
        if used[j, i]:
            continue
        nb = [(dx, dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= i + dx < nx and 0 <= j + dy < ny and blocked[j + dy, i + dx]]
        if not nb:
            continue
        dx, dy = nb[int(rng.integers(0, len(nb)))]
        p = walk(i, j, (-dx, -dy), int(rng.integers(5, 30)))
        if len(p) >= 4:
            commit(p)
    return traces


# ------------------------------------------------------------------ rendering
def draw_traces(traces, lit_frac=1.0, pulse_t=None, rng_phase=None):
    """Return (trace mask, pad mask, pulse mask) at canvas 1x."""
    tm, pm, pu = _canvas(), _canvas(), _canvas()
    dt, dp, du = ImageDraw.Draw(tm), ImageDraw.Draw(pm), ImageDraw.Draw(pu)
    for k, tr in enumerate(traces):
        n = len(tr.dense)
        cut = int(n * lit_frac)
        if cut >= 2:
            pts = [_P(*q) for q in tr.dense[:cut:3]] + [_P(*tr.dense[cut - 1])]
            dt.line(pts, fill=255, width=int(2.2 * SR), joint="curve")
            q = _P(*tr.dense[0])
            r = 1.6 * SR
            dt.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=255)
        if cut >= n:
            q = _P(*tr.dense[-1])
            if tr.end == "pad":
                r0, r1 = 4.4 * SR, 1.9 * SR
                dp.ellipse([q[0] - r0, q[1] - r0, q[0] + r0, q[1] + r0], fill=255)
                dp.ellipse([q[0] - r1, q[1] - r1, q[0] + r1, q[1] + r1], fill=0)
            else:
                r0 = 2.8 * SR
                dp.ellipse([q[0] - r0, q[1] - r0, q[0] + r0, q[1] + r0], fill=255)
        if pulse_t is not None and cut >= n:
            ph = rng_phase[k]
            period = tr.L * 1.7 + 60
            p = (pulse_t * 140 + ph * period) % period
            if p < tr.L:
                for d in np.arange(22, -0.1, -1.0):
                    s = p - d
                    if s < 0:
                        continue
                    idx = min(n - 1, int(s))
                    q = _P(*tr.dense[idx])
                    a = math.exp(-d / 6.0)
                    r = (1.4 + 1.6 * a) * SR
                    du.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=int(255 * a))
    return _arr(tm), _arr(pm), _arr(pu)


def draw_chips(intensity):
    """Chip bodies as two-tone facets (albedo) + pins (emissive-ish) + status LED."""
    W, H = CW * SR, CH * SR
    body = Image.new("RGB", (W, H), (0, 0, 0))
    am = Image.new("L", (W, H), 0)
    pins = _canvas()
    led = _canvas()
    db, da, dpn, dl = ImageDraw.Draw(body), ImageDraw.Draw(am), ImageDraw.Draw(pins), ImageDraw.Draw(led)
    for (x, y, w, h) in CHIPS:
        a, b, c, e = _P(x, y), _P(x + w, y), _P(x + w, y + h), _P(x, y + h)
        db.polygon([a, b, e], fill=(30, 32, 38))
        db.polygon([b, c, e], fill=(18, 19, 24))
        da.polygon([a, b, c, e], fill=255)
        horiz = w >= h
        npin = max(2, int((w if horiz else h) // 10))
        for k in range(npin):
            f = (k + 0.5) / npin
            if horiz:
                px = x + f * w
                for yy, sgn in ((y, -1), (y + h, 1)):
                    p0, p1 = _P(px - 1.6, yy), _P(px + 1.6, yy + sgn * 4)
                    dpn.rectangle([min(p0[0], p1[0]), min(p0[1], p1[1]), max(p0[0], p1[0]), max(p0[1], p1[1])], fill=255)
            else:
                py = y + f * h
                for xx, sgn in ((x, -1), (x + w, 1)):
                    p0, p1 = _P(xx, py - 1.6), _P(xx + sgn * 4, py + 1.6)
                    dpn.rectangle([min(p0[0], p1[0]), min(p0[1], p1[1]), max(p0[0], p1[0]), max(p0[1], p1[1])], fill=255)
        q = _P(x + 5, y + 5)
        r = 1.5 * SR
        dl.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=255)
    alb = np.asarray(body.reduce(SS), np.float32) / 255.0
    return alb, _arr(am), _arr(pins), _arr(led)


ELEMENTS = ["frame", "modem0", "modem1", "modem2", "modem3", "modem4", "cyber", "shop"]


class Sign:
    """Builds the static geometry once; render(state) for any warm-up / pulse state."""

    def __init__(self, seed=7, traces=None):
        rng = np.random.default_rng(seed)
        self.tubes, self.solids = tube_masks()
        self.plate_alb, self.plate_m = facet_plate(rng)
        # routing is resolution-independent; a hi-res close-up reuses the 1x routing
        self.traces = traces if traces is not None else route_traces(self.solids, np.random.default_rng(seed + 1))
        self.phase = np.random.default_rng(seed + 2).random(len(self.traces))
        self.chip_alb, self.chip_m, self.chip_pins, self.chip_led = draw_chips(1.0)
        # tube 'glass' interior (between the double lines) for the unlit look
        self.letter_fill = {k: np.clip(self.solids[k] - self.tubes[k], 0, 1) for k in self.tubes}
        # a per-element banded mask used for part-lit flicker (cold cathode warming unevenly)
        yy = np.arange(CH * R, dtype=np.float32)[:, None] / R
        self.bands = {}
        r = np.random.default_rng(seed + 3)
        for k in ELEMENTS:
            ph, fr = r.uniform(0, 6.28), r.uniform(0.02, 0.05)
            self.bands[k] = np.clip(0.5 + 0.9 * np.sin(yy * fr + ph), 0, 1) * np.ones((1, CW * R), np.float32)

    def render(self, levels, trace_frac=1.0, pulse_t=None, trace_level=1.0):
        """levels: {element: 0..1 or ('flicker', 0..1)}. Returns dict of canvas-sized arrays:
        rgb (tonemapped, sign + its glow), alpha, emis (HDR emission for spill), plate_rgb."""
        emis = np.zeros((CH * R, CW * R, 3), np.float32)
        glass = np.zeros((CH * R, CW * R, 3), np.float32)
        for k in ELEMENTS:
            lv = levels.get(k, 0.0)
            part = None
            if isinstance(lv, tuple):
                part = self.bands[k]
                lv = lv[1]
            col = CYAN if k in ("cyber", "shop") else PINK
            off = CYAN_OFF if k in ("cyber", "shop") else PINK_OFF
            t = self.tubes[k]
            m = t * (part if part is not None else 1.0)
            # warming cathode: dimmer and bluer before full brightness
            warm = col * (0.55 + 0.45 * lv) + np.array([0.2, 0.0, 0.35]) * (1 - lv) * (lv > 0)
            emis += warm[None, None] * (m * lv * 1.55)[..., None]
            core = np.clip((gblur(t, 0.6 * R) - 0.55) / 0.45, 0, 1) * (part if part is not None else 1.0)
            emis += np.array([1.0, 0.92, 0.96])[None, None] * (core * lv * 0.9)[..., None]
            glass += off[None, None] * t[..., None] * (1 - 0.6 * lv)
            glass += off[None, None] * 0.25 * self.letter_fill[k][..., None]
        tm, pdm, pum = draw_traces(self.traces, trace_frac, pulse_t, self.phase)
        tcol = np.array([1.0, 0.22, 0.62], np.float32)
        emis += tcol * (tm * 0.55 + pdm * 0.8)[..., None] * trace_level
        emis += np.array([1.0, 0.75, 0.9], np.float32) * (pum * 2.4)[..., None] * trace_level
        copper_off = np.array([0.30, 0.17, 0.09], np.float32)
        if trace_frac < 1.0:  # unlit copper is always there, only the light is still booting
            tmf, pdf, _ = draw_traces(self.traces, 1.0, None, self.phase)
        else:
            tmf, pdf = tm, pdm
        glass += copper_off * (tmf * 0.55 + pdf * 0.8)[..., None] * (1 - 0.7 * trace_level)
        emis += np.array([1.0, 0.3, 0.7], np.float32) * (self.chip_pins * 0.45)[..., None] * trace_level
        emis += CYAN * (gblur(self.chip_led, 0.7 * R) * 2.2)[..., None] * trace_level
        # albedo: plate + chips; lit by ambient + the sign's own emission
        alb = self.plate_alb * (1 - self.chip_m[..., None]) + self.chip_alb * self.chip_m[..., None]
        alb = alb + glass
        self_light = np.stack([gblur(emis[..., c], 7 * R) * 1.1 + gblur(emis[..., c], 24 * R) * 1.2
                               for c in range(3)], -1)
        plate_rgb = alb * (0.5 + self_light * 2.4) + emis
        glow = np.stack([0.45 * gblur(emis[..., c], 2.0 * R) + 0.34 * gblur(emis[..., c], 7 * R) +
                         0.26 * gblur(emis[..., c], 20 * R) + 0.14 * gblur(emis[..., c], 44 * R)
                         for c in range(3)], -1)
        pm = self.plate_m[..., None]
        rgb = plate_rgb * pm + glow
        return dict(rgb=tonemap(rgb), plate_rgb=plate_rgb, glow=glow, alpha=self.plate_m,
                    emis=emis)


# warm-up script (frame states) shared by the sheet and the strip ----------------------
LIT = {k: 1.0 for k in ELEMENTS}
WARMUP = [
    ("0.00 s  OFF", {}, 0.0, None, 0.0),
    ("0.15 s  FRAME + M STRIKE", {"frame": ("f", 0.55), "modem0": ("f", 0.7)}, 0.0, None, 0.0),
    ("0.35 s  M LIT, O FLICKERS", {"frame": 1.0, "modem0": 1.0, "modem1": ("f", 0.45)}, 0.15, None, 0.4),
    ("0.60 s  M-O-D, E WARMING", {"frame": 1.0, "modem0": 1.0, "modem1": 1.0, "modem2": 1.0,
                                  "modem3": ("f", 0.6), "cyber": ("f", 0.3)}, 0.45, None, 0.7),
    ("0.85 s  MODEM, CYBER SHOP STRIKES", {**{k: 1.0 for k in ELEMENTS[:5]}, "modem4": 0.75, "cyber": 1.0,
                                           "shop": ("f", 0.5)}, 0.8, None, 0.9),
    ("IDLE  DATA PULSES ON TRACES", LIT, 1.0, 0.0, 1.0),
]


def to_img(rgb):
    return Image.fromarray((np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8))


def font(size, var="Bold Condensed"):
    f = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", size)
    try:
        f.set_variation_by_name(var)
    except Exception:
        pass
    return f
