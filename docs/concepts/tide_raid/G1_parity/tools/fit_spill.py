"""Signed spill (range -0.25..0.75 linear). If the old spill path contains "orig" it is the first unsigned (gamma 2.2 x2) bake. Refines the baked light-spill map so the live city's low-frequency luminance and colour match the plate target: new spill = gain * old + factor * (lin(blur(target)) - lin(blur(godot))),
clipped at 0, blurred residual at `sigma` px. The result is stored with the config gain 1 (encoding as bake_spill.py). usage: python fit_spill.py <godot.png> <target.png> <old_spill.png> <old_gain> <sigma> <factor> <out.png>
No python from stdin."""
import sys

sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

g_p, t_p, s_p, gain, sigma, factor, out = sys.argv[1:8]
CLIP = float(sys.argv[9]) if len(sys.argv) > 9 else 0.06
luma_only = len(sys.argv) > 8 and sys.argv[8] == "luma"
gain, sigma, factor = float(gain), float(sigma), float(factor)


def lin(a):
    return np.where(a <= .04045, a / 12.92, ((a + .055) / 1.055) ** 2.4)


def ld(p):
    return lin(np.asarray(Image.open(p).convert("RGB"), np.float32) / 255)


G, T = ld(g_p), ld(t_p)
raw = np.asarray(Image.open(s_p).convert("RGB"), np.float32) / 255
S = raw ** 2.2 * 2.0 if "orig" in s_p else raw * 0.75
bl = lambda a: np.stack([ndi.gaussian_filter(a[..., i], sigma, mode="nearest") for i in range(3)], -1)
LO, HI = 0.0, 0.75
res = bl(T) - bl(G)
if luma_only:
    res = np.repeat((res @ np.array([.2126, .7152, .0722], np.float32))[..., None], 3, -1)
res = np.clip(res, -CLIP, CLIP)
new = S * gain + factor * res
enc = (np.clip(new, LO, HI) - LO) / (HI - LO)
Image.fromarray((enc * 255 + .5).astype(np.uint8)).save(out)
print("resid mean abs", np.abs(bl(T) - bl(G)).mean(), "new spill mean", new.mean((0, 1)), "old", S.mean((0, 1)) * gain)
