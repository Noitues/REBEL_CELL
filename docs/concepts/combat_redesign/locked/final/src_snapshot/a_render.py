"""Render E10 plates on room_bio_bare with per-element option selection for the ACTIONS cluster.
sel keys: send undo name mat snw hint hover locked | rtoken tpath tbadge rburst fire | htag hpath hslice hfdim hodim hcell | ctar
render(beat, sel, tgt=(kind, focus), idle=(sector, opt)).  Missing key / 'cur' = E10 as drawn."""
import sys, os, copy, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
import build10 as B10
from e10lib import *
import e10lib as E
import cv_chrome as CH
import cv_board as CB9
import cv_over as O
import o_ground as G
import o_sched as S
import o_arcs as A
import o_misc as M
import a_kit as K
import a_stick as ST
import a_plan as PL
import a_hover as HV
import a_tgt as TG
import a_hud as HUD
from render import BEATS, cached, CD, core_layer as _core_raw_layer, twist_badge as _twist_cur

J = B10.J


def hud_base(beat, f, tok='cur'):
    def build():
        NOW['words'] = beat != 'nowords'
        f1 = J['f1']
        L = L2()
        B10.header(L, f)
        y = B10.bill_box(L, f, 66, pencil=(beat == 'p2'), plan_tag=('BEST LINE' if beat in ('p2', 'p3') else None), twist_pay=(J['twist_payoff'] if beat in ('p2', 'p3') else None))
        if beat == 'p2':
            y = HUD.option_chip(L, y, 'TRIGGER ONLY', J['meta']['lines']['trigger'][0], J['meta']['lines']['trigger'][1], J['f2t']['pv']['eq'], refund=J['f2t']['refunds'] > 0, tok=tok)
            y = HUD.option_chip(L, y, 'BRACE + SOAK ONLY', J['meta']['lines']['brace'][0], J['meta']['lines']['brace'][1], J['f2b']['pv']['eq'], tok=tok)
            y = HUD.option_chip(L, y, 'BEST: ALL THREE', J['meta']['hero'], J['meta']['hero_end'], f['pv']['eq'], sel=True, refund=f['refunds'] > 0, tok=tok)
        elif beat == 'p3':
            y = HUD.chain_strip(L, f, y, tok)
        y = B10.stars_row(L, f, y + 2)
        y = HUD.ram_trace(L, f, y, tok)
        base = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        base.alpha_composite(L.done())
        played = [a[0] for a in f['played']]
        hand = list(f['hand'])
        if beat == 'p3':
            hand = list(f1['hand'])
            for c_ in played:
                hand.remove(c_)
        hover_i = hand.index('Trigger') if beat == 'p2' else None
        CH.hand(base, hand, x0=1000, hover=hover_i, played=played if beat == 'p3' else (), cy0=948)
        return base
    return cached('hudb_%s_%s' % (beat, tok), build)


def core_layer(beat, f, dim_k=0.5, desat=0.0):
    if beat != 'p2b':
        return _core_raw_layer(beat, f)

    def build():
        raw = Image.open(CD + 'core_p1.png').convert('RGBA')
        ids = [u['id'] for u in f['units'] if u['id'] != J['hover']['id']]
        im = E.grade_units(raw, f, keep_all=False, dim_ids=ids, dim_k=dim_k)
        if desat:
            m = E.unit_mask(f, False, only=set(ids)).filter(ImageFilter.GaussianBlur(0.8))
            a = np.asarray(im, np.float32).copy()
            mk = (np.asarray(m, np.float32) / 255.0)[..., None] * desat
            lum = (a[..., :3] * np.array([0.299, 0.587, 0.114], np.float32)).sum(-1, keepdims=True)
            a[..., :3] = a[..., :3] * (1 - mk) + lum * mk
            im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
        return im
    return cached('core_p2b_%s_%s' % (dim_k, desat), build)


