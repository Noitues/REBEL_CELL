p = 'D:/rc_scratch/combat_polish/E7_waves/E10/src/build10.py'
t = open(p).read()


def rep(old, new, cnt=1):
    global t
    assert t.count(old) >= 1, old[:80]
    t = t.replace(old, new) if cnt == 0 else t.replace(old, new, cnt)


rep('"""Build the E9 Shifting Waves plates', '"""Build the E10 Shifting Waves plates')
rep('from e9lib import *', 'from e10lib import *')
rep("waves_e9/'", "waves_e10/'")
rep("state_e9.json", "state_e10.json")
rep("(dump9.py: the E9 sim, asserted)", "(dump10.py: the E10 sim, asserted)")
# seg kinds: refund
rep("""            elif n:
                x = seg_run(L, x, cy, kind, n, 10, 16) + 10""", """            elif kind == 'refund':
                burst(L, x + 12, cy, 6, 12, 8)
                L.rect([x + 28, cy - 8, x + 50, cy + 8], fill=CYAN, outline=INK, w=2, r=3)
                x += 62
            elif n:
                x = seg_run(L, x, cy, kind, n, 10, 16) + 10""")
# RAM terminal: the refund pip pops
rep("""        L.rect([bx, y + 14, bx + 28, y + 40], fill=CYAN if i < f['ram'] else (20, 34, 52), outline=CYAN, w=2, r=4)
""", """        L.rect([bx, y + 14, bx + 28, y + 40], fill=CYAN if i < f['ram'] else (20, 34, 52), outline=CYAN, w=2, r=4)
        if f.get('refunds') and i == f['ram'] - 1 and i >= 0:
            burst(L, bx + 14, y + 27, 20, 31, 12)
            L.rect([bx, y + 14, bx + 28, y + 40], fill=CYAN, outline=INK, w=2.4, r=4)
            L.line([(bx + 14, y + 20), (bx + 14, y + 34)], INK, 3.4)
            L.line([(bx + 7, y + 27), (bx + 21, y + 27)], INK, 3.4)
""")
open(p, 'w').write(t)
print('ok')
