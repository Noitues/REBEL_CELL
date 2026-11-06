"""gram_render: the plate assembler for the grammar pass (a copy of asm_r2.render with the grammar hooks) + waves + frost + ring tags"""
import sys, os, math, copy, json
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import gram as G
from gram import *
import asm_r2 as A
from asm_r2 import (draw_units, paint_cells, tower_layer, hover_trim, hover_slice, sub_frame)
import hud2, kscene2, kcard2
import a2_stick as AS
import a2_plan as P2
import a2_hover as H2
import a_plan as PL
import wr2_boss as W2B
import wr2_cells as W2C
import wc2_run as WCR
import wc2 as WC2
import r2_sched as S2
import r2_misc as M2
import r2_arcs as A2
import o_misc as OM
import r2_glyphs as RG
import wr_geo as WG
import e8lib as E8
from cv_lib import C, W, H, L2, ppx, NOW, KCOL
import cv_lib

INK_ = (12, 10, 22)
G.install()
G.colour_install()
A2.LANE_R[:] = [436, 474, 512]


# ============================================================================================ L5 arrowed outline
def arrowed(L, pts, w=12.0, col=ENAMEL, ink=True, pitch=22.0, head=18.0):
    """L5: an outline channel (two 2.6 px edges) with inner chevrons pointing the way of travel and an arrowhead.  pts = centre path."""
    pts = resample(list(pts), 2.0) + [pts[-1]]
    n = len(pts)
    tan = []
    for i in range(n):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1
        tan.append((dx / ln, dy / ln))
    hl = head
    # shorten the channel by the head length
    acc = 0.0
    end_i = n - 1
    for i in range(n - 1, 0, -1):
        acc += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
        if acc >= hl * 0.9:
            end_i = i
            break
    cp = pts[:end_i + 1]
    ct = tan[:end_i + 1]
    left = [(p[0] - t[1] * w / 2, p[1] + t[0] * w / 2) for p, t in zip(cp, ct)]
    right = [(p[0] + t[1] * w / 2, p[1] - t[0] * w / 2) for p, t in zip(cp, ct)]
    tipp = pts[-1]
    tt = tan[-1]
    nn = (-tt[1], tt[0])
    base = cp[-1]
    hw = w * 0.95
    head_pts = [(base[0] + nn[0] * hw, base[1] + nn[1] * hw), tipp, (base[0] - nn[0] * hw, base[1] - nn[1] * hw)]
    if ink:
        for q in (left, right):
            L.line(q, INK_, 5.4)
        L.line(left + [head_pts[0]], INK_, 5.4)
        L.line(right + [head_pts[2]], INK_, 5.4)
        L.poly(head_pts, fill=INK_, outline=INK_, w=5.0)
    L.line(left + [head_pts[0], tipp, head_pts[2]] + right[::-1], col, 2.6)
    L.poly(head_pts, fill=col)
    # chevrons
    acc = pitch / 2
    j = 0
    dist = 0.0
    for i in range(1, len(cp)):
        dist += math.hypot(cp[i][0] - cp[i - 1][0], cp[i][1] - cp[i - 1][1])
        if dist >= acc:
            acc += pitch
            p, t = cp[i], ct[i]
            nx, ny = -t[1], t[0]
            s = w * 0.28
            q = [(p[0] - t[0] * s * 1.2 + nx * s * 1.4, p[1] - t[1] * s * 1.2 + ny * s * 1.4), (p[0] + t[0] * s * 0.8, p[1] + t[1] * s * 0.8), (p[0] - t[0] * s * 1.2 - nx * s * 1.4, p[1] - t[1] * s * 1.2 - ny * s * 1.4)]
            L.line(q, col, 2.4)


# ============================================================================================ wave queue
WAVE_N = {}


