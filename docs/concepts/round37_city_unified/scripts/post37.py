"""Round 36 post: ONE finish for every zoom of the unified city.

finish(tag, extra=None, heat=...) -> 1920 x 1080 float RGB (or the render size / 1.5 for the gif frames)
  1. the street-plane NETWORK (Net36): sockets + links evaluated per pixel on the world-position pass, exactly like a
     ground decal shader. Their look is a function of the ZOOM (lod), not of the view: the same node at 760 / 176 / 88
     BU ortho is the same decal with more or less anatomy (see NOTES "what appears at which zoom");
  2. ink from id / normal / depth (E's hand line), grime;
  3. Heat reaction (round 35 option B: searchlight pools on whatever they hit);
  4. bloom + light spill, low fog, depth haze, rain (round 26 locked city mood).
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
import layout36 as L  # noqa: E402
import finish as F0  # noqa: E402
import netdecal19 as N19  # noqa: E402
from netdecal19 import band, sstep, sample, vnoise, hash2  # noqa: E402

ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "scratch", "bl")
C = lambda *v: np.array(v, np.float32)  # noqa: E731
LIME, ORANGE, WHITE, GREY = C(0.83, 1.0, 0.0), C(1.0, 0.52, 0.08), C(0.92, 0.93, 1.0), C(0.42, 0.42, 0.48)
GREEN, PINK, HARM, GOLD, VIOLET = C(0.55, 1.0, 0.35), C(1.0, 0.24, 0.66), C(1.0, 0.25, 0.18), C(1.0, 0.8, 0.25), C(0.6, 0.45, 1.0)
STATE_COL = {"owned": LIME, "core": PINK, "available": ORANGE, "white": WHITE, "grey": GREY}
LINK_COL = {"owned": LIME, "border": ORANGE, "white": WHITE, "grey": GREY}
NET = L.load_net()
NODES = {n["id"]: n for n in NET["nodes"]}
ORT_CITY, ORT_RAID, ORT_TRANSIT = 820.0, 176.0, 88.0


def lod_of(ortho):
    """0 = transit, 1 = raid, 2 = city (continuous)."""
    if ortho >= ORT_RAID:
        return 1 + min(1.0, math.log(ortho / ORT_RAID) / math.log(ORT_CITY / ORT_RAID))
    return max(0.0, math.log(ortho / ORT_TRANSIT) / math.log(ORT_RAID / ORT_TRANSIT))


def load_img(p):
    im = Image.open(p)
    a = np.asarray(im)
    if a.dtype == np.uint16 or im.mode.startswith("I"):
        return a.astype(np.float32) / 65535.0
    return np.asarray(im.convert("RGB"), np.float32) / 255.0


class Passes:
    def __init__(self, tag):
        b = os.path.join(SRC, tag + "_")
        self.sc = json.load(open(b + "scene.json"))
        self.cam = self.sc["cam"]
        self.pos = np.load(b + "pos.npy").astype(np.float32)
        self.gpos = np.load(b + "gpos.npy").astype(np.float32)
        self.vis = (np.abs(self.pos - self.gpos).max(axis=2) < 0.6).astype(np.float32)
        self.nrm = load_img(b + "normal.png")
        self.ids = load_img(b + "id.png")
        self.beauty = load_img(b + "beauty_night.png")
        self.glow = load_img(b + "glow_night.png")
        self.gbeauty = load_img(b + "gbeauty_night.png") if os.path.exists(b + "gbeauty_night.png") else None
        self.gglow = load_img(b + "gglow_night.png") if os.path.exists(b + "gglow_night.png") else None
        r, u, f = L.basis(self.cam)
        t = self.cam["target"]
        P = self.pos
        self.dep = (P[..., 0] - t[0]) * f[0] + (P[..., 1] - t[1]) * f[1] + (P[..., 2] - t[2]) * f[2]
        self.h, self.w = self.dep.shape


# ------------------------------------------------------------------ the network decal
class Net36:
    def __init__(self, P, t=0.0):
        self.P = P
        # evaluated on the GROUND-ONLY position pass: the whole network exists under the buildings too
        self.X, self.Y, self.Z = P.gpos[..., 0], P.gpos[..., 1], P.gpos[..., 2]
        self.G = (self.Z < 0.14) & (self.Z > -0.5)
        self.em = np.zeros(self.X.shape + (3,), np.float32)
        self.dk = np.ones(self.X.shape, np.float32)
        r, u, f = L.basis(P.cam)
        self.rh = np.array([r[0], r[1]]) / math.hypot(r[0], r[1])
        self.fh = np.array([f[0], f[1]]) / math.hypot(f[0], f[1])
        self.ortho = P.cam["ortho"]
        self.lod = lod_of(self.ortho)
        self.ppb = 1920.0 / self.ortho            # final px per BU
        self.t = t

    def px(self, n):
        """n final pixels in BU at this zoom."""
        return n / self.ppb

    def _box(self, x, y, r, mask=None):
        m = mask if mask is not None else self.G
        return (np.abs(self.X - x) < r) & (np.abs(self.Y - y) < r) & m

    # links: one fat trace at city zoom, the 3-trace bus with vias + packets from the raid zoom in
    def link(self, pts_lots, col, style="solid", k=1.0, off=0.0, trim=(True, True), packets=True):
        pts = [np.array(L.W(p), float) for p in pts_lots]
        city = min(1.0, max(0.0, self.lod - 1.0))
        S = self.sock()
        acc_s = 0.0
        for i in range(len(pts) - 1):
            pa, pb = pts[i], pts[i + 1]
            d = pb - pa
            Ls = float(np.hypot(*d))
            if Ls < 1e-3:
                continue
            ux, uy = d / Ls
            lo, hi = np.minimum(pa, pb) - 4, np.maximum(pa, pb) + 4
            m = (self.X > lo[0]) & (self.X < hi[0]) & (self.Y > lo[1]) & (self.Y < hi[1]) & self.G
            if not m.any():
                acc_s += Ls
                continue
            dx, dy = self.X[m] - pa[0], self.Y[m] - pa[1]
            s = dx * ux + dy * uy
            a = -dx * uy + dy * ux - off
            t0 = S * 0.95 if (i == 0 and trim[0]) else -0.6
            t1 = Ls - S * 0.95 if (i == len(pts) - 2 and trim[1]) else Ls + 0.6
            inside = (s > t0) & (s < t1)
            sg = acc_s + s
            # city: a single bright trace, at least ~3 px wide
            wc = max(0.35, self.px(1.6))
            tr_c = band(np.abs(a), -1, wc) + 0.35 * band(np.abs(a), -1, wc * 2.6)
            # raid / transit: three traces 1 BU apart, vias every 4 BU
            tr_r = np.zeros_like(a)
            gr = np.zeros_like(a)
            for j, o in enumerate((-0.95, 0.0, 0.95)):
                dd = np.abs(a - o)
                tr_r = np.maximum(tr_r, band(dd, -1, 0.12))
                gr = np.maximum(gr, band(dd, -1, 0.35))
                sv = np.mod(sg + j * 1.3, 4.0) - 2.0
                rv = np.hypot(sv, a - o)
                tr_r = np.maximum(tr_r, band(rv, 0.22, 0.4))
                gr = np.maximum(gr, band(rv, -1, 0.55))
            tr = tr_c * city + tr_r * (1 - city)
            if style == "dashed":
                tr = tr * (np.mod(sg - self.t * 6, 3.0 if city < 0.5 else self.px(14)) < (1.8 if city < 0.5 else self.px(8)))
            pulse = band(np.mod(sg - self.t * 24.0, 18.0 if city < 0.5 else self.px(90)), 0, 1.2 if city < 0.5 else self.px(10)) if packets else 0
            v = (tr * (1 + 1.4 * pulse)) * inside * k
            corridor = band(np.abs(a), -1, 2.4) * (1 - city) * 0.45     # the street's own lane glow steps back under a link
            self.dk[m] *= (1 - 0.5 * np.clip((gr * (1 - city) + tr_c * city) * inside, 0, 1)) * (1 - corridor * inside)
            self.em[m] += v[:, None] * col
            acc_s += Ls

    def sock(self):
        return max(2.6, self.px(13))

    def node(self, n, integ=1.0, exposed=False, flash=None, run=False, scale=1.0):
        x, y = L.W(n["lot"])
        S = self.sock() * scale * (1.18 if n["state"] == "core" else 1.0)
        m = self._box(x, y, S * 1.7)
        if not m.any():
            return
        dx, dy = self.X[m] - x, self.Y[m] - y
        ax, ay = np.abs(dx), np.abs(dy)
        cheb = np.maximum(ax, ay)
        a = dx * self.rh[0] + dy * self.rh[1]
        b = dx * self.fh[0] + dy * self.fh[1]
        city = min(1.0, max(0.0, self.lod - 1.0))
        st = n["state"]
        col = STATE_COL[st]
        if st == "owned":           # owned sockets: lime on the map, the raid's 'holds' green as you come close
            col = LIME * city + GREEN * (1 - city)
        em = np.zeros((dx.shape[0], 3), np.float32)
        dk = np.ones(dx.shape[0], np.float32)
        plate = cheb < S
        dk *= 1 - 0.65 * plate
        frame = band(cheb, S * 0.86, S * 0.98)
        if st == "white":
            per = np.mod(np.arctan2(dy, dx) / (2 * math.pi) * 24, 1.0)
            frame = frame * (per < 0.55)
        pins = np.zeros_like(cheb)
        for side, along in ((ax, ay), (ay, ax)):
            kk = np.mod(along + S * 0.12, S * 0.24) - S * 0.12
            pins = np.maximum(pins, band(side, S * 0.98, S * 1.12) * band(np.abs(kk), -1, S * 0.04) * (along < S * 0.82))
        track = band(cheb, S * 0.68, S * 0.76)
        per = np.mod((np.arctan2(dy, dx) + 3 * math.pi / 4) / (2 * math.pi), 1.0)
        fill = (per < integ).astype(np.float32)
        gname = L.KIND_GLYPH.get(n["kind"])
        g = sample(N19.glyph(gname), a, b, S * 0.5) if gname else np.zeros_like(a)
        if st == "core":
            ang = np.arctan2(dy, dx)
            hexr = np.abs(np.hypot(dx, dy) * np.cos(np.mod(ang + math.pi / 6, math.pi / 3) - math.pi / 6))
            g = band(hexr, S * 0.25, S * 0.37)
        notch = ((dx + S * 0.82) + (dy + S * 0.82) < S * 0.32) * plate
        detail = 1 - city                           # pins, track and notch only resolve from the raid zoom in
        kg = 1.15 if st != "grey" else 0.5
        em += (frame * 1.3 + g * kg)[:, None] * col
        em += ((pins * 0.9 + track * (0.12 + fill) * 0.9 + notch * 0.7) * detail)[:, None] * col
        if city > 0:                                 # the map read: a filled glow disc + tier ring
            disc = band(cheb, -1, S * 0.86) * 0.22
            em += (disc * city)[:, None] * col
            tier = n.get("tier", 0)
            if tier:
                ring = band(cheb, S * 1.18, S * 1.3) * (np.mod(per * 3 * tier, 1.0) < 0.78)
                tc = GOLD if n["kind"] == "key" else col
                em += (ring * 1.2 * city)[:, None] * tc
        if exposed:
            ticks = band(cheb, S * 1.0, S * 1.08) * (np.mod((dx - dy) * 2.0 / S, 1.0) < 0.5)
            em += (ticks * 1.3)[:, None] * WHITE
        if flash == "hover":
            em += (band(cheb, S * 0.86, S * 1.0) * 1.3)[:, None] * WHITE
        if run:                                      # the run's current position: a white ring that breathes
            rr = band(cheb, S * (1.25 + 0.1 * math.sin(self.t * 6.28)), S * (1.35 + 0.1 * math.sin(self.t * 6.28)))
            em += (rr * 1.5)[:, None] * WHITE
        self.em[m] += em
        self.dk[m] *= dk

    def runnode(self, p_lots, col, kind_glyph, S=None, dashed=False):
        """A run's map node on the transit link (smaller socket, its glyph)."""
        x, y = L.W(p_lots)
        S = S or self.sock() * 0.62
        m = self._box(x, y, S * 1.5)
        if not m.any():
            return
        dx, dy = self.X[m] - x, self.Y[m] - y
        cheb = np.maximum(np.abs(dx), np.abs(dy))
        a = dx * self.rh[0] + dy * self.rh[1]
        b = dx * self.fh[0] + dy * self.fh[1]
        frame = band(cheb, S * 0.84, S * 0.98)
        if dashed:
            frame = frame * (np.mod(np.arctan2(dy, dx) / (2 * math.pi) * 16, 1.0) < 0.55)
        g = sample(N19.glyph(kind_glyph), a, b, S * 0.55)
        self.dk[m] *= 1 - 0.7 * (cheb < S)
        self.em[m] += (frame * 1.4 + g * 1.1)[:, None] * col

    def threat_lane(self, pts_lots, off=-1.9, t=0.0):
        pts = [np.array(L.W(p), float) for p in pts_lots]
        acc = 0.0
        for i in range(len(pts) - 1):
            pa, pb = pts[i], pts[i + 1]
            d = pb - pa
            Ls = float(np.hypot(*d))
            ux, uy = d / Ls
            lo, hi = np.minimum(pa, pb) - 4, np.maximum(pa, pb) + 4
            m = (self.X > lo[0]) & (self.X < hi[0]) & (self.Y > lo[1]) & (self.Y < hi[1]) & self.G
            if not m.any():
                acc += Ls
                continue
            dx, dy = self.X[m] - pa[0], self.Y[m] - pa[1]
            s = dx * ux + dy * uy
            a = -dx * uy + dy * ux - off
            inside = (s > -0.4) & (s < Ls + 0.4)
            tr = band(np.abs(a), -1, max(0.3, self.px(2.2)))
            sv = np.mod(acc + s - t * 8, 3.0) - 1.5
            chev = band(np.abs(sv - np.abs(a) * 0.8), -1, 0.18) * (np.abs(a) < 0.7)
            self.dk[m] *= 1 - 0.4 * band(np.abs(a), -1, 0.7) * inside
            self.em[m] += ((tr + chev * 1.2) * inside * 1.6)[:, None] * HARM
            acc += Ls

    def pool(self, x, y, r, k=1.0):
        """searchlight pool (Heat): returns a mask to brighten whatever it hits (all heights)."""
        return np.exp(-((np.hypot(self.X - x, self.Y - y) / r) ** 2) * 1.6) * (self.Z < 40) * k


