"""asm_r2: ONE generator for the E10 combat screen redesign (all seven clusters' FINAL elements).  render(beat) -> RGB 1920x1080.
beats: p1 (p1_decide), p2 (p2_preview), p2b (p2b_hover), p3 (p3_resolve), nowords (p1_nowords).  Game content is the E10 sim state, unchanged.
Layer order follows DECISIONS.md 5.2 (see the comments); build10's z-order and beat logic are kept."""
import sys, os, copy, math, json
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter

import asm_tokens as TK
import build10 as B10
from build10 import *
import e10lib as E
import e8lib as E8
import cv_board as CB9
import asm_glyphs as AG
import wr_state as ST
import wr_geo as GEO
import wr2_picks, wr2_sets
import wr2_lib as W2L
import wr2_cells as W2C
import wr2_boss as W2B
import wr2_units as W2U
import wr_cells as WCL
import wr_latent as WLT
import asm_units as AU
import wc2, wc2_run as WCR, wc_tower as T
import r2_ground as G2
import o_ground as OG
import r2_sched as S2
import r2_arcs as A2
import r2_misc as M2
import hud2, obj2
import kscene2, kcard2
import a_plan as PL
import a_hover as HV
import a2_kit as K2
import a2_stick as AS
import a2_plan as P2
import a2_hover as H2

J = B10.J
BEATKEY = {'p1': 'f1', 'nowords': 'f1', 'p2': 'f2', 'p2b': 'f1', 'p3': 'f2'}
OUTNAME = {'p1': 'p1_decide', 'p2': 'p2_preview', 'p2b': 'p2b_hover', 'p3': 'p3_resolve', 'nowords': 'p1_nowords'}
ROOM_BIO = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v2/room_bio_bare.png'
DIM_K = 0.38
INFO = {}
_ready = [False]


def setup():
    if _ready[0]:
        return
    # R2 wave-ring picks, kind colour set R (Y6), kglyph2 names for the unit tokens (Y3)
    ST.OPT.clear(); ST.OPT.update(wr2_picks.R2)
    GEO.KIND_TABLE.clear(); GEO.KIND_TABLE.update(wr2_sets.table_for('R'))
    for k_, v_ in GEO.KIND_TABLE.items():
        KCOL[k_] = tuple(min(255, int(c * TK.KIND_TOKEN_F)) for c in v_)
    for kind in AG.KIND_ID:
        KIND[kind] = (KIND[kind][0], AG.kind_name(kind))
    # wheel_core PICKS (DECISIONS 3.1)
    P = WCR.PICKS
    P.update(burst='B', turret='A', repair='P', soakx='B', brace='C', preview='B', trim='A', hpring='A', soakmark='A', soakrim='A', idle='A')
    P['guns'] = dict(pop='shards', wall=False)
    CB9.HUB['col'] = CYAN
    _ready[0] = True


def set_room(path):
    OG.BARE_PATH = path
    OG._bare = None
    G2.BARE_PATH = path if hasattr(G2, 'BARE_PATH') else path


# ----------------------------------------------------------------------------- helpers
def sub_frame(f, units):
    g = dict(f)
    g['units'] = units
    return g


def draw_units(L, f, beat, only=None, skip=None):
    for u in f['units']:
        if only is not None and u['id'] not in only:
            continue
        if skip is not None and u['id'] in skip:
            continue
        if u['consumed'] or u['trigdead']:
            W2U.ghost(L, u, 'consumed' if u['consumed'] else 'killed', beat)
            continue
        if u['w'] == 6:
            WLT.wide6(L, u, f)
            continue
        AU.draw_unit(L, u, f, beat)


