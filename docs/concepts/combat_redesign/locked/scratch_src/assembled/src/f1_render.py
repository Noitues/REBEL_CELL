"""f1_render: the F1 (Black-book burner) plate assembler.  render(beat, key, room, hover_override) -> RGB 1920x1080.
beats: p1, nowords, p2, p2b, p3.  state keys: f1 f2 f2t f2b (default per beat).
Board = redesigned board (f1_geo layout + gram grammar + f1_board).  Player family = f1_tower / f1_guns / f1_hand (never the E10 generator's)."""
import sys, os, copy, json, math, time
sys.dont_write_bytecode = True
import f1_geo
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import gram_render as GR
import f1_board as FB
import gram as G
from gram import *
import asm_r2 as A
from asm_r2 import draw_units, paint_cells, sub_frame
import hud2, kscene2, kcard2
import a2_stick as AS
import a2_plan as P2
import a2_hover as H2
import a_plan as PL
import a_hover as HV
import wc2, wc2_run as WCR
import r2_arcs as A2
import wr2_boss as W2B
from cv_lib import C, W, H, L2, ppx, NOW
import f1_tower as FT
import f1_guns as FG
import f1_hand as FH

# ---- dash audit: every dashed draw call and every dotted mark is logged (the plan: none dashed; dotted only on the +2 threat trim mark)
import cv_lib as _cvl
import gramlib as _gl
DASH_LOG = []
DOT_LOG = []
_ol = _cvl.L2.line


def _line(self, pts, col, w=2, dash=None):
    if dash is not None:
        DASH_LOG.append(dash)
    return _ol(self, pts, col, w, dash)


_cvl.L2.line = _line
_odot = _gl.dotted


def _dotted(L, pts, col, *a, **k):
    DOT_LOG.append(len(pts))
    return _odot(L, pts, col, *a, **k)


for _m in (_gl, G, GR, FB):
    if hasattr(_m, 'dotted'):
        _m.dotted = _dotted

OUT = 'D:/rc_scratch/combat_redesign/locked/assembled/out/'
WORK = 'D:/rc_scratch/combat_redesign/locked/assembled/work/'
os.makedirs(WORK, exist_ok=True)
ROOM = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_bio_bare.png'
KEY = {'p1': 'f1', 'nowords': 'f1', 'p2': 'f2', 'p2b': 'f1', 'p3': 'f2'}
J = A.J
A.setup()
GR.A2.LANE_R[:] = [436, 453, 470]
A2.LANE_R[:] = [436, 453, 470]

# knock out the E10 player-family elements: the F1 hand draws its own tower, guns, hand and stickers
wc2.spokes = lambda L: None
GR.WC2.spokes = lambda L: None
_orig_sel = WCR.sel_for


def _sel_for(o, b):
    s = _orig_sel(o, b)
    z = lambda *a, **k: None
    for k in ('slice_stage', 'threat_trim', 'hp_ring', 'guns', 'p2guns', 'p3guns'):
        s[k] = z
    return s


WCR.sel_for = _sel_for
GR.WCR.sel_for = _sel_for

_tw = {}


def tower_img(f, tag, skip=None, hot=True, hov_sectors=None, nw=False, trim=True):
    key = (tag, tuple(sorted(skip)) if skip else None, hot, tuple(hov_sectors or ()), nw, trim)
    if key in _tw:
        return _tw[key]
    fp = WORK + 'tower_%s_%s_%d_%d_%s_%d.png' % (tag, '-'.join(map(str, sorted(skip))) if skip else 'x', int(hot), int(nw), ''.join(map(str, hov_sectors or [])), int(trim))
    if os.path.exists(fp):
        im = Image.open(fp).convert('RGBA')
    else:
        im, cv = FT.render_tower(f, name='' if nw else 'BREAKER', skip_trim_units=skip, hot=hot, with_trim=trim)
        if hov_sectors:
            cv2 = FT.Canvas(FT.TW, FT.TW, 3, seed=3)
            FT.draw_hover_arcs(cv2, hov_sectors)
            im.alpha_composite(cv2.down())
        im.save(fp)
    _tw[key] = im
    return im


