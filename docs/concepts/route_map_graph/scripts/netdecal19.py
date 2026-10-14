"""Round 19: the LOCKED street-plane grid (round 18 option C, circuit inlay), with every node state
drawn ON the socket so no text tags are needed. numpy prototype of the Godot ground-decal shader.

Socket anatomy (a square chip socket filling the intersection, sidewalk corners included):
  plate      dark inset plate (multiply)                       - always
  frame      outer frame: colour + pattern = STATUS            - solid (holds) / dashed (disabled) / violet hatch (seized)
  track      inner square track, filled clockwise from the     - INTEGRITY (the ring around the socket)
             pin-1 notch = integrity / max
  pins       7 pins a side, lit in the status colour           - power: dark when disabled / seized
  glyph      node type glyph (round 17 set)                    - TYPE (corp mark once seized)
  forecast   dashed outer ring in the outcome colour           - setup projection (dashed = predicted)
  cracks     dark fracture lines, more as integrity drops      - damage
Links: a 3-trace bus with vias, in the link colour (lime cell_turf by default, cyan for comparison).
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as LY  # noqa: E402

GLYPHS = os.path.abspath(os.path.join(HERE, "..", "..", "round17_slice_system", "glyphs"))
FONT_MONO = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\assets\fonts\ShareTechMono-Regular.ttf"
GLYPH_OF = {"home": None, "relay": "picto_all_targets", "firewall": "slice_firewall", "vault": "placeholder_vault",
            "proxy": "placeholder_spoof", "safehouse": "placeholder_key", "entry": "special_citation"}
C = lambda *v: np.array(v, np.float32)  # noqa: E731
PINK, GREEN, AMBER, HARM, HALCYON = C(1.0, 0.24, 0.66), C(0.48, 0.88, 0.48), C(1.0, 0.69, 0.0), C(1.0, 0.27, 0.2), C(0.55, 0.48, 1.0)
ICE, WHITE, DARKPIN = C(0.7, 0.92, 1.0), C(1.0, 1.0, 1.0), C(0.10, 0.10, 0.13)
LINK = {"lime": C(0.83, 1.0, 0.0), "cyan": C(0.36, 0.88, 1.0)}
STATUS_COL = {"holds": GREEN, "damaged": GREEN, "disabled": AMBER, "seized": HALCYON, "home": PINK, "burnt": C(0.5, 0.2, 0.1),
              "empty": C(0.5, 0.5, 0.55)}
PAD_S = 10.4          # socket half size (m)
AA = 0.14

_glyph_cache = {}


def glyph(name):
    if name not in _glyph_cache:
        im = Image.open(os.path.join(GLYPHS, name + ".png")).convert("RGBA")
        _glyph_cache[name] = np.asarray(im, np.float32)[..., 3] / 255.0
    return _glyph_cache[name]


def text_mask(text, size=128):
    f = ImageFont.truetype(FONT_MONO, size)
    w = int(f.getlength(text)) + 8
    im = Image.new("L", (w, size + 16), 0)
    ImageDraw.Draw(im).text((4, 2), text, font=f, fill=255)
    return np.asarray(im, np.float32) / 255.0


def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def band(x, lo, hi, aa=AA):
    return sstep(lo - aa, lo + aa, x) * (1 - sstep(hi - aa, hi + aa, x))


def hash2(a, b, seed=0):
    h = np.sin(a * 12.9898 + b * 78.233 + seed * 37.719) * 43758.5453
    return h - np.floor(h)


def vnoise(x, y, seed=0):
    xi, yi = np.floor(x), np.floor(y)
    xf, yf = x - xi, y - yi
    u, v = xf * xf * (3 - 2 * xf), yf * yf * (3 - 2 * yf)
    a, b = hash2(xi, yi, seed), hash2(xi + 1, yi, seed)
    c, d = hash2(xi, yi + 1, seed), hash2(xi + 1, yi + 1, seed)
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v


def screen_axes():
    r, u, f = LY.cam_basis()
    fh = np.array([f[0], f[1]]) / math.hypot(f[0], f[1])
    rh = np.array([r[0], r[1]]) / math.hypot(r[0], r[1])
    return rh, fh


def sample(g, a, b, hw, hh=None):
    """Sample a mask at ground offsets (a right, b up on screen) inside a box of half sizes hw x hh."""
    hh = hw if hh is None else hh
    H, W = g.shape
    u = ((a / hw) * 0.5 + 0.5) * (W - 1)
    v = (0.5 - (b / hh) * 0.5) * (H - 1)
    ok = (u >= 0) & (u <= W - 1) & (v >= 0) & (v <= H - 1)
    return np.where(ok, g[np.clip(v, 0, H - 1).astype(np.int32), np.clip(u, 0, W - 1).astype(np.int32)], 0.0)


def seg_coords(X, Y, pa, pb):
    d = np.asarray(pb, float) - np.asarray(pa, float)
    L = float(np.hypot(*d))
    ux, uy = d / L
    dx, dy = X - pa[0], Y - pa[1]
    return dx * ux + dy * uy, -dx * uy + dy * ux, L


class Net:
    def __init__(self, pos, mode="night", link="lime"):
        self.X, self.Y, self.Z = pos[..., 0], pos[..., 1], pos[..., 2]
        self.G = (self.Z < 0.1) & (self.Z > -0.5)            # street surface
        self.GP = (self.Z < 0.42) & (self.Z > -0.5)          # street + sidewalks (sockets, risers)
        self.em = np.zeros(self.X.shape + (3,), np.float32)
        self.dk = np.ones(self.X.shape, np.float32)
        self.rh, self.fh = screen_axes()
        self.k = 1.0 if mode == "night" else 0.8
        self.lc = LINK[link]

    def _box(self, x, y, r, mask=None):
        m = mask if mask is not None else self.GP
        return (np.abs(self.X - x) < r) & (np.abs(self.Y - y) < r) & m

    # -------------------------------------------------------------- links (3-trace bus)
    def link(self, a, b, state="ok", t=0.0, packets=False):
        """state: ok / dim (to a disabled node) / dead (to a seized node) / frozen (Lockdown) / hot (flash)."""
        pa, pb = np.array(LY.pt(a), float), np.array(LY.pt(b), float)
        core = np.array(LY.pt("core"), float)
        if np.linalg.norm(pa - core) < np.linalg.norm(pb - core):
            pa, pb = pb, pa
        s, ac, L = seg_coords(self.X, self.Y, pa, pb)
        m = (s > PAD_S * 0.95) & (s < L - PAD_S * 0.95) & (np.abs(ac) < 4.5) & self.G
        if not m.any():
            return
        ss, aa = s[m], ac[m]
        tr = np.zeros(ss.shape, np.float32)
        gr = np.zeros(ss.shape, np.float32)
        for i, off in enumerate((-2.6, 0.0, 2.6)):
            d = np.abs(aa - off)
            gr = np.maximum(gr, band(d, -1, 0.75))
            tr = np.maximum(tr, band(d, -1, 0.26))
            sv = np.mod(ss + i * 3.3, 10.0) - 5.0
            rv = np.hypot(sv, aa - off)
            gr = np.maximum(gr, band(rv, -1, 1.35))
            tr = np.maximum(tr, band(rv, 0.55, 1.0))
        col, k = self.lc, 1.2
        if state == "dim":
            k = 0.3 * (0.6 + 0.4 * (vnoise(ss * 0.3, 0, 5) > 0.5))
        elif state == "dead":
            k = 0.0
        elif state == "frozen":
            col = ICE
            frost = vnoise(ss * 0.8, aa * 0.8, 11)
            tr = tr * (0.4 + 0.8 * frost) + band(np.abs(np.mod(ss, 6.0) - 3.0 + aa * 0.6), -1, 0.15) * (np.abs(aa) < 3.6) * 0.8
            k = 1.1
        elif state == "hot":
            k = 2.0
        pulse = 0.0
        if packets and state in ("ok", "hot"):
            pulse = band(np.mod(L - ss - t * 30.0, 30.0), 0, 2.5)
        self.dk[m] *= 1 - 0.55 * np.clip(gr, 0, 1)
        self.em[m] += ((tr * k * (1 + 1.3 * pulse)) + gr * 0.04 * k)[:, None] * col * self.k

    # -------------------------------------------------------------- threat lanes
    def lane(self, pts, style="solid", col=HARM, off=0.0, t=0.0, trim=(True, True)):
        """Threat route on the street: solid red trace (known route), dashed (redirect preview), ghost (old route)."""
        for i in range(len(pts) - 1):
            pa, pb = np.array(pts[i], float), np.array(pts[i + 1], float)
            s, ac, L = seg_coords(self.X, self.Y, pa, pb)
            a = ac - off
            t0 = PAD_S * 0.95 if (i == 0 and trim[0]) else -off if off else -0.5
            t1 = L - PAD_S * 0.95 if (i == len(pts) - 2 and trim[1]) else L + (off if off else 0.5)
            m = (s > t0) & (s < t1) & (np.abs(a) < 2.5) & self.G
            if not m.any():
                continue
            ss, aa = s[m], a[m]
            tr = band(np.abs(aa), -1, 0.32)
            sv = np.mod(ss, 12.0) - 6.0
            via = band(np.hypot(sv, aa), 0.5, 0.95)
            gr = np.clip(band(np.abs(aa), -1, 0.85) + band(np.hypot(sv, aa), -1, 1.3), 0, 1)
            k = 1.25
            if style == "dashed":
                tr = tr * band(np.mod(ss - t * 12, 5.0), 0, 2.8)
                via = via * 0
                gr = gr * 0.4
                k = 1.6
            elif style == "ghost":
                k = 0.35
                gr = gr * 0.5
            self.dk[m] *= 1 - 0.5 * gr
            self.em[m] += (np.maximum(tr, via) * k)[:, None] * col * self.k

    # -------------------------------------------------------------- socket
    def pad(self, key, state="holds", integ=1.0, forecast=None, exposed=False, flash=None, t=0.0, glyph_name=None,
            hud=None):
        n = LY.NODES[key]
        x, y = n[0], n[1]
        S = PAD_S * (1.15 if key == "core" else 1.0)
        m = self._box(x, y, S * (2.6 if hud else 1.15))
        if not m.any():
            return
        dx, dy = self.X[m] - x, self.Y[m] - y
        ax, ay = np.abs(dx), np.abs(dy)
        cheb = np.maximum(ax, ay)
        a = dx * self.rh[0] + dy * self.rh[1]
        b = dx * self.fh[0] + dy * self.fh[1]
        col = STATUS_COL[state]
        em = np.zeros((dx.shape[0], 3), np.float32)
        dk = np.ones(dx.shape[0], np.float32)
        plate = cheb < S
        dk *= 1 - 0.6 * plate
        # perimeter coordinate (0..1 clockwise from the pin-1 notch corner at -S, -S)
        per = np.where(dy <= -np.abs(dx) + 0, 0, 0).astype(np.float32)
        ang = np.arctan2(dy, dx)
        per = np.mod((ang + 3 * math.pi / 4) / (2 * math.pi), 1.0)
        # ---- frame
        frame = band(cheb, S * 0.9, S * 0.97)
        if state == "disabled":
            frame = frame * (np.mod(per * 32, 1.0) < 0.5) * 0.7
        k_frame = 1.25
        # ---- pins (power)
        pins = np.zeros_like(cheb)
        for side_val, along in ((ax, ay), (ay, ax)):
            kk = np.mod(along + 1.3, 2.6) - 1.3
            pins = np.maximum(pins, band(side_val, S * 0.97, S * 1.13) * band(np.abs(kk), -1, 0.42) * (along < S * 0.85))
        pin_col = col if state not in ("disabled", "seized", "burnt") else DARKPIN
        # ---- integrity track (inner square ring), filled clockwise from the notch
        track = band(cheb, S * 0.70, S * 0.78)
        fill = (per < integ).astype(np.float32)
        tcol = col
        if state in ("holds", "damaged", "home") and integ < 0.34:
            tcol = HARM
        elif state in ("holds", "damaged") and integ < 0.67:
            tcol = AMBER
        # ---- inner square + glyph
        inner = band(cheb, S * 0.55, S * 0.6)
        gname = glyph_name or (GLYPH_OF["entry"] if state == "seized" else GLYPH_OF[n[2]])
        g = sample(glyph(gname), a, b, S * 0.52) if gname else np.zeros_like(a)
        if key == "core" and not glyph_name:
            hexr = np.abs(np.hypot(dx, dy) * np.cos(np.mod(ang + math.pi / 6, math.pi / 3) - math.pi / 6))
            g = band(hexr, S * 0.26, S * 0.38)
        gk = 1.1
        notch = ((dx + S * 0.85) + (dy + S * 0.85) < S * 0.35) * plate
        if state == "disabled":
            flick = (vnoise(dx * 0.5, dy * 0.5, 21) > 0.4).astype(np.float32)
            g, gk = g * flick, 0.45
            inner = inner * flick * 0.5
        if state == "seized":
            hatch = (np.mod((dx + dy) * 0.45, 1.0) < 0.32) * (cheb < S * 0.9)
            em += (hatch * 0.35)[:, None] * col
            inner = inner * 0.6
        if state == "burnt":
            dk *= 1 - 0.35 * plate
            ember = (hash2(np.floor(dx * 1.5), np.floor(dy * 1.5), 9) > 0.985) * plate
            em += (ember * 1.5)[:, None] * C(1.0, 0.45, 0.1)
            frame, g, inner, notch = frame * 0.15, g * 0, inner * 0, notch * 0
        # damage cracks grow as integrity drops
        if state in ("damaged", "disabled", "burnt") or integ < 0.99:
            amount = 1.0 - integ if state != "burnt" else 1.0
            cr = np.zeros_like(cheb)
            for i in range(1 + int(amount * 6)):
                th = 0.6 + i * 1.7
                d = np.abs(np.sin(np.arctan2(dy, dx) * 3 + th) * np.hypot(dx, dy) * 0.35 - 0.6 * np.sin(np.hypot(dx, dy) * 0.4 + i))
                cr = np.maximum(cr, band(d, -1, 0.12) * (np.hypot(dx, dy) < S * (0.4 + 0.6 * amount)))
            dk *= 1 - 0.65 * cr * plate
        em += (frame * k_frame)[:, None] * (col if state != "seized" else HALCYON)
        em += (pins * 0.9)[:, None] * pin_col
        em += (track * (0.12 + 1.0 * fill))[:, None] * tcol * (0.0 if state in ("disabled", "seized", "burnt") else 1.0)
        em += (inner * 0.7 + g * gk + notch * 0.8)[:, None] * (col if state != "seized" else HALCYON)
        # ---- setup forecast: dashed outer ring in the outcome colour (glyph language: dashed = predicted)
        if forecast is not None:
            fcol = STATUS_COL[forecast] if forecast != "seized" else HARM
            ring = band(cheb, S * 1.04, S * 1.12) * (np.mod(per * 24 - t * 2, 1.0) < 0.55)
            em += (ring * 1.4)[:, None] * fcol
        # ---- exposed by a spotlight (PROPOSAL, needs a GDD decision): white hazard ticks round the frame
        if exposed:
            ticks = band(cheb, S * 1.0, S * 1.06) * (np.mod((dx - dy) * 0.5, 1.0) < 0.5)
            em += (ticks * 1.2)[:, None] * WHITE
        # ---- drag feedback
        if flash == "hover":
            em += (band(cheb, S * 0.88, S * 1.0) * 1.2)[:, None] * WHITE
        elif flash == "invalid":
            xx = band(np.abs(np.abs(dx) - np.abs(dy)), -1, 0.7) * (cheb < S * 0.8)
            em += ((band(cheb, S * 0.88, S * 1.0) + xx) * 1.4)[:, None] * HARM
        elif flash == "place":
            em += (band(cheb, S * 1.0, S * 1.35) * 0.9 * (1 - sstep(S, S * 1.35, cheb)))[:, None] * self.lc
        # ---- live option L1: integrity numbers projected flat on the street beside the socket
        if hud is not None:
            tm = text_mask(hud)
            hw = S * 1.0
            hh = hw * tm.shape[0] / tm.shape[1]
            # in front of the socket (screen-down side), reading upright on screen
            bb = b + S * 1.55
            em += (sample(tm, a, bb, hw, hh) * 1.3)[:, None] * tcol
        self.em[m] += em * self.k
        self.dk[m] *= dk

    def entry(self, key, active=True, incoming=False, t=0.0):
        """Corporate entry Site socket (violet), its red spawn pulse when a wave is incoming."""
        x, y = LY.ENTRIES[key]
        S = PAD_S * 0.8
        m = self._box(x, y, S * 1.6)
        if not m.any():
            return
        dx, dy = self.X[m] - x, self.Y[m] - y
        cheb = np.maximum(np.abs(dx), np.abs(dy))
        a = dx * self.rh[0] + dy * self.rh[1]
        b = dx * self.fh[0] + dy * self.fh[1]
        em = (band(cheb, S * 0.9, S * 0.97) * 1.2 + sample(glyph(GLYPH_OF["entry"]), a, b, S * 0.5) * 1.0)[:, None] * HALCYON
        em += ((np.mod((dx - dy) * 0.45, 1.0) < 0.3) * (cheb < S * 0.55) * 0.3)[:, None] * HARM
        if incoming:
            for k in range(3):
                rr = S * (1.0 + 0.2 * k + 0.2 * (t % 1.0))
                em += (band(cheb, rr, rr + 0.4) * (1.0 - 0.3 * k))[:, None] * HARM
        self.dk[m] *= 1 - 0.5 * (cheb < S)
        self.em[m] += em * self.k * (1.0 if active else 0.35)

    def riser(self, key, state="ok"):
        """Inlay traces from the socket into the node's building (ground, curb, sidewalk, facade)."""
        k = {"ok": 1.2, "dim": 0.3, "dead": 0.0, "hot": 2.0}[state]
        for poly in LY.riser_paths(key):
            P = np.array(poly, float)
            lo, hi = P.min(0) - 1.0, P.max(0) + 1.0
            m = ((self.X > lo[0]) & (self.X < hi[0]) & (self.Y > lo[1]) & (self.Y < hi[1]) & (self.Z > lo[2] - 0.5) &
                 (self.Z < hi[2] + 0.5))
            if not m.any():
                continue
            q = np.stack([self.X[m], self.Y[m], self.Z[m]], 1)
            dmin = np.full(q.shape[0], 1e9, np.float32)
            for i in range(len(P) - 1):
                a, b = P[i], P[i + 1]
                ab = b - a
                tt = np.clip(((q - a) @ ab) / max(1e-6, ab @ ab), 0, 1)
                d = np.linalg.norm(q - (a + tt[:, None] * ab), axis=1)
                dmin = np.minimum(dmin, d)
            tr = band(dmin, -1, 0.24)
            gr = band(dmin, -1, 0.6)
            self.dk[m] *= 1 - 0.45 * gr
            self.em[m] += (tr * k)[:, None] * self.lc * self.k

    def threat_ring(self, x, y, hp=1.0, state="live", t=0.0, txt=None):
        if txt:
            mm = self._box(x, y, 24, self.G)
            if mm.any():
                a = (self.X[mm] - x) * self.rh[0] + (self.Y[mm] - y) * self.rh[1]
                b = (self.X[mm] - x) * self.fh[0] + (self.Y[mm] - y) * self.fh[1]
                tm = text_mask(txt)
                hw = 9.0
                self.em[mm] += (sample(tm, a, b + 16.0, hw, hw * tm.shape[0] / tm.shape[1]) * 1.4)[:, None] * HARM * self.k
        m = self._box(x, y, 15, self.G)
        if not m.any():
            return
        dx, dy = self.X[m] - x, self.Y[m] - y
        r = np.hypot(dx, dy)
        ang = np.mod(np.arctan2(dy, dx) / (2 * math.pi) + 0.25, 1.0)
        seg = (np.mod(ang * 14, 1) < 0.7)
        lit = ang < hp
        ring = band(r, 11.0, 12.4) * seg
        if state == "held":
            col = ICE
            crystal = band(np.abs(np.mod(np.arctan2(dy, dx) * 6 / math.pi, 1) - 0.5) * r, -1, 0.3) * (r < 11)
            em = (ring * 2.4 + crystal * 1.6 + band(r, -1, 10.6) * 0.25)[:, None] * col
        elif state == "down":
            xx = band(np.abs(np.abs(dx) - np.abs(dy)), -1, 0.6) * (r < 10)
            em = (ring * 0.3 + xx * 0.9)[:, None] * C(0.6, 0.6, 0.65)
        else:
            em = (ring * np.where(lit, 1.4, 0.18))[:, None] * HARM + (band(r, -1, 10.6) * 0.12)[:, None] * HARM
        self.em[m] += em * self.k

    def pool_ring(self, x, y, r, col=WHITE, k=1.0):
        m = self._box(x, y, r + 2, self.GP)
        if not m.any():
            return
        rr = np.hypot(self.X[m] - x, self.Y[m] - y)
        self.em[m] += (band(rr, r - 0.4, r) * k)[:, None] * col * self.k

    def result(self):
        return self.em, self.dk


