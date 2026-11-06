p='D:/rc_scratch/combat_redesign/locked/fx_o30b/cdhl/src/fx_cdhl.py'
s=open(p).read()
# ribbon helper
s=s.replace("def burst(lay, cx, cy, R,", '''def ribbon(pts, wf):
    """a tapered ribbon polygon along pts; wf(k) = half width at fraction k"""
    n = len(pts)
    L, R_ = [], []
    for i in range(n):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        w = wf(i / max(1, n - 1))
        L.append((pts[i][0] + nx * w, pts[i][1] + ny * w))
        R_.append((pts[i][0] - nx * w, pts[i][1] - ny * w))
    return L + R_[::-1]


def burst(lay, cx, cy, R,''',1)
a=s.index("        if len(part) > 1:\n            n = len(part)"); b=s.index("        g = 1.0 if red else math.sin(math.pi * seg(tt, 0, 120))\n        lay.circle(p1[0]")
s=s[:a]+'''        if len(part) > 2:
            thin = 1 - 0.6 * seg(tt, 150, 300)
            lay.poly(ribbon(part, lambda k: (0.6 + 3.4 * k * thin) if k < 0.85 else (0.6 + 3.4 * 0.85 * thin) * (1 - k) / 0.15 + 0.3), fill=GOLD + (255,), outline=INK, w=1.6, op=fd)
'''+s[b:]
s=s.replace("end = (p1[0] + 62, p1[1] - 26)","end = (p1[0] + 84, p1[1] - 44)")
# firewall rewrite
a=s.index("def d_firewall(lay, t, c):"); b=s.index("# ======================================================================== C corp")
s=s[:a]+'''FW_TOK = [tuple(GEO1['f2']['units']['5']['tok'])]


def d_firewall(lay, t, c):
    red = c.reduce
    for ring, t0 in ((0, 0), (1, 130), (2, 260)):
        r0, r1 = RING[ring]
        depth = 0.6 * (r1 - r0)
        rise = 1.0 if red else eout(seg(t, t0, t0 + 200))
        die = 0.0 if red else seg(t, 700, 1000)
        hk = rise * (1 - 0.7 * die)
        if hk <= 0.01:
            continue
        op = 1 - 0.85 * die
        rng = np.random.RandomState(40 + ring)
        n = 7 + ring
        tongues, cores = [], []
        for i in range(n):
            ac = -27 + 54 * (i + 0.5) / n + rng.uniform(-1.5, 1.5)
            hw = 54.0 / n * rng.uniform(0.62, 0.8)
            fl = 1.0 if red else 0.88 + 0.12 * math.sin(t / 1000.0 * 2 * math.pi * 7 + i * 1.9 + ring)
            h = depth * hk * rng.uniform(0.62, 1.0) * fl
            lean = rng.uniform(-0.35, 0.35) * hw
            for (dst, hh, ww) in ((tongues, h, hw), (cores, h * 0.55, hw * 0.5)):
                pts = []
                m = 10
                for j in range(m + 1):          # left flank, base -> tip
                    k = j / m
                    wk = ww * (1 - k) ** 0.8 * (1 + 0.25 * math.sin(math.pi * k))
                    pts.append(ppx(r0 + 1 + hh * k, ac - wk + lean * k * k / (r0 / 57.3)))
                for j in range(m, -1, -1):
                    k = j / m
                    wk = ww * (1 - k) ** 0.8 * (1 + 0.25 * math.sin(math.pi * k))
                    pts.append(ppx(r0 + 1 + hh * k, ac + wk + lean * k * k / (r0 / 57.3)))
                dst.append(pts)
        # a low base band joins the tongues (one inked shape)
        base_b = band(r0 + 1, r0 + 1 + depth * hk * 0.28, -28, 28, 30)
        lay.polys(tongues + [base_b], PINK + (255,), outline=INK, w=1.9, op=op)
        lay.polys(cores, (255, 158, 210, 255), op=op)
    # the unit token stays readable: its disc is redrawn clear of the flames by masking (never over the icon)
    if t >= 330 or red:
        for i in (0, 1):
            gone_tick(lay, PIPS3['5'][i])


'''+s[b:]
s=s.replace("(330, 120, 745, 345), 'p3', d_firewall","(330, 110, 745, 365), 'p3', d_firewall")
# kill timing + box
s=s.replace("    if not red and t < 34:\n        lay.poly(cell, fill=WHITE + (255,), op=0.70)","    if not red and 16 <= t < 50:\n        lay.poly(cell, fill=WHITE + (255,), op=0.70)")
s=s.replace("'A unit dies', (250, 255, 690, 560)","'A unit dies', (225, 250, 690, 575)")
s=s.replace("(17, 'flare: 2 frames on the cell')","(33, 'flare: 2 frames on the cell')")
s=s.replace("flare=[0, 33], burst=[34, 110]","flare=[17, 50], burst=[34, 110]")
open(p,'w').write(s)