def paint_cells(L, f, beat, which=None, with_base=True):
    """ring cells: gutter bed, empty cells (the Adjuster cell is drawn by wr2_boss.cell instead), unit screens, interior hairlines"""
    if with_base:
        W2C.gutters(L, f)
        cov = WCL.covered(f)
        for dep in range(3):
            for s in range(6):
                if (dep, s) not in cov:
                    W2C.empty_cell(L, dep, s)
    lu = [u for u in WCL.live_units(f) if which is None or u['id'] in which]
    for u in lu:
        W2C.screen(L, u)
    W2C.interior_hairlines(L, sub_frame(f, lu))


def tower_layer(f, nowords):
    o = dict(WCR.PICKS)
    cfg = WCR.make_cfg(o)
    tw = T.render_core(f['wheel'], cfg, ss=3, nowords=nowords)
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).ellipse([C[0] - 160, C[1] - 160, C[0] + 160, C[1] + 160], fill=255)
    m = ImageChops.multiply(m.filter(ImageFilter.GaussianBlur(0.6)), tw.split()[3])
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lay.paste(tw, (0, 0), m)
    return lay


def hover_trim(L, f, sel, hid):
    fz = sub_frame(f, [u for u in f['units'] if u['id'] != hid])
    sel['threat_trim'](L, fz)


def hover_slice(L, f):
    """hover_slice_highlight A (actions look: a yellow rim arc in the trim slot) at the new trim radius of wheel_core (R 139.5)"""
    R = 139.5
    for sec in HV.hover_sectors(f):
        a0, a1 = 60 * sec - 25, 60 * sec + 25
        L.line(L.arc_pts(C, R, a0, a1), INK, 10)
        L.line(L.arc_pts(C, R, a0, a1), YEL, 5.5)


