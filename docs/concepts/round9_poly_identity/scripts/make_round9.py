"""Round 9 deliverables: round 8's program identity with every image redrawn in our polygon style.

Imports the slice agent's round 8 scripts unchanged and swaps only the image drawer
(icons8.art) for the polygon version (polyart.polygonize over the same subject), so the
V2 slice tile (CRT frame, scanlines, dark plate, white glyph + number) is exactly round 8's.
    python make_round9.py [library|wheels|small|compare|all]
"""
import os
import sys
import time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
R8 = os.path.join(os.path.dirname(OUT), 'round8_program_identity')
sys.path.insert(0, os.path.join(R8, 'scripts'))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw
import icons8 as I
import make_round8 as M
import polyicons

_poly = {}
_sized = {}


def art_poly(name, S, t):
    key = (name,)       # the polygon images are static
    if key not in _poly:
        _poly[key] = polyicons.draw(name)
    k2 = key + (S,)
    if k2 not in _sized:
        _sized[k2] = _poly[key].resize((S, S), Image.LANCZOS)
        if len(_sized) > 600:
            _sized.clear()
    return _sized[k2]


_flat_art = I.art
I.art = art_poly
M.OUT = OUT
M.CACHE = os.path.join(OUT, 'scratch', 'renders')


def library():
    M.make_library()
    os.replace(os.path.join(OUT, 'identity_library.png'), os.path.join(OUT, 'identity_library_poly.png'))


def wheels():
    M.make_wheels()
    for k in ('wheel_breaker', 'wheel_enemy_meridian', 'boss_manifest'):
        os.replace(os.path.join(OUT, k + '.png'), os.path.join(OUT, k + '_poly.png'))
    p = os.path.join(OUT, 'wheel_ghost.png')
    if os.path.exists(p):
        os.remove(p)


def compare():
    names = list(I.PRIMARY.items())
    cw, ch = 520, 300
    W = 3 * (2 * cw // 2 + 40) + 40
    im = M.background(3 * 620 + 60, 3 * (ch + 70) + 120, (123, 224, 123), seed=9, dim=0.7)
    d = ImageDraw.Draw(im)
    d.text((30, 16), 'ROUND 8 (flat shaded)  vs  ROUND 9 (polygon facets + toon bands + ink)  -  the 9 primaries',
           font=M.f_num(40), fill=(255, 255, 255))
    for n, (prog, name) in enumerate(names):
        r, c = divmod(n, 3)
        x, y = 30 + c * 620, 90 + r * (ch + 70)
        d.rounded_rectangle([x, y, x + 590, y + ch], radius=12, fill=(14, 12, 20), outline=(60, 60, 72))
        a = _flat_art(name, 270, 0.3)
        b = art_poly(name, 270, 0.3)
        M.paste(im, a, x + 15, y + 15)
        M.paste(im, b, x + 305, y + 15)
        d.line([(x + 295, y + 20), (x + 295, y + ch - 20)], fill=(70, 70, 82), width=2)
        f = M.f_num(28)
        lab = prog + '  -  ' + name.replace('_', ' ')
        d.text((x + 295 - f.getlength(lab) / 2, y + ch + 8), lab, font=f, fill=M.PROGRAMS[prog]['col'])
    im.convert('RGB').save(os.path.join(OUT, 'compare_flat_vs_poly.jpg'), quality=90)


def closeup():
    names = list(I.PRIMARY.items())
    im = M.background(3 * 440 + 40, 3 * 470 + 100, (255, 70, 110), seed=5, dim=0.6)
    d = ImageDraw.Draw(im)
    d.text((24, 16), 'THE 9 PRIMARIES  -  polygon art at 400 px', font=M.f_num(44), fill=(255, 255, 255))
    for n, (prog, name) in enumerate(names):
        r, c = divmod(n, 3)
        x, y = 20 + c * 440, 90 + r * 470
        d.rounded_rectangle([x, y, x + 420, y + 420], radius=12, fill=(14, 12, 20), outline=(60, 60, 72))
        M.paste(im, art_poly(name, 400, 0.3), x + 10, y + 10)
        f = M.f_num(28)
        lab = prog + '  -  ' + name.replace('_', ' ')
        d.text((x + 210 - f.getlength(lab) / 2, y + 426), lab, font=f, fill=M.PROGRAMS[prog]['col'])
    im.save(os.path.join(OUT, 'primaries_closeup.png'))


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'
    os.makedirs(M.CACHE, exist_ok=True)
    t0 = time.time()
    if what in ('closeup', 'all'):
        closeup()
    if what in ('compare', 'all'):
        compare()
        print('compare', round(time.time() - t0, 1), flush=True)
    if what in ('library', 'all'):
        library()
        print('library', round(time.time() - t0, 1), flush=True)
    if what in ('wheels', 'all'):
        wheels()
        print('wheels', round(time.time() - t0, 1), flush=True)
    if what in ('small', 'all'):
        M.make_small()
        print('small', round(time.time() - t0, 1), flush=True)