# ------------------------------------------------------------------ the finish
MODE = dict(ink=(0.05, 0.04, 0.09), haze=(0.08, 0.06, 0.16), haze_k=0.34, bloom=0.75, spill=0.5, rain=(0.75, 0.82, 1.0),
            rain_a=0.11, grime=0.15, fog=(0.20, 0.17, 0.33), grade=(0.94, 0.92, 1.04))


def opacity(lod):
    """Round 37: building opacity by zoom. City 1.0 (the real city); raid and transit 0.32 (translucent, darkened:
    you can tell they are there, the network is the critical layer)."""
    return 0.32 + 0.68 * min(1.0, max(0.0, (lod - 1.05) / 0.5))


def finish(tag, decorate=None, pools=(), out_size=(1920, 1080), seed=1, t=0.0, rain=True, fog=0.22, sky=True):
    P = Passes(tag)
    net = Net36(P, t=t)
    if decorate:
        decorate(net)
    sc = P.w / 2880.0
    op = opacity(net.lod) if P.gbeauty is not None else 1.0
    # visible decal where the ground is seen; through buildings: a hatched ghost (x-ray)
    vis = P.vis
    hh_, ww_ = vis.shape
    yy, xx = np.mgrid[0:hh_, 0:ww_]
    hatch = (np.mod(xx + yy, max(3, int(9 * sc))) < max(2, int(5 * sc))).astype(np.float32)
    # the x-ray ghost grows with the zoom: hatched at raid / transit, solid at the city zoom (the map reads the network)
    cityk = min(1.0, max(0.0, (net.lod - 1.3) / 0.5))
    ghost = (hatch * 0.55) * (1 - cityk) + 1.0 * cityk
    tk = (1 - op) / 0.68                                  # translucent buildings: the network shows through at full strength
    ghost = ghost * (1 - tk) + 0.92 * tk
    em = net.em * vis[..., None] + net.em * ((1 - vis) * ghost)[..., None]
    dk = 1 - (1 - net.dk) * vis
    # management zooms: the street's own lane glow steps back so the network reads (the city zoom keeps the real look)
    lk = 1.0 - 0.72 * (1 - min(1.0, max(0.0, net.lod - 1.0)))
    ground = ((P.pos[..., 2] < 0.12) & (P.pos[..., 2] > -0.5)).astype(np.float32)
    lane = 1 - (1 - lk) * ground
    beauty = P.beauty * (dk * lane)[..., None]
    glow = P.glow * (dk * lane)[..., None] + em * 0.6
    bld = (1 - vis)[..., None]
    if op < 0.999:                                        # see-through: the ground pass under, the buildings dark on top
        gdk = (net.dk * lk)[..., None]                  # the hidden streets step back as much as the visible ones
        gb = P.gbeauty * gdk
        gg = P.gglow * gdk * 0.7 + net.em * 0.6
        dark = 0.4
        beauty = beauty * (1 - bld) + (gb * (1 - op) + P.beauty * op * dark) * bld
        glow = glow * (1 - bld) + (gg * (1 - op) + P.glow * op * 0.45) * bld
    e_id = F0.diff_edges(P.ids, 0.03)
    e_n = F0.diff_edges(P.nrm, 0.42)
    dep = P.dep
    dd = np.abs(dep - np.roll(dep, -1, 1)) + np.abs(dep - np.roll(dep, -1, 0))
    e_d = (dd > 1.2 * (P.cam["ortho"] / 300.0) / max(sc, 0.34)).astype(np.float32)
    ink = F0.warp(np.maximum(np.maximum(e_id, e_n), e_d), 7, amp=1.4 * max(sc, 0.5))
    thick = F0.maxf(ink, 3) if sc > 0.5 else ink
    ink_a = F0.blur(thick, 0.7) * (0.85 if P.cam["ortho"] < 400 else 0.6)
    ink_a = ink_a * (1 - (1 - op) * 0.55 * bld[..., 0])     # translucent buildings keep a thin outline
    h, w = P.h, P.w
    blot = F0.noise(h, w, max(8, int(90 * sc)), 31) * 0.6 + F0.noise(h, w, max(4, int(22 * sc)), 32) * 0.4
    g = 1 - MODE["grime"] * (blot - 0.5) * 1.4
    emis = np.clip(glow.max(axis=2) * 2, 0, 1)
    img = beauty * (g[..., None] * (1 - emis[..., None]) + emis[..., None])
    img = img + em * 0.72
    ink_a = ink_a * (1 - np.clip(emis * 1.6 - 0.4, 0, 1))
    img = img * (1 - ink_a[..., None]) + np.array(MODE["ink"], np.float32) * ink_a[..., None]
    for (x, y, r, k) in pools:                        # Heat B: searchlights on whatever they hit
        Lm = net.pool(x, y, r, k) * (0.85 + 0.15 * F0.noise(h, w, max(4, int(40 * sc)), int(x * 7 + y) % 9999))
        img = img * (1 + 1.4 * Lm[..., None]) + Lm[..., None] * np.array([0.30, 0.31, 0.36], np.float32)
        glow = glow + Lm[..., None] * np.array([0.22, 0.23, 0.28], np.float32)
    if sky:
        lay, lglow = sky_layer(P, net, t, k=1.0 if net.lod > 1.4 else 0.35)
        img = img + lay
        glow = glow + lglow
    b1 = F0.blur_down(glow, 8 * sc, 2)
    b2 = F0.blur_down(glow, 30 * sc, 4 if sc > 0.5 else 2)
    b3 = F0.blur_down(glow, 90 * sc, 8 if sc > 0.5 else 4)
    img = img * (1 + MODE["spill"] * (b2 * 0.8 + b3 * 1.0)) + MODE["bloom"] * (b1 * 0.5 + b2 * 0.4 + b3 * 0.12)
    if fog > 0:                                       # low street fog (round 26), lit by the neon under it
        drift = int(t * 60 * sc)                       # round 26 fog PATCHES, drifting
        fn = np.roll(F0.noise(h, w, max(16, int(160 * sc)), 70 + seed), drift, 1) * 0.6 + \
            np.roll(F0.noise(h, w, max(8, int(60 * sc)), 71 + seed), drift // 2, 1) * 0.4
        low = np.clip(1 - P.pos[..., 2] / 24.0, 0, 1) * 0.6 + 0.4 * (net.lod > 1.4)
        fa = np.clip((fn - 0.5) * 2.6, 0, 1) * low * fog
        img = img * (1 - fa[..., None]) + (np.array(MODE["fog"], np.float32) + b3 * 1.2) * fa[..., None]
    far = np.clip((dep - 0.05 * P.cam["ortho"]) / (1.2 * P.cam["ortho"]), 0, 1) ** 1.2
    img = img * (1 - far[..., None] * MODE["haze_k"]) + np.array(MODE["haze"], np.float32) * far[..., None] * MODE["haze_k"]
    if rain:
        rng = np.random.default_rng(41 + seed + int(t * 1000))
        rl = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(rl)
        for _ in range(int(2200 * sc * sc) + 200):
            x, y = rng.uniform(-100, w), rng.uniform(-100, h)
            Ln = rng.uniform(30, 80) * sc
            d.line([(x, y), (x + Ln * 0.2, y + Ln)], fill=int(rng.uniform(80, 255)), width=1)
        r = np.asarray(rl.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255 * MODE["rain_a"]
        img = img * (1 - r[..., None]) + np.array(MODE["rain"], np.float32) * r[..., None]
    img = img * np.array(MODE["grade"], np.float32)
    out = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))
    if out.size != tuple(out_size):
        out = out.resize(out_size, Image.LANCZOS)
    return np.asarray(out, np.float32) / 255.0, P.cam


