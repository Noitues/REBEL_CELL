"""hv_render: the hover-plate assembler. A parametrised copy of asm_r2.render (p1 branch): board from one frame, HUD from another, ghost layers on top,
dim mask, hand with the lifted card, stickers.  Never edits the E10 generator."""
import sys, os, copy, json, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter
import gram_render as GR
import gram as GM
from gram import ENAMEL as ENAMEL_G
import asm_r2 as A
from asm_r2 import *
import hv_lib as HL
import hover_sim as HS

A.set_room(GM.ROOM)

# hand control for kscene2
HAND = {'hand': None, 'hov': None, 'played': []}


def _hand_lists(beat):
    return list(HAND['hand']), list(HAND.get('played') or []), HAND['hov']


kscene2.hand_lists = _hand_lists

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def board_layer(fb, words, hide_units=(), veil_units=(), arcs_skip=(), draw_adj=True, beat='p1'):
    """board + ring cells + units + guns + arcs of frame fb on the backdrop. Returns (bg RGBA, L layer parts dict)"""
    NOW['words'] = words
    E.reg_reset()
    AU.BADGE_LOG.clear()
    CB9.HUB['name'] = 'Breaker' if words else ''
    o = dict(WCR.PICKS)
    bnm = 'p1' if words else 'nowords'
    sel = WCR.sel_for(o, bnm)
    f = fb
    Lhud = L2()
    _sv = hud2.SCHED
    hud2.SCHED = ENAMEL_G
    bottom = hud2.draw_hud(Lhud, f, 'p1', None)
    hud2.SCHED = _sv
    A.INFO['hud_bottom'] = bottom
    bg = G2.backdrop('P', 'P')
    hud2.scrim_layers(bg, bottom)
    bg.alpha_composite(G2.plate('P').convert('RGBA'))
    bg.alpha_composite(G2.bezel_layer('P').convert('RGBA'))
    bg.alpha_composite(tower_layer(f, not words))
    L = L2()
    sel['hp_ring'](L, f['hp'], f['pv']['hp_after'], f['maxhp'])
    wc2.spokes(L)
    S2.SKIP_LABELS[0] = True
    S2.schedule(L, f['schedule'], {})
    S2.SKIP_LABELS[0] = False
    S2.digits(L, 'P')
    S2.needle(L, 'P')
    paint_cells(L, f, beat)
    for k_ in range(6):
        a_ = 60 * k_ + 30
        L.line([ppx(C, G2.BZ0 - 0.5, a_), ppx(C, G2.BZ1 + 0.5, a_)], INK, 8)
    M2.future(L, f, B10.arcs_data(f), {})
    W2B.ward_arc(L, f)
    sel['slice_stage'](L, f)
    sel['threat_trim'](L, f)
    draw_units(L, f, beat, skip=set(hide_units))
    if draw_adj:
        W2B.adjuster(L, f['adj'], beat)
    sel['guns'](L, f)
    ids = {u['id'] for u in f['units']} - set(arcs_skip)
    A2.landing_arcs(L, f, {}, only=ids)
    M2.ring_tags(L, f, 'P')
    bg.alpha_composite(L.done())
    Lsp = L2()
    for k_ in range(6):
        a_ = 60 * k_ + 30
        Lsp.line([ppx(C, G2.BZ0 - 0.5, a_), ppx(C, G2.BZ1 + 0.5, a_)], INK, 8)
    bg.alpha_composite(Lsp.done())
    Llb = L2()
    S2.labels(Llb, f['schedule'], {})
    bg.alpha_composite(Llb.done())
    return bg, Lhud


def hud_layer(fh, words):
    NOW['words'] = words
    Lhud = L2()
    _sv = hud2.SCHED
    hud2.SCHED = ENAMEL_G
    hud2.draw_hud(Lhud, fh, 'p1', None)
    hud2.SCHED = _sv
    return Lhud.done()


def ghost_units(f_plan, ids, words, alpha=0.74, outline=True, beat='p1', arcs=True, edge_col=None):
    """ghost copy (alpha) of units `ids` as they are in f_plan: cell screens + tokens + chevrons + HP row, pencil outline on the cell; plus their plan landing arcs"""
    NOW['words'] = words
    Lg = L2()
    paint_cells(Lg, f_plan, beat, which=set(ids), with_base=False)
    draw_units(Lg, f_plan, beat, only=set(ids))
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    g = Lg.done()
    g.putalpha(g.split()[3].point(lambda v: int(v * alpha)))
    out.alpha_composite(g)
    if arcs:
        La = L2()
        A2.landing_arcs(La, f_plan, {}, only=set(ids))
        a = La.done()
        a.putalpha(a.split()[3].point(lambda v: int(v * alpha)))
        out.alpha_composite(a)
    if outline:
        Lo = L2()
        for u in f_plan['units']:
            if u['id'] in ids and not (u['consumed'] or u['trigdead']):
                poly = HL.cell_poly_unit(u) if u['w'] < 6 else None
                if poly:
                    HL.pencil_poly(Lo, poly, w=4.2, col=edge_col or HL.PLAN, ink=2.2, seed=u['id'])
        out.alpha_composite(Lo.done())
    return out


