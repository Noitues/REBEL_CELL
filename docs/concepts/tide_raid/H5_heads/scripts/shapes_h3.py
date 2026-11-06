"""H3 head families. Every head = list of ops [(kind, polygon)] in unit space, x = travel direction (y down on screen).
kind: add  = part of the silhouette (fill colour, gets the ink outline)
      ink  = inner detail painted in ink on the fill
      fill = fill colour painted back over an ink (rings)
New families are normalised so the silhouette bbox is 2.1 units on its long side (same footprint as the pass-2 heads)."""
import math

TYPES = ('D', 'N', 'E')
HUE = {'D': (70, 144, 255), 'N': (255, 64, 214), 'E': (255, 238, 58)}
INK = (14, 8, 28)
FOOT = 2.1


def ell(cx, cy, rx, ry, n=36):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def circ(cx, cy, r, n=28):
    return ell(cx, cy, r, r, n)


def mir(p):
    return [(x, -y) for x, y in reversed(p)]


def bez(p0, p1, p2, p3, n=18):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def taper(pts, w0, w1):
    """polygon around a polyline with linearly tapering width."""
    n = len(pts)
    L, R = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        w = (w0 + (w1 - w0) * i / (n - 1)) / 2
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    return L + R[::-1]


def rot(p, a):
    c, s = math.cos(a), math.sin(a)
    return [(x * c - y * s, x * s + y * c) for x, y in p]


def normalise(ops):
    xs = [x for k, p in ops if k == 'add' for x, y in p]
    ys = [y for k, p in ops if k == 'add' for x, y in p]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    s = FOOT / max(max(xs) - min(xs), max(ys) - min(ys))
    return [(k, [((x - cx) * s, (y - cy) * s) for x, y in p]) for k, p in ops]


# ---------------------------------------------------------------- family 0: current (pass 2), unmodified
def cur(t):
    if t == 'D':
        return [('add', [(1.12, 0), (-.9, -.88), (-.42, 0), (-.9, .88)])]
    if t == 'N':
        out = [('add', [(-.52, -.52), (.52, -.52), (.52, .52), (-.52, .52)])]
        th, a, q = .26, .52, 1.08
        for sx in (-1, 1):
            for sy in (-1, 1):
                out.append(('add', [(sx * q, sy * q), (sx * (q - a), sy * q), (sx * (q - a), sy * (q - th)), (sx * (q - th), sy * (q - th)),
                                    (sx * (q - th), sy * (q - a)), (sx * q, sy * (q - a))]))
        return out
    return [('add', [(-.95, -.95), (1.12, -.95), (.68, -.28), (-.12, -.28), (-.12, .28), (.68, .28), (1.12, .95), (-.95, .95)])]


# ---------------------------------------------------------------- family A: frames (triangle / diamond / hexagon)
def fam_a(t):
    if t == 'D':
        return normalise([('add', [(1.15, 0), (-.85, -.9), (-.85, .9)])])
    if t == 'N':
        return normalise([('add', [(1.1, 0), (0, -.95), (-1.1, 0), (0, .95)]), ('ink', circ(0.05, 0, .25))])

    def hexa(r):
        return [(1.1 * r, 0), (.55 * r, .95 * r), (-.55 * r, .95 * r), (-1.1 * r, 0), (-.55 * r, -.95 * r), (.55 * r, -.95 * r)]
    return normalise([('add', hexa(1.0)), ('ink', hexa(.68)), ('fill', hexa(.46))])


# ---------------------------------------------------------------- family B: creatures seen from above (wasp / cobra / bull)
def fam_b(t):
    if t == 'D':  # wasp drone: two long wings swept back, pinched body, round head leading, stinger trailing
        w = rot(ell(0, 0, .62, .17), math.radians(-38))
        wu = [(x - .1, y - .5) for x, y in w]
        ops = [('add', wu), ('add', [(x, -y) for x, y in wu]),
               ('add', ell(-.5, 0, .5, .2)), ('add', ell(.1, 0, .3, .24)), ('add', circ(.62, 0, .27)),
               ('add', [(-.9, .09), (-1.3, 0), (-.9, -.09)])]
        for x in (-.7, -.45):
            ops.append(('ink', [(x, -.3), (x + .08, -.3), (x + .08, .3), (x, .3)]))
        return normalise(ops)
    if t == 'N':  # serpent: flared hood, jaws leading, S-curved tail
        up = [(.2, -.36), (1.1, -.22), (.4, -.03)]
        tail = taper(bez((-.4, 0), (-.8, .75), (-1.2, -.75), (-1.6, .05), 20), .42, .05)
        ops = [('add', ell(-.1, 0, .5, .92)), ('add', up), ('add', mir(up)), ('add', tail),
               ('ink', taper([(-.45, -.5), (-.05, 0), (-.45, .5)], .15, .15))]
        return normalise(ops)
    # bull: small skull, narrow muzzle, two horns that sweep out and forward with clear air between horn and muzzle
    h = taper(bez((-.55, .3), (-.75, 1.25), (.3, 1.3), (.95, .72)), .36, .05)
    ops = [('add', ell(-.4, 0, .5, .5)),
           ('add', [(-.1, -.27), (.85, -.27), (1.05, -.14), (1.05, .14), (.85, .27), (-.1, .27)]),
           ('add', h), ('add', mir(h)),
           ('ink', taper([(-.55, -.25), (-.2, 0), (-.55, .25)], .12, .12))]
    return normalise(ops)


# ---------------------------------------------------------------- family C: hacker symbols (cursor / prompt / shield-keyhole)
def fam_c(t):
    if t == 'D':  # mouse pointer, rotated so its tip leads
        cur_ = [(0, 0), (0, 17), (4.2, 13.2), (7.2, 20), (10, 18.8), (7.1, 12.2), (12.5, 12.2)]
        ang = math.atan2(-math.sin(math.radians(67)), -math.cos(math.radians(67)))  # tip direction = opposite of the bisector into the body
        return normalise([('add', rot(cur_, -ang))])
    if t == 'N':  # >_ prompt: chevron leads, block cursor trails
        chev = [(-.5, -.95), (.1, -.95), (1.1, 0), (.1, .95), (-.5, .95), (.4, 0)]
        blk = [(-1.05, -.42), (-.62, -.42), (-.62, .42), (-1.05, .42)]
        return normalise([('add', chev), ('add', blk)])
    sh = [(-.95, -.92), (-.1, -.92), (.7, -.55), (1.12, 0), (.7, .55), (-.1, .92), (-.95, .92)]
    return normalise([('add', sh), ('ink', circ(.12, 0, .27)), ('ink', [(.12, -.12), (-.62, -.22), (-.62, .22), (.12, .12)])])


FAMILIES = {
    'cur': dict(name='0  CURRENT (pass 2)', fn=cur, concept='dart / block in selection brackets / bull-horn C', ref=True),
    'A': dict(name='A  FRAMES', fn=fam_a, concept='triangle / diamond / hexagon: military unit-frame primitives, side count = weight'),
    'B': dict(name='B  DAEMONS', fn=fam_b, concept='wasp / cobra / bull, seen from above: black-ICE creatures'),
    'C': dict(name='C  HACKER GLYPHS', fn=fam_c, concept='pointer / >_ prompt / keyhole shield: the symbols of the trade'),
}
