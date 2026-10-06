"""Round 18: the grid network as DECALS ON THE STREET PLANE (numpy 'shaders' over the world-position pass).

Every function here is what the Godot ground-decal shader would compute per fragment: it gets the
fragment's world x, y (ground plane), and returns emission (added light) + a darkening factor.
Nothing rises above the asphalt: nodes are pads at intersections, links are markings along streets.

Three approaches, same inputs:
  A  paint  : painted-light road markings (double lane line + flow chevrons, roundel pads, stencil glyph)
  B  holo   : projected holo floor tiles (square tiles along links, hex-tile pads, glyph made of tiles)
  C  trace  : circuit-trace inlays (3-trace bus with vias in grooves, pads as chip sockets with pins)
"""
import math
import os
import sys

import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as LY  # noqa: E402

GLYPHS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "round17_slice_system", "glyphs"))
GLYPH_OF = {"home": None, "relay": "picto_all_targets", "firewall": "slice_firewall", "vault": "placeholder_vault",
            "proxy": "placeholder_spoof", "safehouse": "placeholder_key", "entry": "special_citation"}

C = lambda *v: np.array(v, np.float32)  # noqa: E731
CYAN, PINK, GREEN, VIOLET, AMBER = C(0.36, 0.88, 1.0), C(1.0, 0.24, 0.66), C(0.48, 0.88, 0.48), C(0.78, 0.35, 1.0), C(1.0, 0.69, 0.0)
HARM, HALCYON = C(1.0, 0.27, 0.2), C(0.55, 0.48, 1.0)
STATUS_COL = {"home": PINK, "holds": GREEN, "disabled": AMBER, "seized": HARM}
PAD_R = 12.5          # pad radius (m); CORE x 1.2
AA = 0.14             # antialias width (m) ~ one render pixel

_glyph_cache = {}


def glyph(name):
    if name not in _glyph_cache:
        im = Image.open(os.path.join(GLYPHS, name + ".png")).convert("RGBA")
        _glyph_cache[name] = np.asarray(im, np.float32)[..., 3] / 255.0
    return _glyph_cache[name]


def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def band(x, lo, hi, aa=AA):
    """1 inside [lo, hi] with soft edges."""
    return sstep(lo - aa, lo + aa, x) * (1 - sstep(hi - aa, hi + aa, x))


def hash2(a, b, seed=0):
    h = np.sin(a * 12.9898 + b * 78.233 + seed * 37.719) * 43758.5453
    return h - np.floor(h)


def vnoise(x, y, seed=0):
    xi, yi = np.floor(x), np.floor(y)
    xf, yf = x - xi, y - yi
    u, v = xf * xf * (3 - 2 * xf), yf * yf * (3 - 2 * yf)
    a = hash2(xi, yi, seed)
    b = hash2(xi + 1, yi, seed)
    c = hash2(xi, yi + 1, seed)
    d = hash2(xi + 1, yi + 1, seed)
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v


def screen_axes():
    """Ground directions that read as screen-right and screen-up (for upright glyphs)."""
    r, u, f = LY.cam_basis()
    fh = np.array([f[0], f[1]]) / math.hypot(f[0], f[1])
    rh = np.array([r[0], r[1]]) / math.hypot(r[0], r[1])
    return rh, fh


def glyph_sample(g, a, b, R):
    """Sample glyph alpha at ground offsets (a right, b up) inside a box of half-size R."""
    n = g.shape[0]
    u = ((a / R) * 0.5 + 0.5) * (n - 1)
    v = (0.5 - (b / R) * 0.5) * (n - 1)
    ok = (u >= 0) & (u <= n - 1) & (v >= 0) & (v <= n - 1)
    ui = np.clip(u, 0, n - 1).astype(np.int32)
    vi = np.clip(v, 0, n - 1).astype(np.int32)
    return np.where(ok, g[vi, ui], 0.0)


