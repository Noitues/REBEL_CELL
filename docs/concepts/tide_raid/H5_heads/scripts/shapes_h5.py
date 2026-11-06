"""H5 beam-head triads (round 3). Six SYSTEMS, each a D / N / E set (+ a 'mystery' 4th unit X) built in one construction language.
Same op format as H4: [(kind, polygon)] in unit space, x = travel direction (y down). kinds: add / ink / fill / mot.
fn(t, f): f is a float animation phase, f=0 -> frame 1, f=1 -> frame 2 (half cycle); a full cycle is f in [0, 2).
  o = cos(pi f) is +1 at frame 1 and -1 at frame 2, so every 2-frame motion is the two extremes of a smooth cycle.

Shared language for ALL triads (the 'family' contract):
  * silhouette classes: D = LONG (fast, light), N = BRANCHED (reaches / intrudes), E = ROUND-MASSIVE (heavy);
  * one outline weight (renderer: 7.5 % of size), one corner radius R for every 'add' polygon (rnd() below);
  * one shared motif per triad (a core dot in ink, r 0.17-0.22 u = >= 3 px at 24 px, plus a triad-specific partner);
  * one light treatment (renderer 'shade': lighter top-left rim, darker bottom-right rim, screen space);
  * weight ramp by mass: footprint is fixed (2.1 u long side), so D is thin, N has gaps, E is solid.
"""
import math
from shapes_h3 import TYPES, HUE, INK, FOOT, ell, circ, mir, bez, taper, rot

R = .1          # the shared corner radius (unit space; 1 u = ~9.7 px at 24 px)
DOT = .18       # the shared core-dot radius
BONE = (236, 228, 208)
XCOL = (205, 200, 225)   # hue of the hypothetical 4th unit in the family test


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def rnd(p, r=R):
    """round every corner of polygon p with a quadratic blend of radius r (shared corner radius)."""
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


