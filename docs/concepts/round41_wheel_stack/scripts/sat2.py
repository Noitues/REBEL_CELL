"""Round 39: satellites v2 + the parasite ring.

Changes from round 38 (sat.py):
- a satellite is CENTRED on the slice it docks to (dock angle = slice mid);
- the bar struts are replaced by a rounded CRADLE: an arc band hugging the host rim over the docked slice, a
  waisted neck, and a collar ring round the satellite (all drawn UNDER the host, so the host blade stays on top);
- satellites sit further out (clear of the host blade) and orbit the host's EXACT centre (all positions are
  computed from one centre C; frames are placed by that centre, never by bounding box);
- slice glyph and value are bigger and spread ANGULARLY along each slice (glyph at mid - k*span, value at mid + k*span);
- destroyed = the binary-bit explosion (flash, shock ring, 0/1 bits blasting out and falling; round 21 language);
- a new satellite OVERWRITES the one on an occupied slice (the old one is knocked off and bit-bursts).

Parasite ring (boss mechanic): latches onto one host slice and forms a temporary partial THIRD ring segment over
that slice's arc, outside the host frame, with 3 small slices of NEGATIVE effects on the host slice.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import frames as F
from frames import P, Q, layer, add_glow, over_pil, INK, CREAM
import d4corp as D
import roster_wheel as RW
import slicelib as SL
from slicelib import PROGRAMS, render_slice, f_num, f_ui, f_mono, glyph_rgba, number_rgba, shadowed
from sat import BOTNET_DRONE, SEED_DRONE, CARE_DRONE, sat_acc, active_slot, HP_COL, HURT
from preview15 import dashed_poly

R_OUT0, R_IN0 = SL.R_OUT, SL.R_IN
SAT_K = 0.30
SAT_R = (R_OUT0 + 44) * SAT_K       # satellite outer radius in host master units
GAP = 112                           # from the host frame edge (RA) to the satellite's inner edge: clears the host blade


def dock_r(RA):
    return RA + GAP + SAT_R


# ================================================================== satellite (own wheel)
def render_sat(sat, ang, ss=1, lod=False, srot=0.0, state=None, t=0.4):
    F.set_centre()
    state = state or {}
    canvas = F.new_canvas(ss)
    n = len(sat["slots"])
    span = 360.0 / n
    acc = sat_acc(sat)
    theme = sat["theme"]
    dx, dy = F.grids(ss)
    rho = np.hypot(dx, dy)
    bp = np.clip(R_OUT0 + 4 - rho, 0, 1)
    canvas[..., :3] = canvas[..., :3] * (1 - bp[..., None]) + np.array([0.02, 0.018, 0.03]) * bp[..., None]
    canvas[..., 3] = np.maximum(canvas[..., 3], bp)
    del dx, dy, rho, bp
    act = active_slot(sat, srot)
    opts = dict(RW.LOD) if lod else {}
    opts.update(upright=True, icons=False)
    for j, (prog, val) in enumerate(sat["slots"]):
        a0 = ang - span / 2 + j * span + srot
        render_slice(canvas, F.CX * ss, F.CY * ss, prog, a0, span, val, (t + j * 0.21) % 1.0, theme, ss, dict(opts), seed=j + 11)
    im, d = layer(ss)
    for j in range(n):
        if j != act:
            a0 = ang - span / 2 + j * span + srot
            d.polygon(F.wedge_pts(a0 + 0.5, a0 + span - 0.5, R_IN0 - 2, R_OUT0 + 1, ss, 60), fill=(0, 0, 0, 92))
    over_pil(canvas, im)
    # big glyph + value, spread ANGULARLY along the slice, upright, on soft read plates
    im, d = layer(ss)
    rc = R_IN0 + 0.60 * (R_OUT0 - R_IN0)
    spread = 0.20 if n == 2 else 0.17
    gpx = 150 if n == 2 else 128
    for j, (prog, val) in enumerate(sat["slots"]):
        mid = ang + j * span + srot
        items = [("g", prog, mid - span * spread), ("v", val, mid + span * spread)]
        for kind, x, a in items:
            px, py = P(rc, a, ss)
            pl = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(pl).ellipse([px - 92 * ss, py - 80 * ss, px + 92 * ss, py + 80 * ss], fill=(0, 0, 0, 150))
            im.alpha_composite(pl.filter(ImageFilter.GaussianBlur(26 * ss)))
            if kind == "g":
                g = shadowed(glyph_rgba(x, gpx * ss, 9 * ss), ss)
            else:
                g = shadowed(number_rgba(str(x), gpx * 1.25 * ss, 9 * ss), ss)
            im.alpha_composite(g, (int(px - g.width / 2), int(py - g.height / 2)))
    over_pil(canvas, im)
    is_player = theme == "player"
    base = (0.16, 0.15, 0.19) if is_player else D.CORP_STYLE[theme]["base"]
    R1 = R_OUT0 + 44
    F.machined(canvas, ss, [(R_OUT0 - 4, 0.0), (R_OUT0 - 1, 6.0), (R1 - 4, 8.0), (R1, 0.0)], base, acc, seed=5,
               accent_r=((R_OUT0 + 2, 0.9, 0.9), (R1 - 1.0, 1.2, 1.2)), brushed=0.04)
    im, d = layer(ss)
    gl, gd = layer(ss)
    for k in range(30):
        a = ang + k * 12
        major = k % (30 // n) == 0
        d.line([P(R_OUT0 + 8, a, ss), P(R_OUT0 + (26 if major else 16), a, ss)], fill=(235, 235, 245, 255) if major else acc + (200,),
               width=int((5 if major else 3) * ss))
    a0 = ang - span / 2 + act * span + srot
    pc = PROGRAMS[sat["slots"][act][0]]["col"]
    pts = F.wedge_pts(a0 + 1.2, a0 + span - 1.2, R_IN0 + 2, R_OUT0 - 2, ss, 60)
    gd.polygon(pts, outline=pc + (255,), width=int(18 * ss))
    d.polygon(pts, outline=INK + (255,), width=int(12 * ss))
    d.polygon(pts, outline=CREAM + (255,), width=int(7 * ss))
    hr = R_IN0 - 6
    cx, cy = F.CX * ss, F.CY * ss
    d.ellipse([cx - hr * ss, cy - hr * ss, cx + hr * ss, cy + hr * ss], fill=(12, 11, 18, 255), outline=acc + (255,), width=int(5 * ss))
    hp, hpmax = sat["hp"], sat["hpmax"]
    hpv = state.get("hp", hp)
    for k in range(hpmax):
        a_ = -150 + 300 * (k + 0.5) / hpmax
        col = HP_COL if k < hpv else (HURT if k < hp else (50, 60, 52))
        pa = RW.arc_poly(hr - 26, hr - 8, a_ - 120 / hpmax + 3, a_ + 120 / hpmax - 3, ss, 6)
        pa = [(x - RW.CX * ss + cx, y - RW.CY * ss + cy) for x, y in pa]
        d.polygon(pa, fill=col + (255,))
    f = f_num(int(110 * ss))
    s = str(hpv)
    d.text((cx - f.getlength(s) / 2, cy - 72 * ss), s, font=f, fill=(HP_COL if hpv > 0 else HURT) + (255,), stroke_width=int(4 * ss), stroke_fill=INK + (255,))
    add_glow(canvas, gl, ss, 0.8)
    over_pil(canvas, im)
    val = sat["slots"][act][1]
    top = R1 + 170
    bl, bg = F.blade(ss, ang, acc, CREAM if is_player else D.mix(acc, (255, 255, 255), 0.35), (230, 220, 200), val,
                     sat["slots"][act][0], tip=R_OUT0 - 40, sh=R1 + 34, top=top, wsh=70, wtop=96, win=(R1 + 52, top - 26, 74))
    F.shadow_of(canvas, bl, ss, 10, 16, 6, 0.6)
    add_glow(canvas, bg, ss, 0.9)
    over_pil(canvas, bl)
    if state.get("guard") is not None:
        im, d = layer(ss)
        gl, gd = layer(ss)
        r = R1 + 30
        bb = [cx - r * ss, cy - r * ss, cx + r * ss, cy + r * ss]
        ga = state["guard"]
        gd.arc(bb, ga - 90 - 60, ga - 90 + 60, fill=(120, 220, 255, 255), width=int(40 * ss))
        d.arc(bb, ga - 90 - 60, ga - 90 + 60, fill=(200, 240, 255, 255), width=int(14 * ss))
        x, y = P(r, ga, ss)
        star = [(x + (80 if k % 2 == 0 else 34) * ss * math.cos(math.radians(k * 22.5)), y + (80 if k % 2 == 0 else 34) * ss * math.sin(math.radians(k * 22.5))) for k in range(16)]
        gd.polygon(star, fill=(255, 230, 160, 255))
        d.polygon(star, fill=(255, 240, 200, 255), outline=INK + (255,))
        add_glow(canvas, gl, ss, 1.0, blur=10)
        over_pil(canvas, im)
    F.set_centre()
    rgb = np.clip(canvas[..., :3], 0, 1)
    al = np.clip(canvas[..., 3:], 0, 1)
    st = np.where(al > 1e-4, rgb / np.maximum(al, 1e-4), 0)
    out = Image.fromarray((np.clip(np.concatenate([st, al], 2), 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")
    return out, (F.CX * ss, F.CY * ss)


# ================================================================== effects
def bit_burst(img, x, y, t, seed=9, n=120, col=(255, 70, 160), radius=260, font_px=(22, 40)):
    """Round 21 language: flash, shock ring, 0/1 bits blasting out, falling and fading. t in [0, 1]."""
    rng = np.random.default_rng(seed)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if t < 0.3:
        r = 30 + radius * 1.4 * t
        a = int(255 * (1 - t / 0.3))
        d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 230, 245, a), width=8)
        fl = int(230 * (1 - t / 0.3))
        d.ellipse([x - 80, y - 80, x + 80, y + 80], fill=(255, 240, 250, fl))
    for i in range(n):
        ang = rng.uniform(0, 2 * math.pi)
        sp = rng.uniform(0.3, 1.0) * radius
        rr = sp * (1 - (1 - min(1.0, t * 1.6)) ** 2)
        px = x + math.cos(ang) * rr
        py = y + math.sin(ang) * rr - 60 * math.sin(math.pi * min(1, t * 1.6)) * rng.uniform(0.3, 1) + 160 * t * t
        a = int(255 * max(0.0, 1 - t * 1.05) * rng.uniform(0.6, 1.0))
        if a <= 0:
            continue
        size = int(rng.uniform(*font_px))
        c = col if rng.random() < 0.6 else (255, 240, 250)
        d.text((px, py), rng.choice(["0", "1"]), font=f_mono(size), fill=c + (a,), anchor="mm")
    img.alpha_composite(lay)


def fade(im, k):
    im = im.copy()
    im.putalpha(im.split()[3].point(lambda v: int(v * k)))
    return im


def greyed(im, k=0.4):
    a = np.asarray(im, np.float32)
    lum = a[..., :3].mean(axis=2, keepdims=True)
    a[..., :3] = lum * k
    return Image.fromarray(a.astype(np.uint8), "RGBA")


# ================================================================== host composite
MARGIN = 760
_SAT_CACHE = {}


def host_image(spec, rot=0.0, ss=1, hp_number=False):
    s = dict(spec)
    s["drones"] = []
    return D.render(s, ss=ss, rot=rot, hp_number=hp_number)


class Comp:
    """A fixed-size canvas with the host's EXACT centre at C; everything is placed from C."""

    def __init__(self, host, size=None):
        him, hc, meta = host
        self.meta = meta
        self.RA = meta["hp_r"] - 36
        self.W = him.width + 2 * MARGIN if size is None else size[0]
        self.H = him.height + 2 * MARGIN if size is None else size[1]
        self.C = (self.W / 2, self.H / 2) if size is not None else (hc[0] + MARGIN, hc[1] + MARGIN)
        self.him, self.hc = him, hc
        self.under = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        self.top = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))

    def PP(self, r, a):
        return (self.C[0] + r * math.sin(math.radians(a)), self.C[1] - r * math.cos(math.radians(a)))

    def cradle(self, a, acc, half=22.0, k=1.0):
        """Rounded cradle hugging the host rim over the docked slice + waisted neck + collar ring."""
        d = ImageDraw.Draw(self.under)
        RA, Rd = self.RA, dock_r(self.RA)
        r0, r1 = RA - 4, RA + 30
        band = [self.PP(r1, a - half + half * 2 * j / 40) for j in range(41)] + [self.PP(r0, a + half - half * 2 * j / 40) for j in range(41)]
        cap = []
        for side in (-1, 1):  # rounded ends
            ex, ey = self.PP((r0 + r1) / 2, a + side * half)
            cap.append((ex, ey))
        neck = []
        n = 24
        y0r, y1r = r1 - 2, Rd - SAT_R + 6
        for side in (-1, 1):
            pts = []
            for j in range(n + 1):
                q = j / n
                r = y0r + (y1r - y0r) * q
                w = (0.62 - 0.40 * math.sin(math.pi * q * 0.85)) * (SAT_R * 0.9)  # waisted
                w = max(w, 18)
                pts.append(self.PP(r, a + side * math.degrees(w / r)))
            neck.append(pts)
        poly = neck[0] + neck[1][::-1]
        for fill, wd in (((62, 60, 72, 255), 0),):
            d.polygon(band, fill=fill)
            d.polygon(poly, fill=fill)
            for (ex, ey) in cap:
                rr = (r1 - r0) / 2
                d.ellipse([ex - rr, ey - rr, ex + rr, ey + rr], fill=fill)
        d.line(band[:41], fill=acc + (255,), width=5)
        d.line(band[41:], fill=(90, 88, 100, 255), width=3)
        d.line(neck[0], fill=acc + (255,), width=5)
        d.line(neck[1], fill=acc + (255,), width=5)
        mid_line = [self.PP(y0r + (y1r - y0r) * j / 12, a) for j in range(13)]
        d.line(mid_line, fill=(120, 118, 132, 255), width=6)
        sx, sy = self.PP(Rd, a)
        rr = SAT_R + 16
        d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], outline=(62, 60, 72, 255), width=24)
        d.ellipse([sx - rr - 10, sy - rr - 10, sx + rr + 10, sy + rr + 10], outline=acc + (255,), width=4)
        d.ellipse([sx - rr + 10, sy - rr + 10, sx + rr - 10, sy + rr - 10], outline=(90, 88, 100, 255), width=3)
        for side in (-1, 1):  # rivets on the band
            for j in (0.3, 0.75):
                x, y = self.PP((r0 + r1) / 2, a + side * half * j)
                d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(200, 196, 210, 255), outline=INK + (255,))

    def put_sat(self, sat, a, state=None, lod=False, alpha=1.0, offset=0.0, spin=0.0, grey=False):
        key = (sat["name"], round(a + spin, 2), lod, repr(sorted((state or {}).items())))
        if key not in _SAT_CACHE:
            _SAT_CACHE[key] = render_sat(sat, a + spin, lod=lod, srot=(state or {}).get("srot", 0.0), state=state)
        sim, sc = _SAT_CACHE[key]
        k = SAT_K
        sim = sim.resize((int(sim.width * k), int(sim.height * k)), Image.LANCZOS)
        if grey:
            sim = greyed(sim)
        if alpha < 1:
            sim = fade(sim, alpha)
        sx, sy = self.PP(dock_r(self.RA) + offset, a)
        self.top.alpha_composite(sim, (int(round(sx - sc[0] * k)), int(round(sy - sc[1] * k))))
        return sx, sy

    def ghost(self, sat, a):
        d = ImageDraw.Draw(self.top)
        gx, gy = self.PP(dock_r(self.RA), a)
        rr = SAT_R
        g = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        gd.ellipse([gx - rr, gy - rr, gx + rr, gy + rr], fill=sat_acc(sat) + (60,))
        circ = [(gx + rr * math.cos(math.radians(k * 6)), gy + rr * math.sin(math.radians(k * 6))) for k in range(60)]
        dashed_poly(gd, circ, sat_acc(sat) + (255,), 6, dash=18, gap=10)
        gg = glyph_rgba("DRONE", int(rr * 1.0), 3)
        gg.putalpha(gg.split()[3].point(lambda v: int(v * 0.75)))
        g.alpha_composite(gg, (int(gx - gg.width / 2), int(gy - gg.height / 2)))
        self.top.alpha_composite(g)

    def chase(self, N, ph):
        d = ImageDraw.Draw(self.top)
        R_ch = self.RA + 62
        head = ph * (N + 1.5)
        for j in range(N):
            aa = -12 * (j + 0.6)
            dist = head - (j + 1)
            al = 0.35 if ph >= 1 else (0.18 + 0.82 * math.exp(-(dist / 1.1) ** 2) if dist > -1.5 else 0.10)
            if 1.5 < dist and ph < 1:
                al = max(al, 0.35)
            w = 64
            da = math.degrees(w / R_ch)
            tip = self.PP(R_ch, aa - da * 0.55)
            l0, l1 = self.PP(R_ch + w * 0.62, aa + da * 0.45), self.PP(R_ch - w * 0.62, aa + da * 0.45)
            m0, m1 = self.PP(R_ch + w * 0.62, aa + da * 1.0), self.PP(R_ch - w * 0.62, aa + da * 1.0)
            nt = self.PP(R_ch, aa)
            col = tuple(int(255 * (1 - al) + (255, 214, 64)[k] * al) for k in range(3))
            d.polygon([l0, tip, l1, m1, nt, m0], fill=col + (int(50 + 205 * al),), outline=INK + (int(90 + 165 * al),))

    def image(self, scale=1.0, crop=None):
        out = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        out.alpha_composite(self.under)
        out.alpha_composite(self.him, (int(round(self.C[0] - self.hc[0])), int(round(self.C[1] - self.hc[1]))))
        out.alpha_composite(self.top)
        if crop:
            out = out.crop(crop)
        if scale != 1.0:
            out = out.resize((max(1, int(out.width * scale)), max(1, int(out.height * scale))), Image.LANCZOS)
        return out


