"""Route map graph, A-variants: the Blender G-buffer of the round 38 transit camera, at 1920x1080, and the per-building
relight that makes a branch BLOOM UP ITS BUILDINGS.

Passes (unified39.py, Blender 5.2 headless, ../scratch/bl/t_run38_*): beauty, the night window emission (glow), world
normal, per-building id (the 'bid' attribute: one colour per building), world position (pos.npy) and ground-only position.
The bloom is deferred light on that real geometry: windows are the city kit's own window grid (1.6 BU bays, 1.9 BU
floors, first floor at 1.6 BU), lit floor by floor up to a climbing height; a neon trace runs up the building's
vertical edges and along its roofline; the climb front is a bright line. In Godot the same thing is one per-building
uniform (climb 0..1, colour) on the facade shader (NOTES: build specs).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageFilter  # noqa: E402

BL = os.path.join(os.path.dirname(HERE), "scratch", "bl")
W, H = 1920, 1080
FLOOR = 1.9           # the kit's floor pitch (BU)
FLOOR0 = 1.6          # first window row
BAY = 1.6             # window bay pitch along a wall
WIN_W, WIN_H = 0.8, 0.7


def _rs(a, tag):
    h0, w0 = a.shape[:2]
    ry = (np.arange(H) * h0 / H).astype(int)
    rx = (np.arange(W) * w0 / W).astype(int)
    return a[ry][:, rx]


class GBuf:
    def __init__(self, tag="t_run38"):
        b = os.path.join(BL, tag + "_")
        self.pos = _rs(np.load(b + "pos.npy").astype(np.float32), tag)
        if os.path.exists(b + "gpos.npy"):
            self.gpos = _rs(np.load(b + "gpos.npy").astype(np.float32), tag)
        else:                                      # street (perspective, 'lite' passes): no ground-only pass
            self.gpos = self.pos.copy()
            self.gpos[..., 2] = 0.0
        v = np.asarray(Image.open(b + "normal.png").convert("RGB"), np.float32) / 255.0
        v = np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)     # the PNG is sRGB-encoded: back to linear
        self.nrm = _rs(v, tag) * 2 - 1
        self.glow = _rs(np.asarray(Image.open(b + "glow_night.png").convert("RGB"), np.float32) / 255.0, tag)
        self.z = self.pos[..., 2]
        self.idc = self.footprint_index()          # one exact index per building (footprints), not the id colours
        self.bld = (self.z > 0.25) & (np.abs(self.pos - self.gpos).max(axis=2) > 0.2) & (np.abs(self.pos).max(axis=2) < 3000)
        nz = self.nrm[..., 2]
        self.roof = self.bld & (nz > 0.6)
        self.wall = self.bld & (nz < 0.4)
        # vertical + roof edges: where the building id or the face normal changes (the lines a neon trace follows)
        e = np.zeros((H, W), bool)
        for dy, dx in ((0, 1), (1, 0)):
            a = self.idc
            sh = np.roll(np.roll(a, dy, 0), dx, 1)
            e |= (a != sh)
            n2 = np.roll(np.roll(self.nrm, dy, 0), dx, 1)
            e |= (np.abs(self.nrm - n2).sum(axis=2) > 0.5) & self.bld
        self.edge = e & self.bld
        self._top = {}
        self.clip = {}

    def footprint_index(self, res=8):
        """Per pixel: the index of the building whose footprint (unified.json, lot space) holds the pixel's world
        position (walls sit on the outline: the outline is drawn 2 cells wide). Taller buildings are drawn last."""
        import json
        from PIL import ImageDraw
        os.environ.setdefault("NET36", "net_scope.json")
        import layout36 as L
        u = json.load(open(os.path.join(L.DST, "unified.json")))["buildings"]
        lx, ly = L.lots(self.pos[..., 0], self.pos[..., 1])
        m = (self.z > 0.2) & (np.abs(self.pos).max(axis=2) < 3000)   # (the sky has no position)
        x0, x1 = float(np.floor(lx[m].min())) - 1, float(np.ceil(lx[m].max())) + 1
        y0, y1 = float(np.floor(ly[m].min())) - 1, float(np.ceil(ly[m].max())) + 1
        gw, gh = int((x1 - x0) * res), int((y1 - y0) * res)
        grid = Image.new("I", (gw, gh), 0)
        d = ImageDraw.Draw(grid)
        bl = [(b["h"], k, b) for k, b in enumerate(u) if any(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for p in b["q"])]
        for h, k, b in sorted(bl, key=lambda t: (t[0], t[1])):
            pts = [((p[0] - x0) * res, (p[1] - y0) * res) for p in b["q"]]
            d.polygon(pts, fill=k + 1, outline=k + 1)
            d.line(pts + [pts[0]], fill=k + 1, width=3)
        g = np.asarray(grid, np.int32)
        gx = np.clip(((lx - x0) * res).astype(int), 0, gw - 1)
        gy = np.clip(((ly - y0) * res).astype(int), 0, gh - 1)
        idx = g[gy, gx]
        idx[~m] = 0
        return idx

    # ------------------------------------------------------------ building lookup
    def building_at(self, x, y, r=10):
        """The id of the building under screen point (x, y): the most common building id in a small disc."""
        x, y = int(x), int(y)
        if not (r <= x < W - r and r <= y < H - r):
            return None                            # off screen
        ys, xs = np.mgrid[max(0, y - r):min(H, y + r), max(0, x - r):min(W, x + r)]
        m = self.bld[ys, xs]
        if not m.any():
            return None
        ids, cnt = np.unique(self.idc[ys, xs][m], return_counts=True)
        return int(ids[np.argmax(cnt)])

    def mask(self, bid):
        m = self.idc == bid
        if bid in self.clip:                      # id colours can repeat far away: keep the region near the node
            x0, y0, x1, y1 = self.clip[bid]
            c = np.zeros_like(m)
            c[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = True
            m &= c
        return m

    def set_clip(self, bid, box):
        if bid is not None and bid not in self.clip:
            self.clip[bid] = tuple(int(v) for v in box)
            self._top.pop(bid, None)

    def top(self, bid):
        if bid not in self._top:
            m = self.mask(bid) & self.bld
            self._top[bid] = float(self.z[m].max()) if m.any() else 1.0
        return self._top[bid]

    def roof_point(self, bid):
        """Screen point of the building's roof centre (mean of its roof pixels, else its top pixels)."""
        m = self.mask(bid) & self.roof
        if m.sum() < 8:
            m = self.mask(bid) & (self.z > self.top(bid) - 0.4)
        ys, xs = np.nonzero(m)
        return float(xs.mean()), float(ys.mean())

    def buildings_near_path(self, pts, rad=22, min_px=150, exclude=()):
        """Buildings the path runs past: ids covering >= min_px pixels inside a band of rad px around the polyline."""
        from PIL import ImageDraw
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).line([tuple(p) for p in pts], fill=255, width=rad * 2, joint="curve")
        band = (np.asarray(m) > 0) & self.bld
        ids, cnt = np.unique(self.idc[band], return_counts=True)
        return [int(i) for i, c in zip(ids, cnt) if c >= min_px and int(i) not in exclude]

    # ------------------------------------------------------------ the bloom (deferred, on the real facades)
    def windows(self):
        """Every window bay of the kit's grid on walls (procedural, from world position + wall facing)."""
        if hasattr(self, "_win"):
            return self._win
        x, y, z = self.pos[..., 0], self.pos[..., 1], self.z
        facing_x = np.abs(self.nrm[..., 0]) > np.abs(self.nrm[..., 1])
        u = np.where(facing_x, y, x)
        uu = np.mod(u, BAY)
        zz = z - FLOOR0
        fl = np.floor(zz / FLOOR)
        vv = zz - fl * FLOOR
        win = self.wall & (uu > 0.4) & (uu < 0.4 + WIN_W) & (vv > 0) & (vv < WIN_H) & (zz > 0)
        self._win = (win, fl)
        return self._win

    def bloom(self, bid, climb, col, k=1.0, seed=0, trace=True, flicker=None, wash=0.22):
        """Emission (H, W, 3) for one building: windows lit floor by floor up to climb (0..1 of its height), a facade
        wash under the climb front, the climb front line, neon traces up its edges and, at climb 1, its roofline."""
        em = np.zeros((H, W, 3), np.float32)
        if bid is None or climb <= 0:
            return em
        m = self.mask(bid) & self.bld
        top = self.top(bid)
        zc = climb * (top + 0.4)
        win, fl = self.windows()
        rng = np.random.RandomState(seed + (bid % 9973))
        lut = rng.uniform(0.55, 1.0, 64).astype(np.float32)
        lit_fl = np.floor((zc - FLOOR0) / FLOOR)                       # whole floors only: floor by floor
        w = m & win & (fl <= lit_fl)
        wk = lut[np.clip(fl, 0, 63).astype(int)] if True else 1.0
        if flicker is not None:
            wk = wk * flicker
        c = np.array(col, np.float32) / 255.0
        em += (w * wk)[..., None] * (c * 0.8 + 0.2) * 1.35 * k     # the window cores run hot (toward white)
        below = m & self.wall & (self.z < zc)
        fade = np.clip(1 - (zc - self.z) / max(1.0, top), 0.15, 1)
        em += (below * fade * wash)[..., None] * c * k
        front = m & (np.abs(self.z - zc) < 0.22) & self.wall
        em += (front * 0.9)[..., None] * c * k
        if trace:
            e = self.edge & m & (self.z < zc + 0.1)
            em += (e * 0.95)[..., None] * c * k
            if climb >= 0.98:
                rim = self.edge & m & (self.z > top - 0.35)
                em += (rim * 1.2)[..., None] * c * k
                em += (m & self.roof)[..., None] * c * 0.18 * k
        return em

    def calm(self, em_scale=0.55):
        """The city's own window emission (for blackout variants)."""
        return self.glow * em_scale


def add_emission(img, em, glow_r=(4, 14), glow_k=(0.9, 0.55)):
    """Composite emission onto an RGBA image: core + two blurred glows (bloom)."""
    a = np.asarray(img.convert("RGB"), np.float32) / 255.0
    e8 = Image.fromarray((np.clip(em, 0, 1) * 255).astype(np.uint8))
    out = a + em
    for r, k in zip(glow_r, glow_k):
        g = np.asarray(e8.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255.0
        out = out + g * k
    o = Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")
    return o
