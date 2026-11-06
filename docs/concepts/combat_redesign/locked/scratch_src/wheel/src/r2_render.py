"""R2 assembler for the outer_rings cluster: one function render_r2(beat, sel) draws the E10 plate (p1 / p2 / p2b / p3 / nowords) on room_bio_bare with this cluster's
R2 drawings.  Selectors default to the R2 pick 'P'; 'V' is the variant.  The other clusters' content comes from the same cached E10 core + HUD layers (unchanged)."""
import sys, os, copy, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
import render as R1R
import build10 as B10
from e10lib import *
import e10lib as E
import cv_board as CB9
import cv_over as O
import r2_ground as G2
import r2_sched as S2
import r2_arcs as A2
import r2_misc as M2

J = B10.J
BEATS = R1R.BEATS
_gc = {}


def ground(sel):
    key = (sel.get('grade', 'P'), sel.get('scrim', 'P'), sel.get('plate', 'P'), sel.get('bezel', 'P'), sel.get('rim', 'P'))
    if key not in _gc:
        bg = G2.backdrop(key[0], key[1])
        bg.alpha_composite(G2.plate(key[2]).convert('RGBA'))
        bg.alpha_composite(G2.bezel_layer(key[3], key[4]).convert('RGBA'))
        _gc[key] = bg
    return _gc[key].copy()


def twist_badge(L, f, sel):
    ring, dirn = f['twr']
    if not dirn:
        return
    ax, ay = M2.tag_anchor(L, f, ring)
    bx, by = ax + 22, ay
    L.ellipse([bx - 17, by - 17, bx + 17, by + 17], fill=(26, 22, 4, 250), outline=YEL, w=3)
    L.glyph('C_TWIST', 24, (bx, by), YEL)
    for q in (0, 1):
        xx = bx + 25 + q * 9
        L.line([(xx - 4, by - 8), (xx + 4, by), (xx - 4, by + 8)], INK, 6.5)
        if q == 0 or abs(dirn) > 1:
            L.line([(xx - 4, by - 8), (xx + 4, by), (xx - 4, by + 8)], YEL, 3.4)


def render_r2(beat='p1', sel=None, sched=None, hud=True, rings_wave=None, region=None, tags_only=False):
    sel = dict(sel or {})
    NOW['words'] = beat != 'nowords'
    E.reg_reset()
    CB9.HUB['name'] = 'Breaker' if beat != 'nowords' else ''
    f = copy.deepcopy(J[BEATS[beat]])
    if sched is not None:
        f['schedule'] = list(sched)
    if rings_wave is not None:
        f['rings_wave'] = list(rings_wave)
    bg = ground(sel)
    bg.alpha_composite(R1R.core_layer(beat, f))
    L = L2()
    O.hp_ring(L, f['hp'], f['pv']['hp_after'], f['maxhp'])
    S2.schedule(L, f['schedule'], sel)
    S2.digits(L, sel.get('digits', 'P'))
    S2.needle(L, sel.get('needle', 'P'))
    occ = {(u['dep'], q) for u in f['units'] for q in sectors(u)}
    for d in range(3):
        for q in range(6):
            if (d, q) not in occ:
                O.cell_border(L, d, q, alpha=70)
    M2.future(L, f, B10.arcs_data(f), sel)
    ward_arc(L, f)
    tower_slice_bars(L, f)
    if beat in ('p1', 'nowords', 'p2b'):
        threat_trim(L, f)
    dim = None
    if beat == 'p2b':
        hv = J['hover']
        Ld = L2()
        B10.draw_units(Ld, f, skip={hv['id']})
        dim = Ld.done()
        dim.putalpha(dim.split()[3].point(lambda v: int(v * 0.36)))
        Lh = L2()
        B10.draw_units(Lh, f, only={hv['id']})
        hu_ = [u for u in f['units'] if u['id'] == hv['id']][0]
        cell_outline(Lh, hu_, col=YEL, w=5)
        L.im.alpha_composite(Lh.im)
    else:
        B10.draw_units(L, f)
    adjuster_body(L, f['adj'])
    if beat in ('p1', 'nowords'):
        gun_tracers10(L, f)
    if beat != 'p2b':
        A2.landing_arcs(L, f, sel)
    else:
        A2.landing_arcs(L, f, sel, only={J['hover']['id']})
    M2.ring_tags(L, f, sel.get('rtags', 'P'))
    B10.nudge_ghost(L)
    if beat in ('p2', 'p3'):
        twist_badge(L, f, sel)
        B10.refund_marks(L, f)
    if beat == 'p2':
        for tr in J['trigs']:
            B10.trigger_paths(L, f, dict(tr, entries=[e for e in tr['entries'] if e[0] != 'refund']))
    if beat == 'p2b':
        B10.hover_path(L, f)
    if beat == 'p3':
        for e_ in f['log']:
            if e_[0] == 'fire' and e_[3] is not None:
                s_, dep_ = e_[1], e_[5]
                L.line([ppx(C, RS['s1'] + 3, 60 * s_ + 3), pt(CB.ring_geom(dep_)[0] + 20, 60 * s_, 6)], CYAN + (170,), 2.4, dash=(5, 6))
    if dim is not None:
        bg.alpha_composite(dim)
    bg.alpha_composite(L.done())
    if hud:
        bg.alpha_composite(R1R.hud_overlay(beat, f))
    if sched is None and rings_wave is None:
        try:
            B10.draw_asserts(beat, f)
        except AssertionError as e:
            print('DRAW ASSERT FAIL', beat, e, flush=True)
            raise
    img = bg.convert('RGB')
    if region:
        img = img.crop(region)
    return img


def render_full_circle(sel=None, with_digits=True):
    """LATENT landing_arc_full_circle: ground + schedule bezel + one width-6 Ring arc on lane 0, no core, no HUD"""
    sel = dict(sel or {})
    NOW['words'] = True
    E.reg_reset()
    f = copy.deepcopy(J['f1'])
    f['units'] = []
    bg = ground(sel)
    L = L2()
    S2.schedule(L, f['schedule'], sel)
    if with_digits:
        S2.digits(L, sel.get('digits', 'P'))
        S2.needle(L, sel.get('needle', 'P'))
    A2.landing_arcs(L, f, sel, extra=[A2.full_circle_unit()])
    bg.alpha_composite(L.done())
    return bg.convert('RGB')


FAVP = {}


if __name__ == '__main__':
    import time
    t = time.time()
    im = render_r2('p1')
    im.save(ROOT + 'test_r2_p1.png')
    print('ok', time.time() - t)
