"""LATENT: card targeting / Tab focus cues, idle-gun NO TARGET. Options A/B/C."""
import sys, math, copy
sys.dont_write_bytecode = True
from a_kit import *
from a_hover import band_brackets, brackets

CUE = (232, 240, 255)


def _cue_band(L, ri, ro, a0, a1, opt, mid=None):
    if opt == 'A':          # quiet hairline corner ticks
        out = []
        for r_edge, rs in ((ri, 1), (ro, -1)):
            for ang, sg in ((a0, 1), (a1, -1)):
                da = 12 / r_edge * 57.3
                out.append([ppx(C, r_edge, ang + sg * da), ppx(C, r_edge, ang), ppx(C, r_edge + rs * 12, ang)])
        for p in out:
            L.line(p, (12, 10, 22, 150), 4.4)
        for p in out:
            L.line(p, CUE + (170,), 2)
    elif opt == 'B':        # one small ring marker in the middle of the target
        x, y = mid
        L.ellipse([x - 9, y - 9, x + 9, y + 9], outline=(12, 10, 22, 170), w=5)
        L.ellipse([x - 9, y - 9, x + 9, y + 9], outline=CUE + (190,), w=2.2)
    else:                   # dashed outline, same trace as the target
        pts = L.band(C, ri, ro, a0, a1)
        L.line(pts + [pts[0]], (12, 10, 22, 130), 4.6)
        L.line(pts + [pts[0]], CUE + (170,), 2, dash=(7, 5))


def _focus_band(L, ri, ro, a0, a1, opt, mid):
    band_brackets(L, ri, ro, a0, a1, 24)
    if opt == 'B':
        x, y = mid
        L.ellipse([x - 9, y - 9, x + 9, y + 9], fill=LIME, outline=INK, w=2.6)


def cues(L, f, kind, opt, focus):
    """kind: unit | slice | ring | tower ; focus = id/sector/ring"""
    if kind == 'unit':
        for u in f['units']:
            if u['consumed'] or u['trigdead']:
                continue
            ri, ro = CB.ring_geom(u['dep'])
            a0, a1 = span(u)
            rm = (ri + ro) / 2
            args = (ri + 4, ro - 4, a0 + 3, a1 - 3)
            mid = ppx(C, rm, (a0 + a1) / 2 + (0 if u['w'] < 6 else 0))
            if u['id'] == focus:
                _focus_band(L, *args, opt, mid)
            else:
                _cue_band(L, *args, opt, mid)
    elif kind == 'slice':
        for w in f['wheel']:
            s = w['sector']
            args = (RS['s0'] + 3, RS['s1'] - 1, 60 * s - 28, 60 * s + 28)
            mid = ppx(C, 100, 60 * s)
            if s == focus:
                _focus_band(L, *args, opt, mid)
            else:
                _cue_band(L, *args, opt, mid)
    elif kind == 'ring':
        for d in range(3):
            ri, ro = CB.ring_geom(d)
            rm = (ri + ro) / 2
            tx, ty = ppx(C, rm, 30)
            lane = LANE[d]
            s = lane['name'] + (' W%d' % (f['rings_wave'][d] + 1) if f['rings_wave'][d] >= 0 else '')
            wd = L.tw(s, 17, 'anton') + 14
            box = (tx - wd / 2 - 5, ty - 17, tx + wd / 2 + 5, ty + 17)
            if d == focus:
                # lime corner brackets on the tag + lime arcs at four quarter points on both ring edges
                x0, y0, x1, y1 = box
                a = 9
                brackets(L, [[(x0, y0 + a), (x0, y0), (x0 + a, y0)], [(x1 - a, y0), (x1, y0), (x1, y0 + a)],
                             [(x0, y1 - a), (x0, y1), (x0 + a, y1)], [(x1 - a, y1), (x1, y1), (x1, y1 - a)]], LIME, 4)
                arcs = []
                for qa in (45, 135, 225, 315):
                    for r_ in (ri + 4, ro - 4):
                        da = 7
                        arcs.append(L.arc_pts(C, r_, qa - da, qa + da, 5))
                brackets(L, arcs, LIME, 5)
            else:
                if opt == 'A':
                    out = []
                    x0, y0, x1, y1 = box
                    for (cx_, cy_, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
                        out.append([(cx_ + sx * 8, cy_), (cx_, cy_), (cx_, cy_ + sy * 8)])
                    for p in out:
                        L.line(p, (12, 10, 22, 150), 4.4)
                    for p in out:
                        L.line(p, CUE + (170,), 2)
                elif opt == 'B':
                    x, y = ppx(C, rm, 30 - (L.tw(s, 17, 'anton') / 2 + 22) / rm * 57.3)
                    L.ellipse([x - 7, y - 7, x + 7, y + 7], outline=(12, 10, 22, 170), w=5)
                    L.ellipse([x - 7, y - 7, x + 7, y + 7], outline=CUE + (190,), w=2.2)
                else:
                    L.rect(box, outline=CUE + (170,), w=2, r=8)
    else:                   # tower: one target, always focused
        R = RS['hub'] + 6
        arcs = []
        for qa in (45, 135, 225, 315):
            arcs.append(L.arc_pts(C, R, qa - 14, qa + 14, 6))
        brackets(L, arcs, LIME, 5.5)
        if opt in ('B', 'C'):
            for qa in (0, 90, 180, 270):
                brackets(L, [[ppx(C, R + 2, qa), ppx(C, R + 12, qa)]], LIME, 4)


def idle_gun(L, f, sector, opt, words=True):
    """the gun at `sector` has no target (hypothetical): drop its tracer, show the dead-end"""
    f2 = copy.deepcopy(f)
    f2['guns'] = [g for g in f['guns'] if g['sector'] != sector]
    gun_tracers10(L, f2)
    a = 60 * sector
    p0, p1 = ppx(C, RS['s1'] + 2, a), ppx(C, RS['c0'] + 14, a)
    L.line([p0, p1], CYAN, 2, dash=(4, 8))
    if opt == 'A':          # terminal tag across the slice rim, horizontal, never in the ring-0 cell
        x, y = ppx(C, 124, a)
        L.rect([x - 56, y - 13, x + 56, y + 13], fill=(6, 12, 24, 245), outline=CYAN, w=2, r=6)
        if words:
            L.text((x, y + 1), 'NO TARGET', 18, 'mono', fill=CYAN)
    elif opt == 'B':        # dead-end: the stub ends in a bar, a barred circle (no word)
        q = ppx(C, RS['c0'] + 14, a)
        perp = a + 90
        L.line([ppx((q[0], q[1]), 0, 0), q], CYAN, 2)
        b0 = (q[0] + 10 * math.cos(math.radians(a)), q[1] + 10 * math.sin(math.radians(a)))
        t0 = ppx(C, RS['c0'] + 14, a - 4.2)
        t1 = ppx(C, RS['c0'] + 14, a + 4.2)
        L.line([t0, t1], INK, 7)
        L.line([t0, t1], CYAN, 3.4)
        x, y = ppx(C, 118, a)
        L.ellipse([x - 13, y - 13, x + 13, y + 13], fill=(6, 12, 24, 245), outline=CYAN, w=2.4)
        L.line([(x - 8, y + 8), (x + 8, y - 8)], CYAN, 2.6)
    else:                   # text along the slice rim, hugging it
        if words:
            L.arc_text(C, 128, a, 'NO TARGET', 18, CYAN, 'mono')
        L.arc_pts(C, 128, a - 20, a + 20, 4)