def shadow_of(im, off=(3, 5), blur=7, alpha=0.5):
    pad = int(blur * 3 + 8)
    big = Image.new('RGBA', (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    a = im.split()[3]
    sh = Image.new('L', big.size, 0)
    sh.paste(a, (pad + off[0], pad + off[1]))
    sh = sh.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha))
    out = Image.new('RGBA', big.size, (8, 6, 14, 0))
    out.putalpha(sh)
    return out, pad


def render(beat='p1', **kw):
    """resolve (p3): every motion/mark of a card takes the owner colour (CELL_PINK), never the plan yellow"""
    import wr2_units as _W2U
    if beat == 'p3':
        old = (_W2U.PLAN, P2.YEL)
        _W2U.PLAN = (255, 61, 168)
        P2.YEL = (255, 61, 168)
        try:
            return _render(beat, **kw)
        finally:
            _W2U.PLAN, P2.YEL = old
    return _render(beat, **kw)


def _render(beat='p1', key=None, room=None, hover_unit=None, lift=None, with_ui=True, extra=None, trim=True, frame=None, hud_frame=None, arcs_skip=(), hide_units=(), hand_dim=None, tag=None, hand_beat=None, check=False):
    A.set_room(room or ROOM)
    words = beat != 'nowords'
    NOW['words'] = words
    A.E.reg_reset()
    A.AU.BADGE_LOG.clear()
    A.CB9.HUB['name'] = 'Breaker' if words else ''
    key = key or KEY[beat]
    f = copy.deepcopy(frame if frame is not None else A.J[key])
    if frame is not None:
        key = tag or frame.get('tag', 'plan')
    hover = beat == 'p2b' or hover_unit is not None
    hid = hover_unit if hover_unit is not None else A.J['hover']['id']
    o = dict(WCR.PICKS)
    sel = WCR.sel_for(o, beat)
    hb = 'p1' if beat in ('nowords', 'p2b') else beat
    pbeat = hb if beat != 'p2b' else 'p1'

    Lhud = L2()
    saved = hud2.SCHED
    hud2.SCHED = ENAMEL
    bottom = hud2.draw_hud(Lhud, hud_frame if hud_frame is not None else f, hb, None)
    hud2.SCHED = saved
    A.INFO['hud_bottom'] = bottom

    bg = A.G2.backdrop('P', 'P')
    hud2.scrim_layers(bg, bottom)
    bg.alpha_composite(A.G2.plate('P').convert('RGBA'))
    bg.alpha_composite(A.G2.bezel_layer('P').convert('RGBA'))

    # ---- the tower (F1): page, six slices, HP ring wrapping the hub, pips, trim
    skip = {hid} if hover else None
    hs = None
    if hover:
        hs = sorted(set(HV.hover_sectors(f)))
    tw = tower_img(f, key + ('_h' if hover else ''), skip=skip, hot=(beat != 'p3'), hov_sectors=hs, nw=not words, trim=trim)
    tsh, pad = shadow_of(tw, (3, 5), 7, 0.55)
    ox, oy = int(C[0] - FT.CT[0]), int(C[1] - FT.CT[1])
    bg.alpha_composite(tsh, (ox - pad, oy - pad))
    bg.alpha_composite(tw, (ox, oy))

    L = L2()
    A.S2.SKIP_LABELS[0] = True
    A.S2.schedule(L, f['schedule'], {})
    A.S2.SKIP_LABELS[0] = False
    A.S2.digits(L, 'P')
    A.S2.needle(L, 'P')
    others = {u['id'] for u in f['units'] if u['id'] != hid} if hover else None
    if hover:
        paint_cells(L, f, pbeat, which={hid})
        Ld = L2()
        paint_cells(Ld, f, pbeat, which=others, with_base=False)
    else:
        paint_cells(L, f, pbeat)
        Ld = None
    Lq = L2()
    A.M2.future(Lq, f, A.B10.arcs_data(f), {})
    A.W2B.ward_arc(L, f)
    if hover:
        draw_units(Ld, f, pbeat, skip={hid})
        draw_units(L, f, pbeat, only={hid})
    else:
        draw_units(L, f, pbeat, skip=set(hide_units) or None)
    A.W2B.adjuster(L, f['adj'], pbeat)
    La = L2()
    if hover:
        A2.landing_arcs(Ld, A.sub_frame(f, [u for u in f['units'] if u['id'] in others]), {}, only=others)
        A2.landing_arcs(La, f, {}, only={hid})
    else:
        A2.landing_arcs(La, f, {}, only={u['id'] for u in f['units']} - set(arcs_skip))
    Ltag = L2()
    if not hover:
        A.M2.ring_tags(Ltag, f, 'P')
    if beat in ('p2', 'p3'):
        P2.twist_badge(Ltag, f, 'A')
        if f.get('refunds'):
            P2.refund_place(Ltag, f, 'A', 'A', words)
    if beat == 'p2':
        for tr in A.J['trigs']:
            PL.trigger_path(Ltag, f, dict(tr, entries=[e for e in tr['entries'] if e[0] != 'refund']), 'A')
    bg.alpha_composite(L.done())
    # ---- the Cell's guns (pink marker): full at decide, 55 percent as a preview at p2, resolve at p3
    if beat in ('p1', 'nowords', 'p2b'):
        g, _ = FG.make_guns(f, 1.0, words)
    elif beat == 'p2':
        g, _ = FG.make_guns(f, 0.58, words)
    else:
        g, _ = FG.make_guns(f, 1.0, words)
    if beat == 'p2b':
        g.putalpha(g.split()[3].point(lambda v: int(v * A.DIM_K)))
    bg.alpha_composite(g)
    bg.alpha_composite(La.done())
    Llb = L2()
    A.S2.labels(Llb, f['schedule'], {})
    bg.alpha_composite(Llb.done())
    bg.alpha_composite(Lq.done())
    bg.alpha_composite(Ltag.done())
    if hover:
        d = Ld.done()
        d.putalpha(d.split()[3].point(lambda v: int(v * A.DIM_K)))
        bg.alpha_composite(d)
        Lh = L2()
        A.H2.hover_path(Lh, f, 'A')
        A.H2.hover_cell(Lh, f, 'A', w=A.K2.FB_W)
        A.M2.ring_tags(Lh, f, 'P')
        bg.alpha_composite(Lh.done())
    bg.alpha_composite(Lhud.done())
    if extra:
        extra(bg, f)
    if with_ui:
        # ---- the player UI: YOU strip taped on the HUD, hand, SEND IT, nameplate; UNDO and the hint line stay terminal (S family)
        FH.place_ui(bg, 'you', not words, f)
        FH.draw_hand(bg, A.J, hand_beat or beat, nw=not words, lift=lift, dim_others=hand_dim)
        lay, info = AS.stack_layer(words, {})
        m = Image.new('L', lay.size, 0)
        dr = ImageDraw.Draw(m)
        dr.rectangle([1655, 850, 1895, 899], fill=255)
        dr.rectangle([1660, 1028, 1900, 1060], fill=255)
        lay.putalpha(ImageChops.multiply(lay.split()[3], m))
        FH.place_ui(bg, 'name', not words)
        FH.place_ui(bg, 'send', not words)
        bg.alpha_composite(lay)
        A.INFO['stack'] = info
    if hover and beat == 'p2b':
        L3 = L2()
        A.INFO['hover_tag_box'] = H2.hover_tag(L3, f, 'A') if words else H2.hover_tag_nowords(L3, f)      # parked (note 8): kept in its E10 form and content
        bg.alpha_composite(L3.done())
    if check:
        try:
            A.B10.draw_asserts(beat, f)
        except AssertionError as e:
            print('DRAW ASSERT FAIL', beat, str(e)[:200], flush=True)
    return bg.convert('RGB')


if __name__ == '__main__':
    t = time.time()
    b = sys.argv[1] if len(sys.argv) > 1 else 'p1'
    out = sys.argv[2] if len(sys.argv) > 2 else OUT + 'test_%s.png' % b
    im = render(b)
    im.save(out)
    print('ok', round(time.time() - t, 1))
