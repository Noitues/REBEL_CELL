"""R2 card_targeting (white hairline corner ticks for valid, focus_brackets for the focused target, + the Adjuster-as-target view) and no_target_tag."""
import sys, math, copy
sys.dont_write_bytecode = True
from a2_kit import *
from a2_stick import kit_plate
import a2_plan as PL2

CUE = (232, 240, 255)


def ticks(L, geom, opt='A'):
    """valid-target cue: four 12 px white hairline corner ticks (A); A2 adds a 1.4 px outline at 30 percent"""
    arms, frame, _ = fb_arms(geom[0], geom[1], arm=14, grow=0)
    if opt == 'A2':
        L.line(frame, CUE + (80,), 1.4)
    for p in arms:
        L.line(p, INK + (200,), 5.6)
    for p in arms:
        L.line(p, CUE + (240,), 2.6)


def unit_geom(u):
    ri, ro = CB.ring_geom(u['dep'])
    a0, a1 = span(u)
    return ('band', dict(ri=ri + 4, ro=ro - 4, a0=a0 + 3, a1=a1 - 3))


def adj_geom(f):
    a = f['adj']
    ri, ro = CB.ring_geom(a['ring'])
    return ('band', dict(ri=ri + 4, ro=ro - 4, a0=60 * a['s'] - 28, a1=60 * a['s'] + 28))


def cues(L, f, kind, opt, focus, fopt='A', adj_valid=True):
    """kind: unit | slice | ring | tower | adjuster.  focus = unit id / sector / ring / 'adj'."""
    if kind in ('unit', 'adjuster'):
        for u in f['units']:
            if u['consumed'] or u['trigdead']:
                continue
            g = unit_geom(u)
            if u['id'] == focus:
                focus_brackets(L, *g, fopt, arm=24, grow=0)
            else:
                ticks(L, g, opt)
        if adj_valid:
            g = adj_geom(f)
            if focus == 'adj':
                focus_brackets(L, *g, fopt, arm=24, grow=0)
            else:
                ticks(L, g, opt)
    elif kind == 'slice':
        for w in f['wheel']:
            s = w['sector']
            g = ('band', dict(ri=RS['s0'] + 3, ro=RS['s1'] - 1, a0=60 * s - 28, a1=60 * s + 28))
            if s == focus:
                focus_brackets(L, *g, fopt, arm=22, grow=0)
            else:
                ticks(L, g, opt)
    elif kind == 'ring':
        for d in range(3):
            ri, ro = CB.ring_geom(d)
            x, y, wd, _, _ = PL2.tag_geom(L, d, f['rings_wave'][d])
            box = (x - wd / 2, y - 13, x + wd / 2, y + 13)
            if d == focus:
                focus_brackets(L, 'rect', dict(box=box), fopt, arm=9, grow=4)
                arcs = []
                for qa in (45, 135, 225, 315):
                    for r_ in (ri + 4, ro - 4):
                        arcs.append(L.arc_pts(C, r_, qa - 7, qa + 7, 5))
                for p in arcs:
                    L.line(p, INK, 8.5)
                for p in arcs:
                    L.line(p, LIME, 4)
            else:
                ticks(L, ('rect', dict(box=box)), opt)
    else:                   # tower: one target, always focused
        R = RS['hub'] + 6
        arcs = [L.arc_pts(C, R, qa - 14, qa + 14, 6) for qa in (45, 135, 225, 315)]
        for p in arcs:
            L.line(p, INK, 9.5)
        for p in arcs:
            L.line(p, LIME, 5)


# ---------------------------------------------------------------------------- no_target_tag (LATENT hypothetical: the gun at `sector` has no target)
def tag_img(words=True):
    s = 'NO TARGET'
    w, h, S = 112, 26, 3
    L = L2()
    return w, h


def idle_gun(L, f, sector, opt='A', words=True):
    f2 = copy.deepcopy(f)
    f2['guns'] = [g for g in f['guns'] if g['sector'] != sector]
    gun_tracers10(L, f2)
    a = 60 * sector
    p0, p1 = ppx(C, RS['s1'] + 2, a), ppx(C, RS['c0'] + 14, a)
    L.line([p0, p1], INK + (90,), 3.4, dash=(4, 8))
    L.line([p0, p1], CYAN + ((102 if opt == 'A' else 150),), 1.4, dash=(4, 8))
    if words:
        # tag lies along the slice rim (tangent), centred on r 140: stays between the slice and the ring cells, never over a cell
        w, h = 116, 26
        sub = L2()
        kit_plate(sub, (100, 100, 100 + w, 100 + h), CYAN, 2, 6)
        sub.text((100 + w / 2, 100 + h / 2 + 1), 'NO TARGET', 18, 'mono', fill=CYAN)
        im = sub.im.crop((196, 196, 204 + 2 * w, 204 + 2 * h))
        im = im.crop((0, 0, im.width, im.height))
        # tangent angle in screen space; keep text upright on the lower half
        x, y = ppx(C, 140, a)
        rot = -(math.degrees(math.atan2(y - C[1], x - C[0])) + 90)
        rot = (rot + 180) % 360 - 180
        if abs(rot) > 90:
            rot += 180
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
        L.im.alpha_composite(im, (int(x * 2 - im.width / 2), int(y * 2 - im.height / 2)))
