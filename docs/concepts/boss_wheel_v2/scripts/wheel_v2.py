"""Boss Wheel v2: the template. One compositor, named layer slots, every boss built the same way.

LAYER SLOTS (bottom -> top), each supplied by a Direction object (see roman.py / atlantis.py):
  back_plate      static stage behind everything (also seen through the blank window), parallax depth 1.0
  art_ring_under  ring art behind the slices, turns with the wheel (lags 3 % in a spin: parallax)
  slice_scenes[]  one illustrated, upright scene per slice, masked to its wedge
  blank_window    NULL slices: dark glass onto back_plate + art_ring_under, art dimmed, thin empty outline
  rim_band        slice colour = type, a band per slice at the rim
  (plaque zone)   art under each value plaque is desaturated and darkened
  bezel           the D4 lens & rail frame in the corp material: ticks, telemetry ring, readout rail
  threat_ring     counter-rotating boss ring (D4 boss extra)
  art_ring_over   static overlay art over the rim (arches, tentacles), kept outside r 318
  plaques         value + glyph on a fixed dark plaque, upright, r = 290: ALWAYS on top of the art
  hub_portrait    the boss portrait / emblem, animated
  needle_rig      the thematic pointer: a locked cream blade (precision + value window) + its actor
  fx_idle / fx_land / fx_phase   motion layers; each has a static reduce-effects end state

Master units: R_OUT = 352 (slice outer edge), wheel combat radius r = 236 px -> S = 236 / 360.
"""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

import bw_kit as K

R = dict(hub=112, hub_rim=128, sl_in=130, sl_out=352, band_in=334, plaque_r=290, bezel_in=352, bezel_out=398,
         threat_in=402, threat_out=426, hp_in=438, hp_out=458, over_min=318, canvas=700)
PLAQUE_H = 64
NUM_PX = 60
GLYPH_PX = 46
SLOT_DEG = 60.0
LAYER_ORDER = ["back_plate", "art_ring_under", "slice_scenes", "blank_window", "rim_band", "plaque_zone", "bezel",
               "threat_ring", "art_ring_over", "plaques", "hub_portrait", "needle_rig", "fx_idle", "fx_land", "fx_phase"]


class Ctx:
    def __init__(self, S, t=0.0, phase=1, hp=1.0, rot=0.0, **kw):
        self.S = S
        self.C = int(2 * R["canvas"] * S)
        self.cx = self.cy = self.C / 2
        self.size = (self.C, self.C)
        self.t, self.phase, self.hp, self.rot = t, phase, hp, rot
        self.state = dict(kw)

    def P(self, r, a):
        return K.pol(self.cx, self.cy, r * self.S, a)

    def m(self, v):
        return v * self.S

    def get(self, k, d=None):
        return self.state.get(k, d)


def slot_angle(i, rot):
    return SLOT_DEG * i + rot


def wedge_mask(ctx, i, rot, r0=None, r1=None, inset=0.0, gap=3.0):
    r0 = R["sl_in"] if r0 is None else r0
    r1 = R["sl_out"] if r1 is None else r1
    a = slot_angle(i, rot)
    half = SLOT_DEG / 2
    m = K.L(ctx.size)
    d = ImageDraw.Draw(m)
    n = 48
    g0 = math.degrees((gap + inset) / max(1, r1))
    g1 = math.degrees((gap + inset) / max(1, r0))
    pts = [ctx.P(r1 - inset, a - half + g0 + (2 * half - 2 * g0) * k / n) for k in range(n + 1)]
    pts += [ctx.P(r0 + inset, a + half - g1 - (2 * half - 2 * g1) * k / n) for k in range(n + 1)]
    d.polygon(pts, fill=255)
    return m


def scene_box(ctx):
    """Upright scene sprite size (px): covers the wedge at any angle."""
    return int(2 * 190 * ctx.S)


def slice_centre(ctx, i, rot):
    return ctx.P((R["sl_in"] + R["sl_out"]) / 2 + 6, slot_angle(i, rot))


