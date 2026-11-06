"""hv_key: the one-page hover grammar key (h00) for the rebuilt board, in the 2026-11-03 grammar: FOCUS #D4FF00 four separate corners,
L5 PLAN arrow in wax, L6 pencil 7 px wax + 3 px ink with grain (a real ring round a number, an underline under the YOU change, no brackets),
one RAM treatment, option rows with a neutral selection and BEST star.  Marks are drawn with the plate code at use size; the other samples are
1x crops of the rendered plates (no crop is scaled, so no text in the key is drawn small).  Every text draw is Anton 30 / Mono 23 (cap >= 16 px).
python hv_key.py  -> rebuild/hover/out/h00_key.png, chk/h00_key.json (text draws with cap heights)   (needs out/h02, h03, h04, h05, h06)"""
import sys, os, math, json
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
import hv_core as V
import hv_comp as K
from hv_core import Z, HL, L2, NOW, W, H, PLAN, FOCUS, INKC, RBC
import gramlib as GL

OUT = V.HERE + 'out/'
CHK = V.HERE + 'chk/'
TXT_HI, TXT_MID = (242, 246, 255), (175, 192, 214)
CY = (92, 225, 255)
MONO = 23
LH = 29
BOX_W, BOX_H = 330, 168
ROW_H = 184


def wrap(L, x, y, s, width, col=TXT_MID):
    words = s.split(' ')
    ln = ''
    for w in words:
        t = (ln + ' ' + w).strip()
        if L.tw(t, MONO, 'mono') > width and ln:
            L.text((x, y), ln, MONO, 'mono', fill=col, anchor='lm')
            y += LH
            ln = w
        else:
            ln = t
    L.text((x, y), ln, MONO, 'mono', fill=col, anchor='lm')
    return y


ROWS = [
    ('LIT / DIM', 'lit = what the card touches, at full value. Dim = everything else: value x0.40, chroma x0.45. Cards not in play 70 percent; UNDO, SEND IT, nameplate 62.'),
    ('FOCUS: FOUR CORNERS', 'FOCUS #D4FF00, four separate corners with 12 px legs, never joined, never a full outline. 2 px = a legal target, 3.5 px = the aimed one.'),
    ('PLAN ARROW (L5)', 'PLAN yellow arrowed outline in wax: two 3 px edges on a dark channel, chevrons every 24 px, a filled head. Movement only.'),
    ('PENCIL (L6)', '7 px wax, 3 px ink edge, wax grain, no glow. A closed ring round a number the plan changes; an underline under the YOU segments that change.'),
    ('GHOST', 'the sim plan unit at its new place at 74 percent, a pencil outline outside its cell, its plan landing arc. The origin cell is veiled.'),
    ('HATCH', 'HP lost at THIS END TURN, in the cause colour: pink = ours, red = the enemy hits you, indigo = your soak.'),
    ('LIFTED CARD', '1.10x on its pink print. The fan slides clear: outside r459, 3 px off landings, off sibling cost and rules, 2 px off UNDO / SEND IT; no resting card hides more than at rest.'),
    ('HIT BURST', 'pink comic starburst = a hit that lands on a unit. It marks a cell or an edge, never an icon.'),
    ('OPTION ROWS', 'a card with options splits NEXT into one row per option. The hovered row gets a neutral edge, the best one a neutral star. No PLAN yellow.'),
    ('RAM: ONE TREATMENT', 'the RAM row shows the plan in its own coin states (spent, refunded). No pencil or ring on a coin, no box on a TRACE pip.'),
]


