p = 'D:/rc_art/art-pass/docs/concepts/netrun_cel/v2/scripts/nr_scene_v2.py'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, 1)

# --- icon library + big sign
rep("def facing_of(nn):", '''ICONS = ['cross', 'ring', 'leaf', 'drop', 'bars', 'helix', 'pill', 'bowl']
def vring(cx, y, z, r0, r1, col, n=20, a0=0.0, a1=2 * math.pi):
    for i in range(n):
        t0 = a0 + (a1 - a0) * i / n; t1 = a0 + (a1 - a0) * (i + 1) / n
        quad_flat('flat', [(cx + r0 * math.cos(t0), y, z + r0 * math.sin(t0)), (cx + r1 * math.cos(t0), y, z + r1 * math.sin(t0)),
                           (cx + r1 * math.cos(t1), y, z + r1 * math.sin(t1)), (cx + r0 * math.cos(t1), y, z + r0 * math.sin(t1))], col)
def icon(kind, cx, fy, nn, z, sz, col, depth=0.34):
    y = fy + nn * depth; t = max(0.07, sz * 0.12)
    if kind == 'cross':
        beam('flat', (cx - sz * .5, y, z), (cx + sz * .5, y, z), t * 1.6, col); beam('flat', (cx, y, z - sz * .5), (cx, y, z + sz * .5), t * 1.6, col)
    elif kind == 'ring':
        vring(cx, y, z, sz * .38, sz * .5, col); vring(cx, y, z, 0.0, sz * .16, col, 10)
    elif kind == 'leaf':
        pts = [(cx, z + sz * .55), (cx + sz * .34, z), (cx, z - sz * .55), (cx - sz * .34, z)]
        for a, b in zip(pts, pts[1:] + pts[:1]): beam('flat', (a[0], y, a[1]), (b[0], y, b[1]), t, col)
        beam('flat', (cx, y, z - sz * .55), (cx, y, z + sz * .3), t * .8, col)
    elif kind == 'drop':
        beam('flat', (cx, y, z + sz * .55), (cx - sz * .32, y, z - sz * .1), t, col); beam('flat', (cx, y, z + sz * .55), (cx + sz * .32, y, z - sz * .1), t, col)
        vring(cx, y, z - sz * .12, sz * .22, sz * .34, col, 14, math.pi, 2 * math.pi)
    elif kind == 'bars':
        for i, hh in enumerate((.5, .95, .7)):
            xx = cx + (i - 1) * sz * .3; beam('flat', (xx, y, z - sz * .5), (xx, y, z - sz * .5 + sz * hh), sz * .17, col)
    elif kind == 'helix':
        prev = [None, None]
        for i in range(9):
            tt = i / 8; zz = z - sz * .5 + sz * tt; dx = math.sin(tt * 2 * math.pi * 1.2) * sz * .26
            for k, sg in enumerate((1, -1)):
                p1 = (cx + sg * dx, y, zz)
                if prev[k]: beam('flat', prev[k], p1, t, col)
                prev[k] = p1
            if i % 2 == 0: beam('flat', (cx - dx, y, zz), (cx + dx, y, zz), t * .6, col)
    elif kind == 'pill':
        beam('flat', (cx - sz * .3, y, z - sz * .12), (cx + sz * .3, y, z + sz * .12), sz * .3, col)
    else:  # bowl
        vring(cx, y, z, sz * .3, sz * .42, col, 14, math.pi, 2 * math.pi)
        for k in (-1, 0, 1): beam('flat', (cx + k * sz * .18, y, z + sz * .08), (cx + k * sz * .18, y, z + sz * .45), t * .7, col)

def big_sign(cx, y, z, w, hgt, nn, text, kind, col, panel_hex, size):
    face = facing_of(nn)
    box('solid', cx - w / 2, cx + w / 2, y - .2, y + .2, z - hgt / 2, z + hgt / 2, hexc('#120a20'))
    yy = y + nn * 0.23
    ph = hexc(panel_hex, 1.5)
    quad_flat('flat', [(cx - w / 2 + .25, yy, z - hgt / 2 + .25), (cx + w / 2 - .25, yy, z - hgt / 2 + .25), (cx + w / 2 - .25, yy, z + hgt / 2 - .25), (cx - w / 2 + .25, yy, z + hgt / 2 - .25)], ph)
    yy2 = yy + nn * 0.03
    for (a, b) in (((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1))):
        beam('flat', (cx + a[0] * w / 2, yy2, z + a[1] * hgt / 2), (cx + b[0] * w / 2, yy2, z + b[1] * hgt / 2), 0.14, col)
    icon(kind, cx - w * 0.5 + hgt * .55, y, nn, z, hgt * .6, hexc('#FFFFFF', 3.2), depth=0.27)
    add_text(text, (cx + hgt * 0.3, y + nn * 0.28, z), size, hexc('#FFFFFF', 3.4), face, 'imp')

def facing_of(nn):''')