def engraved_plate(L, box, col_edge, dotted_edge=False, cut=False, fill=GUN_A):
    x0, y0, x1, y1 = box
    if cut:
        pts = [(x0 + 3, y0), (x1 - 14, y0), (x1, y0 + 14), (x1, y1 - 3), (x1 - 3, y1), (x0 + 3, y1), (x0, y1 - 3), (x0, y0 + 3)]
    else:
        pts = [(x0 + 4, y0), (x1 - 4, y0), (x1, y0 + 4), (x1, y1 - 4), (x1 - 4, y1), (x0 + 4, y1), (x0, y1 - 4), (x0, y0 + 4)]
    L.poly(pts, fill=fill + (255,))
    L.line(pts + [pts[0]], INK_, 4.4)
    # L4 engraved groove: dark groove with a highlight 1 px below
    ins = [(x0 + 4, y0 + 4), (x1 - (16 if cut else 4), y0 + 4)]
    if dotted_edge:
        dotted(L, pts, col_edge, dia=3.2, pitch=8.0, ink=False, closed=True)
    else:
        L.line(pts + [pts[0]], col_edge, 1.6)
    L.line([(x0 + 6, y0 + 3.5), (x1 - (18 if cut else 6), y0 + 3.5)], (10, 12, 16), 1.4)
    L.line([(x0 + 6, y0 + 4.9), (x1 - (18 if cut else 6), y0 + 4.9)], GUN_HI, 1.0)


def queue_tickets(L, f, arcs):
    fut = [a for a in arcs if a['state'] == 'future']
    order = list(reversed(fut))            # W6 (far) at the left, W4 (next) at the right
    x = 24
    tw_, th_ = 74, 62
    y0 = 24
    for i, a in enumerate(order):
        n = a['wave'] + 1
        nearest = (i == len(order) - 1)
        box = [x, y0, x + tw_, y0 + th_]
        engraved_plate(L, box, grade(ENAMEL, 1 if nearest else 2), dotted_edge=not nearest, cut=bool(a.get('climax')))
        if NOW['words']:
            L.text((x + 8, y0 + 15), 'W%d' % n, 16, 'mono', fill=TMID if not nearest else (225, 232, 242), anchor='lm')
        units = a['units']
        gx = x + 8
        slot = (tw_ - 12) / max(1, len(units))
        for ui, (kind, wd) in enumerate(units):
            cx = x + 6 + slot * ui + slot / 2
            RG.kind_glyph(L, kind, 19, (cx, y0 + 35), (235, 240, 248) if nearest else (170, 180, 195))
            bw = 4
            bx0 = cx - (wd * bw + (wd - 1) * 1.6) / 2
            for b in range(wd):
                L.rect([bx0 + b * (bw + 1.6), y0 + 49, bx0 + b * (bw + 1.6) + bw, y0 + 52.4], fill=(220, 228, 238, 255) if nearest else (150, 158, 172, 255), r=1)
        if a.get('climax'):       # W6 climax: three SCHEDULE hazard ticks on the lower edge
            for t in range(3):
                bx = x + 8 + t * 9
                L.poly([(bx, y0 + th_ - 2), (bx + 4, y0 + th_ - 2), (bx + 7, y0 + th_ - 8), (bx + 3, y0 + th_ - 8)], fill=SCHED, outline=INK_, w=1.0)
        x += tw_ + 8
    return x


def queue_feed(L, x_end):
    """the L5 feed: from the W4 ticket to the board rim (where the next wave comes in)"""
    p0 = (x_end + 6, 55)
    ang = -19.5
    p1 = (C[0] + 520 * math.sin(math.radians(ang)), C[1] - 520 * math.cos(math.radians(ang)))
    arrowed(L, [p0, p1], w=12.0, col=ENAMEL, pitch=18.0, head=16.0)


