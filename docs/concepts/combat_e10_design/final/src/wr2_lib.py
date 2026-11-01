"""R2 shared kit for the wave_rings cluster: colour tokens, rounded HP segment, phosphor mesh, token placement rule,
the shared radial layout of a unit cell (outline / tray / chevrons), the colour-blind simulators.
Options in R2 are 'R' (the refined AD pick) and 'V' (the one variant); A/B/C are the untouched R1 drawings."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageChops
import wr_state as ST
from wr_state import opt
from wr_geo import *
import e8lib as E8

# ----------------------------------------------------------------------------- tokens (BRIEF 3.3)
INKC = (12, 10, 22)
HARM = (255, 68, 51)
GAINC = (123, 224, 123)
CREAMC = (255, 244, 214)
NETC = (92, 225, 255)
BOSSG = (255, 196, 40)           # BOSS_GOLD (the board gold; the brief lists #FFC428)
BOSSG_HI = (255, 226, 120)
PLAN = (255, 226, 0)             # PENCIL_PLAN
PLAN_THREAT = (255, 28, 44)      # PENCIL_THREAT
STEELC = (150, 162, 182)
STEELC_HI = (226, 233, 246)
STEELC_DK = (84, 96, 120)
LANE_COL = [HARM, (120, 170, 255), (236, 240, 255)]
LW = (4.0, 3.0, 3.0)             # lane ladder 4 / 3 / 3
TOK_R = 27.0                     # 54 px token disc


def R2(el):
    return opt(el) in ('R', 'V')


def alpha_mix(c, bg, a):
    return tuple(int(round(bg[i] + (c[i] - bg[i]) * a)) for i in range(3))


# ----------------------------------------------------------------------------- rounded segment (HP grammar: rounded segment r3)
def rseg(L, r0, r1, a0, a1, fill, rad=3.0, ink=True, ow=1.3, fill_a=255):
    """a rounded arc segment (corner radius rad px) between radii r0..r1 and angles a0..a1; ink keyline ow px outside."""
    rm = (r0 + r1) / 2.0
    rad = min(rad, (r1 - r0) / 2.0 - 0.01, math.radians(a1 - a0) * rm / 2.0 - 0.01)
    rad = max(rad, 0.4)
    da = math.degrees(rad / rm)
    shr = arc_band(r0 + rad, r1 - rad, a0 + da, a1 - da)
    if ink:
        L.line(shr + [shr[0]], INKC, 2 * rad + 2 * ow)
    f = tuple(fill) + (fill_a,)
    L.line(shr + [shr[0]], f, 2 * rad)
    L.poly(shr, fill=f)


def tint(L, poly, col, alpha):
    """true alpha composite of a flat colour over poly (ImageDraw on RGBA OVERWRITES pixels, which is how R1's translucent dead-cell veil went near black)"""
    k = L.k
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    x0, y0 = int(min(xs)) - 2, int(min(ys)) - 2
    x1, y1 = int(max(xs)) + 3, int(max(ys)) + 3
    t = Image.new('RGBA', ((x1 - x0) * k, (y1 - y0) * k), (0, 0, 0, 0))
    ImageDraw.Draw(t).polygon([((x - x0) * k, (y - y0) * k) for x, y in poly], fill=tuple(col) + (int(alpha),))
    L.im.alpha_composite(t, (x0 * k, y0 * k))


# ----------------------------------------------------------------------------- shared 3 px phosphor mesh (BRIEF 3.11 #8: max 8 percent value lift)
def mesh(L, poly, lift=0.08, pitch=3.0):
    """one 3 px mesh shared by slice screens and unit CRT bowls: 1 px lighter lines both ways every 3 px, each lifting value by at most `lift`."""
    import wr_units as WU

    def fn(d, ox, oy, k):
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
        a = int(255 * lift)
        x = math.floor(min(xs) / pitch) * pitch
        while x < max(xs) + 1:
            d.rectangle([(x - ox) * k, (min(ys) - 2 - oy) * k, (x + 1 - ox) * k - 1, (max(ys) + 2 - oy) * k], fill=(255, 255, 255, a))
            x += pitch
        y = math.floor(min(ys) / pitch) * pitch
        while y < max(ys) + 1:
            d.rectangle([(min(xs) - 2 - ox) * k, (y - oy) * k, (max(xs) + 2 - ox) * k, (y + 1 - oy) * k - 1], fill=(255, 255, 255, a))
            y += pitch
    WU.masked(L, poly, fn)


# ----------------------------------------------------------------------------- token placement (element token_placement)
def place_mode():
    return opt('token_placement')


def token_pos_r2(u, mode=None):
    """RULE (R): the token sits at the START CAP of the unit: its centre is TOK_R + 7 px (+4 px half gutter) along the cell mid-line from the cell's counter-clockwise end
    (b0 = 60*s - 30), on the cell's radial middle.  The same arc distance for width 1, 2, 3 and 6; never tied to a sector axis, so chevrons and the
    pencil X end cap (both on axes) stay clear."""
    mode = mode or place_mode()
    ri, ro = CB.ring_geom(u['dep'])
    rm = ri + 32.0
    b0 = 60 * u['s'] - 30
    if mode == 'V':        # flush: the disc touches the cell's start cap (36 -> 31 px)
        d = 4.0 + TOK_R + 1.0
    elif mode == 'C':      # centred on the first sector axis (the 'centre of the first sector' alternative)
        return ppx(C, rm, 60 * u['s'])
    else:
        d = 4.0 + TOK_R + 7.0
    return ppx(C, rm, b0 + math.degrees(d / rm))


# ----------------------------------------------------------------------------- the shared radial layout of a unit cell (outline / armour rails / HP tray / chevrons)
PIP_H = 7.5


def cell_layout(u):
    """radii (px from the tower centre) for one unit cell, outermost first:
    outline centre = rb;  ink sheath inner edge = rb - (lw + 4.5)/2;  tray outer = sheath - 0.5;  HP pips PIP_H high with 1.5 px tray padding
    (armoured: 2.5 px steel rail either side instead);  chevrons grow inward from `start`."""
    ra, rb = radial_ext(u['dep'])
    lw = LW[u['dep']]
    sheath_in = rb - (lw + 4.5) / 2.0
    t_out = sheath_in - 0.5
    armour = u.get('df') == 'armor'
    pad = 2.5 if armour else 1.5
    r1 = t_out - pad
    r0 = r1 - PIP_H
    t_in = r0 - pad
    return dict(ra=ra, rb=rb, lw=lw, sheath_out=rb + (lw + 4.5) / 2, sheath_in=sheath_in, t_out=t_out, t_in=t_in, r0=r0, r1=r1, pad=pad, armour=armour,
                start=(10.5 + (1.5 if u['dep'] == 0 else 0.0)))


def chev_params(u, n_total):
    """chevron pitch / depth for a stack of n_total that must end above the HP tray (compressed only when needed)"""
    ly = cell_layout(u)
    ri, ro = CB.ring_geom(u['dep'])
    limit = (ly['t_in'] - 0.6) - ri - ly['start'] - 5.25          # radial room for (n-1)*pitch + depth
    p, d = 8.4, 6.8
    need = (n_total - 1) * p + d
    if need > limit and n_total > 1:
        p = max(7.3, min(p, (limit - 4.8) / (n_total - 1)))
        d = max(4.4, min(d, limit - (n_total - 1) * p))
    return dict(half=13.5 if d > 5.2 else 12.0, depth=d, w=6.0, ink=10.5, pitch=p, start=ly['start'])


# ----------------------------------------------------------------------------- colour-blind simulation (Machado 2009, severity 1.0)
_M = {
    'deutan': np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
    'protan': np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]),
    'tritan': np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]),
}


def _lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _gam(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055) * 255.0


def sim_cb(img, kind='deutan'):
    a = _lin(np.asarray(img.convert('RGB'), np.float32))
    return Image.fromarray(np.clip(_gam(a @ _M[kind].T), 0, 255).astype(np.uint8), 'RGB')


def sim_rgb(c, kind='deutan'):
    a = _lin(np.array(c, np.float32))
    return tuple(int(v) for v in np.clip(_gam(_M[kind] @ a), 0, 255))


def lab(c):
    a = _lin(np.array(c, np.float32))
    X = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]) @ a
    X = X / np.array([0.95047, 1.0, 1.08883])
    f = np.where(X > 0.008856, np.cbrt(X), 7.787 * X + 16 / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def dE(c1, c2):
    return float(np.linalg.norm(lab(c1) - lab(c2)))