def compose(spec, sats, rot=0.0, states=None, ghosts=None, chase=None, host=None, lod=False, hp_number=True, size=None):
    host = host or host_image(spec, rot, hp_number=hp_number)
    c = Comp(host, size)
    states = states or {}
    for i, sat in sats:
        c.cradle(60 * i + rot, sat_acc(sat))
    if chase:
        c.chase(*chase)
    for i, N in ghosts or []:
        c.ghost(dict(sats)[i], 60 * i + rot + 12 * N)
    for i, sat in sats:
        st = states.get(i)
        if st and st.get("hidden"):
            continue
        c.put_sat(sat, 60 * i + rot, state=st, lod=lod)
    return c


# ================================================================== parasite ring
PARASITE = [("ST_PARASITE", "x0.5", "output halved"), ("PI_RAM", "-2", "drains 2 RAM"), ("ST_CORRUPTED", "CRPT", "slice corrupted")]
PAR_COL = (214, 60, 255)


def parasite(c, slot, prog=1.0, lod=False, turns=3, lit=None, t=0.4):
    """Draw the parasite ring segment over host slot `slot` (60 deg arc), outside the host frame.
    prog 0..1 grows it (latch animation). lit = index of the sub-slice applying now."""
    RA = c.RA
    r_in = RA + 54
    r_out_full = RA + 54 + 150
    r_out = r_in + (r_out_full - r_in) * max(0.05, prog)
    a_mid = 60 * slot
    a0 = a_mid - 28
    span = 56.0
    ss = 1
    # 1) claws: tendrils from the host rim to the ring (always draw first, under)
    d = ImageDraw.Draw(c.under)
    for k in range(5):
        a = a0 + 4 + k * (span - 8) / 4
        pts = []
        for j in range(13):
            q = j / 12
            r = RA - 10 + (r_in + 6 - (RA - 10)) * q * min(1, prog * 1.6)
            pts.append(c.PP(r, a + 3 * math.sin(q * math.pi * 2 + k)))
        d.line(pts, fill=(60, 10, 70, 255), width=16)
        d.line(pts, fill=PAR_COL + (255,), width=6)
        x, y = pts[0]
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=PAR_COL + (255,), outline=INK + (255,))
    if prog <= 0.05:
        return
    # 2) the sub-slices: real C screens (VIRUS ooze), radii swapped to the parasite ring
    canvas = np.zeros((c.H, c.W, 4), np.float32)
    old = (SL.R_OUT, SL.R_IN)
    SL.R_OUT, SL.R_IN = r_out_full, r_in  # always render full size; the grow is a radial mask below
    try:
        n = len(PARASITE)
        sp = span / n
        for j in range(n):
            render_slice(canvas, c.C[0], c.C[1], "VIRUS", a0 + j * sp, sp, None, (t + 0.3 * j) % 1, "player", 1,
                         dict(upright=True, icons=False, tex_gain=0.8), seed=31 + j)
    finally:
        SL.R_OUT, SL.R_IN = old
    rgb, al = canvas[..., :3], canvas[..., 3:]
    st = np.where(al > 1e-4, rgb / np.maximum(al, 1e-4), 0)
    if prog < 1:
        yy, xx = np.mgrid[0:c.H, 0:c.W].astype(np.float32)
        rho = np.hypot(xx - c.C[0], yy - c.C[1])
        al = al * np.clip((r_out - rho) / 4 + 0.5, 0, 1)[..., None]
    ring = Image.fromarray((np.clip(np.concatenate([st, al], 2), 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")
    c.top.alpha_composite(ring)
    d = ImageDraw.Draw(c.top)
    gl = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    # frame: a fleshy violet rim with barbs, on both arcs
    for r in (r_in - 6, r_out + 6):
        arc = [c.PP(r, a0 - 2 + (span + 4) * j / 60) for j in range(61)]
        gd.line(arc, fill=PAR_COL + (200,), width=18)
        d.line(arc, fill=(40, 6, 48, 255), width=14)
        d.line(arc, fill=PAR_COL + (255,), width=5)
    for k in range(9):  # barbs on the outer arc
        a = a0 + span * (k + 0.5) / 9
        b = [c.PP(r_out + 6, a - 2.2), c.PP(r_out + 30, a), c.PP(r_out + 6, a + 2.2)]
        d.polygon(b, fill=PAR_COL + (255,), outline=INK + (255,))
    if prog >= 0.98:
        sp = span / len(PARASITE)
        rc = (r_in + r_out) / 2
        for j, (gname, val, desc) in enumerate(PARASITE):
            mid = a0 + sp * (j + 0.5)
            if lit == j:
                pts = F.wedge_pts(0, 0, 0, 0, 1, 2)
                poly = [c.PP(r_out - 4, mid - sp / 2 + 0.6 + (sp - 1.2) * q / 20) for q in range(21)] + \
                       [c.PP(r_in + 4, mid + sp / 2 - 0.6 - (sp - 1.2) * q / 20) for q in range(21)]
                gd.polygon(poly, outline=(255, 255, 255, 255), width=18)
                d.polygon(poly, outline=(255, 240, 255, 255), width=6)
            x, y = c.PP(rc + (16 if not lod else 0), mid)
            pl = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
            ImageDraw.Draw(pl).ellipse([x - 44, y - 50, x + 44, y + 50], fill=(0, 0, 0, 170))
            c.top.alpha_composite(pl.filter(ImageFilter.GaussianBlur(12)))
            g = shadowed(glyph_rgba(gname, 52 if not lod else 70, 4), 1)
            c.top.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2 - (18 if not lod else 0))))
            if not lod:
                f = f_num(30)
                tw = f.getlength(val)
                d = ImageDraw.Draw(c.top)
                d.text((x - tw / 2, y + 6), val, font=f, fill=(255, 150, 210, 255), stroke_width=3, stroke_fill=INK + (255,))
        # turns left pips + tag
        d = ImageDraw.Draw(c.top)
        for k in range(3):
            x, y = c.PP(r_out + 50, a0 + span / 2 + (k - 1) * 5)
            on = k < turns
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(PAR_COL if on else (60, 40, 70)) + (255,), outline=INK + (255,), width=2)
    c.top.alpha_composite(gl.filter(ImageFilter.GaussianBlur(8)))
    ov = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
    c.top.alpha_composite(ov)
