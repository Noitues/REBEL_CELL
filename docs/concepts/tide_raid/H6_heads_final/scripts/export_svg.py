"""Vector source: heads/D.svg, N.svg, E.svg, X4.svg (pose f=0, travel amplitude), plus a 256 px PNG with the rim for reference.
Unit space: 1 u = 1 SVG user unit, origin = head centre, +x = travel direction, viewBox -1.3 -1.3 2.6 2.6.
Layers (ids): outline (ink, stroke = 2 x outline dilation), body (fill hue), detail (ink dot / armour ring / shell split).
Outline dilation in u = OW_FRAC * FOOT / (1 - 2 * OW_FRAC) = .185 u, so the stroke is .37 u (stroke-linejoin round).
The rim light is NOT in the SVG (nanosvg has no clip/filter): Godot adds it (shader or two offset copies), values in NOTES.md."""
import os, sys
from heads6 import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), 'heads')
FILES = {'D': 'D', 'N': 'N', 'E': 'E', 'X': 'X4'}


def path(p):
    return 'M' + ' L'.join('%.4f %.4f' % (x, y) for x, y in p) + ' Z'


def svg(t):
    ops = head(t)
    dil = OW_FRAC * FOOT / (1 - 2 * OW_FRAC)
    fill = hexs(HUE[t])
    ink = hexs(INK)
    L = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1.3 -1.3 2.6 2.6" width="260" height="260">']
    L.append('<title>%s</title>' % NAMES[t])
    L.append('<g id="outline" fill="%s" stroke="%s" stroke-width="%.3f" stroke-linejoin="round" stroke-linecap="round">' % (ink, ink, 2 * dil))
    for k, p in ops:
        if k == 'add':
            L.append('<path d="%s"/>' % path(p))
    L.append('</g>')
    L.append('<g id="body" fill="%s">' % fill)
    for k, p in ops:
        if k == 'add':
            L.append('<path d="%s"/>' % path(p))
    L.append('</g>')
    L.append('<g id="detail">')
    for k, p in ops:
        if k == 'ink':
            L.append('<path id="dot" d="%s" fill="%s"/>' % (path(p), ink))
        elif k == 'mot':
            L.append('<path id="detail_mot" d="%s" fill="%s"/>' % (path(p), ink))
        elif k == 'fill':
            L.append('<path id="detail_fill" d="%s" fill="%s"/>' % (path(p), fill))
    L.append('</g>')
    L.append('</svg>')
    return '\n'.join(L)


def main():
    os.makedirs(OUT, exist_ok=True)
    for t, name in FILES.items():
        open(os.path.join(OUT, name + '.svg'), 'w').write(svg(t))
        im = render_head(head(t), 256, 0, HUE[t])
        im.save(os.path.join(OUT, name + '_256.png'))
    print('ok')


if __name__ == '__main__':
    main()
