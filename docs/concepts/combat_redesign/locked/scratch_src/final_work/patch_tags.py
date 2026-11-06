"""O-29 occluder pass: ring tags and unit badges stay inside the schedule band edge (no mark on the THIS TURN tape or a label plate)"""
P = 'D:/rc_scratch/combat_redesign/locked/corp/src/'


def sub(fn, a, b):
    s = open(P + fn, newline='').read()
    nl = '\r\n' if '\r\n' in s else '\n'
    a2, b2 = a.replace('\n', nl), b.replace('\n', nl)
    assert s.count(a2) == 1, (fn, a[:60], s.count(a2))
    open(P + fn, 'w', newline='').write(s.replace(a2, b2))


sub('r2_misc.py', """def tag_geom(L, d, w_, opt):
    ri, ro = CB.ring_geom(d)
    x, y = ppx(C, ro - 17, 30)
    depth, wv = tag_words(d, w_)
    if NOW['words']:
        s = depth + ((' ' + wv) if wv else '')
        wd = L.tw(s.replace('+', ''), 20, 'anton') + 18 + (10 if depth.startswith('+') else 0)
    else:
        wd = 44
    return x, y, wd, depth, wv
""", """BAND_EDGE = 388.0      # O-29: inner edge of the schedule band incl. its ink keyline; no ring tag / badge may cross it


def tag_geom(L, d, w_, opt):
    ri, ro = CB.ring_geom(d)
    depth, wv = tag_words(d, w_)
    if NOW['words']:
        s = depth + ((' ' + wv) if wv else '')
        wd = L.tw(s.replace('+', ''), 20, 'anton') + 18 + (10 if depth.startswith('+') else 0)
    else:
        wd = 44
    rt = ro - 17
    while True:                      # O-29: pull the tag inward until its outer corner (incl. the 2.4 px outline) clears the band edge
        x, y = ppx(C, rt, 30)
        if math.hypot(x + wd / 2 + 1.5 - C[0], y - 13 - 1.5 - C[1]) <= BAND_EDGE - 1.0 or rt < ri:
            break
        rt -= 0.5
    return x, y, wd, depth, wv
""")
sub('asm_units.py', """    out['tag'] = n
    rr, aa = _pol(X, Y)
""", """    out['tag'] = n
    rr, aa = _pol(X, Y)
    out['band'] = int((rr >= 388.0 - 1.0).sum())          # O-29: px on the schedule band (THIS TURN tape / label plates)
""")
sub('asm_units.py', """            while (h['tag'] + h['tray'] + h['chev'] + h['glyph']) > 0 and size > 8:""",
    """            while (h['tag'] + h['tray'] + h['chev'] + h['glyph'] + h['band']) > 0 and size > 8:""")
sub('asm_units.py', """            while (h['tag'] + h['tray'] + h['chev'] + h['glyph']) > 0 and size > 6:""",
    """            while (h['tag'] + h['tray'] + h['chev'] + h['glyph'] + h['band']) > 0 and size > 6:""")
sub('asm_render.py', """        for k_ in ('tag', 'tray', 'chev', 'glyph'):""", """        for k_ in ('tag', 'tray', 'chev', 'glyph', 'band'):""")
print('ok')
