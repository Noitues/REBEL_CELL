e = open('e9lib.py').read()
# bigger chips + satellite obstacle
e = e.replace("    w = 12 + 26 + 8 + 13 * n + (18 if u.get('wear') else 0) + 8 + (14 if k == 0 else 10 * k) + 8", "    w = 12 + 32 + 8 + 17 * n + (22 if u.get('wear') else 0) + 8 + (16 if k == 0 else 12 * k) + 8")
e = e.replace("    placed = []\n    for it in items:\n        w, solid, ghost = chip_size", "    placed = []\n    ad = f['adj']\n    if ad['hp'] > 0:\n        ax, ay = ppx(C, RS['bz1'] + 51, 60 * ad['s'])\n        placed.append((ax - 36, ay - 36, ax + 36, ay + 36))\n    for it in items:\n        w, solid, ghost = chip_size")
e = e.replace("box = (x - w / 2, y - 19, x + w / 2, y + 19)", "box = (x - w / 2, y - 22, x + w / 2, y + 22)")
e = e.replace("placed.append((x - w / 2, y - 19, x + w / 2, y + 19))", "placed.append((x - w / 2, y - 22, x + w / 2, y + 22))")
i0 = e.index("    for it in items:\n        u, k = it['u'], it['k']\n        x, y = it['pos']")
new = '''    for it in items:
        u, k = it['u'], it['k']
        x, y = it['pos']
        w = it['w']
        lane = LANE[u['dep']]
        L.rect([x - w / 2, y - 21, x + w / 2, y + 21], fill=(8, 10, 18, 250), outline=lane['col'], w=3, r=9)
        gx = x - w / 2 + 6 + 16
        L.ellipse([gx - 16, y - 16, gx + 16, y + 16], fill=tuple(int(v * 0.55) for v in KCOL[u['kind']]) + (255,), outline=KCOL[u['kind']], w=2.4)
        L.glyph(KIND[u['kind']][1], 24, (gx, y), WHITE)
        cx = gx + 16 + 8
        for i in range(u['land_hit']):
            xx = cx + i * 17 + 8
            p = [(xx - 8, y - 6), (xx, y + 5), (xx + 8, y - 6)]
            if i < it['solid']:
                L.line(p, INK, 8)
                L.line(p, RED, 4.6)
            else:
                L.line(p, WHITE + (200,), 2.4, dash=(3, 3))
        cx += 17 * u['land_hit']
        if u.get('wear'):
            L.rect([cx + 2, y - 9, cx + 17, y + 7], fill=GREEN, outline=INK, w=1.6, r=2)
            L.line([(cx + 6, y - 9), (cx + 10, y - 3), (cx + 8, y + 1), (cx + 13, y + 7)], WHITE, 2)
            cx += 22
        cx += 8
        if k == 0:
            L.ellipse([cx, y - 7, cx + 14, y + 7], fill=RED, outline=WHITE, w=2)
        else:
            for i in range(k):
                L.ellipse([cx + i * 12, y - 4.5, cx + i * 12 + 9, y + 4.5], fill=WHITE, outline=INK, w=1.2)


'''
i1 = e.index("# ----------------------------------------------------------------------------- waves beyond the rim")
e = e[:i0] + new + e[i1:]
e += '''

def warded_mark(L, u):
    """gold shield (not a padlock) on a unit that sits on the Adjuster's sector"""
    ri, ro = CB.ring_geom(u['dep'])
    ang = 60 * u['s'] + 10
    x, y = ppx(C, ri + 31, ang + (30 / rmid(u['dep'])) * 57.3)
    pts = [(x - 10, y - 11), (x + 10, y - 11), (x + 10, y + 2), (x, y + 12), (x - 10, y + 2)]
    L.poly(pts, fill=(40, 30, 6, 245), outline=GOLD, w=2.6)
    L.line([(x, y - 7), (x, y + 6)], GOLD, 2.4)
'''
open('e9lib.py', 'w').write(e)
b = open('build9.py').read()
b = b.replace("    h = 190\n    L.rect([X0 - 4, y, X1, y + h]", "    h = 202\n    L.rect([X0 - 4, y, X1, y + h]")
b = b.replace("    yg = y + 183", "    yg = y + 186")
b = b.replace("x = X0 + 130 + i * 258", "x = X0 + 120 + i * 238")
b = b.replace("            seg_run(L, xx, y + 22, 'gold', f['adj']['hp'], 6, 12, pitch=8)", "            seg_run(L, xx, y + 22, 'gold', f['adj']['hp'], 5, 12, pitch=7)")
open('build9.py', 'w').write(b)
