p = 'D:/rc_scratch/combat_polish/E7_waves/E10/src/e10lib.py'
t = open(p).read()
old = t[t.index('def lit_cell(L, u):'):t.index('# ----------------------------------------------------------------------------- chevrons: solid')]
new = '''KWASH = {'Packet': (124, 64, 104), 'Worm': (106, 68, 130), 'Jammer': (94, 86, 138), 'Payload': (118, 68, 106), 'Ring': (118, 68, 106)}


def lit_cell(L, u):
    """the unit's screen wash: a muted mauve per kind (darkened / desaturated pink, not saturated magenta), well above the dark empty sectors; the deepest ring a touch dimmer"""
    ri, ro = CB.ring_geom(u['dep'])
    a0, a1 = span(u)
    wc = KWASH.get(u['kind'], (118, 68, 106))
    al = (210, 196, 180)[u['dep']]
    fill = tuple(wc) + (al,)
    if u['w'] == 6:
        L.poly(L.band(C, ri + 4, ro - 4, a0, a0 + 359.9), fill=fill)
    else:
        L.poly(L.band(C, ri + 4, ro - 4, a0 + 3, a1 - 3), fill=fill)
    a = DEPTH_DIM[u['dep']]
    if a:
        if u['w'] == 6:
            L.poly(L.band(C, ri + 4, ro - 4, a0, a0 + 359.9), fill=(2, 3, 8, a))
        else:
            L.poly(L.band(C, ri + 4, ro - 4, a0 + 3, a1 - 3), fill=(2, 3, 8, a))


'''
t = t.replace(old, new)
t = t.replace("L.line(pts + [pts[0]], INK, 7.5)\n        L.line(pts + [pts[0]], col_lane, 3.2, dash=dash)", "L.line(pts + [pts[0]], INK, 6.5)\n        L.line(pts + [pts[0]], col_lane, 2.6, dash=dash)")
open(p, 'w').write(t)