# ------------------------------------------------------------------ round 26 v4 sky lanes + blinking tower lights
SKY_COLS = [(255, 70, 190), (80, 220, 255), (255, 196, 60), (170, 120, 255), (90, 255, 200), (255, 120, 60), (255, 255, 255)]


def _line(i0, j0, i1, j1, n=60):
    return [(i0 + (i1 - i0) * k / n, j0 + (j1 - j0) * k / n) for k in range(n + 1)]


def _circle(ci, cj, r, n=48):
    return [(ci + r * math.cos(2 * math.pi * k / n), cj + r * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]


# the round 26 network along the game's avenues (lot lines) + its loops; heights in world units (1 lot = 6 u)
SKY_ROADS = [("A_low", _line(-95, 4, 95, 4), 22.0), ("A_high", _line(-95, 4.6, 70, 4.6), 34.0), ("B", _line(6, -95, 6, 95), 52.0),
             ("C", _line(-90, -5, 16, -5), 28.0), ("F", _line(-10, -95, -10, 95), 44.0), ("D", _line(-60, 43, 95, 43), 24.0),
             ("E", _line(17, 20, 17, 95), 40.0), ("G", _line(-95, 30, 60, 30), 30.0), ("H", _line(28, -95, 28, 30), 36.0),
             ("clover", _circle(-10, 4, 2.4), 33.0), ("stack", _circle(17, 43, 5.5), 62.0), ("spiral", _circle(16, -2.6, 2.4), 20.0)]


def _at(seg, s):
    for a, b, Ls in seg:
        if s <= Ls:
            u = s / Ls if Ls else 0
            return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u), ((b[0] - a[0]) / (Ls or 1), (b[1] - a[1]) / (Ls or 1))
        s -= Ls
    a, b, Ls = seg[-1]
    return b, ((b[0] - a[0]) / (Ls or 1), (b[1] - a[1]) / (Ls or 1))


