p = 'D:/rc_scratch/combat_polish/E7_waves/E10/src/e10lib.py'
t = open(p).read()
t += '''

# ----------------------------------------------------------------------------- gun tracers: the Adjuster is a body on its ring now, so its shots end in its cell (not on the rim)
def gun_tracers10(L, f):
    for g in f['guns']:
        s = g['sector']
        if not g['shots'] or g['shots'][0]['uid'] is None:
            L.line([ppx(C, RS['s1'] + 2, 60 * s), ppx(C, RS['c0'] + 14, 60 * s)], CYAN, 2, dash=(4, 8))
            if NOW['words']:
                xx_, yy_ = ppx(C, RS['c0'] + 30, 60 * s)
                L.rect([xx_ - 52, yy_ - 12, xx_ + 52, yy_ + 12], fill=(6, 12, 24, 235), outline=CYAN, w=2, r=6)
                L.text((xx_, yy_ + 1), 'NO TARGET', 16, 'mono', fill=CYAN)
            continue
        shots = [sh for sh in g['shots'] if sh['uid'] is not None]
        n = len(shots)
        for i, sh in enumerate(shots):
            off = 24 + (i - (n - 1) / 2) * 9
            d = sh['dep']
            ri, ro = CB.ring_geom(d)
            p0 = pt(RS['s1'] + 3, 60 * s, off)
            p1 = pt(ri + 16, 60 * s, off)
            L.line([p0, p1], INK, 6.5)
            L.line([p0, p1], CYAN, 3.6, dash=(10, 4))
            x, y = p1
            if sh['result'] == 'armor':
                L.glyph('X_BOUNCE', 26, pt(ri + 30, 60 * s, off + 18), STEEL_HI)
            elif sh['result'] == 'ward':
                L.glyph('X_BOUNCE', 26, pt(ri + 30, 60 * s, off + 18), GOLD)
            elif sh['result'] == 'sealed':
                L.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(10, 9, 16), outline=WHITE, w=2.4)
            elif sh['result'] == 'shield':
                L.ellipse([x - 8, y - 8, x + 8, y + 8], fill=CYAN, outline=INK, w=2)
                for a_ in range(0, 360, 60):
                    L.line([(x + 10 * math.cos(math.radians(a_)), y + 10 * math.sin(math.radians(a_))), (x + 15 * math.cos(math.radians(a_)), y + 15 * math.sin(math.radians(a_)))], CYAN, 2.4)
            else:
                L.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(255, 255, 255), outline=CYAN, w=2.6)
'''
t = t.replace("L.glyph('C_BRACE', 24, (xx_, yy_), CREAM)", "L.glyph('C_BRACE', 28, (xx_, yy_), CREAM)")
open(p, 'w').write(t)
p = 'D:/rc_scratch/combat_polish/E7_waves/E10/src/build10.py'
t = open(p).read()
assert "        gun_tracers(L, f)" in t
t = t.replace("        gun_tracers(L, f)", "        gun_tracers10(L, f)")
t = t.replace("        burst(L, x + 12, y + 20, 5, 11, 8)\n        L.rect([x + 26, y + 12, x + 44, y + 28]", "        burst(L, x + 12, y + 20, 7, 15, 9)\n        L.rect([x + 28, y + 12, x + 46, y + 28]")
t = t.replace("        L.line([(x + 35, y + 15), (x + 35, y + 25)], INK, 2.6)\n        L.line([(x + 30, y + 20), (x + 40, y + 20)], INK, 2.6)\n        x += 50", "        L.line([(x + 37, y + 15), (x + 37, y + 25)], INK, 2.6)\n        L.line([(x + 32, y + 20), (x + 42, y + 20)], INK, 2.6)\n        x += 54")
# REFUND tag next to the burst
t = t.replace("    burst(L, x, y, 14, 30, 12)\n    ram_pip_pop(L, x + 30, y - 24)", "    burst(L, x, y, 14, 30, 12)\n    ram_pip_pop(L, x + 30, y - 24)\n    if NOW['words']:\n        L.rect([x + 16, y - 66, x + 100, y - 44], fill=(8, 10, 18, 245), outline=(255, 214, 64), w=2, r=5)\n        L.text((x + 58, y - 54), 'REFUND', 16, 'mono', fill=(255, 214, 64))")
open(p, 'w').write(t)