def seg(p0, p1, w):
    """rectangle along a segment (for right-angle trace work)."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    d = math.hypot(dx, dy) or 1
    nx, ny = -dy / d * w / 2, dx / d * w / 2
    return [(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny), (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny)]


def arcpts(cx, cy, r, a0, a1, n=24):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def star(cx, cy, r1, r2, n=4, a0=0.0):
    return [(cx + (r1 if i % 2 == 0 else r2) * math.cos(a0 + math.pi * i / n), cy + (r1 if i % 2 == 0 else r2) * math.sin(a0 + math.pi * i / n)) for i in range(2 * n)]


def rotops(ops, a):
    return [(k, rot(p, a)) for k, p in ops]


def dot(x, y, r=DOT):
    return ('ink', circ(x, y, r, 16))


def ngon(cx, cy, r, n, a0=0.0):
    return [(cx + r * math.cos(a0 + 2 * math.pi * i / n), cy + r * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]


def cap(cx, cy, hl, rr):
    """horizontal capsule, centre (cx, cy), half-length hl (between cap centres), radius rr."""
    return [(cx + hl + rr * math.cos(math.radians(a)), cy + rr * math.sin(math.radians(a))) for a in range(-90, 91, 15)] + \
           [(cx - hl + rr * math.cos(math.radians(a)), cy + rr * math.sin(math.radians(a))) for a in range(90, 271, 15)]


def mk(raw):
    """normalise on frame 0 (footprint 2.1 u), round every 'add' corner with the shared radius."""
    def fn(t, f=0):
        o0 = raw(t, 0)
        xs = [x for k, p in o0 if k == 'add' for x, y in p]
        ys = [y for k, p in o0 if k == 'add' for x, y in p]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        s = FOOT / max(max(xs) - min(xs), max(ys) - min(ys))
        ops = o0 if f == 0 else raw(t, f)
        return [(k, [((x - cx) * s, (y - cy) * s) for x, y in (rnd(p) if k == 'add' else p)]) for k, p in ops]
    return fn


def C(f):
    return math.cos(math.pi * f)


def S(f):
    return math.sin(math.pi * f)


# ===================================================================== T1  IMMUNE WEAPON
# Solace's own immune system, weaponised. Motif: core dot + round KNOB on every extremity.
def t1(t, f):
    o, s = C(f), S(f)
    if t == 'D':  # swarm cell: fat rod, knob tail that flicks
        ops = [('add', cap(.2, 0, .5, .37)), ('add', taper([(-.4, 0), (-1.0, .22 * o)], .24, .2)), ('add', circ(-1.05, .24 * o, .2, 14)), dot(.3, 0, .16)]
        return ops
    if t == 'N':  # programmed antibody: Y, bulb ends, hub dot; arms flex
        y = .62 + .12 * (1 - o) / 2 * 2
        ops = [('add', taper([(-.95, 0), (-.1, 0)], .3, .3)), ('add', circ(-1.0, 0, .24)), ('add', circ(0, 0, .42))]
        for sg in (-1, 1):
            ops.append(('add', taper([(-.05, 0), (.72, sg * y)], .32, .27)))
            ops.append(('add', circ(.82, sg * y * 1.05, .27, 18)))
        ops.append(dot(0, 0))
        return ops
    # E armoured phage: octagon capsid, collar, base plate, two thick splayed legs ending in feet knobs
    sp = .08 * (1 - o) / 2 * 2
    ops = [('add', ngon(.2, 0, .98, 8, math.pi / 8)), ('add', rect(-.8, -.26, -.5, .26)), ('add', rect(-1.0, -.52, -.82, .52))]
    for sg in (-1, 1):
        ops.append(('add', taper([(-.95, sg * .4), (-1.25 - sp, sg * (.75 + sp))], .3, .28)))
        ops.append(('add', circ(-1.27 - sp, sg * (.78 + sp), .2, 12)))
    ops.append(dot(.2, 0, .24))
    return ops


def t1x(f):  # macrophage: lumpy cell with 3 pseudopod knobs
    o = C(f)
    ops = [('add', circ(0, 0, .62, 32))]
    for a in (-55, 20, 150):
        ca, sa = math.cos(math.radians(a + 6 * o)), math.sin(math.radians(a + 6 * o))
        ops.append(('add', taper([(.4 * ca, .4 * sa), (.85 * ca, .85 * sa)], .34, .3)))
        ops.append(('add', circ(.95 * ca, .95 * sa, .24, 14)))
    ops.append(dot(0, 0, .2))
    return ops


# ===================================================================== T2  MALWARE ZOO
# Black-ICE daemons caged as lab specimens. Motif: ONE eye-dot on the leading edge of every beast.
def t2(t, f):
    o, s = C(f), S(f)
    if t == 'D':  # worm: S body, round head leads
        ph = math.pi * f
        pts = [(-1.0 + 1.85 * i / 22, .27 * math.sin(2 * math.pi * (i / 22 * 1.85) / 1.3 + ph)) for i in range(23)]
        return [('add', taper(pts, .3, .46)), ('add', circ(pts[-1][0], pts[-1][1], .36)), dot(pts[-1][0] + .08, pts[-1][1], .16)]
    if t == 'N':  # ghost: dome leads, zig-zag hem, single eye dot on the lead
        dome = [(.62 * math.cos(math.radians(a)), -.1 + .62 * math.sin(math.radians(a))) for a in range(180, 361, 10)]
        hem = []
        for i in range(3):
            bx = .62 - .207 - .413 * i
            by = .66 + .09 * o * (1 if i % 2 == 0 else -1)
            hem += [(bx + .207 * math.cos(math.radians(a)), by + .3 * math.sin(math.radians(a))) for a in range(0, 181, 20)]
        return rotops([('add', dome + hem), dot(0, -.2, .21)], math.radians(90))
    # E logic bomb: heavy ball, capped fuse, spark; eye-dot on the lead of the ball
    d = (math.cos(math.radians(-45)), math.sin(math.radians(-45)))
    c = (-.1, .1)
    e = (c[0] + .9 * d[0], c[1] + .9 * d[1])
    ce = (e[0] + .2 * d[0], e[1] + .2 * d[1])
    fuse = taper(bez(ce, (ce[0] + .1, ce[1] - .2), (ce[0] + .3, ce[1] - .25), (ce[0] + .45, ce[1] - .12), 10), .18, .14)
    tip = fuse[len(fuse) // 2 - 1]
    big = o > 0
    sp = star(tip[0] + .08, tip[1] - .1, .38 if big else .26, .14 if big else .1, 4, math.radians(0 if big else 45))
    return [('add', circ(c[0], c[1], .95, 40)), ('add', taper([e, ce], .44, .36)), ('add', fuse), ('add', sp), dot(c[0] + .28, c[1] + .1, .22)]


def t2x(f):  # beetle: oval shell, two antennae with knob tips, eye-dot on the lead
    o = C(f)
    ops = [('add', ell(-.1, 0, .72, .55, 28)), ('add', circ(.62, 0, .3, 16))]
    for sg in (-1, 1):
        ops.append(('add', taper([(.7, sg * .12), (1.05, sg * (.5 + .08 * o))], .16, .14)))
        ops.append(('add', circ(1.08, sg * (.52 + .08 * o), .14, 12)))
    ops.append(dot(.62, 0, .13))
    return ops


# ===================================================================== T3  CLINICAL ROBOTS
# Solace security as sterile service robots. Motif: a HUB DOT (ink port) set in a round hub/turret on every unit.
def t3(t, f):
    o = C(f)
    if t == 'D':  # quad: four rotor discs on an X, hub dot; wobble
        ops = [('add', circ(sx * .7, sy * .7, .27, 18)) for sx in (-1, 1) for sy in (-1, 1)]
        ops += [('add', seg((-.7, -.7), (.7, .7), .17)), ('add', seg((-.7, .7), (.7, -.7), .17)), ('add', circ(0, 0, .36, 20)), dot(0, 0, .16)]
        for sx in (-1, 1):
            for sy in (-1, 1):
                b = rot(rect(-.28, -.035, .28, .035), math.radians(45 * (1 - o) / 2 * 2 + 20))
                ops.append(('mot', [(x + sx * .7, y + sy * .7) for x, y in b]))
        return rotops(ops, math.radians(-7 * o))
    if t == 'N':  # swab probe: hub, three electrode prongs ending in bulbs, rear cable stub
        ops = [('add', circ(-.35, 0, .42, 22)), ('add', taper([(-.7, 0), (-1.05, 0)], .26, .24)), ('add', circ(-1.08, 0, .2, 12))]
        fan = .08 * o
        for yy in (-.85, 0, .85):
            tip = (.88 + (.18 if yy == 0 else 0), yy * (1 + fan))
            ops.append(('add', taper([(-.3, yy * .25), tip], .22, .18)))
            ops.append(('add', circ(tip[0] + .04, tip[1], .22, 14)))
        ops.append(dot(-.35, 0))
        return ops
    # E tank: chamfered hull, barrel that recoils, hatch dot in the turret
    rec = .2 * (1 - o) / 2 * 2 * .8
    ops = [('add', [(-.95, -.8), (.45, -.8), (.74, -.46), (.74, .46), (.45, .8), (-.95, .8)]), ('add', circ(-.1, 0, .56, 22)),
           ('add', rect(.3, -.17, 1.06 - rec, .17)), dot(-.1, 0, .24)]
    for sg in (-1, 1):
        for k in range(5):
            x = -.85 + .3 * k + .15 * (1 - o) / 2 * 2 * .5
            ops.append(('mot', rect(x, sg * .68 - .05, x + .14, sg * .68 + .05)))
    return ops


def t3x(f):  # sentry dome: half dome on a base slab, barrel, hub dot
    o = C(f)
    dome = [(.0 + .7 * math.cos(math.radians(a)), .7 * math.sin(math.radians(a))) for a in range(-90, 91, 12)]
    return [('add', dome + [(-.0, .7)]), ('add', rect(-.9, -.7, 0, .7)), ('add', rect(.5, -.12, 1.1 - .12 * (1 - o), .12)), dot(.1, 0, .2)]


# ===================================================================== T4  TIDE DRIFTERS
# The Tide itself: plankton drifting in. Motif: every head ends in a round KNOB (head / tendril tips / spike tips) + core dot.
def t4(t, f):
    o = C(f)
    if t == 'D':  # darter: round head leads, curving tail with a flick
        ph = math.pi * f
        pts = [(.1 - 1.2 * i / 14, .22 * math.sin(i / 14 * 2 * math.pi - ph) * (i / 14)) for i in range(15)]
        return [('add', taper(pts, .46, .22)), ('add', circ(.5, 0, .5, 26)), dot(.58, 0, .2)]
    if t == 'N':  # jelly: dome leads, three tendrils trail, each ends in a knob
        dome = [(.25 + .56 * math.cos(math.radians(a)), .56 * math.sin(math.radians(a))) for a in range(-90, 91, 10)]
        ops = [('add', dome + [(.25, .56)])]
        for k, yy in enumerate((-.5, 0, .5)):
            w = .12 * math.sin(math.pi * f + k * 2.1)
            pts = [(.25 - 1.3 * i / 9, yy * (1 + .5 * i / 9) + w * i / 9) for i in range(10)]
            ops.append(('add', taper(pts, .24, .2)))
            ops.append(('add', circ(pts[-1][0] - .02, pts[-1][1], .2, 12)))
        ops.append(dot(.42, 0, .18))
        return ops
    # E sea-mine: solid ball, 8 knobbed spikes, ring turns half a step
    ops = [('add', circ(0, 0, .68, 36))]
    off = math.pi / 8 * (1 - o) / 2 * 2 * .5
    for i in range(8):
        a = 2 * math.pi * i / 8 + off
        ca, sa = math.cos(a), math.sin(a)
        ops.append(('add', taper([(.55 * ca, .55 * sa), (.86 * ca, .86 * sa)], .26, .26)))
        ops.append(('add', circ(.9 * ca, .9 * sa, .22, 14)))
    ops.append(dot(0, 0, .22))
    return ops


def t4x(f):  # crab: oval body, two claws on short arms ending in knobs
    o = C(f)
    ops = [('add', ell(-.25, 0, .6, .5, 26))]
    for sg in (-1, 1):
        ops.append(('add', taper([(.1, sg * .3), (.7, sg * (.55 + .06 * o))], .28, .24)))
        ops.append(('add', circ(.82, sg * (.58 + .06 * o), .26, 16)))
    ops.append(dot(-.25, 0, .18))
    return ops


# ===================================================================== T5  SOLACE GARDEN
# Solace's greenhouse gone feral. Motif: a SEED DOT in a round seed body, plus a flat cap / calyx at the trailing end.
def t5(t, f):
    o = C(f)
    if t == 'D':  # samara: seed leads, one long wing trails, wing twists
        wy = .28 * (.7 + .3 * (1 + o) / 2 * 1)
        wing = [(.5, -.1), (0, -wy * 1.05), (-.7, -wy * .9), (-1.3, 0), (-.7, wy * .9), (0, wy * 1.05), (.5, .1)]
        return [('add', wing), ('add', circ(.68, 0, .4, 20)), dot(.72, 0, .17)]
    if t == 'N':  # thorn claw: hub, two curved pincer horns and a centre thorn; pincers snap
        op = .1 * o
        ops = [('add', circ(-.45, 0, .42, 22)), ('add', rect(-1.05, -.2, -.7, .2)), dot(-.45, 0)]
        for sg in (-1, 1):
            path = bez((-.35, sg * .3), (.0, sg * (.9 + op)), (.55, sg * (1.0 + op)), (1.0, sg * (.62 + op)), 14)
            ops.append(('add', taper(path, .32, .08)))
        ops.append(('add', taper([(-.2, 0), (.8, 0)], .28, .1)))
        return ops
    # E bulb: squat round pod, flat calyx cap behind, 3 thorns forward; thorns bristle
    th = .06 * (1 - o) / 2 * 2
    ops = [('add', ell(.0, 0, .84, .84, 36)), ('add', rect(-1.1, -.42, -.78, .42))]
    for a in (-125, -85, -42, 0, 42, 85, 125):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        bx, by = .8 * ca, .8 * sa
        ops.append(('add', taper([(bx, by), (bx + (.3 + th) * ca, by + (.3 + th) * sa)], .38, .06)))
    ops.append(dot(.0, 0, .22))
    return ops


def t5x(f):  # mushroom: dome cap + stem trailing, seed dot
    o = C(f)
    cap_ = [(.35 + .62 * math.cos(math.radians(a)), .62 * math.sin(math.radians(a))) for a in range(-90, 91, 12)] + [(.35, .62)]
    return [('add', cap_ + [(.2, .62)]), ('add', rect(-.9, -.24 - .03 * o, .3, .24 + .03 * o)), ('add', rect(.2, -.62, .45, .62)), dot(.4, 0, .17)]


# ===================================================================== T6  SILICON
# The ICE as printed circuitry. Motif: VIA DOT in a round node on every part; right-angle trace geometry.
def t6(t, f):
    o = C(f)
    if t == 'D':  # trace bolt: staircase trace, round via head leads; steps shift
        sh = .12 * o
        p = [(-1.0, .5), (-.4, .5), (-.4, -.05 + sh), (.15, -.05 + sh), (.15, -.5)]
        ops = [('add', seg(p[i], p[i + 1], .32)) for i in range(len(p) - 1)] + [('add', circ(q[0], q[1], .16, 10)) for q in p[1:-1]]
        ops += [('add', circ(.55, -.5, .4, 20)), ('add', seg(p[-1], (.55, -.5), .32)), dot(.55, -.5, .17)]
        return ops
    if t == 'N':  # trace fork: stem into a node, a cross trace, two prongs ending in via discs
        sh = .08 * o
        ops = [('add', seg((-1.05, 0), (-.2, 0), .3)), ('add', circ(-.2, 0, .38, 20)), ('add', seg((-.2, -.8), (-.2, .8), .3))]
        for sg in (-1, 1):
            ops.append(('add', seg((-.2, sg * .8), (.72 + sh, sg * .8), .3)))
            ops.append(('add', circ(.76 + sh, sg * .8, .26, 16)))
        ops.append(dot(-.2, 0))
        return ops
    # E die: heavy rounded square, four chunky pin tabs, via dot
    ops = [('add', rect(-.9, -.75, .9, .75)), dot(0, 0, .26)]
    for x in (-.45, .45):
        for sg in (-1, 1):
            ops.append(('add', rect(x - .17, sg * .75, x + .17, sg * (.75 + .25))))
    ops.append(('mot', rect(-.75, -.6, -.6, -.45)))
    return ops


def t6x(f):  # diode: rounded body with a band cut, two lead stubs, via dot
    return [('add', rect(-.5, -.42, .5, .42)), ('add', seg((-1.05, 0), (-.4, 0), .26)), ('add', seg((.4, 0), (1.05, 0), .26)), ('add', rect(.12, -.42, .3, .42)), dot(-.15, 0, .17)]


FAMILIES = {
    'T1': dict(name='T1  IMMUNE WEAPON', fn=mk(t1), x=mk(lambda tt, f: t1x(f)), short='immune',
               theme="Solace's own immune system, weaponised.",
               units=['swarm cell: fat rod, knob tail flicks', 'programmed antibody: Y, bulb ends, hub dot', 'armoured phage: octagon capsid, base plate, 2 thick legs'],
               motif='core dot + a round knob on every extremity', mystery='macrophage: round cell, 3 knob pseudopods'),
    'T2': dict(name='T2  MALWARE ZOO', fn=mk(t2), x=mk(lambda tt, f: t2x(f)), short='zoo',
               theme='Black-ICE daemons caged as lab specimens.',
               units=['worm: S body, round head leads, ripples', 'ghost: dome leads, zig-zag hem, one eye-dot', 'logic bomb: heavy ball, fuse, blinking spark'],
               motif='one eye-dot on the leading edge of every beast', mystery='beetle: shell, 2 knob antennae'),
    'T3': dict(name='T3  CLINICAL ROBOTS', fn=mk(t3), x=mk(lambda tt, f: t3x(f)), short='robots',
               theme='Solace security as sterile service robots.',
               units=['quad drone: 4 rotor discs on an X, hub dot', 'swab probe: hub, 3 bulb-tipped prongs, cable stub', 'tank: chamfered hull, round turret + hatch dot, barrel'],
               motif='a round hub / turret with an ink port dot on every unit', mystery='sentry dome: half dome on a slab, barrel'),
    'T4': dict(name='T4  TIDE DRIFTERS', fn=mk(t4), x=mk(lambda tt, f: t4x(f)), short='tide',
               theme='The Tide itself: plankton drifting in.',
               units=['darter: round head leads, curving tail', 'jelly: dome leads, 3 knob-tipped tendrils', 'sea-mine: ball, 8 knobbed spikes (virion)'],
               motif='a round knob on every tip + core dot', mystery='crab: oval body, 2 knob claws'),
    'T5': dict(name='T5  SOLACE GARDEN', fn=mk(t5), x=mk(lambda tt, f: t5x(f)), short='garden',
               theme="Solace's greenhouse gone feral.",
               units=['samara: seed leads, one long wing trails', 'thorn claw: hub, two pincer horns, centre thorn', 'bulb: squat pod, calyx cap, 3 thorns'],
               motif='seed dot in a round body + flat calyx cap trailing', mystery='mushroom: dome cap, stem'),
    'T6': dict(name='T6  SILICON', fn=mk(t6), x=mk(lambda tt, f: t6x(f)), short='silicon',
               theme='The ICE as printed circuitry.',
               units=['trace bolt: staircase trace, via head leads', 'trace fork: node, cross trace, 2 via prongs', 'die: heavy square, 4 pin tabs, via dot'],
               motif='via dot in a round node on every part, right-angle traces', mystery='diode: body, band cut, 2 leads'),
}
ORDER = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']