# ----------------------------------------------------------------------------- the assembler
def render(beat='p1', room=None, check=True):
    setup()
    set_room(room or ROOM_BIO)
    words = beat != 'nowords'
    NOW['words'] = words
    E.reg_reset()
    AU.BADGE_LOG.clear()
    CB9.HUB['name'] = 'Breaker' if words else ''
    f = copy.deepcopy(J[BEATKEY[beat]])
    hover = beat == 'p2b'
    hid = J['hover']['id']
    o = dict(WCR.PICKS)
    sel = WCR.sel_for(o, beat)

    # --- HUD layer first (its bottom decides the scrim slab)
    Lhud = L2()
    hb = 'p1' if beat in ('nowords', 'p2b') else beat
    bottom = hud2.draw_hud(Lhud, f, hb, None)
    INFO['hud_bottom'] = bottom
    INFO['hud_boxes'] = dict(hud2.R)

    # --- 1. backdrop: room -> grade P -> scrim P -> hud scrim slabs
    bg = G2.backdrop('P', 'P')
    hud2.scrim_layers(bg, bottom)
    # --- 2. board plate, bezel (+ track, spokes), the tower disc
    bg.alpha_composite(G2.plate('P').convert('RGBA'))
    bg.alpha_composite(G2.bezel_layer('P').convert('RGBA'))
    bg.alpha_composite(tower_layer(f, not words))

    L = L2()
    sel['hp_ring'](L, f['hp'], f['pv']['hp_after'], f['maxhp'])
    wc2.spokes(L)                                   # r44-162; wr2 gutters take over at r161 (Y15)
    S2.schedule(L, f['schedule'], {})
    S2.digits(L, 'P')
    S2.needle(L, 'P')
    # --- 3. ring cells
    others = {u['id'] for u in f['units'] if u['id'] != hid} if hover else None
    if hover:
        paint_cells(L, f, beat, which={hid})
        Ld = L2()
        paint_cells(Ld, f, beat, which=others, with_base=False)
    else:
        paint_cells(L, f, beat)
        Ld = None
    for k_ in range(6):          # fix 8 (Y15): the 8 px bezel spoke is drawn AFTER the schedule cells and the ring-cell gutters (which end at r353): r353-360 continuous on all six angles
        a_ = 60 * k_ + 30
        L.line([ppx(C, G2.BZ0 - 0.5, a_), ppx(C, G2.BZ1 + 0.5, a_)], INK, 8)
    M2.future(L, f, B10.arcs_data(f), {})          # future tape, unit pips, hazard ticks, wave tags
    W2B.ward_arc(L, f)
    # --- 5a. tower marks that sit on the disc: bars, pips, break X, soak marks, brace plate, trim
    sel['slice_stage'](L, f)
    if beat in ('p1', 'nowords'):
        sel['threat_trim'](L, f)
    elif hover:
        hover_trim(L, f, sel, hid)
    # --- 4. units
    if hover:
        draw_units(Ld, f, beat, skip={hid})
        draw_units(L, f, beat, only={hid})
    else:
        draw_units(L, f, beat)
    W2B.adjuster(L, f['adj'], beat)
    # --- 5b. guns
    if beat in ('p1', 'nowords'):
        sel['guns'](L, f)
    elif beat in ('p2', 'p3'):
        sel['p2guns'](L, f)
    # --- 6. landing arcs, ring tags
    if hover:
        A2.landing_arcs(Ld, sub_frame(f, [u for u in f['units'] if u['id'] in others]), {}, only=others)
        A2.landing_arcs(L, f, {}, only={hid})
    else:
        A2.landing_arcs(L, f, {})
    if not hover:
        M2.ring_tags(L, f, 'P')
    # --- 7. actions overlays
    if beat in ('p2', 'p3'):
        P2.twist_badge(L, f, 'A')
        if f.get('refunds'):
            P2.refund_place(L, f, 'A', 'A', words)
    if beat == 'p2':
        for tr in J['trigs']:
            PL.trigger_path(L, f, dict(tr, entries=[e for e in tr['entries'] if e[0] != 'refund']), 'A')
    bg.alpha_composite(L.done())
    Lsp = L2()                   # fix 8 (Y15), final pass: a separate layer above the board layer (its glow pass tinted r354 on 330 deg): the 8 px spoke is continuous across r353-360
    for k_ in range(6):
        a_ = 60 * k_ + 30
        Lsp.line([ppx(C, G2.BZ0 - 0.5, a_), ppx(C, G2.BZ1 + 0.5, a_)], INK, 8)
    bg.alpha_composite(Lsp.done())
    if hover:
        d = Ld.done()
        d.putalpha(d.split()[3].point(lambda v: int(v * DIM_K)))
        bg.alpha_composite(d)
        Lh = L2()
        hover_slice(Lh, f)
        H2.hover_path(Lh, f, 'A')
        H2.hover_cell(Lh, f, 'A', w=K2.FB_W)
        M2.ring_tags(Lh, f, 'P')      # tags above the dim veil: they stay readable
        bg.alpha_composite(Lh.done())
    # --- 8. HUD
    bg.alpha_composite(Lhud.done())
    # --- 9. hand
    V = dict(kcard2.BASE_V)
    kscene2.hand_new(bg, 'nowords' if not words else ('p1' if hover else beat), V)
    # --- 10. stickers
    lay, info = AS.stack_layer(words, {})
    bg.alpha_composite(lay)
    INFO['stack'] = info
    if hover:
        L3 = L2()
        if words:
            INFO['hover_tag_box'] = H2.hover_tag(L3, f, 'A')
        else:
            INFO['hover_tag_box'] = H2.hover_tag_nowords(L3, f)
        bg.alpha_composite(L3.done())
    if check:
        try:
            B10.draw_asserts(beat, f)
        except AssertionError:
            print('DRAW ASSERT FAIL', beat, flush=True)
            raise
    return bg.convert('RGB')


if __name__ == '__main__':
    import time
    t = time.time()
    b = sys.argv[1] if len(sys.argv) > 1 else 'p1'
    im = render(b)
    im.save(ROOT + 'out/test_%s.png' % b)
    print('ok', b, round(time.time() - t, 1), INFO.get('hud_bottom'))
