p='D:/rc_scratch/combat_redesign/locked/fx_cdhl/src/fx_cdhl.py'
s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert a in s, a[:60]
    s=s.replace(a,b,cnt)
rep("'A unit grows one more hit', (330, 165, 545, 345)","'A unit grows one more hit', (360, 170, 715, 335)")
rep("        c_slab(lay, 1, a0, e, sk, 0.78)","        c_slab(lay, 1, a0, e, sk, 0.72)")
rep("        c_slab(lay, 1, a0 + (a1 - a0) * eio(k), a1 + 0.01, sk, 0.78 * (1 - k))","        c_slab(lay, 1, a0 + (a1 - a0) * eio(k), a1 + 0.01, sk, 0.72 * (1 - k))")
rep("'Ward applies to units in the Adjuster sector', (690, 470, 915, 860)","'Ward applies to units in the Adjuster sector', (690, 470, 918, 860)")
rep("(330, 'gold scan wipes the unit cell')","(245, 'gold scan wipes the unit cell')")
rep("'A unit dies', (225, 250, 690, 575)","'A unit dies', (195, 240, 690, 575)")
# block: tint off the seat, bigger sparks
rep("""    if t >= 100 or red:
        lay.poly(wedge(s), fill=PINK + (255,), op=0.26 * (1.0 if red else (seg(t, 100, 160) * (1 - seg(t, 360, 560)))))""",
"""    if t >= 100 or red:
        tl = Lay((lay.x0, lay.y0, lay.x1, lay.y1), lay.ss)
        tl.poly(wedge(s), fill=PINK + (255,))
        tl.erase_circle(*seat_xy(s), TOWER['seat'])
        lay.comp(tl.im, 0.30 * (1.0 if red else (seg(t, 100, 160) * (1 - seg(t, 360, 560)))))""")
rep("""        for i in range(12):
            a = math.radians(ax) + rng.uniform(-1.2, 1.2)
            cx, cy = ppx(190, ax + rng.uniform(-14, 14))
            d0 = 4 + 30 * eout(uu) * rng.uniform(0.6, 1.0)
            d1 = d0 - 10 * (1 - uu) - 3""","""        for i in range(16):
            a = math.radians(ax) + rng.uniform(-1.3, 1.3)
            cx, cy = ppx(190, ax + rng.uniform(-16, 16))
            d0 = 5 + 44 * eout(uu) * rng.uniform(0.6, 1.0)
            d1 = d0 - 16 * (1 - uu) - 5""")
