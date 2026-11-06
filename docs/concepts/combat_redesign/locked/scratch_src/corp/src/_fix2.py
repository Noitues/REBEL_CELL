p='xf_tower.py'
s=open(p).read()
old="""    if name:
        xtext(cv, name, c[0], c[1] + 10.5, 17.0, ANTON, fill=tcol, off=(1.5, 1.4), off_col=MAG, wob=0.15, track=0.5, seed=seed + 6)"""
new="""    if name:
        # ransom-note tiles: every letter cut from a different scrap, tilted, dropped
        n_ = len(name)
        tw_ = 9.9 if not isB() else 9.5
        r2 = np.random.default_rng(seed + 31)
        if isB():
            cols = [(TONER, WH_), (MAG, TONER), (TONER, WH_), (CYN, TONER), (TONER, WH_), (MAG, TONER), (TONER, WH_)]
        else:
            cols = [(WH_, TONER), (MAG, TONER), (WH_, TONER), (CYN, TONER), (WH_, TONER), (MAG, TONER), (WH_, TONER)]
        for i, ch in enumerate(name):
            tx = c[0] + (i - (n_ - 1) / 2) * (tw_ + 0.5)
            ty = c[1] + 11.0 + r2.uniform(-1.3, 1.3)
            rot = r2.uniform(-6, 6)
            t = rect_rot(cv, tx - tw_ / 2, ty - 8.2, tx + tw_ / 2, ty + 8.2, rot)
            t = rough(t, cv, 0.25, 4.0, seed + 40 + i)
            cv.paint(shift(t, 1.2 * ss, 1.4 * ss), TONER if not isB() else TONER, 1.0)
            cv.paint(grow(t, 0.8 * ss), TONER if not isB() else WH_ * 0.9)
            ink(cv, t, cols[i % len(cols)][0], 0.02, seed + 50 + i)
            xtext(cv, ch, tx, ty + 0.4, 15.0, ANTON, fill=cols[i % len(cols)][1], rot=rot, wob=0.1, seed=seed + 60 + i, grain=0.0)"""
assert old in s
s=s.replace(old,new)
s=s.replace("WHITE_ = hx('FBFAF4')","WHITE_ = hx('FBFAF4')\nWH_ = WHITE_\n\n\ndef rect_rot(cv, x0, y0, x1, y1, rot):\n    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2\n    c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))\n    return poly(cv, [(cx + (x - cx) * c - (y - cy) * s_, cy + (x - cx) * s_ + (y - cy) * c) for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))])")
open(p,'w').write(s)
p='xf_cards.py'
s=open(p).read()
s=s.replace("px = fit_px(PLEX, txt, CW - 34, 23, ss)","px = fit_px(PLEX, txt, 142, 23, ss)\n    RX = 79")
s=s.replace("hx_ = CW / 2 + wtxt / 2","hx_ = RX + wtxt / 2")
s=s.replace("xtext(cv, txt, CW / 2, ly, px, PLEX","xtext(cv, txt, RX, ly, px, PLEX")
s=s.replace("ul = rect(cv, CW / 2 - wtxt / 2 - 2, ly + 14, CW / 2 + wtxt / 2 + 2, ly + 16.2, -0.6)","ul = rect(cv, RX - wtxt / 2 - 2, ly + 14, RX + wtxt / 2 + 2, ly + 16.2, -0.6)")
s=s.replace("(CW / 2 - wq * 70, ly - 7 + q * 15, CW / 2 + wq * 70,","(RX - wq * 70, ly - 7 + q * 15, RX + wq * 70,")
open(p,'w').write(s)
