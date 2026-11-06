"""H4 head families (round 2): hacking / Solace bio-medical / military, each simpler than H3 B.
Every head = list of ops [(kind, polygon)] in unit space, x = travel direction (y down).
kind: add  = part of the silhouette (fill colour, gets the ink outline)
      ink  = inner detail painted in ink (a 'cut')
      fill = fill colour painted back over an ink
      mot  = fine motion detail in ink, only drawn when the head is >= 40 px (never at game size)
fn(t, f) with f in {0, 1} = motion frame. Normalisation is taken from frame 0 so frames never rescale.
"""
import math
from shapes_h3 import (TYPES, HUE, INK, FOOT, ell, circ, mir, bez, taper, rot, fam_a, fam_b)


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def arcpts(cx, cy, r, a0, a1, n=24):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def star(cx, cy, r1, r2, n=4, a0=0.0):
    out = []
    for i in range(2 * n):
        r = r1 if i % 2 == 0 else r2
        a = a0 + math.pi * i / n
        out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def rotops(ops, a):
    return [(k, rot(p, a)) for k, p in ops]


def mk(raw):
    """normalise with frame-0 bbox so the motion frames keep scale and centre."""
    def fn(t, f=0):
        o0 = raw(t, 0)
        xs = [x for k, p in o0 if k == 'add' for x, y in p]
        ys = [y for k, p in o0 if k == 'add' for x, y in p]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        s = FOOT / max(max(xs) - min(xs), max(ys) - min(ys))
        return [(k, [((x - cx) * s, (y - cy) * s) for x, y in p]) for k, p in (o0 if f == 0 else raw(t, f))]
    return fn