def plaque_centre(ctx, i, rot):
    return ctx.P(R["plaque_r"], slot_angle(i, rot))


# ------------------------------------------------------------------ plaques (readability core)
def plaque(ctx, slot, special_mask=None, scale=1.0, state=None, ghost=False):
    """Value plaque: dark backing, type-colour cap, locked glyph + Bahnschrift number. Upright."""
    S = ctx.S * scale
    typ = slot["type"]
    col = K.TYPE_COL[typ]
    val = slot.get("value")
    gname = slot.get("glyph") or K.TYPE_GLYPH[typ]
    gpx = int(GLYPH_PX * S)
    g = K.glyph(gname, gpx, mask=special_mask, fill=(255, 255, 255) if typ != "NULL" else (170, 170, 176))
    num = None
    if val is not None and typ != "NULL":
        num = K.text_img(str(val), K.f_num(int(NUM_PX * S)), fill=(255, 255, 255), stroke=max(1, int(2.2 * S)))
    pad = 12 * S
    gap = 4 * S
    w = pad * 2 + g.width - 8 * S + ((num.width + gap) if num else 0)
    w = max(w, 92 * S)
    h = PLAQUE_H * S
    im = K.rgba((int(w + 20 * S), int(h + 20 * S)))
    d = ImageDraw.Draw(im)
    x0, y0 = 10 * S, 10 * S
    # soft dark halo so the plaque separates from any art
    halo = K.L(im.size)
    ImageDraw.Draw(halo).rounded_rectangle([x0 - 2 * S, y0 - 2 * S, x0 + w + 2 * S, y0 + h + 2 * S], radius=14 * S, fill=200)
    im.alpha_composite(K.solid(K.blur(halo, 6 * S), (0, 0, 0), 0.85))
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=11 * S, fill=(10, 8, 16, 236), outline=K.mix(col, (0, 0, 0), 0.35) + (255,),
                        width=max(1, int(1.6 * S)))
    # type cap: a bright bar along the outer edge (screen-top) + small corner ticks
    d.rounded_rectangle([x0 + 6 * S, y0 + 3 * S, x0 + w - 6 * S, y0 + 8 * S], radius=2 * S, fill=col + (255,))
    d.line([(x0 + 10 * S, y0 + h - 4 * S), (x0 + w - 10 * S, y0 + h - 4 * S)], fill=(255, 255, 255, 34), width=max(1, int(S)))
    gy = y0 + h / 2 + 3 * S
    if num:
        K.paste_c(im, g, x0 + pad + g.width / 2 - 4 * S, gy)
        K.paste_c(im, num, x0 + pad + g.width - 8 * S + gap + num.width / 2, gy - 1 * S)
    else:
        K.paste_c(im, g, x0 + w / 2, gy)
    if ghost:
        im = K.tone(im, 0.3, 0.6)
    return im


