import sys, json
sys.dont_write_bytecode = True
import wc_over_opts as OO
import wc_sheet as SH
import wc_base as WB

CORE = (376, 380, 696, 700)
RES = {}


def st(fam=None, brk='cur'):
    return dict(sel={'slice_stage': OO.stage_factory(fam or 'cur', brk)})


def run(only):
    def want(e): return not only or e in only
    FAM = [('A', 'Solid grammar, round caps: slashed red, notched indigo, plus-outline mend, empty socket'),
           ('B', 'Hollow-means-lost: red/indigo outlines, dashed mend outline, quiet socket'),
           ('C', 'Butt-capped plates on a slim inner track: hatch / notch / outline plus')]
    if want('slice_hp_bars'):
        RES['slice_hp_bars'] = SH.make_sheet('slice_hp_bars', 'slice_hp_bars: capsule set (showcase state = all five pip states)', CORE,
                                             [(k, i, st(k)) for k, i in FAM], k=2, show=OO.show_slices, state_key='show')
    low = (396, 560, 676, 700)
    if want('slice_pip_lost_harm'):
        RES['slice_pip_lost_harm'] = SH.make_sheet('slice_pip_lost_harm', 'slice_pip_lost_harm: lost to harm', low,
                                                   [(k, i, st(k)) for k, i in zip('ABC', ['Red capsule + white slash, ink under', 'Hollow red outline + red slash', 'Red plate + three hatch strokes'])], k=2)
    if want('slice_pip_lost_soak'):
        RES['slice_pip_lost_soak'] = SH.make_sheet('slice_pip_lost_soak', 'slice_pip_lost_soak: lost to soak (p2, SHIELD sector 1)', (546, 400, 706, 580),
                                                   [(k, i, st(k)) for k, i in zip('ABC', ['Indigo capsule with an ink chevron notch (proposed SOAK token)', 'Hollow indigo outline with an inward chevron', 'Indigo plate with a triangular notch'])], k=3, beats=('p2',))
    if want('slice_pip_mend'):
        RES['slice_pip_mend'] = SH.make_sheet('slice_pip_mend', 'slice_pip_mend (LATENT, showcase sector 3)', (456, 600, 616, 700),
                                              [(k, i, st(k)) for k, i in zip('ABC', ['Green outline capsule with plus', 'Dashed green outline with plus', 'Outlined plate with plus'])], k=3, show=OO.show_slices, state_key='show')
    if want('slice_pip_gone'):
        RES['slice_pip_gone'] = SH.make_sheet('slice_pip_gone', 'slice_pip_gone (LATENT, showcase sector 0)', (456, 400, 616, 470),
                                              [(k, i, st(k)) for k, i in zip('ABC', ['Dark socket capsule, hairline', 'Hairline outline only', 'Hairline plate outline'])], k=3, show=OO.show_slices, state_key='show')
    if want('slice_break_x'):
        RES['slice_break_x'] = SH.make_sheet('slice_break_x', 'slice_break_x: breaks this turn', (546, 420, 706, 660),
                                             [(k, i, st('A', k)) for k, i in zip('ABC', ['Heavy corner X off the icon + hatch dim of the wedge', 'Dim preview + badge disc with X at the hub corner', 'Hazard stripes on the outer third + corner X'])], k=2, beats=('p1',))
    if want('slice_soak_break_x'):
        RES['slice_soak_break_x'] = SH.make_sheet('slice_soak_break_x', 'slice_soak_break_x (p2, sector 1)', (546, 400, 706, 580),
                                                  [(k, i, st('A', k)) for k, i in zip('ABC', ['Same corner X + hatch, soak token indigo', 'Same badge X, soak token indigo', 'Same stripes, soak token indigo'])], k=3, beats=('p2',))
    if want('threat_trim'):
        RES['threat_trim'] = SH.make_sheet('threat_trim', 'threat_trim: now / next / later', CORE,
                                           [(k, i, dict(sel={'threat_trim': OO.trim_factory(k)})) for k, i in zip('ABC', ['Fixed thirds of the slice rim: later | next | now', 'One lane, highest priority full length, extra threats as end beads', 'Three stacked lanes inside the wedge rim, shorter for later'])], k=2, beats=('p1', 'p2b'))
    if want('hp_ring'):
        RES['hp_ring'] = SH.make_sheet('hp_ring', 'hp_ring: 15 HP', CORE,
                                       [(k, i, dict(sel={'hp_ring': OO.hp_ring_factory(k)})) for k, i in zip('ABC', ['6 px segments in groups of 5, red + white slash', 'Hollow red lost segments, 8 px', 'Thin 5 px ring, groups of 5'])], k=2)
    if want('nudge_ghost'):
        RES['nudge_ghost'] = SH.make_sheet('nudge_ghost', 'nudge_ghost', (456, 330, 616, 430),
                                           [(k, i, dict(sel={'nudge': OO.nudge_factory(k)})) for k, i in zip('ABC', ['Removed (3.22 Open note)', 'Hollow cyan chevrons engraved on the bezel at the needle', 'Dim engraved chevrons, 40 percent'])], k=3)
    gr = (376, 520, 576, 700)
    if want('gun_tracers'):
        RES['gun_tracers'] = SH.make_sheet('gun_tracers', 'gun_tracers', gr, [(k, i, dict(sel={'guns': OO.guns_factory(k)})) for k, i in zip('ABC', ['Dash 12/6 ends on the target cell centre', 'Solid core line, ink edge', 'Short dash 6/5'])], k=2)
    if want('gun_result_hit'):
        RES['gun_result_hit'] = SH.make_sheet('gun_result_hit', 'gun_result_hit', gr, [(k, i, dict(sel={'guns': OO.guns_factory(k)})) for k, i in zip('ABC', ['White 8-point spark 18 px with ink', 'Same spark on a solid core line', 'Spark 20 px, short dash'])], k=3)


if __name__ == '__main__':
    run(set(sys.argv[1:]))
    json.dump(RES, open('D:/rc_scratch/e10_design/wheel_core/res2_%s.json' % ('_'.join(sys.argv[1:]) or 'all'), 'w'), indent=1)


def run3(only):
    def want(e): return not only or e in only
    gr = (300, 500, 500, 690)
    if want('gun_result_armor') or want('gun_result_ward') or want('gun_result_shield_pop'):
        for eid, idea in (('gun_result_armor', 'steel ricochet'), ('gun_result_ward', 'gold ricochet'), ('gun_result_shield_pop', 'cyan pop burst')):
            if want(eid):
                RES[eid] = SH.make_sheet(eid, eid + ' (LATENT, showcase: armor / shield / ward on the three guns)', gr,
                                         [('A', idea + ', 24 px, ink, same family as the hit spark', dict(sel={'guns': OO.results_factory('A')})),
                                          ('B', idea + ', same spark footprint', dict(sel={'guns': OO.results_factory('B')})),
                                          ('C', idea + ', variant', dict(sel={'guns': OO.results_factory('C')}))], k=2, show=OO.show_guns, state_key='guns')
    if want('gun_tracer_burst_pair'):
        RES['gun_tracer_burst_pair'] = SH.make_sheet('gun_tracer_burst_pair', 'gun_tracer_burst_pair', (376, 520, 576, 700),
                                                     [(k, i, dict(sel={'guns': OO.burst_pair_factory(k)})) for k, i in zip('ABC', ['Two small muzzle beads, tracer sized', 'Two short bars on the rim', 'Two inward ticks'])], k=2)