def veil_cells(f, ids, k=0.55):
    """veil (ink at k) over the live cells of units `ids`: 'vacated' / 'replaced by the ghost'"""
    L = L2()
    for u in f['units']:
        if u['id'] in ids:
            poly = HL.cell_poly_unit(u) if u['w'] < 6 else None
            if poly:
                HL.tint_poly(L, poly, (8, 10, 20), 255 * k)
    return L.done()


STYLE = {'lift': 'base'}


def lift_layer(a, info, style):
    """the lifted card's P-family print behind it.  base = hand-cut pink offset print (ink edge).  F1 = wheat-paste: hard ink drop, paper slab, kraft tape.
    F2 = Zaun press: pink plate 4 px off the key, press-cyan plate peeking 3 px the other way."""
    off = Image.new('RGBA', (W, H), (0, 0, 0, 0))

    def plate(col, dx, dy, grow=1):
        im = Image.new('RGBA', (W, H), tuple(col) + (255,))
        al = ImageChops.offset(a, dx, dy)
        if grow:
            al = al.filter(ImageFilter.MaxFilter(3))
        im.putalpha(al)
        return im
    if style == 'F2':
        off.alpha_composite(plate((12, 10, 22), 12, 12))
        off.alpha_composite(plate((32, 184, 230), -4, -3, 0))
        off.alpha_composite(plate((255, 61, 168), 8, 7))
    elif style == 'F1':
        off.alpha_composite(plate((12, 10, 22), 12, 14))
        off.alpha_composite(plate((222, 214, 196), 8, 9))
        cx, cy = info['cx'], info['cy']
        w_, h_ = info['W'] * info['s'], info['H'] * info['s']
        tp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        td = ImageDraw.Draw(tp)
        x0, y0 = cx + w_ / 2 - 44, cy - h_ / 2 - 12
        td.polygon([(x0, y0), (x0 + 74, y0 + 16), (x0 + 68, y0 + 44), (x0 - 6, y0 + 28)], fill=(198, 154, 98, 235), outline=(12, 10, 22, 255))
        off.alpha_composite(tp)
    else:
        off.alpha_composite(plate((12, 10, 22), 13, 13))
        off.alpha_composite(plate((255, 61, 168), 10, 10, 0))
    return off


def hand_layers(words, hand, hov, V=None, played=None):
    HAND['hand'] = hand
    HAND['hov'] = hov
    HAND['played'] = played or []
    NOW['words'] = words
    V = dict(V or kcard2.BASE_V)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    kscene2.hand_new(lay, 'nowords' if not words else 'p1', V)
    info = dict(kscene2.HOVINFO)
    if hov is not None and info:
        # the lifted card is a P-family object: a hand-cut pink offset print behind it (misregistered, 9 px down-right) with an ink edge
        sil = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        hi = kscene2.card_cached(hand[hov], V, 'hover', not words, info['W'], info['H'])
        kscene2.place(sil, hi, info['cx'], info['cy'], 0, info['s'], None)
        a = sil.split()[3]
        a = a.filter(ImageFilter.MaxFilter(5))
        off = lift_layer(a, info, STYLE['lift'])
        off.alpha_composite(lay)
        lay = off
    return lay, info


def sticker_layer(words):
    NOW['words'] = words
    lay, info = AS.stack_layer(words, {})
    return lay


def compose(bg, hud, lit_mask, marks, hand_lay, stick_lay, other_card_k=0.72, stick_k=0.62, k=0.40, desat=0.45):
    """bg RGBA (board), hud RGBA layer (above), lit mask, marks = list of RGBA layers drawn above the dim, hand, stickers"""
    base = bg.copy()
    base.alpha_composite(hud)
    img = HL.dim_image(base.convert('RGB'), lit_mask, k=k, desat=desat).convert('RGBA')
    for m in marks:
        img.alpha_composite(m)
    s = stick_lay.copy()
    s.putalpha(s.split()[3])
    arr = np.asarray(s).astype(np.float32)
    arr[..., :3] *= stick_k
    img.alpha_composite(Image.fromarray(arr.astype(np.uint8), 'RGBA'))
    img.alpha_composite(hand_lay)
    return img.convert('RGB')


_cc = kscene2.card_cached


def _cc2(name, V, state, nw, W_, H_):
    im = _cc(name, V, state, nw, W_, H_)
    if state == 'rest' and HAND.get('dim'):
        a = np.asarray(im).astype(np.float32)
        a[..., :3] *= HAND['dim']
        return Image.fromarray(a.astype(np.uint8), 'RGBA')
    return im


kscene2.card_cached = _cc2
