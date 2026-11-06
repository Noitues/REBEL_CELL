"""Wave-rings design pipeline (R1).  render(beat, opts, hud) -> RGB plate on room_bio_bare.
opts = {element_id: 'E'|'A'|'B'|'C'}; E = the approved E10 drawing.  Every element lives in its own function in wr_cells / wr_units / wr_boss / wr_latent.
The unchanged parts of the plate are the E10 generator's own (build10 / e10lib / e9lib / e8lib), imported read-only from this copy."""
import sys, os, json, math
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build10 as B10
from build10 import *            # e10lib * (L2, C, RS, KCOL, ...), header, bill_box ...
import wr_board as WB
import wr_state as ST
import wr_glyphs

ROOM = Image.open('D:/rc_art/art-pass/docs/concepts/combat_backdrop/v2/room_bio_bare.png').convert('RGBA')
WB.HUB["col"] = CYAN
WB.slice_value = lambda w, c: None
_BOARD = {}


def get_board(f, keep_all, units, empties):
    key = (id(f), keep_all, units, empties, NOW['words'])
    if key not in _BOARD:
        WB.HUB['name'] = 'Breaker' if NOW['words'] else ''
        _BOARD[key] = WB.render_board(B10.board_frame(f, keep_all=keep_all), CONS, units=units, empties=empties)
    return _BOARD[key]


_TP0 = [None]


def render(beat='p1', opts=None, hud=False, f_override=None):
    import wr_glyphs as G, e8lib as _E8, wr2_lib as _W2, wr2_glyphs
    saved = {k: v for k, v in KIND.items()}
    if _TP0[0] is None:
        _TP0[0] = _E8.token_pos
    pm = (opts or {}).get('token_placement', 'E')
    import wr_geo as _GEO, wr2_sets as _SETS
    kset = (opts or {}).get('kind_colour_set', 'E')
    saved_kcol = dict(KCOL)
    _GEO.KIND_TABLE.clear()
    if kset != 'E':
        _GEO.KIND_TABLE.update(_SETS.table_for(kset))
        for k_, v_ in _GEO.KIND_TABLE.items():
            KCOL[k_] = tuple(min(255, int(c * _SETS.TOK_F)) for c in v_)
    _E8.token_pos = (lambda u, _m=pm: _W2.token_pos_r2(u, _m)) if pm in ('R', 'V', 'C') else _TP0[0]
    try:
        for el, kind in G.KIND_OF.items():
            o_ = (opts or {}).get(el, 'E')
            KIND[kind] = (KIND[kind][0], G.glyph_name(el, kind, o_))
        return _render(beat, opts, hud, f_override)
    finally:
        KIND.clear(); KIND.update(saved)
        KCOL.clear(); KCOL.update(saved_kcol)
        _GEO.KIND_TABLE.clear()