def sky_layer(P, net, t, k=1.0):
    """Fast multi-coloured flying cars on the sky lanes (round 26 v4: mixed colours, streaks, guide dots), depth-tested
    against the city, plus the blinking aircraft lights on the towers. Returns (additive layer, glow layer)."""
    cam = P.cam
    h, w = P.h, P.w
    ppu = w / cam["ortho"]
    lay = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(lay)
    r_, u_, f_ = L.basis(cam)
    tg = cam["target"]

    def proj(x, y, z):
        px, py = L.project(cam, x, y, z, w, h)
        dep = (x - tg[0]) * f_[0] + (y - tg[1]) * f_[1] + (z - tg[2]) * f_[2]
        return px, py, dep

    def visible(px, py, dep):
        ix, iy = int(px), int(py)
        if not (0 <= ix < w and 0 <= iy < h):
            return False
        return P.dep[iy, ix] > dep - 1.0

    rng = np.random.default_rng(2626)
    for name, pts, z in SKY_ROADS:
        wp = [L.W(p) for p in pts]
        seg = [(a, b, math.hypot(b[0] - a[0], b[1] - a[1])) for a, b in zip(wp, wp[1:])]
        total = sum(sg[2] for sg in seg)
        if total < 1:
            continue
        dstep = max(6.0, 20.0 / ppu)                  # faint lane-guide dots
        s0 = 0.0
        while s0 < total:
            p, dv = _at(seg, s0)
            for side in (-1, 1):
                q = (p[0] + dv[1] * side * 1.6, p[1] - dv[0] * side * 1.6)
                px, py, dp = proj(q[0], q[1], z)
                if visible(px, py, dp):
                    rr = max(0.6, ppu * 0.12)
                    d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=tuple(int(v * 0.22 * k) for v in (150, 170, 230)))
            s0 += dstep
        gap = 14.0
        n = int(total / gap)
        speed = 4 * gap                                   # whole car gaps per loop: the gif loops seamlessly
        for side in (-1, 1):
            lane_off = 0.9 * side if abs(side) == 1 else 2.2 * (side / 2)
            side = 1 if side > 0 else -1
            off = rng.uniform(0, gap)
            for c in range(n):
                skip = rng.random() < 0.22
                col = SKY_COLS[int(rng.integers(0, len(SKY_COLS)))]
                L_ = rng.uniform(8.0, 14.0)
                if skip:
                    continue
                s = (off + c * gap + side * t * speed) % total
                p, dv = _at(seg, s)
                q = (p[0] + dv[1] * lane_off, p[1] - dv[0] * lane_off)
                a = proj(q[0], q[1], z)
                b = proj(q[0] - dv[0] * side * L_, q[1] - dv[1] * side * L_, z)
                if not visible(*a):
                    continue
                wdt = max(1 if w < 1500 else 2, int(round(ppu * 0.7)))
                d.line([b[:2], a[:2]], fill=tuple(int(v * 0.8 * k) for v in col), width=wdt)
                rr = max(0.9 if w < 1500 else 1.6, ppu * 0.6)
                d.ellipse([a[0] - rr, a[1] - rr, a[0] + rr, a[1] + rr], fill=tuple(int(min(255, v * 1.2) * k) for v in col))
    for i, (x, y, z) in enumerate(P.sc.get("ants", [])):    # blinking aircraft lights on the towers
        ph = (i * 0.618) % 1.0
        if (t * 3.0 + ph) % 1.0 > 0.45:
            continue
        px, py, dp = proj(x, y, z)
        if not visible(px, py, dp):
            continue
        rr = max(1.4, ppu * 0.55)
        d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=(255, 50, 45))
    a = np.asarray(lay, np.float32) / 255.0
    return a * 1.15, a * 0.85


