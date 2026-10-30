p='bd2_cutaway.py'
s=open(p,encoding='utf-8').read()
i=s.index('def neighbours(img):')
j=s.index('def lighting(img):')
new='''def neighbours(img):
    pal = [(40, 38, 78, 255), (34, 46, 86, 255), (58, 40, 82, 255)]
    defs = [(-8.5, 0.0, -0.8, 10.0, 11, 0), (-8.5, 10.6, -0.8, 18, 7, 1), (0.0, -8.5, 10.0, -0.8, 9, 2),
            (-8.5, -8.5, -0.8, -0.8, 14, 1), (10.6, -8.5, 18, -0.8, 3, 0)]
    for i, (x0, y0, x1, y1, h, pi) in enumerate(defs):
        base = pal[pi]
        box(img, x0, y0, 0, x1, y1, h, base)
        windows_on_face(img, 'x', x1, y0, y1, 0.5, h - 0.3, 5, max(2, int(h * 1.1)), (170, 150, 104, 255), 0.22, seed=i * 3)
        windows_on_face(img, 'y', y1, x0, x1, 0.5, h - 0.3, 5, max(2, int(h * 1.1)), (140, 170, 180, 255), 0.22, seed=i * 3 + 1)
        a, b = Pt(x1, y1, h), Pt(x1, y0, h)
        line(img, [a[0], a[1], b[0], b[1]], (255, 62, 160, 150) if pi == 0 else (0, 229, 255, 150), 3)


def building(img):
    tones = {
        0: dict(L=(18, 34, 36), R=(24, 44, 46), F=(30, 46, 46)),
        1: dict(L=(40, 84, 78), R=(52, 108, 98), F=(86, 126, 106)),
    }
    X, Y = 10.0, 10.0
    for f in range(2):
        z0, z1 = 3.0 * f, 3.0 * f + 3.0
        t = tones[f]
        face(img, [(0, 0, z0), (0, Y, z0), (0, Y, z1), (0, 0, z1)], t['L'] + (255,), INK, 3.5)
        face(img, [(0, 0, z0), (X, 0, z0), (X, 0, z1), (0, 0, z1)], t['R'] + (255,), INK, 3.5)
        face(img, [(0, 0, z0), (X, 0, z0), (X, Y, z0), (0, Y, z0)], t['F'] + (255,), INK, 3.5)
        for k in range(1, 10):
            a, b = Pt(k, 0, z0), Pt(k, Y, z0)
            line(img, [a[0], a[1], b[0], b[1]], (0, 0, 0, 55), 1.5)
            a, b = Pt(0, k, z0), Pt(X, k, z0)
            line(img, [a[0], a[1], b[0], b[1]], (0, 0, 0, 55), 1.5)
        for yv in (1.2, 4.2, 7.2):
            face(img, [(0, yv, z0 + 0.9), (0, yv + 2.0, z0 + 0.9), (0, yv + 2.0, z0 + 2.3), (0, yv, z0 + 2.3)], (22, 34, 66, 255), INK, 2)
        for xv in (1.2, 4.2, 7.2):
            face(img, [(xv, 0, z0 + 0.9), (xv + 2.0, 0, z0 + 0.9), (xv + 2.0, 0, z0 + 2.3), (xv, 0, z0 + 2.3)], (22, 34, 66, 255), INK, 2)
    # ---- ground floor: lobby behind the slab
    box(img, 1.0, 3.6, 0, 2.3, 7.4, 1.0, (60, 70, 76, 255))
    for yy in (1.2, 5.0, 8.8):
        cyl(img, 0.9, yy, 0, 0.45, 1.5, (30, 70, 40, 255), (60, 150, 60, 255), frac=0.9)
    pa, pb = [], []
    for i in range(31):
        t = i / 30
        zz = 1.0 + t * 1.8
        yy = 5.0 + math.sin(t * 6.283 * 1.6) * 1.0
        pa.append(Pt(0, yy, zz))
        pb.append(Pt(0, 10 - yy, zz))
    G = layer(W, H)
    line(G, [c for p in pa for c in p], LIME, 6)
    line(G, [c for p in pb for c in p], LIME, 6)
    img.paste(glow(img, G, 6, 0.8))
    line(img, [c for p in pa for c in p], (140, 230, 80, 255), 3)
    line(img, [c for p in pb for c in p], (110, 190, 70, 255), 3)
    # slab between floors (front edges)
    face(img, [(10, 0, 2.62), (10, 10, 2.62), (10, 10, 3.0), (10, 0, 3.0)], (30, 36, 44, 255), INK, 3)
    face(img, [(0, 10, 2.62), (10, 10, 2.62), (10, 10, 3.0), (0, 10, 3.0)], (22, 28, 36, 255), INK, 3)
    # ---- the lab (fight floor)
    z = 3.0
    for k, yy in enumerate((1.4, 3.5, 5.6, 7.7)):
        cyl(img, 1.0, yy + 0.4, z, 0.62, 2.4, (30, 40, 42, 255), (110, 220, 70, 255))
    for k, xx in enumerate((2.6, 4.4, 6.2, 8.0)):
        box(img, xx, 0.2, z, xx + 1.2, 1.1, z + 2.2, (40, 56, 62, 255))
        for m in range(5):
            a, b = Pt(xx + 1.2, 0.2, z + 0.4 + m * 0.36), Pt(xx + 1.2, 1.1, z + 0.4 + m * 0.36)
            line(img, [a[0], a[1], b[0], b[1]], (0, 229, 255, 170) if (m + k) % 2 else (150, 255, 70, 170), 2)
    box(img, 3.6, 3.6, z, 6.2, 5.6, z + 0.9, (74, 92, 88, 255))
    cyl(img, 4.4, 4.6, z + 0.9, 0.34, 0.8, (30, 40, 42, 255), (150, 255, 70, 255), frac=0.9)
    cyl(img, 5.4, 4.2, z + 0.9, 0.26, 0.6, (30, 40, 42, 255), (0, 229, 255, 255), frac=0.9)
    box(img, 8.4, 6.8, z, 9.4, 8.9, z + 1.0, (56, 70, 70, 255))
    box(img, 5.6, 8.0, z, 7.2, 9.2, z + 0.7, (50, 64, 62, 255))
    # front slab edge of the lab floor, columns, parapet rails
    face(img, [(10, 0, z - 0.2), (10, 10, z - 0.2), (10, 10, z), (10, 0, z)], (30, 36, 44, 255), INK, 3)
    for (x, y) in ((10, 0), (10, 10), (0, 10)):
        box(img, x - 0.25, y - 0.25, 0, x + 0.25, y + 0.25, 6.0, (44, 50, 62, 255))
    # glass rail along the open front edges of the lab floor
    for (a, b) in [((10, 0, 3.0), (10, 10, 3.0)), ((0, 10, 3.0), (10, 10, 3.0))]:
        p0, p1 = Pt(*a), Pt(*b)
        p0u, p1u = Pt(a[0], a[1], 4.0), Pt(b[0], b[1], 4.0)
        poly(img, [p0, p1, p1u, p0u], fill=(120, 200, 190, 36), outline=(160, 230, 220, 170), width=2)


'''
s=s[:i]+new+s[j:]
s=s.replace("poly(L, [Pt(0.2, 0.2, 3.05), Pt(8.8, 0.2, 3.05), Pt(8.8, 8.8, 3.05), Pt(0.2, 8.8, 3.05)], fill=(150, 255, 150, 70))","poly(L, [Pt(0.2, 0.2, 3.05), Pt(9.8, 0.2, 3.05), Pt(9.8, 9.8, 3.05), Pt(0.2, 9.8, 3.05)], fill=(150, 255, 150, 60))")
s=s.replace("hx = 1800","hx = 1840").replace("yv = 120 + t * 560","yv = 330 + t * 420")
s=s.replace("Pt(9.5, 0, 0.02), Pt(14, 0, 0.02), Pt(14, 9, 0.02), Pt(9.5, 9, 0.02)","Pt(10.5, 0, 0.02), Pt(14, 0, 0.02), Pt(14, 10, 0.02), Pt(10.5, 10, 0.02)")
s=s.replace("face(img, [(9.5, -9, 0), (14.5, -9, 0), (14.5, 19, 0), (9.5, 19, 0)]","face(img, [(10.5, -9, 0), (15.5, -9, 0), (15.5, 19, 0), (10.5, 19, 0)]")
s=s.replace("pa = Pt(11.2, yv, 0.02)\n        pb = Pt(12.0, yv + 4.2, 0.02)","pa = Pt(12.2, yv, 0.02)\n        pb = Pt(13.0, yv + 4.2, 0.02)")
open(p,'w',encoding='utf-8').write(s)
