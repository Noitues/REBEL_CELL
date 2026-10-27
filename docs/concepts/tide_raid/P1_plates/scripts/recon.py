"""P1 recon: world positions per pixel from the Godot depth pass -> heightfield (Godot X,Z grid, max Y) + camera numbers.
Usage: python recon.py <capture dir> <out npz>
Godot world: X right-ish, Y up, Z; Blender = (gx, -gz, gy)."""
import sys, json, numpy as np
from PIL import Image

d = sys.argv[1]
out = sys.argv[2]
cap = json.load(open(d + '/capture.json'))['camera']
rg = np.asarray(Image.open(d + '/depth20_rg.png'))[..., :2].astype(np.int64)
q = rg[..., 0] * 256 + rg[..., 1]
dep = q / 20.0
idm = np.asarray(Image.open(d + '/id.png'))[..., 0]
Hh, Ww = dep.shape
size = cap['size']
O = np.array(cap['position'])
yaw, pitch = np.radians(45.0), np.radians(-40.0)
# camera basis from the capture.json rotation (YXZ euler: y=45, x=-40)
cy, sy, cx, sx = np.cos(yaw), np.sin(yaw), np.cos(pitch), np.sin(pitch)
right = np.array([cy, 0, -sy])
up = np.array([sy * sx * -1 * -1, cx, cy * sx * -1 * -1])
# explicit from the capture print: X (0.707107,0,-0.707107) Y(-0.454519,0.766044,-0.454519) Z(0.541675,0.642788,0.541675)
right = np.array([0.707107, 0.0, -0.707107])
up = np.array([-0.454519, 0.766044, -0.454519])
back = np.array([0.541675, 0.642788, 0.541675])
fwd = -back
print('depth range', dep.min(), dep.max(), 'size', size)
for keep_width in (True, False):
    if keep_width:
        w_bu = size
        h_bu = size * Hh / Ww
    else:
        h_bu = size
        w_bu = size * Ww / Hh
    u = (np.arange(Ww) + 0.5) / Ww - 0.5
    v = 0.5 - (np.arange(Hh) + 0.5) / Hh
    P = (O[None, None, :] + right[None, None, :] * (u[None, :, None] * w_bu) + up[None, None, :] * (v[:, None, None] * h_bu)
         + fwd[None, None, :] * dep[..., None])
    g = idm == 4
    print('keep_width' if keep_width else 'keep_height', 'ground y: mean %.3f std %.3f p5 %.3f p95 %.3f' % (P[..., 1][g].mean(), P[..., 1][g].std(), np.percentile(P[..., 1][g], 5), np.percentile(P[..., 1][g], 95)))
    if keep_width:
        PW = P
np.savez_compressed(out, P=PW.astype(np.float32), idm=idm.astype(np.uint8), dep=dep.astype(np.float32))
