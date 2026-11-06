import sys, json
sys.dont_write_bytecode = True
import wc_core_opts as CO
import wc_sheet as SH
import wc_base as WB

HUB = (474, 478, 598, 602)
CORE = (376, 380, 696, 700)
RES = {}


def core(cfg):
    return dict(core='wc', cfg=cfg)


def run(only):
    def want(e): return not only or e in only
    if want('hub_disc'):
        RES['hub_disc'] = SH.make_sheet('hub_disc', 'hub_disc: Hub core disc and rim', HUB, [
            ('A', 'Quiet lens: near-black glass, one medium cyan rim, faint TL bevel, ink halo', core(CO.cfg_with(hub=CO.hub_factory(disc='A')))),
            ('B', 'Socket: heavier dimmer rim, dark halo ring separates it from slices', core(CO.cfg_with(hub=CO.hub_factory(disc='B')))),
            ('C', 'CRT dome: scanlines and glint, thinner bright rim', core(CO.cfg_with(hub=CO.hub_factory(disc='C'))))], k=4, beats=('p1',))
    if want('hub_inner_rings'):
        RES['hub_inner_rings'] = SH.make_sheet('hub_inner_rings', 'hub_inner_rings: lens material', HUB, [
            ('A', 'One bevel arc: light TL, shade BR, hairline', core(CO.cfg_with(hub=CO.hub_factory(disc='A', rings='A')))),
            ('B', 'No rings: a soft glass sheen crescent only', core(CO.cfg_with(hub=CO.hub_factory(disc='A', rings='B')))),
            ('C', 'One full hairline lip ring, one step above fill', core(CO.cfg_with(hub=CO.hub_factory(disc='A', rings='C'))))], k=4)
    if want('hub_label'):
        RES['hub_label'] = SH.make_sheet('hub_label', 'hub_label: BREAKER word', HUB, [
            ('A', 'Anton 17 white with ink keyline, clear margin, below the emblem', core(CO.cfg_with(hub=CO.hub_factory(disc='A', rings='A', label='A', emblem='A')))),
            ('B', 'Word demoted: emblem only, nameplate carries the word', core(CO.cfg_with(hub=CO.hub_factory(disc='A', rings='A', label='B', emblem='B')))),
            ('C', 'Word on a small ink chip, mono 16, under the emblem', core(CO.cfg_with(hub=CO.hub_factory(disc='A', rings='A', label='C', emblem='C'))))], k=4, beats=('p1', 'nowords'))
    if want('hub_emblem'):
        RES['hub_emblem'] = SH.make_sheet('hub_emblem', 'hub_emblem: Breaker class emblem', HUB, [
            ('A', 'Cracked ring, cyan engraved', core(CO.cfg_with(hub=CO.hub_factory(disc='A', rings='A', label='A', emblem='A')))),
            ('B', 'Crowbar, class-accent pink at reduced value', core(CO.cfg_with(hub=CO.hub_factory(disc='A', rings='A', label='A', emblem='B')))),
            ('C', 'Wedge splitting a bar, pale steel stencil', core(CO.cfg_with(hub=CO.hub_factory(disc='A', rings='A', label='A', emblem='C'))))], k=4, beats=('p1', 'nowords'))
    if want('slice_frame'):
        RES['slice_frame'] = SH.make_sheet('slice_frame', 'slice_frame: wedge outline', CORE, [
            (k, i, core(CO.cfg_with(tile=CO.FRAME[k]))) for k, i in (('A', 'Fine type-colour edge on the tile outline, ink outside, even r 9 corners, 8 px gutters'),
                                                                   ('B', 'Screen-side hairline pushed heavier, r 12 corners, ink outside'),
                                                                   ('C', 'Lit rail: heavy type-colour edge, slim bezel, glass catch-light'))], k=2)
    if want('slice_screen'):
        RES['slice_screen'] = SH.make_sheet('slice_screen', 'slice_screen: programme screen texture', CORE, [
            (k, i, core(CO.screen_cfg(k, 'A'))) for k, i in (('A', 'Phosphor mesh: one dot grid, value capped 30 percent'),
                                                            ('B', 'Column rain: faint falling streaks'),
                                                            ('C', 'Tinted glass: flat tint, one soft glint'))], k=2)
    if want('slice_screen_code_text'):
        RES['slice_screen_code_text'] = SH.make_sheet('slice_screen_code_text', 'slice_screen_code_text: no legible text', CORE, [
            (k, i, core(CO.screen_cfg('A', k))) for k, i in (('A', 'Sub-8 px pseudo-glyph rows, under 10 percent'),
                                                            ('B', 'Blurred code columns, under 10 percent'),
                                                            ('C', 'Dot-matrix tally rows, no characters'))], k=2, beats=('p1', 'nowords'))
    if want('slice_gutters'):
        RES['slice_gutters'] = SH.make_sheet('slice_gutters', 'slice_gutters: spokes', CORE, [
            (k, i, core(CO.gutter_cfg(k))) for k, i in (('A', '8 px even gutters hub to slice tip'),
                                                       ('B', '8 px strip continues through HP ring and frame'),
                                                       ('C', '8 px strip + engraved hairline spoke through the HP ring'))], k=2)
    for el, reg, name in (('icon_burst', (466, 384, 606, 504), 'BURST'), ('icon_shield', (466, 578, 606, 698), 'SHIELD'), ('icon_turret', (551, 529, 691, 649), 'TURRET'), ('icon_repair', (381, 431, 521, 551), 'REPAIR')):
        if want(el):
            RES[el] = SH.make_sheet(el, el + ': slice icon', reg, [
                (k, i, core(CO.cfg_with(icon_dims=(34, 34), icons=CO.icons_cfg({name: k})))) for k, i in zip('ABC', IDEAS[name])], k=4)
    if want('codebase_frame'):
        RES['codebase_frame'] = SH.make_sheet('codebase_frame', 'codebase_frame: cyan frame', (396, 376, 676, 486), [
            (k, i, core(CO.cfg_with(frame=CO.frame_factory(k)))) for k, i in (('A', 'One fine cyan ring at the HP ring outer edge, ink outside'),
                                                                            ('B', 'Same ring with a bracket tick at each sector boundary'),
                                                                            ('C', 'Six arcs split at the gutters'))], k=2)


IDEAS = {
    'BURST': ['Twin bullets with streaks', 'Pistol profile with two rounds ahead', 'Double-barrel muzzle, front view'],
    'SHIELD': ['Solid heater shield, two pips', 'Round buckler with boss', 'Tall tower shield, two bars'],
    'TURRET': ['Single bullet with streaks', 'Pistol profile with one round', 'Single barrel muzzle, front view'],
    'REPAIR': ['Crossed bandages, pad ring', 'Crossed bandages, plus knocked out', 'One wide strip, pad and perforations'],
}

if __name__ == '__main__':
    run(set(sys.argv[1:]))
    json.dump(RES, open('D:/rc_scratch/e10_design/wheel_core/res1_%s.json' % ('_'.join(sys.argv[1:]) or 'all'), 'w'), indent=1)