def cut(pts, f0, f1):
    """Sub-polyline of pts between arc fractions f0 .. f1."""
    seg = [(a, b, math.hypot(b[0] - a[0], b[1] - a[1])) for a, b in zip(pts, pts[1:])]
    total = sum(sg[2] for sg in seg)
    s0, s1 = f0 * total, f1 * total
    out = []
    acc = 0.0
    for a, b, Ls in seg:
        for sv in [acc] + [v for v in (s0, s1) if acc < v < acc + Ls]:
            if s0 - 1e-6 <= sv <= s1 + 1e-6:
                u = (sv - acc) / Ls if Ls else 0
                out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
        acc += Ls
    if s1 >= total - 1e-6:
        out.append(tuple(pts[-1]))
    dedup = []
    for p in out:
        if not dedup or math.hypot(p[0] - dedup[-1][0], p[1] - dedup[-1][1]) > 1e-6:
            dedup.append(p)
    return dedup


# ------------------------------------------------------------------ the shared network state (one campaign moment)

def threat_route():
    """A Halcyon raid route toward the Cell's CORE along the real streets (from the white Halcyon-side Site)."""
    import citydata as CD
    d = CD.load()
    import grid27
    grid27.patch(d)
    cells = L.street_graph(d)
    start = min((n for n in NET["nodes"] if n["state"] == "white" and n["corp"] == "halcyon"),
                key=lambda n: math.hypot(n["lot"][0] - NODES["core"]["lot"][0], n["lot"][1] - NODES["core"]["lot"][1]))
    p = L.bfs(tuple(start["cell"]), tuple(NODES["core"]["cell"]), cells)
    return start, L.simplify(p)


