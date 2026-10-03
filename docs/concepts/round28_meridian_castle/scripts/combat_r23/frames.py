"""Round 13: wheel FRAME details.

Four frame versions over the locked round-11 parts (C "Screens & Data" slices, V2 telemetry ring):
  d1  Blade & window      notched blade pointer carrying the live value; active slice lifted + outlined
  d2  Instrument readout  long gauge needle on a hub collar, hub CRT readout, 30-tick scale, slice brackets
  d3  Layered stack       machined bezel over a recessed slice disc, glass, cast shadows, physical
                          pointer with counterweight and a split-flap value counter
  d4  Lens & rail         d1 blade + lift, d3-lite bezel and shadows, and the telemetry ring turning
                          into the active slice's readout rail over the pointer

render(frame, spec, ss, lod, rot, tilt) -> (RGBA at ss, centre px at ss, meta)
All geometry is in master units (slice outer radius R_OUT = 360); the canvas is premultiplied float.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import slicelib as SL
from slicelib import R_OUT, R_IN, PROGRAMS, CORPS, render_slice, f_num, f_ui, f_mono, glyph_rgba, c01
import roster_wheel as RW
import combat_wheel as CWL
import screens10 as S10

S10.select(virus="OOZE", proxy="TURN")

CW, CH, CX, CY = 1240, 1420, 620, 780
INK = (10, 8, 16)
CREAM = (250, 240, 214)
THREAT = (255, 52, 64)
YEL = (255, 214, 64)
KIND = {"ATTACK": "ATK", "CRITICAL": "CRIT", "DEFEND": "DEF", "SHIELD": "SHIELD", "EVADE": "EVADE",
        "HEAL": "HEAL", "AFFLICT": "AFFLICT", "DEPLOY": "DEPLOY", "MISS": "MISS", "TBD": "-"}


def set_centre(dx=0.0, dy=0.0):
    RW.CW, RW.CH, RW.CX, RW.CY = CW, CH, CX + dx, CY + dy


set_centre()


def P(r, ang, ss):
    return RW.P(r, ang, ss)


def Q(r, v, ang, ss):
    """Point at radius r on the axis at angle ang, offset v laterally (clockwise positive)."""
    a = math.radians(ang)
    return ((RW.CX + r * math.sin(a) + v * math.cos(a)) * ss, (RW.CY - r * math.cos(a) + v * math.sin(a)) * ss)


# ================================================================== canvas helpers (premultiplied)
def new_canvas(ss):
    return np.zeros((CH * ss, CW * ss, 4), np.float32)


def over_arr(dst, src, x=0, y=0, k=1.0):
    x, y = int(round(x)), int(round(y))
    h, w = src.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(dst.shape[1], x + w), min(dst.shape[0], y + h)
    if x1 <= x0 or y1 <= y0:
        return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x]
    if k != 1.0:
        s = s * k
    d = dst[y0:y1, x0:x1]
    d[...] = s + d * (1 - s[..., 3:])


def premult(im):
    a = np.asarray(im, np.float32) / 255
    a[..., :3] *= a[..., 3:]
    return a


def over_pil(canvas, im, dx=0, dy=0):
    over_arr(canvas, premult(im), dx, dy)


def add_glow(canvas, g_img, ss, k=0.9, blur=7):
    small = g_img.resize((g_img.width // 4, g_img.height // 4), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(blur * ss / 4))
    g = np.asarray(small.resize(g_img.size, Image.BILINEAR), np.float32) / 255
    canvas[..., :3] += g[..., :3] * g[..., 3:] * k
    canvas[..., 3:] = np.maximum(canvas[..., 3:], np.clip(g[..., 3:] * k, 0, 1))


def layer(ss):
    im = Image.new("RGBA", (CW * ss, CH * ss), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def shadow_of(canvas, im, ss, dx, dy, blur=6, k=0.6):
    """Cast a soft black shadow of a PIL layer's alpha, offset (dx, dy) master units."""
    a = im.split()[3].resize((im.width // 4, im.height // 4), Image.BILINEAR)
    a = a.filter(ImageFilter.GaussianBlur(blur * ss / 4)).resize(im.size, Image.BILINEAR)
    sh = np.zeros((im.height, im.width, 4), np.float32)
    sh[..., 3] = np.asarray(a, np.float32) / 255 * k
    over_arr(canvas, sh, dx * ss, dy * ss)


def grids(ss, dx=0.0, dy=0.0):
    yy, xx = np.mgrid[0:CH * ss, 0:CW * ss].astype(np.float32)
    ddx = (xx + 0.5) / ss - (CX + dx)
    ddy = (yy + 0.5) / ss - (CY + dy)
    return ddx, ddy


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# ================================================================== slices (cached layers)
_SL_CACHE = {}


def slice_layer(spec, i, ss, lod, rot, boss):
    sl = spec["slots"][i]
    key = (spec.get("key"), i, ss, lod, round(rot, 3))
    if key in _SL_CACHE:
        return _SL_CACHE[key]
    a0 = -30.0 + 60 * i + rot
    angs = np.radians(np.linspace(a0, a0 + 60, 40))
    xs = [r * np.sin(a) for r in (R_IN, R_OUT) for a in angs]
    ys = [-r * np.cos(a) for r in (R_IN, R_OUT) for a in angs]
    m = 24
    x0, x1 = int((min(xs) - m) * ss), int((max(xs) + m) * ss)
    y0, y1 = int((min(ys) - m) * ss), int((max(ys) + m) * ss)
    cv = np.zeros((y1 - y0, x1 - x0, 4), np.float32)
    opts = dict(RW.LOD) if lod else {}
    opts["upright"] = True
    opts["defer_icons"] = True
    if boss:
        opts.update(boss=True, phase=1)
    val = sl["value"]
    if sl["program"] == "NULL" or (sl.get("special") and sl["special"] != "tariff"):
        val = None
    res = render_slice(cv, -x0, -y0, sl["program"], a0, 60, val, (0.3 + i * 0.137) % 1.0, spec["theme"], ss, opts,
                       seed=i + spec.get("seed", 1) * 7, glyph=RW.SPECIAL_GLYPH.get(sl.get("special")),
                       badge=sl.get("badge"), special=sl.get("special"))
    blk, bx, by = res
    L = dict(arr=cv, x0=x0, y0=y0, blk=premult(blk), bx=bx + x0, by=by + y0, a0=a0, mid=a0 + 30, prog=sl["program"],
             value=val)
    _SL_CACHE[key] = L
    return L


def scale_arr(arr, s):
    h, w = arr.shape[:2]
    W2, H2 = max(1, int(round(w * s))), max(1, int(round(h * s)))
    out = np.zeros((H2, W2, 4), np.float32)
    for c in range(4):
        out[..., c] = np.asarray(Image.fromarray(arr[..., c], "F").resize((W2, H2), Image.BICUBIC))
    return np.clip(out, 0, None)


def place_slice(canvas, L, ss, scale=1.0, shift=0.0, dim=1.0, off=(0.0, 0.0), what="both", blk_scale=1.0):
    """Composite a slice layer. scale is about the wheel centre, shift is radial (master units)."""
    m = math.radians(L["mid"])
    sx, sy = math.sin(m) * shift * ss, -math.cos(m) * shift * ss
    ox, oy = (CX + off[0]) * ss, (CY + off[1]) * ss
    if what in ("both", "screen"):
        arr = L["arr"] if scale == 1.0 else scale_arr(L["arr"], scale)
        if dim != 1.0:
            arr = arr.copy()
            arr[..., :3] *= dim
        over_arr(canvas, arr, ox + L["x0"] * scale + sx, oy + L["y0"] * scale + sy)
    if what in ("both", "icons"):
        b = L["blk"]
        k = scale * blk_scale
        if k != 1.0:
            b = scale_arr(b, k)
        bh, bw = L["blk"].shape[:2]
        cxb = (L["bx"] + bw / 2) * scale
        cyb = (L["by"] + bh / 2) * scale
        over_arr(canvas, b, ox + cxb - b.shape[1] / 2 + sx, oy + cyb - b.shape[0] / 2 + sy)


def wedge_pts(a0, a1, r0, r1, ss, n=30, scale=1.0, shift=0.0):
    m = math.radians((a0 + a1) / 2)
    sx, sy = math.sin(m) * shift * ss, -math.cos(m) * shift * ss
    pts = [P(r1 * scale, a0 + (a1 - a0) * k / n, ss) for k in range(n + 1)]
    pts += [P(r0 * scale, a1 - (a1 - a0) * k / n, ss) for k in range(n + 1)]
    cx, cy = RW.CX * ss, RW.CY * ss
    # P already includes the centre; rescale only the radial part (done via r*scale), then shift
    return [(x + sx, y + sy) for x, y in pts]


def active_index(spec, rot=0.0):
    ang = spec.get("pointers", [0])[0] * 12
    return int(((ang - rot + 30) % 360) // 60)


# ================================================================== machined ring (numpy shaded)
LIGHT = np.array([-0.45, -0.72, 0.53], np.float32)
LIGHT /= np.linalg.norm(LIGHT)
HALF = LIGHT + np.array([0, 0, 1], np.float32)
HALF /= np.linalg.norm(HALF)


def machined(canvas, ss, knots, base, acc, screen=None, seed=0, off=(0.0, 0.0), accent_r=(), gloss=1.0,
             brushed=0.05, alpha=1.0):
    """knots: [(r, h)] height profile across the ring (h in master units). screen: (r0, r1) dark glass channel."""
    rmin, rmax = knots[0][0], knots[-1][0]
    rr = np.linspace(rmin - 2, rmax + 2, 4096)
    hh = np.interp(rr, [k[0] for k in knots], [k[1] for k in knots])
    sig = 1.2 / (rr[1] - rr[0])
    kx = np.arange(-int(4 * sig), int(4 * sig) + 1)
    ker = np.exp(-(kx / sig) ** 2 / 2)
    ker /= ker.sum()
    hh = np.convolve(np.pad(hh, len(kx), mode="edge"), ker, mode="same")[len(kx):-len(kx)]
    dh = np.gradient(hh, rr)
    pad = int((rmax + 8) * ss)
    cxs, cys = (CX + off[0]) * ss, (CY + off[1]) * ss
    y0, y1 = max(0, int(cys) - pad), min(CH * ss, int(cys) + pad)
    x0, x1 = max(0, int(cxs) - pad), min(CW * ss, int(cxs) + pad)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx, dy = (xx + 0.5 - cxs) / ss, (yy + 0.5 - cys) / ss
    rho = np.hypot(dx, dy) + 1e-6
    th = np.degrees(np.arctan2(dx, -dy)) % 360
    ux, uy = dx / rho, dy / rho
    g = np.interp(rho, rr, dh)
    nx, ny, nz = -g * ux, -g * uy, np.ones_like(g)
    nl = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / nl, ny / nl, nz / nl
    diff = np.clip(nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2], 0, 1)
    spec = np.clip(nx * HALF[0] + ny * HALF[1] + nz * HALF[2], 0, 1) ** 48
    refl = np.exp(-((ny + 0.55) / 0.22) ** 2) * (nz < 0.995)  # studio strip on up-facing bevels
    rng = np.random.default_rng(seed)
    streak = np.interp(rho * 3.0, np.arange(4096), rng.random(4096).astype(np.float32))
    ang_var = 0.5 + 0.5 * np.sin(np.radians(th) * 3 + 1.3)
    b = np.array(base, np.float32)
    col = b[None, None] * (0.32 + 0.85 * diff)[..., None]
    col += (spec * 0.9 * gloss)[..., None]
    col += (refl * 0.35 * gloss)[..., None] * (0.4 + b[None, None])
    col += ((streak - 0.5) * brushed * (0.6 + ang_var))[..., None]
    if screen:
        s0, s1 = screen
        sm = (smooth(s0, s0 + 1.2, rho) * (1 - smooth(s1 - 1.2, s1, rho)))[..., None]
        glass = np.array([0.012, 0.016, 0.022], np.float32)[None, None] + \
            (np.exp(-((th - 315 + 180) % 360 - 180) ** 2 / 2400) * 0.05)[..., None]
        col = col * (1 - sm) + glass * sm
    a = c01(acc)
    for (r, w, k) in accent_r:
        gg = (np.exp(-((rho - r) / w) ** 2) * k)[..., None]
        col = col + gg * a[None, None]
    al = (np.clip(rho - rmin + 0.5, 0, 1) * np.clip(rmax - rho + 0.5, 0, 1))[..., None] * alpha
    region = canvas[y0:y1, x0:x1]
    region[..., :3] = np.clip(col, 0, 2) * al + region[..., :3] * (1 - al)
    region[..., 3:] = al + region[..., 3:] * (1 - al)


def disc_shadow(canvas, ss, r_in_mask, rmin_ring, off, k=0.6, soft=7.0, cut=None, centre_off=(0.0, 0.0),
                raised_disc=None):
    """Analytic cast shadow on the slice disc: from a ring starting at rmin_ring (bezel lip) and/or a
    raised disc of radius raised_disc (hub), light offset 'off' (master units)."""
    dx, dy = grids(ss, *centre_off)
    rho = np.hypot(dx, dy)
    rs = np.hypot(dx - off[0], dy - off[1])
    sh = np.zeros_like(rho)
    if rmin_ring is not None:
        sh = np.maximum(sh, smooth(rmin_ring - soft, rmin_ring + soft, rs))
        sh = np.maximum(sh, 0.45 * smooth(rmin_ring - 26, rmin_ring, rho))  # contact occlusion
    if raised_disc is not None:
        sh = np.maximum(sh, smooth(raised_disc + soft, raised_disc - soft, rs) * (rho > raised_disc - 1))
    sh *= (rho < r_in_mask)
    canvas[..., :3] *= (1 - k * sh)[..., None]


# ================================================================== pieces
def blade(ss, ang, acc, body, edge, value, prog, tip, sh, top, wsh, wtop, win, crown=False, notch_col=None,
          boss=False, scale=1.0):
    """Notched blade pointer with a value window. Returns (layer, glow layer)."""
    im, d = layer(ss)
    gl, gd = layer(ss)
    s = scale

    def q(r, v):
        return Q(r, v * s, ang, ss)
    pts = [q(tip, 0), q(sh, wsh), q(top - 12 * s, wtop), q(top, wtop - 12), q(top, 16), q(top - 16 * s, 0),
           q(top, -16), q(top, -wtop + 12), q(top - 12 * s, -wtop), q(sh, -wsh)]
    if crown:  # boss: horns on the blade's shoulders
        horn_r = [q(top - 30 * s, wtop - 2), q(top + 26 * s, wtop + 18), q(top - 4 * s, wtop - 18)]
        horn_l = [q(top - 30 * s, -wtop + 2), q(top + 26 * s, -wtop - 18), q(top - 4 * s, -wtop + 18)]
        for h in (horn_r, horn_l):
            gd.polygon(h, fill=acc + (200,))
            d.polygon(h, fill=edge + (255,), outline=INK + (255,), width=int(3 * ss))
    gd.polygon(pts, fill=acc + (230,))
    d.polygon(pts, fill=body + (255,), outline=INK + (255,), width=int(3.5 * ss))
    # bevel: the left half catches the key light
    hl = [q(tip + 10 * s, 0), q(sh, -wsh + 6), q(top - 14 * s, -wtop + 7), q(top - 6 * s, -wtop + 14), q(top - 6 * s, -2)]
    d.polygon(hl, fill=tuple(min(255, int(c * 1.08 + 10)) for c in body) + (255,))
    dk = [q(tip + 10 * s, 0), q(sh, wsh - 6), q(top - 14 * s, wtop - 7), q(top - 6 * s, wtop - 14), q(top - 6 * s, 2)]
    d.polygon(dk, fill=tuple(int(c * 0.82) for c in body) + (255,))
    # accent chevrons near the tip
    for k in range(2):
        r = sh - 14 * s - k * 13 * s
        w = (r - tip) / (sh - tip) * wsh * 0.62
        d.line([q(r + 8 * s, -w), q(r, 0), q(r + 8 * s, w)], fill=(notch_col or acc) + (255,), width=int(4 * ss * s))
    # value window
    w0, w1, ww = win
    wp = [q(w0, -ww), q(w0, ww), q(w1, ww), q(w1, -ww)]
    d.polygon([q(w0 - 4 * s, -ww - 5), q(w0 - 4 * s, ww + 5), q(w1 + 4 * s, ww + 5), q(w1 + 4 * s, -ww - 5)], fill=INK + (255,))
    d.polygon(wp, fill=(12, 12, 18, 255), outline=acc + (255,), width=int(2.4 * ss))
    gd.polygon(wp, fill=acc + (120,))
    for k in range(int(w0 * 1), int(w1), 3):  # scanlines inside the window
        d.line([q(k, -ww + 3), q(k, ww - 3)], fill=(255, 255, 255, 14), width=max(1, ss // 2))
    if value is not None:
        txt = str(value)
        hgt = (w1 - w0) * s
        f = f_num(int(hgt * 0.92 * ss))
        tw = f.getlength(txt)
        cx, cy = Q((w0 + w1) / 2, 0, ang, ss)
        pc = PROGRAMS[prog]["col"]
        gd.text((cx - tw / 2, cy - hgt * 0.56 * ss), txt, font=f, fill=pc + (255,))
        d.text((cx - tw / 2, cy - hgt * 0.56 * ss), txt, font=f, fill=(255, 255, 255, 255),
               stroke_width=int(1.5 * ss), stroke_fill=INK + (255,))
    else:
        g = glyph_rgba("NULL", int((w1 - w0) * 0.8 * s * ss), 2 * ss)
        cx, cy = Q((w0 + w1) / 2, 0, ang, ss)
        im.alpha_composite(g, (int(cx - g.width / 2), int(cy - g.height / 2)))
    # program colour pip strip on the window's lower edge
    pc = PROGRAMS[prog]["col"]
    d.polygon([q(w0 + 2 * s, -ww + 6), q(w0 + 2 * s, ww - 6), q(w0 + 7 * s, ww - 6), q(w0 + 7 * s, -ww + 6)], fill=pc + (255,))
    return im, gl


def outline_slice(d, gd, L, ss, scale, shift, col, w=4.5, glow_col=None):
    pts = wedge_pts(L["a0"] + 0.9, L["a0"] + 59.1, R_IN + 2, R_OUT - 1.5, ss, 40, scale, shift)
    gd.polygon(pts, outline=(glow_col or col) + (255,), width=int(16 * ss))
    d.polygon(pts, outline=INK + (255,), width=int((w + 4) * ss))
    d.polygon(pts, outline=col + (255,), width=int(w * ss))


def telemetry(img, d, gd, spec, R0, R1, ss, acc, emblem, lod=False, rail=None, badges=True):
    """V2 telemetry ring text (+ emblem badges). rail = (prog, value, half_angle): the arc over the pointer
    switches to the active slice's readout in its program colour (d4)."""
    ring_r = (R0 + R1) / 2 - 5
    for rr in (R0 + 4, R1 - 4):
        bb = [RW.CX * ss - rr * ss, RW.CY * ss - rr * ss, RW.CX * ss + rr * ss, RW.CY * ss + rr * ss]
        d.ellipse(bb, outline=tuple(int(v * 0.5) for v in acc) + (255,), width=max(1, ss))
    key = spec.get("key", "")
    a_s, a_e = 0, 360
    if rail:
        prog, value, half = rail
        a_s, a_e = half + 2, 360 - half - 2
    if not lod:
        f = f_mono(int(13 * ss))
        CWL.text_ring(img, CWL.READOUT.get(key, key.upper() + " // "), ring_r, a_s, a_e, ss, f,
                      tuple(int(v * 0.95) for v in acc), head=300)
    else:
        for i in range(120):
            a = i * 3
            if i % 7 in (0, 1) or (rail and (a < a_s or a > a_e)):
                continue
            d.line([P(ring_r + 2, a, ss), P(ring_r + 2, a + 1.6, ss)], fill=acc + (200,), width=int(4 * ss))
    if rail:
        prog, value, half = rail
        pc = PROGRAMS[prog]["col"]
        # tinted channel + brackets
        poly = RW.arc_poly(R0 + 5, R1 - 5, -half, half, ss, 40)
        gd.polygon(poly, fill=pc + (150,))
        d.polygon(poly, fill=tuple(int(v * 0.42) for v in pc) + (255,))
        for a in (-half, half):
            d.line([P(R0 + 2, a, ss), P(R1 - 2, a, ss)], fill=pc + (255,), width=int(3 * ss))
        kind = KIND[PROGRAMS[prog]["kind"]]
        txt = "%s %s // %s // PERFECT // " % (prog, value if value is not None else "", kind) if value is not None \
            else "%s // MISS // NO EFFECT // " % prog
        if not lod:
            f = f_mono(int(14 * ss))
            CWL.text_ring(img, txt * 3, ring_r, -half + 1, half - 1, ss, f, (255, 255, 255))
        else:
            for i in range(int(-half), int(half), 3):
                d.line([P(ring_r + 2, i, ss), P(ring_r + 2, i + 2, ss)], fill=(255, 255, 255, 255), width=int(6 * ss))
    if badges:
        ptr = [p * 12 for p in spec.get("pointers", [0])]
        for a in (0, 90, 180, 270):
            if any(abs(((a - p + 180) % 360) - 180) < 40 for p in ptr):
                continue
            x, y = P((R0 + R1) / 2, a, ss)
            CWL.emblem_badge(img, d, gd, x, y, 19 * ss, acc, emblem)


def banner(img, d, gd, ss, y_bottom, title, sub, acc, mount=False):
    """Boss nameplate. mount=True: the banner is the pointer's mount (d1/d4): a bracket notch underneath."""
    f = f_num(int(46 * ss))
    fs = f_ui(int(15 * ss), b"Bold SemiCondensed")
    tw = max(f.getlength(title), fs.getlength(sub)) + 70 * ss
    y1 = y_bottom * ss
    y0 = y1 - 86 * ss
    cx = RW.CX * ss
    x0, x1 = cx - tw / 2, cx + tw / 2
    poly = [(x0 - 20 * ss, y0), (x1 + 20 * ss, y0), (x1, y1), (cx + 60 * ss, y1), (cx + 46 * ss, y1 + 16 * ss),
            (cx - 46 * ss, y1 + 16 * ss), (cx - 60 * ss, y1), (x0, y1)] if mount else \
        [(x0 - 20 * ss, y0), (x1 + 20 * ss, y0), (x1, y1), (x0, y1)]
    gd.polygon(poly, fill=acc + (150,))
    d.polygon(poly, fill=(16, 13, 18, 255), outline=acc + (255,), width=int(3 * ss))
    # hazard chamfers at the ends
    for sx in (-1, 1):
        xe = cx + sx * (tw / 2 + 4 * ss)
        for k in range(4):
            yk = y0 + 12 * ss + k * 17 * ss
            d.polygon([(xe, yk), (xe + sx * 10 * ss, yk), (xe + sx * 4 * ss, yk + 10 * ss), (xe - sx * 6 * ss, yk + 10 * ss)],
                      fill=acc + (255,))
    d.line([(x0 + 14 * ss, y1 - 9 * ss), (x1 - 14 * ss, y1 - 9 * ss)], fill=acc + (255,), width=int(2 * ss))
    w = f.getlength(title)
    d.text((cx - w / 2, y0 + 6 * ss), title, font=f, fill=(255, 255, 255, 255), stroke_width=int(2 * ss), stroke_fill=INK + (255,))
    w = fs.getlength(sub)
    d.text((cx - w / 2, y0 + 57 * ss), sub, font=fs, fill=acc + (255,))
    return x0, x1


def armour(img, d, gd, ss, R0, R1, acc, emblem, base=(46, 36, 28), skip=()):
    """Boss: 12 bolted armour plates with hazard chamfers + crest lugs at 90/270."""
    for i in range(12):
        a0 = i * 30 + 1.2
        a1 = a0 + 27.6
        if any(abs(((((a0 + a1) / 2) - s + 180) % 360) - 180) < 16 for s in skip):
            continue
        poly = RW.arc_poly(R0, R1, a0, a1, ss, 16)
        d.polygon(poly, fill=base + (255,), outline=INK + (255,), width=int(2 * ss))
        d.polygon(RW.arc_poly(R1 - 7, R1, a0 + 0.6, a1 - 0.6, ss, 16), fill=tuple(min(255, int(c * 1.9)) for c in base) + (255,))
        for k in range(5):  # hazard chamfer
            aa = a0 + 3 + k * 5
            d.polygon([P(R0 + 2, aa, ss), P(R0 + 2, aa + 2.2, ss), P(R0 + 9, aa + 3.4, ss), P(R0 + 9, aa + 1.2, ss)],
                      fill=acc + (255,))
        for aa in (a0 + 2.4, a1 - 2.4):
            x, y = P((R0 + R1) / 2 + 2, aa, ss)
            r = 3.6 * ss
            d.ellipse([x - r, y - r, x + r, y + r], fill=(205, 200, 190, 255), outline=INK + (255,))
    for a in (90, 270):
        x, y = P(R1 + 6, a, ss)
        r = 40 * ss
        hexp = [(x + r * math.cos(math.radians(60 * j)), y + r * math.sin(math.radians(60 * j))) for j in range(6)]
        gd.polygon(hexp, fill=acc + (160,))
        d.polygon(hexp, fill=(30, 24, 20, 255), outline=acc + (255,), width=int(3 * ss))
        r2 = r * 0.78
        hexp2 = [(x + r2 * math.cos(math.radians(60 * j)), y + r2 * math.sin(math.radians(60 * j))) for j in range(6)]
        d.polygon(hexp2, outline=INK + (255,), width=int(2 * ss))
        g = RW.tinted_glyph(emblem, int(44 * ss), acc)
        img.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))


def threat_ring(d, gd, ss, R0, R1, acc, rot=0.0, telegraph=(120, 240), lod=False):
    """Boss: a second outer ring, counter-rotating, red chevrons + telegraphed next-pointer marks."""
    bb0 = [RW.CX * ss - R1 * ss, RW.CY * ss - R1 * ss, RW.CX * ss + R1 * ss, RW.CY * ss + R1 * ss]
    d.ellipse(bb0, outline=(30, 8, 12, 255), width=int((R1 - R0) * ss))
    d.ellipse(bb0, outline=INK + (255,), width=int(2 * ss))
    bb1 = [RW.CX * ss - R0 * ss, RW.CY * ss - R0 * ss, RW.CX * ss + R0 * ss, RW.CY * ss + R0 * ss]
    d.ellipse(bb1, outline=(120, 26, 34, 255), width=int(2 * ss))
    n = 24 if lod else 36
    rm = (R0 + R1) / 2
    hw = (R1 - R0) * 0.32
    for i in range(n):
        a = i * 360 / n - rot
        if any(abs(((a - t + 180) % 360) - 180) < 8 for t in telegraph):
            continue
        da = math.degrees(hw / rm) * 1.1
        pts = [P(rm - hw, a - da, ss), P(rm, a + da * 0.2, ss), P(rm + hw, a - da, ss), P(rm + hw, a - da * 0.4, ss),
               P(rm, a + da * 0.8, ss), P(rm - hw, a - da * 0.4, ss)]
        d.polygon(pts, fill=THREAT + (255,))
        gd.polygon(pts, fill=THREAT + (150,))
    for t in telegraph:  # hollow ghost-needle marks: where the next pointers will appear
        x, y = P(rm, t, ss)
        tip = P(R0 - 20, t, ss)
        bl, br = P(R1 + 2, t - 4.5, ss), P(R1 + 2, t + 4.5, ss)
        gd.polygon([tip, bl, br], fill=(255, 255, 255, 120))
        d.polygon([tip, bl, br], outline=(255, 255, 255, 255), width=int(3 * ss))
        if not lod:
            f = f_num(int(17 * ss))
            s = "NEXT"
            xx, yy = P(R1 + 22, t, ss)
            tw = f.getlength(s)
            d.text((xx - tw / 2, yy - 10 * ss), s, font=f, fill=(255, 255, 255, 255), stroke_width=int(2 * ss),
                   stroke_fill=INK + (255,))


def hub_readout(img, d, gd, ss, hub_r, acc, prog, value, aim=3, boss=False, emblem=None, lod=False, threat=False):
    """d2: the hub is a CRT readout of the slice under the needle (accessibility second read)."""
    cx, cy = RW.CX * ss, RW.CY * ss
    R = hub_r * ss
    d.ellipse([cx - R - 7 * ss, cy - R - 7 * ss, cx + R + 7 * ss, cy + R + 7 * ss], fill=(40, 40, 48, 255), outline=INK + (255,), width=int(2 * ss))
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(7, 12, 15, 255), outline=acc + (255,), width=int(2 * ss))
    pc = PROGRAMS[prog]["col"]
    gd.ellipse([cx - R * 0.7, cy - R * 0.7, cx + R * 0.7, cy + R * 0.7], fill=pc + (40,))
    if emblem and not lod:
        g = RW.tinted_glyph(emblem, int(hub_r * 1.4 * ss), acc)
        g.putalpha(g.split()[3].point(lambda v: int(v * 0.16)))
        img.alpha_composite(g, (int(cx - g.width / 2), int(cy - g.height / 2)))
        d, gd = ImageDraw.Draw(img), gd
    for k in range(-int(R), int(R), int(3 * ss)):
        hw = math.sqrt(max(0, R * R - k * k))
        d.line([(cx - hw, cy + k), (cx + hw, cy + k)], fill=(0, 0, 0, 70), width=max(1, ss // 2))
    if lod:
        txt = str(value) if value is not None else "-"
        f = f_num(int(hub_r * 1.25 * ss))
        tw = f.getlength(txt)
        gd.text((cx - tw / 2, cy - hub_r * 0.78 * ss), txt, font=f, fill=pc + (255,))
        d.text((cx - tw / 2, cy - hub_r * 0.78 * ss), txt, font=f, fill=(255, 255, 255, 255), stroke_width=int(3 * ss), stroke_fill=INK + (255,))
        return
    s = hub_r / 96

    def ctext(txt, font, ymid, x=None, fill=(255, 255, 255), stroke=0, glow=None):
        bb = font.getbbox(txt)
        xx = (cx - (bb[2] - bb[0]) / 2 - bb[0]) if x is None else x - bb[0]
        yy = ymid - (bb[1] + bb[3]) / 2
        if glow:
            gd.text((xx, yy), txt, font=font, fill=glow + (255,))
        ImageDraw.Draw(img).text((xx, yy), txt, font=font, fill=fill + (255,), stroke_width=stroke, stroke_fill=INK + (255,))
        return bb[2] - bb[0]
    f1 = f_num(int(24 * s * ss))
    ctext(prog, f1, cy - 50 * s * ss, fill=pc, glow=pc)
    f2 = f_num(int(58 * s * ss))
    t2 = str(value) if value is not None else "--"
    g = glyph_rgba(prog, int(38 * s * ss), 2.5 * ss)
    bb = f2.getbbox(t2)
    w2 = bb[2] - bb[0]
    tot = g.width + 6 * ss + w2
    x = cx - tot / 2
    ym = cy - 6 * s * ss
    img.alpha_composite(g, (int(x), int(ym - g.height / 2)))
    ctext(t2, f2, ym, x=x + g.width + 6 * ss, stroke=int(2 * ss), glow=pc)
    d = ImageDraw.Draw(img)
    f3 = f_mono(int(14 * s * ss))
    kind = KIND[PROGRAMS[prog]["kind"]]
    t3 = ("%s > YOU" % kind) if threat else kind
    tw = f3.getlength(t3)
    py = cy + 34 * s * ss
    pw = tw + 3 * 15 * s * ss + 8 * ss
    x0 = cx - pw / 2
    d.text((x0, py), t3, font=f3, fill=(THREAT if threat else (210, 215, 225)) + (255,))
    for k in range(3):
        xx = x0 + tw + 8 * ss + k * 15 * s * ss
        r = 5 * s * ss
        d.ellipse([xx, py + 3 * ss, xx + 2 * r, py + 3 * ss + 2 * r], fill=(YEL if k < aim else (60, 60, 70)) + (255,))
    return d


# ================================================================== render
def theme_of(spec):
    if spec["theme"] == "player":
        st = RW.CLASS_STYLE[spec["cls"]]
        return st["acc"], st["emblem"], st
    return CORPS[spec["theme"]]["col"], RW.CORP_EMBLEM[spec["theme"]], None


def render(frame, spec, ss=2, lod=False, rot=0.0, tilt=0.0, hp_number=False, extras=True, banner_on=True):
    boss = spec.get("boss") if extras else None
    is_boss = bool(spec.get("boss"))
    acc, emblem, st = theme_of(spec)
    canvas = new_canvas(ss)
    ai = active_index(spec, rot)
    ptr_ang = spec.get("pointers", [0])[0] * 12
    Ls = [slice_layer(spec, i, ss, lod, rot, is_boss) for i in range(6)]
    La = Ls[ai]
    hub_r = 96 if spec.get("ring") else 126
    meta = {}
    fn = {"d1": _d1, "d2": _d2, "d3": _d3, "d4": _d4}[frame]
    fn(canvas, spec, ss, lod, rot, tilt, Ls, La, ai, acc, emblem, st, boss, hub_r, ptr_ang, meta, hp_number, banner_on)
    set_centre()
    rgb = np.clip(canvas[..., :3], 0, 1)
    a = np.clip(canvas[..., 3:], 0, 1)
    straight = np.where(a > 1e-4, rgb / np.maximum(a, 1e-4), 0)
    im = Image.fromarray((np.clip(np.concatenate([straight, a], 2), 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")
    bb = im.split()[3].point(lambda v: 255 if v > 3 else 0).getbbox()
    im = im.crop(bb)
    centre = (CX * ss - bb[0], CY * ss - bb[1])
    return im, centre, meta


def _hp(d, gd, ss, R, spec, boss, hp_number):
    hp = spec.get("hp")
    if hp:
        CWL.draw_hp(d, gd, ss, R, hp[0], hp[1], pred=spec.get("pred", 0), phases=boss.get("pips") if boss else None,
                    active_phase=boss.get("phase", 1) if boss else 1, number=hp_number)


def _hub_std(img, d, gd, spec, ss, hub_r, acc, st, lod, hp_in_hub=False):
    if spec.get("ring"):
        RW.draw_inner_ring(img, d, gd, spec["ring"], ss, acc, st)
    hub = spec["hub"]
    if hp_in_hub and spec.get("hp"):
        RW.draw_hub(img, d, gd, ss, hub_r, acc, None, "", "")
        hp = spec["hp"]
        f = f_num(int(hub_r * 0.95 * ss))
        s = "%d" % hp[0]
        tw = f.getlength(s)
        cx, cy = RW.CX * ss, RW.CY * ss
        d.text((cx - tw / 2, cy - hub_r * 0.62 * ss), s, font=f, fill=RW.HP_GREEN + (255,), stroke_width=int(3 * ss), stroke_fill=INK + (255,))
    elif lod:
        RW.draw_hub(img, d, gd, ss, hub_r, acc, hub.get("emblem"), "", "")
    else:
        RW.draw_hub(img, d, gd, ss, hub_r, acc, hub.get("emblem"), hub["name"], hub.get("sub", ""))


# ------------------------------------------------------------------ D1 blade & window
def _d1(canvas, spec, ss, lod, rot, tilt, Ls, La, ai, acc, emblem, st, boss, hub_r, ptr_ang, meta, hp_number, banner_on):
    Rt = R_OUT + 40
    R1 = Rt + (30 if boss else 0)
    RW.ring_base(canvas, ss, R_OUT + 1, Rt, (0.025, 0.03, 0.04), acc, rim=1.4)
    for L in Ls:
        if L is not La:
            place_slice(canvas, L, ss, dim=0.66)
    im, d = layer(ss)
    gl, gd = layer(ss)
    telemetry(im, d, gd, spec, R_OUT + 1, Rt, ss, acc, emblem, lod)
    if boss:
        armour(im, d, gd, ss, Rt, R1, acc, emblem, skip=(ptr_ang,))
    _hub_std(im, d, gd, spec, ss, hub_r, acc, st, lod)
    _hp(d, gd, ss, R1, spec, boss, hp_number)
    add_glow(canvas, gl, ss)
    over_pil(canvas, im)
    # lifted active slice: shadow, slice, outline
    s_l, sh_l = 1.065, 4.0
    tmp = new_canvas(ss)
    place_slice(tmp, La, ss, scale=s_l, shift=sh_l)
    sa = tmp[..., 3]
    small = Image.fromarray((sa * 255).astype(np.uint8)).resize((CW * ss // 4, CH * ss // 4), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(4 * ss)).resize((CW * ss, CH * ss), Image.BILINEAR)
    shd = np.zeros_like(tmp)
    shd[..., 3] = np.asarray(small, np.float32) / 255 * 0.8
    over_arr(canvas, shd, 6 * ss, 12 * ss)
    over_arr(canvas, tmp)
    del tmp
    im2, d2 = layer(ss)
    gl2, gd2 = layer(ss)
    outline_slice(d2, gd2, La, ss, s_l, sh_l, CREAM, w=4.5, glow_col=PROGRAMS[La["prog"]]["col"])
    add_glow(canvas, gl2, ss, 0.8, blur=9)
    over_pil(canvas, im2)
    # blade pointer
    ps = 1.55 if lod else 1.0
    tip = R_OUT - 26
    top = R1 + 118 * ps
    body = CREAM if not boss else (255, 150, 40)
    edge = (230, 220, 200) if not boss else (60, 40, 30)
    bl, bg = blade(ss, ptr_ang, acc, body, edge, La["value"], La["prog"], tip=tip, sh=R1 + 30 * ps, top=top,
                   wsh=38 * ps, wtop=56 * ps, win=(R1 + 42 * ps, top - 20 * ps, 40 * ps), crown=bool(boss),
                   notch_col=acc if not boss else INK)
    shadow_of(canvas, bl, ss, 7, 12, 5, 0.65)
    add_glow(canvas, bg, ss, 0.9)
    over_pil(canvas, bl)
    meta.update(ptr_r=(R1 + 44 * ps + top - 22 * ps) / 2, hp_r=R1 + 36, top_r=top)
    if boss and banner_on and not lod:
        im3, d3 = layer(ss)
        gl3, gd3 = layer(ss)
        y_b = RW.CY - top + 4
        x0, x1 = banner(im3, d3, gd3, ss, y_b, boss["title"], boss["sub"], acc, mount=True)
        # struts from the banner down to the armour
        for sx in (-1, 1):
            p0 = (RW.CX * ss + sx * 150 * ss, y_b * ss)
            p1 = P(R1 - 4, sx * 34, ss)
            d3.line([p0, p1], fill=INK + (255,), width=int(14 * ss))
            d3.line([p0, p1], fill=(120, 112, 104, 255), width=int(8 * ss))
            d3.line([p0, p1], fill=acc + (255,), width=int(2 * ss))
            for p in (p0, p1):
                d3.ellipse([p[0] - 8 * ss, p[1] - 8 * ss, p[0] + 8 * ss, p[1] + 8 * ss], fill=(70, 66, 62, 255), outline=INK + (255,), width=int(2 * ss))
        # threat tab on the blade
        f = f_num(int(19 * ss))
        s = "HITS YOU"
        tw = f.getlength(s)
        tx, ty = Q(R1 + 60, 46 + 4, ptr_ang, ss)
        d3.polygon([(tx, ty - 14 * ss), (tx + tw + 22 * ss, ty - 14 * ss), (tx + tw + 30 * ss, ty), (tx + tw + 22 * ss, ty + 14 * ss), (tx, ty + 14 * ss), (tx - 10 * ss, ty)],
                   fill=THREAT + (255,), outline=INK + (255,), width=int(2 * ss))
        d3.text((tx + 8 * ss, ty - 12 * ss), s, font=f, fill=(255, 255, 255, 255))
        shadow_of(canvas, im3, ss, 6, 10, 6, 0.6)
        add_glow(canvas, gl3, ss)
        over_pil(canvas, im3)


# ------------------------------------------------------------------ D2 instrument readout
def _d2(canvas, spec, ss, lod, rot, tilt, Ls, La, ai, acc, emblem, st, boss, hub_r, ptr_ang, meta, hp_number, banner_on):
    Rt = R_OUT + 40
    Rs = Rt + 24  # tick scale band
    R1 = Rs + (30 if boss else 0)
    RW.ring_base(canvas, ss, R_OUT + 1, Rt, (0.025, 0.03, 0.04), acc, rim=1.4)
    RW.ring_base(canvas, ss, Rt, Rs, (0.16, 0.16, 0.18), acc, rim=0.9)
    for L in Ls:
        place_slice(canvas, L, ss, what="screen", dim=1.0 if L is La else 0.8)
    im, d = layer(ss)
    gl, gd = layer(ss)
    # active slice: instrument brackets + lit hairline
    pc = PROGRAMS[La["prog"]]["col"]
    pts = wedge_pts(La["a0"] + 0.9, La["a0"] + 59.1, R_IN + 2, R_OUT - 1.5, ss, 40)
    gd.polygon(pts, outline=pc + (255,), width=int(12 * ss))
    d.polygon(pts, outline=pc + (255,), width=int(2.5 * ss))
    a0, a1 = La["a0"], La["a0"] + 60
    for (r, a, sr, sa) in ((R_OUT - 10, a0 + 3.5, -1, 1), (R_OUT - 10, a1 - 3.5, -1, -1), (R_IN + 12, a0 + 8, 1, 1), (R_IN + 12, a1 - 8, 1, -1)):
        L1 = 26
        p = P(r, a, ss)
        pr = P(r + sr * L1, a, ss)
        pa = P(r, a + sa * math.degrees(L1 / r), ss)
        for w, c in ((9, INK), (4.5, (255, 255, 255))):
            d.line([pr, p, pa], fill=c + (255,), width=int(w * ss), joint="curve")
    add_glow(canvas, gl, ss, 0.7)
    over_pil(canvas, im)
    # needle passes UNDER the glyph/value blocks (they sit on the glass)
    im, d = layer(ss)
    gl, gd = layer(ss)
    collar = hub_r + 6
    tip_r = Rs - 2
    a = ptr_ang
    ns = 1.7 if lod else 1.0
    root_w, tip_w = 11 * ns, 4.0 * ns
    # bold root (hub -> slice inner edge), a hairline across the slice glass, bold tip over rim + tick scale
    root = [Q(collar, -root_w, a, ss), Q(R_IN + 6, -root_w * 0.7, a, ss), Q(R_IN + 6, root_w * 0.7, a, ss), Q(collar, root_w, a, ss)]
    tipp = [Q(R_OUT - 14, -root_w * 0.8, a, ss), Q(tip_r - 34, -tip_w, a, ss), Q(tip_r, 0, a, ss), Q(tip_r - 34, tip_w, a, ss),
            Q(R_OUT - 14, root_w * 0.8, a, ss)]
    for pts in (root, tipp):
        gd.polygon(pts, fill=acc + (200,))
        d.polygon(pts, fill=(245, 245, 250, 255), outline=INK + (255,), width=int(2.4 * ss))
    d.line([Q(R_IN + 6, 0, a, ss), Q(R_OUT - 8, 0, a, ss)], fill=(255, 255, 255, 215), width=max(1, int(3.0 * ss * ns)))
    d.polygon([Q(tip_r - 40, -tip_w - 1.4, a, ss), Q(tip_r, 0, a, ss), Q(tip_r - 40, tip_w + 1.4, a, ss)], fill=YEL + (255,), outline=INK + (255,), width=int(1.5 * ss))
    shadow_of(canvas, im, ss, 5, 9, 4, 0.6)
    add_glow(canvas, gl, ss, 0.6)
    over_pil(canvas, im)
    for L in Ls:
        place_slice(canvas, L, ss, what="icons")
    im, d = layer(ss)
    gl, gd = layer(ss)
    telemetry(im, d, gd, spec, R_OUT + 1, Rt, ss, acc, emblem, lod)
    # 30-tick scale (rotates with the wheel); numerals at slice centres
    fnum = f_num(int(17 * ss))
    for i in range(30):
        ang = i * 12 + rot
        major = i % 5 == 0
        r0 = Rt + 2
        r1 = Rt + (14 if major else 8)
        d.line([P(r0, ang, ss), P(r1, ang, ss)], fill=(235, 235, 240, 255), width=int((3 if major else 1.6) * ss))
        if major and not lod and abs(((ang - ptr_ang + 180) % 360) - 180) > 8:
            s = str(i)
            x, y = P(Rt + 19, ang + 5.5, ss)
            tw = fnum.getlength(s)
            d.text((x - tw / 2, y - 10 * ss), s, font=fnum, fill=(225, 225, 235, 255))
    if boss:
        threat_ring(d, gd, ss, Rs + 1, R1, acc, rot=rot * -1.7 + 7, telegraph=(120, 240), lod=lod)
    # hub collar + counterweight
    cx, cy = RW.CX * ss, RW.CY * ss
    ring = bool(spec.get("ring"))
    if ring:
        RW.draw_inner_ring(im, d, gd, spec["ring"], ss, acc, st)
        # inner ring: the needle marks the live segment too
        d.line([Q(hub_r + 4, 0, a, ss), Q(hub_r + 34, 0, a, ss)], fill=INK + (255,), width=int(8 * ss))
        d.line([Q(hub_r + 4, 0, a, ss), Q(hub_r + 34, 0, a, ss)], fill=(245, 245, 250, 255), width=int(4 * ss))
    cr = hub_r + (2 if ring else 10)
    rc = cr * ss
    d.ellipse([cx - rc, cy - rc, cx + rc, cy + rc], fill=(54, 54, 62, 255), outline=INK + (255,), width=int(2 * ss))
    hub_readout(im, d, gd, ss, hub_r - (6 if spec.get("ring") else 4), acc, La["prog"], La["value"], aim=3 if not boss else 3,
                boss=bool(boss), emblem=emblem if boss else None, lod=lod, threat=bool(boss))
    d = ImageDraw.Draw(im)
    # needle root stub on the collar + counterweight opposite
    d.polygon([Q(cr - 6, -root_w, a, ss), Q(cr + 8, -root_w, a, ss), Q(cr + 8, root_w, a, ss), Q(cr - 6, root_w, a, ss)],
              fill=(245, 245, 250, 255), outline=INK + (255,), width=int(2 * ss))
    cwx, cwy = Q(cr, 0, a + 180, ss)
    r = 15 * ss * ns
    d.ellipse([cwx - r, cwy - r, cwx + r, cwy + r], fill=(90, 90, 100, 255), outline=INK + (255,), width=int(2 * ss))
    d.ellipse([cwx - r * 0.5, cwy - r * 0.6, cwx - r * 0.05, cwy - r * 0.15], fill=(200, 200, 210, 255))
    _hp(d, gd, ss, R1, spec, boss, hp_number)
    if boss and banner_on and not lod:
        RW.draw_banner(im, d, gd, ss, R1, boss["title"], boss["sub"], acc)
    add_glow(canvas, gl, ss)
    over_pil(canvas, im)
    if boss:  # ambient: radar sweep across the face
        dx, dy = grids(ss)
        rho = np.hypot(dx, dy)
        th = np.degrees(np.arctan2(dx, -dy)) % 360
        lead = 305.0 + rot * 3
        lag = (lead - th) % 360
        sw = np.exp(-lag / 26.0) * (lag < 120) * (rho < R_OUT) * (rho > hub_r + 10)
        edge = np.exp(-(np.minimum(lag, 360 - lag) / 1.2) ** 2) * (rho < R_OUT) * (rho > hub_r + 10)
        a_ = c01(acc)
        canvas[..., :3] += (sw * 0.22 + edge * 0.6)[..., None] * a_[None, None]
    meta.update(ptr_r=Rs - 10, hp_r=R1 + 36, top_r=R1)


# ------------------------------------------------------------------ D3 layered stack
def _d3_bezel_knots(R_lip, Rch0, Rch1, R1):
    return [(R_lip, 0.0), (R_lip + 4, 7.0), (R_lip + 10, 9.0), (Rch0 - 4, 8.0), (Rch0, 3.0), (Rch1, 3.0),
            (Rch1 + 4, 9.0), (R1 - 8, 11.0), (R1 - 2, 6.0), (R1, 0.0)]


def _d3(canvas, spec, ss, lod, rot, tilt, Ls, La, ai, acc, emblem, st, boss, hub_r, ptr_ang, meta, hp_number, banner_on):
    # layer depths (parallax: offset = tilt * depth, master units)
    t = tilt
    D_DISC, D_BEZ, D_HUB, D_PTR, D_GLASS = -6, 0, 5, 10, -14
    R_lip = R_OUT - 8
    Rch0, Rch1 = R_OUT + 14, R_OUT + 46
    R1 = R_OUT + 66
    RA = R1 + (34 if boss else 0)
    is_player = spec["theme"] == "player"
    base = (0.34, 0.33, 0.37) if is_player else (0.52, 0.30, 0.12)
    # back plate + disc
    dx, dy = grids(ss, t * D_DISC, 0)
    rho = np.hypot(dx, dy)
    bp = np.clip(R_OUT + 4 - rho, 0, 1)
    canvas[..., :3] = canvas[..., :3] * (1 - bp[..., None]) + np.array([0.02, 0.018, 0.03]) * bp[..., None]
    canvas[..., 3] = np.maximum(canvas[..., 3], bp)
    del dx, dy, rho, bp
    for L in Ls:
        lit = L is La
        place_slice(canvas, L, ss, dim=1.08 if lit else 0.7, off=(t * D_DISC, 0))
    # spotlight from the pointer lamp onto the active slice
    dx, dy = grids(ss, t * D_DISC, 0)
    rho = np.hypot(dx, dy)
    th = np.degrees(np.arctan2(dx, -dy)) % 360
    da = np.abs(((th - (La["mid"]) + 180) % 360) - 180)
    cone = np.exp(-(da / 26) ** 4) * smooth(R_IN, R_IN + 60, rho) * (rho < R_OUT) * (0.55 + 0.45 * rho / R_OUT)
    pc = c01(PROGRAMS[La["prog"]]["col"])
    canvas[..., :3] += cone[..., None] * (np.array([0.10, 0.09, 0.07]) + pc * 0.06)[None, None]
    del dx, dy, rho, th, da, cone
    # bezel + hub cast shadows onto the recessed disc
    sh_off = (7 + t * (D_BEZ - D_DISC), 12)
    disc_shadow(canvas, ss, R_lip + 0.5, R_lip, sh_off, k=0.62, soft=7, centre_off=(t * D_DISC, 0))
    hub_off = (8 + t * (D_HUB - D_DISC), 13)
    disc_shadow(canvas, ss, R_OUT, None, hub_off, k=0.55, soft=8, centre_off=(t * D_DISC, 0),
                raised_disc=(127 if spec.get("ring") else hub_r + 8))
    # glass (sheen moves against the tilt)
    dx, dy = grids(ss, t * D_GLASS, 0)
    rho = np.hypot(dx, dy)
    dxx, dyy = grids(ss, 0, 0)
    inside = np.hypot(dxx, dyy) < R_lip
    th = np.degrees(np.arctan2(dx, -dy)) % 360
    crescent = np.exp(-((rho / R_lip - 0.86) / 0.07) ** 2) * np.clip(np.cos(np.radians(th - 315)), 0, 1) ** 2 * 0.16
    band = np.exp(-(((dx + dy) / 1.414 + 150) / 40) ** 2) * 0.05 + np.exp(-(((dx + dy) / 1.414 + 60) / 9) ** 2) * 0.05
    spark = np.exp(-((rho - (R_lip - 10)) / 2.2) ** 2) * np.clip(np.cos(np.radians(th - 312)), 0, 1) ** 8 * 0.45
    gl_ = (crescent + band + spark) * inside
    canvas[..., :3] += gl_[..., None]
    del dx, dy, rho, dxx, dyy, th, crescent, band, spark, gl_, inside
    # machined bezel (above the disc)
    set_centre(t * D_BEZ, 0)
    knots = _d3_bezel_knots(R_lip, Rch0, Rch1, R1)
    machined(canvas, ss, knots, base, acc, screen=(Rch0, Rch1), seed=13, off=(t * D_BEZ, 0),
             accent_r=((Rch0 + 0.5, 0.9, 0.9), (Rch1 - 0.5, 0.9, 0.9), (R1 - 0.8, 1.0, 0.7)), brushed=0.06)
    if boss:  # heavier armour collar outside the bezel
        kn = [(R1, 0.0), (R1 + 3, 12.0), (RA - 10, 14.0), (RA - 3, 9.0), (RA, 0.0)]
        machined(canvas, ss, kn, (0.30, 0.20, 0.12), acc, seed=29, off=(t * D_BEZ, 0), accent_r=((RA - 1, 1.0, 1.0),),
                 brushed=0.08, gloss=0.7)
    im, d = layer(ss)
    gl, gd = layer(ss)
    telemetry(im, d, gd, spec, Rch0 - 2, Rch1 + 2, ss, acc, emblem, lod)
    # screws on the outer bead
    for i in range(12):
        a = i * 30 + 15
        if abs(((a - ptr_ang + 180) % 360) - 180) < 20:
            continue
        x, y = P(R1 - 9, a, ss)
        r = 4.2 * ss
        d.ellipse([x - r, y - r, x + r, y + r], fill=(70, 68, 74, 255), outline=INK + (255,), width=max(1, ss))
        d.line([(x - r * 0.7, y + r * 0.2), (x + r * 0.7, y - r * 0.2)], fill=INK + (255,), width=max(1, ss))
    if boss:
        threat = []
        for i in range(24):  # rivets on the armour collar
            x, y = P((R1 + RA) / 2, i * 15 + 7.5, ss)
            r = 3.4 * ss
            d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 205, 180, 255), outline=INK + (255,), width=max(1, ss))
        # crest plates (embossed corp emblem) at 90 / 270
        for a in (90, 270):
            x, y = P(RA - 4, a, ss)
            r = 46 * ss
            gd.ellipse([x - r, y - r, x + r, y + r], fill=acc + (120,))
            d.ellipse([x - r, y - r, x + r, y + r], fill=(66, 44, 26, 255), outline=INK + (255,), width=int(3 * ss))
            d.ellipse([x - r * 0.84, y - r * 0.84, x + r * 0.84, y + r * 0.84], outline=acc + (255,), width=int(2 * ss))
            g = RW.tinted_glyph(emblem, int(56 * ss), acc)
            im.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))
    add_glow(canvas, gl, ss, 0.8)
    over_pil(canvas, im)
    # hub layer (raised cap with a machined rim)
    set_centre(t * D_HUB, 0)
    hr = 127 if spec.get("ring") else hub_r
    machined(canvas, ss, [(hr - 2, 0.0), (hr, 6.0), (hr + 6, 8.0), (hr + 10, 0.0)], base, acc, seed=5,
             off=(t * D_HUB, 0), accent_r=((hr + 9, 0.8, 0.6),))
    im, d = layer(ss)
    gl, gd = layer(ss)
    _hub_std(im, d, gd, spec, ss, hub_r, acc, st, lod)
    # glass dome over the hub too: a small specular
    x, y = P(hub_r * 0.62, 315, ss)
    gd.ellipse([x - 20 * ss, y - 10 * ss, x + 20 * ss, y + 10 * ss], fill=(255, 255, 255, 60))
    add_glow(canvas, gl, ss, 0.8)
    over_pil(canvas, im)
    # HP arc on the bezel layer
    set_centre(t * D_BEZ, 0)
    im, d = layer(ss)
    gl, gd = layer(ss)
    _hp(d, gd, ss, RA, spec, boss, hp_number)
    if boss and banner_on and not lod:
        RW.draw_banner(im, d, gd, ss, RA + 70, boss["title"], boss["sub"], acc)
    add_glow(canvas, gl, ss, 0.9)
    over_pil(canvas, im)
    # physical pointer: pivot housing with split-flap counter, metal arm, counterweight
    set_centre(t * D_PTR, 0)
    ps = 1.5 if lod else 1.0
    im, d = layer(ss)
    gl, gd = layer(ss)
    a = ptr_ang
    piv = R_OUT + 34
    tip = R_OUT - 50
    cw_r = R1 + 62 * ps + (34 if boss else 0)
    # arm
    arm = [Q(tip, 0, a, ss), Q(piv - 30, -15 * ps, a, ss), Q(cw_r, -7 * ps, a, ss), Q(cw_r, 7 * ps, a, ss), Q(piv - 30, 15 * ps, a, ss)]
    d.polygon(arm, fill=(170, 172, 180, 255), outline=INK + (255,), width=int(2.5 * ss))
    d.polygon([Q(tip + 6, 0, a, ss), Q(piv - 30, -12 * ps, a, ss), Q(cw_r - 4, -4 * ps, a, ss), Q(cw_r - 4, 0, a, ss)], fill=(232, 232, 238, 255))
    d.polygon([Q(tip, 0, a, ss), Q(tip + 30, -6 * ps, a, ss), Q(tip + 30, 6 * ps, a, ss)], fill=acc + (255,))
    gd.polygon([Q(tip, 0, a, ss), Q(tip + 30, -6, a, ss), Q(tip + 30, 6, a, ss)], fill=acc + (255,))
    # counterweight (outside the rim)
    x, y = Q(cw_r, 0, a, ss)
    r = 22 * ss * ps
    d.ellipse([x - r, y - r, x + r, y + r], fill=(92, 92, 102, 255), outline=INK + (255,), width=int(2.5 * ss))
    d.ellipse([x - r * 0.72, y - r * 0.72, x + r * 0.72, y + r * 0.72], outline=(140, 140, 150, 255), width=int(2 * ss))
    d.ellipse([x - r * 0.55, y - r * 0.6, x - r * 0.05, y - r * 0.2], fill=(215, 215, 225, 255))
    # pivot housing + split-flap value counter
    hw, hh = 52 * ps, 34 * ps
    hx, hy = Q(piv, 0, a, ss)
    d.rounded_rectangle([hx - hw * ss, hy - hh * ss, hx + hw * ss, hy + hh * ss], radius=10 * ss, fill=(58, 58, 66, 255), outline=INK + (255,), width=int(3 * ss))
    d.rounded_rectangle([hx - hw * ss + 3 * ss, hy - hh * ss + 3 * ss, hx + hw * ss - 3 * ss, hy - hh * ss + 9 * ss], radius=4 * ss, fill=(120, 120, 132, 255))
    val = La["value"]
    txt = "%2s" % (val if val is not None else "--")
    fw, fh = 32 * ps, 46 * ps
    ff = f_num(int(46 * ps * ss))
    for k, ch in enumerate(txt):
        x0 = hx + (-fw - 2 * ps + k * (fw + 4 * ps)) * ss
        y0 = hy - fh / 2 * ss
        d.rounded_rectangle([x0, y0, x0 + fw * ss, y0 + fh * ss], radius=4 * ss, fill=(18, 18, 22, 255), outline=INK + (255,), width=int(1.5 * ss))
        d.rectangle([x0, y0 + fh * ss / 2, x0 + fw * ss, y0 + fh * ss], fill=(12, 12, 15, 255))
        if ch.strip():
            tw = ff.getlength(ch)
            d.text((x0 + fw * ss / 2 - tw / 2, y0 - 3 * ps * ss), ch, font=ff, fill=(250, 250, 245, 255))
        d.line([(x0, y0 + fh * ss / 2), (x0 + fw * ss, y0 + fh * ss / 2)], fill=(0, 0, 0, 255), width=int(2 * ss))
    pcx = PROGRAMS[La["prog"]]["col"]
    for sx in (-1, 1):  # program-colour indicator lamps either side of the flaps
        lx = hx + sx * (hw - 9 * ps) * ss
        lr = 5 * ps * ss
        gd.ellipse([lx - lr * 2, hy - lr * 2, lx + lr * 2, hy + lr * 2], fill=pcx + (200,))
        d.ellipse([lx - lr, hy - lr, lx + lr, hy + lr], fill=pcx + (255,), outline=INK + (255,), width=max(1, ss))
    shadow_of(canvas, im, ss, 9 + t * (D_PTR - D_BEZ) * 0.6, 15, 6, 0.65)
    add_glow(canvas, gl, ss, 0.7)
    over_pil(canvas, im)
    meta.update(ptr_r=piv, hp_r=RA + 36, top_r=cw_r + 22)


# ------------------------------------------------------------------ D4 lens & rail
def _d4(canvas, spec, ss, lod, rot, tilt, Ls, La, ai, acc, emblem, st, boss, hub_r, ptr_ang, meta, hp_number, banner_on):
    R_lip = R_OUT - 4
    Rch0, Rch1 = R_OUT + 8, R_OUT + 44
    R1 = R_OUT + 54
    RT = R1 + (30 if boss else 0)  # threat ring (boss)
    is_player = spec["theme"] == "player"
    base = (0.16, 0.15, 0.19) if is_player else (0.36, 0.21, 0.09)
    dx, dy = grids(ss)
    rho = np.hypot(dx, dy)
    bp = np.clip(R_OUT + 4 - rho, 0, 1)
    canvas[..., :3] = canvas[..., :3] * (1 - bp[..., None]) + np.array([0.02, 0.018, 0.03]) * bp[..., None]
    canvas[..., 3] = np.maximum(canvas[..., 3], bp)
    del dx, dy, rho, bp
    for L in Ls:
        if L is not La:
            place_slice(canvas, L, ss, dim=0.68)
    disc_shadow(canvas, ss, R_lip + 0.5, R_lip, (5, 9), k=0.5, soft=6)
    disc_shadow(canvas, ss, R_OUT, None, (6, 10), k=0.45, soft=7, raised_disc=(127 if spec.get("ring") else hub_r))
    machined(canvas, ss, [(R_lip, 0.0), (R_lip + 3, 6.0), (Rch0 - 3, 7.0), (Rch0, 2.0), (Rch1, 2.0), (Rch1 + 3, 7.0),
                          (R1 - 4, 8.0), (R1, 0.0)], base, acc, screen=(Rch0, Rch1), seed=17,
             accent_r=((Rch0 + 0.5, 0.9, 0.8), (Rch1 - 0.5, 0.9, 0.8), (R1 - 0.8, 1.0, 1.0)), brushed=0.04, gloss=0.8)
    im, d = layer(ss)
    gl, gd = layer(ss)
    telemetry(im, d, gd, spec, Rch0 - 2, Rch1 + 2, ss, acc, emblem, lod,
              rail=(La["prog"], La["value"], 50))
    if boss:
        threat_ring(d, gd, ss, R1 + 1, RT, acc, rot=-rot * 1.7 + 7, telegraph=(), lod=lod)  # round 19: no standing NEXT arrows
        armour_lugs(im, d, gd, ss, RT, acc, emblem)
    _hub_std(im, d, gd, spec, ss, hub_r, acc, st, lod, hp_in_hub=lod)
    _hp(d, gd, ss, RT, spec, boss, hp_number)
    add_glow(canvas, gl, ss)
    over_pil(canvas, im)
    # lifted active slice
    s_l, sh_l = 1.025, 1.0
    tmp = new_canvas(ss)
    place_slice(tmp, La, ss, scale=s_l, shift=sh_l)
    sa = tmp[..., 3]
    small = Image.fromarray((sa * 255).astype(np.uint8)).resize((CW * ss // 4, CH * ss // 4), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(4 * ss)).resize((CW * ss, CH * ss), Image.BILINEAR)
    shd = np.zeros_like(tmp)
    shd[..., 3] = np.asarray(small, np.float32) / 255 * 0.8
    over_arr(canvas, shd, 6 * ss, 11 * ss)
    over_arr(canvas, tmp)
    del tmp, shd
    im2, d2 = layer(ss)
    gl2, gd2 = layer(ss)
    outline_slice(d2, gd2, La, ss, s_l, sh_l, CREAM, w=4.0, glow_col=PROGRAMS[La["prog"]]["col"])
    add_glow(canvas, gl2, ss, 0.8, blur=9)
    over_pil(canvas, im2)
    # compact blade, rooted in the bezel
    ps = 1.6 if lod else 1.0
    tip = R_OUT - 24
    top = RT + 96 * ps
    body = CREAM if not boss else (255, 150, 40)
    bl, bg = blade(ss, ptr_ang, acc, body, (230, 220, 200), La["value"], La["prog"], tip=tip, sh=RT + 18 * ps, top=top,
                   wsh=34 * ps, wtop=50 * ps, win=(RT + 30 * ps, top - 18 * ps, 36 * ps), crown=bool(boss),
                   notch_col=acc if not boss else INK, scale=1.0)
    shadow_of(canvas, bl, ss, 7, 12, 5, 0.65)
    add_glow(canvas, bg, ss, 0.9)
    over_pil(canvas, bl)
    # glass sheen over the disc (d3-lite)
    dx, dy = grids(ss)
    rho = np.hypot(dx, dy)
    th = np.degrees(np.arctan2(dx, -dy)) % 360
    inside = rho < R_lip
    crescent = np.exp(-((rho / R_lip - 0.88) / 0.06) ** 2) * np.clip(np.cos(np.radians(th - 315)), 0, 1) ** 2 * 0.10
    canvas[..., :3] += (crescent * inside)[..., None]
    del dx, dy, rho, th, inside, crescent
    meta.update(ptr_r=(RT + 30 * ps + top - 20 * ps) / 2, hp_r=RT + 36, top_r=top)
    if boss and banner_on and not lod:
        im3, d3 = layer(ss)
        gl3, gd3 = layer(ss)
        banner(im3, d3, gd3, ss, RW.CY - top - 8, boss["title"], boss["sub"], acc, mount=True)
        shadow_of(canvas, im3, ss, 6, 10, 6, 0.6)
        add_glow(canvas, gl3, ss)
        over_pil(canvas, im3)


def armour_lugs(img, d, gd, ss, R, acc, emblem):
    for a in (90, 270):
        x, y = P(R + 8, a, ss)
        r = 40 * ss
        hexp = [(x + r * math.cos(math.radians(60 * j)), y + r * math.sin(math.radians(60 * j))) for j in range(6)]
        gd.polygon(hexp, fill=acc + (160,))
        d.polygon(hexp, fill=(34, 26, 20, 255), outline=acc + (255,), width=int(3 * ss))
        g = RW.tinted_glyph(emblem, int(44 * ss), acc)
        img.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))


def fit(im, centre, ss, r):
    """Resize an ss render so R_OUT maps to r px. Returns (img, centre)."""
    k = r / (R_OUT * ss)
    out = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    return out, (centre[0] * k, centre[1] * k)





