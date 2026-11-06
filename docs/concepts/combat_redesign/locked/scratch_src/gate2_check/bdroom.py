"""bdroom.py -- backdrop plates: room mean L* / p95 in the rb_checks room region (p1 masks, the board is the same p1 board on every backdrop),
compared with backdrop/checks.json 'after'; plus the ring-NOW glass p95 reference from the same plate, the reviewer box, and the room pink share."""
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

BD = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/backdrop/'
WORK = 'D:/rc_scratch/combat_redesign/locked/corp/work/'
C = (536, 540)


def lum(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def ls(y):
    y = np.asarray(y, float)
    return np.where(y > 0.008856, 116 * np.cbrt(y) - 16, 903.3 * y)


def load_masks(sfx):
    z = np.load(WORK + 'masks_%s.npz' % sfx)
    return {k: np.unpackbits(z[k])[:1080 * 1920].reshape(1080, 1920).astype(bool) for k in z.files}


yy, xx = np.mgrid[0:1080, 0:1920]
RHO = np.hypot(xx - C[0], yy - C[1])
ck = json.load(open(BD + 'checks.json', encoding='utf-8'))
for nm, sfx in (('p1_bio', 'p1'), ('p1_srv', 'p1'), ('p1_gh', 'p1'), ('p1_rec', 'p1'), ('p1_lobby', 'p1'), ('p1_event', 'p1'), ('p1_shop', 'p1'),
                ('p1_bio_solace', 'p1_solace'), ('p1_shop_meridian', 'p1_meridian')):
    rgb = np.asarray(Image.open(BD + nm + '.png').convert('RGB')).astype(float)
    Y = lum(rgb)
    L = ls(Y)
    M = load_masks(sfx)
    get = lambda k: M.get(k, np.zeros((1080, 1920), bool))
    ui = get('hud') | get('hand_rest') | get('send') | get('undo') | get('name') | get('you') | get('tags') | get('leader')
    a = (xx >= 1100) & (yy >= 420) & ~ndi.binary_dilation(ui, iterations=4) & (RHO > 505) & ~get('scrim')
    a2 = (xx >= 1100) & (yy >= 420) & ~ndi.binary_dilation(ui, iterations=4) & (RHO > 505)
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    pink = (R > 200) & (B > 120) & (G < 120)
    after = ck['plates'][nm].get('after', {}).get('L', {}).get('room', {})
    print('%-18s room mean %.1f p95 %.1f | as seen %.1f | box mean %.1f | pink %.3f %% | checks.json after %s' % (
        nm, float(ls(Y[a].mean())), float(np.percentile(L[a], 95)), float(ls(Y[a2].mean())), float(ls(Y[450:800, 1200:1800].mean())),
        100 * float(pink[a].mean()), after))