# ------------------------------------------------------------------ network geometry
def link_segments(state):
    """Axis-aligned link segments oriented toward CORE (flow direction for chevrons / packets)."""
    core = np.array(LY.pt("core"), np.float64)
    segs = []
    for a, b in LY.LINKS:
        pa, pb = np.array(LY.pt(a), float), np.array(LY.pt(b), float)
        if np.linalg.norm(pa - core) < np.linalg.norm(pb - core):
            pa, pb = pb, pa
            a, b = b, a
        segs.append((pa, pb, a, b))
    return segs


def route_segments():
    linkset = set()
    for a, b in LY.LINKS:
        pa, pb = LY.pt(a), LY.pt(b)
        linkset.add((pa, pb))
        linkset.add((pb, pa))
    out = []
    for rid in LY.ROUTES:
        ps = LY.route_points(rid)
        for i in range(len(ps) - 1):
            shared = (ps[i], ps[i + 1]) in linkset
            out.append((np.array(ps[i], float), np.array(ps[i + 1], float), shared, rid))
    return out


def seg_coords(X, Y, pa, pb):
    """For an axis-aligned segment: along s (0 at pa), across (signed, left of travel = +), length."""
    d = pb - pa
    L = float(np.hypot(*d))
    ux, uy = d / L
    dx, dy = X - pa[0], Y - pa[1]
    s = dx * ux + dy * uy
    across = -dx * uy + dy * ux
    return s, across, L


