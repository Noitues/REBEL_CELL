"""gate1 C7: dying cell glass vs the brightest empty reference on h03 (and the board p1 for comparison).
Cells from corp/work/chk_p1.json rb.geometry (same board layout).  Glass = cell poly eroded 4 px, minus the token disc (+8 px), minus PLAN / FOCUS
pixels (dE < 30, dilated 2), minus chevrons (HARM-ish red, dilated 2).  (a) hatch kept; (b) pink (dE < 35 of CELL_PINK, dilated 1) cut too.
Empty reference: the probe image's ring cell glass of the same sector (the skin's empty-cell probe) and every empty cell of the ring on the plate.
usage: c7.py <plate png> <probe png> <ring> <sector,...>"""
import sys, json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import glib as G
chk = json.load(open('D:/rc_scratch/combat_redesign/locked/corp/work/chk_p1.json'))
geo = chk['rb']['geometry']
rgb = G.load(sys.argv[1]); prgb = G.load(sys.argv[2])
ring = int(sys.argv[3]); secs = [int(s) for s in sys.argv[4].split(',')]
Y = G.lum(rgb); PY = G.lum(prgb)
lab = G.lab(rgb)


def pm(poly):
    m = Image.new('L', (1920, 1080), 0)
    ImageDraw.Draw(m).polygon([tuple(q) for q in poly], fill=255)
    return np.asarray(m) > 0


cut = ndi.binary_dilation((G.de(lab, '#FFE200') < 30) | (G.de(lab, '#D4FF00') < 30) | (G.de(lab, '#FF6452') < 30) | (G.de(lab, '#FF4433') < 30), iterations=2)
pink = ndi.binary_dilation(G.de(lab, '#FF3DA8') < 35, iterations=1)
yy, xx = np.mgrid[0:1080, 0:1920]
for u in geo.get('units', []):
    cut |= np.hypot(xx - u['token'][0], yy - u['token'][1]) <= u['tok_r'] + 8
for c in geo['cells']:
    if c['dep'] != ring or c['s'] not in secs:
        continue
    g = ndi.binary_erosion(pm(c['poly']), iterations=4)
    a = g & ~cut; b = a & ~pink
    ya = Y[a].mean(); yb = Y[b].mean() if b.sum() > 50 else float('nan')
    # probe
    pr = [p for p in geo.get('probe', []) if p['dep'] == ring]
    pv = []
    for p in pr:
        pg = ndi.binary_erosion(pm(p['poly']), iterations=4)
        pv.append(PY[pg].mean())
    pmax = max(pv) if pv else float('nan')
    print('ring %d s%d %s (%s): glass(a) px %d L* %.1f | (b, pink cut) px %d L* %.1f | probe empty max L* %.1f (n %d) | ratio a %.2f b %.2f' % (
        ring, c['s'], c['kind'], c['state'], a.sum(), G.lstar_y(ya), b.sum(), G.lstar_y(yb), G.lstar_y(pmax), len(pv),
        (ya + 0.05) / (pmax + 0.05), (yb + 0.05) / (pmax + 0.05)))
print('probe polys', [(p['dep'], p.get('s')) for p in geo.get('probe', [])][:20])
