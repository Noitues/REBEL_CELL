"""sg_build: components (SEND IT, nameplate, YOU strip, guns, hand) + the plate assembler on top of the E10 generator.
python sg_build.py <A|B> [p1|p2]"""
import sys, os, math, copy, json
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
from sg_lib import *
from sg_icons import *
import sg_tower as ST
import sg_hand as SH

OUT = 'D:/rc_scratch/combat_redesign/sketchbook_graffiti/out/'
COMP = OUT + 'comp/'
os.makedirs(COMP, exist_ok=True)
ROOM = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_bio_bare.png'
TOWER_XY = (366, 370)      # tower canvas origin on the plate (board centre 536,540 minus TW/2)


def cached(path, fn):
    if os.path.exists(path):
        return Image.open(path).convert('RGBA')
    im = fn()
    im.save(path)
    return im


# ------------------------------------------------------------------ SEND IT sticker
def make_send_it(variant, S=4):
    A = variant == 'A'
    w, h = 250, 128
    cv = Canvas(w, h, S, seed=71 if A else 72)
    r = cv.r
    shape = cv.poly_mask([(10, 18), (238, 12), (242, 112), (14, 116)]) if A else cv.poly_mask([(10, 14), (240, 20), (236, 116), (12, 108)])
    t, rim = torn_mask(cv, shape, rough=1.6 if A else 0.6, fringe=1.0)
    sh = np.roll(np.roll(t, int(3 * S), 0), int(3 * S), 1)
    cv.over(ndi.gaussian_filter(sh, 2.5 * S), (8, 6, 14), 0.5)
    if A:
        cv.over_rgb(t, paper_rgb(cv, 'dot', PAPER, pitch=11))
        cv.over(np.clip(rim, 0, 1) * 0.5, (252, 250, 244), 1.0)
    else:
        cv.over(t, INK, 1.0)
        cv.over(np.clip(ndi.gaussian_filter(edge_ring(ndi.binary_erosion(t > 0.5, iterations=int(5 * S)).astype(np.float32), S, 2.2), 0.4), 0, 1), PINK, 0.95)
    letters(cv, 'SEND IT', (126, 68), 44 if A else 43, fill=PINK if A else PAPER, extrude=4.5, ink_w=2.6 if A else 1.6, rot=-3 if A else 2,
            ext_col=INK if A else PINK_D, fill_mode='flat', miss=(1.8, 1.4), spacing=1.5, hatch_ext=A)
    if A:
        doodle_arrow(cv, (30, 100), (62, 104), BLUE, 1.1, curve=-5, head=5)
        doodle_star(cv, (222, 30), 8, BLUE, 1.1)
        doodle_spark(cv, (30, 36), 8, BLUE, 1.0, n=8)
        tape(cv, (120, 12), 62, 18, -2)
    else:
        doodle_star(cv, (28, 36), 7, PAPER, 1.2)
        doodle_spark(cv, (222, 98), 8, PAPER, 1.1, n=8)
        tape(cv, (30, 16), 40, 15, -32, col=(228, 232, 238))
        tape(cv, (222, 112), 40, 15, -32, col=(228, 232, 238))
    return cv.down()