# sign_board with optional icon
rep("def sign_board(cx, fy, nn, z, w, hgt, text, tcol, rimcol, bcol='#140a22', fnt='imp', size=None, vertical=False, depth=0.28):",
    "def sign_board(cx, fy, nn, z, w, hgt, text, tcol, rimcol, bcol='#140a22', fnt='imp', size=None, vertical=False, depth=0.28, icon_kind=None):")
rep("    add_text(text, (cx, fy + nn * (depth + 0.05), z), size, tcol, facing_of(nn), fnt)",
    """    if icon_kind and not vertical:
        icon(icon_kind, cx + w / 2 - hgt * 0.55, fy, nn, z, hgt * 0.62, tcol, depth=depth + 0.03)
        add_text(text, (cx - hgt * 0.3, fy + nn * (depth + 0.05), z), size * 0.9, tcol, facing_of(nn), fnt)
    else:
        add_text(text, (cx, fy + nn * (depth + 0.05), z), size, tcol, facing_of(nn), fnt)""")
# bay sign: icon on wide boards
rep("            sign_board(bc, fy, nn, 4.9, wsz, 1.6, nm, tcol, rcol, size=1.15 if len(nm) < 8 else 0.9)",
    "            ik = R.choice(ICONS) if (wsz >= 3.6 and R.random() < 0.6) else None\n            sign_board(bc, fy, nn, 4.9, wsz + (1.0 if ik else 0), 1.6, nm, tcol, rcol, size=1.15 if len(nm) < 8 else 0.9, icon_kind=ik)")
# spill on pavement under lit windows
rep("            box('flat', bx0 + .25, bx1 - .25, min(fy, fy + nn * .13), max(fy, fy + nn * .13), zb0, zb1, shopc)",
    "            box('flat', bx0 + .25, bx1 - .25, min(fy, fy + nn * .13), max(fy, fy + nn * .13), zb0, zb1, shopc)\n            quad_flat('flat', [(bx0 + .2, fy + nn * .3, 0.19), (bx1 - .2, fy + nn * .3, 0.19), (bx1 - .2, fy + nn * 4.2, 0.19), (bx0 + .2, fy + nn * 4.2, 0.19)], hexc(wc, 0.55))")
# blade signs: some icon-only
rep("        sign_board(bxx, fy, nn, z0 + hh / 2, wv, hh, word, hexc(lc, 3.2), hexc(lc, 3.0), size=min(1.2, hh / max(1, len(word.split(chr(10)))) * 0.86), vertical=True, depth=0.5)",
    """        if R.random() < 0.38:
            sign_board(bxx, fy, nn, z0 + hh / 2, wv, hh, '', hexc(lc, 3.2), hexc(lc, 3.0), vertical=True, depth=0.5, size=0.1)
            icon(R.choice(ICONS), bxx, fy, nn, z0 + hh / 2, wv * 0.85, hexc(lc, 3.4), depth=0.53)
        else:
            sign_board(bxx, fy, nn, z0 + hh / 2, wv, hh, word, hexc(lc, 3.2), hexc(lc, 3.0), size=min(1.2, hh / max(1, len(word.split(chr(10)))) * 0.86), vertical=True, depth=0.5)""")
# roof sign -> big sign with icon and panel
rep("        sign_board((x0 + x1) / 2, ry, nn, zc, wsz, 3.2, nm, hexc(R.choice([WARM, '#FFFFFF', PINK, LIME]), 3.4), lc, size=1.9, depth=0.0)",
    "        big_sign((x0 + x1) / 2, ry, zc, wsz + 3, 4.2, nn, nm, R.choice(ICONS), lc, R.choice(['#7a1a58', '#1a5a3a', '#2a2a8a', '#8a3a10', '#0e4a6a', '#5a1a7a']), 2.1)")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