# ============================================================ H1  MALWARE: worm / ghost (rootkit daemon) / logic bomb
def malware(t, f):
    if t == 'D':  # worm: one tapered S-body, round head leading; the S ripples
        ph = f * math.pi
        pts = [(-1.0 + 1.85 * i / 22, .28 * math.sin(2 * math.pi * (i / 22 * 1.85) / 1.3 + ph)) for i in range(23)]
        return [('add', taper(pts, .34, .6)), ('add', circ(pts[-1][0], pts[-1][1], .38))]
    if t == 'N':  # ghost: dome leads, zig-zag hem trails, two eye cuts. Drawn upright then turned to +x
        dome = [(.9 * math.cos(math.radians(a)), -.1 + .9 * math.sin(math.radians(a))) for a in range(180, 361, 10)]
        xs = [.9 - .3 * i for i in range(7)]
        hem = [(x, .98 if (i + f) % 2 == 0 else .7) for i, x in enumerate(xs)]
        body = dome + hem
        eyes = [('ink', circ(-.32, -.28, .19)), ('ink', circ(.32, -.28, .19))]
        return rotops([('add', body)] + eyes, math.radians(90))
    # E logic bomb: heavy ball, capped fuse up and forward, spark
    d = (math.cos(math.radians(-45)), math.sin(math.radians(-45)))
    c = (-.2, .14)
    e = (c[0] + .8 * d[0], c[1] + .8 * d[1])
    cap_end = (e[0] + .28 * d[0], e[1] + .28 * d[1])
    fuse = taper(bez(cap_end, (cap_end[0] + .1, cap_end[1] - .2), (cap_end[0] + .3, cap_end[1] - .25), (cap_end[0] + .45, cap_end[1] - .12), 10), .16, .12)
    tip = fuse[len(fuse) // 2 - 1]
    sp = star(tip[0] + .08, tip[1] - .1, .38 if f == 0 else .26, .13 if f == 0 else .09, 4, math.radians(0 if f == 0 else 45))
    return [('add', circ(c[0], c[1], .8, 36)), ('add', taper([e, cap_end], .42, .34)), ('add', fuse), ('add', sp)]


# ============================================================ H2  EXPLOIT GLYPHS: bolt / hook (phish) / data cylinder
def exploit(t, f):
    if t == 'D':  # zero-day bolt, tip leads; frame 2 is the mirrored strike
        b = [(.3, -1), (-.5, .1), (-.05, .1), (-.3, 1), (.5, -.15), (.05, -.15)]
        b = rot(b, math.radians(90))
        return [('add', b if f == 0 else [(x, -y) for x, y in b])]
    if t == 'N':  # phishing hook: thick J, barb, eye ring at the shank end; the hook swings
        arc = arcpts(0, 0, .58, -90, 190, 22)
        path = [(-1.1 + .11 * i, -.58) for i in range(10)] + arc[1:]
        ops = [('add', taper(path, .44, .12)), ('add', circ(-1.1, -.58, .3)), ('ink', circ(-1.1, -.58, .12))]
        return rotops(ops, math.radians(-9 if f == 0 else 9))
    # E data cylinder (heavy store): lid lifts in frame 2
    lid = -.6 - .16 * f
    arc = [(x, lid + .3 * math.sqrt(max(0, 1 - (x / .8) ** 2))) for x in [-.8 + 1.6 * i / 16 for i in range(17)]]
    return [('add', rect(-.8, -.6, .8, .65)), ('add', ell(0, .65, .8, .3)), ('add', ell(0, lid, .8, .3)), ('ink', taper(arc, .16, .16))]


# ============================================================ B1  PATHOGENS: bacillus / bacteriophage / virion
def pathogen(t, f):
    if t == 'D':  # bacillus rod, round-ended, one flagellum tail that waves
        ph = f * math.pi
        rod = [(.55 + .4 * math.cos(math.radians(a)), .4 * math.sin(math.radians(a))) for a in range(-90, 91, 15)] + \
              [(-.45 + .4 * math.cos(math.radians(a)), .4 * math.sin(math.radians(a))) for a in range(90, 271, 15)]
        fl = [(-.8 - .62 * i / 14, .24 * math.sin(i / 14 * 2 * math.pi + ph)) for i in range(15)]
        return [('add', rod), ('add', taper(fl[::-1], .12, .26)[::1])] if False else [('add', rod), ('add', taper(fl, .26, .12))]
    if t == 'N':  # bacteriophage: elongated capsid leads, tail, baseplate, two splayed legs
        head = [(1.1, 0), (.62, .6), (-.12, .6), (-.46, 0), (-.12, -.6), (.62, -.6)]
        sp = .1 * (1 if f else -1)
        ops = [('add', head), ('add', rect(-.95, -.11, -.4, .11)), ('add', rect(-1.02, -.46, -.88, .46))]
        for s in (-1, 1):
            ops.append(('add', taper([(-.95, s * .4), (-1.28 - sp, s * (.78 + sp))], .15, .12)))
        return ops
    # E virion: round capsid, 10 knobbed spikes; the spike ring turns half a step
    ops = [('add', circ(0, 0, .6, 36))]
    off = math.pi / 10 * f
    for i in range(10):
        a = 2 * math.pi * i / 10 + off
        ca, sa = math.cos(a), math.sin(a)
        ops.append(('add', taper([(.5 * ca, .5 * sa), (.8 * ca, .8 * sa)], .2, .2)))
        ops.append(('add', circ(.9 * ca, .9 * sa, .2, 14)))
    return ops


# ============================================================ B2  CLINICAL: capsule / antibody / syringe
def clinical(t, f):
    if t == 'D':  # pill capsule, one seam cut; tumbles +-10 deg
        pill = [(.6 + .45 * math.cos(math.radians(a)), .45 * math.sin(math.radians(a))) for a in range(-90, 91, 15)] + \
               [(-.6 + .45 * math.cos(math.radians(a)), .45 * math.sin(math.radians(a))) for a in range(90, 271, 15)]
        return rotops([('add', pill), ('ink', rect(.02, -.5, .16, .5))], math.radians(-10 if f == 0 else 10))
    if t == 'N':  # antibody Y: arms lead with bulb ends, stem trails; arms flex open
        y = .62 + .16 * f
        ops = [('add', taper([(-1.05, 0), (.0, 0)], .4, .4))]
        for s in (-1, 1):
            ops.append(('add', taper([(-.05, 0), (.72, s * y)], .4, .32)))
            ops.append(('add', circ(.82, s * y * 1.06, .27, 20)))
        return ops
    # E syringe, chunky: needle leads, barrel with one liquid-window cut, flange, plunger; plunger pushes in
    p = .3 * f
    return [('add', taper([(1.12, 0), (.55, 0)], .1, .22)), ('add', rect(-.5, -.5, .62, .5)), ('add', rect(-.62, -.72, -.46, .72)),
            ('add', rect(-.98 + p, -.15, -.6, .15)), ('add', rect(-1.1 + p, -.5, -.95 + p, .5)),
            ('ink', rect(-.3, -.17, .4 - p * .8, .17))]


# ============================================================ M1  VEHICLES: quad drone / radar dish / tank (top-down or side, 1-2 shapes)
def vehicles(t, f):
    if t == 'D':  # quadcopter: four rotor discs on an X; hover wobble
        ops = [('add', circ(sx * .64, sy * .64, .4, 20)) for sx in (-1, 1) for sy in (-1, 1)]
        ops += [('add', taper([(-.64, -.64), (.64, .64)], .26, .26)), ('add', taper([(-.64, .64), (.64, -.64)], .26, .26)), ('add', circ(0, 0, .4, 20))]
        for sx in (-1, 1):
            for sy in (-1, 1):
                ops.append(('mot', rot(rect(-.34, -.04, .34, .04), math.radians(45 * f + 20) + 0 * sx)))
                ops[-1] = ('mot', [(x + sx * .64, y + sy * .64) for x, y in ops[-1][1]])
        return rotops(ops, math.radians(-7 if f == 0 else 7))
    if t == 'N':  # radar / ECM dish: crescent opens forward, feed arm and focus dot; the dish sweeps
        th = [120 + 120 * i / 18 for i in range(19)]
        outer = [(.35 + 1.15 * math.cos(math.radians(a)), 1.15 * math.sin(math.radians(a))) for a in th]
        inner = [(.62 + 1.0 * math.cos(math.radians(a)), 1.0 * math.sin(math.radians(a))) for a in th][::-1]
        ops = [('add', outer + inner), ('add', rect(-.45, -.1, .42, .1)), ('add', circ(.42, 0, .22, 16))]
        return rotops(ops, math.radians(-16 if f == 0 else 16))
    # E tank: chamfered hull, turret hatch cut, long barrel that recoils; tread dashes only in large size
    rec = .32 * f
    ops = [('add', [(-.95, -.62), (.45, -.62), (.7, -.3), (.7, .3), (.45, .62), (-.95, .62)]),
           ('add', rect(.3, -.14, 1.12 - rec, .14)), ('ink', circ(-.15, 0, .3, 20))]
    for s in (-1, 1):
        for k in range(5):
            x = -.85 + .3 * k + .15 * f
            ops.append(('mot', rect(x, s * .5 - .05, x + .14, s * .5 + .05)))
    return ops


# ============================================================ M2  APP-6 SYMBOLS: air frame + slash / hostile diamond + signal / ground frame + armour oval
def app6(t, f):
    if t == 'D':  # APP-6 air = dome frame, recon slash
        frame = [(-.95, -.9), (-.1, -.9)] + [(-.1 + .9 * math.cos(math.radians(a)), .9 * math.sin(math.radians(a))) for a in range(-80, 81, 10)] + [(-.1, .9), (-.95, .9)]
        sl = taper([(-.7, .55), (.5, -.55)] if f == 0 else [(-.7, -.55), (.5, .55)], .2, .2)
        return [('add', frame), ('ink', sl)]
    if t == 'N':  # hostile diamond, signals bolt
        z = [(-.62, 0), (-.2, -.34), (.1, .34), (.52, 0)]
        z = z if f == 0 else [(x, -y) for x, y in z]
        return [('add', [(1.1, 0), (0, -.95), (-1.1, 0), (0, .95)]), ('ink', taper(z, .2, .2))]
    ry = .34 if f == 0 else .26  # E: ground frame, armour oval (the oval squashes / swells)
    return [('add', [(-1.0, -.78), (.82, -.78), (1.0, -.55), (1.0, .55), (.82, .78), (-1.0, .78)]), ('ink', ell(0, 0, .62, ry))]


FAMILIES = {
    'A': dict(name='R1 A  FRAMES', fn=lambda t, f=0: __import__('shapes_h3').fam_a(t), concept='round 1 reference: triangle / diamond / hexagon', ref=True),
    'B': dict(name='R1 B  DAEMONS', fn=lambda t, f=0: __import__('shapes_h3').fam_b(t), concept='round 1 reference: wasp / serpent / bull', ref=True),
    'H1': dict(name='H1  MALWARE', fn=mk(malware), concept='worm / ghost (rootkit daemon) / logic bomb'),
    'H2': dict(name='H2  EXPLOITS', fn=mk(exploit), concept='zero-day bolt / phishing hook / data cylinder'),
    'B1': dict(name='B1  PATHOGENS', fn=mk(pathogen), concept='bacillus + flagellum / bacteriophage / virion'),
    'B2': dict(name='B2  CLINICAL', fn=mk(clinical), concept='pill capsule / antibody Y / syringe'),
    'M1': dict(name='M1  VEHICLES', fn=mk(vehicles), concept='quad drone / radar dish / tank'),
    'M2': dict(name='M2  APP-6', fn=mk(app6), concept='air dome + slash / hostile diamond + signal / ground frame + armour oval'),
}
NEW = ['H1', 'H2', 'B1', 'B2', 'M1', 'M2']
FILES = {'A': 'ref_A_frames', 'B': 'ref_B_daemons', 'H1': 'family_H1_malware', 'H2': 'family_H2_exploits', 'B1': 'family_B1_pathogens',
         'B2': 'family_B2_clinical', 'M1': 'family_M1_vehicles', 'M2': 'family_M2_app6'}
UNITS = {
    'H1': ['worm: one S body, round head leads, ripples', 'ghost: dome leads, zig-zag hem, two eye cuts', 'logic bomb: heavy ball, fuse, blinking spark'],
    'H2': ['zero-day bolt, tip leads, mirrors on strike', 'phishing hook: thick J, barb, eye ring', 'data cylinder, one disc cut, lid lifts'],
    'B1': ['bacillus rod + waving flagellum', 'bacteriophage: capsid, tail, base plate, legs', 'virion: capsid + 10 knobbed spikes, ring turns'],
    'B2': ['pill capsule, one seam, tumbles', 'antibody Y: arms lead, flex open', 'syringe: needle leads, plunger pushes in'],
    'M1': ['quadcopter: 4 rotor discs on an X, wobbles', 'radar dish: crescent opens forward, sweeps', 'tank: hull, hatch cut, barrel recoils, treads roll'],
    'M2': ['APP-6 air dome + recon slash', 'APP-6 hostile diamond + signals bolt', 'APP-6 ground frame + armour oval'],
    'A': ['triangle', 'diamond + dot', 'hexagon, armour ring'],
    'B': ['wasp', 'serpent', 'bull'],
}