_TR = {}


def route():
    if "r" not in _TR:
        rp = os.path.join(L.DST, "threat36.json")
        if os.path.exists(rp):
            _TR["r"] = json.load(open(rp))
        else:
            s, p = threat_route()
            _TR["r"] = dict(start=s["id"], pts=p)
            json.dump(_TR["r"], open(rp, "w"))
    return _TR["r"]


def network(net, raid=False, transit=None, exposed=(), walked=None):
    """walked = fraction of the transit link already walked (drawn lime, the rest stays the border orange)."""
    lod = net.lod
    tl = NET["transit"]["link"]
    for l in NET["links"]:
        st = l["state"]
        if walked is not None and [l["a"], l["b"]] == tl:
            wp = cut(l["pts"], 0.0, walked)
            rp = cut(l["pts"], walked, 1.0)
            if len(wp) >= 2:
                net.link(wp, LIME, k=1.35, trim=(True, False), packets=True)
            if len(rp) >= 2:
                net.link(rp, LINK_COL["border"], style="dashed", k=1.15, trim=(False, True), packets=False)
            continue
        k = {"owned": 1.2, "border": 1.15, "white": 0.45, "grey": 0.4}[st]
        net.link(l["pts"], LINK_COL[st], style="dashed" if st in ("border", "white") else "solid", k=k, packets=st == "owned")
    if raid:
        r = route()
        net.threat_lane(r["pts"], t=net.t)
    for n in NET["nodes"]:
        net.node(n, exposed=n["id"] in exposed)
