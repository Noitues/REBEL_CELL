"""dbg_rim.py <name> : radial run widths of the pencil all / wax masks and of dark-ink pixels across the rim arcs (r 470-515), every 2 deg"""
import sys, math
sys.dont_write_bytecode = True
import numpy as np
import hv_checks as HC
name = sys.argv[1]
rep, M, lit, rgb, bg, probe = HC.load(name)
A = HC.g(M, 'P__L6_all')
Wx = HC.g(M, 'P__L6_wax')
C = HC.C
for deg in range(0, 360, 2):
    a = math.radians(deg)
    ra, rw, ri = [], [], []
    for r10 in range(4600, 5300):
        r = r10 / 10.0
        x, y = C[0] + r * math.sin(a), C[1] - r * math.cos(a)
        xi, yi = int(round(x)), int(round(y))
        if not (0 <= xi < 1920 and 0 <= yi < 1080):
            continue
        if A[yi, xi]:
            ra.append(r)
        if Wx[yi, xi]:
            rw.append(r)
    if ra:
        print('deg %3d  all r %.1f-%.1f (%.1f)  wax %s' % (deg, min(ra), max(ra), max(ra) - min(ra), ('%.1f-%.1f (%.1f)' % (min(rw), max(rw), max(rw) - min(rw))) if rw else '-'))