# ------------------------------------------------------------------ the shader
class Net:
    def __init__(self, X, Y, G, approach, statuses, mode="night", wave=False, heat=1, threat_lanes=True,
                 integrity=None):
        self.X, self.Y, self.G = X, Y, G
        self.ap = approach
        self.st = statuses
        self.wave = wave
        self.heat = heat
        self.lanes = threat_lanes
        self.integ = integrity or {}
        self.em = np.zeros(X.shape + (3,), np.float32)      # emission (added light)
        self.dk = np.ones(X.shape, np.float32)              # multiply (grooves, plates)
        self.rh, self.fh = screen_axes()
        self.k = 1.0 if mode == "night" else 0.75

    def add(self, mask, col, k=1.0):
        self.em += (mask * k * self.k)[..., None] * col

    def darken(self, mask, amt):
        self.dk *= 1 - mask * amt

    # -------------------------------------------------------------- links
    def links(self):
        pads = [(LY.pt(k), PAD_R * (1.2 if k == "core" else 1.0)) for k in LY.NODES]
        for pa, pb, a, b in link_segments(self.st):
            s, ac, L = seg_coords(self.X, self.Y, pa, pb)
            inside = (s > PAD_R * 0.8) & (s < L - PAD_R * 0.8) & (np.abs(ac) < 8) & self.G
            if not inside.any():
                continue
            ss, aa = s[inside], ac[inside]
            dead = self.st.get(a) in ("seized",) or self.st.get(b) in ("seized",)
            fl = 0.55 if dead else 1.0
            em, dk = self._link_pattern(ss, aa, L, dead)
            self.em[inside] += em * fl * self.k
            self.dk[inside] *= dk

    def _link_pattern(self, s, a, L, dead):
        ap = self.ap
        n = s.shape[0]
        em = np.zeros((n, 3), np.float32)
        dk = np.ones(n, np.float32)
        col = CYAN
        if ap == "A":
            wear = 0.7 + 0.3 * vnoise(s * 0.9, a * 0.9, 3)
            chip = (vnoise(s * 0.35, a * 0.35, 4) > 0.22).astype(np.float32)
            lines = band(np.abs(a), 2.3, 3.0)
            v = np.mod(L - s, 7.0) - 1.15 * np.abs(a)
            chev = band(v, 0.0, 1.25) * (np.abs(a) < 1.75)
            m = (lines * 1.0 + chev * 0.85) * wear * chip
            em += m[:, None] * col * 1.25
            dk *= 1 - 0.1 * m
            if self.wave:  # data packet: a bright run of chevrons travelling home
                pk = band(np.mod(L - s - 3, 28.0), 0, 7.0)
                em += (chev * pk * 1.2)[:, None] * C(0.9, 1.0, 1.0)
        elif ap == "B":
            tile = 1.9
            corr = np.abs(a) < 3.8
            tu = np.floor(s / tile)
            tv = np.floor((a + 3.8) / tile)
            fu = s / tile - tu
            fv = (a + 3.8) / tile - tv
            body = band(fu, 0.08, 0.92, 0.04) * band(fv, 0.08, 0.92, 0.04) * corr
            edge = body * (1 - band(fu, 0.2, 0.8, 0.04) * band(fv, 0.2, 0.8, 0.04))
            h = hash2(tu, tv, 7)
            on = (h > 0.07).astype(np.float32)
            lvl = 0.22 + 0.35 * np.exp(-(a / 2.4) ** 2) + 0.18 * (h > 0.85)
            scan = 0.8 + 0.2 * np.sin(a * 2 * math.pi / 0.62)
            pk = band(np.mod(L - s, 22.0), 0, 3.8) if True else 0
            m = (body * lvl * scan + edge * 0.55 + body * pk * 0.6) * on
            em += m[:, None] * col * 1.35
            # thin rails either side (the projector's frame)
            em += band(np.abs(a), 4.0, 4.3)[:, None] * col * 0.6
        else:  # C traces
            m = np.zeros(n, np.float32)
            groove = np.zeros(n, np.float32)
            for i, off in enumerate((-2.6, 0.0, 2.6)):
                d = np.abs(a - off)
                groove = np.maximum(groove, band(d, -1, 0.75))
                m = np.maximum(m, band(d, -1, 0.26))
                # vias: every 10 m, staggered per trace
                sv = np.mod(s + i * 3.3, 10.0) - 5.0
                rv = np.hypot(sv, a - off)
                groove = np.maximum(groove, band(rv, -1, 1.35))
                m = np.maximum(m, band(rv, 0.55, 1.0))
            pulse = band(np.mod(L - s, 30.0), 0, 2.5) if True else 0
            dk *= 1 - 0.55 * groove
            em += (m * (0.95 + 1.2 * pulse))[:, None] * col * 1.2
            em += (groove * 0.06)[:, None] * col
        return em, dk

    # -------------------------------------------------------------- threat lanes (routes on the ground)
    def threat_lanes(self):
        if not self.lanes:
            return
        for pa, pb, shared, rid in route_segments():
            s, ac, L = seg_coords(self.X, self.Y, pa, pb)
            off = -5.6 if shared else 0.0
            a = ac - off
            inside = (s > PAD_R * 0.9) & (s < L - PAD_R * 0.9) & (np.abs(a) < 2.5) & self.G
            if not inside.any():
                continue
            ss, aa = s[inside], a[inside]
            if self.ap == "A":
                dash = band(np.mod(ss, 7.0), 0, 4.0) * band(np.abs(aa), -1, 0.5)
                v = np.mod(ss, 21.0) - 1.3 * np.abs(aa)
                head = band(v, 6.0, 7.2) * (np.abs(aa) < 2.2)
                m = (dash + head) * (0.7 + 0.3 * vnoise(ss * 0.8, aa, 9))
                e = m[:, None] * HARM * 1.3
            elif self.ap == "B":
                tu = np.floor(ss / 1.9)
                fu = ss / 1.9 - tu
                body = band(fu, 0.1, 0.9, 0.04) * band(np.abs(aa), -1, 0.8)
                on = (hash2(tu, 1.0, 11) > 0.1) * (np.mod(tu, 4) != 3)
                m = body * on
                e = m[:, None] * HARM * 1.25
            else:
                tr = band(np.abs(aa), -1, 0.3)
                sv = np.mod(ss, 12.0) - 6.0
                via = band(np.hypot(sv, aa), 0.5, 0.95)
                gr = band(np.abs(aa), -1, 0.8) + band(np.hypot(sv, aa), -1, 1.3)
                self.dk[inside] *= 1 - 0.5 * np.clip(gr, 0, 1)
                m = np.maximum(tr, via)
                e = m[:, None] * HARM * 1.2
            self.em[inside] += e * self.k

    # -------------------------------------------------------------- pads
    def pads(self):
        for key, n in LY.NODES.items():
            st = self.st.get(key, "holds")
            R = PAD_R * (1.22 if key == "core" else 1.0)
            self._pad(n[0], n[1], R, STATUS_COL[st], GLYPH_OF[n[2]], st, key)
        for key, e in LY.ENTRIES.items():
            self._pad(e[0], e[1], PAD_R * 0.8, HALCYON, GLYPH_OF["entry"], "entry", key)

    def _pad(self, x, y, R, col, gname, st, key):
        X, Y = self.X, self.Y
        box = (np.abs(X - x) < R * 1.25) & (np.abs(Y - y) < R * 1.25) & self.G
        if not box.any():
            return
        dx, dy = X[box] - x, Y[box] - y
        r = np.hypot(dx, dy)
        a = dx * self.rh[0] + dy * self.rh[1]   # screen-right on the ground
        b = dx * self.fh[0] + dy * self.fh[1]   # screen-up on the ground
        ang = np.arctan2(dy, dx)
        g = glyph(gname) if gname else None
        em = np.zeros((r.shape[0], 3), np.float32)
        dk = np.ones(r.shape[0], np.float32)
        broken = np.ones_like(r)
        if st == "disabled":   # flickering, chunks missing, cracks
            broken = (vnoise(dx * 0.5, dy * 0.5, 21) > 0.36).astype(np.float32)
            crack = band(np.abs(np.sin(ang * 3 + r * 0.25) * r - 2.0), -1, 0.25) * (r < R)
            dk *= 1 - 0.5 * crack
        ap = self.ap
        if ap == "A":
            wear = 0.72 + 0.28 * vnoise(dx * 1.1, dy * 1.1, 5)
            ring = band(r, R * 0.86, R * 0.98)
            ticks = band(r, R * 0.70, R * 0.76) * (np.mod(ang / (2 * math.pi) * 24, 1) < 0.55)
            fill = (r < R * 0.66) * 0.13
            m = ring * 1.15 + ticks * 0.9 + fill
            if g is not None:
                m = m + glyph_sample(g, a, b, R * 0.58) * 1.1
            elif key == "core":
                hexr = np.abs(r * np.cos(np.mod(ang + math.pi / 6, math.pi / 3) - math.pi / 6))
                m = m + band(hexr, R * 0.38, R * 0.52) * 1.2
            if st == "seized":   # painted hazard hatch over the pad
                hatch = (np.mod((dx + dy) * 0.45, 1.0) < 0.35) * (r < R * 0.98)
                m = np.maximum(m, hatch * 0.55)
            if st == "entry":
                hatch = (np.mod((dx - dy) * 0.4, 1.0) < 0.4) * (r < R * 0.98)
                m = np.maximum(m, hatch * 0.45)
            m *= wear * broken
            em += m[:, None] * col * 1.3
            dk *= 1 - 0.18 * (r < R)
        elif ap == "B":
            # hex tile field
            s3 = math.sqrt(3)
            cell = 1.55
            q = (dx * s3 / 3 - dy / 3) / cell
            rr = (dy * 2 / 3) / cell
            # cube round
            xq, zq = q, rr
            yq = -xq - zq
            rx, ry, rz = np.round(xq), np.round(yq), np.round(zq)
            ddx, ddy, ddz = np.abs(rx - xq), np.abs(ry - yq), np.abs(rz - zq)
            fixx = (ddx > ddy) & (ddx > ddz)
            fixz = ~fixx & (ddz >= ddy)
            rx = np.where(fixx, -ry - rz, rx)
            rz = np.where(fixz, -rx - ry, rz)
            cxw = cell * s3 * (rx + rz / 2)
            cyw = cell * 1.5 * rz
            loc = np.hypot(dx - cxw, dy - cyw)
            tilebody = 1 - sstep(cell * 0.62, cell * 0.8, loc)
            tedge = tilebody * sstep(cell * 0.42, cell * 0.62, loc)
            rc = np.hypot(cxw, cyw)
            inpad = rc < R * 0.95
            ca = cxw * self.rh[0] + cyw * self.rh[1]
            cb = cxw * self.fh[0] + cyw * self.fh[1]
            lvl = 0.18 + 0.75 * (rc > R * 0.78)
            if g is not None:
                gl = glyph_sample(g, ca, cb, R * 0.62)
                lvl = lvl + 0.95 * (gl > 0.5)
            elif key == "core":
                cang = np.arctan2(cyw, cxw)
                hexr = np.abs(rc * np.cos(np.mod(cang + math.pi / 6, math.pi / 3) - math.pi / 6))
                lvl = lvl + 0.9 * ((hexr > R * 0.36) & (hexr < R * 0.55))
            if st == "seized":
                lvl = lvl * (0.6 + 0.6 * (np.mod((cxw + cyw) * 0.3, 1) < 0.4))
            h = hash2(rx, rz, 13)
            on = (h > 0.05) * inpad
            m = (tilebody * lvl + tedge * 0.5) * on * (0.85 + 0.3 * h)
            m = m + band(r, R * 1.0, R * 1.06) * 0.9
            m *= broken
            em += m[:, None] * col * 1.25
        else:  # C chip socket
            ax, ay = np.abs(dx), np.abs(dy)
            cheb = np.maximum(ax, ay)
            S = R * 0.86
            plate = cheb < S
            dk *= 1 - 0.55 * plate
            frame = band(cheb, S * 0.9, S * 0.97)
            inner = band(cheb, S * 0.55, S * 0.6)
            pins = np.zeros_like(r)
            for side_val, along in ((ax, ay), (ay, ax)):
                pin_on = band(side_val, S * 0.97, S * 1.22)
                k = np.mod(along + 1.3, 2.6) - 1.3
                pins = np.maximum(pins, pin_on * band(np.abs(k), -1, 0.45) * (along < S * 0.85))
            notch = ((dx + S * 0.85) + (dy + S * 0.85) < S * 0.35) * plate
            m = frame * 1.2 + inner * 0.7 + pins * 1.0 + notch * 0.9
            if g is not None:
                m = m + glyph_sample(g, a, b, S * 0.55) * 1.05
            elif key == "core":
                hexr = np.abs(r * np.cos(np.mod(ang + math.pi / 6, math.pi / 3) - math.pi / 6))
                m = m + band(hexr, S * 0.28, S * 0.4) * 1.2
            if st == "seized":
                m = np.maximum(m, (np.mod((dx + dy) * 0.45, 1.0) < 0.3) * (cheb < S * 0.55) * 0.5)
            if st == "entry":
                m = np.maximum(m, (np.mod((dx - dy) * 0.45, 1.0) < 0.35) * (cheb < S * 0.55) * 0.45)
            m *= broken
            em += m[:, None] * col * 1.25
        self.em[box] += em * self.k
        self.dk[box] *= dk

    def threat_marks(self, pts):
        """A hostile ring painted under each moving threat (same street plane as the grid)."""
        for (x, y) in pts:
            box = (np.abs(self.X - x) < 14) & (np.abs(self.Y - y) < 14) & self.G
            if not box.any():
                continue
            dx, dy = self.X[box] - x, self.Y[box] - y
            r = np.hypot(dx, dy)
            ang = np.arctan2(dy, dx)
            ring = band(r, 11.0, 12.4) * (np.mod(ang / (2 * math.pi) * 14, 1) < 0.62)
            inner = band(r, -1, 10.6) * 0.14
            self.em[box] += ((ring * 1.3 + inner)[:, None] * HARM) * self.k

    def build(self, threats=None):
        self.links()
        self.threat_lanes()
        self.pads()
        if threats:
            self.threat_marks(threats)
        return self.em, self.dk
