s = open('p1_heads.py').read()
s = s.replace('''    """items: dicts typ, x, y, ang, k. cv is a lib.Cv (sRGB float canvas)."""
    for it in items:''', '''    """items: dicts typ, x, y, ang, k. cv is a lib.Cv (sRGB float canvas).
    P3 threat silhouette (Bad North): an item with `mass` (scale vs the 44 px head) first gets a big ink silhouette with a type-hue rim + aura and a ground shadow ahead of it."""
    for it in items:
        ms = it.get('mass')
        if not ms:
            continue
        kk = it.get('k', 1.0)
        sz = int(it.get('size', SIZE) * ms * S)
        im2 = sprite(it['typ'], it['ang'], sz)
        a2 = np.asarray(im2, np.float32)[..., 3] / 255
        pad = 36 * S
        big = np.zeros((a2.shape[0] + 2 * pad, a2.shape[1] + 2 * pad), np.float32)
        big[pad:-pad, pad:-pad] = a2
        off = (int(round(it['x'] * S - im2.width / 2)) - pad, int(round(it['y'] * S - im2.height / 2)) - pad)
        col = np.array(H.HUE[it['typ']], np.float32) / 255
        ink = np.array([0.02, 0.012, 0.05], np.float32)
        # ground shadow: a soft ink ellipse cast ahead of the head along its heading (dread before the hit)
        ca, sa = math.cos(math.radians(it['ang'])), math.sin(math.radians(it['ang']))
        sh = np.zeros_like(big)
        yy, xx = np.mgrid[0:big.shape[0], 0:big.shape[1]].astype(np.float32)
        cx = big.shape[1] / 2 + ca * 70 * S; cy = big.shape[0] / 2 + sa * 70 * S + 22 * S
        dx = (xx - cx); dy = (yy - cy)
        al_ = dx * ca + dy * sa; pe_ = -dx * sa + dy * ca
        sh = np.exp(-(((al_ / (120 * S)) ** 2) + ((pe_ / (34 * S)) ** 2)))
        cv.over(ink, sh * 0.55, kk, off)
        cv.add(col, blur_fn(big, 16), 0.34 * kk, off)
        body = np.clip(blur_fn(big, 1.4) * 1.25, 0, 1)
        cv.over(ink, body, 0.86 * kk, off)
        rim = np.clip(np.clip(blur_fn(big, 5.0) * 2.0, 0, 1) - np.clip(blur_fn(big, 1.6) * 1.5, 0, 1), 0, 1)
        cv.add(col, rim * 0.9, kk, off)
    for it in items:''')
open('p1_heads.py', 'w').write(s)
f = open('p1_final.py').read()
f = f.replace("""    if beat in ('impact', 'home_hit'):
        hd = [dict(h, halo=True) for h in hd]""", """    if beat in ('impact', 'home_hit'):
        hd = [dict(h, halo=True) for h in hd]
    if beat in ('plan', 'forecast', 'reveal'):
        hero = B.ui.get('hero', {}).get(beat)
        hd = [dict(h, mass=(3.7 if h.get('rid') == hero else 2.3)) for h in hd]""")
open('p1_final.py', 'w').write(f)