def belt(L, f, arcs):
    """option B: one rim lane, top-left: three annular plates W6 > W5 > W4 clockwise toward the needle, an L5 arrow past W4"""
    fut = [a for a in arcs if a['state'] == 'future']
    order = list(reversed(fut))
    R0, R1 = 491.0, 511.0
    a = 262.0
    span = 31.0
    gap = 2.2
    for i, w_ in enumerate(order):
        nearest = (i == len(order) - 1)
        a1 = a + span
        n = w_['wave'] + 1
        pts = L.band(C, R0, R1, a, a1)
        L.poly(pts, fill=(58, 64, 76, 255))
        L.line(pts + [pts[0]], INK_, 4.0)
        if nearest:
            L.line(pts + [pts[0]], grade(ENAMEL, 1), 1.5)
        else:
            dotted(L, pts, grade(ENAMEL, 2), dia=3.0, pitch=8.0, ink=False, closed=True)
        rm = (R0 + R1) / 2
        if NOW['words']:
            L.arc_text(C, rm, a + 4.6, 'W%d' % n, 14, TMID if not nearest else (225, 232, 242), 'mono')
        units = w_['units']
        a_u = a + 9.4
        slot = (span - 10.5) / max(1, len(units))
        for ui, (kind, wd) in enumerate(units):
            am = a_u + slot * ui + slot / 2
            x, y = ppx(C, rm - 1.5, am)
            RG.kind_glyph(L, kind, 17, (x, y), (235, 240, 248) if nearest else (170, 180, 195))
        a = a1 + gap
    # feed arrow continues clockwise past the last plate, pointing at the needle side
    pts = L.arc_pts(C, 499, a + 1.0, a + 11.0, 8)
    arrowed(L, pts, w=11.0, col=ENAMEL, pitch=16.0, head=14.0)


def future(L, f, arcs, sel):
    w = CFG['wave']
    if w is None:
        return ORIG_FUTURE(L, f, arcs, sel)
    if w == 'A':
        xe = queue_tickets(L, f, arcs)
        queue_feed(L, xe - 8)
    else:
        belt(L, f, arcs)
    return []


ORIG_FUTURE = M2.future
A.M2.future = future


# ============================================================================================ ring tags (time grammar)
ORIG_TAGS = M2.ring_tags


def ring_tags(L, f, opt):
    if not NOW['words']:
        return ORIG_TAGS(L, f, opt)
    t = CFG['time']
    for d in range(3):
        w_ = f['rings_wave'][d]
        x, y, wd, depth, wv = M2.tag_geom(L, d, w_, opt)
        c = grade(ENAMEL, d)
        box = [x - wd / 2, y - 13, x + wd / 2, y + 13]
        L.rect(box, fill=(8, 10, 18, 250), outline=INK_, w=5.0, r=6)
        if t == 'A' and d == 2:
            ring = [(box[0] + 6, box[1]), (box[2] - 6, box[1]), (box[2], box[1] + 6), (box[2], box[3] - 6), (box[2] - 6, box[3]), (box[0] + 6, box[3]), (box[0], box[3] - 6), (box[0], box[1] + 6)]
            dotted(L, ring, c, dia=3.2, pitch=7.5, ink=False, closed=True)
        else:
            if t == 'A' and d == 0:
                glow_line(L, [(box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3]), (box[0], box[1])], ENAMEL, 5, blur=3, strength=0.3)
            L.rect(box, outline=ENAMEL if (t == 'A' and d == 0) else c, w=2.4 if d == 0 else 1.8, r=6)
        tx0 = x - wd / 2 + 9
        if depth.startswith('+'):
            OM.plus_glyph(L, tx0 + 3, y, c, 4.2, 2.4)
            tx0 += 10
            txt = depth[1:] + ((' ' + wv) if wv else '')
        else:
            txt = depth + ((' ' + wv) if wv else '')
        L.text((tx0, y + 1), txt, 20, 'anton', fill=c, anchor='lm', stroke=1.4)
        # the time mark rides the tag's tower-facing end
        if t == 'A':
            if d == 0:
                end_notch(L, box[0] - 9, y, 90, col=ENAMEL, s=5.2)
            else:
                pips(L, box[0] - 8 - 10 * (d - 1), y, d, 90, 10.0, 3.0) if False else None
                for i in range(d):
                    xx = box[0] - 8 - 10 * i
                    L.ellipse([xx - 4.6, y - 4.6, xx + 4.6, y + 4.6], fill=INK_)
                    L.ellipse([xx - 3.0, y - 3.0, xx + 3.0, y + 3.0], fill=TMID)
        elif t == 'B':
            dial(L, box[0] - 13, y, d, r=8.0)