def dim_layer(im, mode):
    """non-hovered overlay marks: cur .36; A alpha .38; B grey at .5; C defocus (blur 1.6) at .45"""
    a = {'cur': 0.36, 'A': 0.38, 'B': 0.5, 'C': 0.45}[mode]
    if mode == 'B':
        arr = np.asarray(im, np.float32).copy()
        lum = (arr[..., :3] * np.array([0.299, 0.587, 0.114], np.float32)).sum(-1, keepdims=True)
        arr[..., :3] = arr[..., :3] * 0.25 + lum * 0.75
        im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')
    if mode == 'C':
        im = im.filter(ImageFilter.GaussianBlur(1.6))
    im = im.copy()
    im.putalpha(im.split()[3].point(lambda v: int(v * a)))
    return im


def veil(bg, f):
    """spotlight (hfdim C): board outside the hovered cell and its hit slices x0.6"""
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    u = HV.hv_unit(f)
    ri, ro = CB.ring_geom(u['dep'])
    a0, a1 = span(u)
    pts = [ppx(C, ro, a0 + (a1 - a0) * i / 30) for i in range(31)] + [ppx(C, ri, a1 - (a1 - a0) * i / 30) for i in range(31)]
    d.polygon(pts, fill=255)
    for sec in HV.hover_sectors(f):
        n = 12
        pp = [ppx(C, RS['s1'], 60 * sec - 28 + 56 * i / n) for i in range(n + 1)] + [ppx(C, RS['s0'], 60 * sec + 28 - 56 * i / n) for i in range(n + 1)]
        d.polygon(pp, fill=255)
    m = m.filter(ImageFilter.GaussianBlur(5))
    disc = Image.new('L', (W, H), 0)
    ImageDraw.Draw(disc).ellipse([C[0] - 530, C[1] - 530, C[0] + 530, C[1] + 530], fill=255)
    al = np.asarray(m, np.float32) / 255.0
    al = (1 - al) * np.asarray(disc, np.float32) / 255.0 * 150
    dark = Image.new('RGBA', (W, H), (2, 3, 10, 255))
    dark.putalpha(Image.fromarray(al.astype(np.uint8)))
    bg.alpha_composite(dark)


