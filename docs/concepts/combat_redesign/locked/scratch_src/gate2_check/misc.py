"""misc.py -- assorted probes on the published plates.

next   : NEXT row digit L* vs the SPLIT row digit L* above it (p1: '2' at NEXT vs '6' at SPLIT, same column) -> value ratio in sRGB terms
best   : PLAN-yellow pixels (R > 220, G > 190, B < 90) inside the BEST LINE chip and the BEST: ALL THREE chip (p2, p3)
kill   : GAIN / FOCUS green pixels (G > 170, G - R > 40, G - B > 60) on the ring cells r 214-385, per plate (dead units sit there)
adj    : the Adjuster HP mask under the plate or the guns mask (masks)
hand   : lowest hand-mask row; hand mask under SEND / UNDO masks; plus an independent bottom-edge read: the lowest row in x 930-1660 whose
         pixels differ from the same row 40 px further down the backdrop column average... (not robust), so only the mask figure is used
far    : ink height of the FAR count digits at the top of the board (search box around the '3' and '2' near x 452-470 / 600-616, y 84-104)
lift   : p2: pixels of the SPIN 3 title and the x3 multiplier badge covered by the lifted card (card_r masks)"""
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
WORK = 'D:/rc_scratch/combat_redesign/locked/corp/work/'
C = (536, 540)


def lstar_img(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    Y = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    return np.where(Y > 0.008856, 116 * np.cbrt(Y) - 16, 903.3 * Y)


def load_masks(sfx):
    z = np.load(WORK + 'masks_%s.npz' % sfx)
    return {k: np.unpackbits(z[k])[:1080 * 1920].reshape(1080, 1920).astype(bool) for k in z.files}


yy, xx = np.mgrid[0:1080, 0:1920]
RHO = np.hypot(xx - C[0], yy - C[1])
img = lambda n: np.asarray(Image.open(FINAL + n + '.png').convert('RGB')).astype(float)

# next
rgb = img('p1_decide')
L = lstar_img(rgb)
for nm, box in (('SPLIT 6', (1198, 230, 1218, 256)), ('NEXT 2', (1198, 262, 1218, 288)), ('SPLIT 6 (YOU)', (1456, 230, 1476, 256)), ('NEXT 10', (1456, 262, 1480, 288))):
    x0, y0, x1, y1 = box
    b = L[y0:y1, x0:x1]
    rb = rgb[y0:y1, x0:x1].reshape(-1, 3)
    top = rb[np.argsort(b.ravel())[-15:]].mean(0)
    print('next  %-14s digit L* p98 %.1f  brightest-15 rgb %s' % (nm, float(np.percentile(b, 98)), np.round(top).astype(int)))

# best
for n in ('p2_preview', 'p3_resolve', 'p2_preview_solace', 'p2_preview_meridian'):
    rgb = img(n)
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    yel = (R > 220) & (G > 190) & (B < 90)
    chip = np.zeros((1080, 1920), bool)
    chip[80:108, 1710:1880] = True
    opt = np.zeros((1080, 1920), bool)
    opt[392:424, 1076:1896] = True
    print('best  %-20s yellow px in BEST LINE chip %d, in BEST: ALL THREE row %d' % (n, int((yel & chip).sum()), int((yel & opt).sum())))

# kill / green on ring cells
for n, s in (('p1_decide', 'p1'), ('p2_preview', 'p2'), ('p3_resolve', 'p3'), ('p2b_hover', 'p2b'), ('p1_nowords', 'nowords')):
    rgb = img(n)
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    green = (G > 170) & (G - R > 40) & (G - B > 60)
    lime = (R > 170) & (G > 200) & (B < 90) & (G - B > 120)
    ring = (RHO >= 214) & (RHO <= 385)
    M = load_masks(s)
    dead_near = np.zeros((1080, 1920), bool)
    g = json.load(open(WORK + 'chk_%s.json' % s))['rb']['geometry']
    for c in g['cells']:
        if c['state'] in ('dying',) or (c['state'] == 'dimmed' and c['uid'] == 2):
            p = np.array(c['poly']).reshape(-1, 2)
            if len(p):
                from PIL import ImageDraw
                mm = Image.new('L', (1920, 1080), 0)
                ImageDraw.Draw(mm).polygon([tuple(q) for q in p], fill=255)
                dead_near |= np.asarray(mm) > 0
    dead_near = ndi.binary_dilation(dead_near, iterations=12)
    badges = M.get('badges', np.zeros((1080, 1920), bool))
    print('kill  %-12s GAIN-green px on ring cells %d (on/near dying cells %d); lime px on ring cells %d (near dying %d); green/lime px on badges %d' % (
        n, int((green & ring).sum()), int((green & dead_near).sum()), int((lime & ring).sum()), int((lime & dead_near).sum()), int(((green | lime) & badges).sum())))

# adj and hand
for n, s in (('p1_decide', 'p1'), ('p2_preview', 'p2'), ('p2b_hover', 'p2b'), ('p3_resolve', 'p3'), ('p1_nowords', 'nowords'),
             ('p1_decide_solace', 'p1_solace'), ('p1_decide_meridian', 'p1_meridian'), ('p3_resolve_meridian', 'p3_meridian')):
    M = load_masks(s)
    get = lambda k: M.get(k, np.zeros((1080, 1920), bool))
    hand = get('hand') | get('hand_rest') | get('hand_lift') | get('hand_played')
    ys = np.nonzero(hand.any(1))[0]
    print('adj/hand %-20s adj_hp px %d covered %d | hand lowest row %d (margin %d) | hand x SEND %d x UNDO %d' % (
        n, int(get('adj_hp').sum()), int((get('adj_hp') & (get('adj') | get('guns'))).sum()), ys.max(), 1079 - ys.max(),
        int((hand & get('send')).sum()), int((hand & get('undo')).sum())))

# far digits
rgb = img('p1_decide')
L = lstar_img(rgb)
for nm, (x0, y0, x1, y1) in (('FAR 3 (top)', (450, 82, 470, 106)), ('FAR 2 (top)', (598, 82, 618, 106))):
    b = L[y0:y1, x0:x1]
    lo, hi = np.percentile(b, 5), np.percentile(b, 99.5)
    rows = np.nonzero(((b > (lo + hi) / 2).sum(1)) >= 1)[0]
    print('far   %-12s ink rows %d-%d = %d px, L* p99.5 %.1f' % (nm, y0 + rows.min(), y0 + rows.max(), rows.max() - rows.min() + 1, hi))

# lifted card over Spin 3 title / multiplier on p2
M = load_masks('p2')
chk = json.load(open(WORK + 'chk_p2.json'))
cards = chk['rb']['cards']
li = [i for i, c in enumerate(cards) if c['role'] == 'lift']
print('lift  cards', [(c['name'], c['role'], round(c['cx']), round(c['cy'])) for c in cards])