def make_nameplate(variant, S=4):
    A = variant == 'A'
    w, h = 220, 106
    cv = Canvas(w, h, S, seed=81 if A else 82)
    shape = cv.poly_mask([(8, 14), (210, 8), (213, 94), (10, 98)])
    t, rim = torn_mask(cv, shape, rough=1.3 if A else 0.5, fringe=0.9)
    sh = np.roll(np.roll(t, int(3 * S), 0), int(3 * S), 1)
    cv.over(ndi.gaussian_filter(sh, 2.5 * S), (8, 6, 14), 0.5)
    cv.over_rgb(t, paper_rgb(cv, 'graph' if A else 'ruled', PAPER, pitch=12))
    cv.over(np.clip(rim, 0, 1) * 0.5, (252, 250, 244), 1.0)
    if not A:
        cv.over(np.clip(ndi.gaussian_filter(edge_ring(ndi.binary_erosion(t > 0.5, iterations=int(2.4 * S)).astype(np.float32), S, 3.0), 0.4), 0, 1), INK, 0.97)
    # emblem coin: pink bolt in a ring
    c = (36, 52)
    cv.over(cv.circle_mask(c, 20), PINK, 1.0)
    ink_edge(cv, cv.circle_mask(c, 20), 0, 0, INK, 2.0, 0.97, wob=0.5, rough='out')
    ex, ey = c
    bolt = [(ex + 4, ey - 14), (ex - 9, ey + 2), (ex - 1, ey + 2), (ex - 5, ey + 15), (ex + 9, ey - 3), (ex + 1, ey - 3)]
    bm = cv.poly_mask(bolt)
    cv.over(np.clip(ndi.gaussian_filter(outline_mask(bm, S, 1.4), 0.4) * 1.5, 0, 1), INK, 0.98)
    cv.over(bm, PAPER, 1.0)
    letters(cv, 'CELL-9', (132, 38), 32, fill=PINK, extrude=3, ink_w=1.7, rot=-2, miss=(1.4, 1.1), fill_mode='flat')
    letters(cv, '// BREAKER', (128, 74), 17, fill=INK, ink_w=0, outline=False, miss=(0, 0), wob=0.2, spacing=0.8, rot=-1)
    tape(cv, (110, 10), 46, 15, 2) if A else staple(cv, (24, 16), 14)
    if A:
        doodle_star(cv, (196, 72), 5, BLUE, 1.0)
    return cv.down()


def paint_rect_block(cv, x, y, w, h, state, S):
    m = cv.poly_mask([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])
    m = warp(m, 0.35 * S, 6 * S, cv.r)
    solid = np.clip((ndi.gaussian_filter(m, 0.5 * S / 4 * 1.5) - 0.45) * 6, 0, 1)
    ring = np.clip(ndi.gaussian_filter(outline_mask(solid, S, 1.5), 0.3) * 1.6, 0, 1)
    if state == 'harm':
        cv.over(np.clip(ndi.gaussian_filter(solid, 2.4 * S) * 1.6, 0, 1), HARM, 0.32)
    cv.over(ring, INK, 0.98)
    if state == 'lit':
        fm = np.roll(np.roll(solid, int(0.6 * S), 0), int(0.5 * S), 1)
        cv.over(fm, GAIN, 0.97)
        marker(cv, [(x + 2, y + 3), (x + w - 3, y + 2.6)], (214, 255, 214), w=1.4, alpha=0.5, wob=0.1, grain=0, rough=0, taper=(0.1, 0.4))
    elif state == 'harm':
        cv.over(solid, (14, 14, 22), 0.97)
        inner = ndi.binary_erosion(solid > 0.5, iterations=max(1, int(1.0 * S))).astype(np.float32)
        hatch_region(cv, inner, 0, 0, HARM, ang=45, pitch=2.9, w=1.15, alpha=0.95, over=0, jit=0.1, cross=True)
        cv.over(np.clip(ndi.gaussian_filter(outline_mask(inner, S, 1.0, inner=1.0), 0.3) * 1.6, 0, 1), HARM, 0.98)


def make_you_strip(variant, hp, hp_after, mx=15, S=4):
    A = variant == 'A'
    w, h = 336, 50
    cv = Canvas(w, h, S, seed=91 if A else 92)
    shape = cv.poly_mask([(6, 8), (328, 5), (331, 42), (8, 45)])
    t, rim = torn_mask(cv, shape, rough=1.1, fringe=0.8)
    cv.over(ndi.gaussian_filter(np.roll(np.roll(t, int(2.5 * S), 0), int(2.5 * S), 1), 2.2 * S), (4, 6, 14), 0.55)
    cv.over_rgb(t, paper_rgb(cv, 'dot' if A else 'graph', PAPER, pitch=11))
    cv.over(np.clip(rim, 0, 1) * 0.5, (252, 250, 244), 1.0)
    cv.over(t * 0.0, INK, 0)
    # pink highlighter band behind the blocks
    marker(cv, [(58, 26), (322, 25)], PINK_L, w=26, alpha=0.7, wob=0.3, mode='mult', taper=(0, 0), grain=0.2)
    letters(cv, 'YOU', (34, 27), 25, fill=PINK, extrude=2, ink_w=1.4, rot=-3, miss=(1.1, 0.9))
    bw, gap, ggap = 14.2, 2.7, 7.0
    x = 64.0
    for i in range(mx):
        if i and i % 5 == 0:
            x += ggap
        st = 'lit' if i < hp_after else ('harm' if i < hp else 'gone')
        paint_rect_block(cv, x, 15.5, bw, 21, st, S)
        x += bw + gap
    tape(cv, (6, 9), 24, 13, -36)
    tape(cv, (330, 42), 24, 13, -36)
    return cv.down()