rep("        lay.lines(sp, WHITE, 1.8, op=1 - seg(t, 240, 380), key=0.8)","        lay.lines(sp, WHITE, 2.4, op=1 - seg(t, 240, 380), key=1.0)\n        sparkle(lay, *ppx(192, ax - 4), 13 * math.sin(math.pi * seg(t, 100, 260)) + 0.5, WHITE)")
# hp_through: one ribbon trail, tighter stagger
a=s.index("    for i, (sx, sy, sw) in enumerate(segs):\n        t0 = 120 + i * 40"); b=s.index("    # arrival: a red slap")
s=s[:a]+'''    lead = None
    for i, (sx, sy, sw) in enumerate(segs):
        t0 = 120 + i * 30
        u = 1.0 if red else eio(seg(t, t0, t0 + 560))
        lift = 0 if red else eout(seg(t, i * 20, i * 20 + 120))
        p0 = (HT_SRC[0] + (i - 2.5) * 7, HT_SRC[1] - 9 * lift)
        cur = bez(p0, ctrl, (sx, sy), 60)
        if red or u >= 1.0:
            continue
        if i == 0 and 0 < u < 1:
            lead = (cur, u)
    if lead is not None:
        cur, u = lead
        a0 = max(0.0, u - 0.22)
        pts = [partial(cur, a0 + (u - a0) * k / 16)[-1] for k in range(17)]
        if math.dist(pts[0], pts[-1]) > 4:
            lay.poly(ribbon(pts, lambda k: 0.4 + 4.6 * k), fill=HARM + (255,), outline=INK, w=1.4, op=0.85)
    for i, (sx, sy, sw) in enumerate(segs):
        t0 = 120 + i * 30
        u = 1.0 if red else eio(seg(t, t0, t0 + 560))
        lift = 0 if red else eout(seg(t, i * 20, i * 20 + 120))
        p0 = (HT_SRC[0] + (i - 2.5) * 7, HT_SRC[1] - 9 * lift)
        cur = bez(p0, ctrl, (sx, sy), 60)
        if red or u >= 1.0:
            continue
        q = partial(cur, u)[-1]
        s_ = 7.5
        lay.poly([(q[0], q[1] - s_), (q[0] + s_, q[1]), (q[0], q[1] + s_), (q[0] - s_, q[1])], fill=HARM + (255,), outline=INK, w=1.8)
'''+s[b:]
rep("    ta = 120 + (n - 1) * 40 + 560","    ta = 120 + (n - 1) * 30 + 560")
# refund: lower control, ribbon trail
rep("        cur = bez(REFUND_AT, (840, 330), RAM_SLOT, 50)","        cur = bez(REFUND_AT, (900, 560), RAM_SLOT, 60)")
rep("""        for e in range(3):
            ue = u - 0.06 * (e + 1)
            if ue > 0 and u < 1:
                qe = partial(cur, ue)[-1]
                lay.circle(qe[0], qe[1], 11 - 2 * e, fill=CYAN + (255,), op=0.32 - 0.08 * e)""","""        a0_ = max(0.0, u - 0.2)
        pts = [partial(cur, a0_ + (u - a0_) * k / 16)[-1] for k in range(17)]
        if math.dist(pts[0], pts[-1]) > 4:
            lay.glow(lambda g: g.poly(ribbon(pts, lambda k: 0.5 + 7 * k), fill=CYAN + (255,)), blur=4, op=0.55)
            lay.poly(ribbon(pts, lambda k: 0.3 + 4.5 * k), fill=(200, 246, 255, 255), op=0.8)""")
rep("'Trigger-kill refund, +1 RAM', (400, 440, 1290, 800)","'Trigger-kill refund, +1 RAM', (400, 470, 1290, 800)")
# clear: brighter wash, bigger check
rep("    lay.glow(lambda g: g.poly(band(r - 7, r + 7, a0 + 2, e, 40), fill=GAIN + (255,)), blur=3, op=op * 0.7)\n    lay.poly(band(r - 6, r + 6, a0 + 2, e, 40), fill=GAIN + (255,), op=op * 0.6)",
    "    lay.glow(lambda g: g.poly(band(r - 10, r + 10, a0 + 2, e, 40), fill=GAIN + (255,)), blur=4, op=op * 0.9)\n    lay.poly(band(r - 8, r + 8, a0 + 2, e, 40), fill=GAIN + (255,), op=op * 0.55)")
rep("        S = 15 * k\n","        S = 20 * k\n")
rep("        lay.line(chk, GAIN, 5.2, key=1.8)","        lay.line(chk, GAIN, 6.4, key=2.0)")
# repair strokes: brush ribbons
rep("""    for p, k in strokes:
        g.line(p, MINT, 5.0 * k + 0.5, key=1.2 * k)""","""    for p, k in strokes:
        rb = ribbon(p, lambda q: (0.4 + 5.2 * k * math.sin(math.pi * min(1.0, q * 1.15)) ** 0.7))
        g.poly(rb, fill=MINT + (255,), outline=INK, w=1.2)""")
rep("        p = [(x + 3 * math.sin(j * 0.9 + i), y - rise + L * (1 - j / 5.0)) for j in range(6)]","        p = [(x + 2.5 * math.sin(j * 0.7 + i), y - rise + L * (1 - j / 9.0)) for j in range(10)]")
open(p,'w').write(s)