def render(beat='p1', sel=None, hud=True, tgt=None, idle=None, nowords_extra=None):
    sel = dict(sel or {})
    words = beat != 'nowords'
    NOW['words'] = words
    E.reg_reset()
    CB9.HUB['name'] = 'Breaker' if words else ''
    f = copy.deepcopy(J[BEATS[beat]])
    tok = sel.get('rtoken', 'cur')
    bg = G.backdrop('cur', 'cur')
    bg.alpha_composite(G.plate('cur').convert('RGBA'))
    bg.alpha_composite(G.bezel_layer('cur').convert('RGBA'))
    hover = beat == 'p2b'
    dimA = sel.get('hfdim', 'cur')
    dim_k = {'cur': 0.5, 'A': 0.38, 'B': 0.40, 'C': 0.62}[dimA]
    desat = 0.6 if dimA == 'B' else 0.0
    bg.alpha_composite(core_layer(beat, f, dim_k, desat))
    L = L2()
    O.hp_ring(L, f['hp'], f['pv']['hp_after'], f['maxhp'])
    S.schedule(L, f['schedule'], {})
    S.digits(L, 'cur', 'A')
    S.needle(L, 'cur')
    occ = {(u['dep'], q) for u in f['units'] for q in sectors(u)}
    for d in range(3):
        for q in range(6):
            if (d, q) not in occ:
                O.cell_border(L, d, q, alpha=70)
    M.future(L, f, B10.arcs_data(f), {})
    ward_arc(L, f)
    tower_slice_bars(L, f)
    hs = sel.get('hslice', 'cur')
    hid = J['hover']['id']
    if hover:
        if hs == 'cur':
            threat_trim(L, f)
        else:
            HV.trim_hover(L, f, True)
    elif beat in ('p1', 'nowords'):
        threat_trim(L, f)
    dim = None
    Lh = None
    if hover:
        Ld = L2()
        B10.draw_units(Ld, f, skip={hid})
        others = {u['id'] for u in f['units'] if u['id'] != hid}
        if sel.get('hodim', 'cur') != 'cur':
            A.landing_arcs(Ld, f, {}, only=others)
        dim = dim_layer(Ld.done(), sel.get('hodim', 'cur') if sel.get('hodim', 'cur') != 'cur' else 'cur')
        Lh = L2()
        B10.draw_units(Lh, f, only={hid})
    else:
        B10.draw_units(L, f)
    adjuster_body(L, f['adj'])
    if beat in ('p1', 'nowords'):
        if idle:
            TG.idle_gun(L, f, idle[0], idle[1], words)
        else:
            gun_tracers10(L, f)
    if not hover:
        A.landing_arcs(L, f, {})
    else:
        A.landing_arcs(L, f, {}, only={hid})
    M.ring_tags(L, f, 'cur')
    B10.nudge_ghost(L)
    if beat in ('p2', 'p3'):
        tb = sel.get('tbadge', 'cur')
        if tb == 'cur':
            _twist_cur(L, f, {})
        else:
            PL.twist_badge(L, f, tb)
        rb = sel.get('rburst', 'cur')
        if rb == 'cur' and tok == 'cur':
            B10.refund_marks(L, f)
        elif f.get('refunds'):
            PL.refund_place(L, f, 'A' if rb == 'cur' else rb, 'A' if tok == 'cur' else tok, words)
    if beat == 'p2':
        for tr in J['trigs']:
            t2 = dict(tr, entries=[e for e in tr['entries'] if e[0] != 'refund'])
            tp = sel.get('tpath', 'cur')
            if tp == 'cur':
                B10.trigger_paths(L, f, t2)
            else:
                PL.trigger_path(L, f, t2, tp)
    if beat == 'p3':
        fl = sel.get('fire', 'cur')
        if fl == 'cur':
            for e_ in f['log']:
                if e_[0] == 'fire' and e_[3] is not None:
                    s_, dep_ = e_[1], e_[5]
                    L.line([ppx(C, RS['s1'] + 3, 60 * s_ + 3), pt(CB.ring_geom(dep_)[0] + 20, 60 * s_, 6)], CYAN + (170,), 2.4, dash=(5, 6))
        else:
            PL.fire_lines(L, f, fl)
    if tgt:
        TG.cues(L, f, tgt[0], sel.get('ctar', 'A'), tgt[1])
    bg.alpha_composite(L.done())
    if hover:
        bg.alpha_composite(dim)
        if dimA == 'C':
            veil(bg, f)
        L2h = L2()
        L2h.im.alpha_composite(Lh.im)
        he = sel.get('hcell', 'cur')
        if he == 'cur':
            cell_outline(L2h, HV.hv_unit(f), col=YEL, w=5)
        else:
            HV.cell_outline(L2h, f, he)
        hp_ = sel.get('hpath', 'cur')
        if hp_ == 'cur':
            B10.hover_path(L2h, f)
        else:
            HV.hover_path(L2h, f, hp_)
        if hs != 'cur':
            HV.hover_slice(L2h, f, hs)
        bg.alpha_composite(L2h.done())
    if hud:
        bg.alpha_composite(hud_base(beat, f, tok))
    if any(k in sel for k in ('send', 'undo', 'name', 'mat', 'snw', 'hint')):
        lay, info = ST.stickers_layer(words, sel)
        bg.alpha_composite(lay)
    else:
        bg.alpha_composite(ST.stickers_cur(words))
    if hover:
        ht = sel.get('htag', 'cur')
        L3 = L2()
        if ht == 'cur':
            B10.hover_tag(L3, f)
        else:
            HV.hover_tag(L3, f, ht)
        bg.alpha_composite(L3.done())
    return bg.convert('RGB')


def crop2(img, box, scale=2):
    c = img.crop(box)
    return c.resize((int(c.width * scale), int(c.height * scale)), Image.LANCZOS)


if __name__ == '__main__':
    import time
    t = time.time()
    for b in sys.argv[1:] or ['p1']:
        im = render(b)
        im.save(ROOT + 'a_cur_%s.png' % b)
    print('ok', time.time() - t)