# ------------------------------------------------------------------ the default network state
def setup_state(net, forecast=True, link_states=None, statuses=None, t=0.0, packets=False, hud=False, integ=None,
                exposed=(), entries_incoming=(), routes=("r1", "r2", "r3"), skip=()):
    """Draw the standard raid setup network: links, risers, sockets, entries, threat lanes."""
    st = statuses or {k: ("home" if k == "core" else "holds") for k in LY.NODES}
    integ = integ or {}
    fc = {k: LY.NODES[k][4] for k in LY.NODES} if forecast else {}
    link_states = link_states or {}
    for a, b in LY.LINKS:
        s = link_states.get((a, b), link_states.get((b, a)))
        if s is None:
            s = "ok"
            if "seized" in (st.get(a), st.get(b)):
                s = "dead"
            elif "disabled" in (st.get(a), st.get(b)):
                s = "dim"
        net.link(a, b, s, t=t, packets=packets)
    for key in LY.NODE_BUILDINGS:
        sk = st.get(key, "holds")
        net.riser(key, "dead" if sk == "seized" else "dim" if sk in ("disabled", "burnt") else "ok")
    for rid in routes:
        pts = LY.route_points(rid)
        lanes_on_street(net, pts)
    for k in LY.ENTRIES:
        net.entry(k, active=any(LY.ROUTES[r][0] == k for r in routes), incoming=k in entries_incoming, t=t)
    for k in LY.NODES:
        if k in skip:
            continue
        f = fc.get(k)
        if f in ("holds", "home"):
            f = None if st.get(k) in ("holds", "home") else f
        n_int = integ.get(k, 1.0)
        hud_txt = None
        if hud:
            mx = LY.NODES[k][5][1]
            hud_txt = "%02d/%02d" % (round(n_int * mx), mx)
        net.pad(k, st.get(k, "holds"), integ=n_int, forecast=f, exposed=k in exposed, t=t, hud=hud_txt)


def lanes_on_street(net, pts, style="solid", t=0.0):
    """Threat lane along a route; beside our own link (offset) where they share a street."""
    linkset = set()
    for a, b in LY.LINKS:
        linkset.add((LY.pt(a), LY.pt(b)))
        linkset.add((LY.pt(b), LY.pt(a)))
    for i in range(len(pts) - 1):
        seg = [pts[i], pts[i + 1]]
        off = -6.2 if (tuple(pts[i]), tuple(pts[i + 1])) in linkset else 0.0
        stops = [LY.pt(k) for k in LY.NODES] + list(LY.ENTRIES.values())
        net.lane(seg, style=style, off=off, t=t, trim=(tuple(pts[i]) in stops, tuple(pts[i + 1]) in stops))