M2.ring_tags = ring_tags
A.M2.ring_tags = ring_tags


# ============================================================================================ frost (time option C)
def frost_apply(bg, extra_mask=None):
    """future rings sit behind frosted glass: blur, desaturate, lift and lower contrast, with a pane edge between NOW and +1"""
    rgb = bg.convert('RGB')
    a = np.asarray(rgb, np.float32)
    blur = np.asarray(rgb.filter(ImageFilter.GaussianBlur(1.35)), np.float32)
    lum = (0.2126 * blur[..., 0] + 0.7152 * blur[..., 1] + 0.0722 * blur[..., 2])[..., None]
    des = lum + (blur - lum) * 0.42
    veil = np.array([128, 150, 188], np.float32)
    fr = des * 0.84 + veil * 0.16
    fr = 30 + (fr - 30) * 0.88
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rho = np.hypot(xx + 0.5 - C[0], yy + 0.5 - C[1])

    def sm(x):
        return np.clip(x, 0, 1)
    m1 = sm((rho - 224.0) / 1.6) * sm((354.0 - rho) / 1.6) * 0.70      # ring +1 and +2 annuli
    m2 = sm((rho - 289.0) / 1.6) * sm((354.0 - rho) / 1.6) * 0.30
    m = m1 + m2
    if extra_mask is not None:
        m = np.maximum(m, extra_mask)
    m = np.clip(m, 0, 1)[..., None]
    out = a * (1 - m) + fr * m
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    # the pane edge: a bright hairline where the frosted glass starts (r 224)
    ed = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ed)
    for r, al in ((224.5, 110), (354.0, 70)):
        d.ellipse([C[0] - r, C[1] - r, C[0] + r, C[1] + r], outline=(215, 228, 245, al), width=2)
    im = im.convert('RGBA')
    im.alpha_composite(ed)
    return im.convert('RGB')