# ------------------------------------------------------------------ guns (player paint across the board)
def make_guns(f, variant, S=2):
    import cv_lib as CL
    import wc2
    import cv_board as CB
    cv = Canvas(1070, 1080, S, seed=5)
    shots_out = []
    for gn in f['guns']:
        s = gn['sector']
        shots = [sh for sh in gn['shots'] if sh['uid'] is not None]
        n = len(shots)
        for i, sh in enumerate(shots):
            s_, off = wc2.gun_geom(f, gn, i, n)
            p0 = wc2.pt(wc2.MUZ_R - 6, 60 * s, off)
            cc = wc2.cell_centre(f, sh['uid'])
            ri, ro = CB.ring_geom(sh['dep'])
            p1 = CL.ppx(CL.C, (ri + ro) / 2, cc[0]) if cc else wc2.pt((ri + ro) / 2, 60 * s, off * 0.6)
            shots_out.append((p0, p1, sh))
    for p0, p1, sh in shots_out:       # ink keyline under, pink paint on top (L1 + L2)
        d = np.array(p1) - np.array(p0)
        nrm = np.array([-d[1], d[0]]) / (np.hypot(*d) + 1e-9)
        mid = (np.array(p0) + np.array(p1)) / 2 + nrm * 7
        t = np.linspace(0, 1, 30)[:, None]
        pts = (1 - t) ** 2 * np.array(p0) + 2 * (1 - t) * t * mid + t ** 2 * np.array(p1)
        marker(cv, pts, INK, w=9.2, alpha=0.96, wob=0.5, wl=30, taper=(0.02, 0.25), grain=0.05)
        marker(cv, pts, PINK, w=5.2, alpha=0.99, wob=0.35, wl=30, taper=(0.02, 0.3), grain=0.14)
        marker(cv, pts[:18], PINK_L, w=1.4, alpha=0.6, wob=0.2, wl=30, taper=(0.1, 0.5), grain=0)
    for p0, p1, sh in shots_out:       # muzzle bead + impact starburst
        cv.over(cv.circle_mask(p0, 6.0), INK, 1.0)
        cv.over(cv.circle_mask(p0, 3.6), PINK, 1.0)
        x, y = p1
        pts = []
        for k in range(16):
            rr = 10.5 if k % 2 == 0 else 4.4
            pts.append(pol((x, y), rr, k * 22.5 + cv.r.uniform(-4, 4)))
        m = cv.poly_mask(pts)
        cv.over(np.clip(ndi.gaussian_filter(outline_mask(m, S, 1.8), 0.4) * 1.5, 0, 1), INK, 1.0)
        cv.over(m, WHITE, 1.0)
        cv.over(cv.circle_mask((x, y), 3.0), PINK, 1.0)
    return cv.down()