def _render(beat='p1', opts=None, hud=False, f_override=None):
    """beat p1|p2|p2b|p3|nowords.  f_override = a synthetic frame (latent-element lab) instead of the sim state."""
    import wr_cells as WC, wr_units as WU, wr_boss as WBS
    ST.OPT.clear(); ST.OPT.update(opts or {})
    reg_reset()
    NOW['words'] = beat != 'nowords'
    key = {'p1': 'f1', 'nowords': 'f1', 'p2': 'f2', 'p2b': 'f1', 'p3': 'f2'}[beat]
    f = f_override or J[key]
    keep_all = beat == 'p2'
    bg = ROOM.copy()
    painter = WC.painter_mode()          # does a wr_cells painter replace the programme-screen cells / the dark empty cells?
    prog_units = not painter['units']
    orig_empty = not painter['empties']
    dim_ids = [u['id'] for u in f['units'] if u['id'] != J['hover']['id']] if beat == 'p2b' else None
    board = get_board(f, keep_all, prog_units, orig_empty)
    if prog_units:
        board = grade_units(board, f, keep_all=keep_all, dim_ids=dim_ids)
    if painter['units'] and ST.opt('unit_cell_screen') == 'B':
        ST.PROG = grade_units(get_board(f, keep_all, True, False), f, keep_all=keep_all)
    bg.alpha_composite(board)
    L = L2()
    WC.paint_cells(L, f, beat, painter)           # replaces the master cells where an option asks (separators, empties, unit screens)
    O.hp_ring(L, f['hp'], f['pv']['hp_after'], f['maxhp'])
    bezel9(L, f['schedule'])
    O.sector_digits(L)
    if orig_empty:
        occ = {(u['dep'], q) for u in f['units'] for q in sectors(u)}
        for d in range(3):
            for q in range(6):
                if (d, q) not in occ:
                    O.cell_border(L, d, q, alpha=70)
    wave_arcs10(L, arcs_data(f))
    WBS.ward_arc(L, f)
    tower_slice_bars(L, f)
    if beat in ('p1', 'nowords', 'p2b'):
        threat_trim(L, f)
    dim = None
    if beat == 'p2b':
        hv = J['hover']
        Ld = L2()
        WU.draw_units(Ld, f, beat, skip={hv['id']})
        dim = Ld.done()
        dim.putalpha(dim.split()[3].point(lambda v: int(v * 0.36)))
        Lh = L2()
        WU.draw_units(Lh, f, beat, only={hv['id']})
        hu_ = [u for u in f['units'] if u['id'] == hv['id']][0]
        WU.outline_hover(Lh, hu_)
        L.im.alpha_composite(Lh.im)
    else:
        WU.draw_units(L, f, beat)
    WBS.adjuster(L, f['adj'], beat)
    lab = f.get('_lab')
    if beat in ('p1', 'nowords') and not lab:
        gun_tracers10(L, f)
    if lab:
        pass
    elif beat != 'p2b':
        landing_arcs(L, f)
    else:
        landing_arcs(L, f, only={J['hover']['id']})
    ring_tags(L, f)
    nudge_ghost(L)
    if beat in ('p2', 'p3') and not lab:
        twist_badge(L, f)
        refund_marks(L, f)
    if beat == 'p2':
        for tr in J['trigs']:
            trigger_paths(L, f, dict(tr, entries=[e for e in tr['entries'] if e[0] != 'refund']))
    if beat == 'p2b':
        hover_path(L, f)
    if beat == 'p3':
        for e_ in f['log']:
            if e_[0] == 'fire' and e_[3] is not None:
                s_, dep_ = e_[1], e_[5]
                L.line([ppx(C, RS['s1'] + 3, 60 * s_ + 3), pt(CB.ring_geom(dep_)[0] + 20, 60 * s_, 6)], CYAN + (170,), 2.4, dash=(5, 6))
    if hud:
        header(L, f)
        y = bill_box(L, f, 66, pencil=(beat == 'p2'), plan_tag=('BEST LINE' if beat in ('p2', 'p3') else None), twist_pay=(J['twist_payoff'] if beat in ('p2', 'p3') else None))
        if beat == 'p2':
            y = option_chip(L, y, 'TRIGGER ONLY', J['meta']['lines']['trigger'][0], J['meta']['lines']['trigger'][1], J['f2t']['pv']['eq'], refund=J['f2t']['refunds'] > 0)
            y = option_chip(L, y, 'BRACE + SOAK ONLY', J['meta']['lines']['brace'][0], J['meta']['lines']['brace'][1], J['f2b']['pv']['eq'])
            y = option_chip(L, y, 'BEST: ALL THREE', J['meta']['hero'], J['meta']['hero_end'], f['pv']['eq'], sel=True, refund=f['refunds'] > 0)
        elif beat == 'p3':
            y = chain_strip(L, f, y)
        y = stars_row(L, f, y + 2)
        y = ram_trace(L, f, y)
    base = bg
    if dim is not None:
        base.alpha_composite(dim)
    base.alpha_composite(L.done())
    if hud:
        f1 = J['f1']
        played = [a[0] for a in f['played']]
        hand = list(f['hand'])
        if beat == 'p3':
            hand = list(f1['hand'])
            for c_ in played:
                hand.remove(c_)
        hover_i = hand.index('Trigger') if beat == 'p2' else None
        CH.hand(base, hand, x0=1000, hover=hover_i, played=played if beat == 'p3' else (), cy0=948)
        L3 = L2()
        stickers(base, L3)
        if beat == 'p2b':
            hover_tag(L3, f)
        base.alpha_composite(L3.done())
    return base.convert('RGB')


if __name__ == '__main__':
    import time
    t = time.time()
    b = sys.argv[1] if len(sys.argv) > 1 else 'p1'
    im = render(b, {}, hud=(len(sys.argv) > 2))
    im.save(ROOT + 'out/base_%s.png' % b)
    print('t', time.time() - t)
