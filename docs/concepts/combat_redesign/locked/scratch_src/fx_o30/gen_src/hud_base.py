"""Base layer for the top_hud design work: cutaway backdrop + board + every board mark, NO right-column HUD, NO hand, NO stickers.
Cached per beat in ../cache/base_<beat>.png.  python hud_base.py all"""
import sys, os
sys.dont_write_bytecode = True
from build10 import *
import build10 as B10
from PIL import Image

CACHE = ROOT + 'cache/'
os.makedirs(CACHE, exist_ok=True)
BARE = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v2/room_bio_bare.png'
BEATKEY = {'p1': 'f1', 'nowords': 'f1', 'p2': 'f2', 'p2b': 'f1', 'p3': 'f2'}


def make_base(beat, old_bg=False):
    """same as build10.make() up to header(): returns (base RGBA, frame f)"""
    reg_reset()
    NOW['words'] = beat != 'nowords'
    CB9.HUB['name'] = 'Breaker' if beat != 'nowords' else ''
    f = J[BEATKEY[beat]]
    bg = backdrop() if old_bg else Image.open(BARE).convert('RGBA')
    dim_ids = [u['id'] for u in f['units'] if u['id'] != J['hover']['id']] if beat == 'p2b' else None
    bg.alpha_composite(grade_units(render_board(board_frame(f, keep_all=(beat == 'p2')), CONS), f, keep_all=(beat == 'p2'), dim_ids=dim_ids))
    L = L2()
    O.hp_ring(L, f['hp'], f['pv']['hp_after'], f['maxhp'])
    bezel9(L, f['schedule'])
    O.sector_digits(L)
    occ = {(u['dep'], q) for u in f['units'] for q in sectors(u)}
    for d in range(3):
        for q in range(6):
            if (d, q) not in occ:
                O.cell_border(L, d, q, alpha=70)
    wave_arcs10(L, arcs_data(f))
    ward_arc(L, f)
    tower_slice_bars(L, f)
    if beat in ('p1', 'nowords', 'p2b'):
        threat_trim(L, f)
    dim = None
    if beat == 'p2b':
        hv = J['hover']
        Ld = L2()
        draw_units(Ld, f, skip={hv['id']})
        dim = Ld.done()
        dim.putalpha(dim.split()[3].point(lambda v: int(v * 0.36)))
        Lh = L2()
        draw_units(Lh, f, only={hv['id']})
        hu_ = [u for u in f['units'] if u['id'] == hv['id']][0]
        cell_outline(Lh, hu_, col=YEL, w=5)
        L.im.alpha_composite(Lh.im)
    else:
        draw_units(L, f)
    adjuster_body(L, f['adj'])
    if beat in ('p1', 'nowords'):
        gun_tracers10(L, f)
    if beat != 'p2b':
        landing_arcs(L, f)
    else:
        landing_arcs(L, f, only={J['hover']['id']})
    ring_tags(L, f)
    nudge_ghost(L)
    if beat in ('p2', 'p3'):
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
    if dim is not None:
        bg.alpha_composite(dim)
    bg.alpha_composite(L.done())
    return bg, f


def load_base(beat):
    p = CACHE + 'base_%s.png' % beat
    if not os.path.exists(p):
        im, f = make_base(beat)
        im.save(p)
    NOW['words'] = beat != 'nowords'
    return Image.open(p).convert('RGBA'), J[BEATKEY[beat]]


if __name__ == '__main__':
    import time
    beats = ['p1', 'p2', 'p2b', 'p3', 'nowords'] if sys.argv[1] == 'all' else [sys.argv[1]]
    for b in beats:
        t = time.time()
        im, f = make_base(b)
        im.save(CACHE + 'base_%s.png' % b)
        print(b, 'ok', round(time.time() - t, 1), flush=True)
        if len(sys.argv) > 2:
            im2, _ = make_base(b, old_bg=True)
            im2.save(CACHE + 'base_old_%s.png' % b)
