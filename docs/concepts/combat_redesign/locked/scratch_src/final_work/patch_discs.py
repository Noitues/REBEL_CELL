"""O-29 fix 8: disc inks so disc vs the art around the halo is >= 2.5:1 (measured by disc_probe.py)"""
p = 'D:/rc_scratch/combat_redesign/locked/cards/src/card_render.py'
s = open(p, newline='').read()
rep = [
    ("bone='F1EAD6', disc='FF3DA8', mis='101018', dirn='radial'", "bone='F1EAD6', disc='15121A', mis='FF3DA8', dirn='radial'"),
    ("city='06182A', disc='FF3DA8', mis='FFC83A'", "city='06182A', disc='15121A', mis='FF3DA8'"),
    ("bone='F1EAD6', disc='FF3DA8', mis='0B1A14', dirn='down'", "bone='F1EAD6', disc='15121A', mis='FF3DA8', dirn='down'"),
    ("disc='FF3DA8', mis='15121A', slide=True", "disc='15121A', mis='FF3DA8', slide=True"),
    ("neon=['27D3F5', 'FF3DA8'], disc='7A2CFF', mis='C8FF3C'", "neon=['27D3F5', 'FF3DA8'], disc='FF3DA8', mis='C8FF3C'"),
    ("    cv.paint(halftone(cv, cov * 0.6, 7.0, 45, 3.5, 3.5) * blk * ab, INK, 0.9)\n",
     "    cv.paint(halftone(cv, cov * 0.6, 7.0, 45, 3.5, 3.5) * blk * ab, INK, 0.9)\n"
     "    # O-29 fix 8: a black toner pool round the icon (the spot block stops short of the halo) so the pink disc reads >= 2.5:1\n"
     "    cv.paint(np.clip((52.0 - rr) / 3.0, 0, 1) * ab, bg)\n"),
]
for a, b in rep:
    a2, b2 = a.replace('\n', '\r\n'), b.replace('\n', '\r\n')
    if a2 in s:
        s = s.replace(a2, b2)
    elif a in s:
        s = s.replace(a, b)
    else:
        raise SystemExit('missing: ' + a[:60])
open(p, 'w', newline='').write(s)
print('ok')
