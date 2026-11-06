p = 'D:/rc_scratch/combat_polish/E7_waves/E10/src/cv_board.py'
t = open(p).read()
old = "dict(upright=True, rc=0.55, glyph_scale=1.0, tex_gain=0.9), seed=s + 3)"
new = "dict(upright=True, rc=0.55, glyph_scale=1.0, tex_gain=0.9), seed=s + 3, glyph=('SHIELD' if w['t'] == 'SHIELD' else None))"
assert old in t
open(p, 'w').write(t.replace(old, new))
p = 'D:/rc_scratch/combat_polish/E7_waves/E10/src/e10lib.py'
t = open(p).read()
old = """                else:
                    L.line(p, INK, 8.5)
                    L.line(p, REDC, 4.8)
                    L.line(p, (10, 6, 14), 1.8)"""
new = """                else:
                    L.line(p, INK, 10.5)
                    L.line(p, REDC, 6.6)
                    L.line(p, (8, 5, 12), 3.0)"""
assert old in t
open(p, 'w').write(t.replace(old, new))
