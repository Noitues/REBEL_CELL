"""H6 final beam heads: D drone (T2 worm), N netrunner (T5 thorn claw), E enforcer (T4 sea-mine / virion), X4 beetle (T2).

THE FAMILY CONTRACT (all four obey it, enforced here in code, not re-drawn per head):
  * one outline weight: 7.5 % of the render size (renderer), ink 0E081C;
  * one corner radius R = .10 u applied AFTER the footprint scale (so E keeps the same radius though it is smaller);
  * one core dot: ink, r = DOT = .18 u on every head, always in a round node (worm head, claw hub, mine body, beetle head)
    that leaves >= .18 u (3 px at 44 px) of fill around it;
  * one rim light: screen-space, lighter top-left rim, darker bottom-right rim (renderer 'shade');
  * footprints: D and N 2.1 u (N is the reference), E and X4 0.852 x that = 1.79 u (designer ruling: E ~15 % smaller than N);
  * mass ramp is carried by SOLIDITY and DENSITY, not size: D thin (one 0.3-0.46 u line) < X4 (oval shell + legs-free, 1 body)
    < N open (hub + 3 horns with gaps) < E solid (full ball, 8 short spikes, armour ring round the dot, no gaps).
  * direction: D head leads (round head + eye-dot ahead of the body), N hub trails and the horns open forward,
    E has a longer lead spike with a bigger knob and the dot sits forward of centre, X4 head + antennae lead.
Ops: [(kind, polygon)] unit space, x = travel direction, y down. kinds: add / ink / fill / mot (mot only drawn at size >= 40).
fn(t, f, amp): f is the cycle phase in [0, 2) (4 frames = f 0, .5, 1, 1.5), amp scales the motion (1 travel, .35 idle)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageChops
from shapes_h3 import ell, circ, bez, taper, rot

FOOT = 2.1                 # N / D footprint (u)
E_FOOT = 2.1 * 0.852       # = 1.79 u, E and X4
R = .10                    # shared corner radius (u)
DOT = .18                  # shared core dot (u)
INK = (14, 8, 28)
HUE = {'D': (70, 144, 255), 'N': (255, 64, 214), 'E': (255, 238, 58), 'X': (176, 182, 200)}
NAMES = {'D': 'D  DRONE (T2 worm)', 'N': 'N  NETRUNNER (T5 thorn claw)', 'E': 'E  ENFORCER (T4 sea-mine / virion)', 'X': '4th  BEETLE (T2, neutral / future)'}
TYPES = ('D', 'N', 'E', 'X')
OW_FRAC = .075
RIM_LITE, RIM_DARK = .38, .66
KEYS = ('D', 'N', 'E', 'X')


def hexs(c):
    return '#%02X%02X%02X' % tuple(c)


def rim_lite(c):
    return tuple(int(v + (255 - v) * RIM_LITE) for v in c)


def rim_dark(c):
    return tuple(int(v * RIM_DARK) for v in c)


def rnd(p, r=R):
    n = len(p)
    out = []
    for i in range(n):
        a, b, c = p[i - 1], p[i], p[(i + 1) % n]
        l1 = math.hypot(a[0] - b[0], a[1] - b[1])
        l2 = math.hypot(c[0] - b[0], c[1] - b[1])
        if l1 < 1e-6 or l2 < 1e-6:
            out.append(b)
            continue
        k1, k2 = min(r, .45 * l1) / l1, min(r, .45 * l2) / l2
        p0 = (b[0] + (a[0] - b[0]) * k1, b[1] + (a[1] - b[1]) * k1)
        p2 = (b[0] + (c[0] - b[0]) * k2, b[1] + (c[1] - b[1]) * k2)
        for t in (0, .25, .5, .75, 1):
            u = 1 - t
            out.append((u * u * p0[0] + 2 * u * t * b[0] + t * t * p2[0], u * u * p0[1] + 2 * u * t * b[1] + t * t * p2[1]))
    return out


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def dot(x, y, r=DOT):
    return ('ink', circ(x, y, r, 20))


def C(f):
    return math.cos(math.pi * f)


# ------------------------------------------------------------------ D DRONE: T2 worm, round head leads
def raw_D(f, amp):
    ph = math.pi * f
    pts = [(-1.0 + 1.85 * i / 22, .27 * amp * math.sin(2 * math.pi * (i / 22 * 1.85) / 1.3 + ph)) for i in range(23)]
    hx, hy = pts[-1]
    return [('add', taper(pts, .22, .32)), ('add', circ(pts[0][0], pts[0][1], .13, 12)), ('add', circ(hx, hy, .35, 24)), dot(hx + .05, hy)]


# ------------------------------------------------------------------ N NETRUNNER: T5 thorn claw
def raw_N(f, amp):
    o = C(f)
    op = .2 * amp * o
    ops = [('add', circ(-.45, 0, .38, 26)), ('add', rect(-1.05, -.2, -.7, .2)), dot(-.45, 0)]
    for sg in (-1, 1):
        path = bez((-.3, sg * .3), (.3, sg * (.6 + op)), (.6, sg * (1.3 + op)), (1.1, sg * (.55 + op * .5)), 16)
        ops.append(('add', taper(path, .28, .16)))       # tip .17 u (was .08): >= 3 px at 44 px
    ops.append(('add', taper([(-.2, 0), (.55, 0)], .24, .16)))
    return ops


# ------------------------------------------------------------------ E ENFORCER: T4 sea-mine / virion, with a lead spike
def raw_E(f, amp):
    ops = [('add', circ(0, 0, .88, 40))]
    for i in range(8):
        a = 2 * math.pi * i / 8
        ca, sa = math.cos(a), math.sin(a)
        lead = (i == 0)
        pulse = amp * .12 * math.cos(math.pi * f + (i % 2) * math.pi)
        reach = (1.10 if lead else (.94 if i == 4 else .98)) + pulse
        kr = .30 if lead else .18
        ops.append(('add', taper([(.7 * ca, .7 * sa), (reach * ca, reach * sa)], .30, .28)))
        ops.append(('add', circ((reach + .04) * ca, (reach + .04) * sa, kr, 16)))
    # armour ring (density mark) round the shared dot, dot sits forward of centre
    ops.append(('mot', circ(.12, 0, .50, 28)))
    ops.append(('fill', circ(.12, 0, .38, 28)))
    ops.append(dot(.12, 0))
    return ops


# ------------------------------------------------------------------ X4 BEETLE (neutral / future)
def raw_X(f, amp):
    o = C(f)
    ops = [('add', ell(-.2, 0, .74, .56, 30)), ('add', circ(.58, 0, .36, 20))]
    for sg in (-1, 1):
        ops.append(('add', taper([(.7, sg * .2), (1.1, sg * (.55 + .1 * amp * o * sg * sg))], .17, .15)))
        ops.append(('add', circ(1.14, sg * (.58 + .1 * amp * o), .16, 14)))
    ops.append(('mot', rect(-.92, -.045, .3, .045)))   # shell split, only >= 40 px
    ops.append(dot(.6, 0))
    return ops


RAW = {'D': raw_D, 'N': raw_N, 'E': raw_E, 'X': raw_X}
FOOTS = {'D': FOOT, 'N': FOOT, 'E': E_FOOT, 'X': E_FOOT}


def head(t, f=0.0, amp=1.0):
    """normalised ops for head t at phase f. Scale/centre come from frame 0 at amp 1, rounding after scaling."""
    o0 = RAW[t](0.0, 1.0)
    xs = [x for k, p in o0 if k == 'add' for x, y in p]
    ys = [y for k, p in o0 if k == 'add' for x, y in p]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    s = FOOTS[t] / max(max(xs) - min(xs), max(ys) - min(ys))
    ops = RAW[t](f, amp)
    out = []
    for k, p in ops:
        q = [((x - cx) * s, (y - cy) * s) for x, y in p]
        out.append((k, rnd(q) if k == 'add' else q))
    return out


# ------------------------------------------------------------------ renderer
SS = 8


def render_head(ops, size, ang_deg, fill, ink=INK, ow=None, detail=None, shade=True, mot_min=40):
    ow = max(1.5, size * OW_FRAC) if ow is None else ow
    Cc = int(size * 1.6) + 6
    H = Cc * SS
    u = (size - 2 * ow) / FOOT * SS
    a = math.radians(ang_deg)
    c, s = math.cos(a), math.sin(a)

    def T(p):
        return [(H / 2 + (x * c - y * s) * u, H / 2 + (x * s + y * c) * u) for x, y in p]
    sil = Image.new('L', (H, H), 0)
    d = ImageDraw.Draw(sil)
    for k, p in ops:
        if k == 'add':
            d.polygon(T(p), fill=255)
    out = Image.new('L', (H, H), 0)
    do = ImageDraw.Draw(out)
    if ow > 0:
        r = ow * SS
        for k, p in ops:
            if k != 'add':
                continue
            q = T(p)
            do.polygon(q, fill=255)
            for i in range(len(q)):
                x0, y0 = q[i]
                x1, y1 = q[(i + 1) % len(q)]
                do.line([(x0, y0), (x1, y1)], fill=255, width=int(2 * r))
                do.ellipse([x0 - r, y0 - r, x0 + r, y0 + r], fill=255)
    img = Image.new('RGB', (H, H), (0, 0, 0))
    img.paste(Image.new('RGB', (H, H), ink), mask=out)
    img.paste(Image.new('RGB', (H, H), fill), mask=sil)
    if shade:
        dd = max(1.0, size * .055) * SS * .75
        dx = int(round(dd))
        up = ImageChops.subtract(sil, ImageChops.offset(sil, -dx, -dx))
        lo = ImageChops.subtract(sil, ImageChops.offset(sil, dx, dx))
        img.paste(Image.new('RGB', (H, H), rim_dark(fill)), mask=up)
        img.paste(Image.new('RGB', (H, H), rim_lite(fill)), mask=lo)
    dc = detail or ink
    di = ImageDraw.Draw(img)
    for k, p in ops:
        if k == 'ink' or (k == 'mot' and size >= mot_min):
            di.polygon(T(p), fill=dc)
        elif k == 'fill' and size >= mot_min:
            di.polygon(T(p), fill=fill)
    alpha = Image.fromarray(np.maximum(np.asarray(out), np.asarray(sil)))
    img = img.resize((Cc, Cc), Image.LANCZOS)
    alpha = alpha.resize((Cc, Cc), Image.LANCZOS)
    img.putalpha(alpha)
    return img


def paste_head(base, ops, cx, cy, size, ang_deg, t, **kw):
    im = render_head(ops, size, ang_deg, kw.pop('fill', HUE[t]), **kw)
    base.alpha_composite(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))))


def mask_at(ops, size, ang_deg):
    im = render_head(ops, size, ang_deg, (255, 255, 255), shade=False)
    return np.asarray(im.split()[3], np.float32) / 255.0
