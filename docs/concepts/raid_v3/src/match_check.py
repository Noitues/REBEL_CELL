"""match check: the new hi capture against the P3 4k plate on their overlap (same stage: raw window_nonet vs depth30/window_nonet,
and, when graded, city_albedo_hi vs city_albedo4k).  Both are brought to the 4k plate's density (2 px per city_default px) over
the overlap; prints the normalised correlation and the best shift (phase correlation), and writes a side-by-side.

    python match_check.py [raw|graded]
"""
import json
import sys

sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw

TC = 'D:/rc_scratch/tide_concepts/p3_work/'
HI = 'D:/rc_scratch/raid_v3/city_hi/'
mode = sys.argv[1] if len(sys.argv) > 1 else 'raw'
RIGHT = np.array([0.707107, 0.0, -0.707107]); UP = np.array([-0.454519, 0.766044, -0.454519])
oc = json.load(open(TC + 'depth30/capture.json'))['camera']
nc = json.load(open(HI + 'capture/capture.json'))
res = nc['resolution']; nc = nc['camera']
O0, S0 = np.array(oc['position']), oc['size']
O1, S1 = np.array(nc['position']), nc['size']
K = (res[0] / S1) / (1920 / S0)
d = O1 - O0
cx0, cy0 = d @ RIGHT / S0 * 1920 + 960, 540 - d @ UP / S0 * 1920
print('hi camera size %.3f  K %.4f  centre on city_default (%.2f, %.2f)' % (S1, K, cx0, cy0))
# the overlap in city_default px
x0, y0 = max(cx0 - res[0] / 2 / K, 0), max(cy0 - res[1] / 2 / K, 0)
x1, y1 = min(cx0 + res[0] / 2 / K, 1920), min(cy0 + res[1] / 2 / K, 1080)
print('overlap on city_default: x %.1f..%.1f  y %.1f..%.1f' % (x0, x1, y0, y1))
if mode == 'raw':
    old = Image.open(TC + 'depth30/window_nonet.png').convert('RGB'); new = Image.open(HI + 'capture/window_nonet.png').convert('RGB')
else:
    old = Image.open(TC + 'city_albedo4k.png').convert('RGB'); new = Image.open(HI + 'city_albedo_hi.png').convert('RGB')
ow, oh = int(round((x1 - x0) * 2)), int(round((y1 - y0) * 2))
A = old.resize((ow, oh), Image.BOX, box=(x0 * 2, y0 * 2, x1 * 2, y1 * 2))
bx = (res[0] / 2 + (x0 - cx0) * K, res[1] / 2 + (y0 - cy0) * K, res[0] / 2 + (x1 - cx0) * K, res[1] / 2 + (y1 - cy0) * K)
bx = (max(bx[0], 0.0), max(bx[1], 0.0), min(bx[2], res[0]), min(bx[3], res[1]))
B = new.resize((ow, oh), Image.LANCZOS, box=bx)
a = np.asarray(A, np.float32).mean(-1); b = np.asarray(B, np.float32).mean(-1)
za = (a - a.mean()) / a.std(); zb = (b - b.mean()) / b.std()
print('NCC at the computed alignment: %.3f' % (za * zb).mean())
F = np.fft.fft2(za) * np.conj(np.fft.fft2(zb))
r = np.fft.ifft2(F / np.maximum(np.abs(F), 1e-9)).real
iy, ix = np.unravel_index(np.argmax(r), r.shape)
sy = iy if iy < oh // 2 else iy - oh; sx = ix if ix < ow // 2 else ix - ow
print('best shift (4k px, old relative to new): dx %d dy %d   peak %.3f' % (sx, sy, r.max()))
# per-tile NCC (where the city changed, it drops)
tiles = []
for ty in range(0, oh - 63, 64):
    for tx in range(0, ow - 63, 64):
        p, q = za[ty:ty + 64, tx:tx + 64], zb[ty:ty + 64, tx:tx + 64]
        if p.std() > 0.2 and q.std() > 0.2:
            tiles.append(((p - p.mean()) * (q - q.mean())).mean() / (p.std() * q.std()))
tiles = np.array(tiles)
print('64 px tiles: %d, NCC median %.3f, p10 %.3f, share < 0.5: %.2f' % (len(tiles), np.median(tiles), np.percentile(tiles, 10), (tiles < 0.5).mean()))
sbs = Image.new('RGB', (ow * 2 + 12, oh + 40), (10, 10, 14))
sbs.paste(A, (0, 40)); sbs.paste(B, (ow + 12, 40))
dr = ImageDraw.Draw(sbs)
dr.text((8, 10), 'P3 4k (%s)' % ('depth30 raw' if mode == 'raw' else 'city_albedo4k'), fill=(230, 230, 230))
dr.text((ow + 20, 10), 'hi capture (%s), at the 4k density' % ('raw' if mode == 'raw' else 'graded'), fill=(230, 230, 230))
sbs.save(HI + 'match_%s.jpg' % mode, quality=88)
print('ok', HI + 'match_%s.jpg' % mode)