# ============================================================================================ the assembler
def render(beat='p1', room=None, check=False, cfg=None):
    if cfg:
        CFG.update(cfg)
    A.set_room(room or ROOM)
    words = beat != 'nowords'
    NOW['words'] = words
    A.E.reg_reset()
    A.AU.BADGE_LOG.clear()
    A.CB9.HUB['name'] = 'Breaker' if words else ''
    f = copy.deepcopy(A.J[A.BEATKEY[beat]])
    hover = beat == 'p2b'
    hid = A.J['hover']['id']
    o = dict(WCR.PICKS)
    sel = WCR.sel_for(o, beat)
    frost = CFG['time'] == 'C'

    Lhud = L2()
    hb = 'p1' if beat in ('nowords', 'p2b') else beat
    saved = hud2.SCHED
    hud2.SCHED = ENAMEL
    bottom = hud2.draw_hud(Lhud, f, hb, None)
    hud2.SCHED = saved
    A.INFO['hud_bottom'] = bottom

    bg = A.G2.backdrop('P', 'P')
    hud2.scrim_layers(bg, bottom)
    bg.alpha_composite(A.G2.plate('P').convert('RGBA'))
    bg.alpha_composite(A.G2.bezel_layer('P').convert('RGBA'))
    bg.alpha_composite(tower_layer(f, not words))

    L = L2()
    sel['hp_ring'](L, f['hp'], f['pv']['hp_after'], f['maxhp'])
    WC2.spokes(L)
    A.S2.SKIP_LABELS[0] = True
    A.S2.schedule(L, f['schedule'], {})
    A.S2.SKIP_LABELS[0] = False
    A.S2.digits(L, 'P')
    A.S2.needle(L, 'P')
    others = {u['id'] for u in f['units'] if u['id'] != hid} if hover else None
    if hover:
        paint_cells(L, f, beat, which={hid})
        Ld = L2()
        paint_cells(Ld, f, beat, which=others, with_base=False)
    else:
        paint_cells(L, f, beat)
        Ld = None
    for k_ in range(6):
        a_ = 60 * k_ + 30
        L.line([ppx(C, A.G2.BZ0 - 0.5, a_), ppx(C, A.G2.BZ1 + 0.5, a_)], INK, 8)
    Lq = L2()
    A.M2.future(Lq, f, A.B10.arcs_data(f), {})
    A.W2B.ward_arc(L, f)
    sel['slice_stage'](L, f)
    if beat in ('p1', 'nowords'):
        sel['threat_trim'](L, f)
    elif hover:
        hover_trim(L, f, sel, hid)
    if hover:
        draw_units(Ld, f, beat, skip={hid})
        draw_units(L, f, beat, only={hid})
    else:
        draw_units(L, f, beat)
    A.W2B.adjuster(L, f['adj'], beat)
    Lg = L2()
    if beat in ('p1', 'nowords'):
        sel['guns'](Lg, f)
    elif beat in ('p2', 'p3'):
        sel['p2guns'](Lg, f)
    La = L2()
    Lk = {1: L2(), 2: L2()}
    if hover:
        A2.landing_arcs(Ld, A.sub_frame(f, [u for u in f['units'] if u['id'] in others]), {}, only=others)
        A2.landing_arcs(La, f, {}, only={hid})
    elif frost:
        ids = {k: {u['id'] for u in f['units'] if u['fate']['k'] == k and u['fate']['kind'] == 'lands'} for k in (0, 1, 2)}
        rest = {u['id'] for u in f['units']} - ids[1] - ids[2]
        A2.landing_arcs(La, f, {}, only=rest)
        A2.landing_arcs(Lk[1], f, {}, only=ids[1])
        A2.landing_arcs(Lk[2], f, {}, only=ids[2])
    else:
        A2.landing_arcs(La, f, {})
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
    Lsp = L2()
    for k_ in range(6):
        a_ = 60 * k_ + 30
        Lsp.line([ppx(C, A.G2.BZ0 - 0.5, a_), ppx(C, A.G2.BZ1 + 0.5, a_)], INK, 8)
    bg.alpha_composite(Lsp.done())
    xm = None
    if frost:
        for k in (1, 2):
            im_ = Lk[k].done()
            bg.alpha_composite(im_)
        am = np.zeros((H, W), np.float32)
        for k in (1, 2):
            al = Lk[k].done().split()[3].filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
            am = np.maximum(am, np.asarray(al, np.float32) / 255.0 * (0.40 if k == 1 else 0.58))
        xm = am
        bg_rgb = frost_apply(bg, xm)
        bg = bg_rgb.convert('RGBA')
    bg.alpha_composite(Lg.done())
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
        hover_slice(Lh, f)
        A.H2.hover_path(Lh, f, 'A')
        A.H2.hover_cell(Lh, f, 'A', w=A.K2.FB_W)
        A.M2.ring_tags(Lh, f, 'P')
        bg.alpha_composite(Lh.done())
    bg.alpha_composite(Lhud.done())
    V = dict(kcard2.BASE_V)
    kscene2.hand_new(bg, 'nowords' if not words else ('p1' if hover else beat), V)
    lay, info = AS.stack_layer(words, {})
    bg.alpha_composite(lay)
    A.INFO['stack'] = info
    return bg.convert('RGB')


if __name__ == '__main__':
    import time
    t = time.time()
    b = sys.argv[1] if len(sys.argv) > 1 else 'p1'
    tt = sys.argv[2] if len(sys.argv) > 2 else 'A'
    out = sys.argv[3] if len(sys.argv) > 3 else 'D:/rc_scratch/combat_redesign/locked/wheel/out/test_%s_%s.png' % (b, tt)
    im = render(b, cfg=dict(time=tt))
    im.save(out)
    print('ok', time.time() - t)
