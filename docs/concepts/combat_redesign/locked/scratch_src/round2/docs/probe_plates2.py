"""probe_plates2.py: (a) where the L* >= 95 px inside r 480 sit on the published p1 (radius histogram, hue of those px);
(b) the button column on the round-1 board plate (the committed b26022f5 p1_decide.png, extracted to work/ by git show)
against the published round-2 p1 and h01, by the same column-profile edge.  Reads only; prints.
usage: python probe_plates2.py <round1_p1_png>"""
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/round2/docs')
from probe_plates import load, lab, lstar, radius, LOCK  # noqa: E402  (module-level probes in probe_plates run on import)

im = load('final/p1_decide.png')
Lb = lab(im)
L = Lb[..., 0]
r = radius(L.shape)
m = (L >= 95) & (r < 480)
ys, xs = np.nonzero(m)
rr = r[m]
print('\n## (a) L*>=95 inside r480 on p1:', m.sum(), 'px')
hist, edges = np.histogram(rr, bins=[0, 100, 162, 200, 214, 300, 385, 430, 436, 470, 480])
for h, e0, e1 in zip(hist, edges[:-1], edges[1:]):
    print('   r %3d-%3d : %d' % (e0, e1, h))
C = np.hypot(Lb[..., 1][m], Lb[..., 2][m])
hue = np.degrees(np.arctan2(Lb[..., 2][m], Lb[..., 1][m])) % 360
print('   chroma p50 %.1f; hue share 0-60 (red/orange) %.2f; C<10 (white) %.2f' % (np.median(C), ((hue < 60) | (hue > 340)).mean(), (C < 10).mean()))
# sample rgb of these px
rgb = im[m]
print('   median rgb', np.median(rgb, 0))


def edge(L, y0, y1):
    col = L[y0:y1, 1600:1920].mean(0)
    xs = np.nonzero(col >= 0.5 * col.max())[0]
    return 1600 + xs.max(), col.max()


print('\n## (b) button column, right edge by column profile (SEND IT band y 930-1000 / UNDO band y 860-890)')
for nm, img in (('round-1 p1 (b26022f5)', np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.float64)),
                ('round-2 p1', load('final/p1_decide.png')), ('round-2 h01', load('hover/h01_tower_turn.png'))):
    Lx = lstar(img)
    print('   %-24s SEND IT x %d (peak %.1f) | UNDO x %d (peak %.1f)' % ((nm,) + edge(Lx, 930, 1000) + edge(Lx, 860, 890)))
