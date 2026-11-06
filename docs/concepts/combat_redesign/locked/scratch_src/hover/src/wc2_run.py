"""R2 assembler: ONE function builds any beat from a dict of element choices (PICKS + overrides)."""
import sys, os, json, time
sys.dont_write_bytecode = True
import wc2 as E
import wc_base as WB
from wc_base import *

OUT = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/r2/wheel_core/'
os.makedirs(OUT + 'crops', exist_ok=True)

PICKS = dict(frame='A', screen='A', hub_disc='A', hub_rings='A', hub_label='A', crest='A', burst='B', turret='A', repair='P', cfr='A',
             bars='A', brk='A', soakx='A', trim='A', hpring='A', guns=dict(pop='arcs', wall=False), brace='A', soakmark='A', soakrim='A',
             cracked='A', broken='A', idle='A', preview='A', spin=None)


def make_cfg(o):
    tile = E.tile2(o['frame'], E.tex_phosphor(lift=0.05) if o['screen'] == 'B' else None)
    return E.cfg2(tile=tile, hub=E.hub_factory(o['hub_disc'], o['hub_rings'], o['hub_label'], o['crest']), frame=E.frame2(o['cfr']),
                  icons=E.icons2(o['burst'], o['turret'], o['repair']))


def stage_fn(o):
    bars = E.bars2()
    brk = E.break_x(o['brk'])
    sbrk = E.break_x(o['soakx'] if o['soakx'] != 'A' else 'A', soak=True)
    brace = E.brace_plate2(o['brace']); smark = E.soak_mark2(o['soakmark']); srim = E.soak_rim2(o['soakrim'])
    cr = E.cracked2(o['cracked']); bk = E.broken2(o['broken'])
    GN = {'BURST': 'WC2_BURST_B', 'TURRET': 'WC2_TURRET_A', 'REPAIR': 'WC2_REPAIR_P'}

    def stage(L, f):
        for w in f['wheel']:
            s = w['sector']; hp = w['hp']; ha = w.get('hp_after', hp)
            if hp == 0:
                bk(L, s, GN.get(w['t'])); continue
            if ha == 0:
                (sbrk if w.get('soaked') else brk)(L, s, 'pre')
            bars(L, w, s)
            if ha == 0:
                (sbrk if w.get('soaked') else brk)(L, s, 'post')
            elif hp < w['mx'] and ha == hp:
                cr(L, s)
            if w.get('brace'): brace(L, s)
            if w.get('soak'):
                smark(L, s); srim(L, s)
    return stage


def sel_for(o, beat):
    sel = {'slice_stage': stage_fn(o), 'threat_trim': E.trim2(o['trim']), 'hp_ring': E.hp_ring2(o['hpring']), 'nudge': lambda L: None}
    g = o['guns']
    sel['guns'] = E.guns2(pop=g.get('pop', 'arcs'), wall=g.get('wall', False), idle=o['idle'])
    pv = E.guns_preview(o['preview'], o['idle']) if o['preview'] else (lambda L, f: None)
    sel['p2guns'] = pv
    sel['p3guns'] = pv
    return sel


def plate(beat, over=None, show=None, extras=None, state=None):
    o = dict(PICKS); o.update(over or {})
    sel = sel_for(o, beat)
    if o.get('idle_fn'):
        pass
    if extras:
        sel['extras'] = extras
    return WB.render(beat, sel=sel, core='wc', cfg=make_cfg(o), show=show, state=state)


if __name__ == '__main__':
    t = time.time()
    for beat in sys.argv[1:] or ['p1']:
        im = plate(beat)
        im.convert('RGB').save(OUT + 'plate_picks_%s.png' % beat)
        print(beat, time.time() - t, flush=True)