def main():
    NOW['words'] = True
    del RBC.TEXT[:]
    need = {k: OUT + v + '.png' for k, v in (('h02', 'h02_brace'), ('h03', 'h03_trigger'), ('h04', 'h04_twist'), ('h06', 'h06_shove'))}
    plates = {k: Image.open(p).convert('RGB') for k, p in need.items()}
    rep = json.load(open(CHK + 'h02_brace.json'))
    rep4 = json.load(open(CHK + 'h04_twist.json'))
    rep3 = json.load(open(CHK + 'h03_trigger.json'))
    bg = Image.new('RGBA', (W, H), (8, 10, 22, 255))
    L = L2()
    L.text((40, 46), 'HOVER GRAMMAR', 60, 'anton', fill=TXT_HI, anchor='lm')
    L.text((42, 100), 'one key for every hover plate  |  rebuilt board 2026-11-03, neutral skin  |  marks drawn at use size, crops at 1x', MONO, 'mono',
           fill=TXT_MID, anchor='lm')
    Y0 = 130
    cols = [40, 980]
    pos = []
    for i, (t, s) in enumerate(ROWS):
        c, r = divmod(i, 5)
        x, y = cols[c], Y0 + r * ROW_H
        pos.append((x, y))
        L.rect([x, y, x + BOX_W, y + BOX_H], fill=(5, 13, 28, 255), outline=CY + (255,), w=2, r=8)
        L.text((x + BOX_W + 22, y + 20), t, 30, 'anton', fill=TXT_HI, anchor='lm')
        wrap(L, x + BOX_W + 22, y + 58, s, 940 - BOX_W - 40)
    bg.alpha_composite(L.done())
    paste = lambda im, xy: bg.paste(im, xy)
    # 1 lit / dim: 1x crops of h02 (the lit aimed slice; a dimmed ring cell)
    x, y = pos[0]
    h02 = plates['h02']
    paste(h02.crop((585, 525, 735, 655)), (x + 12, y + 8))
    paste(h02.crop((150, 420, 300, 550)), (x + 170, y + 8))
    IW, IH = BOX_W - 24, BOX_H - 16

    def centred(im, xy):
        """paste a 1x crop centred in a sample box (no scaling)"""
        bx, by = xy
        bg.paste(im, (bx + 12 + (IW - im.width) // 2, by + 8 + (IH - im.height) // 2))
    # 4 pencil: the h02 YOU strip's changed segments with their underline, and the hero pair with its rings (1x crops, no word cut)
    x4, y4 = pos[3]
    fits = {f['tag']: f for f in rep['hud_ring_fits']}
    rl = fits['lands']['ring_box']
    rt = fits['through']['ring_box']
    yu = fits['you']
    a_, b_ = yu['segments']
    ux0, ux1 = V.you_pip_x(a_) - 8, V.you_pip_x(b_ - 1) + V.RB2.YOU_SEG_W + 8
    you_c = h02.crop((int(ux0), int(yu['y']) - 52, int(ux1), int(yu['y']) + 10))
    ring_c = h02.crop((int(rl[0]) - 2, int(rl[1]), int(rt[2]) + 3, int(rl[3]) + 1))
    if you_c.width + ring_c.width + 8 > IW:
        ring_c = h02.crop((int(rl[0]) - 2, int(rl[1]), int(rl[0]) - 2 + IW - you_c.width - 8, int(rl[3]) + 1))
    # the ring's bottom reaches the row of HUD words below (their glyph tops): those word pixels are painted out with the panel ground so the
    # sample shows no cut word (the rings themselves are kept whole)
    z = np.load(CHK + 'h02_brace.npz')
    unp = lambda k: np.unpackbits(z[k])[:H * W].reshape(H, W).astype(bool) if k in z.files else np.zeros((H, W), bool)
    words_m = np.zeros((H, W), bool)
    for k in ('Z__hud_labels', 'R__hud_labels', 'Z__digits', 'R__digits'):
        words_m |= unp(k)
    keep_m = unp('P__L6_all') | unp('Zf__hud_hero_full')
    bx0, by0 = int(rl[0]) - 2, int(rl[1])
    sub_w = words_m[by0:by0 + ring_c.height, bx0:bx0 + ring_c.width]
    sub_w = sub_w & ~keep_m[by0:by0 + ring_c.height, bx0:bx0 + ring_c.width]
    if sub_w.any():
        from scipy import ndimage as _ndi
        sub_w = _ndi.binary_dilation(sub_w, iterations=1) & ~keep_m[by0:by0 + ring_c.height, bx0:bx0 + ring_c.width]
        a_ = np.asarray(ring_c).copy()
        ground = np.median(a_[~sub_w & ~keep_m[by0:by0 + ring_c.height, bx0:bx0 + ring_c.width]].reshape(-1, 3), axis=0)
        a_[sub_w] = ground.astype(np.uint8)
        ring_c = Image.fromarray(a_)
    row = Image.new('RGB', (you_c.width + 8 + ring_c.width, max(you_c.height, ring_c.height)), (5, 13, 28))
    row.paste(you_c, (0, (row.height - you_c.height) // 2))
    row.paste(ring_c, (you_c.width + 8, (row.height - ring_c.height) // 2))
    centred(row, (x4, y4))
    # 5 ghost: 1x crop of h06 (veiled origin, ghost with its pencil outline, the PLAN arrow), clear of the ring tags' words
    x5, y5 = pos[4]
    centred(plates['h06'].crop((600, 300, 600 + IW, 300 + IH)), (x5, y5))
    # 7 lifted card: 1x crop of the h02 lifted card's top (cost hex, art) and the next card's cost hex
    x7, y7 = pos[6]
    lc = [c for c in rep['hand']['cards'] if c['role'] == 'lift'][0]
    cx0 = int(lc['cx'] - 120)
    centred(h02.crop((cx0, 740, cx0 + IW, 740 + IH)), (x7, y7))
    # 9 option rows: 1x crop of h04's NEXT rows, right part (the option tags, the selected edge, the BEST star)
    x9, y9 = pos[8]
    nr = rep4['hud2_R'].get('next_row')
    if nr:
        x1_ = int(nr[2]) + 4
        centred(plates['h04'].crop((x1_ - IW, int(nr[1]) - 4, x1_, int(nr[3]) + 5)), (x9, y9))
    # 10 RAM: 1x crop of h03's RAM row and its REFUND tab (the coins in their own states), the TRACE word left out
    x10, y10 = pos[9]
    rs = rep3['obj2_R'].get('res_plate')
    rf = rep3['obj2_R'].get('refund_tab') or (0, 0, 0, rs[3] + 40)
    if rs:
        centred(plates['h03'].crop((int(rs[0]) - 2, int(rs[1]) - 2, int(rs[0]) + 230, int(max(rs[3], rf[3])) + 4)), (x10, y10))
    L = L2()
    L.text((x + 87, y + BOX_H - 16), 'LIT', MONO, 'mono', fill=TXT_HI, anchor='mm')
    L.text((x + 245, y + BOX_H - 16), 'DIM', MONO, 'mono', fill=TXT_HI, anchor='mm')
    # 2 focus: drawn with the plate's FOCUS corners
    x, y = pos[1]
    for (bx, th, lab) in ((x + 24, False, 'legal'), (x + 184, True, 'aimed')):
        L.rect([bx + 8, y + 30, bx + 122, y + 112], fill=(52, 60, 78, 255), r=4)
        K.focus_layer(lambda L_, b_, w_: HL.rect_corners(L_, b_, w=w_, leg=V.FOCUS_LEG, pad=5), L, (bx + 8, y + 30, bx + 122, y + 112),
                      V.FOCUS_W_AIM if th else V.FOCUS_W)
        L.text((bx + 65, y + 144), lab, MONO, 'mono', fill=TXT_HI, anchor='mm')
    # 3 plan arrow (L5 in wax)
    x, y = pos[2]
    V.pc(L, [(x + 26, y + 64), (x + 120, y + 64), (x + 190, y + 34), (x + 304, y + 34)], w=13, head=19)
    V.pc(L, [(x + 40, y + 126), (x + 304, y + 126)], w=12, head=17, tail_dot=True)
    # 6 hatch: the board's own pending-loss segments (gramlib.seg_shape), one per cause
    x, y = pos[5]
    for i, (st, lab) in enumerate((('ours', 'pink'), ('harm', 'red'), ('soak', 'indigo'))):
        bx = x + 18 + i * 104
        core = [(bx + 6, y + 24), (bx + 86, y + 24), (bx + 86, y + 108), (bx + 6, y + 108)]
        GL.seg_shape(L, core, 4.0, st, ink_w=1.6, pitch=8.0, lw=2.4, opt='A', glow=False)
        L.text((bx + 46, y + 142), lab, MONO, 'mono', fill=TXT_HI, anchor='mm')
    # 8 burst
    x, y = pos[7]
    Z.pink_burst(L, x + 96, y + 84, 40, 3)
    HL.speed_lines(L, x + 240, y + 84, 0, 5, 20, 54, HL.PINK)
    Z.pink_burst(L, x + 240, y + 84, 22, 5)
    bg.alpha_composite(V.done_box(L))
    bg.convert('RGB').save(OUT + 'h00_key.png')
    caps = [dict(text=t['text'][:40], cap_px=t.get('cap_px'), where=t.get('where')) for t in RBC.TEXT]
    smallest = min((c['cap_px'] for c in caps if c['cap_px'] is not None), default=None)
    json.dump(dict(plate='h00', text=caps, smallest_cap_px=smallest, focus_calls=len(K.FOCUS_CALLS), crops_scaled=False,
                   rule='every key text draw cap height >= 16 px; every crop at 1x'), open(CHK + 'h00_key.json', 'w'), indent=1)
    print('ok key, smallest cap px', smallest)


if __name__ == '__main__':
    main()
