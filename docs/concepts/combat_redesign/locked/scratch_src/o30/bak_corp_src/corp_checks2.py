"""real-plate unit wash read-back: median colour of each unit cell (cell poly minus 14 px inset from marks is not available; the median ignores thin marks)"""
import sys, os, json
sys.dont_write_bytecode = True
os.environ['LW_SKIN'] = '0'
import numpy as np
from PIL import Image, ImageDraw
from wr_geo import cell_poly, unit_bounds
import de_kinds as DK
J = json.load(open('../state_e10.json'))['f1']
res = {}
for n, f in (('neutral', 'as_p1.png'), ('solace', 'as_p1_solace.png'), ('meridian', 'as_p1_meridian.png')):
    im = np.asarray(Image.open('../out/' + f).convert('RGB')).astype(np.float64)
    med = {}
    for u in J['units']:
        b0, b1 = unit_bounds(u)
        poly = cell_poly(u['dep'], b0, b1, kind='unit')
        m = Image.new('L', (1920, 1080), 0)
        ImageDraw.Draw(m).polygon(poly, fill=255)
        m = np.asarray(m) > 0
        med[u['id']] = (u['kind'], u['dep'], np.median(im[m], 0))
    out = {}
    for a in med:
        for b in med:
            if a < b and med[a][1] == med[b][1] and med[a][0] != med[b][0]:
                out['%d%s-%d%s ring%d' % (a, med[a][0], b, med[b][0], med[a][1])] = round(DK.de2000(DK.rgb2lab(med[a][2]), DK.rgb2lab(med[b][2])), 1)
    res[n] = out
json.dump(res, open('../work/corp_checks2.json', 'w'), indent=1)
print(json.dumps(res, indent=1))