# ------------------------------------------------------------------ bezel (D4 'lens & rail' in a corp material)
def bezel(ctx, mat, telemetry, rail=None, ticks=True, cracks=0.0, seed=7, rail_at=0.0):
    """mat: dict(base, hi, lo, accent, glass). rail: (text, colour) for the readout rail over the pointer (+-50 deg)."""
    S = ctx.S
    im = K.rgba(ctx.size)
    r0, r1 = R["bezel_in"] * S, R["bezel_out"] * S
    ring = K.ring_mask(ctx.size, ctx.cx, ctx.cy, r0, r1)
    rr, ang = K.polar_field(ctx.size, ctx.cx, ctx.cy)
    tt = np.clip((rr - r0) / max(1, r1 - r0), 0, 1)
    # machined profile: lip highlight, channel, outer lip
    prof = np.interp(tt, [0, 0.08, 0.2, 0.32, 0.68, 0.8, 0.92, 1], [0.55, 1.0, 0.7, 0.28, 0.28, 0.75, 1.0, 0.45])
    light = 0.82 + 0.28 * np.cos(np.radians(ang - 315))
    base, hi, lo = (np.array(c, np.float32) for c in (mat["base"], mat["hi"], mat["lo"]))
    v = np.clip(prof * light, 0, 1.4)[..., None]
    col = np.where(v > 0.6, base + (hi - base) * np.clip((v - 0.6) / 0.6, 0, 1), lo + (base - lo) * np.clip(v / 0.6, 0, 1))
    n = K.noise(ctx.size, max(4, int(18 * S)), seed, 3)[..., None]
    col = col * (0.9 + 0.2 * n)
    a = np.asarray(ring, np.float32)[..., None]
    im = Image.fromarray(np.concatenate([np.clip(col, 0, 255), a], 2).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(im)
    # glass channel (telemetry) at the middle of the bezel
    ch0, ch1 = (R["bezel_in"] + 14) * S, (R["bezel_out"] - 14) * S
    chm = K.ring_mask(ctx.size, ctx.cx, ctx.cy, ch0, ch1)
    im.alpha_composite(K.solid(chm, mat["glass"], 0.92))
    # telemetry text scrolling round the channel
    tel = K.rgba(ctx.size)
    f = K.f_mono(max(6, int(13 * S)))
    rmid = (ch0 + ch1) / 2
    s_ = (telemetry + "  //  ") * 8
    step = 360.0 / (len(s_) * 0.98)
    td = ImageDraw.Draw(tel)
    off = (ctx.t * 4.0) % 360
    for j, ch in enumerate(s_):
        a_ = j * step + off
        if rail and -54 < ((a_ - rail_at + 180) % 360) - 180 < 54:
            continue
        ci = K.text_img(ch, f, fill=K.mix(mat["accent"], (255, 255, 255), 0.25))
        ci = ci.rotate(-a_, resample=Image.BICUBIC, expand=True)
        x, y = K.pol(ctx.cx, ctx.cy, rmid, a_)
        tel.alpha_composite(ci, (int(x - ci.width / 2), int(y - ci.height / 2)))
    im.alpha_composite(K.masked(tel, chm).point(lambda v: v) if False else K.masked(tel, chm))
    # readout rail: static, tinted, bracketed, splits around the needle (+-8 deg gap)
    if rail:
        txt, rc = rail
        railm = K.ring_mask(ctx.size, ctx.cx, ctx.cy, ch0 - 2 * S, ch1 + 2 * S, rail_at - 52, rail_at + 52)
        cut = K.ring_mask(ctx.size, ctx.cx, ctx.cy, ch0 - 4 * S, ch1 + 4 * S, rail_at - 8, rail_at + 8)
        flip = 90 < (rail_at % 360) < 270
        railm = ImageChops.subtract(railm, cut)
        im.alpha_composite(K.solid(railm, K.mix(rc, (0, 0, 0), 0.72), 0.95))
        fr = K.f_ui(max(6, int(15 * S)), b"Bold Condensed")
        for side in (-1, 1):
            s2 = txt
            total = sum(fr.getlength(c) for c in s2) / (rmid) * 57.3
            a0 = 11 if side > 0 else -11 - total
            acc = a0
            for ch in s2:
                wdeg = fr.getlength(ch) / rmid * 57.3
                ci = K.text_img(ch, fr, fill=K.mix(rc, (255, 255, 255), 0.35))
                if flip:     # bottom rail: read left to right, upright
                    aa = rail_at - (acc + wdeg / 2)
                    ci = ci.rotate(-(aa - 180), resample=Image.BICUBIC, expand=True)
                else:
                    aa = rail_at + acc + wdeg / 2
                    ci = ci.rotate(-aa, resample=Image.BICUBIC, expand=True)
                x, y = K.pol(ctx.cx, ctx.cy, rmid, aa)
                im.alpha_composite(ci, (int(x - ci.width / 2), int(y - ci.height / 2)))
                acc += wdeg
        for a_ in (rail_at - 52, rail_at + 52):
            p0, p1 = K.pol(ctx.cx, ctx.cy, ch0 - 3 * S, a_), K.pol(ctx.cx, ctx.cy, ch1 + 3 * S, a_)
            d.line([p0, p1], fill=rc + (255,), width=max(1, int(3 * S)))
    # 30 precision ticks on the inner lip (every 12 deg; slice centres longer)
    if ticks:
        for k in range(30):
            a_ = k * 12 + ctx.rot
            ln = 10 if k % 5 == 0 else 5
            p0, p1 = K.pol(ctx.cx, ctx.cy, (R["bezel_in"] + 2) * S, a_), K.pol(ctx.cx, ctx.cy, (R["bezel_in"] + 2 + ln) * S, a_)
            d.line([p0, p1], fill=K.mix(mat["accent"], (255, 255, 255), 0.4) + (200,), width=max(1, int(2 * S)))
    # outer and inner hairlines in the accent
    for rr_ in (R["bezel_in"] + 1, R["bezel_out"] - 1):
        d.ellipse([ctx.cx - rr_ * S, ctx.cy - rr_ * S, ctx.cx + rr_ * S, ctx.cy + rr_ * S], outline=mat["accent"] + (150,), width=max(1, int(1.5 * S)))
    # glass crescent glint
    gl = K.ring_mask(ctx.size, ctx.cx, ctx.cy, (R["bezel_in"] + 3) * S, (R["bezel_in"] + 9) * S, 280, 350)
    im.alpha_composite(K.solid(K.blur(gl, 2 * S), (255, 255, 255), 0.35))
    if cracks > 0:
        im.alpha_composite(crack_layer(ctx, cracks, R["bezel_in"] - 4, R["bezel_out"] + 30, seed + 11, col=(20, 10, 10), glow=mat["accent"]))
    return im


def crack_layer(ctx, amount, r0, r1, seed, col=(16, 8, 8), glow=(255, 120, 60), n_max=7):
    """Damage cracks across a ring band: count and length grow with amount (0..1)."""
    S = ctx.S
    lay = K.rgba(ctx.size)
    d = ImageDraw.Draw(lay)
    gl_m = K.L(ctx.size)
    gd = ImageDraw.Draw(gl_m)
    r = K.rng(seed)
    n = int(round(n_max * amount))
    angs = r.uniform(0, 360, n_max)
    for j in range(n):
        a = angs[j]
        rr = r.uniform(r0, r1)
        pts = [K.pol(ctx.cx, ctx.cy, rr * S, a)]
        L_ = (40 + 90 * amount) * S
        heading = r.uniform(0, 360)
        for k in range(7):
            heading += r.uniform(-50, 50)
            x, y = pts[-1]
            st = L_ / 7
            pts.append((x + st * math.cos(math.radians(heading)), y + st * math.sin(math.radians(heading))))
            if k == 3:
                h2 = heading + r.choice([-70, 70])
                bx, by = pts[-1]
                br = [(bx, by), (bx + st * 1.4 * math.cos(math.radians(h2)), by + st * 1.4 * math.sin(math.radians(h2)))]
                d.line(br, fill=col + (230,), width=max(1, int(2 * S)))
                gd.line(br, fill=255, width=max(1, int(2 * S)))
        d.line(pts, fill=col + (240,), width=max(1, int(3.2 * S)), joint="curve")
        gd.line(pts, fill=255, width=max(1, int(3 * S)))
    lay = K.screen(lay, K.solid(K.blur(gl_m, 4 * S), glow, 0.7 * amount))
    return lay


# ------------------------------------------------------------------ HP arc + phase pips (D4)
def hp_arc(ctx, hp, accent, pips=(0.66, 0.33), span=(128, 232)):
    S = ctx.S
    im = K.rgba(ctx.size)
    d = ImageDraw.Draw(im)
    a0, a1 = span
    nseg = 26
    for k in range(nseg):
        aa = a1 - (a1 - a0) * (k + 0.1) / nseg
        ab = a1 - (a1 - a0) * (k + 0.9) / nseg
        on = (k + 0.5) / nseg <= hp
        pts = [K.pol(ctx.cx, ctx.cy, R["hp_out"] * S, aa + (ab - aa) * q / 4) for q in range(5)]
        pts += [K.pol(ctx.cx, ctx.cy, R["hp_in"] * S, ab - (ab - aa) * q / 4) for q in range(5)]
        d.polygon(pts, fill=((123, 224, 123, 255) if on else (40, 44, 48, 220)), outline=(6, 16, 8, 255))
    for p in pips:
        aa = a1 - (a1 - a0) * p
        x0, y0 = K.pol(ctx.cx, ctx.cy, (R["hp_out"] + 8) * S, aa)
        sz = 8 * S
        d.polygon([(x0, y0 - sz), (x0 + sz, y0), (x0, y0 + sz), (x0 - sz, y0)], fill=accent + (255,), outline=K.INK + (255,))
    return im


# ------------------------------------------------------------------ compositor
def compose(D, ctx, slots, layers_on=None, return_layers=False):
    """Build the wheel. D = Direction. ctx.state keys used:
       rot, blur (deg of motion blur), par (dx,dy master parallax), act_slot, act, landed (slot index, after landing),
       forecast (slot index or None), gesture (-1..1), tier ('PERFECT'|'GOOD'|'WEAK'|None), values_only, reduce,
       dmg (0..1 crack amount), flash (0..1), hide (set of layer names)."""
    S = ctx.S
    st = ctx.state
    rot = ctx.rot
    hide = set(st.get("hide", ()))
    on = (lambda n: n not in hide) if layers_on is None else (lambda n: n in layers_on)
    par = st.get("par", (0.0, 0.0))
    out = K.rgba(ctx.size)
    L_ = {}

    def shift(im, k):
        if par == (0.0, 0.0) or k == 0:
            return im
        return ImageChops.offset(im, int(round(par[0] * k * S)), int(round(par[1] * k * S)))

    disc = K.ring_mask(ctx.size, ctx.cx, ctx.cy, 0, R["bezel_in"] * S)
    if on("back_plate"):
        bp = D.back_plate(ctx)
        L_["back_plate"] = shift(bp, 1.0)
        out.alpha_composite(L_["back_plate"])
    # ---- rotating group
    G = K.rgba(ctx.size)
    if on("art_ring_under"):
        u = D.art_ring_under(ctx)
        u = K.rot_c(u, rot * 0.97 + (st.get("under_lag", 0.0)))
        L_["art_ring_under"] = shift(u, 0.5)
        G.alpha_composite(L_["art_ring_under"])
    scenes = K.rgba(ctx.size)
    blanks = K.rgba(ctx.size)
    box = scene_box(ctx)
    for i, slot in enumerate(slots):
        wm = wedge_mask(ctx, i, rot)
        cxs, cys = slice_centre(ctx, i, rot)
        if slot["type"] == "NULL":
            if on("blank_window"):
                bw = D.blank_window(ctx, i, rot, wm, L_.get("back_plate"), L_.get("art_ring_under"))
                blanks.alpha_composite(bw)
            continue
        if not on("slice_scenes"):
            continue
        act = st.get("act", 0.0) if st.get("act_slot") == i else 0.0
        sp = D.scene(slot, ctx, act, i)
        lay = K.rgba(ctx.size)
        lay.alpha_composite(sp, (int(cxs - sp.width / 2), int(cys - sp.height / 2)))
        lay = K.masked(lay, wm)
        lay.alpha_composite(D.slice_glass(ctx, i, rot, wm, slot))
        scenes.alpha_composite(lay)
    L_["slice_scenes"] = scenes
    L_["blank_window"] = blanks
    G.alpha_composite(scenes)
    G.alpha_composite(blanks)
    # dim others / lift landed (D4 active-slice rule), forecast glow
    landed = st.get("landed")
    if landed is not None:
        dimm = K.L(ctx.size)
        for i in range(len(slots)):
            if i != landed:
                dimm = ImageChops.lighter(dimm, wedge_mask(ctx, i, rot))
        G = Image.composite(K.tone(G, 0.75, 0.62), G, dimm)
    # separators (a Direction can replace them: chalk lines, tentacles...)
    sep = K.rgba(ctx.size)
    if getattr(D, "separators", None) is not None:
        sep = D.separators(ctx, slots)
        G.alpha_composite(sep)
        sep = K.rgba(ctx.size)
    sd = ImageDraw.Draw(sep)
    for i in (range(len(slots)) if getattr(D, "separators", None) is None else []):
        a = slot_angle(i, rot) + SLOT_DEG / 2
        sd.line([ctx.P(R["sl_in"], a), ctx.P(R["sl_out"], a)], fill=(8, 6, 10, 255), width=max(1, int(7 * S)))
        sd.line([ctx.P(R["sl_in"] + 4, a - 0.25), ctx.P(R["sl_out"] - 2, a - 0.25)], fill=D.mat["accent"] + (110,), width=max(1, int(1.3 * S)))
    G.alpha_composite(sep)
    # plaque zone: desaturate + darken art under every plaque (readability)
    if on("plaque_zone"):
        zm = K.L(ctx.size)
        zd = ImageDraw.Draw(zm)
        for i in range(len(slots)):
            x, y = plaque_centre(ctx, i, rot)
            zd.ellipse([x - 80 * S, y - 42 * S, x + 80 * S, y + 42 * S], fill=255)
        zm = K.mask_mul(K.blur(zm, 16 * S), disc)
        za = np.asarray(zm, np.float32) / 255
        G = K.tone_map(G, 1 - 0.5 * za, 1 - 0.4 * za)
    # rim band: type colour per slice
    if on("rim_band"):
        band = K.rgba(ctx.size)
        for i, slot in enumerate(slots):
            col = K.TYPE_COL[slot["type"]]
            bm = wedge_mask(ctx, i, rot, R["band_in"], R["sl_out"], gap=4.5)
            band.alpha_composite(K.solid(bm, col, 0.95 if slot["type"] != "NULL" else 0.7))
            hl = wedge_mask(ctx, i, rot, R["sl_out"] - 4, R["sl_out"], gap=4.5)
            band.alpha_composite(K.solid(hl, K.mix(col, (255, 255, 255), 0.5), 0.8))
        L_["rim_band"] = band
        G.alpha_composite(band)
    if st.get("forecast") is not None and landed is None:
        i = st["forecast"]
        col = K.TYPE_COL[slots[i]["type"]]
        wm = wedge_mask(ctx, i, rot, inset=2)
        edge = ImageChops.subtract(wm, K.shrink(wm, 5 * S))
        pulse = 0.55 + 0.25 * math.sin(ctx.t * 2 * math.pi / 1.6)
        G.alpha_composite(K.solid(K.blur(edge, 3 * S), col, pulse))
        G = K.add(G, K.solid(K.blur(wm, 30 * S), col, 0.10 * pulse), 1.0)
    if landed is not None:
        wm = wedge_mask(ctx, landed, rot, inset=1)
        edge = ImageChops.subtract(wm, K.shrink(wm, 3.5 * S))
        G.alpha_composite(K.solid(edge, (255, 236, 200), 1.0))
    if st.get("flash", 0) > 0 and landed is not None:
        wm = wedge_mask(ctx, landed, rot)
        fc = st.get("flash_col", (255, 255, 255))
        G = K.add(G, K.solid(wm, fc, 0.55 * st["flash"]), 1.0)
    # plaques ride in the group only while blurred (values need not read mid-spin)
    blur_deg = st.get("blur", 0.0)
    plq = K.rgba(ctx.size)
    if on("plaques"):
        for i, slot in enumerate(slots):
            pi = D.plaque(ctx, slot, i)
            x, y = plaque_centre(ctx, i, rot)
            sc = 1.0
            if landed == i and st.get("pop", 0) > 0:
                pi = pi.resize((int(pi.width * (1 + 0.12 * st["pop"])), int(pi.height * (1 + 0.12 * st["pop"]))), Image.LANCZOS)
            plq.alpha_composite(pi, (int(x - pi.width / 2), int(y - pi.height / 2)))
        L_["plaques"] = plq
    if blur_deg > 0.5:
        G.alpha_composite(plq)
        acc = np.zeros((ctx.C, ctx.C, 4), np.float32)
        n = max(3, min(26, int(blur_deg / 1.5) + 2))
        for k in range(n):
            dlt = blur_deg * (k / (n - 1) - 0.5)
            acc += np.asarray(K.rot_c(G, dlt, Image.BILINEAR), np.float32)
        G = Image.fromarray((acc / n).astype(np.uint8), "RGBA")
    out.alpha_composite(K.masked(G, K.ring_mask(ctx.size, ctx.cx, ctx.cy, 0, (R["bezel_in"] + 2) * S)))
    if getattr(D, "inner_ring", None) is not None and on("inner_ring"):
        L_["inner_ring"] = D.inner_ring(ctx, slots)
        out.alpha_composite(L_["inner_ring"])
    if on("bezel"):
        L_["bezel"] = D.bezel(ctx)
        out.alpha_composite(L_["bezel"])
    if on("threat_ring"):
        tr = D.threat_ring(ctx)
        if tr is not None:
            L_["threat_ring"] = tr
            out.alpha_composite(tr)
    if on("art_ring_over"):
        ov = D.art_ring_over(ctx)
        if ov is not None:
            L_["art_ring_over"] = shift(ov, -0.4)
            out.alpha_composite(L_["art_ring_over"])
    if on("hp_arc"):
        out.alpha_composite(hp_arc(ctx, ctx.hp, D.mat["accent"], span=getattr(D, "hp_span", (128, 232))))
    if blur_deg <= 0.5 and on("plaques"):
        out.alpha_composite(plq)
    if on("hub_portrait"):
        hb = D.hub(ctx)
        L_["hub_portrait"] = shift(hb, -0.2)
        out.alpha_composite(L_["hub_portrait"])
    if on("needle_rig"):
        nd = D.needle(ctx, slots)
        L_["needle_rig"] = nd
        out.alpha_composite(nd)
    if on("fx"):
        fx = D.fx(ctx, slots)
        if fx is not None:
            L_["fx"] = fx
            out.alpha_composite(fx)
    if return_layers:
        return out, L_
    return out


# ------------------------------------------------------------------ default pieces a Direction can reuse
def default_blank(D, ctx, i, rot, wm, back, under, tint=(70, 76, 90)):
    """The blank (NULL) window: dark glass onto the art below, art dimmed + desaturated, thin empty outline."""
    S = ctx.S
    lay = K.rgba(ctx.size)
    if back is not None:
        lay.alpha_composite(back)
    if under is not None:
        lay.alpha_composite(under)
    lay = K.tone(lay, 0.35, 0.42)
    lay = K.masked(lay, wm)
    # dark glass tint + inner shadow
    lay.alpha_composite(K.solid(wm, (8, 10, 16), 0.35))
    inner = ImageChops.subtract(wm, K.shrink(wm, 16 * S))
    lay.alpha_composite(K.solid(K.blur(inner, 10 * S), (0, 0, 0), 0.8))
    # reflection streak across the glass
    a = slot_angle(i, rot)
    st = K.L(ctx.size)
    sd = ImageDraw.Draw(st)
    p0 = ctx.P(R["sl_out"] - 30, a - 22)
    p1 = ctx.P(R["sl_in"] + 40, a + 4)
    sd.line([p0, p1], fill=255, width=max(1, int(14 * S)))
    lay.alpha_composite(K.solid(K.mask_mul(K.blur(st, 6 * S), wm), (200, 220, 255), 0.10))
    # thin empty outline, inset
    em = wedge_mask(ctx, i, rot, inset=12)
    edge = ImageChops.subtract(em, K.shrink(em, max(1, 2.2 * S)))
    lay.alpha_composite(K.solid(edge, tint, 0.95))
    return lay


def default_glass(ctx, i, rot, wm, depth_k=0.75):
    S = ctx.S
    lay = K.rgba(ctx.size)
    inner = ImageChops.subtract(wm, K.shrink(wm, 12 * S))
    lay.alpha_composite(K.solid(K.blur(inner, 8 * S), (0, 0, 0), depth_k))
    return lay