# ------------------------------------------------------------------ assembly
def shadowed(im, off=(3, 5), blur=6, alpha=0.55):
    pad = int(blur * 3 + 8)
    big = Image.new('RGBA', (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    big.paste(im, (pad, pad))
    sh = drop_shadow(big, off, blur, alpha)
    sh.alpha_composite(big)
    return sh, pad


def hand_layer(variant, cards, costs, fan=(1006, 934, 158, 5.0, 905.0)):
    left, cy0, step, dang, arc = fan
    W_, H_ = 172, 236
    layer = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    n = len(cards)
    for i, nm in enumerate(cards):
        im = cached(COMP + 'card_%s_%s_%d.png' % (variant, nm, costs[nm]), lambda nm=nm: SH.render_card(nm, variant, costs[nm]))
        a = (i - (n - 1) / 2) * -dang
        th = math.radians(a)
        cx = left + W_ / 2 + i * step
        cy = cy0 + arc * th * th
        im = im.resize((int(im.width * 0.94), int(im.height * 0.94)), Image.LANCZOS)
        rot = im.rotate(a, resample=Image.BICUBIC, expand=True)
        sh, pad = shadowed(rot)
        layer.alpha_composite(sh, (int(cx - sh.width / 2), int(cy - sh.height / 2)))
    return layer


def assemble(variant='A', beat='p1', name=None):
    import asm_r2 as AR
    import wc2, wc2_run as WCR, kscene2, a2_stick as AS, wc2 as W2
    J = AR.J
    AR.setup()
    # --- knock out the E10 player-family elements (tower, hp ring, spokes, slice stage, trim, guns, hand, stickers)
    AR.tower_layer = lambda f, nw: Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    wc2.spokes = lambda L: None
    AR.wc2.spokes = lambda L: None
    orig_sel = WCR.sel_for

    def sel_for(o, b):
        s = orig_sel(o, b)
        z = lambda *a, **k: None
        for k in ('slice_stage', 'threat_trim', 'hp_ring', 'guns', 'p2guns', 'p3guns'):
            s[k] = z
        return s
    WCR.sel_for = sel_for
    kscene2.hand_new = lambda *a, **k: None
    orig_stack = AS.stack_layer

    def stack(words, d):
        lay, info = orig_stack(words, d)
        m = Image.new('L', lay.size, 0)
        dr = ImageDraw.Draw(m)
        dr.rectangle([1655, 850, 1895, 899], fill=255)
        dr.rectangle([1660, 1028, 1900, 1060], fill=255)
        a = ImageChops_mul(lay.split()[3], m)
        lay.putalpha(a)
        return lay, info
    AS.stack_layer = stack
    bt = {'p1': 'p1', 'p2': 'p2'}[beat]
    base = AR.render(bt, room=ROOM, check=False).convert('RGBA')
    f = copy.deepcopy(J[AR.BEATKEY[bt]])
    f['wheel'] = copy.deepcopy(f['wheel'])
    # tower
    tw = cached(COMP + 'tower_%s_%s.png' % (variant, beat), lambda: ST.render_tower(f, variant, name or 'BREAKER')[0])
    sh, pad = shadowed(tw, (3, 5), 7, 0.6)
    base.alpha_composite(sh, (TOWER_XY[0] - pad, TOWER_XY[1] - pad))
    # guns
    g = cached(COMP + 'guns_%s_%s.png' % (variant, beat), lambda: make_guns(f, variant))
    base.alpha_composite(g, (0, 0))
    # YOU strip over the HUD row
    ys = cached(COMP + 'you_%s_%s.png' % (variant, beat), lambda: make_you_strip(variant, f['hp'], f['pv']['hp_after'], f['maxhp']))
    ysh, yp = shadowed(ys, (2, 3), 3, 0.5)
    base.alpha_composite(ysh, (1074 - yp, 97 - yp))
    # hand
    cards = f['hand']
    costs = {k: J['cards'][k][0] for k in cards}
    played = [a[0] for a in f['played']]
    hand = [c for c in cards if c not in played] if beat == 'p2' else cards
    hl = hand_layer(variant, hand, {k: costs[k] for k in hand})
    base.alpha_composite(hl)
    # SEND IT + nameplate
    se = cached(COMP + 'send_%s.png' % variant, lambda: make_send_it(variant))
    ses, sp = shadowed(se, (2, 4), 5, 0.5)
    base.alpha_composite(ses, (1775 - ses.width // 2, 972 - ses.height // 2))
    npl = cached(COMP + 'name_%s.png' % variant, lambda: make_nameplate(variant))
    nps, npp = shadowed(npl, (2, 4), 5, 0.5)
    base.alpha_composite(nps, (126 - nps.width // 2, 1010 - nps.height // 2))
    return base.convert('RGB'), tw, hl


def ImageChops_mul(a, b):
    from PIL import ImageChops
    return ImageChops.multiply(a, b)


if __name__ == '__main__':
    import time
    t = time.time()
    v = sys.argv[1] if len(sys.argv) > 1 else 'A'
    beat = sys.argv[2] if len(sys.argv) > 2 else 'p1'
    im, tw, hl = assemble(v, beat)
    im.save(OUT + 'plate_%s_%s.png' % (v, beat))
    print('ok', time.time() - t)
