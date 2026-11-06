p = 'hv_key.py'
s = open(p, encoding='utf-8').read()
a = s.index("    # 4 pencil: the h02 bill hero pair with its rings (1x crop) and the YOU underline")
b = s.index("    L = L2()\n    L.text((x + 87, y + BOX_H - 16), 'LIT'")
new = '''    IW, IH = BOX_W - 24, BOX_H - 16

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
'''
s = s[:a] + new + s[b:]
open(p, 'w', encoding='utf-8').write(s)
print('ok')
